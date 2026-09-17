## 0. Before anything else — measured on the base, at proposal time

- [x] 0.1 The base, recorded. Worktree
      `solid-node-viewer/WTs/clocked-machine`, branch `clocked-machine`,
      head `ee9bb6c` (cycle 5's two commits over main `4a63aaa`; ADR-062
      Accepted). Package `0.2.0` unreleased, `solidNodeViewerApi: 17`,
      `solidNodeDocumentVersions: [1..8]`, highest EXPORT ADR 062.
      `npx tsc --noEmit` clean; `npx vitest run` → **44 files, 1139
      tests, 31.5 s, all green**.

      **Environment note:** `solid_node_viewer/widget/node_modules` is a
      SYMLINK to the primary checkout's. NEVER run `npm ci`,
      `npm install` or `scripts/check-dist` here — through that symlink
      they EMPTY the primary's (it happened on 2026-09-15). `npx vitest
      run`, `npx tsc --noEmit` and `npm run build` are safe.
      `dist/solid-widget.js` is gitignored and kept current by the
      package itself (ADR-059). One heavy process at a time on this host
      (virtiofs; EMFILE means wait, not a broken venv).
- [x] 0.2 The producer, recorded. solid-node branch `clocked-machine`,
      head `1a959d3`, nine commits ahead of main `81c5364`,
      UNINTEGRATED, checked out READ-ONLY at
      `solid-node/WTs/clocked-machine` — never written, and the pilot's
      primary `solid-node/` never touched. ADR-125, ADR-126, **ADR-127**
      and ADR-128 accepted 2026-09-17. `tests/clocked-corpus.json`:
      139 262 bytes, md5 `852b86b804ebd785f6e6b1f5568fb01a`,
      `"tolerance": {"float": 0.0}`, 30 machines, 76 steps, 722 numbers —
      already committed here byte for byte as `src/clocked-corpus.json`.
      **This cycle does not re-copy it.**
- [x] 0.3 The refusal this cycle lifts, read off the base:
      `src/clocked/machine.ts:281-292` — "asks this machine's clock to
      advance, which this build does not yet do". The three corpus
      machines that declare a clock and move it at their FIRST step:
      `Regulator` (5 steps), `ClockAlone` (1), `Lift` (2). The census
      pinned at `76 = 68 + 3 + 5` and `652 + 48 + 22 = 722`
      (`src/clocked/clocked-corpus.test.ts:183-247`); the departure and
      deferral branches at `:365-405`.
- [x] 0.4 What already exists and must NOT be rewritten: the clock's
      driver-shaped declaration (`machine.ts:136-140`), the relation
      selection by published `shapes` (`machine.ts:172`,
      `document.ts:562-566`), the derived bank order and the clock at
      zero (`document.ts:288-302`), the clock readout
      (`clockedControls.ts:228, 236-240`), `machine.reset()`
      (`machine.ts:370-372`), the speed ladder (`playback.ts:25-26`) and
      the render loop's wall-seconds hook (`viewer.ts:1352-1377`).

## 1. The corpus, pinned RED before a line changes

- [x] 1.1 In `src/clocked/clocked-corpus.test.ts`, turn the census into
      the closed one FIRST, derived from the file exactly as it is now:
      30 machines, 76 steps, **76 replayed, 0 departed, 0 deferred**,
      **722 of 722 numbers**. Keep both "derived from the file" tests
      (`:263-289`) unchanged. Run it: red, naming the three machines.
- [x] 1.2 Delete the departure and deferral branches of the replay
      (`:365-405`) and the `clockMoves`/`departureAt` helpers they exist
      for, so every machine goes through `replayStep`. Run it: red on
      `Regulator` 0, `ClockAlone` 0 and `Lift` 0 with the clock-request
      refusal's own message. **Record the three failures verbatim** —
      this is the cycle's red.
- [x] 1.3 Add the exactness test in the shape of the two that exist
      (`:406-448`): `Regulator`'s first recorded landing,
      `0.49999999999999994`, moved by ONE representable value must turn
      the replay red. Red now for the wrong reason; green at the end for
      the right one.

## 2. A request moves the clock

- [x] 2.1 Delete `machine.ts:281-292`. In its place, and in the
      producer's own position — after the by/to exclusivity refusal and
      after `target` is computed, BEFORE the clip — the BACKWARDS
      refusal, mirroring `clocked.py:2064-2082`: kind `ValueError`
      (`ClockedRequestError`), naming the clock, the banked instant and
      the instant the request ends at. Unit test first, in
      `machine.test.ts`: a negative `by`, a `to` behind the bank, and
      `by`+`to` together on a backwards clock getting the EXCLUSIVITY
      message rather than this one (the order is observable).
- [x] 2.2 Zero admitted, asserted rather than assumed: `by=0` and `to=`
      the banked instant each report `admitted === 0`, no commits, no
      stops, an unchanged bank, and `move(clock, {to: t})` twice equals
      once. No code is expected here — if a test is red, the fall-through
      is wrong.
- [x] 2.3 `Regulator` replays: five events on `by=5`, first landing
      `0.49999999999999994`, fractions and `count` values bit for bit,
      then `snapshot`, the `ValueError`, the zero move and `restore`.
      `ClockAlone` replays: a relation no driver can move, three events.
      Both by the corpus, with `toBe`.
- [x] 2.4 `Lift` replays BOTH steps: `move('time', by=4)` admitted WHOLE
      with four events and NO stop on a machine with two compiled
      bounds, then `move('lift', by=12)` clipped to 9.0 with the high
      stop at fraction 0.75. Assert in the same test that `clip` was
      never consulted for the clock — the promise of design §3, not an
      accident of the fixture.
- [x] 2.5 The end-of-request judgement on a TIME request, which no corpus
      machine exercises: a hand-written version 8 document in
      `machine.test.ts` — a `Regulator`-shaped machine whose counted dial
      carries a declared range the committed count drives past — refuses
      the whole request with kind `JointRangeError`, commits nothing and
      never poses. Red first.
- [x] 2.6 ADR-062's finding F7 kept: `move('time', …)` on a machine whose
      `clocked.clock` is `null` still meets the ordinary undeclared-input
      refusal (`machine.ts:151-156`), asserted by name.
- [x] 2.7 The whole corpus green: `76 = 76`, `722 = 722`, no departure,
      no deferral. If any operation genuinely cannot agree, STOP and
      report — never widen a comparison, edit the fixture or skip a
      scenario.

## 3. The loader mirrors the producer's guard

- [x] 3.1 Red first, in `document.test.ts`: a version 8 document whose
      `clocked.bounds[0].value` names the machine's clock loads today and
      must not. Likewise its `bound`, and likewise a `shapes` key naming
      the clock (`document.ts:753-757` already refuses that one — widen
      the message to name the clock and the reason).
- [x] 3.2 In `readBound`, refuse a constraint whose chain, whose bound or
      whose level names the clock, by name, with the producer's own
      reason (`clocked.py:1448-1487`): a clocked stop is compiled over
      the bank — the drivers and the states — and a clock-driven
      coordinate is not something a stop can hold. `declaredNames` is NOT
      narrowed: the clock is a legal name everywhere else.
- [x] 3.3 Assert over all 30 corpus machines that no published `bounds`
      entry names a clock anywhere, so the guard refuses nothing the
      producer writes.

## 4. The per-frame advance, as a pure decision

- [x] 4.1 `src/clocked/clock.ts` (new), pure, on `playback.ts`'s pattern:
      the seconds one frame advances the clock by, from the wall seconds
      elapsed, the speed and the frame budget — `elapsed × speed`, capped
      at four frames' worth of the current speed exactly as
      `src/run/runtime.ts:286-295` caps the run's debt. No remainder is
      carried (design §5). Tests first, in node: ×1, ×3600, a 10 s stall
      capped, a zero-length frame requesting nothing.
- [x] 4.2 Assert the cap's consequence rather than its arithmetic: a
      frame handed 10 s of wall time at ×3600 advances the clock by the
      cap and fires the cap's events, not 36 000 s worth — which would
      exceed the corpus's own `max_crossings` of 1000.

## 5. The transport on screen

- [x] 5.1 `clockedControls.ts`: the clock readout gains a TRANSPORT —
      play/pause, a step with an editable amount in seconds (no minus),
      and the speed control — present exactly when `machine.clock` is not
      `null`. Pure data, as the rest of that module is; tests in node
      first, including a machine with `clock: null` getting none.
- [x] 5.2 `viewer.ts`: render it, on `buildRunChrome`'s own action shape
      (`viewer.ts:1266-1316`) — `play()`, `step()`, `setSpeed`, and the
      `reset()` that already exists (`:1074-1081`), which now also stops
      the transport. The frame hook goes in the animation loop beside
      `runtime.frame(elapsed)` (`:1352-1377`): while playing, ONE
      `clockedRequest(clock, {by})` per frame with task 4.1's seconds.
- [x] 5.3 A refused frame PAUSES and reports, once — mirroring the run's
      rule (`viewer.ts:975-981`) — rather than repeating a refused
      request per frame. Test it with a machine whose frame exceeds
      `max_crossings`.
- [x] 5.4 `MachineHandle` becomes `ClockedMachine` plus `clockPlaying()`
      and `setClockPlaying(playing)` (`viewer.ts:166`, `:249`). NOT named
      `play`/`step`: `step()` is an existing member that refuses by name
      and must go on refusing. `setClockPlaying(true)` on a machine with
      no clock is refused by name; `clockPlaying()` is `false` there.
- [x] 5.5 The chrome switch is unchanged and asserted: a host that
      suppresses the chrome (`showsRunControls`, `viewer.ts:1059`) keeps
      the whole machine API including the two new verbs, and gets no
      transport pixels.
- [x] 5.6 `$t` and the clock coexist, asserted: for a document whose
      expressions read no `$t`, `tree.animated` is false and NO timeline
      chrome is built (`tree.ts:553-561`, `options.ts:217-224`); for one
      that reads both, the timeline advances `$t` and the transport
      advances the clock and neither moves the other's value.

## 6. A version 8 ELAPSED document with geometry, in a real page

- [x] 6.1 Export `tests/clocked_project/pendulum.py:Regulator` VERBATIM
      from a THROWAWAY COPY of solid-node at branch `clocked-machine`
      head `1a959d3` with `solid export … --no-widget` — never writing
      the read-only worktree and never touching the pilot's primary
      checkout. Commit the written `manifest.json` as
      `tests/fixtures/regulator/viewer.json` with its models; record its
      md5, byte size and `clocked.identity`; write the README on
      `tests/fixtures/calculator/README.md`'s pattern, recording the
      export's version warning and ADR-062's F2 identity difference.
      Nothing about the document is edited. A REFUSAL is a finding to
      report, not a fixture to hand-edit.
- [x] 6.2 A fixture test: every model path resolves beside the document;
      the document declares version 8, carries `states`, carries
      `clocked.clock: "time"`, carries NO `program` and NO `controls`,
      and its pose expressions read the free name `time`.
- [x] 6.3 Playwright acceptance beside `tests/test_calculator_document.py`
      (design §10): the page opens at `t = 0` with `count = 0`; play for
      one wall second at ×1 advances the readout by ≈1 s and the count by
      ≈1 (a release every `T/2 = 1 s`); pause holds both; a 2 s step
      advances the count by exactly 2; reset returns clock, count and bob
      to rest; the bob's transform DIFFERS between two instants, so the
      pose really follows the bank. Two screenshots to `tests/_shots/`.

## 7. What a played frame costs

- [x] 7.1 `src/clocked/cost.test.ts` gains the frame numbers, printed:
      one frame-sized request on `Regulator` at ×1, ×60 and ×3600 (the
      last ≈58 events in a 16 ms frame), and the per-EVENT cost, which is
      the number that scales. **No corpus machine is added** — the corpus
      is the framework's, and the speed ladder supplies the event rate.
      Say so in the test.
- [x] 7.2 Time a played second IN THE PAGE at ×1 and ×60, inside task
      6.3's Chromium, asserted under one 16 ms frame budget — the form
      that makes the main-thread decision falsifiable
      (`tests/test_calculator_document.py:390-399`).
- [x] 7.3 The whole-corpus replay time, against cycle 5's recorded
      **13.6 ms for 68 steps**; this cycle replays 76. Print it.
- [x] 7.4 State in the evidence and the ADR what is NOT being compared:
      nothing here is held against the running Curta — a clock request is
      not a tick and `Regulator` is not the Curta, which has no clock at
      all (ADR-127's own note).

## 8. Publication and the record

- [x] 8.1 `package.json`: `solidNodeViewerApi: 18`;
      `solidNodeDocumentVersions` UNCHANGED at `[1..8]`;
      `RELEASED_DOCUMENT_VERSIONS` left at `[1,2,3,4]`;
      `src/version.test.ts` updated.
- [x] 8.2 Assert UNCHANGED by diff (design §13): not one line of
      `src/run/run.ts`, `worker.ts`, `runtime.ts`, `jumps.ts` or
      `edges.ts`; `running-corpus.json` byte for byte; `capture.py`
      untouched and its tests green; versions 1–7 load, pose, animate,
      drive and run as they do.
- [x] 8.3 `npx tsc --noEmit` clean and `npx vitest run` green; the whole
      Python suite run (`PYTHONPATH=$PWD .venv/bin/python -m pytest tests
      -q -p no:cacheprovider`) and its skips reported honestly. One heavy
      process at a time.
- [x] 8.4 `npm run build` in THIS WORKTREE's widget, and the bundle's own
      report checked: API **18**, documents **[1..8]**. The PRIMARY
      checkout's bundle is NOT rebuilt here — that belongs to integration
      and is the orchestrator's.
- [x] 8.5 `README.md`'s version table now reads `0.2.0 | 18 | 1..8`, its
      "Operating a clocked machine" section gains the clock (the
      transport, what plays, what a host drives), and `CHANGELOG.md`
      carries the entry under `0.2.0 — unreleased`. Nothing is described
      as released. `workflow/warts.md` gains this cycle's dated entry.
- [x] 8.6 `docs/adrs/EXPORT/ADR-063-the-clock-is-an-input-and-a-frame-advances-it.md`,
      extracted AFTER implementation from
      what was actually built — consuming solid-node ADR-127 and
      ADR-128 §10, extending ADR-062, building on ADR-045, ADR-046,
      ADR-047 and ADR-048 — saying explicitly what it does NOT change
      (the run's worker and playback, the capture, versions 1–7) — and
      `docs/adrs/README.md` updated.
- [x] 8.7 `evidence.md` inside this change: task 1's three red failures
      verbatim, the closed census, every measurement of task 7, the page
      evidence of task 6, and every finding reported rather than silently
      resolved.
- [x] 8.8 Record as warts for the pilot: what an instruction means under a
      clocked root (ADR-128 §14, still open); a clip in time and a chain
      that follows the clock (ADR-127's own recorded narrowing, whose
      first task is ADR-126's contested direction test); and anything
      this mirror turned up that belongs to the producer rather than
      here.
- [x] 8.9 The delta is SYNCED into `openspec/specs/viewer-package/spec.md`
      (eight modified requirements carrying every surviving scenario, two
      added ones) and the change is archived as
      `openspec/changes/archive/2026-09-17-run-the-clock` with
      `evidence.md` inside. The COMMIT is deliberately not made here: two
      commits for the cycle and no more, and the implementation commit is
      the cycle's second and is the orchestrator's.
