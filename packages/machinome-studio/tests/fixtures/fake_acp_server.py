"""Small process-local ACP server double for Hermes backend testing.

Speaks newline-delimited JSON-RPC over stdio, implementing the minimal
ACP surface needed by HermesBackend: ``session/new``, ``session/prompt``,
``session/cancel``.

The fixture uses the same streamed ``agent_message_chunk`` update shape as a
real Hermes ACP process so acceptance tests cover wire-compatible output.
"""

from __future__ import annotations

import json
import importlib.util
import os
import sys


def main() -> None:
    sessions: dict[str, dict] = {}
    next_session = 0
    capture_path = os.environ.get("FAKE_ACP_CAPTURE")

    def send(message: dict) -> None:
        print(json.dumps(message), flush=True)

    def capture(message: dict) -> None:
        if capture_path:
            with open(capture_path, "a", encoding="utf-8") as stream:
                stream.write(json.dumps(message) + "\n")

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
                    active_request = sessions[sid].pop("active_request", None)
                    if active_request is not None:
                        send(
                            {
                                "method": "session/update",
                                "params": {
                                    "sessionId": sid,
                                    "update": {
                                        "sessionUpdate": "agent_message_chunk",
                                        "content": {
                                            "type": "text",
                                            "text": "STALE",
                                        },
                                    },
                                },
                            }
                        )
                        send(
                            {
                                "id": active_request,
                                "result": {"stopReason": "cancelled"},
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
                        "protocolVersion": params.get("protocolVersion", 1),
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
            if sessions[sid]["active"]:
                send(
                    {
                        "method": "session/update",
                        "params": {
                            "sessionId": sid,
                            "update": {
                                "sessionUpdate": "agent_message_chunk",
                                "content": {
                                    "type": "text",
                                    "text": "Redirected the active turn with your correction.",
                                },
                            },
                        },
                    }
                )
                send({"id": request_id, "result": {"stopReason": "end_turn"}})
                continue
            sessions[sid]["active"] = True
            sessions[sid]["active_request"] = request_id
            if prompt_text == "HOLD":
                continue
            for text in ("FAKE", "_REPLY"):
                send(
                    {
                        "jsonrpc": "2.0",
                        "method": "session/update",
                        "params": {
                            "sessionId": sid,
                            "update": {
                                "content": {"text": text, "type": "text"},
                                "sessionUpdate": "agent_message_chunk",
                            },
                        },
                    }
                )
            sessions[sid].pop("active_request", None)
            sessions[sid]["active"] = False
            send({"id": request_id, "result": {"stopReason": "end_turn"}})

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
