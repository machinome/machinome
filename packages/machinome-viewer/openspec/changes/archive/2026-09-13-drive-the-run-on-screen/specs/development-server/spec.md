## MODIFIED Requirements

### Requirement: The development page renders through the viewer package

The development app SHALL mount the viewer package against the served
snapshot; it SHALL NOT carry its own tree walk, operation composition,
expression evaluation, animation clock or mechanical run. It SHALL refresh a
changed model through the package's targeted document update rather than
rebuilding its tree, preserving the maker's viewpoint and avoiding refetch of
unchanged geometry. It SHALL name the tab after the model and show build errors
or the missing-bundle remedy in its error pane. An installation whose development
app is not built SHALL answer the page with the build remedy while keeping
every other route available.

When the served snapshot carries a mechanical program and a run is live, a
targeted document update SHALL keep that run — its committed bank, its
active commands and its elapsed simulation time — only when the
republished program's identity and the run's step size are both unchanged.
Otherwise it SHALL discard the run and start a fresh one at the
republished document's own rest state, and SHALL say which of the two it
did. A coordinate SHALL NOT be carried across a republish because an
identifier happened to match.

#### Scenario: A built project is opened in the development loop

- **WHEN** a maker opens a completed project
- **THEN** it is coloured, lit, framed, and has shared animation controls when
  animated

#### Scenario: An edit refreshes without a teardown

- **WHEN** a rebuild completes and the reload channel signals the browser
- **THEN** the page updates the model through the targeted document update,
  keeping its canvas, camera, and unchanged meshes

#### Scenario: A source checkout without the built app

- **WHEN** a browser requests the page of a server whose development app is
  not built
- **THEN** it receives the build remedy, and the build, bundle and error
  routes still answer

#### Scenario: A cosmetic edit leaves the machine running

- **WHEN** a maker edits a part's geometry or colour while a run stands
  part way through a movement, and the rebuild republishes a program of
  the same identity
- **THEN** the model refreshes and the machine is exactly where it was:
  the same bank, the same step count, the same elapsed time

#### Scenario: An edit to the mechanism restarts the machine

- **WHEN** a maker edits a relation, a joint or a driver declaration, so
  the republished program's identity differs
- **THEN** the run is discarded, a fresh one starts at the new document's
  rest state, and the page says the machine was reset rather than
  carrying coordinates across two different mechanisms
