## ADDED Requirements

### Requirement: The studio command loads none of the studio's application to be listed

Importing `machinome.studio.cli`, as `machinome -h` and every dispatch of
`machinome studio` do, SHALL NOT import a web framework, a server, a file
watcher or a TOML writer, nor any module of `machinome.studio` other than its
root and `machinome.studio.cli`: the package's root SHALL read each exported
name from its module on first use. Starting the studio SHALL import what it
runs when it runs.

#### Scenario: The help imports no application

- **WHEN** `machinome -h` or `machinome studio -h` runs in a fresh interpreter
  with `machinome-studio` installed
- **THEN** none of `fastapi`, `starlette`, `uvicorn`, `watchdog`, `tomlkit`,
  `machinome.studio.app` or `machinome.studio.orchestrator` is among the
  process's imported modules

#### Scenario: A name is read when it is used

- **WHEN** a caller runs `from machinome.studio import create_app`
- **THEN** the name is the application factory of `machinome.studio.app`,
  loaded with what that module imports
