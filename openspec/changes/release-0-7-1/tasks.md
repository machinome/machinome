## 1. Red first

- [ ] 1.1 Write `tests/test_release_records.py`: the version from `pyproject.toml` equals `machinome.__version__`, the vet universe's version, `setup.cfg`'s `current_version` and `docs/conf.py`'s `release`; the changelog's first section is `Machinome <version>` with a `Released on` line and no `Unreleased` section anywhere; `HISTORY.rst`'s first section is `Machinome <version> (<date>)`; the status page contains no `unreleased`; `docs/conf.py`'s `release_date` is the changelog's and `HISTORY.rst`'s date; `context7.json` names the version. Run it and record the failure on the current tree.
- [ ] 1.2 Repoint the three tests that read the section above `Machinome 0.7.0` as unreleased: `test_mates.py` (`test_the_changelog_names_the_mate_above_the_release`), `test_frame_precision_docs.py` (`test_changelog_records_precision_only_under_unreleased`) to the 0.7.1 section; check `test_profile_documentation.py` needs no edit. Run them and record the failure.

## 2. Version and release facts

- [ ] 2.1 Move the version to 0.7.1 in `pyproject.toml`, `machinome/__init__.py`, `machinome/vet/universe.toml`, `setup.cfg` and `docs/conf.py` (`release`); set `release_date` to 27 September 2026 and `viewer_version` to 0.7.1; leave `viewer_api` 27, `document_versions` 1 to 13 and `mechanics_version` 0.1.0.
- [ ] 2.2 Update `tests/test_machinome_identity.py`'s version literal.

## 3. Records

- [ ] 3.1 Rewrite the changelog's `Unreleased` section as `Machinome 0.7.1`, `Released on 27/Sep/2026`, in families and in the order a maker meets them, adding bullets for `machinome vet` (ADR-149), the source-qualified wrapper identity (ADR-155) and the stable rest-rotation recovery, each checked against the archived change and its code; keep the 0.7.0 section unchanged.
- [ ] 3.2 Add the `Machinome 0.7.1 (2026-09-27)` section to `HISTORY.rst` in the 0.7.0 section's shape, with ADR numbers and the originating machines described by kind.
- [ ] 3.3 Rewrite `docs/project/status.rst`: drop "Since |release|", name frames, mates and vet in "What |version| is", keep every fact a substitution.
- [ ] 3.4 Add the dated 0.7.1 section to `docs/releases/release-0.7.rst`.
- [ ] 3.6 Take the status page's first sentence out of bold, where its `|release|` and `|release_date|` substitutions were never resolved (the 0.7.0 manual on Read the Docs shows them literally); pin it with a test that refuses a substitution inside inline markup on any page.
- [ ] 3.5 Update `context7.json`: 0.7.1 and its date, the viewer 0.7.1, a rule for frames and mates, a rule for `machinome vet`.

## 3b. The suite is green

- [ ] 3.7 Commit the three `sim/parts` fixture packages of the vet fixture projects, hidden by `.gitignore`'s `parts/` rule since the vet cycle, with a negation for `tests/vet_projects/*/sim/parts/`; run the four `test_vet_*` files green.

## 4. Green and checked

- [ ] 4.1 Run the documentation tests (`test_release_records`, `test_machinome_identity`, `test_mates`, `test_frame_precision_docs`, `test_profile_documentation`, `test_docs_structure`, `test_docs_exports`, `test_viewer_documentation_links`, `test_vet*`) green.
- [ ] 4.2 Build the manual with warnings as errors (`python -m sphinx -b html -n -W --keep-going -E docs docs/_build/html`) and read the status, changelog and release-note pages as a reader.
- [ ] 4.3 Run the full suite in the worktree and record the counts.
- [ ] 4.4 Sync the spec deltas, archive the change with its evidence, and commit the completed state; report what remains the pilot's (tag, push, upload, Read the Docs, Context7).
