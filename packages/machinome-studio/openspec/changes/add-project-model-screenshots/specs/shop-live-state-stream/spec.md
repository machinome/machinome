## ADDED Requirements

### Requirement: Hub live state carries project screenshot revisions
The complete hub snapshot SHALL identify whether each project has a usable
canonical screenshot and SHALL carry a content revision for each available
image. When an open project's screenshot bytes change, the hub stream SHALL
publish a project-metadata change carrying the new revision. That change SHALL
NOT carry project conversation, agent state, or project-session events. A
reconnecting hub SHALL recover the current revision from its new complete
snapshot.

#### Scenario: A browser connects after a screenshot exists
- **WHEN** a browser connects or reconnects to the hub after a project has a usable `screenshot.png`
- **THEN** its complete hub snapshot identifies that screenshot and its current content revision

#### Scenario: An open project's screenshot changes
- **WHEN** the shop atomically replaces an open project's `screenshot.png` with different bytes
- **THEN** connected hub browsers receive the new screenshot revision and refresh only that project's preview

#### Scenario: Screenshot bytes do not change
- **WHEN** a screenshot refresh produces the same bytes already stored for the project
- **THEN** the hub stream publishes no screenshot-revision change

#### Scenario: A project screenshot changes while the hub is disconnected
- **WHEN** a project's screenshot changes while a hub browser is disconnected and that browser reconnects
- **THEN** the reconnecting snapshot carries the current revision without relying on retained event history
