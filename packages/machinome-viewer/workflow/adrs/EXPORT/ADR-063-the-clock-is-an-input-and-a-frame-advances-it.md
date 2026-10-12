# ADR-063: The clock is an input a request moves, and one rendered frame is one request

**Status:** Accepted

**Date:** 2026-09-17

**Change:** `run-the-clock`

**Extends:**
- [ADR-062: The viewer executes a clocked machine in thread, and a declared stop clips the request before any event](ADR-062-the-viewer-executes-a-clocked-machine-in-thread.md)

**Builds on:**
- [ADR-045: The run executes in a worker and the main thread only poses](ADR-045-the-run-executes-in-a-worker.md)
- [ADR-046: A committed bank is a name in the same scope as a driver](ADR-046-a-committed-bank-is-a-name-in-the-same-scope.md)
- [ADR-047: The corpus is what makes the two runtimes one algorithm](ADR-047-the-corpus-makes-the-two-runtimes-one-algorithm.md)
- [ADR-048: Running controls submit requests; nothing binds back](ADR-048-running-controls-submit-requests.md)

**Consumes:**
- solid-node ADR-127: a clocked root may declare an elapsed time base, and
  nothing stops a clock
- solid-node ADR-128 §10: the clock is published as `clocked.clock`, and the
  document carries the free name `time` wherever the model reads it

## Context

ADR-062 made this viewer read and execute a version 8 clocked machine —
the bank, the request, the event solve, the commit, the clip at a declared
stop, the pose — and left exactly one thing behind, in its own last line:
the CLOCK. A version 8 document whose root declares `Time.elapsed()` banks
`time` in seconds at `0.0`, poses from it, animates and takes every request
on its ordinary drivers, and `move('time', …)` was refused by name at the
gesture:

```text
move('time', ...) asks this machine's clock to advance, which this build
does not yet do. The bank stands at 0 seconds and the model is posed
there; a later build moves the clock and fires the events on it.
```

Three things followed from that refusal, and this cycle closes all three.

**The conformance corpus was not whole.** `src/clocked-corpus.json` (the
producer's `tests/clocked-corpus.json`, 139 262 bytes, md5
`852b86b804ebd785f6e6b1f5568fb01a`, `"tolerance": {"float": 0.0}`) carries 30
machines and 76 steps; ADR-062 replayed 68 of them and 652 of the 722
recorded numbers. The 8 remaining were the clock's — three requests this
build refused where the producer admitted them (`Regulator` 0, `ClockAlone`
0, `Lift` 0) and five steps standing downstream of them — asserted as a
DEPARTURE and pinned by a census at `76 = 68 + 3 + 5`. The exactness claim
was therefore untested on the machine shape whose landings are the strangest
the file holds: `Regulator`'s first release lands on
`0.49999999999999994`, one representable value below the ideal instant,
which is ADR-127's landing rule working rather than a rounding error.

**A maker could not RUN an elapsed machine.** The chrome showed the clock as
a follow-only readout and offered no transport at all. A pendulum whose bob
is a formula of elapsed seconds, with a counter beside it, stood at `t = 0`
for ever — a truthful render of one instant, and not a machine anyone can
watch.

**A published guard was missing.** The producer compiles a constraint plan
per DECLARED DRIVER (`clocked.py:1422`) and refuses any composed chain
carrying a name the bank has not got (`clocked.py:1448-1487`, ADR-127's own
tightening), so no document it writes can carry a stop that follows the
clock. The viewer's loader mirrored the first of those and not the second: a
bound's chain was checked against `declaredNames`, which INCLUDES the clock.
A hand-written or corrupted document could therefore be clipped against a
clock-driven coordinate the producer would have refused outright.

The producer is solid-node branch `clocked-machine` at `1a959d3`, read-only
and unintegrated. The originating project remains the Curta, which declares
no clock at all and neither owes this cycle anything nor is compared with it.

## Decision

**The clock is one more input a request may move, and the CADENCE that moves
it belongs to the page: one `move(clock, {by})` per rendered frame.**

### The request

- `machine().move('time', {by})` and `{to}` execute on the path that already
  exists. `declarationOf` answers for the clock with a driver-shaped
  declaration — `{default: 0, range: null, unit: 's', dtype: null, scale:
  null}`, which is the producer's `_ClockInput` field for field — so
  `native()` is the identity, **no conversion is added anywhere**, and `by`,
  `to` and the admitted travel are all plain seconds. Every `commits` entry
  whose published `shapes` names the clock is examined and no others,
  crossings are solved and landed by the same far-side walk, relations
  landing on one float are one event with synchronous pre-event reads,
  commits fire in path order, and the tree is posed ONCE from the resulting
  bank. **An event on the clock is an event**: one solver, one landing rule,
  one ordering, one conflict rule, and no new tolerance. `by=0` and `to=` the
  banked instant are ADMITTED, fire nothing and pose what already stands.
- **Time never reverses.** A request whose travel is negative, or whose `to=`
  lies behind the banked seconds, is REFUSED by name — kind `ValueError`
  (`ClockedRequestError`), naming the clock and both instants. The check sits
  exactly where the producer's does (`clocked.py:2064-2082`): after the
  by/to exclusivity refusal and after `target` is computed, BEFORE the clip.
  That order is observable — a request stating both `by` and `to` on a
  backwards clock must get the exclusivity message — so it is mirrored
  rather than re-derived. It is a REFUSAL and not a stop: a stop reports a
  bound the machine MET, and no bound was met.
- The eleven lines of ADR-062's gesture refusal are deleted. ADR-062's
  finding F7 is kept: on a machine whose `clocked.clock` is `null`,
  `move('time', …)` still meets the ordinary undeclared-input refusal.

### Nothing stops a clock — stated, asserted, guarded

- **No declared stop ever clips a request that moves the clock.** It already
  fell out of the compile — the clip finds no plan for an input no
  constraint names — and ADR-127 states it as a PROMISE rather than leaving
  it an accident, because a declared range is a MECHANICAL stop (ADR-108)
  and nothing is in the way of the next second. This cycle writes **no clip
  code at all** and instead states it in the spec, asserts it on `Lift` —
  the corpus machine that declares a clock AND two compiled bounds, whose
  `move('time', by=4)` is admitted WHOLE with four events and no stop while
  the very next step's `move('lift', by=12)` is clipped to 9.0 with a high
  stop at fraction 0.75 — and refuses at load any document that would make
  it false.
- **The END-OF-REQUEST judgement is unchanged and still runs on a time
  request.** A commit fired by a time request that carries a bounded
  coordinate out of its range refuses the whole request by name, kind
  `JointRangeError`, committing nothing and posing nothing. No corpus
  machine exercises that on a time request, so it is pinned by a
  hand-written version 8 document — a `Regulator`-shaped machine whose
  counted dial carries a declared range the count drives past — rather than
  left as a spec sentence nothing checks.
- **A constraint that follows the clock is refused at LOAD, by name.**
  `readBound` refuses a `bounds` entry whose chain (`value`), whose `bound`
  or whose derived level reads the machine's clock, and says the producer's
  own reason; the existing `shapes` refusal now names the clock as the case
  a reader will actually meet. `declaredNames` is NOT narrowed — the clock
  is a bank id and a legal name in a commit's level, in a commit's law and
  in the tree's own pose expressions. The refusal belongs where the fact is:
  a CONSTRAINT's chain. This is the `mirror-the-gate-guard` shape: a guard
  the producer states and the consumer must not be silently wider than. It
  costs one `Set` difference per compiled constraint at load and nothing per
  request. Asserted over all 30 corpus machines: no published `bounds` entry
  names a clock anywhere, so the guard refuses nothing the producer writes.

### The transport: one request per rendered frame, and no scrub

- **PLAY issues exactly ONE `move(clock, {by})` per rendered frame**, for the
  wall seconds since the previous frame times the playback speed. This is the
  shape the run's real-time playback already has (ADR-046/048: the render
  loop drives the cadence), and it is right here for a reason of its own —
  **each frame is one request, so every event inside it is located exactly
  and in order**, by the same solver and the same landings. Sampling instead
  (posing at `t = k·Δ` without a request) would skip every event between
  samples; one request per EVENT would need the events located first, which
  is the request. The frame-sized request is not a convenience: it is the
  only shape that keeps the exactness claim while the clock runs.
- **The advance is CAPPED at four frames' worth of the current speed**, as
  the run caps its debt, and **wall time beyond the cap is LOST** — visibly,
  because the seconds readout falls behind the clock on the wall. A long
  frame is a long request, and `limits.max_crossings` applies to it: at
  ×3600 a one-second stall would ask for 3600 releases of `Regulator`, past
  the corpus's own limit of 1000. Losing time is honest where firing a burst,
  or refusing the frame, is not.
- **No remainder is carried.** The run carries a debt because its `dt`
  quantizes what a frame can earn; a clock request has no quantization —
  `by` may be any float — so the frame's own elapsed seconds are requested as
  they are. One fewer piece of state, and ten frames of `by` equal one frame
  of ten times `by`, instant for instant, which is the property ADR-127 says
  a tolerance would have cost.
- **A refused frame PAUSES** and reports across the panel, once — the run's
  own rule — rather than repeating a refused request sixty times a second.
- **No scrub and no reverse.** A timeline slider implies both directions and
  the clock refuses one of them by decision; a one-way slider that silently
  ignores half its travel is worse than none. What replaces it is a **STEP**:
  one request of a stated number of seconds, with an editable amount and no
  minus. A negative or non-finite amount typed there is refused as a
  SETTING — the field keeps the amount it had — never clamped as a request,
  because nothing a maker asks the machine for is ever clamped. A maker who
  wants an earlier instant restores a snapshot, which is what the backwards
  refusal's own message says.
- **Speed is the existing ladder** (`0.1 … 3600`, whose 360 and 3600 exist
  for watching a clock), reached through the same `setSpeed` the run uses:
  one meaning of speed in the widget for all three kinds of document.
  **Pause holds the bank** — no request is issued, so nothing moves — and
  **RESET** returns the whole bank to its published defaults with the clock
  at `0` and STOPS the transport, because a machine that reset itself while
  running would be a machine nobody could read. A republish rebuilds the
  machine at its initial bank and therefore does the same, exactly as it
  restarts a run.
- **A machine that declares no clock gets no transport**, exactly as before.

### `$t` and the clock never interfere

ADR-128 §10 publishes the clock as `clocked.clock` and carries the free name
`time` wherever the model reads it; `$t` is a 0..1 animation variable and is
not seconds. `tree.animated` is true only where something reads `$t`, so for
the ordinary elapsed clocked document it is false and **no timeline chrome is
built at all** — the clock's transport is the only transport such a document
has, and there is nothing for a maker to confuse it with. Where a document
carries both, the two controls are independent and each says what it
advances; the pose reads both through one scope, so a frame in which both
moved re-evaluates once. Under `clocked.clock: null` nothing changes.

### The handle, and the chrome that is not built

- `MachineHandle` is the pure `ClockedMachine` WRAPPED, with **two page verbs
  and no more**: `clockPlaying()` and `setClockPlaying(playing)`. They are
  deliberately not named `play`/`step` — `step()` is an existing member that
  refuses by name, because a clocked machine has no tick, and it goes on
  refusing. `setClockPlaying(true)` on a machine with no clock is refused by
  name; `clockPlaying()` is `false` there. A host that wants one frame's
  worth calls `move(machine.clock()!, {by})`, which it always could.
- The wrap also fixes a defect ADR-062 left: **every readout follows the
  COMMITTED bank, whoever moved it.** A host driving `machine().move(…)`
  moved the model but left the panel — the states, the drivers and the
  clock's seconds — showing the instant the machine had LEFT, because only
  the panel's own gesture path rebuilt the chrome. `move`, `restore` and
  `reset` on the handle now make the same rebuild a gesture makes.
- **A clocked document builds ONE chrome.** The posed driver panel is not
  built beside the clocked one — as it already is not built for a document
  carrying a program — because a clocked machine's inputs are moved by
  REQUESTS over its bank: a posed panel would offer a second control over
  the same input that writes the driver straight past the machine, and, both
  being anchored at the container's corner, would stand behind the clocked
  panel. (Found by inspecting this cycle's own screenshots; the defect is
  ADR-062's and the calculator fixture had it too.)
- **An INTEGER coordinate reads as the whole number it is.** The fixed four
  decimals are a continuous quantity's policy — a readout that changes sixty
  times a second under a drag wants one constant shape — and a state the
  machine commits as an integer has no fraction to report: `count` reads `5`,
  not `5.0000`. A scaled int still reads as a float, because its design
  value is not whole; the clock, which declares no dtype, keeps its decimals.
- The per-frame arithmetic — elapsed × speed, the cap — is a new PURE module,
  `src/clocked/clock.ts`, decided and tested in node exactly as
  `playback.ts` and `clockedControls.ts` are. Nothing about the frame loop is
  decided inside `machine.ts`, which stays the corpus's own library.

### The declared version

The widget API version rises **17 → 18**; `solidNodeDocumentVersions` does
NOT move and stays `[1 … 8]`, and `RELEASED_DOCUMENT_VERSIONS` stays
`[1, 2, 3, 4]`. No new document shape is read: what moves is a CAPABILITY a
host may require. A build at 17 mounts an elapsed clocked document, renders
it truthfully at its initial bank, and refuses every request that would make
it run — with no way for a host to tell the two builds apart except by
trying. That is precisely the case the version exists to answer without
trying, and this cycle is the clean case that shows the two declarations are
independent: a capability gate moving while the schema list stands still.

## Consequences

**The census closes: 76 of 76 steps, 722 of 722 recorded numbers, 30 of 30
machines, no departure and no deferral.** Agreement is EXACT — every
comparison `toBe` against the corpus's own `tolerance.float` of `0.0` — and
**not one operation disagreed**: the three clock machines replayed bit for
bit at the first run after the backwards refusal went into the producer's
position, `Regulator`'s `0.49999999999999994` landing included. Nothing was
widened, no fixture edited and no scenario skipped. The census is now read
off the REPLAY itself (the replay accumulates what it actually compared), so
a later build cannot narrow the suite by declaring a departure without
failing there, while the head-of-file census stays derived from the FILE —
the three clock machines are still named by a `move` whose input is that
machine's own `clocked.clock`, now as the machines this build must EXECUTE.
One exactness test is added in the shape of the two that exist: `Regulator`'s
first landing moved by ONE representable value must turn the replay red.

**A played frame costs a small fraction of the frame budget.** Three runs
each, printed by the tests themselves:

| `Regulator`, in thread | ms | events |
| --- | --- | --- |
| one frame at ×1 (`by` 0.0167 s) | 0.14 / 0.03 / 0.02 | 0 |
| one frame at ×60 (`by` 1 s) | 0.16 / 0.06 / 0.06 | 1 |
| one frame at ×3600 (`by` 60 s) | 3.20 / 1.10 / 1.56 | 60 |
| one CAPPED stalled frame (`by` 240 s) | 8.52 / 10.45 / 5.53 | 240 |
| per EVENT | 0.0355 / 0.0435 / 0.0231 | — |

| `Regulator`, in Chromium (SOLVE AND POSE) | ms |
| --- | --- |
| one frame at ×1 | 0.300 / 0.300 / 0.400 |
| one frame at ×60 | 0.400 / 0.500 / 0.400 |
| one frame at ×3600 | 1.500 / 1.800 / 1.000 |
| the POSE alone | 0.200 / 0.300 / 0.300 |

Each page number is asserted under ONE 16 ms frame budget, which is what
makes the main-thread decision falsifiable. The whole-corpus replay is
**15.5 ms for 76 steps over 30 machines**, against ADR-062's 13.6 ms for 68:
eight more steps — including the 5 + 3 + 4 events of the three clock
machines — for 1.9 ms more, with the per-step cost unchanged (0.200 →
0.204 ms). **No corpus machine was added for these**: the corpus is the
framework's, and the speed ladder supplies the event rate. **Nothing here is
compared with the running Curta**: a clock request is not a tick, and
`Regulator` is not the Curta, which has no clock at all.

**One assertion floor was widened, to the design's own ratified number.** The
×3600 frame measures 1.1 ms alone and 6.5 ms under a full parallel vitest
run, so the 4 ms floor the file's GESTURE measurements use failed on load.
The frame assertions are held against **16 ms — the frame budget this
cycle's design ratifies for this claim** — with the reason written into the
test. No other floor moved. This is ADR-062's recorded load-sensitivity
risk materialising, and it is recorded rather than quietly absorbed.

**An elapsed version 8 model with geometry RUNS in a real page.**
`tests/fixtures/regulator/` is the framework's own
`tests/clocked_project/pendulum.py:Regulator` exported verbatim
(2 116 bytes, md5 `2f3fbfa80f4f125c5915c7f4ae74cc66`, one driver, one state,
one committing relation on the clock, no bound at all) — a bob posed by
`12·sin(360·time/2)`, a formula of the BANK, and a count committed twice a
period. In Chromium it opens at `t = 0` with `count = 0`, the transport
present and stopped, no scrub, and no positional handle for the clock; PLAY
for one wall second at ×1 advances the clock to a real instant and the count
follows the MACHINE'S OWN LAW (`count == int(time + 0.5)`) rather than a
number the test invented; PAUSE holds the bank value for value; a 2 s STEP
advances the clock by exactly 2.0 s and the count by exactly 2; RESET
returns the bank, stops the transport and returns the bob to the rest
picture byte for byte; two instants differ in pixels, so the pose really
follows the bank; a backwards request is refused by kind and by name with the
bank standing; a refused frame pauses and reports once; and a host with the
chrome suppressed runs the clock from the handle with no transport pixels.
Two screenshots are kept as evidence. Two pixel claims are deliberately NOT
made, for the machine's own arithmetic rather than any weakness of the
evidence: the bob's angle returns to zero at every whole second, and a step
of exactly 2 s is exactly one period.

**A harness fact worth carrying**: the renderer keeps no drawing buffer
between frames, so a canvas read from a TIMER returns a cleared canvas and
every picture matches every other. Every picture in this suite is taken
inside a `requestAnimationFrame` callback, after the widget's own loop has
rendered that frame. ADR-062's suite never met this because every one of its
shots followed a synchronous request.

**Nothing of the run changed, and it is asserted by diff.** Not one line of
`src/run/run.ts`, `worker.ts`, `runtime.ts`, `jumps.ts` or `edges.ts`;
`running-corpus.json` byte for byte (md5
`651a3b5750c49eecad4587438dc9a85a`); `capture.py` and `bundle.py` untouched.
The capture still photographs a clocked document at its INITIAL bank and
never plays, and `--time` still addresses `$t`. Versions 1–7 load, pose,
animate, drive and run exactly as they did, `run()` stays `null` for a
version 8 document and `machine()` stays `null` for every other, and nothing
of the framework, of another checkout or of the document's shape was
altered. **The development page and the studio need no hook**: the transport
is inside the widget.

**Five warts are recorded for the pilot, and none was worked around.** Four
belong to the producer: what an instruction MEANS under a clocked root
(ADR-128 §14 publishes the table and gives it no runtime meaning; the chrome
lists each one disabled with the reason); a CLIP in time and a chain that
follows the clock (ADR-127's own recorded narrowing — this cycle mirrors the
refusal rather than anticipating the later cycle, whose first task is
settling ADR-126's contested direction test for a level periodic in time);
TWO IDENTITIES for one machine (ADR-062's F2, reproduced exactly by this
cycle's fixture, whose `clocked.identity` `281dfdc2…` differs from the
corpus's `2e172caa…` while every other field of both `clocked` objects is
identical); and a MULTI-INPUT request moving a driver and the clock together
(ADR-125's narrowing, asked for by nothing yet). The fifth is a limit of this
decision: `max_crossings` bounds a played frame, and the refusal **cannot
name the speed to drop to** — computing the largest admissible speed would
need the event RATE, which the machine does not publish. The refusal names
the split and pauses; a maker's remedy is a lower speed.

**The suites.** `npx tsc --noEmit` clean; `npx vitest run` **45 files, 1168
tests, green** (from 44 / 1139); `pytest tests` **173 passed, 18 subtests, no
skips** — the bundle built and Playwright present, so nothing was skipped.

**What is left.** The Curta project's own clocked model and its migration;
the PRIMARY checkout's bundle rebuild, which belongs to integration; how the
studio's floor presents a clocked transport, which is the shop's own
follow-up; and the narrowings above, which are the producer's.

## Alternatives considered

- **A separate `advance(seconds)` verb on the handle.** ADR-127 rejected
  `sim.advance(seconds)` on the producer side for reasons that hold here
  unchanged: it would carry its own return type, ordering rules and
  documentation, all copies of `move`'s, and it could not say "advance to
  exactly `t = 10`" without a second argument that is `to=` under another
  name. The corpus scripts `{"move": {"input": "time", …}}`, so a second verb
  would also make the replay translate.
- **Clamping a backwards request to zero travel.** It reads as forgiving and
  it is a lie: a stop reports a bound the machine MET, and no bound was met.
  ADR-127 draws that line and the corpus pins it as a refusal.
- **A timeline scrub over elapsed seconds.** It implies a direction the clock
  refuses; dragging left would raise a refusal on every pointer move, and a
  slider that silently ignores half its travel is worse than no slider.
- **A `duration=` on the request**, the shape ADR-127 records as an open
  narrowing. It would put the cadence inside the machine, where the whole
  clocked discipline's point is that there is none; the cadence belongs to
  the page, which is where the frames are.
- **Carrying the fractional remainder**, as the run carries its debt.
  Rejected because a clock request has no quantization to create one: it
  would be a piece of state that could only make ten frames disagree with one
  long one.
- **Refusing a frame that would cross too many surfaces, or firing the burst
  anyway.** Both were rejected in favour of a cap that loses wall time
  VISIBLY: the readout falls behind the clock on the wall, which is a thing a
  maker can see and reason about, where a burst is a stall and a refusal
  stops the watch for a reason the maker did not cause.
- **Narrowing `declaredNames` so the clock is not a legal name at all.** The
  clock is a bank id and is legal in a commit's level, in a commit's law and
  in the tree's own pose expressions. The refusal belongs on a CONSTRAINT's
  chain, which is the only place the fact is true.
- **Leaving "nothing stops a clock" to fall out of the compile.** It does
  fall out — but an accident that a later refactor could reverse is not a
  promise. Stating it, asserting it on a machine that really declares stops,
  and refusing at load what would falsify it are what make it one.

## Review (2026-09-17)

Accepted at the cycle's adversarial review with no closure. The reviewer
re-ran `npx tsc --noEmit` (clean) and the clocked and running-corpus suites
(187 passed), and inspected both `Regulator` screenshots. The ratified 16 ms
frame floor and the kept `clockMoves` helper stand as reported. Two chrome
nits raised at that review were fixed during completion, each red first: an
integer state's readout (`5.0000` → `5`), and the posed driver panel standing
behind the clocked one — which turned out to be ADR-062's defect rather than
a layout accident, and is now a stated decision above.
