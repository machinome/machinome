# Evidence: release-0-8-1

Base `31c8507` (framework `main`), bench `machinome/WTs/release-0-8-1`,
10 October 2026. Authorization: the pilot's request of 10 October 2026,
"prepare releases for v0.8.1 of framework and viewer. leave everything
ready for me to twine upload. tag repositories". Review: mine, as the
ratification gate, of the planning artifacts and of the implementation.

## Published state checked first

- PyPI: `machinome` 0.8.0 and `machinome-viewer` 0.8.0 are the latest
  releases; no 0.8.1 exists.
- GitHub: tag `v0.8.0` (object `cb1e1d4`, commit `d22d0a1`) pushed;
  `main` pushed to `d7b6f9b`; local `main` 66 commits ahead.

## A clean checkout's suite, before the change

A fresh `git clone` of `31c8507` into a scratch directory, a fresh
`uv venv -p 3.12` with `requirements.txt` and `requirements_dev.txt`,
`SOLID_BUILD_DIR` and `PYTHONPATH` unset, as CI runs:
1 failed, 4751 passed, 20 skipped, 6728 subtests, 566 s. The failure is
`tests/test_missing_source_file.py::UndeclaredSourceTest::test_a_declaration_given_alone_is_resolved_beside_its_module`:
`MissingSourceFile` for `tests/stl_project/bracket.stl`, the gitignored
mesh `tests/test_stl_node.py` writes later in the run
(`workflow/warts.md`, 9 October 2026). Flake8 reports findings, as before;
CI's lint steps are `continue-on-error`.

## Red, then green

- 1.1 `test_release_records.py` and `test_machinome_identity.py` at
  0.8.0: 14 passed, 63 subtests.
- 1.2 With the five version files at 0.8.1 and `release_date` moved:
  6 failed, each naming a record left behind — the matching viewer
  (`'0.8.0' != '0.8.1'`), `context7.json`, the changelog's first release
  section (`'Machinome 0.8.0' != 'Machinome 0.8.1'`), `HISTORY.rst`'s top
  entry, the release note's last section (`'0.8.1' not found in
  'Upgrading'`) and the identity literal.
- 2.8 `test_missing_source_file.py` on the bench, which carries no
  `bracket.stl`: 1 failed (`MissingSourceFile`, as on the fresh clone);
  with the module's own `declared_alone.stl`: 29 passed, and
  `tests/stl_project/` holds no file afterwards.
- Documentation tests (`test_release_records`, `test_machinome_identity`,
  `test_docs_structure`, `test_docs_exports`,
  `test_viewer_documentation_links`, `test_profile_documentation`,
  `test_production_documentation`, `test_frame_precision_docs`,
  `test_mates`, `test_tutorial_counter`, `test_sphinx_ext`,
  `test_node_root_exports_nothing`): 230 passed, 1360 subtests.

## The full suite on the bench

With the workspace venv, `PYTHONPATH` at the bench: 4768 passed,
4 skipped, 6734 subtests, 746 s (the fixture fix included; the suite
before it, on a fresh clone, is above). A fresh clone of the completed
commit is run again before integration; its result is reported with the
integration, since this record is part of that commit.

## The manual

`python -m sphinx -b html -n -W --keep-going -E docs <scratch>`: clean.
Read in the built HTML: the changelog's 0.8.1 section (opening, the five
changes a project may follow, the bullets in a maker's order); the
upgrading page, titled by its first part "Upgrading from Machinome 0.8.0 to
0.8.1", as the 0.8.0 release left it titled by its own; the release note's
"0.8.1: corrections from real machines"; the status page's first sentence,
"Machinome 0.8.1 was released on 10 October 2026", and "viewer 0.8.1, API
29".

Release-pass corrections to the bullets as written: three named a project
(a wall clock by its Foundry number, a mechanical calculator by name, a
telescope mount by name); each now names the machine by kind
(`skills/write-the-manual/SKILL.md`, rule 3). The 0.8 release note's
"opens with every breaking change of 0.8" now reads "lists", since the
upgrading page opens with 0.8.1's part.

## Claims checked against the code

- `ClockedSnapshot.__init__(self, model, values, identity)`
  (`machinome/simulation/clocked.py`); `restore` raises `ValueError`
  naming both identities.
- The early read of `children` raises `StructureError`
  (`machinome/node/internal.py`, `_early_read`), a `RuntimeError`
  subclass from `machinome/node/declarative.py`.
- `require_source_file` is `machinome.node.sources.require_source_file`.
- ADRs since `v0.8.0`: none new; ADR-033, ADR-096 and ADR-142 amended;
  ADR-156's status line only cites ADR-164 (not an amendment).

ADR disposition: none. A release records and decides no architecture.
