## Context

The pilot's eighth decision for Machinome 0.9 (`workflow/ongoing/release-0.9.md`
at the repository root, 12 October 2026) puts this cycle inside 0.9: the
framework's `machinome/viewer/__init__.py` declares the contract of viewers,
with the providers `machinome.viewer.openscad` and `machinome.viewer.web`, and
it extends its path with portions. Decisions 1, 3 and 4 bound it: the web
viewer's address is `machinome.viewer.web` and nothing of it is renamed;
nothing of the set is published on npm; the viewer's verbs become a
subcommand in a cycle of their own, `viewer-command`, after this one. The
outline the decision ratifies is "The last cycle of the phase: `viewer-seam`
(pilot, 4 October 2026)" in `packages/machinome/workflow/ongoing/lean-core.md`,
read with that note's "D2. How a seam resolves its provider" (a try-import of
a known provider, refused by its extra) and "Every node type is a package". The
outline predates the viewer's join; its own clause for that event applies:
"when the viewer comes into the monorepo under the one licence, its own
portion `machinome.viewer.web` replaces that wrapper, the entry-point group
`machinome.viewer` and the subprocess go, and the bundle ships inside the
provider". The bundle already ships inside the provider since `join-viewer`.

The orchestrator made two reversible decisions within the outline, flagged to
the pilot: the default rule (Decision 2) and a recommendation to carry for the
OpenSCAD provider's distribution (Decision 4, Open Questions 1).

This design is written against the line `v0.9-joins` as it will be at this
cycle's planning commit: 462f7119 (the viewer's, the movie's and the skills'
joins and the command seam), then `release-tooling` (feb1b46e, integrated on
the line on 12 October 2026: the root `Makefile` with `PACKAGES` and `TESTED`,
`scripts/check-dist --out`, `make docs` from `docs/requirements.txt` alone,
the layout gate reading the Makefile's list), then `join-studio` (proposed on
its bench, not yet landed: `machinome.studio` at
`packages/machinome-studio/machinome/studio`, written `P` below, which reads
the viewer's bundle from `machinome viewer`'s report and photographs every
project with `machinome snapshot --renderer web` in `P/screenshots.py`; its
ADR-193; its delta modifying `framework-identity`'s "Extras select
independent Machinome products"). Where a sentence below depends on
`join-studio` it says so; the applier re-reads the landed text before editing
it.

Paths below are the framework directory's (`packages/machinome/`) unless they
start with `packages/` or name a root file. The probes ran in the scratch
directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C9-propose/`
(written `<scratch>`): `<scratch>/tree` is the bench's HEAD (462f7119)
extracted by `git archive`, with the bench's built bundle copied in, its venv
synced from the lock (`uv sync --python 3.12`, 198 packages, exit 0), and the
prototype of this design written into it; nothing was written in the bench but
this change's planning artifacts. Baselines were taken with the bench's own
venv on unmodified code. Tools: uv 0.11.8, CPython 3.12.3, OpenSCAD 2021.01
under `xvfb-run`, Playwright's Chromium headless shell 1243, Sphinx 9.1.0, the
OpenSpec CLI 1.6.0.

### What the core reaches today

The web viewer is reached from seven places, the OpenSCAD viewer from one:

| caller | today | through |
|---|---|---|
| `machinome snapshot --renderer web` | `BrowserRenderer().render`: lock, build STLs, stage, then `python -m machinome.viewer.web capture <staging>` | `machinome/viewers/browser.py`, `viewers/bundle.py` |
| `machinome snapshot` (default) | `supported.renderer('openscad')`: `present` in the lock, `render` after | the table's provisional column, `machinome.node.openscad.renderer` |
| `machinome develop` | `Popen([python, -m, machinome.viewer.web, serve, --build-dir, ...])`, terminated and started again after every builder exit | `viewers/bundle.viewer_command`, `has_bundle`, `INSTALL_REMEDY` |
| `machinome export` | copies `index.html` and `machinome-viewer.js`; warns on an unreadable version | `viewers/bundle` |
| the builder | warns once when the installed viewer cannot read the published version | `viewers/bundle.unreadable_document` |
| the Sphinx extension | completes widget-less exports; warns on an unreadable version | `viewers/bundle` |
| `docs/conf.py` | copies the bundle beside the embedding guide | `viewers/bundle.bundle_path` |
| `machinome viewer` | prints the entry point's report | `viewers/bundle.describe` |
| `machinome movie` (`installed_viewer`) | the bundle path for the Node side | `machinome.viewers.bundle.describe()['path']` |

`viewers/bundle.py` finds the viewer by loading the entry point `bundle` of the
group `machinome.viewer`, which the viewer's manifest declares as
`machinome.viewer.web.bundle:describe`. Outside the core, the studio runs
`machinome viewer` and `machinome snapshot --renderer web` as processes; the
site reads the bundle the report names.

### Probes

1. **The seam, editable** (`<scratch>/probe-01-seam-editable.txt`).
   `machinome/viewer/__init__.py` written into the core with the line
   `machinome/node/__init__.py` carries, `__path__ =
   _namespace_portions(__path__, __name__)`, as the viewer join's probe 20
   found it must: `machinome.viewer` is the core's regular package whose path
   is the core's directory, then `packages/machinome-viewer/machinome/viewer`
   (and, once the new member is synced, `packages/machinome-viewer-openscad/
   machinome/viewer`); `machinome.viewer.web` resolves to the viewer's
   `__init__.py`. Before the provider declared a contract, `viewer('web')`
   raised "The web viewer machinome.viewer.web declares none, but this
   machinome speaks viewer contract version 1; install the viewer released
   with this machinome"; `viewer('openscad')` with no provider installed raised
   `ExtraUnavailable`: "the openscad viewer needs machinome.viewer.openscad,
   which is not installed; install it with 'pip install
   "machinome[viewer-openscad]"'"; `viewer('povray')` raised "no viewer is
   named 'povray'; the viewers are openscad, web".
2. **The web server in the framework's process** (`<scratch>/probe_serve_thread.py`,
   `probe-02-serve-thread.txt`). `WebViewer`'s app served by `uvicorn.Server`
   in a daemon thread: importing fastapi, uvicorn and the server module 241
   ms; listening 68 ms after start; `/build/viewer.json` and `/_viewer` answer
   (`available` true, API 29); the reload socket greets with `reload`; a
   broadcast of `reload` on the open socket arrives in 0.3 ms; `stop()` (the
   server's `should_exit`, then the thread joined) 197 ms, the client seeing
   the connection closed; a second server on the same port listening 7 ms
   later.
3. **Today's server process** (`<scratch>/probe_serve_process.py`,
   `probe-03-serve-process.txt`): `python -m machinome.viewer.web serve`
   listening after 366, 380 and 336 ms; `terminate()` and `wait()` 202, 195
   and 200 ms. Every rebuild today costs about 0.55 s with no server, during
   which the open page shows its offline banner and reconnects.
4. **The manual's snapshot example through the seam**
   (`<scratch>/probe-04-pixels.txt`). The three commands of
   `docs/tutorial/10-share.rst` ("Photograph") on two copies of
   `docs/tutorial` (model `c09`): with the bench's venv (base) and with the
   prototype (the seam, the OpenSCAD provider as the distribution
   `machinome-viewer-openscad`, the web capture in the command's process),
   `--renderer web` spelt `--viewer web`, plus `--viewer openscad` explicitly.
   Four pairs, each 1920 x 1080 RGBA: `counter` (default viewer, `--viewall
   --autocenter`), `carry` (`--drive crank=3580`), `carry` explicit, and
   `carry-web`: 0 differing pixels of 2073600 each, and the PNGs
   byte-identical (SHA-256 `78e213ff…`, `2d4127a1…`, `2d4127a1…`,
   `b46f77a4…`). The images were looked at: the counter on its base with the
   crank, the drum's digits on the web image only (the OpenSCAD viewer draws no
   markings, as the export spec states). Under `strace -f -e trace=execve`
   the web capture executed Playwright's driver and Chromium's headless shell
   and no `python -m machinome.viewer.web` (`<scratch>/strace-web.txt`, six
   `execve`).
5. **Import cost** (`<scratch>/probe-05-seam-importtime.txt`, three runs).
   `import machinome.viewer` 1.3 to 1.6 ms of its own (`typing`, 6 to 8 ms
   cumulative, is usually loaded already); today's `machinome.viewers.bundle`
   29 to 33 ms cumulative, nearly all `importlib.metadata`, which the entry
   point needs. `viewer('web').readable(13)` imports the viewer's `bundle` and
   `currency` (17 ms) and no fastapi, uvicorn or Playwright. `machinome -h`
   (1029 modules), `snapshot -h` (355) and `develop -h` (359) import no
   provider, at the base and in the prototype.
6. **The manual's environment** (`<scratch>/probe-06-docs-venv.txt`). The
   environment `make docs` builds from `docs/requirements.txt` holds Sphinx,
   its theme and the published `machinome-viewer` 0.8.0, whose package is
   `machinome_viewer` and whose entry point is the only way the source core
   finds it. With `docs/conf.py`'s path (the source core first, every
   `packages/machinome-*` but the viewer's), the seam refuses `web`: "the web
   viewer needs machinome.viewer.web, which is not installed". With the
   viewer's directory on the path too, `web` resolves to the repository's
   viewer and its report answers.
7. **The manual through the seam** (`<scratch>/probe-07-docs-build.txt`). The
   prototype's `machinome/sphinx.py` and `docs/conf.py` asking the seam, the
   viewer's directory on the path, a built bundle present: `python -m sphinx
   -b html -W -E docs <out>` exit 0 in 9.8 s; every tutorial export completed
   with `index.html` and `machinome-viewer.js`; the embedding guide's copy
   made. With the bundle moved aside (`probe-07b-docs-nobundle.txt`): exit 2,
   the warning "machinome: Viewer bundle not found at …/widget/dist/
   machinome-viewer.js. A release of machinome-viewer from PyPI carries it; a
   source checkout builds it with: …". The manual cannot be built through the
   seam without the bundle being built first.
8. **The OpenSCAD provider as its own distribution, from the wheels**
   (`<scratch>/probe-08-wheels-A.txt`). `uv build --wheel` of the core, the
   viewer, `machinome-viewer-openscad` and `machinome-node-openscad`: the
   core's wheel ships `machinome/viewer/__init__.py`, the new one
   `machinome/viewer/openscad/__init__.py` alone, the viewer its eight modules,
   `stage.py` and the bundle. `uv pip install --find-links … "machinome[openscad,viewer]"`
   into a fresh venv installs the four (the `openscad` extra listing the node
   package and the viewer); from `/tmp` both viewers resolve from
   `site-packages`, `machinome.viewer`'s path one directory. A one-part
   `OpenScadNode` project: `machinome snapshot` exit 0, "Snapshot saved";
   `--viewer web` without Playwright exit 1 with the viewer's own remedy
   ("Install the browser renderer with `pip install
   'machinome-viewer[snapshot]'` and then download Chromium …", wording this
   change rewrites).
9. **The OpenSCAD provider as a second portion of the node package**
   (`<scratch>/probe-09-wheels-B.txt`). The node package's find configuration
   `include = ["machinome.node.openscad", "machinome.viewer.openscad"]` with
   the provider's directory beside the node package's: the wheel ships both,
   and installed with the core and the viewer the provider resolves from
   `site-packages/machinome/viewer/openscad/__init__.py`. Both shapes work;
   Decision 4 chooses.
10. **`machinome vet`** (`<scratch>/probe-10-vet.txt`). The universe's denylist
    with `machinome.viewer` in place of `machinome.viewers` and
    `machinome.viewer.web`: a model file importing `from machinome.viewer
    import viewer`, `import machinome.viewer.openscad` and `from
    machinome.viewer.web.server import WebViewer` gets three
    `framework-internal` findings naming `machinome.viewer`.
11. **`machinome develop` on `Vibecoded-demos/gear-shift`**
    (`<scratch>/probe_develop.py`, `probe-11-develop.txt`, two copies of the
    project's HEAD by `git archive`, `MACHINOME_PORT=8771`, the process group
    interrupted as a terminal does). Through the prototype (the session in a
    thread, `reload()` where the loop restarted the server): server up 0.43 s;
    document version 4 published at 9.3 s; the page served; the socket
    greeted; after a source edit the socket receives `reload` 0.5 s later,
    when the builder exits and the loop goes round; 45 s later `/_viewer` 200;
    SIGINT to the group: exit 0 in 0.72 s; no viewer process left. Today
    (the bench's venv): up 0.74 s; document at 9.6 s; after the edit the open
    socket is closed (`ConnectionClosedError` at 0.7 s, the server
    restarted); exit 0 in 0.67 s. A first run that signalled the parent alone
    hung both shapes alike for 30 s (the builder child is in the same group
    and is not signalled), so the comparison was rerun with the group.
12. **A published viewer of the new shape behind the manual's source core**
    (`<scratch>/probe-12-docs-published.txt`). The fresh venv of probe 8
    (core and viewer wheels in `site-packages`) with `docs/conf.py`'s path in
    front: `machinome.viewer` resolves to the source core and its path holds
    the source directories only; `site-packages/machinome/viewer/` holds the
    core's `__init__.py`, so `_namespace_portions` excludes it as another copy
    of the core, and `web` is refused. Publishing 0.9 does not restore the
    manual's present arrangement.
13. **The lock with the member** (`<scratch>/uv-lock-A.log`). The root's
    sources line and the core's two extras added: `uv lock` 0.8 s, "Added
    machinome-viewer-openscad v0.8.1", 198 to 199 packages, 35 diff lines
    (the member's entry and the extras' markers); `uv sync` installs it
    editable.
14. **The default rule on a manifest**. `viewer = "web"` under
    `[tool.machinome]` of the tutorial copy: `machinome models` still reads
    the manifest (exit 0); `machinome snapshot --drive crank=3580` with no
    `--viewer` writes the web image, identical to the explicit one
    (`ImageChops.difference(...).getbbox()` None); `--viewer openscad` with the
    manifest naming `web` writes the OpenSCAD image, identical to the base.
15. **The refusals' wording** (prototype). `machinome snapshot --renderer web`:
    "Error: machinome snapshot --renderer is --viewer since Machinome 0.9:
    write --viewer web", exit 2; `--viewer povray`: "Error: no viewer is named
    'povray'; the viewers are openscad, web", exit 1.
16. **The report through the provider**. `machinome viewer` before and after
    the prototype's `manager/viewer.py` asks `viewer('web').describe()`:
    byte-identical standard output; `machinome-viewer describe` identical to
    both.
17. **The projects** (read-only; `git grep -n -e --renderer` in each of the 83
    repositories under the catalogue, `WTs/` and `machinome-projects/`
    skipped; `<scratch>/projects-renderer-tracked.txt`): 59 lines in 20
    repositories, every one in a README, a `docs/` page, recorded evidence or
    an archived OpenSpec record; none in code. `git grep` for
    `machinome.viewers`, `OpenScadRenderer`, `BrowserRenderer`,
    `supported.renderer` and `DEFAULT_RENDERER` in the same repositories finds
    no code use (`<scratch>/projects-viewers-imports.txt`; the hits are logs,
    evidence and one comment).

## Goals / Non-Goals

**Goals:**

- One seam, `machinome.viewer`, through which every caller in the set reaches
  a viewer, by name, with one contract version and one set of refusals.
- Both viewers providers at their outline addresses, each declaring what it
  offers; the OpenSCAD one out of the node package.
- The flag `--viewer`, the old one refused naming it; the word viewer in
  every message, help line, class and logger of the seam and the providers.
- The web viewer in the framework's process: no entry point, no subprocess.
- Pixels unchanged through both viewers.
- `machinome viewer` and `machinome-viewer describe|serve|capture` printing
  what they print today.

**Non-Goals:**

- The viewer's verbs under `machinome viewer` (`viewer-command`, Decision 15).
- A third viewer, an OpenSCAD GUI viewer, a viewer chosen by availability.
- Renaming `develop`'s `--web`, `--no-web`, `--web-dev` (Open Questions 8).
- The projects' move (the orchestrator's step after the implementation,
  Decision 12) and the workspace's skills (`workspace-consistency`).
- Changing what the web viewer draws, its API (29), its document versions
  (1 to 13) or its page.

## Decisions

### 1. The seam, `machinome/viewer/__init__.py`

A regular package of the core, written fresh, standard library and
`machinome.extras` only:

- `CONTRACT = 1`, the viewer contract version this core speaks; a provider
  declares the version it implements as its own `CONTRACT`.
- `EXTRAS = {'web': 'viewer', 'openscad': 'viewer-openscad'}`: the viewers the
  core knows by name and the extra that installs each. This mapping, and
  `DEFAULTS` below, are the only place the core names a viewer's technology;
  the SCAD scan's allowed modules gain this file for the three letters of
  `openscad` (Decision 11).
- `OPERATIONS = ('present', 'capture', 'serve', 'embed')`, the operations a
  provider may declare beyond what every viewer answers.
- `DEFAULTS = {'capture': 'openscad', 'serve': 'web', 'embed': 'web'}`: each
  command's default of today (Decision 2).
- The Protocols, the outline's operation list:
  - `Viewer`: `NAME: str`, `CONTRACT: int`, `OPERATIONS: frozenset`;
    `identity() -> (distribution, version)`; `document_versions() -> list |
    None`, `None` for a viewer that reads no node-tree document;
    `readable(version) -> bool`.
  - `Presenter` (`present`): `present(node, build_dir) -> presented`, called
    by the command inside the project build lock with the posed root, and
    `withdraw(presented)`, called after the capture whether it succeeded or
    failed. `presented` is the provider's own value: the staging directory of
    the web viewer, the root of the OpenSCAD viewer.
  - `Capturer` (`capture`): `CAPTURE_OPTIONS: frozenset`, the snapshot options
    it honours beyond the common `output`, `imgsize`, `time` and `camera`;
    `capture(presented, request, output)`.
  - `Server` (`serve`): `serve(build_dir, port=None) -> Session`, the server
    listening when it returns.
  - `Session`: `reload()`, which tells every open page a build was published;
    `stop()`, which returns when the server has stopped.
  - `Embedder` (`embed`): `files() -> {'index.html': Path,
    'machinome-viewer.js': Path}`, what an export or a page copies;
    `describe() -> dict`, the report `machinome viewer` prints.
- `CaptureRequest`, a frozen dataclass of the snapshot's options (`imgsize`,
  `time`, `camera`, `autocenter`, `viewall`, `projection`, `colorscheme`,
  `view`, `render`, `preview`), so a provider reads no argparse namespace.
- The refusals: an absent viewer is `machinome.extras.ExtraUnavailable(extra,
  f'the {name} viewer', f'machinome.viewer.{name}')`, which words "the web
  viewer needs machinome.viewer.web, which is not installed; install it with
  'pip install "machinome[viewer]"'"; `UnknownViewer` (a `LookupError`) "no
  viewer is named '<name>'; the viewers are openscad, web";
  `ViewerIncompatible` "The <name> viewer machinome.viewer.<name> declares
  contract version <n> (or: declares none), but this machinome speaks viewer
  contract version 1; install the viewer released with this machinome";
  `ViewerLacks` "<needed_by> needs a viewer that can <operation>, and the
  <name> viewer cannot; the viewers that can: <names>"; `ViewerError`, the
  one exception a provider raises for an operational failure, its message the
  sentence the command writes after `Error: `.
- `viewer(name)`: imports `machinome.viewer.<name>`. A `ModuleNotFoundError`
  whose `name` is that address is absence (refused by `EXTRAS[name]`, or
  `UnknownViewer` for a name not in it); an `ExtraUnavailable` the provider's
  own import raises (the OpenSCAD provider's node package or SolidPython
  absent) passes unmodified, as `machinome.node.supported.load` passes a node
  module's; any other import error propagates. A provider whose `CONTRACT`
  differs, or is missing, is `ViewerIncompatible`. Exceptions are not cached;
  a resolved provider is the module, cached by the import system.
- `require(name, operation, needed_by)`: `viewer(name)`, then `ViewerLacks`
  when `operation` is not in its `OPERATIONS`.
- `chosen(operation, explicit=None, origin=None)`: Decision 2.
- `unreadable(version, name)`: the one sentence today's
  `bundle.unreadable_document` returns ("this model needs document version
  <v>, and the installed <name> viewer renders <list> (<distribution>
  <version>)"), or `None` when the viewer reads it, reads no document, or is
  not installed. The builder, the exporter and the web provider's staging use
  it.
- The last line: `__path__ = _namespace_portions(__path__, __name__)` with
  the comment the engine package carries. Probe 1, and the viewer join's
  probe 20: without it every editable workspace hides both providers.

Rejected: a `machinome.viewer.seam` module beside an `__init__` holding
nothing (the outline names the `__init__`, and the engine package has its
seams in its `__init__`); discovery by entry points (D2: a try-import of a
known address; the group is what this cycle removes).

### 2. The default rule

An explicit `--viewer <name>` wins. Without it, a project may name its viewer
in its manifest, `[tool.machinome] viewer = "<name>"`; without that, each
command keeps its default of today: `snapshot` `openscad`, `develop` `web`,
`export`'s embedding `web` (`DEFAULTS` by operation). `export` has no
fixed-pose capture today, only the embedding, so it has one default. No
availability is consulted and nothing falls back: the chosen viewer is
resolved, and an absent one is refused by its extra.

The manifest's viewer is the project's viewer for every command that chooses
one: a command whose operation it lacks is refused by name, naming the key
and the flag ("machinome develop needs a viewer that can serve, and the
openscad viewer, this project's viewer (`[tool.machinome] viewer`), cannot;
the viewers that can: web; name one with --viewer"). `read_declaration`
gains the key's validation: a value that is not a string is a
`ProjectManifestError` naming the key; an unknown name is the command's
`UnknownViewer` refusal. The builder's and the exporter's readability warning
ask the viewer of the operation that will read the document (`serve`, `embed`)
by the same rule; `develop` hands its chosen name to the builders it starts.
The Sphinx extension, the manual's configuration and `machinome movie` read no
project manifest: they ask `web`, the one viewer that embeds.

The evidence for the key: four project repositories photograph every image
through the web viewer and spell `--renderer web` on each line, 3DPrintedClocks
fourteen times, Metamaquina2 five, openarm and YouCanBuildBiPed three each
(probe 17); the studio passes it on every preview. The rule keeps the
`web-snapshot` requirement that the default never follows availability or the
project's backends: a project's declared viewer is a declaration, read from
the manifest, not inferred (probe 14).

### 3. The web provider, `machinome.viewer.web`

The distribution `machinome-viewer` and its package keep their names and
address. Its `__init__.py` gains, below `__version__` and importing only the
standard library at module level:

- `CONTRACT = 1`, `NAME = 'web'`, `OPERATIONS = frozenset({'present',
  'capture', 'serve', 'embed'})`, `CAPTURE_OPTIONS = frozenset({'autocenter',
  'viewall'})` (what the browser does by default, accepted as today).
- `identity()` (`('machinome-viewer', bundle.version())`),
  `document_versions()` and `readable()` from `bundle.py`'s declaration;
  `describe()` and `files()` from `bundle.py`.
- `present(node, build_dir)`: `node.build_stls()` then the staging, the code
  of `machinome/viewers/browser.py` moved by `git mv` to `stage.py` (its
  `stage`, `_stage`, `refuse_unreadable`, `artifact_path`, `remove_stage`),
  reading the core's offer: the assembled node, `machinome.core.serializer`'s
  `serialize_node`, `compiled_program`, `compiled_clocked`, `drivers_table`
  and `document_body`, and `machinome.core.pieces.PieceInventory`, the four
  things the outline names, imported inside the function. The refusal of an
  unreadable version is the seam's `unreadable` sentence followed by today's
  words with `--viewer openscad`.
- `withdraw(staging)`: removes the staging directory.
- `capture(staging, request, output)`: `capture.py`'s `Capture(staging).render`
  with `mount_options` and the camera resolved by `machinome.core.camera`, in
  the caller's process (probe 4). `CaptureError` becomes `ViewerError`'s
  message.
- `serve(build_dir, port=None)`: `session.py`, new, the shape of probe 2: a
  `Session` holding `WebViewer(build_dir, port=port)` and a `uvicorn.Server`
  run in a daemon thread named `machinome-viewer-web`; `start` returns when
  the server listens; `reload()` sends `reload` to every socket the server's
  reload route holds open, on the server's loop; `stop()` sets `should_exit`
  and joins the thread. `server.py`'s reload route keeps its greeting and
  records its open sockets, so `machinome-viewer serve` (which keeps
  `WebViewer.start()`, blocking) is unchanged for a browser.

The page needs no change: its reloader already answers a `reload` message on
an open socket by fetching the build (`widget/src/reloader.ts`, `onmessage`).
The only difference a maker sees is that a rebuild no longer drops the socket
and flashes the offline banner (probe 11).

`cli.py` keeps `describe`, `serve` and `capture` with their options, help
and output; its module docstring and `__init__`'s say the framework reaches
the package through the seam. `capture.py`'s and the package's messages and
docstrings say viewer (`PLAYWRIGHT_REMEDY`: "Install the browser viewer's
capture with `pip install 'machinome-viewer[snapshot]'` and then download
Chromium with `playwright install chromium`."). The manifest loses
`[project.entry-points."machinome.viewer"]` and its comment; the dependency
comment says the viewer imports the core it is released with. The viewer's
README and `CHANGELOG.md` (its `Unreleased`) say so; its own specs
(`packages/machinome-viewer/openspec/specs/`) are brought current in place
where they state the entry point or `machinome snapshot --renderer web`, as
`join-viewer` brought them current. The viewer's tests that assert the entry
point (`tests/test_bundle.py`, `tests/test_machinome_identity.py`) assert the
provider's declarations instead.

### 4. The OpenSCAD provider, `machinome.viewer.openscad`, a distribution of its own

Recommended (Open Questions 1): the outline's own shape, the distribution
`machinome-viewer-openscad` at `packages/machinome-viewer-openscad/`, its
portion `machinome.viewer.openscad`, installed by the core's extra
`viewer-openscad`. The second shape, a second portion of
`machinome-node-openscad` installed by the `openscad` extra, also works (probe
9) and saves one member; it is not recommended because it makes a node
distribution ship an address outside `machinome.node` (ADR-183's one portion
per distribution, the layout gate's one address per extension package), names
the viewer's identity after a node type, and departs from the ratified
outline for no gain to the maker: under the recommended shape the `openscad`
and `solid2` extras install the viewer too (Decision 5), so every install that
draws an OpenSCAD still today keeps doing so (probe 8).

`git mv packages/machinome-node-openscad/machinome/node/openscad/renderer.py
packages/machinome-viewer-openscad/machinome/viewer/openscad/__init__.py`,
then in that file: the module docstring (the OpenSCAD viewer, a provider of
`machinome.viewer`); the class `OpenScadRenderer` renamed `OpenScadViewer`;
the logger `viewer.openscad`; `binary.require_openscad`'s alternative `use
--viewer web`; `render`'s `sys.exit` paths raising `ViewerError` with today's
words ("OpenSCAD could not open import file …", "OpenSCAD rendering failed:
<stderr>", "OpenSCAD not found in PATH. Please install OpenSCAD and ensure it
is accessible.", the binary contract's refusal, the xvfb sentence), the
partial image removed as today; and the module-level declarations:
`CONTRACT = 1`, `NAME = 'openscad'`, `OPERATIONS = frozenset({'present',
'capture'})`, `CAPTURE_OPTIONS = frozenset({'autocenter', 'viewall',
'projection', 'colorscheme', 'view', 'render', 'preview'})`, `identity()`,
`document_versions()` returning `None`, `readable()` `False`, `present(node,
build_dir)` (assemble and write the root's SCAD, today's `present`),
`withdraw(node)`, `capture(node, request, output)` (today's `draw` and
`_report`, the subprocess runner injectable for the tests as today). It
imports `machinome.node.openscad.writer` and `binary`, so its import without
SolidPython or without the node package raises the node package's refusal,
naming `machinome[openscad]`, which the seam passes through.

The manifest:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-viewer-openscad"
version = "0.8.1"
description = "The OpenSCAD viewer of Machinome: a still of a machine drawn by the openscad executable"
readme = { file = "README.md", content-type = "text/markdown" }
requires-python = ">=3.11"
license = "GPL-2.0-or-later OR CERN-OHL-S-2.0+"
license-files = ["LICENSE", "LICENSES/*.txt"]
authors = [
    { name = "Luis Fagundes", email = "lhfagundes@gmail.com" },
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
keywords = ["machinome"]
dependencies = [
    # The core whose seam this viewer is a provider of, released with it:
    # the set carries one version, and the pins between its packages are ~=
    # both ways.
    "machinome~=0.8.1",
    # The OpenSCAD node family's writer, which writes the SCAD this viewer
    # draws, and the contract of the openscad executable. The executable
    # itself is no package's to install.
    "machinome-node-openscad~=0.8.1",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

[tool.setuptools.packages.find]
# The package directory machinome/viewer/openscad/, which has its own
# __init__.py, with none at machinome/ or machinome/viewer/, so the core's
# seam admits it as a portion.
include = ["machinome.viewer.openscad"]
namespaces = true
```

The README:

```markdown
# machinome-viewer-openscad

The OpenSCAD viewer of [Machinome](https://github.com/machinome/machinome):
the package `machinome.viewer.openscad`, which draws a still of a machine at
one assembled instant by writing its SCAD through the OpenSCAD node family and
running the [OpenSCAD](https://openscad.org) executable, for `machinome
snapshot --viewer openscad`. The executable itself is installed apart, from
OpenSCAD.

## Install

    pip install "machinome[viewer-openscad]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

The links `LICENSE -> ../../LICENSE` and `LICENSES -> ../../LICENSES`. The
OpenSCAD node package loses the renderer from its `__init__` docstring, its
README ("and the OpenSCAD renderer of `machinome snapshot`" goes) and its
description ("The OpenSCAD node family of Machinome and its SCAD writer");
`binary.py`'s docstring names the viewer.

### 5. The extras

The core's manifest, replacing the `openscad` and `solid2` blocks and adding
one:

```toml
# The OpenSCAD node family (`machinome.node.openscad`: OpenScadNode, the
# OpenSCAD writer and the contract of the openscad executable), which writes
# SCAD through SolidPython, and the OpenSCAD viewer that draws it
# (`machinome.viewer.openscad`); the OpenSCAD executable itself is no
# extra's to install.
openscad = [
    "machinome-node-openscad~=0.8.1",
    "machinome-viewer-openscad~=0.8.1",
]
# The OpenSCAD viewer alone (`machinome.viewer.openscad`, the distribution
# machinome-viewer-openscad), which requires the OpenSCAD node family for
# its writer: `machinome snapshot --viewer openscad` on a model of any parts.
viewer-openscad = [
    "machinome-viewer-openscad~=0.8.1",
]
# `machinome.node.solid2` (Solid2Node), which renders with SolidPython over
# the OpenSCAD node family and requires it, and the OpenSCAD viewer.
solid2 = [
    "machinome-node-solid2~=0.8.1",
    "machinome-viewer-openscad~=0.8.1",
]
```

The `viewer` and `web-snapshot` comments say the browser viewer is reached
through the seam (no "separate process"). `all` is unchanged and installs the
OpenSCAD viewer through `openscad`. `dev` is unchanged. The `kernel-extras`
rule that each node type's extra is named by its key holds; these two extras
install one more distribution of the set, as `all` does.

### 6. `machinome snapshot`

- Options: `--viewer NAME` (help: "The viewer that takes the image: openscad
  or web (default: the project's viewer, else openscad)", the names and the
  default read from the seam); `--renderer` kept as a suppressed option whose
  use exits 2 with "Error: machinome snapshot --renderer is --viewer since
  Machinome 0.9: write --viewer <value>" (probe 15). The other options are
  unchanged.
- `handle`: the model selected; the name chosen (Decision 2); the viewer
  required for `capture` before anything is loaded or written: an
  `ExtraUnavailable` answered "Error: machinome snapshot --viewer <name> needs
  the <extra> extra: <refusal>; or use --viewer <the other>", exit 1 (today's
  line, R4 of `openscad-out`, with the flag's new name); `UnknownViewer`,
  `ViewerLacks`, `ViewerIncompatible` as "Error: <message>", exit 1. Then the
  options the chosen viewer does not honour, beyond the common four, refused
  together: "Error: the web viewer does not support: --projection,
  --colorscheme" (today's sentence with "viewer"). Then the existing
  validations of `--time`, `--view` and `--imgsize`.
- Inside one `project_build_lock()`: load, `--drive`, keyframe, and
  `presented = viewer.present(node, build_dir)`, the build directory the one
  the web renderer computed (`get_build_dir(args.path or node.file)`,
  absolute). The lock is released; `viewer.capture(presented,
  CaptureRequest(...), output)`; `viewer.withdraw(presented)` in a `finally`.
  A `ViewerError` is written "Error: <message>", exit 1, no image. Today the
  web path took the lock twice, once to load and once to build and stage; it
  is now taken once, and released before the browser starts, as
  `web-snapshot` requires.
- The module imports no table of node types: `renderer_names`,
  `supported.renderer`, `supported.DEFAULT_RENDERER` and the string
  comparisons with `'web'` go (the four of the outline). `COLORSCHEMES` and
  `VIEW_OPTIONS` stay, for argparse.

### 7. The other callers

- **`machinome develop`**: `--viewer NAME` (default by Decision 2, `web`);
  `--web` stays the explicit spelling of the browser viewer and combined with
  `--viewer` naming another is an argument error; `--no-web` resolves no
  viewer, as today. Before any child starts, `require(name, 'serve',
  'machinome develop')` and the provider's `describe()` (the bundle present
  and current), each refusal one `Error:` line, exit 1, no builder started.
  `self.web()` returns `provider.serve(build_dir)`; where the loop terminated
  and restarted the process it calls `session.reload()`; on Ctrl-C and on a
  failed first build it calls `session.stop()`. `--web-dev` is accepted and
  logs the warning the viewer's command gives for `--start-frontend`
  ("--web-dev no longer does anything: the development page is served
  directly, with no separate frontend process."), Open Questions 8.
  `run_builder` takes the chosen name for the builder's readability warning.
  `web_viewer_command` and the `Popen` import go.
- **`machinome export`**: `--viewer NAME` (default `web`, the embedding);
  with the widget, `require(name, 'embed', 'machinome export')` and
  `files()`; `WidgetBundleMissing` words the refusal or the provider's
  `describe()` failure, then "Or pass --no-widget to export only the manifest
  and models." `--no-widget` resolves no viewer. The readability warning uses
  `unreadable(version, name)` when the viewer is installed.
- **The builder** (`core/builder.py`): `_warn_unreadable(version)` asks
  `unreadable(version, self.viewer)`, the name given by `develop`, else
  `chosen('serve')`; its sentence is unchanged after the viewer's words.
  `machinome.viewers` is no longer imported; the seam is (probe 5).
- **The Sphinx extension** (`machinome/sphinx.py`): `require('web', 'embed',
  'machinome.sphinx')`; `document_versions()` for the warning, `files()` and
  `describe()` for completing an export; an absent viewer, a missing bundle or
  a stale one is one warning naming the refusal (with `-W`, a failure), as
  today. It still imports no CAD runtime.
- **`docs/conf.py`**: `copy_the_embedding_example` copies
  `require('web', 'embed', 'the manual').files()['machinome-viewer.js']`;
  the path line stops excluding `machinome-viewer` (Decision 13).
- **`machinome viewer`** (`manager/viewer.py`): prints
  `require('web', 'embed', 'machinome viewer').describe()` as JSON, unchanged
  (probe 16); every refusal on standard error, exit 1, nothing on standard
  output. `viewer-command` takes the command over (Decision 15).
- **`machinome movie`** (`packages/machinome-movie/machinome/movie/cli.py`):
  `installed_viewer(verb)` returns `str(require('web', 'embed', ...).files()
  ['machinome-viewer.js'])` after `describe()`, its refusal "machinome movie
  <verb> needs the browser viewer: <refusal>" unchanged in shape; its test
  (`tests/test_command.py`) patches the seam.
- **The studio** (inside the repository since `join-studio`):
  `P/screenshots.py` passes `--viewer web`; its tests
  (`packages/machinome-studio/tests/test_screenshots.py`,
  `test_project_preparation.py`) and its skills
  (`P/shop-skills/machinome-api/SKILL.md`, `P/shop-skills/machinome/SKILL.md`)
  say `--viewer`. Its record (`packages/machinome-studio/workflow/`, archived
  records, ADRs) is not rewritten. Its reading of `machinome viewer` is
  unchanged.

### 8. What goes

`packages/machinome/machinome/viewers/` (`__init__.py`, `bundle.py`, and
`browser.py`, moved); in `machinome/node/supported.py`, the `renderers` field
of `NodeType`, the row's renderer pair, `DEFAULT_RENDERER`, `renderer()` and
the docstring's provisional paragraph (the table states classes and commands);
the viewer's entry point; `viewer_command()` and every run of `python -m
machinome.viewer.web` by the framework; `OpenScadRenderer` and
`BrowserRenderer`; the logger channel `viewers.openscad`. No module of a former
name is provided: `import machinome.viewers` is a `ModuleNotFoundError`, as
for any removed module.

### 9. `machinome vet`

`machinome/vet/universe.toml`'s contract denylist names `"machinome.viewer"` in
place of `"machinome.viewers"` and `"machinome.viewer.web"` (the latter's
comment rewritten: the seam and its providers serve, capture, build bundles
and launch programs). A vetted file reaching the seam or either provider is
`framework-internal`, the finding naming `machinome.viewer` (probe 10).
Recommended over denying the providers alone (Open Questions 4): a pure model
has no use for choosing a viewer; the commands do that. No project reaches it
(probe 17).

### 10. The set's tooling

- **The workspace**: the root `pyproject.toml`'s sources gain
  `machinome-viewer-openscad = { workspace = true }` after the viewer's;
  `uv lock` (probe 13: 199 packages); `uv sync`.
- **The Makefile** (`release-tooling`): `PACKAGES` gains
  `machinome-viewer-openscad` in its sorted place; it is not in `TESTED` (the
  core's suite tests it, as the node packages), so `make test
  PKG=machinome-viewer-openscad` gives the existing "keeps no tests of its
  own" line.
- **`.bumpversion.cfg`**: the two tables, after the viewer's:
  `[bumpversion:file(version):packages/machinome-viewer-openscad/pyproject.toml]`
  (`version = "{current_version}"`) and `[bumpversion:file(pins):…]`
  (`~={current_version}"`), the shape of the node packages' tables.
- **The layout gate** (`tests/test_repository_layout.py`): `EXTENSIONS` gains
  `'machinome-viewer-openscad': ('machinome.viewer.openscad',
  'viewer-openscad')`; `PACKAGE_PORTIONS` gains it with `('__init__',)` and
  the OpenSCAD node package's row loses `'renderer'`;
  `test_the_core_viewers_hold_no_node_type_s_renderer` becomes
  `test_the_core_holds_the_seam_of_viewers_and_no_viewer`: no
  `machinome/viewers/`, and `machinome/viewer/` holds `__init__.py` alone; the
  module docstring names the distribution.
- **`scripts/check-dist`**: the `machinome-viewer` row loses the entry-point
  and `viewer_command` assertions and asserts instead that
  `machinome.viewer.viewer('web')` is the distribution's `__init__.py`, its
  `CONTRACT` the seam's, its `OPERATIONS` the four, that the distribution
  ships no `entry_points.txt` group `machinome.viewer`, and that the shipped
  modules are ten, today's eight with `session.py` and `stage.py`; its commands
  stay `machinome-viewer describe` and `machinome viewer`. The
  `machinome-node-openscad` row's shipped list loses `renderer.py` and its
  `supported.renderer` lines. A new row `machinome-viewer-openscad`,
  `'through': 'viewer-openscad'`, from the `MESH_NODE` template's helpers: the
  one shipped file, the pins `machinome~=` and `machinome-node-openscad~=`,
  `viewer('openscad')` the distribution's file with `CONTRACT` and
  `OPERATIONS`, and `machinome snapshot` of a one-part `OpenScadNode`
  project drawing a PNG where `openscad` and `xvfb-run` (or a display) are on
  the PATH, else `present` writing the root's SCAD and `withdraw` removing it;
  plus the licence lines. The core's own row is unchanged.
- **CI**: no new job; the docs job's change is Decision 13's.

### 11. The tests, red first

New, `tests/test_viewer_seam.py` (red: `ModuleNotFoundError: No module named
'machinome.viewer'`'s `__init__` from the core, the import failing at
collection): the seam's names (`CONTRACT == 1`, `EXTRAS`, `DEFAULTS`,
`OPERATIONS`, the Protocols); `viewer('web')` and `viewer('openscad')`
resolving to their distributions' files, each provider's `CONTRACT`,
`OPERATIONS` (web the four, OpenSCAD `present` and `capture`) and Protocol
members; absence by a meta-path finder hiding `machinome.viewer.openscad` and
then `machinome.viewer.web` (the `ExtraUnavailable` with `viewer-openscad`
and `viewer`); the node package hidden under the OpenSCAD provider (the
`openscad` extra's refusal passing through); an unknown name; a fake provider
portion in a temporary directory with `CONTRACT = 2` and with none
(`ViewerIncompatible`); `require` refusing `serve` of the OpenSCAD viewer by
name; `chosen` over a temporary manifest (explicit, the key, each default; a
non-string key refused); `unreadable`; the path extension (an editable
portion admitted, a second core copy refused) and the seam's own import
loading no provider and no web stack.

Changed, each run first at the base to record its red:

| module | change | expected red at the base |
|---|---|---|
| `test_snapshot.py` | `--viewer`, the refusal of `--renderer`, the manifest default, presenters through the seam, `OpenScadViewer`, `assertLogs('viewer.openscad')` | collection: `machinome.viewer` has no `viewer`; `--viewer` unknown |
| `test_browser_renderer.py`, renamed `test_web_viewer_capture.py` | the staging and capture through `machinome.viewer.web` | `ImportError` on `present`, `stage` |
| `test_openscad_dependency.py`, `test_scad_presentation.py`, `test_markings.py`, `test_build_publication.py`, `test_openscad_node.py`, `test_clocked_publication.py`, `test_running_play.py`, `test_running_document.py`, `test_profile_running_bound.py` | patches and imports at the providers and the seam | collection or `ModuleNotFoundError` on the new addresses |
| `test_supported_node_types.py` | no renderer row, no `renderer()`; the absent-package doors without the renderer's | `NODE_TYPES['openscad'].renderers` exists |
| `test_manager_develop.py` | the session (`serve`, `reload`, `stop`) in place of `Popen`, `--viewer`, `--web` with another viewer refused | `Develop` has no session; `Popen` called |
| `test_export.py`, `test_sphinx_ext.py`, `test_docs_exports.py` | the seam patched; `export --viewer` | patches at `machinome.core.export.viewer_bundle` absent |
| `test_manager_viewer.py`, `test_viewer_bundle.py` (renamed `test_viewer_report.py`), `test_cli_lazy_imports.py`, `test_machinome_identity.py` | the report through the seam; the help paths import no provider; no entry point | `machinome.viewers.bundle` still imported; entry point found |
| `test_repository_layout.py`, `test_kernel_extras.py`, `test_release_records.py` | Decision 10's rows, the extras of Decision 5 | no directory, no extra, no table |
| `test_core_names_no_scad.py` | `ALLOWED_PACKAGES` gains `machinome-viewer-openscad`; `ALLOWED_MODULES` gains `machinome/viewer/__init__.py` | the scan finds the seam |
| `test_core_kernel_free.py` | `TABLE_READERS` loses `snapshot.py` | `snapshot.py` still reads the table |
| `test_vet_universe.py` | `machinome.viewer` denied | the seam passes |
| `test_viewer_documentation_links.py`, `test_docs_structure.py` | the pages of Decision 16 | the 0.9 section and the reference's sentences absent |
| a new `test_the_word_is_viewer` (in `test_viewer_seam.py`) | no `--renderer`, `machinome.viewers`, `renderer_names`, `DEFAULT_RENDERER`, `OpenScadRenderer`, `BrowserRenderer`, `viewers.openscad` in the core's `machinome/`, the two providers, the movie and the studio packages, and no "renderer" in a string the seam or a provider writes | the four places of `snapshot.py`, `browser.py`, the renderer module |

The viewer's own suite (`packages/machinome-viewer/tests`) and the movie's run
at their places: the entry-point tests replaced by the provider's
declarations, the server's reload broadcast tested on a live session.

### 12. The projects' move, the orchestrator's step

After the implementation is committed, with the workspace's
`scripts/rewrite-projects` and a table `viewer-seam.toml`, or by hand: in the
20 repositories of probe 17, `--renderer <name>` becomes `--viewer <name>` in
live instructions: `README.md` files and `docs/` pages that a reader runs
(3DPrintedClocks `simulation/README.md` fourteen lines; Metamaquina2 five
`docs/*-verification.md`; Prusa3-vanilla five; openarm `README.md` three;
YouCanBuildBiPed three; splitflap three; dragon-r1 three; kossel two;
Pascaline-module two; mechanical-multiplier, CycloidalDrive, AlbertPro,
hexapod_spiderbot_model, BCN3D-Moveo, OpenCycloid, OpenTorque-Actuator,
fender-bender, dutch-windmill-2 one each; Vault_with_combination_lock's
`docs/handoff.md` one). Recorded evidence is not rewritten: Voron-2's
`docs/evidence/**` (eight lines in logs and JSON), openarm's archived
OpenSpec evidence, and any file under `openspec/changes/archive/` or
`docs/evidence/`: they record a command that was run. One commit per
repository on its checked-out branch, a repository with uncommitted changes
in a file to rewrite skipped and reported, as the root-cleanup pass did
(Open Questions 9). The universe sweep runs before and after; nothing a
project imports moves, so the rows are expected identical.

### 13. The manual's build takes the repository's viewer (the pilot's word needed)

The `user-documentation` requirement "The documentation build produces
nothing" builds the manual from `docs/requirements.txt` alone, which installs
the published `machinome-viewer`, and forbids a Node tool in the Read the Docs
configuration, the CI docs job and the Makefile's `docs` target; the
`release-tooling` requirement makes `make docs` install that file alone. The
manual's source core finds the published viewer, 0.8.0 at `machinome_viewer`,
only through the entry point this cycle removes (probe 6), and even a
published viewer at the new address is hidden behind the source core (probe
12). The seam and the present arrangement cannot both stand.

Recommended: the manual takes the repository's viewer. `docs/conf.py` puts
`packages/machinome-viewer` on the path with the other packages;
`docs/requirements.txt` names Sphinx and its theme; the widget's bundle is
built with npm before Sphinx: `.readthedocs.yaml` gains `build.tools.nodejs:
"22"` and `build.jobs.pre_build` running `npm ci` and `npm run build
--workspace packages/machinome-viewer/machinome/viewer/web/widget` at the
repository root (Read the Docs runs commands at the checkout's root and offers
Node 14 to 24); the CI docs job installs Node 22; `make docs` depends on the
Makefile's `bundle` rule (it already exists for `test-machinome`). Probe 7
shows the build passes with `-W` once the bundle is there and fails naming the
bundle when it is not. The `user-documentation` and `release-tooling` deltas
carry this, and `test_docs_exports.py`'s pin on "no Node tool" changes with
them.

Alternatives: (a) keep a second lookup of the published viewer through the
entry point for the manual alone, a compatibility path the pilot's rulings
refuse; (b) commit the built bundle, which the viewer's join ruled out; (c)
leave the manual broken until 0.9.0 is published, which probe 12 shows does
not mend it. If the pilot declines the recommendation, everything else in this
design stands; the manual's validation leg and the two deltas wait on the
decision (tasks group 9 is gated on it).

### 14. The spec deltas

New: `viewer-seam`. Modified, each requirement copied whole from the line's
head with its scenario titles kept: `web-snapshot` (six), `cli` (five),
`viewer-distribution` (three modified, two removed), `kernel-extras` (two
modified, one added), `framework-identity` (two; "Extras select independent
Machinome products" written on `join-studio`'s modified text), `openscad-node`
(three), `openscad-dependency` (two), `build-pipeline` (three: the scenarios
spelling the flag), `backend-neutral-materialization` (one), `cli-startup-cost`
(one), `movie-distribution` (one), `vet` (one), `user-documentation` (two
modified, one added), `release-tooling` (one, gated). `node-model` is not
modified: its requirements name the table of node types by its classes and
state no renderer column; the column was stated in `cli`, `kernel-extras` and
`openscad-node`. The specs' `Purpose` lines that name `machinome/viewers/`
(`export`, `printed-pieces`, `openscad-node`) are brought current at the sync,
by hand, since a delta carries no purpose. Requirements that use the word
"renderer" in prose without a flag, an address or a mechanism (the STL render
protocol, the markings' z-fighting sentence, "under either renderer") are not
rewritten by this change.

### 15. What `viewer-command` takes over

This cycle leaves, for the next: `machinome viewer` reporting the web viewer's
`describe()` as today (the studio and the site parse it), where the outline
has it report the installed viewers; the verbs `describe`, `serve` and
`capture` under `machinome viewer`, dispatching through the seam (`serve`
through `Session`, `capture` through `present`, `capture` and `withdraw` on a
staged directory); the fate of the console script `machinome-viewer` and of
`python -m machinome.viewer.web` (projects' tools spell the latter, probe 17);
the reference page `reference/viewer/cli.rst`; the studio's and the site's
readings if the report's shape changes. Nothing here forecloses those.

### 16. The records, the manual and the validation

- **ADR-194**, "Viewers are providers behind one seam, chosen by name"
  (`docs/adrs/BUILD/`), Proposed, Accepted at the archive: the seam, the
  contract and its version, resolution by a known address with the path
  extension, the refusals, the default rule, the two providers and their
  operation sets, the web viewer in the framework's process, the OpenSCAD
  viewer's distribution and extras, the flag. Supersedes ADR-068 in what
  ADR-188 left of it (the lookup through the entry point and the process
  boundary) and ADR-188's "The seam is unchanged" paragraph and its vet
  sentence; amends ADR-179 (the renderer column removed; the table states
  classes and commands), ADR-183 (an extension package may be a portion of
  `machinome.viewer`), ADR-191 (the films take the bundle through the seam);
  cites ADR-103 (the browser stays the only interactive viewer) and ADR-176
  (the engines' seam it is modelled on). Index lines in `docs/adrs/README.md`
  and the status lines of the amended ADRs. Open Questions 5.
- **`HISTORY.rst`** and **`docs/project/changelog.rst`**: one `Unreleased`
  bullet each: the seam and its two providers; `--viewer` on `snapshot`,
  `develop` and `export`, `--renderer` refused naming it; the project's
  `viewer` key; the OpenSCAD viewer as `machinome-viewer-openscad`, installed
  by `viewer-openscad`, `openscad` and `solid2`; the web viewer in the
  framework's process, a rebuild reaching the page without a reconnect; the
  entry point and `machinome.viewers` removed; vet.
- **`docs/project/upgrading.rst`**: a section "Upgrading from Machinome 0.8 to
  0.9" begun above the 0.8.0 to 0.8.1 one, holding "The viewer flag": `--renderer`
  is `--viewer`, the project key, the `viewer-openscad` extra for a project
  whose parts are not OpenSCAD, the entry point gone for a host that read it
  (use `machinome viewer`). `release-0.9.0` completes the section.
- **The pages** that spell `--renderer` or the process boundary:
  `reference/cli.rst` (snapshot, develop, export), `tutorial/10-share.rst`,
  `howto/share-an-export.rst`, `howto/markings.rst`,
  `concepts/publishing.rst`, `start/install.rst` (the extras table and the
  viewer paragraph), `reference/viewer/cli.rst` and `reference/viewer/index.rst`
  (the entry-point sentences go: "The framework reaches the package through
  its viewer seam, in its own process"), `reference/viewer/mount.rst` and
  `layouts.rst` where they name the capture as a process; the movie's pages
  where they name the entry point. A how-to section "Choose the viewer of a
  still" in the snapshot how-to (the flag, the key, the two viewers'
  options). The released records (`releases/`, older changelog sections, the
  ADRs' histories) are not rewritten.
- **`docs/architecture.md`**: the viewers section and the Map's rows: the
  seam, the two providers, the in-process web viewer; the renderer column and
  the process boundary as history.
- **`README.md`** (root): a row for `machinome-viewer-openscad`;
  **`CONTRIBUTING.rst`**: its `-e packages/machinome-viewer-openscad` line;
  `context7.json` where it names the flag.
- **Validation**: the suite on the bench's venv, one process, against the
  base the line's latest evidence records; the viewer's and the movie's suites
  at their places; `make lint`; `make docs` (gated, Decision 13);
  `make check` (`scripts/check-dist` on the tree and on a clean copy); the
  universe sweep before and after the projects' move; the originating check:
  the three commands of `docs/tutorial/10-share.rst` on a copy of the
  tutorial, `--viewer` for `--renderer`, against base images taken with the
  base's venv, 0 differing pixels each, the images looked at; and `machinome
  develop` on a copy of `Vibecoded-demos/gear-shift` (`git archive` of its
  HEAD): served, the page loaded, a source edit producing a `reload` message
  on the open socket, the group interrupted, exit 0, no process left.

## Risks / Trade-offs

- [The web stack in the framework's process: an exception in the server
  thread no longer kills a child, and uvicorn shares the process with the
  develop loop] → the thread is the provider's, daemon, named; a server that
  fails to start raises from `serve()` before any builder starts; `stop()` is
  called on every exit path the loop has today (probe 11).
- [Playwright's sync API in the snapshot's process] → the capture is a
  one-shot at the end of the command, after the build lock is released, as the
  subprocess was; probe 4's pixels are identical.
- [A reload now arrives as a message, not a reconnect: a page that was offline
  when it was sent never sees it] → the reloader fetches the build on
  reconnect, as today; only an open page gets the message, and an open page is
  what restarting the server reached before.
- [The manual's build gains Node] → the pilot's decision (Decision 13); the
  rest does not depend on it.
- [One more distribution to version, build and smoke] → the node packages'
  tables, rows and gate entries are the pattern; probe 13's lock diff is one
  package.
- [A project naming `openscad` as its viewer cannot `develop` without
  `--viewer web`] → the refusal names the key and the flag; no project names
  it today, and the four that would name a viewer would name `web`
  (Decision 2, Open Questions 3).
- [Projects and tools that ran `python -m machinome.viewer.web` keep working;
  ones that read the entry point stop] → none in the catalogue reads it
  (probe 17); the upgrading page says to use `machinome viewer`.

## Migration Plan

1. Planning commit (the orchestrator), after fast-forwarding the bench onto
   the line holding `release-tooling` and `join-studio`.
2. Implementation on the bench, red first, as tasks.md orders it; nothing
   committed by the applier; the orchestrator's review, then the
   implementation commit.
3. The projects' move (Decision 12), the orchestrator's, after the
   implementation commit, with the sweep before and after.
4. Integration into `v0.9-joins`, the orchestrator's.

Rollback: the cycle is two commits on a branch; reverting them restores the
column, the entry point and the subprocess together. The projects' move is
one commit per repository and reverts alone.

## Open Questions

1. **The OpenSCAD provider's distribution.** A distribution of its own,
   `machinome-viewer-openscad` with the extra `viewer-openscad`, requiring
   `machinome-node-openscad` (the outline's), or a second portion of
   `machinome-node-openscad` installed by the `openscad` extra (probe 9).
   Recommendation: the outline's, with the `openscad` and `solid2` extras
   installing it, so "openscad installs everything OpenSCAD" stays true and
   no install loses its still (probe 8). The orchestrator ratifies.
2. **The in-process serve's shape.** A thread the provider owns, reloading
   by a message on the open sockets (probes 2 and 11), or a child process the
   provider owns (`multiprocessing`) restarted as today. Recommendation: the
   thread: no second interpreter, no 0.55 s of offline banner per rebuild,
   no process to reap; the outline's "the subprocess goes".
3. **The manifest key.** `[tool.machinome] viewer = "<name>"`, one key, the
   project's viewer for every command, a command whose operation it lacks
   refused by name. Alternatives: the key applying only to commands whose
   operation the viewer offers (which needs the provider imported to know,
   and reads like a fallback); one key per operation (`[tool.machinome.viewer]
   capture = "web"`), more than any project needs. Recommendation: one key,
   as Decision 2.
4. **The vet denials.** `machinome.viewer` denied whole (the seam and both
   providers), or the providers alone with the seam's functions in the
   contract. Recommendation: whole; a model does not choose a viewer.
5. **The ADR.** ADR-194 as Decision 16 outlines it, or amendments to ADR-068,
   ADR-179 and ADR-188 alone. Recommendation: ADR-194; the seam is a new
   architectural element with its own contract version, and three earlier
   ADRs each hold one piece of what it replaces.
6. **What `viewer-command` takes over.** Decision 15's list.
   Recommendation: as listed; this cycle changes no output of `machinome
   viewer` or `machinome-viewer`.
7. **The manual's build (the pilot's).** Decision 13: the repository's viewer
   with its bundle built by npm in Read the Docs, CI and `make docs`.
   Recommendation: accept; the alternatives are a compatibility path, a
   committed bundle, or a broken manual.
8. **`develop`'s `--web`, `--no-web` and `--web-dev`.** Kept as they are, with
   `--web-dev` warning that it does nothing (as the viewer's command already
   warns for `--start-frontend`); or renamed now. Recommendation: keep; they
   name the browser, not a renderer, and the outline does not touch them;
   `--web-dev`'s removal can follow when no tool passes it.
9. **The projects' recorded evidence.** Rewrite only live instructions
   (READMEs and `docs/` pages a reader runs), leaving logs, JSON evidence and
   archived OpenSpec records as the commands that were run. Recommendation:
   as Decision 12.
