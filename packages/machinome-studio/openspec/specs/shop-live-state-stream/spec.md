# shop-live-state-stream Specification

## Purpose

Define how a Floor browser learns the current state of an open shop and every
subsequent change to it, so that a page is correct when it loads, while it
runs, and after it loses and regains contact with the service.

## Requirements

### Requirement: A connecting browser receives the current situation
The shop floor SHALL deliver the complete current run state and the complete
ordered conversation to a browser as the first thing it receives on a live
connection, on every connection and not only the first. A browser SHALL NOT be
required to make any further request to display correct state.

#### Scenario: A browser connects to a shop with work already under way
- **WHEN** a maker opens the shop floor page after agents have manifested and
  messages have been exchanged
- **THEN** the page displays the manifested agents with their current work
  states and the whole conversation in its original order, without issuing any
  request beyond the one that carries them

#### Scenario: A browser reloads
- **WHEN** the maker reloads the page during an active run
- **THEN** the restored page displays the same agents, work states, and
  conversation as before the reload

### Requirement: State missed while disconnected is restored on reconnection
When a browser's live connection is lost and re-established, the shop floor
SHALL restore that browser to the shop's current state, including every change
published while it was disconnected, without a page reload and without a bound
on how many changes it may have missed.

#### Scenario: Work happens while the browser is disconnected
- **WHEN** an agent manifests and begins work while a browser's live connection
  is down, and that connection is then re-established
- **THEN** the page shows that agent in its current work state

#### Scenario: More changes occur than the activity buffer retains
- **WHEN** more changes are published while a browser is disconnected than the
  shop retains for display, and the connection is re-established
- **THEN** the page shows the shop's current state, with no missing or stale
  agent, work state, or conversation entry

#### Scenario: The service restarts under an open page
- **WHEN** the shop floor service restarts at the same browser location while a
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
