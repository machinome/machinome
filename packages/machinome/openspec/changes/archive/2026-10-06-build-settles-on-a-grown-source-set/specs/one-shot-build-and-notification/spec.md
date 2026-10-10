## MODIFIED Requirements

### Requirement: One-shot conventional node build

The system SHALL provide `machinome build [reference]`, using the same node
reference resolution and ordinary build pipeline as `machinome develop
[reference]`. It SHALL
produce the complete current model in the normal project build directory and
exit 0 without starting a watcher or viewer. Its exit status SHALL reflect
whether the model built. When its builder stands down because the source moved
while it waited for the project build lock, the command SHALL build again from
the source on disk rather than exiting, so what it publishes is the current
model. The order of the project's file timestamps SHALL NOT by itself make
its builder stand down: a project none of whose files change during the
command, such as a fresh clone or worktree, SHALL build as it would with
every file dated alike.

#### Scenario: Build the project model

- **WHEN** a user runs `machinome build` from a project whose manifest declares
  `[tool.machinome] model`
- **THEN** the command resolves that model, completes the ordinary model build
  in the project's normal build directory, and exits 0

#### Scenario: Build publishes beside a running watch loop

- **WHEN** a user runs `machinome build` while `machinome develop` is
  watching the same project
- **THEN** the two builds serialise on the project build lock and the command
  exits 0 for a model that built correctly

#### Scenario: The source moves while the build waits

- **WHEN** the project source is edited while `machinome build` is waiting for the
  project build lock
- **THEN** the command rebuilds from the edited source and exits 0 with the
  current model published

#### Scenario: A freshly checked-out project builds once

- **WHEN** a user runs `machinome build` in a project whose part reads a mesh
  file dated later than the module declaring the part, every file older than
  the command and none edited while it runs
- **THEN** the command builds the model with one builder, publishes it and
  exits 0
