## 1. Red first

- [x] 1.1 Run `tests/test_release_records.py` on the unmodified bench and record it green at 0.8.0.
- [x] 1.2 Move the five version statements to 0.8.1 by hand, set `release_date = '10 October 2026'` and `viewer_version = '0.8.1'`; run `tests/test_release_records.py` and `tests/test_machinome_identity.py` and record the red naming each record left behind.

## 2. Release facts and records

- [x] 2.1 `pyproject.toml`: the `viewer` and `web-snapshot` extras require `machinome-viewer>=0.8.1`.
- [x] 2.2 The changelog's `Unreleased` section becomes `Machinome 0.8.1`, `Released on 10/Oct/2026`, with an opening and the bullets grouped as a maker meets them, unchanged in wording.
- [x] 2.3 `HISTORY.rst` gains `Machinome 0.8.1 (2026-10-10)` above 0.8.0, in its shape, naming the archived changes.
- [x] 2.4 `docs/releases/release-0.8.rst` gains a last section `0.8.1: ...`, "Released on 10 October 2026.", in the shape of release-0.7's 0.7.1 section.
- [x] 2.5 `docs/project/upgrading.rst` opens with "Upgrading from Machinome 0.8.0 to 0.8.1", each change checked against the code.
- [x] 2.6 `context7.json` states 0.8.1 (released 2026-10-10) and the matching viewer 0.8.1, API 29.
- [x] 2.7 `tests/test_machinome_identity.py` states 0.8.1; `tests/test_production_documentation.py` still reads the 0.8.0 section, which records production profiles.
- [x] 2.8 `tests/test_missing_source_file.py` writes its own source beside `tests/stl_project/parts.py` in `setUpModule` and removes it in `tearDownModule`; red first on the bench, which carries no `bracket.stl`; mark the warts entry fixed.

## 3. Green and checked

- [x] 3.1 Run the documentation tests green; build the manual with `-n -W --keep-going -E`; read the changelog, upgrading and release-note pages in the built HTML.
- [x] 3.2 Run the full suite on the bench and the suite on a fresh clone with a fresh environment from `requirements*.txt`; record both in `evidence.md`.
- [x] 3.3 Sync the spec delta, archive, commit 2; ADR disposition: none (a release records and decides no architecture).
