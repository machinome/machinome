## 1. Red evidence

- [x] 1.1 Add tests for equal rebind, changed branch cone, input presence and signed-zero/NaN, binding dependency, and `at` isolation; demonstrate the relevant old-work assertion red.

## 2. Incremental bind

- [x] 2.1 Retain bound node values and bank-name snapshot, propagate dirtiness in the original postorder, and evaluate only affected nodes.
- [x] 2.2 Pass expression tests and the running conformance corpus without changing results or fallback behavior.

## 3. Actual-machine verification

- [x] 3.1 Remeasure the pinned OperatingCurta export with the same dt and compare bank digest, work count and CPU time.
- [x] 3.2 Build and exercise the viewer in Chromium for physical selector and crank; attempt visible readout and replay, recording the bounded-run limitation honestly if the turn cannot finish.
- [x] 3.3 Validate OpenSpec, sync/archive the change, update changelog and findings, commit and integrate the viewer branch without publishing.
