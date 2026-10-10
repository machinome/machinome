# Evidence — `expression-type`

The fifth cycle of layer 1 of the lean-core campaign
(`workflow/ongoing/lean-core.md`, "Layers (pilot, 3 October 2026)", item 5).
Worktree `machinome/WTs/v0.8-expression-type`, branch `v0.8-expression-type`,
cut from `v0.8` at edff84e. Planning commit 2c9d65f. Every command below ran
from inside the worktree with `PYTHONPATH=<worktree>` and the workspace venv
(solidpython2 2.1.3, Python 3.12.3); `machinome.__file__` resolved to
`<worktree>/machinome/__init__.py` and `machinome.openscad.__file__` to
`<worktree>/machinome/openscad.py` before the change (checked once,
`env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -c 'import
machinome, machinome.openscad; ...'`). Pytest ran one process at a time,
never in parallel.

## 1. Baseline on the unmodified tree (2c9d65f)

### 1.2 The expression golden

`tests/expression_type_golden.py` (new, not collected) builds, under a
temporary `SOLID_BUILD_DIR`, `SharedMotion` of the new fixture package
`tests/expression_type_project/machine.py`: one driver `drive` and animation
time composed once through `machinome.math` (`phase = sin($t * 360 + drive)`,
`swing = clamp(phase * phase, 0, 1)`) and read in four places -- a rotation
of `arm`, two components of a translation of `slider`, and, through
`connect`, the `height` port of a molejo `Coil`, so a flexible parameter
carries an expression. Read in symbolic driver mode (`symbolic_document`),
the operations' closed text carries a `let`:

```
arm    ['r', 'let(_s0 = ($t * 360), _s1 = (_s0 + drive), _s2 = sin(_s1)) ((min(max((_s2 * _s2), 0), 1) * 45) + _s2)', [0, 0, 1]]
slider ['t', ['let(_s0 = ($t * 360), _s1 = (_s0 + drive), _s2 = sin(_s1)) (cos(drive) * min(max((_s2 * _s2), 0), 1))', 'let(...) (min(max((_s2 * _s2), 0), 1) + 1)', '0']]
```

It records the SHA-256 and length of each operation's `serialized` form (as
JSON), of `scad_code` for the assembly and its three children in the same
mode, and of the document `export_node(..., widget=False)` writes
(`manifest.json`, sorted-key JSON without every `mtime` and the `source`
field, which name the checkout and not the model), with its `bindings`
table's digest and its `version` (4): 17 values. Run twice in separate
processes into the scratchpad, the two JSON files were byte-identical
(`cmp`), then written to `tests/data/expression_type_golden.json` (bench
commit 2c9d65f). `--check` on the unmodified tree:

```
golden comparison: 17 values, 0 differences
```

### 1.3 The cost of the symbolic path, before

A scratch script in the session scratchpad (not committed): `t` is the
unbound `SharedMotion().time`; each operation runs twice as a warm-up, then
once under `sys.setprofile`, counting `call` and `c_call` events; timings are
the best of five `timeit` repeats of 200 000. The SolidPython operand `L` is
`scad_inline('($t * 2)')`, the shape that reproduces design.md's 125/135
(`scad_inline('L')` gives 50/50/60, `scad_inline('sin($t)')` 102/102/112);
`solid2.get_animation_time()`, a `ScadValue`, is recorded beside it:

```
type(t) <class 'machinome.scad_expression.GraphValue'> ['machinome.scad_expression.GraphValue', 'solid2.core.object_base.object_base_impl.OpenSCADConstant', 'builtins.object']
t+1          calls   11
1+t          calls   11
t*t          calls    8
t-t          calls    8
t/2          calls   11
t%2          calls   11
t**2         calls   11
-t           calls    6
abs(t)       calls   11
t<1          calls   11
sin(t)       calls   18
atan2(t,1)   calls   28
min(t,1)     calls   28
clamp01(t)   calls   56
solid2.get_animation_time()    t+L      calls   50  -> GraphValue
solid2.get_animation_time()    L+t      calls   59  -> OpenSCADConstant
solid2.get_animation_time()    sin(L)   calls   60  -> GraphValue
scad_inline('($t * 2)')        t+L      calls  125  -> GraphValue
scad_inline('($t * 2)')        L+t      calls  125  -> GraphValue
scad_inline('($t * 2)')        sin(L)   calls  135  -> GraphValue
time t+1          1.52 us
time 1+t          1.53 us
time t*t          0.76 us
time -t           0.69 us
time sin(t)       1.50 us
time clamp01(t)   5.35 us
```

One fact the table adds to design.md's "What the facade is" (3):
`solid2.get_animation_time()` is a `ScadValue`, a subclass of
`OpenSCADConstant` that `GraphValue` does not subclass, so `L + t` with it on
the left already returns SolidPython's own `OpenSCADConstant` on the
unmodified tree; reflected priority held only for a plain `OpenSCADConstant`
(`scad_inline`).

Importing the vocabulary, in a fresh interpreter, median of five:

```
import machinome.math              28.8 ms   solid2 in sys.modules afterwards: True
import machinome.math              5.7 ms    (solid2 imported first)
import machinome.expression_graph  13.3 ms   solid2 in sys.modules afterwards: False
import machinome.expression_graph  3.9 ms    (solid2 imported first)
```

### 1.4 The files the change touches or relies on

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_math.py tests/test_expression_graphs.py tests/test_expressions.py \
  tests/test_expression_bindings.py tests/test_graph_value_scalar_dispatch.py \
  tests/test_expression_evaluation_order.py tests/test_expression_corpus.py \
  tests/test_running_corpus.py tests/test_clocked_corpus.py tests/test_driver_ids.py \
  tests/test_couplings.py tests/test_openscad_dependency.py tests/test_core_kernel_free.py \
  tests/test_exact_engine_seam.py
426 passed, 11 warnings, 478 subtests passed in 19.46s
wall time 20.9 s
```

### 1.5 The path extension, re-probed

A copy of the bench's `machinome/` in the scratchpad with `openscad.py` and
`scad_expression.py` removed and a scratch `machinome/openscad/__init__.py`
(a docstring), run with only that copy on `PYTHONPATH` (the venv's editable
install still puts the primary checkout on `sys.path`):

```
sys.path has primary: True
machinome.__path__ ['<scratch>/pathprobe/machinome']
machinome.openscad -> <scratch>/pathprobe/machinome/openscad/__init__.py
import machinome.openscad.binary -> ModuleNotFoundError: No module named 'machinome.openscad.binary'
from machinome.openscad import require_openscad -> ImportError: cannot import name 'require_openscad' from 'machinome.openscad' (<scratch>/pathprobe/machinome/openscad/__init__.py)
import machinome.scad_expression -> ModuleNotFoundError: No module named 'machinome.scad_expression'
```

Neither the primary checkout's `machinome/openscad.py` nor its
`machinome/scad_expression.py` resolves (both exist there): the
`lean-install` filter admits no portion carrying its own `__init__.py`, as
design.md Decision 4 inferred.

## 2. Red first (task 2.9)

The tests of tasks 2.1 to 2.8 were written before any source change and run
on the unmodified source (2c9d65f plus the tests), in one pytest process:

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider -rfEp \
  tests/test_expression_type.py tests/test_scad_engine_seam.py tests/test_openscad_engine.py \
  "tests/test_expression_graphs.py::ExpressionGraphTest::test_every_supported_operator_keeps_both_legacy_operand_orders" \
  tests/test_expression_faces.py tests/test_expression_type_cost.py
33 failed, 10 passed, 178 subtests passed in 6.67s
```

(Counts include subtests: three subtests of
`test_the_package_itself_exports_nothing` are red.) What the new and changed
files hold:

- `tests/test_expression_type.py` (new; 2.1-2.3): `NoExpressionImportTest`,
  three AST rules over every module under `machinome/` outside
  `machinome/openscad/` (no SolidPython expression name; the remaining
  `solid2` importers are exactly the seven, each with the cycle that removes
  it; the modules reaching the engine's package directly are exactly the
  seam and the four binary-locator importers of design.md Decision 4);
  `ImportsNoSolidPythonTest`, two fresh interpreters; `TheTypeTest`, five
  tests of the type.
- `tests/test_scad_engine_seam.py` (new; 2.4): the declaration, the
  provider resolving once, the provider absent (`sys.modules`), the engine
  package absent and `solid2` absent (subprocesses under
  `tests/exact_engine_absent.py`'s finder, whose `absent=` already takes a
  list since `lean-install`), a broken provider (an `ImportError`, and a
  `ModuleNotFoundError` for another module), contract 2 and none (each
  twice: not cached); with `machinome.openscad.engine` blocked, the golden
  of 1.2 compared in that interpreter, and a SolidPython value through
  `machinome.math.sin` and a running law; a counting stub around the seam.
- `tests/test_openscad_engine.py` (new; 2.5).
- `tests/test_expression_graphs.py` (2.6):
  `test_every_supported_operator_keeps_both_legacy_operand_orders` rewritten
  to the delta's scenario: the legacy operand on the right gives a
  `GraphValue` evaluating `op(3, 2)`; on the left, a SolidPython constant
  whose adoption (`machinome.expression_graph.as_node`) evaluates `op(2, 3)`
  with free names `{'drive'}`, which `machinome.math.sin` takes as a
  `GraphValue` over `drive` and `bind_expressions` publishes without a
  warning or a `let`; and `Sim(LegacyLeft(), 0.1)` compiles the law
  `(2 * crank)`. The old test is kept in the scratchpad to record its
  failure after the change (section 3).
- `tests/expression_type_project/running.py` (new): `LegacyLeft` and
  `LegacyTime`, running roots whose laws return SolidPython's values when
  applied to a token (and a number at rest: a running root's rest render
  applies the law to numbers, and a SolidPython text constant there leaves
  the coordinate unbound, on the unmodified tree as after).
- `tests/test_expression_faces.py` (new; 2.7) and
  `tests/test_expression_type_cost.py` (new; 2.8): characterisations.

Each red test and its reason:

| task | test | red because |
|---|---|---|
| 2.1 | `test_no_core_module_imports_a_solidpython_expression_name` | `{'machinome/math.py', 'machinome/scad_expression.py', 'machinome/simulation/clocked.py', 'machinome/simulation/profile.py', 'machinome/simulation/program.py'}` each import `OpenSCADConstant` from `solid2.core.object_base` |
| 2.1 | `test_the_remaining_solid2_importers_are_presentation_leaves_and_template` | "Items in the first set but not the second": the same five |
| 2.1 | `test_the_binary_locator_is_reached_directly_only_by_presentation_and_runner` | "Items in the second set but not the first: 'machinome/scad_engine.py'" (no seam) |
| 2.2 | `test_importing_the_vocabulary_imports_no_solidpython` | `"['solid2', 'solid2.config', 'solid2.core[790 chars]es']" != '[]'` |
| 2.3 | `TheTypeTest` x 5 | `ImportError: cannot import name 'GraphValue' from 'machinome.expression_graph'` |
| 2.4 | every test of `test_scad_engine_seam.py` but one (13) | `ModuleNotFoundError: No module named 'machinome.scad_engine'` (in-process and in the subprocesses); the counting stub's test `ImportError: cannot import name 'as_node' from 'machinome.expression_graph'` |
| 2.5 | `test_the_package_itself_exports_nothing` (3 subtests) | `require_openscad`, `openscad_binary`, `OpenScadUnavailable`: `True is not false` (the module `machinome/openscad.py` defines them) |
| 2.5 | `AdoptTest` x 4, `test_the_provider_declares_contract_version_one`, `test_the_binary_contract_refuses_unchanged` | `ModuleNotFoundError: No module named 'machinome.openscad.engine'; 'machinome.openscad' is not a package` (`.binary` for the last) |
| 2.5 | `test_the_binary_module_imports_no_solidpython` | `FileNotFoundError: ... machinome/openscad/binary.py` |
| 2.6 | `test_every_supported_operator_keeps_both_legacy_operand_orders` | `ImportError: cannot import name 'GraphValue' from 'machinome.expression_graph'`; past the import its left-hand `assertNotIsInstance(value, GraphValue)` fails on this tree (reflected priority returns a `GraphValue`) |

Green before, as characterisations by design:
`test_importing_the_expression_graph_imports_no_solidpython` (it imports none
today); `test_native_values_compose_and_publish_the_golden` (with a module that
does not exist blocked, the golden reproduces: `17 values, 0 differences`);
`ThreeFacesTest` x 5 (159 subtests); `CallCountTest` x 2 (17 subtests, every
count equal to its ceiling).

Departure in a characterisation: task 2.7 states `asin(0.5) == 30.0`; in IEEE
doubles `degrees(asin(0.5))` is `30.000000000000004`, in the numeric face as in
Python's own `math`, so `test_degree_conventions` asserts it to 1e-12 and
asserts equality with `math.degrees(math.asin(0.5))`. `sin(90) == 1.0` and
`atan2(1, 0) == 90.0` hold exactly.

## 3. The change (groups 3 to 6)

### 3.1 The type, the engine, the seam

- `machinome/expression_graph.py` holds `GraphValue` (subclassing `object`),
  `SymbolicTruthError(Exception)`, `symbolic`, `as_node`, `call`, `symbol`,
  `get_animation_time`, `depends_on_time`, `scalar` and `restore_scalar`.
  Each of the eighteen binary operators and `__neg__` builds its node
  directly (no `__operator_base__` indirection); `__abs__` is
  `call('abs', self)`; `evaluate`, `value`, `__str__`, `__repr__` and
  `__float__` are verbatim; `_render` is dropped. `restore_scalar`'s
  unparseable fallback is `GraphValue(ExpressionNode('raw', text=value))`.
  `symbolic` decides a plain `int`/`float` by a membership test of its class
  (no call), then a `GraphValue`, then an `ExpressionNode`, and only then
  asks `machinome.scad_engine.scad_engine()` and the provider's `adopt`.
- `machinome/scad_expression.py` deleted; `machinome/openscad.py` moved to
  `machinome/openscad/binary.py` unchanged (`git mv`).
- `machinome/openscad/__init__.py` (docstring only), `engine.py` (`CONTRACT
  = 1`, `adopt`), `machinome/scad_engine.py` (`CONTRACT`, `PROVIDER`,
  `ScadEngineIncompatible`, `scad_engine()`; absent when the missing module
  is `machinome.openscad`, the provider or `solid2`).

**One addition to design.md Decision 4, for the cost pin.** `adopt` keeps
the node it read on the SolidPython constant it read it from
(`value.__dict__['_machinome_adopted'] = (text, node)`), and reads the text
again only if the constant's text object was replaced. Without it,
`machinome.math.sin(L)` parsed `L`'s text three times (`_face` asks whether
it is symbolic, `_is_formula` asked again, `call` builds its node): 380 calls
against the 0.7.1 ceiling of 135 (148.5 with the 10 % allowance), measured
by `test_expression_type_cost.py` before the cache. With the cache, and with
`_is_formula` reduced to `isinstance(value, Expression)` (a number or a
symbolic value is never an `Expression`, so its first clause asked nothing
the last did not answer), a constant never read before costs 144 for
`sin(L)` and 128 for `t + L`. The cost test measures that cold case: the
SolidPython operand is made anew for the measured call.

### 3.2 Callers

- `machinome/math.py`: imports `ExpressionNode`, `GraphValue`, `call` and
  `symbolic` from `machinome.expression_graph`; `_is_symbolic` is
  `GraphValue` first, then a plain number, a bare `ExpressionNode` or a
  declared `Expression` answer `False` without consulting the engine (a
  declared formula is the third face, never a SolidPython value, and asking
  the engine about one would import SolidPython from inside a class body),
  and anything else is `symbolic(value) is not None`. The module docstring's
  symbolic face is rewritten; the "four clock models never needed to import
  solid2's private OpenSCADConstant" comment is kept as history.
  `_is_formula` as above.
- `simulation/program.py` (four sites: `_compiled_bound`,
  `_compiled_reading_bound`, the law-return free-name check, `_graph_of`),
  `simulation/clocked.py` (`_Chain._expression`), `simulation/profile.py`
  (`profile_overlap`): `symbolic(value)` in place of `isinstance(value,
  OpenSCADConstant)`; every refusal's wording unchanged.
- Import lines to `machinome.expression_graph`: `node/operations.py`,
  `node/flexible.py`, `node/qualified.py` (its two `expression_graph`
  imports merged), `node/assembly.py`, `node/solid2.py`,
  `core/serializer.py`; and `tools/generate_clocked_corpus.py`, which
  `test_clocked_corpus.py` runs (not in task 5.3's list; found by the 1.4
  file list after the change: 57 failures of `No module named
  'machinome.scad_expression'`, all from that tool).
- Import lines to `machinome.openscad.binary`: `node/base.py`,
  `node/solid2.py`, `viewers/openscad.py`, `manager/snapshot.py`.
- Docstrings and comments (5.5): `node/qualified.py` (module, `DriverToken`),
  `node/assembly.py` (`clear_keyframe`, `time`), `motion/ports.py`,
  `motion/couplings.py` (`Affine`), `node/flexible.py`
  (`bound_expressions`, `_time_fed_ports`), `node/operations.py`
  (`_as_number`, `Rotation.matrix`).

### 3.3 Existing tests (group 6)

- 6.1: 18 test files repointed from `machinome.scad_expression` to
  `machinome.expression_graph` (`tests/base.py` and 17 `test_*.py`); the
  six files patching the binary locator now import from and patch
  `machinome.openscad.binary` (`shutil.which`, `openscad_binary`).
- 6.2 `tests/test_math.py`: `get_animation_time` is the core's
  (`machinome.expression_graph`); `SymbolicModeTest` and
  `SymbolicBuiltinStringTest` assert `GraphValue` (`test_returns_openscad_constant`
  renamed `test_returns_a_symbolic_value`). `LegacySolidPythonTimeTest`
  subclasses `SymbolicModeTest` with SolidPython's `$t`: the same three
  tests, the same texts, a `GraphValue` result, and a fourth test that the
  operand and `720.0 * $t` are SolidPython's own constants.
- 6.3 `test_legacy_operand_order_and_public_math`: framework-left results
  (`x - legacy`, `abs(x)`, `sin(x)`) are `GraphValue`; legacy-left
  (`legacy - x`, `legacy / x`) are SolidPython constants, not `GraphValue`;
  the four texts unchanged; `bool(x < legacy)` raises `SymbolicTruthError`,
  `bool(legacy < x)` SolidPython's `Exception`.
- 6.4: `test_expressions.py`, `test_driver_ids.py`, `test_couplings.py`
  and `tests/clocked_project/unsupported.py` passed unchanged; none asserts
  `OpenSCADConstant` of a framework value. One present-tense comment in
  `test_keyframe_reversal.py` ("Symbolic time is solid2's $t, an
  OpenSCADConstant") now says the framework's own `GraphValue`.

The old `test_every_supported_operator_keeps_both_legacy_operand_orders`,
run after the change from a scratch copy with only its import repointed
(task 2.6):

```
12 failed, 1 passed, 12 subtests passed in 3.01s
E   AssertionError: (2 + drive) is not an instance of <class 'machinome.expression_graph.GraphValue'>
E   AssertionError: (2 - drive) is not an instance of <class 'machinome.expression_graph.GraphValue'>
... one per operator, the twelfth:
E   AssertionError: (2 >= drive) is not an instance of <class 'machinome.expression_graph.GraphValue'>
```

The right-hand subtests pass; every left-hand one fails on the type alone,
which is the delta's scenario.

## 4. Characterisations and the suite (group 7)

Group 8's documentation was written before the whole suite, so the one run
covers it (the lean-install precedent); otherwise tasks.md's order.

### 4.1 The goldens (7.1)

```
tests/expression_type_golden.py --check  golden comparison: 17 values, 0 differences
tests/exact_engine_golden.py --check     golden comparison: 7 fixtures, 0 differences
tests/leaf_contract_golden.py --check    golden comparison: 7 fixtures, 97 values, 0 differences
tests/markings_golden.py --check         golden comparison: 18 values, 0 differences
```

The SCAD of the assembly and its children, the operations' standalone
texts and the published document (version 4, bindings, graph values) are
byte-identical. `test_running_corpus.py` and `test_clocked_corpus.py`
reproduce their committed corpora with the fixtures untouched (in 4.3's
1.4 list and in the suite).

### 4.2 Tasks 2.1-2.8, green (7.2)

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider -rf \
  tests/test_expression_type.py tests/test_scad_engine_seam.py tests/test_openscad_engine.py \
  "tests/test_expression_graphs.py::ExpressionGraphTest::test_every_supported_operator_keeps_both_legacy_operand_orders" \
  tests/test_expression_faces.py tests/test_expression_type_cost.py
40 passed, 215 subtests passed in 7.88s
```

Two of the new tests were corrected after the change, for their own
defects: `test_a_plain_number_never_consults_the_seam` called `m.min(1, 2,
3)` (min takes two), and the binary-locator AST rule read import statements
only, so it missed `scad_engine.py`, which names the provider in a string
constant as `exact_engine.py` does; it now also matches a string constant
`machinome.openscad(.x)*`, as `test_core_kernel_free.py`'s rule does. The
cost test was changed once, to measure a SolidPython constant never read
before (3.1); it is green on the unmodified tree too (run against `git
archive 2c9d65f` in the scratchpad: `2 passed, 17 subtests passed`).

The 1.4 file list after the change: `430 passed, 11 warnings, 478 subtests
passed in 19.38s` (426 before: the four of `LegacySolidPythonTimeTest`).
Every test file the change touches, with `test_vet_assertions.py`,
`test_keyframe_reversal.py`, `test_meta.py` and `test_conrod_symbolic.py`:
`815 passed, 6 warnings, 907 subtests passed in 120.96s`.

### 4.3 The whole suite (7.3)

Run once, alone (no other pytest process; checked with `pgrep -af
"[p]ytest"`):

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider -rf
4350 passed, 4 skipped, 53 warnings, 3648 subtests passed in 526.46s (0:08:46)
exit 0; wall time 529 s; no "Too many open files"
```

Beside `lean-install`'s run of record (`4307 passed, 4 skipped, 3457
subtests passed in 537.46s`): 43 more tests, the new files of group 2 and
`LegacySolidPythonTimeTest`; wall time within 11 s. While it ran, two
cosmetic edits were made to already-collected test files (a comment
re-wrapped in `test_math.py`, a test method of `test_expression_type.py`
renamed under flake8's line length); those two files re-run alone after:
`69 passed, 6 subtests passed`.

Lint: `flake8 --max-line-length=89` (7.3.0) over every changed or new
Python file finds nothing new against the originals (the new files: 0;
`test_math.py` keeps its five pre-existing findings).

### 4.4 The cost, before and after (7.4)

Same scratch script, same machine; `t` is the unbound `SharedMotion().time`,
`L` a SolidPython constant reused across the warm-up (so after the change
the measured call meets an already adopted value):

| operation | calls before | calls after | time before | time after |
|---|---|---|---|---|
| `t+1` | 11 | 9 | 1.52 µs | 1.39 µs |
| `1+t` | 11 | 9 | 1.53 µs | 1.38 µs |
| `t*t` | 8 | 7 | 0.76 µs | 0.70 µs |
| `t-t` | 8 | 7 | | |
| `t/2` | 11 | 9 | | |
| `t%2` | 11 | 9 | | |
| `t**2` | 11 | 9 | | |
| `-t` | 6 | 5 | 0.69 µs | 0.64 µs |
| `abs(t)` | 11 | 11 | | |
| `t<1` | 11 | 9 | | |
| `sin(t)` | 18 | 16 | 1.50 µs | 1.38 µs |
| `atan2(t,1)` | 28 | 25 | | |
| `min(t,1)` | 28 | 25 | | |
| `clamp01(t)` | 56 | 50 | 5.35 µs | 4.88 µs |
| `t+L`, `L = scad_inline('($t * 2)')` | 125 | 13 (cached) | | |
| `L+t` | 125 (a `GraphValue`) | 59 (SolidPython's own text) | | |
| `sin(L)` | 135 | 29 (cached) | | |
| `t+L`, `L = solid2.get_animation_time()` | 50 | 13 | | |
| `L+t` | 59 (SolidPython's text already) | 59 | | |
| `sin(L)` | 60 | 29 | | |

With a constant made anew for the measured call (no adoption cached;
`git archive 2c9d65f` for "before"):

| operation | before | after | ceiling (110 %) |
|---|---|---|---|
| `t+L` | 125 | 128 | 137.5 |
| `L+t` | 125 | 59 | 137.5 |
| `sin(L)` | 135 | 144 | 148.5 |

Importing the vocabulary, fresh interpreter, median of five:

```
                                   before                after
import machinome.math              28.8 ms, solid2 True  14.3 ms, solid2 False
import machinome.expression_graph  13.3 ms, solid2 False 13.3 ms, solid2 False
```

Per-tick evaluation (`GraphValue.evaluate`, the compiled path evaluators)
is unchanged code and was not re-measured; the projects' wall times are the
validation's (task 10).

### 4.5 What still imports SolidPython (AST, after)

```
machinome/manager/templates/project/root/__init__.py  solid2: cube, cylinder, translate   (cycle 8)
machinome/node/base.py        solid2: color, import_stl, scad_render                     (cycle 6)
machinome/node/flexible.py    solid2: union                                              (cycle 6)
machinome/node/internal.py    solid2: union                                              (cycle 6)
machinome/node/openscad.py    solid2: scad_render; solid2.core.parse_scad; solid2.core.utils (cycle 7)
machinome/node/operations.py  solid2: rotate, translate                                  (cycle 6)
machinome/node/solid2.py      solid2: scad_render                                        (cycle 7)
machinome/openscad/engine.py  solid2.core.object_base: OpenSCADConstant                  (the engine)
```

## 5. Documentation and the plan (group 8)

- `docs/architecture.md`: the schema-4 paragraph names `GraphValue` in
  `expression_graph.py` and the adoption by `machinome.openscad.engine`
  through `machinome/scad_engine.py`; the ADR-046 paragraph names
  `machinome.openscad.binary`; the map's Kinematics row gains
  `expression_graph.py`, `motion-expression-sharing`, 101 and 170, and a new
  "OpenSCAD engine" row (`scad_engine.py`, `openscad/`; `scad-engine-dependency`,
  `openscad-engine`, `openscad-dependency`; 046, 102, 171).
- `docs/project/changelog.rst`: task 8.2's bullet, verbatim, at the top of
  `Unreleased`. No `.rst` page of the manual named `OpenSCADConstant`,
  `scad_expression`, `GraphValue` or the binary helpers (grep), so no
  teaching page changes.
- `workflow/ongoing/lean-core.md`: the validation table's `expression type`
  row (its result sentence waits for task 10), the Import paths row for
  `machinome.openscad`, the note under "Where the core reaches each
  kernel", and Layers item 5 marked done with ADR-170, ADR-171 and the
  evidence path.

## 6. Empirical validation (group 10, run by the orchestrator)

Reported by the orchestrator on 3 October 2026; quoted verbatim where they
quote a message, a hash or a summary line. The bench held this change
uncommitted for every "after" leg.

### 6.1 Deep: Locks/Pin_tumbler_lock (10.1)

Run in the project's own checkout on branch `lean-core-validation` (from
main e461fba; no file changed, the branch holds no commit; the checkout is
back on main), each leg into a fresh scratch build directory
(`SOLID_BUILD_DIR`) and a fresh export directory,
`PYTHONPATH=<bench>:<project>`.

| leg | `machinome build` | `machinome test --faceted` | `machinome export --set key_delta=0` | `program_of(PinTumblerLock())` |
|---|---|---|---|---|
| before (bench 2c9d65f, 21:12) | exit 0 in 12 s | `Ran 24 tests in 27.66 seconds: 24 passed, 0 failed` | exit 0; 24 `.scad` files hashed | 0.142 s |
| after (21:50) | exit 0 in 11 s | `Ran 24 tests in 27.97 seconds: 24 passed, 0 failed` | exit 0; all 24 `.scad` files byte-identical to the before leg | 0.120 s |

`manifest.json` differs in exactly one value: `pieces[1].volume` (the Core
piece) `21065.08699624388` before, `21065.086996243885` after; every other
key, `bindings`, `drivers`, `program`, `animation`, `source` and `version`
included, is identical. The cause is not the change: the STL files of
several parts (Body, Core, DriverPin, Key, ...) differ in bytes between the
two scratch builds although their SCAD sources are byte-identical, so
OpenSCAD renders the same SCAD to different triangle orderings run to run,
and the piece volume summed over a differently ordered mesh differs by one
unit in the last place; exporting twice from the same build directory gives
the same volume both times. The stop condition (a change to the document's
expression graph or bindings) did not fire. Migration: none. Recorded in
`workflow/warts.md` ("Findings from the framework cycle `expression-type`").

### 6.2 Clocked probe: the Curta (10.2)

Read-only in `projects/Calculators/Curta-Type-I-3x` with
`PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=<bench>:<project>`. The names in
the code are `machinome.simulation.clocked.clocked_of` (returning the
compiled machine and the initial values) and
`machinome.core.serializer.clocked_block` (design.md and task 10.2 said
`compiled_clocked`):
`json.dumps(clocked_block(*clocked_of(EventDrivenCurta())), default=str,
sort_keys=True)`.

```
before: 88910 bytes, SHA-256 prefix be1e37234b443566, clocked_of 1.96 s
after:  88910 bytes, SHA-256 prefix be1e37234b443566, clocked_of 1.79 s
```

Identical.

### 6.3 Cross-package probe: machinome-mechanics (10.3)

Its suite from `/home/asa/devel/machinome/machinome-mechanics` with
`PYTHONPATH=<bench>:<repo>`:

```
before: 201 passed, 24 subtests passed in 2.03s
after:  9 failed, 200 passed, 16 subtests passed in 1.93s
```

Every failure is one assertion in mechanics' tests: `isinstance(result,
OpenSCADConstant)` (`tests/test_motion.py:46`
`test_the_realized_law_preserves_symbolic_math`, and
`tests/test_mechanisms.py:349` under eight subtests), the solid2 class
having been the only public spelling of "this value is symbolic"; the
results are the core's expression nodes (`<ExpressionNode binop '*'>`
etc.). Mechanics' library code does not name the class; only those two test
sites do.

design.md ("Impact", "Downstream") and task 10.3 expected the same counts,
so this was returned to the pilot as a stop. **The pilot's decision,
3 October 2026:** integrate the framework change and run a mechanics cycle
in that repository, its tests asserting the core's public predicate
`machinome.expression_graph.symbolic` in place of solid2's class. The
expectation was wrong about mechanics' tests, not about its behaviour, and
the correction is mechanics'.

### 6.4 Shallow: the universe (10.4)

From the workspace root at 21:51, five moved-names files (the four previous
and this change's `moved-names.toml`), `--timeout 300`, JSON at
`load-projects.json` beside this file. Ended 22:13, exit 1:

```
62 repositories, 129 rows: 117 ok, 4 expected, 2 unexpected, 0 timeout, 6 no-model; 2 skipped
Skipped: .Trash-1000 (skip rule), sandbox (skip rule)
```

Identical to the fourth cycle's sweep: expected Voron-2,
Internal-Cycloidal-Actuator, YouCanBuildDog, openvmp/don1; unexpected
wall_clock_41 and Dum-E (pre-existing); six no-model. No row names a name
this cycle moved.

### 6.5 Findings outside this repository

- machinome-mechanics' tests name solid2's `OpenSCADConstant` as the test of
  symbolic-ness (6.3); corrected by a mechanics cycle, the pilot's decision.
- machinome-viewer carries a stray root-level `openscad.py`, outside its
  package and imported by nothing, which imports
  `machinome.openscad.require_openscad`, a name this change moved to
  `machinome.openscad.binary` (design.md, "Deferred").

## 7. Records (group 11)

- **ADR-170** under `docs/adrs/MATH/`, "The core's symbolic value is its own
  type", amending ADR-101's facade decision and ADR-056's `DriverToken`
  representation clause, citing ADR-022, ADR-080 and ADR-171.
- **ADR-171** under `docs/adrs/NODE/`, "The OpenSCAD engine is
  `machinome.openscad`, reached for expressions through
  `machinome.scad_engine`", amending ADR-046's module location, citing
  ADR-161, ADR-162 and ADR-170. It records the adoption cache of 3.1.
- **Amendments:** ADR-101 (status line; "Amendment (2026-10-03)" at the
  end), ADR-056 (status line; "Amendment (2026-10-03): the token is the
  core's own value" before "Implementation status"; the spike evidence kept
  as history), ADR-046 (status line; "Amendment (2026-10-03): the locator's
  module" before References, whose paths stay history).
- `docs/adrs/README.md`: ADR-171 under NODE after ADR-169, ADR-170 under
  MATH after ADR-132; ADR-046 "amended by 166, 171", ADR-056 "`DriverToken`
  representation amended by 170", ADR-101 "facade amended by 170". Every
  relative link in the five ADRs and the index resolves (checked by script);
  the ADRs link the change at `openspec/changes/archive/2026-10-03-expression-type/`,
  which resolves with this archive.
- `workflow/ongoing/lean-core.md`: the `expression type` row of the
  "Empirical validation" table now carries its result (6.1 to 6.4) and this
  file's path.
- `workflow/warts.md`: a section "Findings from the framework cycle
  `expression-type` (3 October 2026)": OpenSCAD's STL output not
  reproducible run to run (untriaged), and, for the record, mechanics' tests
  and the viewer's stray `openscad.py`.
- **Specs.** `openspec archive expression-type --yes` applied the deltas:
  `motion-expression-sharing` + 1 added, ~ 1 modified; `openscad-engine`
  created, + 2; `scad-engine-dependency` created, + 3; "Totals: + 6, ~ 1,
  - 0, → 0", archived as `2026-10-03-expression-type` (with
  `moved-names.toml` and `load-projects.json`). A copy of `openspec/specs/`
  taken before the archive was diffed against the result: the removed lines
  are the old text of the one modified requirement and nothing else. Then by
  hand: the two new capabilities' Purpose (the archive writes "TBD").
  The archive warned "3 incomplete task(s)": 11.2 to 11.4, ticked in the
  archived `tasks.md` with this commit.

```
openspec validate --specs --strict   -> Totals: 43 passed, 0 failed (43 items)
```

After the records (no source change since the whole-suite run of 4.3), the
files that read specs, records and documentation were run alone with the
cycle's new files: `tests/test_release_records.py
tests/test_docs_structure.py tests/test_docs_exports.py
tests/test_leaf_contract_members.py tests/test_profile_documentation.py
tests/test_frame_precision_docs.py tests/test_scad_import_paths.py
tests/test_core_kernel_free.py tests/test_expression_type.py
tests/test_scad_engine_seam.py tests/test_openscad_engine.py
tests/test_vet_assertions.py`: `116 passed, 6 warnings, 505 subtests passed
in 12.00s`.
