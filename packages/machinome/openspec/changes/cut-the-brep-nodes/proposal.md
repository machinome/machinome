## Why

The pilot's plan for Machinome 0.9 (`workflow/ongoing/monorepo-0.9.md` at the
repository root, accepted on 10 October 2026) names this change its third
cycle: the four node types over the B-rep engine, `cadquery`, `build123d`,
`step` and `molejo`, leave the core as packages of their own, in the shape the
second cycle fixed for an extension package (ADR-183). The probes in design.md
show the shape holds for a node type as it held for an engine, and find two
places where the cut alone would break a promise: the manual's API reference
imports the four modules from the core's directory and no longer builds with
warnings as errors, and a node type whose distribution is absent is no longer
refused by its extra at the import a project writes.

## What Changes

- **Four distributions founded under `packages/`**:
  `machinome-node-cadquery`, `machinome-node-build123d`, `machinome-node-step`
  and `machinome-node-molejo`, each shipping `machinome/node/<name>.py` moved
  from `packages/machinome/machinome/node/` by `git mv`, unchanged, with its
  `pyproject.toml`, `README.md` and the links `LICENSE` and `LICENSES` to the
  root's, and no `__init__.py` under its `machinome/` or `machinome/node/`
  (design.md, Decisions 1 and 2).
- **Each node distribution states its kernel and requires the B-rep engine**:
  `machinome~=0.8.1` and `machinome-engine-brep~=0.8.1`, with `cadquery==2.7.*`,
  `build123d==0.10.*` and `ocp-gordon>=0.2.2,<0.3`, or `molejo[brep]==0.2.*`,
  each with the comment the core carries today; `machinome-node-step` also
  requires `machinome-node-cadquery~=0.8.1`, whose `workplane_shape` it
  imports, and names CadQuery and the engine itself, since it imports both
  (Decision 3). The OCCT range stays stated once, in the engine.
- **The core's `cadquery`, `build123d`, `step` and `molejo` extras install the
  sibling distributions** with `~=0.8.1` pins; the kernel pins leave the core
  with their comments. Every extra keeps its name and its meaning, `all`
  included: `pip install "machinome[step]"` still installs the STEP node, and
  `from machinome.node.step import StepNode` still resolves it (Decision 4).
- **An absent node package is refused by its extra at its import**: the node
  root appends to `sys.meta_path`, last, a finder that answers a node type of
  the table of supported node types that nothing else found with a module
  whose import raises the refusal `machinome.node.supported.load` already
  raises, naming the node type, its module and `pip install
  "machinome[<key>]"`. The project's import line, `from machinome.node import
  <key>`, the markings' artwork seam and the CLI then refuse alike, as they did
  before the cut. This is the cycle's one change to the framework's modules
  (Decision 5); the pilot may decline it (Open Questions 1).
- **The manual builds from the source tree with the siblings on its path**:
  `docs/conf.py` puts every `packages/machinome-*` directory after the core's on
  `sys.path`, so autodoc imports the four node types as portions (Decision 6).
- **The workspace**: the root manifest names the four as sources; `uv.lock` is
  regenerated (183 packages, four more than the second cycle's); `.bumpversion.cfg`
  gains a version table and a pin table for each manifest; the core's
  `setup.cfg` names the moved `step.py` and `molejo.py` by their new paths in
  its per-file ignores (Decisions 7 to 9).
- **`scripts/check-dist`** gains four rows, each installed through the core's
  extra from the built archives, its smoke resolving `machinome.node.<name>`,
  finding its file owned by its distribution and its version the core's,
  rendering one part on its kernel and reading its volume through the B-rep
  engine (Decision 11).
- **The gate, red first** (Decision 10): the layout gate's extension-package
  group reads one table of every sibling (`{distribution: (address, extra)}`),
  each portion resolving from its directory, the core's `machinome/node/`
  holding none of the four, and no sibling without a row; the kernel-extras
  tables; the kernel-free censuses; the leaf-contract reach test reading the
  modules where they are installed; the node root's export scan reading the
  siblings, as the split-words gate already does; the installation page naming every
  extension distribution; the absent package's refusal at every door.
- **Records**: `HISTORY.rst` and the manual's changelog gain their `Unreleased`
  bullets; `docs/start/install.rst` names the distribution each node extra
  installs and the message an install without it gives; `docs/architecture.md`'s
  Map gains the row of the four; the root `README.md` gains four rows;
  `CONTRIBUTING.rst`'s pip line names the four; ADR-184 records the absent
  package's refusal (Decision 12).

Not in this change: the OpenSCAD family, `solid2`, `jscad` and `stl` (the cycle
`cut-the-mesh-nodes`), any version bump, any upload or push, a leaf contract
declared on the four classes (Open Questions 3), and the workspace's
`scripts/setup` and `scripts/dev-env` (the campaign's close).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `kernel-extras`: the `cadquery`, `build123d`, `step` and `molejo` extras
  install the node distributions, which state the kernels and require the
  B-rep engine; the installation page names every extension distribution; the
  core's kernel scan no longer finds the four modules, which live in their
  distributions and import only their kernels; an absent node package is
  refused by its extra at its import (new requirement).
- `node-model`: the four node types' modules are each shipped by its own
  distribution as a portion of `machinome.node`, at the same address; the
  framework's distribution ships none of them.
- `markings`: the artwork reducer is shipped by `machinome-node-build123d`,
  and a stale marking built without that distribution is refused naming the
  part, the marking, the artwork and `pip install "machinome[build123d]"`.
- `cli`: `import-step`'s reader is shipped by `machinome-node-step`, and the
  command refuses its absence as it refuses an absent kernel.
- `framework-identity`: the extension packages today are the two engines and
  the four node packages, and a requirement between two extension packages is
  pinned `~=` like every pin of the set.
- `framework-contributor-guidance`: the install without uv names the four
  node package directories.

`step-import`, `step-assembly` and `flexible-parts` name no install line and
no module path the cut moves; they are unchanged (design.md, Context).

## Impact

- **Tree.** Four files move (`machinome/node/cadquery.py`, `build123d.py`,
  `step.py` and `molejo.py` of `packages/machinome/` into their
  distributions); new: four package directories (manifest, README, two links
  each) and ADR-184.
- **Code.** `machinome/node/supported.py` gains `absent(key)`, which `load`
  raises; `machinome/node/__init__.py` gains the finder `_AbsentNodeType` and
  appends it to `sys.meta_path` (Decision 5). `docs/conf.py` widens its path (Decision 6).
  The four moved modules, every seam and every message are unchanged.
- **Tests.** Changed: `test_repository_layout.py`, `test_kernel_extras.py`,
  `test_core_kernel_free.py`, `test_leaf_contract_reach.py`,
  `test_node_root_exports_nothing.py`, `test_docs_structure.py`,
  `test_supported_node_types.py`, `test_markings.py`; design.md's probe 7
  names every test the move alone turns red and every gate it leaves blind.
- **Build and CI.** Seven distributions build from `packages/`; `check-dist`
  gains four rows; CI's lint glob already covers the siblings. The
  tag-triggered `build` job still builds the core alone.
- **Records.** ADR-184 (NODE); six delta specs; `HISTORY.rst`; the manual's
  changelog, installation page and architecture Map.

Originating evidence: the campaign plan (`workflow/ongoing/monorepo-0.9.md`,
"The rule", "Decisions accepted by the pilot" 1 to 3, cycle 3), ADR-183 and
the second cycle's archive
(`openspec/changes/archive/2026-10-10-cut-the-engines/`), and the probes
recorded in design.md.
