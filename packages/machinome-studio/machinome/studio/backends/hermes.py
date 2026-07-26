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
from collections.abc import AsyncIterator, Sequence
from pathlib import Path
from typing import Any

from .base import (
    AgentBackend,
    BackendEvent,
    DeliveryReceipt,
    RoleContext,
    RoleHandle,
)
from .codex import InactiveTurn


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
        model_callback_url: str | None = None,
    ) -> None:
        self.cwd = cwd.resolve()
        self.project = (project or cwd).resolve()
        self.command = (command,) if isinstance(command, str) else tuple(command)
        self.broker_url = broker_url
        self.solid_command = (
            (solid_command,) if isinstance(solid_command, str) else tuple(solid_command)
        )
        self.model_callback_url = model_callback_url

        # Subprocess state (set by start())
        self.process: asyncio.subprocess.Process | None = None
        self.notifications: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._next_id = 0
        self._reader_task: asyncio.Task[None] | None = None
        self._stderr_task: asyncio.Task[None] | None = None

        # Session tracking: session_id -> (role, session_id)
        self._handles: dict[str, tuple[str, str]] = {}
        # Which request_id is the active prompt for each session
        self._active_prompts: dict[str, int] = {}

        self.events = self._event_iterator()

    # ── AgentBackend protocol ──────────────────────────────────────────

    async def start(self) -> None:
        """Launch the ``hermes acp`` subprocess (idempotent)."""
        if self.process is not None:
            return
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

        # Inject role context via an initial fire-and-forget prompt.
        # The orchestrator delivers real work later; this primes the
        # session so the agent knows its identity and workspace.
        context_text = (
            f"Shop checkout: {context.shop_checkout}\n"
            f"Active project: {context.active_project}\n"
            f"Role: {role}\n"
            "You are a specialist agent in the solid-node shop.  "
            "The foreman will direct you when work is ready.\n"
        )
        await self._send_notify(
            "session/prompt",
            {
                "sessionId": session_id,
                "prompt": [{"type": "text", "text": context_text}],
            },
        )
        return handle

    async def deliver_start(
        self, handle: RoleHandle, message: str
    ) -> DeliveryReceipt:
        """Start a prompt on an idle role session.

        Returns immediately with a receipt; the prompt response is
        processed asynchronously and surfaced as a turn_completed event.
        """
        session_id = handle.backend_id
        delivery_id = await self._send_async(
            "session/prompt",
            {
                "sessionId": session_id,
                "prompt": [{"type": "text", "text": message}],
            },
        )
        self._active_prompts[session_id] = delivery_id
        return DeliveryReceipt(delivery_id=str(delivery_id), accepted=True)

    async def deliver(
        self, handle: RoleHandle, message: str
    ) -> DeliveryReceipt:
        """Default: start a new delivery."""
        return await self.deliver_start(handle, message)

    async def deliver_steer(
        self,
        handle: RoleHandle,
        expected_delivery_id: str,
        message: str,
    ) -> DeliveryReceipt:
        """Steer an active prompt.  Raises InactiveTurn on completion race."""
        session_id = handle.backend_id
        try:
            expected_id = int(expected_delivery_id)
        except ValueError:
            raise InactiveTurn from None

        # Check whether the expected prompt already completed.
        future = self._pending.get(expected_id)
        if future is None or future.done():
            raise InactiveTurn

        active = self._active_prompts.get(session_id)
        if active is None or active != expected_id:
            raise InactiveTurn

        # Cancel the current prompt.
        await self._notify("session/cancel", {"sessionId": session_id})

        # Start a new prompt with the correction.
        return await self.deliver_start(handle, message)

    async def interrupt(self, handle: RoleHandle) -> None:
        """Interrupt the active prompt (best-effort)."""
        session_id = handle.backend_id
        await self._notify("session/cancel", {"sessionId": session_id})

    async def close_role(self, handle: RoleHandle) -> None:
        """Release a role session (best-effort — cancels active prompt)."""
        session_id = handle.backend_id
        await self._notify("session/cancel", {"sessionId": session_id})
        self._handles.pop(session_id, None)
        self._active_prompts.pop(session_id, None)

    async def close(self) -> None:
        """Stop the acp process and release OS resources."""
        if self.process is None:
            return
        if self.process.stdin is not None:
            self.process.stdin.close()
        try:
            await asyncio.wait_for(self.process.wait(), timeout=5)
        except asyncio.TimeoutError:
            self.process.terminate()
            await self.process.wait()
        if self._reader_task is not None:
            await self._reader_task
        if self._stderr_task is not None:
            await self._stderr_task
        self.process = None

    # ── event iterator ─────────────────────────────────────────────────

    async def _event_iterator(self) -> AsyncIterator[BackendEvent]:
        """Yield portable BackendEvents from the ACP notification queue."""
        while True:
            message = await self.notifications.get()
            event = self._translate_notification(message)
            if event is not None:
                yield event

    def _translate_notification(
        self, message: dict[str, Any]
    ) -> BackendEvent | None:
        """Translate one ACP message into a BackendEvent.

        Handles:
        - ``session/update`` with ``agentMessage`` → role_message
          (foreman session only; designer/machinist messages are internal)
        - ``session/prompt`` response with ``stopReason`` → turn_completed
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
                if role == "foreman" and text:
                    return BackendEvent(
                        kind="role_message",
                        role="foreman",
                        text=text,
                    )
            return None

        if method == "session/prompt":
            # This is a server-to-client notification about a completed
            # prompt (the response-to-request was already handled by
            # _read_stdout).  The ACP spec sends session/update for
            # streaming; session/prompt as a notification carries the
            # final stop reason.  We treat it as turn_completed.
            session_id = params.get("sessionId", "")
            role_info = self._handles.get(session_id)
            role = role_info[0] if role_info else None
            return BackendEvent(
                kind="turn_completed",
                role=role,
                delivery_id=session_id,
            )

        return None

    # ── JSON-RPC plumbing ──────────────────────────────────────────────

    async def _request(
        self, method: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Send a JSON-RPC request and await the response."""
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
        return await asyncio.wait_for(future, timeout=30)

    async def _send_async(self, method: str, params: dict[str, Any]) -> int:
        """Send a JSON-RPC request and return the request_id immediately.

        The response is handled asynchronously by ``_read_stdout``.
        Used for ``session/prompt`` where we want to return a receipt
        without waiting for the full agent turn to complete.
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

    async def _send_notify(
        self, method: str, params: dict[str, Any]
    ) -> None:
        """Send a JSON-RPC notification without awaiting a response.

        Used for fire-and-forget operations like the initial context
        prompt in ``open_role``.  Drains stdin synchronously before
        returning.
        """
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
                await self.notifications.put(message)

    async def _drain_stderr(self) -> None:
        """Drain stderr (Hermes logs to stderr in ACP mode)."""
        assert self.process is not None and self.process.stderr is not None
        while await self.process.stderr.readline():
            pass


# ── registration ─────────────────────────────────────────────────────────

from . import _register  # noqa: E402

_register("hermes", HermesBackend)
