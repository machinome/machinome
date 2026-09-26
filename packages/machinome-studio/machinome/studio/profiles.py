# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Validated, shop-owned runtime profiles loaded from package resources."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Literal

from .preparation import (
    CLAUDE_EFFORTS,
    CLAUDE_MODELS,
    ProjectRuntimeError,
    ProjectRuntimeSelection,
)


PROFILE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PROFILE_BACKENDS = ("claude",)
_TOP_LEVEL = {"schema_version", "user_label", "user_agent", "work_mode", "agents"}
_AGENT = {"id", "label", "prompt", "assigns", "reports_to", "backends"}
_RUNTIME = {"model", "effort", "tools"}
# These profile-owned capability names are resolved to floor MCP tools. A
# backend that cannot enforce a declared tool policy is not selectable.
_PROFILE_TOOLS = {"Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch", "OpenSpec"}


class ProfileError(ValueError):
    """A selected runtime profile is not safe to open."""


@dataclass(frozen=True)
class BackendRuntime:
    model: str
    effort: str
    tools: str | tuple[str, ...]
    backend: str = "claude"
    provider: str | None = None


@dataclass(frozen=True)
class ProfileSkill:
    """One allowlisted skill, resolved with the announcement it declares."""

    name: str
    description: str
    path: Path


@dataclass(frozen=True)
class ProfileAgent:
    id: str
    label: str
    prompt_path: Path
    skills: tuple[ProfileSkill, ...]
    assigns: tuple[str, ...]
    reports_to: str | None
    runtime: BackendRuntime | None
    backends: dict[str, BackendRuntime] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeProfile:
    id: str
    root: Path
    user_label: str
    user_agent_id: str
    work_mode: Literal["direct", "delegated"]
    agents: tuple[ProfileAgent, ...]
    ignored_agent_ids: tuple[str, ...] = ()

    @property
    def user_agent(self) -> ProfileAgent:
        return self.agent(self.user_agent_id)

    def agent(self, agent_id: str) -> ProfileAgent:
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        raise ProfileError(f"profile {self.id}: unknown agent {agent_id!r}")


def load_profile(
    profile_id: str | None,
    *,
    shop_root: Path,
    default: str | None = "fordesmac",
    selection: ProjectRuntimeSelection | None = None,
) -> RuntimeProfile:
    """Select and load one validated profile without project or backend side effects."""
    from_project = profile_id is None and selection is not None and selection.profile is not None
    if profile_id is not None:
        selected = profile_id
    elif from_project:
        assert selection is not None
        selected = selection.profile
    else:
        selected = default
    if selected is None:
        raise ProfileError("profile is required")
    try:
        return _load_profile(selected, shop_root=shop_root)
    except ProfileError as error:
        if from_project:
            assert selection is not None
            raise ProjectRuntimeError(
                selection.source_path,
                f"profile value {selected!r} cannot be loaded: {error}",
            ) from error
        raise


def _load_profile(selected: str, *, shop_root: Path) -> RuntimeProfile:
    """Load one named profile package from the running shop resources."""
    if not PROFILE_ID.fullmatch(selected):
        raise ProfileError(f"profile {selected!r} must be lowercase kebab-case")
    shop = shop_root.resolve()
    profiles_root = shop / "profiles"
    root = profiles_root / selected
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as error:
        raise ProfileError(f"profile {selected}: package is unavailable at {root}") from error
    if resolved_root.parent != profiles_root.resolve() or not resolved_root.is_dir():
        raise ProfileError(f"profile {selected}: package must be directly beneath profiles/")
    manifest = resolved_root / "profile.toml"
    if not manifest.is_file() or manifest.is_symlink():
        raise ProfileError(f"profile {selected}: profile.toml must be a contained regular file")
    try:
        with manifest.open("rb") as source:
            value = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ProfileError(f"profile {selected}: invalid profile.toml: {error}") from error
    _only(value, _TOP_LEVEL, f"profile {selected}")
    if value.get("schema_version") != 1:
        raise ProfileError(f"profile {selected}.schema_version must be 1")
    user_label = _string(value, "user_label", selected)
    user_agent_id = _id(_string(value, "user_agent", selected), f"profile {selected}.user_agent")
    work_mode = value.get("work_mode")
    if work_mode not in {"direct", "delegated"}:
        raise ProfileError(f"profile {selected}.work_mode must be direct or delegated")
    raw_agents = value.get("agents")
    if not isinstance(raw_agents, list) or not raw_agents:
        raise ProfileError(f"profile {selected}.agents must declare at least one standing agent")
    agents: list[ProfileAgent] = []
    ids: set[str] = set()
    labels: set[str] = set()
    raw_by_id: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(raw_agents):
        if not isinstance(raw, dict):
            raise ProfileError(f"profile {selected}.agents[{index}] must be a table")
        _only(raw, _AGENT, f"profile {selected}.agents[{index}]")
        agent_id = _id(_string(raw, "id", selected), f"profile {selected}.agents[{index}].id")
        label = _string(raw, "label", selected)
        if agent_id in ids:
            raise ProfileError(f"profile {selected}: duplicate agent id {agent_id!r}")
        if label in labels:
            raise ProfileError(f"profile {selected}: duplicate agent label {label!r}")
        ids.add(agent_id)
        labels.add(label)
        raw_by_id[agent_id] = raw
    if user_agent_id not in ids:
        raise ProfileError(f"profile {selected}.user_agent must name exactly one declared agent")
    for index, raw in enumerate(raw_agents):
        assert isinstance(raw, dict)
        agent_id = str(raw["id"])
        prompt = _contained_file(resolved_root, _string(raw, "prompt", selected), f"profile {selected}.{agent_id}.prompt")
        declared = _prompt_skills(prompt, selected, agent_id)
        skills = tuple(_skill(resolved_root, skill, selected) for skill in declared)
        assigns = _ids(raw.get("assigns", []), f"profile {selected}.{agent_id}.assigns")
        reports_to_value = raw.get("reports_to")
        reports_to = None if reports_to_value is None else _id(reports_to_value, f"profile {selected}.{agent_id}.reports_to")
        backend_settings = raw.get("backends")
        if not isinstance(backend_settings, dict):
            raise ProfileError(f"profile {selected}.{agent_id}.backends must declare every backend")
        _only(backend_settings, set(PROFILE_BACKENDS), f"profile {selected}.{agent_id}.backends")
        if set(backend_settings) != set(PROFILE_BACKENDS):
            raise ProfileError(f"profile {selected}.{agent_id}.backends must declare Claude")
        runtimes = {
            runtime_backend: _runtime(runtime_value, selected, agent_id, runtime_backend)
            for runtime_backend, runtime_value in backend_settings.items()
        }
        agents.append(ProfileAgent(agent_id, str(raw["label"]), prompt, skills, assigns, reports_to, None, runtimes))
    _topology(selected, work_mode, tuple(agents), ids, user_agent_id)
    return RuntimeProfile(selected, resolved_root, user_label, user_agent_id, work_mode, tuple(agents))


def resolve_profile_runtime(
    profile: RuntimeProfile,
    selection: ProjectRuntimeSelection | None = None,
) -> RuntimeProfile:
    """Merge project choices over trusted profile defaults per declared agent."""
    roster = {agent.id for agent in profile.agents}
    choices = selection.agents if selection is not None else {}
    ignored = tuple(sorted(set(choices) - roster))
    resolved: list[ProfileAgent] = []
    for agent in profile.agents:
        choice = choices.get(agent.id)
        if choice is None:
            runtime = agent.backends["claude"]
        elif choice.backend == "opencode":
            runtime = BackendRuntime(
                choice.model,
                choice.effort or "inherit",
                agent.backends["claude"].tools,
                backend="opencode",
                provider=choice.provider,
            )
        else:
            default_runtime = agent.backends[choice.backend]
            runtime = replace(
                default_runtime,
                model=choice.model,
                effort=choice.effort or default_runtime.effort,
                provider=choice.provider,
            )
        resolved.append(replace(agent, runtime=runtime))
    return replace(profile, agents=tuple(resolved), ignored_agent_ids=ignored)


def _only(value: dict[str, Any], permitted: set[str], context: str) -> None:
    unknown = set(value) - permitted
    if unknown:
        raise ProfileError(f"{context}: unknown key {sorted(unknown)[0]!r}")


def _string(value: dict[str, Any], key: str, profile: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ProfileError(f"profile {profile}.{key} must be a non-empty string")
    return item


def _id(value: Any, context: str) -> str:
    if not isinstance(value, str) or not PROFILE_ID.fullmatch(value):
        raise ProfileError(f"{context} must be lowercase kebab-case")
    return value


def _ids(value: Any, context: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ProfileError(f"{context} must be a list of agent IDs")
    parsed = tuple(_id(item, context) for item in value)
    if len(parsed) != len(set(parsed)):
        raise ProfileError(f"{context} contains duplicate agent IDs")
    return parsed


def _contained_file(root: Path, value: str, context: str) -> Path:
    candidate = root / value
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise ProfileError(f"{context} is missing: {value}") from error
    if root not in resolved.parents or candidate.is_symlink() or not resolved.is_file():
        raise ProfileError(f"{context} must be a regular file contained by its profile")
    return resolved


def _frontmatter(source: Path, context: str) -> dict[str, str]:
    """Read a Markdown file's leading `---` block as flat single-line fields."""
    lines = source.read_text().splitlines()
    if not lines or lines[0] != "---":
        raise ProfileError(f"{context} must have YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ProfileError(f"{context} has unterminated frontmatter") from error
    return dict(line.split(":", 1) for line in lines[1:end] if ":" in line)


def _prompt_skills(prompt: Path, profile: str, agent: str) -> tuple[str, ...]:
    fields = _frontmatter(prompt, f"profile {profile}.{agent}.prompt")
    if fields.get("name", "").strip() != agent:
        raise ProfileError(f"profile {profile}.{agent}.prompt frontmatter name must equal {agent!r}")
    skills = fields.get("skills")
    if skills is None or not skills.strip().startswith("[") or not skills.strip().endswith("]"):
        raise ProfileError(f"profile {profile}.{agent}.prompt frontmatter must declare skills")
    names = tuple(item.strip() for item in skills.strip()[1:-1].split(",") if item.strip())
    if any(not PROFILE_ID.fullmatch(name) for name in names) or len(names) != len(set(names)):
        raise ProfileError(f"profile {profile}.{agent}.prompt skills must be unique lowercase kebab-case names")
    return names


def _skill(root: Path, skill: str, profile: str) -> ProfileSkill:
    return _announcement(_skill_path(root, skill, profile), skill, profile)


def _skill_path(root: Path, skill: str, profile: str) -> Path:
    entry = root / "skills" / skill
    if not entry.is_symlink():
        candidate = (entry / "SKILL.md").resolve(strict=False)
        if root not in candidate.parents or not candidate.is_file():
            raise ProfileError(f"profile {profile}.skills.{skill} must be a contained local skill directory")
        return entry
    try:
        target = entry.resolve(strict=True)
    except OSError as error:
        raise ProfileError(f"profile {profile}.skills.{skill} is a broken link") from error
    shop = root.parent.parent
    expected_parent = shop / "shop-skills"
    if target.parent != expected_parent.resolve() or not target.is_dir() or not (target / "SKILL.md").is_file():
        raise ProfileError(f"profile {profile}.skills.{skill} must link directly to shop-skills/<skill>")
    return entry


def _announcement(path: Path, skill: str, profile: str) -> ProfileSkill:
    """Resolve the name and description a skill uses to announce itself.

    A session is offered its skills by name and description alone, so a skill
    that cannot describe itself cannot be chosen and must not reach a floor.
    """
    context = f"profile {profile}.skills.{skill}"
    fields = _frontmatter(path / "SKILL.md", context)
    if fields.get("name", "").strip() != skill:
        raise ProfileError(f"{context} frontmatter name must equal {skill!r}")
    description = fields.get("description", "").strip()
    if not description:
        raise ProfileError(f"{context} frontmatter must declare a non-empty description")
    return ProfileSkill(skill, description, path)


def _runtime(value: Any, profile: str, agent: str, backend: str) -> BackendRuntime:
    if not isinstance(value, dict):
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend} must be a table")
    _only(value, _RUNTIME, f"profile {profile}.{agent}.backends.{backend}")
    if set(value) != _RUNTIME:
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend} must declare model, effort, and tools")
    model, effort, tools = value["model"], value["effort"], value["tools"]
    if not isinstance(model, str) or not model:
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend}.model must be concrete or inherit")
    if backend == "claude" and model not in CLAUDE_MODELS | {"inherit"}:
        raise ProfileError(f"profile {profile}.{agent}.backends.claude.model is unsupported")
    if not isinstance(effort, str):
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend}.effort is unsupported")
    supported_efforts = CLAUDE_EFFORTS
    if effort not in supported_efforts | {"inherit"}:
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend}.effort is unsupported")
    # A Claude table declares the tools concretely: the declared list is the
    # whole authority its sessions hold, so there is nothing to inherit from.
    if backend == "claude" and not isinstance(tools, list):
        raise ProfileError(f"profile {profile}.{agent}.backends.claude.tools must be a list")
    if not (tools == "inherit" or (isinstance(tools, list) and all(isinstance(item, str) and item for item in tools))):
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend}.tools must be inherit or a list")
    if backend == "claude" and (
        len(tools) != len(set(tools)) or any(tool not in _PROFILE_TOOLS for tool in tools)
    ):
        raise ProfileError(f"profile {profile}.{agent}.backends.claude.tools is unsupported")
    return BackendRuntime(
        model,
        effort,
        tools if isinstance(tools, str) else tuple(tools),
        backend=backend,
    )


def _topology(profile: str, mode: str, agents: tuple[ProfileAgent, ...], ids: set[str], user_agent: str) -> None:
    edges: dict[str, tuple[str, ...]] = {}
    for agent in agents:
        if any(target not in ids or target == agent.id for target in agent.assigns):
            raise ProfileError(f"profile {profile}.{agent.id}.assigns references an undeclared agent")
        if agent.reports_to is not None and agent.reports_to not in ids:
            raise ProfileError(f"profile {profile}.{agent.id}.reports_to references an undeclared agent")
        if agent.reports_to is not None and agent.id not in next(item.assigns for item in agents if item.id == agent.reports_to):
            raise ProfileError(f"profile {profile}.{agent.id}.reports_to must also declare an assignment edge")
        edges[agent.id] = agent.assigns
    if mode == "direct":
        if len(agents) != 1 or agents[0].id != user_agent or agents[0].assigns or agents[0].reports_to:
            raise ProfileError(f"profile {profile}: direct mode requires one user-facing agent with no edges")
    else:
        roots = [agent for agent in agents if agent.reports_to is None]
        if len(roots) != 1 or roots[0].id != user_agent or any(agent.reports_to is None for agent in agents if agent.id != user_agent):
            raise ProfileError(f"profile {profile}: delegated mode requires user-facing root and reporting parents")
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(agent_id: str) -> None:
        if agent_id in visiting:
            raise ProfileError(f"profile {profile}: assignment edges must be acyclic")
        if agent_id in visited:
            return
        visiting.add(agent_id)
        for target in edges[agent_id]:
            visit(target)
        visiting.remove(agent_id)
        visited.add(agent_id)
    for agent in agents:
        visit(agent.id)
