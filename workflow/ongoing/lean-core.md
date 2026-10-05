# Lean core: machinome as a core with node and engine packages

Campaign plan, provisional. Written 1 October 2026 in the workspace as
`docs/lean-core-package.md`, revised 2 October 2026 with the import-path
decisions, accepted in scope by the pilot the same day and moved here as
the plan the campaign's OpenSpec changes are cut from; the workspace
copy now points at this file. Working record, not a promise: nothing
here is ratified, no ADR is accepted, and a baseline spec or an accepted
ADR outranks every sentence below. Pilot decisions recorded in the
conversations that produced this note are marked as such. Written from
the code as it stands at Machinome 0.7.1 on `main` and the
machinome-freecad adapter's first worktree.

## Aim and the pilot's decisions

machinome-freecad was split into its own package because its licence is
LGPL-2.1-or-later. The pilot wants the same modularity for the other
kernels, so that machinome is a core with kernel packages around it, and
so that a later decision about the core's grant is possible without
re-architecting. Three decisions bound this note:

- **The core's licence is not changing now.** The work builds the
  architecture that would support a different grant; it does not make
  one. Nothing below depends on the licence.
- **FusionNode stays in core.** Fusing an OpenSCAD part with a JSCAD
  part is a statement about the machine, that two pieces are one piece,
  and belongs beside assembly whatever kernel computes it.
- **Every package is imported from `machinome.something`, under one
  rule** (2 October 2026): a node type is `machinome.node.<nodetype>`,
  installed as `machinome[<nodetype>]`, published as
  `machinome-node-<nodetype>`, one package per node type; anything a
  satellite brings that is not a node type is `machinome.<name>`,
  `machinome[<name>]`, `machinome-<name>`. The pilot chose to maintain
  a universe of packages, each with its own repository, CI and release
  line, over a monolith, so that a project installs only what it
  needs; and settled that machinome-occt carries no node type, that
  machinome-node-molejo is a package of its own in its own repository,
  and that `ExactLeafNode` stays in the core. "Import paths" below is
  the shape.

## Facts established on 1 October 2026

### The dependency chain

The pilot's working premise was that Apache-2.0 is under machinome
because of CadQuery. The chain is wider. Every required dependency of
`pyproject.toml`, its licence as installed in the workspace
venv, where the core reaches it, and its fate under the shape below:

| required dependency | licence | reached from | fate |
|---|---|---|---|
| cadquery 2.7 | Apache-2.0 | `exact.py` (4 calls), `node/adapters/step.py`, `node/adapters/molejo.py` | machinome-node-cadquery; the exact layer rewritten on bare OCP |
| build123d 0.10 | Apache-2.0 | its two adapters; `node/markings.py` imports it lazily to reduce SVG artwork | machinome-node-build123d; markings made conditional |
| cadquery-ocp 7.8 | Apache-2.0 (the CadQuery/OCP repository's LICENSE, checked upstream on 1 October 2026; OCCT itself is LGPL-2.1 with exception) | `exact.py`, `step.py`, `test.py` | machinome-occt |
| ocp-gordon | Apache-2.0 | transitive of build123d | machinome-node-build123d |
| manifold3d | Apache-2.0 | `mesh_engine.py` (already conditional), `node/fusion.py`, `test.py` | the `manifold` extra; `machinome.manifold.engine` behind `machinome.mesh_engine` (change `mesh-engine`, 4 October 2026) |
| molejo[brep] 0.2 | Apache-2.0 | `node/adapters/molejo.py` only | machinome-node-molejo |
| watchdog | Apache-2.0 | `core/builder.py` | a `develop` extra, or replaced |
| solidpython2 | LGPL-2.1-or-later | 13 core modules, see below | stays in core |
| trimesh, numpy, scipy, shapely, rtree | MIT / BSD | core | stay in core |
| fastapi, uvicorn, httpx, asgiref, termcolor | MIT / BSD | core | stay in core |

machinome-mechanics and molejo are Apache-2.0 and pilot-owned.
machinome-viewer is AGPL-3.0-or-later and is reached only as a separate
process, which this note does not touch. The OpenSCAD binary is
GPL-2.0-or-later and the JSCAD CLI is MIT; both run as separate
processes exchanging files and neither is a Python dependency.

the workspace's `docs/foundry-licensing-policy.md` already states the consequence: a
framework runtime profile with no Apache-2.0 code beneath it needs the
leaf plugin architecture and a non-Apache boolean engine before any
grant decision on machinome and molejo could matter. This note is the
plugin architecture part.

### Where the core reaches each kernel

- **solid2 is the core's rendering language, not a leaf.** `node/base.py`
  renders every node to SCAD (`as_scad`, `generate_scad`),
  `scad_expression.py` wraps shared motion values as OpenSCAD constants,
  and `math.py`, `node/operations.py`, `node/internal.py`,
  `node/flexible.py`, `simulation/clocked.py`, `simulation/profile.py`
  and `simulation/program.py` import it. The project template
  `manager/templates/project/root/__init__.py` is a Solid2Node.
  (solid2 is no longer the core's expression type since change
  `expression-type`, 3 October 2026: the symbolic value is
  `machinome.expression_graph.GraphValue`, and a SolidPython value is
  adopted by `machinome.openscad.engine` through the seam
  `machinome.scad_engine`; `scad_expression.py` is removed, and the core's
  remaining solid2 importers are the SCAD presentation, `node/{base,
  operations, internal, flexible}.py`, the two leaves `node/{solid2,
  openscad}.py` and the template. ADR-170, ADR-171.) The SCAD presentation
  is the engine's since change `scad-presentation`, 3-4 October 2026: the
  core composes a description in its own types (`node/presentation.py`)
  and `machinome.openscad.engine.scad_text` writes the text, so
  `node/{base, operations, internal, flexible}.py` import no solid2, and
  the core's remaining solid2 importers are the two leaves `node/{solid2,
  openscad}.py` and the template; the core reaches the binary through the
  seam too, and only `node/solid2.py` still imports `machinome.openscad`
  (ADR-172, ADR-173).
- **The exact layer is one module, `exact.py`,** importing cadquery and
  OCP at module top. Its cadquery use is four spellings: `Shape.cast`
  (four times), `Shape.importBrep`, `Compound.makeCompound`,
  `Vertex.makeVertex`. Every boolean and transform already goes through
  OCP directly, as ADR-047 records. Its importers: `node/exact_leaf.py`,
  `node/fusion.py` (module top), `node/adapters/{build123d,
  build123d_sheet, step, stl, molejo}.py`, `node/declarative.py`,
  `core/loader.py`, `simulation/__init__.py`, `manager/test.py`, and
  `test.py` lazily at the assertion that needs it.
- **`node/__init__.py` already defers every backend class** (PEP 562)
  precisely so that importing the node base does not pull cadquery into
  every `machinome` invocation. Its docstring states that nothing
  dispatches on a registry of subclasses.
- **`mesh_engine.py` is the existing engine seam:** `mesh_engine()`
  resolves the provider `machinome.manifold.engine` once per process and
  checks its contract version, answering None when it or its kernel is
  absent, and `require_mesh_engine` raises one actionable error naming
  `machinome[manifold]`, only when a path needs it (change `mesh-engine`,
  4 October 2026; on 1 October it returned manifold3d's classes).
- **`node/fusion.py` has two recipes.** `exact-fusion-occt-v1` when
  every child is exact, computed with `fuse_shapes` and `placed_shape`
  from the exact layer; otherwise `faceted-fusion-manifold-v1`, which
  unions the children's STL meshes through the mesh engine. Exactness is
  a property of the children (`internal.py`: all children exact).
- **`node/exact_leaf.py` is the de facto extension point** for exact
  leaves, and its docstring still says "a framework-internal base, not a
  declared extension point". machinome-freecad's worktree subclasses it
  and imports the private `machinome.exact._evict`, plus cadquery and OCP
  directly.
- **`node/base.py:1262` chooses a backend by class name:** the spellings
  `Solid2Node`, `OpenScadNode`, `FusionNode`. A magic string of the kind
  `workflow/ongoing/magic-strings.md` inventories. (removed by change
  `backend-switch`, 3 October 2026: the refusal names the node and its
  class; ADR-166)
- **`vet/universe.toml` names the kernels** a pure project may import:
  cadquery, build123d, OCP, solid2, trimesh, numpy, scipy, manifold3d,
  shapely, each with a denylist of file-exchange names. It is the one
  registry that genuinely has to learn about packages.
- **Precedents for a separate package:** the viewer is found through the
  `machinome.viewer` entry-point group (`viewers/bundle.py`);
  machinome-mechanics, machinome-viewer, machinome-freecad and the
  videomaker's Python package spell their imports `machinome_mechanics`,
  `machinome_viewer`, `machinome_freecad`, `machinome_movie`. The core
  is a regular package with an `__init__.py`. The 1 October reading
  that this keeps a dotted name under `machinome.` away from other
  distributions was wrong; see "Facts established on 2 October 2026".
- **ADRs:** ADR-004 (multi-CAD adapter pattern, OpenSCAD as the universal
  compilation target), ADR-046 (conditional OpenSCAD binary), ADR-047
  (one shared OCCT currency for every exact backend), ADR-102 (native
  materialization precedes optional SCAD presentation).
- **The pin coupling:** cadquery 2.8 moved to cadquery-ocp 7.9 and
  build123d 0.11 to cadquery-ocp-novtk, so requiring both in one package
  already blocks both upgrades (the comment in `pyproject.toml`).

### Usage across projects

A grep for each class name over the 81 project directories under
`projects/`, counting directories, on 1 October 2026:

| leaf | projects |
|---|---|
| CadQueryNode | 78 |
| MolejoNode | 39 |
| StlNode | 25 |
| StepNode | 17 |
| Solid2Node | 16 |
| Build123dNode | 9 |
| StepAssembly | 8 |
| OpenScadNode | 4 |
| Build123dSheetNode | 3 |
| FreeCADAssemblyNode | 1 |
| JScadNode | 0 |

The counts were read on 1 October as the size of an import-line
migration. Under the one-path rule every root import changes anyway in
the cycle the 0.8 roadmap orders first, and the counts now size the
rows of that cycle's rewrite script and the one-time artifact rebuild
described under "Import paths".

### Facts established on 2 October 2026: import paths

Verified with two throwaway distributions built by the workspace venv's
setuptools 84.0.0 under Python 3.12.3, against a stand-in core:
`machinome-fakesat`, shipping only `machinome/fakesat/` and no
`machinome/__init__.py`, and `machinome-node-fakesat`, shipping only
`machinome/node/fakesat.py`. Nothing in the workspace was installed or
changed.

- **Several distributions can share the `machinome` directory while the
  core stays a regular package.** A satellite that ships
  `machinome/<kernel>/` and no `machinome/__init__.py` installs beside
  the core's files, and pip's per-distribution RECORD keeps uninstalls
  clean. This is the Python Packaging User Guide's native namespace
  portion, with the core's regular `__init__.py` in the parent's place.
- **The guide's warning against mixing pkgutil-style and native
  portions** concerns the shared `__init__.py` vanishing when one
  distribution is uninstalled. Here only the core carries it and every
  satellite requires the core, so that failure cannot occur. The pure
  alternative, dropping the core's `__init__.py`, would cost
  `machinome.__version__`, which the vet universe test pins, for no
  gain.
- **A satellite can ship a module one level down, into
  `machinome/node/`.** The second experiment, `machinome-node-fakesat`
  with `py-modules = ["machinome.node.fakesat"]`, built a wheel holding
  only `machinome/node/fakesat.py` and an editable install whose finder
  maps `machinome.node` to the satellite's directory. The class defined
  there subclasses the core's node base as a local module would. The
  matrix below holds for it with `extend_path` in
  `machinome/node/__init__.py` as well as in `machinome/__init__.py`.
- **A satellite cannot add a name to a module it does not own,** so a
  root re-export such as `machinome.node.CadQueryNode` could only come
  from a table in the core. The one-path rule makes the question moot:
  the root exports nothing, and the one path is a plain submodule
  import, `from machinome.node.cadquery import CadQueryNode`, which a
  type checker follows; the root spelling never was static. An absent
  satellite fails with Python's own `ModuleNotFoundError` naming the
  module.
- **Neither a table nor a registry is paid for.** The morning's table
  and the entry-point registry weighed against it, whose scan over this
  venv's 213 distributions was measured at about 34 ms, both served a
  root re-export the rule forbids.
- **Module paths are recorded in artifacts.** The native recipe identity
  (`node/base.py:1629`) and the flexible-node digest
  (`node/flexible.py:386`) include the class's module, and the
  simulation program and clocked runner print it. A class that moves
  from `machinome.node.adapters.cadquery` to `machinome.node.cadquery`
  changes those strings once.

Which install combinations find the portion:

| install combination | result |
|---|---|
| core editable, satellite editable | works with no core change; the setuptools editable finder maps the dotted name `machinome.fakesat` itself |
| both from wheels into one site-packages | works with no code at all |
| core editable, satellite from a wheel | works only when the core's `__init__.py` extends `__path__` with `pkgutil.extend_path` |
| satellite absent | Python's own `ModuleNotFoundError` naming the module |

The one `extend_path` line therefore covers every combination. A
regular package always wins over portions found earlier on `sys.path`,
so order does not matter -- for which `__init__.py` runs, not for which
submodules resolve: the plain line appends every directory of the
package's name on `sys.path`, a second copy of the core included, and in
a development workspace the editable primary checkout sits on `sys.path`
behind every bench, so a module the bench lacks resolved to the primary's
file (probed in the `lean-install` cycle, 3 October 2026: `import
machinome.exact`, deleted by `exact-engine`, resolved to the primary's
`machinome/exact.py`). The line as built therefore admits only portions
that ship no `__init__.py` of their own, which a satellite never does
(the check-dist collision guard), so every combination above still works
and no second copy of the core is ever merged.

## The shape

Split by what the core would otherwise have to carry, a Python kernel
with its own licence and install cost, not by leaf type. The two axes
coincide, and the result is three new packages.

### machinome, the core

The node base and the four declared leaf bases, `LeafNode`,
`ExactLeafNode`, `SheetLeafNode` and `FlexibleNode`, at leaf contract
version 1 (`machinome.node.leaf.CONTRACT`; leaf-contract cycle, 3 October
2026); AssemblyNode and FusionNode; the tree, frames and mates, motion,
simulation, the CLI,
the document format, vet, the test harness, the markings declarations;
and the four leaf types whose Python side carries no kernel, at
`machinome.node.openscad`, `.solid2`, `.jscad` and `.stl`.

Two engine seams, both resolved on first use and both allowed to be
absent:

- the existing mesh engine seam, manifold3d behind it as today, optional;
- a new exact engine seam of the same shape, `exact_engine()` returning
  the engine or None and `require_exact_engine(needed_by, reason)`
  raising the install remedy, filled by machinome-occt when it is
  installed.

The exactness protocol stays in core: the node base already carries an
`exact` property defaulting to False and a `shape()` that refuses.
FusionNode keeps every model fact it holds today: the declaration, the
recipe identity, artifact naming and currency, time, validation, child
placement, and the rule that a fusion is exact when its children are. Its
two booleans become calls on whichever engine answers. The exact path is
unreachable without an exact child, which only the OCCT package can
create, so a core without machinome-occt never imports OCP and never
asks for it. The faceted path is the OpenSCAD plus JSCAD case and works
in core as it stands.

### machinome-occt, LGPL-2.1

The engine and nothing else: the exact layer rewritten on bare OCP,
dropping the four cadquery spellings, as `machinome.occt`; the OCCT
currency, the booleans and transforms, and reading BREP and STEP files
into that currency; the exact engine the core's seam resolves; the OCP
paths of the test kernel that `test.py` already imports lazily. It
depends on cadquery-ocp only and carries no node type (pilot, 2 October
2026). Its licence is LGPL-2.1, matching OCCT, the provider it wraps
(pilot, 2 October 2026: the policy is to match the provider's licence;
OCCT's is LGPL-2.1 with the Open CASCADE exception, and cadquery-ocp's
Apache-2.0 covers only the binding). The exact-leaf contract it serves, `ExactLeafNode`, stays in the
core at `machinome.node.exact_leaf`, resolving the engine lazily.

It also carries the exact operations a project calls directly, the ones
that used to be `machinome.exact`: `intersect_shapes`, `fuse_shapes`,
`placed_shape`, `solid_count` and `solid_volume`, at
`machinome.occt.engine`, the one module that is both the provider the
core's seam resolves and their address (change `exact-engine`, 3 October
2026). They are operations, not node types, so the rule that the package
carries no node type stands.

Why an engine package distinct from the node packages: three node types
need the engine and no CadQuery (build123d, STEP, FreeCAD), ADR-047
already named the OCCT shape as the currency, and the pin coupling shows
the forced co-install already costs upgrades. With separate packages a
project using one front end escapes the intersection constraint; a
project using both still resolves one OCP.

### The node packages, Apache-2.0 and LGPL-2.1-or-later

One package per node type, each its own repository (pilot, 2 October
2026), named and imported under "Import paths":

- **machinome-node-cadquery:** `machinome.node.cadquery`, `CadQueryNode`
  with its namespace and the CQ-editor metaclass. About thirty lines,
  plus tests and a manual. Depends on cadquery.
- **machinome-node-build123d:** `machinome.node.build123d`,
  `Build123dNode`, `Build123dSheetNode` and the markings SVG reducer.
  Depends on build123d.
- **machinome-node-step:** `machinome.node.step`, `StepNode`,
  `StepAssembly` and the `import-step` command. Depends on
  machinome-occt.
- **machinome-node-molejo:** `machinome.node.molejo`, `MolejoNode`.
  Depends on machinome-occt and molejo[brep]. Its own repository under
  the machinome organisation, not a package inside molejo's: the
  dependency runs from the node package to the library, molejo's
  repository stays independent of machinome as documented, the two
  release on different clocks, and the viewer already keeps molejo's
  three.js evaluation on the machinome side.
- **machinome-freecad:** unchanged in purpose and outside this
  refactor; when it is retargeted it becomes machinome-node-freecad at
  `machinome.node.freecad`, depends on machinome-occt, and stops
  importing cadquery and the private eviction helper.

Extras on the core, one per package, named by the address's last
component: `machinome[cadquery]`, `[build123d]`, `[step]`, `[molejo]`,
`[occt]`, `[freecad]`, `[all]`.

The licence of a node package matches its node technology (pilot,
2 October 2026). Checked in the workspace venv's metadata the same day:
cadquery, build123d, ocp-gordon and molejo declare Apache-2.0;
cadquery-ocp declares nothing in its metadata and its upstream LICENSE
is Apache-2.0, OCCT beneath it being LGPL-2.1 with exception, which
places no condition on code that uses it. The four node packages are
therefore Apache-2.0, copyright Luis Henrique Cassis Fagundes, with the
core's NOTICE pattern; machinome-occt is LGPL-2.1, matching OCCT
rather than the binding, by the pilot's ruling of the same day that a
package matches its provider's licence. A node package over the engine
keeps its own provider's licence, so machinome-node-step and
machinome-node-molejo stay Apache-2.0 over an LGPL engine, as any
program may be over an LGPL library. FreeCAD is the other LGPL
technology and machinome-freecad already matches it; OpenSCAD is
GPL-2.0-or-later and is reached as a process, never a dependency.

### Import paths

Locked by the pilot on 2 October 2026, after the table shape of the
morning was found to contradict the one-path rule the 0.8 roadmap
records the pilot ordering on 27 September: "exactly one import path
for each name", the module that defines it, with the package roots
re-exporting nothing. That rule stands. The norm is the one the
namespaced Python ecosystems converged on, OpenTelemetry, Airflow
providers, Google Cloud and Azure alike: the import address is the
architectural location, and the distribution name is the address with
dashes.

**The three rules.**

1. *Address.* A node type lives at `machinome.node.<nodetype>`, whether
   the core or a satellite ships it. Anything a satellite brings that is
   not a node type lives at `machinome.<name>`.
2. *Install.* The extra is the last component of the address:
   `machinome[cadquery]` for `machinome.node.cadquery`,
   `machinome[occt]` for `machinome.occt`. No lookup.
3. *Distribution.* The address with dashes: `machinome-node-cadquery`,
   `machinome-occt`, `machinome-mechanics`. One package per node type;
   a project author never types the distribution name.

A node type is a package when it brings a Python dependency the core
would otherwise carry. The core's own leaf types, `machinome.node.solid2`,
`.openscad`, `.jscad` and `.stl`, stay in the core at the same kind of
address; the `adapters` level dissolves, since every leaf type is one
module under `machinome.node` beside `assembly`, `fusion`, `flexible` and
`sheet_leaf`. Nothing needs moving to keep that namespace clean: the
modules under `machinome.node` that are not node types, `base`, `frames`,
`markings`, `declarative`, `decorators`, `internal`, `operations`,
`sources`, collide with nothing.

| what | address | install | distribution |
|---|---|---|---|
| `CadQueryNode` | `machinome.node.cadquery` | `machinome[cadquery]` | machinome-node-cadquery |
| `Build123dNode`, `Build123dSheetNode`, the SVG reducer | `machinome.node.build123d` | `machinome[build123d]` | machinome-node-build123d |
| `StepNode`, `StepAssembly`, `import-step` | `machinome.node.step` | `machinome[step]` | machinome-node-step |
| `MolejoNode` | `machinome.node.molejo` | `machinome[molejo]` | machinome-node-molejo |
| the exact engine: OCCT currency, booleans, file reading | `machinome.occt` | `machinome[occt]` | machinome-occt |
| the exact operations a project calls, formerly `machinome.exact`: `intersect_shapes`, `fuse_shapes`, `placed_shape`, `solid_count`, `solid_volume` | `machinome.occt.engine` | `machinome[occt]` | machinome-occt |
| the mesh engine | `machinome.manifold.engine` | `machinome[manifold]` | machinome-manifold |
| the OpenSCAD engine: `machinome.openscad.engine`, the provider of the seam `machinome.scad_engine` (contract 2: adopting SolidPython's values as expressions, writing the SCAD text of the core's presentation description, locating the binary); `machinome.openscad.binary`, the OpenSCAD binary contract (`require_openscad`, `openscad_binary`, `OpenScadUnavailable`) | `machinome.openscad` | `machinome[openscad]` (declared by cycle 7) | machinome-openscad |
| `ExactLeafNode`, the declared exact-leaf base, beside the other three declared leaf bases `LeafNode`, `SheetLeafNode` and `FlexibleNode` | `machinome.node.exact_leaf`; `machinome.node.leaf`, `.sheet_leaf`, `.flexible` | core | machinome |
| mechanics, movie, later and under their own processes | `machinome.mechanics`, `machinome.movie` | `machinome[mechanics]`, `[movie]` | machinome-mechanics, machinome-movie |

`Build123dSheetNode` lives in `machinome.node.build123d`, beside
`Build123dNode` (decided in the `lean-install` cycle, design.md
Decision 1): "node type" in rule 1 names the technology, not the class,
as `StepNode` and `StepAssembly` share `machinome.node.step`. The sheet
node has the kernel, pin and licence of `Build123dNode`, and a module
`machinome.node.build123d_sheet` would need an extra installing exactly
what `build123d` installs, or break rule 2.

The viewer keeps `machinome_viewer`: it is reached as a separate process,
nothing imports it, and its entry-point group is already called
`machinome.viewer`. The studio is not a library and keeps its name.

**The core.** Three edits, none of them a table of satellites.

- `machinome/__init__.py` and `machinome/node/__init__.py` each gain the
  line `__path__ = __import__('pkgutil').extend_path(__path__, __name__)`,
  so a satellite's `machinome/<name>/` directory or
  `machinome/node/<nodetype>.py` module joins the package in every
  install combination.
- The node root stops answering the names that leave. `CadQueryNode`,
  `Build123dNode`, `Build123dSheetNode`, `StepNode` and `MolejoNode`
  leave its export table and enter its moved-names table, refused with
  an ImportError naming the new module and the extra, the mechanism the
  root already uses for the ports. The core's own leaf types move from
  `machinome.node.adapters.<x>` to `machinome.node.<x>`. The remaining
  root re-exports are struck by the one-path cycle the roadmap orders
  first, which takes the paths as they then stand.
- `pyproject.toml` declares the extras, one per package, and drops
  cadquery, build123d, cadquery-ocp and molejo from the required
  dependencies.

**The seams** are the only places the core names a satellite's module,
each a try-import of a known provider refusing with the extra's name
(D2): FusionNode's exact engine and `ExactLeafNode` resolve
`machinome.occt`; the `Svg` marking resolves its reducer from
`machinome.node.build123d`; the CLI's command table maps `import-step`
to `machinome.node.step`. Each provider declares the contract version it
implements and the seam checks it at resolve time, refusing with a
message naming both versions, as the package standard's section 1.2
requires. The vet universe stays one core file. No entry-point group is
introduced; the viewer's stays.

**A satellite,** taking machinome-node-cadquery as the model.

- Layout: `machinome/node/cadquery.py`, never a `machinome/__init__.py`
  or a `machinome/node/__init__.py`. A node package is one module, so
  the one path is the module that defines the class:
  `from machinome.node.cadquery import CadQueryNode`. An engine package
  is a subpackage, `machinome/occt/`, whose `__init__.py` defines
  nothing, per the ratified sentence of the ports spec.
- `pyproject.toml`: depends on `machinome~=0.8.0` and on its kernel;
  `py-modules = ["machinome.node.cadquery"]` for a node package,
  `include = ["machinome.occt*"]` for an engine package; setuptools
  handles both without an `__init__.py` in the parent.
- Tests prove the one path, that the class subclasses the core's leaf
  contract, and the dependency pin on the kernel's version.
- `check-dist` lists the wheel and refuses one that contains
  `machinome/__init__.py` or `machinome/node/__init__.py`, since pip will
  not catch that collision; then installs the wheel beside the core in a
  throwaway environment and imports the one path there.

**What follows.**

- The root spelling of the five moved names is refused as soon as they
  leave, so every project that uses it breaks against the campaign
  branch until the one-path cycle's rewrite script runs over the 74
  repositories with every row, the moved names included. One migration,
  not two; the refactor itself validates in named originating projects
  migrated by hand on branches.
- When an extra is missing, the error is Python's own "No module named
  'machinome.node.step'". Rule 2 tells the reader the install line, and
  the manual states the rule once. No import hook improves the message:
  Flask tried that with `flask.ext` and removed it.
- A one-time artifact rebuild, because the moved classes' module paths
  enter the recipe identities (see the facts above).
- A kernel the core does not declare takes the same addresses and ships
  the same way; its only difference is that no extra on the core names
  it.

### Not split, and why (superseded 4 October 2026: see "Every node type is a package")

- **No machinome-node-openscad, -solid2, -jscad or -stl.** A node type
  is a package when it brings a Python dependency the core would
  otherwise carry. These four bring none: solid2 is the core's rendering
  language (see the module list above), the OpenSCAD binary is already
  conditional under ADR-046 and runs as a separate process, JSCAD wraps
  an MIT tool in a subprocess, and StlNode's only kernel is trimesh,
  which the core needs anyway. They take the address of the norm,
  `machinome.node.<nodetype>`, inside the core. If ADR-102's direction
  ever makes the SCAD presentation optional, openscad and solid2 leave
  as one package, never two: solid2 is a Python writer for OpenSCAD and
  both evaluate through the same binary.
- **No node type inside machinome-occt.** The engine package carries
  the currency and the operations on it; STEP and molejo, which
  evaluate through it, are node packages over it (pilot, 2 October
  2026; the 1 October shape had both riding in the engine).

## The campaign line is `v0.8-split` (pilot, 4 October 2026)

The framework branch carrying the campaign was `v0.8` from its opening
on 2 October 2026 until 4 October, when the pilot renamed it
`v0.8-split`: the release of the 0.8 line is tagged `v0.8.0`, and a
branch named like the tag confused the two. The bench at
`machinome/WTs/v0.8-split` (slot 1) is the same worktree, moved; the six
integrated cycle branches keep their `v0.8-<change>` names as history. A
new cycle bench is `scripts/dev-env v0.8-split-<change> setup --base
v0.8-split`. The pilot's parallel branch `v0.8-production` is cut from
this line (its bench, slot 6) and is not part of the campaign.

## State of the campaign (4 October 2026, handoff)

Written at the end of the session that ran cycles 4 to 7 (4 October
2026, updated at its close), for the next agent. Nothing below is pushed or uploaded; framework `main` holds 0.7.1
tagged and unpublished, and the line `v0.8-split` merges into it only at
the campaign's close.

**Done, layer 1, cycles 1 to 7,** each archived under
`openspec/changes/archive/` with its evidence, sweep JSON and moved-names
table, each integrated into the line by fast-forward after the
orchestrator's own suite run: `exact-engine` (ADR-160 to 165),
`leaf-contract`, `backend-switch` (ADR-166), `lean-install` (ADR-167 to
169), `expression-type` (ADR-170, 171), `scad-presentation` (ADR-172,
173), and `mesh-engine` (ADR-176), taken up by the pilot on 4 October:
manifold3d behind the mesh seam as the `manifold` extra, joined to the
line by the merge d4eb5c0 because the line had moved under the pilot's
warts commit a66aee5 (a merge, never a rewrite, is the rule when the line
moves). The pilot's own production-layer cycle joined the line by merge
(69c7019) before it. The suite at the line's head d4eb5c0: 4482 passed,
4 skipped. The workspace holds `scripts/load-projects` and the seven
tables under `scripts/load-projects.d/`; the universe sweep reads 117 ok, 4 expected
(the root cleanup's customers), 2 unexpected and pre-existing
(wall_clock_41's own CadQuery error, Dum-E without machinome-freecad), 6
no-model. The validation branches `lean-core-validation` stay in
OpenAstroMount, machinome-freecad, splitflap, the Internal-Cycloidal-
Actuator and Pin_tumbler_lock, never merged, as fixtures for the rewrite.
machinome-mechanics' branch `v0.8` (symbolic assertions, 201 passed) is
not merged into its main.

**No package is split.** The extras today (`occt`, `manifold` since the
seventh cycle, `cadquery`, `build123d`, `step`, `molejo`, `all`) only pull
the third-party kernels; every machinome module still ships in the one
distribution, refusing by its extra's name when its kernel is absent. That
is layer 1's design; layer 2, the split, has not started for any package
and starts only on the pilot's word, for the architecture and the lean
install.

**Left in layer 1:**

- Next, the eighth cycle: the STL runner into `machinome/openscad/`, `Solid2Node` and
  `OpenScadNode` as the node modules `machinome.node.solid2` and
  `machinome.node.openscad` over it, SolidPython as the `openscad` extra
  refused at the three doors. Loose ends it absorbs: `Solid2Node.as_number`
  reaching the engine's package directly; the web snapshot renderer and
  `Sim(meshes=True)` calling `assemble()` only for a flexible leaf's
  per-pose snapshot STL, whose owner is undecided; ADR-173's removal
  candidates, ADR-086's assembly-phase coalescing and
  `LeafNode._render_can_be_skipped`.
- The ninth: `machinome new` scaffolding whatever leaf kind the installed
  extras provide, the template being the last SolidPython importer.
- The root cleanup (roadmap of 27 September): both roots stop
  re-exporting, the rewrite script runs once over the 74 project
  repositories with the moved-names tables as rows. Its first customers:
  Voron-2 (`shape()` is the engine's currency, 29 project files call
  CadQuery methods on it), the Actuator, YouCanBuildDog and the Don1
  (`machinome.node.adapters` dissolved).

**Struck or deferred by the pilot:** watchdog remains a required
Apache-2.0 dependency, and as a `develop` extra is D6; manifold3d left the
required list on 4 October 2026 for the `manifold` extra, by the seventh
cycle (`mesh-engine`), the pilot's decision of that day; the test suite
organised by future package; a non-Apache faceted fusion engine, struck
until a project names itself.

**Follow-ups the campaign owes outside the framework:** the workspace's
`scripts/setup` tier 2 installs the framework editable without `[all]`,
and `docs/collaborator-setup.md` matches; the workspace contract still
says `machinome develop` opens OpenSCAD without the viewer (gone since
ADR-103); the studio's `machinome-api` skill still teaches
`machinome.node.adapters.step`, a `--openscad` develop flag,
`import-step` without its `step` extra and the OpenSCAD GUI fallback, and
neither it nor the machining skill teaches the extras or the one path;
the push script for package repositories (in scope, nothing to push to
before layer 2); machinome-mechanics' pin `machinome>=0.7.0` and its
twelve test files on solid2's `get_animation_time`, at the release pass;
machinome-viewer's stray root `openscad.py` importing a moved name; the
venv's editable `machinome` dist-info still reading 0.7.0;
machinome-freecad's retarget to `machinome.node.freecad` and the assembly
extension contract its carriers evidence; D10's conformance gaps of the
framework against the package standard, not checked.

**Warts filed by the cycles, untriaged** (`workflow/warts.md`, 3 October
2026): OpenAstroMount's scenario test refused by the exact common guard on
its master; a first build's sweep removing fused children's STLs; a
self-materializing leaf that publishes nothing falling through to the
OpenSCAD path (`JScadNode`); a `machinome build` hanging three hours in a
fresh project worktree on virtiofs; OpenSCAD's STL output not
reproducible run to run (hash SCAD, never STL). Cycle 6 filed none: the
self-import overwrite it found is fixed by it (ADR-173). Cycle 7
reproduced the fresh-worktree hang and recorded its mechanism under that
entry: a build in a project whose sources were written moments earlier
restarts every second, each generation ending `SOURCE_CHANGED`, without
end; sources dated an hour back build once; still untriaged.

**Orchestration as practised** (D12): one proposer and one applier per
cycle, fresh Opus agents with a written briefing, the orchestrator's
adversarial review as the ratification gate, the orchestrator running
the validation legs and the sweep itself and handing the reports to the
paused applier, one suite at a time, no commit amended (pilot, 4 October
2026: commit the state and add commits), fast-forward into the line.

**The licence, for the next agent.** The grant stays Apache-2.0 by the
pilot's spoken decision of 4 October 2026 ("Settled by the pilot, 4 October
2026, later the same day"), and nothing in the framework's licence files,
NOTICE or classifiers moved. The same day the pilot committed in the
workspace (483a0f3, `workflow/`) a proposal of AGPL-3.0-or-later with an
open-simulation permission: the pilot's own deliberation for the dedicated
licensing session, not a decision this plan acts on. Layer 2 waits on that
session's outcome only for what it says about the split's worth; layer 1
does not.

**Update at the eighth cycle's integration (4 October 2026, later
session).** `openscad-out` is done and integrated: cycle commits f76aa20
(plan) and f51b4de (implementation, archive `2026-10-04-openscad-out`,
ADR-177, 178, 179; the specs `openscad-engine` and `scad-engine-dependency`
removed, 45 remain), merged into the line as 04809f7 (a merge, not a
fast-forward: the line had taken the viewer-seam plan commit meanwhile).
Suite at f51b4de: 4513 passed, 4 skipped, twice; at the merge head the
same, after one environment failure worth knowing about: a bench that
takes a commit deleting a package directory keeps that directory alive
through its ignored `__pycache__`, and Python then imports the deleted
package as an empty namespace package, so the test that the former
addresses are gone fails until `git clean -fdX <directory>` removes the
leftover. Every checkout that pulls this cycle (the primary `machinome/`
when the line merges into main, every bench cut before it) needs that
cleaning once; the same will hold for `brep-mesh` (the `occt/` and
`manifold/` directories) and `viewer-seam` (`viewers/`). Validation legs
all identical to their baselines (the lock's 15 and Prusa's 55 `.scad`
hashes, 2573 and 15935 verdicts, the snapshot's root SCAD and pixels, the
three goldens, OpenAstroMount built and tested with SolidPython and both
OpenSCAD packages unfindable, `machinome new` under three installs); the
universe sweep unchanged (117 ok, 4 expected, 2 unexpected pre-existing, 6
no-model). The workspace holds the eighth table,
`scripts/load-projects.d/openscad-out.toml` (main b1c1bf5). The bench is
torn down, the branch kept.

What this leaves of the list above: the ninth cycle's template work was
absorbed by `openscad-out` (the template scaffolds the installed leaf
kind); `jscad` and `stl` as packages go with the root cleanup. **Next:
`brep-mesh`**, then `root-cleanup`, then `viewer-seam`, as "The next
phase" and "The last cycle of the phase" below record.

## Every node type is a package (pilot, 4 October 2026, at the session's close)

The pilot's ruling, after the seventh cycle, superseding "Not split, and
why" below and the one-package OpenSCAD shape of "Layers":

- **Every node type is its own package contributing to the `machinome.node`
  namespace**, symmetric: `machinome.node.<x>` / `machinome[<x>]` /
  `machinome-node-<x>` for all eight, `cadquery`, `build123d`, `step`,
  `molejo`, `openscad`, `solid2`, `jscad` and `stl`. The rule "a node type
  is a package when it brings a Python dependency the core would otherwise
  carry" is dropped. The reason is not weight but declaration: a project's
  dependencies must say at once what mix it makes. cadquery beside openscad
  says precision is lost somewhere; step or stl says a source is missing
  and a binary is handled.
- **`Solid2Node` and `OpenScadNode` are two packages.** solid2 is a node
  type that depends on openscad; an OpenSCAD project that does not use
  SolidPython authoring does not carry `Solid2Node`. `machinome[solid2]`
  includes `machinome[openscad]`, as `[cadquery]` includes `[occt]`.
- **`machinome.openscad` is not an engine.** Tested the same day: it
  decides no spatial question (every comparison of an OpenSCAD part is
  faceted and the mesh engine decides it; with manifold3d absent such a
  project cannot test), so it fails the criterion `occt` and `manifold`
  meet. It is the OpenSCAD node family's backend: the SCAD writer
  (SolidPython), the binary runner, and the OpenSCAD snapshot renderer
  (OpenSCAD-specific, in the core only by history). It belongs in the
  `openscad` node package, and the seam `machinome.scad_engine` is to be
  renamed for what it is, a SCAD-text writer the core calls for
  `scad_code`, `generate_scad()` and the snapshot renderer, or dissolved
  if those move with the package; the eighth cycle's proposer settles
  that with the evidence and the pilot ratifies.
- **No SCAD in the core.** `scad_code` and `generate_scad()` move with
  the `openscad` node package, with `scad_file`, `scad_authored`, `as_scad`
  and the OpenSCAD snapshot renderer; the core mentions SCAD nowhere but in
  a table of supported node types, if one exists. At the ruling the core
  says "scad" in fifteen modules (counts of 4 October 2026: `node/base.py`
  80, `viewers/openscad.py` 47, `scad_engine.py` 32, `manager/snapshot.py`
  25, `source_generation.py` 23, `node/leaf.py` 22, `core/builder.py` 21,
  `math.py` 16, `node/flexible.py` 12, `expression_graph.py` 11,
  `node/presentation.py` 10, `node/internal.py` 9, `core/expressions.py`
  7; `node/jscad.py` is JSCAD's own name). The eighth cycle is therefore
  "OpenSCAD out of the core" complete, not the runner alone.
- **Engines are named as engines.** The `node-` infix stands; the engine
  packages are `machinome-engine-<name>`, not named after their libraries
  alone (the pilot, 4 October 2026). Which `<name>` (the technology, `occt`
  and `manifold`, as the providers' addresses are today, or the role,
  `exact` and `mesh`, as the seams are) is the pilot's next decision; the
  code today names seams by role (`machinome.exact_engine`,
  `machinome.mesh_engine`; "the exact engine", "the mesh engine" in every
  message; the paths `'exact'` and `'faceted'` in the test framework and
  the verdict keys) and providers by technology (`machinome.occt.engine`,
  `machinome.manifold.engine`; the recipe identities `exact-fusion-occt-v1`
  and `faceted-fusion-manifold-v1`).
- **Still midway.** The addresses of the eight node types already obey the
  norm; what is not yet in shape is the packaging of the OpenSCAD family
  (the eighth cycle), the four node types the earlier rule kept in the
  core, and the names, which the pilot fine-tunes before more packages
  come in. The licence will be one for the whole suite (the pilot's
  decision of 4 October, recorded in the workspace, not in scope here);
  the split is kept, in a monorepo.

## Locked at the session's close (pilot, 4 October 2026)

**The version's goal.** 0.8 solves the long-deferred architectural debts
of the whole suite, the licence included (one licence for every package,
GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, called MGPL in the pilot's
notes; the packages kept split inside a monorepo). The licence and the
monorepo are decided by the pilot and are not this plan's scope; the
architecture below is.

**The engines are `brep` and `mesh`.** Locked by the pilot after the
domain modelling of 4 October: the two engines are named for the
representation each consumes, a boundary representation of parametric
surfaces and a polyhedral triangle mesh, not for a claim ("exact") or a
quality ("faceted"). Packages `machinome-engine-brep` and
`machinome-engine-mesh`; providers `machinome.engine.brep` and
`machinome.engine.mesh` (the provider module carries the role, so one
engine per role is installed at a time; a second mesh engine is another
package providing the same module). The same two words replace `exact`,
`faceted` and `mesh` everywhere the code uses them for this split: the
seams, the leaf base (`ExactLeafNode` becomes the B-rep leaf base), the
`exact-geometry` capability and its spec names, the verdict paths `'exact'`
and `'faceted'`, `machinome test --faceted`, the fusion recipe identities,
the refusals' words. Artifact extensions stay (`.brep`, `.stl`). This is
its own cycle, with the rewrite script over the universe (every
`ExactLeafNode` subclass), placed with the root cleanup, where every
project is rewritten once.

**A proper OpenSCAD removal cycle.** The pilot's finding: cycles 5 and 6
were described as taking OpenSCAD out of the core, and the core still says
"scad" in fifteen modules (the counts above). What those cycles did was
put the SCAD *writing* behind a seam; the core still presents, names,
sweeps, snapshots and coalesces SCAD. The removal is one cycle,
`openscad-out`, gated by one acceptance test written red first: an AST and
token scan finding no `scad` (any case) in any core module outside the
`openscad` and `solid2` node packages and outside one table of supported
node types, `node/jscad.py`'s own name excepted. Its scope is the whole of
what the eighth and ninth cycles were going to do and what they left out:

- the OpenSCAD node package founded (`machinome.node.openscad`): the SCAD
  writer (SolidPython), the binary runner (`generate_stl`'s OpenSCAD
  launch), `scad_code`, `generate_scad()`, `scad_file`, `scad_authored`,
  `as_scad`, the OpenSCAD snapshot renderer (`viewers/openscad.py`) and
  its command line in `manager/snapshot.py`, with the `openscad` extra;
  `Solid2Node` as `machinome.node.solid2` over it, `as_number` and the
  adoption of SolidPython values with it, with the `solid2` extra;
- the seam `machinome.scad_engine` dissolved: what the core needs of the
  family is expressed in the leaf and presentation contracts without
  naming SCAD (a leaf declares the artifacts it keeps and renders; a
  presentation is a description the installed node packages may write);
- the builder's sweep rule for `.scad` made generic: an artifact kept by
  reference because a node declares it, not by suffix;
- ADR-086's assembly-phase coalescing removed with its production producer
  (`source_generation.py`);
- the presentation description (`node/presentation.py`, `internal.py`,
  `flexible.py`, `leaf.py`) worded for what it is, a presentation, with
  the per-binding snapshot STL's owner decided;
- the expression modules (`math.py`, `expression_graph.py`,
  `core/expressions.py`) documented as machinome's expression language,
  which the viewer reads, whatever syntax it inherited;
- the project template scaffolding whatever leaf kind the installed
  extras provide;
- `jscad` and `stl` as node packages with their extras, for symmetry, in
  the same cycle or the next.

Then the root cleanup, then the `brep`/`mesh` rename, then the names of
the packages confirmed before more packages enter the monorepo.

## Layers (pilot, 3 October 2026)

The campaign is built in layers, and the repository question is not
decided. Layer 1 is the internal architecture for the whole split,
OpenSCAD included, inside one repository and one distribution. Layer 2 is
the package split, for licensing: the requirement behind it is that a
GPL-2.0-only project, which is an OpenSCAD project, imports machinome
with no Apache-2.0 code beneath it; that turns on the core's own grant
and its required dependencies, decisions the pilot has not taken.
Whether distributions become repositories is decided later, on evidence
a published package produces; the package standard's "its own
repository" is read as "its own distribution" until then. Layer 2 starts
only when layer 1 is complete. The three archived cycles (`exact-engine`,
`leaf-contract`, `backend-switch`) are layer 1's first three; its five
remaining cycles:

4. `lean-install`: every leaf's address final, `machinome.node.<x>` with
   the `adapters` level dissolved; the two path-extension lines; the
   command table resolving `import-step` by a try-import naming the
   extra; the markings reducer behind a seam; the vet universe
   following; and the four kernel dependencies, cadquery, build123d,
   cadquery-ocp and molejo, as extras with their modules still in the
   core, each module refusing by its extra when its kernel is absent.
   The lean install, before any package exists. **Done** 3 October 2026
   (ADR-167, ADR-168, ADR-169);
   `openspec/changes/archive/2026-10-03-lean-install/evidence.md`.
5. to 8. OpenSCAD out of the core, four cycles: the core's own
   expression type in place of solid2's `OpenSCADConstant` facade
   (`expression-type`, the fifth: `GraphValue` at
   `machinome.expression_graph`, the engine package `machinome.openscad`
   with the seam `machinome.scad_engine`; **Done** 3 October 2026,
   ADR-170, ADR-171;
   `openspec/changes/archive/2026-10-03-expression-type/evidence.md`); the
   SCAD presentation behind a seam, `assemble()` no longer requiring it,
   the `develop` fallback included (`scad-presentation`, the sixth: the
   core describes its presentation in `machinome.node.presentation` and
   the engine writes the text, contract 2; **Done** 4 October 2026, ADR-172,
   ADR-173; `openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.
   The `develop` fallback it names had been removed by ADR-103 on 11
   September 2026, before the campaign: nothing of `develop` moved but its
   builder's `scad_output`. The pilot decided design.md Decision 3 on 3
   October 2026: option A, a `.scad` written only where a path reads it, a
   SCAD-authored leaf's for its STL and the root's on demand for the
   OpenSCAD snapshot renderer, which removes it once drawn (the
   orchestrator's correction of 4 October, with the rule that a `.scad` no
   current node writes never survives a successful build); option B, every
   build's `.scad` kept when the engine is installed, rejected because
   those deliverables served a reader machinome does not have); the binary runner as an engine
   subpackage with `Solid2Node` and `OpenScadNode` as two node modules
   over it; the project template scaffolding whatever leaf kind the
   installed extras provide.

Dropped and deferred the same day: a non-Apache faceted fusion engine
(no GPL-2.0-only project uses `FusionNode`; their fusions happen inside
OpenSCAD); watchdog optional, and the test suite organised by future
package, both deferred as not architecture. The root cleanup ordered on
27 September follows layer 1 and precedes layer 2, after cycle 4 fixes
the addresses. "What it takes" below is the 2 October scope; its items
4 to 6 and the five repositories are layer 2 material now, kept as
written.

## What it takes: the scope of the first refactor (2 October 2026; see "Layers")

Proposed 2 October 2026 under the locked import-path norm; the pilot
accepts or trims it. Each framework item is a candidate cycle under
the workspace's `skills/framework-change/SKILL.md`; each new repository is cut under
the workspace's `docs/software-package-standard.md` and its manual under
the workspace's `skills/write-the-manual/SKILL.md`.

**In the framework, on the campaign branch:**

1. **Declare the leaf extension contract.** `LeafNode` for faceted
   leaves, `ExactLeafNode` for exact ones, and `SheetLeafNode` and
   `FlexibleNode` for sheet and flexible ones become declared extension
   points (four bases, not two: settled by the pilot on 3 October 2026,
   since `Build123dSheetNode` and `MolejoNode` leave at the cut),
   `ExactLeafNode` staying in the core and resolving the exact engine
   lazily; the contract is versioned, `machinome.node.leaf.CONTRACT = 1`,
   checked against a class's own `leaf_contract` when it is created; the
   eviction helper machinome-freecad reaches today is made unnecessary
   by keying the shape cache on the artifact's observation. What `shape()` returns once cadquery
   is out of the exact layer is a consequential interface and goes to
   the pilot with the proposal. Validated against machinome-freecad's
   adapter on a branch of that repository, the Dum-E cycle being the
   originating evidence; the adapter's retarget and rename are a later
   cycle there.
2. **Remove the class-name switch** at `node/base.py:1262` (removed by
   change `backend-switch`, 3 October 2026: the refusal names the node and
   its class; ADR-166).
3. **The exact engine seam and the exact layer on bare OCP.**
   `exact_engine()` and `require_exact_engine(needed_by, reason)` of the
   mesh engine's shape; the layer rewritten without the four cadquery
   spellings and moved out as `machinome.occt`; `node/fusion.py`
   resolving it lazily; `node/markings.py` resolving the SVG reducer
   from `machinome.node.build123d` and refusing an `Svg` marking by the
   extra's name without it.
4. **Dependencies.** cadquery, build123d, cadquery-ocp and molejo leave
   the core's required list, because their code leaves; the extras of
   "Import paths" replace them. No other dependency changes: the
   1 October list also named watchdog and manifold3d as grant
   groundwork, and the pilot struck them from this refactor on
   2 October as no technical dependency of it.
5. **The node root under the norm.** The five moved names leave the
   export table for the moved-names table; the core's own leaf types
   move from `machinome.node.adapters.<x>` to `machinome.node.<x>`;
   `machinome/__init__.py` and `machinome/node/__init__.py` extend
   their paths; the CLI's command table answers `import-step` with the
   `step` extra. vet's universe and its version pin follow; no new vet
   rule.
6. **The framework's manual and conformance gaps.** The install page
   with the extras, the node pages that move out, the imports section;
   and, since the framework is open anyway, the docs and dist CI jobs,
   the uploading release target and the assistant prompts the standard's
   section 6 lists (D10).

**Five new repositories,** each its own Git repository beside the
workspace, remotes and pushes the pilot's: machinome-occt,
machinome-node-cadquery, machinome-node-build123d, machinome-node-step,
machinome-node-molejo. Each born to the standard: licence and NOTICE,
README, changelog, CI with test, docs and dist jobs, `check-dist` with
the collision guard, OpenSpec and workflow records, a manual, and the
tests of "Import paths". Numbered with the framework (D7).

**Outside the framework:**

- *Workspace.* The layout, status and work sections of the operating
  contract, the README, the workspace's `scripts/setup` tier 2 and
  the workspace's `docs/collaborator-setup.md` learn the five repositories; the venv
  installs them editable; this note is copied to the framework's
  `workflow/ongoing/` as the campaign plan (D11). And a script that
  does the pushing work for the package repositories beside the
  workspace, the sibling of the workspace's `scripts/project-git-status --push` for
  the projects: report each repository's state, push safely-ahead
  branches and tags, and create a missing remote under the machinome
  organisation on an explicit flag. Run by the pilot only; an agent
  never passes its push flag (pilot, 2 October 2026).
- *Studio.* `shop-skills/machinome-api/SKILL.md` and the machining craft
  skill teach the one path and the extras.
- *Projects.* No import line is rewritten by this refactor; the
  one-path cycle's script does that once, with the moved names as rows.
  Every cycle is validated empirically as "Empirical validation, per
  cycle" below says.

### Empirical validation, per cycle

Settled by the pilot on 3 October 2026: every cycle of this campaign is
validated empirically before it integrates, at two depths, and the
validation is orchestrated with subagents like the rest of the cycle.

- **One project refactored by hand, deep.** On a branch
  `lean-core-validation` of that project's own repository: its suite run
  against the cycle's bench before and after the migration, both results
  in the cycle's evidence. The branch is never merged. It is also a
  fixture for the root-cleanup cycle's rewrite script, which must
  reproduce the hand edit exactly.
- **The whole universe loaded, shallow.** A workspace script beside
  `scripts/scan-projects`, cut in its own workspace cycle before the
  leaf-contract cycle needs it, loads every project's root against a
  given bench, one project at a time (the workspace is on virtiofs), and
  classifies each failure as expected, a name the cycle moved, or
  unexpected. It migrates nothing; an unexpected failure is a finding for
  the cycle before it integrates.
- **The end validation is not a substitute.** The root-cleanup cycle
  runs the rewrite script over the 74 repositories and every suite after
  it; the per-cycle work is what makes that step routine.

| cycle | project | why |
|---|---|---|
| exact engine | OpenAstroMount | the smallest direct caller of the exact operations |
| leaf contract | machinome-freecad, the Dum-E adapter | the originating evidence; the one third-party exact leaf. **Done** 3 October 2026: 82 passed after the migration, the universe loaded with no leaf-contract row; `openspec/changes/archive/2026-10-03-leaf-contract/evidence.md` |
| class-name switch | splitflap, a solid2 project (the abacus named on 3 October is CadQuery, a misreading corrected the same day) | the switch chooses backends by class name for solid2, OpenSCAD and fusion nodes. **Done** 3 October 2026: splitflap green before and after, refusal `node front (Solid2Node backend)` → `node front (FrontPanel)`; universe 120 ok, non-ok rows unchanged; `openspec/changes/archive/2026-10-03-backend-switch/evidence.md` |
| lean install | Actuators/Internal-Cycloidal-Actuator | its companion test imports `machinome.node.adapters.step` twice, so the migration runs in the suite the sweep loads; scaffolded by `machinome import-step` and all `StepNode` leaves, so it exercises the `step` extra, the moved module and the command. **Done** 3 October 2026: ICA 33/35 faceted before and after, the two failures the first cycle's currency; universe 117 ok, three new expected rows, nothing unexpected; `openspec/changes/archive/2026-10-03-lean-install/evidence.md` |
| expression type | Locks/Pin_tumbler_lock, with the Curta Type I 3x's clocked block and machinome-mechanics' suite as probes | a running root whose laws and bounds are built on `machinome.math`, whose flexible ports carry expressions and whose `Solid2Node` parts write SCAD carrying symbolic values: four of the five former facade importers, the seam's native path and the SCAD bytes in one cheap project; the Curta exercises the clocked face, mechanics the SolidPython operands. **Done** 3 October 2026: the lock 24/24 faceted before and after with every `.scad` byte-identical and `manifest.json` differing only in one piece volume's last digit, OpenSCAD's own STL noise; the Curta's clocked block identical (88910 bytes, `be1e37234b443566`); mechanics 9 failures, all its tests asserting solid2's `OpenSCADConstant` of a symbolic value, corrected by a mechanics cycle (the pilot); universe unchanged from the fourth cycle; `openspec/changes/archive/2026-10-03-expression-type/evidence.md` |
| scad presentation | Locks/Pin_tumbler_lock, and OpenAstroMount without SolidPython | the fifth cycle's project, so its 11 `Solid2Node` `.scad` hashes are compared byte for byte, and its sub-assembly, flexible spring and running root exercise every presentation construct and the three files a build stops writing; OpenAstroMount is the all-STEP project a build must publish with no SolidPython. **Done** 4 October 2026: the lock's build writes exactly its 11 `parts-*.scad`, byte-identical to a single-process build of the fifth cycle (its three-process after leg held self-imports a later process's `assemble()` wrote, a defect this change removes), no `lock-*` or `flexibles-*` file, 24/24 faceted, `manifest.json` identical; the OpenSCAD snapshot draws the root's SCAD (6916 bytes, 20 imports resolving) and removes it, and is refused naming the engine and `--renderer web` without it; the project's 31 lingering `.scad` swept to 11, also by a build that left the document unchanged; OpenAstroMount builds with `solid2` unfindable, 90 STL, 90 BREP, no `.scad`; universe identical to the fifth cycle's sweep, no row for this cycle; `openspec/changes/archive/2026-10-04-scad-presentation/evidence.md` |
| mesh engine | Locks/Pin_tumbler_lock, 3D-Printers/Prusa3-vanilla, Leonardo/models (`cam_hammer`) and OpenAstroMount without the engine | the lock is the campaign's faceted reference and Prusa3-vanilla the heaviest faceted user, so their verdict logs are compared line for line before and after; no project fuses faceted children, so `cam_hammer`'s two exact fusions show an exact fusion never asks for the engine, and the all-exact OpenAstroMount builds and tests with it absent. **Done** 4 October 2026: the lock 24/24 faceted before and after with its 2573 verdicts byte-identical, and with the engine absent `machinome test --faceted` refused at its start (exit 1, no STL) while `machinome build` wrote its 11 STL with no ask of `machinome.manifold`; Prusa3-vanilla 16 passed and 3 failed (pre-existing) before and after, its 15935 verdicts byte-identical, 1974 s against 1963 s; `cam_hammer`'s 14 artifacts identical unblocked and with the engine absent; OpenAstroMount built (90 STL, 90 BREP) and tested 8/9 (the known exact-common wart) with the engine absent, no process asking for `machinome.manifold` and every ask of `manifold3d` trimesh's own (`trimesh.boolean`, `trimesh.util`); universe identical to the sixth cycle's sweep, no row for this cycle; `openspec/changes/archive/2026-10-04-mesh-engine/evidence.md` |
| openscad out | Locks/Pin_tumbler_lock, 3D-Printers/Prusa3-vanilla, OpenAstroMount without the family, `machinome new` under three installs | the lock is the faceted and SCAD reference: its 11 `parts-*.scad`, its verdict log and an OpenSCAD snapshot's root `.scad` are compared byte for byte, the root `.scad` gone after the render; Prusa3-vanilla's verdicts likewise; OpenAstroMount builds and tests with `solid2`, `machinome.node.openscad` and `machinome.node.solid2` unfindable and `machinome snapshot` refuses naming the extra; `machinome new` scaffolds the template its installed extras provide. **Done** 4 October 2026: the lock's 11 build `.scad` and 15 after the test, 2573 verdicts and the snapshot's root `.scad` (and image, 0 differing pixels) byte-identical, the root `.scad` gone after the render and a transient one removed by an unchanged build; Prusa3-vanilla 16 passed and 3 failed (pre-existing), its 15935 verdicts byte-identical; OpenAstroMount 90 STL, 90 BREP, 0 `.scad` and 8/9 with the family unfindable and no attempt of it, `machinome snapshot` refused naming `machinome[openscad]`; `machinome new` byte-identical under all extras, CadQuery without SolidPython, refused with neither; universe identical to the mesh-engine sweep, no row for this cycle; `openspec/changes/archive/2026-10-04-openscad-out/evidence.md` |
| the cut | one per node package: a mid-size CadQuery project, one of the nine build123d projects, a STEP importer such as the Don1, a molejo project such as the Kossel; and the Curta Type I 3x | the Curta is the deepest caller, a hundred files reading shapes, and the 0.8 roadmap's conductor |
| manual and conformance | none | the manual's examples are pinned by tests |

**Orchestration.** The orchestrator runs the validation, as it runs
every agent of a cycle (pilot, 3 October 2026: "don't delegate your job,
you are the reviewer"). The applier implements, runs the framework's own
suite, then stops before its implementation commit and reports. The
orchestrator briefs and launches one validator subagent per project,
one at a time, with the bench, the project, the names the cycle moved
and the declared members it may use; runs the universe scan itself,
`scripts/load-projects` with every cycle's moved-names file and a 300 s
timeout; and hands both reports to the paused applier, which folds them
into the cycle's evidence, archives the change and commits. An applier
never spawns an agent. A failed validation returns to the orchestrator
with the project's output; it is never fixed in the project. The
moved-names file of a cycle is archived with the change and copied to
the workspace's `scripts/load-projects.d/<cycle>.toml`.

**Out of scope,** each its own later work: the one-path cycle itself,
both roots and the 74-repository migration; machinome-freecad's
retarget and rename; mechanics and movie moving to their addresses;
the machinome.org software roster; publication of anything; an
assembly extension contract, for which the FreeCAD adapter's carriers
are the evidence (its `_link_children` and `track_sources` reaches, the
`object.__new__` construction and the undeclared members the leaf-contract
validation recorded in its evidence, section 8).

## Sequencing

A bare `pip install machinome` stops providing exact leaves and the root
spelling of the moved names is refused, so this is 0.8 work. The pilot
settled on 2 October 2026 that it starts the 0.8 line, and that 0.8 is
released only when the whole set of packages complies with one set of
guidelines, mechanics, the studio and the video package included, none
of which is in this refactor's scope. The refactor opens the 0.8 line
and lands before the one-path cycle, so that cycle's tables carry the
final paths and the 74 repositories migrate once; the one-path cycle
runs right after it. Items 1 to 5 above go in that order, each a cycle;
the repositories are cut when item 3 has an engine to ship and item 5 a
root to leave. Framework main holds 0.7.1 tagged and unpublished;
merging the campaign at its close does not move the tag, and uploading
0.7.1 first, if wanted, is a step before the close.

The orchestrator's sequencing put item 3, the engine, first (change
`exact-engine`, 3 October 2026), and it runs before item 1's leaf-contract
cycle because that contract names the engine's currency: what `render()`
may return and what `shape()` returns are the engine's to state. The
markings' SVG reducer and its refusal by extra wait for the cut.

## What packaging does not solve

A project on the core alone gets OpenSCAD, solid2, JSCAD and STL leaves,
assemblies, mates, motion, simulation, faceted fusion and the viewer,
and loses only what needs a kernel that is not installed: exact leaves,
exact fusion, and the mesh-based assertions without `machinome[manifold]`,
the mesh engine's extra since the seventh cycle.
The policy names the remaining gap for a profile with no Apache code
beneath it: a non-Apache boolean engine. The obvious candidate is the
OpenSCAD process behind the existing mesh engine seam, since unioning
imported STLs in a SCAD file is what the pre-manifold compile-to-OpenSCAD
path did under ADR-004. That is a framework change of its own, gated on
a named project that needs it; none is named today.

## Open decisions, the pilot's

Twelve decisions a campaign needs settled, listed on 1 October 2026
with a recommendation on each. D1 to D5 were settled by the pilot on
2 October 2026 and are marked; the rest remain open, the pilot
deliberating and having said the matter is big. A recommendation here
is an agent's reading of the evidence above, not a default that applies
if nobody answers.
The first five are design, the next two are release policy, the last
five are scope and sequencing.

### D1. Package names (settled 2 October 2026)

The norm of "Import paths": `machinome.node.<nodetype>`,
`machinome[<nodetype>]`, `machinome-node-<nodetype>`, one package per
node type; `machinome.<name>`, `machinome[<name>]`, `machinome-<name>`
for anything else. Hence machinome-occt, machinome-node-cadquery,
machinome-node-build123d, machinome-node-step and machinome-node-molejo.
The engine package is named for the kernel it wraps; the alternatives
`machinome-exact` and `machinome-brep` name a capability rather than a
kernel, so a second exact kernel would have nowhere to go. The morning's
`machinome.cadquery` was struck by the pilot: that address is what the
norm reserves for a non-node thing, which is why it read wrong for a
node.

### D2. How a seam resolves its provider (settled 2 October 2026)

A try-import of a known provider, as the mesh engine does, for every
seam: the exact engine from `machinome.occt`, the `Svg` reducer from
`machinome.node.build123d`, the `import-step` command from
`machinome.node.step`, each refusing with the name of the extra that
provides it. No entry-point group is introduced; the viewer's stays. The
node root keeps no table of satellite names: under the one-path rule it
exports nothing, so the question that produced the morning's table, and
the plugin registry weighed against it, is moot. A kernel the core does
not declare takes the same addresses; only the extra is missing.

### D3. CLI commands that move with a package (settled 2 October 2026)

`import-step` is reached by 33 projects and its implementation goes to
machinome-node-step. The core keeps a command table naming the module,
`machinome.node.step`, and the extra; the command exists when the
package is installed, and when it is not, the core answers the command
name with the extra to install, not with an unknown-command error.

### D4. Where MolejoNode lives (settled 2 October 2026)

Its own package, machinome-node-molejo, in its own repository under the
machinome organisation; machinome-occt carries no node type. The
1 October recommendation, riding in the engine, was struck by the pilot
with the package-per-node-type rule. Not a package inside molejo's
repository, for the reasons under "The node packages".

### D5. Markings and build123d (settled with the map, 2 October 2026)

Four projects use SVG markings, and the SVG region reducer is
build123d. The declarations `Marking`, `Wrapped`, `Flat` and `Svg` stay
in the core; the reducer lives in `machinome.node.build123d`; an `Svg`
marking resolves it through the seam and refuses by the extra's name
when it is absent.

### D6. watchdog

The file watcher behind `develop` is the one Apache-2.0 dependency that
would remain required in core after the split.

Recommendation: leave it required for now and record it here as the
item to revisit if the grant question returns. Making `develop` an
extra is awkward because the floor uses it.

### D7. Kernel package numbering (settled 2 October 2026)

Numbered with the framework and released with it, the viewer pattern,
or an own sequence with a declared framework minimum, the mechanics
and molejo pattern.

Numbered with the framework, the pilot's decision: the node and engine
packages implement an extension contract that moves with framework
minors and release together with it; mechanics and molejo are
independent libraries and these packages are not. A node package
depends on `machinome~=0.8.0` and the core's extra pins it back the
same way.

### D8. One campaign or two

Recommendation: one campaign, the scope under "What it takes", its
cycles in order on one line, the repositories cut mid-campaign when
there is an engine and a root to ship. The 1 October reason for two,
that the cut broke import lines and so belonged inside 0.8's declaration
break, dissolved under the one-path rule: the root spelling is refused
either way, and the one-path cycle migrates every project once, right
after this campaign.

### D9. The Dum-E cycle

machinome-freecad is mid-cycle in its worktree, pinned to
`machinome==0.7.1`, importing cadquery and the private eviction helper.

Recommendation: let that cycle close on 0.7.1 first. The
extension-contract cycle then takes its evidence and the adapter is
retargeted afterwards. Opening the campaign under it would move the
ground the adapter is being validated on.

### D10. Conformance gaps of the existing packages

the workspace's `docs/software-package-standard.md` applies to every package and its
section 6 lists the gaps.

Recommendation: the framework's own gaps ride in the first campaign,
since the framework is open anyway: the missing docs and dist CI jobs,
the uploading `make release` target, the `.claude/commands` and
`.claude/skills` prompts. The viewer, mechanics, molejo and studio
gaps are their own small cycles later, each under its repository's
process.

### D11. Where the plan lives (done 2 October 2026)

This plan lives in the framework at `workflow/ongoing/lean-core.md`,
framework material committed in the framework; the workspace's
`docs/lean-core-package.md` points at it. The standard stays in the
workspace at `docs/software-package-standard.md`, since it governs
every repository.

### D12. Orchestration

As practised from the first cycle (2 and 3 October 2026): one proposer
and one applier per cycle, fresh agents with a written briefing, the
orchestrating agent's adversarial review as the ratification gate, one
agent at a time; the orchestrator fast-forwards a reviewed cycle into
the campaign line `v0.8-split` (named `v0.8` from 2 to 4 October 2026,
renamed by the pilot so the name is not the release tag's), merges the
line into `main` at the campaign's
close, and pushing and uploading stay the pilot's. The empirical
validation of each cycle is orchestrated the same way, with validator
subagents, as "Empirical validation, per cycle" under "What it takes"
says (pilot, 3 October 2026).

### Settled by the pilot, 4 October 2026, later the same day: the grant stays Apache-2.0

The reopening below lasted a few hours. Assessing what a GPL-2.0-only
OpenSCAD project needs (collision and clearance tests above all: Prusa3-
vanilla's suite is 63 `assertNotIntersecting`, 24 gap assertions, 16
motion sweeps of the same question, 4 overlap-volume thresholds), the
pilot found that supporting them would cost not only the core's grant
but a second faceted engine behind a reshaped mesh seam (predicates on
a BSD collision library such as FCL, overlap volumes through the
OpenSCAD process or refused), since manifold3d is Apache-2.0 and no
GPLv2-compatible mesh-boolean library exists for Python (CGAL is GPLv3).
The pilot's decision: "I'm not giving up patent protection for
supporting those projects." The core stays Apache-2.0; the licence
policy of "Settled" stands as written; GPL-2.0-only projects stay out of
the Foundry (the policy of `docs/foundry-licensing-policy.md`).

Consequences for this plan: the package split (layer 2) is no longer a
licensing requirement. It remains wanted for the architecture and for
the lean install, choosing only what a project needs; its repository
question stays open on evidence, as "Layers" says. The next cycle after
this session is the extraction of manifold3d behind the mesh seam, for
the architecture alone, by the same shape as the exact engine (the pilot,
4 October 2026); watchdog stays as it is.

### Reopened by the pilot, 4 October 2026: the licences

The pilot unlocked the licence policy below ("a package's licence matches
its provider's": the four node packages Apache-2.0, machinome-occt
LGPL-2.1 as OCCT) and, with it, "the core's grant stays as it is". The
pilot is reconsidering and named the direction under consideration:
everything but the studio under LGPL-2.1-or-later. Nothing is decided; a
dedicated licensing session decides, with the line-level check of the
second author's commits recorded under "Settled" still due before any
relicensing. Until then no layer-2 package is cut and no licence file,
NOTICE or classifier moves. Layer 1 (cycles 7 and 8, then the root
cleanup) does not depend on the answer; layer 2 turns on it.

### Settled, and not reopened

- The core's grant stays as it is (reopened 4 October 2026, see above). For the record, the framework's
  history is 798 commits by Luis Fagundes and 9 by Fabio Montefuscolo
  (July 2023 and February 2025: CI workflows, docs, requirements files
  and a `solid_node/exceptions.py` since removed); a line-level check
  that nothing of those commits survives is due before any relicensing.
  molejo and machinome-mechanics are single-author.
- FusionNode stays in core.
- Every package is imported as `machinome.something` under the norm of
  "Import paths": `machinome.node.<nodetype>`, `machinome[<nodetype>]`,
  `machinome-node-<nodetype>`, one package per node type, each its own
  repository; machinome-occt carries no node type; machinome-node-molejo
  is its own package and repository; `ExactLeafNode` stays in the core;
  no table and no entry-point group (2 October 2026).
- A package's licence matches its provider's: the four node packages
  are Apache-2.0 and machinome-occt is LGPL-2.1 as OCCT is (reopened
  4 October 2026, see above); all are
  numbered with the framework; the
  refactor starts the 0.8 line, and 0.8 is released only when every
  package of the set, mechanics, studio and video included, complies
  with one set of guidelines (2 October 2026).
- watchdog and manifold3d are not touched by this refactor; they were
  grant groundwork on the 1 October list, not a dependency of the
  split (2 October 2026).
- No name holders; the packages of a release set are published together
  when the pilot decides.
- A GPLv2 boolean engine is struck until a project names itself.

## Evidence pointers

- `pyproject.toml`, the dependency list and the pin comment.
- `machinome/exact.py`, `node/exact_leaf.py`, `node/fusion.py`,
  `mesh_engine.py`, `node/__init__.py`, `node/base.py:1262`,
  `node/markings.py`, `core/builder.py`, `test.py`, `vet/universe.toml`.
- `docs/adrs/NODE/ADR-046-conditional-openscad-dependency.md`,
  `ADR-047-shared-occt-currency-for-exact-backends.md`.
- `machinome-freecad/README.md`,
  `machinome-freecad/workflow/ongoing/dume-native-freecad.md`, and the
  adapter's imports in `machinome-freecad/WTs/native-freecad-assembly/`.
- the workspace's `docs/foundry-licensing-policy.md`, section "What the framework's
  license allows".
- `workflow/ongoing/roadmap-0.8.md` and `magic-strings.md`.
- `machinome/__init__.py` and `node/__init__.py`, the regular
  package and the lazy accessor the import paths build on; the
  workspace venv's `__editable__.*` files, which show the setuptools
  finder strategy the install matrix was verified against.
- Python Packaging User Guide, "Packaging namespace packages".
- `workflow/ongoing/roadmap-0.8.md`, the section headed "Task
  1 — one import path", the one-path cycle this note's import paths
  obey; `openspec/specs/ports/spec.md` for the ratified
  sentence.

## The next phase: the architecture ready for the split (pilot, 4 October 2026, later session)

Ratified by the pilot from the counts of 4 October 2026, taken on the
line at 57928eb, after the closing rulings above. The phase is the rest
of layer 1: four cycles on `v0.8-split` (three, and the viewer cycle the
pilot added the same day), then the pilot confirms the package names, then
layer 2 starts with an actual cut.

**What "ready for the split" means, measured on 57928eb.**

- The core imports no node package and no kernel. One blocker: the
  import-step command (`manager/import_step.py`) reaches
  `machinome.node.step`. Node `step` imports `machinome.node.cadquery`,
  which is a declared dependency (`[step]` installs CadQuery) and stays.
- No "scad" in the core outside the OpenSCAD family: 41 modules say it
  (the fifteen above with more than five mentions, and 26 more with one to
  five), and 105 test files. No project names the SCAD API (`scad_file`,
  `scad_code`, `generate_scad`, `as_scad`, `scad_authored`, the seam, the
  renderer): grep of `projects/` on 4 October 2026 with vendored trees
  excluded. The removal breaks no project.
- One address per name: 1007 project files import from the `machinome.node`
  root (679 `AssemblyNode`, 190 `CadQueryNode`, 78 `MolejoNode`, 56 `Frame`,
  55 `StlNode`, 28 `StepNode`, 12 `FusionNode`, 12 `declared_children`,
  `Solid2Node`, `Build123dNode`, 4 `OpenScadNode`, 1 `JScadNode`); 35
  import from the module. `machinome/__init__.py` re-exports nothing
  already.
- The final engine words: `exact` and `faceted` appear in 39 of the 46
  specs and in eight spec names (`exact-engine-dependency`,
  `exact-geometry`, `manifold-engine`, `mesh-engine-dependency`,
  `occt-engine`, `openscad-dependency`, `openscad-engine`,
  `scad-engine-dependency`); in the projects only three files of
  3DPrintedClocks spell `--faceted` (the Curta's tools use `faceted` as
  their own parameter names, which stay).
- A portion resolves without the core's `__init__`: `_namespace_portions`
  exists since `lean-install` and nothing uses it yet; the first cut of
  layer 2 is its proof.

**The cycles, in order.**

1. `openscad-out`, gated by the red-first scan test (above). The family
   becomes one package directory `machinome/node/openscad/`: the node, the
   SolidPython writer (with `scad_expression` from `core/expressions.py`),
   the binary runner, the OpenSCAD snapshot renderer, and the `scad_code`
   family as the family's own methods; `Solid2Node` as its own module over
   it, with `as_number` and the adoption of SolidPython values that
   `expression_graph.py` does today through the seam. `machinome/openscad/`,
   `machinome/scad_engine.py` and `machinome/viewers/openscad.py` vanish.
   What the core keeps is nameless: a leaf declares the artifacts it keeps,
   so the builder's sweep is generic; a presentation is a description any
   installed package may write; the expression graph adopts foreign values
   through a hook the solid2 package registers; the generation census of
   `source_generation.py` stays and ADR-086's coalescing goes; the template
   scaffolds whatever leaf kind the installed extras provide. `jscad` and
   `stl` as packages wait for the root cleanup: this cycle is the
   campaign's biggest and symmetry adds nothing to its risk.
   **Done** (4 October 2026): branch `v0.8-split-openscad-out`, planning
   commit f76aa20, ratified with the transient record for the
   unchanged-document sweep (ADR-177, 178, 179). As ratified it narrows the
   paragraph above: the OpenSCAD snapshot renderer stays at
   `machinome/viewers/openscad.py`, importing the package directly, until the
   viewer cycle; `scad_expression` stays in the core as `closed_expression`;
   the table of supported node types is `machinome/node/supported.py`. The
   gate is at zero, the suite green (4513 passed, 4 skipped), every
   validation leg green. Evidence:
   `openspec/changes/archive/2026-10-04-openscad-out/evidence.md`.
2. `brep-mesh`. Providers at `machinome/engine/brep.py` and
   `machinome/engine/mesh.py`; the two seams in the engine package's
   `__init__`, which extends its path with portions as `machinome/node/`
   does. Renamed: the B-rep leaf base, the capability and the eight spec
   names, the verdict paths, `--faceted`, the recipe identities, the
   refusals, and the extras (`occt` becomes `brep`, `manifold` becomes
   `mesh`: an extra is named for the module it serves, ADR-167). Persisted
   verdicts are keyed by the path words, so every project's store
   recomputes once after the rename; no migration code (the orchestrator's
   preference, for the pilot at ratification). Moved-names table
   `brep-mesh.toml`.
   **Done** (5 October 2026): branch `v0.8-split-brep-mesh`, planning
   commit dfc9681 on faf1c80, ratified with every recommendation of
   design.md's Open Questions but the second, ruled the other way: the
   run's choice is its engine (`SOLID_TEST_ENGINE`, `--brep`/`--mesh`,
   `ComparisonPolicy.engine`, `ENGINES`), the former variable refused when
   set (ADR-180). The gate is at zero, the suite green (4568 passed, 4
   skipped), the five goldens and every validation leg green (the lock's
   2573, Prusa3-vanilla's 15935 and OpenAstroMount's 1302 verdicts identical
   but for the path word; the universe one new expected row,
   OpenAstroMount). Evidence:
   `openspec/changes/archive/2026-10-05-brep-mesh/evidence.md`; the
   moved-names table is that archive's `moved-names.toml`.
   Follow-ups the campaign owes outside the framework, none of them this
   cycle's edits: machinome-studio's `machinome_test` tool
   (`floor/mcp_server.py`) and its test pass `--faceted`/`--exact`, and its
   `machinome-api` and `machinome` skills spell those flags and
   `SOLID_TEST_KERNEL` (now `SOLID_TEST_ENGINE`), a paired studio change
   when the line merges into `main`; the workspace's
   `skills/simulate-project/SKILL.md` spells the former flags; the
   workspace's `scripts/load-projects.d/` gains `brep-mesh.toml` from this
   change's `moved-names.toml`; every checkout's `.env` setting
   `SOLID_TEST_KERNEL` is refused until renamed; machinome-freecad's
   retarget subclasses `BrepLeafNode` and declares leaf contract 3.
3. `root-cleanup`. The node root stops re-exporting: each of its 20 names
   refuses with the module's address, as the moved port names do. A new
   rewrite script, modelled on `scripts/migrate-projects-to-machinome`,
   applies every moved-names table and the root table over the universe in
   one pass, fixes the four customers waiting since `lean-install`
   (Voron-2, the Actuator, YouCanBuildDog, the Don1), and the sweep comes
   back with no expected failure; the project repositories are committed
   one by one after the sweep is green. `jscad` and `stl` become packages
   here.
4. The viewer cycle, the phase's last by the pilot's decision of 4 October
   2026: viewers become providers behind a seam `machinome.viewer`
   (`machinome.viewer.openscad`, `machinome.viewer.web`), done after the
   root cleanup. It moves `machinome/viewers/openscad.py`, the last module
   outside the OpenSCAD node family the `openscad-out` gate admits, and
   removes the provisional renderer column of the table of supported node
   types.

Then the first cut of layer 2 is the mesh engine: one module, one extra,
the smallest proof that a portion resolves from a second distribution.

**Two rulings of the same discussion (pilot, 4 October 2026).**

- *Capability flags become one declared set on the leaf base.* Today the
  node spine is nominal (a node type subclasses one of the four leaf bases,
  whose `leaf_contract` integer is checked at class creation; the core
  dispatches by `isinstance` on the bases, never on a class name, ADR-166)
  and every kind distinction inside it is a duck attribute the core probes
  with `getattr` and a default: `exact`, `flexible`, `rigid`, `stl_file`,
  `base_mesh`, `scad_authored`. Each flag was added when a kind appeared,
  and that accretion is how SCAD leaked into the core (the sweep and the
  renderer probe `scad_authored`; the leaf base still says a faceted leaf
  "presents its render as SCAD"). The ruling: the flags are one declared
  set on the base, which `openscad-out`'s proposer designs; `scad_authored`
  and `as_scad` become a leaf's declaration of the artifacts it keeps and
  how it presents, without the technology's name.
- *The renderer architecture is revisited by the pilot on this
  architecture.* Renderers have neither nominal nor duck typing today: the
  OpenSCAD renderer answers `present`, `withdraw` and `render`, the browser
  renderer `render` and `capture`, and the snapshot command chooses by
  comparing a string. `openscad-out` does the least that gets SCAD out of
  the core, so that the pilot's revisit is not pre-empted: the OpenSCAD
  renderer moves into the package and the snapshot command reaches it, and
  the import-step command reaches the step package, through the one table
  of supported node types the ruling allows, each entry naming the
  package's module and extra, refusing with the extra's name when absent.
  Discovery of contributions from installed portions, and a renderer
  contract, are the pilot's later decision. The engine shape (a module of
  free functions behind one address, an integer contract, an opaque
  currency, a golden conformance kit for the mesh side) is the model the
  pilot wants carried to it.

For this session the removal cycle is the realistic work; the rename is
mechanical and may follow; the root cleanup depends on the rewrite script
and runs last. The orchestration stays as practised.

## The last cycle of the phase: `viewer-seam` (pilot, 4 October 2026)

Decided by the pilot while `openscad-out` was being proposed, and deferred
to the end of the phase because that cycle is too big to carry it: the
viewers become pluggable providers, symmetric, behind one seam, on the
engines' model. The word is **viewer**: "renderer" confuses with
`node.render()`; the directory `machinome/viewers/`, the flag
`--renderer` and the word in every message become `viewer`, singular like
`node` and `engine`. Planned now, executed after `root-cleanup`.

**What exists today (the line at a16d45a).** `machinome/viewers/` holds
three modules and no seam. The OpenSCAD one (`openscad.py`) is a class
answering `present`, `withdraw` and `render`: it writes the root SCAD on
demand inside the build lock, runs the binary, removes the SCAD in a
`finally`. The web one (`browser.py`) answers `render` and `capture`: it
stages a directory from the existing build, baking one instant and copying
artifacts, then runs `machinome-viewer capture` as a subprocess. The third
(`bundle.py`) finds the viewer package through the entry-point group
`machinome.viewer` and answers describe, bundle path, API version,
document versions and the command line. The snapshot command compares the
string `--renderer` in four places and calls different methods on each.
The web viewer is reached from six places in the core (snapshot, develop
running `machinome-viewer serve`, export embedding the bundle, the builder
refusing a document version the installed viewer cannot read, the Sphinx
extension, the `machinome viewer` command); the OpenSCAD one from one. The
process boundary and the entry point exist for the licence difference
(ADR-068), which the one licence removes. Two roles are mixed under
"renderer": capturing a fixed pose to an image, which both do, and
interactive viewing, which only the browser does since ADR-103; export and
documentation embedding are a third, browser-only by nature.

**The shape, ratified in outline.**

- A seam `machinome/viewer/__init__.py` declares the contract as Protocols
  with an integer `CONTRACT` and extends its path with portions, as
  `machinome/node/` does. Providers `machinome.viewer.openscad` and
  `machinome.viewer.web`; packages `machinome-viewer-openscad` and
  `machinome-viewer-web`; extras `viewer-openscad` and `viewer-web` (the
  extras cannot be `openscad` and `web`: `openscad` is the node extra).
- Unlike the engines (one per role at a fixed address), viewers coexist
  and are chosen by name: `viewer(name)` imports `machinome.viewer.<name>`,
  refuses an absent one by its extra and a wrong contract as incompatible.
  The existing requirement of `web-snapshot`, "the renderer is selected
  explicitly and never substituted", stays the rule. The default rule
  (today: `openscad` for snapshot, `web` for develop) is the pilot's
  decision at ratification; the orchestrator's preference is an explicit
  `--viewer`, a project able to name its default viewer in its manifest,
  and no fallback chain.
- The contract's operations are what the core asks today: identity and the
  document versions read; whether a document version is readable; present
  and withdraw, preparing what the viewer reads at one assembled instant;
  capture to an image; serve interactively; embed into an export or a
  documentation page. Not every viewer offers every operation: the ruling
  on leaves applies again, one declared set on the contract, and a command
  asking for an operation the chosen viewer lacks is refused by name (the
  OpenSCAD viewer declines to serve unless someone wants the GUI back).
- The web viewer's staging moves into its provider, which knows what its
  page reads; the core offers the assembled node, the presentation
  description, the document serializer and the artifact inventory.
- The OpenSCAD provider depends on the openscad node package for the SCAD
  writer and the binary. `openscad-out` leaves `machinome/viewers/openscad.py`
  where it is, an allowed zone of its scan, reached through the node-type
  table's provisional column; this cycle moves both viewers under the seam
  once and removes that column and `viewers/`.
- The web provider in the core wraps the viewer process (`capture`,
  `serve`, the bundle) exactly as `browser.py` and `bundle.py` do today, so
  the cycle does not wait for the viewer package's return; when the viewer
  comes into the monorepo under the one licence, its own portion
  `machinome.viewer.web` replaces that wrapper, the entry-point group
  `machinome.viewer` and the subprocess go, and the bundle ships inside the
  provider (a change in the viewer repository too, two changes in two
  repositories as the contract says).
- Commands: `snapshot --viewer <name>`; `develop` asks the chosen viewer to
  serve; export and the Sphinx extension ask embed; the builder asks
  readable; `machinome viewer` reports the installed viewers.
- Moved names: the `viewers` package and its three modules, the flag. The
  projects' `--renderer` uses are rewritten by the rewrite script's second
  run, with this cycle's table, after the root cleanup's single pass.

**What the deferral costs**: one provisional column in the node-type
table, removed here; the `viewers` directory living beside the plan for
three cycles; a second, small run of the rewrite script for the flag.
Nothing in `brep-mesh` or `root-cleanup` touches a viewer.

## Root cleanup decided; the viewer deferred; 0.8 after the root is clean (pilot, 5 October 2026)

Three decisions for `root-cleanup`, the pilot's, taken while `brep-mesh`
was in validation:

1. **The node root exports nothing.** Every name is imported from its
   module (`machinome.node.assembly`, `machinome.node.cadquery`, ...); each
   of the twenty former root names refuses with the module's address, as
   the moved port names do. The one-path rule, applied to the core's own
   structural names as well as to the node types. The manual's examples
   change with the code.
2. **The script rewrites every repository.** The pilot stops work in
   Voron-2 for it; Voron-2's `shape()` call sites (29 files calling CadQuery
   methods on the engine's shape) are done by hand inside the same pass.
   The orchestrator announces the pass; no session writes in a project
   repository during it; a repository with uncommitted changes in a file
   the script must rewrite is skipped and reported, never overwritten.
3. **Rewrite and commit on whatever branch each repository has checked
   out**, one commit per repository naming the cycle, only the rewritten
   files in it; untracked `.env` files are rewritten and not committed;
   worktrees inside a project (the Curta's `WTs/`) are other branches and
   are reported, not rewritten.

**The viewer cycle is deferred** past 0.8: the phase ends with
`root-cleanup`; `viewer-seam` ("The last cycle of the phase" above) waits
for the pilot's word after the release, and ADR-179's provisional
renderer column ships as it is.

**0.8 is released once the root is clean** (the pilot). Before or with the
release, outside the framework: the studio's `machinome_test` tool and its
two skills, and the workspace's `skills/simulate-project/SKILL.md`, still
pass `--faceted`/`--exact` and break against the renamed flags.
