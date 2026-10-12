## Context

Skills reach a runtime agent through two different, both unsatisfactory, paths.

`floor/profiles.py` validates a prompt's `skills: [...]` frontmatter against the
profile's `skills/` allowlist and resolves each to a directory
(`ProfileAgent.skill_paths`). From there:

- `floor/backends/claude.py` appends `Required profile skill: <abs>/SKILL.md`
  to `--append-system-prompt`. A scoped Claude session runs with
  `--strict-mcp-config` and `--tools mcp__floor__…`, and every floor tool
  resolves paths through `ProjectTools._path`, which rejects anything outside
  the active project. The path is therefore unreadable, and the role proceeds
  without the skill.
- `floor/backends/opencode.py` inlines each `SKILL.md` in full into
  `_system_contract`, which is sent as `system` on every `prompt_async`. Skill
  text is paid for on every turn, whether or not the turn needs it.

The floor MCP server (`floor/mcp_server.py`) is a hand-written stdio JSON-RPC
server with a fixed `TOOL_NAMES` tuple and a `PROFILE_TOOL_MAP` that resolves
profile capabilities (`Read`, `Bash`, …) to floor tool names. Claude writes one
MCP config per role; OpenCode configures one server for the whole floor at
`start()`.

## Goals / Non-Goals

**Goals:**

- Give every backend the same progressive-disclosure shape: announce skills by
  name and description, load one on demand.
- Make a skill reachable from a scoped session without widening project
  containment for any other tool.
- Keep the profile the sole authority over which skills a role holds.

**Non-Goals:**

- Skill discovery beyond the profile allowlist. Nothing scans `shop-skills/`.
- Repository-development skills under `skills/`. They stay out of the runtime
  namespace.
- Changing profile manifests, prompt frontmatter syntax, or `shop-skills/`
  layout.
- Native skill mechanisms in either vendor runtime. OpenCode's native `skill`
  tool stays disabled; Claude's plugin/skill discovery stays off.

## Decisions

### A name-keyed registry, not a second path root

`load_skill` takes a skill name and resolves it against a registry the shop
supplies when the server is launched (`--skills-json`, a name → absolute
directory map). It accepts no path.

Alternative considered: let `read_file` accept a second containment root
covering skill directories. Rejected — it weakens the project-sandboxing
requirement for every path-taking tool to solve a problem that is not about
paths, and it forces the model to know where skills live on disk.

Bundled resources are reached with `load_skill(name, resource=…)`, resolved
inside the named skill's directory. That keeps the one exception in one tool.

### Availability follows declared skills, not declared capabilities

`load_skill` is not in `PROFILE_TOOL_MAP`. A session gets it when its agent
declares at least one skill, whatever its `tools` policy says — mirroring the
native Skill tool, which is not something a tool allowlist grants. A session
whose agent declares no skill does not get it, and the server reports no such
tool when nothing is registered.

### Claude registers per role; OpenCode registers the profile union

Claude writes an MCP config per role, so its registry is exactly that agent's
skills. OpenCode configures one server for the whole floor before any role
opens, so its registry is the union of the profile's skills, threaded from
`SessionRegistry` through `create_backend`.

This is a real asymmetry: on OpenCode a role could name a sibling role's skill.
It is bounded and acceptable — shop skills are non-secret operating
documentation, the per-role catalogue names only that role's own skills, and
the same shared-server property already applies to every other floor tool
(`floor_assign` takes the sender's role as an argument rather than deriving it
from the connection). Tightening it means per-session MCP configuration, which
OpenCode's server does not offer.

### The catalogue is session-level, the instructions are not

Each backend renders the catalogue into the instructions it already delivers at
session level — Claude's `--append-system-prompt`, OpenCode's per-prompt
`system`. The catalogue is small and stable; the bodies are not, which is what
made inlining them expensive.

Each backend names its own tool spelling in the catalogue text
(`mcp__floor__load_skill` for Claude, `floor_load_skill` for OpenCode) so the
agent has an exact string to call.

### Descriptions come from the skill, validated at profile load

`ProfileAgent.skill_paths` becomes `ProfileAgent.skills`, a tuple of
`ProfileSkill(name, description, path)` parsed from `SKILL.md` frontmatter with
the same deliberately crude line-oriented reader `_prompt_skills` already uses —
no YAML dependency. A skill with no usable `name`/`description` fails profile
validation, so an unannounceable skill can never reach a session.

## Risks / Trade-offs

- **A role ignores the catalogue and never loads its skill** → The catalogue
  states loading is required before work the skill covers, and role prompts
  already name their skills as authoritative. This is the same reliance the
  native mechanism makes; the previous Claude behaviour was strictly worse
  (the skill was unreachable even when the role tried).
- **OpenCode roles can load a sibling role's skill** → Accepted above; recorded
  rather than hidden.
- **`load_skill` reads outside the active project** → Bounded to
  shop-registered directories, name-keyed, read-only, and asserted by spec and
  test that no other tool gains that reach.
- **Skill text no longer arrives automatically on OpenCode** → A behaviour
  change for existing OpenCode roles: they must now call the tool. Covered by
  the catalogue instruction and by tests asserting the tool is enabled whenever
  the catalogue is present.
