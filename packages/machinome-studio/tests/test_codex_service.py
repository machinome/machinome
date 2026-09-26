# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
import asyncio
import tempfile
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

from floor.backends.codex_service import CodexService
from floor.codex_auth import AuthLease, CodexAuthError


class NativeFixture:
    def __init__(self):
        self.notifications = asyncio.Queue()
        self.dead = asyncio.Event()
        self.closed = 0
        self.deleted = []
        self.responses = []
        self.next_id = 0

    async def rpc(self, method, params):
        if method == "config/read":
            return {"config": {}, "layers": [], "origins": {}}
        if method == "project/create":
            return {"project": {"id": "studio-owned-group", "name": params["name"], "roots": [], "metadata": params["metadata"]}}
        if method == "thread/list":
            return {"data": [], "nextCursor": None}
        if method == "thread/start":
            self.next_id += 1
            return {"thread": {"id": f"thread-{self.next_id}"}}
        if method == "thread/resume":
            return {"thread": {"id": params["threadId"]}}
        if method == "thread/delete":
            self.deleted.append(params["threadId"])
        return {}

    async def close(self):
        self.closed += 1
        self.dead.set()

    async def send(self, frame):
        self.responses.append(frame)


class CodexServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name) / "codex"
        self.native = NativeFixture()
        self.service = CodexService(home=self.home)
        self.patches = [
            patch.object(self.service, "_launch", AsyncMock(return_value=self.native)),
            patch.object(self.service.qualifier, "qualify", AsyncMock(return_value={})),
            patch("floor.backends.codex_service.validate_home"),
            patch("floor.backends.codex_service.check_policy", AsyncMock()),
        ]
        for item in self.patches:
            item.start()

    async def asyncTearDown(self):
        await self.service.close()
        for item in self.patches:
            item.stop()
        self.temporary.cleanup()

    async def test_two_projects_share_owner_and_last_close_releases_lease(self):
        a = await self.service.acquire("session-a", [])
        b = await self.service.acquire("session-b", [])
        self.assertEqual(self.service._launch.await_count, 1)
        await a.close()
        self.assertEqual(self.native.closed, 0)
        with self.assertRaises(CodexAuthError):
            AuthLease(self.home).acquire()
        await b.close()
        self.assertEqual(self.native.closed, 1)
        lease = AuthLease(self.home)
        lease.acquire()
        lease.release()

    async def test_second_borrower_cannot_replace_active_qualified_contract(self):
        self.service.qualifier.qualify.return_value = {"contract": "first"}
        first = await self.service.acquire("session-a", [])
        self.service.qualifier.qualify.return_value = {"contract": "changed"}
        with self.assertRaisesRegex(RuntimeError, "changed while"):
            await self.service.acquire("session-b", [])
        self.assertEqual(self.service._qualified["contract"], "first")
        self.assertEqual(self.service._launch.await_count, 1)
        self.assertEqual(self.service.references, {first})

    async def test_shared_recovery_waits_for_every_sibling_quiescence(self):
        a = await self.service.acquire("session-a", [])
        b = await self.service.acquire("session-b", [])
        first = await a.open_thread("builder", {}, [])
        sibling = await b.open_thread("builder", {}, [])
        stopping = asyncio.Event()
        release = asyncio.Event()
        async def delayed_stop():
            stopping.set()
            await release.wait()
        first.quiesce = AsyncMock()
        sibling.quiesce = delayed_stop
        self.native.dead.set()
        replacement = NativeFixture()
        replacement.next_id = 100
        self.service._launch.return_value = replacement
        recovering = asyncio.create_task(self.service.recover())
        await stopping.wait()
        self.assertFalse(recovering.done())
        self.assertEqual(self.service._launch.await_count, 1)
        release.set()
        await recovering
        first.quiesce.assert_awaited_once()
        self.assertEqual(self.service._launch.await_count, 2)

    async def test_recovery_discards_and_tags_previous_generation_events(self):
        reference = await self.service.acquire("session-a", [])
        handle = await reference.open_thread("builder", {}, [])
        await self.native.notifications.put({"method": "item/completed", "params": {"threadId": handle.thread_id}})
        await asyncio.sleep(0.01)
        old = handle.generation
        self.assertEqual(handle.events.qsize(), 1)
        self.native.dead.set()
        await asyncio.sleep(0.01)
        replacement = NativeFixture()
        replacement.next_id = 100
        self.service._launch.return_value = replacement
        await self.service.recover()
        self.assertTrue(handle.events.empty())
        await replacement.notifications.put({"method": "item/completed", "params": {"threadId": handle.thread_id}})
        event = await asyncio.wait_for(handle.events.get(), 1)
        self.assertGreater(event["studioGeneration"], old)
        self.assertEqual(event["studioGeneration"], handle.generation)

    async def test_same_role_handles_route_exactly_and_close_only_owned_thread(self):
        a = await self.service.acquire("session-a", [])
        b = await self.service.acquire("session-b", [])
        first = await a.open_thread("builder", {}, [])
        replacement = await a.open_thread("builder", {}, [])
        other = await b.open_thread("builder", {}, [])
        await self.native.notifications.put({"method": "item/completed", "params": {"threadId": first.thread_id}})
        self.assertEqual((await asyncio.wait_for(first.events.get(), 1))["params"]["threadId"], first.thread_id)
        self.assertTrue(replacement.events.empty())
        self.assertTrue(other.events.empty())
        await first.close()
        self.assertEqual(self.native.deleted, [first.thread_id])
        await self.native.notifications.put({"id": 77, "method": "item/tool/call", "params": {"threadId": first.thread_id}})
        await asyncio.sleep(0.01)
        self.assertFalse(self.native.responses[-1]["result"]["success"])
        self.assertTrue(replacement.events.empty())

    async def test_shared_crash_fans_out_only_exact_attached_handles(self):
        a = await self.service.acquire("session-a", [])
        b = await self.service.acquire("session-b", [])
        first = await a.open_thread("builder", {}, [])
        second = await b.open_thread("builder", {}, [])
        self.native.dead.set()
        for handle in (first, second):
            frame = await asyncio.wait_for(handle.events.get(), 1)
            self.assertEqual(frame["method"], "studio/transportFailed")
            self.assertEqual(frame["params"]["threadId"], handle.thread_id)

    async def test_cancelled_close_keeps_owner_until_native_cleanup_finishes(self):
        a = await self.service.acquire("session-a", [])
        entered = asyncio.Event()
        complete = asyncio.Event()
        async def blocked_close():
            entered.set()
            await complete.wait()
            self.native.closed += 1
            self.native.dead.set()
        self.native.close = blocked_close
        task = asyncio.create_task(a.close())
        await entered.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        with self.assertRaises(CodexAuthError):
            AuthLease(self.home).acquire()
        complete.set()
        await a.close()
        self.assertEqual(self.native.closed, 1)

    async def test_cancelled_pending_acquire_releases_before_session_exists(self):
        entered = asyncio.Event()
        finish = asyncio.Event()
        async def qualify(_):
            entered.set()
            await finish.wait()
        self.service.qualifier.qualify.side_effect = qualify
        task = asyncio.create_task(self.service.acquire("pending", []))
        await entered.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(self.native.closed, 0)
        lease = AuthLease(self.home)
        lease.acquire()
        lease.release()

    async def test_recovery_resumes_used_and_recreates_pristine_sibling(self):
        a = await self.service.acquire("session-a", [])
        b = await self.service.acquire("session-b", [])
        used = await a.open_thread("builder", {}, [])
        pristine = await b.open_thread("builder", {}, [])
        record = self.home / "sessions" / "used.jsonl"
        record.parent.mkdir()
        record.write_text('{"type":"session_meta","payload":{"id":"thread-1","dynamic_tools":[]}}\n')
        used.path = str(record)
        used.used = True
        next_native = NativeFixture()
        next_native.next_id = 100
        self.service._launch.return_value = next_native
        self.native.dead.set()
        await used.events.get()
        await pristine.events.get()
        old = pristine.thread_id
        await self.service.recover()
        self.assertEqual(used.thread_id, "thread-1")
        self.assertNotEqual(pristine.thread_id, old)
        self.assertEqual(used.generation, pristine.generation)
        self.assertNotIn(old, self.service.threads)
        await next_native.notifications.put({"method":"item/completed","params":{"threadId":used.thread_id}})
        self.assertEqual((await asyncio.wait_for(used.events.get(), 1))["params"]["threadId"], used.thread_id)
        await a.close()
        self.assertEqual(next_native.closed, 0)
        await b.close()
        self.assertEqual(next_native.closed, 1)

    async def test_cleanup_covers_marked_paginated_archived_orphans_only(self):
        original = self.native.rpc
        async def inventory(method, params):
            if method == "thread/list":
                identity = "archived" if params["archived"] else "second" if params["cursor"] else "first"
                return {"data":[{"id":identity,"projectId":"studio-owned-group"}],
                        "nextCursor":"page2" if identity == "first" else None}
            return await original(method, params)
        self.native.rpc = inventory
        reference = await self.service.acquire("session-a", [])
        self.assertEqual(set(self.native.deleted), {"first", "second", "archived"})
        await reference.close()

    async def test_cleanup_refuses_unmarked_inventory(self):
        original = self.native.rpc
        async def inventory(method, params):
            if method == "thread/list":
                return {"data":[{"id":"unrelated","projectId":"different-native-group"}],"nextCursor":None}
            return await original(method, params)
        self.native.rpc = inventory
        with self.assertRaisesRegex(RuntimeError, "owner group"):
            await self.service.acquire("session-a", [])
        self.assertEqual(self.native.deleted, [])
        self.assertEqual(self.native.closed, 1)
