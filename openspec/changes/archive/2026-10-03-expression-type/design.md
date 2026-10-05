## Context

Cycle 5 of the lean-core campaign's "Layers" (`workflow/ongoing/lean-core.md`,
pilot, 3 October 2026): "the core's own expression type in place of solid2's
`OpenSCADConstant` facade", the first of four cycles that take OpenSCAD out of
the core. The plan's "Import paths" (an engine package is `machinome.<name>`, a
subpackage whose `__init__.py` defines nothing; seams are try-imports of one
known provider with a contract version, D2), "Where the core reaches each
kernel" (solid2 as the core's rendering language) and "Empirical validation,
per cycle" govern it; the four archived cycles are its precedents, above all
`exact-engine` (an engine at its final address inside the core, reached
through a seam, with its own capability spec that leaves with the code;
ADR-161, ADR-162).

Facts below were read in the bench at edff84e on 3 October 2026, with the
workspace venv (solidpython2 2.1.3, Python 3.12.3), unless marked *inferred*.

### Originating evidence

- **The layering ruling and its licence reason.** Layer 2 exists so that a
  GPL-2.0-only project, an OpenSCAD project, can import machinome with no
  Apache-2.0 code beneath it; that turns on the core's grant and its required
  dependencies, and a package matches its provider's licence. solidpython2 is
  LGPL-2.1-or-later and required; OpenSCAD is GPL-2.0-or-later and a process.
  Layer 1 builds the architecture for that split, OpenSCAD included, inside one
  distribution; the pilot wants OpenSCAD out of the core before the package
  split.
- **The twelve importers** (proposal.md's table): five take only
  `OpenSCADConstant` (`math.py`, `scad_expression.py`,
  `simulation/{clocked,program,profile}.py`); four take SCAD presentation
  (`node/{base,operations,internal,flexible}.py`); two are the OpenSCAD leaves
  (`node/{solid2,openscad}.py`); one is the template. `node/jscad.py`,
  `node/leaf.py`, `test.py`, `motion/ports.py` and `motion/couplings.py`
  mention solid2 in text only.
- **What projects and siblings do with SolidPython expressions** (grep,
  3 October 2026, `projects/` excluding `WTs/`, `_build*`, `.venv`):
  - no project file imports `OpenSCADConstant`, `scad_inline`, `ScadValue`,
    `GraphValue`, `restore_scalar` or `depends_on_time`; four import
    `solid2.core.object_base.OpenSCADObject` (a *shape* base: kossel,
    Prusa3-vanilla, Metamaquina2 twice, snappy-reprap), which is presentation;
  - five probe files call `solid2.get_animation_time()` and pass it through
    project kinematics built on `machinome.math` (hexapod_spiderbot_model,
    Metamaquina2 twice, strandbeest, Thor; all under `docs/`);
  - three probe files import `get_animation_time` from
    `machinome.scad_expression` (Pascaline-module, CycloidalDrive, Leonardo
    `models/cam_hammer`; all under `docs/probes/`);
  - no project imports `machinome.openscad` (the binary locator);
  - machinome-mechanics' suite calls `solid2.get_animation_time()` in four
    test files (`test_internal_mesh_angle.py`, `test_indexed_advance.py`,
    `test_belts.py`, `test_belt_paths.py`) and feeds it to functions built on
    `machinome.math`; it reads results through `str()` and
    `machinome.core.expressions.parse`/`render`;
  - the studio's contract skill names none of `OpenSCADConstant`,
    `GraphValue` or `machinome.scad_expression`; it teaches `self.time`,
    drivers and `machinome.math`, symbolic `$t` "in the build and viewer".

### What the facade is

`GraphValue` (`machinome/scad_expression.py`) holds an immutable
`ExpressionNode` (`machinome/expression_graph.py`, no backend) and subclasses
`solid2.core.object_base.OpenSCADConstant`. Time (`get_animation_time()`, the
`AssemblyNode.time` fallback), driver reads (`DriverToken(GraphValue)`), port
values, every symbolic result of `machinome.math`, compiled law, bound, chain,
jump-plan and profile-contact graphs are `GraphValue`s. Consumers:

1. **Arithmetic and comparison.** `GraphValue` defines `__operator_base__`,
   `__roperator_base__`, `__unary_operator_base__`, every reflected operator,
   the six comparisons and `__abs__`. It *inherits* from `OpenSCADConstant`
   only `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__mod__`,
   `__pow__`, `__neg__`, `__bool__` and `__illegal_operator__` (probe of
   `vars()` on both classes). The first seven are one-liners that call
   `self.__operator_base__`/`__unary_operator_base__`, which `GraphValue`
   overrides: solid2 supplies only the method names. `__bool__` raises a bare
   `Exception`: "You can't evaluate scad variables because we don't know the
   value of the variable at SolidPython runtime."
2. **Recognition.** Ten `isinstance(x, OpenSCADConstant)` sites decide "this is
   symbolic": `math._is_symbolic`; `scad_expression.as_node`,
   `depends_on_time`, `scalar`; `clocked._Chain._expression`;
   `program._compiled_bound`, `_compiled_reading_bound`, the law-return
   check and `_graph_of`; `profile.profile_overlap`. For a `GraphValue` each
   could test `GraphValue`. They exist as `OpenSCADConstant` checks so that a
   value SolidPython built is accepted too: `as_node` reads such a value by
   parsing `str(value)` with the core's own parser, falling back to a `raw`
   node.
3. **Reflected priority.** Because `GraphValue` subclasses `OpenSCADConstant`,
   `legacy + native` dispatches to `GraphValue.__radd__` (Python prefers a
   right operand's reflected method when its type subclasses the left's), so
   it returns a graph. `tests/test_expression_graphs.py::
   test_every_supported_operator_keeps_both_legacy_operand_orders` pins it.
4. **Text.** `str(GraphValue)` is `core.expressions.scad_expression(node)`: the
   compact closed scalar, `let(_s0 = ..., ...) body` when the graph shares a
   subexpression, plain otherwise. It is written by the core (Apache, no
   solid2), read back by the core's own parser, and used as: the standalone
   `Operation.serialized` form (kinematics spec), `.value`, every diagnostic,
   the clocked identity's canonical lines (`clocked._text`), the verbatim
   fallback of `bind_expressions` for `raw` content, and SCAD output.
5. **SCAD output.** solid2's `py2openscad` renders a parameter that is not a
   `bool`, `str`, `ObjectBase` or iterable by `str(o)`
   (`solid2/core/utils.py:56`); it never asks whether the value is an
   `OpenSCADConstant`. Probe: `scad_render(rotate(t*360, [0,0,1])(cube(1)))`
   is `rotate(a = ($t * 360), v = [0, 0, 1]) {...}` through `str()` alone.
6. **Publication.** The document's expression graph is compiled from native
   `ExpressionNode` roots (`serialize_node(graph_values=True)`,
   `bind_document`, `bind_expressions`), never from the type. A foreign value
   reaches it only through `as_node`.

So solid2's type is **load-bearing** in exactly two places: (2) recognising a
value SolidPython built, and (3) keeping a native graph when such a value is on
the left. Everywhere else it is the spelling of a constant: seven inherited
method names, one refusal message, and an `isinstance` target that a native
check would replace.

The **native shared graphs** are already the core's: `ExpressionNode` and
`postorder` (`expression_graph.py`), interning, binding and the schema-4
language (`core/expressions.py`, `core/expression_parser.py`),
`GraphValue.evaluate`, and the simulation's compiled path evaluators. None
imports solid2.

### The document and SCAD text are the core's language

The document's expression language (schema 4, ADR-080/101) is OpenSCAD's
scalar expression syntax minus `let`, by design (ADR-022: OpenSCAD's
degree-in/degree-out builtins, `^` as power). The closed `let` form is the same
grammar plus OpenSCAD's `let`, which the core's parser reads and the document
never carries. Both are written by `core/expressions.py`. There is no
translation from "the core's expression" to "OpenSCAD syntax" to perform: the
text *is* OpenSCAD syntax, which is why SCAD output needs nothing but `str()`.

### Cost of the symbolic path today

Measured in the bench, warm, on the test machine, 3 October 2026:

| what | value |
|---|---|
| Python calls per operation (`sys.setprofile`, `call` + `c_call`), after a warm-up | `t+1` 11, `1+t` 11, `t*t` 8, `t-t` 8, `t/2` 11, `t%2` 11, `t**2` 11, `-t` 6, `abs(t)` 11, `t<1` 11, `sin(t)` 18, `atan2(t,1)` 28, `min(t,1)` 28, `clamp01(t)` 56; with a SolidPython constant `L`: `t+L` 125, `L+t` 125, `sin(L)` 135 |
| time per operation (`timeit`) | `t+1` 1.43 µs, `1+t` 1.57, `t*t` 0.73, `-t` 0.67, `sin(t)` 1.56, `clamp01(t)` 5.61 |
| `GraphValue.evaluate` of a 2001-node chain | 462 µs; `str()` of it 12.6 ms |
| Locks/Pin_tumbler_lock: import 1.10 s, construct 0.13 s, `program_of` 0.085 s | running root, 5 law/bound graphs |
| Calculators/Curta-Type-I-3x `EventDrivenCurta`: import 3.10 s, construct 1.84 s, `compiled_clocked` 0.45 s cold / 0.16 s warm; 16 604 `machinome.math._face` calls | clocked root |
| `import machinome.math` | 32 ms, pulling `solid2` (≈20 ms of it); `import machinome.expression_graph` 12 ms, no solid2 |

Per-tick evaluation (`GraphValue.evaluate`, `_PathValue`, `_KinkCuts`) walks
`ExpressionNode`s and never touches the facade, so this change does not move
it; construction and recognition are what it can move.

## Goals / Non-Goals

**Goals:**

- No core module imports SolidPython for an expression; importing
  `machinome.math` or `machinome.expression_graph` imports no SolidPython.
- The symbolic value is a type the core defines once, at one address.
- Unchanged arithmetic, comparisons, degree math, evaluation, text, SCAD
  bytes and document bytes; no document version moves.
- The ratified acceptance of SolidPython operands kept, through the OpenSCAD
  engine at its final address, reached by a seam of the exact engine's shape.
- No construction cost regression.

**Non-Goals:**

- The SCAD presentation (`as_scad`, `generate_scad`, `_publish_scad`,
  `scad_code`, `stl_builder_command_for`, `assemble()`, `Operation.scad`, the
  `union`s, `_ArtifactImport`) and the `develop` fallback: cycle 6.
- The binary runner, `Solid2Node`/`OpenScadNode` as node modules over the
  engine, `Solid2Node.as_number`'s OpenSCAD evaluation of SolidPython values,
  the `openscad` extra and its refusal, the snapshot renderer: cycle 7.
- The project template: cycle 8.
- Any change to required dependencies; solidpython2 stays required.
- The studio skill (nothing it teaches changes), the viewer, the projects.

## Decisions

### 1. The type: `GraphValue` at `machinome.expression_graph`

The value type and its helpers move from `machinome/scad_expression.py` into
`machinome/expression_graph.py`, beside `ExpressionNode` and `postorder`, and
`scad_expression.py` is deleted (one path, defined once; no alias module, the
`exact-engine` precedent for `machinome.exact`). The name stays `GraphValue`:
it is backend-neutral, it is the evaluator's name in ADR-106/107/124/126 and in
`docs/architecture.md`, and no project spells it.

Alternatives:

- *`machinome.math`.* It is the vocabulary a project imports with names that
  shadow builtins; the type is the representation the vocabulary's symbolic
  face returns, also used by the node layer, the motion layer, the serializer
  and the simulation, none of which should import the vocabulary to get it.
  `GraphValue.evaluate` already imports `machinome.math` lazily for the
  numeric faces; putting the type in `math.py` would make that a self-import
  and couple the graph to the dimension algebra `math.py` imports.
- *`machinome.motion`.* Lower layers need it: `node/qualified.py`,
  `core/serializer.py`, `simulation/profile.py`; the motion package's
  `__init__` exports nothing and its submodules are kinds of mechanism.
- *A new module (`machinome/symbolic.py`).* Splits one subject in two:
  `GraphValue` is a handle on an `ExpressionNode`; `expression_graph.py` is
  "native immutable motion operations, no modelling backend", which is what
  the type now is.
- *Rename the type `Expression`.* `machinome.parameters.Expression` is the
  declared face's formula, imported by `math.py`; two `Expression`s would
  misread at every call site.

### 2. What the type defines

Everything it has today, defined on itself: `__add__`, `__sub__`, `__mul__`,
`__truediv__`, `__mod__`, `__pow__` (published as `^`), their reflections,
`__neg__`, `__abs__` (`abs(x)` call), the six comparisons returning graphs,
`__float__` (evaluate with no inputs), `evaluate(inputs)` verbatim, `value`
(the `str()` property ADR-101 names), `__str__` (the closed scalar text,
verbatim) and `__repr__`. Defining `__eq__` keeps it unhashable, as today. No
`__iter__`, `__len__`, `__index__` or `__pos__`, as today (solid2 would read
an iterable as a vector; `+t` raises `TypeError` as now). `_render`, which only
SolidPython's `OpenSCADParameterFunction` path ever calls, is dropped.

**Truth.** `__bool__` raises `SymbolicTruthError(Exception)`, defined in
`machinome.expression_graph`, with a bounded description of the value (the
`_describe` rule of `math.py`, 200 characters) and the remedy: compose with
`machinome.math`'s `min`, `max`, `clamp`, `sign`, or bind the drivers first.
It subclasses `Exception` and *not* `TypeError` deliberately: 25 sites in the
framework catch `TypeError` (`motion/joints.py`, `couplings.py`,
`simulation/*.py`, `parameters.py`, ...), none audited for a truth test of a
symbolic value inside their `try`; SolidPython's refusal was a bare
`Exception`, which none of them catch, so a `TypeError` could turn a refusal
into a silent branch. Every `except Exception` still catches it.

**Recognition** is one core predicate, `symbolic(value)`, returning the graph
node of a value that is symbolic or `None`: a `GraphValue` → its node; an
`ExpressionNode` → itself (as `as_node` and `profile_overlap` accept one
today; `machinome.math`'s own `_is_symbolic` keeps answering only for a
`GraphValue` or an adopted value, as today it answers only for an
`OpenSCADConstant`, so no bare node newly reaches a symbolic face); `int`/`float` (not `bool`) → `None` before any
other test, so the numeric face pays one `isinstance`; anything else → the
OpenSCAD engine's `adopt(value)` if the engine resolves, else `None`. `as_node`
keeps its contract (a node for anything; a number becomes `num` text, an
unrecognised object `num` of its `str()`, as today); the ten recognition sites
of "What the facade is" (2) call `symbolic` instead of `isinstance(...,
OpenSCADConstant)`. `restore_scalar`'s fallback for unparseable text becomes a
`GraphValue` over a `raw` node instead of an `OpenSCADConstant`; its `str()`,
time dependence and publication are the same text.

### 3. Rendering to SCAD: no renderer moves

The brief proposed a renderer at the engine's address that takes the core's
expression and emits OpenSCAD syntax, reached by the core's SCAD presentation
through a try-import. Read against the code, there is nothing for it to do:
the core's closed text is OpenSCAD syntax (Context), solid2 embeds a value by
`str()`, and the same `str()` is also the core's standalone serialization,
its clocked identity lines, its diagnostics, its document fallback, and what
machinome-mechanics' tests parse. So:

- `str(GraphValue)` stays `core.expressions.scad_expression(node)`, in the
  core, byte for byte;
- the SCAD presentation keeps passing values to solid2, which keeps calling
  `str()`; cycle 6, moving the presentation behind the seam, decides whether
  the presentation wraps a value explicitly.

Alternatives:

- *A renderer at `machinome.openscad`, called by `__str__`.* `str()` of time,
  a standalone operation's serialization and the clocked identity would then
  need the OpenSCAD engine; a core without it could not name its own
  expressions. Rejected: the dependency points the wrong way.
- *A renderer at `machinome.openscad`, called only by the presentation.* It
  would return `str(value)`: an identity function with one caller, built for a
  use nobody has. Rejected under "every feature needs empirical evidence";
  cycle 6 adds a wrapper if its presentation needs one.
- *Renaming `core.expressions.scad_expression`.* Cosmetic; the function is the
  core's closed-text writer whatever its name. Not done.

### 4. The engine at its final address; the seam

`machinome/openscad/` is created now, as `machinome/occt/` was by
`exact-engine`:

- `__init__.py`: a docstring and nothing else (ports spec's rule for an
  engine package).
- `engine.py`: the provider. `CONTRACT = 1`. `adopt(value)`: the
  `ExpressionNode` of a SolidPython scalar (`isinstance(value,
  OpenSCADConstant)`, which covers `ScadValue` and `scad_inline`), parsed from
  `str(value)` by `machinome.core.expressions.parse`, or a `raw` node when the
  text is outside the language; `None` for anything else. It imports
  `solid2.core.object_base` and the core, nothing else of solid2.
- `binary.py`: today's `machinome/openscad.py`, moved verbatim
  (`OpenScadUnavailable`, `openscad_binary`, `require_openscad`).

`machinome/scad_engine.py`, the seam, of `exact_engine.py`'s shape:
`CONTRACT = 1`; `PROVIDER = 'machinome.openscad.engine'`; `scad_engine()`,
`lru_cache(maxsize=1)`, returning the provider or `None`, where a
`ModuleNotFoundError` whose `.name` is `machinome.openscad`, the provider, or
`solid2` answers `None` (no SolidPython installed means no SolidPython value
can exist, so there is nothing to adopt) and any other import error
propagates; a provider whose `CONTRACT` differs raises
`ScadEngineIncompatible`, naming both versions and the provider, in ADR-162's
words, not cached. It is the one core module that names the provider.

**The refusal in this cycle.** No path *requires* the engine: adoption is
optional by nature, and a value that cannot be adopted is not an expression.
So the seam has no `require_scad_engine` and no install refusal yet; without
the engine a SolidPython value reaching a law, a bound or `machinome.math`
meets the existing refusals unchanged ("... returned <value>, which is neither
a number nor an expression over its sources."; in `machinome.math` the numeric
face's own `TypeError`). The extra `openscad` does not exist until cycle 7,
which declares it and adds the refusal naming it where the presentation and
the runner require the engine. Saying `machinome[openscad]` now would name an
install line that installs nothing.

**The forced move of the binary locator.** `machinome/openscad.py` exists (the
ADR-046 locator). A package directory of the same name shadows the module, so
creating `machinome/openscad/` moves the locator: to `binary.py`, unchanged,
which is also its final address (it is the engine's: cycle 7 makes the runner
an engine subpackage). Its importers change their import line:
`node/base.py`, `node/solid2.py`, `viewers/openscad.py`,
`manager/snapshot.py`; tests patch `machinome.openscad.binary.shutil.which`
and `machinome.openscad.binary.openscad_binary`. These four core modules
reach the engine's directory directly, outside the seam, until cycles 6 and 7
move them; the AST test of Decision 6 lists them by name so those cycles
shrink the list. The bench's path extension admits no portion carrying its own
`__init__.py` (lean-install Decision 9), so the primary checkout's
`machinome/openscad.py` cannot resolve in the bench (*inferred* from that
filter; task 1 re-probes it).

Alternatives:

- *Keep an `OpenSCADConstant`-compatible shim in the core* (`GraphValue`
  subclassing `OpenSCADConstant` when solid2 imports, or always). Zero
  behaviour change, including reflected priority; but the core imports solid2
  for an expression, which is the goal's negation, and the type's ancestry
  would depend on the install. Rejected.
- *An engine-supplied subclass the core instantiates* (a factory returning
  `class _(GraphValue, OpenSCADConstant)` when the engine is present). Keeps
  reflected priority without a core import, but every value the core builds
  becomes a SolidPython instance whenever SolidPython is installed, which is
  the shim by the back door, and each of the 23 `GraphValue(...)` construction
  sites in `simulation/` pays a lookup. Rejected.
- *Drop SolidPython operands* (retire the legacy requirement). Simplest, but
  it retires a ratified behaviour that machinome-mechanics' suite and five
  probes exercise, and nothing requires it now. Not proposed; the pilot may
  choose it.
- *Put adoption in `machinome/node/solid2.py`.* That is a node type's module;
  adoption is not a node type, and rule 1 puts a non-node thing at
  `machinome.<name>`. The plan says openscad and solid2 leave as one package.
- *Defer creating `machinome/openscad/`* and keep adoption in a temporary core
  module. Cycle 7 would move it a second time. Rejected.

### 5. A SolidPython operand on the left

Without the subclass relation, `legacy OP native` runs `OpenSCADConstant`'s
method, which builds `OpenSCADConstant(f'({legacy} OP {native})')`, embedding
the native value's closed text. The framework adopts that text when the value
reaches `machinome.math`, a law, a bound, an operation or a flexible
parameter: same evaluation, same free inputs, same operand order, sharing
recovered from the `let` closure by the parser (probe today: `t+L` and `L+t`
both read through `as_node`). What changes is observable to the author only as
a type (`isinstance(result, GraphValue)` false; `.evaluate` absent on the
SolidPython object) and as construction memory for a chain that keeps a
SolidPython operand on the left: SolidPython's own text building, linear in
the compact text per step, as for any explicitly expanded project text. No
project model does this; machinome-mechanics' tests and the probes compose at
small size. The `motion-expression-sharing` delta states it.

### 6. Proof, red first

Red on the unmodified tree, green after:

- **AST.** `tests/test_expression_type.py`: walking every `.py` under
  `machinome/`, no module outside `machinome/openscad/` imports from
  `solid2.core.object_base` or names `OpenSCADConstant`, `scad_inline`,
  `ScadValue` or `get_animation_time` from any `solid2` module; and the set of
  modules outside `machinome/openscad/` importing `solid2` at all equals
  exactly {`node/base.py`, `node/operations.py`, `node/internal.py`,
  `node/flexible.py`, `node/solid2.py`, `node/openscad.py`,
  `manager/templates/project/root/__init__.py`}. Red today: five modules.
- **Imports.** In a fresh interpreter, `import machinome.math` and `import
  machinome.expression_graph` leave `solid2` out of `sys.modules`. Red today
  for `machinome.math`.
- **Type.** `type(AssemblyNode-time fallback)`, a `DriverToken`, and
  `machinome.math.sin(symbol)` have no class from a `solid2` module in their
  MRO; `bool(t < 1)` raises `SymbolicTruthError`, not `TypeError`, and its
  message is at most a bounded length for a 10 000-node graph. Red today.
- **Seam.** With `machinome.openscad.engine` blocked by the finder of
  `tests/exact_engine_absent.py` (generalised), `scad_engine()` is `None`, a
  `GraphValue` still composes and publishes, `machinome.math.sin(scad_inline(
  '$t'))` raises the numeric face's `TypeError`, and a law returning a
  SolidPython constant is refused with the existing wording; with a stub
  provider declaring `CONTRACT = 2`, `ScadEngineIncompatible` names 1, 2 and
  the provider. Red today (no seam).
- **Engine.** `adopt` of `get_animation_time()` from solid2 is a `name`
  `$t` node; of `scad_inline('(other + 2)')` the parsed binop; of
  `scad_inline('$mystery ? 1 : 2')` a `raw` node; of `1.0`, a `GraphValue`
  or a string, `None`. `machinome.openscad` exposes no attribute of its own.
- **Legacy left.** For each of the twelve operators of
  `test_every_supported_operator_keeps_both_legacy_operand_orders`, with the
  SolidPython operand on the left the result is a SolidPython value whose
  adopted graph evaluates to `op(a, b)` and whose free names are the
  operands'; on the right it is a `GraphValue` as today. The existing test
  is rewritten to this (its left-hand assertion is red after, green with
  the rewrite: the behaviour change is the delta's).

Characterisations, green before and after by design (a byte pin cannot be red
first; they are written and recorded on the unmodified tree, task 1):

- **SCAD.** `tests/expression_type_golden.py` writes, for a fixture assembly
  whose operations carry `self.time` through `machinome.math` with a shared
  subexpression and a driver (so the closed text has a `let`), its
  `scad_code` and `Operation.serialized` forms, and the SHA-256 of each, to
  `tests/data/expression_type_golden.json`.
- **Document.** The same fixture's published document (graph values,
  bindings, version) unchanged byte for byte, in the same golden; and the
  corpus tests that reproduce `tests/running-corpus.json` and
  `tests/clocked-corpus.json` from the framework (`test_running_corpus.py::
  test_the_framework_reproduces_its_own_corpus` and its clocked twin) pass
  with the fixtures untouched.
- **Three faces.** For every name in `SYMBOLIC_BUILTINS` and every
  composition and vector helper of `machinome.math.__all__`, over sample
  points inside each function's domain: the numeric face at `x`, the symbolic
  face's `GraphValue.evaluate({'$t': x})`, and the declared face evaluated on
  an instance with the parameter bound to `x` (where the function has one:
  `bump`'s dimensionless argument, `sin` of an `Angle`), agree to the bit
  for the primitives and to 1e-12 for compositions; `sin(90) == 1.0`,
  `asin(0.5) == 30.0`, `atan2` in degrees. `SYMBOLIC_BUILTINS` unchanged.
- **Cost.** `tests/test_expression_type_cost.py`: the per-operation Python
  call counts of the table in Context, measured by `sys.setprofile` after a
  warm-up, are each at most the 0.7.1 value recorded there. A count, not a
  time, so it is deterministic on any machine. Expected after: lower for the
  seven formerly inherited operators (one call fewer each, *inferred*), equal
  for the rest; the SolidPython rows gain the seam's cached lookup and must
  stay within 10 % of 125/135.

Wall time is evidence, not a test: the validation records Pin_tumbler_lock's
`program_of` and export and the Curta's `compiled_clocked` before and after;
the budget is no regression beyond 5 % (run-to-run noise on virtiofs).

### 7. SOLID

- **Single responsibility.** `expression_graph.py` holds the value and its
  graph; `core/expressions.py` its text and publication; `math.py` the
  vocabulary; `openscad/engine.py` the one thing SolidPython-specific, reading
  SolidPython's values; `openscad/binary.py` locating a binary;
  `scad_engine.py` resolving the provider. Before, one class was at once the
  graph handle, SolidPython's compatibility type and the truth refusal
  SolidPython wrote.
- **Open/closed.** A new symbolic function extends `machinome.math` and
  `SYMBOLIC_BUILTINS` without touching the type; a second foreign expression
  library would be a second provider behind a seam, not a change to
  `GraphValue`.
- **Liskov.** `DriverToken` stays a `GraphValue` and substitutes for it
  everywhere. `GraphValue` stops claiming to be an `OpenSCADConstant`, a
  substitution it only half honoured (its `value` is a property where
  SolidPython's is an attribute, its `__init__` skips SolidPython's).
- **Interface segregation.** The engine's contract is one function, `adopt`,
  plus `CONTRACT`; cycles 6 and 7 add what their consumers call, bumping the
  version, rather than this cycle declaring presentation or runner methods
  nobody calls yet.
- **Dependency inversion, above all.** The core depends on its own type and
  on the seam's contract; it never imports SolidPython for an expression. The
  engine depends on the core (`ExpressionNode`, the parser), never the
  reverse; the core names the engine in one place, by one constant, checked
  by version. The four direct reaches into `machinome.openscad.binary` are
  presentation and runner, named in the AST test, and leave with cycles 6–7.

### 8. Empirical validation

- **Deep: Locks/Pin_tumbler_lock** (`main`, e461fba, clean on 3 October
  2026). A running root (`Time.running()`) with two drivers, a key-insert
  coordinate driving five pin lifts through `key_lift` laws built on
  `machinome.math` (`abs`, `piecewise`), five spring heights through a law
  into flexible ports (so flexible `params` carry expressions), a `Bound`
  reading the five lifts (the shear window, so `_compiled_reading_bound`'s
  recognition site runs) and one reading the plug's turn, molejo springs
  (`PenSpring`, a `MolejoNode`) fed through ports, and `Solid2Node` parts
  (`simulation/parts.py`), so the SCAD presentation writes files whose
  operations carry symbolic values (*inferred* from the September build log,
  which wrote `lock-Plug,...scad` and `lock-PinTumblerLock,...scad`). Its suite ran 5 tests in 4.3 s in September
  (`_evidence/faceted-final.log`); its compile is 0.085 s. It exercises four
  of the five facade importers, the seam's native path and the SCAD bytes in
  one cheap project. Expected migration: none (it imports no moved name).
  Its legs: `machinome build`, `machinome test --faceted`, `machinome export
  --set key_delta=0 -o <scratch>`; compare `manifest.json`, every `.scad`
  under `_build/`, and the timings, before and after.
- **Clocked probe: the Curta's `EventDrivenCurta`.** The clocked face (commit
  laws, chains, bounds) is not in the lock. The Curta loads on this line;
  `json.dumps(clocked_block(*compiled_clocked(node)), default=str,
  sort_keys=True)` is 88 910 bytes with SHA-256 prefix `be1e37234b443566` at
  edff84e (3 October 2026, this proposal's probe), and costs 0.16–0.45 s. Its
  `default=str` is the closed text, so the hash pins text and structure. The
  whole Curta suite is not run (cost).
- **Cross-package probe: machinome-mechanics' suite** before and after, with
  `PYTHONPATH=<bench>`: the only real consumer of SolidPython operands.
- **Shallow:** the universe sweep with the four previous moved-names files
  and this cycle's; no project root imports a moved name (the importers are
  probes), so no new row is expected.

## Risks / Trade-offs

- [A project or package relies on `isinstance(x, OpenSCADConstant)` for a
  framework value] → none found in `projects/`, machinome-mechanics,
  machinome-freecad or the videomaker; the changelog says so.
- [A `SolidPython-left` chain grows quadratically] → only for text a project
  builds through SolidPython's own operators, as any explicitly expanded text
  already does under the ratified requirement; no model does it.
- [Something catches the truth refusal by type] → it stays an `Exception`, not
  a `TypeError`; a test pins that.
- [The binary locator's move breaks a caller outside the framework] → only
  machinome-viewer's stray, unpackaged root `openscad.py`, which nothing
  imports (recorded as a finding for that repository).
- [Recognition through the seam costs on a hot path] → numbers and native
  values are decided before the seam is consulted; the call-count test pins it.
- [The document changes] → it cannot through the type (publication reads
  nodes), and the byte pins and the validation compare it. If it did change,
  that would be a document-version bump the viewer must follow, and the cycle
  stops there for the pilot.

## Migration Plan

Projects: nothing to do. The three probes importing
`machinome.scad_expression.get_animation_time` change one import line to
`machinome.expression_graph`, by the one-path cycle's rewrite script, whose
rows `moved-names.toml` carries. Rollback is reverting the implementation
commit; no artifact or document needs rebuilding either way beyond the verdict
store's automatic reset.

## Open Questions

None at ratification (3 October 2026). Settled by the orchestrator: the
SolidPython-operand acceptance is kept through the engine, as proposed,
because a ratified requirement and machinome-mechanics' suite depend on
it; retiring it is a later decision for the pilot, taken with mechanics
migrated, and the modified requirement states the left-operand
degradation plainly. The brief's expression renderer at the engine's
address is not taken: the core's expression text is the core's own
serialization, which OpenSCAD reads, and routing it through the engine
would point the dependency the wrong way. `binary.py`'s name is cycle 7's.
The validation project is Pin_tumbler_lock, with the Curta's clocked
block and machinome-mechanics' suite as the two probes, all run by the
orchestrator.

## Deferred

- Cycle 6: the SCAD presentation behind `machinome.scad_engine` (the contract
  gains presentation and its version moves), `assemble()` and `develop`
  without it, and whether presentation wraps values explicitly.
- Cycle 7: `Solid2Node` and `OpenScadNode` as node modules over the engine,
  the runner, `Solid2Node.as_number`'s `type(n).__module__` check, the
  snapshot renderer, the `openscad` extra, `require_scad_engine` and its
  refusal naming the extra, and `node/base.py`'s, `viewers/openscad.py`'s and
  `manager/snapshot.py`'s direct reaches into `machinome.openscad.binary`.
- Cycle 8: the template.
- The studio's contract skill: no line changes this cycle (it names neither
  type nor module). Its "`Solid2Node.as_number()` resolves a solid2
  expression by running OpenSCAD" stays true until cycle 7.
- machinome-viewer's stray root `openscad.py`: a finding for that repository.
