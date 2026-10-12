# The player: a take transport and a movie transport over the render's stage

Status: working note, drafted 4 October 2026 at the pilot's request and
revised the same day after two rulings of the pilot. Nothing here is
ratified, no OpenSpec change has been cut from it, and no schedule is
implied. Every name is provisional. Where this note and a baseline spec
disagree, the spec is right.

## What it does not claim

- That the studio has agreed to host the piece, or to any seam named here.
- That any command, directory, route or page named here exists. None does.
- That the viewer, the framework or the studio have agreed to the later
  moves named under "The lift". They are the pilot's arrangement at the
  migration, not a request to those repositories now.

## Where it comes from

`roadmap.md` item 13, *Live preview*: a browser page with a timeline
scrubber that reloads when the source changes. `declarative-python-api.md`
made it the fifth step of its path and placed it in the studio, on the
pilot's word.

Two rulings of 4 October 2026 shape this note:

1. Before it reaches the studio, the piece exists in Videomaker, for the
   studio to use.
2. Watching a scenario is a feature by itself, and a video is a recording
   of that watching. The player is both a scenario player and a movie
   player. Posing a take at a time is a rule the viewer's widget already
   applies when it draws a solved request, and the natural home of a take
   transport is the view layer; but the pilot wants the viewer to stay
   thin, so the thin layer is built here, in Videomaker, where the risk of
   coupling is lower, and is arranged into its final place when Videomaker
   migrates into the monorepo (one repository, one licence, packages such
   as `machinome[video]`). The direction note already records that a take
   belongs to the simulation and that the movie only reads it.

The cost it answers is recorded: every timing revision of *Revolutions*
meant a preview run and a look at the contact sheet, and *Addition* renders
in 63 minutes. The person editing a film cannot see it move, and the Curta
film's take was written blind: nothing could show a take before the movie
rendered.

## The rule

**Two transports, nested, over the render's stage.**

- The **take transport** moves a machine through a take: time in, pose
  out, marks as stops. It knows the viewer's public handle and the take
  document, and nothing of the stage or the movie.
- The **movie transport** moves a movie through video time: it takes the
  frame from the same frame function the renderer uses, feeds each view's
  take time to that view's take transport, and keeps the narration as its
  clock.

The video is a recording of the movie transport's output. Neither
transport draws: the stage draws the frame the renderer would capture,
through the same bundle, the same frame function and the same viewer, and
the transports add a clock, a ruler and a reload. Where the page cannot
show what the renderer composes, it says so rather than drawing something
else.

Three consequences:

1. The stage bundle is the render's, byte for byte, and the stage runtime
   changes in one call (below).
2. A movie frame comes from `frameAt(film, t)` in the Node process that
   loaded the film. The browser computes no movie frame; it computes a
   take pose, by the pure rule both sides share.
3. A document the loader refuses is not shown. The player prints the
   refusal and keeps the last accepted film posed.

## Where it sits in the pipeline

    source  →  resolved movie document  →  frameAt(film, t)
                                                 │
                 ┌───────────────────────────────┴───────────────────────┐
                 ▼                                                       ▼
      stage.setFrame in headless Chromium                stage.setFrame in the person's browser
      captures, proofs, shot cache, FFmpeg                the movie transport (live)
      (check, preview, render)
                                                         viewer + take transport, no stage
                                                         the take surface (live)

Everything above the frame is shared: both loaders, `check`'s refusals,
the layout measurement, the stage bundle, the viewer requirement. Nothing
below the renderer's capture is touched. The live session opens no
Chromium to draw; the person's browser is the browser. Chromium is still
opened at load, by the code `check` uses, to measure a layout when the
document shows a picture or comes in by a reframe (ADR-009, ADR-010).

## The layers, bottom up

1. **The take**, as today. Declared in the project's Python through
   `machinome_movie` (`Take`, `Move`, `Trigger`, `Mark`), recorded through
   the framework's `Sim` into the document's take block (ADR-011). The
   pose rule stays in `src/take.mjs`, which is pure and imports nothing,
   so one implementation serves Node for the frame and the browser for
   the transport. This is the part that later moves to the core.
2. **The take transport**, new, in its own directory `transport/`.
   `attachTake(viewer, take)` returns `{kind, duration, marks, seek(t),
   pose(bank), bank(), time()}`. A clocked take seeks by restoring the
   bank the pose rule gives for `t`, with the take's identity, then a
   redraw (`setView(viewer.view())`, the API 29 rule); a posed loop is
   the trivial take and seeks by the viewer's own normalized time. Beside
   it `clock.ts`: play, pause, rate, seek and a per-frame callback, driven
   by an audio element or by a timer. No UI, no React. This is the part
   that later moves to the viewer package.
3. **The stage**, one change: where a view on a take restores its frame's
   bank today (`runtime.tsx`, `poseViews`), it calls the transport's
   `pose(bank)`. The frame keeps carrying the bank and the renderer keeps
   holding it to the record at every frame and mark, so ADR-012 and the
   proofs are untouched. `window.film` gains `transport(key)` for the
   player's readout; nothing else.
4. **The player page**, `player/`, TypeScript bundled at start by the
   esbuild the stage build uses, into `_build/player/`, cached by content,
   with no project module. Two surfaces over one server:
   - **Take.** The viewer mounted directly on the export (`/viewer.js`,
     `/model/manifest.json`, the assets the renderer serves), the
     transport attached to a take the document carries, a timer clock, a
     ruler with the take's marks, free camera through the viewer's own
     navigator. Nothing of the stage is loaded. This is watching a
     scenario by itself.
   - **Movie.** The stage page `/film.html` in an iframe of exactly the
     output geometry at `--width`, scaled by CSS to fit; frames fetched
     from `/frame?t=`; the narration audio as the clock when a mix exists,
     the timer otherwise; a ruler with chapters as bands, shots as
     segments, joins hatched, cues as ticks, take marks as flags. The page
     drives `iframe.contentWindow.film.setFrame(frame)`, the renderer's
     own entry, after waiting for `film` or `filmError` as the renderer
     does.
   - **Shared.** The ruler, the keys (space; one frame left and right;
     one second with shift; home and end; a click on a shot or a mark),
     the readout (time, frame, shot, chapter, mark), the refusal display,
     the reload. One pose in flight at a time; the latest requested time
     wins; a frame the stage cannot reach in time is dropped and the audio
     never waits.
5. **The server**, `src/live.mjs`. A **generation** is one accepted load:
   the film (`loadEpisode` or `loadMovie`), the stage bundle
   (`buildFilmStage`, reused while its inputs are unchanged), the measured
   layout and reframe boxes when the document needs them, the stage
   config and the asset paths, with a number, the time it loaded and the
   check lines it printed. A failed load is a refusal; the previous
   generation stays served. The server is `assetServer()` of `render.mjs`
   with one handler for the session's life; the handler that serves a
   film's stage page and assets, today a closure in `browserSession`,
   moves to `src/film-assets.mjs` so the renderer and the live session
   serve the same files the same way. Routes beside the renderer's:
   - `/` the player, `/player.js`, `/player.css`.
   - `/film.json` the outline: id, title, output; chapters with start and
     end; shots with chapter, start, end, set and incoming join; cues with
     their instants; the takes the document carries with their marks in
     take time and in video time; whether a mix exists; the stage hash;
     the viewer API required; the generation's number and time; the
     current refusal or null.
   - `/frame?t=` the frame at `t` snapped to the grid (`round(t·fps)/fps`,
     the renderer's rule), as JSON: `frameAt` and nothing else.
   - `/narration.wav` and `/captions.json` when `speech` has written them.
   - `/events`: `loading`, `generation` (number, stage hash, whether the
     export changed), `refused` (the message).
   - The watcher settles changes into one reload: the document, the stage
     modules, the excerpt sources, the stills and clips, the export
     manifest, the audio cache and mix. `_build/stage/`, `_build/player/`
     and `_build/preview/` are the tool's own and are not watched.
     `fs.watch` recursive on Linux, with `--poll <ms>` for a filesystem
     whose events do not arrive (virtiofs sees the guest's writes and not
     the host's). Reload replaces the generation atomically; the page
     keeps its iframe and mounted viewers when the stage hash and the
     export are unchanged and poses the current time again, otherwise
     reloads the iframe.
6. **The command**, in `bin/videomaker.mjs`:

       videomaker live EPISODE.yaml|MOVIE.json [--viewer BUNDLE.js] [--width 960] [--port 0] [--open] [--poll MS]

   It loads as `check` does and prints the check lines, starts the
   server, prints one address line, and runs until interrupted. `--viewer`
   defaults as the other commands' does. `live` buys no speech: a movie
   with spoken anchors loads only with its cached takes, as `check` does,
   and a film without a mix plays on the timer.
7. **Recording**, unchanged: `render` is the movie transport's output
   captured and encoded.

## The tree

    src/take.mjs            pose rule, pure, shared            exists
    transport/              take transport + clock             new; lifts to the viewer later
    stage/runtime.tsx       pose(bank) through the transport   one call changed
    player/                 take surface, movie surface, ruler, keys, reload
    src/live.mjs            generation, routes, watcher, events
    src/film-assets.mjs     the asset handler, shared with render.mjs
    bin/videomaker.mjs      the command

## The coupling boundary and the lift

`transport/` imports the viewer's handle types (`stage/runtime.tsx`'s
`ViewerInstance` shape moved beside it as a declaration file) and
`src/take.mjs`, and nothing else in the repository. The stage and the
player depend on it; it depends on neither. A layer 9 repository pin reads
the directory's imports and refuses any other, so the boundary cannot
erode unnoticed.

At the migration, by the pilot's arrangement and not by this note:

- the take declarations and the take document move to the core's
  simulation layer, split into the declared scenario and its recorded
  take;
- `transport/` and the pose rule move to the viewer package, at whichever
  level the pilot sets (the widget, or a view component over it), with
  their parity tests;
- the take surface of the player moves with them, wherever the view layer
  lands;
- the movie transport, the stage, the frame route, the server and the
  renderer stay in the video package.

Until then every one of those lives here, and the pin above is what keeps
the move a move.

## What the first cut does not draw live

- **Composed joins.** A dissolve, fade, wipe or slide is blended by the
  renderer from captures of two frames, and a page cannot capture itself.
  Live, the outgoing frame is posed until the join's midpoint and the
  incoming one after it; the ruler hatches the span and the readout names
  the join and says it is shown as a cut. A reframe is drawn live already
  (ADR-010) and shows exactly. An open line, not proposed: a fade drawn
  live in the transition layer as a black overlay, a stage change.
- **Fading marks and pictures.** The renderer blends captures to keep
  subpixel text; live, the stage's own opacity is shown. The same to the
  eye, not the same pixels, and not a proof.
- **The take surface** shows the machine and nothing drawn over it: no
  marks, no highlights, no layers hidden. Those are the movie's.
- **Captions** are not drawn in the frame; the transport shows the current
  caption's text under it as a readout when `captions.json` exists.

## Costs

Per frame, one local request and one pose. The renderer's headless
numbers, software rendering, are the ceiling to expect without a GPU:

| model | one pose |
|---|---|
| sawmill | 0.43 s |
| Curta | 1.0 s |

On a desktop browser with a GPU the cost is unmeasured and is the first
thing the episode records. A tab with the Curta mounted is about 900 MB.

## What the studio takes from it

A process with an HTTP surface, the pattern the viewer already follows with
`machinome-viewer serve`. The studio spawns `videomaker live <document>
--viewer <bundle> --port <n>` in the session's environment, embeds `/` in a
Film panel beside Model, Code, Agents and Build, shows the state `/events`
and `/film.json` carry, and re-evaluates the movie through its own venv
when the project's Python changes; the live process sees `_build/movie.json`
change and reloads. Nothing in the piece knows the studio. What the piece
guarantees for that: a stable command line, one printed address line, a
page that may be framed, and the event stream.

## Who re-evaluates

For a YAML episode the document is the source. For a Python movie the
document is `_build/movie.json`, written by `python -m machinome_movie
evaluate`. The preference, not yet the pilot's word: a `watch` subcommand
on the Python side that re-evaluates its own project when its files
change, one process per side, so the Node tool never selects a Python
interpreter. The alternatives, the author re-evaluating on save or the
live process running Python itself, reach the same page.

## Tests by layer

- **Layer 3.** `/frame` returns `frameAt` for the snapped time.
- **Layer 5**, the browser and the double: the transport seeks a clocked
  fixture take to the bank the pose rule gives and reads it back; a loop
  take seeks by time; the clock advances by its driver and drops frames;
  the movie surface poses the frame `frameAt` gives, with the iframe's
  measurements equal to the renderer's; A-B-A exact; a reload with an
  unchanged bundle keeps the mounted viewer and poses the current time
  again; a changed stage module reloads the iframe; a refused document
  shows its message and keeps the last frame.
- **Layer 6**, the real bundle: the transport's restore equals the record
  at every mark and its replay of each step equals the recorded request,
  the tests the Curta campaign wrote, moved to the transport.
- **Layer 8**, the pipeline: `live` end to end on the fixture movie: it
  starts and prints its address, both surfaces answer, `/film.json` and
  `/frame` answer, touching the document emits `generation`, a broken
  document emits `refused`, an interrupt stops it cleanly.
- **Layer 9.** The manual documents `live` and each option; the changelog
  bullet; the transport's import boundary.
- Red first: the command refused as unknown, the routes absent, the
  transport directory absent, the stage still restoring on its own.

## Records

A new baseline spec, `openspec/specs/live-preview/`. Two ADRs at the next
numbers: *a take transport is the browser's pose of a take, written to
lift* (STAGE) and *the player is a transport over the render's stage*
(PIPELINE). The architecture overview's pipeline gains the branches drawn
above; "What is changing" loses "the studio's live preview" from what is
not built. `README.md` gains the command. `CHANGELOG.md` gains its bullet
under Unreleased.

## Decided and open

Decided by the pilot, 4 October 2026: the piece lives in Videomaker; the
viewer stays thin; the arrangement into the monorepo is the pilot's at
the migration. Open, with the orchestrator's preferences stated once: the
command's name (`live`); who re-evaluates (the Python side's own watcher);
caption text as a readout (yes). Composed joins are shown as a cut and
said so.

## The episode

The next timing revision of *Addition* in the Curta project, or of
*Cut and Advance* in Leonardo, and the Curta's take watched on the take
surface before any movie is written. What the episode records: the time
from the edit to the frame on screen, whether the Curta keeps the
narration's pace on the pilot's machine with a GPU, and what the take
surface showed that the spike had to find by hand.

## Relation to other records

- `roadmap.md` item 13 is this; the roadmap is not edited by this note.
- `declarative-python-api.md`: its fifth step and the studio requirement
  under "What it asks of the other repositories" are served by the seam
  above; its "Take belongs to the simulation" is the lift's premise.
- `docs/architecture-overview.md` "What is changing" and the
  film-production report's closure note say the live preview is not built.
  They stay right until a change lands.

## The campaign

Opened 4 October 2026 on branch `player` (worktree `WTs/player`) from
videomaker `main` at 7fba270, on the pilot's "do it", with the pilot's
instruction to **stop before sync**: every change is proposed, ratified,
applied red-first, tested and committed, and its baseline specs are not
synced nor the change archived until the pilot has validated the player in
the browser. Integration of `player` into `main` is then the pilot's.

Three changes, each an OpenSpec cycle in its own worktree on an opus agent,
the orchestrator's adversarial review being the ratification gate the pilot
delegated:

| # | change | worktree | depends on |
|---|---|---|---|
| 1 | `take-transport`: `transport/` (the take transport and the clock), the stage's one call, the viewer-handle types moved beside it, the import pin, the parity tests moved | `WTs/take-transport` | the contract |
| 2 | `live-server`: `checkFilm` extracted from the command script, `src/film-assets.mjs` extracted from the renderer, `src/live.mjs` (generation, routes, watcher, events), the `live` command | `WTs/live-server` | the contract |
| 3 | `player-page`: `player/` with the take and movie surfaces, the ruler, keys, readouts and reload, `src/player-build.mjs`, and `python -m machinome_movie watch` | `WTs/player-page` | 1 and 2 merged |

Then the episode, with the pilot: the Curta's *Addition* take on the take
surface, and a timing revision seen live.

## The contract

Written by the orchestrator before any cycle runs. The two parallel cycles
build against it, and the third consumes both. A cycle that finds the
contract wrong says so in its proposal and stops for the orchestrator;
it does not quietly build something else.

### The take transport, `transport/`

```ts
// transport/viewer-handle.ts — types only, moved from stage/runtime.tsx,
// which imports them from here afterwards: Vec3, Bank, MachineHandle,
// ViewerInstance, ViewerFactory and whatever the stage declared of the
// viewer's public handle. No value, no import.

// transport/take.ts
export interface MachineTransport {
  readonly identity: string;
  // restore({identity, bank}) on the viewer's machine, then the camera when
  // one is given (setView with camera, target, up, fov as the viewer's API
  // allows), else a redraw with the current view (setView(viewer.view())).
  // Refuses by name, before touching the viewer, a viewer whose document is
  // not clocked or whose machine has another identity: the stage's wording
  // today ("View … in shot …" is the caller's prefix; the transport names
  // the identities).
  pose(bank: Bank, view?: {camera: Vec3; target: Vec3; up?: Vec3; fov?: number}): void;
  bank(): Bank;                       // the committed bank the viewer reports
}
export interface TakeTransport {
  readonly kind: 'clocked' | 'loop';
  readonly duration: number;          // clocked: the take's length in take seconds; loop: 1
  readonly marks: ReadonlyArray<{name: string; time: number}>;   // loop: []
  seek(t: number): void;              // clocked: pose(bankAt(take, t)) with t clamped to [0, duration]; loop: setTime(t) clamped to [0, 1]
  time(): number;                     // the last sought time, 0 before any
  readonly machine: MachineTransport | null;   // clocked: the one seek poses through; loop: null
}
export function attachMachine(viewer: ViewerInstance, identity: string): MachineTransport;
export function attachTake(viewer: ViewerInstance, take: TakeDocument): TakeTransport;      // the document's take block, kind 'clocked'
export function attachLoop(viewer: ViewerInstance): TakeTransport;                          // the trivial take
```

Every call is synchronous: the viewer's `restore`, `setView` and `setTime`
render before they return, under on-demand and continuous rendering alike.
The pose rule is `bankAt` of `src/take.mjs`, imported, never copied; it is
typed for `tsc` by a declaration file beside the transport or by `allowJs`,
whichever the cycle finds cleaner, and bundled by esbuild as the stage's
own modules are.

```ts
// transport/clock.ts
export interface Clock {
  readonly duration: number;
  play(): void; pause(): void; playing(): boolean;
  seek(t: number): void;              // clamps to [0, duration]; pauses nothing
  time(): number;
  rate(): number; setRate(r: number): void;     // positive, finite
  onFrame(cb: (t: number) => void): () => void; // per animation frame while playing, and once after a seek; returns the unsubscribe
}
export function timerClock(duration: number, now?: () => number): Clock;   // performance.now by default; stops at duration
export function audioClock(audio: HTMLAudioElement, duration: number): Clock;  // the element's currentTime is the time; play, pause, seek and rate drive the element
```

The import pin: a layer 9 test reads every file under `transport/` and
refuses a static import that is not `./…` within the directory or
`../src/take.mjs`. No package, nothing from `stage/`, nothing else from
`src/`.

The stage change, in `stage/runtime.tsx` `poseViews`: a view whose state
carries a bank is posed by `attachMachine(viewer, config.take.identity)`
once per mounted instance and `pose(state.bank, view)` per frame, replacing
the restore, the identity check and the camera call it makes today. One
render per frame, as today. `window.film` gains `transport(key)` returning
that view's `MachineTransport` or `null`. Nothing else in the stage
changes; the frame keeps carrying the bank; ADR-012 and every proof hold.

### The live server, `src/live.mjs`

- `src/check.mjs`: `export async function checkFilm(source, {viewer, width,
  fps, silent})` is the body of the `check` command moved out of
  `bin/videomaker.mjs`: it loads, bundles, measures, resolves and prints
  exactly the lines `check` prints today, in the same order, and returns
  `{film, bundle, layouts}`. The script's `check` calls it and exits. The
  pipeline tests that pin `check`'s output stay green through the move.
- `src/film-assets.mjs`: `export function filmAssets({paths, config})`
  returns the `(req, res)` handler that `browserSession` builds inline
  today for a film's page and assets, and `browserSession` uses it.
- `export async function live(source, {viewer, width = 960, port = 0, poll
  = 0, open = false})` returns `{origin, close(), generation()}`. A
  generation is `{number, loadedAt, film, bundle, config, paths, stageSha256,
  exportSha256}` or, after a failed load, the previous generation with
  `refusal: {message, at}` set on the session. The first load must succeed
  or `live` throws as `check` would.
- Routes, beside the renderer's own (`/film.html` serves `src/film.html`;
  `/config.json`, `/stage.js`, `/stage.css`, `/viewer.js`, `/model/…` and
  the pictures through `filmAssets`):
  - `GET /film.json` →
    `{id, title, output: {width, height, fps, duration}, chapters: [{id, start, end}],
      shots: [{id, chapter, start, end, set, join: {kind, duration} | null, model: <the shot's resolved model span as the resolved document records it>}],
      cues: [{shot, id, at, until}], takes: {<name>: {kind, duration, marks: [{name, time}]}},
      speech: {mix: boolean, captions: boolean}, stage: {sha256}, viewer: {api},
      generation: {number, loadedAt}, refusal: {message, at} | null}`.
    Times in seconds, video time unless under `takes`, where they are take
    seconds.
  - `GET /frame?t=<seconds>` → `frameAt(film, round(t·fps)/fps)` as JSON,
    `t` clamped to `[0, duration)`; 400 for a missing or non-finite `t`.
  - `GET /narration.wav`, `GET /captions.json` → the files `speech` wrote
    under `_build`, 404 when absent.
  - `GET /events` → server-sent events, `event: loading | generation |
    refused`, `data:` the generation's `{number, loadedAt, stageSha256,
    exportChanged}` or the refusal's `{message, at}`; a `generation` event
    is sent to a new subscriber at once.
  - `GET /`, `/player.js`, `/player.css` → `_build/player/` when it exists,
    else 404 `The player is not built`. The player change adds the build.
- The watcher settles changes within 200 ms into one reload: the document
  file (and `production.yaml` for an episode), the stage modules, the
  excerpt sources, the stills and clips, the export manifest, the audio
  cache and the mix. `fs.watch` with `recursive: true`; `--poll <ms>` uses
  stat polling instead. `_build/stage/`, `_build/player/`, `_build/preview/`
  and the frames are never watched.
- Reload runs `checkFilm` again. Success replaces the generation
  atomically and emits `generation`; failure emits `refused` and keeps the
  generation served.
- The command: `videomaker live SOURCE [--viewer BUNDLE.js] [--width 960]
  [--port 0] [--poll MS] [--open]`, in `bin/videomaker.mjs` beside the
  others, prints the check lines, then `Live: http://127.0.0.1:<port>/`,
  and runs until SIGINT, exiting 0. `--open` runs `xdg-open` on the
  address, best effort.

### The player, `player/` (the third cycle)

- `src/player-build.mjs` bundles `player/index.ts` with esbuild into
  `_build/player/player.js` and `player.css`, reused by content, run by
  `live` before serving; `tsc --noEmit` over `player/` in the suite. No
  React; plain DOM.
- Surfaces by location hash: `#movie` (the default when the document has
  chapters) and `#take/<name>` for each take `/film.json` lists; a loop
  document gets `#take/loop`.
- Movie surface: an iframe on `/film.html` of exactly `output.width ×
  output.height` at the server's `--width`, CSS-scaled to fit; frames from
  `/frame`; `setFrame` through `contentWindow.film` after `film` or
  `filmError` appears; `audioClock` over `/narration.wav` when
  `speech.mix`, else `timerClock`.
- Take surface: `MachinomeViewer.mount` on `/model/manifest.json` with
  `renderMode: 'continuous'`, `animation: 'external'`, `autoplay: false`,
  `driverControls: 'none'`, `partControls: 'none'`; `attachTake` or
  `attachLoop`; `timerClock`; the viewer's own navigator for the camera.
- Shared: the ruler (chapters as bands, shots as segments, joins hatched,
  cues as ticks, marks as flags, the playhead; take surface: marks only),
  keys (space; left and right one frame; with shift one second; home,
  end; click on a shot or a mark), the readout (time, frame, shot, chapter,
  mark; the current caption's text when `speech.captions`), the refusal
  display, the reload (same stage hash and export: keep the iframe and
  pose the current time again; otherwise reload the iframe; take surface:
  remount only when the export changed).
- One pose in flight; the latest requested time wins.
- `python -m machinome_movie watch <project-dir> <movie> [--out FILE]
  [--interval SECONDS]`: evaluates, then re-evaluates whenever a file under
  the project (excluding `_build` and `.git`) changes by stat polling,
  printing the output path or the refusal each time; stdlib only; the loop
  body is a function a test drives with an injected clock.
