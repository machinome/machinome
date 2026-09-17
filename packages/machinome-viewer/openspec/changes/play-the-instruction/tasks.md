## 0. Before anything else — measured on the base, at proposal time

- [x] 0.1 The base, recorded. Worktree
      `solid-node-viewer/WTs/clocked-machine`, branch
      `play-the-instruction`, head `757ad84` (cycle 6's two commits over
      `4a63aaa`; ADR-062 and ADR-063 Accepted and archived). Package
      `0.2.0` unreleased, `solidNodeViewerApi: 18`,
      `solidNodeDocumentVersions: [1..8]`, highest EXPORT ADR 063.
      `npx tsc --noEmit` clean; `npx vitest run` → **45 files, 1168
      tests, 31.88 s, all green**.

      **Environment note:** `solid_node_viewer/widget/node_modules` is a
      SYMLINK to the primary checkout's. NEVER run `npm ci`,
      `npm install` or `scripts/check-dist` here — through that symlink
      they EMPTY the primary's (it happened on 2026-09-15). `npx vitest
      run`, `npx tsc --noEmit` and `npm run build` are safe. One heavy
      process at a time on this host (virtiofs; EMFILE means wait, not a
      broken venv).
- [x] 0.2 The producer, recorded. solid-node branch
      `play-the-instruction`, head `2ab9505` (ADR-129's implementation
      over the proposal commit `0186ed3`), one commit's worth of
      behaviour over `1a959d3`, UNINTEGRATED, checked out READ-ONLY at
      `solid-node/WTs/play-the-instruction` — never written, and the
      pilot's primary `solid-node/` never touched.
      `tests/clocked-corpus.json`: **145 673 bytes**, md5
      `bc4174cf47f844b035125ed3afcee3aa`, `"tolerance": {"float": 0.0}`,
      30 machines, **81 steps**, **917 recorded numbers**, 13 machines
      with bounds over 41 steps. Two `trigger` steps, both on
      `Calculator`: step 12 `Set four`, step 14 `Stroke`, with step 16
      the same request by hand from the bank of snapshot `d`.
- [x] 0.3 The refusals this cycle lifts, read off the base:
      `src/clocked/machine.ts:402-408` (`trigger` by name) and
      `src/clockedControls.ts:206-208` + `:99-109`
      (`INSTRUCTIONS_DISABLED`, `disabled: true`). The corpus census this
      cycle moves: `src/clocked/clocked-corpus.test.ts:172-173` (bytes,
      md5), `:212-243` (76 steps, 722 numbers, 13/36), and
      `replayStep`'s `else { unknown script step }` at `:344`.
- [x] 0.4 The Curta, recorded, READ-ONLY:
      `_build/clocked_curta/viewer.json` — version 8, 952 464 bytes, 23
      drivers, 18 states, 39 commits, 35 bounds, `clock: "time"`,
      `'Turn crank': {"by": {"crank_rotation": 360}, "duration": 2}`;
      `_build/fast_curta/viewer.json` — version 4, 846 163 bytes, 8
      drivers, 7 instructions, `'Turn crank': targets crank_turns 1 over
      6 s`. 54 MB of meshes beside each, which is why the measurement
      serves SYMLINKS and copies nothing.
- [x] 0.5 What already exists and must NOT be rewritten: the request and
      its clip (`machine.ts:281-378`), the one `native()` conversion
      (`:113-117`), the pose hook and its atomicity
      (`viewer.ts:1039-1056`), the outcome report and its formatting
      (`clockedControls.ts:56-58, 361-378`), the running chrome's
      busy/report seam (`viewer.ts:3549-3580`), the render loop's wall
      seconds (`viewer.ts:1477-1510`), `posed()` and `clockedScope`
      (`run/pose.ts`), and the corpus's derived census
      (`clocked-corpus.test.ts:206-270`).

## 1. The corpus, pinned RED before a line of engine changes

- [ ] 1.1 In `src/clocked/clocked-corpus.test.ts`, move the census to the
      numbers the NEW file will carry — 30 machines, **81** steps, **917**
      numbers, 13 bounded machines over **41** steps — and the byte count
      and md5 to `145 673` / `bc4174cf47f844b035125ed3afcee3aa`. Keep both
      "derived from the file" tests unchanged. Run it: **red**, naming the
      old file. Record the failures verbatim.
- [ ] 1.2 Copy the producer's `tests/clocked-corpus.json` over
      `src/clocked-corpus.json`, byte for byte, from
      `solid-node/WTs/play-the-instruction` at `2ab9505`. Verify the md5
      after copying. Run it: census green, replay **red** on `Calculator`
      steps 12 and 14 with "unknown script step". Record it: this is the
      cycle's corpus red.
- [ ] 1.3 Add to `replayStep` the comparison of BOTH ENDS on every step,
      and to the machine-level assertions nothing else. Run it: red on
      every machine with `result.origin` undefined.

## 2. The request reports both ends

- [ ] 2.1 `src/clocked/machine.test.ts`: a `by` request from a non-zero
      start reports `origin` and `end` equal to the bank before and
      after; a CLIPPED request reports the stop's landing as `end`; a
      zero-travel request reports them equal; a `to` request over an
      integer driver reports the converted native value. Red first.
- [ ] 2.2 `ClockedRequest` gains `origin` and `end`, returned from the
      two values `move` already holds (`:292`, `:364`), with the units
      stated in the interface's own doc comment as the producer states
      them. Green, including 1.3.

## 3. `trigger` executes

- [ ] 3.1 `machine.test.ts`, red: `trigger('Stroke')` over the corpus's
      `Calculator` equals `move('crank', {by: 360})` from the same bank,
      field for field, and leaves the same bank; `trigger('Set four')`
      equals `move('operand', {to: 4})`; an unknown name is refused
      listing the declared names and the bank stands; `rate` and `step`
      still refuse with their own messages.
- [ ] 3.2 Implement `trigger` on `clockedMachine`: resolve the
      instruction from `machine.instructions`, take its one entry, and
      delegate to `move`. No conversion, no rounding, no second copy of
      the driver resolution. Green, and the corpus replay's `trigger`
      branch (3.3) turns green with it.
- [ ] 3.3 The corpus replay's `trigger` verb, in `replayStep`, recorded
      exactly as a `move` step is; plus the test that `Calculator` steps
      14 and 16 are equal field for field and both reproduced. Green;
      the whole corpus replays.

## 4. An unplayable instruction is refused at load

- [ ] 4.1 `src/clocked/document.test.ts`, red: a version 8 document
      whose instruction states both forms or neither, names no driver or
      two, names a state, names the clock, names an id nothing declares,
      or declares a duration that is negative, infinite, NaN or not a
      number — each refused at load, by name, naming the instruction.
- [ ] 4.2 Implement it in `readInstructions`, in the refusal shape the
      rest of the loader uses. Green. Assert the corpus's own 30
      documents and every committed fixture still load.

## 5. The drawing, decided in node

- [ ] 5.1 `src/clocked/drawing.test.ts`, red, over hand-written requests
      (the corpus's own recorded `Stroke` among them): the value at 0, at
      each commit's fraction, just before each, and at 1; the bank at
      each; the last frame equal to the request's `end` and to the
      machine's bank value for value; a DOWNWARD request drawn by the
      same rule; a whole-number input whole at every frame and never past
      `end`, rising and falling; `duration: 0` landing in one frame; a
      zero-travel request drawing nothing; a zero-span request's
      `fraction: 1` commits landing at the end; `land()` from any point
      giving the same frame as the last one.
- [ ] 5.2 Write `src/clocked/drawing.ts` — the request, the start bank,
      the duration, the whole-number flag, `advance`, `land`, and the
      `moved` ids per frame. It takes NO machine, which is the
      structural half of "one solve per press". Green.

## 6. The page plays it

- [ ] 6.1 `viewer.ts`: hold at most one drawing; `clockedTrigger(name)`
      issues the request through the same `clockedRequest` reporting path
      (keyed by the instruction NAME), poses frame 0 in the same task,
      and starts the drawing. Advance it in the render loop beside
      `clockFrame`, posing through `tree.update(clockedScope(...),
      posed(moved))` and nothing else.
- [ ] 6.2 Landing: every other path — `clockedRequest`, the handle's
      `move`/`restore`/`reset` wrappers, `clockFrame`, another trigger —
      lands the drawing first. Starting a drawing pauses the clock's
      transport.
- [ ] 6.3 The chrome: `ClockedInstructionControl` carries an outcome
      instead of `disabled`/`reason`; the button is pressable, indicates
      while its drawing runs and reports where it was pressed;
      `ClockedChrome.follow` rewrites the moved input's field and slider
      and the readouts the drawing has committed. Update
      `src/clockedControls.test.ts` red-first for the layer's half.
- [ ] 6.4 The posed `ViewerHandle.trigger` refuses by name under a
      clocked document, pointing at `machine().trigger`.
- [ ] 6.5 `npx tsc --noEmit` and `npx vitest run`: green, with the base's
      1168 tests still green and the new ones beside them.

## 7. The acceptance, in a real browser

- [ ] 7.1 Re-export `tests/fixtures/calculator/` from a THROWAWAY COPY of
      the producer at `2ab9505` (`PYTHONPATH="$PWD" solid export
      tests/clocked_project/calculator.py:Calculator -o <dir>
      --no-widget`), copy the document in as `viewer.json` verbatim, and
      update its README with the new size, md5, commit and the two
      instructions. Nothing is written into the read-only worktree.
      Assert in `tests/test_calculator_document.py` that the document now
      carries exactly `Stroke` and `Set four`.
- [ ] 7.2 The drawing acceptance (design §20, items 20-25): the per-frame
      samples, the landing, two presses, a gesture landing a drawing, the
      screenshots, and the posed trigger's refusal. Red first against the
      un-wired page where it can be.
- [ ] 7.3 `tests/test_curta_drawing.py` (new, skipped where the build is
      absent): the symlink harness, `'Turn crank'` on the clocked build
      and on `fast_curta`, frame times recorded, one assertion — more
      than one distinct pose.
- [ ] 7.4 `pytest tests -q` from the worktree root: green, with every
      skip printing its reason.

## 8. Measure, and say it in numbers

- [ ] 8.1 The Curta's drawing: frames per second, median and worst frame,
      against `fast_curta`'s posed ramp, same session. Recorded in
      `evidence.md` whatever it says.
- [ ] 8.2 `trigger` against the same `move` on the corpus `Calculator`,
      median of 20, in thread.
- [ ] 8.3 The bundle's size before and after, and the widget suite's wall
      time before and after.

## 9. The record

- [ ] 9.1 `npm run build` in THIS worktree's widget, so
      `dist/solid-widget.js` reports API 19 and the Playwright tests run
      against what this cycle built. The primary checkout's bundle is the
      orchestrator's after integration; nothing here touches it.
- [ ] 9.2 `package.json`: `solidNodeViewerApi: 19`,
      `solidNodeDocumentVersions` unchanged; `src/version.test.ts` and
      `tests/test_version.py` green.
- [ ] 9.3 `docs/adrs/EXPORT/ADR-064`, extracted after implementation
      (design §16), with the `**Amends:**` header naming ADR-062; the
      index line in `docs/adrs/README.md` reading "amends 062, extends
      063, consumes solid-node ADR-129".
- [ ] 9.4 `CHANGELOG.md` under `0.2.0 — unreleased`, and `README.md`'s
      version table.
- [ ] 9.5 `evidence.md`: the red log for every task, the measurements,
      the corpus diff, and anything reported rather than silently
      resolved.
- [ ] 9.6 `openspec validate play-the-instruction --strict`, then sync
      the deltas into `openspec/specs/viewer-package/spec.md` and archive
      the change.
