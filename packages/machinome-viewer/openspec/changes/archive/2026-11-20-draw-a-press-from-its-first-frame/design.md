## Context

A clocked machine's request is solved once, at the gesture, and the viewer draws the transition it reports over a duration (ADR-064 for a pressed instruction, ADR-065 for a gesture on a handle, ADR-073 for the gesture's tempo). Two doors in `viewer.ts` make such a drawn request: `clockedPlay(name)`, used by the instruction buttons and by the host's `machine().trigger(name)`, and `clockedRequest(id, request, draw = true)`, used by the panel's number field, slider and nudge pair (the comment "ONE DOOR with `clockedPlay`"). On the base, inside the click's own task, each does:

1. `landDrawing()`, which poses a running drawing at its end;
2. the request, whose `pose` hook (installed by `startMachine`) is called by `machine.ts`'s `posed(next)` with the bank the request is about to commit, before the bank is assigned. The hook calls `tree.update(clockedScope(next), posed(moved))` over the ids that differ from the standing bank, then `renderer.render`. `tree.update` prepares every affected transform (refusing a thrown, non-finite or non-composable one before any is copied, `refuse-nonfinite-clocked-pose`), copies them into the live groups, then evaluates every reached flexible part (`rebuild-only-changed-flexible-parts`: rebuilt only when a value moved). A throw from the hook refuses the request and the bank stands;
3. `rebuildClockedChrome()`, which reads `drawnBank ?? machine.state()`; `drawnBank` is null at this point, so the panel is built with the END values;
4. `startDrawing`, which stops a playing clock (a second rebuild), sets `clockedDrawing = { name, drawn, elapsed: 0 }`, indicates the button, and calls `drawFrame(drawn.advance(0))`: a second `tree.update`, from the end back to the origin, because `drawing.ts` measures frame 0's `moved` against the request's END bank, and a `follow` that rewrites the panel's fields to the origin;
5. `renderer.render` again.

The loop then calls `drawingFrame(elapsed)`, which adds the loop's wall delta since the previous frame to `running.elapsed` and poses `advance(running.elapsed)`. The first such delta spans the click's task.

On the Enigma I page (`workflow/evidence/enigma-press-path-2026-11-20.md`, script only, single run, viewer `fd334597`): a wheel step's click is 249 ms, of which 202 ms are the two tree updates (91 ms of it flexible evaluations); a Press is 381 ms, 320 ms in the two updates; the remainder (47 and 61 ms) holds the request, the panel's rebuild and both renders, which the method did not separate. A wheel step declared at 0.4 s draws its first frame 0.25 s after the click at about 0.6 of its travel and lands on the second; a Press draws 9 changing frames over its 2 s.

What the end pose in step 2 is for is written in ADR-064 ("The end pose is COMPUTED (and may refuse the request, which is the point) and never seen") and in the baseline requirement "Clocked final rendered transforms are admitted atomically": the final pose is part of the request's admission. A final pose refused by a transform, a colour condition, a parameter expression or molejo refuses the request. What it is not for is showing anything: step 4 overwrites it in the same task, and the browser presents only the second render.

## Goals / Non-Goals

**Goals:**

- A drawn transition is drawn over its declared duration counted from its first drawn frame, and that frame stands at the transition's origin, whatever the press cost and however late that frame comes.
- A drawn press does no tree update and no render whose result is not shown: its final pose is judged and not shown, the origin is never re-posed because the scene never left it, and nothing is rendered inside the press.
- Everything a request guarantees today holds: one request per gesture, solved once, before the first frame; every refusal the end pose makes today is made, with the same message, before the bank is assigned; a refused request leaves the bank, the scene and the panel as they stood, its report at the control that made it; the panel shows the origin at the first paint after a press; a frame of a drawing costs at most one tree update and never calls the machine; every scenario of the baseline drawn-instruction and on-demand requirements.

**Non-Goals:**

- Anything that lowers a part's resolution or a flexible part's sampling.
- The cost of a frame in the middle of a drawing, how a long frame in the middle of one behaves, the idle redraw, the expression store, the machine's solving, `machine.ts` and its `pose` hook interface, the clock's transport, any project's source.
- The flexible-refusal gap on the doors that publish their pose (see Decision 7): not widened, not repaired there.
- Viewer API (stays 30) and document versions (stay 1 to 14): verified in `widget/package.json` (`machinomeViewerApi: 30`, `machinomeDocumentVersions`). The mount handle, `machine()` and its verbs, `MachineOptions` and every published name are unchanged; `WidgetTree` and `FlexibleShape` are not exported by `src/widget.ts`.

## Decisions

### 1. A drawn request's final pose is judged, not shown

`WidgetTree` gains `admit(scope, changed)`: inside `withExpressions`, the same `prepareTransforms(scope, changed, …)` `update` runs, into a list that is then dropped, followed by a walk that calls `FlexibleShape.admit(scope)` on every flexible part `touchedBy` the change set, in the order `updateShapes` uses. `FlexibleShape.admit(scope)` evaluates every parameter as `evaluate` does; if the part has buffers and remembered values equal to them by `Object.is`, it returns (molejo accepted exactly these values when it built the present geometry); otherwise it builds the `{name: value}` record and calls molejo's `evaluate(spec, values)` with no buffers, which allocates fresh ones that are discarded. It writes nothing on the part: not the buffers, not `built`, not `needsUpdate`, not the bounds. Every throw propagates unchanged, so the refusal's message is the one `update` would give.

`update` itself is unchanged, and so is every caller of it.

The viewer's pose hook gets one closure flag, `judging`, false except while a drawn request runs. With it set, the hook computes `moved` as today and calls `tree.admit(clockedScope(next, time, bindingsTable), posed(moved))`, and neither updates the tree nor renders. `machine.ts` still calls the hook before assigning the bank, so a refusal still leaves the bank standing; the hook interface and `machine.ts` do not change. The flag is set in a `try`/`finally` around `started.trigger(name)` in `clockedPlay` when the declared duration is greater than zero, and around `started.move(id, request)` in `clockedRequest` when `draw` is true (a gesture's duration is known only from the admitted travel, after the request).

A judged request that starts no drawing leaves the scene where the bank was. When its bank differs from the one before (a gesture on an input whose declared tempo is zero, the one case: `gestureSeconds` is zero only for a zero admitted travel, which moves nothing, or for a declared duration of zero), the door publishes it with one `tree.update` over the ids that differ, then renders as today. That repeats the evaluation the judgement accepted, under the same scope, and so cannot refuse: transform and colour evaluation is a function of the scope (ADR-043's memo is keyed on it, `refuse-nonfinite-clocked-pose` Decision 5) and molejo's output is a function of the spec and the values (`rebuild-only-changed-flexible-parts` Decision 3). A judged request that moved nothing (an interlock holding it at zero travel) needs no publication.

Measured on this bench during the proposal with a prototype of `admit` (since removed): a rigid node translated by `(2 * v.lift)` beside a spring whose `height` is `sqrt(10 - v.lift)`, mounted at lift 0; `admit` at lift 3 made one molejo call and left the rigid translation at 0 and the spring's positions and attribute version as they were; `admit` at lift 12 threw `values: parameter 'height' must be a finite number, got nan …` with the rigid translation still 0, where `update` at lift 12 threw the same message with it at 24; a following `update` at lift 3 made one molejo call.

Alternatives rejected:

- *Publish the end pose without rendering it, and pose the origin at the first frame.* It keeps two whole-tree updates per press (one moved into the first frame, which then shows the picture already on screen), and the scene would stand at the end between the click and that frame, where any other render (`setTime`, `setVisible`, a highlight, `setView`, a republish) would show it.
- *Skip the end pose for a drawn request.* A final pose the tree would refuse would be banked, and the refusal would surface at the drawing's landing frame inside the animation loop; this is the weakening ADR-064 and `refuse-nonfinite-clocked-pose` forbid.
- *Judge flexible parts by their parameter values alone, without molejo.* Molejo's own refusals of a value would no longer refuse the request.
- *Keep the end pose and remove only the renders and the clock's deduction.* It fixes the jump and leaves two tree updates in the click, 202 ms of the wheel step's 249.
- *Make `tree.update` judge before it publishes on every door,* closing the flexible-refusal gap everywhere. Without swapping buffers it doubles the molejo work of every publishing request, including each frame of a playing clock; it is a separate change if wanted (Open Questions).
- *A retained scratch buffer per flexible part for the judgement.* It doubles the retained vertex memory of every part ever judged; molejo's own allocation is released after the call.
- *A `draw` flag in `MachineOptions.pose`.* `machine.ts` is the pure library the corpus replays and knows nothing of drawings; the viewer owns which of its requests it draws.

### 2. The drawing starts where the scene stands

Because nothing was shown, the scene and every flexible part stand at the bank the machine stood at before the request. `drawing.ts` therefore measures the first frame's `moved` against `start` (a copy of the bank it is given) instead of `bankAt(1, end)`. Frame 0 (`advance(0)`) then moves exactly what differs from `start`: its value is `origin`, which is `start[input]`, so it moves nothing unless a commit carries a fraction of 0. None can be expected (an event lands on the far side of its surface, and a request that did not travel reports its commits at fraction 1), and if one did, frame 0 would pose it, as frame 0 shows it on the base. `land()` from a fresh drawing moves every id the transition moves. The module comment and `DrawnFrame.moved`'s comment say so.

`startDrawing` returns whether it started a drawing. It stops a playing clock without rebuilding the panel, sets `clockedDrawing`, and calls `drawFrame(drawn.advance(0))`, which sets `drawnBank` to the origin bank and, by Decision 4, poses nothing. It no longer indicates the button. The two doors then rebuild the panel once (it reads `drawnBank`, the origin), indicate the instruction's button when a drawing started with a name, and call `renderer.render` only when no drawing started (a refusal, a zero travel, a zero duration, or the published case of Decision 1). The order in both doors becomes: land, take the bank, request, write the outcome, start the drawing, rebuild the panel once, indicate, render only if nothing is drawn.

### 3. The drawing's clock starts at its first drawn frame

`drawing.ts` gains a pure `drawingClock()`: an object whose `frame(wallSeconds)` returns the drawing's total elapsed seconds, 0 at its first call whatever it is given, and the sum of the wall seconds given to every later call. `clockedDrawing` holds one in place of `elapsed`, and `drawingFrame` poses `advance(clock.frame(elapsedWallSeconds))`. The first animation frame after a press therefore draws the origin; the declared duration is counted from that frame's timestamp; each later frame advances by its own wall delta, as on the base.

- *A busy main thread.* However long the press or anything else delays the first frame, that frame draws the origin. The cost is visible as a pause before the motion, not as travel skipped. Time from the click to the landing is the press, the wait for the first frame, and the declared duration.
- *A hidden tab.* Animation frames are paused, so a drawing started there (a host's `machine().trigger` from script) waits and plays from its origin over its declared duration once frames resume. On the base it landed at the first frame after resuming, whose delta spanned the hidden time. The bank is final from the request in both cases.
- *The middle of a drawing.* Unchanged: a long frame adds its whole delta, travel between samples is skipped, and a delta reaching the duration lands the drawing.
- *The first frame's own delta* is discarded whole. The second frame's delta is the first frame's own duration, which poses nothing (Decision 4).

Alternatives rejected: capping the first delta at a nominal frame (a constant, and a slow first frame still skips); stamping the drawing's start with `performance.now()` at the press (a second clock beside the loop's, and the wait for the first frame is still taken from the motion); putting the rule inside `Drawing` (ADR-064 fixed `advance` to take total elapsed seconds).

### 4. A frame that moves nothing poses nothing

`drawFrame` calls `tree.update` only when `frame.moved` is not empty; it still sets `drawnBank` and calls `follow`. On the base such a frame traversed the whole tree with an empty change set and changed nothing. This removes the traversal from the press (frame 0) and from the first drawn frame; in the middle of a drawing it applies only to frames whose truncated whole-number value and commits did not change, where it is a saving with nothing visible either way.

### 5. Every door

| Door | Changes? |
| --- | --- |
| `clockedPlay`, duration > 0 (button, `machine().trigger`) | Judged (Decision 1); no tree update and no render in the press; one panel rebuild reading the origin; clock from first frame. |
| `clockedPlay`, duration 0 (draws nothing) | Unchanged: the hook updates and renders, `clockedPlay` rebuilds and renders. |
| `clockedRequest`, `draw = true` (number field, slider, nudge) | Judged; as `clockedPlay` when a drawing starts; a zero tempo publishes (Decision 1); a zero travel or a refusal renders as today. |
| `clockedRequest`, `draw = false` (`clockFrame`, the panel's step) | Unchanged. |
| `machine().move`, `restore`, `reset`; the panel's reset | Unchanged: land, then the hook updates and renders. |
| `machine().trigger` on demand | Unchanged: refused by `assertFrameLoop` before any request. |
| `landDrawing` and its callers | Unchanged code. Landing a drawing that has drawn no frame poses the whole transition, from the start (Decision 2), which is where the scene stands. |
| A press while a drawing runs | The running drawing lands (one published update to its end, where the bank stands), then the new request is judged from there. |
| `dispose`, republish (`startMachine`, `manifestChanged`) | Unchanged; both read `drawnBank ?? machine.state()`, which now matches the scene from the press on. |

### 6. What can be seen between the click and the first drawn frame

Continuous mode. The scene: a pose reaches group matrices and flexible buffers only through `tree.update` (or a republish's `reconcile`, which poses from `drawnBank ?? machine.state()`); on a drawn press no update is made (Decision 1), frame 0 makes none (Decisions 2 and 4), so the scene holds the bank the machine stood at before the request, which is the transition's origin. Any render made by anyone before the first drawn frame (a host's `setTime`, `setVisible`, `setView` or highlight, a republish) renders that, and every `scope()` the viewer builds in that interval reads `drawnBank`, the origin. The canvas: the press renders nothing, so the browser keeps presenting the last frame drawn before the click, which is the origin. The panel: it is rebuilt once, after `drawnBank` is set, so its handles and readouts read the origin at the first paint; any later rebuild before the first frame (a focus change, a clock toggle) reads `drawnBank` too. The outcome text ("moved 360 deg") is shown at the press, as on the base; it is the report, not a reading. `machine.state()` reports the end, as the baseline requires.

On demand (ADR-077). There is no frame loop, `machine().trigger` is refused before any request, and the mount conditions remove the clocked panel, so no drawn request can be made. The doors that remain (`move`, `restore`, `reset`) still pose and render through the hook before they return. Nothing changes there.

### 7. Refusals, before and after

| Refusal | Where | Before | After, drawn doors | After, other doors |
| --- | --- | --- | --- | --- |
| By-name request errors, a backward clock, two writers at one event, a non-finite law, a level refusal, a constraint carried out of range by a commit (`judged`) | `machine.ts`, before `posed` | Hook not called; bank, scene, panel, flexible memory stand | Same | Same |
| An interlock (zero travel) | Not a refusal: admitted with its stop | Hook poses an unchanged bank | Judged unchanged bank; no drawing, no publication; render | Same as before |
| A pose operation that throws or is non-finite, a non-finite composition, an invalid colour condition | `prepareTransforms`, in the hook | Nothing copied; bank stands; no flexible part evaluated | Same | Same |
| A flexible parameter that throws | Hook, flexible walk | Rigid parts at the candidate; earlier reached parts in the walk rebuilt at the candidate with `built` at the candidate; the throwing part standing; bank stands | Nothing written: every part, rigid or flexible, and its memory stand | Same as before |
| Molejo refuses a value | Hook, flexible walk | As above, the refused part's `built` forgotten | Nothing written | Same as before |

In every row the bank stands, the panel is rebuilt from `machine.state()` with the refusal at the control that made it, and `clockedPlay` rethrows to the host's `trigger`. The gap the previous change recorded (its archived `evidence.md`, "Out of scope, found while proposing") is narrowed for the drawn doors, left as it is for the publishing doors, and widened nowhere. The baseline's "A request the viewer refuses for any reason SHALL leave the bank, the pose and the model exactly as they stood" therefore now holds on the drawn doors and still does not on the publishing ones for the two flexible rows.

### 8. Proof by counted work

`mount()` cannot run in vitest. The seams it can reach, and a browser test over a committed fixture:

**`clocked/drawing.test.ts`** (no DOM, no three.js, no machine):

- D1. "a drawing begins where the scene stands": `drawing(TWO_COMMITS, START, 4, false).advance(0).moved` is `[]`. Red on the base: `['m', 'n', 'x']`.
- D2. "landing a drawing that drew no frame moves the whole transition": `drawing(TWO_COMMITS, START, 4, false).land().moved` sorted is `['m', 'n', 'x']`. Red on the base: `[]`.
- C1–C3. `drawingClock()`: the first `frame(0.3)` returns 0; then `frame(0.1)` and `frame(0.2)` return `0.1` and `0.1 + 0.2`; a later long `frame(5)` adds 5, so a drawing advanced by it lands as on the base. Red on the base: the export does not exist. Checked during this proposal with a throwaway file: under vitest 3.2.7 a missing named import fails at the call (`(0 , drawingClock) is not a function`) and the file's other tests still run.

**`flexible.test.ts`** (molejo spy and helpers already there) and **`color.test.ts`**, on `WidgetTree.admit`:

- T1. Judging a moving candidate shows nothing: the fixture of Decision 1's measurement at lift 3; the rigid node's matrix, the spring's positions, attribute version and bounds (`computeBoundingBox`/`computeBoundingSphere` spies: no call) as they stood; one molejo call. A following `update` at lift 3 makes one molejo call and moves the rigid node to 6.
- T2. A reached part whose values equal its remembered ones costs no molejo call when judged (`min(46.8, (66.8 - valvetrain.lift))` from lift 0 to 3).
- T3. A molejo refusal while judging (lift 12): throws `/must be a finite number/`; rigid translation, positions and version stand; a following `update` at lift 3 rebuilds once.
- T4. A transform refusal while judging (the existing `sqrt(1 - valvetrain.lift)` sibling): throws `/later.*operation 0/`, no molejo call, nothing changes.
- T5. A parameter expression that throws while judging (`(1 + gate.on.x)` at `gate.on = 1`, as the previous change's test D): propagates; no molejo call; nothing written; a following `update` at the standing values makes no molejo call.
- T6 (`color.test.ts`). Judging a candidate that changes a chosen colour leaves the material's colour and identity; judging a candidate whose colour condition is invalid throws `/later.*color/i` with every matrix and colour standing.

T1 to T6 are red on the base because `admit` does not exist; their assertions are what the implementation is held to.

**Browser** (`tests/test_calculator_document.py`, a new class over the committed `tests/fixtures/calculator`, whose `'Stroke'` is `by crank 360` over 2 s on a non-integer driver and `'Set four'` is `targets operand 4` over 0.5 s). The harness wraps the WebGL context's draw methods as `test_widget_e2e.py`'s `test_reading_positions_draws_no_frame` does, and samples after the raw `requestAnimationFrame` as the existing drawn-instruction tests do, so a sample follows the viewer's own frame. No elapsed time is asserted.

- B1. Draw calls inside the click's synchronous task: `'Stroke'` 0, `'Set four'` 0, a whole-turn nudge of `crank` 0. Guard: `machine().move('feed', {by: 1})` (a publishing door) draws more than 0, so the probe counts. Red on the base: two renders' worth.
- B2. The panel's `crank` reading at the first animation frame after the press of `'Stroke'` is 0, exactly, as is the nudge's; the readings then rise to 360 and land, and `machine.state()` is the same bank throughout. Red on the base: the first frame is advanced by the loop's delta, so it reads above 0.
- B3. A slow press: the click followed in the same task by a 300 ms busy wait; the first frame's reading is still 0. Red on the base: about 300/2000 of 360, the Enigma's symptom on the calculator.
- B4. `partOnScreen` of a part the stroke moves, read in the click's task and at the first frame, equals its value before the click. A guard: it holds on the base in the click's task, and is red on the base at the first frame.

The reviewer's Enigma measurement (tasks 6.2) counts the tree work directly with the evidence file's probe, wrapping `WidgetTree.prototype.admit` beside `update`.

Rejected: extracting the press sequence from `viewer.ts` into a pure module so vitest can count its effects. It moves the doors, the landing and the panel's ordering out of the file that owns them, for a test whose red on the base could only be a missing module; B1 to B4 are red on the base for the behavioural reason.

### 9. Existing tests that pin the order or the count of a press

Vitest:

- `clocked/drawing.test.ts`, "reports as MOVED exactly the ids the frame changed": its first expectation, `advance(0).moved` equal to `['m', 'n', 'x']`, pins ADR-064's review decision that frame 0 is diffed against the end. It does not hold and is changed to `[]`, with its comment, and D1 states the new rule; its other four expectations hold. Confirmed during this proposal with the Decision 2 change applied to the base and reverted: 1 failed (that one), 15 passed.
- Every other `drawing.test.ts` test holds, including "draws NOTHING for a request admitted at zero travel" (start equals end) and "ONE SOLVE per press, structurally".
- `clocked/machine.test.ts`'s hook tests (the hook sees the bank before it is assigned; a hook that throws refuses) hold: `machine.ts` is unchanged. `clockedControls.test.ts`, `cost.test.ts` and the corpus tests do not reach `viewer.ts`. `flexible.test.ts`, `color.test.ts` and `tree.test.ts` hold: `update` is unchanged.

Python (browser tests that press a drawn instruction or gesture):

- `test_calculator_document.py`, `InstructionDrawnInABrowserTest`: `crankAtOnce == 0` (panel at the origin in the press's task), the rising readings, more than 10 samples, `machine.state()` the same bank throughout, the landing, two presses giving 720, the gesture and restore landings, `midDrawing < 360` (now 0 after one frame), and the digits sampled before each frame (the first being the press's own picture) all hold. One more frame of wall time is added to every drawing; nothing there asserts on it.
- `GestureDrawnInABrowserTest`: `crankAtOnce`, `bankAtOnce`, `readings[0] == 0`, the typed, slider and real-pointer drawings, the host's undrawn `move`, and `FREEZE` at 30 and 90 frames hold. The tempo checks are wall-time windows, and the added frame enters each wall: 10a (1.5 to 3.5 s), 10b (a twelfth between 1/24 and 1/6), 10c (1.5 to 2.5), 10d (below a quarter, above 0.05 s) and 10f (0.7 to 1.4) have margins of many frames. **10e is at risk**: it allows `4/60` s between the clipped gesture's wall and the declared rate on a travel of a few degrees, and one added frame interval uses part of that. Estimated, not measured: it holds while the calculator page draws above about 20 frames a second (ADR-065 recorded about 60 on this host). If it fails, the applier stops and reports instead of widening it.
- `test_curta_drawing.py` (skipped on this bench: the Curta's builds are absent): `atOnce` 0 holds; the frozen nudge with a budget of 2 frames at a 50 ms stride holds, because the second frame advances 50 ms; with a budget of 1 it would freeze at the origin.
- `test_clocked_pose_admission.py`, "continuous instruction refuses before drawing or committing" (`'Invalid'`, 0.1 s): the refusal now comes from the judgement, from the same `prepareTransforms`, with the same message; bank, `partOnScreen` and pixels stand. Holds.
- On-demand tests (`test_widget_e2e.py`, "a clocked machine mounts on demand and poses by restore", "an on-demand clocked mount shows no control"; `test_capture.py`'s clocked cases) and `test_state_color.py`'s clocked cases use publishing doors only. Unchanged.

### 10. What the Enigma should show (predictions)

Rest on: the end and origin updates of the click costing about the same (the evidence measured their sum only); the two renders' bookkeeping being part of the 47 and 61 ms remainders (not separated); the per-frame script of a drawing being unchanged (this change does not touch it); and judging costing about what publishing cost (the same evaluation, molejo allocating instead of refilling, no matrix copies). Two estimates in this campaign that scaled one figure were wrong, so these are predictions only:

- A drawn instruction's click: 0 outermost `update` calls, 1 `admit`, 0 draw calls. `Key B` (0 s): 1 `update`, 0 `admit`, as before.
- Press task: a wheel step about 100 to 150 ms (from 249), a Press about 160 to 230 ms (from 381); `Key B` unchanged.
- The first frame after the click changes nothing in the picture; the first changing frame is the one after it, at about a tenth of a wheel step's travel (an idle frame's 34 ms of script over 0.4 s), and in any case below a quarter.
- A 0.4 s wheel step changes the picture in 4 to 6 frames at the base's 79 ms a changing frame; the firm expectation is more than 2. A Press keeps about its 9 changing frames.

## Risks / Trade-offs

- [Every drawing takes one more frame interval from click to landing, because its first frame stands at the origin] → Accepted: it is the frame the motion is counted from. Test 10e's margin is the one place it is felt (Decision 9).
- [Judging allocates a fresh molejo buffer for each reached part whose values moved] → Released after the call. On the Enigma a wheel step judges one part of 122,928 triangles, a Press about seven to nine parts (the previous change's counts).
- [The publish fallback of Decision 1 evaluates a zero-tempo gesture's pose twice] → Only a gesture on an input whose first declared `by` instruction has a duration of zero. The calculator fixture has none; whether the Enigma declares one was not checked.
- [The scene, the panel and `drawnBank` stand at the origin while `machine.state()` stands at the end, for longer than one task] → This is the drawing's existing state; it now begins at the press rather than in the middle of it. Every reader of the pose reads `drawnBank ?? machine.state()` (Decision 5).
- [A drawn frame that throws in the middle of a drawing stops the animation loop: three.js 0.156's `WebGLAnimation` requests the next frame after the loop's callback returns] → Pre-existing and unchanged: intermediate points are not admitted, by the baseline's own rule. This change adds no frame that can throw: the first frame poses nothing.

## Migration Plan

No document, host or API migration. Rollback is the previous bundle.

## Decision record

The change alters what ADR-064 decided under "One solve per press, and the end pose that is computed but never seen" (the end pose is now judged and not posed, frame 0 is no longer posed in the press, nothing is rendered there) and the first-frame diff its review accepted, and it adds where a drawing's clock starts. After the reviewer's Enigma measurement and review of the implementation confirm the design, a dated amendment to ADR-064 records Decisions 1 to 4 and the measured figures; ADR-065, whose decision restates the press order ("start the drawing — whose frame 0 is posed in the same task — and render"), gets a pointer amendment. ADR-073 (the tempo) and ADR-077 (on demand) are unchanged.

## Open Questions

None technical. Two are the pilot's: whether the publishing doors should also judge before they publish, which would close the flexible-refusal gap there at the cost of Decision 1's rejected alternative; and whether a drawing started in a hidden tab should play on return, as this design makes it, or land.

## Found while proposing, out of scope

- A frame of a playing clock renders three times: the hook renders inside `clockFrame`'s request, `clockedRequest` renders after its rebuild, and the loop renders. The panel's step renders three times likewise, and the panel's reset follows the hook's update with an update of the whole tree (`'all'`). None of these is a drawn press.
