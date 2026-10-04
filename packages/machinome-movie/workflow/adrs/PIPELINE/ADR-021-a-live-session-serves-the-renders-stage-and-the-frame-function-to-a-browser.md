# ADR-021: A live session serves the render's stage and the frame function to a browser

Status: Proposed (OpenSpec change `live-server`, 4 October 2026; the player
campaign stops before sync, so the change is not archived and this ADR is
not yet promoted).

## Context

A film is seen only after it is produced: `preview` poses stills and a
contact sheet, `render` captures every frame. Every timing revision of
*Revolutions* meant a preview run and a look at the contact sheet;
*Addition*, the Curta film, renders in 63 minutes, and its take was written
blind, because nothing could show a take before the movie rendered
(`workflow/ongoing/roadmap.md` item 13, *Live preview*). The pilot's
rulings of 4 October 2026 put the piece that shows a film while it is
edited in Videomaker, for the studio to use later, as two transports over
the render's own stage (`workflow/ongoing/player-campaign/plan.md`): a
take transport that poses a machine at a take time, and a movie transport
that poses the stage at a video time.

What the browser is shown has to be what the renderer would capture, or
the session teaches the author something the film will not do. The
renderer's guarantees rest on one frame function (`frameAt`, pure in video
time), one stage bundle, one stage page and one load that `check` makes and
refuses by name. A second implementation of any of them in a browser page
would drift.

## Decision

1. **One process per film, on the loopback interface.**
   `videomaker live SOURCE` loads the film, prints `check`'s lines and one
   address line, `Live: http://127.0.0.1:<port>/`, and serves until it is
   interrupted. It buys no speech and opens no browser to draw; a person's
   browser, or later the studio's panel, is the browser.
2. **A generation is `check`'s load, accepted whole or refused.** The
   session loads through `checkSource`, the body of `check` moved into
   `src/check.mjs`, and keeps the result with the stage bundle, the stage
   config and the page's files as a numbered generation. The first load
   must succeed, or the command fails as `check` would. A later load that
   fails is a refusal: it is printed and announced, and the previous
   generation stays served, routes and frames included, until a load is
   accepted.
3. **The stage page and its files are the renderer's, served by the
   renderer's handler.** The handler and the map of a film's page files
   move from `src/render.mjs` into `src/film-assets.mjs`, used by both;
   the live session serves the page at `/film.html` and its files at the
   root, where the page names them.
4. **Frames come from `frameAt` in Node, on the render's grid.**
   `/frame?t=` answers the frame at the output instant nearest `t`, clamped
   to the film; the browser computes no movie frame. `/film.json` is the
   film's outline at the session's width, and `/take.json` a clocked take's
   document, which the browser's take transport poses through the same pose
   rule (`src/take.mjs`).
5. **Events, not polling, tell the page.** `/events` streams `loading`,
   `generation` (with the hash of what the stage page boots from and
   whether the export changed) and `refused`; a new subscriber hears the
   current generation at once.
6. **The film's inputs reload it; the tool's outputs never do.** The
   document, an episode's production settings, the project files the stage
   bundle read, the excerpt sources, the stills and clips, the export's
   manifest, the cached takes and the mix are watched, each in its own
   directory and without recursion, the set recomputed from every accepted
   generation; changes within 200 ms are one reload. `--poll` compares
   their file status instead, for a filesystem whose change events do not
   arrive.

## Options considered

- **Compute frames in the browser** from the resolved document. Two
  implementations of the frame function, and the page would need the
  excerpts, the takes and the measured layout the load attaches; the
  renderer's proofs would not cover what the page shows.
- **Run `check` as a child process per reload and parse its output.** The
  film would be loaded twice per change and its result would not be kept.
- **Pre-render stills on each change.** As slow as `preview`, which is what
  the episode wants to avoid.
- **A WebSocket.** Two-way, which nothing here needs; server-sent events
  are one direction, need no dependency and every browser reads them.
- **Watch the inputs' directories recursively.** They include `_build/` and
  a directory that holds it, so a recursive watch would watch the tool's
  own outputs and a render's frames; the bundle's record names a module's
  imports, so no input needs recursion to be seen.

## Consequences

- A person sees `check`'s lines again within a fraction of a second of a
  save, and the refusal when there is one, without losing the last good
  film; what they scrub is what `render` would capture, short of what the
  renderer composes from captures (joins, fading marks), which the player
  page, the campaign's next change, is to say it shows otherwise.
- A movie with a picture or a reframe opens headless Chromium at every
  reload, to measure its layout as `check` does: about 1.3 s per reload on
  the fixture `tour`, against about 0.1 s for the fixture `count`.
- The session rewrites `movie-resolved.json` and may rebuild
  `_build/stage/` at each load, as `check` does; a render of the same film
  from another process shares that directory (finding 16 of
  `workflow/warts.md`).
- Editing `src/render.mjs` moved the shot cache's common key once, so every
  film recaptures once; the key also hashes `src/film-assets.mjs`, so the
  moved serving code stays covered.
- The studio can spawn the command, read its one address line, frame `/`
  and follow `/events`; nothing in the session knows the studio.
