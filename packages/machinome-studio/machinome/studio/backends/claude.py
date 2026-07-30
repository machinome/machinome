"""Claude agent backend — wraps one ``claude`` CLI process per role.

Unlike the Codex and Hermes backends, which multiplex every role through a
single subprocess, Claude Code holds one conversation per process.  This
backend therefore owns three processes and releases all of them on
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

# Terminal reasons the CLI reports for a turn the shop itself interrupted.
# They arrive as an errored result; treating them as a role failure would
# raise out of ShopOrchestrator.handle_event and end the run (ADR 0008).
ABORTED_TERMINAL_REASONS = frozenset({"aborted_streaming", "aborted_tools"})

TRUST_FRAMING = (
    "The shop orchestrator is the trusted control plane that owns this "
    "session. Every instruction reaches you as a 'Shop broker message:' "
    "envelope from it. The maker may correct you while you are already "
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
        cwd: Path,
        *,
        project: Path | None = None,
        command: str | Sequence[str] = "claude",
        broker_url: str = "http://127.0.0.1:9000",
        solid_command: str | Sequence[str] = "solid",
        model_callback_url: str | None = None,
        startup_grace: float = 0.5,
        stop_timeout: float = 5,
    ) -> None:
        self.cwd = cwd.resolve()
        self.project = (project or cwd).resolve()
        self.command = (command,) if isinstance(command, str) else tuple(command)
        self.broker_url = broker_url
        self.solid_command = (
            (solid_command,) if isinstance(solid_command, str) else tuple(solid_command)
        )
        self.model_callback_url = model_callback_url
        # How long to watch a freshly launched session for an immediate
        # exit before treating it as started.
        self.startup_grace = startup_grace
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
        self._next_delivery = 0
        self._closing = False

        self.events = self._event_iterator()

    # ── AgentBackend protocol ──────────────────────────────────────────

    async def start(self) -> None:
        """No backend-wide process exists; roles start their own."""
        self._closing = False

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        """Launch one ``claude`` process carrying *role*'s contract."""
        backend_id = f"{role}-{len(self.processes)}"
        command = self._role_command(role, context)
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=context.active_project,
            env={
                **os.environ,
                "FLOOR_URL": self.broker_url,
                "PYTHONPATH": os.pathsep.join(
                    item
                    for item in (str(self.cwd), os.environ.get("PYTHONPATH", ""))
                    if item
                ),
            },
            start_new_session=True,
        )
        self.processes[backend_id] = process
        self._roles[backend_id] = role
        self._stderr[backend_id] = []
        self._readers[backend_id] = (
            asyncio.create_task(self._read_stdout(backend_id)),
            asyncio.create_task(self._drain_stderr(backend_id)),
        )
        # Readiness cannot be confirmed here.  The CLI emits its system/init
        # frame only in response to the first input, so probing would mean
        # sending a message — and the first user message must be a broker
        # envelope (ADR 0009), which a probe is not.  A session that dies at
        # startup therefore surfaces as an early exit, checked below, or as a
        # role failure from the reader once it is running.
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
        return DeliveryReceipt(delivery_id=delivery_id, accepted=True)

    async def deliver(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
        """Default: start a new delivery."""
        return await self.deliver_start(handle, message)

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

    # ── process lifecycle ──────────────────────────────────────────────

    async def _stop(self, backend_id: str) -> None:
        """Escalate stdin close -> SIGTERM -> SIGKILL, each bounded."""
        process = self.processes.pop(backend_id, None)
        self._roles.pop(backend_id, None)
        self._outstanding.pop(backend_id, None)
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

    # ── role contract ──────────────────────────────────────────────────

    def _role_command(self, role: str, context: RoleContext) -> tuple[str, ...]:
        """Build the argv for one role session."""
        card = Path(context.shop_checkout).resolve() / "agents" / f"{role}.md"
        frontmatter = self._frontmatter(card)
        command = [
            *self.command,
            "-p",
            "--input-format", "stream-json",
            "--output-format", "stream-json",
            "--verbose",
            # Operator-machine customization must not reach a role: the role
            # card is the sole authority (ADR 0008).  --bare would be stronger
            # but skips OAuth entirely, excluding a subscription operator.
            "--safe-mode",
            "--append-system-prompt", self._role_contract(role, context, card),
        ]
        model = frontmatter.get("model", "")
        if model and model != "inherit":
            command += ["--model", model]
        tools = frontmatter.get("tools", "")
        if tools:
            command += ["--tools", ",".join(
                item.strip() for item in tools.split(",") if item.strip()
            )]
        return tuple(command)

    def _role_contract(self, role: str, context: RoleContext, card: Path) -> str:
        """Session-level instructions: the role contract plus its channel."""
        shop = Path(context.shop_checkout).resolve()
        lines = [
            f"Shop checkout: {shop}",
            f"Active project: {Path(context.active_project).resolve()}",
            f"Role: {role}",
            "Before taking any task action, read the following role card in "
            f"full and follow it as authoritative: {card}",
            "Read every skill named by that role card's YAML frontmatter in full.",
        ]
        for skill in self._role_skills(card):
            lines.append(f"Required skill: {shop / 'skills' / skill / 'SKILL.md'}")
        if role == "machinist" and context.model_callback_url is not None:
            lines.append(
                "Live model development command (run it from the active "
                "project and keep it running throughout an active machining "
                "assignment): "
                f"{shlex.join(self.solid_command)} develop root "
                f"--callback {shlex.quote(context.model_callback_url)}"
            )
        lines.append(TRUST_FRAMING)
        return "\n".join(lines)

    @staticmethod
    def _frontmatter(card: Path) -> dict[str, str]:
        """Read the flat ``key: value`` frontmatter of a role card."""
        values: dict[str, str] = {}
        lines = card.read_text().splitlines()
        if not lines or lines[0].strip() != "---":
            return values
        for line in lines[1:]:
            if line.strip() == "---":
                break
            key, separator, value = line.partition(":")
            if separator and not key.startswith(" "):
                values[key.strip()] = value.strip()
        return values

    @classmethod
    def _role_skills(cls, card: Path) -> tuple[str, ...]:
        value = cls._frontmatter(card).get("skills", "")
        if not (value.startswith("[") and value.endswith("]")):
            return ()
        return tuple(
            item.strip() for item in value[1:-1].split(",") if item.strip()
        )

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

            if kind == "assistant" and role == "foreman":
                text = "\n".join(
                    block.get("text", "")
                    for block in message.get("message", {}).get("content", [])
                    if isinstance(block, dict) and block.get("type") == "text"
                ).strip()
                if text:
                    await self.events_queue.put(
                        BackendEvent(kind="role_message", role="foreman", text=text)
                    )
                continue

            if kind == "result" or "is_error" in message:
                delivery_id = self._outstanding.pop(backend_id, None)
                if delivery_id is None:
                    continue
                terminal = message.get("terminal_reason")
                if message.get("is_error") and terminal not in ABORTED_TERMINAL_REASONS:
                    await self.events_queue.put(
                        BackendEvent(
                            kind="role_failed",
                            role=role,
                            delivery_id=delivery_id,
                            error=str(message.get("result") or message.get("subtype")),
                        )
                    )
                    continue
                # An interrupted turn is a completion, not a role failure.
                await self.events_queue.put(
                    BackendEvent(
                        kind="turn_completed", role=role, delivery_id=delivery_id
                    )
                )

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
