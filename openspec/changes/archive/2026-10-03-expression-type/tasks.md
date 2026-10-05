## 1. Baseline on the unmodified tree

- [x] 1.1 Create `openspec/changes/expression-type/evidence.md` in the shape of
  the archived cycles' (`2026-10-03-lean-install/evidence.md`), with the bench
  commit.
- [x] 1.2 The expression golden: write `tests/expression_type_golden.py`,
  which builds, in a temporary build directory, a fixture assembly whose
  operations carry `self.time` and one driver through `machinome.math` with a
  shared subexpression (so its closed text carries a `let`) and one flexible
  parameter fed from them, and writes `tests/data/expression_type_golden.json`:
  the SHA-256 and length of each operation's `Operation.serialized` text, of
  `scad_code` for the assembly and its children, and of the published
  document (graph values, `bindings`, `version`) as the browser producer
  serializes it. Run it twice in separate processes, record that both agree,
  record the bench commit in the JSON. A characterisation, green before and
  after by design (`--check` after).
- [x] 1.3 Record on the unmodified tree, verbatim, the per-operation call
  counts and timings of design.md's "Cost of the symbolic path today"
  (scratch script outside the bench, none committed): the fourteen native
  rows and the three SolidPython rows; and `import machinome.math` with and
  without `solid2` in `sys.modules`.
- [x] 1.4 Run, on the unmodified tree, `tests/test_math.py`,
  `tests/test_expression_graphs.py`, `tests/test_expressions.py`,
  `tests/test_expression_bindings.py`, `tests/test_graph_value_scalar_dispatch.py`,
  `tests/test_expression_evaluation_order.py`, `tests/test_expression_corpus.py`,
  `tests/test_running_corpus.py`, `tests/test_clocked_corpus.py`,
  `tests/test_driver_ids.py`, `tests/test_couplings.py`,
  `tests/test_openscad_dependency.py`, `tests/test_core_kernel_free.py`,
  `tests/test_exact_engine_seam.py`; record counts and wall time.
- [x] 1.5 Re-run from a scratch script: the path-extension probe for the new
  package (with a scratch `machinome/openscad/__init__.py` in a temporary copy,
  not the bench: `import machinome.openscad.binary` never resolves to the
  primary checkout's `machinome/openscad.py`); record verbatim.

## 2. Red tests

- [x] 2.1 `tests/test_expression_type.py`, the AST rule (design.md Decision
  6): no module under `machinome/` outside `machinome/openscad/` imports from
  `solid2.core.object_base`, or imports `OpenSCADConstant`, `scad_inline`,
  `ScadValue` or `get_animation_time` from a `solid2` module; and the modules
  outside `machinome/openscad/` importing `solid2` at all are exactly
  `node/base.py`, `node/operations.py`, `node/internal.py`, `node/flexible.py`,
  `node/solid2.py`, `node/openscad.py` and
  `manager/templates/project/root/__init__.py`, each with a comment naming
  the cycle that removes it (6, 6, 6, 6, 7, 7, 8). Red: five modules.
- [x] 2.2 Same file: in subprocesses, `import machinome.math` and `import
  machinome.expression_graph` leave no `solid2` module in `sys.modules`. Red
  for `machinome.math`.
- [x] 2.3 Same file, the type: unbound `AssemblyNode.time`, a `DriverToken`
  and `machinome.math.sin(t * 360)` are `GraphValue`s with no `solid2` class
  in their MRO; `bool(t < 1)` raises `SymbolicTruthError`, which is an
  `Exception` and not a `TypeError`; for a 10 000-addition chain its message
  stays under 600 characters and names `machinome.math`; `+t` raises
  `TypeError`; `hash(t)` raises `TypeError`; `iter(t)` raises `TypeError`.
  Red.
- [x] 2.4 `tests/test_scad_engine_seam.py`: `machinome.scad_engine` declares
  `CONTRACT = 1` and `PROVIDER = 'machinome.openscad.engine'`; importing it
  imports neither the provider nor `solid2`; `scad_engine()` returns the
  provider and the same object twice; with `machinome.openscad` blocked (the
  finder of `tests/exact_engine_absent.py`, generalised to a list of modules)
  it is `None`, and with `solid2` blocked it is `None`; with the provider
  *broken* the error propagates; a stub provider declaring `CONTRACT = 2`, and
  one declaring none, raise `ScadEngineIncompatible` naming
  `machinome.openscad.engine` and both versions (or "declares none"), on every
  call. With the engine blocked: a model of native values composes, compiles
  and publishes the golden of 1.2 byte for byte; `machinome.math.sin(
  scad_inline('$t'))` raises the numeric face's `TypeError`; a running law
  returning `scad_inline('$t')` is refused "...which is neither a number nor
  an expression over its sources."; a numeric argument never consults the
  seam (a counting stub). Red (no seam).
- [x] 2.5 `tests/test_openscad_engine.py`: `machinome.openscad` has no
  attribute `adopt`, `CONTRACT` or `require_openscad`;
  `machinome.openscad.engine.CONTRACT == 1`; `adopt(solid2.
  get_animation_time())` is a `name` node `$t`; `adopt(scad_inline('(other +
  2)'))` the parsed binop; `adopt(scad_inline('$mystery ? 1 : 2'))` a `raw`
  node carrying that text; `adopt` of `1.0`, `'x'`, a `GraphValue` and an
  `ExpressionNode` is `None`; `machinome.openscad.binary` imports no `solid2`
  (AST) and `require_openscad` raises `OpenScadUnavailable` with the unchanged
  message when `machinome.openscad.binary.shutil.which` answers `None`. Red.
- [x] 2.6 Rewrite `tests/test_expression_graphs.py::
  test_every_supported_operator_keeps_both_legacy_operand_orders` to the
  delta's scenario "Legacy operand on the left yields SolidPython text the
  framework reads": right-hand legacy → `GraphValue` evaluating `op(a, b)`;
  left-hand legacy → a SolidPython constant whose adoption
  (`machinome.expression_graph.as_node`) evaluates `op(a, b)` with free names
  `{'drive'}`, and which `machinome.math.sin`, a running law and
  `bind_expressions` all accept. Red after the change until rewritten; record
  the old assertion's failure verbatim in the evidence.
- [x] 2.7 `tests/test_expression_faces.py`, the three faces (characterisation,
  green before and after): for every name in `SYMBOLIC_BUILTINS` and every
  composition and vector helper in `machinome.math.__all__`, over sample
  points inside its domain, the numeric face, `GraphValue.evaluate` of the
  symbolic face over the core's own `$t` symbol, and, where the function
  takes a declared argument, the declared face evaluated on a constructed
  instance, agree (bit-identical for primitives, 1e-12 for compositions);
  `sin(90) == 1.0`, `asin(0.5) == 30.0`, `atan2(1, 0) == 90.0`;
  `SYMBOLIC_BUILTINS` equals its 0.7.1 tuple.
- [x] 2.8 `tests/test_expression_type_cost.py` (non-regression pin, green
  before and after): each of the fourteen native call counts of 1.3 at most
  its recorded value; the three SolidPython rows at most 110 % of theirs.
- [x] 2.9 Run 2.1–2.8 on the unmodified tree; record each red with its first
  failing line, and each characterisation green.

## 3. The type

- [x] 3.1 Move `GraphValue`, `as_node`, `call`, `symbol`,
  `get_animation_time`, `depends_on_time`, `scalar` and `restore_scalar` into
  `machinome/expression_graph.py`; `GraphValue` subclasses `object`; define
  `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__mod__`, `__pow__` and
  `__neg__` on it (the reflected ones, comparisons, `__abs__`, `__float__`,
  `evaluate`, `value`, `__str__`, `__repr__` verbatim); drop `_render`.
- [x] 3.2 `SymbolicTruthError(Exception)` and `GraphValue.__bool__` raising it
  with the bounded description and remedy of design.md Decision 2.
- [x] 3.3 `symbolic(value)`: `GraphValue` → its node, `ExpressionNode` →
  itself, `int`/`float` (not `bool`) → `None`, else the engine's `adopt` via
  `machinome.scad_engine.scad_engine()`, else `None`; `as_node` keeps its
  contract on top of it; `depends_on_time` and `scalar` use it;
  `restore_scalar`'s unparseable fallback becomes `GraphValue(ExpressionNode(
  'raw', text=value))`.
- [x] 3.4 Delete `machinome/scad_expression.py`; update the module docstring
  of `expression_graph.py` (the value, its graph, no backend; SolidPython
  values are adopted by the OpenSCAD engine).

## 4. The engine and the seam

- [x] 4.1 `machinome/openscad/__init__.py` (docstring only, the
  `machinome/occt/__init__.py` shape); move `machinome/openscad.py` to
  `machinome/openscad/binary.py` unchanged (`git mv`).
- [x] 4.2 `machinome/openscad/engine.py`: `CONTRACT = 1`; `adopt(value)` as
  the `openscad-engine` delta states, parsing through
  `machinome.core.expressions.parse`.
- [x] 4.3 `machinome/scad_engine.py`: `CONTRACT`, `PROVIDER`,
  `ScadEngineIncompatible`, `scad_engine()` of `exact_engine.exact_engine`'s
  shape with the absence rule of design.md Decision 4 (including `solid2`).

## 5. Callers

- [x] 5.1 `machinome/math.py`: import from `machinome.expression_graph`;
  `_is_symbolic` through `symbolic`; the module docstring's symbolic face
  rewritten (native shared graphs, the core's own type; SolidPython values
  adopted by the OpenSCAD engine) and the comment at "four clock models never
  needed to import solid2's private OpenSCADConstant" kept as history.
- [x] 5.2 `simulation/clocked.py`, `simulation/program.py` (four sites),
  `simulation/profile.py`: drop the `OpenSCADConstant` import; each
  recognition site calls `symbolic` (or `as_node` after it), wording of every
  refusal unchanged.
- [x] 5.3 Import lines from `machinome.scad_expression` →
  `machinome.expression_graph`: `node/operations.py`, `node/flexible.py`,
  `node/qualified.py`, `node/assembly.py`, `node/solid2.py`,
  `core/serializer.py`.
- [x] 5.4 Import lines from `machinome.openscad` →
  `machinome.openscad.binary`: `node/base.py`, `node/solid2.py`,
  `viewers/openscad.py`, `manager/snapshot.py`.
- [x] 5.5 Docstrings and comments that call time or a driver "solid2's `$t`"
  or describe the facade as subclassing `OpenSCADConstant`:
  `node/qualified.py` (module and `DriverToken`), `node/assembly.py`
  (`clear_keyframe`, `time`), `motion/ports.py`, `motion/couplings.py`
  (`Affine`), `node/flexible.py`, `node/operations.py` (`_as_number`,
  `matrix`).

## 6. Existing tests

- [x] 6.1 Repoint imports from `machinome.scad_expression` to
  `machinome.expression_graph` (18 test files, grep), and patches of
  `machinome.openscad.shutil.which` / `machinome.openscad.openscad_binary` to
  `machinome.openscad.binary.*` (`test_openscad_dependency.py`,
  `test_no_class_name_recognition.py`, `test_stl_node.py`,
  `test_sheet_leaf.py`, `test_step_node.py`, `test_manager_develop.py`).
- [x] 6.2 `tests/test_math.py`: the symbolic-mode tests use the core's own
  `$t` (`machinome.expression_graph.get_animation_time`) and assert
  `GraphValue`; the cases that test SolidPython's `$t` stay, as legacy
  adoption, asserting what the delta states.
- [x] 6.3 `tests/test_expression_graphs.py::
  test_legacy_operand_order_and_public_math`: assert `GraphValue` for a
  framework-left result and SolidPython text for a legacy-left one, with the
  same `str()` texts; `bool(x < legacy)` still raises.
- [x] 6.4 `tests/test_expressions.py`, `tests/test_driver_ids.py`,
  `tests/test_couplings.py`, `tests/clocked_project/unsupported.py`: keep their
  SolidPython operands (they are the legacy surface); adjust only an assertion
  of `OpenSCADConstant` type on a framework value, each recorded in the
  evidence with its reason.

## 7. Characterisations and the suite

- [x] 7.1 `tests/expression_type_golden.py --check` and the exact-engine,
  leaf-contract and markings goldens `--check`: green.
- [x] 7.2 2.1–2.8 green; record each.
- [x] 7.3 The framework suite, once, alone (never two suites at once); record
  counts against 1.4's and the previous cycle's.
- [x] 7.4 The call counts and timings of 1.3 again; record both tables side
  by side.

## 8. Documentation and the plan

- [x] 8.1 `docs/architecture.md`: the schema-4 paragraph's sentence naming
  `machinome/scad_expression.py` as "the SolidPython compatibility facade"
  (the value now lives in `expression_graph.py`; SolidPython values are
  adopted by `machinome.openscad.engine` through `machinome.scad_engine`), and
  the source map's rows.
- [x] 8.2 `docs/project/changelog.rst`, under Unreleased, the bullet:

  > **Symbolic values are machinome's own:** animation time, driver reads
  > and what ``machinome.math`` returns for them are
  > ``machinome.expression_graph.GraphValue``, a type the core defines; they
  > no longer derive from SolidPython's ``OpenSCADConstant``, and importing
  > ``machinome.math`` no longer imports SolidPython. Arithmetic,
  > comparisons, degree math and their text are unchanged, and so is every
  > SCAD file and published document, byte for byte. SolidPython's own
  > values (``solid2.get_animation_time()``, ``scad_inline(...)``) are still
  > accepted by ``machinome.math``, laws and bounds, read by the OpenSCAD
  > engine, now the package ``machinome.openscad``; with a SolidPython value
  > on the LEFT of an operator, SolidPython builds the result as its own
  > text, which machinome reads back wherever it is used. Asking a symbolic
  > value for its truth raises ``SymbolicTruthError`` naming it, where
  > SolidPython raised a bare ``Exception``. Breaking:
  > ``machinome.scad_expression`` is removed and its names
  > (``get_animation_time``, ``GraphValue``, ...) are imported from
  > ``machinome.expression_graph``; the OpenSCAD binary helpers
  > ``require_openscad``, ``openscad_binary`` and ``OpenScadUnavailable``
  > are imported from ``machinome.openscad.binary`` (ADR-170, ADR-171).

- [x] 8.3 `workflow/ongoing/lean-core.md`: the "Empirical validation" table
  gains the row for `expression-type` (Locks/Pin_tumbler_lock, why, the
  result in one sentence, the evidence path); "Import paths"' table gains the
  OpenSCAD engine, `machinome.openscad` (`machinome.openscad.engine` the
  provider of the seam `machinome.scad_engine`, `machinome.openscad.binary`
  the binary contract), install `machinome[openscad]` (declared by cycle 7),
  distribution machinome-openscad; "Where the core reaches each kernel"
  gains that solid2 is no longer the core's expression type (this change),
  and the "Layers" item 5 is marked done with its ADRs and evidence path.

## 9. Stop and report (the applier)

- [x] 9.1 With 1 to 8 done and the suite green, stop before any commit and
  report to the orchestrator: the diff stat, the red and green results, the
  suite's counts, the cost tables. The applier spawns no agent and runs
  neither validation below.

## 10. Empirical validation (the orchestrator)

- [x] 10.1 **Deep, Locks/Pin_tumbler_lock,** by a validator subagent the
  orchestrator briefs and launches, once per leg, from design.md Decision 8:
  - *Where.* `/home/asa/devel/machinome/projects/Locks/Pin_tumbler_lock`
    (`main`, e461fba, clean on 3 October 2026): a branch
    `lean-core-validation` from `main` in a worktree under the project's own
    `WTs/`; never merged, never pushed. Everything with `PYTHONPATH=<bench>`
    and the workspace venv, from the worktree.
  - *Legs.* Before: after the planning commit, before the applier starts.
    After: after 9.1, the change uncommitted in the bench. Each leg:
    `machinome build`; `machinome test --faceted`; `machinome export --set
    key_delta=0 -o <scratch>/<leg>`; the SHA-256 of `manifest.json` and of
    every `.scad` under `_build/`; and, timed by a scratch script,
    `program_of(PinTumblerLock())`. Expected before: green. Expected after:
    green with the same counts, `manifest.json` and every `.scad`
    byte-identical (if `manifest.json` differs, report the diff, with and
    without `mtime` keys, and stop); timings within 5 %.
  - *Migration.* None expected: the project imports no moved name. If
    anything must change, stop and report.
  - *Must not change:* anything in the bench or the framework; any project
    file.
- [x] 10.2 **Clocked probe, the Curta,** by the same validator or the
  orchestrator, read-only in
  `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x`
  (`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=<bench>:<project>`):
  `EventDrivenCurta()`, `compiled_clocked`, `clocked_block`, `json.dumps(...,
  default=str, sort_keys=True)`; record its length and SHA-256 before and
  after. Expected: 88 910 bytes, prefix `be1e37234b443566`, both legs.
- [x] 10.3 **Cross-package probe, machinome-mechanics,** its suite with
  `PYTHONPATH=<bench>` from `/home/asa/devel/machinome/machinome-mechanics`,
  before and after; expected the same counts.
- [x] 10.4 **Shallow, the universe,** run by the orchestrator from the
  workspace root: `scripts/load-projects --bench <bench> --moved
  scripts/load-projects.d/exact-engine.toml
  scripts/load-projects.d/leaf-contract.toml
  scripts/load-projects.d/backend-switch.toml
  scripts/load-projects.d/lean-install.toml
  <bench>/openspec/changes/expression-type/moved-names.toml --timeout 300
  --json <bench>/openspec/changes/expression-type/load-projects.json`.
  Expected: no row for this cycle (its importers are probes, not roots);
  carried: `3D-Printers/Voron-2`, `Actuators/Internal-Cycloidal-Actuator`,
  `Robots/YouCanBuildDog`, `Robots/openvmp` (`don1`) `expected`;
  `3DPrintedClocks` `wall_clock_41` and `Robotic-Arms/Dum-E` `unexpected`,
  pre-existing; six `no-model`. Any other row returns to the orchestrator
  with its output before integration.
- [x] 10.5 A failed validation returns to the orchestrator with the project's
  output; nothing is fixed in a project. The orchestrator hands the reports to
  the paused applier.

## 11. Records, ADRs, specs, commit (the applier, after 10)

- [x] 11.1 Fold 10.1–10.4 into the evidence, verbatim where they quote a
  message, a hash or a summary line.
- [x] 11.2 Write ADR-170 (`docs/adrs/MATH/`, the core's symbolic value is its
  own type: `GraphValue` at `machinome.expression_graph`, no SolidPython
  ancestry, `SymbolicTruthError`, text unchanged; amends ADR-101's facade
  decision and ADR-056's `DriverToken` representation clause, which gain
  status lines and amendment sections; cites 022, 080) and ADR-171
  (`docs/adrs/NODE/`, the OpenSCAD engine is `machinome.openscad`, reached for
  expressions through the seam `machinome.scad_engine`; SolidPython values are
  adopted there; the binary locator's address; amends ADR-046's module
  location; cites 161, 162); list them in `docs/adrs/README.md`.
- [x] 11.3 Sync the delta specs into `openspec/specs/` (the new
  `scad-engine-dependency` and `openscad-engine`; the
  `motion-expression-sharing` delta); run `openspec validate --specs
  --strict`; archive the change with its `moved-names.toml` and
  `load-projects.json`.
- [x] 11.4 Make the one implementation commit on `v0.8-expression-type`. The
  copy of `moved-names.toml` to the workspace's
  `scripts/load-projects.d/expression-type.toml` is the orchestrator's,
  outside the framework.
