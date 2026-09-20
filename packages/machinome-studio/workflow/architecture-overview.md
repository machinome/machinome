# Machinome Studio architecture overview

Machinome Studio is a local agent harness for mechanical CAD projects. A
human pilot owns intent and consequential choices; the runtime opens a
project hub over one working folder and can hold several isolated project
sessions, each with a repository-owned validated team profile. `AGENTS.md`
governs how this repository is changed. This document describes the running
system.

## Product identity and ecosystem boundary

Machinome means the source code of one machine and, collectively, the body of
source code for machines. Machinome Studio is the experimental local harness;
the independently versioned framework, viewer, and mechanics repositories are
`machinome`, `machinome-viewer`, and `machinome-mechanics` under the
Machinome organization (ADR 0031). Their Python distributions are `machinome`,
`machinome-viewer`, and `machinome-mechanics`. The studio invokes the
`machinome` command from its own Python environment and finds project runtime
choices only under `[tool.machinome-studio]`; a former
`[tool.libresolid-studio]` table is a migration error, never silently ignored.

The studio and the two optional packages remain unpublished. Historical ADRs,
archived changes, and past release evidence retain their former names; current
source, contracts, workspace paths, and guidance use the Machinome identity.

## Project hub and sessions

The process starts without preparing a project, building a model, or starting
an agent. Both entry points first verify that the `openspec` CLI resolves and
runs, and refuse to start when it does not, naming the prerequisite and how to
install it; nothing is bound and no project is opened. There is no reduced mode
in which projects open without their spec record (ADR 0027). Both entry points
require `--projects-dir`, which names the exact external catalogue served by
`floor/app.py`. The runtime neither appends a
directory name nor derives a location from cwd or Git metadata.

Its inventory is derived from the filesystem, one folder at a time, and every
entry is identified by its path under the working folder — `sandbox/windmill`
for a nested project, `3DPrintedClocks/wall_clock_01` for one declared model
(ADR 0029). An entry is a folder, an openable project, or an unopenable
directory. A directory that is not a repository but holds one anywhere below it
is a folder of those projects; a repository whose manifest declares more than
one model is a folder of those models, read straight from `pyproject.toml`
rather than through `machinome models`; a repository declaring one model or none is
a single project. Every folder also reports the entry path and preview revision
of up to three entries, so its card can stand on those pictures rather than a
folder glyph: a multi-model project reports the first three models it declares,
and a grouping directory reports the first three openable entries it holds,
found by descending it in listing order and abandoning the walk once the card
is full. Exact independent Git repository roots also report their declared profile,
branch, and last commit time. Regular files are omitted;
malformed project configuration and directories that hold no project remain
visible with an unopenable reason. Project directory names have no stylistic
constraint.

`resolve_entry` is the single gate between a requested path and the filesystem.
It refuses empty, dot and absolute segments, walks only inside the working
folder, and stops at the first directory that is a repository root; anything
after that names a model the manifest declares. Because the walk stops there,
the hub never lists a directory inside a project, and a model name cannot
collide with one.

`floor/sessions.py` owns a `SessionRegistry` keyed by entry path and also
indexed by an opaque generated session identifier. An entry has at most one
session; different entries have no cardinality limit, including two models of
one repository, which run as two sessions with their own agents, conversation,
build, watch and preview over one shared checkout. Each `Session` owns the
verified project root, the model it was opened for and that model's artifact
root, build environment, resolved profile,
broker, orchestrator and backend processes, delivery/event tasks, source
workspace, source/model/artifact watchers, and filesystem observer. Opening is asynchronous and
reported on the hub stream. Profile resolution, preparation, and agent start
are fatal and tear down partial resources; a failed initial model build is
recorded in the session and does not prevent its workspace from opening. A
session opened on an existing publication carries a build behind it: the broker
holds the in-flight flag, so the hub listing and the session stream cannot
disagree, and a `model_build_settled` event clears it on every outcome —
including a build that publishes nothing, which moves no artifact and would
otherwise signal nothing. Both the hub card and the workspace say the model is
being brought up to date while that flag is set, so a publication that is not
yet current is never presented as settled. Closing cancels and awaits that
build, so it cannot outlive its session.

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
The project's `[tool.machinome-studio]` `profile` value selects it;
otherwise the shop uses `fordesmac`. The launcher provides no override. A
profile is strict trusted configuration: it declares the
human label, one user-facing agent, standing roster, direct or delegated work
mode, prompt paths, allowed skills, communication edges, and Claude
runtime defaults. The option overrides a project declaration for one run
without modifying it. The project may select backend, provider, model, and
reasoning level per agent under `[tool.machinome-studio.agents]`; the profile
tool policy remains non-overridable and is the whole authority a Claude session
holds, so no profile or project declaration can widen it or disable permission
checking. OpenCode has no profile
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
execution and file editing whatever the profile declares (ADR 0025). The
Fordesmac librarian is provisionally non-functional because this surface
intentionally has no web or external documentation tools, pending a bounded
research surface.

`OpenSpec` is a capability of its own in that vocabulary, resolving to the
floor's two OpenSpec tools. Only `builder` declares it; no other capability
reaches those tools, so a session holding the shell or filesystem capabilities
does not reach a project's spec record as a side effect.

The initial profiles are:

| Profile | Mode | Human-facing agent | Standing roster |
| --- | --- | --- | --- |
| `builder` | direct | Builder | Builder |
| `fordesmac` | delegated | Foreman | Foreman, Designer, Machinist, Librarian |

Builder keeps a durable design record inside its project: an OpenSpec root
whose capabilities name interfaces between parts, planned in one commit and
implemented, synced, and archived in a second. The discipline is stated in
Builder's own prompt and nothing on the floor gates a commit on it. The Maker
neither ratifies nor handles a spec artifact.

Runtime prompts live beside their profile. A prompt names only skills exposed
through its profile `skills/` allowlist. Shared runtime skills live under
`shop-skills/`; repository operator and development skills remain under
`skills/`. Each declared agent receives the exact verified project repository
root, while prompts and skills remain shop-owned outside that project.

Every allowlisted skill declares its own `name` and `description` in
`SKILL.md` frontmatter, and profile loading resolves the two together with the
skill's directory. A skill that cannot describe itself fails validation,
because a session chooses a skill from its announcement alone.

## Runtime layers

```text
browser hub <--> SessionRegistry <--> Session (one per open entry)
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
selected model, effort, and permitted tools into its supported command fields.
It writes a strict MCP config, omits `--safe-mode` because that flag disables
MCP, and empties the built-in tool set. It grants the resolved `mcp__floor__*`
names — together with `mcp__floor__load_skill` when that agent declares a skill
— by name, and withholds every remaining floor tool, because the built-in tool
option does not filter MCP tools. A role without a concrete tool list does not
open. Because Claude emits no init
before its first user input, project opening manifests the process after the
short exit grace without a warm-up turn. The first real broker envelope triggers
initialization, and that delivery is accepted only after `system/init` reports
the floor server connected with exactly that tool set, waiting through
transitional `pending` frames within a separate bounded readiness deadline. That
comparison is the live proof that scoping held. No session disables the
runtime's permission checking: the granted tools run without confirmation, a
withheld tool is neither advertised nor callable, and containment remains the
MCP server's project gate rather than operating-system sandboxing (ADR 0026).
Claude normalizes completed tool-use blocks but exposes no mutable
runtime catalogue after first use: model changes require a new process, for
which context preservation has not been verified. Its fresh-session catalogue
does permit replacement of a pristine process. These two adapters consume one resolved
runtime and never parse project or profile files or load global role adapters.

The floor MCP server is rooted at the exact active project. Every path-bearing
filesystem, Git, and machinome operation resolves and rejects escapes before
acting. It exposes text and raster reads, bounded writes, non-destructive Git
and commit operations, finite build/test, and temporary image-returning
snapshots. Its broker lifecycle wrappers can assign, direct, acknowledge,
report, and complete only through the backend-injected floor URL and opaque
session; they expose no generic network operation. Push, reset, checkout,
branch, rebase, arbitrary shell, web, and arbitrary HTTP are absent.

Two tools reach the project's OpenSpec record. `openspec_setup` initializes it,
seeds the project's house rules for writing mechanical specs, and commits, and
reports and changes nothing when the record already exists. `openspec_run`
passes an argument vector to the CLI in the project root and returns its status
and output; it is deliberately a passthrough rather than a wrapper per
subcommand, so the shop's spec does not freeze one CLI version's surface. The
guardrails act on the vector instead. Before any process starts, the server
resolves the root the CLI would use by the same nearest-ancestor walk and
refuses when it is not the project root, naming the root it would have used —
an unprepared project otherwise resolves to whatever repository contains it.
Store, global-configuration, telemetry, and shell-completion subcommands, a
`--store` argument, and any path-shaped argument escaping the project are
rejected. Archiving is refused while the change's own task record shows
unfinished work, with the incomplete tasks named and no overriding argument:
the CLI cannot gate this, since it prompts without `--yes` and archives anyway
with it.

A floor-mediated commit whose staged content lies wholly inside the spec record
carries no model content, so it skips the render, leaves the session's preview
untouched and unstaged, and reports that it did. Anything the server cannot
prove inert still renders.

`load_skill` is the one tool that reads outside the active project, and the
only tool that reads a skill. It takes a skill name, never a path, and
resolves it against a name-keyed registry the shop supplies when the server is
launched; an optional `resource` reads a file bundled beside that skill's
`SKILL.md`, contained by its directory. A session reaches it whenever its agent
declares a skill, whatever tool capabilities the profile declared — skill
loading follows skills, not capabilities — and a server holding no registered
skill does not advertise the tool at all.

Each session is told which skills it holds by name and description, not by
path or instruction text, and loads one when it needs it. Claude configures a
tool server per role and registers exactly that agent's skills; OpenCode's
server is shared by every role, so it registers the profile's whole
allowlist while each role's contract still announces only its own.

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
carries the exact profile prompt and that role's own skill catalogue as
that session's system contract; no skill's instructions travel with a delivery. For a fresh role the adapter intersects the
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
and optional effort, while the tool policy still comes from the profile. These choices are backend configuration, not broker semantics.

## Floor and browser

The service binds its listener before any project is selected, and only after
the startup preflight has resolved the `openspec` CLI. For each open
request, profile validation and runtime resolution complete before preparation
creates or verifies the named independent project repository. When that project
already holds a complete, valid publication, the session registers and its
agents start on it and the build then runs behind the open session; a project
with nothing published, or one being created, still waits for its build. Either
way the repository boundary is verified before any agent starts. A screenshot is
rendered only when the open changed what is published — decided from a digest of
the published viewer document, not by rendering and comparing afterwards — or
when the project has no valid screenshot yet, extending to opening the rule
floor-mediated commits already follow. The framework viewer bundle is resolved
once per running shop rather than per open (ADR 0028); the framework reports
it from the separately installed `machinome-viewer` package, and an
installation without that package fails the open with the framework's remedy,
installing the `viewer` extra. Where the project publishes is the
framework's answer too: preparation asks it for the build directory of the
project's default model, so a project that declares named models is prepared
on `_build/<model>/` and one that declares none on `_build/` itself. That one
directory is the session's artifact root — what it serves, watches, and
packages — and a directory outside the project fails the open. The initial build
runs through the `solid` console script installed beside the Python interpreter
running the shop, so an unrelated executable earlier on ambient `PATH` cannot
select a different framework installation. `openspec` is the single exception:
it is a Node program the shop cannot supply from its own environment, so it is
resolved from ambient `PATH` and named as an installation prerequisite. No
other shop or backend behavior depends on an ambient executable (ADR 0027). The build
runs off the event loop and reports an error into that session instead of
gating it; agent start remains all-or-nothing. The hub remains available during
opening and after any one project's failure. The browser renders
profile-provided roster labels, conversation attribution, and event summaries;
it does not encode a participant's role. The transcript is independently
scrollable, reveals newly appended messages, sends a non-empty draft on Enter,
and inserts a newline on Ctrl+Enter.

Model, Code, Agents, and Build are mounted workspace peers sharing that
conversation and the session's single snapshot/SSE connection. Agents selects one roster
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

Build consumes the framework-published distinct-piece inventory from the last
completed `viewer.json`. It selects pieces by their stable content id and uses
the first sorted model reference as the representative STL. A dedicated
Three.js scene renders that one mesh and a fixed 250 × 210 × 220 mm build
volume in common millimetre units, preserving a truthful scale relationship
while the maker orbits, zooms, and resets the view. Published quantity,
dimensions, volume, watertightness, and provenance remain framework facts. The
only derived result is an orthogonal bounding-box envelope comparison, labelled
as such rather than as a printability guarantee. Build does not slice, arrange
copies, choose orientation or supports, or estimate time, mass, or material.

The session-scoped Build download reads that same verified publication and
returns an ephemeral deterministic ZIP. It contains one canonical STL per
piece and a `README.md` listing every filename and required copy count; stable
entry names, order, timestamps, permissions, and compression make unchanged
inputs byte-identical. The route rejects malformed, escaping, missing, or
non-STL references and never writes a package into the project or `_build`.

Floor serves that publication directory's artifacts beneath the session that
owns them and, separately, one entry's preview by entry path (including for a
closed entry): the exact regular non-symlink `screenshot.png` at the root of a
single-model project, or `screenshots/<model>.png` for one declared model of a
project that has several. The screenshot is
a fixed 640x360 preview of that entry's own model, rendered through the selected
CLI after an observed successful build and before a floor-mediated commit. It
goes through `machinome snapshot --renderer web`, so a workspace needs the viewer's
`snapshot` extra and its Chromium; `scripts/setup` installs both, and a refusal
is logged rather than swallowed. Rendering and
staging are best-effort: they never turn a valid build or Git commit into a
failure. Every session owns a filesystem observer with separate source and
artifact handlers. Qualifying Python changes outside `_build` settle into one
`machinome build`, regardless of whether the writer is an agent, the Code
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
synthesized from those paths. The listing also names the project-relative file
the session's model is declared in, read at preparation from the reference
`machinome models --json` reports and resolved to a file inside the project; the
browser opens that file once per session so the Code area starts on the
assembly being shown. A reference that resolves to no file is not an error. Read and save revalidate Git visibility, reject
escapes, symlinks, and non-regular files, and accept at most one MiB of UTF-8
text. A read returns the SHA-256 byte revision. A save runs under the session's
source lock, compares the expected revision, preserves the file mode, flushes a
same-directory temporary file, and atomically replaces the original. It does
not create absent files or invoke a build. A mismatch returns the current
document as a conflict without writing. A separate read-only preview operation
reuses the same visibility, containment, symlink, regular-file, and one-MiB
checks for `.png` paths, verifies the PNG signature, and returns inert image
bytes without admitting them to the text save flow.

Each project browser mounts its framework viewer for that workspace, and
mounts that same viewer's own assembly navigator into the Model context
panel, over the mounted viewer rather than beside a copy of it. It maps
each published path directly to the viewer: the manifest reconciles the model,
a regular artifact updates only the geometry that names it, and `errors.json`
updates the separate build-failure banner. A failed targeted request reports
beside the retained model and the next publication retries normally; the browser
does not remount the viewer or interpret artifact contents. The navigator is
themed by the workspace's own stylesheet, entirely through the viewer's
published `--machinome-nav-*` custom properties and its two named classes for the
two accents a shared variable cannot carry; the browser specifies none of the
navigator's tree, keyboard, or visibility behaviour and holds no assembly
state of its own — no focused root, no hidden set, no expansion — and
disposes the navigator when the viewer it was mounted over goes away or the
panel unmounts.

The activity rail has interactive Model, Code, Agents, and Build areas, in that
order; there is no Files or deferred Sheets area. Code shows the
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
instrumenting agent tools. Model, Code, Agents, Build, and conversation components remain
mounted while visibility changes, preserving viewer, editor, transcript,
scroll, selection, camera, and draft state.

The hub holds one live-state connection to `/api/stream`, scoped by the folder
it is listing. It opens with that folder's complete inventory — its folders, its
projects, and each usable screenshot's content revision — and then carries
opening, open, failed, closed, and screenshot-revision changes, each naming the
entry's path and the folder it belongs to so a browser can ignore a change to a
folder it is not showing. A workspace holds one connection to its session stream. It
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
dirty-conflict rule as a live invalidation. Build also re-reads `viewer.json`,
retaining its selection when the content id remains. Bounded normalized
activity is part of the snapshot and repopulates the Agents feed after
reconnect; generic broker event history remains display metadata rather than a
recovery log.

## Workspace boundaries

Each `<projects-dir>/<name>/` directory is an independent Git repository. The
required catalogue directory is an external runtime input and may be unrelated
to the shop installation. In this repository's development workspace, the
framework checkout belongs under `machinome/`; framework worktrees belong
under `machinome/WTs/`; the browser viewer's independent repository belongs
under `machinome-viewer/` (the framework's `viewer` extra, AGPL-3.0-only,
with its own OpenSpec and decision records); shop worktrees belong under
`WTs/`. Runtime agents use
only their session's verified project root plus their selected profile contract.
The session identifier is the routing boundary as well as the process
environment supplied to the agent; runtime agents do not inspect sibling
mechanical projects.
