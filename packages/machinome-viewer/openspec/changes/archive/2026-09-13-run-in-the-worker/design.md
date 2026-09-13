# Design — run in the worker

## Context

### What exists here

- **The document loader** (`viewer.ts`). `RENDERED_VERSIONS = [1, 2, 3, 4]`;
  `assertRenderable(document, sourceUrl)` refuses an unreadable version by
  name, builds and validates the `bindings` table, refuses a flexible
  technology or spec it cannot evaluate, and refuses any expression naming
  a free name that is neither `$t`, a binding, nor a declared driver id.
- **The evaluator** (`expressions.ts`, `evaluator.ts`, `bindings.ts`). A
  page-scoped, hash-consed DAG: `prepare(text)` interns an expression once
  and returns a `NodeId`; `valueOf(id, scope)` walks it memoized by a pass
  stamp; `freeNames(id)` is memoized per node. `EvalScope` is
  `{time, drivers?, bindings?}`; a name resolves as `$t`, then a binding,
  then the driver map, then the OpenSCAD context. A dotted id is member
  access: the parser gives `['units', 'drum', 'turn']` and the scope must
  be nested.
- **The driver store** (`drivers.ts`). Native values, `toNative` with
  round-half-to-even, wall-clock ramps and `trigger`. `range` never clamps.
- **The chrome as pure data** (`controls.ts`) and its DOM in `viewer.ts`;
  the playback clock (`playback.ts`); the tree (`tree.ts`), whose
  `update(scope, changed)` re-evaluates exactly the nodes whose free
  variables `changed` touches.
- **The build** (`build.mjs`): one esbuild pass, `iife`, one published
  file, `dist/solid-widget.js`, whose name is a compatibility contract.
- **The tests**: vitest in plain node for everything that decides, a
  producer-generated parity fixture for the evaluator, and a Python
  Playwright suite (`tests/test_widget_e2e.py`) for what only a real page
  can show.

### What the framework published

`solid-node`'s archived `2026-09-13-publish-the-mechanical-program`
(ADR-110, ADR-111) and its `openspec/specs/export/spec.md`. Version 5 is
version 4 plus `program`, and is taken here **verbatim** — §1 of that
design is the schema, and this document does not restate it field by field
except where the engine's own rule depends on it. Beside it:
`2026-09-13-run-owns-the-coordinates` (the program, the tick, commands,
the snapshot), `2026-09-13-integrate-jumps` (the branch-per-segment
partition) and `2026-09-13-ranges-are-stops` (localization, the group,
segments, `blocked`), with `solid_node/simulation/program.py` and
`run.py` as the reference implementation this engine is measured against.

### The authority for the interface

`workflow/open-run-simulation/design.md`, "Decision 2026-09-13" item 10
(the browser worker integrates with the same rule over the expression
evaluator the widget already has; Python and browser share a conformance
corpus), "Python-to-browser architecture" (a new capability/version
boundary an old viewer must refuse; the renderer may drop display frames
but not mechanical events; it draws absolute poses from committed
coordinates) and "Browser interface".

### The acceptance document

`projects/Calculators/Pascaline-module/WTs/open-run-simulation/_build/viewer.json`:
version 5, 32,994 bytes, 50 bindings, three inputs (`units_entry`, `tens_entry`,
`hundreds_entry`, all `unit: digit`, no scale, no dtype, no range), nine
joint coordinates, six intermediates, nine edges of which three carry a
`floor` plan, no spans, three `by=` instructions. Read, not built, by this
repository.

## 1. Where the run runs, and who drives the clock

### D1. The engine is a library; the worker is a transport

`src/run/` is a pure TypeScript library with no DOM, no three.js and no
`postMessage` in it: it takes the program-bearing keys of a document and a
`dt`, and answers ticks. `worker.ts` is a thin decoder around it, and
`runtime.ts` is the main thread's side. That split is what lets the
conformance corpus replay the engine **in-thread** under vitest, where a
divergence is a stack trace rather than a message that never came back —
and it is the same split `controls.ts` already has against `viewer.ts`.

*Alternative that lost:* the engine written directly as the worker's
message loop. It would make the corpus suite spawn thirteen workers and
would put the algorithm behind a transport in every test that touches it.

### D2. The main thread drives the cadence; the worker owns the mechanics

Per animation frame the main thread computes how many ticks the elapsed
wall time has earned, sends **one** `advance` message, and renders the
bank of the reply. It sends the next `advance` only after the reply
arrives: **one advance in flight, always**.

This single rule settles three questions at once.

- **Backlog.** A page whose tab is hidden gets no animation frame, sends no
  `advance`, and the run stops where it stands. Nothing accumulates, and
  the elapsed-simulation-time readout tells the truth about it. A paused
  page is a paused machine, which is what the pilot's "a blocked drag
  accumulates no hidden movement" asks for one layer up.
- **A slow tick.** If the worker takes longer than a frame, frames are
  dropped for *display*, never for mechanics: no tick is skipped, the next
  advance simply asks for the ticks the stall earned, and the run runs
  slower than wall time. The wall-time debt is capped (D9), so a long
  stall cannot produce an unbounded burst.
- **Ordering.** Commands are queued in the worker and applied before the
  next tick it integrates, which is exactly the corpus's own rule: a
  script entry is applied before the tick it names.

*Alternative that lost:* the worker owns a timer and pushes frames. In a
hidden tab a browser throttles that timer to about 1 Hz, and the worker
would then be handed a one-second catch-up — an invisible backlog integrated
while nobody is looking, with a thousand ticks of mechanism happening
between two paints. Rejected on the pilot's own rule.

*Alternative that lost:* no worker at all — the tick on the main thread
beside the render. Rejected: a jumping law with a non-affine level quantity
searches 64 sample points and bisects up to 64 rounds per crossing per
tick, and that is exactly the work that must not compete with the frame.

### D3. The worker is bundled into the one published file

`build.mjs` gains a first pass that bundles `src/run/worker.ts` to a
string (`write: false`), and the main pass injects it as
`__WORKER_SOURCE__`. `runtime.ts` creates the worker from a blob URL of
that string. There is still exactly one published artifact,
`dist/solid-widget.js`; `solid export`, the dev server's `/_viewer/bundle.js`
and the capture page copy one file, as they always have.

A page whose Content-Security-Policy forbids a blob worker throws at
`new Worker(...)`. The runtime catches it **once**, runs the same engine
in-thread, and reports `runsInWorker: false` on the running handle. The
mechanics are identical — same module, same numbers — and the only
difference is which thread pays. Silently degrading would be wrong; failing
to open the machine would be worse.

*Alternative that lost:* publish `solid-widget.worker.js` beside the
bundle. It breaks four copy sites and the export contract for one file, to
avoid one blob URL.

## 2. The message protocol

One request type carries the cadence; everything else is a request with a
correlated reply. Types live in `protocol.ts` and are shared by both sides,
so the compiler checks the wire.

```
main -> worker
  {t:'load',     document, dt, record}              // program-bearing keys only
  {t:'advance',  id, ticks}                         // one in flight
  {t:'command',  id, op:'move'|'rate'|'trigger'|'cancel', ...args}
  {t:'control',  id, op:'reset'|'snapshot'|'restore', state?}
  {t:'dispose'}
worker -> main
  {t:'ready',    identity, order:string[], kinds, units, domains, bank:Float64Array}
  {t:'frame',    id, tick, clock, bank:Float64Array, moved:number[],
                 crossings, stops, commands}        // reply to one advance
  {t:'outcome',  id, handle, status, admitted, message?}
  {t:'refusal',  id, tick, kind, message}           // the tick committed nothing
  {t:'error',    id, message}                       // a request refused, nothing changed
```

- `order` is the bank's id order, fixed at load; every `bank` afterwards is
  a positional `Float64Array` in that order and `moved` is indices into it.
  A twelve-coordinate machine costs 96 bytes a frame and a three-hundred
  one costs 2.4 kB; a string-keyed object would cost a structured clone of
  three hundred keys sixty times a second for no gain.
- A `frame` reports the crossings and stops located in the ticks it
  integrated, and the status and admitted travel of every command that is
  still active or retired in them — the same three things the corpus
  compares, so the chrome and the conformance suite read one shape.
- `refusal` carries the framework's own message text: a conflict names both
  relations, a partition over a thousand cuts names the law, a divisor of
  zero names the primitive. The run pauses at a refusal rather than
  retrying the same admissions sixty times a second.
- `error` answers a request the run declines — a second command on an owned
  input, a duration that is not a whole number of ticks, an unknown
  instruction, a snapshot from another program — leaving the run untouched.

## 3. The engine, module by module

Every module below names the Python it reproduces. The rule is *the same
arithmetic in the same order*, not *an equivalent result*: where Python
accumulates `total = total + held[key] * factor` in `needs` order, so does
this, because the corpus pins floats to `1e-9` relative and a re-associated
sum is how a runtime drifts into that window and then out of it.

| `src/run/…` | reproduces | what it holds |
| --- | --- | --- |
| `scope.ts` | — | the nested evaluation scope builder (D10) and the id-prefix refusal |
| `program.ts` | `program.py` `Program`, `_published_*` read backwards | the loaded, validated program: coordinates in order, `kinds`, `units`, `domains`, `initial`, intermediates, edges, spans, sources, limits, clock, identity, and the `determiner` map derived from `gives` |
| `edges.ts` | `program.py` `class Edge` | `values`, `increments`, `cuts`, `linear`, `predicts`, the `affine` flags read from the document rather than recomputed |
| `jumps.ts` | `program.py` `JumpPlan`, `_branch_of`, `_surfaces`, `_deduplicated`, `_merged`, `_along`, `_too_many`, `_no_level` | `increment`, `cuts`, `partition`, `branches`, `level`, `crossingsOf`, `searched`, `bisect` |
| `commands.ts` | `run.py` `class Command` + `driver.py` `RampProgram` | `admits`, `cumulative`, `finished`, `record`, `requested`/`admitted`/`remaining`/`rate` in design units, `cancel` |
| `run.ts` | `run.py` `class Run` | `integrate` (the segment loop), `pass`, `scaled`, `deltas`, `reached`, `event`, `locate`, `piecewise`, `searched`, `along`, `group`, `pushes`, `block`, `values`, `bounds`, `refuse`, `conflict`/`disagreement` messages, `snapshot`, `restore`, `reset`, the three rings |
| `engine.ts` | `sim.py`'s running branch | the façade: `move`, `rate`, `trigger`, `cancel`, `advance(n)`, `snapshot`, `restore`, `reset`, `state()`, `tick`, `clock`, and `ticksFor(seconds)` reproducing `Sim._ticks` |

What the engine does **not** hold, because the framework publishes it and
publishing it was a decision: the edge order (Kahn's tie-break), each law's
`affine` flag, each plan's postorder, level quantity and `%` rewrite, the
`sources` table, and the five `limits`. The engine reads all six and
computes none of them. It derives exactly what §5 of the framework's design
says is derived: the `determiner` inversion of `gives`, the bank-key set,
every value after the initial one, the per-tick increments, the partition,
the localization, the group, the statuses.

### D4. The tick, in one paragraph, because it is one loop

`integrate(tick, advance)` reproduces `Run.integrate` including its
staging: admissions from the active commands; a `while` over segments, each
scaling the admissions by the remaining stretch, propagating one pass over
the edges in program order, and testing every ranged coordinate for having
ended the stretch outside a bound *and further outside than it began it*;
on a stop, the earliest `t*` and everything within `crossing_tolerance` of
it become one event, the segment is re-integrated over `[0, t*]`, each
stopped coordinate is committed **at** its bound, the group of inputs that
push it is stopped for the rest of the tick, and the loop goes round. The
bank, the admitted travel and the three record lists are staged and applied
only when every segment has succeeded; a conflict, a `TooManyCrossings`, an
unintegrable law or a broken stop invariant in any segment commits nothing
and retires the commands that moved as `refused`. Then, and only then:
the bank is taken, the tick count advances, admissions are added, stopped
inputs' commands retire `blocked`, finished commands retire `completed`,
and the rings are appended.

### D5. What a segment boundary means for a crossing's `t`

`_record`'s mapping is reproduced exactly: a segment's partition is in the
fraction of the *segment*, and a `Crossing`'s `t` is the fraction of the
*tick*, so an entry located at `u` inside a segment `[first, last]` is
recorded at `first + u * (last − first)`. Without it the same crossing
would be reported at a different fraction depending on whether a stop
happened to cut the tick after it — and `StopAndJump` in the corpus is
precisely that case, at `t = 0.1666…` for the fold and `0.5` for the stop.

### D11. Every evaluation gets a fresh scope object

`expressions.ts` memoizes by a pass stamp and takes an identity fast path:
`if (scope === lastScope) return` — a scope object it has already seen is
assumed to hold the same values. An engine that reused one object and
mutated it between evaluations would therefore read the *previous*
evaluation's memoized numbers, silently and everywhere. The rule is
absolute and stated here because it is invisible at the call site: **build
a new scope object for every point on the path** — the start, the end, each
midpoint, each bisection probe — and never write into one that has been
passed to `valueOf`. A test asserts it directly: two evaluations of one
expression at two source values through a mutated object disagree with the
same two through fresh ones.

*Why not disable the fast path:* it is what makes one `tree.update` walk
cost one pass rather than one per operation, on every document version.

### D12. The program's held node ids are generation-guarded

`prepare` hands out `NodeId`s from a page-scoped store that `resetStore()`
empties when the node ceiling is reached, handing ids out again from zero.
`bindings.ts` already guards its held map with `expressionGeneration()`;
the loaded program holds one id per published expression and needs exactly
the same guard, re-preparing from the expression strings it keeps when the
generation has moved. Without it a long `solid develop` session that
republished past the ceiling would integrate a machine out of another
document's nodes.

## 4. Loading the program: read, derive, refuse

`loadProgram(document, sourceUrl)` runs inside `assertRenderable`, after
the bindings table is built and before the tree's expressions are walked,
and returns the compiled program or throws. Every refusal names the thing
and quotes the source, in the voice the loader already uses.

**Read** (verbatim, no interpretation): `identity`, `clock`,
`coordinates` (order, `kind`, `initial`, `unit`, `domain`),
`intermediates`, `edges` in order with their `needs`, `gives`,
`description`, `stated_by` and their kind-specific fields, `spans`,
`sources`, `limits`.

**Derived**: `determiner` (one inversion of `gives`), the bank-key set, the
set of ids a name may resolve to, and one `NodeId` per published expression
through `prepare` — the same interning the tree's own expressions get, so a
subexpression a law shares with its plan's level quantity and with a pose
is one node on the page.

**Refused by name.** The list is the whole of what a consumer can check
without running the machine:

1. `version: 5` with no `program`, a `program` that is not an object, or a
   missing required key — naming the key.
2. a `coordinates` entry whose `kind` is neither `input` nor `coordinate`,
   or whose `initial` is not a finite number.
3. the `kind: "input"` ids and the `drivers` table's keys disagreeing in
   either direction — naming the difference. The framework asserts this
   identity; a consumer that holds both tables must check it, because
   which one is authoritative is otherwise unknowable.
4. an id set that cannot be nested: `a.b` present beside `a.b.c`, naming
   both (D10).
5. `clock` colliding with a coordinate or a driver id.
6. an `edges` entry whose `kind` is not `law`, `wiring`, `formula` or
   `check`; a law whose `expressions`, `affine` or `plans` is not aligned
   with `gives`; a check with a non-empty `gives`; a formula or check
   without `slot`, `factors` aligned with `needs`, or `constant`.
7. a `needs` or `gives` id that is neither a bank coordinate nor an
   intermediate.
8. a jump whose `primitive` is outside `floor`, `ceil`, `sign`, `%`, `<`,
   `<=`, `>`, `>=`, `==`, `!=` — naming it and the ten. **This is the
   forward-compatibility seam of the engine**: a framework that grows a
   sixth jump kind inside version 5 would otherwise be integrated with a
   branch rule this engine invented.
9. two jump entries anywhere in the document sharing a placeholder name.
   The framework mints them document-wide for exactly this reason; sharing
   one would silently give two different jump nodes one published subtree.
10. an expression (a law's, a skeleton, a level quantity, a bound) whose
    free names, closed over the bindings table and minus that plan's own
    placeholders, are not all in the edge's `needs` (a bound's: not the
    coordinate's own id). A law need not read every source, so the test is
    containment, not equality.
11. a `spans` key that is not a bank coordinate; a bound that is neither
    `null`, a finite number, nor `{expression}`.
12. a `limits` value that is missing or not a finite number — naming it.
13. a `sources` key or member that is not a known id.
14. **an intermediate that something reads and no edge gives.** See §11,
    finding 1: the Pascaline publishes six intermediates no edge
    determines. They are harmless while nothing reads them and fatal the
    moment something does, so the refusal is scoped to being *read*.

The existing declared-name refusal is widened, not replaced: after the
bindings closure, a free name anywhere in the document must be the clock
name, a key of `drivers`, a key of `program.coordinates`, a
`program.intermediates` entry, or — inside a plan's own expressions — one
of that plan's placeholders.

## 5. Posing from a committed bank

Per rendered frame:

```
scope = { time: 0,
          drivers: nest({ ...bank, [program.clock]: elapsedSeconds }),
          bindings: bindingsTable.roots() }
tree.update(scope, { time: false, drivers: movedIds })
```

Three things are worth saying about that.

- **Nothing new is evaluated.** The framework's "a committed bank poses the
  geometry" makes a joint's placement its coordinate's id and a flexible
  leaf's `params` an expression over bank ids, so the widget evaluates in a
  version 5 document exactly what it evaluates in a version 4 one, from a
  wider scope. `flexible.ts` needs no change at all.
- **The bounding rule is untouched.** `Changed.drivers` already means "the
  qualified ids whose values moved this frame", and a coordinate id is a
  qualified id. `movedIds` is the `moved` indices of the frame message
  mapped through `order`. A machine whose carry is idle re-evaluates only
  the nodes the moving drum reaches.
- **`time` is a bank-shaped name, not `$t`.** `program.clock` is `time`;
  under a run it binds to elapsed simulation seconds, which never wrap;
  with no run — a still capture, a thumbnail — it binds to zero, the
  instant the rest pose is defined at. `scope.time` (`$t`) stays 0 for a
  version 5 document, because no expression in one reads it.

### D10. A qualified id is nested at every segment

`nest(flat)` builds `{units: {drum: {turn: v}}}` from `units.drum.turn`,
for as many segments as the id has, and is used by the engine's scopes and
by `DriverStore.scope()` alike. Today's builder splits at the first dot
only; measured against the shipped modules, `evalExpr('(-1 *
units.drum.turn)', {time: 0, drivers: store.scope()})` is `NaN`. Every
coordinate id is three segments or more, so the run cannot pose without
this; and the same bug already silently breaks a three-segment *driver* id
in a version 2 to 4 document, which is why the fix goes in the shared
builder and carries its own red test. It changes no correct pose: it
changes a `NaN` into the number the producer meant.

Two ids that cannot both be nested — `a.b` a value beside `a.b.c` a value —
are refused at load naming both, because the nesting would have to make one
number an object. Nothing the framework publishes produces that shape
today; the refusal is what keeps it loud if it ever does.

*Alternative that lost:* look the whole dotted name up in a flat map inside
`resolveName`, before the member chain. It fixes the same bug more simply
and would let the scope be flat — but it changes a name-resolution rule
that is ratified for every document version and pinned by the parity
fixture, and it changes `scopesEqual` for every document on the page, to
avoid a refusal for a shape nothing emits.

## 6. `dt`, speed, and the background tab

### D6. `dt` defaults to 1/240 s and is fixed for the life of a mount

The framework deliberately publishes no `dt` (its §10 item 1): the step is
the executing runtime's choice, a continuous law is exact across its kinks
at any step, and a jump or a stop is located inside whatever tick it falls
in. What `dt` changes is the granularity of commands and the first-order
localization of a stop behind a nonlinear edge.

`1/240` is proposed because:

- it is the step the campaign's own interface sketch uses
  (`Sim(machine, dt=1 / 240)`);
- the acceptance machine resolves at it with room to spare: the Pascaline's
  carry ramps are 3° and 6° wide in drum angle and a dial turns 36° per
  digit over one second, so the narrowest window is 1/12 s — twenty ticks;
  the project's own scenarios agree at 1/60 and 1/120, so 1/240 is inside
  the cadence-independent band it has already measured;
- it is four ticks per frame at 60 Hz and real-time speed, which is a
  cadence a worker absorbs without ever being the frame's critical path;
- every instruction the acceptance document declares has a duration of
  1.0 s, a whole number of ticks at 1/240 within `Sim._ticks`' own 1e-9
  window.

A host sets it once, through the `run: {dt}` mount option; a non-finite or
non-positive value is refused naming it. It cannot be changed afterwards:
`RunSnapshot` carries `dt` and a restore across two step sizes is refused
by the framework's own rule, so a `setDt` would silently invalidate every
snapshot a host held. Changing it means a new mount.

### D7. Speed is a multiple of real time; the tick rate follows from it

The viewer already has one meaning for speed — a multiple of real time,
with `speed()`, `setSpeed()`, a ladder from ×0.1 to ×3600 and
`assertSpeed` — and a version 5 document gets the same one. The ticks an
advance asks for are `speed × elapsedWallSeconds / dt`, accumulated with
the fractional remainder carried across frames so ×0.1 does not round to
zero ticks a frame and stall. **Speed never changes `dt`**: at ×3600 the
machine takes 3600 times as many ticks per wall second, each of them the
same tick, so the mechanics are cadence-identical and only the wall clock
differs. The alternative — scaling `dt` with speed — would make a fast
watch a *coarser* simulation, which is the one thing a jump law cannot
survive.

*Why reuse `speed()` rather than add `setTickRate()`:* a maker means one
thing by "faster", and two speed numbers on one handle is two numbers to
get out of step.

### D8. A hidden page holds still

No animation frame, no advance, no tick: the run stops where it stands and
its elapsed-simulation-time readout stops with it. It is stated here
because it is a behaviour a maker will meet — leave the tab, come back, the
machine is where you left it — and because the alternative, catching up,
is a thousand ticks of mechanism nobody watched.

### D9. The advance is capped

`ticks` per advance is capped at `4 × speed × frameBudget / dt` (four
frames' worth). A stall longer than that — a garbage collection, a
long-running extension, a laptop lid — loses the wall time beyond the cap
rather than integrating it in a burst. Losing it is visible (the elapsed
readout falls behind the clock on the wall) and integrating it is not.

## 7. The running handle

`ViewerHandle.run()` returns `RunHandle | null` — `null` for a document
that carries no program, which is every document versions 1 to 4, so a host
asks one question and gets a truthful answer. The handle:

```
identity(): string           dt(): number            tick(): number
elapsed(): number            state(): Record<string, number>
coordinates(): Record<string, {kind, unit, domain, initial}>
start(): void                pause(): void           running(): boolean
step(ticks = 1): Promise<void>
move(input, {by?|to?, duration}): Promise<Outcome>
rate(input, rate): Promise<Outcome>
trigger(name): Promise<Outcome[]>
cancel(input): void          reset(): Promise<void>
snapshot(): Promise<RunState>  restore(state): Promise<void>
onCommit(fn): () => void     onOutcome(fn): () => void
runsInWorker: boolean
```

`move`, `rate` and `trigger` resolve when the command retires, with its
final status and the travel it admitted — the one thing the pilot's model
insists every request reports. `step(n)` integrates exactly `n` ticks
whether or not the run is started, which is what makes a headless or a
scripted drive deterministic: the acceptance test presses ten instructions
and steps 2400 ticks rather than waiting ten wall seconds.

`onCommit` fires once per frame with the committed bank, the tick and the
records; it is the channel a host's own instrument panel reads, and in the
next change it is what the chrome's readouts follow.

### D13. A mounted run starts paused

A run does not begin advancing because a page opened. It is created at the
published rest bank, paused, and starts when a host calls `start()` — or,
in the next change, when a maker presses a control. Three reasons, and the
third is the one that decides it:

- with no command active nothing moves anyway, so auto-starting would
  integrate empty ticks sixty times a second for a machine standing still;
- a machine that begins moving the instant a page loads is a surprise, and
  a law that reads the run's clock *would* move;
- **the capture and every thumbnail get the rest pose for free**, without
  knowing that runs exist. `solid-node-viewer capture` already mounts with
  `animation: 'external'` and never plays the timeline; under this default
  it never steps the run either, which is exactly the still the framework
  asks for.

`autoplay` is not reused for it: `autoplay` is about `$t`, and a version 5
document has no `$t`. A host that wants a machine running on arrival calls
`start()`, or mounts with `run: {autostart: true}`.

## 8. Numeric parity: every place the two runtimes could differ

Each row is a decision, and the corpus is what proves it.

| Where | Python | Here |
| --- | --- | --- |
| `%` in an expression | `math.fmod` | JS `%` — verified identical in sign and magnitude for `(-7) % 3` and `7 % (-3)` |
| `^` | `operator.pow` | already exponentiation in the shared evaluator, with the unary-minus rule, pinned by the parity fixture |
| a comparison in an expression | `operator.lt` … returning `bool`, then float arithmetic | JS comparison returning `boolean`, coerced by the same arithmetic |
| `sign` | `(x > 0) − (x < 0)` | the same formula, in `branchOf` **and** in `context.sign`; `Math.sign(-0)` is `-0` where the framework's is `0` |
| `floor`, `ceil` | `math.floor`, `math.ceil` | `Math.floor`, `Math.ceil` |
| a branch for `%` | `math.trunc(level)` | `Math.trunc` |
| an integer ramp | `start + (delta * k) // ticks` | `start + Math.floor((delta * k) / ticks)`, which is Python's floor division for these operands and, unlike truncation, agrees for a negative delta |
| an integer rate | `math.trunc(rate * dt * elapsed)` | `Math.trunc`, and the same "truncated toward zero, so a negative rate rounds the way a positive one does" |
| a design-unit target | `Driver.native`, round half to **even** | `toNative` in `drivers.ts`, already round-half-to-even |
| a linear formula | `total = constant; total = total + held[k] * f` in `needs` order | the same accumulation, in the same order |
| the earliest stop | `sorted((t, identifier, side, bound))`, Python tuple order | an explicit comparator on `t`, then id, then side; ASCII ids compare identically by code point and by UTF-16 code unit |
| a partition's listing | `located.sort(key=(t, postorder index))` | the same comparator |
| duplicate crossings | `_deduplicated` by `(where, level)` with the tolerance | the same |
| whole-number surfaces | `range(floor(first), ceil(last) + 1)` | the same enumeration, guarded by the same `isFinite` and `_MAX_CROSSINGS` checks |
| agreement | `abs(a − b) <= 1e-9 * max(1, |a|, |b|)` with `1e-9` read from `limits.agreement` | the same, read from the same published number |

Two of these are corrections to the shipped evaluator (`sign`, and the
nesting of D10); the rest are obligations on new code. None is a tolerance:
the corpus compares discrete state exactly, and the only floats it admits a
window on are the ones the run itself declines to distinguish.

## 9. The conformance suite

`src/running-corpus.json` is the framework's `tests/running-corpus.json`,
copied byte for byte — the same arrangement the expression parity fixture
already has, and for the same reason: **the numbers in it are the
framework's, not ours.** `src/run/running-corpus.test.ts` replays it.

Per scenario: build the engine from the fixture's `document` — which
carries `format`, `version`, `drivers`, `instructions`, `bindings` (when
the machine has any) and `program`, and deliberately **not** `root`,
`pieces` or `animation` — at the fixture's `dt`, with a record ring large
enough for the whole run. Then for `tick = 1 … steps`: apply the script
entries naming that tick in array order, integrate one tick, and compare
the fixture's entry:

- `tick`, every status word, every coordinate, relation, primitive, bound
  side and input name, every crossing `level`, and the **order** of every
  list: exact;
- every bank value, every `t`, every `admitted`, every stop `value`:
  `|a − b| <= 1e-9 · max(1, |a|, |b|)`, the corpus's own
  `tolerance.float`, which is `program.limits.agreement`.

Commands are compared in the order the fixture lists them, which is the
order the handles were created — a `trigger` naming one handle per input it
claims, in issue order.

The suite also asserts the fixture's **width**, mirroring the generator's
`uncovered_features`: the five jump primitives, a multi-source law, a stop
inside a tick, an expression bound, a `blocked` command, a rate, a
snapshot, a restore, both instruction forms and a tick carrying both a
crossing and a stop. A narrower corpus copied in is then loud here, without
anyone running the generator.

*Why the engine and not the worker:* the worker is a transport and the
engine is the algorithm. The worker gets its own small test (a message
round trip against an in-thread fake), and the in-thread fallback path is
the one the corpus exercises 260 times.

## 10. The version and capability bumps

- **Document versions.** `RENDERED_VERSIONS = [1, 2, 3, 4, 5]`. A version 6
  document is refused by name and by list, which is the same sentence a
  version 5 document gets from every viewer released so far.
- **The viewer API rises to 7 → 8.** Executing a published program is a
  capability a host may require — the shop floor, `solid develop` and the
  export page all mount documents the framework now publishes at version 5
  — and the handle gains `run()`. That is both halves of the rule the
  package states for raising the number.
- **`documentVersions`.** `describe()` gains
  `documentVersions: [1, 2, 3, 4, 5]`. The
  framework reads it to decide whether `solid build` warns and whether
  `solid snapshot --renderer web` is refused before a browser starts;
  absent, it assumes `[1, 2, 3, 4]`, which is every viewer released so far.
  It is declared **once**, in `package.json` as
  `solidNodeDocumentVersions`, injected into the bundle by `build.mjs` as
  `__DOCUMENT_VERSIONS__` and read by `bundle.py` from the same file, so
  the Python answer and the JavaScript refusal can never disagree —
  exactly the arrangement `solidNodeViewerApi` already has. The
  development server's `/_viewer` route is deliberately **not** widened:
  its consumer is the development page, which mounts the bundle and lets
  it refuse, and the only consumer that has to ask before publishing is the
  framework, which asks the entry point.

## 11. What this change does not do

- **No on-screen control for a running document.** No nudge, no jog, no
  instruction button, no run/pause/step/speed bar, no elapsed readout,
  no reset. A version 5 document mounts, poses at its rest bank and is
  driven by its host. The chrome is `drive-the-run-on-screen`, and
  constrained dragging of a part is the cycle after that.
- **No change to the dev server or the capture.** They inherit version 5
  through the bundle; what they must say about a *run* — reload keeping a
  run whose program identity is unchanged, a capture stating what it
  photographs — is the next change's, because both sentences are about
  controls and state a host can see.
- **No recording, checkpointing or replay UI.** The rings are bounded and
  internal; seeking belongs to recorded history, and the pilot has ruled
  out a live-time scrubber.
- **No framework edit.** The `viewer` extra's version floor is the
  framework's follow-up once this package is released.

## 12. Risks

1. **A divergence the corpus does not exercise.** Its guard covers the
   feature list the framework stated, not every float path — a `%` with a
   negative divisor, a `sign` at exactly zero, a bisection landing on a
   sample. Mitigation: §8 is a table of *decisions*, each with a unit test
   of its own beside the corpus, and the acceptance document is a
   fourteenth scenario the corpus does not contain.
2. **Cost per tick.** A non-affine level quantity samples 64 points and
   bisects up to 64 rounds per crossing, per jump node, per segment. The
   acceptance machine's three plans are affine (`affine: true` on every
   published jump), so they solve rather than search; a machine that
   searches is the one to measure. A task records ticks per second for the
   Pascaline and for a searched-plan fixture, so a regression is a number.
3. **Blob-worker policy.** A host page with `worker-src 'none'` gets the
   in-thread fallback and a slower frame. Reported on the handle, not
   hidden.
4. **The bindings table now carries names that are only bound inside a
   plan** (`_j0`). A future change that evaluates a binding outside the
   plan that defines its placeholder would read `undefined` and pose a
   `NaN`. Mitigation: the placeholder set is part of the loaded program and
   the load-time name check knows where each one is legal; §11 finding 2
   proposes the framework-side narrowing.
5. **One advance in flight means the run's rate depends on the frame
   rate.** A 30 Hz display integrates the same ticks per wall second as a
   60 Hz one (the elapsed time is what is measured), but a display that
   stops stops the machine. Stated, not mitigated: it is D2's decision.

## 13. Open questions

1. **Should a host be able to advance the run without a display?** `step(n)`
   does it today, but a genuinely headless host (a test, a thumbnail
   pipeline) might want the worker to free-run without an animation frame.
   Deliberately not offered here, because free-running is where invisible
   backlogs come from.
2. **Should `identity` gate a reload?** The framework refuses a snapshot
   across a changed program. The next change states the reload rule
   (`drive-the-run-on-screen`, keep the run when the identity is unchanged,
   reset otherwise); whether a host should also be able to *migrate* a run
   across a changed program is the pilot's.
3. **Should the frame message carry the intermediates too?** The engine
   recomputes them per tick and discards them; a host's readout of a plain
   port (`units.stop.angle`) would have to re-derive them. Cheap to add,
   and not added until something asks.
4. **`record` default.** 600 ticks (2.5 s at 1/240) is proposed as the
   ring length. The framework's own default is `None` — no record at all.

## 14. The ADRs to extract

The viewer's log continues from its highest number, 044.

- **ADR-045 (EXPORT): The run executes in a worker and the main thread only
  poses.** The decision that a published program is integrated by a
  TypeScript engine mirroring the Python run function for function; that it
  runs in a Web Worker with the *render loop driving the cadence and one
  advance in flight*, so a hidden page accumulates no backlog and a dropped
  frame drops display and never mechanics; and that a page that cannot
  create the worker runs the same engine in-thread and says so. Extends
  ADR-035 (the reusable core and the declared API version); consumes
  solid-node's ADR-110.
- **ADR-046 (EXPORT): A committed bank is a name in the same scope as a
  driver.** The decision that a run's coordinates pose the geometry through
  the evaluator the widget already has, by widening the evaluation scope
  rather than adding a second pose path — with the full-depth nesting of a
  qualified id, and the refusal of an id set that cannot be nested, as its
  consequences. Extends ADR-043 and ADR-044.
- **ADR-047 (EXPORT): The corpus is what makes the two runtimes one
  algorithm.** The viewer's half of solid-node's ADR-111: the framework's
  committed fixture is replayed in-thread against the engine, exact for
  discrete state and at the run's own agreement window for floats, with the
  generator's coverage list mirrored here so a narrowed corpus is loud, and
  a divergence is a bug in this viewer. Beside ADR-022's pattern, which the
  expression parity fixture already follows.

## 15. Findings against the framework's published contract

Neither blocks this change; both are named so the framework side can decide.

1. **`program.intermediates` lists ids no edge determines.** The export
   spec says an intermediate is "every value a compiled edge determines
   that the bank does NOT hold", but the acceptance document publishes six
   — `units.wheel`, `units.stop.angle` and their two siblings per column —
   that appear in no edge's `needs` or `gives`, and whose `sources` entry
   is the empty list. They are `Program.nodes` entries of kind
   `intermediate` whose edges were not compiled because they drive nothing
   in the bank. **Proposed resolution, viewer side:** accept them as
   declared names and refuse only one that something actually *reads*,
   since a read one cannot be computed. **Framework follow-up, if the
   pilot wants the published list to mean what the spec says:** publish
   only the intermediates some edge gives, or publish the
   uncomputable ones under a name that says so.
2. **The ratified rule for a `bindings` entry no longer describes what is
   published.** The export spec's "A shared subexpression is published
   once" says an entry's expression "names only `$t`, qualified driver ids
   declared in the document's `drivers` table, and entries appearing
   earlier in the array", and concludes that "a consumer SHALL therefore be
   able to evaluate the table in one forward pass … before evaluating any
   operation or `params` expression". A version 5 document breaks both
   halves, in two different ways, and the acceptance document shows each:

   - **Bank ids.** `_b0 = (-1 * units.drum.turn)` names a joint
     coordinate, which is not a key of `drivers`. This is the intended
     consequence of "a committed bank poses the geometry" — the pose
     expressions name bank ids, so the subexpressions shared out of them
     do too — but the bindings requirement was not widened with it.
   - **Branch placeholders.** `_b33 = (360.0 * _j0)`, `_b41`, `_b48` name
     placeholders that are bound only while *one* plan's skeleton is being
     evaluated. There is no scope in which the whole table has a value, so
     the one-forward-pass reading is not merely inconvenient, it is
     impossible.

   **Resolution, viewer side (free):** this viewer has never evaluated the
   table forward — a binding name resolves through the shared DAG *where it
   is read*, so an entry nothing reads is never evaluated (ADR-044's own
   "An entry nobody reads costs nothing"). The loaded program records which
   placeholders belong to which plan, the load-time name check admits a
   placeholder only inside its own plan's expressions, and the engine binds
   it only there.
   **Framework follow-up, for the pilot:** widen that requirement's
   sentence to say an entry may also name a bank coordinate, a published
   computed value and — inside a plan — that plan's branch placeholder, and
   replace the one-forward-pass conclusion with the lazy reading the
   consumer actually performs. The alternative, keeping placeholder-bearing
   subexpressions out of the shared table, costs the document the sharing
   ADR-080 exists for.
3. **`sign` differs at negative zero.** `solid_node.math.sign` is
   `(x > 0) − (x < 0)`, which is `0` at `-0.0`; the viewer's `Math.sign` is
   `-0`. No parity case pins it. **Resolution, viewer side:** take the
   framework's formula, here, with a red test. No framework change asked.
4. **The corpus's machine entries carry a `steps` key** the framework's
   §7.3 does not list. Harmless and used (it is the tick count), recorded
   only so the viewer's replay is not thought to be reading something it
   invented.
