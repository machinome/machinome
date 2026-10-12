## Context

ADR-064 built the drawing machinery; ADR-065 pointed it at every gesture and
gave a gesture one duration of the viewer's own, `GESTURE_SECONDS = 0.2`. The
pilot's finding (proposal, *Why*) is that a fixed duration cannot be right: the
Curta's one-tooth digit advance is 11.25 degrees of crank wide, and at 0.2 s a
360-degree nudge moves 30 degrees a frame, so the ramp the pilot wants to watch
falls inside one frame. The document already states the rate that makes it
visible — `'Turn crank': by crank_rotation 360 over 2 s` — and ADR-065 did not
read it.

This is a one-rule correction to a one-day-old decision. It adds one function
and no mechanism: `src/clocked/drawing.ts`, the machine, the corpus and the
clock are untouched.

## Goals / Non-Goals

**Goals:** a gesture on an input the document declares a travel and a duration
for is drawn at that rate; every other gesture keeps ADR-065's fifth of a
second; no new surface, no document change, no API bump.

**Non-Goals:** the drawing module; the instruction button's own declared
duration; the clock's transport; the mount handle; the framework; a
maker-editable duration; a cap.

## Decisions

### D1. The tempo is `duration × |admitted| / |by|`, in design units

One exported function beside `GESTURE_SECONDS` in `clockedControls.ts`, where
the clocked chrome's other policy numbers live, called by `clockedRequest`
with the answer it already holds:

```
seconds(inputId, admitted, instructions) =
    tempo === null ? GESTURE_SECONDS
                   : tempo.duration * |admitted| / |tempo.by[inputId]|
```

`ClockedRequest.admitted` speaks DESIGN units, deliberately and by its own
documented asymmetry with `origin`/`end` (`clocked/machine.ts:64-87`), and an
instruction's `by` is design units too (`readInstructions`,
`clocked/document.ts:480-548`). The ratio is therefore unit-free and needs no
`scale`: nothing is converted, and a driver whose scale is not 1 is right for
free.

ADMITTED, not asked: a gesture an interlock clips is drawn for the travel the
machine made, at the declared rate. Scaling by what was asked would draw a
10-degree clipped stroke over the 360-degree stroke's duration — a crawl whose
slowness means "you were stopped", which the outcome already says in words.

Zero travel gives zero seconds, which `startDrawing`'s existing guard
(`viewer.ts:1237`) already lands at once — the same thing ADR-065's zero-travel
rule does today, reached by arithmetic instead of a special case.

### D2. Only a `by=` instruction is a source, and the FIRST one declared

A `targets=` instruction states a LANDING. The travel it makes depends on where
the input stands when it is pressed: the same instruction is 4 units of travel
from one bank, 1 from another, and 0 from its own landing — three different
rates and one division by zero. A rate is a travel over a duration, and only
`by=` publishes one. The calculator fixture already carries both shapes
(`'Stroke': by crank 360 over 2 s`, `'Set four': targets operand 4 over 0.5 s`),
so the distinction is pinned by a committed document rather than by an argument.

Where SEVERAL `by=` instructions name one input, the first in the document's own
key order wins. That order is the producer's declaration order, preserved
end-to-end (`readInstructions` inserts into a fresh object in `Object.entries`
order; the chrome lists instructions in `Object.keys(machine.instructions)`
order, `clockedControls.ts:324`, `:365`), so the tempo is the one from the
button nearest the top of the list — a rule a maker can see, and stable under
a rebuild.

*Rejected: the smallest `|by|`.* Invisible in the panel, and it makes adding a
second instruction silently retime an unrelated input's gestures. *Rejected:
the instruction naming the input in the FOCUSED layer only.* The tempo is a
property of what the document declares about that input, not of what the panel
currently shows; a maker who navigates into a sub-assembly would otherwise
watch the same nudge at two speeds.

An instruction whose declared `by` is ZERO states no rate (a travel of nothing
over some duration) and is skipped, the search continuing. An instruction
declaring a duration of ZERO states a real one — "this travel is drawn in no
time" — and is honoured: gestures on that input land at once, as its own press
does.

### D3. No cap, and the speed still scales nothing

A nudge of 720 on an input declaring 360 over 6 s takes 12 s, which is what the
maker asked to watch: the rate is the whole point, and a cap would draw the
first half of a long stroke at the declared rate and the rest faster — a
picture of neither. The handle stays usable throughout and any further gesture
lands the drawing (ADR-064 §8), so a maker is never held. The playback speed
does not scale either duration, for ADR-064's unchanged reason: the speed means
machine time and a drawing is wall time.

### D4. The pressed instruction keeps its own declared duration

A press is drawn over the duration the instruction DECLARES, whatever travel
its request admits — ADR-064, unchanged. The asymmetry is deliberate and stated
in the spec: an instruction's duration is a statement about that stroke, and the
viewer is not entitled to rescale a declared number; a tempo is derived only
where the document declares nothing for the gesture at hand. The two agree
where it matters — a gesture asking for exactly the declared travel is drawn
over exactly the declared duration, which is the new scenario "A gesture of the
declared travel takes the declared duration".

### D5. `clockedRequest` decides the duration after the answer, not before

Today the caller passes the seconds (`clockedRequest(id, request, draw)`), which
cannot work: the duration depends on `answered.admitted`, which does not exist
until the request is made. The panel's `move`/`nudge` therefore ask for a DRAWN
request (a boolean), and `clockedRequest` computes the seconds from the answer
before calling `startDrawing`. The clock's `step()` and `clockFrame` pass
nothing and keep the default, so they stay undrawn with no copy of the bank
taken — the property ADR-065 measured and kept. Everything else of that
function's order is untouched: land, take the bank before, request, report,
rebuild the panel ONCE, start the drawing, render.

### D6. One new ADR, amending ADR-065

`workflow/adrs/EXPORT/ADR-073`, with an `Amends:` header naming ADR-065's fixed
duration and an index row saying so, exactly as ADR-065 amended ADR-064 one
cycle earlier. Written after implementation from what was built and measured.

## Risks / Trade-offs

- **A gesture can now last much longer than a fifth of a second** — 2 s on the
  Curta's crank today, 6 s if that project raises its declared duration, 12 s
  for a nudge of 720. That is the maker's own request at the maker's own
  declared rate, and any further gesture lands it at once. Reversible: the rule
  is one function in one file.
- **A document that declares an instruction for one input and not another gives
  its handles two feels.** That is the document speaking: the input a maker is
  told how to operate gets the rate its own instruction states, and the rest
  keep the button-like fifth of a second.
- **Retiming an input by adding an instruction.** A producer that adds a `by=`
  instruction changes how gestures on that input are drawn. It is the same
  declaration the button reads, and no bank, no request and no geometry moves —
  only how long the picture takes.
- **The committed browser acceptance gets slower**: the calculator's nudge of
  360 draws over 2 s instead of 0.2 s, and its samples grow accordingly. A few
  seconds of an already Playwright-driven test.

## Open Questions

1. **Should the pressed instruction's own duration also become a tempo** — a
   clipped press drawn only for as long as it travelled? D4 says no; the pilot
   may disagree, and it is the one place where a gesture and a press now behave
   differently for the same clipped travel.
2. **Is the fallback still 0.2 s** for an input no instruction states a travel
   for, now that it is a fallback rather than the rule? Unchanged here; one
   constant if the floor says otherwise.

**ANSWERED at ratification (2026-09-17), before implementation.** 1: no — a
clipped PRESS keeps ADR-064's declared duration, as D4 proposed; the asymmetry
stands and is stated in the spec. 2: yes — 0.2 s stays the fallback. Both are
implemented as proposed, with no departure.
