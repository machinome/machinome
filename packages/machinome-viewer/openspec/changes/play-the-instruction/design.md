## Context

Two cycles brought the clocked machine into the browser: ADR-062 loads and
executes a version 8 document — the bank, the request, the event solve, the
commit, the clip at a declared stop, one pose per request, the session verbs
— and ADR-063 made the CLOCK an input a rendered frame advances. Both left
one thing deliberately behind, because the producer had not decided it: what a
declared INSTRUCTION means. ADR-062 §14 listed the buttons and disabled them,
and `ClockedMachine.trigger` refuses by name today
(`src/clocked/machine.ts:402-408`).

solid-node's ADR-129 decided it on 2026-09-17, from the Curta's own evidence:
an instruction under a clocked root IS one request over the one driver it
names; `trigger` returns that request; `Request` now carries `origin` and
`end`, the two ends of the path it travelled, verbatim from the bank; the
declared `duration` is carried and silent, and says how long a CONSUMER draws
the transition. The corpus records a `trigger` step so the two runtimes cannot
agree about `move` and disagree about a BUTTON.

The originating project is `projects/Calculators/Curta-Type-I-3x`, whose
clocked sibling publishes `_build/clocked_curta/viewer.json`: version 8, 23
drivers, 18 states, 39 commits, 35 bounds, `clock: "time"`, and the single
instruction `'Turn crank': by crank_rotation 360 over 2 s`. Its posed sibling
`_build/fast_curta/viewer.json` (version 4, 8 drivers, 7 instructions)
ANIMATES, because `Ramp` (`src/drivers.ts:64-85`) interpolates the driver
linearly over the duration, one pose per frame. The pilot's requirement,
verbatim: *"I need it to be animated fast between states with smooth
transition just like the fast_curta, but holding state."*

The decision about HOW is the pilot's and is already taken: **one solve per
gesture, before the first frame; the viewer draws the returned transition
over the duration; no machine work in the frame loop.** This cycle is that,
and deliberately nothing more.

## Goals / Non-Goals

### Goals

1. Pressing a clocked document's declared instruction plays it: one request,
   made once, and the transition it describes drawn over the declared
   duration.
2. The drawing lands ON the machine's own bank — the same values, not near
   them — so what was watched and what was committed are one state.
3. What a frame of a drawing costs is a POSE. The machine is not called.
4. The corpus's `trigger` steps and both path ends replay EXACTLY, so this
   runtime's meaning of a button is the producer's.
5. A maker reads, beside the model, what the model is showing.

### Non-Goals

- **The shop floor's use of the button** — the studio's own repository.
- **The Curta's own edits**, its unneeded `Time.elapsed()` included — the
  project's own repository.
- **Per-frame requests on a driver**, in any form (§17).
- **ADR-063's clock transport, the run's worker, the posed `Ramp`, document
  versions 1–7, the document's shape and the framework** — untouched,
  asserted by diff and by fixture.
- **An instruction naming several drivers, or naming the clock** — refused by
  the producer before a document exists; refused here at load, and designed
  for nowhere.

## Decisions

### 1. `trigger` is the producer's verb, mirrored where the producer put it

`Sim.trigger` resolves the instruction and delegates the motion to
`Clocked.move` (ADR-129 §"Where the code goes"). This viewer's
`ClockedMachine` already holds both halves: `LoadedMachine.instructions`
(`src/clocked/document.ts:177`, read at load) and `move` itself. So `trigger`
is, exactly as in Python:

| declaration | request |
| --- | --- |
| `by: {id: travel}` | `move(id, {by: travel})` |
| `targets: {id: value}` | `move(id, {to: value})` |

and it RETURNS the `ClockedRequest`. Nothing converts, rounds or clamps on the
way: `move` already takes DESIGN units and performs the one `native()`
conversion (`machine.ts:113-117`), so an integer-typed driver rounds once, in
the one place it rounds today, and the half-to-even agreement with the
producer is inherited rather than re-stated.

`trigger` leaves the cadence refusals; `rate` and `step` stay refused by name
and keep their messages. An unknown name is refused listing the declared ones
— the shape `DriverStore.trigger` already uses (`drivers.ts:256-260`) and the
one `declarationOf` uses for an unknown driver.

**No new handle verb.** `MachineHandle extends ClockedMachine`, so the host
API gains the meaning and not a member. The viewer's own wrapper
(`viewer.ts:1628-1660`) wraps `trigger` for the same reason it wraps `move`:
the panel is pure data rendered whole and must follow whoever moved the
machine.

### 2. `origin` and `end`, mirrored field for field

`ClockedRequest` mirrors the producer's `Request` field for field; the
producer added two, so this adds the same two, with the same names and the
same units:

- **`origin`** — the value the moving input held when the request began, the
  bank entry verbatim (`machine.ts:292`);
- **`end`** — the value it ended at, the CLIPPED target verbatim
  (`machine.ts:364`), which is where the bank stands afterwards.

Both NATIVE, as every `ClockedCommit.value` already is; `admitted` stays
DESIGN, because that is what `by` asked in. The asymmetry is the producer's
and is documented in one sentence of the interface, as it is there.

They are not conveniences: the corpus records them on all 65 recorded
requests across all 30 machines (63 `move` steps and the two `trigger`s;
ADR-129's own "63" counts the moves it added them to), so a build that
computed them instead of reporting them would fail the replay the moment a
clip, a `to=` request or an integer driver made the arithmetic disagree in
the last bit. That is
ADR-128's one-authority rule reaching a value object, and it is why the
drawing below reads `end` rather than `origin + admitted / scale`.

### 3. The DRAWING is a pure module, and the render loop advances it

`src/clocked/drawing.ts` — no DOM, no three.js, no machine — holds the whole
decision:

```ts
drawing(request: ClockedRequest, start: Record<string, number>,
        duration: number, integer: boolean): Drawing
Drawing.advance(elapsedSeconds: number): DrawnFrame
Drawing.land(): DrawnFrame           // jump to the end
DrawnFrame = { value: number; bank: Record<string, number>;
               moved: string[]; done: boolean }
```

It is handed the request, the bank the machine stood at BEFORE it, and the
declared duration; it holds no machine and cannot call one. That is the
structural proof behind the "one solve per press" requirement — the frame
loop's collaborator has nothing to solve WITH — and it is why the rule is
decided and tested in node, where `clockedControls.ts` and `bounds.ts`
already are, instead of only in a browser.

`viewer.ts` holds at most one drawing beside the clock's transport state and
advances it in the render loop, in the same place and for the same reason
`clockFrame` runs there (`viewer.ts:1477-1510`): the loop already knows the
wall seconds since the last frame. Each frame it updates the tree through the
existing `tree.update(clockedScope(bank, time, bindings), posed(moved))`, so
only the nodes the moved ids reach are re-evaluated, and the loop's own
`renderer.render` shows it. `$t` keeps sweeping beside it, untouched: the
timeline and a drawing advance different things, exactly as the timeline and
the clock do.

**Rejected: a drawing inside `machine.ts`.** The machine is a pure
synchronous library the corpus replays in thread; a frame is a page concern,
and ADR-063 already drew that line for the clock's transport ("the frames are
here, not in `machine.ts`").

### 4. Commits are keyed on the FRACTION

Every `ClockedCommit` carries `fraction` (of the clipped path) and `value`
(the landing, native). Either could select which commits a frame has passed.
The drawing keys on **`fraction`**, for three reasons that are each testable:

1. **Direction.** `fraction = (landing - origin) / (end - origin)` is positive
   and increasing in path order whichever way the input travels
   (`machine.ts:356-360`), so a downward transition is drawn by the same rule
   as an upward one, with no `<=`/`>=` case analysis and no place for one of
   the two to be wrong.
2. **Rounding.** A whole-number input's drawn value is quantised (§5); a value
   comparison would then apply a commit a frame early or late depending on the
   rounding, where the elapsed fraction is exact and independent of it.
3. **It is the producer's own number for "where on the path".** ADR-129 states
   both and asserts nothing about which, and the fraction is what the corpus
   pins for every commit of every machine.

A request whose span is zero reports `fraction: 1` for its commits by the
producer's own rule, so such a transition lands its commits at the end of its
drawing — which is also where the drawing begins and ends.

### 5. The drawn value: `Ramp`'s rule, and one deliberate difference

Linear, as `Ramp.valueAt` is (`drivers.ts:74-80`) — the pilot asked for "just
like the fast_curta", and `Ramp` neither eases nor scales. Endpoints are
contract and intermediate values are sampling, also as `Ramp` has it: at or
past the duration the value is `end` ITSELF rather than a computed
approximation of it, so the last frame stands on the float the machine stood
on.

The one difference is a whole-number input. `Ramp` adds `Math.floor(delta)`,
which on a FALLING ramp overshoots by up to one native unit; a drawn value
that passes the machine's own `end` would show a tooth the machine never
turned. The drawing truncates toward the origin instead — identical to
`Ramp`'s floor for a rising travel, which is every posed instruction this
package has ever played, and never past `end` for a falling one. The
difference is stated here rather than silently introduced, and `Ramp` is not
changed: a posed document's ramps are not this cycle's business.

### 6. The duration is WALL seconds, and the playback speed does not scale it

The clocked chrome DOES carry a speed (`ClockTransportPlan.speed`,
`ladderFor`), but it belongs to things that have machine time — the timeline's
loop and the clock's transport — and ADR-063 gave it exactly that meaning:
how fast a SECOND of the machine's own time is watched. An instruction's
duration is not machine time at all: ADR-129 §4 says the machine does not read
it, and a machine with no clock has no transport and no speed on the panel
while still declaring instructions.

So a drawing runs on wall seconds, at the declared duration, exactly as the
posed `Ramp` does — which is also what "just like the fast_curta" means, since
`fast_curta`'s ramps ignore the speed control today. Recorded as a reversible
working assumption and raised as open question 1: the pilot may want the speed
to scale a drawing, and that is one multiplication if so.

### 7. One solve per press, and the end pose that is computed but never seen

A request POSES the tree as part of itself — that is ADR-125's atomicity, and
this viewer implements it through the machine's `pose` hook so that a tree
which refuses the new bank leaves the bank standing (`viewer.ts:1039-1056`).
So `trigger` necessarily poses at the transition's END before it returns. The
drawing must not start from there.

It does not: `trigger` returns inside the press's own task, and the drawing's
frame 0 — the start bank, with the input at `origin` — is posed immediately
after, in the same task, before the browser paints. The end pose is COMPUTED
(and may refuse the request, which is the point) and never seen. Nothing in
`machine.ts` changes for this, and the atomicity contract is untouched.

The bank is therefore FINAL from the press: a readback during a drawing
reports the transition's end. That is the honest answer and the only one that
does not invent a second bank: what the drawing holds is a picture of a
transition that has already happened.

### 8. One authority over the pose: everything else LANDS the drawing

A drawing owns the pose while it runs. Anything else that would move or
repose the machine — another press, a handle gesture, a host's `move`,
`restore`, `reset`, or the clock's own frame — LANDS the drawing first (the
drawn pose taking the transition's end, which is where the bank already
stands) and then acts.

This is the cheapest rule that is also the truthful one: the machine has
ALREADY made the transition, so landing it loses nothing, and every gesture
acts on a bank the maker can read. It settles the briefing's question
directly: pressing "Turn crank" twice quickly lands the first drawing and
draws the second from the bank it left, so two presses ARE two strokes and
the crank ends at 720°.

**Rejected: refusing a gesture while a drawing runs** (the running root's
"an instruction whose input the previous press still owns starts nothing").
That rule exists because a RUNNING command owns an input over TIME and two
owners would fight over one coordinate; a clocked request owns nothing after
it returns. Refusing would make a maker wait out a picture.

**Rejected: queueing presses.** A queue is a program, and sequencing is the
G-code layer's job — the same sentence ADR-129 quoted from `Instruction`'s own
docstring when it refused multi-input instructions.

Starting a drawing PAUSES the clock's transport where the machine declares
one (as `reset` already does, `viewer.ts:1171-1177`), and does not resume it:
a playing clock submits a request per frame, and two things posing one tree
per frame is the one conflict a maker cannot read. The Curta's clocked build
declares `clock: "time"`, so this is the acceptance document's own case and
not a hypothetical.

### 9. The chrome: pressable, indicating, reporting, and following

`ClockedInstructionControl` loses `disabled` and `reason` and gains
`outcome: ClockedOutcome | null`, which is exactly what
`RunInstructionControl` carries (`runControls.ts:105-107`). The button
indicates while its drawing runs (`aria-busy`, the running chrome's own
`outcomeWriter` treatment) and reports where it was pressed: `moved 360 deg`,
`moved 12 deg, held by knob.travel (high 0)`, or `refused: …`. The existing
`formatClockedOutcome` needs nothing.

While a drawing runs the panel FOLLOWS it, through one narrow writer
`ClockedChrome.follow(bank, input, value)` that rewrites the moved input's
field and slider and the readouts of the ids the drawing has committed.

**Rejected: rebuilding the panel per frame.** It is what every clocked gesture
does today, and the clock's transport does it 60 times a second — but the
Curta's panel is 23 inputs and 18 readouts, several hundred elements, and this
cycle claims that a frame costs a pose. Rebuilding would also destroy focus
and selection while a maker watches. The narrow writer mirrors the running
chrome's `rows`/`outcomeWriter` seam rather than inventing one.

**Rejected: leaving the readouts at the final bank.** They would disagree with
the model for the whole drawing, which is exactly the confusion the panel
exists to prevent. The Curta's registers are geometry, so this is a secondary
surface — but a cheap one to get right.

### 10. An instruction this viewer could not play is refused at LOAD

`readInstructions` (`document.ts:468-482`) currently accepts any object. For a
version 8 document it now validates what ADR-129 guarantees: exactly one of
`targets` and `by`; exactly ONE key in it; that key a declared DRIVER (not a
state, not the clock, not a name nothing declares); a duration that is a
finite number at or above zero. Each is refused BY NAME at load, on the
surface ADR-062 already refuses a malformed `clocked` object on.

A producer's compile refuses every one of these before a document exists
(ADR-129 §2), so a document carrying one is not a document with a quirk — it
is a document this viewer cannot trust to say what a press means. Refusing at
load keeps the invariant the producer bought: every instruction a loaded
version 8 document carries is one a maker may press, and the chrome needs no
arity logic.

### 11. The posed `trigger` under a clocked document

`ViewerHandle.trigger` ramps the DRIVER STORE (`viewer.ts:1626`). A version 8
document still reconciles that store (`viewer.ts:1208`), but it is posed from
the machine's BANK (`viewer.ts:456-458`), so those ramps move nothing anybody
can see. Today that is a silent no-op; after this cycle it is a trap — one
handle, one word, two meanings, and the wrong one does nothing at all. So it
is refused by name, pointing at `machine().trigger(name)`.

This is the one thing in the cycle that the Curta does not itself require, and
it is included because this cycle CREATES the ambiguity. It is one branch, one
message and one scenario, and it is flagged for the pilot to strike at
ratification if the evidence rule is meant to bite harder.

### 12. The API version rises to 19; `documentVersions` does not move

Playing a declared instruction is a capability a host may require before
mounting: a build at 18 lists the same button and refuses it, which is a
working page with a dead control rather than a loud failure. That is what the
version is for (16 → 17 for executing a clocked machine, 17 → 18 for running
its clock).

`solidNodeDocumentVersions` stays `[1..8]`: ADR-129 changed no field, no key
and no version, and a version 8 document published after it is byte for byte
the one published before. `bundle.py`'s `RELEASED_DOCUMENT_VERSIONS` is not
touched either.

### 13. The corpus: the fourth verb, both ends, and the census

`src/clocked-corpus.json` is re-copied from the producer, byte for byte, as
ADR-062 copied it: **145 673 bytes**, md5 `bc4174cf47f844b035125ed3afcee3aa`,
taken at solid-node branch `play-the-instruction` HEAD `2ab9505`. Measured
against the file this build carries (139 262 bytes, md5
`852b86b804ebd785f6e6b1f5568fb01a`):

| | before | after |
| --- | ---: | ---: |
| machines | 30 | 30 |
| steps | 76 | **81** |
| recorded numbers | 722 | **917** |
| machines with bounds / their steps | 13 / 36 | 13 / **41** |
| `tolerance.float` | 0.0 | 0.0 |

The growth is `Calculator`'s five new steps (12 `trigger: Set four`, 13
`snapshot: d`, 14 `trigger: Stroke`, 15 `restore: d`, 16 `move crank by
360`) and `origin`/`end` on every recorded request. The replay's
`replayStep` gains the `trigger` branch — it throws "unknown script step"
today, which is this cycle's corpus red — and compares both ends on every
step, refused steps included. The census is DERIVED from the file as it
already is, so the two "derived from the file" tests stay unchanged and the
numbers move with the copy.

Step 16 is the producer's own gift: the same request the instruction states,
made by hand from the same restored bank. A test asserts the two recorded
results are equal field for field AND that this engine reproduces both, so
"an instruction is a request and nothing else" is pinned in the viewer too.

### 14. The acceptance, and what is measured against what

**The committed acceptance** stays `tests/fixtures/calculator/`, re-exported
from the producer's own `tests/clocked_project/calculator.py:Calculator`,
which now declares `'Stroke': by crank 360 over 2 s` and `'Set four': targets
operand 4 over 0.5 s` — the Curta's own instruction and its absolute twin, on
a fixture with three bounds and six committing relations. The export is run
from a THROWAWAY COPY of the framework worktree, as its README already
records, so nothing is written into the read-only producer. The page presses
the button and reads, per frame, the panel the drawing follows: the crank's
reading rising, `w0.digit` unchanged until the frame the fraction reaches the
commit and changed from it on, the bank standing at the transition's end
throughout, and the two screenshots that prove the dials turned.

**The measurement** is the Curta's own two builds, where the pilot's
workspace has them (`_build/clocked_curta/viewer.json`,
`_build/fast_curta/viewer.json`, both READ-ONLY). Nothing is copied into this
repository: the harness serves a temporary directory of SYMLINKS to the
build's files beside the bundle and the page, and the test SKIPS with its
reason where the path is absent — this repository depends on nothing outside
itself, and a measurement is not a contract. What is recorded: frames per
second and the per-frame cost of a drawing of `'Turn crank'` on the clocked
build, against the same of `'Turn crank'` on the posed `fast_curta` build on
the same machine in the same session, plus the one-off cost of the
`trigger` itself (which the project measured at 36.95 ms in Chromium for the
same stroke through `move`).

The comparison is labelled for what it is: the clocked pose binds a bank of
41 values against the posed document's 8 drivers, so the two per-frame costs
are not the same work, and the claim being tested is "a clocked stroke can be
WATCHED", not "it costs what a posed one costs".

### 15. What is asserted UNCHANGED

- `src/run/` — the worker, the program, the running corpus: untouched,
  asserted by diff.
- `src/drivers.ts` — `Ramp`, `toNative`, the posed `trigger`'s ramps: the only
  change in this file is none; the posed refusal of §11 lives in `viewer.ts`.
- ADR-063's clock transport: the play/pause/step/speed path and
  `clockFrame` unchanged but for the drawing's pause (§8), asserted by test.
- The document: no key, no field, no version. `documentVersions` and
  `RELEASED_DOCUMENT_VERSIONS` unchanged, asserted by `version.test.ts` and
  `tests/test_version.py`.
- Every other fixture and every other Playwright acceptance: unchanged.

### 16. The ADR plan

ONE EXPORT ADR, candidate **ADR-064**, "A clocked instruction is one request,
drawn over its duration", extracted after implementation in the house style:

- **Extends** ADR-062 and ADR-063; **builds on** ADR-045, ADR-047 and ADR-048
  as the run's own request/outcome precedents; **consumes** solid-node
  ADR-129.
- **Amends** ADR-062 on ONE section, its "declared instructions are listed
  DISABLED": the house `**Amends:**` header plus "amends 062" in
  `docs/adrs/README.md`, which is this repository's own convention (there is
  no "Amended by" note in an amended record here — checked across
  `docs/adrs/EXPORT/`).
- **Considered and rejected**: per-frame requests, with the project's table;
  a drawing inside `machine.ts`; keying commits on the value; rebuilding the
  panel per frame; refusing or queueing a second press; scaling the duration
  by the playback speed.
- **Consequences**: a clocked stroke can be watched; published implies
  playable reaches the load; the API rises to 19; the document does not move.

### 17. What the evidence rule struck

Under `AGENTS.md` §"Every feature needs empirical evidence", and recorded in
the report:

- **A cancel, a pause or a scrub for a drawing.** Nothing asks. A drawing is
  two seconds of a transition that has already happened, and the next gesture
  lands it (§8).
- **A `done` promise or a drawing event on the handle.** The posed `trigger`
  returns `{done, cancel}` because a ramp is the only thing that moved; here
  the machine is final at once and the button reports. A host that needs the
  landing can read the panel or the pose, and no project has asked.
- **Easing.** `Ramp` is linear and the pilot asked for "just like the
  fast_curta".
- **A drawing over the CLOCK, or over several inputs.** The producer admits
  neither.
- **Any playback hint in the document.** ADR-129 rejected it on the producer's
  side; nothing here reads one.

One thing is admitted that the Curta does not exercise: the `targets=` form
(a drawing from `origin` to an absolute landing, over an integer driver). The
reason is the producer's own: version 8 publishes both forms, the corpus
exercises both — `'Set four'` is a recorded `trigger` step — and refusing one
here would cost a refusal, a message and a test to reject something the
contract requires this runtime to reproduce.

## Risks / Trade-offs

- **The Curta's per-frame pose may not be fast enough to look smooth.** 41
  bank values over a 39-commit machine is a bigger pose than anything this
  package has drawn per frame. Nothing in the design hides it: §14 MEASURES it
  against `fast_curta` on the same hardware and the number is recorded in
  `evidence.md` whatever it is. If a pose turns out to cost more than a frame,
  the finding belongs to the pilot and to a later cycle (the expression DAG),
  not to a widened claim here.
- **The bank is final while the picture is not.** A host reading `state()`
  mid-drawing gets the end. It is the honest answer (§7) and it is what makes
  "one solve per press" true, but it will surprise someone; it is stated in
  the requirement, in the interface and in the ADR.
- **The panel-follow writer is a second way to update the chrome.** Every
  other path rebuilds it whole. The writer is narrow, is used only while a
  drawing runs, and lands on a rebuild; the alternative was hundreds of
  elements per frame (§9).
- **Landing a drawing on any other gesture loses the rest of the picture.**
  Deliberate: the transition already happened, and the alternative is a maker
  who cannot act for two seconds (§8).
- **The duration is wall seconds while the panel shows a speed.** A maker at
  0.1× watching a pendulum may expect the button to slow too (§6, open
  question 1).
- **Two scenarios are replaced rather than carried.** Both now assert the
  opposite of what is true; the replacement is named in the proposal, as
  `run-the-clock` named its own.

## Open Questions

1. **Should the playback speed scale a drawing's duration?** This design says
   no (§6), matching the posed `Ramp` and ADR-063's meaning of speed. One
   multiplication either way; cheap to settle now, and the answer is
   observable on the Curta, whose clocked build declares a clock and therefore
   shows the speed control.
2. **Should the viewer handle's posed `trigger` be refused under a clocked
   document (§11), or left as the silent no-op it is today?** The design
   refuses. It is the one surface here the Curta does not need.
3. **What should the button do while its own drawing runs — indicate only, as
   designed, or also re-press?** It re-presses (§8, two strokes). Recorded so
   the pilot can say otherwise before the acceptance pins it.

## Planned proof

Every test below is RED FIRST, run and SEEN to fail for the stated reason
before the change that turns it green. The widget suite is `npx vitest run`
and `npx tsc --noEmit` in `solid_node_viewer/widget`; the Python suite is
`pytest` from the worktree root. `npm ci`, `npm install` and
`scripts/check-dist` are NEVER run here (the symlinked `node_modules`).

### 18. Fixtures

- `src/clocked-corpus.json` — the producer's regenerated file, byte for byte
  (§13). Its md5 and byte count are asserted, as they are today.
- `tests/fixtures/calculator/` — re-exported from a throwaway copy of the
  producer at `2ab9505`, carrying the two new instructions. Its README records
  the new size, md5, the commit and the identity finding it already carries.
- No new fixture is invented: the corpus and the Curta-shaped machine are what
  this cycle is about.

### 19. Tests, per requirement

**"The viewer plays a clocked instruction as one drawn transition" (ADDED)**

1. `src/clocked/machine.test.ts`: `trigger('Stroke')` over the corpus's own
   `Calculator` returns the request `move('crank', {by: 360})` returns from
   the same bank — field for field, ends included — and leaves the same bank.
   RED: `trigger` throws by name.
2. The same for `'Set four'` against `move('operand', {to: 4})`, so the
   `targets` branch is proved and not inferred.
3. An unknown name is refused listing the declared names; the bank stands.
4. `src/clocked/drawing.test.ts`: over a hand-written request with two commits
   at known fractions, the drawn value at 0, at each commit's fraction, just
   before it, and at 1; the bank at each; the last frame equal to the request's
   `end` and to the machine's own bank, value for value.
5. Direction: the same over a request whose `end` is below its `origin` —
   the commits apply in path order at the same fractions.
6. A whole-number input is whole at every frame and never passes `end`, rising
   and falling.
7. `duration: 0` lands in one frame; a request with `admitted: 0` and a stop
   draws nothing; a zero-span request's `fraction: 1` commits land at the end.
8. ONE SOLVE: the drawing is constructed and advanced 200 times with no
   machine in scope at all (the module takes none), and the machine's bank
   read at every step of a page drawing is the same bank (§20, the page).

**"The viewer executes a clocked machine's requests" (MODIFIED)**

9. `machine.test.ts`: a `by` request from a non-zero start reports `origin`
   equal to the bank before and `end` equal to the bank after; every commit's
   value lies between them. A CLIPPED request reports the stop's landing as
   `end`; a zero-travel request reports them equal; a `to` request over an
   integer driver reports the converted native value. RED: the fields do not
   exist.

**"A clocked machine the viewer cannot execute is refused by name" (MODIFIED)**

10. `src/clocked/document.test.ts`: a document whose instruction names two
    drivers, names none, states both forms or neither, names a state, names
    the clock, names nothing declared, or declares a duration that is
    negative, infinite, NaN or not a number — each refused at load, by name,
    naming the instruction. RED: each loads today.
11. The cadence refusals for `rate` and `step` still fire with their own
    messages (regression), and `trigger` is no longer among them.

**"The two runtimes agree on the clocked corpus" (MODIFIED)**

12. `src/clocked/clocked-corpus.test.ts`: the census FIRST, moved to the new
    file's derived numbers (30 machines, 81 steps, 917 numbers, 13 bounded
    machines over 41 steps) — red before the file is copied, naming the
    difference. Then the file copied, and the replay red on `Calculator` 12
    and 14 with "unknown script step".
13. Both ends compared on every step; the md5 and byte count asserted.
14. `Calculator` step 14 and step 16 — the trigger and the same request by
    hand — reproduced by this engine and equal to each other field for field.
15. The two "derived from the file" tests unchanged and still green.

**"A maker operates a clocked machine on screen" (MODIFIED)**

16. `src/clockedControls.test.ts`: a listed instruction is pressable, carries
    the outcome it was given, and no longer carries a reason; the layer's
    other contents are unchanged (regression over the existing tests).
17. The follow writer's decisions, where they are decisions rather than DOM:
    which ids a frame changed, from the drawing's own `moved`.

**"A host triggers declared instructions" (MODIFIED)**

18. The posed `trigger` under a clocked document is refused by name (page
    test, §20, since the refusal is in `viewer.ts`).

**"The viewer declares its API version" (MODIFIED)**

19. `src/version.test.ts` and `tests/test_version.py`: 19, and
    `documentVersions` still `[1..8]`.

### 20. In a real browser

`tests/test_calculator_document.py`, beside the existing acceptance:

20. Press `.clocked-instructions button` for `'Stroke'` and sample, per
    animation frame: the crank's panel reading (strictly rising over the two
    seconds), `w0.digit`'s readout (unchanged until the frame the drawing
    reaches the commit, then `4`), and `machine.state()` (the SAME bank at
    every sample — proof that nothing was solved per frame).
21. When it lands: the bank equals one `move('crank', {by: 360})` from the
    same start, and the panel equals the bank.
22. Two presses in quick succession leave the crank at 720 with two strokes
    committed.
23. A press while a drawing runs on another control, and a `restore` during a
    drawing, both land it first.
24. Screenshots before and after, written to `tests/_shots/`, showing the
    dials turned — pixels are evidence.
25. The posed `viewer.trigger('Stroke')` is refused by name on the same
    document.

`tests/test_curta_drawing.py` (new, SKIPPED where the build is absent):

26. The Curta's clocked build mounted from a symlink directory, `'Turn crank'`
    pressed, frame times recorded over the whole drawing; then `fast_curta`
    mounted and its own `'Turn crank'` played, frame times recorded the same
    way. Both printed and written into `evidence.md`. Nothing asserted about
    the ratio; one assertion only, that the drawing produced more than one
    distinct pose — a drawing that renders once is the bug this cycle exists
    to remove.

### 21. Measurement plan

- Frames per second and per-frame milliseconds for a drawing of the Curta's
  `'Turn crank'`, against `fast_curta`'s posed ramp of the same name, same
  session, median and worst frame.
- The cost of `trigger` against the cost of the same `move` on the corpus
  `Calculator`, in thread, median of 20 — the difference should be two
  dictionary lookups, and the claim "an instruction is a request and nothing
  else" is false if it is not (the producer measured +0.22%).
- The bundle's size before and after, stated rather than discovered later.
- The full widget suite's wall time before and after (the base is 45 files,
  1168 tests, 31.9 s).
