## 1. Red evidence

- [x] 1.1 Add a test that spies on unrelated bank reads during path binding and proves the full-bank copy red.
- [x] 1.2 Add a generation-reset test for relevant present, absent and bound inputs, exact against uninterrupted evaluation.

## 2. Minimal retention

- [x] 2.1 Retain a copy of the bound path's relevant flat-bank inputs from its existing snapshot; remove the full-bank spread.
- [x] 2.2 Pass expression, running and source-timing conformance suites and typecheck.

## 3. Actual-machine verdict

- [x] 3.1 Compare the same 48-tick OperatingCurta document's full bank digest and elapsed CPU time to viewer `f748463`.
- [x] 3.2 Validate, sync and archive OpenSpec, document measured gain or lack of gain, commit and integrate viewer branch without publishing.
