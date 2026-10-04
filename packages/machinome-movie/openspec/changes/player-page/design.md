## Context

The campaign's contract (`workflow/ongoing/player-campaign/plan.md`, "The
contract", part "The player, `player/`") is binding for this change, read
together with what the two merged changes built, which wins where the two
differ:

- `transport/` (`take-transport`, ADR-020): `attachTake(viewer, doc)` over
  the take document `{model: {expectedDurationSeconds}, marks, take}`,
  `attachLoop(viewer)` normalized to [0, 1], `timerClock(duration, now?,
  frames?)` and `audioClock(audio, duration, frames?)`, every call
  synchronous; the stage's `window.film` gains `transport(key)`, beside
  `setFrame`, `views()` and `filmError`. Its sources import only their own
  directory and `src/take.mjs`, a layer 9 pin.
- `src/live.mjs` (`live-server`, ADR-021): one session per film on the
  loopback interface; `/film.json`, the outline at the session's width
  (`output` is the session's geometry; `takes` keyed `take` for a clocked
  take, with its length, its marks in take seconds and `url: '/take.json'`,
  or `loop` with its period and marks in model seconds); `/frame?t=`, the
  renderer's frame at the nearest output instant, clamped; `/take.json`;
  `/film.html` and its files at the root; `/narration.wav` and
  `/captions.json` (an array of `{text, start, end}` in video seconds);
  `/events` (`loading`, `generation` `{number, loadedAt, stageSha256,
  exportChanged}`, `refused` `{message, at}`), where `stageSha256` hashes
  the whole stage page as served and `exportChanged` compares with the
  previous generation; and `/`, `/player.js`, `/player.css` from the film's
  `_build/player/` when they exist, else 404 `The player is not built`.
- The renderer (`src/render.mjs`, `show`) poses a frame by
  `window.film.setFrame` of the frame without its `transition`, adding back
  `{transition: {kind: 'reframe', progress, boxes}}` for a reframe, which
  the stage draws live (ADR-010); a dissolve, wipe or slide is composed from
  captures of `transition.outgoing` and the frame, a fade from one of them
  under a colour plate, a shot's fade in or out (`field` `fadeIn`,
  `fadeOut`) from the frame under a plate. The stage itself draws no
  composed join and no plate.

## Goals / Non-Goals

**Goals:** the page the contract describes, on the server and the
transport as built: two surfaces, one ruler, the keys, the readout, the
refusals and the reload; the player built as tool content; the Python
watcher; each proved at the innermost layer that can fail, red first.

**Non-Goals:** those of the proposal: drawing a composed join or a fade
live, the studio's panel, any proof on a real film.

## Decisions

### D1. `player/`: plain DOM over the transport, nothing of the stage

`player/` holds `index.html` (the page: its stylesheet, its regions and
`/player.js`), `index.ts` (the entry: the surfaces, the ruler and readout
drawn in the DOM, the keys, the events), `model.ts` (pure: snapping, the
stage request and the join-as-cut rule, routing, the ruler's geometry, the
readout, the reload decision), `poser.ts` (one pose in flight, the latest
wins), `player.css`, `tsconfig.json` (the transport's strict options) and
the unit tests beside them. It imports only its own files and the take
transport (`../transport/take`, `../transport/clock`, the handle's types):
no package, no React, nothing of `stage/`, nothing of `src/` directly (the
pose rule reaches it through the transport). A layer 9 test holds that
boundary, and the transport's own pin keeps refusing any import of
`player/` from `transport/`.

The page types the subset of the stage's `window.film` it calls
(`setFrame`, `transport`, `views`, `filmError`) structurally, rather than
importing `stage/runtime.tsx`, which would bring React's types into the
player's type check.

### D2. `src/player-build.mjs`: built once per session, reused by content, named by the tool

`buildPlayer(build)` writes `<build>/player/index.html` (the bytes of
`player/index.html`), `player.js` and `player.css` (esbuild over
`player/index.ts`, IIFE, browser, es2022, no source maps, no legal
comments, as the stage bundle), and `inputs.json`, the record:
`{key, inputs: [{path, sha256}], htmlSha256, jsSha256, cssSha256,
versions}`. It returns the three paths, their hashes and whether it
`reused` them.

- **Names (ADR-013's rule):** esbuild names each file relative to the output
  directory, so the bundle's comments would carry the path from a film's
  `_build/player/` to the tool. Every file of `player/`, `transport/` and
  `src/` is named `videomaker/player/<file>`, `videomaker/transport/<file>`
  and `videomaker/src/<file>`, by the stage build's own `renameOutput`,
  before anything is written; two builds into directories at different
  places write the same bytes.
- **Key:** the SHA-256 of every file under `player/` and `transport/` but
  their tests and of `src/take.mjs`, each under its name, and esbuild's
  version. The player's imports are held to those files by the boundary pin
  (D1), so the key covers every input. An equal key whose outputs still
  hash as recorded is reused without building; a missing or damaged output
  rebuilds; never an mtime.
- **When:** `live` calls it once, after the first load is accepted and
  before the server listens, into the film's build directory (where
  `live-server` serves `/`, `/player.js` and `/player.css` from). It is
  tool content: no generation rebuilds it, and the session's handle
  reports it (`player: {sha256, reused}`). `live` prints nothing more: its
  lines stay `check`'s and the address line.

`_build/player/` is never watched (`live-server`, D7), so the build reloads
nothing.

### D3. The outline gives the marks in video time

`markInstants(film)`, pure, in `src/live.mjs`: for each output frame `i`
on the renderer's grid (`i / fps`, `i` from 0 to `round(duration · fps) −
1`), the shot that frame shows (`frameAt`'s rule: `start ≤ t < end`) and
its model time there (`modelSecondsAt` of `src/timeline.mjs`, the function
the frame's pose reads). A mark is placed at frame `i` of a shot when the
shot's model time there is the mark's time (within 10⁻⁹) and the frame
before it in the same shot was not, or when the model time has passed the
mark between the previous frame of the same shot and this one; so a shot
that starts at a mark flags it at its first frame, a shot that crosses it
at the first frame past it, a shot that holds at it once. The marks are
the document's `marks`: take seconds for a clocked take, model seconds for
a posed loop, both compared with the shot's model time. The outline gains
`marks: [{name, shot, at}]`, in video time, ordered by `at` then name.

On the fixture `count` (10 fps): `one` at 3.2 in `nine` (the shot begins
at the mark) and `nine` at 5.3 in `carry`; `ten` (8 s) is never reached
on the grid (`carry`'s last frame poses 7.97 s), so it is not flagged on
the movie ruler, and is on the take surface. A flag means a frame poses
the mark, and nothing else.

`src/timeline.mjs` is not edited (its hash is in the shot cache's common
key); `src/live.mjs` reads `modelSecondsAt` and `filmShots` from it.

### D4. Surfaces by the location hash

`routeOf(hash, outline)`: `#movie` is the movie surface; `#take/<key>` the
take surface for a key of `outline.takes` (`take` or `loop`); an empty or
unknown hash is the default, the movie surface when the outline has
chapters (every film has), else the first take, and the page replaces the
hash with it. The switch is a list of links, one per surface
(`Movie`, `Take` or `Loop`); a `hashchange` takes the current surface down
(the iframe, or the viewer's host, removed) and builds the other.

### D5. The movie surface

- **Geometry.** An iframe on `/film.html` whose `width` and `height` are
  `output.width × output.height` of the outline (the session's `--width`
  and the renderer's height for it), scaled by a CSS transform to fit the
  region the page gives it, and never above 1: the stage is drawn at the
  size `render --width` captures, and a larger window shows it at that
  size. The iframe takes no pointer events and no focus, so the keys stay
  the page's; the page draws nothing inside it.
- **Readiness.** After the iframe loads, the page waits, a frame at a time,
  for `contentWindow.film` or `contentWindow.filmError`, as the renderer
  does; a `filmError` is shown in the refusal display.
- **A pose.** The frame of the snapped time is fetched from `/frame?t=`
  and posed by `film.setFrame(request)`, where `stageRequest(frame)` is the
  renderer's `show` rule: the frame without `transition`, with
  `{transition: {kind: 'reframe', progress, boxes}}` added back for a
  reframe. Inside a composed join (`field` `transition`, kind `dissolve`,
  `wipe`, `slide` or `fade`), the page poses the outgoing frame
  (`transition.outgoing`, itself without a transition) while the frame's
  time is before the join's midpoint (`time − start < duration / 2`; for a
  fade, while the frame carries an outgoing picture, which is the same
  half), and the frame itself from the midpoint on. A shot's fade in or
  out poses the frame without its plate. `stageRequest` returns, beside the
  request, what is shown: `{field, kind, into, duration, shown: 'cut' |
  'live' | 'unfaded'}`, which the readout words: `dissolve into carry,
  0.5 s: shown as a cut at its midpoint`, `reframe into question, 0.8 s:
  drawn live`, `fade in, 1 s: shown without its fade`.
- **The clock.** With `speech.mix`, `audioClock` over an audio element on
  `/narration.wav` and the film's duration; otherwise `timerClock` of the
  duration. When the mix's length, once known, differs from the film's by
  more than a frame, the readout says so (`the mix is <a> s and the film
  <b> s: run speech again`): it is the mix `speech` last wrote. The clock is
  made again at each generation, keeping its time and whether it played.
- **Snapping.** Video time snaps to the frame grid: index
  `clamp(round(t · fps), 0, round(duration · fps) − 1)`, the server's rule,
  so the last frame is `(count − 1) / fps`.

### D6. One pose in flight, the latest wins

`poser(pose)`: `request(t)` records `t` as wanted; when no pose runs it
starts `pose(t)`; when one finishes and the wanted time differs from the
one posed, it starts that one. Requests made while a pose runs replace each
other, so a frame the stage cannot reach before the clock moves on is
dropped, never queued; the clock is never paused for a pose, so the audio
never waits. `idle()` resolves when nothing runs and nothing is wanted.
The clock's per-frame callback and every seek request the snapped time.
An error of a pose (a fetch, `setFrame`) is shown in the refusal display
and does not stop the poser.

### D7. The take surface

- **Mount.** `/viewer.js` is loaded on first use (a script element), then
  `MachinomeViewer.mount(<host>, '/model/manifest.json', {renderMode:
  'continuous', animation: 'external', autoplay: false, driverControls:
  'none', partControls: 'none'})`: no camera is given, the viewer frames the
  model itself and its navigator moves the camera. Nothing of the stage is
  loaded.
- **Attach.** `take`: `attachTake(viewer, <the JSON of /take.json>)`;
  `loop`: `attachLoop(viewer)`. A refusal of the transport is shown in the
  refusal display, named by the take.
- **Clock and seek.** `timerClock` of the take's duration: the transport's
  `duration` for a clocked take; the loop's period in seconds from the
  outline for a loop, whose transport is sought at `t / period`. Take time
  snaps to the film's frames, end included (index `clamp(round(t · fps), 0,
  round(duration · fps))`), so the take's last instant is reachable; a click
  on a mark seeks to the mark's own time, a stop, so a mark between two
  frames still poses its recorded bank. The readout shows the time posed
  and its nearest frame.
- **Ruler.** The take's marks only (`transport.marks`, or the loop's from
  the outline in model seconds).

### D8. Shared: the ruler, the keys, the readout, the refusals, `window.player`

- **Ruler geometry** (`rulerOf(outline, surface)`, pure), in fractions of
  the surface's duration: chapters as bands, shots as segments, each
  shot's incoming join hatched over `[start, start + join.duration]`, cues
  as ticks at `at`, marks as flags (the outline's `marks` in video time, or
  the take's), and the playhead at the time. A shot's name and a mark's
  flag are controls: a click on one seeks to the shot's start or to the
  mark. Ticks and hatches take no pointer of their own.
- **The scrubber** (the orchestrator's addition at ratification). A pointer
  pressed anywhere else on the ruler (the bands, the segments, the track
  under them) pauses the clock, captures the pointer and seeks to the time
  under it; while it is held, each move seeks to the time under it again;
  releasing it, or losing the capture, ends the scrub with the playhead at
  the last time sought, the clock paused. The time under the pointer is
  `timeAt(x, ruler)` (pure): the pointer's fraction of the ruler's width,
  clamped to [0, 1], times the surface's duration, then snapped as every
  time is (D5, D7). Every seek of a scrub goes through the clock and the
  poser as a play's frames do (D6): one pose in flight, the latest time
  wins, a frame the stage cannot reach before the pointer moves on is
  dropped.
- **Keys** on the document: space plays or pauses; left and right one
  frame from the current frame; with shift one second (`fps` frames); home
  the first frame; end the last. A seek keeps the clock playing or paused,
  as the clock's contract says.
- **Readout** (`readoutOf`, pure), under the frame: the time posed, the
  frame index of the count, the shot and the chapter (movie), the mark at
  the playhead (a mark within half a frame of the time posed), the join as
  D5 words it, and the caption whose `[start, end)` holds the time when
  `speech.captions` (fetched again at each generation). Nothing of it is
  drawn in the frame.
- **Refusal display:** the outline's `refusal` at load and each `refused`
  event's message, until the next `generation`; a stage error or a pose's
  error beside it.
- **`window.player`**: the page's state for the proofs and for a page that
  frames it: `surface()`, `time()`, `frame()`, `playing()`, `generation()`,
  `poses()` (the frame indices posed, in order), `observed()` (the last
  `setFrame`'s report on the movie surface), `take()` (the take surface's
  transport), `seek(t)`, `play()`, `pause()` and `idle()`. Provisional,
  as every name here, and said so in the spec; not a protocol.

### D9. The reload

`reloadAction(surface, held, event)` (pure), with `held` the generation the
page shows (`number`, `stageSha256`):

- an event of the generation held does nothing (the stream's first event);
- on the movie surface, the next generation with the same `stageSha256` and
  `exportChanged` false keeps the iframe and its viewers: the page fetches
  the outline (and the captions) again and poses the current time again;
  otherwise it reloads the iframe, waits for `film` again, then poses;
- on the take surface, `exportChanged` remounts the viewer (the script
  loaded again) and attaches again; otherwise the page attaches the
  transport again to the new `/take.json` and seeks the current time again;
- a generation that skips one (the page missed an event, its stream
  reconnected) is treated as changed, since `exportChanged` compares only
  with the generation just before it.

A `loading` event marks the page as reloading; `refused` shows its message
and keeps everything as it is.

### D10. `python -m machinome_movie watch`

`machinome_movie/watch.py`:

- `listing(project)`: every file under the project, by its path relative to
  it, with its size, modification time and inode, passing over directories
  named `_build`, `.git` and `__pycache__` at any depth (the tool's products,
  Git's store, and what evaluation's own imports write).
- `Watch(evaluate, files, sleep, interval)`: `start()` evaluates once and
  takes the listing; `step()` sleeps one interval through the injected
  `sleep`, takes the listing again, and evaluates once when it differs
  (a file added, removed, or whose size, time or inode changed), returning
  whether it did. `run()` is `start()` then `step()` until interrupted.
- `evaluate` runs `python -m machinome_movie evaluate <project> <movie>
  [--out FILE]` in a child process of the interpreter running `watch`,
  which prints the output path or the refusal as `evaluate` does; a refusal
  does not stop the watch. A child process because importing a project's
  modules again in one process keeps the modules imported before, and the
  classes declared by them, so a second evaluation could read stale
  declarations; a fresh process evaluates exactly what `evaluate` would.
- The command line: `watch <project-dir> <movie> [--out FILE] [--interval
  SECONDS]`; the interval a positive number of seconds (0.5 by default),
  refused otherwise naming `--interval`. An interrupt ends it with status 0.

### D11. Proofs, red first, innermost first

- **Layer 1 and 9 (pytest).** `tests/test_watch.py`: with an injected
  listing and sleep, `start` evaluates once; a `step` over an unchanged
  listing evaluates nothing; a changed size, time or inode, a file added or
  removed each evaluate once; each `step` sleeps one interval; `listing`
  passes over `_build`, `.git` and `__pycache__`. The command line on a copy
  of the fixture project: `watch` prints the path, a touched module prints
  it again, an interrupt exits 0; a bad interval is refused naming
  `--interval`. The manual and `python/README.md` document `watch`. Red:
  the module absent, `watch` an unknown subcommand (argparse's status 2).
- **Layer 3.** `test/live.test.mjs`: `markInstants` on the resolved `count`
  (`one` at 3.2, `nine` at 5.3, no `ten`) and `tour`, and `outline`'s
  `marks`. Red: `markInstants` not exported.
- **Layer 4 (jsdom; `tsc --noEmit -p player/tsconfig.json`).**
  `player/model.test.ts`: snapping (movie and take, the end), the stage
  request (plain, reframe, the four composed joins before and after the
  midpoint, a shot's fade), routing, the ruler's geometry from the outline
  of `count` and the time under a pointer, the readout (shot, chapter,
  mark, join, caption), the reload decision; `player/poser.test.ts`: one pose at a time, the latest wins,
  `idle`. Red: `player/` absent.
- **Layer 5 (Chromium, the double, the session in-process).**
  `test/browser/player.test.mjs`: on `count`, the movie surface poses the
  frame `/frame` gives, the iframe's report equal to the renderer's for the
  same frame; A-B-A identical pixels of the iframe; the keys and the clicks;
  a drag on the ruler from `once` across the boundary into `nine` poses
  frames of both shots and ends, released, on the released time;
  a `generation` with the same stage hash keeps the iframe (its window and
  its viewer instance) and poses again; a changed stage module reloads it;
  a refusal shown and cleared; the caption readout from a fixture
  `captions.json`; the take surface attaches from `/take.json` and each mark
  clicked poses the recorded bank. On `tour`, the join rule (the outgoing
  frame before a dissolve's midpoint, the incoming after; a wipe; a reframe
  posed live; a fade in without its plate) and the loop surface. Red: `/`
  is 404, so the page has no `window.player`.
- **Layer 6 (the API 29 bundle).** `test/viewer/player.test.mjs`: the take
  surface over the counter's real export, each mark clicked, the bank the
  viewer's machine holds equal to the record.
- **Layer 8.** `test/pipeline/live.test.mjs`: `/`, `/player.js` and
  `/player.css` are the built player; a second session reuses it, the same
  bytes. Red: `/` is 404.
- **Layer 9.** `test/player-build.test.mjs`: two builds into directories at
  different places write the same bytes, named `videomaker/player/…`,
  `videomaker/transport/…`, `videomaker/src/take.mjs`; a second build is
  reused; a damaged output rebuilds. The boundary pins (D1). The README,
  the changelog, the ADR index, the overview and `AGENTS.md`. Red: the
  module absent, the records unwritten.

The double (`test/viewer-double.mjs`) mounts without a camera, as the real
viewer does, at a default camera of its own; every slow test's key reads
it, so every slow test runs once more.

### D12. ADR-022 and the records

`docs/adrs/PIPELINE/ADR-022-the-player-is-two-transports-over-the-renders-stage-and-a-video-is-its-recording.md`,
Proposed: the player is a page over the session, with two surfaces that
transport the film and the take through the stage and the viewer the
renderer uses, drawing nothing of the film itself and saying what it
cannot show; a video is the recording of the movie transport. It stays
Proposed: the campaign stops before sync.

## Risks / Trade-offs

- [A Curta frame costs about a second to pose in software] → the poser
  drops what it cannot reach; the narration keeps its pace; the cost on a
  GPU is the episode's first measurement.
- [A mix older than the document plays out of step with the film] → the
  readout says when its length differs; a mix of the same length re-timed
  is not detected (the session cannot know which document `speech` mixed).
- [The take surface's viewer renders continuously] → its navigator needs
  it; one viewer, only while that surface is shown.
- [A composed join or a fade is not drawn as the film draws it] → said in
  the readout and the README; an open line of the plan, not proposed.
- [The double's default camera] → only the take surface mounts without one;
  the real viewer's own framing is proved at layer 6.
- [`window.player` is a seam a host may come to rely on] → named
  provisional in the README; no protocol before a release.
