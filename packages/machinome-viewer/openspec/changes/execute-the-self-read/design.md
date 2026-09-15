## Context

`solid-node`'s change `read-the-driven-coordinate` (ADR-121, framework
main `8e15791`) lets a running law READ the coordinate it drives. The
producer publishes such a program as a **version 6** document with no new
key — the self-read is a law edge whose `needs` intersects its own
`gives` — because a consumer reading a law edge as `f(end) − f(start)`
would read that coordinate at both ends, freeze the branch its gate
selects, and move the part by a different mechanism without saying so.

This viewer executes the published program (ADR-045, ADR-047): the whole
of `simulation/program.py`'s `JumpPlan` and `Edge` and
`simulation/run.py`'s `Run` are mirrored function for function in
`src/run/`, and the framework's committed conformance corpus is the
contract that keeps them one algorithm. ADR-121 therefore lands here as a
second implementation of one algorithm, held to one fixture.

**The rule of this cycle, stated before any decision.** Where this design
and ADR-121 disagree, ADR-121 is right. Where the TypeScript and
`program.py` disagree, `program.py` is right. The corpus is the contract;
nothing here invents a branch rule, a tolerance, or an ordering the
producer did not state.

**What is measured on this base**, and what the cycle must therefore
close, is in `proposal.md`: the committed corpus is two framework
regenerations behind, the older of the two is a DOCUMENT difference in
`Train` that replays green, and the newer is the three self-read
scenarios, which fail with the dial driven straight through its gap
(`wheel.turn` at `408` where the producer commits `359.5`).

### What the producer publishes, and what it does not

The self-read costs the document nothing. `Clearing`'s published program
(framework `tests/base_documents/clearing.json`, and the same edge in the
corpus's own copy) is one law edge:

```json
{"kind": "law",
 "needs": ["setter", "ring", "wheel.turn"],
 "gives": ["wheel.turn"],
 "plans": [{"skeleton": "(setter + ((ring * _j1) * _j3))",
            "jumps": [{"name": "_j0", "primitive": "floor", "level": "_b1"},
                      {"name": "_j1", "primitive": "==",
                       "level": "(_j0 - 0)"},
                      {"name": "_j2", "primitive": "floor", "level": "_b3"},
                      {"name": "_j3", "primitive": ">=",
                       "level": "((_b2 - (360.0 * _j2)) - 1.0)"}]}]}
```

with `_b1 = ((ring - 100.0) / 400.0)` and
`_b3 = ((wheel.turn + 0.5) / 360.0)`. Everything this cycle needs is
there: `needs ∩ gives = {wheel.turn}`; the skeleton does not name
`wheel.turn`; `_j0`/`_j1` are the rack's station over the RING and
`_j2`/`_j3` the band over the DIAL, and which is which is read off the
free names of each level.

## Goals / Non-Goals

**Goals.**

1. Execute a version 6 document's self-read edge exactly as
   `program.py` does, to the float.
2. Replay the framework's regenerated corpus (17 scenarios, 328 ticks)
   green, and keep the width guard honest about it.
3. Render and run a version 6 document in a real page, driven by the
   Curta's own clearing input.
4. Leave every document with no self-read edge byte-for-byte on the path
   it takes today, at the cost it pays today.

**Non-goals.**

- Changing the document. The self-read is `needs ∩ gives`; no key is
  added, none is read that was not read before.
- Changing the framework, or moving any of this viewer's code into it.
  The two packages remain separate processes over the unchanged
  `solid_node.viewer` entry point.
- Producing a corpus. The generator is the framework's; this repository
  copies the committed fixture and never regenerates it.
- Executing a driven GROUP with a self-read. The producer refuses one at
  class definition (ADR-121 §1), so no published document carries one;
  the loader guards the shape and refuses it by name rather than guessing
  a joint walk.
- A cheap exact path for a kinked-but-piecewise-affine skeleton. The
  Curta's `clamp01` station window makes every one of its self-read
  crossings a SEARCHED one, which is what it costs (D8); the framework
  records the same follow-up on its own side and neither is this cycle's.

## Decisions

### D1. The self-read is recognised at LOAD, and the reading is derived there

**Decision.** `loadProgram` recognises a law edge whose `needs`
intersects its `gives`, and derives — once, per driven end, at load — the
two-layer reading `program.py`'s `Edge._retained_ends` derives at
compile time. `ProgramEdge` gains one field:

```ts
/** The driven ends this edge's own law READS -- the `gives` whose id is
 * also one of its `needs` -- each with the two-layer reading of its
 * plan. EMPTY for every other edge, which is the one test
 * `edgeIncrements` makes before taking ADR-107's path unchanged. */
retained: (RetainedReading | null)[];
```

parallel to `gives` and `[]` — not `[null, …]` — where no driven end
reads itself, so the one test is `edge.retained.length > 0`. That is
`Edge.retained`'s own shape, corrected by the framework's implementation
notes against its design §6's prose, and the parallel array is what lets
`increments` and `cuts` index it beside `gives` with no lookup.

A `RetainedReading` carries exactly what `_Retained` carries:

- `own` — the driven id (`edge.gives[index]`);
- `dependent` — the plan's jumps that DEPEND on `own`, in the plan's own
  postorder;
- `outer` — `{ skeleton: plan.skeleton, jumps: <the independent ones> }`,
  a well-formed plan of its own because dependence is upward closed along
  the nesting;
- `affine` — whether the SKELETON is affine along the path.

**Dependence, and where the free names come from.** `_dependence` asks
whether the driven id is among the free names of a jump's ARGUMENT
SUBTREE, read off the plan where every inner jump is already a
placeholder: the node's level names the driven id, OR it names the
placeholder of a node that depends on it. The published `level` IS that
argument — `_published_plan` writes `'level': _renamed(jump.argument, …)`
— so the viewer asks the same question of the same expression. The free
names must be taken through the document's **bindings table**:
`Clearing`'s band gate reaches `wheel.turn` only through `_b3 = ((wheel.turn
+ 0.5) / 360.0)`, and a viewer reading `freeVariables` alone would sort
that node INDEPENDENT and integrate the whole tick under one branch.
`loadProgram` already owns exactly this closure — `namesOf(expression) =
table.closure(freeVariables(expression))` — and it is reused verbatim.
Placeholders are then propagated in plan order, as `_dependence` does,
because a plan lists its jumps in postorder and a placeholder is always
defined before it is named.

**Affinity is READ, not recomputed.** `_Retained.affine` is
`_affine_in_sources(plan.skeleton)` — and that is precisely what the
producer already publishes as the edge's per-end `affine` flag for a
plan-bearing law (`Edge._affine_ends`: `if plan is not None:
found.append(_affine_in_sources(as_node(plan.skeleton)))`). The viewer
takes `edge.affine[index]` and computes nothing. This is ADR-047's rule
holding: what compile time decided is read, never recomputed.

**Alternative rejected: a `reads` array published on the edge.** That is
the shape `Constraint` suggests and the framework rejected on its own
side, because the export spec says in its own words that the free names
of a law edge's expressions are exactly the ids in `needs`. A separate
list makes that sentence false and needs a document key. Keeping the id
in `needs` keeps it true, and `needs ∩ gives` is the whole recognition.

**Alternative rejected: deriving the reading lazily, per tick.** The
dependence split is a function of the plan alone, so per-tick derivation
would recompute a bindings closure on every step of every machine that
carries a self-read. It is compile-time work on the producer's side and
load-time work here, which is where ADR-054 already put the constraint
table.

**Three refusals at load, by name** — beside the refusals for an
unreadable version, an unresolvable bindings table, an inexecutable
program and an undeclared name:

1. A law edge whose `needs ∩ gives` holds MORE THAN ONE id, or whose
   `gives` has more than one entry while any of them is read. ADR-121
   refuses a driven group with a self-read at class definition, so no
   published document carries one; the loader is the guard, and it says
   that a relation reading its own driven end drives one coordinate.
2. A self-read whose driven id is NOT a bank coordinate — a published
   intermediate. The producer refuses this at construction ("a retained
   value is a history and only a coordinate the run owns keeps one") and
   the loader says the same, because a run banks nothing for an
   intermediate and would have no retained value to read.
3. A self-read edge whose plan's SKELETON still names the driven id. The
   producer refuses a continuous read by relation identity; here the
   check is free, because the skeleton's free names are already closed
   over the bindings table by the existing per-edge expression check. A
   read that survives the skeleton makes the relation a differential
   equation that the difference of two evaluations does not define, and
   the message says so — including that a bare remainder is not a switch,
   since with the quotient fixed `a % b` leaves `a − q·b`, which still
   carries the coordinate's slope.

**A version 6 document with NO self-read edge is fine and is stated so.**
The version is a property of the content and the loader judges the
content: nothing keys off the number 6 except the rendered-version list.
Equally, a version 5 document is never given a self-read reading, because
the producer would have published it at 6 — but the loader does not test
the version to decide, it tests `needs ∩ gives`, which is the same
question `serializer.py`'s `_reads_its_own` asks.

### D2. The step: the two-layer walk, mirrored in `jumps.ts`

**Decision.** `_Retained` and `_Walk` live in `src/run/jumps.ts`, beside
`planIncrement` and `planCuts`, and reuse that file's own `partition`,
`branchesAt`, `levelAt`, `surfacesOf`, `branchOf` and `bisect` rather
than copies. `edges.ts` dispatches on `edge.retained` and `run.ts` knows
only that an edge may report a landing. That is the same seam the
framework has (`_Retained` beside `JumpPlan` in `program.py`, `Edge`
dispatching, `Run` applying), and it keeps every branch rule in the one
file that owns branch rules.

**Layer 1 — the source partition, UNCHANGED.** `partition` is called over
`reading.outer`: a plan whose jumps are the independent subset. Its
crossings are found over the whole tick and recorded, its branches read
at the MIDPOINTS of its pieces, and `merged`/`deduplicated` fold two near
cuts into one — all of it ADR-107 exactly as it stands, valid because
those levels do not depend on the walk. Where the independent subset is
empty the partition is `[0, 1]` and no evaluation is made.

**Layer 2 — the walk, inside each layer-1 piece.** At the walk's left end
`t` the driven coordinate holds `ownLeft`: the tick's committed value at
the start, and what the cuts already taken placed it at afterwards. Then,
per piece:

1. **Decide** every dependent node's branch in the plan's postorder, with
   the driven coordinate at `ownLeft` and every OTHER source at `t` — the
   piece's LEFT END, never its midpoint. A midpoint reading is wrong for
   a MIXED level such as `ring − wheel`, which can cross inside the piece
   by the sources' motion alone: the branch read past that crossing is
   the far-side branch, and the piece's own left half would be integrated
   under it.
2. **Substitute** and evaluate. With the branches fixed the skeleton does
   not name the driven coordinate (D1 refusal 3), so
   `own(s) = ownLeft + skeleton(s) − skeleton(t)` is one ordinary
   evaluation.
3. **Cut** at the FIRST surface any dependent level reaches strictly
   inside the piece.
4. **Land** the coordinate on the far side (D4), record a `Crossing`,
   and decide again from `t = s*`.

Until the layer-1 piece is exhausted or `limits.maxCrossings` cuts have
been taken, which is the existing refusal and needs no new one.

**Rule (c), the level exactly ON a surface at a left end.** This is not
an edge case: it happens at EVERY cut the walk takes, and at a tick's
start after a stop, a restore, or a rest default that lands on a digit
boundary. Such a node takes the branch its OPERATOR gives; the level is
then followed under the tentative branches, and if it LEAVES the surface
into the other branch's region the node is FLIPPED at `left` — a
zero-length piece — and every branch is decided again. A node flipped
twice refuses the tick as chattering.

Two details from the framework's implementation notes, which its ratified
prose did not have and which this cycle takes as written:

- The probe that answers "does the level leave the surface" is the level
  at the FIRST of the `subdivisions` samples at which it differs from the
  surface — an inequality between two evaluated floats, no tolerance.
- The branch a flipped node takes is **not** the branch at that probe. It
  is `branchOf(jump, nextAfter(surface, probe))` — the region IMMEDIATELY
  on the side the level departs to. For a comparison or `sign`, whose two
  regions are the only ones there are, that is the same answer; for
  `floor`, `ceil` and `%` a sample a whole tooth away names a branch the
  piece never enters, and taking it changes the RATE and refuses the next
  probe as a sliding mode.

**Rule (d), a crossing near a piece's left end is NOT folded away.**
`merged` and `deduplicated` belong to layer 1 only. In layer 2 every
crossing with `where > t` is returned, one a hair inside the left end
included: folding it would integrate the piece under the near-side branch
and drive the part through its gap. The framework's implementation found
this the hard way (its notes, "a genuine crossing a hair inside a piece's
left end was dropped"), and the ratified simulation spec states it
outright.

**The first cut, solved.** Where the jump's level is affine AND the
skeleton is affine — `jump.affine && reading.affine`, both published —
the level is determined on the piece by its two endpoint values, and the
EARLIEST of the surfaces between them is taken. Note the difference from
ADR-107's `crossingsOf`, which returns ALL of them: under a self-read the
path is known only until the branch changes, so the walk takes the first
and re-decides. Three tooth windows in one tick are still three throws,
as three successive pieces rather than three surfaces of one solve.

**The first cut, searched.** Anything else is sampled at
`limits.subdivisions` and bisected to `limits.crossingTolerance`, with
the three corrections the framework's implementation records and the
ratified spec requires:

- a sub-interval whose level does not MOVE crosses nothing and is
  skipped — a dependent node whose branch HOLDS the driven coordinate
  sits on the surface it was landed at for the whole piece, and an
  inclusive search would report that surface again and again;
- a surface EQUAL to the level at a sub-interval's LEFT sample is not a
  crossing of that sub-interval (at the piece's left end it is rule
  (c)'s, and at an interior sample it was reported in the sub-interval
  before). Without this exclusion `bisect` starts from a `below` of zero,
  every round takes the `else` arm, the bracket collapses onto the
  sub-interval's right end, and the landing then carries the coordinate
  to the NEXT surface — a whole unit per phantom;
- the surface the path reaches FIRST is the one NEAREST the left sample,
  not the lowest, because `surfacesOf` counts upward and a DESCENDING
  level crosses them in the other order; and a right sample EXACTLY on a
  surface is the crossing at that sample.

**The driven coordinate's own delta is ZEROED inside the walk.** The
edge's `delta` map is built from `edge.needs`, which under a self-read
includes the driven id, so `along()` would otherwise advance the
coordinate by the increment the tick handed it. `_Walk.__init__` sets
`self.delta[self.own] = 0.0`, and the TypeScript must too: what the
coordinate holds on a piece is what the pieces before it produced, never
an increment. This is the single easiest place to be silently wrong, and
the corpus's `StoppedClearing` — where the setter drives the same
coordinate — is what would catch it.

**Two dependent nodes crossing at one fraction are ONE cut**, within
`crossingTolerance`, and each takes its far side.

**Alternative rejected: one flat partition over all jump nodes, with the
driven coordinate held at its tick-start value.** That is what a version
5 consumer effectively does and what the base measures at `408` instead
of `359.5`.

**Alternative rejected: writing a second, self-read-only copy of the
partition.** It would drift from `partition` at the first correction
either file received, which is exactly the failure the corpus exists to
prevent.

### D3. Where a walk's numbers come from, when JavaScript has no `nextafter`

`math.ulp`, `math.nextafter` and `math.copysign` have no JavaScript
equivalents, and the landing is defined in terms of all three. They are
added to `jumps.ts` as the producer defines them, over a
`Float64Array`/`BigInt64Array` view of the same eight bytes:

```
ordinalOf(v)   bits = int64 of v; bits >= 0 ? bits : -(2n**63n) - bits
fromOrdinal(n) n < 0 ? bits = -(2n**63n) - n : bits = n; float64 of bits
```

which is `_ordinal`/`_from_ordinal` exactly: adjacent floats differ by one
here at any magnitude, with no tolerance anywhere, and `-0.0` maps to the
same ordinal `0` as `+0.0` — the ±0 handling the framework's docstring
means. `BigInt` rather than `number` because the ordinal range is the
whole of int64 and `2**63` is not exactly representable as a double.

On top of them:

- `ulpOf(v)` — `fromOrdinal(ordinalOf(|v|) + 1n) − |v|`, and the walk
  uses `5e-324` where `own_star` is zero, as `_far_side` does
  (`math.ulp(own_star) if own_star else 5e-324`);
- `nextAfter(x, y)` — `y` when `x === y`, otherwise `fromOrdinal` of
  `ordinalOf(x) ± 1n` toward `y`;
- `copySign(1, d)` — `d < 0 || Object.is(d, -0) ? -1 : 1`.

Each gets its own node test against values the producer's own functions
answer, including `±0`, the smallest subnormal, `1.0`, and a value across
a binade boundary.

### D4. The far-side landing, and what the run commits

**Decision.** After a cut that MOVED the driven coordinate, the
coordinate is committed at the nearest representable value on the FAR
side of the surface: the segment's own arithmetic gives `own*`, a bracket
is found by stepping out from it with the stride doubling from one ulp —
in BOTH directions, because the arithmetic lands past the surface about
as often as it lands short — and the bracket is bisected in ORDINAL float
space until the two values are adjacent. The far one is taken. Where the
piece did NOT move the coordinate there is nothing to walk: the level
crossed by the sources' motion while the gate held, and the coordinate
stands where it stood. Where two nodes were crossed at one fraction, each
is walked in turn, in the plan's postorder, judging each with the OTHER
nodes at the piece's NEAR-SIDE branches — which is what makes a knife-edge
gate hold from both sides, and is the framework's `_land` verbatim.

**The run commits that float.** `edgeIncrements` gains a `landings`
output; `Run.pass` threads it; `Run.integrate` applies it to `committed`
in BOTH places it builds one — after the full-stretch pass and after the
segment pass — and BEFORE the bounds are examined, so that:

- a declared range on the same coordinate in the same segment OVERWRITES
  the landing, because a physical bound is a bound of the coordinate
  itself (`StoppedClearing` is the fixture for this);
- `reachedBounds` sees the value the tick will actually commit.

`value + delta` is not enough on its own: `x + (y − x) !== y` for about
six pairs of floats in a hundred, so an exact landing inside the plan
would still be a ulp out in the bank the next tick starts from — and a
ulp back toward the surface is the ENGAGED side of the gate.

**An unlanded landing is LOUD.** Where no bracket is found within 200
doublings the framework raises `LandingInvariantError` rather than
committing `own_star`. The viewer adds the same class. It is unreachable
by construction — a cut exists because the level crossed the surface, so
the branch differs somewhere on either side of it, and 200 doublings of a
ulp cover every distance a double expresses — and it is raised rather
than committed because committing `own*` would commit the one value the
design says is never committed. No test can reach it; the code says so
where it throws.

**Alternative rejected: committing what the segment's arithmetic gives.**
That is the rule the framework's first draft adopted and measured out:
6.3 % of crossings left the gate ENGAGED after the cut and another 12.7 %
were refused as `TooManyCrossings`. With the far-side landing: 200 000
randomized crossings, zero re-engagements, zero refusals.

**Alternative rejected: snapping the coordinate to the surface solved
from the level.** Measured and rejected on the producer's side: taking a
slope from two evaluations one unit apart and dividing by it loses about
a thousand ulps to cancellation.

### D5. The refusals a TICK can make, and the protocol

**Decision.** Two tick refusals are added and one protocol union widens.

- **Chattering** — a node flipped twice at one left end — is an
  `UnsupportedLaw`, which is what `_chattering` raises. It therefore
  reports as `kind: 'law'` with no protocol change, and its message is
  the producer's: the relation, the coordinate, the primitive, that a
  sliding mode is not a mechanism, and that the tick committed nothing.
- **An unlanded landing** gets its own class `LandingInvariantError`, as
  it does in `program.py`, and `RefusalKind` gains `'landing'`. The
  alternative — reusing `'stop'`, which `StopInvariantError` already
  carries — would report a broken landing invariant as a broken stop
  invariant, and the two name different things in their messages.

Widening `RefusalKind` is safe and does not move the API version on its
own: `kind` crosses only the worker boundary INSIDE the published bundle,
and the one consumer on the main thread reads `reply.message` and never
`reply.kind` (`viewer.ts` line 902). The API version moves for D6's
reason, not this one.

`Run.integrate`'s catch must list the new class beside `RunConflict`,
`TooManyCrossings`, `UnsupportedLaw` and `StopInvariantError`, so a tick
that fails after a cut commits NOTHING — not the landing, not the
crossing, not the bank.

### D6. Versions: `documentVersions` 1–6, API 15, and what does not move

**Decision.**

- `package.json`'s `solidNodeDocumentVersions` becomes
  `[1, 2, 3, 4, 5, 6]`; `RENDERED_VERSIONS` in `viewer.ts` follows, and
  `version.test.ts` keeps pinning the two to each other and to the
  package.
- `solidNodeViewerApi` rises **14 → 15**. Executing a version 6 document
  is a capability a host may require BEFORE it mounts — the precedent is
  exact: `run-in-the-worker` raised the API to 8 when `documentVersions`
  grew to include 5, and `drive-the-run-by-touch` and
  `draw-what-a-part-carries` deliberately did NOT move the document list
  because `controls` and `markings` are additive. This one is not
  additive: a bundle at API 14 refuses the Curta by name.
- **`bundle.py`'s `RELEASED_DOCUMENT_VERSIONS` does not move.** Its
  comment says what it is — "what every viewer released so far reads. A
  consumer that receives no `documentVersions` is entitled to assume
  exactly this" — and the only released viewer is 0.1.0, which reads
  `[1, 2, 3, 4]`. It is a floor for builds that predate the declaration,
  not a mirror of this build.
- `describe()` reports the new list with no change, because it reads
  `package.json`.
- Two code sites test the version NUMBER today and must become `>= 5`:
  `viewer.ts`'s `document.version === 5 || program !== undefined` gate,
  and `capture.py`'s `carries_program`, which returns
  `document.get("program") is not None or document.get("version") == 5`.
  Both are load-time gates on "does this document carry a program", and a
  version 6 document does by definition. Each gets a red-first test.
- `README.md`'s version table row becomes `| 0.2.0 | 15 | 1, 2, 3, 4, 5,
  6 |`. The parenthetical under it about 13 being skipped stays as it is.
- `CHANGELOG.md`'s existing 0.2.0 bullet for the API-8 rise says "A
  version 6 document is refused by name and by list". Within one
  unreleased release that sentence cannot stand beside a bullet saying a
  version 6 document runs, so its last clause is amended to name version
  7 — the smallest true edit, made where the untrue claim is, rather than
  left for a reader to reconcile.

**The numbering hazard, recorded and not acted on.** The unmerged branch
`slide-and-turn-parts` carries a delta claiming API version **13**, and
ADR-055 is an unused gap that the same in-flight cycle is expected to
take (its tasks name "the confirmed ADR-053 successor"). This cycle takes
API **15** and **ADR-057**, which collide with neither whatever order
they integrate in. Reconciling that branch's own numbers is its
integration's business, not this cycle's.

### D7. The corpus, and the width guard

**Decision.** `src/running-corpus.json` is replaced **byte for byte** by
framework main `8e15791`'s `tests/running-corpus.json`. Nothing here
edits it and nothing here regenerates it: it is the producer's own run,
and every expected value in it is a value the framework PRODUCED.

The census in `running-corpus.test.ts` becomes 17 machines entries, 14
distinct names, 328 ticks.

The width guard gains the producer's three new `REQUIRED` features,
computed the way `tools/generate_running_corpus.py`'s
`uncovered_features` computes them, over the committed fixture only:

- `'a law that reads the coordinate it drives'` — some law edge of some
  machine's document has `needs ∩ gives` non-empty;
- `'a self-read coordinate holding at its gate while its input moves on'`
  — for such an id, a tick in which its bank value is UNCHANGED from the
  previous tick while at least one id of `program.sources[<that id>]`
  that is itself in the bank DID change;
- `'a tick carrying both a self-read crossing and a stop'` — a tick with
  a non-empty `stops` list one of whose `crossings` names a self-read
  coordinate.

The "narrowed corpus is refused" case is extended to name one of the
three, so the guard is red exactly when the corpus is narrowed.

**The `Train` document difference is taken with the rest and is not a
separate step.** It is `publish-only-what-runs` catching up: `Train`'s
`program.intermediates` loses `wheel.turn` and `program.sources` loses
its `"wheel.turn": []` entry, the program `identity` unchanged. Measured
on this base, both `Train` scenarios replay GREEN against the new file,
so it changes no number this engine produces — but the copy is byte for
byte or it is nothing, and `running-corpus.test.ts`'s first assertion is
that it came from the generator unedited.

**Alternative rejected: keeping the old corpus and adding the three
scenarios by hand.** The fixture's authority is that the framework's run
produced every value in it. A hand-merged corpus has no such author.

### D8. What it costs

**Decision.** `cost.test.ts` gains three printed measurements beside the
four it already prints, each with a floor an order of magnitude below the
bench, as that file already does:

- the corpus's `Clearing` machine, whose skeleton IS affine, so its
  self-read crossings are SOLVED;
- the committed Curta fixture (D9), whose `clamp01` station window makes
  `_affine_in_sources` answer false on the skeleton, so every one of its
  self-read crossings falls to the 64-sample search plus its bisection —
  six dials of it;
- `Train` again, asserted NOT to move: a machine with no self-read pays
  one array-length test per edge per tick and nothing else.

The producer's own numbers, for the same shapes, are the comparison:
`Clearing` 1 349 ticks/s and `CurtaInterface` 24.4 ticks/s in Python, and
`Train`'s graph-evaluation count identical before and after (80 over ten
ticks). This viewer's base numbers to read them against are, measured on
this worktree: `Train` 73 188 ticks/s, the Pascaline at `dt = 1/240`
32 942 ticks/s, the lock advancing its key 132 ticks/s.

**Whether the Curta fixture runs at the viewer's default `1/240 s` step
is a question this cycle must ANSWER, not assume.** If it does not, that
is a FINDING reported to the pilot — never mended by widening a
tolerance, coarsening the step, or skipping a sample. The framework
recorded the same shortfall shape on its own side and named the same
follow-up (a cheap exact path for a piecewise-affine skeleton).

### D9. The acceptance: a version 6 document in a real page

**Decision — two levels, one new fixture.**

**Engine level: nothing new is committed.** The corpus's own `Clearing`
and `StoppedClearing` entries carry version 6 documents verbatim
(`document.version === 6` in all three), so `Engine.load` over a version 6
document, the derived reading, and the refusals are all testable against
the fixture already being copied in. The framework's
`tests/base_documents/clearing.json` is deliberately NOT committed: it is
the same program the corpus already carries, its `root` names a mesh
`wheel` that does not exist, and a second copy of one program is a second
thing to keep in step.

**Browser level: `tests/fixtures/clearing/`.** The mountable fixture is
the framework's own `tests/clearing_project/machine.py:CurtaInterface` —
six dials in two rows of three, one `clearing` input, and the project's
own source-backed numbers (rack starts `9.75` and `10.5` ring degrees,
pitches `degrees(3.75/52)` and `degrees(3.75/49.55)`, `36°` per tooth,
stations `(130 if counter else 0) − 20·place`, band half-width `0.5`).
It is the right fixture for three reasons: it is a version 6 document
with SIX self-read edges rather than one; it is the searched path, which
the corpus's `Clearing` is not; and it is the Curta's own interface, the
mechanism ADR-121 exists for.

**How it is produced, reproducibly.** From a **throwaway copy** of a
solid-node checkout at main `8e15791` — a copy, so nothing is written
into the pilot's framework checkout — with the workspace environment:

```
PYTHONPATH="$PWD" solid export \
    tests/clearing_project/machine.py:CurtaInterface \
    -o <dir> --no-widget
```

`viewer.json` is copied in **verbatim** and its byte count recorded. The
geometry is NOT: each distinct model path the document names holds a
stand-in 684-byte binary unit cube, the same one `tests/fixtures/pascaline`
already carries, exactly as the `lock` and `touched` fixtures do — this
repository tests a run, not a mesh, and `Arbor`'s cylinder shows what a
cube shows. `tests/fixtures/clearing/README.md` says in that fixture's
voice what is verbatim, what is a stand-in, and which framework commit it
came from; `tests/support.py` gains `CLEARING = FIXTURES / 'clearing'`
and a plain test that every model path resolves.

**What the page proves**, driven by the document's own `clearing` input
and asserted against the framework's own numbers for the same machine:

1. the document MOUNTS — no refusal, a run exists, no tick taken, the
   bank at the published rest values;
2. one full sweep of `clearing` leaves each of the six dials within the
   band half-width of a multiple of 360 in the sweep's direction, at a
   value that reads DISENGAGED under the viewer's own arithmetic;
3. a SECOND sweep moves no dial at all — bit for bit, not within a
   tolerance — while the clearing input completes its whole travel;
4. no stop is recorded and every crossing is in the crossing record;
5. two inspected screenshots in `tests/_shots/`, as the lock and
   Pascaline acceptances write their own. Pixels are evidence.

**Alternative rejected: mounting a corpus machine's document.** The
corpus carries only the program-bearing keys — `format`, `version`,
`drivers`, `instructions`, `bindings`, `program` — and no `root`. There
is nothing to render.

## Risks / Trade-offs

- **The landing is a float-space search, and the two runtimes must find
  the same float.** They do not compute the same `own*` — only one within
  the run's agreement window — and the bracket is grown from it. What
  makes them agree is that the bisection converges on a BOUNDARY OF THE
  BRANCH FUNCTION, a property of the published level expression and of
  IEEE arithmetic, not of `own*`; two starting points a few ulps apart on
  the same side of the same surface reach the same adjacent pair. The
  residual risk is a piece whose bracket spans more than one surface,
  where the two could converge on different boundaries; the corpus is
  where that would show, and it would show as a bank divergence on the
  NEXT tick rather than as a near miss on this one. → Pinned by
  `Clearing` at two step sizes and by the second-sweep assertion, and
  reported rather than tolerated if it appears.
- **The corpus's float tolerance is `1e-9` but a HOLD is exact.** A
  landing one float short of the far side re-engages the gate, and the
  dial then turns a whole tooth on a later tick — a divergence of order
  36, far outside `1e-9`. So the corpus pins the landing not by the
  tightness of its tolerance but by the tick after it, which is exactly
  why `Clearing` runs for 24 ticks after its first cut. Stated here
  because it looks like a gap and is not.
- **`_Walk` is the largest single piece of algorithm this repository has
  mirrored**, and the framework's own implementation found three blocking
  defects in it after ratification (a phantom crossing, a flip to a
  branch the piece never enters, a dropped crossing a hair inside a left
  end). → All three are written into D2 as rules, and each gets a node
  test of its own in `jumps.test.ts` rather than being left to the corpus
  to catch.
- **A version bump refuses nothing that used to render**, but it does
  mean a host at API 14 and a producer at version 6 disagree silently
  unless the host checks. → That is what `documentVersions` is for, and
  `describe` reports it.
- **The Curta fixture may not run at `1/240 s`.** → Measured and
  reported (D8), never mended by loosening anything.
- **`solid export` of a framework test machine needs OpenSCAD and writes
  a build tree.** → Run from a throwaway copy; the fixture is the
  document plus stand-in cubes, and nothing here regenerates it.

## Open Questions

1. **Should the loader refuse a version 6 document that carries no
   self-read edge?** No: the version is a property of the content, a
   producer is entitled to publish 6 for a program that happens to have
   none after an edit, and refusing it would turn away a document this
   engine executes correctly. Stated in D1 and in the delta spec rather
   than left to inference.
2. **Does any host read `RefusalReply.kind`?** Not in this repository
   (D5). If a host outside it does, `'landing'` is a new value it has not
   seen; the field has never been documented as closed, and the API
   version rises in this cycle anyway.
3. **`RELEASED_DOCUMENT_VERSIONS` will keep drifting from what the build
   reads** as the list grows, which reads oddly. It is correct as
   written — it is a floor for builds that predate the declaration — and
   is left alone; a later cycle may want to rename it.
