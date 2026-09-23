## 1. Pin the refusal and red tests

- [ ] 1.1 Record the clean viewer base, actual v13 Curta manifest and failed hosted report hashes, the two controls' exact selected joints, and the current API-26 load refusal without changing the project.
- [ ] 1.2 Add synthetic load tests for two valid Turns on one part with ancestor/descendant joints, and for same-joint duplicates with differing labels/inputs; run them red against the current `(kind,part)` validation.
- [ ] 1.3 Add a two-Turn selected-handle gesture test: two distinct accessible handles and gesture points, undecided body drag inert, each chosen handle sending only its own input. Record its pre-change result, then add a red hover-crossing test matching the actual Curta failure where a different controlled part lies behind the handle.

## 2. Implement the narrow viewer correction

- [ ] 2.1 Change the Turn claim to exact `(kind,part,joint)` paths after existing per-control validation; keep Button/Slide duplicate behavior, and make a duplicate Turn refusal name both declarations, the part and the shared joint.
- [ ] 2.2 Keep the existing selected-handle and per-joint geometry path. Suppress scene-hover recast only while a pointer moves over a current, owned, visible selected handle; preserve ordinary hover off it and hidden/stale/foreign handle refusal.
- [ ] 2.3 Raise only `machinomeViewerApi` to 27 in its single declaration; leave document versions 1–13, the v13 wire, mount/run methods and package release version unchanged.

## 3. Document the tested source capability

- [ ] 3.1 Add an Unreleased changelog entry for API 27 and distinct selected-joint Turn handles, without rewriting the recorded 0.7.0/API-26 release or implying a push/upload.
- [ ] 3.2 Keep the manual home/README historical release facts at API 26, distinguish current-source API 27 in compatibility and the controls reference, and update the source `describe` example and documentation structure tests accordingly.
- [ ] 3.3 Build the manual strictly, run the documentation/browser check, and inspect the changed HTML as a reader; do not insert an originating project or workspace path into reader pages.

## 4. Prove the actual trial and preserve regressions

- [ ] 4.1 Run focused control/parser/surface tests, typecheck, full widget suite, and relevant Python tests; record exact counts and any environment skips or failures.
- [ ] 4.2 Build a fresh candidate bundle and load the pinned actual Curta export through the public hosted mount. Assert API 27, all 26 controls, both named handles and distinct gesture points; use real pointer gestures to prove each requested input and unchanged unrelated controls, including an undecided body-drag negative. Inspect pixels and record bundle/document hashes. Coordinate the browser slot with root.
- [ ] 4.3 Check the prior one-control, Button+Turn, Turn+Slide and same-joint-duplicate fixtures, and run an old API-26 bundle refusal control so the compatibility boundary is honest.

## 5. Close the viewer-owned cycle

- [ ] 5.1 Record red/green results and actual Curta evidence in the change, sync both accepted delta specs, strict-validate and archive the change.
- [ ] 5.2 Commit only viewer-owned implementation, docs, tests and archived record after root's final evidence review; reconcile with moving viewer main and rerun relevant merged-state gates before local integration. Do not push or publish.
