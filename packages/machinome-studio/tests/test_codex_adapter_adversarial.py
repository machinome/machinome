# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Coordinator-owned attacks against the model-to-floor dispatch boundary."""
from __future__ import annotations

import asyncio
from pathlib import Path
import unittest
from unittest.mock import AsyncMock

from floor.backends.base import BackendEvent, ContextUnrecoverable, InactiveTurn, session_tool_names
from floor.backends.codex_wire import CodexProtocolError
from floor.orchestrator import ShopOrchestrator
from tests import test_codex_backend as fixtures
from tests import test_orchestrator as orchestration


class CodexAdapterAdversarialTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await fixtures.CodexBackendTests.asyncSetUp(self)
        self.worker.names = session_tool_names(self.context.agent.skills, self.context.agent.runtime.tools)
        await self.backend.deliver_start(self.handle, "synthetic direction")
        self.state = self.backend.roles[self.handle.backend_id]

    async def asyncTearDown(self):
        await fixtures.CodexBackendTests.asyncTearDown(self)

    def call(self, *, rpc_id=70, call_id="model-call", tool="floor_read_file", arguments=None, **changes):
        params = {"threadId": self.state.thread.thread_id, "turnId": self.state.native_turn,
                  "callId": call_id, "namespace": "functions", "tool": tool,
                  "arguments": {"path": "README.md"} if arguments is None else arguments}
        params.update(changes)
        return {"id": rpc_id, "method": "item/tool/call", "params": params,
                "studioGeneration": self.state.thread.generation}

    async def test_actual_functions_namespace_reaches_exact_declared_tool(self):
        await self.backend._callback(self.state, self.call())
        self.worker.rpc.assert_awaited_once_with("tools/call", {"name": "read_file", "arguments": {"path": "README.md"}})
        self.assertTrue(self.native.responses[-1]["result"]["success"])

    async def test_spoofed_lifecycle_sender_never_reaches_worker(self):
        await self.backend._callback(self.state, self.call(namespace=None, tool="floor_report", arguments={
            "sender": "foreman", "recipient": "builder", "text": "impersonation"}))
        self.worker.rpc.assert_not_awaited()
        self.assertFalse(self.native.responses[-1]["result"]["success"])

    async def test_duplicate_call_id_with_new_rpc_id_is_not_second_mutation(self):
        first = self.call(namespace=None, tool="floor_write_file", arguments={"path": "file", "content": "one"})
        await asyncio.gather(self.backend._callback(self.state, first),
                             self.backend._callback(self.state, {**first, "id": 71}))
        self.assertEqual(self.worker.rpc.await_count, 1)
        self.assertEqual(len(self.native.responses), 2)
        self.assertEqual(self.native.responses[0]["result"], self.native.responses[1]["result"])
        changed = self.call(rpc_id=72, namespace=None, tool="floor_write_file", arguments={"path": "file", "content": "two"})
        await self.backend._callback(self.state, changed)
        self.assertEqual(self.worker.rpc.await_count, 1)
        self.assertFalse(self.native.responses[-1]["result"]["success"])

    async def test_cross_owner_turn_generation_and_bad_schema_never_dispatch(self):
        frames = [self.call(threadId="other-project-thread"), self.call(turnId="old-turn"),
                  self.call(arguments={"path": 12}), self.call(namespace="collaboration"),
                  self.call(tool="exec_command"), self.call()]
        frames[-1]["studioGeneration"] -= 1
        for frame in frames:
            await self.backend._callback(self.state, frame)
        self.worker.rpc.assert_not_awaited()

    async def test_duplicate_completed_message_is_only_published_once(self):
        frame = {"method": "item/completed", "params": {"threadId": self.state.thread.thread_id,
                 "turnId": self.state.native_turn, "item": {"id": "message-one", "type": "agentMessage", "text": "done"}},
                 "studioGeneration": self.state.thread.generation}
        await self.state.thread.events.put(frame)
        await self.state.thread.events.put(frame)
        await asyncio.sleep(0.02)
        messages = []
        while not self.backend.events_queue.empty():
            event = self.backend.events_queue.get_nowait()
            if event.kind == "role_message":
                messages.append(event.text)
        self.assertEqual(messages, ["done"])

    async def test_native_execution_notification_fails_closed(self):
        frame = {"method": "item/started", "params": {"threadId": self.state.thread.thread_id,
                 "turnId": self.state.native_turn, "item": {"id": "native-command", "type": "commandExecution", "command": "forbidden"}},
                 "studioGeneration": self.state.thread.generation}
        await self.state.thread.events.put(frame)
        await asyncio.sleep(0.03)
        self.worker.close.assert_awaited()
        failures = []
        while not self.backend.events_queue.empty():
            event = self.backend.events_queue.get_nowait()
            if event.kind == "role_failed":
                failures.append(event)
        self.assertTrue(failures, "unexpected native execution must not be ignored")

    async def test_confirmed_steer_completion_can_immediately_start_next_delivery(self):
        old = self.state.active
        original = self.native.rpc

        async def completed_race(method, params):
            if method == "turn/steer":
                raise CodexProtocolError("synthetic rejection")
            if method == "thread/read":
                return {"thread": {"id": self.state.thread.thread_id,
                        "turns": [{"id": self.state.native_turn, "status": "completed"}]}}
            return await original(method, params)

        self.native.rpc = completed_race
        with self.assertRaises(InactiveTurn):
            await self.backend.deliver_steer(self.handle, old, "completion-race direction")
        # Do not give the event reader an unrelated notification to rescue the
        # race. The state evidence already established that the old turn ended.
        receipt = await self.backend.deliver_start(self.handle, "completion-race direction")
        self.assertTrue(receipt.accepted)
        self.assertNotEqual(receipt.delivery_id, old)

    async def test_closing_blocked_tool_emits_terminal_activity(self):
        entered = asyncio.Event()
        blocked = asyncio.Event()

        async def operation(*_):
            entered.set()
            await blocked.wait()

        self.worker.rpc.side_effect = operation
        await self.state.thread.events.put(self.call())
        await asyncio.wait_for(entered.wait(), 1)
        await asyncio.wait_for(self.backend.close_role(self.handle), 1)
        activities = []
        while not self.backend.events_queue.empty():
            event = self.backend.events_queue.get_nowait()
            if event.kind == "activity" and event.activity.name == "read_file":
                activities.append(event.activity)
        self.assertEqual([activity.state for activity in activities], ["running", "failed"])
        self.assertEqual(activities[0].id, activities[1].id)
        self.assertFalse(self.state.callbacks)

    async def test_interrupted_native_turn_stops_its_blocked_floor_operation(self):
        entered, blocked = asyncio.Event(), asyncio.Event()

        async def operation(*_):
            entered.set()
            await blocked.wait()

        self.worker.rpc.side_effect = operation
        await self.state.thread.events.put(self.call())
        await asyncio.wait_for(entered.wait(), 1)
        await self.state.thread.events.put({"method": "turn/completed", "studioGeneration": self.state.thread.generation,
            "params": {"threadId": self.state.thread.thread_id, "turn": {"id": self.state.native_turn, "status": "interrupted"}}})
        await asyncio.sleep(0.03)
        self.worker.close.assert_awaited()
        self.assertTrue(all(task.done() for _, task in self.state.calls.values()))


class CodexRoutingAdversarialTests(unittest.IsolatedAsyncioTestCase):
    async def test_old_failure_waiting_lock_cannot_poison_new_delivery_on_same_handle(self):
        backend, broker = orchestration.FakeMultiplexBackend(), orchestration.FakeBroker()
        shop = ShopOrchestrator(backend, broker, profile=orchestration.FORDESMAC,
                                shop_root=orchestration.ROOT, active_project=Path("/tmp/synthetic-project"))
        await shop.open()
        try:
            runtime = shop.roles["designer"]
            await shop._adopt_started_delivery("designer", runtime, "old-delivery")
            lock = shop._delivery_locks["designer"]
            await lock.acquire()
            pending = asyncio.create_task(shop.handle_event(BackendEvent(kind="role_failed", role="designer",
                handle_id=runtime.handle.backend_id, delivery_id="old-delivery", error="old generation failed")))
            await asyncio.sleep(0)
            await shop._adopt_started_delivery("designer", runtime, "recovered-delivery")
            lock.release()
            await pending
            self.assertFalse(runtime.failed)
            self.assertEqual(runtime.active_delivery_id, "recovered-delivery")
            self.assertNotIn("designer", broker.failures)
        finally:
            await shop.close()

    async def test_initial_context_failure_does_not_end_mixed_project_delivery(self):
        failing, sibling = orchestration.FakeMultiplexBackend(), orchestration.FakeMultiplexBackend()
        broker = orchestration.FakeBroker()
        backends = {agent.id: failing if agent.id == "designer" else sibling for agent in orchestration.FORDESMAC.agents}
        shop = ShopOrchestrator(backends, broker, profile=orchestration.FORDESMAC,
                                shop_root=orchestration.ROOT, active_project=Path("/tmp/synthetic-project"))
        await shop.open()
        failing.deliver_start = AsyncMock(side_effect=ContextUnrecoverable("retained context unavailable"))
        try:
            await shop.deliver({"sequence": 1, "recipient": "designer", "sender": "foreman", "kind": "direction", "body": "first"})
            await shop.deliver({"sequence": 2, "recipient": "machinist", "sender": "foreman", "kind": "direction", "body": "sibling"})
            self.assertTrue(shop.roles["designer"].failed)
            self.assertEqual(broker.failed_deliveries, [(1, "retained context unavailable")])
            self.assertIn(2, broker.delivered)
            self.assertFalse(shop.roles["machinist"].failed)
        finally:
            await shop.close()
