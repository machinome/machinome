## Context

The first cycle of the lean-core campaign's phase "The next phase: the
architecture ready for the split" (`workflow/ongoing/lean-core.md`, pilot,
4 October 2026), gated by the acceptance scan the section "Locked at the
session's close" orders, and shaped by the ruling "Every node type is a
package": the OpenSCAD family is the node package `openscad`, `Solid2Node` is
the node package `solid2` over it, `machinome.openscad` is not an engine (it
decides no spatial question), and "the core mentions SCAD nowhere but in a
table of supported node types". Two rulings of the phase bind the design: the
leaf's capability flags become one declared set on the leaf base, and the
renderer architecture is the pilot's to revisit on this architecture, so this
cycle does the least that gets SCAD out of the core. A later ruling of the same
day narrows it: the OpenSCAD snapshot renderer does **not** move into the
package. Viewers become pluggable providers behind a seam `machinome.viewer`
(`machinome.viewer.openscad`, `machinome.viewer.web`), the phase's **last**
cycle, planned now and done after the root cleanup (pilot, 4 October 2026, via
the orchestrator). Here `machinome/viewers/openscad.py` stays at its address as
the OpenSCAD viewer's own module, an allowed zone of the gate, and reaches the
package directly; `viewers/browser.py` and `viewers/bundle.py` keep their
behaviour.

Precedents, all archived under `openspec/changes/archive/`: `lean-install`
(ADR-166 to 169: no class-name recognition, a kernel is an extra refused at
import, the command table names the module a command needs, a leaf type is one
module under `machinome.node`), `expression-type` (ADR-170, 171: the core's
symbolic value is its own type, the OpenSCAD engine at `machinome.openscad`),
`scad-presentation` (ADR-172, 173: the core describes its presentation, the
engine writes it, SCAD is written only where it is read, the pilot's option A),
`leaf-contract` (ADR-163 to 165: the four leaf bases are declared extension
points, versioned) and `mesh-engine` (ADR-176, the model of a provider behind a
seam).

Facts below were read in the bench at a16d45a on 4 October 2026 with the
workspace venv (solidpython2 2.1.3, Python 3.12.3), unless marked *inferred*.
Probes are under the session scratchpad, not in the bench.

### The family today, and who calls each piece

| today's address | what | called by |
|---|---|---|
| `machinome/node/openscad.py` | `OpenScadNode` (SolidPython's SCAD parser for `render`, own `scad_code`) | projects (4), the root export table |
| `machinome/node/solid2.py` | `Solid2Node`, `as_number` (SolidPython `scad_render`, the binary) | projects (16), the root export table, the template |
| `machinome/openscad/engine.py` | `adopt`, `scad_text`, `require_binary`, `CONTRACT = 2` | the seam only |
| `machinome/openscad/binary.py` | `openscad_binary`, `require_openscad`, `OpenScadUnavailable` | the engine, `node/solid2.py` |
| `machinome/scad_engine.py` | the seam: `scad_engine`, `require_scad_engine`, `ScadEngineUnavailable`, `ScadEngineIncompatible`, `CONTRACT`, `PROVIDER` | `node/base.py`, `expression_graph.py`, `viewers/openscad.py`, `manager/snapshot.py`, `openscad/binary.py` |
| `machinome/viewers/openscad.py` | `OpenScadRenderer` (`require_engine`, `present`, `withdraw`, `render`), `OpenScadImportError` | `manager/snapshot.py` |
| `node/base.py` | `scad_file`, `mesh_scad_file`, `fn`, `as_scad`, `scad_code`, `generate_scad`, `_publish_scad`, `_atomic_write_text`, `_scad_engine_for`, `_require_scad_engine`, `_model_for_own_scad`, `_uses_legacy_scad_materialization`, `scad_authored`, `_render_can_be_skipped`, and `generate_stl`'s OpenSCAD launch with `stl_builder_command(_for)` | the builder, the leaves, `model.py`, the renderer, tests |
| `node/leaf.py` | `LeafNode.as_scad` (raises), `scad_authored`, `_uses_legacy_scad_materialization`, `_render_can_be_skipped` | `node/base.py`, tests |
| `source_generation.py` | ADR-086's coalescing (`_PendingScadPublication` 47, `coalesces_scad` 361, `_pending_scad` 362, the flush in `__exit__` 382-393, `pending_scad_count` 398, `defer_scad` 401, `_flush_scad` 414) beside the generation census and the reuse record (`_scad_artifacts` 482, `has_scad_artifact` 597, `remember_scad_artifact` 603) | `node/base.py` `generate_scad` (1274-1290), the builder's phases |
| `core/builder.py` | the sweep's `collect_scad` (765), `scad_only` (691, 744, 826) | `Builder` |
| `core/expressions.py` | `scad_expression` (344): the closed scalar text | `GraphValue.__str__` (`expression_graph.py:136`), `bind_expressions` (388) |

The seam's only production resolver of `adopt` is `expression_graph.symbolic`
(`expression_graph.py:101`); `scad_text` is reached by `scad_code` (base,
`node/openscad.py`); `require_binary` by `generate_stl` and the renderer.

### Who reads a presentation

`assemble()` composes the core's description (`node/presentation.py`:
`ArtifactImport`, `Color`, `Rotate`, `Translate`, `Union`, `Authored`). Its only
reader that writes anything is the engine's `scad_text`, for a SCAD-authored
leaf's own `.scad` (from its materialization) and for the root's on-demand
`.scad` (the OpenSCAD snapshot renderer, ADR-173). `machinome snapshot` calls
`node.assemble()` for both renderers (`manager/snapshot.py:285`), and
`Sim(meshes=True)` calls it before `build_stls()` (`simulation/sim.py:215,
231`); the web renderer reads the published document and `build_stls()`
(`viewers/browser.py:40-43`), `Sim` reads meshes through `base_mesh`. So the
only effect `assemble()` has for those two callers beyond what `build_stls()`
does is a flexible leaf's per-binding snapshot STL (`FlexibleNode.as_scad`,
`node/flexible.py:299-337`), which only the root's SCAD imports: the loose end
"whose owner is undecided" of the plan's "State of the campaign".

### The capability probes today

The core asks a node what kind of thing it is through `getattr` with a
default at these sites (`grep` of `machinome/`, a16d45a):

| site | probe |
|---|---|
| `test.py:237` (`_routes_exact`) | `getattr(node, 'exact', False)` |
| `test.py:497` (`_fast_geometry`) | `getattr(node, 'flexible', False)` |
| `test.py:500` | `getattr(node, 'stl_file', None)` |
| `test.py:1984` (`_exact_identity`) | `getattr(node, 'flexible', False)` |
| `test.py:2002` (`_mesh_in_frame`) | `getattr(node, 'base_mesh', None)` |
| `core/builder.py:725` (`_artifacts_are_current`) | `getattr(node, 'exact', False)` |
| `core/builder.py:734` | `getattr(node, 'declared_markings', None)` |
| `core/builder.py:779` (`collect_scad`) | `getattr(node, 'scad_authored', False)` |
| `core/builder.py:782` | `getattr(node, 'children', ())` |
| `core/pieces.py:248` (`_project_relative_source`) | `getattr(node, 'src', None)` |
| `core/pieces.py:250` | `getattr(node, 'stl_file', repr(node))` |
| `core/serializer.py:964` (`marking_entries`) | `getattr(node, 'declared_markings', None)` |
| `node/declarative.py:1173` (marking guard) | `getattr(cls, 'rigid', False)`, `getattr(cls, 'flexible', False)` |
| `viewers/openscad.py:85` (`withdraw`) | `getattr(node, 'scad_authored', True)` |

Fourteen sites. The defaults exist for duck-typed stand-ins of the suite
(`core/serializer.py:959-963` says so: "a node DOUBLE ... is a stand-in for the
two or three attributes a producer reads"): `FakeNode` in
`tests/test_assertions.py`, `test_broad_phase_culling.py`,
`test_builder_lifecycle.py`, `test_connectivity.py`,
`test_intersection_memo.py` (with `MeshOnlyNode`, `ExactFakeNode`). Not
capability probes, and unchanged: `test.py:404` and `1985` (identity of an
override, `getattr(node.base_mesh, '__func__', None)`), `core/pieces.py:273`
(`_up_to_date`, currency), `node/assembly.py:804` (structure of a root walked
for a writer), `model.py:444` (an addressed attribute).

`optimize` is read directly (`node/base.py:923, 934, 937, 1041`,
`node/leaf.py:108, 118`); `as_scad` and `materialize` split the leaves by
override (`node/leaf.py:196-215`, the legacy path).

## Goals / Non-Goals

**Goals:**

- The scan of "The gate" passes: no `scad` in the core outside the family's
  package, the `solid2` module, the OpenSCAD viewer's module
  `machinome/viewers/openscad.py` and the table of supported node types.
- The OpenSCAD family is one package directory at its node type's address,
  with everything SCAD the core held but the OpenSCAD viewer, which the viewer
  cycle moves; `Solid2Node` is its own module over it.
- The core keeps only nameless mechanisms: a declared set of leaf
  capabilities, a presentation description, an expression language, a
  generation census, a sweep by declaration, an asynchronous render signal.
- `solidpython2` becomes the family's extra; a plain install writes no SCAD
  and imports no SolidPython.
- Every `.scad` the family writes, every node's SCAD text and the OpenSCAD
  snapshot's root text stay byte-identical; no document byte moves.

**Non-Goals:**

- `jscad` and `stl` as packages (the root cleanup's, plan "The three cycles").
- The `brep`/`mesh` rename: every `exact` and `faceted` word stays.
- The root cleanup: the node root keeps re-exporting its names.
- A renderer contract, renderer discovery, entry points (the pilot's).
- Moving the OpenSCAD snapshot renderer, or touching the web viewer's modules
  beyond their three mentions of the word (Decision 6): the viewer seam
  `machinome.viewer` is the phase's last cycle, by the pilot's decision.
- Cutting a distribution: the package directory is a portion-ready layout
  inside the one distribution.
- The licence, watchdog, the `.brep` sparing by kind in the sweep.

## Decisions

### 1. The gate: one scan, written red first, kept in the suite

`tests/test_core_names_no_scad.py` (provisional name), permanent. Its rule:

- **What is read.** Every file matching `machinome/**/*.py` in the
  distribution, the project templates included
  (`machinome/manager/templates/project/**`). For each file, its path relative
  to the repository, and every token Python's `tokenize` yields of type
  `NAME` (identifiers, attribute names, keywords), `STRING` (strings and
  docstrings, f-string literals included in Python 3.11's tokenizer) and
  `COMMENT`, plus `FSTRING_MIDDLE` where the running Python has it (3.12).
  Tokens cover what an AST walk would see of identifiers and attributes and
  also see comments, which the AST drops; the test also parses each module
  with `ast.parse` so a file that does not parse fails the gate rather than
  being skipped.
- **What is found.** Every case-insensitive occurrence of `scad` in that text.
- **The one exception.** An occurrence immediately preceded by `j` or `J` is
  JSCAD's own name, and passes, when that `j` begins a word: at the start of
  the text, after a character that is not a letter, or an upper-case `J`
  after a lower-case letter (a camel-case boundary). So `jscad`, `JSCAD`,
  `jscad_source`, `JScadNode`, `OpenJScadNode` and `machinome/node/jscad.py`
  pass; `openscad`, `OpenSCAD`, `.scad`, `scad_file`, `xscad`, `openjscad`
  (no boundary) and `cascade` (`ca`-`scad`-`e`) fail.
- **Where it may occur.** In the package `machinome/node/openscad/` (every
  file beneath it), the module `machinome/node/solid2.py`, the OpenSCAD
  viewer's module `machinome/viewers/openscad.py` (until the viewer cycle moves
  it behind `machinome.viewer`), and the module `machinome/node/supported.py`,
  which holds the one table of supported node types and nothing else that
  names a technology (Decision 6).
- **What it reports.** Every offending file with its count and the first
  offending tokens with their line numbers, so a failure says where.

Prototyped in the bench as a script (not pytest) on 4 October 2026. **Red on
the unmodified tree: 37 modules, 453 occurrences** (38 and 513 before the scope
reduction made `viewers/openscad.py`, 60 occurrences, an allowed zone). Per
module: `node/base.py` 97, `node/openscad.py` 41, `scad_engine.py` 40,
`manager/snapshot.py` 33, `node/leaf.py` 29, `openscad/engine.py` 24,
`source_generation.py` 24, `core/builder.py` 23, `openscad/binary.py` 17,
`math.py` 16, `expression_graph.py` 13, `node/flexible.py` 13,
`node/presentation.py` 13, `node/internal.py` 9, `core/expressions.py` 7,
`openscad/__init__.py` 7, `core/camera.py` 5, `node/exact_leaf.py` 4,
`node/stl.py` 4, `model.py` 3, `node/__init__.py` 3, `node/operations.py` 3,
`node/qualified.py` 3, `node/sources.py` 3, `parameters.py` 3,
`viewers/browser.py` 3, `node/jscad.py` 2 (`as_scad` and its docstring;
`JScadNode` passes), `node/sheet_leaf.py` 2, and one each in
`core/expression_parser.py`, `core/pieces.py`, `motion/couplings.py` (the word
`cascade`), `motion/joints.py`, `node/assembly.py`, `node/build123d.py`,
`node/cadquery.py`, `node/decorators.py`, `test.py`. The plan's "41 modules" is
`grep -il scad` over the same files: it also counts `node/solid2.py` and
`viewers/openscad.py` (allowed), `currency.py` and `vet/assertions.py`
(`JScadNode`, `JSCAD_SOURCE` only, which pass). The red count is re-measured by the applier as task 1.1 and recorded in
`evidence.md`.

Rejected: an exception list for `cascade` (one comment reworded is cheaper
than a second rule, and the rule as the pilot stated it fails `scad` inside any
other word); an AST-only scan (misses comments, which is where most of the
history of the word lives: `core/pieces.py:176`, `test.py:323`).

Not scanned, and stated: `machinome/vet/universe.toml` (data, not Python: it
admits `solid2` as a kernel, denies `solid2.scad_render_to_file` and
`save_as_scad`, and lists `scad_source` among source attributes; the vet
universe is "the one registry that genuinely has to learn about packages",
plan "Where the core reaches each kernel"); `pyproject.toml`; `docs/`; `tests/`.

### 2. The family is one package directory, `machinome/node/openscad/`

Layout (module names provisional, the pilot ratifies):

| tomorrow's address | holds | from today's | called by |
|---|---|---|---|
| `machinome.node.openscad` (`__init__.py`) | `require_extra('openscad', ...)` first; `OpenScadNode` | `node/openscad.py` | projects, the root export table (through the table of Decision 6) |
| `machinome.node.openscad.leaf` | `ScadLeafNode`, the family's leaf base: `fn`, `scad_file`, `scad_code`, `generate_scad()`, `present` (the authored object), `materialize` (writes its `.scad`), `generate_stl()` (launches OpenSCAD, raises `StlRenderStart`), `stl_builder_command(_for)`, `kept_artifacts()` = `(scad_file,)` | `node/base.py` (the SCAD members and the runner), `node/leaf.py` (`scad_authored`), `node/solid2.py` and `node/openscad.py` (`scad_authored`, `as_scad`, `materialize`) | `OpenScadNode`, `Solid2Node` |
| `machinome.node.openscad.writer` | `scad_text(description, fn=None)` (SolidPython), `scad_code(node)`, `generate_scad(node)` (publishes `<basepath>.scad` with the generation's reuse record, transient when the node does not keep it) | `openscad/engine.py` (`scad_text`), `node/base.py` (`scad_code`, `generate_scad`, `_publish_scad`) | the family leaves, the OpenSCAD viewer |
| `machinome.node.openscad.binary` | `openscad_binary`, `require_openscad`, `OpenScadUnavailable` (a `RuntimeError`, its message unchanged) | `openscad/binary.py` | the family leaves, `Solid2Node.as_number`, the OpenSCAD viewer |
| `machinome.viewers.openscad` (stays) | `OpenScadRenderer` (`present`, `render`, `withdraw`), `OpenScadImportError`, now importing the package's writer and binary directly, and taking the OpenSCAD branch of the snapshot command's error handling | itself; `manager/snapshot.py:224-245` | `manager/snapshot.py` through the table's provisional column |

`machinome/openscad/` (three modules), `machinome/scad_engine.py` and
`machinome/node/openscad.py` are deleted; `machinome/viewers/openscad.py` stays
(the scope reduction above).
Nothing re-exports or aliases them (ADR-169's one-path rule): an import of a
removed name fails with Python's own `ModuleNotFoundError` or "cannot import
name", as `exact-engine` and `expression-type` did. `_namespace_portions` keeps
a second copy of the core (the workspace's editable primary checkout) from
answering for a deleted module, since that copy ships its `__init__.py`
(`machinome/__init__.py:8-24`).

**`OpenScadNode` is defined in the package's `__init__`.** Its address is the
node type's, `machinome.node.openscad` (rule 1 of "Import paths"), and its
`__module__` stays `machinome.node.openscad`, so `from machinome.node.openscad
import OpenScadNode` keeps working and nothing that records a class's module
moves. A submodule `machinome.node.openscad.node` would have changed the one
path. The other members are submodules because they are not the node type.

**The seam `machinome.scad_engine` is dissolved, not renamed.** After the move
nothing in the core asks the family for SCAD text or the binary: `scad_code`,
`generate_scad()` and the runner are the family leaves' own members, the
OpenSCAD viewer imports the package's writer and binary itself, and adoption is
a hook (Decision 3). A seam whose
only remaining caller would be the package itself has no reason to exist.
Its contract version goes with it; ADR-162's check moves to no new place,
because the core resolves no provider of the family. The snapshot renderer
is reached through the table (Decision 6), which checks no version: a
viewer contract is the viewer cycle's.

**The writer keeps SolidPython; settled with evidence.** The brief asked
whether the description could be written without SolidPython, which would let
the `openscad` extra carry no Python dependency. The five core constructs
could be: `scad_render` writes them in a fixed shape (probed 4 October 2026:
`import(file = "a/b.stl", origin = [0, 0]);`, `color(alpha = 1, c = [...]) {`,
`rotate(a = 30, v = [0, 0, 1]) {`, `translate(v = [1, 2.5, 0]) {`,
`union() {`, children tab-indented, `union();` when empty). Two facts make a
SolidPython-free writer change bytes or behaviour:

1. **SolidPython's text depends on process-global state.** Its `use` and
   `include` registry is filled by every `import_scad` in the process, and
   `scad_render` prefixes every later rendering with it, whatever the tree.
   Probe: `scad_text` of `Translate((1, 2, 3), Union((ArtifactImport('a.stl'),
   ArtifactImport('b.stl'))))` gives 129 bytes, and after
   `solid2.import_scad('m.scad')` in the same process gives the same text
   preceded by `use <.../m.scad>;\n\n`. Pin_tumbler_lock's parts module calls
   `import_scad` at import (`simulation/parts.py:9`), so the root SCAD its
   OpenSCAD snapshot draws carries that line today (*inferred* from the probe;
   the capture of task 12.1 shows it); a writer of its own would
   drop it from the root's text and from any coloured or inlined authored
   leaf's text.
2. **`OpenScadNode`'s module call needs SolidPython's SCAD parser.**
   `render()` parses the `.scad` (`solid2.core.parse_scad.get_scad_file_as_dict`,
   a ply grammar) to learn each module's parameter names, so a positional
   argument is written by name and a wrong arity is refused: probe,
   `m(3, b=4.5)` over `module m(a, b=2)` writes `m(a = 3, b = 4.5);` and
   `m(3, 'x', True, [1, 2])` raises `TypeError: too many arguments to m(...)`.
   Without the parser, the node would have to ship a SCAD signature reader or
   write positional arguments (different bytes) and lose the arity check.

So the `openscad` extra installs SolidPython, both family modules import it,
and `solid2` is not the only SolidPython importer. The declaration goal still
holds: `machinome[openscad]` and `machinome[solid2]` are distinct extras, and a
project's extras say which node types it uses. A SolidPython-free OpenSCAD
package is recorded in Open Questions with its cost.

### 3. `Solid2Node` is `machinome.node.solid2` over the package

`machinome/node/solid2.py` calls `require_extra('solid2', 'machinome.node.solid2
(Solid2Node)', 'solid2')` first, then imports SolidPython and the package. It
holds `Solid2Node(ScadLeafNode)` with `namespace = 'solid2'` and `as_number`
(OpenSCAD evaluation of a SolidPython value through
`machinome.node.openscad.binary.require_openscad`, unchanged), and `adopt`, the
function the engine provided (`openscad/engine.py:39-71`, unchanged), which it
registers with `machinome.expression_graph.register_adopter(adopt)` at import.

**The expression graph adopts a foreign value through registered adopters.**
`machinome.expression_graph` gains `register_adopter(adopt)` (idempotent, by
identity) and keeps a module-level tuple of adopters; `symbolic(value)` decides
plain numbers, `GraphValue` and `ExpressionNode` first, as today
(`expression_graph.py:88-104`), then asks each adopter in registration order and
returns the first node, else `None`. Without an adopter no foreign value is
symbolic, which is today's behaviour without the engine (`scad-engine-dependency`,
"A SolidPython value without the engine"). `math.py`'s `_is_symbolic` keeps
going through `symbolic`.

Rejected: the table of supported node types naming an adopter, consulted when
an unknown value arrives (a third reach beyond renderer and command, which the
ruling's "and nothing more" excludes); an import of `machinome.node.solid2` by
the core when SolidPython is importable (the core naming a package to adopt
its values is the seam again).

The consequence, a behaviour change: a SolidPython value is adopted only in a
process that imported `machinome.node.solid2`. A project using `Solid2Node`
always has (its class lives there; the root export imports the module on first
access). One that passes `solid2.get_animation_time()` to machinome math
without any `Solid2Node` would see its value refused as a non-expression;
machinome-mechanics' twelve test files do exactly that (`tests/test_rolling.py:8,
31`). Open Questions.

### 4. What the core keeps is nameless

**(a) A leaf declares the artifacts it keeps; the sweep keeps by declaration.**
`kept_artifacts()` on the node base returns `()`; `ScadLeafNode` returns its
`scad_file`. The builder's `_sweep_unreferenced_artifacts` collects, beside the
document's references, `kept_artifacts()` of every node of the tree it published
(`collect_scad` becomes `collect_kept`, reading `node.kept_artifacts()` and
`node.children` directly), and keeps a file because a node declares it, never by
its suffix. `scad_only` goes, with the branch at `core/builder.py:685-692`, and
what that branch did survives as a rule that names nothing: **an artifact
published as transient never survives a build.** The root's on-demand `.scad`
is the one artifact a process writes into the build directory for its own
single use (the OpenSCAD viewer's `present`, which `render` removes in a
`finally`); only a killed process leaves it. Its writer declares that in the
artifact's currency record: `currency.record` and `currency.publish` take
`transient=False`, and a transient record carries `"transient": true` beside
its digest, fingerprint and recipe (version 3 of the record, one optional key;
`_recorded_source` reads it, `recorded_transient(artifact)` answers it; a
record without the key is not transient). The writer's `generate_scad(node)`
publishes as transient when the node does not list the file in its
`kept_artifacts()` (a SCAD-authored root's own `.scad` is kept, and the
renderer's `withdraw` leaves it); every other publication is as today. The
builder's sweep then has two passes with one vocabulary: on every successful
build, changed document or not, it removes every file of the build directory
whose record marks it transient, with its record; on a changed document it
also removes every unreferenced file as before. The `.scad` rule of the
`scad-presentation` correction of 4 October (a build whose document is
unchanged still removes every `.scad` no current node writes) is thereby kept
in effect for the one file it was made for, without the core recognising a
`.scad`: the pilot's choice of 4 October 2026 among the three shapes the
orchestrator put to the pilot (this one; a nameless sweep that does nothing on
an unchanged document, leaving a killed snapshot's root `.scad` until the next
snapshot or document change; a suffix rule derived from the declared kinds).
Sweeping every unreferenced file on every build stays rejected (it removes
what `machinome test` wrote for other parameter sets). `.brep`, locks and
temporaries keep their sparing by kind (not this cycle's).

**(b) A presentation is the core's description; the core writes none.**
`node/presentation.py` keeps its six types, `described` and `reanchored`,
worded for what they are: a node's presentation, which an installed package may
write. `as_scad` becomes **`present(rendered)`** on the bases, and
`_model_for_own_scad` becomes **`presentation()`**, public because the writer
needs it ("this node's own presentation, its artifact imports resolving from its
own build directory", ADR-116 unchanged). `LeafNode.present` gets a default,
the body every native leaf repeats today (`exact_leaf.py:159-165`,
`stl.py:176-181`, `jscad.py:94-100`): materialize when the STL is not current,
then return `artifact_import(self.local_stl)`; those three overrides are deleted
and their behaviour is the default's. `InternalNode.present(children)` and
`FlexibleNode.present(rendered)` keep their bodies. `assemble()` keeps its
template and returns the description; no project uses its return value (plan,
grep of 3 October 2026, 210 files).

**(c) The expression modules are machinome's expression language.**
`math.py`, `expression_graph.py`, `core/expressions.py` and
`core/expression_parser.py` are documented as machinome's expression language,
which the viewer evaluates, in degrees, with `let` closures for sharing, and
whose builtins are the ones `SYMBOLIC_BUILTINS` lists; that its syntax was
inherited from OpenSCAD is history for the ADR, not a fact the code needs.
`scad_expression` is renamed `closed_expression` in place (Decision 7).

**(d) The generation census stays; ADR-086's coalescing goes with its
producer.** Verified in the code (`source_generation.py`): the census
(`SourceCensus`, 128-293), the phases, the import guard and the reuse record are
used by every build; the coalescing (`_PendingScadPublication` 47-56,
`coalesces_scad` and `_pending_scad` 361-362, the pre-flush/post-flush branch of
`__exit__` 382-386 and its clearing 393, `pending_scad_count` 397-399,
`defer_scad` 401-412, `_flush_scad` 414-420) has one producer,
`generate_scad`'s branch for a non-rigid, non-flexible node inside the
`assembly` phase (`node/base.py:1281-1287`). Since ADR-173 no build calls
`generate_scad` on an assembly (the builder composes no presentation), so the
branch has no production caller; only `tests/test_generation_dedup.py` drives it.
The coalescing and its branch go; the `assembly` phase's exit checkpoints
`assembly post` like every other phase (it checkpointed `assembly pre-flush` and
`assembly post-flush`). The reuse record stays, renamed for what it records:
`_scad_artifacts` → `_published`, `has_scad_artifact` → `has_published`,
`remember_scad_artifact` → `remember_published`; the writer's `generate_scad`
uses it as today. The byte-identical text publication `_atomic_write_text`
(`node/base.py:52-81`), whose one caller is the SCAD publication, moves to
`machinome.currency.publish_text`, beside `currency.publish`: it is a currency
rule (`build-pipeline`, "Unchanged text is not replaced"), not a SCAD one.

**(e) The template scaffolds the leaf kind the installed extras provide.**
`machinome/manager/templates/project/root/__init__.py` becomes two templates,
`root/solid2.py` (today's text, byte for byte) and `root/cadquery.py` (the same
part in CadQuery: a 50 mm cube centred on the Z axis and standing on the XY
plane, less a radius-10 cylinder along Z). `machinome new` takes the first of `solid2`, `cadquery` whose module
imports (through the table, Decision 6; a refusal `ExtraUnavailable` means
absent), so an installation with SolidPython keeps today's output byte for
byte, an installation with only `[cadquery]` (the manual's tutorial route,
`docs/start/install.rst`) gets a CadQuery part, and one with neither is refused
before anything is written (Decision 8, text R8). The templates no longer form
a Python package (`root/__init__.py` made `machinome.manager.templates.project.root`
importable and importing SolidPython); `MANIFEST.in` already ships the
directory. The `solid2` template is the core's last SolidPython importer outside
the family, as the plan says.

**(f) Every `.scad` is the package's.** As the orchestrator corrected on
4 October: a build writes `.scad` only for a family leaf (its own, from which
OpenSCAD renders its STL), and the root's `.scad` exists only while the
OpenSCAD renderer draws it (ADR-173, option A). A CadQuery-only build already
writes none (cycle 6's OpenAstroMount leg: 90 STL, 90 BREP, no `.scad`). What
changes is the owner: the family leaf's materialization and the OpenSCAD
viewer write them through `machinome.node.openscad.writer`, and nothing in
the core writes SCAD. No build output changes.

### 5. The capability flags become one declared set on the leaf base

The set is what the core asks a node of a leaf kind, declared once, with a
default on the node base so every node answers, and documented together on
`LeafNode` with the contract's meaning (the `leaf-contract` delta, "A leaf
declares its kind as one set"):

| member | form | meaning | default |
|---|---|---|---|
| `rigid` | class attribute, `bool` | a time-invariant solid with a cached STL, in the piece and artifact sets | `True`; `False` on `FlexibleNode`, `AssemblyNode` |
| `flexible` | class attribute, `bool` | its shape is a function of its bound ports; published as a flexible object | `False`; `True` on `FlexibleNode` |
| `exact` | property, `bool` | exposes boundary-representation geometry through `shape()` | `False`; `True` on `ExactLeafNode`; all children on `InternalNode` |
| `optimize` | class attribute, `bool` | a presentation imports the leaf's STL (`True`) or carries what it rendered (`False`); a `False` leaf is prepared on every build | `True` |
| `present(rendered)` | method | the leaf's presentation of one render | `LeafNode`: materialize if stale, import its own STL |
| `kept_artifacts()` | method → tuple of paths | the artifacts beyond its `.stl`, `.brep` and markings that a build keeps for it | `()`; the family's `.scad` |
| `generate_stl()` | method | make the STL current: a rigid leaf whose STL is still not current after its materialization is refused (Decision 9); a leaf rendering in a subprocess starts it and raises `StlRenderStart` | the refusal |
| `stl_file`, `brep_file`, `basepath`, `local_stl` | instance attributes | its artifact paths | set by the constructor |
| `base_mesh()` | method | its geometry in its own frame | the cached STL; `FlexibleNode` evaluates |
| `declared_markings()` | method | its declared markings | the class's |

No member names a technology. `scad_authored` is `kept_artifacts()`; the
`as_scad`/`materialize` split (`_uses_legacy_scad_materialization`) goes: every
leaf produces its STL in `materialize` or `generate_stl`, and presents through
`present`.

Every probe of "The capability probes today" becomes a direct read:

| site | becomes |
|---|---|
| `test.py:237` | `node.exact` |
| `test.py:497`, `1984` | `node.flexible` |
| `test.py:500` | `node.stl_file`; `None` means a stand-in with no artifact |
| `test.py:2002` | `node.base_mesh`; `None` means a stand-in whose `mesh` is already placed |
| `core/builder.py:725` | `node.exact` |
| `core/builder.py:734`, `core/serializer.py:964` | `node.declared_markings` |
| `core/builder.py:779` | `node.kept_artifacts()` |
| `core/builder.py:782` | `node.children` |
| `core/pieces.py:248`, `250` | `node.src`; the `stl_file`/`repr` fallback goes (every node has `src`, `node/base.py:707`) |
| `node/declarative.py:1173` | `cls.rigid`, `cls.flexible` (declared on the base `NodeMeta` creates every node class from) |
| `viewers/openscad.py:85` | in the OpenSCAD viewer's module (an allowed zone, not the core's reading): `withdraw` keeps the file when the root lists it in `kept_artifacts()` |

The suite's duck-typed stand-ins then declare the set: a shared mixin
`tests/stand_in.py` (`exact = False`, `flexible = False`, `stl_file = None`,
`base_mesh = None`, `children = ()`, `src = None` where a producer reads it, and
`declared_markings` returning `{}`), from which every stand-in derives. The
test framework's own wording ("test doubles implementing only `.mesh`") stays
true: a stand-in declaring no artifact and no base mesh exposes only `.mesh`;
`test-framework` needs no delta. A permanent test pins the rule: an AST scan of
`machinome/` finds no `getattr(x, '<member>', <default>)` and no
`hasattr(x, '<member>')` for a member of the set.

Rejected: a literal `capabilities = frozenset({...})` attribute (a string
registry the core would test membership of; `exact` on `InternalNode` is
computed from its children and `rigid` and `flexible` are read by the
serializer as attributes, so it would change every reader for no new
guarantee); a nominal split of the test framework's input (`isinstance(node,
AbstractBaseNode)` or mesh-only), which keeps the probes' defaults out of the
code but turns the culling and memo stand-ins that expose an `stl_file`
(`test_broad_phase_culling.py:57`, `test_intersection_memo.py:59`) into mesh-only
ones and rewrites what those tests prove.

**The leaf contract goes to `CONTRACT = 2`** (`machinome.node.leaf.CONTRACT`,
ADR-163, 165: a removed member or a changed meaning changes the number). Removed
from `LeafNode`'s declared members: `as_scad`, `scad_file`, `generate_scad`.
Added: `present`, `presentation`, `kept_artifacts`, `generate_stl`, `rigid`,
`flexible`, `exact`, `optimize`, `base_mesh`, `declared_markings`, and
`StlRenderStart` as the signal a subprocess render raises. Changed meaning:
`generate_stl` no longer launches OpenSCAD for a rigid leaf whose STL is not
current. A class declaring `leaf_contract = 1` is refused at creation, naming 1,
2 and `machinome.node.leaf` (ADR-165, unchanged): machinome-freecad's
`lean-core-validation` branch declares 1 (`machinome_freecad/adapter.py:143`)
and its retarget declares 2.

### 6. The table of supported node types: a second table, `machinome.node.supported`

**Evidence for a second table rather than ADR-168's extended.** `cli.COMMANDS`
(`cli.py:34-46`) is keyed by command name, its rows are the core's command
modules and its third column names a module a command needs; it is read by the
CLI only. A renderer is not a command, and the snapshot command chooses among
renderers after it is dispatched. Extending it would put `openscad` into
`cli.py`, making the whole CLI an allowed module of the scan. The node root's
export table (`node/__init__.py:70-91`) already maps node-type class names to
their modules (`'OpenScadNode': 'openscad'` is one of its three offending
tokens) and is struck by the root cleanup; the names it resolves for node types
then become refusals naming each module, which still need the node types'
class names. One table of node types, read by the export table, the CLI and the
snapshot command, serves all three, and holds the only `openscad` the core
spells.

**Location: `machinome/node/supported.py`**, a module of the node package that is
not a node type (as `base`, `frames`, `markings`, `declarative` are; no node
type will be called `supported`). Its content is the table and the three
functions that read it, nothing else:

```python
@dataclass(frozen=True)
class NodeType:
    classes: tuple[str, ...]           # the names the node root resolves
    renderers: tuple[tuple[str, str], ...] = ()   # provisional: (renderer name, 'module.Class')
    commands: tuple[str, ...] = ()     # CLI commands that need this node type's module

NODE_TYPES = {
    'cadquery': NodeType(('CadQueryNode',)),
    'build123d': NodeType(('Build123dNode', 'Build123dSheetNode')),
    'step': NodeType(('StepNode',), commands=('import-step',)),
    'molejo': NodeType(('MolejoNode',)),
    'solid2': NodeType(('Solid2Node',)),
    'openscad': NodeType(('OpenScadNode',),
                         renderers=(('openscad',
                                     'machinome.viewers.openscad.OpenScadRenderer'),)),
    'jscad': NodeType(('JScadNode',)),
    'stl': NodeType(('StlNode',)),
}
DEFAULT_RENDERER = 'openscad'

def load(key): ...        # import machinome.node.<key>; a refusal names machinome[<key>]
def renderer(name): ...   # the renderer instance a table row contributes, or the refusal
def needed_by(command): ...  # the node type a command needs, or None
```

The address and the extra of a node type are not stored: they are
`machinome.node.<key>` and `machinome[<key>]` by rules 1 and 2 of "Import
paths". `load` imports the module; a module that refuses its kernel raises its
own `ExtraUnavailable` (ADR-167), and a module that cannot be found at all (a
package not installed, layer 2) is refused the same way, `ExtraUnavailable(key,
'the <key> node type (<classes>)', 'machinome.node.<key>')`, so every caller
answers both layers with one `except`.

Its readers:

- **The node root** (`node/__init__.py`): its export table keeps the non-node
  names (`AssemblyNode`, `declared_children`, `FusionNode`, `SheetLeafNode`,
  `FlexibleNode`, the markings, `Frame`, `property_as_number`) and takes each
  node type's class names from `NODE_TYPES`, resolving them from
  `machinome.node.<key>` as today. Same names, same objects.
- **The snapshot command**: `--renderer` takes `choices=['web',
  *renderer names]` and `default=DEFAULT_RENDERER`; for a name other than
  `web` it calls `supported.renderer(name)` before loading the node, and
  answers an `ExtraUnavailable` with text R4 (Decision 8) and exit 1. The
  renderer's `present(node)` runs inside the build lock after posing (it
  assembles and writes the root's `.scad`), `render(node, args, output, run)`
  after it, reporting its own failures as the command did (the OpenSCAD branch
  of `handle()`, `manager/snapshot.py:224-245`, moves into
  `machinome/viewers/openscad.py` verbatim: an unopenable import removes the
  partial image; a process failure, a missing executable and the binary's
  refusal each write their line and exit 1). The renderer's address is the
  table's **provisional column**: the viewer cycle replaces it with the seam
  `machinome.viewer` and removes the column.
- **The CLI**: `COMMANDS['import-step']`'s third column becomes the node type
  `'step'` (`supported.needed_by('import-step')` names it, and a test pins that
  the two agree); `require_needed_module` calls `supported.load(key)` and keeps
  its message (ADR-168, text R9). `manager/import_step.py` takes
  `StepAssembly` from `supported.load('step')`. `cli.py` and
  `manager/import_step.py` no longer spell `machinome.node.step`.
- **`machinome new`**: `supported.load(key)` for `solid2`, then `cadquery`
  (Decision 4e).

**Provisional, and already decided to be temporary.** The pilot ruled on
4 October 2026 that viewers become pluggable providers behind a seam
`machinome.viewer` (`machinome.viewer.openscad`, `machinome.viewer.web`,
symmetric), the phase's last cycle, planned now and done after the root
cleanup; this cycle leaves the OpenSCAD renderer at `machinome.viewers.openscad`
for it and gives the table only the column that cycle removes. This is the
least that keeps the core nameless; it is not a renderer architecture. What the renderers'
lack of a contract looks like after this change, recorded for the pilot's
revisit: the OpenSCAD renderer answers `present(node)` and `render(node, args,
output, runner)` (its `withdraw` is internal; `require_engine` is gone, its
refusal now the module's import refusal); the web renderer, `BrowserRenderer`,
answers `render(node, args, output)` and `capture(...)`; `manager/snapshot.py`
still compares the string `'web'`, still owns options only the OpenSCAD
renderer reads (`--projection`, `--colorscheme`, `--view`, `--render`,
`--preview`, worded without the technology's name) and the web renderer's
refusal of them, and imports `BrowserRenderer` by name. `viewers/browser.py`
and `viewers/bundle.py` keep their behaviour; `browser.py`'s three mentions of
the word (its module docstring, a docstring, and the refusal's suggestion
`--renderer openscad`, which becomes `--renderer {DEFAULT_RENDERER}` read from
the table) are the only edit there, because the gate admits no exception for
it (Open Questions). No version is checked on
a renderer, no entry point or portion is discovered, and no protocol class
exists.

### 7. `scad_expression` is renamed in place, not moved to the package

The brief places `scad_expression` in the package. The code contradicts it:
`scad_expression` is the core's `str()` of every symbolic value
(`GraphValue.__str__`, `expression_graph.py:135-140`), which the standalone
operation form, the clocked identity, diagnostics and the published document's
verbatim originals (`core/expressions.py:388`) all read, with or without the
family installed. Moving it would leave the core without the text of its own
values. It is renamed `closed_expression(root)` in `machinome.core.expressions`
("the closed text of an expression: one scalar, its shared subexpressions bound
by `let`"), and the writer obtains it, as today, through `str()` of the value
SolidPython is handed (ADR-172, Decision 7 of `scad-presentation`). Recorded in
Open Questions for ratification.

### 8. Extras, dependencies, the three doors, and the refusal texts

`pyproject.toml`: `solidpython2==2.1.*` leaves `dependencies`; new extras
`openscad = ["solidpython2==2.1.*"]` and `solid2 = ["machinome[openscad]"]` (as
`[cadquery]` includes `[occt]`); `all` adds `openscad,solid2`; `dev` takes
`all` (unchanged). `requirements.txt` keeps naming SolidPython for CI;
`tox.ini` installs `all` (unchanged); `setup.cfg` ignores E402 for the two new
kernel modules as for the others. `machinome/extras.py` gains no row: it holds
no table by design ("No table here maps a module to its extra: each module
states its own"), and the two modules state theirs by calling `require_extra`
as ADR-167 shaped every kernel module.

The three doors (ADR-167):

1. **The module refuses at import.** `machinome.node.openscad` (so every
   submodule) and `machinome.node.solid2` call `require_extra` first, before
   importing SolidPython or each other.
2. **A caller reads that as absent.** The node root re-raises it unmodified
   (`node/__init__.py:131-132`, unchanged); `supported.load` raises it to its
   readers; `machinome new` treats it as "not installed".
3. **A command refuses at its start.** `machinome snapshot` (default or
   `--renderer openscad`) before loading the node; `import-step` before parsing.

Refusal texts, verbatim (`{...}` filled per node):

- **R1**, `import machinome.node.openscad` without SolidPython:
  `machinome.node.openscad (OpenScadNode and the OpenSCAD writer) needs solid2, which is not installed; install it with 'pip install "machinome[openscad]"'`
- **R2**, `import machinome.node.solid2` without SolidPython:
  `machinome.node.solid2 (Solid2Node) needs solid2, which is not installed; install it with 'pip install "machinome[solid2]"'`
- **R3**, `supported.load('openscad')`, or the table's resolution of the
  `openscad` renderer, when the package itself cannot be found:
  `the openscad node type (OpenScadNode) needs machinome.node.openscad, which is not installed; install it with 'pip install "machinome[openscad]"'`
- **R4**, `machinome snapshot` with the OpenSCAD renderer and R1 or R3, on
  standard error, exit 1, nothing loaded or written:
  `Error: machinome snapshot --renderer openscad needs the openscad extra: {R1 or R3}; or use --renderer web`
- **R5**, the binary missing when the renderer launches it (unchanged):
  `Error: the OpenSCAD snapshot renderer requires the OpenSCAD binary because rendering the requested image launches OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH, or use --renderer web`
- **R6**, the binary missing for a family leaf's STL (unchanged):
  `node housing (FacetedBox) requires the OpenSCAD binary because its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH`
- **R7**, a rigid leaf whose STL is not current after its materialization,
  `ArtifactNotProduced(RuntimeError)` from `generate_stl`, before any process:
  `node {name} ({qualname}) produced no STL: its materialization published nothing at {stl_file}`
- **R8**, `machinome new` with neither `solid2` nor `cadquery` importable, exit
  1, nothing created:
  `Error: machinome new scaffolds its first part with SolidPython or CadQuery, and neither is installed; install one with 'pip install "machinome[solid2]"' or 'pip install "machinome[cadquery]"'`
- **R9**, `import-step` without its extra (unchanged, ADR-168):
  `Error: machinome import-step needs the step extra: machinome.node.step (StepNode, StepAssembly) needs cadquery, which is not installed; install it with 'pip install "machinome[step]"'`

The brief asked the OpenSCAD renderer to refuse "naming `machinome[openscad]`
when the package or the binary is absent". For the package it does (R4). For
the binary it keeps R5: no extra installs an executable, and naming one that
cannot provide it is the "install line that installs nothing" `expression-type`
rejected. Open Questions.

### 9. The STL runner leaves the base; a leaf that produced no STL is refused

`AbstractBaseNode.generate_stl` (`node/base.py:1321-1352`) launches OpenSCAD on
`self.scad_file` for any rigid, unlocked node whose STL is not current. It moves
to `ScadLeafNode.generate_stl`, unchanged (the binary through
`machinome.node.openscad.binary.require_openscad`, the command
`stl_builder_command_for`, the lock file, `StlRenderStart`). The base keeps the
three early returns (current, not rigid, locked) and then raises R7. Its only
callers reaching that point today are a leaf whose materialization published
nothing, which the `backend-switch` cycle recorded as a wart (`workflow/warts.md`,
"A self-materializing leaf that publishes nothing falls through to the OpenSCAD
path": `JScadNode.materialize`'s `if not os.path.exists(temporary): return`),
and a rigid internal node that is not a `FusionNode`, which no core type is.
`StlRenderStart` stays in the core (`node/base.py:1715`), generic: a leaf that
renders in a subprocess raises it and the builder waits (`core/builder.py:594`).
`FusionNode.generate_stl` is unchanged.

### 10. `--renderer web` and `Sim(meshes=True)` no longer compose a presentation

`manager/snapshot.py:_load_and_prepare_node` calls `node.assemble()` only through
the table renderer's `present(node)`; `--renderer web` keeps what
`BrowserRenderer.render` does under the lock, `build_stls()` and the staged
document. `simulation/sim.py:215-216, 231-232` drop `node.assemble()` and keep
`node.build_stls()`, which prepares the tree (`trigger_stl` → `_prepare` →
`InternalNode.materialize`, which links children and unions their sources as
`present` does). The per-binding snapshot STL of a flexible leaf is therefore
written only where a presentation is composed: by the OpenSCAD renderer's root,
by a caller's `assemble()`, `presentation()` or `scad_code`. Its owner is the
presentation, nameless. Rejected: moving the snapshot STL's production into the
package (the package would call `FlexibleNode`'s evaluation and publication from
outside, reaching a non-declared path).

### 11. Bytes

By construction, and pinned:

- **The family's `.scad` and every node's SCAD text**: the writer is the
  engine's `scad_text`, moved unchanged; the leaf's `scad_code` and the root's
  on-demand text compose the same description (`presentation()` is
  `_model_for_own_scad` renamed). `tests/scad_presentation_golden.py --check` and
  `tests/expression_type_golden.py --check` pass unchanged, their scripts
  repointed from `node.scad_code` to `machinome.node.openscad.writer.scad_code(node)`
  for non-family nodes (task 6.5).
- **`OpenScadNode`'s module, uniq ids, artifact names, recipe identities**:
  unchanged, its `__module__` unchanged (Decision 2).
- **The leaf-contract golden** (`tests/leaf_contract_golden.py --check`):
  unchanged hashes, uniq ids and records for every leaf, `Solid2Node` and
  `OpenScadNode` included.
- **Documents**: no serializer change; the document version does not move.
- **Pin_tumbler_lock**: its 11 `parts-*.scad` hashes, the root text of an
  OpenSCAD snapshot (6916 bytes, 20 imports in the cycle 6 evidence), its 2573
  faceted verdicts (Decision 14).

### 12. Specs: two removed, one new, fourteen modified

`openscad-engine` and `scad-engine-dependency` describe a package and a seam that
no longer exist; their surviving content (the writer's bytes, adoption, the
binary at its address, the refusals) moves to the new capability
`openscad-node`. OpenSpec 1.6.0 records a removal of requirements with
`## REMOVED Requirements`, but its archive validates every rebuilt spec before
writing and a spec must keep at least one requirement (`dist/core/archive.js`,
"Validate every rebuilt spec before writing any of them";
`dist/core/schemas/spec.schema.js`, `.min(1, SPEC_NO_REQUIREMENTS)`), so a delta
removing every requirement of a capability aborts the archive. This change
therefore carries no delta for the two, and the archive task deletes
`openspec/specs/openscad-engine/` and `openspec/specs/scad-engine-dependency/`
with `git rm` after `openspec archive`, checking that no other spec names them;
the precedent is `web-viewer`, removed from `openspec/specs/` while its last
delta stayed in `2026-08-02-dev-viewer-on-shared-package`. Modified
requirements keep every scenario name, with content rewritten where the name's
subject changed (OpenSpec refuses to drop a scenario through MODIFIED,
`dist/core/specs-apply.js:219-221`). `openscad-dependency` is kept (the binary
contract) and modified. `test-framework`, `exact-geometry`, `export`,
`cli-startup-cost`, `model-consumption`, `mesh-engine-dependency`,
`printed-pieces`, `simulation`, `step-import` and `user-documentation` mention
SCAD in requirements whose behaviour does not change (history, OpenSCAD as a
technology, its camera notation, "SCAD presentation" as a phrase) and get no
delta; the `brep`/`mesh` rename cycle renames spec names.

### 13. Proof, red first

Each red assertion and why it is red on the unmodified tree:

1. The gate (Decision 1): 37 modules offend.
2. `tests/test_openscad_node.py`: `machinome.node.openscad.writer.scad_text`,
   `.binary.require_openscad` and `.leaf.ScadLeafNode` import (red: no such
   modules); `machinome.viewers.openscad` imports neither `machinome.scad_engine`
   nor `machinome.openscad` and, with `solid2` blocked, raises R1 at import (red:
   it imports the seam and imports with SolidPython absent); `OpenScadNode.__module__
   == 'machinome.node.openscad'` and `issubclass(OpenScadNode, ScadLeafNode)`
   and `issubclass(Solid2Node, ScadLeafNode)` (red: no base); `import
   machinome.openscad` and `machinome.scad_engine` raise `ModuleNotFoundError`
   (red: they exist).
3. With `solid2` blocked by a finder: importing `machinome.node.openscad` and
   `machinome.node.solid2` raise `ExtraUnavailable` with R1 and R2 (red: today
   `ModuleNotFoundError: solid2` with no extra); `from machinome.node import
   Solid2Node` carries R2 (red likewise); in a fresh interpreter, importing
   `machinome.node`, `machinome.node.base`, `machinome.core.builder` and
   `machinome.test`, and assembling and building an `StlNode` assembly, leaves
   no SolidPython module (`solid2`, `solid2.*`) and no module that is or lies
   under `machinome.scad_engine`, `machinome.openscad` or
   `machinome.node.openscad` in `sys.modules` (red: probed 4 October 2026, the
   four imports leave `machinome.scad_engine` loaded, through `node/base.py:21`
   and `expression_graph.py:29`; matched by module name, not by substring,
   since trimesh's own `trimesh.exchange.cascade` is loaded too).
4. The metadata: `solidpython2` absent from `Requires-Dist` without extra,
   `openscad` and `solid2` extras present, `solid2` includes `openscad`, `all`
   includes both (red: required today, no such extras).
5. `machinome snapshot` with the family blocked: R4, exit 1, the node not
   loaded (red: today `ScadEngineUnavailable`'s text naming `pip install
   solidpython2`).
6. The declared set: `LeafNode.present` returns `artifact_import(local_stl)`
   for a self-materializing leaf; `kept_artifacts()` is `()` on the base and
   `(scad_file,)` on a family leaf; `CONTRACT == 2`; a class declaring
   `leaf_contract = 1` is refused naming 1 and 2; the AST probe scan of
   Decision 5 finds none of the fourteen sites (red: `present`,
   `kept_artifacts` do not exist, `CONTRACT` is 1, the scan finds fourteen).
7. R7: a `LeafNode` subclass whose `materialize` publishes nothing raises
   `ArtifactNotProduced` from `build_stls()` naming it, with `openscad` on the
   PATH patched to a sentinel never called (red: today it reaches
   `require_binary`/`Popen`).
8. The sweep: a build of a tree with a family leaf whose STL is current keeps
   its `.scad` with no suffix rule (the test removes `.scad` from every
   suffix list it can reach by patching `kept_artifacts` to `()` and asserts the
   file goes); a file published with `transient=True` is removed, with its
   record, by a build that publishes an unchanged document, while an
   unreferenced file whose record is not transient stays (red: today
   `collect_scad` keeps it by `scad_authored` whatever `kept_artifacts` says,
   `currency.record` takes no `transient`, `recorded_transient` does not
   exist, and the unchanged-document pass removes by the `.scad` suffix).
9. Coalescing gone: `SourcePhase` has no `defer_scad`; the `assembly` phase
   checkpoints `assembly post` (red).
10. Adoption: in a fresh interpreter, `machinome.expression_graph.symbolic(
    solid2.get_animation_time())` is `None` until `machinome.node.solid2` is
    imported, and a `$t` name node after (red: today it resolves through the seam
    without the import).
11. `closed_expression` exists and `str(GraphValue)` equals it (red: no such name).
12. The table: `NODE_TYPES` names eight node types; the root export table
    resolves the same names to the same objects as before; `COMMANDS` names no
    `machinome.node.` module; `--renderer` choices are `web` plus the table's
    (red: no module).
13. `machinome new` with `solid2` blocked and `cadquery` present writes the
    CadQuery template; with both blocked prints R8 and writes nothing (red).
14. `--renderer web` and `Sim(meshes=True)` do not call `assemble()` (patched to
    raise; red).

### 14. Empirical validation (the orchestrator runs every leg)

Run against the bench after the suite, one project at a time (virtiofs):

- **Deep, `Locks/Pin_tumbler_lock`** (OpenSCAD-authored `Solid2Node` parts,
  `import_scad`, a flexible spring, a running root). Before (bench at a16d45a)
  and after, in fresh build directories: the 11 `parts-*.scad` files'
  SHA-256 identical; `machinome test --faceted` verdict logs byte-identical
  (2573 verdicts, 24/24 in the mesh-engine evidence); `manifest.json`
  identical but OpenSCAD's own STL noise; a `machinome snapshot --renderer
  openscad` whose root `.scad` is captured before removal (a wrapper renderer
  copying the file) is byte-identical to the before-run's capture, and is gone
  afterwards; the image is written.
- **Deep, `3D-Printers/Prusa3-vanilla`** (the heaviest faceted user): 16 passed,
  3 failed (pre-existing) before and after, its 15935 verdicts byte-identical.
- **Deep, OpenAstroMount, CadQuery and STEP only**, with `solid2`,
  `machinome.node.openscad` and `machinome.node.solid2` made unfindable (the
  finder the earlier legs used) and an audit hook recording import attempts:
  `machinome build` writes 90 STL, 90 BREP and zero `.scad`; no import of any of
  the three is attempted; `machinome test` reaches the same verdicts (8/9, the
  known exact-common wart); `machinome snapshot` without `--renderer` prints R4
  and exits 1.
- **The goldens**: `leaf_contract_golden.py --check`,
  `scad_presentation_golden.py --check`, `expression_type_golden.py --check`,
  each in a fresh process: no difference.
- **`machinome new` in throwaway directories** under three installs simulated by
  finders: all extras (the Solid2Node template, byte-identical to a16d45a's
  output; `machinome build` and `machinome test` green); `solid2` blocked (the
  CadQuery template; build and its two tests green with `[manifold]`); both
  blocked (R8, exit 1, nothing created).
- **Shallow, the universe**: `scripts/load-projects` with the seven earlier
  tables plus this change's `openscad-out.toml`, 300 s timeout. Expected: the
  mesh-engine sweep's rows unchanged (117 ok, 4 expected, 2 unexpected and
  pre-existing, 6 no-model), no row for this change, since no project imports a
  moved name.
- **Greps the orchestrator runs over `projects/`** (the proposer may not):
  project files importing from `solid2` that do not import `Solid2Node` (the
  adoption hook's reach, Decision 3); project classes declaring `fn` or
  `optimize = False` on a node that is not a family leaf; any `as_scad`,
  `scad_code`, `generate_scad`, `scad_file` or `scad_authored` (the plan says
  none, 4 October 2026).

### 15. The tests: which are rewritten, which stay, none moves

105 test files mention the word (`grep -rli scad tests --include=*.py`, a16d45a).
None moves to another directory: organising the suite by future package was
deferred by the pilot (plan, "Struck or deferred"). Counted by grep for every
name this change moves or removes (the seam and engine modules, the SCAD
members of the bases, the coalescing and record names, `scad_expression`,
`OPENSCAD_FOV`, `OPENSCAD_RENDERER`, the template path), 48 files are
rewritten, 47 of them among the 105:

- **Merged into `tests/test_openscad_node.py`, then deleted:**
  `test_openscad_engine.py` (the package, the writer's bytes, adoption; its
  seam-contract cases go with the seam) and `test_scad_engine_seam.py` (its
  resolution and contract-version cases test a seam that no longer exists; its
  refusal cases become the three doors of task 2.3).
- **Rewritten onto the family and the writer:** `test_scad_presentation.py`,
  `test_scad_import_paths.py`, `test_scad_stl.py`, `test_generation_dedup.py`,
  `test_openscad_dependency.py` (messages unchanged), `test_snapshot.py`,
  `test_backend_neutral_materialization.py`, `test_expression_type.py`,
  `test_source_generation.py`, `test_build_publication.py`,
  `test_coarse_filesystem_freshness.py`, `test_content_verified_currency.py`,
  `test_two_pipes.py`, `test_manager_develop.py`, `test_manager_test.py`,
  `test_manager_new.py`, `test_browser_renderer.py`, `test_camera.py`,
  `test_no_class_name_recognition.py`, and the scripts and fixtures
  `scad_presentation_golden.py`, `expression_type_golden.py`,
  `scad_presentation_project/parts.py`, `scad_where_read_project/legacy.py`,
  `contract_package/scad_stand_in.py`, `vet_projects/framework_internal/sim/model.py`
  (its `import machinome.openscad` becomes `import machinome.node.openscad`) and
  `tests/base.py`.
- **Renamed calls only** (`as_scad` → `present`, `scad_code`/`generate_scad` on a
  non-family node → the writer, `_render_can_be_skipped` →
  `_prepare_can_be_skipped`): `test_assert_code.py`, `test_build123d_adapter.py`,
  `test_builder_lifecycle.py`, `test_connectivity.py`,
  `test_declarative_nodes.py`, `test_declarative_render.py`,
  `test_document_drivers.py`, `test_exact_geometry.py`,
  `test_expression_bindings.py`, `test_flexible_node.py`,
  `test_jscad_integration.py`, `test_markings.py`, `test_model_consumption.py`,
  `test_molejo_adapter.py`, `test_project_through_a_symlink.py`,
  `test_sheet_leaf.py`, `test_source_set.py`, `test_step_node.py`,
  `test_stl_node.py`, `test_traversal_naming.py`.
- **Stay unchanged: 58 files**, which use `Solid2Node` or `OpenScadNode` as cheap
  fixture leaves through the root export or `machinome.node.solid2`, keep
  `.scad` sources for `OpenScadNode` fixtures, or mention the word in comments;
  every address they import survives, and the dev install carries both extras.
- **Stand-ins gain the declared set** (task 3.4): `test_assertions.py`,
  `test_broad_phase_culling.py`, `test_intersection_memo.py` and whatever else
  the suite reports, through `tests/stand_in.py`.
- **New:** `test_core_names_no_scad.py` (the gate), `test_openscad_node.py`,
  `test_leaf_capability_set.py`, `test_supported_node_types.py`.

## SOLID review

The pilot's standing requirement; where the design follows each principle and
where it bends.

- **Single responsibility.** The core composes structure, presentation as data,
  currency and the expression language; the family writes SCAD and runs
  OpenSCAD, the OpenSCAD viewer draws with it (until the viewer seam gives it
  its own provider), `Solid2Node` adopts SolidPython values. Before, `node/base.py`
  was also the OpenSCAD runner and the SCAD text's caller, `source_generation`
  also a SCAD publication queue, the builder's sweep also a SCAD rule, and the
  seam a resolver for three unrelated needs. `currency.publish_text` is one rule
  (do not rewrite identical bytes) where it belongs.
- **Open/closed.** A new node type with its own artifacts declares them in
  `kept_artifacts()` and presents through `present`; the sweep, the builder and
  the test framework do not change. A new adopter registers itself. **Bend,
  accepted by the pilot's ruling:** the table of supported node types is a
  closed list in the core: a ninth node type is a row, and a renderer or command
  contributed by a package is a row (ADR-167 rejected exactly such a table for
  extras; it is allowed here as the one place, provisional until the pilot's
  renderer revisit).
- **Liskov.** Every leaf answers the whole declared set with the base's
  meaning, so the core treats a family leaf, a native leaf and a leaf written
  outside the core alike; a stand-in in the suite substitutes for a node because
  it declares the set, not because the core tolerates its absence. The base's
  `generate_stl` no longer behaves as an OpenSCAD node for every subclass, which
  was the substitution failure the wart describes.
- **Interface segregation.** The family's members (`scad_file`, `scad_code`,
  `generate_scad`, `fn`, the runner) live on the family's base, not on every node;
  a CadQuery leaf no longer carries SCAD members it cannot honour. The leaf
  contract grows by the members the core actually reads.
- **Dependency inversion.** The core depends on its own abstractions (the
  declared set, the presentation description, the adopter hook,
  `StlRenderStart`) and the family depends on the core; nothing in the core
  imports the family except through the table, and the table is data the core
  reads, not code it calls into for a technology. **Bend:** the family's writer
  reaches two core functions not yet declared in the leaf contract,
  `currency.publish_text` and the generation's published-state record; declaring
  them is the cut's (Open Questions).

## ADRs

Extracted after implementation, under the framework-change skill:

- **ADR-177** (NODE), "The OpenSCAD family is a node package, and the core names
  no technology": the package and its modules, `Solid2Node` over it, the writer
  keeping SolidPython (evidence of Decision 2), the seam dissolved, the adopter
  hook, the gate. Supersedes ADR-171; amends ADR-172 (the writer's owner and
  address; `presentation()`), ADR-173 (the sweep by declaration; the `.scad` rule
  on an unchanged document kept by the transient record), ADR-086 (coalescing removed), ADR-046 (the
  binary contract's address), ADR-103 (`OpenScadRenderer` stays at its address,
  reaches the package directly and is reached through the table; the default
  unchanged), ADR-102 (no legacy SCAD-only override).
- **ADR-178** (NODE), "A leaf declares its kind as one set on the leaf base": the
  set, the fourteen probes removed, `present` and `kept_artifacts`, the runner's
  move and the refusal of a leaf that produced no STL, `CONTRACT = 2`. Amends
  ADR-163 (the declared members) and ADR-165 (the version's first change).
- **ADR-179** (BUILD), provisional, "The core reaches a node package's renderer
  and command through the table of supported node types": the table's shape and
  location, its readers, its provisional renderer column, what the renderers'
  lack of a contract looks like, and the pilot's decision that the viewer seam
  `machinome.viewer` is the phase's last cycle, which removes the column.
  Amends ADR-168 (the third column names a node type) and ADR-167 (the table's
  bend, by ruling).

ADR-052 (conditional mesh engine dependency) mentions OpenSCAD only as ADR-046's
precedent and needs no amendment.

## Moved names

`moved-names.toml` in this change lists every importable name that moves or
vanishes: the seam's names, `machinome.openscad.*` (`OpenScadRenderer` keeps its
address and loses only `require_engine`), `machinome.core.expressions.scad_expression`, `machinome.core.camera.OPENSCAD_FOV`
(renamed `DEFAULT_FOV`), `machinome.manager.snapshot.OPENSCAD_RENDERER`, the
source generation's renamed and removed members, and the members leaving the node
and leaf bases, each with where it went or that it is gone.

## Risks / Trade-offs

- [A SolidPython value reaches machinome math in a process that never imported
  `machinome.node.solid2`] → refused as a non-expression with today's wording;
  machinome-mechanics' twelve test files are the known case (a mechanics change:
  `machinome.expression_graph.get_animation_time`); the orchestrator's grep of
  `projects/` sizes the rest before integration (Decision 14).
- [A stand-in in the suite lacks a member the core now reads] → `AttributeError`
  in that test, not a silent default; the shared mixin and the suite's run list
  them all (task 5.3).
- [A project leaf overrides `as_scad` to author SCAD] → none known (grep of
  4 October 2026); it now presents its STL, produces none, and meets R7 naming
  it; the changelog and the upgrade page say to subclass `Solid2Node`.
- [A project declares `fn` on an assembly for its root `.scad`] → the writer
  reads `fn` off any node it writes, so the root text keeps it; the attribute is
  no longer declared by the core base for non-family nodes (*inferred* safe, the
  orchestrator's grep confirms).
- [A transient record is written for a file a node keeps] → the writer marks
  transient only a file absent from the node's `kept_artifacts()`, and 2.8 pins
  that a SCAD-authored root's own `.scad` survives a snapshot and a build; a
  killed snapshot's leftover is removed by the next build (Decision 4a).
- [A plain install's default snapshot is refused] → R4 names the extra and the
  web renderer; the default is unchanged by ruling; Open Questions.
- [`supported.py` grows into a registry] → its test pins that it defines only the
  table and its three functions and imports no node module at import.
- [The family reaches undeclared core functions] → `currency.publish_text` and
  the published-state record are named in this design and ADR-177; the cut
  declares them or gives them a leaf-contract member.
- [Byte drift in SCAD] → by construction none; three goldens and the lock's leg
  stop the cycle if one moves.

## Migration Plan

Projects: none of the moved names is used (grep of 4 October 2026). A project
with `Solid2Node` parts installs `machinome[solid2]`; with `OpenScadNode` parts or
taking OpenSCAD snapshots, `machinome[openscad]`; `[all]` installs both. A project
leaf that authored SCAD by overriding `as_scad` subclasses `Solid2Node` instead.
Framework tests: repointed as tasks 6 say. Workspace and studio (findings for the
orchestrator, not this cycle's edits): `scripts/setup` and
`docs/collaborator-setup.md` install `[all]` already for tier 2 per the plan's
follow-ups; the studio's `machinome-api` skill teaches no SCAD API but should name
the two extras. Rollback: revert the implementation commit; no artifact or document
needs rebuilding beyond the verdict store's automatic reset (ADR-156).

## Open Questions

1. **A SolidPython-free OpenSCAD package.** Decision 2 keeps SolidPython in the
   writer: a writer of its own changes the root text of any process that ran
   `import_scad` (the global `use` lines) and needs a SCAD signature reader for
   `OpenScadNode`. Recommendation: keep SolidPython in this cycle; revisit only if
   the pilot wants `machinome[openscad]` to carry no Python dependency, accepting
   one byte change in the OpenSCAD snapshot's root text.
2. **`scad_expression` stays in the core, renamed `closed_expression`**, against
   the brief's "goes to the package" (Decision 7: it is the core's `str()`).
   Recommendation: ratify the rename in place.
3. **Adoption only after `machinome.node.solid2` is imported** (Decision 3).
   Recommendation: accept, with machinome-mechanics' twelve test files moving to
   `machinome.expression_graph.get_animation_time` in mechanics' own cycle (already
   a plan follow-up), and decide after the orchestrator's grep of `projects/`.
4. **The unchanged-document sweep** (Decision 4a). Resolved by the pilot on
   4 October 2026: the transient record. The two shapes not taken: a nameless
   sweep that does nothing on an unchanged document (a killed snapshot's root
   `.scad` lingering until the next snapshot or document change), and a second
   pass removing files of a kind some node declares in `kept_artifacts()` by
   suffixes derived from the declarations.
5. **The default renderer stays `openscad`.** The code gives one reason to revisit:
   a plain `pip install machinome` cannot use it (R4), and a CadQuery-only project
   now meets that refusal on `machinome snapshot` with no flag. The web renderer
   needs `[web-snapshot]` and a browser, so neither default works in a plain
   install. Recommendation: keep `openscad` (the ruling) and let the pilot's
   renderer revisit decide.
6. **R5 for the binary, not the extra.** The brief asked the renderer to refuse
   "naming `machinome[openscad]` when the package or the binary is absent".
   Recommendation: R4 for the package, R5 (unchanged) for the binary, since no
   extra installs an executable.
7. **`import-step`'s implementation stays in `machinome.manager`**, reaching
   `machinome.node.step` through the table (Decision 6). The plan's D3 places it in
   the step package at the cut. Recommendation: move it with the cut (ADR-168's
   consequence), not here.
8. **The template order, `solid2` before `cadquery`** (Decision 4e), which keeps
   today's output wherever SolidPython is installed. The alternative,
   `cadquery` first, matches the manual's tutorial route but changes what `[all]`
   installations scaffold. Recommendation: `solid2` first.
9. **The family's two undeclared reaches** (`currency.publish_text`, the
   published-state record). Recommendation: declare them at the cut, when the
   family's leaves first declare `leaf_contract = 2` from another distribution.
10. **`viewers/browser.py` "untouched" against the gate.** The scope reduction
    keeps `viewers/browser.py` and `viewers/bundle.py` untouched, but
    `browser.py` holds three occurrences of the word (line 12, "resolved from
    OpenSCAD's syntax"; line 158, "It never falls back to OpenSCAD"; line 169,
    the suggestion `--renderer openscad` in `refuse_unreadable`'s message), and
    the gate's allowed zones do not include it. Recommendation: reword the two
    docstrings and build the suggestion from the table's `DEFAULT_RENDERER`,
    leaving the module's behaviour and every other line as they are; the
    alternative, a fourth allowed zone for a module the viewer cycle rewrites
    anyway, widens the gate for no lasting reason.
11. **`core/camera.py`'s notation.** The web viewer's camera parser converts the
    `--camera` gimbal and vector forms, OpenSCAD's command-line notation, with
    OpenSCAD's field of view (`OPENSCAD_FOV = 22.5`). The notation stays (it is
    what `--camera` takes); the constant is renamed `DEFAULT_FOV` and the
    docstrings describe the two forms and the view transform without naming
    their origin, which ADR-177 records. Recommendation: accept; the viewer
    cycle may move the parser into its seam.
