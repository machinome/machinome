## MODIFIED Requirements

### Requirement: Composite node tree

The system SHALL model a project as a tree of nodes rooted in
`AbstractBaseNode`, where `InternalNode` subclasses compose children and
`LeafNode` subclasses generate geometry. An `InternalNode.render()` SHALL
return a list or tuple of node instances, or `None` on a class with
declared children under the `declarative-nodes` capability, in which case
the framework substitutes the realized declared children minus the omitted
ones before any consumer sees the result. A `LeafNode.render()` SHALL
return a single geometry object, never a list and never `None`. Validation
runs during framework preparation before geometry production or SCAD
presentation. Public `assemble()` uses that same preparation and returns its
presentation description; neutral consumers compose the tree without a SCAD
union.

#### Scenario: Internal node returns children

- **WHEN** an `InternalNode` subclass's `render()` returns a list of
  `AbstractBaseNode` instances
- **THEN** preparation links and prepares each child; `assemble()` presents
  the assembly's children together, or the canonical fused geometry for a
  fusion, preserving their placements

#### Scenario: Internal node returns nothing

- **WHEN** an `InternalNode` subclass with declared children defines a
  `render()` that positions them and returns nothing
- **THEN** `assemble()` links, prepares and presents the declared children
  exactly as if `render()` had returned them in declaration order

#### Scenario: Structural contract violations are rejected

- **WHEN** an `InternalNode.render()` returns a non-list that is not the
  declarative `None`, returns an element that is not an `AbstractBaseNode`,
  or returns an instance of its own type
- **THEN** validation raises an error during `assemble()`
- **WHEN** a `LeafNode.render()` returns a list, returns `None`, or returns
  an object whose module does not start with the adapter's declared
  `namespace`
- **THEN** validation raises an error during `assemble()`

### Requirement: Template-method render lifecycle

The system SHALL control preparation, validation, native artifact production
and placement through a framework-owned lifecycle. Users SHALL NOT override
that lifecycle. Native geometry consumers SHALL NOT require `as_scad()` or
SCAD generation to prepare the tree or produce its native artifacts.
Public `assemble()` SHALL remain a SCAD compatibility entry point over the
same prepared tree: it composes the node's presentation description under the
`scad-engine-dependency` capability, preserves optimized imports and colours,
applies queued operations in their existing order, and returns that
description. It SHALL request no SCAD presentation: it SHALL write no
`.scad` for any node, with or without the OpenSCAD engine, and SHALL require
neither SolidPython nor the engine. A node's `.scad` is written only by the
paths that read it, under the `backend-neutral-materialization` capability.
`assemble()` SHALL be idempotent — the result is memoized and `render()` is
called at most once per instance. On an assembly the framework SHALL run
`simulate()` after `render()` ONCE PER ENUMERATION of the tree, under the
current binding: the `render()` that begins an enumeration drives the
simulate phase of every assembly in the subtree it renders, parents
before children, before it returns, and a later `render()` reached by the
walk's own descent within that same enumeration SHALL return the
children at rest without running that assembly's phase again. Every
assembly's motion is therefore in place before the walk reads any of the
tree's geometry. Users override `render()` and `simulate()`, never
`assemble()` or the framework's preparation lifecycle. The same simulation
ordering SHALL hold for native preparation and SCAD compatibility consumers.

#### Scenario: Assemble is memoized

- **WHEN** `assemble()` is called twice on the same instance
- **THEN** `render()` runs only once and the cached result is returned

#### Scenario: Optimized import of cached STL

- **WHEN** a node has `optimize = True`, is rigid, and its STL is up to date
- **THEN** `assemble()` presents an import of the STL artifact instead of
  inlining the SCAD model, and queued operations are applied after the import

#### Scenario: An up-to-date leaf is not rendered

- **WHEN** a rigid optimizing leaf's artifact is up to date and `assemble()` runs
- **THEN** the node's `render()` is not called and no CAD geometry is computed

#### Scenario: A stale leaf is rendered

- **WHEN** any file tracked for that leaf has changed since its artifact was written
- **THEN** `assemble()` renders the node and regenerates the artifact

#### Scenario: Simulate follows render

- **WHEN** an assembly defining both `render()` and `simulate()` is
  assembled
- **THEN** `render()` has run before `simulate()`, and the queued
  operations applied include those `simulate()` produced

#### Scenario: Every phase precedes the first geometry read

- **WHEN** a root with two subtrees is assembled
- **THEN** both subtrees' `simulate()` methods ran before the first
  subtree's geometry was composed, so a coordinate bound while the
  second subtree simulated still moves a body in the first

#### Scenario: Assemble writes no SCAD

- **WHEN** `assemble()` is called with the OpenSCAD engine installed on an
  assembly of an exact leaf and a `Solid2Node` leaf whose artifacts are
  current
- **THEN** it returns the presentation description and no `.scad` file is
  written or rewritten, the assembly's included

#### Scenario: Assemble without the OpenSCAD engine

- **WHEN** `assemble()` is called on an assembly of native artifact-owning
  leaves with the OpenSCAD engine absent
- **THEN** it renders, validates, links, simulates and prepares exactly as with
  the engine, returns the same presentation description, and writes no
  `.scad`

#### Scenario: Native preparation is independent of SCAD presentation

- **WHEN** an assembly of native artifact-owning leaves is exported or built
  for geometry tests and its SCAD presentation methods are unavailable
- **THEN** structure, validation, motion, geometry and publication succeed
  without invoking those presentation methods
