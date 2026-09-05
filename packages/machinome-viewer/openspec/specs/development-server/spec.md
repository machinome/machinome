# Development Server Specification

## Purpose

The development server puts a published build in front of the viewer. It is
the process `solid develop` launches beside its builder, and it knows the
build only as a directory: it serves the published document and model files,
the installed viewer bundle, the reload channel and the build-error surface,
and never imports project source. Migrated from solid-node's `web-viewer`
baseline when the viewer became this package; the launch contract is new.

Code: `solid_node_viewer/server.py`, `solid_node_viewer/app/`,
`solid_node_viewer/cli.py` (`serve`).

## Requirements

### Requirement: The server is launched on a build directory

The system SHALL provide `solid-node-viewer serve --build-dir DIR`, serving
the published build at `DIR` as a FastAPI app via uvicorn on
`0.0.0.0:PORT`, where `PORT` is `--port` when given, else `SOLID_NODE_PORT`,
else 8000. Starting the server SHALL NOT import a project model and SHALL
succeed whether or not `DIR` holds a published build, leaving the reload
socket, error, snapshot and bundle routes available. `--dev` SHALL proxy the
page to the development app's npm dev server on `--frontend-port`, else
`SOLID_NODE_FRONTEND_PORT`, else 3000; `--start-frontend` SHALL additionally
start that npm server and implies `--dev`.

#### Scenario: A framework launches the server beside its builder

- **WHEN** `solid develop` starts `solid-node-viewer serve --build-dir _build`
  as a separate process
- **THEN** the server listens on the configured port and serves that build
  directory, having imported nothing of the project

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
and the development app SHALL retry disconnected clients every 2 seconds and
show an offline banner while the development process is unavailable. On
reconnect, it SHALL check `/_build_error` before refreshing the published
snapshot.

#### Scenario: Rebuild refreshes the browser

- **WHEN** a source edit completes a rebuild cycle and the launching process
  restarts the server
- **THEN** the browser re-reads the published snapshot without a page refresh

### Requirement: The server serves the published build snapshot

The system SHALL serve the published `viewer.json` and its referenced model
files below `/build/`, resolving every request from the build directory it
was launched on, refusing any path that resolves outside it, and never
importing project source or waiting for an artifact.

#### Scenario: A completed build is served to the browser

- **WHEN** a browser requests `/build/viewer.json`
- **THEN** it receives the snapshot and every named model resolves below
  `/build/`

#### Scenario: A path that escapes the build directory

- **WHEN** a request resolves to a file outside the build directory
- **THEN** the server answers not found and serves nothing

#### Scenario: Serving a project never imports it

- **WHEN** the served project's source would raise on import
- **THEN** its published snapshot remains servable unchanged

### Requirement: The server serves the installed viewer bundle

The system SHALL serve this installation's bundle at `/_viewer/bundle.js`
and report at `/_viewer` whether it is available, its declared API version
and, when absent, the remedy, rather than serving an empty or partial script.

#### Scenario: An installation with a built bundle

- **WHEN** a browser requests the bundle route
- **THEN** it receives JavaScript and the reported API version

#### Scenario: An installation without a built bundle

- **WHEN** a browser requests the bundle route of a source checkout that has
  not built the widget
- **THEN** the route answers unavailable with the build remedy and `/_viewer`
  reports the same remedy

### Requirement: The development page renders through the viewer package

The development app SHALL mount the viewer package against the served
snapshot; it SHALL NOT carry its own tree walk, operation composition,
expression evaluation, or animation clock. It SHALL refresh a changed model
through the package's targeted document update rather than rebuilding its
tree, preserving the maker's viewpoint and avoiding refetch of unchanged
geometry. It SHALL name the tab after the model and show build errors or the
missing-bundle remedy in its error pane. An installation whose development
app is not built SHALL answer the page with the build remedy while keeping
every other route available.

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

### Requirement: Build error surfacing

The system SHALL expose `GET /_build_error`, returning the build directory's
`errors.json` or `{}`; the browser SHALL show an active error instead of
refreshing and self-heal once the error clears.

#### Scenario: Error shown then cleared

- **WHEN** a reload finds a build error and a later save fixes it
- **THEN** the browser shows the error, then renders the next successful build
