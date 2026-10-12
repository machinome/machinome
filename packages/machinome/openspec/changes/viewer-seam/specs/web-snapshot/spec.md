## MODIFIED Requirements

### Requirement: A snapshot can be rendered with a transparent background

The system SHALL render a node to a PNG carrying a real alpha channel, in which
every pixel not covered by the model is fully transparent, by having the web
viewer, `machinome.viewer.web`, present the node in a staging directory and
display that document in a headless browser and capture its canvas, in the
process of the command that asks it. The rendered model SHALL be the published
build of the node at the requested animation time.

#### Scenario: A host composites a model onto its own surface

- **WHEN** a maker renders a snapshot with the web viewer
- **THEN** the PNG's background pixels are fully transparent and the model
  pixels are opaque, so a host may composite it over any surface without
  removing a background

#### Scenario: An enclosed light feature survives

- **WHEN** the model contains a light-coloured region enclosed by the
  silhouette
- **THEN** that region remains opaque in the PNG

### Requirement: The web renderer reads the existing build without rebuilding it

The web viewer SHALL obtain geometry from the project's published build,
rendering only artifacts that are out of date, and SHALL NOT copy mesh data to
present it to the browser. Beyond rendering those artifacts it SHALL NOT alter
the published build: it SHALL describe the photographed node in its own staging
area rather than republishing the build's document, and SHALL leave artifacts
and recorded build errors that document names untouched. The snapshot command
SHALL hold the project build lock while it loads and poses the node and the
viewer presents it, bringing artifacts up to date and staging them, and SHALL
release it before the browser starts. Staged artifacts SHALL remain readable
for the whole capture even if the published build is republished meanwhile.

#### Scenario: A snapshot of an already-built project

- **WHEN** every artifact of the node is already current
- **THEN** the viewer rebuilds nothing and the capture reads the existing
  artifacts

#### Scenario: A rebuild lands while the browser is capturing

- **WHEN** another process republishes the build and removes artifacts the
  previous publication referenced, after the viewer has staged them
- **THEN** the capture still reads the staged artifacts and produces a complete
  model

#### Scenario: A snapshot of one part of a project being developed

- **WHEN** a maker photographs a node other than the one the published build
  describes
- **THEN** the published document still describes the same model afterwards,
  the artifacts it names are still present, and a recorded build error is still
  recorded

#### Scenario: Another producer waits for the build lock

- **WHEN** another build starts while a web snapshot holds the build lock
- **THEN** it waits, and once it acquires the lock it re-evaluates whether the
  published build covers its loaded source rather than skipping its build

### Requirement: The renderer is selected explicitly and never substituted

The system SHALL let a caller choose the viewer that takes the image by name,
with `--viewer openscad` or `--viewer web`, or by the project's declared viewer,
defaulting to OpenSCAD, under the `viewer-seam` capability's rule. When the
chosen viewer cannot run, the system SHALL fail with an error identifying what
is missing, and SHALL NOT render with another viewer instead. A missing web
viewer package SHALL be reported as `pip install "machinome[viewer]"`; a
missing browser SHALL be reported with the web viewer's own remedy, which names
its `snapshot` extra and the browser download step.

The rule SHALL hold symmetrically. When the OpenSCAD viewer is chosen,
including by the default, and the OpenSCAD binary is unavailable, the system
SHALL fail with an error identifying the missing binary and naming `--viewer
web` as the alternative, and SHALL NOT render with the web viewer instead. The
same SHALL hold when the OpenSCAD viewer cannot be imported, because its
distribution, the OpenSCAD node package whose writer it draws with, or
SolidPython is not installed: the error names the extra that installs what is
missing, the module that could not be found, its install line and `--viewer
web`, before the node is loaded and before OpenSCAD is launched.

The default viewer SHALL NOT vary with the availability of either viewer, with
whether the viewer package is installed, nor with whether the project's model
has B-rep geometry. A default that followed availability would be substitution
by another name, and one that followed the project's backends would silently
change the appearance of snapshots taken of an existing project. A project
SHALL change it only by declaring its viewer.

#### Scenario: The default renderer

- **WHEN** a maker renders a snapshot without choosing a viewer, in a project
  that declares none
- **THEN** the OpenSCAD viewer produces the image

#### Scenario: The viewer bundle is unavailable

- **WHEN** the web viewer is requested in an installation without
  `machinome-viewer`
- **THEN** the command fails naming the `viewer` extra, and writes no image

#### Scenario: The browser is unavailable

- **WHEN** the web viewer is requested and its browser dependency is not
  installed
- **THEN** the command fails with the viewer's remedy, naming both the package
  to install and the browser download step, and writes no image

#### Scenario: The renderer is run by the superuser

- **WHEN** the web viewer is requested by a process running as root
- **THEN** the command fails with an error explaining that the browser cannot
  be sandboxed as root, and writes no image

#### Scenario: The OpenSCAD binary is unavailable

- **WHEN** the OpenSCAD viewer is chosen, by default or explicitly, and the
  binary is not on the PATH
- **THEN** the command fails naming the missing binary and `--viewer web` as
  the alternative, and writes no image

#### Scenario: The default is unchanged by a B-rep model

- **WHEN** a snapshot is rendered without choosing a viewer for a project
  whose model is entirely B-rep and that declares no viewer
- **THEN** the OpenSCAD viewer is selected, exactly as for any other project

#### Scenario: The OpenSCAD engine is unavailable

- **WHEN** the OpenSCAD viewer is chosen and SolidPython, the `openscad`
  extra's kernel, is not installed
- **THEN** the command fails naming `machinome snapshot --viewer openscad`,
  the `openscad` extra, the missing module and `--viewer web`, loads no node,
  launches no OpenSCAD process, and writes no image

#### Scenario: The OpenSCAD viewer is not installed

- **WHEN** the OpenSCAD viewer is chosen in an installation where no
  distribution ships `machinome.viewer.openscad`
- **THEN** the command fails naming `machinome snapshot --viewer openscad`,
  the `viewer-openscad` extra and `--viewer web`, loads no node and writes no
  image

### Requirement: A requested camera is honoured or refused, never approximated

The web viewer SHALL accept a camera specification in either OpenSCAD form,
eye and target, or translation, rotations, and distance, resolve it to an eye,
a target, an up direction and the field of view OpenSCAD uses, and photograph
with those, so the same specification frames the model equivalently under
either viewer. A specification SHALL be honoured whatever the signs of its
values, including one whose resolved eye, target or up direction begins with a
negative component. Options the chosen viewer does not honour SHALL be refused
with an error naming them, rather than ignored.

#### Scenario: A maker asks for a specific viewpoint

- **WHEN** a maker renders the same camera specification with each viewer
- **THEN** both images frame the model from the same viewpoint at the same
  scale

#### Scenario: A rotated camera

- **WHEN** the camera is specified as a translation, rotations, and a distance
- **THEN** the model appears with the orientation those rotations describe,
  including any roll

#### Scenario: A camera vector that begins with a negative component

- **WHEN** a maker renders with `--viewer web --camera 0,0,0,65,0,35,1400`,
  whose resolved up direction is `(-0.2424..., 0.3462..., 0.9063...)`
- **THEN** the image is written, framed from the viewpoint those rotations
  describe, and the capture is not refused for the sign of a value

#### Scenario: An option the browser viewer cannot honour

- **WHEN** a maker requests the web viewer together with an OpenSCAD-only
  option
- **THEN** the command fails, naming the options that the web viewer does not
  support, and writes no image

#### Scenario: No camera requested

- **WHEN** no camera is specified
- **THEN** the whole model is framed automatically

### Requirement: The framework stages and the viewer photographs

The web viewer's provider SHALL hold every step of a web still: bringing
artifacts up to date and serializing the photographed node into its own
staging directory, from what the core offers it (the assembled node, the
presentation description, the document serializer and the artifact
inventory), linking the models it names, and photographing that directory with
the image size, the animation time and the resolved camera, in the command's
process. The snapshot command SHALL ask the provider to present the node inside
the build lock, to capture after the lock is released, and to withdraw the
staging directory afterwards whether the capture succeeded or failed. A
capture failure SHALL be reported with the viewer's own message and SHALL
write no image.

#### Scenario: The staged document is what the viewer photographs

- **WHEN** the web viewer takes an image
- **THEN** it photographs a directory holding the staged `viewer.json` and the
  models it names, and nothing of the project's published build is handed
  over or altered

#### Scenario: The viewer's failure is the framework's failure

- **WHEN** the web viewer's capture fails
- **THEN** the command fails with the viewer's message, writes no image and
  leaves no staging directory

### Requirement: The OpenSCAD renderer writes the root's SCAD on demand

When the OpenSCAD viewer is chosen, the snapshot command SHALL obtain the SCAD
it draws on demand, through the OpenSCAD node package's writer, and from no
build: after posing the root inside the project build lock, the viewer's
`present` SHALL assemble it and write the root's `.scad` at `<basepath>.scad`
of the root in the build directory, holding the text the writer's
`scad_code(root)` gives in that pose, every artifact import in it resolving
from that file's directory, and SHALL write no other node's `.scad` for the
image. Every OpenSCAD snapshot SHALL write the file for its own pose rather
than reuse one an earlier run or build left. The file is not a build artifact:
it is published as transient in its currency record and exists only for the
viewer, whose `withdraw` SHALL remove it and its currency record once OpenSCAD
has read it, whether the render succeeded or failed. A root that declares that
`.scad` in `kept_artifacts()` (a family leaf snapshotted alone) keeps it, as
its own build artifact, published as any kept artifact is, and holding the
leaf's own SCAD text under the `openscad-node` capability: a snapshot of such a
root whose STL is current SHALL leave the file its build wrote as it was, and
SHALL NOT rewrite it as an import of the leaf's STL. A file an interrupted
render left is removed, by its transient record, by the next successful build
whether or not the document changed, under the `build-pipeline` capability.

When the web viewer is chosen, the snapshot command SHALL write and read no
`.scad` and SHALL compose no presentation: the viewer prepares the tree and
builds its STLs, so no flexible leaf's per-binding snapshot STL is written for
it.

#### Scenario: The OpenSCAD renderer writes the root's SCAD

- **WHEN** `machinome snapshot --viewer openscad` renders a model whose root
  places an assembly and a flexible leaf, in a build directory holding no
  `.scad` for the root
- **THEN** OpenSCAD is given the root's `.scad` at the root's artifact path,
  holding the root's SCAD text in the snapshot's pose, no `.scad` is written
  for the assembly or the flexible leaf, and once OpenSCAD has read it the
  root's `.scad` is gone

#### Scenario: A failed render removes the root's SCAD too

- **WHEN** OpenSCAD fails while rendering the root's `.scad`
- **THEN** the command fails as before and the root's `.scad` is gone

#### Scenario: Each snapshot presents its own pose

- **WHEN** two OpenSCAD snapshots of one root are taken at two different
  `--time` positions, one after the other
- **THEN** each time, the root's `.scad` OpenSCAD is given holds the SCAD
  text of that snapshot's pose

#### Scenario: The web renderer touches no SCAD

- **WHEN** `machinome snapshot --viewer web` renders a model holding no
  SCAD-authored leaf, in a build directory holding no `.scad`
- **THEN** the image is written and no `.scad` exists under the build
  directory

#### Scenario: A current SCAD-authored root keeps its SCAD as built

- **WHEN** `machinome snapshot --viewer openscad` renders a `Solid2Node`
  root whose `.stl` a build made current
- **THEN** OpenSCAD is given the leaf's `.scad` holding the geometry its build
  wrote, and after the snapshot that file has the same bytes, the same inode
  and the same stamp as before it
