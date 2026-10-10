## Context

`GraphValue.evaluate(inputs)` walks its immutable `ExpressionNode` DAG in postorder on every numeric evaluation, then evaluates nodes into a fresh per-call values map. The Curta's running constraint search calls it 41,029 times in one bounded crank tick, repeatedly traversing the same graphs while only the input mapping changes. Postorder reached 3.49 million node visits in that profile. The expression-sharing spec already requires order-preserving arithmetic and reclamation of discarded graphs.

## Goals / Non-Goals

**Goals:** Reuse the DAG's traversal order for one `GraphValue` instance, reevaluate every node with current inputs, preserve the same exception timing and observable float results, and avoid a process-global graph registry.

**Non-Goals:** Change the 64-sample constraint search, path partitioning, operator implementations, expression serialization, source timing, carry or stop semantics.

## Decisions

Compute the tuple of `postorder([root])` lazily on first numeric evaluation and retain it on the `GraphValue` instance. The root and its `ExpressionNode` children are frozen, so the tuple stays valid; a discarded value releases its tuple and graph. Each evaluation still creates its own `values` dictionary and invokes the same operator dispatch in the same order. Do not cache numeric results, since inputs, branch values and error conditions change.

Keep the existing local imports and operator mapping initially, to narrow the semantic change to traversal reuse. Test a shared DAG's repeated evaluation under different inputs, missing-input errors, degree math and exact output. A red test counts actual postorder walks on the same value. Compare the same mesh-free Curta crank tick on the same base before and after, including the exact full bank digest and process CPU time.

## Risks / Trade-offs

- A cached tuple retains each reachable graph node for the value's lifetime. The value already owns the root and its reachable nodes; the tuple adds one reference per unique node but no process-global retention. Test release through a weak reference.
- Profiling under other CAD jobs affects wall time. Report process CPU for a bounded operation and exact numerical parity.
