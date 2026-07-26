"""Small process-local ACP server double for Hermes backend testing.

Speaks newline-delimited JSON-RPC over stdio, implementing the minimal
ACP surface needed by HermesBackend: ``session/new``, ``session/prompt``,
``session/cancel``.

Not yet exercised through the orchestrator — the HermesBackend is a
structural outline and does not launch a real process.  This fixture
exists so the first integration test lands on solid ground.
"""

from __future__ import annotations

import json
import sys


def main() -> None:
    sessions: dict[str, dict] = {}
    next_session = 0

    def send(message: dict) -> None:
        print(json.dumps(message), flush=True)

    for raw_line in sys.stdin:
        message = json.loads(raw_line)
        request_id = message.get("id")
        if request_id is None:
            continue
        method = message["method"]
        params = message.get("params", {})

        if method == "session/new":
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
            sessions[sid]["active"] = True
            # Simulate a completed prompt after a short delay (not applicable in stdio mode)
            send({"id": request_id, "result": {"stopReason": "end_turn"}})
            send(
                {
                    "method": "session/update",
                    "params": {
                        "sessionId": sid,
                        "update": {"agentMessage": {"text": ""}},
                    },
                }
            )

        elif method == "session/cancel":
            sid = params["sessionId"]
            if sid in sessions:
                sessions[sid]["active"] = False
            send({"id": request_id, "result": {}})

        elif method == "session/load":
            send(
                {
                    "id": request_id,
                    "result": {"models": [], "modes": []},
                }
            )

        else:
            send({"id": request_id, "error": {"code": -32601, "message": f"unknown method: {method}"}})


if __name__ == "__main__":
    main()
