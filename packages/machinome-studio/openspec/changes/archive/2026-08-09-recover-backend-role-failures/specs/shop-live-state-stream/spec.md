## ADDED Requirements

### Requirement: Role failure state survives browser connection changes
The complete current run state in every live-connection snapshot SHALL include each manifested role's current failure reason, if any. Live `agent_failed` and `agent_recovered` events SHALL carry the complete current browser value for that role so a connected page applies the same state without another request.

#### Scenario: A connected browser observes a role failure and recovery
- **WHEN** a role fails and later recovers while the browser remains connected
- **THEN** the page receives the failure reason and its later clearing in publication order

#### Scenario: A browser connects while a role is failed
- **WHEN** the browser initially connects or reconnects after a role failure
- **THEN** its first snapshot includes the current failure reason without relying on bounded event history
