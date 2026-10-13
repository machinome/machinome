Groups 1 to 5 are the half before the day: one applier, one commit,
"Prepare 0.9.0: the mechanics helpers numbered with the set", which the
orchestrator reviews and commits on the bench. Groups 6 to 10 are the day,
once the pilot names the date: a fresh applier for 6 to 8 and one commit,
"Release 0.9.0"; the orchestrator for 9 and the archive of 10. Group 11 is
the pilot's alone. No agent tags, pushes or uploads.

## 1. Before the day: the base

- [ ] 1.1 Record the base in a new `evidence.md`: `git -C <bench> log --oneline -3` (this change's planning commit on the closed line's head, `manual-extras` and the close included), `git status --porcelain` empty, `make -s version` 0.8.1, the `Unreleased` bullets of `HISTORY.rst` (expected 16) and of the manual's changelog (expected 14) counted, and every page that still spells `|mechanics_version|` listed (`grep -rn` under `packages/machinome/docs`, `_build` aside).
- [ ] 1.2 Record the line's last suite counts from the close's evidence; do not rerun them here. One pytest process at a time, none while another bench's suite runs.

## 2. Before the day: red first

- [ ] 2.1 `tests/test_release_records.py` (design.md, Decision 4): `OWN_VERSION` and its branches removed from `test_every_member_is_numbered_with_the_core`, `test_every_pin_between_members_is_compatible` and `test_the_version_is_bumped_from_the_root`; `test_a_member_of_its_own_version_is_outside_the_bump` replaced by `test_the_mechanics_helpers_are_bumped_with_their_two_pins`; `PRODUCTS` and `ReleaseRecordsTest.test_each_product_records_the_release` added; the docstring. Run it. Expected red: the mechanics member not numbered (0.1.0), its two floors not `~=`, its manifest outside the tables, the two tables absent; the product test green (0.8.1 holds the viewer alone).
- [ ] 2.2 `tests/test_mechanics_boundary.py` and the mechanics package's `tests/test_machinome_identity.py` (Decision 4). Run them. Expected red: the extra is `machinome-mechanics>=0.1.0`, the dependency `machinome>=0.8.0`.
- [ ] 2.3 `tests/test_docs_structure.py`: `mechanics_version` out of `test_facts_are_substitutions`, `test_the_mechanics_version_is_the_package_s` removed, `UpgradingPageTest.test_the_0_9_part_names_every_move` added (Decision 5). Run the module. Expected red: the moves the part does not spell (design.md probe 6: seventeen subtests).
- [ ] 2.4 The tests that pinned a literal state (Decision 4's table): `tests/test_machinome_identity.py`, `tests/test_viewer_documentation_links.py`'s `current_text`, the viewer's `tests/test_documentation.py`, the movie's `tests/test_repository.py`, the studio's `tests/test_documentation.py`, the mechanics package's `tests/test_documentation.py`. Run each: green at 0.8.1 (they are rewritten to hold either state; their red is the day's, task 6.3, and probe 5 of design.md shows the base's forms failing on a dated tree).
- [ ] 2.5 Record in `evidence.md` every red of 2.1 to 2.3 with its reason and every green of 2.4.

## 3. Before the day: the mechanics helpers numbered with the set

- [ ] 3.1 Decision 3: the mechanics manifest (`version = "0.8.1"`, `machinome~=0.8.1`, the two comments), the core's `mechanics` extra (`machinome-mechanics~=0.8.1`, its comment), the two tables after the studio's in `.bumpversion.cfg`, `uv lock` (expected "Updated machinome-mechanics v0.1.0 -> v0.8.1"), `uv sync --python 3.12` at the bench root. Run 2.1 and 2.2: green.
- [ ] 3.2 `scripts/check-dist`: `MECHANICS_VERSION` removed; the mechanics row asserts the framework's version, `machinome~={version}` and the core's `machinome-mechanics~={version}` (Decision 3).
- [ ] 3.3 `docs/conf.py`: `mechanics_version`, its comment and its substitution line removed; the pages of 1.1 state `|release|`, but the upgrading page's 0.7 part, which states `0.1.0`; the status page's sentence as Decision 3 gives it. Run `test_docs_structure.py`'s `ReleaseFactsTest` and the mechanics package's `tests/test_documentation.py`: green.
- [ ] 3.4 The records (Decision 3, texts in Decision 7): `HISTORY.rst`'s mechanics join bullet without "its own version" and the mechanics bullet last under `Unreleased`; the manual changelog's mechanics bullet last under `Unreleased`; the mechanics `CHANGELOG.md` join bullet's last sentence; `context7.json`'s mechanics rule.
- [ ] 3.5 The mechanics package's own specs in place (Decision 3): `openspec/specs/distribution/spec.md` and `openspec/specs/user-documentation/spec.md`.
- [ ] 3.6 ADR-187: the status line and the amendment section of Decision 10, dated the day of this commit; its index line in `docs/adrs/README.md`.
- [ ] 3.7 `tests/test_repository_layout.py`'s docstring: the mechanics helpers numbered with the set.

## 4. Before the day: the upgrading page and the day note

- [ ] 4.1 The upgrading page's 0.9 part, verbatim from Decision 5, under the title, its label and `.. needs:: none`, before "The viewer flag". Run 2.3: green; `test_viewer_documentation_links.py` green.
- [ ] 4.2 The installation page's "Upgrading" paragraph, verbatim from Decision 5.
- [ ] 4.3 `workflow/ongoing/release-0.9.0-day.md` at the repository root, verbatim from Decision 9, `<prep date>` this commit's day.

## 5. Before the day: checked, rehearsed and committed

- [ ] 5.1 `make test` (every package with tests), `make docs`, `make check` on the bench; record the counts and that every smoke line reads 0.8.1, the mechanics row among them. `make lint`: the finding count against the base's.
- [ ] 5.2 The rehearsal, on a scratch copy of the bench's tracked tree at this group's state, made a Git repository and committed: `make sync`; `make bump VERSION=0.9.0` (expected exit 0 and probe 3's 29 files, the mechanics manifest among them); `uv sync --python 3.12`; the release-records test and the products' documentation tests red (probe 7's failures); Decision 7's records placed at a stand-in date; the same tests green; `make docs`; `make check`; commit; `make dist` (36 archives in `dist/v0.9.0`); `twine check --strict dist/v0.9.0/*`; `make -n upload`. Nothing of the copy is kept.
- [ ] 5.3 `evidence.md` complete for groups 1 to 5; this file's boxes ticked; pause before the commit and report. The orchestrator commits "Prepare 0.9.0: the mechanics helpers numbered with the set". The archive of this change waits for the day.

## 6. The day: the date and the bump (a fresh applier, the pilot's date)

- [ ] 6.1 Record the pilot's date and the base in `evidence.md`: the bench at the preparation's commit (or the head the orchestrator names), `git status --porcelain` empty, `make -s version` 0.8.1.
- [ ] 6.2 `make bump VERSION=0.9.0` from the bench root; record `git diff --stat` (expected 29 files, design.md probe 3) and `make -s version` (0.9.0); `git log` shows no new commit and `git tag` no new tag. Then `uv sync --python 3.12` at the bench root; `importlib.metadata.version` of `machinome` and `machinome-mechanics` reads 0.9.0 (design.md probe 12).
- [ ] 6.3 Run `tests/test_release_records.py` and the products' documentation tests (the viewer's, the movie's, the studio's, the mechanics package's). Expected red, each naming a record not yet dated: `context7.json`, the four products' changelogs, the changelog's first release section, the history's top entry, the release note's page, the viewer's release section and its `describe` example. Record each.

## 7. The day: the records

- [ ] 7.1 `docs/conf.py`: `version = '0.9'`, `release_date` the pilot's date (Decision 7).
- [ ] 7.2 `HISTORY.rst`: the `Unreleased` heading becomes `Machinome 0.9.0 (<YYYY-MM-DD>)` with its opening paragraph, verbatim; every bullet kept in its order.
- [ ] 7.3 The manual's changelog: `Machinome 0.9.0`, `Released on <dd/Mon/YYYY>`, the opening and the moves a project may follow, verbatim; the toctree's `../releases/release-0.9`.
- [ ] 7.4 `docs/releases/release-0.9.rst`, verbatim.
- [ ] 7.5 The status page: the four passages of Decision 7.
- [ ] 7.6 `context7.json`: the two rules of Decision 7.
- [ ] 7.7 The four products' changelogs and the studio's preamble, verbatim.
- [ ] 7.8 `docs/reference/viewer/cli.rst`'s `"version": "0.9.0"`; the viewer's own `user-documentation` and `viewer-distribution` specs at 0.9.0, in place.
- [ ] 7.9 Re-read every bullet list against the head: a bullet landed after the planning commit stays in its place; `grep -rn "0\.8\.1"` over the tracked files, records, archives and workflow aside, finds only the 0.8.1 records and the tests' fixtures.

## 8. The day: green, checked and committed

- [ ] 8.1 Run 6.3's tests: green. `make test` whole; `make docs`; read the status page, the changelog's 0.9.0 section, the release note and the upgrading page's 0.9 part in the built HTML.
- [ ] 8.2 `make check`: 36 archives from the tree and 36 from the clean copy, every smoke line reading 0.9.0.
- [ ] 8.3 `git status --short`: the bump's 29 files, the records of group 7, `evidence.md` and this file, nothing else. Pause before the commit and report; the orchestrator commits "Release 0.9.0".

## 9. The day: integration and the archives (the orchestrator)

- [ ] 9.1 Fast-forward the framework's `main` to "Release 0.9.0" (the line merged before it; the preparation reaches `main` with it).
- [ ] 9.2 In the primary checkout at `main`: `make sync`, `git status --porcelain` empty, `make dist` (expected `dist/v0.9.0` with 36 archives, each `twine check --strict` PASSED), `ls dist/v0.9.0`, `make -n upload`. `make upload` is never run.

## 10. The day: the archive

- [ ] 10.1 `evidence.md`: 9.1 and 9.2 recorded; the spec deltas synced into `openspec/specs/` (`user-documentation`, `framework-identity`, `mechanics-distribution`); `openspec validate --specs` green; the change archived as `archive/<date>-release-0-9-0/`; ADR disposition: ADR-187 amended in the preparation, nothing new.
- [ ] 10.2 `workflow/ongoing/release-0.9.md`'s progress entry for cycle 10, the commits and counts; the day note stays in `ongoing/` until the pilot's steps are done.
- [ ] 10.3 One commit on the bench, which touches `packages/machinome/openspec/` and `workflow/` alone (`git diff --stat`); the orchestrator fast-forwards `main` to it. The tag stays on "Release 0.9.0".

## 11. The pilot's steps (no agent runs these)

- [ ] 11.1 The day note's steps 1 to 4: read `dist/v0.9.0`; tag "Release 0.9.0" `v0.9.0`; push `main` and `v0.9.0`; `make upload`.
- [ ] 11.2 The day note's steps 5 to 8: Read the Docs, Context7, the original repositories, the 0.8.1 archives.
