## Why

The episodes are the Curta film *Addition* (the Curta Type I 3x project,
`videos/addition/`) and Leonardo's *Cut and Advance*
(`videos/cut_and_advance`), as `workflow/ongoing/player-campaign/plan.md`
names them; the finding is `workflow/ongoing/roadmap.md` item 13, *Live
preview*, with its recorded cost: every timing revision of *Revolutions*
meant a preview run and a look at the contact sheet, *Addition* renders in
63 minutes, and the Curta film's take was written blind, because nothing
could show a film, or a take, before the movie rendered. The pilot's
rulings of 4 October 2026 put the piece that shows them in Videomaker, for
the studio to use later, as two transports over the render's own stage.

This change is the server half of that piece, cut from the campaign's
contract ("The live server, `src/live.mjs`"): one long-lived process that
loads the film as `check` does, serves the renderer's stage page and the
frame function to a browser, and reloads when the film's inputs change. The
player page that drives it is the campaign's third change (`player-page`);
the take transport is the second (`take-transport`), in parallel.

## What the film does with the result

Nothing in a film changes. With this change and `player-page`, the author
of *Addition* or *Cut and Advance* edits the movie, sees `check`'s lines
again within a fraction of a second of the save (or the refusal, while the
last accepted film stays served), and scrubs the result in a browser at the
renderer's frames, instead of a preview run. Until `player-page` lands, the
server answers its routes and says at `/` that the player is not built;
what the episode records (the time from an edit to the frame on screen, the
Curta's pace on a GPU) waits for the page.

## What Changes

- **`check`'s body moves into `src/check.mjs`** as
  `checkSource(source, {viewer, width, fps, silent})`: it loads, bundles,
  measures, resolves and prints exactly the lines `check` prints today, in
  the same order, and returns `{film, bundle, layouts}`. The command calls
  it and exits as before; the pipeline tests that pin `check`'s output stay
  green with their expectations unchanged.
- **The renderer's asset handler moves into `src/film-assets.mjs`**:
  `filmAssets({paths, config})` is the `(req, res)` handler `browserSession`
  built inline, and the map of a film's page files it serves moves with it,
  so the renderer and the live session serve the same files the same way.
  The renderer's behaviour is unchanged; editing `src/render.mjs` changes
  the shot cache's common key once for every film, as every edit of the
  renderer does (design D2).
- **`src/live.mjs`**: `live(source, {viewer, width = 960, port = 0, poll =
  0, open = false})` returns `{origin, close(), generation()}`. A
  **generation** is one accepted load. The first load must succeed or
  `live` throws as `check` would; a later failed load is a **refusal**: the
  previous generation stays served. Routes beside the renderer's own:
  `/film.json` (the outline of the film), `/frame?t=` (the renderer's frame
  at the nearest output instant), `/narration.wav` and `/captions.json`
  (what `speech` wrote, or 404), `/events` (server-sent `loading`,
  `generation`, `refused`), `/film.html` (the renderer's stage page, its
  assets at the root), and `/`, `/player.js`, `/player.css` from
  `_build/player/` when it is built, else 404 `The player is not built`.
  A watcher settles changes to the film's inputs within 200 ms into one
  reload, or polls them with `--poll`. `live` opens no Chromium to draw;
  `checkSource` opens the headless layout page as `check` does.
- **The command** `videomaker live SOURCE [--viewer BUNDLE.js] [--width
  960] [--port 0] [--poll MS] [--open]` prints the check lines, then
  `Live: http://127.0.0.1:<port>/`, and runs until interrupted, exiting 0;
  `--open` runs `xdg-open` on the address, best effort.
- **Records**: a new capability `live-preview`; ADR-021 (PIPELINE),
  *A live session serves the render's stage and the frame function to a
  browser*, Proposed; `README.md` (the command and each option),
  `docs/architecture-overview.md` (the live branch of the pipeline, the
  three modules), `CHANGELOG.md`, and the status line of `AGENTS.md` that
  says there is no live preview.

## Where the contract is refined

The campaign's contract is followed, with these readings, each argued in
`design.md`; the orchestrator ratifies or corrects them:

1. **The watcher is not recursive** (D7). The contract asks for `fs.watch`
   with `recursive: true` over the inputs' directories and that
   `_build/stage/`, `_build/player/`, `_build/preview/` and the frames are
   never watched. The inputs' directories include `_build/` itself (a
   Python movie's document, the mix and the captions live there) and a
   YAML episode's directory, which holds `_build/`; a recursive watch of
   either watches the tool's own outputs. Each input's directory is
   watched without recursion, and only events naming an input reload; a
   stage module's own imports are inputs by name, read from the bundle's
   record, so nothing needs recursion.
2. **The stage hash is the stage page's** (D3): `stageSha256` hashes what
   the page boots from, the script, the stylesheet, the config and the page
   itself, not the script alone, because a stylesheet change or a
   document change that changes the config leaves `stage.js`'s bytes as
   they were and the page must still reload.
3. **`/film.json`'s `output` is the session's geometry** (D5): the width is
   `--width` and the height the renderer's rule for it, as `render --width`
   captures, since that is the size the player gives the stage page and the
   outline is where the player reads it.
4. **The take's name** (D5): the document records none; the outline keys
   the document's clocked take as `take` and a posed loop as `loop`, the
   loop with its period and marks in model seconds.
5. **Small additions to the named functions** (D2, D4): `filmAssets` takes
   an optional `onError`, `assetServer` an optional `port`, and the path map
   and `clipUses` move with the handler.
6. **`checkFilm` is `checkSource`** (D1): `src/timeline.mjs` already exports
   a `checkFilm(film)`; the contract's name yields to the existing one, by
   the orchestrator's ruling at ratification.

## Capabilities

### New Capabilities

- `live-preview`: the `live` command and the server it runs: the first
  load as `check`, the address line, the outline, the frame at a time, the
  stage page and its assets, narration and captions, the player's files or
  their absence, the event stream, the watched reload and the refusal that
  keeps the last accepted film, and the clean stop.

### Modified Capabilities

None. `check`, `preview` and `render` keep every observable behaviour.

## Impact

Code: `src/check.mjs`, `src/film-assets.mjs`, `src/live.mjs` (new);
`bin/videomaker.mjs` (`check` calls `checkSource`; the `live` command; the
usage line); `src/render.mjs` (`browserSession` uses `filmAssets`;
`assetServer` takes a port; the common key hashes `film-assets.mjs`); tests
`test/live.test.mjs` (layer 3), `test/pipeline/live.test.mjs` (layer 8),
`test/repository.test.mjs` (layer 9), `test/support/reach.mjs` (what the
new modules and the new test read). No change to the movie document, its
schema, the stage, the Python side, the viewer or the framework. No new
dependency.

## Non-goals

The player page, its build and the take transport (the campaign's other
changes); re-evaluating a Python movie (`machinome_movie watch`, the third
change); composed joins or captions drawn live; any proof run on a real
film (finding 16 of `workflow/warts.md`); serving beyond the loopback
interface; speech: `live` buys none and generates no take. No publication,
push or paid request.
