## MODIFIED Requirements

### Requirement: The viewer is chosen by the flag, the project, or the command's default

A command that uses a viewer SHALL choose it in this order and no other: the
name given by its `--viewer` option; else the name the project declares as
`viewer` under `[tool.machinome]` in its manifest; else the default of the
operation the command needs: `openscad` for an image (`machinome snapshot`),
`web` for serving (`machinome develop`) and for embedding (`machinome export`).
The choice SHALL NOT depend on which viewers are installed, on the project's
node types or backends, or on anything but the flag, the declaration and the
operation. A declared viewer that does not offer the command's operation SHALL
be refused by name, naming the manifest key and the flag. A `viewer` value that
is not a string SHALL be refused as a manifest error naming the key. The
documentation build and the films, which read no project manifest, SHALL use
the `web` viewer. `machinome viewer`, which takes no node path and acts on the
installation and on the directories it is given, SHALL read no project manifest
either: its verbs SHALL use the viewer their `--viewer` names, else `web`, and
its report with no verb the `web` viewer.

#### Scenario: The flag wins

- **WHEN** a project declares `viewer = "web"` and a user runs `machinome
  snapshot --viewer openscad`
- **THEN** the OpenSCAD viewer takes the image

#### Scenario: The project's viewer

- **WHEN** a project declares `viewer = "web"` and a user runs `machinome
  snapshot` with no `--viewer`
- **THEN** the web viewer takes the image, the same image `--viewer web`
  takes

#### Scenario: No declaration

- **WHEN** a project declares no viewer
- **THEN** `machinome snapshot` uses the OpenSCAD viewer, and `machinome
  develop` and `machinome export` the web viewer

#### Scenario: The declared viewer cannot serve

- **WHEN** a project declares `viewer = "openscad"` and a user runs
  `machinome develop` with no `--viewer`
- **THEN** the command is refused naming the `openscad` viewer, the key
  `[tool.machinome] viewer` and `--viewer`, and starts nothing

#### Scenario: The viewer command reads no project

- **WHEN** a project declares `viewer = "openscad"` and a user runs `machinome
  viewer serve --build-dir _build` inside it with no `--viewer`
- **THEN** the web viewer serves the build directory

### Requirement: The web viewer runs in the framework's process

The web viewer SHALL serve and capture in the process of the command that asks
it. Its `serve` SHALL start the development server in a thread the provider
owns and return a session once the server listens, having printed the line
`Serving at http://0.0.0.0:PORT (Ctrl+C to stop)` on standard output, and
SHALL raise, printing nothing, when the server cannot listen; the session's
`reload` SHALL send `reload` to every open
page's reload socket, which the page answers by fetching the published build;
its `stop` SHALL return when the server has stopped. Its `capture` SHALL
photograph the staged directory with the browser driver in the command's
process. The framework SHALL run no program of the viewer's to serve or
capture, and the viewer's distribution SHALL install no program of its own:
its verbs are the framework's `machinome viewer`.

#### Scenario: A rebuild reaches the open page in place

- **WHEN** `machinome develop` is serving a project, a page is open, and a
  source file changes
- **THEN** the open page's socket receives `reload` without being closed, and
  no viewer process is started or stopped

#### Scenario: Interrupting develop stops the server

- **WHEN** a user interrupts `machinome develop` from its terminal
- **THEN** the command exits 0 and no thread, process or listener of the
  viewer is left

#### Scenario: A web still is taken in the command's process

- **WHEN** `machinome snapshot --viewer web` writes an image
- **THEN** no `python -m machinome.viewer.web` process is run

## ADDED Requirements

### Requirement: A capture request names its camera by the notation or by its parts

A request to capture SHALL name its camera in one of two forms: the `--camera`
notation `machinome snapshot` takes, or the camera's parts, the eye, the
target, the up direction and the vertical field of view, each of which may be
absent. A request naming both forms SHALL be refused. The web viewer SHALL
resolve the notation into its parts as the snapshot has always resolved it,
SHALL take parts as given, and SHALL leave each absent part to its own default,
so a capture asked with the eye and target alone is framed with the viewer's
own up direction and field of view, not those of the notation.

#### Scenario: The parts reach the viewer as given

- **WHEN** the web viewer is asked to capture a staged document with an eye and
  a target and no up direction or field of view
- **THEN** the page is mounted with that eye and target and with no up
  direction or field of view of the request's, and the image is the one the
  viewer's own defaults give

#### Scenario: The notation is resolved

- **WHEN** the web viewer is asked to capture with the notation
  `0,0,0,65,0,35,1400`
- **THEN** the page is mounted with the eye, target, up direction and field of
  view the notation resolves to, as `machinome snapshot --viewer web --camera`
  mounts it

#### Scenario: Both forms at once

- **WHEN** a request is made with the notation and an eye
- **THEN** it is refused before any viewer is asked
