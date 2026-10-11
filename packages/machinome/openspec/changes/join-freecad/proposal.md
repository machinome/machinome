## Why

The pilot's plan for the joins of Machinome 0.9 (`workflow/ongoing/joins-0.9.md`
at the repository root, set on 11 October 2026) names this change its first
cycle: machinome-freecad, the native FreeCAD assembly adapter born from the
Dum-E project, joins the repository as the extension package
`machinome-node-freecad`, the module `machinome.node.freecad`, installed by
`machinome[freecad]`, its history imported to its final paths. The probes in
design.md find the product cannot be used today against the framework it would
join: on the line's head every one of its four test modules fails at collection
(`from machinome.node import AssemblyNode` is refused since `root-cleanup`), and
behind that import its leaf still names `machinome.node.exact_leaf`, leaf
contract 1 and `machinome.occt.engine`, all gone in 0.8. Dum-E, the originating
project, imports `machinome_freecad`, which no index serves, so the universe
sweep has reported it unexpected since `root-cleanup`. The join is the plan's
remedy: one repository, one version, one licence, the product's tests in the
framework's suite.

## What Changes

- **The join, by the orchestrator, after the planning commit**: a fresh clone
  of machinome-freecad rewritten by `git filter-repo` with the mapping of
  design.md Decision 2 (51 of the product's 60 tracked files land at their
  final paths, 9 are dropped), its branch `lean-core-validation` merged with
  `--allow-unrelated-histories`; rehearsed in the scratch directory, where
  the merge is clean and `git log --follow` on the adapter at its new path
  reaches the commit of 1 October 2026 that wrote it.
- **`machinome-node-freecad` founded under `packages/`** in the shape of the
  OpenSCAD package (ADR-183): its manifest (version 0.8.1, `machinome~=0.8.1`,
  `machinome-engine-brep~=0.8.1`, `numpy`, `scipy`, the set's licence), a README
  in the shape of the ten, the links `LICENSE` and `LICENSES`, and the package
  directory `machinome/node/freecad/` with `__init__.py`, `adapter.py`,
  `runtime.py` and `worker.py`; its `__init__` checks the OCCT binding with
  `require_extra('freecad', ...)` (Decisions 3 and 4).
- **The adapter onto today's core**, four import lines (Decision 5): the
  assembly base from `machinome.node.assembly`, the occurrence leaf on
  `BrepLeafNode` with leaf contract 3, its solid count through the B-rep
  engine's seam. Probed: the product's 82 tests pass on the bench's venv with
  FreeCAD 1.1.4 once those and one test line (`leaf.exact` to `leaf.brep`) are
  changed; Dum-E's seven tests pass and its posed snapshot is byte-identical to
  the one recorded on 1 October 2026.
- **The core names it once**: the row `'freecad': NodeType(('FreeCADAssemblyNode',
  'FreeCADJoint'))` in the table of supported node types, so an absent package
  is refused by its extra at every door (ADR-184, no edit to the finder); the
  extra `freecad` and `all`; the workspace's sources, lock and sync; the root's
  `.bumpversion.cfg`; `scripts/check-dist`'s row, whose smoke runs the native
  fixture to its enabled limit where `MACHINOME_FREECAD_ROOT` is set and checks
  the refusal naming it where it is not (Decisions 6 to 9).
- **Its tests join the framework's suite** as `tests/test_freecad_*.py`, their
  helpers as `tests/freecad_*.py` and their 27 FCStd fixtures under
  `tests/fixtures/freecad/`; each test module is skipped by one guard, naming
  `MACHINOME_FREECAD_ROOT`, where the variable is unset (Decision 10). The
  fixtures are regenerated with the set's licence in their document metadata
  (Decision 11; Open Questions 4).
- **Its record joins the framework's**: its spec `native-freecad-assembly`
  joins the framework's specs, its archived change the framework's archive
  under its own date, its workflow archive as
  `workflow/archive/native-freecad-assembly-2026-10-01/`, verbatim; its
  `docs/api.md` becomes the how-to guide `howto/freecad-assemblies`, and
  `docs/runtime.md` that guide's runtime section and the installation page's
  row; the provenance of its `NOTICE.md` joins `CREDITS.md` (Decisions 2, 12
  and 13).
- **One licence at the join**: the product's licence file and notice are
  dropped by the import; every file it brings states the set's expression; the
  records this change writes name no licence the product carried.
- **Records**: the `Unreleased` bullets of `HISTORY.rst` and the manual's
  changelog, the installation page, the backends guide, the API reference, the
  architecture Map, `CONTRIBUTING.rst`, the root `README.md`, ADR-185
  (recommended, Open Questions 1), and two findings in `workflow/warts.md`:
  `machinome vet` and the leaf-contract reach gate do not read the package
  (Decision 14).
- **Validation in the originating project**, by the orchestrator: Dum-E moved
  onto `machinome.node.freecad` in its own repository and run on the bench's
  venv with the runtime set (Decision 15).

Not in this change: teaching `machinome vet` the attribute `freecad_source`
(Open Questions 2), the leaf-contract reach gate over the adapter (Open
Questions 3), FreeCAD in CI, any version bump, any upload or push, the original
repository's fate on GitHub, and the other four joins.

## Capabilities

### New Capabilities

None. `native-freecad-assembly` arrives as a baseline spec by the import itself
(design.md Decision 2), so this change modifies it.

### Modified Capabilities

- `native-freecad-assembly`: the public import is `machinome.node.freecad`;
  the requirement on the separate optional package is renamed and restated for
  the distribution `machinome-node-freecad` of the repository, installed by
  `machinome[freecad]`, its provenance in `CREDITS.md`, its tests skipped
  without the runtime (new scenario).
- `kernel-extras`: the `freecad` extra and its distribution, which requires
  the B-rep engine (new scenario); the FreeCAD package checks the OCCT binding
  at import and its adapter imports it, alone among its modules; an absent
  FreeCAD package is refused by its extra (new scenario).
- `node-model`: the table of supported node types gains the FreeCAD node type,
  a package whose node is an assembly (new scenario).
- `framework-identity`: the extension packages include `machinome-node-freecad`,
  a package portion like the OpenSCAD family's, whose record is the framework's
  although it joined from its own repository; `check-dist` smokes it (new
  scenario).
- `framework-contributor-guidance`: the install without uv names the FreeCAD
  package directory.
- `user-documentation`: a how-to guide for native FreeCAD assemblies, the
  installation row, the backends row and the reference entries (new
  requirement).

`vet` is unchanged; its gap is a finding (Open Questions 2).

## Impact

- **Tree.** The join adds 51 files: six in `packages/machinome-node-freecad/`
  (README, manifest, four modules), the rest under `packages/machinome/`
  (one manual page, seven test modules and helpers, 27 FCStd documents and a
  README, one baseline spec, five archived change files, three workflow
  archive files). The cycle adds the two licence links, `tests/freecad_support.py`
  and ADR-185, and edits what Decisions 3 to 14 name.
- **Code.** `machinome/node/supported.py` gains one row; the core's manifest one
  extra and `all`; no other core module changes. The product's modules change
  their headers and the four import lines of Decision 5.
- **Tests.** Joining: four modules, 82 tests with FreeCAD (four skipped modules
  without). Changed: `test_repository_layout.py`, `test_kernel_extras.py`,
  `test_core_kernel_free.py`, `test_supported_node_types.py`,
  `test_node_root_exports_nothing.py`, `test_core_names_no_split_words.py`,
  `test_docs_structure.py`; design.md probe 6 lists every gate the join alone
  turns red.
- **Build and CI.** Twelve members build from `packages/`; `check-dist` gains a
  row; CI's lint and test jobs read `packages/machinome-*` already and run the
  FreeCAD tests as skips.
- **Records.** ADR-185 (recommended); six delta specs; `HISTORY.rst`;
  `CREDITS.md`; the manual's changelog, installation page, backends guide,
  reference and a new how-to; the architecture Map; two warts.

Originating evidence: the campaign plan (`workflow/ongoing/joins-0.9.md`, "The
method" and cycle 1), the product's own record (its spec, its archived change
`2026-10-01-native-freecad-assembly`, its workflow archive), Dum-E's issues
DUME-005 and DUME-006, and the probes recorded in design.md.
