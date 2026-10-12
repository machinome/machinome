# Evidence: release-0-8-1

Base `ff9ac52` (viewer `main`), worktree `WTs/release-0-8-1`, 10 October
2026. Authorization: the pilot's request of 10 October 2026 to prepare
releases for v0.8.1 of the framework and the viewer, ready for upload, with
the repositories tagged.

## What 0.8.0 shipped and what changed since

- PyPI `machinome-viewer` 0.8.0, uploaded 2026-10-06T08:09 UTC: sha256
  `0c332da5…b0a838` (wheel) and `02feec08…8033fd` (sdist), equal to
  `dist/machinome_viewer-0.8.0*` built at `v0.8.0` (`29f1ed9`).
- `git diff --stat v0.8.0 main -- machinome_viewer`: one file,
  `machinome_viewer/widget/src/run/running-corpus.test.ts` (+16), a test;
  the root `openscad.py` removed in `ff9ac52` was outside the package.

## Red, then green

- 1.1 `tests/test_documentation.py` at the base: 11 passed.
- 1.2 Pins moved to 0.8.1: 2 failed
  (`test_the_manual_states_the_release`: first release section
  `0.8.0 — 5 October 2026`; `test_film_annotations_are_documented_as_part_of_the_0_8_0_release`:
  `'The 0.8.1 release declares:'` not in the compatibility page).
- After the facts moved: 11 passed.

## Checks

- Widget bundle built in the worktree with `node build.mjs` (its
  `node_modules` a link to the primary, so no `npm ci`): banner
  `machinome-viewer 0.8.1 - viewer API 29`.
- Python suite: 246 passed, 469 subtests (6 bundle tests failed before the
  bundle was built, all "Viewer bundle not found").
- Widget: `tsc --noEmit` clean; vitest 1715 passed, 2 skipped (65 files).
- Manual: `sphinx -b html -n -W --keep-going -E` clean; the home note reads
  "released on 10 October 2026 together with Machinome 0.8.1".
- `openspec validate release-0-8-1 --strict`: valid.

No ADR: a release records and decides no architecture.
