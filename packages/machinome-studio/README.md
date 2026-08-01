# solid-node shop

An experimental local harness for building 3D-printable mechanical CAD
projects with solid-node. The pilot chooses a repository-owned runtime profile;
the profile, rather than Python role constants, defines the standing team,
authority, prompts, skills, and backend controls.

## Open a floor

```text
python -m floor.orchestrator <project-name> --profile builder --backend codex
python -m floor.orchestrator <project-name> --profile fordesmac --backend claude
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

The selected backend receives the profile's validated controls: Codex gets the
configured model and reasoning effort, Claude gets its selected model, effort,
and supported tools, and Hermes explicitly inherits its process configuration.
No backend loads global role cards or `.codex/agents` runtime adapters.

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
