## 1. Red-first numerical and public-path witnesses

- [x] 1.1 Reproduce the exact pure Z -95.6-degree cos/sin matrix in a focused `_axis_angle` regression; prove phantom X/Y components and reconstructed/physical-basis error on the recorded base without CAD or caller edits.
- [x] 1.2 Add a public mate rest-placement witness independently comparing emitted operations and transformed basis points to the hand-written principal rotation. Confirm it fails before implementation at unchanged snap/tolerances.
- [x] 1.3 Add signed principal rotations for X/Y/Z above 90 degrees and around the 90-degree branch, identity omission and snap-boundary checks; compare reconstructed matrices rather than asserting an arbitrary half-turn axis sign.
- [x] 1.4 Add proper oblique rotations with genuine small positive/mixed-sign axis components above 1e-9, including near/exact half-turns. Pin matrix reconstruction and component retention; preserve existing equal-component half-turn fixtures and serialized symmetry.

## 2. Narrow stable conversion

- [x] 2.1 Stabilize nondominant component recovery in `_axis_angle`, retaining atan2 angle recovery and current identity/snap behavior. Prefer dominant-component diagonal recovery plus symmetric off-diagonal terms or an equivalently narrow well-conditioned approach; do not enlarge snap or loosen tests.
- [x] 2.2 Preserve deterministic exact-half-turn behavior and symmetric equal components while retaining genuine small components. Verify all red witnesses and existing mate rest-placement tests pass without API, operation-order, translation, binding or serialization-schema changes.

## 3. Verification and caller evidence

- [x] 3.1 Run focused numerical, complete mate and relevant frame/joint/operation regressions against this worktree with the workspace venv; record commands, red/green results and any independently reproduced baseline failures. No broad suite is required merely for planning.
- [x] 3.2 Coordinate the root-owned Curta caller rerun using the unchanged selector candidate/test and tolerances. Record framework/caller content and that both structural and physical-basis/state/replay comparisons pass; do not edit caller-owned files or claim a fit failure/fix from numerical evidence alone.
- [x] 3.3 Present implementation and compatibility evidence for root adversarial review before synchronization/archive. Stop and present any proposed interface or tolerance change to the pilot first.

## 4. Proportional completion record

- [x] 4.1 Record the wart's verified resolution and archive the provisional intent note under workflow conventions after accepted implementation. Record nonarchitectural ADR disposition; create no gratuitous ADR or unrelated documentation cleanup.
- [x] 4.2 After root review, use supported OpenSpec sync/archive and strict validation for the completed record under root direction. No intermediate implementation commits, proposer commit/integration/cleanup, Studio/viewer work or push is implied.
