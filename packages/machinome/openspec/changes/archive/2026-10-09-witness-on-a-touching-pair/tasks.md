Bench: `/home/asa/devel/machinome/machinome/WTs/witness-on-a-touching-pair`,
branch `witness-on-a-touching-pair`, base `d9fd98d3`. Every framework
command runs as `env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
/home/asa/devel/machinome/.venv/bin/<tool> ...`. `<change>` is
`openspec/changes/witness-on-a-touching-pair/`; its `measurements/` holds
the proposal's scripts, `side.py` the sketch of design.md Decisions 1 and 2.
`<pair>` is a directory holding the placed `shell.brep` and `screw.brep` of
wall clock 02 at `ec2a05d`: the proposal's capture is under
`/tmp/claude-1000/-home-asa-devel-machinome/b6c584a7-7bce-4b09-8a25-3732645cbf62/scratchpad/distance-tier/shell-screw/`;
if it is gone, recapture it with `workflow/ongoing/distance-tier-measurement-2026-10-09/capture.py`
(`MEASURE_PAIR=shell,screw`) from the clock's detached worktree
`/home/asa/devel/machinome/projects/3DPrintedClocks/WTs/distance-tier-ec2a05d`
with a scratch `SOLID_BUILD_DIR`. The geometry is the clock project's and is
not copied into the framework. Projects are read-only: run them with
`PYTHONDONTWRITEBYTECODE=1` and a scratch `SOLID_BUILD_DIR`, and confirm
`git status --short`, `HEAD` and `find <project> -newer <marker> -not -path
'*/.git*'` unchanged after each. The Curta Type I is not run. One test run or
project run of ours at a time; wait on a PID, never on a `pgrep -f` pattern
that matches its own command line. Every test marked RED is run and seen red,
for the reason it names, before the code that turns it green. Record every
command, its result and the load average in `<change>/evidence.md` as you go.

## 1. Baseline on the unmodified tree

- [x] 1.1 Create `evidence.md` with the bench commit, the interpreter check
  (`python -c 'import machinome; print(machinome.__file__)'` prints a path
  under the bench) and the OCP version (`cadquery-ocp` 7.8.1.1.post1).
- [x] 1.2 Run `pytest -q -p no:cacheprovider tests/test_brep_common_guard.py
  tests/test_witness_neighbourhood.py tests/test_resolved_brep_witness.py
  tests/test_engine_package.py`; record the counts (the first three: 19
  passed, 7 subtests passed).
- [x] 1.3 The captured pair, bench: `python <change>/measurements/m6_bench_screw_first.py
  <pair>` (screw first; 146.9 s and 2,490 classifications on 9 October) and
  `workflow/ongoing/distance-tier-measurement-2026-10-09/stencil.py <pair>`
  (shell first; 324 s and 2,547 on 9 October). Record time, counts, load.
- [x] 1.4 Voron-2's thread seats, bench: write `<change>/measurements/voron_thread_seats.py`,
  which builds the six nut and screw pairs of
  `projects/3D-Printers/Voron-2/simulation/test_thread_seat_contacts.py`
  (`ThreadSeatContacts.nuts`/`.screws`, each `cq_shape(part)` translated by
  `-BED_DATUM` as that test does) and calls `intersect_shapes` on each pair
  in both orders, printing the refusal's type and point; it calls nothing
  that writes the project's `CACHE` and builds no STL. Run it from the
  project at `a88fac4` with `PYTHONPATH=<bench>:<project>`; record every
  refusal and its point. If the project cannot be loaded without writing
  into it, stop and report.

## 2. Red tests

- [x] 2.1 Write `tests/test_witness_touching_pair.py` with design.md's four
  red tests: the nearest side of a point on the unit cases of
  `measurements/m8_side_cases.py`; a pin that fits its hole settled without
  the plate's classifier, both orders, counted per solid by a wrapping
  classifier (as `measurements/m7_red_sketch.py` counts); a side reading does
  not move a refusal, for overlapping boxes, the 0.4 mm slab, a pin 0.2 mm
  over its hole and a key 0.1 mm into a slot overlapping its floor, each
  with `_boolean` patched empty, comparing the refusal's point with and
  without `_nearest_side` patched to return `None`; the side reading
  excludes `LoneInsideReadingTest`'s lone reading without asking it.
- [x] 2.2 Run the file on the unmodified tree. RED: the first and third
  because `_nearest_side` does not exist; the second because the plate's
  classifier is asked 1,404 and 486 times; the fourth because the lie is
  told once. Record the output. A test red for another reason is fixed, not
  its expectation, and the reason recorded.

## 3. The change

- [x] 3.1 `machinome/engine/brep.py`: `_boundary(solid)` (a compound of the
  solid's shells and its edge-to-face map) and `_nearest_side(boundary,
  point)` returning `'out'`, `'in'`, `'on'` or `None` by design.md
  Decision 2: one extrema against the shells; a face's normal; an edge used
  by two faces or by one as its seam, same-parameter and not degenerated,
  with the faces' normals through their pcurves; `None` for a vertex, any
  other edge, a failed or empty extrema, a non-finite distance or
  tolerance, a vanishing normal, disagreeing solutions or an unclear sign.
- [x] 3.2 Same file, `_false_empty_witness`: order the operands' solids,
  classifiers and boundaries by total face count (the first on a tie); at
  each point classify the cheaper operand's solids; for a point inside one,
  read the sides of both operands' solids, drop those reading `'out'` or
  `'on'`, skip the point when an operand has none left, and classify the
  other operand's remaining solids; margins, neighbours and the returned
  point as before. The stencil, its budget and order, the section, the
  errors and their messages are unchanged.
- [x] 3.3 Docstrings of `_false_empty_witness` and `intersect_shapes` name
  the order and the side reading.
- [x] 3.4 design.md Decision 5: in `LoneInsideReadingTest` and in
  `test_rounded_in_classification_on_tangent_faces_is_not_a_witness`, patch
  `machinome.engine.brep._nearest_side` to return `None`, and nothing else.
  Confirm the first still asserts the lie was told once.

## 3b. The revision (design.md, "Revision after apply evidence")

- [x] 3b.1 `_boundary(solid)` also holds one box per face, taken as
  `face_bounds` takes them, in the face map's order.
- [x] 3b.2 `_nearest_side`: the point's distance to every face's box,
  vectorised; faces visited in ascending box distance, each by one extrema
  from the point to that face alone; stop when the next box distance is not
  below the best face distance; the nearest face's support gives the side
  as Decision 2 states. Remove the whole-shell extrema. RED first: a test
  in `tests/test_witness_touching_pair.py` that counts the faces an extrema
  is run against for a point near one face of a many-faced solid (a
  240-gon prism) and asserts it is far fewer than the face count; red
  against the whole-shell search because that count is the whole compound
  (one extrema, every face). The existing side tests of task 2.1 stay green
  unchanged.
- [x] 3b.3 Rerun 5.1 and 5.3 under the revised search and apply the
  acceptance of the Revision; 5.2 once more as well, since the instrument's
  search changed.

## 3c. The second revision (design.md, "Second revision after apply evidence")

- [x] 3c.1 `_boundary(solid)` also records, per face, its surface type and
  the plane (a point and unit normal) or cylinder (axis point, unit axis
  direction, radius) it lies in, from `BRepAdaptor_Surface`; other types
  carry no surface bound.
- [x] 3c.2 `_nearest_side`: each face's bound is the larger of its box
  distance and its surface distance (plane: |(p − o)·n|; cylinder:
  | ‖(p − a) − ((p − a)·d) d‖ − r |), computed in the same vectorised pass;
  the visit order and the stop rule are unchanged. RED first: a test in
  `tests/test_witness_touching_pair.py` with a 240-gon prism rotated 45°
  about an axis in its end-face plane, so that its two end faces' boxes are
  slabs holding a point 0.01 mm outside the middle of a side face; count
  the faces measured by extrema and assert the two end faces are not among
  them (red under the box-only search, which measures both at every
  reading; the measured count there is recorded in evidence).
- [x] 3c.3 Rerun 5.1, 5.2 and 5.3, the lock and then the clock, and apply
  the restated acceptance of the second Revision.

## 3d. After the acceptance ruling (design.md, "Acceptance ruling after the third apply")

- [x] 3d.1 No further change to the search. The records of section 6
  carry the final numbers of both projects, the two gear-side groups with
  theirs, and the ruling's reason.

## 4. Green

- [x] 4.1 Run `tests/test_witness_touching_pair.py`, the three guard files,
  `tests/test_engine_package.py`, `tests/test_verdict_store.py` and
  `tests/test_brep_geometry.py`; all green. Record.
- [x] 4.2 `flake8 --max-line-length=89` on `machinome/engine/brep.py` and
  the new test file; record anything the file already carried.

## 5. Validation outside the repository

- [x] 5.1 The captured pair, changed bench: both scripts of 1.3. Expect no
  candidate and no classification of the shell; record time, counts, load.
- [x] 5.2 Voron-2: the script of 1.4 against the changed bench; every pair
  refused as at 1.4, at the same point. A difference stops the cycle and
  goes to the pilot.
- [x] 5.3 The combination safe lock at `8f185f6` and wall clock 02's
  detached worktree at `ec2a05d`, cold, with a scratch build directory:
  `workflow/ongoing/distance-tier-measurement-2026-10-09/measure.py test
  <model> --brep --no-verdict-store` as on 9 October, one at a time. Record
  the suites' results (unchanged from 9 October) and the witness time on
  zero- and tiny-distance empties per pair group against the 9 October
  records (`shell`/`screw`, `collet`/`beat_screw`, `shell`/`nut`,
  `arbor`/`hour_holder`, `cannon_pinion`/`hour_holder` and the lock's
  `lock_pin`/`cam` named). A group whose witness time grows is reported
  with its numbers.
- [x] 5.4 OpenAstroMount, if the host allows: the archived `astro_pair.py`
  (in `openspec/changes/archive/2026-10-07-a-witness-is-interior-in-its-neighbourhood/evidence.md`)
  at the Target pose: the empty common returned; record the time.
- [x] 5.5 Record in evidence that the Curta was not run, and why
  (design.md, Open Question 1).

## 6. Records

- [x] 6.1 `docs/adrs/TEST-FRAMEWORK/ADR-142-a-shared-interior-witness-refuses-an-empty-exact-common.md`:
  add "## Amendment — <date>: A Point's Side Is Read From Its Nearest
  Boundary Before a Slower Classifier" after the 2026-10-09 amendment: the
  shell and screw, the order, the side reading and why it is sound, that a
  side reading never makes a point count, the synthetic refusals and
  Voron-2's kept, the Curta's re-run owed, link to this change's archive.
  `docs/adrs/README.md`: ADR-142's index line lists every amendment date,
  2026-10-09 included.
- [x] 6.2 `docs/architecture.md`, the guard paragraph: the cheaper operand
  first, and a point whose nearest boundary shows it outside either solid is
  not put to the other's classifier.
- [x] 6.3 Read `/home/asa/devel/machinome/skills/write-the-manual/SKILL.md`;
  then `docs/reference/assertions.rst`, the `intersect_shapes` sentence on
  the witness: one clause, that a point whose nearest boundary shows it
  outside either shape is not a witness. Nothing added beyond it.
- [x] 6.4 `docs/project/changelog.rst`, one bullet under `Unreleased`: a
  touching pair no longer exhausts the empty-common witness; the cheaper
  part is classified first and a point's side of the other is read from its
  nearest boundary; wall clock 02's weight shell against its screw with the
  measured before and after; refusals unchanged
  (witness-on-a-touching-pair).
- [x] 6.5 `workflow/warts.md`: mark the bullet "A touching pair can exhaust
  the witness" fixed by this change with the measured result; add to the
  shallow-dent finding that a 3.75 mm ball sunk 0.5 and 1.0 mm into a block
  is missed too (design.md, M4); record that the Curta's ±0.2 mm refusals
  are owed a re-run under this change; record any pair group of 5.3 whose
  witness time grew.

## 7. Sync, archive, final checks

- [x] 7.1 Sync the delta specs into `openspec/specs/brep-engine/spec.md` and
  `openspec/specs/test-framework/spec.md`.
- [x] 7.2 Archive the change; `openspec validate --all` passes.
- [ ] 7.3 The focused tests of 4.1 once more, then the full suite once,
  alone (`pytest -q -p no:cacheprovider` at the bench root); record counts
  and wall time.
- [x] 7.4 Leave everything uncommitted and report.
