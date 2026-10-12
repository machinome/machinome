## MODIFIED Requirements

### Requirement: A command loads only its own implementation

The system SHALL import the implementation module of exactly the command being
run. Importing `machinome.cli` SHALL NOT import any command implementation
module, nor `importlib.metadata`, and dispatching one command SHALL NOT import
another command's module, whether either is a registry command or a command an
installed package contributes (the `cli` capability, "An installed package may
contribute a command").

Dispatching a registry command SHALL NOT read the entry-point group
`machinome.commands`: it imports what it imported before contributed commands
existed. The group SHALL be read only when the first argument that is not an
option is not a registry command's name: for the help, a contributed command,
an unknown name and the migration guard's path.

The command names, the command-first grammar, and the pre-0.4 migration guard
SHALL be derived from the command registry, and where the group is read from
its entries' names, without importing any command implementation module,
because all three need only names.

An unknown command name SHALL be reported with an error that names the valid
commands, the contributed ones included, and exits nonzero, as it does today.

#### Scenario: Importing the CLI loads no command

- **WHEN** `machinome.cli` is imported in a fresh interpreter
- **THEN** no `machinome.manager.*` command implementation module, and not
  `importlib.metadata`, is present in `sys.modules`

#### Scenario: One command does not load another

- **WHEN** `machinome viewer` runs to completion
- **THEN** the process has imported the `viewer` command's module and has
  imported no other command's module

#### Scenario: The legacy grammar is still recognised

- **WHEN** a user runs `solid mynode.py develop`
- **THEN** the CLI exits with code 2 and prints the migration hint, without
  importing any command implementation module

#### Scenario: A framework command reads no entry point

- **WHEN** `machinome vet -h` runs in a fresh interpreter with a distribution
  contributing a command installed
- **THEN** `importlib.metadata` and that distribution's module are absent
  from the process's imported modules

#### Scenario: A contributed command loads no framework command

- **WHEN** a contributed command is dispatched in a fresh interpreter
- **THEN** its module is imported and no `machinome.manager.*` command
  implementation module is

### Requirement: Top-level help still describes every command

The system SHALL keep `machinome -h` and the no-subcommand invocation listing every
command with the help derived from that command's docstring, unchanged from
today, followed by every command an installed package contributes with the
help derived from its docstring. This is the one invocation whose output
depends on every command, and it alone MAY import every command module, the
contributed ones included.

#### Scenario: Help lists the full command set

- **WHEN** a user runs `machinome -h`
- **THEN** the command list includes `build`, `develop`, `test`, `snapshot`,
  `new`, `export`, and `viewer`, each with its docstring help, and after the
  registry's commands each command an installed package contributes

#### Scenario: Per-command help is complete

- **WHEN** a user runs `solid <command> -h` for any command
- **THEN** every option that command accepts is listed, as it is today
