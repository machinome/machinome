# Evidence — `count-bodies-without-repair`

Cycle 17 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`a16e0e22b3fa3409a625c952a62fd08be671b245` (`git -C <bench> rev-parse
HEAD`). Every framework command below ran as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool>`;
`<scratch>` is the campaign scratchpad's `cycle17/` directory, which holds
the Stage P scripts `networkx_hidden.py`, `red_test_sketch.py`,
`repair_count_survey.py` and `so_arm100_mesh.py`. `<project>` is
`/home/asa/devel/machinome/projects/Robotic-Arms/SO-ARM100`, branch
`frames-and-mates`, `4438106`, read only. One test run or build at a time,
checked with `ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome
snapshot\|[m]achinome build'` before each.

## 1. Baseline on the unmodified tree (a16e0e2)

### 1.1 Interpreter and packages

```
$ python -c 'import machinome, trimesh; print(machinome.__file__, trimesh.__version__)'
/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py 4.4.9

$ python -m pip show trimesh networkx
Name: trimesh
Version: 4.4.9
Requires: numpy
Required-by: machinome
Name: networkx
Version: 3.6.1
Requires:
Required-by:
```

trimesh requires only numpy; `networkx` 3.6.1 is in the workspace venv and
required by nothing in it.

### 1.2 Six fixtures, `networkx` refused and present

`env -C <bench> HIDE_NETWORKX=1 PYTHONPATH=<bench> <venv>/python
<scratch>/networkx_hidden.py` (a `sys.meta_path` finder at position 0
refusing `networkx`), then the same with `HIDE_NETWORKX=0`. Both exit 0.
Refused, at import trimesh asked for `networkx` from `trimesh.graph`,
`trimesh.poses`, `trimesh.repair`, `trimesh.path.traversal`,
`trimesh.path.polygons`, `trimesh.path.path`, `trimesh.exchange.threemf`,
`trimesh.base` and `trimesh.exchange.threedxml`, and coped with its absence.

| Fixture | watertight | assertion, refused | `_body_count`, refused | `split(repair=True)`, refused | `split(repair=False)`, refused | present: assertion; `_body_count`; both splits |
|---|---|---|---|---|---|---|
| connected watertight box | yes | PASSED | 1 | 1 | 1 | PASSED; 1; 1, 1 |
| disconnected watertight pair | yes | fails, "contains 2 connected bodies" | 2 | 2 | 2 | fails, 2 bodies; 2; 2, 2 |
| connected open box (1 triangle missing) | no | `ModuleNotFoundError` | `ModuleNotFoundError` | `ModuleNotFoundError` | 1 | PASSED; 1; 1, 1 |
| connected open box (2 triangles missing) | no | `ModuleNotFoundError` | `ModuleNotFoundError` | `ModuleNotFoundError` | 1 | PASSED; 1; 1, 1 |
| connected open tube (large holes) | no | `ModuleNotFoundError` | `ModuleNotFoundError` | `ModuleNotFoundError` | 1 | PASSED; 1; 1, 1 |
| disconnected open pair | no | `ModuleNotFoundError` | `ModuleNotFoundError` | `ModuleNotFoundError` | 2 | fails, 2 bodies; 2; 2, 2 |

Every refused assertion's traceback, as the script prints it:

```
assertNoDisconnectedSolids -> ModuleNotFoundError: No module named 'networkx' [networkx_hidden.py:26 find_spec <- repair.py:16 <module> <- exceptions.py:30 __getattribute__ <- repair.py:261 fill_holes]
```

### 1.3 The suite's own finder

`env -C <bench> TMPDIR=<scratch>/tmp PYTHONPATH=<bench> <venv>/python
<scratch>/red_test_sketch.py` (`tests.mesh_engine_absent.run_python(SNIPPET,
absent=('networkx',))` on an open box):

```
returncode 0
CONNECTIVITY ModuleNotFoundError No module named 'networkx'
BODY COUNT ModuleNotFoundError No module named 'networkx'

asks of networkx by: ['trimesh.base', 'trimesh.exchange.threedxml', 'trimesh.exchange.threemf', 'trimesh.graph', 'trimesh.path.path', 'trimesh.path.polygons', 'trimesh.path.traversal', 'trimesh.poses', 'trimesh.repair']
```

### 1.4 SO-ARM100, baseline

`git -C <project> branch --show-current` → `frames-and-mates`;
`git -C <project> rev-parse --short HEAD` → `4438106`;
`git -C <project> status --short` → empty. `touch <scratch>/project-marker`
(2026-10-07 06:06:26 UTC), then, one at a time,
`env -C <bench> PYTHONPATH=<bench> <venv>/python <scratch>/so_arm100_mesh.py
simulation/<suite>.py [--hide-networkx]`: the README's
`machinome test --mesh simulation/<suite>.py`, run through
`tests.mesh_engine_absent.run_machinome` with `cwd=<project>`,
`SOLID_BUILD_DIR=<scratch>/so-arm100-build`, `PYTHONDONTWRITEBYTECODE=1`,
`TMPDIR=<scratch>/tmp`, and with `--hide-networkx` the finder refusing
`networkx` in every process.

| Suite | `networkx` present | `networkx` refused |
|---|---|---|
| `simulation/parts.py` | `Ran 4 tests in 0.27 seconds: 4 passed, 0 failed`; exit 0; 1.2 s | `Ran 4 tests in 0.18 seconds: 3 passed, 1 failed`; exit 1; 1.0 s |
| `simulation/hardware.py` | `Ran 5 tests in 0.13 seconds: 5 passed, 0 failed`; exit 0; 3.0 s | `Ran 5 tests in 0.11 seconds: 5 passed, 0 failed`; exit 0; 2.7 s |
| `simulation/so_arm100.py` | `Ran 12 tests in 37.46 seconds: 12 passed, 0 failed`; exit 0; 40.4 s | `Ran 12 tests in 37.00 seconds: 11 passed, 1 failed`; exit 1; 39.9 s |

Every summary line ends `(mesh engine, volume epsilon 0 mm³)`. The two
refused failures are `ImportedPartTest.test_each_selected_body_is_connected`
(`parts.py`) and `SOArm100Test.test_solid_integrity` (`so_arm100.py`), both
`ModuleNotFoundError: No module named 'networkx'`. The `parts.py` traceback:

```
Running ImportedPartTest.test_each_selected_body_is_connected.FAIL!
Traceback (most recent call last):
  File "<bench>/machinome/manager/test.py", line 506, in run_test
    method()
  File "<project>/simulation/test_parts.py", line 68, in test_each_selected_body_is_connected
    self.assertNoDisconnectedSolids(part)
  File "<bench>/machinome/test.py", line 2310, in assertNoDisconnectedSolids
    bodies = len(cached_base_mesh(solid.stl_file).split(
  File ".../site-packages/trimesh/base.py", line 1338, in split
    return graph.split(self, **kwargs)
  File ".../site-packages/trimesh/graph.py", line 372, in split
    meshes = mesh.submesh(components, only_watertight=only_watertight, **kwargs)
  File ".../site-packages/trimesh/base.py", line 2775, in submesh
    return util.submesh(mesh=self, faces_sequence=faces_sequence, **kwargs)
  File ".../site-packages/trimesh/util.py", line 1631, in submesh
    watertight = [i.fill_holes() and len(i.faces) >= 4 for i in result]
  File ".../site-packages/trimesh/base.py", line 1862, in fill_holes
    return repair.fill_holes(self)
  File ".../site-packages/trimesh/repair.py", line 261, in fill_holes
    g = nx.from_edgelist(np.column_stack((boundary_edges, index_as_dict)))
  File ".../site-packages/trimesh/exceptions.py", line 30, in __getattribute__
    raise super().__getattribute__("exception")
  File ".../site-packages/trimesh/repair.py", line 16, in <module>
    import networkx as nx
ModuleNotFoundError: No module named 'networkx'
```

With `networkx` present no process asked for it; refused, every process's
asks came from the nine trimesh modules of 1.2.

After the six runs, `find <project> -newer <scratch>/project-marker -not
-path '*/.git/*'` printed nothing and `git -C <project> status --short` was
empty.

### 1.5 Focused tests

`pytest -q -p no:cacheprovider tests/test_connectivity.py
tests/test_mesh_engine_dependency.py`:

```
32 passed in 19.50s   (wall 19.96 s)
```

### 1.6 Repair survey

Stage P's `<scratch>/repair_count_survey.log` still exists (467 lines, one
per mesh plus the summary, written by `repair_count_survey.py` with
`networkx` present); its summary line:

```
465 meshes, 157 not watertight, 0 counts differ, 0 errors, 84.5 s
```

No line reads `DIFFER` or `ERROR`.

## 2. Red tests

`tests/test_connectivity.py` gains the fixture helpers `open_box(missing=1)`,
`open_tube()` and `open_pair(gap=5.0)` beside `one_body` and `two_bodies`,
the table `BODY_COUNT_FIXTURES` (the six fixtures of 1.2 with the bodies
each holds), the snippet `OPEN_MESHES_WITHOUT_NETWORKX`, and the class
`CountWithoutRepairTest`:

- `test_open_meshes_are_counted_where_networkx_is_absent` runs the snippet
  through `tests.mesh_engine_absent.run_python(..., absent=('networkx',))`:
  an open box and an open pair, each exported to STL in a temporary
  directory, asked `assertNoDisconnectedSolids` on a `NodeDouble` and
  `_body_count` on the STL read back. It asserts exit 0, no
  `ModuleNotFoundError` in the output, `NETWORKX FOUND False` (the refusal
  was in force), the box passed and counted 1, the pair failed with
  `AssertionError ... its STL contains 2 connected bodies` and counted 2.
- `test_counts_are_the_bodies_the_mesh_holds`, in-process, one subtest per
  fixture: `_body_count` of the STL read back is the fixture's count, and
  the assertion passes a one-body fixture and fails a two-body one with
  `contains 2 connected bodies`.
- `test_counts_match_the_repairing_split`, skipped unless `networkx` can be
  imported: for each fixture `_body_count(mesh) == len(mesh.split(
  only_watertight=False, repair=True))`.

`pytest -v -rs -p no:cacheprovider
tests/test_connectivity.py::CountWithoutRepairTest`, unmodified
`machinome/test.py`:

```
tests/test_connectivity.py::CountWithoutRepairTest::test_counts_are_the_bodies_the_mesh_holds PASSED [ 33%]
tests/test_connectivity.py::CountWithoutRepairTest::test_counts_match_the_repairing_split PASSED [ 66%]
tests/test_connectivity.py::CountWithoutRepairTest::test_open_meshes_are_counted_where_networkx_is_absent FAILED [100%]

=================================== FAILURES ===================================
_ CountWithoutRepairTest.test_open_meshes_are_counted_where_networkx_is_absent _

    def test_open_meshes_are_counted_where_networkx_is_absent(self):
        run = run_python(OPEN_MESHES_WITHOUT_NETWORKX, absent=('networkx',))

        self.assertEqual(run.returncode, 0, run.output)
>       self.assertNotIn('ModuleNotFoundError', run.output)
E       AssertionError: 'ModuleNotFoundError' unexpectedly found in "NETWORKX FOUND False\nopen-box ASSERTION ModuleNotFoundError No module named 'networkx'\nopen-box COUNT ModuleNotFoundError No module named 'networkx'\nopen-pair ASSERTION ModuleNotFoundError No module named 'networkx'\nopen-pair COUNT ModuleNotFoundError No module named 'networkx'\n"

tests/test_connectivity.py:290: AssertionError
=============== 1 failed, 2 passed, 12 subtests passed in 1.93s ================
```

The guard and the repairing comparison ran (12 subtests passed, nothing
skipped: `networkx` 3.6.1 is importable in the workspace venv).

## 3. The change

`machinome/test.py`: `_body_count` splits with `only_watertight=False,
repair=False`, its docstring saying why (design.md, Decision 2), and
`assertNoDisconnectedSolids`'s mesh branch reads
`bodies = _body_count(cached_base_mesh(solid.stl_file))`. Both connectivity
assertions now count bodies through the one function.

Same command:

```
tests/test_connectivity.py::CountWithoutRepairTest::test_counts_are_the_bodies_the_mesh_holds PASSED [ 33%]
tests/test_connectivity.py::CountWithoutRepairTest::test_counts_match_the_repairing_split PASSED [ 66%]
tests/test_connectivity.py::CountWithoutRepairTest::test_open_meshes_are_counted_where_networkx_is_absent PASSED [100%]
==================== 3 passed, 12 subtests passed in 1.76s =====================
```

## 4. Green and validation

### 4.1 Fixtures and the suite's finder, before and after

`networkx_hidden.py` with `HIDE_NETWORKX=1` and `HIDE_NETWORKX=0`, both
exit 0:

| Fixture | refused, before: assertion; `_body_count` | refused, after: assertion; `_body_count` | present, before | present, after |
|---|---|---|---|---|
| connected watertight box | PASSED; 1 | PASSED; 1 | PASSED; 1 | PASSED; 1 |
| disconnected watertight pair | fails, 2 bodies; 2 | fails, 2 bodies; 2 | fails, 2 bodies; 2 | fails, 2 bodies; 2 |
| connected open box (1 triangle missing) | `ModuleNotFoundError`; `ModuleNotFoundError` | PASSED; 1 | PASSED; 1 | PASSED; 1 |
| connected open box (2 triangles missing) | `ModuleNotFoundError`; `ModuleNotFoundError` | PASSED; 1 | PASSED; 1 | PASSED; 1 |
| connected open tube (large holes) | `ModuleNotFoundError`; `ModuleNotFoundError` | PASSED; 1 | PASSED; 1 | PASSED; 1 |
| disconnected open pair | `ModuleNotFoundError`; `ModuleNotFoundError` | fails, 2 bodies; 2 | fails, 2 bodies; 2 | fails, 2 bodies; 2 |

Every failure reads `<fixture> should be one connected body, but its STL
contains 2 connected bodies`. With `networkx` present the after output
equals the before output line for line in these columns. With it refused,
the after output still holds four `ModuleNotFoundError` lines: they are
the script's own raw `split(only_watertight=False, repair=True)` column on
the four open fixtures, trimesh's call and not the framework's, and they
show the refusal was in force.

`red_test_sketch.py`, after:

```
returncode 0
CONNECTIVITY PASSED
BODY COUNT 1

asks of networkx by: ['trimesh.base', 'trimesh.exchange.threedxml', 'trimesh.exchange.threemf', 'trimesh.graph', 'trimesh.path.path', 'trimesh.path.polygons', 'trimesh.path.traversal', 'trimesh.poses', 'trimesh.repair']
```

(before: `CONNECTIVITY ModuleNotFoundError No module named 'networkx'`,
`BODY COUNT ModuleNotFoundError No module named 'networkx'`). The asks are
trimesh's at its import, as before.

### 4.2 SO-ARM100, before and after

`touch <scratch>/project-marker-after` (2026-10-07 06:10:57 UTC), then the
six runs of 1.4, one at a time, against the changed bench:

| Suite | present, before | present, after | refused, before | refused, after |
|---|---|---|---|---|
| `simulation/parts.py` | 4 passed, 0 failed; 1.2 s | 4 passed, 0 failed; 1.3 s | 3 passed, 1 failed; 1.0 s | 4 passed, 0 failed; 1.0 s |
| `simulation/hardware.py` | 5 passed, 0 failed; 3.0 s | 5 passed, 0 failed; 2.9 s | 5 passed, 0 failed; 2.7 s | 5 passed, 0 failed; 2.7 s |
| `simulation/so_arm100.py` | 12 passed, 0 failed; 40.4 s | 12 passed, 0 failed; 38.9 s | 11 passed, 1 failed; 39.9 s | 12 passed, 0 failed; 39.2 s |

The summary lines after:

```
present  parts.py      Ran 4 tests in 0.26 seconds: 4 passed, 0 failed (mesh engine, volume epsilon 0 mm³)
present  hardware.py   Ran 5 tests in 0.13 seconds: 5 passed, 0 failed (mesh engine, volume epsilon 0 mm³)
present  so_arm100.py  Ran 12 tests in 35.80 seconds: 12 passed, 0 failed (mesh engine, volume epsilon 0 mm³)
refused  parts.py      Ran 4 tests in 0.24 seconds: 4 passed, 0 failed (mesh engine, volume epsilon 0 mm³)
refused  hardware.py   Ran 5 tests in 0.11 seconds: 5 passed, 0 failed (mesh engine, volume epsilon 0 mm³)
refused  so_arm100.py  Ran 12 tests in 36.58 seconds: 12 passed, 0 failed (mesh engine, volume epsilon 0 mm³)
```

All six exit 0. With `networkx` refused,
`Running ImportedPartTest.test_each_selected_body_is_connected. passed` and
`Running SOArm100Test.test_solid_integrity. passed`. Every refused run
equals its present run, and every present run equals its baseline.
Afterwards `find <project> -newer <scratch>/project-marker-after -not -path
'*/.git/*'` printed nothing, `git -C <project> status --short` was empty
and `git -C <project> rev-parse --short HEAD` was still `4438106`.

### 4.3 Focused tests, after

`pytest -q -rs -p no:cacheprovider tests/test_connectivity.py
tests/test_mesh_engine_dependency.py`:

```
35 passed, 12 subtests passed in 20.81s   (wall 21.30 s)
```

32 before, plus the three tests of `CountWithoutRepairTest`; nothing
skipped.

## 5. Docs and changelog

`docs/project/changelog.rst`, under `Unreleased`, after the existing
bullets: the bullet of design.md, Decision 4, ending
`(count-bodies-without-repair)`. No manual page changed (design.md,
Decision 4: none names the repair or `networkx`).

`pytest -q -p no:cacheprovider tests/test_release_records.py
tests/test_docs_structure.py`:

```
25 passed, 819 subtests passed in 0.36s
```

## 6. Records, sync and archive

- 6.1 `workflow/warts.md`: the entry "**`networkx` is an undeclared need
  of the mesh path.**" left the section "YouCanBuildDog", which keeps its
  other two entries; its text is verbatim in
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
  "`count-bodies-without-repair`", with a "What shipped" paragraph.
- 6.2 `workflow/ongoing/fix-warts-3.md`, "Progress": one line for this
  cycle, after investigation 3's.
- 6.3 `openspec/specs/test-framework/spec.md`: the requirement
  "Connectivity assertions" synced by hand, its one sentence and one
  scenario added; compared with the delta by `diff` (the baseline's
  requirement from its heading to the next, against the delta from its
  heading on): equal but for the blank line before the next requirement.
  Its eight scenarios are carried and one is added (nine).
- 6.4 `openspec validate count-bodies-without-repair`: "Change
  'count-bodies-without-repair' is valid". A copy of the hand-synced
  baseline was taken to `<scratch>/spec-after-manual-sync.md`, then
  `openspec archive count-bodies-without-repair --yes` (openspec 1.6.0):
  "Specs to update: test-framework: update", "~ 1 modified", "Totals: + 0,
  ~ 1, - 0, → 0", "Change 'count-bodies-without-repair' archived as
  '2026-10-07-count-bodies-without-repair'". Its warnings: the Why
  section's length, and 20 of 22 tasks complete (6.4 and 6.5, done after
  it and ticked in the archived copy). `diff <scratch>/spec-after-manual-sync.md
  openspec/specs/test-framework/spec.md` printed nothing: the CLI's
  replacement of the requirement is byte-identical to the hand sync.
  `openspec validate --specs`: "Totals: 45 passed, 0 failed (45 items)".

## 7. Checks

### 7.1 Lint, compared against HEAD

`flake8 --max-line-length=89 machinome/test.py tests/test_connectivity.py`
(the pyenv `flake8` shim), at HEAD and after, the same two lines, both
outside this change:

```
machinome/test.py:26:35: E127 continuation line over-indented for visual indent
machinome/test.py:27:35: E127 continuation line over-indented for visual indent
```

`black --check machinome/test.py tests/test_connectivity.py` (black
26.5.1) reports "2 files would be reformatted" at HEAD and after: neither
file is in black's style (single quotes, lines wrapped at 79). `black
--diff`: `machinome/test.py` 63 hunks at HEAD and 63 after;
`tests/test_connectivity.py` 7 hunks at HEAD and 11 after, the new ones of
the same two kinds as the file's existing ones (quote normalization and
rejoining a wrapped line) over the added code, which follows the file's
own style.

### 7.2 Focused tests, once more

`pytest -q -rs -p no:cacheprovider tests/test_connectivity.py
tests/test_mesh_engine_dependency.py tests/test_release_records.py
tests/test_docs_structure.py`:

```
60 passed, 831 subtests passed in 20.82s   (wall 21.29 s)
```

### 7.3 The full suite, once, alone

`pytest -q -p no:cacheprovider` at the bench root, no other run of ours
in progress:

```
4749 passed, 4 skipped, 55 warnings, 6706 subtests passed in 672.12s (0:11:12)
(exit 0, wall 674 s)
```

Everything is left uncommitted.
