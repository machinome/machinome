## MODIFIED Requirements

### Requirement: Leaf adapters are distinct types

Each leaf adapter SHALL be a distinct type, and no adapter SHALL be an
instance of another. Adapters that share an implementation base SHALL NOT
thereby become interchangeable to a type test: a project or a framework path
that distinguishes backends by `isinstance` or by walking the method
resolution order SHALL get the same answer whatever bases the adapters
happen to share.

This constrains how shared adapter behaviour may be factored. It does not
require any particular factoring. The shared leaf bases — `LeafNode`,
`ExactLeafNode`, `SheetLeafNode` and `FlexibleNode` — are the declared
extension points of the `leaf-contract` capability; declaring them does not
make two adapters sharing one interchangeable, and an adapter written outside
the core against one of them is as distinct a type as the core's own.

#### Scenario: Adapters sharing a base stay distinct

- **WHEN** the exact adapters `CadQueryNode` and `Build123dNode` are tested
  against each other with `isinstance`
- **THEN** neither is an instance of the other, and each remains its own type

#### Scenario: The sheet adapter is not its backend's solid adapter

- **WHEN** `Build123dSheetNode` and `Build123dNode` are tested against each
  other with `isinstance`
- **THEN** neither is an instance of the other, though both drive build123d

#### Scenario: An adapter written outside the core is its own type

- **WHEN** an `ExactLeafNode` subclass defined outside `machinome/` is tested
  against `CadQueryNode` and `Build123dNode` with `isinstance`
- **THEN** it is an instance of neither, and neither is an instance of it

#### Scenario: The backend lookup is not confused by a shared ancestor

- **WHEN** a node's STL generation resolves the backend name by walking the
  method resolution order for adapter class names
- **THEN** an exact adapter resolves to no mesh-rendering backend, as it did
  before any base was shared, and never launches OpenSCAD
