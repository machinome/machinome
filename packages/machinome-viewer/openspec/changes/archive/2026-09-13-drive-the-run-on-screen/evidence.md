# Evidence — drive the run on screen

Every number below was produced in the worktree
`solid-node-viewer/WTs/open-run-simulation` (branch `open-run-simulation`),
with the widget suite run from `solid_node_viewer/widget` and the Python
suite with the workspace venv and `PYTHONPATH` at the repository root.

## 0. Before anything else

### 0.1 `run-in-the-worker` is implemented and integrated

`git log --oneline -3` at the start of this change:

```
8574c0a feat(run): execute a published program in a worker
3ee1236 openspec: propose running a version 5 document in a worker, and driving it on screen
6fb082b fix(viewer): restore passive calibration readouts
```

`openspec/changes/archive/2026-09-13-run-in-the-worker/` holds the archived
cycle, and `src/run/` holds the engine, the worker, the runtime and the
`run()` handle this change drives. The head this change starts from is
`8574c0a4011a5f163797ca899688a56ecd89ea85`.

### 0.2 The baseline

```
$ npm run typecheck          # solid_node_viewer/widget
(clean)
$ npm test
 Test Files  26 passed (26)
      Tests  482 passed (482)
$ npm run build
  dist/solid-widget.js  631.6kb
$ python -m pytest tests -q
62 passed, 1 skipped, 11 warnings in 23.82s
```

The one skip is `tests/test_server.py:170`, "development app not built
(npm run build)" — the React development app, which this repository does
not build in the bench.

## 1. The running chrome, decided as data

### 1.1 / 1.2 / 2.6 / 3.1 RED

`src/runControls.test.ts`, the `formatElapsed` block appended to
`src/playback.test.ts`, the two blocks appended to `src/options.test.ts`
and `src/run/republish.test.ts` were written first and run against the
tree as `run-in-the-worker` left it:

```
 FAIL  src/runControls.test.ts [ src/runControls.test.ts ]
Error: Cannot find module './runControls' imported from '…/src/runControls.test.ts'
 FAIL  src/run/republish.test.ts [ src/run/republish.test.ts ]
Error: Cannot find module './republish' imported from '…/src/run/republish.test.ts'
 FAIL  src/playback.test.ts > formatElapsed > writes minutes, seconds and hundredths below an hour
TypeError: (0 , formatElapsed) is not a function
 FAIL  src/playback.test.ts > formatElapsed > grows an hours field at an hour and keeps it
TypeError: (0 , formatElapsed) is not a function
 FAIL  src/playback.test.ts > formatElapsed > rounds into the next second rather than showing sixty
TypeError: (0 , formatElapsed) is not a function
 FAIL  src/playback.test.ts > formatElapsed > holds one width while its leading field holds its digits
TypeError: (0 , formatElapsed) is not a function
 FAIL  src/playback.test.ts > formatElapsed > never narrows once it has widened
TypeError: (0 , formatElapsed) is not a function
 FAIL  src/playback.test.ts > formatElapsed > reads zero for a clock that has not started
TypeError: (0 , formatElapsed) is not a function
 FAIL  src/options.test.ts > resolveOptions: the run > defaults to 1/240 s, a 600-tick record, and NOT started
AssertionError: expected { dt: 0.004166666666666667, …(2) } to deeply equal { dt: 0.004166666666666667, …(4) }
 FAIL  src/options.test.ts > resolveOptions: the running controls > takes a nudge amount and duration the host chooses
AssertionError: expected undefined to deeply equal { amount: 5, seconds: 1 }
 FAIL  src/options.test.ts > resolveOptions: the running controls > takes either half of a nudge on its own
AssertionError: expected undefined to deeply equal { amount: 36, seconds: 0.2 }
 FAIL  src/options.test.ts > resolveOptions: the running controls > takes a jog rate in design units per simulated second
AssertionError: expected undefined to deeply equal { rate: 0.25 }
 FAIL  src/options.test.ts > resolveOptions: the running controls > refuses a request it could never issue, naming the value
AssertionError: expected [Function] to throw an error
 FAIL  src/options.test.ts > showsRunControls > shows the running chrome for a document that carries a program
TypeError: (0 , showsRunControls) is not a function
 Test Files  2 failed | 25 passed (27)
      Tests  14 failed | 482 passed (488)
```

### 1.3 GREEN

`src/runControls.ts` (the layer, `runInputControl`, `transportPlan`,
`formatOutcome`, `DEFAULT_NUDGE`, `DEFAULT_JOG`), `formatElapsed` in
`src/playback.ts`, `run: {nudge, jog}` and `showsRunControls` in
`src/options.ts`, and `src/run/republish.ts`. None of them touches the
DOM.

```
 Test Files  28 passed (28)
      Tests  520 passed (520)
$ npm run typecheck
(clean)
```

## 2. The panel, the transport and the interactions

### 2.1 – 2.5 RED

The chrome has no node-side test bench, so its red is the Playwright
acceptance (task 5) and the export page, written BEFORE any of
`viewer.ts`'s panel existed and run against the tree with only the pure
modules green:

```
E  playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 30000ms exceeded.
E  Call log:
E    - waiting for locator("#host .run-controls") to be visible
FAILED tests/test_running_document.py::DrivenOnScreenTest::test_a_maker_drives_the_module_from_the_panel
FAILED tests/test_running_document.py::DrivenOnScreenTest::test_a_second_request_on_a_busy_input_is_answered_in_place
E  playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 60000ms exceeded.
E    - waiting for locator("#solid-widget .run-controls") to be visible
FAILED tests/test_running_document.py::RunningExportPageTest::test_the_export_page_runs_the_machine_from_a_static_directory
3 failed, 1 passed in 126.37s
```

### 2.2 The two bars never appear together

`src/tree.test.ts`, on the acceptance document itself:

```
it('is not animated for a document a committed bank poses')
  expect(document.version).toBe(5);
  expect(tree.animated).toBe(false);
```

and in the page, `#host .animation-controls` and `#host input[type=range]`
both count zero.

### 2.3 The jog's five release paths

`pointerup`, `pointercancel` and `lostpointercapture` are wired on the
button, which captures the pointer on press; the window's `blur` and a
`visibilitychange` to hidden are wired once for the whole chrome and
removed with it. Proved in the browser:

- the drive test presses a jog, **drags the pointer off the control** and
  releases — the release still reaches the captured button and the
  machine stops (`tens_entry` 0.7333, unchanged 500 ms later);
- `test_a_jog_ends_when_the_pointer_or_the_page_goes_away` holds a jog
  and dispatches the window's `blur`, then holds one and makes the page
  report itself hidden — each time the readout advanced and then stood
  still with the button still held.

### 2.6 The mount options

Red above; green in `src/options.ts`. `driverControls: 'none'` suppresses
the running chrome through `showsRunControls`, exactly as it suppresses
the posed one, and the whole run API is untouched by it.

## 3. A republish keeps the run only when it is the same machine

`src/run/republish.test.ts` (red: `Cannot find module './republish'`) and,
in a real browser, `RepublishedRunTest`: the Pascaline is driven one
`Add one`, paused, and republished twice through the same
`manifestChanged()` the development page calls.

- a **cosmetic** edit (a part's colour) republishes the same
  `program.identity`: the tick, the elapsed clock, the identity and every
  coordinate of the bank compare **equal** to what they were before the
  rebuild, and the panel says the run was kept;
- an edit to the **mechanism** (`program.identity` changed) disposes the
  run: the new identity is on the handle — so the document really was
  refetched — the tick and the elapsed clock are 0, `units_entry` and
  `units.drum.turn` are back at their rest values, the readout reads
  `0.0000`, and the panel says the machine was reset.

`tests/support.py`'s file server now answers `Cache-Control: no-store`,
because a browser answering the second fetch of one URL from its cache
would have tested the bytes of the first. That is what the first attempt
did, and it is how the reset case was caught:

```
E  AssertionError: '62bb22d2e374…' != 'a-different-mechanism'
E  : the republished document was not read
```

## 4. The capture

### 4.1 RED

```
FAILED tests/test_capture.py::MountOptionsTest::test_no_camera_means_the_viewer_frames_the_model
E  AssertionError: {'animation': 'external', 'time': 0.25} != {'animation': 'external', 'time': 0.25, 'driverControls': 'none'}
FAILED tests/test_capture.py::MountOptionsTest::test_a_camera_is_passed_through_verbatim
FAILED tests/test_capture.py::RunningStagedDocumentTest::test_an_animation_instant_is_refused_by_name_before_any_browser
E  AssertionError: CaptureError not raised
FAILED tests/test_capture.py::RunningCapturePageTest::test_the_rest_state_is_photographed_and_no_step_is_taken
E  AssertionError: None != '0'
FAILED tests/test_cli.py::CaptureCommandTest::test_the_options_reach_the_capture_as_mount_options
E  AssertionError: expected call not found.
5 failed, 23 passed
```

### 4.2 GREEN

`capture.py` reads the staged document before anything is copied or
started, and refuses a non-zero `--time` on one carrying a program by
name. The page it writes reports what it photographed — `data-tick`,
`data-clock` and `data-state` — and the test reads them back: the tick is
`0`, the clock is `0`, **every one of the twelve coordinates equals the
program's own published `initial`**, and neither chrome is in the
picture.

## 5. The acceptance: a maker drives the Pascaline

`tests/test_running_document.py::DrivenOnScreenTest`. Nothing in it calls
`run()` to move anything: every movement is a control a person can see.

- the panel presents three input rows labelled `hundreds_entry`,
  `tens_entry`, `units_entry`, each reading `digit`, with six nudge
  buttons and six jog buttons, three instruction buttons `Add hundred`,
  `Add one`, `Add ten`, and a transport carrying run/pause, step, a speed
  select, an elapsed readout and reset — and **no `input[type=range]` and
  no `.animation-controls` anywhere in the container**;
- ten presses of `Add one`, each awaited until the button stopped
  indicating its own run, each reporting `completed` at the button;
- `units_entry`'s readout reads **`10.0000`** and the run's own state
  says `units_entry === 10`;
- `tens.drum.turn` is **65.54** within `1e-9` relative — the framework's
  own number, the one the module's `test_the_second_carry_is_cumulative`
  pins — and mid-drive it is strictly between 0 and 65.54;
- pause then step advances the run by exactly one step and leaves it
  paused;
- a jog held for 700 ms at ×1 admitted 0.7333 digit, the pointer was
  dragged off the control before releasing, and the readout stood still
  afterwards; the committed state agrees with the readout to its four
  decimals;
- reset returns tick, elapsed and every coordinate to the mounted state,
  the readouts follow, the elapsed readout reads `0:00.00`, and the
  transport is left exactly as it was found;
- a second `Add one` while the first still owns `units_entry` reports
  `refused: 'units_entry' is already owned by a move command…` at the
  button, in place, with no page error, and the first movement lands its
  whole digit.

### 5.4 The screenshots, looked at

Three, in `tests/_shots/`, 800×600. The fixture's meshes are stand-in
unit cubes, so the machine reads as a scatter of small cubes with three
larger slabs (the three column bases); what moves is visible but small —
451 pixels differ between the rest and after-ten frames in the model area
below the panel, 537 between rest and mid-carry.

- **`pascaline-panel-rest.png`** — the panel at the top left: the
  breadcrumb `Pascaline`; `Instructions` with `Add hundred`, `Add one`,
  `Add ten`; `Inputs — ask the machine to move` with three rows, each
  `<name> 0.0000 digit [−][+] by [1] over [0.2] s [◂][▸] at [1] digit/s`;
  the transport along the bottom: `Run`, `Step`, `0:00.00`, `×1`,
  `Reset`. Every row is one line.
- **`pascaline-panel-mid-carry.png`** — after the fourth press, inside
  the source's carry window (it opens 3.194 digits into a revolution):
  `units_entry` reads `4.0000 digit`, `Add one` says `completed`, the
  transport reads `Pause` (the run is running), `0:09.16`, `×10`.
  `tens_entry` still reads `0.0000` — correctly: the carry drives the
  tens **drum**, which is a joint coordinate and not an input, and the
  bank is not rendered as a bank of editable registers.
- **`pascaline-panel-after-ten.png`** — `units_entry` reads
  `10.0000 digit`, `Add one` says `completed`, elapsed `0:23.83` at ×10.
  The cubes of the units column have turned a full revolution and those
  of the tens column part of one.

## 6. The whole suite

```
$ npm run typecheck          # solid_node_viewer/widget
(clean)
$ npm test
 Test Files  28 passed (28)
      Tests  521 passed (521)      # 482 before this change
$ npm run build
  dist/solid-widget.js  643.8kb    # 631.6kb before
$ python -m pytest tests -q -rs
SKIPPED [1] tests/test_server.py:170: development app not built (npm run build)
73 passed, 1 skipped, 11 warnings in 44.69s   # 62 passed, 1 skipped before
```

Every pre-existing test passes unedited except the four this change
deliberately changed, all of them named by the tasks:

- `src/options.test.ts` — `resolveOptions: the run > defaults …` now
  expects the `nudge` and `jog` the resolved options gained;
- `tests/test_capture.py` — the two `mount_options` assertions gained
  `driverControls: 'none'`;
- `tests/test_cli.py` — the same key in the options the command hands the
  capture.

## Deviations from design.md

1. **A control's BUSY state is a different question from its last
   report.** Design §5 risk 2 asks the instruction button to report
   `refused: … already owned` in place *and* to indicate busy until its
   own commands retire. One "last outcome" field cannot do both: the
   second press is refused while the first press's movement is still
   running, and writing that refusal cleared the busy mark. The chrome
   now counts the requests each control has in flight and indicates on
   that, while the text shows the most recent report. Caught by the
   acceptance, which read `units_entry === 0.0958…` where it expected a
   whole digit.

2. **`formatElapsed` takes the width its caller carries.** D6 asks the
   readout to widen once and never narrow; a pure function of seconds
   cannot remember what it has shown. It takes a `minWidth` and
   zero-pads its leading field, and `viewer.ts` carries the widest
   reading so far. **Reset puts that width back with the clock**:
   narrowing because a maker asked the machine to go back to the start
   is not the digits walking about as a run grows.

3. **`RunInputControl` carries the declaration** (`driver`), which §2's
   sketch does not list — for the same reason `controls.ts`'s
   `DriverControl` carries it: a committed frame re-derives one control
   from one native value, and the design-unit conversion needs the
   scale.

4. **`RunInstructionControl` extends `controls.ts`'s
   `InstructionControl` with `outcome`.** §2 says the instruction
   control is reused verbatim, and D7 says every control reports where
   the request was made. The interface is imported and extended, not
   copied, so there is still one definition of what an instruction
   control is.

5. **The capture suppresses the chrome** — `mount_options` gains
   `driverControls: 'none'`. §4 does not mention it; the capability's own
   transparency requirement does. The photograph is a page screenshot
   clipped to the canvas, so a panel over the canvas is *in* it: without
   this, every photograph of a version 5 document would carry the running
   panel and the transport bar, and the promise that every pixel not
   covered by the model is fully transparent would be false. It also
   takes the posed chrome out of a photograph of a driver-declaring
   document, which had been in one.

6. **The capture's mount page reports what it photographed** —
   `data-tick`, `data-clock` and `data-state` beside the existing
   `data-ready` and `data-error`. Nothing in the product reads them;
   they are the only way a test outside the browser can show that no
   step of the run was taken.

7. **The transport says `Run` and `Pause` in words**, where the
   animation bar uses ▶ and ⏸. The first screenshots rendered ⏸ as an
   empty box in the headless browser's font, and a maker meeting a
   machine for the first time should not have to guess. `Step` and
   `Reset` are words for the same reason.

8. **Reset leaves the transport exactly as it found it** — design open
   question 3's own proposal, adopted: a run that was running goes on
   ticking from zero, and the acceptance pauses before resetting for
   that reason.

9. **The breadcrumb is built by one function for both chromes**, taking
   the trail, the children, the focus callback and a class prefix,
   rather than a second copy of it. One meaning of "the focused layer"
   in the widget, rendered one way.

10. **`reload()` restarts the run; only `manifestChanged()` takes the
    republish rule.** §3 is about the targeted document update the
    development page performs; `reload()` rebuilds the tree from
    scratch, and a run rebuilt from scratch starts at the rest bank.

11. **`tests/support.py`'s file server answers `Cache-Control:
    no-store`.** Test scaffolding only; without it a browser answers the
    second fetch of one URL from its cache, and the republish tests test
    the bytes of the first.

12. **Task 5.1 reads the drum off the run, not off the panel.** The
    brief asked for "the tens drum readout"; D2 is explicit that only
    declared inputs get one — "internal mechanical state is not rendered
    as an extra bank of editable calculator registers" — so the
    acceptance reads `units_entry` on screen (`10.0000 digit`) and
    `tens.drum.turn` from the run's own state, which is what `tasks.md`
    5.1 asks for.

## 6.5 Design §6's open questions, for the pilot

1. **Should a nudge's amount come from the document?** One design unit is
   right for the Pascaline (one digit) and arbitrary for a millimetre
   axis. Whether a `Driver` declaration should state a nudge step is the
   framework's question, and the same one its §10 item 7 asks about a
   driver's domain. Until then a host sets it with
   `run: {nudge: {amount, seconds}}` and a maker edits it in the panel.
2. **Should the panel show the crossings and stops the run records?**
   They arrive on every frame and they are exactly what makes a carry
   legible. Not shown; a candidate for the dragging cycle.
3. **Should reset clear the pause?** It does not (deviation 8).

## What is not proved here

- **Constrained dragging of a part** is not in this change, by design.
  The next viewer cycle binds a pick to a declared input through the same
  command interface.
- **A blocked outcome's wording is not exercised against a real stop.**
  The acceptance document declares no `spans`, so nothing in it can block
  a nudge; `formatOutcome`'s blocked form is pinned in node
  (`blocked after 12.5 mm`) and the engine's `blocked` status is pinned
  by the framework's corpus, but no browser test has yet watched a
  control report one.
- **A refused tick's panel line is not exercised in a browser** for the
  same reason: no document in this repository refuses a tick. The wiring
  (`onRefusal` → the panel line, the run pausing, the line clearing on
  the next commit) is pinned by `runtime.test.ts`'s refusal test on the
  runtime side and read by eye on the chrome side.
- **Pointer capture** is proved in Chromium only; Firefox and WebKit are
  untested here, which is why the jog has five release paths rather than
  one.
