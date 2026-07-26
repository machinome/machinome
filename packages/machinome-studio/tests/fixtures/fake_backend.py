"""In-memory AgentBackend double for orchestrator acceptance tests."""

from __future__ import annotations

from collections.abc import AsyncIterator

from floor.backends.base import (
    AgentBackend,
    BackendEvent,
    DeliveryReceipt,
    RoleContext,
    RoleHandle,
)


class FakeBackend:
    """In-memory AgentBackend that records calls and emits configurable events.

    Each ``open_role`` returns a ``RoleHandle`` with a predictable backend_id.
    ``deliver`` records the call and returns an accepted receipt.  Events are
    pushed into ``self._event_queue`` and yielded by ``self.events``.
    """

    events: AsyncIterator[BackendEvent]

    def __init__(self) -> None:
        self.started = False
        self.opened_roles: list[tuple[str, RoleContext]] = []
        self.deliveries: list[tuple[RoleHandle, str]] = []
        self.interrupted: list[RoleHandle] = []
        self.closed_roles: list[RoleHandle] = []
        self.closed = False
        self._event_queue: list[BackendEvent] = []
        self._next_role = 0
        self.events = self._event_iterator()

    async def start(self) -> None:
        self.started = True

    async def open_role(self, role: str, context: RoleContext) -> RoleHandle:
        self.opened_roles.append((role, context))
        self._next_role += 1
        return RoleHandle(backend_id=f"fake-{role}-{self._next_role}", role=role)

    async def deliver(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
        return await self.deliver_start(handle, message)

    async def deliver_start(self, handle: RoleHandle, message: str) -> DeliveryReceipt:
        self.deliveries.append((handle, message))
        return DeliveryReceipt(delivery_id=f"delivery-{len(self.deliveries)}", accepted=True)

    async def deliver_steer(
        self, handle: RoleHandle, expected_delivery_id: str, message: str
    ) -> DeliveryReceipt:
        self.deliveries.append((handle, message))
        return DeliveryReceipt(delivery_id=expected_delivery_id, accepted=True)

    async def interrupt(self, handle: RoleHandle) -> None:
        self.interrupted.append(handle)

    async def close_role(self, handle: RoleHandle) -> None:
        self.closed_roles.append(handle)

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
