## Context

`bin/videomaker.mjs` runs `speech` on a movie document in two steps:

1. `generateMovieTakes(source)` (`src/movie.mjs`): `pendingMovie` reads the
   document with `readMovie`, which parses it and runs `checkMovie(doc)`
   without the export's manifest (format, schema and the static rules), and
   `generateTakes` (`src/speech.mjs`) checks the audio settings
   (`checkAudio`) and then, chapter by chapter, reuses a verified cached
   take or reads the key and requests one from the provider (`ensureTake`).
2. `loadEpisode(source)`, which for a document is `loadMovie`: the whole
   load, every refusal of which is made here, after the takes were bought.

`build` without `--silent` runs the same first step on the same line. The
order was decided by the `movie-document` change (its design D4, "Speech on
the unresolved document"): speech needs only the narration, so it generates
from the unresolved document with "format, schema and static checks passed,
nothing resolved". ADR-001 (decision 5) asks that everything refusable
without a take be refused before `speech` is needed; the static rules were,
but the load's checks against the project have only ever run after
generation, and they have grown since (ADR-019's recorded revision, the
take's identity of `take-identity`).

`loadMovie` makes its checks in this order (line references are to
`src/movie.mjs` at e9b08f9):

| step | what it checks | needs a take? |
|---|---|---|
| 1. `readMovie` | JSON, format, schema, `checkMovie(doc)` without the export, the root | no (already before generation) |
| 2. the manifest | `realpath` of `model.manifest` (a missing export), its JSON | no |
| 3. `exportSource`, `pinnedRevision` | the export's `source` record, the pin against `source.revision` (ADR-019) | no |
| 4. `checkMovie(doc,{manifest,sources})` | layers, highlighted and marked parts against the export; emphasised tokens against the excerpts' files; a take's `identity`, step inputs and initial bank against the export's `clocked` block | no |
| 5. repository and modules | the project repository at the root, the root inside it, each stage module present and inside it | no |
| 6. the cached takes | `missingTake` for a chapter with spoken anchors and no take | the take itself |
| 7. `resolveMovie` | anchors against the takes' alignments, then `checkResolved` and `recordCrossings` on the resolved times | yes |
| 8. `checkProject(film,manifest)` | a running `program`; a loop document on a clocked export; a loop whose length is not `expectedDurationSeconds`; a take document on an export with no clocked machine; the model duration; the output's width, height and rate, even dimensions; **a whole number of frames**; the cameras | only the frame count: it reads `output.durationSeconds`, which resolution writes from the takes; every other check reads fields resolution copies unchanged (`model`, `output.width`, `height`, `fps`, `cameras`) |
| 9. evidence | each `evidence` file is read | no |
| 10. `loadSourceCode` | each excerpt's file, inside the project, a `.py`, a full revision, its bytes equal to the file at the pinned revision (`Source differs from pinned model revision: <path>`), its line range, not empty | no |
| 11. `loadPictures` | each still and clip: entry, extension, inside the repository, one picture or a probed clip | no |
| 12. `checkFilm` | a token typed before it is spoken, a clip long enough for its cue, the camera's up at every output frame | yes: all on resolved times |

So the refusals that need no take are steps 1 to 5, step 8 without the frame
count, and steps 9 to 11. The Curta's present refusal is step 10.

## Goals / Non-Goals

Goals: on a movie document, `speech` and `build` without `--silent` raise
every refusal of steps 1 to 5, 8 (without the frame count) and 9 to 11
before the first take is requested, with the load's words and in the load's
relative order; nothing else changes. Non-goals: those of the proposal.

## Decisions

### D1. The line is the load's two halves

The load has a half that holds the document against its project (steps 1
to 5 and 8 to 11: it reads the document, the export, the excerpts, the
stage modules, the evidence and the media) and a half that holds the
resolved film (steps 7 and 12 and the frame count: it judges times
resolved from the takes). The first half is made before generation; the
second stays after it. In a document with spoken anchors every time from
the first anchored chapter on depends on a take, since chapters play end
to end; a check of the second half that in some document judges only
literal times (a transition on the film's first shot, model keys written
as numbers that run back, the frame count of a document with no anchor) is
still made on the resolved film, after generation. Splitting the
resolution by which values happen to be literal would be a new check, not
the load moved; no film needs it.

### D2. The early load lives in `src/movie.mjs`, inside `generateMovieTakes`

Steps 2 to 5 move, unchanged, out of `loadMovie` into one function,
`openMovie(file)`, which runs `readMovie` and then them, and returns what
`loadMovie` goes on with (the document, its paths, the manifest and its
path, the export's source, the repository). `loadMovie` calls it first and
continues at step 6 exactly as before, so `check`, `preview`, `render`,
`build` and `live` load in the same order with the same words.

A second function, `checkBeforeTakes(opened)`, runs on the unresolved
document the functions `loadMovie` runs at steps 8 to 11, in that order,
each with the fields `loadMovie` gives it: `checkProject(doc, manifest)`,
the read of each evidence file through the root, `loadSourceCode` with the
document's `sourceCode` and `model` and the root and repository, and
`loadPictures` with `source: 'movie'`, the document's `stills` and `clips`
and the same paths (as `check` already calls the last two before its load,
for the layout). It writes nothing.

`generateMovieTakes(file)` becomes: `openMovie`, `checkBeforeTakes`, then
`generateTakes` on the pending chapters as before. Generation of a
document's takes therefore cannot run without the checks, the in-process
callers (tests) get them too, and `bin/videomaker.mjs` changes only its
comment. `pendingMovie` stays for the tests that compute a take's key.

`checkProject` makes its frame count only on a resolved film: `if
(film.resolved)`. Every resolved film carries `resolved: true`
(`resolveMovie` writes it first), and an unresolved document cannot,
since the schema's top-level field list is closed and has no `resolved`;
in `loadMovie` it is called on the resolved film as before, so its order
of checks there is unchanged.

### D3. What stays the same, and the one order that moves

- Every refusal is made by the code that made it, so its words are the
  same; the test asserts each line literally.
- `loadMovie`'s order is unchanged (D2), and so are `check`, `preview`,
  `render` and `live`, which never generate.
- After the checks, `speech` runs as before: `generateTakes` (its audio
  settings check first, then each missing take), the whole load (the
  take-free half made a second time, then the takes, the resolution and the
  resolved checks), the summary line, word timing, fit, captions and mix. A
  refusal after generation still leaves the takes cached.
- What moves is only the take-free half of the load, ahead of generation.
  Since `checkAudio` is generation's first step, a document that both fails
  a take-free check of the load and lacks a supported provider, model,
  voice or output format is now refused for the load's fault first (before,
  for its audio settings). Both are refused before any request either way.
- The YAML episode path is not touched: `speech` on a YAML episode already
  runs `loadEpisode`, its whole load, before `speech(e, {generate: true})`
  requests anything, and `generateMovieTakes` serves only `.json` sources.
- `check`'s own refusals before its load (the stage bundle and its type
  check, the measured layout and the picture enlargements) are `check`'s,
  not the load's: `speech` never made them, before or after generation,
  and does not now.

The cost: on a document that passes, the take-free half runs twice, so
each excerpt is read at its revision (`git show`) and each picture probed
(`ffprobe`) once more, a fraction of a second against a paid request.

### D4. The capability is `movie-document`

`movie-document`'s requirement "A chapter's narration is one take" owns
what `speech` does on a document and when: "`speech` SHALL generate one
take per chapter from the narration alone, before anything in the document
is resolved". The change modifies that requirement: generation comes after
the load's take-free checks and before resolution. Its "What a document
names is checked before any take" lists the static rules and "Anchors are
resolved only from cached takes" belongs to `check`, `preview` and
`render`; `educational-video-production`'s revision requirement already
says the commands refuse "when they load the film", and `declarative-movie`
is the Python side. None of them changes.

### D5. The proof: the takes layer in process, and the command line once

The innermost layer that can fail is the takes layer, in process.
`test/pipeline/movie-pipeline.test.mjs` already has the provider double the
proof needs ("speech generates one take per chapter from the unresolved
document, and only once"): it replaces `globalThis.fetch` under a
placeholder key, answers each request with the fixture take of its
chapter (`fixtures/takes/<movie>/<chapter>.json`) and counts the requests.
Its take lookup is generalized by movie name, so the same double serves a
`count` copy; the takes it answers with are the fixture's, in the
document's own audio format. Since D2 puts the checks inside
`generateMovieTakes`, the proof calls it on copies of the fixture project
(`fixtureMovie`, no takes installed), one fault at a time, and asserts that
it rejects with the load's refusal (literal) and that `requests.length` is
0:

- `tour` (three chapters): the export's `source.revision` changed (step
  3); the export's directory removed (step 2, the bare `ENOENT` of its
  `realpath`); a line appended to `models/seesaw.py` after the copy's
  commit, outside the excerpt's lines (step 10, `Source differs from pinned
  model revision: models/seesaw.py`); a `program` block in the manifest
  (step 8);
- `count` (one chapter): the export's `clocked.identity` changed (step 4).

Before the change the same calls record one request per chapter (three,
or one for `count`) before the same refusal: the red. The passing case, a
valid document whose takes are requested one per chapter, is the existing
test, which now runs the checks too.

The command line is proved with the existing `NO_FETCH` import of `cli()`,
whose child has an empty key and a `fetch` that throws "A test attempted a
network request". On the changed-revision `tour` copy, `speech` and, once,
`build` exit 1 and print the load's refusal line, asserted literally, and
neither the network-request error nor the missing-key refusal ("No
ElevenLabs key"), which the command reaches first when it tries to buy
before the load (the red; the evidence records which of the two it
prints).

The mutation: with `generateMovieTakes` back to `pendingMovie` alone, the
in-process assertions and the command-line assertion are red again; the
output is recorded.

## No ADR

No structural decision is made. ADR-001 decided (its decision 5) that
everything refusable without a take is refused before `speech` is needed;
this change makes the speech command meet that for the load's checks
against the project, which the `movie-document` design D4 had left after
generation. The load, its order, the documents, the cache and the pipeline
keep their shape: one function of the load is split in two and its first
half is also called before generation. The record is this design and the
modified requirement.

## Alternatives rejected

- **Move steps 8 to 11 ahead of the takes inside `loadMovie`.** One load,
  no second run, but `check`, `preview` and `render` would name a
  take-free fault before a missing take where they name the take today: an
  order the finding does not ask to change.
- **Steps 1 to 5 only** (the load up to the takes, the record's literal
  "load and refuse first"). The Curta's present refusal (step 10), a
  running program (step 8) and a missing evidence file would still be
  refused after the purchase.
- **Resolve with placeholder takes to check the resolved half early.** A
  placeholder's times are not the take's: refusals made on them would not
  hold for the recorded narration, and refusals the recorded one causes
  would be missed.
- **Load the film whole before generating when no chapter needs a take.**
  Complete for such documents, and a second path for a case no film has.
- **Call the checks from `bin/videomaker.mjs`.** The command line would
  hold load logic, and an in-process caller of `generateMovieTakes` could
  still buy takes for a refused document.
