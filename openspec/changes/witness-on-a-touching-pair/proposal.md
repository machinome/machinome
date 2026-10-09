## Why

`workflow/warts.md`, "The overlap question is asked of a Boolean that is
only needed at zero distance", bullet "A touching pair can exhaust the
witness", measured on 9 October 2026 on framework `main`: after an empty
common, ADR-142's witness walks a stencil of 1,872 points and classifies
each at zero tolerance against the first operand's solids, then the
second's. Wall clock 02's weight shell against its screw is a genuinely
touching pair, and on it the witness costs 324 s and never reaches a
candidate: 2,547 classifications, 1,872 of them on the shell, whose
classifier answers in 0.6 ms at its centre and in 190–300 ms at every
stencil point. On the clock's cold suite the witness spends 583 s of its
948 s on the 115 touching empties. None of that time is spent on shared
interior: on a touching pair every stencil point is outside one of the two
solids, and the search pays the slower classifier to learn it.

## What Changes

- **The cheaper operand is asked first.** At each stencil point the
  classifiers of the operand with fewer boundary faces are consulted first
  (the first operand when the counts are equal), so a point outside it
  costs nothing more. On the captured pair that is the screw, 5 faces
  against the shell's 32.
- **A point's side is read from its nearest boundary point before the
  other operand's classifier is asked.** For a point the first classifier
  puts inside, the engine measures the point's nearest boundary point in
  each solid of both operands with one extrema against the solid's shells.
  When that boundary point lies inside a face, or inside an edge where two
  faces meet (a seam counts as one face on both sides), the face normals
  there say whether the point is outside or inside, and a point within the
  native tolerance of a face there is on the boundary. A solid that reads
  outside or on the boundary holds no candidate at that point; when no
  solid of an operand remains, the point is skipped and the classifiers of
  the operand with more faces are not consulted there. A boundary point at a
  vertex, a non-manifold edge or an unclear sign leaves the side undecided,
  and the classifier is asked as today.
- **What refuses is unchanged.** A side reading never makes a point count:
  a witness is still a point classified inside a solid of each operand at
  zero tolerance, resolved beyond every face tolerance, whose six
  neighbours are classified inside both. The stencil, its budget and its
  order, the errors and their messages are as before.
- **ADR-142 gains a dated amendment**, its fourth: the same decision with a
  cheaper route to "outside", not a new one (design.md, Decision 4).
- The `brep-engine` and `test-framework` requirements on the empty common,
  `docs/architecture.md`'s guard paragraph and the manual's
  `docs/reference/assertions.rst` sentence on the witness say that a point
  whose nearest boundary shows it outside either solid is not a candidate.

Deliberately out:

- **The stencil.** Coarse-first walking, an early stop, fewer directions
  or steps, and a cap on classifications were each measured or reasoned
  and rejected (design.md, Decision 3): each saves time only by searching
  less, and the step at which the Curta's witnesses are found is not
  recorded. The shallow-sphere blind spot is untouched.
- **A slow classifier on the operand with fewer faces** is not helped:
  that operand is still asked at every stencil point.
- **The section's own cost**, which is most of the witness's time on
  empties at positive distance, and the contact-semantics decision, both
  the distance-tier finding's.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `brep-engine`: "An empty common is verified before it is returned" — the
  operand with fewer faces is classified first, and a point whose nearest
  boundary point shows it outside, or on the boundary of, every solid of
  either operand is skipped without consulting the other operand's
  classifiers; two scenarios added, every existing scenario carried.
- `test-framework`: "An empty B-rep common contradicted by strict shared
  interior is refused" — a point whose nearest boundary shows it outside
  either solid does not count; one scenario added (wall clock 02's weight
  shell on its screw), every existing scenario carried.

## Impact

- Code: `machinome/engine/brep.py` only: one private helper reading a
  point's side of a solid from its nearest boundary point, and
  `_false_empty_witness`'s order of instruments; the docstrings of
  `_false_empty_witness` and `intersect_shapes`. `_resolved_interior`, the
  neighbour check, the section and the stencil are unchanged.
- Tests: a new `tests/test_witness_touching_pair.py`, red today (design.md,
  Proof plan). Two existing tests that inject a classifier error at a point
  the side reading now excludes (`LoneInsideReadingTest` and
  `test_rounded_in_classification_on_tangent_faces_is_not_a_witness`) gain
  one patch making every side undecided, so they keep exercising the rule
  they were written for; the rest of the three guard files stay unedited.
- Cost: measured on the captured shell and screw, 324 s and 2,547
  classifications become about 1.5 s, 1,872 classifications of the screw
  and none of the shell. On healthy synthetic touching pairs it runs
  between 0.9× and 2.2× today's time (design.md, Context); the clock's and
  the lock's cold runs measure the real ones.
- Behaviour: an empty common that is refused today is refused at the same
  point, unless the side reading excludes that point, which requires
  OCCT's extrema to misplace the nearest boundary point. A classifier of the
  operand with fewer faces may now be asked at a point where today it was
  not, so an UNKNOWN there can refuse where today it would not have been
  asked; the classifiers of the operand with more faces are asked at fewer
  points.
- Public contract: `intersect_shapes` keeps its signature, errors and
  messages.
- Records: ADR-142 amended, its index line noting the amendment;
  `docs/architecture.md`; `docs/reference/assertions.rst`; one changelog
  bullet under `Unreleased`; the warts bullet marked fixed.
- Documents, artifacts, viewer: unchanged.

## Authorization

The pilot's request to propose this cycle (9 October 2026), carried by the
orchestrator: propose, do not implement or commit; a reviewer reads the
artifacts before anything is committed. ADR-142 chose the stencil and its
classifiers, so the amendment is the pilot's to ratify. Validation available
in this cycle: the repository's synthetic tests, the captured shell and
screw, and Voron-2's thread seats, which the reviewer may run read-only.
The Curta Type I cannot be run in this cycle; its re-run is owed (design.md,
Open Question 1).

Reviewed and ratified on 9 October 2026 by the orchestrator's adversarial
review, under the pilot's standing discipline for this work (an Opus agent
proposes and applies; the orchestrator reviews and gates each commit) and
the pilot's goal of the same day, to clear the warts opened since
fix-warts-3. Two review notes bind the apply: the outward normal of a face
is taken from the face as explored from its solid, so the composed
orientation of solid, shell and face applies, and a test covers a solid
whose shell carries a reversed orientation if one can be built cheaply;
and the validation runs of tasks 1.3, 1.4, 5.1 to 5.4 are one at a time,
the lock before the clock.
