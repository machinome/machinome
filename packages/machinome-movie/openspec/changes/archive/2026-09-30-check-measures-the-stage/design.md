## Context

`bin/videomaker.mjs`'s `check` path, for a movie document, reads the
document, bundles and type-checks its stage (`buildFilmStage`), then loads
the episode (`loadEpisode`, which resolves the anchors and so needs the
cached takes), prints the summary, the chapters' takes, the stage bundle,
and one line per picture shown. For a picture it knows a box only for the
shipped paper sets (`PAPER_STAGE`, fractions of the frame, YAML episodes
only); for every set a movie document can use (`frame`, `split` and the
project's) it prints "allowance N×; enlargement checked against its slot's
box at preview and render". A YAML episode's pictures are refused at load
(`validatePictureSizing`, and the per-frame view check in
`validateLoadedPictures`), against `STAGE_AREAS`.

`src/render.mjs` refuses, on every posed frame, a picture drawn more
enlarged than its allowance and a view that leaves the picture, against the
element box the stage reports (`seen.box`), and for the paper sets checks
the live box against `knownSlotBox()`.

`stage/runtime.tsx`'s `boot()` fetches `/config.json`, checks the registry,
requires `window.MachinomeViewer` with a `mount` function, decodes the stills
the config lists, waits for fonts and creates `window.film`.
`setFrame(frame)` renders the set the frame names with the elements in its
slots, poses the views it places, repaints when needed and measures every
`.vm-slot` (`observed.slots`) and every placed element's box. A picture's
element is `div.vm-element.vm-element-picture`, a size container
(`container-type: size`) filling its slot (`width: 100%; height: 100%`); the
drawn rectangle is CSS arithmetic over that box.

The fixture tour's `Playbill` draws `stage`, `plate` and `aside` with fixed
boxes and `headline` with a width and no height: its box is as tall as the
title it holds.

## Goals / Non-Goals

Goals: `check` refuses, for a movie document, the two picture refusals the
live box gives, measured on the page the renderer draws, before `speech`
for the enlargement; a movie without a picture pays nothing. Non-goals:
those of the proposal.

## Decisions

### D1. When `check` measures

`check` measures when the source is a movie document and at least one cue
of one of its shots fires `show` on a picture element. It measures after
the stage is bundled and type-checked and before `loadEpisode`, so before
any take is read. A YAML episode never measures: its sets are the paper
sets, whose boxes are known, and its pictures are refused at load as
before. A movie document without a picture never measures, so it opens no
browser, as today.

Every set kind a shot of the movie uses is measured, once each, whether or
not it holds a picture: the `Layout` lines report the movie's layout, and a
pose per set costs a few milliseconds once the page is open. The shipped
`frame` and `split` are measured like a project's set: their boxes come
from `stage.css` and the movie's safe inset, known only in the page, and the
ruling covers "a project's set as a shipped one". (The ruling's "no browser
when the movie shows no picture in a project's set" is read as "no picture
in a set whose boxes Node does not know"; for a movie document that is
every set, so the rule is "no picture, no browser".)

### D2. How: the renderer's page, a stub viewer

`src/layout.mjs` launches one headless Chromium (or takes a browser and an
asset server, as `browserSession` does, so tests use the run's one Chromium),
opens a page of the output size at a device scale of 1, and serves it
exactly what the renderer serves for the stage: `src/film.html`,
`stage.js` and `stage.css` of the bundle just built, and `/config.json`
from `stageConfig` (the renderer's) with no media, so the page decodes no
still. `/viewer.js` is a stub, written in the module:

    window.MachinomeViewer={mount(){throw new Error('The layout probe mounts no viewer')}};

`boot()` requires the factory and never calls `mount` while no view is
placed. Each set kind is then posed with `window.film.setFrame`, with the
frame of the first shot that uses it, emptied: its `time`, `chapterId`,
`shotId` and `set`, no slot filled and no element.

Alternatives rejected:

- **A probe entry in the runtime** (`window.film.layout(set)`): a second
  code path in the page that could lay out differently from the one the
  renderer poses, and a change to `stage/runtime.tsx`, which is bundled
  into every film: every film's bundle hash, a common input of every cached
  shot, would change and every film would recapture once, for nothing it
  draws. The stub keeps the page and the bundle byte for byte what the
  renderer serves.
- **Requiring `--viewer` and mounting the real viewer.** No view is placed,
  so no viewer is needed, and `check` of a document needs no viewer bundle
  today unless the movie needs API 28.
- **Computing the boxes in Node from the stylesheets.** The stage owns
  layout (ADR-004); any Node model of CSS is a second layout engine.

### D3. What is measured, and which box is trusted

After `setFrame` with no element, in the page, for every `.vm-slot` of the
set:

1. the slot's box;
2. the box a picture placed there gets: a `div.vm-element.vm-element-picture`
   is appended to each slot, the element and classes the stage gives a
   picture's box, so the set's stylesheet and the stage's size containment
   apply to it as to a picture's; its box is measured;
3. whether the slot's box depends on what the set's slots hold: every
   appended box loses the picture class and receives a block three times the
   frame's width and height, and every slot is measured again. A slot whose
   box changed (an auto height, a flex or grid track that grows with its
   content or a sibling's) is **sized by what it holds**.

The appended boxes are removed before the next set is posed. A slot is
trusted at `check` when its box did not change in step 3 and the picture
box of step 2 has a positive width and height; otherwise `check` defers to
the live box at preview and render, and says so. At the tour's 1280×720,
`plate` is 870.4×576 at (64, 86.4) and trusted; `headline` is sized by what
it holds.

The measurement is a pure function of the bundle, the document's stage
block and style and the output size: `setFrame` draws only what the frame
gives it, and an empty frame depends on no time.

### D4. The refusals

- **Enlargement, before the takes.** For each `show` of a picture element
  in a trusted slot: `peak = fit(w/W, h/H) × zoom`, where `w×h` is the
  measured picture box, `W×H` the probed source size, `fit` is `min` for
  `contain` and `max` for `cover`, and `zoom` the largest zoom of the
  action's view keys (1 without keys, and for a clip). Zoom between keys is
  interpolated between the keys' zooms, so the largest key is the peak. An
  SVG still has no limit. The media are probed with `loadPictures` before
  the takes (paths, formats, sizes, committed status), and again by
  `loadEpisode` as today. The refusal is the YAML message, with the measured
  box for the area and the document's remedy (D7 says where it is written):

      Still plate would be enlarged 1.40× in shot still (864×576 source pixels in the 870.4×576 box of slot plate of set playbill); its upscale allowance is 1.2. Set upscale on the still, place it in a smaller slot, or use a larger source.

  The YAML wording is unchanged: `(… in the 1152×453.6 stage area); … choose
  area: stage, or use a larger source.`
- **A view that leaves the picture, once the takes resolve.** A view key's
  time may be anchored to the narration, so the frames of a cue are known
  only after `loadEpisode`. For each `show` of a still with view keys in a
  trusted slot, every output frame from the cue's `at` to its `until` is
  resolved with `frameAt` (the state the stage is given), and the view's
  rectangle computed with `pictureRect` in the measured box; the rule is
  YAML's: a rectangle that overfills an axis must cover the box on it, one
  that underfills must stay inside it. The refusal, in YAML's words:

      Picture view leaves the picture in shot still at 16.67 s (tip.plate, plate); keep the view inside the picture or zoom in

  naming the shot, the video time, the element and the picture where YAML
  names the picture's index and its media.
- A page error while measuring (a set the bundle does not register, slots
  that differ) is refused as the stage refuses it at mount, prefixed
  `Measuring the stage's layout for check:`.

### D5. What `check` prints

After the `Stage:` line, one line per measured set, in the order the shots
first use them:

    Layout playbill at 1280×720: stage 870.4×576 at 64,86.4; plate 870.4×576 at 64,86.4; aside 243.2×288 at 972.8,216; headline sized by what it holds

and for each picture shown, `peak P×; allowance A×` when its slot is
trusted, `vector, no enlargement limit` for an SVG, and, for a slot sized by
what it holds, `allowance A×; slot S of set K is sized by what it holds,
enlargement checked against its box at preview and render`.

### D6. Preview and render are unchanged

The ruling allows the probe's boxes to serve preview and render as a
project set's known layout if that costs nothing. It costs a decision: the
renderer compares an element's box, which a set may pad inside its slot,
and a known box would need either a second probe page per session or the
boxes carried from `check`, which may have run on other content. The live
box already judges every frame there. Left out, recorded in the evidence.

### D7. Where the code lives

`src/layout.mjs`: `picturesShown(doc)` (the shown pictures, from an
unresolved or a resolved document), `measureLayouts(doc, bundle,
{browser, assets})`, `layoutLines(layouts)`, `checkEnlargements(doc, media,
layouts)` and `checkPictureViews(film, layouts)`. `bin/videomaker.mjs` calls
them on the document path. `test/support/reach.mjs` declares that
`src/layout.mjs` reads `src/film.html`.

Implementation note (30 September 2026): the plan put the two refusals'
words in one function each in `src/pictures.mjs`, shared with the YAML
checks. `src/pictures.mjs` is hashed into the common key of every cached
shot (`render.mjs`, the render's `commonKey`), so that refactor would have
recaptured every film for nothing drawn. The words are written in
`src/layout.mjs` instead, in the YAML wording (the same sentence, the
measured box standing for the area, the slot and set for `choose area:
stage`, the element key for the picture's index), and `src/pictures.mjs` is
unchanged. The finding is recorded in the evidence.

## Risks / Trade-offs

- **The content test is a probe, not a proof.** A layout could change for
  content of another shape than a block larger than the frame and not for
  that block. The live check at preview and render still refuses on every
  frame, so a slot misjudged as fixed can only let `check` pass what preview
  refuses, or refuse what preview would refuse at a slightly different
  peak; the layer 5 test pins the four sets the suite has.
- **A second Chromium launch at `check`** for a movie with a picture: one
  launch and one pose per set kind, measured on the tour in the evidence.
- **The media are probed twice** at `check` (before and after the takes):
  `ffprobe` on each still and clip, milliseconds each.
