# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Best-effort publication of a project's canonical model preview."""

from __future__ import annotations

import os
import subprocess
import tempfile
import threading
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from stat import S_ISREG


SCREENSHOT_NAME = "screenshot.png"
SCREENSHOT_DIRECTORY = "screenshots"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_locks: dict[Path, threading.Lock] = {}
_locks_guard = threading.Lock()


@dataclass(frozen=True)
class ScreenshotResult:
    """The non-fatal result of one screenshot refresh request."""

    updated: bool = False
    revision: str | None = None
    warning: str | None = None


def screenshot_path(project_root: Path, model: str | None = None) -> Path:
    """Where the canonical preview of one openable entry lives.

    A project listed as one project keeps the root `screenshot.png` it has
    always had. One declared model of a multi-model project gets its own
    committed preview beside its siblings, because a folder of models needs a
    picture per card and a fresh clone should have them before anything is
    built.
    """
    if model is None:
        return project_root / SCREENSHOT_NAME
    return project_root / SCREENSHOT_DIRECTORY / f"{model}.png"


def screenshot_revision(project_root: Path, model: str | None = None) -> str | None:
    """Return the content revision only for a regular, local PNG file."""
    path = screenshot_path(project_root, model)
    try:
        status = path.lstat()
        if not S_ISREG(status.st_mode):
            return None
        data = path.read_bytes()
    except OSError:
        return None
    return sha256(data).hexdigest() if _is_png(data) else None


def is_safe_screenshot(project_root: Path, model: str | None = None) -> bool:
    """Whether the canonical path is a regular non-symlink PNG file."""
    return screenshot_revision(project_root, model) is not None


def refresh_project_screenshot(
    project_root: Path,
    machinome_command: Sequence[str],
    *,
    model: str | None = None,
    extra_environment: Mapping[str, str] | None = None,
) -> ScreenshotResult:
    """Render and atomically publish the fixed 640x360 project thumbnail.

    The rendered output is always outside the project.  A short-lived staging
    file beside the destination is only used after a valid completed PNG is
    available, so ``os.replace`` never exposes a partial image to the hub.
    """
    root = project_root.resolve()
    with _lock_for(screenshot_path(root, model)):
        target = screenshot_path(root, model)
        relative = target.relative_to(root)
        try:
            existing = _existing_bytes(target)
            if existing is _UNSAFE:
                return ScreenshotResult(warning=f"{relative} is not a regular non-symlink file")
            with tempfile.TemporaryDirectory(prefix="machinome-studio-screenshot-") as temporary:
                output = Path(temporary) / SCREENSHOT_NAME
                env = {**os.environ, **dict(extra_environment or {})}
                result = subprocess.run(
                    [
                        *machinome_command,
                        "snapshot",
                        *([model] if model else ()),
                        "--renderer",
                        "web",
                        "-o",
                        str(output),
                        "--time",
                        "0.1",
                        "--imgsize",
                        "640x360",
                        "--autocenter",
                        "--viewall",
                    ],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    env=env,
                )
                if result.returncode:
                    detail = (result.stderr or result.stdout or f"exit {result.returncode}").strip()
                    return ScreenshotResult(warning=f"screenshot render failed: {detail}")
                data = output.read_bytes()
            if not _is_png(data):
                return ScreenshotResult(warning="screenshot render produced no valid PNG")
            if existing == data:
                return ScreenshotResult(revision=sha256(data).hexdigest())
            # Refuse a path that turned unsafe during rendering too.
            if _existing_bytes(target) is _UNSAFE:
                return ScreenshotResult(warning=f"{relative} became an unsafe path")
            target.parent.mkdir(parents=True, exist_ok=True)
            descriptor, staged_name = tempfile.mkstemp(prefix=".screenshot-", suffix=".png", dir=target.parent)
            staged = Path(staged_name)
            try:
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(staged, target)
            finally:
                staged.unlink(missing_ok=True)
            return ScreenshotResult(updated=True, revision=sha256(data).hexdigest())
        except (OSError, subprocess.SubprocessError) as error:
            return ScreenshotResult(warning=f"screenshot refresh failed: {error}")


_UNSAFE = object()


def _existing_bytes(path: Path) -> bytes | None | object:
    try:
        status = path.lstat()
    except FileNotFoundError:
        return None
    except OSError:
        return _UNSAFE
    if not S_ISREG(status.st_mode):
        return _UNSAFE
    try:
        return path.read_bytes()
    except OSError:
        return _UNSAFE


def _is_png(data: bytes) -> bool:
    return len(data) >= len(PNG_SIGNATURE) and data.startswith(PNG_SIGNATURE)


def _lock_for(target: Path) -> threading.Lock:
    """One lock per published preview: two models never wait on each other."""
    with _locks_guard:
        return _locks.setdefault(target, threading.Lock())
