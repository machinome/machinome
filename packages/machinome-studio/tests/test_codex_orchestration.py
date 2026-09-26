# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from floor.backends.base import BackendEvent, ContextUnrecoverable, RoleHandle
from floor.orchestrator import ShopOrchestrator
from tests.test_orchestrator import FakeMultiplexBackend, FakeBroker, FORDESMAC, ROOT


class CodexOrchestrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.backend = FakeMultiplexBackend()
        self.broker = FakeBroker()
        self.orchestrator = ShopOrchestrator(self.backend, self.broker, profile=FORDESMAC,
            shop_root=ROOT, active_project=Path("/tmp/synthetic-project"))
        await self.orchestrator.open()

    async def asyncTearDown(self):
        await self.orchestrator.close()

    async def test_used_context_failure_never_opens_fresh_replacement(self):
        runtime = self.orchestrator.roles["designer"]
        original = runtime.handle
        self.backend.deliver_start = AsyncMock(side_effect=ContextUnrecoverable("Retained role context cannot be restored"))
        self.backend.open_role = AsyncMock()
        self.assertFalse(await self.orchestrator._recover_and_deliver("designer", runtime, 7, "continue"))
        self.backend.open_role.assert_not_awaited()
        self.assertEqual(runtime.handle, original)
        self.assertEqual(self.broker.failed_deliveries, [(7, "Retained role context cannot be restored")])

    async def test_old_handle_failure_already_waiting_lock_cannot_poison_replacement(self):
        runtime = self.orchestrator.roles["designer"]
        old = runtime.handle
        lock = self.orchestrator._delivery_locks["designer"]
        import asyncio
        await lock.acquire()
        task = asyncio.create_task(self.orchestrator.handle_event(BackendEvent(kind="role_failed", role="designer",
            handle_id=old.backend_id, error="old failure")))
        await asyncio.sleep(0)
        runtime.handle = RoleHandle("replacement", "designer")
        lock.release()
        await task
        self.assertFalse(runtime.failed)
        self.assertNotIn("designer", self.broker.failures)

    async def test_same_handle_queued_failure_cannot_poison_new_delivery(self):
        import asyncio
        runtime = self.orchestrator.roles["designer"]
        await self.orchestrator._adopt_started_delivery("designer", runtime, "old-delivery")
        lock = self.orchestrator._delivery_locks["designer"]
        await lock.acquire()
        task = asyncio.create_task(self.orchestrator.handle_event(BackendEvent(kind="role_failed", role="designer",
            handle_id=runtime.handle.backend_id, delivery_id="old-delivery", error="old failure")))
        await asyncio.sleep(0)
        await self.orchestrator._adopt_started_delivery("designer", runtime, "new-delivery")
        lock.release()
        await task
        self.assertFalse(runtime.failed)
        self.assertEqual(runtime.active_delivery_id, "new-delivery")

    async def test_pristine_failure_liveness_is_rechecked_after_delivery_lock(self):
        import asyncio
        runtime = self.orchestrator.roles["designer"]
        owner = {"epoch": "old"}
        event = BackendEvent(kind="role_failed", role="designer", handle_id=runtime.handle.backend_id,
            error="old pristine failure", is_current=lambda: owner["epoch"] == "old")
        lock = self.orchestrator._delivery_locks["designer"]
        await lock.acquire()
        task = asyncio.create_task(self.orchestrator.handle_event(event))
        await asyncio.sleep(0)
        owner["epoch"] = "recovered"
        lock.release()
        await task
        self.assertIsNone(runtime.latest_delivery_id)
        self.assertFalse(runtime.failed)
