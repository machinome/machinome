## MODIFIED Requirements

### Requirement: The server is launched on a build directory

The system SHALL provide `solid-node-viewer serve --build-dir DIR`, serving
the published build at `DIR` as a FastAPI app via uvicorn on
`0.0.0.0:PORT`, where `PORT` is `--port` when given, else `SOLID_NODE_PORT`,
else 8000. Starting the server SHALL NOT import a project model and SHALL
succeed whether or not `DIR` holds a published build, leaving the reload
socket, error, snapshot and bundle routes available.

The development page is a static page this package carries, so there is no
separate frontend process to start or proxy. The command SHALL nevertheless
go on **accepting** `--dev`, `--start-frontend` and `--frontend-port`,
changing nothing and logging one notice naming the flag and saying the page
is served directly, and SHALL go on reading `SOLID_NODE_FRONTEND_PORT`
harmlessly. This is a compatibility promise, not an oversight: a released
solid-node passes `--start-frontend` under its own viewer-development flag,
and a viewer that refused it would turn a working framework command into an
error on a flag the maker never typed. A later change SHALL NOT remove
these flags as unused.

#### Scenario: A framework launches the server beside its builder

- **WHEN** `solid develop` starts `solid-node-viewer serve --build-dir _build`
  as a separate process
- **THEN** the server listens on the configured port and serves that build
  directory, having imported nothing of the project

#### Scenario: A released framework asks for the old npm dev server

- **WHEN** a framework launches the server with `--start-frontend`, `--dev`
  or `--frontend-port`
- **THEN** the server starts and serves the same static development page,
  starts no second process, and says in its log that the flag no longer
  does anything

#### Scenario: Viewer started before any build completed

- **WHEN** the server starts on a directory with no published document
- **THEN** the snapshot route reports its absence and the server remains
  available

#### Scenario: Broken node at viewer start

- **WHEN** the server restarts while the project has a build error
- **THEN** it remains available for the browser to poll `/_build_error` and
  reconnect the reload socket

### Requirement: Reload channel

The system SHALL expose `/ws/reload`, immediately send `"reload"` on connect,
and the development page SHALL retry disconnected clients every 2 seconds and
show an offline banner while the development process is unavailable. On
reconnect, it SHALL check `/_build_error` before refreshing the published
snapshot. The banner SHALL be shown only once an attempt that had succeeded
drops, or after repeated failures to connect at all, so an ordinary page load
never flashes it; it SHALL leave the stale model underneath fully
interactive, and SHALL be removed once the connection is back.

Nothing of that behaviour depends on a UI framework: the reload client is
carried by the same bundle the viewer is.

#### Scenario: Rebuild refreshes the browser

- **WHEN** a source edit completes a rebuild cycle and the launching process
  restarts the server
- **THEN** the browser re-reads the published snapshot without a page refresh

#### Scenario: The development process goes away

- **WHEN** the server a page was connected to stops
- **THEN** the page shows a banner saying the model may be stale, goes on
  retrying, and the model stays on screen and orbitable

#### Scenario: The development process comes back

- **WHEN** the server is started again
- **THEN** the page reconnects, checks the build error surface, refreshes
  the model and removes the banner, with no interaction from the maker

### Requirement: The development page renders through the viewer package

The development page SHALL be a static page this package carries and the
server answers `/` with. It SHALL check the viewer status route, load the
installed bundle from the bundle route, and mount the package's **inspector
layout** against the served snapshot with inline animation controls playing
— with the sidebar OPEN: a maker developing a machine is there to inspect
its parts, and no embedding constrains the page. The page's query-string
option collapses it for a link that wants the model alone. It SHALL NOT carry its own tree
walk, operation composition, expression evaluation, animation clock or
mechanical run, and SHALL NOT require a UI framework, a package manager or a
build step of its own.

It SHALL refresh a changed model through the package's targeted document
update rather than rebuilding its tree, preserving the maker's viewpoint and
avoiding refetch of unchanged geometry. It SHALL name the tab after the
model. It SHALL show a build error, and the remedy for an absent bundle, in
an error surface of its own **over a viewer that stays mounted**, so a
failed save does not discard the camera or a live run, and SHALL clear that
surface when the error clears. An installation whose viewer bundle is not
built SHALL answer the page with the build remedy while keeping every other
route available.

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
  animated, and the assembly sidebar is open beside it with the model's tree

#### Scenario: An edit refreshes without a teardown

- **WHEN** a rebuild completes and the reload channel signals the browser
- **THEN** the page updates the model through the targeted document update,
  keeping its canvas, camera, and unchanged meshes, and without loading the
  page again

#### Scenario: An installation without a built bundle

- **WHEN** a browser requests the page of a server whose viewer bundle is
  not built
- **THEN** it receives the page, which reports the build remedy, and the
  build, bundle and error routes still answer

#### Scenario: A failed save does not discard the model

- **WHEN** a rebuild fails and the page shows the build error, and a later
  save fixes it
- **THEN** the error is shown over the model rather than instead of it, the
  camera is where the maker left it, and the next successful build refreshes
  in place

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
