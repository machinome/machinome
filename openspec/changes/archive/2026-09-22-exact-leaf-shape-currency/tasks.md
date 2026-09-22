## 1. Reproduce

- [x] 1.1 Add an isolated exact-fusion regression with an assembled exact leaf whose BREP is stale; prove it fails before the fix.

## 2. Correct

- [x] 2.1 Make the stale exact-leaf shape path render and validate native geometry rather than reading SCAD presentation state.
- [x] 2.2 Verify current-BREP reuse, exact-fusion behavior, and the originating Curta counter fixture without modifying its model or deleting its existing build cache.

## 3. Complete

- [x] 3.1 Sync the exact-geometry requirement, record verification evidence, validate and archive the OpenSpec change.
