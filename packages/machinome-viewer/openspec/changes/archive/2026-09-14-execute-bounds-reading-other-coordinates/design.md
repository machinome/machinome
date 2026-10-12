## Context

The viewer's worker already executes a version 5 document's compiled
program: `src/run/program.ts` reads and refuses it, `src/run/run.ts` is
`solid_node/simulation/run.py`'s `class Run` reproduced function for
function, and `src/run/running-corpus.test.ts` replays the producer's
committed corpus step for step (ADR-045, ADR-047). Declared bounds are
physical stops there today, including a bound stated as an expression
over the bounded coordinate's OWN id: `Run.boundsNow()` evaluates each
span once per tick from the committed bank, `reachedBounds` compares the
stretch's committed value against those numbers, `locate` solves or
searches the fraction, the coordinate is committed AT its bound, and
`groupOf`/`pushes` stop every input whose own admission moves it.

solid-node's ADR-113 widens a bound to READ OTHER COORDINATES and gives
that reading a running meaning: a CONSTRAINT, the own coordinate frozen
at the tick's committed value and the reads taken along the path over
the bound's sub-program, detected and localized by sampling INSIDE the
stretch, stopping every input that carries the level outward — the
inputs moving what it reads included, so a dependency never overruns a
standing coordinate. The framework's cycle is complete and archived
(`2026-09-14-bounds-read-other-coordinates`, ADR-113), its corpus
regenerated with a fourteenth machine, `Captured`, and its design §8
names this cycle as the one that must follow.

What the document carries is unchanged in shape: a span side is still
`null`, a number, or `{"expression": <text>}`. What changed is that the
expression's free names may now be other bank ids. The shipped worker's
check on a span allows the own id alone, so the pin tumbler lock's
document is refused by name. Removing that refusal is not the work;
EXECUTING the document is, and the refusal must stay for everything the
viewer still cannot run.

Two facts of the lock's own published document shape this design. Its
`plug.turn` high bound is `(((((90.0 * _b10) * _b13) * _b16) * _b19) *
_b22)` — every read reached through the document's BINDINGS table, none
of them a free name of the text itself — and its expression never names
`plug.turn` at all. Its `plug.key.insert` low bound is
`(-60.0 - (-60.0 * (abs(plug.turn) > 0)))`, which reads one coordinate
directly.

## Goals / Non-Goals

**Goals:**

- Reproduce ADR-113's running semantics function for function, so the
  two runtimes stay ONE algorithm and the regenerated corpus replays
  green — exactly for discrete state, within
  `program.limits.agreement` for floats.
- Refuse, by name and at load, every bound this viewer still cannot
  execute, naming what it may read.
- Leave a self-only bound untouched: same meaning, same code path, same
  cost, and the Pascaline acceptance unchanged to the digit.
- Mount and run the pin tumbler lock's own published document in a real
  browser, driven by its own declared instructions.

**Non-Goals:**

- A document version change, a span shape change, or a widget API
  version bump. Nothing public moves.
- Any part of the framework's DECLARATION side: `Bound`, `reads=`, the
  class-definition checks, the untimed judgement at the enumeration's
  close. None of it reaches a document.
- A general constraint solver, and any tolerance the document does not
  publish. The four limits stay `crossing_tolerance`, `subdivisions`,
  `bisection_rounds` and `agreement`.
- The performance follow-ups the framework recorded in its own
  `workflow/warts.md` (`f(start)` once per stretch per edge; one
  sampling for the two sides of one coordinate). Measured here, not
  taken here.

## Decisions

### D1. A constraint is DERIVED at load, in `program.ts`

`loadProgram` gains a `constraints` table, `Map<string, Constraint>`
keyed by `` `${identifier}:${side}` ``, each entry carrying
`{ identifier, side, expression, reads, edges, candidates }` — the
mirror of `simulation/program.py`'s `Constraint` dataclass
(`program.py:161`). `reads` is derived by D2; `edges` is
`Program._sub_program` reproduced (walk `program.edges` in REVERSE,
skipping `check` edges, keeping any edge that gives a needed key and
adding its `needs`, then reverse again); `candidates` is the sorted
union of `program.sources` over the bounded coordinate and every read.

*Chosen over publishing them.* The framework decided (design §7,
ADR-110) that the sub-program and the candidates are projections of
`edges` and `sources` with no decision in them, so the document carries
neither. A viewer that asked for them would be asking for a document
change the producer has already refused, and would let the two runtimes
disagree about a derivation neither of them decides.

*Rejected: deriving them lazily in `Run`, on the first tick that needs
one.* A read that is not a bank id would then surface as a failed tick
on a rendered page rather than as a refusal at load, which the ratified
requirement "A program the viewer cannot execute is refused by name"
forbids: nothing is rendered from a document that cannot be executed.

*Rejected: deriving in `Run`'s constructor.* `Engine.load` builds the
program and the run together, so it costs the same; but `program.ts`
already holds every other compile-time projection (`determiner`,
`placeholders`, `declaredNames`), and the refusal machinery with its
quoted-document message lives there.

### D2. The reads are the bindings CLOSURE of the free names, minus the own id

`reads = sort(table.closure(freeVariables(expression)) \ {identifier})`
— exactly the set `program.ts`'s existing `namesOf` computes for the
free-name check, which is why this is one line and not a second reader.

*This is load-bearing, not a detail.* The lock's `plug.turn` bound names
`_b10`, `_b13`, `_b16`, `_b19`, `_b22` and nothing else. Its RAW free
names contain no coordinate at all; the closure contains
`plug.p1.lift … plug.p5.lift`. A viewer deriving reads from
`freeVariables` alone would find no reads, take the static-reads
shortcut on every tick, evaluate the bound from five standing lifts and
run a lock that turns while its pins move — silently, and only for
documents that share a subexpression. The closure is the only correct
source.

*Order.* The framework's `Constraint.reads` is the DECLARED order; a set
has none. Order never reaches a number: `reads` is used for an
all-quantified comparison, for building an evaluation scope, as a key
set for the sub-program, and in a union that is sorted. We sort, so the
derivation is deterministic for a given document.

*Why the own id is subtracted and not required.* The framework refuses a
read that names the bounded coordinate itself, and refuses a declared
read the expression never uses, so the published free names minus the
own id ARE the declared reads. The own id may be absent — the lock's
plug bound never names `plug.turn` — so the test is containment, never
equality.

### D3. What a bound may read, and the message when it may not

The span check in `loadProgram` widens from `new Set([id])` to
`{id} ∪ bank ids`, where the bank is `program.coordinates`' keys. An
intermediate, the clock, a placeholder or an unknown name is still
refused.

The message keeps the shape the shipped one has — what is wrong, what it
may read, the expression quoted, the document named — and gains one
sentence when the offending name IS a published intermediate, carrying
the framework's own advice:

```text
<sourceUrl> declares document version 5 and the bound declared on
"plug.turn" names "plug.core.angle", which it may not read: that name is
a published computed value, not a coordinate of the bank, and a bound
reads the STATE — read the joint the port follows. It may read:
plug.turn and any of the program's 16 coordinates. Quoting the
expression: "…". The document is malformed: refusing it rather than
running a machine this viewer cannot execute.
```

*Rejected: listing every bank id in the message, as the existing `check`
helper does.* On the lock that is sixteen qualified ids in one sentence
for a document whose author wrote one wrong name; the count plus the own
id says as much and stays readable. The intermediates ARE listed when
the name is one of them, because that is the case where the author
needs to know which joint to name instead.

*Rejected: admitting intermediates.* The sub-program pass recomputes
them anyway, so it would "work". The framework refuses a read of a plain
port at construction — a port is a calculation the enumeration recomputes
from the state, not the state — and a viewer that ran what the producer
refuses to publish would be a second, laxer semantics wearing the same
corpus.

### D4. The sub-program pass lives in `run.ts` and reuses `edges.ts`

`Run.constraintLevel(constraint, held, values, admissions, t, own)`
mirrors `run.py:793`'s `_constraint_level`: a FRESH delta map from
`this.deltasOf(scale(admissions, t))`, then, for each edge of
`constraint.edges` in order, `edgeIncrements(this.program, edge, values,
deltas, null, 0)` written back into it — the same call `pushes()`
already makes, so a law that jumps takes its published plan over the
truncated path exactly as the segment later will. The scope is
`{ [identifier]: own }` plus `held[read] + deltas[read]` per read, and
the level is `value − bound` for a high side, `bound − value` for a low
one, with `value = held[identifier] + deltas[identifier]`.

*Chosen over a helper in `edges.ts`.* `edges.ts` is per-edge arithmetic;
`Run` owns the delta map, the bank and the tick. The DERIVATION of the
sub-program belongs to `program.ts` (compile time, D1) and the PASS over
it belongs to `run.ts` (tick time), which is exactly how the framework
splits `Program._sub_program` from `Run._constraint_level`.

*Chosen over reusing `Run.pass()`.* `pass` mutates the tick's own delta
map, records crossings and raises on a check disagreement. The framework
says so in as many words: "on a FRESH delta map — never `_pass`'s, which
mutates and raises". A sample must cost nothing and record nothing.

*Not memoized.* A cache keyed by `t` would pay only on the bisection,
where every `t` is new. The framework's own follow-ups
(`f(start)` once per stretch per edge) are recorded upstream and are not
taken here, so that the two runtimes stay the same arithmetic.

### D5. The static-reads shortcut dispatches into the EXISTING stop path

`boundsNow()` stops returning numbers only: a side that is a constraint
returns the `Constraint` object, mirroring `run.py:1087`'s `_bounds`,
which substitutes the compiled `Constraint` for that side. `Reached`
becomes `[identifier, side, number | Constraint, number | null]` — the
fourth element the fraction already located, `null` for everything else
— and `eventOf` uses it instead of calling `locate`.

`reachedBounds` then reproduces `run.py:674`'s `_reached` branch for
branch:

- no read moves and the coordinate does not move → nothing;
- no read moves and the coordinate moves → the bound is the NUMBER its
  expression gives at the tick's committed own value and the reads'
  START-OF-STRETCH values, and the entry is pushed as an ordinary
  numeric `Reached`. From there nothing is new: `locate` solves or
  searches, the commit snaps AT the bound, `groupOf`/`pushes` choose the
  group. The plug turning with its pins standing still pays ONE
  evaluation;
- a read moves → `constraintReached` samples and localizes (D6), and the
  entry carries the `Constraint` and its fraction;
- the plain numeric low/high comparison runs afterwards with a
  constraint side treated as `null`, so no side is judged twice.

*Chosen over a second detection pass for constraints.* One list keeps
one ordering: the earliest `t*` first, everything within
`crossing_tolerance` of it one event, the union of the groups. Two lists
would need a rule for how they interleave, and that rule is exactly the
one `eventOf` already is.

### D6. Detection, localization, group and commit, mirrored exactly

- `constraintReached` (`_constraint_reached`): examined only when the
  bounded coordinate or a read has a nonzero increment over the stretch;
  otherwise `null`, and a coordinate standing outside is free.
- `searchedConstraint` (`_searched_constraint`): `start = level(0)`;
  `outward(h) = h > 0 && h > start`; samples `k/subdivisions` for
  `k = 1 … subdivisions`, stopping at the first outward sample; brackets
  `[(k−1)/s, k/s]` and bisects while `high − low > crossingTolerance`,
  at most `bisectionRounds` rounds; returns `low` — the INSIDE end. A
  first sample that is outward with `start > 0` yields `0`.
- `constraintGroup` (`_constraint_group`): over `constraint.candidates`,
  each with a nonzero admission, `level(1) − level(0)` computed with
  that candidate's admission ALONE. `held` is the stretch's start bank
  and `admissions` the stretch's `scaled` — not the segment's.
- The commit: for a constraint, NO snap; `value` is the bound evaluated
  at the committed state with the own coordinate still frozen at
  `this.bank`; the `Stop` record is `{coordinate, bound: side, value, t:
  boundary, inputs: sorted(group)}`.
- The invariant: `assertInside` runs in a SECOND loop over the event,
  after every entry's group and record, because a numeric snap on
  another entry of the same event mutates `committed` and the assertion
  must see the state the segment actually commits. `run.py:583-585`
  splits the loops for this reason and the viewer must too. A level
  above zero throws `StopInvariantError`, which the existing `catch`
  already turns into a tick that commits nothing.

*`own` is `this.bank[identifier]`, never `staged[identifier]`.* The
framework reads the TICK's committed bank in `_searched_constraint`,
`_constraint_bound` and `_constraint_group`, which is what makes a
ratchet's tooth the tooth it started the tick on across every segment.

### D7. The corpus, and the width guard

`src/running-corpus.json` is replaced by the producer's regenerated
`tests/running-corpus.json` BYTE FOR BYTE: 14 scenarios over 12
machines, 276 ticks, tolerance `{"float": 1e-9}`, the new machine
`Captured` (`dt` 0.05, 16 ticks, a script of two moves, a snapshot, a
third move and a restore). Nothing here edits it and nothing here
regenerates it.

`uncoveredFeatures` in `running-corpus.test.ts` gains the producer's two
new entries, computed the producer's way
(`tools/generate_running_corpus.py:285-331`):

- `'a bound reading another coordinate'` — a span side that is an
  object whose free names, CLOSED OVER THE FIXTURE'S OWN BINDINGS,
  contain a bank id other than the span's own key. The guard therefore
  needs a closure of its own over `entry.document.bindings`; the
  producer's `free_names(expression, bindings)` is the model.
- `'a stop reached by the motion of what a bound reads'` — a recorded
  stop whose coordinate holds the SAME value in the previous tick's bank
  (or the published `initial`, on tick one) as in its own.

*Rejected: importing `loadProgram`'s closure into the guard.* The guard
reads the FIXTURE and nothing else, on purpose: it must be red when a
narrowed corpus is copied in even if the engine is broken, and green
without the engine being asked anything.

### D8. The acceptance: the lock's own document, in a real page

`tests/fixtures/lock/viewer.json` is
`projects/Locks/Pin_tumbler_lock/_build/viewer.json`, verbatim — version
5, two drivers (`insertion` mm, `rotation` deg), six instructions,
sixteen coordinates, fourteen edges, twenty-three bindings, eleven
flexible pieces. The fifteen model paths it names hold the same 684-byte
stand-in unit cube `tests/fixtures/pascaline` already uses, and a
`README.md` says which half is verbatim and which is a stand-in. This is
the `pascaline` fixture's own precedent, and it keeps the fixture at
tens of kilobytes instead of 3.2 MB.

The acceptance is a Playwright test in the Python suite, beside
`tests/test_running_document.py`'s (`needs_playwright`, `needs_bundle`,
`serve_directory`, `page.evaluate` over the mounted handle), because
that is where every other "a real machine in a real browser" proof in
this repository lives and because the refusal this cycle removes fires
on LOAD in a page. It drives the document by its own declared
instructions and asserts the mechanism, not a pixel.

*Rejected: a vitest acceptance in node, like `acceptance.test.ts`.* That
proves the engine, and the engine is already proved by the corpus. What
is unproved is that the lock's document MOUNTS — the thing that fails
today is `loadProgram` inside the worker inside a page.

*Also added, cheaply:* a vitest case that loads the same fixture through
`Engine.load` and asserts the derived constraint table (five reads on
`plug.turn`'s high side through the bindings, one on
`plug.key.insert`'s low side, seven sub-program edges, both inputs as
candidates), because a browser failure is a poor place to learn that a
closure was wrong.

### D9. What this costs, and what the worker measures

The framework measured (ADR-113 Consequences), on CPython: the
lock-shaped `Gate` fixture at a four-edge sub-program — a quiet tick
**0.36 ms / 8 graph evaluations**, an active tick **5.4 ms / 528**, a
blocking tick **3.3 ms / 328**; and the lock itself, whose plug bound
reads five `piecewise` laws of 8–26 knots — **2.9 ms** idle, **4.7 ms**
turning the seated plug, **45 ms** advancing the key (**193 ms** before
the static-reads shortcut). Each sample costs about one pass over the
sub-program.

`src/run/cost.test.ts` prints ticks/s and asserts floors an order of
magnitude below what the bench measures. It gains three measurements,
each printed and each floored the same way:

1. the corpus's `Captured` machine, advanced through its blocking ticks
   — a constraint that SAMPLES;
2. the lock fixture idle at its rest bank — a constraint that evaluates
   nothing, which must cost what a program with no constraint costs;
3. the lock fixture advancing the key — the worst case, where five
   bounds sample over a seven-edge sub-program.

And one regression floor the other way: `Train`'s existing measurement
must not move, because a machine declaring no such bound pays nothing.

The number that MATTERS is (3) against the run's own cadence: at the
default step size `1/240 s` a tick must cost under about 4 ms for the
lock to advance its key at real time. The framework's 45 ms is CPython
evaluating a graph; the worker's is a hash-consed DAG (ADR-043) and
should be far cheaper, but it is unmeasured until this cycle measures
it. The measurement is recorded in evidence either way, and a shortfall
is reported to the pilot as a finding — never mended by widening a
tolerance, coarsening the step size, or skipping a sample.

## Risks / Trade-offs

- **[The lock does not advance its key at real time in the browser.]**
  → Measure it (D9) before the acceptance is written, record the number,
  and report a shortfall as a finding with the framework's own recorded
  follow-ups named (`f(start)` once per stretch per edge; one sampling
  for the two sides of one coordinate). The acceptance drives the
  machine by instructions and asserts the mechanism, so a slow tick
  makes it take longer, never wrong.
- **[The closure derivation is wrong and the lock runs a bound over
  standing lifts.]** → This fails SILENTLY, which is the worst shape a
  bug can have here. Mitigated three ways: the derived table is asserted
  directly against the lock fixture (D8); the corpus's `Captured`
  machine has NO bindings at all, so it cannot catch this alone and is
  not relied on to; and a red-first test loads a hand-written document
  whose bound reads a coordinate ONLY through a binding.
- **[A mirroring drift the corpus cannot see.]** The corpus's `Captured`
  machine exercises one constraint shape. The framework's
  `test_running_stops.py` pins six more — the plug blocked at `t = 0`,
  insertion and turning in one tick, the withdrawal at `t ≈ 0.41`, the
  declared capture, the plug returned and the key withdrawn together,
  and the pawl at 0.3 and 0.5. → Every one of them is reproduced as a
  `bench()` document in `run.test.ts` against the framework's own
  numbers (tasks 4).
- **[The two-loop commit order is missed.]** A single loop passes every
  test in which one event carries one stop, which is all of them until
  a numeric snap and a constraint land within `crossing_tolerance` of
  each other. → Stated in D6, given its own task, and given a test in
  which one event carries both.
- **[A larger refusal surface.]** Widening the span check admits every
  bank id, so a genuinely malformed bound that happens to name a
  coordinate now loads and fails later. → It cannot fail later: an
  expression over bank ids is exactly what the engine executes. The one
  thing that gets quieter is a producer bug in which a span names the
  wrong coordinate, and no consumer can see that.
