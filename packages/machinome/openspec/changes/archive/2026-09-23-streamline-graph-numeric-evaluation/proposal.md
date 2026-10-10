## Why

The installed Curta reverser profile trial still spends several CPU seconds on one 0.1-second operating tick. Its kink search calls `GraphValue.evaluate` 439,729 times per tick, and the evaluator currently builds a child-argument list even for scalar leaves and ordinary binary nodes that do not need one. A process-local equivalent dispatch prototype retaining live per-call operators saved 0.62–1.08 CPU seconds across three alternating originating-tick pairs without changing ordered numeric results or the 214-coordinate bank.

## What Changes

- Keep `GraphValue.evaluate` as the one eager, ordered numeric graph evaluator, but avoid unnecessary child-list allocations for supported scalar leaves and binary operations. Keep its live per-call operator table unchanged.
- Preserve the existing fallback behavior and error precedence for malformed arity, unsupported nodes, custom operands and uncertain values. No generated code, numeric-result cache, new search rule or changed sample count is proposed.
- Add red-first evaluator regressions and validate the unchanged Curta operating request against its pinned ordered results and full bank.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `motion-expression-sharing`: Clarify that the existing numerical-evaluation contract includes signed-zero and nonfinite binary results and first-error precedence. No previously valid behavior changes.

## Impact

Only the private Python numeric loop in `machinome/scad_expression.py` and focused framework tests should change. There is no public API, expression graph, program document, viewer, dependency, or project-source change. Machinome Viewer has a separate JavaScript evaluator and no measured matching bottleneck in this investigation, so no viewer cycle is included.
