# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Native synthetic callbacks through actual owned workers, no model/auth."""
import asyncio
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import unittest

from floor.backends.base import RoleContext
from floor.backends.codex import CodexBackend
from floor.profiles import load_profile, resolve_profile_runtime
from tests import test_codex_service as fixtures

ROOT = Path(__file__).resolve().parents[1]


class CodexDelegationTests(unittest.IsolatedAsyncioTestCase):
    async def test_declared_lifecycle_names_and_identities_reach_owned_session(self):
        await fixtures.CodexServiceTests.asyncSetUp(self)
        requests = []
        class BrokerFixture(BaseHTTPRequestHandler):
            def do_POST(handler):
                body = json.loads(handler.rfile.read(int(handler.headers["Content-Length"])))
                requests.append((handler.path, body))
                handler.send_response(200)
                handler.send_header("Content-Type", "application/json")
                handler.end_headers()
                handler.wfile.write(b'{"ok":true}')

            def log_message(handler, *_):
                pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), BrokerFixture)
        serving = threading.Thread(target=server.serve_forever, daemon=True)
        serving.start()
        original = self.native.rpc
        async def rpc(method, params):
            if method == "turn/start":
                return {"turn": {"id": "turn-" + params["threadId"]}}
            return await original(method, params)
        self.native.rpc = rpc
        reference = await self.service.acquire("delegated-synthetic", [])
        backend = CodexBackend(shop_root=ROOT, project=Path(self.temporary.name),
            broker_url=f"http://127.0.0.1:{server.server_port}", session_id=reference.session_id,
            codex_service=self.service, codex_reference=reference)
        try:
            profile = resolve_profile_runtime(load_profile("fordesmac", shop_root=ROOT))
            handles = {}
            for role in ("foreman", "machinist"):
                agent = profile.agent(role)
                agent = replace(agent, runtime=replace(agent.runtime, backend="codex", model="gpt-6-sol", effort="medium"))
                context = RoleContext(str(ROOT), self.temporary.name, agent, profile.id, profile.user_label, profile.user_agent.label)
                handles[role] = await backend.open_role(role, context)
                await backend.deliver_start(handles[role], "Synthetic lifecycle request")
            async def call(role, tool, arguments, identity):
                state = backend.roles[handles[role].backend_id]
                await backend._callback(state, {"id": identity, "studioGeneration": state.thread.generation,
                    "params": {"threadId": state.thread.thread_id, "turnId": state.native_turn,
                    "callId": f"call-{identity}", "namespace": "functions", "tool": tool, "arguments": arguments}})
                self.assertTrue(self.native.responses[-1]["result"]["success"])
            await call("foreman", "floor_assign", {"sender": "foreman", "recipient": "machinist", "assignment": "fixture", "text": "Synthetic task"}, 1)
            await call("machinist", "floor_acknowledge", {"role": "machinist", "assignment": "fixture"}, 2)
            await call("machinist", "floor_report", {"sender": "machinist", "recipient": "foreman", "assignment": "fixture", "text": "Synthetic completion"}, 3)
            await call("machinist", "floor_complete", {"role": "machinist", "assignment": "fixture"}, 4)
            self.assertEqual([path for path, _ in requests], [
                "/api/sessions/delegated-synthetic/envelopes", "/api/sessions/delegated-synthetic/agents/machinist/acknowledgments",
                "/api/sessions/delegated-synthetic/envelopes", "/api/sessions/delegated-synthetic/agents/machinist/completions"])
            self.assertEqual(requests[0][1]["sender"], "foreman")
            self.assertEqual(requests[2][1]["sender"], "machinist")
        finally:
            await backend.close()
            await asyncio.to_thread(server.shutdown)
            server.server_close()
            serving.join(timeout=2)
            await fixtures.CodexServiceTests.asyncTearDown(self)
