## Context

`intersect_shapes` (`machinome/engine/brep.py`) returns OCCT's Common when it
holds a solid. When it holds none and neither operand is inside out,
`_false_empty_witness` builds the operands' native section and walks up to
eight of its edges: at a quarter, a half and three quarters of each, three
steps (10⁻⁴, 10⁻³ and 10⁻² of the smallest bounding-box span) in 26
directions, 1,872 points at most. At each point it asks the first operand's
zero-tolerance `BRepClass3d_SolidClassifier`s, and for a point inside, the
second operand's; a point inside both is measured (`_resolved_interior`, its
margin: the smallest distance to each solid's faces, or nothing within a
face's tolerance), and its six axis neighbours at half the smaller margin
must be classified inside both before it refuses the common (ADR-142 and its
amendments of 23 September, 7 October and 9 October 2026).

On a touching pair no point is inside both, so the walk runs to its end, and
its cost is whatever the classifiers cost there. Wall clock 02's weight
shell is a valid 32-face solid whose classifier answers in 0.6 ms at its
centre and in 190–300 ms near the screw it touches; the screw's (5 faces)
answers in under 0.1 ms.

**Measured for this proposal (9 October 2026)** on the bench at `d9fd98d3`,
against the placed pair captured from wall clock 02 at `ec2a05d`
(`shell.brep`, `screw.brep`). Every script ran from the bench as
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
/home/asa/devel/machinome/.venv/bin/python <script> ...`, one at a time,
while other sessions kept the host's load average between 5 and 32 (noted
per row), so absolute times run high and the counts are the evidence. The
scripts are copied into this change's `measurements/` directory; `side.py`
there is the sketch of Decisions 1 and 2.

| Run | What | Result |
| --- | --- | --- |
| warts, 9 Oct (`stencil.py`) | bench, shell first, as the clock asks it | 324 s; 2,547 classifications (1,872 shell, 675 screw); no candidate |
| M6 (`m6_bench_screw_first.py`, load 27–32) | bench, operands swapped (screw first; the section's edge order differs) | 146.9 s; 2,490 classifications (1,872 screw, 618 shell); no candidate |
| M1 (`m1_points.py`, load 12–14) | the 1,872 stencil points one by one | 8 section edges used of 9, scale 6.2 mm, steps 0.00062/0.0062/0.062 mm; screw classifier: 1,872 points in 0.18 s, 730 inside, 242/246/242 per step; shell classifier on a 280-point sample: 204 ms mean, 287 ms median, 445 ms max, 79 inside, none inside both |
| M1 | the nearest-boundary side read from faces only, one `BRepExtrema_DistShapeShape` against the solid's shells | shell 1.59 ms a point, screw 0.18 ms; of the 730 points inside the screw, the shell reads outside at 330, on the boundary at 17, and its nearest boundary point lies on an edge at 383 |
| M2 (`m2_side.py`) | the side read from faces and two-faced edges (a seam as one face on both sides) | shell 1.4–2.1 ms a point, screw 0.17–0.24 ms; nothing undecided on either solid. Screw, all 1,872 points: 888 read outside and 702 inside, each as its classifier reads it, and 282 on the boundary. Shell, M1's 280-point sample: 176 outside and 59 inside, each as its classifier reads it, and 45 on the boundary |
| M2, M5 (`m5_orders.py`, load 12–14) | the sketch's search, end to end | **1.57 s** (shell given first) and **1.27 s** (screw given first): 1,872 classifications of the screw, **none of the shell**, 730 and 618 side readings; no candidate |
| M3 (`m3_synthetic.py`) | the bench and the sketch on synthetic pairs | the same witness, to the last digit, in each of the nine shared-material cases, every one found at the finest step: overlapping unit boxes, a 0.4 mm slab, a pin 0.2 and 0.05 mm over its hole, a key overlapping its slot's floor by 0.5 mm with and without 0.1 mm side interference, two 240-gon prisms overlapping by a sliver (0.00056 mm³), a 240-gon prism and a box overlapping by a sliver (0.00028 mm³) and by 0.83 mm³; the touching pairs (unit boxes meeting on a face and on an edge, a pin exactly in its hole, a hemisphere standing on a face) give no witness in either |
| M4 (`m4_spheres_and_cost.py`) | a full 3.75 mm ball sunk 1.0, 0.5, 0.2 and 0.05 mm into a block | genuine overlaps (native common 10.7 to 0.029 mm³) on which neither search finds a witness: the shallow-dent blind spot reaches deeper than the 0.2 mm the warts entry records, and is unchanged |
| M3 | `BRepExtrema_DistShapeShape` of a vertex against the shell *solid* at five slow points | 304–421 ms, against 316–367 ms for the classifier there: against a solid operand the extrema classifies the vertex, and costs what the classifier costs; against the solid's shells it is 1.4 ms |
| M5 | healthy touching pairs, bench / side read first for both / the proposed order | boxes on a face 0.03 / 0.21 / 0.04 s; pin exactly in its hole 0.09 / 0.42 / 0.20 s; 240-gon prism and box 0.21 / 0.48 / 0.26 s; 214-face slotted body and a ring 1.63 / 4.61 / 1.48 s, the ring given first 0.77 / 2.33 / 1.61 s |
| M7 (`m7_red_sketch.py`) | classifier calls by solid on the pin exactly in its hole, Boolean patched empty | bench: plate (7 faces) 1,404 and pin 480 with the plate first; pin 1,404 and plate 486 with the pin first. Sketch: pin 1,404, **plate 0**, in both orders |
| M8 (`m8_side_cases.py`) | the side on unit cases | unit box: inside at the centre, outside past a face, outside past an edge, on the boundary 10⁻⁹ mm either side of a face, undecided past a corner; an L-shaped solid: inside nearest its concave edge; a cylinder: outside and inside nearest its seam. Each agrees with the classifier where both decide |
| guard tests under the sketch (`sketchplugin.py`) | `tests/test_brep_common_guard.py`, `test_witness_neighbourhood.py`, `test_resolved_brep_witness.py` | 18 of 19 pass; `LoneInsideReadingTest` fails because its lie is never asked: the side reading excludes the point. With every side undecided (`undecidedplugin.py`) all 19 pass |

## Goals / Non-Goals

**Goals:** the witness's cost on a touching pair is bounded by side readings
and the cheaper classifier rather than by the slower classifier; on the
captured pair, seconds instead of minutes, with no classification of the
shell; every refusal the guard makes today is made at the same point; no
overlap volume, tolerance or mesh verdict enters.

**Non-Goals:** changing the stencil, its budget or its order; finding the
witnesses the stencil misses; explaining why OCCT's classifier is slow near
the shell's contact; the section's cost; the contact-semantics decision.

## Decisions

### 1. The operand with fewer faces is classified first

At each point the search asks the classifiers of the operand whose solids
have fewer faces in total, the first operand on a tie; the other operand is
asked only for a point the first puts inside, as the second operand is
today. A witness needs both operands inside, so the order changes neither
which points count nor which point is found first. It changes which
classifier is asked at points outside one operand, and so where an UNKNOWN
can arise: the cheaper operand's classifier is now asked at every point, and
the other's at fewer.

Alone, this halves the measured case (M6: 146.9 s, 618 shell
classifications): the screw holds 730 of the stencil's points, and each
still costs a shell classification of 200 ms or more.

### 2. A point's side is read from its nearest boundary point before the other operand's classifier

For a point the cheaper operand puts inside, before any classifier of the
other operand is consulted, the engine reads the point's side of every
solid of both operands:

- The nearest boundary point `q`, its distance `d` and its support (a
  face's interior, an edge, a vertex) found face by face through the
  faces' boxes, as the Revision below rules (the proposal's one extrema
  against the compound of the solid's shells measured nine times a
  healthy classification on the clock's 218-face parts). Never against the
  solid: an extrema against a solid classifies the point and is as slow
  as the classifier (M3).
- `q` inside a face `F`: if `d` is within `F`'s native tolerance, the side is
  *on the boundary*. Otherwise the outward normal `n` of `F` at `q`
  (`BRepGProp_Face.Normal`, which follows the face's orientation in the
  solid) gives the side: *outside* when `(p − q)·n > 0`, *inside* when
  `< 0`.
- `q` inside an edge `E` used by exactly two faces of the solid, or by one
  face as its seam: *on the boundary* if `d` is within either face's
  tolerance; otherwise `n1` and `n2` are the faces' outward normals at `q`,
  each at the edge parameter of `q` mapped through that face's pcurve, and
  the sign of `(p − q)·(n1 + n2)` gives the side. A seam counts its face
  twice. An edge that is degenerated or not same-parameter is undecided.
- Undecided: `q` at a vertex, an edge with another number of faces, a
  failed or empty extrema, a non-finite distance or tolerance, a vanishing
  normal or `n1 + n2`, solutions that disagree, or a sign that is not clear
  (a face reading whose `p − q` is more than about 25° off the normal,
  `|cos| < 0.9`, or an edge reading with `|cos| < 0.1`).

A solid whose side reads *outside* or *on the boundary* holds no candidate
at that point. When no solid of an operand remains, the point is skipped,
and the other operand's classifiers are not consulted there. Otherwise the
remaining solids are classified exactly as today, and the margins, the
neighbours and the refusal follow unchanged. A side reading never makes a
point count; it only spares a classification whose answer could not make
one.

Why it is sound. The open ball of radius `d` about `p` meets no face, so all
of it has `p`'s state (the argument of the 7 October amendment). If `q` is
inside a face, the ball is tangent to the face at `q`, `p − q` is along its
normal, and the ball's points next to `q` lie on the side `p − q` points to.
If `q` is inside an edge, `p − q` lies in the cone both face sheets leave
free: at a convex edge the cone spanned by `n1` and `n2`, which is outside;
at a concave edge the cone spanned by `−n1` and `−n2`, which is inside; at a
tangent edge or a seam `n1 = n2`. In each case `(p − q)·(n1 + n2)` has the
sign of the side. A point within a face's tolerance is one
`_resolved_interior` already rejects, so reading it *on the boundary*
excludes nothing that could count. The argument is first order at `q`,
which is why a reading near a tangent direction is left undecided. It rests
on OCCT's extrema placing the nearest boundary point correctly, the same
instrument `_resolved_interior` already trusts for the margin and the
neighbour radius.

What a wrong reading could do. A side read *outside* where the point is in
fact inside would skip a point the classifiers might have refused on; a
side read *inside* where it is outside only leaves the classifiers to answer
as today. So the guard's one new way to miss a false empty is an extrema
that misplaces the nearest boundary point at a genuine witness. No
disagreement was seen: 1,590 decided screw points and 235 decided shell
points agree with the classifier (M2), the unit cases agree (M8), and every
synthetic refusal is made at the same point (M3).

What it costs. One extrema per solid at each point the cheaper operand puts
inside: on the captured pair 1.4–2.1 ms on the shell and 0.2 ms on the
screw, against 200 ms or more for the shell's classifier. On healthy pairs
the side readings replace classifications of similar cost; M5's synthetic
touching pairs run between 0.9× and 2.2× today's time.

Code shape, `machinome/engine/brep.py`: a private `_boundary(solid)` (the
compound of its shells and its edge-to-face map, from
`TopExp.MapShapesAndUniqueAncestors_s`; its faces explored from the solid
itself, so each face's orientation is the composed one and its
`BRepGProp_Face` normal points out of the solid, review note of
9 October) and `_nearest_side(boundary, point)`
returning `'out'`, `'in'`, `'on'` or `None`; in `_false_empty_witness`, the
operands' classifiers and boundaries ordered by face count, the cheaper
operand's `inside` first, then the side readings, then the other operand's
`inside` over the solids left. Patching `_nearest_side` to return `None`
restores today's classifications exactly, apart from the order of
Decision 1.

### 3. Levers measured or reasoned and not taken

- **Choosing the cheaper classifier by timing its first probes.** The order,
  and with it which classifier is asked where an UNKNOWN can refuse, would
  follow the host's load. The face count is deterministic and right on the
  measured pair.
- **The margin before the classifier.** `_resolved_interior` costs 10.5 ms a
  point on the shell (32 face distances); 370 of the 1,872 points are within
  a shell face's tolerance (M2), so measuring every margin first would add
  about 20 s to spare about 74 s of classification, about 270 s in all
  (derived from M2's counts, not run). Decision 2's *on the boundary*
  reading is this lever at one extrema's cost.
- **Faces only, without the edge rule.** 383 of the 730 points inside the
  screw have their nearest shell boundary point on an edge (M1), mostly the
  hole's rim and the seams; about 370 shell classifications would remain,
  some 75–107 s.
- **Coarse step first, and stopping early.** The shell's classifier costs the
  same at every step (190–300 ms, and the screw holds 242, 246 and 242
  points per step), so only stopping saves time, and stopping is searching
  less. The step at which the Curta's two witnesses are found is not
  recorded; their margins (1.6 × 10⁻⁴ to 5.9 × 10⁻⁴ mm) do not exclude the
  finest step, every synthetic witness of M3 is found at the finest step,
  and the Curta cannot be run in this cycle.
- **Fewer directions or steps.** Savings proportional to the points removed,
  on a stencil that already misses balls sunk up to 1 mm into a block (M4).
- **A cap on classifications.** Bounded, but to bring the shell under a few
  seconds the cap would be about 20 classifications, the first anchor's
  first step, and which witnesses survive it is unknowable without the
  Curta. No measured case needs a cap once Decision 2 holds.
- **Another OCCT point classifier.** `BRepClass3d_SClassifier`,
  `BRepClass3d_SolidExplorer` and `BRepClass3d_SolidPassiveClassifier` are
  the same ray algorithm the classifier wraps; `BRepExtrema_DistShapeShape`
  against a solid classifies the point and costs what the classifier costs
  (M3); a ray-parity count of our own
  over `IntCurvesFace_ShapeIntersector` would have to own the tangent and
  edge hits the classifier retries on; a classifier tolerance above zero is
  an epsilon by another name. Only the nearest-boundary reading is a
  different instrument whose correctness argument is the one ADR-142's
  amendments already use.
- **Reading the side first for both operands, with no reordering.** As
  sound, independent of which classifier is slow, and it asks no classifier
  that today is not asked; but on healthy pairs it costs 2–7× today's (M5:
  1.63 s against 4.61 s, 0.09 s against 0.42 s). Decision 1's order keeps
  healthy pairs near today's cost.

### 4. An amendment of ADR-142, not a new ADR

ADR-142 decides that a resolved, corroborated shared-interior point refuses
an empty common and nothing else does. This change does not move that line:
a side reading never makes a point count. It changes which points the
finite search puts to the classifiers and in what order, which ADR-142's
decision ("a bounded native section-edge stencil and independently classify
candidate points") fixed; the pilot ratifies that as a fourth dated
amendment, "A Point's Side Is Read From Its Nearest Boundary Before a Slower
Classifier", recording the shell and screw, the soundness argument, the
synthetic refusals kept, Voron-2's result and the Curta's owed re-run. Its
index line in `docs/adrs/README.md` notes it.

### 5. Two existing tests are made to keep testing what they were written for

`LoneInsideReadingTest` and
`test_rounded_in_classification_on_tangent_faces_is_not_a_witness` inject a
classifier error (a lone IN, an ON rounded to IN) at points just outside a
solid or on its face. The side reading now excludes those points before the
lying classifier is asked: the first test fails on its own assertion that
the lie was told once, and the second passes without exercising anything.
Each gains one patch making `_nearest_side` return `None`, so the
neighbourhood rule and the tolerance rule are still tested on the
classifier path; the new file tests that the side reading excludes the
lone reading without asking. No other test in the three guard files is
edited.

## Proof plan

Red tests, new file `tests/test_witness_touching_pair.py`, each run on the
unmodified tree and seen failing for the reason given; none depends on
timing:

1. **The nearest side of a point** (`_nearest_side` on M8's cases: a unit
   box inside, outside past a face, outside past an edge, on the boundary
   10⁻⁹ mm inside and outside a face, undecided past a corner; an L-shaped
   solid inside by its concave edge; a cylinder outside and inside by its
   seam). Red: the helper does not exist.
2. **A pin that fits its hole is settled without the plate's classifier.**
   `_boolean` patched empty, the classifier wrapped to count calls per
   solid, the pin and the plate in both orders: the empty Common returned
   and the plate's classifier never asked. Red: 1,404 and 486 calls (M7).
3. **A side reading does not move a refusal.** For overlapping boxes, the
   0.4 mm slab, a pin 0.2 mm over its hole and a key 0.1 mm into its slot,
   `_boolean` patched empty: the refusal's point with the side readings
   equals the point with `_nearest_side` patched to `None`. Red: the patch
   target does not exist.
4. **The side reading excludes a lone inside reading without asking it.**
   `LoneInsideReadingTest`'s boxes and lying classifier, with the real side
   reading: the empty Common returned and the lie never told. Red: the lie
   is told once.

Preservation, green before and after: the three guard files, with the two
edits of Decision 5 (each green under the bench and with the side readings
undecided), and `tests/test_engine_package.py`.

Validation outside the repository, read-only, one run at a time:

- **The captured shell and screw**: `measurements/m6_bench_screw_first.py`'s
  instrumentation (and the warts' `stencil.py`) run against the changed
  bench, both operand orders: no candidate, no shell classification, the
  times recorded with the load average.
- **Voron-2's thread seats**, the reviewer's: the six nut and screw pairs of
  `simulation/test_thread_seat_contacts.py`, placed as that test places them
  and compared with `intersect_shapes` in both orders under the bench and
  under the change, from a scratch script that calls nothing writing the
  project's cache and runs with a scratch `SOLID_BUILD_DIR`: every pair
  refused under both, at the same point.
- **The clock and the lock**: `ongoing/distance-tier-measurement-2026-10-09/measure.py`
  on wall clock 02's detached worktree at `ec2a05d` and on the combination
  safe lock at `8f185f6`, cold, with a scratch build directory, as on
  9 October: the witness time on zero-distance empties per pair group
  against the 9 October records, the shell, `collet`/`beat_screw` and
  `shell`/`nut` named.
- **OpenAstroMount**, optionally: the archived `astro_pair.py` at the Target
  pose: the empty common returned, as since 7 October.

## Revision after apply evidence (9 October 2026, the reviewer's ruling)

The first apply implemented Decisions 1 and 2 as written, with the side
read by one extrema from the point to the compound of the solid's shells,
and stopped at a stop point on task 5.3: on wall clock 02 the three
pathological groups settled (`shell`/`screw` 297.8 s → 1.26 s,
`beat_screw`/`collet` 43.7 s → 1.80 s, `nut`/`shell` 41.2 s → 0.62 s) and
Voron-2's twelve refusals stayed at the same points, but
`arbor`/`hour_holder` grew 119.0 s → 469.1 s (3.94×) and
`cannon_pinion`/`hour_holder` 57.2 s → 244.2 s (4.27×), and the clock's
zero-distance empties went from 582.9 s to 810.3 s. Diagnosed on the
captured pinion and holder: the holder's classifier settles a point in
0.9 ms, and one extrema over its 218 faces costs 8.4 ms. Decision 2's cost
assumption, that a side reading costs about what a healthy classification
costs, came from synthetic pairs and does not hold on gear-train parts.
(Evidence: this change's `evidence.md`, 5.3.)

The ruling: the instrument stays, its search changes. The nearest boundary
point is found through the faces' boxes, the same outward-only enclosures
`face_bounds` takes (`BRepBndLib.Add_s(face, box, False)`, the surface's
own extent plus its tolerance, never a triangulation), computed once per
`_boundary`. For a point, the distance from the point to every face's box
is a vectorised lower bound on its distance to that face; faces are visited
in ascending box distance, each by one extrema from the point to that face
alone, and the visit stops as soon as the next box distance is not below
the best face distance found. The nearest face and its support (inside the
face, on an edge, at a vertex) then give the side exactly as Decision 2
states: a face's outward normal, a two-faced edge's normals through the
edge-face map, undecided otherwise. The reading is the same reading, since
a box never excludes the face holding the true nearest point; what changes
is that a healthy solid costs the numpy pass over its boxes plus one or two
single-face extrema, in the order of a classification, instead of a search
over all its faces. The whole-shell extrema is not kept as a fallback:
there is one instrument.

Acceptance, on top of the Proof plan: tasks 5.1 and 5.3 are rerun under the
revised search; the pathological groups stay settled, no real pair group of
the lock or the clock exceeds 1.3× its 9 October witness time, and the
clock's zero-distance empties cost less than on 9 October. A group that
still grows is a stop point again, reported with its numbers.

Not taken, and why: accepting the regression spends more of the clock's
suite than the change saves; reading the side only where the other
classifier is slow is timing-based, which Decision 3 rejected; keeping
Decision 1 alone leaves the shell at about 147 s.

## Second revision after apply evidence (9 October 2026, the reviewer's ruling)

The box-pruned search was implemented, went red first and green, kept
every refusal (Voron-2's twelve at the same points, the synthetic ones),
settled the captured shell and screw in 1.3–1.6 s, and failed the first
Revision's acceptance. On the lock the suite's witness time fell below
9 October in every class of empty (zero distance 16.9 s → 13.3 s, under a
micrometre 23.7 s → 19.4 s, positive 89.6 s → 87.7 s), but four groups
each under a second grew 1.6–1.7×, since a reading carries about 0.3 ms of
fixed cost (the vertex, the numpy pass, the loop, the normals) against
0.09 ms for a healthy classification there. On the clock's captured cannon
pinion and hour holder the change is 3.55× in process: the holder is
placed on a 45° axis, its two gear faces are planes with 211 edges each
whose axis-aligned boxes are 29 × 29 × 41 mm slabs holding every stencil
point, so both are measured at every reading at 2.5–3.7 ms each, 7.1 ms a
reading against 0.9 ms for the holder's classifier. (Evidence: this
change's `evidence.md`, 3b.)

The ruling: two exact lower bounds join the boxes. For a planar face, the
point's distance to the face's plane; for a cylindrical face, the
magnitude of the difference between the point's distance to the cylinder's
axis and its radius; each is a lower bound on the point's distance to the
face, each is a few floating-point operations, and each is exact for the
surface the face lies in (`BRepAdaptor_Surface` gives the type, the plane
and the cylinder). The bound used for a face is the larger of its box
distance and its surface distance; faces are visited in ascending bound
exactly as before, and the stop rule is the same. A face of any other
surface type keeps its box alone. Nothing else changes: the reading, what
it may exclude, the composed orientation, the edge rule.

The acceptance is restated to what the suites measure. On the lock and the
clock, cold, each class of empty common (zero distance, under a
micrometre, positive distance) costs no more witness time than on
9 October, the three pathological groups stay settled, and no pair group
grows by more than 5 s over its 9 October time; a sub-second group growing
by a fraction of a second is recorded, not a stop. The clock run is made
this time, since the acceptance is measured on it. A class or group
outside those bounds is a stop point, reported with its numbers.

Not taken: an oriented box per face (OCCT's `Bnd_OBB`) would also thin the
tilted gear faces but is heavier to compute and no better than the plane
for a planar face; reducing the fixed cost by batching the stencil's points
through one numpy pass per solid is possible but is an optimisation of the
same instrument and is left for the measurement to call for.

## Risks / Trade-offs

- [The extrema misplaces a nearest boundary point at a genuine witness, and a
  false empty passes] → only a side read *outside* or *on the boundary*
  skips anything, and only for that point; M2, M3 and M8 found no
  disagreement; Voron-2's pairs and the Curta's re-run are the real checks.
  An unwitnessed empty was never certified.
- [Side readings cost more than a healthy classifier on many-faced solids] →
  the cheaper operand's classifier still settles every point outside it; M5's
  worst synthetic case is 1.61 s against 0.77 s; the clock and the lock
  measure the real pairs, and a group that grows is reported, not hidden.
- [A slow classifier on the operand with fewer faces] → not helped; the
  measured slow pairs (shell 32 against screw 5, and on the clock
  `collet`/`beat_screw` 36/4 and `shell`/`nut` 32/9, not yet measured) have
  the slow part on the many-faced side.
- [An UNKNOWN where none arose before] → the cheaper operand's classifier is
  asked at points where today the other operand settled the point first; an
  UNKNOWN there refuses, as any UNKNOWN does.
- [Two existing tests edited] → Decision 5; each keeps testing its rule on
  the classifier path, and the new test 4 covers the side path.

## Open Questions

1. **The Curta Type I's two refusals are not re-run in this cycle.** By the
   ball argument each recorded witness has margins of at least
   1.6 × 10⁻⁴ mm in both solids, three orders above their 10⁻⁷ mm
   tolerances, with all six neighbours inside both; a correct side reading
   there is *inside* or undecided in both solids, so the classifiers are
   asked as today, and every earlier stencil point failed on the bench and
   fails no less here. The change therefore refuses at the same two points
   unless the extrema misreads the nearest boundary point there.
   Recommendation: accept, and record in `workflow/warts.md` that the
   Curta's ±0.2 mm refusals are owed a re-run under this change when the
   pilot allows the project to be run.
2. **Should a slow classifier on the cheaper operand be covered too?** Only
   by reading sides first for both operands, at 2–7× on healthy pairs, or by
   a timing-based order. No measured pair needs it. Recommendation: no;
   record it with the clock's per-pair results if one appears there.
