## Why

The pilot's decisions for Machinome 0.9 (`workflow/ongoing/release-0.9.md` at
the repository root, 12 October 2026) put the viewer seam inside 0.9 as their
eighth decision: the framework's `machinome/viewer/__init__.py` declares the
contract of viewers, with the providers `machinome.viewer.openscad` and
`machinome.viewer.web`, and extends its path with portions. The outline it
ratifies is the pilot's of 4 October 2026 ("The last cycle of the phase:
`viewer-seam`", `packages/machinome/workflow/ongoing/lean-core.md`): the word is
viewer, never renderer; viewers coexist and are chosen by name behind one seam
with Protocols and an integer `CONTRACT`; an absent viewer is refused by its
extra, a wrong contract as incompatible, an operation a viewer lacks by name,
and nothing is substituted; the web viewer's staging moves into its provider;
the provisional renderer column of the table of node types (ADR-179) and the
core's `machinome/viewers/` go; the commands take `--viewer <name>`.

Today the core reaches its two viewers in two unrelated ways. The OpenSCAD one
is a row of the table of node types (`machinome.node.openscad.renderer`, a
module of a node package, ADR-179's provisional column); the web one is found
through the entry-point group `machinome.viewer` and run as a subprocess,
`python -m machinome.viewer.web serve|capture` (ADR-068, kept "unchanged" by
ADR-188), a process boundary that existed for a licence difference the one
licence removed. `machinome snapshot` compares the string `'web'` in four
places and calls different methods on each viewer. The viewer joined the
repository on 12 October 2026 at `machinome.viewer.web`, the address the
outline gives its provider, so the outline's own clause now applies: the
portion is the provider, and the entry point and the subprocess go.

The probes in design.md show the seam resolves both providers editable and
from the wheels when its `__init__.py` extends its path (the viewer join's
probe 20, repeated with the file present); that the manual's snapshot example
draws the same pixels through the seam as today, through each viewer (0
differing pixels of 2073600, four images, byte-identical); that the web
viewer serves and captures in the framework's process, a rebuild reaching the
page as a message on its open socket instead of a server restart; and that
removing the entry point breaks the manual's build, which finds the published
viewer only through it (probes 6, 7 and 12).

## What Changes

- **The seam `machinome.viewer`**, a new module of the core
  (`machinome/viewer/__init__.py`): `CONTRACT = 1`; the Protocols of the
  contract (`Viewer`: identity, the document versions it reads, whether a
  version is readable; `Presenter`: present and withdraw at one assembled
  instant; `Capturer`: capture to an image, with the snapshot options it
  honours; `Server` and `Session`: serve interactively, reload, stop;
  `Embedder`: the files an export or a page embeds and the report);
  `viewer(name)` importing `machinome.viewer.<name>`; `require(name,
  operation, needed_by)`; `chosen(operation, explicit)`, the default rule; the
  refusals (an absent viewer by its extra, an unknown name naming the
  viewers, a wrong `CONTRACT` as incompatible, a lacking operation by name);
  the path extension through `machinome._namespace_portions`. It imports
  nothing but the standard library and `machinome.extras`.
- **The web provider is `machinome.viewer.web`** (the distribution
  `machinome-viewer`): its `__init__` declares `CONTRACT`, `NAME`,
  `OPERATIONS` (all four) and the operations, each importing its machinery
  only when called. The core's staging (`machinome/viewers/browser.py`) moves
  into it as `stage.py`; capture runs in the caller's process; `serve` starts
  the development server in a thread the provider owns and returns a session
  whose `reload()` sends `reload` to every open page and whose `stop()` ends
  it. **BREAKING** for nothing outside the repository: the entry-point group
  `machinome.viewer` is removed and the framework no longer runs `python -m
  machinome.viewer.web`; the console script `machinome-viewer
  describe|serve|capture` and `python -m machinome.viewer.web` keep working,
  printing what they print today.
- **The OpenSCAD provider is `machinome.viewer.openscad`**, the distribution
  `machinome-viewer-openscad` at `packages/machinome-viewer-openscad/` (the
  outline's, Open Questions 1), requiring `machinome~=` and
  `machinome-node-openscad~=` for the SCAD writer and the binary; its module
  is `machinome/node/openscad/renderer.py` moved by `git mv` to
  `machinome/viewer/openscad/__init__.py`; it offers present and capture
  only. The core's extra `viewer-openscad` installs it, and the `openscad` and
  `solid2` extras install it beside their node packages, so every install
  that snapshots through OpenSCAD today still does.
- **The commands**: `machinome snapshot --viewer <name>`, `machinome develop
  --viewer <name>` and `machinome export --viewer <name>`; an explicit
  `--viewer` wins, then the project's `[tool.machinome] viewer = "<name>"`,
  then each command's default of today (`snapshot` `openscad`, `develop` and
  `export`'s embedding `web`); no fallback chain. **BREAKING**: `--renderer`
  is refused naming `--viewer` ("machinome snapshot --renderer is --viewer
  since Machinome 0.9: write --viewer web"); every message says viewer. The
  builder, the exporter, the Sphinx extension, the manual's configuration,
  `machinome viewer` and `machinome movie` ask the seam.
- **Removed**: `machinome/viewers/` (three modules), the renderer column of
  `machinome.node.supported` with `DEFAULT_RENDERER` and `renderer()`, the
  entry-point group `machinome.viewer`, the subprocess, the class names
  `OpenScadRenderer` and `BrowserRenderer`, the logger channel
  `viewers.openscad` (now `viewer.openscad`). No module of a former name is
  provided and no alias.
- **`machinome vet`** denies `machinome.viewer`, the seam and both providers,
  in place of `machinome.viewers` and `machinome.viewer.web`.
- **The manual's build takes the repository's viewer** (design.md Decision
  13, **needs the pilot's word**: it contradicts the "no Node tool" clause of
  `user-documentation` and the "requirements.txt alone" clause of
  `release-tooling`): `docs/conf.py` stops leaving the viewer's directory off
  its path, `docs/requirements.txt` stops naming the published viewer, and
  Read the Docs, the CI docs job and `make docs` build the widget's bundle
  with npm before Sphinx.
- **The core of the set**: the member, its sources line and the lock; the
  Makefile's `PACKAGES`; two `.bumpversion.cfg` tables; the layout gate's
  rows; `scripts/check-dist`'s new row and its viewer and OpenSCAD rows
  rewritten; the extras and `tests/test_kernel_extras.py`.
- **The studio's own `--renderer` uses**, inside the repository since
  `join-studio`, move with the code (its screenshots, their tests, its
  skills); the projects' uses (59 lines in 20 repositories, all
  documentation) move after the implementation, in the orchestrator's step.
- **Records**: `HISTORY.rst`, the manual's changelog, the start of the
  upgrading page's 0.9 section, `architecture.md`, the manual's pages that
  name `--renderer` or the process boundary, ADR-194 (recommended, Open
  Questions 5), ADR-068 and ADR-188 superseded in their seam, ADR-179 amended
  (its column removed), ADR-183 and ADR-191 amended.

Not in this change: the viewer's verbs under `machinome viewer`
(`viewer-command`, the next cycle; design.md Decision 15 names what it takes
over), the retirement of `machinome-viewer` as a console script, a third
viewer, a GUI OpenSCAD viewer, the projects' move (the orchestrator's, after
the implementation), the workspace's skills (`workspace-consistency`), any
push and any upload.

## Capabilities

### New Capabilities

- `viewer-seam`: the contract of viewers, their resolution by name, the
  refusals, the default rule, the two providers' declared operations, and the
  path extension.

### Modified Capabilities

- `web-snapshot`: the viewer is chosen by `--viewer` and the default rule and
  never substituted; the web viewer stages and captures in the command's
  process; options a viewer does not honour are refused for any viewer; the
  OpenSCAD viewer presents and withdraws the root's SCAD at its new address.
- `cli`: `snapshot`, `develop` and `export` take `--viewer`; `--renderer` is
  refused naming it; the snapshot reaches no table of node types; `develop`
  serves through the seam and reloads the page in place; `viewer` reports
  through the seam.
- `viewer-distribution`: the framework finds the web viewer at its address
  through the seam and runs it in its own process; the entry-point and
  process requirements are removed.
- `kernel-extras`: the `viewer-openscad` extra, and the `openscad` and
  `solid2` extras installing it; the table of node types holds no renderer
  row.
- `framework-identity`: the OpenSCAD viewer is a distribution of the set; the
  viewer is reached through the seam; check-dist smokes both providers.
- `openscad-node`: the package holds no viewer; the core's allowed zones.
- `openscad-dependency`, `build-pipeline`, `backend-neutral-materialization`:
  the flag `--viewer` where their scenarios spell `--renderer`.
- `cli-startup-cost`: `machinome viewer` answers through the seam, loading no
  server or capture.
- `movie-distribution`: the films take the web viewer's bundle through the
  seam.
- `vet`: `machinome.viewer` is denied whole.
- `user-documentation`: the viewer's provenance without a process boundary;
  the manual's build takes the repository's viewer (gated on the pilot); the
  seam documented.
- `release-tooling`: `make docs` builds the bundle first (gated on the
  pilot).

`node-model` is not modified: its requirements state the table of node types
by the classes it lists and name no renderer column (design.md Decision 14).

## Impact

- **Code.** New: `machinome/viewer/__init__.py`;
  `packages/machinome-viewer-openscad/` (manifest, README, the two licence
  links, `machinome/viewer/openscad/__init__.py`);
  `machinome/viewer/web/session.py`. Moved: `machinome/viewers/browser.py` to
  `machinome/viewer/web/stage.py`; `machinome/node/openscad/renderer.py` to
  `machinome/viewer/openscad/__init__.py`. Deleted: `machinome/viewers/`.
  Edited: `manager/snapshot.py`, `manager/develop.py`, `manager/export.py`,
  `manager/viewer.py`, `core/builder.py`, `core/export.py`, `sphinx.py`,
  `node/supported.py`, `vet/universe.toml`, the core's `pyproject.toml`; the
  viewer's `__init__.py`, `server.py`, `cli.py`, `capture.py`,
  `pyproject.toml`, README; the OpenSCAD node package's `__init__.py`,
  `binary.py`, README and description; the movie's `cli.py`; the studio's
  screenshots and skills.
- **Tests.** Red first: a new `tests/test_viewer_seam.py`; the snapshot,
  develop, export, viewer-command, builder, Sphinx, vet, layout, extras,
  supported-types, SCAD-scan, kernel-free and lazy-import gates; about
  twenty modules move from `machinome.viewers` and the renderer classes to
  the seam (design.md Decision 11 lists them); the viewer's and the movie's
  tests at their addresses.
- **Build.** One member more (eighteen with the studio's); `uv.lock` one package more (probe 13);
  `scripts/check-dist` one row more; the docs job gains Node (gated).
- **Projects.** 59 tracked lines in 20 repositories spell `--renderer`, all in
  READMEs, docs and recorded evidence; none in code; none imports a moved
  module (design.md Decision 12).

Originating evidence: the pilot's decisions above, the outline, the viewer
join's probes 19 and 20, and design.md's probes; the originating check is the
manual's snapshot example (`docs/tutorial/10-share.rst`) through each viewer,
pixels compared to today's, and `machinome develop` on a copy of
`Vibecoded-demos/gear-shift` serving through the seam (design.md Decision 16).
