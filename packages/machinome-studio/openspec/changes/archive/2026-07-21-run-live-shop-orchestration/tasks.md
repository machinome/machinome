## 1. Prove broker and orchestration behavior red

- [x] 1.1 Extend broker tests first to fail for ordered per-agent direction, non-mutating direction delivery, one active plus queued assignments, ordered specialist reports to foreman, and rejection of unknown roles.
- [x] 1.2 Add command- and event-level tests first to fail until persisted envelopes emit once in order, remain unacknowledged until accepted by a recipient adapter, and expose assignment acknowledgment/completion and specialist reporting without any agent receive command.
- [x] 1.3 Add a Codex app-server acceptance fixture first that fails until one owning process manifests persistent foreman, designer, and machinist threads, uses start for idle delivery and steer for active delivery, incorporates direction after an active tool call, records no turn or token use during standby, rejects cross-process steering as unsupported, and closes every owned thread and process.
- [x] 1.4 Extend browser unit and Playwright coverage first to fail until bounded broker-event history loads beneath the roster, updates live, and rolls off its oldest entry.

## 2. Build the broker coordination plane

- [x] 2.1 Add immutable sequenced direction, assignment, and report envelopes, per-role delivery state, active and pending assignment state, and one async broker event channel that wakes the orchestrator only for new events or shutdown.
- [x] 2.2 Extend lifecycle operations so waiting agents can acknowledge available work, active agents retain their current assignment while later work queues, completion exposes the next assignment, and direction alone never changes work state.
- [x] 2.3 Add the role-neutral outgoing agent command surface for manifest, send direction, acknowledge, report, complete, and stop operations, sharing broker state-machine behavior with the HTTP surface and intentionally providing no agent receive loop.
- [x] 2.4 Implement the orchestrator event subscription as one indefinite FastAPI async wait with no sleep, timeout, periodic request, or keepalive completion; close it during shutdown and preserve per-role delivery cursors across transport reconnection within the run.

## 3. Run the persistent Codex shop team

- [x] 3.1 Replace the porter model role with a deterministic Codex orchestrator that starts FastAPI and one app-server, creates foreman, designer, and machinist role threads through that owner, keeps role-to-thread and active-turn handles only in memory, verifies manifestation, and unwinds every resource under failure and shutdown.
- [x] 3.2 Rename the live drawing-office role card and Codex adapter to designer, update role identifiers and dispatch language, and add coverage proving `drawing-office` is no longer addressable.
- [x] 3.3 Implement per-role serialized routing so an idle role receives `turn/start`, an active regular turn receives `turn/steer` with its expected turn ID, completion races retry the still-unacknowledged envelope on the now-idle role, and broker delivery advances only after app-server acceptance.
- [x] 3.4 Update the foreman role and `running-the-shop` skill so only foreman dispatches specialists, starts machining from an immutable released drawing, runs one designer draft concurrently, waits when design finishes first, and reconciles before the next machining assignment.
- [x] 3.5 Prove the Codex acceptance path green for maker-to-foreman direction, foreman-to-designer direction, released-drawing dispatch to machinist, one-ahead parallel work, mid-task message delivery, specialist reports, and orderly close.

## 4. Add bounded floor observability

- [x] 4.1 Give every displayable broker event a global sequence and minimal summary, retain the most recent 20 summaries, and include current history in the run snapshot while preserving live SSE delivery.
- [x] 4.2 Render one compact event box per summary below agent status, exclude full direction and report bodies, and preserve responsive menu access.
- [x] 4.3 Make the focused browser tests and complete Playwright shop-floor suite green for initial history, live events, rolling eviction, reconnect, and the renamed Designer roster entry.

## 5. Align durable shop knowledge and verify

- [x] 5.1 Update current README, CLAUDE bootstrap guidance, AGENTS entry points, listener documentation, and role references to describe the Codex-only persistent team and designer name without rewriting archived sprint or OpenSpec history or claiming Claude support.
- [x] 5.2 Record the accepted single-owner app-server, role-only broker addressing, in-memory runtime registry, and foreman-dispatch decisions in an ADR after implementation evidence confirms them.
- [x] 5.3 Run the focused broker and event tests, Codex ownership and routing acceptance fixture, complete Python suite, frontend checks, Playwright acceptance suite, and a manual open/direct/standby/parallel-work/close inspection; report measured standby turn and token counts and any tool-boundary coverage the runtime cannot expose directly.
- [x] 5.4 Sync the accepted delta specs to baseline, archive the completed OpenSpec change, and commit the implementation record only after every required behavior and migration check passes.
