## ADDED Requirements

### Requirement: Movie command

When the distribution `machinome-movie` is installed, `machinome movie` SHALL
be the command it contributes through the entry-point group
`machinome.commands`, listed by `machinome -h` after the registry's commands
with its docstring as its help, declaring `needs_node = False`, with the verbs
`list`, `evaluate`, `watch`, `check`, `speech`, `preview`, `render`, `build`,
`live`, `review` and `setup` that the `movie-distribution` capability
specifies. Its dispatch SHALL import no registry command's module, and its
module SHALL import nothing at module scope beyond the standard library.
`python -m machinome.movie` SHALL run the same command. In the suite's
environment, synced from the lock, the contract walk over the group SHALL
find the entry `movie` of `machinome-movie` and its class meeting the contract
of a contributed command, and no fake distribution of the suite SHALL declare
the name of a package of the set.

#### Scenario: The movie command is listed

- **WHEN** `machinome-movie` is installed and a user runs `machinome -h`
- **THEN** `movie` is listed after the registry's commands with its docstring,
  and `machinome movie -h` lists the eleven verbs

#### Scenario: A verb's own argument spells a framework command

- **WHEN** a user runs `machinome movie build film.yaml`
- **THEN** the movie command runs its verb `build` on `film.yaml`, and the
  framework's `build` command is neither imported nor run

#### Scenario: The suite walks the real movie command

- **WHEN** the suite runs on the workspace synced from the lock
- **THEN** the walk of the group finds `movie` contributed by
  `machinome-movie` alone, its class imports and constructs with no argument,
  carries a docstring, `add_arguments` and `handle`, and declares
  `needs_node` as a boolean, and the seam's own tests pass beside it
