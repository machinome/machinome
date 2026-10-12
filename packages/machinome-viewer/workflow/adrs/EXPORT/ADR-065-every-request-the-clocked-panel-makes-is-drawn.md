# ADR-065: Every request the clocked panel makes is drawn, over a duration of the viewer's own

**Status:** Accepted

**Date:** 2026-09-17

**Change:** `draw-every-request`

**Amends:**
- [ADR-064: A clocked instruction is one request, drawn over its duration](ADR-064-a-clocked-instruction-is-one-request-drawn-over-its-duration.md)
  — its §"a gesture on a HANDLE stays one immediate request"

**Extends:**
- [ADR-064: A clocked instruction is one request, drawn over its duration](ADR-064-a-clocked-instruction-is-one-request-drawn-over-its-duration.md)
- [ADR-062: The viewer executes a clocked machine in thread, and a declared stop clips the request before any event](ADR-062-the-viewer-executes-a-clocked-machine-in-thread.md)
- [ADR-063: The clock is an input a request moves, and one rendered frame is one request](ADR-063-the-clock-is-an-input-and-a-frame-advances-it.md)

## Context

**The pilot pressed `+` on the studio floor and the Curta still
teleported.** One day after ADR-064 shipped the drawing machinery, on a
floor serving API 19 and
`projects/Calculators/Curta-Type-I-3x`'s `_build/clocked_curta/viewer.json`:

> I still see instant change when I click to change something in the curta,
> no animation transitioning from one state to another.

ADR-064 drew exactly ONE control: the instruction button. The Curta
declares one instruction — `'Turn crank': by crank_rotation 360 over 2 s`
— and its own record tells a maker to operate it by hand instead:

> In the browser panel, set a selector, set the `crank_rotation` nudge
> amount to `360`, and press `+` repeatedly.
> — `simulation/docs/clocked-curta-2026-09-17.md:42`

`crank_rotation` publishes `range: null`, so that row has no slider at
all: a number field, `-`, `+`, and the amount box. Every one of those
went through `clockedRequest`, which posed ONCE and returned. A 360-degree
stroke — every tooth, every carry — arrived in a single frame, and so did
every gesture on the other 22 drivers, on `carriage_rotation` and on the
eight digit sliders.

The defect was a sentence this repository ratified the day before, in the
requirement "A maker operates a clocked machine on screen" —

> A gesture on a HANDLE SHALL remain ONE immediate request, posed once: a
> duration is something a declared instruction states, and a handle
> declares none.

— and its twin in the code, `clockedControls.ts:188-190`: *"A clocked
request is instantaneous by construction … so a nudge is a travel and
nothing else."* Both confuse ONE REQUEST with ONE FRAME, which is exactly
the distinction ADR-064 exists to draw. The running chrome had settled the
same question from the other side and written the reason into its own
source (`runControls.ts:39-62`, `DEFAULT_NUDGE = {amount: 1, seconds:
0.2}`): *"a nudge that teleports is a nudge nobody can watch."*

## Decision

**Every request a maker's gesture makes on a clocked INPUT is DRAWN, by
the machinery ADR-064 already built, over one short duration of the
viewer's own.**

### One door, generalized from "an instruction" to "a request and a duration"

`clockedRequest(id, request, draw)` now takes the bank BEFORE the request
and finishes through `startDrawing`, in exactly the order ADR-064 fixed:
land the running drawing, take the bank, make the ONE request, write the
outcome, rebuild the panel ONCE carrying that report, start the drawing —
whose frame 0 is posed in the same task — and render. The panel's `move`
(the number field's commit and the slider's) and `nudge` (the `±` pair)
pass the gesture duration; `clockedPlay` stays the instruction's thin
wrapper over the same steps. The bank before the request is taken ONLY
where a drawing will be drawn, so the clock's sixty requests a second
cost no copy they cannot use.

`clockedDrawing.name` becomes an optional INDICATOR KEY, `null` for a
handle's gesture. An instruction BUTTON needs `aria-busy` because nothing
else on it moves; a handle row indicates by the thing the maker is
watching — its own reading and its thumb sweeping under `follow`. No new
chrome surface. `src/clocked/drawing.ts`, `machine.ts`, the corpus, the
run, the posed `Ramp` and `runControls.ts` are byte for byte unchanged.

### The duration is 0.2 s, whatever the travel

One constant, `GESTURE_SECONDS`, beside `DEFAULT_NUDGE` where the clocked
chrome's other policy numbers live. It is the running chrome's own number
and the running chrome's own reason, inherited rather than imported: the
two chromes state their own policy and one already differs, the clocked
nudge carrying an amount and no seconds.

It is a DURATION and never a rate. The running chrome can afford a rate
because its nudge is a travel over SIMULATED time inside a cadence; a
clocked gesture has no cadence, and one design unit per 0.2 s would draw
the Curta's 360-degree crank nudge over **72 seconds**. The playback speed
does not scale it, for ADR-064's own reason: the speed means machine time
and a drawing is wall time. A maker who wants the two-second stroke
presses the declared instruction, which states exactly that.

### There is no live-drag exception, because there is no live drag

The clocked slider listens on `change` ALONE (`viewer.ts:3485`), where the
posed chrome's driver slider writes on `input` (`:3095`). A drag therefore
moves the thumb while the model stands still, and the release is ONE jump
request — precisely the teleport this cycle removes. A track click and an
arrow key are the same one request. So the rule has no exception to state,
and the requirement says "a gesture on a handle" without qualification.

### The clock's own requests are not drawn, and neither is the host's handle

`clockFrame` and the panel's STEP pass a duration of ZERO through the same
door and land at once. The reason is ADR-064's one-authority rule, which
this cycle MEASURED rather than assumed: routing the step through the
gesture duration stops the transport that asked for it, and routing the
played frame through it stops the transport on its first frame (the clock
advanced 1/15 s of a wall second before the page went quiet). A clock has
seconds to spend per frame; a request has a path.

`machine().move(...)` keeps its meaning and gains no `{draw}` option and
no new verb: it is programmatic, the bank is final at the request either
way, and no project has asked. **The panel draws; the handle does not.**
`machine().trigger` remains `clockedPlay`, drawn.

### No API bump

`solidNodeViewerApi` stays **19** and `solidNodeDocumentVersions` stays
`[1 … 8]`. The mount interface, the handle's verbs and their answers are
unchanged, no document field is read or written differently, and a host
can neither require nor detect this through the API: it is the on-screen
behaviour of a control that already worked. ADR-060/061 changed how the
viewer behaves without a bump; ADR-064 bumped because at 18 a listed
button was DEAD, which a host could require the fix for.

## Consequences

**The gesture is drawn, proved in a real browser on the committed version
8 fixture.** `tests/test_calculator_document.py` gains
`GestureDrawnInABrowserTest`, sampled per animation frame. The nudge
amount is set to a whole turn and `+` is pressed: the panel reads **0** on
the gesture's own frame while the machine already banks **360**; the
reading rises monotonically through more than five distinct values to 360;
`machine.state()` is the SAME bank at every one of those frames — one
solve, proved rather than asserted; the landing equals one
`move('crank', {by: 360})` from the same start, bank for bank; and the
canvas at frame 3 differs from the canvas at the end. A typed 720 draws the
second stroke. The ranged, whole-number `operand` draws 1 → 9 by its
slider's commit with **every drawn frame a whole number** that never
passes the end, the thumb following — and the same holds for a REAL
POINTER: the harness clicks that slider's track with the browser's own
mouse and the reading rises from where the input stood, through whole
numbers, to the bank the click made. The host's own `machine().move`
lands at once, the panel reading the end in the same task. Two screenshots are
kept: `tests/_shots/clocked-gesture-mid-nudge.png` (crank **149.94**,
the amount box at 360, the outcome `moved 360 deg`) and
`clocked-gesture-landed.png`.

```
calculator gesture: 60 frames over 1.00 s (60.1 fps),
  per-frame pose median 0.50 ms, worst 3.30 ms
```

**The claims that cannot go red on the base were proved by mutation.**
Nothing draws before this cycle, so "the clock is not drawn" and "the host
handle is not drawn" have no red of their own. Each guard was watched to
fail against a deliberate mutation of the implementation (a drawn step:
`steppedWhilePlaying.playing` false; a drawn played frame: the clock
advanced 0.067 s instead of a wall second; a drawn host handle:
`hostAtOnce.crank` 0 instead of 360), and every mutation was reverted.

**The Curta, measured where the finding came from.** One session on the
project's own clocked build, served through a directory of SYMLINKS with
nothing copied into this repository:

```
IDLE (no drawing): 12 frames over 5.54 s (2.2 fps), median 6.10 ms
the NUDGE of 360 deg (0.2 s): one solve 54.50 ms; the panel read 0 on the
  gesture's own frame, the bank 360; 2 distinct poses; +11.00 ms a frame
the TYPED 720 (0.2 s):      one solve 40.00 ms; 2 distinct poses
the declared 'Turn crank' (2 s): one solve 42.40 ms; 4 distinct poses,
  readings [720, 947.988, 1028.988, 1080, …]
```

The machinery is right on the Curta: one request at the gesture, at the
same 40–55 ms solve ADR-064 measured; the panel reading the transition's
ORIGIN on the gesture's own frame while the machine banks the end; and the
pose costing **+11.00 ms** a frame, which is ADR-064's 9.20 ms within this
bench's noise. What a 0.2 s gesture cannot do ON THIS HOST is be watched:
the page idles at **2.2 fps** — headless Chromium on `swiftshader` with
54 MB of meshes, the 3 fps this repository's `workflow/warts.md` already
records — so a fifth of a second gets ONE frame after its origin and lands
in it. Both distinct poses are endpoints; the ten-times-longer declared
stroke draws four. **That frame rate measures the software rasteriser, not
this cycle** — the calculator draws 60 frames at 60.1 fps on the same host
— and whether 0.2 s is watchable on the pilot's own hardware is a question
only that hardware can answer. Recorded as a reversible working
assumption: the constant is one number in one file. The pictures of the
Curta's own nudge, mid-travel at **crank 180** with the bank at 360 and
landed at 360, are kept OUTSIDE this repository, because a measurement is
not a contract.

**Two findings, neither worked around.**

- **The nudge AMOUNT reaches a row's buttons only at the next rebuild of
  the panel.** `setNudge` writes the setting and rebuilds nothing, while
  the `±` buttons carry the amount their row was BUILT with, so the
  pilot's own sequence — type 360, press `+` — moves **1 deg** the first
  time and 360 after. Pre-existing, ADR-062's; the running chrome keeps
  its amount in a live closure instead. Both new harnesses ARM the amount
  with a reset rather than hiding it, and the finding is in
  `workflow/warts.md`. **Closed at review, in this cycle's own commit:**
  a press now reads the amount the box holds at that instant, so the
  pilot's sequence moves 360 the first time.
- **A value committed with the field still focused loses the element it
  was typed into.** Every request rebuilds the whole clocked panel, so the
  focused `<input>` is replaced and the new one follows the drawing
  (measured: the field reads `30.06` a frame later). The requirement's
  clause is still met and still reachable — a maker whose cursor is in a
  field WHILE a drawing runs keeps what they typed, pinned by an
  acceptance where `42` survives twelve frames of a whole turn — but it
  protects the field a maker moves INTO, not the one they committed from.
  The design's own open item said otherwise and was wrong.

**The suites.** `npx tsc --noEmit` clean; `npx vitest run` **46 files,
1219 tests, 35.3 s, green** (from 1218: the chrome's new policy test);
`pytest tests` **178 passed, 18 subtests, 242.6 s, no skips** (from 176)
— this host has the Curta's builds, so both measurements ran. `dist/solid-widget.js` **804 744 B → 804 870 B**.
`src/clocked-corpus.json` is untouched, md5
`bc4174cf47f844b035125ed3afcee3aa`, and `git diff --stat` over
`src/clocked/drawing.ts`, `src/clocked/machine.ts`, the corpus, `src/run/`,
`src/drivers.ts` and `src/runControls.ts` is EMPTY.

## Alternatives considered

- **Deriving the duration from the amount, at the running chrome's RATE**
  (one design unit per 0.2 s). It draws the Curta's 360-degree crank nudge
  over 72 seconds. A rate belongs to a travel over simulated time inside a
  cadence; a clocked gesture's duration is a picture, not a request.
- **Requesting per pointer move during a drag** (`input` rather than
  `change`). That is the per-frame-request shape ADR-064 measured and the
  pilot rejected; on the Curta it is a 40 ms solve and a pose per pointer
  sample. The clocked slider does not listen on `input` at all.
- **A seconds box on every row, or a maker-editable default.** Nobody
  asked, and a maker who wants a two-second stroke presses the declared
  instruction, which states exactly that.
- **Scaling the gesture's duration by the playback speed.** ADR-064 ruled
  it for an instruction and the reason is unchanged: the speed means
  machine time, a drawing is wall time.
- **Drawing the clock's STEP, or a played frame.** Measured above: each
  stops the transport that asked for it, ADR-064's one-authority rule
  turned against the control that invoked it.
- **A `{draw: seconds}` option on `machine().move`.** No project has asked,
  and the evidence rule says a feature needs one. The bank is final at the
  request either way.
- **Indicating a drawn gesture on its row** (`aria-busy`, as an instruction
  button does). The sweep of the row's own reading and thumb IS the
  indication; a busy state on a row would be a new surface nobody asked
  for. Left open for the pilot.
- **A dated `## Amendment` section inside ADR-064.** The house allows it,
  and its two existing examples (ADR-013, ADR-020) are POINTERS at a later
  decision rather than decisions themselves. This cycle has its own
  context, its own alternatives and its own measurements, and an archived
  change links an ADR.

## Review (2026-09-17)

Written after implementation, from what was built and measured. The two
departures from the design are recorded above rather than quietly fixed:
the design's open item 3 (a typed value committed with Enter keeps its
focus) is false in this chrome, because a request rebuilds the panel; and
the nudge amount's own staleness, found while writing the acceptance, is
filed in `workflow/warts.md` rather than repaired inside this cycle.
