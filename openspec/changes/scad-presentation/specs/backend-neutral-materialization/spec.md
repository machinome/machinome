## MODIFIED Requirements

### Requirement: SCAD remains a supported output and compatibility boundary

Existing SCAD-facing calls, including public `assemble()` and `as_scad()`,
SHALL remain usable. `assemble()` SHALL return the node's presentation
description under the `scad-engine-dependency` capability, retaining the
placement order, colours and optimized artifact imports its SCAD carried; it
SHALL require neither SolidPython nor the OpenSCAD engine and SHALL write no
SCAD.

SCAD text SHALL be written only where a path reads it. A build SHALL write the
`.scad` of a leaf whose geometry is authored in SCAD (a `Solid2Node`, an
`OpenScadNode`, or a project leaf overriding `as_scad`), from which OpenSCAD
renders that leaf's STL, and SHALL write no other `.scad`: none for an
assembly, a fusion, a flexible leaf or any other leaf, with or without the
engine. `machinome snapshot --renderer openscad` SHALL write the root's
`.scad` on demand, under the `web-snapshot` capability, because the OpenSCAD
renderer draws it. With the engine installed, a caller MAY ask any node for its
SCAD text (`scad_code`) or have it write its `.scad` (`generate_scad()`).
Whatever SCAD is written SHALL use the same prepared machine and canonical
geometry as other consumers. Without the engine, a build of a tree with no
SCAD-authored leaf SHALL complete writing no `.scad` and SHALL log nothing
about SCAD presentation, since nothing in it asks for SCAD; a SCAD-authored
leaf meets the refusal of the `scad-engine-dependency` capability.

The system SHALL preserve OpenSCAD and Solid2 modelling support and legacy
SCAD-only adapter overrides. The OpenSCAD snapshot renderer SHALL remain
selectable with its existing default and missing-tool behavior. Flexible SCAD
output SHALL retain its numeric-snapshot and symbolic-time limitations; it
SHALL NOT be described as supporting live independent driver controls. The
OpenSCAD GUI SHALL NOT be offered as a machinome viewer or automatic
development fallback.

SCAD text is presentation, not the machine's identity. Equivalent output text
is permitted where artifact references replace obsolete fusion expressions,
but SCAD presentation SHALL NOT compute a second faceted fusion with a
different geometry engine.

#### Scenario: A direct SCAD caller remains supported

- **WHEN** existing project code asks for `node.assemble()` or `node.scad_code`
  with the OpenSCAD engine installed
- **THEN** `assemble()` returns the node's presentation description and
  `scad_code` the SCAD text the engine writes of it, with the existing
  transform and colour semantics, even if native preparation already occurred

#### Scenario: assemble() writes no SCAD

- **WHEN** `node.assemble()` is called on an assembly of exact, imported STL
  and flexible leaves with the OpenSCAD engine installed
- **THEN** it returns the presentation description and no `.scad` is written
  for any node

#### Scenario: assemble() without the engine

- **WHEN** a project of exact and imported STL leaves calls `node.assemble()`
  and then `node.build_stls()` with the OpenSCAD engine absent
- **THEN** both succeed, every node is linked and prepared, `mesh` answers in
  world coordinates, and no `.scad` is written

#### Scenario: A build writes SCAD only for SCAD-authored leaves

- **WHEN** an ordinary `machinome build` of a project holding an assembly, a
  fusion, a flexible leaf, an exact leaf and a `Solid2Node` leaf completes
  with the OpenSCAD engine installed
- **THEN** the only `.scad` under its build directory is the `Solid2Node`
  leaf's, and repeated unchanged builds do not rewrite it

#### Scenario: OpenSCAD users obtain a machine's SCAD on demand

- **WHEN** a person wants the SCAD of a built machine
- **THEN** `node.scad_code` gives any node's SCAD text, and `machinome
  snapshot --renderer openscad` renders the root's SCAD with OpenSCAD and
  then removes the file it wrote for it

#### Scenario: A normal build without the engine

- **WHEN** an ordinary `machinome build` of a project whose leaves need no
  OpenSCAD completes with the OpenSCAD engine absent
- **THEN** it publishes the same document and artifacts it publishes with the
  engine, writes no `.scad`, and logs nothing about SCAD presentation

#### Scenario: SCAD and browser view the same fused part

- **WHEN** a faceted fusion is rendered from SCAD and in a browser export
- **THEN** both consume the canonical fused artifact rather than independently
  fusing the ingredients with different engines

#### Scenario: Viewer policy is independent of SCAD support

- **WHEN** `machinome develop` runs without the optional browser viewer package
  and OpenSCAD is available
- **THEN** it fails naming the viewer extra rather than treating modelling or
  SCAD-output support as an interactive viewer

#### Scenario: The OpenSCAD snapshot boundary remains

- **WHEN** `machinome snapshot --renderer openscad` renders a numerically bound
  machine pose
- **THEN** it writes the root's SCAD presentation for that pose on demand and
  renders it with OpenSCAD, with the existing snapshot behavior
