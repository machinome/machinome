# Evidence: release-0-7-1

Base `1e67c83` (viewer `main`, 27 September 2026), worktree
`machinome-viewer/WTs/release-0-7-1` with `node_modules` linked to the
primary checkout (build and tests only; no `npm ci`, no `npm install`,
no `scripts/check-dist` here).

## Red first

`tests/test_documentation.py::test_the_manual_states_the_release`,
repointed to `0.7.1 — 27 September 2026` and `Machinome 0.7.1`, failed on
the base tree: the changelog's first section still read
`0.7.0 — 23 September 2026`.

## Green

- `npm run build` after the bump: the banner reads
  `machinome-viewer 0.7.1 - viewer API 27`.
- `test_documentation`, `test_bundle`, `test_cli`: 33 passed.
- Manual: `python -m sphinx -b html -n -W --keep-going docs docs/_build/html`
  exit 0; the home page's note reads "released on 27 September 2026
  together with Machinome 0.7.1".
- Python suite: 219 passed, 435 subtests, 364 s (2 skipped in earlier
  runs are Chromium-dependent and ran here).
- Widget suite (`npm test`): 1614 passed, 2 skipped, 1 failed:
  `src/run/cost.test.ts > runs the acceptance machine far faster than
  real time` measured 1937 ticks/s against a 2400 floor while the
  framework's full suite was loading the same CPU. Re-run alone:
  `cost.test.ts` 14 passed, the same test in 667 ms. No viewer source
  changed in this cycle.

## Facts recorded

PyPI's `machinome-viewer` 0.7.0 files (uploaded 2026-09-26T08:49Z) have
the sha256 of `dist/0.7.0-2026-09-25/`, built from `1e67c83`; the GitHub
`v0.7.0` tag points at `0761145`. 0.7.1 renumbers `1e67c83`'s source.

## Left to the pilot

Integration into `main`, `scripts/check-dist` from the primary checkout,
the `v0.7.1` tag, the push and the PyPI upload.
