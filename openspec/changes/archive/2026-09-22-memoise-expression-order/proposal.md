## Why

After class port memoization, one mesh-free OperatingCurta crank tick still costs 6.87 CPU seconds. A bounded cProfile attributes 7.41 profiled seconds to 41,029 `GraphValue.evaluate` calls and 7.94 seconds to repeated postorder traversals within the unchanged 64-sample constraint search. The graph is immutable while input values change.

## What Changes

- Reuse a graph value's immutable evaluation order across numeric evaluations while recomputing every node's value from the current inputs.
- Preserve exact operator order, error behavior, graph sharing, and reclamation of discarded machine expressions.
- Prove a bounded Curta crank tick's full bank remains identical and measure its CPU cost.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `motion-expression-sharing`: repeated numerical evaluation of a shared expression preserves semantics and does not retain discarded graphs.

## Impact

`machinome/scad_expression.py`, expression and running simulation tests, and the Curta caller. No syntax, serialized format, sampling count, tolerance, stop, carry, or source-timing law changes. Standalone isolated framework worktree from `main` `6ff9806`; the pilot's clean-worktree exception preserves the primary's pre-existing untracked `docs/examples/v8-engine/`.
