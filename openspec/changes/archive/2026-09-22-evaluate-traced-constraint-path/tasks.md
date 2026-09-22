## 1. Pin the traced-search failure and controls

- [x] 1.1 Add red-first focused tests proving a traced bound samples through a search-local path, standing reads refresh on a later search, and the first sample remains eager.
- [x] 1.2 Add signed-zero/NaN and nontraced-prefix-replay tests that compare exact sample order and results against the existing whole-graph path.

## 2. Reuse the moving-path evaluator only where paths are determined

- [x] 2.1 Classify moving read names conservatively from actual `Motion` paths and input deltas, guarding opposite signed-zero constant endpoints.
- [x] 2.2 Bind one `_PathValue` at the first traced constraint sample and evaluate later samples through it, leaving nontraced replay and search arithmetic unchanged.

## 3. Validate the originating machine and complete the cycle

- [x] 3.1 Run focused, broad running source-timing/carry/stop suites and strict specs; obtain independent semantic review.
- [x] 3.2 Compare pinned `7586002` Curta active-stop sample argument/result bits, full 213-state bank, and controlled before/after CPU time; record exact graph/source identity.
- [x] 3.3 Sync baseline spec and prepare fully evidenced change for archive; integrate locally only after the separate clean two-commit and primary-head gate.
