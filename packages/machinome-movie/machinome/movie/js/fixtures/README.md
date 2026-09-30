# Shared fixtures

Fixtures both the Python suite and the JavaScript suite run, so the two
sides of the movie document cannot drift from each other. A fixture is added
once and paid for twice: a document one side does not handle fails that
side's suite.

- `documents/<name>.json` — valid `machinome-movie/0.1` documents. The Python
  suite asserts that evaluating the fixture movie of the same name
  (`python/tests/movies/<name>.py`) yields exactly this document (compare the
  parsed JSON; files are written with two-space indentation and a final
  newline). The Node suite asserts that it validates against
  `schema/machinome-movie-0.1.json`, passes the static checks, resolves
  against its takes to exactly `resolved/<name>.json`, twice identically,
  with every anchor on the frame grid.
- `takes/<name>/<chapter-id>.json` — the speech double: one per chapter whose
  anchors need a take (a chapter without spoken anchors may have one too). Its
  shape is the part of the speech cache record the resolver reads:

  ```json
  {"duration": 4.54,
   "alignment": {"characters": ["W", "a", …],
                 "character_start_times_seconds": [0, 0.06, …],
                 "character_end_times_seconds": [0.06, 0.12, …]}}
  ```

  `characters` spell the chapter's spoken narration (after
  `audio.replacements`) one code point each, times in seconds from the take's
  start, non-decreasing; `duration` is the take's length. The fixtures here
  give every character 0.06 s (`test/project-fixture.mjs`, `evenAlignment`)
  and a duration of the characters plus 0.1 s. The Node pipeline test
  installs a take as the speech command caches it: a silent WAV of
  `duration` at `_build/audio/<chapter-id>-<key16>.wav` beside a record with
  its checksum. A registered document whose anchors need a take this
  directory lacks fails the Node suite naming the file to add.
- `resolved/<name>.json` — the numeric episode the Node resolver produces
  from `documents/<name>.json` with `takes/<name>/`: format 0.4 shots with
  `start` and `end`, and `chapters`. Pinned by the Node suite, reviewed by
  hand when written; the Python suite does not read it.
- `invalid/<name>.json` — `{"name", "document", "must_mention": [...]}`: a
  document that must be refused, with the substrings the refusal names.
  Both suites iterate every file here. Each is refusable without a take:
  format, schema, a static rule (sets, fades, literal `until`, phrases in the
  written narration, marks, camera presets, the last model keyframe at the
  shot's `until`, duplicate ids), or the parts it names checked against its
  export when the export is in the repository. The document's `root`
  resolves from the fixture's own file, as a document's does from its file.
- `scripts/pin-resolved.mjs NAME...` writes `resolved/<name>.json` from the
  document and its takes, for a person to review before committing; never
  regenerate a pin to make a failing test pass.

`manifest.json` indexes the valid documents so a new fixture is registered
once and missed by neither side.

## Refusal words

The substrings are locations, vocabulary and field names, chosen to be stable
across languages, never a runtime's type names, quoting or number
formatting. Both runtimes name:

- the chapter and the shot by id, and an anchor's field by its path inside
  the shot: `until`, `camera[1].at`, `simulation.from`,
  `simulation.keyframes[2].seconds`, `overlays[0].to`, `code.typing[0].from`,
  `pictures[0].view[1].at`;
- the phrase or mark as written, and the vocabulary word of the rule:
  `absent`, `ambiguous`, `at or before its start`, `first shot`,
  `last shot`, `shot id`, the set's name and `code`;
- for a schema refusal, the field's name (an unknown `narration` on a shot is
  refused naming `narration`).

The Node wording, for reference (`src/movie.mjs`):

| fixture | refusal |
|---|---|
| unknown format | `Unsupported movie format: machinome-movie/9.9; this Videomaker reads machinome-movie/0.1` |
| unknown set (`set-not-drawn`) | `Unknown set: stage (shot wheel in chapter opening); a set is paper, paper-split or source-only` |
| `paper` with code | `Set paper has no source panel: shot wheel (chapter opening) has code; use paper-split or source-only` |
| `paper-split` without code | `Set paper-split needs code: shot wheel (chapter opening)` |
| absent phrase | `Spoken phrase is absent from the narration of chapter opening: the saw (until of shot wheel)` |
| ambiguous phrase | `Spoken phrase is ambiguous in the narration of chapter opening: turns (until of shot wheel)` |
| unknown mark (`mark-misspelled`) | `Unknown mark: pull_stat (simulation.from of shot wheel in chapter opening)` |
| unknown camera preset | `Unknown camera preset: widest (camera[0] of shot wheel in chapter opening)` |
| last keyframe before the end | `Model keyframes must end at the shot's until: shot wheel (chapter opening) has its last keyframe at 1 and until 2` |
| unknown assembly path (needs the export) | `Missing assembly path: Beam/Plonk (highlight[0] of shot whole in chapter only)` |
| `until` at the start | `Shot wheel ends at or before its start: until 0 (chapter opening)` |
| `fadeIn` on a later shot | `fadeIn is accepted only on the film's first shot: shot hold (chapter opening)` |
| `fadeOut` on an earlier shot | `fadeOut is accepted only on the film's last shot: shot wheel (chapter opening)` |
| narration on a shot | `Unknown field: narration (chapters/0/shots/0)` |
| duplicate shot id | `Duplicate shot id: wheel (chapter closing)` |
