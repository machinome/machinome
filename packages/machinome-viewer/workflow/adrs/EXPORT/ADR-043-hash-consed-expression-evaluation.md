# ADR-043: Hash-consed expression evaluation

**Status:** Accepted

**Date:** 2026-09-07

**Change:** `share-expression-subtrees`

**Amends:**
- [ADR-035: Reusable viewer core and declared API version](ADR-035-reusable-viewer-core-and-declared-api.md)

## Context

Operation and flexible-parameter expressions arrive in a published document
as text and are evaluated in the browser on every frame an input changes.
Until now that meant `jokenizer`: `tokenize` to a tree, a module-level cache
from expression string to that tree, and `evaluate` — a visitor that walks
every node of the tree, every time.

That is affordable only while expressions are small, and the producer does
not guarantee they are. solid2's `OpenSCADConstant` builds an expression by
string concatenation, so every reuse of a value pastes its full text again.
3DPrintedClocks' `wall_clock_53_grasshopper` publishes 31.6 MB of
expressions: 116 operations, 30 distinct strings, 4.28 million parsed nodes
— and 293 distinct subexpressions. The viewer walked 6.25 million nodes per
animated frame (~0.5 s per frame) and retained 723 MB of parse trees for the
life of the page.

Nothing about the numbers is wrong, and no document format change can reach
the documents already published. The cost is structural: the evaluator has
no way to notice that it is computing the same thing again, because two
identical subtrees are two objects and its visitor has nowhere to put a
memo.

## Decision

The viewer evaluates a **hash-consed DAG**, not a parse tree.

- `jokenizer`'s `tokenize` stays the parser — the grammar, the literal rules
  and the precedence are the parity-proven half of the package — and its
  `evaluate` is replaced by an evaluator this package owns.
- Each parsed expression is interned bottom-up into one module-level table
  keyed structurally (kind, operator or name, and the ids of already-interned
  children), so structurally identical subtrees become one node across the
  whole document, not only within one expression. The parse tree is dropped
  as soon as its root is interned.
- Evaluation walks the DAG with a memo indexed by node id and stamped by an
  evaluation pass, where a pass is a set of scope values: an identity fast
  path, and behind it a value comparison that recurses through the driver
  map, because the viewer rebuilds those nested maps on every call and
  identity would report them changed every time. One frame therefore costs
  the distinct subexpressions the frame's operations read.
- The OpenSCAD semantics move onto the builder and the evaluator unchanged:
  degree trig, `mod`, `ln`, `log(base, value)`, the exponent-literal rewrite
  in front of the parser, and `^` folded into a `pow` call with the rule
  that a leading unary minus stays outside it. Name resolution keeps the
  order the old spread scope established: `$t`, then the driver map, then
  the math context, reproducing jokenizer's member-access edge cases
  (a missing or falsy owner yields `undefined`; a truthy primitive owner
  throws the same native `TypeError`) rather than tidying them.
- A dotted driver id interns as ONE name node, so free variables — which
  bound re-evaluation for drivers and flexible parts — are read off the DAG
  with exactly the rules they had: a dotted id is one name, a call's callee
  is never a variable.
- The table is retained while a viewer is mounted and emptied when the last
  one is disposed of, with a node ceiling behind that for long
  republish sessions. It is a pure cache: emptying it costs a re-parse and
  can never cost a wrong number.
- The win is asserted as counted subexpression resolutions, exported from
  the widget's source for its own tests. It is not on the host handle, so
  the viewer API version does not move.

## Alternatives considered

- **Keep jokenizer's `evaluate` and cache more.** Rejected: its visitor
  cannot memoize — there is no node identity to key on — and caching whole
  expressions is what already exists and what costs the 723 MB.
- **Compile each expression to JavaScript with `new Function`.** Rejected:
  a second numeric implementation to hold in parity for a win the memo
  already delivers (~24,000× fewer node visits per frame), and `new
  Function` is refused under a strict Content-Security-Policy, which a
  static export may well be served under.
- **Wait for the producer to emit shared subexpressions.** Rejected as the
  answer *here*: it is the right fix upstream and is a separate solid-node
  change, but it cannot help any document already published, and the viewer
  must render what the framework has already written.
- **De-duplicate the text before parsing.** Rejected: a textual
  common-subexpression pass is a parser in disguise, and it would still hand
  the tree walker the work.
- **Intern per document rather than per page.** Rejected as the primary
  key: sharing across documents costs nothing and helps the development
  server's republishes; lifetime is handled by mount refcounting instead.

## Consequences

- A frame of the grasshopper clock resolves 255 nodes instead of walking
  6.25 million; sixty frames take 29 ms where the pilot measured about half
  a second each.
- Retained expression state for a document falls from hundreds of megabytes
  of parse trees to a table of a few hundred nodes.
- Preparing an expression costs the interning walk on top of parsing
  (measured ~16% more one-time work for the clock, 8.86 s against 7.65 s);
  frame cost falls by four orders of magnitude.
- `freeVariables` becomes a walk of distinct nodes rather than of the whole
  parse tree, which speeds the load path that reads dependencies.
- This package now owns a numeric evaluator. The producer-parity fixture,
  which was already the contract, becomes the thing that holds it honest,
  and a builder-level comparison against jokenizer's own `evaluate` guards
  the seam while the two coexist.
- An expression form the DAG does not support — an inline function — is
  refused by name when the document is loaded, beside the existing refusals
  for an unknown document version, an unknown flexible technology and an
  undeclared driver id, because the loader's own free-variable walk is what
  prepares every expression. Nothing the producer emits carries one, and no
  such expression can first be met inside a frame.
- The viewer API version stays 6: no interface change and no capability a
  host may require.

## Lifetime amendment — 22 September 2026

`keep-expression-references-valid` corrects the assumption that one model
fits below the reclamation threshold. The Curta remaining-result-bank
export needs 94,854 nodes during program loading; a reset between its
expression root and binding roots caused either missing-node failures or
reuse of an integer for a different expression.

The store remains page-scoped. A nestable, synchronous `withExpressions`
operation protects complete preparation and consumption. Threshold-based
reclamation happens before an outer operation acquires references; a live
operation may exceed the unchanged 50,000-node trigger. Scopes release in
`finally`, including refusals. Final-mount disposal inside a scope defers
the clear until its end. No scope spans an `await` or a mounted session.

Long-lived kink descriptors retain source plus postorder index and rebuild
their operands once per generation. `ExpressionPath` retains source and
the original piece's standing values to rebuild `PathValue` after a reset;
the numerical path algorithm is unchanged. Raw `NodeId`, structural walkers
and `PathValue` are operation-local. Program root lookups reuse the shared
string cache instead of retaining a second map. A tick, clocked request or
tree update scopes its full synchronous work. No host API, document version,
numeric expectation or memory ceiling increase is part of this amendment.

## Capacity amendment — 22 September 2026

`retain-large-expression-working-set` raises only the finite node-reclaim
trigger from 50,000 to 125,000. The committed OperatingCurta export prepares
97,474 nodes, and the currently operating CounterTens trial prepares 102,580;
the two mounted together retain a 102,690-node union. At 50,000, every
adjacent tick of the committed machine reclaimed and rebuilt about 94,763
nodes. The raised trigger keeps one fitting graph across those ticks and
the measured pair of mounts without changing evaluation or generation
reconstruction.

The same pinned 48-tick segment admitted 36° and produced the identical
213-coordinate bank at both thresholds. On a reserved core it took 65.670 s
at 50,000 and 37.440 s with the source change. This is a cache-capacity
change, not a numerical or sampling change; the full browser turn remains
far slower than its declared two-second drawing duration.

The trigger is not a hard maximum: a protected operation can temporarily
exceed it. Reclamation still happens before a later outer operation, and
disposing the last mounted viewer still clears the table. The trade-off is
greater retained headroom for a current large machine, not unbounded
publication history. Terminal V8 heap/RSS samples varied enough that they
do not establish a fixed memory budget for one export. The viewer API and
document version remain unchanged.

## Validation-boundary amendment — 5 October 2026

Amendment accepted after parent text and actual Voron adversarial review under
the pilot's advance authority; the preceding accepted decisions retain their
status. Change: [mount-voron-export](../../../openspec/changes/archive/2026-10-05-mount-voron-export/).

The full Voron-2 export demonstrated that protecting each expression check
separately is not protecting validation. Its 232,347 bindings prepare a graph
above the finite reclamation trigger; the next check could reclaim and rebuild
the entire table. A counted low-trigger regression prepared one valid table
91 times and changed generation 171 times within a single validation.

`assertRenderable` therefore encloses **all synchronous validation** in the
existing nestable `withExpressions` operation: table preparation, program and
clocked loading, tree operation/flexible-parameter checks and final entry checks.
Nested checks acquire and consume roots inside that same protected operation.
The scope releases on success or refusal through the existing `finally` path.
Fetching, geometry loading, runtime readiness and other asynchronous work stay
outside it; no scope spans an `await` or a mounted session.

The trigger remains **125,000**, not a hard limit on a protected live graph.
Reclamation before a later outer operation and clearing after final-viewer
disposal remain required. Source/postorder reconstruction and document-generation
guards are unchanged. The corrected regression prepares the table once, changes
generation zero times, then reconstructs the same value after forced reclamation.
No numeric rules, API or document version change. The operation-owned structural
facts are specified separately in ADR-044's amendment; network admission belongs
to ADR-078, not the expression store.

[Implementation evidence](../../../openspec/changes/archive/2026-10-05-mount-voron-export/evidence.md)
and [parent adversarial acceptance](../../../openspec/changes/archive/2026-10-05-mount-voron-export/parent-review.md)
record the counts, refusals, full unchanged export and measured cleanup. A large
live validation graph still consumes memory; this establishes correct lifetime,
not a universal memory budget or cross-browser performance guarantee.

## Reclamation-point amendment — 20 November 2026

Amendment accepted after the repository agent's adversarial review of the plan
and of the implementation, under the pilot's advance authority of 20 November
2026; the preceding accepted decisions retain their status.

`keep-a-live-model-parsed` moves where the store is reclaimed, and leaves the
trigger at 125,000. Until this change every outermost operation emptied the
store once it held that many nodes, which could not tell a loaded document's
own graph from obsolete state. The Enigma I page mounts a document of 546,768
nodes, so its 214,278 binding entries were prepared again before every pose,
request and drawn frame, and an instruction showed its start and its end and
nothing between. It was the third document to meet the line, after the Curta
(the capacity amendment above) and the Voron-2 (the validation-boundary
amendment above).

Ordinary operations no longer reclaim, whatever the store holds. The trigger
is headroom for obsolete state only, and the store is reclaimed at it where
obsolete state is created:

- at the start of an outermost document load (`withDocumentLoad`, entered by
  `assertRenderable`);
- at the end of a refused load;
- when the viewer settles a validated document: abandoned (refused after its
  validation, or its viewer disposed during the load) at the trigger, or
  installed at the trigger plus the nodes that load added, so that an
  installation keeps its incoming graph;
- at every viewer's disposal, the last one still emptying the store whatever
  it holds.

A request made inside an open scope is honoured at the end of the outermost
scope; no reset happens inside a scope, every reset is still `resetStore()`,
and the generation still rises by exactly one per reset and only then. The
holders that rebuild by generation are unchanged.

The invariant this gives: at the start of every outermost operation that is
not a document load, fewer than 125,000 resident nodes belong to no loaded
document. Retention is bounded by the graphs of the loaded documents plus
that headroom, not by past publications, refusals or disposals. It rests on
one fact about the source, recorded so that a later change that breaks it is
visible: after load, no operation prepares expression text the loaded
document does not already hold.

`EXPRESSION_LIMITS.everyOperation` is a source-only switch for the widget's
own tests. When true, every outermost operation also reclaims at its start,
as before this amendment. Every test that forces pressure asserts that the
generation rose.

Measured on the Enigma I page (`enigma-i` at `081f4e6`), script only, with
draw calls skipped: the generation stayed 0 and the binding table was prepared
once across the mount and nine instructions; press tasks fell from between
2,398 and 7,225 ms to between 47 and 775 ms; the flap and the hood showed 46
and 124 distinct pictures instead of 2. The store is 115.6 MB resident on that
page, which the previous policy also held between operations. A reload raised
the generation once, at its start, and the first press after it took 66 ms.

Stated limits. In a page with more than one viewer, one viewer's load,
settlement or disposal empties the whole store at the trigger, and another
viewer's large graph then rebuilds once; per-mount accounting of graph sizes
is what a project that needs more would justify. The viewer's settlement
calls are not exercised by the widget's suite, which mounts no viewer; one
reload was measured on the page. No GPU's frame time was measured. The viewer
API and the document versions are unchanged.

[Design](../../../openspec/changes/archive/2026-11-20-keep-a-live-model-parsed/design.md)
and [evidence](../../../openspec/changes/archive/2026-11-20-keep-a-live-model-parsed/evidence.md)
record the cases, the tests and the measurements.

## Flat-pass amendment — 21 November 2026

Amendment accepted after the repository agent's adversarial review of the plan
and of the implementation, under the pilot's advance authority of 20 November
2026; the preceding accepted decisions retain their status.

`evaluate-a-pose-in-one-flat-pass` adds a second way of computing the values
this record's memoized walk computes, for poses only, and keeps the walk as
the reference and as the evaluator of everything the second way does not
cover. On the Enigma I page almost every one of 546,768 nodes depends on
whichever operation input moves, so each pose walked about 540,000 nodes,
about 100 ms. Keeping a node's value across passes while its inputs stand was
prototyped and does not pay there: there is almost nothing a moved input does
not feed.

**What it is.** A pose (`WidgetTree.update`, `admit`) of a document whose
binding table holds at least `FLAT_PASS.minimumBindings` entries (1,000)
first calls `prepareFlatPass(scope)`. Once per table and store generation the
part of the graph reached from the table's roots is compiled into a program
over typed arrays: a slot per covered node in one `Float64Array`, a kind per
slot (number or boolean), an operator and two operands per entry, the entries
laid out in segments by the set of inputs they depend on, in an order that is
also a dependency order. A run reads the program's inputs from the scope,
finds those that changed since its own last run, and runs only the segments
they meet. `valueOf` then reads a covered node from its slot, a comparison
handed out as the boolean the walk gives.

**What it covers.** Numeric literals, `$t`, binding names (which share their
root's slot), names read from the scope, unary minus as `-1 * v`, the
arithmetic operators, the comparisons and `==`/`!=`, and calls of twenty
named functions of the OpenSCAD context that never throw on numbers and keep
no state, wherever every operand is covered. Everything else stays with the
walk, lazy as it is: `&&`, `||`, a ternary, `===`, a member or index read,
`random`, `profileOverlap`, anything that can throw. The pass has no
operation that can throw, so every refusal a pose makes is still made by the
walk, at the same point and with the same message.

**Inputs a scope does not supply.** An input that is missing, is not a
number, or is reached through a member read on a primitive is absent for that
run, and takes off the pass only what depends on it: those nodes are neither
computed nor served, and the walk evaluates them if a pose reads them. An
input supplied again counts as changed whatever its value. The first design
declined the whole pass instead; its own parity proof showed twelve of 52
committed documents declining at every pose, because their tables name things
no pose binds (`_own`, `_j0`), and the rule was replaced before the change was
committed. Two scopes are still left to the walk whole: a driver map that is
not an object, and a driver named like a function the program calls.

**Who enters it.** Poses only. The clocked machine's solving, a running
program's ticks, `PathValue` and validation evaluate few nodes under many
scopes and are not routed through it; their path gains one comparison per
memo miss.

**Lifetime.** Programs are kept per table in a `WeakMap` that `resetStore()`
replaces, so every reclamation point of the amendment above drops them with
the nodes they index. Two documents on one page keep two programs.

**Counts.** `expressionMetrics().resolutions` still counts values computed by
the walk; `flatPassMetrics()` counts compilations, runs served in full and in
part, declines, failures and entries computed. Sharing ("one resolution per
pass") is asserted as before by tests that do not pose a tree.

**One ratified sentence is qualified.** "An entry SHALL be evaluated only when
something reads it" no longer holds for a pose served by the pass: a covered
entry is computed whenever an input it reads moves. Such an evaluation cannot
throw, changes no value and is counted apart.

**Proof.** A source-only switch makes the pass compare every covered value
with the walk's after each run. With it on, a parity proof poses every
committed document that carries a table, 52 of them, by both evaluators: all
are served, in full or in part, with no mismatch. Eleven deliberate
mutations of the implementation each turn named tests red.

**Measured** on the Enigma I page (`enigma-i` at `081f4e6`), script only, with
draw calls skipped: 444,782 nodes covered by 216,690 entries in 53 segments
over 14 inputs, compiled once at the load; 24,463,010 covered values compared
with the walk's over 55 poses with no difference; a key press frame 197 to
108 ms and 10 to 20 pictures in its two seconds; a key press's click 176 to
120 ms, a key selection's 152 to 67 ms, a wheel step's 108 to 29 ms; a flap
frame's run seven entries. Not measured: the program's memory on that page,
any GPU's frame time, another browser. The viewer API and the document
versions are unchanged.

[Design](../../../openspec/changes/archive/2026-11-21-evaluate-a-pose-in-one-flat-pass/design.md)
and [evidence](../../../openspec/changes/archive/2026-11-21-evaluate-a-pose-in-one-flat-pass/evidence.md)
record the cases, the tests and the measurements.

## Flexible-part roots amendment — 21 November 2026

`rebuild-a-flexible-part-for-less` adds a holder of node ids across
operations. The lifetime amendment says raw `NodeId` is operation-local and
names the holders that keep source and generation; the binding table (D4)
already kept ids with a generation. A flexible part now keeps the root of
each of its parameter expressions, in the order of their names, with the
store generation they were prepared in.

**Read.** A part's parameters are read in one `withExpressions` scope, for a
pose that is shown and for one that is judged alike. The generation is read
inside that scope, so no reset can fall between the check and the last
evaluation. When it is the held generation, each parameter is evaluated by
its root with no lookup of its text. Otherwise each text is prepared just
before its own evaluation and the roots are kept only after the whole read:
a refusal is the one evaluating the texts one by one gives, of the first
parameter in name order that refuses, and leaves the held roots as they
stood.

**Dropped** by a rebind to new expressions or a new table, and superseded at
the first read after any reclamation. The ids are numbers and keep nothing
of the store alive. The part adds no expression state the document does not
already hold, so the reclamation-point amendment's rule stands.

**Unchanged.** `expressions.ts`, the flat pass, and what
`expressionMetrics()` and `flatPassMetrics()` count: a read by root makes
the `valueOf` calls a read by text made, at the same point of the walk,
without the lookup.

**Proof.** Tests that count text lookups and scopes on a warm read, shown
and judged, red before the change; values and refusals compared with
`evalExpr`'s, a reclamation between two reads and pressure switched on over
a warm part included. Eight designed mutations and seventeen faults planted
in review turn named tests red or are shown equivalent.

**Measured** on the Enigma I page (`enigma-i` at `081f4e6`), script only,
with draw calls skipped: 36,415 parameters read on each frame of a key
press, 13 to 19 ms before and 8 to 10 after; 6,154,135 values compared with
`evalExpr`'s with no difference. Not measured: any GPU's frame time, another
browser. The viewer API and the document versions are unchanged.

[Design](../../../openspec/changes/archive/2026-11-21-rebuild-a-flexible-part-for-less/design.md)
and [evidence](../../../openspec/changes/archive/2026-11-21-rebuild-a-flexible-part-for-less/evidence.md)
record the cases, the tests and the measurements.

