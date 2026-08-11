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
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

import uvicorn

from .app import Broker, Envelope, SystemNotice, create_app
from .backends.base import AgentBackend, BackendEvent, DeliveryReceipt, InactiveTurn, RoleContext, RoleHandle
from .backends import create_backend, parse_backend_command_overrides
from .preparation import (
    PreparationError,
    ProjectRuntimeError,
    default_solid_command,
    prepare_project,
    read_project_runtime,
    shop_resource_root,
)
from .profiles import ProfileError, RuntimeProfile, load_profile, resolve_profile_runtime


class BrokerControl(Protocol):
    async def manifest(self, role: str, label: str) -> None: ...
    async def mark_delivered(self, sequence: int) -> None: ...
    async def record_conversation(self, author: str, text: str) -> None: ...
    async def register_direct_delivery(self, role: str, delivery_id: str) -> None: ...
    async def turn_started(self, role: str, delivery_id: str) -> None: ...
    async def turn_completed(self, role: str, delivery_id: str) -> None: ...
    async def role_failed(self, role: str, error: str) -> None: ...
    async def role_recovered(self, role: str) -> None: ...
    async def mark_delivery_failed(self, sequence: int, error: str) -> None: ...
    async def pending_system_notices(self, role: str) -> list[SystemNotice | dict[str, object]]: ...
    async def mark_system_notices_delivered(self, role: str, sequences: list[int]) -> None: ...


@dataclass
class RoleRuntime:
    handle: RoleHandle | None
    active_delivery_id: str | None = None
    failed: bool = False


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

    async def role_failed(self, role: str, error: str) -> None:
        self.broker.role_failed(role, error)

    async def role_recovered(self, role: str) -> None:
        self.broker.role_recovered(role)

    async def mark_delivery_failed(self, sequence: int, error: str) -> None:
        self.broker.mark_delivery_failed(sequence, error)

    async def pending_system_notices(self, role: str) -> list[SystemNotice]:
        return self.broker.pending_system_notices(role)

    async def mark_system_notices_delivered(self, role: str, sequences: list[int]) -> None:
        self.broker.mark_system_notices_delivered(role, sequences)


class ShopOrchestrator:
    """Own role sessions and perform only deterministic lifecycle and routing."""

    def __init__(
        self,
        backends: Mapping[str, AgentBackend] | AgentBackend,
        broker: BrokerControl,
        *,
        profile: RuntimeProfile,
        shop_root: Path,
        active_project: Path,
    ) -> None:
        self.broker = broker
        self.profile = profile
        if isinstance(backends, Mapping):
            self.backends_by_agent = dict(backends)
        else:
            self.backends_by_agent = {agent.id: backends for agent in profile.agents}
        roster = {agent.id for agent in profile.agents}
        if set(self.backends_by_agent) != roster:
            missing = sorted(roster - set(self.backends_by_agent))
            extra = sorted(set(self.backends_by_agent) - roster)
            raise ValueError(f"backend ownership must match the profile roster (missing={missing}, extra={extra})")
        distinct: list[AgentBackend] = []
        seen: set[int] = set()
        for agent in profile.agents:
            backend = self.backends_by_agent[agent.id]
            if id(backend) not in seen:
                seen.add(id(backend))
                distinct.append(backend)
        self.backends = tuple(distinct)
        self.shop_root = shop_root.resolve()
        self.active_project = active_project.resolve()
        self.roles: dict[str, RoleRuntime] = {}
        self._delivery_locks = {agent.id: asyncio.Lock() for agent in self.profile.agents}
        self._started_deliveries: set[tuple[str, str]] = set()
        self._completed_deliveries: set[tuple[str, str]] = set()

    async def open(self) -> None:
        """Start the backend and open one persistent session per role."""
        try:
            for backend in self.backends:
                await backend.start()
            for agent in self.profile.agents:
                role = agent.id
                handle = await self._backend(role).open_role(role, self._role_context(role))
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
        runtime = self.roles.get(role)
        if runtime is None:
            raise ValueError(f"unknown orchestrated role: {role}")
        async with self._delivery_locks[role]:
            notices = await self.broker.pending_system_notices(role)
            message = self._message(value, notices)
            if runtime.failed:
                accepted = await self._recover_and_deliver(role, runtime, sequence, message)
                if accepted and notices:
                    await self.broker.mark_system_notices_delivered(
                        role,
                        [self._notice_sequence(notice) for notice in notices],
                    )
                return
            if runtime.handle is None:
                raise RuntimeError(f"{role} has no open backend session")
            if runtime.active_delivery_id is None:
                receipt = await self._backend(role).deliver_start(runtime.handle, message)
                await self._adopt_started_delivery(role, runtime, receipt.delivery_id)
            else:
                active_delivery_id = runtime.active_delivery_id
                try:
                    receipt = await self._backend(role).deliver_steer(
                        runtime.handle, active_delivery_id, message
                    )
                    if receipt.delivery_id != active_delivery_id:
                        raise RuntimeError("backend steering changed the active delivery identity")
                except InactiveTurn:
                    receipt = await self._backend(role).deliver_start(runtime.handle, message)
                    await self._adopt_started_delivery(role, runtime, receipt.delivery_id)
            await self.broker.mark_delivered(sequence)
            if notices:
                await self.broker.mark_system_notices_delivered(
                    role,
                    [self._notice_sequence(notice) for notice in notices],
                )

    async def deliver_pending_notices(self, role: str) -> None:
        """Steer retained notices only when the role's current turn accepts them."""
        runtime = self.roles.get(role)
        if runtime is None:
            raise ValueError(f"unknown orchestrated role: {role}")
        async with self._delivery_locks[role]:
            if runtime.failed or runtime.handle is None or runtime.active_delivery_id is None:
                return
            notices = await self.broker.pending_system_notices(role)
            if not notices:
                return
            accepted = await self._backend(role).deliver_notice(
                runtime.handle,
                runtime.active_delivery_id,
                self._system_notice_message(notices),
            )
            if accepted:
                await self.broker.mark_system_notices_delivered(
                    role,
                    [self._notice_sequence(notice) for notice in notices],
                )

    async def _recover_and_deliver(
        self,
        role: str,
        runtime: RoleRuntime,
        sequence: int,
        message: str,
    ) -> bool:
        """Use a surviving failed session, or replace a dead one exactly once."""
        error: Exception | None = None
        backend = self._backend(role)
        if runtime.handle is not None:
            try:
                receipt = await backend.deliver_start(runtime.handle, message)
            except Exception as delivery_error:
                error = delivery_error
                failed_handle, runtime.handle = runtime.handle, None
                try:
                    await backend.close_role(failed_handle)
                except Exception:
                    pass
            else:
                await self._accept_recovery(role, runtime, receipt.delivery_id)
                await self.broker.mark_delivered(sequence)
                return True

        replacement: RoleHandle | None = None
        try:
            replacement = await backend.open_role(role, self._role_context(role))
            runtime.handle = replacement
            receipt = await backend.deliver_start(replacement, message)
        except Exception as recovery_error:
            error = recovery_error
            if replacement is not None:
                runtime.handle = None
                try:
                    await backend.close_role(replacement)
                except Exception:
                    pass
        else:
            await self._accept_recovery(role, runtime, receipt.delivery_id)
            await self.broker.mark_delivered(sequence)
            return True

        reason = str(error or "unknown error")
        await self.broker.role_failed(role, reason)
        await self.broker.mark_delivery_failed(sequence, reason)
        return False

    async def _accept_recovery(
        self,
        role: str,
        runtime: RoleRuntime,
        delivery_id: str,
    ) -> None:
        runtime.failed = False
        await self._adopt_started_delivery(role, runtime, delivery_id)
        await self.broker.role_recovered(role)

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
        elif event.kind == "role_failed":
            role = event.role or ""
            runtime = self.roles.get(role)
            if runtime is None:
                raise RuntimeError(f"unknown role failed: {role or 'missing role'}")
            async with self._delivery_locks[role]:
                runtime.active_delivery_id = None
                runtime.failed = True
                self._started_deliveries = {
                    key for key in self._started_deliveries if key[0] != role
                }
                self._completed_deliveries = {
                    key for key in self._completed_deliveries if key[0] != role
                }
                await self.broker.role_failed(role, event.error or "unknown error")
        elif event.kind == "backend_failed":
            raise RuntimeError(f"agent backend failed: {event.error or 'unknown error'}")

    def _role_context(self, role: str) -> RoleContext:
        agent = self.profile.agent(role)
        return RoleContext(
            shop_root=str(self.shop_root),
            active_project=str(self.active_project),
            agent=agent,
            profile_id=self.profile.id,
            user_label=self.profile.user_label,
            user_agent_label=self.profile.user_agent.label,
        )

    def _backend(self, role: str) -> AgentBackend:
        return self.backends_by_agent[role]

    def _message(
        self,
        value: dict[str, Any],
        notices: Sequence[SystemNotice | dict[str, object]] = (),
    ) -> str:
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
            runtime = self.profile.agent(str(value["recipient"])).runtime
            if runtime is not None and runtime.backend in {"claude", "opencode"}:
                acknowledgement = (
                    f'floor_acknowledge(role="{value["recipient"]}", '
                    f'assignment="{assignment_id}")'
                )
            else:
                acknowledgement = (
                    f"python -m floor.agent acknowledge --role {value['recipient']} "
                    f"--assignment {assignment_id}"
                )
            lines.extend(
                (
                    "ASSIGNMENT LIFECYCLE GATE:",
                    "Before anything else, your FIRST TOOL CALL must be:",
                    acknowledgement,
                    "Do not read files or investigate, load a role card or skill, start a development process, "
                    "or make any other tool call until that command succeeds.",
                )
            )
        lines.extend(("instruction:", str(value["body"])))
        message = "\n".join(lines)
        if notices:
            return f"{self._system_notice_message(notices)}\n\n{message}"
        return message

    @staticmethod
    def _notice_value(notice: SystemNotice | dict[str, object]) -> dict[str, object]:
        return notice.delivery_value() if isinstance(notice, SystemNotice) else notice

    def _notice_sequence(self, notice: SystemNotice | dict[str, object]) -> int:
        return int(self._notice_value(notice)["sequence"])

    def _system_notice_message(
        self,
        notices: Sequence[SystemNotice | dict[str, object]],
    ) -> str:
        lines = [
            "Shop broker events:",
            "These are trusted informational events, not user direction or new assignments.",
        ]
        for notice in notices:
            value = self._notice_value(notice)
            lines.extend(
                (
                    "event:",
                    f"kind: {value['kind']}",
                    f"path: {value['path']}",
                    f"revision: {value['revision']}",
                )
            )
        return "\n".join(lines)

    async def close(self) -> None:
        errors: list[BaseException] = []
        for runtime in reversed(tuple(self.roles.values())):
            if runtime.handle is not None and runtime.active_delivery_id is not None:
                try:
                    await asyncio.wait_for(
                        self._backend(runtime.handle.role).interrupt(runtime.handle),
                        timeout=2,
                    )
                except BaseException as error:
                    errors.append(error)
        for runtime in reversed(tuple(self.roles.values())):
            if runtime.handle is None:
                continue
            try:
                await asyncio.wait_for(
                    self._backend(runtime.handle.role).close_role(runtime.handle),
                    timeout=2,
                )
            except BaseException as error:
                errors.append(error)
        self.roles.clear()

        async def close_backend(backend: AgentBackend) -> BaseException | None:
            try:
                # Concrete process owners escalate to termination and kill;
                # this outer bound also covers a wedged native close request.
                await asyncio.wait_for(backend.close(), timeout=16)
            except BaseException as error:
                return error
            return None

        backend_errors = await asyncio.gather(
            *(close_backend(backend) for backend in reversed(self.backends))
        )
        errors.extend(error for error in backend_errors if error is not None)
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


async def _route_backend_events(
    orchestrator: ShopOrchestrator,
    backend: AgentBackend,
) -> None:
    async for event in backend.events:
        await orchestrator.handle_event(event)


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
    shop_root = shop_resource_root()
    project_home = arguments.projects_dir
    solid_command = arguments.solid_command or default_solid_command()
    command_overrides = parse_backend_command_overrides(getattr(arguments, "backend_command", None))
    from .sessions import SessionRegistry
    registry = SessionRegistry(
        project_home,
        shop_root=shop_root,
        solid_command=solid_command,
        broker_url=f"http://127.0.0.1:{arguments.port}",
        backend_commands=command_overrides,
    )
    app = create_app(project_home, registry=registry)
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
    try:
        while not server.started and not server_task.done():
            await asyncio.sleep(0.01)
        if server_task.done():
            await server_task
            raise RuntimeError("shop-floor server stopped before opening")
        print(f"shop-floor open at http://127.0.0.1:{arguments.port}", flush=True)
        await server_task
    except asyncio.CancelledError:
        pass
    finally:
        if not server_task.done():
            server.should_exit = True
            await server_task


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the event-driven agent shop")
    parser.add_argument("--port", type=int, default=int(os.environ.get("FLOOR_PORT", "9000")))
    parser.add_argument(
        "--projects-dir",
        type=Path,
        required=True,
        help="exact directory containing project repositories",
    )
    parser.add_argument("--solid-command", help=argparse.SUPPRESS)
    parser.add_argument("--backend-command", action="append", default=[], metavar="BACKEND=COMMAND", help=argparse.SUPPRESS)
    try:
        asyncio.run(_serve(parser.parse_args()))
    except (PreparationError, ProfileError, ProjectRuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
