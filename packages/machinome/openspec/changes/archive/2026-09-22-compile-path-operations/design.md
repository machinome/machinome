## Context

ADR-124 limits a repeated path sample to its moving expression cone, and recent cycles replaced expression-node hashing with positional child references. On the frozen Curta `7586002` graph at framework `3afb3f7`, an ordinary 360° turn costs 72.56 CPU seconds for two simulated seconds. One early tick calls `_PathValue.at` 188,027 times and visits 4.78 million moving nodes. The repeatedly sampled 51-node path has 49 numeric operators, predominantly arithmetic and two-argument `min`/`max`. Its per-sample Python interpretation is now measurable; the anti-reversal pawl's separate prefix replay is required by ADR-137 and stays untouched.

## Goals / Non-Goals

**Goals:** Reuse a path's immutable operation classification and child positions across its samples; retain exact float bits, first errors, eager binding, standing refresh, visit counts, and graph collectability; demonstrate a material gain on an actual ordinary Curta tick and exact bank parity.

**Non-Goals:** Changing source paths, constraint samples or tolerances, laws, model geometry, viewer code, public expression APIs, or the anti-reversal prefix replay. No generated Python source or process-wide cache.

## Decisions

1. Extend the existing `_PathValue` moving program with a private, per-instance numeric instruction sequence after the first **successful** eager bind. Each instruction keeps the current child positions in their original order and resolves the already-supported operator to its existing callable. An invalid or unsupported node remains subject to the first bind's current error order; no instruction is published after a failed bind. Rebinding only refreshes numeric standing values, not immutable instructions.
2. Keep the existing `at` walk and a fresh local result array per sample. It reads moving names from that sample and standing positions from the most recent complete bind. Numeric `min`/`max` retain Python built-in operand selection for valid two-argument calls; malformed arity still follows the public `machinome.math` error path at its original place. Other math calls use their current numeric function and argument order. The path remains the sole owner of instruction references.
3. Reject the change if the controlled frozen-Curta before/after pair does not show a useful CPU-time improvement with byte-identical bank/sampled-level evidence. A no-gain result is evidence, not a reason to weaken search or add a knob.

Alternatives: source-generated closures were previously measured by ADR-124, but add runtime code generation and security/audit cost; this cycle first tests the smaller instruction-dispatch change. Caching entire graph results has been measured to cost more to key than it saves; interpolating the retained pawl would change the actual motion path.

## Risks / Trade-offs

- [Operator lookup moves to binding] → Use the same callable and operand order, retain the old malformed-call path, and test signed zero, NaN, missing input, arithmetic errors and evaluation precedence.
- [Failed bind exposes partial instructions] → Publish only after full eager evaluation and complete structural compilation; test failure followed by a good bind.
- [Per-path instructions increase allocation] → Keep them in the existing path's lifetime only and verify discarded graph collectability and a real Curta CPU gain.

## Migration Plan

Private implementation only; no document or API migration. A reverted implementation commit restores the prior interpreter without changing a model or its records.

## Open Questions

Whether callable-dispatch preparation amortizes on the real Curta after its compilation cost. The measured before/after pair decides this before integration.
