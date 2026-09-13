# Design — drive the run on screen

## Context

This change is the second half of the open-run campaign's cycle 5 and
depends on `run-in-the-worker`, which brings document version 5, the run
engine, the worker and the `run()` handle. Everything below issues
requests against that handle and renders what comes back.

The interaction model is **ratified, not proposed**:
`workflow/open-run-simulation/design.md`, "Browser interface" and "Inputs,
instructions and controls — pilot ratification, 2026-09-12", carried
forward by "Decision 2026-09-13" item 8. The design below decides only
what that record leaves open: the layout, the defaults, the formatting,
the republish rule and the capture's posture.

What exists here: `controls.ts` decides the posed chrome as pure data and
`viewer.ts` renders it, calling the same public driving API a host would —
"which is what keeps the on-screen and programmatic doors
indistinguishable". That is the pattern this change repeats, for a
different set of controls and a different door.

## 1. Two chromes, chosen by the document

### D1. A running document gets a different panel, not a widened one

`viewer.ts` builds the posed chrome (`controlLayer`) when the document
carries no program, and the running chrome (`runControlLayer`) when it
does. They never both appear, and a document versions 1 to 4 reaches
exactly the code it reaches today.

The reason is not tidiness. A **slider writes a position into a
coordinate**, and under a run a coordinate is the output of an
integration that carries history: writing a position is the re-entry the
running mode exists to remove, and would put the tens drum where one
`Add one` left it however many times a maker asked. The pilot's rule —
"there is no two-way binding between an editable position and the
mechanism", "readouts follow committed state and never feed another
movement request back into the run" — makes the slider the one control a
running document cannot have. So it does not have one.

*Alternative that lost:* keep the slider and make it issue a `move(to=)`
per drag sample. It reads like a compromise and is the bug: a drag is
sixty requests a second on one input, each taking ownership from the
last, each reporting an outcome nobody reads, and the thumb would fight
the committed readout every time the machine refused to follow.

### D2. The bank is not an editable register panel

Only **declared inputs** get a readout. Joint coordinates — the drums,
the arbors, the carry wheels — are visible *as the machine*, which is the
pilot's own rule: "Internal mechanical state is not rendered as an extra
bank of editable calculator registers. In Curta the visible answer is the
geometry of the numbered wheels." A host that wants a coordinate readout
has `run().state()` and `onCommit`; the widget does not invent a
dashboard.

## 2. The running chrome as pure data

`runControls.ts` exports `runControlLayer(input): RunControlLayer`,
deciding everything and touching nothing:

```
RunControlLayer {
  present: boolean                  // the document carries a program
  breadcrumb: BreadcrumbSegment[]   // controls.ts's, reused verbatim
  children: string[]                // the same navigable-children rule
  inputs: RunInputControl[]
  instructions: InstructionControl[] // controls.ts's, reused verbatim
  transport: TransportPlan
}

RunInputControl {
  id, label, unit                    // qualified id, last segment, declared unit
  value: number                      // NATIVE, as the bank holds it
  display: number                    // DESIGN units, what the readout shows
  readout: string                    // formatReadout(display), fixed width
  nudge: { amount: number, seconds: number }   // a REQUEST, never a value
  jog:   { rate: number }                      // design units per simulated second
  outcome: OutcomeReport | null
}

TransportPlan {
  running: boolean, speed: number, ladder: number[],
  elapsed: string, tick: number, refusal: string | null
}
```

The focus rule is `controls.ts`'s `scopedIds`/`navigableChildren`
unchanged: an id belonging to the focused layer is the focus path's
segments plus exactly one more, by segment equality and never by string
prefix. Reusing those functions rather than copying them is what keeps
one meaning of "the focused layer" in the widget.

### D3. A nudge is a move over a duration, not an instant

`+` issues `move(id, {by: +amount, duration: seconds})`; `−` issues the
negation. The defaults are `amount = 1` design unit and
`seconds = 0.2`, rounded to whole ticks (48 at 1/240), and both are
editable — the amount in a small field beside the pair, the jog rate in
another.

*Why not instantaneous* (`duration: 0`). A zero-duration move admits its
whole travel in one tick. The jump machinery survives that — it
partitions the tick — but a stop behind a nonlinear edge is located to
first order inside it, and a nudge that teleports is a nudge nobody can
watch. A fifth of a second is long enough to see the carry throw and
short enough to feel like a button.

*Why the editors configure the request.* Ratified: "Amount and rate
editors configure future commands, not current mechanical coordinates."
Typing `5` into the amount field moves nothing; the next `+` asks for
five.

### D4. A jog is a rate command bounded by the interaction

`pointerdown` → `rate(id, ±rate)`; the command is cancelled — `rate(id,
0)` — on `pointerup`, `pointercancel`, `lostpointercapture`, the window's
`blur`, and a `visibilitychange` to hidden. All five, because the
ratified rule names three and the fourth and fifth are the same failure:
a pointer or a page that goes away while the button is held must not
leave a machine running. The button captures the pointer on press, so a
drag off it still releases.

A jog while another owner holds the input is refused by the run, and the
refusal is reported in place rather than thrown at the console:
"manual controls never silently replace a program's ownership of the same
input."

### D5. A request starts a paused run

A nudge, a jog or an instruction pressed while the run is paused starts
it. A command admits travel only on a tick, so a request into a paused
run would report nothing, forever — which is indistinguishable from a
broken button. Pressing a control is asking the machine to move.

*Alternative that lost:* disable every request control while paused. It
is defensible and it makes pause mean "nothing happens", but it puts a
mode between the maker and the machine for no gain.

### D6. The transport, and no scrubber

Run/pause, step one tick, the speed select over `playback.ts`'s existing
ladder (×0.1 … ×3600), the elapsed simulation time, and reset. **No
timeline slider**: ratified, "No live-time scrubber is offered: seeking
belongs to recorded history and replay." A version 5 document has no
`$t`, so `tree.animated` is false and the animation bar is not built
anyway; the transport bar is a different bar with a different meaning,
and the two never appear together.

**Step** advances exactly one tick, which is what makes a jump or a stop
inspectable: press step until the drum crosses its window and look at the
crossing the panel reports.

**Elapsed** is formatted by a new `formatElapsed(seconds)` beside
`formatMachineTime`: `m:ss.ss` up to an hour and `h:mm:ss.ss` beyond it,
widening once and never narrowing, so the digits hold still the way the
driver readouts do. It is elapsed *simulation* seconds — the same number
the program's clock name binds to — and it never wraps.

**Reset** calls `run().reset()`, which restores the initial snapshot: the
rest bank, tick zero, no commands. The readouts follow, because they
follow committed state.

### D7. Outcomes are reported where the request was made

Each input control and each instruction button carries the outcome of the
last request issued from it: `completed`, `blocked` with the travel
admitted in design units (`blocked after 12.5 mm`), `refused` with the
run's own message, or `cancelled`. A blocked outcome is the interesting
one and it says what the pilot asked it to say: the travel the machine
actually made, with nothing remembering the rest.

A **refused tick** is different in kind: it is the whole machine
disagreeing with itself, its message names the relation as its author
wrote it and the class that stated it, and the run pauses on it. It is
shown once, across the panel rather than on one control, and it clears
when the next tick commits.

## 3. A republish keeps the run only when it is the same machine

`manifestChanged()` today reconciles the tree and refreshes the chrome.
With a run alive:

- if the republished document carries a program whose `identity` equals
  the running one, and the step size is unchanged, **the run continues**:
  the bank, the commands, the tick and the elapsed clock stand, and only
  the geometry and the chrome reconcile;
- otherwise the run is disposed and a fresh one starts at the new
  document's published rest bank, and the panel says so.

This is the workflow design's own rule — "Live updates must invalidate or
explicitly migrate incompatible simulation state, not preserve
coordinates solely because strings happen to match" — and `identity` is
exactly the digest the framework publishes to answer it: the root class,
the bank's ids, the inputs' declarations, the spans and every edge's
ends, direction and expression. An edit that moves a law changes it; an
edit that moves a mesh does not.

A document that gains or loses its program across a republish is the
second case: a run appears at rest, or disappears with its chrome.

## 4. The capture

`solid-node-viewer capture` photographs a staged document through the
widget. Under a document carrying a program it photographs the **rest
pose**: no run is started, no tick is taken, and the program's clock name
binds to zero — which is the instant the rest pose is defined at, and the
same still the framework's `--drive` flag produces on its own side.

`--time` is refused, by name, when the staged document carries a program
and the value is not zero: `--time` is the animation fraction, a running
document publishes no `animation.loop` and carries no `$t`, and honouring
it would silently photograph the same pose while claiming an instant. The
refusal happens before any browser starts, which is the posture this
capability already takes for every other thing it cannot do.

The framework learns that the capture supports version 5 the same way it
learns everything else about this package: `documentVersions` from
`describe()`, published by `run-in-the-worker`. Nothing here talks to the
framework.

*Alternative that lost:* run the machine for `--time` seconds and
photograph it there. It is a genuinely useful picture and it is a
different feature — a still of a reachable run state, which the framework
itself recorded as an open question and declined to invent. A capture
flag that silently ran a machine for two seconds would answer that
question by accident.

## 5. Risks

1. **Pointer capture across browsers.** `setPointerCapture` /
   `lostpointercapture` are well supported, but a jog left engaged is the
   failure that damages trust. Mitigation: five independent release
   paths (D4), and a Playwright test that presses, moves the pointer off
   the button, and asserts the rate command retired.
2. **A control that outruns the machine.** Ten `Add one` pressed quickly
   are ten instructions on one input, and the second is refused while the
   first owns it. Mitigation: the button reports `refused: units_entry is
   already owned` in place, and it indicates busy until its own commands
   retire — the same `aria-busy` the posed instruction button already
   uses.
3. **Chrome cost per frame.** The readouts follow every committed frame.
   Mitigation: the same shape `controls.ts` already has — the layer is
   re-derived per control from the committed value, and only the controls
   whose input moved are written.
4. **The export page grows a machine.** A self-contained export of a
   running model now runs one, offline, from a static directory. That is
   the intent; the risk is that a maker opening an old export sees no
   change and a new one sees a transport bar with no explanation.
   Mitigated by labels and accessible names, not by a tour.

## 6. Open questions

1. **Should a nudge's amount default to something the document says?** A
   `Driver` declares a unit, a scale and a range, and no natural step. One
   design unit is a guess that is right for the Pascaline (one digit) and
   arbitrary for a millimetre axis. Whether the framework should let a
   declaration state a nudge step is the pilot's, and is the same question
   its own §10 item 7 asks about a driver's domain.
2. **Should the panel show the crossings and stops the run records?** They
   arrive on every frame and they are exactly what makes a carry legible.
   Not shown here; a candidate for the dragging cycle.
3. **Should reset also clear the pause?** It restores the initial
   snapshot; whether it leaves the run paused or running is a taste
   question. Proposed: it leaves the transport exactly as it found it.

## 7. The ADR to extract

- **ADR-048 (EXPORT): Running controls submit requests; nothing binds
  back.** The decision that a document carrying a program is driven by
  requests — a nudge, a hold-to-jog, a named instruction — whose outcomes
  are reported with the travel actually admitted; that a readout follows
  committed state and never writes to it, so a running document has no
  slider and no timeline; that the interaction bounds a jog (release, lost
  capture, lost focus, a page that stops being displayed); and that a
  republish keeps a live run only when the published program identity says
  it is the same machine. Beside ADR-035 and the posed chrome's own
  decision; consumes `run-in-the-worker`'s ADR-045.
