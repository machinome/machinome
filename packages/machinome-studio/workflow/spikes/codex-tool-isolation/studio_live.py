# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Bounded authenticated adapter diagnostic, ONLY temporary synthetic projects.

Run from the Studio worktree after review:
  PYTHONPATH=. /path/to/python docs/spikes/codex-tool-isolation/studio_live.py

Uses the separately provisioned Studio login through production CodexService.
Never reads/copies ordinary Codex credentials, prints vendor frames or tokens,
or runs mechanical projects. The HTTP peer is explicitly a diagnostic fixture,
not a substitute production broker or authentication implementation.
"""
import asyncio
from contextlib import nullcontext
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import random
import struct
import subprocess
import tempfile
import threading
import zlib

from floor.backends.base import InactiveTurn, RoleContext
from floor.backends.codex import CodexBackend
from floor.backends.codex_service import CodexService, role_registry
from floor.profiles import load_profile, resolve_profile_runtime

ROOT = Path(__file__).resolve().parents[3]


def check(name, value):
    if not value:
        raise AssertionError(name)
    print(json.dumps({"check": name, "passed": True}), flush=True)


def png():
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    rng = random.Random(123)
    pixels = bytearray()
    for y in range(192):
        pixels.append(0)
        for _ in range(192):
            low = [rng.randrange(64) for _ in range(3)]
            low[0 if y < 96 else 2] = rng.randrange(192, 256)
            pixels.extend(low)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 192, 192, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(bytes(pixels))) + chunk(b"IEND", b"")


class Events:
    def __init__(self, backend):
        self.backend = backend
        self.items = []
        self.changed = asyncio.Event()
        self.task = asyncio.create_task(self.read())

    async def read(self):
        async for event in self.backend.events:
            self.items.append(event)
            self.changed.set()

    async def completed(self, receipt):
        async with asyncio.timeout(120):
            while True:
                self.changed.clear()
                relevant = [event for event in self.items if event.delivery_id == receipt.delivery_id]
                if any(event.kind == "role_failed" for event in relevant):
                    raise RuntimeError("native model delivery unavailable; retained context preserved")
                if any(event.kind == "turn_completed" for event in relevant):
                    return "\n".join(event.text or "" for event in relevant if event.kind == "role_message")
                await self.changed.wait()


async def run():
    requests = []
    class Peer(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append((self.path, body))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

        def log_message(self, *_):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), Peer)
    serving = threading.Thread(target=server.serve_forever, daemon=True)
    serving.start()
    service = CodexService()
    adapters, readers, paths = [], [], []
    temporary = tempfile.TemporaryDirectory(prefix="studio-codex-live-")
    try:
        with nullcontext(temporary.name) as directory:
            base = Path(directory)
            profiles = {name: resolve_profile_runtime(load_profile(name, shop_root=ROOT)) for name in ("builder", "fordesmac")}
            async def adapter(name, roles):
                project = base / name
                project.mkdir()
                subprocess.run(["git", "init", "-q", str(project)], check=True)
                profile = profiles[name]
                agents = {role: replace(profile.agent(role), runtime=replace(profile.agent(role).runtime,
                    backend="codex", model="gpt-6-sol", effort="low")) for role in roles}
                reference = await service.acquire("diagnostic-" + name, [role_registry(agent) for agent in agents.values()])
                backend = CodexBackend(shop_root=ROOT, project=project, model=None,
                    broker_url=f"http://127.0.0.1:{server.server_port}", session_id=reference.session_id,
                    codex_service=service, codex_reference=reference)
                adapters.append(backend)
                reader = Events(backend)
                readers.append(reader)
                handles = {}
                for role, agent in agents.items():
                    handles[role] = await backend.open_role(role, RoleContext(str(ROOT), str(project), agent,
                        profile.id, profile.user_label, profile.user_agent.label))
                return backend, reader, handles, project

            direct, events, handles, project = await adapter("builder", ("builder",))
            handle = handles["builder"]
            image = png()
            check("image fixture exceeds64KiB", len(image) > 65536)
            (project / "fixture.png").write_bytes(image)
            receipt = await direct.deliver_start(handle,
                "This is a disposable backend diagnostic, no mechanical work. Remember memory marker SCOPED-EMBER. "
                "Call floor_read_file on fixture.png and inspect the image. Identify the dominant color of its top half and bottom half "
                "using marker IMAGE:<color>-top,<color>-bottom. Also read nonexistent.txt and report the expected tool error without changing files.")
            try:
                await direct.deliver_steer(handle, receipt.delivery_id, "Keep the exact requested image marker in the final response.")
                check("active steering", True)
                check("active notice", await direct.deliver_notice(handle, receipt.delivery_id, "This is a diagnostic notice, not another task."))
            except InactiveTurn:
                check("steering completion race", True)
            text = await events.completed(receipt)
            check("actual image observation", "IMAGE:red-top,blue-bottom" in text)
            check("image result activity", any(event.activity and "image result" in event.activity.summary for event in events.items))
            check("tool error activity", any(event.activity and event.activity.state == "failed" and event.activity.path == "nonexistent.txt" for event in events.items))
            check("late notice does not start turn", not await direct.deliver_notice(handle, receipt.delivery_id, "late"))
            state = direct.roles[handle.backend_id]
            native_thread = state.thread.thread_id
            await direct.update_runtime(handle, replace(state.runtime, model="gpt-6-astra", effort="low"))
            delegated, other_events, other_handles, other_project = await adapter("fordesmac", ("foreman", "machinist"))
            owner = service.connection
            check("two projects share authenticated owner", len(service.references) == 2 and owner is not None)
            memory_receipt = await direct.deliver_start(handle, "Return only the memory marker I asked you to remember. Do not use tools.")
            receipt = await delegated.deliver_start(other_handles["foreman"],
                "Disposable diagnostic, no mechanical work or file changes. Use floor_assign to send machinist assignment diagnostic-only "
                "with text 'Reply diagnostic complete without changing files'. Do not dispatch any other role. Then finish this diagnostic turn.")
            memory_text, _ = await asyncio.gather(events.completed(memory_receipt), other_events.completed(receipt))
            check("concurrent projects and model change retain context", "SCOPED-EMBER" in memory_text)
            check("model change retains thread", state.thread.thread_id == native_thread)
            assignment = next((body for path, body in requests if body.get("kind") == "assignment" and body.get("sender") == "foreman"), None)
            check("native foreman actual declared assignment tool", assignment is not None and assignment.get("recipient") == "machinist")
            assignment_id = assignment.get("assignment_id", "diagnostic-only")
            pristine = delegated.roles[other_handles["machinist"].backend_id]
            pristine_native = pristine.thread.thread_id
            foreman_native = delegated.roles[other_handles["foreman"].backend_id].thread.thread_id
            paths.extend(Path(thread.path) for thread in service.threads.values() if thread.path)
            await owner.close()
            await asyncio.sleep(0.1)
            receipt = await direct.deliver_start(handle, "After the transport restart, return only the memory marker from earlier. Do not use tools.")
            check("used context resumes without replay", "SCOPED-EMBER" in await events.completed(receipt))
            check("used native identities retained", state.thread.thread_id == native_thread
                  and delegated.roles[other_handles["foreman"].backend_id].thread.thread_id == foreman_native)
            check("pristine handle retained and native thread recreated", delegated.roles[other_handles["machinist"].backend_id] is pristine
                  and pristine.thread.thread_id != pristine_native)
            receipt = await delegated.deliver_start(other_handles["machinist"],
                f"Synthetic assignment {assignment_id}: acknowledge with floor_acknowledge, report diagnostic complete to foreman with floor_report, "
                "and floor_complete. No file changes or mechanical work. Use your own role identity.")
            await other_events.completed(receipt)
            check("native machinist lifecycle tools", any(path.endswith("/acknowledgments") for path, _ in requests)
                  and any(path.endswith("/completions") for path, _ in requests))
            check("native machinist report and exact session routes", any(body.get("kind") == "report" and body.get("sender") == "machinist"
                  and body.get("recipient") == "foreman" for _, body in requests)
                  and all(path.startswith("/api/sessions/diagnostic-fordesmac/") for path, _ in requests))
            paths.extend(Path(thread.path) for thread in service.threads.values() if thread.path)
            survivor = service.connection
            await direct.close()
            check("closing one project preserves sibling", service.connection is survivor and len(service.references) == 1)
            receipt = await delegated.deliver_start(other_handles["machinist"], "Return exactly SIBLING-ALIVE, no tools or file changes.")
            check("sibling delivers after other project closes", "SIBLING-ALIVE" in await other_events.completed(receipt))
            await delegated.close()
            check("last project reaps native owner", service.connection is None and survivor.process.returncode is not None)
            check("owned rollout files removed", bool(paths) and all(not path.exists() for path in paths))
            check("dedicated login persists", (service.home / "auth.json").is_file())
            check("synthetic projects unchanged", sorted(path.name for path in project.iterdir()) == [".git", "fixture.png"]
                  and sorted(path.name for path in other_project.iterdir()) == [".git"])
    finally:
        await asyncio.gather(*(adapter.close() for adapter in adapters), return_exceptions=True)
        try:
            await service.close()
        finally:
            for reader in readers:
                reader.task.cancel()
            await asyncio.gather(*(reader.task for reader in readers), return_exceptions=True)
            await asyncio.to_thread(server.shutdown)
            server.server_close()
            serving.join(timeout=2)
            temporary.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(asyncio.wait_for(run(), 600))
    except Exception as error:
        # No native frames, credential-bearing exception payloads or auth data.
        print(json.dumps({"passed": False, "failure_type": type(error).__name__,
                          "check": str(error) if isinstance(error, AssertionError) else "native delivery/setup failed",
                          "remedy": "Inspect sanitized Studio availability; model/account may be unavailable. No credentials were copied."}), flush=True)
        raise SystemExit(1) from None
