# Backend-Neutral Materialization Specification

## Purpose

Defines geometry preparation and composition without SCAD as an intermediate,
while retaining OpenSCAD as a supported modelling, output and fixed-pose
snapshot boundary.
## Requirements
### Requirement: Machine composition is independent of SCAD presentation

A project SHALL be usable for geometry tests, portable export, browser
development and web snapshots without constructing a SCAD assembly as an
intermediate representation. The system SHALL preserve the same node names,
hierarchy, colours, rigid/flexible distinctions, driver bindings, motion and
geometry that those consumers expose through their existing contracts.

This independence SHALL apply to native adapters. Geometry authored in
OpenSCAD SHALL still be evaluated through its own supported backend boundary,
the OpenSCAD node package of the `openscad-node` capability, without making
the rest of the machine use SCAD for composition. No other leaf SHALL reach
that boundary: a native producer's failure, or a leaf that produced no STL, is
refused naming the leaf, never handed to OpenSCAD as a fallback.

#### Scenario: Native export without assembly SCAD

- **WHEN** a project containing exact leaves, imported STL leaves and a
  port-driven flexible leaf is exported with SCAD presentation disabled
- **THEN** the complete export succeeds with its rigid geometry, flexible
  shape and interactive controls intact, without assembly SCAD or flexible
  SCAD snapshot artifacts

#### Scenario: Geometry tests use the same placed machine

- **WHEN** a native multi-backend project with nested rotations and
  translations is built for tests without SCAD presentation
- **THEN** its mesh and exact questions see the same local and world frames
  and the same bound pose as its published machine

#### Scenario: A SCAD leaf does not impose SCAD composition on siblings

- **WHEN** an assembly mixes an OpenSCAD-authored leaf with native leaves
- **THEN** its authored leaf uses OpenSCAD when needed, while native siblings
  produce their geometry without SCAD conversion

#### Scenario: Independent preparation does not change phase ordering

- **WHEN** one subtree binds a coordinate used by a body in another subtree
- **THEN** the complete simulation phase runs before geometry reads and every
  consumer sees the final binding, without a second placement being stacked

### Requirement: Backend geometry retains its own capabilities

Native geometry production SHALL preserve each built-in adapter's validation,
source tracking, artifact freshness, native geometry and declared precision.
Exact nodes SHALL retain exact geometry and their existing BREP/STL contract;
sheet parts SHALL retain DXF output; imported meshes SHALL retain explicit
selection, adjustment and admission rules; JSCAD SHALL retain its own native
tool. No common mesh representation SHALL replace exact geometry merely to
prepare a machine.

Current rigid geometry SHALL be reusable without re-running its CAD render.
Flexible shape SHALL remain a function of its current ports rather than enter
the rigid artifact cache. A change of pose SHALL NOT change structural
parameter identity.

#### Scenario: Exact capabilities survive native composition

- **WHEN** a project mixes CadQuery, build123d and STEP exact leaves in a fusion
- **THEN** it retains exact fusion and the current BREP and tessellation
  behavior without requiring OpenSCAD or the mesh union engine

#### Scenario: A current sheet part stays current

- **WHEN** a sheet part's required BREP, STL and DXF are current
- **THEN** native preparation reuses those artifacts without evaluating its
  profile again, and missing any required artifact causes its ordinary rebuild

#### Scenario: Flexible state is evaluated only by its consumer

- **WHEN** a flexible leaf is published interactively and then inspected at
  two numeric bindings
- **THEN** publication retains its symbolic parameters, numeric geometry
  reflects each binding, and no rigid geometry identity is minted per pose

### Requirement: Faceted fusions produce the union of their placed child meshes

A non-exact `FusionNode` SHALL produce the geometric union of its children's
current meshes in the fusion's local frame using the supported mesh union
engine, without an OpenSCAD fusion render. Nested child fusions SHALL
contribute their fused geometry once. The fusion's own placement and its
ancestors' placements SHALL remain outside its artifact.

The result SHALL preserve overlapping, contained, identical, disjoint and
face-touching solid unions within the input mesh precision. A mixed fusion
SHALL use its exact children's declared tessellations; it SHALL NOT claim an
exact result. Different triangulation or STL bytes SHALL NOT by themselves
constitute a geometry failure, and piece IDs SHALL still describe those bytes.
Disconnected valid results SHALL remain permitted until the project asks for
a connectivity assertion.

#### Scenario: Overlapping solids fuse rather than concatenate

- **WHEN** two valid box meshes of known dimensions overlap in a fusion
- **THEN** the result has the analytic union volume and bounds, without an
  internal duplicate surface or double-counted overlap

#### Scenario: Identical and contained solids do not add material

- **WHEN** one child is identical to, or wholly contained within, another
- **THEN** the union occupies only the outer solid's volume

#### Scenario: Disconnected material is not a build assertion

- **WHEN** valid child meshes are disjoint and no connectivity test is requested
- **THEN** the artifact contains both solids and the build does not reject
  them solely for being disconnected

#### Scenario: Faces that touch can join

- **WHEN** valid box meshes meet exactly on one complete face
- **THEN** the union contains their combined material without a spurious gap

#### Scenario: Nested placement is applied once

- **WHEN** a rotated nested fusion is translated within another fusion whose
  root is also placed in an assembly
- **THEN** the enclosing artifact includes the nested placement once, excludes
  its own assembly placement, and displays correctly in the assembled machine

### Requirement: Fusion failures are explicit and preserve published state

A mesh union failure SHALL identify the fusion and the engine's reason,
including the offending child when identifiable. The system SHALL NOT change
engines, repair the source, fill holes, move surfaces or substitute mesh
concatenation to turn that failure into a successful build. A failed producer
SHALL NOT overwrite the prior artifact with a partial result or publish a
viewer document certifying the failed geometry.

These production-validity checks SHALL NOT introduce whole-model geometry
assertions into normal build publication.

#### Scenario: The engine rejects an input

- **WHEN** a fusion input cannot be admitted by the mesh union engine
- **THEN** the build reports the fusion, input and engine reason, without an
  OpenSCAD retry or an automatically repaired replacement

#### Scenario: A replacement union fails

- **WHEN** a fusion with a previously published artifact fails to produce its
  replacement
- **THEN** its old complete artifact and currency record remain readable and
  no new viewer document certifies the failed replacement

### Requirement: SCAD remains a supported output and compatibility boundary

Public `assemble()` SHALL remain usable. It SHALL return the node's
presentation description (`machinome.node.presentation`), composed through
each node's `present()`, retaining the placement order, colours and optimized
artifact imports its SCAD carried; it SHALL require no node package and SHALL
write no SCAD. The core SHALL write no SCAD at all: SCAD is the OpenSCAD node
package's output, under the `openscad-node` capability.

SCAD text SHALL be written only where a path reads it. A build SHALL write the
`.scad` of a leaf of the OpenSCAD node family (a `Solid2Node`, an
`OpenScadNode`, or another subclass of the family's leaf base), from which
OpenSCAD renders that leaf's STL, and SHALL write no other `.scad`: none for an
assembly, a fusion, a flexible leaf or any other leaf, whatever is installed.
`machinome snapshot --renderer openscad` SHALL write the root's `.scad` on
demand, under the `web-snapshot` capability, because the OpenSCAD renderer
draws it. With the OpenSCAD node package installed, a caller MAY ask any node
for its SCAD text (`machinome.node.openscad.writer.scad_code(node)`, and
`scad_code` on a family leaf) or have it written
(`machinome.node.openscad.writer.generate_scad(node)`, and `generate_scad()` on
a family leaf). Whatever SCAD is written SHALL use the same prepared machine and
canonical geometry as other consumers. Without the package or SolidPython, a
build of a tree with no family leaf SHALL complete writing no `.scad` and SHALL
log nothing about SCAD, since nothing in it asks for SCAD; a project using a
family leaf meets the package's refusal at its import, under the `openscad-node`
capability.

The system SHALL preserve OpenSCAD and Solid2 modelling support, through the
`openscad` and `solid2` extras. A project leaf overriding a method named
`as_scad` is no longer a SCAD-only adapter: the core never calls it. The
OpenSCAD snapshot renderer SHALL remain selectable with its existing default
and missing-tool behavior, and SHALL be refused naming the `openscad` extra
when the package cannot be imported. Flexible SCAD
output SHALL retain its numeric-snapshot and symbolic-time limitations; it
SHALL NOT be described as supporting live independent driver controls. The
OpenSCAD GUI SHALL NOT be offered as a machinome viewer or automatic
development fallback.

SCAD text is presentation, not the machine's identity. Equivalent output text
is permitted where artifact references replace obsolete fusion expressions,
but SCAD presentation SHALL NOT compute a second faceted fusion with a
different geometry engine.

#### Scenario: A direct SCAD caller remains supported

- **WHEN** existing project code asks for `node.assemble()`, and for the SCAD
  text of the node through the OpenSCAD node package's writer (or `scad_code` on
  a family leaf), with the package installed
- **THEN** `assemble()` returns the node's presentation description and the
  writer the SCAD text of it, with the existing transform and colour semantics,
  even if native preparation already occurred

#### Scenario: assemble() writes no SCAD

- **WHEN** `node.assemble()` is called on an assembly of exact, imported STL
  and flexible leaves with the OpenSCAD node package installed
- **THEN** it returns the presentation description and no `.scad` is written
  for any node

#### Scenario: assemble() without the engine

- **WHEN** a project of exact and imported STL leaves calls `node.assemble()`
  and then `node.build_stls()` with SolidPython and the OpenSCAD node package
  absent
- **THEN** both succeed, every node is linked and prepared, `mesh` answers in
  world coordinates, and no `.scad` is written

#### Scenario: A build writes SCAD only for SCAD-authored leaves

- **WHEN** an ordinary `machinome build` of a project holding an assembly, a
  fusion, a flexible leaf, an exact leaf and a `Solid2Node` leaf completes
  with the OpenSCAD node package installed
- **THEN** the only `.scad` under its build directory is the `Solid2Node`
  leaf's, and repeated unchanged builds do not rewrite it

#### Scenario: A normal build remains useful to OpenSCAD users

- **WHEN** an ordinary `machinome build` completes
- **THEN** the `.scad` of each leaf whose geometry is authored in SCAD, from
  which OpenSCAD renders its STL, remains available, repeated unchanged
  builds do not rewrite it, and no other `.scad` is a build deliverable

#### Scenario: OpenSCAD users obtain a machine's SCAD on demand

- **WHEN** a person wants the SCAD of a built machine
- **THEN** `machinome.node.openscad.writer.scad_code(node)` gives any node's
  SCAD text, and `machinome snapshot --renderer openscad` renders the root's
  SCAD with OpenSCAD and then removes the file it wrote for it

#### Scenario: A normal build without the engine

- **WHEN** an ordinary `machinome build` of a project whose leaves need no
  OpenSCAD completes with SolidPython and the OpenSCAD node package absent
- **THEN** it publishes the same document and artifacts it publishes with
  them, writes no `.scad`, and logs nothing about SCAD

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

