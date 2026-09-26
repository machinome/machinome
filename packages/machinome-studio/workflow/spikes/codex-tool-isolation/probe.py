#!/usr/bin/env python3
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Exercise the real Codex app-server with a deterministic local model transport.

No model credentials, external model requests, project execution or production
configuration are used. All Codex state and sentinels live in temporary storage.
The mock deliberately sends tool calls even when they were not advertised.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


DISABLED = (
    "apps", "plugins", "browser_use", "browser_use_external", "computer_use",
    "multi_agent", "multi_agent_v2", "hooks", "memories", "image_generation",
    "shell_tool", "shell_snapshot", "view_image", "goals", "sleep_tool",
    "skill_search", "skill_mcp_dependency_install", "enable_request_compression",
    "code_mode", "code_mode_host", "workspace_dependencies", "tool_suggest",
)
HELLO = {
    "type": "function", "name": "floor_hello", "description": "Return a fixture greeting.",
    "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}},
                    "required": ["name"], "additionalProperties": False},
}


class ModelServer(ThreadingHTTPServer):
    def __init__(self):
        super().__init__(("127.0.0.1", 0), ModelHandler)
        self.requests = []
        self.outputs = queue.Queue()
        threading.Thread(target=self.serve_forever, daemon=True).start()


class ModelHandler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.requests.append(request)
        try:
            item = self.server.outputs.get(timeout=5)
        except queue.Empty:
            item = None
        response_id = f"resp_{len(self.server.requests)}"
        events = [{"type": "response.created", "response": {"id": response_id}}]
        if item is None:
            item = {"type": "message", "id": "msg_fixture", "role": "assistant",
                    "status": "completed", "content": [{"type": "output_text", "text": "DONE"}]}
        events.extend([
            {"type": "response.output_item.added", "output_index": 0, "item": item},
            {"type": "response.output_item.done", "output_index": 0, "item": item},
            {"type": "response.completed", "response": {"id": response_id,
             "status": "completed", "output": [item],
             "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}}},
        ])
        body = "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class Client:
    def __init__(self, codex, root, model_server, events, catalog=None, guard_turns=False):
        self.events = events
        self.guard_turns = guard_turns
        self.incoming = queue.Queue()
        self.ident = 0
        env = {k: v for k, v in os.environ.items()
               if k in ("PATH", "LANG", "LC_ALL", "SSL_CERT_FILE", "SSL_CERT_DIR")}
        env.update(HOME=str(root / "home"), CODEX_HOME=str(root / "home/.codex"),
                   XDG_CONFIG_HOME=str(root / "home/.config"),
                   XDG_DATA_HOME=str(root / "home/.local/share"))
        config = {
            "model_provider": '"spike"',
            "model_providers.spike.name": '"Local fixture"',
            "model_providers.spike.base_url": json.dumps(f"http://127.0.0.1:{model_server.server_port}/v1" if model_server else ""),
            "model_providers.spike.wire_api": '"responses"',
            "model_providers.spike.requires_openai_auth": "false",
            "model_providers.spike.supports_websockets": "false",
            "web_search": '"disabled"', "sandbox_mode": '"read-only"',
            "approval_policy": '"never"', "analytics.enabled": "false",
            "feedback.enabled": "false",
            "tools.experimental_request_user_input.enabled": "false",
            "tools.update_plan.enabled": "false",
        }
        if model_server is None:
            config = {key: value for key, value in config.items()
                      if key != "model_provider" and not key.startswith("model_providers.")}
        if catalog:
            config["model_catalog_json"] = json.dumps(str(catalog))
        command = [codex]
        for name in DISABLED:
            command += ["--disable", name]
        for key, value in config.items():
            command += ["-c", f"{key}={value}"]
        command += ["app-server", "--stdio"]
        self.stderr = []
        self.proc = subprocess.Popen(command, cwd=root / "project", env=env,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, bufsize=1)
        threading.Thread(target=self._read, daemon=True).start()
        threading.Thread(target=lambda: self.stderr.extend(self.proc.stderr), daemon=True).start()
        self.rpc("initialize", {"clientInfo": {"name": "studio_isolation_spike", "version": "0.1"},
                                "capabilities": {"experimentalApi": True}})
        self.send({"method": "initialized"})

    def _read(self):
        for line in self.proc.stdout:
            try:
                self.incoming.put(json.loads(line))
            except json.JSONDecodeError:
                self.events.append({"non_json_stdout": line})
        self.incoming.put({"process_ended": self.proc.poll()})

    def send(self, message):
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def next(self, timeout=60):
        message = self.incoming.get(timeout=timeout)
        self.events.append(message)
        if "process_ended" in message:
            raise RuntimeError("app-server ended: " + "".join(self.stderr)[-4000:])
        if message.get("method") == "item/tool/call" and "id" in message:
            params = message["params"]
            success = params["tool"] == "floor_hello"
            result = "HELLO_SPIKE_RESULT" if success else "DENIED_BY_SPIKE_CLIENT"
            self.send({"id": message["id"], "result": {"success": success,
                       "contentItems": [{"type": "inputText", "text": result}]}})
        elif "method" in message and "id" in message:
            self.send({"id": message["id"], "error": {"code": -32601, "message": "Denied by spike"}})
        return message

    def rpc(self, method, params):
        self.ident += 1
        ident = self.ident
        self.send({"id": ident, "method": method, "params": params})
        while True:
            message = self.next()
            if message.get("id") == ident and "method" not in message:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message["result"]

    def turn(self, thread, server, item, *, model=None):
        start = len(server.requests)
        server.outputs.put(item)
        if item is not None:
            server.outputs.put(None)
        params = {"threadId": thread, "input": [{"type": "text", "text": "Run this fixture."}]}
        if self.guard_turns:
            params["environments"] = []
        if model:
            params["model"] = model
        result = self.rpc("turn/start", params)
        turn_id = result["turn"]["id"]
        while True:
            message = self.next()
            if (message.get("method") == "turn/completed"
                    and message["params"]["turn"]["id"] == turn_id):
                assert message["params"]["turn"]["status"] == "completed", message
                return server.requests[start:]

    def close(self):
        if self.proc.poll() is not None:
            return
        self.proc.stdin.close()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()


def call(name, arguments):
    return {"type": "function_call", "id": "fc_fixture", "call_id": "call_fixture",
            "name": name, "arguments": json.dumps(arguments)}


def exposed_tools(request):
    specs = list(request.get("tools", []))
    for item in request.get("input", []):
        if item.get("type") == "additional_tools":
            specs.extend(item["tools"])
    names = []
    for spec in specs:
        if spec["type"] == "namespace":
            names.extend(f"{spec['name']}.{tool['name']}" for tool in spec["tools"])
        else:
            names.append(spec.get("name", spec["type"]))
    return sorted(names)


def summarize(label, requests):
    outputs = [item for item in requests[-1].get("input", [])
               if item.get("type") in ("function_call_output", "custom_tool_call_output")]
    return {"name": label, "models": [request["model"] for request in requests],
            "tool_sets": [exposed_tools(request) for request in requests],
            "last_output": outputs[-1].get("output") if outputs else None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--controlled-catalog", action="store_true")
    parser.add_argument("--guard-turns", action="store_true")
    args = parser.parse_args()
    codex = shutil.which("codex")
    assert codex
    evidence = {"version": subprocess.check_output([codex, "--version"], text=True).strip(),
                "disabled_features": DISABLED, "cases": [], "events": []}
    server = ModelServer()
    client = None
    try:
        with tempfile.TemporaryDirectory(prefix="studio-codex-spike-") as temporary:
            root = Path(temporary)
            (root / "project").mkdir()
            (root / "home/.codex").mkdir(parents=True)
            catalog = None
            if args.controlled_catalog:
                models = json.loads(subprocess.check_output([codex, "debug", "models", "--bundled"], text=True))
                for model in models["models"]:
                    model["tool_mode"] = "direct"
                    model.pop("multi_agent_version", None)
                    model["experimental_supported_tools"] = []
                catalog = root / "models.json"
                catalog.write_text(json.dumps(models))
            evidence["controlled_catalog"] = args.controlled_catalog
            evidence["guard_turns"] = args.guard_turns
            sentinel = root / "project/sentinel.txt"
            sentinel.write_text("UNCHANGED\n")
            client = Client(codex, root, server, evidence["events"], catalog, args.guard_turns)
            params = {"model": "gpt-6-sol", "cwd": str(root / "project"),
                      "environments": [], "dynamicTools": [HELLO],
                      "sandbox": "read-only", "approvalPolicy": "never"}
            started = client.rpc("thread/start", params)
            thread = started["thread"]["id"]
            probes = [
                ("hello", call("floor_hello", {"name": "Spike"})),
                ("native_exec", call("exec_command", {"cmd": "touch forbidden-native-exec"})),
                ("native_shell", call("shell", {"command": ["touch", "forbidden-native-exec"]})),
                ("native_shell_command", call("shell_command", {"command": "touch forbidden-native-exec"})),
                ("native_stdin", call("write_stdin", {"session_id": 99999, "chars": ""})),
                ("native_patch", {"type": "custom_tool_call", "id": "ctc_fixture", "call_id": "call_fixture",
                                  "name": "apply_patch", "input": "*** Begin Patch\n*** Add File: forbidden-native-patch\n+bad\n*** End Patch"}),
                ("native_image", call("view_image", {"path": str(sentinel)})),
                ("native_mcp", call("list_mcp_resources", {})),
                ("native_delegation", call("spawn_agent", {"message": "Read sentinel.txt"})),
                ("namespaced_agent_list", {**call("list_agents", {}), "namespace": "collaboration"}),
                ("native_question", call("request_user_input", {"questions": []})),
                ("native_plan", call("update_plan", {"plan": []})),
                ("native_web", call("web.run", {"search_query": [{"q": "fixture"}]})),
                ("code_mode_inventory", {"type": "custom_tool_call", "id": "ctc_inventory", "call_id": "call_inventory",
                                         "namespace": "functions", "name": "exec",
                                         "input": "text(ALL_TOOLS.map(t => t.name)); text(typeof tools.exec_command); text(typeof tools.apply_patch);"}),
                ("undeclared_dynamic", call("floor_write_file", {"path": str(sentinel), "text": "BAD"})),
                ("second_turn", call("floor_hello", {"name": "Again"})),
            ]
            for label, item in probes:
                item["call_id"] = f"call_{label}"
                requests = client.turn(thread, server, item)
                evidence["cases"].append(summarize(label, requests))
                if args.controlled_catalog:
                    assert all(exposed_tools(request) == ["functions.floor_hello"] for request in requests)
                    output = evidence["cases"][-1]["last_output"]
                    if label in ("hello", "second_turn"):
                        assert output == "HELLO_SPIKE_RESULT", output
                    else:
                        assert "unsupported" in output, output
                assert sentinel.read_text() == "UNCHANGED\n"
                assert not (root / "project/forbidden-native-exec").exists()
                assert not (root / "project/forbidden-native-patch").exists()
                print(label, "completed", flush=True)
            requests = client.turn(thread, server, call("floor_hello", {"name": "Switch"}), model="gpt-6-astra")
            evidence["cases"].append(summarize("model_change", requests))
            requests = client.turn(thread, server, probes[1][1])
            evidence["cases"].append(summarize("model_change_native_exec", requests))
            client.close()
            client = Client(codex, root, server, evidence["events"], catalog, args.guard_turns)
            client.rpc("thread/resume", {"threadId": thread})
            requests = client.turn(thread, server, call("floor_hello", {"name": "Resume"}))
            evidence["cases"].append(summarize("restart_resume", requests))
            requests = client.turn(thread, server, probes[4][1])
            evidence["cases"].append(summarize("restart_resume_native_stdin", requests))
            requests = client.turn(thread, server, probes[5][1])
            evidence["cases"].append(summarize("restart_resume_native_patch", requests))
            # A second role must not acquire the first role's dynamic tool.
            other = client.rpc("thread/start", {**params, "dynamicTools": []})["thread"]["id"]
            requests = client.turn(other, server, call("floor_hello", {"name": "Other role"}))
            evidence["cases"].append(summarize("other_role_no_tools", requests))
            if args.controlled_catalog:
                assert all(exposed_tools(request) == [] for request in requests)
                assert "unsupported" in evidence["cases"][-1]["last_output"]
                for case in evidence["cases"][:-1]:
                    assert all(names == ["functions.floor_hello"] for names in case["tool_sets"]), case
                    if case["name"] in ("hello", "second_turn", "model_change", "restart_resume"):
                        assert case["last_output"] == "HELLO_SPIKE_RESULT", case
                    else:
                        assert "unsupported" in case["last_output"], case
            # Positive control: omitting environments must restore native patching
            # in the advertised registry, even with shell tools disabled.
            control_params = {k: v for k, v in params.items() if k != "environments"}
            control = client.rpc("thread/start", control_params)["thread"]["id"]
            client.guard_turns = False
            requests = client.turn(control, server, None)
            evidence["cases"].append(summarize("positive_control_default_environment", requests))
            if args.controlled_catalog:
                assert any("apply_patch" in name for name in exposed_tools(requests[0]))
            evidence["sentinel_unchanged"] = sentinel.read_text() == "UNCHANGED\n"
            assert evidence["sentinel_unchanged"]
            assert not (root / "project/forbidden-native-exec").exists()
            assert not (root / "project/forbidden-native-patch").exists()
            evidence["completed"] = True
    except Exception as error:
        evidence["error"] = repr(error)
        raise
    finally:
        if client:
            client.close()
            evidence["stderr"] = client.stderr
        # Keep raw fixture transport separately for audit; the summary stays small.
        args.output.parent.mkdir(parents=True, exist_ok=True)
        evidence["raw_transport_file"] = str(args.output.with_suffix(".raw.json"))
        args.output.with_suffix(".raw.json").write_text(json.dumps(server.requests, indent=2) + "\n")
        evidence["dynamic_calls"] = [event["params"] for event in evidence.pop("events")
                                     if event.get("method") == "item/tool/call"]
        server.shutdown()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2) + "\n")


if __name__ == "__main__":
    main()
