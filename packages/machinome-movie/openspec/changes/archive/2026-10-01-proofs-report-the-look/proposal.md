## Why

The episode is *Addition*, the Curta film of the curta-video campaign (the
Curta Type I 3x project, `videos/addition/`), the first film on a clocked
take. Producing it met two findings (`workflow/warts.md`, "Addition (Curta,
1 October 2026)", 2 and 4):

2. **The highlight proof cannot tell the right part from the wrong one.** A
   highlight on the bevel tips at the top of the shafts passed `preview`'s
   proof (changed, restored, re-applied) exactly as the one on the input
   pinions beside the drum does; the wrong part was caught by looking at
   the stills, by luck of which still was looked at.
4. **No proof or check line says when a title wraps or code is too small.**
   `check` reported the headline slot "sized by what it holds" and the
   source panel's fit proof passed with its code at 0.82 vw; both were
   found by looking.

The orchestrator's cut (plan, 1 October 2026): no proof can know which part
the author meant, since the take names a part by its path and the viewer
lights that path; whether it was the intended part is a human judgment.
Nor is a code size too small or a two-line headline wrong in itself. The
tool's job is to make the look systematic instead of lucky, and to measure
what the author would otherwise estimate.

## What the film does with the result

*Addition* is checked and previewed again from the campaign head. `preview`
leaves, for each of its eleven highlights, the lit frame, the unlit frame of
the same instant and their difference, named by shot, cue and the parts
lit, and `preview/report.json` lists them under each part's name: the
reviewer opens the pinion highlight of `add-23` and sees in red where it
landed, beside the drum, without choosing the right still. `check` prints,
for the shots that show the question, the answer and the three source
panels, the headline's line count and the code's size in pixels and vw at
the output size, so the next tuning of `stage.css` is read from a line
instead of estimated from a render.

## What Changes

- **Preview lays out each highlight.** For every highlight cue, `preview`
  keeps the two captures its proof already compares at the cue's midpoint
  (the unlit and the lit frame of one instant) and writes their difference
  image, the unlit frame in grey with every pixel that differs in red, into
  `preview/highlights/`, emptied at each preview, as
  `<shot>-<cue>-<parts>-{lit,unlit,difference}.png`. (Added in
  implementation, design D4a: a cue that dims or ghosts the rest changes
  every part, so it is posed once more with its parts lit and the rest
  kept, `-parts-lit.png`, and its difference is taken against that.)
  `preview/report.json` gains a `highlights` index keyed by each
  highlighted part's name (a layer by its name, an assembly path by its
  names joined with `/`), and each `highlightChecks` entry gains the parts,
  the paths lit, the images, the number of pixels changed and the box that
  holds them. `preview` prints one line per highlight with the same facts.
- **`check` reports measured text.** When `check` measures a movie
  document's layout (the document shows a picture or comes in by a
  reframe), the same probe, on the same page, at the output size and before
  any take, also poses each shot's source panels and shown titles, wholly
  shown, and reads what the stage measured: the code's font size and each
  title's (and subtitle's) line count. One line per shot:
  `Shot question: title question.problem in headline on 2 lines, its subtitle on 1 line`,
  `Shot inputs: source machinome.drivers in left at 17.3 px (0.90 vw)`. No
  threshold, no refusal. A movie document the probe does not measure gets
  one line saying its text was not measured and why.
- **The stage reports what it needs for that.** The shipped source element
  reports `fontSize`, the shipped title `lines` and, with a subtitle,
  `subtitleLines`.
- **Proofs**: layer 5, the double's highlight leaves the three images and
  the index (red first); layer 5, the probe measures the tour's text and a
  narrowed headline's wrapping (red first); layer 6, the real viewer's
  highlights of the tour leave the images under `Stand`, `Beam`,
  `Beam/Plank` and `Beam/Weight`; layer 8, `check`'s lines on the tour and
  on a narrowed headline, the not-measured line on the clocked fixture, and
  `preview`'s highlight line.
- **Records**: ADR-017 (PIPELINE); `README.md`, `docs/FORMAT.md`,
  `docs/stage.md`, `docs/architecture-overview.md`, `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `part-highlighting`: preview lays out each highlight's lit, unlit and
  difference images, indexed by part.
- `movie-document`: `check` reports the measured text of each shot when it
  measures the layout, and says when it did not.

## Impact

Code: `src/render.mjs` (preview's highlight loop), `src/pixels.mjs` (the
difference image), `src/layout.mjs` (the text the probe measures and its
lines), `src/code.mjs` (a wholly typed panel's state), `bin/videomaker.mjs`
(`check`'s and `preview`'s lines), `stage/runtime.tsx` (what the shipped
source and title report). Tests in `test/browser/render.test.mjs`,
`test/browser/layout.test.mjs`, `test/viewer/real-viewer.test.mjs`,
`test/pipeline/movie-pipeline.test.mjs`, `test/repository.test.mjs`. No
schema, document, contract page, Python or viewer change. The stage runtime
and `render.mjs` are inputs of the shot cache's common key, so every film is
recaptured once, as any change of the renderer is; no frame's pixels change.

## Non-goals

Any refusal. Any change to how a highlight is drawn or to the proof's
verdicts. Declared expected regions for a highlight (rejected in
`design.md`). Thresholds on code size or title lines. Text measurement for
a YAML episode, or for a movie document `check` opens no browser for (the
contract says it opens none; recorded as a finding). The encoded film's
review pack (`review-packs/`) is not changed: every image there is decoded
from the MP4, which holds no unlit frame of a highlighted instant. No
publication, push or paid request.
