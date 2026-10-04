## Why

The episodes are the campaign's (`workflow/ongoing/player-campaign/plan.md`,
"The episode"): the Curta's *Addition* take watched on its own before any
movie is written, and the next timing revision of *Addition* (the Curta
Type I 3x project, `videos/addition/`) or of Leonardo's *Cut and Advance*
(`videos/cut_and_advance`) seen live. The finding is
`workflow/ongoing/roadmap.md` item 13, *Live preview*, with its recorded
cost: every timing revision of *Revolutions* meant a preview run and a look
at the contact sheet, *Addition* renders in 63 minutes, and the Curta's take
was written blind, because nothing could show a take before the movie
rendered. The pilot's rulings of 4 October 2026 put the piece in Videomaker,
as two transports over the render's stage: watching a scenario is a feature
by itself, and a video is a recording of that watching.

The campaign's first two changes built everything under the page:
`take-transport` (ADR-020) the pose of a take in a browser and its clocks,
`live-server` (ADR-021) the session that serves the render's stage page, the
frame function, the outline, a take's document and the events, and answers
`/` with `The player is not built`. This change, the third and last, builds
the page and the Python side's watcher, so that `videomaker live` opens in a
browser as a scenario player and a movie player, and a Python movie's
document is evaluated again when its declarations change.

## What the film does with the result

Nothing in a film changes; no frame, document or render differs. The author
of *Addition* or *Cut and Advance* runs `python -m machinome_movie watch`
beside `videomaker live`, opens the address, and scrubs the film at the
renderer's frames, its narration as the clock: an edit of the movie's Python
is evaluated, loaded and posed again within seconds, with `check`'s refusal
shown when there is one and the last accepted film kept. The Curta's take is
watched on its own, the machine posed at each mark by the rule the frame
uses, the camera free. What the episode then records (the time from an edit
to the frame on screen, whether the Curta keeps the narration's pace on a
GPU, what the take surface showed) is the pilot's, in a browser.

## What Changes

- **The player page, `player/`**: TypeScript, plain DOM, no React, bundled
  by a new `src/player-build.mjs` with the esbuild the stage build uses
  into `_build/player/` (`index.html`, `player.js`, `player.css`, the names
  `live` already serves), reused by content, every file named by the tool
  so its bytes never depend on where the tool lies. `live` builds it once
  per session, before serving. Two surfaces, chosen by the location hash:
  - **Movie** (`#movie`, the default): the render's stage page in an iframe
    of exactly the session's output geometry, scaled down to fit; each
    frame fetched from `/frame` and posed through the iframe's
    `window.film.setFrame`, after `film` or `filmError` appears, as the
    renderer does; the narration's mix as the clock when it exists, a timer
    otherwise. A composed join (dissolve, fade, wipe, slide) is shown as a
    cut at its midpoint and said so; a reframe is drawn live as the frame
    gives it. The page draws nothing in the frame.
  - **Take** (`#take/take` for a clocked take, `#take/loop` for a posed
    loop): the viewer mounted on the export alone, the take transport
    attached to `/take.json` or the loop, a timer clock, the viewer's own
    navigator for the camera. Nothing of the stage is loaded.
  - **Shared**: the ruler (chapters, shots, joins hatched, cues, marks, the
    playhead; marks only on the take surface) and its scrubber: a pointer
    pressed on the ruler seeks to the time under it and, held and moved,
    keeps seeking, latest time winning, frames the stage cannot reach
    dropped, as a play does, the playhead left where it is released; a click
    on a shot's name or a mark's flag seeks to it; the keys (space; a frame
    left and right; a second with shift; home, end); the readout under the
    frame (time, frame, shot, chapter, mark, join, caption); the refusal
    display; and the reload driven by `/events`: the iframe and the viewers
    kept when the stage page and the export are unchanged, the current time
    posed again. One pose in flight; the latest requested time wins; the
    audio never waits.
- **The outline places the marks in video time** (a contract gap, below):
  `/film.json` gains `marks`, each mark at the output frames where a shot's
  model time reaches it, so the movie surface can flag and seek them.
- **`python -m machinome_movie watch <project-dir> <movie> [--out FILE]
  [--interval SECONDS]`**: evaluates as `evaluate` does and prints the
  output path, then evaluates again whenever a file under the project
  (outside `_build`, `.git` and `__pycache__`) changes its status, polled
  at the interval (0.5 s by default), printing the path or the refusal
  each time, until interrupted. Standard library only; the loop body is a
  function a test drives with an injected clock and file listing.
- **Records**: ADR-022 (PIPELINE), *The player is two transports over the
  render's stage, and a video is its recording*, Proposed, indexed; the
  README (the player: surfaces, keys, what is not drawn live; `watch`
  beside `live`), `docs/declaring-a-movie.md` and `python/README.md`
  (`watch` beside `evaluate`), the architecture overview (the player in the
  pipeline and the modules; "What is changing" no longer says the page is
  not built), `AGENTS.md` (the status line; layer 4 runs the player's
  tests), `CHANGELOG.md` (one bullet).

## Where the contract is read

The plan's contract (part "The player, `player/`") is binding, read with
what the two merged changes built. The design argues each reading:

1. **Marks in video time are missing from the outline.** The contract's
   ruler flags the take's marks on the movie surface and a click on a mark
   seeks to it, but the outline `live-server` built gives marks in take
   seconds only, and where a mark falls in video time depends on each
   shot's model keys and their curves, which the browser does not compute
   (it computes no movie frame). This change adds `marks: [{name, shot,
   at}]` to `/film.json`, computed in Node from the timeline's own model
   time on the renderer's frame grid (design D3). The alternative is no
   mark flags on the movie surface (the take surface keeps them).
2. **A shot's fade in or fade out is not a join**, and the stage does not
   draw its plate either (the renderer composes it). The readout says such
   a frame is shown without its fade, as it says a join is shown as a cut
   (D5).
3. **A mark is a stop on the take surface**: the ruler and the readout snap
   to the film's frames, and a click on a mark seeks the take to the mark's
   own time, so a mark between two frames still poses its recorded bank
   (D7).
4. **`watch` evaluates in a fresh process each time** (`python -m
   machinome_movie evaluate`, the interpreter running it), because a
   project's modules imported once and imported again in one process keep
   stale modules and class identities; and it also passes over
   `__pycache__`, which that evaluation writes (D10).
5. **The page carries its state on `window.player`** (surface, time,
   frame, generation, the poses made, the last pose, the take transport,
   seek, play, pause and a promise of the poses settling), for the proofs
   and for a page that frames it; provisional, not a protocol (D8).
6. **The ruler is a scrubber** (the orchestrator's addition at
   ratification, 4 October 2026: the roadmap's item is "a timeline
   scrubber", and a click on a shot or a mark is not one). A pointer
   pressed anywhere on the ruler but a shot's name or a mark's flag seeks to
   the time under it and keeps seeking while it is held and moved, through
   the same one-pose-in-flight rule as a play; a scrub pauses the clock,
   and the playhead stays where the pointer is released (D8).

## Capabilities

### New Capabilities

None: the player belongs to the `live-preview` capability, which the
`live-server` change introduces and which is not yet in `openspec/specs/`
(the campaign stops before sync). This change's delta to it adds
requirements only.

### Modified Capabilities

- `live-preview` (introduced by `live-server`, unsynced): the player is
  built and served; the outline gives marks in video time; the surfaces,
  the ruler, the keys, the readout, the refusal display and the reload.
- `declarative-movie`: a movie is evaluated again when its project's files
  change (`watch`).

## Impact

New: `player/` (`index.html`, `index.ts`, `model.ts`, `poser.ts`,
`player.css`, `tsconfig.json`, unit tests), `src/player-build.mjs`,
`python/machinome_movie/watch.py`, tests at layers 1, 4, 5, 6, 8 and 9.
Changed: `src/live.mjs` (the build before serving; `markInstants` and the
outline's `marks`), `python/machinome_movie/__main__.py`, `vitest.config.mjs`
(layer 4 runs `player/**/*.test.ts`), `test/support/reach.mjs` (what the
player build reads), `test/viewer-double.mjs` (a mount without a camera,
as the take surface mounts the viewer), the existing layer 8 test (`/` is
now the built player). No change to the stage, the transport, the
timeline, the renderer, the document, its schema or the fixtures' documents,
so no film's stage bundle or shot cache key changes. No new dependency.

## Non-goals

Composed joins or fades drawn live (an open line of the plan: a fade as a
black overlay in the transition layer, a stage change); the studio's
panel; any proof on a real film (finding 16 of `workflow/warts.md`);
speech: nothing is bought, no key is read. No publication, push or paid
request.
