# Evidence — import the artifact by path

Everything below was measured on this worktree at `b8409cc`, with
`PYTHONPATH=$PWD` and `/home/asa/devel/libresolid-studio/.venv`, OpenSCAD
2021.01, before any change to the framework.

## The fixture

`evidence/probe_cross_package.py` writes a throwaway project outside the
repository and builds it with the real `solid build`. The project declares
four models:

    sim/parts.py         RigidLeaf(Solid2Node), ExactLeaf(CadQueryNode),
                         FlexLeaf(MolejoNode, height port), UnoptimizedLeaf
    sim/tools/bench.py   Bench       — places all three leaf kinds
                         UnoptBench  — places the optimize=False leaf
    sim/samebench.py     SameBench   — the control, beside the leaves
    sim/sub/deep/group.py   Group    — an intermediate assembly
    sim/tools/deep_bench.py DeepBench — a root over that intermediate

Run:

    PYTHONPATH=$PWD python \
      openspec/changes/import-the-artifact-by-path/evidence/probe_cross_package.py \
      /tmp/probe --save openspec/changes/import-the-artifact-by-path/evidence/generated

Each model is built twice; every generated `.scad` is printed after each
pass, with each `import(file = …)` checked for existence **relative to the
directory holding that `.scad`** — which is how OpenSCAD resolves it. The
generated files are kept under `evidence/generated/` (the state after the
second pass).

## The measurement

`Bench`, in `sim/tools/`, over leaves declared in `sim/` — the Thor shape.
`_build/bench/sim/tools/bench-Bench-3f8c65be8e28.scad`, identical after
build 1 and build 2:

```
union() {
	import(file = "../parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
	translate(v = [20, 0, 0]) {
		import(file = "../parts-ExactLeaf-d20b313b0496.stl", origin = [0, 0]);
	}
	translate(v = [40, 0, 0]) {
		import(file = "parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl", origin = [0, 0]);
	}
}
    OK   ../parts-RigidLeaf-5c13fc621640.stl
    OK   ../parts-ExactLeaf-d20b313b0496.stl
    MISS parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl
```

### Leaf kind × build → path form

| leaf kind | build 1 | build 2 | resolves from the parent's build directory? |
| --- | --- | --- | --- |
| rigid (`Solid2Node`) | `../parts-RigidLeaf-5c13fc621640.stl` | identical | yes, both builds |
| exact (`CadQueryNode`) | `../parts-ExactLeaf-d20b313b0496.stl` | identical | yes, both builds |
| flexible (`MolejoNode`) | `parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl` | identical | **no**, both builds |
| rigid, `optimize = False` | no import at all — `cylinder(h = 12, r = 4);` inlined | identical | n/a |

The briefing's addendum predicted a bare name for the rigid and exact leaves
on the FIRST build (on the reading that `assemble()`'s `else` branch returns
`self.model`). **Refuted by the measurement above**: `assemble()`
(`base.py:825-834`) materialises the artifact in that branch and then
returns `self.import_optimized()` as well, so by the time the path is
spelled the STL is current and the root-relative form is taken. The
briefing's other prediction — a bare name for every flexible leaf, always —
**is confirmed**, on both passes.

The rigid and exact leaves are correct here by coincidence:
`import_optimized()` anchors on the ROOT NODE's directory
(`base.py:910`, `os.path.relpath(self.basedir, self.root)`), and in this
fixture the root IS the importing parent. Change that and it breaks:

### The same bug from the other side — an intermediate assembly

`DeepBench` (root, `sim/tools/`) → `Group` (`sim/sub/deep/`) → `RigidLeaf`
(`sim/`). Both generated files hold the SAME string, and it resolves in only
one of them:

```
=== _build/deep/sim/sub/deep/group-Group-34ca0e766088.scad
import(file = "../parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
    MISS ../parts-RigidLeaf-5c13fc621640.stl

=== _build/deep/sim/tools/deep_bench-DeepBench-0bc412547ce1.scad
import(file = "../parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
    OK   ../parts-RigidLeaf-5c13fc621640.stl
```

An assembly is not rigid (`assembly.py:365`), so its parent inlines its whole
tree rather than importing an STL of it: one emitted string lands in two
`.scad` files at two depths. That is the measurement behind design.md's
claim that no single relative string can be finished at emission time.

### The control — a parent beside its parts

`SameBench`, in `sim/` with the leaves. Every import is a bare basename and
every one of them resolves:

```
union() {
	import(file = "parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
	import(file = "parts-ExactLeaf-d20b313b0496.stl", origin = [0, 0]);
	import(file = "parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl", origin = [0, 0]);
}
    OK   parts-RigidLeaf-5c13fc621640.stl
    OK   parts-ExactLeaf-d20b313b0496.stl
    OK   parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl
```

This is why the bug only ever appeared to projects that put a viewing helper
in a sub-package, and why moving the assembly beside the leaf cured it.

### What the published document says about the same artifacts

`_build/bench/viewer.json`, same build:

```json
"model": "sim/parts-RigidLeaf-5c13fc621640.stl"
"model": "sim/parts-ExactLeaf-d20b313b0496.stl"
```

Build-directory-relative, unambiguous, and correct — the document path has
never had this bug. That is the anchor this change adopts for the SCAD path
as well.

## What OpenSCAD does with an import it cannot open

`evidence/probe_openscad_missing.py`, calling OpenSCAD exactly as
`solid_node/viewers/openscad.py` does (`check=True`, `capture_output=True`):

```
openscad: /usr/bin/openscad
OpenSCAD version 2021.01
returncode: 0
--- stdout (the only stream the renderer logs)
WARNING: Can't open import file '/…/does-not-exist.stl', import() at line 3
Compiling design (CSG Products normalization)...
…
--- stderr (discarded by the renderer today)

image written: True
```

Three facts for the design:

1. The warning goes to **stdout**, not stderr, on 2021.01.
2. The return code is **0**, so `check=True` raises nothing and
   `manager/snapshot.py:216`'s `CalledProcessError` handler never runs.
3. The renderer does capture that stdout and then calls
   `logger.debug(result.stdout)` (`viewers/openscad.py:29-30`) — below the
   default level, so nothing reaches the maker. The image is written, minus
   the part, and the command prints `Snapshot saved to …`.

Reproduced end to end on the fixture itself:

    xvfb-run -a openscad -o bench.png --imgsize 400,300 --autocenter \
        --viewall bench-Bench-3f8c65be8e28.scad

warns about the flexible leaf's STL, exits 0, and writes
`evidence/generated/bench-missing-flexible-leaf.png` — the rigid box and the
exact box, and no helix at x = 40 at all.

## Feasibility of the proposed mechanism

`evidence/probe_reanchor.py`, against the installed solid2:

```
str subclass survives construction: False

--- as the parent inlines it
union() {
	import(file = "sim/a.stl", origin = [0, 0]);
	import(file = "vendor/x.stl", origin = [0, 0]);
}
--- re-anchored for a .scad one directory deeper
union() {
	import(file = "../sim/a.stl", origin = [0, 0]);
	import(file = "vendor/x.stl", origin = [0, 0]);
}
--- the tree the parent inlines is untouched
union() {
	import(file = "sim/a.stl", origin = [0, 0]);
	import(file = "vendor/x.stl", origin = [0, 0]);
}
```

So: a subclass of `import_stl` renders byte-identically (it passes the call
name `'import'` to its base) and is the marker that separates a framework
artifact import from the project's own; a `str` subclass on the `file`
parameter is NOT, because `import_stl` normalises it with
`_Path(file).as_posix()`; and re-anchoring a deep copy leaves the tree a
parent inlines untouched.

## Existing coverage checked

- `tests/deep_project/` is a nested-package fixture, but every model in it
  is a parent ABOVE its children (`third_level.py` → `one/` → `one/two/` →
  `one/two/three/`), and each is exercised as the ROOT. It cannot produce
  this bug: the root anchor and the importing directory coincide. There is
  no cross-package parent — an assembly in a SIBLING or DEEPER package than
  the leaf it places — anywhere in `tests/`.
- No existing test reads a generated `.scad` FILE and resolves its imports
  against disk. `tests/test_scad_stl.py` compares `self.solid.scad_code`
  text for a node loaded as the root; `tests/test_stl_node.py`,
  `tests/test_sheet_leaf.py`, `tests/test_build123d_adapter.py` and
  `tests/test_backend_neutral_materialization.py` assert
  `node.local_stl in str(assembled)`, a substring check that an anchored
  path still satisfies.
- `tests/test_snapshot.py` patches `OPENSCAD_RENDERER.render` and
  `find_xvfb_run`; the renderer takes its subprocess runner as an argument
  (`manager/snapshot.py:215`, `run` from `subprocess`), so a fake runner can
  deliver OpenSCAD's warning text without OpenSCAD.

## Noticed and left out of scope

- **A rigid leaf's own `.scad` stops describing its geometry after the first
  build.** Build 1 writes `_build/bench/sim/parts-RigidLeaf-….scad` as
  `cube(size = [10, 10, 10]);`; build 2 rewrites it as
  `import(file = "parts-RigidLeaf-….stl");` — `assemble()` sets
  `self.model = import_stl(self.local_stl)` on the up-to-date path
  (`base.py:819-821`) and then calls `generate_scad()`. The file that is
  supposed to be able to regenerate the STL becomes a file that imports it.
  It resolves (same directory), so it is not this change's bug; it is a
  separate finding for `workflow/warts.md`.
- A `FusionNode`'s `.scad` is written the same self-importing way, but its
  STL is produced natively (`fusion.py:93-140`, OCCT or manifold3d) and
  never by OpenSCAD from that `.scad`, so no geometry is at risk there.
- `self.mesh_scad_file` / `self.mesh_stl_file` are vestigial — nothing
  writes or reads them (the baseline spec says so, and a grep of
  `solid_node/` confirms only the assignment at `base.py:670-671`).

## Red

Measured on this worktree before any production change, immediately after
adding `tests/cross_package_project/` and the two test files.

    PYTHONPATH=$PWD /home/asa/devel/libresolid-studio/.venv/bin/python \
        -m pytest tests/test_scad_import_paths.py -q -p no:cacheprovider

    3 failed, 3 passed, 2 warnings

Failing, for exactly the reason predicted above:

```
FAILED CrossPackageLeafKindsTest::test_every_leaf_kind_resolves_from_the_parents_own_directory
  AssertionError: False is not true : 'parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl',
  imported by .../tests/_build/cross_package_project/tools/bench-Bench-3f8c65be8e28.scad,
  does not exist relative to .../tests/_build/cross_package_project/tools

FAILED CrossPackageLeafKindsTest::test_second_build_spells_it_the_same_way
  same MISS, on a freshly constructed second Bench() with every artifact
  already current on disk

FAILED IntermediateAssemblyScadImportTest::test_intermediate_assemblys_own_scad_resolves_from_its_own_directory
  AssertionError: False is not true : '../parts-RigidLeaf-5c13fc621640.stl',
  imported by .../tests/_build/cross_package_project/sub/deep/group-Group-34ca0e766088.scad,
  does not exist relative to .../tests/_build/cross_package_project/sub/deep
```

Passing today, as predicted (guards, not red): the root's own `.scad` over
the intermediate assembly still resolves
(`IntermediateAssemblyScadImportTest::test_root_scad_over_that_intermediate_still_resolves`),
the same-package control's bare basenames are unchanged
(`SamePackageControlTest::test_bare_basenames_unchanged`), and a project's
own `import_stl` is reproduced verbatim
(`ProjectsOwnImportTest::test_own_import_reproduced_verbatim`).

    PYTHONPATH=$PWD /home/asa/devel/libresolid-studio/.venv/bin/python \
        -m pytest tests/test_snapshot.py -q -p no:cacheprovider

    5 failed, 87 passed, 5 subtests passed

```
FAILED SnapshotErrorHandlingTest::test_unopenable_import_stops_the_image
  AssertionError: SystemExit not raised -- today the command reports
  "Snapshot saved to ..." and exits 0 over the missing part

FAILED SnapshotErrorHandlingTest::test_unrelated_warning_is_logged_without_failing
  AssertionError: no logs of level WARNING or higher triggered on
  viewers.openscad -- today OpenSCAD's stdout reaches only logger.debug()

FAILED OpenScadRendererDiagnosticsTest::test_missing_import_on_stderr_is_caught_too
FAILED OpenScadRendererDiagnosticsTest::test_unopenable_import_raises_named_error
  ImportError: cannot import name 'OpenScadImportError' from
  'solid_node.viewers.openscad' -- the type does not exist yet

FAILED OpenScadRendererDiagnosticsTest::test_unrelated_warning_is_promoted_to_warning_level
  AssertionError: no logs of level WARNING or higher triggered on
  viewers.openscad
```

The other four new `OpenScadRendererDiagnosticsTest`/`SnapshotErrorHandlingTest`
tests (a clean render, progress-stays-at-debug) pass unmodified today, as
expected — they guard the fix against regressing what already works.

## Green

`evidence/probe_cross_package.py` against the fixed tree, both build
passes, all four models (`bench`, `deep`, `same`, `unopt`):

    PYTHONPATH=$PWD /home/asa/devel/libresolid-studio/.venv/bin/python \
        openspec/changes/import-the-artifact-by-path/evidence/probe_cross_package.py \
        /tmp/probe-fixed \
        --save openspec/changes/import-the-artifact-by-path/evidence/generated_fixed

Every `import(file = …)` in every generated `.scad`, on both passes: 27
checked, 0 MISS. The two ends the bug broke are both fixed, and neither
regresses the other:

```
=== _build/bench/sim/tools/bench-Bench-3f8c65be8e28.scad   (build pass 2)
union() {
	import(file = "../parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
	translate(v = [20, 0, 0]) {
		import(file = "../parts-ExactLeaf-d20b313b0496.stl", origin = [0, 0]);
	}
	translate(v = [40, 0, 0]) {
		import(file = "../parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl", origin = [0, 0]);
	}
}
    OK   ../parts-RigidLeaf-5c13fc621640.stl
    OK   ../parts-ExactLeaf-d20b313b0496.stl
    OK   ../parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl
```

The flexible leaf's import is now `../parts-FlexLeaf-…stl` — anchored and
resolving — where it was the bare, non-resolving basename before (compare
`## The measurement` above). The rigid and exact leaves are unchanged, byte
for byte: they were correct here by coincidence (the root IS the importing
parent) and stay correct on purpose now.

```
=== _build/deep/sim/sub/deep/group-Group-34ca0e766088.scad   (both passes)
import(file = "../../parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
    OK   ../../parts-RigidLeaf-5c13fc621640.stl

=== _build/deep/sim/tools/deep_bench-DeepBench-0bc412547ce1.scad   (both passes)
import(file = "../parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
    OK   ../parts-RigidLeaf-5c13fc621640.stl
```

The intermediate assembly's own `.scad` now holds `../../parts-RigidLeaf-…`
(two directories up: `sub/deep` → `sub` → `sim`) instead of the
root-anchored `../parts-RigidLeaf-…` it held before, and resolves. The
root's own `.scad` over it is untouched, byte for byte — the guard that
fixing the intermediate end did not break the root's.

```
=== _build/same/sim/samebench-SameBench-890c6f13505b.scad   (both passes)
union() {
	import(file = "parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
	import(file = "parts-ExactLeaf-d20b313b0496.stl", origin = [0, 0]);
	import(file = "parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl", origin = [0, 0]);
}
```

Identical to `## The control` above: the same-package control's bare
basenames are untouched.

`_build/unopt/sim/tools/bench-UnoptBench-2de30c6e8e55.scad` still inlines
`cylinder(h = 12, r = 4);` with no import at all, on both passes, exactly
as before — `optimize = False` was never on this change's path and stays
off it.

Generated files saved under `evidence/generated_fixed/` (state after the
second pass), parallel to `evidence/generated/`'s pre-fix state.

Full test-file run, section 2.7's list together:

    PYTHONPATH=$PWD /home/asa/devel/libresolid-studio/.venv/bin/python \
        -m pytest tests/test_scad_import_paths.py tests/test_scad_stl.py \
        tests/test_snapshot.py tests/test_stl_node.py tests/test_sheet_leaf.py \
        tests/test_build123d_adapter.py tests/test_backend_neutral_materialization.py \
        tests/test_flexible_cache_performance.py tests/test_flexible_document.py \
        tests/test_flexible_node.py tests/test_files.py tests/test_running_document.py \
        -q -p no:cacheprovider

    371 passed, 9 warnings, 102 subtests passed

## The deep-copy cost (task 2.9)

Measured on the largest real assembly fixture the suite builds through the
ordinary `generate_scad()`/`scad_code` path: the 24-part `Machine` from
`tests/test_retained_builder_generation.py::FreshProcessBatchTest`
(`bench/solid.py`, one package below the project root — the reviewer's
"every real project" shape, not the no-op "root at the top of the source
tree" one). `_model_for_own_scad` was wrapped to time each call and count
the copied tree (`self` plus every `_children` descendant, recursively)
without changing production code; the wrapper was installed and removed
around one in-process build, mirroring `tests.base`'s trigger-STL/reassemble
dance. The timing wrapper was a throwaway and was not kept: the numbers
below are its only record (reviewer's correction — an earlier draft of this
paragraph claimed the script sat beside this file's evidence; it does not).

Second pass — every one of the 24 STLs already current on disk, the steady
state a real project actually re-builds in:

    pass 2 (all artifacts current): 25 _model_for_own_scad calls
    total wall time across all calls: 1.426 ms
    max wall time for one call: 0.6955 ms
    max copied-tree object count (one call): 49
    average wall time per call: 0.0571 ms

    slowest 5 calls:
      Machine: 0.6955 ms, 49 objects in the copied tree
      Part: 0.0615 ms, 1 objects in the copied tree
      Part: 0.0358 ms, 1 objects in the copied tree
      Part: 0.0350 ms, 1 objects in the copied tree
      Part: 0.0302 ms, 1 objects in the copied tree

Each of the 24 leaves' own `.scad` deep-copies a one-object tree (its own
`_ArtifactImport`, no children) at a few hundredths of a millisecond; the
root's own `.scad` deep-copies the 49-object tree of all 24 re-anchored
imports plus their `translate()` wrappers and the outer `union()`, at
under a millisecond. Total added cost for this 24-part build: 1.4 ms
across 25 `.scad` writes — not free, as the reviewer's note insists, but
small next to the OpenSCAD subprocess render time each of those `.scad`
files eventually feeds (milliseconds to seconds per artifact, `evidence.md`
elsewhere and `clock2-test-cost-profile.md`). The cost scales with the
number of artifact imports and wrapper nodes a `.scad` holds, not with
geometry complexity — a 24-cube machine and a 24-part machine of arbitrarily
complex leaves pay the same copy, since only the re-anchored solid2 shell
(imports, transforms, unions) is walked, never the STL/BREP the import
names.

## Reviewer finding: jscad guard tests patched a removed name

The reviewer's full suite run (2 failed, 2694 passed, 4 skipped) failed
deterministically on:

    tests/test_source_generation.py::JScadGenerationGuardTest::test_failed_renderer_discards_partial_output_and_preserves_old
    tests/test_source_generation.py::JScadGenerationGuardTest::test_source_replacement_after_renderer_preserves_old_artifact

with `AttributeError: <module 'solid_node.node.adapters.jscad'> does not
have the attribute 'import_stl'`. Cause: task 2.2 routed
`adapters/jscad.py` through `self.artifact_import(self.local_stl)` and
removed the unused `import_stl` import; task 2.7's file list did not
include `tests/test_source_generation.py`, whose two tests patched the
now-removed module-level name `solid_node.node.adapters.jscad.import_stl`
around calls to `JScadNode.as_scad(self.node(), None)`, where `self.node()`
returns a `SimpleNamespace` stand-in with no `artifact_import` attribute.

Fix, in the test file only: gave the `SimpleNamespace` stand-in returned by
`JScadGenerationGuardTest.node()` an `artifact_import=mock.Mock()`
attribute (the analogue of the old module-level patch — the successful
path now returns `self.artifact_import(self.local_stl)` off the mock
rather than hitting a real `_ArtifactImport` on a stand-in lacking
`src`/`build_dir`), and deleted the two
`mock.patch('solid_node.node.adapters.jscad.import_stl')` context managers,
keeping the `Popen` patches and everything else byte for byte.

Before (RED):

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \
      -m pytest tests/test_source_generation.py -q -p no:cacheprovider

    2 failed, 12 passed in 3.21s

After (GREEN):

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \
      -m pytest tests/test_source_generation.py -q -p no:cacheprovider

    14 passed in 3.14s

## Full suite (task 3.5)

    PYTHONPATH="$PWD" timeout 590 /home/asa/devel/libresolid-studio/.venv/bin/python \
      -m pytest tests -q -p no:cacheprovider

    2696 passed, 4 skipped, 52 warnings, 1501 subtests passed in 319.63s (0:05:19)

Exit code 0 (no `failed` count in the summary line; pytest exits 0 only
when every collected test passes).

Failures: none.

The baseline at the previous cycle was 2682 passed, 4 skipped, exit 0. This
run adds 14 passing tests, not the 12 this task's brief anticipated: 6 new
tests in `tests/test_scad_import_paths.py` (not 4 — recounted directly with
`grep -c 'def test_' tests/test_scad_import_paths.py`) plus 8 new tests
added to `tests/test_snapshot.py` (confirmed via `git diff` on that file),
6 + 8 = 14, matching 2682 + 14 = 2696 exactly. Skipped count (4) is
unchanged from baseline. All warnings observed are the pre-existing
`FutureWarning`s about reading drivers/time/ports in `render()`, unrelated
to this change.
