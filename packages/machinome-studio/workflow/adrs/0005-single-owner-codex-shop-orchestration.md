# ADR 0005: Use one app-server owner for live Codex shop orchestration

**Status:** Accepted

**Date:** 2026-07-21

**Supersedes:** ADR 0003

**Origin:** OpenSpec change `run-live-shop-orchestration`

## Context

Shop-floor needs persistent Foreman, Designer, and Machinist contexts that can
receive ordered broker input while working and remain available without token
use while idle. A model-driven porter and agent-side receive loops cannot
provide that control: a receive tool ends when it returns and cannot inject
new model input in the background.

An app-server spike established the ownership boundary. A second app-server
could discover and read an active thread and turn but saw the thread as
`notLoaded` and could not steer it. The app-server owning the same active turn
accepted `turn/steer` during a six-second tool call, and the agent incorporated
the new input after the tool completed. The implementation acceptance fixture
also proves start-when-idle, steer-when-active, no-request standby, completion
race recovery, cross-process rejection, and reverse-order cleanup.

## Decision

One deterministic, non-model shop orchestrator SHALL own one Codex app-server
process and create the Foreman, Designer, and Machinist threads through that
owner. It SHALL keep role-to-thread and active-turn handles in memory and SHALL
not store Codex identifiers in the broker.

The broker SHALL address portable role names and persist each envelope before
delivery. The orchestrator SHALL serialize delivery per role, use `turn/start`
when that role is idle, use `turn/steer` with the expected turn ID while it is
active, and acknowledge broker delivery only after app-server accepts the
input. A completion race leaves the envelope unacknowledged and retries it as a
new turn on the now-idle owned thread.

Idle roles SHALL have no active model turn. Only the non-model orchestrator
waits on FastAPI's asynchronous broker event channel. The Foreman alone owns
pipeline transitions; the orchestrator never interprets message meaning or
dispatch policy.

The live design role is **Designer**. The porter and drawing-office role
identities are removed. Claude orchestration remains unimplemented until it can
be exercised independently.

## Consequences

- Standby uses no model resumption, agent tool call, polling request, or token.
- Direction arriving during a tool call is queued within the active Codex turn
  and becomes visible at the next model boundary.
- Broker history and browser observability remain independent of Codex payloads
  and thread identifiers.
- The orchestrator process is a lifecycle owner and delivery adapter, not a
  fourth agent or a workflow decision-maker.
- Restart recovery is intentionally absent: losing the owner closes the
  in-memory run rather than attaching another app-server to uncontrollable
  sessions.
- App-server protocol changes are isolated in one adapter and guarded by
  ownership and routing acceptance tests.
