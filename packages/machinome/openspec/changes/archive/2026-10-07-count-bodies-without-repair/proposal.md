## Why

From `workflow/warts.md`, section "YouCanBuildDog":

> - **`networkx` is an undeclared need of the mesh path.**
>   `assertNoDisconnectedSolids` now takes the exact path for an exact solid
>   (`_routes_exact`), which closed the first half of this finding. Its mesh
>   path (`split(only_watertight=False)`) can still reach trimesh's
>   `fill_holes`, which imports `networkx`, and `networkx` is not among the
>   package's declared dependencies: the workspace venv has it only because
>   it was installed by hand on 2026-09-07. Whether trimesh's split still
>   reaches `fill_holes` is unverified. Condensed 2026-10-04.

It does. Measured on the bench `fix-warts-3` at `5a71304` with trimesh 4.4.9
(design.md, Context):

- Both connectivity assertions count bodies with
  `mesh.split(only_watertight=False)`: `assertNoDisconnectedSolids` on a
  solid's own STL (`machinome/test.py:2310`), and `assertJoined`'s mesh
  branch on the union, through `_body_count` (`machinome/test.py:461`).
  Neither passes `repair`, so trimesh's default `repair=True` sends every
  component to `fill_holes`, which builds a `networkx` graph for any
  component that is not watertight. trimesh does not require `networkx`
  (only its `easy` extra does), machinome does not declare it, and the CI
  requirement files do not install it.
- With `networkx` refused on import, on six exported STL fixtures, the two
  watertight ones are decided and the four that are not watertight raise
  `ModuleNotFoundError: No module named 'networkx'` from
  `trimesh/repair.py:261 fill_holes`, through both
  `assertNoDisconnectedSolids` and `_body_count`. The same split with
  `repair=False` returns the right count for all six.
- **The originating evidence in a project.** `Robotic-Arms/SO-ARM100`
  (branch `frames-and-mates`, `4438106`) admits `Lower_Arm.stl`'s eight
  bodies with `require_watertight = False` and calls
  `assertNoDisconnectedSolids` on them. Its documented
  `machinome test --mesh` suites, run against the bench with `networkx`
  refused in every process (the suite's own finder,
  `tests/mesh_engine_absent`), fail where they pass with it:
  `simulation/parts.py` 3 passed, 1 failed
  (`test_each_selected_body_is_connected`), and `simulation/so_arm100.py`
  11 passed, 1 failed (`test_solid_integrity`), both on that
  `ModuleNotFoundError`. With `networkx` present they pass: 4, 5 and 12
  passed for `parts.py`, `hardware.py` and `so_arm100.py`.

The repair's work is thrown away: only `len()` of the split is read. trimesh
builds the list of components before it repairs any of them and returns that
same list, so filling holes cannot change how many there are. Over the 465
STL files of the four catalogue projects that combine
`require_watertight = False` with `assertNoDisconnectedSolids`
(SO-ARM100, roboto_origin, hexapod_spiderbot_model, mechanical-multiplier),
157 of them not watertight, the count with `repair=True` and with
`repair=False` is identical for every file (design.md, Context, 3).
`machinome/node/stl.py:_bodies` already splits with `repair=False`, for the
reason the framework gives there: a repair machines geometry the project
never authored.

## What Changes

- `_body_count` in `machinome/test.py` counts with
  `mesh.split(only_watertight=False, repair=False)`, its docstring saying
  why, and `assertNoDisconnectedSolids` counts a solid's STL through
  `_body_count` rather than its own `split` call, so both connectivity
  assertions count bodies one way.
- A red test in `tests/test_connectivity.py`: in a subprocess where
  `networkx` cannot be imported (`tests.mesh_engine_absent.run_python(...,
  absent=('networkx',))`), `assertNoDisconnectedSolids` passes a connected
  open STL and fails a disconnected open STL naming 2 bodies, and
  `_body_count` counts both. Today it is red with `ModuleNotFoundError`.
  Beside it, a guard over the six fixtures in-process: the verdicts and
  counts as expected, and, where `networkx` is installed, each count equal
  to the repairing split's.
- One sentence and one scenario in the `test-framework` requirement
  "Connectivity assertions": bodies are counted as the mesh holds them, with
  no repair, so counting needs nothing outside machinome's core
  dependencies.
- The changelog's `Unreleased` section takes one bullet; the warts entry
  moves to the campaign's resolved record.

**Deliberately out**, with the reason:

- Declaring `networkx`. It would have to be a core dependency, not a `mesh`
  one: `tests/test_mesh_engine_dependency.py::
  ExactPathWithoutMeshEngineTest::test_connectivity_asserts_without_the_mesh_engine`
  pins that `assertNoDisconnectedSolids` needs no mesh engine. A new core
  dependency for a computation whose result is discarded is the wrong
  remedy (design.md, Decision 1).
- `StlNode._load_source_mesh` reading a `stl_source` that names a `.3mf`
  through trimesh's 3MF loader, which also uses `networkx`. Not in the
  finding and not tested; investigation 3 records it as adjacent.
- `node/stl.py:_bodies`. It already passes `repair=False`; it stays a
  separate function because it returns the sorted components, not a count.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `test-framework`:
  - MODIFIED "Connectivity assertions": on the mesh path a mesh is split
    with no repair, as it holds its geometry, so counting needs no package
    outside machinome's core dependencies; its eight scenarios carried and
    one added.

## Impact

- Code: `machinome/test.py` (`_body_count`'s split and docstring;
  `assertNoDisconnectedSolids`'s mesh branch calls it).
- Tests: `tests/test_connectivity.py` (one red test, one guard).
- Docs: `docs/project/changelog.rst` (`Unreleased`, one bullet). No manual
  page is made wrong: the assertion reference and the API reference say "a
  split of the part's own STL", and `docs/architecture.md` already says
  "nothing is ever auto-repaired" (design.md, Decision 4).
- Records: the warts entry to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`; a progress line in
  `workflow/ongoing/fix-warts-3.md`.
- Dependencies: none added or removed.
- Verdicts: unchanged wherever they were reached, by construction and by
  measurement (design.md, Context, 2 and 3). Where `networkx` is absent, an
  open mesh is now counted instead of raising.
- Projects: none edited. SO-ARM100 is run read-only against the bench, its
  build in the scratchpad.
- No ADR: this restores the stated rule that geometry is never repaired
  (`docs/architecture.md`, the `StlNode` paragraph) to the one counting call
  that did not follow it.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign's cycle 17, `count-bodies-without-repair`, cut from
investigation 3 (7 October 2026) and validated in `Robotic-Arms/SO-ARM100`.
