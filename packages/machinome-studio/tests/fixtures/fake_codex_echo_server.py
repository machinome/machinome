#!/usr/bin/env python3
"""Codex app-server double that echoes turns and settles on request.

Unlike ``fake_codex_app_server.py`` (which leaves every turn under explicit
test control), this fixture drives a turn's whole visible lifecycle by
itself so a real browser can watch it happen through a live orchestrator:
every ``turn/start``/``turn/steer`` immediately echoes the delivered text
back as an agent message, and completes the turn only once the delivered
text contains the ``SETTLE_TURN`` marker. That lets one browser-submitted
direction, followed by a plain steer and then a settling steer, exercise a
real start/steer/complete sequence end to end.
"""

from __future__ import annotations

import json
import sys


SETTLE_MARKER = "SETTLE_TURN"

threads: dict[str, str | None] = {}
threads_with_rollouts: set[str] = set()
next_thread = 0
next_turn = 0


def send(message: dict[str, object]) -> None:
    print(json.dumps(message), flush=True)


def _text(params: dict[str, object]) -> str:
    entries = params.get("input", [])
    return "\n".join(str(entry.get("text", "")) for entry in entries if isinstance(entry, dict))


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
        thread = {"id": thread_id, "status": {"type": "idle"}, "turns": [], "cwd": params.get("cwd")}
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
        turn = {"id": turn_id, "status": "inProgress", "items": []}
        send({"id": request_id, "result": {"turn": turn}})
        send({"method": "turn/started", "params": {"threadId": thread_id, "turn": turn}})
        text = _text(params)
        send(
            {
                "method": "item/completed",
                "params": {"threadId": thread_id, "item": {"type": "agentMessage", "text": f"Echo: {text}"}},
            }
        )
        if SETTLE_MARKER in text:
            threads[thread_id] = None
            send(
                {
                    "method": "turn/completed",
                    "params": {"threadId": thread_id, "turn": {"id": turn_id, "status": "completed", "items": []}},
                }
            )
    elif method == "turn/steer":
        thread_id = params["threadId"]
        turn_id = params["expectedTurnId"]
        if threads.get(thread_id) != turn_id:
            send({"id": request_id, "error": {"code": -32600, "message": f"thread not found: {thread_id}"}})
            continue
        send({"id": request_id, "result": {"turnId": turn_id}})
        text = _text(params)
        send(
            {
                "method": "item/completed",
                "params": {"threadId": thread_id, "item": {"type": "agentMessage", "text": f"Echo: {text}"}},
            }
        )
        if SETTLE_MARKER in text:
            threads[thread_id] = None
            send(
                {
                    "method": "turn/completed",
                    "params": {"threadId": thread_id, "turn": {"id": turn_id, "status": "completed", "items": []}},
                }
            )
    elif method == "turn/interrupt":
        thread_id = params["threadId"]
        turn_id = params["turnId"]
        if threads.get(thread_id) != turn_id:
            send({"id": request_id, "error": {"code": -32600, "message": f"turn not active: {turn_id}"}})
        else:
            threads[thread_id] = None
            send({"id": request_id, "result": {}})
            send(
                {
                    "method": "turn/completed",
                    "params": {"threadId": thread_id, "turn": {"id": turn_id, "status": "interrupted", "items": []}},
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
