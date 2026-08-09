"""Fail-closed preparation of one named workspace project."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path


PROJECT_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
AGENT_ID = PROJECT_NAME
REQUIRED_VIEWER_API = 2
CODEX_MODELS = {"gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.3-codex-spark"}
CLAUDE_MODELS = {"sonnet", "opus"}
CODEX_EFFORTS = {"low", "medium", "high", "xhigh", "max", "ultra"}
CLAUDE_EFFORTS = {"low", "medium", "high"}


@dataclass(frozen=True)
class ProjectAgentRuntime:
    backend: str
    provider: str | None
    model: str
    effort: str | None
    source: str


@dataclass(frozen=True)
class ProjectRuntimeSelection:
    project_root: Path
    source_path: Path
    agents: dict[str, ProjectAgentRuntime]


@dataclass(frozen=True)
class PreparedProject:
    name: str
    project_root: Path
    model: Path
    artifact_root: Path
    viewer_bundle: Path | None = None
    viewer_api_version: int | None = None
    solid_command: tuple[str, ...] = ()
    build_environment: dict[str, str] | None = None

    def build_invocation(self) -> tuple[tuple[str, ...], dict[str, str] | None]:
        """The command and environment overlay that builds this project.

        The watcher rebuilds the same project the same way preparation
        first built it; carrying the invocation on the prepared project
        keeps one definition rather than two that can drift apart.
        """
        return build_command(self.solid_command), self.build_environment


def artifact_root_for(project_root: Path) -> Path:
    """The project's single, atomically updated published build directory."""
    return project_root / "_build"


def build_command(solid_command: str | Sequence[str]) -> tuple[str, ...]:
    # No node reference: the framework resolves the project's model from
    # [tool.solid-node] in the project's pyproject.toml.
    return (*_command(solid_command), "build")


def build_environment(shop_root: Path | None) -> dict[str, str] | None:
    """PYTHONPATH overlay for a solid-node checkout inside the shop.

    When solid-node is run from a checkout inside the shop, the checkout
    must be on PYTHONPATH for ``python -c "from solid_node.cli ..."`` to
    find the package.
    """
    if shop_root is None:
        return None
    solid_node_path = shop_root / "solid-node"
    if not solid_node_path.is_dir():
        return None
    existing = os.environ.get("PYTHONPATH", "")
    return {"PYTHONPATH": os.pathsep.join(
        item for item in (str(solid_node_path), existing) if item
    )}


class PreparationError(RuntimeError):
    def __init__(self, stage: str, name: str | None, project_root: Path | None, reason: str) -> None:
        self.stage = stage
        self.name = name
        self.project_root = project_root
        location = f" at {project_root}" if project_root is not None else ""
        super().__init__(f"project preparation failed during {stage}{location}: {reason}")


class ProjectRuntimeError(ValueError):
    """The active project's shop runtime selection is malformed or unsafe."""

    def __init__(self, source_path: Path, reason: str) -> None:
        self.source_path = source_path
        super().__init__(f"project runtime configuration at {source_path}: {reason}")


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
        # Module has no __main__.py, so use -c to call manage() directly.
        return (sys.executable, "-c", "from solid_node.cli import manage; manage()")
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
    candidate = _project_path(name, project_home)
    assert name is not None
    home = project_home.resolve()
    try:
        home.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise PreparationError("project-home", name, home, str(error)) from error
    if not home.is_dir():
        raise PreparationError("project-home", name, home, "workspace projects directory does not exist")
    return candidate


def read_project_runtime(name: str | None, *, project_home: Path) -> ProjectRuntimeSelection:
    """Read project-owned agent runtime choices without creating anything."""
    project_root = _project_path(name, project_home)
    source_path = project_root / "pyproject.toml"
    if not source_path.exists():
        return ProjectRuntimeSelection(project_root, source_path, {})
    if source_path.is_symlink() or not source_path.is_file():
        raise ProjectRuntimeError(source_path, "pyproject.toml must be a regular non-symlink file")
    try:
        with source_path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ProjectRuntimeError(source_path, f"invalid TOML: {error}") from error
    tool = document.get("tool", {})
    if not isinstance(tool, dict):
        raise ProjectRuntimeError(source_path, "tool must be a table")
    table = tool.get("solid-node-studio")
    if table is None:
        return ProjectRuntimeSelection(project_root, source_path, {})
    if not isinstance(table, dict):
        raise ProjectRuntimeError(source_path, "tool.solid-node-studio must be a table")
    unknown = set(table) - {"agents"}
    if unknown:
        raise ProjectRuntimeError(source_path, f"tool.solid-node-studio: unknown key {sorted(unknown)[0]!r}")
    raw_agents = table.get("agents", {})
    if not isinstance(raw_agents, dict):
        raise ProjectRuntimeError(source_path, "tool.solid-node-studio.agents must be a table")
    agents: dict[str, ProjectAgentRuntime] = {}
    for agent_id, raw in raw_agents.items():
        if not isinstance(agent_id, str) or not AGENT_ID.fullmatch(agent_id):
            raise ProjectRuntimeError(source_path, f"agent key {agent_id!r} must be lowercase kebab-case")
        if not isinstance(raw, str):
            raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} must be a string")
        agents[agent_id] = _parse_agent_runtime(agent_id, raw, source_path)
    return ProjectRuntimeSelection(project_root, source_path, agents)


def _project_path(name: str | None, project_home: Path) -> Path:
    if name is None or not PROJECT_NAME.fullmatch(name):
        raise PreparationError("project-name", name, None, "a lowercase kebab-case project name is required")
    home = project_home.resolve()
    if project_home.exists() and not project_home.is_dir():
        raise PreparationError("project-home", name, home, "workspace projects directory is not a directory")
    candidate = home / name
    if candidate.is_symlink():
        raise PreparationError("project-path", name, candidate, "project location must not be a symbolic link")
    resolved = candidate.resolve(strict=False)
    if resolved.parent != home:
        raise PreparationError("project-path", name, candidate, "project path escapes the workspace projects directory")
    if candidate.exists() and not candidate.is_dir():
        raise PreparationError("project-path", name, candidate, "project location is not a directory")
    return resolved


def _parse_agent_runtime(agent_id: str, raw: str, source_path: Path) -> ProjectAgentRuntime:
    parts = raw.split(":")
    if any(not part for part in parts):
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} contains an empty segment")
    backend = parts[0] if parts else ""
    if backend not in {"codex", "claude", "opencode"}:
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} names an unknown backend")
    expected = {2, 3} if backend in {"codex", "claude"} else {3, 4}
    if len(parts) not in expected:
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} has the wrong segment count")
    if backend == "opencode":
        _, provider, model, *tail = parts
    else:
        _, model, *tail = parts
        provider = None
    effort = tail[0] if tail else None
    if backend == "codex" and model not in CODEX_MODELS:
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} names an unsupported Codex model")
    if backend == "claude" and model not in CLAUDE_MODELS:
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} names an unsupported Claude model")
    supported_efforts = CODEX_EFFORTS if backend == "codex" else CLAUDE_EFFORTS if backend == "claude" else None
    if effort is not None and supported_efforts is not None and effort not in supported_efforts:
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} names an unsupported reasoning level")
    return ProjectAgentRuntime(backend, provider, model, effort, raw)


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
    solid_env = build_environment(shop_root)
    if created:
        package_name = name.replace("-", "_")
        with tempfile.TemporaryDirectory(prefix=f".{name}-", dir=project_home.resolve()) as temporary:
            staging_home = Path(temporary)
            staged_project = staging_home / package_name
            _run(
                (*_command(solid_command), "new", package_name),
                cwd=staging_home,
                stage="scaffold",
                name=name,
                project_root=project_root,
                extra_env=solid_env,
            )
            if not staged_project.is_dir():
                raise PreparationError("scaffold", name, project_root, "solid new did not create the normalized project scaffold")
            try:
                staged_project.rename(project_root)
            except OSError as error:
                raise PreparationError("scaffold", name, project_root, str(error)) from error
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

    viewer_bundle, viewer_api_version = _viewer_info(
        solid_command, name=name, project_root=project_root, extra_env=solid_env,
    )
    artifact_root = artifact_root_for(project_root)
    snapshot = artifact_root / "viewer.json"
    _run(
        build_command(solid_command),
        cwd=project_root,
        stage="build",
        name=name,
        project_root=project_root,
        extra_env=solid_env,
    )
    _validate_snapshot(snapshot, artifact_root, name, project_root)
    return PreparedProject(
        name=name,
        project_root=project_root,
        model=Path("root"),
        artifact_root=artifact_root,
        viewer_bundle=viewer_bundle,
        viewer_api_version=viewer_api_version,
        solid_command=_command(solid_command),
        build_environment=solid_env,
    )


def _viewer_info(
    solid_command: str | Sequence[str],
    *,
    name: str,
    project_root: Path,
    extra_env: dict[str, str] | None,
) -> tuple[Path, int]:
    result = _run(
        (*_command(solid_command), "viewer"),
        cwd=project_root,
        stage="viewer",
        name=name,
        project_root=project_root,
        extra_env=extra_env,
    )
    try:
        value = json.loads(result.stdout)
        path = Path(value["path"])
        api_version = value["apiVersion"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise PreparationError("viewer", name, project_root, "solid viewer returned malformed bundle metadata") from error
    if not isinstance(api_version, int) or isinstance(api_version, bool):
        raise PreparationError("viewer", name, project_root, "solid viewer returned a non-integer API version")
    if api_version < REQUIRED_VIEWER_API:
        raise PreparationError(
            "viewer", name, project_root,
            f"viewer API {REQUIRED_VIEWER_API} is required but installed viewer API is {api_version}",
        )
    if not path.is_file():
        raise PreparationError("viewer", name, project_root, f"viewer bundle is unavailable: {path}")
    return path, api_version


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
    # Publication now uses one real build directory. Resolve the candidate once
    # for containment; a later atomic rename cannot make this path escape it.
    published = artifact_root.resolve()
    for model in models:
        candidate = (artifact_root / model).resolve()
        if published not in candidate.parents or not candidate.is_file():
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
