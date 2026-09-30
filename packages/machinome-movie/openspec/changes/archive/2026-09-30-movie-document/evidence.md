# Implementation evidence

## Authority and scope

Cycle A of the declarative-python campaign, on branch `movie-document` (worktree
`WTs/movie-document`), cut from `declarative-python` at `6e86728`. Planning
commit `30b138d`, ratified by the orchestrator's review (the campaign's gate
under the pilot's delegation) with one correction: the closed `audio` field is
`voiceLabel`, not `label` (design D9, amended). During implementation the
orchestrator relayed the Python side's design and its invalid fixtures; the
allowances of D14 and the checks of D15 come from those messages. No viewer,
project or Leonardo file was touched; nothing was pushed, published or paid
for; no network request was made. Integration into `declarative-python` is
the pilot's.

## Base

`npm test` on the base source (`6e86728`), before any change: 189 tests,
188 pass, 1 fail, 5 min 37 s. The failure is
`every incremental PNG equals a separately cold film across the first
reused-shot gap` (`test/incremental-rendering.test.mjs`): global frame 1's PNG
hash differed between the incremental and the cold film. Run alone right
after, it passed (9.0 s). It is an existing, intermittent pixel test of the
shot cache, unrelated to this change; recorded here as an environmental
flake, not fixed.

## The YAML identity pins, computed on the base

Before any source change, `test/project-fixture.mjs` (the fixture project:
one deterministic commit of `models/fixture.py`, whose hash is
`ef62273f3a1c8f435f208ec027d18fba5dbb0b5b` on every run, and a three-shot
format 0.4 YAML episode with a spoken reveal, source emphasis, a
pronunciation alias, a per-shot speech offset, a dissolve and fades) was
written, and a scratch script loaded that episode with the base
`loadEpisode`, installed a take per shot at the base `speechCacheEntry` path
(silent WAV and record, alignment 0.05 s a character), ran the base
`prepareWordTimingForCommand` and `speech(e, {generate: false})` with `fetch`
replaced by a throwing function, and printed the take file names
(`hook-11814c00c2ad9784.wav`, `coupling-7126e3bf3e18a59a.wav`,
`closing-f6d9fbde9278b628.wav`), the speech records, the captions, the word
timing, the SHA-256 of all 70 `frameAt` requests
(`42fa6bae9d8feab7a7faae5ea4b9d4bd22abd7f48ebe910f631ad438f91767fc`) and five
whole frames (0, 13, 27 in the dissolve, 41, 66 in the fade-out). Two runs
printed identical values. They are written literally in
`test/movie-pipeline.test.mjs` (`BASE`), which after the change also asserts
that the loaded episode's `chapters` are one per shot. Green after the change.

## Red / green

Red, before implementation (no source file of this change existed):

- `node --test test/movie-document.test.mjs` and
  `node --test test/movie-pipeline.test.mjs`: both fail to load,
  `ERR_MODULE_NOT_FOUND: Cannot find module .../src/movie.mjs`.

First run after implementing `src/schema.mjs`, `src/chapters.mjs`,
`src/movie.mjs` and the changes to `episode`, `speech`, `words`, `code`,
`pictures`, `render`, `shot-cache`: `movie-document.test.mjs` 13 of 15 pass.
The two failures were the fixtures, not the code: no pinned
`fixtures/resolved/minimal.json` yet, and the first two-chapter fixture put a
picture view key (`spokenEnd "the wheel." plus 0.1`) past its shot's end,
refused as `Anchor … of pictures[0].view[1].at in shot wheel (chapter drive)
falls outside the shot`. The key was moved to `plus -0.1`; the take doubles'
character step was changed from 0.05 s to 0.06 s after measuring that at
0.05 s two anchors fell exactly on half a frame (13.5 and 56.5 frames), where
snapping would depend on floating-point rounding (at 0.06 s the closest is 0.1
frame from a half). The resolutions were then written and reviewed by hand
against the characters' times (every shot's start and end, every anchored key
and cue, marks with `plus`, chapter offsets; D6's arithmetic by hand for each).
`movie-pipeline.test.mjs` passed on its first run (its two tests at the time,
28 s); the provider-double test was added after, with its red shown below.

Each new test's specific failure, shown by a targeted mutation of the
implementation, each reverted at once:

| mutation | result |
|---|---|
| `validateEpisode` whole-frame test back to `Number.isInteger` | `a duration on the frame grid …` fails: `Video duration must be a whole number of frames` |
| `outputShotUnits` back to `Number.isInteger` | same test fails: `Frame count is not integral` |
| `takeOffset` without the `chapter.start === shot.start` shortcut | the YAML identity test fails (word timing differs from the base pin) |
| no snapping in `resolveMovie` | `two-chapters resolution differs from fixtures/resolved/two-chapters.json` |
| take file named by `e.shots[i].id` instead of the chapter's | pipeline: `/^drive-[0-9a-f]{16}\.wav$/` does not match |
| `generateTakes` not allowed to generate | provider-double test: `Missing speech for drive; run the speech command first` |
| word timing offset = the chapter's offset, not `takeOffset` | `Emphasis clears after shot coupling ends` in the word-timing test |
| no settling of a shot-local anchor onto 0 or the duration | first no test failed; the test `an anchor on a cut made of literal durations lands exactly on it` was added (0.1 + 0.2 = 0.30000000000000004), and with the mutation it fails: `Anchor spoken "A" of overlays[0].from in shot three (chapter opening) falls outside the shot` |
| (D15) no camera preset check | 2 fail: the invalid-fixture test and the checks test |
| (D15) no last-keyframe check | 2 fail: same two tests |
| (D15) annotation parts not checked against the export | the checks test fails |

The D15 checks were written together with their fixtures and tests after
the orchestrator relayed the Python side's invalid fixtures; their red is the
mutation rows above. All seven of the Python side's invalid fixtures
(`keys-without-end`, `phrase-absent`, `phrase-repeated`, `unknown-camera`,
`unknown-mark`, `unknown-part`, `unknown-set`), read from its worktree without
changing it, are refused by this side with every `must_mention` substring
(`unknown-part` through `checkMovieExport` against the Python fixture
project's export), and its two documents (`minimal`, `tour`) pass the schema
and the static checks. They are not in this branch; the merge brings them.

No provider was called. The pipeline tests replace `fetch` with a function
that fails the test and remove `ELEVENLABS_API_KEY`; the command-line runs are
child processes with an empty key and `fetch` replaced through `--import`.
The provider-double test answers `fetch` in process with the fixture takes and
sets a placeholder key the double never sends anywhere; it asserts one request
per chapter with the chapter's narration and its neighbours' as context, and
none on a second run.

## Green

After implementation, before D15: `npm test`, 208 tests, 208 pass, 0 fail,
5 min 54 s.

After D15, the final source and tests: `npm test`, 209 tests, 209 pass,
0 fail, 6 min 7 s (189 existing, 17 in `movie-document.test.mjs`, 3 in
`movie-pipeline.test.mjs`; the new pipeline tests take about 30 s together).
Nothing is memoized, so every run is cold. The base's intermittent
incremental-rendering test passed in both runs after the change.

## What changed

- `schema/machinome-movie-0.1.json` (new): the unresolved document's schema.
- `src/schema.mjs` (new): the validator of the schema's keywords (D9).
- `src/chapters.mjs` (new): `chaptersOf`, `chapterOf`, `narrationOf`,
  `takeOffset`, `shotChapters` (D2).
- `src/movie.mjs` (new): `checkMovie` (format, schema, static checks),
  `checkMovieExport`, `chaptersNeedingTakes`, `resolveMovie`, `readMovie`,
  `pendingMovie`, `generateMovieTakes`, `loadMovie`.
- `src/episode.mjs`: `.json` dispatch; YAML episodes get one chapter per shot;
  a movie's shots need no narration, its chapters are validated; whole-frame
  tolerance.
- `src/speech.mjs`: one take per chapter, same keys; `cachedTake`,
  `generateTakes`; the key read only for a missing take; the overflow wording
  for a movie.
- `src/words.mjs`: word timing from the shot's chapter narration and take
  offset. `src/code.mjs`: emphasis phrase in the chapter narration; source
  excerpts from the root. `src/pictures.mjs`, `src/render.mjs`: paths from the
  root; `render` without a description template. `src/shot-cache.mjs`:
  whole-frame tolerance. `src/util.mjs`: `sourceBase`.
- `bin/videomaker.mjs`: takes generated from the unresolved document for
  `speech` and `build`; the usage line.
- Tests: `test/movie-document.test.mjs` (17), `test/movie-pipeline.test.mjs`
  (3), `test/project-fixture.mjs`, `test/viewer-double.mjs` (moved unchanged
  from `test/render.test.mjs`).
- Fixtures: `bare`, `two-chapters`, their takes and resolutions, fourteen
  invalid documents; `scripts/pin-resolved.mjs`.
- Records: ADR-001 (Accepted), the ADR index, the architecture overview, the
  manual (`README.md`, `docs/FORMAT.md`, `docs/movie-document.md`'s
  implementation notes, `fixtures/README.md`), `AGENTS.md`'s status line,
  `CHANGELOG.md`.

## Not claimed

The film from a document is cycle C's evidence: nobody has looked at a
document's frames or listened to a chapter take. The pipeline test proves the
document resolves, previews with every proof passing, and encodes with the
expected frames, size and audio, at 320×180 and 10 fps with the viewer double
and silent takes.
