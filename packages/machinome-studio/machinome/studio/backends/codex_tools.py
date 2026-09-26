# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Bounded per-handle floor worker; native Codex never owns tool processes."""
from __future__ import annotations

import asyncio
import base64
import json
import os
import subprocess
from pathlib import Path
import tempfile
from typing import Any

from ..mcp_server import mcp_command
from .base import RoleContext, session_tool_names, skill_registry
from .codex_wire import stop_process, CodexProtocolError
from .codex_qualification import _bounded_read


def git_identity(project: str) -> tuple[dict[str, str], bool]:
    """Resolve only ordinary identity/signing intent, never import Git config."""
    environment = {key: value for key, value in os.environ.items() if key in {"PATH", "HOME", "XDG_CONFIG_HOME", "GIT_CONFIG_GLOBAL"}}
    resolved = {}
    for key in ("user.name", "user.email", "commit.gpgsign"):
        invocation = ["git", "-C", project, "config"] + (["--bool"] if key == "commit.gpgsign" else []) + ["--get", key]
        response = subprocess.run(invocation, env=environment, capture_output=True, text=True, timeout=5)
        if response.returncode not in (0, 1):
            raise CodexProtocolError("Cannot resolve project Git identity/signing intent for the private floor worker")
        value = response.stdout.strip()
        if len(value) > 4096 or "\n" in value or "\r" in value:
            raise CodexProtocolError("Invalid resolved Git identity")
        resolved[key] = value
    identities = {}
    for kind in ("AUTHOR", "COMMITTER"):
        for suffix, key in (("NAME", "user.name"), ("EMAIL", "user.email")):
            name = f"GIT_{kind}_{suffix}"
            value = os.environ.get(name) or resolved[key]
            if value:
                if len(value) > 4096 or "\n" in value or "\r" in value:
                    raise CodexProtocolError("Invalid explicit Git identity")
                identities[name] = value
    return identities, resolved["commit.gpgsign"] == "true"


def validate_arguments(value: Any, schema: dict[str, Any]) -> None:
    """Validate the closed floor schema vocabulary, refusing unknown dialects."""
    supported = {"type", "description", "properties", "required", "additionalProperties", "items", "enum", "default", "title"}
    if set(schema) - supported:
        raise ValueError("Unsupported floor argument schema")
    types = {"object": lambda item: isinstance(item, dict), "array": lambda item: isinstance(item, list),
             "string": lambda item: isinstance(item, str), "integer": lambda item: type(item) is int,
             "number": lambda item: type(item) in (int, float), "boolean": lambda item: type(item) is bool,
             "null": lambda item: item is None}
    kind = schema.get("type")
    if kind not in types or not types[kind](value):
        raise ValueError("Floor tool argument has an invalid type")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError("Floor tool argument is not an allowed value")
    if kind == "object":
        properties = schema.get("properties", {})
        if set(schema.get("required", [])) - set(value):
            raise ValueError("Floor tool argument is missing a required field")
        if schema.get("additionalProperties") is not False:
            raise ValueError("Floor tool object schema must be closed")
        if set(value) - set(properties):
            raise ValueError("Floor tool argument has an undeclared field")
        for name, item in value.items():
            validate_arguments(item, properties[name])
    elif kind == "array":
        for item in value:
            validate_arguments(item, schema["items"])


def dynamic_result(result: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise CodexProtocolError("Floor worker returned an invalid result")
    items = result.get("content")
    if not isinstance(items, list) or not items or len(items) > 128:
        raise CodexProtocolError("Floor worker returned unsupported content")
    content = []
    size = 0
    for item in items:
        if not isinstance(item, dict):
            raise CodexProtocolError("Floor worker returned invalid content")
        if item.get("type") == "text" and isinstance(item.get("text"), str):
            content.append({"type": "inputText", "text": item["text"]})
        elif item.get("type") == "image" and item.get("mimeType") in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
            base64.b64decode(item["data"], validate=True)
            content.append({"type": "inputImage", "imageUrl": f"data:{item['mimeType']};base64,{item['data']}"})
        else:
            raise CodexProtocolError("Floor worker returned unsupported content")
        size += len(json.dumps(content[-1]).encode())
        if size > 6 * 1024 * 1024:
            raise CodexProtocolError("Floor worker result exceeds the bounded native result limit")
    return {"success": not result.get("isError", False), "contentItems": content}


class FloorWorker:
    def __init__(self, context: RoleContext, *, machinome_command: tuple[str, ...], broker_url: str, session_id: str):
        self.context = context
        self.command = mcp_command(Path(context.active_project), machinome_command, model=context.active_model,
            floor_url=broker_url, floor_session=session_id, skills=skill_registry(context.agent.skills))
        self.names = session_tool_names(context.agent.skills, context.agent.runtime.tools)
        self.command.extend(("--tools-json", json.dumps(self.names)))
        self.process: asyncio.subprocess.Process | None = None
        self.private: tempfile.TemporaryDirectory | None = None
        self.sequence = 0
        self.lock = asyncio.Lock()
        self.closing: asyncio.Task | None = None

    async def start(self) -> None:
        identities, signed = await _bounded_read(git_identity, self.context.active_project)
        if signed:
            self.command.append("--git-signing-required")
        self.private = tempfile.TemporaryDirectory(prefix="studio-floor-worker-")
        # Tool subprocesses need the installed command PATH, never auth homes,
        # provider keys or the authenticated owner's inherited lease descriptor.
        environment = {key: value for key, value in os.environ.items() if key in {"PATH", "LANG", "LC_ALL", "SSL_CERT_FILE", "SSL_CERT_DIR"}}
        environment.update(HOME=self.private.name, XDG_CONFIG_HOME=self.private.name, XDG_STATE_HOME=self.private.name,
                           CODEX_HOME=self.private.name)
        environment.update(identities)
        try:
            self.process = await asyncio.create_subprocess_exec(*self.command, cwd=self.context.shop_root, env=environment,
                stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
                start_new_session=True, limit=8 * 1024 * 1024)
            await self.rpc("initialize", {})
            listed = await self.rpc("tools/list", {})
            if {item["name"] for item in listed["tools"]} != set(self.names):
                raise CodexProtocolError("Floor worker registered a different role tool catalogue")
        except BaseException:
            await self.close()
            raise

    async def rpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        async with self.lock:
            if self.process is None or self.closing is not None or self.process.returncode is not None:
                raise CodexProtocolError("Floor worker is unavailable")
            self.sequence += 1
            identity = self.sequence
            assert self.process.stdin is not None and self.process.stdout is not None
            self.process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": identity, "method": method, "params": params}).encode() + b"\n")
            await self.process.stdin.drain()
            try:
                # Some allowed builds take minutes; close still kills their group.
                line = await asyncio.wait_for(self.process.stdout.readline(), 600)
                response = json.loads(line)
                if response.get("id") != identity or "error" in response or not isinstance(response.get("result"), dict):
                    raise ValueError
                return response["result"]
            except (ValueError, TimeoutError):
                raise CodexProtocolError("Floor worker response failed") from None

    async def _close(self) -> None:
        try:
            if self.process is not None:
                await stop_process(self.process)
        finally:
            if self.private is not None:
                self.private.cleanup()
                self.private = None

    async def close(self) -> None:
        if self.closing is None:
            self.closing = asyncio.create_task(self._close())
        await asyncio.shield(self.closing)
