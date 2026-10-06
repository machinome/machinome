## MODIFIED Requirements

### Requirement: Snapshot command

The system SHALL provide `machinome snapshot [reference]` rendering a PNG, with
options: `-o/--output` (defaulting to a file name derived from the resolved
node), `--time` (0.0–1.0, validated, default
0.0, applied via `set_keyframe`), `--camera` (gimbal or vector spec),
`--autocenter`, `--viewall`, `--imgsize` (default `1920x1080`, validated),
`--projection` (`ortho`|`perspective`), `--colorscheme` (the 11 OpenSCAD
schemes, default Cornfield), mutually exclusive `--render`/`--preview`,
`--view` (comma-separated of axes, crosshairs, edges, scales, wireframe),
`--renderer` (`web` and the renderers the table of supported node types
lists, today `openscad`; default the table's `DEFAULT_RENDERER`, `openscad`),
and `--drive NAME=VALUE` (repeatable). The snapshot command SHALL name no
renderer technology itself: it SHALL reach every renderer other than `web`
through the table of supported node types (`machinome.node.supported`), whose
`openscad` entry names the OpenSCAD renderer at `machinome.viewers.openscad` in
a provisional column, until the viewers become providers behind
`machinome.viewer`.

`--drive` SHALL bind a DECLARED DRIVER by its qualified id, to a value parsed
as a number and checked by the declaration exactly as `set_state` checks it,
after the node is loaded and before it is keyframed and assembled, under
either renderer. It is distinct from `--set`, which reaches the root's
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
requested driver values — the state a simulation itself starts from, and
admissible by construction. A state carrying HISTORY is not posed from the
command line: only a run knows which banks are reachable.

The default renderer SHALL remain `openscad` regardless of whether the
project's model has B-rep geometry, regardless of whether the binary is installed, and
regardless of whether the viewer package is installed. Choosing a renderer by
availability, or by the project's backends, would change the appearance of
snapshots taken of existing projects; the renderer is selected explicitly and
never substituted, as the web-snapshot capability requires.

With `--renderer openscad` the image is produced by the OpenSCAD CLI; without a
`DISPLAY` it SHALL wrap the render under `xvfb-run -a`, and error clearly if
xvfb is also unavailable. When the renderer's node type cannot be imported —
the `openscad` extra's SolidPython is absent, or the OpenSCAD node package is
not installed — the command SHALL fail at its start, before loading the node,
with one line `Error: machinome snapshot --renderer openscad needs the openscad
extra: <the refusal>; or use --renderer web`, exit 1, and write nothing. When
the OpenSCAD binary itself is unavailable the command SHALL fail naming it and
naming `--renderer web` as the alternative, and SHALL write no image.

Under the OpenSCAD renderer, `--preview` SHALL draw the image with OpenSCAD's
ThrownTogether previewer, and a snapshot taken with `--preview` SHALL write its
image as one taken without it does. The option SHALL reach the OpenSCAD CLI in
the form that binary accepts for that previewer, and SHALL never leave the
binary reading the model's `.scad` path as the option's own value.

The OpenSCAD renderer alone SHALL compose the root's presentation for the
image (it calls `assemble()` inside the build lock); the web renderer SHALL
prepare the tree and build its STLs without composing one.

With `--renderer web` the image is produced by the installed viewer package's
capture, run as a separate process on a staging directory the framework
prepares, with a transparent background, as specified in the web-snapshot
capability, and no X display is required. `--projection`, `--colorscheme`,
`--view`, `--render`, and `--preview` are OpenSCAD-only: supplying any of
them together with `--renderer web` SHALL fail with an error naming them
rather than ignoring them. Options with renderer-independent meaning —
`-o/--output`, `--time`, `--imgsize`, `--camera` — SHALL behave equivalently
under either renderer, and `--autocenter` and `--viewall` describe what the
web renderer does by default. When the viewer package is not installed,
`--renderer web` SHALL fail naming `pip install "machinome[viewer]"` and
write no image.

Node preparation SHALL hold the project build lock, and SHALL release it before
the render begins, so a snapshot never blocks a rebuild while an image is being
produced.

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
  OpenSCAD renderer
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

- **WHEN** an agent runs `machinome snapshot --renderer web -o card.png` with the
  viewer installed
- **THEN** a PNG of the assembly with a transparent background is written to
  `card.png`

#### Scenario: An OpenSCAD-only option with the web renderer

- **WHEN** an agent runs `machinome snapshot --renderer web --colorscheme
  Metallic`
- **THEN** the command fails, reporting that `--colorscheme` is not supported
  by the web renderer, and writes no image

#### Scenario: The OpenSCAD extra is missing

- **WHEN** an agent runs `machinome snapshot` without choosing a renderer in an
  installation where `solid2` cannot be found
- **THEN** the command fails before loading the node with the line naming
  `machinome snapshot --renderer openscad`, the `openscad` extra,
  `pip install "machinome[openscad]"` and `--renderer web`, exits 1, and writes
  no image and no `.scad`

#### Scenario: The OpenSCAD binary is missing

- **WHEN** an agent runs `machinome snapshot` on an all-B-rep project on a
  machine with no `openscad` on the PATH
- **THEN** the command fails naming the missing binary and `--renderer web`,
  and writes no image

#### Scenario: The default does not follow the project's backends

- **WHEN** a snapshot is taken of an all-B-rep project without choosing a
  renderer, on a machine where OpenSCAD and the `openscad` extra are
  installed
- **THEN** the OpenSCAD renderer produces the image, as it does for any other
  project

#### Scenario: The default does not follow the viewer's presence

- **WHEN** a snapshot is taken without choosing a renderer in an installation
  with `machinome-viewer`
- **THEN** the OpenSCAD renderer produces the image

#### Scenario: The web renderer without the viewer

- **WHEN** an agent runs `machinome snapshot --renderer web` in an installation
  without `machinome-viewer`
- **THEN** the command fails naming the extra, and writes no image
