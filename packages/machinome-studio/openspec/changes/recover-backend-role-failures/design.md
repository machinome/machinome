## Context

`ShopOrchestrator.handle_event()` currently raises for both `role_failed` and `backend_failed`. Because the backend event router is a required runtime task, either event ends the router, tears down Uvicorn, and closes every role. Claude reports quota/session-limit results as `role_failed`, even though the other role processes and often the failed role's own persistent CLI process remain usable for a later turn.

The portable backend contract already distinguishes a fault confined to one role from a fault that ends the backend. The broker owns current browser state, snapshots, and live events; it is therefore the appropriate durable-for-the-run home for the visible failure. Assignment lifecycle must remain broker-owned and must not be silently completed by a backend error.

## Goals / Non-Goals

**Goals:**

- Keep an open shop usable after a `role_failed` event.
- Preserve the failed role's native session when it can accept another turn, while replacing it transparently if that process has died.
- Make the current failure and exact backend reason visible on initial load, live update, and reconnection.
- Let the next envelope addressed to the failed role act as the explicit recovery trigger.
- Preserve delegated assignment state across a role-session failure.

**Non-Goals:**

- Recover a backend-wide process failure without restarting the floor.
- Retry work automatically or poll an external quota.
- Infer when a provider limit resets.
- Claim that a replacement native session retains backend-private conversation state; the project repository, broker conversation, assignments, and role contract are the recovery record.

## Decisions

### Treat role failure as orthogonal to assignment state

`Agent` gains an optional failure reason. Its existing `waiting`/`active` state remains the assignment/direct-work state, so a delegated assignment is not falsely completed. Browser values include the failure reason, and broker methods publish `agent_failed` and `agent_recovered` with the complete current agent value. Snapshots naturally carry the same data.

This is preferable to adding `failed` to the lifecycle state enum: doing so would require storing and restoring a second hidden assignment state and would conflate backend availability with acknowledged work.

### Preserve first, replace on transport failure

On `role_failed`, the orchestrator clears the failed turn identity and records the failure, but retains the role handle. The next addressed envelope is always delivered as a new turn. If that handle rejects the delivery synchronously, the orchestrator closes it, opens a replacement role with the same resolved `RoleContext`, and retries the same envelope once. Recovery is published only after a delivery is accepted.

This preserves a Claude session after a quota result while still recovering from a role process that exited. Always reopening would unnecessarily discard useful native context; never reopening would leave dead processes unrecoverable.

### Do not auto-retry or poll

No timer probes the failed role and no failed turn is replayed. A later broker envelope is the recovery signal. For the delegated profile, a maker can message Foreman after access returns; a failed Foreman is directly retriggered by that message, while a surviving Foreman can decide how to resume and send a new envelope to a failed specialist.

If both the retained handle and its one replacement reject the trigger, the broker records the updated failure and consumes that failed delivery attempt so the routing loop remains live. The maker can trigger another attempt later. This avoids an unbounded retry loop and preserves human control over paid or quota-bound work.

### Present a recoverable failure notice in the conversation area

The workspace derives failure notices from current run agents rather than appending synthetic participant messages to conversation history. Each notice identifies the profile label and exact backend reason, and tells the maker to message the configured user-facing agent after backend access is restored. React's normal text rendering escapes backend-provided content. The notice disappears on `agent_recovered`.

Synthetic conversation entries were rejected because failures are runtime state, not authored speech, and because conversation accepts only the user and configured user-facing agent.

### Keep backend-wide failure fail-closed

`backend_failed` continues to raise and end the runtime. The portable contract defines it as a fault that ends the run; keeping HTTP alive without a working backend would falsely present a recoverable shop and requires a separate backend restart protocol.

No ADR is required: this change applies the accepted role/backend failure distinction from ADRs 0006 and 0008 without changing the backend seam or introducing a new architectural boundary.

## Risks / Trade-offs

- **A provider accepts a trigger and then reports the limit again** → The failure briefly clears when delivery is accepted and is restored by the next `role_failed`; there is no polling or hidden retry.
- **A replacement session lacks backend-private conversation context** → The same role contract and project root are reloaded, and the maker/Foreman supplies the resume instruction using durable project and broker state.
- **A delivery exception has ambiguous provider acceptance** → Retry only after a synchronous exception and only once; report the result visibly rather than looping.
- **A failed specialist still has an active assignment** → Keep assignment state intact and show failure as a separate condition, allowing Foreman to decide whether to resume or redirect it.
