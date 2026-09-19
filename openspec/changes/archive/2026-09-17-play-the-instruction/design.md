## Context

Four cycles built the clocked machine: a bank of drivers and states that moves
on requests (`declare-the-state`, ADR-125), a declared range that STOPS a
request on its path (`a-bound-stops-the-request`, ADR-126), a clock that is a
banked value (`time-without-running`, ADR-127) and a published compiled
machine at document version 8 (`publish-the-clocked-machine`, ADR-128). The
fifth and sixth gave the viewer an executor and a clock, so a version 8
document runs in a browser (viewer ADR-062, ADR-063, API 18).

The originating project has the machine and cannot show it working.
`projects/Calculators/Curta-Type-I-3x` (branch `direct-operation`, HEAD
`9fb725f`) models one Curta three ways. `fast_curta` is closed-form, has seven
instructions with durations and ANIMATES; `operating_curta` runs on
`Time.running()` and costs a tick per frame; `clocked_curta`
(`simulation/clocked.py:ClockedCurta`) holds state, reproduces the operating
model's registers at every stroke end, and completes a stroke in 0.07875 s in
Python and 36.95 ms in Chromium
(`simulation/docs/clocked-curta-2026-09-17.md`, "Timing"). It declares one
instruction, `'Turn crank': Instruction(by={'crank_rotation': 360},
duration=2)` (line 95), and that instruction does nothing at all: ADR-128
§"Instructions are published in the version 5 shape, with no meaning"
publishes the table and refuses `trigger` by name
(`solid_node/simulation/sim.py:523`). The project's record calls it "disabled
metadata under the current clocked contract".

The pilot's requirement, verbatim: *"I need it to be animated fast between
states with smooth transition just like the fast_curta, but holding state."*

The gap is not a missing capability in the machine. The machine computes the
whole stroke, with every carry landed in path order, in one request; what is
missing is that nothing turns "the maker pressed Turn crank" into that
request, and nothing the request returns says where the crank STARTED, so a
consumer cannot draw the stroke between its two ends. This cycle is those two
things and deliberately nothing more.

The decision about HOW a transition is drawn is the pilot's and is already
taken. A request is ONE state transition, computed once and exactly. A
consumer draws it over the instruction's `duration` by interpolating the moved
input from `origin` to `end` and posing the tree from the bank as it stood
after every commit already reached; the machine does no work per frame, and
the framework never learns what a frame is.

## Goals / Non-Goals

### Goals

1. `sim.trigger(name)` on a clocked `Sim` makes the request the instruction
   states, and returns it.
2. A `Request` carries everything a consumer needs to DRAW the transition it
   describes, with no arithmetic, no unit conversion and no re-derivation of a
   float the machine already stood at.
3. Every instruction a version 8 document carries is one a consumer can play.
4. The corpus pins the meaning, so the viewer's replay inherits it exactly.
5. The document does not change: no field, no key, no version, no producer.

### Non-Goals

- **The viewer's playback.** `solid-node-viewer`'s own repository and cycle.
- **Any frame, tick, cadence or clock in the framework.**
- **Per-frame slicing of an instruction** (§10).
- **Sequencing several inputs from one instruction** (§2).
- **Any change to `Time.elapsed()`, `Time.running()`, the running instruction
  path, document versions 1..7, the running corpus or `controls`.**
- **The Curta's own migration.** The project wires its button and drops its
  unneeded `Time.elapsed()` line in its own repository.

## Decisions

### 1. An instruction under a clocked root is ONE request, and `trigger` makes it

`Instruction` states a mapping of driver name to a design-unit value and a
duration, in exactly one of two forms (`solid_node/simulation/instruction.py`).
`Clocked.move(input_id, by=…, to=…)` takes a design-unit travel or landing on
one declared driver. The two already line up, term for term:

| declaration | request |
| --- | --- |
| `by={id: travel}` | `move(id, by=travel)` |
| `targets={id: value}` | `move(id, to=value)` |

So the meaning is not invented here; it is READ OFF two existing surfaces. The
same mapping is what a RUNNING root already makes of an instruction —
`Run.trigger` issues "`targets=` a move TO each target, `by=` a move BY each
travel" (`solid_node/simulation/run.py:440-459`) — which is why this cycle
adds no concept: the third base makes the same two moves the second one makes,
through its own `move`.

Both forms are admitted. Refusing `targets=` under a clocked root would cost
MORE than admitting it — a new refusal, a message, a test and an asymmetry a
maker cannot explain — where admitting it costs one branch and no new idea,
and a version 8 document already publishes both forms today, with a ratified
scenario saying so (`openspec/specs/export/spec.md`, "A clocked document
publishes both instruction forms"). The Curta exercises `by=`; `targets=` is
the same sentence's other half rather than a second feature (recorded in the
report under the evidence rule).

### 2. Exactly ONE driver, refused where the machine is compiled

The ratified requirement "A clocked simulation solves a request path event by
event" already says a request "SHALL name exactly ONE MOVING INPUT" and that
"a request naming … more than one input SHALL be refused by name". If an
instruction under a clocked root IS a request, then it names one driver, and
an instruction naming two or none is refused. That refusal is the EXISTING
rule reaching the declaration; it is not a new one.

It goes where the facts first exist: `compile_clocked`, in the loop that
already refuses an instruction naming a State
(`solid_node/simulation/clocked.py:421-430`), whose docstring states exactly
that principle — "the refusals here are the ones whose facts first exist at
simulation construction". Every producer compiles before it publishes, so the
refusal also means no document can carry such an instruction, and a consumer
never has to check an instruction's arity before enabling its button.

**The alternative, sequential requests in declaration order, is rejected**,
against the briefing's own recommendation, for four reasons:

1. **No project has one.** The clocked Curta declares one instruction naming
   one input. `fast_curta`'s multi-input `'Rest'` is a POSED model whose
   instructions are ramps; nothing clocked names two. The governing rule in
   `AGENTS.md` ("Every feature needs empirical evidence") forbids the
   speculative half.
2. **It would be a third meaning for one declaration.** Under a running root
   the inputs move CONCURRENTLY over one duration, every input claimed before
   any starts. Sequential requests are neither that nor a ramp.
3. **It would need machinery nothing else needs.** Requests are atomic
   individually (ADR-125); a sequence of them is not, so the instruction would
   need a snapshot/restore envelope, a rule for a STOP in the middle, and two
   corpus features — all for a machine nobody has written.
4. **The framework already said so.** `Instruction`'s docstring: "Sequencing
   ('home X, then home Y') is the beginning of a program, and that is the
   G-code layer's job — faking it here would have to be unfaked later."

The refusal is cheap to LIFT when a project needs it; a published semantics,
mirrored by the viewer and pinned by an exact corpus, is not cheap to change.

### 3. `trigger` returns the request itself

One input means one request, so `trigger` returns a `Request` — not a
one-element tuple, not a `Triggered(name, requests)` wrapper. A tuple of one
is ceremony that anticipates §2's rejected alternative, and a wrapper carries a
name the caller already typed and a duration the document already publishes.
The running `trigger` returns a tuple because a running instruction really can
own several inputs at once; copying that shape here would be design symmetry,
which is explicitly not evidence.

The consequence is stated rather than hidden: if a later cycle admits several
inputs with evidence, `trigger`'s return shape changes with it. That is the
cost of not guessing now, and it is smaller than the cost of a wrapper every
caller unwraps forever.

### 4. `duration` is carried and silent

A request is a PATH, not an interval: it has no dt, no cadence and nothing to
spend seconds on. So the machine does not read `duration`. It stays validated
where it is validated today — finite and non-negative, at declaration
(`instruction.py:53-58`) — and published where ADR-128 publishes it. Its
meaning is stated once, in the simulation capability, as a sentence about the
CONSUMER: it says how long a consumer draws the transition, and zero means
"draw nothing, land".

This is testable rather than asserted: two roots differing only in the
declared duration make the identical request and the identical bank.

### 5. The request carries BOTH ENDS of its path

`Request(input, by, to, commits, admitted, stops)` (`clocked.py:1589-1616`)
does not say where the input STOOD. Probed on this worktree over the
`Calculator` fixture:

```
move('crank', by=740.0)
  -> input='crank', by=740.0, to=None, admitted=740.0, stops=()
     commits at value 360.0 (fraction 0.4865) and 720.0 (0.9730)
```

Nothing in it is `0`. `to` is `None` for a relative request; `by` is the ASK,
in DESIGN units, and not the travel the machine admitted. So a consumer
holding only the request cannot say where to start drawing.

Two fields are added:

- **`origin`** — the value the moving input held when the request began,
  `self.bank[input_id]` verbatim (`clocked.py:2063`);
- **`end`** — the value it ended at, the CLIPPED target verbatim
  (`clocked.py:2090`), which is where the bank stands afterwards.

Both are in the input's NATIVE units, which is the units every `Commit.value`
already speaks, so every event's value lies on the segment `origin..end`
and a drawer compares like with like. `admitted` is untouched and stays in
DESIGN units, which is what a caller asking `by=` wants to hear.

**Why the end is published and not computed.** A consumer could try
`origin + admitted / scale`. It must not. ADR-128's own one-authority driver
says the thing that compiled the machine is the thing that says what it is,
because a consumer that re-derives lands on a different float; and this is
exactly such a float. A commit landing ON the endpoint — which the ratified
containment rule makes that request's own event — is drawn only if the
reconstructed end is not one ulp short of it. Publishing the two floats the
machine actually used removes the question. It also removes a `scale` lookup
and a division from every drawer, and the clock has no scale at all.

**Nothing else is added.** `Commit` was checked, not assumed
(`clocked.py:1552-1585`): it carries `relations` (as written), `fraction` (of
the clipped path), `value` (the LANDING, the input's own value where the
relation fired) and `targets` (the ids written and the values written), and
the tuple is in path order. That is every piece a drawer needs to rebuild the
bank at any point of the transition. A drawer may key on `fraction` or on
`value`; the framework states both and asserts nothing about which.

### 6. Where the code goes

`Sim.trigger` keeps the resolution and delegates the motion, exactly as
`Sim.move` already does (`sim.py:309-331`):

- `self._instruction(name)` resolves the qualified name and raises the
  existing `KeyError` listing the declared ones (`sim.py:595-603`) — so the
  unknown-name message shape is the running one by construction, not by
  imitation;
- `self._driver(id, name)` resolves the one class-local target against the
  declaring node's path and raises the existing `KeyError` (`sim.py:605-613`);
- the request itself is `self._clocked.move(id, by=…)` or `(id, to=…)`.

`Clocked` gains nothing: it does not hold the instruction table, and putting a
second copy of the resolution there would be two authorities for one message.
`_not_clocked` keeps refusing `run`, `at`, `every`, `tick`, `rate`,
`commands`, `program` and `crossings`; `trigger` simply leaves that list.
`_At.trigger` (`sim.py:86`) is unreachable under a clocked root because `at()`
is refused, and stays as it is.

An instruction whose target resolves to `time` is refused by the existing
`_driver` message: the clock is not in `sim.drivers`, and no project has
asked for a timed instruction.

### 7. The document changes nothing

Version 8 already carries `instructions` in the version 5 shape, with
`duration` and exactly one of `targets` and `by`, and `clocked.commits`
already says everything about how a request is executed. A consumer that can
execute a request can execute the one an instruction names, because it IS one.
So: no new key, no new field, no version bump, no producer change, and a
version 8 document published after this cycle is byte for byte the one the same
root published before it.

Two sentences of the export capability move, and only because they say the
opposite of what is now true: "This version SHALL give a published instruction
NO execution meaning" becomes the statement of what it does mean and where
that is stated, and the "both instruction forms" scenario's closing clause
becomes the byte-identity claim above. One sentence is added, saying an
instruction naming none or several drivers reaches no document — a consequence
of §2, stated where a consumer reads.

### 8. The corpus records a `trigger` step

`tests/clocked-corpus.json` is the contract between the two runtimes and it is
EXACT (ADR-128). The viewer's cycle will play a returned request; if the
corpus records only hand-made requests, the two runtimes could agree about
`move` and disagree about what a BUTTON does. So the generator gains a fourth
script verb, `{'trigger': '<name>'}`, recorded through the same `apply_step`
shape as a request — the bank after it, the admitted travel, both ends, the
commits and the stops — so a divergence in the instruction's meaning is a
replay failure like any other. The declared `duration` is NOT recorded in a
step: it is already in the document copy the fixture carries verbatim, and the
machine does not read it.

No clocked fixture declares a playable instruction today; the only one is
`unsupported.py:Instructed`, which exists to be refused. Rather than invent a
machine, the Curta-shaped `Calculator` — the fixture whose whole purpose is
the Curta's interactions — gains the Curta's own instruction and its absolute
twin:

```python
instructions = {
    'Stroke': Instruction(by={'crank': 360.0}, duration=2.0),
    'Set four': Instruction({'operand': 4}, duration=0.5),
}
```

`'Stroke'` is the Curta's `'Turn crank'` on this fixture's crank, and crosses
a stroke event on the way, so the recorded step carries commits and not merely
a bank. `'Set four'` lands an `int`-typed driver through `native()`, which is
the `targets=` branch. Both enter the generator's `REQUIRED` inventory, so a
corpus that stopped exercising either is refused rather than quietly narrower.

`tests/clocked-corpus.json` and `tests/clocked_documents/calculator.json` are
regenerated, because the fixture's own declarations changed. The viewer
commits and replays the regenerated corpus in ITS cycle, in its own
repository; nothing here touches it.

### 9. What a consumer does with the result (informative, and not the framework's)

Stated once so the cycle's purpose is legible, and stated nowhere in a spec: a
consumer holding `Request(origin, end, commits, …)` and the published
`duration` draws the transition by walking a progress `p` from 0 to 1 over
that duration, setting the moved input to `origin + p * (end - origin)`,
applying every commit whose `fraction` is at or below `p` (equivalently, whose
`value` lies at or before the interpolated value), and posing from the bank
that results. One solve, N poses, no machine work in the frame loop. The
framework asserts none of this: it states the ends, the landings and the
written values, and stops.

### 10. The rejected alternative, with its measurement

**Slicing the instruction into per-frame requests** — `trigger` returning a
generator of small `move`s, or a consumer making one request per frame — was
rejected by the pilot, and the originating project measured why. From
`simulation/docs/clocked-curta-2026-09-17.md`:

| | one request | the same stroke in 20 requests/poses |
| --- | ---: | ---: |
| Python | 0.07875 s | 1.56363 s |
| Chromium | 36.95 ms | 647.7 ms |

Twenty slices already cost 17-20x the whole stroke, and a 2-second instruction
drawn at 60 fps is 120 slices, not 20. Beyond cost it is also WRONG in kind:
each slice would solve its own events, so the stroke's carries would be
located 120 times instead of once, and the machine would be back in the frame
loop — the `operating_curta` structure the clocked discipline exists to
replace.

### 11. What the evidence rule struck

Under `AGENTS.md` §"Every feature needs empirical evidence", three surfaces the
briefing raised were struck rather than designed, each recorded in the report:

- **sequential multi-input instructions** and their snapshot atomicity (§2) —
  no clocked machine names two inputs; refused instead;
- **a `Triggered(name, requests)` wrapper or a tuple return** (§3) — nothing
  needs the name or the plurality;
- **any statement about frames, interpolation or playback in a framework
  spec** (§9) — the consumer's, and the viewer's cycle owns it.

One surface was ADMITTED that the Curta does not exercise: the `targets=`
form (§1). The reason is that refusing it costs more surface than admitting
it, and version 8 already publishes it with a ratified scenario.

### 12. The ADR plan

One NODE ADR, candidate **ADR-129**, "An instruction under a clocked root is
one request, and the consumer draws it", extracted after implementation in the
house style of ADR-125..128:

- **Context**: the Curta finding above — the project, the branch, the record,
  the pilot's sentence, the two measurements.
- **Decision**: an instruction under a clocked root means one request per the
  driver it names, exactly one driver, `trigger` returns the request, `Request`
  carries `origin` and `end`, the consumer draws, the document does not
  change.
- **Considered and rejected**: per-frame slicing (with the table of §10);
  sequential multi-input requests (§2); a wrapper return (§3); publishing a
  playback hint in the document (§7).
- **Consequences**: every published instruction is playable; the corpus pins
  the meaning; the viewer's cycle owes a player and no solver change.
- **Amends** ADR-128 §"Instructions are published in the version 5 shape, with
  no meaning", with the house `Amended` line added there, and **closes** the
  wart at `workflow/warts.md:3285-3292`.

### 13. Zero behaviour change elsewhere, as a requirement with a test

Nothing outside a clocked root moves. `Run.trigger`, the untimed ramp path,
`Time.running()`, `tests/running-corpus.json`, every document of versions 1..7
and every producer are untouched, asserted by diff and by a fixture that
republishes a running and a stateless model byte for byte.

## Risks / Trade-offs

- **`trigger`'s return shape is not future-proof** (§3). Accepted knowingly:
  a later multi-input cycle would change it. The alternative is ceremony in
  every caller today for a machine nobody has written.
- **The arity refusal narrows what a clocked root may declare.** A
  multi-input instruction on a clocked root is legal today (published as a
  disabled button) and becomes a construction refusal. No model in this
  repository, in the Curta or in any fixture declares one — checked — and the
  gain is the invariant "published implies playable", which keeps a consumer
  from needing arity logic.
- **`origin`/`end` are native while `admitted` is design.** A genuine
  asymmetry inside one value object. It is the honest one: the two ends must
  match `Commit.value`, and `admitted` must match what `by=` asked. Both are
  documented in the same sentence.
- **Two names are minted into a public value object.** `origin` and `end`
  are plain words (`Clocked.move`'s local `origin`; `end` chosen over
  "landing" at review, open question 2).
  The viewer will mirror them, as its `ClockedRequest` mirrors every other
  field (`solid-node-viewer`,
  `solid_node_viewer/widget/src/clocked/machine.ts:60-67`).
- **The corpus grows.** Two script steps and one fixture's two declarations;
  the file is regenerated, and its exactness and inventory refusals are
  unchanged.

## Open Questions

1. **Does the pilot want the multi-input refusal, or the sequential
   semantics the briefing recommended?** This design refuses, under the
   evidence rule, and says exactly what lifting it would cost (§2). A
   ratification answer either way is cheap now and expensive after the corpus
   ships.
2. **`end`, not `landing`.** SETTLED at review: the request's second end is
   `end`. "Landing" is the ratified word for where an EVENT fires (and for
   where a stop puts the input), and a drawer compares every commit's landing
   against the request's end; one word for both would make that comparison
   read as a tautology. The viewer mirrors `origin`/`end`.
3. **Should `trigger` under an UNTIMED root also return its ramps?** It
   returns `None` today. Out of scope, no project needs it, and it is recorded
   here only so the asymmetry is not mistaken for an oversight.

## Planned proof

Every test below is RED FIRST, run and SEEN to fail for the stated reason
before the change that turns it green. Every fixture is geometry-free.

### 14. Fixtures

- `tests/clocked_project/calculator.py`: the two instructions of §8, on the
  existing `Calculator`. Nothing else in that fixture changes, so every
  existing test over it must stay green unchanged.
- `tests/clocked_project/unsupported.py`: beside the existing `Instructed`
  (an instruction naming a State), two more — one whose `by` names two
  drivers, one whose `by` is empty — each written so the refusal test can
  quote the declaration.

### 15. Tests, per requirement

**"Instructions carry design-unit targets" (simulation)**

1. `tests/test_clocked_sim.py`: triggering `'Stroke'` on the `Calculator`
   returns a request EQUAL, field for field, to `sim.move('crank', by=360.0)`
   made from the same bank, and leaves the same bank. RED: `trigger` raises
   `TypeError` from `_not_clocked`.
2. The same for `'Set four'` against `sim.move('operand', to=4)`, so the
   `targets=` branch is proved and not inferred.
3. Two roots differing only in `duration` (2.0 and 0.0) make equal requests
   and equal banks — the duration's silence, §4.
4. An unknown name under a clocked root raises `KeyError` listing the declared
   qualified names, and the bank and pose stand. RED: today it raises
   `TypeError` about a cadence.
5. `tests/test_clocked_refusals.py`: constructing `Sim` over the two-driver
   instruction, and over the empty one, is refused naming the instruction, the
   inputs and the rule. RED: both construct today.
6. The existing State-target refusal still fires with its own message
   (regression, must not be absorbed by the new one).

**"A clocked simulation solves a request path event by event" (simulation)**

7. `tests/test_clocked_sim.py`: a `by=` request from a non-zero start reports
   `origin` equal to the bank before it and `end` equal to the bank after
   it, and every commit's `value` lies between them. RED: `Request` has no
   such fields.
8. A CLIPPED request reports `end` at the stop's landing and not at the
   value asked for; a request admitted at ZERO travel reports
   `origin == end`.
9. A `to=` request over an `int` driver reports `end` as the converted
   native value.
10. `trigger` is absent from the cadence refusal test's list, and `run`, `at`,
    `every`, `tick`, `rate`, `commands`, `program` and `crossings` still
    refuse by name (regression).

**"A clocked root's document publishes its compiled machine" (export)**

11. `tests/test_clocked_document.py`: the golden documents of every clocked
    fixture whose declarations did NOT change are byte-identical before and
    after this cycle; `calculator.json` differs ONLY in its `instructions`
    table.
12. Publishing a root whose instruction names two drivers writes no document
    and is refused by the machine's compile, through each producer that
    compiles.

**"The two runtimes share a clocked conformance corpus" (export)**

13. `tests/test_clocked_corpus.py`: the regenerated corpus replays exactly,
    both ends of every path included, with `tolerance.float == 0.0` unchanged.
14. A `trigger` step's recorded fields equal those of the same request made by
    hand in a second script.
15. The generator refuses a corpus in which no machine plays an instruction,
    and one in which only the relative form is played — the two new inventory
    entries, tested directly as the existing ones are.

**Zero change elsewhere**

16. `tests/running-corpus.json` replays unchanged; a running root's
    `trigger` still returns its tuple of commands and still refuses an
    already-owned input; a stateless model's document is byte-identical.

### 16. Measurement plan

- The cost of `trigger` against the cost of the same `move`, over the
  `Calculator` fixture, median of 20: the difference should be a dictionary
  lookup, and the claim "an instruction is a request and nothing else" is
  false if it is not.
- The clocked counter (ADR-128's zero-cost property) still reads ZERO across a
  stateless model's construction, render, symbolic walk, compile and
  `document_body`.
- The size of `tests/clocked-corpus.json` before and after, stated rather than
  discovered later.
