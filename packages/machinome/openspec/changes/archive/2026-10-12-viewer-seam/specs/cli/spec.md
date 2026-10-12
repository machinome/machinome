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
connection; Ctrl-C stops the session and exits 0.

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

### Requirement: Snapshot command

The system SHALL provide `machinome snapshot [reference]` rendering a PNG, with
options: `-o/--output` (defaulting to a file name derived from the resolved
node), `--time` (0.0–1.0, validated, default
0.0, applied via `set_keyframe`), `--camera` (gimbal or vector spec),
`--autocenter`, `--viewall`, `--imgsize` (default `1920x1080`, validated),
`--projection` (`ortho`|`perspective`), `--colorscheme` (the 11 OpenSCAD
schemes, default Cornfield), mutually exclusive `--render`/`--preview`,
`--view` (comma-separated of axes, crosshairs, edges, scales, wireframe),
`--viewer <name>` (`openscad` or `web`; default the project's declared viewer,
else `openscad`), and `--drive NAME=VALUE` (repeatable). The snapshot command
SHALL name no viewer technology itself and SHALL read no table of node types:
it SHALL reach the chosen viewer through the seam `machinome.viewer`, asking it
to present the posed root inside the build lock, to capture it after, and to
withdraw what it presented, under the `viewer-seam` capability. The former
option `--renderer` SHALL be refused, with exit status 2 and the line `Error:
machinome snapshot --renderer is --viewer since Machinome 0.9: write --viewer
<the value given>`, before anything is loaded or written.

`--drive` SHALL bind a DECLARED DRIVER by its qualified id, to a value parsed
as a number and checked by the declaration exactly as `set_state` checks it,
after the node is loaded and before it is keyframed and assembled, under
either viewer. It is distinct from `--set`, which reaches the root's
declared parameters; a driver is not a parameter and a parameter is not a
driver. A name that is not a declared driver of the tree SHALL fail listing
the drivers the tree publishes, and nothing SHALL be rendered.

A `--drive` naming a JOINT COORDINATE of a running root SHALL be REFUSED by
name, saying that a coordinate's value is what the run makes of it and
naming the drivers that can be set instead. The refusal states a fact rather
than a preference: with no run to own it, the enumeration that binding runs
immediately recomputes that coordinate from the drivers, so the value would
be silently discarded.

Under a running root the image is therefore the untimed REST POSE at the
requested driver values, the state a simulation itself starts from, and
admissible by construction. A state carrying HISTORY is not posed from the
command line: only a run knows which banks are reachable.

The default viewer SHALL remain `openscad`, unless the project declares
another, regardless of whether the project's model has B-rep geometry,
regardless of whether the binary is installed, and regardless of whether the
viewer package is installed. Choosing a viewer by availability, or by the
project's backends, would change the appearance of snapshots taken of
existing projects; the viewer is selected explicitly and never substituted,
as the web-snapshot capability requires.

With `--viewer openscad` the image is produced by the OpenSCAD CLI; without a
`DISPLAY` it SHALL wrap the render under `xvfb-run -a`, and error clearly if
xvfb is also unavailable. When the chosen viewer cannot be imported (the
`openscad` extra's SolidPython is absent, the OpenSCAD node package or the
OpenSCAD viewer is not installed, or the web viewer is not installed) the
command SHALL fail at its start, before loading the node, with one line
`Error: machinome snapshot --viewer <name> needs the <extra> extra: <the
refusal>; or use --viewer <the other viewer>`, exit 1, and write nothing. A
name no viewer answers, a viewer that does not capture and a viewer of another
contract SHALL each fail with one `Error:` line naming it, exit 1. When the
OpenSCAD binary itself is unavailable the command SHALL fail naming it and
naming `--viewer web` as the alternative, and SHALL write no image.

Under the OpenSCAD viewer, `--preview` SHALL draw the image with OpenSCAD's
ThrownTogether previewer, and a snapshot taken with `--preview` SHALL write its
image as one taken without it does. The option SHALL reach the OpenSCAD CLI in
the form that binary accepts for that previewer, and SHALL never leave the
binary reading the model's `.scad` path as the option's own value.

The OpenSCAD viewer alone SHALL compose the root's presentation for the
image (its `present` calls `assemble()` inside the build lock); the web viewer
SHALL prepare the tree and build its STLs without composing one.

With `--viewer web` the image is produced by the web viewer's capture, in the
command's process, on a staging directory the viewer prepares, with a
transparent background, as specified in the web-snapshot capability, and no X
display is required. Each viewer declares the options it honours beyond
`-o/--output`, `--time`, `--imgsize` and `--camera`: supplying an option the
chosen viewer does not honour SHALL fail with one error naming every such
option rather than ignoring it, so `--projection`, `--colorscheme`, `--view`,
`--render` and `--preview` with `--viewer web` fail naming them. Options with
viewer-independent meaning (`-o/--output`, `--time`, `--imgsize`, `--camera`)
SHALL behave equivalently under either viewer, and `--autocenter` and
`--viewall` describe what the web viewer does by default. When the viewer
package is not installed, `--viewer web` SHALL fail naming `pip install
"machinome[viewer]"` and write no image.

Node preparation, with the viewer's `present`, SHALL hold the project build
lock, and SHALL release it before the capture begins, so a snapshot never
blocks a rebuild while an image is being produced.

#### Scenario: A driver posed for a still

- **WHEN** an agent runs `machinome snapshot --drive units_entry=3` on a project
  declaring that driver
- **THEN** the image shows the machine posed at that driver value, and the
  drivers left unnamed stand at their declared defaults

#### Scenario: A coordinate is not a driver

- **WHEN** an agent runs `machinome snapshot --drive units.drum.turn=108` on a
  running root
- **THEN** the command fails naming that id as a joint coordinate the run
  owns, lists the declared drivers, and writes no image

#### Scenario: A name that is neither

- **WHEN** `--drive crnak=3` names no declared driver
- **THEN** the command fails listing the drivers the tree publishes, and
  writes no image

#### Scenario: Headless snapshot

- **WHEN** an agent runs `machinome snapshot --time 0.5 -o pose.png` on a
  machine with no X display but xvfb installed
- **THEN** a PNG of the project model at `$t = 0.5` is written to `pose.png`

#### Scenario: A ThrownTogether preview

- **WHEN** an agent runs `machinome snapshot --preview -o quick.png` with the
  OpenSCAD viewer
- **THEN** OpenSCAD draws the model with its ThrownTogether previewer and the
  PNG is written to `quick.png`, as it is for the same command without
  `--preview`

#### Scenario: Snapshotting a sub-assembly

- **WHEN** an agent runs `machinome snapshot windmill.windmill:Sail` with no `-o`
- **THEN** the image is written to a file derived from the resolved node, not
  to a fixed default name

#### Scenario: A snapshot does not block a rebuild

- **WHEN** a snapshot has finished preparing its node and is rendering the image
- **THEN** another process can acquire the project build lock and rebuild the
  same project

#### Scenario: Transparent snapshot for a host

- **WHEN** an agent runs `machinome snapshot --viewer web -o card.png` with the
  viewer installed
- **THEN** a PNG of the assembly with a transparent background is written to
  `card.png`

#### Scenario: An OpenSCAD-only option with the web renderer

- **WHEN** an agent runs `machinome snapshot --viewer web --colorscheme
  Metallic`
- **THEN** the command fails, reporting that `--colorscheme` is not supported
  by the web viewer, and writes no image

#### Scenario: The OpenSCAD extra is missing

- **WHEN** an agent runs `machinome snapshot` without choosing a viewer in an
  installation where `solid2` cannot be found
- **THEN** the command fails before loading the node with the line naming
  `machinome snapshot --viewer openscad`, the `openscad` extra,
  `pip install "machinome[openscad]"` and `--viewer web`, exits 1, and writes
  no image and no `.scad`

#### Scenario: The OpenSCAD binary is missing

- **WHEN** an agent runs `machinome snapshot` on an all-B-rep project on a
  machine with no `openscad` on the PATH
- **THEN** the command fails naming the missing binary and `--viewer web`,
  and writes no image

#### Scenario: The default does not follow the project's backends

- **WHEN** a snapshot is taken of an all-B-rep project that declares no
  viewer, without choosing one, on a machine where OpenSCAD and the
  `openscad` extra are installed
- **THEN** the OpenSCAD viewer produces the image, as it does for any other
  project

#### Scenario: The default does not follow the viewer's presence

- **WHEN** a snapshot is taken without choosing a viewer in an installation
  with `machinome-viewer`, of a project that declares none
- **THEN** the OpenSCAD viewer produces the image

#### Scenario: The web renderer without the viewer

- **WHEN** an agent runs `machinome snapshot --viewer web` in an installation
  without `machinome-viewer`
- **THEN** the command fails naming the extra, and writes no image

#### Scenario: The OpenSCAD node package is missing

- **WHEN** an agent runs `machinome snapshot` without choosing a viewer in an
  installation where the OpenSCAD viewer is installed and no installed
  distribution ships `machinome.node.openscad`
- **THEN** the command fails before loading the node with the line `Error:
  machinome snapshot --viewer openscad needs the openscad extra: the
  openscad node type (OpenScadNode) needs machinome.node.openscad, which is
  not installed; install it with 'pip install "machinome[openscad]"'; or use
  --viewer web`, exits 1, and writes no image and no `.scad`

#### Scenario: The table's renderer is the OpenSCAD node package's

- **WHEN** the OpenSCAD viewer is resolved in an installation with
  `machinome-viewer-openscad`
- **THEN** it is the module `machinome.viewer.openscad` of that distribution,
  and the table of supported node types names no viewer

#### Scenario: The former option is refused

- **WHEN** an agent runs `machinome snapshot --renderer web -o card.png`
- **THEN** the command exits 2 with the line `Error: machinome snapshot
  --renderer is --viewer since Machinome 0.9: write --viewer web`, loads no
  node and writes no image

#### Scenario: The project's viewer takes the image

- **WHEN** a project declares `viewer = "web"` under `[tool.machinome]` and an
  agent runs `machinome snapshot -o card.png`
- **THEN** the web viewer writes the image `--viewer web` writes

### Requirement: Export command

The system SHALL provide `machinome export [reference]` with `-o/--output` (default
`export`), `--fps` (default 30), `--frames` (default 360), `--viewer <name>`
(the viewer whose files the export embeds; default the project's declared
viewer, else `web`) and `--no-widget`. With the widget, the chosen viewer SHALL
be asked through the seam for the files it embeds, and a viewer that does not
embed SHALL be refused by name; `--no-widget` SHALL resolve no viewer. A node
that fails to load reports to stderr and exits 1. Artifact contents are
specified in the export capability.

#### Scenario: Default export

- **WHEN** a user runs `machinome export -o docs/_exports/windmill`
- **THEN** the output directory contains `manifest.json`, `models/`, and the
  embeddable widget files

#### Scenario: A viewer that does not embed

- **WHEN** a user runs `machinome export --viewer openscad`
- **THEN** the command fails naming the `openscad` viewer, embedding and
  `web`, and writes no output directory

### Requirement: Viewer command

The system SHALL provide `machinome viewer`, a command that takes no node path and
prints one JSON object on standard output with the absolute path of the
installed web viewer's bundle, the absolute path of its standalone export page,
its integer API version, the document versions it reads and the viewer package
version, the report the web viewer gives through the seam. When the viewer
package is not installed it SHALL print nothing on standard output, name
`pip install "machinome[viewer]"` on standard error, and exit 1.

#### Scenario: Viewer command appears in CLI help

- **WHEN** a user runs `machinome -h`
- **THEN** the command list includes `viewer`

#### Scenario: A consumer reads the installed viewer

- **WHEN** a program runs `machinome viewer` against an installation with
  `machinome-viewer`
- **THEN** it parses one JSON object carrying the bundle path, export page,
  API version and package version, and the command exits 0

#### Scenario: No bundle installed

- **WHEN** a user runs `machinome viewer` in an installation without
  `machinome-viewer`
- **THEN** the command exits 1 and standard error names the extra

#### Scenario: The report is the one the viewer's own command prints

- **WHEN** `machinome viewer` and `machinome-viewer describe` run in one
  installation
- **THEN** their standard outputs are identical

### Requirement: A snapshot never silently drops geometry OpenSCAD could not open

`machinome snapshot --viewer openscad` SHALL fail when OpenSCAD reports that it
could not open a file the design imports: the command SHALL exit non-zero
with an error naming the file OpenSCAD could not open and the `.scad` it was
rendering, and SHALL write no image. OpenSCAD reports such a file as a
warning and exits zero, so a command that only consults the exit status
reports success over a picture that is missing a part: the failure the
maker needs to see is the missing geometry, not the process status.

Every other warning, error or deprecation OpenSCAD reports on either stream
SHALL reach the operator's log, on the channel `viewer.openscad`, at a level a
normal run shows, rather than only the debug stream, so a warning the
framework does not classify is still visible to whoever is looking at the
image. OpenSCAD's progress output stays on the debug stream, as today.

This SHALL NOT change `--viewer web`, which renders from the published
document and opens no `.scad`.

#### Scenario: An unopenable import stops the image

- **WHEN** `machinome snapshot` renders a `.scad` whose `import()` names a file
  OpenSCAD cannot open
- **THEN** the command exits non-zero naming that file and the `.scad`, and
  no image file is written

#### Scenario: A clean render still succeeds

- **WHEN** `machinome snapshot` renders a design whose imports all resolve
- **THEN** the image is written and the command reports success, exactly as
  before

#### Scenario: Other OpenSCAD output is visible

- **WHEN** OpenSCAD reports a warning that is not an unopenable import
- **THEN** the run logs what OpenSCAD said and the image is still written
