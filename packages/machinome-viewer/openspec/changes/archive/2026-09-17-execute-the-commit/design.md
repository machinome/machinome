## Context

The producer half of this campaign is solid-node branch `clocked-machine`
(HEAD `2d2dc2b`, eight commits ahead of main `81c5364`, unintegrated).
Four archived changes stand behind it:

- `declare-the-state` (ADR-125) — the `State`, the `.commits(at=, law=)`
  verb, the untimed clocked `Sim`, and the solver: `at` is ONE jump node
  whose level is SOLVED, only RISING steps fire, the landing is ADR-121's
  far side by ADR-121's own walk, ties are IDENTITY of the landing, reads
  are synchronous and PRE-EVENT, commits are in PATH order, two answers
  for one value at one landing refuse the REQUEST, and a refused request
  commits nothing — the final pose included.
- `a-bound-stops-the-request` (ADR-126) — one compiled constraint per
  (coordinate, SIDE), the chain composed down to declared drivers and
  states, the own-coordinate read at the request's start, the threshold
  `max(0, g(0))`, and the clip taken ONCE before the first event.
- `time-without-running` (ADR-127) — `Time.elapsed()`, the clock banked
  as `time`, `move('time')`, events on the clock, and nothing that stops
  one.
- `publish-the-clocked-machine` (ADR-128) — document **version 8**: the
  `states` table, the `clocked` object, the `%` desugaring in a published
  commit law, half-to-even integer commits, instructions carried with no
  meaning, and the EXACT corpus `tests/clocked-corpus.json`.

ADR-128 closes two defects of the shared locator that this cycle
inherits as contract: **closure 1**, a crossing belongs to the request
whose path contains its LANDING (not the fraction reading ADR-125 first
stated, which lost an event at a strict surface reached exactly at an
endpoint, and which a `sign` level standing at zero also lost); and
**closure 2**, the landing walk's first step is sized by the SEGMENT
rather than by the ulp of a value that happens to be `0.0`.

**On this side.** The viewer renders versions 1–7
(`src/viewer.ts:1941`) and refuses 8 by name (`src/viewer.ts:2052`). It
already owns, from ADR-045, ADR-047, ADR-054, ADR-057, ADR-058, ADR-060
and ADR-061, almost every primitive a clocked solve needs, as EXPORTED
functions of `src/run/jumps.ts`: `branchOf` (:75), `ordinalOf`/
`fromOrdinal` (:108, :114) over one `ArrayBuffer` viewed as a
`Float64Array` and a `BigInt64Array`, `ulpOf` (:121), `nextAfter` (:128),
`copySign` (:135), `along` (:188), `surfacesOf` (:200) with its inclusive
end, `deduplicated` (:243), `merged` (:264), `kinkBreaks` (:296),
`onSurface` (:694) and — the partition a JUMPED constraint level needs —
`planCuts` (:1377) over the same `{skeleton, jumps}` plan the program
loader already reads (`src/run/program.ts:940-975`). What it does NOT own
as a reusable piece is the far-side walk: it is a private method of
`Walk` (`src/run/jumps.ts:1217-1273`), which is exactly where the
framework's was before ADR-125 extracted it.

The originating project is the Curta. Its running model costs
40.52 / 42.31 / 43.70 ms per crank tick on ADR-060's bench, a figure
ADR-061 measured again and did not move; the clocked model exists to beat
that, and cannot be opened at all today. §14 is where that comparison is
made and labelled.

## Goals / Non-Goals

**Goals:**

- Read, validate and refuse a version 8 document by name, field by field.
- Execute a REQUEST on one input exactly as `Committing.next_event`,
  `Clocked._next_event` and `Clocked.move` do, bit for bit.
- CLIP that request at every declared stop before an event is located,
  and judge what its commits carried at the end, exactly as
  `Bounded.clip`, `Clocked._clipped` and `Clocked._judged` do (§8).
- Replay the clocked corpus EXACTLY over EVERY machine, with a census
  that makes visible the one thing this build does not do — advance a
  clock — and the steps that stand downstream of it.
- Pose the tree from the bank through the expression DAG the viewer
  already has, and animate `$t` over it.
- Give a maker a panel that operates the machine, and a real page that
  cranks the Curta-shaped published model and feels its interlocks.
- MEASURE what a request costs against the running Curta's own recorded
  number, and label exactly what the comparison is (§14).

**Non-Goals:**

- A time REQUEST and a clock that advances, the events on a clock and
  the elapsed base's playback — the next cycle's, §9. The next cycle
  also rebuilds the primary checkout's bundle.
- An instruction with runtime meaning: ADR-128 §14 publishes the table
  and gives it none, and `trigger` stays refused.
- Part controls under a clocked root: ADR-128 §14 keeps a `Control`
  refused in BOTH framework places, so a version 8 document never carries
  a `controls` key and there is nothing for an ADR-053 pick to bind to.
- The Curta project's own migration to the clocked discipline, the shop's
  hub and the studio floor.
- Any change to the framework, to the document's shape, or to the
  contract between the two packages.

## Decisions

### 1. Version 8 joins the rendered list, and the loader reads the `clocked` object

`RENDERED_VERSIONS` becomes `[1 … 8]` (`src/viewer.ts:1941`), and
`package.json`'s `solidNodeDocumentVersions` with it — the ONE
declaration `bundle.py` reads (`solid_node_viewer/bundle.py:59-79`) and
`version.test.ts` pins against. `RELEASED_DOCUMENT_VERSIONS` stays
`[1, 2, 3, 4]`: it is what a viewer predating the declaration is entitled
to be assumed to read.

`assertRenderable` gains one branch beside the program gate
(`src/viewer.ts:2079`). A document DECLARING version 8 must carry a
`clocked` object whether or not the key is there — the first thing §7
refuses — exactly as a version 5 document must carry a `program`. A
document carrying BOTH `program` and `clocked` is two machines and is
refused: the framework publishes one or the other, never both
(ADR-128 "Version 8 is a property of the ROOT'S DECLARATION, and it
dominates").

What is read, in ADR-128 §5–§9's own order:

| key | read as |
| --- | --- |
| `identity` | a string; the guard on a restored bank (§12) |
| `clock` | a string or `null`; the free name elapsed seconds bind to |
| `own` | a string; the free name every bound reads its own coordinate under, bound for the length of one request (§8) |
| `commits` | one entry per relation: `sources`, `targets`, `at: {primitive, level}`, `law` (one expression per target), `shapes`, `description`, `stated_by` |
| `bounds` | one entry per (coordinate, side): `coordinate`, `side`, `unit`, `value`, `bound`, `plan`, `shapes`, `node`, `joint`, `description` — the clip's own input (§8) |
| `limits` | `crossing_tolerance` and `max_crossings`, both required finite numbers |

Every expression slot is a STRING naming bank ids and `bindings` entries,
exactly as a published program's is, and reaches the same
`bindings.closure` / `nodeOf` interning the run already uses
(`src/run/program.ts:302-337`). `states` is validated as a second driver
table: the same five fields with the same meanings (ADR-128 §3), and its
ids are disjoint from `drivers`'.

**Rejected: treat version 8 as additive and render what can be read.**
ADR-128 rejects it on the producer's side for the reason that holds here
too — the pose expressions are the part a version 7 consumer cannot read.

### 2. The bank's order is DERIVED, because ADR-128 publishes no `coordinates` table

A running document publishes `program.coordinates`, whose `initial`
values come from the rest render — "the one number a consumer cannot
compute without running the CAD tree". A clocked bank holds no joint
coordinate: it is every declared driver and every declared state at its
declared `default`, plus, under an elapsed base, the clock at zero
(ADR-128 §4). Every one of those numbers is already in the document, so
inventing a table would publish something a consumer must be told to
ignore.

The viewer therefore fixes the bank's id order itself: the `drivers`
table's key order, then the `states` table's key order, then the clock
name when `clock` is not `null`. Both tables are published with SORTED
keys, so the order is deterministic for a given document and stable
across republication. It is the order a host reads on the handle and the
order a snapshot serializes in.

### 3. The executor runs SYNCHRONOUSLY on the main thread

The run executes in a worker (ADR-045) because it is a CADENCE: 60 to
240 integrations a second, forever, and the frame must stay responsive.
A clocked request is not a cadence. It is one gesture → one solve → one
pose, and the pose is main-thread work in any case (three.js). Putting
the solve in a worker would add a structured-clone round trip and a task
hop to EVERY gesture and make a drag asynchronous — a slider moved at
60 Hz would have to queue and coalesce replies to keep its order — for a
computation the whole clocked discipline exists to make cheap.

So `src/clocked/machine.ts` is a pure synchronous library — no DOM, no
three.js, no `postMessage` — for the reason `src/run/engine.ts:8-16`
already states of the engine: it is what lets the corpus replay IN-THREAD
under vitest, where a divergence is a stack trace rather than a message
that never came back. `viewer.ts` calls it directly and poses the reply.

**This decision is falsifiable and §14 measures it, in a real page.** If
a request on the corpus's widest machine — the Curta-shaped `Calculator`,
clip and all — costs more than one frame budget (16 ms), a page would
stutter on a gesture and the decision is wrong; the
cost test asserts a floor an order of magnitude below the bench number,
as `src/run/cost.test.ts` already does, and a regression is a NUMBER
rather than an impression. A worker remains available later without
moving a line of the solver, because the solver is a pure library:
`worker.ts` is a thin decoder around exactly such an object today.

### 4. A clocked machine is a SECOND executor, not a widened `Run`

`Run` integrates a tick: `dt`, commands with durations and rates, edges
in propagation order, spans, stops, a trajectory ring. A clocked machine
has none of those — ADR-125 refuses `run`, `at`, `every`, `time`,
`tick`, `rate`, `trigger`, `crossings`, `stops`, `commands` and
`program` BY NAME over a clocked root. Widening `Run` would carry every
one of those fields into a machine that must refuse them, and would put
the running corpus and the clocked corpus through one code path where
each is meant to pin a different algorithm.

`src/clocked/` is therefore its own small module — `document.ts`
(reading and refusing), `machine.ts` (bank, request, session),
`events.ts` (locating), `commit.ts` (writing), `bounds.ts` (the clip, the
stops and the end-of-request judgement) — and what it SHARES with the run
is the level of the primitives, not the level of the executor:
`jumps.ts`'s exported float, surface and partition helpers,
`expressions.ts`'s evaluator, `bindings.ts`'s table and `pose.ts`'s
scope. That is the same boundary the framework drew: `clocked.py` imports
`JumpPlan._solved`, `far_side_of`, `_branch_of`, `_on_surface`,
`_deduplicated` and `_plan_of` from `program.py` and shares nothing else,
and its own clip (`Bounded`) sits beside its own event solve
(`Committing`) in one file for the same reason these two sit in one
module.

The handle gains `machine(): MachineHandle | null`, beside
`run(): RunHandle | null`, which stays `null` for a version 8 document.
One question, one truthful answer.

### 5. `farSideOf` is extracted, with a `scale` that defaults to nothing

`Walk.farSide` (`src/run/jumps.ts:1217-1273`) is already the bit walk
ADR-128 asks for: bracket by doubling from one ulp, then bisect in float
ORDINAL space, membership decided by EVALUATING the branch and never by
comparing to the surface. It is private, and its first step is
`ownStar ? ulpOf(ownStar) : 5e-324` — the ulp of the landed value alone,
which is the ulp-of-zero defect ADR-128 closure 2 fixed on the clocked
side and DELIBERATELY left on the running side so no running landing
moves.

It is lifted to a free exported function, body unchanged, with one added
argument:

```ts
farSideOf(branchAt, near, ownStar, direction, unlanded, scale = 0): number
```

whose step is `ulpOf(Math.max(Math.abs(ownStar), Math.abs(scale)))` —
`math.ulp(max(abs(own_star), abs(scale)))`, the framework's own line
(`solid_node/simulation/program.py:1611`). `Walk.farSide` calls it with
no `scale` and keeps the value's own ulp exactly as before; the clocked
caller passes `max(|start|, |start + delta|)`, the segment the landing
sits on. This is the framework's extraction mirrored: one walk, not two,
and the running corpus must replay byte-identically afterwards, which
task 2.2 asserts before anything clocked is written.

### 6. The event solve mirrors `Committing.next_event` step for step

Per `commits` entry whose `shapes` names the moving input
(`clocked.py:138-141`, `moves_with`: an input ABSENT from `shapes`
cannot move this level and is not examined for it):

1. **Standing and steps.** Every source at its banked value, the moving
   input at the path's start, its step the remaining `delta` and every
   other step zero (`clocked.py:157-161`).
2. **Every crossing on the path, BOTH ends closed** (`_located`,
   `clocked.py:216-265`). A `shapes` entry of `affine` solves the whole
   path by one division (`surfacesOf` with `inclusive: true`, then the
   linear interpolation `_solved` makes); `kinked` cuts the path at the
   level's own `abs` / `min` / `max` breakpoints — re-derived from the
   published expression by the same rule ADR-061 already derives them by,
   `kinkBreaks` (`src/run/jumps.ts:296`) — solves each piece the same
   way, and folds the results with `deduplicated` under
   `limits.crossing_tolerance`. More than `limits.max_crossings`
   crossings refuses the request.
3. **The path's OWN opening surface is added** when the level starts ON
   one (`onSurface`, `src/run/jumps.ts:694`), because a solve excludes a
   piece's left end (`_on_surface` read off the opening level,
   `clocked.py:262-264`; the function itself is
   `solid_node/simulation/program.py:1010`).
4. **Per crossing, in path order**: the branch BEFORE it is read at the
   midpoint of the piece behind it (`clocked.py:194-196`), or — where the
   crossing is at fraction 0 — at the START, with the surface kept only
   when the branch at the next representable value the path reaches
   DIFFERS, read through `math.nextafter(start, copysign(inf, delta))`
   (closure 1; `clocked.py:179-193`, the `nextafter` at `:191-192`). The
   landing is `farSideOf(..., scale)`, `scale` being
   `max(|start|, |start + delta|)` (`clocked.py:176-177`, `:197-199`). A
   landing BEYOND the request's endpoint belongs to the next request and
   is skipped (`clocked.py:200-206`). The step FIRES only if the branch
   AT THE LANDING is greater than the branch before it — rising, read at
   the landing because a crossing at the request's own endpoint has no
   right-hand piece (`clocked.py:207-213`).
5. **The earliest crossing wins, and ties are IDENTITY** of the landing
   float — `landings.get(id(relation)) == landing`, never a tolerance
   (`Clocked._next_event`, `clocked.py:2160-2186`, the tie at
   `:2183-2185`).

Then, per event: every firing relation reads the bank as it stood BEFORE
the landing with the input AT the landing, all of them; a second answer
for one qualified id refuses the request naming the id, both relations as
written and the landing; the targets take their results TOGETHER; the
input takes the landing; and the solve resumes from there with the new
bank, so a surface that reads a committed state moves with it
(`clocked.py:2063-2091`).

**Rejected: re-deriving `shapes`.** ADR-128 §6 publishes the
classification precisely so a consumer does not: `_shape_of` is a hundred
lines of structural rules, and a consumer that classified a level
differently would cut a kinked path differently and land on a different
float. The viewer READS `shapes` and refuses a value that is neither
`affine` nor `kinked`.

### 7. The commit is one expression evaluation, and the rounding is stated

`law` is one published expression per target, aligned with `targets`
(ADR-128 §6). The viewer evaluates it over the PRE-EVENT bank with the
input at the landing, through the same interned DAG the pose uses.

- **A law returning a plain number publishes that number**, and it is a
  real answer — the asymmetry with a running law edge, whose `null` means
  "contributes no increment". `Scaled`'s law is the literal `4.0`.
- **`%` needs nothing new.** ADR-128 desugars a `%` in a published commit
  law to the floored remainder using the document's own vocabulary:
  `r + b * ((r != 0) * ((r < 0) != (b < 0)))` where `r` is `a % b`. The
  viewer's `%` is JavaScript's native operator
  (`src/expressions.ts:632`), which is TRUNCATED, which is what the
  desugaring assumes. The corpus's `Counter`, `Register`, `JumpsOnly` and
  `Calculator` carry the desugared form verbatim. The one detail to get
  right is that comparisons evaluate to BOOLEANS here and to `bool` in
  Python, and both coerce to 0/1 under `*` and `+` identically; a law
  whose TOP node is a comparison must still bank a number, so the
  commit's result is coerced once with `Number(...)` and a non-numeric
  result refuses.
- **An `int` target is rounded ONCE, half to EVEN**
  (`State.committed`, `solid_node/simulation/state.py:84-94`, is Python's
  `round`). `Math.round` takes a half toward +infinity and is WRONG here;
  the viewer implements `halfToEven` and uses it for every
  `dtype: "int"` target and nothing else. No `scale` is applied at a
  commit and none is published for one: the corpus's `Scaled` declares a
  state of `scale: 10.0` and banks the law's own `4.0`.
- **A REQUEST's `by`/`to` are DESIGN units and the bank is NATIVE.**
  `Driver.native` (`solid_node/simulation/driver.py:88-96`) divides by
  `scale` and, for a `dtype: "int"` driver, rounds ONCE — Python's
  `round` again, so `halfToEven` here too — and the admitted travel is
  reported back multiplied by `scale`
  (`Clocked.move`, `clocked.py:2111-2113`). The corpus pins both ends:
  `ScaledStroke`'s `move('lift', by=30.0)` on a `scale: 0.5` driver
  travels 60 native units, is clipped at native `9.0`, records
  `fraction: 0.15` and reports `admitted: 4.5`; `Calculator`'s
  `move('operand', to=4)` on an `int` driver standing at 1 reports
  `admitted: 3.0`.
- **A non-finite commit refuses the whole request.** The document cannot
  express a raise; ADR-128 §16 says a consumer that computes a
  non-finite commit value refuses rather than banking it.

### 8. A declared STOP CLIPS the request, before any event is located

ADR-126's whole rule, mirrored from `Bounded` (`clocked.py:1112-1307`),
`compile_bounds`' consumer side (`:1326-1413`) and `Clocked._clipped` /
`_judged` (`:2118-2158`), over exactly what ADR-128 §7 publishes.

**What a `bounds` entry carries**, read and refused field by field:
`coordinate`, `side` in `{low, high}`, `unit`, `value` (the CHAIN, one
expression over bank ids and `bindings` entries), `bound` (a NUMBER, or
an expression reading `clocked.own` and the bank), `plan` (the running
document's own `{skeleton, jumps}` shape, through the loader that
already reads one — `null` where the level carries no jump), `shapes`
(per input that can move the level: `{level, jumps: [...]}`), `node`,
`joint`, `description`.

**Three readings the commit side does not have, and each is pinned:**

- a bound's `shapes` admits `constant` as well as `affine` and `kinked`,
  where a commit's publishes only the latter two (`_published_bound`
  against `_published_commit`, `clocked.py:1911-1993`). `Calculator`'s
  freeze publishes `{"crank": {"level": "constant", "jumps": ["affine",
  "affine"]}, "setting": {"level": "affine", "jumps": ["constant",
  "constant"]}}`: the crank moves the level only through its jumps.
- an input is examined for a constraint exactly when `shapes` NAMES it —
  `Bounded.moves_with` is `input_id in self.plans`, and `plans`,
  `shapes` and `kinks` are filled together for every driver in the
  level's free names (`clocked.py:1169-1173`, `:1393-1412`). A
  constraint whose `shapes` does not name the moving input is constant
  along the path, is not examined during the clip, and is judged only at
  the END (below). `Decorative` and `Untouchable` publish a numeric
  `value` with `shapes: {}` and are exactly that.
- **the LEVEL is the consumer's own subtraction**: `value − bound` on
  the high side, `bound − value` on the low (`_constrained`,
  `clocked.py:1381-1384`; ADR-128 §7 "publishing it as well would
  publish the bound twice"). Where a `plan` is published its `skeleton`
  IS that same level with the jump nodes replaced by placeholders —
  `Pawl`'s is `((6.0 * _j0) - crank)` for the low side of
  `crank_dial.turn` — so the partition runs on the plan while every
  value of the level comes from the subtraction, which is what
  `Bounded.at`/`threshold` evaluate.

**What is read ONCE, at the request's start** (`_Level`,
`clocked.py:1309-1323`): the chain over the bank, bound to the
own-name for the whole request (`Bounded.standing`, `:1175-1181`); the
bound evaluated with it, each `reads=` coordinate already substituted by
its own chain so it moves ALONG the path; and the threshold
`h = max(0, g(0))` (`Bounded.threshold`, `:1183-1189`). ADR-126's
cross-request consequence comes with it, unchanged and not hidden: a
machine standing OUTSIDE a bound may move as long as it does not go
further out, and once a request has carried it back inside, the next
request reads `h = 0` and is clipped at the bound. `Standing` is the
corpus's own case — `move('feed', by=-1)` admits `0.0` and reports its
stop; `move('feed', by=5)` admits all five.

**The clip itself** (`Bounded.clip`, `:1209-1275`):

1. The path is PARTITIONED at the level's own jump surfaces through the
   published `plan` — `JumpPlan.cuts` on the producer, `planCuts`
   (`src/run/jumps.ts:1377`) here — and each piece's branches are read
   at its MIDPOINT. `planCuts` and the `partition` / `branchesAt` /
   `kinkLevel` beneath it take a `LoadedProgram` only for its interned
   expressions and its `limits.crossingTolerance`, so the clocked module
   presents THAT surface rather than copying a partition the running
   corpus already pins. Widening those signatures to a narrower type is
   part of task 6.2 and must leave the running corpus byte-identical,
   the same gate §5 puts on `farSideOf`.
2. On each piece, in order, the level's first exceeding of `h` is found
   by the skeleton's own classification (`Bounded._crossed`,
   `:1277-1307`): a piece whose LEFT end already exceeds `h` is one the
   level STEPPED across at the cut behind it, and the stop is the end of
   the last satisfied piece; a `kinked` skeleton is cut further at its
   own breakpoints inside the piece, with that piece's branches held;
   otherwise one division between the two ends.
3. A crossing at fraction `0.0` admits ZERO travel, said OFF THE
   CROSSING and never left to the walk (`:1246-1257`; ADR-128's closure:
   leaving it to the walk would let the low side admit half an ulp of
   the level only because the coordinate stands near zero).
4. Otherwise the landing is the SAME walk run backwards:
   `farSideOf(satisfied, 0, star, -direction, unlanded, scale)` with
   `satisfied(v) = Number(level(v) <= h)` and
   `scale = max(|start|, |start + delta|)` (`:1258-1266`). An event
   lands BEYOND its surface because the path has reached it; a stop
   lands SHORT of it because that is where the machine still is — one
   walk, two directions (ADR-126).
5. `fraction = (landing − start) / delta`; `<= 0` is zero travel with
   the stop, `>= 1` is no stop at all (`:1267-1275`).

**Across constraints** (`Clocked._clipped`, `:2118-2145`): the EARLIEST
fraction wins and its landing becomes the request's target BEFORE the
first event is located; every constraint whose landing is that same
value reports a `Stop` — `coordinate`, `side`, `bound` and `value` as
the chain gives them AT the landing, the input's value there, and the
fraction — and the message names `node`, `joint` and `description`. A
request stopped at zero travel is ADMITTED: it commits nothing, poses
nothing new and returns `admitted: 0.0` with its stops, which is what
makes an interlocked machine operable.

**The fraction's SIGN is part of the contract.** `Standing`'s recorded
stop carries `"fraction": -0.0`, which `Object.is` — and therefore
vitest's `toBe` — distinguishes from `0`. The viewer computes it as the
producer does, `(landing − origin) / requested`, and normalises nothing.

**The END-OF-REQUEST judgement** (`Clocked._judged`, `:2147-2158`;
`_commit_out_of_range`, `:1479-1504`). With the clip in front of the
events the only thing that can still carry a coordinate out of range is
a COMMIT — a state an event wrote, which the clip read at its
pre-request value. So after the last event and BEFORE the pose, every
constraint's level is evaluated over the FINAL bank through the same
chains, with the own-name still at the value the request started from,
against the same threshold; above it the WHOLE request is refused by
name, kind `JointRangeError`, and nothing is committed or posed. The
corpus pins it as `Shut`'s only step, refused with names `crank`,
`shutter.travel`, `travel`. It is also why a decorative range that rests
outside its own declared pair does not refuse anything: `Untouchable`'s
low level stands at `2.0` when the request begins, so `h = 2.0`, and the
level is still `2.0` at the end.

**The viewer needs no MARK.** The framework carries `clocked_marking`
because its POSE re-judges declared bounds by enumeration and would
re-decide, in a different order of the same arithmetic, what the clip
already decided (ADR-126, "ONE AUTHORITY"). This viewer's pose is
expression evaluation over the bank and judges no bound at all, so the
clocked executor is the sole authority by construction and there is
nothing to mark, open or close.

**A request on the CLOCK is never clipped.** Nothing stops a clock
(ADR-127), and `compile_bounds` refuses at construction any constraint
whose chain reaches one (`_over_the_bank`, `clocked.py:1416-1456`), so
no published `bounds` entry can name it. It is moot this cycle, because
a clock request is refused outright (§9); it is stated here so the cycle
that moves the clock inherits it.

**Why the clip is in THIS cycle.** Measured on the corpus file: **13 of
the 30 machines declare a `clocked.bounds` entry** — `Pawl`, `Stroke`,
`ScaledStroke`, `Lock`, `Kinked`, `Freeze`, `Gate`, `Shut`, `Lift`,
`Decorative`, `Untouchable`, `Standing` and `Calculator` — carrying 36 of
the 76 steps. Without the clip this cycle cannot replay the corpus's
only exact-HALF integer commit (`Calculator`'s `halved`), its only
scaled stroke (`ScaledStroke`), its only end-of-request refusal
(`Shut`), or the Curta-shaped machine the whole campaign exists to put
in a browser — and so cannot produce the one number it exists to produce
(§14). The reds stay separable INSIDE the cycle: the 17 unbounded
machines go green first on the event solve alone, and the 13 bounded
ones then fail on their first clipped step and go green with the clip
(tasks 5 and 6).

**Rejected: read the bounds, validate them, and REFUSE a bounded
document by name for one cycle.** It is this repository's established
posture for a shape it cannot execute
(`execute-bounds-reading-other-coordinates` refused the pin tumbler
lock's version 5 document for a whole cycle), and it was this proposal's
first shape. Rejected because the refusal would be lifted by the very
next cycle while costing this one its acceptance fixture, its speed
number and half its corpus — and because an ADR recording "version 8 is
read, except when it is not" is a half-state in this repository's
permanent record with no lasting reason behind it.

**Rejected: execute a bounded document UNCLIPPED.** Not a smaller
version of the clip but a wrong render: the events would be located on a
path the machine never travels. `Calculator`'s step 2,
`move('setting', by=1)`, admits `0.0` with a stop at fraction 0 where an
unclipped build admits `1.0` and slides the selector while the crank is
off rest.

**Rejected: clip the bounded COORDINATE and let the driver run on.**
ADR-108's clamp, refused there for the reason that holds here: the
group's other coordinates would stand where an unstopped request put
them.

**Rejected: re-compute the clip after each commit.** The finer reading,
and ADR-126's own rejected alternative: the clocked quantum is the
REQUEST. The consequence is behaviour with a corpus fixture of its own —
`Gate`'s `move('crank', by=1000)` is clipped against the CLOSED gate and
admits 300, where 200 then 800 commits the opening first and admits all
1000 — and it is why §13's split-request equivalence is claimed only
where no constraint binds.

### 9. The clock STANDS, and a request naming it is refused — but the document is not

Under `Time.elapsed()` the document carries `clock: "time"`, the clock is
in the bank at zero, and a request may move it (ADR-127). This cycle
banks the clock and poses from it, and refuses `move('time', …)` by name:

```text
move('time', …) asks this machine's clock to advance, which this build
does not yet do. The bank stands at 0 seconds and the model is posed
there; a later build moves the clock and fires the events on it.
```

**The DOCUMENT is not refused**, and the line is drawn at the gesture
rather than at the load because **a clock that stands renders
TRUTHFULLY**: the initial bank is a real instant of the machine, which
is exactly what ADR-128 §10 calls the preview a clocked model gets. An
elapsed document loads, poses, animates and takes every request on its
ordinary drivers — `Lift`'s `move('lift', …)` is clipped by its plate
bound like any other — and only the one gesture this build cannot honour
says so. Nothing else about an elapsed machine is special-cased: the
clock is a bank id like any other, read by the commit levels that name
it and posed through the same scope (§10).

The refusal is by REQUEST and is reported where the gesture was made, so
a panel on an elapsed document shows its clock as a standing readout
rather than a handle, and the corpus's three clock requests are asserted
against it (§15). Cycle 6 turns that refusal into a clip-free request —
nothing stops a clock (§8) — and fires the events on it.

### 10. `$t` sweeps while the bank stands, and the capture is corrected

A version 8 document publishes the ordinary `animation` object — `fps`
and `frames`, no `loop` (ADR-128 §10) — so the timeline is presented
exactly as it is for a version 1–4 document and a geometry that is a
formula of `$t` animates while the bank stands. The clocked pose scope is
therefore `poseScope`'s (`src/run/pose.ts:27-34`) with ONE difference:
`time` is the playback's `$t` rather than the fixed `0` a running
document poses at, because a running document publishes no animation
cycle and a clocked one does.

That same fact makes `capture.py` wrong today. `carries_program` reads
`version >= 5` as "carries a program" (`solid_node_viewer/capture.py:
59-74`, and `tests/test_capture.py:255-265` pins `carries_program({"version":
8}) is True`), and `assert_instant` (`capture.py:137-155`) uses it to
refuse a non-zero `--time` before any browser starts. A version 8
document HAS an animation cycle, so the question the capture asks splits
in two: "does this document carry a compiled program" (still
`version >= 5` or a `program` key — the rest-state posing) and "does this
document animate `$t`" (true for every version EXCEPT one carrying a
`program` object). A clocked staging is photographed at its INITIAL BANK,
and `--time 0.5` is honoured on it rather than refused.

### 11. Refusals carry a KIND and the NAMES, because that is what the corpus pins

The corpus records a refused step as `{"kind": …, "names": [...]}` and
nothing else: "the kind and the names are pinned and the prose is not"
(ADR-128 §16). The four kinds it uses are the framework's own exception
class names — `TooManyEvents`, `ClockedError`, `ValueError`,
`JointRangeError` — so the viewer's clocked errors carry an explicit
`kind` field mapping onto them, beside `RefusalKind`'s existing five
(`src/run/program.ts:84-94`):

| corpus kind | viewer error | raised when | pinned by |
| --- | --- | --- | --- |
| `TooManyEvents` | `TooManyEvents` | more than `limits.max_crossings` crossings on one path, from an event level or a constraint level (`_too_many_events`, `_too_many_stops`) | `Counter` step 6 |
| `ClockedError` | `ClockedConflict` | two relations write one id at one landing | `Conflict` step 0 |
| `JointRangeError` | `ClockedRangeError` | the END-OF-REQUEST judgement: a commit carried a compiled coordinate outside its bound (§8) | `Shut` step 0 |
| `ValueError` | `ClockedRequestError` | a request the machine has no meaning for — a clock asked to run backwards, an input it does not declare, `by` and `to` together or neither | `Regulator` step 2 (deferred with the clock, §15) |

The viewer's own clock-request refusal (§9) carries `ValueError` too:
it is the kind the producer gives every meaningless request, and the
corpus's one recorded `ValueError` names the clock exactly as this one
does.

The `names` a refusal must carry are what the generator extracts from
the producer's message — every bank id that appears in it, plus every
`'quoted.name'` (`tools/generate_clocked_corpus.py:389-398`, `:423-429`)
— so the replay asserts the kind and that the message CONTAINS each
qualified name the corpus lists, and never the prose. Every refusal
leaves the bank, the tree and the pose standing (ADR-125's atomicity):
the request is computed over a WORKING copy and assigned only after the
pose is accepted.

### 12. The session: snapshot, restore, reset, and the identity guard

`snapshot()` returns `{identity, bank}`; `restore(state)` refuses a
snapshot whose `identity` is not this document's, by name — ADR-128 §13:
the identity is a sha256 over the root class, each input and state with
its `dtype` and `scale`, each relation's ends, primitive and law text,
and each constraint's coordinate, side and level text, "so a bank taken
against one machine is refused against another, and a changed RANGE
changes the identity". `reset()` returns every id to its published
default. All three are session-local and nothing is persisted; the
corpus scripts all three (`{"snapshot": "a"}`, `{"restore": "a"}`,
`{"reset": true}`) and the replay drives them.

### 13. The chrome: a driver is a handle, a state is a readout

A THIRD chrome, `src/clockedControls.ts`, pure data exactly as
`src/runControls.ts` is — no DOM, no three.js, no machine — so every
decision is tested in plain node and `viewer.ts` renders exactly what it
returns.

- **A driver is a HANDLE.** Unlike a running coordinate — where
  `runControls.ts:16-25` refuses a slider because a coordinate carries
  history and writing a position is the re-entry the running mode exists
  to remove — a clocked driver IS positional: the bank holds where it
  stands and `move(id, {to})` is a straight path from there. So the
  control carries the banked value as an editable readout in DESIGN
  units, ± nudge buttons, and, where the driver declares a `range`, a
  slider across it. `range` remains presentation and never a clamp: a
  request past it is admitted exactly as the framework admits one.
- **A state is a READOUT**, follow-only, listed under the same focused
  layer and never a source of a request. The Curta's registers are what
  the maker looks at, and ADR-128 §3 makes the split the handle rule:
  every key of `drivers` is an input a person may move and no key of
  `states` ever is.
- **Every gesture is ONE request** `move(id, {to: value})`, and its
  outcome — the admitted travel in design units, the STOPS it met, or the
  refusal's own message — is reported where it was made, on
  `runControls.ts`'s `OutcomeReport` shape (`src/runControls.ts:71-80`),
  widened by the stop list §8 defines. **A gesture an interlock holds is
  reported, not swallowed**: `admitted: 0` with a stop naming the
  coordinate, the side and the bound is what a maker must see when the
  knob will not move, and it is the difference between an operable
  machine and a broken control.
- **A CLOCK is a readout, never a handle.** It is not a key of `drivers`,
  and this build refuses a request on it (§9).
- **A drag is a SERIES of requests, and that is correct.** Because the
  executor is synchronous (§3), a pointer move cannot interleave with
  another: request N+1 starts from the bank request N left. Closure 1 is
  exactly what makes this safe — a request resuming from its own landing
  fires nothing, and a surface reached exactly at an endpoint belongs to
  the request that begins on it — so no event is skipped and none fires
  twice.
  **The equivalence is claimed only where no constraint binds.** Task 7.4
  proves that splitting a recorded request into N consecutive
  sub-requests covering the same path leaves the SAME bank, over the 17
  corpus machines that declare no bound — including those whose laws read
  what an earlier event wrote (`Counter`, `Register`, `Clearer`), because
  the events fire at the same landings in the same order. It is NOT
  claimed where a bound binds, and ADR-126 says why: the clip is read
  once per request, so `Gate`'s one `move('crank', by=1000)` admits 300
  while 200 then 800 admits all 1000. The test asserts that difference on
  `Gate` rather than leaving it as prose, and names the machines each
  half covers.
- **Instructions are LISTED and DISABLED.** ADR-128 §14 publishes every
  declared instruction in the version 5 shape and gives the table no
  runtime meaning. Hiding them would make the panel disagree with the
  document a maker can read; showing them live would offer a gesture that
  cannot be honoured. They are listed, disabled, with the reason
  available to a reader and to assistive tools, and `machine().trigger()`
  refuses by name.
- **No transport for the bank**: there is no cadence to run, step or
  speed. The `$t` timeline is the document's own and is presented as it
  always was (§10).

### 14. What is measured, against what, and what the comparison is not

**The number this cycle exists to produce is the per-REQUEST cost of the
Curta-shaped `Calculator`, held against the running Curta's recorded
per-TICK cost.** ADR-060's own bench table is the thing it is held
against, quoted here so the comparison cannot drift:

| the operating Curta, ADR-060's `Measured` | before | after |
| --- | --- | --- |
| idle ms/tick | 18.27 / 18.66 / 20.94 | 9.52 / 9.57 / 9.86 |
| crank ms/tick | 156.91 / 161.30 / 163.42 | **40.52 / 42.31 / 43.70** |

Its method, which this cycle copies: this package's own worktree, node
v24.11.1, the engine bundled by esbuild and run IN-THREAD; the document
is the Curta's own re-exported `_build_running/viewer.json`; step
`1/240`; 100 idle ticks, then the document's own `Turn crank`
instruction, then 60 more; three runs. ADR-061 then measured the same
document again and moved it by nothing — 20 718 evaluations on an idle
tick and 268 968 on a crank tick, to the unit, digest `7f7bc77a…` — so
40.52/42.31/43.70 ms per crank tick is the standing figure.

`src/clocked/cost.test.ts`, on `src/run/cost.test.ts`'s pattern: every
number is PRINTED and the asserted floor is an order of magnitude below
the bench, so the test catches a tenfold regression and never a slow
machine. On `Calculator`, three requests that together are one operating
gesture each:

- **one stroke**: `move('crank', {by: 360})` from rest, which fires one
  stroke commit over four digits with the carry inside the law;
- **one clearing sweep**: `move('ring', {by: 500})` — the corpus's own
  step 6, four clearing relations reading the digits they write;
- **one CLIPPED selector move**: `move('setting', {by: 1})` with the
  crank off rest — the corpus's own step 2, one clip over three
  constraints, zero events, `admitted: 0.0`. This is the number that says
  what an interlock costs, and it exists only because §8 is in this
  cycle.

Beside them: `Counter` per EVENT (the corpus's `by: 3700` request, ten
events on one path, divided by the events) and the published POSE
separately, so a request and a render are never confused with each other.

**The same three requests are timed IN A REAL PAGE**, in the acceptance
test's Chromium (§16), with ADR-060's own care — same host, same
document, three runs, numbers printed — because an in-thread vitest
number is not what a maker's browser does, and the main-thread decision
(§3) is falsifiable only on the page: a request costing more than one
16 ms frame budget would stutter a drag.

**What the comparison is NOT, stated plainly:**

- It is FIXTURE-to-PROJECT. The Curta's OWN clocked model does not exist
  yet — the project's migration to the clocked discipline is pending and
  is not this cycle's (Non-Goals) — so the clocked side is
  `Calculator`: four wheels of one class, a stroke over four digits and
  an operand, a clearing relation per wheel, a ratchet and an off-rest
  freeze, which ADR-128 calls the corpus's Curta-shaped fixture and
  which is NOT the Curta's seventeen wheels.
- The UNITS differ. A running crank turn is a sequence of 1/240-second
  ticks at ~40 ms each; a clocked crank turn is ONE request. The per-turn
  ratio is therefore the per-tick figure multiplied by the ticks a turn
  takes, and this cycle quotes the per-tick figure rather than inventing
  a turn count for a document it did not time.
- Every number is recorded with its host, its node version and its run
  count in `evidence.md`, and the claim is the RATIO on one host, which
  is the host-independent part (ADR-060's own words).

`halfToEven` is pinned twice over: by the corpus, where `Calculator`'s
`halved` is the one law that lands an `int` state on an exact half, and
by a unit test whose expectations are computed BY HAND from the rule
(`0.5 → 0`, `1.5 → 2`, `2.5 → 2`, `-0.5 → -0`, `-1.5 → -2`, `-2.5 → -2`)
with `Math.round`'s answers quoted beside them.

### 15. Every machine is executed, and the one departure is a TEST

`src/clocked-corpus.json` is solid-node's `tests/clocked-corpus.json`
copied byte for byte (139 262 bytes, md5 `852b86b8…`, 30 machines,
76 steps, 722 recorded numbers), from branch `clocked-machine` HEAD
`2d2dc2b`, recorded in the test's own header as the running corpus's is.

**All 30 machines LOAD and EXECUTE.** The replay walks each machine's
script step by step with `toBe` — `tolerance.float` is read from the file
and asserted `0.0` — comparing the WHOLE bank, the admitted travel, the
commits (relations, fraction, value, targets), the STOPS (coordinate,
side, bound, value, input, fraction) and the refusals by kind and by
names, and it derives everything it does from the file rather than from a
list. The counts, measured on the file:

| | machines | steps | recorded numbers |
| --- | --- | --- | --- |
| replayed EXACTLY | 30 load; 27 replay whole | **68** | **652** |
| the clock requests this build refuses | 3 | **3** | 48 |
| deferred because they stand downstream of one | — | **5** | 22 |
| total | 30 | 76 | 722 |

**The one departure, exactly.** Three steps move the CLOCK: `Regulator`
step 0 (`by: 5.0`), `ClockAlone` step 0 (`by: 3.0`) and `Lift` step 0
(`by: 4.0`) — every one of them the machine's FIRST step. The corpus
records them ADMITTED; this build refuses them (§9), so the replay
asserts a refusal where the corpus records a request, which is a
departure and is written in the test as one, by kind and by name. After
it the bank has diverged from the corpus's, so the five steps standing
downstream cannot be compared either: `Regulator` 1–4 (a snapshot, the
recorded backwards-clock `ValueError`, a zero-travel clock move and a
restore) and `Lift` 1 (a clipped `move('lift', by=12)` this build would
execute correctly against a bank it cannot reach). They are asserted
SKIPPED-BY-NAME with the reason, never silently dropped.

**Three of the corpus's four recorded refusals are reproduced**:
`Counter` step 6 (`TooManyEvents`), `Conflict` step 0 (`ClockedError`)
and `Shut` step 0 (`JointRangeError`, the end-of-request judgement §8
brings into scope). The fourth, `Regulator` step 2's `ValueError`, is one
of the five deferred steps.

**A CENSUS test pins `30 = 30` and `76 = 68 + 3 + 5`**, deriving the
three clock steps from the file (a `move` whose input is the machine's
own `clocked.clock`) rather than naming them, so a corpus regenerated
wider or narrower is loud here without anyone running the generator —
what `running-corpus.test.ts`'s width check already does for the running
file, aimed at what this cycle actually claims.

**A DISAGREEMENT IS A BUG IN THIS ENGINE.** Not a tolerance to widen, not
a scenario to skip, not a fixture to edit. Where an operation cannot
agree bit for bit, the implementation STOPS and reports rather than
widening anything.

### 16. The acceptance: a version 8 model with geometry, in a real page

`tests/fixtures/calculator/` — the framework's own
`tests/clocked_project/calculator.py:Calculator`, the Curta-shaped
fixture: four `Wheel`s of one class each carrying a `Dial` solid, a
`Dial` crank and a `Slide` knob (`tests/clocked_project/parts.py`), a
selector wired through a `TranslationalPort`, an anti-reversal ratchet on
the crank dial and an off-rest FREEZE on the knob. Exported VERBATIM
with

```
PYTHONPATH="$PWD" solid export \
    tests/clocked_project/calculator.py:Calculator -o <dir> --no-widget
```

from a throwaway copy of solid-node at branch `clocked-machine` HEAD
`2d2dc2b`, with the written `manifest.json` committed under the name
`viewer.json` and its md5 recorded — the `clearing` fixture's own
provenance rule (`tests/fixtures/clearing/README.md`). Nothing about the
document is edited. `solid export` WARNS for a version this viewer's
installed bundle does not read and writes anyway (ADR-128 §15), which is
why the fixture can exist at all.

It is the acceptance fixture BECAUSE it carries the interlocks: a page
that only turns dials would prove the event solve and nothing of §8.
Mounted in Chromium beside `tests/test_clearing_document.py`, the
acceptance replays the corpus's own `Calculator` steps against the
screen, with the expectations the corpus already records:

- the page opens at the initial bank, every digit at 0;
- `operand` to 4 admits 3.0, and a crank request of 1100° fires three
  strokes — the dials read 2, 1, 0, 0 with the carry visible;
- `setting` by 1, with the crank off rest, admits **0.0**: the knob does
  not move on screen and the control reports the freeze's stop by
  coordinate and side;
- a crank request of −30° admits **−2.0** and stops on the last seated
  tooth of the ratchet;
- `ring` by 500° clears the four dials back to 0;
- a refused request — one naming an input this machine does not
  declare — leaves every dial where it was. The MID-request refusals are
  not reachable on this machine (no commit of it feeds a bounded
  coordinate's chain, and no two relations write one id at one landing),
  and the corpus pins each of them on the machine built for it:
  `Conflict`, `Counter` and `Shut` (§15).

Two screenshots are written to `tests/_shots/` as evidence: the machine
after its strokes, and the knob held by the freeze.

### 17. What is asserted UNCHANGED

- The running corpus replays byte-identically after the `farSideOf`
  extraction (§5) — asserted BEFORE any clocked code is written.
- Every version 1–7 document loads, poses, animates, drives and runs
  exactly as it does today: the clocked branch is entered only when
  `clocked` is present, and `run()` is untouched.
- `RELEASED_DOCUMENT_VERSIONS` does not move.
- Nothing of the framework, no other repository, and no document shape.

## Risks / Trade-offs

- **A bit-for-bit disagreement this design has not anticipated** →
  §15's rule: stop and report at the operation, never widen. The
  candidates are known and each has a named mitigation: the ordinal walk
  (already proved by ADR-057's own corpus), `%` (§7), boolean coercion
  (§7), the negative-zero cases `branchOf` already normalises
  (`src/run/jumps.ts:61-63`), and the kink breakpoints ADR-061 already
  agrees with the producer on for 73 + 815 published flags.
- **The cycle is wide**: the event solve and the clip are two solvers,
  and the chrome is a third piece → the reds are separable and ordered
  (tasks 5, 6, 7), each half has its own corpus evidence, and the one
  thing that is NOT separable — a bounded document executed unclipped —
  is exactly what §8 refuses to ship.
- **The clip's own hazards are named, each with its fixture**: the
  threshold read once per request (`Standing`, `Gate`), the negative-zero
  fraction (`Standing`), a level that STEPS across its zero rather than
  crossing it (`Pawl`, `Lock`, `Freeze`, `Calculator`), a kinked
  constraint level (`Kinked`), a constant chain outside its own declared
  pair (`Untouchable`), the design-unit scale on a clipped travel
  (`ScaledStroke`) and the end-of-request judgement (`Shut`).
- **Three corpus steps are asserted as a DEPARTURE from the producer**
  rather than as agreement, and five more are skipped → §15 counts them
  exactly, the census derives them from the file, and the next cycle
  turns all eight into ordinary replayed steps.
- **The main-thread decision** → §3 is falsifiable and §14 measures it; a
  worker is a decoder away because the solver is a pure library.
- **The panel's slider is a new affordance under a machine with memory**
  → it is positional by construction (§13) and every gesture is a
  REQUEST that reports its outcome; nothing binds back, which is
  ADR-048's rule kept.

## Migration Plan

Additive. A document below version 8 takes exactly the code it takes
today; the API version rises so a host can ask before mounting; the
bundle rebuilds itself from its sources (ADR-059) so an installed
checkout answers with the new list without a manual build. Rollback is
the revert of one cycle: no document, no fixture and no framework
artifact changes shape.

## Decided at review

1. **The campaign's split moved, and the CLIP is this cycle's.** The
   first draft of this design kept the campaign's original order — clip
   and clock both in the next cycle — and refused a bounded version 8
   document by name. Measured on the corpus, that cost half the file, the
   acceptance fixture and the one number the cycle exists to produce
   (§8's "Why the clip is in THIS cycle"). The clip is now in scope; the
   CLOCK alone is the next cycle, with the primary bundle rebuild.
2. **Engine and chrome are ONE cycle.** Splitting them the way ADR-045
   and ADR-048 split the run was considered and rejected: `machine()`
   without a panel is a capability no maker can reach, and the API
   version would have to rise twice for one document version.

## Open Questions

1. **What an instruction MEANS under a clocked root.** ADR-128 §14 leaves
   it open and records it as a framework wart; this cycle shows the table
   disabled. If the answer is "an instruction is a request on its
   targets", it is a later cycle in both repositories.
