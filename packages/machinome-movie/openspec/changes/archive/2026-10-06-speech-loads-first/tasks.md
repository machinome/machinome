## 0. Preconditions

- [x] 0.1 Base: branch `speech-loads-first` from `catch-up-0-8` at `e9b08f9`
  (worktree `WTs/speech-loads-first`).
- [x] 0.2 The viewer bundle (API 29) passed by path in the environment for
  the cold Node suite, never written into the repository.
- [x] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. Red first

- [x] 1.1 Takes layer, in process (`test/pipeline/movie-pipeline.test.mjs`):
  the existing provider double, its take lookup generalized by movie name;
  the speech command's two steps (`generateMovieTakes`, then `loadEpisode`)
  on the `tour` copy with a changed `source.revision`,
  a removed export, an excerpt file changed after the commit and a
  `program` block, and on the `count` copy with a changed
  `clocked.identity`: each is refused with the load's refusal (literal)
  and the double records no request (design D5).
- [x] 1.2 Command line, with `cli()`'s `NO_FETCH` import: `speech` and
  `build` on the changed-revision `tour` copy exit 1 with the load's
  refusal line and print neither the network-request error nor the
  missing-key refusal.
- [x] 1.3 Run both cold before any product code and record in
  `evidence.md` (red: one request per chapter before the same refusal in
  process; the purchase attempted from the command line).

## 2. Green

- [x] 2.1 `src/movie.mjs`: `openMovie` (steps 2 to 5 of `loadMovie`,
  unchanged, called first by `loadMovie`), `checkBeforeTakes` (steps 8 to
  11 on the unresolved document), `generateMovieTakes` opening and checking
  before `generateTakes`, and `checkProject`'s frame count on a resolved
  film only (D2).
- [x] 2.2 `bin/videomaker.mjs`: the comment on the first step.
- [x] 2.3 The test green; the mutation (`generateMovieTakes` back to
  `pendingMovie` alone) red again, then restored; both in `evidence.md`.

## 3. Records

- [x] 3.1 `docs/movie-document.md`, "Resolution" item 2: what `speech`
  refuses before it generates, stated once.
- [x] 3.2 `CHANGELOG.md`, one bullet under `Unreleased`.
- [x] 3.3 `workflow/warts.md`, Addition 31: fixed by `speech-loads-first`.
- [x] 3.4 `docs/architecture-overview.md` read; changed only if the
  structure it describes moved.
- [x] 3.5 The delta spec synced into `openspec/specs/movie-document/spec.md`
  and the change archived with the CLI.

## 4. Proof

- [x] 4.1 The Node suite cold with the API 29 bundle selected
  (`npm test -- --cold`), counts, skips, failures and wall time in
  `evidence.md`.
- [x] 4.2 The Python suite with the worktree's `python/` on `PYTHONPATH`;
  the known collection failure of the campaign (the fixture project's
  models under machinome 0.8, cycle `fixture-under-0-8`) reported as such,
  and the tests that collect run.
- [x] 4.3 No paid request, no run of `speech` on a real film, nothing
  pushed.
