## ADDED Requirements

### Requirement: A role-scoped backend failure is recoverable
After the shop has opened, a `role_failed` event SHALL NOT stop the backend event router, broker, browser service, or unaffected role sessions. The orchestrator SHALL clear the failed turn identity, retain the role's session handle for a later attempt, and treat the next envelope addressed to that role as an explicit recovery trigger delivered as a new turn.

If the retained handle rejects that recovery delivery synchronously, the orchestrator SHALL release it, open one replacement session with the same resolved role context, and retry that envelope once. It SHALL report the role recovered only after a delivery is accepted. If both attempts fail, it SHALL keep the role failed, report the latest reason, consume that delivery attempt without ending routing, and wait for a later envelope rather than polling or retrying autonomously.

`backend_failed` SHALL remain a runtime-ending fault.

#### Scenario: A quota result fails one persistent role
- **WHEN** a role reports a provider session-limit error through `role_failed` while other role sessions are open
- **THEN** the orchestrator records that role failure, clears its active delivery, and continues routing the other roles without closing the shop

#### Scenario: The retained role session accepts a later trigger
- **WHEN** an envelope is addressed to a failed role after backend access is restored and its retained session accepts a new turn
- **THEN** the orchestrator uses that session, reports the role recovered, and marks the envelope delivered

#### Scenario: A dead role process is replaced
- **WHEN** a failed role's retained handle rejects the next delivery and a replacement session accepts it
- **THEN** the orchestrator releases the dead session, opens the same role contract once, reports recovery, and delivers that envelope once to the replacement

#### Scenario: Recovery is triggered before access returns
- **WHEN** the retained handle and its one replacement both reject a recovery envelope
- **THEN** the role remains failed with the latest reason, the routing loops remain live, and no further attempt occurs until another envelope is addressed to that role

#### Scenario: The whole backend fails
- **WHEN** the backend emits `backend_failed`
- **THEN** the orchestrator ends the runtime and releases its resources
