# Videomaker architecture overview

The synthesis: how the tool is built, in one place, derived from the
baseline specs in [`openspec/specs/`](../openspec/specs/) and the decision
log in [`docs/adrs/`](adrs/README.md). ADRs accumulate; this document
integrates. When an archived change shifts the structure described here,
updating this page is part of landing the change.

## What it does

Videomaker turns a machinome project's exported, posed simulation into a
narrated film that a person can inspect frame by frame. The project writes a
source; the tool checks it, generates and caches narration, proves the
picture in a real browser, renders frames and encodes them. Every frame is a
pure function of video time, which is what every proof, cache and provenance
claim rests on. Mechanics stay in the project's simulation: the tool poses
the real model through the machinome viewer and never invents a pose.

## The pipeline

    source: YAML episode (formats 0.2-0.4), or movie document (machinome-movie/0.2)
        │  a YAML episode: every rule of its format,     src/episode.mjs
        │    converted to the resolved document in the paper sets
        │  a document: format, schema, static checks,    src/movie.mjs, src/schema.mjs
        │    at check its stage bundled and, if it shows    src/stage-build.mjs,
        │    a picture, its sets' layout measured on the    src/layout.mjs
        │    stage and enlargements refused, before takes;
        │    anchors resolved from the cached takes
        │    a clocked take: held to its export and to    src/take.mjs
        │    the replay of its steps, before any take
        │  both: validated against the export and project
        ▼
    resolved movie document (numeric times, chapters, sets, slots, elements)
        │  written to <root>/_build/movie-resolved.json for a document
        │  frameAt(film, t): pure                          src/timeline.mjs
        ▼
    frame: set, the element in each slot, each placed element's state
           (a view: a loop's time, or a clocked take's bank, ADR-012),
           the transition with its outgoing frame, or a reframe with
           each moving view's box (measured slot boxes, ADR-010)
        │  window.film.setFrame(frame) on the React stage  stage/
        │  bundled per movie with the project's modules    src/stage-build.mjs
        ▼
    observed: what the stage drew, per element, with the chrome's rectangles
        │  readback checks, pixel proofs (chrome masked)   src/render.mjs, src/pixels.mjs
        ▼
    PNG frames per shot, cached by content                src/shot-cache.mjs
        │  FFmpeg
        ▼
    rehearsal.mp4 + rehearsal.srt + manifest + review packs

The seam after loading is the resolved movie document
([ADR-006](adrs/SOURCE/ADR-006-yaml-episodes-and-movie-documents-load-into-one-resolved-document.md)):
a movie document resolves to it against its cached takes; a YAML episode,
validated as before, converts to it one chapter per shot, its fields
synthesized into elements and actions placed in the shipped sets `paper`,
`paper-split` and `source-only`. The timeline, the stage, the renderer, the
shot cache and the review packs read only this shape.

The stage ([ADR-004](adrs/STAGE/ADR-004-the-stage-is-a-react-template-that-owns-the-screen.md),
[the authoring contract](stage.md)) is a React 19 runtime in `stage/`:
`registry.ts` (`defineSet`, `defineElement` and the refusals at mount),
`components.tsx` (`Slot`, `Chrome`, `useMovie`, `useReport`), `shipped.tsx`
(the sets `frame`, `split`, `paper`, `paper-split` and `source-only`; the
elements `view`, `source`, `title` and `picture`), `marks.ts` (rings, labels
and arrows over a view), `runtime.tsx` (the boot, the viewer instances
hosted outside React and leased to the view elements each frame places
([ADR-007](adrs/STAGE/ADR-007-viewer-instances-are-leased-to-view-elements-per-frame.md)),
the transition layer and `window.film`) and `stage.css`. Four joins are
composed in the transition layer from same-instant captures; a reframe is
drawn live, its moving views' hosts over the boxes the frame gives them and
the incoming shot's other elements at its progress as opacity (ADR-010). `src/film.html` holds three empty layers,
the stage, the transitions and the chrome, and no colour, word or layout.
`src/stage-build.mjs` bundles the runtime with a movie's stage modules into
`_build/stage/stage.js` and `stage.css` with esbuild, generates `movie.d.ts`
from the document's stage block, checks TypeScript modules with `tsc
--noEmit`, and reuses the bundle while the content of its inputs is
unchanged; a YAML episode is drawn by the runtime alone. The bundle and its
key name every file by the tool (`videomaker/stage/…`,
`videomaker/node_modules/…`) or the project repository (`project/…`),
rewriting esbuild's machine-relative names in its outputs, so a checkout's
location never changes the bytes, the hashes or the shot cache's key
(ADR-013).

Narration belongs to chapters (`src/chapters.mjs`): a movie document groups
shots into chapters of one narration each; a YAML episode is one chapter per
shot. Speech runs beside the pipeline: `src/speech.mjs` generates one take
per chapter through the provider, caches audio and character alignment by
request hash, mixes the narration bed and writes captions; `src/words.mjs`
turns the alignment into word onsets for reveals and source emphasis, reading
a shot's chapter take from where it starts relative to the shot. For a movie
document, `speech` generates the takes from the unresolved document, because
the anchors that place cuts and cues are resolved from those takes.
`src/code.mjs` pins source excerpts to the model's Git revision and gives a
source panel's typed text and markup; `src/text.mjs` holds the counting
rules for phrases, words and tokens; `src/style.mjs` the style's defaults;
`src/pictures.mjs` probes stills and clips and computes a picture's
rectangle; `src/layout.mjs` is the layout `check` measures for a movie
document that shows a picture or comes in by a reframe: each set its shots
use posed once, empty, on the renderer's page with a stub viewer, at the
output size, each slot's box, the box a picture gets there and whether the
slot is sized by what it holds, and the enlargement and view refusals
against the boxes that stay put
([ADR-009](adrs/STAGE/ADR-009-check-measures-a-sets-layout-before-speech.md));
it also turns a measured layout into the film's `reframes`, the slot boxes
each reframe moves its views between, which `check` and every renderer
session (on its own page, before its first frame) attach to the film for
the timeline
([ADR-010](adrs/STAGE/ADR-010-a-reframe-is-a-join-that-moves-a-views-box-and-fades-the-rest.md));
`src/export.mjs` is what the renderer serves from the model's export: the
files the viewer reads, each part's `model` and each marking's under the
manifest's `root` as the framework's export document defines them, each
refused by its field in the manifest when the export does not hold it, and
nothing else of the manifest (the piece inventory's sources are
provenance);
`src/easing.mjs` is the five-curve vocabulary;
`src/review-samples.mjs` and `src/review-pack.mjs` choose, from the
element states, and decode the frames a person reviews;
`src/provenance.mjs` reads a Git work tree's head and whether it is dirty,
and words it: `check`, `preview` and `render` print the project's and
Videomaker's own, `preview` and `render` reading them once before the first
frame and recording each head beside its dirt in the preview report, every
captured shot generation and the manifest, whose `releaseIssues` name a
dirty tree; the dirt is never a cache key
([ADR-015](adrs/PIPELINE/ADR-015-provenance-records-whether-each-tree-was-dirty.md)).

## Commitments

1. **A frame is a pure function of video time.** No wall clock, no state
   carried between frames, no dependence on posing order. The stage's
   components draw only the state a frame gives them, in one synchronous
   commit. Preview proves it by posing an instant, another, and the first
   again, and comparing pixels.
2. **The source is data.** It is validated completely before a browser
   opens, hashed for the shot cache and recorded in the manifest. The YAML
   formats refuse aliases, anchors, tags and merge keys; format 0.4 and the
   movie document close every field list so a misspelling is never silently
   dropped. A document's stage modules are bundled to draw the film, never
   run to read it.
3. **The template owns the screen**
   ([ADR-004](adrs/STAGE/ADR-004-the-stage-is-a-react-template-that-owns-the-screen.md)).
   Everything on a frame is drawn by a set and the elements in its slots;
   what a set marks as chrome stays above transitions and is masked by the
   proofs, and nothing else is. No film draws a progress indicator: a
   viewer's place in a film is the player's to show.
4. **The viewer is a separate product.** The stage mounts the bundle a
   caller selects, no more instances than one frame places views, leased
   to the view elements frame by frame (ADR-007), requires the API the
   movie needs (21, 28 for marks, highlights or a change of lens or up, 29
   for a clocked take) and refuses an older one when its first view mounts.
   The tool reaches the viewer only through its declared handle. A view on
   a clocked take is posed by restoring its frame's bank on the viewer's
   machine, and the viewer is held to the take: before the first frame each
   step is replayed on it and compared exactly with the record, and every
   frame's bank, at a mark the recorded one, is read back
   ([ADR-012](adrs/STAGE/ADR-012-a-view-on-a-take-is-posed-by-restoring-the-machines-bank.md)).
5. **Speech is measured, never assumed.** Timing that depends on the voice
   is read from the cached alignment. Narration is never truncated or
   stretched; a take that does not fit is refused with its measurement.
6. **Proofs are stated as tolerances and masks**, once, in `src/pixels.mjs`.
7. **Nothing is published by the tool.** Release fields left null block a
   release bundle and never default to an address.
8. **One resolved document is the seam after loading**
   ([ADR-006](adrs/SOURCE/ADR-006-yaml-episodes-and-movie-documents-load-into-one-resolved-document.md),
   amending [ADR-001](adrs/SOURCE/ADR-001-movie-document-and-chapter-narration.md)):
   one JSON Schema (`schema/machinome-movie-0.2.json`) both runtimes check,
   one set of shared fixtures (`fixtures/`) with their pinned resolutions,
   and the resolution written to `_build/movie-resolved.json` so what the
   film is produced from can be read.

## Movies declared in Python

A project can declare a movie in Python and evaluate it to the movie
document, `machinome-movie/0.2` ([Declaring a movie in Python](declaring-a-movie.md),
ADR-002, ADR-005); the renderer's reading of that document and the stage that
draws it are the Node side's. The `machinome_movie` package under `python/`
is the Python side of the movie document:

    movie.py in the project (Movie, Chapter, Shot, Loop, Take, Set, Element, ...)
        │  class creation: found by type, named by attribute, refused by name
        ▼                                         python/machinome_movie/movie.py
    compiled chapters (elements and shots in document form,
        │              parts, tokens and sets to check)
        │  evaluate(movie, name=, out=): opens the export's manifest and
        │  source revision and the emphasised excerpts; a Take's steps are
        ▼  made once by the framework's Sim and recorded   .../evaluate.py
    movie document, canonical JSON, with its stage block (and take block),
        │  checked against schema/machinome-movie-0.2.json   .../document.py
        ▼
    <movie dir>/_build/movie.json  →  the Node side and the project's stage module

- `names.py` holds the refusal type, the naming rules (an attribute's
  underscores become hyphens; a class's kind is its name as a slug) and JSON
  props; `text.py` the three counting rules (a phrase in the narration,
  words in a phrase, a token in an excerpt); `anchors.py` the narration and
  its symbolic anchors; `take.py` the takes and what they declare (the
  posed `Loop`; the clocked `Take` with its `Move`, `Trigger` and `Mark`
  steps, resolved at class creation to the framework's names, take seconds
  and marks), model time, and the resolution of a model's declaration paths
  to export names;
  `stage.py` the sets and slots (`Frame`, `Split`, the project's), the
  elements (`View` with its marks, the source panel, `Title`, `Picture`, the
  project's, with their `Action`s), the actions a cue performs and the
  joins (`Dissolve`, `Fade`, `Wipe`, `Slide`, `Reframe`); `movie.py` the chapter and movie trees; `project.py` and
  `__main__.py` the `[tool.machinome.movies]` table and the command line.
- A set is a layout and does not know what it holds; an element is content
  and does not know where it is placed. A project's set or element is a
  class naming the stage module that draws it; the document's stage block
  carries its slots, props and actions, from which the stage generates its
  components' types.
- Chapters check themselves and compile their elements and shots when their
  class is created, where every class is known; evaluation adds only what
  needs a file (part paths against the export, tokens against their
  excerpts, stage modules on disk, the model block) and is a pure function
  of the declarations and those files. Two evaluations are byte-identical.
- A clocked take is recorded, not computed (ADR-011): evaluation constructs
  the framework's `Sim` over the declared model once, makes the steps with
  its own requests and writes what they returned, verbatim, with the bank
  before the first step and at every mark and the identity the export
  publishes; the steps' `at`, the marks and the length are the exact sums
  of the declared durations, which both runtimes compare without a
  tolerance and Node reads rather than adds (ADR-016). `document.py` holds a take document to its export (identity,
  inputs, the bank's ids) and to the replay of its steps, the rule both
  runtimes share; `src/take.mjs` is the Node side of it, and the pose rule
  the frame reads (ADR-012).
- The schema is one file, `schema/machinome-movie-0.2.json`, shipped in the
  package through a link; the shared `fixtures/` pin what Python emits and
  every refusal both runtimes must make.

## What is changing

The declarative-python campaign (`workflow/ongoing/declarative-python-api.md`,
`docs/movie-document.md`) made the movie document the seam at the top of
the pipeline, a step and not a protocol by the pilot's ruling of
30 September 2026 (no format is a protocol before a release). Python
declarations in the project evaluate to `machinome-movie/0.2`, the commands
read it, and the React stage draws every film, a project's movie on its own
template and a YAML episode on the shipped paper sets. The curta-video
campaign adds machine takes: a clocked take is declared and recorded in
Python (`declare-a-take`, ADR-011), and the commands read it and pose it on
the viewer's machine, held to the record (`pose-a-take`, ADR-012). Running
machines' takes, the page element and the studio's live preview are later
steps of the same direction and are not built.
