## ADDED Requirements

### Requirement: Skills command

When the distribution `machinome-skills` is installed, `machinome skills`
SHALL be the command it contributes through the entry-point group
`machinome.commands`, listed by `machinome -h` after the registry's commands
with its docstring as its help, declaring `needs_node = False`, with the verbs
`install`, `update` and `list` that the `skills-distribution` capability
specifies. Its dispatch SHALL import no registry command's module, and its
module SHALL import nothing at module scope beyond the standard library. In
the suite's environment, synced from the lock, the contract walk over the
group SHALL find the entry `skills` of `machinome-skills` and its class
meeting the contract of a contributed command.

#### Scenario: The skills command is listed

- **WHEN** `machinome-skills` is installed and a user runs `machinome -h`
- **THEN** `skills` is listed after `vet` with its docstring, and `machinome
  skills -h` lists `install`, `update` and `list`

#### Scenario: The skills command runs alone

- **WHEN** a user runs `machinome skills list`
- **THEN** the command's module and its installer are imported, no registry
  command's module is, and the command exits 0

#### Scenario: The suite walks a real contributor

- **WHEN** the suite runs on the workspace synced from the lock
- **THEN** the walk of the group finds `skills` contributed by
  `machinome-skills` alone, its class imports and constructs with no
  argument, carries a docstring, `add_arguments` and `handle`, and declares
  `needs_node` as a boolean
