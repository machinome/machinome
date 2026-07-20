## Context

Sprint 001 calls for a browser-based shop floor whose menu makes the live
shop understandable to the pilot.  The feature needs an authoritative agent
roster and an explicit agent lifecycle.  The lifecycle must distinguish an
agent that exists and is available from one that has actually accepted work;
dispatch alone is not evidence that work has started.

The pilot needs a small, observable slice now.  It must fit the local service
and browser viewer while leaving the later chat, project browser, and artifact
viewer free to evolve.

## Goals / Non-Goals

**Goals:**

- Maintain an authoritative roster for each active shop run.
- Give the menu a stable initial roster and live updates without a page reload.
- Make acknowledgment and completion the authoritative boundaries for the
  visible active and waiting states.
- Preserve a concise lifecycle history suitable for diagnosing a stale or
  missing agent report.

**Non-Goals:**

- Launching, scheduling, or supervising Codex agents.
- Routing pilot chat messages or allowing direct chat with non-foreman agents.
- Project browsing, artifact rendering, or solid-node widget integration.
- Inferring agent activity from a transcript, process list, or timeout.

## Decisions

### Give each manifested agent a run-scoped identity and explicit state

The broker will create a roster entry when the orchestrator manifests an agent
for a run and remove it when the orchestrator reports that the agent has
stopped.  Each entry has a stable role identifier, a display label, and one of
`waiting` or `active`.  A browser reconnect receives the current roster, not
only events emitted after it connected.

This gives the pilot a deterministic view and avoids treating a process that
has merely been dispatched as working.  A global roster was considered, but
would mix agents from separate shop runs and make historical state ambiguous.

### Make agent reports the state-transition authority

The broker records an assignment as pending without changing the visible
state.  The agent's acknowledgment of that assignment changes it to `active`.
Its completion report changes it back to `waiting`.  Reports are accepted only
when they identify a manifested roster entry and the relevant assignment.

Using dispatch as the active signal was rejected because it cannot prove that
an agent received the work.  Inferring activity from host-session inspection
was rejected because it is non-portable and can disagree with an agent's work
contract.

### Publish roster snapshots and lifecycle changes on the existing live path

The service will expose the current roster in the run representation and emit
structured roster lifecycle updates on the viewer's live event stream.  The
browser will render its initial state from the snapshot, then apply updates as
they arrive.

This preserves one live-update mechanism for the first interface slices and
allows the UI to recover after reconnecting.  Browser polling was considered
but would make the real-time activity goal less direct and duplicate the event
stream's ordering concerns.

### Build the browser interface with TypeScript, React, and Vite

The shop-floor frontend will be a TypeScript React application scaffolded and
built with Vite.  The service will serve the built frontend for normal local
use, while the Vite development server supports rapid frontend work.  The
roster will be a typed React component fed by the initial run representation
and the live-update path.

React provides a durable component boundary for the menu, future artifact view,
and chat, while Vite supplies a small, standard development and production
build workflow.  TypeScript makes the broker-to-frontend roster representation
explicit at that boundary.  Extending the current static browser script was
rejected because Sprint 001 already calls for three independently evolving
interface areas.

## Risks / Trade-offs

- [An agent exits without reporting completion] → Remove it when the
  orchestrator reports its stop; do not silently convert its unfinished work
  into a completion report.
- [Duplicate or out-of-order reports] → Associate reports with assignments and
  make repeated lifecycle reports idempotent.
- [A browser reconnect misses a live event] → Render the authoritative current
  roster before consuming later updates.
- [An initial event transport constrains later orchestration] → Keep the roster
  model behind the broker boundary and treat the event transport as an adapter,
  not a user-facing requirement.
- [Frontend tooling adds a JavaScript build step] → Pin the frontend toolchain,
  document its development and production commands, and run it in automated
  checks where practical.

## Migration Plan

Add the roster model and endpoints alongside the existing run event history.
Update the viewer to render roster state from the new representation and live
updates.  Existing callers that only publish generic events continue to work;
only orchestrators using the agent lifecycle receive the roster behavior.
Rollback is removal of the new roster rendering and lifecycle handlers, leaving
the existing event history intact.

## Open Questions

- Which roles and display labels the initial orchestrator manifests is a later
  workflow decision; this change only requires that every manifested agent be
  visible.

## Review Status

During protocol reconstruction on 2026-07-20, the pilot directed this existing
implemented change to be replayed as-is. That direction ratifies the
`shop-agent-lifecycle` behavioral specification and the four decisions in this
design for this replay.
