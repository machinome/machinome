# SolidNode Studio

SolidNode Studio is an experimental local harness for building 3D-printable
mechanical CAD projects with solid-node. The pilot chooses a repository-owned runtime profile;
the profile defines the standing team, authority, prompts, skills, tool policy,
and safe runtime defaults. Each project can durably select backend, provider,
model, and reasoning level per agent.

## Open a floor

```text
python -m floor.orchestrator <project-name> --profile builder
python -m floor.orchestrator <project-name> --profile fordesmac
python -m floor <project-name> --profile builder
```

`builder` is the default profile and opens one direct Builder session.
`fordesmac` opens standing Foreman, Designer, Machinist, and Librarian sessions;
Foreman alone assigns and receives specialist reports. The broker-only command
does not open a backend. The launcher reads project runtime configuration
without creating anything, then validates the profile and resolved runtime
before the named project is created, built, or served.

Declare runtime choices in the project's `pyproject.toml`. Omitted agents use
their profile's Codex model and effort. A final segment overrides reasoning;
OpenCode additionally requires a provider:

```toml
[tool.solid-node-studio.agents]
foreman = "codex:gpt-5.6-terra"
designer = "opencode:anthropic:claude-sonnet-4-5:high"
machinist = "claude:sonnet:medium"
```

The launcher has no run-wide backend flag. One floor may open several backends,
and it starts each distinct selected backend exactly once.

Each runtime agent receives the exact verified `projects/<name>` repository
root. Runtime prompts belong to `profiles/<id>/`; their shared allowlisted
skills are in `shop-skills/`. Repository operation and development skills stay
under `skills/` and are not runtime capabilities.

Three backends are selectable per agent: Codex, Claude, and OpenCode. Codex and
Claude resolve project-selected model/reasoning values over explicit profile
defaults; supported tools and Claude permission remain profile-owned.

OpenCode currently uses a bounded compatibility exception. Existing profiles
remain unchanged and valid and do not contain OpenCode tables. A project-selected
provider/model pair is sent on each prompt, with an optional reasoning variant.
When no concrete pair is resolved, the adapter inherits the authenticated
operator model, variant, and global OpenCode configuration and owns temporary
model/variant/tool defaults. One generated
deny-by-default primary agent serves persistent role sessions; every prompt
carries that session's exact profile prompt and allowlisted skill instructions.
This does not claim that OpenCode exposes controls equivalent to the other
backends.

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

`projects/<name>/` is an independent Git repository. `solid-node/` and its
`WTs/` are framework checkouts; top-level `WTs/` holds shop worktrees. The
floor prepares and validates the selected project before opening. It serves
only completed `_build/` artifacts and refreshes them with its own watcher.

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
