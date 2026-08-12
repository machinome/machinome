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
broker, orchestrator and backend processes, delivery/event tasks, source
workspace, source/model/artifact watchers, and filesystem observer. Opening is asynchronous and
reported on the hub stream. Profile resolution, preparation, and agent start
are fatal and tear down partial resources; a failed initial model build is
recorded in the session and does not prevent its workspace from opening.

Agents receive `FLOOR_SESSION` beside `FLOOR_URL`, and every agent-facing API
route resolves that identifier through the registry. An unknown or expired
identifier is a 404 and never falls back to a project name or another session.
Closing removes both registry indexes before boundedly ending agents, routing
tasks and watchers. Conversation, activity, temporary runtime overrides, and
broker state are session-local; reopening generates a new identifier and fresh
state. A maker may explicitly persist an idle role's supported model/reasoning
change into the existing project runtime table.

## Profile-defined runtime

When a project is opened, the registry makes one side-effect-free read of its
`pyproject.toml`, then loads `profiles/<id>/profile.toml` from the running shop
package resources. A source-worktree launch therefore exercises that worktree;
an installed launch uses its installed resources and requires no Git checkout.
The project's `[tool.solid-node-studio]` `profile` value selects it;
otherwise the shop uses `fordesmac`. The launcher provides no override. A
profile is strict trusted configuration: it declares the
human label, one user-facing agent, standing roster, direct or delegated work
mode, prompt paths, allowed skills, communication edges, and Claude
runtime defaults. The option overrides a project declaration for one run
without modifying it. The project may select backend, provider, model, and
reasoning level per agent under `[tool.solid-node-studio.agents]`; profile tool
policy and Claude permission remain non-overridable. OpenCode has no profile
table and is available only through an explicit project selection. Creating a
project records the profile selected in the hub in that repository's initial
commit. Before a role's first message, assignment, accepted delivery, or
activity, an idle role may immediately replace its unused standing handle with
a complete backend/provider/model/reasoning selection. First use permanently
locks backend and provider. A supported idle role may still replace model and
reasoning together for later turns on the same backend and provider, temporarily
or with a revision-checked update to the same project table.

The profile's Claude tool list is also the shared capability vocabulary for
scoped Claude and OpenCode sessions. The adapters resolve those names to a
floor-owned MCP allowlist; OpenCode inherits the policy without adding a
profile table. Enforcing that allowlist is a condition of being selectable at
all: Codex was retired as a backend because its sessions keep native command
execution and file editing whatever the profile declares (ADR 0024). The
Fordesmac librarian is provisionally non-functional because this surface
intentionally has no web or external documentation tools, pending a bounded
research surface.

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
project browser <--> source service      +--> filesystem/build watchers
        |               |
        +-----------> Broker <--> Orchestrator <--> per-agent backend owners
                          |             |                   /    |    \
                    state, SSE,    resolved profile        Claude OpenCode
                    conversation   and runtime map       event streams fan in
```

`floor/app.py` contains the in-memory broker and browser API. Each session's
broker uses stable internal
identity `user`, profile agent IDs, and profile labels. It validates every
sender, recipient, assignment edge, reporting edge, lifecycle operation, and
conversation author against the active profile. Browser run state contains the
stable profile ID, human label, user-facing agent, and full declared roster.
Only output from the selected profile's user-facing agent enters the user
conversation. Browser state also contains each role's resolved runtime,
backend-native idle flag, authoritative combined editability, and a bounded
normalized activity history. Running and terminal forms of one activity share
a stable role/id key and replace rather than duplicate each other.

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

An accepted maker source save snapshots the roles whose broker work state is
active and queues a trusted `user_file_changed` notice for each. Notices are
separate from conversation, direction, assignment, and reporting envelopes;
they do not change direct or delegated work state. A later unsent revision for
the same role and path supersedes the earlier notice. Delivery removes only the
exact accepted notice, so a newer revision queued during an in-flight delivery
remains pending.

`floor/orchestrator.py` is deterministic and backend-neutral. It instantiates
each distinct selected backend once, lazily resolves another backend when a
pristine catalogue or replacement needs it, maps every agent to its owner, consumes
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

Before an ordinary delivery, the orchestrator prepends that role's pending
trusted notices and acknowledges them only after the backend accepts the
ordinary message. Immediately after a maker save it may also call the
backend's notice-only operation for the exact active delivery. Rejection or a
completion race retains the notice for the next ordinary delivery; notice-only
delivery never opens a replacement session or starts a turn.

Runtime mutation uses the same per-role lock as delivery. The orchestrator
requires no active native delivery, failure, current assignment, pending
assignment, or active broker work. The broker separately retains a monotonic
pristine bit that the first message, assignment, accepted delivery, or activity
clears. Only a pristine role may replace its unused handle across backend or
provider; a used role rejects that change permanently. Model and reasoning are
one runtime value. For persisted changes the session
prepares a comment-preserving TOML edit against its content revision; while the
role gate remains held, the orchestrator updates the backend and invokes the
atomic file publication before changing its runtime map or publishing browser
state. A publication failure restores the old backend runtime first. A pristine
replacement keeps its old handle authoritative until the new handle and file
publication both succeed, then swaps ownership and closes the unused handle.

## Backend seam

The portable `AgentBackend` protocol owns external processes and exposes
`open_role`, `deliver_start`, `deliver_steer`, `deliver_notice`, `interrupt`,
`close_role`, `runtime_catalog`, `update_runtime`, and `close`. A runtime
catalogue without a handle describes fresh-session backend/provider/model
choices; one with a handle describes context-preserving choices for that
session. It emits
portable role-message, turn, failure, and normalized activity events.
`deliver_notice` is steer-only: each adapter verifies that the expected
delivery is still active and returns false instead of starting a turn. The
protocol has no generic compatibility delivery operation.

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
safe mode. Claude normalizes completed tool-use blocks but exposes no mutable
runtime catalogue after first use: model changes require a new process, for
which context preservation has not been verified. Its fresh-session catalogue
does permit replacement of a pristine process. These two adapters consume one resolved
runtime and never parse project or profile files or load global role adapters.

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
that session's system contract. For a fresh role the adapter intersects the
live endpoint's complete catalogue with its connected provider IDs and exposes
only those provider/model/variant combinations. It never falls back to the
known-provider catalogue when none are connected. For a provider-pinned used
role the adapter applies the same connected boundary, limits choices to that
same provider, and may replace the model/variant used by later prompts without
replacing the session. Tool and patch parts are normalized into the portable
activity schema.

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
`sonnet` and Designer on Claude `opus`, all at medium effort. An unnamed
project agent uses that Claude default. A project selection replaces the model
and optional effort, while tool and permission values still come from the
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

Model, Code, and Agents are mounted workspace peers sharing that conversation
and the session's single snapshot/SSE connection. Agents selects one roster
role, renders normalized messages, tools, results, failures, file diffs, and
honest native token counts, and can open an activity path in the existing Code
workspace. Its runtime controls are ordered backend, provider, model, and
reasoning. Claude shows its fixed Anthropic provider; OpenCode shows exact
connected provider IDs separately and filters models by the selected provider. Profile-owned tools are not part of this choice. The
explicit Apply control fetches the role-owned catalogue, remains disabled
unless the server reports the role idle, and defaults to writing the selection
to `pyproject.toml`; unchecking persistence creates a session-only override.
The corresponding GET/PATCH runtime routes are role- and session-scoped and
revision-check durable writes. They accept a complete
backend/provider/model/reasoning replacement only while the role is pristine;
no used session is migrated. No polling or second lifecycle connection is introduced.

Floor serves published `_build/` artifacts beneath a project-scoped browser
path and, separately, the exact regular non-symlink root `screenshot.png` for
each verified project repository (including closed projects). The screenshot is
a fixed 640x360 preview rendered through the selected CLI after an
observed successful build and before a floor-mediated commit. Rendering and
staging are best-effort: they never turn a valid build or Git commit into a
failure. Every session owns a filesystem observer with separate source and
artifact handlers. Qualifying Python changes outside `_build` settle into one
`solid build`, regardless of whether the writer is an agent, the Code
workspace, or another local process. Source create, modify, move, and delete
events also become project-scoped browser invalidations after the watcher
re-evaluates Git visibility; they carry paths and operations, never content or
actor attribution. Each atomic rename into `_build` becomes a named artifact
event for that session's browser. The floor neither hashes nor diffs
publication contents nor forwards artifact deletions; `errors.json` is
published and reported through the same path. Each artifact route holds one
fixed build root and therefore does not re-resolve a symlink during a request.
Agent sessions do not run a callback process.

Each session has a project-rooted source service for the browser Code area. Git
defines the working set as tracked plus non-ignored untracked files; `.git`,
`_build`, and build-staging families are always excluded. Directory rows are
synthesized from those paths. Read and save revalidate Git visibility, reject
escapes, symlinks, and non-regular files, and accept at most one MiB of UTF-8
text. A read returns the SHA-256 byte revision. A save runs under the session's
source lock, compares the expected revision, preserves the file mode, flushes a
same-directory temporary file, and atomically replaces the original. It does
not create absent files or invoke a build. A mismatch returns the current
document as a conflict without writing. A separate read-only preview operation
reuses the same visibility, containment, symlink, regular-file, and one-MiB
checks for `.png` paths, verifies the PNG signature, and returns inert image
bytes without admitting them to the text save flow.

Each project browser mounts its framework viewer for that workspace. It maps
each published path directly to the viewer: the manifest reconciles the model,
a regular artifact updates only the geometry that names it, and `errors.json`
updates the separate build-failure banner. A failed targeted request reports
beside the retained model and the next publication retries normally; the browser
does not remount the viewer or interpret artifact contents.

The activity rail has interactive Model, Code, and Agents areas, in that order;
Sheets remains deferred and there is no Files area. Code shows the
Git-visible project-root navigator with an always-open root and initially
collapsed, independently operable directories. One monochrome inline-SVG icon
family distinguishes folders, Markdown, PNG, Python, and generic files. The
locally bundled Monaco editor gives each open text path its own model, tab, undo
history, and view state. Ctrl/Cmd+S sends a revision-checked save. Clean open
models accept external content through a guarded edit; dirty models preserve
maker text and expose the external document as an explicit reload conflict. A
PNG instead opens a closable read-only image tab backed by the bounded preview
operation and never creates a Monaco model. Source invalidations refresh the
tree, so an agent-created non-ignored untracked file appears without
instrumenting agent tools. Model, Code, Agents, and conversation components remain
mounted while visibility changes, preserving viewer, editor, transcript,
scroll, and draft state.

The hub holds one live-state connection to `/api/stream`. It opens with the
complete project inventory, including each usable screenshot's content revision,
and then carries project opening, open, failed, closed, and screenshot-revision
changes. A workspace holds one connection to its session stream. It
opens with that broker's complete run state and full ordered conversation, then
carries only that project's subsequent changes, including source invalidations,
runtime/idle state, and normalized agent activity.
Neither scope polls live state, and the hub never receives a conversation. A
broker subscribes the connection before reading the snapshot, and its snapshot
carries the explicit latest event sequence so the browser can discard that
hand-off overlap exactly once.

Project cards use a revision-cache-busted request for that canonical image and
fall back to their striped placeholder if it is absent or cannot be decoded.
Screenshot changes are hub metadata only; they do not enter project conversation
or broker history.

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
artifact events are not recoverable broker state. Reconnect also re-lists the
source tree and re-reads every open source path, using the same clean-update or
dirty-conflict rule as a live invalidation. Bounded normalized activity is part
of the snapshot and repopulates the Agents feed after reconnect; generic broker
event history remains display metadata rather than a recovery log.

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
