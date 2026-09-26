# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Coordinator-owned adversarial regressions for Codex resource ownership."""
from __future__ import annotations

import asyncio
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from floor.backends.codex_service import CodexService
from floor.codex_auth import AuthLease, CodexAuthError
from tests.test_codex_service import NativeFixture


class CodexAdversarialOwnershipTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name) / "codex"
        self.native = NativeFixture()
        self.service = CodexService(home=self.home)
        for item in (
            patch.object(self.service, "_launch", AsyncMock(return_value=self.native)),
            patch.object(self.service.qualifier, "qualify", AsyncMock(return_value={})),
            patch("floor.backends.codex_service.validate_home"),
            patch("floor.backends.codex_service.check_policy", AsyncMock()),
        ):
            item.start()
            self.addCleanup(item.stop)

    async def asyncTearDown(self):
        try:
            await self.service.close()
        except Exception:
            # A failing assertion must not leave the review fixture's lease
            # behind. Production close behavior is asserted in the test.
            await self.native.close()
            self.service.lease.release()
        self.temporary.cleanup()

    async def test_failed_native_delete_does_not_pin_project_or_sibling(self):
        first = await self.service.acquire("first", [])
        sibling = await self.service.acquire("sibling", [])
        own = await first.open_thread("builder", {}, [])
        other = await sibling.open_thread("builder", {}, [])
        original = self.native.rpc

        async def fail_delete(method, params):
            if method == "thread/delete" and params["threadId"] == own.thread_id:
                raise RuntimeError("synthetic native delete failure")
            return await original(method, params)

        self.native.rpc = fail_delete
        try:
            await asyncio.wait_for(first.close(), 1)
        except RuntimeError:
            pass  # Reporting a cleanup failure is allowed; leaking is not.
        self.assertNotIn(first, self.service.references)
        self.assertIn(sibling, self.service.references)
        self.assertNotIn(own.thread_id, self.service.threads)
        self.assertEqual(self.native.closed, 0)
        await self.native.notifications.put({
            "method": "item/completed", "params": {"threadId": other.thread_id},
        })
        frame = await asyncio.wait_for(other.events.get(), 1)
        self.assertEqual(frame["params"]["threadId"], other.thread_id)
        await sibling.close()
        self.assertEqual(self.native.closed, 1)
        lease = AuthLease(self.home)
        lease.acquire()
        lease.release()

    async def test_malformed_notification_fails_handles_instead_of_losing_router(self):
        reference = await self.service.acquire("project", [])
        handle = await reference.open_thread("builder", {}, [])
        await self.native.notifications.put({"method": "item/completed", "params": []})
        frame = await asyncio.wait_for(handle.events.get(), 1)
        self.assertEqual(frame["method"], "studio/transportFailed")
        self.assertEqual(frame["params"]["threadId"], handle.thread_id)

    async def test_hub_close_releases_all_projects_even_when_every_delete_fails(self):
        for name in ("first", "sibling"):
            reference = await self.service.acquire(name, [])
            await reference.open_thread("builder", {}, [])
        original = self.native.rpc

        async def fail_delete(method, params):
            if method == "thread/delete":
                raise RuntimeError("synthetic native delete failure")
            return await original(method, params)

        self.native.rpc = fail_delete
        try:
            await asyncio.wait_for(self.service.close(), 1)
        except RuntimeError:
            pass
        self.assertFalse(self.service.references)
        self.assertFalse(self.service.threads)
        self.assertEqual(self.native.closed, 1)
        lease = AuthLease(self.home)
        lease.acquire()
        lease.release()


class CodexInheritedLeaseTests(unittest.TestCase):
    def test_native_child_lifetime_not_wrapper_lifetime_owns_lease(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "codex"
            first = AuthLease(home)
            first.acquire()
            child = subprocess.Popen(
                [sys.executable, "-c", "import sys; sys.stdin.read()"],
                stdin=subprocess.PIPE, pass_fds=(first.descriptor,),
            )
            second = AuthLease(home)
            try:
                first.release()
                with self.assertRaises(CodexAuthError):
                    second.acquire()
            finally:
                if child.stdin is not None:
                    child.stdin.close()
                child.wait(timeout=5)
                first.release()
                second.release()
            second.acquire()
            second.release()


if __name__ == "__main__":
    unittest.main()
