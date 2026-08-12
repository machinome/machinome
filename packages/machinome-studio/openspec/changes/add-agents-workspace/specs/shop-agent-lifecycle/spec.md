## ADDED Requirements

### Requirement: Runtime mutation requires broker and backend idleness
The orchestrator SHALL serialize a runtime update with role delivery and SHALL
accept it only when the role has no active native delivery, no backend failure,
no active acknowledged work, no current delegated assignment awaiting
acknowledgement, and no queued delegated assignment. The same checks SHALL be
made while holding the role's delivery lock so a concurrent delivery or
lifecycle transition cannot pass between validation and application.

#### Scenario: A direct agent is processing a turn
- **WHEN** the maker requests a runtime update while the direct agent has an active backend delivery
- **THEN** the shop rejects it without changing runtime or configuration

#### Scenario: A specialist is awaiting acknowledgement
- **WHEN** a delegated specialist has a current assignment but is still visibly waiting
- **THEN** the shop rejects a runtime update because the role is not idle

#### Scenario: A specialist has queued work
- **WHEN** a specialist completes its native turn but still has current or pending assignments
- **THEN** the shop rejects a runtime update without changing its assignment lifecycle

#### Scenario: Work starts during a runtime request
- **WHEN** a runtime request and delivery race for the same idle role
- **THEN** the role lock admits exactly one first and the other observes the resulting active or updated state
