#!/usr/bin/env python3
"""Small process-local stand-in for `claude -p --input-format stream-json`.

Speaks the newline-delimited stream-json frames the Claude backend consumes:
a `system`/`init` frame, `assistant` frames carrying text and `tool_use`
blocks, `user` frames carrying `tool_result`, and exactly one `result` frame
per exchange.

The sequences here replay what a spike measured against a real `claude`
2.1.220 (see `openspec/changes/add-claude-agent-backend/spike/`), not what the
adapter would find convenient:

* Input arriving while a turn is outstanding is *queued* and injected at the
  next tool boundary, **inside** that turn. The exchange still answers with a
  single `result`. In 14 of 14 measured runs the correction never produced a
  second `result`, so a fixture that emitted one would hide the real contract.
* `control_request`/`interrupt` answers
  `{"subtype": "success", "response": {"still_queued": []}}`, then ends the
  turn with `is_error: true` and `terminal_reason: "aborted_tools"`. The
  session stays usable afterwards.

**What this fixture cannot prove.** It always acts on a delivered correction.
Whether a real model does is a separate, measured, *probabilistic* property
that no fixture can cover; see ADR 0009 and the spike table. A green suite
here says the correction was delivered into the running turn, never that an
agent obeyed it.

Prompt text drives the modes:

``HOLD``          open a turn, emit a `tool_use`, and leave it outstanding.
``SESSION_LIMIT`` end the turn with a recoverable provider-limit error.
anything else     an ordinary complete turn answering ``FAKE_REPLY``.

Environment:

``FAKE_CLAUDE_CAPTURE``        append a JSONL trace of argv, environment, and
                               every frame received.
``FAKE_CLAUDE_IGNORE_SIGNALS`` ignore SIGTERM/SIGINT and outlive stdin EOF, so
                               a close path must escalate to SIGKILL.
"""

from __future__ import annotations

import importlib.util
import json
import os
import signal
import sys
import time
import uuid

SESSION_ID = str(uuid.uuid4())

USAGE = {
    "input_tokens": 4,
    "output_tokens": 7,
    "cache_read_input_tokens": 14439,
    "cache_creation_input_tokens": 8821,
}


def main() -> None:
    capture_path = os.environ.get("FAKE_CLAUDE_CAPTURE")

    if os.environ.get("FAKE_CLAUDE_IGNORE_SIGNALS"):
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def send(message: dict) -> None:
        print(json.dumps(message), flush=True)

    def capture(message: dict) -> None:
        if capture_path:
            with open(capture_path, "a", encoding="utf-8") as stream:
                stream.write(json.dumps(message) + "\n")

    def assistant_text(text: str) -> None:
        send(
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "model": "claude-sonnet-5",
                    "content": [{"type": "text", "text": text}],
                },
                "session_id": SESSION_ID,
                "parent_tool_use_id": None,
            }
        )

    def assistant_tool_use(tool_id: str) -> None:
        send(
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "model": "claude-sonnet-5",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": tool_id,
                            "name": "Bash",
                            "input": {"command": "sleep 30"},
                        }
                    ],
                },
                "session_id": SESSION_ID,
                "parent_tool_use_id": None,
            }
        )

    def tool_result(tool_id: str) -> None:
        send(
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [
                        {
                            "tool_use_id": tool_id,
                            "type": "tool_result",
                            "content": "tick",
                            "is_error": False,
                        }
                    ],
                },
                "session_id": SESSION_ID,
                "parent_tool_use_id": None,
            }
        )

    def result(text: str | None, *, aborted: bool = False, failure: bool = False) -> None:
        """One result frame ends one exchange, however many inputs it carried."""
        send(
            {
                "type": "result",
                "subtype": "error_during_execution" if aborted or failure else "success",
                "is_error": bool(aborted or failure),
                "stop_reason": "tool_use" if aborted else "end_turn",
                "terminal_reason": "aborted_tools" if aborted else "error" if failure else "completed",
                "num_turns": 2,
                "result": text,
                "session_id": SESSION_ID,
                "duration_ms": 12,
                "total_cost_usd": 0.001,
                "usage": USAGE,
                "uuid": str(uuid.uuid4()),
            }
        )

    capture(
        {
            "kind": "environment",
            "argv": sys.argv[1:],
            "cwd": os.getcwd(),
            "pythonpath": os.environ.get("PYTHONPATH", ""),
            "floor_url": os.environ.get("FLOOR_URL", ""),
            "floor_session": os.environ.get("FLOOR_SESSION", ""),
            "floorImportable": importlib.util.find_spec("floor") is not None,
        }
    )

    mcp_server_names: list[str] = []
    tools = ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]
    if "--mcp-config" in sys.argv:
        config = json.loads(open(sys.argv[sys.argv.index("--mcp-config") + 1]).read())
        mcp_server_names = list(config.get("mcpServers", {}))
        tools = sys.argv[sys.argv.index("--tools") + 1].split(",")

    def init(mcp_status: str) -> None:
        send({
            "type": "system",
            "subtype": "init",
            "cwd": os.getcwd(),
            "session_id": SESSION_ID,
            "tools": tools,
            "model": "claude-sonnet-5",
            "permissionMode": "bypassPermissions",
            "mcp_servers": [
                {"name": name, "status": mcp_status}
                for name in mcp_server_names
            ],
        })

    pending_delay = float(os.environ.get("FAKE_CLAUDE_MCP_PENDING_DELAY", "0"))
    initialized = False

    # The turn currently outstanding, if any: its tool id and whether a
    # correction has been queued into it.
    held: dict | None = None

    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        message = json.loads(raw_line)
        capture({"kind": "message", "value": message})

        if message.get("type") == "control_request":
            request = message.get("request", {})
            send(
                {
                    "type": "control_response",
                    "response": {
                        "subtype": "success",
                        "request_id": message.get("request_id"),
                        "response": {"still_queued": []},
                    },
                }
            )
            if request.get("subtype") == "interrupt" and held is not None:
                # The turn dies; the session does not.
                result(None, aborted=True)
                held = None
            continue

        if message.get("type") != "user":
            continue

        if not initialized:
            if mcp_server_names and pending_delay:
                init("pending")
                time.sleep(pending_delay)
            init(os.environ.get("FAKE_CLAUDE_MCP_FINAL_STATUS", "connected"))
            initialized = True

        text = "".join(
            block.get("text", "")
            for block in message.get("message", {}).get("content", [])
            if isinstance(block, dict)
        )

        if held is not None:
            # Queued behind a running turn. A real CLI delivers this at the
            # next tool boundary and answers the whole exchange with one
            # result — so no result is emitted here.
            tool_result(held["tool_id"])
            assistant_text(f"CORRECTED:{text}")
            result("CORRECTED")
            held = None
            continue

        if text.strip() == "HOLD":
            tool_id = f"toolu_{uuid.uuid4().hex[:12]}"
            assistant_tool_use(tool_id)
            held = {"tool_id": tool_id}
            continue

        if "SESSION_LIMIT" in text:
            result("You've hit your session limit · resets 1pm (UTC)", failure=True)
            continue

        assistant_text("FAKE_REPLY")
        result("FAKE_REPLY")

    if os.environ.get("FAKE_CLAUDE_IGNORE_SIGNALS"):
        while True:
            time.sleep(3600)


if __name__ == "__main__":
    main()
