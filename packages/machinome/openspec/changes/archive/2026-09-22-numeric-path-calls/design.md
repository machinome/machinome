## Context

The Curta contact-stop tick visits millions of expression nodes while preserving a 64-sample crossing search. About 1.72 million calls reach `machinome.math.min/max` on already-numeric path values. Their numeric face delegates directly to Python's built-in `min/max`, but first checks for symbolic and formula operands. `_PathValue` has already resolved every leaf to a number, and its call operands are prior numeric node results.

## Goals / Non-Goals

**Goals:** Remove repeated face classification for numeric path `min/max` calls without changing operand order, selected operand, signed-zero or NaN behavior, exception ordering, graph traversal, source values, or path lifetime.

**Non-Goals:** Skip inactive charts or branch sectors; change piecewise's ordered sum, viewer/OpenSCAD semantics, constraint sample count, dt, tolerance, or publicly callable `machinome.math.min/max`.

## Decisions

The path evaluator will dispatch `min/max` call nodes directly to the same Python built-ins that their numeric math face invokes, in the same position in the existing node walk. All other call nodes retain the existing `machinome.math` implementation. This is narrower than introducing a new expression bytecode or chart primitive, neither of which the measured finding requires, and it avoids a different floating-point operation order.

A red-first test will establish that a numeric path's `min/max` calls still enter the generic face today. It will compare the path's exact float value and error behavior against the unchanged `GraphValue` evaluator over operand order, positive/negative zero, NaN, changed inputs and failed bindings. The Curta validation will pin project source hashes, run the same one-tick 213-coordinate bank before/after, then run expression and running regressions.

## Risks / Trade-offs

- A boolean or NaN result could select a different operand if the replacement used arithmetic comparison or reversed arguments. Use Python's same built-ins and test identity-sensitive cases.
- This reduces wrapper overhead, not the number of eager piecewise terms or constraint probes. Report measured gain honestly; abandon integration if the real caller does not improve.
- Retaining a private direct-call mapping has a small maintenance cost if `machinome.math.min/max` numeric semantics change later. A focused parity test keeps that coupling visible.
