## MODIFIED Requirements

### Requirement: Leaf adapters are distinct types

Each leaf adapter SHALL be a distinct type, and no adapter SHALL be an
instance of another. Adapters that share an implementation base SHALL NOT
thereby become interchangeable to a type test: a project or a framework path
that distinguishes backends by `isinstance` or by walking the method
resolution order SHALL get the same answer whatever bases the adapters happen
to share.

This constrains how shared adapter behaviour may be factored. It does not
require any particular factoring. The shared leaf bases — `LeafNode`,
`ExactLeafNode`, `SheetLeafNode` and `FlexibleNode` — are the declared
extension points of the `leaf-contract` capability; declaring them does not
make two adapters sharing one interchangeable, and an adapter written outside
the core against one of them is as distinct a type as the core's own.

Sharing a base SHALL NOT change which framework path a leaf reaches: an exact
adapter, whatever bases it shares, writes its STL through the exact engine and
SHALL NOT reach the OpenSCAD rendering path.

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

#### Scenario: A shared base does not route an exact adapter through OpenSCAD

- **WHEN** a `CadQueryNode`, a `Build123dNode` or a `Build123dSheetNode` leaf
  is prepared and its STL generated with OpenSCAD's availability check and
  subprocess launch both made to fail
- **THEN** its STL is written and neither the check nor the launch is
  attempted

## ADDED Requirements

### Requirement: No node type is recognised by its class name

The core SHALL NOT decide anything about a node by the spelling of its class
name, or of any class in its method resolution order: no module under
`machinome/` SHALL compare a class's `__name__` or `__qualname__` with a
string literal, nor a string literal naming a class defined under
`machinome/` with any value. What a path needs to know about a node it SHALL
learn from members the node declares or inherits, so a node type written
outside the core is treated exactly as a core type that declares the same
members. A class name MAY be displayed, as in a refusal naming a node and its
class.

#### Scenario: No core module compares a class name to a string

- **WHEN** every module under `machinome/` is parsed and each comparison is
  examined
- **THEN** none compares a `__name__` or `__qualname__` attribute with a
  string literal or a collection of string literals, and none compares a
  string literal that spells a class defined under `machinome/`

#### Scenario: A refusal describes a node by its own class only

- **WHEN** a `Solid2Node` subclass `ScadPart` and a SCAD-presented `LeafNode`
  subclass `MeshScad` defined outside `machinome/` both reach STL generation
  with no `openscad` on the PATH
- **THEN** each refusal names its own node and its own class, and neither
  names `Solid2Node`, another core class or a backend
