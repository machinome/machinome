# Evidence: add-the-machinome-studio-command

## Red (task 1.5)

Run against the unchanged tree (`floor/launcher.py` temporarily removed, no
edits yet to `floor/orchestrator.py`, `floor/__main__.py`, `pyproject.toml`
or the manual), one test module at a time:

```
PYTHONPATH="$PWD" /home/asa/devel/machinome/.venv/bin/python -m pytest tests/test_launcher.py -q
```
```
ERROR collecting tests/test_launcher.py
ModuleNotFoundError: No module named 'floor.launcher'
1 error in 0.39s
```

```
PYTHONPATH="$PWD" /home/asa/devel/machinome/.venv/bin/python -m pytest tests/test_floor_entrypoint.py -q
```
```
FAILED tests/test_floor_entrypoint.py::FloorEntrypointTest::test_configuration_file_supplies_the_folder_and_port
FAILED tests/test_floor_entrypoint.py::FloorEntrypointTest::test_missing_projects_dir_with_no_file_exits_one
    AssertionError: 2 != 1   # argparse still exits 2 for a missing --projects-dir
FAILED tests/test_floor_entrypoint.py::FloorEntrypointTest::test_port_zero_exits_one_before_any_server_starts
    AssertionError: SystemExit not raised   # --port 0 is accepted and reaches uvicorn.run
FAILED tests/test_floor_entrypoint.py::FloorEntrypointTest::test_the_isolated_environment_never_reads_the_developers_own_file
    AssertionError: '/tmp/...' not found in "...error: the following arguments are required: --projects-dir\n"
FAILED tests/test_floor_entrypoint.py::OrchestratorEntrypointTest::test_missing_projects_dir_with_no_file_exits_one
    AssertionError: 2 != 1
FAILED tests/test_floor_entrypoint.py::OrchestratorEntrypointTest::test_port_zero_exits_one_before_any_server_starts
    TypeError: a coroutine was expected, got <MagicMock name='Server().serve()' ...>
    (orchestrator.main() proceeds past argument parsing straight into _serve,
    which builds the mocked uvicorn.Server before any launch-resolution check)
6 failed, 4 passed, 6 subtests passed in 1.97s
```

```
PYTHONPATH="$PWD" /home/asa/devel/machinome/.venv/bin/python -m pytest tests/test_openspec_prerequisite.py -q
```
```
6 passed in 0.84s
```
(Unchanged: the environment-isolation edits to this module only tighten what
each test's `main()` call is allowed to see; the unmodified entry points'
existing behaviour still satisfies the assertions.)

```
PYTHONPATH="$PWD" /home/asa/devel/machinome/.venv/bin/python -m pytest tests/test_packaging.py -q
```
```
FAILED tests/test_packaging.py::ConsoleScriptTest::test_machinome_studio_console_script_is_declared
    KeyError: 'scripts'
1 failed in 0.03s
```

```
PYTHONPATH="$PWD" /home/asa/devel/machinome/.venv/bin/python -m pytest tests/test_documentation.py -q
```
```
SUBFAILED(page='docs/opening-a-project.rst') ReferenceTest::test_pages_that_start_the_hub_show_the_command
SUBFAILED(needed='machinome-studio') ReferenceTest::test_the_configuration_file_is_documented
SUBFAILED(needed='MACHINOME_STUDIO_CONFIG') ReferenceTest::test_the_configuration_file_is_documented
SUBFAILED(needed='config.toml') ReferenceTest::test_the_configuration_file_is_documented
SUBFAILED(needed='[studio]') ReferenceTest::test_the_configuration_file_is_documented
FAILED ReferenceTest::test_the_configuration_file_is_documented
    FileNotFoundError: floor/launcher.py (reading STUDIO_KEYS)
6 failed, 22 passed, 213 subtests passed in 1.84s
```

`floor/launcher.py` was then restored and implementation proceeded.

## Green (task 4.1)

Static frontend built fresh in the worktree first:

```
npm --prefix floor/frontend install && npm --prefix floor/frontend run build
```
succeeded (763 modules transformed, `floor/static/` populated).

Whole suite:

```
PYTHONPATH="$PWD" /home/asa/devel/machinome/.venv/bin/python -m pytest tests -q
```
```
480 passed, 1 skipped, 1 warning, 399 subtests passed in 158.91s (0:02:38)
```
The one warning is a pre-existing, unrelated `PytestUnraisableExceptionWarning`
from an asyncio subprocess `__del__` racing interpreter shutdown in
`test_orchestrator.py::ClaudeBackendShutdownTest`; it was present in the
436-passed/1-skipped baseline run before this change and is not touched by
it. The one skip is also pre-existing.

Manual build, warning-free:

```
/home/asa/devel/machinome/.venv/bin/python -m sphinx -b html -n -W --keep-going docs docs/_build/html
```
```
build succeeded.
```
The changed pages (`reference/cli.html`, `opening-a-project.html`,
`installation.html`, `troubleshooting.html`) were read in the built HTML:
the `:ref:` cross-reference from the Options section to the Configuration
file section resolves correctly, the precedence table and refusal list
render, and the sibling pages' pointers to `machinome-studio` render as
plain text with no broken links.

### Real installed command (tasks 2.3 and 4.1)

A throwaway venv was created outside the repository
(`python -m venv` in the scratchpad), the studio installed into it with
`pip install --no-deps -e <worktree>`, and its declared dependencies
(`fastapi`, `tomlkit`, `uvicorn`, `watchdog`) installed directly into that
same venv (simpler than fighting `PYTHONPATH` against the workspace venv's
own editable install of the studio, which shadowed the worktree's package
when placed ahead of it on `sys.path`). Nothing was ever installed into
`/home/asa/devel/machinome/.venv`. The venv was deleted after this run.

`machinome-studio --help`:
```
usage: machinome-studio [-h] [--port PORT] [--projects-dir PROJECTS_DIR]

Run the event-driven agent shop

options:
  -h, --help            show this help message and exit
  --port PORT
  --projects-dir PROJECTS_DIR
                        exact directory containing project repositories
```
(`--projects-dir` is no longer marked required, and `argv[0]` names the
program `machinome-studio`, confirming D1.)

Start/stop on a temporary folder:
```
$ machinome-studio --projects-dir <tmp> --port 9321
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:9321 (Press CTRL+C to quit)
shop-floor open at http://127.0.0.1:9321
^C (SIGINT)
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [...]
$ echo $?
0
```

Configuration-file-driven start (no `--projects-dir`, no `--port`; a
`~/.config/machinome-studio/config.toml` under an isolated `HOME` with
`projects = "~/machines"` and `port = 9331`), confirmed against the
running hub's own `/api/entries`:
```
shop-floor open at http://127.0.0.1:9331
$ curl -s http://127.0.0.1:9331/api/entries
{"working_folder":"<HOME>/machines","folder":"","models":false,"entries":[]}
```
`working_folder` matches the `~/machines` the configuration file named,
expanded against the isolated `HOME`, and the port matches the file's
`port = 9331`, confirming the file supplies both settings on its own.

Each design-D6 refusal text observed once from the real installed command,
under an isolated environment (`env -i PATH=... [HOME=...] [XDG_CONFIG_HOME=...] [MACHINOME_STUDIO_CONFIG=...] [FLOOR_PORT=...] machinome-studio [options]`):

| Case | Observed text (file path elided) |
|---|---|
| No folder, default file location known | `error: no project folder: pass --projects-dir or set projects under [studio] in <file>` |
| No folder, no default location | `error: no project folder: pass --projects-dir (no configuration file: neither XDG_CONFIG_HOME nor HOME is an absolute path)` |
| Named file missing | `error: <file>: no such file (named by MACHINOME_STUDIO_CONFIG)` |
| Not TOML | `error: <file>: not valid TOML: Expected '=' after a key in a key/value pair (at line 1, column 6)` |
| Unknown top-level key | `error: <file>: unknown key 'host'; the file accepts [studio] with projects and port` |
| `studio` not a table | `error: <file>: studio must be a table` |
| Unknown key in `[studio]` | `error: <file>: unknown key 'studio.host'; [studio] accepts projects and port` |
| Bad port (file) | `error: <file>: studio.port must be an integer from 1 to 65535` |
| `projects` not a string | `error: <file>: studio.projects must be a string` |
| `projects` relative | `error: <file>: studio.projects must be an absolute path, ~, or a path starting with ~/, got 'relative/machines'` |
| `projects` is `~name` | `error: <file>: studio.projects must be an absolute path, ~, or a path starting with ~/, got '~name/machines'` |
| `~`/`~/...` and `HOME` not absolute | `error: <file>: studio.projects starts with ~ but the home directory is unknown (HOME is not an absolute path)` |
| Bad `FLOOR_PORT` | `error: FLOOR_PORT must be an integer from 1 to 65535, got 'not-a-number'` |
| `--port` out of range | `error: --port must be an integer from 1 to 65535, got 0` |

Every case exited `1`. The file-unreadable case (`<file>: cannot be read:
<strerror>`) is covered by `tests/test_launcher.py`'s
`MalformedFileTest.test_unreadable_file` (permission-based, exercised as
the unprivileged worktree user) rather than repeated here; the text
template is identical to the other file-based refusals.
