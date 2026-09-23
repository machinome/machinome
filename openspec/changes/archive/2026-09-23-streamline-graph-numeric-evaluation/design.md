## Context

The originating caller is the Curta Type I-3x installed reverser-profile trial. On framework main `8d0fd156787f5136174fb752be78451ce172bce8`, one no-mesh 0→18° / 0.1-second request made 439,729 full-graph numeric evaluations; its 214-coordinate bank and ordered evaluated values were pinned. `GraphValue.evaluate` already caches a positional postorder per value, but allocates an operator dictionary on every call and a child-value list at every node, including leaves that do not use it. The baseline `motion-expression-sharing` spec and ADR-101/124 require the same shared-graph lifetime, eager postorder, current-input and arithmetic behavior.

The process-local prototype `/tmp/curta_graph_scalar_codegen_probe.py` (current SHA-256 `c65ad50f56567b5f9c23703d0e535760fd3ba0607aa908de31799b03fbe63638`) used the unchanged project trial source (SHA-256 `7072a3fc2a9811b9cee375d224b5e6a96eedfde22ec3485710c16d02126021bb`) and profile reference (SHA-256 `d41e1b46ee7f4c92b61d2ddae586f01242574213942d7dd93f0e9c4aefad01a3`). Three alternating baseline/direct-dispatch-with-live-map CPU12 pairs measured `8.907→7.829`, `8.558→7.827`, `8.958→8.339` seconds, respectively; median paired saving was 0.731 CPU seconds (about 8% of baseline). Every run produced ordered GraphValue-result digest `22dd70b636d6d3fe77dcb92df4d3ddd063f3c23570e34c3e456f1f0c1d9fda32`, complete bank-bit digest `3e44081383251e2e2c12b91a58f03336ff887a465e840b8a26d88788d686983d`, and completed status. These values are transcribed from terminal JSON; no raw log was saved. A generated straight-line evaluator was slower at 8.861 seconds, so generated code is excluded. A hoisted-operator prototype gained more on some runs but would require a live-monkeypatch guard; it is excluded in favor of the smaller equivalent change.

## Goals / Non-Goals

**Goals:** Remove only avoidable child-list allocation from the private full-graph numeric loop, while preserving the same per-node operation and error order for all supported inputs, including custom numeric operands and signed zero. Reproduce the measured Curta gain with unchanged ordered results, stop and bank.

**Non-Goals:** No JIT or source generation, result or topology cache, profile-contact shortcut, expression rewrite, altered search samples or tolerances, public API, document field/version, or viewer change. No performance target is imposed on unrelated machines.

## Decisions

1. Retain the existing positional postorder on each `GraphValue` and its `values` slots. Numeric operation calls, `float` conversions, `min`/`max` operand order, and profile-contact calls remain at their original node positions. The binop fast path obtains two previously evaluated child slots directly; malformed arity uses the original splatted argument form to keep Python's error text and precedence. Calls retain the existing argument-list path. Leaves need no child-value list.
2. Keep the existing per-call operator dictionary and its live `operator`/`math.fmod` function lookup. No private shared map is introduced or exposed, so replacing those module functions between evaluations has exactly the previous effect. The direct two-child path invokes the selected original operator on the same operands and in the same order, including author-defined arithmetic methods.
3. Keep unsupported-operation and missing-input failures in the same eager walk. No compile-time validation or speculative callback execution is added. One red-first test will observe the existing child-list-comprehension call on a simple leaf/binary graph and require its absence after the change. Separate baseline-parity tests will compare the old and changed evaluator on malformed arity, left/right competing failures, custom mapping and operand behavior, signed zero, NaN/infinity, live operator rebinding and recovery on later calls; those semantic tests are expected to pass before and after the optimization.
4. Validate the actual pinned Curta request with ordered numeric-result IEEE bytes and the complete bank, not only elapsed time. Repeat CPU timing under the same affinity and input. Viewer is independently implemented in JavaScript; this Python-only allocation finding supplies no evidence for a paired viewer mutation.

## Risks / Trade-offs

- [Changed error or author-operand order] → Preserve postorder and function calls, retain splatted fallback for malformed shapes, and pin adversarial parity tests against the baseline behavior.
- [Operator lookup changes under instrumentation] → Do not hoist or expose a shared operator map; test replacement of an operator function between successive evaluations.
- [Small gain vanishes under normal load] → Report both repeated process-CPU pairs and a current-source Curta rerun; retain the change only if the gain survives proportionate validation.
- [Generated specialization appears attractive] → Reject it for this cycle: it was slower on the originating tick and changes far more error/lifetime surface than the allocation fix.
