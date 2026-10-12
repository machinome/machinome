## 1. Red first

- [x] 1.1 Run `tests/test_documentation.py` on the unmodified worktree and record it green at 0.8.0.
- [x] 1.2 Move the test's release pins to 0.8.1 (first release section `0.8.1 — 10 October 2026` naming Machinome 0.8.1 and "0.8.0 renumbered", project version, README, the compatibility page's "The 0.8.1 release declares:"); run and record the red.

## 2. Release facts and records

- [x] 2.1 Version 0.8.1 in `pyproject.toml`, `machinome_viewer/__init__.py`, the widget's `package.json` and both `version` fields of `package-lock.json`, by hand.
- [x] 2.2 `CHANGELOG.md`: `0.8.1 — 10 October 2026` above 0.8.0, in the shape of 0.7.1's section.
- [x] 2.3 `README.md`, `context7.json`, `docs/index.rst`, `docs/installation.rst`, `docs/compatibility.rst` and `docs/reference/cli.rst` state 0.8.1, released with Machinome 0.8.1 on 10 October 2026; API 28 and 29 stay "the 0.8.0 release".
- [x] 2.4 `workflow/release-0.8.md` records the renumbering, the PyPI digest check of 0.8.0 and what remains the pilot's.

## 3. Green and checked

- [x] 3.1 Run the Python suite and the widget's tests and typecheck; build the manual with warnings as errors.
- [x] 3.2 Sync the spec deltas, archive, commit 2; no ADR (a release decides no architecture).
- [ ] 3.3 After the fast-forward into `main`, `scripts/check-dist` in the primary checkout: expect version 0.8.1, API 29, documents 1 through 13.
