# shop-live-state-stream Specification

## Purpose

Define how a browser learns the current state of the hub or one open project
and every subsequent change to it, including across reconnection.

## Requirements

### Requirement: A connecting browser receives the current situation
The shop SHALL deliver the complete current state of what a browser is looking
at as the first thing that browser receives on a live connection, on every
connection and not only the first. For a project workspace that state SHALL be
the complete run state and the complete ordered conversation of that project.
For the hub that state SHALL be the working folder's projects plus any accepted
creation still in progress, with each project's current lifecycle state and
whether it can be opened. A browser SHALL NOT be required to make any further
request to display correct state.

#### Scenario: A browser connects to a project with work already under way
- **WHEN** a maker opens a project workspace after its agents have manifested and
  messages have been exchanged
- **THEN** the page displays the manifested agents with their current work
  states and the whole conversation in its original order, without issuing any
  request beyond the one that carries them

#### Scenario: A browser reloads
- **WHEN** the maker reloads a project workspace during active work
- **THEN** the restored page displays the same agents, work states, and
  conversation as before the reload

#### Scenario: A browser connects to the hub
- **WHEN** a maker opens the hub
- **THEN** the page displays every project of the working folder with its current open state, without issuing any further request

#### Scenario: A browser connects while project creation is running
- **WHEN** a maker opens the hub after creation was accepted but before the project directory or session is ready
- **THEN** the first state includes that project as `creating` with its chosen profile

### Requirement: State missed while disconnected is restored on reconnection
When a browser's live connection is lost and re-established, the shop SHALL
restore that browser to the current state of what it is looking at, including
every change published while it was disconnected, without a page reload and
without a bound on how many changes it may have missed.

#### Scenario: Work happens while the browser is disconnected
- **WHEN** an agent manifests and begins work while a browser's live connection
  is down, and that connection is then re-established
- **THEN** the page shows that agent in its current work state

#### Scenario: More changes occur than the activity buffer retains
- **WHEN** more changes are published while a browser is disconnected than the
  shop retains for display, and the connection is re-established
- **THEN** the page shows the current state, with no missing or stale
  agent, work state, or conversation entry

#### Scenario: Projects open and close while the hub is disconnected
- **WHEN** projects are opened or closed while a hub page's live connection is down, and that connection is then re-established
- **THEN** the hub shows every project's current open state without a page reload

#### Scenario: The service restarts under an open page
- **WHEN** the shop service restarts at the same browser location while a
  page remains open, and that page reconnects
- **THEN** the page displays the state of the restarted shop, and every change
  the restarted service subsequently publishes appears on that page without a
  reload

### Requirement: No change is lost between the situation and the changes to it
A change published after a browser's live connection is established SHALL reach
that browser exactly once in publication order, whether it was published before
or after the current situation was determined for that connection.

#### Scenario: A change is published during the connection hand-off
- **WHEN** a change is published between the moment a browser's live connection
  is established and the moment that connection's current situation is sent
- **THEN** the browser applies that change, and applies it once

### Requirement: The browser does not periodically re-request live state
The Floor browser SHALL NOT re-request run state or conversation on a timer or
any other periodic schedule. State the live connection delivers SHALL reach the
page only through that connection.

#### Scenario: An idle open shop
- **WHEN** a browser page is open on a shop where nothing is happening
- **THEN** the page issues no repeating requests for run state or conversation

### Requirement: Role failure state survives browser connection changes
The complete current run state in every live-connection snapshot SHALL include each manifested role's current failure reason, if any. Live `agent_failed` and `agent_recovered` events SHALL carry the complete current browser value for that role so a connected page applies the same state without another request.

#### Scenario: A connected browser observes a role failure and recovery
- **WHEN** a role fails and later recovers while the browser remains connected
- **THEN** the page receives the failure reason and its later clearing in publication order

#### Scenario: A browser connects while a role is failed
- **WHEN** the browser initially connects or reconnects after a role failure
- **THEN** its first snapshot includes the current failure reason without relying on bounded event history

### Requirement: A live connection carries one project's changes only
A live connection opened for a project SHALL carry the changes of that project
alone. No change published for one open project SHALL reach a browser connected
for another project or for the hub, and no other project's state SHALL appear in
a project's connection.

#### Scenario: Two projects publish at once
- **WHEN** two open projects each manifest agents and record conversation entries
- **THEN** each project's browser receives only its own project's changes, in publication order

#### Scenario: The hub observes sessions rather than their work
- **WHEN** an open project records conversation entries and work-state changes
- **THEN** a hub page is not sent that project's conversation or work states, and continues to show only which projects are open
### Requirement: Session live state includes runtime and agent activity
The project session snapshot SHALL include each manifested role's resolved
backend, provider, model, reasoning level, tool summary, authoritative idle
availability, current and queued assignment data, and the
session's bounded recent agent activity. A role-scoped catalogue request SHALL
report mutation support and choices when the maker focuses that role.
Subsequent runtime, lifecycle, and activity changes SHALL arrive through the
existing project live-state connection in publication order without polling or
a second connection.

#### Scenario: A browser connects to an idle mixed-backend session
- **WHEN** a maker opens Agents after Claude and OpenCode roles have manifested
- **THEN** the existing snapshot displays each role's current runtime, idle availability, assignments, and recent activity, and the focused role's catalogue request supplies its editability and choices

#### Scenario: A runtime update succeeds
- **WHEN** an idle role applies a new model and reasoning level
- **THEN** connected workspaces receive its complete updated agent value and a runtime-change activity record without another request

#### Scenario: A tool runs while Agents is visible
- **WHEN** the selected role starts and completes a tool operation
- **THEN** the existing live-state stream adds and then updates that activity record in publication order
