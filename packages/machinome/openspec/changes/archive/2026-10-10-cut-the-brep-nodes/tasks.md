## 1. Evidence baseline

- [x] 1.1 Record the base: `git -C <bench> log --oneline -1` is the planning commit on top of 84757c38 (or the line's head the orchestrator names), the worktree clean but this change; start `evidence.md` in this change with it.
- [x] 1.2 Make the bench venv on the base's tree: `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12`. Expected: 179 packages resolved, three `__editable__` `.pth` files (the core and the two engines), each holding its package directory. Record the base suite count the second cycle measured on the same tree and recipe (its evidence, 9.1): 4786 passed, 20 skipped, 6831 subtests. Do not rerun it. One suite at a time.
- [x] 1.3 Record the lint base: `env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-engine-brep/machinome ../machinome-engine-mesh/machinome | wc -l` (expected 759, design.md probe 10). Name the paths; a glob passed through `env -C` is expanded in the caller's directory.
- [x] 1.4 Record the sweep base: the second cycle's counts (design.md, Decision 14): 63 repositories, 130 rows, 121 ok, 0 expected, 3 unexpected, 0 timeout, 6 no-model, 2 skipped. Do not rerun it here.

## 2. Red first, at the base's paths (nothing moves in this group)

- [x] 2.1 `tests/test_repository_layout.py`: `EXTENSIONS` and the generalised group of design.md Decision 10 (`test_each_extension_directory_holds_only_what_distinguishes_it`, `test_each_extension_manifest_is_a_portion_of_the_set`, `test_each_extension_readme_names_its_install_and_the_licence`, `test_each_portion_resolves_from_its_package`, `test_the_core_node_package_holds_no_extension_module`, `test_every_sibling_is_in_the_table`; `test_the_core_engine_package_holds_only_the_seams` unchanged); the module docstring names the node packages. Run the module. Expected red: the four node subtests of the four per-package tests (no directory; each module resolves under `packages/machinome/`), and `test_the_core_node_package_holds_no_extension_module` (the four modules are there). Green: the engine subtests, `test_every_sibling_is_in_the_table`, the README and guide tests (no node directory yet). Record each reason.
- [x] 2.2 `tests/test_kernel_extras.py` (Decision 10): `EXTRAS` for the four node extras, `PACKAGE_REQUIREMENTS` with the four manifests' sets of design.md Decision 2, `test_every_node_package_requires_the_brep_engine` in place of `test_every_kernel_extra_includes_the_brep_extra`, `test_no_node_extra_includes_the_mesh_engine` and `test_cadquery_carries_one_range_wherever_it_is_named` reading the sibling manifests, the docstring. Run it. Expected red: `test_each_extra_lists_what_its_module_needs` subtests `cadquery`, `build123d`, `step`, `molejo` (the core lists the kernels), the requirements test (`FileNotFoundError` on the node manifests), the brep-engine test (no node manifest), the lock test (no node package in `uv.lock`).
- [x] 2.3 `tests/test_core_kernel_free.py` (Decision 10): the two core censuses keep the template alone, `test_the_extension_packages_import_only_their_kernels` with the five entries, `EXTRA_OF`'s and `SEAMS`' node keys spelled `machinome-node-<x>/machinome/node/<x>.py`, the seams test reading both scans, the docstring. Run it. Expected red: both core censuses (they find the four), the portion census (it finds the engines alone), `test_each_kernel_module_checks_its_kernel_first` (`KeyError` on the four portion keys), `test_kernel_modules_are_named_only_at_the_seams` (the step key is absent).
- [x] 2.4 `tests/test_leaf_contract_reach.py`: `LEAVING` through `importlib.util.find_spec(f'machinome.node.{name}').origin`; the two `ALLOWED` reasons of Decision 10. Run it: green. Its red without this edit is design.md probe 7 (six `FileNotFoundError`); record it there by reference.
- [x] 2.5 `tests/test_docs_structure.py`: `test_the_installation_page_names_the_extension_distributions` in place of the engines' test, the six names written out. Run it. Expected red: the four node distributions are not on `start/install.rst`.
- [x] 2.6 `tests/test_supported_node_types.py`: `absent` among the names `test_the_module_defines_only_the_table_and_its_readers` expects, and `AbsentPackageTest` of Decision 10 (a subprocess removing `<repository>/packages/machinome-node-step` from `sys.path` before importing `machinome`). Run it. Expected red: the names test (`absent` is not defined), and every door of `AbsentPackageTest` (the module is in the core and imports; no refusal); `machinome.node.cadquery` imports.
- [x] 2.7 `tests/test_markings.py`: `ArtworkSeamTest.test_a_stale_marking_without_the_reducer_package_is_refused` (Decision 10). Run the class. Expected red: the build succeeds and writes the two marking artifacts (the reducer is in the core).
- [x] 2.8 Record in `evidence.md` every red of 2.1 to 2.7 with its reason and each green this group expects.

## 3. The cut

- [x] 3.1 For each of `cadquery`, `build123d`, `step`, `molejo`: `mkdir -p <bench>/packages/machinome-node-<x>/machinome/node`, then `git -C <bench> mv packages/machinome/machinome/node/<x>.py packages/machinome-node-<x>/machinome/node/<x>.py`. `git status` shows four renames with no content change.
- [x] 3.2 The links, from each node directory: `ln -s ../../LICENSE LICENSE`, `ln -s ../../LICENSES LICENSES`; `git add` them; `git ls-files -s packages/machinome-node-* | grep ^120000` lists eight with those targets.
- [x] 3.3 Run `test_repository_layout.py`, `test_core_kernel_free.py`, `test_leaf_contract_reach.py` and `test_supported_node_types.py` on the bench venv (its `.pth` lines name the core and the engines alone, so the four modules are on no path). Expected: `test_every_member_is_a_workspace_source` red (four directories, no source), the README and guide tests red (probe 7), the node link and core-node tests green, the directory, manifest and README tests red (no `pyproject.toml` or `README.md`), the resolution test red; the leaf-contract and table tests red (the modules cannot be found until the sync of 4.4). Show `test_every_sibling_is_in_the_table`'s red once: `mkdir <bench>/packages/machinome-node-stray`, the test fails naming it, `rmdir` it. Record each.

## 4. The manifests, the core's extras and the workspace

- [x] 4.1 The four `pyproject.toml` (design.md Decision 2, verbatim). Run `test_release_records.py`: `test_every_member_is_numbered_with_the_core` and `test_every_pin_between_members_is_compatible` green, `test_the_version_is_bumped_from_the_root` red (four manifests without a table). Show the pin test's red once: the step manifest's `machinome-node-cadquery~=0.8.1` edited to `machinome-node-cadquery>=0.8.1`, the test run (red naming that requirement), the pin restored (`git diff` of the manifest against 4.1's text empty).
- [x] 4.2 The four `README.md` (Decision 2, verbatim).
- [x] 4.3 The core's `pyproject.toml`: the block and the `dependencies` comment of Decision 4; nothing else in it changes (`git diff` shows the two hunks).
- [x] 4.4 The root `pyproject.toml` sources (Decision 7); `env -C <bench> /home/asa/.local/bin/uv lock` (expected: 183 packages, "Added machinome-node-build123d v0.8.1", "-cadquery", "-molejo", "-step"); `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12` (expected: seven `__editable__` `.pth` files, each holding its package directory; record them). Then `env -C /tmp <bench>/.venv/bin/python -c` printing `machinome.node.__path__` and each of the four modules' `__file__`. If the lock or the sync fails, stop and report the error. `git -C <bench> status --short` shows no build leaving under `packages/machinome-node-*`.
- [x] 4.5 Run the modules of group 2 and `test_node_root.py`, `test_import_step.py`, `test_manager_new.py`, `test_step_node.py`, `test_molejo_adapter.py`, `test_build123d_adapter.py`, `test_cli_lazy_imports.py` on the bench venv. Expected green but `test_release_records.py`'s bumped-from-root test (group 7), the layout README and guide tests and the docs page test (group 10), `test_supported_node_types.py`'s names test and `AbsentPackageTest`, and the markings test of 2.7 (group 5), whose reds are now the cut's: a plain `ModuleNotFoundError` naming the module with no extra, the root's `ImportError: cannot import name 'step'` and `hasattr` `False`; the marking build's `No module named 'machinome.node.build123d'`. Record them. Anything else red is investigated before group 5.
- [x] 4.6 `tests/test_node_root_exports_nothing.py` (Decision 10), its blind spot red first: plant, in a comment of the moved `step.py`, the root import of `StepNode` (written in the file as the two halves `from machinome.node ` and `import StepNode` joined on one line); the gate as it is passes; repoint it to merge `scan()` of every `packages/machinome-*` with its paths prefixed by the directory's name; it fails naming `machinome-node-step/machinome/node/step.py`; remove the plant (`git diff` of `step.py` empty); green. Record both runs.
- [x] 4.7 `tests/test_core_names_no_split_words.py`, unchanged: plant the mesh-quality word in a comment of the moved `molejo.py`; the gate fails naming `machinome/node/molejo.py`; remove the plant (`git diff` empty); green. Record both runs.

## 5. The absent node package (design.md Decision 5)

- [x] 5.1 `machinome/node/supported.py`: `absent(key)` and `load`'s branch, verbatim; `machinome/node/__init__.py`: the two imports, `_AbsentNodeType` and its installation, verbatim, and the docstring sentence. `git diff` of the two modules shows nothing else.
- [x] 5.2 Run `test_supported_node_types.py` and `test_markings.py::ArtworkSeamTest`: green. Then `test_node_root.py`, `test_node_root_exports_nothing.py`, `test_cli_lazy_imports.py`, `test_import_step.py`, `test_leaf_addresses.py`, `test_manager_new.py`, `test_cli.py`, `test_kernel_extras.py`: green (design.md probe 3).
- [x] 5.3 By hand on the bench venv, from `/tmp`, with `machinome-node-step` uninstalled (`uv pip uninstall --python <bench>/.venv/bin/python machinome-node-step`): `machinome import-step` on a STEP file prints the refusal naming `machinome[step]` and exits 1; then `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12` restores it ("Installed 1 package"). Record both.

## 6. The manual's path (design.md Decision 6)

- [x] 6.1 Red first: a fresh venv under the scratch directory installing `packages/machinome/docs/requirements.txt` alone, then `env -C <bench>/packages/machinome <venv>/bin/python -m sphinx -b html -W --keep-going docs <scratch>/html-red`. Expected: exit 1, five `autodoc: failed to import` warnings (`CadQueryNode`, `Build123dNode`, `Build123dSheetNode`, `StepNode`, `MolejoNode`), design.md probe 8.
- [x] 6.2 `docs/conf.py`'s first lines, verbatim. The same build into `<scratch>/html`: success.

## 7. One version for the set, and the lint

- [x] 7.1 The root `.bumpversion.cfg`: the eight tables of Decision 8, after the mesh engine's, no comment. `test_release_records.py` green.
- [x] 7.2 The bump on a copy (design.md probe 9): the root's `.bumpversion.cfg` and the files it names copied under the scratch directory, made a git repository, `bump2version --no-commit --no-tag --new-version 0.9.0 patch`; record that `git diff -U0` changes the 28 statements of probe 9 in 11 files and nothing else. Nothing is written in the bench.
- [x] 7.3 `packages/machinome/setup.cfg`'s two ignores of Decision 9, in place. `env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests` and the six `../machinome-*/machinome` paths named: expected 759 lines, equal to 1.3's once the `../machinome-node-<x>/` prefix is stripped; `grep -c E402` of it: 2 (`tests/test_couplings.py`, as at the base).

## 8. `scripts/check-dist`

- [x] 8.1 Red first: `env -C <bench> <bench>/.venv/bin/python scripts/check-dist` fails "machinome-node-build123d has no smoke in scripts/check-dist"; record it.
- [x] 8.2 The `NODE` template and the four rows of Decision 11; the core's and the engines' rows unchanged (`git diff` shows no line of them changed). `flake8 --max-line-length=89 scripts/check-dist`: 0.
- [x] 8.3 Run it. Expected: seven members built; `twine check --strict` passed for fourteen archives; each member's linked files in its sdist as regular files equal to the root's; the install naming the core's wheel with `[openscad,stl]` and `machinome[<through>]` for the six siblings with seven `--find-links`; each node's line printing its version 0.8.1, its module file inside the venv and its volume (1000, 24, 120, about 477.89); the three licence files listed for each; `machinome --help` exit 0; the last line saying nothing was uploaded. Record the archives' member counts (each node 18 and 8) and `git -C <bench> status --short` afterwards (nothing new but ignored leavings).

## 9. The records

- [x] 9.1 `HISTORY.rst`: the `Unreleased` bullet of Decision 12, verbatim, after the second cycle's.
- [x] 9.2 `docs/project/changelog.rst`: the bullet of Decision 12, verbatim, after the engines'. `test_release_records.py` and `test_profile_documentation.py` green.
- [x] 9.3 `docs/start/install.rst`: the four rows' cells, the example refusal and the first sentence of "Packages and licences" of Decision 12, each rewrapped at the page's width, the rest of the page unchanged. `test_docs_structure.py` green.
- [x] 9.4 The root `README.md`: the four rows of Decision 12 after the engines'. The layout gate's README test green.
- [x] 9.5 `CONTRIBUTING.rst`: the pip block of Decision 12, in place. The layout gate's guide and link tests green.
- [x] 9.6 `docs/architecture.md`: the Map row, the Node model row's edits and the sentences of Decision 12.
- [x] 9.7 `docs/adrs/NODE/ADR-184-an-absent-node-package-is-refused-by-its-extra-at-its-import.md` (Decision 12), Status Proposed; its index entry under NODE after ADR-181 in `docs/adrs/README.md`, and ADR-183's index line naming the B-rep node packages.
- [x] 9.8 The whole layout gate, the docs and the release tests green.

## 10. Validation

- [x] 10.1 The whole suite, one process, from the framework's directory on the bench venv: `env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider`, output to a file under the scratch directory. Record passed, skipped (each reason) and failed. Expected: no failure; 20 skips, the base's (16 the viewer, networkx, the `jscad` command, two vendor STEP); the passed count the base's 4786 with each test this change adds, renames or removes named.
- [x] 10.2 The lint of 7.3 again on the final tree; record the count.
- [x] 10.3 The manual as in 6.2 on the final tree: success.
- [x] 10.4 `scripts/check-dist` as in 8.3 on the final tree, and once on a clean copy of the tracked tree (`git ls-files -z | tar --null -T - -cf -` unpacked under the scratch directory, links kept), recording the archives' counts from both (the clean copy's core sdist: 1015, its wheel 122, design.md probe 4).
- [x] 10.5 The universe sweep with the command of design.md Decision 14 (`--timeout 300`, the ten tables, `--json` under the scratch directory). Expected: the counts of 1.4; any row that differs is reported with its explanation, not worked around.
- [x] 10.6 Git: `git -C <bench> status --short` shows the four modules as renames, the four node directories' four files each as added (the links with mode 120000), ADR-184 added, and the edited files; `git ls-files -ci --exclude-standard | wc -l` still 34.
- [x] 10.7 `env -C <bench>/packages/machinome openspec validate cut-the-brep-nodes --strict`.
- [x] 10.8 Stop before any commit and report to the orchestrator: the reds of groups 2 to 4, 6.1 and 8.1, the counts of 1.2, 4.4, 7.2, 7.3, 8.3 and 10.1 to 10.6, and anything that departed from the design. Resume only on the orchestrator's message.

## 11. Records closing (after the orchestrator's review)

- [x] 11.1 ADR-184 promoted to Accepted; `docs/adrs/README.md` updated; ADR-167's, ADR-181's and ADR-183's status lines and index lines note "amended by 184"; `docs/architecture.md` checked against it.
- [x] 11.2 `env -C <bench>/packages/machinome openspec archive cut-the-brep-nodes -y` (the deltas synced into `packages/machinome/openspec/specs/`), then `openspec validate --specs --strict` there.
- [x] 11.3 The root's `workflow/ongoing/monorepo-0.9.md`: cycle 3 marked done with its branch, the planning commit, ADR-184, the suite count of 10.1, the manual, the check-dist result with the clean copy's counts, the lock and the sweep's counts, as cycles 1 and 2 are recorded.
- [x] 11.4 `evidence.md` complete; the implementation commit is the orchestrator's, never amending the planning commit; nothing pushed.
