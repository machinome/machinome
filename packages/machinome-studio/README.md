# solid-node shop

An experimental local harness for building 3D-printable mechanical CAD
projects with solid-node. The pilot chooses a repository-owned runtime profile;
the profile, rather than Python role constants, defines the standing team,
authority, prompts, skills, and normally the backend controls. OpenCode's
temporary compatibility policy is the documented exception.

## Open a floor

```text
python -m floor.orchestrator <project-name> --profile builder --backend codex
python -m floor.orchestrator <project-name> --profile fordesmac --backend claude
python -m floor.orchestrator <project-name> --profile builder --backend opencode
python -m floor <project-name> --profile builder
```

`builder` is the default profile and opens one direct Builder session.
`fordesmac` opens standing Foreman, Designer, Machinist, and Librarian sessions;
Foreman alone assigns and receives specialist reports. The broker-only command
does not open a backend. A profile is validated before the named project is
created, built, or served.

Each runtime agent receives the exact verified `projects/<name>` repository
root. Runtime prompts belong to `profiles/<id>/`; their shared allowlisted
skills are in `shop-skills/`. Repository operation and development skills stay
under `skills/` and are not runtime capabilities.

Four backends are selectable: Codex, Claude, Hermes, and OpenCode. Codex gets
the profile-configured model and reasoning effort, Claude gets its selected
model, effort, and supported tools, and Hermes explicitly inherits its process
configuration. These three use explicit profile runtime tables.

OpenCode currently uses a bounded compatibility exception. Existing profiles
remain unchanged and valid and do not contain OpenCode tables. The adapter
inherits the authenticated operator model, variant, and global OpenCode
configuration and owns temporary model/variant/tool defaults. One generated
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
commits remain in solid-node-shop.

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
