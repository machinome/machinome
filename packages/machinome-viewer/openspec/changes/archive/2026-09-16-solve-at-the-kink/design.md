# Design: solve at the kink

## 1. The finding

`src/run/jumps.ts` and `src/run/run.ts` decide between SOLVING a followed
quantity and SEARCHING it by reading one published boolean:

- `jumps.ts:423` `if (jump.affine)` — a jump level's crossings;
- `jumps.ts:898` `if (jump.affine && this.reading.affine)` — a self-read
  walk's crossing;
- `run.ts:851` `if (edge.affine[index])` — a stop's localization.

The producer publishes that flag as `shape in ('constant', 'affine')`,
and ADR-123 made its own classification THREE-valued without moving the
flag. So a quantity built over `abs`, `min` or `max` — `clamp01` is
`min(max(x, 0), 1)`, and `clamp`, `ramp` and `piecewise` are built on it
— arrives here as `affine: false` and is sampled 64 times and bisected,
where three divisions would do and would be exact.

The gap is entirely in the FALSE branch of those three tests. Nothing the
producer publishes as affine changes.

## 2. The base, measured

Worktree `solid-node-viewer/WTs/curta-speed`, branch `curta-speed`, head
`a35957d`; node v24.11.1; one job at a time. `npx vitest run` → 37 files,
962 tests, 37.3 s; `npx tsc --noEmit` clean.

**This cycle stacks on `mirror-the-kink-guard`** and is measured against
the refreshed corpus, because `KinkedStop` is the scenario whose float
this change moves. Applied in order: the guard first, this second.

Do NOT run `npm ci`, `npm install` or `scripts/check-dist` in this
worktree: `solid_node_viewer/widget/node_modules` is a SYMLINK to the
primary checkout's and `npm ci` through it empties the primary's.

## 3. The mechanism, and why the document need not change

ADR-123's `_shape_of` is structural: it reads the expression tree and
nothing else. The viewer holds the same expressions — that is what
`prepare` interns and what `PathValue` and `foldedNames` already walk —
so it can compute the same shape. The only reading that differs is where
a CONSTANT comes from: the producer's graph spells a branch placeholder
`$j…`, the published document spells it by the jump's own `name`, so the
viewer's classification takes the plan's jump names as its constant set
rather than a prefix.

**Validated against the flag, which is the only external check there is.**
Mirroring `_shape_of` over the published documents and their bindings
tables and comparing `shape in (constant, affine)` with the published
`affine`:

| document | published flags | disagreements |
| --- | --- | --- |
| the refreshed corpus's 20 documents | 39 driven ends + 34 jump levels = **73** | **0** |
| the operating Curta (`OperatingCurta`, version 7) | 268 driven ends + 547 jump levels = **815** | **0** |

and the Curta's census reproduces the producer's own published one
exactly — 28 kinked plan-bearing skeletons, 41 unclassified, 183 affine
plan-less laws, 16 kinked plan-less laws, 532 affine and 15 kinked jump
levels. Two independent implementations, one number.

### D1. The shape

Over the interned DAG, walking INTO the bindings table (a binding name
has the binding's root as its one child, exactly as `PathValue`'s
`childrenOf` and `foldedNames` already do):

| node | shape |
| --- | --- |
| numeric literal | constant |
| a name in the plan's jump-name set (a branch placeholder) | constant |
| any other source name | affine |
| a bindings-table name | the binding's own shape |
| every child constant | constant |
| unary `+`/`-` | the child's, if movable |
| `+`, `-` | kinked if either side is, else affine |
| `*` with one CONSTANT side, `/` by a constant | the moving side's |
| `abs`, `min`, `max` over movable children | **kinked** |
| anything else | unclassified |

"Movable" is constant, affine or kinked. A call with no arguments is
unclassified, as the producer's `if not node.children: return None` makes
it. `$t` is unclassified: no published running expression names it, and
guessing would be a silent divergence from the producer, which has no
such node at all. A cyclic bindings table classifies as unclassified
rather than recursing — the loader refuses one anyway.

**The classification is computed at LOAD**, once per published quantity,
and stored where the run already reads the flag: beside `ProgramPlan`'s
skeleton, beside each `ProgramJump`, beside each `RetainedReading`, and
per driven end of a law edge (for the plan-less case). Computing it in
the run would be work per tick for an answer that cannot change.

**It never weakens the published flag.** The solve path for
`affine === true` is untouched; the new branch is reached only where the
flag is false. Where the viewer's shape says constant-or-affine the
producer's flag already says true (measured above, 888 quantities), so
the two paths never disagree about the same quantity; if they ever did,
the flag wins and a test says so (D6).

### D2. The kink inventory and the breakpoints

A kink node's LEVEL is the argument of `abs`, and the DIFFERENCE of the
two operands for `min` and `max`. The producer mints a fresh `a - b` node
for that. **This viewer mints nothing**: it holds the two operand node
ids and evaluates `a − b` as the subtraction of two evaluations of the
same DAG. That is the same float — IEEE subtraction of the same two
operands — and it keeps the interning table free of nodes no expression
names, which `expressions.ts` guards deliberately.

Breakpoints over a stretch `[left, right]`, mirroring `_KinkCuts.between`:

1. kinks in the expression's own postorder, so a kink nested inside
   another's level is cut first;
2. for each, over each sub-interval the earlier kinks have produced,
   evaluate its level at the two ends; skip where the two are equal or
   not finite (a level that does not move reaches nothing), and skip
   unless zero lies strictly between them;
3. the zero is `low_t + (high_t − low_t)·(0 − low)/(high − low)`, kept
   only when strictly inside its sub-interval;
4. fold into the sub-division under the CROSSING tolerance, the
   partition's right end pinned at the stretch's own `right` — which is
   why `merged` gains an `end` parameter instead of its hardcoded `1`.

Returns the interior breakpoints only.

### D3. A breakpoint is not a crossing

The load-bearing rule, and the reason every other answer stays
bit-identical. A breakpoint is not pushed to `crossings`, does not enter
`partition`'s cut list, does not reach `land` or `farSide`, and does not
count toward `maxCrossings`. It exists only inside a solve.

### D4. The three sites

**(a) `crossingsOf` (a jump level).** The affine body becomes a local
`solved(left, right, closed)`; `closed` takes the right end inclusively
and drops a surface equal to the piece's own left value. Where the level
is kinked: compute the breakpoints under the same `values` the level is
read at (`along(start, delta, t)` plus the piece's `inner` branches), and
if there are none, solve over the whole piece — the level IS affine over
it. Otherwise solve each sub-piece left to right with `closed` true for
all but the last, and pass the concatenation through the existing
`deduplicated`, whose own comment says it exists for exactly this.

**(b) `Walk.crossing` (a self-read).** Mirrors `_crossing`. If
`jump.affine && reading.affine`, unchanged. If either shape is
unclassified, search, unchanged. Otherwise: cut the piece at the
SKELETON's breakpoints (under this piece's branches), and cut each of
those at the LEVEL's breakpoints — located INSIDE one skeleton sub-piece,
with the driven coordinate read by interpolation between that
sub-piece's two ends, because `ownAt` is affine only there. Solve each
sub-piece left to right and return the first surface found; `closed` is
true for all but the very last sub-piece of the very last skeleton piece.
The ordering is an ORDER OF COMPUTATION and not merely of concatenation.

**(c) The stop (`run.ts`'s `locate` through `edges.ts`'s `edgeCuts`).**
`locate` takes the solved path when the published flag is true OR the
viewer's shape is kinked. `edgeCuts` then supplies the breakpoints:

- a law with a jump plan and a kinked skeleton: `planCuts`'s partition,
  plus the skeleton's kinks located inside each piece with that piece's
  branch readings substituted (a placeholder is constant only within its
  own piece), merged;
- a self-read law: the walk's own cuts, which gain the skeleton's kinks
  inside each branch reading — asked only when the caller wants cuts, so
  an ordinary tick pays nothing for them;
- a law with NO plan at all: its own kinks over the step as one piece.
  `edgeCuts` returns `[]` for such a law today, which sends `locate`
  through the one-division fast path STRAIGHT THROUGH the kink — not a
  rounding error but a wrong stop, and the reason `KinkedStop` exists;
- a kinked law no kink of which is reached over this step: an EMPTY list,
  and the one-division fast path stays, because the path really is affine
  over the whole step. "Empty cuts means affine" is an invariant worth a
  test of its own.

### D5. Where the kink level is evaluated, and the constraint that decides it

`src/run/edges.test.ts` asserts, as a structural test, that
`program.ts` is the ONLY module under `src/run/` that calls `valueOf` or
`evalExpr`: "no module under src/run/ evaluates through a scope of its
own". The prototype tripped it. So the kink level's evaluation lives in
`program.ts` beside `evaluateExpression`, and `jumps.ts` imports it.

It stays on the PLAIN evaluator, as the producer left `_KinkCuts` on
`GraphValue.evaluate`, and the number that says this is the right call
for now: on the `clearing` fixture the kink levels are **960 of the
prototype's 2 724 evaluations/tick, in 96 calls**; on `Clearing`,
`Train`, the Curta carriage and the whole corpus they are **zero**. A
path-valued kink level would chase a third of a cost that has already
fallen 11.7×, at the price of another `PathValue` per kink per piece with
its own binding discipline. Recorded as a follow-up with its number, not
taken.

### D6. The flag-agreement contract

The viewer's classification is a SECOND implementation of the producer's,
and the only external check on it is the flag the document already
carries. So the suite asserts, over every document it holds — the 20
corpus documents and the committed fixtures — that the quantities the
viewer finds constant or affine are exactly those published `affine:
true`, and that nothing it finds kinked or unclassified is published
affine. Measured at proposal time: 73 corpus flags and 815 of the
operating Curta's, zero disagreements. It is the test that catches the
classification drifting from the producer's without anyone running the
producer.

## 4. The corpus audit

This is the heart of the proposal, and it is done twice: statically, by
classifying every followed quantity of every corpus document, and
dynamically, by replaying the whole corpus through the prototype and
diffing every recorded float.

**Statically.** Under the new classification the refreshed corpus's 17
machines have SEVEN reclassified driven ends and **no reclassified jump
level at all**:

| machine | driven end | published | plan | self-read |
| --- | --- | --- | --- | --- |
| `Captured` | `p1.lift` | false | none | no |
| `Captured` | `p2.lift` | false | none | no |
| `CarryLead` | `tens.turn` | false | yes | no |
| `KinkedStop` | `slide.travel` | false | none | no |
| `Remainder` | `pinion.turn` | false | yes | no |
| `Train` | `slide.travel` | false | none | no |
| `Window` | `pinion.turn` | false | yes | no |

A reclassified end is observable only through `locate`, because a
crossing's location depends on the jump LEVEL's shape (none is kinked) or
on a self-read walk's skeleton (none of the seven is a self-read). The
corpus records ten stops, and exactly ONE of them is on one of the seven:
`KinkedStop`'s, at `t = 0.478125`. So exactly one recorded float can
move, and it moves toward the producer's own answer. This reproduces
ADR-123's own audit — five reclassified machines, no stop on any of them
— on the viewer's side, with `KinkedStop` added.

**Dynamically.** The prototype replayed against the refreshed corpus,
every banked value, every crossing `t` and level, every stop `t` and
value and every command's admitted travel compared bit for bit with the
producer's:

| | base | prototype |
| --- | --- | --- |
| floats compared | 2 018 | 2 018 |
| not bit-identical to the producer's | **9** | **0** |

and the nine are `KinkedStop`'s stop fraction (9.09e-14 out), the `lever`
bank value of all four ticks (3.6e-12 out) and `h0`'s admitted travel of
all four. Nothing else in 360 ticks moves by one bit, in either
direction. The `run/` suite over the refreshed corpus: 340 tests, all
green on the prototype.

## 5. The operating Curta: nothing, and the number

`projects/Calculators/Curta-Type-I-3x`'s own published document, driven
through this engine in node (50 idle ticks, then its own `Turn crank`,
then 20):

| | base | prototype |
| --- | --- | --- |
| idle | 10.1-11.0 ms/tick, **20 718** evaluations/tick | 11.1 ms/tick, **20 718** |
| crank | 41.3 ms/tick, **260 306** evaluations/tick | 42.2 ms/tick, **260 306** |
| bank + crossings + stops after 70 ticks | — | **byte-identical** |

Of its 32 self-read skeletons 17 are kinked and 15 unclassified, and
ADR-060 measured that 100 % of its skeleton evaluations, level
evaluations and searches are under the 15. This change therefore does not
touch it, and the proposal says so rather than implying otherwise.

## 6. Red first

Five cases, each failing on this tree for a stated reason:

**A. The stop on a plan-less kinked determiner.** `KinkedStop`'s own
scenario, asserted as an IDENTITY and not within the corpus tolerance:
the stop fraction, the `lever` bank value and `h0`'s admitted travel must
equal the producer's `0.478125`, `119.125` and `19.125` EXACTLY. RED on
this tree at 9.09e-14 / 3.6e-12 / 3.6e-12. Plus the strong form, stated
as a number: an implementation that leaves `edgeCuts` returning `[]` for
a plan-less law divides once over the whole step and puts the stop at the
fraction that gives — write that fraction into the test's comment so the
trap is named.

**B. A kinked jump level's crossing.** A running root whose gate's level
reads a `clamp01` of a driver, crossed strictly inside a step with the
clamp inside its window there, and the exact fraction stated as a closed
form of the fixture's own arithmetic — never read back from the law. RED
by the search's tolerance; GREEN within a few ulp. The corpus has no such
level at all (measured), so this is a fixture written here.

**C. A kinked self-read skeleton.** The committed `clearing` fixture,
whose skeleton is kinked and whose levels are affine — so it is the
SKELETON's classification that sends it to the search today. The cost
assertion is the evidence: subexpression resolutions per tick, RED at
32 004 and GREEN under the number §8 states.

**D. A breakpoint is not a crossing, and nothing else moves.** The
crossing record of a machine whose path passes a breakpoint carries no
entry for it; `Clearing`, `Train` and the Curta carriage cost EXACTLY
471.1, 31.0 and 5 913.2 evaluations/tick before and after; the whole
corpus replays; and `src/running-corpus.json` is not touched by this
cycle at all.

**E. A curved quantity is still searched.** `max(0, sin(x))` and a
product of two movers classify as unclassified and cost exactly what they
cost today. One test, so a later per-branch cycle has a stated starting
point.

And one test that is neither red nor green but a CONTRACT: for every
document the suite loads — the 20 corpus documents and the committed
fixtures — the viewer's classification agrees with every published
`affine` flag (D6). It is the test that would catch the classification
drifting from the producer's without anyone running the producer.

## 7. Risks

- **A classification that is wider than the producer's.** Solving
  something the producer searches means the two runtimes disagree in the
  other direction, and the corpus would not catch it where no stop sits
  on the quantity. The flag-agreement test (D6) is the guard: a viewer
  shape of constant-or-affine where the document says false is a failure.
- **The `closed` convention at an interior breakpoint.** Getting it wrong
  loses or doubles a surface. Named tests in both (a) and (b).
- **The level cuts located outside their skeleton sub-piece.** A level
  rides `ownAt`, which is affine only inside one skeleton sub-piece;
  locating the level's breakpoints over the whole piece would read the
  driven coordinate along a path it does not take. Mirrored from
  `_level_cuts`, interpolating between the sub-piece's two ends.
- **A kink whose operand is curved.** `max(0, sin(x))` must stay
  searched. The classification is by OPERANDS, never by node type; case E
  pins it.
- **The walk's cuts growing for an ordinary tick.** The skeleton's kinks
  are added to the walk's cut list only when the caller asked for cuts (a
  stop being localized), mirroring `cutting=True`. An implementation that
  always computed them would pay for them on every self-read tick.
- **Shape stored on the wrong object.** A plan is shared by nothing, but
  a `RetainedReading` holds the SAME skeleton text as its plan: classify
  the full plan's skeleton with the full plan's jump names as constants,
  not the `outer` subset's.

## 8. Acceptance

Must hit:

| measure | base | after |
| --- | --- | --- |
| corpus floats not bit-identical to the producer's | 9 | **0** |
| `clearing` fixture, evaluations/tick | 32 004 | **≤ 4 000** (prototype 2 724) |
| `clearing` fixture, ticks/s | 297-308 | **≥ 900** (prototype 1 216-1 254) |
| `KinkedStop` stop fraction | 0.47812500000009095 | **0.478125 exactly** |

Must NOT move:

| measure | value |
| --- | --- |
| `Clearing` / `Train` / Curta carriage evaluations/tick | 471.1 / 31.0 / 5 913.2, exactly |
| the operating Curta, evaluations/tick idle and crank | 20 718 / 260 306, exactly |
| every other corpus float | bit-identical |
| `RangedBlock`'s searched stop, the lock advancing the key | within the repeats' spread |
| `src/running-corpus.json` | untouched by this cycle |
| `solidNodeViewerApi`, `solidNodeDocumentVersions`, `RENDERED_VERSIONS` | 16, `[1..7]`, 1-7 |

## 9. The prototype

`scratchpad/spikes-bc/`: `base/` (a copy of `src/` at `a35957d`),
`newcorpus/` (the same with the refreshed corpus dropped in — the
measurement of what cycle B alone does), `proto/` (the same patched at
the sites of D4), `probe/` (the prototype with the kink-level evaluations
counted), `audit-base.json` / `audit-proto.json` (every recorded float of
every scenario), `shapes.py` (the classification mirrored in Python for
the static audit), `kinked.py` (the guard's derivation, for cycle B), and
the census and Curta harnesses. The prototype is a SPIKE and not a patch
to copy: it caches the classification in a `WeakMap` where the real cycle
computes it at load, and it has no refusal path of its own.
