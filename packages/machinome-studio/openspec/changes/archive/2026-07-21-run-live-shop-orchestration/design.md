## Context

The existing FastAPI process owns one in-memory shop run, conversation history,
agent roster, lifecycle transitions, and browser SSE events. It does not own
agent sessions, addressed messages, reports, assignment queues, or event
history. The current porter role can start the service and the current Codex
configuration defines custom foreman, drawing-office, and machinist agents,
but it does not provide a runtime that can deliver new work into those sessions.

Codex app-server exposes thread lifecycle and turn control, including
`thread/start`, `turn/start`, `turn/steer`, `turn/interrupt`, and event
notifications. A design spike against installed Codex 0.144.6 established the
ownership boundary:

- an independent app-server process could discover and read another process's
  active thread and turn, but saw it as `notLoaded` and `turn/steer` failed with
  `thread not found`;
- the app-server process that owned the active turn accepted the identical
  steer in 0.5 ms while a six-second tool call was running, and the agent
  incorporated the new marker after that tool completed; and
- persisted rollout metadata exposed subagent lineage, but
  `thread/list(ancestorThreadId=...)` returned no descendants for two known CLI
  parent sessions in this build.

Session inspection is therefore useful observability but not a control plane.
The shop must own the app-server process that owns every controlled role thread.
This also removes the need for a model-driven porter session or an agent-side
broker receive loop.

The shop remains private and experimental. This change provides one tested
Codex path. The broker behavior and role protocol should not depend on Codex
payloads, but no claim is made that Claude or another assistant can launch the
same floor until an adapter can be exercised there.

## Goals / Non-Goals

**Goals:**

- Make one “open the shop” request start the broker and a persistent foreman,
  designer, and machinist under deterministic orchestrator lifecycle control.
- Deliver new direction between task tool calls and keep idle role threads
  without an active model turn, polling, or token consumption.
- Give foreman one authoritative view of maker messages, specialist reports,
  lifecycle events, and pipeline state.
- Keep design and machining concurrent without allowing the design lane to
  advance more than one increment or mutate active machining work.
- Expose bounded, low-detail broker activity in the browser.
- Replace the drawing-office role name with designer throughout the working
  shop and its Codex adapter.

**Non-Goals:**

- A Claude, cloud-agent, IDE-specific, or generic OpenAI API launcher.
- Direct maker conversation with designer or machinist.
- Including the librarian in the initially opened team.
- Durable recovery of agent mailboxes or sessions after the shop process exits
  or crashes.
- Automatic semantic interpretation of new direction as cancellation,
  supersession, priority, or completion.
- Letting the designer dispatch the machinist.

## Decisions

### One deterministic orchestrator owns one Codex app-server

Replace the porter model role with a persistent non-model shop orchestrator.
Opening the shop starts FastAPI and one Codex app-server process, then creates
one role thread each for foreman, designer, and machinist through that same
app-server. The orchestrator records the returned runtime handles in memory:

```text
role -> {thread_id, active_turn_id, delivery_state}
```

The broker addresses portable role names and never stores or exposes Codex
thread or turn identifiers. The orchestrator is the only adapter that translates
between those domains. Because crash recovery is out of scope, the mapping is
not persisted: losing the owning process closes the run instead of attempting
to attach a new app-server to sessions it cannot control.

The orchestrator makes no pipeline or message-meaning decisions. Foreman owns
workflow policy; each recipient interprets delivered direction. The process
only owns lifecycle, ordered delivery, app-server calls, and cleanup. On close
it interrupts active turns, closes all three threads through their owning
app-server, stops app-server, and then stops FastAPI. Partial open unwinds every
started resource in reverse order.

Alternatives rejected:

- Inspecting `~/.codex/sessions` as Lazyagent does can recover identifiers and
  lineage for observation, but the spike proved that a separate app-server
  cannot steer the discovered active thread.
- A root porter agent plus CLI-spawned subagents makes thread ownership depend
  on another Codex process and spends a fourth model-thread slot on lifecycle
  work that is deterministic.
- Recursively launching independent `codex` CLI processes reproduces the same
  cross-process control failure and requires fragile terminal automation.

### The orchestrator converts broker events into Codex turns

The broker persists every envelope before acknowledging the sender and emits
one ordered event on its existing async event channel. The orchestrator keeps
one persistent event subscription and serializes delivery per recipient role.
For each next undelivered envelope it consults the role's runtime state:

- if the role is idle, call `turn/start` with the envelope as new input;
- if the role has an active regular turn, call `turn/steer` with that thread ID
  and the expected active turn ID; and
- if the expected-turn precondition loses a completion race, re-read the
  owning runtime state and deliver the still-unacknowledged envelope through
  `turn/start` once the role is idle.

The broker advances delivery only after the owning app-server accepts the
input, preserving exactly-once ordered presentation within the in-memory run.
Steering during a task tool call does not cancel or preempt that call. Codex
queues the added input within the same turn and presents it when the tool
returns, before the model can choose another task action. The recipient then
decides what the message means under its role authority.

Agents still use the broker command surface to acknowledge and complete
assignments, send direction, and report to foreman. They never receive or poll
the broker themselves. Their outgoing broker action creates an event; the
orchestrator delivers it to the addressed role through the same turn routing.

### Standby means no active model turn

After a role finishes a turn, its Codex thread remains owned and ready but has
no active turn. No model invocation, agent tool call, token use, pending agent
HTTP request, timeout, or polling loop exists during that interval. The single
orchestrator event subscription waits asynchronously in FastAPI infrastructure
for a new broker event or shutdown and starts the addressed role only when work
arrives.

The event stream has no application polling interval or periodic response.
Transport failure may reconnect with infrastructure-level backoff, but it must
not resume any agent or lose the broker delivery cursor. Tests prove that an
idle interval produces no `turn/start`, `turn/steer`, agent tool call, or token
usage event, and that one addressed event produces exactly one accepted turn
delivery.

Alternatives rejected:

- A long-running agent receive tool cannot inject new model input and exhausts
  when it returns, so it is not a persistent control channel.
- Timer-based broker polling wastes infrastructure and violates the required
  event-driven standby even if it consumes no model tokens.
- Sending Codex input without first recording a broker envelope would bypass
  the floor history and foreman's authoritative event view.
- Treating every message as an interrupt would impose semantics the sender and
  recipient did not request.

### The broker separates direction, assignments, and reports

Store immutable envelopes with a global sequence, kind, sender role, recipient
role, concise body, and optional assignment identity. The portable kinds are:

- `direction`: available to the recipient at its next work boundary and
  never changes lifecycle state by itself;
- `assignment`: ordered work owned by the foreman, with at most one assignment
  acknowledged active per recipient and later assignments held in a pending
  queue; and
- `report`: specialist progress, finding, or completion information addressed
  to foreman.

Maker conversation remains its existing dedicated contract. Submitting a
maker message records the conversation entry and emits an event for delivery
to the foreman role. The browser still offers no specialist composer.

An assignment to a waiting agent becomes available immediately but leaves the
agent visually waiting until acknowledgment. An assignment to an active agent
is recorded but withheld as future work until completion of the active one.
Ordinary direction and reports are not withheld behind an assignment and
therefore can influence ongoing work at the next boundary.

HTTP schemas and CLI flags are implementation interfaces, not behavioral
requirements. They should be thin translations over the same broker methods
so tests can exercise the state machine without running a browser.

### Foreman is the only pipeline dispatcher

The designer never sends an assignment to the machinist. It reports released
or draft state to foreman. The foreman uses those reports and the immutable
drawing metadata to issue each specialist assignment:

1. Assign designer to release the smallest first drawing; machinist waits.
2. After release, assign machinist that exact drawing and assign designer one
   planning-ahead draft concurrently.
3. If designer finishes first, leave it waiting with that one draft.
4. After machinist completes, assign designer a reconciliation pass using the
   machining evidence.
5. Only after designer releases the reconciled drawing may foreman assign the
   next machining increment and another single planning-ahead pass.

The broker may hold a later assignment, but it does not infer this pipeline or
promote a draft. This keeps orchestration policy in the foreman skill and role
card, where project evidence and maker decisions are available.

The alternative—designer dispatches machinist—shortens one handoff but splits
authority, lets ahead-work reach the machining lane before reconciliation, and
makes it harder to incorporate new maker direction safely.

### Broker events have live delivery and bounded history

Every lifecycle transition, envelope creation/delivery, and model change emits
one globally sequenced broker event. Keep the most recent 20 display summaries
in an in-memory bounded deque and return them with the current run snapshot;
continue using SSE for live additions. The number is a presentation knob, not
a workflow decision, and can later become configurable without changing the
contract.

Display summaries include event kind, involved role or roles, and assignment
identity when useful. They exclude full direction and report bodies so the
left bar remains small and does not duplicate private working context. The
React menu renders one compact box per event below the roster and discards its
oldest item when the bound is exceeded.

### Designer is a clean role rename

Rename `agents/drawing-office.md` and `.codex/agents/drawing-office.toml` to
their designer equivalents and update their frontmatter, descriptions,
instructions, skills, shop process, adapters, tests, and current documentation.
Do not leave a compatibility custom agent named drawing-office: silently
accepting both names would produce duplicate identities and ambiguous broker
addressing. Historical sprint and archived OpenSpec records remain historical
and are not rewritten.

## Risks / Trade-offs

- **A completion race can choose the wrong delivery operation** → Serialize
  per-role delivery, require the expected active turn ID for steering, and
  leave the broker envelope unacknowledged until app-server accepts it.
- **An idle event subscription can make shutdown look hung** → Shop shutdown
  closes the orchestrator subscription before it closes role threads and
  verifies that every owned process exits.
- **A failed partial open can strand a process or thread** → Record every
  started resource in orchestrator order and unwind them in reverse before
  reporting failure.
- **Queued future work may be stale after new maker direction** → Only foreman
  creates assignments; direction does not auto-promote queued work, and
  foreman can explicitly withdraw or replace pending assignments without
  changing active work implicitly.
- **A fourth role changes runtime capacity and workflow** → Librarian is
  deliberately out of scope and requires a later exercised design.
- **In-memory queues disappear on crash** → Recovery across a closed or crashed
  floor is explicitly out of scope; durable project files and commits remain
  the source of mechanical truth.
- **Codex app-server behavior evolves** → Confine native thread and turn
  operations to the orchestrator adapter, pin acceptance evidence to the
  exercised Codex surface, and keep broker envelopes role-addressed and free of
  Codex identifiers.

## Migration Plan

1. Add red broker and CLI tests for ordered inboxes, active-plus-pending
   assignments, event-driven delivery, reports, shutdown, and bounded event
   history.
2. Implement the broker state, outgoing agent commands, and persistent async
   event channel without changing the existing maker conversation or browser
   contract.
3. Add red Codex orchestration acceptance coverage, then implement one
   app-server-owning orchestrator that starts, routes to, idles, interrupts, and
   closes the three role threads without an agent receive loop.
4. Rename drawing-office to designer across live adapters and documentation,
   while leaving archived records intact.
5. Add red browser coverage and render the rolling event log.
6. Run focused tests, the complete Python suite, browser acceptance tests, and
   a manual open/direct/parallel-work/close exercise.

Rollback is one shop commit revert while the change is still experimental.
Because no queue is persisted beyond a run and no compatibility alias is
created, rollback requires closing any active shop before returning to the old
roles and broker.

## Open Questions

None. The pilot selected a Codex-only first implementation, one non-model
orchestrator owning all controlled app-server threads, role-only broker
addressing, foreman-owned pipeline dispatch, role-level interpretation of
queued direction, event-driven zero-token standby, a designer rename, and
minimal rolling browser observability.
