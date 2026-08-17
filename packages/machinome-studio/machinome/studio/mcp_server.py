# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
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

# Metadata `git diff` emits around each file, which carries no hunk content.
GIT_DIFF_PREAMBLE = (
    "diff --git ", "index ", "new file mode ", "deleted file mode ",
    "old mode ", "new mode ", "similarity index ", "dissimilarity index ",
    "rename from ", "rename to ", "copy from ", "copy to ",
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
        """List the project files in a directory.

        Ignored and untracked-but-excluded files are omitted.  Paths are
        relative to the project root; directories end with `/`.
        """
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
        """Find project files whose path or basename matches a glob pattern."""
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
        """Search project file contents, returning `path:line:text` matches."""
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
        """Read a project file.

        Text files return their content; PNG, JPG, GIF, and WEBP files return
        viewable image content instead of raw bytes.  Read the lines you are
        about to patch immediately before patching them: `apply_patch`
        matches context against the file as it is now, not as it was earlier
        in the session.
        """
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
        """Report existence, type, size, and modification time for a path."""
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
        """Write a file whole, creating it and any missing parent directories.

        This is the way to create a new file: no prior file, `make_dir` call,
        or patch is needed.  Prefer `edit_file` or `apply_patch` when only
        part of an existing file changes.
        """
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
        """Replace an exact string in an existing file.

        The most reliable edit when one known block changes, because it does
        not depend on line numbers or surrounding context.  `old_string` must
        match exactly once unless `replace_all` is set.
        """
        target = self._path(path, must_exist=True)
        content = target.read_text()
        count = content.count(old_string)
        if count == 0:
            raise ValueError("old_string was not found")
        if not replace_all and count != 1:
            raise ValueError(f"old_string matched {count} times; use replace_all")
        target.write_text(content.replace(old_string, new_string, -1 if replace_all else 1))
        return {"path": target.relative_to(self.root).as_posix(), "replacements": count if replace_all else 1}

    def apply_patch(self, unified_diff: str, path: str | None = None) -> dict[str, Any]:
        """Apply a standard unified diff to one or more project files.

        The diff names the files it changes, so `path` is optional; supply it
        only for a single-file diff, where it is checked against the diff.
        `--- /dev/null` creates a file and `+++ /dev/null` deletes one, so one
        call can carry a whole coherent edit across implementation and tests.

        Every file is verified against its current content before anything is
        written: if any hunk does not match, no file is modified at all.  So
        re-read the affected lines before building the diff if anything has
        changed since you last read them.

        Output from `git diff` applies unedited, including its `diff --git` and
        `index` preamble.  This tool is not Codex `apply_patch`; a
        `*** Begin Patch` envelope is rejected.  Hunks must match exactly, with
        no fuzz or offset search.
        """
        lines = unified_diff.splitlines(keepends=True)
        if any(line.startswith("*** ") for line in lines):
            raise ValueError(
                "patch is not a unified diff: remove the '*** Begin Patch' envelope "
                "and send ordinary '--- a/<path>' and '+++ b/<path>' headers "
                "followed by '@@' hunks"
            )
        headers = [index for index, line in enumerate(lines) if line.startswith("--- ")]
        if not headers or any(
            index + 1 >= len(lines) or not lines[index + 1].startswith("+++ ")
            for index in headers
        ):
            raise ValueError(
                "patch must contain a unified-diff file header: a '--- a/<path>' "
                "line immediately followed by a '+++ b/<path>' line"
            )
        if path is not None and len(headers) > 1:
            raise ValueError(
                f"patch describes {len(headers)} files but 'path' names one; omit "
                "'path' for a multi-file diff, since the diff names its own targets"
            )

        if path is not None:
            named = self._path(path)
            described = self._patch_target(lines[headers[0]], lines[headers[0] + 1])
            if named != described:
                raise ValueError(
                    f"patch changes {described.relative_to(self.root).as_posix()} but "
                    f"'path' names {named.relative_to(self.root).as_posix()}"
                )

        # Phase one: resolve and verify every file the diff describes.  A file's
        # hunks end before the next file's `diff --git`/`index` preamble.
        plans: list[tuple[Path, str, list[str] | None]] = []
        for position, start in enumerate(headers):
            stop = headers[position + 1] if position + 1 < len(headers) else len(lines)
            while stop > start + 2 and lines[stop - 1].startswith(GIT_DIFF_PREAMBLE):
                stop -= 1
            plans.append(self._patch_plan(lines, start, stop))

        # Phase two: no plan can fail from here, so the whole diff lands.
        files: list[dict[str, str]] = []
        for target, relative, content in plans:
            if content is None:
                target.unlink()
                files.append({"path": relative, "change": "deleted"})
                continue
            created = not target.exists()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("".join(content))
            files.append({"path": relative, "change": "created" if created else "changed"})
        return {"files": files, "applied": True}

    HUNK_HEADER = re.compile(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")

    def _patch_plan(
        self, lines: list[str], start: int, stop: int
    ) -> tuple[Path, str, list[str] | None]:
        """Verify one file's hunks and return its resolved content, or None to delete."""
        source = self._patch_header_path(lines[start])
        destination = self._patch_header_path(lines[start + 1])
        target = self._patch_target(lines[start], lines[start + 1])
        relative = target.relative_to(self.root).as_posix()
        if source is None:
            if target.exists():
                raise ValueError(
                    f"patch creates {relative} from /dev/null but that file already "
                    "exists; diff it against its current content instead"
                )
            original: list[str] = []
        else:
            if not target.is_file():
                raise ValueError(
                    f"patch changes {relative}, which is not an existing file; "
                    "create new files with write_file or with a '--- /dev/null' header"
                )
            original = target.read_text().splitlines(keepends=True)

        output: list[str] = []
        cursor = 0
        index = start + 2
        while index < stop:
            match = self.HUNK_HEADER.match(lines[index].rstrip("\n"))
            if match is None:
                raise ValueError(
                    f"invalid unified-diff hunk header for {relative}: "
                    f"{lines[index].rstrip()!r}; expected "
                    "'@@ -<old-start>,<old-count> +<new-start>,<new-count> @@'"
                )
            hunk_header = lines[index].rstrip("\n")
            old_start = max(int(match.group(1)), 1)
            output.extend(original[cursor : old_start - 1])
            cursor = old_start - 1
            index += 1
            while index < stop and not lines[index].startswith("@@ "):
                line = lines[index]
                if line.startswith("\\ No newline at end of file"):
                    index += 1
                    continue
                if not line or line[0] not in " +-":
                    raise ValueError(
                        f"invalid unified-diff line for {relative}: {line.rstrip()!r}; "
                        "every line in a hunk must begin with ' ', '+', or '-'"
                    )
                marker, value = line[0], line[1:]
                if marker in " -":
                    if cursor >= len(original) or original[cursor] != value:
                        actual = (
                            repr(original[cursor]) if cursor < len(original)
                            else "end of file"
                        )
                        raise ValueError(
                            f"patch context does not match target file at line "
                            f"{cursor + 1} of {relative} (hunk {hunk_header!r}): "
                            f"patch expected {value!r} but the file has {actual}. "
                            "Re-read the file and rebuild the diff, or use edit_file "
                            "for a narrow exact replacement. No file was modified."
                        )
                    cursor += 1
                if marker in " +":
                    output.append(value)
                index += 1
        output.extend(original[cursor:])
        if destination is None:
            if output:
                raise ValueError(
                    f"patch deletes {relative} to /dev/null but leaves content behind"
                )
            return target, relative, None
        return target, relative, output

    def _patch_target(self, source_header: str, destination_header: str) -> Path:
        """Resolve the project file one file header pair describes."""
        source = self._patch_header_path(source_header)
        destination = self._patch_header_path(destination_header)
        if source is None and destination is None:
            raise ValueError("unified-diff file header names /dev/null on both sides")
        return self._path(destination if destination is not None else source)

    @staticmethod
    def _patch_header_path(header: str) -> str | None:
        """Read a file path out of a '---' or '+++' header, or None for /dev/null."""
        value = header.split("\t", 1)[0].rstrip("\n")[4:].strip()
        if not value:
            raise ValueError(f"unified-diff file header names no path: {header.rstrip()!r}")
        if value in ("/dev/null", "a/dev/null", "b/dev/null"):
            return None
        prefix, separator, remainder = value.partition("/")
        return remainder if separator and prefix in ("a", "b") else value

    def delete_file(self, path: str) -> dict[str, Any]:
        """Delete one existing project file."""
        target = self._path(path, must_exist=True)
        if not target.is_file():
            raise ValueError(f"not a file: {path!r}")
        target.unlink()
        return {"path": target.relative_to(self.root).as_posix(), "deleted": True}

    def move_file(self, src: str, dst: str) -> dict[str, Any]:
        """Move or rename a project file; the destination must not exist."""
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
        """Create a directory and its parents; `write_file` does not need it."""
        target = self._path(path)
        target.mkdir(parents=True, exist_ok=True)
        return {"path": target.relative_to(self.root).as_posix(), "created": True}

    # -- git ---------------------------------------------------------

    def git_status(self) -> dict[str, Any]:
        """Show the short branch-annotated working-tree status."""
        return self._git("status", "--short", "--branch")

    def git_diff(self, path: str | None = None, staged: bool = False) -> dict[str, Any]:
        """Show unstaged changes, or staged changes when `staged` is set."""
        args = ["diff"]
        if staged:
            args.append("--cached")
        if path is not None:
            args.extend(("--", self._relative(path)))
        return self._git(*args)

    def git_log(self, path: str | None = None, limit: int = 20) -> dict[str, Any]:
        """Show recent commits in one-line decorated form."""
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        args = ["log", f"-{limit}", "--oneline", "--decorate"]
        if path is not None:
            args.extend(("--", self._relative(path)))
        return self._git(*args)

    def git_show(self, revision: str, path: str) -> dict[str, Any]:
        """Read one file's content as of a given revision.

        Use this to read a released drawing exactly as it was committed,
        rather than the possibly edited working copy.
        """
        relative = self._relative(path)
        return self._git("show", f"{self._revision(revision)}:{relative}")

    def git_rev_parse_toplevel(self) -> str:
        """Return the repository root, failing unless it is the active project."""
        result = self._git("rev-parse", "--show-toplevel")
        if not result["ok"]:
            raise RuntimeError(result["stderr"] or "git rev-parse failed")
        toplevel = Path(result["stdout"].strip()).resolve()
        if toplevel != self.root:
            raise RuntimeError(f"active project is not its repository root: {toplevel}")
        return str(toplevel)

    def git_merge_base_is_ancestor(self, commit: str, ref: str = "HEAD") -> dict[str, Any]:
        """Report whether `commit` is an ancestor of `ref` (default HEAD)."""
        result = self._git(
            "merge-base", "--is-ancestor", self._revision(commit), self._revision(ref)
        )
        result["is_ancestor"] = result["exit_code"] == 0
        return result

    def git_head(self) -> dict[str, Any]:
        """Return the current commit sha and branch name."""
        sha = self._git("rev-parse", "HEAD")
        branch = self._git("symbolic-ref", "--quiet", "--short", "HEAD")
        if not sha["ok"]:
            raise RuntimeError(sha["stderr"] or "git rev-parse HEAD failed")
        return {
            "sha": sha["stdout"].strip(),
            "branch": branch["stdout"].strip() if branch["ok"] else None,
        }

    def git_add(self, paths: list[str]) -> dict[str, Any]:
        """Stage the exact paths given; no path is unstaged or substituted."""
        if not paths:
            raise ValueError("paths must not be empty")
        return self._git("add", "--", *(self._relative(path) for path in paths))

    def git_commit(self, message: str) -> dict[str, Any]:
        """Commit the staged changes in the active project.

        The shop also best-effort refreshes and stages the managed root
        `screenshot.png` preview; a screenshot failure never blocks the
        commit and is reported separately as a warning.
        """
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
        """Run `solid build`, returning its exit status and output."""
        reference = self._reference(path)
        result = self._run([*self.solid_command, "build", *([reference] if reference else [])])
        if result["ok"]:
            screenshot = refresh_project_screenshot(self.root, self.solid_command)
            if screenshot.warning:
                result["screenshot_warning"] = screenshot.warning
        return result

    def solid_test(self, path: str | None = None, failfast: bool = False) -> dict[str, Any]:
        """Run `solid test`, returning its exit status and output."""
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
        """Render a snapshot and return the image; nothing is left in the project.

        Accepts the same options as the `solid snapshot` CLI command.  The
        image is returned as tool output, so it never appears in git status
        and is never commit evidence.
        """
        reference = self._reference(path)
        with tempfile.TemporaryDirectory(prefix="libresolid-studio-snapshot-") as temporary:
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
        """Dispatch an assignment to a role that reports to you."""
        return self._floor().assign(sender, recipient, assignment, text)

    def floor_direction(
        self,
        sender: str,
        recipient: str,
        text: str,
    ) -> dict[str, Any]:
        """Send steering direction that does not replace the active assignment."""
        return self._floor().direction(sender, recipient, text)

    def floor_acknowledge(self, role: str, assignment: str) -> dict[str, Any]:
        """Acknowledge a received assignment before starting work on it."""
        return self._floor().acknowledge(role, assignment)

    def floor_report(
        self,
        sender: str,
        recipient: str,
        text: str,
        assignment: str = "",
    ) -> dict[str, Any]:
        """Send progress, findings, or a final report to another role."""
        return self._floor().report(sender, recipient, text, assignment)

    def floor_complete(self, role: str, assignment: str) -> dict[str, Any]:
        """Mark an assignment finished after sending its final report."""
        return self._floor().complete(role, assignment)


def _schema(properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties or {},
        "required": required or [],
        "additionalProperties": False,
    }


def _param(kind: str, description: str, **extra: Any) -> dict[str, Any]:
    """Describe one tool parameter so the calling model needs no guesswork."""
    return {"type": kind, "description": description, **extra}


def STR(description: str, **extra: Any) -> dict[str, Any]:
    return _param("string", description, **extra)


def BOOL(description: str) -> dict[str, Any]:
    return _param("boolean", description)


def INT(description: str) -> dict[str, Any]:
    return _param("integer", description)


def NUMBER(description: str) -> dict[str, Any]:
    return _param("number", description)


PROJECT_PATH = "Path relative to the active project root."
TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "list_dir": _schema({
        "path": STR(f"Directory to list. {PROJECT_PATH} Defaults to the root."),
        "recursive": BOOL("List every descendant instead of one level."),
    }),
    "find_files": _schema({
        "pattern": STR("Glob matched against each file's path or basename, such as 'test_*.py'."),
    }, ["pattern"]),
    "search_content": _schema({
        "pattern": STR("Literal text, or a regular expression when 'regex' is true."),
        "path": STR(f"File or directory to search. {PROJECT_PATH} Defaults to the root."),
        "regex": BOOL("Treat 'pattern' as a regular expression."),
    }, ["pattern"]),
    "read_file": _schema({
        "path": STR(f"File to read. {PROJECT_PATH}"),
        "offset": INT("First line to return, counting from 1."),
        "limit": INT("Maximum number of lines to return."),
    }, ["path"]),
    "stat": _schema({"path": STR(f"Path to inspect. {PROJECT_PATH}")}, ["path"]),
    "write_file": _schema({
        "path": STR(f"File to write. {PROJECT_PATH} Missing parent directories are created."),
        "content": STR("Complete new content of the file; it replaces anything already there."),
        "must_not_exist": BOOL("Fail instead of overwriting an existing file."),
    }, ["path", "content"]),
    "edit_file": _schema({
        "path": STR(f"Existing file to edit. {PROJECT_PATH}"),
        "old_string": STR("Exact text to replace, including its indentation and line breaks."),
        "new_string": STR("Replacement text."),
        "replace_all": BOOL("Replace every occurrence instead of requiring exactly one."),
    }, ["path", "old_string", "new_string"]),
    "apply_patch": _schema({
        "unified_diff": STR(
            "Standard unified diff. Each file it changes is introduced by a "
            "'--- a/<path>' line and a '+++ b/<path>' line, followed by "
            "'@@ -<start>,<count> +<start>,<count> @@' hunks whose lines each "
            "begin with ' ', '+', or '-'. Several files may appear in one diff, "
            "and they are all applied together or not at all. Use '/dev/null' on "
            "the '---' side to create a file or on the '+++' side to delete one. "
            "Output from 'git diff' is accepted unedited. Not the Codex "
            "'*** Begin Patch' format."
        ),
        "path": STR(
            "Optional. The diff already names its targets; supply this only for a "
            f"single-file diff, where it is checked against the diff. {PROJECT_PATH}"
        ),
    }, ["unified_diff"]),
    "delete_file": _schema({"path": STR(f"File to delete. {PROJECT_PATH}")}, ["path"]),
    "move_file": _schema({
        "src": STR(f"Existing file to move. {PROJECT_PATH}"),
        "dst": STR(f"Destination, which must not already exist. {PROJECT_PATH}"),
    }, ["src", "dst"]),
    "make_dir": _schema({
        "path": STR(f"Directory to create, with its parents. {PROJECT_PATH}"),
    }, ["path"]),
    "git_status": _schema(),
    "git_diff": _schema({
        "path": STR(f"Limit the diff to this path. {PROJECT_PATH}"),
        "staged": BOOL("Show staged changes rather than unstaged ones."),
    }),
    "git_log": _schema({
        "path": STR(f"Limit history to this path. {PROJECT_PATH}"),
        "limit": INT("Number of commits to show, from 1 to 1000. Defaults to 20."),
    }),
    "git_show": _schema({
        "revision": STR("Commit sha, tag, or ref to read the file from."),
        "path": STR(f"File to read at that revision. {PROJECT_PATH}"),
    }, ["revision", "path"]),
    "git_rev_parse_toplevel": _schema(),
    "git_merge_base_is_ancestor": _schema({
        "commit": STR("Commit tested as the ancestor, such as a released drawing commit."),
        "ref": STR("Descendant ref to test against. Defaults to HEAD."),
    }, ["commit"]),
    "git_head": _schema(),
    "git_add": _schema({
        "paths": {
            "type": "array",
            "items": STR(f"Path to stage. {PROJECT_PATH}"),
            "description": "Exact paths to stage. Nothing else is staged or unstaged.",
        },
    }, ["paths"]),
    "git_commit": _schema({
        "message": STR("Commit message for the already staged changes."),
    }, ["message"]),
    "solid_build": _schema({
        "path": STR("Node reference or file to build. Defaults to the project model."),
    }),
    "solid_test": _schema({
        "path": STR("Test file or node reference to run. Defaults to the whole suite."),
        "failfast": BOOL("Stop at the first failing test."),
    }),
    "solid_snapshot": _schema({
        "path": STR("Node reference or file to render. Defaults to the project model."),
        "time": NUMBER("Animation time to render at."),
        "camera": STR("Camera placement, as accepted by 'solid snapshot'."),
        "imgsize": STR("Image size as 'width,height', such as '1024,768'."),
        "projection": {
            "type": "string",
            "enum": ["ortho", "perspective"],
            "description": "Projection used for the render.",
        },
        "colorscheme": STR("Named render colour scheme."),
        "view": STR("View flags, as accepted by 'solid snapshot'."),
        "autocenter": BOOL("Centre the model in the frame."),
        "viewall": BOOL("Zoom so the whole model is visible."),
    }),
    "floor_assign": _schema(
        {
            "sender": STR("Your own role id."),
            "recipient": STR("Role id you are assigning work to."),
            "assignment": STR("Assignment id this dispatch opens."),
            "text": STR("Assignment brief."),
        },
        ["sender", "recipient", "assignment", "text"],
    ),
    "floor_direction": _schema(
        {
            "sender": STR("Your own role id."),
            "recipient": STR("Role id being steered."),
            "text": STR("Direction, which does not by itself replace an active assignment."),
        },
        ["sender", "recipient", "text"],
    ),
    "floor_acknowledge": _schema(
        {
            "role": STR("Your own role id."),
            "assignment": STR("Assignment id being acknowledged."),
        },
        ["role", "assignment"],
    ),
    "floor_report": _schema(
        {
            "sender": STR("Your own role id."),
            "recipient": STR("Role id to report to."),
            "text": STR("Progress, findings, blockers, or the final report."),
            "assignment": STR("Assignment id the report belongs to, when it has one."),
        },
        ["sender", "recipient", "text"],
    ),
    "floor_complete": _schema(
        {
            "role": STR("Your own role id."),
            "assignment": STR("Assignment id being completed."),
        },
        ["role", "assignment"],
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
                    "serverInfo": {"name": "libresolid-studio-floor-tools", "version": "0.1.0"},
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
