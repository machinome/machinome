# Harmonic cam lift validation

## Package

Planning commit: `8d40d0a6b23490a715187f81e4e9b2f3bfc4ad43`.
Tested uncommitted `machinome_mechanics/cams.py` SHA-256:
`ee7e70d16cad6e6403743d58d86af78d2b97a58d5fc3028d1fd75f64518293c5`.
Commands use workspace Python and PYTHONPATH=$PWD from this worktree.

- Missing-helper collection ImportError observed before implementation.
- Full `python -m pytest -q`: 171 passed, 24 subtests, 1.75 seconds;
  768 MiB address-space, 45 CPU seconds and 60 wall seconds, BLAS/OMP threads1.
  Fifteen new cases exercise full stroke, four timing pairs against independent
  piecewise oracle across signed turns and boundary neighborhoods, intentional
  45/80-degree returns, linear signed lift, zero/unvalidated spans, and actual
  Solid2 angle/lift/timing operands. The first implemented run exposed missing
  min/max mappings in the test evaluator; those standard primitives are now
  mapped without altering production expression behavior or expected values.
- `python -m sphinx -b doctest -W --keep-going docs
  /tmp/mechanics-harmonic-doctest`: 143 examples passed. An initial command
  omitted thread limits and hit its address-space cap importing trimesh in
  pre-existing examples. Repeated with BLAS/OMP threads1 in a 768 MiB
  process-tree cgroup, zero swap and 60-second runtime: PASS, 1.72 seconds,
  141,104 KiB process maximum RSS. The cap was not raised.
- `python -m sphinx -q -b html -n -W --keep-going docs
  /tmp/mechanics-harmonic-html`: passed under 768 MiB address-space and
  45 CPU/60 wall-second limits with threads1.
- `python scripts/check-dist`: wheel/sdist builds, strict metadata and installed
  numeric/deferred smokes outside the checkout passed; 768 MiB address-space,
  90 CPU/120 wall-second limits, threads1. Nothing uploaded or repointed.
- `openspec validate --all --strict`: four items pass. `git diff --check` passes.

Framework/viewer remained clean at
`8d2bd71171be81f13ba5dd492851ed8b3a9ababb` and
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f`.

Independent read-only Sol review found no substantive issue. All fifteen
focused tests repeated under the 768 MiB address-space/thread limits in
0.24 seconds. A separate piecewise-oracle probe checked 60,522 evaluations
over turns +/-100 and additional 1/1, 359/1 and fractional 17.5/81.25 spans;
maximum difference was 7.11e-15. Boundary neighborhoods retained the expected
base/peak/base continuity. Very large floating phase precision is explicitly
documented, not promised away.

## Consumers

### Leonardo cam hammer

Base main `87b76494fe9509b82b72468e9448a2949c908d42`; final reviewed
consumer commit `5349757c3b358d20c147f0dc764ab1ed998dccca`. Project record:
`models/cam_hammer/docs/harmonic-cam-lift.md`.

The local adapter explicitly retains 240-degree rise, default 80-degree return
and separate 45-degree profile return. Independent test_model.py is unchanged;
the existing dependency declaration is retained. Parent reviewed the adapter,
probe and record. At parent's request the legacy oracle retains the exact
former square-root clipping algebra, and the deferred probe asserts its
selected relation really drives the lever swing. A removed still-needed sin
import and missing evaluator cos were caught during probe development and
fixed before acceptance; no package change was necessary.

Final probe passes 168 numeric adapter comparisons, 21 actual bound-law
deferred values and all 2,160 profile points at lifts 16/18/20. Parent reran
it independently in a 768 MiB process-tree cgroup, zero swap, 60 seconds,
threads1: PASS 3.78 seconds, maximum RSS 525,072 KiB.

Full faceted CAD passed six methods including 37 assembly poses, cam contact,
ground/anvil seating, measured intermediate lift, nine-pose shaft capture and
guards, then hit the 768 MiB cap at the release-gap method (15.192 seconds).
Exact passed 37 assembly samples and cam contact, then hit the same cap at
the ground check (25.864 seconds). These are incomplete suites, with no
untouched-base capped rerun; historic uncapped results are context only.
Neither tolerances nor assertions were weakened. Exact sampled profile parity
and bound-motion equality cover the refactor despite the bounded broad-suite gap.

Build passed in 10.05 seconds, RSS 515,880 KiB. Fresh OpenSCAD lift/release
images passed in 5.97/6.04 seconds, RSS 668,904/669,352 KiB. Parent read raw
logs and viewed both images: assembled pivots/frame, raised head and visible
cam/shoe release gap. Pixels alone do not certify precise contact. Logs/images
are retained under ignored `_evidence/harmonic-cam-lift/`, outside rebuilt CAD.

### Deepseek Leonardo hydraulic sawmill

Base main `6ae7aa8429a60a11ce86f45794fa2d93688af55d`; reviewed Sol commit
`15fdf591411c20a7f88138d4b9c5bb5d1d1b2800`.
Project record: `docs/harmonic-cam-lift.md`.

Only the feed-lift adapter changes production arithmetic, passing 2*FEED_THROW
as full peak lift. Positive follower axis, negative pawl swing, ratchet stroke,
fourth-turn reset, guards and independent tests remain. Numeric cam-profile
construction is unchanged. The tool-only project retains no invented package
metadata; README now explains its founded/unpublished source dependency.

Retained `scripts/check-harmonic-cam-lift` checks sixteen actual assembly states,
including seams and reset, against independent old lift/swing/ratchet laws;
seven signed/unwrapped actual bound-follower deferred samples agree within
1e-10. Parent corrected missing evaluator primitive mappings before execution,
reviewed the complete final probe, and reran it independently in the same
768 MiB/zero-swap/60-second cgroup: PASS 3.53 seconds, RSS 525,492 KiB.

Sequential capped CAD gates all passed: focused exact feed 5/5 (3.49 seconds,
RSS 527,356 KiB), root exact 10/10 (11.68 seconds, RSS 607,952 KiB), root build
plus fresh OpenSCAD image (11.36 seconds, RSS 525,760 KiB). Parent read retained
`/tmp/leonardo-harmonic-cam-{feed-test,exact,build-image}.log` and inspected
`_build/harmonic-cam-lift-quarter-rise.png` at normalized time .0625 / wheel
90 degrees: wheel, sash/rod, bed and log carriage coherently assembled. The
partly occluded follower's precise lift is supplied by the binding probe and
tests, not inferred from the overview pixels.

Both consumers tested the exact helper SHA above; dependency heads remained
clean/stable. No helper issue remains. Local integration is not yet claimed;
guarded fast-forwards and post-merge checks follow the completed-cycle commit.

Baseline sync added only the harmonic-lift requirement. Its complete block
matches the delta; strict validation passed all four items. All seven tasks
complete; archive `2026-09-20-add-harmonic-cam-lift` retains the full record.
