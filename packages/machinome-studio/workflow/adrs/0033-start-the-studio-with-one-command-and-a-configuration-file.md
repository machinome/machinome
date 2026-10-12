# ADR 0033: Start the studio with one command and a configuration file

**Status:** Accepted

**Date:** 2026-09-26

**Deciders:** Pilot

**Origin:** `add-the-machinome-studio-command`

**Amends:** the project-folder boundary ratified by `context-isolation` and
stated in `scoped-agent-tools` ("Runtime location independence")

## Context

The studio is started with `python -m floor.orchestrator --projects-dir
PATH`, or `python -m floor` for the hub without agents. Both are module
paths inside the package, both require the project folder on every launch,
and the port is an option or `FLOOR_PORT`. The pilot, who starts the hub
daily, asked on 26 September 2026 for a `machinome-studio` command on `PATH`
once the studio is installed, reading a global configuration file with the
project folder and the port, both still accepted as options, and approved
the shape recorded here.

The project folder is a deliberate boundary. The `context-isolation` change
made `--projects-dir` the exact and sole catalogue: the studio never
derives it from its working directory, its installation or Git metadata,
so an installed studio can serve an arbitrary folder and never guesses one.
No earlier ADR records that boundary; the specs, the architecture overview
and `AGENTS.md` do. ADR 0027, amended by 0032, bounds ambient discovery of
`PATH` executables; it says nothing about configuration files.

## Decision

The package declares a console script, `machinome-studio`, bound to the
orchestrator's `main`. It is the hub with agents, with exactly the options,
defaults and failures of `python -m floor.orchestrator`. Both module entry
points remain.

A studio configuration file, TOML, lives at
`$XDG_CONFIG_HOME/machinome-studio/config.toml` when `XDG_CONFIG_HOME` is
absolute, else `$HOME/.config/machinome-studio/config.toml` when `HOME` is
absolute, the same rule on every platform; when neither is, there is no
default file. `MACHINOME_STUDIO_CONFIG` names another file. Its one
table, `[studio]`, accepts `projects` (an absolute path, or `~` or `~/...`
expanded against `HOME`; `~name` is refused) and `port` (1–65535). Nothing else: no `host`, since both entry points bind
loopback only and nobody needs otherwise; no keys for the hidden test
overrides; no runtime choices, which belong to each project's
`[tool.machinome-studio]` table.

Each setting is resolved once, first source winning: command-line option,
environment (`FLOOR_PORT`, port only), configuration file, built-in default
(port 9000; the project folder has none). One shared function performs the
resolution for all three ways of starting the hub, so `python -m floor`
reads the file too.

The project folder remains required. A folder written in the configuration
file is a declared value, supplied by the maker exactly as the option is,
and not discovery: the boundary becomes "the folder the caller supplies, by
option or by configuration file", still used exactly and still never
derived. A relative `projects` value is refused rather than resolved
against the working directory (which would reintroduce cwd derivation) or
the configuration directory (which is almost never meant). When neither
source supplies a folder, the studio refuses to start with `error:` and exit
1, naming the file it looked for or saying that no default location
exists; this replaces argparse's exit 2, since
omitting the option is no longer a malformed command line.

A missing configuration file is not an error. A present file that does not
parse, carries an unknown table or key, or holds a value of the wrong type
or range refuses startup, naming the file and the key, whether or not the
command line overrides that key; so does a file named by
`MACHINOME_STUDIO_CONFIG` that does not exist. A typo never silently falls
back to a default.

## Alternatives considered

- **A shell alias or wrapper script in the workspace.** Serves one machine
  and one checkout; the need is a command wherever the studio is installed.
- **A `--config` option.** No launch needs it; the environment variable
  serves tests and a second setup without widening the command line.
- **Defaulting the project folder** (to `~/machines`, the working directory,
  or a folder beside the installation). Rejected: it is the derivation the
  catalogue boundary forbids, and a hub opened on the wrong folder is worse
  than a refusal.
- **Ignoring unknown keys** for forward compatibility. Rejected: the file
  has two keys and one reader; an unknown key is far more likely a typo
  than a newer studio's setting.
- **A `host` key.** Rejected until someone needs the hub beyond loopback,
  which would be its own security decision.

## Consequences

- A maker writes the folder once and starts the hub with `machinome-studio`.
  An explicit option still wins, and the hub names its working folder on its
  first screen, so a stale file is visible.
- The catalogue boundary is restated in `scoped-agent-tools`, the
  architecture overview and `AGENTS.md` to admit the configuration file as a
  second declared source.
- A missing project folder exits 1 instead of 2. Anything that relied on the
  old status must change; the studio is unpublished and no such caller is
  known.
- The port is range-checked once, whatever its source: `FLOOR_PORT` used to
  raise a traceback when not numeric, and `--port 0` or `--port 70000` used
  to fail at bind time with a traceback; both now refuse with `error:` and
  exit 1.
- The workspace venv's editable install predates the entry point; after
  integration it is reinstalled from the primary checkout (`scripts/setup`)
  before `machinome-studio` appears on its `PATH`.
- The studio gains no dependency: the standard library's `tomllib` reads the
  file.
- The workspace's `running-the-shop` skill, outside this repository, still
  documents `python -m floor.orchestrator`, which keeps working.
