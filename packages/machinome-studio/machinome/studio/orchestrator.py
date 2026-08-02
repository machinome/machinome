"""Pluggable agent-backend orchestration for a live shop run."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Sequence
from typing import Any, Protocol

import uvicorn

from .app import Broker, Envelope, create_app
from .backends.base import AgentBackend, BackendEvent, DeliveryReceipt, InactiveTurn, RoleContext, RoleHandle
from .backends import create_backend
from .preparation import PreparationError, default_project_home, default_solid_command, prepare_project, primary_shop_root
from .profiles import ProfileError, RuntimeProfile, load_profile


class BrokerControl(Protocol):
    async def manifest(self, role: str, label: str) -> None: ...
    async def mark_delivered(self, sequence: int) -> None: ...
    async def record_conversation(self, author: str, text: str) -> None: ...
    async def register_direct_delivery(self, role: str, delivery_id: str) -> None: ...
    async def turn_started(self, role: str, delivery_id: str) -> None: ...
    async def turn_completed(self, role: str, delivery_id: str) -> None: ...


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

    async def register_direct_delivery(self, role: str, delivery_id: str) -> None:
        self.broker.register_direct_delivery(role, delivery_id)

    async def turn_started(self, role: str, delivery_id: str) -> None:
        self.broker.turn_started(role, delivery_id)

    async def turn_completed(self, role: str, delivery_id: str) -> None:
        self.broker.turn_completed(role, delivery_id)


class ShopOrchestrator:
    """Own role sessions and perform only deterministic lifecycle and routing."""

    def __init__(
        self,
        backend: AgentBackend,
        broker: BrokerControl,
        *,
        profile: RuntimeProfile,
        shop_checkout: Path,
        active_project: Path,
    ) -> None:
        self.backend = backend
        self.broker = broker
        self.profile = profile
        self.shop_checkout = shop_checkout.resolve()
        self.active_project = active_project.resolve()
        self.roles: dict[str, RoleRuntime] = {}
        self._delivery_locks = {agent.id: asyncio.Lock() for agent in self.profile.agents}
        self._started_deliveries: set[tuple[str, str]] = set()
        self._completed_deliveries: set[tuple[str, str]] = set()

    async def open(self) -> None:
        """Start the backend and open one persistent session per role."""
        if hasattr(self.backend, "start"):
            await self.backend.start()
        try:
            for agent in self.profile.agents:
                role = agent.id
                handle = await self.backend.open_role(role, self._role_context(role))
                self.roles[role] = RoleRuntime(handle=handle)
                await self.broker.manifest(role, agent.label)
        except BaseException as opening_error:
            try:
                await self.close()
            except BaseException as cleanup_error:
                opening_error.add_note(
                    f"shop-open cleanup also failed: {cleanup_error}"
                )
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
                await self._adopt_started_delivery(role, runtime, receipt.delivery_id)
            else:
                active_delivery_id = runtime.active_delivery_id
                try:
                    receipt = await self.backend.deliver_steer(
                        runtime.handle, active_delivery_id, message
                    )
                    if receipt.delivery_id != active_delivery_id:
                        raise RuntimeError("backend steering changed the active delivery identity")
                except InactiveTurn:
                    receipt = await self.backend.deliver_start(runtime.handle, message)
                    await self._adopt_started_delivery(role, runtime, receipt.delivery_id)
            await self.broker.mark_delivered(sequence)

    async def _adopt_started_delivery(
        self,
        role: str,
        runtime: RoleRuntime,
        delivery_id: str,
    ) -> None:
        """Correlate a start receipt with events that may have won the race."""
        key = (role, delivery_id)
        runtime.active_delivery_id = delivery_id
        direct = self.profile.work_mode == "direct" and role == self.profile.user_agent_id
        if direct:
            await self.broker.register_direct_delivery(role, delivery_id)
            if key in self._started_deliveries:
                await self.broker.turn_started(role, delivery_id)
        if key in self._completed_deliveries:
            runtime.active_delivery_id = None
            if direct:
                await self.broker.turn_completed(role, delivery_id)

    async def handle_event(self, event: BackendEvent) -> None:
        """Consume one portable backend event."""
        if event.kind == "role_message" and event.role == self.profile.user_agent_id:
            if event.text and event.text.strip():
                await self.broker.record_conversation(self.profile.user_agent_id, event.text.strip())
        elif event.kind == "turn_started":
            runtime = self.roles.get(event.role or "")
            if runtime is not None and event.role is not None and event.delivery_id is not None:
                key = (event.role, event.delivery_id)
                if key in self._completed_deliveries or key in self._started_deliveries:
                    return
                self._started_deliveries.add(key)
                if event.delivery_id == runtime.active_delivery_id:
                    if self.profile.work_mode == "direct" and event.role == self.profile.user_agent_id:
                        await self.broker.turn_started(event.role, event.delivery_id)
        elif event.kind == "turn_completed":
            runtime = self.roles.get(event.role or "")
            if runtime is not None and event.role is not None and event.delivery_id is not None:
                key = (event.role, event.delivery_id)
                if key in self._completed_deliveries:
                    return
                self._completed_deliveries.add(key)
                if runtime.active_delivery_id == event.delivery_id:
                    runtime.active_delivery_id = None
                    if self.profile.work_mode == "direct" and event.role == self.profile.user_agent_id:
                        await self.broker.turn_completed(event.role, event.delivery_id)
        elif event.kind in {"role_failed", "backend_failed"}:
            subject = event.role or "agent backend"
            raise RuntimeError(f"{subject} failed: {event.error or 'unknown error'}")

    def _role_context(self, role: str) -> RoleContext:
        agent = self.profile.agent(role)
        return RoleContext(
            shop_checkout=str(self.shop_checkout),
            active_project=str(self.active_project),
            agent=agent,
            profile_id=self.profile.id,
            user_label=self.profile.user_label,
            user_agent_label=self.profile.user_agent.label,
        )

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
        errors: list[BaseException] = []
        for runtime in reversed(tuple(self.roles.values())):
            if runtime.active_delivery_id is not None:
                try:
                    await self.backend.interrupt(runtime.handle)
                except BaseException as error:
                    errors.append(error)
        for runtime in reversed(tuple(self.roles.values())):
            try:
                await self.backend.close_role(runtime.handle)
            except BaseException as error:
                errors.append(error)
        self.roles.clear()
        try:
            await self.backend.close()
        except BaseException as error:
            errors.append(error)
        if errors:
            raise errors[0]


async def _wait_for_runtime(
    server_task: asyncio.Task[None],
    route_tasks: Sequence[asyncio.Task[None]],
) -> None:
    """Wait until the HTTP server or a required routing loop stops.

    A routing loop ending is a runtime failure, not a reason to leave an
    apparently open but nonfunctional broker behind.
    """
    done, _ = await asyncio.wait(
        (server_task, *route_tasks), return_when=asyncio.FIRST_COMPLETED
    )
    for task in route_tasks:
        if task in done:
            await task
            raise RuntimeError("shop routing task stopped unexpectedly")
    await server_task


async def _shutdown_runtime(
    orchestrator: ShopOrchestrator | None,
    server: Any,
    server_task: asyncio.Task[None],
) -> None:
    """Release backend and HTTP resources even when one cleanup step fails."""
    errors: list[BaseException] = []
    if orchestrator is not None:
        try:
            await orchestrator.close()
        except BaseException as error:
            errors.append(error)
    if not server_task.done():
        server.should_exit = True
    try:
        await server_task
    except BaseException as error:
        errors.append(error)
    if errors:
        raise errors[0]


async def _serve(arguments: argparse.Namespace) -> None:
    shop_root = primary_shop_root(arguments.cwd)
    profile = load_profile(
        getattr(arguments, "profile", None),
        shop_root=shop_root,
        backend=arguments.backend,
    )
    project_home = arguments.project_home or default_project_home(arguments.cwd)
    solid_command = arguments.solid_command or default_solid_command(arguments.cwd)
    prepared = prepare_project(arguments.project_name, project_home=project_home, solid_command=solid_command,
                               shop_root=shop_root)
    broker = Broker(profile=profile)
    app = create_app(
        prepared.project_root,
        artifact_root=prepared.artifact_root,
        viewer_bundle=prepared.viewer_bundle,
        broker=broker,
        solid_command=prepared.solid_command,
        build_environment=prepared.build_environment,
        profile=profile,
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
        )
        orchestrator = ShopOrchestrator(
            backend,
            LocalBrokerControl(broker),
            profile=profile,
            shop_checkout=shop_root,
            active_project=prepared.project_root,
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
        await _wait_for_runtime(server_task, (delivery_task, event_task))
    except asyncio.CancelledError:
        pass
    finally:
        broker.shutdown()
        route_tasks = tuple(task for task in (delivery_task, event_task) if task is not None)
        for task in route_tasks:
            task.cancel()
        if route_tasks:
            await asyncio.gather(*route_tasks, return_exceptions=True)
        await _shutdown_runtime(orchestrator, server, server_task)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the event-driven agent shop")
    parser.add_argument("project_name", help="lowercase kebab-case project name below projects/")
    parser.add_argument("--port", type=int, default=int(os.environ.get("FLOOR_PORT", "9000")))
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="shop checkout containing role adapters")
    parser.add_argument("--backend", choices=("codex", "hermes", "claude", "opencode"), default="codex",
                        help="agent backend (default: codex)")
    parser.add_argument("--profile", help="runtime profile owned by this shop checkout")
    parser.add_argument("--project-home", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--solid-command", help=argparse.SUPPRESS)
    parser.add_argument("--backend-command", default=None, help=argparse.SUPPRESS)
    try:
        asyncio.run(_serve(parser.parse_args()))
    except (PreparationError, ProfileError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
