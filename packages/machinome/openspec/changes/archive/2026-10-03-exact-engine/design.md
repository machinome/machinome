## Context

This is item 3 of the lean-core campaign plan (`workflow/ongoing/lean-core.md`,
"What it takes"), cut first by the orchestrator's sequencing. The plan's
sections "Import paths" (especially "The seams"), "machinome-occt, LGPL-2.1"
and "Facts established on 1 October 2026" govern it. Facts below were read in
the bench at feb23f2 on 2 and 3 October 2026 unless marked *inferred*.

This revision folds in the pilot's ruling on the first draft: "`machinome.exact`
in the core providing a bare OCCT shape is core providing a capability of the
occt satellite. A model that is purely OpenSCAD based should have no BREP." Read
by the orchestrator and confirmed by the pilot: the core holds no OCCT code and
defines no operation on OCCT shapes under its own name; `machinome.exact`
disappears, its operations move into the engine; the core keeps only what an
abstract exact node needs; the core's specs never name OCCT's type, and the
currency becomes the engine's decision.

### The originating evidence

- **machinome-freecad's adapter** (`machinome_freecad/adapter.py`,
  `_leaf_class`, read-only). Its exact leaf subclasses `ExactLeafNode`, declares
  `namespace = 'cadquery'`, and its `render()` reads a FreeCAD BREP with
  `BRepTools.Read_s` into a bare `TopoDS_Shape`, then imports cadquery only to
  return `cq.Shape.cast(shape)` and call `.Solids()` and `.isValid()` on it.
  Its `materialize()` imports `machinome.exact._evict` twice: once after
  restoring backups on `SourceChanged`, once after a native recipe change
  replaced a BREP "while source mtime stays equal".
- **The dependency chain** of the plan's table: cadquery is reached from
  `exact.py` and the STEP and molejo adapters; cadquery-ocp from `exact.py`,
  `step.py` and `test.py` (four lazy OCP imports in `_mutually_outside`).
- **The pin coupling**: cadquery 2.8 → cadquery-ocp 7.9; build123d 0.11 →
  cadquery-ocp-novtk; the forced co-install blocks both (ADR-047's
  consequence, the `pyproject.toml` comment). The core pins no cadquery-ocp
  itself: cadquery 2.7.0 requires `cadquery-ocp<7.9,>=7.8.1` and build123d
  0.10.0 `cadquery-ocp<7.9,>=7.8` (installed metadata; the venv holds
  7.8.1.1.post1).

### What `machinome/exact.py` mixes today (548 lines)

1. **OCCT operations**: placement (`_place`), fuse and common (`_boolean`),
   the empty-common witness (`_false_empty_witness`, `_resolved_interior`),
   solid counting and volume, bounding boxes, per-face boxes, BREP read and
   write, STL tessellation.
2. **Process identity and caches**: `_shape_cache` keyed `(path, float mtime)`,
   `_shape_keys` by `id()`, `_shape_observations` (ADR-156), `_bounds_cache`,
   `_face_box_cache`, the bounded `_placement_cache`, `_evict`,
   `_reset_placement_cache`.
3. **Artifact publication**: `_atomic_export` (temporary file, mtime stamp,
   `currency.publish` with digest and fingerprint) and the degenerate-triangle
   cleanup with trimesh.
4. **Node-attribute validation**: `deflections(node)`.
5. **Front-end recognition**: `build123d_shape` (build123d by module name, a
   builder's `.part`) and `shape_from_rendered` (CadQuery's `Workplane.vals()`,
   `Compound.makeCompound`).

Its CadQuery dependency is wider than the plan's four spellings: those are the
only `cq.` calls, but the module and the test kernel then call CadQuery `Shape`
*methods* on the currency: `Solids`, `Faces`, `Edges`, `Vertices`, `Volume`,
`BoundingBox`, `copy`, `exportBrep`, `exportStl`, `distance`, `positionAt`,
`Length`, `toTuple`, `.wrapped`. Each has a plain OCP equivalent, read from
cadquery 2.7.0's own source in the venv (table in Decision 4).

Job 1, and the containment guard in `test.py`, are OCCT code: they go to the
engine. Jobs 2, 3 and 4 key on files, bytes, object identity and node
attributes, not on shapes: they stay in the core. Job 5 goes to the adapters.

### Who imports `machinome.exact` today

Verified by grep. The plan's list also names `node/adapters/{step,stl,molejo}.py`,
`node/declarative.py`, `core/loader.py` and `simulation/__init__.py`; those
only mention it in docstrings or comments (`molejo.py` imports cadquery itself,
not the exact layer; `declarative.py` does not mention it at all).

| importer | what it takes | after this change |
|---|---|---|
| `node/exact_leaf.py` (module top) | `cached_shape`, `deflections`, `shape_from_rendered`, `write_brep`, `write_stl` | `exact_cache.cached_shape`; `exact_artifacts.{deflections,write_brep,write_stl}`; conversion becomes the method `ExactLeafNode.shape_from_rendered` over `engine.as_shape` |
| `node/fusion.py` (module top) | `cached_shape`, `deflections`, `fuse_shapes`, `placed_shape`, `write_brep`, `write_stl` | `exact_cache.{cached_shape,cached_placement}`, `exact_artifacts.*`, all kernel-free at module top; the engine is resolved inside the exact branch and `engine.fuse_shapes` called on it |
| `node/adapters/build123d.py` | `build123d_shape` | the function moves into this module, returning `.wrapped`; validation counts solids through the engine |
| `node/adapters/build123d_sheet.py` | `_atomic_export` | `exact_artifacts._atomic_export` |
| `test.py` (deferred, 9 names) | `cached_bounding_box`, `cached_face_boxes`, `shape_identity`, `shape_load_observation`, `fuse_shapes`, `intersect_shapes`, `placed_shape`, `solid_count`, `solid_volume` | memos looked up on `machinome.exact_cache` at call time; operations on the resolved engine; `_deferred_exact` goes (Decision 8) |
| `manager/test.py` | `sys.modules.get('machinome.exact')._reset_placement_cache()` | imports `exact_cache` directly (now free) |
| `tests/` | 19 files name `machinome.exact`; more patch names on `machinome.test` | repointed (task group 5) |
| machinome-freecad | `_evict` | breaks; next cycle (it is pinned to `machinome==0.7.1` and refuses any other version at construction) |
| projects | `intersect_shapes` ×12 files, `placed_shape`, `solid_volume` (OpenAstroMount) | import line moves to `machinome.occt.engine` (the one-path cycle's rewrite script; OpenAstroMount by hand here) |

## Goals / Non-Goals

**Goals:**

- The core holds no OCCT code and names no OCCT type in its specs; a model
  with no exact node never imports the engine.
- One exact engine seam in the core, of `mesh_engine.py`'s shape, resolving
  the known provider `machinome.occt.engine`, refusing absence by install line
  and a contract mismatch by both versions.
- Every OCCT operation of the exact layer and the test kernel rewritten on bare
  OCP, at the engine's final address, importing no cadquery, each defined once
  under one name.
- The engine's currency fixed by the engine (Decision 3), in its own spec and
  ADR, which leave with the code at the cut.
- Unchanged geometry: same BREP and STL bytes, same verdicts, same recipe
  identity.

**Non-Goals:**

- No change to required dependencies: cadquery, build123d, cadquery-ocp and
  molejo stay required (plan item 4). The `occt` extra is declared as
  metadata only (Decision 12).
- No change to `StepNode`'s reader, its `adjust` argument or
  `solids_from_faces`; it keeps importing cadquery and OCP.
- No declared extension contract and no public eviction (plan item 1, next
  cycle); no class-name switch removal (item 2); no markings change.
- No new repository; the engine directory, its spec and its ADR are cut into
  machinome-occt by the cut cycle.

## Decisions

### 1. The seam: `machinome/exact_engine.py`

Same shape as `machinome/mesh_engine.py`, plus the contract:

- `CONTRACT = 1`, the exact engine contract version the core speaks.
- Three `typing.Protocol` classes, `ExactCurrency`, `ExactComposition` and
  `ExactComparison`, and `ExactEngine` combining them: the operations the core
  calls (Decision 5), each documented, each named exactly as the engine
  defines it. This is the contract text; it names operations, never a type
  (the currency is annotated as an opaque `Any`-like alias, `ExactShape`,
  documented as "the engine's currency").
- Errors: `ExactEngineUnavailable(needed_by, reason)` (message names the exact
  engine, both arguments and `pip install "machinome[occt]"`, the viewer's
  quoted spelling), `ExactEngineIncompatible` (names `CONTRACT`, the provider's
  declaration or "declares none", and `machinome.occt.engine`), and the two
  common-guard errors `ExactCommonInconsistency` and
  `ExactCommonVerificationError`, which move here from `exact.py` because the
  engine raises them and the core, tests and projects catch them: both sides
  depend on the contract module, not on each other.
- `exact_engine()`, `functools.lru_cache(maxsize=1)`: `importlib.import_module(
  'machinome.occt.engine')`; a `ModuleNotFoundError` whose `.name` is
  `machinome.occt` or `machinome.occt.engine` answers `None`; any other import
  error propagates (the `cli-startup-cost` broken-installation rule; this is
  where it deliberately differs from `mesh_engine()`, which catches every
  `ImportError`); then the contract check (Decision 6). An exception is not
  cached by `lru_cache`, so a refused engine is refused at every ask.
- `require_exact_engine(needed_by, reason)` returns the engine or raises
  `ExactEngineUnavailable`.

Rejected: an entry-point group or a provider registry (D2 settled it).

### 2. What stays in the core, what goes to the engine

**The engine**, `machinome/occt/`:

- `machinome/occt/__init__.py`: licence header and a docstring, no names (the
  ports spec's sentence, which the plan extends to an engine package).
- `machinome/occt/engine.py`: one module, both the provider the seam resolves
  and the project's address for the exact operations. `CONTRACT = 1` as its own
  literal; the 13 operations of Decision 5, each defined once under the name
  the core's Protocol uses; the private helpers (`_boolean`,
  `_false_empty_witness`, `_resolved_interior`, `_representative_points`,
  `_classified_out`, the subshape walkers of Decision 4); OCP and numpy imports
  at module top. From the framework it imports only `machinome.exact_engine`,
  for the error types. It does not import trimesh, `machinome.currency`,
  `machinome._artifact` or any core cache. It keeps no state: every operation
  is a function of its arguments. Its licence header is the core's Apache-2.0
  while it ships in the core; the cut cycle gives machinome-occt its LGPL-2.1
  (the plan's ruling; every commit touching `exact.py` is Luis Fagundes's, per
  `git log --follow`).

**The core**, none of it OCCT code:

- `machinome/exact_engine.py`, the seam (Decision 1).
- `machinome/exact_cache.py`, new: memos over opaque handles and artifact
  files (Decision 9): `cached_shape`, `shape_identity`,
  `shape_load_observation`, `cached_bounding_box`, `cached_face_boxes`,
  `cached_placement`, `_evict`, `_reset_placement_cache`.
- `machinome/exact_artifacts.py`, new: publishing an exact shape's artifacts.
  `_atomic_export` (unchanged), `write_brep` (engine writes to the temporary
  path), `write_stl` (engine writes the raw STL to the temporary path, then
  the trimesh degenerate-triangle cleanup, imported where used),
  `deflections`.
- `node/exact_leaf.py`, `node/fusion.py`, the adapters and `test.py`, which
  pass shapes as handles and call the engine through the seam.
- `machinome/exact.py` is **removed**.

**Why one engine module and not two.** The pilot's rule is one name, one path.
The core needs the five project-facing operations too (the test kernel
intersects, counts and measures; fusion fuses and places), so with one module
the Protocol simply names them by their public names and nothing is defined
twice. Splitting the package into a provider module and a public module would
force one of three things the rule forbids or the seam cannot do: the provider
re-exporting the public functions, two functions per operation
(`intersect` beside `intersect_shapes`, the first draft's shape), or a seam
resolving two modules. One module is the simplest shape that satisfies the
rule. Its cost is that a project can also reach the contract operations it
does not need (`as_shape`, `compound`, `bounds`, the file operations); see
the SOLID review and Open Questions.

**Why `machinome.exact` goes rather than staying as five thin functions.** The
first draft kept it because it was a public address. Under the ruling, a core
module defining `intersect_shapes` over OCCT shapes is the core offering the
OCCT package's capability; and five functions that resolve the engine and call
the same five functions on it would be two names at two paths for one
operation. Projects import the engine's module instead, exactly as the plan
has them import a node package's module; a missing engine there is Python's own
`No module named 'machinome.occt'`, which rule 2 of "Import paths" turns into
the install line, as for every satellite.

Rejected: moving the caches, publication and validation into the engine (the
first draft's rejected option, still rejected: the engine would import core
privates `machinome.currency` and `machinome._artifact` across a package and
licence boundary, and the next cycle's fix for `_evict` would have to be made
in the engine; Decision 9).

### 3. The currency: the engine's decision

What `shape()` returns and what the engine's operations pass around once
cadquery is out of the exact layer. The core does not decide it: its specs say
`shape()` returns the exact engine's currency, one type for every exact node,
never a front end's object, which a consumer rewraps for a front end's
methods. The engine decides the type, in its own capability spec
(`occt-engine`, "The engine's currency is the kernel's own shape") and its own
ADR (ADR-160), both leaving with the code at the cut. It is still put to the
pilot, now as the engine's decision, in the form to relay:

> **A. Bare `OCP.TopoDS.TopoDS_Shape` (recommended and expected).** The type
> OCCT, OCP, CadQuery (`.wrapped`), build123d (`.wrapped`), molejo
> (`result.solid`) and FreeCAD's BREP transfer already hand around; the engine
> adds no type and the contract carries the kernel's own object. Cost: project
> code calling CadQuery methods on `shape()` or on the engine's results wraps
> it, `cq.Shape.cast(...)`: 29 project files on 2 October 2026.
> **B. A thin engine-owned wrapper** holding the `TopoDS_Shape`: the same
> project cost (it cannot offer CadQuery's methods without re-implementing
> CadQuery), plus a second type every front end, molejo and FreeCAD must wrap
> and unwrap, and a type the engine contract must version.

Consequences, option by option:

| where | A: bare `TopoDS_Shape` | B: engine wrapper (`Shape` with `.wrapped`) |
|---|---|---|
| CadQuery adapter | `Workplane.vals()` → each `.wrapped`; several → `engine.compound` | the same, then wrap |
| build123d adapter | `.wrapped` (builder `.part`); no cast | `.wrapped`, then wrap |
| `StepNode` | document shape is `TopoDS`; this cycle `adjust` still gets `cq.Shape.cast(...)` and its result is unwrapped by `.wrapped`; at the step package's cut `adjust`'s argument becomes `TopoDS` unless that package keeps cadquery (its decision) | the same, plus wrap |
| `MolejoNode` | returns `result.solid`; cadquery import dropped | wraps `result.solid` |
| `FlexibleNode` | nothing: its memo compares `result[0] is shape` | nothing |
| fusion | engine ops on `TopoDS` | engine ops unwrap and rewrap |
| test kernel | `cached_bounding_box` returns `((xmin, ymin, zmin), (xmax, ymax, zmax))`; the containment guard is an engine operation | the same, through the wrapper |
| verdict memo (ADR-156) | unaffected: in-process identity is the cache key found by `id(shape)`, persistent identity is the SHA-256 of the BREP bytes, which do not change; neither involves the shape's type | unaffected, unless the wrapper takes over identity (a design change B would invite) |
| machinome-freecad | `render()` may return the `TopoDS_Shape` with `namespace = 'OCP'` and drop cadquery; returning `cq.Shape` still works through `.wrapped` | must import the engine's wrapper to return one, or rely on `.wrapped` |
| next cycle's exact-leaf contract | "`render()` returns what the engine admits; `shape()` returns the engine's currency" | the contract must specify the wrapper's methods and version them |
| projects | `cq.Shape.cast(node.shape())` where CadQuery methods are called | the same |

B's one real advantage, an owned identity (`__eq__`/`__hash__`) in place of
`_shape_keys` by `id()`, is not needed: the core's cache already owns identity
and the next cycle's fix for `_evict` is a key change, not a type change.

Rejected outright: **C**, `shape()` returns each front end's own type and a
fusion returns `TopoDS` (a fusion's shape and its children's would differ in
type, breaking substitutability); **D**, keep CadQuery's `Shape` this cycle
and change it at the cut (the engine would import cadquery to cast, an interim
shape existing only to be replaced).

The core's specs are written so either A or B satisfies them; the
`occt-engine` spec is written for A. Taken as A at ratification on 3 October
2026 by the orchestrator, under the pilot's ruling that the currency is the
engine's decision and its stated expectation of the bare shape; recorded so
the pilot may overrule before the implementation commit, which would change
only the engine's spec, its `as_shape` and ADR-160.

### 4. Conversion at the adapter boundary; the CadQuery-to-OCP table

`ExactLeafNode.shape_from_rendered(self, rendered)` replaces the free function;
its default is `require_exact_engine(...).as_shape(rendered)`: the currency as
is, else a `.wrapped` that is one, else `TypeError` naming the type.
Overrides: `CadQueryNode` and `StepNode` call `workplane_shape(rendered,
engine)` defined in `node/adapters/cadquery.py` (`.vals()`; empty →
`ValueError('CadQuery render produced no shape')` as today; one → `as_shape`;
several → `compound`); `Build123dNode` uses its module's `build123d_shape`. The
hook is a method so the next cycle can declare it or not; it is not declared
here.

The engine reproduces each CadQuery call exactly, so results and bytes match:

| CadQuery | OCP in the engine |
|---|---|
| `Shape.cast(x)` | identity on the `TopoDS_Shape`; `TopoDS.Face_s`/`Edge_s`/`Solid_s` where an API needs the subtype |
| `Shape.importBrep(p)` | `BRepTools.Read_s(s, p, BRep_Builder())`, `ValueError` if `IsNull()` |
| `exportBrep(p)` | `BRepTools.Write_s(s, p)` |
| `exportStl(p, tolerance, angularTolerance)` | `BRepMesh_IncrementalMesh(s, lin, True, ang, True)`; `StlAPI_Writer`, `ASCIIMode = False` |
| `Compound.makeCompound` | `TopoDS_Compound` through `TopoDS_Builder.MakeCompound`/`Add` |
| `Vertex.makeVertex` | `BRepBuilderAPI_MakeVertex(gp_Pnt(...)).Vertex()` |
| `Solids/Faces/Vertices` | `TopExp.MapShapes_s` into `TopTools_IndexedMapOfShape`, in index order |
| `Edges` | the same, dropping `BRep_Tool.Degenerated_s` edges |
| `copy()` | `BRepBuilderAPI_Copy(s, True, False).Shape()` |
| `Volume()` | `BRepGProp.VolumeProperties_s` on each solid |
| `BoundingBox()` | `BRepBndLib.AddOptimal_s(s, box)` with its defaults |
| `distance(other)` | `BRepExtrema_DistShapeShape` with `SetMultiThread(True)`, `.Value()` |
| `Length()`, `positionAt(f)` | `GCPnts_AbscissaPoint.Length_s(BRepAdaptor_Curve(e))`; parameter by `GCPnts_AbscissaPoint(c, L·f, c.FirstParameter())`, point `c.Value(u)` |
| `toTuple()` | `BRep_Tool.Pnt_s(vertex)` → `(X, Y, Z)` |

Probe, 2 October 2026, two separate processes in the bench: a CadQuery box
fused with a cylinder through the current `fuse_shapes`, written by CadQuery's
`exportBrep` and `exportStl(tolerance=0.1, angularTolerance=0.1)` and by the
raw OCP calls above: BREP SHA-256 `509c27cdd1c8100a…` and STL
`3d1bb8cd4dfe2059…` both times and both ways; volume 1282.743338823081, one
solid.

### 5. The engine contract, version 1, segregated by consumer

The provider module satisfies `ExactEngine`; its three component Protocols
group the operations by who calls them (the SOLID review, interface
segregation), and each core consumer is written against the one it uses. The
names are the engine's own; the five project-facing operations are marked †.

- **currency I/O** (exact leaves, fusion, `exact_cache`, `exact_artifacts`):
  `as_shape(obj)`, `compound(shapes)`, `read_brep(path)`,
  `write_brep(shape, path)`, `write_stl(shape, path, linear_deflection,
  angular_deflection)`;
- **composition** (fusion, `exact_cache.cached_placement`, `assertJoined`):
  `placed_shape(shape, matrix)` † with the framework's composed 4×4 matrix,
  of which the engine sends the upper three rows as exact IEEE-754 values;
  `fuse_shapes(first, second, first_name, second_name)` †;
- **comparison and measurement** (`exact_cache`, the test kernel):
  `intersect_shapes(first, second, first_name, second_name)` † with the
  witness and its two refusals, `solid_count(shape)` †, `solid_volume(shape)` †,
  `bounds(shape)`, `face_bounds(shape)` (an `(F, 2, 3)` float64 array,
  `useTriangulation=False` as today), `mutually_outside(first, second)` (the
  containment guard, declining with `False`).

The project-facing operations accept anything `as_shape` admits, as
`machinome.exact` accepted CadQuery shapes; the others take the currency.
`copy` stays private to the engine (the Booleans and the witness copy their
own operands, as today).

### 6. The compatibility declaration and check

The viewer's pattern: the provider states an integer, the framework compares.
`machinome.occt.engine.CONTRACT = 1`, a literal; `machinome.exact_engine.CONTRACT
= 1`. `exact_engine()` reads `getattr(module, 'CONTRACT', None)`; unequal or
absent raises `ExactEngineIncompatible`. Equality, not a range: the engine is
numbered with the framework (D7) and a contract change bumps both. At the cut
the same integer is also declared in the package metadata the standard's
section 1.2 asks for; in this cycle the engine ships inside the core, so a
mismatch is exercised only by a stub provider in tests. A conformance test
checks every `ExactEngine` member exists on the provider. A project importing
`machinome.occt.engine` directly bypasses the check; in this cycle the two
cannot differ, and at the cut the engine package's dependency pin on the core
(`machinome~=0.8.0`) guards it.

### 7. Fusion and leaves resolve the engine lazily, and not for current artifacts

`node/fusion.py` imports `exact_cache` and `exact_artifacts` at module top;
neither imports the engine. The exact branch of `shape()` and
`generate_stl()` resolves it through `require_exact_engine(f'exact fusion
{self.name}', ...)` before any exact work; a current fusion returns from
`generate_stl()` before that, and `shape()` on a current fusion loads its BREP
through `cached_shape`. `geometry_recipe` keeps `exact-fusion-occt-v1`: the
fuse is the same OCCT call on the same operands with the same copies and
parallel flag, and its BREP bytes are unchanged (Decision 4's probe), so an
artifact built before this change is the artifact this change would build.
`_generate_faceted_stl` is untouched.

Finding, verified in the code: `ExactLeafNode.materialize` calls
`shape_from_rendered(rendered)` before its two `_up_to_date` checks, and
`Node._prepare` (`node/base.py`, near line 960) calls `materialize` whenever
`_prepare_can_be_skipped()` is false, which it always is for a leaf declaring
`optimize = False`, current artifacts or not. Such a leaf would convert, and so
resolve the engine, for nothing. The conversion moves after the checks, into
the branch that writes. Whether the
builder reaches any other exact path for a current fusion is *not verified*;
task 2.2's red test for "A current exact fusion does not resolve the engine"
decides it, and the task says to return the evidence rather than weaken the
spec if the code cannot keep the promise.

### 8. The test kernel orders; the engine operates

`machinome/test.py` keeps the culling order and holds no OCCT code:

- `_deferred_exact` and the nine module-level names go. The exact path calls
  memos as attributes of `machinome.exact_cache` (`exact_cache.cached_face_boxes(
  ...)`) and operations as attributes of the engine it resolved
  (`engine.intersect_shapes(...)`), looked up at call time. That keeps one path
  per name (the cli-startup-cost delta) and keeps patching working: a test
  patches a name where it is defined, and every core path sees the patch.
- `_mutually_outside`, `_representative_points` and `_classified_out` move into
  the engine as `mutually_outside` and two private helpers; `_faces_disjoint`
  calls `engine.mutually_outside`. No delegating function stays behind.
- `_exact_verdict`'s AABB cull reads the tuple bounds; its placements use
  `exact_cache.cached_placement`; `assertJoined`'s union uses
  `cached_placement` and `engine.fuse_shapes`; the solid-count assertion uses
  `engine.solid_count`.
- The exact branch resolves the engine naming the assertion, as
  `require_mesh_engine` does on the faceted branch.

Chosen over keeping lazy OCP imports in `test.py` to be moved at the cut:
those imports would make the core name OCP until the cut and move the same
code twice, and the plan already lists them as the engine's.

### 9. Caches: memos over opaque handles stay in the core

The principle: a memo that serves the core's own paths may stay in the core
when it is kernel-agnostic memoization calling contract operations; no core
module reads, measures or places a shape itself. Each cache, decided:

| cache | goes to | why |
|---|---|---|
| loaded-BREP cache `_shape_cache` `(path, float mtime)`, its identity map `_shape_keys` by `id()`, `_evict` | core, `exact_cache.cached_shape` calling `engine.read_brep` | keyed on files and object identity; `_evict`'s replacement is the next cycle's core change |
| load observations `_shape_observations`, `shape_load_observation`, `shape_identity` | core, `exact_cache` | they read `machinome._artifact.observe_artifact`, a core private the engine must not import; the verdict memo in the core reads them |
| bounds memo `_bounds_cache`, face-box memo `_face_box_cache` | core, `cached_bounding_box`/`cached_face_boxes` calling `engine.bounds`/`engine.face_bounds` | keyed on the identity only the core knows; they store tuples and numpy arrays, not shapes |
| placement memo `_placement_cache`, LRU of 512, `_reset_placement_cache` | core, `cached_placement(shape, matrix)` calling `engine.placed_shape` | keyed on identity and the matrix's packed bytes, computed in the core from numbers; `manager/test.py` resets it per run |
| verdict memo (ADR-156) and `_verdict_store` | core, unchanged | keys on artifact bytes and observations |
| anything in the engine | nothing | the engine is stateless; caching is its caller's choice |

`shape_identity` and `shape_load_observation` keep serving the verdict memo
exactly as today: `cached_shape` records the key by `id()` of the object
`engine.read_brep` returned and the observation taken before and after the
read; `shape_identity(shape)` is a dictionary lookup by `id()`, and
`_persistent_identity` digests the observed BREP bytes. Neither looks at the
shape, so neither depends on the currency's type. The memo for placement is
named `cached_placement`, beside `cached_shape`, `cached_bounding_box` and
`cached_face_boxes`, so the memo and the engine's `placed_shape` are two
different functions with two different names, not one operation at two paths.
A project calling `machinome.occt.engine.placed_shape` gets an uncached
placement; `machinome.exact.placed_shape` was cached. *Inferred* to matter
little: OpenAstroMount places each source solid once per pair.

The `_evict` finding stands. The shape cache keys on `(path, float mtime)`,
while `_atomic_export` stamps every artifact's mtime with the node's source
mtime, so a BREP replaced under an unchanged source (machinome-freecad's
native recipe change, its restore on `SourceChanged`) is the same key and is
served stale; and the cache offers no public invalidation. This cycle moves the
cache unchanged into `exact_cache.py`, so the next cycle can key it on the
artifact observation (`_artifact.observe_artifact`: inode, mtime_ns, ctime_ns,
which a replacement changes), making eviction unnecessary for every subclass,
or publish one call. The fix is deferred to that cycle.

### 10. `StepNode`, `MolejoNode`, `build123d_sheet`

`StepNode` keeps its reader, cadquery and its `adjust` argument; only its
conversion changes (Decision 4). `MolejoNode._snapshot_shape` returns
`(result.solid, result.tolerance)`. `build123d_sheet` takes `_atomic_export`
from `exact_artifacts`.

### 11. Verdict store

`_verdict_store.KERNELS` keeps `('cadquery', 'cadquery')` this cycle: CadQuery
still produces CadQuery leaves' BREPs, and an extra stamp component costs only
invalidation. The stamp's `_package_digest` walks the `machinome` package
directory, so `machinome/occt/engine.py` is covered while the engine ships in
the core; this change alters package source, so the store starts afresh once.
At the cut the stamp must add machinome-occt (deferred below).

### 12. The `occt` extra

`pyproject.toml` declares `occt = ["cadquery-ocp>=7.8.1,<7.9"]` with a comment
that the cut repoints it at machinome-occt. The range is the one the core's
pinned cadquery 2.7 already requires (the core pins no cadquery-ocp of its
own), so installing the extra resolves nothing new and the required list does
not change. From this cycle the refusal's install line names a real extra;
until the cut, the only absent-engine case is a broken install, which the
extra repairs. Rule 2 of "Import paths" names the extra `occt` after the
address `machinome.occt`.

### 13. Where the engine's records live

The engine's capability spec, `occt-engine`, governs behaviour that leaves the
core at the cut, so it leaves with the code (package standard, section 1.3):
the cut cycle moves `openspec/specs/occt-engine/` into machinome-occt's
`openspec/specs/`. The `exact-engine-dependency` capability, the seam, stays in
the core. ADR-160, the engine's currency, is the engine package's ADR: written
now in the framework under a category directory of its own, `docs/adrs/OCCT/`
(settled at ratification), so the cut moves the directory whole and the ADR
keeps its number, as the viewer-owned ADRs did.

### 14. Vet denies the exact internals and the engine's file operations

`machinome.occt.engine` passes vet as a contract member, and so would its
`read_brep`, `write_brep` and `write_stl`, as `machinome.exact.write_brep`,
`_atomic_export` and `cached_shape` pass today; so would
`machinome.exact_artifacts`, which writes through `currency.publish` (itself
denied), and `machinome.exact_cache`, whose `cached_shape` reads a
caller-chosen path. The universe's own rule denies framework modules that
write to a caller-chosen path, and its kernel tier already denies
`BRepTools.Read_s` and `Write_s`. The contract denylist is matched by dotted
name, equal or beneath, as the kernel denylist is (`universe.toml`,
verified), so five entries close the gap: `machinome.exact_cache`,
`machinome.exact_artifacts`, `machinome.occt.engine.read_brep`,
`machinome.occt.engine.write_brep`, `machinome.occt.engine.write_stl`. The
engine module itself, its five project-facing operations, `bounds`,
`face_bounds`, `mutually_outside`, `as_shape`, `compound`, and the seam
module `machinome.exact_engine` (whose error types a project catches) keep
passing. Settled at ratification: this cycle creates the addresses, so it
denies them; the pre-existing gap for `machinome.exact.write_brep` closes
with the module's removal.

## SOLID review

**Single responsibility.** Today `exact.py` mixes the five jobs listed under
Context, and `test.py` holds OCCT classification code. After: `occt/engine.py`
does geometry only (currency, Booleans and transforms, measurement,
classification, BREP read and write, STL tessellation); `exact_engine.py`
resolution and the contract only; `exact_cache.py` memoization over handles
and files only; `exact_artifacts.py` artifact publication only; `test.py` the
order of culling and comparison only; front-end recognition lives in each
adapter. *Bends:* the engine module has two audiences, the core through the
Protocol and projects by import, accepted so each operation has one name at
one path; and one STL artifact is made in two packages, raw tessellation by
the engine and the degenerate-triangle cleanup by the core, because the
cleanup is framework policy (the mesh engine's edge pairing), not kernel work.

**Open/closed.** A new node type needs no core change: it subclasses
`ExactLeafNode`, renders something the engine admits, and the default
conversion takes it (the stand-in leaf of task 2.3 proves it with no
override). *Bend:* a second exact engine needs the seam's known-provider name
changed, the accepted compromise of D2; it is one string in one module.

**Liskov substitution.** Every exact node returns the same currency from
`shape()`, so a fusion, a molejo solid and a leaf are interchangeable to every
consumer. The `_evict` reach (Decision 9) is the remaining violation: a
subclass that replaces its BREP under an unchanged source must reach a private
of the core to stay correct. *Bend:* `_evict` stays private this cycle,
because the extension contract is the next cycle's.

**Interface segregation.** The core consumes the 13 operations of Decision 5,
grouped by consumer: currency I/O for nodes and publication, composition for
fusion and placement, comparison for the test kernel and the memos. A node
package needs none of them to produce geometry: it returns the kernel's own
object. *Bends:* the provider is one module serving all three groups, because
the seam resolves one known provider; and projects importing that module see
the contract operations they do not need, the file operations among them
(Open Questions).

**Dependency inversion.** The core depends on `machinome.exact_engine`
(`CONTRACT`, the `ExactEngine` Protocol, the error types) and never imports
OCP or cadquery on the exact path; the engine depends on the same module for
the error types and declares its own `CONTRACT`. The first draft's bend, a
core facade over the engine (`machinome.exact` resolving the engine and
re-offering its operations), no longer exists. *Bends that remain:*
`node/adapters/step.py` still imports OCP and cadquery (the STEP reader moves
with its package, item 5 and the cut); `machinome/node/markings.py` and
`build123d_sheet.py` still import build123d lazily (the markings reducer waits
for the cut); and the core's memos rely on Python object identity (`id()`) of
handles the engine returns, a property of the language, not of the engine.

## ADRs

Written after implementation, from what the pilot ratified; fresh numbers
(released numbers are not reused):

- **ADR-160, the OCCT engine's currency is the kernel's own shape.** The
  engine package's ADR, leaving with the code at the cut (Decision 13).
  Supersedes ADR-047's chosen option ("one shared currency ... the CadQuery
  `Shape`"), adopting its rejected option 2 now that cadquery leaves the exact
  layer; keeps ADR-047's conversion-at-the-boundary rule. Notes that ADR-057's
  sentence "returns the OCCT solid, recast to the CadQuery `Shape` the exact
  layer trades in" is historical. Taken to the pilot.
- **ADR-161, the core holds no kernel code: the exact engine seam and its
  address.** A core contract module with a known provider
  `machinome.occt.engine`, resolved on first use; exact shapes as opaque
  handles in the core; the removal of `machinome.exact` and the split of its
  jobs into engine, memos and publication; the engine module as the one path
  for its operations. Cites ADR-047, ADR-045 (fusion), ADR-046 (conditional
  dependency), ADR-070 (placement cache), ADR-092 (containment guard),
  ADR-143 (operand copies), ADR-156.
- **ADR-162, a resolved provider declares the contract version it
  implements**, checked by equality at resolve time with a refusal naming both;
  the pattern the `Svg` reducer and `import-step` seams will follow.

Not architectural: the CadQuery-to-OCP translation table, the test kernel's
lookup mechanics, `MolejoNode`'s return value, the docstring corrections.

## Risks / Trade-offs

- [Project breakage on the campaign branch: 12 files import
  `machinome.exact`, 29 call CadQuery methods on `shape()` results] → the plan
  already accepts breakage until the one-path cycle's rewrite; both rows are
  added to that script's scope (deferred), and this cycle validates on one
  project by hand (task 6.3).
- [A translated method diverges from CadQuery's (order of `Solids()`, the
  `relative=True` meshing flag, optimal vs plain bounding boxes)] → the golden
  fixtures of task 1.1 pin bytes and measurements recorded on the unmodified
  tree; the existing witness, face-box and placement-cache suites pin the
  behaviour.
- [Tests that patch exact names on `machinome.test`, about seven files] →
  repointed to the defining module (task 5.1); the cli-startup-cost delta
  states the new rule.
- [`_evict` callers break] → machinome-freecad is pinned to 0.7.1 and the next
  cycle replaces the call.
- [Python `id()` identity on OCP objects] → unchanged mechanism; the cache
  returns the very Python object it stored.

## Migration Plan

One commit for planning, one for implementation, on `v0.8-exact-engine`;
integration into `v0.8` is the orchestrator's. Rollback is reverting the
implementation commit. Artifacts need no rebuild (bytes unchanged); the
verdict store re-fills once.

## Deferred, recorded here so it is not lost

- The markings SVG reducer resolved from `machinome.node.build123d` and its
  refusal by extra (waits for the cut).
- The declared `LeafNode`/`ExactLeafNode` extension contract, the public
  form of `shape_from_rendered`, and the public replacement for `_evict`
  (re-keying the shape cache on the artifact observation is the candidate),
  validated against machinome-freecad on a branch (plan item 1, the next
  cycle, which runs after this one because the contract names the engine's
  currency).
- The class-name switch at `node/base.py:1262` (item 2).
- Dependencies (item 4): cadquery, build123d, cadquery-ocp and molejo leave the
  required list, and the `occt` extra is repointed at machinome-occt; the
  verdict stamp gains machinome-occt's version or digest once the engine
  installs outside the core's package directory.
- The STEP reader (XCAF document, `solids_from_faces`) and `StepNode.adjust`'s
  argument type: the plan places STEP reading in machinome-occt; whether the
  reader moves into the engine or stays in machinome-node-step is decided when
  that package is cut.
- The one-path cycle's rewrite script gains two rows: `machinome.exact` →
  `machinome.occt.engine` on import lines, and `cadquery.Shape.cast(...)`
  around `shape()` results that call CadQuery methods.
- `_verdict_store.KERNELS` dropping cadquery once no core path produces it.
- The engine directory's LGPL-2.1 licence, header and NOTICE, its spec and
  its ADR directory, at the cut.
- The studio's `shop-skills/machinome-api/SKILL.md` lines on `shape()` and
  `machinome.exact`, updated once, at the cut, in the studio repository.

## Open Questions

None at ratification (3 October 2026). The vet reach of the file operations
is Decision 14. Patching at the defining module (Decision 8, the
`cli-startup-cost` delta) was accepted by the orchestrator as the one-path
rule applied to test doubles: a self-replacing wrapper on `machinome.test`
would be a second path to each engine operation.
