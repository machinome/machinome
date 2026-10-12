# ADR-074: A path piece reuses unchanged bound nodes

**Status:** Accepted

**Date:** 2026-09-22

**Change:** `cache-unchanged-path-piece-nodes`

**Amends:** ADR-060 §Decision 2 (the later-bind whole-graph rewalk). Preserves its moving-cone and point-evaluation rule.

## Context

ADR-060 avoids recomputing standing nodes at every sampled point of one piece, but explicitly re-evaluates the whole graph when binding each later piece. The 213-coordinate OperatingCurta v11 export still took 32.605 s for the first 48 of 480 crank ticks without WebGL. The viewer CPU profile placed `PathValue.bind` and `valueAt` among the leading self costs; the actual browser accepted the handle command but could not draw a revolution at its declared two-second tempo.

## Decision

The first `bind` still computes every node in the graph's postorder and classifies the moving cone. A later `bind` compares each unresolved bank-name leaf against a retained own-property presence and `Object.is` value. It recomputes changed leaves and their dependent nodes only, in that same postorder and through the same operators. A bound value is retained for every node; an `at` sample has separate scratch values and never alters the bound map. The owner `ExpressionPath` is replaced on expression generation change as before.

No cross-step cache, document field, option, API version or altered search point is introduced. A new piece with changed branches gets newly evaluated values for exactly the affected cone; one with equal inputs reuses all values. Neither `at`'s moving point nor a prior branch can contaminate the next piece.

## Consequences

The real export's first 48 crank ticks fell from 32.605 s to 27.838 s without WebGL, while committed source-timing corpus banks and restored replay remained exact. This is worthwhile but does **not** make a full physical revolution interactive. A subsequent viewer cycle must address the measured remaining costs; the original two-second duration remains the declaration, not a performance claim.

## Traced-constraint amendment — 22 September 2026

`trace-constraint-bounds-with-path` applies the existing `ExpressionPath`
moving-cone rule to one determined constraint search. The first prescribed
sample binds the bound, and later prescribed samples evaluate only work
depending on a moving read. Movement classification uses the traced
`Motion`, including a nominally constant motion whose start and end are
opposite signed zeros, or the undetermined read's linear delta. An
unsupported node disables the path for that search and falls back to the
generic evaluator; other errors are not caught. The untraced prefix replay,
search fractions, bisection, numeric operations and final bound read remain
unchanged.

On the pinned current OperatingCurta export, an active stopped tick made the
same 69 ordered bound samples and identical IEEE-754 argument/result bytes
in both variants, then blocked at the same 213-coordinate bank. Its first
48 crank ticks fell from 47.948 to 27.985 process-CPU seconds in the
post-review no-WebGL rerun, with unchanged 36° admission and full bank. The browser
accepted the real pointer command but had reached only 12° in 21.284 wall
seconds; this amendment does not claim a completed interactive revolution.

A read-only review exposed an error-order hazard in the first implementation:
`PathValue.bind` could evaluate an unsupported ternary's dead child before
throwing the fallback signal. The accepted implementation preflights the
whole binding-expanded path graph for unsupported structure before evaluating
any child. A red-first bound with `(feed ? 90 : missing())` now completes
through generic fallback without touching `missing()`. This preflight adds
no sample or arithmetic operation to a supported path.

## Successful Bound-search amendment — 22 September 2026

`cache-standing-bound-bind` narrows the original “no cross-step cache” decision
for determined Bound searches. A `Run` may retain one successful finite
`ExpressionPath` per constraint, only while expression generation and the
actual moving-name set match. The next search still compares each referenced
input's own-property presence and `Object.is` value, evaluates changed
standing dependents in the original postorder, and forces the whole moving
cone at its first prescribed sample even if the moving leaf's endpoint value
is unchanged. Subsequent samples still use `at`. A failed or unsupported
search cannot seed the cache; restore/reset clears it, and paths with a
standing `Math.random` call are ineligible. Nonfinite search scope uses a fresh
path. Generic fallback and untraced prefix replay remain unchanged. This is
Run-local reuse of bound values, not a global cache or a new document/API
field.

The pinned pre-joint production Curta export's first 48 default-timestep
crank ticks took 20.0603 versus 17.1970 process-CPU seconds on reserved CPU
15, with 4,027,665 fewer node resolutions. All 6,240 ordered Bound samples
and the complete 213-coordinate bank matched bitwise. The actual standalone
export auto-mounted with the changed bundle; a canvas pointer gesture moved
digit 1 from zero to two and completed. This remains a partial throughput
improvement, not a claim that a two-second crank request finishes in two
seconds of wall time; the originating evidence records its scope and limits.
