# ADR-017: What a proof cannot judge, it measures and lays out for the reviewer

Status: Accepted (OpenSpec change `proofs-report-the-look`, 1 October 2026).

## Context

Two findings of the Curta film *Addition* were caught by looking, by luck
of which still was looked at (`workflow/warts.md`, "Addition", 2 and 4). A
highlight on the bevel tips at the top of the shafts passed `preview`'s
highlight proof (the cue changes the pixels, its restore returns them
exactly, it re-applies identically) as the highlight on the input pinions
beside the drum does: the proof asks whether something changed, which is
true of the wrong part too. And the headline wrapped and the code was drawn
at 0.82 vw while `check` reported the headline's slot "sized by what it
holds" and the source panel's fit proof passed.

Neither is a defect a tool can decide. The take names a part by its
assembly path and the viewer lights that path; whether it is the part the
author meant is a judgment about the film's subject. Whether a two-line
headline is wanted, or 0.82 vw reads in an upload, is the author's.

## Decision

1. **A proof that cannot judge the look keeps what it compared, and
   measures what the author would otherwise estimate.** It adds no
   threshold, no expected value and no refusal; it says what it found in
   numbers and leaves the images where a reviewer finds them by name.
2. **A highlight's images are preview's.** For every highlight cue,
   `preview` keeps the unlit and the lit capture its proof compares at the
   cue's midpoint and writes a difference (the unlit frame in grey, every
   pixel that differs in red) under `preview/highlights/`, emptied at each
   preview, named by shot, cue and parts. The difference marks the named
   parts: a highlight that dims or ghosts the rest changes every part of the
   view, so for one the same instant is posed once more with the same
   highlight keeping the rest (`-parts-lit.png`, a review capture the film
   never draws) and the difference is taken against that; the first preview
   of *Addition* without it marked the whole machine for the pinions as for
   the drum. `preview/report.json`
   indexes them under each part as its author named it (a layer by its
   name, an assembly path by its names joined with `/`), with the paths
   lit, the pixels changed and their box; `preview` prints a line per
   highlight. The encoded film's review pack is not the place: its images
   are decoded from the MP4, which holds no unlit frame of a highlighted
   instant.
3. **`check` measures text in the layout probe it already runs** (ADR-009):
   on the same page, at the output size, before any take, each shot's
   source panels and shown titles are posed wholly shown, in their slots,
   and the stage reports the code's font size and each title's and
   subtitle's lines. `check` prints them per shot, in pixels and vw. The
   probe's conditions do not change: a movie document that shows no picture
   and has no reframe opens no browser, and `check` says its text was not
   measured.

## Consequences

- A reviewer opens `preview/report.json`, finds the part by name and the
  difference image beside it, and sees where the highlight landed without
  choosing a still; a highlight on the wrong part is as visible as one on
  the right part, and named.
- `check`'s lines give the numbers a stylesheet tuning moves, before any
  render: the code's size and how many lines each headline takes.
- The shipped source element reports `fontSize` and the shipped title
  `lines` and `subtitleLines`; the renderer compares none of them.
- `preview` writes three PNGs per highlight, four and one more pose for a
  highlight that dims or ghosts the rest; *Addition*'s eleven highlights,
  six of them ghosted or dimmed, add thirty-nine images at the preview's
  width.
- The stage runtime, `code.mjs`, `pixels.mjs` and `render.mjs` are inputs
  of the shot cache's common key, so every film is recaptured once; no
  pixel changes.
- Text is not measured for a YAML episode or for a movie document `check`
  opens no browser for; extending the probe to them would change the
  contract's "no picture, no browser" and is left to a film that needs it.

## Alternatives rejected

- **Declared expected regions** for a highlight, refused when its changed
  pixels fall outside: the region is another estimate of what the path
  already names, kept by hand through every camera change; a wrong path
  with a region drawn from the wrong still passes.
- **Thresholds** on code size or title lines: the finding was that nothing
  said the number, not that a number was wrong.
- **Highlights in the encoded film's review pack**: no unlit frame of the
  instant exists in the film, and a frame before the cue is another instant.
- **Measuring after the takes on the timeline's frames**: the text states
  do not depend on time; it would need a second probe or a page held open
  across the take reading.
