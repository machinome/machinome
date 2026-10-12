## ADDED Requirements

### Requirement: An installed package may contribute a command

The system SHALL take its commands from two sources: the command registry of
the framework (`machinome.cli.COMMANDS`), and the entry-point group
`machinome.commands`, in which an installed distribution declares a command
as `name = "package.module:Class"`. The framework's own distribution SHALL
declare no entry in the group.

A contributed command's class SHALL meet the contract the registry's commands
meet: it is constructed with no argument; its docstring, not empty, is its
help; `add_arguments(parser)` registers its options on its subparser;
`handle(args)` runs it, its exit status set by `SystemExit` and 0 when it
returns; and it declares `needs_node` as `True` or `False`. A contributed
command declaring `needs_node = True` SHALL receive the shared `reference`
positional, `--set` and the refusal of a directory as a reference, as a
node-scoped registry command does.

`machinome -h` and the invocation with no command SHALL list every
contributed command after the registry's commands, in the order of their
names, each with its docstring as its help. `machinome <name> ...` for a
contributed name SHALL import that command's module and no registry command's
module, and run it with the arguments its parser accepts.

A contributed name equal to a registry command's SHALL NOT be used: the
registry's command runs, and every invocation that reads the group SHALL
write, for that entry, one line on standard error naming its distribution,
its location and the name, without changing standard output or the exit
status. A name contributed by two or more distributions SHALL run none of
them: invoking it SHALL write one line on standard error naming each
distribution and location, import none of their modules and exit 1. A
distribution found more than once on the path SHALL count once.

When a contributed command's module refuses for an absent extra
(`machinome.extras.ExtraUnavailable`), invoking it SHALL write `Error:
machinome <name> needs the <extra> extra: <refusal>` on standard error and
exit 1 before its arguments are parsed. When its class does not meet the
contract, invoking it SHALL write one line naming the command, its
distribution, its location and the first unmet term, and exit 1 before its
arguments are parsed. Any other failure to import or construct it SHALL
propagate, naming what could not be loaded. On the help path, each of these
cases and the name contributed by two distributions SHALL instead be listed
with a help that begins `(unavailable:` and gives the reason, and the help
SHALL exit 0, listing every other command as it would without it.

#### Scenario: A contributed command is listed

- **WHEN** a distribution declaring `movie` in `machinome.commands` is
  installed and a user runs `machinome -h`
- **THEN** the command list holds the registry's commands in their order,
  then `movie` with its docstring help, and the command exits 0

#### Scenario: A contributed command runs

- **WHEN** a user runs `machinome movie render film.yaml` with that
  distribution installed
- **THEN** the movie command's `handle` receives the verb `render` and the
  source `film.yaml`, its module is imported, and no registry command's
  module is imported

#### Scenario: A contributed command operates on a node

- **WHEN** a contributed command declares `needs_node = True` and a user runs
  it with a reference and `--set bore=3`, and again with a directory as its
  reference
- **THEN** its `handle` receives the reference and the override as a
  registry command's does, and the directory is refused naming the accepted
  spellings, with exit 2

#### Scenario: A contributed name is a framework command's

- **WHEN** an installed distribution declares `build` in `machinome.commands`
  and a user runs `machinome -h`, then `machinome build -h`
- **THEN** the help is the one printed without that distribution, with one
  line on standard error naming the distribution, its location and `build`;
  and `machinome build -h` prints the framework's `build` help, writes nothing
  on standard error and imports nothing of that distribution

#### Scenario: Two packages contribute one name

- **WHEN** two installed distributions each declare `movie` and a user runs
  `machinome movie list .`
- **THEN** nothing is printed on standard output, one line on standard error
  names both distributions and their locations, neither module is imported,
  and the command exits 1; and `machinome -h` lists `movie` once, as
  unavailable, naming both

#### Scenario: A contributed command lacks its extra

- **WHEN** a contributed command's module raises the `step` extra's refusal
  at its import and a user invokes the command
- **THEN** standard error holds `Error: machinome <name> needs the step
  extra: ` followed by the refusal, and the command exits 1; and `machinome
  -h` exits 0, listing the command as unavailable for that extra

#### Scenario: A contributed class does not meet the contract

- **WHEN** a contributed command's class has no docstring and a user invokes
  it
- **THEN** one line on standard error names the command, its distribution,
  its location and the missing docstring, and the command exits 1; and
  `machinome -h` lists it as unavailable with that reason

#### Scenario: A contributed module cannot be imported

- **WHEN** a contributed entry names a module that does not exist
- **THEN** `machinome -h` exits 0, listing the command as unavailable and
  naming the import error; and invoking the command fails with the import
  error naming the module

## MODIFIED Requirements

### Requirement: Command-first grammar with migration guard

The system SHALL parse `solid <command> <path> [options]` with one argparse
subparser per command, using each command's docstring as help. The command is
the first argument that does not begin with `-`; a later argument that spells
a command, as a contributed command's own verb or positional may, SHALL NOT
select that command. The command names are the registry's together with the
contributed commands' (requirement "An installed package may contribute a
command"). When invoked with the pre-0.4 path-first order (`argv[1]` not a
command name but `argv[2]` one, either read over those names), it SHALL exit
with code 2 and the message "The CLI grammar changed in 0.4: commands come
first. Try: solid {command} {path} [options]". With no subcommand it prints
help.

#### Scenario: Legacy grammar

- **WHEN** a user runs `solid mynode.py develop`
- **THEN** the CLI exits with code 2 and prints the migration hint

#### Scenario: Legacy grammar with a contributed command

- **WHEN** a distribution contributing `movie` is installed and a user runs
  `machinome film.yaml movie`
- **THEN** the CLI exits with code 2 and prints the migration hint

#### Scenario: A later argument spells a framework command

- **WHEN** a distribution contributing `movie` is installed and a user runs
  `machinome movie build film.yaml`
- **THEN** the movie command runs with the verb `build`, no migration hint is
  printed, and the framework's `build` command is not imported

### Requirement: A command that needs an extra is answered by the extra

The command registry SHALL be able to name, for a command, the one node type
of the table of supported node types (`machinome.node.supported`) that command
needs beyond its own implementation, whose module is `machinome.node.<type>`;
the registry and the command's implementation SHALL NOT spell that module
themselves. Dispatching
that command SHALL import that module first; when the module refuses because
its kernel cannot be found (the `kernel-extras` capability), the CLI SHALL
print one line on standard error naming the command and the install line the
refusal names, and exit 1, without running or parsing the command. The extra
SHALL be the one the module's refusal names, not a second copy kept in the
CLI.

The command SHALL stay registered and listed whether or not its extra is
installed: `machinome -h` SHALL list it with its docstring help and SHALL NOT
import the module it needs, and an invocation of it SHALL never be reported as
an unknown command. `import-step` is the one such command; its entry names
the node type `step`, whose module is `machinome.node.step`, and the table's
`step` entry lists `import-step` among the commands that need it. No
entry-point group SHALL be consulted to find or dispatch a registry command:
the registry's commands are found from the registry alone, and the commands of
other packages through the requirement "An installed package may contribute a
command".

#### Scenario: The command is listed without its extra

- **WHEN** `machinome -h` is run in an installation without the `step`
  extra's kernel
- **THEN** the command list includes `import-step` with its docstring help,
  the command exits 0, and `machinome.node.step` is not imported

#### Scenario: Dispatching a command imports the module it needs

- **WHEN** `machinome import-step FILE` is dispatched with the `step` extra
  installed
- **THEN** `machinome.node.step` is imported before the command runs, and the
  command behaves as the Import-step command requirement states

#### Scenario: A command needing no module imports none

- **WHEN** `machinome viewer` is dispatched
- **THEN** no leaf module under `machinome.node` is imported
