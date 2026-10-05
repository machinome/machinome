## 1. Red first

- [ ] 1.1 Repoint `tests/test_documentation.py::test_the_manual_states_the_release` to `0.8.0 — 5 October 2026`, `Machinome 0.8.0`, `viewer API 29` (compared with `package.json`; drop the comment that the source runs ahead of the record), version `0.8.0` and the README's mention; require `workflow/release-0.8.md` in `test_docs_contains_no_development_records`; repoint `test_film_annotations_are_documented_as_current_source` (renamed `..._as_part_of_the_0_8_0_release`) and `test_on_demand_clocked_capture_is_documented` to the 0.8.0 section and the pages' release wording.
- [ ] 1.2 Add `tests/test_licence.py::test_reader_facing_pages_name_only_the_viewers_grant`: over `README.md`, `CHANGELOG.md`, `context7.json` and every `docs/**/*.rst`, every SPDX-shaped licence identifier is the viewer's grant and no capitalised word stands directly before "licence"/"license"; the test names no other licence.
- [ ] 1.3 Run both files on the unmodified tree and record the failures in `evidence.md`.

## 2. Version

- [ ] 2.1 Move the version to 0.8.0 in `pyproject.toml`, `machinome_viewer/__init__.py`, `machinome_viewer/widget/package.json` and both `version` fields of `package-lock.json`; check no other `0.7.1` version statement remains outside the records.
- [ ] 2.2 Rebuild the bundle with `npm run build --prefix machinome_viewer/widget` in this worktree (linked `node_modules`, never `npm ci` or `npm install`) and check the banner reads `machinome-viewer 0.8.0 - viewer API 29`.

## 3. Records

- [ ] 3.1 Turn `CHANGELOG.md`'s `Unreleased` section into `0.8.0 — 5 October 2026`: released with Machinome 0.8.0 and numbered with it; viewer API 29 and document versions 1 through 13; what a host gets (screen position and projection, highlight, up and field of view per view call, a clocked machine captured on demand) and what a maker gets (fresh rigid assets drawn in a deterministic order), each naming its archived change in one line, with API 28 and API 29 placed where they arrived; compatibility both ways. Verify each claim against the source and the reference pages. No `Unreleased` section remains.
- [ ] 3.2 Rewrite the licensing sentence of the 0.7.0 changelog section, `README.md`, `docs/index.rst`, `docs/sharing.rst`, `context7.json` and `openspec/config.yaml` to name only the viewer's grant and say the framework is licensed separately.
- [ ] 3.3 Update `docs/index.rst`, `docs/installation.rst`, `docs/compatibility.rst`, `docs/reference/mount.rst`, `docs/reference/cli.rst`'s `describe` example, `README.md` and `context7.json` to 0.8.0, released with Machinome 0.8.0 on 5 October 2026, API 29; the compatibility page names API 28 and API 29 as the 0.8.0 release and keeps "API 27, the 0.7.0 release". `docs/conf.py` states no fact and stays.
- [ ] 3.4 Write `workflow/release-0.8.md` in the shape of `workflow/release-0.7.md`; point `README.md` and `workflow/README.md` at it.

## 4. Green and checked

- [ ] 4.1 Run the Python suite with `PYTHONPATH` on this worktree and the widget suite; report the widget suite's known timing test.
- [ ] 4.2 Build the manual with `python -m sphinx -b html -n -W --keep-going docs docs/_build/html`, run `python scripts/check-docs-browser.py` on it, and read the home, installation and compatibility pages as a reader.
- [ ] 4.3 Sync the `user-documentation` and `viewer-distribution` deltas, validate strictly, record the evidence; archive and commit only when the orchestrator says so, and state that `scripts/check-dist`, the `v0.8.0` tag, the push, the uploads, Read the Docs and Context7 remain the pilot's.
