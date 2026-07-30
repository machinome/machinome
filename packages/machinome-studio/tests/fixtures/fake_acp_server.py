"""Small process-local ACP server double for Hermes backend testing.

Speaks newline-delimited JSON-RPC over stdio, implementing the minimal
ACP surface needed by HermesBackend: ``session/new``, ``session/prompt``,
``session/cancel``.

The frame sequences here replay what a spike measured against a real
``hermes`` 0.19.0 (see ``openspec/changes/harden-hermes-turn-control/spike/``),
not what the adapter would find convenient:

* A ``session/prompt`` on a session that already has one outstanding is
  Hermes' steer surface. It streams an acknowledgement chunk, then answers
  that request immediately with a bare ``{"stopReason": "end_turn"}`` and
  **no** ``usage``. The original prompt stays outstanding and its own
  response — carrying ``usage`` — is the real turn completion.
* ``session/cancel`` aborts the work but then fails the outstanding prompt
  with JSON-RPC ``-32603`` instead of reporting ``stopReason: "cancelled"``,
  and leaves the session unable to run anything afterwards.

Prompt text drives the modes:

``HOLD``            open a turn, stream ``PRE``, and leave it outstanding.
``...FINISH...``    (as a steer) apply the correction inside the held turn:
                    stream ``POST`` and complete the original prompt.
anything else       an ordinary complete turn streaming ``FAKE`` ``_REPLY``.

Environment:

``FAKE_ACP_CAPTURE``        append a JSONL trace of environment and messages.
``FAKE_ACP_IGNORE_SIGNALS`` ignore SIGTERM/SIGINT and outlive stdin EOF, so
                            a close path must escalate to SIGKILL.
"""

from __future__ import annotations

import json
import importlib.util
import os
import signal
import sys
import time

# The exact adapter crash observed on hermes 0.19.0 when a cancelled prompt
# is completed. Kept verbatim so a test cannot pass by matching our own text.
CANCEL_CRASH = "'NoneType' object has no attribute 'startswith'"

USAGE = {
    "cachedReadTokens": 43520,
    "inputTokens": 60192,
    "outputTokens": 289,
    "thoughtTokens": 152,
    "totalTokens": 60481,
}


def main() -> None:
    sessions: dict[str, dict] = {}
    next_session = 0
    capture_path = os.environ.get("FAKE_ACP_CAPTURE")

    if os.environ.get("FAKE_ACP_IGNORE_SIGNALS"):
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def send(message: dict) -> None:
        print(json.dumps(message), flush=True)

    def capture(message: dict) -> None:
        if capture_path:
            with open(capture_path, "a", encoding="utf-8") as stream:
                stream.write(json.dumps(message) + "\n")

    def chunk(sid: str, text: str) -> None:
        send(
            {
                "jsonrpc": "2.0",
                "method": "session/update",
                "params": {
                    "sessionId": sid,
                    "update": {
                        "sessionUpdate": "agent_message_chunk",
                        "content": {"type": "text", "text": text},
                    },
                },
            }
        )

    def complete(sid: str, request_id: int) -> None:
        """Finish the outstanding turn the way a real completion looks."""
        sessions[sid].pop("active_request", None)
        sessions[sid]["active"] = False
        send({"id": request_id, "result": {"stopReason": "end_turn", "usage": USAGE}})

    capture(
        {
            "kind": "environment",
            "pythonpath": os.environ.get("PYTHONPATH", ""),
            "floorImportable": importlib.util.find_spec("floor") is not None,
        }
    )

    for raw_line in sys.stdin:
        message = json.loads(raw_line)
        capture({"kind": "message", "value": message})
        request_id = message.get("id")
        method = message["method"]
        params = message.get("params", {})

        if request_id is None:
            if method == "session/cancel":
                sid = params["sessionId"]
                if sid in sessions:
                    sessions[sid]["active"] = False
                    # A cancelled session is wedged from here on.
                    sessions[sid]["wedged"] = True
                    active_request = sessions[sid].pop("active_request", None)
                    if active_request is not None:
                        # hermes 0.19.0 fails the pending prompt rather than
                        # answering it with stopReason "cancelled".
                        send(
                            {
                                "id": active_request,
                                "error": {
                                    "code": -32603,
                                    "message": "Internal error",
                                    "data": {"details": CANCEL_CRASH},
                                },
                            }
                        )
            continue

        if method == "initialize":
            send(
                {
                    "id": request_id,
                    "result": {
                        "agentCapabilities": {
                            "prompt": {"text": True},
                            "mcp": False,
                        },
                        "authMethods": [],
                        # Real Hermes answers 1 even when offered 2.
                        "protocolVersion": 1,
                    },
                }
            )

        elif method == "session/new":
            if "mcpServers" not in params:
                send(
                    {
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "mcpServers is required",
                        },
                    }
                )
                continue
            next_session += 1
            sid = f"session-{next_session}"
            sessions[sid] = {"cwd": params.get("cwd", ""), "active": False}
            send(
                {
                    "id": request_id,
                    "result": {"sessionId": sid, "models": [], "modes": []},
                }
            )

        elif method == "session/prompt":
            sid = params["sessionId"]
            if sid not in sessions:
                send({"id": request_id, "error": {"code": -32600, "message": f"session not found: {sid}"}})
                continue
            prompt_text = "".join(
                block.get("text", "") for block in params.get("prompt", [])
            )

            if sessions[sid].get("wedged"):
                # Queued behind a turn that will never run again.
                chunk(sid, "Queued for the next turn. (1 queued)")
                continue

            if sessions[sid]["active"]:
                # Steer surface: acknowledge, then answer instantly with a
                # bare stop reason and no usage. The original stays open.
                held = sessions[sid].get("active_request")
                chunk(sid, "Redirected the active turn with your correction.")
                send({"id": request_id, "result": {"stopReason": "end_turn"}})
                if "FINISH" in prompt_text and held is not None:
                    # The correction runs inside the turn already in flight.
                    chunk(sid, "POST")
                    complete(sid, held)
                continue

            sessions[sid]["active"] = True
            sessions[sid]["active_request"] = request_id
            if prompt_text == "HOLD":
                chunk(sid, "PRE")
                continue
            delay = float(os.environ.get("FAKE_ACP_PROMPT_DELAY", "0"))
            if delay:
                # Model work that outlasts any control-plane budget.
                time.sleep(delay)
            for text in ("FAKE", "_REPLY"):
                chunk(sid, text)
            complete(sid, request_id)

        elif method == "session/load":
            send(
                {
                    "id": request_id,
                    "result": {"models": [], "modes": []},
                }
            )

        else:
            send({"id": request_id, "error": {"code": -32601, "message": f"unknown method: {method}"}})

    if os.environ.get("FAKE_ACP_IGNORE_SIGNALS"):
        # Outlive stdin EOF so only SIGKILL can end this process.
        while True:
            time.sleep(3600)


if __name__ == "__main__":
    main()
