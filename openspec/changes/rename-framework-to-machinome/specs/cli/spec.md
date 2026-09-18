## ADDED Requirements

### Requirement: The command surface uses the framework identity

Every framework command SHALL be invoked through `machinome`. Command-first
grammar and the existing command set SHALL otherwise remain unchanged. Help,
errors, subprocess launches, templates and tests SHALL name `machinome`, and
worktree-specific runtime configuration SHALL use `MACHINOME_*` variables.

#### Scenario: A user asks for command help

- **WHEN** the user runs `machinome --help`
- **THEN** the existing framework commands are listed under the Machinome
  executable name

#### Scenario: A manager starts a child build

- **WHEN** a command delegates a build or test to a fresh interpreter
- **THEN** the child runs the Machinome module/command and receives the
  `MACHINOME_*` environment
