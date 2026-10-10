## Why

On the current source-backed OperatingCurta graph with its counter-ones crank Bound, one mesh-free 0.1-second crank tick takes 5.95 CPU seconds. A bounded profile shows 74,048 `_PathValue.bind` calls and 1.55 million postorder visits, repeatedly rediscovering the same immutable graph order inside the existing 64-sample constraint search.

## What Changes

- Reuse each path value's immutable expression traversal order after its first successful binding while recomputing every piece's standing values.
- Preserve exact evaluation order, cuts, stops, source timing, error behavior, graph lifetime and caller state.
- Prove full Curta bank parity and measure the same bounded crank tick before and after.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `motion-expression-sharing`: repeated path evaluation retains the same expression results and reclaimable graph lifetime.

## Impact

`machinome/simulation/program.py`, expression and running tests. No public interface, search subdivisions, tolerance, dt, arithmetic operator, document format or machine law changes. Isolated standalone framework worktree from `main` `9f693bb`; the pilot's existing clean-worktree exception preserves the primary's untracked example directory. The Curta project remains read-only; the current graph is identified by `simulation/running.py` SHA-256 `588ff2a3…`, `running_parts.py` `f732d764…`, and `counter_lockout_parts.py` `f6a5d718…` before the paired measurement.
