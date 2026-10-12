## Why

The pilot's decisions for Machinome 0.9 (`workflow/ongoing/release-0.9.md` at
the repository root, 12 October 2026) make `machinome` one command, to which
the packages contribute their subcommands, and give the viewer's command a
cycle of its own before the bump (decision 4): "the framework's `viewer`
command grows the viewer's verbs and dispatches to the installed provider
through the seam, since a framework name is never taken by a contributor"
(ADR-189); unifying anything beyond that is deferred. Decision 1 bounds it: no
module of a former name, no alias.

Today the set has two commands for one viewer. `machinome viewer` prints the
web viewer's report and takes no verb (`machinome viewer describe` exits 2,
"unrecognized arguments"); the viewer's distribution installs a second
executable, `machinome-viewer describe|serve|capture`, and `python -m
machinome.viewer.web` runs the same program. The `viewer-seam` cycle, which
lands before this one, gives the framework typed operations on every viewer
(`describe` and `files` of `embed`, `serve` and its session, `capture` on what
was presented) and leaves this cycle, in its Decision 15, the verbs under
`machinome viewer`, the fate of the console script and of the module entry,
the reference page, and the readers of the report.

The probes in design.md show the verbs through the seam reproduce the viewer's
command: five captures of a staged document of the tutorial's counter, with
and without the camera's parts, byte-identical to `machinome-viewer capture`'s
(probe 3); the same page and document served on the same port, Ctrl-C exiting
0 and a termination signal ending the process as it does today (probe 6); and
the report unchanged byte for byte (probe 5). They also show what the
console script's removal reaches: inside the repository, the viewer's manifest
and one identity test, one row of `scripts/check-dist`, four manual pages and
the records; outside it, the site's viewer intake, which runs
`<workspace>/.venv/bin/machinome-viewer describe` (three files of the site's
repository); no project and no studio module runs it (probes 12 and 14).

## What Changes

- **`machinome viewer` takes the viewer's verbs.** With no verb it prints the
  web viewer's report as today, byte for byte. `machinome viewer describe`
  prints the chosen viewer's report; `machinome viewer serve --build-dir DIR
  [--port N]` serves a published build until interrupted; `machinome viewer
  capture STAGING -o PNG [--imgsize WxH] [--time T] [--view EYE,TARGET] [--up
  X,Y,Z] [--fov DEG]` photographs a staged document into a transparent PNG.
  Each verb takes `--viewer NAME` (default `web`; the command reads no project
  manifest) and asks the seam for the operation it needs: a viewer that cannot
  embed, serve, or capture a published document is refused by name.
- **The seam's capture request carries the camera's parts.** `CaptureRequest`
  gains `eye`, `target`, `up` and `fov`, each left to the viewer when absent,
  beside the `--camera` notation the snapshot passes; a request naming both is
  refused. The `--camera` notation fixes the field of view at 22.5 degrees
  where the viewer's command left it to the viewer (probe 4).
- **BREAKING: the console script `machinome-viewer` is removed.** The viewer's
  manifest declares no `[project.scripts]`; `machinome viewer <verb>` is its
  replacement, the same report and the same options but serve's three
  deprecated flags (`--dev`, `--frontend-port`, `--start-frontend`), which no
  caller passes once the seam serves in the framework's process.
- **`python -m machinome.viewer.web` runs the framework's command.** Its
  `__main__.py` is unchanged; `cli.py` is reduced to `main(argv)`, which runs
  the `machinome viewer` command class with its own parser, as `python -m
  machinome.movie` runs the movie's. With no verb it now prints the report,
  where it printed its help.
- **The reference.** `reference/cli.rst` gains the section `machinome viewer`
  (the synopsis, the report, the verbs, the exit statuses), and
  `reference/viewer/cli.rst` becomes "The viewer command", its examples spelt
  `machinome viewer <verb>`; the pages that spell the former command
  (`reference/viewer/compatibility.rst`, `reference/viewer/troubleshooting.rst`,
  `howto/share-an-export.rst`, `reference/cli.rst`'s `--debug-builder` line)
  name the new one.
- **The core of the set.** `scripts/check-dist`'s viewer row runs `machinome
  viewer`, `machinome viewer describe` and `python -m machinome.viewer.web
  describe`, and asserts the distribution installs no executable of its own;
  `context7.json`'s line.
- **Records.** `HISTORY.rst`, the manual's changelog, the upgrading page's 0.9
  section ("The viewer's command"), `docs/architecture.md`, the viewer's
  `CHANGELOG.md` (its `Unreleased`), its own specs and its OpenSpec
  configuration brought current in place, ADR-196 (recommended, Open
  Questions 6).

Not in this change: a listing of the installed viewers (Open Questions 3; no
reader needs it), `develop`'s `--web` and `--web-dev` (the seam's Open
Questions 8), the site's intake (its repository's change, the pilot's: three
files), the Curta's eleven tools that run the former module `machinome_viewer`
(broken since `join-viewer`, the orchestrator's projects' move, Decision 13),
the workspace's contract line (`workspace-consistency`), any push and any
upload.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `cli`: `machinome viewer` takes the verbs `describe`, `serve` and `capture`
  with `--viewer`, its report unchanged; the report's identity scenario names
  `machinome viewer describe` and the module entry in place of the console
  script.
- `cli-startup-cost`: the verbs' help imports no viewer; `describe` answers as
  the report does.
- `viewer-distribution`: the distribution declares no command of its own;
  `python -m machinome.viewer.web` runs the framework's command.
- `viewer-seam` (founded by `viewer-seam`): `machinome viewer` reads no
  project manifest and defaults to the web viewer; the framework keeps no
  console script of the viewer's; a capture request names its camera by the
  notation or by its parts.
- `framework-identity`: `scripts/check-dist` smokes the viewer's verbs and the
  module entry and finds no executable of the viewer's.
- `user-documentation`: the viewer's reference documents `machinome viewer`,
  and every option of its verbs has its line.

`web-snapshot` is not modified: no requirement of it names the viewer's
command once the seam lands (design.md Decision 12).

## Impact

- **Code.** `packages/machinome/machinome/manager/viewer.py` (the verbs);
  `packages/machinome/machinome/viewer/__init__.py` (`CaptureRequest`'s four
  fields); `packages/machinome-viewer/machinome/viewer/web/__init__.py`
  (`capture` reading the parts), `cli.py` (reduced), `bundle.py` and
  `capture.py` (docstrings); `packages/machinome-viewer/pyproject.toml` (no
  `[project.scripts]`).
- **Tests.** Red first: `tests/test_manager_viewer.py` (the verbs, the
  refusals, the request, the signals), `tests/test_cli_lazy_imports.py`,
  `tests/test_viewer_seam.py` (the request), `tests/test_docs_structure.py`
  (the section, the former spelling), `tests/test_machinome_identity.py` (no
  member but the core declares a script); the viewer's
  `tests/test_machinome_identity.py`, `tests/test_cli.py` and
  `tests/test_documentation.py`.
- **Build.** `scripts/check-dist`'s viewer row; no member, extra, lock or
  Makefile line changes (the Makefile names no script).
- **Outside the repository.** The site's intake
  (`src/machinome_site/intake_viewer.py`, `tests/test_intake_viewer.py`,
  `docs/building.md`) runs the removed script; the workspace contract's line
  409 names it; no project and no studio module runs it.

Originating evidence: the pilot's decisions above, the seam's Decision 15, and
design.md's probes; the originating check is `machinome viewer capture` of a
staged document of the manual's tutorial against `machinome-viewer capture`'s
image, and `machinome viewer serve` of a build of `Vibecoded-demos/gear-shift`
opened in Chromium (design.md Decision 15).
