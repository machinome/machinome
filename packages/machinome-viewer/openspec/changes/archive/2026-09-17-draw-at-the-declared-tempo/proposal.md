## Why

**The crank moves and the digits still teleport.** ADR-065 shipped this
morning; the pilot went back to the studio floor, nudged the Curta's crank
and reported:

> now the crank moves as expected. but the digits teleport, I expected a
> transition there too.

The digits are not a second control and they are not undrawn. They are drawn
by exactly the machinery that draws the crank, in the same frames — and the
whole transition they make falls INSIDE one of those frames. The Curta's own
laws say how narrow it is
(`projects/Calculators/Curta-Type-I-3x/simulation/cycle.py`, READ-ONLY):

```python
TOOTH_PITCH = 11.25                                          # cycle.py:7

def tooth_passage(angle, count, end):                        # cycle.py:38-42
    """A tooth train advances at 72 / 11.25; a zero row remains stationary."""
    denominator = max(1, count)
    return count * clamp01((angle - end + TOOTH_PITCH * count) /
                           (TOOTH_PITCH * denominator))
```

A result dial advances `count` teeth over `count × 11.25°` of CRANK, at the
sector where the transmission engages it (`dial_positions`, `cycle.py:63-81`).
So a one-tooth advance — the digit `4` becoming `5`, the thing the pilot is
watching — is a ramp **11.25 degrees of crank wide**.

ADR-065 draws every gesture over `GESTURE_SECONDS = 0.2` wall seconds,
whatever the travel. A 360-degree nudge over 0.2 s is 1800 deg/s: **30
degrees of crank per frame** at 60 Hz, twelve frames for the whole turn. An
11.25-degree ramp inside a 30-degree frame is not drawn at all — the digit
stands at its old value in one frame and its new value in the next. The
declared instruction the same document carries, `'Turn crank': by
crank_rotation 360 over 2 s`, gives the same ramp **about four frames**, and
the six seconds the project is moving to (what `fast_curta` has always
declared for its own `'Turn crank'`) give it **about eleven**. Nothing about
the digits changed between those three numbers except how long the crank was
drawn.

This is ADR-065's own **open question 1** — *"Is 0.2 s the right gesture
duration for the Curta on the pilot's hardware?"* — answered, and the answer
is that no fixed duration can be right. A gesture's visible detail scales
with the travel it asks for: the same 0.2 s that makes a one-degree nudge
smooth makes a whole turn a slideshow. What the document already states, and
what ADR-065 did not read, is a RATE: this input travels this far in this
long.

## What Changes

- **A gesture on an input a declared instruction states a TRAVEL for is drawn
  at that instruction's TEMPO.** The duration drawn is the instruction's
  declared duration in the proportion the gesture's ADMITTED travel bears to
  the declared travel: `duration × |admitted| / |by|`. On the Curta, whose one
  instruction is `by crank_rotation 360 over 2 s`, the pilot's nudge of 360 is
  drawn over 2 s — the same stroke the button draws — and a nudge of 30 over a
  twelfth of it. Both are in DESIGN units on both sides of the ratio
  (`ClockedRequest.admitted` says so in its own comment), so the ratio needs no
  scale and carries no unit.
- **`GESTURE_SECONDS` stays, as the FALLBACK it now is.** An input that no
  declared instruction states a travel for keeps the fifth of a second, for
  ADR-065's unchanged reason. That is every input of a document declaring no
  instructions (the committed `tests/fixtures/regulator/`), every input no
  instruction names (`feed`, `ring`, `setting` on the calculator fixture), and
  every input named only by an instruction that states a LANDING rather than a
  travel (`operand`, named by `'Set four': targets operand 4`).
- **Only a `by=` instruction is a tempo source.** A `targets=` instruction
  states where its driver LANDS, not how far it travels: the travel it would
  make depends on where the input stands when it is pressed, so it states a
  different rate at every bank and none at all at its own landing. A rate needs
  a travel and a duration, and only `by=` publishes one.
- **Where SEVERAL `by=` instructions name one input, the FIRST the document
  declares gives the tempo.** That order is the producer's own declaration
  order, preserved by the loader and by the panel's list, so the tempo is the
  one the maker reads first; picking by the smallest or largest travel would
  infer an intent the document never states.
- **There is no cap.** A nudge of 720 on an input declaring 360 over 6 s takes
  12 s, because that is the stroke the maker asked to watch at the rate the
  document declares. A cap would draw the beginning of a long stroke at one
  rate and the end at another — a picture of neither — and the handle stays
  usable throughout, a further gesture landing the drawing as it already does.
- **The travel that counts is the one ADMITTED, not the one asked for.** A
  gesture an interlock clips is drawn for as far as the machine went, at the
  declared rate; scaling by what was asked would crawl through a clipped stroke.
- **The instruction BUTTON is unchanged.** A press is drawn over the duration
  it DECLARES, whatever its request admits (ADR-064). An instruction states its
  own duration and the viewer honours it; a tempo is DERIVED only where nothing
  is declared.
- **Everything else of ADR-064/065 is unchanged**: one solve per gesture, made
  before the first frame; the bank final from the request; each commit at its
  own fraction; the panel following the drawing; the outcome reported where the
  gesture was made; a gesture landing a running drawing; a zero-travel request
  drawing nothing; the clock's transport and the mount handle undrawn; the
  playback speed scaling neither duration. `src/clocked/drawing.ts` is
  untouched.

## Capabilities

### New Capabilities

None. One existing rule — how long an existing drawing of an existing gesture
lasts — is read off the document instead of being a constant.

### Modified Capabilities

- `viewer-package`: **MODIFIED** — "A maker operates a clocked machine on
  screen" (the paragraph stating one short duration of the viewer's own for
  every handle and every travel becomes the declared tempo with that duration
  as its fallback; four scenarios added) and "The viewer plays a clocked
  instruction as one drawn transition" (the sentence carrying the gesture's
  duration; a pressed instruction's own duration stated explicitly as
  unchanged; one scenario added, one existing scenario's body reworded where it
  named the viewer's own duration). Every existing scenario of both
  requirements is carried under its exact title.

## Impact

- `solid_node_viewer/widget/src/clockedControls.ts` — one exported function
  beside `GESTURE_SECONDS` (`:211`): the seconds a gesture on an input is drawn
  over, given the travel admitted and the document's instruction table. The
  constant keeps its name, its value and most of its reason; the sentence
  claiming the duration is "the same fifth of a second whatever the amount"
  (`:186-192`, `:194-211`) is corrected to say where that is now true.
- `solid_node_viewer/widget/src/viewer.ts` — the panel's `move` and `nudge`
  (`:1350-1355`) ask for a DRAWN request rather than passing a fixed number of
  seconds, and `clockedRequest` (`:1133`) computes the duration from the answer
  it already has (`answered.admitted`) before calling `startDrawing` (`:1234`).
  The clock's `step()` (`:1384`) and `clockFrame` (`:1280`) pass nothing and
  stay undrawn, exactly as they do today.
- `solid_node_viewer/widget/src/clockedControls.test.ts` — the policy test at
  `:201-213`, whose title and body say the duration is "the same for every
  travel", is corrected and extended: the tempo arithmetic, the `targets=`
  source that is not one, the fallback, the zero travel, and a declared travel
  of zero.
- `tests/test_calculator_document.py` — `GestureDrawnInABrowserTest`'s nudge of
  360 on `crank` now takes the fixture's own declared 2 s instead of 0.2 s, so
  its 60-frame samples no longer reach the landing: it is RED on this cycle's
  change and is updated to measure the tempo rather than assert the old one. It
  gains the twelfth-travel gesture, the `feed` fallback and the `operand`
  `targets=` fallback.
- `tests/test_curta_drawing.py` — the skippable measurement's `watch(…, 1.0)`
  windows are sized to the tempo, and the numbers recorded beside the declared
  instruction's.
- `CHANGELOG.md` under `0.2.0 — unreleased`; ONE new decision record,
  `docs/adrs/EXPORT/ADR-066`, AMENDING ADR-065; `docs/adrs/README.md`.
- **No API bump** (`solidNodeViewerApi` stays 19, `solidNodeDocumentVersions`
  stays `[1 … 8]`) and **no document change**: the tempo is read from the
  `instructions` table this viewer already loads, validates and lists, and no
  host-callable behaviour differs. ADR-065's own argument, unchanged.

### Non-goals

- The framework, the document schema, the corpus, the machine, the drawing
  module, the run, the posed `Ramp`, the clock's transport, the mount handle.
- A maker-editable duration or rate, a per-row seconds box, an easing, a cancel,
  a progress event, a cap or a floor on the drawn duration: nothing asked.
- Rescaling a PRESSED instruction's declared duration by what its request
  admitted.
- The Curta's own edits: that project is READ-ONLY here, and whether it raises
  its declared duration from 2 s to 6 s is its own decision, which this rule
  then follows.
