"""In-memory AgentBackend double for orchestrator acceptance tests."""

from __future__ import annotations

from collections.abc import AsyncIterator

from floor.backends.base import (
    AgentBackend,
    BackendEvent,
    DeliveryReceipt,
    RoleContext,
    RoleHandle,
    RuntimeCatalogue,
    RuntimeChoice,
)
from floor.profiles import BackendRuntime


class FakeBackend:
    """In-memory AgentBackend that records calls and emits configurable events.

    Each ``open_role`` returns a ``RoleHandle`` with a predictable backend_id.
    Delivery calls are recorded and events are pushed into ``self._event_queue``
    for ``self.events`` to yield.
    """

    events: AsyncIterator[BackendEvent]

    def __init__(self) -> None:
        self.started = False
        self.opened_roles: list[tuple[str, RoleContext]] = []
        self.deliveries: list[tuple[RoleHandle, str]] = []
        self.interrupted: list[RoleHandle] = []
        self.closed_roles: list[RoleHandle] = []
        self.closed = False
        self.runtime_updates: list[tuple[RoleHandle, BackendRuntime]] = []
        self._event_queue: list[BackendEvent] = []
        self._next_role = 0
        self.events = self._event_iterator()

    async def start(self) -> None:
        self.started = True

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        self.opened_roles.append((role, context))
        self._next_role += 1
        return RoleHandle(backend_id=f"fake-{role}-{self._next_role}", role=role)

    async def deliver_start(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
        self.deliveries.append((handle, message))
        return DeliveryReceipt(delivery_id=f"delivery-{len(self.deliveries)}", accepted=True)

    async def deliver_steer(
        self, handle: RoleHandle, expected_delivery_id: str, message: str
    ) -> DeliveryReceipt:
        self.deliveries.append((handle, message))
        return DeliveryReceipt(delivery_id=expected_delivery_id, accepted=True)

    async def deliver_notice(
        self, handle: RoleHandle, expected_delivery_id: str, message: str
    ) -> bool:
        self.deliveries.append((handle, message))
        return True

    async def interrupt(self, handle: RoleHandle) -> None:
        self.interrupted.append(handle)

    async def close_role(self, handle: RoleHandle) -> None:
        self.closed_roles.append(handle)

    async def runtime_catalog(self, handle: RoleHandle | None) -> RuntimeCatalogue:
        return RuntimeCatalogue(
            True,
            (
                RuntimeChoice("sonnet", ("medium", "high"), "claude"),
                RuntimeChoice("opus", ("medium", "high"), "claude"),
            ),
        )

    async def update_runtime(self, handle: RoleHandle, runtime: BackendRuntime) -> None:
        self.runtime_updates.append((handle, runtime))

    async def close(self) -> None:
        self.closed = True

    def emit(self, event: BackendEvent) -> None:
        """Push a portable event for the orchestrator to consume."""
        self._event_queue.append(event)

    async def _event_iterator(self) -> AsyncIterator[BackendEvent]:
        while True:
            while self._event_queue:
                yield self._event_queue.pop(0)
            # In a real test, orchestrator consumes events in a task.
            # Break out so tests don't hang.
            await __import__("asyncio").sleep(0)
