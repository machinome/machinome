## Why

The pilot's plan for the joins of Machinome 0.9 (`workflow/ongoing/joins-0.9.md`
at the repository root, set on 11 October 2026) names this change its third
cycle: machinome-viewer, the browser viewer published as 0.7.0, 0.7.1 and
0.8.0 and held at 0.8.1, joins the repository whole, its history imported to
its final paths. On 12 October 2026 the pilot settled how: the viewer joins
into `packages/machinome-viewer/` with its record (tests, specs, archived
changes, working record, its own decision log, changelog) and its whole
history, the 79 commits from before the split included, its four tags
prefixed `viewer-`; its manual folds into the framework's; one licence, the
set's; one version, the set's, with `~=` pins both ways; pip-only
distribution, the widget's `package.json` private and the first member of a
root npm workspace founded here; the seam unchanged, the framework finding
the viewer through the entry point `machinome.viewer` and running it as a
separate process; the root manifest's `exclude-dependencies` losing
`machinome-viewer`.

The probes in design.md find the product does not work at its new place as
it is: its widget's tests read the repository's fixtures and its manual by
relative paths (at `machinome/viewer/web/widget/` eight of 66 vitest files
fail, 121 tests), its
manual's 12 pages build with 32 warnings in the framework's manual, its
`ensure_current` refuses to rebuild a stale bundle when npm installs the
dependencies at the workspace root ("the widget's dependencies are not
installed"), its packaging guard watches only the widget's own `node_modules`
while `npm ci` there writes the root's inside the workspace, and a source
copy of the viewer on the manual's path shadows the published viewer the
manual's build installs.

On 12 October 2026 the pilot gave the viewer's Python package the address
`machinome.viewer.web`: the dot like the rest of the set, and the address the
pilot's `viewer-seam` outline of 4 October 2026 gives the web provider, so no
later cycle renames it. Not `machinome.viewer`, the address of the seam
itself, which a later cycle writes (`machinome/viewer/__init__.py` with the
OpenSCAD provider `machinome.viewer.openscad`), and not `machinome_viewer`
kept. The probes of the revision (design.md probes 19 to 21) find the package
resolves at that address editable, from its wheel beside the core's and alone;
that the seam's future `machinome/viewer/__init__.py` hides it in an editable
workspace unless it extends its path with portions as `machinome/node/` does;
and that `machinome vet`, which refused an import of `machinome_viewer` as
outside the universe, admits `machinome.viewer.web` as part of the contract
unless it is denied.

## What Changes

- **The join, by the orchestrator, after the planning commit**: a fresh clone
  of machinome-viewer rewritten by `git filter-repo` with the mapping of
  design.md Decision 2 (893 files land, 877 under `packages/machinome-viewer/`
  and 16 in the framework's manual; 11 tracked files and the stray
  `openscad.py` of history are dropped), its `main` (bd2bf75, every branch an
  ancestor) merged with `--allow-unrelated-histories`, its tags renamed
  `viewer-v0.7.0` to `viewer-v0.8.1`; rehearsed in the scratch directory,
  where the merge is clean and `server.py` reads at its new path, without
  `--follow`, back to the framework commit of 18 July 2023 that founded it;
  the rewritten `main` is 1b41968.
- **`machinome-viewer` at `packages/machinome-viewer/`**, a product that keeps
  its record in its directory: its manifest at the set's version 0.8.1,
  requiring `machinome~=0.8.1`, under the set's licence, its scripts and its
  `machinome.viewer` entry point; the links `LICENSE` and `LICENSES`; the
  package directory `machinome/viewer/web/` (the import
  `machinome.viewer.web`, the pilot's decision of 12 October 2026), with no
  `__init__.py` at `machinome/` nor at `machinome/viewer/`, and the widget
  inside it as at bd2bf75. **BREAKING** for anything that runs `python -m
  machinome_viewer` (eleven tools of one project and one of another; the
  framework moves with the change, to `python -m machinome.viewer.web`).
- **The npm workspace at the root**: a private root `package.json` whose one
  member is the widget, one lockfile at the root seeded from the widget's (the
  same 174 resolutions), the widget's own lockfile retired, `node_modules/` at
  the root and ignored; the bundle is never tracked and the wheel carries it.
  The viewer's currency check and packaging guard read `node_modules` where
  npm puts it inside the workspace.
- **One version and the pins**: the viewer enters `.bumpversion.cfg` (its
  manifest, its pin, `__init__.py`, the widget's `package.json`); the core's
  `viewer` and `web-snapshot` extras become `machinome-viewer~=0.8.1` and
  `machinome-viewer[snapshot]~=0.8.1`; the core's `dev` extra installs
  `web-snapshot`, so the workspace installs the viewer and Playwright; the root
  manifest names the member as a source and excludes only the studio; `uv
  lock` resolves 192 packages.
- **One licence at the join**: the product's `LICENSE` and `context7.json` are
  dropped by the import; its manifests, 155 file headers, the bundle's banner
  and its reader-facing pages state the set's expression; its third-party
  provenance (three.js, jokenizer, molejo, bundled into `machinome-viewer.js`)
  joins `CREDITS.md`; no record this change writes names the licence it
  carried.
- **The manual folds in** by reader intent: three how-to guides (operate a
  machine in the viewer, share an export and take a still, embed the viewer)
  and the reference section `reference/viewer/` (mount, the handle, layouts,
  running, clocked, the command, compatibility, troubleshooting); the working
  embedding example is copied into the built manual with the installed
  viewer's bundle and a committed spinner export; the framework's pages that
  link the separate manual link inside it; its install and source-build facts
  go to the installation page and the contributor guide.
- **The tests at their new place**: the widget's vitest suite and the viewer's
  pytest suite run from the repository (CI's test job gains Node, the root
  `npm ci`, the widget's typecheck, test and build, Chromium, and a step
  running the viewer's pytest from its directory); the pinning tests are
  rewritten for the new place; the core's sixteen tests that skipped without
  the viewer run.
- **`scripts/check-dist`** builds the viewer (its sdist builds the bundle,
  so the dist job gains Node) and smokes it from its wheel: its files, its
  version and pins, the entry point, the report, the banner and the licence.
- **`machinome vet`** denies `machinome.viewer.web` as a framework internal
  (it serves, captures and builds in processes of its own), so a vetted
  project that reaches the viewer is refused as it was under the former
  name; the former name stays outside the universe.
- **The parity fixture's generator** writes, with no argument, the fixture of
  the viewer package in its own repository, no longer a sibling checkout.
- **Records**: `HISTORY.rst`, the manual's changelog and the viewer's
  `CHANGELOG.md`; the root `README.md`, `CONTRIBUTING.rst`, `context7.json`
  and `AI-USE.md`; the framework's `README.rst` and the pages that stated the
  viewer's separate licence; the architecture's viewers section and Map;
  ADR-188 (recommended, Open Questions 2), ADR-068 superseded in its
  repository and licence, ADR-182, ADR-183 and ADR-187 amended; the viewer's
  own specs and notes brought current in place, its decision log untouched
  but for a dated note.

Not in this change: the viewer seam of the `viewer-seam` outline (the pilot's,
deferred), the videomaker's `--viewer` option, a version for upload, the
retirement of the separate Read the Docs project and of the original
repository (the pilot's), the projects' tools (listed for the orchestrator),
any push, and the remaining two joins.

## Capabilities

### New Capabilities

None. The viewer's own sixteen specs arrive by the import under
`packages/machinome-viewer/openspec/specs/`, its own record, and are brought
current in place by the applier (design.md Decision 13).

### Modified Capabilities

- `framework-identity`: the viewer extras pin the set's viewer with `~=`; the
  monorepo holds a second product, numbered with the set, and a root npm
  workspace; `scripts/check-dist` smokes the viewer from its wheel (new
  scenarios).
- `viewer-distribution`: the framework runs the viewer as
  `python -m machinome.viewer.web`.
- `user-documentation`: the viewer's provenance, the separate manual's
  requirement (renamed), the embedding claims, the build that produces
  nothing, the licence rule of the 0.8.0 record, the extras of the 0.8.1
  record and the README's licence sentence follow the one licence and the
  folded manual (scenario titles kept, new ones added).
- `framework-contributor-guidance`: the guide states the Node setup, the root
  `npm ci`, where the widget's and the viewer's tests run, and the pip
  command names the viewer's directory.
- `kinematics`: the parity fixture's generator writes the repository's own
  viewer package by default.
- `vet`: the browser viewer's package `machinome.viewer.web` is a denied
  framework internal; its former name stays outside the universe (one new
  scenario).

`kernel-extras`, `cli`, `export`, `sphinx-embedding` and `web-snapshot` are
unchanged: they name the distribution, the extra and the entry point, which
keep their names.

## Impact

- **Tree.** The join adds 893 files. The cycle adds the root `package.json`
  and `package-lock.json`, the viewer's two licence links, the committed
  spinner export under `docs/_exports/`, ADR-188, and the edits of design.md
  Decisions 3 to 13; it deletes the widget's `package-lock.json`.
- **Code.** In the viewer: the internal imports and docstrings (the address
  `machinome.viewer.web`), `currency.py`'s dependency check, `packaging.py`'s
  guard, the bundle banner. In the core: `viewers/bundle.py`'s command and
  remedy, the manifest's three extras, the vet universe's denylist,
  `docs/conf.py`, `tools/generate_parity_fixture.py`.
- **Tests.** Joining: 24 Python test modules and 66 vitest files run from the
  viewer's directory and the root. Changed in the core's suite:
  `test_repository_layout.py`, `test_release_records.py`,
  `test_docs_structure.py`, `test_viewer_documentation_links.py`,
  `test_generate_parity_fixture.py`, `test_vet_universe.py`, and (the
  address) `test_viewer_bundle.py`, `test_browser_renderer.py`,
  `test_manager_develop.py`, `test_cli_lazy_imports.py`.
- **Build and CI.** Fourteen members build from `packages/`; Node 22 enters
  the test, browser-snapshot and dist jobs; the docs job is unchanged and
  keeps the published viewer.
- **Environment.** The lock resolves Playwright 1.63.0, whose Chromium
  (revision 1243) this machine does not have; the viewer's browser tests need
  `playwright install chromium` once, which the orchestrator runs for the
  bench at the implementation step (Open Questions 6).

Originating evidence: the campaign plan (`workflow/ongoing/joins-0.9.md`, "The
method" and cycle 3), the pilot's decisions of 12 October 2026, the product's
own record, the probes of design.md, and the originating check of design.md
Decision 16: `machinome develop` and `machinome snapshot --renderer web` on
the bench, through the joined viewer.
