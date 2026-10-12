# viewer-seam Specification

## Purpose

The contract of viewers and their resolution by name: one seam,
`machinome.viewer`, through which every caller of the set reaches a viewer,
with one contract version and one set of refusals; the default rule (the
flag, the project's `[tool.machinome] viewer`, the operation's default); the
two providers, the web viewer `machinome.viewer.web` of `machinome-viewer`
and the OpenSCAD viewer `machinome.viewer.openscad` of
`machinome-viewer-openscad`, and the operations each declares; the web
viewer in the framework's process; the capture request, naming its camera
by the notation or by its parts; `machinome viewer`, which reads no
manifest; and the word viewer in place of renderer. Encodes ADR-194
(OpenSpec change `viewer-seam`) and ADR-196 (OpenSpec change
`viewer-command`).

Code: `machinome/viewer/__init__.py`, `machinome/manifest.py` (the
`viewer` key), `machinome/manager/viewer.py` (the command); the providers at
`packages/machinome-viewer/machinome/viewer/web/` (`__init__.py`,
`stage.py`, `session.py`) and
`packages/machinome-viewer-openscad/machinome/viewer/openscad/__init__.py`;
`tests/test_viewer_seam.py`.
## Requirements
### Requirement: The core declares the contract of viewers in one seam

The framework SHALL declare the contract of viewers in one module of its own,
`machinome.viewer` (`machinome/viewer/__init__.py`), importing nothing but the
standard library and `machinome.extras`. It SHALL state the contract version
it speaks as the integer `CONTRACT`, the operations a viewer may offer
(`present`, `capture`, `serve`, `embed`), and, as Protocols, what each
operation asks: every viewer its name, its `CONTRACT`, the operations it
offers, its identity, the node-tree document versions it reads (none, for a
viewer that reads no document) and whether a version is readable; `present`
and `withdraw`, preparing what the viewer reads at one assembled instant and
removing it; `capture`, an image of what was presented, with the snapshot
options the viewer honours; `serve`, an interactive session on a build
directory that can be told a build was published and can be stopped; `embed`,
the files an export or a documentation page carries and the report of the
installed viewer. The seam SHALL name the viewers the core knows and the extra
that installs each, and the default viewer of each operation, and no other
module of the core SHALL name a viewer's technology.

The seam's `__path__` SHALL be extended with the namespace portions found on
`sys.path` that ship no `__init__.py` of their own
(`machinome._namespace_portions`), so a provider installed by another
distribution resolves in an editable workspace as it does from the wheels.

#### Scenario: Both providers resolve in the workspace

- **WHEN** `machinome.viewer.web` and `machinome.viewer.openscad` are
  imported in the repository's editable workspace
- **THEN** each resolves to the `__init__.py` of its own distribution's
  directory, and `machinome.viewer`'s path holds the core's directory followed
  by the providers'

#### Scenario: Both providers resolve from the wheels

- **WHEN** the core's, the viewer's and the OpenSCAD viewer's wheels are
  installed into one environment
- **THEN** both providers resolve from it

#### Scenario: The seam loads no viewer

- **WHEN** `machinome.viewer` is imported
- **THEN** no provider, web framework, browser driver or CAD library is
  imported

### Requirement: A viewer is chosen by name and resolved at a known address

The seam SHALL resolve a viewer by importing `machinome.viewer.<name>` and
nothing else: no entry point is read and no program is run to find it. A
provider SHALL declare the contract version it implements as its own
`CONTRACT` and the operations it offers as `OPERATIONS`. The seam SHALL refuse:
a viewer the core knows whose module cannot be found, with the
`machinome.extras.ExtraUnavailable` refusal naming the viewer, its module and
the line that installs its extra; a name the core does not know, naming the
viewers it knows; a provider whose `CONTRACT` differs from the seam's, or that
declares none, as incompatible, naming both versions and the remedy to install
the viewer released with this framework; an operation the chosen viewer does
not offer, naming what needs it, the viewer and the viewers that offer it. A
refusal a provider's own import raises because a package its extra installs is
absent SHALL pass unmodified. A viewer SHALL NEVER be replaced by another: a
refusal is the answer.

#### Scenario: An absent viewer is refused by its extra

- **WHEN** a command asks for the `openscad` viewer and no installed
  distribution ships `machinome.viewer.openscad`
- **THEN** the refusal reads "the openscad viewer needs
  machinome.viewer.openscad, which is not installed; install it with 'pip
  install "machinome[viewer-openscad]"'", and the web viewer is not used
  instead

#### Scenario: The web viewer absent

- **WHEN** a command asks for the `web` viewer and `machinome-viewer` is not
  installed
- **THEN** the refusal names `machinome.viewer.web` and `pip install
  "machinome[viewer]"`

#### Scenario: An unknown name

- **WHEN** a command asks for the viewer `povray`
- **THEN** the refusal reads "no viewer is named 'povray'; the viewers are
  openscad, web"

#### Scenario: A provider of another contract

- **WHEN** an installed `machinome.viewer.<name>` declares `CONTRACT = 2`, or
  no `CONTRACT`
- **THEN** resolving it is refused as incompatible, naming the version it
  declares or that it declares none, and the version this framework speaks

#### Scenario: An operation the viewer lacks

- **WHEN** `machinome develop` asks the `openscad` viewer to serve
- **THEN** it is refused naming `machinome develop`, the operation, the
  `openscad` viewer and `web` as the viewer that serves, and no builder
  starts

#### Scenario: The OpenSCAD node package absent under the OpenSCAD viewer

- **WHEN** the OpenSCAD viewer is installed and the OpenSCAD node package or
  SolidPython cannot be found
- **THEN** resolving the viewer raises the node package's refusal naming
  `pip install "machinome[openscad]"`

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

### Requirement: Each viewer declares what it offers

The web viewer, `machinome.viewer.web` of the distribution `machinome-viewer`,
SHALL offer `present`, `capture`, `serve` and `embed`, read the document
versions its widget declares, and honour, beyond the common snapshot options
(output, image size, time, camera), `--autocenter` and `--viewall`, which
describe what it does by default. The OpenSCAD viewer, `machinome.viewer.openscad`
of the distribution `machinome-viewer-openscad`, SHALL offer `present` and
`capture`, read no node-tree document, and honour every snapshot option. Each
provider SHALL import its machinery only when an operation is called, so
resolving it and asking its identity or the versions it reads imports no web
framework, browser driver or CAD library.

#### Scenario: The declarations

- **WHEN** both providers are resolved
- **THEN** the web viewer's `OPERATIONS` are `present`, `capture`, `serve`
  and `embed`, the OpenSCAD viewer's are `present` and `capture`, and each
  `CONTRACT` equals the seam's

#### Scenario: Asking whether a version is readable is cheap

- **WHEN** the builder asks the web viewer whether it reads document version
  13
- **THEN** the answer is given without importing the viewer's server, its
  capture, a web framework or a browser driver

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

### Requirement: The word is viewer

The seam, both providers, the commands' options, help and messages, and the
logger channels of the viewers SHALL say viewer where they named a renderer:
the flag is `--viewer`, the OpenSCAD viewer's logger is `viewer.openscad`, its
class `OpenScadViewer`, and no module of the core, of either provider, of the
films or of the studio SHALL spell `--renderer` other than to refuse it,
`machinome.viewers`, `renderer_names`, `DEFAULT_RENDERER`, `OpenScadRenderer`
or `BrowserRenderer`.

#### Scenario: A scan of the set's sources

- **WHEN** the sources of the core, the two providers, the films and the
  studio are scanned for the former names
- **THEN** none is found but the refusal of `--renderer`, and the test fails
  naming any file that holds one

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

