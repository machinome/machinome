## Context

After the path-local numeric extrema fix, a Curta 0.1-second crank tick still executes 41,029 `GraphValue.evaluate` calls. cProfile attributes 9.49 seconds cumulative and 4.81 seconds self to full-graph evaluation. The current working graph genuinely includes the new result-bank `Bound`: its program identity differs from project checkpoint `f7e4945`, and its aggregate crank-low graph has 23 reads/126,032 DAG nodes versus 5 reads/18,829 nodes before. The early 0–18° profile takes a held-read fast path for that bound, so it is evidence for this evaluator cost, not a claim about active result-bank cost later in the revolution.

## Goals / Non-Goals

**Goals:** Compile one `GraphValue`'s immutable graph order and child positions once; evaluate fresh values in the exact same postorder and child order on every call. Remove numeric `min/max` face classification while retaining their exact Python built-in selection behavior. Reduce real Curta tick CPU without changing its full bank.

**Non-Goals:** Prune inactive chart sectors, memoize any numeric value across evaluations, alter operator definitions, constraint samples, dt, source-timing, branches, errors or viewer-document syntax.

## Decisions

The object-local evaluation plan will store ordered node instructions and each child's positional slot. A temporary node-to-slot index exists only while compiling; it is discarded. Each `evaluate(inputs)` allocates fresh numeric slots and processes instructions in the same postorder, gathering child arguments in their original order. Unknown operations remain errors at their original instruction rather than being rejected early during compilation, preserving preceding missing-input or arithmetic failures. The plan is published only after complete structural compilation; a failed numeric evaluation may retain it, as the existing cached postorder already does.

Known two-argument numeric `min/max` call instructions use Python's built-ins, exactly the numeric face of `machinome.math`; other supported calls still use the library function. The public math functions have a fixed two-argument signature, unlike Python's built-ins. For malformed arities, both `GraphValue` and the earlier `_PathValue` fast path therefore invoke the original public function at the same evaluation node, preserving Python's exact TypeError before its numeric body runs. An independent review found this pre-existing path fast-path regression before this cycle integrated. A red test will prove the current node-keyed lookup and generic extrema dispatch and the malformed-arity regression, then compare exact float bits, exception type/message/order, changing inputs and graph collection. The Curta source graph will be pinned by hashes for a paired bounded tick and exact 213-state comparison. If a positional program fails to improve the caller, no optimization will be integrated merely because the microtest is green.

## Risks / Trade-offs

- Per-value positional plans use additional memory proportional to the reachable DAG. Keep them object-local and test reclamation, with no global registry or expanded expression tree.
- Prechecking unsupported opcodes during compilation could move an exception ahead of an earlier failing operand. Defer unsupported-operation errors to the same evaluation step as before.
- Signed zero and NaN selection can change under arithmetic replacement or reversed operands. Use the same Python built-ins and test exact bits.
- Python built-ins accept other arities and produce different TypeErrors from the public two-argument functions. Route invalid arity through those functions and test type and full message on both evaluators.
- A later active-bank crank region may have a different hotspot. This cycle reports its measured early-tick scope explicitly and does not weaken or remove any Bound.
