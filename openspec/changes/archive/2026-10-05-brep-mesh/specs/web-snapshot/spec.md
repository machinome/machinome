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
instead. The same SHALL hold when the OpenSCAD node package, which writes the
SCAD the OpenSCAD renderer draws, cannot be imported, because SolidPython or
the package itself is not installed: the error names the `openscad` extra, the
module that could not be found, its install line `pip install
"machinome[openscad]"` and the web renderer, before the node is loaded and
before OpenSCAD is launched.

The default renderer SHALL NOT vary with the availability of either renderer,
with whether the viewer package is installed, nor with whether the project's
model has B-rep geometry. A default that followed availability would be substitution by
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
  whose model is entirely B-rep
- **THEN** the OpenSCAD renderer is selected, exactly as for any other project

#### Scenario: The OpenSCAD engine is unavailable

- **WHEN** the OpenSCAD renderer is requested and SolidPython, the `openscad`
  extra's kernel, is not installed
- **THEN** the command fails naming `machinome snapshot --renderer openscad`,
  the `openscad` extra, the missing module and `--renderer web`, loads no node,
  launches no OpenSCAD process, and writes no image
