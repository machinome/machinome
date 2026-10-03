## Context

Cycle 6 of the lean-core campaign's "Layers" (`workflow/ongoing/lean-core.md`,
pilot, 3 October 2026): "the SCAD presentation behind a seam, `assemble()` no
longer requiring it, the `develop` fallback included", the second of four
cycles taking OpenSCAD out of the core. Its precedents are `exact-engine` (an
engine at its final address reached through a seam of one known provider with
a contract version; ADR-161, ADR-162), `lean-install` (absence refused by
naming the install) and `expression-type` (the OpenSCAD engine
`machinome.openscad` and its seam `machinome.scad_engine`, contract 1; ADR-170,
ADR-171), whose "Deferred" list names this cycle's work.

Facts below were read in the bench at a4a1f84 on 3 October 2026 with the
workspace venv (solidpython2 2.1.3, Python 3.12.3), unless marked *inferred*.

### What the core composes today

`node/base.py` imports `scad_render`, `import_stl` and `color` from `solid2`
at module top, and `machinome.openscad.binary.require_openscad`. The SCAD
presentation is built from six constructs and nothing else:

| construct | where | SolidPython call |
|---|---|---|
| import of a build artifact | `AbstractBaseNode.artifact_import` → `_ArtifactImport(import_stl)`, path relative to the build-wide anchor; used by `ExactLeafNode.as_scad`, `StlNode.as_scad`, `JScadNode.as_scad`, `FlexibleNode.as_scad`, `assemble()` and `import_optimized()` | `import_stl(path)` |
| colour | `_colorize`, `#RRGGBB` → three floats, alpha `1` | `color([r, g, b], 1)(child)` |
| rotation | `Rotation.scad` (operations.py), angle and axis as the operation holds them | `rotate(angle, axis)(child)` |
| translation | `Translation.scad`, the vector as held | `translate(vector)(child)` |
| union | `InternalNode.as_scad` (two or more children; one child is itself; none is `union()()`), `FlexibleNode.as_scad` for a time-fed port (`union()`) | `union()(children)` |
| authored geometry | a `Solid2Node`'s or `OpenScadNode`'s render result, or a project leaf's `as_scad` override, held as `model` | (the leaf's own object) |

Text is produced by `scad_code` (`scad_render` of `_model_for_own_scad()`,
preceded by `$fn = N;` and a blank line when the node declares `fn`) and by
`OpenScadNode.scad_code` (the source plus the last line of `scad_render`).
`_model_for_own_scad` deep-copies the tree and rewrites every `_ArtifactImport`
path onto the directory of the `.scad` about to hold it (ADR-116), walking
SolidPython's private `_children` and `_params`. `generate_scad()` publishes the
text with the generation reuse and non-rigid coalescing of ADR-086.

Probes (3 October 2026): `scad_render(union())` and `scad_render(union()())`
are both `union();\n`; SolidPython writes a tuple as a list (`[1, 2, 3]`), a
float as `30.0`, an int as `1`, and a non-string scalar by `str()`
(`rotate(a = ($t * 360), v = [0, 0, 1])` for the core's symbolic value).

### Who reads SCAD

Verified by reading every consumer (grep of `machinome/`, the projects, the
viewer, the studio, 3 October 2026):

- **OpenSCAD, for a SCAD-authored leaf's own STL.** `Solid2Node.materialize`
  and `OpenScadNode.materialize` call `generate_scad()`; a project leaf that
  overrides `as_scad` does the same through `_prepare`'s legacy branch;
  `generate_stl` then runs `openscad <scad_file> -o <stl>`.
- **The OpenSCAD snapshot renderer** (`viewers/openscad.py`), which hands
  OpenSCAD `node.scad_file` of the root, written by the `node.assemble()` that
  `manager/snapshot.py` calls for either renderer.
- **A person** opening a `.scad` in the OpenSCAD GUI
  (`backend-neutral-materialization`, "A normal build remains useful to
  OpenSCAD users").
- **The framework's tests**, which pin SCAD text (`expression_type_golden.py`,
  `test_scad_import_paths.py`, `test_generation_dedup.py` and others).

Nothing else. The published document carries no SCAD (`core/serializer.py`
has no SCAD path; the viewer repository reads no `.scad`). No build reads a
`.scad`: currency is decided on `.stl`, `.brep` and markings
(`_artifacts_are_current`, `_prepare_can_be_skipped`), and the sweep spares
`.scad` by kind. `LeafNode._render_can_be_skipped`, the one predicate that
consults `.scad` currency, has no production caller since ADR-102 (only tests
call it). `machinome test` prepares with `_prepare()`, export with
`build_stls()`; neither presents SCAD.

**Where presentation runs.** `Builder._present_scad_if_requested` calls
`node.assemble()` when `scad_output` is true: `machinome build` passes nothing
(true); `machinome develop`'s builder, first run and reloads, passes false.
`manager/snapshot.py` calls `node.assemble()` for both renderers.
`Sim(meshes=True)` calls `node.assemble()`. Project and framework tests call
`node.assemble()` directly: 210 Python files in 17 top-level project
directories, none using the return value (grep, excluding worktrees, builds
and archives). With the viewer installed, therefore, the assembly SCAD of a
`machinome build` is read by no build and no test of the project; only the
OpenSCAD snapshot renderer reads the root's.

**Pin_tumbler_lock, one in-process `assemble()`** into a scratch build
directory: 14 `.scad` files. 11 are `Solid2Node` leaves (`OriginalPart`
subclasses), whose own SCAD OpenSCAD renders; 3 exist only because
`assemble()` presented them: the root `PinTumblerLock`, the sub-assembly
`Plug`, and the flexible `PenSpring`. The fifth cycle's 24 files at a4a1f84 come
from its build, test and export legs together, the tests assembling further
parameter sets (*inferred* from `test_lock.py`'s `wrong.assemble()` and
`alternate.assemble()`). The names tell the two apart: the `OriginalPart`
leaves are `simulation/parts-*.scad` (`Body`, `Circlip`, `Core`, `DriverPin`,
`SpringCover`, `Key` and five `Pin` depths in the default build), every
presentation file is `simulation/lock-*`, `simulation/flexibles-*` or
`simulation/poses-*` (read in the project's own `_build/`, 3 October 2026,
31 files from earlier builds).

### `develop`

`machinome develop` has had no OpenSCAD path since ADR-103 (11 September 2026).
Probed on 3 October 2026 in Pin_tumbler_lock with `has_bundle` patched false:
`Error: The browser viewer is not installed. It is the separate machinome-viewer
package; install it with: pip install "machinome[viewer]"`, exit 1, neither the
viewer nor the builder started; `--openscad` is `unrecognized arguments` (exit
2). With the viewer, the builder runs with `scad_output=False`, so only
SCAD-authored leaves write `.scad`. The "fallback" the plan names does not
exist, and nothing in this cycle changes `develop`. The workspace contract
(`CLAUDE.md`) and the studio's two skills still describe the removed fallback
and `--openscad` (proposal.md, Impact): stale documentation outside the
framework, recorded as findings.

## Goals / Non-Goals

**Goals:**

- No core module composes SCAD or imports SolidPython for presentation; the
  core describes, the engine writes.
- `assemble()` needs neither SolidPython nor the engine and writes no SCAD; a
  build of a project whose leaves need no OpenSCAD completes without the
  engine.
- A `.scad` is written only where a path reads it (Decision 3, the pilot's):
  a SCAD-authored leaf's, from which OpenSCAD renders its STL, and the
  root's, on demand, for the OpenSCAD snapshot renderer. A build sweeps every
  other `.scad`.
- Every `.scad` still written is byte-identical to the file today's code
  writes at the same path in the same pose, and every node's `scad_code` is
  byte-identical to today's; no document byte moves.
- The seam's contract at 2, naming the operations the core calls; the binary
  reached through it where this cycle touches a module.
- Absence refused where SCAD text is actually needed, naming the install that
  works today.

**Non-Goals:**

- Whether `machinome snapshot --renderer web` and `Sim(meshes=True)` should
  prepare rather than assemble (cycle 7): both still call `assemble()`, which
  under this change writes no SCAD.
- The runner: `stl_builder_command_for`, the `Popen` in `generate_stl`,
  `StlRenderStart`, and the OpenSCAD snapshot renderer's command line and
  its move into the engine package (cycle 7).
- `Solid2Node` and `OpenScadNode` as node modules over the engine,
  `Solid2Node.as_number`, the `openscad` extra and its refusal (cycle 7).
- The template (cycle 8). The viewer. The studio skill.
- `develop` (nothing to move; see Context).

## Decisions

### 1. What the core hands the engine: a presentation description

The core composes a small immutable tree of its own, defined in
`machinome/node/presentation.py` (names provisional):

- `ArtifactImport(path)`: a build artifact, `path` relative to the build-wide
  anchor (`get_build_dir`), exactly the string `_ArtifactImport` holds today;
- `Color(rgb, alpha, child)`: the floats `_colorize` computes, alpha `1`;
- `Rotate(angle, axis, child)` and `Translate(vector, child)`: the values the
  operation holds, by reference, unconverted;
- `Union(children)`: a tuple of zero or more descriptions;
- `Authored(geometry)`: the object a SCAD-authored leaf rendered or its
  `as_scad` returned, opaque to the core;
- `reanchored(description, build_dir, own_build_dir)`: a new description
  whose `ArtifactImport` paths resolve from `own_build_dir`, sharing every
  other node; `Authored` content is never entered, as today a project's own
  `import_stl` is never re-anchored.

`as_scad`, `assemble()`, `import_optimized()`, `_colorize`, `artifact_import`
and the operations build it (`Rotation.scad`/`Translation.scad` become
`Rotation.presented(child)`/`Translation.presented(child)`, returning the
description); a value an `as_scad` returns that is not a description is held
as `Authored`. The engine's `scad_text(description, fn=None)` maps each node to
the SolidPython call of the table above, passes `Authored` content through, and
returns `scad_render` of the result, prefixed by `$fn` when given.

Why: it is the same tree the core builds today with the SolidPython calls
replaced by data, so the engine rebuilds exactly today's SolidPython tree and
the text is byte-identical by construction (Decision 7). Re-anchoring becomes a
pure function over the core's own types, with no private walk of SolidPython
and no `copy.deepcopy` per `.scad` (the ADR-116 reviewer's cost note).

Alternatives:

- *The serializer's document.* Exists, but carries no authored SCAD
  (`Solid2Node`'s and `OpenScadNode`'s own models, a legacy leaf's override,
  an `optimize = False` node's inlined model), no `$fn`, and its operations as
  graph slots and a bindings table rather than the closed text SCAD carries;
  the engine would have to re-derive SolidPython's structure and number
  formatting from it, with byte identity a hope rather than a construction.
- *Matrices.* A matrix cannot carry `$t`: SCAD presents symbolic motion as
  `rotate(a = <text>)`, and the document already keeps operations, not
  matrices, for the same reason.
- *Engine-built objects* (the core calls `engine.import_(...)`,
  `engine.rotate(...)`). Every `assemble()` would then require the engine,
  which is the opposite of the goal, and re-anchoring would stay a walk of
  SolidPython's privates.
- *Text composed by the core* (`f'rotate(a = {angle}, v = {axis})'`). The core
  would write SCAD syntax and duplicate SolidPython's formatting of numbers,
  lists and indentation (`30.0`, `[1, 2.5, 0]`, tabs), a byte risk for every
  model and the single responsibility this cycle separates.

### 2. `assemble()`

`assemble(root=None)` keeps its template (memoized, `_prepare` first, the
optimized-import decision, operations applied in order, `_link_child` through
`InternalNode.as_scad`) and returns the node's presentation description. It
writes no `.scad`, at any node, with or without the engine: the two
`generate_scad()` calls it makes today go (Decision 3), and it asks the engine
for nothing. It requires neither SolidPython nor the engine, so the 210
project files that call it to prepare a node for mesh use keep working in
any install, and nothing is skipped or logged when the engine is absent.
Composing a flexible leaf's description still evaluates its bound instant
and publishes its per-binding snapshot STL, as today: the description
imports it, and the root's SCAD the OpenSCAD snapshot renderer writes reads
it.

`generate_scad()` stays the one writer of a node's `.scad`, called by a
SCAD-authored leaf's materialization and by the OpenSCAD snapshot renderer
on the root. It and `scad_code` require the engine (Decision 4): a direct
request for SCAD text cannot be answered without the writer of SCAD text.

### 3. When `.scad` is written: only where it is read (the pilot's decision)

The brief asked that `.scad` be written only when a path needs it. Three
ratified requirements said otherwise: `backend-neutral-materialization`, "SCAD
remains a supported output and compatibility boundary" ("The normal `machinome
build` SHALL retain its SCAD deliverables"; scenario "A normal build remains
useful to OpenSCAD users"); `build-pipeline`, "Build artifact layout" ("The
ordinary `machinome build` and SCAD presentation path SHALL retain `.scad`
deliverables"); and `node-model`, "Template-method render lifecycle", where
`assemble()` "requests SCAD presentation". The change therefore returned the
choice to the pilot. **The pilot chose A on 3 October 2026: a `.scad` file is
written only where a path reads it.** The deltas rewrite those three
requirements, the sweep's rule and the scenarios that read a build's assembly
`.scad`.

The rule:

- **A build writes the `.scad` of a SCAD-authored leaf and no other.** A
  `Solid2Node`, an `OpenScadNode` or a project leaf overriding `as_scad`
  (`_uses_legacy_scad_materialization()`) writes its own `.scad` at
  materialization, through the engine, because OpenSCAD renders that leaf's
  STL from it. No assembly, fusion, flexible leaf or native leaf (exact,
  STEP, STL, JScad, sheet) writes one, with or without the engine.
- **`assemble()` composes and returns the description and writes nothing of
  SCAD** (Decision 2). The builder stops presenting: under A its call of
  `assemble()` would compose a description no build reads, so
  `Builder._present_scad_if_requested`, the `assembly` source-generation phase
  it opens and the `scad_output` parameter (of `Builder` and of
  `manager/develop.run_builder`, whose only callers pass it false or rely on
  the default) are removed. `machinome build` and `develop`'s builder become
  the same pipeline.
- **The OpenSCAD snapshot renderer obtains the root's SCAD on demand**,
  through the seam, when it runs (below). It is not a build deliverable.
  `machinome snapshot --renderer web` writes and reads no SCAD: it still
  calls `assemble()`, which writes none, and stages the document.
- **With the engine absent, a build writes no `.scad` because nothing in it
  asks for one.** Nothing is skipped, so nothing is logged. A SCAD-authored
  leaf meets the existing refusal paths: a project leaf overriding `as_scad`
  is refused by name at its materialization (Decision 4); `Solid2Node` and
  `OpenScadNode` import `solid2` at their module top until cycle 7, so with
  SolidPython absent a project using them fails at its import, as today, and
  cycle 7's `openscad` extra gives that its refusal.

**Where the renderer's on-demand SCAD is written: the build directory, at the
root's own `scad_file`.** `manager/snapshot.py` poses and assembles the root
inside the project build lock, as today, then, for the OpenSCAD renderer
only, has the renderer write the root's SCAD (`OpenScadRenderer.present`,
provisional, calling the root's `generate_scad()`) in the same locked step;
OpenSCAD
renders the file after the lock is released, as today. Every OpenSCAD
snapshot writes it for its own pose (the byte-identical write suppression of
`build-pipeline` applies; nothing an earlier run left is trusted); it is a
renderer artifact with no currency beyond that run, and the next successful
build of that directory removes it with its currency record, like any
`.scad` no current node writes. Reasons:

- It is exactly today's file: the same path, its imports re-anchored onto
  its own directory by ADR-116's rule, the bytes the root's `scad_code`
  gives, and `OpenScadImportError` still names a file that exists. A
  temporary elsewhere would need its imports anchored onto a foreign
  directory, a second anchoring case in the core, and its bytes would match
  no recorded hash.
- What it imports lives in the build directory anyway, including the
  per-binding snapshot STL a flexible leaf publishes while the description is
  composed; a temporary would not free the renderer from the build directory.
- It is the route left to a person who wants a machine's SCAD in a file:
  `machinome snapshot --renderer openscad` leaves it beside the artifacts it
  imports, openable in the OpenSCAD GUI until the next build. From Python,
  `node.scad_code` gives any node's text.

Rejected: a temporary directory removed after rendering, invisible to builds
and sweeps, for the three reasons above. Trade-off accepted: a build that
runs between the snapshot's release of the lock and OpenSCAD reading the file
now removes it, and the render fails naming it; today the same interval lets
the build overwrite it with the build's own pose, a silently wrong image.
Holding the lock through the render would close the interval at the cost of
blocking builds for a render's duration; not taken, since `build-pipeline`'s
lock is held for artifact work only.

**The sweep: a `.scad` is kept by reference, not by kind.** Today `kept()` in
`Builder._sweep_unreferenced_artifacts` spares every file ending `.scad`
(`build-pipeline`, "A successful build sweeps unreferenced artifacts"), so
under A an earlier build's assembly files would linger forever. Instead the
sweep walks the builder's node tree, as it already does for a flexible
leaf's per-binding snapshot, and keeps the `scad_file` of every node whose
geometry is authored in SCAD, with its currency record (which the sweep
already judges by the artifact it vouches for); every other `.scad` in the
build directory is removed: an assembly's, a fusion's, a flexible or native
leaf's left by an earlier build, the root's left by a snapshot, and a
renamed or re-parameterised SCAD-authored leaf's. A leaf's own `.scad` is
kept while its node is in the tree, whether or not this build rewrote it (a
current STL skips materialization). The node answers through one core
predicate (provisional name `scad_authored`: false on the base, true on
`Solid2Node` and `OpenScadNode` by a class attribute, and on a leaf whose
`_uses_legacy_scad_materialization()` holds), the same predicate that names
"the materialization of a leaf whose geometry is authored in SCAD" among the
requiring paths (Decision 4). Telling the files apart by name was rejected:
an exact or STL leaf's `.scad` sits beside its referenced `.stl` under the
same basename exactly as a `Solid2Node`'s does, so a sibling rule would keep
the lingering native-leaf files. The `collect_snapshots` walk goes with the
builder's presentation: no build composes a description, so no per-binding
snapshot STL is current in one, and the reference rule removes those too.

**Why B was rejected.** B, proposed by this change before the ruling: keep
writing every node's `.scad` from every build when the engine is installed,
skip and log once when it is not. It changed no ratified behaviour. The pilot
rejected it because those deliverables existed for a reader machinome does not
have: no build, document, viewer, export or test reads an assembly `.scad`,
and the one consumer, the OpenSCAD snapshot renderer, reads only the root's.
The pilot wants OpenSCAD's artifacts produced only where machinome itself
needs them.

**The `.scad` files that stop being written.** In general: by a build, the
`.scad` of every node whose geometry is not authored in SCAD (assemblies,
fusions, flexible leaves, native leaves); by `assemble()` anywhere (project
tests, `Sim(meshes=True)`, either snapshot renderer), every `.scad`; the
root's is written only by `machinome snapshot --renderer openscad`, and a
flexible leaf's per-binding snapshot STL is no longer written by a build.
For Pin_tumbler_lock a build writes 11 of the 14 files one `assemble()`
wrote, its `OriginalPart` leaves' `simulation/parts-*.scad`; the three it
stops writing are the root `PinTumblerLock`'s
(`simulation/lock-PinTumblerLock-*.scad`), the sub-assembly `Plug`'s
(`simulation/lock-Plug-*.scad`) and the flexible `PenSpring`'s
(`simulation/flexibles-PenSpring-*.scad`). For an all-exact project such as
OpenAstroMount, every one. Who loses something: a person who opened a
build's `.scad` in the OpenSCAD GUI; no named project relies on it (grep, 3
October 2026: `splitflap`'s and `openflexure-microscope`'s SCAD tooling reads
their own upstream sources, not `_build/`). The changelog says so as BREAKING
and names the on-demand route.

### 4. Absence: `require_scad_engine` and its refusal

The seam gains, of `machinome.exact_engine`'s shape:

- `ScadEngineUnavailable(RuntimeError)`, with `needed_by`, `reason`, the
  missing module and an optional alternative;
- `require_scad_engine(needed_by, reason, alternative=None)`, returning the
  provider or raising it;
- the module whose absence made `scad_engine()` answer `None`, remembered at
  resolution.

The remedy names what installs the missing module **today**: for `solid2`,
`install SolidPython with 'pip install solidpython2'` (the distribution
machinome requires, absent only when removed); for `machinome.openscad` or the
provider, `reinstall machinome, whose distribution carries the OpenSCAD
engine`. No extra is named: `machinome[openscad]` does not exist until cycle 7,
which replaces both remedies with it (the `expression-type` reasoning: naming
an install line that installs nothing is worse than none).

Requiring paths, each checked where attempted: `scad_code`; `generate_scad()`;
the materialization of a SCAD-authored leaf (it calls `generate_scad()`); the
OpenSCAD snapshot renderer, before the node is loaded (so before any
artifact or the root's SCAD is written and before OpenSCAD is resolved or
launched), with `alternative='use --renderer web'`
(`web-snapshot`'s symmetric rule). `machinome build` and `assemble()` do not
require it: neither asks for SCAD text except through a SCAD-authored leaf's
materialization (Decision 3), so without the engine a build of a tree with no
such leaf writes no `.scad` and logs nothing about SCAD, and a tree holding
one meets that leaf's refusal.

`OpenScadUnavailable` (the binary's refusal, `machinome.openscad.binary`)
becomes a subclass of `ScadEngineUnavailable`, its message unchanged, so
`manager/snapshot.py` catches both through the seam without importing the
engine's package. The engine importing the core's exception is the permitted
direction (the exact engine raises the seam's `ExactCommonInconsistency`).

### 5. The contract, version 2, and the binary through the seam

`machinome.scad_engine.CONTRACT = 2` and `machinome.openscad.engine.CONTRACT =
2`, under ADR-162. The provider's operations, which the seam's docstring lists
as cycle 5's and `exact_engine`'s list theirs:

- `adopt(value)`, since 1, unchanged;
- `scad_text(description, fn=None) -> str` (Decision 1);
- `require_binary(needed_by, reason, alternative=None) -> str`, delegating to
  `machinome.openscad.binary.require_openscad` (so the existing patches of
  `machinome.openscad.binary.openscad_binary` and `shutil.which` keep
  governing it).

Reaches into `machinome.openscad` after this cycle:

| module | before | after |
|---|---|---|
| `node/base.py` | `require_openscad` (`generate_stl`) | through the seam: `require_scad_engine(...).require_binary(...)` |
| `viewers/openscad.py` | `require_openscad` | through the seam |
| `manager/snapshot.py` | `OpenScadUnavailable` | the seam's `ScadEngineUnavailable` |
| `node/solid2.py` | `require_openscad` (`as_number`) | unchanged, cycle 7 |

So the AST rule of `expression-type` shrinks to {`scad_engine.py`,
`node/solid2.py`}. What remains for cycle 7: `node/solid2.py`'s reach and its
`scad_render`; `node/openscad.py`'s SolidPython parsing for `render()`; the
runner in `node/base.py` (`stl_builder_command_for`, `generate_stl`'s
`Popen`, `StlRenderStart`), which builds an OpenSCAD command line in the core;
`viewers/openscad.py`'s OpenSCAD command line; `Solid2Node.as_number`.

The seam stays the one core module naming the provider; a second
presentation engine would need its `PROVIDER` changed (open/closed's accepted
bend, as for the exact engine).

### 6. The leaf contract stays at version 1

The `leaf-contract` capability declares `as_scad`, `artifact_import`, `model`,
`scad_file` and `generate_scad` on `LeafNode` and says a SCAD-presented leaf's
`as_scad` returns "a solid2 object". After this change it still does: an
authored object is held as `Authored`. `artifact_import` returns the core's
description of an import instead of a SolidPython `import_stl` subclass; its
meaning (the anchored import of the leaf's own artifact, for `as_scad` to
return) is unchanged, its type was never stated, and no leaf outside the core
calls it (projects, machinome-freecad, machinome-mechanics: none, grep 3
October 2026). A leaf that composed `artifact_import()` inside a SolidPython
tree would now fail; none does. `model` holds what it held (the as_scad result
or the description). The contract version therefore stays 1, and the
`leaf-contract` delta says how `artifact_import` is used. If the orchestrator
reads the type change as a change of meaning, the alternative is
`leaf_contract` 2 in this change, refusing a leaf that declares 1 (ADR-165),
which would refuse machinome-freecad's adapter for a member it does not use.

### 7. Expressions travel as values; the engine does not wrap them

Cycle 5 left open whether presentation wraps values explicitly. It does not.
A rotation's angle and a translation's components travel in the description
exactly as the operation holds them, a number, the core's `GraphValue`
(a `DriverToken` in symbolic driver mode), or a SolidPython value a project
passed; the engine passes them to SolidPython, which writes a non-string
scalar by `str()`, and `str()` of the core's value is its closed OpenSCAD text
(ADR-170, Decision 3).

- *Not the core's expression nodes.* An `ExpressionNode` has no SCAD text of
  its own; the closed text, with its `let` sharing, is the `GraphValue`'s
  `str()`, the core's own serialization, which also feeds the standalone
  operation form, the clocked identity and diagnostics. Giving the engine
  nodes would make it re-implement `core.expressions.scad_expression`, a
  second writer of one language.
- *Not pre-rendered text.* A string given to SolidPython is written quoted;
  the engine would have to wrap it (`scad_inline(text)`), and a number
  pre-rendered by the core would have to reproduce SolidPython's number
  formatting. Both are byte risks for no gain: an identity wrapper with one
  caller, the alternative cycle 5 rejected.

### 8. Bytes

By construction (Decision 1), and pinned twice:

- `tests/expression_type_golden.py --check` (17 values; the assembly's and
  children's `scad_code` with shared `let` text, a time-fed flexible's empty
  union, a driver) passes unchanged after the change.
- A new characterisation, `tests/scad_presentation_golden.py`, written and
  recorded on the unmodified tree (task 1.2), covers what the first golden
  does not: a colour on a leaf and on an assembly, `fn` on a `Solid2Node`, an
  `optimize = False` assembly inlining authored geometry, a single-child and
  an empty non-rigid assembly, an assembly in another package than its parts
  (re-anchoring, reusing `tests/cross_package_project` or
  `tests/deep_project`), an `StlNode` import, an exact leaf import, a faceted
  `FusionNode`'s import of its fused artifact, a numerically bound flexible
  leaf's snapshot import, an `OpenScadNode`'s `scad_code`, a project leaf
  overriding `as_scad`, and a project's own `import_stl` inside a
  `Solid2Node` render. It records the SHA-256 and length of every node's
  `scad_code` (the text any on-demand writer produces, the snapshot
  renderer's root file included), and of every `.scad` file under the build
  directory after one `assemble()` of the root, by path relative to the
  build directory, each marked with whether its node is SCAD-authored.
  `--check` after the change requires every node's `scad_code` and every
  SCAD-authored leaf's file byte-identical and present, and every other
  recorded file absent, which is what Decision 3 expects; the red test of
  Decision 9 asserts the same set on its own fixture.
- The deep validation compares Pin_tumbler_lock's SCAD-authored leaves'
  `.scad` with the fifth cycle's hashes for the same paths.

No difference is unavoidable: the engine adds no header.

### 9. Proof, red first

Red on the unmodified tree, green after:

- **AST** (`tests/test_scad_presentation.py`): outside `machinome/openscad/`,
  the modules importing `solid2` are exactly `node/solid2.py`,
  `node/openscad.py` and the template (red: also `node/base.py`,
  `node/operations.py`, `node/internal.py`, `node/flexible.py`); the modules
  importing `machinome.openscad` or beneath it are exactly `scad_engine.py`
  and `node/solid2.py` (red: also `node/base.py`, `viewers/openscad.py`,
  `manager/snapshot.py`). `tests/test_expression_type.py`'s two lists shrink
  to match.
- **No SolidPython, no engine** (subprocesses under
  `tests/exact_engine_absent.py`'s finder, `absent=solid2`, and separately
  `absent=machinome.openscad`): `machinome build` of an all-STL fixture and of
  an all-exact fixture exits 0, writes `viewer.json` and every STL and BREP,
  leaves no `.scad` under the build directory and logs nothing about SCAD;
  `assemble()` then `build_stls()` then `mesh` works on a fixture node. Red:
  `ModuleNotFoundError: No module named 'solid2'` at `node/base.py`'s import
  (with `absent=solid2`), and `.scad` files written (with
  `absent=machinome.openscad`, since today's presentation never asks).
- **Written only where read** (engine installed): `machinome build` of a
  fixture holding an assembly, a faceted `FusionNode`, a flexible leaf, an
  exact or STL leaf and a `Solid2Node` leaf leaves exactly the `Solid2Node`'s
  `.scad` under the build directory, and no per-binding snapshot STL of the
  flexible leaf; `assemble()` of the fixture's root afterwards writes no
  `.scad`. Red: every node's `.scad` written.
- **Sweep**: a build directory seeded with what the unmodified tree's build
  leaves (the `.scad` and currency record of the assembly, the fusion, the
  flexible leaf, the native leaf and the root) plus the `.scad` of a
  SCAD-authored leaf since renamed; a successful build of the fixture ends
  with only its current `Solid2Node`'s `.scad` and record. Red: every seeded
  `.scad` spared by kind. `test_builder_lifecycle.py`'s
  `test_the_sweep_spares_inputs_locks_and_in_flight_temporaries` drops
  `part.scad` from what is spared and gains the case of a SCAD-authored
  `part`, whose `.scad` is kept.
- **Snapshot on demand**: `Snapshot.handle` with the OpenSCAD renderer (its
  runner patched) leaves the root's `.scad` at the root's `scad_file`, its
  text the root's `scad_code` in the snapshot's pose, every import resolving
  from its directory, and no assembly's or flexible leaf's `.scad` beside it;
  a following build removes it. With `--renderer web` (the browser renderer
  patched) no `.scad` is written. Red: every node's `.scad` written by the
  snapshot's `assemble()`, under either renderer.
- **Refusals**: `scad_code` and `generate_scad()` without the engine raise
  `ScadEngineUnavailable` with the spec's words for each missing module; the
  OpenSCAD snapshot renderer without the engine exits 1 with the renderer,
  the module and `--renderer web` named, no image, OpenSCAD not launched
  (a patched `run` never called), and no `.scad` written. Red: no such
  class.
- **Seam**: `CONTRACT == 2` on the seam and the provider; a stub provider
  declaring 1 is refused naming 1 and 2; `require_scad_engine` returns the
  provider; `OpenScadUnavailable` is a `ScadEngineUnavailable`; a counting
  stub provider sees `scad_text` called once per `.scad` a build writes (one
  per stale SCAD-authored leaf, none for an assembly) and
  `require_binary` called by a stale `Solid2Node`'s STL render and by the
  snapshot renderer. Red: contract 1, no operations.
- **Description**: `assemble()` returns a `machinome.node.presentation`
  value for every leaf kind; `reanchored` rewrites only `ArtifactImport`
  paths and leaves `Authored` content and the original untouched. Red.
- **Develop** (characterisation, green before and after): with the viewer
  hidden, `Develop.handle` exits 1 with the viewer remedy and starts neither
  process; the develop builder (as `run_builder` constructs it: today with
  `scad_output=False`, after the change with no such parameter) of a project
  mixing a `Solid2Node` with exact leaves writes the `Solid2Node`'s `.scad`
  only.

Characterisations, green before and after by design: the two goldens of
Decision 8.

### 10. SOLID

- **Single responsibility.** The core composes the tree, the document and
  the presentation *description*; the engine composes SCAD *text*; the seam
  resolves and refuses. Before, `node/base.py` was at once the node lifecycle,
  a SolidPython tree builder, a walker of SolidPython's privates and a locator
  of a binary. Under Decision 3 the builder builds and publishes only, and
  writing a presentation file is the business of the one consumer that reads
  it: a SCAD-authored leaf's materialization for its own STL, the OpenSCAD
  snapshot renderer for the root. `assemble()` composes; it no longer also
  writes files.
- **Open/closed.** A new presented construct is a description type and one
  engine mapping, not a change across four node modules. A new SCAD-authored
  leaf kind answers the one predicate (`scad_authored`), and the sweep and
  the requiring paths follow without change. A second presentation engine
  needs the seam's `PROVIDER` changed: the accepted bend, as for the exact
  engine.
- **Liskov.** Every leaf's `as_scad` result is presentable: an authored
  object or a description; every SCAD-authored leaf, built-in or legacy,
  answers the predicate and keeps its `.scad` through the sweep alike;
  `OpenScadUnavailable` substitutes for `ScadEngineUnavailable` wherever the
  latter is caught.
- **Interface segregation.** The contract grows by the two operations the core
  now calls (`scad_text`, `require_binary`), not by the runner's, which cycle
  7 adds when its consumer moves.
- **Dependency inversion, above all.** The core depends on its own
  description and the seam's contract; it imports neither SolidPython nor the
  engine's modules (only the leaf `node/solid2.py`, until cycle 7). The engine
  depends on the core (the description types, `ScadEngineUnavailable`), never
  the reverse.

### 11. Empirical validation (run by the orchestrator)

- **Deep, Locks/Pin_tumbler_lock**, for continuity with the fifth cycle: a
  running root with `Solid2Node` parts, a sub-assembly, symbolic laws and a
  flexible spring, so the presentation of authored geometry, assemblies with
  symbolic operations and a flexible snapshot all run. Legs as the fifth
  cycle's after leg, into a scratch build directory: `machinome build`,
  `machinome test --faceted`, `machinome export --set key_delta=0`; the
  SHA-256 of every `.scad` (never the STL: OpenSCAD's STL bytes vary run to
  run) and of `manifest.json`. Expected after the build leg: exactly 11
  `.scad` files, the `OriginalPart` (`Solid2Node`) leaves'
  `simulation/parts-*.scad`, each byte-identical to the fifth cycle's hash
  for the same path, and none of `simulation/lock-PinTumblerLock-*.scad`,
  `simulation/lock-Plug-*.scad`, `simulation/flexibles-PenSpring-*.scad`, nor
  the `PenSpring`'s per-binding snapshot STL. Expected after all three legs:
  every `.scad` is a `simulation/parts-*.scad` of the fifth cycle's set, each
  byte-identical, and every `lock-*` and `flexibles-*` file of that set is
  absent (the test leg's further parameter sets add `parts-*` files of their
  own, as they did then; no leg after the build sweeps).
- **Snapshot on demand**, after those legs, into the same scratch build
  directory: `machinome snapshot --renderer openscad` of the root (PNG
  existence and size, not bytes; `xvfb-run` when no `DISPLAY`, which the
  renderer wraps itself). Expected: the PNG; the root's
  `simulation/lock-PinTumblerLock-*.scad` present, every
  `import(file = ...)` in it naming a file that exists relative to its
  directory, its SHA-256 recorded (not compared with the build's: the
  snapshot binds its keyframe, so it presents the pose numerically where
  the build's presented `$t`); no `lock-Plug-*` or `flexibles-*` `.scad`.
  Then `machinome build` into the same directory again: the root's `.scad`
  is gone and the 11 `parts-*` files remain. Then the snapshot with
  `machinome.openscad.engine` made unfindable by the finder's
  `sitecustomize`: refused naming the renderer, the module, reinstalling
  machinome and `--renderer web`, exit 1, no PNG and no root `.scad` (before
  the change: an image).
- **Lingering files**: a scratch build directory seeded with a copy of the
  project's own `_build/` (`cp -a`; 31 `.scad` files from earlier builds on 3
  October 2026, among them `lock-*`, `flexibles-*`, `poses-*`,
  `_probe_old-*` and other parameter sets' `parts-*`), then `machinome
  build` into it. Expected: exactly the 11 `parts-*.scad` of the current
  tree remain, with their currency records; every other `.scad` and its
  record is gone. The project's own `_build/` is only read.
- **`develop` without a display.** Nothing to launch: (a) the viewer-hidden
  probe of Context, as a script (refusal, exit 1, no process started); (b) the
  develop builder alone, `run_builder`'s `Builder(<ref>, watch=False,
  lifecycle=True)` (with `scad_output=False` on the unmodified tree, a
  parameter this change removes) in a subprocess into a scratch build
  directory: expected, before and after, the 11 `Solid2Node` `.scad` files
  and no other. This stands in for the fallback the plan names, which
  ADR-103 removed; after the change it is also what `machinome build`
  writes.
- **Engine absent on a real project, OpenAstroMount** (all `StepNode` leaves
  under assemblies; the `exact-engine` cycle's project): `machinome build`
  into a scratch build directory with `solid2` made unfindable. Expected
  before: `ModuleNotFoundError` for `solid2`; after: success, the document
  and every STL and BREP, no `.scad`, nothing logged about SCAD. Cost
  unmeasured (95 STEP leaves rebuilt in a scratch directory); the
  orchestrator may drop this leg if it is too slow, since the framework
  tests carry the same proof on fixtures.
- **Shallow, the universe**: `scripts/load-projects` with the five previous
  moved-names files and this cycle's (empty), `--timeout 300`. Expected: no
  row for this cycle; carried: `3D-Printers/Voron-2`,
  `Actuators/Internal-Cycloidal-Actuator`, `Robots/YouCanBuildDog`,
  `Robots/openvmp` (`don1`) `expected`; `3DPrintedClocks` `wall_clock_41` and
  `Robotic-Arms/Dum-E` `unexpected`; six `no-model`.

## Risks / Trade-offs

- [A leaf outside the core composes `artifact_import()` into SolidPython] →
  none found (projects, machinome-freecad, machinome-mechanics); the changelog
  says so; Decision 6 names the stricter alternative.
- [Code or tests rely on `assemble()` returning a SolidPython object] → no
  project uses the return value; the framework tests that render it
  (`test_generation_dedup.py`, `test_stl_node.py`, `test_sheet_leaf.py` and
  others) are rewritten onto `scad_text`.
- [Code or tests rely on a build or `assemble()` leaving an assembly's or a
  native leaf's `.scad` on disk] → no project reads `_build/*.scad` (grep, 3
  October 2026); the framework tests that read one call `generate_scad()` on
  that node first, or assert its absence where build output is the subject
  (tasks 7.2).
- [A person opened a build's `.scad` in the OpenSCAD GUI] → no named project
  relies on it; the changelog states the removal as BREAKING and the
  on-demand route (`machinome snapshot --renderer openscad`, `scad_code`).
- [A concurrent build removes the snapshot's root `.scad` before OpenSCAD
  reads it] → the render fails naming the file, where today the same
  interval silently drew the build's pose (Decision 3).
- [A `.scad` byte moves] → by construction it cannot; two goldens and the
  lock's 11 hashes would show it, and the cycle stops for the orchestrator.
- [A SCAD-authored leaf's `.scad` swept while still needed] → it is kept by
  reference for as long as its node is in the published tree; a stale leaf
  rewrites it before its STL is rendered, inside the same build.
- [`scad_engine()` imports SolidPython during the first `assemble()`] → it is
  imported at `node.base`'s import today; the cost moves later, not up.
- [The engine-absent install is artificial in layer 1] → yes: SolidPython is
  required until cycle 7. The finder-based tests and the OpenAstroMount leg
  are what layer 2 will rely on.

## Migration Plan

Projects: nothing to do; no importable name moves (`moved-names.toml` is
empty). A project's next build removes the `.scad` files earlier builds left
for its assemblies, fusions, flexible and native leaves. A person who wants a
machine's SCAD runs `machinome snapshot --renderer openscad` (the root's, in
the build directory until the next build) or reads `node.scad_code`.
Framework tests that patch `machinome.node.base.require_openscad` patch
`machinome.openscad.binary.openscad_binary` instead. Rollback is reverting the
implementation commit; the next build after a rollback writes the
presentation files again, and no artifact or document needs rebuilding beyond
the verdict store's automatic reset.

## Open Questions

None at ratification (3 October 2026). The pilot chose A. The orchestrator
confirmed the reviser's four decisions: the builder no longer calls
`assemble()` (its assembly phase and `scad_output` go, and a build no
longer writes a flexible leaf's per-binding snapshot STL, which only the
assembly SCAD imported; the applier's red tests and the full suite are
the check that nothing else read it, and a contradiction there is a stop);
ADR-086's coalescing stays in place and its removal is deferred; the
refusal by name for an absent engine holds for a project leaf overriding
`as_scad`, while `Solid2Node` and `OpenScadNode` import solid2 at module
top until cycle 7; `--renderer web` and `Sim(meshes=True)` still call
`assemble()` until cycle 7 decides where the flexible snapshot belongs.
Decision 6 (`artifact_import` returning the description, leaf contract
at 1) is accepted.

### As proposed before ratification (record)

None for the pilot. Decision 3 is the pilot's (A, 3 October 2026). Decision
6 (`artifact_import` returning the core's description, the leaf contract at
1) is accepted by the orchestrator. Names stay provisional until
ratification: `machinome.node.presentation` and its six types, `scad_text`,
`require_binary`, `presented`, `ScadEngineUnavailable`, `scad_authored`.

## Deferred

- Cycle 7: the runner (`stl_builder_command_for`, `generate_stl`'s `Popen`,
  `StlRenderStart`) and the snapshot renderer's OpenSCAD command line as an
  engine subpackage; `Solid2Node` and `OpenScadNode` as node modules over the
  engine, `node/solid2.py`'s binary reach and `scad_render`, `node/openscad.py`'s
  SolidPython parsing; `Solid2Node.as_number`; the `openscad` extra, replacing
  this cycle's two remedies and giving a project of `Solid2Node` or
  `OpenScadNode` leaves its refusal without SolidPython; whether `machinome
  snapshot --renderer web` and `Sim(meshes=True)` should prepare rather than
  assemble (both still publish a flexible leaf's per-binding snapshot STL
  while composing a description nothing writes).
- Cycle 8: the template.
- ADR-086's assembly-phase coalescing of non-rigid SCAD (`Phase.coalesces_scad`,
  `defer_scad`, `build-pipeline`'s "Stable-generation work is shared without
  redundant writes"): its only production producer was an assembly's `.scad`
  written in the builder's `assembly` phase, which this change removes. Its
  tests drive it directly and stay green; the mechanism and the
  requirement's non-rigid clause are candidates for removal, not this
  cycle's.
- `LeafNode._render_can_be_skipped`, which consults `.scad` currency and has
  no production caller since ADR-102: a candidate for removal, not this
  cycle's.
- Outside the framework: the workspace contract's and the studio skills'
  description of a `develop` OpenSCAD fallback and `--openscad`, removed by
  ADR-103 (proposal.md, Impact). The studio's contract skill needs no line
  changed by this cycle.
- Candidate ADRs, named not written: **ADR-172** (NODE), "The core describes
  its SCAD presentation and the OpenSCAD engine writes it" (the description,
  contract 2, expressions as values, the binary through the seam; amends
  ADR-102's compatibility consumer, ADR-116's re-anchoring mechanism,
  ADR-171's reaches); **ADR-173** (BUILD), "SCAD is written only where it is
  read" (the pilot's decision: a SCAD-authored leaf's `.scad` for its STL,
  the root's on demand for the OpenSCAD snapshot renderer in the build
  directory, the builder no longer presenting, the sweep keeping a `.scad`
  by reference; B recorded as rejected; `require_scad_engine` and its
  remedies; amends ADR-102's consequences, ADR-046's refusal family and
  ADR-086, whose coalescing loses its producer).
