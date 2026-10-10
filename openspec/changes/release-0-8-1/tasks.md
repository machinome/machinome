## 1. Red first

- [ ] 1.1 Run `tests/test_release_records.py` on the unmodified bench and record it green at 0.8.0.
- [ ] 1.2 Move the five version statements to 0.8.1 by hand, set `release_date = '10 October 2026'` and `viewer_version = '0.8.1'`; run `tests/test_release_records.py` and `tests/test_machinome_identity.py` and record the red naming each record left behind.

## 2. Release facts and records

- [ ] 2.1 `pyproject.toml`: the `viewer` and `web-snapshot` extras require `machinome-viewer>=0.8.1`.
- [ ] 2.2 The changelog's `Unreleased` section becomes `Machinome 0.8.1`, `Released on 10/Oct/2026`, with an opening and the bullets grouped as a maker meets them, unchanged in wording.
- [ ] 2.3 `HISTORY.rst` gains `Machinome 0.8.1 (2026-10-10)` above 0.8.0, in its shape, naming the archived changes.
- [ ] 2.4 `docs/releases/release-0.8.rst` gains a last section `0.8.1: ...`, "Released on 10 October 2026.", in the shape of release-0.7's 0.7.1 section.
- [ ] 2.5 `docs/project/upgrading.rst` opens with "Upgrading from Machinome 0.8.0 to 0.8.1", each change checked against the code.
- [ ] 2.6 `context7.json` states 0.8.1 (released 2026-10-10) and the matching viewer 0.8.1, API 29.
- [ ] 2.7 `tests/test_machinome_identity.py` states 0.8.1; `tests/test_production_documentation.py` still reads the 0.8.0 section, which records production profiles.

## 3. Green and checked

- [ ] 3.1 Run the documentation tests green; build the manual with `-n -W --keep-going -E`; read the changelog, upgrading and release-note pages in the built HTML.
- [ ] 3.2 Run the full suite on the bench and the suite on a fresh clone with a fresh environment from `requirements*.txt`; record both in `evidence.md`.
- [ ] 3.3 Sync the spec delta, archive, commit 2; ADR disposition: none (a release records and decides no architecture).
