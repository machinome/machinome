## 0. Before anything else — measured on the base, at proposal time

- [x] 0.1 The base, recorded. Worktree
      `solid-node-viewer/WTs/clocked-machine`, branch `draw-every-request`,
      head `77b97e1` (ADR-064's implementation; ADR-062, ADR-063 and ADR-064
      Accepted and archived). Package `0.2.0` unreleased,
      `solidNodeViewerApi: 19`, `solidNodeDocumentVersions: [1..8]`, highest
      EXPORT ADR 064. `npx tsc --noEmit` clean; `npx vitest run` → **46 files,
      1218 tests, 34.72 s, all green**. `src/clocked-corpus.json` md5
      `bc4174cf47f844b035125ed3afcee3aa` — this cycle does not touch it, and
      the closing run must report the same md5.

      **Environment note:** `solid_node_viewer/widget/node_modules` is a
      SYMLINK to the primary checkout's. NEVER run `npm ci`, `npm install` or
      `scripts/check-dist` here — through that symlink they EMPTY the
      primary's (it happened on 2026-09-15). `npx vitest run`, `npx tsc
      --noEmit` and `npm run build` are safe. One heavy process at a time on
      this host.
- [x] 0.2 The finding, recorded. The pilot, on the studio floor serving the
      Curta's `_build/clocked_curta/viewer.json` at API 19: *"I still see
      instant change when I click to change something in the curta, no
      animation transitioning from one state to another."* The document:
      version 8, 23 drivers, 18 states, `clock: "time"`, one instruction
      `'Turn crank': by crank_rotation 360 over 2 s`; `crank_rotation` has
      `range: null` (NO slider — a number field, `-`, `+` and the amount box),
      `carriage_rotation` `[0, 100]`, `digit_1..8` `[0, 9]`. The project's own
      record, `simulation/docs/clocked-curta-2026-09-17.md:42`: *"set the
      `crank_rotation` nudge amount to `360`, and press `+` repeatedly."*
      READ-ONLY; nothing in that project is edited by this cycle.
- [x] 0.3 The sentences this cycle corrects, read off the base: the spec
      paragraph "A gesture on a HANDLE SHALL remain ONE immediate request,
      posed once…" in "A maker operates a clocked machine on screen", and
      `src/clockedControls.ts:188-190` ("A clocked request is instantaneous by
      construction … so a nudge is a travel and nothing else").
- [x] 0.4 What must NOT be rewritten: `src/clocked/drawing.ts` (byte for byte
      at the end of the cycle), `src/clocked/machine.ts`, the corpus and its
      replay, `clockFrame` (`viewer.ts:1256`), `landDrawing` (`:1105`),
      `drawFrame` (`:1087`), `drawingFrame` (`:1235`), the handle wrappers
      (`:1843-1870`), `runControls.ts` and the posed `drivers.ts`.
- [x] 0.5 The evidence that kills the "live drag" exception: the clocked
      slider listens on `change` only (`viewer.ts:3485`); the posed chrome's
      driver slider writes on `input` (`:3095`). Confirmed by reading both.

## 1. The chrome's own policy, red first

- [x] 1.1 `src/clockedControls.test.ts`, red: the module exports the gesture
      duration a drawn handle gesture takes, it is `0.2` seconds, and it does
      not depend on the nudge amount. Record the failure.
- [x] 1.2 Add the constant beside `DEFAULT_NUDGE` with its reason (design §D2,
      citing `runControls.ts`'s `DEFAULT_NUDGE.seconds`), and correct
      `DEFAULT_NUDGE`'s comment, which today says a clocked request is
      instantaneous by construction. Green.

## 2. The one door, red first

- [x] 2.1 DONE, and the red is recorded in `evidence.md` as RED 2
      (`self.assertEqual(result['crankAtOnce'], 0)` → `360 != 0`).
      The RED for this wiring is a BROWSER one, honestly: `viewer.ts` has
      no node-level harness in this package — nothing under `src/*.test.ts`
      mounts it, which is why ADR-064's own proof is the Python acceptance.
      So write §4.1's acceptance FIRST, run it on the base, and record it
      failing for the stated reason (one pose, no intermediate frames, the
      reading already at the landing on the first frame). What vitest pins in
      node is the policy of §1 and the drawing module, which already has its
      own suite.
- [x] 2.2 Route the panel's `move` and `nudge` actions
      (`viewer.ts:1321-1326`) through the one door `clockedPlay` uses,
      generalized to take a request and a duration: land, take the bank
      before, request, report, rebuild the panel ONCE, start the drawing,
      render — in exactly that order, so frame 0 corrects the readings before
      the browser paints. Green.
- [x] 2.3 `clockedDrawing` (`:421`) carries an optional indicator key instead
      of an instruction name; a handle's gesture passes none and indicates by
      following. No new chrome surface.
- [x] 2.4 DONE in `tests/test_regulator_document.py` §4b. No red is
      possible on the base — nothing draws there — so the guard is
      proved by MUTATION instead, recorded in `evidence.md`: routing the
      step through the gesture duration stops the transport, and routing
      the played frame through it stops it on its first frame.
      The CLOCK's own requests stay undrawn: `clockFrame` and the panel's
      `step()` pass a zero duration through the same door. Test, red first:
      pressing step while the transport plays leaves it playing and starts no
      drawing; a played frame starts none.
- [x] 2.5 DONE, asserted in the gesture acceptance §7 and proved by
      the third mutation (a drawn handle reads the origin, not the end).
      The host handle's `move` is unchanged and lands at once; a test
      asserts it (red first if nothing asserts it today).

## 3. What the drawing machinery must NOT have become

- [x] 3.1 `git diff --stat src/clocked/drawing.ts src/clocked/machine.ts
      src/clocked-corpus.json src/run/ src/drivers.ts src/runControls.ts` is
      EMPTY at the end of implementation; the corpus md5 is still
      `bc4174cf47f844b035125ed3afcee3aa`. Recorded in the report.
- [x] 3.2 `solidNodeViewerApi` is still 19 and `solidNodeDocumentVersions`
      still `[1..8]`; `src/version.test.ts` is untouched and green
      (design §D5).

## 4. The committed acceptance, in a real browser

- [x] 4.1 `tests/test_calculator_document.py`, red first, on the committed
      `tests/fixtures/calculator/` version 8 fixture, sampling per animation
      frame as the existing sections do: a `+` on `crank` with the nudge
      amount set to 360 gives a crank reading that is strictly increasing
      across several frames and lands on 360, with the bank equal to one
      `move('crank', {by: 360})` from the same start; the canvas shows more
      than one distinct pose over the drawing.
- [x] 4.2 Same file: a typed value committed on `crank`'s number field (typed,
      then blurred, which is what `change` means) draws the second stroke to
      720; and a value committed with the field still FOCUSED draws the model
      while that field keeps what the maker typed (the requirement's own
      clause).
- [x] 4.3 Same file: a gesture on the ranged input `operand` (`range: [0, 9]`,
      `dtype: int`) — setting the slider and firing `change`, and clicking its
      track — is drawn, the whole-number rule holding at every frame.
- [x] 4.4 Update the existing section 4 ("a gesture lands a running drawing"):
      the `+` on `feed` still lands the `Stroke` drawing, and now starts its
      own. Assert both, so the landing is not confused with the absence of a
      drawing.
- [x] 4.5 One screenshot mid-gesture kept beside ADR-064's two
      (`tests/_shots/`), showing the calculator part-way through a nudged
      stroke.

## 5. The Curta, measured where the finding came from

- [x] 5.1 `tests/test_curta_drawing.py` (skippable, a measurement and not a
      contract), served through the directory of SYMLINKS it already builds,
      copying nothing: set `crank_rotation`'s nudge amount to 360, press `+`,
      and record the frame count, the distinct poses drawn and the per-frame
      cost over the 0.2 s, beside the same numbers for the declared
      instruction's 2 s. Then type 720 into the field and record the same.
- [x] 5.2 ANSWERED, and the answer is a limit of this host and not of
      this cycle: the Curta's page idles at 2.2 fps, so a 0.2 s gesture
      draws its origin and its landing and nothing between, while the
      same page draws four poses of the 2 s instruction and the
      calculator draws 60 frames at 60.1 fps. See `evidence.md` and
      ADR-065's Consequences.
      Record what the numbers say about the pilot's own question — whether
      a 0.2 s stroke on that page is watchable — and report it rather than
      asserting a frame rate this harness cannot promise (the 3 fps idle
      finding in `workflow/warts.md`).

## 6. The record

- [x] 6.1 `docs/adrs/EXPORT/ADR-065`, written after implementation from what
      was actually built and measured: every request the clocked panel makes
      is drawn; the fifth of a second and why; the live drag that does not
      exist; the clock and the handle left alone; no API bump. **Amends**
      ADR-064. Index row in `docs/adrs/README.md` in chronological order.
- [x] 6.2 `CHANGELOG.md` under `0.2.0 — unreleased`.
- [x] 6.3 `openspec validate draw-every-request --strict`; sync the delta into
      `openspec/specs/viewer-package/spec.md` and archive the change.
- [x] 6.4 Closing suites recorded: `npx tsc --noEmit`, `npx vitest run` (from
      46 files / 1218 tests), `pytest tests` from the worktree root with the
      workspace venv, and `npm run build` for `dist/solid-widget.js` (byte
      size before and after). Anything that went red on the way is recorded
      with its reason, not buried.
