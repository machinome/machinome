## Why

`workflow/warts.md`, section "OpenAstroMount — a scenario test refused by
the exact common guard (3 October 2026)":

> Found validating the framework change `exact-engine` on a branch of the
> project. `OpenAstroMountScenarioTest.test_every_instruction_reaches_its_documented_end_state`
> fails on the project's `master` against the unmodified framework (feb23f2)
> and against the change alike, with `ExactCommonInconsistency`: the exact
> common of `housing` and `rolamento_uc206_valor_predeterminado_1` is empty
> while a point near (-2.02, 265.56, 442.98) classifies strictly inside both
> solids beyond their face tolerances. Same pair, same witness to the last
> digit before and after the change, so it is not the engine's doing. Either
> the housing and the bearing genuinely overlap at that pose, or the guard
> witnesses a false empty on a valid common. Not triaged; the project's other
> eight tests pass.

The investigation of 7 October 2026 settled it: the guard witnesses a false
empty on a valid common. On the bench at `a5d148f`, the project
`OpenAstroMount` (branch `exact-engine-validation`, `58e46cd`, which is
`master` with the 0.8 spellings) runs `machinome test --brep
--no-verdict-store simulation/mount.py` to 8 passed, 1 failed in 569 s. The
failure is `BrepCommonInconsistency` for the polar frame's bearing housing
`head.frame.mancal_f206_valor_predeterminado_1.housing` and the right
ascension body's insert
`head.right_ascension_axis.rolamento_uc206_valor_predeterminado_1`, at
`(-2.0242287706088176, 265.5583117280026, 442.97547336608244)`, the same
witness to the last digit as on 3 October.

The two vendor STEP solids, both valid, meet on two spheres of radius
31.000 mm with the same centre. The right ascension axis passes through that
centre, so at every angle the seat is a contact of zero volume and OCCT's
empty common is right. The witness lies 31.1357 mm from that centre: outside
the insert. The insert's zero-tolerance `BRepClass3d_SolidClassifier`
answers IN at that one point and OUT at its neighbours from 1e-4 mm away; on
a ring of 3600 points at the witness's radius and height it answers IN at
the witness's azimuth only. A ball of radius 0.01 mm there has no common
with the insert, and 40,000 samples of the shared bounding box and the seat
shell find no point inside both. The guard accepts the single IN because it
asks only that the point be farther from every face than that face's
tolerance (0.0999563 mm from the housing, 0.135651 mm from the insert, both
against tolerances of 1e-7 mm). That test filters a classifier that rounds
a point *on* a face, the case ADR-142's amendment of 23 September was
written for; it does not filter a classifier that is wrong away from every
face.

Reproduced on the bench at `a5d148f` without the project: two unit boxes
touch along y = 1, the Boolean is made to return empty, and the second box's
classifier answers IN at exactly one point 0.0000577 mm below the contact,
beyond every face tolerance, and truthfully everywhere else.
`intersect_shapes` raises `BrepCommonInconsistency` at
`(5.7735026918962585e-05, 0.999942264973081, 0.24994226497308103)`.

## What Changes

- **A witness must be interior in its own neighbourhood.**
  `_resolved_interior(solid, point)` reports the point's smallest distance
  to the solid's faces, or nothing when the point is within some face's
  tolerance, where it now reports `True` or `False`. A resolved IN/IN
  candidate becomes a witness only if the six points at half the smaller of
  its two distances along ±x, ±y and ±z are also classified IN, at zero
  tolerance, by the classifiers of the same two solids. No face of a solid
  lies closer to the point than that distance, so the whole ball of that
  radius has the point's true state, and a single OUT among the six proves
  a reading in the ball wrong. A candidate whose neighbours disagree is
  skipped and the search goes on, as an unresolved candidate is skipped
  today. A neighbour classified UNKNOWN refuses verification, as any
  classification does.
- **ADR-142 gains a dated amendment**, "2026-10-07: A Witness Is Interior in
  Its Neighbourhood", beside the first. It is the same decision narrowed
  again, not a new one (design.md, Decision 3).
- The `brep-engine` and `test-framework` requirements on the empty common,
  `docs/architecture.md`'s paragraph on the guard and the manual's
  `docs/reference/assertions.rst` sentence on the witness say what a witness
  now is.

Deliberately out:

- **The witness stencil is unchanged**: the same section edges, the same
  three steps and 26 directions, the same budget, the same order. Its
  measured blind spots (design.md, Open Question 2) are not this finding.
- **No tolerance, mesh verdict, volume or second Boolean** enters the
  decision. A small ball's common with each operand, the investigation's
  independent proof, is not used: it would make the witness rest on another
  OCCT Boolean, the operation the guard doubts, and would need a ball radius
  of its own.
- **Why OCCT's classifier answers IN at that one point** was not
  established and is not needed: the six neighbours expose the reading
  whatever its cause.
- **OpenAstroMount's records** owe nothing: the project's test is right to
  check the pair, and the pair does not overlap.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `brep-engine`: "An empty common is verified before it is returned" — the
  point that refuses an empty common must also have its six axis neighbours
  at half its smallest face distance classified inside the same two solids;
  one scenario added, every existing scenario carried.
- `test-framework`: "An empty B-rep common contradicted by strict shared
  interior is refused" — the same narrowing in the requirement's sentence;
  one scenario added (OpenAstroMount's seat), every existing scenario
  carried.

`brep-geometry` names the witness only as an operation that must not mutate
its inputs, which is unchanged; it is not modified.

## Impact

- Code: `machinome/engine/brep.py` only: `_resolved_interior` and
  `_false_empty_witness`, plus the docstrings of `intersect_shapes` and
  `_false_empty_witness`.
- Tests: a new `tests/test_witness_neighbourhood.py` (the false witness,
  red today; the margin `_resolved_interior` reports; a neighbour classified
  UNKNOWN; a slab of genuine shared interior still refused).
  `tests/test_brep_common_guard.py` and `tests/test_resolved_brep_witness.py`
  stay green unedited.
- Cost: six more classifications in each of the two solids for each
  resolved IN/IN candidate, which only an empty common reaches. A candidate
  that is now skipped lets the search run on through the rest of its finite
  budget where it used to stop.
- Public contract: `intersect_shapes` keeps its signature, its errors and
  its messages. An empty common that used to be refused on a lone IN
  reading is now returned.
- Records: ADR-142 amended; its index line in `docs/adrs/README.md` notes
  the amendment; `docs/architecture.md`; `docs/reference/assertions.rst`;
  one changelog bullet under `Unreleased`; the warts entry moves to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`.
- Documents, artifacts, viewer: unchanged.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change closes the OpenAstroMount finding that the campaign's investigations
(cycle 17 of the campaign table) classified as a guard defect, and is
validated in OpenAstroMount, run read-only against the bench. Voron-2,
whose thread-seat refusals are genuine OCCT false empties this guard must
keep refusing, is paused by the pilot and is not run (design.md, Proof
plan).
