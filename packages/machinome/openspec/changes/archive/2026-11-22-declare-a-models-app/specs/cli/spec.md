## MODIFIED Requirements

### Requirement: Develop command

The system SHALL provide `machinome develop [reference]`, orchestrating the
builder and the viewer that serves, by default the web viewer. It SHALL choose
the viewer by `--viewer <name>`, else the project's declared viewer, else
`web`, under the `viewer-seam` capability, and SHALL ask it, through the seam,
to serve the project's build directory. With no viewer flag, and with the
retained explicit `--web` spelling, it SHALL require the `machinome-viewer`
package and fail before starting development processes, naming `pip install
"machinome[viewer]"`, when that package is not installed. `--web` combined
with `--viewer` naming another viewer SHALL be rejected as an argument error.
A chosen viewer that does not serve SHALL be refused by name before any
process starts. The framework SHALL provide no OpenSCAD GUI viewer flag or
fallback.

`--no-web` runs the builder watch loop alone and SHALL NOT resolve a viewer or
bind `MACHINOME_PORT`. The web viewer SHALL serve in the develop process,
in a session the viewer owns; `--web-dev` SHALL be accepted and SHALL change
nothing but a warning that the development page is served directly, with no
separate frontend process; `--debug-builder` runs the builder once in-process
for breakpoints. `--no-web` SHALL be rejected with a clear argument error when
combined with a flag that explicitly requests the browser viewer (`--web`,
`--web-dev`). Each rebuild cycle SHALL respawn the builder and tell every open
page, through the session, that a build was published, without closing its
connection. When it serves through a session it SHALL also tell every open
page, through the session, each time a build replaces the published
document, after the files that document names are in place, so a page reads
the build it is told of rather than the one before it. Ctrl-C stops the
session and exits 0.

#### Scenario: Default develop session

- **WHEN** a user runs `machinome develop` in an installation with
  `machinome-viewer`
- **THEN** the builder and the web viewer start on the project model, and the
  model is viewable at `http://localhost:<MACHINOME_PORT>`

#### Scenario: Default develop session without the viewer

- **WHEN** a user runs `machinome develop` in an installation without
  `machinome-viewer`, whether or not OpenSCAD is installed
- **THEN** the command fails before starting development processes, naming
  `pip install "machinome[viewer]"`, and does not open OpenSCAD

#### Scenario: The web viewer is requested but not installed

- **WHEN** a user runs `machinome develop --web` without `machinome-viewer`
- **THEN** the command fails naming the extra and starts no builder or viewer

#### Scenario: The removed OpenSCAD flag is rejected

- **WHEN** a user runs `machinome develop --openscad`
- **THEN** command-line parsing rejects the unknown option and starts no
  development process

#### Scenario: Headless develop session

- **WHEN** a user runs `machinome develop --no-web` without
  `machinome-viewer`
- **THEN** the builder watch loop runs and rebuilds on source changes, and no
  listener is bound on `MACHINOME_PORT`

#### Scenario: Browser viewer requested and suppressed at once

- **WHEN** a user runs `machinome develop --no-web --web-dev`
- **THEN** the command exits with a clear argument error before starting
  development processes

#### Scenario: The browser viewer runs in its own process

- **WHEN** `machinome develop` serves through the web viewer and a source
  file changes
- **THEN** no viewer program is run, the server runs in the develop process,
  and every open page receives `reload` on its socket after the builder is
  respawned, without the socket being closed

#### Scenario: A viewer that does not serve

- **WHEN** a user runs `machinome develop --viewer openscad`
- **THEN** the command fails naming the `openscad` viewer, serving and `web`,
  and starts no builder

#### Scenario: An open page shows a source edit when it is published

- **WHEN** a maker edits the model's source while its development page is
  open
- **THEN** the page receives `reload` once the rebuilt document is
  published, and shows the edit then rather than at a later edit

#### Scenario: An open page shows an app edit without a model reload

- **WHEN** a maker edits the model's app while its development page is open
- **THEN** the page receives `reload` once the watching builder has
  published the document naming the new app, and no builder is respawned
