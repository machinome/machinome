## Context

ADR-064 (yesterday, `77b97e1`) built the whole drawing machinery and pointed
it at ONE control: the instruction button. `src/clocked/drawing.ts` takes a
request, the bank before it and a duration, and answers a frame; `viewer.ts`
holds at most one drawing, advances it in the render loop, poses through the
change set and lets the panel follow. None of that is in question here.

What is in question is the sentence that kept every OTHER control out of it —
"a gesture on a handle stays one immediate request; a duration is something a
declared instruction states" — which the pilot disproved on the floor by
nudging the Curta's crank and seeing it teleport. The Curta's `crank_rotation`
publishes `range: null`, so its row has no slider: the project's own record
tells a maker to set the nudge amount to 360 and press `+`
(`simulation/docs/clocked-curta-2026-09-17.md:42`). That gesture is the one
the pilot makes, and it is the one nothing draws.

This is a one-day correction to a one-day-old decision, so the design is
short and deliberately adds no mechanism.

## Goals / Non-Goals

**Goals:**

- Every request a maker's gesture makes on a clocked INPUT is drawn, by the
  existing machinery, with one door for the panel's gestures and the
  instruction button alike.
- One stated duration for a gesture, with its reason recorded.
- No new module, no new handle surface, no document change, no API bump.

**Non-Goals:** the drawing module itself; the machine; the clock's transport;
the run's worker; the posed `Ramp`; the framework; the Curta's own edits; any
maker-editable duration, easing, cancel or progress event.

## Decisions

### D1. Every gesture on an input is drawn, and there is nothing to exempt

The panel's two request actions (`viewer.ts:1321-1326`) are `move(id, to)` —
the number field's `change` and the slider's `change` — and `nudge(id, amount)`
— the `±` buttons. Both are drawn.

**The "live drag" exception the assignment anticipated does not exist.** The
clocked slider listens on `change` ALONE (`viewer.ts:3485`), where the posed
chrome's driver slider writes on `input` (`:3095`). A drag therefore moves the
thumb while the model stands still, and the release is ONE jump request —
precisely the teleport this cycle removes. A track click and an arrow key are
the same one request. So the rule has no exception to state, which is also why
the spec delta can say "a gesture on a handle" without qualification.

*Rejected: requesting per pointer move during a drag (`input`).* That is the
per-frame-request shape ADR-064 measured and the pilot rejected; on the Curta
it is a solve and a pose per pointer sample.

### D2. A gesture's drawing lasts 0.2 s, whatever the travel

One constant beside `DEFAULT_NUDGE` in `clockedControls.ts`, where the chrome's
other policy numbers live, with the reason the running chrome already wrote for
the same control: `runControls.ts:39-62`, `DEFAULT_NUDGE = {amount: 1, seconds:
0.2}`, *"a nudge that teleports is a nudge nobody can watch. A fifth of a
second is long enough to see the carry throw and short enough to feel like a
button."* The clocked chrome inherits the number and the reason; it does not
import the running chrome's plan object, because the two chromes state their
own policy and one already differs (the clocked nudge has no seconds field).

*Rejected: deriving the duration from the amount at the running chrome's RATE*
(one design unit per 0.2 s). It draws the Curta's 360-degree crank nudge over
**72 seconds**. The running chrome can afford a rate because its nudge is a
travel over SIMULATED time inside a cadence; a clocked gesture has no cadence
and the duration is a picture, not a request.

*Rejected: a seconds box on every row, or a maker-editable default.* Nobody
asked, and a maker who wants a two-second stroke presses the declared
instruction, which states exactly that.

*Rejected: scaling by the playback speed.* ADR-064 ruled it for an
instruction's duration and the reason is unchanged: the speed means machine
time, and a drawing is wall time.

### D3. One door, generalized from "an instruction" to "a request and a duration"

`clockedPlay` (`viewer.ts:1160`) already does the whole sequence: land the
running drawing, take the bank BEFORE, make the one request, write the outcome,
rebuild the panel once, `startDrawing`, render. `clockedRequest` (`:1117`) does
the same minus the drawing. The change is to make `clockedRequest` finish
through `startDrawing` with the gesture duration, and to keep `clockedPlay` as
the instruction's thin wrapper over the same steps.

The order matters and is kept exactly as ADR-064 has it: the panel is rebuilt
BEFORE the drawing starts, and frame 0 is posed in the same task, so the
report reaches the panel and the readings are corrected to the transition's
ORIGIN before the browser paints.

`clockedDrawing` (`:421`) carries `name` only to drive
`clockedChrome.indicate`. It becomes an optional indicator key, `null` for a
handle's gesture: an instruction BUTTON needs `aria-busy` because nothing else
on it moves, while a handle row indicates by the thing the maker is watching —
its own reading and thumb sweeping under `follow`. Adding a busy state to a row
would be a new surface nobody asked for.

`startDrawing`'s existing guards are reused unchanged: nothing is drawn for a
duration of zero, and nothing for a request that neither travelled nor
committed (an interlock holding a knob still reports its stop).

### D4. The clock and the host handle stay as they are

The transport's played frame (`clockFrame`, `:1256`) and its STEP button
(`:1355`) call `clockedRequest` too, and must NOT acquire a drawing. Reason,
beyond "nobody asked": ADR-064 makes starting a drawing STOP the transport, so
a drawn step would be a transport control that pauses the transport, and a
drawn played frame would fight itself sixty times a second. They pass the
gesture duration as zero — the same guard that already means "land at once".

`machine().move` (`:1843`) stays instantaneous and gains no `{draw}` option:
it is programmatic, the bank is final at the request either way, and the
browser probe and the acceptances read it immediately. `machine().trigger`
remains `clockedPlay`, drawn, as ADR-064 left it.

### D5. No API bump, and nothing in the document

`solidNodeViewerApi` stays **19** and `solidNodeDocumentVersions` stays
`[1 … 8]`. The rule is "raised whenever the mount interface or handle changes
incompatibly, and when a capability a host may require is added": the mount
interface, the handle's verbs and their answers are unchanged, no document
field is read or written differently, and a host cannot require or detect this
through the API at all — it is the on-screen behaviour of a control that
already worked. The precedent is ADR-060/061, which changed how the viewer
behaves without a bump; ADR-064 bumped because at 18 a listed button was DEAD,
which a host could require the fix for.

### D6. One new ADR, amending ADR-064

`docs/adrs/EXPORT/ADR-065`, amending ADR-064 the way ADR-064 amended ADR-062
one cycle earlier — the house's own form for a correction to a neighbouring
decision, and the form the index already renders ("**Accepted**, amends 064").

*Rejected: a dated `## Amendment` section inside ADR-064.* The house allows it
(`docs/adrs/README.md`), and the two existing examples (ADR-013, ADR-020) are
POINTERS at a later decision, not decisions themselves. This cycle has its own
context (a floor finding), its own alternatives (D2's rate, D1's live drag) and
its own consequences; an archived change links an ADR, and folding it into
ADR-064 would leave this cycle without a record and rewrite an accepted
Decision section rather than annotate it.

## Risks / Trade-offs

- **A 360-degree stroke in 0.2 s is about 12 frames on a 60 Hz page** → that is
  what "animated fast" asks for, and the declared instruction remains the
  2-second version of the same stroke. Recorded as a reversible working
  assumption: the constant is one number in one file.
- **A drawn slider commit sweeps the thumb back to the origin and forward** →
  it is what the model is showing, which is the panel's whole rule; and the
  thumb is written only where the row is not being edited.
- **A typed value committed with Enter keeps focus, so its own field does not
  follow** → pre-existing (`viewer.ts:3502`), now reachable; stated in the
  requirement and pinned by an acceptance rather than hidden.
- **A host that drives the panel's DOM in a test now sees intermediate poses**
  → the committed acceptance's section 4 asserts a landing immediately after a
  `+` on another input; it is updated in this cycle, red first.
- **Every gesture now costs a drawing's frames rather than one pose** → the
  cost per frame is a pose of only the ids that moved, measured at 9.20 ms on
  the Curta's own page and 0.40 ms on the calculator (ADR-064); at 0.2 s the
  total added work is about a dozen such poses.

## Open Questions

1. **Is 0.2 s the right gesture duration for the Curta on the pilot's
   hardware?** The number is inherited from the running chrome's own design
   decision, and the pilot can see it on the floor at once. One constant.
2. **Should a drawn gesture indicate on its row** (the way an instruction
   button does) **as well as follow?** This design says no; the sweep is the
   indication.
