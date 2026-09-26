# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import replace
from pathlib import Path
from unittest.mock import AsyncMock, patch
import unittest

from floor.backends.codex import CodexBackend
from floor.backends.base import ContextUnrecoverable, InactiveTurn, RoleContext, session_tool_names
from floor.profiles import BackendRuntime, load_profile, resolve_profile_runtime
from tests import test_codex_service as service_fixtures
from tests.test_orchestrator import ROOT


class CodexBackendTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await service_fixtures.CodexServiceTests.asyncSetUp(self)
        self.reference = await self.service.acquire("synthetic", [])
        agent = resolve_profile_runtime(load_profile("builder", shop_root=ROOT)).user_agent
        agent = replace(agent, runtime=BackendRuntime("gpt-6-sol", "medium", agent.runtime.tools, backend="codex"))
        self.context = RoleContext(str(ROOT), self.temporary.name, agent, "builder", "Maker", "Builder")
        self.worker_patch = patch("floor.backends.codex.FloorWorker")
        self.worker = self.worker_patch.start().return_value
        self.worker.start = AsyncMock()
        self.worker.close = AsyncMock()
        self.worker.rpc = AsyncMock(return_value={"content": [{"type": "text", "text": "done"}]})
        self.worker.names = session_tool_names(agent.skills, agent.runtime.tools)
        self.worker.context = self.context
        self.addCleanup(self.worker_patch.stop)
        self.backend = CodexBackend(shop_root=ROOT, project=Path(self.temporary.name), model=None, broker_url="http://unused",
            machinome_command="machinome", session_id="synthetic", codex_service=self.service, codex_reference=self.reference)
        original = self.native.rpc
        self.calls = []
        async def rpc(method, params):
            self.calls.append((method, params))
            if method == "turn/start":
                return {"turn": {"id": "native-turn"}}
            return await original(method, params)
        self.native.rpc = rpc
        self.handle = await self.backend.open_role("builder", self.context)

    async def asyncTearDown(self):
        await self.backend.close()
        await service_fixtures.CodexServiceTests.asyncTearDown(self)

    async def test_delivery_native_no_env_and_opaque_handle_receipt(self):
        receipt = await self.backend.deliver_start(self.handle, "hello")
        self.assertNotEqual(self.handle.backend_id, "thread-1")
        self.assertNotEqual(receipt.delivery_id, "native-turn")
        parameters = next(params for method, params in self.calls if method == "turn/start")
        self.assertEqual(parameters["environments"], [])
        self.assertEqual(parameters["sandboxPolicy"], {"type": "readOnly"})
        self.assertEqual(parameters["approvalPolicy"], "never")
        self.assertTrue(next(iter(self.reference.threads)).used)

    async def test_notice_completion_race_never_starts_turn(self):
        self.assertFalse(await self.backend.deliver_notice(self.handle, "missing", "notice"))
        with self.assertRaises(InactiveTurn):
            await self.backend.deliver_steer(self.handle, "missing", "steer")
        self.assertFalse(any(method == "turn/start" for method, _ in self.calls))

    async def test_used_ambiguous_send_is_context_unrecoverable(self):
        original = self.native.rpc
        async def failing(method, params):
            if method == "turn/start":
                raise RuntimeError("ambiguous send")
            return await original(method, params)
        self.native.rpc = failing
        with self.assertRaises(ContextUnrecoverable):
            await self.backend.deliver_start(self.handle, "hello")
        self.assertTrue(next(iter(self.reference.threads)).used)

    async def test_tool_running_terminal_path_and_native_tokens_are_portable(self):
        import asyncio
        await self.backend.deliver_start(self.handle, "hello")
        state = self.backend.roles[self.handle.backend_id]
        await self.backend._callback(state, {"id": 20, "studioGeneration": state.thread.generation,
            "params": {"threadId": state.thread.thread_id, "turnId": state.native_turn, "callId": "read",
                       "tool": "floor_read_file", "arguments": {"path": "README.md"}, "namespace": "functions"}})
        await state.thread.events.put({"method": "thread/tokenUsage/updated", "studioGeneration": state.thread.generation,
            "params": {"threadId": state.thread.thread_id, "turnId": state.native_turn,
                       "tokenUsage": {"total": {"inputTokens": 12, "outputTokens": 4}}}})
        await asyncio.sleep(0.01)
        activity = []
        while not self.backend.events_queue.empty():
            event = self.backend.events_queue.get_nowait()
            if event.activity is not None:
                activity.append(event.activity)
        self.assertEqual([(item.state, item.path) for item in activity[:2]], [("running", "README.md"), ("completed", "README.md")])
        self.assertEqual(activity[0].id, activity[1].id)
        self.assertEqual((activity[-1].input_tokens, activity[-1].output_tokens), (12, 4))

    async def test_idle_runtime_change_retains_exact_handle_and_thread(self):
        state = self.backend.roles[self.handle.backend_id]
        native = state.thread.thread_id
        await self.backend.update_runtime(self.handle, replace(state.runtime, model="gpt-6-astra", effort="high"))
        await self.backend.deliver_start(self.handle, "next")
        params = next(params for method, params in self.calls if method == "turn/start")
        self.assertEqual(params["model"], "gpt-6-astra")
        self.assertEqual(params["effort"], "high")
        self.assertEqual(params["threadId"], native)

    async def test_used_catalogue_preserves_unavailable_reason_without_requalification(self):
        await self.backend.deliver_start(self.handle, "used")
        self.service.invalidated = True
        before = self.service.qualifier.qualify.await_count
        catalogue = await self.backend.runtime_catalog(self.handle)
        self.assertFalse(catalogue.supported)
        self.assertIn("codex", catalogue.unavailable)
        self.assertIn("close", catalogue.reason)
        self.assertEqual(before, self.service.qualifier.qualify.await_count)

    async def test_nondefault_codex_command_is_explicitly_refused(self):
        with self.assertRaisesRegex(ValueError, "overrides are unsupported"):
            CodexBackend(shop_root=ROOT, command="alternate-codex", codex_service=self.service,
                         codex_reference=self.reference)

    async def test_already_yielded_pristine_failure_is_stale_after_shared_recovery(self):
        state = self.backend.roles[self.handle.backend_id]
        self.backend._emit(state, "role_failed", error="Synthetic old generation")
        event = await anext(self.backend.events)
        self.assertIsNone(event.delivery_id)
        self.assertTrue(event.is_current())
        replacement = service_fixtures.NativeFixture()
        replacement.next_id = 100
        self.service._launch.return_value = replacement
        self.native.dead.set()
        await self.service.recover()
        self.assertFalse(event.is_current())

    async def test_malformed_notification_quiesces_running_callback_before_failure(self):
        import asyncio
        await self.backend.deliver_start(self.handle, "hello")
        state = self.backend.roles[self.handle.backend_id]
        entered, cancelled = asyncio.Event(), asyncio.Event()
        async def blocked(*args):
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
        self.worker.rpc.side_effect = blocked
        await state.thread.events.put({"method": "item/tool/call", "id": 31,
            "studioGeneration": state.thread.generation, "params": {
                "threadId": state.thread.thread_id, "turnId": state.native_turn,
                "callId": "blocked", "namespace": "functions", "tool": "floor_read_file",
                "arguments": {"path": "README.md"}}})
        await asyncio.wait_for(entered.wait(), 1)
        await state.thread.events.put({"method": "thread/tokenUsage/updated",
            "studioGeneration": state.thread.generation, "params": {
                "turnId": state.native_turn, "tokenUsage": None}})
        async def failure():
            while True:
                event = await self.backend.events_queue.get()
                if event.kind == "role_failed":
                    return event
        await asyncio.wait_for(failure(), 1)
        self.worker.close.assert_awaited_once()
        self.assertTrue(cancelled.is_set())
        self.assertTrue(all(task.done() for _, task in state.calls.values()))
        self.assertFalse(state.callbacks)
