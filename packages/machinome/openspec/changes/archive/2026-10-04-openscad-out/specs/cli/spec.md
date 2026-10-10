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
project's model is exact, regardless of whether the binary is installed, and
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

- **WHEN** an agent runs `machinome snapshot` on an all-exact project on a
  machine with no `openscad` on the PATH
- **THEN** the command fails naming the missing binary and `--renderer web`,
  and writes no image

#### Scenario: The default does not follow the project's backends

- **WHEN** a snapshot is taken of an all-exact project without choosing a
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

### Requirement: New command

The system SHALL provide `machinome new <name>` scaffolding a project offline from
templates packaged in the wheel. It SHALL normalize the input basename to an
ASCII Python package identifier `<package>` by replacing non-alphanumeric or
underscore characters with underscores, removing boundary underscores, and
using `project` when nothing remains. If that sanitized name starts with a
digit or is a Python keyword, the command SHALL prefix it with `project_`.
After deriving `<ClassName>` from that final package identifier, it SHALL
create:

- `<package>/pyproject.toml`, declaring
  `model = "<package>.<package>:<ClassName>"`;
- `<package>/<package>/__init__.py`;
- `<package>/<package>/<package>.py`, defining the model node: a
  `Solid2Node` from the `solid2` template when `machinome.node.solid2` imports,
  otherwise a `CadQueryNode` from the `cadquery` template when
  `machinome.node.cadquery` imports;
- `<package>/<package>/test_<package>.py`, defining a companion `TestCase`
  whose generated `test_solid_integrity` calls
  `assertNoDisconnectedSolids(self.node)` and whose generated
  `test_assembly_integrity` calls `assertNoSolidInterference(self.node)`; and
- `<package>/.gitignore`.

The node module and companion test filenames SHALL use the same normalized
package name, so the existing companion-file mapping discovers the tests
without a new loader convention. The generated tests SHALL be ordinary project
source: visible, editable, and deletable, with no registration or automatic
execution outside `machinome test`. The assembly test SHALL use the runner's
default testing instant and SHALL remain valid when the generated model is a
single rigid node.

When neither node type imports, the command SHALL write nothing and fail with
`Error: machinome new scaffolds its first part with SolidPython or CadQuery,
and neither is installed; install one with 'pip install "machinome[solid2]"' or
'pip install "machinome[cadquery]"'`, exit 1. It SHALL reach the two node types
through the table of supported node types, and the template it copies SHALL be
the only module of the framework, outside the OpenSCAD node family, that
imports SolidPython.

The command SHALL refuse to overwrite an existing target directory (exit 1)
and SHALL print next steps for entering the generated directory and running
`machinome develop`. It SHALL NOT predict a viewer kind or endpoint; the develop
command owns viewer selection, configured ports, and dependency diagnostics.

#### Scenario: Fresh project includes both declared integrity tests

- **WHEN** a user runs `machinome new my-project` in an empty directory
- **THEN** `my_project/my_project/my_project.py`,
  `my_project/my_project/test_my_project.py`, `my_project/pyproject.toml`, and
  `my_project/.gitignore` are created with no network access
- **AND** the companion test explicitly calls
  `assertNoDisconnectedSolids(self.node)` and
  `assertNoSolidInterference(self.node)` in separate named tests

#### Scenario: The scaffolded tests are discovered normally

- **WHEN** the user enters a freshly scaffolded project and runs `machinome test`
- **THEN** the existing companion-test loader discovers `test_<package>.py`
  and the summary counts exactly the two generated integrity tests
- **AND** both pass for the generated single-rigid-node model

#### Scenario: Non-test commands do not execute the scaffolded tests

- **WHEN** a freshly scaffolded project is run with `machinome build`,
  `machinome develop`, or `machinome snapshot`
- **THEN** the generated tests are not discovered or executed

#### Scenario: The template follows the installed extras

- **WHEN** `machinome new my-project` runs where `solid2` cannot be found and
  CadQuery is installed, and again where neither is installed
- **THEN** the first writes a `CadQueryNode` model whose generated source
  compiles, builds and passes its two tests with the mesh engine installed, and
  the second writes nothing and fails naming both extras

#### Scenario: Existing target is preserved

- **WHEN** the normalized target directory already exists
- **THEN** `machinome new` exits 1 without overwriting it

#### Scenario: Digit-leading project is made identifier-safe

- **WHEN** a user runs `machinome new 3d-printer`
- **THEN** the command creates `project_3d_printer` with package
  `project_3d_printer`, class `Project3dPrinter`, and a matching manifest
- **AND** its generated source compiles, builds, and tests without edits

#### Scenario: Python-keyword project is made identifier-safe

- **WHEN** a user runs `machinome new class`
- **THEN** the command creates `project_class` with package `project_class`,
  class `ProjectClass`, and a matching manifest
- **AND** its generated source compiles, builds, and tests without edits

#### Scenario: Next steps defer viewer details to develop

- **WHEN** `machinome new my-project` succeeds in any viewer installation or port
  configuration
- **THEN** its next steps name the generated directory and `machinome develop`
- **AND** they do not claim a browser URL or viewer kind

### Requirement: A command that needs an extra is answered by the extra

The command registry SHALL be able to name, for a command, the one node type
of the table of supported node types (`machinome.node.supported`) that command
needs beyond its own implementation, whose module is `machinome.node.<type>`;
the registry and the command's implementation SHALL NOT spell that module
themselves. Dispatching
that command SHALL import that module first; when the module refuses because
its kernel cannot be found (the `kernel-extras` capability), the CLI SHALL
print one line on standard error naming the command and the install line the
refusal names, and exit 1, without running or parsing the command. The extra
SHALL be the one the module's refusal names, not a second copy kept in the
CLI.

The command SHALL stay registered and listed whether or not its extra is
installed: `machinome -h` SHALL list it with its docstring help and SHALL NOT
import the module it needs, and an invocation of it SHALL never be reported as
an unknown command. `import-step` is the one such command; its entry names
the node type `step`, whose module is `machinome.node.step`, and the table's
`step` entry lists `import-step` among the commands that need it. No entry-point group or plugin registry SHALL be
consulted to find a command.

#### Scenario: The command is listed without its extra

- **WHEN** `machinome -h` is run in an installation without the `step`
  extra's kernel
- **THEN** the command list includes `import-step` with its docstring help,
  the command exits 0, and `machinome.node.step` is not imported

#### Scenario: Dispatching a command imports the module it needs

- **WHEN** `machinome import-step FILE` is dispatched with the `step` extra
  installed
- **THEN** `machinome.node.step` is imported before the command runs, and the
  command behaves as the Import-step command requirement states

#### Scenario: A command needing no module imports none

- **WHEN** `machinome viewer` is dispatched
- **THEN** no leaf module under `machinome.node` is imported
