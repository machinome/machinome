# Evidence: follow-the-slider-as-it-is-dragged

Recorded by the applying agent on 22 November 2026 in the framework worktree
`machinome/WTs/follow-the-slider-as-it-is-dragged`, branch
`follow-the-slider-as-it-is-dragged`. Tasks 7.2 (the Enigma page) and 8.2
(the decision record) are the reviewer's and are not recorded here.

## The bench (task 1.2)

- `git log --oneline -3`: `b1729544 plan: follow the slider as it is
  dragged`, `f6119628 viewer: draw only when the picture changes`,
  `79e52106 plan: ...`. `git rev-list --count f6119628..HEAD` is 1; the
  planning commit changed no source (`git diff --stat f6119628 HEAD`: the
  change directory, `workflow/warts.md` and the opening evidence only).
  `git status --short` was empty.
- `openspec validate follow-the-slider-as-it-is-dragged --strict`: `Change
  'follow-the-slider-as-it-is-dragged' is valid`.
- Tools: vitest 3.2.7, jsdom 29.1.1, three 0.156.1 (the bench's
  `node_modules`); Playwright 1.63.0 on the bench's `.venv`.

## Facts checked before relying on them

- **jsdom.** jsdom 29.1.1 implements `PointerEvent`, `valueAsNumber` on a
  range input, and clamps a range input's value to its range (the pinned
  thumb of R9 reads 1 after the host moved `open` to 1.4). It implements no
  drag of a range input, as the design says.
- **The hand-written documents load** and behave as the design states,
  checked in node through the real `loadClocked` and `clockedMachine`
  (a scratch script, deleted): on FOLLOW, `press` 0 to 0.2, 0.7, 1, 1.3, 1.4
  leaves `count` 0, 0, 1, 1, 1 (a request starting on the surface at 0
  fires nothing), 1.6 is admitted to 1.5 with the stop `block.travel (high
  1.5)`, 1.8 from 1.5 is admitted at zero travel with the same stop; one
  request to 1.4 gives `count` 1; `scaled` to 4 design units holds 2. On
  FINE, 0.1, 0.2, then 0.75 and 0.8 refused, then 0.3, 0.4, 0.55 leave
  `{fine: 0.55, teeth: 5}`, and one request of 0.55 from 0 is refused.
- **A refusal's message is not the same for two refused positions** (a
  stated fact that is false; see "Departures", 1). The two refusals of R11
  read `the request move('fine', by=0.55) would cross 5 surfaces ...` and
  `... by=0.6000000000000001 would cross 5 surfaces ...`: the message
  names the request. Design Decision 4's "Later positions that repeat a
  stop or a refusal produce the same text" holds for stops and not for
  refusals.
- **A republish of a version 8 document keeps the machine whatever its
  identity** (a stated fact that is false for version 8; see
  "Departures", 2). `manifestChanged` calls `startMachine` only when
  `document.version === 14` (base `viewer.ts` 2302-2305); for a version 8
  document neither `machine` nor `loadedMachine` is replaced. Design
  Decision 5's "When `startMachine` replaces the machine (1295, called at
  1783 and 2304)" is right for a reload (1783) and for a version 14
  republish (2304) only.
- **A reload replaces the machine before its `refreshControls`** (see
  "Departures", 3): `replaceTree` calls `startMachine` (1783) and then
  `refreshControls` (1812), so the design's door for a reload,
  `refreshControls`, would come after the press was dropped.
- **The order of events in Chromium** (B4, on the base bundle and again on
  the implementation's): recorded below. It holds the design's table.

## Red on the base (tasks 2.2 and 2.3)

### The widget tests

`src/follow-the-slider.test.ts` run alone on the base source, after the
last edit to the test file (the implementation's `viewer.ts` was set aside
and the base's, byte-equal to `HEAD`, put back for the run; `git diff
--stat -- src/viewer.ts` printed nothing; the implementation was restored
and confirmed byte-equal afterwards): **40 failed, 4 passed (44)**. Each
red test fails at its first assertion that reads the change's behaviour,
for the reason below; none at a fixture, import or setup error.

| Test | Base | Reason shown |
|---|---|---|
| R1 | red | `the frame after the thumb reached 0.2: expected [] to deeply equal [ [ 'press', { to: 0.2 } ] ]` (no request where one is due) |
| R2 | red | `the release made a request: expected [ [ 'press', { to: 1.4 } ] ] to deeply equal []` (a request made by the release's `change`). The window-listener assertion before the press, which comes first, passed: the base mount adds no `pointermove`, `pointerup` or `pointercancel` listener to the window. |
| R3 | red | `expected [] to deeply equal [ [ 'press', { to: 0.7 } ] ]` (no request) |
| R4 | red | `the release did not ask the last position: expected [] to deeply equal [ [ 'press', { to: 0.9 } ] ]` |
| R5, pointercancel, lostpointercapture, pointerup elsewhere | red | `the pending position: expected [] to deeply equal [ [ 'press', { to: 1.8 } ] ]` |
| R5, window blur, hidden page, blur on another element | red | `expected [] to deeply equal [ [ 'press', { to: 0.8 } ] ]` (the next position is not followed, because nothing is) |
| R6, track press held | red | `the track press made no request at its input: expected [] to deeply equal [ [ 'press', { to: 1.2 } ] ]` |
| R6, click | red | the request count held (`[['press', {to: 1.2}]]`, asserted first) and the drawn path equalled the constant recorded on the base; then `the thumb right after the click: expected +0 to be 1.2` (the rebuild wrote the thumb back to the origin) |
| R7 | red | `expected [] to deeply equal [ [ 'press', { to: 0.4 } ] ]` |
| R8, released during the jump | red | `the release did not wait for the jump: expected [ [ 'press', { to: 0.6 } ] ] to deeply equal [ [ 'press', { to: 0.4 } ] ]` (the release's `change` made the request) |
| R8, a host request during the jump | red | `expected [ [ 'press', { to: 0.6 } ], ...(1) ] to deeply equal [ [ 'press', { to: 0.4 } ], ...(2) ]` |
| R9 | red | `the pinned thumb's first position: expected [] to deeply equal [ [ 'open', { to: 0.9 } ] ]` |
| R10 | red | `expected +0 to be 1.5` (the bank stood at 0) |
| R11 | red | `expected +0 to be 0.2` |
| R12 | red | `expected 1 to be 2` (the release's one request to 1.3 committed once) |
| R13 | red | `expected 1 to be 2` (the bank stood at 1) |
| R14 | red | `expected [] to deeply equal [ [ 'scaled', { to: 4 } ] ]` |
| R15 | red | `the drawing wrote the held thumb: expected 0.048 to be 0.3` |
| R16, every door that asks (host move, restore, reset, trigger, `setClockPlaying(true)`, an instruction pressed, a typed value, a nudge, `setRoot` and back, `reload()`, `manifestChanged()` with the same machine, version 8 and version 14) | red | `<door>: the pending position was never asked: expected -1 to be greater than or equal to 0` |
| R16, `manifestChanged()` with another machine (version 14) | red | `the old slider asked: expected [ { to: 1.1 } ] to deeply equal []`: the pending position was asked of no machine (that assertion, first, passed), and then the base's `change` on the replaced slider made a request of the new machine |
| R16, `dispose()` | **green**, as task 2.2 requires | |
| R17, no press while the clock plays | **green** (recorded constant `R17`) | |
| R17, with the clock paused, a drag is followed | red | `expected [] to deeply equal [ [ 'press', { to: 0.3 } ] ]`. This is the design's "With the clock paused, the same events are R1's", R1 on FOLLOW-CLOCK, kept as its own `it`; it is red on the base for R1's reason. |
| R18, a key, an input with no press, a typed value, a nudge | **green** (recorded constant `R18`) | |
| R18, a `change` one frame after a release | red | `the release's own change was a request: expected [ [ 'press', { to: 0.5 } ] ] to deeply equal []` |
| R19 | red | `the frame at 0.2: expected { draws: +0, named: +0 } to deeply equal { draws: 1, named: 1 }` |
| R20 | red | `expected [] to deeply equal [ [ 'press', { to: 0.4 } ] ]` |
| O1 | **green** (recorded constant `O1`) | |
| G1 | red | `196 of 200 sequences failed`, the first: `seed 1 after ... typed press: the last position: expected undefined` (the drag asked nothing); others `asked 0, not dispatched in order` (a request made by the release's `change` for a thumb pressed and let go), `the last position: expected undefined to be 4.812` |

The constants `R6.click`, `R17`, `R18` and `O1` were printed on the base as
`RECORDED <name> <json>` and written into the test as printed; they were
not regenerated, and the implementation reproduces each of them (the four
tests are green on it):

- `R6.click`: the click is one request, `[['press', {to: 1.2}]]`, and its
  field is drawn 0, 0.016, ... 1.184, 1.2 over 76 drawn frames.
- `R17`: on FOLLOW-CLOCK playing, a `pointerdown` and three positions on
  the slider, with three frames, made only the clock's three requests
  (`["time","time","time"]`), the clock still playing; a `change` on the
  panel's current slider was one request `[['press', {to: 1.2}]]`, rebuilt
  and replaced the panel, stopped the transport, and was drawn over 76
  frames from 0 to 1.2.
- `R18`: a key (`keydown`, a value, `input`, `change`) was one request
  `[['press', {to: 1}]]`, one rebuild, the panel replaced, drawn over 64
  frames; an `input` with no press asked and drew nothing; a typed value
  `4` in `wheel` was `[['wheel', {to: 4}]]`, one rebuild, drawn through
  whole numbers 0 to 4 over 85 frames; a nudge `-1` on `wheel` was
  `[['wheel', {by: -1}]]`, one rebuild, 22 frames from 4 to 3. The banks
  after each are in the constant.
- `O1`: an on-demand mount of FOLLOW presents no slider and is given no
  loop; the handle's `move` (three calls), `restore` and `reset` drew once
  each.

### The browser tests

The bundle built from the base source with `npm run build`: SHA256
`d1b7b0af54e27ac5ddb48be8f2a96114269ff0ed8a9141a96b6bb17ab84c780f`
(915.3 kB); a copy was kept under the widget's `.scratch/` while the work
lasted. `tests/test_follow_the_slider.py` alone on it: **4 failed, 1
passed, 1 skipped**.

- B1 red: `AssertionError: 0 != 0.124953606334282 : step 1: the bank is not
  the thumb`; the bank stood at 0 through all sixteen steps while the thumb
  went from 0.125 to 2.
- B2 red: `0 != 1 : step 1: the bank is not the thumb`; the thumb went 1,
  1, 2, ... 9 and the bank stood at 0.
- B3 red: `0 != 8 : the bank does not hold the pressed value from the first
  frame`; the field read 0 in all forty held frames.
- B4 green (a property of the browser). Recorded order, the leading
  `pointermove` being the hover that brings the mouse to the press point:
  - plain slider, track: `pointermove#1 pointerdown#1 input
    gotpointercapture#1 pointermove#1 input pointerup#1 change
    lostpointercapture#1`
  - plain slider, thumb: `pointermove#1 pointerdown#1 gotpointercapture#1
    pointermove#1 input pointermove#1 input pointermove#1 input
    pointermove#1 input pointerup#1 change lostpointercapture#1`
  - viewer's slider, track: `pointermove#1 pointerdown#1 input
    gotpointercapture#1 pointermove#1 input pointerup#1 change` (on the
    base the `change` rebuilt the panel, so the removed slider saw no
    `lostpointercapture`)
  - viewer's slider, thumb: as the plain slider's, without the
    `lostpointercapture`, for the same reason.
- B4's Firefox leg skipped: `Playwright's firefox is not installed at the
  revision it expects (/home/asa/.cache/ms-playwright/firefox-1543/firefox/firefox
  is absent)`. Firefox build 1538 is installed; this Playwright expects
  1543.
- B5 red: `0 != 0.249907212668564 : touch step 1: the bank is not the
  thumb`. Its tap on the track was drawn on the base (the field 0, 0,
  0.125, ... 1.4999 over thirteen frames), from the release's `change`.

`tests/test_calculator_document.py` alone on the same base bundle: **16
passed** in 54.6 s.

## The implementation (tasks 3.1 to 3.3)

Only `src/viewer.ts` changed among the sources; `clockedControls.ts` and its
test are untouched (the drag's outcome is three lines in the mount, not
pure data worth a module of its own).

- **The chrome** (`buildClockedChrome`, `buildClockedRow`): `ClockedChrome`
  gains `report(id, outcome)` (the row's outcome line, written only when
  its text differs) and `hold(id | null)`; the row writer skips the held
  thumb. The slider listens on `pointerdown`, `input`, `change`,
  `lostpointercapture` and `keydown`, each acting only while the slider is
  connected, through five new `ClockedChromeActions` entries
  (`pressSlider`, `slide`, `commitSlider`, `loseSlider`, `keySlider`). The
  field, the nudge pair and the amount box are unchanged.
- **The mount**: one `press` (a `SliderPress`: its slider, pointer, held,
  moved, the count of its positions, pending and last asked positions, the
  input's banked value and scale at the press, pinned, its own drawing, its
  report and its machine); `released`, the release's marker, cleared by the
  next frame; the pose hook's third mode (`following`), which updates the
  tree and records what it posed and does not draw; `askPosition` (the
  followed request: land a running drawing, one `move(id, {to})`, the
  drag's outcome, the narrow writes); `endPress`, `dropPress`,
  `releasePress`, `beginPress`, `pressFrame`; the window's `pointermove`,
  `pointerup` and `pointercancel` listeners in the capture phase, filtered
  by the press's pointer id, added in `beginPress` and removed in
  `releasePress`, `endPress` and `dropPress`. `clockedRequest` takes a
  fourth parameter, `pressed`, for a press's own drawn jump: no `endPress`,
  and `report` in place of the rebuild. `endPress()` is called first by
  `clockedRequest` (unless `pressed`), `clockedPlay`, `setClockPlaying`
  (after its refusals), `rebuildClockedChrome`, the panel's reset, step,
  step amount and speed, `refreshControls`, `focusOn` (after
  `assemblyNavigation.setRoot`), `replaceTree` (before `startMachine`), and
  the handle's `move`, `restore` and `reset`; `dropPress()` by
  `startMachine` and `dispose()`. `pressFrame()` runs in the loop after
  `drawingFrame`. No press begins while the clock's transport plays.
  Nothing else in `viewer.ts` changed: `moving()` has no term for a press,
  and the posed panel, the running panel and the part surface are
  untouched.
- **What stands on the window while no slider is held**: nothing of this
  change. R2 asserts that a mount adds no `pointermove`, `pointerup` or
  `pointercancel` listener to the window, and that every one a press adds
  is removed at its release; MU24 turns it red.

`tsc --noEmit`: no output, exit 0. `src/follow-the-slider.test.ts` alone on
the implementation: **44 passed (44)** in 56 s, G1 `0 of 200 sequences
failed; exercised {"drags":995,"asked":891,"jumps":588,"dropped":20,
"refused":103,"monotone":447}` (995 drags checked by A3, 891 positions
asked, 588 drawn jumps, 20 drags dropped by a republish that replaced the
machine, 103 refused requests, 447 monotone drags compared with one
request).

## Existing tests (task 4.1)

Each run alone, unmodified, on the implementation: `src/draw-on-change.test.ts`
62 passed; `src/clockedControls.test.ts` 21 passed; `src/clocked/drawing.test.ts`
21 passed; `src/clocked/machine.test.ts` 44 passed;
`src/clocked/clocked-corpus.test.ts` 47 passed; `src/controls.test.ts` 41
passed; `src/runControls.test.ts` 18 passed; `src/partSurface.test.ts` 36
passed; `src/picture-revision.test.ts` 22 passed. No existing test was
changed.

## Mutations (task 4.2)

Each applied alone to the implementation's `viewer.ts` (a saved copy, under
the widget's `.scratch/`, rewritten by exact text replacement), the whole of
`src/follow-the-slider.test.ts` run, its output kept, and `viewer.ts`
restored from the saved copy and confirmed byte-equal (`cmp`) before the
next. Every restore was byte-equal. The tests that went red (G1 with its
count of failed sequences out of 200):

| Mutation | Design says red | Red |
|---|---|---|
| MU1 every position followed | R6, R7, R9 | R6 (both), R7, R8 (released during the jump), R9 |
| MU2 every position drawn | R1, R3, R19 | R1, R2, R3, R4, all six R5, R7, R8, R9, R10, R11, R13, R14, R15, twelve R16 cases, R18 (change after a release), R19, G1 (126) |
| MU3 the pinned clause removed | R9 | R9 |
| MU4 positions asked in the input's task | R3, R1 | R1, R3, R5 (the three that end nothing), R7, R8, R9, twelve R16 cases, R19, G1 (114) |
| MU5 the pending position kept after it is asked, and asked every frame | R3 | R3, R5 (the three that end nothing), G1 (87) |
| MU5a the pending position kept, the "never twice in succession" check kept | (not in the design) | **nothing**: the check that a pending position differing from the last asked is the only one asked holds the rule by itself; MU5 removes both |
| MU6 nothing asked when a press ends | R4, R5 | R4, R5 (the three endings), R8 (both), twelve R16 cases, R20, G1 (97) |
| MU7 the release's `change` not ignored (the marker's check removed) | R2, R6 | R2, R10, R11, R12, R14, R18 (change after a release), G1 (61). **R6 not red**: in both R6 cases the release comes while the press's own drawn jump is still being drawn, so the press still lasts and its `change` is ignored by the press's own check, not by the marker |
| MU8 the marker not cleared by the frame | R18 | R18 (change after a release) |
| MU9 the panel rebuilt at the end of a press | R2 | R2, R6 (track press held), R18 (change after a release), R20, G1 (14) |
| MU10 the held thumb written | R1, R6, R10, R15 | R6 (track press held), R10, R15. **R1 not red**: a followed request writes the thumb at the bank's position, which in R1 is the pointer's position, so the write changes nothing R1 reads |
| MU11 the hook draws in its new mode | R19 | R4, R19 |
| MU12 a held press counted as moving | R3 | R3 |
| MU13 a press begins while the clock plays | R17 | R17 (no press while the clock plays), G1 (1) |
| MU14 `clockedRequest`'s | its R16 case | R16 typed value, R16 nudge, G1 (11) |
| MU14 `clockedPlay`'s | its R16 case | R16 host trigger, R16 instruction pressed, G1 (9) |
| MU14 `setClockPlaying`'s | its R16 case | nothing: **equivalent** to the catch-all, since `setClockPlaying` does nothing but set a flag before its rebuild, whose `endPress()` asks first |
| MU14 `rebuildClockedChrome`'s (the catch-all) | | nothing: every door carries its own call, as the design expects |
| MU14 the panel's reset | | **nothing, and not equivalent**: the panel's Reset button resets the machine before its rebuild, so without its own call the pending position would be asked after the reset. No R16 case and no G1 step presses the panel's Reset button; the gap is reported, not closed |
| MU14 the panel's step | | nothing: equivalent, its `clockedRequest` ends the press first |
| MU14 the panel's step amount | | nothing: equivalent to the catch-all (it sets a number, then rebuilds) |
| MU14 the panel's speed | | nothing: the speed select makes no request and no rebuild of the clocked panel; its call protects nothing a test can see |
| MU14 the reload's (in `replaceTree`) | its R16 case | R16 `reload()`, G1 (8) |
| MU14 `refreshControls`'s | its R16 case | nothing: equivalent to the catch-all (`refreshControls` rebuilds the posed and running chromes, which do not touch the machine, then the clocked one) |
| MU14 `focusOn`'s | its R16 case | nothing: equivalent to the catch-all, for the same reason (`applyFrame` moves the camera, not the machine) |
| MU14 the handle's `move` | its R16 case | R8 (a host request during the jump), R16 host move, G1 (9) |
| MU14 the handle's `restore` | its R16 case | R16 host restore |
| MU14 the handle's `reset` | its R16 case | R16 host reset, G1 (5) |
| MU15 `startMachine` keeps the press | R16 different identity | **nothing**: `endPress` and `askPosition` ask only the machine the press was begun on (`machine === press.machine`), so a press that survives a replaced machine still asks nothing; the drop in `startMachine` is the first of two guards, and it is the one that takes the window's listeners away at once |
| MU16 the window's `pointerup` | R5 let go elsewhere | R2, R4, R5 let go elsewhere, R10, R18, G1 (15) |
| MU16 the window's `pointercancel` | R5 pointercancel | R5 pointercancel, G1 (8) |
| MU16 the slider's `lostpointercapture` | R5 lostpointercapture | R5 lostpointercapture, G1 (17) |
| MU16 the slider's `keydown` | | G1 (56) only: no R test presses a key on a held slider |
| MU17 a drawn jump not waited for | R7 | R7, R8 (released during the jump), R9 |
| MU18 at the release, the jump landed at once | R6, R8 | R6 (click), R8 (released during the jump) |
| MU19 the outcome written at every request (the text comparison and the refusal rule both removed) | R10, R11 | R10, R11 |
| MU20 the latest request's `admitted` reported | R2, R10 | R2, R10, R11 |
| MU21 the pointer id not checked (window listeners and the second-pointer guard) | R20 | R20, G1 (41) |
| MU22 the window's `pointerup` replaced by one on the slider | R5 let go elsewhere | R5 let go elsewhere, G1 (3) |
| MU23 a detached slider's events not ignored | R16 | eleven of the fourteen R16 cases: all but `reload()` and `manifestChanged()` with another machine, whose old sliders belong to a replaced machine and are held off by the `builtFor` check, and `dispose()`, which dispatches nothing |
| MU24 the window's listeners left in place | R2 | R2 |
| MU25 a press ended by the window's `blur` | R5 | R5 the window's blur, G1 (40) |

G1 stayed green under MU1, MU3, MU5a, MU8, MU10, MU11, MU12, MU17, MU18,
MU19, MU20, MU23, MU24 and the equivalent MU14 cases: its assertions are
the panel against the model, the model against the bank at rest, and each
drag's requests; they do not see whether a position was drawn or posed, a
draw count, a rebuild, the outcome line's writes, or the window's listeners.

**MU-W.** The bundle built from the implementation under MU1 (SHA256
`936d92e75098278f20874b0fcda0258fbdf6295f554cdfd5eb0d94acde3b5fa6`):
`tests/test_follow_the_slider.py` 2 failed, 3 passed, 1 skipped, the
failures B3 (`8 != 0 : the reading did not start where the input stood`)
and B5's tap (`1.499938 != 0 : the tap was not drawn from where the input
stood`); `tests/test_calculator_document.py` 1 failed, 15 passed, the
failure 6b in `GestureDrawnInABrowserTest` (`2 not greater than 2 : the
track click drew one pose, not many`). Under MU2 (SHA256
`1cc101c8913ac31f91b166d1851a6f9c5c5f0f7a6f2a086e05e5f4db509cdc4c`):
`tests/test_follow_the_slider.py` 1 failed, 4 passed, 1 skipped, the
failure B1 (`0.020805 != 0.124953606334282 within 5 places ... step 1: the
field`: drawn, the field trailed the thumb). `viewer.ts` was then restored,
confirmed byte-equal, and the bundle built again (SHA256 below).

## Gates (tasks 5.1 and 5.2)

- The whole widget suite, `vitest run` from the widget directory, once:
  **75 files, 74 passed and 1 skipped; 2044 tests, 2042 passed and 2
  skipped; no failure** (65 s). The two skips are the suite's own
  environment-gated tests: `src/run/profile-installed-benchmark.test.ts`
  (`it.skipIf(!path)`, `CURTA_INSTALLED_PROFILE_DOCUMENT` unset) and one
  test of `src/run/profile-contact.test.ts` (`it.skipIf(!actualCurtaDocument)`,
  the Curta's installed document absent). The wall-clock gates of
  `src/run/cost.test.ts` passed on this run.
- `tsc --noEmit`: no output, exit 0.
- The bundle built from the implementation with `npm run build`: SHA256
  `755ff5e3a7bee353715ca2ff7d50eaa84ba27d0be437cca4592e3f6080d66d97`
  (918.6 kB), the same after the rebuild that followed MU-W and before the
  Python suite.
- The viewer's Python suite, `pytest tests -rs` from
  `packages/machinome-viewer` on the bench's venv, once: **295 passed, 3
  skipped, no failure** (5 min 18 s). Skipped, each for a missing input and
  not passed: `tests/test_curta_drawing.py` 375 and 469 (`the Curta's own
  builds are not at .../WTs/projects/Calculators/Curta-Type-I-3x/_build`),
  and `tests/test_follow_the_slider.py` 380, B4's Firefox leg (`Playwright's
  firefox is not installed at the revision it expects (.../firefox-1543/firefox/firefox
  is absent)`). `tests/test_calculator_document.py`, 6b included, passed
  within it unmodified.
- `tests/test_follow_the_slider.py` alone on the implementation's bundle,
  with its prints: **5 passed, 1 skipped**. B1: at each of the sixteen
  steps the bank equals the thumb (0.125 ... 2) and `count` the integers
  crossed; nothing drawn and nothing changed while held still twenty frames
  and in the thirty frames after the release; the slider pressed is the
  element there and has the focus. B2: thumb and bank `(1, 1), (1, 1), (2,
  2) ... (9, 9)`, whole at every recorded frame. B3: pressed at 8, the bank
  8 from the first frame, the field `0, 0, 1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8,
  ...`, the thumb at 8 throughout, nothing after the release. B4 in
  Chromium on the implementation: the same orders as on the base, the
  viewer's slider now also reporting `lostpointercapture#1` last, since it
  is no longer replaced at the release. B5: the touch drag's bank equals the
  thumb at each of eight steps; the tap is drawn from 0 to 1.4999 over
  fourteen frames.

## The manual (task 6.1)

`/home/asa/devel/machinome/skills/write-the-manual/SKILL.md` read first. In
`packages/machinome/docs/howto/browser-viewer.rst` the clocked row of the
table now reads "Input requests, one at a time while a slider is dragged;
an optional elapsed clock", and the first paragraph of "Clocked machines"
says that dragging a slider's thumb moves the machine with it, each
position requested one request at a time with the model and the readouts
following while the thumb stays under the pointer, and that a click on the
track, a key, a typed value and a nudge each request one movement, drawn as
the next paragraph describes ("a manual gesture" there became "such a
gesture"). In `packages/machinome/docs/reference/viewer/clocked.rst`,
`MachineHandle.state()` gains "and it follows a slider of the built-in
panel while a maker drags it", and `MachineHandle.move()` gains "and a
slider a maker is dragging on the built-in panel is let go first, its last
position requested before this one". No section was added. Run alone on
the bench's venv: `packages/machinome-viewer/tests/test_documentation.py`
13 passed; `packages/machinome/tests/test_docs_structure.py` 39 passed;
`packages/machinome/tests/test_viewer_documentation_links.py` 15 passed.
The HTML build of the manual was not run (the task names these three
tests).

## The CHANGELOG (task 8.1)

One bullet appended to "Unreleased" in `packages/machinome-viewer/CHANGELOG.md`,
in the form of the bullets above it.

## Departures from the design, and decisions it left open

Departures, each forced by a fact the design states and the base does not
bear out. None changes what the delta promises; each keeps a sentence of
the delta that the design's mechanism would have broken.

1. **A refusal repeated by later positions leaves the report as it
   stands, by status and not by text.** Decision 4 has the row's line
   written "only when its text changes" and expects a repeated refusal to
   produce the same text; the machine's refusal names the request
   (`by=0.55`, `by=0.6000000000000001`), so the text changes at every
   refused position, and the delta's "the handle reports the refusal once
   however many later positions are refused" and "A stop or a refusal
   repeated by later positions SHALL leave the report as it stands" would
   fail. A followed request refused while the press's report is already a
   refusal therefore writes nothing and leaves `clockedOutcomes` as it is:
   the row keeps the first refusal's message of that run of refusals. A
   stop is still compared by text (its text does repeat). R11 holds it.
2. **"A republish that replaces the machine" is a version 14 republish.**
   For a version 8 document `manifestChanged` keeps the machine whatever
   its identity, so a press there is ended by `refreshControls` with its
   last position asked of the machine that stays, exactly as for "an
   in-place update that keeps the machine". R16 therefore has
   `manifestChanged()` with another machine on a version 14 copy of FOLLOW
   (`follow-14.json`, asserting that the republish did build a second
   machine), and `manifestChanged()` with the same machine on both
   versions. G1 adds the version 14 copy as a fourth document so that its
   republish with another identity is exercised (20 drags dropped in the
   recorded run), and marks a drag dropped only where a republish built a
   new machine.
3. **A reload ends the press in `replaceTree`, before `startMachine`.**
   The design names `refreshControls` as a reload's door, but `replaceTree`
   replaces the machine before it refreshes the controls, which would drop
   the press with nothing asked, against the delta's "a reload ... SHALL
   end the press first, its last position asked before that thing acts" and
   R16's `reload()` case. `endPress()` stands immediately before
   `startMachine(loaded)` in `replaceTree`: the press goes on while the
   document loads, and its last position is asked of the machine the maker
   dragged before that machine is replaced. `refreshControls` keeps its own
   `endPress()` for an in-place update.
4. **The slider has a fifth listener, `keydown`.** Task 3.1 lists four
   (`pointerdown`, `input`, `change`, `lostpointercapture`); Decisions 1
   and 5 need a key on the held slider to end its press and a key to clear
   the release's marker, so the key's own `change` is a request. It is on
   the slider, through a fifth action, `keySlider`; nothing is on the
   window for it.

Decisions the design left open, made here:

5. **A panel's sliders act only for the machine they were built for**
   (`builtFor` in `rebuildClockedChrome`). Between `startMachine` and the
   rebuild in `manifestChanged` lies `await startRuntime(...)`; a slider of
   the old panel, still in the page then, asks nothing (Decision 5: "its
   slider's events ask nothing until the panel is rebuilt"). This covers
   the slider's `change` too, which on the base would in that interval have
   made a request of the new machine. Outside that interval `builtFor` is
   the mounted machine and nothing differs.
6. **The drag's start is the machine's bank at the press**, the drawing's
   end where one runs (the drag's first request lands that drawing and
   travels from there), so the reported travel is what the drag's requests
   admitted. The pinned test reads the bank as the model shows it, as
   Decision 7 says.
7. **A lost capture and a cancelled pointer are releases**: each sets the
   release's marker and, while the press's own drawn jump runs, waits for
   it, as Decision 5's "the state is the one a release leaves" says.
8. **The setRoot door ends the press after `assemblyNavigation.setRoot`**,
   which refuses an unknown path by throwing; a refused `setRoot` leaves a
   press alone. Every other door ends the press at its start, after only
   the checks that refuse the call (`setClockPlaying`'s two refusals).
9. **The panel's speed select ends a press** through a wrapper on the
   clocked chrome's `setSpeed` action; the mount's `setSpeed`, which the
   handle and the timeline use, is unchanged.
10. **The thumb is placed at the end of a press through `follow`**, the
    existing row writer, so the field is written with it (unless focused),
    to the value it already reads.
11. **A drawn jump records its position as asked**, refused or not, so a
    later position equal to it is not asked twice in succession.
12. **A press ended by another slider's press leaves that first pointer
    held.** Its later `input`s ask nothing (no press) and its eventual
    `change`, if the browser sends one, is a slider's `change` outside a
    press: one drawn request, as before. Only a second simultaneous pointer
    can do this; the design does not say, and no test covers it.
13. **R17's clause "With the clock paused, the same events are R1's"** is
    its own `it`; it is red on the base for R1's reason.
14. **R16's `dispose()` case dispatches nothing after the dispose**: the
    viewer's elements are gone with it. Its different-identity case does,
    and is red on the base because the base's `change` on the replaced
    slider asks the new machine (the pending position was asked of no
    machine there, as on the implementation).
15. **G1, beyond the design's list**: the fourth document (2 above); a
    replay of a drag builds its fresh machine from the served document with
    the identity of the snapshot taken at the press, since G1's republishes
    change the identity and nothing else; an `input` dispatched with no
    press is checked to ask nothing and its value then put back, because a
    script's value standing on a thumb is today's behaviour and not the
    model's; a pinned thumb is recognised from the model at the press; a
    count of what G1 exercised is printed.

Sentences that disagree with "Corrected in review": Decision 5's
"`dispose()`: the press is dropped, nothing asked; the window and document
listeners are removed with the loop's" speaks of document listeners; this
implementation has none (no `visibilitychange` is listened to), and the
window's are removed by `dropPress()` in `dispose()`. No other sentence of
the proposal, the design, the delta or the tasks was found to stop the
clock at a press, end a press on `blur` or a hidden page, or install the
window's listeners with the loop.

## The reviewer's record (tasks 7.2, 8.2, 8.3)

Recorded by the reviewing agent on 22 November 2026, after the applying
agent stopped. Where a figure above describes the implementation as it was
handed over (44 tests, the bundle `755ff5e3…`, the speed select as a
door), this section gives what was committed.

### What the review changed, each red first

1. **A press's jump that starts no drawing left the panel stale.** Read in
   the diff: `clockedRequest`'s `pressed` path replaced the rebuild with the
   row's report, and where the gesture's tempo is zero seconds no drawing
   follows to carry the fields. A document with `Push` declared at no
   duration (FOLLOW-INSTANT) showed it: after a click on the track the
   readout of `count` read `0` with the bank at `1` (`V2`, the click: green
   on the base, red on the implementation as handed over, `the readout the
   request's commit wrote: expected '0' to be '1'`), and with the button
   held the field of `press` read `0` beside a model at `1.2` (`V2`, the
   press). `clockedRequest` now writes what such a request published
   through `follow`; `publishJudged` answers the ids it published.
2. **The clock's speed ended a press.** It makes no request, reposes
   nothing and replaces nothing, and the applying agent's own mutation
   found its call to protect nothing. Ending the press there left the
   slider in the page and the rest of the drag unfollowed (`V3`: `the drag
   was not followed after the speed changed: expected [] to deeply equal
   [['press', {to: 0.8}]]`). The wrapper is struck.
3. **Two checks that nothing could reach** were removed: the panel's
   machine checked on a position and on a key. A press never outlives its
   machine (`startMachine` drops it), so only a press's beginning and a
   `change` need the check, and `V6` holds both.
4. **The manual** said "each position the thumb reaches is requested, one
   request at a time"; a fast hand's positions are not all requested. It
   says the thumb's latest position is requested once per animation frame.

The design's last section, "Corrected in review, after the implementation",
states these and the applying agent's departures that the review accepts.

### Tests added in review

- R16 has a case for the panel's Reset button, the gap the applying agent
  reported under MU14.
- `V1` the panel's Reset during a drag; `V2` (two) a click and a held press
  on the track that start no drawing; `V3` the clock's speed during a drag;
  `V4` a drag begun while a drawing runs reports its travel from the bank
  that drawing ends at; `V5` a thumb is pinned by what the model shows, not
  by a bank a running drawing has yet to reach; `V6` between a republish
  replacing the machine and the panel being rebuilt, the old panel asks
  nothing, begins no press and holds nothing on the window; `V7` a key in
  the task of a release is a request; `V8` another pointer's movement and
  lost capture leave the press as it is; `V9` `dispose()` during a drag
  takes the press's listeners off the window and nothing is asked
  afterwards.
- G1 runs over a fifth document (FOLLOW-INSTANT), presses the panel's Reset
  as a door, changes the clock's speed while a thumb is held, and has its
  second pointer lose its capture.

The file is 55 tests. On the base source (put back for the run and the
final source restored, byte-equal by digest): **48 failed, 7 passed**. The
seven that pass assert what the base does and the change keeps: R16's
`dispose()`, R17 beside a playing clock, R18's key, typed value and nudge,
O1, `V2`'s click, `V7` and `V9`. G1 on the base: 196 of 200 sequences
failed.

### Faults planted in review

Twenty-eight, each applied alone to the committed `viewer.ts` by exact text
replacement, the file's tests run (R, V and O first; G1 where none of those
went red), and the source restored and checked by digest. The verdict was
first seen green on a replacement that changes nothing and red on a
followed position never asked (20 tests).

| Fault | Red |
|---|---|
| The panel's Reset does not end the press first | R16 (the panel's Reset), V1 |
| A press's jump that starts no drawing writes nothing in place | V2 (both) |
| The drag's travel counted from the drawn bank, not the machine's | V4 |
| Pinned read from the bank, not from what the model shows | V5 |
| A followed position does not land a running drawing | G1 (12 of 200) |
| A `change` on a panel built for a machine since replaced asks the new one | V6 |
| A press begins on a panel built for a machine since replaced | V6 |
| Every refusal of a press rewrites the report | R11 |
| The end of a press asks a position asked already | G1 (7) |
| `dispose()` leaves the press and its listeners | V9, R18 |
| A replaced machine does not drop the press | V6 |
| A reload drops the press with nothing asked | R16 (`reload()`) |
| A release during the press's own jump lands it | R6 (click), R8 |
| The end of a press does not place the thumb | R5 (the three endings), R10 |
| The thumb placed at the bank, not at what the model shows | G1 (4) |
| A key in the task of a release does not clear the release's marker | V7 |
| A second pointer on the held slider begins a press | R20 |
| Another pointer losing its capture releases the press | V8 |
| Another pointer's movement marks the press moved | V8 |
| Another pointer's release ends the press | R20 |
| Any button begins a press | R20 |
| The outcome line written whether or not its text changes | R10 |
| A followed position drawn inside its request | R4, R19 |
| The press's jump goes through the rebuilding path | R6 (both), R7, R8 (both), R9, V2, V8 |
| The press's step runs before the drawing's frame, not after it | R7 |
| The press's step runs before the drawing's frame as well as after it | nothing: equivalent, the second call finds nothing pending |
| A change of focus without its own call to end the press | nothing: equivalent to the rebuild's own, as the applying agent found |
| A position that is not a number is taken | nothing: unreachable, a range input's value is always a number |

Five of these stood on the tests as handed over (the drawn bank as the
drag's start, pinned read from the bank, a key in the release's task,
another pointer's movement, another pointer's lost capture) and three more
were held only by a test of something else or by one guard hiding another
(`dispose()`, the panel's machine on a `change` and on a press, a replaced
machine keeping its press); `V4` to `V9` were written for them.

### Gates on what is committed

- `tsc --noEmit`: no output, exit 0.
- The whole widget suite, once: **75 files, 74 passed and 1 skipped; 2055
  tests, 2053 passed and 2 skipped; no failure.** The skips are the two
  the applying agent names. G1 of this change: `0 of 200 sequences failed;
  exercised {"drags":982,"asked":836,"jumps":596,"dropped":10,"refused":65,
  "monotone":462}`.
- The bundle built from the committed source: SHA256
  `67c7794777ea6d40b888a638781ce4df1077c4141b20da14daec1cf6e8843e28`
  (918.7 kB).
- The viewer's Python suite on that bundle, once: **295 passed, 3 skipped,
  no failure** (5 min 20 s); the skips are the two Curta builds that are
  not on this machine and B4's Firefox leg.

### The Enigma I page (task 7.2)

`projects/enigma-i` at `081f4e6`, its built page served on this machine
only, opened in the suite's Chromium (Playwright 1.63, headless, 1440 by
900) with a probe build of the viewer in place of the page's bundle: this
bench's source, or the base's (`f6119628`), each with molejo's `main`
(`363847a`), unminified, with handles for measurement and no source file
edited. Every gesture was made by the browser's own pointer and keyboard on
the page's own sliders. Two runs on each build, one at a time.

**Counts and script time** (draw calls counted and not executed; script
time of the animation-frame callbacks that drew, on this virtual machine):

| Gesture | New build | Base |
|---|---|---|
| The case's thumb dragged from 1 to 0.25, twelve positions | The machine's `case_open` equals the thumb at each position (`===`); 12 requests, 12 tree updates, 12 draws, up to 78 meshes moved; 18.6 to 24.2 ms, median 20.4 | The machine stood at 1 through all twelve; nothing moved, nothing drawn |
| The thumb then held still, sixty frames | No request, no update, no draw; 0.2 ms a callback at most | The same |
| The release | Nothing asked, nothing drawn in the 1.5 s after; the slider is the element pressed and has the focus; the row reads `moved -0.750037` | One request; 7 frames moved and 8 drawn between 42 and 220 ms, 19.9 to 31.9 ms each, median 22.0; the slider replaced, the focus lost |
| The flap's thumb, 0 to 60 degrees, ten positions | Equal at each; 10 draws, 7 meshes; 16.9 to 30.5 ms, median 22.9; nothing after the release | Nothing until the release, then 9 frames moved |
| A press on the case's track, held 0.7 s, let go | One request at the press; 7 frames moved between 51 and 232 ms with the button down, the thumb at the press point throughout; nothing after the release | Nothing while held; after the release 7 frames moved between 43 and 230 ms |
| A press on the track, then dragged eight steps without letting go | At the first step the machine holds the jump's end (0.3) and the thumb 0.35; from the second step on, equal at each | The machine stood where it was until the release, then one drawn request |
| An arrow key on the slider | `keydown`, `input`, `change`; one request, drawn over 6 moving frames; the panel rebuilt, the focus lost | The same, over 8 moving frames |
| A wheel's thumb (`operation.right_wheel`, whole numbers), 0 to 6 | Equal at each of six positions, six requests of one tooth, 305 meshes moved a request; 20.4 to 39.6 ms, median 33.2; states `right` 10, `middle` 11, `left` 17 at the end | Nothing until the release; then one request of six, its drawing still running when the 1.5 s recorded after the release ended; the same states at its end |
| A key's press by its slider (`operation.press`), 0 to 1 and back, ten positions each way | Equal at each; up to 334 meshes; 28.4 to 48.0 ms, medians 34.9 and 33.0 | Nothing until each release |

The wheel's and the key's sliders are shown only with `operation` in
focus, and that node of the Enigma's tree has no part: the stage is empty
there on both builds (0 of 3,347 meshes visible, no draw call), so their
frames carry no draw of the model. Recorded in `workflow/warts.md`.

**Listeners on the window**, counted as the browser keeps them (by type,
listener and capture): at rest the same four on both builds (`pointerdown`,
`pointerup`, `mousemove`, `mouseup`, none of this change's); while a thumb
is held, one `pointermove`, one `pointerup` and one `pointercancel` more;
after each release, the four again.

**Pictures, really drawn in software.** On the new build, in nine states
(the case with the thumb held at its fourth and ninth position, and after
each of seven gestures), the page's picture equals the picture after a
forced draw: no pixel differs. For the seven states a gesture ends in, the
bank was saved and restored on the base with `machine().restore`, the page
scrolled as it stood, and both pictures taken again there: outside the
panel's rail (the canvas from its 300th column on) **0 of 6,732,908 pixels
differ** between the two builds, over the seven states on screen and
forced. Inside the rail the two differ by 1,940 to 2,420 pixels a picture:
the drag's outcome line and the focused slider, which a restored panel
does not have. The pictures are of the page's imported CAD and are not in
this repository.

**The design's predictions.** The machine equals the thumb at every step:
yes. Nothing drawn after the release, the thumb where it was let go: yes.
A click on the track is one request drawn from where the input stood,
starting at the press: yes. Whole numbers at every step on a wheel: yes.
The pictures equal the base's of the same bank: yes, outside the panel.
22 to 30 ms of script in a followed frame on the case: 18.6 to 24.2
measured. A thumb held still costs no draw: yes.

**Limits.** Script time on a virtual machine with no GPU; the draw calls
were not executed in the timed runs, and no drawing time is claimed.
Chromium only on this page. Twelve, ten and six positions a drag, two
frames apart: a hand moves faster and less evenly. The model was not
turned while a thumb was held.

### The decision record (task 8.2) and the archive (task 8.3)

The measurement confirms the design. ADR-081, its line in
`workflow/adrs/README.md` and the dated amendments to ADR-065 and ADR-064
were written by the reviewing agent, the applying agent having stopped. The
finding is closed in `workflow/warts.md`, with the empty stage under the
`operation` focus recorded beside it. Integration into `main`, pushing and
publication are the pilot's.
