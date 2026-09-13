## 0. Before anything else

- [ ] 0.1 Confirm `run-in-the-worker` is implemented and integrated in this
      repository, and record its head here. This change has no run to
      drive without it; do not start on a branch that lacks it.
- [ ] 0.2 Record the baseline: `npm test`, `npm run typecheck`,
      `npm run build` in `solid_node_viewer/widget`, and the Python suite
      with the workspace venv, naming what it skips.

## 1. The running chrome, decided as data

- [ ] 1.1 Red: `src/runControls.test.ts` in plain node — `runControlLayer`
      over hand-written programs and banks: `present` only for a document
      carrying a program; the focused layer's inputs and instructions by
      `scopedIds` (segment equality, never a string prefix — pin
      `x_axis_two.motor` against a focus of `x_axis`); the breadcrumb and
      navigable children reused from `controls.ts` unchanged; each input's
      `value` native, `display` and `readout` in design units through the
      declared scale with the declared unit; the nudge and jog defaults
      (amount `1`, `0.2` s, rate `1`/s) and an edited amount or rate
      appearing in the plan without changing any value; an instruction
      entry for a `by` instruction as well as a `targets` one; the
      transport plan's running flag, speed, ladder, step count, elapsed
      string and refusal.
- [ ] 1.2 Red: the elapsed formatter — `formatElapsed` gives `m:ss.ss`
      below an hour and `h:mm:ss.ss` at or above it, holds a constant
      width within each form, and never narrows once it has widened.
- [ ] 1.3 Green: `src/runControls.ts` and `formatElapsed` in
      `src/playback.ts`. Nothing in either touches the DOM.

## 2. The panel, the transport, and the interactions

- [ ] 2.1 Green: `viewer.ts` renders the running layer — one row per input
      (label, readout with its unit, nudge − / +, jog ◂ / ▸, the amount and
      rate fields), one button per instruction, and the transport bar (run
      / pause, step, speed select over the existing ladder, elapsed
      readout, reset). Every control calls the same `run()` handle a host
      would call and decides nothing of its own.
- [ ] 2.2 Green: the choice — a document carrying a program builds the
      running chrome and never `controlLayer`'s; a document with none
      builds exactly what it builds today. `tree.animated` is already
      false for a version 5 document, so no animation bar is built; assert
      that, so a future change cannot make both bars appear.
- [ ] 2.3 Green: the jog's five release paths — `pointerup`,
      `pointercancel`, `lostpointercapture`, the window's `blur`, and a
      `visibilitychange` to hidden — each cancelling the rate command. The
      button captures the pointer on press.
- [ ] 2.4 Green: a request issued while the run is paused starts it.
- [ ] 2.5 Green: outcomes — each control shows its last outcome
      (completed; blocked with the admitted travel in design units;
      refused with the run's reason; cancelled); a refused step shows the
      run's message across the panel and pauses the run, and the message
      clears on the next committed step.
- [ ] 2.6 Red then green: `src/options.test.ts` — the `run: {nudge: {amount,
      seconds}, jog: {rate}}` mount options and their defaults;
      `driverControls: 'none'` suppresses the running chrome exactly as it
      suppresses the posed one, while the run API stays whole.

## 3. A republish keeps the run only when it is the same machine

- [ ] 3.1 Red: `src/run/runtime.test.ts` (or a new `republish.test.ts`) —
      `manifestChanged` with a republished program of the SAME identity and
      step size keeps the bank, the active commands, the step count and the
      elapsed time; with a different identity, or a different step size, it
      disposes the run and starts a fresh one at the new rest bank; a
      document that gains or loses its program across a republish takes the
      second path.
- [ ] 3.2 Green: `viewer.ts`'s `manifestChanged`, and the panel line saying
      which of the two happened.

## 4. The capture

- [ ] 4.1 Red: `tests/test_capture.py` and `tests/test_cli.py` — a staged
      document carrying a program is photographed at its rest state with no
      step taken; a non-zero `--time` on one is refused by name before any
      browser starts and writes no image; a zero `--time` (the default) is
      accepted; a document with no program is unaffected in every case.
- [ ] 4.2 Green: `capture.py` and `cli.py`. Nothing here talks to the
      framework: it learns what this package supports from
      `documentVersions`.

## 5. The acceptance: a maker drives the Pascaline

- [ ] 5.1 Red: `tests/test_running_document.py` gains the on-screen half,
      on the committed fixture — mount with the chrome presented; assert
      three instruction buttons (`Add one`, `Add ten`, `Add hundred`),
      three input rows with readouts in `digit`, nudge and jog pairs, no
      slider and no timeline anywhere in the container; press `Add one`
      ten times, waiting for each button to stop indicating a run; assert
      the `units_entry` readout reads ten digits and the run's
      `tens.drum.turn` is **65.54** within `1e-9` relative — the
      framework's own number for ten `Add one`.
- [ ] 5.2 Red: the jog release — press a jog control, move the pointer off
      it until capture is lost, and assert the rate command retired and the
      machine stopped.
- [ ] 5.3 Red: a second request on a busy input — press `Add one` twice in
      immediate succession and assert the second reports the input owned,
      in place, with no page error.
- [ ] 5.4 Screenshots at rest, mid-carry and after ten instructions,
      inspected by eye and recorded here. Pixels are evidence.

## 6. The whole suite, the docs and the records

- [ ] 6.1 `npm run typecheck`, `npm test`, `npm run build`, and the Python
      suite — record counts, and that every pre-existing test passes
      unedited except the ones this change deliberately changed.
- [ ] 6.2 `README.md`: the opening list says the widget drives a running
      model with nudge, jog and instruction controls and a transport.
- [ ] 6.3 `CHANGELOG.md`: the same unreleased `0.2.0` section gains the
      controls, the republish rule and the capture's posture. Say plainly
      that constrained dragging of a part is not in it.
- [ ] 6.4 Write `docs/adrs/EXPORT/ADR-048-…` as design §7 names it, and add
      it to `docs/adrs/README.md`'s index.
- [ ] 6.5 Record design §6's open questions where the pilot will see them.
- [ ] 6.6 `openspec validate drive-the-run-on-screen --strict` passes.
