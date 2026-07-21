## ADDED Requirements

### Requirement: The foreman remains available while shop work proceeds
The running foreman SHALL continue receiving maker messages and publishing
conversation messages while designer or machinist work is active. A maker
message received during a foreman tool call SHALL remain queued until that call
completes and SHALL be presented before the foreman's next task action.

#### Scenario: The maker writes while specialists work
- **WHEN** the maker submits a message while the designer or machinist is active
- **THEN** the message remains available to the running foreman without stopping the specialist work

#### Scenario: The maker writes during a foreman tool call
- **WHEN** the maker submits a message while the foreman is using a tool
- **THEN** the foreman receives it after that call completes and before starting its next task action

#### Scenario: The foreman updates the maker during specialist work
- **WHEN** the foreman publishes progress or asks for a consequential decision while specialists are active
- **THEN** the message appears in the maker's conversation without waiting for the specialist assignments to finish
