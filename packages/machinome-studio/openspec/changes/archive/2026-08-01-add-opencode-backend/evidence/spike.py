#!/usr/bin/env python3
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Record the OpenCode server contract required by this change.

This probe intentionally does not send a model prompt unless --exercise-prompt
is passed. It is safe to run before provider credentials or billing are chosen.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "<redacted>"
            if any(token in key.lower() for token in ("key", "secret", "token", "password"))
            else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


class Server:
    def __init__(self, project: Path, config: Path) -> None:
        self.port = _port()
        self.password = secrets.token_urlsafe(24)
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.request_log: list[dict[str, Any]] = []
        environment = {
            **os.environ,
            "OPENCODE_CONFIG": str(config),
            "OPENCODE_CONFIG_DIR": str(config.parent / "role-config"),
            "OPENCODE_SERVER_PASSWORD": self.password,
            # The adapter must inject root AGENTS.md itself rather than allow
            # native project discovery to activate project customization.
            "OPENCODE_DISABLE_PROJECT_CONFIG": "true",
        }
        self.process = subprocess.Popen(
            [
                "opencode",
                "serve",
                "--pure",
                "--hostname",
                "127.0.0.1",
                "--port",
                str(self.port),
                "--print-logs",
            ],
            cwd=project,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        payload = None if body is None else json.dumps(body).encode()
        auth = base64.b64encode(f"opencode:{self.password}".encode()).decode()
        request = Request(
            f"{self.base_url}{path}",
            data=payload,
            method=method,
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=2) as response:  # nosec: local probe server
                raw = response.read().decode()
                value = json.loads(raw) if raw else None
                self.request_log.append({"method": method, "path": path, "status": response.status, "body": _redact(value)})
                return value
        except HTTPError as error:
            raw = error.read().decode(errors="replace")
            self.request_log.append({"method": method, "path": path, "status": error.code, "body": raw})
            raise

    def wait_for_health(self) -> dict[str, Any]:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(f"OpenCode exited at startup: {self.stderr()}")
            try:
                value = self.request("GET", "/global/health")
                if value.get("healthy") is True:
                    return value
            except (HTTPError, URLError, TimeoutError):
                time.sleep(0.05)
        raise RuntimeError(f"OpenCode did not become healthy: {self.stderr()}")

    def stderr(self) -> str:
        if self.process.stderr is None:
            return ""
        return self.process.stderr.read().strip()

    def close(self) -> dict[str, Any]:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        return {"returncode": self.process.returncode, "stderr": self.stderr()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--exercise-prompt", action="store_true")
    arguments = parser.parse_args()

    temporary = Path(tempfile.mkdtemp(prefix="opencode-spike-"))
    try:
        project = temporary / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("ROOT_PROJECT_GUIDANCE: subordinate guidance only.\n")
        (project / "opencode.json").write_text(json.dumps({"agent": {"hostile": {"prompt": "must not load"}}}))
        (project / ".opencode").mkdir()
        (project / ".opencode" / "agents").mkdir()
        (project / ".opencode" / "agents" / "hostile.md").write_text("hostile project agent\n")
        config = temporary / "opencode.json"
        config.write_text(json.dumps({"plugin": [], "mcp": {}, "instructions": []}))
        (temporary / "role-config").mkdir()

        server = Server(project, config)
        try:
            health = server.wait_for_health()
            config_value = server.request("GET", "/config")
            agents = server.request("GET", "/agent")
            providers = server.request("GET", "/config/providers")
            session = server.request("POST", "/session", {"title": "shop spike"})
            if arguments.exercise_prompt:
                server.request(
                    "POST",
                    f"/session/{session['id']}/prompt_async",
                    {
                        "messageID": "spike-user-message",
                        "system": "PROFILE_CONTRACT\nPRECEDENCE_FRAMING\nROOT_PROJECT_GUIDANCE",
                        "parts": [{"type": "text", "text": "Reply exactly: spike."}],
                    },
                )
            result = {
                "opencode_version": health.get("version"),
                "command": server.process.args,
                "environment_controls": {
                    "OPENCODE_CONFIG": str(config),
                    "OPENCODE_CONFIG_DIR": str(temporary / "role-config"),
                    "OPENCODE_DISABLE_PROJECT_CONFIG": "true",
                    "pure": True,
                    "authenticated_loopback": True,
                },
                "health": health,
                "effective_config": _redact(config_value),
                "agents": [
                    {
                        "name": item.get("name"),
                        "mode": item.get("mode"),
                        "native": item.get("native"),
                    }
                    for item in agents
                ],
                "providers": {
                    "default": _redact(providers.get("default", {})),
                    "ids": [item.get("id") for item in providers.get("providers", [])],
                },
                "session": _redact(session),
                "requests": server.request_log,
            }
        finally:
            result["cleanup"] = server.close()
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


if __name__ == "__main__":
    main()
