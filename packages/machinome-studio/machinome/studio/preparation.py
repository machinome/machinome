"""Fail-closed preparation of one named workspace project."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path


PROJECT_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


@dataclass(frozen=True)
class PreparedProject:
    name: str
    project_root: Path
    model: Path
    artifact_root: Path


class PreparationError(RuntimeError):
    def __init__(self, stage: str, name: str | None, project_root: Path | None, reason: str) -> None:
        self.stage = stage
        self.name = name
        self.project_root = project_root
        location = f" at {project_root}" if project_root is not None else ""
        super().__init__(f"project preparation failed during {stage}{location}: {reason}")


def primary_shop_root(checkout: Path) -> Path:
    """Return this repository's primary checkout, including from a worktree."""
    result = _run(
        ("git", "-C", str(checkout.resolve()), "rev-parse", "--git-common-dir"),
        stage="workspace",
        name=None,
        project_root=None,
    )
    common = Path(result.stdout.strip())
    if not common.is_absolute():
        common = checkout.resolve() / common
    return common.resolve().parent


def default_project_home(checkout: Path) -> Path:
    return checkout.resolve() / "projects"


def default_solid_command(checkout: Path) -> tuple[str, ...]:
    primary = primary_shop_root(checkout)
    solid_node_cli = primary / "solid-node" / "solid_node" / "cli.py"
    if solid_node_cli.is_file():
        # Prefer the checked-out solid-node framework inside the shop.
        return (sys.executable, "-m", "solid_node.cli")
    executable = primary / ".venv" / "bin" / "solid"
    if not executable.is_file():
        raise PreparationError(
            "solid-command",
            None,
            None,
            f"workspace solid executable is unavailable: {executable}; configure an explicit equivalent",
        )
    return (str(executable),)


def resolve_project(name: str | None, project_home: Path) -> Path:
    if name is None or not PROJECT_NAME.fullmatch(name):
        raise PreparationError("project-name", name, None, "a lowercase kebab-case project name is required")
    home = project_home.resolve()
    try:
        home.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise PreparationError("project-home", name, home, str(error)) from error
    if not home.is_dir():
        raise PreparationError("project-home", name, home, "workspace projects directory does not exist")
    candidate = home / name
    if candidate.is_symlink():
        raise PreparationError("project-path", name, candidate, "project location must not be a symbolic link")
    resolved = candidate.resolve(strict=False)
    if resolved.parent != home:
        raise PreparationError("project-path", name, candidate, "project path escapes the workspace projects directory")
    if candidate.exists() and not candidate.is_dir():
        raise PreparationError("project-path", name, candidate, "project location is not a directory")
    return resolved


def prepare_project(
    name: str | None,
    *,
    project_home: Path,
    solid_command: str | Sequence[str],
    shop_root: Path | None = None,
) -> PreparedProject:
    project_root = resolve_project(name, project_home)
    assert name is not None
    created = not project_root.exists()
    # When solid-node is run from a checkout inside the shop, add the
    # solid-node checkout to PYTHONPATH so ``python -m solid_node.cli``
    # can find the package.
    solid_env: dict[str, str] | None = None
    if shop_root is not None:
        solid_node_path = shop_root / "solid-node"
        if solid_node_path.is_dir():
            existing = os.environ.get("PYTHONPATH", "")
            solid_env = {"PYTHONPATH": os.pathsep.join(
                item for item in (str(solid_node_path), existing) if item
            )}
    if created:
        _run(
            (*_command(solid_command), "new", name),
            cwd=project_home.resolve(),
            stage="scaffold",
            name=name,
            project_root=project_root,
            extra_env=solid_env,
        )
        if not project_root.is_dir():
            raise PreparationError("scaffold", name, project_root, "solid new did not create the named project directory")
        _run(("git", "init", "-q", "-b", "main", str(project_root)), stage="git-init", name=name, project_root=project_root)
        _require_exact_repository(project_root, name)
        _run(("git", "-C", str(project_root), "add", "--all"), stage="git-add", name=name, project_root=project_root)
        _run(
            ("git", "-C", str(project_root), "commit", "-q", "-m", "Initial solid-node scaffold"),
            stage="git-commit",
            name=name,
            project_root=project_root,
        )
    else:
        _require_exact_repository(project_root, name)

    artifact_root = (project_root / "_build").resolve()
    snapshot = artifact_root / "viewer.json"
    previous = _fingerprint(snapshot)
    _run(
        (*_command(solid_command), "build", "root"),
        cwd=project_root,
        stage="build",
        name=name,
        project_root=project_root,
        extra_env=solid_env,
    )
    if previous is not None and _fingerprint(snapshot) == previous:
        raise PreparationError("snapshot", name, project_root, "build left the previous viewer snapshot unchanged")
    _validate_snapshot(snapshot, artifact_root, name, project_root)
    return PreparedProject(name=name, project_root=project_root, model=Path("root"), artifact_root=artifact_root)


def _require_exact_repository(project_root: Path, name: str) -> None:
    result = _run(
        ("git", "-C", str(project_root), "rev-parse", "--show-toplevel"),
        stage="repository",
        name=name,
        project_root=project_root,
    )
    if Path(result.stdout.strip()).resolve() != project_root.resolve():
        raise PreparationError("repository", name, project_root, "location is not the exact root of an independent Git repository")


def _validate_snapshot(snapshot: Path, artifact_root: Path, name: str, project_root: Path) -> None:
    try:
        value = json.loads(snapshot.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise PreparationError("snapshot", name, project_root, f"viewer snapshot is unavailable or malformed: {error}") from error
    if not isinstance(value, dict) or not isinstance(value.get("root"), dict):
        raise PreparationError("snapshot", name, project_root, "viewer snapshot has no root model tree")
    models = tuple(_model_references(value["root"]))
    if not models:
        raise PreparationError("snapshot", name, project_root, "viewer snapshot references no model artifacts")
    for model in models:
        candidate = (artifact_root / model).resolve()
        if artifact_root not in candidate.parents or not candidate.is_file():
            raise PreparationError("artifact", name, project_root, f"referenced model artifact is missing or outside _build: {model}")


def _model_references(value: object) -> Iterator[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "model" and isinstance(child, str):
                yield child
            else:
                yield from _model_references(child)
    elif isinstance(value, list):
        for child in value:
            yield from _model_references(child)


def _fingerprint(path: Path) -> tuple[int, int, int] | None:
    try:
        stat = path.stat()
    except OSError:
        return None
    return stat.st_ino, stat.st_size, stat.st_mtime_ns


def _command(command: str | Sequence[str]) -> tuple[str, ...]:
    return (command,) if isinstance(command, str) else tuple(command)


def _run(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    stage: str,
    name: str | None,
    project_root: Path | None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = None
    if extra_env:
        env = {**os.environ, **extra_env}
    try:
        return subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True, env=env)
    except FileNotFoundError as error:
        raise PreparationError(stage, name, project_root, str(error)) from error
    except subprocess.CalledProcessError as error:
        reason = (error.stderr or error.stdout or f"command exited {error.returncode}").strip()
        raise PreparationError(stage, name, project_root, reason) from error
