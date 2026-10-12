## MODIFIED Requirements

### Requirement: A connecting browser receives the current situation
The shop SHALL deliver the complete current state of what a browser is looking
at as the first thing that browser receives on a live connection, on every
connection and not only the first. For a project workspace that state SHALL be
the complete run state and the complete ordered conversation of that session.
For the hub that state SHALL be the entries of the folder that browser is
listing — its folders, its openable projects, and its unopenable directories —
plus any accepted creation still in progress in that folder, with each entry
named by its path under the working folder, each project's current lifecycle
state, and whether it can be opened. A browser SHALL NOT be required to make any
further request to display correct state.

Every hub change the shop publishes SHALL name the entry it is about by that
same path, so a browser can tell whether the change belongs to the folder it is
listing.

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
- **THEN** the page displays every entry of the working folder with its current open state, without issuing any further request

#### Scenario: A browser connects to the hub inside a folder
- **WHEN** a maker opens the hub listing a folder below the working folder
- **THEN** the first state is that folder's own entries, and entries outside it are not part of it

#### Scenario: A browser connects while project creation is running
- **WHEN** a maker opens the hub on the folder a project is being created in, after creation was accepted but before the project directory or session is ready
- **THEN** the first state includes that project as `creating` with its chosen profile
