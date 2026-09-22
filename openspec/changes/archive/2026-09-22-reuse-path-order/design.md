## Context

`_PathValue.bind` reevaluates a graph's standing nodes for every piece, which is necessary because branch placeholders and source values change. It also calls `postorder([root])` for every piece, although the reachable `ExpressionNode` DAG is immutable. The current Curta crank tick has 74,048 binds and 1.55 million postorder visits after the previous expression-evaluation cache. The new counter-ones Bound has not changed the first tick's bank, but its source files and hashes are recorded for the paired proof.

## Goals / Non-Goals

**Goals:** Reuse one path value's immutable traversal order after successful first binding, retain per-piece recomputation and exact evaluation/exception order, and keep graph storage scoped to the tick's path object.

**Non-Goals:** Cache numeric results, reduce 64-sample constraint checks, alter branch cuts, tolerances, dt or move semantics.

## Decisions

On a first successful `bind`, collect the nodes as `postorder` yields them while evaluating in the existing interleaved order. Save that tuple on the `_PathValue` object only after the bind completes. Later binds iterate the tuple and still compute every node from the current `values`, then set the same `standing` table. This avoids a process-wide cache and preserves first-error precedence: a failed initial bind leaves no cached order or standing result. The moving-node decision remains the existing first-bind calculation.

A narrow test counts postorder traversals across repeated binds, changes a standing input between pieces, checks a failed first bind and later recovery, and proves graph reclamation. The same Curta selector and 18°/0.1s crank tick will be timed on both sides with a full bank digest and unchanged project file hashes.

## Risks / Trade-offs

- Retaining the node tuple adds one reference per unique graph node for a `_PathValue`'s tick lifetime. The path already owns the root and its reachability; a weak-reference test verifies no global retention.
- A premature cache on a failed bind could change error recovery. Publish the tuple only after the existing evaluator succeeds and test this explicitly.
