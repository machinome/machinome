# ADR-048: Running controls submit requests; nothing binds back

**Status:** Accepted

**Date:** 2026-09-13

**Change:** `drive-the-run-on-screen`

**Extends:**
- [ADR-035: Reusable viewer core and declared API version](ADR-035-reusable-viewer-core-and-declared-api.md)

**Consumes:**
- [ADR-045: The run executes in a worker and the main thread only poses](ADR-045-the-run-executes-in-a-worker.md)

## Context

ADR-045 gave this viewer a tick. A version 5 document mounts, poses at
its published rest bank and stands there: every request goes through
`handle.run()`, so the machine was drivable by a host and not by a
maker. The campaign exists for the opposite — the Pascaline module in a
browser, for a person to press.

What that person may press is not open design work. The pilot ratified
the interaction model on 2026-09-12 and carried it forward in the
2026-09-13 decision:

- an **input** exposes a mechanical coordinate as an entry point for
  movement requests, and stores no second editable copy of it;
- an **instruction** is a named, reusable movement request, and a button
  for one *references* it rather than repeating its definition;
- a **control** is how a person issues a request — a button, a held jog,
  later a dragged part;
- there is **no two-way binding** between an editable position and the
  mechanism; amount and rate editors configure future commands, and
  readouts follow committed state and never feed a movement back into
  the run;
- every request reports completed, blocked, refused or cancelled **with
  the motion actually admitted**, and a blocked request accumulates no
  hidden movement;
- release, lost pointer capture and lost window focus end a manual jog,
  and manual controls never silently replace a program's ownership of an
  input;
- there is **no live-time scrubber**: seeking belongs to recorded
  history;
- the existing static and looping position controls keep their meaning
  and do not become running mechanical controls.

The viewer already had a chrome — sliders, click-to-edit readouts,
instruction buttons, an animation bar — and the tempting move was to
widen it.

## Decision

**A document that carries a program is driven by requests, and nothing in
its chrome writes a coordinate.**

1. **Two chromes, chosen by the document.** `runControls.ts` decides the
   running chrome as pure data and `viewer.ts` renders it, the same split
   `controls.ts` already has; a document carrying a program builds that
   and never the posed one, and a document of versions 1 to 4 reaches
   exactly the code it always did. The two never appear together.

2. **No slider, and no timeline.** A slider *is* a two-way binding: it
   writes a position into a coordinate. Under a run a coordinate is the
   output of an integration with history in it, so writing a position is
   the re-entry the running mode was built to remove — ten `Add one` on a
   slider would leave the tens drum where one did. A running document
   therefore has no position control and no animation timeline; a version
   5 document reads no `$t`, so the animation bar is not built for one at
   all.

3. **Only declared inputs get a readout.** Joint coordinates are visible
   *as the machine*. The widget does not render the bank as a second,
   editable panel of registers; a host that wants one has `run().state()`
   and `onCommit`.

4. **A nudge asks for a travel over a duration** (one design unit over a
   fifth of a second by default, both editable and settable at mount),
   and **a jog asks for a rate** until the interaction ends. The editors
   configure the request: typing into one moves nothing.

5. **The interaction bounds the jog, from five sides** — `pointerup`,
   `pointercancel`, `lostpointercapture`, the window's `blur`, and a
   `visibilitychange` to hidden. The ratified rule names three; a pointer
   that goes away and a page that stops being displayed are the same
   failure, and a jog left engaged is the failure that damages trust.

6. **Every request reports at the control that issued it** — completed,
   blocked with the travel admitted in design units, refused with the
   run's own message, or cancelled — and a control indicates the run
   until its own commands retire, which is a separate question from what
   its last report said. A **refused tick** is different in kind: it is
   the machine disagreeing with itself, so its message is shown across
   the panel, the run pauses on it rather than repeating it sixty times a
   second, and it clears when the next step commits.

7. **A request into a paused run starts it.** A command admits travel
   only on a tick, so a request into a paused run would report nothing,
   forever — indistinguishable from a broken button.

8. **A republish keeps a live run only when the published program
   identity and the run's step size are both unchanged**, and otherwise
   discards it, starts a fresh run at the new document's rest state and
   says which it did. `identity` is the digest the framework publishes
   for exactly this question, so an edit that moves a law changes it and
   an edit that moves a mesh does not. A coordinate is never carried
   across because an identifier matched.

9. **A staged document carrying a program is photographed at its rest
   state**, with no step taken and the clock at zero, and a non-zero
   `--time` on one is refused by name before any browser starts: a
   running document publishes no animation cycle. A still of a state the
   machine *reached* is a different picture and is not offered.

The host's presentation switch covers both chromes: `driverControls:
'none'` suppresses the running controls exactly as it suppresses the
posed ones, and leaves the whole run API intact.

## Consequences

- A maker meeting a version 5 document sees what the machine's author
  declared — its inputs, with their units, and its instructions by name —
  and can drive it with no host code at all, including from a
  self-contained export opened offline from a static directory.
- On-screen and programmatic driving stay indistinguishable: every
  control calls the same `run()` handle a host would, so a request made
  by hand and one made by a script produce the same observable run
  state, the same listener traffic and the same readbacks.
- A blocked request tells the truth about the machine, and nothing
  remembers the remainder. That is only as legible as the document's
  declared bounds: a machine that declares no stop can never report one.
- The panel costs one readout write per moved input per committed frame,
  and nothing for an input standing still.
- Nothing seeks. A maker who wants to look at an instant walks the run
  one step at a time, which is the transport's step button, and recorded
  history and replay remain a later cycle's question.
- Constrained dragging of a part is deliberately out: the next viewer
  cycle binds a pick to a declared input through this same command
  interface, with the same blocked-travel reporting.

## Alternatives considered

**Keep the slider and make it issue a `move(to=)` per drag sample.** It
reads like a compromise and is the bug: a drag is sixty requests a second
on one input, each taking ownership from the last, each reporting an
outcome nobody reads, and the thumb fighting the committed readout every
time the machine declined to follow.

**Disable every request control while the run is paused.** Defensible,
and it makes pause mean "nothing happens"; rejected because it puts a
mode between the maker and the machine for no gain.

**Photograph a running document after `--time` seconds of simulation.**
A genuinely useful picture, and a different feature — a still of a
reachable run state, which the framework itself recorded as an open
question and declined to invent. A capture flag that silently ran a
machine for two seconds would answer that question by accident.
