# Evidence: `viewer-seam`

A cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` and `release-0.9.md` at the repository
root). Worktree `machinome/WTs/v0.9-joins-viewer-seam`, branch
`v0.9-joins-viewer-seam`, on the line `v0.9-joins` at 01981a3f (after
`release-tooling` and `join-studio`). Planning commit 1f0c1cb0, ratified by
the orchestrator on 12 October 2026 with every recommendation of its Open
Questions accepted, Decision 13 as a reversible working assumption flagged
to the pilot. Applied on 12 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), OpenSCAD 2021.01 under
`xvfb-run` (no `DISPLAY`), the OpenSpec CLI 1.6.0. Every command ran with
`env -C <dir>` and absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-viewer-seam`, `<scratch>`
is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C9-apply/`,
`<propose>` the proposer's `.../scratchpad/C9-propose/`. The core's tests
ran from `<bench>/packages/machinome` on the bench venv, one pytest process
at a time. Logs are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -3
1f0c1cb0 Propose viewer-seam: viewers are providers behind one seam, chosen by name
01981a3f Implement join-studio: the studio as the distribution machinome-studio, imported as machinome.studio, run as machinome studio
d291bc8b Join the studio: its whole history at its final paths
$ git -C <bench> status --short | wc -l
0
$ git -C <bench> ls-files | wc -l
6124
$ grep -n -- "--renderer" <bench>/packages/machinome-studio/machinome/studio/screenshots.py
95:                        "--renderer",
```

`join-studio` has landed: `P/screenshots.py` exists and spells `--renderer`.

### 1.2 The venv and the base suite (task 1.2)

The bench venv was synced from the lock by the orchestrator before the
planning commit (`<join>/uv-sync-2.log`, ending "exit 0"): 191 packages
(`uv pip list`), 17 `__editable__` `.pth` files (the core, the two engines,
the mechanics, the movie, nine node packages, the skills, the studio, the
viewer).

The base suite, from the line's latest archived evidence
(`2026-10-12-join-studio/evidence.md`, 14.2), not rerun: the core 4916
passed, 9 skipped; the mechanics 204 passed; the skills 47 passed; the viewer
252 passed, 2 skipped; the movie 322 passed; the studio 485 passed, 24
skipped.

### 1.3 The lint base (task 1.3)

```
$ env -C <bench> make lint 2>&1 | tail -3
tests/vet_projects/unresolved_import/sim/__init__.py:4:1: W391 blank line at end of file
tests/vet_projects/unresolved_reference/sim/__init__.py:4:1: W391 blank line at end of file
make: *** [Makefile:139: lint] Error 1
```

(`<scratch>/1.3-lint.out`.) flake8: 2549 lines, `join-studio`'s count;
black: 591 files would be reformatted, 200 left unchanged, 1 would fail (the
vet's planted `broken.py`).

### 1.4 The pixel and develop baselines (task 1.4)

A copy of `packages/machinome/docs/tutorial` at `<scratch>/tut-base` (its
`_build` removed), the three commands of `docs/tutorial/10-share.rst`
("Photograph") with the bench venv on the PATH:

```
$ env -C <scratch>/tut-base machinome snapshot -o <scratch>/base-counter.png --viewall --autocenter
$ env -C <scratch>/tut-base machinome snapshot --drive crank=3580 -o <scratch>/base-carry.png --viewall --autocenter
$ env -C <scratch>/tut-base machinome snapshot --renderer web --drive crank=3580 -o <scratch>/base-carry-web.png
```

Each exit 0, "Snapshot saved" (`<scratch>/base-snap-{1,2,3}.log`). SHA-256:

```
78e213ff31c895253589b184b7b5f3b5f161cf6cf2483e4577f5d21da9df339d  base-counter.png
2d4127a10a6b40df649cf155477b6e479f492f9c10a7042b120570736eebd480  base-carry.png
b46f77a49af602ae32e9a76f41fc315bdbab7bc155cd7e356e4a4c49083072f3  base-carry-web.png
```

The same three digests as the proposer's base images of probe 4. Looked at
(`<scratch>/base-montage.png`): the counter on its base with the crank; the
crank turned for the carry; the web image on a transparent background with
the drum's digits, which the OpenSCAD images do not draw.

The develop baseline: `Vibecoded-demos/gear-shift` at f3c79c2, its HEAD
extracted by `git archive` into `<scratch>/gs-base`; `<scratch>/probe_develop.py`
(the proposer's probe 11 script, its port read from `PROBE_PORT`, default
8781, and its final `pgrep` pattern spelt `machinome.viewer.web [s]erve`):
`machinome develop` in a new session under `MACHINOME_PORT=8781`, a
websocket client on `/ws/reload`, one source edit, the process group
interrupted:

```
$ <bench>/.venv/bin/python <scratch>/probe_develop.py <scratch>/gs-base <bench>/.venv/bin/machinome <scratch>/develop-base.log
server up 0.84 s; document v4 at 10.0 s; page b'<!DOCTYPE html>\n<!--\n  machinome-viewer '; greeting 'reload'; after a source change: 'ConnectionClosedError' in 0.7 s; 45 s later /_viewer 200; SIGINT exit 0 in 0.67 s; threads/children after: none
```

(`<scratch>/1.4-develop-base.txt`.) Today the open socket is closed when the
builder exits and the server process is restarted.

### 1.5 The sweep base (task 1.5)

The line's latest sweep, recorded in `2026-10-12-join-movie/evidence.md`
(14.3), not rerun: 63 repositories, 130 rows, 122 ok, 0 expected, 2
unexpected (wall clock 41 and fender-bender's), 0 timeout, 6 no-model.
`join-viewer` and `join-studio` ran none (their 11.6 and 14.6).

## 2. Red first

Every module below was run with `env -C <bench>/packages/machinome
<bench>/.venv/bin/python -m pytest -q -p no:cacheprovider tests/<module>`
before any line of the implementation existed (the viewer's and the movie's
from their directories), one process at a time; logs `<scratch>/2.*.out`.

### 2.1 `tests/test_viewer_seam.py`, new (task 2.1)

```
37 failed, 3 passed, 7 subtests passed in 1.60s     (<scratch>/2.1-red.out)
```

The red is not a collection failure, as the task foresaw, because the module
imports `machinome.viewer` inside its tests: at the base `machinome.viewer`
is the namespace package the viewer's distribution makes, holding `web`
alone, so each test fails on its first name: `AttributeError: module
'machinome.viewer' has no attribute 'viewer'` (and `chosen`, `ViewerLacks`,
`CONTRACT`), `FileNotFoundError` for `machinome/viewer/__init__.py` (the
path-extension and word tests), and the subprocess refusals reporting
`AttributeError` where `ExtraUnavailable` is expected. The three that pass at
the base: `test_the_seam_loads_no_viewer` (a namespace package imports
nothing), `test_the_rule_reads_each_former_name` (the scan's own rule) and
the parent of the contract-version test, whose two subtests fail.

### 2.2 `tests/test_snapshot.py` (task 2.2)

```
ERROR tests/test_snapshot.py
E   ImportError: cannot import name 'CaptureRequest' from 'machinome.viewer' (unknown location)
1 error in 0.42s                                     (<scratch>/2.2-red.out)
```

Red at collection, on the seam's names, where the task foresaw argparse's
`unrecognized arguments: --viewer`: the module now imports
`CaptureRequest`, `ViewerError` and `viewer` from the seam and
`OpenScadViewer` from `machinome.viewer.openscad`. What changed in it: the
OpenSCAD viewer's command, diagnostics and xvfb tests on `OpenScadViewer` and
`CaptureRequest`; every runner patch at `machinome.viewer.openscad.run`; the
loader stand-in sets `presented`; `assertLogs('viewer.openscad', ...)`; the
web viewer's unsupported options worded "the web viewer does not support"
and named together; `--viewer` with no argparse default and `--renderer`
parsed and hidden from the help; `SnapshotViewerFromTheSeamTest` in place of
`SnapshotRendererFromTheTableTest`: the help read from the seam, no table
read by the module, R4 with `--viewer`, the former flag refused (exit 2 and
its line), an unknown viewer, the web viewer absent, the project's viewer
taking the image, a failed capture withdrawing and writing one line, and the
web viewer composing no presentation.

### 2.3 The modules that move to the seam and the providers (task 2.3)

`git mv tests/test_browser_renderer.py tests/test_web_viewer_capture.py`
first. Runs (`-x` for the first four, which stop at collection):

```
test_web_viewer_capture:   1 error   ImportError: cannot import name 'CaptureRequest' from 'machinome.viewer'
test_openscad_dependency:  1 error   ImportError: cannot import name 'CaptureRequest' from 'machinome.viewer'
test_markings:             1 error   ImportError: cannot import name 'CaptureRequest' from 'machinome.viewer'
test_clocked_publication:  1 error   ImportError: cannot import name 'ViewerError' from 'machinome.viewer'
test_running_play:         1 error   ImportError: cannot import name 'ViewerError' from 'machinome.viewer'
test_scad_presentation:    9 failed, 17 passed (the snapshot runs on `--viewer`, the refusals' words, the
                           table's reach now empty, `viewers.absent` missing)
test_build_publication:    3 failed, 10 passed (`machinome.core.builder` has no attribute `viewers`;
                           `viewer` not in `machinome.viewer`)
test_openscad_node:        4 failed, 27 passed (no `machinome.viewer.openscad`: find_spec None,
                           ModuleNotFoundError where ExtraUnavailable is expected; renderer.py exists)
test_running_document:     1 failed, 109 passed (AttributeError: no attribute 'viewer')
test_profile_running_bound: 1 failed, 5 passed (AttributeError: no attribute 'viewer')
test_expression_type:      1 failed, 10 passed (`supported.py` still reaches the family's package)
```

`test_expression_type.py` is not in Decision 11's table; its constant
`BINARY_REACHES` named `supported.py` for the renderer column, so it becomes
the empty set with `ENGINE_REACHES` of `test_scad_presentation.py`.
`grep -rn "machinome.viewers\|node.openscad.renderer\|OpenScadRenderer\|BrowserRenderer"`
over the tests then lists `test_viewer_seam.py`'s own spellings, the absence
check of `test_openscad_node.py` (`find_spec('machinome.node.openscad.renderer')`
is None) and the modules of 2.5 to 2.7, which those groups rewrite.

### 2.4 `tests/test_manager_develop.py` (task 2.4)

Rewritten on a fake web provider at the seam (`viewers.viewer` patched for
`web`), with the session's `serve`, `reload` and `stop`; `--viewer`; `--web`
with another viewer an argument error (exit 2); the OpenSCAD viewer refused
by name; the project's viewer refused naming the key; `--web-dev`'s warning;
the builder handed the chosen name; no `Popen`; and `TakenPortTest`, a real
`machinome develop` in a scratch project with `MACHINOME_PORT` held by a
listening socket.

```
29 failed in 1.08s                                   (<scratch>/2.4-red.out)
28 x AttributeError: module 'machinome.viewer' has no attribute 'CONTRACT'
 1 x AssertionError: Lists differ: [] != ['Error: the web viewer cannot serve on port 54041: Address already in use']
```

The last is the brief's port test at the base: today's command starts the
server as a child, which fails on its own, and writes no such line.

### 2.5 `test_export.py`, `test_sphinx_ext.py`, `test_docs_exports.py` (task 2.5)

```
test_export:       11 failed, 19 passed   (6 x no attribute 'viewer'; 2 x core.export has no 'viewers';
                                           1 x Namespace has no 'viewer')
test_sphinx_ext:    4 failed, 10 passed   (no attribute 'viewer' / 'absent')
test_docs_exports: 10 failed, 12 passed   (sphinx has no 'viewers'; tools {'python'} != {python, nodejs};
                                           no pre_build job; docs target has no 'bundle'; no setup-node;
                                           runs ['make docs']; requirements name machinome-viewer;
                                           conf.py leaves the viewer's directory off its path)
```

`test_docs_exports.py` carries Decision 13's pins (group 9) as well as the
seam's patch, both red here.

### 2.6 `test_manager_viewer.py`, `test_viewer_report.py`, `test_cli_lazy_imports.py`, `test_machinome_identity.py` (task 2.6)

`git mv tests/test_viewer_bundle.py tests/test_viewer_report.py` first.

```
test_manager_viewer:     4 failed (no attribute 'viewer' / 'absent')
test_viewer_report:      1 error at collection (no attribute 'viewer')
test_cli_lazy_imports:   1 error at collection (cannot import name 'viewer' from 'machinome.viewer')
test_machinome_identity: 1 failed, 3 passed (no attribute 'viewer')
```

### 2.7 `test_supported_node_types.py`, `test_core_names_no_scad.py`, `test_core_kernel_free.py`, `test_vet_universe.py` (task 2.7)

```
test_supported_node_types: 4 failed, 11 passed (the column exists; the module defines DEFAULT_RENDERER
                           and renderer; the viewer door is a ModuleNotFoundError; the snapshot's line
                           says --renderer)
test_core_names_no_scad:   2 subtests failed (the zones `machinome-viewer-openscad` and
                           `machinome/viewer/__init__.py` do not exist)
test_core_kernel_free:     4 subtests failed (supported.py names machinome.node.openscad; the OpenSCAD
                           viewer's module and the seam do not exist)
test_vet_universe:         2 failed (the denylist names machinome.viewers and machinome.viewer.web;
                           the seam passes vet)
```

### 2.8 `test_repository_layout.py`, `test_kernel_extras.py`, `test_release_records.py` (task 2.8)

```
test_repository_layout: 6 failed (no packages/machinome-viewer-openscad; renderer.py in the node
                        package; machinome/viewer/ absent in the core)
test_kernel_extras:     7 failed (no viewer-openscad extra; openscad and solid2 without the viewer;
                        no manifest; the lock has no machinome-viewer-openscad)
test_release_records:   1 failed (no .bumpversion.cfg table for the new member)
```

The Makefile's `PACKAGES` test is green at the base, the directory not yet
existing; it turns red when 5.1 makes it (recorded there).

### 2.9 The viewer's and the movie's tests (task 2.9)

From `packages/machinome-viewer`: `tests/test_machinome_identity.py` asserts
no entry point and the provider's declarations; `tests/test_session.py`,
new: a live session's server listening when `serve` returns, a `reload`
reaching two open sockets twice without closing them, `stop` joining the
thread and freeing the port, and the brief's taken port refused by `serve`
within a second, naming the port, with no thread left.

```
test_machinome_identity: 2 failed, 5 passed ('entry-points' found; no attribute 'viewer')
test_session:            5 failed (no attribute 'serve' on the web package; no 'ViewerError')
test_bundle:             11 passed (unchanged)
```

From `packages/machinome-movie`, `tests/test_command.py` with its bootstrap
patching the seam's web provider:

```
8 failed, 9 passed                                   (<scratch>/2.9-movie.out)
AttributeError: module 'machinome.viewer' has no attribute 'viewer'
```

### 2.10 The manual's tests (task 2.10)

`tests/test_viewer_documentation_links.py` gains the scan of current pages
for the former flag (a paragraph spelling `--renderer` must say it is
refused; the changelog's `Unreleased` section and the upgrading page's 0.9
section are the current parts of those two records), the 0.9 upgrading
section, the tutorial's `--viewer web`, the how-to section "Choose the viewer
of a still", `--viewer` in the reference of `snapshot`, `develop` and
`export`, and the installation page's new extra and distribution.

```
8 failed, 8 passed      (five pages offend: concepts/publishing.rst 2 paragraphs, howto/markings.rst 1,
                         howto/share-an-export.rst 1, reference/cli.rst 3, tutorial/10-share.rst 1)
```

`tests/test_docs_structure.py`: the movie's test "no page spelling
`--viewer`" (`test_no_page_shows_the_videomaker_s_former_command_lines`)
would meet the seam's own flag on the snapshot, develop and export pages. It
is narrowed, as the brief directs, to the films' pages and to lines of a
film's command (`machinome movie`, `videomaker`), and is green at the base so
narrowed (a departure from `join-movie`'s test, recorded here); the
installation page's distributions gain `machinome-viewer-openscad`:

```
1 failed, 31 passed     (machinome-viewer-openscad not on the installation page)
```

### 2.11 What is green at the base and stays so

Every other module of the core's suite, the viewer's and the movie's other
modules, and in the modules above every test not listed as failing. The
suite's count at the end (11.1) accounts for each test added and removed.

## 3. The seam

### 3.1 and 3.2 `machinome/viewer/__init__.py` and the manifest key (tasks 3.1, 3.2)

The seam as Decision 1 states it, its last line the path extension under the
engine package's comment; `machinome/manifest.py` gains `Declaration.viewer`,
validated by `read_declaration` (a non-string value is a
`ProjectManifestError` naming `[tool.machinome] viewer`), `declared_viewer`
(the nearest project's value, or None where no project is found) and
`reference_origin` (the file a command's reference names, where the
project's manifest is looked for). The seam imports `machinome.manifest`
inside `chosen` only, so its module level imports the standard library and
`machinome.extras` alone. Beside Decision 1's names the seam has
`resolve(operation, needed_by, explicit, origin)`, the rule and `require` in
one call, so a project's viewer that lacks the operation is refused naming
the key and the flag (Decision 2's sentence), and `KEY`.

```
$ pytest tests/test_viewer_seam.py -rA
13 failed, 19 passed, 15 subtests passed in 1.54s      (<scratch>/3.1-seam.out)
```

Green: the contract's names, the Protocols, `CaptureRequest`, the default
rule over scratch manifests, the non-string key, an unknown name, a provider
of contract 2 and of none, the absent web and OpenSCAD viewers, the path
extension (a portion admitted, a second core copy refused) and the seam
loading no provider. Red, as the task expects, what needs the providers
(no `CONTRACT` on the web viewer, no OpenSCAD viewer) and what group 7
removes.

### 3.3 The path extension's red, once (task 3.3)

```
$ sed -i 's/^__path__ = .../# &/' machinome/viewer/__init__.py
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome.viewer.web"
ModuleNotFoundError: No module named 'machinome.viewer.web'        exit 1
$ (the saved file copied back)
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome.viewer.web; print(machinome.viewer.web.__file__)"
<bench>/packages/machinome-viewer/machinome/viewer/web/__init__.py  exit 0
$ cmp machinome/viewer/__init__.py <scratch>/seam.saved
(identical)
```

## 4. The web provider

### 4.1 and 4.2 `stage.py`, the operations, `session.py` (tasks 4.1, 4.2)

`git mv packages/machinome/machinome/viewers/browser.py
packages/machinome-viewer/machinome/viewer/web/stage.py`, then module
functions `stage`, `_stage`, `refuse_unreadable`, `artifact_path` and
`remove_stage`, the core's modules imported inside them, every refusal a
`ViewerError`; the unreadable refusal is the seam's `unreadable(version,
'web')` sentence followed by today's words with `--viewer openscad`, the
second viewer's name read from the seam's `EXTRAS` (the viewer's package is
not a zone of the SCAD scan, so it may not spell it).

`machinome/viewer/web/__init__.py`: `CONTRACT`, `NAME`, `OPERATIONS`,
`CAPTURE_OPTIONS`, `identity`, `document_versions`, `readable`, `describe`,
`files`, `present`, `withdraw`, `capture` (in the caller's process, the
camera resolved by `machinome.core.camera`, a `CaptureError` becoming a
`ViewerError`) and `serve`; the standard library only at module level.
`session.py`, new: the server's thread `machinome-viewer-web`, on a port the
session binds before the thread starts, so a held port is refused at once
("the web viewer cannot serve on port N: Address already in use"), the
brief's finding from `viewer-command`'s probes; the thread's own
`asyncio.run`, so the process's event loop policy is left alone (uvloop is
installed and uvicorn's `run` would set it process-wide); `reload` sends
`reload` on the open sockets on the server's loop; `stop` sets
`should_exit` and joins. `server.py` records its open reload sockets and
gains `broadcast`; `machinome-viewer serve` still runs `WebViewer.start()`
in the foreground. Messages and docstrings say viewer (`capture.py`'s
`PLAYWRIGHT_REMEDY` is "Install the browser viewer's capture with ...", the
root refusal "The web viewer cannot run as root ..."), `cli.py`'s and
`__main__.py`'s docstrings say the framework runs none of them, and the
compatibility comment on `--start-frontend` names a machinome released
before the seam.

A finding the design did not foresee: importing a submodule binds it as an
attribute of its package, and the provider's operation `capture` has the
name of its submodule `capture.py`. The first import of
`machinome.viewer.web.capture` (the operation's own, the CLI's, a test's
`patch('machinome.viewer.web.capture.Capture')`) replaced the operation by
the module, so the seam would find a module where it calls a function. The
package therefore sets its module's class to a `ModuleType` subclass that
does not bind a submodule over an operation of the same name; the submodule
stays in `sys.modules`, where `importlib.import_module` and `from
machinome.viewer.web.capture import ...` find it. The viewer's
`tests/test_capture.py` reads the module by `importlib.import_module` in
place of `from machinome.viewer.web import capture`, and
`tests/test_machinome_identity.py` pins the operation (see "Departures").

```
$ env -C /tmp <bench>/.venv/bin/python -X importtime -c "import machinome.viewer as v; print(v.viewer('web').readable(13))"
True
(<scratch>/4.2-importtime.out: machinome.viewer, machinome.extras, the viewer's bundle and currency;
 0 lines naming fastapi, uvicorn, playwright, or the viewer's server, capture, stage or session)
```

### 4.3 The entry point removed (task 4.3)

The viewer's manifest loses `[project.entry-points."machinome.viewer"]` and
its comment; its dependency comment says it is the web provider of the seam.

```
$ env -C <bench> uv sync --python 3.12          exit 0 (machinome-viewer reinstalled)
$ env -C /tmp <bench>/.venv/bin/python -c "from importlib.metadata import entry_points; print(list(entry_points(group='machinome.viewer')))"
[]
```

### 4.4 The viewer's suite and the core's web-viewer modules (task 4.4)

```
$ env -C <bench>/packages/machinome-viewer python -m pytest -q -rs
259 passed, 2 skipped, 63 warnings, 186 subtests passed in 257.68s   (<scratch>/4.4-viewer.out)
```

252 at the base and 2 skipped (the Curta's own builds absent), plus the
five of `test_session.py` and the two new identity tests.

```
$ pytest tests/test_web_viewer_capture.py tests/test_clocked_publication.py tests/test_running_play.py tests/test_running_document.py
9 failed, 144 passed, 1 skipped                      (<scratch>/4.4-core.out)
```

Every failure goes through a caller of group 6 (the snapshot command, the
exporter, the builder).

## 5. The OpenSCAD provider, its distribution and the extras

### 5.1 The move (task 5.1)

```
$ git mv packages/machinome-node-openscad/machinome/node/openscad/renderer.py packages/machinome-viewer-openscad/machinome/viewer/openscad/__init__.py
$ git diff --cached -M --stat
 .../machinome/viewer/openscad/__init__.py} | 0
```

Then Decision 4's edits: the module docstring, `OpenScadViewer`, the logger
`viewer.openscad`, `binary.require_openscad('the OpenSCAD viewer', ...,
'use --viewer web')`, the former `render` as `capture`, raising `ViewerError`
with today's words (the import OpenSCAD could not open, the partial image
removed; "OpenSCAD rendering failed:\n<stderr>"; "OpenSCAD not found in
PATH. ..."; the binary contract's refusal; the xvfb sentence, now raised by
`wrap_command` rather than exiting), and the module-level declarations and
operations, `capture` reading the module's `run` when called so a test
patches `machinome.viewer.openscad.run`.

### 5.2 to 5.4 The manifest, the README, the links, the node package, the extras, the lock (tasks 5.2 to 5.4)

The manifest and the README of Decision 4 verbatim; `LICENSE ->
../../LICENSE` and `LICENSES -> ../../LICENSES`, `git add`ed. The OpenSCAD
node package's `__init__` docstring, `binary.py`'s docstring, its README and
its description ("The OpenSCAD node family of Machinome and its SCAD
writer"). The core's `openscad`, `viewer-openscad` and `solid2` blocks of
Decision 5 verbatim; the `viewer` comment says the viewer is reached through
the seam. The root's sources line.

```
$ env -C <bench> uv lock
Resolved 201 packages in 601ms
Added machinome-viewer-openscad v0.8.1
(200 [[package]] entries before, 201 after; 38 diff lines, <scratch>/5.4-lock.diff)
$ env -C <bench> uv sync --python 3.12          exit 0
 + machinome-viewer-openscad==0.8.1 (editable)
(192 packages by `uv pip list`, one more than 1.2's 191; 18 __editable__ .pth files, one more than 17)
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome.viewer as v; print(v.__path__); ..."
['<bench>/packages/machinome/machinome/viewer', '<bench>/packages/machinome-viewer/machinome/viewer', '<bench>/packages/machinome-viewer-openscad/machinome/viewer']
<bench>/packages/machinome-viewer-openscad/machinome/viewer/openscad/__init__.py
<bench>/packages/machinome-viewer/machinome/viewer/web/__init__.py
('machinome-viewer-openscad', '0.8.1')
```

(`<scratch>/5.4-paths.out`.) The proposer's probe 13 counted 198 to 199 on
the line before `join-studio`; the lock now holds the studio's packages.

### 5.5 (task 5.5)

```
$ pytest tests/test_viewer_seam.py tests/test_kernel_extras.py tests/test_openscad_node.py tests/test_openscad_dependency.py tests/test_core_names_no_scad.py tests/test_core_kernel_free.py
6 failed, 107 passed, 183 subtests passed            (<scratch>/5.5.out)
```

The six: the core still holding `machinome/viewers/` and the renderer
column (group 7), the word test (the callers, group 6), and the snapshot's
substitution test (group 6).

## 6. The callers

### 6.1 `machinome snapshot` (task 6.1)

`machinome/manager/snapshot.py` as Decision 6 states it: `--viewer NAME`
(help from the seam's names and default), `--renderer` a suppressed option
spelt once (`RENAMED`) and refused first, exit 2; the viewer chosen and
required to capture before anything is loaded, an `ExtraUnavailable`
answered with Decision 6's line, any other refusal one `Error:` line; the
options the viewer does not honour refused together; one
`project_build_lock(build_dir)` for load, `--drive`, keyframe and `present`,
the build directory `abspath(get_build_dir(reference))`; `capture` after the
lock, `withdraw` in a `finally`; no table of node types, no `'web'`, no
`run`. The OpenSCAD and web viewers are both reached only through the seam.

```
$ pytest tests/test_snapshot.py
109 passed, 5 subtests passed                        (<scratch>/6.1-snapshot.out)
```

Two of the tests written in 2.2 were wrong and are corrected here: the
module test asserted that "supported" is not in the source, which the
message "does not support" never met but "unsupported" does, and now asserts
`node.supported` and `NODE_TYPES` absent; and the web viewer's integration
test asserted no `.scad` under the whole build directory, where the two
cylinder leaves write their own `.scad` for their STLs, and now asserts the
root's alone, as before. The project-viewer test needed its `demo.py` to
exist for `reference_origin` to find the project.

### 6.2 `machinome develop` and the builder (task 6.2)

`develop.py` as Decision 7 states it: `--viewer`; `--web` the explicit
spelling of the web viewer, an argument error with `--viewer` naming
another; `--no-web` resolving none (and, beyond the design, an argument
error with `--viewer`, which it would ignore); the viewer resolved by the
seam's rule with its `describe()` before any child, each refusal one line;
the session started before the builders (and before `--debug-builder`'s
in-process build, as the server process was); `session.reload()` where the
loop restarted the server; `session.stop()` on Ctrl-C and on a failed first
build; `--web-dev`'s warning; the chosen name handed to `run_builder` and
`Builder(viewer=...)`; no `Popen`, no `web_viewer_command`. The builder's
readability warning asks `unreadable(version, name)`, the name given, else
`chosen('serve')` for the project of the builder's reference.

```
$ pytest tests/test_manager_develop.py tests/test_build_publication.py
42 passed, 2 subtests passed                         (<scratch>/6.2.out)
```

`TakenPortTest` among them: a real `machinome develop` in a scratch project
with `MACHINOME_PORT` held by a listening socket exits 1 with the one line
`Error: the web viewer cannot serve on port <port>: Address already in use`,
publishes nothing, and returns in under 30 seconds; the viewer's own
`TakenPortTest` (4.4) has `serve` raise within a second.

### 6.3 `machinome export`, the exporter, the Sphinx extension, the manual's configuration, `machinome viewer` (task 6.3)

`core/export.py`: `embedder(name)` requires the viewer to embed and asks its
report, an absent viewer or a missing or stale bundle being
`WidgetBundleMissing` with the viewer's words and "Or pass --no-widget to
export only the manifest and models."; `export_node(..., viewer=None)`
resolves it before anything is written and copies `files()`; the
readability warning asks `unreadable(version, name)`. `manager/export.py`:
`--viewer NAME`, resolved by the seam's rule before the node is loaded, one
`Error:` line for a refusal; `--no-widget` refuses on no viewer.
`sphinx.py` and `docs/conf.py`'s `copy_the_embedding_example` ask
`require('web', 'embed', ...)`. `manager/viewer.py` prints the web viewer's
`describe()`, every refusal on standard error.

```
test_export:           30 passed            (<scratch>/6.3-test_export.out)
test_sphinx_ext:       14 passed
test_manager_viewer:    4 passed
test_viewer_report:    12 passed
test_cli_lazy_imports: 24 passed
test_docs_exports:      7 failed, 15 passed (group 9's pins, below)
```

Two test corrections here: `test_no_widget_resolves_no_viewer` asserted that
no viewer is even asked, but the readability warning asks the viewer whether
it reads the version under `--no-widget` as it did at the base (the warning
tests of `RunningPublicationWarningTest` export with `widget=False`); it is
`test_no_widget_refuses_no_viewer` now, an absent viewer and a viewer that
does not embed refusing nothing. And the help-fidelity test of
`test_cli_lazy_imports.py` read every option string, the suppressed
`--renderer` among them; `option_strings` now skips an option whose help is
`argparse.SUPPRESS`.

### 6.4 The films (task 6.4)

`installed_viewer(verb)` asks `require('web', 'embed', f'machinome movie
{verb}')`, its `describe()` and `files()['machinome-viewer.js']`; the
refusal's shape unchanged.

```
$ env -C <bench>/packages/machinome-movie python -m pytest -q
322 passed in 38.09s                                 (<scratch>/6.4-movie.out)
```

### 6.5 The studio (task 6.5)

Red first: the studio's `tests/test_screenshots.py` (two tests) and
`tests/test_project_preparation.py` (the call log) spelling `--viewer`:

```
$ env -C <bench>/packages/machinome-studio python -m pytest -q tests/test_screenshots.py tests/test_project_preparation.py
3 failed, 43 passed, 1 skipped                       (<scratch>/6.5-studio-red.out)
```

Then `P/screenshots.py` passes `--viewer web`; the shop skills say `--viewer`
(`machinome/SKILL.md` one sentence; `machinome-api/SKILL.md` four places,
the synopsis gaining `[--viewer web]` on `export` and `develop`, and one
sentence naming the project key and the refused flag); the fake's and the
test's "Install the browser renderer" are "Install the browser viewer's
capture", the viewer's new words. The studio's record is untouched.

```
$ env -C <bench> make test PKG=machinome-studio
485 passed, 24 skipped, 3 warnings in 110.24s        (<scratch>/6.5-studio.out)
```

## 7. What goes, and vet

### 7.1 (task 7.1)

```
$ git rm packages/machinome/machinome/viewers/__init__.py packages/machinome/machinome/viewers/bundle.py
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome.viewers"
ModuleNotFoundError: No module named 'machinome.viewers'          exit 1
```

`machinome/node/supported.py` without the `renderers` field, the row's
pair, `DEFAULT_RENDERER`, `renderer()` and the provisional paragraph.

### 7.2 and 7.3 (tasks 7.2, 7.3)

`universe.toml` denies `machinome.viewer`, with its comment, in place of
`machinome.viewers` and `machinome.viewer.web`.

```
test_vet_universe:          18 passed
test_viewer_seam:           32 passed, 41 subtests passed
test_supported_node_types:  14 passed, 63 subtests passed
test_core_names_no_scad:     6 passed, 20 subtests passed
test_core_kernel_free:      11 passed, 35 subtests passed
```

The plant:

```
$ echo "# planted: machinome snapshot --renderer web" >> machinome/manager/develop.py
$ pytest tests/test_viewer_seam.py -k test_the_word_is_viewer
E  AssertionError: {'packages/machinome/machinome/manager/develop.py': 1} != {}
1 failed
$ (the saved file copied back; cmp: identical)
$ pytest tests/test_viewer_seam.py -k test_the_word_is_viewer
1 passed
```

The viewer's widget test `src/version.test.ts` named `machinome snapshot
--renderer web` in a comment; it says `--viewer web` now.

## 8. The set's tooling

### 8.1 (task 8.1)

The Makefile's `PACKAGES` gains `machinome-viewer-openscad` last (sorted);
`.bumpversion.cfg` its two tables after the viewer's `docs/conf.py` table.
The Makefile list's red, shown once with the line taken out again:

```
test_repository_layout (without the line): 4 failed (the package list against the directories; the
                       README row and the guide's line, which 10.4 writes)
test_repository_layout: 2 failed, 55 passed (the README row and CONTRIBUTING.rst's line, 10.4)
test_release_records:   19 passed
test_kernel_extras:     19 passed
```

### 8.2 The bump on a copy (task 8.2)

The root's `.bumpversion.cfg` and the 24 files it names copied to
`<scratch>/bump`, made a git repository, then:

```
$ bump2version --no-commit --no-tag --new-version 0.9.0 patch      exit 0
25 files changed, 71 insertions(+), 71 deletions(-)   (<scratch>/8.2-bump-stat.txt)
```

`packages/machinome-viewer-openscad/pyproject.toml`: its version and its two
pins move to 0.9.0; the core's manifest moves the three new
`machinome-viewer-openscad~=` pins with its others; no `0.8.1` is left in
the copy. Nothing was written in the bench.

### 8.3 `scripts/check-dist` (task 8.3)

```
$ env -C <bench> python scripts/check-dist
check-dist failed: machinome-viewer-openscad has no smoke in scripts/check-dist
Nothing uploaded.                                        exit 1
```

Then the rows: the viewer's (no entry point in the distribution, the
provider the seam resolves for `web` its `__init__.py` with the seam's
contract and the four operations, ten modules with `session.py` and
`stage.py`, its report read from the provider); the OpenSCAD node package's
(`renderer.py` and the `supported.renderer` lines gone); and the new
`machinome-viewer-openscad`, through `viewer-openscad`, from a template of
its own (`OPENSCAD_VIEWER`): one shipped module owned by its distribution in
the venv, its version and two pins, `CONTRACT` and `OPERATIONS`, and
`machinome snapshot` of a one-part `OpenScadNode` project drawing a PNG
where `openscad` and a display or `xvfb-run` are there, else `present` and
`withdraw`; its licence lines.

```
$ flake8 --max-line-length=89 scripts/check-dist
(nothing)                                                exit 0
```

### 8.4 `make check` (task 8.4)

The new files `git add`ed first, so the clean copy of the tracked files
holds them.

```
$ env -C <bench> make check
Members: (18) machinome, ..., machinome-viewer, machinome-viewer-openscad
machinome-node-openscad 0.8.1 module .../machinome/node/openscad/__init__.py volume 24.0 through OpenSCAD
machinome-viewer 0.8.1 module .../machinome/viewer/web/__init__.py contract 1 operations ['capture', 'embed', 'present', 'serve'] API 29 documents 1 to 13
machinome-viewer-openscad 0.8.1 module .../machinome/viewer/openscad/__init__.py contract 1 operations ['capture', 'present'] a still 892 bytes through OpenSCAD
Every distribution built, checked, installed and smoked; nothing uploaded.
(the same three lines and the same last line from the clean copy)
exit 0                                                   (<scratch>/8.4-check.out)
```

18 members each run, one more than `join-studio`'s 17; `twine check
--strict` 72 PASSED lines over the two runs. The new member's archives,
built apart into `<scratch>/wheel-vo`: the wheel holds
`machinome/viewer/openscad/__init__.py` and its dist-info (8 entries, the
three licence files among them), the sdist 19 entries. `git status` after
the run: the tracked changes of this cycle and nothing else; the build
scratch is ignored.

## 9. The manual's build

Decision 13, accepted by the orchestrator on 12 October 2026 as a reversible
working assumption flagged to the pilot, so this group was not gated.

### 9.1 (task 9.1)

`docs/conf.py`'s path line puts every `packages/machinome-*` directory on the
path, the viewer's among them; `docs/requirements.txt` names `sphinx` and
`sphinx_rtd_theme` (a comment says the repository's viewer completes the
exports); `.readthedocs.yaml` gains `build.tools.nodejs: "22"` and one
`pre_build` job, `npm ci --no-audit --no-fund` and `npm run build --workspace
packages/machinome-viewer/machinome/viewer/web/widget`; the Makefile's `docs`
target depends on `bundle`; the CI docs job installs Node 22
(`actions/setup-node@v4`, the npm cache on `package-lock.json`, as the test
job) and runs `make widget` before `make docs`.

The CI step is a departure from the task's wording: `make docs` depends on
`bundle`, which runs the widget's build and needs the workspace's
`node_modules`, and `release-tooling`'s rule (the layout test's
`TheContinuousIntegrationTest`) lets a job spell no `npm` but call the
Makefile's targets. The job therefore runs `make widget` (`npm ci` from the
root's lock and every member's build) then `make docs`, and the layout
test's `CALLS['docs']` and `test_docs_exports.py`'s pin say `['make widget',
'make docs']`. The `user-documentation` delta's "install Node and run `make
docs`" and the `release-tooling` delta hold as written.

```
$ pytest tests/test_docs_exports.py
22 passed, 15 subtests passed                        (<scratch>/9.1.out; red in 2.5)
```

### 9.2 `make docs` (task 9.2)

```
$ env -C <bench> make docs
npm run build --workspace packages/machinome-viewer/machinome/viewer/web/widget
  dist/machinome-viewer.js  895.9kb
test -x .docs-venv/bin/python || uv venv --python 3.12 .docs-venv
...
build succeeded.                     exit 0, 13.19 s wall, 0 WARNING lines   (<scratch>/9.2-docs.out)
```

The six tutorial exports under `_build/html/_machinome/` each hold
`machinome-viewer.js`, and `howto/embed-the-viewer/` holds the guide's copy
(7 copies of the bundle in the build). Then with the bundle moved aside, the
same Sphinx run from `.docs-venv`:

```
$ env -C <bench>/packages/machinome <bench>/.docs-venv/bin/python -m sphinx -b html -W -E docs <scratch>/docs-nobundle
WARNING: machinome: Viewer bundle not found at <bench>/packages/machinome-viewer/machinome/viewer/web/widget/dist/machinome-viewer.js. A release of machinome-viewer from PyPI carries it; a source checkout builds it with: cd .../widget && npm ci && npm run build.
exit 2                                               (<scratch>/9.2-nobundle.out)
$ env -C <bench> make widget                          exit 0 (<scratch>/9.2-widget.out)
```

The remedy is the viewer's own wording from `join-viewer` (`npm ci` in the
widget's directory, where in the workspace it runs at the root); not changed
here. `.docs-venv/` is ignored by the root's `.gitignore`; the bench's
`node_modules` is a directory of its own, not a link.

## 10. The records

### 10.1 and 10.2 (tasks 10.1, 10.2)

`HISTORY.rst` and `docs/project/changelog.rst`: one `Unreleased` bullet each
("Viewers are PROVIDERS behind one seam, chosen by name", "Choose the viewer
by name"). `docs/project/upgrading.rst` begins "Upgrading from Machinome 0.8 to
0.9" (label `upgrading-0-8-to-0-9`) above the 0.8.0 to 0.8.1 section, with
"The viewer flag": `--renderer` is `--viewer`, the project's key, the
`viewer-openscad` extra, and `machinome viewer` in place of the entry point.

### 10.3 The pages (task 10.3)

`reference/cli.rst` (`develop`: `--viewer`, the in-process session,
`--web-dev`'s warning, `--no-web` with `--viewer`; `snapshot`: `--viewer` in
place of `--renderer`, the refusal stated, "OpenSCAD viewer only";
`export`: `--viewer`, `--no-widget` asking none), `tutorial/10-share.rst`,
`howto/share-an-export.rst` (the framework's still through the seam, and the
new section "Choose the viewer of a still", label `choose-the-viewer`: the
two viewers, their options, the project key, the refusals),
`howto/markings.rst`, `concepts/publishing.rst`, `start/install.rst` (the
`openscad` row, a `viewer-openscad` row, the `solid2` row, the distribution
list, the seam sentence), `reference/viewer/cli.rst` (the report paragraph
and the reload route), `reference/viewer/index.rst`, and the films'
`reference/movie/command.rst`. `reference/viewer/mount.rst` and
`layouts.rst` name no capture process: their "renderer" is three.js's, left
as it is, with the films' renderer and the markings' z-fighting sentence.

```
$ grep -rn -- "--renderer" <bench>/packages/machinome/docs (rst only)
reference/cli.rst:240         the refusal: "``--renderer`` is refused, exit status 2, naming ``--viewer``."
project/upgrading.rst:14,15   the 0.9 section's refusal
project/upgrading.rst:194     the released 0.7 to 0.8 section
project/changelog.rst:99      the Unreleased bullet's refusal
project/changelog.rst:209, 357, 588, 1184   released sections
$ pytest tests/test_viewer_documentation_links.py tests/test_docs_structure.py tests/test_release_records.py tests/test_profile_documentation.py
16 passed / 31 passed, 6187 subtests / 19 passed, 193 subtests / 2 passed
```

### 10.4 (task 10.4)

`docs/architecture.md`: the node model's paragraph (the renderer column as
history), the CLI's `machinome viewer` sentence and its snapshot paragraph,
the Viewers section rewritten around the seam and its two providers, the
in-process session, the staging, the document-versions paragraph, the
films' sentence, and the Map (the OpenSCAD node family row without
`renderer.py`, a row for the OpenSCAD viewer, the viewers row naming the
seam, `stage.py` and `session.py`, ADR-194). The root `README.md` gains the
`machinome-viewer-openscad` row and loses "the OpenSCAD snapshot renderer"
from the node package's; `CONTRIBUTING.rst` installs `-e
packages/machinome-viewer-openscad`; `context7.json` names `--viewer`, the
OpenSCAD viewer's distribution and extras, the refused flag, the project key
and the seam in place of the entry point.

```
$ pytest tests/test_repository_layout.py tests/test_release_records.py
55 passed, 472 subtests passed / 19 passed, 193 subtests passed
```

### 10.5 ADR-194 (task 10.5)

`docs/adrs/BUILD/ADR-194-viewers-are-providers-behind-one-seam-chosen-by-name.md`,
Status Proposed, as Decision 16 outlines it; its links resolve. Status lines:
ADR-068 (the lookup and the process boundary superseded by 194), ADR-179
(the renderer column removed, with an amendment section of 12 October 2026),
ADR-183 (a portion of the seam of viewers), ADR-188 ("The seam is unchanged"
and its vet sentence superseded, with a dated note), ADR-191 (the viewer
through the seam, with a dated note). `docs/adrs/README.md`: ADR-194's line
after ADR-193's, and the five index lines amended.

### 10.6 The viewer's record (task 10.6)

The viewer's `README.md` (`--viewer web`, the server `machinome develop`
serves through), `CHANGELOG.md` `Unreleased` (one bullet), and its specs
brought current in place: `viewer-distribution` (the lookup requirement now
"A framework finds the installed viewer at its address", the provider's
declarations and no entry point; "Everything else is a process" now the
provider's operations in the framework's process, the package importing the
core only inside the operations that stage a still; every "entry point"
read as the provider's report), `development-server` (the session, `reload`
on open connections, the taken port), `snapshot-capture` (its Purpose and
Code lines). Its decision log `workflow/adrs/README.md` gains a dated note
naming framework ADR-194; no record is rewritten. The OpenSCAD node package's
README was edited in 5.3.

```
$ env -C <bench>/packages/machinome-viewer python -m pytest -q tests/test_documentation.py tests/test_machinome_identity.py tests/test_licence.py tests/test_version.py
30 passed, 166 subtests passed                       (<scratch>/10.6-viewer-docs.out)
```

## 11. Validation

### 11.1 The suite (task 11.1)

No other bench's suite ran (`pgrep -af "WTs/v0.9-joins-.*[p]ytest"`: none).

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -rs -p no:cacheprovider
2 failed, 4984 passed, 9 skipped, 55 warnings in 800.81s           (<scratch>/11.1-suite.out)
```

The two failures were this change's:

- `test_openscad_dependency.py::test_snapshot_does_not_substitute_the_web_viewer`:
  the snapshot now withdraws what the viewer presented, and the test's
  `Mock` node had no `kept_artifacts`; the mock gains it (`basepath`,
  `kept_artifacts=()`), as the other OpenSCAD tests' mocks have.
- `test_scad_presentation.py::WithoutTheEngineTest::test_the_openscad_viewer_is_refused_before_loading`
  (the subtest hiding `machinome.node.openscad` by a finder placed first on
  `sys.meta_path`): the provider's `from machinome.node.openscad import ...`
  met that finder's plain `ModuleNotFoundError` before the node root's last
  finder could word it, so the seam propagated it. The OpenSCAD viewer now
  loads its node package through the table's `supported.load('openscad')`
  first, which words a missing node package as the node type's refusal
  however the import system reports it, as the table's renderer column did
  (`renderer()` loaded the node type first). In an installation without the
  node package both forms give the same line; see "Departures".

```
$ pytest tests/test_openscad_dependency.py tests/test_scad_presentation.py tests/test_viewer_seam.py tests/test_core_kernel_free.py tests/test_core_names_no_scad.py tests/test_openscad_node.py tests/test_supported_node_types.py tests/test_snapshot.py
239 passed, 197 subtests passed                      (<scratch>/11.1-fix.out)
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -rs -p no:cacheprovider
4985 passed, 9 skipped, 55 warnings in 822.02s (0:13:42)            (<scratch>/11.1-suite-2.out)
```

Against the base's 4916 passed and 9 skipped (1.2): 69 tests more, the
nine skips the base's (four FreeCAD, the opt-in web capture, networkx, the
jscad CLI, two vendor STEP files). Per module, by collected items:
`test_viewer_seam.py` +32 (new); `test_viewer_report.py` 12 in place of
`test_viewer_bundle.py`'s 16 (-4); `test_web_viewer_capture.py` 23 in place
of `test_browser_renderer.py`'s 25 (-2: the two argv tests of a capture
command the framework no longer builds); `test_manager_develop.py` +11;
`test_snapshot.py` +8; `test_viewer_documentation_links.py` +9 (seven
functions, one parametrized three ways); `test_export.py` +5;
`test_docs_exports.py` +3; `test_cli_lazy_imports.py`,
`test_core_names_no_scad.py`, `test_kernel_extras.py`,
`test_manager_viewer.py`, `test_openscad_node.py`, `test_release_records.py`
and `test_sphinx_ext.py` +1 each: 32 - 4 - 2 + 11 + 8 + 9 + 5 + 3 + 7 = 69.

### 11.2 The other suites and the lint (task 11.2)

```
$ env -C <bench>/packages/machinome-viewer python -m pytest -q
259 passed, 2 skipped, 63 warnings, 188 subtests passed              (<scratch>/11.2-viewer.out)
$ env -C <bench>/packages/machinome-movie python -m pytest -q
322 passed                                                           (<scratch>/11.2-movie.out)
$ env -C <bench> make test PKG=machinome-studio
485 passed, 24 skipped                                               (<scratch>/6.5-studio.out)
$ env -C <bench> make lint
flake8: 2539 lines, against 1.3's 2549, and no line that was not at the base
black: 594 files would be reformatted, 198 unchanged, 1 would fail (the vet's planted `broken.py`)
                                                                     (<scratch>/11.2-lint.out)
```

The new flake8 lines this change first wrote (`binary.py`'s docstring, an
E302 in `supported.py`, an E402 in `test_clocked_publication.py`, an E501 in
`test_supported_node_types.py`'s docstring, an unused import in
`test_web_viewer_capture.py`) were corrected; ten base lines went with the
code that held them. black's list differs only by the moved and new files
(the repository is not black-formatted; CI's lint step continues on error).

### 11.3 The originating check, part one: the pixels (task 11.3)

A fresh copy of `docs/tutorial` at `<scratch>/tut-new`, the bench venv on
the PATH:

```
$ machinome snapshot -o <scratch>/new-counter.png --viewall --autocenter                                  exit 0
$ machinome snapshot --drive crank=3580 -o <scratch>/new-carry.png --viewall --autocenter                exit 0
$ machinome snapshot --viewer openscad --drive crank=3580 -o <scratch>/new-carry-explicit.png --viewall --autocenter   exit 0
$ strace -f -e trace=execve -o <scratch>/11.3-strace-web.txt machinome snapshot --viewer web --drive crank=3580 -o <scratch>/new-carry-web.png   exit 0
78e213ff31c895253589b184b7b5f3b5f161cf6cf2483e4577f5d21da9df339d  new-counter.png
2d4127a10a6b40df649cf155477b6e479f492f9c10a7042b120570736eebd480  new-carry.png
2d4127a10a6b40df649cf155477b6e479f492f9c10a7042b120570736eebd480  new-carry-explicit.png
b46f77a49af602ae32e9a76f41fc315bdbab7bc155cd7e356e4a4c49083072f3  new-carry-web.png
base-counter vs new-counter: (1920, 1080) RGBA, 0 differing pixels of 2073600
base-carry vs new-carry: (1920, 1080) RGBA, 0 differing pixels of 2073600
base-carry vs new-carry-explicit: (1920, 1080) RGBA, 0 differing pixels of 2073600
base-carry-web vs new-carry-web: (1920, 1080) RGBA, 0 differing pixels of 2073600
                                                                     (<scratch>/11.3-pixels.txt)
```

Byte-identical to 1.4's images. Under `strace` the web still executed
`machinome`, Playwright's driver and Chromium's headless shell (8 `execve`
lines) and no `python -m machinome.viewer.web` (0 lines naming it). The
images were looked at (`<scratch>/new-montage.png`): the counter on its base
with the crank, the crank turned for the carry, the explicit OpenSCAD image
the default's, the web image transparent with the drum's digits.

```
$ machinome snapshot --renderer web --drive crank=3580 -o <scratch>/new-renamed.png
Error: machinome snapshot --renderer is --viewer since Machinome 0.9: write --viewer web
exit 2, no image
```

A copy of the tutorial whose manifest adds `viewer = "web"` under
`[tool.machinome]` (`<scratch>/tut-manifest`): `machinome snapshot --drive
crank=3580 -o <scratch>/new-manifest-web.png`, no flag, exit 0, SHA-256
`b46f77a4...`, the web image, byte-identical to the base's.

### 11.4 The originating check, part two: develop (task 11.4)

`Vibecoded-demos/gear-shift` at f3c79c2, its HEAD extracted again into
`<scratch>/gs-new`, the probe of 1.4 under `PROBE_PORT=8782`:

```
server up 0.74 s; document v4 at 10.9 s; page b'<!DOCTYPE html>\n<!--\n  machinome-viewer '; greeting 'reload'; after a source change: 'reload' in 0.6 s; 45 s later /_viewer 200; SIGINT exit 0 in 0.72 s; threads/children after: none
$ pgrep -af "machinome.viewer.web [s]erve"      (nothing)
$ pgrep -af "[m]achinome develop"              (nothing)
```

(`<scratch>/11.4-develop.txt`, `<scratch>/develop-new.log`.) Where the base
closed the open socket on the rebuild (`ConnectionClosedError` at 0.7 s),
the socket now receives `reload` and stays open; the log reads "Reloading the
viewer" and one server's startup and shutdown. The builder child's
`KeyboardInterrupt` traceback on the group's SIGINT is printed at the base
too (`<scratch>/develop-base.log`).

## Departures from the design and the brief

1. The seam has `resolve(operation, needed_by, explicit, origin)` and `KEY`
   beside Decision 1's names, so a project's viewer lacking an operation is
   refused with Decision 2's wording; `machinome.manifest` gains
   `Declaration.viewer`, `declared_viewer` and `reference_origin` (the file
   a reference names, where the project's manifest is looked for).
2. `capture` collides with the web package's submodule `capture.py`: the
   package's module class keeps a submodule from being bound over an
   operation of the same name (4.1); the viewer's `test_capture.py` reads
   the module by `importlib.import_module`. A rename of the submodule would
   avoid the guard; it was not made because Decision 10 lists `capture.py`
   among the ten shipped modules.
3. The session binds its port before starting the server's thread, and runs
   the server's own `asyncio.run` rather than `uvicorn.Server.run`, which
   would set uvloop's event-loop policy for the whole develop process.
4. `--no-web` with `--viewer` is an argument error, beyond Decision 7.
5. The OpenSCAD viewer loads its node package through `supported.load`
   first (11.1), so it imports the table of node types; Decision 4 had it
   import the writer and binary alone.
6. The CI docs job runs `make widget` before `make docs` (9.1); the layout
   test's `CALLS['docs']` changes with it.
7. The movie's docs test is narrowed to the films' pages and the films'
   command lines (2.10), as the brief directs.
8. Tests outside Decision 11's table changed: `test_expression_type.py`
   (`BINARY_REACHES` empty), `test_repository_layout.py`'s CI calls, the
   help-fidelity helper of `test_cli_lazy_imports.py` (suppressed options
   skipped), and three of this change's own tests corrected after their red
   (6.1, 6.3).
9. The suite's 4985 is the base's 4916 plus 69; the projects' move, the
   universe sweep, the archive, ADR-194's acceptance, the specs' sync and
   the plan entry are not done here (the checkpoint).

## The checkpoint

Reported to the orchestrator; reviewed on 12 October 2026, the departures
recorded above standing (the module-class guard, `supported.load` in the
OpenSCAD viewer, `make widget` before `make docs` in CI's docs job, the
narrowed films' docs test). The orchestrator's own run on the bench, ended
21:58: `make test PKG=machinome` 4985 passed, 9 skipped; `make test
PKG=machinome-viewer` 259 passed, 2 skipped; `make docs` exit 0; `make
check` exit 0, 36 archives on the tree and 36 on the clean copy, after the
last edits of group 11.

## The projects' move and the sweep (Decision 12; the orchestrator's)

12 October 2026: the workspace's `scripts/rewrite-projects` with a table
`viewer-seam.toml` (one `[[text]]` rule, `--renderer` to `--viewer` in
`*.md` and `*.rst`, archived changes, evidence and logs excluded), run over
a scratch catalogue of links to the catalogue's top-level entries (its
self-referencing link `machinome-projects` left out): 63 repositories
walked, 19 changed, 28 files, 0 skipped for uncommitted changes, one commit
per repository on its checked-out branch, "Photograph with --viewer, the
viewer seam's flag" (3DPrintedClocks 60b81ab, dragon-r1 40e9651, openarm
031434a among them). Recorded evidence untouched. The table goes into the
workspace's `scripts/rewrite-projects.d/` by the `workspace-consistency`
cycle.

The universe sweep after the move, on this bench's venv: 63 repositories,
130 rows, 122 ok, 0 expected, 2 unexpected (wall clock 41 and
fender-bender's, as before), 0 timeout, 6 no-model; identical to the movie
cycle's sweep (1.5) row for row by project, model and outcome. Leonardo's
rows carry a new checkout label, its branch having been switched in the
pilot's own session between the two sweeps.

## 12. The archive

### Before the archive: the deltas against the head

`framework-identity` and `release-tooling` re-derived against the bench's
baseline specs (after `release-tooling` and `join-studio` landed), each
modified requirement compared with the baseline's of the same title
(`<scratch>/12.0-rederive.txt`): the requirements "Extras select independent
Machinome products", "The framework is the package directory
`packages/machinome` of a monorepo" and "The workspace, the bundles, the
lint and the manual have a target each" differ from the baseline only by
this change's sentences and scenarios; `join-studio`'s text is carried.

### 12.1 ADR-194 (task 12.1)

Status Accepted, its change link the archive's; its index line in
`docs/adrs/README.md` "**Accepted**, supersedes 068's lookup and process
boundary and 188's seam, amends 179/183/191, cites 103/162/176".
`docs/architecture.md` checked against it: the Viewers section, the CLI
paragraph, the node model's paragraph and the Map's rows agree with the
decision outcome.

### 12.2 and 12.3 The sync and the archive (tasks 12.2, 12.3)

```
$ env -C <bench>/packages/machinome openspec archive viewer-seam -y
Specs to update:
  backend-neutral-materialization, build-pipeline, cli, cli-startup-cost,
  framework-identity, kernel-extras, movie-distribution, openscad-dependency,
  openscad-node, release-tooling, user-documentation, vet,
  viewer-distribution: update
  viewer-seam: create
  web-snapshot: update
Totals: + 8, ~ 32, - 2, → 0
Specs updated successfully.
Change 'viewer-seam' archived as '2026-10-12-viewer-seam'.
```

(`<scratch>/12.3-archive.out`; its task count, 53 of 57, counted group 12
before this section ticked it; its proposal warnings are non-blocking.)
`viewer-distribution` took two modified requirements and two removed, the
delta's (design.md's "three modified" counted one more than the delta
holds). By hand: the created spec `viewer-seam`'s Purpose in place of the
CLI's placeholder, and the Purpose lines of `export`, `printed-pieces` and
`openscad-node` that named `machinome/viewers/`, now naming the seam, the
web viewer's `stage.py` and the OpenSCAD viewer's distribution.

```
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 51 passed, 0 failed (51 items)
$ env -C <bench>/packages/machinome openspec validate --all --strict
Totals: 51 passed, 0 failed (51 items)
```

(`<scratch>/12.2-validate-specs.out`, `<scratch>/12.3-validate-all.out`.)

### The plan's progress

`workflow/ongoing/release-0.9.md`, Progress, entry "3. `viewer-seam`." after
the seam's and `release-tooling`'s, written as those are.

### The record-reading tests at the close

```
$ ... pytest -q tests/test_repository_layout.py tests/test_release_records.py tests/test_docs_structure.py \
    tests/test_viewer_documentation_links.py tests/test_docs_exports.py tests/test_expression_type_cost.py \
    tests/test_node_root_exports_nothing.py
167 passed, 6992 subtests passed in 20.69s                         (<scratch>/12-close-core.out)
```

### 12.4 (task 12.4)

Everything left uncommitted for the orchestrator's review; the
implementation commit and the integration into `v0.9-joins` are the
orchestrator's. Nothing pushed.
