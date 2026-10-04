## Context

The campaign's contract (`workflow/ongoing/player-campaign/plan.md`, "The
contract", "The live server, `src/live.mjs`") fixes this change's interface;
this design says how it is built and where it reads the contract more
narrowly. The rule above it is the plan's: the player is a transport over
the render's stage. A movie frame comes from `frameAt(film, t)` in the Node
process that loaded the film; the stage page is the renderer's, byte for
byte; a document the loader refuses is not shown, and the last accepted
film stays posed.

Today:

- `bin/videomaker.mjs` holds `check`'s body inline, interleaved with what
  every command shares: the early stage bundle and layout probe of a movie
  document (ADR-009, ADR-010), `loadEpisode`, the viewer default and the
  `--width` and `--fps` refusals, the summary line, `prepareWordTimingForCommand`,
  then `check`'s own lines and `readTrees(e, 'check')`.
- `src/render.mjs` has `stage(film, viewer, bundle)`, the map of URLs to
  files a film's page is served (the viewer, the export's manifest and the
  files the viewer reads from it, the stage bundle, the page at `/`, the
  stills and the extracted clip frames) with their hashes, which enter the
  shot cache's common key; `clipUses(film)`; and in `browserSession` an
  inline handler serving `/config.json` (`stageConfig(film)`), `/favicon.ico`
  and the map. `assetServer()` listens on port 0 of the loopback interface
  and mounts one handler at a time.
- The stage page (`src/film.html`) names its files from the root:
  `/stage.css`, `/viewer.js`, `/stage.js`; the runtime fetches
  `/config.json` once at boot and mounts viewers on `/model/manifest.json`;
  pictures are `/pictures/stills/<name>` and `/pictures/clips/<name>/<n>.png`.

## Goals / Non-Goals

**Goals:** a server a browser page and, later, the studio can rely on:
check's own load, the renderer's own page and frame function, one address
line, an event stream, a reload that never serves a refused film; and the
two extractions that let it share code with `check` and the renderer
without changing either.

**Non-Goals:** those of the proposal: the player page and its build, the
take transport, Python re-evaluation, anything drawn live that the
renderer composes.

## Decisions

### D1. `checkSource` is `check`'s body, moved, and the script's shared steps are named

`src/check.mjs` exports:

- `commandOptions(film, {viewer, width, fps})`: the viewer bundle (the
  given path, or `machinome-viewer.js` beside the export's manifest),
  `width` and `fps`, refusing them in today's words (`Width must be an even
  integer >= 320`, `FPS must be an integer from 1 to 120`); the script
  calls it for every command after `loadEpisode`, where it ran inline.
- `summaryLine(film)`: `<title>: <n> chapters, <n> shots, <d>s; model
  <d>s`, which every command prints.
- `checkSource(source, {viewer, width, fps, silent = false})`: the movie
  document's early bundle and layout probe, `loadEpisode`, `commandOptions`,
  the summary line, the take lines, the take line, the continuation lines,
  `prepareWordTimingForCommand` with `command: 'check'`, the reframes'
  boxes, the picture views, the viewer API line, the Stage line, the
  layout, reframe and text lines or `Text not measured`, the picture
  lines, and `readTrees(film, 'check')`, in that order, the code moved and
  not rewritten. It returns `{film, bundle, layouts}` (`layouts` null when
  nothing was measured) and never exits.

The script's `check` is `await checkSource(…); process.exit(0)`, its numbers
parsed as before (`Number(values.width)` when given). The pipeline tests
that pin `check`'s lines are the proof that nothing moved but the code.

The contract named it `checkFilm`, which is already the name of
`timeline.mjs`'s static checks of a loaded movie (`checkFilm(film)`, which
`loadMovie` imports dynamically). Two exports of one name in one repository
are a trap, so the contract's name yields to the existing one: the
orchestrator's ruling at ratification, 4 October 2026.

Rejected: `live` running `check` as a child process and parsing its output
(two processes per reload, and the film is then loaded twice).

### D2. `src/film-assets.mjs`: the files a film's page is served, and the handler that serves them

Moved from `src/render.mjs`, unchanged in behaviour:

- `filmFiles(film, viewer, bundle)` → `{paths, hashes}`: `stage()` renamed,
  the URL map and the hashes the shot cache keys on, `/` the page as
  before (the key hashes by URL, so the name stays).
- `clipUses(film)`: the clip spans a film shows, for `extractClips`.
- `filmAssets({paths, config, onError})`: the `(req, res)` handler, serving
  `/config.json` as `config`, `/favicon.ico` as 204 and every path of the
  map with its content type, 404 `Not found` otherwise and 500 `Asset error`
  on a failure, which it reports through `onError` (the session's error
  list in the renderer, as `errors.push` was). `onError` is an addition to
  the contract's signature, optional.

`browserSession` calls `extractClips(film, clipUses(film))`,
`buildFilmStage`, `filmFiles` and mounts `filmAssets` as it did the inline
handler. `film-assets.mjs` locates `src/film.html` and is declared in
`test/support/reach.mjs` as reading it.

The shot cache's common key hashes `src/render.mjs`, which this change
edits: every film's key changes once and every film recaptures once, as
every edit of the renderer does (ADR-015's consequence, the precedent of
`serve-what-the-viewer-reads`). The moved code was inside that hash; the
key gains `assets`, the hash of `src/film-assets.mjs`, so a later edit of
the content types or the map still recaptures. What the map decides
already reaches the key as the served files' hashes.

### D3. A generation is one accepted load

`live` loads a generation in these steps, each the code the commands use:

1. `checkSource(source, {viewer, width})`, which prints `check`'s lines;
2. `extractClips(film, clipUses(film))`, so a clip picture's frames can be
   served (FFmpeg, cached by content under `_build/clips/`; `check` itself
   extracts nothing);
3. `filmFiles(film, viewer, bundle)` with `/` moved to `/film.html`, since
   `/` is the player's;
4. `stageConfig(film)`.

The generation is `{number, loadedAt, film, bundle, config, paths,
stageSha256, exportSha256}` and, beside the contract's fields,
`exportChanged` (for its event) and the watched inputs (D7). Numbers start
at 1 and count accepted loads; `loadedAt` is an ISO time, session
metadata, never in a frame.

- `stageSha256` is the SHA-256 of what the stage page boots from: the
  page's hash, the bundle's script and stylesheet hashes, and the hash of
  the config as served. The contract calls it the stage hash; the player
  keeps its iframe while it is unchanged, and the script's hash alone
  (the `Stage:` line's first) would miss a stylesheet change, which leaves
  the script's bytes as they were, and a document change that changes the
  config (a set's props, the style, a picture's size), which the page
  reads only at boot.
- `exportSha256` is the SHA-256 of the served viewer bundle and every
  served `/model/` file: what a viewer mounted on the export loads.
  `exportChanged` is whether it differs from the previous generation's
  (false for the first).

The first load runs before the server starts; if it throws, `live` throws
the same error and nothing is served, so the command fails as `check`
would, with `check`'s message. A later load that throws is a refusal:
`{message, at}` is set on the session, printed to stderr, and the previous
generation stays served; the next accepted load clears it. A generation is
replaced only once it is whole, by one assignment, and each request reads
the current generation once.

### D4. One server for the session

`assetServer({port})` gains an optional port (default 0, as before) and
`live` mounts one handler for the session's life; a port in use is refused
naming it (`Port <n> is in use on 127.0.0.1; choose another with --port,
or 0 for any free port`). It listens on 127.0.0.1 only. Every response
carries `Cache-Control: no-store`, so a page reloaded after a new
generation never reads a stale `stage.js`. Only GET and HEAD are answered
(405 otherwise). Routes:

- `/film.json`: the outline (D5), with `refusal` the session's.
- `/frame?t=`: D5; 400 naming `t` when it is missing, empty or not a
  finite number.
- `/take.json` (D11): the take document of a film on a clocked take, 404
  `No take document` otherwise.
- `/narration.wav`, `/captions.json`: the files `speech` wrote under the
  film's `_build/`, read when asked, 404 `Not found` when absent.
- `/events`: D6.
- `/`, `/player.js`, `/player.css`: `_build/player/index.html`,
  `player.js`, `player.css` when each exists, else 404 `The player is not
  built`. The `player-page` change writes them.
- everything else through the generation's `filmAssets`: `/film.html`,
  `/config.json`, `/stage.js`, `/stage.css`, `/viewer.js`, `/model/…`, the
  pictures.

### D5. The outline and the frame are pure functions of the generation

`src/live.mjs` exports them for the layer 3 tests:

- `frameFor(film, t)`: refuses a `t` that is not a finite number
  (`RangeError` naming `t`), then returns `frameAt(film, i / fps)` with
  `i = round(t · fps)` clamped to `[0, count − 1]`, `count =
  round(duration · fps)`: the renderer's grid (`outputShotUnits`), so the
  last instant is the film's last frame and nothing past it is asked of
  `frameAt`.
- `outline(film, {width, number, loadedAt, stageSha256, speech, refusal})`:

      {id, title,
       output: {width, height, fps, duration},
       chapters: [{id, start, end}],
       shots: [{id, chapter, start, end, set, join: {kind, duration} | null, model}],
       cues: [{shot, id, at, until}],
       takes: {<name>: {kind, duration, marks: [{name, time}]}},
       speech: {mix, captions}, stage: {sha256}, viewer: {api},
       generation: {number, loadedAt}, refusal: {message, at} | null}

  - `output.width` is the session's `--width` and `output.height` the
    renderer's rule for it (`round(height · width / output width / 2) · 2`),
    `fps` the film's, `duration` its resolved length: the geometry the stage
    page is drawn at in this session, as `render --width` captures it. The
    contract places the iframe at "`output.width × output.height` at the
    server's `--width`", and the outline is the only place the player reads
    that width.
  - `join` is the shot's incoming join (`transition`), `null` for none; a
    fade-in or fade-out is not a join. `model` is the shot's resolved
    `model`, as the resolved document records it (with `crossing` when it
    has one).
  - A cue's `id` is `cues[<i>]`, its index in its shot as refusals name it;
    `at` and `until` are video time (`until` null for a cue without one).
  - `takes`: the document records no take name. A clocked take is `take`,
    `{kind: 'clocked', duration: <its length in take seconds>, marks, url:
    '/take.json'}`, the `url` where its take document is served (D11); a
    posed loop is `loop`, `{kind: 'loop', duration: <the loop's period in
    model seconds>, marks}`, its marks the document's in model seconds
    (the take seconds of a loop, as the movie document defines `marks`).
    Marks are sorted by time, as `check`'s take line lists them. The take
    transport's loop is normalized to [0, 1]; the player divides.
  - `speech` says whether `_build/narration.wav` and `_build/captions.json`
    exist when asked; `viewer.api` is the API the film requires.

### D6. Events

`/events` answers `text/event-stream`. Each message is `event: <kind>` and
one `data:` line of JSON:

- `loading` `{at}`, when a reload starts;
- `generation` `{number, loadedAt, stageSha256, exportChanged}`, when a
  load is accepted;
- `refused` `{message, at}`, when one is refused.

A new subscriber receives the current `generation` at once and, while a
refusal stands, the `refused` after it, so a page opened during a refusal
knows it (the contract's at-once event, with the refusal added). A
comment line (`: keep-alive`) is sent every 15 s. `close()` ends every
stream.

### D7. The watcher: the inputs' directories, without recursion

A generation's inputs are, as absolute paths:

- the document, and for an episode its `production.yaml`;
- every project file the stage bundle read: the `project/<path>` names of
  `_build/stage/inputs.json` (the stage modules, what they import, their
  stylesheets);
- each excerpt's source file, each still's and each clip's file;
- the export's `manifest.json`;
- `_build/narration.wav` and `_build/captions.json`, and the directory
  `_build/audio/` (any entry in it).

Each input's directory is watched with `fs.watch`, not recursively; an
event reloads only when it names an input, an entry of `_build/audio/`, or
(for an input that does not exist yet) a directory on the way to it, whose
nearest existing ancestor is what is watched. An event that does not name
its file reloads, to be safe. The tool's own products are therefore never
inputs: `_build/movie-resolved.json` (which every load writes),
`_build/stage/`, `_build/player/`, `_build/preview/`, `_build/clips/`, the
shot cache and the frames; and `_build/stage/`, `_build/player/`,
`_build/preview/` and the frames are never watched at all.

The contract asks for `recursive: true` over the inputs' directories. Those
directories include `_build/` (a Python movie's document, the mix, the
captions) and a YAML episode's directory, which holds `_build/`, so a
recursive watch would watch exactly what the contract says is never
watched; the bundle's record names a module's imports, so no input needs
recursion to be seen. Rejected: recursive watches with the same filter
(the tool's outputs are then watched, a render's frames flood the
watcher, and a large project tree costs a watch per directory).

The first event arms a 200 ms timer; events before it fires join the same
reload. One reload runs at a time; an event during a reload schedules one
more after it.

The watched set is recomputed after every accepted generation, from that
generation's film and its `_build/stage/inputs.json`, and the watches (or
the poll's list) are replaced by it: a stage module that starts importing a
new file is watched from the next generation on, and a file no module
imports any more stops being watched (the orchestrator's requirement at
ratification). A refused load keeps the previous set, so a file a refused
document names for the first time is watched only once a load accepts it
(touching the document reloads it).

`--poll <ms>` replaces the watches with a stat poll every `ms`
milliseconds of the same inputs (size, modification time and inode of
each file; the entries of `_build/audio/`); a difference from the last poll
is an event. For a filesystem whose events do not arrive (virtiofs shows
the guest's writes and not the host's).

### D8. The command

`videomaker live SOURCE [--viewer BUNDLE.js] [--width 960] [--port 0]
[--poll MS] [--open]`:

- `--width` is refused as `check` refuses it; `--port` must be an integer
  from 0 to 65535 (`--port must be an integer from 0 to 65535`) and
  `--poll` a whole number of milliseconds (`--poll must be a whole number
  of milliseconds (0 watches instead of polling)`), each refused before
  any load. Implementation note: `--poll 0`, the default, watches, where
  this design first said a poll starts at 1, because `live(…, {poll: 0})`
  is the module's own default and the two should agree. `--fps` and
  `--silent` are refused
  for `live`, and `--port`, `--poll` and `--open` for the other commands
  (they were unknown options before, and refused as such).
- It prints `check`'s lines (`live` calls `checkSource`), then
  `Live: http://127.0.0.1:<port>/`, and nothing else on success; a later
  load prints `check`'s lines again, a refusal its message on stderr.
- On SIGINT (and SIGTERM) it calls `close()` and exits 0.
- `--open` spawns `xdg-open <address>` detached, ignoring its output, its
  exit status and a missing `xdg-open`: best effort, never a failure.

The usage line gains the `live` form.

### D9. `close()`

Stops the watches or the poll, clears the settle timer, waits for a
reload in flight to finish, ends every event stream and closes the server;
the port is free when it resolves.

### D10. ADR-021 and the records

ADR-021 (PIPELINE, Proposed): *A live session serves the render's stage
and the frame function to a browser*: one process per film on the
loopback interface; a generation is `check`'s load, accepted whole or
refused; the stage page and its files are the renderer's, served by the
renderer's handler; frames come from `frameAt` in Node on the render's
grid; events, not polling, tell the page; the watcher reloads on the
film's inputs and never on the tool's outputs. Not promoted in this cycle:
the campaign stops before sync and archive.

`README.md` documents the command, each option, the address line and the
routes; `docs/architecture-overview.md` gains the live branch and the
three modules; `CHANGELOG.md` one bullet; `AGENTS.md`'s status line lists
`live` and says the player page is not built.

### D11. `/take.json`: the take document the take transport attaches to

Added after the planning commit, on the orchestrator's message of
4 October 2026, from a finding of the `take-transport` cycle: the outline
gives a clocked take's marks and length, but the player's take surface
attaches the transport to the take document itself (`attachTake(viewer,
take)`, whose pose rule is `bankAt` of `src/take.mjs`), and no route served
it.

`GET /take.json` answers, for a film on a clocked take, the JSON object
`{model: {expectedDurationSeconds}, marks, take}`, each taken verbatim from
the generation's resolved film: the take's length, the top-level marks in
take seconds, and the take block as the document records it. That is
exactly what `bankAt` reads. For a posed loop or a YAML episode it answers
404 `No take document`. The outline's `takes.take` names it
(`url: '/take.json'`), so the player finds it without guessing; the loop
entry has no `url`.

## Risks / Trade-offs

- [A movie with a picture or a reframe opens Chromium at every reload, to
  measure its layout as `check` does] → the reload of such a film costs
  seconds, not milliseconds; measured and recorded in `evidence.md` on the
  fixture `tour`. A layout cache is not this change.
- [`/narration.wav` is the mix `speech` last wrote, which may be older than
  the document] → served as it is, as `render` would read it after
  `speech`; the player shows what exists. The mix's change reloads.
- [The live session and a `preview` or `render` of the same film share
  `_build/` (finding 16 of `workflow/warts.md`)] → each load rewrites
  `movie-resolved.json` and may rebuild `_build/stage/`, as `check` does;
  the README says so.
- [An event between a load's reading of a file and the re-armed watch is
  missed] → the window is the load's own duration for a file the previous
  generation did not watch; the next change to any input catches up.
- [`loadedAt` and `at` read a clock] → session records only; no frame, no
  hash and no proof reads them.
- [Editing `src/render.mjs` recaptures every film once] → stated in the
  changelog bullet.
