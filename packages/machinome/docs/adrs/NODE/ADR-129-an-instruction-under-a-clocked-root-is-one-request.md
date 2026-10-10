# ADR-129: An Instruction Under a Clocked Root Is One Request, and the Consumer Draws It

**Status:** Accepted
**Date:** 2026-09-17
**Depends on:**
- [ADR-125: A state is a driver the machine writes, committed at an event](./ADR-125-a-state-is-a-driver-the-machine-writes.md) — the clocked root, its bank, its REQUEST (one moving input, a straight path, every rising crossing an event landed on the far side, committed in path order, atomic), and the value object `move` returns, which this decision gives two fields and one more way to make
- [ADR-126: A bound stops a clocked request on its path](./ADR-126-a-bound-stops-a-clocked-request-on-its-path.md) — the CLIP, which is why the path's second end is the landing the stop gave it and not the value asked for, and the `admitted`/`stops` report this decision leaves exactly as it is
- [ADR-128: A clocked root publishes its compiled machine](./ADR-128-a-clocked-root-publishes-its-compiled-machine.md) — version 8, the published `instructions` table, the EXACT corpus and the one-authority rule that makes the machine publish the floats it stood at rather than let a consumer rebuild them; **amended** by this decision on one section, below
- [ADR-056: Signals, drivers, ports and stepped simulation](./ADR-056-signals-drivers-ports-and-stepped-simulation.md) — `Instruction(targets|by=, duration)`, its design units, its qualified name and its class-local target resolution, all taken unchanged
**Cites:**
- [ADR-127](./ADR-127-a-clock-is-a-banked-value-and-an-event-on-it-is-an-event.md) — the elapsed clocked root, whose `trigger` means exactly what an untimed clocked root's means; no instruction moves the CLOCK, and none is added here
- [ADR-104](./ADR-104-a-third-time-base-elapsed-seconds-that-never-wrap.md), [ADR-105](./ADR-105-the-run-owns-the-coordinates-and-binds-them.md) — the RUNNING base, whose `trigger` issues the run's own commands and is untouched, asserted by diff
- [ADR-110](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md) — the version ladder, which does not move: this decision adds no field, no key and no version
- [ADR-111](../EXPORT/ADR-111-a-conformance-corpus-is-the-contract-between-the-two-runtimes.md) — the producer-generated fixture with its enforced coverage inventory, which gains a fourth script verb and two entries
- [ADR-121](./ADR-121-a-law-may-read-the-coordinate-it-drives.md) — `far_side_of`, the one landing walk that produces the floats this decision publishes as the path's ends
**Amends** ADR-128 on ONE section, §"Instructions are published in the version
5 shape, with no meaning": the table is unchanged and the document is
unchanged, and what moves is the MEANING — `trigger` is no longer refused
under a clocked root, and an instruction naming none or more than one driver
is refused where the machine is compiled. It **amends nothing else**: ADR-125's
request, ADR-126's clip and ADR-127's clock stand as written, versions 1
through 8 and every published byte stand, and `Time.running()`'s own
instruction path is untouched, asserted by diff and by fixture.
**OpenSpec change:** `play-the-instruction` (archived at
`openspec/changes/archive/2026-09-17-play-the-instruction/`)
**Originating project:** `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation`, HEAD `9fb725f`, whose third sibling
`simulation/clocked.py:ClockedCurta` declares, on line 95,
`instructions = {'Turn crank': Instruction(by={'crank_rotation': 360},
duration=2)}` and got nothing for it. The project's own record is
`simulation/docs/clocked-curta-2026-09-17.md`, whose "Limits" section says it
in one line — *"The instruction remains disabled metadata under the current
clocked contract"* — and whose "Timing" section measured both this decision's
cost and its rejected alternative's.

## Context and Problem Statement

ADR-125 through ADR-128 built a machine with memory, gave it bounds and a
clock, and published what it is. The originating project has all of it and
cannot show it working.

The Curta is modelled three ways in that repository. `fast_curta` is
closed-form, declares seven instructions with durations, and ANIMATES,
because a POSED document's instruction is played by the viewer as a ramp of
its drivers over `duration`, one pose per frame. `operating_curta` runs on
`Time.running()` and pays a tick per frame. `clocked_curta` holds state,
reproduces the operating model's registers at every stroke end, and completes
a whole stroke — every tooth, every carry, in path order — in **0.07875 s** in
Python and **36.95 ms** in Chromium. It is fast enough to be watched, and it
could not be watched.

The pilot's requirement, verbatim: *"I need it to be animated fast between
states with smooth transition just like the fast_curta, but holding state."*

The gap was ADR-128 §"Instructions are published in the version 5 shape, with
no meaning". That cycle published every declared instruction and deliberately
gave the table no runtime meaning: `sim.trigger` stayed refused BY NAME on a
clocked `Sim`, among `run`, `at`, `every`, `tick`, `rate`, `commands`,
`program` and `crossings`, and a viewer listed the buttons disabled. So the
only way to turn that crank was `sim.move('crank_rotation', by=360)`: one
request, the crank jumps a whole turn, every carry fires, the tree poses ONCE
at the end, and nothing is seen moving. That was recorded as the open wart
*"the instruction's meaning under a clocked root"*.

The missing capability was not in the machine. The machine computes the whole
stroke exactly, in one request. What was missing was that nothing turned "the
maker pressed Turn crank" into that request, and that nothing the request
returned said where the crank STARTED — so a consumer could not draw the
stroke between its two ends.

## Decision Drivers

- **A request is one state transition, computed once and exactly.** How it is
  DRAWN is the consumer's, and the framework never learns what a frame is.
- **Every feature needs empirical evidence** (`AGENTS.md`). This cycle was run
  under that rule, and the rule STRUCK three surfaces its own brief raised:
  sequential multi-input instructions with the snapshot/restore envelope they
  would need, a `Triggered(name, requests)` wrapper or a tuple return, and any
  statement about frames, interpolation or playback in a framework spec. Each
  is recorded below with the reason.
- **One authority** (ADR-126, restated by ADR-128): the thing that computed a
  float is the thing that says what it is. A consumer that re-derives a path's
  end lands on a different float.
- **Published implies playable.** An instruction a consumer must inspect
  before enabling its button is a table with a footnote.
- **The framework may not move what it already published.** Version 8 shipped
  its document and its exact corpus in the cycle before this one.

## Considered Options

**Slice the instruction into per-frame requests** — `trigger` returning a
generator of small `move`s, or a consumer making one request per frame.
Rejected by the pilot, and the originating project measured why:

| | one request | the same stroke in 20 requests/poses |
| --- | ---: | ---: |
| Python | 0.07875 s | 1.56363 s |
| Chromium | 36.95 ms | 647.7 ms |

Twenty slices already cost 17-20x the whole stroke, and a 2-second
instruction drawn at 60 fps is 120 slices, not 20. Beyond the cost it is wrong
in KIND: each slice would solve its own events, so the stroke's carries would
be located 120 times instead of once, and the machine would be back in the
frame loop — which is the `operating_curta` structure the clocked discipline
exists to replace.

**Sequential requests, one per named driver, in declaration order.** Rejected
under the evidence rule, against the cycle's own briefing recommendation. No
clocked machine in this repository, in the Curta or in any fixture names two
inputs in one instruction; `fast_curta`'s multi-input `'Rest'` is a POSED
model whose instructions are ramps. It would also be a THIRD meaning for one
declaration — under a running root the named inputs move CONCURRENTLY over one
duration, every input claimed before any starts — and it would need machinery
nothing else needs: requests are atomic individually (ADR-125), a sequence of
them is not, so it would want a snapshot/restore envelope, a rule for a STOP
in the middle, and two more corpus features, all for a machine nobody has
written. `Instruction`'s own docstring already said so: sequencing "is the
beginning of a program, and that is the G-code layer's job — faking it here
would have to be unfaked later."

**A `Triggered(name, requests)` wrapper, or a one-element tuple.** Rejected:
the name is what the caller typed, the duration is what the document
publishes, and a tuple of one is ceremony anticipating the alternative above.
The running `trigger` returns a tuple because a running instruction really can
own several inputs at once; copying that shape here would be design symmetry,
which is not evidence.

**Refuse the `targets=` form under a clocked root.** Rejected on cost:
refusing it needs a new refusal, a message, a test and an asymmetry a maker
cannot explain, where admitting it costs one branch and no new idea — and
version 8 already publishes both forms with a ratified scenario saying so.
The Curta exercises `by=`; `targets=` is the same sentence's other half.

**Publish a playback hint in the document** — a frame count, a cadence, an
interpolation kind. Rejected: the document already carries the duration, and
what a consumer does with seconds is the consumer's.

## Decision

### An instruction under a clocked root IS one request, and `trigger` makes it

The meaning is not invented; it is read off two existing surfaces that already
line up term for term:

| declaration | request |
| --- | --- |
| `by={id: travel}` | `move(id, by=travel)` |
| `targets={id: value}` | `move(id, to=value)` |

Both in design units, through `Sim`'s EXISTING `_instruction` and `_driver`
resolvers — so the qualified-name rule, the class-local target resolution and
the unknown-name `KeyError` listing the declared names are the running base's
by construction and not by imitation. `Clocked` gains nothing: it does not
hold the instruction table, and a second copy of the resolution there would
be two authorities for one message. This is the same mapping a RUNNING root
already makes of an instruction, which is why the third base adds no concept.

`sim.trigger(name)` leaves the refused cadence list. `run`, `at`, `every`,
`tick`, `rate`, `commands`, `program` and `crossings` stay refused by name
under every time base; `trigger` is the one verb of that list with a meaning
here, as `stops` was and as `time` is under `Time.elapsed()`.

### Exactly ONE driver, refused where the machine is compiled

A request names exactly one moving input. If an instruction under a clocked
root IS a request, then it names exactly one driver, and one naming two or
none is refused. That is the EXISTING rule reaching the declaration, not a new
rule.

The refusal goes where the facts first exist: `compile_clocked`'s instruction
loop, beside the refusal of an instruction naming a State, raising
`ClockedError` with the instruction, the count, the sorted qualified inputs
and the rule. Every producer compiles before it publishes, so no document can
carry such an instruction, and a consumer never has to check an instruction's
arity before enabling its button. The State refusal stays exactly where and
what it was, asserted unabsorbed by the new one.

The narrowing is deliberate and is cheap to LIFT when a project writes the
machine that needs it. A published semantics, mirrored by a second runtime and
pinned by an exact corpus, is not cheap to change.

### `trigger` returns the request itself

One input means one request, so `trigger` returns the `Request` — the same
value object `move` returns, not a wrapper and not a tuple. A caller that
pressed a button holds exactly what a caller that moved the input holds.

The cost is stated rather than hidden: if a later cycle admits several inputs
with evidence, this return shape changes with it. That is smaller than the
cost of a wrapper every caller unwraps forever.

### `duration` is carried and silent

A request is a PATH, not an interval: no dt, no cadence, nothing to spend
seconds on. The machine does not read the duration. It stays validated where
it is validated today — finite and non-negative, at declaration — and
published where ADR-128 publishes it, and what it says is how long a CONSUMER
draws the transition, zero meaning "draw nothing, land". This is proved rather
than asserted: two roots differing ONLY in the declared duration make the
identical request and the identical bank.

### A request reports BOTH ENDS of the path it travelled

`Request` gains `origin` and `end` beside `input`, `by`, `to`, `commits`,
`admitted` and `stops`. Before this cycle nothing in it said where the input
STOOD: probed at the cycle's base, `move('crank', by=740.0)` returned `by`
and `admitted` both `740.0`, `to` `None`, and commits at `360.0` and `720.0`
with nothing anywhere saying the path began at `0`.

- **`origin`** is the value the moving input held when the request began, the
  bank entry verbatim;
- **`end`** is the value it ended at, the CLIPPED target verbatim, which is
  where the bank stands afterwards.

Both are in the input's NATIVE units — the units every `Commit.value` already
speaks — so every event's value lies on the segment they span and a drawer
compares like with like. That is a deliberate asymmetry with `admitted`, which
stays in DESIGN units because that is what `by=` asked in, and both are stated
in one sentence of the value object's own docstring.

Because each end is the bank entry verbatim, `origin` carries whatever TYPE
the bank holds: an `int` where an integer-typed driver stands at its integer
default, a float everywhere else. A consumer treats both ends as numbers and
reads neither as a declaration of type.

**The end is published and not computed.** A consumer could try
`origin + admitted / scale`. It must not: this is exactly the float ADR-128's
one-authority driver is about. A commit landing ON the endpoint — which the
ratified containment rule makes that request's own event — is drawn only if
the reconstructed end is not one ulp short of it. Publishing the two floats
the machine actually used removes the question, removes a `scale` lookup and a
division from every drawer, and costs the machine nothing: both values were
already in hand at the return.

**Nothing else is added.** `Commit` was checked rather than assumed: it
carries the relations as written, the fraction of the clipped path, the
LANDING value and the targets with the values written, in path order, which
is everything a drawer needs to rebuild the bank at any point of the
transition.

### The document does not change

No field, no key, no version bump, no producer change. Version 8 already
carries `instructions` in the version 5 shape and `clocked.commits` already
says how a request is executed; a consumer that can execute a request can
execute the one an instruction names, because it IS one. A version 8 document
published after this decision is byte for byte the one the same root published
before it — asserted, not inspected, by publishing one class twice, once with
the declarations and once without, and comparing every other key.

What moves in the export capability is one sentence that now says the
opposite of what is true, plus one consequence of the arity refusal: an
instruction naming none or more than one driver reaches no document, so every
instruction a version 8 document carries is one a consumer can play.

### The corpus records a `trigger`

`tests/clocked-corpus.json` is the contract between the two runtimes and it is
EXACT. If it recorded only hand-made requests, the runtimes could agree about
`move` and disagree about what a BUTTON does. So the generator gains a fourth
script verb, `{'trigger': '<name>'}`, recorded through the SAME shape a
request step is recorded in — the bank after it, the admitted travel, both
ends, the commits, the stops — and the coverage inventory gains two entries,
"an instruction played as a request BY a travel" and "an instruction played as
a request TO a target", so a corpus that stopped exercising either is refused
rather than quietly narrower. The declared `duration` is recorded in no step:
it is already in the document copy the fixture carries verbatim, and the
machine does not read it.

The Curta-shaped `Calculator` fixture — the one whose purpose is the Curta's
interactions — gained the Curta's own instruction and its absolute twin,
`'Stroke': Instruction(by={'crank': 360.0}, duration=2.0)` and
`'Set four': Instruction({'operand': 4}, duration=0.5)`.

**Measured**: 30 machines, 30 scenarios, 81 steps, 145 673 bytes (from 76
steps and 139 262 bytes), `"tolerance": {"float": 0.0}` unchanged. The growth
is five new `Calculator` steps and `origin`/`end` on all 63 recorded requests
across all 30 machines. Every other clocked golden document and
`tests/running-corpus.json` are byte-identical; `calculator.json` differs in
exactly one hunk, its `instructions` table.

### An instruction is a request and nothing else, measured

Over the `Calculator`, median of 20, one process, each request from the same
restored bank: `sim.trigger('Stroke')` **0.7833 ms** against
`sim.move('crank', by=360.0)` **0.7817 ms** — a difference of **1.7 us,
+0.22%**, where twenty dictionary lookups of the instruction cost 1.9 us in
the same process. The difference between pressing the button and making the
request is the table lookup, the driver lookup and the `'.'.join` that
qualifies the name.

## Consequences

**A clocked stroke can be watched.** A consumer holding the returned
`Request` and the published `duration` has everything it needs: it walks a
progress from 0 to 1 over the duration, sets the moved input between `origin`
and `end`, applies every commit already reached — keyed on the fraction or on
the value, the framework states both and asserts nothing about which — and
poses from the bank that results. ONE solve, N poses, no machine work in the
frame loop. The framework states the ends, the landings and the written
values, and stops there: it names no frame, no cadence and no interpolation.

**What a consumer now holds** is a `Request` carrying `origin`, `end`,
`commits` and `stops`, a `trigger` that makes exactly one request and returns
it, and a corpus carrying two `trigger` steps — one of each form, one crossing
a commit — plus both path ends on every recorded request. Playing that over a
duration is a consumer's own work, in its own repository and its own records;
this decision does not state it and does not claim it exists.

**Published implies playable**, by construction: the arity refusal happens
before any document exists, so no document carries an instruction a consumer
must inspect before enabling.

**Every existing caller keeps what it had.** A running root's `trigger` still
returns its tuple of command handles, still claims every input before starting
any and still refuses an already-owned input; an untimed root's still ramps
and still returns `None` — an asymmetry now pinned by a test rather than left
to be discovered, and left open deliberately, no project needing it. Document
versions 1 through 8 carry the same fields; `Time.running()`, `Time.elapsed()`
and `Time(loop=)` are untouched; `solid_node/simulation/run.py`,
`program.py` and `solid_node/core/` did not change, asserted by diff.

**What this decision does not do.** It does not touch the viewer (its own
repository, its own records), does not migrate the Curta (its own repository),
does not admit an instruction over the CLOCK or a multi-input one, does not
make `trigger` return anything under an untimed root, and does not reconcile
either of ADR-128's two meanings of `%`.

**Recorded and open** in `workflow/warts.md`: the multi-input refusal as a
deliberate, liftable narrowing with the cost of lifting it stated; an untimed
root's silent `trigger`; and `trigger`'s return shape being the thing a
later multi-input cycle would change.

## Promotion

Accepted 2026-09-17 at the cycle's adversarial review, which ran an
independent probe against the uncommitted implementation and agreed with it:
over the `Calculator` standing with its operand at 7, `trigger('Stroke')`
returned a request with `origin` `0` and `end` `360.0` carrying one commit at
value `360.0`, fraction `1.0`, writing `w0`..`w3`; a second `trigger` reported
`origin` `360.0` and `end` `720.0`; `trigger('Set four')` reported `origin`
`7` and `end` `4`; and an unknown name raised `KeyError` listing
`Set four, Stroke`. The review accepted the implementation as it stands,
including the four things it reported rather than silently resolved: a new
**Clocked simulation** section in `docs/api-reference.rst`, which is more
surface than the ratified task named and was accepted because `Request`,
`Commit`, `Clocked` and `ClockedError` were documented nowhere and this is the
first cycle to hand a `Request` to a consumer; `HISTORY.rst`'s corpus step
count corrected in place in the same unreleased section, ADR-128's own
measurement left alone as that cycle's record; the cadence list corrected in
BOTH test modules, the elapsed root's copy being what proves the meaning holds
under every time base; and `_instructed()` made parameterizable, the only way
to vary one declaration and nothing else when a published commit carries the
name of the assembly that stated it. The implementation's own record — the red
log for every task, every measurement quoted above and the corpus diff — is
`evidence.md` inside the archived change.
