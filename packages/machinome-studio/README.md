# Machinome Studio

Machinome Studio is an experimental local harness for building 3D-printable
mechanical CAD projects with machinome. The project normally chooses a
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
pilot-selected machinome installation; the shop invokes that environment's
`machinome` command directly rather than resolving an unrelated command through
ambient `PATH`.

The OpenSpec CLI is an unconditional startup prerequisite and an exception to that rule:
it is a Node program, so the shop resolves `openspec` from ambient `PATH` and
refuses to start when it is missing or will not run, naming what to install.
There is no reduced mode — a shop that cannot record a project's design would
lose that record silently. Install it with:

```text
npm install -g @fission-ai/openspec
```

Qualifying fresh Codex availability, resolving explicit Codex selection or
provisioning its dedicated login additionally discovers `codex` through ambient
`PATH`, then retains and qualifies its pinned executable. Other projects do not
require Codex. This exception changes neither package/framework resolution nor
the discovery authority for other tools.

The orchestrator takes no project or profile. The pilot opens an
existing project or creates one in the browser;
several projects may be open at once. `fordesmac` is the default and opens
standing Foreman, Designer, Machinist, and Librarian sessions; Foreman alone
assigns and receives specialist reports. `builder` opens one direct Builder
session, which keeps the project's own OpenSpec record of the interfaces
between its parts and plans each design change there before machining it. The broker-only command serves the same hub without opening a backend.

Opening a project reads its runtime configuration without changing it, then
validates the profile and resolved runtime before preparation or agents start.
A failed initial model build still opens the project so it can be repaired in
the workspace; profile, preparation, and agent-start failures leave no partial
session and are reported on the hub. Closing a project ends its ephemeral
conversation, agents, watcher, and backend resources without stopping the hub
or another project.

The hub lists every entry under the selected projects directory, including
unopenable entries with their reason. Each open project has one opaque session
identifier, an isolated broker, profile roster, conversation, model build and
watcher. Agent processes receive only their own identifier through
`FLOOR_SESSION`; a stale identifier cannot reach a later session of the same
project. The service serves only each session's completed `_build/` artifacts
and refreshes them with its own watcher. The floor serves the viewer bundle
the framework reports through `machinome viewer`, and refuses to open a
project when no usable viewer is installed.

Declare runtime choices in the project's `pyproject.toml`. Omitted agents use
their profile's Claude model and effort. A final segment overrides reasoning;
OpenCode additionally requires a provider:

```toml
[tool.machinome-studio]
profile = "fordesmac"

[tool.machinome-studio.agents]
foreman = "claude:opus"
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
allowlisted skills are in `shop-skills/`.

Three backends are selectable per agent: Claude, OpenCode and qualified Codex. Claude resolves
project-selected model/reasoning values over explicit profile defaults; the
supported tools remain profile-owned, and that declared list is the whole
authority a session holds — no session runs with permission checking disabled.

All replace native file, shell, and network access with a floor-owned
surface for roles with explicit profile tools. It is rooted at the active
project and provides bounded filesystem, Git, machinome, image, and
shop-broker lifecycle operations. A backend that cannot enforce a
profile-declared tool policy is not selectable. The librarian is provisionally unavailable on
the scoped backends because bounded external-research tools are not yet
present.

Codex is explicitly selected as `codex:gpt-6-sol[:effort]` or
`codex:gpt-6-astra[:effort]`; Claude remains the default and profiles gain no
Codex tables. Effort defaults to `medium`; supported values are `low`, `medium`,
`high`, `xhigh`, `max` and `ultra`. Only pinned Linux x86_64
`codex-cli 0.157.1` is qualified. Studio verifies
the actual native schemas, model catalogue, effective private configuration and
forced-call isolation before preparing a selected project. Its native sessions
use read-only sandboxing, never approvals, and no environment at thread creation
or any turn. Exact declared floor tools are bridged dynamically through owned
per-role MCP workers, including raster image results.

Provision Studio once with your existing ChatGPT account:

```sh
python -m floor.codex_auth login
```

This creates a separate Studio-owned login under
`$XDG_STATE_HOME/machinome-studio/codex` (or
`$HOME/.local/state/machinome-studio/codex`), never copies refresh tokens from
ordinary Codex or changes its credentials. One exclusively leased native
app-server owns authentication and refresh across simultaneous Studio projects.
Closing project roles removes their owned native histories, not the login.
Unsupported policy, missing login or changed qualification reports an unavailable
reason; it does not silently fall back to another runtime. Used Codex contexts
that cannot safely resume fail role-locally without fresh-session replacement.
Workers preserve resolved plain Git identity but cannot honor required signed
commits; signing-required commit/setup operations refuse with an explicit remedy.
This is a bounded tool boundary, not an OS sandbox guarantee for executable
project code: owned process groups are stopped, but malicious code deliberately
escaping those groups is outside this implementation's containment claim.

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

## Install

Machinome Studio is not published to any package index; installing it means
cloning this repository and running:

```text
scripts/setup
```

It creates `.venv/`, installs `machinome[viewer]` and
`machinome-viewer[snapshot]` from PyPI with the Chromium the snapshot renderer
needs, installs the OpenSpec CLI, builds the frontend into `floor/static/`, and
installs the studio itself editable. It requires Python 3.11 or later,
node and npm, git, and OpenSCAD.

`<projects-dir>/<name>/` is an independent Git repository. The catalogue path
comes only from the required launcher option and need not be inside the studio
checkout or installation.

## Development

Run the local checks with:

```text
python -m unittest discover -s tests -v
npm --prefix floor/frontend run test
npm --prefix floor/frontend run build
scripts/test-e2e
```

`floor/static/` is generated output, not tracked: the frontend build empties
and rewrites it. `scripts/setup` builds it, so a fresh checkout has a browser
surface; rerun the build above after changing `floor/frontend`.

The studio is developed from the machinome workspace repository
(<https://github.com/machinome/workspace>), beside the framework and the other
packages of the ecosystem; framework changes, cross-repository sprints and the
rest of the ecosystem's process live there. [AGENTS.md](AGENTS.md) is the
contract for changing this repository.

## License

Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes.

Machinome Studio is licensed under the GNU Affero General Public License,
version 3 or (at your option) any later version. See [LICENSE](LICENSE).
