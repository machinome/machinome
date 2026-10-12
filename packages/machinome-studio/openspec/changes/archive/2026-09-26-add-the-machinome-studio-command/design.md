## Context

The studio has two entry points, `python -m floor.orchestrator` (the hub with
agents) and `python -m floor` (the same hub without agents). Each builds its
own argparse parser with `--projects-dir` marked `required=True` and
`--port` defaulting to `int(os.environ.get("FLOOR_PORT", "9000"))`, plus
hidden `--machinome-command` (both) and `--backend-command` (orchestrator)
overrides. A missing `--projects-dir` is an argparse usage error, exit 2.
Every other failed prerequisite (OpenSpec missing, preparation, profile,
runtime errors, `ValueError`) is printed as `error: ...` on stderr with exit
1. Both bind `127.0.0.1` only. `pyproject.toml` declares no console script.

The project-folder boundary is load-bearing. `scoped-agent-tools`
("Runtime location independence") ratifies the caller-supplied
`--projects-dir` as the exact and sole catalogue, never derived from cwd or
Git metadata; the architecture overview and `AGENTS.md` say the same
("comes only from the launcher's required `--projects-dir` option"). No ADR
records that boundary: it was ratified by the archived `context-isolation`
change. ADR 0027 bounds ambient `PATH` discovery to `openspec` (amended by
0032 for `codex`); a configuration file is not a `PATH` executable and does
not touch that bound.

The need, from the pilot on 26 September 2026: a `machinome-studio` command
on `PATH`, reading a global configuration file with the project folder and
the port, both still accepted as options. The pilot approved the shape this
design refines.

## Goals / Non-Goals

**Goals:**

- `machinome-studio` starts the hub with agents from any installed
  environment, with exactly the options and failures of
  `python -m floor.orchestrator`.
- The maker writes the project folder and port once, in one file, and can
  override either per launch.
- One resolution rule shared by all three ways of starting the hub.
- The project folder stays an explicit, declared value; a malformed file
  never silently becomes a default.

**Non-Goals:**

- No `host` key. Both entry points bind `127.0.0.1` only and nobody has
  asked to listen elsewhere; binding beyond loopback would be a security
  decision in its own right.
- No configuration keys for the hidden `--machinome-command` /
  `--backend-command` overrides, for profiles, backends or models (those
  belong to each project's `[tool.machinome-studio]` table), or for the
  Codex login store.
- No `--config` option. `MACHINOME_STUDIO_CONFIG` covers the one known use
  (tests, a second setup) without adding a launcher option.
- No second console script for the agent-less hub, and no subcommands:
  `python -m floor` and `python -m floor.codex_auth login` are unchanged.
- No command that writes or edits the configuration file.
- No change to how the project folder is used once resolved: exactly as
  given, possibly empty, anywhere on disk.
- No publication. The command exists wherever the studio is installed,
  which today means from a clone.

## Decisions

### D1. The console script is the orchestrator's `main`

`[project.scripts] machinome-studio = "floor.orchestrator:main"`. The
editable install `scripts/setup` performs generates
`.venv/bin/machinome-studio` once it is run against a `pyproject.toml` that
declares the entry, so the command is on `PATH` once the environment is
activated, with no setup change beyond its closing message. An existing
editable install predates the entry and must be reinstalled (see Migration
Plan).
argparse's program name follows `argv[0]`, so `machinome-studio --help`
names itself. Alternative considered: a new `floor/cli.py` wrapper — rejected,
it would be a third entry point with nothing of its own to do.

### D2. One shared resolution function, used by both entry points

A new module, `floor/launcher.py`, holds the configuration-file location,
the reader and `resolve_launch(arguments, environ) -> (projects_dir, port)`.
Each entry point keeps its own `add_argument` calls (so
`tests/test_documentation.py`'s option scan of `floor/__main__.py` and
`floor/orchestrator.py` keeps working unchanged), drops `required=True` from
`--projects-dir`, sets `--port`'s default to `None`, and calls
`resolve_launch` right after `parse_args()`, before the OpenSpec check.
Failures raise `LaunchError(ValueError)`: the orchestrator already turns
`ValueError` into `error: ...` and exit 1; `floor/__main__.py` gains the
same handling. The function takes the environment as a mapping and reads
every variable it uses from that mapping alone (`MACHINOME_STUDIO_CONFIG`,
`XDG_CONFIG_HOME`, `HOME`, `FLOOR_PORT`), including the home directory used
for `~` expansion, so tests never touch the real home directory.

`python -m floor` reads the configuration file too. It is the same hub over
the same folder, and a maker who runs it to inspect a build without agents
expects it on the folder they configured; a second rule would be the kind
of divergence the shared function exists to prevent.

### D3. Where the file is

1. `MACHINOME_STUDIO_CONFIG`, when set and not empty: that path, used as
   given (a relative value is relative to the working directory, like any
   path the maker types). It must exist.
2. Otherwise `$XDG_CONFIG_HOME/machinome-studio/config.toml` when
   `XDG_CONFIG_HOME` is an absolute path (the XDG rule; a relative value is
   ignored), else `$HOME/.config/machinome-studio/config.toml` when `HOME`
   is an absolute path. It may be absent.
3. When neither variable is an absolute path there is no default file; that
   is not an error, and the missing-folder refusal says that no default
   location exists instead of naming a path.

This mirrors the Codex login store's `XDG_STATE_HOME`/`HOME` rule in
`floor/codex_auth.py`. The rule is the same on every platform; the studio
is validated on Linux only.

### D4. Shape and validation

```toml
[studio]
projects = "~/machines"
port = 9000
```

Read with the standard library's `tomllib` (Python ≥ 3.11 is already
required; `tomlkit` stays the writer for project manifests). Validation is
strict because a typo that silently fell back to a default would start the
hub on the wrong folder or port:

- the top level accepts only the `studio` table; `studio` must be a table;
- `studio` accepts only `projects` and `port`;
- `port` is an integer from 1 to 65535 (a TOML boolean is refused even
  though Python's `bool` is an `int`);
- `projects` is a string. When it is exactly `~` or begins with `~/`, that
  `~` is replaced by the `HOME` value of the supplied environment mapping,
  which must be an absolute path (else the "home directory is unknown"
  refusal). `Path.expanduser()` is not used: it reads the process's real
  home and raises when it cannot find one. No other `~` form is expanded:
  `~name` (another user's home) falls under the relative-path refusal. The
  result must be absolute.

**Relative `projects` is refused**, not resolved against the file's
directory. The configuration file lives in a per-user configuration
directory, so a path relative to it would name a folder inside
`~/.config`, which is almost never meant; resolving against the working
directory would reintroduce exactly the cwd derivation the catalogue
boundary forbids. Refusal is reversible: a later need can admit a relative
form with a stated base. The command-line `--projects-dir` is unchanged and
still used as given.

The file is read and validated whenever it exists, even when the command
line supplies both settings: a broken file is reported the first time the
hub starts, not the first time the maker relies on it.

### D5. Precedence

Per setting, first source wins: option, environment, file, default.

| Setting | Option | Environment | File | Default |
|---|---|---|---|---|
| project folder | `--projects-dir` | — | `studio.projects` | none: refuse |
| port | `--port` | `FLOOR_PORT` | `studio.port` | `9000` |

There is no environment variable for the project folder; nobody needs one
and `--projects-dir` already serves scripts. `FLOOR_PORT` keeps its meaning
and gains the same 1–65535 validation as the file (today a non-numeric
value raises a traceback while the parser is being built). The `--port`
option keeps its argparse `int` type, so a non-integer is still argparse's
usage error, exit 2. The resolved port is range-checked once, whatever its
source, and refused with the text for the source that supplied it; today
`--port 0` or `--port 70000` passes parsing and fails at bind time with a
traceback.

### D6. Refusals and their exact texts

All are printed to standard error as `error: <text>`, exit status 1, before
the OpenSpec check, the registry or the listener. `<file>` is the path as
resolved (not `~`-abbreviated).

| Case | Text |
|---|---|
| No folder, default file location known | `no project folder: pass --projects-dir or set projects under [studio] in <file>` |
| No folder, no default location | `no project folder: pass --projects-dir (no configuration file: neither XDG_CONFIG_HOME nor HOME is an absolute path)` |
| Named file missing | `<file>: no such file (named by MACHINOME_STUDIO_CONFIG)` |
| File unreadable (either location) | `<file>: cannot be read: <strerror>` |
| Not TOML | `<file>: not valid TOML: <tomllib message>` |
| Unknown top-level key or table | `<file>: unknown key '<key>'; the file accepts [studio] with projects and port` |
| `studio` not a table | `<file>: studio must be a table` |
| Unknown key in `[studio]` | `<file>: unknown key 'studio.<key>'; [studio] accepts projects and port` |
| Bad port | `<file>: studio.port must be an integer from 1 to 65535` |
| `projects` not a string | `<file>: studio.projects must be a string` |
| `projects` relative, or a `~` form other than `~` and `~/...` (such as `~name`) | `<file>: studio.projects must be an absolute path, ~, or a path starting with ~/, got '<value>'` |
| `projects` is `~` or `~/...` and `HOME` is not an absolute path | `<file>: studio.projects starts with ~ but the home directory is unknown (HOME is not an absolute path)` |
| Bad `FLOOR_PORT` | `FLOOR_PORT must be an integer from 1 to 65535, got '<value>'` |
| `--port` an integer outside 1–65535 | `--port must be an integer from 1 to 65535, got <value>` |

A missing folder moves from argparse's exit 2 to exit 1. It is no longer a
malformed command line: the command line may legitimately omit
`--projects-dir` when the file supplies it, so its absence alone is not a
usage error. An unknown option is still argparse's exit 2, as the command
reference states.

### D7. Records the implementation must bring along

- ADR 0033 (drafted Proposed with this proposal) is accepted; the index and
  the architecture overview's "Project hub and sessions" paragraph ("Both
  entry points require `--projects-dir`") are rewritten to state the
  command, the file and the precedence.
- `AGENTS.md`, "Repository boundaries": "The catalogue path comes only from
  the launcher's required `--projects-dir` option" becomes "from the
  launcher's `--projects-dir` option or the studio configuration file's
  `projects` key; the studio never derives it".
- The workspace's `running-the-shop` skill lives outside this repository
  and keeps working with `python -m floor.orchestrator`; it is reported to
  the pilot, not edited.

## Risks / Trade-offs

- [A stale configuration file silently steers a launch] → Options always
  win, the hub names its working folder on its first screen (existing
  `shop-project-hub` behaviour), and the startup line prints the port.
- [Tests reading the developer's real configuration] → `resolve_launch`
  takes the environment explicitly. Every test that calls an entry point's
  `main()` in-process (`tests/test_floor_entrypoint.py` and the three in
  `tests/test_openspec_prerequisite.py`) patches `os.environ` with
  `clear=True`, keeping only the variables it needs (`PATH`, where it
  resolves or hides `openspec`) and adding a temporary `XDG_CONFIG_HOME`, so
  neither the developer's file nor their `FLOOR_PORT` is read; a test
  asserts the developer's file is never consulted under that patch.
  Known exposure, not patched: the subprocess-based tests
  (`tests/test_orchestrator.py`, `tests/test_floor_api.py`,
  `tests/test_shop_lifecycle_e2e.py`) pass `--projects-dir` and a port, so
  options win, but they still read the developer's real configuration file
  and would fail if it were malformed. That failure names the file, and the
  remedy is to fix the file.
- [The command is missing from the workspace environment after
  integration] → The workspace venv's editable install was generated from
  the primary checkout's `pyproject.toml` before the entry existed. After
  integration it must be reinstalled editable from the primary checkout
  (`scripts/setup` does this) before `machinome-studio` appears on its
  `PATH`. During the cycle nothing from the worktree is ever installed into
  that shared venv.
- [Scripts that relied on exit 2 for a missing `--projects-dir`] → Stated as
  breaking in the proposal and the changelog; the studio is unpublished and
  its only known caller is the pilot's own launch, which passes the option.
- [`python -m floor` users surprised by the file] → It resolves exactly as
  the orchestrator does and an explicit `--projects-dir` still wins.
- [The command shadows another `machinome-studio` on `PATH`] → Nothing else
  of that name exists in the ecosystem; the framework's command is
  `machinome`.

## Migration Plan

No data migration. Existing launches with `--projects-dir` behave
identically when no configuration file exists. After integration the
workspace venv is reinstalled editable from the primary checkout
(`scripts/setup`), which generates `.venv/bin/machinome-studio`; the pilot
may then write `~/.config/machinome-studio/config.toml` and start with
`machinome-studio`. Rollback is reverting the implementation commit; a
configuration file left behind is then ignored.

## Open Questions

None blocking. Whether the workspace's `running-the-shop` skill should
switch to `machinome-studio` is a workspace change for the pilot.
