## ADDED Requirements

### Requirement: `live` loads a film as `check` does and serves it at one loopback address

`videomaker live SOURCE [--viewer BUNDLE.js] [--width 960] [--port 0]
[--poll MS] [--open]` SHALL load the YAML episode or movie document as
`check` does and print exactly the lines `check` prints for it, in the same
order, then one line `Live: http://127.0.0.1:<port>/`, and SHALL answer at
that address on the loopback interface only until it is interrupted. A
source `check` refuses SHALL be refused with `check`'s message and exit
status, and nothing SHALL be served. `--port` SHALL fix the port (0, the
default, takes any free one) and a port in use SHALL be refused naming it;
`--width` SHALL set the width the stage page is drawn at and be refused as
`check` refuses it; `--viewer` SHALL default as the other commands' does.
On SIGINT the command SHALL end every event stream, release the port and
exit 0. `--open` SHALL run `xdg-open` on the address, and SHALL NOT fail
the command when it is missing or fails. `live` MUST NOT generate speech or
open a browser to draw; a movie with spoken anchors loads only with its
cached takes, as `check` does.

#### Scenario: The fixture counter is served

- **WHEN** `videomaker live <project>/videos/count/_build/movie.json
  --viewer <double>` is run on the fixture movie `count`
- **THEN** it prints the lines `check` prints for it (the summary, the
  take, the continuation, the viewer API, the Stage line, the trees and the
  export), then `Live: http://127.0.0.1:<port>/`, and answers there.

#### Scenario: A document check refuses

- **WHEN** `live` is run on a document that is not valid JSON
- **THEN** it exits 1 with the message `check` gives, and no address is
  printed.

#### Scenario: A fixed port and an interrupt

- **WHEN** `live` is run with `--port <n>` on a free port, then sent
  SIGINT
- **THEN** its address uses port `<n>`, it exits 0, and the port can be
  listened on again.

#### Scenario: Opening the address

- **WHEN** `live` is run with `--open` and the `xdg-open` it finds records
  its arguments, or exits with an error
- **THEN** `xdg-open` was given the address, and in both cases the command
  serves as without `--open`.

### Requirement: The outline of the film

`GET /film.json` SHALL answer the outline of the film the session serves:
its `id` and `title`; `output` with the `width` given by `--width`, the
`height` the renderer's rule gives for it, the film's `fps` and its
resolved `duration`; its chapters with `start` and `end`; its shots with
`chapter`, `start`, `end`, `set`, the incoming `join` as `{kind, duration}`
or `null`, and `model`, the shot's resolved model time as the resolved
document records it; its cues with `shot`, `id` (`cues[<i>]`), `at` and
`until` (null when the cue has none); its take, `take` for a clocked take
with its length and its marks in take seconds, or `loop` for a posed loop
with its period and its marks in model seconds, the marks sorted by time;
`speech` saying whether the mix and the captions exist; `stage.sha256`, the
hash of what the stage page boots from; `viewer.api`, the API the film
requires; `generation` with its `number` and `loadedAt`; and `refusal`,
`null` or the standing refusal's `{message, at}`. Times SHALL be seconds of
video time except under `takes`.

#### Scenario: The counter's outline

- **WHEN** `/film.json` is read from a session on the fixture `count` at
  `--width 640`
- **THEN** it gives `output` 640 × 360 at 10 fps for 11.4 s, one chapter
  `counting`, the shots `once`, `nine` and `carry` with `carry`'s 0.5 s
  dissolve and each shot's resolved `model` (`nine`'s with its `crossing`),
  `carry`'s cues in video time, the take `take` of 8 s with the marks `one`
  at 2, `nine` at 6 and `ten` at 8, `viewer.api` 29, generation 1 and no
  refusal.

#### Scenario: A loop's outline

- **WHEN** `/film.json` is read from a session on the fixture `tour`
- **THEN** its take is `loop`, 20 s long, with the marks `rise` 5, `top` 10
  and `fall` 15, and its joins include the reframe into `question` and the
  wipe into `push`.

### Requirement: The frame at a time is the renderer's frame

`GET /frame?t=<seconds>` SHALL answer, as JSON, `frameAt` of the film at
the output instant nearest `t` on the renderer's grid,
`round(t · fps) / fps`, clamped to the film's first and last frames, and
nothing else. A `t` that is missing, empty or not a finite number SHALL be
refused with status 400 naming `t`.

#### Scenario: A time between frames

- **WHEN** `/frame?t=6.04` is asked of the counter at 10 fps
- **THEN** the answer is `frameAt` of the film at 6.0 s.

#### Scenario: Times outside the film

- **WHEN** `/frame?t=-1` and `/frame?t=99` are asked
- **THEN** they answer the frames at 0 s and at the film's last frame.

#### Scenario: A time that is not a number

- **WHEN** `/frame`, `/frame?t=` or `/frame?t=soon` is asked
- **THEN** each is refused with status 400 naming `t`.

### Requirement: The stage page and its files are the renderer's

The session SHALL serve the renderer's stage page at `/film.html` and, at
the root as the renderer serves them, `/config.json` (the stage config the
renderer gives the film), `/stage.js` and `/stage.css` (the bundle `check`
reported), `/viewer.js` (the selected bundle), `/model/manifest.json` and
the files the viewer reads from the export, and the film's stills and clip
frames. It SHALL serve them through the same handler the renderer uses.

#### Scenario: The stage page of the counter

- **WHEN** `/film.html`, `/config.json`, `/stage.js`, `/viewer.js` and
  `/model/manifest.json` are read from a session on `count`
- **THEN** they are `src/film.html`, the film's stage config, the bundle
  whose hash the Stage line printed, the selected viewer and the export's
  manifest, byte for byte.

#### Scenario: A still of the tour

- **WHEN** `/pictures/stills/plate` is read from a session on `tour`
- **THEN** it is the project's `media/plate.png`.

### Requirement: Narration and captions are served when speech has written them

`GET /narration.wav` and `GET /captions.json` SHALL answer the mix and the
captions `speech` wrote under the film's `_build/`, and 404 when it has not
written them.

#### Scenario: Before and after speech

- **WHEN** a session on `count` is asked for both before `speech` has run,
  and again after `speech` has mixed the cached take
- **THEN** both are 404 first, then the files `speech` wrote, and the
  outline's `speech` says so.

### Requirement: The player's files are served when it is built

`GET /`, `/player.js` and `/player.css` SHALL answer
`_build/player/index.html`, `player.js` and `player.css` under the film's
build directory when each exists, and 404 `The player is not built` when it
does not.

#### Scenario: No player

- **WHEN** `/` is read and `_build/player/` does not exist
- **THEN** it answers 404 `The player is not built`.

#### Scenario: A built player

- **WHEN** `_build/player/index.html`, `player.js` and `player.css` exist
- **THEN** `/`, `/player.js` and `/player.css` answer them.

### Requirement: The session reports its generations and refusals as events

`GET /events` SHALL be a server-sent event stream of `loading` (a reload
started, `{at}`), `generation` (a load accepted:
`{number, loadedAt, stageSha256, exportChanged}`) and `refused` (a load
refused: `{message, at}`). A new subscriber SHALL receive the current
`generation` at once, and the standing refusal after it when there is one.

#### Scenario: A page subscribes

- **WHEN** `/events` is opened on a session that has accepted one load
- **THEN** its first event is `generation` with number 1 and
  `exportChanged` false.

### Requirement: A change to a film's inputs reloads it, and a refused change keeps the last accepted film

The session SHALL watch the film's inputs, the document (and an episode's
`production.yaml`), the project files the stage bundle read, the excerpt
sources, the stills and clips, the export's manifest, the cached takes and
the mix and captions, and SHALL settle the changes within 200 ms into one
reload, which loads the film as `check` does and prints `check`'s lines
again. An accepted reload SHALL replace the served film whole and emit
`generation` with the next number; a refused one SHALL print its message,
emit `refused`, set the outline's `refusal`, and keep the previous film
served, routes and frames included, until a later load is accepted. The
tool's own products under `_build/` (the resolved document, the stage
bundle, the player, the preview, the shot cache and extracted frames) MUST
NOT reload the film, and `_build/stage/`, `_build/player/`, `_build/preview/`
and captured frames MUST NOT be watched. The watched inputs SHALL be
recomputed from each accepted generation, so a file the stage bundle reads
for the first time is watched from the generation that read it on. With
`--poll <ms>` the inputs SHALL be compared by their file status every `ms`
milliseconds instead of watched.

#### Scenario: Saving the document

- **WHEN** the counter's document is written again
- **THEN** a `generation` event with number 2 follows, and the check lines
  are printed again.

#### Scenario: A broken document, then a repaired one

- **WHEN** the document is replaced by text that is not JSON, then
  restored
- **THEN** a `refused` event follows with `check`'s message, `/film.json`
  carries the refusal with generation still 2 and `/frame` still answers;
  after the restore a `generation` event with number 3 follows and the
  refusal is gone.

#### Scenario: A stage module imports a new file

- **WHEN** the stage module of a served movie is changed to import a second
  module, and that second module is then changed
- **THEN** the first change reloads the film, and the change to the second
  module reloads it again.

#### Scenario: The tool writes its own products

- **WHEN** files are written under `_build/stage/`, `_build/preview/` and
  as `_build/movie-resolved.json` of a served film
- **THEN** no reload starts.

#### Scenario: An episode's production settings

- **WHEN** the `production.yaml` of a served YAML episode is written
- **THEN** the episode reloads.

#### Scenario: Polling

- **WHEN** `live --poll 100` serves the fixture `tour` and its document is
  changed
- **THEN** the change is found by polling and a `generation` event follows.
