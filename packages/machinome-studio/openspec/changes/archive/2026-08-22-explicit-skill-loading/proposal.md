## Why

A runtime agent cannot reach its profile-allowlisted skills the way agents
normally reach skills. The Claude backend names each skill's absolute
`SKILL.md` path in the session contract, but a scoped Claude session has only
the floor MCP tool set, and every one of those tools rejects a path outside the
active project — so the skill is unreadable and the role silently works without
its craft manual. The OpenCode backend compensates by inlining the full text of
every allowlisted skill into the system contract of every prompt, which spends
the context budget on instructions the role may never need and makes skill size
a per-turn cost.

Both are workarounds for a missing capability: progressive disclosure. The
established pattern is to announce the available skills by name and description
and let the agent load one on demand.

## What Changes

- Add a `load_skill` tool to the floor MCP tool set. It resolves a skill by
  name against an explicit registry supplied when the server is launched, and
  returns that skill's instructions. An optional `resource` argument returns a
  file bundled beside `SKILL.md`, contained by the skill directory.
- **BREAKING** (internal contract): `load_skill` reads outside the active
  project. It is the single, named exception to project sandboxing, bounded to
  pre-registered skill directories the shop itself supplied; it accepts a skill
  name, never a path.
- Expose `load_skill` to a session when, and only when, that session's agent
  declares at least one skill. Its availability follows the profile's declared
  skills, not the profile's declared tool capabilities — a role with skills can
  always load them.
- Inject a skill catalogue — one line of `name: description` per allowlisted
  skill, plus the instruction to load a skill before doing work it covers —
  into every backend's session contract.
- **BREAKING** The Claude session contract stops naming unreachable `SKILL.md`
  paths, and the OpenCode system contract stops inlining whole skill bodies.
- Validate each allowlisted skill's `SKILL.md` frontmatter at profile load,
  requiring a `name` matching the directory and a non-empty single-line
  `description`. A skill that cannot describe itself cannot be announced, so
  loading the profile fails rather than opening a floor with an unannounceable
  skill.

## Capabilities

### New Capabilities
- `runtime-skill-loading`: how a runtime agent learns which skills it has and
  loads one on demand — the catalogue injected into every session contract, the
  `load_skill` tool and its bounded containment, and the per-session
  availability rule.

### Modified Capabilities
- `scoped-agent-tools`: the tool set gains `load_skill`, and the project
  sandboxing requirement gains its one bounded exception.
- `shop-agent-backend`: both backends deliver a skill catalogue as
  session-level instructions instead of skill paths (Claude) or full skill
  instructions per delivery (OpenCode).
- `shop-runtime-profile`: an allowlisted skill must carry self-describing
  frontmatter, which profile validation checks.

## Impact

- `floor/profiles.py` — allowlisted skills resolve to name, description, and
  directory rather than a bare path; `ProfileAgent.skill_paths` becomes
  `ProfileAgent.skills`.
- `floor/mcp_server.py` — new `load_skill` tool, skill registry parameter on
  `ProjectTools` and `mcp_command`.
- `floor/backends/claude.py` — per-role skill registry in the generated MCP
  config, `load_skill` in the scoped tool list and readiness expectation,
  catalogue in the session contract.
- `floor/backends/opencode.py` — skill registry on the shared server, per-role
  catalogue in the system contract, `load_skill` in the per-prompt tool payload.
- `floor/backends/__init__.py`, `floor/sessions.py` — thread the profile's
  skills to the backend that needs them at construction.
- No change to profile manifests, prompt frontmatter syntax, or the
  `shop-skills/` layout.
