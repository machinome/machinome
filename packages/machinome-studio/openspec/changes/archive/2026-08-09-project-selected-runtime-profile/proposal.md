## Why

ADR 0017 moved backend, provider, model, and reasoning level into the project's
`pyproject.toml` so a project would be a durable statement of how it was built.
It stopped one step short: the profile — which roster of agents opens, and
therefore whether the project is machined by a single Builder or by a Foreman
directing a Designer, a Machinist, and a Librarian — is still chosen by a flag
someone types. That is a larger fact about how a project is built than which
model its Machinist ran on, and today nothing in the project records it.

A project is normally worked one way. A gearbox that has been developed through
the delegated pipeline should open that way tomorrow, on another machine, without
the pilot remembering a flag. Reaching for the other roster remains legitimate —
a quick fix under a single Builder on a project that usually runs Fordesmac — so
the flag stays, as an explicit override rather than as the only source.

Separately, the pilot no longer wants `builder` as the shop's default. Fordesmac
is the profile the shop is being built around, and it should be what opens when
nothing says otherwise.

## What Changes

- Read the runtime profile from the active project's `pyproject.toml` as a
  `profile` key in the shop-owned `[tool.solid-node-studio]` table, alongside
  the existing `agents` table.
- Establish one precedence chain for profile selection: `--profile` when given,
  otherwise the project's declared profile, otherwise the shop default. Unlike
  `--backend`, the flag is retained deliberately, so that a project may be opened
  under a roster it does not normally use and so that a project scaffolded by the
  launcher can be opened under any profile before it has a file to declare one in.
- **BREAKING** Change the shop default profile from `builder` to `fordesmac`.
  Omitting `--profile` for a project that declares none now opens the delegated
  roster rather than a single Builder session. This is an independent decision
  from project-declared profiles and would stand on its own.
- Reject a project-declared profile that does not resolve, with an error naming
  the project file and the offending value, rather than falling back to the
  default. Silently opening a one-agent floor when the project asked for the
  delegated pipeline is a failure a pilot would not notice quickly.
- Leave the scaffold silent. A project the launcher creates carries no profile
  key, exactly as it carries no runtime selection; the pilot writes one when the
  project has a settled way of being worked.
- Keep the existing tolerance for agent keys outside the active roster. A project
  declaring a profile can still be opened under another one, so a selection for
  an agent the active roster does not contain remains ignored and reported rather
  than rejected.

Deliberately out of scope: tool policy and Claude permission remain
profile-owned and untouched. Naming a profile selects a repository-owned trusted
package as a whole; that those packages bundle policy with topology and models
is a pre-existing layering question this change neither creates nor resolves.

## Capabilities

### New Capabilities

None. This extends two existing capabilities rather than introducing one.

### Modified Capabilities

- `shop-runtime-profile`: the prohibition on a project supplying a profile is
  replaced by a stated precedence chain of flag, project, and default; the
  default becomes `fordesmac`; validation ordering gains the profile identity
  itself as something read from the project before the profile is loaded.
- `project-runtime-selection`: the `[tool.solid-node-studio]` table admits a
  `profile` key beside `agents`, with its own well-formedness and resolution
  rules and its own rejection behaviour.

## Impact

Code: `floor/preparation.py` (`read_project_runtime` accepts and validates the
`profile` key; `ProjectRuntimeSelection` carries it), `floor/orchestrator.py`
and `floor/__main__.py` (apply the precedence chain at the two places that
already read project selection before loading a profile), `floor/profiles.py`
(`load_profile`'s `default` becomes `fordesmac`; errors distinguish a
project-supplied name from a flag-supplied one).

Docs: `skills/running-the-shop/SKILL.md` (the `--profile` parameter description
and the default), `README.md`, `AGENTS.md` (the shop-floor lane tells the
repository agent to select a profile explicitly), `docs/architecture-overview.md`.
A new ADR amending 0011 and 0017, and an ADR index entry.

Tests: `tests/test_project_runtime_selection.py` (the key's parsing and
rejection), `tests/test_runtime_profiles.py` (precedence and default),
`tests/test_floor_entrypoint.py` and `tests/test_orchestrator.py` (both entry
points), `tests/test_development_protocols.py` if it asserts documented defaults.

No change to the broker, the browser workspace, role prompts, shop skills, the
profile schema itself, or the framework.
