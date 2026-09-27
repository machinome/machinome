# Evidence: release-0-7-1

Base `fabfc3d` (framework `main`, 27 September 2026), worktree
`machinome/WTs/release-0-7-1`, workspace venv.

## Red first

On the base tree, before any edit:

- `tests/test_release_records.py` (new): 5 of 10 tests failed
  (`test_the_changelog_top_entry_is_the_released_version`,
  `test_the_0_7_1_entry_names_what_it_ships`,
  `test_the_status_page_describes_nothing_as_unreleased`,
  `test_the_release_note_has_the_dated_section`,
  `test_context7_states_the_release`); the version-file tests passed
  because every file still agreed on 0.7.0.
- `test_no_release_fact_is_trapped_in_inline_markup` (added after the
  built status page was read): failed on `docs/project/status.rst`.
- `tests/test_frame_precision_docs.py::test_changelog_records_precision_in_the_release_that_ships_it`
  and `tests/test_mates.py::ManualTest::test_the_changelog_names_the_mate_in_the_release_that_ships_it`,
  repointed from the `Unreleased` section to the 0.7.1 section: both
  failed ("'Machinome 0.7.1' not found").

## Green

- Documentation tests after the edits: `test_release_records`,
  `test_frame_precision_docs`, `test_machinome_identity`,
  `test_profile_documentation`, `test_docs_structure`,
  `test_docs_exports`, `test_viewer_documentation_links`: 41 passed,
  139 subtests; `test_mates.py -k ManualTest`: 8 passed.
- Manual built with the CI flags plus `-E`
  (`python -m sphinx -b html -W --keep-going -E docs docs/_build/html`):
  exit 0. With `-n` as well, 5 warnings, all `reference target not
  found` in `docs/reference/api.rst` and `machinome/simulation/sim.py`
  docstrings, present on `main` before this change and outside the
  flags CI and Read the Docs use.
- The built status page's first sentence reads "Machinome 0.7.1 was
  released on 27 September 2026". Before the fix, and on Read the Docs
  for 0.7.0, it reads "Machinome |release| was released on
  |release_date|": a substitution inside `**...**` is not resolved.
- Full suite at the tree before the fixture restoration: 4092 passed,
  11 failed, 4 skipped, 2994 subtests, 536 s. The 11 are the four
  `test_vet_*` files' closure tests; the same 11 fail on `main`
  `fabfc3d` (run here) and in the framework's CI at that commit (run
  36339468539, "11 failed, 4071 passed, 17 skipped"). Cause: `.gitignore`
  ignores `parts/`, so `tests/vet_projects/{pure_project,star_import,init_on_path}/sim/parts/`
  were never committed by `vet-the-project`. Restored from the
  `fix-warts-2` bench, which still held them untracked, with a
  `!tests/vet_projects/*/sim/parts/` negation: the four files 60 passed,
  76 subtests.

## Read as a reader

`project/status`, `project/changelog` (the 0.7.1 section) and
`releases/release-0.7` (the 0.7.1 section) in the built HTML. The
changelog's bullets were checked against the archived changes:
`vet-the-project` (the command, the universe, the adapters' refusal),
`external-wrapper-cache-identity` (ADR-155: the four source-bound
adapters, artifacts rebuild once) and
`stable-mate-rotation-conversion` (`_axis_angle`, the `1e-9` snap kept).

## Left to the pilot

Integration into `main`, the `v0.7.1` tag, the push, the PyPI upload
from a fresh build at the tagged commit, the Read the Docs builds and
the Context7 refresh.
