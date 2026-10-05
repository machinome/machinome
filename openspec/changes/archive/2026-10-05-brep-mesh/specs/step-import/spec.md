## RENAMED Requirements

- FROM: `### Requirement: The STEP part is an exact leaf`
- TO: `### Requirement: The STEP part is a B-rep leaf`

## MODIFIED Requirements

### Requirement: The STEP part is a B-rep leaf

`StepNode` SHALL be a B-rep adapter under the `brep-geometry` capability:
`brep` is true, `shape()` returns the selected, adjusted, admitted
geometry in the node's own frame, its `.brep` artifact is persisted and
reloaded like any B-rep leaf's, it fuses on the B-rep engine with the other
B-rep adapters,
 and the spatial assertions answer on its B-rep. Its STL artifact
SHALL be written by the B-rep leaf path and SHALL therefore honour the
`linear_deflection` and `angular_deflection` the node declares, at the same
defaults every B-rep leaf has.

Producing its artifacts SHALL NOT require OpenSCAD or any other external
tool, and reading a STEP file SHALL NOT be a cost paid by a project that
declares no `StepNode`.

#### Scenario: The adapter is exact

- **WHEN** `brep` is read on a `StepNode`
- **THEN** it is true, and `shape()` returns the part's geometry in its own
  frame

#### Scenario: A STEP part fuses exactly with a modelled part

- **WHEN** a `FusionNode` fuses a `StepNode` with an overlapping
  `CadQueryNode`
- **THEN** the fusion has B-rep geometry and its shape is one solid

#### Scenario: A declared precision shapes the STEP part's mesh

- **WHEN** a `StepNode` declares `angular_deflection = 0.5`
- **THEN** its STL artifact holds strictly fewer triangles than the same
  node declaring nothing, and its `.brep` is unchanged
