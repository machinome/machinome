# ADR-128: A Clocked Root Publishes Its Compiled Machine, at a Version an Old Consumer Refuses

**Status:** Accepted
**Date:** 2026-09-17
**Corrected:** 2026-09-17 — the framework's own commit path REFUSES a non-finite commit value (`ClockedError` naming the relation, the state and the value, judged before an integer state's rounding, the request refused whole), which this decision's export requirement already required of a CONSUMER and the implementation did not do on either side; the corpus generator refuses to write a fixture recording one, and `tests/clocked-corpus.json` is byte-identical. Narrow adjustment under this decision, not an amendment of it: the document, its version, its keys and every value it carries stand as written (`openspec/changes/archive/2026-09-17-publish-the-clocked-machine/evidence.md`, section 10).
**Depends on:**
- [ADR-125: A state is a driver the machine writes, committed at an event](./ADR-125-a-state-is-a-driver-the-machine-writes.md) — the clocked root, its bank, its request, its exact event solve, its landing rule, its commit and the publication refusal this decision LIFTS; it is also the decision this one CLARIFIES on one point, below
- [ADR-126: A bound stops a clocked request on its path](./ADR-126-a-bound-stops-a-clocked-request-on-its-path.md) — the compiled constraint per (coordinate, side), its chain, its own-coordinate read, its jump plan and its threshold, all of which this decision publishes; clarified on one point, below
- [ADR-127: A clock is a banked value, and an event on it is an event](./ADR-127-a-clock-is-a-banked-value-and-an-event-on-it-is-an-event.md) — the elapsed clocked root whose banked seconds this decision publishes as a free name, and whose "no new tolerance" claim this decision corrects to "no new USE"
- [ADR-110: The compiled program is published in the document](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md) — the version ladder, the rung-is-a-property-of-the-declaration rule, the reserved free name published as a string, the native-graph expression slots and the producer behaviours this decision takes unchanged
- [ADR-111: A conformance corpus is the contract between the two runtimes](../EXPORT/ADR-111-a-conformance-corpus-is-the-contract-between-the-two-runtimes.md) — the producer-generated fixture, its coverage guard and its replay, whose pattern the clocked corpus follows with ONE substantive difference: it is EXACT
- [ADR-080: A shared subexpression is named once](../EXPORT/ADR-080-a-shared-subexpression-is-named-once.md) — the document's ordered `bindings` table, which every expression the `clocked` object carries joins in the same pass as the tree's
- [ADR-121: A law may read the coordinate it drives](./ADR-121-a-law-may-read-the-coordinate-it-drives.md) — `far_side_of`, the ONE landing walk, whose first step this decision sizes by the segment
**Cites:**
- [ADR-107](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md), [ADR-123](./ADR-123-a-kink-is-a-cut.md) — the jump vocabulary, its surfaces and branches, and the structural classification a published `shapes` entry states; no key is added for any of them
- [ADR-109](./ADR-109-a-range-bound-may-be-an-expression-evaluated-at-the-committed-state.md) — the law/bound asymmetry, which is why a published commit law is DESUGARED and a published chain is VERBATIM
- [ADR-022](../MATH/ADR-022-cross-runtime-degree-trig-parity-for-t-expressions.md) — the parity fixture, which pins the symbolic vocabulary function for function and, as this cycle measured, does NOT pin `%`
- [ADR-034](../EXPORT/ADR-034-shared-node-tree-document-schema.md), [ADR-051](../EXPORT/ADR-051-producer-owned-animation-time-in-node-documents.md) — the document schema and the producer-owned `animation` object, unchanged here
- [ADR-124](./ADR-124-only-what-moves-along-a-tick-s-path-is-evaluated.md) — path evaluation, which a commit still does not use: a commit is a Python call
**Amends** ADR-125 and ADR-126 on ONE point each, both of them
CLARIFICATIONS found by this cycle's own corpus and closed here rather than
deferred — the containment of a crossing in a request, and the size of the
landing walk's first step. It **amends nothing else**: versions 5, 6 and 7,
the running corpus, `simulation/run.py` and `Time.running()` are untouched,
asserted by diff and by hash.
**OpenSpec change:** `publish-the-clocked-machine` (archived at
`openspec/changes/archive/2026-09-17-publish-the-clocked-machine/`)
**Originating project:** `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation`, HEAD `9fb725f`; the project-level spike is its worktree
`WTs/clocked-spike`. The Curta's clocked model reproduces the operating
model's registers at every stroke end and is worth nothing to its pilot
until a browser can crank it — which needs, first, a document that says what
the machine IS.

## Context and Problem Statement

ADR-125 gave the framework a machine with MEMORY and refused to publish it.
That refusal was deliberate and temporary: a clocked tree's pose expressions
read its declared states as FREE NAMES, so a document carrying them at a
version an existing consumer believes it can read would resolve `w0.digit` to
nothing and animate the model wrongly. ADR-126 and ADR-127 then added
constraints and a clock to the same executor, and the refusal held through
both.

The consequence is that everything ADR-125, ADR-126 and ADR-127 built exists
only inside a Python process. A browser cannot crank the Curta, a snapshot
cannot photograph it, an export cannot carry it. The machine is compiled at
`Sim` construction — every relation's event level classified, every
constraint's chain composed, every refusal already made — and none of that
compile leaves the process.

Two questions had to be answered together:

1. **What does a consumer need in order to EXECUTE a request?** Not to
   replay a recording: to solve, land, commit and clip the way the framework
   does, on its own, from the document alone.
2. **How does a consumer that cannot do that fail?** Loudly, before it draws
   anything — because the failure mode of getting this wrong is a model that
   renders and is silently wrong.

## Decision Drivers

- **One authority.** ADR-126's own principle: the thing that COMPILED the
  machine is the thing that says what it is. A consumer that re-derived a
  classification would cut a kinked path differently and land on a different
  float.
- **A wrong render is worse than a refusal.** ADR-110's rung rule exists for
  exactly this, and a clocked document is a stronger case than a running one.
- **Nothing a stateless model pays.** ADR-125's zero-cost property has to
  survive publication, not only simulation.
- **Bit-for-bit, or the discipline is not what it claims.** A clocked
  executor has no window inside which it declines to distinguish two values:
  two relations are ONE event exactly when their landings are the SAME float.
- **The framework may not move what it already published.** Versions 5, 6 and
  7 and the running corpus are other cycles' ratified contracts.

## Considered Options

**Publish the states as their initial values at a lower version.** Rejected
outright, and not reopened: the geometry would be right only at the initial
state and would then silently stop following the machine.

**Treat version 8 as additive, so a version 7 consumer renders what it can.**
Rejected: the pose expressions are the part it cannot read.

**Publish a recording instead of a machine** — a table of instants a consumer
plays back. Rejected: a machine is operated, not played; the Curta's whole
point is that the maker turns the crank.

**Let the consumer re-derive the classification, the plan and the chain from
the law text.** Rejected by the one-authority driver above.

**Publish the commit law verbatim.** Rejected on measurement: the executor
CALLS the project's Python callable, and Python's `%` is floored where the
document's is truncated, so a verbatim law would not mean what the executor
computed (see *the two remainders*, below).

## Decision

### Version 8 is a property of the ROOT'S DECLARATION, and it dominates

A tree in which anything declares a `State` publishes `version: 8`, whatever
its tree content. This is version 5's rung and not version 3's or 4's: a
flexible leaf and a shared subexpression are properties of the TREE, read off
the finished document, while a compiled machine is a property of the
declaration — "a running root with a trivial program is still a machine a
version 4 consumer would animate wrongly", and a clocked root with one state
is exactly that machine. Eight DOMINATES every other rung: a clocked document
carrying a flexible leaf or a non-empty `bindings` table still declares 8.

**The bump is not additive.** A version 7 consumer handed such a document
resolves the states to nothing, so it SHALL refuse the document by name
rather than render it. A root that declares no `State` never declares 8,
carries no `clocked` key, and publishes the document it published before this
rule existed, byte for byte.

### The gate is re-aimed, not deleted

ADR-125 put its publication refusal in `document_body`, the one function all
four producers pass through, because a browser-rendered snapshot BAKES one
instant and never enters the symbolic walk. The refusal stays there and
changes meaning: `document_body` gains a `clocked=` parameter beside
`program=`, and refuses a clocked tree published WITHOUT its compiled
machine, naming the states. That is a PRODUCER error — it is what stops a
fifth producer, added later, from reaching a lower-version document by a
route nobody re-checked. The structural question it asks, its cost, and "a
stateless model is answered by one walk that renders nothing" are unchanged.

### `drivers` stays the handles; `states` joins it as a second table

A `State` takes `Driver`'s five fields with their meanings, so it publishes
through exactly the drivers table's rules: `default` native, `range` in design
units and never a clamp, `dtype` by name, `unit` and `scale` verbatim, keys
sorted. They are TWO tables and the split IS the handle rule: every key of
`drivers` is an input a person may move, and no key of `states` ever is. One
table with a `kind` field would put that mistake one field-read away. The two
id sets are disjoint, which the qualified walk already guarantees.

**There is no `coordinates` table.** A running bank holds joint coordinates
whose initial values come from the rest render — the one number a consumer
cannot compute without running the CAD tree. A clocked bank holds no joint
coordinate: it is every declared driver and every declared state at its
declared default, plus, under an elapsed base, the clock at zero. Every one
of those numbers is already in the document. Inventing an entry would publish
something a consumer must then be told to ignore. The consequence is stated
rather than hidden: `Sim(model, state={...})` is session setup and is NOT
published — a document says where the machine RESTS.

### The `clocked` object

Top-level, beside `drivers`, `states`, `instructions` and `bindings` and
ahead of `root` — the program's position, for the program's reason — ordered
deterministically so republishing an unchanged model is byte-identical:

```
clocked: { "identity", "clock", "own", "commits", "bounds", "limits" }
```

Every expression slot holds a NATIVE GRAPH and not text, so a subexpression a
commit law shares with the geometry that displays it is named ONCE in the
document's own ordered `bindings` table.

- **`commits`**, one entry per committing relation in tree order, carrying
  `sources` in WRITTEN order (the law's positional order), `at` as ONE jump
  node — its `primitive` and its jump-free LEVEL, the surfaces and branches
  being the published vocabulary a version 5 consumer already implements, so
  no key is added for them — `law` as one expression per target aligned with
  `targets`, `shapes` per input, and `description`/`stated_by` so a consumer's
  refusal names what a reader can find in the model. A law returning a plain
  number publishes that number: a commit's law IS the value written, so a
  constant is a real answer, which is the asymmetry with a running law edge
  whose `null` means "contributes no increment". An `int` target is rounded
  ONCE at the commit, half to EVEN, and the document states which: JavaScript
  rounds a half toward +infinity and OpenSCAD away from zero, three runtimes
  and three answers. No `scale` is applied at a commit and none is published
  for one.
- **`bounds`**, one entry per compiled constraint — per (coordinate, SIDE),
  which is the unit ADR-126 compiles and the unit a `Stop` reports — carrying
  the CHAIN as `value`, the compiled `bound` with its own coordinate under
  the minted own-name, the level's jump `plan` in exactly the running
  document's shape through the same publisher and the same placeholder
  minting, `shapes` per moving input (the skeleton's and each jump's), and the
  `node`/`joint` a stop names. **The LEVEL is the consumer's own
  subtraction**: `side` says which, and publishing it as well would publish
  the bound twice. A declared range that reaches nothing still appears, as a
  numeric `value` with empty `shapes` — the machine really does declare it.
- **`own`** is a MINTED name, `_own`, lengthened while any published id
  equals it. `$own` cannot travel: the document's expression language admits
  exactly one `$`-name, and widening that shared regex for one producer's
  private convention was rejected. A consumer evaluates each bound's `value`
  over the bank at the request's start and holds the result under this name
  for the whole request. It is the published-clock pattern exactly: one
  reserved free name, published as a string, not a convention a consumer has
  to know.
- **`limits`** publishes `crossing_tolerance` and `max_crossings`.
  `subdivisions`, `bisection_rounds` and `agreement` are NOT published: a
  clocked path never searches, never bisects and never compares two
  increments.
- **`identity`** is a sha256 over a canonical listing — the root class, each
  input and state with its `dtype` and `scale`, each relation's ends,
  primitive and law text, each constraint's coordinate, side and level text —
  so a bank taken against one machine is refused against another, and a
  changed RANGE changes the identity.

### The clock is the free name `time`, and `$t` is untouched otherwise

Under `Time.elapsed()` the document carries the free name `time` — version
5's rule applied to the base it was written for, and necessary, because the
viewer poses a clocked machine at its BANKED INSTANT while `$t` is a 0..1
animation variable. Under a clocked root with no time base, `clocked.clock`
is `null`, the `animation` object is the one an undeclared root publishes,
and a geometry that is a formula of `$t` animates on that timeline while the
bank stands. The preview a clocked model gets, stated plainly, is the INITIAL
BANK posed with `$t` sweeping.

### Instructions are published in the version 5 shape, with no meaning

The cycle's brief said an instruction under a clocked root is refused today.
**It is not**, and the probe is in the evidence: only an instruction whose
TARGET is a state is refused, at simulation construction, and every producer
compiles before it publishes — so there is no route to a document that skips
the refusal. A version 8 document therefore publishes EVERY declared
instruction, each carrying exactly one of `targets` and `by` beside
`duration`. The table's flag was never "running": it means "version 5 or
above", and it is renamed to say so. **This cycle gives the table no runtime
meaning**; `trigger` stays refused by name, and what a clocked consumer may
do with an instruction is a later question, recorded as a wart. A CONTROL
stays refused in both places, so a version 8 document never carries a
`controls` key.

### The producers need nothing new

The viewer's own `describe` report already carries the document versions it
renders, and the framework already turns "this viewer cannot read version N"
into one sentence. Version 8 is simply absent from that list until the
viewer's own cycle adds it, and a viewer reporting no versions at all is read
as the four every viewer released before the field existed renders. So a
build and an export WARN and publish — an export is an artifact a later
viewer may open — a web snapshot is REFUSED before the browser starts, with
no image and no staging directory left behind and never a silent fall back to
OpenSCAD, and an OpenSCAD snapshot renders the tree as posed: the initial
bank. Each producer gains two lines, compiling the machine and passing the
block.

### The two remainders, and which one a document carries

The `%` hazard is real and it is NOT Python-versus-JavaScript. **The
DOCUMENT's `%` is TRUNCATED in both runtimes** — the framework's two
evaluators spell it `fmod`, the viewer's is JavaScript's native `%` — and the
two runtimes agree. **The CLOCKED EXECUTOR does not evaluate the law graph
at all**: it calls the project's Python callable with the bank's numbers, and
Python's float `%` is FLOORED. So the breach is INSIDE the framework, and a
law graph published as written would not mean what the executor computed:
`(-1) % 10` is `9` in the bank and `-1` in a verbatim graph.

**Decision: a `%` node in a published commit LAW is DESUGARED to the floored
remainder.** CPython's `float_rem` is `mod = fmod(a, b); if (mod) { if ((b <
0) != (mod < 0)) mod += b; } else mod = copysign(0.0, b);` — `fmod` is exact
and the correction is a single IEEE addition, so the document's own
vocabulary reproduces it with the same one rounding. Verified against
CPython's own operator over **500 000 random double pairs** — uniform small,
wide-magnitude with a sub-ulp divisor, integral, and random finite bit
patterns of both signs — with **zero value mismatches**; 5577 pairs differed
only in the SIGN OF A ZERO, which compares equal as a number in both
runtimes and which nothing in the published vocabulary distinguishes. The
committed regression runs 6000 pairs plus six hand cases on every suite run.

**A CHAIN, a BOUND and a constraint LEVEL keep the document's `%`**, verbatim
and un-desugared, because the framework evaluates THOSE through the graph —
every threshold, clip and judgement calls the graph evaluator, whose `%` is
`fmod` — so the published graph already says exactly what the clip computed.
An `at` cannot carry a `%` at all: `%` is a jump operator and an event level
admits exactly one jump node, which must be `floor`, `ceil`, `sign` or a
comparison.

This cycle publishes the truth of each place it publishes FROM and fixes only
what it publishes for the FIRST time. The rest is recorded as warts, not
silence: the CROSS-MODE divergence (the same law text means floored under a
clocked root and `fmod` under a running one) and the POSE-versus-GRAPH
divergence, which is framework-wide and pre-existing — a `drives(law=)`
taking `%` of a negative poses through the callable and publishes through the
graph, in EVERY document version from 2 upward. Reconciling either means
changing what a published pose expression or a running law edge MEANS, which
moves versions 5, 6 and 7 — the one thing this cycle may not do.

### The corpus is EXACT, and the claim is stated operation by operation

`tests/clocked-corpus.json` is written from the framework's own clocked
executor, replayed by the framework's suite, and committed by the viewer for
its own replay. It carries `"tolerance": {"float": 0.0}` as a FIELD of the
file rather than a convention of its reader, and the replay compares with
`assertEqual` and nothing else.

A tolerance would not merely be slack here; it would admit a consumer that is
wrong about the thing this discipline exists to be right about, because two
relations are one event exactly when their landings are the same float. The
claim rests on IEEE `+ - * /` and `sqrt`, correctly rounded by the standard;
the truncated remainder, exact, and the floored one composed from it, one
extra rounding; `floor`, `ceil`, `abs`, `sign`, `min`, `max` and the six
comparisons, which SELECT rather than round; and the LANDING WALK, a
bisection in the ORDINAL space of a double's own bits, which a second runtime
must reproduce as a bit walk and never with arithmetic. It does NOT rest on a
transcendental or a power, neither correctly rounded — and the generator
REFUSES a machine carrying one in a published commit law, event level,
constraint level or chain, so the limitation is enforced rather than
remembered.

**Measured**: 30 machines, 30 scenarios, 76 steps, 139 262 bytes. The claim
is PROVED rather than declared — moving ONE recorded landing by ONE
representable value, a drift far inside `1e-9` relative, makes the replay
fail. A coverage inventory stated in the tool refuses to write a corpus that
misses any listed feature, and the suite tests that refusal directly, so the
corpus's width is visible without running the generator.

The corpus's widest machine is the **Curta-shaped fixture**: four dials of
one class so a carry propagates twice, a stroke relation over all four digits
and an operand, one clearing relation per dial reading the digit it writes, a
selector wired through an intermediate PORT, a ratchet reading its own
coordinate, a freeze both of whose bounds read it, and a law landing an `int`
state on an exact half. Compiling it costs 8.3 ms, publishing 0.39 ms; its
longest published chain is 3 nodes and its `clocked` object 4919 bytes in a
document of 8071. The cases a second runtime gets wrong are the
INTERACTIONS, and a corpus of machines that each carry one feature exercises
none of them.

### Closure: two clarifications of ADR-125 and ADR-126

This cycle's corpus found two requests the SHARED locator had no answer for.
Neither is a new behaviour; each is a place where the locator refused or LOST
a request the ratified rules already describe, so both close here.

**A crossing belongs to the request whose path CONTAINS its landing.**
ADR-125 stated the containment by FRACTION — the right end inclusive, the
left end exclusive — and that reading loses an event. A request ending
exactly ON a STRICT comparison's surface solves its crossing at fraction 1.0,
but the landing, the nearest representable value on the far side of a strict
surface, is the first float BEYOND the endpoint; the request committed it and
then resumed from a point past its own target, so the remaining travel was
NEGATIVE and the same surface was re-solved backwards until the walk raised.
And the NEXT request, resuming from that endpoint, excluded its own left end
by fraction, so the surface was skipped there too and the event was lost by
both. The rule is now stated by LANDING in both directions: a landing ON the
endpoint is this request's, a landing one representable value beyond it is
the next request's, and the left end is therefore excluded by LANDING and not
by fraction — a crossing solved at fraction ZERO whose far side lies ahead
inside the path IS an event, while a request resuming from its own landing
still fires nothing because there the landing IS its start. The correction
also recovers an event outside the strict case: a `sign` level standing at
zero and moved off it takes TWO rising steps, `-1 → 0` at the centre and
`0 → +1` at the float above it, and the corpus now records both.

**The landing walk's first step is sized by the SEGMENT, never by the ulp of
zero.** `far_side_of` doubled `math.ulp(own_star)`, and the ulp of a value
that happens to be `0.0` is a denormal: two hundred doublings reach about
1e-263, no distance at all on a segment a millimetre long, so a bank standing
outside a LOW bound with its coordinate at exactly zero raised instead of
stopping, where the HIGH-bound mirror admitted zero travel and reported its
stop. The walk now takes the ulp of the larger magnitude of the landed value
and the path's ends, passed by the two CLOCKED callers; a caller that passes
no segment keeps the value's own ulp exactly as before, which is what the
RUNNING walk does, so no running landing moves. The stop itself is now said
off the CROSSING and not left to the walk: a level already AT its limit and
pushed further admits ZERO travel, because leaving it to the walk would let
the low side admit half an ulp OF THE LEVEL — `-2.22e-16`, measured — only
because the coordinate happens to stand near zero.

Both are corpus contract, so the viewer's own cycle inherits them.

ADR-127's claim that no tolerance REACHES a clocked path is corrected in the
same spirit: a clocked path introduces no NEW use of the crossing tolerance,
but it does REACH it, when a kinked event level's crossings are merged and
when a jumped constraint level's cuts are folded, both inside the shared
locator. That is why `limits` publishes it.

## Consequences

**A clocked machine is a thing that can leave the process.** A consumer with
the document alone can classify nothing, re-derive nothing and still execute
a request: it has the event levels and their shapes, the laws, the
constraints with their chains, plans and thresholds, the reserved names and
the two limits.

**A wrong render is impossible by construction, not by care.** An old
consumer refuses by name, a producer that forgets to compile is refused by
the gate, and the refusal is tested from each of the four producers rather
than from the gate alone.

**A stateless model pays exactly nothing**, publication included: the clocked
counter reads ZERO across a stateless model's construction, `set_state`,
render, stepping, symbolic walk, compile and `document_body`; importing the
serializer imports neither clocked module; and every stateless and running
document published at the cycle's base is byte-identical afterwards.

**The corpus is now the contract**, and it is exact. The viewer's cycle owes
a bit walk, not an epsilon walk; anything else lands on a different float at
exactly the surfaces the corpus is built on.

**What this decision does not do.** It gives an instruction no meaning under
a clocked root, does not touch the viewer (its own repository, its own
records), does not migrate the Curta, does not reconcile the framework's two
meanings of `%` outside a published commit law, and leaves ADR-125's
structural pre-check for two writers at one event where ADR-125 left it.

**Recorded and open** in `workflow/warts.md`: the two `%` divergences, with
the pose-versus-graph one marked for the pilot because it reaches every
document version from 2 upward; the instruction's meaning under a clocked
root; the identity's consumer; and the RUNNING walk's untouched ulp-of-zero
step, which is the same defect closure 1 fixed on the clocked side and which
this cycle deliberately did not change, because `tests/running-corpus.json`
had to stay byte-identical.

## Promotion

Accepted 2026-09-17 at the cycle's adversarial review, which ran an
independent probe against the uncommitted implementation — an elapsed root
with two child wheels published at version 8, checking that the pose
expressions carry the states as FREE NAMES, that the carry law is desugared
through shared `_b` bindings, that the clock publishes as `time` and the
own-name as `_own`, with the corpus and the golden documents green — and
returned the review's own decisions on seven findings the implementer
reported rather than silently resolved: the constant `shapes` entries are
omitted because the requirement admits two values and a consumer needs two;
the compiled machine and the executor are ONE object and the ADR names it so;
`published(initial)` keeps a parameter it does not read, for the one call
site that dispatches between it and the program's; and the parity fixture's
claim is corrected by evidence rather than re-edited, because it measurably
does not pin `%`.

One finding was NOT deferred. The two `LandingInvariantError`s the
implementer found and left for the pilot are defects of the shared locator
that lose or refuse legitimate requests, and this cycle's corpus is what
found them, so they were closed here, red first, as the closure above. The
implementation's own record — the full red log, every measurement quoted
above, the closure's reds and its corpus diff step by step, and the seven
findings — is `evidence.md` inside the archived change.
