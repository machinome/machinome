"""Validated, repository-owned runtime profiles for the shop floor."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


PROFILE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
BACKENDS = ("codex", "claude", "hermes", "opencode")
PROFILE_BACKENDS = ("codex", "claude", "hermes")
_TOP_LEVEL = {"schema_version", "user_label", "user_agent", "work_mode", "agents"}
_AGENT = {"id", "label", "prompt", "assigns", "reports_to", "backends"}
_RUNTIME = {"model", "effort", "tools"}
_CLAUDE_RUNTIME = _RUNTIME | {"permission"}
_EFFORTS = {"low", "medium", "high", "xhigh", "max", "ultra"}
_CODEX_MODELS = {"gpt-5.6-terra", "gpt-5.6-sol", "gpt-5.3-codex-spark"}
_CLAUDE_MODELS = {"sonnet", "opus"}
_CLAUDE_EFFORTS = {"low", "medium", "high"}
_CLAUDE_TOOLS = {"Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch"}


class ProfileError(ValueError):
    """A selected runtime profile is not safe to open."""


@dataclass(frozen=True)
class BackendRuntime:
    model: str
    effort: str
    tools: str | tuple[str, ...]
    permission: str = "inherit"


@dataclass(frozen=True)
class ProfileAgent:
    id: str
    label: str
    prompt_path: Path
    skill_paths: tuple[Path, ...]
    assigns: tuple[str, ...]
    reports_to: str | None
    runtime: BackendRuntime


@dataclass(frozen=True)
class RuntimeProfile:
    id: str
    root: Path
    user_label: str
    user_agent_id: str
    work_mode: Literal["direct", "delegated"]
    agents: tuple[ProfileAgent, ...]
    backend: str

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
    backend: str,
    default: str | None = "builder",
) -> RuntimeProfile:
    """Load one fully validated profile without touching a project or backend."""
    selected = default if profile_id is None else profile_id
    if selected is None:
        raise ProfileError("profile is required")
    if not PROFILE_ID.fullmatch(selected):
        raise ProfileError(f"profile {selected!r} must be lowercase kebab-case")
    if backend not in BACKENDS:
        raise ProfileError(f"profile {selected}: unsupported backend {backend!r}")
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
        skills = _prompt_skills(prompt, selected, agent_id)
        skill_paths = tuple(_skill_path(resolved_root, skill, selected) for skill in skills)
        assigns = _ids(raw.get("assigns", []), f"profile {selected}.{agent_id}.assigns")
        reports_to_value = raw.get("reports_to")
        reports_to = None if reports_to_value is None else _id(reports_to_value, f"profile {selected}.{agent_id}.reports_to")
        backend_settings = raw.get("backends")
        if not isinstance(backend_settings, dict):
            raise ProfileError(f"profile {selected}.{agent_id}.backends must declare every backend")
        _only(backend_settings, set(PROFILE_BACKENDS), f"profile {selected}.{agent_id}.backends")
        if set(backend_settings) != set(PROFILE_BACKENDS):
            raise ProfileError(f"profile {selected}.{agent_id}.backends must declare Codex, Claude, and Hermes")
        for runtime_backend, runtime_value in backend_settings.items():
            _runtime(runtime_value, selected, agent_id, runtime_backend)
        runtime = (
            BackendRuntime("inherit", "inherit", "inherit")
            if backend == "opencode"
            else _runtime(backend_settings[backend], selected, agent_id, backend)
        )
        agents.append(ProfileAgent(agent_id, str(raw["label"]), prompt, skill_paths, assigns, reports_to, runtime))
    _topology(selected, work_mode, tuple(agents), ids, user_agent_id)
    return RuntimeProfile(selected, resolved_root, user_label, user_agent_id, work_mode, tuple(agents), backend)


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


def _prompt_skills(prompt: Path, profile: str, agent: str) -> tuple[str, ...]:
    lines = prompt.read_text().splitlines()
    if not lines or lines[0] != "---":
        raise ProfileError(f"profile {profile}.{agent}.prompt must have YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ProfileError(f"profile {profile}.{agent}.prompt has unterminated frontmatter") from error
    fields = dict(line.split(":", 1) for line in lines[1:end] if ":" in line)
    if fields.get("name", "").strip() != agent:
        raise ProfileError(f"profile {profile}.{agent}.prompt frontmatter name must equal {agent!r}")
    skills = fields.get("skills")
    if skills is None or not skills.strip().startswith("[") or not skills.strip().endswith("]"):
        raise ProfileError(f"profile {profile}.{agent}.prompt frontmatter must declare skills")
    names = tuple(item.strip() for item in skills.strip()[1:-1].split(",") if item.strip())
    if any(not PROFILE_ID.fullmatch(name) for name in names) or len(names) != len(set(names)):
        raise ProfileError(f"profile {profile}.{agent}.prompt skills must be unique lowercase kebab-case names")
    return names


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


def _runtime(value: Any, profile: str, agent: str, backend: str) -> BackendRuntime:
    if not isinstance(value, dict):
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend} must be a table")
    fields = _CLAUDE_RUNTIME if backend == "claude" else _RUNTIME
    _only(value, fields, f"profile {profile}.{agent}.backends.{backend}")
    if set(value) != fields:
        suffix = ", effort, tools, and permission" if backend == "claude" else ", effort, and tools"
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend} must declare model{suffix}")
    model, effort, tools = value["model"], value["effort"], value["tools"]
    permission = value.get("permission", "inherit")
    if not isinstance(model, str) or not model:
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend}.model must be concrete or inherit")
    if backend == "codex" and model not in _CODEX_MODELS | {"inherit"}:
        raise ProfileError(f"profile {profile}.{agent}.backends.codex.model is unsupported")
    if backend == "claude" and model not in _CLAUDE_MODELS | {"inherit"}:
        raise ProfileError(f"profile {profile}.{agent}.backends.claude.model is unsupported")
    if not isinstance(effort, str):
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend}.effort is unsupported")
    supported_efforts = _CLAUDE_EFFORTS if backend == "claude" else _EFFORTS
    if effort not in supported_efforts | {"inherit"}:
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend}.effort is unsupported")
    if not (tools == "inherit" or (isinstance(tools, list) and all(isinstance(item, str) and item for item in tools))):
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend}.tools must be inherit or a list")
    if backend in {"codex", "hermes"} and tools != "inherit":
        raise ProfileError(f"profile {profile}.{agent}.backends.{backend}.tools cannot be enforced")
    if backend == "claude" and isinstance(tools, list) and (
        len(tools) != len(set(tools)) or any(tool not in _CLAUDE_TOOLS for tool in tools)
    ):
        raise ProfileError(f"profile {profile}.{agent}.backends.claude.tools is unsupported")
    if backend == "claude" and permission not in {"manual", "autonomous"}:
        raise ProfileError(f"profile {profile}.{agent}.backends.claude.permission is unsupported")
    if backend == "hermes" and (model != "inherit" or effort != "inherit" or tools != "inherit"):
        raise ProfileError(f"profile {profile}.{agent}.backends.hermes must explicitly inherit unsupported controls")
    return BackendRuntime(model, effort, tools if isinstance(tools, str) else tuple(tools), permission)


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
