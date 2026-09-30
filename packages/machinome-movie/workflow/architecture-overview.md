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

    source: YAML episode, or movie document (machinome-movie/0.1)
        │  load; a document: schema, static checks,     src/episode.mjs
        │  anchors resolved from cached takes           src/movie.mjs, src/schema.mjs
        │  validate against the export and project
        ▼
    episode object (numeric times, format 0.4 shape, chapters)
        │  frameAt(e, t): pure                          src/timeline.mjs
        ▼
    frame data: view, model time, hidden layers, overlays, annotations,
                highlight, code, picture, transition
        │  window.film.setFrame(frame)                  src/film.html, src/film.js
        ▼
    the film page in headless Chromium, the viewer mounted on-demand
        │  screenshot, readback checks, pixel proofs    src/render.mjs, src/pixels.mjs
        ▼
    PNG frames per shot, cached by content               src/shot-cache.mjs
        │  FFmpeg
        ▼
    rehearsal.mp4 + rehearsal.srt + manifest + review packs

Narration belongs to chapters (`src/chapters.mjs`): a movie document groups
shots into chapters of one narration each; a YAML episode is one chapter per
shot. Speech runs beside the pipeline: `src/speech.mjs` generates one take
per chapter through the provider, caches audio and character alignment by
request hash, mixes the narration bed and writes captions; `src/words.mjs`
turns the alignment into word onsets for reveals and source emphasis, reading
a shot's chapter take from where it starts relative to the shot. For a movie
document, `speech` generates the takes from the unresolved document, because
the anchors that place cuts and cues are resolved from those takes. `src/code.mjs`
pins source excerpts to the model's Git revision; `src/pictures.mjs` probes
stills and clips; `src/easing.mjs` is the five-curve vocabulary;
`src/review-samples.mjs` and `src/review-pack.mjs` choose and decode the
frames a person reviews.

## Commitments

1. **A frame is a pure function of video time.** No wall clock, no state
   carried between frames, no dependence on posing order. Preview proves it
   by posing an instant, another, and the first again, and comparing pixels.
2. **The source is data.** It is validated completely before a browser
   opens, hashed for the shot cache and recorded in the manifest. The YAML
   formats refuse aliases, anchors, tags and merge keys; format 0.4 closes
   every field list so a misspelling is never silently dropped.
3. **The viewer is a separate product.** The page mounts the bundle a caller
   selects, requires the API it needs (21, or 28 for cues that point at
   parts, highlight or change the lens) and refuses an older one on mount.
   The tool reaches the viewer only through its declared handle.
4. **Speech is measured, never assumed.** Timing that depends on the voice
   is read from the cached alignment. Narration is never truncated or
   stretched; a take that does not fit is refused with its measurement.
5. **Proofs are stated as tolerances and masks**, once, in `src/pixels.mjs`.
6. **Nothing is published by the tool.** Release fields left null block a
   release bundle and never default to an address.

7. **The movie document is the seam at the top of the pipeline for this step**
   ([ADR-001](adrs/SOURCE/ADR-001-movie-document-and-chapter-narration.md)):
   one JSON Schema (`schema/machinome-movie-0.1.json`) both runtimes check,
   one set of shared fixtures (`fixtures/`), and a resolution written to
   `_build/movie-resolved.json` so what the film is produced from can be read.

## Movies declared in Python

A project can declare a movie in Python and evaluate it to the movie
document ([Declaring a movie in Python](declaring-a-movie.md), ADR-002); the
renderer's reading of that document is the Node side's. The
`machinome_movie` package under `python/` is the Python side of the movie
document:

    movie.py in the project (Movie, Chapter, Shot, Loop, ...)
        │  class creation: found by type, named by attribute, refused by name
        ▼                                         python/machinome_movie/movie.py
    compiled chapters (shots in document form, parts to check)
        │  evaluate(movie, name=, out=): reads the export's manifest and
        ▼  source revision only                    python/machinome_movie/evaluate.py
    movie document, canonical JSON, checked       python/machinome_movie/document.py
        │  against schema/machinome-movie-0.1.json
        ▼
    <movie dir>/_build/movie.json  →  the Node side

- `names.py` holds the refusal type and the naming rule (an attribute's
  underscores become hyphens); `anchors.py` the narration and its symbolic
  anchors; `take.py` the `Loop` and what it declares, model time, and the
  resolution of a model's declaration paths to export names; `stage.py` the
  three sets, the view and source-panel elements, actions and joins;
  `movie.py` the chapter and movie trees; `project.py` and `__main__.py` the
  `[tool.machinome.movies]` table and the command line.
- Chapters check themselves and compile their shots when their class is
  created, where every class is known; evaluation adds only what needs the
  export (part paths, the model block) and is a pure function of the
  declarations, the manifest and the revision. Two evaluations are
  byte-identical.
- The schema is one file, `schema/machinome-movie-0.1.json`, shipped in the
  package through a link; the shared `fixtures/` pin what Python emits.

## What is changing

The declarative-python campaign (`workflow/ongoing/declarative-python-api.md`,
`docs/movie-document.md`) made the movie document the seam at the top of
the pipeline for this step, a step and not a protocol by the pilot's ruling
of 30 September 2026 (the stage will replace its shape without preserving
it, and no format is a protocol before a release): Python declarations in the project evaluate to it,
YAML episodes load into its resolved shape, and narration moved to the
chapter with anchors resolved against the take. The React stage that
replaces the fixed film page, takes recorded from running and clocked
scenarios, and the studio's live preview are later steps of the same
direction and are not built.
