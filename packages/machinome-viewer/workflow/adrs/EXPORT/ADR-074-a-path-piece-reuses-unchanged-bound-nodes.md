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
