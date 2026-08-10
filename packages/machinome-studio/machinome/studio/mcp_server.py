"""Project-scoped MCP tools exposed to runtime agents over stdio.

The server deliberately implements the small MCP JSON-RPC surface it needs
instead of importing the Python MCP SDK.  The workspace venv also carries the
solid-node CLI, whose pinned Uvicorn version conflicts with the SDK's runtime
dependency.  Keeping this server stdio-only avoids changing that environment.
"""

from __future__ import annotations

import argparse
import base64
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from .agent import FloorClient
from .screenshots import is_safe_screenshot, refresh_project_screenshot


SERVER_NAME = "floor"
PROTOCOL_VERSION = "2025-06-18"

FILESYSTEM_READ_TOOLS = (
    "list_dir", "find_files", "search_content", "read_file", "stat",
)
FILESYSTEM_WRITE_TOOLS = (
    "write_file", "edit_file", "apply_patch", "delete_file", "move_file", "make_dir",
)
GIT_TOOLS = (
    "git_status", "git_diff", "git_log", "git_show", "git_rev_parse_toplevel",
    "git_merge_base_is_ancestor", "git_head", "git_add", "git_commit",
)
SOLID_TOOLS = ("solid_build", "solid_test", "solid_snapshot")
FLOOR_TOOLS = (
    "floor_assign", "floor_direction", "floor_acknowledge", "floor_report",
    "floor_complete",
)
TOOL_NAMES = (
    FILESYSTEM_READ_TOOLS + FILESYSTEM_WRITE_TOOLS + GIT_TOOLS + SOLID_TOOLS
    + FLOOR_TOOLS
)

# Existing profile declarations remain the profile-facing policy.  Their
# native capabilities resolve to the narrower floor operations below.
PROFILE_TOOL_MAP: dict[str, tuple[str, ...]] = {
    "Read": ("read_file", "stat"),
    "Glob": ("list_dir", "find_files"),
    "Grep": ("search_content",),
    "Write": ("write_file", "delete_file", "move_file", "make_dir"),
    "Edit": ("edit_file", "apply_patch"),
    "Bash": GIT_TOOLS + SOLID_TOOLS + FLOOR_TOOLS,
    # The ratified change intentionally supplies no replacement web surface.
    "WebSearch": (),
    "WebFetch": (),
}

NATIVE_OPENCODE_TOOLS = (
    "read", "write", "edit", "bash", "glob", "grep", "list", "webfetch",
    "websearch", "task", "todowrite", "todoread", "patch", "question", "skill",
)

RASTER_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


@dataclass(frozen=True)
class ImagePayload:
    """Binary image result converted to MCP image content at the transport."""

    data: bytes
    mime_type: str

    @property
    def _mime_type(self) -> str:  # compatibility with the SDK Image shape
        return self.mime_type


def resolved_tool_names(profile_tools: str | tuple[str, ...]) -> tuple[str, ...]:
    """Resolve trusted profile capabilities to stable floor tool names."""
    if profile_tools == "inherit":
        return ()
    resolved: list[str] = []
    for capability in profile_tools:
        for name in PROFILE_TOOL_MAP.get(capability, ()):
            if name not in resolved:
                resolved.append(name)
    return tuple(resolved)


def mcp_command(
    project: Path,
    solid_command: tuple[str, ...],
    *,
    python: str | None = None,
    floor_url: str | None = None,
    floor_session: str | None = None,
) -> list[str]:
    """Build the portable local-server command used by both backends."""
    command = [
        python or sys.executable,
        "-m",
        "floor.mcp_server",
        "--project",
        str(project.resolve()),
        "--solid-command-json",
        json.dumps(solid_command),
    ]
    if floor_url is not None:
        command.extend(("--floor-url", floor_url))
    if floor_session is not None:
        command.extend(("--floor-session", floor_session))
    return command


class ProjectTools:
    """All tool actions, with one shared active-project containment gate."""

    def __init__(
        self,
        project: Path,
        *,
        solid_command: tuple[str, ...] = ("solid",),
        floor_url: str | None = None,
        floor_session: str | None = None,
    ) -> None:
        self.root = project.resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError(f"active project is not a directory: {self.root}")
        self.solid_command = tuple(solid_command)
        if not self.solid_command:
            raise ValueError("solid command must not be empty")
        self.floor = (
            FloorClient(floor_url, floor_session)
            if floor_url is not None and floor_session is not None
            else None
        )

    def _floor(self) -> FloorClient:
        if self.floor is None:
            raise RuntimeError("active floor session is unavailable")
        return self.floor

    # -- containment -------------------------------------------------

    def _path(self, value: str, *, must_exist: bool = False) -> Path:
        if not isinstance(value, str) or not value or "\x00" in value:
            raise ValueError("path must be a non-empty string")
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = self.root / candidate
        try:
            resolved = candidate.resolve(strict=must_exist)
        except OSError as error:
            raise ValueError(f"invalid project path {value!r}: {error}") from error
        if resolved != self.root and self.root not in resolved.parents:
            raise ValueError(f"path resolves outside active project: {value!r}")
        return resolved

    def _relative(self, value: str, *, must_exist: bool = False) -> str:
        return self._path(value, must_exist=must_exist).relative_to(self.root).as_posix() or "."

    def _reference(self, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str) or not value or "\x00" in value:
            raise ValueError("reference must be a non-empty string")
        source, separator, target = value.partition(":")
        looks_like_path = (
            Path(source).is_absolute()
            or "/" in source
            or "\\" in source
            or source.startswith(".")
            or source.endswith(".py")
        )
        if not looks_like_path:
            if value.startswith("-"):
                raise ValueError("reference must not start with '-'")
            return value
        relative = self._relative(source)
        return f"{relative}{separator}{target}" if separator else relative

    @staticmethod
    def _revision(value: str) -> str:
        if not isinstance(value, str) or not value or value.startswith("-") or "\x00" in value:
            raise ValueError("git revision must be a non-empty non-option string")
        return value

    # -- subprocesses ------------------------------------------------

    def _run(self, command: list[str]) -> dict[str, Any]:
        completed = subprocess.run(
            command,
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )
        return {
            "ok": completed.returncode == 0,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def _git(self, *args: str) -> dict[str, Any]:
        return self._run(["git", *args])

    def _visible_files(self, path: str = ".") -> list[str]:
        relative = self._relative(path, must_exist=True)
        target = self._path(path, must_exist=True)
        if target.is_file():
            return [relative]
        result = self._git("ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", relative)
        if not result["ok"]:
            raise RuntimeError(result["stderr"] or result["stdout"] or "git ls-files failed")
        return sorted(item for item in result["stdout"].split("\x00") if item)

    # -- filesystem reads -------------------------------------------

    def list_dir(self, path: str = ".", recursive: bool = False) -> list[str]:
        target = self._path(path, must_exist=True)
        if not target.is_dir():
            raise ValueError(f"not a directory: {path!r}")
        relative = target.relative_to(self.root)
        files = self._visible_files(path)
        values: set[str] = set()
        prefix_count = len(relative.parts)
        for item in files:
            parts = Path(item).parts[prefix_count:]
            if not parts:
                continue
            if recursive:
                values.add(PurePosixPath(*parts).as_posix())
            else:
                values.add(parts[0] + ("/" if len(parts) > 1 else ""))
        return sorted(values)

    def find_files(self, pattern: str) -> list[str]:
        if not isinstance(pattern, str) or not pattern or "\x00" in pattern:
            raise ValueError("pattern must be a non-empty string")
        return [
            path for path in self._visible_files()
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(Path(path).name, pattern)
        ]

    def search_content(
        self,
        pattern: str,
        path: str = ".",
        regex: bool = False,
    ) -> list[str]:
        if not isinstance(pattern, str) or not pattern:
            raise ValueError("pattern must be a non-empty string")
        matcher = re.compile(pattern) if regex else None
        matches: list[str] = []
        for relative in self._visible_files(path):
            candidate = self._path(relative, must_exist=True)
            try:
                lines = candidate.read_text().splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for line_number, line in enumerate(lines, 1):
                if (matcher.search(line) if matcher else pattern in line):
                    matches.append(f"{relative}:{line_number}:{line}")
        return matches

    def read_file(
        self,
        path: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> str | ImagePayload:
        target = self._path(path, must_exist=True)
        if not target.is_file():
            raise ValueError(f"not a file: {path!r}")
        mime = RASTER_MIME_TYPES.get(target.suffix.lower())
        if mime is not None:
            if offset is not None or limit is not None:
                raise ValueError("offset and limit are not valid for raster images")
            return ImagePayload(target.read_bytes(), mime)
        if offset is not None and offset < 1:
            raise ValueError("offset must be at least 1")
        if limit is not None and limit < 0:
            raise ValueError("limit must be non-negative")
        lines = target.read_text().splitlines(keepends=True)
        start = 0 if offset is None else offset - 1
        stop = None if limit is None else start + limit
        return "".join(lines[start:stop])

    def stat(self, path: str) -> dict[str, Any]:
        raw = Path(path)
        candidate = raw if raw.is_absolute() else self.root / raw
        target = self._path(path, must_exist=False)
        exists = target.exists()
        result: dict[str, Any] = {
            "exists": exists,
            "is_symlink": candidate.is_symlink(),
            "is_dir": exists and target.is_dir(),
            "size": None,
            "mtime": None,
        }
        if exists:
            value = target.stat()
            result["size"] = value.st_size
            result["mtime"] = datetime.fromtimestamp(value.st_mtime, timezone.utc).isoformat()
        return result

    # -- filesystem writes ------------------------------------------

    def write_file(self, path: str, content: str, must_not_exist: bool = False) -> dict[str, Any]:
        target = self._path(path)
        if target.exists() and target.is_dir():
            raise ValueError(f"target is a directory: {path!r}")
        if must_not_exist and target.exists():
            raise FileExistsError(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return {"path": target.relative_to(self.root).as_posix(), "bytes": len(content.encode())}

    def edit_file(
        self,
        path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> dict[str, Any]:
        target = self._path(path, must_exist=True)
        content = target.read_text()
        count = content.count(old_string)
        if count == 0:
            raise ValueError("old_string was not found")
        if not replace_all and count != 1:
            raise ValueError(f"old_string matched {count} times; use replace_all")
        target.write_text(content.replace(old_string, new_string, -1 if replace_all else 1))
        return {"path": target.relative_to(self.root).as_posix(), "replacements": count if replace_all else 1}

    def apply_patch(self, path: str, unified_diff: str) -> dict[str, Any]:
        target = self._path(path, must_exist=True)
        original = target.read_text().splitlines(keepends=True)
        lines = unified_diff.splitlines(keepends=True)
        headers = [index for index, line in enumerate(lines) if line.startswith("--- ")]
        if len(headers) != 1 or headers[0] + 1 >= len(lines) or not lines[headers[0] + 1].startswith("+++ "):
            raise ValueError("patch must contain exactly one unified-diff file header")
        output: list[str] = []
        cursor = 0
        index = headers[0] + 2
        hunk_pattern = re.compile(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
        while index < len(lines):
            match = hunk_pattern.match(lines[index].rstrip("\n"))
            if match is None:
                raise ValueError(f"invalid unified-diff hunk header: {lines[index].rstrip()!r}")
            old_start = int(match.group(1))
            output.extend(original[cursor : old_start - 1])
            cursor = old_start - 1
            index += 1
            while index < len(lines) and not lines[index].startswith("@@ "):
                line = lines[index]
                if line.startswith("\\ No newline at end of file"):
                    index += 1
                    continue
                if not line or line[0] not in " +-":
                    raise ValueError(f"invalid unified-diff line: {line.rstrip()!r}")
                marker, value = line[0], line[1:]
                if marker in " -":
                    if cursor >= len(original) or original[cursor] != value:
                        raise ValueError("patch context does not match target file")
                    cursor += 1
                if marker in " +":
                    output.append(value)
                index += 1
        output.extend(original[cursor:])
        target.write_text("".join(output))
        return {"path": target.relative_to(self.root).as_posix(), "applied": True}

    def delete_file(self, path: str) -> dict[str, Any]:
        target = self._path(path, must_exist=True)
        if not target.is_file():
            raise ValueError(f"not a file: {path!r}")
        target.unlink()
        return {"path": target.relative_to(self.root).as_posix(), "deleted": True}

    def move_file(self, src: str, dst: str) -> dict[str, Any]:
        source = self._path(src, must_exist=True)
        destination = self._path(dst)
        if destination.exists():
            raise FileExistsError(dst)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        return {
            "src": source.relative_to(self.root).as_posix(),
            "dst": destination.relative_to(self.root).as_posix(),
        }

    def make_dir(self, path: str) -> dict[str, Any]:
        target = self._path(path)
        target.mkdir(parents=True, exist_ok=True)
        return {"path": target.relative_to(self.root).as_posix(), "created": True}

    # -- git ---------------------------------------------------------

    def git_status(self) -> dict[str, Any]:
        return self._git("status", "--short", "--branch")

    def git_diff(self, path: str | None = None, staged: bool = False) -> dict[str, Any]:
        args = ["diff"]
        if staged:
            args.append("--cached")
        if path is not None:
            args.extend(("--", self._relative(path)))
        return self._git(*args)

    def git_log(self, path: str | None = None, limit: int = 20) -> dict[str, Any]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        args = ["log", f"-{limit}", "--oneline", "--decorate"]
        if path is not None:
            args.extend(("--", self._relative(path)))
        return self._git(*args)

    def git_show(self, revision: str, path: str) -> dict[str, Any]:
        relative = self._relative(path)
        return self._git("show", f"{self._revision(revision)}:{relative}")

    def git_rev_parse_toplevel(self) -> str:
        result = self._git("rev-parse", "--show-toplevel")
        if not result["ok"]:
            raise RuntimeError(result["stderr"] or "git rev-parse failed")
        toplevel = Path(result["stdout"].strip()).resolve()
        if toplevel != self.root:
            raise RuntimeError(f"active project is not its repository root: {toplevel}")
        return str(toplevel)

    def git_merge_base_is_ancestor(self, commit: str, ref: str = "HEAD") -> dict[str, Any]:
        result = self._git(
            "merge-base", "--is-ancestor", self._revision(commit), self._revision(ref)
        )
        result["is_ancestor"] = result["exit_code"] == 0
        return result

    def git_head(self) -> dict[str, Any]:
        sha = self._git("rev-parse", "HEAD")
        branch = self._git("symbolic-ref", "--quiet", "--short", "HEAD")
        if not sha["ok"]:
            raise RuntimeError(sha["stderr"] or "git rev-parse HEAD failed")
        return {
            "sha": sha["stdout"].strip(),
            "branch": branch["stdout"].strip() if branch["ok"] else None,
        }

    def git_add(self, paths: list[str]) -> dict[str, Any]:
        if not paths:
            raise ValueError("paths must not be empty")
        return self._git("add", "--", *(self._relative(path) for path in paths))

    def git_commit(self, message: str) -> dict[str, Any]:
        if not isinstance(message, str) or not message:
            raise ValueError("message must be a non-empty string")
        screenshot = refresh_project_screenshot(self.root, self.solid_command)
        warning = screenshot.warning
        if is_safe_screenshot(self.root):
            staged = self._git("add", "--", "screenshot.png")
            if not staged["ok"]:
                warning = staged["stderr"] or "could not stage screenshot.png"
        result = self._git("commit", "-m", message)
        if warning:
            result["screenshot_warning"] = warning
        return result

    # -- solid-node --------------------------------------------------

    def solid_build(self, path: str | None = None) -> dict[str, Any]:
        reference = self._reference(path)
        result = self._run([*self.solid_command, "build", *([reference] if reference else [])])
        if result["ok"]:
            screenshot = refresh_project_screenshot(self.root, self.solid_command)
            if screenshot.warning:
                result["screenshot_warning"] = screenshot.warning
        return result

    def solid_test(self, path: str | None = None, failfast: bool = False) -> dict[str, Any]:
        reference = self._reference(path)
        command = [*self.solid_command, "test"]
        if failfast:
            command.append("--failfast")
        if reference:
            command.append(reference)
        return self._run(command)

    def solid_snapshot(
        self,
        path: str | None = None,
        time: float | None = None,
        camera: str | None = None,
        imgsize: str | None = None,
        projection: str | None = None,
        colorscheme: str | None = None,
        view: str | None = None,
        autocenter: bool = False,
        viewall: bool = False,
    ) -> ImagePayload:
        reference = self._reference(path)
        with tempfile.TemporaryDirectory(prefix="solid-node-studio-snapshot-") as temporary:
            output = Path(temporary) / "snapshot.png"
            command = [*self.solid_command, "snapshot"]
            if reference:
                command.append(reference)
            command.extend(("-o", str(output)))
            for option, value in (
                ("--time", time), ("--camera", camera), ("--imgsize", imgsize),
                ("--projection", projection), ("--colorscheme", colorscheme), ("--view", view),
            ):
                if value is not None:
                    command.extend((option, str(value)))
            if autocenter:
                command.append("--autocenter")
            if viewall:
                command.append("--viewall")
            result = self._run(command)
            if not result["ok"]:
                raise RuntimeError(
                    f"solid snapshot failed ({result['exit_code']}): "
                    f"{result['stderr'] or result['stdout']}"
                )
            if not output.is_file():
                raise RuntimeError("solid snapshot succeeded without producing an image")
            return ImagePayload(output.read_bytes(), "image/png")

    # -- bounded shop broker lifecycle ------------------------------

    def floor_assign(
        self,
        sender: str,
        recipient: str,
        assignment: str,
        text: str,
    ) -> dict[str, Any]:
        return self._floor().assign(sender, recipient, assignment, text)

    def floor_direction(
        self,
        sender: str,
        recipient: str,
        text: str,
    ) -> dict[str, Any]:
        return self._floor().direction(sender, recipient, text)

    def floor_acknowledge(self, role: str, assignment: str) -> dict[str, Any]:
        return self._floor().acknowledge(role, assignment)

    def floor_report(
        self,
        sender: str,
        recipient: str,
        text: str,
        assignment: str = "",
    ) -> dict[str, Any]:
        return self._floor().report(sender, recipient, text, assignment)

    def floor_complete(self, role: str, assignment: str) -> dict[str, Any]:
        return self._floor().complete(role, assignment)


def _schema(properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties or {},
        "required": required or [],
        "additionalProperties": False,
    }


STR = {"type": "string"}
BOOL = {"type": "boolean"}
INT = {"type": "integer"}
NUMBER = {"type": "number"}
TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "list_dir": _schema({"path": STR, "recursive": BOOL}),
    "find_files": _schema({"pattern": STR}, ["pattern"]),
    "search_content": _schema({"pattern": STR, "path": STR, "regex": BOOL}, ["pattern"]),
    "read_file": _schema({"path": STR, "offset": INT, "limit": INT}, ["path"]),
    "stat": _schema({"path": STR}, ["path"]),
    "write_file": _schema({"path": STR, "content": STR, "must_not_exist": BOOL}, ["path", "content"]),
    "edit_file": _schema({"path": STR, "old_string": STR, "new_string": STR, "replace_all": BOOL}, ["path", "old_string", "new_string"]),
    "apply_patch": _schema({"path": STR, "unified_diff": STR}, ["path", "unified_diff"]),
    "delete_file": _schema({"path": STR}, ["path"]),
    "move_file": _schema({"src": STR, "dst": STR}, ["src", "dst"]),
    "make_dir": _schema({"path": STR}, ["path"]),
    "git_status": _schema(),
    "git_diff": _schema({"path": STR, "staged": BOOL}),
    "git_log": _schema({"path": STR, "limit": INT}),
    "git_show": _schema({"revision": STR, "path": STR}, ["revision", "path"]),
    "git_rev_parse_toplevel": _schema(),
    "git_merge_base_is_ancestor": _schema({"commit": STR, "ref": STR}, ["commit"]),
    "git_head": _schema(),
    "git_add": _schema({"paths": {"type": "array", "items": STR}}, ["paths"]),
    "git_commit": _schema({"message": STR}, ["message"]),
    "solid_build": _schema({"path": STR}),
    "solid_test": _schema({"path": STR, "failfast": BOOL}),
    "solid_snapshot": _schema({
        "path": STR, "time": NUMBER, "camera": STR, "imgsize": STR,
        "projection": {"type": "string", "enum": ["ortho", "perspective"]},
        "colorscheme": STR, "view": STR, "autocenter": BOOL, "viewall": BOOL,
    }),
    "floor_assign": _schema(
        {"sender": STR, "recipient": STR, "assignment": STR, "text": STR},
        ["sender", "recipient", "assignment", "text"],
    ),
    "floor_direction": _schema(
        {"sender": STR, "recipient": STR, "text": STR},
        ["sender", "recipient", "text"],
    ),
    "floor_acknowledge": _schema(
        {"role": STR, "assignment": STR}, ["role", "assignment"]
    ),
    "floor_report": _schema(
        {"sender": STR, "recipient": STR, "text": STR, "assignment": STR},
        ["sender", "recipient", "text"],
    ),
    "floor_complete": _schema(
        {"role": STR, "assignment": STR}, ["role", "assignment"]
    ),
}


class StdioMcpServer:
    """Minimal MCP tools server using newline-delimited JSON-RPC stdio."""

    def __init__(self, tools: ProjectTools) -> None:
        self.tools = tools

    def run(self) -> None:
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self._handle(request)
            except BaseException as error:
                response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(error)},
                }
            if response is not None:
                sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
                sys.stdout.flush()

    def _handle(self, request: dict[str, Any]) -> dict[str, Any] | None:
        request_id = request.get("id")
        method = request.get("method")
        if method == "notifications/initialized":
            return None
        if method == "initialize":
            return self._result(
                request_id,
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "solid-node-studio-floor-tools", "version": "0.1.0"},
                },
            )
        if method == "ping":
            return self._result(request_id, {})
        if method == "tools/list":
            return self._result(
                request_id,
                {
                    "tools": [
                        {
                            "name": name,
                            "description": getattr(self.tools, name).__doc__ or name.replace("_", " "),
                            "inputSchema": TOOL_SCHEMAS[name],
                        }
                        for name in TOOL_NAMES
                    ]
                },
            )
        if method == "tools/call":
            params = request.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            if name not in TOOL_NAMES:
                return self._tool_error(request_id, f"unknown tool: {name}")
            if not isinstance(arguments, dict):
                return self._tool_error(request_id, "tool arguments must be an object")
            try:
                value = getattr(self.tools, name)(**arguments)
            except BaseException as error:
                return self._tool_error(request_id, f"{type(error).__name__}: {error}")
            if isinstance(value, ImagePayload):
                content = [{
                    "type": "image",
                    "data": base64.b64encode(value.data).decode(),
                    "mimeType": value.mime_type,
                }]
                return self._result(request_id, {"content": content, "isError": False})
            text = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
            payload: dict[str, Any] = {
                "content": [{"type": "text", "text": text}],
                "isError": False,
            }
            if isinstance(value, dict):
                payload["structuredContent"] = value
            return self._result(request_id, payload)
        if "id" not in request:
            return None
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"method not found: {method}"},
        }

    @staticmethod
    def _result(request_id: Any, value: Any) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": value}

    @classmethod
    def _tool_error(cls, request_id: Any, message: str) -> dict[str, Any]:
        return cls._result(
            request_id,
            {"content": [{"type": "text", "text": message}], "isError": True},
        )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--solid-command-json", default='["solid"]')
    parser.add_argument("--floor-url")
    parser.add_argument("--floor-session")
    args = parser.parse_args(argv)
    raw_command = json.loads(args.solid_command_json)
    if not isinstance(raw_command, list) or not raw_command or not all(isinstance(item, str) for item in raw_command):
        parser.error("--solid-command-json must encode a non-empty string array")
    StdioMcpServer(
        ProjectTools(
            args.project,
            solid_command=tuple(raw_command),
            floor_url=args.floor_url,
            floor_session=args.floor_session,
        )
    ).run()


if __name__ == "__main__":
    main()
