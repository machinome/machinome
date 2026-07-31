"""Hermes agent backend — wraps ``hermes acp`` over stdio.

Launches ``hermes acp`` as a subprocess and speaks the ACP JSON-RPC
protocol (newline-delimited JSON over stdio).  Translates ACP
``session/update`` notifications and ``session/prompt`` responses
into portable ``BackendEvent`` instances.
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
from collections.abc import AsyncIterator, Sequence
from pathlib import Path
from typing import Any

from .base import (
    AgentBackend,
    BackendEvent,
    DeliveryReceipt,
    InactiveTurn,
    RoleContext,
    RoleHandle,
)

# Hermes streams one of these as an ``agent_message_chunk`` when it accepts a
# correction into a running turn. They are control-plane chatter, not turn
# output, so they are filtered out of the assembled message.
#
# This is content filtering only. ADR 0007 forbids deciding delivery identity
# from agent prose, and nothing here does: if Hermes reworded these, a stray
# sentence would reach the conversation, but no turn output would be lost and
# no delivery identity would change. Suppressing by session instead would drop
# genuine turn text that was still in flight when the correction was sent.
STEER_ACKNOWLEDGEMENTS = (
    "Redirected the active turn with your correction.",
    "Queued for the next turn.",
)


def _is_steer_acknowledgement(text: str) -> bool:
    stripped = text.strip()
    return any(stripped.startswith(marker) for marker in STEER_ACKNOWLEDGEMENTS)


class HermesBackend:
    """AgentBackend backed by a ``hermes acp`` subprocess.

    Each role gets one persistent ACP session.  The orchestrator routes
    envelopes via ``deliver_start()`` (``session/prompt`` when idle) and
    ``deliver_steer()`` (cancel + new ``session/prompt`` when active).
    Events translate from ACP ``session/update`` notifications and
    ``session/prompt`` responses.
    """

    events: AsyncIterator[BackendEvent]

    def __init__(
        self,
        cwd: Path,
        *,
        project: Path | None = None,
        command: str | Sequence[str] = "hermes",
        broker_url: str = "http://127.0.0.1:9000",
        solid_command: str | Sequence[str] = "solid",
        control_timeout: float = 30,
        prompt_timeout: float = 900,
        stop_timeout: float = 5,
    ) -> None:
        self.cwd = cwd.resolve()
        self.project = (project or cwd).resolve()
        self.command = (command,) if isinstance(command, str) else tuple(command)
        self.broker_url = broker_url
        self.solid_command = (
            (solid_command,) if isinstance(solid_command, str) else tuple(solid_command)
        )
        # Control-plane liveness (initialize, session/new) and model work are
        # different budgets: a profile bootstrap reads its prompt and every skill
        # it names, which says nothing about whether the protocol is alive.
        self.control_timeout = control_timeout
        self.prompt_timeout = prompt_timeout
        self.stop_timeout = stop_timeout

        # Subprocess state (set by start())
        self.process: asyncio.subprocess.Process | None = None
        self.notifications: asyncio.Queue[dict[str, Any] | BackendEvent] = (
            asyncio.Queue()
        )
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._next_id = 0
        self._reader_task: asyncio.Task[None] | None = None
        self._stderr_task: asyncio.Task[None] | None = None

        # Session tracking: session_id -> (role, session_id)
        self._handles: dict[str, tuple[str, str]] = {}
        # Which request_id is the active prompt for each session
        self._active_prompts: dict[str, int] = {}
        # Prompt request_id -> (session_id, role), for response correlation.
        self._prompt_requests: dict[int, tuple[str, str]] = {}
        self._prompt_chunks: dict[int, list[str]] = {}
        # Steer prompts carry a correction into a turn that is already running.
        # They are not turns of their own, so they never reach the orchestrator.
        self._steer_requests: set[int] = set()
        self._steer_by_session: dict[str, int] = {}
        # Sessions this backend cancelled. Hermes 0.19.0 fails their outstanding
        # prompt instead of reporting a "cancelled" stop reason, and cannot run
        # anything afterwards (see ADR 0007).
        self._cancelled_sessions: set[str] = set()
        self._bootstrap_sessions: set[str] = set()
        self._closing = False

        self.events = self._event_iterator()

    # ── AgentBackend protocol ──────────────────────────────────────────

    async def start(self) -> None:
        """Launch the ``hermes acp`` subprocess (idempotent)."""
        if self.process is not None:
            return
        self._closing = False
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            "acp",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd,
            env={
                **os.environ,
                "HERMES_ACP_SKIP_CONFIGURED_MCP": "1",
                "FLOOR_URL": self.broker_url,
                "PYTHONPATH": os.pathsep.join(
                    item
                    for item in (
                        str(self.cwd),
                        os.environ.get("PYTHONPATH", ""),
                    )
                    if item
                ),
            },
            start_new_session=True,
        )
        self._reader_task = asyncio.create_task(self._read_stdout())
        self._stderr_task = asyncio.create_task(self._drain_stderr())
        await self._request(
            "initialize",
            {
                "protocolVersion": 1,
                "clientCapabilities": {},
                "clientInfo": {
                    "name": "solid-node-shop-orchestrator",
                    "title": "solid-node shop orchestrator",
                    "version": "0.1.0",
                },
            },
        )

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        """Create a persistent ACP session for *role* with *context*."""
        result = await self._request(
            "session/new",
            {"cwd": context.active_project, "mcpServers": []},
        )
        session_id = str(result["sessionId"])
        handle = RoleHandle(backend_id=session_id, role=role)
        self._handles[session_id] = (role, session_id)

        # ACP has no developer-instructions field on session/new. Prime the
        # persistent session with an ordinary request and await completion so
        # the role contract is loaded before the broker manifests the role.
        self._bootstrap_sessions.add(session_id)
        try:
            await self._request(
                "session/prompt",
                {
                    "sessionId": session_id,
                    "prompt": [
                        {
                            "type": "text",
                            "text": self._role_bootstrap(role, context),
                        }
                    ],
                },
                timeout=self.prompt_timeout,
            )
        except BaseException:
            self._handles.pop(session_id, None)
            raise
        finally:
            self._bootstrap_sessions.discard(session_id)
        return handle

    async def deliver_start(
        self, handle: RoleHandle, message: str
    ) -> DeliveryReceipt:
        """Start a prompt on an idle role session.

        Returns immediately with a receipt; the prompt response is
        processed asynchronously and surfaced as a turn_completed event.
        """
        session_id = handle.backend_id
        delivery_id = await self._send_prompt(handle, message)
        return DeliveryReceipt(delivery_id=str(delivery_id), accepted=True)

    async def deliver_steer(
        self,
        handle: RoleHandle,
        expected_delivery_id: str,
        message: str,
    ) -> DeliveryReceipt:
        """Steer the active prompt.  Raises InactiveTurn on a completion race.

        Per ADR 0007 this sends an additional ``session/prompt`` and never
        ``session/cancel``: Hermes applies the correction to the turn already
        running, delivering it at the next tool-batch boundary. The turn — and
        therefore the delivery identity — survives.
        """
        session_id = handle.backend_id
        try:
            expected_id = int(expected_delivery_id)
        except ValueError:
            raise InactiveTurn from None

        # The only authority on whether the turn is still live is our own
        # record of the outstanding prompt. Never the agent's prose reply.
        if expected_id not in self._prompt_requests:
            raise InactiveTurn

        active = self._active_prompts.get(session_id)
        if active is None or active != expected_id:
            raise InactiveTurn

        await self._send_steer_prompt(handle, message)
        return DeliveryReceipt(delivery_id=expected_delivery_id, accepted=True)

    async def interrupt(self, handle: RoleHandle) -> None:
        """Cancel the active prompt.  Spends the session (ADR 0007).

        hermes 0.19.0 cannot run anything on a session after it is cancelled, so
        this is reserved for closing or shutting down the shop and the session is
        never returned to standby.
        """
        session_id = handle.backend_id
        self._cancelled_sessions.add(session_id)
        await self._notify("session/cancel", {"sessionId": session_id})

    async def close_role(self, handle: RoleHandle) -> None:
        """Release a role session (best-effort — cancels active prompt)."""
        session_id = handle.backend_id
        self._cancelled_sessions.add(session_id)
        await self._notify("session/cancel", {"sessionId": session_id})
        self._handles.pop(session_id, None)
        self._active_prompts.pop(session_id, None)

    async def close(self) -> None:
        """Stop the acp process and release OS resources."""
        if self.process is None:
            return
        self._closing = True
        if self.process.stdin is not None:
            self.process.stdin.close()
        # Escalate so no close path can wait forever on a subprocess that
        # declines to exit: input close, then SIGTERM, then SIGKILL.
        for stop in (None, self.process.terminate, self.process.kill):
            if stop is not None:
                stop()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=self.stop_timeout)
                break
            except asyncio.TimeoutError:
                continue
        if self._reader_task is not None:
            self._reader_task.cancel()
            await asyncio.gather(self._reader_task, return_exceptions=True)
        if self._stderr_task is not None:
            self._stderr_task.cancel()
            await asyncio.gather(self._stderr_task, return_exceptions=True)
        self._pending.clear()
        self._prompt_requests.clear()
        self._active_prompts.clear()
        self._prompt_chunks.clear()
        self._steer_requests.clear()
        self._steer_by_session.clear()
        self._cancelled_sessions.clear()
        self._handles.clear()
        self.process = None
        self._reader_task = None
        self._stderr_task = None

    # ── event iterator ─────────────────────────────────────────────────

    async def _event_iterator(self) -> AsyncIterator[BackendEvent]:
        """Yield portable BackendEvents from the ACP notification queue."""
        while True:
            message = await self.notifications.get()
            if isinstance(message, BackendEvent):
                yield message
                continue
            event = self._translate_notification(message)
            if event is not None:
                yield event

    def _translate_notification(
        self, message: dict[str, Any]
    ) -> BackendEvent | None:
        """Translate one ACP message into a BackendEvent.

        Legacy whole-message ``agentMessage`` updates are accepted here.
        Current streamed ``agent_message_chunk`` updates and prompt responses
        are correlated and assembled by ``_read_stdout``.
        """
        method = message.get("method")
        params = message.get("params", {})

        if method == "session/update":
            update = params.get("update", {})
            agent_message = update.get("agentMessage")
            if agent_message is not None:
                session_id = params.get("sessionId", "")
                role_info = self._handles.get(session_id)
                if role_info is None:
                    return None
                role = role_info[0]
                text = str(agent_message.get("text", "")).strip()
                if text:
                    return BackendEvent(
                        kind="role_message",
                        role=role,
                        text=text,
                    )
            return None

        return None

    def _role_bootstrap(self, role: str, context: RoleContext) -> str:
        """Build the authoritative role-contract bootstrap prompt."""
        agent = context.agent
        shop = Path(context.shop_checkout).resolve()
        lines = [
            f"Shop checkout: {shop}",
            f"Active project: {Path(context.active_project).resolve()}",
            f"Role: {role}",
            "Before taking any task action, read the following profile prompt in full ",
            f"and follow it as authoritative: {agent.prompt_path}",
        ]
        for skill in agent.skill_paths:
            lines.append(f"Required profile skill: {skill / 'SKILL.md'}")
        lines.append(
            "Do not begin project work. Finish loading this contract, then return "
            "to standby for a broker message."
        )
        return "\n".join(lines)


    # ── JSON-RPC plumbing ──────────────────────────────────────────────

    async def _request(
        self, method: str, params: dict[str, Any], timeout: float | None = None
    ) -> dict[str, Any]:
        """Send a JSON-RPC request and await the response.

        ``timeout`` defaults to the control-plane budget. Prompt work must pass
        ``self.prompt_timeout`` instead: model work taking longer than a
        liveness check is healthy, not a stalled protocol.
        """
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("hermes acp is not running")
        self._next_id += 1
        request_id = self._next_id
        future: asyncio.Future[dict[str, Any]] = (
            asyncio.get_running_loop().create_future()
        )
        self._pending[request_id] = future
        payload = (
            json.dumps(
                {"id": request_id, "method": method, "params": params}
            )
            + "\n"
        )
        self.process.stdin.write(payload.encode())
        await self.process.stdin.drain()
        try:
            return await asyncio.wait_for(
                future,
                timeout=self.control_timeout if timeout is None else timeout,
            )
        finally:
            if self._pending.get(request_id) is future:
                self._pending.pop(request_id, None)

    async def _send_prompt(self, handle: RoleHandle, message: str) -> int:
        """Dispatch a prompt and emit its portable start event."""
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("hermes acp is not running")
        self._next_id += 1
        request_id = self._next_id
        session_id = handle.backend_id
        self._prompt_requests[request_id] = (session_id, handle.role)
        self._active_prompts[session_id] = request_id
        self._prompt_chunks[request_id] = []
        payload = (
            json.dumps(
                {
                    "id": request_id,
                    "method": "session/prompt",
                    "params": {
                        "sessionId": session_id,
                        "prompt": [{"type": "text", "text": message}],
                    },
                }
            )
            + "\n"
        )
        self.process.stdin.write(payload.encode())
        # Queue the portable start before yielding to the reader task. A fast
        # ACP response can therefore never overtake its start event.
        self.notifications.put_nowait(
            BackendEvent(
                kind="turn_started",
                role=handle.role,
                delivery_id=str(request_id),
            )
        )
        try:
            await self.process.stdin.drain()
        except BaseException:
            self._prompt_requests.pop(request_id, None)
            if self._active_prompts.get(session_id) == request_id:
                self._active_prompts.pop(session_id, None)
            self._prompt_chunks.pop(request_id, None)
            raise
        return request_id

    async def _send_steer_prompt(self, handle: RoleHandle, message: str) -> int:
        """Carry a correction into the turn already running on this session.

        Hermes answers this request immediately with a bare stop reason that is
        an acknowledgement, not a completion, so it is deliberately not awaited
        and never becomes a portable turn. The original prompt's own response
        remains the turn's completion.
        """
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("hermes acp is not running")
        self._next_id += 1
        request_id = self._next_id
        session_id = handle.backend_id
        self._steer_requests.add(request_id)
        # Text streamed between this request and its acknowledgement is
        # control-plane chatter ("Redirected the active turn with your
        # correction."), not turn output. Suppress it until the ack lands.
        self._steer_by_session[session_id] = request_id
        payload = (
            json.dumps(
                {
                    "id": request_id,
                    "method": "session/prompt",
                    "params": {
                        "sessionId": session_id,
                        "prompt": [{"type": "text", "text": message}],
                    },
                }
            )
            + "\n"
        )
        self.process.stdin.write(payload.encode())
        try:
            await self.process.stdin.drain()
        except BaseException:
            self._steer_requests.discard(request_id)
            if self._steer_by_session.get(session_id) == request_id:
                self._steer_by_session.pop(session_id, None)
            raise
        return request_id

    async def _notify(
        self, method: str, params: dict[str, Any]
    ) -> None:
        """Send a JSON-RPC notification (no response expected)."""
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("hermes acp is not running")
        payload = (
            json.dumps({"method": method, "params": params}) + "\n"
        )
        self.process.stdin.write(payload.encode())
        await self.process.stdin.drain()

    async def _read_stdout(self) -> None:
        """Read JSON-RPC messages from the acp subprocess stdout.

        Responses (with id + result or error) resolve the corresponding
        pending future.  Notifications (with method, no id) are placed
        on the notification queue for event translation.
        """
        assert self.process is not None and self.process.stdout is not None
        while line := await self.process.stdout.readline():
            message = json.loads(line)
            request_id = message.get("id")
            if request_id is not None and (
                "result" in message or "error" in message
            ):
                if request_id in self._steer_requests:
                    # Acknowledgement of a correction carried into a live turn.
                    # Not a turn: emit nothing and stop suppressing chunks.
                    self._steer_requests.discard(request_id)
                    for session, steer in tuple(self._steer_by_session.items()):
                        if steer == request_id:
                            self._steer_by_session.pop(session, None)
                    continue
                prompt = self._prompt_requests.pop(request_id, None)
                if prompt is not None:
                    session_id, role = prompt
                    is_active = self._active_prompts.get(session_id) == request_id
                    if is_active:
                        self._active_prompts.pop(session_id, None)
                    chunks = self._prompt_chunks.pop(request_id, ())
                    text = ""
                    if is_active:
                        text = "".join(chunks).strip()
                    # A prompt this backend cancelled ends the turn, however the
                    # subprocess chose to report it. hermes 0.19.0 answers with
                    # a transport error rather than a "cancelled" stop reason,
                    # and treating that as a role failure would end the run.
                    if "error" in message and session_id in self._cancelled_sessions:
                        await self.notifications.put(
                            BackendEvent(
                                kind="turn_completed",
                                role=role,
                                delivery_id=str(request_id),
                            )
                        )
                        continue
                    if "error" in message:
                        await self.notifications.put(
                            BackendEvent(
                                kind="role_failed",
                                role=role,
                                delivery_id=str(request_id),
                                error=json.dumps(message["error"]),
                            )
                        )
                    else:
                        if text:
                            await self.notifications.put(
                                BackendEvent(
                                    kind="role_message",
                                    role=role,
                                    text=text,
                                )
                            )
                        await self.notifications.put(
                            BackendEvent(
                                kind="turn_completed",
                                role=role,
                                delivery_id=str(request_id),
                            )
                        )
                    continue
                future = self._pending.pop(request_id, None)
                if future is None:
                    continue
                if "error" in message:
                    future.set_exception(
                        RuntimeError(json.dumps(message["error"]))
                    )
                else:
                    future.set_result(message["result"])
            elif "method" in message:
                session_id = message.get("params", {}).get("sessionId")
                if session_id in self._bootstrap_sessions:
                    continue
                update = message.get("params", {}).get("update", {})
                if update.get("sessionUpdate") == "agent_message_chunk":
                    content = update.get("content", {})
                    if session_id in self._steer_by_session and (
                        _is_steer_acknowledgement(str(content.get("text", "")))
                    ):
                        # Hermes acknowledging the correction, not turn output.
                        continue
                    active_request = self._active_prompts.get(session_id)
                    if (
                        content.get("type") == "text"
                        and active_request is not None
                    ):
                        self._prompt_chunks.setdefault(active_request, []).append(
                            str(content.get("text", ""))
                        )
                    continue
                await self.notifications.put(message)
        if not self._closing:
            returncode = await self.process.wait()
            error = f"hermes acp exited unexpectedly with status {returncode}"
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(RuntimeError(error))
            self._pending.clear()
            self._prompt_requests.clear()
            self._active_prompts.clear()
            self._prompt_chunks.clear()
            self._steer_requests.clear()
            self._steer_by_session.clear()
            await self.notifications.put(
                BackendEvent(kind="backend_failed", error=error)
            )

    async def _drain_stderr(self) -> None:
        """Drain stderr (Hermes logs to stderr in ACP mode)."""
        assert self.process is not None and self.process.stderr is not None
        while await self.process.stderr.readline():
            pass


# ── registration ─────────────────────────────────────────────────────────

from . import _register  # noqa: E402

_register("hermes", HermesBackend)
