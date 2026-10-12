## Context

`src/expressions.ts` holds ONE evaluator for the whole widget: a
hash-consed DAG of interned nodes (ADR-043), walked by `valueOf` with a
per-pass memo. `src/run/program.ts`'s `evaluateExpression` is the ONE
place `src/run/` reaches it (design D11), and by construction every call
builds a FRESH scope — `drivers: nest(values)` — because the memo's
identity fast path would otherwise hand one evaluation the previous one's
numbers.

Under a POSE that is exactly right and costs nothing: one `tree.update`
walk is one scope object, the identity fast path hits, and a
subexpression shared by fifty operations is resolved once. Under a RUN it
is the finding in `workflow/warts.md`: every call arrives with a new
object, the fast path cannot hit, `scopesEqual` deep-compares, the pass
counter advances, and the memo is abandoned. Measured on the operating
Curta at 40.6 % of an idle tick's self time.

That is the symptom. The disease is upstream of it, and the producer
named it in ADR-124: the run does not ask for ONE evaluation. It FOLLOWS
a quantity along a path — 64 samples of a searched piece, up to 64
bisection rounds behind each bracket, two endpoints of a solve, a
midpoint per partition piece — and at every one of those points it walks
the WHOLE expression, although the run already knows, from the `delta` it
built, that almost nothing in it can have changed. On this document 104
of a followed skeleton's 680 nodes move; the other 576 were recomputed
64 times a piece.

## Goals / Non-Goals

**Goals:**

- A quantity followed along a step's path costs, per point, its MOVING
  cone and nothing else.
- Every float the engine produces is the float it produced before, bit
  for bit — proved against the conformance corpus and against the
  originating document's own bank, crossings and stops.
- No knob, no document field, no API version, no cross-step cache.
- The cost is asserted as WORK PERFORMED, through the probe this
  repository already has.

**Non-Goals:**

- ADR-123's kink cut, the corpus refresh, `run.ts`'s constraint search,
  and the remainder of the scope-rebuild wart. Each is measured in
  `proposal.md`'s Non-goals with the number that puts it outside this
  cycle.
- Restoring cross-expression memo sharing under a run.

## Decisions

### D1. A path value is a view of the SHARED DAG, not a second graph

`PathValue` takes a `NodeId` — the root `program.nodeOf(expression)`
already returns — and walks the same interned nodes `valueOf` walks,
through the same `applyUnary`/`applyBinary`/`readMember` and the same
OpenSCAD `context` table. It mints no node, parses nothing, and holds no
expression text.

That is what makes bit-identity a property of the construction rather
than a test result: a node's value is the same operator applied to the
same operands, and the only difference is whether the operand was
computed at this point or read back from this piece's bind.

**Alternative rejected: a second evaluator keyed by expression text.** It
would drift from `compute` at the first correction either received, which
is the failure the conformance corpus exists to prevent and the reason
`jumps.ts` reuses `partition`, `branchesAt` and `levelOf` rather than
copying them.

### D2. Structure is decided in the walk `bind` was going to make anyway

The first `bind` walks the whole graph in postorder — which is what an
ordinary evaluation of the piece's first point does — and decides, per
node, whether it moves: a NAME node moves when its dotted id is in the
moving set; every other node moves when any child does. A node that does
not move has its value stored as this piece's STANDING value. So a
quantity followed at one point costs what it cost before plus a boolean
per node, and every later point of that piece walks only `order`, the
moving nodes in the same postorder.

A later `bind` — a new piece — re-walks the whole graph and re-stores the
standing values, because a branch placeholder is a constant only on its
own piece. It does NOT re-decide structure: which nodes move is a
property of the path, not of the piece.

### D3. A BINDING name is walked into, not reported

The document's bindings table maps a name to an interned root, and
`resolveName` resolves a binding BEFORE a driver id. A path value follows
the same rule structurally: a name node that is a binding has the binding
root as its one CHILD, so it moves exactly when the binding's own
expression moves, and its value is that root's value.

This is the reading `foldedNames` already makes for the selection fold
(design D1.5), for the same reason: a binding stands for exactly the
subexpression the publication extracted, and stopping at the name would
call a moving subtree standing.

### D4. Names resolve against the FLAT bank

`compute`'s name resolution reads a qualified id as MEMBER ACCESS, which
is why the run has to nest the bank at every segment on every call. A
path value reads `values['units.drum.turn']` directly.

The two answers agree, and the guarantee is already ratified: at load
`assertNestable` refuses an id set in which one id is a strict prefix of
another, which is precisely the shape that makes flat and nested
resolution disagree. With that refused, an id present in the bank
resolves to the same number either way, and an id absent from it falls
through to the OpenSCAD context either way.

**This is the only externally visible difference in the mechanism, and it
is why `nest` falls out of the run's hot path rather than being
optimized.** `workflow/warts.md`'s "Proposed interface" listed exactly
this as its first direction and declined to ratify it; this cycle takes
it for the path evaluator ONLY. `evaluateExpression` keeps its fresh
nested scope, unchanged, for every call that is not a followed point.

### D5. The moving set is the run's own statement

- A source whose `delta` entry is non-zero MOVES.
- A branch placeholder is NEVER in it: it is a constant of the piece by
  construction, and it is substituted into `values` per piece.
- The coordinate a law READS AND DRIVES is added explicitly for a
  DEPENDENT jump's level, and only there, because `Walk`'s constructor
  deliberately zeroes it in `delta` while `levelOfJump` hands it its own
  value at every point. For the SKELETON it is not added: a skeleton that
  named the driven coordinate is refused at load.

Nothing is inferred from sampling, from a tolerance, or from comparing
two evaluations.

### D6. A piece is identified by a token, never by a transient object

ADR-124 records the bug this rule closes: keying a piece by `id()` of a
transient dict let a later, unrelated piece inherit an earlier one's
standing values once the earlier dict was collected, moving a committed
coordinate by exactly 100 on `Clearing`'s own corpus scenario.

JavaScript has no such hazard — a `Map` keyed by object identity keeps
the key alive and two live objects cannot share an identity — but the
robustness is free, so `LevelPaths` hands out a strictly increasing
integer per piece (`newPiece()`), exactly as the producer does.

`Walk` is the one place that keys by the `branches` object itself, as the
producer's `_skeleton`/`_level` do, and for the same reason it keeps
every `branches` dict it builds alive for the walk's lifetime.

### D7. Five sites, and no sixth

| site | path values | re-bound on |
| --- | --- | --- |
| `Walk.skeletonAt` | one per walk | the piece's `branches` |
| `Walk.levelOfJump` | one per dependent jump | the piece's `branches` |
| `partition` → `branchesAt` | one per jump, in a `LevelPaths` | a fresh token per one-shot point |
| `partition` → `crossingsOf`/`bisect` → `levelAt` | the same `LevelPaths` | a fresh token per piece |
| `Walk.outerCuts`/`outerBranches` | one `LevelPaths` for the whole walk | as above |

`planIncrement` builds one `LevelPaths` and hands it to both its
`partition` and its per-piece `branchesAt`, so the structure decided for
a jump's level is decided once for the whole increment.

`branchesAt` is a ONE-SHOT point — every jump is asked its branch exactly
once for that `t` — so it always binds; what it shares with the rest of
the scope is the decided STRUCTURE, not a standing part.

`substituted` (the increment's two endpoint evaluations) and
`Walk.skeletonAt`'s caller `ownAt` are NOT given separate path values:
the former is two points a piece, the latter is `skeletonAt` already.
`_KinkCuts`' own level has no counterpart here, because this viewer does
not cut at kinks.

`run.ts`'s constraint search is deliberately outside the table: same
shape, no measured cost on this document, its own cycle.

### D8. The probe is charged

`expressionMetrics().resolutions` counts DAG node computations, and the
spec requires this repository to assert cost as work performed rather
than as elapsed time. A path walk charges it one per node it computes, so
the number stays comparable: on this document it falls from 1 428 635 to
10 492 per crank tick, which is the measurement, not an omission.

This is a widget-source export for the widget's own tests. It does not
appear on the mount handle and the API version does not rise for it.

### D9. What is deliberately NOT bit-identical-by-luck

Two shapes could break bit-identity if the path evaluator were careless,
and both are settled by construction rather than by testing:

0. **`member` nodes and multi-part names absent from the bank** (review
   amendment). `resolveName` walks a multi-part name by `readMember`
   from its first part; the path value reads the whole id from the flat
   bank. They agree for every id the bank holds (`assertNestable`), and
   a multi-part name the bank does not hold, or a `member` node, is
   REFUSED by the path value and falls back to the whole-graph
   evaluation rather than guessed (tasks 1.4, 1.5).
1. **Short-circuit and ternary nodes.** `compute` does not visit the
   unchosen arm; a postorder path walk visits every node. In JavaScript
   arithmetic that changes no value (there are no exceptions and no side
   effects to trigger), and the ROOT's value is the chosen arm's either
   way. The published documents this viewer executes carry no `?:`, `&&`
   or `||` at all — verified on the originating document (zero
   occurrences) — so the first implementation may refuse an unsupported
   node kind loudly rather than guess, and a document carrying one falls
   back to the whole-graph evaluation.
2. **Order of operations inside one node.** None: a node is one operator
   over its children's values, and the children's values are the same
   floats.

### D10. Red first, and what red looks like

A performance change whose contract is "every float is unchanged" cannot
be proved by a green suite alone — the suite was already green. The
increments therefore each carry a test that FAILS before them:

- a path value asked for a point of a piece it has not bound, or bound
  under another piece's branches, returns a DIFFERENT number than the
  whole-graph walk — the test that pins D6, written against a two-piece
  fixture;
- a followed quantity whose standing part is stale gives a crossing at a
  different fraction — pinned on `Clearing`'s own corpus scenario, which
  is the scenario that caught the producer's `id()` bug;
- the node-visit count of a second point of a piece is the MOVING count
  and not the total — the structural claim, asserted through the probe;
- and the whole corpus, replayed, which is red for any of the above that
  escapes the three.

## Risks / Trade-offs

- **A path value is built per followed quantity per scope, and a tiny
  machine pays for building it.** Measured: `Train` 164 138 → 182 211
  ticks/s, the Pascaline 34 555 → 33 734 — inside this bench's own
  spread, in both directions. The guard is kept as a cost-test floor.
- **Memory.** One `Map` of standing values per followed quantity, sized
  by the graph, alive for one step. The Curta's fifteen followed
  skeletons hold 9 951 node values between them — under a hundred
  kilobytes, dropped every tick.
- **The flat-bank resolution (D4) is a genuine behavioural commitment,**
  not an optimization: it makes `assertNestable`'s refusal load-bearing
  for the run's arithmetic. The refusal already exists and already fires
  at load, so a document that could disagree never reaches a path value —
  but the spec must say so, and it does.
- **Two evaluators now exist for one DAG.** The mitigation is D1: they
  share the operator table, the context and the node store, so there is
  one place to correct. A test asserting `PathValue` and `valueOf` agree
  on every node of a real document, for a real set of values, is part of
  the increment rather than an afterthought.

## Migration

None. No document changes, no host-visible interface changes, no stored
state. A page that reloads the bundle gets the faster engine and the same
numbers.
