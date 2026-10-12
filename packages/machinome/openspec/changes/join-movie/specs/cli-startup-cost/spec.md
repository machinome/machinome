## ADDED Requirements

### Requirement: The movie command loads none of the movie's evaluation to be listed

Importing `machinome.movie.cli`, as `machinome -h` and every dispatch of
`machinome movie` do, SHALL NOT import a JSON-schema library or a module of
`machinome.movie` other than its root and `machinome.movie.cli`: the
package's root SHALL read each exported name from its module on first use. A
verb SHALL import what it runs when it runs.

#### Scenario: The help imports no evaluation

- **WHEN** `machinome -h` or `machinome movie -h` runs in a fresh interpreter
  with `machinome-movie` installed
- **THEN** neither `jsonschema` nor `machinome.movie.document`,
  `machinome.movie.evaluate` or `machinome.movie.take` is among the process's
  imported modules

#### Scenario: A name is read when it is used

- **WHEN** a project's module runs `from machinome.movie import Movie, Take`
- **THEN** both names are the classes of their modules, and only the modules
  that define them and what those import are loaded
