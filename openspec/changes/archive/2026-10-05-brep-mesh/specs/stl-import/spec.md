## RENAMED Requirements

- FROM: `### Requirement: Mesh-only faceted participation`
- TO: `### Requirement: Mesh-only participation`

## MODIFIED Requirements

### Requirement: Mesh-only participation

`StlNode` SHALL be a mesh adapter: `brep` is false, it exposes no
`shape()`, and it participates in a `FusionNode` through the mesh
union path, making the enclosing fusion a mesh fusion. Mesh-only is settled
doctrine for this adapter: the framework SHALL NOT offer a B-rep or
triangle-faced B-rep STL import route, and this is a recorded non-goal rather
than an open question.

#### Scenario: The adapter is not exact

- **WHEN** `brep` is read on an `StlNode` instance
- **THEN** it reports false, and reading `shape()` raises

#### Scenario: A fusion over an imported STL takes the mesh path

- **WHEN** a `FusionNode` combines an `StlNode` with a B-rep leaf
- **THEN** the fusion's `brep` is false and its union is produced

  through the mesh path, per the B-rep fusion composition rule
