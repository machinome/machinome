# Evidence — `a-witness-is-interior-in-its-neighbourhood`

Cycle 18 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`2e1b16145c6a4e06a6eb01d5bb6af8321ed2f34c` (`git -C <bench> rev-parse
HEAD`). Every framework command below ran as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool>`
(Python 3.12.3, CadQuery 2.7.0); `<scratch>` is the campaign scratchpad's
`cycle18/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle18`).
`<astro>` is `/home/asa/devel/machinome/projects/OpenAstroMount`, branch
`exact-engine-validation`, `58e46cd548126ce4a5be5b33c8a0a11670c8cad4`;
`<curta>` is `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x`,
`main`, `1f3dc221d43cdb2091a1385c38384e52621d5bb7`. Both are read only: every
run in them had `PYTHONDONTWRITEBYTECODE=1` and a `SOLID_BUILD_DIR` under
`<scratch>`. One test run or project run of ours at a time, checked with
`ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome
snapshot\|[m]achinome build'` before each; Voron-2 was not run.

## 1. Baseline on the unmodified tree (2e1b161)

### 1.1 Interpreter and project states

```
$ python -c 'import machinome, OCP, cadquery; print(machinome.__file__, cadquery.__version__)'
/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py 2.7.0

$ git -C <astro> rev-parse --abbrev-ref HEAD; git -C <astro> rev-parse HEAD; git -C <astro> status --short
exact-engine-validation
58e46cd548126ce4a5be5b33c8a0a11670c8cad4
(nothing)

$ git -C <curta> rev-parse HEAD; git -C <curta> status --short
1f3dc221d43cdb2091a1385c38384e52621d5bb7
?? "3D Printed Curta Calculator Assembly_720p.mp4"
?? CREDITS
?? curta-2x-files/
?? screenshots/reverser_inspection.png
```

The Curta's four untracked entries predate this cycle. `<astro>/_build`
carries the stamp `2026-10-03 08:48:40` and `<astro>/_build.lock`
`2026-09-12 00:25`. Before the first run, an empty marker file
`<scratch>/stageA-marker` was touched, so a later `find <project>
-newer <scratch>/stageA-marker` lists whatever a run wrote into a project.

The scratchpad is not durable, so the three Stage P scripts the cycle runs
are copied here.

`<scratch>/neighbourhood_patch.py`, the design in scratch form (a pytest
plugin and a module the two measurement scripts import):

```python
"""Scratch pytest plugin, not a framework change: replace
`machinome.engine.brep._resolved_interior` and `_false_empty_witness` with
the shape this cycle proposes, so the planning stage can show the red test
turn green and the refusal fixtures stay refused before anything is
implemented on the bench.

Load with `-p neighbourhood_patch` and the scratch directory on PYTHONPATH.
"""

import math
from itertools import product

from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN, TopAbs_UNKNOWN

from machinome.engine import brep

STATS = {'resolved': 0, 'rejected': 0, 'accepted': 0, 'margins': []}


def _resolved_interior(solid, point):
    faces = brep._faces(solid)
    if not faces:
        raise RuntimeError('classified solid has no boundary faces')
    vertex = BRepBuilderAPI_MakeVertex(
        gp_Pnt(point.X(), point.Y(), point.Z())).Vertex()
    margin = math.inf
    for face in faces:
        tolerance = brep.BRep_Tool.Tolerance_s(face)
        distance = brep._distance(face, vertex)
        if not (math.isfinite(tolerance) and tolerance >= 0 and
                math.isfinite(distance) and distance >= 0):
            raise RuntimeError('invalid native face tolerance or distance')
        if distance <= tolerance:
            return None
        margin = min(margin, distance)
    return margin


def _false_empty_witness(first, second):
    solids1, solids2 = brep._solids(first), brep._solids(second)
    if not solids1 or not solids2:
        return None
    left, right = brep._copy(first), brep._copy(second)
    section = brep.BRepAlgoAPI_Section(left, right, False)
    section.Build()
    if not section.IsDone():
        raise RuntimeError('OCCT section reported not-done')
    crossing = section.Shape()
    if crossing.IsNull():
        raise ValueError('Null TopoDS_Shape object')
    edges = brep._edges(crossing)
    if not edges:
        return None
    spans = []
    for shape in (first, second):
        low, high = brep.bounds(shape)
        spans.extend(span for span in (high[0] - low[0], high[1] - low[1],
                                       high[2] - low[2])
                     if span > 0 and math.isfinite(span))
    if not spans:
        return None
    scale = min(spans)
    steps = (scale * 1e-4, scale * 1e-3, scale * 1e-2)
    directions = [tuple(value / math.sqrt(sum(one * one for one in direction))
                        for value in direction)
                  for direction in product((-1, 0, 1), repeat=3)
                  if any(direction)]
    classifiers1 = [brep.BRepClass3d_SolidClassifier(solid)
                    for solid in solids1]
    classifiers2 = [brep.BRepClass3d_SolidClassifier(solid)
                    for solid in solids2]

    def classified_in(classifier, point):
        classifier.Perform(point, 0.0)
        if classifier.Rejected():
            return False
        state = classifier.State()
        if state == TopAbs_UNKNOWN:
            raise RuntimeError('OCCT solid classifier returned UNKNOWN')
        return state == TopAbs_IN

    def resolved(classifiers, solids, point):
        found = []
        for classifier, solid in zip(classifiers, solids):
            if classified_in(classifier, point):
                found.append((classifier, solid))
        return found

    def neighbours(coords, distance):
        for axis in range(3):
            for sign in (1, -1):
                probe = list(coords)
                probe[axis] += sign * distance
                yield gp_Pnt(*probe)

    for edge in edges[:8]:
        if brep._length(edge) <= 0:
            continue
        for fraction in (.25, .5, .75):
            at = brep._position_at(edge, fraction)
            for step in steps:
                for direction in directions:
                    coords = tuple(at[i] + step * direction[i]
                                   for i in range(3))
                    point = gp_Pnt(*coords)
                    inside1 = resolved(classifiers1, solids1, point)
                    if not inside1:
                        continue
                    inside2 = resolved(classifiers2, solids2, point)
                    if not inside2:
                        continue
                    margins1 = [(c, s, brep._resolved_interior(s, point))
                                for c, s in inside1]
                    margins2 = [(c, s, brep._resolved_interior(s, point))
                                for c, s in inside2]
                    margins1 = [m for m in margins1 if m[2] is not None]
                    margins2 = [m for m in margins2 if m[2] is not None]
                    if not margins1 or not margins2:
                        continue
                    STATS['resolved'] += 1
                    for c1, _s1, m1 in margins1:
                        for c2, _s2, m2 in margins2:
                            half = min(m1, m2) / 2
                            if all(classified_in(c1, probe) and
                                   classified_in(c2, probe)
                                   for probe in neighbours(coords, half)):
                                STATS['accepted'] += 1
                                STATS['margins'].append((m1, m2))
                                return coords
                    STATS['rejected'] += 1
    return None


def pytest_configure(config):
    brep._resolved_interior = _resolved_interior
    brep._false_empty_witness = _false_empty_witness


def pytest_unconfigure(config):
    print(f'\n[neighbourhood_patch] {STATS}')
```

`<scratch>/astro_pair.py`, OpenAstroMount's refused pair at the Target end
state under the bench guard and under the patch:

```python
"""OpenAstroMount's refused pair at the Target end state (azimuth 2,
altitude 44, RA 5, DEC 5) under the bench guard and the proposed
neighbourhood check, timed. Scratch measurement; reads the project, writes
nothing into it (run with PYTHONDONTWRITEBYTECODE=1 and a scratch
SOLID_BUILD_DIR)."""

import sys
import time
from unittest.mock import patch

sys.dont_write_bytecode = True
PROJECT = '/home/asa/devel/machinome/projects/OpenAstroMount'
sys.path.insert(0, PROJECT)
sys.path.insert(0, sys.argv[1])

import neighbourhood_patch as proposed  # noqa: E402
from machinome.engine import BrepCommonInconsistency  # noqa: E402
from machinome.engine import brep  # noqa: E402
from machinome.test import _compose_world_matrix  # noqa: E402
from simulation.mount import OpenAstroMount  # noqa: E402

started = time.perf_counter()
mount = OpenAstroMount()
mount.set_state(azimuth=2, altitude=44, right_ascension=5, declination=5)
mount.assemble()
housing = mount.head.frame.mancal_f206_valor_predeterminado_1.housing
insert = mount.head.right_ascension_axis.rolamento_uc206_valor_predeterminado_1
operands = [brep.placed_shape(node.shape(), _compose_world_matrix(node))
            for node in (housing, insert)]
print(f'loaded in {time.perf_counter() - started:.1f} s', flush=True)

for label, witness, resolved in (
        ('bench', brep._false_empty_witness, brep._resolved_interior),
        ('proposed', proposed._false_empty_witness,
         proposed._resolved_interior)):
    with patch('machinome.engine.brep._false_empty_witness', witness), \
         patch('machinome.engine.brep._resolved_interior', resolved):
        started = time.perf_counter()
        try:
            common = brep.intersect_shapes(*operands, 'housing', 'insert')
            verdict = f'returned {brep.solid_count(common)} solids'
        except BrepCommonInconsistency as error:
            verdict = 'refused: ' + str(error).split('solids: ')[1]
        print(f'{label}: {verdict} ({time.perf_counter() - started:.1f} s)',
              flush=True)
print(f'proposed stats {proposed.STATS}', flush=True)
```

`<scratch>/curta_measure.py`, ADR-142's originating Curta pair under the
bench guard and under the patch, with the two hand-measured witnesses of 23
September re-read:

```python
"""ADR-142's originating Curta Type I pair under the bench guard and under
the proposed neighbourhood check. Scratch measurement, project read-only.

Pair: the positioning ball and the upper frame's main body, the ball copy
translated by (2.213142830078919, 0, +/-0.2) as in the archived evidence of
refuse-false-empty-exact-common. Also re-reads the two hand-measured
witnesses recorded there: their face margins and the classifier at the six
axis points at half the smaller margin.
"""

import logging
import sys
import time
from unittest.mock import patch

import cadquery as cq
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN

sys.path.insert(0, sys.argv[1])
import neighbourhood_patch as proposed  # noqa: E402

from machinome.engine import BrepCommonInconsistency  # noqa: E402
from machinome.engine import brep as engine  # noqa: E402
from machinome.simulation import Sim  # noqa: E402
from simulation.mechanistic import MechanisticCurta  # noqa: E402
from simulation.tools.interference import world_solids  # noqa: E402
from simulation.tools.positioning_ball_contact import BALL, FRAME  # noqa: E402

logging.disable(logging.INFO)
WITNESSES = {-1: (11.93431004745964, .4477315369512816, 26.088069310162098),
             1: (11.541571853564232, 3.0652117978127276, 32.321879856111245)}


def state(solid, coords):
    classifier = BRepClass3d_SolidClassifier(solid)
    classifier.Perform(gp_Pnt(*coords), 0.0)
    if classifier.Rejected():
        return 'OUT(rejected)'
    return {TopAbs_IN: 'IN'}.get(classifier.State(), str(classifier.State()))


def attempt(label, witness, resolved, ball, frame):
    started = time.perf_counter()
    with patch('machinome.engine.brep._false_empty_witness', witness), \
         patch('machinome.engine.brep._resolved_interior', resolved):
        try:
            common = engine.intersect_shapes(ball, frame, 'ball', 'frame')
            verdict = f'returned {engine.solid_count(common)} solids'
        except BrepCommonInconsistency as error:
            verdict = 'refused at ' + str(error).split('solids: ')[1].split(
                '. No')[0]
    print(f'  {label}: {verdict} ({time.perf_counter() - started:.2f} s)',
          flush=True)


started = time.perf_counter()
sim = Sim(MechanisticCurta(), dt=.1)
sim.node.assemble()
native = world_solids(sim.node, selected={BALL, FRAME})
print(f'loaded in {time.perf_counter() - started:.1f} s', flush=True)
frame = native[FRAME].wrapped
for sign in (-1, 1):
    moved = native[BALL].translate((2.213142830078919, 0, sign * .2))
    ball = moved.wrapped
    print(f'z {sign * .2:+.1f}: native common solids '
          f'{len(moved.intersect(native[FRAME]).Solids())}', flush=True)
    attempt('bench', engine._false_empty_witness, engine._resolved_interior,
            ball, frame)
    proposed.STATS['margins'].clear()
    attempt('proposed', proposed._false_empty_witness,
            proposed._resolved_interior, ball, frame)
    print(f'  proposed accepted margins {proposed.STATS["margins"]} '
          f'stats resolved {proposed.STATS["resolved"]} rejected '
          f'{proposed.STATS["rejected"]}', flush=True)
    coords = WITNESSES[sign]
    margins = [proposed._resolved_interior(engine._solids(shape)[0],
                                           gp_Pnt(*coords))
               for shape in (ball, frame)]
    print(f'  hand witness {coords}: states '
          f'{[state(engine._solids(s)[0], coords) for s in (ball, frame)]} '
          f'margins {margins}', flush=True)
    if None not in margins:
        half = min(margins) / 2
        for axis in range(3):
            for step in (half, -half):
                probe = list(coords)
                probe[axis] += step
                print(f'    neighbour axis {axis} {step:+.3g}: '
                      f'{[state(engine._solids(s)[0], probe) for s in (ball, frame)]}',
                      flush=True)
```

### 1.2 The guard's tests, unmodified tree

`pytest -q -p no:cacheprovider tests/test_brep_common_guard.py
tests/test_resolved_brep_witness.py tests/test_engine_package.py`:

```
23 passed, 61 subtests passed in 3.48s   (wall 4.64 s)
```

### 1.3 OpenAstroMount, unmodified tree

`env -C <astro> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
SOLID_BUILD_DIR=<scratch>/astro-build /usr/bin/time -v
/home/asa/devel/machinome/.venv/bin/machinome test --brep --no-verdict-store
simulation/mount.py` (log `<scratch>/astro-before.log`):

```
start 2026-10-07T07:52:30+00:00  load average: 0.25, 0.60, 0.77
Running OpenAstroMountTest.test_control_surface_names_the_four_physical_axes. passed
Running OpenAstroMountTest.test_declination_turns_the_payload_not_its_bearing_carrier. passed
Running OpenAstroMountTest.test_demo_names_five_builder_facing_poses. passed
Running OpenAstroMountTest.test_polar_adjustment_moves_the_head_about_measured_axes_only. passed
Running OpenAstroMountTest.test_released_pose_matches_exact_source_overlap_inventory. passed
Running OpenAstroMountTest.test_right_ascension_turns_its_carried_structure_not_the_frame. passed
Running OpenAstroMountTest.test_source_pose_is_the_control_default. passed
Running OpenAstroMountScenarioTest.test_every_instruction_reaches_its_documented_end_state ...
machinome.engine.BrepCommonInconsistency: B-rep common of housing and rolamento_uc206_valor_predeterminado_1 was empty despite a point strictly inside both native solids: (-2.0242287706088176, 265.5583117280026, 442.97547336608244). No overlap volume was inferred.
Running OpenAstroMountScenarioTest.test_present_instruction_reaches_a_distinct_observing_pose ... passed
Ran 9 tests in 575.30 seconds: 8 passed, 1 failed (verdict store off)
Elapsed (wall clock) time: 9:38.71   Maximum resident set size: 1222312 kB
exit=1
end 2026-10-07T08:02:09+00:00  load average: 1.43, 1.32, 1.09
```

8 passed, 1 failed, the failure and its witness to the last digit as on 3
and 7 October. Afterwards `git -C <astro> status --short` printed nothing,
`HEAD` was `58e46cd`, `find <astro> -newer <scratch>/stageA-marker -not
-path '*/.git*'` printed nothing, and `_build` and `_build.lock` kept their
stamps.

### 1.4 The pair alone, unmodified tree

`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
SOLID_BUILD_DIR=<scratch>/astro-build /usr/bin/time
.venv/bin/python <scratch>/astro_pair.py <scratch>` (load average 1.21 at
the start, 1.12 at the end; the shapes came from the build directory the
run of 1.3 had filled):

```
loaded in 1.6 s
bench: refused: (-2.0242287706088176, 265.5583117280026, 442.97547336608244). No overlap volume was inferred. (28.5 s)
proposed: returned 0 solids (37.2 s)
proposed stats {'resolved': 1, 'rejected': 1, 'accepted': 0, 'margins': []}
wall 70.62 s, max rss 789664 kB
```

As in Stage P (27.6 s and 36.9 s): one resolved candidate, rejected by its
neighbours.

### 1.5 The Curta pair, unmodified tree

`env -C <curta> PYTHONPATH=<bench>:<curta> PYTHONDONTWRITEBYTECODE=1
SOLID_BUILD_DIR=<scratch>/curta-build /usr/bin/time
.venv/bin/python <scratch>/curta_measure.py <scratch>` (load average 1.03 at
the start, 1.02 at the end; the `stats resolved` count is cumulative over the
two poses):

```
loaded in 6.0 s
z -0.2: native common solids 0
  bench: refused at (11.891042595905658, 1.106601773115647, 26.217514791126693) (0.35 s)
  proposed: refused at (11.891042595905658, 1.106601773115647, 26.217514791126693) (0.37 s)
  proposed accepted margins [(0.000163776590032148, 0.0005772348360788288)] stats resolved 1 rejected 0
  hand witness (11.93431004745964, 0.4477315369512816, 26.088069310162098): states ['IN', 'IN'] margins [0.010000113260256849, 0.00029428320044078837]
    neighbour axis 0 +0.000147: ['IN', 'IN']
    neighbour axis 0 -0.000147: ['IN', 'IN']
    neighbour axis 1 +0.000147: ['IN', 'IN']
    neighbour axis 1 -0.000147: ['IN', 'IN']
    neighbour axis 2 +0.000147: ['IN', 'IN']
    neighbour axis 2 -0.000147: ['IN', 'IN']
z +0.2: native common solids 0
  bench: refused at (11.749660151572499, 2.137450584281421, 33.27912367737267) (0.32 s)
  proposed: refused at (11.749660151572499, 2.137450584281421, 33.27912367737267) (0.32 s)
  proposed accepted margins [(0.0005945586249650472, 0.00050408508775406)] stats resolved 2 rejected 0
  hand witness (11.541571853564232, 3.0652117978127276, 32.321879856111245): states ['IN', 'IN'] margins [0.010005803566569304, 0.0013332730964030494]
    neighbour axis 0 +0.000667: ['IN', 'IN']
    neighbour axis 0 -0.000667: ['IN', 'IN']
    neighbour axis 1 +0.000667: ['IN', 'IN']
    neighbour axis 1 -0.000667: ['IN', 'IN']
    neighbour axis 2 +0.000667: ['IN', 'IN']
    neighbour axis 2 -0.000667: ['IN', 'IN']
wall 31.14 s, max rss 634256 kB
```

Both pairs refused by the bench and by the patch at the same witnesses, as
in design.md's Context table. Afterwards `git -C <curta> status --short`
printed the same four untracked entries and `find <curta> -newer
<scratch>/stageA-marker -not -path '*/.git*'` printed nothing.

## 2. Red tests

`tests/test_witness_neighbourhood.py` (new), four tests:

- `LoneInsideReadingTest.test_a_lone_inside_reading_is_not_a_witness`: unit
  boxes at the origin and at (0, 1, 0) touch along y = 1; `_boolean` is
  patched to return an empty compound; the second box's classifier answers
  IN at exactly one point, the first it is asked about strictly below the
  contact (0.9 < y < 1 − 10⁻⁶), and natively everywhere else. Expects the
  empty common and one lie.
- `ResolvedMarginTest.test_resolved_interior_reports_the_smallest_face_distance`:
  in the unit box, `(.5, .5, .5)` gives 0.5 and `(.9, .5, .5)` gives 0.1
  (to 10⁻¹²); `(1 − 10⁻¹⁵, .5, .5)` gives `None`.
- `UndecidedNeighbourTest.test_an_undecided_neighbour_refuses_verification`:
  boxes at the origin and at (.5, .5, .5), `_boolean` patched empty, every
  classifier answers natively until the second box's has once answered IN
  and UNKNOWN after that. Expects `BrepCommonVerificationError` matching
  `first.*second.*UNKNOWN`.
- `SharedInteriorStillRefusedTest.test_a_slab_of_shared_interior_is_still_refused`
  (the Voron-2 shape, real material of both operands around the witness):
  boxes at the origin and at (0, .6, 0) share a 0.4 mm slab; `_boolean`
  patched empty. Expects `BrepCommonInconsistency` whose witness lies inside
  the slab (0 < x < 1, 0.6 < y < 1, 0 < z < 1).

On the unmodified engine, `pytest -q -p no:cacheprovider
tests/test_witness_neighbourhood.py`:

```
E           machinome.engine.BrepCommonInconsistency: B-rep common of first and second was empty despite a point strictly inside both native solids: (5.7735026918962585e-05, 0.999942264973081, 0.24994226497308103). No overlap volume was inferred.
E       AssertionError: True != 0.5 within 1e-12 delta (0.5 difference)
tests/test_witness_neighbourhood.py:83: AssertionError
E           machinome.engine.BrepCommonInconsistency: B-rep common of first and second was empty despite a point strictly inside both native solids: (0.999942264973081, 0.500057735026919, 0.624942264973081). No overlap volume was inferred.
FAILED tests/test_witness_neighbourhood.py::LoneInsideReadingTest::test_a_lone_inside_reading_is_not_a_witness
FAILED tests/test_witness_neighbourhood.py::ResolvedMarginTest::test_resolved_interior_reports_the_smallest_face_distance
FAILED tests/test_witness_neighbourhood.py::UndecidedNeighbourTest::test_an_undecided_neighbour_refuses_verification
3 failed, 1 passed in 2.01s
```

Each red for its stated reason: the lone reading refused at the witness
design.md names, the margin read as `True`, and the undecided neighbour
never asked (the bench returns the first resolved candidate as a witness).
The slab is green, as a preservation test should be.

## 3. The change

`machinome/engine/brep.py` only:

- `_resolved_interior(solid, point)` keeps its loop over the solid's faces
  and its refusals of an invalid tolerance or distance, keeps the running
  minimum of the distances, returns `None` where it returned `False` and that
  minimum, the margin, where it returned `True`. Its docstring says so.
- `_false_empty_witness`: one local `classified_in(classifier, point)` holds
  the zero-tolerance reading the search already made (Rejected is OUT,
  UNKNOWN raises); `inside` returns the `(classifier, solid)` pairs that read
  IN; `resolved` keeps each IN solid's classifier with its margin and drops
  the unresolved; `corroborated` classifies the six points at half the given
  margin along ±x, ±y and ±z with both classifiers. A point IN both operands
  is returned only if some resolved pair's six neighbours, at half the
  smaller of its two margins, are IN both; otherwise the search goes on.
  The margins of the first operand's solids are measured before the
  second's and only when both operands read IN, so face distances stay as
  rare as before.
- The docstrings of `_false_empty_witness` and `intersect_shapes` name the
  neighbourhood.

The stencil, its budget and order, the messages and the errors are
unchanged.

## 4. Green

`pytest -q -p no:cacheprovider tests/test_witness_neighbourhood.py
tests/test_brep_common_guard.py tests/test_resolved_brep_witness.py
tests/test_engine_package.py tests/test_verdict_store.py`:

```
73 passed, 72 subtests passed in 6.38s   (wall 7.45 s)
```

The new file alone, `-rA`: all four PASSED (1.86 s).
`git -C <bench> status --short tests/test_brep_common_guard.py
tests/test_resolved_brep_witness.py` prints nothing: both guard files are
unedited.

Lint, on `machinome/engine/brep.py` and `tests/test_witness_neighbourhood.py`
(the pyenv `flake8` and `black` shims, black 26.5.1):

- `flake8 --max-line-length=89`: nothing, exit 0. HEAD's `brep.py` through
  the same configuration (`git show HEAD:machinome/engine/brep.py | flake8
  --max-line-length=89 --stdin-display-name machinome/engine/brep.py -`, run
  in the bench): nothing, exit 0.
- `black --check`: "2 files would be reformatted", as HEAD's `brep.py`
  already would be; the file is not in black's style (single quotes, lines
  wrapped at 79). `black --diff`: `brep.py` 13 hunks at HEAD and 14 after;
  the new test file 3 hunks, of the kinds black gives the existing
  `tests/test_resolved_brep_witness.py` (quote normalization, rejoined
  wrapped lines, `.9` as `0.9`, parenthesized context managers); the added
  code follows its files' own style.

## 5. Project validation

### 5.1 OpenAstroMount, changed tree

The command of 1.3, unchanged (log `<scratch>/astro-after.log`):

```
start 2026-10-07T08:05:32+00:00  load average: 0.47, 0.96, 0.99
Running OpenAstroMountTest.test_control_surface_names_the_four_physical_axes. passed
Running OpenAstroMountTest.test_declination_turns_the_payload_not_its_bearing_carrier. passed
Running OpenAstroMountTest.test_demo_names_five_builder_facing_poses. passed
Running OpenAstroMountTest.test_polar_adjustment_moves_the_head_about_measured_axes_only. passed
Running OpenAstroMountTest.test_released_pose_matches_exact_source_overlap_inventory. passed
Running OpenAstroMountTest.test_right_ascension_turns_its_carried_structure_not_the_frame. passed
Running OpenAstroMountTest.test_source_pose_is_the_control_default. passed
Running OpenAstroMountScenarioTest.test_every_instruction_reaches_its_documented_end_state ... passed
Running OpenAstroMountScenarioTest.test_present_instruction_reaches_a_distinct_observing_pose ... passed
Ran 9 tests in 1273.74 seconds: 9 passed, 0 failed (verdict store off)
Elapsed (wall clock) time: 21:17.19   Maximum resident set size: 1224316 kB
exit=0
end 2026-10-07T08:26:49+00:00  load average: 1.04, 1.11, 1.10
```

9 passed, where 1.3 gave 8 passed and 1 failed. The two runs saw the same
host load (one-minute averages between 0.25 and 1.43 at their ends). The
time is not like for like: in 1.3,
`test_every_instruction_reaches_its_documented_end_state` ended with the
uncaught `BrepCommonInconsistency` raised from the method itself (the
traceback runs from `run_test`'s `method()` through `seats.py`'s
`assert_overlap_inventory` at line 309), so the rest of the Target pose's
overlap inventory and the whole of the Present pose's, the last of
`INSTRUCTION_END_STATES`, were never compared. In this run both were (user
CPU 1459.65 s against 651.93 s). The guard's own share is measured on the
pair alone below: the changed engine returns the pair's empty common in
37.5 s, where the unmodified engine refused it in 28.5 s. Stage P's
investigation took 1243.25 s for the same 9 passed with the design patched
in.

Afterwards `git -C <astro> status --short` printed nothing, `HEAD` was
`58e46cd548126ce4a5be5b33c8a0a11670c8cad4`, `find <astro> -newer
<scratch>/stageA-marker -not -path '*/.git*'` printed nothing, and `_build`
(`2026-10-03 08:48:40`) and `_build.lock` (`2026-09-12 00:25:04`) kept their
stamps.

The pair alone, `astro_pair.py` as in 1.4 against the changed tree (its
`bench` line now runs the implementation; load average 1.10 at the start,
1.09 at the end):

```
loaded in 1.5 s
bench: returned 0 solids (37.5 s)
proposed: returned 0 solids (37.7 s)
proposed stats {'resolved': 1, 'rejected': 1, 'accepted': 0, 'margins': []}
wall 80.29 s, max rss 789036 kB
```

The project again unchanged (`git status --short` and `find -newer`
empty).

### 5.2 The Curta pair, changed tree

The command of 1.5, unchanged; the `bench` lines now run the implementation
(load average 0.63 at the start, 0.78 at the end):

```
loaded in 6.0 s
z -0.2: native common solids 0
  bench: refused at (11.891042595905658, 1.106601773115647, 26.217514791126693) (0.39 s)
  proposed: refused at (11.891042595905658, 1.106601773115647, 26.217514791126693) (0.36 s)
  proposed accepted margins [(0.000163776590032148, 0.0005772348360788288)] stats resolved 1 rejected 0
  hand witness (11.93431004745964, 0.4477315369512816, 26.088069310162098): states ['IN', 'IN'] margins [0.010000113260256849, 0.00029428320044078837]
    neighbour axis 0 +0.000147: ['IN', 'IN']
    neighbour axis 0 -0.000147: ['IN', 'IN']
    neighbour axis 1 +0.000147: ['IN', 'IN']
    neighbour axis 1 -0.000147: ['IN', 'IN']
    neighbour axis 2 +0.000147: ['IN', 'IN']
    neighbour axis 2 -0.000147: ['IN', 'IN']
z +0.2: native common solids 0
  bench: refused at (11.749660151572499, 2.137450584281421, 33.27912367737267) (0.31 s)
  proposed: refused at (11.749660151572499, 2.137450584281421, 33.27912367737267) (0.32 s)
  proposed accepted margins [(0.0005945586249650472, 0.00050408508775406)] stats resolved 2 rejected 0
  hand witness (11.541571853564232, 3.0652117978127276, 32.321879856111245): states ['IN', 'IN'] margins [0.010005803566569304, 0.0013332730964030494]
    neighbour axis 0 +0.000667: ['IN', 'IN']
    neighbour axis 0 -0.000667: ['IN', 'IN']
    neighbour axis 1 +0.000667: ['IN', 'IN']
    neighbour axis 1 -0.000667: ['IN', 'IN']
    neighbour axis 2 +0.000667: ['IN', 'IN']
    neighbour axis 2 -0.000667: ['IN', 'IN']
wall 31.43 s, max rss 635108 kB
```

Both ±0.2 mm pairs are still refused by the implementation, at the witnesses
the unmodified engine reports. Afterwards `git -C <curta> status --short`
printed the same four untracked entries, `HEAD` was `1f3dc22`, and `find
<curta> -newer <scratch>/stageA-marker -not -path '*/.git*'` printed
nothing.

### 5.3 Voron-2 was not run

`projects/3D-Printers/Voron-2` is paused by the pilot and its suites take
hours. Its twelve ordered thread-seat refusals are genuine OCCT false
empties: in its `docs/evidence/thread-seat-actual-contacts.json`, an
independent ball of radius 0.01 mm at 0.2 mm from both surfaces has a full
common with each operand. The slab test of section 2 stands in for that
shape (real material of both operands around the witness); the Voron pairs
themselves were not re-run under this change, and `workflow/warts.md`
records the re-run as owed, under the Voron-2 section.

## 6. Records

- 6.1 ADR-142 gains "Amendment — 2026-10-07: A Witness Is Interior in Its
  Neighbourhood" after the first amendment: the OpenAstroMount reading, the
  neighbourhood rule and why it is sound, the skipped candidate, the Curta
  pairs still refused, Voron-2 not re-run, and a link to this evidence. Its
  index line in `docs/adrs/README.md` reads "**Accepted**, amended
  2026-09-23 and 2026-10-07".
- 6.2 `docs/architecture.md`, the guard paragraph: the witness's six axis
  neighbours at half its smaller face distance are inside both too; a
  neighbour read outside proves a reading wrong and the candidate is
  skipped.
- 6.3 `docs/reference/assertions.rst`, the `intersect_shapes` paragraph: one
  clause added to the witness sentence.
- 6.4 `docs/project/changelog.rst`: one bullet at the end of the single
  `Unreleased` section, "An empty common is not refused on one reading its
  neighbourhood contradicts.", naming the change.
- 6.5 The warts entry "OpenAstroMount — a scenario test refused by the exact
  common guard (3 October 2026)" moved verbatim from `workflow/warts.md` to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
  "`a-witness-is-interior-in-its-neighbourhood`", with a "What shipped"
  paragraph that says Voron-2 was not re-run.
- 6.6 The orchestrator's answers to design.md's open questions recorded in
  `workflow/warts.md`: "A re-run owed under
  `a-witness-is-interior-in-its-neighbourhood` (7 October 2026)" under the
  Voron-2 section (**Owed**), and "Findings from the framework cycle
  `a-witness-is-interior-in-its-neighbourhood` (2026-10-07)" with the
  shallow sphere dent the stencil misses (**Untriaged**). The campaign note
  `workflow/ongoing/fix-warts-3.md` gains Progress lines for investigation 2
  and this cycle after cycle 17's.

## 7. Sync, archive, checks

- 7.1 The two delta requirements were synced by hand into
  `openspec/specs/brep-engine/spec.md` (the requirement's sentence and the
  scenario "A lone inside reading is not a witness"; its three scenarios
  carried, four now) and `openspec/specs/test-framework/spec.md` (the
  requirement's sentences and the scenario "OpenAstroMount bearing seat";
  its five scenarios carried, six now). Copies of both were taken to
  `<scratch>/brep-engine-after-manual-sync.md` and
  `<scratch>/test-framework-after-manual-sync.md`.
- 7.2 `openspec validate a-witness-is-interior-in-its-neighbourhood`:
  "Change 'a-witness-is-interior-in-its-neighbourhood' is valid". Then
  `openspec archive a-witness-is-interior-in-its-neighbourhood --yes`
  (openspec 1.6.0): "brep-engine: update", "test-framework: update",
  "Totals: + 0, ~ 2, - 0, → 0", "Change
  'a-witness-is-interior-in-its-neighbourhood' archived as
  '2026-10-07-a-witness-is-interior-in-its-neighbourhood'", with the
  warning that the Why section exceeds 1000 characters. `diff` of each
  hand-synced copy against the archived result printed nothing: the CLI's
  replacement is byte-identical to the hand sync. `openspec validate
  --specs`: "Totals: 45 passed, 0 failed (45 items)".
- 7.3 Focused tests once more, after the archive:
  `pytest -q -p no:cacheprovider tests/test_witness_neighbourhood.py
  tests/test_brep_common_guard.py tests/test_resolved_brep_witness.py
  tests/test_engine_package.py tests/test_verdict_store.py
  tests/test_release_records.py tests/test_docs_structure.py`:

  ```
  98 passed, 891 subtests passed in 7.39s   (wall 8.68 s)
  ```

- 7.4 The full suite, once, alone: `pytest -q -p no:cacheprovider` at the
  bench root, no other run of ours in progress (load average 0.54 at the
  start, 1.80 at the end):

  ```
  4753 passed, 4 skipped, 55 warnings, 6706 subtests passed in 735.12s (0:12:15)
  (exit 0, wall 737 s)
  ```

  During that run `_false_empty_witness`'s docstring was rewrapped (its
  last two lines joined, no word changed). After it, `flake8
  --max-line-length=89` on the two touched Python files printed nothing,
  `black --diff` gave `brep.py` 14 hunks as before, and the focused tests
  of section 4 gave "73 passed, 72 subtests passed in 6.64s".

Everything is left uncommitted.
