## Why

The pilot, the studio's one daily maker, starts the hub with
`python -m floor.orchestrator --projects-dir PATH` every time: a module path
inside the package, typed from an activated environment, repeating the same
folder and port on every launch. On 26 September 2026 he asked for a
`machinome-studio` command on `PATH` once the studio is installed, reading a
global configuration file that holds the project folder and the port, with
both still accepted as options. He approved the design recorded here. What
he does with it: open the hub by typing `machinome-studio`, with his project
folder written once.

## What Changes

- Add a `machinome-studio` console script to the package. Installing the
  studio, editable or not, puts it on the environment's `PATH`; it starts
  the same service `python -m floor.orchestrator` starts, with the same
  options.
- Add a studio configuration file at
  `$XDG_CONFIG_HOME/machinome-studio/config.toml`, or
  `$HOME/.config/machinome-studio/config.toml` when `XDG_CONFIG_HOME` is not
  an absolute path; when neither variable is an absolute path there is no
  default file. Its one table, `[studio]`, accepts `projects` (the project
  folder, absolute, or `~` / `~/...` expanded against `HOME`) and `port`.
  `MACHINOME_STUDIO_CONFIG` names a different file.
- Resolve each setting once, highest first: the command-line option, the
  environment (`FLOOR_PORT` for the port), the configuration file, the
  built-in default (port 9000; the project folder has none).
- The project folder stays required: when neither `--projects-dir` nor the
  configuration file supplies it, the studio refuses to start, naming the
  file it looked for or saying that no default location exists. **BREAKING** for scripts that test the exit status: a
  missing project folder now exits `1` with an `error:` line, as a failed
  prerequisite, instead of argparse's usage error `2`. An unknown option
  still exits `2`.
- A missing configuration file is not an error. A file that is present but
  malformed (not TOML, an unknown table or key, a value of the wrong type,
  a relative project folder) is a failed prerequisite that names the file,
  whether or not options override its values. So is a file named by
  `MACHINOME_STUDIO_CONFIG` that does not exist. The resolved port is
  range-checked whatever its source, so `--port 0` now refuses cleanly
  instead of failing at bind time.
- `python -m floor.orchestrator` and `python -m floor` (the hub without
  agents) keep working and resolve their options through the same rule,
  configuration file included.
- The manual, the README, the changelog, the `floor` docstring and the
  setup script teach `machinome-studio`; the command reference documents the
  configuration file, its keys, its location and the precedence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-floor-lifecycle`: the shop is started by an installed command, and
  its project folder and port may come from a studio configuration file
  under a stated precedence; a malformed file refuses startup.
- `scoped-agent-tools`: runtime location independence names the project
  folder as the one the caller supplies, by option or by the configuration
  file, still used exactly and never derived from the working directory or
  Git metadata.
- `user-documentation`: the command reference documents the command, the
  configuration file and every key it accepts, and the documentation test
  refuses an undocumented key.

## Impact

- `pyproject.toml`: a `[project.scripts]` entry.
- `floor/orchestrator.py`, `floor/__main__.py`: option resolution moves into
  one shared function in a new small module; argparse no longer marks
  `--projects-dir` required. Reading uses the standard library's `tomllib`;
  no new dependency.
- Tests: `tests/test_floor_entrypoint.py` (the missing-folder case changes
  from exit 2 to exit 1); `tests/test_openspec_prerequisite.py`, whose
  in-process calls of the entry points must isolate the environment so the
  developer's own configuration file and `FLOOR_PORT` are never read; a new
  configuration test module; a packaging test that reads `pyproject.toml`;
  `tests/test_documentation.py`.
- Records: ADR 0033, the architecture overview's "Project hub and
  sessions", `AGENTS.md`'s repository-boundaries line that says the
  catalogue comes only from `--projects-dir`.
- Reader-facing: `docs/reference/cli.rst`, `docs/installation.rst`,
  `docs/opening-a-project.rst`, `docs/troubleshooting.rst`, `README.md`,
  `CHANGELOG.md` (`Unreleased`), the `floor` package docstring,
  `scripts/setup`'s closing message.
- Outside this repository, and not changed by this cycle: the workspace's
  `running-the-shop` skill still documents `python -m floor.orchestrator`,
  which keeps working. Updating it is a workspace change for the pilot to
  direct.
- Nothing is published: the command is on `PATH` wherever the studio is
  installed, which today means from a clone.
- Migration: the workspace venv's editable install was generated before the
  entry point existed. After integration it must be reinstalled editable
  from the primary checkout (`scripts/setup` does this) before
  `machinome-studio` appears on its `PATH`. During the cycle nothing from
  the worktree is installed into that venv; the installed command is
  exercised in a throwaway venv.
