## Why

**The pilot pressed `+` on the studio floor and the Curta still teleported.**
Today, on the shop floor serving API 19 (viewer main `77b97e1`) with
`projects/Calculators/Curta-Type-I-3x`'s `_build/clocked_curta/viewer.json`
(version 8, 23 drivers, 18 states, `clocked.clock: "time"`), the pilot's
words:

> I still see instant change when I click to change something in the curta,
> no animation transitioning from one state to another.

ADR-064 shipped the drawing machinery one day earlier, and it draws exactly
ONE thing: a pressed INSTRUCTION. The Curta declares one instruction
(`'Turn crank': by crank_rotation 360 over 2 s`) — but its own record tells a
maker to operate it by hand, not by that button:

> In the browser panel, set a selector, set the `crank_rotation` nudge amount
> to `360`, and press `+` repeatedly.
> — `simulation/docs/clocked-curta-2026-09-17.md:42`

And `crank_rotation` publishes `range: null`, so its panel row has no slider at
all: a number field, `-`, `+`, and the amount box. Every one of those goes
through `viewer.ts:1322` and `:1325` into `clockedRequest`, which poses ONCE
and returns. A 360-degree stroke — every tooth, every carry — arrives in a
single frame. The same is true of the other 22 drivers, of the digit sliders
(`range: [0, 9]`) and of `carriage_rotation` (`range: [0, 100]`).

The defect is a sentence this repository ratified yesterday, in the
requirement "A maker operates a clocked machine on screen":

> A gesture on a HANDLE SHALL remain ONE immediate request, posed once: a
> duration is something a declared instruction states, and a handle declares
> none.

and its twin in the code, `clockedControls.ts:188-190`: *"A clocked request is
instantaneous by construction — there is no cadence for it to be spread over
— so a nudge is a travel and nothing else."*

Both confuse ONE REQUEST with ONE FRAME. ADR-064 already proved they are
different things: the request is made once, and what the page does afterwards
is DRAW the transition it reports. The running chrome settled the same
question from the other side and wrote the reason into its own source —
`runControls.ts:39-62`, `DEFAULT_NUDGE = {amount: 1, seconds: 0.2}`: *"a nudge
that teleports is a nudge nobody can watch"*. The clocked chrome's nudge, alone
of the three chromes, carries an amount and no seconds.

The pilot's standing requirement is unchanged and still unmet for the gesture
the project's own record prescribes: *"animated fast between states with smooth
transition just like the fast_curta, but holding state."*

## What Changes

- **Every request a maker's gesture makes on a clocked INPUT is DRAWN**, by
  the machinery ADR-064 already built and unchanged in kind: one request at
  the gesture, solved before the first frame; the returned transition drawn
  from its `origin` to its `end` with each commit at its own fraction; one
  pose per frame and no machine work in the frame loop; the panel following;
  the outcome reported where the gesture was made. That is the `+`/`-` nudge,
  a value typed into the number field, and a slider's commit.
- **A gesture's drawing lasts a fifth of a second, whatever the travel.** A
  handle declares no duration, so the viewer states one: `0.2 s` of wall time,
  the running chrome's own `DEFAULT_NUDGE.seconds` and its reason. It is NOT
  derived from the amount — the running chrome's rate of one design unit per
  0.2 s would draw the Curta's 360-degree crank nudge over 72 seconds — and
  the playback speed does not scale it (ADR-064's ruling). A maker who wants
  the two-second stroke presses the instruction; a nudge is a button and feels
  like one.
- **There is no live-drag exception, because there is no live drag.** The
  clocked slider listens on `change` alone (`viewer.ts:3485`), where the POSED
  chrome's driver slider writes on `input` (`:3095`): a drag moves the thumb
  and the model stands still until the pointer is released, and the release is
  one jump request. So a drag's commit, a click on the track and an arrow key
  are each ONE request and each drawn, and nothing has to be exempted.
- **The clock is not a drawn gesture.** The transport's played frame and its
  STEP stay exactly as ADR-063 made them: a clock has seconds to spend per
  frame, and drawing a step would pause the transport under ADR-064's
  one-authority rule — a transport control that stops the transport. Nothing
  asked for it.
- **The host's `machine().move(...)` stays instantaneous**, with no new option
  and no new verb. It is programmatic, the bank is final at the request
  either way, and no project has asked. The PANEL draws; the handle does not.
- **A field a maker is editing is still not overwritten by a drawing**
  (`viewer.ts:3502`) — a rule that existed already and becomes reachable now
  that a typed value starts a drawing. Stated in the requirement rather than
  left as a surprise.
- **NOT** a change to the drawing module, to the machine, to the document, to
  the corpus, to the framework, to the clock's transport or to the posed
  `Ramp`. `src/clocked/drawing.ts` is untouched.

## Capabilities

### New Capabilities

None. One existing chrome's existing gestures reach an existing drawing.

### Modified Capabilities

- `viewer-package`: **MODIFIED** — "A maker operates a clocked machine on
  screen" (a gesture on a handle is drawn, not jumped; the fifth of a second;
  the field a maker is editing); "The viewer plays a clocked instruction as one
  drawn transition" (a transition the viewer draws for a gesture that declares
  no duration; the clock's transport is not drawn). Every existing scenario of
  both requirements is carried verbatim under its exact title; one sentence of
  the first is REPLACED because this cycle makes it say the opposite of what is
  true, and one scenario body ("A maker moves an input and the machine
  commits") stops saying the model poses at the resulting bank in one go.

## Impact

- `solid_node_viewer/widget/src/viewer.ts` — the panel's `move` and `nudge`
  actions (`:1321-1326`) route through the one door `clockedPlay` already uses,
  generalized from "an instruction" to "a request and a duration"
  (`clockedRequest` `:1117`, `clockedPlay` `:1160`, `startDrawing` `:1210`);
  `clockedDrawing` (`:421`) carries an optional indicator key instead of an
  instruction name. `landDrawing`, `drawFrame`, `drawingFrame`, `clockFrame`,
  the handle wrappers and the reset path are unchanged in behaviour.
- `solid_node_viewer/widget/src/clockedControls.ts` — the gesture duration
  named and given its reason, beside `DEFAULT_NUDGE` (`:188-195`), whose
  comment is corrected.
- `solid_node_viewer/widget/src/clocked/drawing.ts` — **nothing**.
- `tests/test_calculator_document.py` — the committed acceptance gains the
  drawn nudge, the drawn typed value and the drawn slider commit on the
  calculator fixture; its existing section 4 ("a gesture lands a running
  drawing") now also starts a drawing of its own and is updated to say so.
- `tests/test_curta_drawing.py` — the skippable measurement gains the Curta's
  own `crank_rotation` nudge at 360 and a typed 720, served through the
  directory of SYMLINKS it already builds, copying nothing.
- `CHANGELOG.md` under `0.2.0 — unreleased`; ONE new decision record,
  `docs/adrs/EXPORT/ADR-065`, AMENDING ADR-064; `docs/adrs/README.md`.
- **No API bump** (`solidNodeViewerApi` stays 19) and no document change: the
  mount interface, the handle, its verbs and their answers are byte for byte
  what they were, and nothing a host can call behaves differently. The
  requirement "The viewer declares its API version" is not touched.

### Non-goals

- The framework and the document: `move` already reports `origin` and `end`,
  and nothing new is published or read.
- The instruction path (ADR-064, done), the clock's transport (ADR-063), the
  run's worker, the posed `Ramp`, and the Curta's own edits.
- A maker-editable gesture duration, an easing, a cancel, a per-input seconds
  box, a `{draw: seconds}` option on the handle: nothing asked for one.
