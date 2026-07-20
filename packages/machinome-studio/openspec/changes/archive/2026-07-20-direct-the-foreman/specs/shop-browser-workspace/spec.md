## MODIFIED Requirements

### Requirement: Deferred workspace areas are truthful
Until artifact inspection is available, the artifact area SHALL show that no
artifact is selected. The foreman-conversation area SHALL show the active
foreman conversation and a control for directing the foreman; it SHALL not
claim that a foreman conversation is unavailable.

#### Scenario: The workspace has no selected artifact
- **WHEN** the maker opens the Story 3 workspace before artifact inspection is implemented
- **THEN** the artifact area shows its empty state and the foreman-conversation area remains available for conversation
