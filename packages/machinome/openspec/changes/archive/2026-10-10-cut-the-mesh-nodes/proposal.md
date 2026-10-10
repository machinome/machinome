## Why

The pilot's plan for Machinome 0.9 (`workflow/ongoing/monorepo-0.9.md` at the
repository root, accepted on 10 October 2026) names this change the fourth and
last cycle of the cut: the four node types that need no B-rep engine,
`openscad`, `solid2`, `jscad` and `stl`, leave the core as packages of their
own, in the shape ADR-183 fixed, and the one place the core still imports a
node package, the OpenSCAD snapshot renderer `machinome/viewers/openscad.py`
(left in the core provisionally by ADR-179), moves into the OpenSCAD node
package. The pilot ruled on 4 October 2026 that every node type is a package;
the `jscad` and `stl` extras, which install nothing today, were declared by
`root-cleanup` for this cut. The probes in design.md show the shape holds for
a package directory as it held for a module, that ADR-184's finder refuses the
four absent packages with no edit, and that the cut alone leaves the
kernel-free census, the SCAD-free scan and the layout gate blind to it.

## What Changes

- **Four distributions founded under `packages/`**: `machinome-node-openscad`
  ships the package directory `machinome/node/openscad/` (moved by `git mv`
  from `packages/machinome/machinome/node/openscad/`, its own `__init__.py`
  included) and the OpenSCAD snapshot renderer, moved from
  `packages/machinome/machinome/viewers/openscad.py` to
  `machinome/node/openscad/renderer.py`; `machinome-node-solid2`,
  `machinome-node-jscad` and `machinome-node-stl` ship
  `machinome/node/<name>.py`. Each has its `pyproject.toml`, `README.md` and
  the links `LICENSE` and `LICENSES`, and no `__init__.py` under its
  `machinome/` or `machinome/node/` (design.md, Decisions 1 and 2).
- **The renderer's address moves**: `machinome.viewers.openscad` becomes
  `machinome.node.openscad.renderer`; the renderer row of
  `machinome/node/supported.py` names it; its classes, its output, its
  messages and its logger's name (`viewers.openscad`) are unchanged; the
  core's `machinome/viewers/` keeps `bundle.py` and `browser.py`, and ADR-179's
  renderer column stays provisional (Decision 3). This is the one address the
  change moves; no project imports it.
- **Each distribution states what its module imports**: every one requires
  `machinome~=0.8.1`; `machinome-node-openscad` requires
  `solidpython2==2.1.*`; `machinome-node-solid2` requires
  `machinome-node-openscad~=0.8.1` and `solidpython2==2.1.*`, since its module
  imports both; `machinome-node-stl` requires `trimesh`, unranged, the core
  pinning the range; `machinome-node-jscad` requires nothing more (Decision 2).
- **The core's `openscad`, `solid2`, `jscad` and `stl` extras install the
  sibling distributions** with `~=0.8.1` pins; SolidPython leaves the core's
  manifest; `all` keeps its meaning. **BREAKING** for an install line without
  the node type's extra: a bare `pip install machinome` no longer carries
  `StlNode` and `JScadNode`, so a project of those parts names
  `machinome[stl]` or `machinome[jscad]`, which the refusal at its import line
  names (Decision 4; Open Questions 1).
- **The core imports no node type and no engine provider**, pinned by the
  kernel-free census, which also counts SolidPython as a kernel; the SCAD-free
  scan reads every extension package and allows the word only in the family's
  two distributions and the table of supported node types (Decision 9).
- **The workspace**: the root manifest names the four as sources; `uv.lock` is
  regenerated (187 packages); `.bumpversion.cfg` gains a version table and a
  pin table for each manifest; `setup.cfg`'s two lint ignores name the moved
  files by their new paths (Decisions 5 to 7). The manual builds with no edit
  to `docs/conf.py`, whose path already names every sibling (Decision 8).
- **`scripts/check-dist`** gains a template for a node package over no B-rep
  engine and four rows, each installed through the core's extra from the built
  archives and rendering one part: through OpenSCAD where the binary is on the
  PATH, else writing its SCAD; the `stl` part through trimesh; the `jscad` part
  constructed only, since no environment of the set has the `jscad` command;
  the `openscad` row also resolves the renderer through the table
  (Decision 10).
- **The gate, red first** (Decision 9): the layout gate's table of every
  sibling gains the four and admits a package-directory portion; the core's
  `machinome/node/` holds no node type and its `machinome/viewers/` no
  renderer; the extras, pins and ranges tables; the censuses and scans; the
  renderer's address in the tests that import it; the absent packages'
  refusal at every door, the renderer's and the snapshot command's included;
  the installation page naming every extension distribution.
- **Records**: `HISTORY.rst` and the manual's changelog gain their
  `Unreleased` bullets; `docs/start/install.rst`, `docs/howto/backends.rst`
  and `docs/architecture.md` follow; the root `README.md` gains four rows;
  `CONTRIBUTING.rst`'s pip line names the four; ADR-179 and ADR-183 are amended
  with a dated section, and no ADR is new (Decision 11).

Not in this change: the viewer seam `machinome.viewer` (deferred past 0.8 by
the pilot), `machinome/viewers/bundle.py` and `browser.py`, any version bump,
any upload or push, a leaf contract on the four classes, and the workspace's
`scripts/setup` and `scripts/dev-env` (the campaign's close).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `kernel-extras`: the `openscad`, `solid2`, `jscad` and `stl` extras install
  the node distributions, which state SolidPython or trimesh; SolidPython's
  range is stated wherever it is named; the installation page names every
  extension distribution; the core imports no kernel, no node type and no
  engine provider but in the templates; an absent OpenSCAD node package is
  refused for its submodules and for the node type built over it.
- `openscad-node`: the family is the distributions `machinome-node-openscad`
  and `machinome-node-solid2`; the snapshot renderer is
  `machinome.node.openscad.renderer`; SolidPython's importers and the SCAD-free
  scan's zones are read over the extension packages.
- `cli`: the snapshot command's table row names the renderer at
  `machinome.node.openscad.renderer`, and an absent OpenSCAD node package is
  refused at the command's start by the `openscad` extra.
- `node-model`: every node type's module is shipped by its own distribution,
  the OpenSCAD node package as a package directory; the framework's
  distribution ships none.
- `framework-identity`: the extension packages today are ten; a portion may be
  a package directory with its own `__init__.py` below the levels the core
  defines; `check-dist` smokes the node packages over no B-rep engine.
- `framework-contributor-guidance`: the install without uv names the four
  directories.

`openscad-dependency` and `stl-import` name no install line, no distribution
and no module path the cut moves (the binary's contract keeps its address,
`machinome.node.openscad.binary`); they are unchanged (design.md, Context).

## Impact

- **Tree.** Five files of the OpenSCAD package (four moved with their
  directory, the renderer moved from `machinome/viewers/`) and three modules
  move into four new package directories (manifest, README, two links each).
- **Code.** `machinome/node/supported.py`: the renderer row's string. The
  OpenSCAD package's docstring names its new module. Nothing else in a moved
  module or in the core changes: no class, refusal, message, table key,
  writer output or renderer output.
- **Tests.** Changed: `test_repository_layout.py`, `test_kernel_extras.py`,
  `test_core_kernel_free.py`, `test_core_names_no_scad.py`,
  `test_supported_node_types.py`, `test_docs_structure.py`,
  `test_expression_type.py`, `test_scad_presentation.py`,
  `test_openscad_node.py`, and the renderer's address in `test_snapshot.py`,
  `test_openscad_dependency.py`, `test_markings.py`, `test_build_publication.py`
  and `test_browser_renderer.py`. `tests/base.py` is unchanged: the suite runs
  against the whole set installed.
- **Build and CI.** Eleven distributions build from `packages/`; `check-dist`
  gains four rows; CI's lint glob already covers the siblings; the `dist` job
  has no OpenSCAD, so its two SCAD rows write SCAD rather than render.
- **Records.** Six delta specs; ADR-179 and ADR-183 amended; `HISTORY.rst`;
  the manual's changelog, installation page, backends page and architecture.

Originating evidence: the campaign plan (`workflow/ongoing/monorepo-0.9.md`,
"The rule", "Decisions accepted by the pilot" 1 to 3, "Facts", cycle 4),
ADR-179, ADR-183 and ADR-184, the third cycle's archive
(`openspec/changes/archive/2026-10-10-cut-the-brep-nodes/`), and the probes
recorded in design.md.
