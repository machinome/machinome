## Context

The viewer re-derives a compiled cyclic law block's selector partition and output `Motion` paths in `blockMotion` on every propagation. This is required when source paths move: a zero net delta can hide an interior excursion, and crossings depend on the current tick. It is redundant only for a successful block whose *actual* source paths are constant and whose complete numeric inputs match a prior successful evaluation.

On viewer main `b976a17`, Curta's asymmetric v13 program has blocks of 31 and 16 laws. During the actual 90° preparation plus 144 default-`dt=1/240` reversing-lever ticks, the 31-law block received constant source Motions on 146 of 147 calls, produced zero positive increments and constant output Motions on all 147, and produced no crossings on those constant-source calls. It took about 7.4–7.6 CPU seconds; the 16-law block took about 1.0. The process-local experiment achieved 145 hits and about 60–67% less CPU per 48-tick lever gesture with exact bank/status/admission parity. It reused mutable Motion objects globally and is evidence only, not the implementation.

Accepted ADR-058 requires per-piece selector order and crossing ownership. ADR-071 requires determined source paths, not endpoint chords. The concurrent terminal-target cycle adds `Motion.exactTerminal`; it can preserve a target's final bit pattern even when endpoint arithmetic or signed zero differs. This change must preserve all three contracts after both viewer histories are merged.

## Goals / Non-Goals

**Goals:**

- Avoid repeated selector partition and law evaluation only for a certified, previously successful, side-effect-free, constant-source cyclic block with the same exact finite inputs.
- Return bit-identical increments and fresh, behaviorally identical constant output paths while retaining existing crossings, landings, errors and searches for all other calls.
- Own a bounded cache in one `Run`; invalidate on successful restore/reset, new `Run`, changed expression generation or changed input/path metadata.
- Validate on the pinned Curta gesture, ordinary moving crank, blocked/replay and the merged terminal-target signed-zero corpus.

**Non-Goals:**

- No reuse for moving paths, including leave-and-return paths with zero net delta; no generic result memo, static-law compiler, JIT or public cache API.
- No change to input admission, timestep, branch/cut sampling, tolerances, numeric operator order, document schema, viewer API or framework producer.
- No claim that engine CPU explains hosted browser wall time or that this makes the Curta real-time.

## Decisions

1. **Run-owned, one entry per compiled block.** A private map on `Run` stores at most one successful descriptor for each block object. Pass this cache explicitly through the running propagation path; no process/global registry or document-owned history. A block with a different complete key replaces its own entry only after successful integration. Clear on successful `restore` (and thus `reset`); failed restore validation does not mutate it. A new `Run` starts empty. This bounds entry count to the finite number of compiled blocks and allows garbage collection with the Run. A global WeakMap or identity-only cache would hide cross-run state and is rejected.

2. **Eligibility is an exact path and graph proof, not a bank shortcut.** Before a lookup, require every actual source `Motion` delivered to the block to be `constant`, affine, finite, and bit-identical at both endpoints, including the concurrent `exactTerminal` metadata. Require all held output values and all other names read by the members' selector and law graphs to be present finite built-in numbers; compare their IEEE-754 bits (`Object.is` for numbers suffices, but serialization must not collapse `+0`/`-0`). Include the compiled block identity and expression generation. A deterministic closed numeric-expression provenance check must reject `random`, context/binding-shadowed or custom calls, nonnumeric/coercing operands, and any unknown graph shape; inspection failures fall back to the original eager evaluation, not an earlier new error. Function identities used by the certified expression context must still be the native functions certified when the entry was made, or the call falls back. This is conservative: a missed hit is acceptable.

3. **Publish only complete, effect-free results.** The ordinary first evaluation still performs its whole selector partition and member walk in the original order. A cache candidate is eligible for publication only if that call succeeds, emits no crossings or landing writes, and every output Motion is finite, affine, truly constant with bit-identical start/end and the canonical one-piece, no-interior-cut shape (including terminal metadata), with a bit-identical positive-zero increment where the ordinary call returns one. Publish after the containing integration commits, not from a failing/rolled-back prefix. Store immutable scalar descriptors (names, exact start/end/terminal bits, increment bits, required path metadata), never the mutable `Motion` instances or closures. A hit constructs fresh constant Motions using the same supported construction semantics and returns a fresh increments list; compare `at(0)`, interior `at(t)`, `at(1)`, `cuts()` and `exactTerminal` to the original before accepting this construction. If that equivalence cannot be established for a metadata shape, use the ordinary path. Keep the Block's own crossing-limit validation and later Bound evaluation in their original places. Storing the original Motion or an entire propagation result is rejected.

4. **Preserve eligibility and errors at the original boundary.** The inexpensive lookup/certification occurs where `blockMotion` would run, after preceding edges have evaluated. Nothing is memoized if the current source path is nonconstant, a required name is absent/nonfinite, a callback can be stateful, or a cache-hit descriptor cannot be reconstructed. The full function then runs unchanged. Preflight may read already-produced metadata but must not evaluate a graph expression in a new order; any preflight exception is treated as ineligible, allowing the scheduled expression to raise its original first error.

5. **Paired regression and empirical gate.** The implementation branch must merge (not overwrite/rebase away) the independently integrated terminal-target cycle before final validation. The test matrix covers `+0`/`-0` source and output endpoints, exactTerminal true/false, nonlinear zero-net excursion, different mid-piece cuts, changed branch/binding values, stateful/custom calls, malformed operand and competing errors, crossing/landing emission, failed integration/retry, restore/reset/new Run and cache bound. Compare every ordered crossing/stop and complete 214-coordinate IEEE bank, not only a final control value. On the pinned Curta manifest, compare normal 18° crank, 90° prep and three 48-tick lever gestures under identical CPU conditions; retain the original prefix sample counts and report process CPU and hosted browser separately.

## Risks / Trade-offs

- **A numeric endpoint appears constant while the interior moves** → require actual `Motion.constant` plus exact endpoint/path-metadata proof; never infer from net delta or bank equality.
- **A reused path loses signed zero, target landing or future cuts** → restrict to bit-identical constant output descriptors and construct fresh Motions with preserved `exactTerminal`; fallback for any unsupported metadata shape.
- **A cached call suppresses a required error or event** → closed pure graph gate, successful-only publication after integration, no crossing/landing outputs, unchanged fallback and adversarial first-error tests.
- **Extra certification outweighs savings on small blocks** → one-entry bounded design and actual Curta paired CPU gate; do not extend to all shapes or add a broader compiler on an unmeasured promise.
- **Concurrent endpoint work changes the Motion contract** → wait for its integration, merge both histories in the isolated worktree and rerun exact corpus/Curta gates before any viewer main integration.

## Migration Plan

No document or host migration. The viewer can drop this private optimization without changing its externally observable result. Integration is permitted only after the paired terminal-target history and validation are present; no push or publication follows automatically.

## Open Questions

- Confirm the terminal-target implementation's constructor/metadata invariants for a fresh constant Motion, especially an exact target with signed-zero bits. If no simple descriptor is equivalent, decline that metadata shape rather than reusing a path.
- Determine whether the deterministic graph-provenance check can reuse the existing certified-kink walk without exposing a new public helper; otherwise implement the smallest private shared predicate. Do not evaluate graph nodes during eligibility.
