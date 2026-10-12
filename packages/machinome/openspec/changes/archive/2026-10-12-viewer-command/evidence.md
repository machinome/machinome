# Evidence: `viewer-command`

A cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` and `release-0.9.md` at the repository
root). Worktree `machinome/WTs/v0.9-joins-viewer-command`, branch
`v0.9-joins-viewer-command`, on the line `v0.9-joins` at cca33986 (after
`join-studio` and `viewer-seam`). Planning commit 4c68d02c, ratified by the
orchestrator on 12 October 2026 with every recommendation of its Open
Questions accepted. Applied on 12 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), npm (the root's
workspace), Playwright's Chromium headless shell, the OpenSpec CLI 1.6.0.
Every command ran with `env -C <dir>` and absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-viewer-command`,
`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C11-apply/`,
`<propose>` the proposer's `.../scratchpad/C11-propose/`. The core's tests
ran from `<bench>/packages/machinome` on the bench venv, one pytest process
at a time. Logs and images are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -4
4c68d02c Propose viewer-command: the viewer's verbs are the framework's viewer command
cca33986 Implement viewer-seam: viewers are providers behind one seam, chosen by name
1f0c1cb0 Propose viewer-seam: viewers are providers behind one seam, chosen by name
01981a3f Implement join-studio: the studio as the distribution machinome-studio, imported as machinome.studio, run as machinome studio
$ git -C <bench> status --short | wc -l
0
$ git -C <bench> ls-files | wc -l
6143
```

The seam landed as design.md reads it: `packages/machinome/machinome/viewer/__init__.py`
defines `CaptureRequest` (the snapshot's ten options, `camera` the
notation), `require` and `ViewerLacks`;
`packages/machinome-viewer/machinome/viewer/web/__init__.py` defines
`describe`, `capture` (resolving `request.camera` with `parse_camera`) and
`serve` (a `Session` started, whose `start()` raises `ViewerError` when the
port cannot be bound or the thread dies first);
`packages/machinome/machinome/manager/viewer.py` prints
`viewers.require('web', 'embed', 'machinome viewer').describe()` as JSON,
importing the seam at its top; `packages/machinome-viewer/pyproject.toml`
declares `[project.scripts] machinome-viewer =
"machinome.viewer.web.cli:main"`.

### 1.2 The venv and the base suite (task 1.2)

The bench venv was synced from the lock by the orchestrator
(`<join>/uv-sync-2.log`: "Resolved 201 packages", ending "exit 0", `<join>`
being `.../scratchpad/C11-join/`): 192 packages (`uv pip list`), 18
`__editable__` `.pth` files; `<bench>/.venv/bin/machinome-viewer` exists (373
bytes).

The base suite, from the line's latest archived evidence
(`2026-10-12-viewer-seam/evidence.md`, 11.1 and 11.2), not rerun: the core
4985 passed, 9 skipped; the viewer 259 passed, 2 skipped; the movie 322
passed; the studio 485 passed, 24 skipped.

### 1.3 The modified requirements against the landed baseline (task 1.3)

Each requirement this change modifies was extracted from
`openspec/specs/<capability>/spec.md` (landed), from the seam's delta as
committed at its planning (`git show 1f0c1cb0:...`) and as archived, and from
this change's delta (`<scratch>/reqdiff.py`, diffs in `<scratch>/1.3/`):

| capability / requirement | seam planned vs archived | seam planned vs landed | landed vs this delta |
|---|---|---|---|
| `cli` "Viewer command" | identical | identical | this change's edits only |
| `cli-startup-cost` "The viewer command loads no geometry stack" | identical | identical | this change's edits only |
| `viewer-distribution` "The framework resolves the Machinome viewer" | identical | identical | this change's edits only |
| `viewer-seam` "The viewer is chosen by the flag, the project, or the command's default" | identical | identical | this change's edits only |
| `viewer-seam` "The web viewer runs in the framework's process" | identical | identical | this change's edits only |
| `framework-identity` "The framework is the package directory `packages/machinome` of a monorepo" | identical | identical | this change's edits only |
| `user-documentation` "The browser viewer is documented in the manual" | (not in the seam) | the line's text at 01981a3f equals the landed text | this change's edits only |

No difference: nothing re-applied.

```
$ env -C <bench>/packages/machinome openspec validate viewer-command --strict
Change 'viewer-command' is valid
```

### 1.4 The lint base (task 1.4)

```
$ env -C <bench> make lint 2>&1 | tail -3
tests/vet_projects/unresolved_import/sim/__init__.py:4:1: W391 blank line at end of file
tests/vet_projects/unresolved_reference/sim/__init__.py:4:1: W391 blank line at end of file
make: *** [Makefile:140: lint] Error 1
```

(`<scratch>/1.4-lint.out`.) flake8: 2539 lines, the seam's count; black: 594
files would be reformatted, 198 left unchanged, 1 would fail (the vet's
planted `broken.py`).

### 1.5 The originating baselines (task 1.5)

The bench's widget bundle was older than its sources (the first staging
refused with the `BundleStale` remedy, `<scratch>/1.5-stage.log` of the
first attempt); `npm ci` at the bench root (exit 0, `<scratch>/1.5-npm-ci.log`)
and `npm run build --workspace
packages/machinome-viewer/machinome/viewer/web/widget` (exit 0, 895.9 kB,
`<scratch>/1.5-npm-build.log`) made it current. `git status` clean after
both (the bundle is ignored).

The staging. A copy of `packages/machinome/docs/tutorial` at
`<scratch>/base/tut` (no `_build`), its carry pose staged by the bench's
`machinome snapshot --viewer web --drive crank=3580` run through
`<scratch>/stage_keep.py`, which wraps `machinome.viewer.web.withdraw` to copy
the staging to `<scratch>/base/staged` before removing it:

```
$ env -C <scratch>/base/tut python <scratch>/stage_keep.py <scratch>/base/staged \
      snapshot --viewer web --drive crank=3580 -o <scratch>/base/base-carry-web.png
Snapshot saved to <scratch>/base/base-carry-web.png      exit 0, 9.3 s
$ sha256sum <scratch>/base/base-carry-web.png
b46f77a49af602ae32e9a76f41fc315bdbab7bc155cd7e356e4a4c49083072f3
```

The staging holds `viewer.json`, the four STLs and the marking under
`counter/`, and the page and bundle the capture wrote; the image is
design.md probe 2's (`b46f77a4…`).

The five captures, `machinome-viewer capture` on a fresh copy of the staging
each (`<scratch>/1.5-captures.txt`):

| set | options | exit | time | SHA-256 |
|---|---|---|---|---|
| 1 | (none) | 0 | 2.48 s | `b46f77a49af602ae32e9a76f41fc315bdbab7bc155cd7e356e4a4c49083072f3` |
| 2 | `--view=-80,60,40,0,0,0` | 0 | 2.81 s | `690121f6467fa73f7306717070007dde8e6cf359d32691e16f682cd7af36a8f4` |
| 3 | `--view=-80,60,40,0,0,0 --up 0,1,0 --fov 30` | 0 | 3.74 s | `8d397810b875a9d3101021956166184e1a4ffb22b49baa283b7fb8c38bbf7d8d` |
| 4 | `--fov 30 --imgsize 800x600` | 0 | 1.33 s | `2b4e094d14a381b13417c9dae0bd84849986f7f81f1602601b6103eb630d9c9f` |
| 5 | `--time 0.25` | 0 | 2.26 s | `b46f77a49af602ae32e9a76f41fc315bdbab7bc155cd7e356e4a4c49083072f3` |

Each hash is design.md probe 3's. Looked at
(`<scratch>/base/contact-base.png`): the counter on its base, the drum's
digits and the crank, framed whole (1, 5); from the requested eye towards the
origin (2); up the Y axis at 30 degrees (3); 800 x 600 at 30 degrees (4).

Gear-shift. `Vibecoded-demos/gear-shift` at f3c79c2 copied by `git archive
HEAD` to `<scratch>/base/gear-shift`, built with the bench's `machinome
build` (exit 0, 17.1 s, `<scratch>/1.5-gs-build.log`), served by
`machinome-viewer serve --build-dir <scratch>/base/gear-shift/_build --port
8793` and opened at 1280 x 800 in headless Chromium for 8 s with
`<scratch>/probe_gs_page.py` (design.md probe 11's):

```
base: listening after 10.2s total; console ['warning']; exit 0
```

`<scratch>/base/gs-base.png`, looked at: the gearbox on its open frame, the
assembly sidebar with `GearboxDemo` and its five subassemblies
(`open_frame`, `input_axis`, `layshaft_axis`, `output_axis`, `selector`), the
time slider and the full-screen button. Then `<scratch>/probe_serve.py`
(design.md probe 6's) on the same build and port
(`<scratch>/1.5-serve-signals.txt`): SIGINT, listening after 558 ms,
`/_viewer` available with API 29, `viewer.json` `8f656a301326`, page
`f4a78266072d`, the socket greeting `'reload'`, exit 0 after 182 ms; SIGTERM,
listening after 497 ms, the same bytes, exit -15 after 163 ms; uvicorn's
eight lines on standard error each time. No listener on 8793 afterwards
(`ss -ltn`).

## 2. Red first

Every red below was run on the bench at the base code (the planning
commit's implementation, the seam's `manager/viewer.py`, `CaptureRequest`
of ten fields, the viewer's `cli.py` whole and its `[project.scripts]`),
with only the tests edited. The core's tests ran from
`<bench>/packages/machinome`, the viewer's from
`<bench>/packages/machinome-viewer`, `python -m pytest -q -p
no:cacheprovider`.

### 2.1 `tests/test_manager_viewer.py` (task 2.1)

Rewritten: the three tests of the seam kept, patching the seam (the bare
report now also asserts `require('web', 'embed', 'machinome viewer')`), the
document-versions test kept, and 27 tests added in eight classes:
`TheVerbsTest` (6: no verb, `--viewer` on each verb, serve's options,
capture's options as tuples, nine usage errors, serve's three deprecated
flags refused), `DescribeVerbTest` (2), `RefusalTest` (6, through the real
seam and both installed providers: describe, serve and capture refused for
the OpenSCAD viewer, the document refusal naming the viewers that can, an
unknown name, an absent viewer), `TheVerbsReadNoProjectTest` (2, inside a
project declaring `viewer = "openscad"`), `CaptureVerbTest` (5: the parts as
given, absent parts `None`, a lone field of view, `--time 2` refused before
the seam is asked, a `ViewerError` exit 1, the staging never withdrawn),
`ServeVerbTest` (3: the call, `stop()` on `KeyboardInterrupt`, exit 0, the
SIGTERM handler restored; the default port; a `serve()` that raises exit 1),
`ServeSignalsTest` (2, a `machinome` process whose seam answers a stand-in
viewer: SIGINT exit 0 and `stopped`, SIGTERM exit -15 and `stopped`) and
`ThePortIsTakenTest` (1, the real web viewer, a socket bound and listening
on `0.0.0.0` first, `subprocess.run(..., timeout=10)`).

```
32 failed, 10 passed, 10 subtests passed in 1.18s                 (<scratch>/2.1-red.out)
```

31 tests: 21 failed and 11 subtests failed. Every failure is argparse's:
`machinome viewer: error: unrecognized arguments: describe` (and `serve
...`, `capture ...`), exit 2 where 0 or 1 was asserted;
`test_no_verb_is_the_report` `AttributeError: 'Namespace' object has no
attribute 'verb'`; the two `ServeSignalsTest` tests read `''` where
`'serving _build 8791\n'` was expected (the process exited 2 before
serving); `ThePortIsTakenTest` `2 != 1`, "-c: error: unrecognized arguments:
serve --build-dir ... --port 36797". Green at the base and to stay so: the
four report tests (`ViewerCommandTest` three, `DocumentVersionsReportTest`
one), and `test_usage_errors` and `test_serve_takes_none_of_the_deprecated_flags`,
green at the base only because the base refuses every verb.

### 2.2 `tests/test_viewer_seam.py` (task 2.2)

Two classes added: `TheCaptureRequestTest` (3: the parts absent unless
given, held as given, the notation and each part refused together, four
subtests) and `TheWebCaptureTest` (5, `machinome.viewer.web.capture.Capture`
patched: an eye and a target alone, every part, a lone field of view, no
part, the notation resolved by `parse_camera`).

```
$ python -m pytest -q tests/test_viewer_seam.py -k "CaptureRequest or WebCapture"
9 failed, 3 passed, 32 deselected, 3 subtests passed in 0.46s     (<scratch>/2.2-red.out)
```

Reasons: `TypeError: CaptureRequest.__init__() got an unexpected keyword
argument 'eye'` (and `'target'`, `'up'`, `'fov'` in the four subtests,
`'fov'` in the lone field of view); `AttributeError: 'CaptureRequest' object
has no attribute 'eye'`. Green at the base: no part, the notation resolved.

### 2.3 `tests/test_cli_lazy_imports.py` (task 2.3)

`test_the_describe_verb_answers_as_the_report_does` added (in a fresh
interpreter: `machinome viewer describe` exits 0, prints the bare report's
bytes, imports `machinome.viewer.web` and none of its server, capture,
stage or session, `fastapi`, `uvicorn`, `playwright`, `cadquery`, `trimesh`
or `solid2`); `test_a_command_s_help_imports_no_viewer` gains `['viewer',
'-h']` and `['viewer', 'capture', '-h']`.

```
1 failed, 1 passed, 23 deselected, 5 subtests passed in 2.68s     (<scratch>/2.3-red.out)
```

Reason: `2 != 0`, "-c: error: unrecognized arguments: describe". The help
test is green at the base: `machinome viewer capture -h` prints the base's
help, `-h` being acted on before the unknown verb.

### 2.4 `tests/test_machinome_identity.py` (task 2.4)

`test_no_distribution_but_the_framework_declares_a_command`: every
`packages/*/pyproject.toml` but the core's read, none declaring
`[project.scripts]`.

```
1 failed, 4 passed, 5 subtests passed in 0.47s                    (<scratch>/2.4-red.out)
```

Reason: `Lists differ: ['machinome-viewer'] != []`.

### 2.5 `tests/test_docs_structure.py` (task 2.5)

`CommandReferenceTest.test_the_viewer_command_has_its_section`: the label
`.. _viewer-command:` before the title `machinome viewer`; in the section
`machinome viewer describe`, `serve`, `capture`, `python -m
machinome.viewer.web` and `:doc:\`/reference/viewer/cli\``; the parser built
by `Viewer().add_arguments` on a fresh parser, its subparsers exactly
`capture`, `describe`, `serve`, and every option string of every verb but
`-h`/`--help` in the section (ten: `-o`, `--output`, `--imgsize`, `--time`,
`--view`, `--up`, `--fov`, `--build-dir`, `--port`, `--viewer`).
`KernelExtrasTest.STALE` gains `VIEWER_COMMAND`, the three spellings of the
former command written in pieces, and `RECORDS` allows them on
`project/changelog.rst` and `project/upgrading.rst`.

```
$ python -m pytest -q tests/test_docs_structure.py -k "viewer_command or old_addresses"
8 failed, 1 passed, 30 deselected, 2072 subtests passed in 0.44s   (<scratch>/2.5-red.out)
```

Reasons: "'.. _viewer-command:\n\nmachinome viewer\n' not found in" the
page; seven subtests of the stale scan: `howto/share-an-export.rst`
(`capture`), `reference/cli.rst` (`serve`), `reference/viewer/cli.rst`
(`describe`, `serve`, `capture`), `reference/viewer/compatibility.rst` and
`reference/viewer/troubleshooting.rst` (`describe`).

### 2.6 The viewer's tests (task 2.6)

`tests/test_machinome_identity.py`: the manifest declares no `scripts`
(its docstring says so). `tests/test_cli.py` rewritten: `ModuleCommandTest`
(4, the seam's `require` patched: `main(['describe'])` prints the report
through the seam, `main([])` prints it too, `--start-frontend`, `--dev` and
`--frontend-port` exit 2 with "unrecognized arguments" and no server and no
viewer asked, `main(['-h'])` prints `usage: machinome viewer` and the three
verbs) and `ModuleEntryTest` kept; the describe, capture and serve tests of
the former command are the core's `test_manager_viewer.py`'s now.
`tests/test_documentation.py`: `test_cli_options_are_all_documented` and its
`import ast` removed (the core's section test reads the parser).

```
$ env -C <bench>/packages/machinome-viewer python -m pytest -q \
      tests/test_machinome_identity.py tests/test_cli.py tests/test_documentation.py
7 failed, 21 passed, 1 warning, 4 subtests passed in 0.68s        (<scratch>/2.6-red.out)
```

Reasons: "'scripts' unexpectedly found in {'name': 'machinome-viewer', ...}";
the describe test read the installed bundle's report, not the seam's
(`cli.describe`); "'usage: machinome viewer' not found in 'usage:
machinome-viewer [-h] {describe,serve,capture} ...'"; `main([])` printed
the help (`JSONDecodeError: Expecting value: line 1 column 1`); the three
deprecated flags "SystemExit not raised" (accepted). Green at the base: the
module entry and the documentation tests (the `describe` example test
among them).

### 2.7 `scripts/check-dist` (task 2.7)

The `machinome-viewer` row: its code asserts no entry point in the group
`console_scripts` and no `Path(VENV) / 'bin' / 'machinome-viewer'`; its
commands are `['machinome', 'viewer']`, `['machinome', 'viewer',
'describe']` and `['python', '-m', 'machinome.viewer.web', 'describe']`.

```
$ flake8 --max-line-length=89 scripts/check-dist
(nothing)                                                          exit 0
$ env -C <bench> python scripts/check-dist                         (<scratch>/2.7-check-dist-red.out)
...
machinome-studio 0.8.1 module .../machinome/studio/__init__.py hub answered
   machinome studio -h: exit 0
$ .../venv/bin/python -I -c VENV = '...' ...
Traceback (most recent call last):
  File "<string>", line 33, in <module>
AssertionError: (EntryPoint(name='machinome-viewer', value='machinome.viewer.web.cli:main', group='console_scripts'),)
check-dist failed: exit 1: ...
Nothing uploaded.
real 4m35.271s
```

Every member before the viewer built, checked and smoked; the viewer's
smoke fails on the `console_scripts` assertion, its wheel still declaring
`machinome-viewer`.

## 3. The seam's request

### 3.1 `CaptureRequest` (task 3.1)

`packages/machinome/machinome/viewer/__init__.py`: `CaptureRequest` gains
`eye`, `target`, `up` and `fov`, default `None`, its docstring the two forms,
and `__post_init__` raising `ValueError` ("a capture request names its
camera by the --camera notation or by its parts (eye, target, up, fov), not
both") when `camera` is not `None` and any part is. `git diff --stat` of the
module: 19 insertions, 1 deletion, that hunk alone.

### 3.2 The web viewer's `capture` (task 3.2)

`packages/machinome-viewer/machinome/viewer/web/__init__.py`: with
`request.camera`, `parse_camera` resolves the four parts as before; else the
request's parts are taken as given; `view = (eye, target)` only when the eye
is given, `up` a tuple when given, then `mount_options` as before. Its
docstring and the module's no longer name the console script.

```
$ python -m pytest -q tests/test_viewer_seam.py tests/test_snapshot.py tests/test_web_viewer_capture.py
171 passed, 1 skipped, 55 subtests passed in 7.39s                (<scratch>/3.2-green.out)
```

## 4. The command

### 4.1 `machinome/manager/viewer.py` (task 4.1)

As design.md Decisions 1 to 4 state it. The module imports `argparse`,
`json`, `os`, `signal`, `sys` and `time` and nothing else at its top; the
seam is imported in each handler. The class docstring, `machinome -h`'s
help: "Reports the installed viewer as JSON, and serves or photographs
through a viewer." The verbs are an argparse subparser group `dest='verb'`
titled "Verbs", the three parsers `_imgsize`, `_view` and `_triple` moved
from the viewer's `cli.py` with their messages, the options with the former
command's help strings, metavars and defaults, `--viewer NAME` (default
`web`) on each verb. With no verb, `require('web', 'embed', 'machinome
viewer').describe()` as before. `describe` asks `embed`; `serve` asks
`serve`, then `provider.serve(build_dir, port=port)`, a `ViewerError` written
"Error: <message>", exit 1, then waits in `time.sleep` with a SIGTERM
handler that raises `KeyboardInterrupt`; the interrupt stops the session,
the previous handler is restored, and after a SIGTERM the default action is
restored and the signal re-raised. `capture` checks `--time` first (exit 2,
the former line), asks `capture`, refuses a viewer whose
`document_versions()` is `None` with the seam's `ViewerLacks` sentence for
"photograph a published document" and the viewers that capture and read a
document, computed over `EXTRAS` as the seam computes `_able`, builds
`CaptureRequest(imgsize='WxH', time, eye, target, up, fov)`, and writes a
`ViewerError` as "Error: <message>", exit 1; it never calls `withdraw`.
Every refusal of the seam (`ImportError`, `LookupError`, `RuntimeError`,
`OSError`, the seam's own tuple) goes to standard error, exit 1. flake8:
0 lines on the module.

### 4.2 The tests green (task 4.2)

```
$ python -m pytest -q tests/test_manager_viewer.py
31 passed, 21 subtests passed in 1.61s                            (<scratch>/4.2-manager.out)
$ python -m pytest -q tests/test_manager_viewer.py tests/test_cli_lazy_imports.py tests/test_cli.py \
      tests/test_viewer_seam.py tests/test_viewer_report.py tests/test_machinome_identity.py \
      tests/test_docs_structure.py
163 passed, 6590 subtests passed in 15.85s                        (<scratch>/4.2-green.out)
```

The serve test against a bound port (`ThePortIsTakenTest`) exits 1 with one
`Error:` line naming the port, well inside its 10 s timeout: the seam's
`serve()` raises (the session's `bind` fails before the thread starts).

`tests/test_viewer_report.py`'s
`test_the_report_is_the_one_the_viewer_s_own_command_prints` was extended
after the reds, during the implementation, to run `machinome viewer
describe` beside `machinome viewer` and `python -m machinome.viewer.web
describe` and compare the three outputs (the `cli` scenario "The report is
the one the viewer's own command prints"), its module docstring naming the
new spellings; it was not run red, and at the base it would have failed on
`machinome viewer describe` exiting 2, the red 2.3 records. 12 passed.

### 4.3 By hand (task 4.3)

From `<scratch>/4.3`, the bench venv on the PATH (`<scratch>/4.3-by-hand.txt`):

| command | stdout | exit |
|---|---|---|
| `machinome viewer` | the report, SHA-256 `8e46a00f8f459aff…` | 0 |
| `machinome viewer describe` | byte-identical (`cmp`) | 0 |
| `python -m machinome.viewer.web describe` | byte-identical | 0 |
| `python -m machinome.viewer.web` | byte-identical | 0 |
| the base's `Viewer().handle()` (`git show HEAD:.../manager/viewer.py`, run from a scratch file) | byte-identical | 0 |
| `machinome viewer describe --viewer openscad` | nothing; "machinome viewer describe needs a viewer that can embed, and the openscad viewer cannot; the viewers that can: web" | 1 |
| `machinome viewer serve --viewer openscad --build-dir _build` | nothing; "... serve needs a viewer that can serve, and the openscad viewer cannot; the viewers that can: web" | 1 |
| `machinome viewer capture --viewer openscad <staged> -o never.png` | nothing; "... capture needs a viewer that can photograph a published document, and the openscad viewer cannot; the viewers that can: web"; no image | 1 |
| `machinome viewer describe --viewer povray` | "no viewer is named 'povray'; the viewers are openscad, web" | 1 |
| `machinome viewer -h` | the three verbs under "Verbs" | 0 |
| `machinome viewer capture -h`, `serve -h` | the former options and `--viewer NAME` | 0 |
| `machinome viewer serve` | "the following arguments are required: --build-dir" | 2 |
| `machinome viewer serve --build-dir _build --start-frontend` | "unrecognized arguments: --start-frontend" | 2 |
| `machinome viewer capture st -o x.png --time 2` | "Error: --time must be between 0.0 and 1.0, got 2.0" | 2 |
| `machinome viewer capture <nowhere> -o never.png` | "Error: Staged document not found: <nowhere>/viewer.json"; nothing created | 1 |
| `machinome viewer bogus` | "argument verb: invalid choice: 'bogus' (choose from 'describe', 'serve', 'capture')" | 2 |

Each line is design.md probe 5's, the refusals now ending with the seam's
"; the viewers that can: web", which the landed `ViewerLacks` adds.

## 5. The console script and the module entry

### 5.1 The manifest (task 5.1)

`packages/machinome-viewer/pyproject.toml`: the `[project.scripts]` table
(two lines and the blank after them) removed, nothing else (`git diff`).

```
$ env -C <bench> uv sync --python 3.12                            (<scratch>/5.1-uv-sync.log)
Installed 1 package in 12ms
 ~ machinome-viewer==0.8.1 (from file://<bench>/packages/machinome-viewer)
exit 0
$ ls <bench>/.venv/bin/machinome-viewer
ls: cannot access '<bench>/.venv/bin/machinome-viewer': No such file or directory
$ python -c "import importlib.metadata as m; print(list(m.distribution('machinome-viewer').entry_points))"
[]
```

`uv.lock` unchanged (`git status`).

### 5.2 `cli.py`, `__main__.py` and the docstrings (task 5.2)

`cli.py` is its header, a module docstring and design.md Decision 7's
`main(argv=None)` (the framework's `Viewer` with a parser `prog='machinome
viewer'`, `return 0`); `build_parser`, `run_describe`, `run_serve`,
`run_capture`, `COMMANDS`, `FRONTEND_FLAG_NOTICE`, the logger and the three
parsers are gone. `git diff` of `__main__.py`: its docstring's first line
alone ("the framework's ``machinome viewer``, through an interpreter"). The
docstrings of `bundle.py`, `capture.py`, `server.py` and `session.py` (and
a comment of `session.py`) name `machinome viewer describe`, `capture` and
`serve`; `server.py`'s comment that `cli.py` goes on accepting `--dev` and
`--start-frontend` now says no command passes `dev` or `frontend`.

## 6. The core of the set

### 6.1 `context7.json` (task 6.1)

The viewer line's sentence, in place: "The framework reaches it through its
seam of viewers, machinome.viewer, in its own process, and no entry point
names it. Its command is machinome viewer describe|serve|capture; machinome
viewer alone prints the report." The file parses as JSON.

## 7. The manual

### 7.1 `reference/cli.rst` (task 7.1)

The section `.. _viewer-command:` / `machinome viewer`, between `machinome
export` and `machinome models`: the synopsis of design.md Decision 1, the
report and its five keys, `describe`, the refusal path, `python -m
machinome.viewer.web`; `--viewer NAME` (the web viewer by default, the
project's `viewer` key not read, a viewer refused by name naming the viewers
that can, what each verb needs); `serve` and `capture` in one paragraph each;
the exit statuses; the link to `:doc:\`/reference/viewer/cli\``.
`develop`'s `--debug-builder` names `machinome viewer serve --build-dir
_build`.

### 7.2 The viewer's pages (task 7.2)

`reference/viewer/cli.rst` kept, retitled "The viewer command": its opening
says `machinome viewer` reports and runs the installed viewer, the verbs ask
the viewer `--viewer` names, `web` by default, no project key read, refusals
by name, and `python -m machinome.viewer.web` runs the same command, linking
`:ref:\`viewer-command\``; each example spelt `machinome viewer <verb>`;
`describe`'s closing paragraph says `machinome viewer` with no verb prints the
same report; `serve`'s table without the three deprecated flags and with
`--viewer NAME`, its prose stating Ctrl-C exit 0, a termination signal ending
the process and a taken port exit 1; `capture`'s table with `--viewer NAME`
(a viewer that reads no published document refused), its closing paragraph
the exit statuses with the staging left in place; the endpoints table, the
warning on 0.0.0.0 and the capture's notes unchanged.
`reference/viewer/compatibility.rst` (`machinome viewer describe`; "The
framework exposes its own lookup as ``machinome viewer``" became
"``machinome viewer`` with no verb prints the same report"),
`reference/viewer/troubleshooting.rst` (`machinome viewer describe`) and
`howto/share-an-export.rst` (`machinome viewer capture`).

### 7.3 `project/upgrading.rst` (task 7.3)

In the 0.9 section, the subsection "The viewer's command" (label
`upgrade-viewer-command`): the three verbs where the former command was
written, a host that ran `machinome-viewer describe` running `machinome
viewer`; serve's three flags dropped; the module form printing the report
with no verb. The section's earlier bullet ("or runs ``machinome-viewer
describe``") loses those words in place, since the command it named is gone.

## 8. The records

### 8.1 `HISTORY.rst` and the manual's changelog (task 8.1)

`HISTORY.rst`: one `Unreleased` bullet after the seam's, "The viewer's verbs
are the framework's ``viewer`` command", naming ADR-196 and the two amended.
`docs/project/changelog.rst`: one `Unreleased` bullet after the seam's,
"The viewer's verbs are ``machinome viewer``'s", linking
`:ref:\`viewer-command\`` and `:ref:\`upgrade-viewer-command\``; and the
`join-viewer` bullet "The browser viewer is part of this manual", which said
a script "runs ``python -m machinome.viewer.web`` or the
``machinome-viewer`` command, which is unchanged", now ends "runs ``python
-m machinome.viewer.web`` or ``machinome viewer``" (in place; the design
names only the new bullet, but the old one's claim is no longer true).

### 8.2 `docs/architecture.md` (task 8.2)

The viewer section, after "the one licence removed the reason for that
boundary", gains the command's sentences: the report with no verb, the
verbs asking the viewer `--viewer` names, never the project's, the
operations, the parts in the request, the console script removed and the
module form running `machinome viewer` (ADR-196).

### 8.3 ADR-196 (task 8.3)

`docs/adrs/BUILD/ADR-196-the-viewer-s-verbs-are-the-framework-s-viewer-command.md`,
Status Proposed, dated 2026-10-12, amending ADR-188 and ADR-194, related to
ADR-189, ADR-024 and ADR-193: context, five options, the decision (the
command, no manifest, the request, the console script, the module form),
consequences, references. ADR-188's status line: "its console script
`machinome-viewer` removed, amended 2026-10-12 by ADR-196"; ADR-194's: "its
clause keeping `machinome-viewer` and the module form printing what they
printed, amended 2026-10-12 by ADR-196". `docs/adrs/README.md`: the index
line of ADR-196 after ADR-194's, **Proposed**; ADR-188's line ends
"console script removed by 196", ADR-194's "amended by 196".

### 8.4 The viewer's own record (task 8.4)

`packages/machinome-viewer/CHANGELOG.md`, `Unreleased`: the `join-viewer`
bullet loses "the `machinome-viewer` command," in place, the seam's bullet
loses "or `machinome-viewer describe`" and its closing sentence on the
console script and the module form, and one bullet is added: the command
removed, its verbs `machinome viewer`'s, serve's three flags gone, the
module form, the camera's parts.
`packages/machinome-viewer/openspec/config.yaml`: the context paragraph
naming the entry point and the console script states the seam and the
command. The viewer's specs, in place: `development-server` (the purpose,
the code line, the requirement "The server is launched on a build
directory", whose compatibility promise to go on accepting the three flags
this change's Open Questions 7 withdraws, and its two scenarios),
`snapshot-capture` (the purpose, the code line, the requirement's opening),
`user-documentation` (two scenarios) and `viewer-distribution` (the purpose,
the code line, eleven lines naming `machinome-viewer describe`, the
requirement "Everything else is a process" and "The viewer remains an
independent process", which named the process commands). The decision log
is untouched.

```
$ git -C <bench> grep -nE "machinome-viewer (describe|serve|capture)" \
    | grep -vE "openspec/changes/archive/|/releases/|workflow/|docs/adrs/|openspec/changes/viewer-command/"
packages/machinome-viewer/CHANGELOG.md:205:- `machinome-viewer describe|serve|capture`: the version, API and document
packages/machinome-viewer/openspec/changes/execute-running-time-drives/evidence.md:41:| Workspace `machinome-viewer describe` | API 23, documents 1–10, package 0.2.0 |
packages/machinome/docs/project/upgrading.rst:42:   **where you wrote** ``machinome-viewer describe``, ``machinome-viewer
packages/machinome/docs/project/upgrading.rst:43:   serve`` and ``machinome-viewer capture``. The options are the same, and
packages/machinome/docs/project/upgrading.rst:45:   ``machinome-viewer describe`` runs ``machinome viewer``, whose output is
packages/machinome/openspec/specs/cli/spec.md:826:- **WHEN** `machinome viewer` and `machinome-viewer describe` run in one
packages/machinome/openspec/specs/framework-identity/spec.md:521:  repository, and its licence texts; `machinome-viewer describe` and
packages/machinome/openspec/specs/viewer-distribution/spec.md:112:remedy. The viewer's console script `machinome-viewer describe|serve|capture`
packages/machinome/openspec/specs/viewer-distribution/spec.md:119:  the same object `machinome-viewer describe` prints
packages/machinome/openspec/specs/viewer-seam/spec.md:204:`machinome-viewer describe|serve|capture` and `python -m machinome.viewer.web`
```

What remains: the viewer changelog's released section (its 0.7.0 entry); a
dated evidence file of a viewer change (`execute-running-time-drives`,
what a run printed then, kept as recorded); the upgrading page, which records
the former spelling by design; and the framework's baseline specs, which
this change's deltas replace at the archive (task 11.3).

## 9. Validation

### 9.1 The suite (task 9.1)

No other bench's pytest ran (`ps`, no `pytest` process but this one).

```
$ env -C <bench>/packages/machinome python -m pytest -q -p no:cacheprovider
5023 passed, 9 skipped, 55 warnings, 13246 subtests passed in 805.11s (0:13:25)   (<scratch>/9.1-suite.out)
```

Against the base's 4985 passed and 9 skipped (1.2): 38 tests more, each this
change's: `test_manager_viewer.py` 31 in place of 4 (+27),
`test_viewer_seam.py` +8 (`TheCaptureRequestTest` 3, `TheWebCaptureTest` 5),
`test_cli_lazy_imports.py` +1, `test_machinome_identity.py` +1,
`test_docs_structure.py` +1; `test_viewer_report.py`'s extended test is the
same test. No test removed from the core. No EMFILE.

### 9.2 The other suites and the lint (task 9.2)

```
$ env -C <bench>/packages/machinome-viewer python -m pytest -q -p no:cacheprovider
250 passed, 2 skipped, 63 warnings, 191 subtests passed in 256.86s   (<scratch>/9.2-viewer.out)
$ env -C <bench>/packages/machinome-movie python -m pytest -q -p no:cacheprovider
322 passed in 36.62s                                                 (<scratch>/9.2-movie.out)
$ env -C <bench> make test PKG=machinome-studio
485 passed, 24 skipped, 3 warnings in 108.42s                        (<scratch>/9.2-studio.out)
```

The viewer against the base's 259 passed, 2 skipped: 9 fewer, all this
change's. `test_cli.py` 5 in place of 13 (-8: the former command's
`DescribeCommandTest` 3, `CaptureCommandTest` 6, `ServeCommandTest` 3 and
`ModuleEntryTest` 1 became `ModuleCommandTest` 4 and `ModuleEntryTest` 1;
the verbs' tests are the core's now), `test_documentation.py` -1
(`test_cli_options_are_all_documented`); 191 subtests against 188 (+3, the
three refused flags). The movie and the studio: the base's counts. (A first
viewer run at 5.3, before the changelog and the specs were edited, gave the
same 250 passed, 2 skipped, `<scratch>/5.3-viewer.out`.)

```
$ env -C <bench> make lint 2>&1 | tail -1
make: *** [Makefile:140: lint] Error 1                               (<scratch>/9.2-lint.out)
```

flake8: 2538 lines against 1.4's 2539; the one line gone is the former
`cli.py`'s E501, and no line is new (the two outputs compared with line
numbers stripped). black: 594 would be reformatted, 198 left unchanged, 1
would fail, the same set of files as 1.4's.

### 9.3 The manual (task 9.3)

```
$ env -C <bench> make docs
...
The HTML pages are in docs/_build/html.                              exit 0, 13.2 s (<scratch>/9.3-docs.out)
```

Warnings as errors (`-W -E`); the only "warning" lines are uv's hardlink
notice while installing the docs venv.

### 9.4 The archives (task 9.4)

```
$ env -C <bench> make check                                          exit 0, 8 min 18 s (<scratch>/9.4-check.out)
```

Both runs, on the tree and on a clean copy of the tracked files, end
"Every distribution built, checked, installed and smoked; nothing
uploaded.", 36 archives each, 72 `twine check --strict` PASSED lines. The
viewer row, each run:

```
machinome-viewer 0.8.1 module .../venv/lib/python3.12/site-packages/machinome/viewer/web/__init__.py contract 1 operations ['capture', 'embed', 'present', 'serve'] API 29 documents 1 to 13
   machinome viewer: exit 0
   machinome viewer describe: exit 0
   python -m machinome.viewer.web describe: exit 0
```

its code having asserted no `console_scripts` entry point and no
`venv/bin/machinome-viewer`. The archives' counts are the base's (2.7) but
for: the viewer's wheel 23 entries and sdist 1092 on the tree, 22 and 1091
on the clean copy, against 24 and 1093 on the base tree (the wheel's
`entry_points.txt` and the sdist's egg-info copy of it gone; the tree's one
entry more than the clean copy is `widget/dist/.build.lock`, an ignored file
the bundle's build leaves beside the bundle, which the package data's glob
ships from a working tree); and the core's sdist on the tree 1154 entries
against 1092 on the clean copy and at the base. The working tree then held
ignored files the 9.1 suite and 9.3's build had left: 54 under `tests/`
(the STEP fixtures written to `tests/step_project/`, `tests/_build_meta/`,
the locks), which `MANIFEST.in`'s `recursive-include tests *` takes, and 3
images under `docs/_build/html/_static`; the 62 entries were not itemised
one by one. 2.7 ran before any suite on this bench, and the clean copy,
which has none of them, gives the base's count.

## 10. The originating check

### 10.1 The five captures (task 10.1)

A fresh staging of the carry pose with the changed code
(`<scratch>/after/tut`, `stage_keep.py` as in 1.5, exit 0, 10.8 s,
`<scratch>/10.1-stage.log`): the snapshot's image SHA-256 `b46f77a4…` again,
and `diff -rq` against 1.5's staging differs only in `viewer.json`, whose
differences are the artifacts' `mtime` fields (five lines, the two builds'
times). Then `machinome viewer capture`, the bench venv on the PATH, on a
fresh copy of 1.5's staging for each of the five option sets
(`<scratch>/10.1-captures.txt`, `<scratch>/pixels.py`):

| set | options | exit | time | against 1.5's image | staging after the capture |
|---|---|---|---|---|---|
| 1 | (none) | 0 | 2.86 s | 0 of 2073600 pixels differ; `b46f77a49af6…` byte-identical | identical to 1.5's (`diff -rq`) |
| 2 | `--view=-80,60,40,0,0,0` | 0 | 3.01 s | 0 differ; `690121f6467f…` byte-identical | identical |
| 3 | `--view=-80,60,40,0,0,0 --up 0,1,0 --fov 30` | 0 | 4.08 s | 0 differ; `8d397810b875…` byte-identical | identical |
| 4 | `--fov 30 --imgsize 800x600` | 0 | 1.48 s | 0 of 480000 differ; `2b4e094d14a3…` byte-identical | identical |
| 5 | `--time 0.25` | 0 | 2.58 s | 0 differ; `b46f77a49af6…` byte-identical | identical |

And on a copy of the fresh staging, no option: exit 0, byte-identical to
1.5's set 1, the staging directory still there. Looked at
(`<scratch>/after/contact-after.png`): the same six pictures as
`<scratch>/base/contact-base.png`, the counter framed whole, from the
requested eye, up the Y axis at 30 degrees, 800 x 600.

### 10.2 Serving gear-shift (task 10.2)

A fresh copy of gear-shift at f3c79c2 (`git archive HEAD`,
`<scratch>/after/gear-shift`), built with `machinome build` (exit 0, 17.3 s),
served by `machinome viewer serve --build-dir <scratch>/after/gear-shift/_build
--port 8793` and opened in Chromium with `probe_gs_page.py`
(`<scratch>/10.2-gs-page.txt`):

```
after: listening after 10.2s total; console ['warning']; exit 0
```

`<scratch>/after/gs-after.png` against 1.5's `gs-base.png`: 41834 of 1024000
pixels differ, all inside the box (552, 286, 1111, 791), design.md probe 11's
box; looked at side by side (`<scratch>/after/contact-gs.png`): the same
gearbox, sidebar with its five subassemblies, time slider and camera, the
crank and the slider at another instant of the model's animation.
`probe_serve.py` (`<scratch>/10.2-serve-signals.txt`): SIGINT, listening after
539 ms, `/_viewer` available with API 29, `viewer.json` `8f656a301326` and the
page `f4a78266072d` (1.5's bytes), the socket greeting `'reload'`, exit 0
after 207 ms; SIGTERM, listening after 496 ms, the same bytes, exit -15
after 165 ms. Afterwards `ss -ltn` shows no listener on 8793 and no
`machinome viewer serve` process is left.

The served process logs seven of uvicorn's eight lines: "Uvicorn running on
http://0.0.0.0:8793 (Press CTRL+C to quit)", which `machinome-viewer serve`
printed at 1.5, is absent. uvicorn 0.30.6's `Server.startup` logs that line
only when it binds the socket itself (`if sockets is None:
self._log_started_message(listeners)`), and the seam's landed `Session`
binds the port before the thread starts and hands uvicorn the socket. The
proposer's probe 6 ran on the seam's prototype, whose session let uvicorn
bind, and recorded eight lines; design.md Decision 4 ("The server logs
uvicorn's lines on standard error as today") does not hold for that line.
`machinome develop`, through the same session, omits it as well since the
seam. Reported to the orchestrator, not changed here.

A port already taken (`<scratch>/port_taken.py`, a socket bound and
listening on `0.0.0.0:8794`; 8793 was still in TIME_WAIT,
`<scratch>/10.2-port-taken.txt`):

```
exit 1 after 0.70 s; stdout ''
stderr:
Error: the web viewer cannot serve on port 8794: Address already in use
Error lines: 1
```

No listener on 8794 and no serve process afterwards.

### 10.3 The studio reads the report (task 10.3)

```
$ env -C <scratch> python -c "from machinome.studio.preparation import resolve_viewer_bundle; \
      print(resolve_viewer_bundle(['<bench>/.venv/bin/machinome']))"
ViewerBundle(path=PosixPath('<bench>/packages/machinome-viewer/machinome/viewer/web/widget/dist/machinome-viewer.js'), api_version=29)
```

(`<scratch>/10.3-studio.txt`.)

## 11. Stopped for review (task 11.1)

Stopped on 12 October 2026 before any commit, archive, ADR promotion or plan
entry. Departures from the design, each recorded above: the served process
logs seven of uvicorn's eight lines (10.2), the seam's session binding the
port itself; the framework changelog's `join-viewer` bullet and the upgrading
page's first 0.9 subsection lose their words on the former command in place
(7.3, 8.1); `server.py`'s comment on the three flags rewritten (5.2);
`test_viewer_report.py` extended without a red run of its own (4.2). Tasks
11.2 to 11.4 remain, on the orchestrator's message.

## 12. The address line (after the review)

The orchestrator's review on 12 October 2026 kept departures 2 to 4 and
asked a fix for the first (10.2): since the seam's `Session` binds the port
itself, uvicorn prints no "Uvicorn running on http://..." and a maker
running `machinome viewer serve` or `machinome develop` sees no address. The
session now prints one line of its own once the server listens, `Serving at
http://HOST:PORT (Ctrl+C to stop)` on standard output; nothing else of the
logging changes.

### 12.1 Red

`packages/machinome-viewer/tests/test_session.py` gains
`TheAddressIsPrintedTest` (2): standard output redirected, `web.serve` on a
free port holds exactly `Serving at http://0.0.0.0:<port> (Ctrl+C to
stop)\n` when `serve` returns, the page answers, and nothing more is printed
until `stop()`; a port another socket listens on raises `ViewerError` and
prints nothing. The module's docstring says so.

```
$ env -C <bench>/packages/machinome-viewer python -m pytest -q -p no:cacheprovider tests/test_session.py
1 failed, 6 passed, 9 warnings in 1.51s                          (<scratch>/12-session-red.out)
E       AssertionError: '' != 'Serving at http://0.0.0.0:41311 (Ctrl+C to stop)\n'
```

The taken-port test is green at the base (nothing was printed before either).

### 12.2 Green

`packages/machinome-viewer/machinome/viewer/web/session.py`: `start()`, once
`server.started`, prints `f'Serving at http://{HOST}:{self.port} (Ctrl+C to
stop)'` with `flush=True` before returning the session, with a comment on why
(uvicorn's `Server.startup` calls `_log_started_message` only when it binds
the socket itself); its docstring states the line and that a refusal prints
nothing.

```
$ ... tests/test_session.py
7 passed, 9 warnings in 1.37s                                     (<scratch>/12-session-green.out)
$ env -C <bench>/packages/machinome python -m pytest -q -p no:cacheprovider \
      tests/test_manager_viewer.py tests/test_manager_develop.py tests/test_viewer_seam.py
100 passed, 69 subtests passed in 3.82s                           (<scratch>/12-core-modules.out)
$ env -C <bench>/packages/machinome-viewer python -m pytest -q -p no:cacheprovider \
      tests/test_session.py tests/test_server.py tests/test_cli.py
27 passed, 21 warnings, 3 subtests passed in 6.01s                (<scratch>/12-viewer-modules.out)
$ flake8 --max-line-length=89 session.py tests/test_session.py
(nothing)
```

These module runs were made while the orchestrator's own validation ran on
the bench, as its message allowed; the whole suites were not rerun here. The
viewer's module count is 252 tests with this change's two, against 9.2's
250 (not run as a whole).

### 12.3 By hand

`<scratch>/address_line.py` starts a command, waits for `/_viewer`, sends
SIGINT and reads its standard output (`<scratch>/12-by-hand.txt`):

```
machinome viewer serve --build-dir <scratch>/after/gear-shift/_build --port 8795
exit 0; stdout lines matching "Serving at": ['Serving at http://0.0.0.0:8795 (Ctrl+C to stop)']; "Uvicorn running" in stderr: False
```

`machinome develop` in the gear-shift copy (`MACHINOME_PORT=8796`,
`<scratch>/develop_interrupt.py`, output to a file): the same line, `Serving
at http://0.0.0.0:8796 (Ctrl+C to stop)`. One SIGINT sent to the develop
process alone left it alive after 30 s (its builder's `multiprocessing`
child is not signalled, and the `atexit` join waits on it; a second SIGINT
ended it, exit 0), and the same happened with the session as the seam left
it, `session.py` restored from `HEAD` for that run and put back after
(`<scratch>/12-develop-with-line.txt`, `<scratch>/12-develop-base-session.txt`):
the seam's behaviour of a lone signal, not this line's. Sent to the process
group, as a terminal's Ctrl+C is (`os.killpg`, the process started in a new
session): exit 0 0.67 s after one SIGINT, the line printed
(`<scratch>/12-develop-group-sigint.txt`). No listener and no develop
process left afterwards.

### 12.4 Records of the line

The line is stated where serving is: the `cli` delta's serve bullet and its
scenario "Serving until interrupted" (title kept), the `viewer-seam` delta's
"The web viewer runs in the framework's process", `reference/viewer/cli.rst`
(serve's paragraph, `machinome develop` printing the same line), ADR-196
(the paragraph "The address"), the viewer's `development-server` spec (the
scenario "A framework launches the server beside its builder"), the viewer's
`CHANGELOG.md` bullet, the manual's changelog bullet and `HISTORY.rst`'s
bullet. `openspec validate viewer-command --strict`: valid.

Departure 1 of 11.1 is closed: both commands show the address again, in the
session's words rather than uvicorn's.

## 13. The records' closing (tasks 11.2 to 11.4)

Resumed on the orchestrator's message of 12 October 2026, after its own
validation run on the bench (`C11-join/validate.sh`: `make test
PKG=machinome`, `make test PKG=machinome-viewer`, `make docs`, `make check`)
had ended (waited on with `pgrep -f "C11-join/[v]alidate.sh"`, ended 23:27);
no red reported by it.

### 13.1 ADR-196 (task 11.2)

`docs/adrs/BUILD/ADR-196-the-viewer-s-verbs-are-the-framework-s-viewer-command.md`:
Status Accepted, its change link the archive's; `docs/adrs/README.md`
"**Accepted**, amends 188/194, cites 024/189/193". ADR-188's and ADR-194's
status lines name the amendment (8.3).

### 13.2 The sync and the archive (tasks 11.3, 11.4)

```
$ env -C <bench>/packages/machinome openspec archive viewer-command -y
Proposal warnings in proposal.md (non-blocking):
  ⚠ Why section should not exceed 1000 characters
Task status: 41/42 tasks
Specs to update:
  cli: update
  cli-startup-cost: update
  framework-identity: update
  user-documentation: update
  viewer-distribution: update
  viewer-seam: update
Totals: + 1, ~ 7, - 0, → 0
Specs updated successfully.
Change 'viewer-command' archived as '2026-10-12-viewer-command'.
```

(`<scratch>/11.4-archive.out`; the open task is 11.5, not the applier's.)
By hand, the Purposes: `viewer-seam`'s names the capture request's two
forms, `machinome viewer` reading no manifest, ADR-196 and
`machinome/manager/viewer.py`; `cli`'s code line names
`machinome/manager/viewer.py` among the commands. The Purposes of
`cli-startup-cost`, `framework-identity` and `user-documentation` are the
CLI's placeholders from their first archives, as before this change, and
were left.

```
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 51 passed, 0 failed (51 items)                            (<scratch>/11.3-validate-specs.out)
$ env -C <bench>/packages/machinome openspec validate --all --strict
Totals: 51 passed, 0 failed (51 items)                            (<scratch>/11.4-validate-all.out)
```

The baseline specs now spell `machinome-viewer describe|serve|capture`
nowhere but in the `user-documentation` scenario that forbids the spelling.

### 13.3 After the close

```
$ env -C <bench>/packages/machinome python -m pytest -q -p no:cacheprovider \
      tests/test_docs_structure.py tests/test_release_records.py tests/test_profile_documentation.py \
      tests/test_repository_layout.py tests/test_viewer_documentation_links.py \
      tests/test_production_documentation.py tests/test_frame_precision_docs.py \
      tests/test_missing_source_file.py tests/test_mates.py tests/test_manager_viewer.py \
      tests/test_viewer_seam.py tests/test_cli_lazy_imports.py tests/test_machinome_identity.py \
      tests/test_viewer_report.py
406 passed, 7669 subtests passed in 18.99s                        (<scratch>/13-records-core.out)
$ env -C <bench>/packages/machinome-viewer python -m pytest -q -p no:cacheprovider
252 passed, 2 skipped, 63 warnings, 191 subtests passed in 252.62s   (<scratch>/13-viewer.out)
$ env -C <bench> make docs
The HTML pages are in docs/_build/html.                           exit 0 (<scratch>/13-docs.out)
```

The viewer's 252: 9.2's 250 and `TheAddressIsPrintedTest`'s two. The core's
whole suite was not rerun after 12 (the fix touches the viewer's session and
records; the core modules that serve through it ran in 12.2, the records'
tests here). `make check` was not rerun after 12; 9.4's archives predate the
address line.

### 13.4 The orchestrator's step, recorded

The Curta's eleven browser tools under `simulation/tools/`, which ran
`[sys.executable, '-m', 'machinome_viewer', 'describe']`, now run `'-m',
'machinome.viewer.web', 'describe'`, the module form this change keeps for
tools: one commit, f4a7005, in that repository on 12 October 2026 ("Ask the
viewer's report through machinome.viewer.web"), nothing of the former
module left under its tools. No other project ran the script or the module
(design.md probe 14). The site's intake (three files in the site's
repository) is held for the pilot. No universe sweep: nothing a project
imports moved.

### 13.5 The plan

`workflow/ongoing/release-0.9.md`, Progress: entry 4, `viewer-command`,
written as entries 1 to 3 are.
