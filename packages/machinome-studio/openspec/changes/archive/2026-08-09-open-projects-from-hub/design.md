## Context

`floor/__main__.py` resolves a project and a profile, prepares the project,
builds the model, and only then calls `create_app(...)` and `uvicorn.run(...)`.
Everything downstream of that assumes exactly one project for the life of the
process: `create_app` closes over one `project_root`, one `artifact_root`, one
`build_environment` and one `profile`; it constructs one `Broker`; the routes are
`/api/runs/{run_id}/...` where `run_id` is in practice the constant
`shop-floor`; `floor/agent.py` defaults `--run` to that same constant; the
watcher watches the one project; `/artifacts/{path}` serves the one artifact
root.

The reference design (`docs/design/README.md`, screens 1a and 3c) replaces the
command-line choice with a hub. That means the process outlives any one project,
several projects can be prepared and running at once, and preparation moves from
process startup into a request whose progress the maker watches in a browser.

Two things already in place carry most of this. `/api/stream` sends a complete
snapshot on every connection before live events, so a per-project stream needs
scoping, not invention. The watcher is watchdog-based rather than polling, so N
concurrent watchers cost N inotify registrations rather than N scan loops.

## Goals / Non-Goals

**Goals:**

- One shop process serves a working folder, with any number of projects open at
  once and each fully isolated from the others.
- Screens 1a and 3c implemented at the fidelity `docs/design/README.md` states.
- An agent cannot act on a project other than its own, by construction rather
  than by discipline.
- Opening and closing a project are ordinary operations of a running shop, with
  their progress and their failures visible where the maker is.

**Non-Goals:**

- Session persistence, and therefore reopening a project into its previous
  conversation. Deliberately deferred; the specs say sessions keep nothing.
- Setup screens 3a and 3b: choosing the working folder, and enabling, locating
  or installing backends. The working folder is fixed and backend reporting is
  read-only.
- Workspace screens 1b, 2a and 2b. The workspace keeps its current presentation;
  it moves to a per-project location and gains a close control, nothing else.
- Any limit, quota or scheduling across open projects.
- Lazy agent start. Opening a project starts its agents, as it does today.

## Decisions

### A session object owns everything that is per-project

`create_app` stops closing over one project. A `Session` owns what the closure
owned — project root, artifact root, build environment, resolved profile,
`Broker`, watcher task, agent processes — and a `SessionRegistry` owned by the
app holds them keyed by project name, since at most one session exists per
project.

The alternative, keeping the closure and running one process per project behind
a front controller, isolates better and was rejected as far more machinery: it
needs port allocation, child supervision, and a proxy, to solve a problem that a
dictionary solves, in a tool where every project is the same trusted maker's.

### The session identifier is opaque, and the browser never uses it

The registry is keyed by project name because the product rule is one session
per project. The *session identifier* is separate: an opaque generated value,
recorded on the session, used only to authorise agent traffic.

The browser therefore navigates `/projects/<name>` and never sees or sends a
session id — the service resolves the name to the live session. Agents use the
id and never the name. This is what makes a leftover agent from a closed session
harmless: the project name it knows resolves to a new session whose id it does
not have, and its requests are refused rather than silently applied.

Using the project name as the session id was rejected for exactly that reason.

### Agents receive the session id in their environment

`floor/agent.py` gains `--session`, defaulting from a `FLOOR_SESSION`
environment variable that the session sets when it spawns each agent process,
alongside the existing `FLOOR_URL`. `--run` and its `shop-floor` default are
removed.

The agent never states the id, so it cannot state a wrong one, and no profile
prompt or runtime skill has to teach it about sessions. This was preferred over
putting the id in the agent's prompt context: a value in a prompt is a value an
agent can copy, paraphrase, or hallucinate, and it would have meant editing
every role card under `profiles/` and `shop-skills/solid-node-api/SKILL.md` to
describe an isolation mechanism that agents do not need to understand.

Agent-facing routes become `/api/sessions/{session_id}/...`, and an unknown id
is a 404 rather than a fallback to any session.

### Opening is a request whose progress is streamed, and is all-or-nothing except for the build

`POST /api/projects/{name}/session` starts opening and returns immediately; the
hub stream carries `opening`, then `open` or `failed` with a reason. The hub is
the natural place for this, because at that moment the maker is on the hub and
the workspace cannot render a project that has no session.

Creation adds a provisional registry entry before preparation begins. Hub
snapshots and events expose it with the chosen profile and a `creating` state,
even before its directory exists, so every connected browser can render the
same immediate card. Once the project is ready, the ordinary `open` event
replaces that provisional state; a failure replaces it with the reason.

Profile resolution, project preparation and agent start are fatal: on failure
the partially built session is torn down completely and the project is reported
not open. The initial model build is not fatal — the session opens and the
workspace shows the build error. Otherwise a project whose model does not
compile could never be opened, and the shop is exactly where a maker would go to
fix it; the workspace already renders `modelBuildError`, so this costs a
condition rather than a feature.

This preserves the substance of the old fail-closed guarantee — no partial
session ever exists — while dropping the part that only made sense when one
project was the whole process.

### Two stream scopes, one existing mechanism

`/api/sessions/{id}/stream` is today's `/api/stream` bound to a session's
broker: same snapshot-then-events shape, same client code. `/api/stream` becomes
the hub stream, carrying the project list and open-state changes and nothing
else — a hub page is never sent another project's conversation.

Reusing one stream for both was rejected: it would send every maker every
project's traffic and put the filtering in the browser.

### Nothing is persisted, and last-opened is not invented

There is no store. The project list is derived from the filesystem on each
listing: directory entries under the working folder, name validity, whether the
entry is a Git repository root, the declared profile from `pyproject.toml`,
branch from `git rev-parse --abbrev-ref HEAD`, and — in place of the design's
`4m ago` last-opened — the last commit time, which is real, free, and arguably
more useful. Open state comes from the registry, which is memory.

A small JSON index would have matched the design literally and would have been
the thing session persistence later grows into. It was rejected for this cycle
as a store introduced for one cosmetic field; the later persistence change can
introduce one deliberately, with the durability question in front of it.

### Backend reporting is observation only

`floor/backends/` gains a probe per backend: `shutil.which` for the executable,
one version invocation, and the configured model from the profile. The hub
reports found or missing automatically when it loads. The service keeps
`POST /api/backends/detect` as a read-only re-probe operation, but the hub does
not expose a manual detection control. No enable flag, no manual path, no
persisted backend settings — those are 3b, and adding them here would mean
introducing the settings store this cycle otherwise avoids.

### The project grid has explicit density and card proportions

The hub uses four columns at viewport widths of 1500 pixels and above, three
columns by default, two at 900 pixels and below, and one at 700 pixels and
below. Project cards and the new-project tile have a 252-pixel minimum height,
with 158 pixels reserved for each project preview. These values preserve the
accepted desktop proportions while keeping the existing compact breakpoints.

### The launcher loses its arguments and gains no replacement

`floor/__main__.py` keeps `--port` and its hidden test options and loses
`project_name` and `--profile`. No `--open <project>` shortcut is added: it
would be a second way to open a project, with its own failure surface in the
terminal, immediately after making the browser the way to open projects.

End-to-end tests that opened a project by launching the process open one through
`POST /api/projects/{name}/session` instead, which is also closer to what the
browser does.

## Risks / Trade-offs

- **Preparation runs inside a request, on the event loop's process.** A model
  build is CPU-heavy and blocking it would stall every other open project's
  stream. → Opening runs as a task and the build and git work run off the event
  loop, as the watcher's builds already must.

- **Concurrent agent processes grow without bound.** Five open Fordesmac
  projects is twenty backend sessions; the maker can reach that in five clicks,
  and nothing warns them. → Accepted deliberately: a cap is complexity for a
  problem that has not been observed. The close control is prominent, and the
  hub shows exactly what is open.

- **`/artifacts/{path}` becomes session-scoped.** The viewer bundle and
  `viewer.json` URLs change shape, and the three.js viewer and the S1 bridge
  build those URLs. → Route artifacts under the project location the workspace
  already lives at, so the change is a prefix rather than a new scheme.

- **Closing discards a conversation with no way back.** A maker who closes
  mid-work loses the thread entirely, and there is no undo. → The workspace
  warns before closing while an agent holds an assignment, and this is the
  strongest argument for the persistence change that follows.

- **Deriving the list on every request costs a `git` invocation per project.**
  A working folder with many projects makes the hub slow. → Two cheap
  invocations per project, only when the hub is listed; if it ever bites, it is
  a cache, not a schema.

- **The unopenable-project card is a state the design never drew.** Rendering it
  badly is worse than the silence it replaces. → Build it from tokens the design
  does specify, and say plainly what is wrong and what the maker can do.

## Migration Plan

The shop is private and experimental, and its only operator is the pilot, so no
compatibility shim is warranted. `python -m floor.orchestrator <project>
--profile <p>` stops working in the same commit that makes the hub work, and
`AGENTS.md`, `skills/running-the-shop/SKILL.md`, `README.md` and
`docs/architecture-overview.md` change with it. Rollback is reverting the
change; no data exists to migrate, because sessions persist nothing and projects
are independent repositories the shop only reads and prepares.

## Open Questions

None outstanding. Session persistence, the setup screens, and the redesigned
workspace are each deferred deliberately rather than unresolved.
