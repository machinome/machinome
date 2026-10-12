## Why

The declarative-python campaign (`workflow/ongoing/declarative-python-campaign/plan.md`)
commissions one film: *Cut and Advance*, specified in the Leonardo project at
`videos/cut_and_advance/spec.md`, about 100 seconds in five chapters, produced
from a Python source on today's renderer and inspected by the pilot. Its
Python declarations evaluate to a JSON document, `machinome-movie/0.1`,
whose contract is the draft `docs/movie-document.md`. This change is cycle A
of the campaign: the Node tool must load that document. Without it the film
cannot be produced, whatever the Python side emits.

The film needs three things the YAML episode cannot express, each named in
its spec's "What the film must prove" table:

- **One continuous take per chapter.** "Chapter narration as one continuous
  take; shots cut on spoken phrases" (every chapter). Today narration belongs
  to a shot and is synthesized per shot, so a paragraph spanning a cut is two
  takes with a restart at the cut, and an author must move every cut by hand
  after each new take.
- **Spoken anchors.** "`spoken`, `spokenEnd`, `plus` on shot ends, camera keys,
  cue starts and ends" (`question`, `coupling`, `pawls`, `shaft`): the
  `coupling` shot ends where the narrator begins "A crank"; its highlight moves
  to the crankshaft on the spoken word "crankshaft"; the `still` shot's push
  ends half a second before "Explore". Today every such instant is a number
  copied from a measured take and revised by hand after every regeneration.
- **Marks.** "Marks on the loop take resolved to model seconds, with easing
  into a hold" (`pawls`): the pull starts at mark `pull_start` (436), the
  return at `return_start` (438) with `out` easing, keyed on the spoken "On
  the return".

The film also names the `paper` and `paper-split` sets (`wheel`, `coupling`),
which are today's model and split layouts under the names the document uses.

## What Changes

- `check`, `speech`, `preview`, `render` and `build` accept a movie document
  (`.json`) wherever they accept an episode (`.yaml`). A YAML episode loads as
  today.
- Both sources produce one internal episode: the format 0.4 shape the rest of
  the tool already consumes, plus `chapters`. A YAML episode becomes one
  chapter per shot with that shot's narration and speech offset, so its
  frames, its speech cache keys and its captions are unchanged.
- One narration take per chapter, placed at the chapter's start plus its
  speech offset, which must fit the chapter. Captions come from the chapter's
  alignment. Spoken reveals and source emphasis read the shot's chapter take.
- Spoken anchors (`spoken`, `spokenEnd`, optional `plus`) on a shot's `until`,
  camera keys, model keyframes, cue starts and ends and typing cues, resolved
  from the cached take and snapped to the output frame grid; marks (`mark`,
  optional `plus`) wherever model seconds are taken. Refusals name the
  chapter, the shot, the field and the phrase or mark.
- Sets `paper`, `paper-split` and `source-only`, mapped to today's three
  layouts; `fadeIn` and `fadeOut` only on the film's first and last shots.
- `check`, `preview` and `render` refuse a document with spoken anchors whose
  takes are not cached, naming the chapter and asking for `speech`; each
  writes the resolved document to `<root>/_build/movie-resolved.json` before
  any capture.
- `schema/machinome-movie-0.1.json`, the JSON Schema of the unresolved
  document, checked before any semantic rule.
- Shared fixtures under `fixtures/` that this suite and the Python suite both
  iterate: valid documents with their take doubles and pinned resolutions,
  and invalid documents with the words each refusal must contain.

## Capabilities

### New Capabilities

- `movie-document`: loading a `machinome-movie/0.1` document, chapters with
  one take each, spoken anchors and marks, sets, the schema, the resolved
  document and the shared fixtures.

### Modified Capabilities

- `educational-video-production`: the screenplay requirement admits a movie
  document beside the YAML episode (narration read beside the shots of its
  chapter), and the narration requirement measures a take against its
  chapter, which for a YAML episode is its shot.

## Impact

New: `src/movie.mjs` (document loading, static checks, anchor resolution),
`src/chapters.mjs` (a shot's chapter, narration and take offset),
`src/schema.mjs` (a validator for the schema's keywords),
`schema/machinome-movie-0.1.json`, fixtures, tests, the first ADR
(`docs/adrs/SOURCE/ADR-001-movie-document-and-chapter-narration.md`),
`CHANGELOG.md`. Changed: `src/episode.mjs` (dispatch, chapters, validation of
chapter-owned narration), `src/speech.mjs` (one take per chapter),
`src/words.mjs` (word timing from the chapter take), `src/code.mjs`,
`src/pictures.mjs`, `src/render.mjs` (relative paths resolve against the
document's root), `src/shot-cache.mjs` (whole-frame test tolerant of floating
error), `bin/videomaker.mjs`, `README.md`, `docs/FORMAT.md`,
`docs/architecture-overview.md`, `docs/adrs/README.md`, `fixtures/README.md`.
`src/film.js`, `src/film.html`, `src/timeline.mjs`, the viewer and the
Leonardo project are unchanged. Changing any hashed source module
invalidates existing shot caches once, as every source change does.

## Non-goals

The Python declarations (cycle B, `declarative-movie`), the film itself
(cycle C, project work), the React stage and project-defined sets, takes from
running or clocked scenarios, several narrators, music, live preview. No
anchor form beyond the contract's (no "end of the narration" anchor: the
whole narration or its last words spoken once serve, see design D6). No
change to YAML episode formats 0.2 to 0.4. No publication, push or paid
request.
