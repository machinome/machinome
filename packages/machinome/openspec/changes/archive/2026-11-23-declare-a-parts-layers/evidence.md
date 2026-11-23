# Evidence: declare-a-parts-layers

Applied on the bench `machinome/WTs/layers`, branch `layers`, above the planning commit `2d81792d` (base `cc2e661a`). The companion `show-only-a-layer` was already implemented in the worktree (viewer API 32, bundle rebuilt) when this was applied, so X1 ran.

## Red on the base (task 2.3)

`tests/test_layers.py` alone on the framework source as it stood (no `machinome/layers.py`): `29 failed, 1 passed`. The one pass is P5 (the pin). Every other test fails with `ModuleNotFoundError: No module named 'machinome.layers'`, because every fixture module but `untagged.py` imports it and F1 imports it directly.

Departure from the design's "P6 green on the base": P6 compares `machine.py:Layered` with `untagged.py:Layered`, and `machine.py` cannot be imported on the base, so P6 is red there for that reason, not green.

Because the module's absence is a weak reason for F2, F3 and P1-P4, the red was repeated at two later stages, each for the design's own reason:

- After task 3.1 only (`Layer` present, no declaration check, no serializer change): `32 failed, 6 passed, 10 subtests passed`. F2 `layers = 'electrical'`, `[LAYER]`, `()`, `(LAYER, 'x')`, `3`, `None`, a set and a child instance are each reported as a failing subtest, `AssertionError: TypeError not raised` (accepted today); F2 repeated-layer, F3 (`AttributeError: ... no attribute '_declared_layers'`), P1-P7 and X1 still red. (pytest lists a test with failing subtests as PASSED in the `-rA` summary line and as SUBFAILED in the body; the totals above count them.)
- After task 3.2 (declaration done, serializer not): `15 failed, 15 passed`; the 15 failures are P1-P4, P6, P7 and X1, with `KeyError: 'layers'` (the document carries no field), `ValueError not raised` (P3 published) and `TypeError not raised` (P4 published).

## The pin (task 2.2)

`tests/layers_project/untagged.py:Layered`, built with `Builder(path, build_dir=..., watch=False)` in a temporary copy of the fixture project on the unchanged base source, before `serializer.py`, `declarative.py` or `base.py` were touched; `viewer.json` of 3,581 bytes; each `"mtime": <seconds>` written `"mtime": 0` (a file's modification time is a property of the checkout):

    c9ea090d4ecf846a1cabd862b867a2dab3b81913bef624db435da4cc32cec267

(the raw bytes: `d33a9b7737d8e9c42862dcafd0d5491c4b7dfef9f0f5c6a33c468482d3b32757`, equal across two builds in two directories). `UNTAGGED_SHA256` in `tests/test_layers.py` holds the normalized digest; P5 passes on the finished source.

## Green (tasks 3 and 4)

- `tests/test_layers.py`: `30 passed, 18 subtests passed`, no skip, X1 ran (Chromium, the viewer's JavaScript toolchain and OpenSCAD present).
- Tests that read the node metaclass, alone: `test_declarative_nodes.py` 94 passed (4 warnings), `test_markings.py` 109, `test_leaf_contract_reach.py` 5, `test_lazy_test_framework.py` 36.
- The existing pins and producers, each file alone: `test_running_document` 110, `test_clocked_document` 72, `test_flexible_document` 20, `test_document_drivers` 22, `test_state_color` 16, `test_model_app` 27 (including its P4 pin and the browser pages), `test_mates` 137, `test_export` 30, `test_build_publication` 13, `test_builder_lifecycle` 35, `test_expression_bindings` 22, `test_persistent_piece_facts` 17, `test_source_generation` 14, and every other file a search for `serialize_node`, `document_body`, `export_node` and `_write_viewer_snapshot` names: all pass. The golden documents (`tests/base_documents/`, `markings_golden.py`) pass unchanged through their tests.
- The whole framework suite, every `tests/test_*.py` once, file by file: 245 files; every file passes except `test_profile_documentation.py` (1 failed, the known base red on "current source" in `docs/project/status.rst`) and `test_math.py` (3 failed in `LegacySolidPythonTimeTest`, `TypeError: must be real number, not ScadValue`), which fails identically on a copy of the base source (`git archive cc2e661a`), so it is not this change's. Skips, all existing: `test_connectivity` 1, `test_freecad_*` 4 files, `test_jscad_integration` 1, `test_step_assembly` 2, `test_web_viewer_capture` 1.

Task 4.2 first run found 21 failures in four files (`test_builder_lifecycle` 17, `test_expression_bindings` 1, `test_persistent_piece_facts` 2, `test_source_generation` 1): `AttributeError: type object 'NodeDouble' has no attribute '_declared_layers'`. The suite's node doubles do not derive from the node base; the design (Decision 2) says they read the empty tuple directly, so `tests/stand_in.py`'s `StandIn` gained `_declared_layers = ()` and its docstring one clause. All four files then pass.

## Timings (task 4.3)

`machinome build <reference>` run in a temporary copy of the fixture project (a process per run, the parts current: one unmeasured cold run, then three), seconds:

| model | cold | three warm runs | median |
| --- | --- | --- | --- |
| `machine.py:Layered` (tagged, with its app) | 1.66 | 1.542, 1.554, 1.538 | 1.542 |
| `machine.py:Bare` (tagged, no app) | 1.25 | 1.339, 1.219, 1.181 | 1.219 |
| `untagged.py:Layered` (untagged, no app) | 1.49 | 1.333, 1.270, 1.262 | 1.270 |

(An earlier set of three-run medians, tagged-with-app 1.406 and untagged 1.239, agrees within the spread. The tagged-with-app cost is the app's bundling; the tagged build without an app, 1.22, is not slower than the untagged, 1.27, within the 0.15 s spread.) `_publish_layers` alone on a synthetic tree of 4,000 node entries, a quarter of them tagged: 0.970, 0.901, 0.901 ms, median 0.901 ms.

## X1 (task 4.4)

Ran and passed: the fixture `Layered` exported with its app into a temporary directory, served on an ephemeral port, opened in headless Chromium with the arguments of `Capture.launch`; three buttons (`Whole machine`, `Electrical path`, `Rotor stepping`); after "Electrical path", `partOnScreen` is null for `case` and `lever` and not null for `circuit/wire` and `key`, and `navigation().layer` is the electrical layer; after "Whole machine" `case` and `lever` are on screen and `navigation().layer` is null. The server and the browser are stopped in `finally`. The export page's own `index.html` keeps no handle, so the test adds a `harness.html` beside the manifest that mounts the manifest through the same bundle (which starts the model's app) and keeps the handle on `window`, as the viewer's own browser tests do.

## The tests bite (task 5.1)

Each mutation applied alone to the source, the named tests run, the file restored and compared byte-equal (`cmp`) with the copy taken before:

| mutation | file | tests run | result |
| --- | --- | --- | --- |
| form check removed (`raise` replaced by `return (value,)`) | `node/declarative.py` | F2 | red: 10 failed (the eight forms, the parameter, the quoted sentence) |
| collection reads only the class's own `__dict__` | `node/declarative.py` | F3 | red: 2 failed (inherited and mixin layers; the mixin refusal) |
| `layers` read off the instance, refusal removed | `core/serializer.py` | P4 | red: 1 failed |
| node entry carries effective keys | `core/serializer.py` | P1 | red: 1 failed (declared-keys test) |
| conflict compares key and label instead of objects | `core/serializer.py` | P3 | red: 1 failed (the second layer with an equal label) |
| empty table written as `[]` | `core/serializer.py` | P5 | red: 1 failed (the pin) |
| table gathered at the build's call site instead of `document_body` | `core/serializer.py`, `core/builder.py` | P7 | red: 2 failed (the export, the capture staging) |

No mutation turned nothing red. P3's twin-label case exists because the fifth mutation needed it.

## The documentation tests (task 6.1)

`test_docs_structure` 39 passed (6,597 subtests), `test_docs_exports` 22, `test_manual_extras` 16, `test_viewer_documentation_links` 15, `test_release_records` 21; all alone. `test_docs_structure` first failed on the new page (`a teaching page does not declare an extra its code needs`: its snippet imports `machinome.node.solid2`), see the departures. The strict manual build `python -m sphinx -b html -n -W --keep-going docs <dir>` could not run with the theme named in `docs/conf.py` (`sphinx_rtd_theme` is not installed in the bench's venv); with `-D html_theme=alabaster` it builds clean, no warning, `howto/show-a-layer.html` written. `test_profile_documentation.py::test_released_status_changelog_and_history` is red on the base ("current source" in `docs/project/status.rst`) and is not touched.

## The Studio skill (task 6.3)

`machinome/studio/shop-skills/machinome-api/SKILL.md` gained a "Layers" paragraph after the app's, before the viewer panel paragraph; nothing else in the Studio changed. Run alone from `packages/machinome-studio`: `test_scoped_tools` 23 passed, `test_runtime_profiles` 14, `test_state_color_contract` 1, `test_frame_precision_contract` 1, `test_documentation` 23.

## Departures from the design

1. `show-a-layer.rst` declares `.. needs:: viewer, solid2`, not `viewer`: the manual's structure test derives `solid2` from the declaration snippet's `machinome.node.solid2` import. A routine detail.
2. `tests/stand_in.py` changed (`StandIn._declared_layers = ()`), against task 2.1's "nothing else under `tests/` changes": the design's own rule that doubles read the attribute directly requires it.
3. `Bare` exists in `tests/layers_project/machine.py`: `Layered` is `Bare` plus `app = 'app/index.tsx'`. The build and capture tests (P7) need a tagged model that bundles no app, so that they run without the viewer's toolchain; the design's fixture list is otherwise unchanged. `conflict.py` also holds `Twinned` (an equal-label second layer, for the fifth mutation), `Separate` and `Elsewhere` (two machines, one key each); `inherit.py` holds `Plain` and `Mixed`.
4. P6 is red, not green, on the base (above); P6 also normalizes the module-derived artifact names, the file modification time and the clocked machine's `identity` (a hash that names the root class's module) before comparing, since `machine.py` and `untagged.py` are different modules.
5. The refusal sentence for a plain mixin reads `Contact inherits layers = 'x' from Copper. On a node class ...` (the design's "…" elided; the full form sentence follows a full stop, as for the class's own value). A layer repeated in a mixin's tuple is refused as `Contact (layers inherited from Copper) names ... twice`.
6. The strict manual build ran with `alabaster` in place of the unavailable theme (above).

## Reviewer's planted faults

Ten faults planted by the reviewer, nine caught, the tenth (a node's keys
sorted in `_publish_layers` instead of kept in declaration order) closed by
`test_p1_a_node_s_keys_are_in_the_order_its_classes_declare_them`, whose
fixture `tests/layers_project/order.py` declares against alphabetical order.
Red with the fault applied, green on the restored source (`cmp` equal).
