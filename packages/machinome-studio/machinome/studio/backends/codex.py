"""Codex agent backend — wraps ``codex app-server --stdio``.

The ``CodexBackend`` class owns one Codex app-server subprocess and
translates its native JSON-RPC thread/turn operations into the portable
``AgentBackend`` protocol.  The orchestrator never sees ``threadId``,
``turnId``, or other Codex-specific identifiers.
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import tomllib
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


# ── InactiveTurn (delivery completion race) ────────────────────────────────


class InactiveTurn(RuntimeError):
    """The expected turn completed before steering was accepted."""


# ── CodexBackend ───────────────────────────────────────────────────────────


class CodexBackend:
    """AgentBackend backed by a ``codex app-server --stdio`` subprocess."""

    events: AsyncIterator[BackendEvent]

    def __init__(
        self,
        cwd: Path,
        *,
        project: Path | None = None,
        command: str | Sequence[str] = "codex",
        broker_url: str = "http://127.0.0.1:9000",
        solid_command: str | Sequence[str] = "solid",
        model_callback_url: str | None = None,
    ) -> None:
        self.cwd = cwd.resolve()
        self.project = (project or cwd).resolve()
        self.command = (command,) if isinstance(command, str) else tuple(command)
        self.broker_url = broker_url
        self.solid_command = (solid_command,) if isinstance(solid_command, str) else tuple(solid_command)
        self.model_callback_url = model_callback_url
        self.process: asyncio.subprocess.Process | None = None
        self.notifications: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._next_id = 0
        self._reader_task: asyncio.Task[None] | None = None
        self._stderr_task: asyncio.Task[None] | None = None
        # Map backend_id → (role, thread_id) so events can resolve the role.
        self._handles: dict[str, tuple[str, str]] = {}
        self.events = self._event_iterator()

    # ── AgentBackend protocol ────────────────────────────────────────────

    async def start(self) -> None:
        """Launch the Codex app-server subprocess (idempotent)."""
        if self.process is not None:
            return
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            "app-server",
            "--stdio",
            cwd=self.cwd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={
                **os.environ,
                "FLOOR_URL": self.broker_url,
                "PYTHONPATH": os.pathsep.join(
                    item for item in (str(self.cwd), os.environ.get("PYTHONPATH", "")) if item
                ),
            },
            start_new_session=True,
        )
        self._reader_task = asyncio.create_task(self._read_stdout())
        self._stderr_task = asyncio.create_task(self._drain_stderr())
        await self._request(
            "initialize",
            {
                "clientInfo": {
                    "name": "solid-node-shop-orchestrator",
                    "title": "solid-node shop orchestrator",
                    "version": "0.1.0",
                },
                "capabilities": {"experimentalApi": True},
            },
        )
        await self._notify("initialized", {})

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        """Create a persistent Codex thread for *role* with *context*."""
        config_path = self.cwd / ".codex" / "agents" / f"{role}.toml"
        with config_path.open("rb") as handle:
            config = tomllib.load(handle)
        role_instructions = str(config.get("developer_instructions", ""))
        runtime_instructions = (
            f"Shop checkout: {context.shop_checkout}\n"
            f"Active project: {context.active_project}\n"
            "Treat the active project as the sole mechanical-project repository for this shop run. "
            "Shop role cards and skills come from the shop checkout named above.\n\n"
        )
        if role == "machinist" and context.model_callback_url is not None:
            runtime_instructions += (
                "Live model development command (run it from the active project and keep it running "
                "throughout an active machining assignment):\n"
                f"{shlex.join(self.solid_command)} develop root "
                f"--callback {shlex.quote(context.model_callback_url)}\n\n"
            )
        result = await self._request(
            "thread/start",
            {
                "cwd": context.active_project,
                "model": config.get("model"),
                "developerInstructions": runtime_instructions + role_instructions,
                "sandbox": "workspace-write",
                "serviceName": f"solid-node-shop-{role}",
            },
        )
        thread_id = str(result["thread"]["id"])
        handle = RoleHandle(backend_id=thread_id, role=role)
        self._handles[thread_id] = (role, thread_id)
        return handle

    async def deliver_start(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
        """Start a new turn on an idle role thread."""
        thread_id = handle.backend_id
        result = await self._request(
            "turn/start",
            {"threadId": thread_id, "input": [{"type": "text", "text": message}]},
        )
        turn_id = str(result["turn"]["id"])
        return DeliveryReceipt(delivery_id=turn_id, accepted=True)

    async def deliver(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
        """Default: start a new delivery (orchestrator uses deliver_start/deliver_steer)."""
        return await self.deliver_start(handle, message)

    async def deliver_steer(
        self, handle: RoleHandle, expected_delivery_id: str, message: str
    ) -> DeliveryReceipt:
        """Steer an active turn.  Raises ``InactiveTurn`` on a completion race."""
        thread_id = handle.backend_id
        try:
            await self._request(
                "turn/steer",
                {
                    "threadId": thread_id,
                    "expectedTurnId": expected_delivery_id,
                    "input": [{"type": "text", "text": message}],
                },
            )
        except RuntimeError as error:
            msg = str(error).lower()
            if "active turn" in msg or "thread not found" in msg:
                raise InactiveTurn from error
            raise
        return DeliveryReceipt(delivery_id=expected_delivery_id, accepted=True)

    async def interrupt(self, handle: RoleHandle) -> None:
        """Interrupt the active turn (best-effort, uses thread ID as turn ID)."""
        thread_id = handle.backend_id
        await self._request("turn/interrupt", {"threadId": thread_id, "turnId": thread_id})

    async def close_role(self, handle: RoleHandle) -> None:
        """Archive the Codex thread (best-effort)."""
        thread_id = handle.backend_id
        try:
            await self._request("thread/archive", {"threadId": thread_id})
        except RuntimeError as error:
            if "no rollout found for thread id" not in str(error).lower():
                raise

    async def close(self) -> None:
        """Stop the app-server process and release OS resources."""
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

    # ── legacy API (used by acceptance tests) ────────────────────────────

    async def start_thread(self, role: str) -> str:
        """Legacy: open a role thread and return its thread ID."""
        ctx = RoleContext(
            shop_checkout=str(self.cwd),
            active_project=str(self.project),
            model_callback_url=self.model_callback_url if role == "machinist" else None,
        )
        handle = await self.open_role(role, ctx)
        return handle.backend_id

    async def start_turn(self, thread_id: str, message: str) -> str:
        """Legacy: start a turn and return the turn ID."""
        handle = RoleHandle(backend_id=thread_id, role="")
        receipt = await self.deliver_start(handle, message)
        return receipt.delivery_id

    async def steer_turn(
        self, thread_id: str, turn_id: str, message: str
    ) -> None:
        """Legacy: steer an active turn."""
        handle = RoleHandle(backend_id=thread_id, role="")
        await self.deliver_steer(handle, turn_id, message)

    async def interrupt_turn(self, thread_id: str, turn_id: str) -> None:
        """Legacy: interrupt an active turn."""
        handle = RoleHandle(backend_id=thread_id, role="")
        await self.interrupt(handle)

    async def close_thread(self, thread_id: str) -> None:
        """Legacy: archive a thread."""
        handle = RoleHandle(backend_id=thread_id, role="")
        await self.close_role(handle)

    # ── event iterator ───────────────────────────────────────────────────

    async def _event_iterator(self) -> AsyncIterator[BackendEvent]:
        """Yield portable BackendEvents from the app-server notification queue."""
        while True:
            message = await self.notifications.get()
            event = self._translate_notification(message)
            if event is not None:
                yield event

    def _translate_notification(self, message: dict[str, Any]) -> BackendEvent | None:
        """Translate one app-server notification into a BackendEvent."""
        method = message.get("method")
        params = message.get("params", {})

        if method == "item/completed":
            item = params.get("item", {})
            thread_id = params.get("threadId")
            if thread_id is None:
                return None
            role_info = self._handles.get(thread_id)
            if role_info is None:
                return None
            role = role_info[0]
            if (
                role == "foreman"
                and item.get("type") == "agentMessage"
                and str(item.get("text", "")).strip()
            ):
                return BackendEvent(
                    kind="role_message",
                    role="foreman",
                    text=str(item["text"]).strip(),
                )
            return None

        if method == "turn/started":
            thread_id = params.get("threadId")
            role_info = self._handles.get(thread_id)
            if role_info is None:
                return None
            return BackendEvent(
                kind="turn_started",
                role=role_info[0],
                delivery_id=thread_id,
            )

        if method == "turn/completed":
            thread_id = params.get("threadId")
            role_info = self._handles.get(thread_id)
            if role_info is None:
                return None
            return BackendEvent(
                kind="turn_completed",
                role=role_info[0],
                delivery_id=thread_id,
            )

        return None

    # ── JSON-RPC plumbing ────────────────────────────────────────────────

    async def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("app-server is not running")
        self._next_id += 1
        request_id = self._next_id
        future: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self._pending[request_id] = future
        payload = json.dumps({"id": request_id, "method": method, "params": params}) + "\n"
        self.process.stdin.write(payload.encode())
        await self.process.stdin.drain()
        return await asyncio.wait_for(future, timeout=30)

    async def _notify(self, method: str, params: dict[str, Any]) -> None:
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("app-server is not running")
        payload = json.dumps({"method": method, "params": params}) + "\n"
        self.process.stdin.write(payload.encode())
        await self.process.stdin.drain()

    async def _read_stdout(self) -> None:
        assert self.process is not None and self.process.stdout is not None
        while line := await self.process.stdout.readline():
            message = json.loads(line)
            request_id = message.get("id")
            if request_id is not None and ("result" in message or "error" in message):
                future = self._pending.pop(request_id, None)
                if future is None:
                    continue
                if "error" in message:
                    future.set_exception(RuntimeError(json.dumps(message["error"])))
                else:
                    future.set_result(message["result"])
            elif "method" in message:
                await self.notifications.put(message)

    async def _drain_stderr(self) -> None:
        assert self.process is not None and self.process.stderr is not None
        while await self.process.stderr.readline():
            pass


# ── registration ───────────────────────────────────────────────────────────

from . import _register  # noqa: E402

_register("codex", CodexBackend)
