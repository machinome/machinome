# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Coordinator-owned process tests: cancellation must stop tool descendants."""
from __future__ import annotations

import asyncio
import base64
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest

from floor.backends.base import RoleContext
from floor.backends.codex_tools import FloorWorker, dynamic_result
from floor.backends.codex_wire import CodexProtocolError
from floor.profiles import load_profile, resolve_profile_runtime

ROOT = Path(__file__).resolve().parents[1]


class CodexResultAdversarialTests(unittest.TestCase):
    def test_result_conversion_rejects_unsupported_and_oversized_content(self):
        invalid = [None, {}, {"content": []}, {"content": [None]},
            {"content": [{"type": "resource", "uri": "file:///outside"}]},
            {"content": [{"type": "image", "mimeType": "image/svg+xml", "data": "YWJj"}]},
            {"content": [{"type": "text", "text": 42}]},
            {"content": [{"type": "text", "text": "x"}] * 129},
            {"content": [{"type": "text", "text": "x" * (6 * 1024 * 1024)}]}]
        for index, result in enumerate(invalid):
            with self.subTest(index=index), self.assertRaises(CodexProtocolError):
                dynamic_result(result)

    def test_malformed_image_cannot_be_forwarded_and_tool_error_is_preserved(self):
        with self.assertRaises(ValueError):
            dynamic_result({"content": [{"type": "image", "mimeType": "image/png", "data": "invalid!!"}]})
        result = dynamic_result({"isError": True, "content": [{"type": "text", "text": "fixture denied"}]})
        self.assertEqual(result, {"success": False,
            "contentItems": [{"type": "inputText", "text": "fixture denied"}]})


class CodexWorkerAdversarialTests(unittest.IsolatedAsyncioTestCase):
    async def test_partial_worker_start_reaps_process_and_private_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            agent = resolve_profile_runtime(load_profile("builder", shop_root=ROOT)).agents[0]
            context = RoleContext(str(ROOT), temporary, agent, "builder", "Pilot", "Builder")
            worker = FloorWorker(context, machinome_command=("unused",),
                broker_url="http://127.0.0.1:1", session_id="synthetic")
            worker.command = [sys.executable, "-c",
                "import sys,time; sys.stdin.readline(); print('invalid native frame',flush=True); time.sleep(60)"]
            try:
                with self.assertRaises(CodexProtocolError):
                    await asyncio.wait_for(worker.start(), 3)
                self.assertIsNotNone(worker.process)
                self.assertIsNotNone(worker.process.returncode)
                self.assertIsNone(worker.private)
                await worker.close()
            finally:
                await worker.close()

    async def test_actual_worker_preserves_large_image_and_denies_undeclared_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            # Valid small PNG with an inert trailing payload exercises stdio
            # frames larger than asyncio's usual 64-KiB reader limit.
            payload = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=") + b"\0" * 96_000
            (project / "fixture.png").write_bytes(payload)
            agent = resolve_profile_runtime(load_profile("builder", shop_root=ROOT)).agents[0]
            agent = replace(agent, skills=(), runtime=replace(agent.runtime, tools=("Read",)))
            context = RoleContext(str(ROOT), str(project), agent, "builder", "Pilot", "Builder")
            worker = FloorWorker(context, machinome_command=("unused",), broker_url="http://127.0.0.1:1", session_id="synthetic")
            await worker.start()
            try:
                result = await worker.rpc("tools/call", {"name": "read_file", "arguments": {"path": "fixture.png"}})
                image = dynamic_result(result)["contentItems"][0]
                self.assertEqual(image["type"], "inputImage")
                self.assertEqual(base64.b64decode(image["imageUrl"].split(",", 1)[1]), payload)
                denied = await worker.rpc("tools/call", {"name": "write_file", "arguments": {"path": "forbidden", "content": "bad"}})
                self.assertTrue(denied["isError"])
                outside = await worker.rpc("tools/call", {"name": "read_file", "arguments": {"path": "/proc/self/environ"}})
                self.assertTrue(outside["isError"])
                self.assertEqual([path.name for path in project.iterdir()], ["fixture.png"])
            finally:
                await worker.close()

    async def test_cancelled_close_still_kills_descendant_before_late_mutation(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            started, mutation = project / "started", project / "forbidden-late-write"
            agent = resolve_profile_runtime(load_profile("builder", shop_root=ROOT)).agents[0]
            agent = replace(agent, skills=(), runtime=replace(agent.runtime, tools=("Read",)))
            context = RoleContext(str(ROOT), str(project), agent, "builder", "Pilot", "Builder")
            worker = FloorWorker(context, machinome_command=("unused",), broker_url="http://127.0.0.1:1", session_id="synthetic")
            child_code = (
                "import pathlib,signal,sys,time; "
                "signal.signal(signal.SIGTERM,signal.SIG_IGN); "
                "pathlib.Path(sys.argv[1]).touch(); time.sleep(1.5); "
                "pathlib.Path(sys.argv[2]).write_text('late mutation')"
            )
            server_code = """
import json, signal, subprocess, sys, time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
for line in sys.stdin:
    request = json.loads(line)
    method = request['method']
    if method == 'tools/call':
        subprocess.Popen([sys.executable, '-c', sys.argv[1], sys.argv[2], sys.argv[3]])
        time.sleep(60)
    result = {'tools': [{'name': 'read_file'}, {'name': 'stat'}]} if method == 'tools/list' else {}
    print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result}), flush=True)
"""
            worker.command = [sys.executable, "-c", server_code, child_code, str(started), str(mutation)]
            await worker.start()
            process = worker.process
            private = Path(worker.private.name)
            operation = asyncio.create_task(worker.rpc("tools/call", {"name": "read_file", "arguments": {"path": "anything"}}))
            try:
                async with asyncio.timeout(3):
                    while not started.exists():
                        await asyncio.sleep(0.01)
                closing = asyncio.create_task(worker.close())
                await asyncio.sleep(0)
                closing.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await closing
                await asyncio.wait_for(worker.close(), 2)
                self.assertIsNotNone(process.returncode)
                self.assertFalse(private.exists())
                await asyncio.sleep(1.6)
                self.assertFalse(mutation.exists(), "a child wrote after its role worker closed")
            finally:
                await worker.close()
                await asyncio.gather(operation, return_exceptions=True)
