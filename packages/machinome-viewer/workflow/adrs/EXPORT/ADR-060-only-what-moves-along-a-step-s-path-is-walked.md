# ADR-060: Only what moves along a step's path is walked

**Status:** Accepted

**Amended by:** [ADR-074](ADR-074-a-path-piece-reuses-unchanged-bound-nodes.md) for the later-bind whole-graph rewalk in Decision 2; the first bind and `at` moving-cone rule stand.

**Date:** 2026-09-16

**Change:** `walk-only-what-moves`

**Depends on:** ADR-043 (the shared DAG this is a view of), ADR-046 (the
nested scope this steps around for a followed point), ADR-047 (the corpus
this change is proved against), ADR-057 (the self-read walk), ADR-058 (the
block, whose per-piece partition is the other evaluation site). Consumes
solid-node's ADR-124 (`evaluate-only-what-moves`) as the mechanism this
mirrors, and deliberately does not consume ADR-123 (`cut-at-the-kink`; see
Consequences).

## Context

The pilot drove the operating Curta — `projects/Calculators/Curta-Type-I-3x`,
published as `simulation.running:OperatingCurta`, a version 7 document
with 208 coordinates, 268 law edges and 148 pieces, the largest running
document this viewer has ever executed and the one the studio opens — and
found it "still very slow" in the browser.

The producer answered its own half of that finding on 2026-09-16 in two
framework cycles (`solid-node`'s `curta-speed` worktree). ADR-124,
`evaluate-only-what-moves`, found that a quantity FOLLOWED along a tick's
path — the samples of a search, the rounds of a bisection, the endpoints of
a piece — was evaluated as a fresh WHOLE-GRAPH walk at every one of those
points, although the run already knows, from the `delta` it built, that
almost nothing in it can have changed. On the Curta, 57 of a followed
skeleton's 511 interned nodes moved; the rest were recomputed 64 times a
piece for nothing. Cutting that cost fell the Python tick from 3.279 s to
0.727 s. Its Consequences named this repository:

> The viewer's TypeScript run has the same whole-graph-walk shape and would
> take the same win, with no document or flag change owed to it — a finding
> for solid-node-viewer, not proposed here.

Measured on this package's own base (`4be96e5`) against the SAME document,
the same shape held: of a followed skeleton's 680 interned nodes, 104 moved
(15.3%; 1560 of 9951 over all fifteen followed skeletons this document
evaluates). An idle tick cost 18-20 ms and 20 513 recomputed DAG nodes; a
crank tick cost 157-163 ms and 1 428 635. By self time, `expressions.ts`'s
`nest` — which splits and allocates a fresh nested scope from the run's flat
bank on every one of `run/program.ts`'s `evaluateExpression` calls, because
the whole-graph evaluator resolves a qualified id as member access — was
40.6% of an idle tick and 16.0% of a crank tick, reproducing this package's
own `workflow/warts.md` finding exactly.

## Decision

**A quantity this viewer FOLLOWS along a step's path is evaluated as a
PATH.** The part of its expression that reads no name the step MOVES is
computed once per piece and read back at every point of that piece; only
the moving cone is evaluated per point. Which names move is the run's own
`delta`, never inferred, sampled, or read off a tolerance. The arithmetic is
unchanged — the same nodes, the same order, the same operators, on the same
operand values — so every float is the float the whole-graph walk gives,
bit for bit.

1. **`PathValue` (`expressions.ts`) is a VIEW of the shared DAG, not a
   second evaluator.** It walks the same interned nodes `valueOf` walks,
   through the same `applyUnary`/`applyBinary`/`readMember` and the same
   OpenSCAD `context`. It mints no node and holds no expression text. This
   is what makes bit-identity a property of the construction: a node's
   value is the same operator over the same operands, and the only
   difference is whether the operand was computed at this point or read
   back from this piece's `standing` map.

2. **Structure is decided in the first `bind`, and never again.** The first
   `bind(values)` of a piece walks the WHOLE graph in postorder — what an
   ordinary evaluation of the piece's first point already costs — deciding,
   per node, whether it moves: a name node moves when its id is in the
   moving set; every other node moves when any child does. A node that does
   not move has its value stored as this piece's STANDING value. A LATER
   `bind` — a new piece — re-walks the whole graph and re-stores the
   standing values, because a branch placeholder is a constant only on its
   own piece; it does not re-decide which nodes move, because that is a
   property of the path and not of the piece. `at(values)` — a later point
   of the SAME piece — walks only the decided moving cone.

3. **A binding name is walked INTO, not reported.** A name node that the
   document's bindings table defines has the binding's root as its one
   CHILD, so it moves exactly when the binding's own expression does and
   its value is that root's value — the same reading `resolveName` already
   makes and the same reading the selection fold's `foldedNames` already
   makes, for the same reason: a binding stands for the subexpression the
   publication extracted, and stopping at the name would call a moving
   subtree standing.

4. **A qualified id resolves against the FLAT bank.** The whole-graph
   evaluator reads a dotted id as member access, which is why every call to
   `evaluateExpression` nests the flat bank first (`nest(values)`) — 67 261
   id segments split and allocated per idle tick on this document, for
   20 513 arithmetic nodes. A path value reads `values['units.drum.turn']`
   directly. The two answers agree because `assertNestable` already refuses,
   at load, the one id shape that could make them disagree — an id that is
   a strict prefix of another — so an id present in the bank resolves to
   the same number either way. This is the only externally visible
   difference in the mechanism, and it retires the larger part of
   `workflow/warts.md`'s scope-rebuild finding as a side effect: `nest`
   falls out of the hot path for a followed point rather than being
   optimized. `evaluateExpression` itself is unchanged, for every call that
   is not a followed point.

5. **The moving set is the run's own statement (D5).** A source whose
   `delta` entry is non-zero moves. A jump node's branch placeholder never
   moves — it is a constant of its piece by construction, substituted into
   `values` per piece and never named in `delta`. The coordinate a
   self-read law reads and drives is added explicitly to a DEPENDENT jump's
   moving set, because `Walk.levelOfJump` hands that coordinate its own
   value at every point even though the walk's own `delta` deliberately
   zeroes its source; a skeleton naming the driven coordinate is refused at
   load and never reaches a path value at all.

6. **A piece is identified by a token, never by a transient object.**
   ADR-124 records the bug this closes on the Python side: keying a piece
   by `id()` of a transient dict let a later, unrelated piece inherit an
   earlier one's standing values once the earlier dict was collected,
   moving a committed coordinate on the producer's own corpus. JavaScript
   has no such hazard for an object a live reference still holds, but the
   robustness is free: `LevelPaths` (`run/jumps.ts`) hands out a strictly
   increasing integer per piece (`newPiece()`), and `Walk` — the one place
   that keys by the `branches` object itself, mirroring the producer's
   `_skeleton`/`_level` — keeps every `branches` object it builds alive for
   the walk's own lifetime, so a rebind is decided by reference identity
   rather than by a token that could be reused.

7. **Five call sites, and no sixth.** `Walk.skeletonAt` (one path value per
   walk, re-bound on the piece's own `branches`); `Walk.levelOfJump` (one
   per dependent jump, over the walk's moving names plus the driven
   coordinate); and `branchesAt`, `crossingsOf`/`bisect` through `levelAt`,
   and the walk's own outer layer, sharing one `LevelPaths` per caller's
   scope — one `PathValue` per jump placeholder, re-bound whenever the
   piece token it is asked under changes. `branchesAt` is a ONE-SHOT point
   — every jump is asked its branch exactly once for that `t` — so it
   always binds; what a `LevelPaths` shares across such calls is the
   decided STRUCTURE, never a standing part. `substituted` (a piece's two
   endpoint evaluations) and `run.ts`'s constraint search are deliberately
   OUTSIDE this table: the former is two points a piece, not worth a path
   value of its own; the latter is measured at 0% of this document's tick
   and left for the cycle that has a document demanding it.

8. **The probe is charged.** `expressionMetrics().resolutions` counts DAG
   node computations, and this repository asserts cost as work performed
   rather than as elapsed time. A path walk charges one resolution per node
   it computes — the total for a `bind`, the moving count for an `at` — so
   the number stays comparable and a followed quantity that moves entirely
   costs exactly what it cost before. This is a widget-source export for
   the widget's own tests; it does not appear on the mount handle and the
   viewer API version does not move for it.

9. **What is refused rather than guessed.** A path value refuses, loudly,
   through `UnsupportedPathNode`: a generic `member` node and a multi-part
   name absent from the bank whose first part is not `$t`, a binding or an
   OpenSCAD context name (the one shape flat and nested resolution could
   disagree on, closed at load by `assertNestable` for everything else); an
   index, a ternary, an array, an object literal; and a short-circuit `&&`
   or `||` (postorder visits both arms where `compute` visits one — no
   published document carries one, so this is refused rather than reasoned
   about). Every call site catches the refusal on first use and falls back
   to the unchanged whole-graph evaluator for that quantity's every
   remaining point, permanently: the refusal is a structural property of
   the expression, decided once. No published document or corpus fixture
   exercises this fallback today; it exists so a document that ever does
   integrates correctly rather than silently.

10. **No knob, no document change, no API change.** The saving is
    structural: no declaration, option, tolerance, cache size or sampling
    count, and nothing an author writes selects it. `solidNodeViewerApi`
    stays 16, `solidNodeDocumentVersions` stays `[1..7]`, and the document
    the producer publishes is untouched.

## Measured

Bench: this package's own worktree, node v24.11.1, the engine bundled by
esbuild and run in-thread. Document: the Curta's own re-exported
`_build_running/viewer.json` (re-export's `program`/`bindings`/`drivers`/
`instructions`/`animation` sections byte-identical to the copy measured at
proposal time; only the geometry sections differ, by the build's own
non-deterministic STL-hash nonces). Step `1/240`, 100 idle ticks then the
document's own `Turn crank` instruction and 60 more, three runs:

| | before | after |
| --- | --- | --- |
| idle ms/tick | 18.27 / 18.66 / 20.94 | 9.52 / 9.57 / 9.86 |
| crank ms/tick | 156.91 / 161.30 / 163.42 | 40.52 / 42.31 / 43.70 |

**≈2× an idle tick and ≈3.8× a crank tick** on this host. (The proposal's
own prototype, on its bench, measured 2.1× and 4.0×; the ratio, not the
absolute number, is the host-independent claim.)

**Nothing moved.** The whole bank, every recorded crossing and every stop
after 100 idle ticks, the crank instruction, and 60 more ticks are
byte-identical between the base engine and this implementation, on three
runs each (225 lines, three digests, one hash per side). The full corpus —
`src/running-corpus.json`, 20 machines including the producer's own
`KinkedStop` scenario — replays green, exactly as on the base. `PathValue`
and `valueOf` were additionally checked, `Object.is` exact, over every
followed quantity (every plan's skeleton and every jump's level) the
corpus's 20 machines and the committed `clearing`/`carriage`/`lock`
fixtures publish, at two points of a perturbed piece each.

**And the small machines did not cost more.** `run/cost.test.ts`'s existing
floors for `Train`, the Pascaline, `CarryLead` and `Captured` — none of
which follow a quantity along its own path — hold unraised; on this bench
their measured rates moved within run-to-run noise in both directions.
Floors were raised only where the gain was unambiguous across repeated
runs: `Clearing` (a solved self-read) 5919 → 14042 ticks/s, the Curta's own
clearing fixture (searched) 209 → 321, `ShiftedCarry`'s quiet block tick
4320 → 9859 and its crossing tick 2189 → 4746, and the Curta carriage block
292 → 738.

## Alternatives weighed

**A per-expression cache keyed by scope identity.** What `expressions.ts`
already does for a POSE, and exactly what does not help a RUN: every call
into `evaluateExpression` builds a fresh scope by construction (design D11
of `read-expression-bindings`), so the identity fast path never hits and a
cache keyed by it would never be read. Rejected before this cycle began,
which is why the mechanism follows the run's own knowledge of what moves
instead of trying to detect it after the fact.

**A second evaluator keyed by expression text.** Considered and rejected in
design D1: it would drift from `compute` at the first correction either
received, which is exactly the failure the conformance corpus exists to
prevent.

**Mirroring ADR-123's kink cut in the same cycle.** Measured, not assumed:
`_shape_of` re-implemented against this document and validated against the
producer's own published census classifies 17 of the Curta's 32 self-read
skeletons as KINKED and 15 as unclassified — and 100% of this document's
skeleton evaluations, level evaluations and searches are under the 15
unclassified ones, none under a kinked one. Cutting at kinks would buy this
document nothing, exactly as ADR-123 measured on the Python side; it is a
real improvement in exactness and generality, and belongs in its own cycle
with its own audit of which floats move.

**Taking the producer's refreshed corpus in this cycle.** It adds exactly
one scenario (`KinkedStop`) and replays green through the UNCHANGED base
engine; mixing its census-and-guard shape into an engine-measurement cycle
would put a red assertion in front of every engine number. Left for a
`mirror-the-gate-guard`-shaped cycle of its own.

## Consequences

**The operating Curta is not made interactive.** A crank tick is still
tens of milliseconds and still mostly inside the same two evaluation sites,
because a searched self-read crossing costs its sample count and its
bisection rounds whatever one evaluation costs. The two mechanisms that
would cut that further — a per-piece classification and a compiled moving
cone — are the producer's ADR-124 Considered Options and are the producer's
to decide first.

**`run.ts`'s constraint search follows a quantity too, and is untouched.**
Measured at 0% of this document's tick; left for the cycle that has a
document demanding it.

**The scope-rebuild wart is largely, not fully, retired.** After this
change `nest` is a small fraction of an idle or crank tick's self time,
against 40.6%/16.0% before; `workflow/warts.md`'s entry keeps this
measurement rather than being deleted, because its second cost — the
memo's inability to share a subexpression BETWEEN two followed quantities
under one run — is unaddressed.

**Two evaluators now exist for one DAG.** Mitigated by construction (D1):
they share the operator table, the context and the node store, and a
differential test asserts `PathValue` and `valueOf` agree on every
followed quantity of the whole corpus, not as an afterthought but as part
of the increment.

## Review (2026-09-16)

Accepted at the cycle's adversarial review. The reviewer re-ran the widget suite (37 files, 962 tests) and `tsc --noEmit`, and the bit-identity harness on both engines: base 19.6 ms idle / 159.8 ms crank, this engine 11.3 / 41.6 ms per tick, digests identical (`7f7bc77a…`, 225 lines).
