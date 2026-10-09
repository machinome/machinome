# Evidence — `witness-on-a-touching-pair`

Standalone framework cycle. Bench `machinome/WTs/witness-on-a-touching-pair`,
branch `witness-on-a-touching-pair`, planning commit
`e5c653e1704188596b9cf8ffaa4b49cd006e3522` on base
`d9fd98d35979a7e8f5e70fa87210668eea08d936` (`git -C <bench> rev-parse
HEAD`, `HEAD~1`). Every framework command below ran as
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
/home/asa/devel/machinome/.venv/bin/<tool>`. `<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/b6c584a7-7bce-4b09-8a25-3732645cbf62/scratchpad/applier`;
`<pair>` is the proposal's capture of wall clock 02's placed weight shell
and screw at `ec2a05d`,
`/tmp/claude-1000/-home-asa-devel-machinome/b6c584a7-7bce-4b09-8a25-3732645cbf62/scratchpad/distance-tier/shell-screw/`.
One test run or project run of ours at a time, checked with `ps -eo
pid,args | grep '[p]ytest\|[m]achinome test\|[m]easure.py'` before each.
Other sessions shared the host throughout; the load average is noted per
run, so absolute times are the host's and the counts are the evidence.

## 1. Baseline on the unmodified tree (`e5c653e`)

### 1.1 Interpreter

```
$ python -c 'import machinome, OCP, cadquery, sys; print(machinome.__file__, cadquery.__version__, sys.version.split()[0])'
/home/asa/devel/machinome/machinome/WTs/witness-on-a-touching-pair/machinome/__init__.py 2.7.0 3.12.3

$ pip show cadquery-ocp
Name: cadquery-ocp
Version: 7.8.1.1.post1
```

### 1.2 The guard's tests

`pytest -q -p no:cacheprovider tests/test_brep_common_guard.py
tests/test_witness_neighbourhood.py tests/test_resolved_brep_witness.py
tests/test_engine_package.py` (load average 4.56 at the start, 4.35 at the
end):

```
29 passed, 61 subtests passed in 3.43s   (wall 4.51 s)
```

Split: the three guard files `19 passed, 7 subtests passed in 3.41s`;
`tests/test_engine_package.py` `10 passed, 54 subtests passed in 1.25s`.

### 1.3 The captured pair, bench

`<pair>` holds `screw.brep` (sha256 `930ca4dd…7c0950`) and `shell.brep`
(sha256 `6d4db74b…4236988`), captured 9 October at 16:55.

`python openspec/changes/witness-on-a-touching-pair/measurements/m6_bench_screw_first.py <pair>`
(screw first; load average 4.01 at the start, 2.81 at the end):

```
faces 5 32 volumes 325.896 52192.127
distance 0.0 0.401 s
witness None total 98.4 s
stats {'classify': 2490}
timing {'classify': 98.3}
wall 100.21 s
```

`python workflow/ongoing/distance-tier-measurement-2026-10-09/stencil.py <pair>`
(shell first; load average 2.59 at the start, 1.50 at the end):

```
faces 32 5 volumes 52192.127 325.896
distance 0.0 0.37 s
witness None total 289.4 s
stats {'classify': 2547}
timing {'classify': 289.2}
wall 291.06 s
```

The counts are 9 October's to the unit (2,490 and 2,547 classifications,
no candidate, no margin measured); the times are lower than 9 October's
146.9 s and 324 s on a quieter host.

### 1.4 Voron-2's thread seats, bench

`<voron>` is `/home/asa/devel/machinome/projects/3D-Printers/Voron-2`,
`a88fac458c9ea594a1dc11e4714f516734dac186`, `git status --short` empty.
The script is `measurements/voron_thread_seats.py` in this change: an
assembled `ThreadSeatContacts`, each nut and screw `cq_shape(part)`
translated by `-BED_DATUM` as the project's
`simulation/test_thread_seat_contacts.py` places its bodies, and
`intersect_shapes` on each pair in both orders. Its first run stopped at
once on `SidewaysReadError` (it asked the class declaration's parts to
assemble, not an instance's) before loading any geometry; the script was
corrected to assemble an instance. Marker `<scratch>/voron-marker` touched
before each run.

`env -C <voron> PYTHONPATH=<bench>:<voron> PYTHONDONTWRITEBYTECODE=1
SOLID_BUILD_DIR=<scratch>/voron-build python <change>/measurements/voron_thread_seats.py`
(load average 2.35 at the start, 2.30 at the end; log
`<scratch>/voron-bench.log`):

```
loaded 12 bodies in 1.5 s
1290 1425: BrepCommonInconsistency at (48.469257178063614, -31.63885398162032, -43.32235772104128) (0.74 s)
1425 1290: BrepCommonInconsistency at (49.453297885547684, -32.43929848094744, -42.900867495254396) (0.73 s)
1305 1431: BrepCommonInconsistency at (201.53018830652974, 361.6386053417469, -43.322413659896036) (0.78 s)
1431 1305: BrepCommonInconsistency at (200.54620356506825, 362.43929839880036, -42.900867278759044) (0.81 s)
1306 1434: BrepCommonInconsistency at (48.4692573737759, 358.36114593723175, -43.32235757759779) (0.78 s)
1434 1306: BrepCommonInconsistency at (49.45329825189357, 357.560701734992, -42.90086771177648) (0.74 s)
1319 918: BrepCommonInconsistency at (129.75327238365998, 358.4708297463765, -43.626892632158864) (0.59 s)
918 1319: BrepCommonInconsistency at (130.5959624038181, 357.7342727284763, -43.06862604518789) (0.65 s)
1421 1083: BrepCommonInconsistency at (48.434152062382125, 103.218277590216, -33.48194452642218) (0.56 s)
1083 1421: BrepCommonInconsistency at (48.434152062382125, 103.218277590216, -33.48194452642218) (0.56 s)
1422 1084: BrepCommonInconsistency at (48.43415206238282, 218.21827759021102, -33.48194452641548) (0.56 s)
1084 1422: BrepCommonInconsistency at (48.43415206238282, 218.21827759021102, -33.48194452641548) (0.56 s)
wall 11.89 s
```

All twelve orders refused under the bench, each at the point shown. After
both runs `git -C <voron> status --short` printed nothing, `HEAD` was
`a88fac4`, and `find <voron> -newer <scratch>/voron-marker -not -path
'*/.git*'` printed nothing.

## 2. Red tests

### 2.1 The new file

`tests/test_witness_touching_pair.py`, design.md's four red tests:

- `NearestSideTest.test_a_point_reads_its_side_from_its_nearest_boundary_point`,
  the unit cases of `measurements/m8_side_cases.py`: a unit box inside at
  its centre, outside past a face and past an edge, on the boundary
  10⁻⁹ mm outside and inside a face, undecided past a corner; an L-shaped
  solid inside by its concave edge; a cylinder outside and inside by its
  seam. With it, for the first review note,
  `test_a_face_is_oriented_as_its_solid_holds_it`: a unit box rebuilt from
  a shell stored REVERSED, each face reversed in it (seven lines of
  `BRep_Builder`; the test asserts the stored shell's orientation and a
  positive volume), read inside at its centre and by a face, outside past
  a face and past an edge. Built and checked first in a one-off command:
  volume 1.0, `BRepCheck_Analyzer` valid, stored shell
  `TopAbs_REVERSED`, the classifier IN at the centre and OUT past a face.
- `PinInItsHoleTest`: `_boolean` patched empty, the classifier wrapped to
  count calls by its solid's faces (plate 7, pin 3), plate and pin in both
  orders: the empty common returned, the pin asked, the plate never.
- `RefusalUnmovedTest`: overlapping unit boxes, the 0.4 mm slab, a pin
  0.2 mm over its hole, and a key 0.1 mm into its slot and 0.5 mm into its
  floor (`m3_synthetic.py`'s `slot_and_key(0.1)`), `_boolean` patched
  empty: the refusal's point with `_nearest_side` patched to return `None`
  equals the point without the patch.
- `LoneInsideReadingUnaskedTest`: `LoneInsideReadingTest`'s boxes and
  lying classifier, with the real side reading: the empty common returned
  and the lie never told (`lied_at == []`).

### 2.2 Red on the unmodified engine

`pytest -q -p no:cacheprovider -rf tests/test_witness_touching_pair.py`
(load average 1.87 at the start, 1.73 at the end):

```
SUBFAILED[centre] ...NearestSideTest::test_a_face_is_oriented_as_its_solid_holds_it
SUBFAILED[inside, by a face] ...
SUBFAILED[past a face] ...
SUBFAILED[past an edge] ...
SUBFAILED[box, centre] ...NearestSideTest::test_a_point_reads_its_side_from_its_nearest_boundary_point
  (and each of its eight other cases)
E       AttributeError: module 'machinome.engine.brep' has no attribute '_nearest_side'

SUBFAILED[plate first] ...PinInItsHoleTest::test_a_pin_that_fits_its_hole_is_settled_without_the_plate
E               AssertionError: 1404 != 0
SUBFAILED[pin first] ...
E               AssertionError: 486 != 0

SUBFAILED[overlapping boxes] ...RefusalUnmovedTest::test_a_side_reading_does_not_move_a_refusal
  (and the slab, the pin and the key)
E           AttributeError: <module 'machinome.engine.brep' from '.../machinome/engine/brep.py'> does not have the attribute '_nearest_side'

FAILED ...LoneInsideReadingUnaskedTest::test_the_side_reading_excludes_a_lone_inside_reading_unasked
E       AssertionError: Lists differ: [(5.7735026918962585e-05, 0.999942264973081, 0.24994226497308103)] != []

20 failed, 4 passed in 2.27s
```

Each red for the reason tasks.md names: the side helper does not exist;
the plate's classifier is asked 1,404 times with the plate first and 486
with the pin first (M7's counts); the patch target does not exist; the lie
is told once. (The four "passed" are pytest-subtests' parent entries.)

## 3. The change

- 3.1 `machinome/engine/brep.py`: `_boundary(solid)` returns the solid's
  shells as one compound (explored from the solid), its face map
  (`TopExp.MapShapes_s(solid, TopAbs_FACE, …)`) and its edge-to-face map
  (`TopExp.MapShapesAndUniqueAncestors_s(solid, TopAbs_EDGE, TopAbs_FACE,
  …)`). `_nearest_side(boundary, point)` runs one
  `BRepExtrema_DistShapeShape` from the point's vertex to the shells
  (`Extrema_ExtFlag_MIN`) and reads each solution with `_side_at`: a face
  support is looked up in the solid's face map, so the face read is the
  face as explored from the solid and its orientation the composed one
  (review note); an edge support is looked up in the edge-to-face map,
  two faces or one seam face counted twice, each normal at the edge
  parameter through that face's pcurve (`BRep_Tool.CurveOnSurface_s`);
  `BRepGProp_Face.Normal` gives each oriented normal, normalised before
  summing. 'on' when the distance is within a face's tolerance there;
  'out'/'in' by the sign of `(p − q)·n`, clear at `|cos| ≥ 0.9` on a face
  and `≥ 0.1` on an edge; `None` for a vertex, an edge with another face
  count, unmapped, degenerated or not same-parameter, a missing pcurve, a
  failed or empty extrema, a non-finite distance or tolerance, a normal
  of magnitude ≤ 10⁻¹², a vanishing sum of unit normals (≤ 10⁻⁹), or
  solutions that do not all read the same.
- 3.2 Same file, `_false_empty_witness`: the operands' (classifier, solid)
  pairs are ordered by total face count (`cheap` and `dear`, the first
  operand cheap on a tie); `holders(point)` asks the cheap operand's
  classifiers, then reads the dear operand's sides, then the cheap
  operand's sides over the solids its classifiers put inside, drops the
  solids reading 'out' or 'on', returns `None` when either operand has
  none left, and asks the dear operand's classifiers over the solids left.
  Boundaries are built lazily, once per solid and search, so a search
  with no point inside the cheaper operand builds none. The candidates
  come back in the first/second roles, so the margins, the neighbour
  check (first operand's classifier, then the second's, as before) and
  the returned point are unchanged; the stencil, its budget and order,
  the section, the errors and their messages are untouched.
- 3.3 The docstrings of `_false_empty_witness` and `intersect_shapes` name
  the order and the side reading.
- 3.4 `LoneInsideReadingTest` (`tests/test_witness_neighbourhood.py`) and
  `test_rounded_in_classification_on_tangent_faces_is_not_a_witness`
  (`tests/test_resolved_brep_witness.py`) each gain one patch,
  `patch('machinome.engine.brep._nearest_side', return_value=None)`, in
  their existing `with`; nothing else changes. The first still asserts
  `len(lied_at) == 1`.

Before writing 3.2, the reversed-shell test of 2.1 was checked to
discriminate: a boundary built from the stored shell with its own
REVERSED dropped (faces read as the shell holds them) reads the box's
`(.5, .5, .9)` as 'out' and `(1.5, .5, .5)` and `(1.5, 1.5, .5)` as 'in';
`_boundary` of the solid reads 'in', 'out', 'out'.

## 4. Green

### 4.1 Focused tests

`pytest -q -p no:cacheprovider tests/test_witness_touching_pair.py
tests/test_brep_common_guard.py tests/test_witness_neighbourhood.py
tests/test_resolved_brep_witness.py tests/test_engine_package.py
tests/test_verdict_store.py tests/test_brep_geometry.py` (load average
1.72 at the start, 1.84 at the end):

```
145 passed, 91 subtests passed in 8.87s   (wall 9.93 s)
```

Decision 5's premise, re-read on the changed engine: HEAD's unedited
`tests/test_witness_neighbourhood.py` and `tests/test_resolved_brep_witness.py`
(copied to `<scratch>/orig/` by `git show HEAD:…`) give `1 failed, 9
passed`: `LoneInsideReadingTest` fails on its own assertion,
`AssertionError: 0 != 1` (the lie is never asked for), and the rounded
test passes without reaching its classifier; with the one patch each, both
pass on the classifier path, as 4.1 shows.

### 4.2 flake8

The workspace venv carries no flake8; the host's (`flake8 7.3.0`,
pycodestyle 2.14.0, pyflakes 3.4.0), run at the bench root so
`setup.cfg`'s `[flake8]` applies: `flake8 --max-line-length=89
machinome/engine/brep.py tests/test_witness_touching_pair.py
tests/test_witness_neighbourhood.py
openspec/changes/witness-on-a-touching-pair/measurements/voron_thread_seats.py`
prints nothing, exit 0. `tests/test_resolved_brep_witness.py` reports
`E128` at its line 49 and `E501` at its line 79, both carried by HEAD's
copy of the file (its lines 48 and 78), not by the edit.

## 5. Validation outside the repository

### 5.1 The captured pair, changed bench

`python openspec/changes/witness-on-a-touching-pair/measurements/m6_bench_screw_first.py <pair>`
(screw first; load average 1.85 at the start and the end):

```
faces 5 32 volumes 325.896 52192.127
distance 0.0 0.374 s
witness None total 1.1 s
stats {'classify': 1872}
timing {'classify': 0.1}
wall 2.83 s
```

`python workflow/ongoing/distance-tier-measurement-2026-10-09/stencil.py <pair>`
(shell first; load average 1.85 at the start, 1.86 at the end):

```
faces 32 5 volumes 52192.127 325.896
distance 0.0 0.392 s
witness None total 1.3 s
stats {'classify': 1872}
timing {'classify': 0.1}
wall 3.13 s
```

No candidate and no margin measured in either order; 1,872
classifications, one per stencil point. Which solid each was asked of,
and what the side readings said, from a scratch counter
(`<scratch>/per_solid.py`: the classifier wrapped to count calls by its
solid's face count, `_nearest_side` wrapped to count readings by the
solid's face count and the reading; load average 1.63 at the start and
the end):

```python
"""Per-solid classifier calls and side readings on the captured pair, both
orders, against the changed bench. Scratch."""
import collections, sys, time
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
P = sys.argv[1]
shell, screw = brep.read_brep(P + '/shell.brep'), brep.read_brep(P + '/screw.brep')
asked, sides = collections.Counter(), collections.Counter()
class Counting:
    def __init__(self, solid):
        self.native = BRepClass3d_SolidClassifier(solid); self.faces = len(brep._faces(solid))
    def Perform(self, point, tolerance):
        asked[self.faces] += 1; self.native.Perform(point, tolerance)
    def Rejected(self): return self.native.Rejected()
    def State(self): return self.native.State()
native_side = brep._nearest_side
def side(boundary, point):
    found = native_side(boundary, point)
    sides[(boundary[1].Extent(), found)] += 1
    return found
brep.BRepClass3d_SolidClassifier = Counting
brep._nearest_side = side
for label, first, second in (('shell first', shell, screw), ('screw first', screw, shell)):
    asked.clear(); sides.clear(); t = time.perf_counter()
    found = brep._false_empty_witness(first, second)
    print(f'{label}: witness {found}, {time.perf_counter() - t:.2f} s, classifier calls by faces {dict(asked)}, side readings by (faces, side) {dict(sides)}', flush=True)
```

```
shell first: witness None, 1.27 s, classifier calls by faces {5: 1872}, side readings by (faces, side) {(32, 'out'): 713, (32, 'on'): 17}
screw first: witness None, 1.17 s, classifier calls by faces {5: 1872}, side readings by (faces, side) {(32, 'out'): 605, (32, 'on'): 13}
```

The shell's classifier is asked at no point in either order. The screw
holds 730 stencil points with the shell given first and 618 with the
screw given first (the section's edge order differs), M5's counts; at
every one the shell reads outside or on its boundary, none undecided, so
the screw's own side is never read. 289.4 s and 98.4 s on the unmodified
bench (1.3) become 1.3 s and 1.1 s.

### 5.2 Voron-2, changed bench

The script of 1.4, `env -C <voron> PYTHONPATH=<bench>:<voron>
PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/voron-build python
<change>/measurements/voron_thread_seats.py` (marker
`<scratch>/voron-marker2`; load average 1.54 at the start, 1.98 at the
end; log `<scratch>/voron-change.log`):

```
loaded 12 bodies in 0.9 s
1290 1425: BrepCommonInconsistency at (48.469257178063614, -31.63885398162032, -43.32235772104128) (0.74 s)
1425 1290: BrepCommonInconsistency at (49.453297885547684, -32.43929848094744, -42.900867495254396) (0.71 s)
1305 1431: BrepCommonInconsistency at (201.53018830652974, 361.6386053417469, -43.322413659896036) (0.74 s)
1431 1305: BrepCommonInconsistency at (200.54620356506825, 362.43929839880036, -42.900867278759044) (0.74 s)
1306 1434: BrepCommonInconsistency at (48.4692573737759, 358.36114593723175, -43.32235757759779) (0.72 s)
1434 1306: BrepCommonInconsistency at (49.45329825189357, 357.560701734992, -42.90086771177648) (0.76 s)
1319 918: BrepCommonInconsistency at (129.75327238365998, 358.4708297463765, -43.626892632158864) (0.62 s)
918 1319: BrepCommonInconsistency at (130.5959624038181, 357.7342727284763, -43.06862604518789) (0.58 s)
1421 1083: BrepCommonInconsistency at (48.434152062382125, 103.218277590216, -33.48194452642218) (0.55 s)
1083 1421: BrepCommonInconsistency at (48.434152062382125, 103.218277590216, -33.48194452642218) (0.55 s)
1422 1084: BrepCommonInconsistency at (48.43415206238282, 218.21827759021102, -33.48194452641548) (0.55 s)
1084 1422: BrepCommonInconsistency at (48.43415206238282, 218.21827759021102, -33.48194452641548) (0.56 s)
wall 11.19 s
```

`diff` of the two logs with times, the load line and the wall line
stripped prints nothing: every one of the twelve orders is refused under
the change at the point it was refused at under the bench. Afterwards
`git -C <voron> status --short` printed nothing, `HEAD` was `a88fac4`,
and `find <voron> -newer <scratch>/voron-marker2 -not -path '*/.git*'`
printed nothing.

### 5.3 The lock and the clock, cold, changed bench

One run at a time, the lock first. Each ran
`workflow/ongoing/distance-tier-measurement-2026-10-09/measure.py` (the
9 October wrapper, unchanged; `MEASURE_VARIANTS` unset, so only the
engine's own distance is measured) in-process from the project, with
`PYTHONPATH=<bench>:<project>`, `PYTHONDONTWRITEBYTECODE=1`, a scratch
`SOLID_BUILD_DIR` and `MEASURE_OUT` under `<scratch>`, under
`/usr/bin/time -v`. Per-group witness times were compared with the
9 October per-common records by a scratch script, `<scratch>/groups.py`,
which groups the empty commons by their unordered pair of names and sums
`witness_s` over those at zero distance and at a distance of at most
10⁻⁶ mm (the summaries' "zero" and "tiny").

The 9 October records are the host's under another agent's load of about
two cores; this afternoon's load is noted per run. The ratios are
therefore indicative, and the counts are the evidence.

#### The combination safe lock at `8f185f6`

`<lock>` is `/home/asa/devel/machinome/projects/Locks/Combination-safe-lock`,
`main`, `8f185f616341814301968b9ce4f95ba626c5b8a1`, `git status --short`
empty. `env -C <lock> PYTHONPATH=<bench>:<lock> PYTHONDONTWRITEBYTECODE=1
SOLID_BUILD_DIR=<scratch>/lock-build MEASURE_OUT=<scratch>/lock.jsonl
/usr/bin/time -v python <bench>/workflow/ongoing/distance-tier-measurement-2026-10-09/measure.py
test --brep --no-verdict-store` (log `<scratch>/lock.log`):

```
start 2026-10-09T17:59:54+00:00  load average: 1.39, 1.84, 5.87
Ran 14 tests in 239.15 seconds: 14 passed, 0 failed (verdict store off)
Elapsed (wall clock) time (h:mm:ss or m:ss): 4:03.22
Maximum resident set size (kbytes): 979260
exit=0 end 2026-10-09T18:03:58+00:00  load average: 4.31, 3.09, 5.44
```

Summary against 9 October's (`lock-threaded-variants.summary.json`):

| | 9 October | this change |
| --- | --- | --- |
| suite | 14 passed | 14 passed |
| commons / empty / refused | 730 / 725 / 0 | 730 / 725 / 0 |
| empties at zero / ≤ 10⁻⁶ mm / positive distance | 23 / 78 / 624 | 23 / 78 / 624 |
| witness on all commons | 130.2 s | 147.8 s |
| witness on zero-distance empties | 16.9 s | 23.5 s |
| witness on ≤ 10⁻⁶ mm empties | 23.7 s | 27.0 s |
| witness on positive-distance empties | 89.6 s | 97.3 s |

By pair group, zero and ≤ 10⁻⁶ mm empties, witness time 9 October | this
change:

```
cam/lock_pin                    zero 4 tiny 51    9.35 s |  10.77 s (1.15x)
cam/dial                        zero 1 tiny  0    5.93 s |  11.57 s (1.95x)
lock_pin/wheel_3                zero 4 tiny  5    4.78 s |   4.94 s (1.03x)
lock_pin/wheel_2                zero 4 tiny  5    4.65 s |   4.84 s (1.04x)
peg_3/wheel_3                   zero 1 tiny  3    4.60 s |   4.50 s (0.98x)
lock_pin/wheel_1                zero 4 tiny  5    4.31 s |   4.88 s (1.13x)
peg_1/wheel_1                   zero 1 tiny  2    2.77 s |   3.29 s (1.18x)
peg_2/wheel_2                   zero 1 tiny  2    2.69 s |   3.34 s (1.24x)
frame/frame_ring_1_2_1          zero 1 tiny  0    0.45 s |   0.61 s (1.36x)
frame/frame_ring_3              zero 1 tiny  0    0.31 s |   0.57 s (1.81x)
cam/peg_3                       zero 0 tiny  2    0.26 s |   0.39 s (1.51x)
frame_ring_1_2_2/frame_ring_3   zero 1 tiny  0    0.20 s |   0.32 s (1.59x)
peg_2/peg_3                     zero 0 tiny  2    0.18 s |   0.33 s (1.80x)
peg_1/peg_2                     zero 0 tiny  1    0.09 s |   0.16 s (1.90x)
```

The lock has no slow classifier; its touching pairs grow by 1.24× in all
(40.6 s to 50.5 s), every group within design.md's 0.9×–2.2× range. The
largest growth is `cam`/`dial` (`lock_pin`/`cam` is 1.15×): the dial
(519 faces) against the cam (40), 5.93 s to 11.57 s. On 9 October the
dial's classifier was asked first; now the cam's is, and each point inside
the cam reads its side of the dial, an extrema over 519 faces, where
before a dial classification settled it. That is the risk design.md names
("side readings cost more than a healthy classifier on many-faced
solids"), at 1.95×. Positive-distance empties grow 1.09×.

Afterwards `git -C <lock> status --short` was empty as before, `HEAD`
`8f185f6`, and `find <lock> -newer <scratch>/lock-marker -not -path
'*/.git*'` printed nothing.

#### Wall clock 02 at `ec2a05d`

`<clock>` is the detached worktree
`/home/asa/devel/machinome/projects/3DPrintedClocks/WTs/distance-tier-ec2a05d`,
`ec2a05d10729ddbd2b2e7be1e86e97794bf41621`, `git status --short` empty.
`env -C <clock> PYTHONPATH=<bench>:<clock> PYTHONDONTWRITEBYTECODE=1
SOLID_BUILD_DIR=<scratch>/clock-build MEASURE_OUT=<scratch>/clock.jsonl
/usr/bin/time -v python <bench>/workflow/ongoing/distance-tier-measurement-2026-10-09/measure.py
test wall_clock_02 --brep --no-verdict-store` (log `<scratch>/clock.log`;
the host's load average rose from 2.6 to between 5 and 12 during the run):

```
start 2026-10-09T18:04:29+00:00  load average: 2.61, 2.79, 5.26
Running WallClock02Test.test_assembly_integrity........FAIL! at instant 0.0 (8 of 8 instants failed)
Running WallClock02Test.test_movement_runs_free_through_a_swing....FAIL! at instant 0.0 (48 of 48 instants failed)
Running WallClock02Test.test_solid_integrity.FAIL! at instant 0
Running WallClock02Test.test_source_body_inventory.FAIL! at instant 0
Running WallClock02Test.test_the_train_meshes_all_the_way_round....FAIL! at instant 0.0 (32 of 32 instants failed)
Running WallClock02Test.test_the_weight_screw_engages_its_separate_nut.FAIL! at instant 0
Ran 22 tests in 3534.74 seconds: 16 passed, 6 failed (verdict store off)
Elapsed (wall clock) time (h:mm:ss or m:ss): 58:59.23
Maximum resident set size (kbytes): 1031852
exit=0 end 2026-10-09T19:03:28+00:00  load average: 12.69, 9.69, 9.00
```

The six failures are `collet`/`hinge_screw` interfering by 14.578953408065129
mm³ (three tests), `standoffs` as two connected bodies (two tests) and
`movement.weight.screw should intersect movement.weight.nut`: verdicts on
non-empty commons and on connectivity, none of them a refusal. The
9 October summaries do not record the suite's pass count; its per-common
records hold the same six non-empty commons with the same volumes
(`collet`/`hinge_screw` 14.578953408065129 mm³ among them) and no refusal,
as this run does.

Summary against 9 October's (`wall-clock-02.summary.json`):

| | 9 October | this change |
| --- | --- | --- |
| commons / empty / non-empty / refused | 643 / 637 / 6 / 0 | 643 / 637 / 6 / 0 |
| empties at zero / ≤ 10⁻⁶ mm / positive distance | 115 / 9 / 513 | 115 / 9 / 513 |
| Boolean on all commons | 279.2 s | 308.2 s |
| distance on all commons | 1,724.9 s | 1,776.5 s |
| witness on all commons | 948.0 s | 1,167.2 s |
| witness on zero-distance empties | 582.9 s | 810.3 s |
| witness on ≤ 10⁻⁶ mm empties | 47.2 s | 9.6 s |
| witness on positive-distance empties | 317.8 s | 347.2 s |
| wall | 3,108 s | 3,536 s |

By pair group, zero and ≤ 10⁻⁶ mm empties, witness time 9 October | this
change (`<scratch>/clock-groups.txt`):

```
screw/shell                              zero   1 tiny   0 near-witness   297.84 s | zero   1 tiny   0 near-witness     1.26 s (0.00x)
arbor/hour_holder                        zero  51 tiny   0 near-witness   119.01 s | zero  51 tiny   0 near-witness   469.05 s (3.94x)
cannon_pinion/hour_holder                zero  42 tiny   0 near-witness    57.18 s | zero  42 tiny   0 near-witness   244.18 s (4.27x)
beat_screw/collet                        zero   1 tiny   0 near-witness    43.72 s | zero   1 tiny   0 near-witness     1.80 s (0.04x)
nut/shell                                zero   0 tiny   1 near-witness    41.15 s | zero   0 tiny   1 near-witness     0.62 s (0.02x)
plates/standoffs                         zero   1 tiny   0 near-witness    15.04 s | zero   1 tiny   0 near-witness    31.04 s (2.06x)
front_4/plates                           zero   1 tiny   0 near-witness     6.08 s | zero   1 tiny   0 near-witness     8.64 s (1.42x)
ring/upper_ring_nut                      zero   1 tiny   0 near-witness     4.96 s | zero   1 tiny   0 near-witness     1.12 s (0.23x)
front_3/plates                           zero   1 tiny   0 near-witness     4.86 s | zero   1 tiny   0 near-witness     6.21 s (1.28x)
back_0/plates                            zero   1 tiny   0 near-witness     4.62 s | zero   1 tiny   0 near-witness     7.18 s (1.55x)
collet/collet_screw                      zero   1 tiny   0 near-witness     4.24 s | zero   1 tiny   0 near-witness     0.40 s (0.09x)
back_1/plates                            zero   0 tiny   1 near-witness     4.14 s | zero   0 tiny   1 near-witness     6.40 s (1.55x)
back_3/plates                            zero   1 tiny   0 near-witness     4.13 s | zero   1 tiny   0 near-witness     6.41 s (1.55x)
back_2/plates                            zero   1 tiny   0 near-witness     3.92 s | zero   1 tiny   0 near-witness     6.56 s (1.67x)
front_2/plates                           zero   1 tiny   0 near-witness     3.87 s | zero   1 tiny   0 near-witness     6.28 s (1.62x)
front_1/plates                           zero   1 tiny   0 near-witness     3.74 s | zero   1 tiny   0 near-witness     5.99 s (1.60x)
front_0/plates                           zero   1 tiny   0 near-witness     3.49 s | zero   1 tiny   0 near-witness     7.19 s (2.06x)
body/collet                              zero   1 tiny   0 near-witness     3.13 s | zero   1 tiny   0 near-witness     2.52 s (0.80x)
cannon_pinion/minute_hand                zero   0 tiny   1 near-witness     0.91 s | zero   0 tiny   1 near-witness     0.28 s (0.31x)
beat_nut/collet                          zero   1 tiny   0 near-witness     0.75 s | zero   1 tiny   0 near-witness     0.77 s (1.04x)
body/top_nyloc                           zero   1 tiny   0 near-witness     0.67 s | zero   1 tiny   0 near-witness     0.78 s (1.16x)
hour_hand/hour_holder                    zero   1 tiny   0 near-witness     0.64 s | zero   1 tiny   0 near-witness     0.72 s (1.12x)
rating_button/rating_nyloc               zero   0 tiny   1 near-witness     0.48 s | zero   0 tiny   1 near-witness     0.94 s (1.95x)
lower_ring_nut/ring                      zero   1 tiny   0 near-witness     0.46 s | zero   1 tiny   0 near-witness     1.16 s (2.52x)
body/hinge_screw                         zero   1 tiny   0 near-witness     0.24 s | zero   1 tiny   0 near-witness     0.27 s (1.14x)
nut/screw                                zero   0 tiny   1 near-witness     0.20 s | zero   0 tiny   1 near-witness     0.40 s (2.03x)
collet_half_nut/collet_screw             zero   1 tiny   0 near-witness     0.17 s | zero   1 tiny   0 near-witness     0.27 s (1.65x)
beat_nut/beat_screw                      zero   1 tiny   0 near-witness     0.14 s | zero   1 tiny   0 near-witness     0.33 s (2.38x)
top_half_nut/top_nyloc                   zero   0 tiny   1 near-witness     0.11 s | zero   0 tiny   1 near-witness     0.24 s (2.10x)
lid/lid_screw_left                       zero   0 tiny   1 near-witness     0.10 s | zero   0 tiny   1 near-witness     0.31 s (3.11x)
lid/lid_screw_right                      zero   0 tiny   1 near-witness     0.09 s | zero   0 tiny   1 near-witness     0.27 s (2.98x)
beat_screw/beat_thumb_nut                zero   0 tiny   1 near-witness     0.06 s | zero   0 tiny   1 near-witness     0.17 s (2.88x)
beat_crinkle_washer/beat_thumb_nut       zero   1 tiny   0 near-witness     0.04 s | zero   1 tiny   0 near-witness     0.14 s (3.15x)
```

Per asking, 9 October | this change:

| group | faces (first, second) | askings | Boolean | distance | witness |
| --- | --- | --- | --- | --- | --- |
| `arbor`/`hour_holder` | 244, 218 | 51 | 0.39 s / 0.43 s | 1.51 s / 1.56 s | **2.33 s / 9.20 s** |
| `cannon_pinion`/`hour_holder` | 83, 218 | 42 | 0.23 s / 0.24 s | 0.70 s / 0.69 s | **1.36 s / 5.81 s** |
| `plates`/`standoffs` | 681, 112 | 1 | 1.15 s / 0.42 s | 0.97 s / 0.55 s | 15.04 s / 31.04 s |

The three slow touching pairs the design named are settled: `shell`/`screw`
297.84 s to 1.26 s, `beat_screw`/`collet` 43.72 s to 1.80 s, `nut`/`shell`
41.15 s to 0.62 s. But two of the clock's largest touching groups grow
far past design.md's 2.2×: `arbor`/`hour_holder` 3.94× (119.01 s to
469.05 s) and `cannon_pinion`/`hour_holder` 4.27× (57.18 s to 244.18 s),
and `plates`/`standoffs` 2.06×. The Boolean's and the distance's time per
asking on those pairs is unchanged, so the host's load does not account
for it. `cannon_pinion`/`hour_holder` keeps its order (the cannon pinion,
83 faces, was and is asked first), so its growth is the side readings
alone. In all, the clock's witness on zero-distance empties rises from
582.9 s to 810.3 s despite the 380 s saved on the three named pairs.

**This is a stop point of the apply brief:** a validation run shows a
witness-time group growing by more than the design's 2.2× on a real pair.
The tree is left as it is (tasks 1 to 5.3 done, 6.1 to 6.5 drafted, 5.4,
5.5, 6.5's group note and 7 not done), and the evidence goes back to the
orchestrator.

Afterwards `git -C <clock> status --short` was empty as before, `HEAD`
`ec2a05d`, and `find <clock> -newer <scratch>/clock-marker -not -path
'*/.git*'` printed nothing.

#### Diagnosis of the growth (scratch, after the stop)

To say what the choice is about, the clock's `cannon_pinion`/`hour_holder`
pair was captured as BREP with the 9 October `capture.py`
(`env -C <clock> PYTHONPATH=<bench>:<clock> PYTHONDONTWRITEBYTECODE=1
SOLID_BUILD_DIR=<scratch>/clock-build MEASURE_OUT=<scratch>/pinion
MEASURE_PAIR=cannon_pinion,hour_holder python
<bench>/workflow/ongoing/distance-tier-measurement-2026-10-09/capture.py test
wall_clock_02 --brep --no-verdict-store`: `CAPTURED cannon_pinion,hour_holder
after 24 commons`, 19:04–19:05, load average 4.48 to 3.28; `git -C <clock>
status --short` empty and nothing newer than `<scratch>/capture-marker` in
the worktree afterwards) and its witness timed by solid and instrument
with `<scratch>/diagnose.py`:

```python
"""Where the witness's time goes on a captured touching pair, under the
change and with every side undecided (today's classifications). Scratch."""
import collections, sys, time
from unittest.mock import patch
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
P, A, B = sys.argv[1:4]
first, second = brep.read_brep(f'{P}/{A}.brep'), brep.read_brep(f'{P}/{B}.brep')
print(A, len(brep._faces(first)), 'faces;', B, len(brep._faces(second)), 'faces')
asked, spent = collections.Counter(), collections.Counter()
class Counting:
    def __init__(self, solid):
        self.native = BRepClass3d_SolidClassifier(solid); self.faces = len(brep._faces(solid))
    def Perform(self, point, tolerance):
        t = time.perf_counter(); self.native.Perform(point, tolerance)
        spent['classify', self.faces] += time.perf_counter() - t; asked['classify', self.faces] += 1
    def Rejected(self): return self.native.Rejected()
    def State(self): return self.native.State()
native_side = brep._nearest_side
def side(boundary, point):
    t = time.perf_counter(); found = native_side(boundary, point)
    faces = boundary[1].Extent()
    spent['side', faces] += time.perf_counter() - t; asked['side', faces, found] += 1
    return found
native_resolved = brep._resolved_interior
def resolved(solid, point):
    t = time.perf_counter(); found = native_resolved(solid, point)
    spent['margin'] += time.perf_counter() - t; asked['margin'] += 1
    return found
for label, sider in (('change', side), ('undecided', lambda b, p: None)):
    asked.clear(); spent.clear(); t = time.perf_counter()
    with patch.object(brep, 'BRepClass3d_SolidClassifier', Counting), \
         patch.object(brep, '_nearest_side', sider), \
         patch.object(brep, '_resolved_interior', resolved):
        found = brep._false_empty_witness(first, second)
    print(f'{label}: witness {found}, {time.perf_counter() - t:.2f} s')
    print('  calls', dict(asked)); print('  seconds', {k: round(v, 2) for k, v in spent.items()}, flush=True)
```

`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 python
<scratch>/diagnose.py <scratch>/pinion cannon_pinion hour_holder` (load
average 2.63 at the start, 2.58 at the end):

```
cannon_pinion 83 faces; hour_holder 218 faces
change: witness None, 4.36 s
  calls {('classify', 83): 1872, ('side', 218, 'out'): 426}
  seconds {('classify', 83): 0.48, ('side', 218): 3.57}
undecided: witness None, 1.19 s
  calls {('classify', 83): 1872, ('classify', 218): 426}
  seconds {('classify', 83): 0.48, ('classify', 218): 0.39}
```

The 426 stencil points inside the cannon pinion all read outside the hour
holder, correctly; but the hour holder's classifier settles each in
0.9 ms, and its side reading, one extrema over its 218 faces, costs
8.4 ms. Design.md's Decision 2 costed a side reading at "classifications
of similar cost" on healthy pairs (from M5's synthetic pairs, the worst a
214-face body at 0.9×–2.2×). On the clock's gear-train parts the extrema
costs about nine classifications of a healthy solid, and the witness on
this pair is 3.7× today's (4.36 s against 1.19 s; the suite measured
4.27×). The side reading pays off only where the other operand's
classifier is slow (the shell's 200 ms against its 1.4–2.1 ms reading);
where it is fast, it costs.

## 3b. The revision (design.md, "Revision after apply evidence")

A second applier continued from the tree as the first left it (HEAD
`4add7c35`, the planning commit amended with the Revision; the first
apply's work uncommitted). `<scratch2>` is
`/tmp/claude-1000/-home-asa-devel-machinome/b6c584a7-7bce-4b09-8a25-3732645cbf62/scratchpad/applier2`;
the first applier's `<scratch>` was read, never written.

### 3b.2 Red against the whole-shell search

`tests/test_witness_touching_pair.py` gains `CountingExtrema` (the native
`BRepExtrema_DistShapeShape`, patched into the engine module, counting the
faces of every shape loaded into it, by its constructor, `LoadS1` or
`LoadS2`) and `NearestSideSearchTest.test_a_point_near_one_face_is_measured_against_few_faces`:
a 240-gon prism (`cq.Workplane().polygon(240, 20).extrude(5)`, 242 faces),
a point 0.01 mm outside and one 0.01 mm inside the middle of a side face;
each must read its side (`'out'`, `'in'`) and be measured against fewer
than a tenth of the faces.

`pytest -q -p no:cacheprovider -rf tests/test_witness_touching_pair.py`
on the tree as the first apply left it (load average 0.40 at the start,
1.73 at the end):

```
>               self.assertLess(CountingExtrema.faces, total // 10)
E               AssertionError: 242 not less than 24
SUBFAILED[outside] tests/test_witness_touching_pair.py::NearestSideSearchTest::test_a_point_near_one_face_is_measured_against_few_faces
SUBFAILED[inside] tests/test_witness_touching_pair.py::NearestSideSearchTest::test_a_point_near_one_face_is_measured_against_few_faces
2 failed, 6 passed, 19 subtests passed in 2.45s
```

Red for the stated reason: both sides read correctly, and the one extrema
is loaded with the whole compound, all 242 faces. The other tests of the
file pass.

### 3b.1, 3b.2 The revised search

- `_boundary(solid)` returns `(boxes, faces, edge_faces)`: the face map
  and edge-to-face map as before (both explored from the solid, so each
  face's orientation is the composed one), and an `(F, 2, 3)` array of one
  box per face in the face map's order, each taken as `face_bounds` takes
  it (`BRepBndLib.Add_s(face, box, False)`); a void box is stored as
  unbounded, so its face is never passed over. The compound of shells is
  gone.
- `_nearest_side(boundary, point)`: one numpy pass gives the point's
  distance to every box (zero inside); faces are visited in ascending box
  distance (`argsort`, stable), each by one `BRepExtrema_DistShapeShape`
  from the point's vertex (built once) to that face alone, the face taken
  from the face map; the visit stops at the first box distance not below
  the best face distance; the face with the least distance keeps its
  extrema, whose solutions `_side_at` reads unchanged (a face support
  through the face map, an edge support through the edge-to-face map).
  A failed or empty extrema, or a non-finite distance, on any face visited
  leaves the side undecided. `_side_at`, `_false_empty_witness` and the
  two patched tests are untouched. `TopAbs_SHELL` is no longer imported.

Green: the same command, load average 1.03 at the start and the end:

```
6 passed, 21 subtests passed in 2.32s
```

The task 2.1 side tests pass unchanged, the reversed-shell test among
them. Faces measured per reading on the prism (`<scratch2>/prism_probe.py`,
the test's counter): 0.01 mm outside and inside, 0.5 mm outside and
inside: one face each; 3 mm inside, two (the side face and a cap).

### 3b.3 Reruns

#### 5.1 The captured pair

`m6_bench_screw_first.py <pair>` (load average 0.35 at the start, 0.48 at
the end) and `stencil.py <pair>` (0.48 at the start and the end):

```
faces 5 32 volumes 325.896 52192.127
distance 0.0 0.361 s
witness None total 1.3 s
stats {'classify': 1872}
wall 2.90 s

faces 32 5 volumes 52192.127 325.896
distance 0.0 0.34 s
witness None total 1.6 s
stats {'classify': 1872}
wall 3.18 s
```

`<scratch>/per_solid.py <pair>` (load average 0.44 at the start, 0.49 at
the end):

```
shell first: witness None, 1.51 s, classifier calls by faces {5: 1872}, side readings by (faces, side) {(32, 'out'): 713, (32, 'on'): 17}
screw first: witness None, 1.29 s, classifier calls by faces {5: 1872}, side readings by (faces, side) {(32, 'out'): 605, (32, 'on'): 13}
```

The same readings as the first search, no shell classification.

#### 5.2 Voron-2

The script of 1.4 against the revised bench, marker
`<scratch2>/voron-marker`, `SOLID_BUILD_DIR=<scratch2>/voron-build` (load
average 0.45 at the start, 0.57 at the end; log
`<scratch2>/voron-revised.log`): twelve `BrepCommonInconsistency`
refusals, wall 11 s. `diff` against the bench's log of 1.4, times, the
load line and the wall line stripped, prints nothing: every order is
refused at the bench's point. `git -C <voron> status --short` empty
before and after, `HEAD` `a88fac4`, nothing newer than the marker.

#### 5.3 The lock, cold

As in 5.3 above, `SOLID_BUILD_DIR=<scratch2>/lock-build`,
`MEASURE_OUT=<scratch2>/lock.jsonl` (log `<scratch2>/lock.log`):

```
start 2026-10-09T19:15:07+00:00 load average: 0.52, 1.65, 4.73
Ran 14 tests in 205.08 seconds: 14 passed, 0 failed (verdict store off)
Elapsed (wall clock) time (h:mm:ss or m:ss): 3:28.46
Maximum resident set size (kbytes): 1171244
exit=0 end 2026-10-09T19:18:36+00:00 load average: 4.79, 2.83, 4.55
```

`git -C <lock> status --short` empty before and after, `HEAD` `8f185f6`,
nothing newer than `<scratch2>/lock-marker`.

| | 9 October | first search | revised search |
| --- | --- | --- | --- |
| suite | 14 passed | 14 passed | 14 passed |
| commons / refused | 730 / 0 | 730 / 0 | 730 / 0 |
| empties at zero / ≤ 10⁻⁶ mm / positive | 23 / 78 / 624 | 23 / 78 / 624 | 23 / 78 / 624 |
| witness on zero-distance empties | 16.9 s | 23.5 s | 13.3 s |
| witness on ≤ 10⁻⁶ mm empties | 23.7 s | 27.0 s | 19.4 s |
| witness on positive-distance empties | 89.6 s | 97.3 s | 87.7 s |

By pair group (`<scratch>/groups.py`), zero and ≤ 10⁻⁶ mm empties,
witness time 9 October | first search | revised search, the ratio to
9 October:

```
cam/lock_pin                    zero 4 tiny 51   9.35 s | 10.77 s |  9.44 s (1.01x)
cam/dial                        zero 1 tiny  0   5.93 s | 11.57 s |  4.96 s (0.84x)
lock_pin/wheel_3                zero 4 tiny  5   4.78 s |  4.94 s |  3.80 s (0.79x)
lock_pin/wheel_2                zero 4 tiny  5   4.65 s |  4.84 s |  3.84 s (0.83x)
peg_3/wheel_3                   zero 1 tiny  3   4.60 s |  4.50 s |  1.93 s (0.42x)
lock_pin/wheel_1                zero 4 tiny  5   4.31 s |  4.88 s |  3.77 s (0.88x)
peg_1/wheel_1                   zero 1 tiny  2   2.77 s |  3.29 s |  1.45 s (0.52x)
peg_2/wheel_2                   zero 1 tiny  2   2.69 s |  3.34 s |  1.51 s (0.56x)
frame/frame_ring_1_2_1          zero 1 tiny  0   0.45 s |  0.61 s |  0.48 s (1.07x)
frame/frame_ring_3              zero 1 tiny  0   0.31 s |  0.57 s |  0.51 s (1.61x)
cam/peg_3                       zero 0 tiny  2   0.26 s |  0.39 s |  0.28 s (1.09x)
frame_ring_1_2_2/frame_ring_3   zero 1 tiny  0   0.20 s |  0.32 s |  0.32 s (1.59x)
peg_2/peg_3                     zero 0 tiny  2   0.18 s |  0.33 s |  0.30 s (1.63x)
peg_1/peg_2                     zero 0 tiny  1   0.09 s |  0.16 s |  0.15 s (1.70x)
```

Every tier's total falls below 9 October and `cam`/`dial` (the 519-face
dial read from the cam) returns to 0.84×; but four sub-second groups stay
above the Revision's 1.3×, where the first search had them.

#### Whether the lock's small groups are the side reading

The suite's per-asking times are one sample each, so the lock's
`frame`/`frame_ring_3` pair was captured (`env -C <lock>
PYTHONPATH=<bench>:<lock> PYTHONDONTWRITEBYTECODE=1
SOLID_BUILD_DIR=<scratch2>/lock-build MEASURE_OUT=<scratch2>/frame-ring
MEASURE_PAIR=frame,frame_ring_3 python <bench>/workflow/ongoing/distance-tier-measurement-2026-10-09/capture.py
test --brep --no-verdict-store`, 19:19, load average 2.90 to 3.51; the
lock's status empty, `HEAD` `8f185f6` and nothing newer than
`<scratch2>/capture-marker` afterwards) and timed in-process by
`<scratch2>/ab.py`: the unmodified engine (`git show
HEAD:machinome/engine/brep.py` saved as `<scratch2>/brep_head.py` and
imported beside the bench's package), the revised change, and the change
with `_nearest_side` patched to `None`, interleaved, median of five (three
for the pinion). A first version of `ab.py` left its `None` patch in place
after the first round, so its "change" rows timed the undecided search;
it was corrected (`patch.start`/`stop`, and an assertion that the native
`_nearest_side` is back after each run) before the rows below, and
`<scratch2>/order.py` (the change three times, the bench once, the change
twice more, one process) confirmed the change's time does not depend on
the order of runs: 3.88, 3.78, 3.86, bench 1.14, 3.90, 3.87 s on the
pinion and holder.

Load average 1.38 at the start, 1.23 at the end:

```
frame 50 faces; frame_ring_3 15 faces
bench      witness None median 0.307 s min 0.299 s
change     witness None median 0.513 s min 0.491 s
undecided  witness None median 0.222 s min 0.216 s
bench      calls {('classify', 50): 1872, ('classify', 15): 258}
change     calls {('classify', 15): 1872, ('side', 50): 567}

cannon_pinion 83 faces; hour_holder 218 faces
bench      witness None median 1.090 s min 1.073 s
change     witness None median 3.873 s min 3.819 s
undecided  witness None median 1.096 s min 1.073 s
bench      calls {('classify', 83): 1872, ('classify', 218): 426}
change     calls {('classify', 83): 1872, ('side', 218): 426}
```

The lock's `frame`/`frame_ring_3` grows 1.67× in-process, as the suite
measured; the clock's `cannon_pinion`/`hour_holder` grows 3.55×, against
the first search's 3.7× (4.36 s against 1.19 s above). The revised search
saves little on the hour holder.

Where it goes, by `<scratch2>/holder_probe.py` and `side_probe.py` (each
side reading of the search replayed with the extrema wrapped to time each
face; load average 0.77 to 1.04):

```
hour_holder (218 faces), 426 readings: 7.14 ms a reading; faces measured per reading mean 2.9, max 4
  face 4 Plane: 426 visits, 3.67 ms each, box span [29.19 29.19 41.28]
  face 5 Plane: 426 visits, 2.47 ms each, box span [29.19 29.19 41.28]
  face 207 Cylinder: 276 visits, 0.03 ms each
  face 214 Cylinder: 107 visits, 0.03 ms each

frame (50 faces), 567 readings: 0.59 ms a reading; faces measured per reading mean 3.7, max 4
  face 7 Cylinder: 567 visits, 0.17 ms each, box span [56. 22.75 56.]
  faces 42, 47 Plane: 0.10 ms each; the rest 0.02–0.03 ms each
```

`<scratch2>/holder_faces.py`: the hour holder sits on a 45° axis in the
clock; its faces 4 and 5 are the gear's two flat sides, planes with normal
(0.707, −0.707, 0) bounded by 211 edges each (the tooth outline). Their
axis-aligned boxes are 29 × 29 × 41 mm slabs (`AddOptimal_s` gives the
same box: it is the enclosure of a tilted disc, not slack) that hold every
stencil point near the bore, so both are measured at every reading, and
an extrema from a vertex to a face of 211 edges costs 2.5–3.7 ms. On the
frame the search measures 3.7 small faces a reading at about 0.3 ms in
all, and the rest of its 0.59 ms is the reading's own cost (the numpy
pass, the vertex, the loop, the normals); the classifiers settle a point
in about 0.09 ms (0.222 s undecided for 1,872 ring and 567 frame
classifications).

### Focused tests and flake8 on the revised tree

The focused tests of 4.1 (load average 0.81 at the start, 0.84 at the
end): `146 passed, 93 subtests passed in 8.52s` (wall 9.68 s), the one
test added by 3b.2 included. `flake8 --max-line-length=89
machinome/engine/brep.py tests/test_witness_touching_pair.py
tests/test_witness_neighbourhood.py`: nothing, exit 0.

### Stop point

The Revision's acceptance fails, so the apply stops here, the tree as it
is: the revised search is in `machinome/engine/brep.py` with its red-first
test, green; the records of tasks 6.1 to 6.5 are still the first apply's
drafts; 5.4, 5.5 and 7 are not done; nothing is committed.

- The lock (5.3): `frame`/`frame_ring_3` 1.61×, `frame_ring_1_2_2`/`frame_ring_3`
  1.59×, `peg_2`/`peg_3` 1.63×, `peg_1`/`peg_2` 1.70× of their 9 October
  witness times, each a real pair group, the first confirmed in-process at
  1.67×; the lock's totals do fall below 9 October.
- The clock: not rerun. Its `cannon_pinion`/`hour_holder` pair, captured
  from the clock, grows 3.55× in-process under the revised search (the
  suite measured 4.27× under the first search, whose in-process ratio was
  3.7×), so the clock's two hour-holder groups would exceed 1.3× by about
  the same factor and an hour's run would only confirm it.
- The three pathological pairs stay settled (5.1 above; the clock's
  `beat_screw`/`collet` and `nut`/`shell` not rerun), and Voron-2's twelve
  refusals do not move.

What the measurements say for the choice, not resolved here: a side
reading through the faces' boxes costs about 0.3–0.6 ms on a small part
and 2.5–7 ms where a face with hundreds of edges has an axis-aligned box
around the stencil (a gear's flat side on a part placed off the axes),
while a healthy classifier settles a point in 0.05–0.9 ms and the
shell's in 190–300 ms. So any reading made at every point the cheaper
operand holds costs more than it saves on a healthy pair, whatever its
search; a tighter enclosure (an oriented box, or a planar face's distance
to its plane as a second lower bound) would spare the hour holder's two
gear faces but not the frame's floor of about 0.3 ms a reading.
Decision 3 already rejected reading the side only where the other
classifier is slow, as timing-based.

## 3c. The second revision (design.md, "Second revision after apply evidence")

A third applier continued from the tree as the second left it (HEAD
`271cc1f4`, the planning commit amended with the second Revision; the
earlier appliers' work uncommitted). `<scratch3>` is
`/tmp/claude-1000/-home-asa-devel-machinome/b6c584a7-7bce-4b09-8a25-3732645cbf62/scratchpad/applier3`;
`<scratch>` and `<scratch2>` were read, never written.

### 3c.2 Red against the box-only search

`tests/test_witness_touching_pair.py`: `CountingExtrema` also keeps every
shape loaded into it (`loaded`), and
`NearestSideSearchTest.test_a_tilted_flat_face_is_passed_over_by_its_plane`
builds the 240-gon prism of 3b.2, takes the side face whose normal is
nearest (1, 1, 0) and the point 0.01 mm outside its centre, and turns both
45° about the x axis, which lies in the prism's lower end face. The test
checks its own premise (the two end faces, the faces of area over 100 mm²,
have boxes, by `bounds`, holding the point: 2.5 mm from either end face's
plane), then asserts the point reads `'out'` and that neither end face is
among the shapes loaded into an extrema.

`pytest -q -p no:cacheprovider -rf tests/test_witness_touching_pair.py`
on the tree as the second applier left it. A first run failed for another
reason, `AttributeError: 'Vector' object has no attribute 'rotateX'` in the
test itself; the point is now turned as a vertex
(`cq.Vertex.makeVertex(...).rotate(*axis, 45)`), and the run (load average
1.65 at the start, 1.67 at the end) is red for the stated reason:

```
>       self.assertEqual(measured, [], f'{CountingExtrema.faces} faces '
                         f'measured, the end faces among them')
E       AssertionError: Lists differ: [<OCP.OCP.TopoDS.TopoDS_Shape object at 0x[65 chars]1f0>] != []
E       First list contains 2 additional elements.
E       - [<OCP.OCP.TopoDS.TopoDS_Shape object at 0x7d9485c28270>,
E       -  <OCP.OCP.TopoDS.TopoDS_Shape object at 0x7d9485c281f0>] : 3 faces measured, the end faces among them
FAILED tests/test_witness_touching_pair.py::NearestSideSearchTest::test_a_tilted_flat_face_is_passed_over_by_its_plane
1 failed, 6 passed, 21 subtests passed in 2.73s
```

The box-only search reads the side correctly and measures three faces at
that point: the side face and both end faces.

### 3c.1, 3c.2 The bound

- `_boundary(solid)` returns `(boxes, faces, edge_faces, planes,
  cylinders)`. For each face, `BRepAdaptor_Surface(face).GetType()`: a
  plane records its index, `Plane().Axis()`'s location and unit direction;
  a cylinder its index, `Cylinder().Axis()`'s location and unit direction
  and `Radius()`; each with the face's tolerance there, the largest of
  `BRep_Tool.Tolerance_s(face)` and `BRep_Tool.MaxTolerance_s(face,
  TopAbs_EDGE | TopAbs_VERTEX)`. Kept as numpy columns, `None` when the
  solid has no face of that type; a face of another type, or whose surface
  does not read finite, has its box alone.
- `_nearest_side`: after the box distances, in the same numpy pass, each
  planar face's bound is raised to `|(p − o)·n| − tol` and each cylindrical
  face's to `| ‖(p − a) − ((p − a)·d) d‖ − r | − tol` where that is larger.
  The visit order (ascending bound, stable), the single-face extrema, the
  stop rule and `_side_at` are unchanged.
- One design question met, answered by the design's own claim that the
  bound is a lower bound on the face distance: the extrema measures a
  vertex against the face's edges and vertices too, whose 3-D geometry may
  stand off the surface by up to their tolerance, so a distance to the
  plane or cylinder is a lower bound on what the extrema reports only less
  that tolerance. The tolerance is therefore taken off the surface
  distance (it is 10⁻⁷ mm on the parts measured here, so the bound loses
  nothing). The box carries its tolerance already.

Green, the same command (load average 1.35 at the start, 1.32 at the end):

```
7 passed, 21 subtests passed in 3.22s
```

`<scratch3>/tilted_probe.py` (the test's point and counter): under the
revised bound, `side out faces measured 1 end faces among them 0`; under
the box-only search the run above measured 3.

### 3c In-process timings on the captured pairs

`<scratch3>/ab3.py <dir> <first> <second> <repeats> <order>`: the
unmodified engine (`git show HEAD:machinome/engine/brep.py` saved as
`<scratch3>/brep_head.py`, imported as its own module; the script asserts
it is not the bench's module and has no `_nearest_side`), the change, and
the change with `_nearest_side` patched to `None` by a patch started and
stopped around each run (the script asserts the native `_nearest_side` is
back after every run), interleaved in the order given, each round printed.
Each pair ran twice, in two orders, so an order effect would show.

The clock's cannon pinion and hour holder (`<scratch>/pinion`), three
rounds each (load average 1.08 at the start, 1.32 at the end):

```
cannon_pinion 83 faces; hour_holder 218 faces
round 0: change 2.756, bench 1.065, undecided 1.102
round 1: change 2.813, bench 1.180, undecided 1.115
round 2: change 2.850, bench 1.102, undecided 1.109
change     witness None median 2.813 s min 2.756 s
bench      witness None median 1.102 s min 1.065 s
undecided  witness None median 1.109 s min 1.102 s
bench      calls {('classify', 83): 1872, ('classify', 218): 426}
change     calls {('classify', 83): 1872, ('side', 218): 426}

round 0: bench 1.262, undecided 1.140, change 2.953
round 1: bench 1.120, undecided 1.119, change 2.813
round 2: bench 1.159, undecided 1.185, change 2.906
bench      witness None median 1.159 s min 1.120 s
undecided  witness None median 1.140 s min 1.119 s
change     witness None median 2.906 s min 2.813 s
```

The lock's frame and ring (`<scratch2>/frame-ring`), five rounds each (load
average 1.31 at the start, 1.42 at the end):

```
frame 50 faces; frame_ring_3 15 faces
change     witness None median 0.415 s min 0.409 s   (rounds 0.431, 0.415, 0.415, 0.409, 0.413)
bench      witness None median 0.313 s min 0.313 s
undecided  witness None median 0.227 s min 0.226 s
bench      calls {('classify', 50): 1872, ('classify', 15): 258}
change     calls {('classify', 15): 1872, ('side', 50): 567}
(the other order: bench 0.316, undecided 0.227, change 0.409)
```

| pair | unmodified | first search | box search | box and surface bound |
| --- | --- | --- | --- | --- |
| `cannon_pinion`/`hour_holder` | 1.10 s | 4.36 s (3.7×) | 3.87 s (3.55×) | 2.81–2.91 s (2.55×) |
| `frame`/`frame_ring_3` | 0.31 s | — | 0.51 s (1.67×) | 0.41 s (1.32×) |

The order of runs does not move the numbers. Where the hour holder's
readings still go (`<scratch3>/holder_probe.py`, the second applier's
probe, and `<scratch3>/face4_probe.py`; load average 1.30 to 1.35):

```
points read on the holder 426
total 2.01 s, 4.71 ms a reading; faces measured per reading: mean 1.5 median 1.0 max 2
sides Counter({'out': 426})
  face 4 Plane: 426 visits, 3.74 ms each, box span [29.19 29.19 41.28]
  face 207 Cylinder: 211 visits, 0.04 ms each

planes 82 cylinders 133 faces 218
face 4 extrema distance: min 0.0006561 median 0.009279 max 0.1312
face 4 plane distance:   min 0.0006561 median 0.009279 max 0.1312
face 207 extrema distance: min 0.000676 median 0.1234 max 1.588
face 4 nearer than 207 at 291 of 426
```

The plane bound passes over face 5, the gear's far flat side (2.9 faces a
reading become 1.5), but face 4, the near flat side, is where the cannon
pinion touches the hour holder: it is the nearest face at 291 of the 426
points, its plane distance equals its face distance there, and no lower
bound can spare its extrema, which costs 3.7 ms on a plane bounded by 211
edges against 0.9 ms for the hour holder's classifier.

### 3c.3, 4 Focused tests and flake8 on the second revision

`pytest -q -p no:cacheprovider tests/test_witness_touching_pair.py
tests/test_brep_common_guard.py tests/test_witness_neighbourhood.py
tests/test_resolved_brep_witness.py tests/test_engine_package.py
tests/test_verdict_store.py tests/test_brep_geometry.py` (load average
1.27 at the start, 1.38 at the end; another session's `machinome test
--brep` of a microscope project was running on the host, not ours):

```
147 passed, 93 subtests passed in 8.63s   (wall 9.71 s)
```

`flake8 --max-line-length=89 machinome/engine/brep.py
tests/test_witness_touching_pair.py tests/test_witness_neighbourhood.py`:
nothing, exit 0.

### 3c.3 Reruns

#### 5.1 The captured pair

`m6_bench_screw_first.py <pair>` (load average 1.43 at the start and the
end) and `stencil.py <pair>` (1.43 at the start, 2.76 at the end):

```
faces 5 32 volumes 325.896 52192.127
distance 0.0 0.367 s
witness None total 0.5 s
stats {'classify': 1872}
timing {'classify': 0.1}
wall 2.12 s

faces 32 5 volumes 52192.127 325.896
distance 0.0 0.384 s
witness None total 0.5 s
stats {'classify': 1872}
timing {'classify': 0.1}
wall 2.31 s
```

`<scratch>/per_solid.py <pair>` (load average 2.76):

```
shell first: witness None, 0.52 s, classifier calls by faces {5: 1872}, side readings by (faces, side) {(32, 'out'): 713, (32, 'on'): 17}
screw first: witness None, 0.47 s, classifier calls by faces {5: 1872}, side readings by (faces, side) {(32, 'out'): 605, (32, 'on'): 13}
```

The same readings as both earlier searches, no shell classification;
289.4 s and 98.4 s on the unmodified bench (1.3) are now 0.5 s.

#### 5.2 Voron-2

The script of 1.4, marker `<scratch3>/voron-marker`,
`SOLID_BUILD_DIR=<scratch3>/voron-build` (load average 2.56 at the start,
2.47 at the end; log `<scratch3>/voron-second.log`): twelve
`BrepCommonInconsistency` refusals, 0.55–0.80 s each. `diff` against the
bench's log of 1.4, times, the load line and the wall line stripped,
prints nothing: every order is refused at the bench's point. `git -C
<voron> status --short` empty before and after, `HEAD` `a88fac4`, nothing
newer than the marker.

#### 5.3 The lock, cold

As in 5.3 above, `SOLID_BUILD_DIR=<scratch3>/lock-build`,
`MEASURE_OUT=<scratch3>/lock.jsonl` (log `<scratch3>/lock.log`):

```
start 2026-10-09T19:33:21+00:00 load average: 2.15, 1.48, 2.42
Ran 14 tests in 210.05 seconds: 14 passed, 0 failed (verdict store off)
Elapsed (wall clock) time (h:mm:ss or m:ss): 3:33.70
Maximum resident set size (kbytes): 1042224
exit=0 end 2026-10-09T19:36:54+00:00 load average: 2.92, 2.15, 2.49
```

`git -C <lock> status --short` empty before and after, `HEAD` `8f185f6`,
nothing newer than `<scratch3>/lock-marker`.

`<scratch3>/groups3.py` groups the empty commons by their unordered pair
of names as `groups.py` does, sums `witness_s` per class (zero, at most
10⁻⁶ mm, positive) and per group over every class, and flags a group grown
by more than 5 s over 9 October (`<scratch3>/lock-groups.txt`):

| class of empty | 9 October | first search | box search | box and surface bound |
| --- | --- | --- | --- | --- |
| zero distance (23) | 16.9 s | 23.5 s | 13.3 s | **13.7 s** |
| ≤ 10⁻⁶ mm (78) | 23.7 s | 27.0 s | 19.4 s | **20.3 s** |
| positive distance (624) | 89.6 s | 97.3 s | 87.7 s | **89.1 s** |

Commons 730, refused 0 in every run; the suite 14 passed in every run.

```
group                                    zero tiny  pos        9 Oct        first          box        bound   growth
lock_pin/wheel_1                            4    5   92      58.13 s      63.46 s      56.50 s      57.35 s     -0.78 s
cam/lock_pin                                4   51  104      30.48 s      33.80 s      30.15 s      30.90 s     +0.43 s
lock_pin/wheel_3                            4    5    4       6.71 s       6.91 s       5.70 s       5.96 s     -0.75 s
lock_pin/wheel_2                            4    5    3       6.24 s       6.62 s       5.41 s       5.58 s     -0.67 s
cam/dial                                    1    0    0       5.93 s      11.57 s       4.96 s       5.22 s     -0.72 s
peg_3/wheel_3                               1    3    0       4.60 s       4.50 s       1.93 s       2.02 s     -2.59 s
peg_1/wheel_1                               1    2    0       2.77 s       3.29 s       1.45 s       1.36 s     -1.41 s
peg_2/wheel_2                               1    2    0       2.69 s       3.34 s       1.51 s       1.50 s     -1.20 s
frame/wheel_1                               0    0   14       2.54 s       2.67 s       2.52 s       2.60 s     +0.05 s
frame/lock_pin                              0    0   93       1.24 s       1.42 s       1.20 s       1.23 s     -0.01 s
frame/wheel_3                               0    0   11       1.21 s       1.26 s       1.14 s       1.17 s     -0.04 s
frame/wheel_2                               0    0   11       1.18 s       1.26 s       1.14 s       1.23 s     +0.05 s
cam/frame                                   0    0   12       0.76 s       0.81 s       0.75 s       0.81 s     +0.05 s (sub-second growth)
frame_ring_1_2_2/wheel_3                    0    0   12       0.73 s       0.76 s       0.70 s       0.75 s     +0.02 s (sub-second growth)
frame_ring_1_2_1/wheel_2                    0    0   12       0.72 s       0.74 s       0.68 s       0.70 s     -0.02 s
frame/frame_ring_1_2_1                      1    0    2       0.46 s       0.63 s       0.50 s       0.44 s     -0.02 s
frame/frame_ring_3                          1    0    0       0.31 s       0.57 s       0.51 s       0.44 s     +0.13 s (sub-second growth)
frame_ring_1_2_2/frame_ring_3               1    0    0       0.20 s       0.32 s       0.32 s       0.32 s     +0.12 s (sub-second growth)
peg_2/peg_3                                 0    2    0       0.18 s       0.33 s       0.30 s       0.32 s     +0.14 s (sub-second growth)

groups grown by more than 5 s: none
```

(Groups under 0.5 s in every run and not grown by 0.1 s are left out of
the listing.) Against the second Revision's acceptance: each class of
empty costs less witness time than on 9 October (the positive class by
0.5 s, within the host's noise); no group grows by 5 s, the largest growth
being `cam`/`lock_pin`'s 0.43 s; five sub-second groups grow by
0.02–0.14 s, recorded. The lock passes.

#### 5.3 Wall clock 02, cold

As in 5.3 above, from the detached worktree at `ec2a05d` (`git status
--short` empty), `SOLID_BUILD_DIR=<scratch3>/clock-build`,
`MEASURE_OUT=<scratch3>/clock.jsonl` (log `<scratch3>/clock.log`). It ran
for 47 minutes, too long for one foreground call, so it was started in the
background and waited on by its PID (`tail --pid`); nothing else of ours
ran meanwhile. Other sessions raised the host's load average from 2 to
between 8 and 11 during the run.

```
start 2026-10-09T19:37:17+00:00 load average: 2.07, 2.01, 2.43
Running WallClock02Test.test_assembly_integrity........FAIL! at instant 0.0 (8 of 8 instants failed)
Running WallClock02Test.test_movement_runs_free_through_a_swing....FAIL! at instant 0.0 (48 of 48 instants failed)
Running WallClock02Test.test_solid_integrity.FAIL! at instant 0
Running WallClock02Test.test_source_body_inventory.FAIL! at instant 0
Running WallClock02Test.test_the_train_meshes_all_the_way_round....FAIL! at instant 0.0 (32 of 32 instants failed)
Running WallClock02Test.test_the_weight_screw_engages_its_separate_nut.FAIL! at instant 0
Ran 22 tests in 2822.83 seconds: 16 passed, 6 failed (verdict store off)
Elapsed (wall clock) time (h:mm:ss or m:ss): 47:06.95
Maximum resident set size (kbytes): 910236
exit=0 end 2026-10-09T20:24:24+00:00 load average: 10.84, 9.85, 9.13
```

The same six failures as the first search's run, the verdicts on
non-empty commons and on connectivity that 9 October's records hold; no
refusal. Afterwards `git -C <clock> status --short` was empty, `HEAD`
`ec2a05d`, and nothing in the worktree was newer than
`<scratch3>/clock-marker`.

| | 9 October | first search | box and surface bound |
| --- | --- | --- | --- |
| commons / empty / non-empty / refused | 643 / 637 / 6 / 0 | 643 / 637 / 6 / 0 | 643 / 637 / 6 / 0 |
| Boolean on all commons | 279.2 s | 308.2 s | 262.8 s |
| distance on all commons | 1,724.9 s | 1,776.5 s | 1,584.6 s |
| witness on all commons | 948.0 s | 1,167.2 s | **726.1 s** |
| witness on zero-distance empties (115) | 582.9 s | 810.3 s | **421.9 s** |
| witness on ≤ 10⁻⁶ mm empties (9) | 47.2 s | 9.6 s | **2.4 s** |
| witness on positive-distance empties (513) | 317.8 s | 347.2 s | **301.8 s** |
| wall | 3,108 s | 3,536 s | 2,824 s |

By pair group over every class (`<scratch3>/groups3.py`,
`<scratch3>/clock-groups.txt`; the box search was not run on the clock):

```
group                                    zero tiny  pos        9 Oct        first        bound   growth
screw/shell                                 1    0    0     297.84 s       1.26 s       0.48 s   -297.36 s
plates/wheel                                0    0  100     191.68 s     209.43 s     183.18 s     -8.51 s
arbor/hour_holder                          51    0    0     119.01 s     469.05 s     266.75 s   +147.74 s ** >5 s
wheel/wheel                                 0    0  214     108.45 s     119.76 s     103.77 s     -4.69 s
cannon_pinion/hour_holder                  42    0    0      57.18 s     244.18 s     134.45 s    +77.27 s ** >5 s
beat_screw/collet                           1    0    0      43.72 s       1.80 s       1.38 s    -42.35 s
nut/shell                                   0    1    0      41.15 s       0.62 s       0.22 s    -40.93 s
plates/standoffs                            1    0    0      15.04 s      31.04 s       8.90 s     -6.13 s
rating_button/shell                         0    0    1       8.72 s       7.11 s       6.42 s     -2.29 s
front_4/plates                              1    0    0       6.08 s       8.64 s       0.62 s     -5.46 s
ring/upper_ring_nut                         1    0    0       4.96 s       1.12 s       0.61 s     -4.35 s
front_3/plates                              1    0    0       4.86 s       6.21 s       0.57 s     -4.29 s
back_0/plates                               1    0    0       4.62 s       7.18 s       0.58 s     -4.04 s
collet/collet_screw                         1    0    0       4.24 s       0.40 s       0.21 s     -4.03 s
back_1/plates                               0    1    0       4.14 s       6.40 s       0.57 s     -3.57 s
back_3/plates                               1    0    0       4.13 s       6.41 s       0.57 s     -3.57 s
back_2/plates                               1    0    0       3.92 s       6.56 s       0.57 s     -3.35 s
front_2/plates                              1    0    0       3.87 s       6.28 s       0.59 s     -3.28 s
front_1/plates                              1    0    0       3.74 s       5.99 s       0.58 s     -3.16 s
front_0/plates                              1    0    0       3.49 s       7.19 s       0.57 s     -2.92 s
body/collet                                 1    0    0       3.13 s       2.52 s       2.24 s     -0.89 s
arbor/cannon_pinion                         0    0   40       2.75 s       3.11 s       2.52 s     -0.23 s
hook/plates                                 0    0   21       2.19 s       3.15 s       2.22 s     +0.03 s
ring/standoffs                              0    0   46       1.58 s       1.86 s       1.51 s     -0.08 s
cannon_pinion/minute_hand                   0    1    0       0.91 s       0.28 s       0.17 s     -0.73 s
beat_nut/collet                             1    0    0       0.75 s       0.77 s       0.23 s     -0.51 s
body/top_nyloc                              1    0    0       0.67 s       0.78 s       0.44 s     -0.23 s
cannon_pinion/hour_hand                     0    0   42       0.66 s       0.77 s       0.57 s     -0.09 s
hour_hand/hour_holder                       1    0    0       0.64 s       0.72 s       0.19 s     -0.45 s
plates/rod                                  0    0    5       0.56 s       0.74 s       0.51 s     -0.05 s
rating_button/rating_nyloc                  0    1    0       0.48 s       0.94 s       0.24 s     -0.24 s
lower_ring_nut/ring                         1    0    0       0.46 s       1.16 s       0.60 s     +0.14 s (sub-second growth)
nut/screw                                   0    1    0       0.20 s       0.40 s       0.37 s     +0.17 s (sub-second growth)
beat_nut/beat_screw                         1    0    0       0.14 s       0.33 s       0.31 s     +0.17 s (sub-second growth)
top_half_nut/top_nyloc                      0    1    0       0.11 s       0.24 s       0.22 s     +0.11 s (sub-second growth)
lid/lid_screw_left                          0    1    0       0.10 s       0.31 s       0.22 s     +0.12 s (sub-second growth)
lid/lid_screw_right                         0    1    0       0.09 s       0.27 s       0.21 s     +0.12 s (sub-second growth)

groups grown by more than 5 s: [('arbor/hour_holder', 119.01, 266.75), ('cannon_pinion/hour_holder', 57.18, 134.45)]
```

Per asking (`faces` as the records hold them), 9 October | first search |
box and surface bound:

| group | faces | askings | Boolean | distance | witness |
| --- | --- | --- | --- | --- | --- |
| `arbor`/`hour_holder` | 244, 218 | 51 | 0.39 / 0.43 / 0.37 s | 1.51 / 1.56 / 1.40 s | 2.33 / 9.20 / **5.23 s** |
| `cannon_pinion`/`hour_holder` | 83, 218 | 42 | 0.23 / 0.24 / 0.21 s | 0.70 / 0.69 / 0.64 s | 1.36 / 5.81 / **3.20 s** |

Against the second Revision's acceptance:

- Each class of empty costs less witness time than on 9 October: zero
  distance 582.9 s → 421.9 s, under a micrometre 47.2 s → 2.4 s, positive
  distance 317.8 s → 301.8 s. **Met.**
- The three pathological groups stay settled: `screw`/`shell` 297.84 s →
  0.48 s, `beat_screw`/`collet` 43.72 s → 1.38 s, `nut`/`shell` 41.15 s →
  0.22 s. **Met.**
- No group grows by more than 5 s: **not met.** `arbor`/`hour_holder`
  grows 147.74 s (119.01 s → 266.75 s, 2.24×) and
  `cannon_pinion`/`hour_holder` 77.27 s (57.18 s → 134.45 s, 2.35×). The
  Boolean's and the distance's time per asking on those two groups is at
  or below 9 October's, so the host's load does not account for the
  growth. Six sub-second groups grow by 0.11–0.17 s, recorded.

#### Diagnosis of the two hour-holder groups (scratch, after the stop)

The clock's `arbor`/`hour_holder` pair was captured with the 9 October
`capture.py` (`env -C <clock> PYTHONPATH=<bench>:<clock>
PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch3>/clock-build
MEASURE_OUT=<scratch3>/arbor MEASURE_PAIR=arbor,hour_holder python
<bench>/workflow/ongoing/distance-tier-measurement-2026-10-09/capture.py
test wall_clock_02 --brep --no-verdict-store`: `CAPTURED arbor,hour_holder
after 14 commons`, 20:25, load average 6.4 to 6.0; the worktree's status
empty, `HEAD` `ec2a05d` and nothing newer than `<scratch3>/capture-marker`
afterwards) and timed as in 3c above (load average 5.56 to 3.54):

```
arbor 244 faces; hour_holder 218 faces
round 0: change 4.623, bench 1.924, undecided 1.975
round 1: change 4.317, bench 1.954, undecided 1.978
round 2: change 4.426, bench 1.922, undecided 1.992
bench      calls {('classify', 244): 1872, ('classify', 218): 478}
change     calls {('classify', 218): 1872, ('side', 244): 565}
```

2.30× in process, as the suite measured; `cannon_pinion`/`hour_holder` is
2.55× (3c above). Where the arbor's readings go (`holder_probe.py` with the
arbor as the solid read; load average 3.26 to 2.91):

```
points read on the holder 536
total 2.71 s, 5.06 ms a reading; faces measured per reading: mean 1.5 median 1.0 max 3
sides Counter({'out': 466, 'on': 69, None: 1})
  face 5 Plane: 536 visits, 4.08 ms each, box span [27.72 27.72 39.2 ]
  face 134 Plane: 102 visits, 0.05 ms each
  face 183 Cylinder: 86 visits, 0.05 ms each
```

Both groups are the same case. The hour holder rides against the flat
side of the arbor's wheel, and the cannon pinion against the flat side of
the hour holder's gear: on each pair the contact is a plane bounded by
about two hundred edges (a tooth outline), the stencil's points lie
within 0.0007–0.13 mm of it, and it is the nearest face at most of them
(291 of 426 on the holder, 3c above). The plane bound passes over every
face that is not near (1.5 faces a reading, against 2.9 under the box
search), but no lower bound can pass over the face the point is nearest,
and one extrema from a point to that face costs 4.1 ms, against 0.9 ms for
the hour holder's classifier; the whole undecided search on the arbor
pair, 1,872 holder and 565 arbor classifications, takes 1.98 s. The
second Revision's bound has done what a bound can do on these pairs.

What else was measured, for the choice and not applied
(`<scratch3>/plane_probe.py`): projecting the point onto the plane and
classifying the projection in the face's parameter space
(`BRepTopAdaptor_FClass2d`, built once per face in about 5 ms) costs
0.85 ms a point on the hour holder's face 4 and 0.37 ms on the arbor's
face 5, against the extrema's 4.1 and 4.4 ms; the projection fell inside
the face at 291 of 426 and 356 of 536 points, each at the extrema's
distance to 10⁻⁹ mm, and the rest would still need the extrema. That is a
different route to the nearest point of a planar face, not the ratified
search, and even it costs about what the healthy classifier it replaces
costs.

### 5.4, 5.5

5.4 (OpenAstroMount) was not run: the apply stopped at 5.3. 5.5: the
Curta Type I was not run, as design.md's Open Question 1 records: the
project is not run in this cycle, and by the ball argument its two
recorded witnesses read inside or undecided in both solids, so the
classifiers are asked there as before; their re-run is owed.

### Stop point (second revision)

The second Revision's acceptance fails on one of its three bounds, so the
apply stops here with the tree as it is: the box and surface bound is in
`machinome/engine/brep.py` with its red-first test, green; 4.1 and 4.2
green; 5.1, 5.2 and the lock's 5.3 within the acceptance; the clock's
5.3 within it on every class and on the three pathological groups and
outside it on two groups. The records of tasks 6.1 to 6.5 are still the
first apply's drafts; 5.4 and 7 are not done; nothing is committed.

- The clock's zero-distance empties cost 421.9 s against 582.9 s on
  9 October and 810.3 s under the first search; its witness on all commons
  726.1 s against 948.0 s; every class falls.
- `arbor`/`hour_holder` +147.74 s (2.24×) and `cannon_pinion`/`hour_holder`
  +77.27 s (2.35×) over 9 October, each confirmed in process (2.30× and
  2.55×), each a point nearest a many-edged planar contact face whose one
  extrema costs four to five healthy classifications.
- Voron-2's twelve refusals and the synthetic ones do not move.

## 3d. After the acceptance ruling (design.md, "Acceptance ruling after the third apply")

A fourth applier completed the cycle from the tree as the third left it
(HEAD `9943fcda`, the planning commit amended with the acceptance ruling;
the earlier appliers' work uncommitted, kept). 3d.1: no change to the
search. `<scratch4>` is
`/tmp/claude-1000/-home-asa-devel-machinome/b6c584a7-7bce-4b09-8a25-3732645cbf62/scratchpad/applier4`;
the earlier scratch directories were read, never written.

### 5.4 OpenAstroMount, the changed bench

`<astro>` is `/home/asa/devel/machinome/projects/OpenAstroMount`, branch
`exact-engine-validation`, `58e46cd`, `git status --short` empty. The
script is the archived `astro_pair.py` as the first applier prepared it
(`<scratch>/astro_pair.py`, copied to `<scratch4>/astro_pair.py`: the
housing and the insert at the Target end state, azimuth 2, altitude 44,
right ascension 5, declination 5, `intersect_shapes` in both orders).
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
SOLID_BUILD_DIR=<scratch4>/astro-build /usr/bin/time python
<scratch4>/astro_pair.py` (load average 0.89 at the start, 1.02 at the
end; the build directory empty at the start; log `<scratch4>/astro.log`):

```
loaded in 27.4 s
housing, insert: returned 0 solids (55.6 s)
insert, housing: returned 0 solids (40.8 s)
wall 127.75 s, max rss 1033976 kB
```

The empty common is returned in both orders, as since 7 October (the
archived run: 37.5 s, housing first). The first order is slower than
then, so two in-process comparisons followed. `<scratch4>/astro_ab.py`
(the change and the change with every side undecided, interleaved, the
housing first; load average 0.73 to 1.12; log `<scratch4>/astro_ab.log`):

```
faces 110 84
change: witness None, 54.7 s, calls {('classify', 84): 1872, ('side', 110, 'out'): 912, ('side', 110, 'in'): 1, ('side', 84, 'out'): 1}
undecided: witness None, 58.2 s, calls {('classify', 84): 1873, ('classify', 110): 914}
change: witness None, 54.5 s, calls {('classify', 84): 1872, ('side', 110, 'out'): 912, ('side', 110, 'in'): 1, ('side', 84, 'out'): 1}
undecided: witness None, 59.4 s, calls {('classify', 84): 1873, ('classify', 110): 914}
```

`<scratch4>/astro_head.py` (HEAD's `machinome/engine/brep.py` saved as
`<scratch4>/brep_head.py` and imported as its own module, the script
asserting it is not the bench's and has no `_nearest_side`; each engine in
both orders, every classification and side reading timed by solid; load
average 0.73 to 1.14; log `<scratch4>/astro_head.log`):

```
housing 110 faces; insert 84 faces
bench housing first: witness None, 34.6 s
  calls {('classify', 110): 1873, ('classify', 84): 718}
  seconds {('classify', 110): 11.0, ('classify', 84): 18.9}
bench insert first: witness None, 41.6 s
  calls {('classify', 84): 1873, ('classify', 110): 926}
  seconds {('classify', 84): 33.8, ('classify', 110): 3.6}
change housing first: witness None, 54.1 s
  calls {('classify', 84): 1872, ('side', 110): 913, ('side', 84): 1}
  seconds {('classify', 84): 47.8, ('side', 110): 1.7, ('side', 84): 0.0}
change insert first: witness None, 39.7 s
  calls {('classify', 84): 1872, ('side', 110): 926, ('side', 84): 1}
  seconds {('classify', 84): 33.5, ('side', 110): 2.1, ('side', 84): 0.0}
```

On this pair the slower classifier is the insert's, the operand with
fewer faces (84 against the housing's 110): 18–26 ms a point against the
housing's 4–6 ms. Decision 1 now asks it at every stencil point, so with
the housing given first the witness goes from 34.6 s to 54.1 s (1.56×),
all of it the insert's classifier (47.8 s for 1,872 points, where the
unmodified engine asked it at the 718 points inside the housing); with the
insert given first it is unchanged (41.6 s to 39.7 s). The side readings
cost 1.7–2.1 s and spare every housing classification. This is the case
design.md's Risks and Open Question 2 name, "a slow classifier on the
operand with fewer faces", measured on a real pair for the first time: not
helped, and in one order made slower. No refusal moves: the common is
empty and returned under both engines in both orders.

After each of the three runs `git -C <astro> status --short` printed
nothing, `HEAD` was `58e46cd`, and `find <astro> -newer
<scratch4>/astro-marker{,2,3} -not -path '*/.git*'` printed nothing.

### 5.5 The Curta

Confirmed as recorded under 3c: the Curta Type I was not run in this
cycle (design.md, Open Question 1); its two ±0.2 mm refusals are owed a
re-run under this change, recorded in `workflow/warts.md` (6.5 below).

### 6 Records

The first applier's drafts, revised to the final search and numbers:

- 6.1 `docs/adrs/TEST-FRAMEWORK/ADR-142-a-shared-interior-witness-refuses-an-empty-exact-common.md`,
  "Amendment — 2026-10-09: A Point's Side Is Read From Its Nearest
  Boundary Before a Slower Classifier": the shell and screw; the order;
  the face-by-face search in ascending lower bound (box, plane or
  cylinder less the face's largest tolerance), one extrema per face
  visited, the stop rule, the support's reading; the soundness argument of
  design.md Decision 2; that a side reading never makes a point count;
  both projects by class of empty and the three settled groups; the two
  gear-side groups as the instrument's known cost with the ruling's
  reason, and OpenAstroMount's slow classifier on the operand with fewer
  faces (5.4); the two searches not kept; the synthetic refusals and
  Voron-2's twelve; the Curta's re-run owed; a link to
  `openspec/changes/archive/2026-10-09-witness-on-a-touching-pair/`.
  `docs/adrs/README.md`: ADR-142's line reads "amended 2026-09-23,
  2026-10-07, 2026-10-09 (no classifier verdict on an inside-out operand)
  and 2026-10-09 (a point's side is read from its nearest boundary before
  a slower classifier)".
- 6.2 `docs/architecture.md`, the B-rep guard paragraph: one sentence on
  the order and the face-by-face search.
- 6.3 `docs/reference/assertions.rst`: the draft's one clause, "and its
  nearest boundary point in neither shape shows it outside that shape",
  kept unchanged.
- 6.4 `docs/project/changelog.rst`, the first bullet under `Unreleased`:
  the shell and screw 324 s → half a second; the clock's suite 948 s →
  726 s and the lock's 130 s → 123 s of witness (the lock's all-commons
  total summed from `<scratch3>/lock.jsonl`: 730 records, 123.1 s; the
  clock's 643, 726.1 s); refusals unchanged; a flat many-edged contact up
  to about 2.3×.
- 6.5 `workflow/warts.md`: the "A touching pair can exhaust the witness"
  bullet's **Fixed** note with both projects' classes, the three settled
  groups, the known cost (the two gear-side groups and OpenAstroMount),
  the three searches and why each was revised, and the Curta's owed
  re-run; the shallow-dent finding's *Deeper than recorded* note (the
  3.75 mm ball sunk 0.5 and 1.0 mm, M4) kept from the draft.

Every task box of sections 1 to 6 and 7.1–7.2 ticked in `tasks.md`
before the archive; 7.4 ticked after it, and 7.3 left unticked (below).

### 7.1, 7.2 Sync and archive

`openspec --version` 1.6.0. `env -C <bench> openspec validate
witness-on-a-touching-pair --strict`: `Change 'witness-on-a-touching-pair'
is valid`. Then `env -C <bench> openspec archive witness-on-a-touching-pair
--yes` (load average 0.11; log `<scratch4>/archive.log`):

```
Task status: 31/33 tasks
Warning: 2 incomplete task(s) found. Continuing due to --yes flag.

Specs to update:
  brep-engine: update
  test-framework: update
Applying changes to openspec/specs/brep-engine/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/test-framework/spec.md:
  ~ 1 modified
Totals: + 0, ~ 2, - 0, → 0
Specs updated successfully.
Change 'witness-on-a-touching-pair' archived as '2026-10-09-witness-on-a-touching-pair'.
```

The two incomplete tasks are 7.3 and 7.4. `git diff --stat --
openspec/specs`: `brep-engine/spec.md` 30 insertions and 1 deletion (the
requirement's second paragraph, the undecided-side sentence and two
scenarios), `test-framework/spec.md` 5 insertions and 1 deletion (the
nearest-boundary clause and the wall clock 02 scenario). `env -C <bench>
openspec validate --all` (log `<scratch4>/validate.log`): `Totals: 45
passed, 0 failed (45 items)`, exit 0. The change now lives at
`openspec/changes/archive/2026-10-09-witness-on-a-touching-pair/`;
`openspec/changes/` holds only `archive/`.

### 7.3 Focused tests, then the full suite

The focused tests of 4.1 (load average 0.24 at the start, 0.36 at the
end; log `<scratch4>/focused.log`):

```
147 passed, 93 subtests passed in 8.76s   (wall 9.90 s)
```

The full suite, once, alone (`ps` showed no pytest, `machinome test` or
`measure.py` of ours before it): `env -C <bench> PYTHONPATH=<bench>
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider` at the
bench root, waited on by its PID (log `<scratch4>/full.log`):

```
start 2026-10-09T20:44:08+00:00 load average: 0.38, 0.82, 3.21
FAILED tests/test_machinome_identity.py::MachinomeIdentityTest::test_distribution_import_command_and_extras_share_the_name
FAILED tests/test_missing_source_file.py::UndeclaredSourceTest::test_a_declaration_given_alone_is_resolved_beside_its_module
2 failed, 4766 passed, 4 skipped, 55 warnings, 6731 subtests passed in 717.15s (0:11:57)
exit 1 wall 720 s
end 2026-10-09T20:56:08+00:00 load average: 2.20, 1.60, 2.42
```

Neither failure touches a file of this change, and neither was fixed:

- `test_distribution_import_command_and_extras_share_the_name`:
  `AssertionError: Lists differ: ['machinome-viewer>=0.8.0'] !=
  ['machinome-viewer']`. `pyproject.toml`'s `viewer` extra has carried
  the floor since `dbd52c24` ("The viewer and web-snapshot extras floor at
  the matching viewer"), an ancestor of the base `d9fd98d3`, and neither
  `pyproject.toml` nor `tests/test_machinome_identity.py` differs from the
  base (`git diff --stat d9fd98d3 -- …` prints nothing). It fails alone as
  well (below): a disagreement on the base between that test and the
  extra.
- `test_a_declaration_given_alone_is_resolved_beside_its_module`:
  `MissingSourceFile: Bracket declares stl_source = 'bracket.stl', … but
  …/tests/stl_project/bracket.stl does not exist`. The STL fixtures of
  `tests/stl_project/` are ignored (`.gitignore:127:
  tests/stl_project/*.stl`) and absent from this fresh worktree; another
  test wrote them during the run (`bracket.stl`, `pack.stl` and the rest
  stamped 20:54), after this test had run. An order dependence on
  generated fixtures, not this change.

The two run alone afterwards (load average 1.45):

```
FAILED tests/test_machinome_identity.py::MachinomeIdentityTest::test_distribution_import_command_and_extras_share_the_name
1 failed, 1 passed in 2.90s
```

Per the brief, the failures are recorded and the apply stops here; 7.3 is
left unticked for the orchestrator's ruling.

### The manual

6.3 touched a page, so the manual was built strictly once: `env -C
<bench> PYTHONDONTWRITEBYTECODE=1 python -m sphinx -n -W --keep-going -q
-b html docs <scratch4>/docs-build` (load average 1.37 at the start,
1.34 at the end; log `<scratch4>/sphinx.log`): exit 0, wall 6 s, no
output, no warning.

### 7.4 State left

Nothing committed, amended, pushed or branched. Bench HEAD `9943fcda`.
`git status --short`: modified `docs/adrs/README.md`, ADR-142,
`docs/architecture.md`, `docs/project/changelog.rst`,
`docs/reference/assertions.rst`, `machinome/engine/brep.py`,
`openspec/specs/brep-engine/spec.md`,
`openspec/specs/test-framework/spec.md`,
`tests/test_resolved_brep_witness.py`,
`tests/test_witness_neighbourhood.py`, `workflow/warts.md`; the change's
files under `openspec/changes/witness-on-a-touching-pair/` deleted by the
archive; untracked `openspec/changes/archive/2026-10-09-witness-on-a-touching-pair/`
and `tests/test_witness_touching_pair.py`.
