## MODIFIED Requirements

### Requirement: The OpenSCAD renderer writes the root's SCAD on demand

When the OpenSCAD renderer is selected, the snapshot command SHALL obtain the
SCAD it draws on demand, through the OpenSCAD node package's writer, and from
no build: after posing and assembling the root inside the project build lock,
the renderer SHALL write the root's `.scad` at `<basepath>.scad` of the root in
the build directory, holding the text the writer's `scad_code(root)` gives in
that pose, every artifact
import in it resolving from that file's directory, and SHALL write no other
node's `.scad` for the image. Every OpenSCAD snapshot SHALL write the file for
its own pose rather than reuse one an earlier run or build left. The file is
not a build artifact: it is published as transient in its currency record and
exists only for the renderer, which SHALL remove it and its currency record
once OpenSCAD has read it, whether the render succeeded or failed. A root that
declares that `.scad` in `kept_artifacts()` (a family leaf snapshotted alone)
keeps it, as its own build artifact, published as any kept artifact is, and
holding the leaf's own SCAD text under the `openscad-node` capability: a
snapshot of such a root whose STL is current SHALL leave the file its build
wrote as it was, and SHALL NOT rewrite it as an import of the leaf's STL. A file
an interrupted render left is removed, by its transient record, by the next
successful build whether or not the document changed, under the
`build-pipeline` capability.

When the web renderer is selected, the snapshot command SHALL write and read
no `.scad` and SHALL compose no presentation: it prepares the tree and builds
its STLs, so no flexible leaf's per-binding snapshot STL is written for it.

#### Scenario: The OpenSCAD renderer writes the root's SCAD

- **WHEN** `machinome snapshot --renderer openscad` renders a model whose root
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

- **WHEN** `machinome snapshot --renderer web` renders a model holding no
  SCAD-authored leaf, in a build directory holding no `.scad`
- **THEN** the image is written and no `.scad` exists under the build
  directory

#### Scenario: A current SCAD-authored root keeps its SCAD as built

- **WHEN** `machinome snapshot --renderer openscad` renders a `Solid2Node`
  root whose `.stl` a build made current
- **THEN** OpenSCAD is given the leaf's `.scad` holding the geometry its build
  wrote, and after the snapshot that file has the same bytes, the same inode
  and the same stamp as before it
