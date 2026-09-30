## Why

Two findings of 30 September 2026 in `workflow/warts.md`:

- "The React stage", wart 1: **a picture's geometry is only known in the
  browser.** A slot's box is the set's layout, so `check` cannot refuse a
  picture's enlargement beyond its allowance, or a view that leaves the
  picture, for a project's set; preview and render refuse them against the
  box the stage reports. YAML episodes still refuse them at `check` (the
  paper sets' boxes are known). A layout measured once per set when `check`
  bundles the stage would move the refusal before speech.
- "Cut and Advance, version 2", wart 6: **the picture's enlargement is
  checked only in the browser**: the still over a full-frame plate slot
  passed at preview and render; `check` could not say so before speech.

The episode is *Cut and Advance* (the Leonardo project, version 2,
30 September 2026). Its still `isometric` is shown in the `plate` slot of the
project's own set `Leonardo`, whose box only the template's stylesheet
knows. `check` printed "allowance N×; enlargement checked against its slot's
box at preview and render" and could refuse nothing about it; a still too
small for its plate would be found only after the narration had been bought
and a browser opened for preview. What the film does with the result: its
`check` prints the still's peak enlargement against its allowance, measured
on the box `Leonardo` draws for `plate` at the film's 1920×1080, and would
refuse a still too small for the plate before `speech` is run.

The orchestrator's ruling (fix-warts campaign, 30 September 2026): after
bundling, `check` measures the layout of every set the movie uses, once per
set kind, at the movie's output size, in a headless page served the bundle,
and refuses with the messages `src/pictures.mjs` already has what the
measured boxes let it refuse: a picture's enlargement beyond its allowance
and a picture view that leaves the picture, for a project's set as for a
shipped one; the report line prints the peak and the allowance instead of
deferring to preview. Where a set draws a slot whose box depends on what it
holds, the live box at preview and render remains the judge. `check` opens
no browser when the movie shows no picture, and needs no `--viewer` for the
probe.

## What Changes

- **`check` measures a movie document's sets.** When a movie document shows
  a picture, `check`, after bundling the stage and before reading any take,
  opens one headless Chromium, serves it the page the renderer serves (the
  bundle, `src/film.html`, the stage config) with a stub viewer whose
  `mount` is never called, and poses each set kind the movie's shots use,
  with no element placed, at the output size. For each slot it measures the
  slot's box, the box a picture element placed there gets, and whether the
  box stays put when the set's slots hold content larger than the frame. A
  new module, `src/layout.mjs`, does it; nothing memoizes it: it runs once
  per `check`.
- **The enlargement is refused before speech.** For each picture shown in a
  slot whose box stays put, the peak enlargement (the fit's scale in the
  measured box times the largest zoom of its view keys) is compared with the
  allowance, and `check` refuses a picture beyond it, before the takes are
  read, with the message `validatePictureSizing` gives a YAML episode, the
  measured box standing for the area: `Still plate would be enlarged 1.40×
  in shot still (864×576 source pixels in the 870.4×576 box of slot plate
  of set playbill); its upscale allowance is 1.2. Set upscale on the still,
  place it in a smaller slot, or use a larger source.`
- **A view that leaves the picture is refused at `check`.** Once the takes
  have resolved the times, every output frame of a picture's cue is resolved
  (`frameAt`) and its view's rectangle computed in the measured box; a frame
  that shows the background beside a covering picture, or cuts off one that
  underfills it, is refused naming the shot, the video time, the element and
  the picture, in the YAML wording.
- **The report line.** `check` prints one `Layout` line per measured set
  (each slot's box at the output size, or that it is sized by what it holds)
  and, for each picture, `peak P×; allowance A×` where the box is measured,
  keeping the deferral only for a slot whose box depends on what it holds.
- **No browser without a picture.** A YAML episode (its sets' boxes are
  known) and a movie document that shows no picture open no browser at
  `check`, as today. The comment "check has no browser" in
  `bin/videomaker.mjs` and `src/episode.mjs` says what is now true.
- **Tests.** Layer 8 (`test/pipeline/movie-pipeline.test.mjs`), red first:
  the tour with its still's allowance lowered is refused by `check` before
  any take exists, naming the still, the shot, the peak and the allowance;
  the tour with a view key that leaves the picture is refused naming the
  shot and the time; the tour prints its peak and allowance; `check` on the
  fixture movie without pictures launches no Chromium, counted in the
  command's own process. Layer 5 (`test/browser/layout.test.mjs`): the
  probe's boxes for the shipped `frame` and `split` and the tour's `Playbill`
  and `PlaybillSplit` equal the boxes a posed frame of each set reports, the
  picture box included, and the tour's `headline` is reported as sized by
  what it holds.
- **Records.** ADR-009 (STAGE); spec deltas; `docs/movie-document.md` where
  it says a slot's box is known only in the stage; `docs/stage.md`, where
  it lists what the renderer checks; `README.md`'s `check` paragraph;
  `docs/architecture-overview.md`; `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `movie-document`: `check` measures a document's set layouts and refuses a
  picture's enlargement before any take, and a view that leaves the picture
  once the takes resolve its times.
- `stills-and-clips`: the enlargement rule names the measured box for a
  movie document.
- `test-suite`: the layout probe is proved against a posed frame.

## Impact

Code: a new `src/layout.mjs`; `bin/videomaker.mjs` (the `check` path);
`src/pictures.mjs` (the two refusal messages built by one function each,
the YAML wording unchanged); a comment in `src/episode.mjs`;
`test/support/reach.mjs` (the new module reads `src/film.html`). The stage
runtime, the renderer, the timeline, the formats, the schema and the Python
package do not change, so no stage bundle and no cached shot changes. A
movie that shows a picture pays one Chromium launch and one pose per set
kind at `check` (measured in `evidence.md`).

## Non-goals

No change to the shipped sets' known boxes; no probe at preview or render
(the live box stays the judge there, and the probe's boxes are not given to
the renderer, see design D6); no new command option; no browser when the
movie shows no picture; no refusal at `check` for a slot whose box depends
on what it holds. No publication, push or paid request.
