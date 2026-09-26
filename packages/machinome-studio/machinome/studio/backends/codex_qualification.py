# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Credential-free real-binary registration/rejection proof for private policy.

Only this probe uses a loopback model fixture. Production never accepts a
provider override, fixture executable or bypass environment variable.
"""
from __future__ import annotations
import asyncio
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import queue
import tempfile
import threading
from typing import Any

from ..codex_auth import child_environment, codex_binary
from .codex_policy import SCHEMA_FINGERPRINTS, CodexPolicyError, check_policy, command, controlled_catalogue, digest, settings, validate_schema
from .codex_wire import CodexConnection, CodexProtocolError

PROBE_TIMEOUT = 90


class _ModelServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self):
        super().__init__(("127.0.0.1", 0), _Handler)
        self.items: queue.Queue[dict[str, Any] | None] = queue.Queue()
        self.requests: list[dict[str, Any]] = []
        self.worker = threading.Thread(target=self.serve_forever, daemon=True)
        self.worker.start()


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_: Any) -> None:
        pass

    def do_POST(self) -> None:
        server: _ModelServer = self.server  # type: ignore[assignment]
        size = int(self.headers.get("Content-Length", "0"))
        if not 0 < size <= 8 * 1024 * 1024:
            self.send_error(400)
            return
        request = json.loads(self.rfile.read(size))
        server.requests.append(request)
        item = server.items.get(timeout=5)
        if item is None:
            item = {"type": "message", "id": f"msg_{len(server.requests)}", "role": "assistant", "status": "completed",
                    "content": [{"type": "output_text", "text": "DONE"}]}
        identity = f"response_{len(server.requests)}"
        events = [
            {"type": "response.created", "response": {"id": identity}},
            {"type": "response.output_item.added", "output_index": 0, "item": item},
            {"type": "response.output_item.done", "output_index": 0, "item": item},
            {"type": "response.completed", "response": {"id": identity, "status": "completed", "output": [item],
                                                        "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}}},
        ]
        body = "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _registry(request: dict[str, Any]) -> dict[str, Any]:
    specs = list(request.get("tools", []))
    for item in request.get("input", []):
        if item.get("type") == "additional_tools":
            specs.extend(item["tools"])
        if "<skills_instructions>" in json.dumps(item):
            raise CodexPolicyError("Codex imported native skill instructions")
    result = {}
    for spec in specs:
        if spec["type"] != "namespace" or spec["name"] != "functions":
            raise CodexPolicyError("Codex exposed an unexpected tool namespace")
        for tool in spec["tools"]:
            if tool["name"] in result or tool["type"] != "function":
                raise CodexPolicyError("Codex exposed an unexpected tool declaration")
            result[tool["name"]] = tool["parameters"]
    return result


def _call(name: str, *, namespace: str | None = None) -> dict[str, Any]:
    item = {"type": "function_call", "id": "fixture_item", "call_id": "fixture_call", "name": name, "arguments": "{}"}
    if namespace:
        item["namespace"] = namespace
    return item


class CodexQualifier:
    """Success cache belongs to one injected hub manager, never process globals."""
    def __init__(self):
        self._successes: set[str] = set()

    async def qualify(self, registries: list[list[dict[str, Any]]]) -> dict[str, Any]:
        binary = await _bounded_read(codex_binary)
        binary_digest = await _bounded_read(digest, binary)
        catalog = await _bounded_read(controlled_catalogue, binary)
        configuration = await self._configuration(binary, catalog)
        contract = hashlib.sha256(json.dumps({"binary": binary_digest, "binary_path": str(binary), "catalogue": catalog,
                                             "policy": settings(Path("<private-catalogue>")), "configuration": configuration,
                                             "schemas": SCHEMA_FINGERPRINTS}, sort_keys=True).encode()).hexdigest()
        fingerprint = hashlib.sha256(json.dumps({"contract": contract, "registries": registries}, sort_keys=True).encode()).hexdigest()
        if fingerprint in self._successes:
            return {"fingerprint": fingerprint, "contract": contract, "binary": str(binary), "binary_digest": binary_digest, "cached": True}
        async with asyncio.timeout(PROBE_TIMEOUT):
            cases = await self._probe(binary, catalog, registries)
        # Recheck actual executable, not only version text after probing.
        if await _bounded_read(digest, binary) != binary_digest:
            raise CodexPolicyError("Codex executable changed during qualification")
        self._successes.add(fingerprint)
        return {"fingerprint": fingerprint, "contract": contract, "binary": str(binary), "binary_digest": binary_digest, "cases": cases, "cached": False}

    async def _configuration(self, binary: Path, catalog: dict[str, Any]) -> Any:
        with tempfile.TemporaryDirectory(prefix="studio-codex-config-") as temporary:
            private = Path(temporary)
            home = private / "codex"
            home.mkdir(mode=0o700)
            catalogue = private / "catalogue.json"
            catalogue.write_text(json.dumps(catalog))
            policy = settings(catalogue)
            connection = await CodexConnection.start(command(binary, policy), cwd=str(private), env=child_environment(home, private))
            try:
                await check_policy(connection, policy)
                response = await connection.rpc("config/read", {"includeLayers": True})
                effective = response["config"]
                effective["model_catalog_json"] = "<private-catalogue>"
                return {"effective": effective, "layers": [{"type": layer["name"]["type"], "version": layer["version"]}
                         for layer in response["layers"] if layer["name"]["type"] != "sessionFlags"],
                        "requirements": await connection.rpc("configRequirements/read", {})}
            finally:
                await connection.close()

    async def _probe(self, binary: Path, catalog: dict[str, Any], registries: list[list[dict[str, Any]]]) -> int:
        server = _ModelServer()
        connection = None
        cases = 0
        temporary = tempfile.TemporaryDirectory(prefix="studio-codex-qualify-")
        try:
            private = Path(temporary.name)
            home = private / "codex"
            home.mkdir(mode=0o700)
            environment = child_environment(home, private)
            await _bounded_read(validate_schema, binary, private, environment)
            catalogue = private / "catalogue.json"
            catalogue.write_text(json.dumps(catalog))
            policy = settings(catalogue)
            # Fixture transport is uncredentialed and internal to this proof.
            policy["model_provider"] = "studio_qualification"
            policy["model_providers"] = {"studio_qualification": {
                "name": "Studio local qualification", "base_url": f"http://127.0.0.1:{server.server_port}/v1",
                "wire_api": "responses", "requires_openai_auth": False, "supports_websockets": False,
            }}
            connection = await CodexConnection.start(command(binary, policy), cwd=str(private), env=environment)
            await check_policy(connection, policy)

            async def turn(thread: str, registry: list[dict[str, Any]], item: dict[str, Any] | None, model: str) -> str:
                nonlocal cases
                first = len(server.requests)
                server.items.put(item)
                if item is not None:
                    server.items.put(None)
                result = await connection.rpc("turn/start", {"threadId": thread, "environments": [], "model": model,
                                                           "input": [{"type": "text", "text": "Run the synthetic qualification fixture."}]})
                identity = result["turn"]["id"]
                expected = {tool["name"]: tool["inputSchema"] for tool in registry}
                callbacks = 0
                while True:
                    frame = await asyncio.wait_for(connection.notifications.get(), 15)
                    method = frame.get("method")
                    if "id" in frame:
                        if method != "item/tool/call":
                            raise CodexPolicyError("Codex requested an undeclared native operation")
                        params = frame["params"]
                        if (params["threadId"] != thread or params["turnId"] != identity
                                or params["tool"] not in expected or params.get("namespace") not in (None, "functions")):
                            raise CodexPolicyError("A forced undeclared Codex call reached the client")
                        callbacks += 1
                        await connection.send({"id": frame["id"], "result": {"success": True, "contentItems": [{"type": "inputText", "text": "STUDIO_QUALIFIED"}]}})
                    if method == "turn/completed" and frame["params"]["turn"]["id"] == identity:
                        if frame["params"]["turn"]["status"] != "completed":
                            raise CodexPolicyError("Codex qualification turn failed")
                        break
                requests = server.requests[first:]
                if not requests or any(_registry(request) != expected for request in requests):
                    raise CodexPolicyError("Codex advertised tools differ from the declared registry")
                allowed = item is not None and item["name"] in expected
                if callbacks != int(allowed):
                    raise CodexPolicyError("Codex did not enforce the expected forced-call boundary")
                if item is not None and not allowed:
                    outputs = [i for request in requests for i in request.get("input", []) if i.get("type") in ("function_call_output", "custom_tool_call_output")]
                    if not outputs or "unsupported" not in str(outputs[-1].get("output")):
                        raise CodexPolicyError("Codex did not reject a forced undeclared operation")
                cases += 1
                return identity

            group_parameters = {"name": "Studio qualification group", "roots": [], "idempotencyKey": "studio-qualification",
                                "metadata": {"owner": "machinome-studio-qualification"}}
            group = (await connection.rpc("project/create", group_parameters))["project"]
            if group["roots"] != [] or group["metadata"] != group_parameters["metadata"]:
                raise CodexPolicyError("Codex native group metadata does not preserve ownership")
            for registry in [*registries, []]:
                thread = (await connection.rpc("thread/start", {"model": "gpt-6-sol", "cwd": str(private), "environments": [],
                                                                "projectId": group["id"], "dynamicTools": registry, "sandbox": "read-only", "approvalPolicy": "never"}))["thread"]["id"]
                if registry:
                    await turn(thread, registry, _call(registry[0]["name"]), "gpt-6-sol")
                for model in ("gpt-6-sol", "gpt-6-astra"):
                    for name in ("exec_command", "shell", "shell_command", "write_stdin", "apply_patch", "view_image", "list_mcp_resources", "spawn_agent", "request_user_input", "update_plan", "web.run", "floor_undeclared"):
                        await turn(thread, registry, _call(name), model)
                    await turn(thread, registry, {"type": "custom_tool_call", "id": "fixture_patch", "call_id": "fixture_patch",
                        "name": "apply_patch", "input": "*** Begin Patch\n*** Add File: forbidden-patch\n+bad\n*** End Patch"}, model)
                    await turn(thread, registry, {"type": "custom_tool_call", "id": "fixture_exec", "call_id": "fixture_exec",
                        "namespace": "functions", "name": "exec", "input": "text(typeof tools.exec_command);"}, model)
                    await turn(thread, registry, _call("list_agents", namespace="collaboration"), model)
                await connection.close()
                connection = await CodexConnection.start(command(binary, policy), cwd=str(private), env=environment)
                await check_policy(connection, policy)
                repeated = (await connection.rpc("project/create", group_parameters))["project"]
                if repeated["id"] != group["id"] or repeated["metadata"] != group_parameters["metadata"]:
                    raise CodexPolicyError("Codex native owner group is not durable/idempotent")
                inventory = await connection.rpc("thread/list", {"projectId": group["id"], "sourceKinds": ["vscode", "appServer", "cli"], "limit": 100})
                if not any(item["id"] == thread and item["projectId"] == group["id"] for item in inventory["data"]):
                    raise CodexPolicyError("Codex did not retain the thread's exact owner marker")
                retained = (await connection.rpc("thread/resume", {"threadId": thread}))["thread"]
                latest = await turn(thread, registry, _call("apply_patch"), "gpt-6-sol")
                if registry:
                    latest = await turn(thread, registry, _call(registry[0]["name"]), "gpt-6-sol")
                try:
                    await connection.rpc("turn/steer", {"threadId": thread, "expectedTurnId": latest,
                        "input": [{"type": "text", "text": "Completed-turn steering fixture"}]})
                except CodexProtocolError:
                    completed = (await connection.rpc("thread/read", {"threadId": thread, "includeTurns": True}))["thread"]
                    if completed["id"] != thread or not any(item["id"] == latest and item["status"] == "completed" for item in completed["turns"]):
                        raise CodexPolicyError("Codex completed steering race lacks exact native completion evidence")
                else:
                    raise CodexPolicyError("Codex accepted steering after native completion")
                await connection.rpc("thread/delete", {"threadId": thread})
                for archived in (False, True):
                    removed = await connection.rpc("thread/list", {"projectId": group["id"], "sourceKinds": ["vscode", "appServer", "cli"], "limit": 100, "archived": archived})
                    if any(item["id"] == thread for item in removed["data"]) or removed.get("nextCursor") is not None:
                        raise CodexPolicyError("Codex thread deletion left native owner inventory")
                if not isinstance(retained.get("path"), str) or Path(retained["path"]).exists():
                    raise CodexPolicyError("Codex thread deletion left a native rollout record")
                if (private / "forbidden-patch").exists():
                    raise CodexPolicyError("Codex forced native patch mutated a qualification sentinel")
            return cases
        finally:
            if connection is not None:
                await connection.close()
            server.shutdown()
            server.server_close()
            server.worker.join(timeout=2)
            temporary.cleanup()


async def _bounded_read(function: Any, *arguments: Any) -> Any:
    """Read-only vendor inspection must finish before private state is removed."""
    task = asyncio.create_task(asyncio.to_thread(function, *arguments))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        try:
            await task
        finally:
            raise
