## Why

On the current OperatingCurta graph with its result-bank restraint compiled, one bounded crank tick makes 41,029 full `GraphValue.evaluate` calls, costing 9.49 of 18.36 profiled CPU seconds. Each call walks the same immutable expression graph yet repeats node-keyed dispatch and generic numeric `min/max` face classification. This is now the largest measured Python cost in ordinary operation.

## What Changes

- Compile each `GraphValue`'s immutable postorder and child references once per value, then evaluate fresh numeric inputs in that exact order on every call.
- Use the same numeric `min/max` operations that their existing numeric math face invokes, without repeated symbolic/formula classification.
- Preserve the public two-argument `min/max` TypeError behavior in both the full-graph evaluator and the previously optimized motion-path evaluator when a malformed expression supplies another arity.
- Retain exact floating-point results, error timing, source values, graph collection, all eager chart terms and all constraint search samples; prove the current Curta bank unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `motion-expression-sharing`: Repeated full-graph evaluation keeps current numeric and error behavior while reusing immutable execution structure.

## Impact

Private Python full-graph and motion-path expression evaluators and their tests/spec only. No public expression syntax, viewer document, mechanical law, CAD geometry, dt, search tolerance, or sample-count change. Originating project: Curta-Type-I-3x `OperatingCurta` with the remaining-result-bank `Bound` compiled into its crank restraint.
