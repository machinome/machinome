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
| manifold3d | Apache-2.0 | `mesh_engine.py` (already conditional), `node/fusion.py`, `test.py` | stays an optional engine |
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
  returns manifold3d's classes or None, and `require_mesh_engine` raises
  one actionable error naming the install, only when a path needs it.
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
  `workflow/ongoing/magic-strings.md` inventories.
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
so order does not matter.

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
| `ExactLeafNode`, the declared exact-leaf base, beside the other three declared leaf bases `LeafNode`, `SheetLeafNode` and `FlexibleNode` | `machinome.node.exact_leaf`; `machinome.node.leaf`, `.sheet_leaf`, `.flexible` | core | machinome |
| mechanics, movie, later and under their own processes | `machinome.mechanics`, `machinome.movie` | `machinome[mechanics]`, `[movie]` | machinome-mechanics, machinome-movie |

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

### Not split, and why

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

## What it takes: the scope of the first refactor

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
2. **Remove the class-name switch** at `node/base.py:1262`.
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
| class-name switch | splitflap, a solid2 project (the abacus named on 3 October is CadQuery, a misreading corrected the same day) | the switch chooses backends by class name for solid2, OpenSCAD and fusion nodes |
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
exact fusion, and the mesh-based assertions when manifold3d is absent.
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
the campaign line `v0.8`, merges the line into `main` at the campaign's
close, and pushing and uploading stay the pilot's. The empirical
validation of each cycle is orchestrated the same way, with validator
subagents, as "Empirical validation, per cycle" under "What it takes"
says (pilot, 3 October 2026).

### Settled, and not reopened

- The core's grant stays as it is. For the record, the framework's
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
  are Apache-2.0 and machinome-occt is LGPL-2.1 as OCCT is; all are
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
