## 0. Before anything else — measured on the base, at proposal time

- [x] 0.1 The base, recorded. Worktree
      `solid-node-viewer/WTs/clocked-machine`, branch
      `draw-at-the-declared-tempo`, head `06576a3` (ADR-065's
      implementation, merged). Package `0.2.0` unreleased,
      `solidNodeViewerApi: 19`, `solidNodeDocumentVersions: [1..8]`,
      highest EXPORT ADR 065. `npx tsc --noEmit` clean; `npx vitest run`
      → **46 files, 1219 tests, 35.34 s, all green**.
      `src/clocked-corpus.json` md5 `bc4174cf47f844b035125ed3afcee3aa` —
      this cycle does not touch it, and the closing run must report the
      same md5. `dist/solid-widget.js` 804 950 B. `git status --short`
      carries only this change directory.

      **Environment note:** `solid_node_viewer/widget/node_modules` is a
      SYMLINK to the primary checkout's. NEVER run `npm ci`, `npm install`
      or `scripts/check-dist` here — through that symlink they EMPTY the
      primary's (it happened on 2026-09-15). `npx vitest run`, `npx tsc
      --noEmit` and `npm run build` are safe. One heavy process at a time
      on this host.
- [x] 0.2 The finding, recorded. The pilot, on the studio floor one day
      after ADR-065 merged: *"now the crank moves as expected. but the
      digits teleport, I expected a transition there too."* The cause, read
      off the Curta's own laws (READ-ONLY; a floor agent is live in that
      repository and nothing there is edited by this cycle):
      `projects/Calculators/Curta-Type-I-3x/simulation/cycle.py`,
      `TOOTH_PITCH = 11.25` and `tooth_passage(angle, count, end)` —
      `count` teeth advance over `count × 11.25°` of crank — used by
      `dial_positions` for both the direct and the carry train. A one-tooth
      advance is 11.25° of a 360° stroke; at `GESTURE_SECONDS = 0.2` on a
      60 Hz page a whole turn is ~12 frames of 30°, so the passage falls
      inside one frame.
- [x] 0.3 The document the finding was made on, read at proposal time:
      `_build/clocked_curta/viewer.json` — version 8, `clocked.clock:
      "time"`, 23 drivers, ONE instruction `"Turn crank": {"by":
      {"crank_rotation": 360}, "duration": 2}`; `crank_rotation` publishes
      `range: null`. The project may REPUBLISH it during this cycle with
      `clock: null` and a duration of 6 (its posed `fast_curta` already
      declares one crank turn over 6 s, `simulation/curta.py:38`). The
      measurement of §5 reads whatever the build holds when it runs and
      records it; nothing in this cycle depends on which.
- [x] 0.4 The sentences this cycle corrects, read off the base: in
      `openspec/specs/viewer-package/spec.md`, the paragraph of "A maker
      operates a clocked machine on screen" beginning "A gesture on a
      HANDLE SHALL be ONE request" ("ONE SHORT DURATION OF ITS OWN — the
      same duration for every handle and every travel … SHALL NOT be
      derived from the travel asked for"), the cross-reference in "The
      viewer plays a clocked instruction as one drawn transition" ("drawn
      over the viewer's own short duration because a handle declares
      none"), and that requirement's scenario "A handle's gesture is drawn
      like an instruction's press".
- [x] 0.5 What must NOT be rewritten: `src/clocked/drawing.ts` (byte for
      byte at the end of the cycle), `src/clocked/machine.ts`,
      `src/clocked-corpus.json` and its replay, `src/run/`,
      `src/drivers.ts`, `src/runControls.ts`, `clockFrame`
      (`viewer.ts:1280`), `landDrawing` (`:1110`), `startDrawing`
      (`:1234`), the handle wrappers, and `clockedPlay` (`:1184`), whose
      instruction keeps stating its own duration.

## 1. The tempo, red first, in node

- [x] 1.1 `src/clockedControls.test.ts`, red: the module exports a
      function answering how long a gesture on a named input is drawn,
      given the admitted travel and a document's instruction table. Record
      the failure (the base exports `GESTURE_SECONDS` and nothing else).
      The cases, from design D1–D4:
      - an instruction stating `by 360` over 2 s: a travel of 360 → 2 s,
        of 30 → 2/12 s, of 720 → 4 s, of −360 → 2 s, of 0 → 0 s;
      - an instruction stating `targets` → the fallback 0.2 s, whatever
        the travel;
      - an instruction stating `by 0` → the fallback;
      - no instruction naming that input, and an empty table → the
        fallback;
      - two `by` instructions naming one input over different durations →
        the FIRST the table declares;
      - an instruction whose duration is 0 → 0 s at every travel;
      - a non-finite or absurd travel is never answered with a non-finite
        duration.
- [x] 1.2 Implement it beside `GESTURE_SECONDS` in `clockedControls.ts`,
      which keeps its value, its comment's reason and its name, and
      becomes the fallback. Green.

## 2. The one door, on the admitted travel

- [x] 2.1 The RED for the wiring is a BROWSER one, as it was for ADR-065:
      `viewer.ts` has no node-level harness in this package. Write §4.1's
      acceptance FIRST, run it on the base, and record it failing for the
      stated reason (every gesture drawn over 0.2 s, whatever the input
      and whatever the travel).
- [x] 2.2 `clockedRequest` (`viewer.ts:1133`) takes whether this request
      is DRAWN rather than a duration, and asks §1's function for the
      seconds after the machine answers and before `startDrawing`, from
      `answered.admitted` and the loaded instruction table. The order
      ADR-064 fixed is unchanged: report, rebuild the panel once, frame 0
      in the same task, render. The bank BEFORE is still taken only where
      a drawing will be drawn.
- [x] 2.3 The clock's played frame and its `step`, and the mount handle,
      are UNDRAWN exactly as ADR-065 left them — no drawing started, the
      transport not stopped, `machine().move` landing at once. Proved by
      the same means ADR-065 used (no red is possible: mutate the
      implementation, watch each guard fail, revert, record it in
      `evidence.md`).
- [x] 2.4 `clockedPlay` still draws a pressed instruction over its OWN
      declared duration, unscaled: a press of `Stroke` is 2 s whatever
      travel it admits. Asserted, so the two paths cannot be confused.

## 3. What must not have changed

- [x] 3.1 `git diff --stat src/clocked/drawing.ts src/clocked/machine.ts
      src/clocked-corpus.json src/run/ src/drivers.ts src/runControls.ts`
      is EMPTY at the end of implementation, and the corpus md5 is still
      `bc4174cf47f844b035125ed3afcee3aa`. Recorded in the report.
- [x] 3.2 `solidNodeViewerApi` is still 19 and `solidNodeDocumentVersions`
      still `[1..8]`; `src/version.test.ts` untouched and green (design
      D6).

## 4. The committed acceptance, in a real browser

On `tests/fixtures/calculator/`'s version 8 document, which declares
`Stroke` (`by crank 360` over 2 s) and `Set four` (`targets operand 4`
over 0.5 s) beside `feed`, `ring` and `setting`, which no instruction
names — one bench carrying every case this cycle distinguishes. Sampled
per animation frame, as the existing sections do.

- [x] 4.1 `tests/test_calculator_document.py`, red first: a `+` on `crank`
      with the nudge amount armed at 360 is drawn over the DECLARED two
      seconds — the elapsed wall time and the frame count of the drawing
      both an order above the base's 0.2 s — and lands on the same bank
      one `move('crank', {by: 360})` gives from the same start.
- [x] 4.2 Same file: a nudge of 30 on `crank` is drawn over about a
      twelfth of that (asserted as a RATIO against 4.1's measurement on
      the same page, not as an absolute this harness cannot promise), and
      a typed 720 over about twice it.
- [x] 4.3 Same file: a gesture on `operand` — named only by a `targets`
      instruction — and a gesture on `feed` — named by none — are each
      drawn over the viewer's own 0.2 s, measurably shorter than 4.1's on
      the same page, with the whole-number rule still holding at every
      frame of `operand`'s.
- [x] 4.4 Same file: a gesture an interlock CLIPS on a tempo-governed input
      is drawn for the travel the machine admitted, over the declared duration
      in that proportion — the declared RATE, a shorter picture — and reports
      its stop as it does today (the fixture's own stops are already exercised
      by `test_the_machine_cranks_carries_clears_and_is_held_by_its_stops`).
- [x] 4.5 Same file: a press of `Stroke` is still drawn over 2 s
      (task 2.4), and the existing sections of this file still pass
      unchanged in meaning — the gesture that lands a running drawing, the
      field a maker is editing, the panel following.
- [x] 4.6 One screenshot kept beside the existing ones (`tests/_shots/`):
      the calculator part-way through a tempo-drawn stroke.

## 5. The Curta, where the finding came from

- [x] 5.1 `tests/test_curta_drawing.py` (skippable, a MEASUREMENT and not
      a contract), served through the directory of SYMLINKS it already
      builds, copying nothing into this repository: record the document as
      found (its instruction, duration and clock), then the pilot's own
      gesture — the `crank_rotation` nudge amount armed at 360, `+`
      pressed — with the frame count, the distinct poses, the elapsed
      seconds and the per-frame cost, beside a nudge of 30 and the
      declared instruction's own press. Report the numbers; do not assert
      a frame rate this host cannot promise (headless Chromium on
      `swiftshader` idles that page at ~2.2 fps, ADR-065).
- [x] 5.2 Answer, in those numbers, whether a TOOTH PASSAGE is now drawn
      across more than one frame where it was not: the passage is
      `11.25 / 360` of the stroke, so at the declared duration it should
      occupy that fraction of the drawing's frames. Record what the page
      actually managed, and say plainly where the host's frame rate rather
      than this cycle is the limit.
- [x] 5.3 Two pictures kept OUTSIDE this repository (a measurement is not
      a contract), beside ADR-065's, in the scratchpad's
      `viewer-acceptance/` directory: the Curta part-way through a
      tempo-drawn nudge and at its landing.

## 6. The record

- [x] 6.1 `workflow/adrs/EXPORT/ADR-073`, written after implementation from
      what was actually built and measured: a gesture is drawn at the
      tempo its input's declared instruction states; the admitted travel
      scales it; `targets` and a zero travel give no tempo; the first
      declared travel wins; no cap; the viewer's own 0.2 s is the
      fallback; no API bump. **Amends** ADR-065 (its fixed duration),
      extends ADR-064. Index row in `workflow/adrs/README.md` in chronological
      order.
- [x] 6.2 `CHANGELOG.md` under `0.2.0 — unreleased`, beside ADR-065's
      entry, saying what a maker now sees and what still keeps 0.2 s.
- [x] 6.3 `openspec validate draw-at-the-declared-tempo --strict`; sync
      the delta into `openspec/specs/viewer-package/spec.md` and archive
      the change.
- [x] 6.4 Closing suites recorded: `npx tsc --noEmit`, `npx vitest run`
      (from 46 files / 1219 tests), `pytest tests` from the worktree root
      on the workspace venv, and `npm run build` for
      `dist/solid-widget.js` (byte size before and after, from
      804 950 B). Anything that went red on the way is recorded with its
      reason, not buried.
