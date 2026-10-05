## 1. Evidence baseline

- [ ] 1.1 Record the base: `git -C <bench> log --oneline -1` is 815ceb9 (or the line's head the orchestrator names), the worktree is clean but for this change's planning files; start `evidence.md` in this change with it.
- [ ] 1.2 Re-measure with this change's scripts and record the output in `evidence.md`: `python gate-prototype.py <bench> --files` (expected: `machinome` 6 files / 8 offences, `tests` 291 / 491, `docs` 20 / 58), `python repoint.py <bench>` (expected: `machinome` 3 files, `tests` 290 files with 1 listed site, `docs` 18 files; six `HAND` files), and the probe of `vars(machinome.node)` (21 names in `__all__`; `ExtraUnavailable`, `NODE_TYPES`, `StlRenderStart`, `find_spec`, `import_module` public and not submodules). A different count is reported before any edit.
- [ ] 1.3 Check that `moved-names.toml`'s 21 rows equal the root block (`from = "root-cleanup"`) of the workspace's `scripts/rewrite-projects.d/root-cleanup.toml`, name for name (read-only); record the result.
- [ ] 1.4 Run the suite once on the base and record the count (the brep-mesh integration recorded 4568 passed, 4 skipped); one suite at a time.

## 2. Red tests first (each run and recorded red, with its reason, before the code it proves)

- [ ] 2.1 Write `tests/test_node_root_exports_nothing.py` (design.md, Decision 6): G1, the 21 names and modules written out, each refused by `from machinome.node import <name>` (composed with an f-string), `getattr` and `hasattr` with Decision 3's exact text, each importable from its module; `__all__ == []`; the star import binds nothing; every public name of `vars(machinome.node)` is a submodule; every class of every row of `supported.NODE_TYPES` refused naming `machinome.node.<key>`. G2, the scan of `gate-prototype.py` over the three zones, its planted self-test samples spelled in pieces. Red: the root resolves the 21, `__all__` has 21 entries, five public names are not submodules; the scan finds 6 + 291 + 20 files.
- [ ] 2.2 `tests/test_kernel_extras.py`: `EXTRAS` gains `'jscad': set()` and `'stl': set()` and the `all` line names both; a new test asserts every key of `supported.NODE_TYPES` is an extra. Red: `pyproject.toml` declares neither.
- [ ] 2.3 `tests/test_docs_structure.py`: `KernelExtrasTest.EXTRAS` gains `jscad` and `stl`. Red: `docs/start/install.rst` names neither `machinome[jscad]` nor `machinome[stl]`.
- [ ] 2.4 `tests/test_manager_new.py`: `EXPECTED_INIT` reads `from machinome.node.solid2 import Solid2Node`, and the CadQuery template's expectation `from machinome.node.cadquery import CadQueryNode`. Red: both templates import from the root.
- [ ] 2.5 `tests/test_import_step.py`: the generated `parts.py` holds `from machinome.node.step import StepNode`, `assembly.py` `from machinome.node.assembly import AssemblyNode`, and neither holds `from machinome.node import`. Red: the generator writes the root spelling.
- [ ] 2.6 `git mv tests/test_node_lazy_exports.py tests/test_node_root.py` and revise it by hand (Decision 8): export tests become refusal tests; the import-cost tests import `machinome.node.step`, `machinome.node.cadquery` and the others instead of naming a root export; the broken- and absent-backend tests go through `machinome.node.step` and `from machinome.node import step` (refusal unmodified; broken install spliced naming `step`); the parameter and moved-port tests stay; the star-import test asserts nothing is bound; the docstring says what the root is now. Red: the root resolves the names.
- [ ] 2.7 Run 2.1-2.6 together and record each failure's reason in `evidence.md`.

## 3. Implementation outside the root (the suite stays runnable: nothing yet stops resolving)

- [ ] 3.1 `pyproject.toml`: the extras `jscad = []` and `stl = []` with their comments (Decision 7), and `all` naming `jscad,stl`. 2.2 green.
- [ ] 3.2 The two templates under `machinome/manager/templates/project/root/` import from `machinome.node.solid2` and `machinome.node.cadquery`; `tests/test_core_kernel_free.py`'s `SEAMS` admits `machinome/manager/templates/project/root/cadquery.py` naming `machinome.node.cadquery`, and the root moves from `SEAMS` to `TABLE_READERS`. 2.4 green; `test_core_kernel_free.py` green.
- [ ] 3.3 `machinome/manager/import_step.py` composes its two import lines from the classes it writes for (`f'from {cls.__module__} import {cls.__name__}'`, `StepNode` from the loaded `step` module, `AssemblyNode` from `machinome.node.assembly`), spelling no node type's module. 2.5 green; `test_core_kernel_free.py` still lists it among `TABLE_READERS`.
- [ ] 3.4 Docstrings: `parameters.py` (its example import block per module), `node/adapters/__init__.py` (the root spellings are no longer "unchanged"; the refusal message unchanged), `node/build123d.py` (`machinome.node` "resolves its adapters on first use"), `node/supported.py` (the `classes` column's readers: the root's refusal and `load`'s message; "The node root's export table" becomes its refusals).

## 4. Repoint the suite and the manual's examples (still before the root: every test file must import from the modules first)

- [ ] 4.1 Run `python openspec/changes/root-cleanup/repoint.py <bench> --diff`, compare its counts with `evidence.md` (task 1.2) and review the diff of every split statement and of `docs/`; then run it with `--apply`.
- [ ] 4.2 Hand edits the script lists or cannot judge: `tests/test_external_wrapper_identity.py:260` (the f-string composes one import line per module), and the tests whose subject is the root (Decision 8): `test_supported_node_types.py` (the root identity and `__all__` membership become the refusal), `test_leaf_addresses.py` (docstring; the root-identity test becomes the refusal), `test_openscad_node.py:86-88` (the root identity becomes the refusal), `test_motion_package.py:136` (renamed `test_a_node_class_is_imported_from_its_module`, asserting the refusal names `machinome.node.assembly`), `test_markings.py:476` (`PublicModuleTest`: the four names are refused at the root naming `machinome.node.markings`), `test_leaf_capability_set.py:144` (walk the classes of the table's modules and the core's leaf bases instead of `machinome.node.__all__`, which becomes empty). Read every docstring the script repointed in place for meaning (e.g. `test_leaf_addresses.py:13`).
- [ ] 4.3 `tests/leaf_contract_golden.py`: `ROOT_CLEANUP_EXPECTED`, in the shape of `mesh_engine_golden.py`'s `BREP_MESH_EXPECTED`: under `--check`, a differing `digest` of a source record is reported as expected, every other field must be identical; the JSON is not re-recorded (Decision 9).
- [ ] 4.4 Run the suite. Expected: green but for 2.1's G1 and 2.6 (the root still resolves the names) and 2.1's G2 for what the script leaves (`machinome/node/__init__.py`'s docstring, the changelog and the upgrading page). Anything else red is investigated before the root changes. `python gate-prototype.py <bench> --files` records the remaining offences.

## 5. The root, last

- [ ] 5.1 Rewrite `machinome/node/__init__.py` (Decisions 1-3): no `_EXPORTS`, no eager import of `base` or `NODE_TYPES`; `_DEFINED_IN` (the core's twelve) and the node types' names derived from `supported.NODE_TYPES` on the first refused name; `__getattr__` refusing `_MOVED`, then the 21 with Decision 3's text (a mapping lookup, never a comparison with a string literal), then a submodule, else `AttributeError`; `__all__ = []`; `import_module`, `find_spec` and `ExtraUnavailable` bound privately; `_namespace_portions`, `_load`, `_submodule` and `__dir__` kept; the docstring rewritten (what the root is, why it exports nothing, the refusals, the submodule doors). Why last: refusing before group 4 would fail 291 test files at their import line at once and hide whatever else broke.
- [ ] 5.2 Run 2.1 and 2.6 green; run `test_no_class_name_recognition.py`, `test_core_names_no_scad.py`, `test_core_names_no_split_words.py`, `test_core_kernel_free.py`, `test_cli_lazy_imports.py`, `test_motion_package.py` and `test_leaf_addresses.py` green.

## 6. Documentation

- [ ] 6.1 `docs/reference/api.rst`: the Nodes section's sentence (`:174`) states each class is imported from its module and the root exports nothing; the frames section (`:652`) drops "and from ``machinome.node``"; the twelve directives already at module addresses (task 4.1).
- [ ] 6.2 `docs/concepts/values.rst:54` and `docs/tutorial/03-dimensions.rst:24`: node classes come from their modules under ``machinome.node``.
- [ ] 6.3 `docs/start/install.rst`: rows for `machinome[jscad]` (installs nothing; `JScadNode` needs the `jscad` command from npm) and `machinome[stl]` (installs nothing; trimesh comes with the package); the sentence on `JScadNode` and `StlNode` rewritten; `:93` names the module import the refusal answers; `all` described as every extra. 2.3 green.
- [ ] 6.4 `docs/howto/backends.rst`: the node-type table gains each class's module and extra, all eight node types and nine classes (its "Needs: nothing" for the OCCT classes corrected to their extras).
- [ ] 6.5 `docs/project/upgrading.rst`: a section "Import every name from its module (unreleased)": the root exports nothing, nothing aliases a former spelling, the refusal's text for one name, the 21 names mapped to their modules written as name → module (no root address), and that each part a rewrite touches rebuilds once to the same bytes; the "Update port imports" example imports per module.
- [ ] 6.6 `docs/project/changelog.rst`, Unreleased: this cycle's bullet (the root exports nothing, the refusal, the gate, `machinome[jscad]` and `machinome[stl]`, the generated source; BREAKING notes), and the `lean-install` bullet's two root spellings revised in place to the shipped state (design.md, Decision 10).
- [ ] 6.7 `docs/architecture.md` (`:315-347`): the root's paragraph and the doors (Decision 5).
- [ ] 6.8 The gate's G2 green over all three zones; `python gate-prototype.py <bench>` finds nothing.

## 7. The plan's cycle entry

- [ ] 7.1 `workflow/ongoing/lean-core.md`: item 3 of "The next phase" marked done with the branch, the counts of task 1.2, the suite count, and the follow-ups outside the framework (the studio's two skills; machinome-mechanics' four files; the workspace's `scripts/load-projects.d/root-cleanup.toml`); "State of the campaign" notes that layer 1 is complete once the orchestrator's validation and integration are recorded.

## 8. Suite and checkpoint

- [ ] 8.1 Run the full suite once and `flake8 --max-line-length=89 machinome tests`; record both in `evidence.md`.
- [ ] 8.2 `openspec validate root-cleanup --strict`.
- [ ] 8.3 Stop before any commit and report to the orchestrator: the red evidence of group 2, the suite and lint results, the gate at zero, the repoint counts, the hand edits, anything that departed from the design. Resume only on the orchestrator's message.

## 9. Empirical validation (the orchestrator runs it; the applier waits paused and records the results it is handed)

- [ ] 9.1 The workspace pass over every project repository (`scripts/rewrite-projects --apply`, announced to the pilot; Voron-2's `shape()` call sites by hand), then the universe sweep with the nine earlier tables and this change's `moved-names.toml` as `scripts/load-projects.d/root-cleanup.toml`: 117 or more `ok`, zero `expected`, the 2 pre-existing `unexpected`, 6 no-model.
- [ ] 9.2 The goldens, each `--check` in a fresh process: `leaf_contract_golden.py` (only `digest` fields differ, reported as expected), `scad_presentation_golden.py`, `expression_type_golden.py`, `brep_engine_golden.py`, `mesh_engine_golden.py`: no other difference.
- [ ] 9.3 `Locks/Pin_tumbler_lock` after the pass, on the module spelling: `machinome build` (rewritten parts rebuild once; the 15 `.scad` hashes identical to the line's before the pass), then `machinome test --mesh --no-verdict-store`: the brep-mesh validation's 24 outcomes and its 2573 verdicts identical.
- [ ] 9.4 `machinome new` under the three installs of the `openscad-out` leg (every extra; CadQuery only; neither) and `machinome import-step` on the Internal-Cycloidal-Actuator's document: the generated import lines per module, the generated projects building and loading.
- [ ] 9.5 The extras: metadata built with the pinned backend (`setuptools>=65.5,<77`) shows `Provides-Extra: jscad` and `stl` with no requirement; `pip install "<bench>[jscad,stl]"` in a throwaway environment warns of no unknown extra.
- [ ] 9.6 The doors with SolidPython refused (finder helpers, throwaway processes): `from machinome.node import Solid2Node` meets the root's refusal naming `machinome.node.solid2`; `from machinome.node.solid2 import Solid2Node` and `from machinome.node import solid2` meet the module's refusal naming `machinome[solid2]`.
- [ ] 9.7 The manual: the docs job's build (`docs/requirements.txt`, warnings as errors) succeeds with every directive at its module address.
- [ ] 9.8 Record every leg's result in `evidence.md`.

## 10. Records

- [ ] 10.1 ADR-181 (NODE), "The node package's root exports nothing" (design.md, ADRs), with its amendments of ADR-167, ADR-169 and ADR-179 and its reading of ADR-166; the ADR index updated (and the amended entries' "amended by 181"); `docs/architecture.md` checked against it.
- [ ] 10.2 `openspec archive root-cleanup` (the delta specs synced into `openspec/specs/`), then the two scenario titles of `scenario-titles.tsv` replaced in their specs, the `cli-startup-cost` requirement's rename checked, and `openspec validate --specs --strict`.
- [ ] 10.3 `evidence.md`, `moved-names.toml`, `gate-prototype.py`, `repoint.py` and `scenario-titles.tsv` stay in the archive; the workspace copy of the moved-names table is the orchestrator's.
- [ ] 10.4 The implementation commit, on the orchestrator's word, never amending the planning commit; nothing pushed.
