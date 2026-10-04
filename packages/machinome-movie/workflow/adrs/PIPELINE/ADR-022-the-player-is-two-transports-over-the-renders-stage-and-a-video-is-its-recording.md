# ADR-022: The player is two transports over the render's stage, and a video is its recording

Status: Accepted (OpenSpec change `player-page`, 4 October 2026, the third
and last change of the player campaign, archived the same day, after the pilot validated the player in the browser). Builds on
[ADR-020](../STAGE/ADR-020-a-take-transport-is-the-browsers-pose-of-a-take-written-to-lift.md)
(the take transport) and
[ADR-021](ADR-021-a-live-session-serves-the-renders-stage-and-the-frame-function-to-a-browser.md)
(the live session).

## Context

A film was seen only once it was produced: every timing revision of
*Revolutions* meant a preview run and a look at the contact sheet, the
Curta's *Addition* renders in 63 minutes, and its take was written blind,
because nothing showed a take before a movie rendered
(`workflow/ongoing/roadmap.md` item 13, *Live preview*). The pilot's rulings
of 4 October 2026: the piece lives in Videomaker before the studio takes it,
and watching a scenario is a feature by itself, of which a video is a
recording. The campaign's first two changes built the pose of a take in a
browser (ADR-020) and a session that serves the render's stage page, the
frame function and a take's document (ADR-021). What remained was the page a
person watches, and a way for a Python movie's document to follow its
declarations.

What the page shows has to be what the renderer would capture, or it
teaches the author something the film will not do; and what the page cannot
show, it has to say.

## Decision

1. **Two surfaces, two transports, nothing drawn of the film.** The player
   is a page of plain DOM over the session, chosen by its address. The
   movie surface (`#movie`) is a movie transport: the render's own stage
   page in a frame of exactly the session's output geometry, scaled down to
   fit and never up, each frame fetched from the session's frame function
   and posed through the stage's `window.film.setFrame` as the renderer
   poses it, the narration's mix as its clock when there is one. The take
   surface (`#take/<key>`) is the take transport alone: the viewer mounted
   on the export with its own camera, the take attached by the pose rule the
   frame uses, a mark a stop. The page draws a ruler, keys, a scrubber and a
   readout around the frame and nothing inside it.
2. **A video is the movie transport's recording.** `render` captures the
   same stage page posed by the same frames; the player shows them live.
   Where the renderer composes a picture from captures, the player does not
   imitate it: a dissolve, fade, wipe or slide is shown as a cut at its
   midpoint, a shot's fade in or out without its colour, and the readout
   says so; a reframe, which the stage draws live, is shown as it is drawn.
3. **One pose in flight; the clock never waits.** A play, a seek, a key or a
   drag asks for the frame of a time; a frame the stage cannot reach before
   the clock moves on is dropped, and the narration plays at its pace.
4. **The page follows the session's generations.** The stage page and its
   viewers are kept while what the stage page boots from and the export are
   unchanged, and reloaded otherwise; the take surface's viewer is mounted
   again only when the export changed; a refusal is shown and the film shown
   stays the last one accepted.
5. **The player is tool content.** `live` builds it once per session with
   the stage build's esbuild, its files named by the tool so its bytes never
   depend on where the tool lies, reused while what it reads is unchanged;
   it imports only its own files and the take transport, which a repository
   test holds.
6. **Each side re-evaluates its own.** A Python movie's document is
   evaluated again by `python -m machinome_movie watch`, beside `live`, in a
   fresh process at each change of the project's files; the Node tool never
   selects a Python interpreter, and `live` reloads when the document is
   written.

## Options considered

- **Compute frames in the browser.** A second frame function, which the
  renderer's proofs would not cover (rejected by ADR-021 for the server; the
  page inherits it).
- **Draw the composed joins live** with an overlay or a canvas blend. A
  second composition the renderer's tolerances do not prove; an open line of
  the plan, a stage change, not proposed.
- **A React page.** The stage is React, but the player owns no element of
  the film and its parts are a few DOM rows; plain DOM keeps it outside the
  stage's bundle and its key, and liftable with the transport.
- **The take on the stage** (a set holding one view). It would load a set,
  a slot and React to show a machine, and could not move with the transport
  to the view layer at the migration.
- **`live` re-evaluating Python itself.** One process would then choose an
  interpreter and an environment for a project; the watcher keeps each side
  in its own.

## Consequences

- A person edits, sees `check`'s lines or its refusal, and scrubs the film
  at the renderer's frames within seconds; the Curta's take can be watched
  before a movie is written. What the episode measures (the time from an
  edit to a frame, the Curta's pace on a GPU) is the pilot's, in a browser.
- A composed join or a shot's fade does not look in the player as it does in
  the film, and the readout says so each time; fading marks and pictures are
  shown at the stage's own opacity, the same to the eye, not the same pixels.
- `window.player` carries the page's state for the proofs and a page that
  frames it; its names are provisional, not a protocol.
- The outline gives the marks in video time, at the frames a shot's model
  time reaches them; a mark no frame reaches is not flagged on the movie
  ruler, and is on the take's.
- The take surface's viewer renders continuously while it is shown, for its
  navigator; the viewer's handle declares no release, so a remount leaves the
  previous instance to the page's garbage collection.
