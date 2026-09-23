## Why

The Curta Type I `OperatingCurta` Follow motion still spends substantial time rebuilding identical folded law graphs at the same standing and jump-branch values. On its unchanged 0→90° five-tick command, 7,240 folds yielded only 1,862 distinct bit-exact root/substitution states; a diagnostic 256-entry memo reduced process CPU from 19.744 to 16.423 seconds with the same 214-coordinate bank digest. This is measured repeated preparation, not a reason to alter sampling or mechanics.

## What Changes

- Reuse only successfully folded immutable graph results for an identical root and exact finite builtin-numeric substitution during one running tick.
- Bound the private working set to 256 entries and discard it after the tick, including failure.
- Preserve the original fold path for custom/nonfinite/uncertain values, and all graph evaluation, first-error, landing, stop and bank behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: permit equivalent successful runtime law folds to share their immutable structure without changing any motion or Bound observation.

## Impact

Private `machinome/simulation/program.py` and `run.py` fold/tick machinery, focused tests and performance evidence. No public API, viewer change, document version, sampling parameter or project source change.
