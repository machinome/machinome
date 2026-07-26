# Shop architecture overview

This is the reference architecture of the solid-node shop: the system as it
stands, the boundaries that hold it together, and where each concern lives.
It is the document to read **before starting any work** in this repository.

The Architecture Decision Records under `docs/adrs/` are **deltas**: each one
records a single consequential decision and its context at a point in time.
This file is the **reference**: it describes the whole that those decisions
produced. When the two disagree during a transition, the ADR says *why* a
change was made; this file says *what is true now*. Keep both accurate — update
this overview when an ADR is accepted, and write a new ADR when a consequential
boundary changes.

`AGENTS.md` remains the operating contract for *how to work here* (lanes,
worktrees, OpenSpec). This document describes *what the system is*.

## What the shop is

The shop is an **agent harness** for building 3D-printable mechanical CAD
projects with the solid-node framework. A human pilot describes intent and
makes consequential decisions; a small team of specialist agents does the
token-heavy designing, building, and research. The same harness also drives
solid-node framework development, but that is a separate discipline governed
by `AGENTS.md` and `skills/framework-change/`, not by the runtime described
here.

This checkout is both the harness source and a live workspace. The framework
itself lives under `solid-node/` (an untracked working copy) and is **not** the
shop — do not confuse the two.

## The four runtime layers

The running shop has four layers, with strict responsibility boundaries:

```text
                         HTTP (REST + SSE)
 pilot (browser)  <──────────────────────────>  BROKER
  floor/static                                  floor/app.py  (FastAPI, in-memory)
                                                     │  owns: state, conversation,
                                                     │  envelopes, event log, SSE
                                                     │  speaks ONLY portable role names
                                                     ▼
                                               internal async queue
                                                     ▼
                                               ORCHESTRATOR
                                               floor/orchestrator.py  (deterministic,
                                                non-model, zero tokens at standby)
                                                     │  portable AgentBackend protocol
                                                     ▼
                       ┌─────────────────────────────┴─────────────────────────────┐
                       │                                                            │
                 --backend codex                                              --backend hermes
                       │                                                            │
                CODEX BACKEND                                                HERMES BACKEND
                floor/backends/codex.py                                     floor/backends/hermes.py
                `codex app-server --stdio`                                  `hermes acp`
                JSON-RPC over stdio                                          ACP over stdio
                       │                                                            │
              persistent Codex threads                                 persistent ACP sessions
                ┌──────┼──────┐                                            ┌──────┼──────┐
                ▼      ▼      ▼                                            ▼      ▼      ▼
             foreman designer machinist                                 foreman designer machinist
                │      │      │                                            │      │      │
                └──────┴──────┴──────────── shared role contracts ──────────┴──────┴──────┘
                                  agents/*.md
                                  skills/*/SKILL.md
```

### Layer 1 — Broker (`floor/app.py`, ~590 lines)

An in-memory FastAPI server. It is the shop's coordination state and the only
thing the browser talks to.

- Holds agent state (`waiting`/`active`), the envelope queue, the maker ↔
  foreman conversation, and a bounded event log (last 20 events).
- Speaks **only portable role names** (`foreman`, `designer`, `machinist`). It
  has no knowledge of any backend's thread, turn, or session identifiers —
  that is ADR 0005/0006's central boundary and what keeps broker history and
  browser observability independent of the model runtime.
- Persists every envelope before delivery and serializes delivery per role.
- Enforces messaging rules: only the foreman assigns work; reports must be
  addressed to the foreman; a maker message automatically becomes a `direction`
  envelope to the foreman.
- Serves the static browser UI from `floor/static/` and the completed project
  build artifacts from the project's `_build/` directory.
- Exposes SSE streams: lifecycle (`/events/lifecycle`), the browser event
  stream (`/api/runs/shop-floor/stream`), and the orchestrator's envelope
  delivery stream (`/api/runs/shop-floor/orchestrator/stream`).

There is exactly one run, hard-coded id `shop-floor`.

### Layer 2 — Orchestrator (`floor/orchestrator.py`, ~440 lines)

A deterministic, non-model process. **It is not an agent and makes no
decisions** — it is a lifecycle owner and delivery adapter (ADR 0006).

- Composes one backend selected by `--backend {codex,hermes}`. Default:
  `codex`.
- At open, calls `backend.open_role()` for each role to create one persistent
  agent session per role, then manifests each to the broker. Sessions persist
  with **no token use while idle**.
- Subscribes to the broker's delivery queue and routes each envelope to its
  role handle: `backend.deliver()` when the role is idle, with the active
  delivery ID while it is active. It acknowledges broker delivery only after
  the backend accepts the input.
- Handles the completion race: if a delivery fails because the role already
  completed, it retries the envelope as a fresh delivery on the now-idle role.
- On backend events, records the foreman's agent messages into the maker
  conversation and tracks `turn_started` / `turn_completed` to know whether
  each role is idle.
- On close, interrupts active roles and closes them in reverse order.
- Injects runtime context at role open: the shop checkout, the active project,
  and (for the machinist) the live-model `solid develop` callback command.
- Restart recovery is intentionally absent: losing the owner closes the
  in-memory run rather than attaching a new backend to uncontrollable
  sessions.

### Layer 3 — Agent Backend (`floor/backends/`)

The `AgentBackend` protocol is the portable seam between the orchestrator and
any agent runtime. It exposes only role-level operations and events — no
vendor-specific identifiers or wire protocols escape above this boundary
(ADR 0006).

```python
class AgentBackend(Protocol):
    events: AsyncIterator[BackendEvent]

    async def start(self) -> None: ...
    async def open_role(self, role: str, context: RoleContext) -> RoleHandle: ...
    async def deliver(self, handle: RoleHandle, message: str) -> DeliveryReceipt: ...
    async def interrupt(self, handle: RoleHandle) -> None: ...
    async def close_role(self, handle: RoleHandle) -> None: ...
    async def close(self) -> None: ...
```

Common events: `role_message`, `turn_started`, `turn_completed`,
`role_failed`, `backend_failed`.

| Backend | Process | Protocol | Role primitive |
|---|---|---|---|
| `codex` | `codex app-server --stdio` | JSON-RPC over stdio | Persistent Codex thread |
| `hermes` | `hermes acp` | ACP over stdio | Persistent ACP session |

The current `CodexAppServer` in `floor/orchestrator.py` SHALL move to
`floor/backends/codex.py` and implement `AgentBackend`.

### Layer 4 — Agents (backend sessions)

The specialist roles are persistent sessions owned by the selected backend,
not processes the broker manages.

- **Role cards** (`agents/*.md`) define each role's discipline and are the
  authoritative per-role contract. They are identical across backends.
- **Backend-specific adapters** (`.codex/agents/*.toml` for Codex; Hermes
  adapter metadata for Hermes) give each role its model, reasoning effort,
  and developer instructions. The backend reads these to start sessions; the
  instructions direct the session to load its role card and named skills from
  the shop checkout. Neither backend duplicates the role cards or skills.
- **Skills** (`skills/*/SKILL.md`) are loaded once by the agent at startup.
  `skills/running-the-shop/` is the foreman's operating loop;
  `skills/solid-node-api/` is the framework's public contract;
  `skills/solid-node/` is machinist craft.

Agents talk back to the broker over HTTP through two thin CLIs that read the
`FLOOR_URL` environment variable: `floor/agent.py` (manifest, direction,
assign, acknowledge, report, complete, stop) and `floor/foreman.py` (publish to
the maker conversation).

## Roles

| Role | Kind | Responsibility |
|---|---|---|
| **pilot** | human | Establish intent, decide consequential choices, judge the result by looking at it. |
| **orchestrator** | deterministic process | Own the selected backend, route envelopes, open/close role sessions. No decisions. |
| **foreman** | agent session | Manage shop-floor work, coordinate specialists, own pipeline transitions, talk to the maker. Does **not** own processes or machine parts. |
| **designer** | agent session | Maintain the project design, release the first executable drawing quickly, then plan one evidence-producing slice ahead. |
| **machinist** | agent session | Build and test one committed released drawing; owns code, tests, and implementation evidence. |
| **librarian** | agent (on demand) | Verify a narrow external CAD-library question and file a recipe in the project. |

The foreman manages *work*; the orchestrator manages *processes*. These are
different things and must not be conflated — the foreman role card says so
explicitly.

> **Librarian note.** The librarian has a role card and backend-specific
> adapter, but it is **not** in the broker's `ROLE_LABELS` (`foreman`,
> `designer`, `machinist`), so it is not one of the orchestrator's persistent
> sessions. The foreman dispatches it as a narrower, on-demand specialist
> rather than through the standing envelope pipeline.

## Startup: fail-closed preparation (`floor/preparation.py`)

Before any agent or the HTTP listener starts, the named project is prepared
and validated. Preparation is deliberately **fail-closed**: if any stage
fails, no floor or role process starts.

1. Resolve the project name — lowercase kebab-case, must resolve to exactly
   `projects/<name>`, never a symlink, never escaping the projects directory.
2. Create or verify the repository. A missing project is scaffolded with
   `solid new`, `git init`-ed on `main`, and given one scaffold commit. An
   existing project must already be that exact repository root.
3. Build and validate the initial snapshot. `solid build root` must publish a
   complete `_build/viewer.json` whose referenced model artifacts all exist
   inside `_build/`. A build that leaves a stale snapshot unchanged is a
   failure.

Only after this does the launcher report a browser URL, so a reported URL
never opens on the no-build 404 state.

## The functional-model boundary (ADR 0004)

Floor **never imports, executes, reloads, or serves project Python source**.
The project's model is code that changes during machining; importing it into
the long-lived floor would cache module state and couple the browser service
to project execution.

The only functional-model input is the **completed `_build/` directory**,
published atomically by `solid build`. Floor serves the viewer snapshot and
its referenced model files to the browser as static artifacts. A separate
framework-owned `solid develop root --callback <url>` process (kept running by
the machinist during an assignment) POSTs an empty callback only after a
successful full replacement of `_build/`; floor treats that callback purely as
a signal to reload static output. A failed rebuild keeps the prior inspectable
result and sends no callback.

The browser owns a renderer (React + three.js, source in `floor/frontend/`,
built into `floor/static/`) that fetches only these served static artifacts.
The backend does not interpret the snapshot.

## The product pipeline

The design lives in the project repository — `docs/design.md` plus immutable
committed drawings — so a fresh session picks the project up from the repo,
not from chat memory.

1. The foreman holds one focused opening conversation with the pilot.
2. The designer writes a minimal uncommitted draft checkpoint, establishes the
   design spine, and commits a small executable first drawing.
3. The machinist builds and tests that released slice while the designer
   develops the next slice — design stays at most one increment ahead.
4. The foreman inspects code, tests, and snapshots; implementation evidence is
   reconciled into the next released drawing.

Released drawings do not move underneath the machinist. The designer owns
design documents; the machinist owns project code and tests. The pipeline
stops for the pilot only on genuinely consequential decisions.

## Repository and workspace boundaries

The checkout is also a workspace, and its boundaries are enforced.

- **One repository per project, and never the framework's.** Each CAD project
  at `projects/<name>` is its own git repository (untracked here). The
  boundary is repository membership, not directory nesting; agents verify it
  before every commit.
- The framework clone and its benches live at `solid-node/` and
  `solid-node/WTs/` (untracked) — framework code only.
- `WTs/` at the top level holds shop worktrees only (untracked).
- While the shop is experimental, product-side agents must not read any other
  mechanical project for reference; evaluation context is restricted to the
  active project and shop-provided skills.

## Operating modes

- **Full orchestrated run** (the real path): `python -m floor.orchestrator
  <project-name> --port 9000 [--backend codex|hermes]`. Runs preparation,
  starts the broker, opens the selected backend, and creates the three role
  sessions.
- **Broker only** (browser/lifecycle testing): `python -m floor
  <project-name>`. Runs preparation and serves the broker and static UI with
  no backend or agents.
- **End-to-end test**: `scripts/test-e2e` builds the frontend and runs the
  Python Playwright browser test (ADR 0002).

## Testing strategy

- **Python unit/integration tests** (`tests/`) own the broker's lifecycle,
  HTTP, SSE, configuration, orchestrator routing, and project preparation.
  Process boundaries are exercised against fixtures
  (`tests/fixtures/fake_codex_app_server.py`, `fake_solid.py`).
- **Browser E2E** uses Python Playwright against the running FastAPI app
  through `python -m floor`, asserting the public lifecycle seam (`Shop is
  open` / `Shop is closed` across restart) rather than internals. Failures
  retain trace and screenshot evidence.
- **Frontend** has a TypeScript check (`npm --prefix floor/frontend run test`).

## Current status and limitations

These are accurate as of this writing; keep them current (see `AGENTS.md`).

- The persistent broker/orchestration is implemented and tested **for
  Codex**. The multi-backend protocol and `--backend` flag are proposed
  (ADR 0006, change `multi-backend-orchestration`) but not yet implemented.
- The shop is private and experimental; roles and disciplines are being
  exercised and revised before release.
- Restart recovery is intentionally absent (ADR 0005).
- External event observability is partial: agent-to-agent reports travel the
  orchestrator's internal delivery queue, and the lifecycle SSE endpoint is a
  stub — there is no full external subscription to agent activity.
- Models are stepped-down **evaluation defaults** (foreman `gpt-5.6-terra`
  medium; designer, machinist, librarian `gpt-5.6-luna` low), chosen to test
  whether the prompts are useful before spending heavily — not settled
  performance claims. `.codex/config.toml` caps threads and depth to limit
  token-heavy fan-out.

## Where things live

| Path | What it is |
|---|---|
| `floor/app.py` | Broker: HTTP API, SSE, agent state machine, event log. |
| `floor/orchestrator.py` | Process owner; routes envelopes to the selected backend. |
| `floor/backends/base.py` | `AgentBackend` protocol, role handles, events (proposed). |
| `floor/backends/codex.py` | Codex backend: Codex app-server client (proposed extraction). |
| `floor/backends/hermes.py` | Hermes backend: Hermes ACP client (proposed). |
| `floor/preparation.py` | Fail-closed named-project preparation and validation. |
| `floor/agent.py` | CLI for agents to talk to the broker. |
| `floor/foreman.py` | CLI for the foreman to publish to the maker conversation. |
| `floor/frontend/` | Browser UI source (React + three.js + Vite). |
| `floor/static/` | Built browser UI served by the broker. |
| `agents/*.md` | Role cards — the authoritative per-role contracts. |
| `.codex/config.toml` | Codex model + concurrency defaults. |
| `.codex/agents/*.toml` | Per-role Codex adapters (model, reasoning, instructions). |
| `skills/` | Role skills and vendored OpenSpec workflow skills. |
| `openspec/` | Ratified capability specs (`specs/`) and change records (`changes/`). |
| `docs/adrs/` | Architectural decision records — the deltas behind this reference. |
| `docs/shop-history.md` | Why the designer/machinist pipeline evolved as it did. |
| `governance/` | Proposed framework contribution templates. |
| `projects/<name>/` | Mechanical projects — each its own git repo (untracked). |
| `solid-node/` | The framework working copy (untracked) — not the shop. |

## The decision records (deltas)

| ADR | Decision | Status |
|---|---|---|
| `0001` | FastAPI broker + SSE for shop-floor lifecycle. | Accepted |
| `0002` | Python Playwright for browser E2E. | Accepted |
| `0003` | Separate porter (lifecycle) from foreman (work). | Superseded by 0005 |
| `0004` | Completed `_build/` artifacts as the functional-model boundary. | Accepted |
| `0005` | One deterministic owner for the Codex app-server; broker speaks role names only. | Superseded by 0006 |
| `0006` | Generalize shop orchestration to a pluggable agent backend. | Proposed |

Read an ADR for the reasoning and context behind a boundary; read this file
for the boundary as it stands.
