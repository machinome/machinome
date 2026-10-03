## MODIFIED Requirements

### Requirement: The renderer is selected explicitly and never substituted

The system SHALL let a caller choose between the OpenSCAD renderer and the web
renderer, defaulting to OpenSCAD. When the web renderer is requested but cannot
run, the system SHALL fail with an error identifying what is missing, and SHALL
NOT render with the other renderer instead. A missing viewer package SHALL be
reported as `pip install "machinome[viewer]"`; a missing browser SHALL be
reported with the viewer package's own remedy, which names its `snapshot`
extra and the browser download step.

The rule SHALL hold symmetrically. When the OpenSCAD renderer is requested —
including by the default — and the OpenSCAD binary is unavailable, the system
SHALL fail with an error identifying the missing binary and naming the web
renderer as the alternative, and SHALL NOT render with the web renderer
instead. The same SHALL hold when the OpenSCAD engine, which writes the SCAD the
OpenSCAD renderer draws, is not installed: the error names the engine, the
module that could not be found, its install and the web renderer, before
OpenSCAD is launched.

The default renderer SHALL NOT vary with the availability of either renderer,
with whether the viewer package is installed, nor with whether the project's
model is exact. A default that followed availability would be substitution by
another name, and one that followed the project's backends would silently
change the appearance of snapshots taken of an existing project.

#### Scenario: The default renderer

- **WHEN** a maker renders a snapshot without choosing a renderer
- **THEN** the OpenSCAD renderer produces the image

#### Scenario: The viewer bundle is unavailable

- **WHEN** the web renderer is requested in an installation without
  `machinome-viewer`
- **THEN** the command fails naming the `viewer` extra, and writes no image

#### Scenario: The browser is unavailable

- **WHEN** the web renderer is requested and the viewer's browser dependency is
  not installed
- **THEN** the command fails with the viewer's remedy, naming both the package
  to install and the browser download step, and writes no image

#### Scenario: The renderer is run by the superuser

- **WHEN** the web renderer is requested by a process running as root
- **THEN** the command fails with an error explaining that the browser cannot
  be sandboxed as root, and writes no image

#### Scenario: The OpenSCAD binary is unavailable

- **WHEN** the OpenSCAD renderer is requested, by default or explicitly, and
  the binary is not on the PATH
- **THEN** the command fails naming the missing binary and the web renderer as
  the alternative, and writes no image

#### Scenario: The default is unchanged by an exact model

- **WHEN** a snapshot is rendered without choosing a renderer for a project
  whose model is entirely exact
- **THEN** the OpenSCAD renderer is selected, exactly as for any other project

#### Scenario: The OpenSCAD engine is unavailable

- **WHEN** the OpenSCAD renderer is requested and the OpenSCAD engine is not
  installed
- **THEN** the command fails naming the OpenSCAD snapshot renderer, the
  missing engine module and `--renderer web`, launches no OpenSCAD process,
  and writes no image

## ADDED Requirements

### Requirement: The OpenSCAD renderer writes the root's SCAD on demand

When the OpenSCAD renderer is selected, the snapshot command SHALL obtain the
SCAD it draws on demand, through the OpenSCAD engine, and from no build: after
posing and assembling the root inside the project build lock, it SHALL write
the root's `.scad` at the root's own artifact path in the build directory,
holding the text the root's `scad_code` gives in that pose, every artifact
import in it resolving from that file's directory, and SHALL write no other
node's `.scad` for the image. Every OpenSCAD snapshot SHALL write the file for
its own pose rather than reuse one an earlier run or build left. The file is
not a build artifact: the next successful build of that directory removes it
under the `build-pipeline` capability.

When the web renderer is selected, the snapshot command SHALL write and read
no `.scad`.

#### Scenario: The OpenSCAD renderer writes the root's SCAD

- **WHEN** `machinome snapshot --renderer openscad` renders a model whose root
  places an assembly and a flexible leaf, in a build directory holding no
  `.scad` for the root
- **THEN** the root's `.scad` exists at the root's artifact path holding the
  root's SCAD text in the snapshot's pose, OpenSCAD is given that file, and
  no `.scad` is written for the assembly or the flexible leaf

#### Scenario: Each snapshot presents its own pose

- **WHEN** two OpenSCAD snapshots of one root are taken at two different
  `--time` positions, one after the other
- **THEN** after each, the root's `.scad` holds the SCAD text of that
  snapshot's pose

#### Scenario: The web renderer touches no SCAD

- **WHEN** `machinome snapshot --renderer web` renders a model holding no
  SCAD-authored leaf, in a build directory holding no `.scad`
- **THEN** the image is written and no `.scad` exists under the build
  directory
