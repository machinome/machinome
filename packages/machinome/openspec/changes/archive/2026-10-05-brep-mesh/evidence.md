# Evidence — `brep-mesh`

The ninth cycle of layer 1 of the lean-core campaign, the second of the phase
"The next phase: the architecture ready for the split"
(`workflow/ongoing/lean-core.md`). Worktree
`machinome/WTs/v0.8-split-brep-mesh`, branch `v0.8-split-brep-mesh`, cut from
`v0.8-split` at faf1c80 ("lean-core plan: openscad-out integrated; next
brep-mesh"). Planning commit dfc9681 ("brep-mesh: plan the engines' rename
to brep and mesh (ratified 4 October 2026)"), ratified by the pilot on
4 October 2026 with every recommendation of design.md's Open Questions
taken but the second, ruled the other way and written into the artifacts:
the run's choice is its engine (`SOLID_TEST_ENGINE`, `ComparisonPolicy.engine`,
`ENGINES`, the `engine` argument, the messages). Every command below ran with
`env -C <worktree>`, `PYTHONPATH=<worktree>` and the workspace venv (Python
3.12.3); pytest ran one process at a time, never two of this cycle's at once.
The pilot's other sessions ran `machinome test` on Voron-2 under
`/mnt/data/machinome-projects` throughout; on the orchestrator's instruction
those do not block this cycle's runs. No run of this cycle died with "Too
many open files".

```
$ git -C <bench> log --oneline -2
dfc9681 brep-mesh: plan the engines' rename to brep and mesh (ratified 4 October 2026)
faf1c80 lean-core plan: openscad-out integrated; next brep-mesh
```

## 1. Baseline on the unmodified tree (dfc9681)

### 1.1 The facts design.md rests on, re-measured

**The gate's red count**, `python3 openspec/changes/brep-mesh/gate-prototype.py .`
(Python 3.11.14, and the workspace venv's 3.12.3 alike):

```
  168 machinome/test.py
   65 machinome/exact_engine.py
   38 machinome/occt/engine.py
   32 machinome/node/flexible.py
   27 machinome/manifold/engine.py
   26 machinome/node/exact_leaf.py
   26 machinome/node/fusion.py
   22 machinome/manager/test.py
   19 machinome/_verdict_store.py
   19 machinome/mesh_engine.py
   14 machinome/node/build123d.py
   14 machinome/node/step.py
   12 machinome/exact_cache.py
   10 machinome/exact_artifacts.py
   10 machinome/node/cadquery.py
    7 machinome/node/leaf.py
    7 machinome/occt/__init__.py
    4 machinome/manifold/__init__.py
    4 machinome/node/__init__.py
    4 machinome/node/base.py
    4 machinome/node/sheet_leaf.py
    3 machinome/extras.py
    3 machinome/node/internal.py
    2 machinome/core/processes.py
    2 machinome/node/molejo.py
    2 machinome/simulation/__init__.py
    1 machinome/core/builder.py
    1 machinome/manager/import_step.py
    1 machinome/motion/couplings.py
    1 machinome/motion/joints.py
modules: 30  occurrences: 548
```

30 modules, 548 occurrences, module for module design.md Decision 9's table.
The permanent gate (`tests/test_core_names_no_split_words.py`, task 2.1), its
`scan()` run as a script on the same tree, reports the same
`modules: 30  occurrences: 548`.

**The shadowing probe** (scratch package `pkg.engine` whose `__init__`
defines `brep()` importing the submodule `pkg.engine.brep`):

```
before function
after module
TypeError: 'module' object is not callable
```

**The word `exact` in the core's text** (strings, docstrings, comments, an
f-string read whole; `exactly` and `exactness` not counted), with the gate's
W3 applied to each token (scratch `count_exact.py`):

```
word exact in text: 312 W3 caught: 196 others: 116
```

**The test files naming a moved name.** design.md's grep is not written out;
the nearest reconstruction, `git grep -lE` over `tests/*.py` for the moved
modules, classes, members, flags, extras, values and recipe identities
(`exact_engine|mesh_engine|machinome\.occt|machinome\.manifold|exact_cache|
exact_artifacts|exact_leaf|ExactLeafNode|ExactEngine|ExactCommon|ExactShape|
--faceted|--exact\b|machinome\[occt\]|machinome\[manifold\]|exact-fusion|
faceted-fusion|'exact'|'faceted'|\.exact\b|"occt"|"manifold"|KERNELS|\.kernel\b|
kernel=` and `SOLID_TEST_KERNEL`), finds 77 files, `test_tutorial_counter.py`
among them; design.md's 78 counted one more by a pattern this
reconstruction does not reproduce. A wider grep (data files and every
`_exact_`/`_faceted_` private) finds 103. The baseline below ran the union.

### 1.2 The five goldens

Each `--check` in a fresh process, before any source change:

```
leaf_contract_golden       golden comparison: 7 fixtures, 77 values, 0 differences                                (7.7 s)
scad_presentation_golden   golden comparison: 34 values, 0 differences, 9 presentation files absent as expected    (5.4 s)
expression_type_golden     golden comparison: 17 values, 0 differences                                           (2.2 s)
exact_engine_golden        golden comparison: 7 fixtures, 0 differences                                          (7.3 s)
mesh_engine_golden         AttributeError: '_MeshPart' object has no attribute 'flexible'                        (1.5 s, exit 1)
```

**A pre-existing failure, found and repaired on the base.**
`tests/mesh_engine_golden.py` crashed on faf1c80 before measuring anything:
its stand-in `_MeshPart` predates `openscad-out`'s declared capability set
(ADR-178), under which `machinome.test._fast_geometry` reads `node.flexible`
directly. `openscad-out` checked three goldens and not this one, so the
breakage was not seen. The repair is the set's default on the stand-in,
`flexible = False` (one line, before any source change); with it the golden
holds on the base:

```
mesh_engine_golden   golden comparison: 1095 values, 0 differences, 2 expected (design.md Decision 4)   (161 s)
```

### 1.3 The touched suites, unmodified tree

The 83 test modules of the union of 1.1 and the nine tasks.md names, with the
cycle's own red tests stashed in scratch (the red edits restored from scratch
afterwards, byte for byte):

```
1983 passed, 24 warnings, 1869 subtests passed in 628.12s (0:10:28)
```

## 2. Red first (unmodified source)

The tests of group 2, each in the file tasks.md names:

- 2.1 `tests/test_core_names_no_split_words.py` (new): the rule as functions
  with its own unit cases, and the scan.
- 2.2 `tests/test_engine_package.py` (new): the seams' names and constants,
  no provider or kernel imported with the package, the seams surviving their
  providers' resolution, a portion resolving and a second core copy refused,
  the former addresses not found, no operation on the package; and (2.9) the
  memos and publication.
- 2.3 `tests/test_engine_doors.py` (new): R5, R1 (seam and memos, R25) and
  the stale B-rep fusion's build for the B-rep engine; R6, R3 and
  `machinome test --mesh` exiting 1 before building for the mesh engine. The
  finder helpers are used as they are, each refusal target passed explicitly
  (`OCP`, `manifold3d`, `machinome.engine.brep`).
- 2.4 `tests/test_kernel_extras.py`: `EXTRAS` and `MODULES` written to the
  new extras and addresses; `occt` and `manifold` absent.
- 2.5 `tests/test_leaf_capability_set.py` (contract 3, a declaration of 2
  refused, `BrepLeafNode` and its subclasses, `brep` by node type, no node
  class defining `exact`, the former module not found, R24) and
  `tests/test_leaf_contract_version.py`.
- 2.6 `tests/test_manager_test.py`: the comparison-policy class rewritten to
  the engine (`ComparisonEngineSelectionTest`) and the new cases: `ENGINES`,
  the policy's field, the `engine` argument and `kernel=` refused by Python,
  the flags into `args.engine`, the former flags unrecognised (exit 2), R7
  for the former values, R30 for `SOLID_TEST_KERNEL` whatever its value and
  flag, the runner exiting 1 with R30 before building, R31, R8, R11, R12,
  `IntersectionStats.brep`.
- 2.7 `tests/test_verdict_store.py` `ThePathWords`: the in-process keys carry
  `brep`/`mesh`, the record bit `_BREP`, and a record kept under the former
  word `exact` is not served (the default run's policy, so the old tree keys
  on `exact` and serves the stub: red for the right reason).
- 2.8 `tests/test_backend_neutral_materialization.py` `RecipeIdentityTest`.
- 2.10 `tests/test_vet_universe.py`.

2.11, the run (`--tb=line`):

```
110 failed, 77 passed, 336 subtests passed in 25.38s
```

The failing ids, verbatim:

```
    FAILED tests/test_backend_neutral_materialization.py::RecipeIdentityTest::test_a_brep_fusion_is_brep_fusion_v1
    FAILED tests/test_backend_neutral_materialization.py::RecipeIdentityTest::test_a_mesh_fusion_is_mesh_fusion_v1_and_its_stl_records_it
    FAILED tests/test_backend_neutral_materialization.py::RecipeIdentityTest::test_a_mesh_fusion_under_the_former_recipe_rebuilds_the_same
    FAILED tests/test_core_names_no_split_words.py::TheCoreNamesNoSplitWordsTest::test_no_module_names_the_split_but_by_its_two_words
    FAILED tests/test_engine_doors.py::TheBrepEngineDoorsTest::test_a_stale_brep_fusion_refuses_at_its_build
    FAILED tests/test_engine_doors.py::TheBrepEngineDoorsTest::test_the_memos_and_publication_name_their_needs
    FAILED tests/test_engine_doors.py::TheBrepEngineDoorsTest::test_the_provider_the_seam_and_the_point_of_use_refuse
    FAILED tests/test_engine_doors.py::TheMeshEngineDoorsTest::test_a_mesh_run_refuses_at_its_start_before_building
    FAILED tests/test_engine_doors.py::TheMeshEngineDoorsTest::test_the_provider_and_the_seam_refuse
    FAILED tests/test_engine_package.py::TheMemosAndPublicationTest::test_the_new_modules_import
    FAILED tests/test_engine_package.py::TheSeamsTest::test_importing_the_package_imports_no_provider_or_kernel
    FAILED tests/test_engine_package.py::TheSeamsTest::test_the_contracts_and_the_providers
    FAILED tests/test_engine_package.py::TheSeamsTest::test_the_package_defines_both_seams
    FAILED tests/test_engine_package.py::TheSeamsTest::test_the_package_holds_no_operation
    FAILED tests/test_engine_package.py::TheSeamsTest::test_the_seams_survive_their_providers_resolution
    FAILED tests/test_kernel_extras.py::KernelMetadataTest::test_all_names_every_kernel_extra
    FAILED tests/test_leaf_capability_set.py::ContractVersionThreeTest::test_a_declaration_of_two_is_refused_naming_both_versions
    FAILED tests/test_leaf_capability_set.py::ContractVersionThreeTest::test_the_core_speaks_contract_three
    FAILED tests/test_leaf_capability_set.py::TheBrepMemberTest::test_an_unassembled_internal_node_cannot_say
    FAILED tests/test_leaf_capability_set.py::TheBrepMemberTest::test_brep_answers_by_node_type
    FAILED tests/test_leaf_capability_set.py::TheBrepMemberTest::test_the_brep_leaf_base_and_its_subclasses
    FAILED tests/test_leaf_capability_set.py::TheBrepMemberTest::test_the_former_module_is_not_found
    FAILED tests/test_leaf_capability_set.py::TheSetHasDefaultsTest::test_a_self_materializing_leaf_answers_the_whole_set
    FAILED tests/test_leaf_contract_version.py::ContractVersionTest::test_a_matching_declaration_is_admitted
    FAILED tests/test_leaf_contract_version.py::ContractVersionTest::test_a_mismatched_declaration_is_refused_naming_both_versions
    FAILED tests/test_leaf_contract_version.py::ContractVersionTest::test_an_undeclared_subclass_is_not_checked
    FAILED tests/test_leaf_contract_version.py::ContractVersionTest::test_the_core_speaks_contract_three
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_a_flag_beats_the_environment
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_a_negative_epsilon_is_refused
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_a_non_numeric_environment_epsilon_is_refused
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_a_verdict_says_which_representation_supplied_it
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_an_empty_former_variable_is_unset
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_an_epsilon_offered_to_the_brep_engine_is_refused
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_an_epsilon_on_a_brep_run_is_refused_in_the_engines_words
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_an_unknown_engine_name_is_refused_naming_the_variable
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_an_unknown_explicit_engine_is_refused
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_flags_parse_into_an_engine_and_an_epsilon
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_mesh_without_an_epsilon_is_strict
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_brep_engine_accepts_a_placement_quantum
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_default_is_the_brep_engine
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_engine_argument
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_engines_are_brep_and_mesh
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_environment_epsilon_is_not_read_by_the_brep_engine
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_environment_quantum_is_read_under_both_engines
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_environment_selects_the_mesh_engine
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_environment_selects_the_mesh_engine_by_its_word
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_flags_parse_into_the_engine
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_framework_resolves_lazily_from_the_environment
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_mesh_run_line_and_note
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_placement_quantum_is_not_in_the_engine_group
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_policy_names_its_engine
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_runner_refuses_the_former_variable_before_building
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_runner_sets_the_policy_it_resolved
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_store_note_follows_the_mesh_label_and_the_quantum
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_summary_line_names_a_mesh_run
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_summary_line_names_the_quantum_beside_the_mesh_label
    FAILED tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_verdict_store_flags_are_not_in_the_engine_group
    FAILED tests/test_verdict_store.py::ThePathWords::test_a_brep_comparison_keys_on_brep
    FAILED tests/test_verdict_store.py::ThePathWords::test_a_brep_record_reads_back_with_the_brep_bit
    FAILED tests/test_verdict_store.py::ThePathWords::test_a_mesh_comparison_keys_on_mesh
    FAILED tests/test_verdict_store.py::ThePathWords::test_a_record_under_the_former_path_word_is_not_served
    FAILED tests/test_vet_universe.py::TheDeclarationTest::test_the_contract
    SUBFAILED(cls='AbstractBaseNode') tests/test_leaf_capability_set.py::TheBrepMemberTest::test_no_node_class_defines_the_former_member
    SUBFAILED(cls='ExactLeafNode') tests/test_leaf_capability_set.py::TheBrepMemberTest::test_no_node_class_defines_the_former_member
    SUBFAILED(cls='InternalNode') tests/test_leaf_capability_set.py::TheBrepMemberTest::test_no_node_class_defines_the_former_member
    SUBFAILED(cls='MolejoNode') tests/test_leaf_capability_set.py::TheBrepMemberTest::test_no_node_class_defines_the_former_member
    SUBFAILED(engine='brep') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_verdict_store_is_read_under_both_engines
    SUBFAILED(engine='mesh') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_verdict_store_is_read_under_both_engines
    SUBFAILED(extra='all') tests/test_kernel_extras.py::KernelMetadataTest::test_each_extra_lists_what_its_module_needs
    SUBFAILED(extra='brep') tests/test_kernel_extras.py::KernelMetadataTest::test_each_extra_lists_what_its_module_needs
    SUBFAILED(extra='build123d') tests/test_kernel_extras.py::KernelMetadataTest::test_each_extra_lists_what_its_module_needs
    SUBFAILED(extra='build123d') tests/test_kernel_extras.py::KernelMetadataTest::test_every_kernel_extra_includes_the_brep_extra
    SUBFAILED(extra='cadquery') tests/test_kernel_extras.py::KernelMetadataTest::test_each_extra_lists_what_its_module_needs
    SUBFAILED(extra='cadquery') tests/test_kernel_extras.py::KernelMetadataTest::test_every_kernel_extra_includes_the_brep_extra
    SUBFAILED(extra='manifold') tests/test_kernel_extras.py::KernelMetadataTest::test_the_former_engine_extras_are_gone
    SUBFAILED(extra='mesh') tests/test_kernel_extras.py::KernelMetadataTest::test_each_extra_lists_what_its_module_needs
    SUBFAILED(extra='molejo') tests/test_kernel_extras.py::KernelMetadataTest::test_each_extra_lists_what_its_module_needs
    SUBFAILED(extra='molejo') tests/test_kernel_extras.py::KernelMetadataTest::test_every_kernel_extra_includes_the_brep_extra
    SUBFAILED(extra='occt') tests/test_kernel_extras.py::KernelMetadataTest::test_the_former_engine_extras_are_gone
    SUBFAILED(extra='step') tests/test_kernel_extras.py::KernelMetadataTest::test_each_extra_lists_what_its_module_needs
    SUBFAILED(extra='step') tests/test_kernel_extras.py::KernelMetadataTest::test_every_kernel_extra_includes_the_brep_extra
    SUBFAILED(flag='--exact') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_flags_are_not_recognised
    SUBFAILED(flag='--faceted') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_flags_are_not_recognised
    SUBFAILED(module='machinome.engine.brep', missing='OCP') tests/test_kernel_extras.py::KernelRefusalTest::test_each_kernel_module_refuses_each_absent_kernel
    SUBFAILED(module='machinome.engine.mesh') tests/test_kernel_extras.py::KernelRefusalTest::test_a_broken_kernel_reports_its_own_failure
    SUBFAILED(module='machinome.engine.mesh', missing='manifold3d') tests/test_kernel_extras.py::KernelRefusalTest::test_each_kernel_module_refuses_each_absent_kernel
    SUBFAILED(name='machinome.brep_artifacts') tests/test_vet_universe.py::TheDeclarationTest::test_the_engine_package_is_judged_by_its_new_addresses
    SUBFAILED(name='machinome.brep_cache') tests/test_vet_universe.py::TheDeclarationTest::test_the_engine_package_is_judged_by_its_new_addresses
    SUBFAILED(name='machinome.engine.brep.read_brep') tests/test_vet_universe.py::TheDeclarationTest::test_the_engine_package_is_judged_by_its_new_addresses
    SUBFAILED(name='machinome.engine.brep.write_brep') tests/test_vet_universe.py::TheDeclarationTest::test_the_engine_package_is_judged_by_its_new_addresses
    SUBFAILED(name='machinome.engine.brep.write_stl') tests/test_vet_universe.py::TheDeclarationTest::test_the_engine_package_is_judged_by_its_new_addresses
    SUBFAILED(name='machinome.exact_artifacts') tests/test_engine_package.py::TheMemosAndPublicationTest::test_the_former_modules_are_not_found
    SUBFAILED(name='machinome.exact_cache') tests/test_engine_package.py::TheMemosAndPublicationTest::test_the_former_modules_are_not_found
    SUBFAILED(name='machinome.exact_engine') tests/test_engine_package.py::TheFormerAddressesTest::test_each_former_address_is_not_found
    SUBFAILED(name='machinome.manifold') tests/test_engine_package.py::TheFormerAddressesTest::test_each_former_address_is_not_found
    SUBFAILED(name='machinome.manifold.engine') tests/test_engine_package.py::TheFormerAddressesTest::test_each_former_address_is_not_found
    SUBFAILED(name='machinome.mesh_engine') tests/test_engine_package.py::TheFormerAddressesTest::test_each_former_address_is_not_found
    SUBFAILED(name='machinome.occt') tests/test_engine_package.py::TheFormerAddressesTest::test_each_former_address_is_not_found
    SUBFAILED(name='machinome.occt.engine') tests/test_engine_package.py::TheFormerAddressesTest::test_each_former_address_is_not_found
    SUBFAILED(value='brep', engine='brep') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_variable_is_refused_whatever_its_value_and_flag
    SUBFAILED(value='brep', engine='mesh') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_variable_is_refused_whatever_its_value_and_flag
    SUBFAILED(value='brep', engine=None) tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_variable_is_refused_whatever_its_value_and_flag
    SUBFAILED(value='exact') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_values_are_refused_naming_the_variable
    SUBFAILED(value='faceted') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_values_are_refused_naming_the_variable
    SUBFAILED(value='faceted', engine='brep') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_variable_is_refused_whatever_its_value_and_flag
    SUBFAILED(value='faceted', engine='mesh') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_variable_is_refused_whatever_its_value_and_flag
    SUBFAILED(value='faceted', engine=None) tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_variable_is_refused_whatever_its_value_and_flag
    SUBFAILED(value='mesh', engine='brep') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_variable_is_refused_whatever_its_value_and_flag
    SUBFAILED(value='mesh', engine='mesh') tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_variable_is_refused_whatever_its_value_and_flag
    SUBFAILED(value='mesh', engine=None) tests/test_manager_test.py::ComparisonEngineSelectionTest::test_the_former_variable_is_refused_whatever_its_value_and_flag
```

The reasons, verbatim, with their counts (from the same log):

```
      9 E   AssertionError: ModuleNotFoundError not raised
      8 E   AssertionError: Items in the first set but not the second:
      5 E   SystemExit: 2
      5 E   AssertionError: [] == []
      4 E   ModuleNotFoundError: No module named 'machinome.engine'
      4 E   AssertionError: ValueError not raised
      3 E   ValueError: unknown comparison kernel 'mesh'
      3 E   ValueError: unknown comparison kernel 'brep'
      3 E   ModuleNotFoundError: No module named 'machinome.node.brep_leaf'
      3 E   AssertionError: "unknown comparison kernel 'mesh'" != "SOLID_TEST_KERNEL is not read: the run's [105 chars]env)"
      3 E   AssertionError: "unknown comparison kernel 'brep'" != "SOLID_TEST_KERNEL is not read: the run's [105 chars]env)"
      2 E   TypeError: resolve_comparison_policy() got an unexpected keyword argument 'engine'
      2 E   AttributeError: 'ComparisonPolicy' object has no attribute 'engine'
      2 E   AssertionError: SystemExit not raised
      2 E   AssertionError: ComparisonPolicy(kernel='exact', volume_e[51 chars]True) != ('brep', 0.0, 1e-09, True)
      2 E   AssertionError: 2 != 3
      2 E   AssertionError: 'machinome[brep]' not found in ['cadquery==2.7.*', 'machinome[occt]']
      2 E   AssertionError: 'ModuleNotFoundError' != 'ExtraUnavailable'
      1 E   TypeError: tests.test_leaf_contract_version.declaring.<locals>.Declaring declares leaf contract 3; this machinome speaks leaf contract 2 (machinome.node.leaf.CONTRACT)
      1 E   ModuleNotFoundError: No module named 'machinome.brep_cache'
      1 E   KeyError: 'policy'
      1 E   KeyError: 'mesh'
      1 E   KeyError: 'brep'
      1 E   AttributeError: module 'machinome.test' has no attribute 'ENGINES'
      1 E   AttributeError: module 'machinome._verdict_store' has no attribute '_BREP'
      1 E   AttributeError: 'MeshBlock' object has no attribute 'brep'
      1 E   AttributeError: 'FusionNode' object has no attribute 'brep'
      1 E   AttributeError: 'CadQueryNode' object has no attribute 'brep'
      1 E   AssertionError: {'machinome/_verdict_store.py': (19, [(5, [89693 chars]')])} != {}
      1 E   AssertionError: the probed snippet exited 1
      1 E   AssertionError: TypeError not raised
      1 E   AssertionError: Tuples differ: ('mac[351 chars]nome.exact_cache', 'machinome.exact_artifacts'[102 chars]stl') != ('mac[351 chars]nome.brep_cache', 'machinome.brep_artifacts', [100 chars]stl')
      1 E   AssertionError: True is not false
      1 E   AssertionError: Traceback (most recent call last):
      1 E   AssertionError: Regex didn't match: '^mesh-fusion-v1:[0-9a-f]{64}$' not found in 'faceted-fusion-manifold-v1:e37990e7b3442ad00340aa1e1bf16610f3a878a3fca72c5e864307a2817f532e'
      1 E   AssertionError: Regex didn't match: 'Ran 0 tests in 1\\.00 seconds: 0 passed, 0 failed \\(mesh engine, volume epsilon 0\\.5 mm³\\)' not found in '\nRan 0 tests in 1.00 seconds: 0 passed, 0 failed\n'
      1 E   AssertionError: Lists differ: ['ModuleNotFoundError', None, "No module na[19 chars]ne'"] != ['ExtraUnavailable', 'mesh', 'the mesh engi[115 chars]"\'']
      1 E   AssertionError: Lists differ: ['ModuleNotFoundError', None, "No module na[19 chars]ne'"] != ['ExtraUnavailable', 'brep', 'the B-rep eng[109 chars]"\'']
      1 E   AssertionError: ComparisonPolicy(kernel='exact', volume_e[52 chars]alse) != ('mesh', 0.5, 1e-09, False)
      1 E   AssertionError: ComparisonPolicy(kernel='exact', volume_e[51 chars]True) != ('mesh', 0.25, 1e-09, True)
      1 E   AssertionError: 2 != 1 : usage: -c [-h]
      1 E   AssertionError: 0 == 0 :  INFO -    core.builder - START
      1 E   AssertionError: 0 != 1 : a record kept under the former path word was served
      1 E   RuntimeError: BrepPair exactness is unavailable before its children are linked by assemble()
      1 E   machinome.manifest.ProjectManifestError: No pyproject.toml with [tool.machinome] found above whatever.py
```

Two of them were the test's own fault and were corrected before any source
change, then run red again for the right reason:
`test_a_brep_fusion_is_brep_fusion_v1` read `geometry_recipe` on an
unassembled fusion (the `RuntimeError` above); with `assemble()` first:

```
E   AssertionError: 'exact-fusion-occt-v1' != 'brep-fusion-v1'
E   AssertionError: Regex didn't match: '^mesh-fusion-v1:[0-9a-f]{64}$' not found in 'faceted-fusion-manifold-v1:e37990e7b3442ad00340aa1e1bf16610f3a878a3fca72c5e864307a2817f532e'
E   AssertionError: True is not false
3 failed, 1 passed in 3.36s
```

(`True is not false`: a mesh fusion's STL recording the former recipe stays
current on the old tree, because the former recipe is the current one.)
The `ProjectManifestError` belongs to
`test_the_runner_sets_the_policy_it_resolved`, whose `Namespace(engine=...)`
the old runner does not read, so it resolves the default policy and reaches
the project lookup; green after group 5 without an edit.

Not red on the old tree, and stated: `PortionTest.test_a_portion_resolves`
passes on faf1c80, because `machinome`'s own path already admits a portion
`machinome/engine/` holding no `__init__.py` as a namespace package; the
test pins what the new package must keep. `test_a_current_brep_fusion_stays_current`
is a guard, green before and after.

## 3. Applying, group by group

### Group 3: the engine package and the providers

`machinome/engine/__init__.py` holds both seams (Decision 2's names,
`BREP_CONTRACT = 2`, `MESH_CONTRACT = 1`, R1 to R4), imports only
`functools`, `importlib`, `typing`, `machinome._namespace_portions` and
`machinome.extras`, and ends with `__path__ = _namespace_portions(__path__,
__name__)`. `git mv machinome/occt/engine.py machinome/engine/brep.py` and
`git mv machinome/manifold/engine.py machinome/engine/mesh.py`;
`require_extra('brep', ...)` and `require_extra('mesh', ...)`, the B-rep
provider's error types from `machinome.engine`, `CONTRACT = 2`, R26, R27.
`git rm machinome/occt/__init__.py machinome/manifold/__init__.py
machinome/exact_engine.py machinome/mesh_engine.py`; then

```
$ git clean -ndX machinome/occt machinome/manifold
Would remove machinome/manifold/
Would remove machinome/occt/
$ git clean -fdX machinome/occt machinome/manifold
Removing machinome/manifold/
Removing machinome/occt/
```

(each held only its `__pycache__`, from the baseline runs). Every importer
in the core repointed; the suite's importers repointed by one ordered regex
pass (scratch `repoint3.py`), the finder helpers' default targets
`('machinome.engine.brep',)` and `('manifold3d', 'machinome.engine.mesh')`.

Checkpoint, the group's own tests and their neighbours
(`test_engine_package`, `test_engine_doors`, both seam tests, both provider
tests, `test_core_kernel_free`, `test_kernel_extras`):
`23 failed, 78 passed, 115 subtests passed`, every failure one a later group
turns green: the memos' addresses (group 4), the stale B-rep fusion's and
the mesh run's messages (group 5), the extras (group 6).

### Group 4: the memos, the leaf base, the capability, contract 3

`git mv` of `exact_cache.py`, `exact_artifacts.py` and `node/exact_leaf.py`;
R25; `ExactLeafNode` to `BrepLeafNode`; the member `exact` to `brep` on the
node base, `InternalNode` (R24), `BrepLeafNode`, `MolejoNode`, read by
fusion, the leaf base, the builder and the test framework;
`FlexibleNode`'s private `_brep_*` and `_mesh_cache_snapshot`;
`IntersectionStats.brep` (done here rather than in group 5, since the
capability's readers in `test.py` read the field in the same lines); R21 to
R23; `leaf.CONTRACT = 3` with its comment; the suite's stand-ins declare
`brep` and the three contract-package stand-ins `leaf_contract = 3`.
`tests/test_leaf_contract_members.py` reads the change in progress's delta,
so its `DELTA` path moved from the archived `openscad-out` to `brep-mesh`;
it stayed red on the API reference's members until group 9.

### Group 5: the test framework, the store, fusion

`test.py` per Decision 6 and 13: `ENGINES`, `ComparisonPolicy.engine`,
`resolve_comparison_policy(engine=...)`, R30 checked before the engine is
read (`if environ.get('SOLID_TEST_KERNEL')`: an empty value is unset),
R7, R8, R10, R13 to R18, R31, the path words `'brep'`/`'mesh'`, the private
renames of Decision 6. `manager/test.py`: `--brep`/`--mesh` into
`dest='engine'`, R28's help, R9, R11, R12, `ComparisonPolicy('brep', 0.0)`.
`_verdict_store.py`: `_BREP` (bit 2), `record(..., brep)`, `FORMAT_VERSION`
1 unchanged. `fusion.py`: `brep-fusion-v1`, `mesh-fusion-v1:<sha256>`,
`_generate_mesh_stl`, R19, R20.

### Group 6: the extras and vet

`pyproject.toml` per Decision 10 (`brep`, `mesh`, the four node extras
including `machinome[brep]`, `all`, the comments), `requirements.txt`'s
comment, `setup.cfg`'s E402 ignores for `machinome/engine/brep.py` and
`machinome/engine/mesh.py`, `machinome/extras.py`'s docstring,
`machinome/vet/universe.toml`'s denylist. No reinstall: the metadata tests
read `pyproject.toml`, `requirements.txt` and `tox.ini` from the checkout,
and no test of the extras reads installed metadata.

### Group 7: the wording; the gate

Gate count after groups 3 to 6: `modules: 17  occurrences: 106`. Every
remaining offender reworded from the rename table and the refusal texts:
`core/processes.py` and `manager/import_step.py` without the library's name
("the B-rep engine's kernel", "the STEP reader"), `brep_cache.py`'s and
`brep_artifacts.py`'s "OCCT's" as "the kernel's", `test.py`'s "OCCT's own
precision" as "the B-rep engine's own precision", "trimesh's own manifold
backend" as "trimesh's own Boolean backend". Gate count after group 7:

```
modules: 0  occurrences: 0
```

pycodestyle over every changed core module, compared with the same module
on faf1c80 (E402 ignored as `setup.cfg` does): no new finding.

### 7.2 The residual review

After the gate is green, every remaining word `exact` in `machinome/`
(case-insensitive, `exactly` excluded): **123 occurrences on 115 lines**,
91 of them in text (strings, docstrings, comments) and 32 in the ordinary
identifiers the gate admits by module (`simulation/profile.py`,
`node/frames.py`, `motion/joints.py`, `simulation/trajectory.py`). `exactness`:
none left. On faf1c80 the text held 312, 196 the gate's; the 116 others were
read one by one in groups 4 and 7 and the split's predicates the gate does
not see were rewritten there ("this leaf is exact" in `node/step.py`, "adapter
is exact" in `node/molejo.py`, "a fusion ... is itself exact", "routed
exact", "rigid and exact", "a pair of exact solids", the `_place_solid`
docstring's field names, among others). Every one left is the ordinary
adjective: exact IEEE-754 values and matrix bytes, the exact-bytes key
(ADR-070), the exact-negative shortcut (ADR-090), exact rational arithmetic
and landings in the simulation, exact source lines, the snapped exact 0, 1,
-1, an exact copy, an exact stamp, set, path, length or inverse. None is the
split's.

| module:line | text | reading |
|---|---|---|
| `machinome/_verdict_store.py:27` | The store holds raw engine verdicts -- emptiness, the volume's exact | ordinary |
| `machinome/model.py:537` | """Copy the exact pinned artifact bytes; return their byte SHA-256.""" | ordinary |
| `machinome/math.py:421` | A sum of clamped ramps, so it has no branch and is exact at every | ordinary |
| `machinome/math.py:460` | that exact curve writes the `sin` out; this one is a pulse, and | ordinary |
| `machinome/math.py:461` | exact rational arithmetic every runtime agrees on with no | ordinary |
| `machinome/currency.py:24` | exact set `mtime_ns` is the maximum of -- as a sorted sequence of | ordinary |
| `machinome/currency.py:523` | exact stamp -- the coarse-resolution case build-pipeline already | ordinary |
| `machinome/brep_cache.py:54` | # One placed shape per (shape cache key, exact matrix bytes), and one | ordinary |
| `machinome/brep_cache.py:201` | Cached per ``(shape cache key, exact matrix bytes)``, so a solid placed by | ordinary |
| `machinome/brep_cache.py:203` | compared by the exact IEEE-754 values sent to the kernel: a placement | ordinary |
| `machinome/core/builder.py:535` | filter continues to admit only that exact foreign path.""" | ordinary |
| `machinome/simulation/profile.py:60` | """Exact finite builtin operands only; never convert author objects.""" | ordinary |
| `machinome/simulation/profile.py:170` | exact = tuple((Fraction.from_float(x), Fraction.from_float(y)) | ordinary |
| `machinome/simulation/profile.py:172` | size = len(exact) | ordinary |
| `machinome/simulation/profile.py:174` | for a, b in zip(exact, exact[1:] + exact[:1])) | ordinary |
| `machinome/simulation/profile.py:178` | a, b, c = exact[index - 1], exact[index], exact[(index + 1) % size] | ordinary |
| `machinome/simulation/profile.py:191` | if _segments_meet(exact[left], exact[(left + 1) % size], | ordinary |
| `machinome/simulation/profile.py:192` | exact[right], exact[(right + 1) % size]): | ordinary |
| `machinome/simulation/profile.py:238` | """Flat exact point table; loops remain separate index runs.""" | ordinary |
| `machinome/simulation/run.py:747` | about six pairs of floats in a hundred, so an exact landing | ordinary |
| `machinome/simulation/run.py:1219` | # gives exact prefix coordinates after the bound is snapped. | ordinary |
| `machinome/simulation/run.py:1301` | # Linear in `t`: one division, exact, no extra | ordinary |
| `machinome/simulation/run.py:1338` | the piece that brackets the bound. Exact.""" | ordinary |
| `machinome/simulation/trajectory.py:110` | def _sources(motions, left, right, exact_lines=False, | ordinary |
| `machinome/simulation/trajectory.py:118` | # whose cache holds the exact `to` target. Interior fractions use | ordinary |
| `machinome/simulation/trajectory.py:128` | if exact_lines and left == 0.0 and right == 1.0 | ordinary |
| `machinome/simulation/trajectory.py:138` | """Freeze affine evaluations into a cheap exact segment.""" | ordinary |
| `machinome/simulation/trajectory.py:147` | closed=False, exact_source_lines=False, | ordinary |
| `machinome/simulation/trajectory.py:168` | exact_lines=exact_source_lines, | ordinary |
| `machinome/simulation/trajectory.py:375` | f'one certified exact linear path in this stretch.') | ordinary |
| `machinome/simulation/trajectory.py:392` | None, tick, exact_source_lines=True) | ordinary |
| `machinome/simulation/trajectory.py:394` | None, tick, exact_source_lines=True) | ordinary |
| `machinome/simulation/trajectory.py:555` | # Exact endpoint propagation needs no extra evaluations or | ordinary |
| `machinome/simulation/trajectory.py:570` | exact_source_lines=bool(edge.plans) and | ordinary |
| `machinome/simulation/trajectory.py:577` | # but evaluated the authored exact source at its terminal | ordinary |
| `machinome/simulation/trajectory.py:586` | exact_end = {name: source.end | ordinary |
| `machinome/simulation/trajectory.py:588` | authored_exact = p._evaluated_law( | ordinary |
| `machinome/simulation/trajectory.py:589` | edge, edge.driven[index], edge.graphs[index], exact_end) | ordinary |
| `machinome/simulation/trajectory.py:590` | if (authored_exact == 0.0 and | ordinary |
| `machinome/simulation/trajectory.py:592` | struct.pack('!d', authored_exact)): | ordinary |
| `machinome/simulation/trajectory.py:593` | terminal = authored_exact | ordinary |
| `machinome/simulation/trajectory.py:606` | # A curved law can have an exact authored end even though | ordinary |
| `machinome/simulation/trajectory.py:639` | # case only the relation's exact terminal change is added; | ordinary |
| `machinome/simulation/driver.py:24` | "the same scenario twice" decidable by exact comparison rather than by | ordinary |
| `machinome/simulation/clocked.py:31` | `floor(-crank / 360)`, which is exact and needs no keyword. | ordinary |
| `machinome/simulation/clocked.py:750` | exact and the correction is a single IEEE addition -- so the | ordinary |
| `machinome/simulation/clocked.py:1094` | # so the rearrangement is exact. | ordinary |
| `machinome/simulation/sim.py:476` | """The exact instant this simulation stands at, in seconds. | ordinary |
| `machinome/test.py:493` | A rigid verdict identity is the exact observation that supplied its | ordinary |
| `machinome/test.py:523` | superset of the part's true world footprint -- exact for an | ordinary |
| `machinome/test.py:537` | overlap on some axis -- disjoint boxes make the exact intersection | ordinary |
| `machinome/test.py:582` | # this margin, two solids in exact flush contact -- non-empty at 0.0mm^3, | ordinary |
| `machinome/test.py:666` | not exact where a world box's one product is; the world candidate | ordinary |
| `machinome/test.py:937` | # A second exact-negative tier for a pair of B-REP solids, run after the | ordinary |
| `machinome/test.py:1527` | """Add one coefficient in the dense formulation's exact order.""" | ordinary |
| `machinome/test.py:1699` | A quantum of `0` restores the exact-bytes key ADR-070 specified, keying | ordinary |
| `machinome/test.py:1926` | boxes are disjoint, the exact intersection is provably empty | ordinary |
| `machinome/test.py:1927` | and the boolean is skipped entirely (an exact-negative | ordinary |
| `machinome/test.py:2147` | `volume_epsilon` (mm^3, default 0.0 keeps exact `is_empty` | ordinary |
| `machinome/test.py:2182` | `volume_epsilon` (mm^3, default 0.0 keeps exact `is_empty` | ordinary |
| `machinome/test.py:2555` | share volume, and it is the exact inverse of the adjacency | ordinary |
| `machinome/test.py:2622` | `volume_epsilon` (mm^3, default 0.0 keeps exact `is_empty` | ordinary |
| `machinome/simulation/contact_proof.py:6` | Finite binary constants are exact rationals here. A result certifies one affine | ordinary |
| `machinome/simulation/contact_proof.py:8` | its exact split, while unsupported operations cannot furnish a certificate. | ordinary |
| `machinome/simulation/contact_proof.py:18` | """Return exact (constant, slope), or None when not proved affine.""" | ordinary |
| `machinome/simulation/contact_proof.py:98` | # Split only at an exact selection crossing proved above. This is | ordinary |
| `machinome/core/pieces.py:98` | Binary STL is recognised by its exact length (80-byte header, count, | ordinary |
| `machinome/simulation/program.py:10` | from where the coordinate stood -- which is exact across the kinks of | ordinary |
| `machinome/simulation/program.py:12` | because it is the difference of two exact evaluations. Nothing about the | ordinary |
| `machinome/simulation/program.py:621` | # is what keeps the answer exact when a crossing | ordinary |
| `machinome/simulation/program.py:887` | """Exact finite input identity, or no proof that standing nodes agree.""" | ordinary |
| `machinome/simulation/program.py:1152` | UNRELATED later dict the exact same address: keying a piece by | ordinary |
| `machinome/simulation/program.py:1402` | zero and the coordinate keeps the exact float it | ordinary |
| `machinome/simulation/program.py:1778` | # stationary-threshold landings retain their exact existing floats. | ordinary |
| `machinome/simulation/program.py:1981` | """Prove an exact finite builtin-numeric substitution without coercing | ordinary |
| `machinome/simulation/program.py:2543` | A law with no jump in it is the difference of two exact | ordinary |
| `machinome/simulation/program.py:2544` | evaluations, which is what makes a kink exact -- and that is the | ordinary |
| `machinome/simulation/program.py:2564` | # A preceding play edge reports its exact absolute landing. | ordinary |
| `machinome/simulation/program.py:2628` | one-division fast path exact. | ordinary |
| `machinome/simulation/program.py:2686` | is the formula rearranged for that term -- exact, because a | ordinary |
| `machinome/simulation/program.py:3096` | is exact and an affine chain publishes `-36.0` rather than a | ordinary |
| `machinome/simulation/program.py:3593` | # power of two, so the division by it is exact and a composed affine | ordinary |
| `machinome/simulation/program.py:3594` | # chain publishes the exact product rather than a rounded neighbour. | ordinary |
| `machinome/node/frames.py:68` | # -- normalizing `(0, 0, 2)` must give the exact `(0, 0, 1)` a reader | ordinary |
| `machinome/node/frames.py:89` | for exact in (0, 1, -1): | ordinary |
| `machinome/node/frames.py:90` | if abs(value - exact) <= _SNAP: | ordinary |
| `machinome/node/frames.py:91` | return exact | ordinary |
| `machinome/node/flexible.py:362` | the full structural identity, the exact bound values and the digest | ordinary |
| `machinome/node/flexible.py:462` | caller reading an exact answer deserves to know how exact. | ordinary |
| `machinome/node/step.py:113` | exact but meshes first -- 10.78 s on the worst product of a 35 MB | ordinary |
| `machinome/node/step.py:639` | # exact decomposition into the framework's own rotate-then-translate | ordinary |
| `machinome/node/step.py:820` | occurrence walked through nested sub-assemblies, and the exact | ordinary |
| `machinome/node/build123d.py:125` | the exact profile available to a future offsetting exporter. | ordinary |
| `machinome/node/sources.py:72` | exact path to watch) breaks that rendering: `OSError.__str__` switches | ordinary |
| `machinome/node/sources.py:174` | # _on_reload_exception) the exact foreign path this refusal names. | ordinary |
| `machinome/node/sources.py:261` | # The stamp is the exact set of module names rather than | ordinary |
| `machinome/node/declarative.py:1416` | its arguments against this exact instance, and a site's callable | ordinary |
| `machinome/node/base.py:446` | # Ordinary Python producers retain their exact historical bytes. External | ordinary |
| `machinome/node/base.py:1350` | """Exact artifact equality guarded by every source's metadata. | ordinary |
| `machinome/node/base.py:1405` | filesystem cannot store the exact stamp, the artifact is still | ordinary |
| `machinome/motion/ports.py:529` | # exact class's dictionary so a subclass never inherits a base map. | ordinary |
| `machinome/motion/mates.py:1204` | # Preserve exact equal-component serialization, rather | ordinary |
| `machinome/motion/joints.py:130` | # How close to an exact 0, 1 or -1 a normalized axis component has to be | ordinary |
| `machinome/motion/joints.py:258` | """`value`, or the exact 0, 1 or -1 it is within `_SNAP` of.""" | ordinary |
| `machinome/motion/joints.py:259` | for exact in (0, 1, -1): | ordinary |
| `machinome/motion/joints.py:260` | if abs(value - exact) <= _SNAP: | ordinary |
| `machinome/motion/joints.py:261` | return exact | ordinary |
| `machinome/motion/joints.py:502` | number, the axis normalized and SNAPPED to an exact `0`, `1` or | ordinary |
| `machinome/motion/couplings.py:1494` | an expression tree: that is what makes the backward solve exact and | ordinary |
| `machinome/engine/mesh.py:82` | 4x4 `matrix`, sent as their exact values. Nothing is re-meshed or | ordinary |
| `machinome/engine/brep.py:166` | """A private exact copy, geometry included, triangulation not.""" | ordinary |
| `machinome/engine/brep.py:177` | The upper three rows are sent to OCCT as the exact IEEE-754 values the | ordinary |
| `machinome/engine/brep.py:198` | # the default kernel private exact copies of both reusable operands. | ordinary |
| `machinome/manager/test.py:85` | 'engines; 0 restores the exact-bytes key.') | ordinary |
| `machinome/manager/test.py:497` | """Snapshot each child's exact operations list. The snapshots | ordinary |

### Group 8: the tests

`git mv`, history kept, per Decision 12: `test_exact_common_guard` →
`test_brep_common_guard`, `test_exact_currency` → `test_brep_currency`,
`test_exact_engine_dependency` → `test_brep_engine_dependency`,
`test_exact_engine_seam` → `test_brep_engine_seam`, `test_exact_geometry` →
`test_brep_geometry`, `test_exact_input_copies` → `test_brep_input_copies`,
`test_exact_placement_cache` → `test_brep_placement_cache`,
`test_exact_test_isolation` → `test_brep_test_isolation`,
`test_front_end_free_exact` → `test_front_end_free_brep`,
`test_leaf_contract_exact` → `test_leaf_contract_brep`,
`test_leaf_contract_faceted` → `test_leaf_contract_mesh`,
`test_manifold_cache` → `test_mesh_cache`, `test_manifold_engine` →
`test_mesh_engine`, `test_occt_engine` → `test_brep_engine`,
`test_resolved_exact_witness` → `test_resolved_brep_witness`,
`exact_engine_absent` → `brep_engine_absent` (its variables
`EXACT_ENGINE_ABSENT*` → `BREP_ENGINE_ABSENT*`, `_NAMES`, `_BROKEN_NAMES` and
`_LOG` alike), `exact_engine_golden` → `brep_engine_golden`,
`exact_test_support` → `brep_test_support`, and
`tests/data/exact_engine_golden.json` → `tests/data/brep_engine_golden.json`
(bytes unchanged, a pure rename). The fixture projects keep their file
names (`tests/meta_project/`, `tests/contract_package/`,
`tests/vet_projects/exact_engine_internals/`) and their golden keys
(`exact_leaf_with_marking`, `exact_fusion_shaft_in_bore`,
`test_exact_assembly_is_supported`, ...); their content is repointed.
Test method names that say `exact`/`faceted` in their own prose are left as
they are (the suite is not gated); the comparison-policy class and its
methods were renamed with the tests of 2.6.

**Every changed assertion target, and why:**

| file | target before → after | reason |
|---|---|---|
| `test_kernel_extras.py` | extras `occt`/`manifold` → `brep`/`mesh`; `machinome[occt]` → `machinome[brep]` in the four node extras; `all`'s set; the two providers' refusals (R5, R6) and addresses; the broken-kernel module `machinome.engine.mesh` | Decision 10, R5, R6 |
| `test_leaf_capability_set.py`, `test_leaf_contract_version.py` | `CONTRACT` 2 → 3; the refused declaration 1 → 2 (and 1, 2, `'3'`, `True` refused); the admitted declaration 2 → 3; the patched future version 3 → 4; `exact` → `brep` in the declared set and on the leaf | Decision 4, ADR-165 |
| `test_manager_test.py` | flags `--exact`/`--faceted` → `--brep`/`--mesh`; `args.kernel` → `args.engine`; `Namespace(kernel=...)` → `Namespace(engine=...)`; policy values `'exact'`/`'faceted'` → `'brep'`/`'mesh'`; `SOLID_TEST_KERNEL` → `SOLID_TEST_ENGINE` and the refusal regex `SOLID_TEST_ENGINE.*'brep'.*'mesh'.*fast`; the summary note `(faceted kernel, ...)` → `(mesh engine, ...)` and `'faceted kernel'` → `'mesh engine'` in the run's line | Decision 6, R7, R11, R12 |
| `test_brep_engine_seam.py` | `CONTRACT` → `BREP_CONTRACT`, `PROVIDER` → `BREP_PROVIDER`; the stub declaring "another version" 2 → 1 (2 is now the contract); the extra `occt` → `brep`; R1's text; the saved provider attribute `machinome.engine.brep` (was `machinome.occt.engine`) | Decisions 2, 3, R1 |
| `test_mesh_engine_seam.py` | `CONTRACT` → `MESH_CONTRACT`, `PROVIDER` → `MESH_PROVIDER`; R3's text (`machinome[mesh]`, "B-rep geometry ... the B-rep engine"); the caller's word `faceted fusion` → `mesh fusion`; "the package exports no operation" now reads `machinome.engine` (the package; `machinome.engine.mesh` is the provider, which defines them); the extra `manifold` → `mesh` | Decision 2, R3 |
| `test_brep_engine.py`, `test_mesh_engine.py` | the source path of the provider; "the package exports no operation" reads `machinome.engine`; the B-rep provider's `CONTRACT` literal 1 → 2 | Decision 3 |
| `test_core_kernel_free.py` | the providers are two modules, not packages; the one module naming each provider is `machinome/engine/__init__.py` (was `exact_engine.py`, `mesh_engine.py`); `EXTRA_OF` `occt`/`manifold` → `brep`/`mesh`; its own `KERNELS` (library names) kept | Decisions 2, 10 |
| `test_brep_engine_dependency.py` | the stale fusion's install line `machinome[brep]` and "B-rep engine" | R1 |
| `test_mesh_engine_dependency.py` | `INSTALL` `machinome[mesh]`; the start refusal (R9 + R3); "Comparing on the mesh engine" absent; `mesh fusion Fused`; `SOLID_TEST_ENGINE=mesh` | R3, R9, R11, R19 |
| `test_meta.py` | the run line and notes (`mesh engine`), `--mesh`/`--brep`, `SOLID_TEST_ENGINE` (and its refusal of `fast`) | R7, R11, R12 |
| `test_verdict_store.py` | `set_policy(engine='brep')`; the verdict helpers `_brep_verdict`/`_mesh_verdict`; path words and dictionary keys `'brep'`/`'mesh'`; the provider `machinome.engine.brep`/`.mesh`; plus the four new `ThePathWords` cases | Decision 7 |
| `test_flexible_verdict_identity.py`, `test_assembly_integrity.py`, `test_markings.py`, `test_intersection_memo.py`, `test_brep_geometry.py`, `test_tessellation_precision.py`, `test_face_box_culling.py`, `test_persistent_piece_facts.py`, `test_flexible_cache_performance.py`, `test_brep_placement_cache.py`, `test_brep_common_guard.py`, `test_lazy_test_framework.py`, `test_molejo_adapter.py` | policy values, path words, the run's argument `engine`, `node.brep`/`stats.brep`, the private `_brep_*`/`_mesh_*` names, `MeshShapeNode(..., brep=False)` | Decisions 4, 6, 7 |
| `test_backend_neutral_materialization.py` | `BrepLeafNode`; the new `RecipeIdentityTest` | Decision 8 |
| `test_vet_universe.py` | the denylist's five addresses; the new judgement cases | Decision 15 item 10 |
| `test_leaf_contract_members.py` | `DELTA` reads `openspec/changes/brep-mesh/` (was the archived `openscad-out`); `BrepLeafNode` | the test reads the change in progress |
| `test_docs_structure.py` | `EXTRAS` `brep`/`mesh`; the former names refused on every reader page but the changelog and the upgrading page (task 9.1, red first) | Decision 14 |
| `test_tutorial_counter.py`, `mesh_engine_golden.py` | clear `SOLID_TEST_ENGINE` | Decision 12 |
| every other file of the list in 1.1 | imports and addresses only | the rename table |

`tests/mesh_engine_golden.py` (8.3): its runs are `--mesh` and `--brep` and
kept under those keys; `--check` reads the record's run keys `faceted` and
`exact` as `mesh` and `brep` and its values through `BREP_MESH_EXPECTED`
(the path words, `faceted kernel, volume epsilon` → `mesh engine, volume
epsilon`, `faceted fusion` → `mesh fusion`), counting those values as
renamed; the summary line gains `, N renamed (brep-mesh)`. No JSON
re-recorded.

**A golden difference, explained and removed.** The first `--check` of
`leaf_contract_golden` after group 8 reported

```
DIFFERS: exact_leaf_with_marking.artifacts..brep.digest golden='f5793c6b461752fe471b8edb411d4682c3e4e5b84135e006beb22e46f07bbcaf' now='9752036375b6e05340239810595dacb6c8893533656593c607e4049caf9c9d01'
DIFFERS: exact_leaf_with_marking.artifacts..marking-digits.stl.digest golden='879a2091d9b5f30c04de382a80a9c0090c2477db699b03e0eb28fb12c8472b09' now='3497bdc451661b3f1b754b0c827cba0ca0ba7c2cedb42262275181755bde5f16'
DIFFERS: exact_leaf_with_marking.artifacts..stl.digest golden='f5793c6b461752fe471b8edb411d4682c3e4e5b84135e006beb22e46f07bbcaf' now='9752036375b6e05340239810595dacb6c8893533656593c607e4049caf9c9d01'
golden comparison: 7 fixtures, 77 values, 3 differences
```

The three values are the source digests recorded beside the fixture's
artifacts, not artifact bytes: the group 4 rename had edited a comment of
the fixture `tests/markings_project/dial.py` (`ExactLeafNode`'s 0.1 →
`BrepLeafNode`'s 0.1), and the fixture's own source is digested. A fixture
is data (Decision 12), so the comment was restored to its faf1c80 bytes
(`git checkout -- tests/markings_project/dial.py`), and the golden holds.
No golden was re-recorded.

The five goldens after the change, each in a fresh process:

```
leaf_contract_golden       golden comparison: 7 fixtures, 77 values, 0 differences
scad_presentation_golden   golden comparison: 34 values, 0 differences, 9 presentation files absent as expected
expression_type_golden     golden comparison: 17 values, 0 differences
brep_engine_golden         golden comparison: 7 fixtures, 0 differences
mesh_engine_golden         golden comparison: 1095 values, 0 differences, 2 expected (design.md Decision 4), 200 renamed (brep-mesh)
```

The touched suites after groups 3 to 9 (the 87 modules of 1.3 under their
new names, and the new and changed ones): `10 failed, 2036 passed` on the
first run, every failure in `test_verdict_store.py` and one cause: the
mechanical `.exact` → `.brep` rewrite had turned `exact_pair`'s two calls of
the test's own helper `self.exact(name, path)` into calls of its other
helper `self.brep(name, size)`. Restored; the module then `46 passed, 11
subtests passed`.

## 4. Docs (group 9)

Read `skills/write-the-manual/SKILL.md` first. Red first, the structure test
extended (`KernelExtrasTest`: the extras `brep` and `mesh` on the install
page; the former names refused on every reader page and the README but the
changelog and the upgrading page, which name them on purpose):

```
19 failed, 9 passed, 673 subtests passed in 0.25s
```

Pages rewritten: `docs/architecture.md` (the engine package, both seams and
providers, `BrepLeafNode`, `brep`, the run's engine and `SOLID_TEST_ENGINE`,
the source map), `start/install.rst`, `howto/fast-tests.rst` (the anchor
`comparison-kernel` is `comparison-engine`, its one reference in
`reference/cli.rst` repointed), `howto/backends.rst`, `howto/fusion.rst`,
`howto/imported-parts.rst`, `howto/flexible-parts.rst`, `howto/markings.rst`,
`howto/sheet-parts.rst`, `reference/cli.rst`, `reference/api.rst` (a section
"The two engines" for the seams), `reference/assertions.rst`,
`concepts/node-tree.rst`, `concepts/publishing.rst`, `start/first-machine.rst`,
`tutorial/01-part.rst`, `06-fit.rst`, `09-clocked.rst`, `why.rst`,
`project/status.rst`, `README.rst`, and `project/upgrading.rst` (a section
"Use the engines' new names (unreleased)": the flags, `SOLID_TEST_ENGINE` and
the refusal of `SOLID_TEST_KERNEL`, `.env` files, the extras, the moved names,
leaf contract 3, the verdict recompute, the mesh fusion rebuild, the
`__pycache__` cleaning). Two sentences that described mesh fusion as routed
"through OpenSCAD and CGAL" (`howto/fusion.rst`, `howto/imported-parts.rst`,
and "routes through OpenSCAD" in `howto/backends.rst`), stale since
`mesh-engine`, were rewritten with the words as the mesh engine's union.
The changelog's Unreleased section gains this cycle's bullet, and its
earlier Unreleased bullets name what 0.8 ships (Open Question 5): the
OpenSCAD family's (`brep` in the declared set, contract 3), the mesh
engine's, the SCAD presentation's, the extras', the leaf bases' and the
B-rep engine's. `docs/adrs/` unchanged (9.3).

**The task 9.1 grep**, outside the ADRs, `docs/releases/`,
`docs/performance-improvement.md`, the changelog and the upgrading page (the
orchestrator's note: both name the former names on purpose, as
`openscad-out` excluded them):

```
docs/architecture.md:564:`mesh_engine()` / `require_mesh_engine()` and `MESH_CONTRACT`, sits beside it
docs/reference/api.rst:514:.. py:function:: machinome.engine.mesh_engine()
docs/reference/api.rst:519:.. py:function:: machinome.engine.require_mesh_engine(needed_by, reason)
```

The three hits are the pattern `mesh_engine\b` meeting the mesh seam's own
functions, whose names Decision 2 keeps (`machinome.engine.mesh_engine()`,
`require_mesh_engine()`). With the former module spelled as such,
`machinome\.mesh_engine\b`, the grep finds nothing.

Docs build, strict, into scratch (`python -m sphinx -b html -n -W
--keep-going -E docs <scratch>`): exit 1 on five warnings, the same five
the same build of faf1c80's `docs/` and `machinome/` gives (two
`AssemblyNode` references and a `name keyword` in `api.rst`, two
`Sim` docstrings), no new one. The docs tests (`test_docs_structure`,
`test_release_records`, `test_docs_exports`, `test_leaf_contract_members`,
`test_tutorial_counter`, `test_frame_precision_docs`,
`test_mate_contract_docs`): `47 passed, 4 warnings, 916 subtests passed in
60.36s`.

`workflow/ongoing/magic-strings.md` (the orchestrator's note): lines 177 and
193 spell `SOLID_TEST_ENGINE` and its values `'brep'`, `'mesh'` (with the
current `test.py` lines, 125 and 202), and the sentence between them names
the flags `--mesh` and `--brep`.

## 5. The whole suite, the goldens, the gate (10.1)

The whole suite, once, alone (`python -m pytest -q tests`), 12 min 6 s of
wall time:

```
4568 passed, 4 skipped, 55 warnings, 6338 subtests passed in 722.57s (0:12:02)
```

The line's suite at f51b4de was 4513 passed, 4 skipped; the 55 more are this
cycle's new tests: the gate's 11, the engine package's 10, the doors' 5,
the run's engine's 14, the path words' 4, the recipe identities' 4, the
leaf base's 5, the vet judgement's 1 and the extras' former-names case's 1. The four skips are the line's
own: the browser photograph unless `MACHINOME_WEB_SNAPSHOT_E2E=1`, the
`jscad` CLI not installed, two vendor STEP files not present.

The five goldens again, each in a fresh process:

```
leaf_contract_golden       golden comparison: 7 fixtures, 77 values, 0 differences                                (5.1 s)
scad_presentation_golden   golden comparison: 34 values, 0 differences, 9 presentation files absent as expected    (3.9 s)
expression_type_golden     golden comparison: 17 values, 0 differences                                           (1.6 s)
brep_engine_golden         golden comparison: 7 fixtures, 0 differences                                          (4.9 s)
mesh_engine_golden         golden comparison: 1095 values, 0 differences, 2 expected (design.md Decision 4), 200 renamed (brep-mesh)   (133.3 s)
```

The gate, `python3 openspec/changes/brep-mesh/gate-prototype.py .`:

```
modules: 0  occurrences: 0
```

Gate counts at every measurement: 548 in 30 modules on faf1c80; 106 in 17
after groups 3 to 6; 0 after group 7, and 0 at this checkpoint.

## 6. The campaign plan (10.2)

`workflow/ongoing/lean-core.md`, "The next phase", item 2: marked in
progress with this file as its evidence, and the follow-ups the campaign owes
outside the framework: the studio's `machinome_test` tool and its test, its
`machinome-api` and `machinome` skills (`--faceted`, `--exact`,
`SOLID_TEST_KERNEL`), the workspace's `skills/simulate-project/SKILL.md`,
`scripts/load-projects.d/brep-mesh.toml` from this change's
`moved-names.toml`, checkouts' `.env` files, machinome-freecad's retarget.

## 8. Empirical validation (group 11, the orchestrator's legs)

Measured by the orchestrator on the bench at dfc9681 plus this cycle's
uncommitted implementation, against baselines taken on the line at faf1c80
(code f51b4de), with a recorder logging each memoized verdict's path word,
emptiness, `volume.hex()` and the representation flag (`stats.brep` after,
`stats.exact` before), compared ignoring the path word. Every leg green.

**11.1 `Locks/Pin_tumbler_lock`** (`lean-core-validation` e461fba).
`machinome test --mesh --no-verdict-store`: 24 passed, 0 failed, the summary
line ending `(mesh engine, volume epsilon 0 mm³, verdict store off)`; 2573
verdicts, answers identical to the baseline, path words `faceted` → `mesh`.
The former selectors:

```
$ machinome test --faceted ...
machinome: error: unrecognized arguments: --faceted          (exit 2)
$ SOLID_TEST_KERNEL=faceted machinome test ...
Error: SOLID_TEST_KERNEL is not read: the run's engine is set by SOLID_TEST_ENGINE, 'brep' or 'mesh'; rename the variable where it is set (a checkout's .env)          (exit 1)
```

With the verdict store on, two runs: 24 passed each, 29.6 s and then 25.0 s
(the store-off run with its build, 52.7 s).

**11.2 `3D-Printers/Prusa3-vanilla`** (master 5138091).
`machinome test --no-verdict-store`: 16 passed, 3 failed, the pre-existing
three; 15935 verdicts, answers identical, path words `exact`, `faceted` →
`brep`, `mesh`.

**11.3 OpenAstroMount** (`exact-engine-validation`). The real project does not
load against this change, as design.md predicts:
`ModuleNotFoundError: No module named 'machinome.occt'` from
`simulation/seats.py:15`. The legs ran on a scratch copy whose own code was
changed as the root cleanup's rewrite will change it (the import
`machinome.occt.engine` → `machinome.engine.brep`; `comparison_policy().kernel`
→ `.engine`; its comparisons to `'exact'` → `'brep'`).
`machinome test --brep --no-verdict-store`: 8 passed, 1 failed (the known
B-rep common wart, as before); 1302 verdicts, answers identical to the
`--exact` baseline, path word `exact` → `brep`. With `manifold3d` and
`machinome.engine.mesh` unfindable (`tests/mesh_engine_absent.py`'s finder):
8 passed, 1 failed, the same; the finder's log shows one asker of
`manifold3d`, trimesh's own import-time probe (`trimesh.boolean`,
`trimesh.util`), and `imported: []`: the mesh engine was never resolved.
`machinome build` twice in one build directory: 180 artifacts (90 STL, 90
BREP), hashes identical after the second build, which generated nothing
(0 "generated with" lines).

**11.4 A fusion leg.** Leonardo `cam_hammer`: `machinome build cam_hammer`,
14 artifacts, hashes identical to the mesh-engine cycle's (`ptl7-leo-after.txt`,
code d4eb5c0); no `.sources` record there carries a recipe (a B-rep fusion),
consistent with Decision 8: no B-rep fusion rebuilds. The mesh fusion's
rebuild under the renamed recipe, byte-identical, is pinned by the suite's
own `RecipeIdentityTest.test_a_mesh_fusion_under_the_former_recipe_rebuilds_the_same`
and by `mesh_engine_golden`'s `fusion_stl_sha256`.

**11.5 The goldens**, each in a fresh process on the bench:

```
expression_type      17 values, 0 differences
leaf_contract        7 fixtures, 77 values, 0 differences
markings             18 values, 0 differences
mesh_engine          1095 values, 0 differences, 2 expected (design.md Decision 4), 200 renamed (brep-mesh)
scad_presentation    34 values, 0 differences, 9 presentation files absent as expected
```

The three doors and the portion are the suite's
(`tests/test_engine_doors.py`, `tests/test_engine_package.py`), green in 10.1.

**11.6 The universe.** `scripts/load-projects` with the eight earlier tables
plus this change's `moved-names.toml`, timeout 300:

```
62 repositories, 129 rows: 116 ok, 5 expected, 2 unexpected, 0 timeout, 6 no-model; 2 skipped
```

One new expected row against the `mesh-engine` and `openscad-out` sweeps:
OpenAstroMount, explained by this change's row `machinome.occt` →
`machinome.engine.brep`; the other four expected and the two unexpected are
the earlier cycles'. The sweep's JSON is archived with this change,
`load-projects.json`.

**11.7 The greps over `projects/`.** The workspace's new rewrite tool's
catalogue-wide dry run (5 October 2026) finds 56 of 62 repositories to
change for the root cleanup, 910 files, among them this change's names:
`--faceted`/`--exact` command lines in READMEs, docs and tools;
`comparison_policy().kernel` compared to `'exact'`/`'faceted'` in
OpenAstroMount, the Internal-Cycloidal-Actuator and two clocks (a comparison
to a former value would silently never be true, so the rewrite covers the
member and the values); no project declares the `occt` or `manifold` extras;
no tracked `.env` sets `SOLID_TEST_KERNEL` (untracked `.env` files are
rewritten by the pass). The projects' rewrite is the root cleanup's, as
designed. Confirmed, and not this cycle's edits: machinome-studio's
`machinome_test` tool and its two skills, and the workspace's
`skills/simulate-project/SKILL.md`, spell the former flags.

## 9. Records, specs, archive (group 12)

**12.1 ADR-180** (`docs/adrs/NODE/ADR-180-the-engines-are-named-for-the-representation-each-consumes.md`),
linking this archive. The status lines of ADR-073, 160, 161, 162, 163, 165,
167, 176 and 178 say what ADR-180 amended in each; `docs/adrs/README.md`
indexes ADR-180 under NODE, marks the nine "amended by 180", and the OCCT
heading names the module the B-rep engine leaves the core with,
`machinome/engine/brep.py`. ADR-160 stays in `docs/adrs/OCCT/` (Open
Question 6). `docs/architecture.md` was synthesized in group 9.

**12.2** `openspec validate brep-mesh --strict`: `Change 'brep-mesh' is
valid`. `openspec archive brep-mesh --yes`:

```
Totals: + 33, ~ 70, - 0, → 10
Specs updated successfully.
Change 'brep-mesh' archived as '2026-10-05-brep-mesh'.
```

Then `git rm -r openspec/specs/exact-engine-dependency
openspec/specs/exact-geometry openspec/specs/occt-engine
openspec/specs/manifold-engine` (Decision 11): 45 specs remain, and no spec
under `openspec/specs/` names any of the four.

**12.3** The scenario titles of `scenario-titles.tsv`, renamed by a script
that fails on a row whose old title is missing (scratch `rename_titles.py`):

```
rows 74 replaced 75 missing 0
```

(one title occurs twice in its spec and is renamed at both.) The Purposes of
Decision 11 written: `brep-engine-dependency`, `brep-geometry`,
`brep-engine`, `mesh-engine` (in place of OpenSpec's "TBD"),
`kernel-extras` (the providers' paths, ADR-180), `leaf-contract`,
`mesh-engine-dependency`, `step-import`, `test-framework`.
`openspec validate --specs --strict`:

```
Totals: 45 passed, 0 failed (45 items)
```

What remains of the former words in the baseline specs is intended: the
scenarios and requirements that refuse them (`kernel-extras`' former
addresses and extras, `cli`'s former selectors and variable,
`test-framework`'s refusal of `SOLID_TEST_KERNEL`, `leaf-contract`'s version
3 note), and `FacetedBox`, a fixture class.

**12.4** The moved-names table, for the workspace's
`scripts/load-projects.d/brep-mesh.toml`:
`openspec/changes/archive/2026-10-05-brep-mesh/moved-names.toml` (103 rows,
93 importable and 10 informational). The universe sweep's JSON is beside it,
`load-projects.json`.

**12.5** `machinome/occt` and `machinome/manifold` are gone from the bench
(`ls` finds neither; `git clean -ndX` lists nothing). The campaign plan's
entry is marked done with this file as its evidence.

The final suite after the archive, once, alone (10 min 55 s of wall time):

```
4568 passed, 4 skipped, 55 warnings, 6338 subtests passed in 652.69s (0:10:52)
```
