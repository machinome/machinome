## ADDED Requirements

### Requirement: The roster distinguishes role availability from work state
The broker SHALL record an optional backend failure reason for each manifested agent independently of its waiting or active work state. A role failure SHALL NOT complete, discard, or replace a delegated assignment. Recovery SHALL clear only the failure reason, leaving the broker-owned work lifecycle otherwise unchanged.

#### Scenario: An active specialist session fails
- **WHEN** a specialist with an acknowledged assignment reports `role_failed`
- **THEN** the roster identifies that specialist as failed with the backend reason while retaining its active assignment state

#### Scenario: A failed specialist recovers
- **WHEN** a later delivery to the failed specialist is accepted
- **THEN** the roster clears the failure and continues to show the specialist's unchanged assignment state

#### Scenario: A direct-agent turn fails
- **WHEN** the direct profile's active agent reports `role_failed`
- **THEN** its failed turn identity is cleared, its failure reason is shown, and a later maker direction can start a new turn
