## ADDED Requirements

### Requirement: An internal node's children are refused before they are linked

An internal node's `children` SHALL be the list the framework's
preparation or presentation last assigned when it linked the node's
children, and the framework assigns it only after the tree's `render()`
and `simulate()` phases have run. Inside an assembly's `render()` or
`simulate()` phase, a read of the `children` of an internal node to which
nothing has yet been assigned — the assembly's own or any other internal
node's — SHALL be refused with a `StructureError`, at the read, naming the
assembly whose phase is running, the phase, what was read
(`self.children`, or the read node's name followed by `.children`), and
what to address instead: the node's declared children by the attributes
that declare them, or, for a node that declares none, its own `render()`,
which builds them. Such a read SHALL NOT answer an empty list.

Every other read SHALL answer as before: a read, in any phase or none,
after the node's children have been assigned SHALL answer the assigned
list; a read outside any phase before they have been assigned SHALL
answer an empty tuple; a leaf's `children` SHALL answer an empty tuple
in every phase.

#### Scenario: A simulate-phase read is refused

- **WHEN** an assembly declaring `near` and `far` reads `self.children`
  in `simulate()` to rotate each child, and the tree is enumerated for the
  first time by `set_state`, the loader, the serializer or `assemble()`
- **THEN** a `StructureError` is raised naming the assembly, `simulate()`,
  `self.children`, and `self.near` and `self.far` as what to address,
  where the read used to answer an empty list and rotate nothing

#### Scenario: A render-phase read is refused

- **WHEN** an assembly's `render()` reads `self.children` to colour its
  children, or reads the `children` of a child internal node it declares
- **THEN** a `StructureError` is raised naming the assembly, `render()`
  and the read, and naming the read node's declared attributes, or, when
  it declares none, saying that its own `render()` builds them

#### Scenario: The same loop over the declared attributes works

- **WHEN** the assembly's `simulate()` rotates `self.near` and `self.far`
  by a driver instead
- **THEN** both children carry the rotation after the first enumeration,
  and nothing is refused

#### Scenario: A read after linking, or outside any phase, is unchanged

- **WHEN** an internal node is read outside any phase before anything has
  linked it, and again after `assemble()` has linked it, both outside any
  phase and inside a later enumeration's phase
- **THEN** the first read answers an empty tuple and every later read
  answers the linked children, as before; a leaf's `children` answers an
  empty tuple inside a phase
