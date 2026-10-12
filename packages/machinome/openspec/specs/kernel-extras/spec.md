# kernel-extras Specification

## Purpose

Which CAD kernels the framework requires (none) and how a project installs
the ones its parts use: one extra per kernel module, named by the last
component of the module's address, and a refusal at the module's import,
naming the install line, when its kernel is absent. Encodes ADR-167
(OpenSpec change `lean-install`), ADR-176 (`mesh-engine`), ADR-177 and
ADR-179 (`openscad-out`) and ADR-180 (`brep-mesh`).

Code: `machinome/extras.py`, the kernel modules `machinome/node/cadquery.py`,
`build123d.py`, `step.py`, `molejo.py`, `solid2.py`, the package
`machinome/node/openscad/`, the engine package's providers
`machinome/engine/brep.py` and `machinome/engine/mesh.py`; the table of supported node types
`machinome/node/supported.py`; `pyproject.toml`, `requirements.txt`,
`tox.ini`.
## Requirements
### Requirement: The CAD kernels are extras, not required dependencies

The framework's required dependencies SHALL NOT include a CAD kernel: neither
`cadquery`, `build123d`, `ocp-gordon`, `molejo`, `cadquery-ocp`,
`manifold3d` nor `solidpython2`, nor an engine or node distribution. Each
kernel SHALL be installed by an extra named by the last component of the
address of the module that needs it:

- `brep`, for the B-rep engine `machinome.engine.brep`: the distribution
  `machinome-engine-brep`, which requires the OCCT binding;
- `mesh`, for the mesh engine `machinome.engine.mesh`: the distribution
  `machinome-engine-mesh`, which requires `manifold3d`;
- `cadquery`, for `machinome.node.cadquery`: the distribution
  `machinome-node-cadquery`, which requires CadQuery and the B-rep engine;
- `build123d`, for `machinome.node.build123d`: the distribution
  `machinome-node-build123d`, which requires build123d, its `ocp-gordon`
  bound and the B-rep engine;
- `step`, for `machinome.node.step`: the distribution `machinome-node-step`,
  which requires `machinome-node-cadquery`, CadQuery and the B-rep engine;
- `molejo`, for `machinome.node.molejo`: the distribution
  `machinome-node-molejo`, which requires `molejo[brep]` and the B-rep engine;
- `openscad`, for the package `machinome.node.openscad`: the distribution
  `machinome-node-openscad`, which requires SolidPython;
- `solid2`, for `machinome.node.solid2`: the distribution
  `machinome-node-solid2`, which requires `machinome-node-openscad` and
  SolidPython;
- `jscad`, for `machinome.node.jscad`: the distribution `machinome-node-jscad`,
  which requires no Python package the core does not require (its renderer,
  the `jscad` command, is a Node program no pip extra installs);
- `stl`, for `machinome.node.stl`: the distribution `machinome-node-stl`, which
  requires trimesh, a required dependency of the core;
- `freecad`, for the package `machinome.node.freecad`: the distribution
  `machinome-node-freecad`, which requires the B-rep engine, `numpy` and
  `scipy` (its runtime, FreeCAD, is a program no pip extra installs, found
  through `MACHINOME_FREECAD_ROOT`);
- `all`, every extra above.

Every extra above but `all` SHALL require its distribution with the
compatible-release pin `~=<version>`, the version being the framework's own,
and each of those distributions SHALL require the framework with the same pin
and state its kernel: `machinome-engine-brep` the OCCT binding
`cadquery-ocp>=7.8.1,<7.9`, stated there and nowhere else;
`machinome-engine-mesh` `manifold3d`, unranged; each node distribution over
the B-rep engine its kernel and `machinome-engine-brep~=<version>`, and
`machinome-node-step` also `machinome-node-cadquery~=<version>`, whose module
it imports; `machinome-node-openscad` SolidPython; `machinome-node-solid2`
`machinome-node-openscad~=<version>`, whose modules it imports, and
SolidPython; `machinome-node-freecad` `machinome-engine-brep~=<version>`, whose
OCCT binding its package imports, with `numpy` and `scipy`. A distribution of the set SHALL declare every third-party package
its module imports directly, unranged when the framework pins the range.

Every node type of the table of supported node types SHALL have the extra of
its key, so the install line a refusal or a manifest names for a node type,
`machinome[<key>]`, is always one pip resolves, and each such extra SHALL
install the node type's distribution; the framework's distribution SHALL ship
no node type, so a bare install carries none. `machinome.node.jscad` and
`machinome.node.stl` SHALL check no kernel and refuse nothing at import.

Every kernel requirement SHALL keep the version range the framework required
before it became an extra, and a kernel named by two manifests SHALL carry the
same range in both, so installing several extras resolves one OCCT binding and
one SolidPython.
No node extra and no node distribution SHALL require the mesh engine: a B-rep
project needs it only for a mesh question, which it may never ask.

`watchdog`, `trimesh`, `numpy`, `scipy`, `shapely`, `rtree` and the other
dependencies the core imports SHALL stay required.

The extra that installs the development tools SHALL include `all`, and the
continuous integration SHALL install the repository's workspace from its
lock, whose default group installs that extra, so the framework's own suite
runs every kernel, both engines and every node package.

The installation page of the manual SHALL name, for each extra that installs a
distribution of the set, the distribution it installs.

#### Scenario: A bare install carries no kernel

- **WHEN** the framework's package metadata is read
- **THEN** its required dependencies name none of `cadquery`, `build123d`,
  `ocp-gordon`, `molejo`, `cadquery-ocp`, `manifold3d`, `solidpython2`,
  `machinome-engine-brep`, `machinome-engine-mesh` or a
  `machinome-node-<name>` distribution, and they still name `watchdog` and
  `trimesh`

#### Scenario: Each extra installs what its module needs

- **WHEN** the package metadata's extras are read
- **THEN** `brep`, `mesh`, `cadquery`, `build123d`, `step`, `molejo`,
  `openscad`, `solid2`, `jscad`, `stl`, `freecad` and `all` are declared,
  `brep` requires `machinome-engine-brep~=<version>`, `mesh`
  `machinome-engine-mesh~=<version>`, and each of `cadquery`, `build123d`,
  `step`, `molejo`, `openscad`, `solid2`, `jscad`, `stl` and `freecad`
  `machinome-node-<key>~=<version>`, with the framework's version and nothing
  else, `all` includes every one of them, every key of the table of supported
  node types is an extra, and the development extra includes `all`

#### Scenario: Each engine distribution requires the framework and its kernel

- **WHEN** the manifests of `machinome-engine-brep` and
  `machinome-engine-mesh` are read
- **THEN** each requires `machinome~=<version>` with the framework's
  version and `numpy`, the B-rep engine `cadquery-ocp>=7.8.1,<7.9` and the
  mesh engine `manifold3d`

#### Scenario: Each node distribution requires the framework, its kernel and the B-rep engine

- **WHEN** the manifests of `machinome-node-cadquery`,
  `machinome-node-build123d`, `machinome-node-step` and
  `machinome-node-molejo` are read
- **THEN** each requires `machinome~=<version>` and
  `machinome-engine-brep~=<version>` with the framework's version; the
  CadQuery package `cadquery==2.7.*`; the build123d package
  `build123d==0.10.*`, `ocp-gordon>=0.2.2,<0.3` and `numpy`; the STEP package
  `machinome-node-cadquery~=<version>`, `cadquery==2.7.*` and `numpy`; the
  molejo package `molejo[brep]==0.2.*` and `trimesh`; and none names
  `cadquery-ocp`, `machinome-engine-mesh` or `machinome[mesh]`

#### Scenario: Each node distribution over no B-rep engine requires the framework and what its module imports

- **WHEN** the manifests of `machinome-node-openscad`, `machinome-node-solid2`,
  `machinome-node-jscad` and `machinome-node-stl` are read
- **THEN** each requires `machinome~=<version>` with the framework's version;
  the OpenSCAD package `solidpython2==2.1.*`; the solid2 package
  `machinome-node-openscad~=<version>` and `solidpython2==2.1.*`; the JSCAD
  package nothing more; the STL package `trimesh`; and none names an engine
  distribution or `machinome[mesh]`

#### Scenario: The ranges are the ones required before

- **WHEN** the extras' and the distributions' requirements are read
- **THEN** CadQuery is `==2.7.*` wherever it is named, build123d `==0.10.*`,
  `ocp-gordon` `>=0.2.2,<0.3`, molejo `molejo[brep]==0.2.*`, the OCCT
  binding `>=7.8.1,<7.9` and named only in `machinome-engine-brep`'s
  manifest, SolidPython `solidpython2==2.1.*` wherever it is named and nowhere
  in the framework's manifest, and `manifold3d` carries no range, as when it
  was required

#### Scenario: Continuous integration installs every kernel

- **WHEN** the CI workflow and the repository's lock are read
- **THEN** the `lint`, `test` and `browser-snapshot` jobs each run
  `uv sync --locked` at the repository root, and the lock holds every
  concrete requirement of the `all` extra, `manifold3d`, `cadquery-ocp`,
  `solidpython2`, both engine distributions and the nine node distributions
  among them

#### Scenario: The installation page names the extension distributions

- **WHEN** the manual's installation page is read
- **THEN** it names `machinome[brep]`, `machinome[mesh]`,
  `machinome[cadquery]`, `machinome[build123d]`, `machinome[step]`,
  `machinome[molejo]`, `machinome[openscad]`, `machinome[solid2]`,
  `machinome[jscad]`, `machinome[stl]` and `machinome[freecad]` and the
  distributions `machinome-engine-brep`, `machinome-engine-mesh`,
  `machinome-node-cadquery`, `machinome-node-build123d`,
  `machinome-node-step`, `machinome-node-molejo`, `machinome-node-openscad`,
  `machinome-node-solid2`, `machinome-node-jscad`, `machinome-node-stl` and
  `machinome-node-freecad` they install

#### Scenario: The FreeCAD node distribution requires the framework and the B-rep engine

- **WHEN** the manifest of `machinome-node-freecad` is read
- **THEN** it requires `machinome~=<version>` and
  `machinome-engine-brep~=<version>` with the framework's version, `numpy`
  and `scipy`, unranged, and names neither `cadquery-ocp`, a FreeCAD
  distribution, `machinome-engine-mesh` nor `machinome[mesh]`

### Requirement: A kernel module refuses an absent kernel at import

Each module that needs a kernel the core does not require — the node
modules `machinome.node.cadquery`, `machinome.node.build123d`,
`machinome.node.step`, `machinome.node.molejo` and `machinome.node.solid2`, the
packages `machinome.node.openscad` and `machinome.node.freecad`, the B-rep
engine `machinome.engine.brep` and the mesh engine `machinome.engine.mesh` —
SHALL
check, when it is imported and before it imports any kernel or another kernel
module, that each kernel it needs can be found. The check SHALL NOT import the
kernel.

When a kernel cannot be found, importing the module SHALL raise one error that
is a `ModuleNotFoundError` whose `name` is the missing kernel's module, and
whose message names what the module provides (its node types, or the B-rep or
the mesh engine), the missing module, and the install line
`pip install "machinome[<extra>]"` of the module's extra. The error SHALL carry
the extra's name as data so a caller can answer by it.

A kernel that is found but fails to import SHALL NOT be reported as absent: its
own import error SHALL be raised where the module imports it.

The check SHALL name the extra by the rule of the module's address, never by a
table in the core: a kernel module added later declares its own check and its
own extra, and no core module gains a row for it.

#### Scenario: An absent kernel is refused by its extra

- **WHEN** `machinome.node.cadquery` is imported in an interpreter where
  `cadquery` cannot be found
- **THEN** a `ModuleNotFoundError` is raised whose `name` is `cadquery` and
  whose message names `CadQueryNode`, `cadquery` and
  `pip install "machinome[cadquery]"`

#### Scenario: Each kernel module names its own extra

- **WHEN** `machinome.node.build123d`, `machinome.node.step`,
  `machinome.node.molejo`, `machinome.engine.brep`, `machinome.engine.mesh`,
  `machinome.node.openscad`, `machinome.node.solid2` and
  `machinome.node.freecad` are each imported with their kernel absent
- **THEN** each refusal names what the module provides and
  `pip install "machinome[build123d]"`, `pip install "machinome[step]"`,
  `pip install "machinome[molejo]"`, `pip install "machinome[brep]"`,
  `pip install "machinome[mesh]"`,
  `pip install "machinome[openscad]"`, `pip install "machinome[solid2]"` and
  `pip install "machinome[freecad]"` respectively, the FreeCAD package's
  naming `FreeCADAssemblyNode`, `FreeCADJoint` and `OCP`

#### Scenario: Checking does not import the kernel

- **WHEN** `machinome.node.cadquery` or `machinome.node.build123d` is imported
  with its kernel installed
- **THEN** `cadquery` and `build123d` are absent from the imported modules
  afterwards

#### Scenario: A broken kernel reports its own failure

- **WHEN** `machinome.node.step` is imported where `cadquery` can be found but
  importing it raises an import error from inside
- **THEN** that import error is raised, not the absent-kernel refusal

#### Scenario: A project with the extra sees no change

- **WHEN** a project using `CadQueryNode`, `StepNode`, `Build123dNode`,
  `MolejoNode`, `Solid2Node` or `OpenScadNode`, or comparing parts on meshes,
  is built and tested with the corresponding extra installed
- **THEN** its results, artifacts and messages are those it produced before
  this change

### Requirement: The core imports no kernel outside its kernel modules

No module of the core SHALL import `cadquery`, `build123d`, `OCP`, `molejo`,
`ocp_gordon`, `manifold3d` or `solid2`, at module top or inside a function,
except the project templates `machinome new` scaffolds a part from, which are
copied into a project and never imported by the framework. No module of the
core SHALL import a node type's module, the OpenSCAD node package or anything
beneath it, or an engine's provider, except those templates. The modules of the
framework's extension packages are not modules of the core: the B-rep and
mesh engines' providers, every node type's module and the OpenSCAD node
package SHALL each live in its own distribution, and SHALL import no kernel
but its own: `OCP` for the B-rep engine, `manifold3d` for the mesh engine,
`build123d` for the build123d module, `cadquery` and `OCP` for the STEP
module, `molejo` for the molejo module, `solid2` for the OpenSCAD package's
`__init__` and writer and for the solid2 module, `OCP` for the FreeCAD
package's adapter, and none for the CadQuery, JSCAD and STL modules, the
OpenSCAD package's other modules, the OpenSCAD viewer's module and the FreeCAD
package's other modules, whose worker imports FreeCAD's own modules and runs
only in FreeCAD's interpreter. A core module
that needs a kernel module's capability SHALL reach it through a seam: a
try-import of the one known module that answers by that module's extra when it
is absent.

The core modules that name a kernel module are exactly: the table of
supported node types, `machinome.node.supported`, from which the node root's
refusals, the CLI's command table, the `import-step` command and
`machinome new` reach a node type's module or its name, and which names no
viewer; the project
templates, each of which is a project's file and names its own node type's
module in the import line it gives the project; and the markings' artwork
seam, naming `machinome.node.build123d`. Among the extension packages,
`machinome.node.step` names `machinome.node.cadquery`, for its render
conversion, `machinome.node.solid2` names `machinome.node.openscad`, whose leaf
base and binary contract it is built over, the OpenSCAD viewer
`machinome.viewer.openscad` names `machinome.node.openscad`, whose writer
and binary contract it draws with, and no other names a kernel module but its
own package. The engines' providers are named by their seams under the
`brep-engine-dependency` and `mesh-engine-dependency` capabilities.

#### Scenario: Scanning the core finds kernels only in their modules

- **WHEN** every module under the core's `machinome/` is scanned for imports
  of `cadquery`, `build123d`, `OCP`, `molejo`, `ocp_gordon`, `manifold3d`
  and `solid2`
- **THEN** they are found only in the templates
  `machinome/manager/templates/project/root/cadquery.py` (`cadquery`) and
  `machinome/manager/templates/project/root/solid2.py` (`solid2`)

#### Scenario: Scanning the extension distributions finds only their kernels

- **WHEN** every module of the engine and node distributions under
  `packages/machinome-*` is scanned for the same imports
- **THEN** `machinome/engine/brep.py` of `machinome-engine-brep` imports
  `OCP` alone, `machinome/engine/mesh.py` of `machinome-engine-mesh`
  `manifold3d` alone, `machinome/node/build123d.py` `build123d` alone,
  `machinome/node/step.py` `cadquery` and `OCP`, `machinome/node/molejo.py`
  `molejo` alone, `machinome/node/openscad/__init__.py`,
  `machinome/node/openscad/writer.py` and `machinome/node/solid2.py` `solid2`
  alone, the CadQuery, JSCAD and STL modules and the OpenSCAD package's other
  modules none, `machinome/node/freecad/adapter.py` of
  `machinome-node-freecad` `OCP` alone and the FreeCAD package's other modules
  none, and each module that imports a kernel calls its extra's
  `require_extra` before any kernel import or kernel module import, the
  OpenSCAD and FreeCAD packages in their `__init__`

#### Scenario: Scanning the core finds the kernel modules named only at the seams

- **WHEN** every module under the core's `machinome/` and every module of the
  extension distributions is scanned for imports or string spellings of
  `machinome.node.cadquery`, `machinome.node.build123d`,
  `machinome.node.step`, `machinome.node.molejo`, `machinome.node.solid2`,
  `machinome.node.openscad` and `machinome.node.freecad`, a name beneath one
  counting as it
- **THEN** they are found only in `machinome/node/supported.py`
  (`machinome.node.openscad`), `machinome/node/markings.py`, the step
  distribution's `machinome/node/step.py` (`machinome.node.cadquery` alone),
  the solid2 distribution's `machinome/node/solid2.py`
  (`machinome.node.openscad` alone), the OpenSCAD viewer's
  `machinome/viewer/openscad/__init__.py` (`machinome.node.openscad`
  alone), the OpenSCAD package's own modules naming
  their package, and the templates
  `machinome/manager/templates/project/root/cadquery.py`
  (`machinome.node.cadquery`) and
  `machinome/manager/templates/project/root/solid2.py`
  (`machinome.node.solid2`), each naming only the modules listed for it, and
  `machinome/cli.py`, `machinome/manager/import_step.py`,
  `machinome/manager/snapshot.py`, `machinome/manager/new.py` and the node
  root name none of them

#### Scenario: The core imports no node type and no engine provider

- **WHEN** every import statement of every module under the core's
  `machinome/` is read for the modules of the node types, the OpenSCAD and
  FreeCAD node packages, `machinome.engine.brep`, `machinome.engine.mesh`,
  and any name beneath one of them
- **THEN** they are found only in the two templates, each importing its own
  node type's class from its module

### Requirement: The engine providers are modules of one engine package that admits portions

The two engine providers SHALL be the modules `machinome.engine.brep` and
`machinome.engine.mesh` of the package `machinome.engine`, each named for the
representation its engine consumes, a boundary representation and a triangle
mesh, and each installed by the extra of the same name. The package's
`__init__` SHALL hold the core's two seams (the `brep-engine-dependency` and
`mesh-engine-dependency` capabilities) and SHALL import neither provider.

Each provider SHALL be shipped by its own distribution as a namespace
portion of the package: `machinome-engine-brep` ships
`machinome/engine/brep.py` and `machinome-engine-mesh` ships
`machinome/engine/mesh.py`, each with no `__init__.py` under `machinome/` or
`machinome/engine/`, and the framework's distribution SHALL ship neither
provider. In the repository each lives at
`packages/<distribution>/machinome/engine/<name>.py`.

The package SHALL extend its module path with every portion of
`machinome.engine` found on the import path that ships no `__init__.py` of its
own, as `machinome` and `machinome.node` do, so the seam resolves a provider
from its own distribution, whether installed from its wheel or editable from
its directory. A directory holding its own `__init__.py`, another copy of the
core, SHALL NOT be admitted.

The former addresses `machinome.exact_engine`, `machinome.mesh_engine`,
`machinome.occt` and `machinome.manifold`, and the extras `occt` and
`manifold`, SHALL NOT exist, and nothing SHALL alias them.

#### Scenario: The package imports no provider

- **WHEN** a fresh interpreter imports `machinome.engine`
- **THEN** neither `machinome.engine.brep`, `machinome.engine.mesh`, `OCP` nor
  `manifold3d` is among the imported modules

#### Scenario: A provider portion resolves from another directory

- **WHEN** a directory on the import path holds `machinome/engine/probe.py`
  and no `__init__.py` in `machinome/` or `machinome/engine/`
- **THEN** `machinome.engine.probe` imports from that directory

#### Scenario: Another copy of the core is not admitted

- **WHEN** a directory on the import path holds `machinome/__init__.py`,
  `machinome/engine/__init__.py` and `machinome/engine/probe.py`
- **THEN** importing `machinome.engine.probe` raises `ModuleNotFoundError`

#### Scenario: Each provider resolves from its own distribution in the workspace

- **WHEN** the repository's workspace is synced and `machinome.engine.brep`
  and `machinome.engine.mesh` are imported
- **THEN** their files are `packages/machinome-engine-brep/machinome/engine/brep.py`
  and `packages/machinome-engine-mesh/machinome/engine/mesh.py`, the seams
  return those modules, and the framework's `machinome/engine/` holds only
  `__init__.py`

#### Scenario: Each provider resolves from its installed wheel

- **WHEN** the framework's wheel is installed with its `brep` and `mesh`
  extras, which install the two engine wheels
- **THEN** each seam returns its provider, whose file is listed in its own
  distribution's installed files, which list no `__init__.py`, and the
  framework's wheel holds neither provider

#### Scenario: The former addresses are gone

- **WHEN** `machinome.exact_engine`, `machinome.mesh_engine`,
  `machinome.occt` or `machinome.manifold` is imported
- **THEN** each raises `ModuleNotFoundError`, and the package metadata
  declares neither an `occt` nor a `manifold` extra

### Requirement: An absent node package is refused by its extra at its import

When no installed distribution ships the module of a node type of the table of
supported node types, importing `machinome.node.<key>` SHALL raise the same
refusal `machinome.node.supported.load(key)` raises: a `ModuleNotFoundError`
whose `name` is `machinome.node.<key>`, which carries `<key>` as its extra and
whose message names the node type, its classes, the module and the install
line `pip install "machinome[<key>]"`. The refusal SHALL be raised at the
module's import, so a project's import line, `from machinome.node import
<key>`, an attribute read of `machinome.node`, `hasattr`, the CLI and every
seam that imports the module by name meet it alike. Importing a module beneath
an absent node package, such as `machinome.node.openscad.writer`, and
importing a node type built over one, such as `machinome.node.solid2` without
`machinome-node-openscad`, SHALL raise the absent package's refusal.

The refusal SHALL be the import system's last resort: a module installed from
the framework's directory, from a portion's directory or from a wheel SHALL be
found and imported as it is, and a module whose kernel is absent SHALL raise
its own refusal under the requirement "A kernel module refuses an absent
kernel at import". Importing `machinome.node` SHALL import neither a node
type's module nor the table to make this so.

#### Scenario: A project's import of an absent node package names the extra

- **WHEN** `from machinome.node.step import StepNode` runs where no installed
  distribution ships `machinome.node.step`
- **THEN** it raises a `ModuleNotFoundError` whose `name` is
  `machinome.node.step`, whose extra is `step`, and whose message is `the
  step node type (StepNode) needs machinome.node.step, which is not
  installed; install it with 'pip install "machinome[step]"'`

#### Scenario: The node root's submodule read raises the same refusal

- **WHEN** `from machinome.node import step` runs, or `hasattr` is asked of
  `machinome.node` for `step`, where no installed distribution ships it
- **THEN** each raises that refusal rather than answering with a missing
  attribute or `False`

#### Scenario: An installed package is imported as it is

- **WHEN** `machinome-node-step` is installed and `machinome.node.step` is
  imported
- **THEN** the module is the distribution's file, and no refusal is raised

#### Scenario: Other node packages are unaffected by one absent package

- **WHEN** `machinome-node-step` is absent and `machinome-node-cadquery` is
  installed
- **THEN** `machinome.node.cadquery` imports from its distribution

#### Scenario: Each node package over no B-rep engine is refused by its extra

- **WHEN** `machinome-node-openscad`, `machinome-node-solid2`,
  `machinome-node-jscad` or `machinome-node-stl` is absent and its module is
  imported, its class imported from it, it is imported from `machinome.node`,
  or `hasattr` is asked of `machinome.node` for it
- **THEN** each raises the refusal naming that node type, its class, its
  module and `pip install "machinome[<key>]"`, its extra being the key

#### Scenario: A module beneath an absent node package names the package's extra

- **WHEN** `machinome-node-openscad` is absent and
  `machinome.node.openscad.writer` is imported, or the OpenSCAD viewer
  `machinome.viewer.openscad` is resolved through the seam
- **THEN** each raises the refusal `the openscad node type (OpenScadNode)
  needs machinome.node.openscad, which is not installed; install it with
  'pip install "machinome[openscad]"'`, whose `name` is
  `machinome.node.openscad`

#### Scenario: A node type over an absent node package names that package's extra

- **WHEN** `machinome-node-openscad` is absent and `machinome-node-solid2` and
  SolidPython are installed, and `from machinome.node.solid2 import
  Solid2Node` runs
- **THEN** it raises the OpenSCAD package's refusal, naming
  `machinome.node.openscad` and `pip install "machinome[openscad]"`, while
  `machinome.node.stl` still imports

#### Scenario: The FreeCAD node package is refused by its extra

- **WHEN** `machinome-node-freecad` is absent and `machinome.node.freecad` is
  imported, `FreeCADAssemblyNode` is imported from it, it is imported from
  `machinome.node`, or `hasattr` is asked of `machinome.node` for it
- **THEN** each raises the refusal `the freecad node type
  (FreeCADAssemblyNode, FreeCADJoint) needs machinome.node.freecad, which is
  not installed; install it with 'pip install "machinome[freecad]"'`, whose
  `name` is `machinome.node.freecad` and whose extra is `freecad`

### Requirement: The OpenSCAD viewer is installed by its extra and by the OpenSCAD extras

The framework SHALL declare the extra `viewer-openscad`, requiring the
distribution `machinome-viewer-openscad` with the compatible-release pin
`~=<version>`, the version being the framework's own. That distribution SHALL
ship the package `machinome.viewer.openscad` alone and SHALL require the
framework and `machinome-node-openscad`, each with the same pin, and no
third-party package of its own. The `openscad` and `solid2` extras SHALL each
also require `machinome-viewer-openscad` with that pin, beside their node
distributions, so an installation that can build an OpenSCAD part can also
draw a still through the OpenSCAD viewer; `all` installs it through `openscad`.
No other extra SHALL install it.

#### Scenario: The extras that install the OpenSCAD viewer

- **WHEN** the core's manifest is read
- **THEN** `viewer-openscad` lists `machinome-viewer-openscad~=<version>`
  alone, `openscad` lists `machinome-node-openscad~=<version>` and
  `machinome-viewer-openscad~=<version>`, and `solid2` lists
  `machinome-node-solid2~=<version>` and `machinome-viewer-openscad~=<version>`

#### Scenario: The OpenSCAD extra keeps its still

- **WHEN** `pip install "machinome[openscad]"` resolves the framework's
  distributions and a user runs `machinome snapshot` on a project of
  `OpenScadNode` parts
- **THEN** the OpenSCAD viewer is installed and draws the image

#### Scenario: A model of other parts asks for the OpenSCAD viewer

- **WHEN** an installation holds `machinome[cadquery]` alone and a user runs
  `machinome snapshot`
- **THEN** the command fails naming the `viewer-openscad` extra and `--viewer
  web`, and writes no image

