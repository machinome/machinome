# Curta: a constraint between existing nested joints

Status: implemented and validated; archived in the completion commit. Not
integrated into framework main. 2026-09-20.

## Origin and outcome needed

Curta-Type-I-3x at `0db199f` retains the ones result shaft at 189.6 degrees
after entering selector 3 and turning the crank to 120 degrees. Withdrawing
the selector to zero preserves the shaft angle. A subsequent crank request
to 150 degrees is currently completed, although the ones locking pentagon
intersects the real bell by 1.080401810 mm3. The isolated closing disc first
contacts that shaft phase near 125.33515 degrees. The complete bell and the
admissible operating window must be validated before adopting a stop.

The required restraint relates `main_drive.crank.turn` and
`transmission.result.ones.turn`. Their existing mechanical and educational
ownership, stationary siblings, controls and paths must survive. A dummy
joint, a copied bank, silently banked plain ports or a globally frozen crank
would not implement this finding.

Source evidence in the project: `simulation/docs/nested-lockout-constraint-2026-09-20.md`,
`simulation/docs/result-partial-engagement-2026-09-20.md`,
`simulation/tools/cross_assembly_bound_probe.py`,
`simulation/tools/result_action_order.py`, and
`simulation/tools/result_lockout_boundary.py`.

## Reproduction on the advanced main

Framework base `0ce71cdea6cc4a2e7fd7e85dc68847daef3d34cc` includes
`running-time-drive` (ADR-133), two commits after the original investigation.
On this exact base, the project scope probe produces:

- Flat positive control: a 150-degree request is blocked at 124 degrees.
- Sibling-class reference: declaration refused because the shaft is not
  declared in the nested drive's scope.
- Public port relay: simulation construction refuses the unbanked
  `drive.shaft_phase` read.
- Ancestor child override: construction refuses the undeclared `disc`
  constructor parameter of `NestedDrive`.

Thus this is still a missing supported composition, not a regression in
cross-coordinate bounds or a requirement already served by the new feature.
The probe's `120 + phase` limit is a scope control, not a mechanical law.

Command, from the framework bench:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
PYTHONPATH="$PWD:/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x" \
/home/asa/devel/machinome-studio/.venv/bin/python \
-m simulation.tools.cross_assembly_bound_probe
```

The first invocation used the shop's symlink spelling for the project;
artifact path normalization then attempted `/mnt/home` and failed before
simulation construction. Using the actual project repository root above
completed the probe. That environmental failure is not mechanical evidence.

## Cycle identity and authority

- Shop: `/home/asa/devel/machinome-studio`, clean when opened.
- Primary framework: `/home/asa/devel/machinome-studio/machinome`, clean `main`.
- Base: `0ce71cdea6cc4a2e7fd7e85dc68847daef3d34cc`.
- Branch: `ancestor-joint-constraints`.
- Worktree: `/home/asa/devel/machinome-studio/machinome/WTs/ancestor-joint-constraints`.
- Integration target: framework `main`; recheck its base before any authorized
  fast-forward. No sprint affiliation.
- Created by `scripts/dev-env ancestor-joint-constraints setup`, slot 12.
- Pilot authorized the narrowly scoped framework cycle with Curta as empirical
  validation, explicitly warning that main had advanced. The new declaration
  and its conflict with ADR-113 still require planning ratification before
  implementation. No push, release, viewer mutation or assembly restructuring
  is authorized by this record.

The operational OpenSpec change is `ancestor-joint-constraints`. This note
records evidence, not a public API promise. The framework's existing running,
clocked and untimed meanings of a constraint remain the intended semantics;
this proposal changes where it can be stated.

## Pre-implementation baseline

On the recorded base, the existing `test_running_time_drive.py`,
`test_time_drive_corpus.py`, `test_running_stops.py`, `test_clocked_bounds.py`
and `test_joints.py` suites pass: **316 passed, 302 subtests passed, 9.57 s**.
The one warning is the existing `Symbolic.render()` legacy time-read
deprecation in the joint suite. No framework implementation was changed.

Existing running/clocked corpus and document suites also pass: **235 passed,
328 subtests passed, 12.57 s**. Their two warnings are existing legacy
`render()` driver reads. Combined baseline: **551 tests and 630 subtests**.
Primary `main` was rechecked afterward and remained clean at the recorded
base. No planning or implementation commit has been made before ratification.

Committed producer fixture SHA-256 values before implementation:

- `tests/running-corpus.json`:
  `3f3407c11f321e88d626565d97d43ff56ea63a6c1c1d19bfe8ca028cbd46eed6`
- `tests/time-drive-corpus.json`:
  `4da97d071f3d7b4764575ab1024ccfc0d1f54efe57f5821e66dd6b430a9747ed`
- `tests/clocked-corpus.json`:
  `68fe1bb9f440eec88a8a7076c8c21905262eb277ed571594b9dff0f603a84f7b`

OpenSpec generated context still mentions framework-local web-app symlinks;
that is stale against the independent viewer boundary and was not followed.
The shop's two-commit cycle overrides its generic per-increment commit note.
Strict proposal validation passes; readiness is not ratification.

## Ratification

The pilot subsequently approved the complete presented plan: “Ratify—implement,
validate and archive the cycle” (2026-09-20). Primary remained clean at
`0ce71cd` on reinspection. This authorizes implementation after the validated
planning-only commit; no integration or publication is inferred.

## Completed outcome

The ancestor declaration composes with the existing joint range using the
existing expression/span publication; no executor or viewer format changes.
Accepted ADR-134 amends ADR-113. Baseline `joints` and `simulation` specs are
synchronized. The completed cycle and detailed results are in
`openspec/changes/archive/2026-09-20-ancestor-joint-constraints/`, including
`evidence.md`.

Curta acceptance is committed at `331081436ed3d4e79890e07843f93f82e2d71f2a`.
Complete-bell native and published-mesh measurements establish a local 125.32°
free-side diagnostic stop; retained execution and actual browser pointer motion
stop there while preserving all 608 descendant paths and 25 controls. Existing
arithmetic, partial-input replay and reverser-limit regressions pass. This does
not certify other contact windows or finish the project's operating roadmap.

The cycle is standalone, based on `0ce71cd`, with planning commit `644f5b2`
and one completion commit. Framework `main` is still the intended integration
target; archival is not integration authority. The isolated worktree remains
available until integration is separately authorized and verified.
