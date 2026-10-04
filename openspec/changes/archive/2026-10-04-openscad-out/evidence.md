# Evidence — `openscad-out`

The eighth cycle of layer 1 of the lean-core campaign, the first of the phase
"The next phase: the architecture ready for the split"
(`workflow/ongoing/lean-core.md`). Worktree
`machinome/WTs/v0.8-split-openscad-out`, branch `v0.8-split-openscad-out`, cut
from `v0.8-split` at a16d45a. Planning commit f76aa20 (ratified by the pilot on
4 October 2026, with the answers to design.md's Open Questions the briefing
records: 1 SolidPython kept in the writer and the `openscad` extra; 2
`closed_expression` stays in the core; 3 adoption registered by
`machinome.node.solid2`; 4 the transient record; 5 the default renderer stays
`openscad`; 6 to 11 every recommendation taken). Every command below ran with
`env -C <worktree>`, `PYTHONPATH=<worktree>` and the workspace venv (Python
3.12.3, solidpython2 2.1.3, OpenSCAD at `/usr/bin/openscad`); pytest ran one
process at a time, never in parallel, each after the process guard printed
nothing.

## 1. Baseline on the unmodified tree (f76aa20)

### 1.1 The facts design.md rests on, re-measured

**The gate's red count.** The rule of design.md Decision 1, written as the
gate itself (`tests/test_core_names_no_scad.py`, task 2.1, its `scan()` and
`report()` run as a script before any source change): every `machinome/**/*.py`
file outside the four allowed zones, by path and by `NAME`, `STRING`,
`COMMENT` and `FSTRING_MIDDLE` token.

```
  97 machinome/node/base.py (21: 'scad_engine', 21: 'require_scad_engine', 97: '_scad_engine_for')
  41 machinome/node/openscad.py (0: 'machinome/node/openscad.py', 7: 'parse_scad', 7: 'get_scad_file_as_dict')
  40 machinome/scad_engine.py (0: 'machinome/scad_engine.py', 5: '"""The OpenSCAD engine seam: the contrac', 38: '#: The OpenSCAD engine contract version ')
  33 machinome/manager/snapshot.py (12: 'openscad', 12: 'OpenScadImportError', 12: 'OpenScadRenderer')
  29 machinome/node/leaf.py (20: '"""The base of every leaf: a node that p', 99: '"""A leaf knows its own source set at co', 111: 'scad_file')
  24 machinome/openscad/engine.py (0: 'machinome/openscad/engine.py', 5: '"""The OpenSCAD engine\'s provider: what ', 24: 'scad_render')
  24 machinome/source_generation.py (47: '_PendingScadPublication', 359: '# delay non-rigid SCAD publication safel', 361: 'coalesces_scad')
  23 machinome/core/builder.py (375: '# materialize without constructing an as', 686: '# A `.scad` no current node writes never', 690: '# (`scad-presentation`, design.md Decisi')
  17 machinome/openscad/binary.py (0: 'machinome/openscad/binary.py', 5: '"""Conditional availability contract for', 10: 'scad_engine')
  16 machinome/math.py (5: '"""The expression vocabulary: one semant', 86: '#: OpenSCAD engine.', 90: '#: Every OpenSCAD builtin this module ma')
  13 machinome/expression_graph.py (4: '"""The framework\'s symbolic value and it', 29: 'scad_engine', 84: '#: one membership test and never consult')
  13 machinome/node/flexible.py (112: '_uses_legacy_scad_materialization', 113: '# Flexible SCAD is a per-binding snapsho', 134: "#: The snapshot artifact this node's las")
  13 machinome/node/presentation.py (5: '"""A node\'s SCAD presentation, described', 79: '"""`value` as a description: itself when', 87: '"""A description whose every `ArtifactIm')
   9 machinome/node/internal.py (15: '"""Wraps an InternalNode subclass render', 129: 'as_scad', 132: 'scads')
   7 machinome/core/expressions.py (5: '"""Compile native motion graphs and lega', 34: '"""Text that is not in the language the ', 124: '"""Parse a scalar or a local SCAD closur')
   7 machinome/openscad/__init__.py (0: 'machinome/openscad/__init__.py', 5: '"""The OpenSCAD engine.\n\nThis package ex')
   5 machinome/core/camera.py (5: '"""Convert OpenSCAD command-line camera ', 10: 'OPENSCAD_FOV', 18: 'OPENSCAD_FOV')
   4 machinome/node/exact_leaf.py (78: '# `model` is the SCAD presentation after', 159: 'as_scad', 160: '"""Present the canonical native artifact')
   4 machinome/node/stl.py (95: '"""A part that comes from a committed ST', 169: '# stale (`publish_artifact` asks), and t', 176: 'as_scad')
   3 machinome/model.py (487: '_uses_legacy_scad_materialization', 488: 'as_scad', 489: 'generate_scad')
   3 machinome/node/__init__.py (5: '"""Top-level package for Solid Framework', 81: "'OpenScadNode'", 81: "'openscad'")
   3 machinome/node/operations.py (5: '"""\nThe operations that can be applied t')
   3 machinome/node/qualified.py (214: '# OpenSCAD on the scad path. `_attr_name', 332: '"""Walk `root`\'s tree in linked order, b')
   3 machinome/node/sources.py (38: '"""The identity of a leaf whose part com', 129: '"""Refuse a leaf whose declared source f')
   3 machinome/parameters.py (140: "'scad_file'", 140: "'mesh_scad_file'", 380: '"""A formula applying one of `machinome.')
   3 machinome/viewers/browser.py (5: '"""Transparent PNG rendering through the', 152: '"""Refuse a document the installed viewe', 169: '--renderer openscad.')
   2 machinome/node/jscad.py (94: 'as_scad', 95: '"""Present the part\'s STL artifact: the ')
   2 machinome/node/sheet_leaf.py (65: '# The validated profile of this render, ', 180: '"""The exact adapter\'s STL and BREP, plu')
   1 machinome/core/expression_parser.py (4: '"""Stack-driven scalar parser, including')
   1 machinome/core/pieces.py (173: '"""Patchable counter seam for full artif')
   1 machinome/motion/couplings.py (2619: '"""Drop what THIS assembly bound during ')
   1 machinome/motion/joints.py (1072: '# binding, and for a symbolic one the Op')
   1 machinome/node/assembly.py (712: '"""What `node.time` reads: the one reade')
   1 machinome/node/build123d.py (65: '"""\n    Represents a 3D object created u')
   1 machinome/node/cadquery.py (58: '"""\n    Represents a 3D object created u')
   1 machinome/node/decorators.py (7: '"""Use this decorator to convert a OpenS')
   1 machinome/test.py (318: '"""`solid` if the engine built it cleanl')
modules: 37  occurrences: 453
```

37 modules, 453 occurrences, module for module design.md's list.

**The probe sites of Decision 5.** An AST scan of `machinome/` for
`getattr(x, '<name>', <default>)` and `hasattr(x, '<name>')` whose name is a
member of the set, `children`, `src` or `scad_authored` (scratch
`probe_scan.py`):

```
machinome/core/builder.py:779 getattr(node, 'scad_authored', False)
machinome/core/builder.py:782 getattr(node, 'children', ())
machinome/core/builder.py:725 getattr(node, 'exact', False)
machinome/core/builder.py:734 getattr(node, 'declared_markings', None)
machinome/core/pieces.py:248 getattr(node, 'src', None)
machinome/core/pieces.py:250 getattr(node, 'stl_file', repr(node))
machinome/core/serializer.py:964 getattr(node, 'declared_markings', None)
machinome/node/assembly.py:804 getattr(root, 'children', ())
machinome/node/declarative.py:1173 getattr(cls, 'flexible', False)
machinome/node/declarative.py:1173 getattr(cls, 'rigid', False)
machinome/test.py:497 getattr(node, 'flexible', False)
machinome/test.py:500 getattr(node, 'stl_file', None)
machinome/test.py:1984 getattr(node, 'flexible', False)
machinome/test.py:2002 getattr(node, 'base_mesh', None)
machinome/test.py:237 getattr(node, 'exact', False)
machinome/viewers/openscad.py:85 getattr(node, 'scad_authored', True)
```

The fourteen sites of design.md's table (`declarative.py:1173` is one site
holding two probes) and `node/assembly.py:804`, which design.md classifies as
structure, not a capability probe, and leaves unchanged. Eleven of the
sixteen calls name a member of the declared set itself; `builder.py:779` and
`viewers/openscad.py:85` (`scad_authored`), `builder.py:782` (`children`) and
`pieces.py:248` (`src`) are replaced by the design but are outside the set the
permanent scan (task 2.6) pins.

**The SolidPython probes of Decision 2** (scratch `probe_solid.py`, through
`machinome.openscad.engine.scad_text`):

```
129
'translate(v = [1, 2, 3]) {\n\tunion() {\n\t\timport(file = "a.stl", origin = [0, 0]);\n\t\timport(file = "b.stl", origin = [0, 0]);\n\t}\n}\n'
161
'use </tmp/tmpto_u_ywb/m.scad>;\n\ntranslate(v = [1, 2, 3]) {\n\tunion() {\n\t\timport(file = "a.stl", origin = [0, 0]);\n\t\timport(file = "b.stl", origin = [0, 0]);\n\t}\n}\n'
suffix equal: True prefix: 'use <<tmp>/m.scad>;\n\n'
m(a = 3, b = 4.5);
TypeError too many arguments to m(...)
```

`Translate((1, 2, 3), Union((ArtifactImport('a.stl'), ArtifactImport('b.stl'))))`
is 129 bytes, and the same description after `solid2.import_scad('m.scad')` in
the same process is the same text preceded by `use <…/m.scad>;` and a blank
line. Through `get_scad_file_as_dict` (which takes the `Path` that
`resolve_scad_filename` returns), `m(3, b=4.5)` over `module m(a, b=2)` writes
`m(a = 3, b = 4.5);` and `m(3, 'x', True, [1, 2])` raises
`TypeError: too many arguments to m(...)`.

**What the four imports load** (scratch `probe_modules.py`: import
`machinome.node`, `machinome.node.base`, `machinome.core.builder`,
`machinome.test`; list the modules that are or lie under `solid2`,
`machinome.scad_engine`, `machinome.openscad`, `machinome.node.openscad`):

```
['machinome.scad_engine']
```

### 1.2 The three byte goldens

Each `--check` in a fresh process, before any source change:

```
leaf_contract_golden       golden comparison: 7 fixtures, 77 values, 0 differences            (6.0 s)
scad_presentation_golden   golden comparison: 34 values, 0 differences, 9 presentation files absent as expected   (3.9 s)
expression_type_golden     golden comparison: 17 values, 0 differences                        (1.5 s)
```

### 1.3 The touched suites, unmodified tree

**A stop, and its environmental cause.** The first baseline run hung: in
`test_scad_presentation.py`, `machinome build
tests/scad_where_read_project/native.py:StlBench` (with `solid2` refused)
printed `START` about once a second, each generation ending `SOURCE_CHANGED`
(11), for seven minutes, and was stopped. Reproduced outside pytest
(`timeout 40 … machinome build …:StlBench`: exit 124, 12 `START` lines) and
diagnosed in-process: the root's loaded file set is `['native.py']`
(mtime `…775132173116` ns), and after preparation it is
`['bracket.stl', 'native.py', 'tab.stl']`, whose maximum is `tab.stl`'s
`…775133173149` ns; `Builder._start` compares the two and returns
`SOURCE_CHANGED`, every generation, forever. The worktree's checkout wrote
`tab.stl` one microsecond after `native.py`. This is the wart the mesh-engine
cycle recorded ("a `machinome build` hanging … in a fresh project worktree",
`openspec/changes/archive/2026-10-04-mesh-engine/evidence.md` § 2), on the
unmodified source, and not this cycle's to fix. The bench's 659 unmodified
tracked files under `tests/` were given one mtime
(`touch -m -d @1791126775`, the checkout's second; contents untouched, `git
status` unchanged) and the build then finished in one generation (exit 0, one
`START`).

One pytest process over the 49 files of task 1.3 (the 41 test modules among
design.md Decision 15's 48 files, the other seven being scripts and fixtures,
and the twelve the task names, four of which are among the 41), with the
group 2 additions set aside (the modified files restored from f76aa20 for the
run, the new ones moved out):

```
1259 passed, 2 skipped, 21 warnings, 386 subtests passed in 183.39s (0:03:03)   (wall 184.8 s)
```

## 2. Red tests, on the unmodified source (f76aa20)

New files: `tests/test_core_names_no_scad.py` (2.1), `tests/test_openscad_node.py`
(2.2, 2.3, 2.10), `tests/test_leaf_capability_set.py` (2.6, 2.7),
`tests/test_supported_node_types.py` (2.12). Extended: `tests/test_kernel_extras.py`
(2.4: `solidpython2` among the kernels no bare install carries, the `openscad`
and `solid2` extras and `all`, `requirements.txt`, and the two family modules
among `MODULES`), `tests/test_snapshot.py` (2.5, class
`SnapshotRendererFromTheTableTest`), `tests/test_build_publication.py` (2.8,
class `SweepByDeclarationTest`), `tests/test_content_verified_currency.py`
(2.8, class `TransientRecordTest`), `tests/test_generation_dedup.py` (2.9,
class `PublishedRecordTest`; the coalescing tests are rewritten in group 9),
`tests/test_expression_type.py` (2.11, class `ClosedExpressionTest`),
`tests/test_manager_new.py` (2.13, class `TemplateByInstalledExtrasTest`),
`tests/test_simulation_sim.py` (2.14, class `MeshesWithoutPresentationTest`;
not among Decision 15's files, extended for task 2.14).

One pytest process over them (68 tests collected):

```
64 failed, 22 passed, 2 warnings, 53 subtests passed in 12.80s   (wall 13.8 s)
```

(failures counted with failing subtests). Every red test and its reason,
verbatim:

| task | test | reason |
|---|---|---|
| 2.1 | `TheCoreNamesNoScadTest` | `AssertionError: {'machinome/core/builder.py': (23, …)} != {}`, the report listing the 37 modules of § 1.1 |
| 2.2 | `test_the_package_modules_import`, `test_both_node_types_are_family_leaves` | `ModuleNotFoundError: No module named 'machinome.node.openscad.writer'; 'machinome.node.openscad' is not a package` (and `.leaf`) |
| 2.2 | `test_the_former_addresses_are_gone` (subtests) | `AssertionError: ModuleNotFoundError not raised` |
| 2.2 | `test_the_viewer_imports_neither_former_address` | `AssertionError: {'machinome.scad_engine'} is not false` |
| 2.3 | `test_the_package_refuses_naming_the_openscad_extra`, `test_solid2_refuses_naming_the_solid2_extra` | `'ModuleNotFoundError' != 'ExtraUnavailable'`, `{"type": "ModuleNotFoundError", "name": "solid2", "extra": null, "message": "No module named 'solid2'"}` |
| 2.3 | `test_the_root_export_carries_the_refusal` | likewise, `"message": "No module named 'solid2' (raised resolving machinome.node.Solid2Node from .solid2)"` |
| 2.3 | `test_the_viewer_refuses_with_the_package` | `AssertionError: unexpectedly None : null` (the viewer imports without SolidPython) |
| 2.3 | `test_a_project_without_the_family_loads_none_of_it` | `Lists differ: ['machinome.scad_engine'] != []` |
| 2.4 | `test_a_bare_install_carries_no_kernel` | `Items in the first set but not the second: 'solidpython2'` |
| 2.4 | `test_all_names_every_kernel_extra` | `Items in the second set but not the first: 'solid2' 'openscad'` |
| 2.4 | `test_each_extra_lists_what_its_module_needs` (subtests `openscad`, `solid2`, `all`), `test_the_solid2_extra_installs_the_openscad_extra` | `KeyError: 'openscad'`, `KeyError: 'solid2'`, and `all` lacking both |
| 2.4 | `test_each_kernel_module_refuses_each_absent_kernel` (subtests `machinome.node.openscad`, `machinome.node.solid2`) | `'ModuleNotFoundError' != 'ExtraUnavailable'` |
| 2.5 | `test_the_choices_and_the_default_come_from_the_table` | `ImportError: cannot import name 'supported' from 'machinome.node'` |
| 2.5 | `test_the_default_renderer_is_refused_naming_its_extra`, `test_the_named_renderer_is_refused_naming_its_extra` | the last line of standard error is `Error: the OpenSCAD snapshot renderer requires the OpenSCAD engine because it renders the SCAD the OpenSCAD engine writes, and the module solid2 cannot be found; install SolidPython with 'pip install solidpython2', or use --renderer web`, not R4 |
| 2.5 | `test_the_web_renderer_composes_no_presentation` | `AssertionError: assemble() was called` |
| 2.6 | `test_the_core_speaks_contract_two` | `AssertionError: 1 != 2` |
| 2.6 | `test_a_declaration_of_one_is_refused_naming_both_versions` | `AssertionError: TypeError not raised` |
| 2.6 | `test_a_self_materializing_leaf_answers_the_whole_set`, `test_a_family_leaf_keeps_its_own_scad`, `test_the_node_base_keeps_no_artifact` | `AttributeError: 'MeshBlock' object has no attribute 'kept_artifacts'` (and `'SimpleCylinder'`, `type object 'AbstractBaseNode'`) |
| 2.6 | `test_the_core_reads_the_set_directly` | `Lists differ: ["machinome/core/builder.py:725 getattr(node, 'exact', False)", …] != []`, eleven calls |
| 2.7 | `test_it_is_refused_naming_the_node_and_its_stl` | `AssertionError: AssertionError('a process was started') is not an instance of <class 'RuntimeError'>`: the build reached the patched `Popen` |
| 2.8 | `test_the_scad_is_kept_by_declaration_not_by_suffix` | `AssertionError: True is not false`: the `.scad` stayed with `kept_artifacts` patched to `()` |
| 2.8 | `test_a_transient_artifact_goes_on_an_unchanged_document`, `TransientRecordTest.test_a_transient_record_carries_the_mark` | `TypeError: record() got an unexpected keyword argument 'transient'` |
| 2.8 | `TransientRecordTest.test_publish_passes_the_mark` | `TypeError: publish() got an unexpected keyword argument 'transient'` |
| 2.8 | `test_the_renderer_marks_only_a_root_it_does_not_keep_transient`, the other two `TransientRecordTest` cases | `AttributeError: module 'machinome.currency' has no attribute 'recorded_transient'` |
| 2.8 | `test_the_builder_names_no_kind_of_artifact_it_sweeps` | `AssertionError: 'scad_only' unexpectedly found in …` |
| 2.9 | `test_a_phase_has_no_coalescing` (subtests `defer_scad`, `coalesces_scad`, `pending_scad_count`, `_flush_scad`, `_pending_scad`) | `AssertionError: True is not false` |
| 2.9 | `test_the_assembly_phase_checkpoints_post` | `Lists differ: ['assembly pre-flush', 'assembly post-flush'] != ['assembly post']` |
| 2.9 | `test_historical_identity_is_not_current_identity` | `AssertionError: True is not false` (`has_scad_artifact` exists) |
| 2.10 | `test_adoption_needs_the_solid2_module` | `Lists differ: [['name', '$t'], ['name', '$t']] != [None, ['name', '$t']]` |
| 2.10 | `test_registering_an_adopter_is_idempotent` | `AttributeError: module 'machinome.expression_graph' has no attribute '_ADOPTERS'` |
| 2.11 | `test_the_text_of_a_shared_value_is_its_closed_expression` | `AttributeError: module 'machinome.core.expressions' has no attribute 'closed_expression'. Did you mean: 'scad_expression'?` |
| 2.12 | every `TheTableTest` and `LoadRefusesTest` case but two | `ModuleNotFoundError: No module named 'machinome.node.supported'` (in-process and in the subprocesses), `FileNotFoundError: … machinome/node/supported.py` |
| 2.12 | `test_no_reader_spells_a_node_types_module` (subtests `cli.py`, `manager/import_step.py`) | `Lists differ: ['step', 'step'] != []` |
| 2.13 | `test_without_solidpython_the_cadquery_template` | the module written is the SolidPython template: `'from machinome.node import Solid2Node\nf[200 chars]0)\n' != "import cadquery as cq\n\nfrom machinome.[251 chars]e)\n"` |
| 2.13 | `test_without_either_it_is_refused_and_writes_nothing` | `AssertionError: 0 != 1 : Created new machinome project at /tmp/tmp7hfnccxc/myproj/` |
| 2.14 | `test_meshes_are_built_without_assembling` | `AssertionError: assemble() was called` |

Green on the unmodified source, as guards: the rule's unit cases
(`TheRuleTest`, 4), `test_the_node_type_is_defined_at_its_address`, the
kernel-metadata and refusal cases this cycle does not change,
`test_a_family_leaf_keeps_its_scad_through_a_changed_document` (the
characterisation of a kept `.scad`), `test_the_root_exports_the_same_objects`
and `test_with_every_extra_the_solidpython_template`.

## 3. The table and the declared set

`machinome/node/supported.py` (3.1): `NodeType(classes, renderers=(),
commands=())`, `NODE_TYPES` (the eight rows of design.md Decision 6),
`DEFAULT_RENDERER = 'openscad'`, `load(key)` (an `ExtraUnavailable` of the
module passes unmodified; a `ModuleNotFoundError` whose `name` is the node
type's own address becomes `ExtraUnavailable(key, 'the <key> node type
(<classes>)', 'machinome.node.<key>')`, R3; any other propagates),
`renderer(name)` (loads the row's node type first, then the provisional
column's class) and `needed_by(command)`. The node root's export table takes
its node-type names from `NODE_TYPES` (3.2); its docstring names no
technology.

3.3: `as_scad` is `present` on the node base (raising), `LeafNode` (the
default: materialize when the STL is not current, then
`artifact_import(local_stl)`), `InternalNode`, `FlexibleNode` and the two
family leaves; the identical overrides of `exact_leaf.py`, `stl.py` and
`jscad.py` are deleted (`StlNode`'s called `materialize` unconditionally and
`JScadNode`'s called `JScadNode.materialize` by name; `publish_artifact` and
the default's currency check make both the default's). `_model_for_own_scad`
is `presentation()`; the node base gains `kept_artifacts()` returning `()`.
Between groups 3 and 4 the legacy detection (`_uses_legacy_scad_materialization`)
still looked for an `as_scad` override and answered `False` where no class
defines one, so the suite stayed runnable until 4.5 removed it.

3.4: the probe sites read directly: `test.py` (`_routes_exact`,
`_fast_geometry`, `_exact_identity`, `_mesh_in_frame`), `core/builder.py`
(`_artifacts_are_current`'s `exact` and `declared_markings`, the sweep's
`children`), `core/pieces.py` (`node.src`, the `stl_file`/`repr` fallback
gone), `core/serializer.py` (`marking_entries`, its comment rewritten) and
`node/declarative.py` (`cls.rigid`, `cls.flexible`); the sweep's
`scad_authored` probe went with `collect_scad` in 4.7 and the viewer's in 4.6.
`tests/stand_in.py` holds `StandIn` (`exact`, `flexible`, `stl_file`,
`base_mesh`, `children`, `src`, `declared_markings()`, `kept_artifacts()`)
and `NodeDouble`, a `SimpleNamespace` with the same answers whose `src`
defaults to its `stl_file` (the value the removed fallback gave a double
without a source). Derived from it, as the suite's runs reported each
`AttributeError`: `FakeNode` and its subclasses, `IntersectsWhenPositive`,
`FixedVolumeOverlap`, `IntersectsWhenTranslationPositive` and `Bore`
(`test_assertions.py`); `FakeNode` (`test_broad_phase_culling.py`,
`test_builder_lifecycle.py`, `test_connectivity.py`); `FakeNode`,
`MeshOnlyNode`, `ExactFakeNode` (`test_intersection_memo.py`); `ShapeNode`
(`test_exact_geometry.py`); `RigidNode` and `Assembly`
(`test_assembly_integrity.py`, not in design.md's list: its doubles serve
`test_broad_phase_culling.py`); `StlNode` (`test_connectivity.py`'s own
double); and `NodeDouble` for the `SimpleNamespace` doubles of
`test_builder_lifecycle.py` (six), `test_connectivity.py` (`stl_node`),
`test_expression_bindings.py` and `test_source_generation.py` (one each).

3.5: `CONTRACT = 2`, its comment naming what changed; `LeafNode`'s docstring
lists the delta's declared members (`StlRenderStart` among them, qualified by
its module) and describes the set.

One pytest process over the 61 files of § 1.3 and the new and leaf-contract
files, after 3.1 to 3.5:

```
145 failed, 1288 passed, 2 skipped, 25 warnings, 647 subtests passed in 236.68s (0:03:56)   (wall 238.6 s)
```

Of the failures, the group-2 tests that later groups turn green, and the
stand-ins the first pass did not yet derive (`'StlShapeNode' object has no
attribute 'flexible'` ×20, `'types.SimpleNamespace' object has no attribute
'src'` ×14, and so on). After deriving them, the stand-in suites
(`test_assertions.py`, `test_exact_geometry.py`, `test_broad_phase_culling.py`,
`test_connectivity.py`, `test_builder_lifecycle.py`,
`test_expression_bindings.py`, `test_source_generation.py`,
`test_intersection_memo.py`):

```
25 failed, 220 passed, 7 warnings, 29 subtests passed in 11.73s
```

the remaining failures `'NodeDouble' object has no attribute 'scad_authored'`
(13) and `'FakeNode' object has no attribute 'scad_authored'` (2), which the
sweep's `collect_kept` of 4.7 removes, and the five `SimpleNamespace` and two
double classes fixed next. **A breach of the run rule, recorded:** this
13-second run started while the process guard printed another process, a
`machinome test --exact simulation/head_passages.py:HeadPassages` in
`/mnt/data/machinome-projects/3D-Printers/Voron-2` (not this cycle's); the
guard's output was not gating the command. Every later run is gated by a
script that waits until the guard prints nothing.

## 4-9. The family as a package, the core without it, the commands, the tests

**The package** (4.1): `machinome/node/openscad/__init__.py`
(`require_extra('openscad', 'machinome.node.openscad (OpenScadNode and the
OpenSCAD writer)', 'solid2')` first, then `OpenScadNode` over
`ExternalSourceIdentity, ScadLeafNode`, its `scad_code` reading the writer),
`leaf.py` (`ScadLeafNode`: `fn`, `scad_file` as a property at
`writer.scad_file(self)`, `scad_code`, `generate_scad()`, `present`,
`materialize`, `kept_artifacts()` = `(scad_file,)`, `generate_stl()` moved
from the node base unchanged but for the binary's address,
`stl_builder_command(_for)`), `writer.py` (`scad_text` moved unchanged,
`scad_file(node)`, `scad_code(node)`, `generate_scad(node, code=None)`
publishing through `currency.publish_text`, transient unless the path is in
the node's `kept_artifacts()`, with the generation's `has_published` /
`remember_published` and the node base's log lines), `binary.py`
(`OpenScadUnavailable(RuntimeError)`, its message unchanged). `node/openscad.py`
deleted. Two choices inside the design: `writer.generate_scad` takes an
optional `code` callable (the text when the caller has its own, as the
generation tests' doubles do; the default is the family leaf's own
`scad_code`, else `scad_code(node)`), and `writer.scad_file(node)` is
`<basepath>.scad` for any node, which the viewer uses for a root that is not a
family leaf (non-family nodes no longer carry `scad_file`).

4.2: `machinome/node/solid2.py`: `require_extra('solid2', ...)` first;
`adopt` moved unchanged and registered at import; `Solid2Node(ScadLeafNode)`
with `as_number` on `machinome.node.openscad.binary.require_openscad`. 4.3:
`expression_graph.register_adopter` (idempotent by identity) and `_ADOPTERS`;
`symbolic` asks them after numbers, `GraphValue` and `ExpressionNode`; no
import of a seam. 4.4: `currency.publish_text` (the former
`_atomic_write_text`, unchanged but for `transient`), `record` and `publish`
take `transient=False`; a transient record is version 3 with
`"transient": true` (and `recipe` when given); `recorded_transient` reads the
key, `False` without it, without a record or for an unreadable one.

4.5: the node base loses `fn`, `scad_file`, `mesh_scad_file`, the seam
import, `_scad_engine_for`, `_publish_scad`, `_atomic_write_text`,
`_uses_legacy_scad_materialization`, `scad_authored`,
`_render_can_be_skipped`, `_require_scad_engine`, `scad_code`,
`generate_scad`, `stl_builder_command(_for)` and the OpenSCAD launch;
`_prepare` calls `materialize` only; `generate_stl` keeps its three early
returns and raises `ArtifactNotProduced` (R7), defined beside
`StlRenderStart`. `LeafNode`, `FlexibleNode` and `SheetLeafNode` lose their
legacy and render-skip members; `model.py`'s legacy branch and
`parameters._RESERVED`'s `scad_file` and `mesh_scad_file` go. 4.6:
`machinome/viewers/openscad.py` imports `machinome.node.openscad.binary` and
`.writer`; `present(node)` assembles and has the writer publish the root's
`.scad`; `withdraw` keeps a path the root lists in `kept_artifacts()`;
`render` reports the failures as the snapshot command did, its messages
verbatim, around `draw` (the former `render`, which raises). 4.7: the sweep's
`collect_kept` over `kept_artifacts()` and `children`; `scad_only` becomes
`transient_only`: an unreferenced, unkept file whose record
`recorded_transient` answers is removed with its record (and whichever of the
pair the walk met first), on every successful build; the changed-document
sweep otherwise as before. 4.8: `machinome/openscad/` and
`machinome/scad_engine.py` deleted. 5.1: `source_generation.py` loses
`_PendingScadPublication`, `coalesces_scad`, `_pending_scad`, the
pre-flush/post-flush branch (the assembly phase checkpoints `assembly post`),
`pending_scad_count`, `defer_scad`, `_flush_scad` and its `OrderedDict`
import; `_scad_artifacts`, `has_scad_artifact`, `remember_scad_artifact` are
`_published`, `has_published`, `remember_published`. Group 5 was applied with
group 4 because the writer of 4.1 reads the renamed record.

6.1: `manager/snapshot.py`: `--renderer` choices `['web', *renderer_names()]`,
default and help from `DEFAULT_RENDERER`; `handle` resolves
`supported.renderer(name)` for every renderer but `web` before loading the
node and answers `ExtraUnavailable` with R4 and exit 1; the table renderer is
held as `presenter` (a class attribute `None`, so a `Snapshot.__new__` double
answers it), whose `present` runs in the build lock and whose `render`
reports its own failures; `OPENSCAD_RENDERER`, the seam import and the
OpenSCAD error branch are gone; three help and comment texts no longer name
the technology. 6.2: `Sim(meshes=True)` calls `build_stls()` only. 6.3:
`COMMANDS['import-step'][2] == 'step'`; `require_needed_module` loads through
`supported.load`; `manager/import_step.py` takes `StepAssembly` from
`supported.load('step')`, and its docstring no longer spells the module. 6.4:
`root/__init__.py` is `root/solid2.py` (byte-identical, `cmp` against
f76aa20's file) and `root/cadquery.py` is new; `machinome new` takes the first
of `solid2`, `cadquery` that `supported.load` admits and refuses with R8
before writing anything. 6.5: `tests/scad_presentation_golden.py` and
`tests/expression_type_golden.py` read a family leaf's text from the leaf and
any other node's through `writer.scad_code(node)`, and the presentation
golden reads `writer.scad_file(node)`; the JSON files are untouched.

7.1: `solidpython2==2.1.*` leaves `dependencies`; extras `openscad` and
`solid2` (`machinome[openscad]`), `all` names both; `setup.cfg` ignores E402
for `machinome/node/openscad/__init__.py` and `machinome/node/solid2.py`;
`requirements.txt` keeps SolidPython and names the two extras in its comment.
The metadata test reads `pyproject.toml`, so the bench was not reinstalled.

8.1: every remaining offender reworded without changing behaviour (the list
of tasks.md, and `cli.py`, `core/builder.py` and `node/leaf.py`, whose new
comments first named this change by name, which the gate refuses: they cite
ADR-177, 178 and 179 instead). `scad_expression` is `closed_expression`
(`core/expressions.py`, its caller `bind_expressions`, `GraphValue.__str__`);
`OPENSCAD_FOV` is `DEFAULT_FOV`, the camera docstrings describing the two
`--camera` forms; `viewers/browser.py`'s suggestion is
`--renderer {DEFAULT_RENDERER}`, its two docstrings reworded;
`InternalNode.present`'s local `scads` is `presented`. **The gate after 8.1:**

```
modules: 0  occurrences: 0
```

### 9.1 The repointed tests, and why

Merged into `tests/test_openscad_node.py`, then deleted:
`test_openscad_engine.py` (adoption, the writer's text, the binary contract
and its unchanged messages, at their new addresses; the package-exports and
contract-version cases tested what is gone) and `test_scad_engine_seam.py`
(the seam's resolution, absence, breakage and contract-version cases test a
seam that no longer exists; its golden-without-the-engine case cannot be
built without the family, which the golden's parts are; kept, repointed: a
SolidPython value in a process that never imported `machinome.node.solid2`
meets the existing refusal, numbers never consult an adopter, and the
counting of SCAD text and binary asks, now on the writer's `scad_text` and the
binary's `require_openscad`).

Rewritten onto the family and the writer:

| file | changed assertion targets, and why |
|---|---|
| `test_scad_presentation.py` | importers outside the family: the template `root/solid2.py`; reaches into the package: `viewers/openscad.py`; absences `solid2` and `machinome.node.openscad`, refused naming `machinome[openscad]`; SCAD text refused at the table (`supported.load`) and at the writer's import; the legacy leaf's build refused with R7 naming `node bracket (Bracket)` (no longer an engine refusal); the snapshot refusal is R4; seeds through `currency.publish_text` and `writer.scad_file`; the killed render's root `.scad` seeded through `writer.generate_scad`, published transient, and removed by the unchanged build; a root's text through `writer.scad_code` |
| `test_scad_import_paths.py`, `test_two_pipes.py`, `test_scad_stl.py`, `test_coarse_filesystem_freshness.py`, `test_content_verified_currency.py`, `test_declarative_nodes.py`, `test_declarative_render.py`, `test_document_drivers.py`, `test_expression_bindings.py`, `test_markings.py`, `test_molejo_adapter.py`, `test_project_through_a_symlink.py` | a non-family node's `scad_code`, `scad_file` and `generate_scad()` read through the writer (`tests/base.py`'s `scad_code` helper answers a family leaf's own text, a double's attribute, or the writer's) |
| `test_generation_dedup.py` | the writer's `generate_scad(node, code)` and `currency.publish_text` in place of `AbstractBaseNode.generate_scad` and `_atomic_write_text`; doubles carry `basepath` and `kept_artifacts`; the coalescing cases (last desired value, path order, stable identities across phases, pre-flush, flush and post-flush failures, one log line per flushed value) are removed with the coalescing, replaced by `PublishedRecordTest` (2.9), "publication is immediate in every phase and outside one", "non-rigid instances sharing a path publish each request" and "a failed publication leaves only completed ones"; two assemblies sharing a path now publish twice, the last text standing |
| `test_openscad_dependency.py`, `test_no_class_name_recognition.py`, `test_build123d_adapter.py`, `test_exact_geometry.py`, `test_flexible_node.py`, `test_jscad_integration.py`, `test_sheet_leaf.py`, `test_stl_node.py`, `test_step_node.py`, `test_manager_develop.py` | the binary's address `machinome.node.openscad.binary`; the launch patched at `machinome.node.openscad.leaf.Popen` (the node base launches nothing); the renderer's raising method is `draw` (`render` now reports and exits 1), and `test_snapshot_does_not_substitute_the_web_renderer` patches `draw` |
| `test_snapshot.py` | mock roots carry `basepath` and `kept_artifacts` (the viewer reads `writer.scad_file` and the root's declaration); `assemble()` is the presenter's (`test_assemble_is_called` asserts `presenter.present(node)`; the build-lock test observes it); the two real-node preparations set the presenter `handle` would; the diagnostics call `draw`; the patched renderer and `find_xvfb_run` are `OpenScadRenderer`'s |
| `test_backend_neutral_materialization.py` | `present` patched in place of `as_scad`; the legacy-bridge case now proves an `as_scad` override selects no bridge (the native hook runs, the override never) |
| `test_builder_lifecycle.py` | the kept-`.scad` sweep case: `kept_artifacts` declares the file; on the unchanged document a transient `.scad` goes and a non-transient one stays (formerly every `.scad` no node wrote went); doubles derive from the stand-in |
| `test_browser_renderer.py`, `test_camera.py`, `test_source_set.py`, `tests/vet_projects/framework_internal/sim/model.py`, `scad_presentation_golden.py`, `expression_type_golden.py`, `tests/base.py` | `OpenScadRenderer.render`, `DEFAULT_FOV`, the writer module, `import machinome.node.openscad`, the writer for a non-family node's text, the `scad_code` helper |
| `contract_package/scad_stand_in.py` | `MeshScad` is a `Solid2Node` subclass (its refusal message unchanged, "node MeshScad (MeshScad) requires the OpenSCAD binary …") |
| `scad_presentation_project/parts.py` | `Legacy` is a `Solid2Node` subclass; its `.scad` and text are the golden's bytes (§ 11) |

Renamed calls only: `as_scad(` → `present(` in `test_stl_node.py`,
`test_build123d_adapter.py`, `test_sheet_leaf.py`, `test_connectivity.py`
(and one test's name), `test_source_set.py`, `test_source_generation.py`
(`JScadNode.present` on a double, which gains a `materialize` routed to
`JScadNode.materialize`: the leaf base's default calls the node's own),
`test_molejo_adapter.py`, `test_traversal_naming.py`,
`test_model_consumption.py` (an override); `_render_can_be_skipped` →
`_prepare_can_be_skipped` in `test_markings.py`, `test_sheet_leaf.py`,
`test_flexible_node.py`, where the `.scad` seeded only for the removed
predicate is no longer written.

Unchanged among design.md's 48: `test_manager_test.py`, `test_assert_code.py`
(its double's `scad_code` attribute is what `tests/base.py`'s helper reads)
and `scad_where_read_project/legacy.py`, which is the R7 fixture as it stands.
Outside the 48, changed because the suite proved it: `test_flexible_document.py`
(one of the 58 "unchanged": it patches `as_scad` on a flexible fixture, a
removed attribute, now `present`); `test_assembly_integrity.py` (stand-ins);
`test_cli_lazy_imports.py` (the third column is `'step'`, loaded through the
table); `test_core_kernel_free.py` (the CadQuery template imports `cadquery`
and is listed as a project's file the core never imports; `cli.py` and
`import_step.py` name no kernel module, reaching it through the table);
`test_leaf_contract_version.py`, `test_leaf_contract_exact.py`,
`contract_package/exact_stand_in.py` and `faceted_stand_in.py` (contract 2);
`test_leaf_contract_members.py` (reads this change's delta while it exists,
the synced spec after, and checks a member the spec qualifies with its module,
`StlRenderStart` at `machinome.node.base`, in that module and as an
`autoexception` of the API reference); `test_simulation_sim.py` (2.14).
`tests/test_build_publication.py`'s 2.8 renderer case was corrected after the
first green run: it read `root.scad_file` of an assembly, which no longer
carries one; it reads `writer.scad_file(root)`.

One pytest process over the touched files after groups 4 to 9:

```
18 failed, 1396 passed, 2 skipped, 25 warnings, 689 subtests passed in 203.57s (0:03:23)   (wall 205.2 s)
```

the 18: the API reference not yet documenting the set (group 10, 11
subtests), `test_cli_lazy_imports` and `test_core_kernel_free` (repointed
above), `test_openscad_node`'s viewer-import reader (it read `from
machinome.node.openscad import writer` as the package only; it now reads the
imported names too) and the 2.8 case above. After group 10 and those:

```
147 passed, 5 warnings, 475 subtests passed in 20.65s
```

over the docs, leaf-contract, kernel-free, CLI, gate, table, capability-set,
package and publication files.

## 10. Docs

`docs/architecture.md` (the node model's presentation, the table of supported
node types, the declared set, the OpenSCAD node family as a package, the
binary's address, the writer's publication without coalescing, the sweep by
declaration and the transient rule, adoption, the map's two rows),
`docs/start/install.rst` (SolidPython leaves the plain install; the
`openscad` and `solid2` extras in the table; `machinome new`'s template by
installed extras), `docs/start/first-machine.rst` (the starter part on the
install page's route is a CadQuery part), `docs/howto/backends.rst` (the
extras in the table and the family's section), `docs/reference/cli.rst`
(`new`'s templates and refusal; `snapshot`'s renderer needing
`machinome[openscad]`), `docs/reference/api.rst` (`LeafNode`'s declared set,
`StlRenderStart` and `ArtifactNotProduced`, `ScadLeafNode`, the writer's three
functions, `fn` moved from the node base), `docs/concepts/publishing.rst` (a
`.scad` kept by declaration; a transient file removed by every build),
`docs/project/upgrading.rst` (a section on the extras, the moved members and a
leaf that presented its render as SCAD), `README.rst` (the template by
installed extras). `grep -rn "scad_engine\|machinome.openscad\b\|as_scad"
docs/` outside `docs/adrs/` and the changelog finds nothing. 10.2: the
changelog's Unreleased section gains this cycle's bullet, with its two
breaking notes. The manual builds with warnings as errors, as CI builds it
(`python -m sphinx -b html -W docs <scratch>`): exit 0.

## 11. The plan

`workflow/ongoing/lean-core.md`: the first of the phase's cycles marked in
progress with the evidence pointer and what ratification narrowed; the viewer
cycle recorded as the phase's fourth and last, by the pilot's decision of
4 October 2026; a validation-table row for this cycle, its legs pending.
`openspec validate openscad-out --strict`: `Change 'openscad-out' is valid`.

## 11.1 The whole suite, and the goldens after the change

The three goldens, each in a fresh process, after every source change:

```
leaf_contract_golden       golden comparison: 7 fixtures, 77 values, 0 differences            (4.9 s)
scad_presentation_golden   golden comparison: 34 values, 0 differences, 9 presentation files absent as expected   (3.6 s)
expression_type_golden     golden comparison: 17 values, 0 differences                        (1.4 s)
```

The gate: `modules: 0  occurrences: 0`.

**First whole-suite run** (one process, 18:01 to 12:42, no other run active at
its start):

```
18 failed, 4495 passed, 4 skipped, 55 warnings, 3784 subtests passed in 686.80s (0:11:26)   (wall 689.4 s)
```

The 18, all doubles or a column the earlier touched-file runs did not cover:
`test_manifold_cache.py` (15: `'MeshRaisesIfTouched'` / `'FakeNode'` /
`'_MeshOnly' object has no attribute 'exact'`), `test_persistent_piece_facts.py`
(2: `'CurrentNode' object has no attribute 'declared_markings'`) and
`test_import_step.py` (`AssertionError: 'step' != 'machinome.node.step'`, the
CLI table's third column). Repointed: the three double classes derive from
`tests/stand_in.py`'s `StandIn`; the CLI case expects the node type `'step'`.
Those three files then, one process: `71 passed, 23 subtests passed in 8.01s`.

**Second whole-suite run** (18:14 to 18:25):

```
20 failed, 4493 passed, 4 skipped, 55 warnings, 3784 subtests passed in 689.19s (0:11:29)   (wall 692.1 s)
```

the 18 above gone, and 20 new failures, all in `tests/test_meta.py`, every one
`machinome test printed no summary line`, its subprocess dying at import with
`OSError: [Errno 24] Too many open files` inside trimesh. `test_meta.py` passed
whole in the first run, and nothing it reads changed between the two runs (the
fixes touched three test files). A loop of `machinome test --exact` runs over
`/mnt/data/machinome-projects/3D-Printers/Voron-2` fixtures
(`head_passages`, `revo_spring`, `filament_head`, `filament_grip`), not this
cycle's, started at 18:20:20, during the run: the virtiofs descriptor
exhaustion recorded in the workspace's memory for parallel CAD runs.

`tests/test_meta.py` alone, once the Voron-2 loop had ended and the guard
printed nothing:

```
61 passed in 110.21s (0:01:50)   (wall 110.7 s)
```

So the suite's state at the checkpoint: the second run's 4493 passed, 4
skipped, 3784 subtests, with its 20 failures the 61-test `test_meta.py` that
passes alone and passed in the first run. A third whole-suite run in a window
no other run shares is the orchestrator's to schedule, if wanted.

## Checkpoint (task 11.3)

Groups 1 to 11 applied; nothing committed or staged; the orchestrator's
legs (group 12) and the records, archive and commit (group 13) wait.

## 12. Empirical validation (the orchestrator's legs, folded in, 12.7)

Every leg was run by the orchestrator against the bench at f76aa20 with the
implementation uncommitted, against baselines taken on the line at a16d45a
(code d4eb5c0), one project at a time.

**12.1 `Locks/Pin_tumbler_lock`** (branch `lean-core-validation` e461fba,
fresh build directories). Build: 11 `.scad`, 11 `.stl`, 22 records.
`machinome test --faceted --no-verdict-store`: 24 passed, 0 failed, 2573
verdicts logged, the log byte-identical to the baseline's; after the test 15
`.scad`, their SHA-256 identical before and after. `machinome snapshot
--renderer openscad`: PNG of 35421 bytes, 0 differing pixels of 2073600
against the baseline image; the root `.scad`, captured by a PATH wrapper
before its removal, SHA-256 `d39e88107bd30ce0…` before and after (identical),
and no root `.scad` left in the build directory after the render. The
transient rule: the captured root `.scad` copied back into the build
directory with a record written by `currency.record(path, 'deadbeef',
'cafe', None, transient=True)` (`recorded_transient` True), then `machinome
build` on the unchanged document: the root `.scad` gone, the 15 kept `.scad`
still present. Export (`--set key_delta=0`): 14 files, every non-STL file
identical but `manifest.json`, whose one difference is `/pieces[4]/volume`
137.82648609565126 → 137.8264860956513, OpenSCAD's own STL noise on a
re-rendered STL.

**12.2 `3D-Printers/Prusa3-vanilla`** (master 5138091). Build 135 s, 55
`.scad`, 57 `.stl`, 2 `.brep`, the 55 `.scad` SHA-256 identical before and
after. `machinome test --no-verdict-store`: 16 passed, 3 failed (pre-existing,
the same as before), 15935 verdicts logged, byte-identical to the baseline
log.

**12.3 OpenAstroMount** (`exact-engine-validation` branch, read-only), with
`tests/exact_engine_absent.py`'s finder blocking `solid2`,
`machinome.node.openscad` and `machinome.node.solid2`: build exit 0 in 40 s,
90 STL, 90 BREP, 0 `.scad`; the finder's exit census lists only `OCP`,
`cadquery` and `machinome.occt.engine` for every process, no attempt of the
three blocked names; `machinome test` 8 passed, 1 failed (the known
exact-common wart), as before; `machinome snapshot` with no `--renderer`:
exit 1, standard error

```
Error: machinome snapshot --renderer openscad needs the openscad extra: the openscad node type (OpenScadNode) needs machinome.node.openscad, which is not installed; install it with 'pip install "machinome[openscad]"'; or use --renderer web
```

(R4 with R3 inside it), no image written.

**12.4 The goldens and `machinome new`.** The goldens in fresh processes:
`leaf_contract` "7 fixtures, 77 values, 0 differences"; `scad_presentation`
"34 values, 0 differences, 9 presentation files absent as expected";
`expression_type` "17 values, 0 differences". `machinome new demo` under all
extras: `demo/__init__.py` `e3b0c44298fc1c14…`, `demo/demo.py`
`4feb93ee0da656bf…`, `demo/test_demo.py` `c2ef556500125c74…`, byte-identical
to the same command on the line at a16d45a. With `solid2` blocked: the
CadQuery template (`import cadquery as cq` / `class Demo(CadQueryNode)`),
`machinome build` exit 0 with 1 STL, `machinome test` 2 passed. With `solid2`
and `cadquery` blocked: exit 1, standard error R8 verbatim, nothing created.

**12.5 The universe sweep** (`scripts/load-projects --bench <bench> --moved`
the seven earlier tables and this change's `moved-names.toml`, timeout 300):

```
62 repositories, 129 rows: 117 ok, 4 expected, 2 unexpected, 0 timeout, 6 no-model; 2 skipped
```

identical to the mesh-engine sweep (the 4 expected: Voron-2, the Actuator,
YouCanBuildDog and the Don1 on earlier cycles' names; the 2 unexpected:
wall_clock_41's own CadQuery error and Dum-E without machinome-freecad); no
row cites this change. Its JSON is `load-projects.json` in this change's
directory.

**12.6 Greps over `projects/`** (vendored trees excluded): no project file
names `as_scad`, `scad_code`, `generate_scad`, `scad_file`, `scad_authored`,
`scad_engine`, `machinome.openscad`, `viewers.openscad` or `OPENSCAD_FOV`; a
`fn` declaration outside the family appears only in sandbox projects and on
`Solid2Node` subclasses (Pin_tumbler_lock's `OriginalPart`); SolidPython's
`get_animation_time` is imported only by six probe scripts under `docs/`
(hexapod, Metamaquina2 twice, strandbeest, Thor), besides three
already-stale `machinome.scad_expression` imports in the Pascaline,
CycloidalDrive and cam_hammer probes; machinome-mechanics' main branch has 25
files importing `solid2` (its `v0.8` branch is not checked out; moving its
tests is the plan's follow-up, design.md Open Question 3, not run here).

**The whole suite, clean** (the orchestrator, one process on the bench,
2026-10-04 19:54 to 20:06, no other run active):

```
4513 passed, 4 skipped, 55 warnings, 3784 subtests passed in 749.26s (0:12:29)
```

no "Too many open files" anywhere: the clean run § 11.1 lacked. 4513 against
the line's 4482 at d4eb5c0.

## 13. Records, specs, archive

**ADRs (13.1).** ADR-177 (NODE, the family as a node package and the core
naming no technology; supersedes ADR-171), ADR-178 (NODE, the declared set,
`ArtifactNotProduced`, leaf contract 2) and ADR-179 (BUILD, provisional, the
table of supported node types). Status lines amended: ADR-171 superseded by
177; 172, 173, 086, 046, 103, 102 amended by 177 (103 also by 179); 163 and
165 by 178; 167 and 168 by 179. `docs/adrs/README.md` indexes the three and
records each amendment. `docs/architecture.md`'s map cites them.

**Specs and archive (13.2).** `openspec validate openscad-out --strict`:
`Change 'openscad-out' is valid`. `openspec archive openscad-out --yes`:
"Totals: + 7, ~ 32, - 0, → 0 … Change 'openscad-out' archived as
'2026-10-04-openscad-out'". Then `git rm -r openspec/specs/openscad-engine
openspec/specs/scad-engine-dependency` (design.md Decision 12); no spec under
`openspec/specs/` names either. Purposes written by hand: `kernel-extras`
(its code list: `solid2.py`, the package `machinome/node/openscad/`, the mesh
engine, the table) and the new `openscad-node`. `openspec validate --specs
--strict`: `Totals: 45 passed, 0 failed (45 items)`.

**The moved-names table (13.3)** for the workspace's
`scripts/load-projects.d/openscad-out.toml`:
`openspec/changes/archive/2026-10-04-openscad-out/moved-names.toml` (framework
repository, branch `v0.8-split-openscad-out`). The universe sweep's JSON is
beside it, `load-projects.json`.

**The final suite (13.4)**, one process after the archive, the ADRs and the
spec sync, gated on no other run (20:37 to 20:50):

```
4513 passed, 4 skipped, 55 warnings, 3784 subtests passed in 786.51s (0:13:06)   (wall 789.6 s)
```

no "Too many open files". The completed state is committed on the branch as
one further commit after the planning commit; nothing amended.
