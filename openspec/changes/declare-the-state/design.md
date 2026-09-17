## Context

The originating project, the finding and the measurements are in
`proposal.md`. Two documents bind this design and both are evidence rather
than authority:

- `workflow/docs/clocked-machine.md` — the requirement note, with the
  direction the pilot settled on 2026-09-16 and a **candidate spelling**
  that is explicitly a sketch. Where this design departs from it, the
  departure is numbered below and carries its reason.
- `projects/Calculators/Curta-Type-I-3x/WTs/clocked-spike`, branch
  `clocked-spike`, record `simulation/docs/clocked-spike-2026-09-16.md` —
  the project-level spike, run with no framework change. Its section "What
  the framework proposal must therefore settle" is the requirements input
  this design answers point by point (§13).

Two decisions already made elsewhere constrain everything here:

- **The rejected protocol.** On 2026-09-13 the pilot rejected `running(r)`,
  `r.state`, `r.event` and `r.equal` — a per-relation protocol with event
  objects inside laws (`workflow/open-run-simulation/design.md`, "Decision
  2026-09-13"). Nothing here reintroduces it. A state is a VALUE written by
  commit laws, one answer per event, and the author writes the closed forms
  they already write.
- **`Time.running()` is untouched.** Running mode is the evidence mode: a
  machine whose arithmetic is composed from local laws can FAIL to add, and
  that is where the Curta's framework findings came from. A clocked model's
  commit law already contains the answer. The note records the relationship
  — running is the interpreter over the parts, clocked is the program the
  pilot compiles from it once the parts have proven it — and this cycle
  changes no line of the running executor.

The framework's own tools this design REUSES rather than reproduces:
`JumpPlan._partition`, `_surfaces`, `_solved` and `_branch_of` (ADR-107);
`_shape_of` and `_KinkCuts` (ADR-123); `_far_side` and `_ordinal` (ADR-121);
`_graph_of`'s symbolic inspection and `SYMBOLIC_BUILTINS` (ADR-106); and
`_MAX_CROSSINGS`. **The event solver introduces no new locator, no new
tolerance and no new knob — and it introduces no tolerance AT ALL.**
`_CROSSING_TOLERANCE` goes on doing inside `_solved` and `_KinkCuts` exactly
what it does today, and the clocked solver adds no new use of it: under a
clocked root every crossing is SOLVED, so two relations fire at one event
exactly when their far-side landings are the SAME float (§5).

## Goals / Non-Goals

### Goals

1. A project can declare a retained value and the law that writes it, in the
   grammar the API already has, and get exactly the machine the spike
   emulated in ordinary Python.
2. Events are located EXACTLY. A clocked model's determinism claim is
   stronger than a run's: a snapshot is inputs plus states, a replay is the
   request history, and nothing depends on a `dt`.
3. A model that declares no `State` is unchanged in behaviour, in published
   bytes and in cost.
4. Nothing this cycle admits can publish a document a consumer would animate
   wrongly.

### Non-Goals

Listed in `proposal.md` with the cycle that owns each. The two worth
restating here because a reader will expect them:

- **Bounds do not clip a request path in this cycle.** The spike's finding 4
  asks for it and cycle 2 is where it lands (§11).
- **Time is not a source.** A clocked root in this cycle is UNTIMED, so
  `self.time` is the `$t` animation fraction and not a machine input (§12).

## Decisions

### 1. `State`, beside `Driver`

```python
from solid_node.simulation import Driver, State

class Counter(AssemblyNode):
    crank = Driver(default=0, unit='deg')
    units = State(default=0, range=(0, 9), dtype=int)
    tens = State(default=0, range=(0, 9), dtype=int)
```

`State(default, range=None, unit=None, dtype=None, scale=None)` takes
exactly `Driver`'s arguments with exactly their meanings, including the two
that are easy to get wrong: `range` is PRESENTATION metadata in design
units and clamps nothing (a machine driven past its declared travel is a
crash a simulation must be able to show), and `dtype=int` means the value is
a whole number of NATIVE units. The value is read `self.units` in
`simulate()` and enters an expression exactly as a driver's does.

**Where it may be declared.** On any assembly of the linked tree, exactly
where a `Driver` may be declared, and qualified by the same rule: the dotted
attribute path to the declaring node plus the local name, or the bare name
on the root. The note's example puts both of the Curta's states on the root;
the spike's per-digit clearing state belongs on the dial, and forcing it to
the root would make the id lie about where the value lives. One rule, the
driver's.

*Departure from the note:* the note says "a declaration next to `Driver` on
a root assembly". Read strictly that would refuse `carriage.result.units.digit`,
which is the shape the spike's clearing events need. The state discipline is
still a property of the ROOT — a tree is clocked when anything in it
declares a `State` — exactly as a tree is driven when anything in it
declares a `Driver`.

**Alternatives considered.** `Memory`, `Register`, `Retained`. `State`
collides with `set_state` and `sim.state`, and the collision is half a
feature (a state IS in `sim.state`) and half a hazard (`set_state` refuses
one). It is kept because it is the pilot's own word for the thing —
"declared state again, but this time in the right place" — and because the
refusal message is the place to resolve the collision, not the name.

### 2. Who writes it

Everything that distinguishes a `State` from a `Driver` is about the writer,
and each refusal is made where its facts exist:

| Attempt | Refused | Where |
| --- | --- | --- |
| `node.set_state(units=3)` | by name, saying a state is written by the machine at an event and naming its committing relation | the delivery `set_state` already performs |
| `Instruction({'units': 3})` | by name | where instruction targets resolve |
| `Turn(dial, units)` / `Button(...)` | by name | class definition, where a control's input is already checked |
| `x.drives(units)` | by name | class definition |
| the same target named twice among ONE relation's targets, by the PATH as written | by name | class definition |
| two relations writing one state AT ONE EVENT | the REQUEST, by name, naming the state, both relations and the landing; nothing is committed | the request, which is where a landing exists |
| a `State` with no committing relation | by name, saying nothing writes it | simulation construction |
| a committing relation no driver can reach — every source a state | by name, saying its event level moves with no declared driver | simulation construction |
| a `State` under `Time(loop=)` or `Time.running()` | by name | the enumeration that binds declared defaults |

A state is settable exactly twice, and both are session setup, not
operation: `Sim(model, state={'units': 3})` and `sim.restore(saved)`. The
direct-operation redesign removed the Curta's register-editor sliders on
purpose and this does not bring them back.

### 3. `.commits(targets, at=, law=)`

```python
    (crank & result & turns & operand & subtract & shift).commits(
        (result, turns), at=strokes, law=registers)

def strokes(sources, targets):
    return lambda crank, result, turns, operand, subtract, shift: \
        floor(crank / 360)

def registers(sources, targets):
    return lambda crank, result, turns, operand, subtract, shift: calculate(
        result, turns, operand, 1, subtract, shift)
```

The verb lives beside `drives` on `CoordinateRef` and on `Coordinates`, so
the `&` group, the flat chaining, the tuple driven side and the
missing-parentheses refusal are all the ones the API already has. The
declaration is a class attribute like a `Relation`: read off the class it
is the declaration, read off an instance it is that instance's record.

**The two factories follow the existing law-factory protocol**, which is
what keeps this out of the rejected `running(r)` shape: each is called
exactly ONCE, at realization, with `(sources, targets)` — the realized
OWNERS, shaped as `_law_argument` already shapes an end (one owner for a
side naming one coordinate, the tuple of owners in written order for a side
naming several) — and returns a callable over the sources' VALUES, one
positional per source in written order. No event object, no `r`, no second
face on a law, no mutable state anywhere in a project's Python.

`law` returns one value for one target, or a sequence of exactly as many
values as there are targets, in written order; a return of the wrong shape
is refused naming the relation, the law, the targets as written and what
came back — `_checked_return`'s rule, reused verbatim.

**Refusals at class definition**, each naming the relation as written and
the class that stated it: a target that is not a `State`; a target named
twice among the targets; a source that is not a `Driver` or a `State` (§4);
`at` or `law` missing; a `ratio=`/`offset=` (a commit is not an affine
pair); a `.repeat()` broadcast on either side (§14).

**"Named twice" is decided by the PATH as written, never by the local
name.** `dial.digit` and `other.digit` are two states of two children of one
class, and the class that declares `digit` is written once however many
children hold it — so the duplicate test is on the reference's own key (the
child path plus the local name), which is also what the message prints. The
Curta has seventeen wheels of one class, and a refusal keyed on the local
name would make that machine inexpressible in a single line of its register.

**Several relations MAY write one state; two of them at ONE EVENT may
not.** *Amendment of 2026-09-17, taken during the orchestrator's review of
the implementation and recorded here rather than silently applied.* The
first draft of this design refused a second committing relation naming a
state already written, at class definition and again across the tree. The
originating Curta is inexpressible under that rule: a register digit is
written at the STROKE END (the arithmetic of the crank turn) and at the
CLEARING REACH (to zero, as the clearing ring sweeps past it) — two
different events, on two different inputs, and one relation states one `at`.
The rule's own rationale is "two answers for one value at one event", and
that rationale bites only when both relations fire at the same event. So:

- a `State` MAY be the target of several committing relations, in one class
  body or across the tree;
- at ONE event — one landing, §5 — at most one of the relations firing there
  may write a given state. If two would, the REQUEST is refused by name,
  naming the state, both relations and the landing, and it commits nothing
  (§9's atomicity);
- the class-definition and construction refusals of a second writer are
  therefore GONE. A target named twice among ONE relation's targets stays a
  refusal, and so does a state nothing writes.

The conflict cannot be decided earlier than the request: whether two levels
land on the same float depends on the bank and on the path, which is exactly
what §5 says about ties, and the same identity test decides both.

### 4. Sources are drivers and states, and nothing else

*Departure from the assignment's summary,* which floats "drivers, states,
ports and time" as the source set. This cycle admits **drivers and states**.

The reason is the whole speed argument. A clocked `Sim` holds a BANK of
drivers and states and NOTHING else; a port or a joint coordinate is a
calculation the untimed enumeration recomputes from that bank on every pose.
To read one inside `at` the solver would have to evaluate it at every point
of the path, which is either a pose per sample (22 ms each on the Curta,
destroying the result) or a compiled program over the whole tree — and
compiling the tree is the running root's job, requiring every relation in it
to be a symbolic expression, which is exactly the generality the clocked
discipline exists to avoid paying for.

The evidence agrees: neither of the spike's two committing relations reads
anything but drivers and states. The stroke commit reads the crank, the
registers and the settings; the clearing commit reads the ring and the
digit.

A port, joint coordinate or derived coordinate named as a source is refused
at class definition, by name, saying to name the drivers and states the port
follows. Recorded as a follow-up, not a gap: a mechanism that genuinely
needs one is a mechanism whose event surface is a function of the pose, and
that is a question worth its own evidence.

### 5. `at` is one jump node, and its level is solved

`at` returns exactly ONE jump node of the vocabulary ADR-107 already
locates: `floor(x)`, `ceil(x)`, `sign(x)`, or a comparison `a ⊙ b`. Anything
else — a sum of two `floor`s, a bare arithmetic expression, `a % b`, which
is not integer-valued — is refused at construction, by name, saying that an
event is one surface family and that two are two committing relations.

*Departure from the note,* which says `at` "returns an integer-valued
expression, built through `floor`, `ceil`, `sign` or comparisons". "Integer
valued" is not a structural property the framework can check, and checking
it by sampling is exactly the search this design refuses. One jump node IS
checkable, it gives the node its LEVEL QUANTITY and its SURFACES for free
(`_Jump`, `_surfaces`), and it costs nothing the corpus needs: both of the
spike's relations are one node.

**The exactness claim, stated precisely.** Along a request's path only one
input moves (§6). The `at` node's level graph is bound with every standing
source substituted as a number and classified by `_shape_of` over the
residual:

- `'affine'` — every surface strictly between the level's two endpoint
  values is SOLVED by one division (`JumpPlan._solved`). Exact.
- `'kinked'` — the piece is cut at the kink's own breakpoints, each solved
  by one division, and each sub-piece solved as above (ADR-123
  `_KinkCuts`). Exact, and the breakpoints are not crossings.
- `None` (curved — a `sin`, a product of two moving operands, a moving
  divisor) — **REFUSED at simulation construction, by name**, naming the
  relation, the driver whose motion curves the level and the primitive,
  and saying that a clocked event is solved and never searched. The
  classification is structural and decidable at construction because only a
  DRIVER can move along a request path; a state is constant between events.

**A relation no driver can reach is refused at construction too.** *Added
2026-09-17, from the orchestrator's review.* The classification above runs
per DRIVER among the sources, so a relation whose sources are all states
compiles with an EMPTY table of levels: nothing can ever move it, it can
never fire, and it is silently inert — which is the one failure mode a
declared machine must not have. It is refused by name at simulation
construction, saying its event level moves with no declared driver, beside
the refusal of a state nothing writes and for the same reason: a declaration
that can never do anything is a mistake in the model, not a machine.

The refusal rather than a search is the design's own claim: the run
bisects a curved level to `1e-12` and says so; a clocked model's whole value
is that its events are exact, and admitting a searched event would make the
claim untrue for a model whose author cannot see which of his `at`
expressions is curved.

**The landing.** A crossing gives a fraction `t*`; the input's value there
is `start + delta·t*`. That float is then walked to the NEAREST
REPRESENTABLE VALUE ON THE FAR SIDE of the surface, by ADR-121's `_far_side`
— an ordinal bisection in float space, no tolerance anywhere. That one float
is used for BOTH the event's reads and the resumption of the remaining path,
so the same event can never fire twice and `floor(crank / 360)` crossing at
`crank = 360` reads the law at exactly `360.0`.

**What "the far side" means, exactly**, because an implementer will
otherwise reach for a comparison. Membership of a float in the far side is
decided by EVALUATING the jump node's branch at that float — `_branch_of`
over the level bound there — and never by comparing the float to the
surface's own value. `_far_side` is already written that way (`branch_at`,
`program.py:1536`), and the three cases a reader should be able to predict
follow from it:

- `floor(crank / 360)` with the crossing solved at `360.0`: the branch at
  `360.0` is already `1`, so `360.0` is ITSELF on the far side and IS the
  landing. Nothing is walked.
- a strict comparison `ring > T` with `T` exactly representable: the branch
  at `T` is still `False`, so the landing is the next float ABOVE `T`.
- `ring >= T` with the same `T`: the branch at `T` is `True`, so `T` itself
  is the landing.

**Ties are identity of the landing, not a tolerance.** Two relations fire at
ONE synchronous event exactly when their far-side landings are the SAME
float. Otherwise they are TWO events, taken in path order, and the second
reads what the first committed. This is a departure from the run, which
merges crossings closer than `_CROSSING_TOLERANCE`, and the reason is that
`_CROSSING_TOLERANCE` is stated in TICK-FRACTION units
(`program.py:105-120`): a merge width proportional to the request's travel
would make one `move('crank', by=3600)` merge events that ten
`move('crank', by=360)` requests keep apart, contradicting both the
exactness claim and the scenario "Ten events in one request equal ten
requests of one". Under a clocked root there is no tick and no fraction to
scale by, every crossing is solved rather than bracketed, and identity of a
float is a decidable question — so no tolerance is needed and none is
introduced. Two surfaces one ulp apart are two events; two surfaces that
land on the same float are one.

### 6. Rising steps fire; the other edge is written by negating the level

A step is RISING when `at`'s value AFTER the crossing is GREATER than
before, read from `_branch_of` at the midpoints of the two adjoining pieces
— the existing branch reading, at points genuinely inside their pieces, with
no epsilon and no direction test.

**Why, and what the alternatives were.** The note assumed both edges fire
and the law neutralises the falling one. The spike MEASURED that false: with
`at = floor(crank / 360)`, no pawl, and the note's own additive law, dragging
the crank backwards from one completed revolution commits a SECOND addition,
9 → **18**. The law does not neutralise; an additive law cannot. Four
options were weighed:

| Option | Rejected because |
| --- | --- |
| both edges fire, the law neutralises | measured false on the originating mechanism |
| `at` steps carry a sign the law receives | every law grows an argument it does not use, and a per-event value handed to a law is the shape the pilot rejected |
| a `direction=` keyword | no mechanism in the corpus needs the falling edge, so the keyword would ship with no test that discriminates it |
| rely on the project's `Bound` and fire both | the bound that makes it unreachable is cycle 2's; until then the default would be measurably wrong |

**Rising-only is fully expressive**, which is what makes the missing keyword
harmless rather than a limit: a mechanism that commits on the other edge
negates its own level. `floor(-crank / 360)` rises as the crank falls and
stands still as it rises. Exact, written in the model, visible to its
reader.

**What the register fixture does dragged backwards**, stated as the
requirement asks: `sim.move('crank', by=-3600)` from any state fires NO
event. The crank moves the whole −3600; `units` and `tens` hold; the pose
follows the crank, because the pose is a function of the crank and the
state. That is also what the real Curta's anti-reversal pawl gives, so the
framework default and the machine's mechanism agree before cycle 2 makes
the bound enforce it.

### 7. A commit is evaluated at ONE POINT, so a jump is a jump

`law`'s expression is inspected exactly as ADR-106 inspects a running law —
applied to one symbolic token per source's qualified id, the graph walked
for raw text and for calls outside `SYMBOLIC_BUILTINS` — with ONE
difference, and it is ADR-109's difference: **a commit law is evaluated at a
point and never integrated, so `floor` means `floor`, `%` means `%`, a
comparison means a comparison, and nothing is subtracted.** There is no jump
plan, no skeleton, no `_only_jumps` refusal: a law made entirely of jumps is
a perfectly good commit (`floor(crank / 360) % 10` is a digit), where under
a run it states arithmetic rather than a mechanism.

That asymmetry is the same one ADR-109 drew between a law and a bound, for
the same reason, and it is why the Curta's `calculate` — integer arithmetic
with `%` and comparisons throughout — is expressible as a commit law and is
not expressible as a running law.

**Why a value evaluated at a point has to be an expression at all.** Nothing
in THIS cycle needs the graph: a commit is one evaluation at one float, and
an opaque Python callable would do it. The shape is checked now because
**cycle 4 publishes `at` and `law` as expression graphs** — a document that
carries a state must carry the surface the viewer locates events on and the
law it commits, or the browser cannot operate the machine at all, and an
expression is the only thing the viewer can execute (ADR-043/ADR-080's
expression DAG, API 16's document 7). Checking the shape at the moment the
relation is declared is what stops a project from writing a commit law the
framework accepts and cycle 4 then cannot publish — the alternative being a
project that works in Python for three cycles and is refused at the browser.
`at`'s structural check (§5) has the same double duty: the solver needs the
level and the surfaces, and cycle 4 needs the graph.

**How a commit is evaluated in Python, and it is not through a graph.**
Both factories return an ordinary Python callable over the sources' values;
the executor CALLS it with the bank's numbers, positionally, in written
order. No graph evaluator, no substitution pass, no symbolic arithmetic at
request time — that is the spike's 26 microseconds per commit, and it is the
whole reason a request costs nothing against a pose. The symbolic inspection
happens ONCE, at realization, on the same callable applied to one token per
source; the graph it produces is kept for the check now and for the document
in cycle 4, and is never walked again to compute a value. This is true of
`at` as it is of `law`: the solver reads `at`'s graph to classify and solve
the level, and evaluates `at`'s CALLABLE at the landing when the event
fires.

### 8. Synchronous reads, and ordered commits

**A commit reads the PRE-EVENT value of every state**, including a state the
same event writes and a state a DIFFERENT relation writes at the same event.
This is what a bank of clocked registers does, and it is the note's own
answer to the question it left open.

That is the SYNCHRONOUS case, and it is only ever about DIFFERENT states:
two relations firing at one landing and writing two different states both
read the bank as it stood before the landing, and their targets take their
results together. Two relations firing at one landing and writing the SAME
state is not a synchronous read but a CONFLICT — two answers for one value
at one event — and it refuses the request (§3). The line between them is the
target's qualified id and nothing else.

The alternative — sequential evaluation in declaration order, each relation
seeing what the previous one wrote — was rejected: it makes declaration
order load-bearing and invisible, so moving one line of a class body would
change the machine's arithmetic. Under the synchronous rule the order of
two relations at one event cannot be observed at all.

**Between events in one request, the order is PATH ORDER.** The solver
takes the earliest crossing on the remaining path, commits it, resumes from
its landing, and repeats; each event reads what the previous left. Several
relations whose far-side landings are the SAME FLOAT are ONE event and
commit together, reading the same pre-event bank; relations landing on
different floats — one ulp apart or a thousand — are separate events in path
order, and the later one reads what the earlier committed (§5).

**`at` may read the state it commits.** The spike's finding 2 is not
optional: the Curta's per-digit clearing threshold is
`start_p + pitch_p * (10 - digit_p)`, a function of the committed digit,
where the note's sketch writes a constant `RACK_END[p]` the measured
geometry does not admit. A source group naming its own target is therefore
legal, and `at` reads the pre-event value exactly as `law` does.

This is ADR-121's self-read, and it is **radically simpler here**, which is
worth recording because it is the whole reason a clocked model is cheap: the
read is constant BETWEEN events, so there is no dependence of the level on a
coordinate that is moving along the path, no two-layer partition, no walk
inside a piece, and no landing of the driven value. The state changes only
AT the event, and the event surface therefore moves only at the event —
which is exactly why the solver re-locates on the remaining path after each
commit (§9) instead of partitioning the whole path once.

### 9. The clocked executor

**Construction.** `Sim(model)` — no `dt`. A `dt` given over a clocked root
is refused by name (there is no cadence; a state moves on requests). A `dt`
omitted over any other root is refused as it is today. `state=` overrides
declared drivers AND states by qualified id, for session setup. Construction
binds the declared defaults, poses the tree once, and holds the bank.

**A request.** `sim.move(input_id, by=travel)` or `to=value`, exactly the
run's vocabulary minus `duration`, on ONE declared driver (§14). It is a
straight path from the bank's value to the requested one. Then:

1. With the current bank, each committing relation's level is bound at the
   standing sources, classified (§5), and its earliest RISING crossing on
   the remaining path located.
2. The earliest over all relations is the next event; relations sharing the
   same far-side landing float are one event, and no tolerance decides it
   (§5).
3. The input takes the far-side landing. Every relation firing there
   evaluates `at`'s and `law`'s callables at that input value and at the
   PRE-EVENT state; the targets take the results together.
4. Resume from the landing with the new bank; repeat.
5. The input takes its requested value, and the tree is bound ONCE, at the
   end.

**The units a commit law speaks, and where rounding happens.** The bank
holds NATIVE values, which is what a driver's declaration means by
`default` and what every law in the framework already reads. A commit law
therefore READS native values and RETURNS native values, and its return is
NOT passed through `Driver.native()`. That is not a convenience: `native()`
converts a DESIGN-unit target into native state by dividing by `scale`
(`driver.py:88-96`), so handing it a value the law already computed in
native units would divide a scaled state by `scale` a SECOND time — a state
declared `scale=10` would lose a factor of ten at every commit. `move`'s
`by=`/`to=` are the one design-unit surface, exactly as they are today, and
`native()` goes on serving them and nothing else.

The one thing that does happen to a committed value is the INTEGER
rounding: a state declaring `dtype=int` counts whole native units, so its
committed value is `round()`ed ONCE, at the commit, nearest — the same rule
`native()` applies for the same reason (a repeated rounding drifts; a single
one does not). A state with a `scale` and no `dtype` is committed exactly as
the law returned it. `9 - 1e-12` committed to an `int` state reads `9`; to a
float state it reads `9 - 1e-12`.

**A request costs no pose.** `at` and `law` read only banked values, so
nothing between step 1 and step 4 touches the tree. That is why the spike
measured 26 microseconds per commit against 22 milliseconds per pose, and it
is the whole speed result.

**Atomicity, and it includes the FINAL POSE.** A request that is refused —
a curved level that escaped the construction check, more than
`_MAX_CROSSINGS` events, a law returning the wrong shape, two relations
writing one state at one event (§3), **or a final pose the tree refuses** —
commits NOTHING: the bank, the tree and the record stand as they were,
exactly as a refused running tick does.

*Amendment of 2026-09-17, from the orchestrator's review.* The pose is the
last step of a request, and a `Bound` the final pose violates raises
`JointRangeError` there (§11). Under the first draft that refusal left the
bank ADVANCED while the tree had never been posed at it, so the next request
would solve its path from a bank the geometry had already rejected. A pose
refusal is a refusal. The executor therefore poses the tree over the WORKING
bank first and only then assigns it: on failure it re-poses the previous
bank and re-raises, so the simulation stands exactly where it stood.
`restore()` is the same shape — a snapshot whose pose fails leaves the old
bank and the old pose.

**The result.** `move` returns a `Request` value object naming the input,
the travel, and the tuple of `Commit` records it fired — each with the
relation as written, the fraction of the path, the input's value at the
event, and the targets with their new values. `record=N` keeps a bounded
ring of the same entries on `sim.commits`; without it the request's own
result is still complete. `sim.state` is the readout, a fresh mapping of the
whole bank by qualified id.

**Refused on a clocked `Sim`,** each by name and each naming the cycle that
may give it meaning: `sim.run`, `sim.at`, `sim.every`, `sim.time`,
`sim.tick`, `sim.rate`, `sim.trigger`, `sim.crossings`, `sim.stops`,
`sim.commands`, `sim.program`. There is no clock and no cadence; an
`Instruction` states a duration and may name several inputs, and a control
issues one.

### 10. Publication is refused, loudly

Cycle 4 owns the document. Until it exists, a tree that declares a `State`
is refused publication by name, naming the states and saying that the
document version carrying them is not defined yet.

The alternative, publishing a version-7 document with the states rendered as
their initial values, was rejected outright: the geometry would be correct
only at the initial state and would silently stop following the machine, and
the version ladder's rule (ADR-110) is that a document whose content a
consumer would animate wrongly takes a version that consumer refuses.

**Where the gate goes, checked against the source rather than assumed.**
`serializer.symbolic_document` is the walk `solid build`, `solid develop`
and `solid export` all pass through (`core/builder.py:653`,
`core/export.py:143`), and it is where the running-root control refusal
lives — but it is NOT universal: `solid snapshot --renderer web` stages its
own baked document from `serialize_node` + `document_body` without entering
the symbolic walk at all (`viewers/browser.py:84-104`), because a capture
bakes one instant and has nothing symbolic to bind. The ONE function all
four document producers pass through is **`serializer.document_body`**,
which its own docstring already calls "one place, so the three producers
that share this walk cannot disagree about what they just emitted". The
refusal therefore goes in `document_body`, with a second raise in
`symbolic_document` only if the implementation finds a producer that binds
symbolically before reaching it — the earlier the message, the better, and
the two cannot disagree because both read the same state table.

**The entry points, by group, each to be verified at apply (tasks 7.1).**

| Refused | How it reaches a document |
| --- | --- |
| `solid build` | `Builder._write_viewer_snapshot_with_inventory` → `symbolic_document` → `document_body` |
| `solid develop` | serves what `solid build` publishes, through the same builder |
| `solid export` | `core/export.py:export_node` → `symbolic_document` → `document_body` |
| `solid snapshot --renderer web` | `viewers/browser.py:BrowserRenderer._stage` → `document_body` (NOT `symbolic_document`) |
| the shop hub's build | spawns `solid build` as a subprocess (`floor/mcp_server.py`), so it is refused through that command's own gate and needs no framework-side special case |

| Untouched | Why |
| --- | --- |
| `render()`, `assemble()`, `build_stls()` | geometry, no document |
| `solid test` | runs the project's tests; no document producer in its path |
| `solid snapshot` with the OpenSCAD renderer | `OPENSCAD_RENDERER.render` off the posed node (`manager/snapshot.py:215`); it builds no document, so it is NOT refused — a clocked model can still be photographed |

*Correction to the briefing:* the shop hub does not call `symbolic_document`
itself. It runs `solid build`. The framework's gate reaches it through that
command and nothing extra is owed.

Rendering, `assemble()`, `build_stls()`, `solid test` and the OpenSCAD
snapshot are untouched, so the scenario tests that are this cycle's proof all
run and a clocked model can still be inspected as a picture.

### 11. A `Bound` violation is still an impossible pose

The spike's finding 4 asks for a violated `Bound` to CLIP a request path,
with the events located on the clipped path — the note's "one thing the
clocked mode borrows from the run". This cycle does NOT do it. A request
ends by posing the tree, and a bound the final pose violates raises
`JointRangeError` exactly as it does today, including ADR-113's
close-of-enumeration judgement for a `Bound` with reads. Unchanged, and
stated so a reader is not left guessing.

What that costs, precisely: a request that would drive a mechanism through a
stop is REFUSED WHOLE and commits nothing — the events on the path are
solved, the final pose is refused, and the bank and the tree stand where
they stood (§9) — rather than stopping where the machine stops and keeping
what it committed on the way. *Restated 2026-09-17: the first draft left the
bank advanced past a refused pose, which was a bug and not this gap.* The
Curta's eight interlocks are all of this shape, so the Curta's clocked model
is not complete until cycle 2.
Cycle 2 is `Bound`-clipping on the request path, and the solver here is
written so the clip is a truncation of `delta` before step 1, not a second
locator.

### 12. Time, and the two axes

The note's honest decomposition is two axes — time base × state discipline —
where today's API ties them. This cycle moves one square of that table and
touches no other:

| time base | none | memory | integrated |
| --- | --- | --- | --- |
| untimed | poses today, unchanged | **this cycle** | — |
| looping (`Time(loop=)`) | the clocks today, unchanged | refused by name | — |
| elapsed (ADR-104) | — | cycle 3 | `Time.running()`, unchanged |

Memory and looping time do not mix: a loop replays from zero, so it replays
every commit and the state climbs across loops. The refusal is taken first,
as the note advises; a looping demo that restores a snapshot at each wrap is
a demand that has not appeared.

**What `self.time` reads under a clocked root, stated because a project will
ask.** A clocked root declares no time base, so there is NO `time` in the
bank — the bank is drivers and states and nothing else (§9), and a request
names a driver, never a clock. When a request ends and the tree is bound,
it is bound exactly as the BUILD PATH poses a driven model outside a
simulation: every driver and every state bound to its value, and `time` left
as the untimed symbolic `$t` through ADR-008's fallback
(`node/assembly.py:608`). A `simulate()` that reads `self.time` under a
clocked root therefore sees precisely what it sees today under an untimed
one — a symbol, not a number — and a clocked model whose geometry depends on
`$t` animates on the viewer's timeline exactly as an untimed model's does.
Nothing about `time` changes, and the change is that nothing changes.

That is also why `time` cannot be a SOURCE of a committing relation in this
cycle: a source is a banked value, and `time` is not banked. Cycle 3
(`Time.elapsed()`) gives a clocked root a clock with a value, banks it, and
only then can an event be located on it. Until then `sim.time` is among the
refused names (§9).

**The meaning of a `State` under `Time.running()` is DEFINED and not
implemented.** Under a run a value committed at an event is a self-read law
whose value changes only through a switch — exactly what ADR-121 admitted
and exactly how the operating Curta's wheels already work — so a
`State` under a running root compiles to that self-read switch law and
becomes one retained coordinate among all the others. It buys no speed: every
other coordinate is still integrated at the cadence. The one reason to fix
the meaning now is PORTABILITY — a project writes "this register is a state
committed at the stroke end" once and has it mean the same under both roots,
so a machine proven running can be shipped clocked without rewriting its
state. This goes in the ADR as a Consequence (§15), and construction refuses
the combination by name until a project needs it.

### 13. The spike's seven points, answered

| Spike point | Answered by |
| --- | --- |
| 1. Direction on an event is a real decision | §6 — rising only, with the measurement that rejects the note's assumption and the negation idiom that keeps it expressive |
| 2. `at` may read the state it commits | §8 — legal, pre-event, and simpler than ADR-121's walk because the read is constant between events |
| 3. The pose is fed by the state and only the state | §9 — the bank is drivers and states, the pose is the existing untimed enumeration over it, and a request touches the tree once |
| 4. A violated `Bound` must clip a request path | §11 — NOT this cycle, named, with what it costs |
| 5. Interlocks are project-owned `Bound`s | nothing needed; no new framework idea, and §11 names what cycle 2 owes them |
| 6. No fold in the first cycle | §3 — `at` is required, a `commits` without it refused by name |
| 7. A state is not a control | §2 — the whole refusal table |
| 8. A register digit is written at TWO events | §3 — several relations may write one state, and only two firing at ONE landing conflict |

Point 8 is not in the spike's own list: it is the orchestrator's review
finding of 2026-09-17, read off the spike's own two relations. The spike's
stroke commit and its clearing commit BOTH write the register digits, at the
stroke end and at the clearing reach; a one-writer rule would have made the
machine the cycle exists for inexpressible, and the amendment in §3 is what
admits it.

The spike's own gaps in the OPERATING model — a mid-stroke reversing lift
and a mid-stroke carriage lift the machine forbids, and the open red
`test_running_ratchet.py` — are the Curta project's work and appear nowhere
in these specs.

### 14. Deliberate narrowings, and why each is cheap to lift

- **One driver per request.** The exactness classification of §5 is stated
  against ONE moving input; the underlying machinery integrates a path in a
  joint source space perfectly well, so widening later is a change to the
  check and not to the solver. Nothing in the corpus needs two.
- **No broadcast `commits`.** A `.repeat()` child that owns a banked value
  is already refused under a running root because `drivers-0` is not a legal
  id segment; a repeated `State` has the same problem and it is that
  problem, not this one. The Curta's seventeen clearing relations are
  seventeen written lines until it is fixed.
- **No `Instruction` and no control.** Both name a duration or issue a
  request through the run's command surface, and a clocked root has neither.
- **No `%`-rooted or compound `at`.** §5.

### 15. The ADR plan

ONE NODE ADR, candidate **ADR-125** — "A state is a driver the machine
writes, committed at an event" (ADR-124 is the highest accepted). It is
extracted AFTER implementation, as the framework-change discipline requires,
and is not written now. It will record:

- the declaration and the writer discipline (§1, §2);
- the verb, the two factories and the one-jump-node `at` (§3, §5);
- rising-only firing with the spike's 9 → 18 measurement as its driver (§6);
- a commit evaluated at a point, so jumps are plain (§7);
- synchronous pre-event reads and path-ordered commits (§8), with SEVERAL
  writers admitted for one state and two of them at ONE landing refused as
  the request's own conflict (§3), the Curta's stroke-and-clearing digit as
  the evidence;
- atomicity including the FINAL POSE: a request whose pose is refused
  commits nothing (§9, §11);
- ties decided by IDENTITY of the far-side landing rather than by
  `_CROSSING_TOLERANCE`, and why a tick-fraction tolerance cannot be carried
  onto a request path (§5);
- native units in and out of a commit law, with the single `int` rounding at
  the commit and no second `native()` conversion (§9);
- the solver as a CONSUMER of ADR-107, ADR-121 and ADR-123, adding no
  locator and no tolerance (§5, §9);

and, as CONSEQUENCES and explicitly not implemented: the meaning of a
`State` under `Time.running()` as an ADR-121 self-read switch (§12), and
that `Time.running()` itself is untouched.

No second ADR. The publication refusal (§10) is a gate, not an architecture
decision, and the document's own decision belongs to cycle 4.

### 16. Zero behaviour change, as a requirement with a test

A tree that declares no `State` must be unchanged in behaviour, in published
bytes and in cost. The implementation makes that structural rather than
hoped for:

- states are collected in the walk `qualified_declarations` ALREADY makes
  (`drive_tree`'s `visit` exists for exactly this), so no tree pass is
  added;
- every clocked code path is entered only when that collection is non-empty,
  as the running paths are entered only under `Time.running()`;
- `solid_node.simulation`'s exports stay lazy, so a project that names no
  `State` imports no new module.

Planned proof in §17.

## Risks / Trade-offs

- **Two models of one machine drift.** The note names the risk and the
  mitigation: the clocked model's commit law must agree with the running
  model's readout at every stroke end across one shared scenario corpus.
  That is the Curta's own acceptance work, not this cycle's, and this cycle
  does not make keeping two models a default.
- **A clocked project cannot be published or viewed until cycles 4–6.** The
  refusal in §10 is the honest form of that, and it is loud.
- **A clocked project cannot be operated through its interlocks until cycle
  2.** §11.
- **The refusal of a curved `at`** will reject a model somebody writes. The
  message must say which driver curves which level and what shape is
  admitted; the alternative — searching it — would make the exactness claim
  untrue in a way no message could repair.
- **`State` shadows `set_state`'s noun.** Mitigated by a refusal message
  that says what to do instead, not by a different name (§1).

## Open Questions

Each is recorded rather than silently decided; none blocks this cycle.

1. **Does a clocked root ever want an instruction?** A declared move with no
   duration, targeting one input, is a coherent idea and is what a browser
   panel will want in cycle 6. Left out here because its shape depends on
   what cycle 6 needs from it.
2. **Should `sim.move` report an `admitted` travel?** It is always the full
   travel in this cycle. Cycle 2 makes it meaningful, and the `Request`
   object is shaped so the field can arrive without changing the others.
3. **`phase` as a derived coordinate.** The note asks whether
   `crank - 360 * floor(crank / 360)` is spelled as a derived coordinate,
   which today admits only linear formulas, or stays inside the laws. This
   cycle leaves it inside the laws and proposes nothing.
4. **A fold-commit.** The spike measured that the Curta does not need one
   and that the only state it would close is one the booklet forbids. Its
   shape is recorded there for the project that does need it.

## Planned proof

### 17. Tests, per requirement

Every test below is RED FIRST. Both fixtures are geometry-free — no CAD
build, no `meshes = True` — and every run uses
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one job at a time
(`/home/asa/devel` is a virtiofs mount that exhausts file descriptors under
parallel load).

- **`tests/clocked_project/` — the register fixture.** A two-digit counter
  with carry: a `crank` driver, `units` and `tens` states, one committing
  relation `(crank & units & tens).commits((units, tens), at=floor(crank/360),
  law=((units + 1) % 10, (tens + (units == 9)) % 10))`, and two dials posed
  from the states by ordinary `drives` laws. Expected values are computed BY
  HAND in each test, never by calling the law. It covers: one event per
  request; ten events in ONE request giving the same bank as ten requests of
  one (path independence); the carry; the pose following the state and the
  crank between events; a backwards request firing nothing and moving the
  crank (§6); `set_state` refused by name; `state=` and
  `snapshot`/`restore`/`reset`; the `Request` result's `Commit` entries in
  path order with their fractions and input values.
- **`tests/clocked_project/` — the clearing fixture.** A root carrying a
  `ring` driver and a `dial` CHILD that declares `digit = State(...)`, with
  the committing relation stated on the ROOT and naming its target through
  the path `dial.digit` — the Curta's own shape, where the state belongs to
  the part that holds the value and the relation belongs to the assembly that
  can see both ends. `at` READS that digit:
  `at = ring >= START + PITCH * (10 - dial.digit)`,
  `law = dial.digit * (ring < START + PITCH * (10 - dial.digit))`.
  Curta-shaped and tiny. It covers §8's pre-event reading, a comparison as
  `at`, a target named through a path, the event surface moving after a
  commit, a second sweep firing nothing on a cleared dial, and a reversed
  sweep firing nothing.
- **`tests/clocked_project/` — the register fixture, the Curta's own
  shape** (added 2026-09-17 by the §3 amendment). A `crank`, a `ring`, an
  `operand`, and THREE `Wheel` children of ONE class each declaring `digit`:
  one stroke relation writing all three digits, and one clearing relation
  per wheel reading its own digit at `START + 100*p + PITCH*(10 - digit)`.
  It is the fixture no one-writer rule admits — three states of one class
  written both by the stroke and by their own clearing reach — and it
  covers: strokes adding with carry; a partial sweep clearing only the
  wheels it reaches; a reversed sweep un-clearing nothing; a second sweep
  firing nothing on a cleared wheel; and strokes after clearing continuing
  from zero. Beside it, a CONFLICT fixture: two relations on one input whose
  levels land on the same float and both write one state, whose request is
  refused by name and leaves `sim.state` unchanged.
- **Exactness.** A crossing at an affine level lands on the far-side float:
  `floor(crank / 360)` crossing at `crank = 360` reads `law` at exactly
  `360.0`, and resuming cannot re-fire it. A KINKED level
  (`at = floor(max(crank, 0) / 360)`) is solved at its breakpoint and not
  searched, asserted against a hand-computed fraction. The boundary rule of
  §5 is asserted directly: `ring > T` lands on `math.nextafter(T, inf)` and
  `ring >= T` lands on `T`, for a `T` the fixture chooses representable.
- **Ties are identity, not width.** Two relations whose comparison surfaces
  differ by ONE ULP fire as TWO events in path order, the second reading the
  first's commit; two whose surfaces coincide fire as ONE synchronous event.
  The same pair asserted under a long request (`by=3600`) and under ten short
  ones (`by=360`) gives the same events, which is the scenario a
  travel-scaled tolerance would break.
- **Units.** A state declaring `scale=10` commits the value its law returned,
  unrescaled; an `int` state whose law returns `9 - 1e-12` reads `9`; a float
  state's law returning `9 - 1e-12` reads `9 - 1e-12`.
- **`time` is untouched.** A clocked fixture whose `simulate()` reads
  `self.time` poses after a request with `$t` symbolic, and its rendered
  expression is identical to the same fixture's with its states replaced by
  drivers of the same values.
- **Refusals**, one test each, asserting the message names the relation and
  the offending thing: a non-`State` target; a target named twice among ONE
  relation's targets, by the path; `x.drives(state)`; a state with no
  commit; a relation no driver can reach; a port source; a curved `at`
  (`sin(crank)`); a compound `at` (`floor(a) + floor(b)`); a `commits`
  with no `at`; `at` or `law` returning raw text or calling outside
  `SYMBOLIC_BUILTINS`; a law returning the wrong number of values; a `State`
  under `Time(loop=)`; a `State` under `Time.running()`; `Sim(node)` with no
  state; `Sim(node, dt)` over a clocked root; an instruction and a control
  targeting a state; each refused member of the cadence surface.
- **Several writers, and the one-event conflict** (§3). Two relations on two
  states of two children of ONE class are ADMITTED, in one body and across
  the tree; two relations writing one state at two DIFFERENT events are
  admitted and each fires at its own; two relations writing one state at the
  SAME landing refuse the request by name, and the bank, the tree and the
  record stand as they were.
- **Publication, entry point by entry point** (§10): `solid build`,
  `solid export`, `solid develop`'s publish and `solid snapshot
  --renderer web` each refused naming the states, with no document written
  and no partial output left behind; and `render()`, `assemble()`,
  `build_stls()`, `solid test` and `solid snapshot` with the OpenSCAD
  renderer each succeeding on the same clocked fixture. The browser-renderer
  case is the one that proves the gate is in `document_body` and not only in
  `symbolic_document`.
- **Atomicity.** A request whose law raises on the third event leaves the
  bank, the tree and the record exactly as they were — and so does a request
  whose FINAL POSE violates a joint `range`: the `JointRangeError` is
  raised, the bank has not moved, and the tree is still posed where it was
  (§9's amendment). `restore()` over a snapshot whose pose fails is asserted
  the same way.
- **Zero behaviour change.** The whole existing suite green; a byte-identical
  document assertion for an existing published fixture; an assertion that a
  stateless tree never enters a clocked code path (a counter on the collector,
  asserted zero); and the existing running fixtures' per-tick cost within
  their recorded envelope.

### 18. Measurement plan

Measured on the register and clearing fixtures ONLY, reported as their own
numbers and compared to nothing:

- seconds per request with no event;
- seconds per event (the commit alone), against the spike's 26 microseconds
  through `calculate` as an order-of-magnitude sanity reading, not a claim;
- seconds per pose of the fixture, to show the ratio the design rests on;
- the cost of a stateless fixture's pose before and after the change.

**Not claimed in this cycle:** anything about the Curta. The register
fixture's cost per request against the running Curta's cost per tick is not
a comparison this cycle is entitled to make — the Curta's clocked model is
project work in the project's own repository, and the spike's factor of 35
is that project's measurement, cited as the requirement's evidence and not
reproduced here.
