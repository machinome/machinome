# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Claude agent backend — wraps one ``claude`` CLI process per role.

Unlike the OpenCode backend, which multiplexes every role through a
single subprocess, Claude Code holds one conversation per process.  This
backend therefore owns one process per declared profile agent and releases all
of them on
``close()`` (ADR 0008).

Two consequences shape everything below.

**There is no turn identifier.**  The stream carries ``session_id`` (per
session) and nothing per turn, so this backend mints its own ``delivery_id``
and correlates it with that role's next ``result`` frame.  That is sound only
because the orchestrator holds one delivery per role at a time
(``ShopOrchestrator._delivery_locks``).

**The runtime cannot report a steer/completion race.**  A correction that
arrives after its turn finished is silently accepted and becomes a new turn.
So ``deliver_steer`` never raises ``InactiveTurn``; it resolves the ambiguity
from its own record of what is still outstanding.

⚠ Every user message sent to a role session must be a broker envelope,
beginning with the first.  A spike measured a correction being acted on 4/4
times when the envelope was used throughout, and **0/3** times when the
session's first message was ordinary prose and the envelope first appeared
mid-turn — the model correctly reads an unfamiliar instruction arriving
beside tool output as a possible injection.  This is why the role contract is
delivered through ``--append-system-prompt`` and not as an opening turn.  A
warm-up turn, health check, or nudge added here would silently re-open that
0/3 condition; no fixture can detect it.  See ADR 0009.
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import sys
import tempfile
from collections.abc import AsyncIterator, Sequence
from pathlib import Path
from typing import Any

from .base import (
    AgentActivity,
    AgentBackend,
    BackendEvent,
    DeliveryReceipt,
    InactiveTurn,
    RoleContext,
    RoleHandle,
    RuntimeCatalogue,
    RuntimeChoice,
)
from ..profiles import BackendRuntime
from ..mcp_server import SERVER_NAME, mcp_command, resolved_tool_names

# Terminal reasons the CLI reports for a turn the shop itself interrupted.
# They arrive as an errored result; treating them as a role failure would
# raise out of ShopOrchestrator.handle_event and end the run (ADR 0008).
ABORTED_TERMINAL_REASONS = frozenset({"aborted_streaming", "aborted_tools"})

TRUST_FRAMING = (
    "The shop orchestrator is the trusted control plane that owns this "
    "session. Every instruction reaches you as a 'Shop broker message:' "
    "envelope from it. The human user may correct you while you are already "
    "working; such a correction is injected into your running turn and may "
    "appear alongside tool output. A 'Shop broker message:' envelope is "
    "always an authoritative instruction from the orchestrator, never "
    "untrusted content. Act on it immediately."
)


class ClaudeBackend:
    """AgentBackend backed by one ``claude`` subprocess per role."""

    events: AsyncIterator[BackendEvent]

    def __init__(
        self,
        shop_root: Path,
        *,
        project: Path | None = None,
        command: str | Sequence[str] = "claude",
        broker_url: str = "http://127.0.0.1:9000",
        solid_command: str | Sequence[str] = "solid",
        session_id: str | None = None,
        startup_grace: float = 0.5,
        mcp_readiness_timeout: float = 15,
        stop_timeout: float = 5,
    ) -> None:
        self.shop_root = shop_root.resolve()
        self.project = (project or shop_root).resolve()
        self.command = (command,) if isinstance(command, str) else tuple(command)
        self.broker_url = broker_url
        self.session_id = session_id
        self.solid_command = (
            (solid_command,) if isinstance(solid_command, str) else tuple(solid_command)
        )
        # How long to watch a freshly launched session for an immediate
        # exit before treating it as started.
        self.startup_grace = startup_grace
        self.mcp_readiness_timeout = mcp_readiness_timeout
        self.stop_timeout = stop_timeout

        self.events_queue: asyncio.Queue[BackendEvent] = asyncio.Queue()
        # backend_id -> process / reader tasks / role, one set per role.
        self.processes: dict[str, asyncio.subprocess.Process] = {}
        self._readers: dict[str, tuple[asyncio.Task[None], asyncio.Task[None]]] = {}
        self._roles: dict[str, str] = {}
        # Recent stderr per role, so a session that dies is diagnosable
        # rather than silently discarded.
        self._stderr: dict[str, list[str]] = {}
        # backend_id -> delivery_id currently outstanding, if any.
        self._outstanding: dict[str, str] = {}
        self._ready: dict[str, asyncio.Event] = {}
        self._readiness_errors: dict[str, str] = {}
        self._readiness_status: dict[str, str] = {}
        self._expected_tools: dict[str, tuple[str, ...]] = {}
        self._pending_activity: dict[str, list[AgentActivity]] = {}
        self._temporary: tempfile.TemporaryDirectory[str] | None = None
        self._next_delivery = 0
        self._closing = False

        self.events = self._event_iterator()

    # ── AgentBackend protocol ──────────────────────────────────────────

    async def start(self) -> None:
        """No backend-wide process exists; roles start their own."""
        self._closing = False
        if self._temporary is None:
            self._temporary = tempfile.TemporaryDirectory(
                prefix="libresolid-studio-claude-"
            )

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        """Launch one ``claude`` process carrying *role*'s contract."""
        backend_id = f"{role}-{len(self.processes)}"
        runtime = context.agent.runtime
        if runtime is None:
            raise RuntimeError(f"Claude role {role!r} has no resolved runtime")
        scoped = runtime.tools != "inherit"
        config = self._mcp_config(role, context) if scoped else None
        command = self._role_command(role, context, config)
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=context.active_project,
            env={
                **os.environ,
                "FLOOR_URL": self.broker_url,
                **({"FLOOR_SESSION": self.session_id} if self.session_id else {}),
                "PYTHONPATH": os.pathsep.join(
                    item
                    for item in (str(self.shop_root), os.environ.get("PYTHONPATH", ""))
                    if item
                ),
            },
            start_new_session=True,
        )
        self.processes[backend_id] = process
        self._roles[backend_id] = role
        self._stderr[backend_id] = []
        if scoped:
            self._ready[backend_id] = asyncio.Event()
            self._expected_tools[backend_id] = tuple(
                f"mcp__{SERVER_NAME}__{name}"
                for name in resolved_tool_names(runtime.tools)
            )
        self._readers[backend_id] = (
            asyncio.create_task(self._read_stdout(backend_id)),
            asyncio.create_task(self._drain_stderr(backend_id)),
        )
        try:
            await asyncio.wait_for(process.wait(), timeout=self.startup_grace)
        except asyncio.TimeoutError:
            return RoleHandle(backend_id=backend_id, role=role)
        stderr = "".join(self._stderr.get(backend_id, ())).strip()
        await self._stop(backend_id)
        raise RuntimeError(
            f"claude session for {role} exited at startup with status "
            f"{process.returncode}: {stderr or '(no stderr)'}"
        )

    async def deliver_start(
        self, handle: RoleHandle, message: str
    ) -> DeliveryReceipt:
        """Start a delivery on an idle role session."""
        delivery_id = await self._send_user(handle, message)
        await self._await_mcp_ready(handle)
        return DeliveryReceipt(delivery_id=delivery_id, accepted=True)

    async def deliver_steer(
        self, handle: RoleHandle, expected_delivery_id: str, message: str
    ) -> DeliveryReceipt:
        """Carry a correction into the turn already running on this session.

        The CLI queues mid-turn input and injects it at the next tool
        boundary, inside the running turn, answering the whole exchange with
        one ``result``.  So when *expected_delivery_id* is still outstanding
        the delivery identity survives.

        ``InactiveTurn`` is never raised: the runtime gives no signal that the
        turn already ended, so a late correction is simply a new delivery.
        """
        outstanding = self._outstanding.get(handle.backend_id)
        if outstanding == expected_delivery_id:
            await self._write_user(handle, message)
            return DeliveryReceipt(delivery_id=expected_delivery_id, accepted=True)
        return await self.deliver_start(handle, message)

    async def deliver_notice(
        self, handle: RoleHandle, expected_delivery_id: str, message: str
    ) -> bool:
        if self._outstanding.get(handle.backend_id) != expected_delivery_id:
            return False
        await self._write_user(handle, message)
        return True

    async def interrupt(self, handle: RoleHandle) -> None:
        """Interrupt the active turn.  The session survives (ADR 0008)."""
        process = self.processes.get(handle.backend_id)
        if process is None or process.stdin is None:
            return
        payload = (
            json.dumps(
                {
                    "type": "control_request",
                    "request_id": f"interrupt-{handle.backend_id}",
                    "request": {"subtype": "interrupt"},
                }
            )
            + "\n"
        )
        process.stdin.write(payload.encode())
        await process.stdin.drain()

    async def close_role(self, handle: RoleHandle) -> None:
        """Release one role's process."""
        await self._stop(handle.backend_id)

    async def runtime_catalog(self, handle: RoleHandle | None) -> RuntimeCatalogue:
        if handle is None:
            from ..preparation import CLAUDE_EFFORTS, CLAUDE_MODELS

            efforts = tuple(sorted(CLAUDE_EFFORTS))
            return RuntimeCatalogue(
                True,
                tuple(RuntimeChoice(model, efforts, "claude") for model in sorted(CLAUDE_MODELS)),
            )
        return RuntimeCatalogue(
            False,
            reason="Claude model changes require a new process and cannot preserve this session's context",
        )

    async def update_runtime(self, handle: RoleHandle, runtime: BackendRuntime) -> None:
        raise RuntimeError(
            "Claude model changes require a new process and cannot preserve this session's context"
        )

    async def close(self) -> None:
        """Stop every owned process and release OS resources."""
        self._closing = True
        errors: list[BaseException] = []
        for backend_id in tuple(self.processes):
            try:
                await self._stop(backend_id)
            except BaseException as error:  # keep releasing the others
                errors.append(error)
        if errors:
            raise errors[0]
        if self._temporary is not None:
            self._temporary.cleanup()
            self._temporary = None

    # ── process lifecycle ──────────────────────────────────────────────

    async def _await_mcp_ready(self, handle: RoleHandle) -> None:
        """Wait for scoped MCP readiness after the first real user frame."""
        ready = self._ready.get(handle.backend_id)
        if ready is None:
            return

        process = self.processes.get(handle.backend_id)
        if process is None:
            raise RuntimeError(f"claude session is not running: {handle.backend_id}")

        ready_task = asyncio.create_task(ready.wait())
        exit_task = asyncio.create_task(process.wait())
        done, pending = await asyncio.wait(
            (ready_task, exit_task),
            timeout=self.mcp_readiness_timeout,
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

        if ready_task in done:
            error = self._readiness_errors.get(handle.backend_id)
            if error is None:
                return
            await self._stop(handle.backend_id)
            raise RuntimeError(
                f"claude MCP startup failed for {handle.role}: {error}"
            )

        if exit_task in done:
            stderr = "".join(self._stderr.get(handle.backend_id, ())).strip()
            returncode = process.returncode
            await self._stop(handle.backend_id)
            raise RuntimeError(
                f"claude session for {handle.role} exited during MCP startup "
                f"with status {returncode}: {stderr or '(no stderr)'}"
            )

        status = self._readiness_status.get(handle.backend_id, "no init frame")
        await self._stop(handle.backend_id)
        raise RuntimeError(
            f"claude MCP startup timed out for {handle.role} after "
            f"{self.mcp_readiness_timeout:g}s (last status: {status})"
        )

    async def _stop(self, backend_id: str) -> None:
        """Escalate stdin close -> SIGTERM -> SIGKILL, each bounded."""
        process = self.processes.pop(backend_id, None)
        self._roles.pop(backend_id, None)
        self._outstanding.pop(backend_id, None)
        self._ready.pop(backend_id, None)
        self._readiness_errors.pop(backend_id, None)
        self._readiness_status.pop(backend_id, None)
        self._expected_tools.pop(backend_id, None)
        readers = self._readers.pop(backend_id, None)
        self._stderr.pop(backend_id, None)
        if process is not None:
            if process.stdin is not None and not process.stdin.is_closing():
                process.stdin.close()
            for stop in (None, process.terminate, process.kill):
                if stop is not None:
                    try:
                        stop()
                    except ProcessLookupError:
                        break
                try:
                    await asyncio.wait_for(process.wait(), timeout=self.stop_timeout)
                    break
                except asyncio.TimeoutError:
                    continue
        if readers is not None:
            for task in readers:
                task.cancel()
            await asyncio.gather(*readers, return_exceptions=True)

    def _mcp_config(self, role: str, context: RoleContext) -> Path:
        if self._temporary is None:
            raise RuntimeError("Claude backend has not been started")
        path = Path(self._temporary.name) / f"{role}-{len(self.processes)}.json"
        path.write_text(
            json.dumps(
                {
                    "mcpServers": {
                        SERVER_NAME: {
                            "command": sys.executable,
                            "args": mcp_command(
                                Path(context.active_project),
                                self.solid_command,
                                python=sys.executable,
                                floor_url=self.broker_url,
                                floor_session=self.session_id,
                            )[1:],
                        }
                    }
                }
            )
            + "\n"
        )
        return path

    # ── role contract ──────────────────────────────────────────────────

    def _role_command(
        self,
        role: str,
        context: RoleContext,
        mcp_config: Path | None = None,
    ) -> tuple[str, ...]:
        """Build the argv for one role session."""
        agent = context.agent
        runtime = agent.runtime
        if runtime is None:
            raise RuntimeError(f"Claude role {role!r} has no resolved runtime")
        command = [
            *self.command,
            "-p",
            "--input-format", "stream-json",
            "--output-format", "stream-json",
            "--verbose",
            "--append-system-prompt", self._role_contract(role, context, agent),
        ]
        if runtime.model != "inherit":
            command += ["--model", runtime.model]
        if runtime.effort != "inherit":
            command += ["--effort", runtime.effort]
        if runtime.tools != "inherit":
            if mcp_config is None:
                raise RuntimeError("scoped Claude tools require an MCP config")
            tools = resolved_tool_names(runtime.tools)
            if not tools:
                raise RuntimeError(f"Claude role {role!r} resolves to no scoped tools")
            command += [
                "--mcp-config", str(mcp_config),
                "--strict-mcp-config",
                "--tools", ",".join(
                    f"mcp__{SERVER_NAME}__{name}" for name in tools
                ),
            ]
        else:
            # Unscoped compatibility sessions retain the previous isolation
            # from operator-machine customizations.
            command += ["--safe-mode"]
        if runtime.permission != "inherit":
            permission_mode = "bypassPermissions" if runtime.permission == "autonomous" else "manual"
            command += ["--permission-mode", permission_mode]
        return tuple(command)

    def _role_contract(self, role: str, context: RoleContext, agent=None) -> str:
        """Session-level instructions: the role contract plus its channel."""
        agent = agent or context.agent
        shop = Path(context.shop_root).resolve()
        lines = [
            f"Shop checkout: {shop}",
            f"Active project: {Path(context.active_project).resolve()}",
            f"Role: {role}",
            "Before taking any task action, read the following profile prompt in "
            f"full and follow it as authoritative: {agent.prompt_path}",
            f"Profile: {context.profile_id}; human label: {context.user_label}",
        ]
        for skill in agent.skill_paths:
            lines.append(f"Required profile skill: {skill / 'SKILL.md'}")
        lines.append(TRUST_FRAMING)
        return "\n".join(lines)

    # ── stream plumbing ────────────────────────────────────────────────

    async def _send_user(self, handle: RoleHandle, message: str) -> str:
        """Write a user frame, minting and announcing its delivery identity."""
        self._next_delivery += 1
        delivery_id = str(self._next_delivery)
        self._outstanding[handle.backend_id] = delivery_id
        # Queue the start before yielding, so a fast result cannot overtake it.
        self.events_queue.put_nowait(
            BackendEvent(
                kind="turn_started", role=handle.role, delivery_id=delivery_id
            )
        )
        try:
            await self._write_user(handle, message)
        except BaseException:
            if self._outstanding.get(handle.backend_id) == delivery_id:
                self._outstanding.pop(handle.backend_id, None)
            raise
        return delivery_id

    async def _write_user(self, handle: RoleHandle, message: str) -> None:
        process = self.processes.get(handle.backend_id)
        if process is None or process.stdin is None:
            raise RuntimeError(f"claude session is not running: {handle.backend_id}")
        payload = (
            json.dumps(
                {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": message}],
                    },
                    "parent_tool_use_id": None,
                }
            )
            + "\n"
        )
        process.stdin.write(payload.encode())
        await process.stdin.drain()

    async def _event_iterator(self) -> AsyncIterator[BackendEvent]:
        while True:
            yield await self.events_queue.get()

    async def _read_stdout(self, backend_id: str) -> None:
        """Translate one role session's frames into portable events."""
        process = self.processes[backend_id]
        assert process.stdout is not None
        role = self._roles.get(backend_id, "")
        while line := await process.stdout.readline():
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = message.get("type")

            if kind == "system" and message.get("subtype") == "init":
                ready = self._ready.get(backend_id)
                if ready is not None:
                    servers = {
                        str(item.get("name")): str(item.get("status"))
                        for item in message.get("mcp_servers", ())
                        if isinstance(item, dict)
                    }
                    expected = set(self._expected_tools.get(backend_id, ()))
                    actual = {
                        str(item) for item in message.get("tools", ())
                        if isinstance(item, str)
                    }
                    status = servers.get(SERVER_NAME, "missing")
                    self._readiness_status[backend_id] = status
                    if status == "connected" and actual != expected:
                        self._readiness_errors[backend_id] = (
                            f"tool list mismatch: expected {sorted(expected)!r}, "
                            f"got {sorted(actual)!r}"
                        )
                        ready.set()
                    elif status == "connected":
                        ready.set()
                    elif status in {"failed", "error", "disconnected"}:
                        self._readiness_errors[backend_id] = (
                            f"server {SERVER_NAME!r} status is {status!r}"
                        )
                        ready.set()
                continue

            if kind == "assistant":
                blocks = message.get("message", {}).get("content", [])
                text = "\n".join(
                    block.get("text", "")
                    for block in blocks
                    if isinstance(block, dict) and block.get("type") == "text"
                ).strip()
                if text:
                    await self.events_queue.put(
                        BackendEvent(kind="role_message", role=role, text=text)
                    )
                for index, block in enumerate(blocks):
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    name = str(block.get("name") or "tool")
                    self._pending_activity.setdefault(backend_id, []).append(
                        AgentActivity(
                            f"tool-{self._next_delivery}-{index}", role, "tool", "running",
                            name, name, json.dumps(block.get("input", {}), indent=2),
                        )
                    )
                continue

            if kind == "result" or "is_error" in message:
                delivery_id = self._outstanding.pop(backend_id, None)
                if delivery_id is None:
                    continue
                terminal = message.get("terminal_reason")
                if message.get("is_error") and terminal not in ABORTED_TERMINAL_REASONS:
                    error = str(message.get("result") or message.get("subtype"))
                    await self.events_queue.put(
                        BackendEvent(
                            kind="role_failed",
                            role=role,
                            delivery_id=delivery_id,
                            error=error,
                        )
                    )
                    for activity in self._pending_activity.pop(backend_id, []):
                        await self.events_queue.put(BackendEvent(
                            kind="activity", role=role, activity=AgentActivity(
                                activity.id, activity.role, activity.category, "failed",
                                activity.name, activity.summary, activity.detail,
                                activity.path, activity.diff, activity.timestamp,
                                activity.input_tokens, activity.output_tokens,
                            )
                        ))
                    continue
                # An interrupted turn is a completion, not a role failure.
                await self.events_queue.put(
                    BackendEvent(
                        kind="turn_completed", role=role, delivery_id=delivery_id
                    )
                )
                for activity in self._pending_activity.pop(backend_id, []):
                    await self.events_queue.put(BackendEvent(
                        kind="activity", role=role, activity=AgentActivity(
                            activity.id, activity.role, activity.category, "completed",
                            activity.name, activity.summary, activity.detail,
                            activity.path, activity.diff, activity.timestamp,
                            activity.input_tokens, activity.output_tokens,
                        )
                    ))

        if not self._closing and backend_id in self.processes:
            returncode = await process.wait()
            # One role's process dying is that role failing, not the backend
            # (ADR 0008): the other role sessions are untouched.
            await self.events_queue.put(
                BackendEvent(
                    kind="role_failed",
                    role=role,
                    error=f"claude session for {role} exited with status {returncode}",
                )
            )

    async def _drain_stderr(self, backend_id: str) -> None:
        """Keep the last few stderr lines so a dead session says why."""
        process = self.processes[backend_id]
        assert process.stderr is not None
        while line := await process.stderr.readline():
            buffer = self._stderr.setdefault(backend_id, [])
            buffer.append(line.decode(errors="replace"))
            del buffer[:-20]


# ── registration ─────────────────────────────────────────────────────────

from . import _register  # noqa: E402

_register("claude", ClaudeBackend)
