# live-preview Specification

## Purpose
TBD - created by archiving change live-server. Update Purpose after archive.
## Requirements
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
with its length, its marks in take seconds and the `url` of its take
document, or `loop` for a posed loop
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

### Requirement: The take document of a film on a clocked take

`GET /take.json` SHALL answer, for a film on a clocked take, the JSON
object `{model: {expectedDurationSeconds}, marks, take}`, each taken
verbatim from the served film: the take's length in take seconds, the
document's marks in take seconds, and its take block as the document
records it, which is what the pose rule reads. The outline's `takes.take`
SHALL name it with `url` `/take.json`. For a posed loop or a YAML episode
it SHALL answer 404 `No take document`.

#### Scenario: The counter's take

- **WHEN** `/take.json` is read from a session on the fixture `count`
- **THEN** it is the length 8, the marks `one`, `nine` and `ten` and the
  take block of the served film, byte for byte as JSON, and the outline's
  `takes.take.url` is `/take.json`.

#### Scenario: A loop has no take document

- **WHEN** `/take.json` is read from a session on the fixture `tour`
- **THEN** it answers 404 `No take document`.

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

### Requirement: `live` builds the player and serves it

`live` SHALL build the player page once per session, after the film's
first load is accepted and before it serves, into `_build/player/` under
the film's build directory, and SHALL serve it at `/`, `/player.js` and
`/player.css`; it SHALL print nothing beyond `check`'s lines and the
address line for it. The build SHALL be reused while the content of what
it reads (the player's sources, the take transport's and the pose rule) is
unchanged and its files still hash as recorded, and SHALL name every file
it embeds by the tool, so the same tool content builds the same bytes from
any checkout into any build directory. No generation SHALL rebuild it.

#### Scenario: The counter's session serves its player

- **WHEN** `live` serves the fixture movie `count`
- **THEN** `/`, `/player.js` and `/player.css` answer the built page,
  script and stylesheet, and the page loads `/player.js` and
  `/player.css`.

#### Scenario: A second session reuses the player

- **WHEN** a second session is started on the same film
- **THEN** it reuses the player built by the first, byte for byte.

#### Scenario: The same bytes from anywhere

- **WHEN** the player is built into two build directories at different
  places
- **THEN** the two scripts and stylesheets are identical and name the
  player's files `videomaker/player/<file>`, the transport's
  `videomaker/transport/<file>` and the pose rule `videomaker/src/take.mjs`.

### Requirement: The outline gives each mark in video time

`/film.json` SHALL give `marks`, a list of `{name, shot, at}`: for each
shot and each mark of the document, the first output frame of the shot, on
the renderer's grid, at which the shot's model time reaches the mark (the
shot's first frame when it starts at the mark, or the first frame past it
when the shot crosses it), in video seconds, ordered by time. A mark no
frame reaches SHALL NOT be listed.

#### Scenario: The counter's marks

- **WHEN** `/film.json` is read from a session on `count`
- **THEN** its `marks` are `one` at 3.2 in shot `nine` and `nine` at 5.3 in
  shot `carry`, and `ten`, which no frame of the film reaches, is not
  listed.

### Requirement: The mix is served with its length and by byte ranges

`/narration.wav`, `/captions.json` and the player's files SHALL be answered
with their length and `Accept-Ranges: bytes`, and a request for a single
byte range of one SHALL be answered 206 with that range and its
`Content-Range`, or 416 naming the file's length when the range starts past
its end, so an audio element knows the mix's length and seeks it.

#### Scenario: A range of the mix

- **WHEN** `speech` has mixed the counter's narration and `/narration.wav`
  is asked for `bytes=100-199`, `bytes=-10` and a range past its end
- **THEN** the answers are 206 with those hundred bytes, 206 with the last
  ten, and 416 with `bytes */<length>`, and a request without a range has
  the file's length.

### Requirement: The player shows a film or a take, by the address

The player SHALL show the movie surface at `#movie` and the take surface at
`#take/<key>` for each take the outline lists (`take` for a clocked take,
`loop` for a posed loop); with no hash, or one that names no surface, it
SHALL show the movie surface and say so in the address. A control SHALL
switch between the surfaces.

#### Scenario: The default surface

- **WHEN** the player of a session on `count` is opened without a hash
- **THEN** it shows the movie surface and its address ends `#movie`.

#### Scenario: Switching to the take

- **WHEN** the take's link is followed on the player of `count`
- **THEN** the address ends `#take/take`, the stage page is gone, and the
  viewer is mounted on the export.

### Requirement: The movie surface poses the renderer's frames on the render's stage page

The movie surface SHALL show the render's stage page, `/film.html`, in a
frame of exactly the outline's output width and height, scaled down to fit
the window and never up, and SHALL draw nothing inside it. For a time, it
SHALL fetch the frame `/frame` gives for it and pose it through the stage
page's `window.film.setFrame`, once `window.film` or `window.filmError`
appears, as the renderer poses it; it SHALL show a `filmError` rather than
pose. Its clock SHALL be the narration's mix when `speech.mix` says one
exists, and a timer of the film's duration otherwise; when the mix's length
differs from the film's by more than a frame, it SHALL say so. Times SHALL
snap to the film's frames. One pose SHALL be in flight at a time and the
latest time requested SHALL be the next posed; a frame the stage cannot
reach before the clock moves on SHALL be dropped, and the clock SHALL NOT
wait for a pose.

#### Scenario: The frame the renderer would capture

- **WHEN** the movie surface of `count` at `--width 640` is sought to 6 s
- **THEN** its frame is 640 × 360, the frame `/frame?t=6` gives is posed,
  and what the stage reports of it (the view's box, camera and bank among
  it) equals what the renderer's stage reports for the same frame.

#### Scenario: One time, another, and the first again

- **WHEN** the movie surface is sought to 2.5 s, 8 s and 2.5 s again
- **THEN** the first and third show identical pixels, which differ from
  the second's.

#### Scenario: The narration as the clock

- **WHEN** `speech` has mixed the counter's narration and the session has
  reloaded
- **THEN** the movie surface's clock is an audio element on
  `/narration.wav`, and seeking the player seeks it.

#### Scenario: The latest time wins

- **WHEN** three times are requested while one pose runs
- **THEN** only the last of them is posed after it, and nothing waits for
  the poses to finish.

### Requirement: A composed join is shown as a cut, and the player says so

Inside a dissolve, wipe, slide or fade between shots, the movie surface
SHALL pose the outgoing shot's frame before the join's midpoint and the
incoming shot's from it on, SHALL hatch the join's span on its ruler, and
its readout SHALL name the join and say it is shown as a cut. A reframe
SHALL be posed as the frame gives it, drawn live by the stage. A shot's
fade in or fade out SHALL be posed without its colour, and the readout
SHALL say it is shown without its fade.

#### Scenario: A dissolve on the tour

- **WHEN** the movie surface of `tour` is sought a frame before and a frame
  after the midpoint of the dissolve into `source`
- **THEN** the first poses `holds`'s frame and the second `source`'s, and
  the readout says `dissolve into source, 0.6 s: shown as a cut at its
  midpoint`.

#### Scenario: A reframe on the tour

- **WHEN** it is sought inside the reframe into `question`
- **THEN** the frame is posed with its reframe's progress and boxes, and
  the readout says the reframe is drawn live.

#### Scenario: A fade in on the tour

- **WHEN** it is sought to the first frame of `hook`, which fades in
- **THEN** `hook`'s frame is posed, and the readout says it is shown
  without its fade.

### Requirement: The take surface poses a take on the viewer alone

The take surface SHALL mount the viewer on the export (`/viewer.js`,
`/model/manifest.json`), rendering continuously, its camera its own
navigator's, with no stage loaded; SHALL attach the take transport to the
take document `/take.json` for a clocked take, or to the loop for a posed
loop; and SHALL drive it by a timer of the take's length (a loop's period
in seconds, the loop sought at the time over the period). Times SHALL snap
to the film's frames, the take's end included, and a mark SHALL be a stop:
seeking to a mark poses its own time.

#### Scenario: Every mark of the counter on the double

- **WHEN** the take surface of `count` is shown and each mark on its ruler
  is clicked
- **THEN** the viewer's machine holds, after each, exactly the bank the
  take records at that mark.

#### Scenario: Every mark of the counter on the real viewer

- **WHEN** the viewer layer runs with a Viewer API 29 bundle and the take
  surface of `count` is shown over the counter's export
- **THEN** after each mark is clicked the bank the viewer's machine holds
  equals the recorded one.

#### Scenario: The tour's loop

- **WHEN** the take surface of `tour` (`#take/loop`) is sought to 5 s
- **THEN** the loop is posed at 0.25 of its 20 s period, and the mark
  `rise` is at the playhead.

### Requirement: The ruler scrubs, and the keys and the clicks move the playhead

The player SHALL draw a ruler: on the movie surface the chapters as bands,
the shots as segments, each join hatched over its span, the cues as ticks
and the marks as flags; on the take surface the take's marks; and the
playhead at the time. The ruler SHALL be a scrubber: a pointer pressed on
it, anywhere but a shot's name or a mark's flag, SHALL pause the clock and
seek to the time under the pointer, and while the pointer is held and
moves the player SHALL keep seeking to the time under it, one pose in
flight and the latest time winning, frames the stage cannot reach dropped,
as during play; releasing the pointer SHALL leave the playhead at the last
time sought. A click on a shot's name SHALL seek to the shot's start, and
on a mark's flag to the mark. Space SHALL play and pause; left and right
SHALL move one frame; with shift, one second; home and end SHALL go to the
first and the last frame.

#### Scenario: The counter's ruler

- **WHEN** the movie surface of `count` is shown
- **THEN** its ruler has one band, `counting`; the segments `once`, `nine`
  and `carry`; `carry`'s dissolve hatched from 5.3 s to 5.8 s; three ticks
  in `carry`; and the flags `one` and `nine`.

#### Scenario: The keys

- **WHEN** home, right, shift and right, left and end are pressed in turn
  on the movie surface of `count`
- **THEN** the playhead stands at frames 0, 1, 11, 10 and 113.

#### Scenario: The clicks

- **WHEN** the name of the shot `nine` and then the flag `nine` are clicked
- **THEN** the playhead stands at 3.2 s, then at 5.3 s.

#### Scenario: A drag across a shot boundary

- **WHEN** a pointer is pressed on the ruler of `count` inside `once`,
  moved across the boundary into `nine` and released there
- **THEN** frames of both shots were posed during the drag, the clock is
  paused, and the playhead and the last frame posed are at the frame under
  the released pointer, in `nine`.

### Requirement: The readout says where the playhead is

Under the frame, never in it, the player SHALL show the time, the frame
index, the shot and the chapter (movie surface), the mark at the playhead
when there is one, the join when the time is inside one, and, when
`speech.captions` says the captions exist, the text of the caption that
holds the time.

#### Scenario: At the mark one

- **WHEN** the movie surface of `count` stands at 3.2 s
- **THEN** the readout says 3.20 s, frame 32, shot `nine`, chapter
  `counting` and mark `one`.

#### Scenario: A caption

- **WHEN** the session's `_build/captions.json` holds a caption from 1 s to
  2.5 s and the movie surface stands at 2 s
- **THEN** the readout shows that caption's text.

### Requirement: The player follows the session's generations and refusals

The player SHALL follow `/events`. On a `generation` whose stage hash is the
one it shows and whose export did not change, the movie surface SHALL keep
its frame and the viewers in it, fetch the outline again and pose the
current time again; otherwise it SHALL reload the stage page and pose the
current time on it. The take surface SHALL mount the viewer again only when
the export changed, and otherwise attach the transport again to the new
take document and seek the current time again. A refusal, in the outline or
a `refused` event, SHALL be shown until the next `generation`, the film
shown staying as it was.

#### Scenario: The same stage page

- **WHEN** the counter's document is written again unchanged
- **THEN** the movie surface keeps its frame and its viewer instance, and
  poses the current time again.

#### Scenario: A changed stage module

- **WHEN** a stage module of the served movie changes what it draws
- **THEN** the movie surface reloads the stage page and poses the current
  time on it.

#### Scenario: A refusal shown and cleared

- **WHEN** the document is broken, then restored
- **THEN** the player shows `check`'s message, keeping the film it shows,
  and clears it when the restored document is accepted.

#### Scenario: The take surface on a new generation

- **WHEN** the counter's document is written again while its take surface
  is shown
- **THEN** the viewer stays mounted, the transport is attached again and
  the current time is sought again.

### Requirement: The player reports its state, provisionally

The player SHALL report its state on `window.player`, for the proofs and
for a page that frames it: the surface shown, the time posed and its
frame, whether it plays, the generation shown, the frames posed, the last
report of the stage page (movie surface) and the take transport (take
surface), with `seek`, `play`, `pause` and a promise that resolves when
no pose runs or waits. These names are provisional: they are not a
protocol, and may change before a release.

#### Scenario: The proofs read the page

- **WHEN** a proof seeks the player of `count` to 6 s and waits for it to
  settle
- **THEN** `window.player` reports the movie surface, 6 s, frame 60, the
  generation shown and the stage page's report of the frame posed.

