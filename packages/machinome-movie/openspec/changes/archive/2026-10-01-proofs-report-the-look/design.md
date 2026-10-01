## Context

`preview` (`src/render.mjs`) proves each highlight cue at its midpoint: the
same instant with its shot's transition removed is captured without the
cue, with it, without it and with it again; the cue must change the pixels,
the two unlit captures must be equal and the two lit ones too. On success
it keeps nothing but `{shotId, element, cue, index, time, changed,
restored, reapplied}` in `preview/report.json`; the captures are dropped. A
highlight on the wrong part passes the same way as one on the right part,
because the proof's question (did something change, and does it come back)
is the same for both. The stills `preview` saves (three per shot and one at
each highlight's midpoint) show the lit frame only, among dozens of others.

`check` (`bin/videomaker.mjs`) runs the layout probe (`src/layout.mjs`,
ADR-009) when a movie document shows a picture or comes in by a reframe:
before any take is read, one headless page at the output size, served the
movie's bundle, `src/film.html` and the stage config, with a stub viewer
whose `mount` throws, poses each set kind empty and measures its slots. A
title's slot is reported "sized by what it holds", and nothing measures the
text itself. The stage's shipped elements report what they drew
(`measureElement` in `stage/runtime.tsx`): a source panel its text, lit
tokens, cursor and whether it fits; a title the box of its text and its
revealed count.

The two findings were caught by looking. This change does not make the
tool judge them; it lays the look out so that looking is systematic, and
measures what the author was estimating.

## Goals / Non-Goals

Goals: for every highlight, a reviewer finds the lit frame, the unlit frame
of the same instant and where they differ, named by the part, without
choosing a still; `check` states each shot's code size and title line
counts at the output size. Non-goals: those of the proposal.

## Decisions

### D1. The highlight images are preview's

The unlit frame of a highlighted instant exists only where it is posed: in
`preview`'s proof. The film never draws it, so the encoded film's review
pack, whose every image is decoded from the MP4 (`visual-review-packs`),
cannot carry it, and `render` runs no highlight proof. The images go where
the proof makes them: `preview/highlights/`, beside `preview/report.json`,
which indexes them. The directory is a subdirectory so that the contact
sheet, built from `preview/*.png`, is unchanged; it is emptied at the start
of each preview, so it holds exactly the images the report lists.

The two captures are the ones the proof compares, the first unlit and the
first lit (the second of each is proved equal to them); nothing is posed
for the images.

### D2. Names

    preview/highlights/<shot>-<cue>-<parts>-lit.png
    preview/highlights/<shot>-<cue>-<parts>-unlit.png
    preview/highlights/<shot>-<cue>-<parts>-difference.png

- `<cue>`: a YAML episode's highlight by its index, `highlight-0`; a movie's
  by its place, `cues[1].actions[0]` written `cue1-action0`.
- `<parts>`: each part as the author named it, a layer by its name, an
  assembly path by its last name, joined with `+`, in the authored order:
  the pinion highlight of *Addition* is
  `add-23-cue1-action0-stepped_drum+p_10219_410002_1+p_10230_410008_1_419229`.
  Past 96 characters the remaining parts are counted, `+3-more`, so a file
  name stays well inside the file system's limit; the report carries every
  path.
- Every character other than a letter, a digit, `_`, `.` or `-` becomes `-`.

A shot and a cue identify a highlight uniquely (one highlight action per
cue place), so names never collide.

### D3. The index

`preview/report.json` gains:

    "highlights": {
      "main_drive/stepped_drum": [{"shotId": "add-23", "cue": "cues[1].actions[0]", "element": "first.inside",
        "time": 61.2, "paths": [[…], […], […]],
        "lit": "highlights/add-23-…-lit.png", "unlit": "…-unlit.png", "difference": "…-difference.png",
        "changedPixels": 48210, "changedBox": [1004, 352, 612, 388]}],
      "transmission/result/ones/p_10219_410002_1": [ … the same entry … ],
      …
    }

keyed by each part as the author named it: a layer by its name, an
assembly path by its names joined with `/`. A highlight of three parts is
listed under each of the three; the keys are in the order first met. Each
`highlightChecks` entry gains the same `parts` (as authored), `paths` (every
assembly path the highlight lights, a layer expanded), `images` (`lit`,
`unlit`, `difference`, relative to `preview/`), `changedPixels` and
`changedBox`. Paths in the report are relative to `preview/`, so the
directory can be moved and read.

### D4. The difference image

Both captures are decoded (`src/pixels.mjs`); a pixel is changed when any
channel differs, exactly: the two captures are the same instant, and the
proof already requires exact equality where nothing is lit. The image is
the unlit frame in grey (its luminance mapped to 160 to 255, so the frame
is recognisable and every red mark stands out) with each changed pixel pure
red. `changedPixels` counts them; `changedBox` is `[x, y, width, height]`
of the smallest rectangle holding them, in pixels of the preview's width.

### D4a. Where the parts are, when the rest is dimmed or ghosted (implementation evidence)

Added during implementation, from the film proof. The first preview of
*Addition* with D4 as planned gave, for the pinion highlight (`others:
ghost`), 58 795 changed pixels within 232×416, and for the drum alone
59 865 within 232×417: the difference marked the whole machine red in both,
because a ghost or a dim changes every part of the view. The image said
nothing about where the named parts were, which is the finding.

So for a highlight whose `others` is `dim` or `ghost`, `preview` poses the
same instant once more with the same highlight keeping the rest
(`others: keep`), a review capture the film never draws, keeps it as
`<stem>-parts-lit.png` (`images.partsLit`), and takes the difference, the
changed pixels and their box against it: they mark the named parts alone.
For a `keep` highlight the lit frame is that capture already and nothing
more is posed. The lit frame the film draws is still kept as `-lit.png`.
How a highlight is drawn in the film does not change; the extra pose
applies and restores a highlight exactly as the proof's poses do.

### D5. Preview's line

One line per highlight, after the proofs, before the storyboard:

    Highlight add-23 cues[1].actions[0] lights main_drive/stepped_drum, transmission/result/ones/p_10219_410002_1, transmission/result/tens/p_10230_410008_1_419229: 48210 pixels changed within 612×388 at 1004,352; see preview/highlights/add-23-cue1-action0-stepped_drum+p_10219_410002_1+p_10230_410008_1_419229-difference.png

`preview` returns the report; the command prints the lines from it.

### D6. `check` measures text in the probe it runs

The text is measured where the layout is: in `measureLayouts`, on the
probe's page, at the output size, before any take, when and only when the
probe runs (a movie document that shows a picture or comes in by a
reframe). Nothing about how the probe runs changes: one Chromium, the same
page, the same stub viewer. After the sets, it poses, for each shot that
places a source panel or a title one of its cues shows, a frame of the
shot's set holding only those elements, each wholly shown:

- a title shown at opacity 1, its whole text and its subtitle (a reveal's
  hidden words keep their place, so the reveal does not change its lines);
- a source panel with its whole pinned excerpt typed, as the timeline's
  state gives it when typing is complete: the highlighted markup, no cursor,
  nothing lit (`wholeSource` in `src/code.mjs`, shared with `sourceState`).

Views, pictures and project elements are not placed: the probe mounts no
viewer and serves no media, and its premise (ADR-009) is that a slot's box
is the set's, not its neighbours'; a slot sized by what it holds is
measured holding its own text. The text states do not depend on video
time, so no take is needed; the excerpts are read from the pinned revision
before the takes, with `loadSourceCode`'s refusals in its words.

### D7. What the stage reports

`measureElement` (`stage/runtime.tsx`) adds:

- source: `fontSize`, the computed font size of the panel's code, in CSS
  pixels (null where no layout gives one);
- title, when drawn: `lines`, the number of line boxes its text occupies,
  and `subtitleLines` with a subtitle. Counted from the client rectangles
  of the text's inline boxes: the distance from the first box's centre to
  the last's divided by the line height, plus one, so an empty line of a
  `pre-line` title counts; where the line height is `normal`, the distinct
  centres are counted. Null where the page has no layout (jsdom).

The renderer reads none of it; it does not change what is drawn.

### D8. The words

One line per measured shot, after the `Layout` and `Reframe` lines, in shot
order, its elements in the order the shot places them:

    Shot question: title question.problem in headline on 1 line, its subtitle on 2 lines
    Shot inputs: source machinome.drivers in left at 17.3 px (0.90 vw)

Pixels to one decimal, vw (a hundredth of the output width) to two. No
threshold: the numbers are the author's to judge, and nothing is refused.

A movie document whose layout `check` does not measure, and that places a
source panel or shows a title, gets one line instead:

    Text not measured: check measures a movie's stage only when it shows a picture or comes in by a reframe; read the sizes and the lines on preview's stills

A YAML episode gets none: its check measures nothing of its paper sets.

## Alternatives rejected

- **Declared expected regions for a highlight**: the author declares where
  on screen the part should light, and `preview` refuses a highlight whose
  changed pixels fall outside. The region is the author's estimate of the
  same thing the path names: a wrong path written with a region drawn from
  the wrong still passes, a right path with a loose region passes anything.
  It moves the judgment into another number to maintain, through every
  camera change. The viewer's own `partOnScreen` for the highlighted paths
  agrees with itself by construction. Rejected by the orchestrator's cut:
  no proof can know which part the author meant.
- **The encoded film's review pack.** Its images are decoded from the MP4
  by contract; there is no unlit frame of a highlighted instant in the film,
  and a frame before the cue is another instant (the model and the camera
  move), so its difference would show motion, not the highlight.
- **Thresholds**, a minimum code size or a maximum number of title lines,
  warned or refused. Whether 0.82 vw reads in a 1080p upload, or a two-line
  headline is wanted, is the author's; the finding is that nothing said the
  number, not that a number was wrong.
- **Opening a browser for a document without a picture or a reframe** to
  measure its text. The contract (`docs/movie-document.md`, "The stage";
  `movie-document` spec, "No picture, no browser") says `check` opens none;
  this change keeps it and records the gap as a finding.
- **Measuring after the takes on the timeline's frames.** It would need a
  second probe or the probe's page kept open across the take reading, for
  states that do not depend on time.
- **Measuring from the stylesheet without a browser.** A set's custom
  properties, slot widths and fonts are the template's; only the stage's
  page resolves them.
- **A per-pixel tolerance in the difference.** The captures are of one
  instant on one page; the restore proof already holds them to exact
  equality where nothing is lit.
