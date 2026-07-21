## Why

Sprint 1 made shop-floor observable and gave the maker a live foreman
conversation, but opening the shop still does not start a working agent team.
The shop needs a persistent Codex orchestration path so maker direction can
drive a foreman-managed design-and-machining pipeline while every participant
continues to receive new direction during its work.

## What Changes

- Make opening the shop start an event-driven Codex orchestrator with a
  foreman, designer, and machinist, and make closing the shop end that runtime
  with the broker.
- Give each running agent an ordered inbox for assignments, reports, and new
  instructions that remain queued until the agent reaches its next tool-call
  boundary.
- Keep standby agents idle with no active model turn, timer, periodic request,
  task tool call, or token consumption; the non-model orchestrator alone waits
  for broker events and resumes the addressed role.
- Keep assignment interpretation with the receiving agent; delivery alone does
  not imply cancellation, replacement, or another deterministic response.
- Make the foreman the sole pipeline coordinator: it directs the designer,
  starts the machinist only from a released immutable drawing, keeps the
  designer at most one increment ahead, and holds completed ahead-work until
  the machining lane is ready.
- Let specialists report progress and completion through the broker so the
  foreman can supervise the floor and continue talking with the maker while
  work proceeds.
- Add a small rolling broker-event log below agent status in the shop menu.
- **BREAKING**: Rename the `drawing-office` agent role and Codex adapter to
  `designer`; do not retain `drawing-office` as an active role identifier.
- Target the working launcher and session control at Codex only. Keep the role
  protocol and broker contract suitable for later assistant-specific adapters,
  without claiming or implementing untested Claude support.

## Capabilities

### New Capabilities

- `shop-agent-messaging`: Ordered per-agent direction, reports, queued work,
  tool-boundary delivery, and event-driven zero-token standby for a live shop
  team.
- `foreman-pipeline-coordination`: Foreman-controlled progression from design
  through machining with the designer held at most one increment ahead.

### Modified Capabilities

- `shop-floor-lifecycle`: Opening and closing the shop also starts and stops
  the persistent Codex team controlled by the shop orchestrator.
- `shop-agent-lifecycle`: Manifested agents gain queued-assignment behavior,
  and the design role is identified as `designer`.
- `foreman-conversation`: The foreman remains receptive to maker messages and
  able to respond while specialist work is running.
- `shop-browser-workspace`: The menu gains a compact rolling log of broker
  events beneath the agent roster.

## Impact

- Codex foreman, designer, and machinist role cards and `.codex` role adapters;
  the porter model role is replaced by a deterministic shop orchestrator.
- The shop launcher and its persistent Codex app-server ownership process.
- FastAPI broker state and commands for per-agent messages, assignment queues,
  async event delivery, reports, event history, and shutdown.
- Browser menu data and rendering for the rolling event log.
- Broker, CLI, orchestration, and browser acceptance tests.
- Documentation that currently names the drawing office or describes opening
  the shop as starting only the broker and browser surface.
