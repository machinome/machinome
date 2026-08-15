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
from datetime import UTC, datetime
from pathlib import Path

from .screenshots import refresh_project_screenshot, screenshot_revision


LOWER_KEBAB_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
AGENT_ID = LOWER_KEBAB_ID
REQUIRED_VIEWER_API = 4
CLAUDE_MODELS = {"sonnet", "opus"}
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
    profile: str | None = None


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
    build_error: str | None = None

    def build_invocation(self) -> tuple[tuple[str, ...], dict[str, str] | None]:
        """The command and environment overlay that builds this project.

        The watcher rebuilds the same project the same way preparation
        first built it; carrying the invocation on the prepared project
        keeps one definition rather than two that can drift apart.
        """
        return build_command(self.solid_command), self.build_environment


@dataclass(frozen=True)
class ProjectListing:
    """One filesystem entry as presented by the project hub."""

    name: str
    openable: bool
    reason: str | None
    profile: str
    branch: str | None = None
    last_commit: str | None = None
    screenshot_revision: str | None = None

    def browser_value(self, *, state: str = "closed", session_id: str | None = None) -> dict[str, object]:
        return {
            "name": self.name,
            "openable": self.openable,
            "reason": self.reason,
            "profile": self.profile,
            "branch": self.branch,
            "last_commit": self.last_commit,
            "state": state,
            "session_id": session_id,
            "screenshot_revision": self.screenshot_revision,
        }


def artifact_root_for(project_root: Path) -> Path:
    """The project's single, atomically updated published build directory."""
    return project_root / "_build"


def build_command(solid_command: str | Sequence[str]) -> tuple[str, ...]:
    # No node reference: the framework resolves the project's model from
    # [tool.solid-node] in the project's pyproject.toml.
    return (*_command(solid_command), "build")


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


def shop_resource_root() -> Path:
    """Return resources belonging to the loaded shop package or source tree.

    This is deliberately derived from the imported module, not process cwd or
    Git metadata. A source worktree therefore uses its own files, while an
    installed plugin uses the files shipped beside its loaded ``floor``
    package.
    """
    return Path(__file__).resolve().parents[1]


def default_solid_command() -> tuple[str, ...]:
    """Use solid-node from the Python environment running the shop.

    Console-script lookup through ambient ``PATH`` can silently select a
    different Python installation. The shop and framework are installed into
    one environment, so binding the command to that interpreter's scripts
    directory preserves the selected framework without cwd or Git discovery.
    """
    return (str(Path(sys.executable).with_name("solid")),)


def list_projects(project_home: Path) -> list[ProjectListing]:
    """Describe every project directory in the working folder without mutating it."""
    home = project_home.resolve()
    if not home.exists():
        return []
    if not home.is_dir():
        raise PreparationError("project-home", None, home, "workspace projects directory is not a directory")
    directories = (entry for entry in home.iterdir() if entry.is_dir() and not entry.is_symlink())
    return [_project_listing(entry, home) for entry in sorted(directories, key=lambda item: item.name)]


def _project_listing(entry: Path, home: Path) -> ProjectListing:
    name = entry.name
    try:
        selection = read_project_runtime(name, project_home=home)
    except (PreparationError, ProjectRuntimeError) as error:
        return ProjectListing(name, False, str(error), "fordesmac")
    profile = selection.profile or "fordesmac"
    try:
        root = _run(
            ("git", "-C", str(entry), "rev-parse", "--show-toplevel"),
            stage="repository",
            name=name,
            project_root=entry,
        ).stdout.strip()
        if Path(root).resolve() != entry.resolve():
            raise PreparationError(
                "repository", name, entry,
                "location is not the exact root of an independent Git repository",
            )
        branch = _run(
            ("git", "-C", str(entry), "rev-parse", "--abbrev-ref", "HEAD"),
            stage="repository", name=name, project_root=entry,
        ).stdout.strip()
        timestamp = _run(
            ("git", "-C", str(entry), "log", "-1", "--format=%cI"),
            stage="repository", name=name, project_root=entry,
        ).stdout.strip()
        last_commit = datetime.fromisoformat(timestamp).astimezone(UTC).isoformat() if timestamp else None
    except (PreparationError, ValueError) as error:
        return ProjectListing(name, False, str(error), profile)
    return ProjectListing(name, True, None, profile, branch, last_commit, screenshot_revision(entry))


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


def verified_project_root(name: str | None, project_home: Path) -> Path:
    """Resolve only an exact direct-child project repository for serving."""
    root = resolve_project(name, project_home)
    assert name is not None
    _require_exact_repository(root, name)
    return root


def validate_new_project(name: str | None, project_home: Path) -> Path:
    """Validate a creation target before creating the working folder or project."""
    _validate_project_name(name)
    assert name is not None
    candidate = project_home.resolve() / name
    if candidate.exists() or candidate.is_symlink():
        raise PreparationError("project-name", name, candidate, "an entry with this name already exists")
    return _project_path(name, project_home)


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
    table = tool.get("libresolid-studio")
    if table is None:
        return ProjectRuntimeSelection(project_root, source_path, {})
    if not isinstance(table, dict):
        raise ProjectRuntimeError(source_path, "tool.libresolid-studio must be a table")
    unknown = set(table) - {"agents", "profile"}
    if unknown:
        raise ProjectRuntimeError(source_path, f"tool.libresolid-studio: unknown key {sorted(unknown)[0]!r}")
    profile = table.get("profile")
    if profile is not None and (not isinstance(profile, str) or not LOWER_KEBAB_ID.fullmatch(profile)):
        raise ProjectRuntimeError(
            source_path,
            f"profile value {profile!r} must be a lowercase kebab-case string",
        )
    raw_agents = table.get("agents", {})
    if not isinstance(raw_agents, dict):
        raise ProjectRuntimeError(source_path, "tool.libresolid-studio.agents must be a table")
    agents: dict[str, ProjectAgentRuntime] = {}
    for agent_id, raw in raw_agents.items():
        if not isinstance(agent_id, str) or not AGENT_ID.fullmatch(agent_id):
            raise ProjectRuntimeError(source_path, f"agent key {agent_id!r} must be lowercase kebab-case")
        if not isinstance(raw, str):
            raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} must be a string")
        agents[agent_id] = _parse_agent_runtime(agent_id, raw, source_path)
    return ProjectRuntimeSelection(project_root, source_path, agents, profile)


def _project_path(name: str | None, project_home: Path) -> Path:
    _validate_project_name(name)
    assert name is not None
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


def _validate_project_name(name: str | None) -> None:
    if (
        not isinstance(name, str)
        or not name
        or name in {".", ".."}
        or "/" in name
        or "\\" in name
        or "\0" in name
    ):
        raise PreparationError(
            "project-name",
            name,
            None,
            "project name must be one safe directory name without a path separator",
        )


def _parse_agent_runtime(agent_id: str, raw: str, source_path: Path) -> ProjectAgentRuntime:
    parts = raw.split(":")
    if any(not part for part in parts):
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} contains an empty segment")
    backend = parts[0] if parts else ""
    if backend not in {"claude", "opencode"}:
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} names an unknown backend")
    expected = {2, 3} if backend == "claude" else {3, 4}
    if len(parts) not in expected:
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} has the wrong segment count")
    if backend == "opencode":
        _, provider, model, *tail = parts
    else:
        _, model, *tail = parts
        provider = None
    effort = tail[0] if tail else None
    if backend == "claude" and model not in CLAUDE_MODELS:
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} names an unsupported Claude model")
    supported_efforts = CLAUDE_EFFORTS if backend == "claude" else None
    if effort is not None and supported_efforts is not None and effort not in supported_efforts:
        raise ProjectRuntimeError(source_path, f"agent {agent_id!r} value {raw!r} names an unsupported reasoning level")
    return ProjectAgentRuntime(backend, provider, model, effort, raw)


def prepare_project(
    name: str | None,
    *,
    project_home: Path,
    solid_command: str | Sequence[str],
    profile: str | None = None,
    allow_build_failure: bool = False,
) -> PreparedProject:
    project_root = resolve_project(name, project_home)
    assert name is not None
    created = not project_root.exists()
    solid_env = None
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
        if profile is not None:
            _write_project_profile(project_root, profile)
        _run(("git", "init", "-q", "-b", "main", str(project_root)), stage="git-init", name=name, project_root=project_root)
        _require_exact_repository(project_root, name)
    else:
        _require_exact_repository(project_root, name)

    viewer_bundle, viewer_api_version = _viewer_info(
        solid_command, name=name, project_root=project_root, extra_env=solid_env,
    )
    artifact_root = artifact_root_for(project_root)
    snapshot = artifact_root / "viewer.json"
    build_error: str | None = None
    try:
        _run(
            build_command(solid_command),
            cwd=project_root,
            stage="build",
            name=name,
            project_root=project_root,
            extra_env=solid_env,
        )
        _validate_snapshot(snapshot, artifact_root, name, project_root)
        # A thumbnail is an optional presentation artifact.  The model build
        # has already succeeded; do not fold a renderer problem into it.
        refresh_project_screenshot(project_root, _command(solid_command), extra_environment=solid_env)
    except PreparationError as error:
        if not allow_build_failure:
            raise
        build_error = str(error)
    if created:
        _run(("git", "-C", str(project_root), "add", "--all"), stage="git-add", name=name, project_root=project_root)
        _run(
            ("git", "-C", str(project_root), "commit", "-q", "-m", "Initial solid-node scaffold"),
            stage="git-commit",
            name=name,
            project_root=project_root,
        )
    return PreparedProject(
        name=name,
        project_root=project_root,
        model=Path("root"),
        artifact_root=artifact_root,
        viewer_bundle=viewer_bundle,
        viewer_api_version=viewer_api_version,
        solid_command=_command(solid_command),
        build_environment=solid_env,
        build_error=build_error,
    )


def _write_project_profile(project_root: Path, profile: str) -> None:
    if not LOWER_KEBAB_ID.fullmatch(profile):
        raise PreparationError("profile", project_root.name, project_root, "profile must be lowercase kebab-case")
    path = project_root / "pyproject.toml"
    try:
        source = path.read_text() if path.exists() else ""
        if "[tool.libresolid-studio]" in source:
            marker = "[tool.libresolid-studio]"
            before, after = source.split(marker, 1)
            if re.search(r"(?m)^profile\s*=", after.split("\n[", 1)[0]):
                raise PreparationError("profile", project_root.name, project_root, "scaffold already declares a runtime profile")
            source = f'{before}{marker}\nprofile = "{profile}"{after}'
        else:
            separator = "" if not source else ("" if source.endswith("\n\n") else "\n" if source.endswith("\n") else "\n\n")
            source = f'{source}{separator}[tool.libresolid-studio]\nprofile = "{profile}"\n'
        path.write_text(source)
    except OSError as error:
        raise PreparationError("profile", project_root.name, project_root, str(error)) from error


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
