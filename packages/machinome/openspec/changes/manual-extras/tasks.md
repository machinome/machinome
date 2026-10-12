## 1. Evidence baseline

- [ ] 1.1 Record the base: `git -C <bench> log --oneline -1` is the planning commit on the line's head the orchestrator names (after `release-tooling`, `join-studio` and `viewer-seam`), the worktree clean but this change; start `evidence.md` in this change with it, and with which of design.md's "Assumptions about the cycles before this one" held: `make docs` exists and its recipe; `join-studio`'s eight pages and their names; the flag `viewer-seam` left (`--renderer` or `--viewer`) and any extra it added; whether `viewer-command` landed and its pages. Where an assumption failed, adjust the table of declarations, the `studio` row and the derived rule's flag accordingly and record each adjustment; if one needs a decision the design does not cover, stop and report it.
- [ ] 1.2 Record the manual's base build: `make docs` at the root (or, before it exists, a venv from `packages/machinome/docs/requirements.txt` alone and `python -m sphinx -b html -n -W --keep-going -E docs <scratch>/base-html` from `packages/machinome`): exit, seconds, HTML count. Recount the pages (`.rst` under `docs/` but `releases/` and `_build/`) and record the count with the 77 of 462f7119.
- [ ] 1.3 Record the base runs of the modules this change touches, on the bench venv, one pytest process at a time: `tests/test_docs_structure.py`, `tests/test_kernel_extras.py`, `tests/test_repository_layout.py`, `tests/test_sphinx_ext.py` (passed, skipped, subtests).

## 2. Red first (no page, extension or record changes in this group)

- [ ] 2.1 `tests/test_docs_structure.py`: the class `PageExtrasTest` of design.md Decision 5, its eight tests and its helpers, the module docstring naming `manual-extras`. Run the class. Expected red: `test_every_page_declares_first_under_its_title` naming every page (the count of 1.2), `test_the_table_is_the_manifest_s` (`FileNotFoundError`, no `docs/_ext/manual_extras.toml`), `test_a_product_s_reference_section_declares_its_product`, `test_the_core_s_rules_and_records_declare_none` and `test_a_teaching_page_declares_what_its_code_needs` (no declarations), `test_the_installation_page_derives_its_list` (no label, no directive, a `list-table`), `test_the_tutorial_s_install_line_names_its_chapters_extras` (the line names `viewer,cadquery`; or the union is empty, record which first). Record each reason.
- [ ] 2.2 `tests/test_manual_extras.py`, new, as Decision 5 states. Run it. Expected red: each build errors, the extension `manual_extras` cannot be imported; the import test fails, no module file. Record.
- [ ] 2.3 `tests/test_repository_layout.py`: `test_the_guide_says_a_page_declares_its_extras`. Run it. Expected red: `CONTRIBUTING.rst` does not contain ``` ``.. needs::`` ```.
- [ ] 2.4 `KernelExtrasTest`: remove `test_the_installation_page_names_every_kernel_extra`, `test_the_installation_page_names_the_extension_distributions` and `EXTRAS`, and say in the class docstring that the rendered list holds them (`tests/test_manual_extras.py`, change `manual-extras`); move `join-studio`'s installation-page assertions on the studio, if it added any, to `test_manual_extras.py` the same way. Confirm by `grep` that no other test reads `start/install.rst` for an extra or a distribution, and record what it found.
- [ ] 2.5 Record in `evidence.md` every red of 2.1 to 2.3 with its reason.

## 3. The extension and its table

- [ ] 3.1 `docs/_ext/manual_extras.toml`, design.md Decision 3 verbatim (the `studio` row as 1.1 settled it).
- [ ] 3.2 `docs/_ext/manual_extras.py`, Decision 2: the repository's licence header, a module docstring, the two settings, the two directives, the environment's record with purge and merge, the consistency check, the list's pages filled at `doctree-resolved`, `parallel_read_safe` and `parallel_write_safe`. `docs/_static/manual-extras.css`, Decision 2.
- [ ] 3.3 `docs/conf.py`: `sys.path.insert(0, os.path.abspath('_ext'))` beside the existing path lines, `'manual_extras'` appended to `extensions`, `manual_extras_exempt = ['releases/*']` with a one-line comment. `git diff` of `conf.py` shows those lines and nothing else.
- [ ] 3.4 Run `tests/test_manual_extras.py`. Expected green. `flake8 --max-line-length=89 docs/_ext/manual_extras.py tests/test_manual_extras.py`: 0 lines.

## 4. The declarations and the pages

- [ ] 4.1 Insert `.. needs:: <extras>` (or `none`), with one blank line above and below, as the first line under the title of every page, as design.md's table of declarations states; the extras in the table's order. Use one script with an exact-match assertion per page (the title found, nothing above the inserted line changed); `git diff --stat` shows one insertion of three lines per page and nothing else.
- [ ] 4.2 `start/install.rst` and `start/first-machine.rst` as Decision 4 states, each edit in place; `git diff` of the two shows those hunks only.
- [ ] 4.3 `docs/project/contributing.rst` and `CONTRIBUTING.rst`, Decision 6, in place.
- [ ] 4.4 Run `tests/test_docs_structure.py`, `tests/test_repository_layout.py` and `tests/test_manual_extras.py`. Expected green. Show `test_a_teaching_page_declares_what_its_code_needs`'s red once: remove `build123d` from chapter 5's declaration, run the test (red naming `tutorial/05-buttons` and `build123d`, reached through `counter/c05_buttons.py`'s import of `c04_relations`), restore it (`git diff` of the page against 4.1 empty). Record both runs.

## 5. The records

- [ ] 5.1 `HISTORY.rst` and `docs/project/changelog.rst`: the `Unreleased` bullets of Decision 7, verbatim, after the last bullet of each.
- [ ] 5.2 `docs/architecture.md`: the Map row of Decision 7.
- [ ] 5.3 ADR-195 (or the next free number, recorded) under `docs/adrs/BUILD/`, as Decision 7 outlines, and its index line under BUILD in `docs/adrs/README.md`.
- [ ] 5.4 `workflow/warts.md`: one entry, dated, recording chapter 10's default `machinome snapshot` lines against chapter 1's and the installation page's sentences on OpenSCAD (design.md, Open Questions 6), with probe 3's refusal, for the pilot's triage.
- [ ] 5.5 Run `tests/test_release_records.py`, `tests/test_docs_structure.py`, `tests/test_docs_exports.py`. Expected green.

- [ ] 5.9 (the orchestrator's ratification, 12 October 2026, Open Questions 7 overruled) `packages/machinome/MANIFEST.in` carries everything the manual's build reads: `docs/_ext/`, `docs/_static/`, `docs/_exports/` and the example projects beside the pages, so the source archive's manual builds; red first by a test in `tests/test_release_records.py` (or the layout gate, decide) that unpacks the sdist `python -m build --sdist` writes in a scratch directory and asserts those entries; then proven once in the evidence by building the manual with `-W` from the unpacked archive's `docs/` with the docs venv. The release note's decision 9 says the manual is distributed with the source archive, and this change's extension would widen the gap it already has.

## 6. Validation

- [ ] 6.1 The manual: `make docs` (or 1.2's command): exit 0, no warning, the seconds and HTML count against 1.2's, and the count of built pages holding `machinome-needs` (design.md: 58 with `join-studio`'s pages; record the actual count and explain a difference).
- [ ] 6.2 Show the build's refusal once on the bench: delete the declaration from one page, run 6.1's command (exit 1, the warning naming the page), restore it (`git diff` of the page against 4.1 empty).
- [ ] 6.3 The rendering, looked at: photograph at 1200 and 390 pixels wide, into the scratch directory, the installation page's list and the tops of `tutorial/04-relations`, `tutorial/10-share`, `howto/film-a-movie` and `howto/freecad-assemblies`; read each picture; record `document.documentElement.scrollWidth` of the installation page at 390 (expected 390) and the line each page shows, verbatim.
- [ ] 6.4 `packages/machinome-viewer/scripts/check-docs-browser.py` on 6.1's HTML with the bench venv: exit 0; record pages, viewports, local links, the three checks, reference examples and browser errors (design.md probe 7: 12, 2, 271, passed, 2, 0).
- [ ] 6.5 The tutorial's declarations proved (design.md probe 3, rerun on the changed tree in the scratch directory): `machinome build --all` and `machinome test --all` with every node package but `cadquery` and `build123d`, and the mesh engine, refused; `c01`, `c02`, `c03` and `first` with `machinome.node.build123d` refused too; `c04` with it refused (exit 1, the message). Record exits, seconds and the test summary.
- [ ] 6.6 The modules of design.md Decision 9 on the bench venv, one pytest process at a time, none while another bench's suite runs: `test_docs_structure.py`, `test_manual_extras.py`, `test_repository_layout.py`, `test_kernel_extras.py`, `test_release_records.py`, `test_docs_exports.py`, `test_sphinx_ext.py`, `test_tutorial_counter.py`. Record passed, skipped and subtests for each against 1.3.
- [ ] 6.7 `flake8 --max-line-length=89` of the changed Python files: 0 lines. `git -C <bench> status --short`: only this change's files.

## 7. The record of the change

- [ ] 7.1 Complete `evidence.md`: every command of groups 1 to 6 with its exit and counts, the reds with their reasons, the pictures' paths and what was read in them, the table of declarations as built (pages per extra).
- [ ] 7.2 Sync the delta specs into `openspec/specs/user-documentation/spec.md` and `openspec/specs/framework-contributor-guidance/spec.md`; `openspec validate --specs --strict` (or the CLI's equivalent) green.
- [ ] 7.3 Archive the change (`openspec archive manual-extras`), checking the archive holds `evidence.md`; `openspec validate --strict` on what remains.
- [ ] 7.4 Append the cycle's progress entry to `workflow/ongoing/release-0.9.md` at the root ("Progress"), in the shape of the entries there: the decisions accepted, ADR-195, the counts, the validation.
- [ ] 7.5 Stop before committing and report. The implementation commit, the suite at the cycle's head and the integration into the line are the orchestrator's; a push, a tag and an upload are the pilot's.
