## 0. Preconditions

- [ ] 0.1 The orchestrator, as the campaign's ratification gate, reviews this
  proposal after the report: chapters (D2), one take per chapter with today's
  keys (D3), anchors and their resolution (D6), sets (D7), the schema and its
  in-repository validator instead of a dependency (D9), the resolved file
  (D10) and the deviations from the contract page (D11).
- [ ] 0.2 Base: branch `movie-document` from `declarative-python` at
  `6e86728`. The YAML identity pins of 1.4 are computed on that source before
  any source change; record the base suite in `evidence.md`.

## 1. Red tests (written before any implementation; record each failure)

- [ ] 1.1 Fixtures: `fixtures/documents/two-chapters.json` (two chapters, four
  shots, every anchor form, marks with and without `plus`, a `paper-split`
  shot with code and emphasis, a spoken reveal, a highlight, an annotation, a
  still whose view key is anchored, a dissolve, a wipe, fades, a shot without
  `direction`) and `fixtures/documents/minimal.json` (required fields only: no
  `style`, `credits` or `release`), registered in `fixtures/manifest.json`; their takes under
  `fixtures/takes/<name>/<chapter>.json`; invalid documents under
  `fixtures/invalid/` for: unknown format, unknown set, `paper` with code,
  `paper-split` without code, an absent phrase, an ambiguous phrase, an
  unknown mark, a literal `until` at the shot's start, `fadeIn` on a later
  shot, `fadeOut` on an earlier shot, narration on a shot, a duplicate shot
  id; `fixtures/README.md` states the take shape, the field-path convention
  and the refusal words.
- [ ] 1.2 `test/movie-document.test.mjs` (pure): the schema's keywords are the
  validator's; each manifest document validates, resolves against its takes
  to exactly `fixtures/resolved/<name>.json` (written from the first correct
  resolution and reviewed by hand), twice identically, with every resolved
  anchor on the frame grid; each invalid fixture is refused with every
  `must_mention` substring; anchor arithmetic (`spoken`, `spokenEnd`, `plus`,
  replacements, snapping), marks with `plus`, a picture view key anchor, the
  three sets and their defaults, the missing-take refusal naming the chapter,
  a phrase the take lacks or repeats, an anchor outside its shot, an anchored
  `until` at or before its start, word timing from the chapter take at the
  shot's offset, and the YAML chapter mapping. A registered document whose
  anchors need takes that `fixtures/takes/<name>/` lacks, or whose pinned
  resolution is missing, fails naming the missing file.
- [ ] 1.3 `test/movie-pipeline.test.mjs` (Chromium, FFmpeg, viewer double):
  the two-chapter document in the fixture project is refused before its takes
  exist, naming the chapter; with the fixture takes installed it loads, writes
  `movie-resolved.json` equal to the pinned resolution, `speech` (no
  generation) places one take per chapter and writes captions, `preview`
  passes, `render` writes an MP4 with the expected frame count, dimensions and
  audio and the SRT beside it; `fetch` fails the test if called and no key is
  in the environment. The speech command path on a document with every take
  cached makes no request.
- [ ] 1.4 The YAML identity test in `test/movie-pipeline.test.mjs`: a three-shot
  0.4 YAML episode of the fixture project loads, and its take file names,
  speech records, captions, word timing and every output frame's request
  (SHA-256 of all, five whole frames) equal the values computed on the base
  commit. Green by design before and after; record it green on the base.
- [ ] 1.5 Move the API 28 viewer double of `test/render.test.mjs` into
  `test/viewer-double.mjs`, imported by both tests, with no change to it.

## 2. Implementation

- [ ] 2.1 `schema/machinome-movie-0.1.json` and `src/schema.mjs` (D9).
- [ ] 2.2 `src/chapters.mjs` (D2); `src/movie.mjs`: format, schema, static
  checks (D6–D8), take reading (D5), `resolveMovie` (D6, D7, D10), the loader
  and the resolved file.
- [ ] 2.3 `src/episode.mjs`: dispatch (D1), YAML chapters (D2), validation of
  chapter-owned narration and chapter offsets, the whole-frame tolerance
  (D12); `src/shot-cache.mjs` likewise.
- [ ] 2.4 `src/speech.mjs` one take per chapter, lazy key (D3, D4);
  `src/words.mjs` word timing from the chapter take (D2); `src/code.mjs`,
  `src/pictures.mjs`, `src/render.mjs` resolve paths against the root (D1).
- [ ] 2.5 `bin/videomaker.mjs`: takes generated from the unresolved document
  for `speech` and `build` (D4); usage names a movie document.
- [ ] 2.6 Records: ADR-001 under `docs/adrs/SOURCE/`, promoted to Accepted at
  archive and listed in `docs/adrs/README.md`; `docs/architecture-overview.md`;
  `README.md` and `docs/FORMAT.md` say the commands accept a movie document and
  point at `docs/movie-document.md`; `docs/movie-document.md` gains its
  implementation notes (D11); `CHANGELOG.md` with an `Unreleased` section and
  this change's bullet.
- [ ] 2.7 `npm test` green except a named environmental failure, if any;
  record every red run and the green run in `evidence.md`; sync the baseline
  specs and archive.

## 3. Human review (not claimed by automation)

- [ ] 3.1 The pilot judges the film produced from a document in cycle C; this
  change proves resolution, frames and encodes, not how the film reads.
- [ ] 3.2 The open questions of design.md: the quick render at another frame
  rate, and a maintained schema validator.
