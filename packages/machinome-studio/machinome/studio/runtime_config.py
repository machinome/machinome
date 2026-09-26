# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Revision-checked project runtime edits that preserve maker-authored TOML."""

from __future__ import annotations

import hashlib
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .preparation import AGENT_ID, ProjectRuntimeError
from .profiles import BackendRuntime


class RuntimeConfigConflict(RuntimeError):
    """The project runtime source changed after the browser read it."""


@dataclass(frozen=True)
class RuntimeConfigEdit:
    path: Path
    expected_revision: str
    content: bytes
    revision: str
    mode: int


def runtime_selection(runtime: BackendRuntime) -> str:
    parts = [runtime.backend]
    if runtime.provider is not None:
        parts.append(runtime.provider)
    parts.extend((runtime.model, runtime.effort))
    return ":".join(parts)


def config_revision(path: Path) -> str:
    return _revision(_read(path)[0])


def prepare_runtime_edit(
    path: Path,
    role: str,
    runtime: BackendRuntime,
    expected_revision: str,
) -> RuntimeConfigEdit:
    if not AGENT_ID.fullmatch(role):
        raise ValueError("agent role must be lowercase kebab-case")
    source, mode = _read(path)
    actual = _revision(source)
    if actual != expected_revision:
        raise RuntimeConfigConflict("pyproject.toml changed since the runtime controls were loaded")
    try:
        import tomlkit

        document = tomlkit.parse(source.decode() if source else "")
        tool = _table(document, "tool")
        if "libresolid-studio" in tool:  # type: ignore[operator]
            raise ValueError(
                "Machinome Studio renamed [tool.libresolid-studio] to "
                "[tool.machinome-studio]"
            )
        studio = _table(tool, "machinome-studio")
        agents = _table(studio, "agents")
        agents[role] = runtime_selection(runtime)
        rendered = document.as_string().encode()
        # Parse with the strict project reader's underlying TOML implementation
        # before any live or filesystem state changes.
        import tomllib

        tomllib.loads(rendered.decode())
    except (UnicodeDecodeError, ValueError, TypeError) as error:
        raise ProjectRuntimeError(path, f"invalid TOML: {error}") from error
    return RuntimeConfigEdit(path, expected_revision, rendered, _revision(rendered), mode)


def publish_runtime_edit(edit: RuntimeConfigEdit) -> str:
    current, _mode = _read(edit.path)
    if _revision(current) != edit.expected_revision:
        raise RuntimeConfigConflict("pyproject.toml changed before the runtime update could be published")
    edit.path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".pyproject-", suffix=".toml", dir=edit.path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(edit.content)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, edit.mode)
        os.replace(temporary, edit.path)
    finally:
        temporary.unlink(missing_ok=True)
    return edit.revision


def _table(parent: object, key: str) -> object:
    import tomlkit
    from tomlkit.items import Table

    value = parent.get(key)  # type: ignore[attr-defined]
    if value is None:
        value = tomlkit.table()
        parent[key] = value  # type: ignore[index]
    if not isinstance(value, Table):
        raise ValueError(f"{key} must be a table")
    return value


def _read(path: Path) -> tuple[bytes, int]:
    if not path.exists():
        return b"", 0o644
    if path.is_symlink() or not path.is_file():
        raise ProjectRuntimeError(path, "pyproject.toml must be a regular non-symlink file")
    return path.read_bytes(), stat.S_IMODE(path.stat().st_mode)


def _revision(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
