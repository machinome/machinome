# SolidNode Studio architecture overview

SolidNode Studio is a local agent harness for mechanical CAD projects. A
human pilot owns intent and consequential choices; the runtime opens a
project hub over one working folder and can hold several isolated project
sessions, each with a repository-owned validated team profile. `AGENTS.md`
governs how this repository is changed. This document describes the running
system.

## Project hub and sessions

The process starts without preparing a project, building a model, or starting
an agent. Both entry points require `--projects-dir`, which names the exact
external catalogue served by `floor/app.py`. The runtime neither appends a
directory name nor derives a location from cwd or Git metadata. Its inventory
is derived from the filesystem: every direct-child
directory is listed, and exact independent Git repository roots also report
their declared profile, branch, and last commit time. Regular files are omitted;
malformed project configuration and non-repository directories remain visible
with an unopenable reason. Project directory names have no stylistic constraint.

`floor/sessions.py` owns a `SessionRegistry` keyed by project name and also
indexed by an opaque generated session identifier. A project has at most one
session; different projects have no cardinality limit. Each `Session` owns the
verified project and artifact roots, build environment, resolved profile,
broker, orchestrator and backend processes, delivery/event tasks, model and
artifact watchers, and filesystem observer. Opening is asynchronous and
reported on the hub stream. Profile resolution, preparation, and agent start
are fatal and tear down partial resources; a failed initial model build is
recorded in the session and does not prevent its workspace from opening.

Agents receive `FLOOR_SESSION` beside `FLOOR_URL`, and every agent-facing API
route resolves that identifier through the registry. An unknown or expired
identifier is a 404 and never falls back to a project name or another session.
Closing removes both registry indexes before boundedly ending agents, routing
tasks and watchers. Sessions persist nothing; reopening a project generates a
new identifier and a fresh broker and conversation.

## Profile-defined runtime

When a project is opened, the registry makes one side-effect-free read of its
`pyproject.toml`, then loads `profiles/<id>/profile.toml` from the running shop
package resources. A source-worktree launch therefore exercises that worktree;
an installed launch uses its installed resources and requires no Git checkout.
The project's `[tool.solid-node-studio]` `profile` value selects it;
otherwise the shop uses `fordesmac`. The launcher provides no override. A
profile is strict trusted configuration: it declares the
human label, one user-facing agent, standing roster, direct or delegated work
mode, prompt paths, allowed skills, communication edges, and Codex and Claude
runtime defaults. The option overrides a project declaration for one run
without modifying it. The project may select backend, provider, model, and
reasoning level per agent under `[tool.solid-node-studio.agents]`; profile tool
policy and Claude permission remain non-overridable. OpenCode has no profile
table and is available only through an explicit project selection. Creating a
project records the profile selected in the hub in that repository's initial
commit.

The profile's Claude tool list is also the shared capability vocabulary for
scoped Claude and OpenCode sessions. The adapters resolve those names to a
floor-owned MCP allowlist; OpenCode inherits the policy without adding a
profile table. Codex cannot enforce it and retains `tools = "inherit"` and its
native surface. The Fordesmac librarian is provisionally non-functional on the
scoped backends because this surface intentionally has no web or external
documentation tools; it remains usable on Codex pending a bounded research
surface.

The initial profiles are:

| Profile | Mode | Human-facing agent | Standing roster |
| --- | --- | --- | --- |
| `builder` | direct | Builder | Builder |
| `fordesmac` | delegated | Foreman | Foreman, Designer, Machinist, Librarian |

Runtime prompts live beside their profile. A prompt names only skills exposed
through its profile `skills/` allowlist. Shared runtime skills live under
`shop-skills/`; repository operator and development skills remain under
`skills/`. Each declared agent receives the exact verified project repository
root, while prompts and skills remain shop-owned outside that project.

## Runtime layers

```text
browser hub <--> SessionRegistry <--> Session (one per open project)
                                         |
project browser <--> Broker <--> Orchestrator <--> per-agent backend owners
                         |             |                   /    |    \
                   state, SSE,    resolved profile      Codex Claude OpenCode
                   conversation   and runtime map       event streams fan in
```

`floor/app.py` contains the in-memory broker and browser API. Each session's
broker uses stable internal
identity `user`, profile agent IDs, and profile labels. It validates every
sender, recipient, assignment edge, reporting edge, lifecycle operation, and
conversation author against the active profile. Browser run state contains the
stable profile ID, human label, user-facing agent, and full declared roster.
Only output from the selected profile's user-facing agent enters the user
conversation.

Direct profiles have no assignment identity or assignment lifecycle. A direct
user direction is delivered to the user-facing agent; only a matching backend
delivery's `turn_started` and `turn_completed` events change it between waiting
and active. Steering retains that delivery identity, and stale events cannot
activate or clear work.

Delegated profiles retain assignment state. An assignable specialist becomes
active only after acknowledging its matching assignment and becomes waiting
only after matching completion. Backend turn events neither activate nor clear
delegated assignment work. Backend availability is orthogonal to that work
state: each manifested agent can carry a current failure reason without losing
or completing its assignment, and that reason is part of broker snapshots and
live events.

`floor/orchestrator.py` is deterministic and backend-neutral. It instantiates
each distinct selected backend once, maps every agent to its owner, consumes
all owners' event streams concurrently, and opens profile agents in declaration
order. It constructs a required `RoleContext` containing the validated and
resolved `ProfileAgent`, labels, shop root, and verified project root, and
closes the arbitrary roster in reverse order before closing each backend once. It
uses `deliver_start()` for idle delivery and `deliver_steer()` only for the
currently active delivery. Native session and turn identifiers never enter the
broker. A role-scoped failure clears only that role's active delivery and keeps
the floor and other sessions alive. The next envelope to that role starts a new
turn on the retained session; if its transport is dead, the orchestrator opens
one replacement session and retries once. It never polls or retries without a
new envelope. A backend-wide failure still ends the run.

## Backend seam

The portable `AgentBackend` protocol owns external processes and exposes
`open_role`, `deliver_start`, `deliver_steer`, `interrupt`, `close_role`, and
`close`. It emits portable role-message, turn, and failure events. It has no
generic compatibility delivery operation.

Codex translates the resolved project/profile model and effort into `thread/start`.
Claude launches one isolated CLI process per profile agent and translates the
selected model, effort, permitted tools, and explicit permission policy into
its supported command fields. For a scoped role it writes a strict MCP config,
removes `--safe-mode` because that flag disables MCP and passes only the resolved
`mcp__floor__*` names. Because Claude emits no init
before its first user input, project opening manifests the process after the
short exit grace without a warm-up turn. The first real broker envelope triggers
initialization, and that delivery is accepted only after `system/init` reports
the floor server connected with exactly that tool set, waiting through
transitional `pending` frames within a separate bounded readiness deadline. An autonomous Claude policy
bypasses confirmation prompts only for those tools; it does not grant extras or
provide operating-system sandboxing. An unscoped compatibility role retains
safe mode. These two adapters consume one resolved runtime and never parse
project or profile files or load global role adapters.

The floor MCP server is rooted at the exact active project. Every path-bearing
filesystem, Git, and solid-node operation resolves and rejects escapes before
acting. It exposes text and raster reads, bounded writes, non-destructive Git
and commit operations, finite build/test, and temporary image-returning
snapshots. Its broker lifecycle wrappers can assign, direct, acknowledge,
report, and complete only through the backend-injected floor URL and opaque
session; they expose no generic network operation. Push, reset, checkout,
branch, rebase, arbitrary shell, web, and arbitrary HTTP are absent.

OpenCode owns one password-protected loopback HTTP/SSE server and one persistent
session per role. Its adapter does not require or read OpenCode profile tables.
When a project selects an OpenCode provider and model, each prompt carries that
exact `{providerID, modelID}` pair and its optional reasoning variant. Otherwise
the adapter inherits the authenticated operator model, variant, and global
configuration and owns temporary model/variant/tool compatibility defaults. For each role it
uses the default `build` agent, globally disables the proven native tool set,
registers the floor MCP server, and sends a per-prompt allowlist of the role's
resolved floor tools. Every role launch gets a unique temporary working
directory so OpenCode cannot reuse directory-keyed conversation state. The
adapter consumes OpenCode's server-global event stream and filters it to known
role session IDs, preserving completion and failure delivery across those
isolated directories, while the MCP server remains rooted at the verified
project. Every role delivery
carries the exact profile prompt and exact allowlisted skill instructions as
that session's system contract.

OpenCode native project configuration is disabled. If the exact verified
project-root `AGENTS.md` is a regular non-symlink file, the adapter manually
appends it after explicit subordinate-guidance framing. It does not follow a
symlink or search another location. OpenCode 1.18.11 evidence confirms that
project configuration can be disabled while operator-global authentication and
provider defaults remain available. The server uses `--pure` so external
plugins do not execute. Archived authenticated verification proves the
transport and role-contract composition on the tested 1.18.11 runtime; scoped
tool replacement is covered by the repository's adapter and MCP protocol
fixtures.

The profile defaults are Builder/Foreman/Machinist/Librarian on Claude
`sonnet`, medium effort. On Codex, Builder uses `gpt-5.3-codex-spark` at high
effort while Foreman/Machinist/Librarian use `gpt-5.6-terra` at medium effort;
Designer uses Claude `opus` and Codex `gpt-5.6-sol`, both at medium effort. An
unnamed project agent uses its Codex default. A project selection replaces the
model and optional effort, while tool and permission values still come from the
profile. These choices are backend configuration, not broker semantics.

## Floor and browser

The service binds its listener before any project is selected. For each open
request, profile validation and runtime resolution complete before preparation
creates or verifies the named independent project repository. The initial build
runs through the `solid` console script installed beside the Python interpreter
running the shop, so an unrelated executable earlier on ambient `PATH` cannot
select a different framework installation. The build
runs off the event loop and reports an error into that session instead of
gating it; agent start remains all-or-nothing. The hub remains available during
opening and after any one project's failure. The browser renders
profile-provided roster labels, conversation attribution, and event summaries;
it does not encode a participant's role. The transcript is independently
scrollable, reveals newly appended messages, sends a non-empty draft on Enter,
and inserts a newline on Ctrl+Enter.

Floor serves only published `_build/` artifacts beneath a project-scoped
browser path. Every session owns a filesystem observer with separate source and
artifact handlers: source events outside `_build` settle into a `solid build`,
while each atomic rename into `_build` becomes a named artifact event for that
session's browser. The floor neither hashes or
diffs publication contents nor forwards deletions; `errors.json` is published
and reported through the same path. Each artifact route holds one fixed build
root and therefore does not re-resolve a symlink during a request. Agent
sessions do not run a callback process or expose project source through the
browser service.

Each project browser mounts its framework viewer for that workspace. It maps
each published path directly to the viewer: the manifest reconciles the model,
a regular artifact updates only the geometry that names it, and `errors.json`
updates the separate build-failure banner. A failed targeted request reports
beside the retained model and the next publication retries normally; the browser
does not remount the viewer or interpret artifact contents.

The hub holds one live-state connection to `/api/stream`. It opens with the
complete project inventory and then carries only project opening, open, failed,
and closed changes. A workspace holds one connection to its session stream. It
opens with that broker's complete run state and full ordered conversation, then
carries only that project's subsequent changes. Neither scope polls live state,
and the hub never receives a conversation. A broker subscribes the connection
before reading the snapshot, and its snapshot carries the explicit latest event
sequence so the browser can discard that hand-off overlap exactly once.

Current run state includes any role-scoped backend failure. The browser shows
the profile-labelled reason in an accessible conversation-area notice while
leaving the composer available, and tells the maker to message the configured
user-facing agent after backend access is restored. The notice is runtime
state, not participant-authored conversation, and clears when a recovery
delivery is accepted.

Every reconnection repeats the relevant snapshot path. A workspace assigns its event
position from that snapshot rather than retaining a higher position from a
previous connection. Because sessions are ephemeral, a project page whose
session ended or disappeared after a service restart returns to the hub.
Connection state drives the displayed open/closed lifecycle; reconnecting an
intact session also prompts the mounted viewer to re-read its model because
artifact events are not recoverable broker state. The bounded broker event
history is reserved for a future activity display and is never read for
recovery.

## Workspace boundaries

Each `<projects-dir>/<name>/` directory is an independent Git repository. The
required catalogue directory is an external runtime input and may be unrelated
to the shop installation. In this repository's development workspace, the
framework checkout belongs under `solid-node/`; framework worktrees belong
under `solid-node/WTs/`; shop worktrees belong under `WTs/`. Runtime agents use
only their session's verified project root plus their selected profile contract.
The session identifier is the routing boundary as well as the process
environment supplied to the agent; runtime agents do not inspect sibling
mechanical projects.
