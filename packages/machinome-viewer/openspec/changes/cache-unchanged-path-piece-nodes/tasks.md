## 1. Red evidence

- [ ] 1.1 Add tests for equal rebind, changed branch cone, input presence and signed-zero/NaN, binding dependency, and `at` isolation; demonstrate the relevant old-work assertion red.

## 2. Incremental bind

- [ ] 2.1 Retain bound node values and bank-name snapshot, propagate dirtiness in the original postorder, and evaluate only affected nodes.
- [ ] 2.2 Pass expression tests and the running conformance corpus without changing results or fallback behavior.

## 3. Actual-machine verification

- [ ] 3.1 Remeasure the pinned OperatingCurta export with the same dt and compare bank digest, work count and CPU time.
- [ ] 3.2 Build and exercise the viewer in Chromium for physical selector, crank, readout and replay; record remaining limitations honestly.
- [ ] 3.3 Validate OpenSpec, sync/archive the change, update changelog and findings, commit and integrate the viewer branch without publishing.
