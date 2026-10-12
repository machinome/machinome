# ADR-064: A clocked instruction is one request, drawn over its duration

**Status:** Accepted

**Date:** 2026-09-17

**Change:** `play-the-instruction`

**Amends:**
- [ADR-062: The viewer executes a clocked machine in thread, and a declared stop clips the request before any event](ADR-062-the-viewer-executes-a-clocked-machine-in-thread.md)
  — its §"declared instructions are LISTED and DISABLED"

**Extends:**
- [ADR-062: The viewer executes a clocked machine in thread, and a declared stop clips the request before any event](ADR-062-the-viewer-executes-a-clocked-machine-in-thread.md)
- [ADR-063: The clock is an input a request moves, and one rendered frame is one request](ADR-063-the-clock-is-an-input-and-a-frame-advances-it.md)

**Builds on:**
- [ADR-045: The run executes in a worker and the main thread only poses](ADR-045-the-run-executes-in-a-worker.md)
- [ADR-047: The corpus is what makes the two runtimes one algorithm](ADR-047-the-corpus-makes-the-two-runtimes-one-algorithm.md)
- [ADR-048: Running controls submit requests; nothing binds back](ADR-048-running-controls-submit-requests.md)

**Consumes:**
- solid-node ADR-129: an instruction under a clocked root is one request, and
  the consumer draws it

## Context

ADR-062 brought the version 8 clocked machine into the browser — the bank,
the request, the event solve, the commit, the clip at a declared stop, one
pose per request — and ADR-063 made the CLOCK an input a rendered frame
advances. Each left the same thing behind, and said so: a clocked root
publishes its declared instructions and, under solid-node ADR-128 §14, the
table had NO runtime meaning. ADR-062's chrome therefore **listed the buttons
and disabled them**, and `ClockedMachine.trigger` refused by name
(`src/clocked/machine.ts:402-408` on the base). The gap is recorded in this
repository's own `workflow/warts.md`, under both cycles, as "what an
instruction MEANS under a clocked root".

**The originating project is the Curta**
(`projects/Calculators/Curta-Type-I-3x`, branch `direct-operation`,
read-only here; the clocked model's own record is
`simulation/docs/clocked-spike-2026-09-16.md`). Its clocked sibling builds
`_build/clocked_curta/viewer.json` — a version 8 document of 952 464 bytes,
23 drivers, 18 states, 39 committing relations, 35 bounds,
`clocked.clock: "time"` — and declares exactly ONE instruction:

```json
"instructions": {"Turn crank": {"by": {"crank_rotation": 360}, "duration": 2}}
```

That button was dead. The only way to turn that crank in a browser was a
nudge or a typed value: one request, the crank jumps 360°, every tooth and
carry fires, the tree poses ONCE, and nothing is seen moving. Beside it sits
the project's posed sibling `_build/fast_curta/viewer.json` (version 4, 8
drivers, 7 instructions, `'Turn crank'` targeting `crank_turns` 1 over 6 s),
which ANIMATES, because `Ramp` (`src/drivers.ts:64-85`) interpolates the
driver linearly over the duration and the render loop poses each frame.

The pilot's requirement, verbatim:

> I need it to be animated fast between states with smooth transition just
> like the fast_curta, but holding state.

solid-node's **ADR-129** closed the producer's half on the same day and
handed this one everything it needs: an instruction under a clocked root MEANS
one request — `by` a `move(id, by=travel)`, `targets` a `move(id, to=value)`;
`trigger` RETURNS that request; an instruction there names exactly ONE driver,
refused where the machine is compiled, so *published implies playable*;
`Request` gained `origin` and `end`, the two ends of the path it travelled,
verbatim from the bank; the declared `duration` is carried and silent — what
it says is **how long a CONSUMER draws the transition**; and the conformance
corpus records a `trigger` step, so what a BUTTON does is contract and not
merely what `move` does.

The decision about HOW is the pilot's and was taken before this cycle opened:
**the machine runs ONCE per gesture, before the first frame; the viewer DRAWS
the returned transition over the instruction's duration; no machine work in
the frame loop.** The discipline is `AGENTS.md`'s evidence rule — every
feature needs a project asking for it — and it struck a cancel, a pause and a
scrub for a drawing, a `done` promise on the handle, easing, a drawing over
the clock or over several inputs, and any playback hint in the document.
Nothing asked for one.

## Decision

**A declared instruction is ONE REQUEST, made once at the press, and what the
page does afterwards is DRAW the transition that request reports.**

### `trigger` executes, where the producer put it

`ClockedMachine.trigger(name)` resolves the instruction from the table the
loader already read (`document.ts:177`), takes its ONE entry, and delegates:

| declaration | request |
| --- | --- |
| `by: {id: travel}` | `move(id, {by: travel})` |
| `targets: {id: value}` | `move(id, {to: value})` |

and RETURNS the `ClockedRequest`. Nothing converts, rounds or clamps on the
way — `move` performs the one `native()` conversion (`machine.ts:113-117`), so
an integer driver rounds once, in the one place it rounds, and the half-to-even
agreement with the producer is INHERITED rather than re-stated. `trigger`
leaves ADR-062's cadence refusals; `rate` and `step` go on refusing by name
with their own messages, and an unknown instruction is refused listing the
declared ones. **No new handle verb**: `MachineHandle extends ClockedMachine`,
so the host API gains a meaning and not a member.

### `origin` and `end`, mirrored field for field

`ClockedRequest` mirrors the producer's `Request`, so it gains the same two
fields with the same names and the same units: `origin`, the value the moved
input held when the request began, the bank entry verbatim; `end`, the CLIPPED
target, which is where the bank stands afterwards. Both NATIVE, as every
commit's value already is, while `admitted` stays DESIGN — the producer's own
asymmetry, documented in one sentence of the interface as it is there. They
are REPORTED, never recomputed: the drawing reads `end` rather than
`origin + admitted / scale`, which is ADR-128's one-authority rule reaching a
value object.

### The drawing is a pure module that holds no machine

`src/clocked/drawing.ts` — no DOM, no three.js, **no machine** — is the whole
rule:

```ts
drawing(request, start, duration, integer): Drawing
Drawing.advance(elapsedSeconds): DrawnFrame   // elapsed is TOTAL, as Ramp takes it
Drawing.land(): DrawnFrame
DrawnFrame = { value, bank, moved, done }
```

It is handed the request, the bank the machine stood at BEFORE it, and the
declared duration. That it takes no machine is the **structural half of "one
solve per press"**: the frame loop's collaborator has nothing to solve with,
so a later edit cannot quietly put a request back in the loop. It is also why
the rule is decided and tested in plain node, where `clockedControls.ts` and
`bounds.ts` already are, rather than only in a browser.

`viewer.ts` holds at most ONE drawing beside the clock's transport state and
advances it in the render loop, in the same place and for the same reason
`clockFrame` runs there: the loop already knows the wall seconds since the
last frame. Each frame poses through the change set that already exists,
`tree.update(clockedScope(bank), posed(moved))`, so only the nodes the moved
ids reach are re-evaluated. **What a frame of a drawing costs is a POSE.**

### Commits are keyed on the FRACTION

Every `ClockedCommit` carries a `fraction` of the clipped path and a landing
`value`; either could select which commits a frame has passed. The drawing
keys on the **fraction**, for three reasons that are each testable: the
fraction rises from 0 to 1 whichever way the input travels, so a DOWNWARD
transition is drawn by the same line with no case analysis; it is exact where
a drawn whole-number value is quantised, which a value comparison would let
apply a commit a frame early or late; and it is the producer's own number for
"where on the path", pinned by the corpus for every commit of every machine. A
request whose span is zero reports `fraction: 1` for its commits by the
producer's rule, so such a transition lands them at the end of its drawing.

### The drawn value: `Ramp`'s rule, and one deliberate difference

Linear, as `Ramp.valueAt` is — the pilot asked for "just like the fast_curta",
and `Ramp` neither eases nor scales. Endpoints are contract and the values
between are sampling, also as `Ramp` has it: at or past the duration the value
is the request's own `end` ITSELF, so the last frame stands on the float the
machine stands on.

The one difference is a whole-number input. `Ramp` adds `Math.floor(delta)`,
which on a FALLING ramp overshoots by up to one native unit — a drawn value
past the machine's own `end`, showing a tooth the machine never turned. The
drawing **truncates toward the origin** instead: identical to the floor for a
rising travel, which is every posed instruction this package has ever played,
and never past `end` for a falling one. `Ramp` itself is untouched; a posed
document's ramps are not this cycle's business.

### The duration is WALL seconds, and the playback speed does not scale it

The clocked chrome does carry a speed, but ADR-063 gave it exactly one
meaning: how fast a SECOND OF THE MACHINE'S OWN TIME is watched. An
instruction's duration is not machine time at all — ADR-129 §4 says the
machine does not read it, and a machine with no clock has no transport and no
speed while still declaring instructions. So a drawing runs on wall seconds at
the declared duration, exactly as the posed `Ramp` does, which is also what
"just like the fast_curta" means. Recorded as a reversible working assumption:
scaling it would be one multiplication.

### One solve per press, and the end pose that is computed but never seen

A request POSES the tree as part of itself — ADR-125's atomicity, implemented
here through the machine's `pose` hook so a tree that refuses the new bank
leaves the bank standing. So `trigger` necessarily poses at the transition's
END before it returns. The drawing does not start from there: `trigger` returns
inside the press's own task, and frame 0 — the start bank, the input at
`origin` — is posed immediately after, in the same task, before the browser
paints. The end pose is COMPUTED (and may refuse the request, which is the
point) and never seen. Nothing in `machine.ts` changes for this.

**The bank is therefore FINAL from the press**: a readback during a drawing
reports the transition's end. That is the honest answer and the only one that
does not invent a second bank — what the drawing holds is a picture of a
transition that has already happened. It is stated in the requirement, in the
interface and here, because it will surprise someone.

### One authority over the pose: everything else LANDS the drawing

A drawing owns the pose while it runs. Anything else that would move or repose
the machine — another press, a handle gesture, a host's `move`, `restore`,
`reset`, the clock's own frame, a `dispose` — LANDS the drawing first, the
drawn pose taking the transition's end, and then acts. The machine has ALREADY
made the transition, so landing it loses nothing and every gesture acts on a
bank the maker can read. **Two presses are two strokes**: the first drawing
lands, the second request is made from the bank it left, and the crank ends at
720°.

**Starting a drawing PAUSES the clock's transport** where the machine declares
one, and does not resume it: a playing clock submits a request per frame, and
two things posing one tree per frame is the one conflict a maker cannot read.
The Curta's clocked build declares `clock: "time"`, so this is the measured
document's own case and not a hypothetical.

### The chrome: pressable, indicating, reporting, and following

`ClockedInstructionControl` loses `disabled` and `reason` and gains
`outcome: ClockedOutcome | null` — exactly what `RunInstructionControl`
carries. `INSTRUCTIONS_DISABLED` is deleted. The button is pressable,
indicates while its drawing runs (`aria-busy`, the running chrome's own
treatment) and reports where it was pressed: `moved 360 deg`, a stop naming
the coordinate and side, or the refusal's own message; `formatClockedOutcome`
needed nothing.

While a drawing runs the panel **FOLLOWS** it through one narrow writer,
`ClockedChrome.follow`, over the decision `clockedFollowing(machine, bank,
moved)` makes in node: which ids a frame rewrites, split into handles and
readouts, each saying what a rebuilt panel would have said. A panel REBUILD
during a drawing — a focus change, a republish — reads `drawnBank ??
machine.state()` and so follows the drawing too; without that it would jump to
the end bank, which the requirement forbids in the same sentence.

### An instruction this viewer could not play is refused at LOAD

`readInstructions` validates, for a version 8 document, exactly what ADR-129
guarantees: exactly one of `targets` and `by`; exactly ONE key in it; that key
a declared DRIVER — not a state, not the clock, not a name nothing declares;
a finite travel; a duration that is a finite number of seconds at or above
zero. Each is refused BY NAME at load, naming the instruction, on the surface
ADR-062 already refuses a malformed `clocked` object on. The producer's compile
refuses every one of these before a document exists, so a document carrying one
is not a document with a quirk — it is one this viewer cannot trust to say what
a press means. Refusing at load keeps the invariant the producer bought: every
instruction a loaded version 8 document carries is one a maker may press, and
the chrome needs no arity logic. Zero IS a duration and is accepted; it lands
at once.

### The posed `trigger` is refused under a clocked document

`ViewerHandle.trigger` ramps the DRIVER STORE. A version 8 document still
reconciles that store but is posed from the machine's BANK, so those ramps move
nothing anybody can see: today a silent no-op, and after this cycle a trap —
one handle, one word, two meanings, and the wrong one does nothing at all. It is
refused by name, naming the driver table and pointing at
`machine().trigger(name)`. This is the one surface the Curta does not itself
require, and it is included because this cycle CREATES the ambiguity.

### The declared version

The widget API version rises **18 → 19**. Playing a declared instruction is a
capability a host may require before mounting: a build at 18 lists the same
button and refuses it, which is a working page with a dead control rather than
a loud failure, and no host can tell the two apart except by trying.
`solidNodeDocumentVersions` does NOT move and stays `[1 … 8]` — ADR-129 changed
no field, no key and no version, and a version 8 document published after it is
byte for byte the one published before — and `bundle.py`'s
`RELEASED_DOCUMENT_VERSIONS` stays `[1, 2, 3, 4]`.

## Consequences

**The corpus grew and closed again, exactly.** `src/clocked-corpus.json` is the
producer's regenerated file byte for byte — **145 673 bytes**, md5
`bc4174cf47f844b035125ed3afcee3aa`, `"tolerance": {"float": 0.0}` — against
139 262 bytes and md5 `852b86b8…` before:

| | before | after |
| --- | ---: | ---: |
| machines | 30 | 30 |
| steps | 76 | **81** |
| recorded numbers | 722 | **917** |
| machines with bounds / their steps | 13 / 36 | 13 / **41** |

All **81 steps over all 30 machines** replay bit for bit under `toBe` with the
tolerance read from the file, the two `trigger` steps included and `origin`
and `end` compared on every one of the **65 recorded requests**. The census is
derived from the file, and the closing census is read off the REPLAY, so a
later build cannot narrow the suite quietly. `Calculator` step 14 (the trigger)
and step 16 (the same request by hand from the same restored bank) are equal
field for field and both reproduced, which pins "an instruction is a request
and nothing else" in this runtime too. **No operation was widened and no corpus
value was edited.**

**A pressed instruction costs what the same request costs.** In thread, both
paths warmed and timed ALTERNATELY, median of 40, three separate runs:

| | run 1 | run 2 | run 3 |
| --- | ---: | ---: | ---: |
| `move('crank', {by: 360})` | 0.1340 ms | 0.1349 ms | 0.1274 ms |
| `trigger('Stroke')` | 0.1457 ms | 0.1248 ms | 0.1140 ms |
| difference | +8.7% | −7.5% | −10.6% |

The SIGN changes between runs: the two are the same request within this
bench's noise, which is what "an instruction is a request and two dictionary
lookups" predicts. The producer measured its own at +0.22%.

**The Curta's clocked stroke can be watched, and the per-frame pose is not the
problem.** Measured on the project's own two builds, served through a directory
of SYMLINKS so nothing was copied into this repository, in one browser session,
with an IDLE phase on the same page first so a frame of a DRAWING can be told
from a frame of that page:

```
the CLOCKED Curta's 'Turn crank' (2 s):
  mounted in 0.72 s; one solve 47.60 ms
  IDLE (no drawing): 20 frames over 6.61 s (3.0 fps), median 3.30 ms
  DRAWING: 5 frames over 2.52 s (2.0 fps), median 12.50 ms,
           worst 13.70 ms, 5 distinct poses drawn
  the POSE, by difference: +9.20 ms a frame

fast_curta's 'Turn crank' (6 s, posed Ramp):
  mounted in 0.63 s; one solve 0.00 ms
  IDLE (no drawing): 20 frames over 6.74 s (3.0 fps), median 3.60 ms
  DRAWING: 18 frames over 6.76 s (2.7 fps), median 13.10 ms,
           worst 21.10 ms, 19 distinct poses drawn
  the POSE, by difference: +9.50 ms a frame
```

**The clocked pose — 41 bank values over a 39-commit machine — costs 9.20 ms a
frame, and the posed `fast_curta`'s ramp over 8 drivers costs 9.50 ms** on the
same page in the same session. The clocked pose is NOT more expensive than the
posed one, and it is inside a 60 Hz budget.

What is NOT inside a frame budget on this host is the PAGE: it runs at
**3.0 fps while idle**, before anything is drawn — headless Chromium on
`swiftshader` software rendering with 54 MB of meshes. The drawing does not
move that (2.0 fps against 2.7 fps, over 5 and 18 frames, too few samples to
separate). **That frame rate measures the software rasteriser, not this
cycle**, and it is recorded rather than explained away: the number on a machine
with a GPU is not known from here. For a document this host CAN render at
60 Hz, the committed acceptance's own number is the honest one:

```
calculator drawing: 120 frames over 2.02 s (59.4 fps),
  per-frame pose median 0.40 ms, worst 1.30 ms
```

**The acceptance is a real page.** `tests/fixtures/calculator/` was re-exported
from the producer's own `tests/clocked_project/calculator.py:Calculator`, which
now declares `'Stroke'` (by crank 360 over 2 s) and `'Set four'` (targets
operand 4 over 0.5 s), through a THROWAWAY COPY of the read-only producer
worktree — 15 159 bytes, md5 `d1d1aad665d22a734767ca7a7bdb5872`. In Chromium,
sampled per animation frame: the button is pressable and `aria-busy` from the
instant of the press; the FIRST frame reads the transition's ORIGIN (`crank` 0,
not 360) although the machine already stands at 360; the crank's panel reading
rises monotonically over **120 frames** to 360; **`machine.state()` is the SAME
bank at every one of those 120 samples** — one solve, proved rather than
asserted; **the landing equals one `move('crank', {by: 360})` from the same
start, bank for bank** (`admitted` 360, `origin` 0, `end` 360, one commit) and
the panel equals the bank; two presses leave `crank` 720 and `w0.digit` 2; a
gesture on another handle and a `restore` each land the drawing first; the
posed `viewer.trigger('Stroke')` is refused by name; and an unknown name is
refused listing `Set four` and `Stroke`. Two screenshots are kept:
`tests/_shots/clocked-instruction-mid-stroke.png` (crank **171 deg**, operand
4, the `Stroke` button highlighted and busy, the outcome reading `moved 360
deg`) and `clocked-instruction-landed.png` (crank **360**, no longer busy).

**One claim the committed acceptance cannot make, stated rather than dressed
up.** `'Stroke'` is `by crank 360` from rest and this machine's stroke relation
fires exactly at 360 — the corpus's own `fraction: 1.0` — so `w0.digit` reads
`0` at every sampled frame and `1` at the frame that reaches the end. The
MID-PATH fraction rule (0.25 and 0.75, rising and falling) is pinned in
`src/clocked/drawing.test.ts` instead.

**The suites.** `npx tsc --noEmit` clean; `npx vitest run` **46 files, 1218
tests, 30.2 s, green** (from 45 / 1168 / 31.9 s); `pytest tests` **176 passed,
18 subtests, 183 s, no skips** — this host has the Curta's builds, so the
measurement ran rather than skipping. `dist/solid-widget.js` **800 054 B →
804 744 B**. One existing test moved with the corpus and is recorded rather
than buried: `src/clocked/cost.test.ts`'s whole-corpus budget went red on
`expected 81 to be 76`, gained the `trigger` verb in its own loop (a pressed
instruction is one request, so it belongs in the measured loop) and now
replays **81 steps over 30 machines in 11.4 ms**.

**What did NOT change, shown rather than claimed.** `git diff --stat` over
`src/run/`, `src/drivers.ts`, `src/tree.ts`, `src/controls.ts` and
`src/runControls.ts` is EMPTY: the worker, the program, the posed `Ramp`,
`toNative` and the running chrome are byte for byte what they were, and
`src/running-corpus.json` is untouched (md5 `651a3b57…`) with `src/run` plus
the running corpus green at 14 files and 366 tests. **ADR-063's clock transport
keeps its own shape**: one `move(clock, {by})` per rendered frame, its cap, its
speed ladder and its step are unchanged — a clock has seconds to spend per
frame and a request has a path, and this cycle does not make one the other. The
run's worker, document versions 1–7, the document's shape and the framework are
untouched, and `documentVersions` and `RELEASED_DOCUMENT_VERSIONS` are asserted
unchanged.

**Two findings for the pilot, neither worked around.**

- **`dispose()` does not remove the clocked panel.** Pre-existing, ADR-062's:
  `dispose` removes `driverChrome` and `runChrome` and never `clockedChrome`,
  so two mounts on one host stack two panels. It muddied this cycle's
  screenshots, which now clear the host first. NOT fixed here — it is not this
  cycle's surface.
- **A machine's identity does not cover its instruction table.** The
  re-exported calculator's `clocked.identity` is UNCHANGED (`979b1a0e…`)
  although the class gained two instructions: an instruction table is not part
  of what `Clocked.described` hashes. Producer-side, and beside the identity
  finding this repository already records (a machine's identity is not a
  function of the machine).

**What ADR-062 recorded as open is now closed.** "What an instruction MEANS
under a clocked root" — recorded in `workflow/warts.md` under both ADR-062 and
ADR-063 as the producer's open question — is answered by ADR-129 and
implemented here. This ADR amends ADR-062's "declared instructions are LISTED
and DISABLED" accordingly: they are listed and PRESSED.

## Alternatives considered

- **Slicing an instruction into per-frame requests on the driver.** The pilot
  rejected it and the originating project measured why: one stroke of the Curta
  costs **0.07875 s** in Python and **36.95 ms** in Chromium, while the same
  stroke made as 20 requests with a pose each costs **1.56363 s** and
  **647.7 ms** — and a two-second instruction at 60 fps is 120 slices, not 20.
  The pilot's reason is structural rather than arithmetic: it puts the machine
  back in the frame loop, which is the `operating_curta` shape the whole clocked
  discipline exists to replace. ADR-063's per-frame clock transport is not a
  precedent for it: a clock has SECONDS to spend per frame, and a request has a
  PATH.
- **A drawing inside `machine.ts`.** The machine is a pure synchronous library
  the corpus replays in thread; a frame is a page concern. ADR-063 drew that
  line for the clock's transport and it holds here.
- **Keying commits on the committed VALUE instead of the fraction.** It needs a
  `<=`/`>=` case analysis for a downward transition, where one of the two can be
  wrong, and it disagrees with a quantised whole-number value by a frame in
  either direction.
- **Rebuilding the panel every frame**, as every clocked gesture does today and
  as the clock's transport does 60 times a second. The Curta's panel is 23
  inputs and 18 readouts, several hundred elements, and this cycle claims a
  frame costs a pose; it would also destroy focus and selection while a maker
  watches.
- **Leaving the readouts at the final bank** for the length of a drawing. They
  would disagree with the model throughout, which is the confusion the panel
  exists to prevent.
- **Refusing a gesture while a drawing runs**, as the running root refuses an
  instruction whose input the previous press still owns. That rule exists
  because a RUNNING command owns an input over TIME; a clocked request owns
  nothing after it returns, so refusing would only make a maker wait out a
  picture.
- **Queueing presses.** A queue is a program, and sequencing is the G-code
  layer's job — the sentence ADR-129 quoted when it refused multi-input
  instructions.
- **Scaling the duration by the playback speed.** The speed means machine time
  (ADR-063) and an instruction's duration is not machine time; `fast_curta`'s
  own posed ramps ignore the speed control today. One multiplication if the
  pilot wants it otherwise.

## Review (2026-09-17)

Accepted at the cycle's adversarial review with no closure. The reviewer read
`src/clocked/drawing.ts` and the mid-stroke screenshot (the calculator at crank
171, `Stroke` busy, the outcome reading `moved 360 deg`), and accepted the four
decisions the implementation had to make where the design did not: `advance`
takes TOTAL elapsed rather than a delta (`Ramp.valueAt`'s own convention); frame
0's `moved` is diffed against the request's END bank, because that is where the
tree stands when a drawing begins and a start-bank diff would leave frame 0
posing nothing; a panel REBUILD during a drawing follows the drawing; and the
drawing takes the fourth argument `integer` that design §3's own signature
already carries.
