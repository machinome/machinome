## 1. Exactness proofs, red first

- [x] 1.1 Add focused red tests for repeated successful Bound searches: unchanged standing work falls, moving first-sample work remains, and sample/result bits match the uncached path.
- [x] 1.2 Add red guards for changed/present/missing/signed-zero/nonfinite inputs, unsupported and throwing expressions, moving-set change, generation reset, restore/reset, and two independent runs.

## 2. Bounded implementation

- [x] 2.1 Reuse one successful path per constraint per run only under exact finite scope, generation and moving-set gates; clear on restore/reset and failure.
- [x] 2.2 Re-evaluate the moving cone in original postorder at the first sample of a reused search, leaving later `at` samples and generic fallback untouched.

## 3. Project and distribution proof

- [x] 3.1 Run focused and broader Vitest/typecheck/Python suites, including source timing and snapshot/replay.
- [x] 3.2 Compare paired CPU15 first-48 default-tick measurements and exact 213-bank/ordered Bound samples on a pinned frozen OperatingCurta export; reject the cache if benefit is not material.
- [x] 3.3 Validate current production Curta export with the changed bundle, including a real browser control/terminal-state check; record caveats honestly.
- [x] 3.4 Sync viewer-owned main specs, record the architecture amendment and final evidence, build the candidate bundle, and validate it before archiving. Integrate the archived cycle only after revalidation against current viewer main.
