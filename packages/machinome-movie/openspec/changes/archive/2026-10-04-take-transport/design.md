## Context

The player campaign's contract (`workflow/ongoing/player-campaign/plan.md`,
"The contract", "The take transport, `transport/`") is binding for this
change. It was written by the orchestrator before any cycle ran; the
parallel `live-server` change builds against it, and `player-page`
consumes both.

Today a view on a clocked take is posed inside `stage/runtime.tsx`
(ADR-012): `mountView` calls `viewMachine(viewer, take.identity, "View …
in shot …")`, which refuses a viewer that gives no machine or another
machine; `pose` calls `poseView(viewer, state, identity)`, which restores
`{identity, bank: {...state.bank}}` on `viewer.machine()` and then sets the
camera (`setView` with camera and target, and up and field of view from
Viewer API 28); the view's report reads `viewer.machine().state()`. The
pose rule, the bank at a take time, is `bankAt(doc, seconds)` in
`src/take.mjs`, pure, imported by the timeline in Node; it reads
`doc.take` (initial, steps), `doc.marks` and `doc.model.expectedDurationSeconds`
(the steps' ends, which Node reads rather than adds, ADR-016). The viewer's
handle types (`MachineHandle`, `ViewerInstance`, the factory) are declared
in `runtime.tsx`; `Vec3`, `Rect` and `Bank` in `stage/types.ts`, where
`videomaker/stage` exports `Vec3` and `Rect` to authors.

The stage bundle names every file it embeds by the tool or the project
(ADR-013, `src/stage-build.mjs`): `videomaker/stage/<file>` for the runtime,
`videomaker/node_modules/<file>` for packages, `project/<path>` for a
project's modules; any other file keeps esbuild's name relative to
`_build/stage/`, which depends on where the tool lies. The bundle's key is
the runtime's sources (every file under `stage/` but its tests), the
modules, every file the previous build read, the stage block and the
versions.

## Goals / Non-Goals

Goals: the contract's take transport, exactly; the stage posing a take
through it with nothing else changed; the transport's boundary pinned so
that the lift is a move; every frame as today, proved at layers 4, 5, 6
and 9. Non-goals: those of the proposal.

## Decisions

### D1. `transport/` is TypeScript with a pinned boundary

`transport/` holds `viewer-handle.ts`, `take.ts`, `clock.ts`, a
`tsconfig.json` (the stage's strict options without JSX) and its unit
tests beside them. Its sources import only files of the directory
(`./…`, resolving inside it) and `../src/take.mjs`: no package, nothing
from `stage/`, nothing else from `src/`. A test file of the directory
(`*.test.ts`) may also import `vitest` and the shared fixtures
(`../fixtures/…`), since the tests move with the transport; it too imports
nothing from `stage/`. The layer 9 test `test/transport-boundary.test.mjs`
reads every file under `transport/` and refuses any other static import
(`import … from`, `import '…'`, `export … from`, `import('…')`), naming the
file and the specifier, and proves its own checker refuses `react`,
`../stage/types` and `../src/movie.mjs` and admits `./viewer-handle` and
`../src/take.mjs`.

The contract states the rule for "every file under `transport/`"; read
literally it would refuse the unit tests' `vitest` import, which the
contract's own layer 4 needs beside the sources (AGENTS.md: TypeScript
unit tests sit beside their sources). The tests' wider rule is the
smallest reading that keeps both.

Rejected: the transport under `stage/` (it would be the stage's, and the
stage's bundle key and lint would claim it); plain JavaScript (the stage
and the player are TypeScript, and `tsc` is the check the pin relies on
for the handle's shape).

### D2. The viewer's handle types live in `viewer-handle.ts`

`viewer-handle.ts` declares, with no value and no import: `Vec3`, `Rect`,
`Bank`, `Vector` (what `view()` returns, `{toArray()}`), `CameraView`
(`{camera, target, up?, fov?}`), `MachineHandle` (`identity`, `state`,
`restore`), `ViewerInstance` (every method the stage calls today) and
`ViewerFactory` (`mount`). `stage/runtime.tsx` imports them from there
and declares none; `stage/types.ts` imports `Vec3`, `Rect` and `Bank` from
there and re-exports them, so `videomaker/stage` exports the same names
of the same shapes to authors and a project's type check is unchanged.
`marks.ts` keeps `MarkViewer`, the subset the marks need.

### D3. The pose rule is typed by a declaration beside it, `src/take.d.mts`

TypeScript finds the declarations of an imported `.mjs` module beside it
(`take.d.mts` for `take.mjs`), so a declaration file can only sit beside
`src/take.mjs`, not beside the transport (the contract leaves the choice
between this and `allowJs`); `allowJs` would type `bankAt` as taking and
returning `any`. `src/take.d.mts` declares every export of `src/take.mjs`
and the shapes they read: `TakeDocument`, the subset of a document a take
is read from, `{model: {expectedDurationSeconds}, marks?, take: ClockedTake}`,
which a movie document with a take and the resolved film both are; and
`ClockedTake`, `TakeStep`, `TakeCommit`, `Bank`. A layer 9 test holds the
declared function names to the module's exports, so the declaration cannot
fall behind the rule unseen. Node never reads it; esbuild resolves
`../src/take.mjs` to the module itself.

**A precision of the contract.** The contract's comment says `attachTake`
takes "the document's take block". The take block alone does not carry
the marks' take times (`marks` is top-level) nor the take's length
(`model.expectedDurationSeconds`), and `bankAt`, which the contract
requires imported and never copied, reads all three. `attachTake(viewer,
take)` therefore takes a `TakeDocument`: the same object `bankAt` takes,
which the player can pass from the resolved document. The contract's own
`seek(t)` comment, `pose(bankAt(take, t))`, already reads it so.

### D4. `attachMachine`: refuse first, then restore and one `setView`

`attachMachine(viewer, identity)` reads `viewer.machine()` once (when the
viewer has the method) and refuses, before anything is restored, set or
drawn, in this order and in the stage's words, without the `View … in
shot …` prefix, which the caller supplies:

- an identity that is not a non-empty string: `no take identity was given
  (take.identity); a machine is posed with the identity its take was
  recorded on`;
- no machine: `the viewer gives no machine for this clocked document; a
  view on a take is posed through viewer.machine(), from Viewer API 29`;
- another machine: `the viewer's machine is <own>, and the take was
  recorded on <identity> (take.identity)`.

It returns `{identity, pose(bank, view?), bank()}`, holding the handle it
checked: a mounted viewer's document does not change, so neither does its
machine. `pose` restores `{identity, bank: {...bank}}` (a fresh copy, as
the stage does) and then makes exactly one `setView`: with the view given,
`{camera, target, up, fov}` from Viewer API 28 and `{camera, target}`
below it, the stage's camera call today; without one, the viewer's own
view read back, as arrays: `view()` returns vectors (`toArray()`) and
`setView` takes arrays, so the contract's `setView(viewer.view())` is
`setView` of each vector's `toArray()`, with up and field of view from API
28. That `setView` is what draws a restored bank under on-demand rendering
(ADR-012). `bank()` is `machine.state()`. Every call returns after the
viewer has drawn; nothing is asynchronous.

### D5. `attachTake` and `attachLoop`

`attachTake(viewer, doc)` refuses a take that is not clocked (`take.kind`)
and a length that is not a positive number of seconds
(`model.expectedDurationSeconds`), naming the field, then attaches the
machine with `doc.take.identity` (D4's refusals). It returns `kind
'clocked'`; `duration`, the length as the document writes it (read, never
added: ADR-016); `marks`, `{name, time}` from `doc.marks` in take-time
order (document order for equal times); `machine`; `seek(t)`, which
refuses a `t` that is not a finite number, clamps it to `[0, duration]`
and poses `bankAt(doc, t)` through `machine.pose` with no view (the
redraw), so at a mark it poses exactly the recorded bank; `time()`, the
last clamped time sought, 0 before any. Attaching poses nothing.

`attachLoop(viewer)` returns `kind 'loop'`, `duration` 1, `marks` `[]`,
`machine` `null`, and `seek(t)`, `setTime` of `t` clamped to `[0, 1]`
(refusing a non-finite `t`). The contract states that `setTime` draws
before it returns under on-demand rendering too; layer 6 proves it on the
seesaw's export (A-B-A). Should the proof fail, the cycle stops and
reports rather than adding a redraw the contract does not state.

### D6. The clocks

`Clock` is the contract's interface. Both constructors take an optional
frame scheduler `{request(callback): handle, cancel(handle)}`, by default
`requestAnimationFrame` and `cancelAnimationFrame`, so layer 4 drives them
without a browser.

`timerClock(duration, now?, frames?)`: `now` returns milliseconds, by
default `performance.now()`. The time while playing is the time at the
last play, seek or rate change plus the elapsed milliseconds times the
rate over 1000; on reaching `duration` the clock stops there exactly.
`play()` at the end starts again from 0, as a media element's `play()`
does once ended, so both clocks behave alike under the player's keys.
`seek(t)` clamps to `[0, duration]`, keeps the clock playing or paused,
and asks for one callback on the next animation frame; two seeks within
one frame give one callback, with the later time (the latest requested
time wins). While playing, one callback per animation frame with the time
then: a slow frame is dropped, never queued; the last callback of a play
that reaches the end is at `duration`. `pause()` cancels a pending
callback unless a seek asked for it. `setRate(r)` refuses a rate that is
not positive and finite, naming it, and keeps the time continuous.
`timerClock` refuses a `duration` that is not a positive number of
seconds. `onFrame` returns the function that removes its callback.

`audioClock(audio, duration, frames?)`: the element's `currentTime`,
clamped to `[0, duration]`, is the time; `play()` sets `currentTime` to 0
when the element has ended or stands at `duration` or past it, then calls
the element's `play()`; `pause()`, `seek(t)` (setting `currentTime`) and
`setRate(r)` (setting `playbackRate`) drive the element; while the element
plays, one callback per animation frame; on reaching `duration` the clock
pauses the element and calls back with `duration`. Its parameter is typed
as the subset of `HTMLMediaElement` it uses, which an `HTMLAudioElement`
is. The element's own `play()` promise is not caught: a refusal by the
browser's autoplay policy reaches the page's console, and `playing()`
reports the element paused.

No browser test drives a clock: a verdict read from the wall clock is not
memoizable (AGENTS.md, "Memoization of slow tests"), and layer 4 proves
both clocks with an injected `now` and scheduler and a fake element.

### D7. The stage's one call

In `stage/runtime.tsx`:

- `mountView`, for a state that carries a bank, calls
  `attachMachine(viewer, config.take?.identity)` once and keeps the
  transport on the pooled instance (`PooledView.transport`); a refusal is
  the stage's mount refusal as today, `View <key> in shot <shot>: <the
  transport's words>`, with `window.filmError` set.
- `pose` calls `poseView(viewer, state, view.transport)`: a state with a
  bank is posed by `transport.pose(state.bank, {camera, target, up, fov})`,
  which restores and makes the one camera call; a loop state keeps
  `setTime` then `setView`, unchanged. A state with a bank on an instance
  without a transport is refused (the guard `poseView` has today). Within
  one film every view is on the take or none is (the time mode is the
  document's), so an instance is never leased across the two.
- The view's report reads its bank through `transport.bank()`.
- `Film.transport(key)` returns the transport of the instance the view
  element `key` holds, or `null` when it holds none (a view on a loop);
  for a key no frame has placed it refuses as `project` and `machine` do
  (`No viewer instance for view <key>`). `machine(key)` stays: the
  renderer's replay of the steps uses it.
- `viewMachine` goes; its refusals are `attachMachine`'s, word for word.

One pose per frame, as today: a restore and one `setView`. (On the API 29
bundle `restore` draws before it returns, finding 2 of the evidence, so
the frame is drawn by both, as it was before this change.)

### D8. The bundle names the transport by the tool, and keys on it

`src/stage-build.mjs`: the names gain two roots, before the project's,
`transport/` as `videomaker/transport/<file>` and `src/` as
`videomaker/src/<file>`, so `transport/take.ts`, which the runtime now
bundles, and `src/take.mjs`, which esbuild reads through it (and drops from
the script, since the stage calls only `attachMachine`: finding 1 of the
evidence), are named by the tool from any checkout, in the script and in
the record the key is computed over. The
runtime's sources for the key become every file under `stage/` and
`transport/` but their tests, each named by the tool, so a change to the
handle's types, which esbuild drops as types but a project's type check
reads through `videomaker/stage`, rebuilds the bundle. `src/take.mjs`
enters the key as every bundled file does, a file the build read. The
memo's table (`test/support/reach.mjs`) declares that `src/stage-build.mjs`
and `src/render.mjs` read `transport/` and `src/take.mjs`, and its check
for an undeclared read recognizes a `transport/` path.

### D9. Proofs, red first, innermost first

- **Layer 4** (the `stage` project under jsdom, which gains
  `transport/**/*.test.ts`; `tsc --noEmit -p transport/tsconfig.json`
  among the pure tests beside the stage's): `transport/take.test.ts` on a
  recording fake handle: each refusal of `attachMachine` by its words with
  no call made; `pose` restores a fresh copy with the identity then one
  `setView` with the view given, or with the view read back as arrays when
  none; up and field of view only from API 28; `bank()`; `attachTake` on
  `fixtures/documents/count.json`: duration 8, marks one 2, nine 6, ten 8,
  `seek` of each mark poses the recorded bank, `seek` clamps below 0 and
  past the end, mid-step poses `bankAt`, `time()`, a non-finite time and a
  take not clocked refused by name; `attachLoop` clamps through `setTime`.
  `transport/clock.test.ts`: the timer with an injected `now` and
  scheduler (advance, rate, stop at the end with a last callback at
  `duration`, one callback per frame while playing, one after a seek while
  paused, two seeks in a frame coalesced, pause cancelling, play at the end
  restarting, refusals, unsubscribe); the audio clock on a fake element.
  `stage/take.test.tsx` keeps its proofs of `poseView`, now through a
  machine transport. Red: the modules are absent.
- **Layer 5** (the double): the existing `test/browser/take.test.mjs`
  green through the transport; a new test that `window.film.transport(key)`
  reports the bank and the identity of the frame it posed, at a mark the
  recorded bank, and `null` for a view on the tour's loop (red:
  `window.film.transport` is not a function); `test/browser/transport.test.mjs`,
  the transport bundled by esbuild in the test
  (`test/support/transport-bundle.mjs`) and loaded beside the double whose
  machine answers the counter's take: `attachTake` seeks each mark and
  reads back the recorded bank, poses through restore then `setView` and
  never `setTime`, and A-B-A gives identical pixels (red: no bundle).
- **Layer 6** (the API 29 bundle): the existing parity proofs green
  through the transport; `test/viewer/transport.test.mjs`: the viewer
  mounted directly on the fixture counter's export, `attachTake` seeks every
  mark and the bank equals the record, A-B-A the same bank and identical
  pixels with the two banks distinct; `attachLoop` on the seesaw's export
  A-B-A identical and distinct.
- **Layer 9**: the import pin and the declaration's names; the memo's
  keys: every browser test's key reads `transport/take.ts` and
  `src/take.mjs` (red: the table does not declare them); the two-checkouts
  bundle test copies `transport/` and finds `videomaker/transport/take.ts`
  and `videomaker/src/take.mjs` among the bundle's names (red: esbuild's
  machine-relative name); the existing manual and changelog pins green.
- Mutations where cheap: the identity check removed from `attachMachine`
  turns layer 4 red.

### D10. ADR-020

`docs/adrs/STAGE/ADR-020-a-take-transport-is-the-browsers-pose-of-a-take-written-to-lift.md`,
Proposed: the pose of a take in a browser is a thin layer of its own,
depending on the viewer's handle and the pose rule only, which the stage
poses through and the player will; written in Videomaker now and lifted
to the viewer package at the migration by the pilot's arrangement. It
stays Proposed: the pilot has ordered the campaign to stop before sync, so
the change is not archived and its ADR not promoted in this cycle.

## Risks / Trade-offs

- The runtime changes, so every film's stage bundle changes and its shots
  recapture once (as every runtime change does).
- Two places hold the camera rule (up and field of view from API 28): the
  transport for a take, the stage for a loop. The contract keeps the loop
  path as it is; unifying it would move the loop's pose into the transport,
  which the contract does not ask.
- **The player's take document, outside this change.** The live server's
  `/film.json` carries, per take, `{kind, duration, marks}`, and
  `attachTake` needs the take document. The orchestrator ratified this
  change on 4 October 2026 with an addition to the `live-server` change:
  `GET /take.json` serves exactly the take document of D3, `{model:
  {expectedDurationSeconds}, marks, take}`, from which the player's take
  surface attaches. Nothing here builds it.
