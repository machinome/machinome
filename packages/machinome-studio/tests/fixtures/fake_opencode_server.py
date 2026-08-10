#!/usr/bin/env python3
"""Small authenticated OpenCode HTTP/SSE fixture used by backend tests."""

from __future__ import annotations

import base64
import json
import os
import signal
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from queue import Queue
from typing import Any
from urllib.parse import parse_qs, urlparse


CAPTURE = Path(os.environ["FAKE_OPENCODE_CAPTURE"])
PASSWORD = os.environ["OPENCODE_SERVER_PASSWORD"]
SESSIONS: dict[str, list[dict[str, Any]]] = {}
STREAMS: list[Queue[dict[str, Any] | None]] = []
LOCK = threading.Lock()


def capture(kind: str, **value: Any) -> None:
    with LOCK:
        with CAPTURE.open("a") as output:
            output.write(json.dumps({"kind": kind, **value}) + "\n")


def publish(event: dict[str, Any], *, wrapped: bool = False) -> None:
    value = {"payload": event} if wrapped else event
    with LOCK:
        streams = tuple(STREAMS)
    for stream in streams:
        stream.put(value)


def assistant(session_id: str, parent_id: str, text: str, *, suffix: str = "") -> None:
    message_id = f"assistant-{parent_id}{suffix}"
    part = {
        "id": f"part-{parent_id}{suffix}",
        "sessionID": session_id,
        "messageID": message_id,
        "type": "text",
        "text": text,
    }
    SESSIONS[session_id].append(
        {
            "info": {
                "id": message_id,
                "sessionID": session_id,
                "role": "assistant",
                "parentID": parent_id,
            },
            "parts": [part],
        }
    )
    publish(
        {"type": "message.part.updated", "properties": {"part": part, "delta": text}},
        wrapped=True,
    )
    publish({"type": "message.part.updated", "properties": {"part": part}})


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, _format: str, *_args: Any) -> None:
        pass

    def authorized(self) -> bool:
        expected = base64.b64encode(f"opencode:{PASSWORD}".encode()).decode()
        if self.headers.get("Authorization") == f"Basic {expected}":
            return True
        self.send_response(401)
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length)) if length else {}

    def reply(self, value: Any, status: int = 200) -> None:
        raw = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if not self.authorized():
            return
        parsed = urlparse(self.path)
        path = parsed.path
        capture("request", method="GET", path=path, rawPath=self.path, directory=parse_qs(parsed.query).get("directory", [None])[0])
        if path == "/global/health":
            self.reply({"healthy": True, "version": "fake"})
            return
        if path == "/global/event":
            stream: Queue[dict[str, Any] | None] = Queue()
            with LOCK:
                STREAMS.append(stream)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(b": ready\n\n")
            self.wfile.flush()
            try:
                while True:
                    item = stream.get()
                    if item is None:
                        return
                    envelope = item if "payload" in item else {
                        "directory": "/fake/role-directory",
                        "payload": item,
                    }
                    self.wfile.write(f"data: {json.dumps(envelope)}\n\n".encode())
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                with LOCK:
                    if stream in STREAMS:
                        STREAMS.remove(stream)
            return
        prefix = "/session/"
        suffix = "/message"
        if path.startswith(prefix) and path.endswith(suffix):
            session_id = path[len(prefix) : -len(suffix)]
            self.reply(SESSIONS.get(session_id, []))
            return
        self.reply({"error": "not found"}, 404)

    def do_POST(self) -> None:  # noqa: N802
        if not self.authorized():
            return
        parsed = urlparse(self.path)
        path = parsed.path
        body = self.body()
        capture("request", method="POST", path=path, rawPath=self.path, directory=parse_qs(parsed.query).get("directory", [None])[0], body=body)
        if path == "/session":
            session_id = f"session-{len(SESSIONS) + 1}"
            SESSIONS[session_id] = []
            self.reply({"id": session_id})
            return
        if path == "/instance/dispose":
            self.reply(True)
            return
        if path.endswith("/prompt_async"):
            session_id = path.split("/")[2]
            message_id = body["messageID"]
            if not message_id.startswith("msg_") or len(message_id) != 30:
                self.reply({"error": "invalid native messageID"}, 400)
                return
            existing = next(
                (item for item in SESSIONS[session_id] if item["info"]["id"] == message_id),
                None,
            )
            text = body["parts"][0]["text"] if body["parts"] else ""
            if existing is None:
                SESSIONS[session_id].append(
                    {"info": {"id": message_id, "sessionID": session_id, "role": "user"}, "parts": body["parts"]}
                )
            self.reply(True)
            if text == "ERROR":
                publish(
                    {
                        "type": "session.error",
                        "properties": {
                            "sessionID": session_id,
                            "error": {"name": "ProviderError", "message": "fake failure"},
                        },
                    }
                )
                return
            if text == "HOLD" and existing is None:
                return
            if text == "PARTS" and existing is None:
                assistant(session_id, message_id, "FIRST_PART", suffix="-first")
                time.sleep(0.25)
                assistant(session_id, message_id, "SECOND_PART", suffix="-second")
                time.sleep(0.25)
                publish({
                    "type": "session.status",
                    "properties": {
                        "sessionID": session_id,
                        "status": {"type": "idle"},
                    },
                })
                return
            if existing is not None:
                assistant(session_id, message_id, "after")
                publish({"type": "session.idle", "properties": {"sessionID": session_id}}, wrapped=True)
                return
            users = [item["info"]["id"] for item in SESSIONS[session_id] if item["info"]["role"] == "user"]
            descendants = {
                item["info"].get("parentID")
                for item in SESSIONS[session_id]
                if item["info"]["role"] == "assistant"
            }
            missing = [item for item in users if item not in descendants]
            if len(missing) > 1:
                assistant(session_id, missing[0], "before")
                publish({"type": "session.idle", "properties": {"sessionID": session_id}})
            else:
                publish({
                    "directory": "/unrelated/location",
                    "payload": {
                        "type": "session.status",
                        "properties": {
                            "sessionID": "unrelated-session",
                            "status": {"type": "idle"},
                        },
                    },
                })
                assistant(session_id, message_id, "FAKE_REPLY")
                publish({
                    "type": "session.status",
                    "properties": {
                        "sessionID": session_id,
                        "status": {"type": "idle"},
                    },
                })
            return
        if path.endswith("/abort"):
            session_id = path.split("/")[2]
            self.reply(True)
            publish(
                {
                    "type": "session.error",
                    "properties": {
                        "sessionID": session_id,
                        "error": {"name": "AbortError", "message": "aborted"},
                    },
                }
            )
            return
        self.reply({"error": "not found"}, 404)

    def do_DELETE(self) -> None:  # noqa: N802
        if not self.authorized():
            return
        parsed = urlparse(self.path)
        path = parsed.path
        capture("request", method="DELETE", path=path, rawPath=self.path, directory=parse_qs(parsed.query).get("directory", [None])[0])
        SESSIONS.pop(path.rsplit("/", 1)[-1], None)
        self.reply(True)


def main() -> None:
    argv = sys.argv[1:]
    port = int(argv[argv.index("--port") + 1])
    config = Path(os.environ["OPENCODE_CONFIG"])
    config_dir = Path(os.environ["OPENCODE_CONFIG_DIR"])
    capture(
        "startup",
        argv=argv,
        cwd=os.getcwd(),
        disableProjectConfig=os.environ.get("OPENCODE_DISABLE_PROJECT_CONFIG"),
        password=bool(PASSWORD),
        config=json.loads(config.read_text()),
        configDir=str(config_dir),
        configDirEntries=sorted(item.name for item in config_dir.iterdir()),
        pythonPath=os.environ.get("PYTHONPATH", ""),
    )
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)

    def stop(_signum: int, _frame: Any) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    server.serve_forever()
    with LOCK:
        streams = tuple(STREAMS)
    for stream in streams:
        stream.put(None)
    server.server_close()


if __name__ == "__main__":
    main()
