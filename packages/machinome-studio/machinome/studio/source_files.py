# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Safe, inert project-source discovery and revision-checked editing."""

from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath


DEFAULT_MAX_BYTES = 1_048_576
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class SourceError(RuntimeError):
    """Base error for the browser source boundary."""


class SourceUnavailable(SourceError):
    """The requested path is not safe, visible, or editable text."""


class SourceConflict(SourceError):
    """The requested save was based on a stale content revision."""

    def __init__(self, document: "SourceDocument") -> None:
        super().__init__("source revision conflict")
        self.document = document


@dataclass(frozen=True)
class SourceEntry:
    path: str
    kind: str

    def browser_value(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class SourceDocument:
    path: str
    content: str
    revision: str

    def browser_value(self) -> dict[str, str]:
        return asdict(self)


class SourceWorkspace:
    """Expose the Git-visible working set beneath one verified project root."""

    def __init__(self, project_root: Path, *, max_bytes: int = DEFAULT_MAX_BYTES) -> None:
        self.project_root = project_root.resolve()
        self.max_bytes = max_bytes

    def entries(self) -> list[SourceEntry]:
        files = self._visible_files()
        directories: set[str] = set()
        for path in files:
            parent = PurePosixPath(path).parent
            while str(parent) not in {"", "."}:
                directories.add(parent.as_posix())
                parent = parent.parent
        return [
            *(SourceEntry(path, "directory") for path in sorted(directories)),
            *(SourceEntry(path, "file") for path in sorted(files)),
        ]

    def visible_paths(self) -> set[str]:
        """Return the current Git-visible file paths for watcher reconciliation."""
        return self._visible_files()

    def read(self, path: str) -> SourceDocument:
        relative, candidate = self._editable_candidate(path)
        try:
            size = candidate.stat().st_size
            if size > self.max_bytes:
                raise SourceUnavailable("source file is too large to edit")
            data = candidate.read_bytes()
        except OSError as error:
            raise SourceUnavailable("source file is unavailable") from error
        if len(data) > self.max_bytes:
            raise SourceUnavailable("source file is too large to edit")
        if b"\x00" in data:
            raise SourceUnavailable("source file is not UTF-8 text")
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise SourceUnavailable("source file is not UTF-8 text") from error
        return SourceDocument(relative, content, self._revision(data))

    def read_png(self, path: str) -> bytes:
        relative, candidate = self._editable_candidate(path)
        if PurePosixPath(relative).suffix.lower() != ".png":
            raise SourceUnavailable("source file is not a PNG image")
        try:
            size = candidate.stat().st_size
            if size > self.max_bytes:
                raise SourceUnavailable("source image is too large to preview")
            data = candidate.read_bytes()
        except OSError as error:
            raise SourceUnavailable("source image is unavailable") from error
        if len(data) > self.max_bytes:
            raise SourceUnavailable("source image is too large to preview")
        if not data.startswith(PNG_SIGNATURE):
            raise SourceUnavailable("source file is not a PNG image")
        return data

    def save(self, path: str, content: str, expected_revision: str) -> SourceDocument:
        current = self.read(path)
        if current.revision != expected_revision:
            raise SourceConflict(current)
        try:
            data = content.encode("utf-8")
        except UnicodeEncodeError as error:
            raise SourceUnavailable("source value is not UTF-8 text") from error
        if len(data) > self.max_bytes or b"\x00" in data:
            raise SourceUnavailable("source value is too large or not editable text")

        relative, candidate = self._editable_candidate(path)
        try:
            mode = stat.S_IMODE(candidate.stat().st_mode)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=".machinome-studio-save-",
                dir=candidate.parent,
            )
            temporary = Path(temporary_name)
            try:
                with os.fdopen(descriptor, "wb") as output:
                    output.write(data)
                    output.flush()
                    os.fsync(output.fileno())
                os.chmod(temporary, mode)
                os.replace(temporary, candidate)
            finally:
                if temporary.exists():
                    temporary.unlink()
        except OSError as error:
            raise SourceUnavailable("source file could not be saved") from error
        return SourceDocument(relative, content, self._revision(data))

    def is_visible(self, path: str) -> bool:
        try:
            relative = self._relative(path)
        except SourceUnavailable:
            return False
        return relative in self._visible_files()

    def _editable_candidate(self, path: str) -> tuple[str, Path]:
        relative = self._relative(path)
        if relative not in self._visible_files():
            raise SourceUnavailable("source path is not Git-visible")
        candidate = self.project_root.joinpath(*PurePosixPath(relative).parts)
        current = self.project_root
        try:
            for part in PurePosixPath(relative).parts:
                current = current / part
                if current.is_symlink():
                    raise SourceUnavailable("source symlinks are unavailable")
            if not candidate.is_file() or not stat.S_ISREG(candidate.stat().st_mode):
                raise SourceUnavailable("source path is not a regular file")
            resolved = candidate.resolve(strict=True)
        except OSError as error:
            raise SourceUnavailable("source file is unavailable") from error
        if resolved.parent != self.project_root and self.project_root not in resolved.parents:
            raise SourceUnavailable("source path escapes the project")
        return relative, candidate

    def _visible_files(self) -> set[str]:
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.project_root),
                    "ls-files",
                    "-z",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                ],
                check=True,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            raise SourceUnavailable("project source inventory is unavailable") from error
        files: set[str] = set()
        for value in result.stdout.split(b"\0"):
            if not value:
                continue
            try:
                path = value.decode("utf-8")
                relative = self._relative(path)
            except (UnicodeDecodeError, SourceUnavailable):
                continue
            if not self._excluded(relative):
                files.add(relative)
        return files

    def _relative(self, value: str) -> str:
        if not value or "\x00" in value or "\\" in value:
            raise SourceUnavailable("invalid source path")
        path = PurePosixPath(value)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            raise SourceUnavailable("source path escapes the project")
        relative = path.as_posix()
        if self._excluded(relative):
            raise SourceUnavailable("source path is excluded")
        return relative

    @staticmethod
    def _excluded(relative: str) -> bool:
        first = PurePosixPath(relative).parts[0]
        return (
            first == ".git"
            or first == "_build"
            or first.startswith("_build.")
            or first.startswith(".machinome-build-")
        )

    @staticmethod
    def _revision(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
