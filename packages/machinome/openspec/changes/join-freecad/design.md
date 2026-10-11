## Context

The first cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` at the repository root, cycle 1, set by the
pilot on 11 October 2026), cut from the line `v0.9-joins` at cf631645, whose
head is the campaign plan on top of c6a3ad4f (the cut of the ten extension
packages, `cut-the-mesh-nodes`), on the bench
`machinome/WTs/v0.9-joins-join-freecad`. The decisions of `monorepo-0.9.md`
still hold: the record of an extension package is the framework's (1); one
version for the set, `~=` pins both ways (2); a uv workspace at the root, every
member editable in compat mode (3). The joins plan adds its method: a product
is imported by rewriting its history directly to its final paths, merged with
`--allow-unrelated-histories` by the orchestrator after the cycle's planning
commit; one licence at the join, the product's own licence file and notice
removed, its third-party provenance kept in `CREDITS.md`; the product takes the
set's version; the original repository stays as it is.

machinome-freecad is the native FreeCAD assembly adapter born from the Dum-E
project (`projects/Robotic-Arms/Dum-E`): its branch `lean-core-validation` at
5ed665f, four commits of 1 and 3 October 2026, the whole of its history, its
`main` at 5ed665f's parent b5b6233, never published. It exports
`FreeCADAssemblyNode` and `FreeCADJoint` from `machinome_freecad`; its runtime
is an independently installed FreeCAD 1.1.4 found through
`MACHINOME_FREECAD_ROOT`, run as a separate process whose Python executes the
package's `worker.py`. Its ratified contract is its spec
`native-freecad-assembly` (nine requirements), its archived change
`2026-10-01-native-freecad-assembly`, and three workflow records.

Paths below are the repository's when they start with `packages/` or name a
root file, the framework directory's otherwise. Facts were read on the bench at
cf631645 and in the product's worktree at 5ed665f unless marked *inferred*.
Probes ran in the scratch directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C1-propose/`
(named `<scratch>` below), never in the bench, the product or a project, with
the bench's synced venv (`<bench>/.venv`, 187 packages, from the lock), uv
0.11.8, git-filter-repo `ed61b4050b71`, OpenSCAD 2021.01, the OpenSpec CLI
1.6.0 and the FreeCAD 1.1.4 extraction at
`projects/Robotic-Arms/Dum-E/.tools/freecad-1.1.4/squashfs-root` (named
`<freecad>`).

### What the join touches

- **The product's 60 tracked files** at 5ed665f: `README.md`, `LICENSE`,
  `NOTICE.md`, `MANIFEST.in`, `.gitignore`, `pyproject.toml` (name
  `machinome-freecad`, version 0.1.0, `dependencies = ["machinome"]`, a
  `test` extra), `scripts/smoke_dist.py`; `docs/api.md` and `docs/runtime.md`;
  the module `machinome_freecad/` (`__init__.py` lazy, exporting the two names
  through `__getattr__`; `adapter.py`, 316 lines, the two classes and the
  occurrence leaf; `runtime.py`, 120 lines, the runtime lookup, the worker
  process and the snapshot cache; `worker.py`, 275 lines, run only by
  FreeCAD's Python); `openspec/config.yaml` (the template, no context),
  `openspec/specs/native-freecad-assembly/spec.md` and the five files of
  `openspec/changes/archive/2026-10-01-native-freecad-assembly/`;
  `workflow/README.md` and the three files of
  `workflow/archive/native-freecad-assembly/`; `tests/pyproject.toml`
  (`[tool.machinome] model = "test_public:Machine"`), four test modules
  (`test_public.py`, `test_constraints.py`, `test_diagnostics.py`,
  `test_freshness.py`), three helpers (`generate_fixtures.py` and
  `native_reference.py`, run by FreeCAD's Python; `origin_model.py`, a module
  declaring a node with a relative source), and `tests/fixtures/`: 26 FCStd
  documents, `assembly-dir/Assembly.FCStd` and a README.
- **History.** Earlier paths exist only in history: the change under
  `openspec/changes/native-freecad-assembly/` (renamed into the archive in
  b5b6233) and `workflow/ongoing/dume-native-freecad.md` (renamed into the
  workflow archive in b5b6233). The product has three branches (`main` and
  `native-freecad-assembly` at b5b6233, `lean-core-validation` at 5ed665f) and
  no tags.
- **The licence the product carried** is stated in `LICENSE`, `NOTICE.md`,
  the README, every source file's SPDX line, `tests/fixtures/README.md`,
  `docs/runtime.md`, the generator's three document-metadata assignments and,
  through them, the metadata of all 27 FCStd documents (two strings each), the
  baseline spec's Purpose and its last requirement's title and text, and the
  archived change and workflow records. Third-party provenance is in
  `NOTICE.md`: FreeCAD 1.1.4 (git `4fd3bf320d9566a27e60069fc8387448aaa3a094`)
  called, the Assembly workbench's Python sources and OndselSolver's
  `FixedJoint.cpp`, `RevoluteJoint.cpp`, `AtPointJoint.cpp` and
  `DirectionCosineConstraintIJ.cpp` at `30e9b64e8bf881d438d4b88834f9ba3674865418`
  read, the worker's `constraint_residual` adapting their mathematical
  zero-target constraints, Ondsel's copyright retained for those conventions,
  no implementation copied.
- **The core.** `machinome/node/supported.py` (the table, eight rows),
  `machinome/node/__init__.py` (`_AbsentNodeType`, ADR-184, generic over the
  table), the core's `pyproject.toml` extras, the root's `pyproject.toml`
  sources, `.bumpversion.cfg`, `scripts/check-dist` (`SMOKES`, one row per
  member; a member without a row fails the script), `.github/workflows/python-app.yml`
  (lint over `../machinome-*/machinome`, CI with OpenSCAD and no FreeCAD),
  `CREDITS.md`, `HISTORY.rst` (one `Unreleased` section).
- **The manual** builds `.rst` only (`docs/conf.py` has no Markdown parser);
  `tests/test_docs_structure.py` pins the navigation, the installation page's
  extras and distributions, and that no page spells a licence identifier but
  the viewer's or a publication caveat outside the status page. The
  `user-documentation` requirement "The manual imports every name from its
  module" asks the backends guide to list every node class with its module and
  extra.
- **The originating project.** Dum-E imports `machinome_freecad` in
  `simulation/dume.py`, `simulation/test_preparation.py` and
  `simulation/tools/environment.py`, and declares `machinome==0.7.1` and
  `machinome-freecad==0.1.0`. Its `docs/issues.md` records DUME-006: vet
  reports `outside-universe machinome_freecad` and does not model
  `freecad_source`.

### Probes

1. **The product on today's core, as it is.** A clone of
   `lean-core-validation` (`<scratch>/freecad-run`), its suite run from there
   on the bench's venv with `MACHINOME_FREECAD_ROOT=<freecad>`: 4 errors in
   4.46 s, every module refused at collection by `from machinome.node import
   AssemblyNode` (`root-cleanup`, ADR-181). Nothing runs.
2. **The smallest port, in scratch only** (`<scratch>/freecad-port`, diff in
   `<scratch>/scratch-port.diff`): `from machinome.node.assembly import
   AssemblyNode`; `machinome.node.exact_leaf.ExactLeafNode` with
   `leaf_contract = 1` to `machinome.node.brep_leaf.BrepLeafNode` with
   `leaf_contract = 3`; `machinome.occt.engine.solid_count` to
   `machinome.engine.brep`'s. With the root: 80 passed, 1 failed, 1 skipped in
   140.23 s; the failure `test_exact_geometry_transfer_and_fixed_leaf_occurrences`,
   `'_Solid' object has no attribute 'exact'` (ADR-180 renamed the member
   `brep`); with that test line changed it passes. The skip is the external
   untouched Dum-E refusal, which needs `MACHINOME_FREECAD_DUME_SOURCE`. The
   solid count through the engine's seam (`require_brep_engine(...).solid_count`,
   as `machinome.node.step` reaches the engine) in place of the provider
   import: `test_public.py` 31 passed in 83.37 s.
3. **Without the runtime.** The ported suite with `MACHINOME_FREECAD_ROOT`
   unset: 55 failed, 6 errors, 20 passed, 1 skipped in 4.24 s. No test skips
   for want of the runtime today. Of the 20 that pass, 14 need no runtime (ten
   residual-arithmetic tests and `test_unknown_residual_convention_is_refused`
   of `test_constraints.py` on the worker's `constraint_residual`,
   `test_worker_solver_refusal_names_native_candidates`,
   `test_foreign_reference_refused_without_native_load` and
   `test_optional_runtime`, which unsets the variable itself); the six
   `test_native_refusals[...]` pass for the wrong reason, the missing runtime
   being the `ValueError` they expect.
4. **The import, rehearsed** on a fresh clone of the product
   (`<scratch>/freecad-rw`) with the command of Decision 2: 4 commits parsed,
   every branch rewritten, `lean-core-validation` at 7e5b228a, `main` and
   `native-freecad-assembly` at fc69a67a. Its tree holds 51 files, listed in
   `<scratch>/rehearsal-ls-files.txt`, and no commit of any branch touches a
   path outside `packages/`. `git log --follow` on
   `packages/machinome-node-freecad/machinome/node/freecad/adapter.py` lists
   7e5b228a (3 October) and fc69a67a (1 October), the commit that wrote it;
   `git log` on the archived design and the workflow note at their final paths
   reaches the first commit, d08fe44, without `--follow`. None of the 51 paths
   exists in the bench. Then, in a scratch clone of the bench's branch
   (`<scratch>/merge-rehearsal`), `git fetch <scratch>/freecad-rw
   lean-core-validation` and `git merge --allow-unrelated-histories
   FETCH_HEAD`: no conflict, 51 files created; `git log --follow` on the
   adapter reaches fc69a67a from the merged tree and `git blame` attributes
   the worker's first lines to it.
5. **OpenSpec on a joined spec** (`<scratch>/os-probe`, the CLI 1.6.0): a
   change whose `## ADDED Requirements` repeats a requirement the baseline
   already holds validates, and its archive aborts, "cap ADDED failed for
   header ... - already exists. Aborted. No files were changed."; a change
   with `## RENAMED Requirements` (FROM, TO) and the requirement under its new
   title in `## MODIFIED Requirements` archives ("~ 1 modified, → 1
   renamed"), the baseline's Purpose untouched; a MODIFIED delta whose
   capability has no baseline yet validates. The import lands the product's
   spec at `openspec/specs/native-freecad-assembly/spec.md` before this
   change's archive, so its delta is MODIFIED and RENAMED, not ADDED
   (Decision 16).
6. **The gates at the join**, the rehearsed merge's tree, its suite modules
   run with the bench's venv from `<scratch>/merge-rehearsal/packages/machinome`.
   Red for the join: `test_every_member_is_a_workspace_source`,
   `test_every_sibling_is_in_the_table`,
   `test_the_guide_installs_every_member_without_uv` and
   `test_the_readme_links_every_package_and_states_the_licence`
   (`test_repository_layout.py`); `test_every_member_is_numbered_with_the_core`
   (0.1.0), `test_every_pin_between_members_is_compatible` (`machinome`
   unpinned) and `test_the_version_is_bumped_from_the_root`
   (`test_release_records.py`); `test_the_extension_packages_import_only_their_kernels`
   (the adapter imports `OCP`); `test_no_module_names_the_split_but_by_its_two_words`
   (the adapter's `exact_leaf`, `ExactLeafNode` and `machinome.occt`, the
   worker's result key `'occt'`); `test_no_file_of_the_three_zones_spells_a_former_root_name`
   (the adapter's `from machinome.node import AssemblyNode`). Every other red
   of that run is the rehearsal's own (the bench venv's editable `.pth` lines
   name the bench's directories, so `test_each_portion_resolves_from_its_package`
   and the absent-package doors read the bench, not the clone) and is not
   counted. `test_core_names_no_scad.py`, `test_docs_structure.py`,
   `test_kernel_extras.py`, `test_leaf_capability_set.py`,
   `test_leaf_contract_reach.py`, `test_machinome_identity.py` and
   `test_no_class_name_recognition.py` pass on the joined tree.
7. **Dum-E on the package, in scratch.** A copy of Dum-E without its FreeCAD
   extraction and build directories (`<scratch>/dume`, 33 MB). With the scratch
   port on `PYTHONPATH` as `machinome_freecad`: `simulation/test_dume.py` 4
   passed in 22.98 s; `machinome vet` exit 1, `outside-universe
   machinome_freecad`. Then the port placed as a portion
   (`<scratch>/portion/machinome/node/freecad/`, its own `__init__.py`, none
   above) and the copy's three imports moved to `machinome.node.freecad`
   (`<scratch>/dume-moved`): `machinome.node.freecad` resolves from the
   portion; `test_dume.py` 4 passed in 22.89 s; `test_preparation.py` 3 passed
   in 15.24 s (the corrected source admitted, the untouched original refused
   with its joint residual, the native preparation reproduced); `machinome
   vet` exit 0, `simulation.dume:DumE pure`; `machinome snapshot -o
   <scratch>/dume-posed.png --autocenter --drive turn=70 --drive shoulder=15
   --drive elbow=110 --drive wrist=-25 --imgsize 1280x960`, exit 0, an image
   of the arm on its base, turned and articulated, whose SHA-256
   `40f8d56813970cbfc958c9e7e532646d2e31b20d754989271b42c20aecf3b804` equals
   that of Dum-E's `snapshot-corrected-posed.png` of 1 October 2026 under
   0.7.1, every pixel equal. `git -C <Dum-E> status --short` was empty
   afterwards.
8. **The fixtures regenerated** (`<scratch>/freecad-regen`): the generator's
   three `License` and `LicenseURL` assignments set to the set's expression
   and the repository's `LICENSE` URL, run with `<freecad>/AppRun python`:
   exit 0, "Generated native synthetic fixtures", all 27 documents rewritten,
   with a `.FCBak` backup beside each (26 counted in the fixture directory,
   `assembly-dir/` not listed). Each regenerated document carries the
   former licence string 0 times and the set's expression once. With the root
   and `MACHINOME_FREECAD_DUME_SOURCE` set to Dum-E's untouched
   `upstream/MA_Dum_E_v2_Assembly.FCStd`: 82 passed in 144.98 s, the external
   refusal among them.
9. **The leaf-contract reach gate's own functions on the ported adapter**
   (`tests/test_leaf_contract_reach.py`'s `_reaches` and
   `_undeclared_imports`): two reaches, `imports machinome.currency` (line 147,
   the leaf's `materialize`) and `reads private base member
   self._link_children` (line 306, the assembly); eleven undeclared imports
   with the provider import of probe 2, ten through the seam
   (`machinome.node.assembly`, `machinome.motion.couplings` three names,
   `machinome.motion.joints`, `machinome.motion.ports` two,
   `machinome.node.operations` two, `machinome.currency`). `runtime.py`,
   `__init__.py` and `worker.py`: none.
10. **Lint.** `flake8 --max-line-length=89` on the port: 114 lines on its
    modules, 614 on its tests; the base's count over the core and the ten
    packages is 759.

## Goals / Non-Goals

**Goals:**

- machinome-freecad joins as `machinome-node-freecad` with its whole history,
  every file at its final path, the merge rehearsed and clean.
- The package in ADR-183's shape, refused by its extra when absent under
  ADR-184 with no edit to the finder, numbered and pinned with the set, built
  and smoked by `scripts/check-dist`.
- The adapter working on today's core with the fewest edits, its 82 tests
  green with the runtime and skipped, module by module, without it.
- The product's spec, archived change and working record joining the
  framework's; its documentation joining the manual by reader intent; its
  provenance joining `CREDITS.md`; one licence.
- Dum-E, the originating project, loading and passing its own tests on the
  bench through `machinome.node.freecad`.

**Non-Goals:**

- Any change to the adapter's behaviour, its native acceptance recipe, its
  tolerances or its refusals; any reformatting of its code.
- Teaching `machinome vet` the attribute `freecad_source`, or extending the
  leaf-contract reach gate to the adapter (findings, Decision 14).
- FreeCAD in CI, a FreeCAD wheel, any version bump, upload or push, and the
  original repository's fate on GitHub.
- The joins of mechanics, the viewer, the videomaker and the studio.

## Decisions

### 1. The shape of the package

`packages/machinome-node-freecad/` holds `pyproject.toml`, `README.md`, the
links `LICENSE -> ../../LICENSE` and `LICENSES -> ../../LICENSES`, and the
package directory `machinome/node/freecad/` with its own `__init__.py` and
the three modules `adapter.py`, `runtime.py` and `worker.py`, no
`__init__.py` at `machinome/` or `machinome/node/`: the OpenSCAD package's
shape (ADR-183, its consequence of 10 October 2026). The module names stay the
product's: `adapter.py` names its siblings by file (`Path(__file__).with_name`
for `adapter.py`, `runtime.py` and `worker.py`, which join the native recipe's
contributors), `runtime.py` runs `worker.py` by path, and the archived records
name all three. Alternative: one module `machinome/node/freecad.py`; refused,
because the worker must be a separate file FreeCAD's interpreter runs, and the
package is the address the plan names.

### 2. The mapping and the import

Every tracked file of the product, old path to new path, or dropped:

| at 5ed665f | lands at | reason |
|---|---|---|
| `README.md` | `packages/machinome-node-freecad/README.md` | the package's README; rewritten in place by the applier (Decision 3) |
| `pyproject.toml` | `packages/machinome-node-freecad/pyproject.toml` | the package's manifest; rewritten in place by the applier (Decision 3) |
| `machinome_freecad/__init__.py`, `adapter.py`, `runtime.py`, `worker.py` | `packages/machinome-node-freecad/machinome/node/freecad/` | the portion at its address (Decision 1) |
| `docs/api.md` | `packages/machinome/docs/howto/freecad-assemblies.rst` | the how-to guide; Markdown at the join, converted in place by the applier (Decision 12) |
| `tests/test_public.py` | `packages/machinome/tests/test_freecad_public.py` | joins the core suite, its name saying freecad |
| `tests/test_constraints.py` | `packages/machinome/tests/test_freecad_constraints.py` | as above |
| `tests/test_diagnostics.py` | `packages/machinome/tests/test_freecad_diagnostics.py` | as above |
| `tests/test_freshness.py` | `packages/machinome/tests/test_freecad_freshness.py` | as above |
| `tests/native_reference.py` | `packages/machinome/tests/freecad_native_reference.py` | a helper FreeCAD's Python runs; not `test_*`, never collected |
| `tests/origin_model.py` | `packages/machinome/tests/freecad_origin_model.py` | a helper module a test imports; never collected |
| `tests/generate_fixtures.py` | `packages/machinome/tests/freecad_generate_fixtures.py` | the fixtures' generator, FreeCAD's Python runs it; never collected |
| `tests/fixtures/` (26 FCStd, `assembly-dir/Assembly.FCStd`, `README.md`) | `packages/machinome/tests/fixtures/freecad/` | where the suite keeps fixtures, in a directory of their own |
| `openspec/specs/native-freecad-assembly/spec.md` | `packages/machinome/openspec/specs/native-freecad-assembly/spec.md` | joins the framework's specs |
| `openspec/changes/archive/2026-10-01-native-freecad-assembly/` (5 files), and its earlier path `openspec/changes/native-freecad-assembly/` | `packages/machinome/openspec/changes/archive/2026-10-01-native-freecad-assembly/` | joins the framework's archive under its own date; both spellings to the final path, so its history reads there without `--follow` |
| `workflow/archive/native-freecad-assembly/` (3 files), and the earlier `workflow/ongoing/dume-native-freecad.md` | `packages/machinome/workflow/archive/native-freecad-assembly-2026-10-01/` | joins the framework's archive, named `<campaign>-<YYYY-MM-DD>` by `workflow/README.md`, dated by its change's archive |
| `LICENSE` | dropped | one licence at the join; the package links the root's |
| `NOTICE.md` | dropped | it states the licence the product carried; its provenance is written into `CREDITS.md` (Decision 13) |
| `MANIFEST.in` | dropped | none of the ten carries one; the core's ships the tests and the manual |
| `.gitignore` | dropped | the root's and the framework's cover the build leavings; its `*.FCBak` is not needed once the generator's backups are removed (Decision 11) |
| `scripts/smoke_dist.py` | dropped | replaced by `scripts/check-dist`'s row (Decision 9); it pins machinome 0.7.1 and a frozen checkout |
| `openspec/config.yaml` | dropped | the template with no context; the framework's governs, and it would collide with the framework's file |
| `workflow/README.md` | dropped | the framework's governs, and it would collide with the framework's file |
| `tests/pyproject.toml` | dropped | the suite's `tests/pyproject.toml` already makes `tests/` a machinome project, and it would collide with that file |
| `docs/runtime.md` | dropped | its reader's content becomes the how-to guide's runtime section and the installation page's row, its developer's content the fixtures' README (Decisions 11 and 12); it states the licence the product carried and that the package is unreleased, and no page of the manual may say either |

The import lands files only where the applier would otherwise move them: the
README and the manifest at the package's directory, which the applier rewrites
in place; `docs/api.md` at the guide's path, which the applier converts in
place. A move and an edit never share a commit: the join moves, the
implementation commit edits. A dropped file is absent from every rewritten
commit; the original repository keeps it, with the original hashes. The
rewritten commits keep their messages, authors and dates.

The command, run by the orchestrator in a fresh clone (`git clone
file:///home/asa/devel/machinome/machinome-freecad <dir>`), as rehearsed in
probe 4 (its text is `<scratch>/filter-repo-command.sh`):

```
git filter-repo \
  --path LICENSE --path NOTICE.md --path MANIFEST.in --path .gitignore \
  --path scripts/smoke_dist.py --path openspec/config.yaml \
  --path workflow/README.md --path tests/pyproject.toml --path docs/runtime.md \
  --invert-paths \
  --path-rename README.md:packages/machinome-node-freecad/README.md \
  --path-rename pyproject.toml:packages/machinome-node-freecad/pyproject.toml \
  --path-rename machinome_freecad/:packages/machinome-node-freecad/machinome/node/freecad/ \
  --path-rename docs/api.md:packages/machinome/docs/howto/freecad-assemblies.rst \
  --path-rename tests/test_public.py:packages/machinome/tests/test_freecad_public.py \
  --path-rename tests/test_constraints.py:packages/machinome/tests/test_freecad_constraints.py \
  --path-rename tests/test_diagnostics.py:packages/machinome/tests/test_freecad_diagnostics.py \
  --path-rename tests/test_freshness.py:packages/machinome/tests/test_freecad_freshness.py \
  --path-rename tests/native_reference.py:packages/machinome/tests/freecad_native_reference.py \
  --path-rename tests/origin_model.py:packages/machinome/tests/freecad_origin_model.py \
  --path-rename tests/generate_fixtures.py:packages/machinome/tests/freecad_generate_fixtures.py \
  --path-rename tests/fixtures/:packages/machinome/tests/fixtures/freecad/ \
  --path-rename openspec/specs/native-freecad-assembly/:packages/machinome/openspec/specs/native-freecad-assembly/ \
  --path-rename openspec/changes/native-freecad-assembly/:packages/machinome/openspec/changes/archive/2026-10-01-native-freecad-assembly/ \
  --path-rename openspec/changes/archive/2026-10-01-native-freecad-assembly/:packages/machinome/openspec/changes/archive/2026-10-01-native-freecad-assembly/ \
  --path-rename workflow/ongoing/dume-native-freecad.md:packages/machinome/workflow/archive/native-freecad-assembly-2026-10-01/dume-native-freecad.md \
  --path-rename workflow/archive/native-freecad-assembly/:packages/machinome/workflow/archive/native-freecad-assembly-2026-10-01/ \
  --tag-rename ':freecad-'
```

filter-repo applies path arguments in order, so the drops are matched against
the original paths and every rename is a disjoint, explicit prefix; there is no
catch-all `--to-subdirectory-filter`, because no part of the product moves
whole into one directory. `--tag-rename` is the plan's method and renames
nothing here: the product has no tag. The orchestrator then checks that
`git ls-tree -r --name-only lean-core-validation` lists the 51 paths of
`<scratch>/rehearsal-ls-files.txt` and that the branch's head is 7e5b228a, as
rehearsed (*inferred* deterministic: same input, same options); fetches
`lean-core-validation` from that clone into the bench; and merges it with
`git merge --allow-unrelated-histories` into the cycle's branch, one merge
commit, after the planning commit. The branches `main` and
`native-freecad-assembly`, at fc69a67a, are ancestors of the merged head and
are not fetched as branches.

### 3. The manifest and the README, verbatim

`packages/machinome-node-freecad/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-node-freecad"
version = "0.8.1"
description = "The FreeCAD node type of Machinome: a native FreeCAD assembly, read by FreeCAD"
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
    # The core this node type is a portion of, released with it: the set
    # carries one version, and the pins between its packages are ~= both
    # ways.
    "machinome~=0.8.1",
    # Each occurrence is a B-rep leaf, whose solid FreeCAD hands over as
    # BREP and the package reads through the OCCT binding, whose range the
    # B-rep engine states once.
    "machinome-engine-brep~=0.8.1",
    # Arrays and the rotation of a native placement; the core pins numpy's
    # range and requires scipy. FreeCAD itself, the program that reads the
    # document, is no package's to install: it is found through
    # MACHINOME_FREECAD_ROOT.
    "numpy",
    "scipy",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

[tool.setuptools.packages.find]
# The node package machinome/node/freecad/, which has its own __init__.py,
# with none at machinome/ or machinome/node/, so the core's package path
# admits it.
include = ["machinome.node.freecad"]
namespaces = true
```

`packages/machinome-node-freecad/README.md`, replacing the product's:

```markdown
# machinome-node-freecad

The FreeCAD node type of [Machinome](https://github.com/machinome/machinome):
the package `machinome.node.freecad`, whose `FreeCADAssemblyNode` is a whole
native [FreeCAD](https://www.freecad.org) assembly, read by FreeCAD itself in
a separate process with its fixed and revolute joints and their enabled
limits, and whose `FreeCADJoint` names one of its revolutes for a driver.
FreeCAD is installed apart and found through `MACHINOME_FREECAD_ROOT`.

## Install

    pip install "machinome[freecad]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

### 4. The package's `__init__.py` and the headers

`machinome/node/freecad/__init__.py`, replacing the product's twelve lines;
it keeps their lazy `__getattr__`, so importing the package opens no document
and imports neither the adapter nor numpy:

```python
# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The FreeCAD node type: `FreeCADAssemblyNode`, a whole native FreeCAD
assembly read by FreeCAD itself, and `FreeCADJoint`, one of its revolutes.

- `machinome.node.freecad.adapter`: the two classes, which compile the native
  assembly into ordinary nodes, joints and B-rep leaves;
- `machinome.node.freecad.runtime`: the FreeCAD runtime named by
  `MACHINOME_FREECAD_ROOT`, its worker process and the snapshot cache;
- `machinome.node.freecad.worker`: the script FreeCAD's own Python runs,
  which reads the document through FreeCAD's API.

Importing this package or declaring a class opens no document and needs no
FreeCAD runtime; constructing an instance does. The occurrences' solids are
read through the OCCT binding, whose absence is refused here with the line
that installs it (OpenSpec change `join-freecad`, capabilities
`native-freecad-assembly` and `kernel-extras`).
"""

from machinome.extras import require_extra

require_extra('freecad',
              'machinome.node.freecad (FreeCADAssemblyNode, FreeCADJoint)',
              'OCP')

__all__ = ['FreeCADAssemblyNode', 'FreeCADJoint']


def __getattr__(name):
    if name in __all__:
        from .adapter import FreeCADAssemblyNode, FreeCADJoint
        globals().update(FreeCADAssemblyNode=FreeCADAssemblyNode,
                         FreeCADJoint=FreeCADJoint)
        return globals()[name]
    raise AttributeError(name)
```

The check names `OCP` because the adapter imports it, which the
`kernel-extras` rule "each module that imports a kernel calls its extra's
`require_extra` before any kernel import" asks of the package, as the OpenSCAD
package checks SolidPython in its `__init__`. FreeCAD is not checked here: it
is a program, not a module, and the ratified contract refuses its absence when
an instance is constructed.

Every other Python file the product brings, the package's three other modules
and the seven test modules and helpers, opens with the framework's header in
place of its two copyright and SPDX lines:

```
# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
```

`test_freecad_public.py`, which has no header, gains it, and its docstring
becomes `"""The FreeCAD node package's public contract, on synthetic native
fixtures."""`. The worker keeps its third line, `# Residual conventions derived
from OndselSolver: Copyright (c) 2023 Ondsel, Inc.`, and its fourth becomes `#
Original Python adaptation added 2026-10-01; see the framework's CREDITS.md.`

### 5. The adapter on today's core

Four edits in `adapter.py`, each one of probe 2 or its seam variant, and
nothing else in the module:

- `from machinome.node import AssemblyNode` becomes `from
  machinome.node.assembly import AssemblyNode`.
- In `_leaf_class`, `from machinome.node.exact_leaf import ExactLeafNode`
  becomes `from machinome.node.brep_leaf import BrepLeafNode`, and `class
  _Solid(_NativeCurrency, ExactLeafNode):` with `leaf_contract = 1` becomes
  `class _Solid(_NativeCurrency, BrepLeafNode):` with `leaf_contract = 3`.
- In `_Solid.render`, `from machinome.occt.engine import solid_count` becomes
  `from machinome.engine import require_brep_engine`, and the check `if not
  solid_count(shape) or ...` becomes

  ```python
            engine = require_brep_engine(f'FreeCAD occurrence {self.name}',
                                         'its native solid is read')
            if not engine.solid_count(shape) or not BRepCheck_Analyzer(shape).IsValid():
  ```

The seam rather than the provider: `machinome.node.step` reaches the engine
the same way, and an absent engine is then refused by its extra's line. The
`kernel-extras` delta records the adapter's direct `OCP` import, which stays
for `BRepTools.Read_s` from a stream and `BRepCheck_Analyzer`, neither of which
the engine offers. `runtime.py` changes its header only.

### 6. The core: one row, one extra

- `machinome/node/supported.py`: after the `stl` row,
  `'freecad': NodeType(('FreeCADAssemblyNode', 'FreeCADJoint')),`. No renderer,
  no command. The node root's refusal of each class, `load`'s refusal and the
  last finder's (ADR-184) follow from the row with no other edit.
- The core's `pyproject.toml`: after the `stl` extra,

  ```toml
  # `machinome.node.freecad` (FreeCADAssemblyNode, FreeCADJoint), which reads
  # a native FreeCAD assembly through FreeCAD, a program no pip extra
  # installs, found through MACHINOME_FREECAD_ROOT; its occurrences are B-rep
  # leaves, so the distribution requires the B-rep engine.
  freecad = [
      "machinome-node-freecad~=0.8.1",
  ]
  ```

  `all` becomes `"machinome[cadquery,build123d,step,molejo,brep,mesh,openscad,solid2,jscad,stl,freecad]"`,
  and the `dependencies` comment's list of node extras gains `freecad`
  ("(the extras `cadquery`, `build123d`, `step`, `molejo`, `openscad`,
  `solid2`, `jscad`, `stl` and `freecad`)"). The `dev` extra includes `all`,
  so the workspace installs the package and the suite imports it.

### 7. The workspace

The root `pyproject.toml`'s sources gain `machinome-node-freecad = { workspace
= true }` between `machinome-node-cadquery` and `machinome-node-jscad`. Then
`uv lock` (expected *inferred*: 188 packages, "Added machinome-node-freecad
v0.8.1") and `uv sync --python 3.12` (expected: twelve `__editable__` `.pth`
files, each holding its package directory). The lock adds no third-party
package: every requirement of the new manifest is already locked.

### 8. One version for the set

The root `.bumpversion.cfg` gains, after the `stl` package's two tables:

```
[bumpversion:file(version):packages/machinome-node-freecad/pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file(pins):packages/machinome-node-freecad/pyproject.toml]
search = ~={current_version}"
replace = ~={new_version}"
```

`tests/test_release_records.py` needs no edit: it reads every manifest under
`packages/`, and is red at the join on the product's version 0.1.0, its
unpinned `machinome` and its missing tables (probe 6).

### 9. `scripts/check-dist`: one row

A row built with `mesh_node_smoke`, whose `shipped` and `pins` parameters
already serve a package directory and a pin on the B-rep engine; the template's
docstring sentence "over no B-rep engine" becomes "whose files `shipped` lists",
nothing else of it changes:

```python
    'machinome-node-freecad': {
        'through': 'freecad',
        'extras': [],
        'code': mesh_node_smoke(
            'machinome-node-freecad', 'freecad',
            ['machinome/node/freecad/__init__.py',
             'machinome/node/freecad/adapter.py',
             'machinome/node/freecad/runtime.py',
             'machinome/node/freecad/worker.py'],
            ['machinome~={version}', 'machinome-engine-brep~={version}'],
            '''
from machinome.motion.ports import Time
from machinome.node.freecad import FreeCADAssemblyNode, FreeCADJoint
from machinome.simulation import Driver


class Part(FreeCADAssemblyNode):
    freecad_source = 'cad/Assembly.FCStd'
    time = Time.running()
    turntable = FreeCADJoint('Joint001')
    turn = Driver(default=0, unit='deg')
    turn.drives(turntable)
''',
            f'''
fixtures = Path({str(ROOT / 'packages/machinome/tests/fixtures/freecad')!r})
os.makedirs('cad')
shutil.copyfile(fixtures / 'Maximum120.FCStd', 'cad/Assembly.FCStd')
shutil.copyfile(fixtures / 'Parts.FCStd', 'cad/Parts.FCStd')
import parts
from machinome.node.freecad.runtime import NativeAssemblyError
if os.environ.get('MACHINOME_FREECAD_ROOT'):
    from machinome.simulation import Sim
    node = parts.Part()
    sim = Sim(node, dt=0.02)
    command = sim.move('turn', to=150, duration=1)
    sim.run(1)
    assert command.status == 'blocked', command.status
    assert abs(node.turntable.value - 120) < 1e-9, node.turntable.value
    result = 'blocked at its enabled limit, 120 degrees, through FreeCAD'
else:
    try:
        parts.Part()
    except NativeAssemblyError as error:
        assert 'MACHINOME_FREECAD_ROOT' in str(error), error
    else:
        raise AssertionError('constructed without a FreeCAD runtime')
    result = 'refused without MACHINOME_FREECAD_ROOT, as documented'
'''),
        'commands': [],
    },
```

The fixture pair is the product's own smoke's (`scripts/smoke_dist.py`, which
copied `Maximum120.FCStd` and `Parts.FCStd` into a fresh project): the
assembly links its parts document by its relative name. `check-dist` runs each
smoke with the caller's environment, so the native branch runs on a machine
where `MACHINOME_FREECAD_ROOT` is set and the refusal branch in CI. The
operation is an f-string only to embed the fixture directory; the applier may
instead pass the directory through the template, as long as no other row
changes. Red first: before the row, the script fails "machinome-node-freecad
has no smoke in scripts/check-dist".

### 10. The tests in the suite

- **The guard.** A new helper, `tests/freecad_support.py`:

  ```python
  # Machinome - A framework for mechanical CAD projects
  # Copyright (C) 2026 Luis Henrique Cassis Fagundes
  # SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

  """What the FreeCAD node package's tests share: the one guard that skips
  them where no FreeCAD runtime is configured (OpenSpec change
  `join-freecad`, capability `native-freecad-assembly`)."""

  import os

  import pytest

  #: The variable naming the extracted FreeCAD 1.1.4 runtime.
  RUNTIME = 'MACHINOME_FREECAD_ROOT'


  def skip_without_runtime():
      """Skip the calling test module, at its import, when `RUNTIME` is not
      set."""
      if not os.environ.get(RUNTIME):
          pytest.skip(f'{RUNTIME} is not set: the FreeCAD node package\'s '
                      'tests need an extracted FreeCAD 1.1.4 runtime',
                      allow_module_level=True)
  ```

  Each of the four test modules calls it after its standard-library imports
  and before it imports `machinome.node.freecad` or `cadquery`:
  `from tests.freecad_support import skip_without_runtime` then
  `skip_without_runtime()`. The suite then reports four skips, each naming the
  variable; the 14 tests that need no runtime (probe 3) are among the skipped,
  which the cycle's validation runs with the runtime (Open Questions 5).
- **Imports and paths.** `from machinome_freecad import ...` becomes `from
  machinome.node.freecad import ...` (the two classes, `adapter`, `runtime`,
  `worker`); `import machinome_freecad.adapter as adapter` becomes `import
  machinome.node.freecad.adapter as adapter` (seven places in
  `test_freecad_freshness.py`); the source text `test_freecad_freshness.py`
  writes for its relocated project imports `machinome.node.freecad`; `from
  test_public import ...` becomes `from tests.test_freecad_public import ...`
  (three modules) and `from origin_model import DeclaringModule` becomes
  `from tests.freecad_origin_model import DeclaringModule`, since the suite's
  `tests/` is a package; `FIXTURE` is `Path(__file__).parent / 'fixtures' /
  'freecad' / 'Assembly.FCStd'`; `Path(__file__).with_name('native_reference.py')`
  becomes `with_name('freecad_native_reference.py')`; the relative
  `freecad_source = 'fixtures/Assembly.FCStd'` of `freecad_origin_model.py`
  and of `test_freecad_public.py`'s inheriting class becomes
  `'fixtures/freecad/Assembly.FCStd'`. The test line `assert all(leaf.exact
  for leaf in leaves)` becomes `assert all(leaf.brep for leaf in leaves)`
  (probe 2). Nothing else in the four modules changes.
- **Collection.** pytest collects `test_*.py`; the three helpers and the
  guard's module are never collected, and `conftest.py`'s `collect_ignore`
  needs no entry. The suite's `tests/pyproject.toml` makes `tests/` the
  machinome project whose root the source rule reads, so a fixture under
  `tests/fixtures/freecad/` belongs to the declaring test module's project, as
  it did under the product's own `tests/pyproject.toml`. The tests' builds go
  to `tests/_build`, which the framework's `.gitignore` covers.
- **The gates, red first, after the join** (the reds the join itself causes
  are probe 6's):
  - `test_repository_layout.py`: `EXTENSIONS['machinome-node-freecad'] =
    ('machinome.node.freecad', 'freecad')`; `PACKAGE_PORTIONS['machinome-node-freecad']
    = ('__init__', 'adapter', 'runtime', 'worker')`; the docstring names the
    package and the change. Red: the directory holds no links and the
    product's manifest (name, licence, include); the README names neither the
    install line nor the licence; the portion does not resolve until the sync.
  - `test_kernel_extras.py`: `EXTRAS['freecad']`, `all` with `freecad`;
    `PACKAGE_REQUIREMENTS['machinome-node-freecad'] = {f'machinome~={VERSION}',
    f'machinome-engine-brep~={VERSION}', 'numpy', 'scipy'}`;
    `BREP_NODE_PACKAGES` and the no-mesh list gain it; `test_all_names_every_kernel_extra`'s
    set gains `freecad`; `MODULES['machinome.node.freecad'] = ('freecad',
    'machinome.node.freecad (FreeCADAssemblyNode, FreeCADJoint)', ('OCP',))`.
    Red: no `freecad` extra; the product's manifest; no refusal at import.
  - `test_core_kernel_free.py`: `KERNEL_MODULES` and `EXTENSION_MODULES` gain
    `machinome.node.freecad`; `EXTRA_OF['machinome-node-freecad/machinome/node/freecad/__init__.py']
    = 'freecad'`; the extension census expects
    `'machinome-node-freecad/machinome/node/freecad/adapter.py': ['OCP']`;
    the docstring names the package. Red: no `require_extra` in the package's
    `__init__`.
  - `test_supported_node_types.py`: `NODE_TYPES['freecad'] =
    ('FreeCADAssemblyNode', 'FreeCADJoint')`, last; `ABSENCES['freecad'] =
    doors('freecad')`; `test_it_names_the_eight_node_types_and_their_classes`
    renamed `test_it_names_the_nine_node_types_and_their_classes`. Red: the
    table has no row; the doors import a module that does not refuse.
  - `test_node_root_exports_nothing.py`:
    `test_the_table_lists_the_nine_classes_written_here` reads the table's
    former root names apart from its new ones: the nine of `FORMER` as now,
    and `sorted(set(listed) - set(FORMER)) == ['FreeCADAssemblyNode',
    'FreeCADJoint']`. Red until the row: the new names are not listed. Its
    root-import scan is red at the join on the adapter (probe 6) and green
    after Decision 5.
  - `test_core_names_no_split_words.py`: `ZONES` gains
    `'machinome/node/freecad/worker.py'`, whose result reports FreeCAD's own
    OCCT version under the key `'occt'`; the docstring's W4 sentence names it.
    Red at the join on the adapter's three names and the worker's key; green on
    the adapter after Decision 5 and on the worker after the zone.
  - `test_docs_structure.py`: `KernelExtrasTest.EXTRAS` and the distributions'
    test gain `freecad` and `machinome-node-freecad`; `STALE` gains
    `'machinome_freecad'`; a new test pins the guide (Decision 12). Red: the
    installation page names neither; the guide is Markdown and in no toctree.
  - A new test, in `test_supported_node_types.py`, runs `python -m pytest -q
    -rs -p no:cacheprovider tests/test_freecad_public.py` in a subprocess from
    the framework's directory with `MACHINOME_FREECAD_ROOT` removed from its
    environment, and asserts "1 skipped" and `MACHINOME_FREECAD_ROOT` in its
    output (the scenario "The suite without a runtime skips the native tests").
    Red before the guard: the module's tests fail without the runtime.

### 11. The fixtures

They stay together under `tests/fixtures/freecad/`, `assembly-dir/` included,
since documents link each other by relative name. `README.md` there keeps its
text with three edits: its SPDX line states the set's expression; `../generate_fixtures.py`
becomes `../../freecad_generate_fixtures.py`; and a closing section,
"Regenerate", carries `docs/runtime.md`'s developer recipe:

```
PYTHONPATH="$MACHINOME_FREECAD_ROOT/usr/lib" \
  "$MACHINOME_FREECAD_ROOT/AppRun" python tests/freecad_generate_fixtures.py
```

run from `packages/machinome` with `MACHINOME_FREECAD_ROOT` set, which the
generator reads, with the note that FreeCAD leaves a `.FCBak`
backup beside each document it rewrites, which is deleted. The generator's
`out` becomes `Path(__file__).parent / 'fixtures' / 'freecad'`, and its three
`License` and `LicenseURL` assignments `'GPL-2.0-or-later OR CERN-OHL-S-2.0+'`
and `'https://github.com/machinome/machinome/blob/main/LICENSE'`. The applier
then regenerates the 27 documents with the runtime, deletes the backups, and
runs the four modules with the runtime: probe 8 found 82 passed on documents
regenerated this way. A reviewer cannot read a diff of 27 binary documents;
the evidence records each document's count of the former licence string
before (2) and after (0), and the run. If the orchestrator declines the
regeneration (Open Questions 4), the generator's assignments still change and
the 27 documents stay as they are.

### 12. The manual

- **`howto/freecad-assemblies.rst`**, converted in place from the imported
  `docs/api.md`, listed in the how-to toctree of `index.rst` after
  `howto/simulate-existing`. Title "Simulate a native FreeCAD assembly". Its
  sections and what each states:
  - the opening: a `FreeCADAssemblyNode` is one native FreeCAD assembly, one
    grounded tree of rigid fixed and revolute connections, read by FreeCAD
    itself in a separate process; the project declares no joint, axis, frame,
    zero or limit; FreeCAD's other workbenches, loops, dynamics and inverse
    kinematics are outside it.
  - "Set up FreeCAD": `pip install "machinome[freecad]"`, which installs no
    FreeCAD; the runtime the package is measured with, the official FreeCAD
    1.1.4 AppImage for Linux x86-64 (SHA-256
    `f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434`, git
    build `4fd3bf320d9566a27e60069fc8387448aaa3a094`), extracted, and
    `MACHINOME_FREECAD_ROOT` set to the extraction's root, which holds
    `AppRun`, `usr/lib`, `usr/Mod` and `usr/Mod/Assembly`; other systems,
    versions and layouts are untested; nothing downloads FreeCAD or falls back
    to its GUI; importing the package and declaring a class need no runtime,
    constructing an instance does and is refused naming the variable; open
    trusted documents only, since restoring a document runs the Python it
    carries and the separate process is not a sandbox.
  - "Declare the assembly": the example of `docs/api.md` as a `code-block::
    python`, its first line `from machinome.node.freecad import
    FreeCADAssemblyNode, FreeCADJoint`; then `freecad_source` (a string or a
    path-like, resolved from the declaring module whatever the working
    directory and through inheritance, inside the project; external links
    resolved by FreeCAD, their relative layout kept).
  - "Drive a joint": `docs/api.md`'s paragraphs on the internal Name, the
    alias returning the physical coordinate in degrees, native zero, saved
    coordinates of uncommanded revolutes, enabled limit sides only, `range=`
    being presentation, `"blocked"` and `"completed"`, `sim.state` and
    `sim.stops`.
  - "What is refused": "Selectors and refusals" and the admission paragraphs
    (the supported graph; native recomputation and solve; the residual
    tolerances 0.01 mm and 0.001 degree; the saved-pose drift guard; no repair
    of a source), without the Dum-E narrative and without the link to the
    workflow archive's review.
  - "After an edit": "Refresh and geometry", the cost of two native processes
    per fresh model stated once.
  - "Compare poses": the `occurrence_poses` example as a `code-block:: python`.

  It spells no licence identifier and no publication caveat
  (`test_docs_structure.py`), no `machinome_freecad`, and links no internal
  record.
- **`start/install.rst`**: under "Optional:", "* **FreeCAD** 1.1.4, extracted,
  to read native FreeCAD assemblies with ``FreeCADAssemblyNode``
  (:doc:`/howto/freecad-assemblies`)."; a row after `machinome[stl]`'s:
  ``machinome[freecad]`` | ``machinome.node.freecad`` | "the package
  ``machinome-node-freecad``, for ``FreeCADAssemblyNode`` and
  ``FreeCADJoint``, which read a native assembly through FreeCAD, a program
  no Python package installs, found through ``MACHINOME_FREECAD_ROOT``
  (:doc:`/howto/freecad-assemblies`)"; "Packages and licences"' list gains
  ``machinome-node-freecad`` after ``machinome-node-stl``, rewrapped.
- **`howto/backends.rst`**: a row after `MolejoNode`'s: ``FreeCADAssemblyNode``
  | ``machinome.node.freecad`` | "``freecad_source`` naming a native
  assembly, and a ``FreeCADJoint`` per driven revolute" | yes | "FreeCAD and
  ``machinome[freecad]`` (:doc:`freecad-assemblies`)"; the sentence after the
  table becomes "Each class is imported from the module beside it, the module
  of its node type: nine node types; ``machinome.node.build123d`` defines two
  classes, and ``machinome.node.freecad`` reads a whole assembly rather than
  one part."
- **`reference/api.rst`**, after `StepNode`'s entry:

  ```rst
  .. autoclass:: machinome.node.freecad.FreeCADAssemblyNode

     A whole native FreeCAD assembly, read by FreeCAD when the node is
     constructed. See :doc:`/howto/freecad-assemblies`.

     .. attribute:: freecad_source

        Path of the ``.FCStd`` document holding one native assembly,
        relative to the directory of the python file declaring the
        attribute. A path that resolves outside the project is refused when
        the node is constructed.

  .. autoclass:: machinome.node.freecad.FreeCADJoint

     One revolute of the assembly, selected by its native internal Name, as
     the target of a driver.
  ```

  autodoc imports the package from the source tree (`docs/conf.py` puts every
  `packages/machinome-*` on the path) with `OCP`, `numpy` and `scipy` mocked;
  the build with warnings as errors is the evidence.
- **The pin**: `test_docs_structure.py` gains
  `test_the_freecad_guide_is_a_how_to`: `howto/freecad-assemblies` in the
  How-to toctree; the page spells `from machinome.node.freecad import`,
  `MACHINOME_FREECAD_ROOT` and `1.1.4`.

### 13. The records

- **`HISTORY.rst`**, under `Unreleased`, after the `cut-the-mesh-nodes`
  bullet:

  ```
  * **The FreeCAD node type joins the repository.** The native FreeCAD
    assembly adapter, developed in a repository of its own and never
    published, is the extension package ``machinome-node-freecad``, its
    history kept: ``FreeCADAssemblyNode`` and ``FreeCADJoint`` are imported
    from ``machinome.node.freecad`` (formerly ``machinome_freecad``) and
    installed by ``pip install "machinome[freecad]"``, which installs no
    FreeCAD; the runtime, FreeCAD 1.1.4, is found through
    ``MACHINOME_FREECAD_ROOT``. Without the package, its import names that
    line. Its tests join the framework's suite and skip where no runtime is
    set. Change ``join-freecad`` (ADR-185).
  ```

- **`docs/project/changelog.rst`**, under `Unreleased`, after "Every node type
  is a package of its own.":

  ```
  * **A native FreeCAD assembly is a node type.** ``FreeCADAssemblyNode``
    reads a whole FreeCAD assembly, its fixed and revolute joints and their
    enabled limits, through FreeCAD itself, and ``FreeCADJoint`` hands one of
    its revolutes to a driver; ``pip install "machinome[freecad]"`` installs
    the distribution ``machinome-node-freecad``, and FreeCAD 1.1.4 is found
    through ``MACHINOME_FREECAD_ROOT`` (:doc:`/howto/freecad-assemblies`).
  ```

- **`CREDITS.md`**: after the runtime dependencies' last entry (manifold3d), a
  subsection:

  ```markdown
  ### Called and consulted by the FreeCAD node package

  The package `machinome-node-freecad` (`machinome.node.freecad`) runs an
  independently installed FreeCAD and bundles none of it. Its worker and its
  fixture generator are original programs that call FreeCAD's API; no FreeCAD
  or OndselSolver function or binary is copied into the repository, and its
  test fixtures are original synthetic boxes, with no Dum-E or other upstream
  CAD among them.

  #### FreeCAD
  - **License:** LGPL 2.1 or later
  - **Copyright:** FreeCAD contributors; the Assembly workbench's Python
    sources Copyright (c) 2023 Ondsel <development@ondsel.com>
  - **Repository:** https://github.com/FreeCAD/FreeCAD
  - **Version:** 1.1.4, git `4fd3bf320d9566a27e60069fc8387448aaa3a094`, the
    official Linux x86-64 AppImage
  - **Description:** The CAD program whose Python the package's worker runs to
    read a native assembly; called, not bundled or relicensed. The native API
    and connector semantics were checked against the installed
    `usr/Mod/Assembly/JointObject.py`, `UtilsAssembly.py`,
    `CommandCreateAssembly.py` and the public `AssemblyObject` interface,
    whose notices remain with the installed files; review also read
    `AssemblyObject.cpp` and `AssemblyObjectPyImp.cpp`.

  #### OndselSolver
  - **License:** LGPL 2.1 or later
  - **Copyright:** Copyright (c) 2023 Ondsel, Inc.
  - **Repository:** https://github.com/FreeCAD/OndselSolver
  - **Version:** commit `30e9b64e8bf881d438d4b88834f9ba3674865418`
  - **Description:** FreeCAD's assembly solver. Its `FixedJoint.cpp`,
    `RevoluteJoint.cpp`, `AtPointJoint.cpp` and
    `DirectionCosineConstraintIJ.cpp` at that commit were read; the worker's
    `constraint_residual`, added on 1 October 2026, adapts their mathematical
    zero-target constraints, not their C++ solver algorithm, and copies no
    implementation from them. Ondsel's copyright is retained for those
    constraint conventions in the worker's header.
  ```

  The summary table gains `| FreeCAD (called, not bundled) | LGPL 2.1+ | ✓
  Compatible |` and `| OndselSolver (conventions consulted) | LGPL 2.1+ | ✓
  Compatible |`; the last line's date becomes 2026-10-11. These name the
  third parties' licence, which is their provenance (Open Questions 6).
- **`docs/architecture.md`**: the extras sentence gains, after the node types
  that need no B-rep engine, "`[freecad]` for the FreeCAD node package (the
  distribution `machinome-node-freecad`, over the B-rep engine; FreeCAD itself
  is a program no extra installs, found through `MACHINOME_FREECAD_ROOT`)"; the
  Map gains, after the JSCAD and STL row: "FreeCAD node type, the distribution
  `machinome-node-freecad`" | "the repository's `packages/machinome-node-freecad/`
  (`machinome/node/freecad/`: `__init__.py`, `adapter.py` `FreeCADAssemblyNode`
  and `FreeCADJoint`, `runtime.py` the runtime and its worker process,
  `worker.py` the script FreeCAD's Python runs)" | `native-freecad-assembly`,
  `kernel-extras`, `node-model` | "004, 183, 184, 185".
- **The root `README.md`**: a row after the STL package's:
  ``| [`machinome-node-freecad`](packages/machinome-node-freecad/) | The FreeCAD node type, `machinome.node.freecad`, a native FreeCAD assembly read by FreeCAD; installed by `machinome[freecad]`. |``
- **`CONTRIBUTING.rst`**: the pip block's last package line becomes
  `-e packages/machinome-node-jscad -e packages/machinome-node-stl \` followed
  by `-e packages/machinome-node-freecad \`, then the framework's line.
- **`context7.json`**: the rule on imports and extras names `freecad` among
  the node types and `[freecad]` among the extras, and gains "FreeCAD itself is
  found through MACHINOME_FREECAD_ROOT."
- **ADR-185** (recommended, Open Questions 1), `docs/adrs/NODE/ADR-185-a-node-type-may-read-a-whole-assembly-through-an-external-program.md`,
  Status Proposed, Change `join-freecad`, Amends ADR-183 (a package that
  joined from its own repository is an extension package like the others),
  Related to ADR-004, ADR-046, ADR-167 and ADR-184. Context: the join and the
  facts of probes 1 and 2. Options: (1) the FreeCAD node type as a package
  portion of the table whose node is an `AssemblyNode` compiled at
  construction from a document FreeCAD reads in a separate process found
  through `MACHINOME_FREECAD_ROOT` (chosen); (2) machinome-freecad kept as an
  independent product importing the framework (refused by the pilot's plan of
  11 October 2026); (3) a leaf type per occurrence, joints redeclared by the
  project (refused by the product's ratified contract: the source owns the
  mechanics); (4) FreeCAD installed by the extra (refused: no wheel of the
  program exists, and the separate process is the boundary between its Python
  and OCCT and the host's). Decision: the row, the package, its kernel check
  of `OCP`, its occurrence leaves on `BrepLeafNode` at leaf contract 3 through
  the B-rep engine's seam, its runtime refused at construction, its tests
  skipped without the variable, its record the framework's. Consequences:
  good, one address and one install line, the refusal by the extra for free;
  bad, CI runs none of its tests, vet and the leaf-contract reach gate do not
  read it (Decision 14); neutral, two native processes per fresh model, as
  before. Its index line under NODE after ADR-184; ADR-183's status and index
  lines note "amended by 185", and ADR-183 gains the consequence "Neutral
  (2026-10-11, `join-freecad`): a product of a repository of its own joins as
  an extension package of the same shape, its history imported to its final
  paths and its record folded into the framework's."
- **The plan's progress** (`workflow/ongoing/joins-0.9.md`, "Progress"): the
  cycle's entry at its close, in the form `monorepo-0.9.md` records its
  cycles.

### 14. Two findings, recorded, not fixed

`packages/machinome/workflow/warts.md` gains, at its end:

```markdown
# Findings from the framework cycle `join-freecad` (11 October 2026)

- **`machinome vet` admits the FreeCAD node package whole and does not read
  `freecad_source`.** The vet universe's contract member `machinome` is
  allowed whole, so since the join a project importing
  `machinome.node.freecad` passes the import check, where it failed on
  `outside-universe machinome_freecad` before (Dum-E's DUME-006). The
  universe's `[sources]` names `freecad_source` neither among the checked
  attributes nor among the refused ones, where `jscad_source`, the other
  source an external program reads, is refused; so an escaping or absolute
  FCStd path is not reported, and the FreeCAD runtime, which runs the Python
  a document carries, is not modelled. Measured on a scratch copy of Dum-E
  moved onto the package: `machinome vet` exit 0, `simulation.dume:DumE
  pure`. Not fixed by `join-freecad`, which moves the package and nothing
  else; whether `freecad_source` is checked like `stl_source` or refused like
  `jscad_source` is the pilot's.
- **The leaf-contract reach gate does not read the FreeCAD adapter.**
  `tests/test_leaf_contract_reach.py` reads the four B-rep node modules and
  the stand-ins; `machinome/node/freecad/adapter.py`, whose occurrence leaf is
  a `BrepLeafNode` outside the core, is not in its list. The gate's own
  functions on the adapter (11 October 2026): two reaches, `machinome.currency`
  imported in the leaf's `materialize` for the sidecar paths it backs up, and
  `self._link_children` called on the assembly; and ten imports from modules
  the leaf contract does not declare (`machinome.node.assembly`,
  `machinome.motion.couplings` three names, `machinome.motion.joints`,
  `machinome.motion.ports` two, `machinome.node.operations` two,
  `machinome.currency`). The adapter builds nodes, joints and couplings,
  which no declared contract covers; a contract for a node package that
  compiles an assembly, or the gate's reason for each import, is a later
  cycle's.
```

### 15. Validation in the originating project

The orchestrator moves Dum-E onto the package in Dum-E's own repository, under
its own process, on a branch of its choosing: `simulation/dume.py` and
`simulation/test_preparation.py` import from `machinome.node.freecad`;
`simulation/tools/environment.py` imports `machinome.node.freecad as
machinome_freecad`, which `simulation/tools/evaluate.py`, read by
`test_dume.py`, reaches (its receipt pins machinome 0.7.1 and a frozen checkout
and is the project's to revise); `pyproject.toml`'s dependencies are the
project's to restate (`machinome[freecad]~=0.8.1` is the line that installs the
package now); DUME-006 in `docs/issues.md` records the new vet result. Then,
from Dum-E's root with the bench's venv first on `PATH` and
`MACHINOME_FREECAD_ROOT=<freecad>`:

- `python -m pytest -q -p no:cacheprovider simulation/test_dume.py
  simulation/test_preparation.py`: green is 7 passed (probe 7: 4 and 3);
- `machinome snapshot -o <scratch>/dume-posed.png --autocenter --drive turn=70
  --drive shoulder=15 --drive elbow=110 --drive wrist=-25 --imgsize 1280x960`:
  green is exit 0, an image looked at (the arm on its base, turned and
  articulated, the holder attached) and its SHA-256 equal to that of
  `snapshot-corrected-posed.png`, `40f8d568...b804`;
- `machinome vet`: its exit and verdict recorded (probe 7: 0, pure), the
  finding of Decision 14, not a gate;
- `git -C <Dum-E> status --short` afterwards: only the project's edits.

### 16. The spec deltas

- `native-freecad-assembly`: RENAMED "Optional ... package and documented
  public contract" to "The FreeCAD node package and its documented public
  contract", and MODIFIED both that requirement (the distribution of the
  repository, its extra, its provenance in `CREDITS.md`, no extra installing
  FreeCAD, its manual in the framework's, its tests skipped without the
  runtime: one new scenario) and "Native assembly declaration and selected
  coordinate reference" (the import `machinome.node.freecad`, in its text and
  its example, and nothing else). MODIFIED and RENAMED, not ADDED: the import
  lands the baseline before the archive, and an ADDED delta of a requirement
  the baseline holds aborts the archive (probe 5). The archive leaves the
  Purpose as it is, so the applier then writes it, by hand, in the baseline:
  "Import supported native FreeCAD assemblies into machinome through the
  FreeCAD node package `machinome.node.freecad`, the distribution
  `machinome-node-freecad`, preserving authored joints and enabled limits
  without project-level mechanical redeclaration. Dum-E provides the empirical
  acceptance case, including explicit refusal of inconsistent native
  constraints." The other seven requirements are unchanged.
- `kernel-extras`: MODIFIED "The CAD kernels are extras, not required
  dependencies" (the `freecad` extra and its distribution; one new scenario),
  "A kernel module refuses an absent kernel at import" (the FreeCAD package
  among the checking modules), "The core imports no kernel outside its kernel
  modules" (the adapter's `OCP`; the package's `__init__` check; the census's
  names), "An absent node package is refused by its extra at its import" (one
  new scenario).
- `node-model`: MODIFIED "Each leaf type is one module under the node package"
  (the table's row; the package directory; one new scenario).
- `framework-identity`: MODIFIED "The framework is the package directory
  `packages/machinome` of a monorepo" (the package among the extension
  packages; its package directory; its record the framework's; one new
  scenario for its smoke).
- `framework-contributor-guidance`: MODIFIED "The contributor guide states the
  monorepo's development setup" (the pip command names its directory).
- `user-documentation`: ADDED "A native FreeCAD assembly is documented as a
  how-to".

Each MODIFIED requirement is copied whole from its baseline and edited; every
existing scenario keeps its title, and what is new comes under a new title.

### 17. The universe sweep

The command of `cut-the-mesh-nodes` with this bench and `MACHINOME_FREECAD_ROOT`
in its environment, which `scripts/load-projects` passes to each project's
child:

```
MACHINOME_FREECAD_ROOT=<freecad> /home/asa/devel/machinome/.venv/bin/python \
  /home/asa/devel/machinome/scripts/load-projects \
  --bench /home/asa/devel/machinome/machinome/WTs/v0.9-joins-join-freecad/packages/machinome \
  --python /home/asa/devel/machinome/machinome/WTs/v0.9-joins-join-freecad/.venv/bin/python \
  --moved /home/asa/devel/machinome/scripts/load-projects.d/*.toml \
  --timeout 300 --json <scratch>/load-projects.json
```

Read against `cut-the-mesh-nodes`: 63 repositories, 130 rows, 121 ok, 0
expected, 3 unexpected (wall_clock_41's own CadQuery error, Dum-E without
machinome-freecad, fender-bender without `fb_library`), 0 timeout, 6 no-model.
Run after the Dum-E move of Decision 15 on the checkout the sweep reads, its
Dum-E row is expected ok (122 ok, 2 unexpected); before it, Dum-E's row is
unchanged, its error `No module named 'machinome_freecad'`. Any other
difference is a finding.

## Risks / Trade-offs

- [CI never runs the FreeCAD tests] → They run in the cycle's validation with
  the runtime and wherever a contributor sets the variable; CI proves the
  package's install, its refusal path and the skips. A CI job with FreeCAD is
  a later choice (Open Questions 5).
- [The runtime-free tests are skipped with the rest] → 14 tests (probe 3);
  the cycle's validation runs them; a later cycle may split them out.
- [The rewritten history drops nine files from every imported commit] → The
  original repository keeps them, with the original hashes, as the plan says
  it stays; the imported commits' messages still say what each did.
- [The joined archives keep their words, the licence the product carried among
  them] → Archived records are historical (`workflow/README.md`); the
  framework's own archives name its former licence in 20 files. The baseline
  spec, the source headers, the fixtures' README and metadata, and every
  record this change writes state the set's.
- [The 27 regenerated fixtures cannot be reviewed as a diff] → Their counts of
  the old and the new licence string, and the 82-test run on them, are the
  evidence (Decision 11); declining keeps the bytes.
- [The adapter's lint adds about 728 lines to the lint job's 759] → CI's lint
  is `continue-on-error`; reformatting the adapter would put an edit of every
  line between the join and `git blame`. Not done.
- [`machinome vet` now reports a FreeCAD project pure] → Recorded as a finding
  with its measurement (Decision 14); the pilot decides the attribute's
  treatment.
- [The suite's skips grow by four] → Each names the variable; the evidence
  records the reason of every skip.

## Migration Plan

In the order of tasks.md: the baseline; the join, by the orchestrator, and the
reds it causes; the red tables; the package, the core's row and extra, the
workspace; the tests' edits, the guard and the fixtures; the manual;
`check-dist`; the records; validation, Dum-E's included; the archive. Rollback
is a revert of the implementation commit and of the merge commit, and a `uv
sync`. Outside the cycle: the workspace's `scripts/setup`, its collaborator
guide and its contract's status paragraph (the campaign's close); the studio's
`machinome-api` skill, which names `machinome_freecad` nowhere today
(*inferred*, not read); Dum-E's own records.

## Open Questions

1. **ADR-185.** The join adds the first node type whose node is an assembly
   rather than a leaf and whose runtime is an external program found through an
   environment variable and run as a separate process. The alternative is no
   ADR, ADR-183 gaining the dated consequence of Decision 13 alone.
   Recommendation: ADR-185, since a later reader asking why a node package
   spawns FreeCAD and why its tests skip in CI finds no other record; ADR-004
   (adapters), ADR-046 (an external program as a conditional dependency) and
   ADR-184 (the refusal) are its neighbours and none says it. If declined, the
   HISTORY bullet's "(ADR-185)" becomes "(ADR-183 amended)".
2. **`vet`.** Teach vet `freecad_source` in this cycle, as a checked source
   attribute like `stl_source` or a refused one like `jscad_source`, or record
   it. Recommendation: record (Decision 14); no project finding asks for more
   than the move, and which of the two the attribute is depends on whether vet
   should model a program that runs a document's Python, which is the pilot's.
3. **The leaf-contract reach gate.** Extend `LEAVING` to the adapter with an
   `ALLOWED` reason for each of its ten imports and two reaches, or record.
   Recommendation: record; the gate's subject is a leaf package, and the
   adapter is an assembly compiler whose leaf is private to it.
4. **Regenerating the fixtures.** Their document metadata states the licence
   the product carried. The alternative is to keep their bytes and change only
   the generator. Recommendation: regenerate (Decision 11), since the plan says
   no package in the repository carries another licence, and probe 8 shows the
   82 tests green on regenerated documents.
5. **The engine pin and FreeCAD in CI.** The package requires
   `machinome-engine-brep~=0.8.1` because its leaves are B-rep leaves and its
   adapter reads OCCT; the alternative, no engine pin and `OCP` from whatever
   is installed, would let the package install without the binding its import
   checks. Recommendation: the pin. A CI job with the FreeCAD AppImage is not
   in this cycle; the workflow is the repository's.
6. **The worker's adapted conventions under the set's licence.** The worker's
   `constraint_residual` adapts OndselSolver's mathematical constraints, with
   Ondsel's copyright retained and, per the product's notice, no
   implementation copied; the set offers CERN-OHL-S-2.0-or-later beside
   GPL-2.0-or-later. Recommendation: keep the retained copyright line and the
   `CREDITS.md` entry as the plan asks, and the pilot confirms that the worker
   takes the set's expression like every other file.
7. **The fixture location.** `tests/fixtures/freecad/` or a project directory
   `tests/freecad_project/` beside the suite's `<name>_project` fixtures.
   Recommendation: `tests/fixtures/freecad/`; the documents are data a test
   reads, not a project the suite builds, and the brief names the place the
   suite keeps fixtures.
8. **The rename's one spelling of the former title.** The `RENAMED` line of
   the `native-freecad-assembly` delta must spell the baseline requirement's
   title as it stands, and that title names the licence the product carried;
   every route OpenSpec offers to retitle a requirement (`RENAMED`, or
   `REMOVED` and `ADDED`) spells it once in this change's delta, which the
   archive keeps. The alternative is a hand edit of the baseline's title
   outside the delta, which the archive would not record. Recommendation:
   accept the one spelling, in the delta's `FROM` line, as the record of the
   rename; nothing else this change writes names that licence.
