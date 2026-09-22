# ADR-073: A gesture is drawn at the tempo its input's declared instruction states

**Status:** Accepted

**Date:** 2026-09-17

**Integration note:** Originally numbered ADR-066 on its pre-rename branch;
renumbered ADR-073 when integrated after the Machinome host-contract ADR-066.
The API 19 and document-version 8 statements below describe that branch's
implementation state. The integrated viewer declares API 24 and reads
document versions 1–11.

**Change:** `draw-at-the-declared-tempo`

**Amends:**
- [ADR-065: Every request the clocked panel makes is drawn, over a duration of the viewer's own](ADR-065-every-request-the-clocked-panel-makes-is-drawn.md)
  — its §"the duration is 0.2 s, whatever the travel"

**Extends:**
- [ADR-064: A clocked instruction is one request, drawn over its duration](ADR-064-a-clocked-instruction-is-one-request-drawn-over-its-duration.md)
- [ADR-065: Every request the clocked panel makes is drawn, over a duration of the viewer's own](ADR-065-every-request-the-clocked-panel-makes-is-drawn.md)

## Context

**The crank moved and the digits still teleported.** ADR-065 shipped in
the morning; the pilot went back to the studio floor, nudged the Curta's
crank and reported:

> now the crank moves as expected. but the digits teleport, I expected a
> transition there too.

The digits are not a second control and they are not undrawn. They are
drawn by exactly the machinery that draws the crank, in the same frames
— and the whole transition they make falls INSIDE one of those frames.
The Curta's own laws say how narrow it is
(`projects/Calculators/Curta-Type-I-3x/simulation/cycle.py`, READ-ONLY):

```python
TOOTH_PITCH = 11.25                                          # cycle.py:7

def tooth_passage(angle, count, end):                        # cycle.py:38-42
    """A tooth train advances at 72 / 11.25; a zero row remains stationary."""
    denominator = max(1, count)
    return count * clamp01((angle - end + TOOTH_PITCH * count) /
                           (TOOTH_PITCH * denominator))
```

A result dial advances `count` teeth over `count × 11.25°` of CRANK
(`dial_positions`, `cycle.py:63-81`). The digit `4` becoming `5` — the
thing the pilot is watching — is a ramp **11.25 degrees of crank wide**.

ADR-065 drew every gesture over `GESTURE_SECONDS = 0.2` wall seconds
whatever the travel. A 360-degree nudge over 0.2 s is 1800 deg/s: on a
60 Hz page, **30 degrees of crank per frame**, twelve frames for the
whole turn. An 11.25-degree ramp inside a 30-degree frame is not drawn
at all.

This is ADR-065's own **open question 1** — *"Is 0.2 s the right gesture
duration for the Curta on the pilot's hardware?"* — answered, and the
answer is that no fixed duration can be right. A gesture's visible
detail scales with the travel it asks for: the same fifth of a second
that makes a one-degree nudge smooth makes a whole turn a slideshow.
What the document already states, and ADR-065 did not read, is a RATE:
the same fixture's `'Turn crank': by crank_rotation 360 over 2 s`.

## Decision

**A gesture on an input a declared instruction states a TRAVEL for is
drawn at that instruction's TEMPO.** The duration drawn is the declared
duration in the proportion the gesture's ADMITTED travel bears to the
declared travel:

```
seconds = duration × |admitted| / |by[inputId]|
```

`GESTURE_SECONDS` keeps its name, its value and most of its reason, and
becomes the **fallback**: an input no declared instruction states a
travel on is drawn over the viewer's own fifth of a second exactly as it
was.

### Both sides of the ratio are design units, so it carries no unit

`ClockedRequest.admitted` speaks DESIGN units by its own documented
asymmetry with `origin`/`end` (`clocked/machine.ts:64-87`), and an
instruction's `by` is design units because that is what a press asks in
(`readInstructions`, `clocked/document.ts:480-548`). The ratio is
therefore unit-free, nothing is converted, and a driver whose `scale` is
not 1 is right for free.

### The travel that counts is the one ADMITTED

A gesture an interlock clips is drawn for as far as the machine went, at
the declared rate — a shorter picture, not a slower one. Scaling by what
was asked would crawl through a clipped stroke, and the outcome already
says in words that it was stopped. Measured on the calculator fixture: a
backwards whole turn the ratchet holds on the last seated tooth admits
−5 deg and is drawn in **0.031 s**, the declared rate on that travel
being 0.028 s, where the 360 it ASKED for would have taken 2 s.

### Only a `by=` instruction is a source, and the FIRST one declared

A `targets=` instruction states a LANDING. The travel it makes depends
on where the input stands when it is pressed: 4 units from one bank, 1
from another, and 0 from its own landing — three rates and a division by
zero. A rate is a travel over a duration, and only `by=` publishes one.
The calculator fixture carries both shapes (`'Set four': targets operand
4 over 0.5 s`, `'Stroke': by crank 360 over 2 s`), so the distinction is
pinned by a committed document rather than by an argument.

Where SEVERAL `by=` instructions name one input, the first in the
document's own key order wins — the producer's declaration order,
preserved end to end (`readInstructions` inserts in `Object.entries`
order; the chrome lists `Object.keys(machine.instructions)`), so it is
the button nearest the top of the panel: a rule a maker can see, stable
under a rebuild. A declared `by` of ZERO states no rate and is skipped;
a declared DURATION of zero states a real one — "this travel is drawn in
no time" — and is honoured, as its own press is.

### There is no cap

A nudge of 720 on an input declaring 360 over 2 s takes 4 s, because
that is the stroke the maker asked to watch at the rate the document
declares. A cap would draw the beginning of a long stroke at one rate
and the end at another — a picture of neither. The handle stays usable
throughout and a further gesture lands the drawing (ADR-064 §8), so a
maker is never held.

### The duration is decided AFTER the answer

`clockedRequest(id, request, draw)` now takes WHETHER this request is
drawn, not how long. How long depends on `answered.admitted`, which does
not exist until the request is made, so the seconds are computed between
the panel's single rebuild and `startDrawing` — the order ADR-064 fixed
is otherwise untouched. The clock's `step()` and `clockFrame` pass
nothing and stay undrawn, so no bank copy is taken for them, exactly as
ADR-065 measured and kept.

### The pressed instruction keeps its own declared duration

A press is drawn over the duration the instruction DECLARES, whatever
travel its request admits — ADR-064, unchanged. The asymmetry is
deliberate: an instruction's duration is a statement about that stroke
and the viewer is not entitled to rescale a declared number; a tempo is
DERIVED only where the document declares nothing for the gesture at
hand. The two agree where it matters — a gesture asking for exactly the
declared travel is drawn over exactly the declared duration, measured at
**1.005** of the press on the same page.

### No API bump

`solidNodeViewerApi` stays **19** and `solidNodeDocumentVersions` stays
`[1 … 8]`. The tempo is read from the `instructions` table this viewer
already loads, validates and lists; no document field is read or written
differently, no host-callable behaviour changes, and a host can neither
require nor detect this through the API. ADR-065's own argument,
unchanged.

## Consequences

**The rule is one exported function and one call site.**
`gestureSeconds(inputId, admitted, instructions)` lives beside
`GESTURE_SECONDS` in `clockedControls.ts`, where the clocked chrome's
other policy numbers live, and `clockedRequest` calls it.
`src/clocked/drawing.ts`, `machine.ts`, the corpus and its replay,
`src/run/`, `src/drivers.ts` and `src/runControls.ts` are byte for byte
unchanged (`git diff --stat` over them EMPTY; corpus md5 still
`bc4174cf47f844b035125ed3afcee3aa`).

**Measured in a real browser on the committed version 8 fixture**, which
declares one `targets` instruction, one `by` instruction and three
inputs named by neither — one bench carrying every case the rule
distinguishes. Six gestures on one page at 60 fps:

| gesture | before (ADR-065) | after |
| --- | --- | --- |
| nudge of the declared 360 on `crank` | 12 frames / 0.20 s | **121 frames / 2.01 s** |
| nudge of 30, a twelfth | 12 / 0.20 s | **11 / 0.18 s** |
| typed 720, twice | 12 / 0.20 s | **241 / 4.02 s** |
| nudge on `operand` (`targets` only) | 12 / 0.20 s | 12 / 0.20 s |
| nudge on `feed` (named by nothing) | 12 / 0.20 s | 12 / 0.20 s |
| PRESS of `'Stroke'` | 121 / 2.02 s | 121 / 2.02 s |

The ratios are what is asserted, on the page rather than as absolutes a
host cannot promise: a twelfth of the travel took **0.091** of the time,
twice the travel **2.000**, the press **1.005** of the gesture of the
same travel. **The tooth passage** is 11.25/360 of the stroke, which is
now **3.8 frames** where it was 0.38 of one.

**The Curta, where the finding came from.** The pilot's own build as
found at run time — version 8, `clocked.clock: "time"`, 23 drivers,
`{"Turn crank": {"by": {"crank_rotation": 360}, "duration": 2}}` —
served through a directory of SYMLINKS, nothing copied. This host
renders its 54 MB of meshes on a software rasteriser at **2.2 fps**, so
both runs below are bounded by the page and not by the rule:

```
the NUDGE of 360, BEFORE: 1 frame over 1.16 s, readings [0, 360]
the NUDGE of 360, AFTER:  3 frames over 2.21 s, readings
                          [0, 245.988, 323.982, 360]
the PRESS of 'Turn crank': 3 frames over 2.10 s -> 2.28 s (unchanged)
```

`[0, 360]` is the teleport the pilot reported, in one line. The harness
can also hand the animation loop timestamps at a stated spacing, which
measures the RULE with this host's frame rate out of the way: frozen two
50 ms frames into the same nudge — what a 20 fps page draws in 100 ms —
the crank stood at **180 degrees** before and **18 degrees** after. A
tenfold finer picture at the same page rate.

**What this host cannot show** is stated plainly rather than implied: at
2.2 fps the tooth passage is 0.09 of a frame after the change and 0.03
before, because 2.2 fps cannot draw a 3% band of any stroke. At 60 Hz
the same tempo is 120 frames a stroke and 3.8 a passage, which the
calculator fixture — rendered at 60 fps on this same host — measures
directly.

**The claims that cannot go red were proved by mutation**, as ADR-065's
were, each reverted afterwards: routing the panel's STEP through a drawn
request stops the transport that asked for it
(`steppedWhilePlaying.playing` false); routing the played frame through
one stops the clock on its first frame (0.067 s instead of a wall
second); giving the MOUNT HANDLE's `move` a drawing at the same tempo
makes the panel read 0 where it must read 360.

**Three reds, none of them buried.** The node policy test went red on a
function that did not exist. The committed browser acceptance went red
on the tempo itself — every gesture 0.20 s whatever the input and
whatever the travel, while the press of the same 360-degree travel
already took 2.02 s — and in two harness details the tempo invalidated:
a photograph's frame budget sized to a fifth of a second, and fixed
60-frame sample loops that no longer reached a landing. Both now measure
the landing rather than a count, which is what they always meant.

**The suites.** `npx tsc --noEmit` clean; `npx vitest run` **46 files,
1219 tests, 36.7 s, green** (the chrome's policy test corrected and
extended, no count change); `pytest tests` **178 passed, 18 subtests,
267.2 s, no skips** — this host has the Curta's builds, so both
measurements ran. `dist/solid-widget.js` 804 950 B → **805 192 B**.

## Alternatives considered

- **Keeping a fixed duration and raising it.** Whatever number is
  chosen, the ratio between a one-degree nudge and a whole turn is
  unchanged: one of them is a slideshow and the other a crawl. A rate is
  the thing the document already states.
- **Deriving a rate the viewer invents** (one design unit per 0.2 s, the
  running chrome's shape). ADR-065 ruled it and the reason stands: it
  draws the Curta's crank nudge over 72 seconds. What is new here is that
  the rate is READ from a declaration rather than invented.
- **Taking a `targets=` instruction as a tempo source.** It states a
  landing, so the rate it implies changes with the bank and is undefined
  at its own landing.
- **Picking the smallest declared `|by|` where several name one input.**
  Invisible in the panel, and adding an instruction would silently retime
  an unrelated input's gestures. Declaration order is what a maker reads.
- **Using only instructions in the FOCUSED layer.** The tempo is a
  property of what the document declares about that input, not of what
  the panel currently shows; a maker who navigates into a sub-assembly
  would otherwise watch the same nudge at two speeds.
- **Scaling by the travel ASKED FOR rather than ADMITTED.** A clipped
  stroke would crawl, its slowness meaning "you were stopped" — which the
  outcome already says in words.
- **Capping the drawn duration.** A long stroke would be drawn at the
  declared rate for its first part and faster for the rest: a picture of
  neither. The handle stays usable and any gesture lands the drawing.
- **Rescaling a PRESSED instruction by what it admitted.** The pilot's
  open question; the answer taken here is no — a declared duration is a
  statement the viewer honours. It is the one place a gesture and a press
  differ for the same clipped travel, and it is reversible.
- **A maker-editable duration, a per-row seconds box, an easing, a cap or
  a floor.** Nobody asked, and the evidence rule says a feature needs a
  named project that needs it now.

## Review (2026-09-17)

Written after implementation, from what was built and measured. No
departure from the ratified design. The two open questions the pilot
answered before implementation — a clipped PRESS keeps its declared
duration, and 0.2 s stays the fallback — are recorded above as decided.
The Curta's own choice of duration is its own: this rule follows
whatever that project declares, and the measurement above reads the
build as it stood rather than as the plan guessed it would.
