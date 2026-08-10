# SolidNode Studio

SolidNode Studio is an experimental local harness for building 3D-printable
mechanical CAD projects with solid-node. The project normally chooses a
repository-owned runtime profile;
the profile defines the standing team, authority, prompts, skills, tool policy,
and safe runtime defaults. Each project can durably select backend, provider,
model, and reasoning level per agent.

## Open a floor

```text
python -m floor.orchestrator --projects-dir PATH
python -m floor --projects-dir PATH
```

`--projects-dir` is required and names the exact external project-catalogue
directory; the shop does not append `projects/`, inspect a Git checkout, or
derive it from process cwd. The directory may be unrelated to the shop
installation. The Python environment used to launch the shop must contain the
pilot-selected solid-node installation; the shop invokes that environment's
`solid` command directly rather than resolving an unrelated command through
ambient `PATH`. The orchestrator takes no project or profile. The pilot opens an
existing project or creates one in the browser;
several projects may be open at once. `fordesmac` is the default and opens
standing Foreman, Designer, Machinist, and Librarian sessions; Foreman alone
assigns and receives specialist reports. `builder` opens one direct Builder
session. The broker-only command serves the same hub without opening a backend.

Opening a project reads its runtime configuration without changing it, then
validates the profile and resolved runtime before preparation or agents start.
A failed initial model build still opens the project so it can be repaired in
the workspace; profile, preparation, and agent-start failures leave no partial
session and are reported on the hub. Closing a project ends its ephemeral
conversation, agents, watcher, and backend resources without stopping the hub
or another project.

Declare runtime choices in the project's `pyproject.toml`. Omitted agents use
their profile's Codex model and effort. A final segment overrides reasoning;
OpenCode additionally requires a provider:

```toml
[tool.solid-node-studio]
profile = "fordesmac"

[tool.solid-node-studio.agents]
foreman = "codex:gpt-5.6-terra"
designer = "opencode:anthropic:claude-sonnet-4-5:high"
machinist = "claude:sonnet:medium"
```

When `profile` is absent, the project uses `fordesmac`. A project created from
the hub records the profile chosen in the new-project sheet in its initial
commit.

The launcher has no project, profile, or run-wide backend flag. Each project
session starts each distinct selected backend exactly once.

Each runtime agent receives the exact verified `<projects-dir>/<name>`
repository root. Runtime prompts belong to `profiles/<id>/`; their shared
allowlisted skills are in `shop-skills/`. Repository operation and development
skills stay under `skills/` and are not runtime capabilities.

Three backends are selectable per agent: Codex, Claude, and OpenCode. Codex and
Claude resolve project-selected model/reasoning values over explicit profile
defaults; supported tools and Claude permission remain profile-owned.

Claude and OpenCode replace native file, shell, and network access with a
floor-owned MCP surface for roles with explicit profile tools. It is rooted at
the active project and provides bounded filesystem, Git, solid-node, image, and
shop-broker lifecycle operations. Codex cannot enforce this restriction and
retains its native tools. The librarian is provisionally unavailable on the
scoped backends because bounded external-research tools are not yet present.

OpenCode currently uses a bounded compatibility exception. Existing profiles
remain unchanged and valid and do not contain OpenCode tables. A project-selected
provider/model pair is sent on each prompt, with an optional reasoning variant.
When no concrete pair is resolved, the adapter inherits the authenticated
operator model, variant, and global OpenCode configuration. The adapter uses
the default `build` agent, disables native tools, registers the floor MCP
server, gives every role launch a unique working directory, and consumes the
server-global event stream so those isolated sessions remain observable. Every prompt
carries that session's exact profile prompt, allowlisted skill instructions,
and resolved floor-tool allowlist.

OpenCode requires a locally authenticated `opencode` runtime. Native project
OpenCode configuration is disabled. If the exact project-root `AGENTS.md` is a
regular non-symlink file, the adapter manually appends it as subordinate project
guidance; it does not follow a symlink or search elsewhere. Operator-global
OpenCode configuration remains inherited for authentication and provider
defaults, while `--pure` disables external plugin execution. OpenCode 1.18.11
was measured to preserve those global configuration sources while project
configuration is disabled and an authenticated persistent session is created.

No backend loads global shop role cards or `.codex/agents` runtime adapters.

## Workspace

`<projects-dir>/<name>/` is an independent Git repository. The catalogue path
comes only from the required launcher option and need not be inside a shop
source tree or installation. In this development workspace, `solid-node/` and
its `WTs/` are framework checkouts; top-level `WTs/` holds shop worktrees. The hub
lists every entry under the selected projects directory, including unopenable
entries with their reason. Each open project has one opaque session identifier,
an isolated broker, profile roster, conversation, model build and watcher.
Agent processes receive only their own identifier through `FLOOR_SESSION`; a
stale identifier cannot reach a later session of the same project. The service
serves only each session's completed `_build/` artifacts and refreshes them
with its own watcher.

## Cross-Repository Sprints

A sprint always integrates shop work on branch and worktree `sprint-NNN` and
`WTs/sprint-NNN`. If its ratified scope includes framework work, the framework
repository has its own same-named integration branch and worktree at
`solid-node/WTs/sprint-NNN`. Framework commits remain in solid-node; shop
commits remain in solid-node-studio.

The framework sprint worktree is linked into the shop sprint worktree at
`WTs/sprint-NNN/solid-node`. Run combined validation from the shop sprint
worktree so it uses the exact paired integration content. Framework child cycles
are created from the registered framework sprint head with:

```text
scripts/dev-env sprint-NNN-<change> setup --base sprint-NNN
```

Standalone framework benches keep using `scripts/dev-env <name> setup`. Sprint
dependencies and both tested content commits are recorded in `current.md` on
the shop sprint integration branch. Evidence-only record commits do not create
a new paired product state. The primary copy identifies the active sprint until
final integration. See `skills/sprint/SKILL.md` for lifecycle and authority
rules.

Run the local checks with:

```text
python -m unittest discover -s tests -v
npm --prefix floor/frontend run test
npm --prefix floor/frontend run build
scripts/test-e2e
```
