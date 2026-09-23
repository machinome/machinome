## Why

The Curta's running controls can report a requested move to an inclusive stop as blocked even when the requested native target is exactly the bound. A minimal public running document reproduces it: after reaching `-4.942499999999999`, `move(to=3.9075)` reconstructs `start + (target-start)` as `3.9075000000000006`, records a false upper stop at fraction 1, and leaves the input one ULP beyond its target. The originating Curta request actually asks for `to=-4.9425` first; its present one-ULP wrong landing must also be corrected, so old incorrect bank bits are not a new golden oracle. The framework producer has the same defect; this viewer cycle is the paired reader correction.

## What Changes

- Preserve the exact converted native endpoint of an absolute running `move(to=...)` through final admission and endpoint propagation, so an unobstructed command lands at that endpoint rather than a reconstructed sum.
- Judge existing numeric and dynamic Bounds against the same endpoint state that will be committed. An actual outward excursion remains blocked at the existing located fraction; no epsilon, snap of a blocked partial move, relaxed stop, or altered sampling is introduced.
- Keep relative `move(by=...)`, rates, intermediate tick paths, request reporting, snapshot and replay behavior unchanged. Add red-first one-ULP endpoint, genuine overshoot, and paired producer-document regressions.

## Capabilities

### New Capabilities

- `running-target-endpoint`: Exact absolute-target landing and inclusive-bound judgment for running `move(to=...)` requests.

### Modified Capabilities

None. The existing running request and physical-bound requirements remain in force; this change pins and repairs their endpoint interaction.

## Impact

The change is internal to the viewer's running command/admission and propagation path (`widget/src/run/`). The host mount API, document schema and declared viewer API remain unchanged. The originating Curta browser report is `projects/Calculators/Curta-Type-I-3x/_build_checks/reverser-asymmetric-browser-da9808a-02.json`; paired framework evidence and its final fix will be checked before viewer implementation is accepted. No project source, CAD geometry or bound declaration changes.
