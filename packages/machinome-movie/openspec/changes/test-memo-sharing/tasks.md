## 0. Preconditions

- [x] 0.1 Base: branch `test-memo-sharing` from `react-stage` at `55f255d`,
  its `.test-memo/` holding 108 verdicts copied from the campaign worktree.
  Run the base suite once before any change and record count, time and memo
  hits in `evidence.md` (28 files, 278 tests, 108 passed from the memo, 170
  run, 10.6 s), and the `/tmp/videomaker-cold-*` count (28).
- [x] 0.2 Measure the narrowed key on the base content before adopting it
  (design D4): for each slow file, the files under `src/`, `stage/` and
  `bin/` its key covers under the old and the new rule, and which single-file
  edits invalidate which files; record it in `evidence.md`.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit: the store's place (D1), root-relative keys (D2), concurrent
  writers (D3), the narrowed key, its table and tripwire (D4), the cold run
  directory (D5), the refusal's subject (D6).

## 1. Share the memo (red first)

- [ ] 1.1 Red: in `test/memo.test.mjs`, two worktrees of a temporary Git
  repository resolve one store under the common Git directory, and a plain
  directory falls back to its own `.test-memo/`; a verdict passed from root A
  is passed from the memo from root B with equal content and runs when B's
  content differs; the same for an artefact. Two writers producing one
  artefact at once both return one verified entry. Record the failures.
- [ ] 1.2 `test/support/memo.mjs`: `memoDirectory(root)`, the `root` option
  of `openMemo` for every fingerprint, schema `verdict-memo-v2`, pending and
  staging names carrying the PID, the lost rename race, the damaged entry
  moved aside; `test/support/toolchain.mjs` finds the store and provides it.

## 2. Narrow the verdict key (red first)

- [ ] 2.1 Red: over a temporary tree, a file reached only through an import
  misses when changed; an unreached file's change hits; a served directory
  declared by a reached module is keyed; a spawned command is followed
  through its imports; on the real repository every browser test's key covers
  `stage/shipped.tsx` and `src/film.html`, and the tripwire finds no
  undeclared reader, and finds one when a reached module locates a file
  without an entry. Record the failures.
- [ ] 2.2 `test/support/reach.mjs` (the graph, `READS`, `ALWAYS`, the
  tripwire), and `slowTestInputs` in `memo.mjs` taking its inputs from it.

## 3. Wart 10 (red first)

- [ ] 3.1 Red: a cold artefact is made inside the cold directory it is given
  and nowhere else, and is refused without one; the run directory is removed
  when closed; the sweep removes a dead PID's run directory, staging, trash
  and pending entries and keeps a live one's. Record the failures.
- [ ] 3.2 `openColdRun`, `closeColdRun`, `sweep` in `memo.mjs`; the global
  setup sweeps and opens, the teardown closes.

## 4. Wart 11 (red first)

- [ ] 4.1 Red: `test/annotations.test.mjs` asserts "This episode needs" for a
  YAML episode and "This movie needs" for a movie, from `viewerApiRefusal` and
  `confirmViewerApi`; `test/movie-document.test.mjs` asserts the refusal
  `stageConfig` gives the stage for the fixture movie says "movie". Record the
  failures.
- [ ] 4.2 `src/episode.mjs` (the subject), `src/render.mjs` (`stageConfig`),
  `bin/videomaker.mjs` (`check`).

## 5. Proof and records

- [ ] 5.1 The whole suite cold (`npm test -- --cold`) with counts and time and
  the `/tmp/videomaker-cold-*` count before and after; a warm run filling
  the new store; a probe edit per row of the measurement table showing which
  files are passed from the memo; a copy of the worktree's content into a
  temporary directory, recognised by Git as the same repository, run warm
  against the same store.
- [ ] 5.2 ADR-003 amended in place with a dated section; `AGENTS.md`,
  `README.md`, `docs/architecture-overview.md` where they name the memo;
  `CHANGELOG.md` under `Unreleased`; warts 10 and 11 marked triaged.
- [ ] 5.3 Sync baseline specs and archive the change with the CLI; a warm run
  on the final content showing the hit count, recorded in `evidence.md`.

## 6. Human review (not claimed by automation)

- [ ] 6.1 The pilot decides whether the old `.test-memo/` directories of the
  worktrees and the `videomaker-cold-*` directories the old code left under
  `/tmp` are deleted.
