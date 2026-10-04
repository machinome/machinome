## ADDED Requirements

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
