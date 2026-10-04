## Why

The episode is the player campaign's (`workflow/ongoing/player-campaign/plan.md`,
"The episode"): the Curta's *Addition* take watched on its own before any
movie is written, and the next timing revision of *Addition* (Curta) or of
*Cut and Advance* (Leonardo) seen live. Its finding is the cost the plan
records: every timing revision of *Revolutions* meant a preview run and a
look at the contact sheet, *Addition* renders in 63 minutes, and the Curta
film's take was written blind, because nothing could show a take before
the movie rendered.

Two rulings of the pilot of 4 October 2026 place the answer: the player
lives in Videomaker before the studio takes it, and watching a scenario is
a feature by itself, of which a video is a recording. The player's two
surfaces both need to pose a take at a time in a person's browser, without
the stage for the take surface and through the stage for the movie
surface. Today that pose is a few lines inside `stage/runtime.tsx`
(`poseView`, `viewMachine`) that only the stage can call. This change, the
first of the campaign's three, lifts it into a thin layer of its own that
the stage, and later the player, pose through, written so that it can move
to the viewer package at the migration.

## What the film does with the result

Nothing on screen changes: every frame of every film, `count` and the
Curta's included, is posed exactly as today, with one render per frame,
and the renderer holds the viewer to the take as before (ADR-012). What
changes is who poses: the stage's view on a take goes through the take
transport, `window.film.transport(key)` reports it, and the `player-page`
change can then mount the viewer on an export, attach the take, and seek
it to every mark with the same rule the frame uses.

## What Changes

- **A take transport, `transport/`**, TypeScript, with no React and no
  package import, as the contract of the plan states:
  - `viewer-handle.ts`: the viewer's public handle as Videomaker reaches it
    (`Vec3`, `Rect`, `Bank`, `Vector`, `MachineHandle`, `ViewerInstance`,
    `ViewerFactory`), types only, moved out of `stage/runtime.tsx` and
    `stage/types.ts`; the stage imports them from there.
  - `take.ts`: `attachMachine(viewer, identity)` gives a machine transport
    whose `pose(bank, view?)` restores the bank on the viewer's machine
    with the take's identity and then sets the given camera (up and field
    of view from Viewer API 28) or redraws with the viewer's own, and
    whose `bank()` reads the bank the machine holds; it refuses, by name
    and before anything is restored, a viewer that gives no machine and a
    machine of another identity, in the stage's words today.
    `attachTake(viewer, takeDocument)` gives a clocked take transport
    (`duration`, `marks`, `seek(t)` clamped and posed by the pose rule
    `bankAt` of `src/take.mjs`, imported and never copied, `time()`);
    `attachLoop(viewer)` the trivial take, seeking by the viewer's
    normalized time. Every call is synchronous.
  - `clock.ts`: `timerClock(duration, now?, frames?)` and
    `audioClock(audio, duration, frames?)` (play, pause, seek, rate, and a
    per-frame callback), the frame scheduler injectable.
- **The stage poses a take through it.** In `poseViews`, a view whose
  state carries a bank is attached once per mounted viewer instance
  (`attachMachine(viewer, take.identity)`, kept on the instance) and posed
  per frame by `pose(bank, camera)`, replacing the restore, the identity
  check and the camera call the stage makes for it today. Loop views keep
  `setTime` then `setView`. `window.film.transport(key)` returns that
  view's machine transport, or `null` for a view on a loop. Nothing else
  in the stage changes: the frame carries the bank, ADR-012 and every
  proof hold.
- **The bundle names the transport by the tool.** The stage bundle embeds
  `transport/take.ts` and `src/take.mjs`; ADR-013's names extend to them
  (`videomaker/transport/<file>`, `videomaker/src/<file>`), and the
  bundle's key reads the transport's sources beside the runtime's, so the
  bundle's bytes and hash never depend on where the tool lies.
- **The boundary is pinned.** A layer 9 test reads every file under
  `transport/` and refuses a static import that is not `./…` within the
  directory or `../src/take.mjs` (a test file there may also import
  `vitest` and the shared `fixtures/`), so the lift stays a move.
- **Proofs**: layer 4 (jsdom, the `stage` project, and `tsc --noEmit` over
  `transport/`): the transports and both clocks on fakes and an injected
  scheduler. Layer 5 (the double): the existing take proofs green through
  the transport; `window.film.transport(key)` reports the bank the frame
  carried; `attachTake` over a bundled transport seeks to each mark and
  reads back the recorded bank, A-B-A exact. Layer 6 (the API 29 bundle):
  the existing parity proofs green through the transport; `attachTake` on
  the fixture counter's export at every mark equals the record, A-B-A the
  same bank and the same pixels; `attachLoop` on the seesaw's export A-B-A.
  Layer 9: the import pin; the memo's keys read the transport.
- **Records**: ADR-020 (STAGE), Proposed; `docs/stage.md`,
  `docs/movie-document.md` ("The stage"), `docs/architecture-overview.md`,
  `AGENTS.md` (layer 4), `CHANGELOG.md`.

## Capabilities

### New Capabilities

- `take-transport`: posing a take on the viewer in a browser, outside the
  stage and through it: the machine transport and its refusals, the clocked
  and the loop take transports, the clocks, and the import boundary that
  keeps it liftable.

### Modified Capabilities

- `react-stage`: a view on a take is posed through the take transport,
  attached once per mounted instance, and `window.film.transport(key)`
  reports it.

## Impact

New: `transport/viewer-handle.ts`, `transport/take.ts`, `transport/clock.ts`,
`transport/tsconfig.json`, their tests; `src/take.d.mts`, the pose rule's
types. Changed: `stage/runtime.tsx`, `stage/types.ts`, `stage/take.test.tsx`;
`src/stage-build.mjs` (names and key); `vitest.config.mjs` (layer 4 runs
`transport/**/*.test.ts`); `test/support/reach.mjs` (what the stage bundle
reads); tests at layers 4, 5, 6 and 9. The runtime changes, so every film's
stage bundle changes and recaptures once. No document, schema, fixture,
Python, renderer-check or viewer change.

## Non-goals

The live server, the player page and the `live` command (the campaign's
`live-server` and `player-page` changes). No use of the transport by the
renderer in Node, which poses only through the stage. No change to what a
frame carries, to how the renderer holds the viewer to the take, or to the
viewer. No publication, push or paid request.
