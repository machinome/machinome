## Why

The committed OperatingCurta's expanded result-bank bound makes a declared two-second crank turn take minutes in the viewer. On its pinned export after the expression-capacity fix, 34.3 seconds of a 53.8-second profiled first 48 crank ticks lie under traced constraint search; that search repeatedly evaluates a large bound graph even though only a small subset of its reads moves.

## What Changes

- Reuse a search-local bound evaluation across samples of a determined constraint path, computing only quantities affected by movement after the first sample.
- Keep the existing sample fractions, crossing tests, bisection rounds, endpoint arithmetic, fallback for unsupported expression shapes, nontraced prefix replay, event records and 213-coordinate results exactly as they are.
- Prove sample-by-sample IEEE-754 and full-bank parity on the current OperatingCurta export, plus viewer-owned red-first tests for moving versus standing bound work and fallback/error cases. Record a same-export before/after timing without claiming the declared two seconds is met unless measured.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: a traced constraint search SHALL avoid recomputing standing bound quantities on every sample while preserving the running machine's exact outcomes.

## Impact

Only the independent viewer's running constraint evaluator and its tests, OpenSpec and evidence change. No framework, project source, host API, document version, sampling limit or published package interface changes. The originating machine is committed OperatingCurta project `7586002`, pinned export SHA256 `c36432b1080387eeb40234532f516a9ae05f8a9822fd3f47f44ffbbb42f889d1`.
