## 1. Playback rules (red first, pure)

- [ ] 1.1 Red: `playback.test.ts` — `cycleSecondsFor({fps, frames}, speed)`
      is `frames / fps` without `loop` and `loop / speed` with it;
      `ladderFor(1)` is the fixed ladder; `ladderFor(720)` inserts 720 in
      order; `formatMachineTime` gives `6:00:00` for 21600 of a 43200 loop,
      `1:30.0` for 90 of a 120 loop, `0.75 s` for 0.75 of a 1.5 loop;
      `assertSpeed(0)`, `(-5)`, `(NaN)`, `(Infinity)` throw naming the value.
- [ ] 1.2 Implement `solid_node_viewer/widget/src/playback.ts`. Green.

## 2. Types, options and handle

- [ ] 2.1 Red: `options.test.ts` — `resolveOptions({speed: 60}).speed === 60`,
      default 1, a bad speed throws; `types.ts` accepts `animation.loop`
      (typecheck).
- [ ] 2.2 Red: `document.test.ts` or a new `viewer.test.ts` case — a mounted
      document with `loop` advances `time` by `elapsed * speed / loop` per
      frame; without `loop` by `elapsed * fps / frames`; `setSpeed` changes
      the rate mid-play; speed survives `update()` with a republished
      document; `speed()` reports 1 and `setSpeed` is accepted for a
      loop-less document.
- [ ] 2.3 Implement: `speed` in `ResolvedViewerOptions` and `viewer.ts`
      state, `cycleSeconds` from `playback.ts`, handle `speed()` /
      `setSpeed()`. Green.

## 3. The bar

- [ ] 3.1 Red: a document with `loop` builds a bar with a `select`
      labelled "Playback speed" whose options are the ladder and a readout
      span reading `0:00:00`; selecting ×720 calls through to the same
      `setSpeed`; scrubbing to 0.5 updates the readout to `6:00:00`; a
      document without `loop` builds exactly the bar it built before.
- [ ] 3.2 Implement in `buildControls` / `refreshControls`. Green.

## 4. Package and records

- [ ] 4.1 Raise `solidNodeViewerApi` to 6 in `widget/package.json`; adjust
      any test pinning the number.
- [ ] 4.2 `npm test`, `tsc`, `npm run build`; run the Python suite (the
      capture and server tests must be unaffected).
- [ ] 4.3 `README.md` (the widget's options and handle) and `CHANGELOG.md`
      (0.1.0 unreleased) describe real-time playback, the speed control and
      the readout; sync and archive the change.
- [ ] 4.4 Caller check: rebuild the bundle, open the migrated
      `wall_clock_01` in `solid develop` from the framework worktree, and
      confirm the pendulum beats at 1.5 s at ×1 and a turn of the hour hand
      takes a minute at ×720. Record the evidence here.
