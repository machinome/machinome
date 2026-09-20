## 1. Package

- [x] 1.1 Prove new reference-value and symbolic tests fail before implementation.
- [x] 1.2 Implement and export rolling_travel; document conventions and examples.
- [x] 1.3 Pass the complete package suite and manual checks.

## 2. Empirical consumers

- [x] 2.1 Sol agent migrates Dragon R1, validates motion and records issues.
- [x] 2.2 Sol agent migrates Thor, validates motion and records issues.
- [x] 2.3 Review consumer diffs and exact evidence; resolve any helper regressions.
- [x] 2.4 Audit and migrate other natural forward-travel consumers, recording exclusions.

## 3. Completion

- [x] 3.1 Record tested consumer commits and package results; sync and validate specs.
- [x] 3.2 Archive the complete implementation record for local integration.

Integration is an external Git gate: verify this archive and all eight consumer
commits on their original branches before beginning the next helper. Its result
is carried by the campaign record at the next cycle's planning commit.
