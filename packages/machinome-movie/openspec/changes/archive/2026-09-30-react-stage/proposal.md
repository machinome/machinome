## Why

The validation film *Cut and Advance* (Leonardo project,
`videos/cut_and_advance/spec.md`, version 2) is to be drawn by the project's
own template: a root set `Leonardo` and its split `LeonardoSplit` written in
the project's `stage.tsx`, source shown beside the model in three chapters
with spoken words lighting its tokens, a project element `Jobs` lit on cue,
titles and a picture placed in the template's slots, and no progress rule.
The pilot, inspecting version 1, ruled the fixed film page unacceptable: "the
template needs to own the screen ... no hardcoded stuff in the screen. I want
source code shown, that nice way of highlighting the concepts, side by side,
two different containers." The Python side (`declarative-stage`, merged into
`react-stage`) already evaluates movies to `machinome-movie/0.2`, which
carries sets with slots, elements, cues and actions and names the project's
stage modules. Nothing on the Node side reads it: the commands still load the
removed 0.1 shape, and the renderer draws every film on one page
(`src/film.html`, `src/film.js`) with a hard-coded brand, series label and
progress rule, three layouts with fixed insets and a fixed inventory of
overlays. The Node suite is red on the removed 0.1 schema and fixtures.

The pilot's proposal `remove-progress-rule` (branch `remove-progress-rule`)
decided on the same morning that the progress rule leaves every film: its
decisions D1 to D5 are carried here, where the page it edits is replaced.

## What Changes

- **BREAKING** The commands read `machinome-movie/0.2` (contract
  `docs/movie-document.md`, schema `schema/machinome-movie-0.2.json`) and
  refuse anything else by its format, 0.1 included. A document is checked
  against the schema, then statically (the stage block, sets and slots,
  placements, elements, actions and their fields, spans, phrases, marks,
  cameras, layers, parts against the export, tokens against the source,
  typing across a chapter, stage modules inside the project), then resolved
  against the cached takes to the **resolved document**
  (`<root>/_build/movie-resolved.json`).
- **BREAKING (pixels)** YAML episodes (formats 0.2, 0.3, 0.4) load into the
  same resolved shape, one chapter per shot, drawn through the shipped sets
  `paper`, `paper-split` and `source-only`, which reproduce the earlier
  page's layouts and masthead. Every YAML validation, refusal and timing rule
  keeps its meaning; every film's pixels change.
- **BREAKING (pixels)** No film draws a progress rule; the frame carries no
  film-wide position (the pilot's `remove-progress-rule`, D1 to D5).
- The timeline resolves a **frame** per instant: the set, the element in each
  slot, and each placed element's complete state (views with camera, model
  time, hidden parts, highlight and marks; source panels with typed text,
  highlighted markup, cursor and lit tokens; titles; pictures; project
  elements with their active actions and progress), plus the transition with
  the outgoing frame. A view keeps its camera, and a source panel its typed
  text, across the shots of its chapter.
- The **React stage** replaces the film page: a runtime (`stage/`,
  TypeScript, React 19) with a registry (`defineSet`, `defineElement`),
  `Slot`, `Chrome`, `useMovie`, `useReport`; the shipped sets `frame`,
  `split`, `paper`, `paper-split`, `source-only`; the shipped elements
  `view` (one viewer instance per view element, kept across its chapter),
  `source`, `title`, `picture`; the transition layer; and `window.film`,
  whose `setFrame` returns what the stage measured. The stage refuses at
  mount, by name, an unregistered set or element kind, a set whose slots
  differ from the document's, and a viewer API below what the movie needs.
  `src/film.js` is deleted; `src/film.html` holds only empty layers.
- **One bundle per movie**: the runtime and the document's stage modules
  bundled by esbuild into `<root>/_build/stage/stage.js` and `stage.css`,
  `movie.d.ts` generated from the stage block, TypeScript modules checked
  with `tsc --noEmit`, rebuilt only when the content of its inputs changes.
  `check` bundles and type-checks; the bundle's hashes enter the shot
  cache's common key and the manifest.
- The renderer drives the stage: every readback check and pixel proof is
  ported to what the stage reports per element and for its chrome; review
  samples are chosen from element states.
- Fixtures: resolved pins for the Python documents; the fixture project's
  `tour` gets a real template (`stage.tsx`, `stage.css`), which re-pins its
  revision and re-evaluates the documents.
- Tests: layers 2, 3, 4, 5, 8 and 9 for all of the above under the runner and
  memo of `one-runner`; browser and pipeline tests move to `test/browser/`
  and `test/pipeline/`.

## Capabilities

### New Capabilities

- `react-stage`: the template that owns the screen: sets, slots, chrome,
  elements, the registry and its refusals, one bundle per movie, generated
  types, and what the stage reports to the renderer.

### Modified Capabilities

- `movie-document`: rewritten for `machinome-movie/0.2`: checks, resolution,
  the resolved document and the frame.
- `educational-video-production`: a film carries no progress indicator;
  YAML episodes and documents are both drawn by sets.
- `source-only-shots`, `shot-transitions`, `stills-and-clips`: the masthead
  alone is chrome; layouts are the shipped sets; picture areas are slots.
- `shot-level-incremental-rendering`: duration stays a common input for a
  stated reason; the stage bundle is a common input.
- `part-annotations`, `part-highlighting`: marks and highlights belong to a
  view element; places, offsets and padding are fractions of the view's box.
- `text-animation`, `narrated-source-scenes`: titles and source panels are
  elements; emphasis lights tokens on any line.
- `visual-review-packs`: review events are read from element states.
- `test-suite`: the stage's layers and the test layout.

## Impact

New: `stage/` (runtime, shipped sets and elements, their CSS and tests),
`src/stage-build.mjs`, `docs/stage.md`, ADR-004 (`STAGE`), ADR-006
(`SOURCE`), `test/browser/`, `test/pipeline/`, the fixture project's
`videos/tour/stage.tsx` and `stage.css`. Changed: `src/movie.mjs`,
`src/schema.mjs`, `src/episode.mjs`, `src/timeline.mjs`, `src/words.mjs`,
`src/code.mjs`, `src/pictures.mjs`, `src/render.mjs`, `src/shot-cache.mjs`,
`src/review-samples.mjs`, `src/pixels.mjs`, `src/chapters.mjs`,
`src/speech.mjs`, `bin/videomaker.mjs`, `src/film.html`,
`scripts/pin-resolved.mjs`, `fixtures/resolved/`, the fixture project's
revision and documents, `vitest.config.mjs`, `test/**`, `docs/FORMAT.md`,
`docs/movie-document.md` (wording), `docs/architecture-overview.md`,
`docs/adrs/README.md`, `README.md`, `AGENTS.md`, `CHANGELOG.md`,
`workflow/warts.md`. Removed: `src/film.js`, the 0.1 resolved pins. Consumers:
every existing film re-renders cold with new pixels; no Leonardo source,
speech or export changes here. No Python code changes.

## Non-goals

Takes from running or clocked scenarios; the page element; the studio's live
preview; several formats from one movie; element kinds beyond the contract's;
the Leonardo film itself (the campaign's film step); layer 6 (the real
viewer); publication.
