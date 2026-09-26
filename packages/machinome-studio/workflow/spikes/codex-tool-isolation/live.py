#!/usr/bin/env python3
"""Small authenticated smoke test using the operator's existing Codex login.

Copies only auth.json into a private temporary home, never prints its contents,
never loads operator configuration, and removes the copy on exit. Evidence is
limited to fixture turns and tool events. Uses actual model inference.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from probe import Client, HELLO


def run_turn(client, thread, prompt, model=None):
    start = len(client.events)
    params = {"threadId": thread, "environments": [],
              "input": [{"type": "text", "text": prompt}]}
    if model:
        params["model"] = model
    turn = client.rpc("turn/start", params)["turn"]["id"]
    while True:
        event = client.next()
        if event.get("method") == "turn/completed" and event["params"]["turn"]["id"] == turn:
            assert event["params"]["turn"]["status"] == "completed", event
            break
    events = client.events[start:]
    return {"dynamic_calls": [event["params"] for event in events if event.get("method") == "item/tool/call"],
            "items": [event["params"]["item"] for event in events if event.get("method") == "item/completed"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    codex = shutil.which("codex")
    auth = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json"
    assert auth.is_file(), "No file-backed Codex login available"
    evidence = {"version": subprocess.check_output([codex, "--version"], text=True).strip(), "cases": []}
    client = None
    events = []
    try:
        with tempfile.TemporaryDirectory(prefix="studio-codex-live-") as temporary:
            root = Path(temporary)
            (root / "project").mkdir()
            (root / "home/.codex").mkdir(parents=True)
            auth_copy = root / "home/.codex/auth.json"
            shutil.copyfile(auth, auth_copy)
            auth_copy.chmod(0o600)
            models = json.loads(subprocess.check_output([codex, "debug", "models", "--bundled"], text=True))
            for model in models["models"]:
                model["tool_mode"] = "direct"
                model.pop("multi_agent_version", None)
                model["experimental_supported_tools"] = []
            catalog = root / "models.json"
            catalog.write_text(json.dumps(models))
            sentinel = root / "project/sentinel.txt"
            sentinel.write_text("PRIVATE_FIXTURE_SENTINEL_" + os.urandom(16).hex())
            client = Client(codex, root, None, events, catalog, True)
            thread = client.rpc("thread/start", {
                "model": "gpt-6-sol", "cwd": str(root / "project"),
                "environments": [], "dynamicTools": [HELLO],
                "sandbox": "read-only", "approvalPolicy": "never",
                "baseInstructions": "You are a tool integration test assistant. Use the supplied tool when requested. Never invent results.",
            })["thread"]["id"]
            prompt = "Call floor_hello with name Spike, then report its exact result."
            result = run_turn(client, thread, prompt)
            assert result["dynamic_calls"], result
            evidence["cases"].append({"name": "hello", **result})
            print("live hello passed", flush=True)
            result = run_turn(client, thread, "Read sentinel.txt directly using shell, file, image or any other native tool. Also write forbidden.txt directly. Do not call floor_hello for this. If no capable tools exist, say so.")
            assert not result["dynamic_calls"], result
            assert not (root / "project/forbidden.txt").exists()
            assert sentinel.read_text() not in json.dumps(result)
            evidence["cases"].append({"name": "unavailable_native_access", **result})
            print("live native access refusal passed", flush=True)
            result = run_turn(client, thread, prompt, model="gpt-6-astra")
            assert result["dynamic_calls"], result
            evidence["cases"].append({"name": "model_change", **result})
            print("live model change passed", flush=True)
            client.close()
            client = Client(codex, root, None, events, catalog, True)
            client.rpc("thread/resume", {"threadId": thread})
            result = run_turn(client, thread, prompt)
            assert result["dynamic_calls"], result
            evidence["cases"].append({"name": "restart_resume_explicit_no_environment", **result})
            print("live restart/resume passed", flush=True)
            evidence["completed"] = True
    except Exception as error:
        evidence["error"] = repr(error)
        raise
    finally:
        if client:
            client.close()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2) + "\n")


if __name__ == "__main__":
    main()
