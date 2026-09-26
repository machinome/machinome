## ADDED Requirements

### Requirement: The shop starts from an installed command
Installing the studio SHALL put a `machinome-studio` command on the `PATH`
of the environment it is installed into. Running it SHALL start the shop
exactly as `python -m floor.orchestrator` does, with the same options,
defaults and failures. `python -m floor.orchestrator` SHALL keep working,
and `python -m floor` SHALL keep serving the hub without agents; all three
SHALL resolve their project folder and port by the same rule.

#### Scenario: The maker starts the shop by name
- **WHEN** the maker runs `machinome-studio --projects-dir PATH` from an
  environment the studio is installed into
- **THEN** the shop reports its browser location on port 9000 with no
  project prepared, no model built and no agent running, as
  `python -m floor.orchestrator --projects-dir PATH` does

#### Scenario: The module entry points still start the shop
- **WHEN** the maker runs `python -m floor.orchestrator` or `python -m floor`
  with the same options and the same configuration file
- **THEN** each starts on the same project folder and port the
  `machinome-studio` command would use

### Requirement: A studio configuration file supplies the project folder and port
The shop SHALL read a studio configuration file, a TOML file at the path
`MACHINOME_STUDIO_CONFIG` names when that variable is set and not empty;
otherwise at `$XDG_CONFIG_HOME/machinome-studio/config.toml` when
`XDG_CONFIG_HOME` is an absolute path, else at
`$HOME/.config/machinome-studio/config.toml` when `HOME` is an absolute
path. When neither variable is an absolute path there SHALL be no default
file. The file SHALL accept one table, `[studio]`, with two keys:
`projects`, the project folder, and `port`, the local port. A `projects`
value that is `~` or begins with `~/` SHALL have that `~` expanded to the
maker's home directory, the value of the `HOME` environment variable, which
SHALL be an absolute path; no other `~` form SHALL be expanded, and the
result SHALL be an absolute path.

Each setting SHALL be resolved once, the first source that supplies it
winning: the command-line option (`--projects-dir`, `--port`), then the
environment (`FLOOR_PORT`, for the port only), then the configuration file,
then the built-in default. The port's default SHALL be 9000. The project
folder SHALL have no default: when neither the option nor the file supplies
it, the shop SHALL refuse to start, saying that `--projects-dir` or the
file's `projects` key is needed and naming the file it looked for, or, when
there is no default file, saying that no default location exists.

A missing configuration file at the default location SHALL NOT be an error.
A file that is present and malformed — not valid TOML, a table or key the
studio does not accept, a value of the wrong type, a port outside 1–65535,
or a `projects` value that is not an absolute path after `~` expansion —
SHALL refuse startup with a reason that names the file and the offending
key, whether or not the command line overrides that key. A file named by
`MACHINOME_STUDIO_CONFIG` that does not exist or cannot be read SHALL refuse
startup the same way. A `FLOOR_PORT` that is not an integer from 1 to 65535
SHALL refuse startup naming the variable. The resolved port SHALL be an
integer from 1 to 65535 whatever its source: a `--port` value outside that
range SHALL refuse startup naming the option.

A refusal under this requirement SHALL bind no listener and open no project,
and SHALL be reported on standard error prefixed `error:` with exit status
`1`, as a failed prerequisite is.

#### Scenario: The configuration file names the project folder and port
- **WHEN** the configuration file sets `projects = "~/machines"` and
  `port = 9100`, and the maker runs `machinome-studio` with no option and
  no `FLOOR_PORT`
- **THEN** the hub lists `machines` under the directory `HOME` names, and
  the shop reports its browser location on port 9100

#### Scenario: Options override the configuration file
- **WHEN** the configuration file sets `projects` and `port`, and the maker
  runs `machinome-studio --projects-dir OTHER --port 9200`
- **THEN** the hub lists `OTHER` and the shop listens on port 9200

#### Scenario: The environment overrides the file's port
- **WHEN** the configuration file sets `port = 9100`, `FLOOR_PORT` is `9300`,
  and no `--port` option is given
- **THEN** the shop listens on port 9300

#### Scenario: No configuration file exists
- **WHEN** no file exists at the default location and the maker runs
  `machinome-studio --projects-dir PATH`
- **THEN** the shop starts on `PATH` and port 9000 exactly as before the
  configuration file existed

#### Scenario: Nothing names the project folder
- **WHEN** the maker runs `machinome-studio` with no `--projects-dir` and no
  configuration file sets `projects`
- **THEN** startup fails with exit status 1 and an `error:` line naming
  `--projects-dir` and the `projects` key, and either naming the
  configuration file it looked for or saying that no default location
  exists; no listener is bound and no project is opened

#### Scenario: The configuration file is malformed
- **WHEN** the configuration file is not valid TOML, or has a table or key
  other than `[studio]`, `projects` and `port`, or gives `port` a value that
  is not an integer from 1 to 65535, or gives `projects` a value that is not
  a string naming an absolute path after `~` expansion
- **THEN** startup fails with exit status 1 and an `error:` line naming the
  file and what is wrong with it, even when the command line supplies every
  setting

#### Scenario: The port option is out of range
- **WHEN** the maker runs `machinome-studio --port 0` or
  `machinome-studio --port 70000`
- **THEN** startup fails with exit status 1 and an `error:` line naming
  `--port` and the accepted range, and no listener is bound

#### Scenario: Another configuration file is named
- **WHEN** `MACHINOME_STUDIO_CONFIG` names a file that sets `projects`
- **THEN** the shop reads that file instead of the default one and starts on
  the folder it names

#### Scenario: The named configuration file is missing
- **WHEN** `MACHINOME_STUDIO_CONFIG` names a path where no readable file
  exists
- **THEN** startup fails with exit status 1 and an `error:` line naming that
  path and the variable that named it
