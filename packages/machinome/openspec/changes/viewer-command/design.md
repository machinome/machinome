## Context

The pilot's fourth decision for Machinome 0.9 (`workflow/ongoing/release-0.9.md`
at the repository root, 12 October 2026) makes `machinome` one command and
gives the viewer's command a cycle of its own before the bump: the framework's
`viewer` command grows the viewer's verbs and dispatches to the installed
provider through the seam, since a framework name is never taken by a
contributor (ADR-189); unifying anything beyond that is deferred. The first
decision bounds it: no module of a former name is provided, and no alias.

This design is written against the line `v0.9-joins` as it will be at this
cycle's planning commit: feb1b46e (the viewer's, the movie's and the skills'
joins, the command seam and `release-tooling`), then `join-studio` (being
implemented on its bench: `machinome.studio`, whose hub runs `machinome viewer`
and reads its report), then `viewer-seam` (ratified, not yet implemented: the
seam `machinome.viewer` with `CONTRACT = 1`, `viewer()`, `require()`,
`chosen()`, the Protocols and `CaptureRequest`; the web provider
`machinome.viewer.web` serving in a session it owns and capturing in the
caller's process; `machinome viewer` printing `require('web', 'embed',
'machinome viewer').describe()`; the entry-point group and the subprocess
removed). The seam's Decision 15 lists what it leaves to this cycle: the verbs
`describe`, `serve` and `capture` under `machinome viewer`, dispatching through
the seam; the fate of the console script `machinome-viewer` and of `python -m
machinome.viewer.web`; the reference page `reference/viewer/cli.rst`; the
studio's and the site's readings if the report's shape changes. Where a
sentence below depends on the seam's implementation it says so; the applier
re-reads the landed text before editing it.

The orchestrator made these reversible decisions, flagged to the pilot:
`machinome viewer` with no verb keeps printing what it prints today, byte for
byte; the verbs come beside it with the options the viewer's command has, each
dispatching through the seam to the viewer the default rule names, `--viewer
<name>` choosing another, a verb the chosen viewer lacks refused by name; the
console script goes; `python -m machinome.viewer.web` stays as the provider's
own entry, its `__main__.py` unchanged. This design follows them, with one
departure carried as Open Questions 7 (serve's three deprecated flags) and one
precision carried as Open Questions 8 (the verbs read no project manifest).

Paths below are the framework directory's (`packages/machinome/`) unless they
start with `packages/` or name a root file. The probes ran in the scratch
directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C11-propose/`
(written `<scratch>`). The base is the bench's venv (`uv sync --python 3.12`
from the lock at feb1b46e) running today's code. The prototype is
`<scratch>/tree`, a copy of the seam's prototype (`C9-propose/tree`, read only,
copied without its venv) with a venv synced from its lock (exit 0), into which
this design's `manager/viewer.py`, the web provider's `capture` reading the
camera's parts and, for probe 9 only, the reduced `cli.py` were written.
Nothing was written in the bench but this change's planning artifacts. Tools:
uv 0.11.8, CPython 3.12.3, Playwright's Chromium headless shell 1243, the
OpenSpec CLI 1.6.0.

### Today's commands

| command | prints | exit |
|---|---|---|
| `machinome viewer` | one JSON object: `path`, `index`, `apiVersion`, `documentVersions`, `version` | 0; 1 with the remedy on standard error |
| `machinome viewer describe` | "unrecognized arguments: describe" | 2 |
| `machinome viewer -h` | `usage: machinome viewer [-h]` | 0 |
| `machinome-viewer describe`, `python -m machinome.viewer.web describe` | the same bytes as `machinome viewer` | 0 |
| `machinome-viewer` (no verb), `-h` | its help: `describe`, `serve`, `capture` | 0 |
| `machinome-viewer serve --build-dir DIR [--port N] [--dev] [--frontend-port N] [--start-frontend]` | uvicorn's lines on standard error | 0 on Ctrl-C; killed by a termination signal; 1 when the port is taken; 2 without `--build-dir` |
| `machinome-viewer capture STAGING -o PNG [--imgsize WxH] [--time T] [--view EYE,TARGET] [--up X,Y,Z] [--fov DEG]` | nothing | 0; 1 "Error: Staged document not found: …/viewer.json"; 2 "Error: --time must be between 0.0 and 1.0, got 2.0" |

### Probes

1. **Today's commands** (`<scratch>/probe-01-today.txt`). The table above,
   run with the base: `machinome viewer`, `machinome-viewer describe` and
   `python -m machinome.viewer.web describe` byte-identical
   (`<scratch>/report-*.json`), the five keys in that order; `machinome viewer
   describe` exit 2; every help, usage error and refusal of the table recorded
   verbatim.
2. **A staged document** (`<scratch>/stage_keep.py`, `probe-02-stage.txt`).
   The base's `machinome snapshot --renderer web --drive crank=3580` on a copy
   of `docs/tutorial` (model `c09`), the staging directory copied aside before
   the snapshot removed it (`<scratch>/staged`: `viewer.json`, the four STLs and
   the marking under `counter/`, and the page and bundle the capture wrote);
   the image `base-carry-web.png`, SHA-256 `b46f77a4…`, the seam's probe 4's
   `carry-web` hash.
3. **Capture through the verb** (`probe-03-capture.txt`). On fresh copies of
   the staging, the base's `machinome-viewer capture` and the prototype's
   `machinome viewer capture` with the same options, five pairs: no option;
   `--view=-80,60,40,0,0,0`; the same with `--up 0,1,0 --fov 30`; `--fov 30
   --imgsize 800x600`; `--time 0.25`. Each pair 0 differing pixels and
   byte-identical (SHA-256 `b46f77a4…`, `690121f6…`, `8d397810…`, `2b4e094d…`,
   `b46f77a4…`), the staging directories identical after the capture (`diff
   -rq`), times 1.2 to 3.7 s each way. The images were looked at
   (`contact-capture.png`): the counter on its base with the drum's digits and
   the crank, framed whole; then from the requested eye; then up the Y axis.
4. **The camera's notation is not the viewer's command**
   (`probe-04-notation.txt`). The web provider asked with `camera =
   "-80,60,40,0,0,0"`, the `--camera` notation of the same eye and target:
   1667868 pixels of 2073600 differ from `--view=-80,60,40,0,0,0`'s image. The
   notation resolves the field of view to `DEFAULT_FOV`, 22.5 degrees, and the
   viewer's own default is 50; `--up` and a lone `--fov` have no notation at
   all. A request that carries only the notation cannot reproduce the viewer's
   command (Decision 3).
5. **The verbs' outputs** (`probe-05-verbs.txt`). With the prototype:
   `machinome viewer`, `machinome viewer describe` and `python -m
   machinome.viewer.web describe` byte-identical, with the base's keys, order
   and values but the two paths, which name each tree's widget; `describe
   --viewer openscad` "machinome viewer describe needs a viewer that can embed,
   and the openscad viewer cannot", exit 1; `serve --viewer openscad` the same
   with serve; `capture --viewer openscad` "… a viewer that can photograph a
   published document, and the openscad viewer cannot", exit 1, no image;
   `describe --viewer povray` "no viewer is named 'povray'; the viewers are
   openscad, web", exit 1; `machinome viewer -h` listing the three verbs;
   `capture -h` the base's options and `--viewer NAME`; `serve` without
   `--build-dir` exit 2; `capture --time 2` exit 2 with the base's line; a
   missing staging exit 1 with the base's line; an unknown verb exit 2.
6. **Serve through the verb** (`probe_serve.py`, `probe-06-serve.txt`,
   `probe-06b-serve-sigterm.txt`). The base's `machinome-viewer serve` and the
   prototype's `machinome viewer serve` on the tutorial's build
   (`<scratch>/tut/_build/c09`), each started twice, from outside: listening
   after 465 to 844 ms (base) and 339 to 572 ms (prototype, both probes); `/_viewer`
   available with API 29; `/build/viewer.json` and the page byte-identical
   (`aa5d4314…`, `f4a78266…`); the reload socket greeting `reload`; uvicorn's
   eight lines on standard error, the same; SIGINT exit 0 in 169 to 251 ms.
   On SIGTERM the base exits -15 after uvicorn's shutdown lines (uvicorn
   re-raises the signal it caught); the prototype, stopping its session and
   then re-raising the signal with the default action, exits -15 in 168 ms.
   No listener and no process left (`ss -ltn`, `pgrep`).
7. **The verbs' cost** (`probe-07-help-cost.txt`, six alternating rounds on
   the prototype, the seam's `manager/viewer.py` against this design's):
   `machinome -h` median 640 and 607 ms, 1029 modules each; `machinome viewer
   -h` 44 and 43 ms, 80 and 81 modules; `machinome viewer` 82 and 81 ms, 169
   modules each. The verbs cost nothing measurable (ADR-189's measure).
8. **The verbs' imports** (`probe-08-imports.txt`). `machinome viewer` and
   `machinome viewer describe` import the web provider and none of fastapi,
   uvicorn, playwright, the viewer's server, capture, session or staging, or a
   CAD library; `machinome viewer -h` and `machinome viewer capture -h` import
   no provider. `machinome -h` imports `trimesh` at the base and in the
   prototype alike (1027 modules at the base), not through this command.
9. **The module entry runs the framework's command**
   (`probe-09-module-entry.txt`). `cli.py` reduced to a `main(argv)` running
   the framework's `Viewer` class with its own parser: `python -m
   machinome.viewer.web describe` byte-identical to `machinome viewer`; with no
   verb it prints the report; `capture --view=…` byte-identical to probe 3's
   (`690121f6…`); `serve --start-frontend` exit 2, "unrecognized arguments".
10. **A port already taken** (`probe-10-serve-port-taken.txt`). With a socket
    listening on the port, the base's serve exits 1 in 497 ms after uvicorn's
    "[Errno 98] … address already in use"; the seam's prototype session
    returns from `start()` once the thread has died, and the prototype verb
    then waited until killed after 20 s. The seam's Decision 7 already requires
    `serve()` to raise when the server fails to start; this cycle's verb test
    pins the exit 1 (Decision 4).
11. **Gear-shift in Chromium** (`probe_gs_page.py`, `probe-11-gearshift.txt`,
    `contact-gs.png`). `Vibecoded-demos/gear-shift` at f3c79c2, copied by `git
    archive`, built with the prototype (exit 0, 11.5 s); served by each command
    and opened at 1280 x 800 in headless Chromium for 8 s: the same gearbox,
    the assembly sidebar with its five subassemblies and the time slider, from
    the same camera; 39345 pixels differ inside the gears' box (552, 286, 1111,
    791), the model running its animation; each command exit 0 on SIGINT.
12. **What spells the console script and the module entry**
    (`probe-12-script-uses.txt`, `git grep` in the bench, records under
    `archive/`, `releases/`, `workflow/` and the ADRs left out): the viewer's
    manifest (the `[project.scripts]` table, two lines) and its identity test
    (one assertion); `scripts/check-dist`'s viewer row (one line); four manual
    pages (`reference/viewer/cli.rst` four lines, `compatibility.rst`,
    `troubleshooting.rst`, `howto/share-an-export.rst` one each) and
    `reference/cli.rst`'s `--debug-builder` line; `context7.json` (one line);
    the viewer's docstrings (`__main__.py`, `bundle.py`, `capture.py`), its
    `CHANGELOG.md`'s `Unreleased` bullet, its OpenSpec `config.yaml` (one line)
    and its specs (`development-server` two lines, `snapshot-capture` one,
    `user-documentation` two, `viewer-distribution` thirteen); the framework's
    specs `framework-identity` (one scenario) and `user-documentation` (one
    requirement). `develop.py`'s `--start-frontend` and `browser.py`'s
    docstring, and the framework's `viewer-distribution` lines, are removed by
    the seam. The Makefile names no script.
13. **A listing of the installed viewers** (`probe-13-installed.txt`). An
    optional `--installed` on `machinome viewer` leaves the bare report
    byte-identical and lists `openscad capture present` and `web capture embed
    present serve`. It can be added later without changing the default output
    (Open Questions 3).
14. **The readers** (`probe-14-readers.txt`, read only). The studio
    (`join-studio`'s bench, d291bc8b) runs `machinome viewer` with no verb and
    reads `path` and `apiVersion` (`preparation.py`, `resolve_viewer_bundle`);
    its shop skills name the report; no module runs the console script. The
    site (`machinome.org` at 7c74167) runs `<workspace>/.venv/bin/machinome-viewer
    describe` in its intake (`src/machinome_site/intake_viewer.py`, line 56 and
    61; `tests/test_intake_viewer.py`, which writes a fake script by that name
    at lines 99 and 235; `docs/building.md`, line 144). The workspace's
    `AGENTS.md`, line 409, names the three commands. In the 87 project
    repositories (`git grep` of each checked-out branch): one dated note of the
    Curta (`simulation/docs/source-timing-integration-2026-09-22.md`, line 25)
    names `machinome-viewer describe`, and eleven tools of the Curta
    (`simulation/tools/*.py`, branch `main` at 6ad3a38) run `[sys.executable,
    '-m', 'machinome_viewer', 'describe']`, the module of the former name,
    which no installation of the line provides since `join-viewer`; no project
    spells `python -m machinome.viewer.web` or `machinome-viewer serve` or
    `capture`.

## Goals / Non-Goals

**Goals:**

- One command: the viewer's verbs are `machinome viewer describe|serve|capture`,
  dispatched through the seam, and the viewer's distribution installs no
  executable of its own.
- `machinome viewer` with no verb prints what it prints today, byte for byte.
- The verbs give what the viewer's command gave: the same report, the same
  served pages, the same images, the same exit statuses (probes 3, 5, 6).
- A verb a viewer cannot perform is refused by name, never substituted.

**Non-Goals:**

- A listing of the installed viewers (Open Questions 3).
- Unifying `machinome viewer serve` with `machinome develop`, or `machinome
  viewer capture` with `machinome snapshot` (the pilot's "unifying anything
  beyond that is deferred").
- Changing the report's shape, the viewer's API (29) or its document versions
  (1 to 13).
- The site's intake, the workspace's contract and the Curta's tools, which live
  in other repositories (Decision 13).

## Decisions

### 1. The command's shape

`machinome viewer` keeps `needs_node = False` and gains an optional verb, an
argparse subparser group `dest='verb'` titled "Verbs":

```
machinome viewer
machinome viewer describe [--viewer NAME]
machinome viewer serve --build-dir DIR [--port N] [--viewer NAME]
machinome viewer capture STAGING -o PNG [--imgsize WxH] [--time T]
                         [--view EYE,TARGET] [--up X,Y,Z] [--fov DEG]
                         [--viewer NAME]
```

- With no verb: `require('web', 'embed', 'machinome viewer').describe()` as
  JSON, the seam's `handle` unchanged; it takes no option, so nothing can
  change its bytes (probe 5).
- `describe`: the chosen viewer's `describe()`, the same JSON.
- `serve` and `capture`: Decisions 3 and 4. Their options are the viewer's
  command's, with its help strings, metavars, defaults and parsers (`_imgsize`,
  `_view`, `_triple` move from the viewer's `cli.py` into
  `manager/viewer.py`), less serve's three deprecated flags (Open Questions 7).
- `--viewer NAME` on each verb, default `web` (Decision 2).
- The command's docstring, its help in `machinome -h`: "Reports the installed
  viewer as JSON, and serves or photographs through a viewer".

The module imports at its top only the standard library (`argparse`, `json`,
`sys`); the seam is imported in `handle`, as the seam's version does, so `-h`
loads no viewer (probes 7 and 8).

Rejected: `--viewer` before the verb (`machinome viewer --viewer web serve`),
which would also offer it to the bare report, whose bytes must not depend on
an option; verbs as separate framework commands (`machinome viewer-serve`), a
second naming scheme beside the contributed commands' verbs.

### 2. The dispatch through the seam

Each verb names the operation it needs and asks the seam:

| verb | operation | the provider's call |
|---|---|---|
| `describe` | `embed` | `describe()` |
| `serve` | `serve` | `serve(build_dir, port)` then the session's `stop()` |
| `capture` | `capture`, and a viewer that reads published documents | `capture(staging, request, output)` |

`require(name, operation, f'machinome viewer {verb}')` resolves the viewer;
its refusals (`ExtraUnavailable`, `UnknownViewer`, `ViewerIncompatible`,
`ViewerLacks`) are written on standard error as the seam's words, nothing on
standard output, exit 1 (probe 5). `capture` also refuses a viewer whose
`document_versions()` is `None`: the staging directory holds a published
document (`viewer.json`), which a viewer reading no document cannot
photograph; the refusal is the seam's `ViewerLacks` sentence with the
operation "photograph a published document" and the viewers that can, computed
as the seam computes them. The OpenSCAD viewer offers `capture`, of a node it
presented, so without this check `machinome viewer capture --viewer openscad`
would hand it a directory.

The name is `--viewer`, else `web`. The command reads no project manifest:
it takes no node path, the studio and the site run it from wherever they are,
and a project's `[tool.machinome] viewer = "openscad"` would otherwise make
`machinome viewer describe` refuse inside that project and answer outside it.
The `viewer-seam` requirement on the default rule gains `machinome viewer`
beside the documentation build and the films, which read no manifest either
(Open Questions 8). No availability is consulted and nothing is substituted.

The bare report keeps the seam's `needed_by`, `machinome viewer`; a verb's
refusal names the verb (`machinome viewer serve needs a viewer that can
serve, …`).

### 3. `capture`, and the camera's parts in the seam's request

`machinome viewer capture STAGING -o PNG` photographs the published document in
`STAGING`, as `machinome-viewer capture` did:

- `--time` outside [0, 1] is "Error: --time must be between 0.0 and 1.0, got
  <t>", exit 2, before the viewer is resolved (today's line and status).
- The request: `CaptureRequest(imgsize=…, time=…, eye=…, target=…, up=…,
  fov=…)`, each camera part `None` when its option is absent.
- `provider.capture(STAGING, request, output)`; a `ViewerError` is "Error:
  <message>", exit 1, no image (probe 5's missing staging: the web viewer's
  `CaptureError` text, carried by the seam's `ViewerError`).
- The staging directory is never withdrawn: it is the caller's directory, not
  one the command presented, and the web viewer's `withdraw` removes what it is
  given. The capture adds its page and bundle to it, as today (probe 3: the
  directories identical after both commands).

The seam's `CaptureRequest` (seam Decision 1) is a frozen dataclass of the
snapshot's options with `camera`, the `--camera` notation. This change gives it
four fields more, `eye`, `target`, `up` and `fov`, default `None`, the parts of
`machinome.core.camera.Camera` by the same names, and a `__post_init__` that
raises `ValueError` when `camera` and any part are both given. The web
provider's `capture` resolves `camera` into the four parts with
`parse_camera`, as the snapshot's web path does today; otherwise it takes the
parts as given; then `mount_options(time, view=(eye, target) if eye else None,
up=up, fov=fov)`, a part left `None` being the viewer's own default (fit the
model, Z up, 50 degrees). The snapshot keeps passing `camera` alone, so its
pixels are the seam's. The OpenSCAD provider is never given parts: `machinome
viewer capture` refuses it (Decision 2), and the snapshot passes the notation.

Probe 4 is why: the notation fixes the field of view at 22.5 degrees and has
no spelling for an up vector or a lone field of view, so a request of the
notation alone changes `--view`'s image (1667868 differing pixels). With the
parts, five option sets give byte-identical images (probe 3).

Rejected: the verb taking `--camera` in place of `--view`, `--up` and `--fov`,
one camera spelling across the command (it would change the image of every
`--view` without `--fov` and drop `--up`, against the orchestrator's "the
options the viewer's command has"); a `Camera` whose parts may be `None`,
which changes a class the snapshot and the OpenSCAD viewer read.

### 4. `serve`

`machinome viewer serve --build-dir DIR [--port N]`:

- `session = provider.serve(DIR, port=N)`; `N` absent, the provider's default,
  `MACHINOME_PORT` or 8000, as today. The server logs uvicorn's lines on
  standard error as today (probe 6).
- The command then waits in the main thread until interrupted. Ctrl-C
  (`KeyboardInterrupt`) calls `session.stop()` and returns: exit 0. SIGTERM:
  a handler installed for the wait stops the session, restores the default
  action and re-raises the signal, so the process ends by SIGTERM (-15) as
  uvicorn's own handling ends it today (probe 6).
- A server that cannot listen: the seam's `serve()` raises (seam Decision 7,
  now stated in the `viewer-seam` requirement this change modifies); the
  command writes "Error: <message>" and exits 1, as today uvicorn's error line
  and exit 1 (probe 10). The test pins it against a socket bound
  on the port, so the seam's prototype's hang (probe 10) cannot pass.
- `--build-dir` required, as today (exit 2 without it).

The session's `reload()` is not used: nothing in this command rebuilds; a
host that republishes the directory reloads its own page, as with today's
command, whose socket only greeted.

### 5. The report, and its readers

`machinome viewer` with no verb is the seam's handle, unchanged: one JSON
object, the five keys in today's order, nothing on standard output on a
refusal, exit 1. `machinome viewer describe` prints the same bytes for the web
viewer (probe 5). The readers keep working with no change: the studio runs
`machinome viewer` and reads `path` and `apiVersion`; `machinome movie` asks
the seam (seam Decision 7); the site reads the same object, through the
console script today (Decision 13).

### 6. The console script goes

`packages/machinome-viewer/pyproject.toml` loses `[project.scripts]
machinome-viewer = "machinome.viewer.web.cli:main"`. No alias is provided
(the pilot's first decision; the studio's join dropped `machinome-studio` the
same way). A wheel of the viewer then installs no executable; `machinome
viewer <verb>` and `python -m machinome.viewer.web <verb>` replace it. What
this reaches is probe 12's list, each edited in this cycle but the site's
three files and the workspace's line (Decision 13).

### 7. `python -m machinome.viewer.web`, and the viewer's `cli.py`

`__main__.py` is unchanged: `from machinome.viewer.web.cli import main;
sys.exit(main())`. `cli.py` is reduced to what that line needs:

```python
def main(argv=None):
    """`python -m machinome.viewer.web`: the framework's `machinome viewer`,
    run by this interpreter with the same parser."""
    import argparse
    from machinome.manager.viewer import Viewer
    parser = argparse.ArgumentParser(prog='machinome viewer')
    command = Viewer()
    command.add_arguments(parser)
    command.handle(parser.parse_args(argv))
    return 0
```

the shape of `python -m machinome.movie` (`packages/machinome-movie/machinome/
movie/__main__.py`). One parser serves both spellings, so they cannot drift;
`build_parser`, `run_describe`, `run_serve`, `run_capture`, `COMMANDS`,
`FRONTEND_FLAG_NOTICE` and the three parsers go (the parsers to
`manager/viewer.py`). The module form now prints the report with no verb, where
it printed its help, and refuses `--dev`, `--frontend-port` and
`--start-frontend` (probe 9). The provider imports the framework's command
module only inside `main`, so resolving the provider through the seam still
imports nothing of it.

Rejected: keeping `cli.py` whole as the module entry's own implementation (two
parsers and two code paths for the same three verbs, the module one serving in
uvicorn's main thread and the command's in the provider's session); the
framework's command calling the viewer's `cli.py` (the core would name a
provider's module, which the seam forbids, and the verbs would not go through
the seam).

### 8. The cost

`machinome -h` lists `viewer` with its new docstring and constructs its class,
as before; `machinome viewer -h` builds the verbs' parsers. Probe 7: within
noise (607 against 640 ms, 43 against 44 ms; one module more, 81 against 80).
The `cli-startup-cost` requirement on the viewer command gains the verbs' help
and `describe` (probe 8).

### 9. The core of the set

- **`scripts/check-dist`**, the `machinome-viewer` row (as the seam leaves it):
  its `commands` become `[['machinome', 'viewer'], ['machinome', 'viewer',
  'describe'], ['python', '-m', 'machinome.viewer.web', 'describe']]`; its code
  asserts that the distribution declares no entry point in the group
  `console_scripts` and that `Path(VENV) / 'bin' / 'machinome-viewer'` does not
  exist. The rest of the row is the seam's.
- **`context7.json`**: its viewer line's sentence on the process interface
  becomes "Its command is machinome viewer describe|serve|capture; machinome
  viewer alone prints the report." (in place, as the seam leaves the line).
- **The Makefile**: no line names the script; unchanged. The layout gate, the
  extras, the lock and `.bumpversion.cfg`: unchanged.

### 10. The tests, red first

Each run first at the line's head with this change's planning commit, its red
recorded:

| module | change | expected red |
|---|---|---|
| `tests/test_manager_viewer.py` | the parser's verbs and options; the bare report through the seam (a fake provider patched on `machinome.viewer.require`); `describe` the same bytes; each verb's refusal of the OpenSCAD viewer, of an unknown name and of an absent web viewer, nothing on standard output, exit 1; `capture`'s request (parts `None` when absent, as given otherwise), the document refusal, `--time` exit 2 before the viewer is resolved, a `ViewerError` exit 1; `serve`'s call, `stop()` on `KeyboardInterrupt` with exit 0, a `serve()` that raises exit 1 | `Viewer().add_arguments` registers no verb: "invalid choice"/"unrecognized arguments" |
| `tests/test_viewer_seam.py` | `CaptureRequest`'s four parts and the `ValueError` when both forms are given; the web provider's `capture` handing the parts to `mount_options` (its `Capture` patched), `None` left `None`, and the notation resolved | `TypeError: unexpected keyword argument 'eye'` |
| `tests/test_cli_lazy_imports.py` | `machinome viewer -h` and `machinome viewer capture -h` import no provider; `machinome viewer describe` imports no server, capture, session, staging, fastapi, uvicorn, playwright or CAD library and exits 0 | `machinome viewer describe` exits 2 |
| `tests/test_machinome_identity.py` | no distribution of the set but the core declares `[project.scripts]` (every `packages/*/pyproject.toml` read) | the viewer's manifest declares `machinome-viewer` |
| `tests/test_docs_structure.py` | `CommandReferenceTest.test_the_viewer_command_has_its_section` (the label `viewer-command`, the three verbs, every option of the command's parser read from `Viewer().add_arguments`, the link to `/reference/viewer/cli`); `STALE` gains the former command's three spellings, the changelog and the upgrading page allowed to record them | no section; four pages spell the former command |
| a serve test against a real port (`tests/test_manager_viewer.py`, a socket bound first) | exit 1 within 10 s, one `Error:` line | (red only if the seam's `serve()` does not raise; recorded either way) |
| `packages/machinome-viewer/tests/test_machinome_identity.py` | the manifest declares no `scripts` | the scripts table is there |
| `packages/machinome-viewer/tests/test_cli.py` | `cli.main` runs the framework's command: `main(['describe'])` prints the report; `main([])` prints it too; `main(['serve', '--build-dir', 'x', '--start-frontend'])` exits 2; the module entry through the interpreter (kept); the describe, capture and serve tests move to the core's `test_manager_viewer.py` | `main([])` prints help; `--start-frontend` is accepted |
| `packages/machinome-viewer/tests/test_documentation.py` | `test_cli_options_are_all_documented` goes (the core's section test reads the parser); `test_describe_example_matches_package_versions` reads the page as kept (Decision 11) | (removal; the describe test stays green) |

### 11. The manual

- **`reference/cli.rst`**: a section `.. _viewer-command:` / `machinome
  viewer`, after `machinome export` and before `machinome models`, the order of
  `machinome -h`, holding the
  synopsis of Decision 1, a paragraph on the report (no verb and `describe`,
  the keys, exit 1 with nothing on standard output), one on `--viewer` (the web
  viewer by default; the project's `viewer` key is not read; a viewer that
  cannot do the verb is refused by name), `serve`'s and `capture`'s options in
  one sentence each, the exit statuses, and ":doc:`/reference/viewer/cli` says
  what each verb serves, photographs and refuses". `develop`'s
  `--debug-builder` line names `machinome viewer serve --build-dir _build`.
- **`reference/viewer/cli.rst`**: kept (Open Questions 5), retitled "The viewer
  command"; its opening says `machinome viewer` reports and runs the installed
  viewer and `python -m machinome.viewer.web` runs the same command; each
  example spelt `machinome viewer <verb>`; `serve`'s table without the three
  deprecated flags; a line for `--viewer`; the endpoints table, the warning on
  0.0.0.0 and `capture`'s notes unchanged but the sentence "The framework
  development workflow owns republishing and restarting its serving process"
  (the seam's text as landed).
- **`reference/viewer/compatibility.rst`**, **`troubleshooting.rst`**,
  **`howto/share-an-export.rst`**: `machinome viewer describe` and `machinome
  viewer capture` in place of the former spellings; compatibility's "The
  framework exposes its own lookup as ``machinome viewer``" becomes the one
  command's sentence.
- **`project/upgrading.rst`**: in the 0.9 section the seam begins, a
  subsection "The viewer's command": `machinome-viewer describe|serve|capture`
  is `machinome viewer describe|serve|capture`; serve no longer takes `--dev`,
  `--frontend-port` or `--start-frontend`; `python -m machinome.viewer.web`
  runs the same command and prints the report with no verb; a host that ran
  `machinome-viewer describe` runs `machinome viewer`, whose output is the
  same.

### 12. The spec deltas

Modified, each requirement copied whole from the seam's landed text (or the
line's, where the seam does not touch it), scenario titles kept:

- `cli`: "Viewer command" (the seam's): the verbs, `--viewer`, the refusals,
  the request's parts, serve's signals; its four scenarios kept, the identity
  one naming `machinome viewer describe` and the module entry; seven added.
- `cli-startup-cost`: "The viewer command loads no geometry stack" (the
  seam's): `describe` with the report, the verbs' help.
- `viewer-distribution`: "The framework resolves the Machinome viewer" (the
  seam's): no command of the distribution's own, the module entry the
  framework's command; one scenario added.
- `viewer-seam`: "The viewer is chosen by the flag, the project, or the
  command's default" (`machinome viewer` reads no manifest; one scenario
  added) and "The web viewer runs in the framework's process" (the console
  script clause goes; `serve` raises when the server cannot listen, which the
  seam's Decision 7 states and its requirement did not); added: "A capture
  request names its camera by the notation or by its parts".
- `framework-identity`: "The framework is the package directory
  `packages/machinome` of a monorepo" (the seam's): the scenario "The viewer
  is smoked from its wheel" ends with the three commands and no executable of
  the viewer's.
- `user-documentation`: "The browser viewer is documented in the manual" (the
  line's): `machinome viewer` in place of the `machinome-viewer` command, its
  verbs' options read from the framework's command.

`web-snapshot` is not modified: after the seam no requirement of it names the
viewer's command or its process (the seam's `web-snapshot` delta names
neither the console script nor the module form).
`viewer-seam`'s and the other deltas' copies are of the seam's planning text;
if the seam's implementation changes a requirement copied here, the applier
re-applies this change's edits to the landed text before the archive (tasks
1.3).

### 13. Outside the repository

- **The site** runs the removed script in its viewer intake (probe 14): its
  `run_describe` must run `<workspace>/.venv/bin/machinome viewer` (the same
  JSON, so `describe` or no verb), its test's fake executable be named
  `machinome` and answer `viewer`, and `docs/building.md` say so: three files of
  the site's repository, under its own OpenSpec discipline, the pilot's to
  order. Until then the intake refuses with "… machinome-viewer does not exist"
  against a workspace on this line; the site's build does not run it.
- **The workspace's** `AGENTS.md` line 409 names `machinome-viewer
  describe|serve|capture` as the contract between framework and viewer; the
  `workspace-consistency` cycle rewrites it.
- **The projects**: no tracked file runs the console script or `python -m
  machinome.viewer.web`. The Curta's eleven tools run `python -m
  machinome_viewer describe`, a module no installation of this line provides
  since `join-viewer`; their move, to `[sys.executable, '-m',
  'machinome.viewer.web', 'describe']` (the shortest that keeps "the viewer
  beside this interpreter"), is the orchestrator's projects' step, one commit
  on the Curta's `main` if its tree is clean in those files. The dated note is
  recorded evidence and is not rewritten. The universe sweep is not affected:
  no model imports a module this change touches.

### 14. The records

- **ADR-196**, "The viewer's verbs are the framework's `viewer` command"
  (`docs/adrs/BUILD/`), Proposed, Accepted at the archive: the verbs, their
  dispatch through the seam with an operation each, `--viewer` with the web
  default and no manifest, the report unchanged, the console script removed
  with no alias, the module entry running the framework's command, the request's
  camera parts. Amends ADR-188 (its "Its console script `machinome-viewer` …
  keep their names") and ADR-194 (its clause keeping `machinome-viewer` and the
  module form printing what they printed); cites ADR-189 (a framework name is
  never taken), ADR-024 (the command registry) and ADR-193 (the studio's
  console script dropped). Index line in `docs/adrs/README.md`, status lines of
  the two amended ADRs. Open Questions 6.
- **`HISTORY.rst`** and **`docs/project/changelog.rst`**: one `Unreleased`
  bullet each: `machinome viewer describe|serve|capture`, `--viewer`, the report
  unchanged; the `machinome-viewer` command removed; `python -m
  machinome.viewer.web` runs `machinome viewer`.
- **The viewer's `CHANGELOG.md`**: its `Unreleased` bullet that says "the
  `machinome-viewer` command … unchanged" loses those words in place, and a
  bullet says the command is gone and its verbs are `machinome viewer`'s.
- **The viewer's specs** (`packages/machinome-viewer/openspec/specs/`
  `development-server`, `snapshot-capture`, `user-documentation`,
  `viewer-distribution`) and its `openspec/config.yaml`, brought current in
  place where they state the console script (probe 12's nineteen lines), as
  `join-viewer` and the seam brought them current; its decision log untouched.
- **The viewer's docstrings**: `__main__.py` ("the framework's `machinome
  viewer`, through an interpreter"), `bundle.py` and `capture.py` (the command
  named `machinome viewer`).
- **`docs/architecture.md`**: the viewer section's sentence on the command,
  as the seam leaves it: `machinome viewer` reports and runs the verbs through
  the seam; the console script as history.

### 15. Validation and the originating check

- The suite on the bench's venv, one process, against the seam's archived
  count; the viewer's suite from its directory; the movie's and the studio's
  (they read the report); `make lint`; `make docs` (as the seam's Decision 13
  leaves it); `make check` (`scripts/check-dist` on the tree and on a clean
  copy: the viewer row's three commands exit 0 and no `machinome-viewer` in
  the venv's `bin`).
- The originating check, on scratch copies: the tutorial's carry pose staged
  as probe 2 does, on the landed seam (a capture of the snapshot's staging
  kept by the same wrapper on the seam's `withdraw`), then `machinome viewer
  capture` with probe 3's five option sets; each image against probe 3's base
  images (taken with the line's head before this change): 0 differing pixels,
  SHA-256 recorded, each looked at. Then `machinome viewer serve` of a fresh
  build of `Vibecoded-demos/gear-shift` opened in Chromium (probe 11's script),
  the page photographed and looked at, SIGINT exit 0, and SIGTERM exit -15,
  no listener left; and a port already taken, exit 1.
- The studio's hub reads the report: the studio's `resolve_viewer_bundle`
  against the bench's `machinome` (its test with the real command, or one call
  from the bench's venv printing the path and the API).

## Risks / Trade-offs

- [A tool or a host that runs `machinome-viewer` stops working] → probe 14
  finds one, the site's intake, outside the repository, named in Decision 13
  and in the upgrading page; no project and no studio module.
- [`python -m machinome.viewer.web` with no verb prints the report, not its
  help] → no tool runs it bare (probe 14); `-h` still prints the help.
- [The serve verb runs uvicorn in a thread, not in the main thread] → the
  served bytes, the greeting, the log lines and the exit statuses equal
  today's (probe 6); the port-taken exit is pinned by a test against the seam
  (probe 10).
- [Two camera spellings in one request] → the request refuses both at once;
  the snapshot passes one and the capture verb the other; each viewer reads
  what it is given (Decision 3).
- [The verbs reading no manifest differ from `snapshot`, `develop` and
  `export`] → the command takes no node path and acts on the installation and
  on directories it is given, like the documentation build and the films
  (Open Questions 8).

## Migration Plan

1. Planning commit (the orchestrator), after fast-forwarding the bench onto the
   line holding `join-studio` and `viewer-seam`.
2. Implementation on the bench, red first, as tasks.md orders it; nothing
   committed by the applier; the orchestrator's review, then the implementation
   commit.
3. The Curta's tools (Decision 13), the orchestrator's projects' step, if the
   pilot wants them moved now; the site's intake, the pilot's order to its
   repository.
4. Integration into `v0.9-joins`, the orchestrator's.

Rollback: the cycle is two commits on a branch; reverting them restores the
console script and the bare command.

## Open Questions

Each carries a recommendation; the orchestrator's review and the pilot's word
settle them.

1. **The console script `machinome-viewer`.** Remove it (one command, no
   alias); or keep it as an alias of `machinome viewer`; or keep it as it is,
   a second program. Recommendation: remove it, as the studio's join removed
   `machinome-studio`; its one reader outside the repository, the site's
   intake, moves to `machinome viewer` in three files (Decision 13).
2. **`python -m machinome.viewer.web`.** Keep it, `__main__.py` unchanged,
   running the framework's command (the orchestrator's decision); or remove
   `__main__.py` and `cli.py`, the module form going with the script.
   Recommendation: keep it, as the orchestrator decided, but with the finding
   that no tool spells it today (probe 14): the Curta's tools spell the former
   module, and moving them to `machinome.viewer.web` or to `machinome viewer`
   is the same one-line change; the movie's and the studio's module forms are
   kept by their joins, so the set keeps one pattern.
3. **A listing of the installed viewers** (the 4 October outline's "reports
   the installed viewers"). An option `--installed` (or a verb `list`) can be
   added without changing the bare report (probe 13). Recommendation: not now;
   no project, host or command reads such a list (the empirical-evidence rule),
   and it is a later, additive change when one does.
4. **The viewer's own `cli.py`.** Reduced to a `main(argv)` running the
   framework's command class (Decision 7); kept whole as the module entry's
   own implementation; or kept as the implementation the framework's command
   calls. Recommendation: reduced; one parser for both spellings, the verbs
   through the seam in both, the movie's shape.
5. **The reference page.** Keep `reference/viewer/cli.rst`, retitled "The
   viewer command", with a synopsis section in `reference/cli.rst` linking it
   (the movie's `reference/movie/command.rst` and its section); or fold it whole
   into `reference/cli.rst`, the endpoints table included. Recommendation:
   keep; the endpoints and the capture's notes are the web viewer's, and the
   page is new in 0.9 (`join-viewer`), so no published link moves either way.
6. **The ADR.** ADR-196 as Decision 14 outlines it; or amendments to ADR-188
   and ADR-194 alone. Recommendation: ADR-196; the one command for the viewer
   is an interface decision of its own, and two ADRs each hold a sentence it
   replaces.
7. **Serve's three deprecated flags** (`--dev`, `--frontend-port`,
   `--start-frontend`), against the orchestrator's "with the options the
   viewer's command has". They are accepted today only so a released
   framework's `develop`, which passed `--start-frontend` to the viewer's
   process, keeps working; after the seam no framework launches that process,
   and the `~=` pins forbid a framework of another release with this viewer.
   Recommendation: not carried into the new verb, and refused by the module
   form (Decision 7); the alternative is three options that do nothing in a
   command that never had them.
8. **The verbs and the project's `viewer` key.** The verbs read no manifest,
   `web` unless `--viewer` (Decision 2); or they follow the seam's default rule
   like `snapshot`, `develop` and `export`, reading the manifest of the
   directory they run in. Recommendation: no manifest; the command acts on the
   installation and on directories it is given, and its answer should not
   depend on the directory a host runs it from.
