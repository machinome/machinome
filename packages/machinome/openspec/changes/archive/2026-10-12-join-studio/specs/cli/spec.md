## ADDED Requirements

### Requirement: Studio command

When the distribution `machinome-studio` is installed, `machinome studio`
SHALL be the command it contributes through the entry-point group
`machinome.commands`, listed by `machinome -h` after the registry's commands
with its docstring as its help, declaring `needs_node = False`, with the
options `--projects-dir PATH` and `--port PORT`. It SHALL start the studio's
project hub as the studio's launcher does: the project folder from the
option, else the studio configuration file's `projects` key; the port from
the option, else `FLOOR_PORT`, else the configuration file's `port` key, else
9000; listening on 127.0.0.1 only; refusing without the OpenSpec CLI on the
PATH; printing `shop-floor open at http://127.0.0.1:PORT` once the hub
listens and running until interrupted, opening no browser. A failed
prerequisite SHALL write one line beginning `error:` to standard error and
exit 1; an unknown option SHALL exit 2. Its dispatch SHALL import no registry
command's module. No console script `machinome-studio` and no module `floor`
SHALL be installed; `python -m machinome.studio.orchestrator` SHALL start the
same studio and `python -m machinome.studio` the same hub without agents. In
the suite's environment, synced from the lock, the contract walk over the
group SHALL find the entry `studio` of `machinome-studio` and its class
meeting the contract of a contributed command.

#### Scenario: The studio command is listed

- **WHEN** `machinome-studio` is installed and a user runs `machinome -h`
- **THEN** `studio` is listed among the contributed commands with its
  docstring, and `machinome studio -h` lists `--projects-dir` and `--port`

#### Scenario: The studio opens its hub

- **WHEN** a user runs `machinome studio --projects-dir PATH --port PORT` with
  the OpenSpec CLI on the PATH
- **THEN** it prints `shop-floor open at http://127.0.0.1:PORT`, the hub
  answers on that address listing the folder's projects, and no agent runs
  until a project is opened in the browser

#### Scenario: The studio command refuses without a project folder

- **WHEN** a user runs `machinome studio` with no `--projects-dir` and no
  configuration file naming one
- **THEN** it writes one line beginning `error:` to standard error and exits
  1

#### Scenario: The former launcher is gone

- **WHEN** a user runs `machinome-studio` or `python -m floor` in an
  environment where `machinome-studio` 0.8 or later is installed
- **THEN** the shell finds no such command and Python no such module, and
  `machinome studio` is the command

#### Scenario: The suite walks the studio's entry

- **WHEN** the suite runs on the workspace synced from the lock
- **THEN** the walk of the group finds `studio` contributed by
  `machinome-studio` alone, its class imports and constructs with no
  argument, carries a docstring, `add_arguments` and `handle`, and declares
  `needs_node` as a boolean
