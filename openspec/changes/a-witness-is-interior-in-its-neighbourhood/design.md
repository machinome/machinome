## Context

`intersect_shapes` (`machinome/engine/brep.py`) returns OCCT's Common when it
holds a solid. When it holds none, `_false_empty_witness` builds the native
section of the two operands, takes up to eight of its edges, and at a
quarter, a half and three quarters of each edge tries 26 directions at three
steps (10⁻⁴, 10⁻³ and 10⁻² of the smallest bounding-box span). The first
point that a zero-tolerance `BRepClass3d_SolidClassifier` finds IN a solid of
each operand, and that `_resolved_interior` finds farther from every face of
those solids than that face's own tolerance, is returned as the witness, and
`intersect_shapes` raises `BrepCommonInconsistency` (ADR-142, and its
amendment of 23 September 2026 for the tolerance test).

The tolerance test answers one way a zero-tolerance classifier is wrong: it
rounds a point lying on a face. It does not answer a classifier that is wrong
at a point well away from every face, and OpenAstroMount is that case.

**OpenAstroMount, Target end state (azimuth 2, altitude 44, RA 5, DEC 5).**
The housing `head.frame.mancal_f206_valor_predeterminado_1.housing` and the
insert `head.right_ascension_axis.rolamento_uc206_valor_predeterminado_1`
are vendor STEP solids from the project's single assembly
`CAD/STEP/OpenAstroMount_v1.0.STEP`, both valid by `BRepCheck_Analyzer` as
read and as placed. Their seat is two spheres of radius 31.000 mm with the
same centre `(26.1397, 252.3912, 444.6636)`, and the right ascension turns
the insert about an axis through it, so the pair is a zero-volume contact at
every angle. OCCT's Common is empty in the world frame, with the operands
swapped, in the housing's frame and with fuzzy values from 10⁻⁶ to 10⁻³ mm.
The bench's guard returns `(-2.0242287706088176, 265.5583117280026,
442.97547336608244)`:

| Reading at the witness | Housing | Insert |
| --- | --- | --- |
| Zero-tolerance classifier | IN | IN |
| Distance to the nearest face (that face's tolerance) | 0.0999563 mm (10⁻⁷) | 0.135651 mm (10⁻⁷) |
| Distance from the shared sphere centre | 31.135651 mm | 31.135651 mm, outside the R 31 sphere |
| Classifier at ±10⁻⁴ mm along the axes | IN | OUT on 3 of 6 |
| Classifier at ±10⁻³ mm along the axes (insert's own frame) | | OUT on 5 of 6 |
| Classifier on a 3600-point ring at the witness's radius and height (insert's own frame) | | IN at the witness's azimuth only |
| Common of a 0.01 mm ball there with the operand | the whole ball | no solid |

Forty thousand samples of the shared bounding box and of the seat shell
(|r − 31| ≤ 0.05 mm) find no point IN both. The insert's classifier is wrong
at one point, 0.1357 mm from its nearest face; why OCCT answers IN there was
not established (`scratchpad/investigations/openastromount.md`, §2).

**Reproduced on the bench at `a5d148f`** with the investigation's sketch,
`scratchpad/cycle18/test_neighbourhood_sketch.py`: unit boxes at the origin
and at (0, 1, 0) touch along y = 1; `_boolean` is patched to return an empty
compound; the second box's classifier is wrapped so that it answers IN at
exactly one point, the first point strictly below the contact it is asked
about, and natively everywhere else.

```text
env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/pytest -p no:cacheprovider --rootdir <scratch> -q \
  <scratch>/test_neighbourhood_sketch.py
E  machinome.engine.BrepCommonInconsistency: B-rep common of first and
   second was empty despite a point strictly inside both native solids:
   (5.7735026918962585e-05, 0.999942264973081, 0.24994226497308103).
```

**ADR-142's originating pair, measured under the bench and under this
design** (`scratchpad/cycle18/curta_measure.py`, run from the project
`Calculators/Curta-Type-I-3x` at `1f3dc22` with a scratch `SOLID_BUILD_DIR`,
80 s; the project left unchanged): `Sim(MechanisticCurta(), dt=.1)`,
assembled, `world_solids` for the positioning ball and
`frame.upper_frame.main_body`, the ball translated by
(2.213142830078919, 0, ±0.2) as in that change's evidence. OCCT's Common is
empty at both. Both the bench and this design refuse both, at the same
witness:

| z | Witness (bench and proposed) | Margins (ball, frame) | Hand-measured witness of 23 September: margins; six neighbours at half the smaller |
| --- | --- | --- | --- |
| −0.2 | `(11.891042595905658, 1.106601773115647, 26.217514791126693)` | 1.638 × 10⁻⁴, 5.772 × 10⁻⁴ mm | 0.010000, 0.000294 mm; IN/IN on all six |
| +0.2 | `(11.749660151572499, 2.137450584281421, 33.27912367737267)` | 5.946 × 10⁻⁴, 5.041 × 10⁻⁴ mm | 0.010006, 0.001333 mm; IN/IN on all six |

## Goals / Non-Goals

**Goals:** a single zero-tolerance IN reading that its own face-free
neighbourhood contradicts no longer overturns an empty Common;
OpenAstroMount's scenario passes; every false empty the guard refuses today
for real shared interior (the Curta ball and frame, a slab of shared
interior) is still refused.

**Non-Goals:** no change to the stencil, its budget or its order; no
tolerance, mesh verdict, volume or second Boolean in the decision; no claim
that an unwitnessed empty is certified; no explanation of OCCT's classifier.

## Decisions

### 1. A witness is corroborated inside the ball its own face distance clears

`_resolved_interior(solid, point)` measures the distance from the point to
every face of the solid, as today. Where today it returns `False` for a point
within some face's tolerance and `True` otherwise, it returns `None` for the
former and, for the latter, the smallest of those distances (its *margin*,
always greater than zero).

In `_false_empty_witness`, a candidate classified IN a solid of each operand
and resolved in a solid of each (margins `m1` and `m2`) becomes the witness
only when the six points `p ± (min(m1, m2) / 2)·e` for `e` in x, y and z are
each classified IN, at zero tolerance, by the classifier of that same solid of
the first operand and of that same solid of the second. When an operand has
several solids holding the candidate, any resolved pair whose six neighbours
pass makes the witness. A candidate whose neighbours do not all pass is
skipped and the search goes on to its next point, the treatment an unresolved
candidate already receives.

The reason it is sound: the boundary of a solid is the union of its faces, and
no face of the solid comes closer to `p` than its margin, so the open ball of
that radius about `p` is connected and meets no boundary: every point of it
has `p`'s true state. The six neighbours lie inside both balls, at half the
radius. If the classifier is right at all seven points they all agree; an OUT
among the neighbours proves the classifier wrong somewhere in a ball where the
truth is uniform, and a reading that is contradicted there is no proof of
shared interior. Agreement proves nothing new about the truth; it raises the
evidence a witness needs from one reading per solid to seven.

The neighbours are at half the margin so that they are distinct readings, not
the centre rounded again, and stay clear of the face that sets the margin.

The witness reported is still the centre point, so `BrepCommonInconsistency`'s
message keeps its shape. A neighbour that the classifier answers UNKNOWN
raises, as every classification in the search does today, and so reaches
`BrepCommonVerificationError`. A `Rejected()` neighbour is OUT, as everywhere
in the search.

Code shape, `machinome/engine/brep.py`:

- `_resolved_interior(solid, point)`: the same loop, keeping the running
  minimum distance; `return None` where it returns `False`; returns the
  minimum at the end. Its docstring says it returns the margin.
- `_false_empty_witness(first, second)`: `inside` returns the
  `(classifier, solid)` pairs that classify the point IN, so a neighbour is
  put to the classifier of the same solid; a small local `classified_in(
  classifier, point)` holds the Perform/Rejected/UNKNOWN/IN reading the
  search already does, used by `inside` and by the neighbour check; after
  `candidates2` is non-empty, the margins of the candidates are measured, the
  unresolved dropped, and the six neighbours checked for each resolved pair.
  Its docstring and `intersect_shapes`'s say a witness needs its six
  neighbours.
- `_resolved_interior` is still measured only for a point both classifiers
  call IN, so the face distances stay as rare as today.

### 2. A contradicted candidate is skipped, not refused

The alternative is to raise `BrepCommonVerificationError` when a candidate's
neighbours disagree, on the reading that a classifier inconsistent with
itself makes the check fail. It would keep OpenAstroMount's correct empty
Common refused, under another name, and the project's scenario red. The
finding is that the Common is right; the candidate is the unreliable
evidence. Skipping it is what the first amendment did for an unresolved
candidate, and leaves the rest of the budget to find a corroborated one.

### 3. An amendment of ADR-142, not a new ADR

ADR-142 decides that a strict shared-interior witness refuses an empty Common
and that nothing else does; its first amendment narrowed which points count as
a witness. This change narrows it once more, for the same reason (a
zero-tolerance reading that is not reliable proof), and decides nothing new
about the Boolean, the stencil or the errors. The ADR log's discipline
(`docs/adrs/README.md`) amends an ADR in place with a dated section for that.
Its index line notes both amendments.

### 4. Alternatives not taken

- **A small ball's Common with each operand**, the investigation's proof: it
  would make the witness depend on another OCCT Boolean, the operation the
  guard exists to doubt, and would need a ball radius of its own.
- **Classifying at a tolerance** (`Perform(point, tol)`): an epsilon by
  another name, and ADR-142 keeps the classification at zero.
- **Denser corroboration** (a ring, a cube field, random samples): costlier,
  with no stronger argument than the six points have.
- **Separate probes per solid** (`m1 / 2` in the first, `m2 / 2` in the
  second): as sound, but the six points would no longer be one set claimed
  inside both; the shared half of the smaller margin keeps the witness a
  shared-interior claim.

## Proof plan

Red tests, new file `tests/test_witness_neighbourhood.py`, each run on the
unmodified tree and seen failing for the reason given:

1. **A lone inside reading is not a witness.** The sketch above: red with
   `BrepCommonInconsistency` at `(5.7735026918962585e-05, 0.999942264973081,
   0.24994226497308103)`; green when the empty Common is returned and the lie
   was asked exactly once.
2. **`_resolved_interior` reports the margin.** For the unit box,
   `(.5, .5, .5)` gives 0.5 and `(.9, .5, .5)` gives 0.1 (to 1e-12), and
   `(1 - 1e-15, .5, .5)` gives `None`. Red: it returns `True`.
3. **An undecided neighbour refuses.** Boxes at the origin and at
   (.5, .5, .5), `_boolean` patched empty, a classifier wrapper that answers
   natively until the second operand's classifier has once answered IN and
   UNKNOWN for every query after that: `BrepCommonVerificationError`
   naming `UNKNOWN`. Red: the bench returns the first candidate and raises
   `BrepCommonInconsistency`.

A preservation test in the same file, green before and after:

4. **A slab of shared interior is still refused** (the Voron-2 shape: real
   material of both operands around the witness). Boxes at the origin and at
   (0, .6, 0) share a 0.4 mm slab; `_boolean` patched empty;
   `BrepCommonInconsistency`, its witness inside the slab.

`tests/test_brep_common_guard.py` and `tests/test_resolved_brep_witness.py`
stay green unedited; `test_rounded_boundary_point_is_not_a_resolved_interior`
reads `_resolved_interior` with `assertFalse` and `assertTrue`, which `None`
and a positive margin satisfy. With the design patched in from the scratchpad
(`neighbourhood_patch.py`), the sketch's two tests and those 13 tests pass, 7
subtests passed.

Project validation, read-only, one run at a time:

- **OpenAstroMount** (`exact-engine-validation`, `58e46cd`):
  `env -C <project> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
  SOLID_BUILD_DIR=<scratch>/build machinome test --brep --no-verdict-store
  simulation/mount.py`, before (8 passed, 1 failed, 569 s on 7 October) and
  after (9 passed; the investigation's patched run took 1243 s), with the
  host's load average recorded beside each.
- **The pair alone**, `scratchpad/cycle18/astro_pair.py` (source copied into
  evidence): at the Target pose the bench refuses after 27.6 s and the design
  returns the empty Common after 36.9 s (load average 1.2), one resolved
  candidate seen and rejected.
- **Curta Type I**, `scratchpad/cycle18/curta_measure.py` (source copied into
  evidence) re-run after the change on the real implementation: both ±0.2 mm
  pairs still refused.
- **Voron-2 is not run.** Its thread-seat refusals are genuine false empties
  (in `projects/3D-Printers/Voron-2/docs/evidence/thread-seat-actual-contacts.json`,
  a 0.01 mm ball at 0.2 mm from both surfaces has a full Common with each
  operand); the project is paused by the pilot and its suites take hours. The
  slab test stands in for its shape; the Voron pairs themselves were not
  re-run under this change (Open Question 1).

## Risks / Trade-offs

- [A genuine false empty could now pass] Only if OCCT's classifier is wrong
  OUT at one of the six neighbours of a genuinely interior candidate, and no
  other candidate in the budget is corroborated. Then the empty Common is
  returned, as any unwitnessed empty is; the guard never claimed to certify
  one. Measured: the Curta pairs and the slab are still refused (Open
  Question 1).
- [Probes nearer a face than its tolerance] A margin smaller than twice some
  face's tolerance puts a probe within that tolerance, where a zero-tolerance
  classifier may answer ON; the candidate is then skipped. The margins seen
  are 10⁻⁴ to 10⁻¹ mm against tolerances of 10⁻⁷ mm.
- [Cost] Twelve more classifications for each resolved candidate, which only
  an empty Common reaches; and a skipped candidate lets the search run on
  through the rest of its finite budget where it used to stop. Measured on
  OpenAstroMount's pair: +9.3 s for the one call that used to refuse. The
  investigation's whole patched run took 1243 s against 569 s unpatched, with
  the host's load not recorded; Stage A records both runs' wall times with the
  load average.

## Open Questions

1. **Can the neighbourhood check let through a false empty that ADR-142
   refuses?** Measured, no, for every case at hand: ADR-142's originating
   Curta pairs are refused at the same witness as on the bench, with all six
   neighbours IN both at the stencil's witness and at the two hand-measured
   witnesses of 23 September (table in Context); the 0.4 mm slab is refused.
   In principle yes, if OCCT's classifier answers OUT wrongly inside a
   face-free ball around a genuine interior point (Risks). Voron-2's
   thread-seat pairs, the other known genuine false empties, were not re-run:
   their independent 0.01 mm balls at 0.2 mm from both surfaces say there is
   material of both there, but the stencil's own witness point and its
   neighbours' readings were not measured. Recommendation: accept the change,
   and have Stage A record in `workflow/warts.md` that Voron-2's thread-seat
   refusals are owed a re-run under this change when the pilot resumes that
   project. Answered by the orchestrator at review (7 October 2026):
   accepted; Voron-2's re-run recorded as owed.
2. **The stencil misses a shallow sphere dent, before and after this
   change.** Measured with `scratchpad/cycle18/probe_sphere.py`: a sphere of
   radius 3.75 mm sunk 0.2, 0.05 or 0.01 mm into a 10 mm block's face, with
   the Boolean patched empty, is not refused by the bench or by this design
   in any of five orientations tried: no stencil point is IN both. The 26
   directions miss the thin wedge between a plane and a sphere that meets it
   at under 19°. That is a blind spot of the guard's finite budget, not this
   finding, and this change does not touch the stencil. Recommendation: Stage
   A records it in `workflow/warts.md` as a finding for triage. Answered by
   the orchestrator at review (7 October 2026): recorded, not taken here.
