## ADDED Requirements

### Requirement: The OpenSpec CLI is a startup prerequisite

The shop SHALL verify that the `openspec` CLI is present and runnable before it
binds a listener or opens any project, and SHALL refuse to start when it is
not. The refusal SHALL name the missing prerequisite and how to install it.

The shop SHALL NOT start in a reduced mode in which projects open but their
spec record is unavailable.

#### Scenario: The CLI is missing

- **WHEN** the shop is started in an environment where `openspec` cannot be
  resolved or run
- **THEN** startup fails naming the missing prerequisite, no listener is bound,
  and no project is opened

#### Scenario: The CLI is present

- **WHEN** the shop is started in an environment where `openspec` runs
- **THEN** startup proceeds normally
