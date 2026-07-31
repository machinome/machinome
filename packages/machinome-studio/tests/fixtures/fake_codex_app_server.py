#!/usr/bin/env python3
"""Small process-local app-server double for orchestration acceptance tests."""

from __future__ import annotations

import json
import sys


threads: dict[str, str | None] = {}
turns: dict[str, str] = {}
threads_with_rollouts: set[str] = set()
next_thread = 0
next_turn = 0


def send(message: dict[str, object]) -> None:
    print(json.dumps(message), flush=True)


for raw_line in sys.stdin:
    message = json.loads(raw_line)
    if "id" not in message:
        continue
    request_id = message["id"]
    method = message["method"]
    params = message.get("params", {})
    if method == "initialize":
        send({"id": request_id, "result": {"codexHome": "/tmp", "platformFamily": "unix", "platformOs": "linux"}})
    elif method == "thread/start":
        next_thread += 1
        thread_id = f"thread-{next_thread}"
        threads[thread_id] = None
        thread = {
            "id": thread_id,
            "status": {"type": "idle"},
            "turns": [],
            "cwd": params.get("cwd"),
            "developerInstructions": params.get("developerInstructions"),
            "approvalPolicy": params.get("approvalPolicy"),
            "sandbox": params.get("sandbox"),
            "runtimeWorkspaceRoots": params.get("runtimeWorkspaceRoots"),
            "config": params.get("config"),
        }
        send({"id": request_id, "result": {"thread": thread}})
        send({"method": "thread/started", "params": {"thread": thread}})
    elif method == "turn/start":
        thread_id = params["threadId"]
        if thread_id not in threads:
            send({"id": request_id, "error": {"code": -32600, "message": f"thread not found: {thread_id}"}})
            continue
        next_turn += 1
        turn_id = f"turn-{next_turn}"
        threads[thread_id] = turn_id
        threads_with_rollouts.add(thread_id)
        turns[turn_id] = thread_id
        turn = {"id": turn_id, "status": "inProgress", "items": []}
        send({"id": request_id, "result": {"turn": turn}})
        send({"method": "turn/started", "params": {"threadId": thread_id, "turn": turn}})
    elif method == "turn/steer":
        thread_id = params["threadId"]
        turn_id = params["expectedTurnId"]
        if threads.get(thread_id) != turn_id:
            send({"id": request_id, "error": {"code": -32600, "message": f"thread not found: {thread_id}"}})
        else:
            send({"id": request_id, "result": {"turnId": turn_id}})
    elif method == "turn/interrupt":
        thread_id = params["threadId"]
        turn_id = params["turnId"]
        if threads.get(thread_id) != turn_id:
            send(
                {
                    "id": request_id,
                    "error": {
                        "code": -32600,
                        "message": f"turn not active: {turn_id}",
                    },
                }
            )
        else:
            threads[thread_id] = None
            send({"id": request_id, "result": {}})
            send(
                {
                    "method": "turn/completed",
                    "params": {
                        "threadId": thread_id,
                        "turn": {"id": turn_id, "status": "interrupted", "items": []},
                    },
                }
            )
    elif method == "thread/archive":
        thread_id = params["threadId"]
        if thread_id not in threads_with_rollouts:
            send({"id": request_id, "error": {"code": -32600, "message": f"no rollout found for thread id {thread_id}"}})
        else:
            threads.pop(thread_id, None)
            send({"id": request_id, "result": {}})
    else:
        send({"id": request_id, "error": {"code": -32601, "message": f"unknown method: {method}"}})
