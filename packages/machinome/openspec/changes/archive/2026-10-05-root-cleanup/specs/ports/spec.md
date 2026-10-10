## MODIFIED Requirements

### Requirement: Ports and the time base are not node exports

The system SHALL NOT export `Port`, `RotationalPort`,
`TranslationalPort`, `SignalPort`, `declared_ports` or `Time` from
`machinome.node`, and SHALL NOT provide a module
`machinome.node.ports` or `machinome.node.timebase`. There SHALL be no
re-export, alias, or deprecation shim by which a project can keep
importing them from the node package: a project that has not migrated
SHALL fail at its import line.

Reading one of those names — or either of the two removed submodule
names — as an attribute of `machinome.node` SHALL raise an error whose
message names `machinome.motion.ports` as the module that now answers
for it, so a reader of the failure learns where the name went. Because
the import machinery converts that attribute failure, `from
machinome.node import <name>` SHALL raise `ImportError` carrying the
same message.

#### Scenario: The old path is refused

- **WHEN** a project runs
  `from machinome.node import RotationalPort, SignalPort, Time`
- **THEN** the import raises `ImportError`, the message names
  `machinome.motion.ports` and shows the import line that replaces it,
  and no port or time-base name is bound

#### Scenario: The removed submodules are gone

- **WHEN** a consumer imports `machinome.node` and reads
  `machinome.node.ports` or `machinome.node.timebase`
- **THEN** the read fails with a message naming
  `machinome.motion.ports`, and no such module exists on disk

#### Scenario: A node class is still a node export

- **WHEN** a project runs `from machinome.node.assembly import AssemblyNode`
  after the move, and `from machinome.node import AssemblyNode`
- **THEN** the first receives the class, and the second raises `ImportError`
  naming `machinome.node.assembly`, not `machinome.motion.ports`: a node class
  is imported from its own module (`node-model`, "The node package's root
  exports nothing"), and only the port and time-base names are redirected to
  the motion package
