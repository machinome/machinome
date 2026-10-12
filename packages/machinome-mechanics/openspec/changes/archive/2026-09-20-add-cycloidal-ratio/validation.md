# Fixed-ring cycloidal ratio validation

## Package

Planning commit `07dd6b4d37fa2b4e161f295ae0828381bcaff5bd`.
Tested uncommitted machinome_mechanics/gears.py SHA-256:
`808d1a07a1980d35591bd5f4b837d902caa1ac62ddddbcac6c434b06a8efb73b`.
Commands ran in the cycle worktree with workspace Python and PYTHONPATH=$PWD,
OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1.

- Red: `python -m pytest tests/test_cycloidal_ratio.py -q` failed collection
  because cycloidal_ratio was missing, before implementation.
- Green: full `python -m pytest -q` passed 156 tests and 24 subtests in
  1.82 seconds, under 768 MiB address-space / 45 CPU-second / 60 wall-second
  limits. Thirteen new tests cover measured 20/21, unwrapped reversal,
  relative mesh identities at four count pairs and nine signed inputs,
  common count scaling, uncoerced arithmetic/zero denominator, simultaneous
  actual Solid2 counts/input and deferred multi-turn input.
- `python -m sphinx -b doctest -W --keep-going docs
  /tmp/mechanics-cycloidal-doctest`: 137 examples passed.
- `python -m sphinx -q -b html -n -W --keep-going docs
  /tmp/mechanics-cycloidal-html`: passed. Both documentation commands had the
  same 768 MiB / 45 CPU-second / 60 wall-second limits.
- `python scripts/check-dist` passed wheel/sdist builds, strict metadata and
  installed numeric/symbolic smokes outside the checkout, under 768 MiB
  address-space / 90 CPU-second / 120 wall-second limits. Nothing uploaded;
  no shared environment was repointed.
- `openspec validate --all --strict`: four items passed. `git diff --check`
  passed. Docs reference and flat exports cover the new helper.

Framework and viewer were clean at package validation:
`8d2bd71171be81f13ba5dd492851ed8b3a9ababb` and
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f` respectively.

Independent Sol review reran all 13 focused tests under the memory cap and
found no substantive issue. A separate stdlib Fraction probe checked 6,144
integer count pairs and seven signed angles each: exact-formula converted
float difference was zero and relative mesh identity error stayed below 1e-9.
Review correctly noted that negative sign alone does not promise magnitude
below one (4/9 gives -1.25); the manual now makes that limit explicit rather
than implying every arithmetic count pair is a realizable speed reducer.

## Consumers

Heavy consumer checks are sequential, inside a 768 MiB physical-memory
process-tree cgroup with zero swap and bounded runtime. Positive reduction
magnitudes, independent angle oracles and one-to-one orbits remain local.

### OpenCycloid

Original main: `f9cbb6b810edb5eef35e897f9e2d0d410c4bfb47`.
Reviewed Sol commit: `156b845c40c7c973ca4f37a7cc4c44e78e708b97`.
Project record: `docs/mechanics-cycloidal-ratio.md`; retained reproduction:
`scripts/check-cycloidal-ratio`.

Four actual reduced bindings now use the helper: two disk spins and output
carrier spins in the full actuator and standalone output stage. Five identity
laws, reference phases, positive REDUCTION and controls remain unchanged.
The existing metadata gains the founded/unpublished source dependency; README
explains source installation before the project install.

The pinned stage-one STL independently supports twenty lobes: a 7,200-bin
radial probe has dominant harmonic 20 and twenty separated outer maxima.
Only empty angular bins are interpolated; populated bins containing interior
hole vertices are not repaired. This proves a count, not an exact profile,
watertightness, contact or backlash. The fixed-ring count is 21.

The probe checks seven signed actual states of both assemblies and all four
reduced bindings, then actual declared reduced and identity relations with
Solid2-driven input at six samples. Parent requested this actual-binding
coverage instead of a mere coefficient multiplication and independently reran
the final probe: PASS, 3.50 seconds, 528,652 KiB maximum RSS, under a 768 MiB
process-tree cap, zero swap and 60-second runtime cap.

Sol observed full actuator faceted 13/13 and exact 13/13, plus root build:
51.03 seconds combined, 586,668 KiB RSS. A stages-module test invocation found
zero tests and is not counted as validation. Explicit output-stage build and
fresh root OpenSCAD snapshot at 360 degrees passed in 11.64 seconds combined,
526,636 KiB RSS. The original combined test log inside _build was removed by
a subsequent build; this record preserves observed session results, not a
claim that the raw log remains. Probe and image logs remain in
`/tmp/opencycloid-ratio-probe.log` and `/tmp/opencycloid-ratio-image.log`.
Parent inspected `_build/cycloidal-ratio-full-turn.png`: coherent housing,
hub and frame, with internal contact occluded rather than visually proved.

### CycloidalDrive

Original main: `28b5963e0f78a92566542a4684bab83aa593a92b`.
Reviewed Sol commit: `c8fec93c34e82c0baaa7bce70b9cf19a025646da`.
Project record: `docs/cycloidal-ratio-verification.md`; retained reproduction:
`docs/probes/cycloidal_ratio.py`.

Six production disk/output bindings across two real assemblies use the helper
with existing measured 20/21 counts. Positive REDUCTION_RATIO, independent
test oracle, +1 input and eccentric orbits, -9-degree disk phase, +/-5 mm
eccentric centers, axes, source placements and guarded 0..7200 range remain.
Tool-only pyproject has no package metadata; no packaging was invented.
README documents the source dependency. Narrow ignored evidence paths keep
generated CAD and logs out of the commit.

The probe checks twelve actual assembly states (six per assembly) and 36
evaluated actual deferred output laws, including negative/unwrapped inputs
at the relation boundary without violating the assembly's nonnegative guard.
Parent reviewed all changed source, docs and probes, and independently reran:
PASS, 3.57 seconds, 524,740 KiB RSS under the same capped process-tree policy.
An initial agent probe imported CAD without a cgroup before that short import
was classified as heavy; it was repeated under the cap. A transient-manager
path failure and invalid direct-unittest harness are not mechanical evidence.

Full faceted testing passed assembly_integrity then reached the 768 MiB cap
at ring_engagement (10.845 seconds). The identical faceted command on an
untouched detached base reproduced that same boundary (10.337 seconds).
Full exact testing on the migrated source passed assembly_integrity, then
hit the cap at ring_engagement (37.268 seconds). No untouched-base exact run
was performed. Neither full suite is claimed green; assertions and tolerances
were not weakened. The temporary baseline worktree was removed cleanly.

Capped root build passed (14.24 seconds, 515,708 KiB RSS); fresh actuated web
capture at 1890 degrees passed (14.04 seconds, 647,248 KiB RSS). Parent read
the retained faceted/base-faceted/exact/build/capture logs and inspected
`.cache/cycloidal-ratio-driven-web.png`: assembled ring, opposed disks, shafts
and housing with no gross detachment. Hidden fine contact is not certified.
The known multi-body/nonmanifold source and overlaps remain unchanged.

### Acceptance and completion

Both consumers tested the exact helper source hash above. Framework/viewer
heads stayed clean at the recorded commits. Independent actual numeric and
deferred production-law equality, affected assembly checks, builds and fresh
image review support this focused arithmetic refactor; the bounded full-CAD
gap is explicitly retained, not promoted to a full-suite pass. Parent resolved
the count-evidence, actual-binding coverage and source-install documentation
issues before accepting both commits. No helper issue remains.

Synced only the new fixed-ring requirement; full-block comparison and strict
validation passed (four items). All seven tasks complete. Archived as
`2026-09-20-add-cycloidal-ratio` for the implementation commit. Exact local integration and post-merge
results are recorded in the next campaign ledger update. No push or release.
