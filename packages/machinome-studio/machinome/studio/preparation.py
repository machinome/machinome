# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Fail-closed preparation of one named workspace project."""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from itertools import islice
from pathlib import Path

from .screenshots import refresh_project_screenshot, screenshot_revision


LOGGER = logging.getLogger(__name__)

LOWER_KEBAB_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
AGENT_ID = LOWER_KEBAB_ID
REQUIRED_VIEWER_API = 4
CLAUDE_MODELS = {"sonnet", "opus", "fable"}
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
class ViewerBundle:
    """The installed framework's viewer bundle and the API it implements.

    This describes the framework installed beside the shop rather than any
    project, so one running shop holds one of these for every session it opens.
    """

    path: Path
    api_version: int


@dataclass(frozen=True)
class BuildOutcome:
    """What one build did to a project's publication.

    ``published`` is the answer to the only question the open path needs: did
    this build put something in front of the maker that was not there before.
    """

    published: bool = False
    error: str | None = None


@dataclass(frozen=True)
class PreparedProject:
    name: str
    project_root: Path
    model: Path
    artifact_root: Path
    project_model: str | None = None
    #: The project-relative file that declares this model's root assembly.
    model_source: str | None = None
    viewer_bundle: Path | None = None
    viewer_api_version: int | None = None
    solid_command: tuple[str, ...] = ()
    build_environment: dict[str, str] | None = None
    build_error: str | None = None
    created: bool = False

    def build_invocation(self) -> tuple[tuple[str, ...], dict[str, str] | None]:
        """The command and environment overlay that builds this project.

        The watcher rebuilds the same project the same way preparation
        first built it; carrying the invocation on the prepared project
        keeps one definition rather than two that can drift apart.
        """
        return build_command(self.solid_command, self.project_model), self.build_environment


@dataclass(frozen=True)
class HubEntry:
    """One openable thing in the hub: a project repository and one of its models.

    ``path`` is the entry's identity everywhere the shop names it -- the
    browser location, the open request, hub state, the session -- and is always
    relative to the working folder. ``model`` names one model the project's
    manifest declares; ``None`` means the project is listed as a single project
    and builds the model it defaults to.
    """

    path: str
    project_root: Path
    model: str | None = None

    @property
    def name(self) -> str:
        return self.path.rsplit("/", 1)[-1]

    @property
    def folder(self) -> str:
        head, _, _ = self.path.rpartition("/")
        return head


@dataclass(frozen=True)
class ProjectListing:
    """One openable or unopenable project as presented by the project hub."""

    path: str
    openable: bool
    reason: str | None
    profile: str
    branch: str | None = None
    last_commit: str | None = None
    screenshot_revision: str | None = None

    @property
    def name(self) -> str:
        return self.path.rsplit("/", 1)[-1]

    def browser_value(self, *, state: str = "closed", session_id: str | None = None) -> dict[str, object]:
        return {
            "kind": "project",
            "path": self.path,
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


@dataclass(frozen=True)
class EntryPreview:
    """The picture of one hub entry, named by the entry that owns it.

    A folder card standing for a multi-model project shows these, and the
    browser fetches each one from the same screenshot route that serves the
    model's own project card, so the two never disagree.
    """

    path: str
    revision: str | None

    def browser_value(self) -> dict[str, object]:
        return {"path": self.path, "revision": self.revision}


@dataclass(frozen=True)
class FolderListing:
    """One directory the maker can enter, and what it holds.

    ``projects`` counts the project repositories anywhere below it, which is
    what the maker is looking for when deciding whether to go in. A repository
    declaring several models is one project here and a folder of models once
    entered.

    ``previews`` is what tells the two kinds of folder apart on the hub. A
    multi-model project is one machine and carries the pictures of the first
    few models it declares; a directory grouping unrelated repositories owns no
    model and carries none.
    """

    path: str
    projects: int
    previews: tuple[EntryPreview, ...] = ()

    @property
    def name(self) -> str:
        return self.path.rsplit("/", 1)[-1]

    def browser_value(self) -> dict[str, object]:
        return {
            "kind": "folder",
            "path": self.path,
            "name": self.name,
            "projects": self.projects,
            "previews": [preview.browser_value() for preview in self.previews],
        }


@dataclass(frozen=True)
class ResolvedModel:
    """What the framework says about the one model a session opens on."""

    artifact_root: Path
    #: The project-relative file declaring the model's root class, when the
    #: declared reference resolves to a file inside the project.
    source: str | None


def resolve_model(
    solid_command: str | Sequence[str],
    project_root: Path,
    *,
    name: str | None = None,
    model: str | None = None,
    extra_env: dict[str, str] | None = None,
) -> ResolvedModel:
    """Ask the framework where one of this project's models publishes.

    A project that declares named models gives each one its own directory
    under `_build`, and only the framework knows which. The shop asks and
    reads the answer rather than spelling a path of its own: the directory it
    is given is the one atomically updated publication it serves, watches and
    packages, whatever layout the manifest chose. Without a named model the
    answer is the project's default; with one it is that model's, so two
    sessions on one repository never serve each other's publication.

    The same answer carries the model's declared reference, from which the
    file holding its root assembly is read: the maker who opens Code is
    looking at that model, so that is the file already open.
    """
    result = _run(
        (*_command(solid_command), "models", "--json"),
        cwd=project_root,
        stage="models",
        name=name,
        project_root=project_root,
        extra_env=extra_env,
    )
    try:
        report = json.loads(result.stdout)
        wanted = (
            (lambda declared: declared["name"] == model) if model
            else (lambda declared: declared["default"])
        )
        declared = next(item for item in report["models"] if wanted(item))
        build_dir = Path(declared["build_dir"])
    except (json.JSONDecodeError, KeyError, TypeError, StopIteration) as error:
        described = f"model {model!r}" if model else "a default model"
        raise PreparationError(
            "models", name, project_root,
            f"solid models did not report a build directory for {described}",
        ) from error
    artifact_root = build_dir.resolve()
    if project_root.resolve() not in artifact_root.parents:
        raise PreparationError(
            "models", name, project_root,
            f"model build directory is outside the project: {build_dir}",
        )
    return ResolvedModel(artifact_root, _model_source(project_root, declared.get("reference")))


def _model_source(project_root: Path, reference: object) -> str | None:
    """The file a `package.module:Class` reference is written in, if it exists.

    A reference the framework accepts may still be spelled in ways this shop
    cannot follow -- a namespace package, a class the manifest names through
    an alias -- so a reference that resolves to nothing is not an error; the
    Code area simply opens on no file.
    """
    if not isinstance(reference, str) or ":" not in reference:
        return None
    module = reference.partition(":")[0].strip()
    if not module or module.startswith(".") or "/" in module or "\\" in module:
        return None
    parts = module.split(".")
    if not all(part.isidentifier() for part in parts):
        return None
    root = project_root.resolve()
    for candidate in (f"{'/'.join(parts)}.py", f"{'/'.join(parts)}/__init__.py"):
        target = root / candidate
        if target.is_file() and root in target.parents:
            return candidate
    return None


def build_command(solid_command: str | Sequence[str], model: str | None = None) -> tuple[str, ...]:
    # Without a model the framework resolves the project's default from
    # [tool.solid-node] in the project's pyproject.toml. A session opened on
    # one declared model names it, so it builds its own and not a sibling's.
    return (*_command(solid_command), "build", *([model] if model else ()))


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


SKIPPED_DIRECTORIES = {".git", "_build", "node_modules", "__pycache__", ".venv"}


def declared_models(project_root: Path) -> tuple[str, ...]:
    """The model names the project's manifest declares, in declaration order.

    Read straight from the manifest rather than through ``solid models`` so
    that listing a folder of twenty projects costs no subprocess. The build
    directory of a model still comes from the framework, once, when the entry
    is prepared.
    """
    path = project_root / "pyproject.toml"
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError):
        return ()
    tool = document.get("tool")
    table = tool.get("solid-node") if isinstance(tool, dict) else None
    models = table.get("models") if isinstance(table, dict) else None
    if not isinstance(models, dict):
        return ()
    return tuple(name for name in models if isinstance(name, str) and name)


def is_repository_root(path: Path) -> bool:
    """Whether this exact directory is the root of its own Git repository."""
    return (path / ".git").exists()


def holds_project(path: Path) -> bool:
    """Whether any project repository exists below this directory.

    The walk stops descending as soon as a branch turns out to be a repository
    root, because everything inside one belongs to that project rather than to
    the catalogue, and stops entirely at the first one it finds.
    """
    for entry in _child_directories(path):
        if is_repository_root(entry) or holds_project(entry):
            return True
    return False


def count_projects(path: Path) -> int:
    """How many project repositories live below this directory."""
    found = 0
    for entry in _child_directories(path):
        found += 1 if is_repository_root(entry) else count_projects(entry)
    return found


def _child_directories(path: Path) -> Iterator[Path]:
    try:
        entries = sorted(path.iterdir(), key=lambda item: item.name)
    except OSError:
        return
    for entry in entries:
        if entry.name in SKIPPED_DIRECTORIES or entry.is_symlink() or not entry.is_dir():
            continue
        yield entry


def resolve_folder(folder: str | None, project_home: Path) -> Path:
    """Resolve the directory whose entries the hub is listing.

    An empty path is the working folder itself. Every other path is walked one
    safe segment at a time so nothing outside the working folder is ever
    touched, whatever the caller sent.
    """
    home = project_home.resolve()
    if not folder:
        return home
    path = home
    for segment in _entry_segments(folder):
        path = _child(path, segment, folder)
        if not path.is_dir():
            raise PreparationError("entry-path", folder, path, "folder is not a directory")
    return path


def resolve_entry(path: str | None, project_home: Path) -> HubEntry:
    """Resolve one openable entry path to its project repository and model.

    The walk stops at the first directory that is a repository root: everything
    before it is catalogue, and the one segment that may follow it names a
    model the project declares. That is what keeps a model name from ever
    colliding with a directory inside the same repository.
    """
    segments = _entry_segments(path)
    assert path is not None
    home = project_home.resolve()
    walked = home
    for index, segment in enumerate(segments):
        walked = _child(walked, segment, path)
        if not walked.is_dir():
            raise PreparationError("entry-path", path, walked, "project location is not a directory")
        if not is_repository_root(walked):
            continue
        rest = segments[index + 1:]
        entry_path = "/".join(segments[: index + 1])
        if not rest:
            return HubEntry(entry_path, walked)
        if len(rest) > 1:
            raise PreparationError("entry-path", path, walked, "an entry names one model of one project")
        models = declared_models(walked)
        if rest[0] not in models:
            raise PreparationError(
                "entry-path", path, walked,
                f"{walked.name} declares no model named {rest[0]!r}",
            )
        return HubEntry(f"{entry_path}/{rest[0]}", walked, rest[0])
    raise PreparationError("entry-path", path, walked, "location is not a project repository")


def new_entry(folder: str | None, name: str | None, project_home: Path) -> HubEntry:
    """The entry a project would have if it were created here, unverified."""
    _validate_project_name(name)
    assert name is not None
    home = project_home.resolve()
    if not folder:
        # A first launch names a project before the working folder exists.
        try:
            home.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise PreparationError("project-home", name, home, str(error)) from error
    parent = resolve_folder(folder, project_home)
    if parent != home and is_repository_root(parent):
        raise PreparationError("entry-path", name, parent, "a project cannot be created inside a project")
    project_root = _child(parent, name, name)
    return HubEntry(str(project_root.relative_to(home)).replace(os.sep, "/"), project_root)


def _child(parent: Path, segment: str, requested: str | None) -> Path:
    """One safe step deeper, never leaving the directory it starts from."""
    candidate = parent / segment
    if candidate.is_symlink():
        raise PreparationError("entry-path", requested, candidate, "project location must not be a symbolic link")
    resolved = candidate.resolve(strict=False)
    if resolved.parent != parent.resolve():
        raise PreparationError("entry-path", requested, candidate, "entry path escapes the workspace projects directory")
    return resolved


def _entry_segments(path: str | None) -> tuple[str, ...]:
    if not isinstance(path, str) or not path:
        raise PreparationError("entry-path", path, None, "an entry path names at least one directory")
    segments = tuple(path.split("/"))
    for segment in segments:
        if not segment or segment in {".", ".."} or "\\" in segment or "\0" in segment:
            raise PreparationError(
                "entry-path", path, None,
                "an entry path is safe directory names separated by /",
            )
    return segments


def list_folder(project_home: Path, folder: str | None = "") -> list[ProjectListing | FolderListing]:
    """Describe the entries of one folder without mutating anything.

    A repository declaring several models is listed as a folder of its models;
    a directory holding projects below it is listed as a folder of those; a
    directory that is neither is listed with the reason it cannot be opened.
    """
    home = project_home.resolve()
    if not home.exists():
        return []
    if not home.is_dir():
        raise PreparationError("project-home", None, home, "workspace projects directory is not a directory")
    parent = resolve_folder(folder, project_home)
    prefix = f"{folder}/" if folder else ""
    if parent != home and is_repository_root(parent):
        return [
            _project_listing(parent, f"{folder}/{model}", model=model)
            for model in declared_models(parent)
        ]
    folders: list[FolderListing] = []
    projects: list[ProjectListing] = []
    for entry in _child_directories(parent):
        path = f"{prefix}{entry.name}"
        if is_repository_root(entry):
            models = declared_models(entry)
            if len(models) > 1:
                folders.append(FolderListing(path, len(models), _model_previews(entry, path, models)))
            else:
                projects.append(_project_listing(entry, path))
        elif holds_project(entry):
            folders.append(FolderListing(path, count_projects(entry), _folder_previews(entry, path)))
        else:
            projects.append(_project_listing(entry, path))
    return [*folders, *projects]


PREVIEWED_ENTRIES = 3


def _model_previews(entry: Path, path: str, models: Sequence[str]) -> tuple[EntryPreview, ...]:
    """The pictures a multi-model project's folder card stands on.

    Only the first few declared models are previewed, in declaration order, so
    a card is the same shape whatever the project declares. A model with no
    picture yet still gets an entry, because the card says how many models it
    stands for.
    """
    return tuple(
        EntryPreview(f"{path}/{model}", screenshot_revision(entry, model))
        for model in models[:PREVIEWED_ENTRIES]
    )


def _folder_previews(directory: Path, path: str) -> tuple[EntryPreview, ...]:
    """The pictures a grouping folder's card stands on.

    Such a folder declares no model of its own, so it stands on the first
    entries it holds instead. The walk stops as soon as the card is full,
    which is what keeps listing a folder of two hundred projects as cheap as
    listing a folder of three.
    """
    return tuple(islice(_previewable_entries(directory, path), PREVIEWED_ENTRIES))


def _previewable_entries(directory: Path, path: str) -> Iterator[EntryPreview]:
    """Every openable entry below this directory, one at a time.

    The order is the order the hub itself lists them in: folders first, in
    name order, each descended into as it is reached, then the projects the
    directory holds directly. Yielding lazily is what lets the caller stop
    after the few it shows.
    """
    prefix = f"{path}/" if path else ""
    projects: list[EntryPreview] = []
    for entry in _child_directories(directory):
        child = f"{prefix}{entry.name}"
        if is_repository_root(entry):
            models = declared_models(entry)
            if len(models) > 1:
                yield from (
                    EntryPreview(f"{child}/{model}", screenshot_revision(entry, model))
                    for model in models
                )
            else:
                projects.append(EntryPreview(child, screenshot_revision(entry)))
        else:
            yield from _previewable_entries(entry, child)
    yield from projects


def _project_listing(entry: Path, path: str, *, model: str | None = None) -> ProjectListing:
    try:
        selection = read_project_runtime(entry)
    except (PreparationError, ProjectRuntimeError) as error:
        return ProjectListing(path, False, str(error), "fordesmac")
    profile = selection.profile or "fordesmac"
    name = entry.name
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
        return ProjectListing(path, False, str(error), profile)
    return ProjectListing(
        path, True, None, profile, branch, last_commit,
        screenshot_revision(entry, model),
    )


def verified_project_root(path: str | None, project_home: Path) -> Path:
    """Resolve only an exact project repository, for serving one of its files."""
    entry = resolve_entry(path, project_home)
    _require_exact_repository(entry.project_root, entry.path)
    return entry.project_root


def validate_new_project(folder: str | None, name: str | None, project_home: Path) -> HubEntry:
    """Validate a creation target before creating the working folder or project."""
    entry = new_entry(folder, name, project_home)
    if entry.project_root.exists() or entry.project_root.is_symlink():
        raise PreparationError(
            "project-name", name, entry.project_root,
            "an entry with this name already exists",
        )
    return entry


def read_project_runtime(project_root: Path) -> ProjectRuntimeSelection:
    """Read project-owned agent runtime choices without creating anything."""
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
    entry: HubEntry,
    *,
    solid_command: str | Sequence[str],
    profile: str | None = None,
    viewer: ViewerBundle | None = None,
) -> PreparedProject:
    """Verify and — when it is new — scaffold the entry's project repository.

    This is everything that must hold before an agent may touch the project
    and nothing that produces a model, so the repository boundary gate is
    passed before a session exists whether or not its build is awaited.
    ``build_project`` produces the model, and ``commit_new_project`` records a
    newly created one.

    The entry carries the model this session owns, so the artifact root
    resolved here is that model's own publication and never a sibling's.
    """
    project_root = entry.project_root
    name = entry.path
    created = not project_root.exists()
    solid_env = None
    if created:
        package_name = project_root.name.replace("-", "_")
        with tempfile.TemporaryDirectory(prefix=f".{project_root.name}-", dir=project_root.parent) as temporary:
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

    bundle = viewer if viewer is not None else resolve_viewer_bundle(solid_command, extra_env=solid_env)
    resolved = resolve_model(
        solid_command, project_root, name=name, model=entry.model, extra_env=solid_env,
    )
    return PreparedProject(
        name=name,
        project_root=project_root,
        model=Path("root"),
        artifact_root=resolved.artifact_root,
        model_source=resolved.source,
        project_model=entry.model,
        viewer_bundle=bundle.path,
        viewer_api_version=bundle.api_version,
        solid_command=_command(solid_command),
        build_environment=solid_env,
        created=created,
    )


def build_project(
    prepared: PreparedProject,
    *,
    allow_failure: bool = False,
    watched: bool = False,
) -> BuildOutcome:
    """Build the project and keep its preview in step with what it published.

    Publication is decided from the content of the viewer document, not its
    timestamp: the framework rewrites that document only when the model
    differs, while an atomic write gives a fresh mtime whenever it writes.
    Reading one small file is nothing beside the render it can save, and a
    render that cannot produce different bytes is the largest avoidable cost
    of opening a project.

    ``watched`` says a live ``ArtifactWatcher`` is already refreshing the
    preview for whatever this build publishes, so the only render left here is
    the one owed to a project that has no valid preview at all.
    """
    command, environment = prepared.build_invocation()
    snapshot = prepared.artifact_root / "viewer.json"
    before = _publication_digest(snapshot)
    try:
        _run(
            command,
            cwd=prepared.project_root,
            stage="build",
            name=prepared.name,
            project_root=prepared.project_root,
            extra_env=environment,
        )
        _validate_snapshot(snapshot, prepared.artifact_root, prepared.name, prepared.project_root)
    except PreparationError as error:
        if not allow_failure:
            raise
        return BuildOutcome(error=str(error))
    published = _publication_digest(snapshot) != before
    if (published and not watched) or screenshot_revision(prepared.project_root, prepared.project_model) is None:
        # A thumbnail is an optional presentation artifact.  The model build
        # has already succeeded; do not fold a renderer problem into it. Say
        # what went wrong all the same: a renderer that cannot run is
        # otherwise indistinguishable from a project nobody photographed.
        result = refresh_project_screenshot(
            prepared.project_root,
            prepared.solid_command,
            model=prepared.project_model,
            extra_environment=prepared.build_environment,
        )
        if result.warning:
            LOGGER.warning(
                "no model preview for %s: %s", prepared.name, result.warning,
            )
    return BuildOutcome(published=published)


def commit_new_project(prepared: PreparedProject) -> None:
    """Record a created project's scaffold and the first model built from it.

    Creation commits after its build so a new project's first commit holds it
    as it was first published, preview included. An existing project's build
    output is never staged by the shop.
    """
    if not prepared.created:
        return
    project_root = prepared.project_root
    _run(
        ("git", "-C", str(project_root), "add", "--all"),
        stage="git-add",
        name=prepared.name,
        project_root=project_root,
    )
    _run(
        ("git", "-C", str(project_root), "commit", "-q", "-m", "Initial solid-node scaffold"),
        stage="git-commit",
        name=prepared.name,
        project_root=project_root,
    )


def has_complete_publication(prepared: PreparedProject) -> bool:
    """Whether a complete, valid publication is already on disk to present."""
    try:
        _validate_snapshot(
            prepared.artifact_root / "viewer.json",
            prepared.artifact_root,
            prepared.name,
            prepared.project_root,
        )
    except PreparationError:
        return False
    return True


def _publication_digest(snapshot: Path) -> str | None:
    """Identify the published document; absent is an answer, not a failure."""
    try:
        return sha256(snapshot.read_bytes()).hexdigest()
    except OSError:
        return None


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


def resolve_viewer_bundle(
    solid_command: str | Sequence[str],
    *,
    extra_env: dict[str, str] | None = None,
) -> ViewerBundle:
    """Ask the framework which viewer bundle it installed.

    The framework reports its own installed bundle, so the question has no
    project in it and its answer cannot differ between projects or between
    opens. Asking it once per running shop changes when it is asked, never the
    answer or its consequence: an unusable installation still fails the open.
    """
    result = _run(
        (*_command(solid_command), "viewer"),
        stage="viewer",
        name=None,
        project_root=None,
        extra_env=extra_env,
    )
    try:
        value = json.loads(result.stdout)
        path = Path(value["path"])
        api_version = value["apiVersion"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise PreparationError("viewer", None, None, "solid viewer returned malformed bundle metadata") from error
    if not isinstance(api_version, int) or isinstance(api_version, bool):
        raise PreparationError("viewer", None, None, "solid viewer returned a non-integer API version")
    if api_version < REQUIRED_VIEWER_API:
        raise PreparationError(
            "viewer", None, None,
            f"viewer API {REQUIRED_VIEWER_API} is required but installed viewer API is {api_version}",
        )
    if not path.is_file():
        raise PreparationError("viewer", None, None, f"viewer bundle is unavailable: {path}")
    return ViewerBundle(path, api_version)


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
