## ADDED Requirements

### Requirement: The workspace explains recoverable role failures
While any manifested role is failed, the browser SHALL show a live, accessible notice in the conversation area that identifies the role by its profile-provided label, displays the backend-provided reason, and tells the maker that they can message the configured user-facing agent after backend access is restored to resume the shop. The notice SHALL be derived from current run state rather than inserted as participant-authored conversation and SHALL disappear when the role recovers.

#### Scenario: Claude reports a Machinist session limit
- **WHEN** the Machinist role reports that its provider session limit has been reached
- **THEN** the open workspace displays a Machinist failure notice with that reason while keeping the shop and composer available

#### Scenario: A failed Foreman is retriggered
- **WHEN** the maker sends a new message after Foreman's backend access is restored and the new turn is accepted
- **THEN** the failure notice clears without a page reload and the conversation remains available

#### Scenario: The page reconnects during a role failure
- **WHEN** a page connects or reconnects while any role is failed
- **THEN** it displays the same current failure notice from the snapshot
