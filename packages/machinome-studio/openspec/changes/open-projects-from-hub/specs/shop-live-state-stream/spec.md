## MODIFIED Requirements

### Requirement: A connecting browser receives the current situation
The shop SHALL deliver the complete current state of what a browser is looking
at as the first thing that browser receives on a live connection, on every
connection and not only the first. For a project workspace that state SHALL be
the complete run state and the complete ordered conversation of that project.
For the hub that state SHALL be the working folder's projects with, for each,
whether it is open and whether it can be opened. A browser SHALL NOT be required
to make any further request to display correct state.

#### Scenario: A browser connects to a project with work already under way
- **WHEN** a maker opens a project workspace after its agents have manifested and messages have been exchanged
- **THEN** the page displays the manifested agents with their current work states and the whole conversation in its original order, without issuing any request beyond the one that carries them

#### Scenario: A browser reloads
- **WHEN** the maker reloads a project workspace during active work
- **THEN** the restored page displays the same agents, work states, and conversation as before the reload

#### Scenario: A browser connects to the hub
- **WHEN** a maker opens the hub
- **THEN** the page displays every project of the working folder with its current open state, without issuing any further request

### Requirement: State missed while disconnected is restored on reconnection
When a browser's live connection is lost and re-established, the shop SHALL
restore that browser to the current state of what it is looking at, including
every change published while it was disconnected, without a page reload and
without a bound on how many changes it may have missed.

#### Scenario: Work happens while the browser is disconnected
- **WHEN** an agent manifests and begins work while a browser's live connection is down, and that connection is then re-established
- **THEN** the page shows that agent in its current work state

#### Scenario: More changes occur than the activity buffer retains
- **WHEN** more changes are published while a browser is disconnected than the shop retains for display, and the connection is re-established
- **THEN** the page shows the current state, with no missing or stale agent, work state, or conversation entry

#### Scenario: Projects open and close while the hub is disconnected
- **WHEN** projects are opened or closed while a hub page's live connection is down, and that connection is then re-established
- **THEN** the hub shows every project's current open state without a page reload

#### Scenario: The service restarts under an open page
- **WHEN** the shop service restarts at the same browser location while a page remains open, and that page reconnects
- **THEN** the page displays the state of the restarted shop, and every change the restarted service subsequently publishes appears on that page without a reload

## ADDED Requirements

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
