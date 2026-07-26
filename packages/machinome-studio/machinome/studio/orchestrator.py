"""Pluggable agent-backend orchestration for a live shop run."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import secrets
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Sequence
from typing import Any, Protocol

import uvicorn

from .app import Broker, Envelope, ROLE_LABELS, create_app
from .backends.base import AgentBackend, BackendEvent, DeliveryReceipt, RoleContext, RoleHandle
from .backends.codex import InactiveTurn
from .backends import create_backend
from .preparation import PreparationError, default_project_home, default_solid_command, prepare_project


SHOP_ROLES = tuple(ROLE_LABELS)


class BrokerControl(Protocol):
    async def manifest(self, role: str, label: str) -> None: ...
    async def mark_delivered(self, sequence: int) -> None: ...
    async def record_conversation(self, author: str, text: str) -> None: ...


@dataclass
class RoleRuntime:
    handle: RoleHandle
    active_delivery_id: str | None = None


class LocalBrokerControl:
    def __init__(self, broker: Broker) -> None:
        self.broker = broker

    async def manifest(self, role: str, label: str) -> None:
        self.broker.manifest(role, label)

    async def mark_delivered(self, sequence: int) -> None:
        self.broker.mark_delivered(sequence)

    async def record_conversation(self, author: str, text: str) -> None:
        await self.broker.record_conversation(author, text)


class ShopOrchestrator:
    """Own role sessions and perform only deterministic lifecycle and routing."""

    def __init__(self, backend: AgentBackend, broker: BrokerControl) -> None:
        self.backend = backend
        self.broker = broker
        self.roles: dict[str, RoleRuntime] = {}
        self._delivery_locks = {role: asyncio.Lock() for role in SHOP_ROLES}
        self._completed_deliveries: set[str] = set()

    async def open(self) -> None:
        """Start the backend and open one persistent session per role."""
        if hasattr(self.backend, "start"):
            await self.backend.start()
        try:
            for role in SHOP_ROLES:
                handle = await self.backend.open_role(role, self._role_context(role))
                self.roles[role] = RoleRuntime(handle=handle)
                await self.broker.manifest(role, ROLE_LABELS[role])
        except BaseException:
            await self.close()
            raise

    async def deliver(self, envelope: Envelope | dict[str, Any]) -> None:
        value = envelope.delivery_value() if isinstance(envelope, Envelope) else envelope
        sequence = int(value["sequence"])
        role = str(value["recipient"])
        message = self._message(value)
        runtime = self.roles.get(role)
        if runtime is None:
            raise ValueError(f"unknown orchestrated role: {role}")
        async with self._delivery_locks[role]:
            if runtime.active_delivery_id is None:
                receipt = await self.backend.deliver_start(runtime.handle, message)
                did = receipt.delivery_id
                runtime.active_delivery_id = None if did in self._completed_deliveries else did
            else:
                try:
                    await self.backend.deliver_steer(
                        runtime.handle, runtime.active_delivery_id, message
                    )
                except InactiveTurn:
                    receipt = await self.backend.deliver_start(runtime.handle, message)
                    did = receipt.delivery_id
                    runtime.active_delivery_id = None if did in self._completed_deliveries else did
            await self.broker.mark_delivered(sequence)

    async def handle_event(self, event: BackendEvent) -> None:
        """Consume one portable backend event."""
        if event.kind == "role_message" and event.role == "foreman":
            if event.text and event.text.strip():
                await self.broker.record_conversation("foreman", event.text.strip())
        elif event.kind == "turn_started":
            runtime = self.roles.get(event.role or "")
            if runtime is not None and event.delivery_id is not None:
                runtime.active_delivery_id = event.delivery_id
        elif event.kind == "turn_completed":
            if event.delivery_id is not None:
                self._completed_deliveries.add(event.delivery_id)
            runtime = self.roles.get(event.role or "")
            if runtime is not None and runtime.active_delivery_id == event.delivery_id:
                runtime.active_delivery_id = None

    @staticmethod
    def _role_context(role: str) -> RoleContext:
        # Built by _serve and injected via a closure; see _serve below.
        return RoleContext(shop_checkout="", active_project="")

    @staticmethod
    def _message(value: dict[str, Any]) -> str:
        lines = [
            "Shop broker message:",
            f"kind: {value.get('kind', 'direction')}",
            f"sender: {value.get('sender', 'unknown')}",
            f"recipient: {value['recipient']}",
        ]
        assignment_id = value.get("assignment_id")
        if assignment_id:
            lines.append(f"assignment: {assignment_id}")
        if value.get("kind") == "assignment" and assignment_id:
            lines.extend(
                (
                    "ASSIGNMENT LIFECYCLE GATE:",
                    "Before anything else, your FIRST TOOL CALL must be:",
                    f"python -m floor.agent acknowledge --role {value['recipient']} --assignment {assignment_id}",
                    "Do not read files or investigate, load a role card or skill, start a development process, "
                    "or make any other tool call until that command succeeds.",
                )
            )
        lines.extend(("instruction:", str(value["body"])))
        return "\n".join(lines)

    async def close(self) -> None:
        for runtime in reversed(tuple(self.roles.values())):
            if runtime.active_delivery_id is not None:
                await self.backend.interrupt(runtime.handle)
        for runtime in reversed(tuple(self.roles.values())):
            await self.backend.close_role(runtime.handle)
        self.roles.clear()
        await self.backend.close()


async def _serve(arguments: argparse.Namespace) -> None:
    project_home = arguments.project_home or default_project_home(arguments.cwd)
    solid_command = arguments.solid_command or default_solid_command(arguments.cwd)
    prepared = prepare_project(arguments.project_name, project_home=project_home, solid_command=solid_command)
    broker = Broker()
    callback_token = secrets.token_urlsafe(24)
    callback_url = f"http://127.0.0.1:{arguments.port}/api/runs/shop-floor/model/ready/{callback_token}"
    app = create_app(
        prepared.project_root,
        artifact_root=prepared.artifact_root,
        callback_token=callback_token,
        broker=broker,
    )
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=arguments.port,
            log_level="info",
            timeout_graceful_shutdown=1,
        )
    )
    server_task = asyncio.create_task(server.serve())
    orchestrator: ShopOrchestrator | None = None
    delivery_task: asyncio.Task[None] | None = None
    event_task: asyncio.Task[None] | None = None
    try:
        while not server.started and not server_task.done():
            await asyncio.sleep(0.01)
        if server_task.done():
            await server_task
            raise RuntimeError("shop-floor server stopped before opening")

        backend = create_backend(
            arguments.backend,
            cwd=arguments.cwd,
            project=prepared.project_root,
            broker_url=f"http://127.0.0.1:{arguments.port}",
            command=getattr(arguments, "backend_command", None),
            solid_command=solid_command,
            model_callback_url=callback_url,
        )
        orchestrator = ShopOrchestrator(backend, LocalBrokerControl(broker))

        # Inject runtime context so open_role() can use it.
        orchestrator._role_context = lambda role: RoleContext(  # type: ignore[method-assign]
            shop_checkout=str(arguments.cwd.resolve()),
            active_project=str(prepared.project_root.resolve()),
            model_callback_url=callback_url if role == "machinist" else None,
        )

        await orchestrator.open()
        print(f"shop-floor open at http://127.0.0.1:{arguments.port}", flush=True)

        async def route_deliveries() -> None:
            assert orchestrator is not None
            async for envelope in broker.deliveries():
                await orchestrator.deliver(envelope)

        async def route_events() -> None:
            assert orchestrator is not None
            async for event in backend.events:
                await orchestrator.handle_event(event)

        delivery_task = asyncio.create_task(route_deliveries())
        event_task = asyncio.create_task(route_events())
        await server_task
    except asyncio.CancelledError:
        pass
    finally:
        broker.shutdown()
        route_tasks = tuple(task for task in (delivery_task, event_task) if task is not None)
        for task in route_tasks:
            task.cancel()
        if route_tasks:
            await asyncio.gather(*route_tasks, return_exceptions=True)
        if orchestrator is not None:
            await orchestrator.close()
        if not server_task.done():
            server.should_exit = True
            await server_task


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the event-driven agent shop")
    parser.add_argument("project_name", help="lowercase kebab-case project name below projects/")
    parser.add_argument("--port", type=int, default=int(os.environ.get("FLOOR_PORT", "9000")))
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="shop checkout containing role adapters")
    parser.add_argument("--backend", choices=("codex", "hermes"), default="codex",
                        help="agent backend (default: codex)")
    parser.add_argument("--project-home", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--solid-command", help=argparse.SUPPRESS)
    parser.add_argument("--backend-command", default=None, help=argparse.SUPPRESS)
    try:
        asyncio.run(_serve(parser.parse_args()))
    except PreparationError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
