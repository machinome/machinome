## Context

ADR-124's `_PathValue` already evaluates a graph once per path piece, then follows only the moving cone at later points. ADR-137 now gives a running constraint actual determined read paths; `_searched_constraint` nonetheless sends each traced sample's arguments to whole-graph `GraphValue.evaluate`. The Curta `7586002` higher-result-bank graph has 126,032 nodes and 23 reads, but only two read names move over its active traced searches, yielding 7,851 and 3,670 moving nodes. Fresh-instance instrumentation proved that a search-scoped `_PathValue` returns the identical bit pattern for every one of 264 constraint-graph sample calls (including nontraced searches left unchanged), in the same order and with the same final 213-bank stop. An uninstrumented prototype reduced the active tick from 7.885 to 5.605 process CPU seconds on reserved CPU 14.

## Goals / Non-Goals

**Goals:** Reuse the accepted path evaluator for the one scope where a constraint's actual source paths are already known; preserve every existing sampled level, first-outward bracket, bound argument, refusal, and numerical/error order.

**Non-Goals:** Infer a path for undetermined/Play reads, replace the 64-sample search or bisection with solving, skip chart sectors, cache across searches or ticks, change a bound's own-coordinate value, or change project laws/public APIs/viewer documents.

## Decisions

1. Only the existing `traced` branch of `_searched_constraint` gets one `_PathValue` for the bound graph per search. It binds at the first `level(0.0)` from the exact current argument mapping, then uses `at` for later samples. The nontraced `_constraint_level` prefix replay remains byte-for-byte on its present route. This keeps path structure/standing values search-local and prevents a later search's changed standing reads from using stale values.
2. Classify as moving a read whose determined `Motion` is not constant, or whose untraced-but-undetermined input delta is nonzero. A `Motion.constant` with opposite signed-zero endpoint bits must also be treated as moving because `Motion.at(0)` and `Motion.at(1)` retain those distinct cached bits even though numeric equality says constant. Check that case by a signed-zero sign comparison; NaN is never considered constant by `Motion.constant`. The bound's own coordinate remains fixed to the run bank's tick-start value, just as before.
3. Keep input argument construction, arithmetic, `outward` comparisons, sample loop, bisection, and `_ConstraintContact` unchanged. Let first `bind` evaluate every graph node eagerly at the same first sample; let each later `at` evaluate moving nodes in the same postorder with the same operator functions. Do not catch or move any exception. Prove this with tests for per-sample evaluation counts/order, standing refresh across two searches, signed-zero/NaN, eager first-sample errors, and nontraced fallback, then exact Curta sample/bank parity and broad stop/source-timing regressions.

## Risks / Trade-offs

- [A read classified standing actually changes inside the path] → Use the existing determined `Motion.constant` witness, with the signed-zero endpoint guard; all other traced motions are moving.
- [A new search reuses stale standing values] → Construct a fresh path inside each `_searched_constraint` invocation and test changed standing reads on consecutive searches.
- [An error moves later or a nontraced path changes] → First bind stays eager; nontraced branch is untouched; test missing inputs, arithmetic/refusal behavior and exact Curta sample order.
- [Small constraint graphs pay unnecessary path-compile overhead] → Measure representative framework controls and the real Curta; abandon or narrow if a material regression appears.

## Migration Plan

Private running evaluator only; no data migration. The isolated implementation commit can be reverted if parity or performance gates fail.

## Open Questions

None; the frozen Curta and framework regression gates decide acceptance.
