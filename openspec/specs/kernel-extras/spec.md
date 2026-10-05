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
`manifold3d` nor `solidpython2`. Each kernel SHALL be installed by an extra named by the last
component of the address of the module that needs it:

- `brep`, for the B-rep engine `machinome.engine.brep`: the OCCT binding;
- `mesh`, for the mesh engine `machinome.engine.mesh`: `manifold3d`;
- `cadquery`, for `machinome.node.cadquery`: CadQuery and the `brep` extra;
- `build123d`, for `machinome.node.build123d`: build123d, its `ocp-gordon`
  bound and the `brep` extra;
- `step`, for `machinome.node.step`: CadQuery and the `brep` extra;
- `molejo`, for `machinome.node.molejo`: `molejo[brep]` and the `brep` extra;
- `openscad`, for the package `machinome.node.openscad`: `solidpython2`;
- `solid2`, for `machinome.node.solid2`: the `openscad` extra;
- `jscad`, for `machinome.node.jscad`: nothing, because the module needs no
  Python package the core does not require (its renderer, the `jscad`
  command, is a Node program no pip extra installs);
- `stl`, for `machinome.node.stl`: nothing, because the module reads with
  trimesh, a required dependency;
- `all`, every extra above.

Every node type of the table of supported node types SHALL have the extra of
its key, so the install line a refusal or a manifest names for a node type,
`machinome[<key>]`, is always one pip resolves; an extra that installs nothing
today keeps a manifest naming it valid when the node type's package is cut.
`machinome.node.jscad` and `machinome.node.stl` SHALL check no kernel and
refuse nothing at import.

Every kernel requirement SHALL keep the version range the framework required
before it became an extra, and a kernel named by two extras SHALL carry the
same range in both, so installing several extras resolves one OCCT binding.
No node extra SHALL include `mesh`: a B-rep project needs the mesh engine
only for a mesh question, which it may never ask.

`watchdog`, `trimesh`, `numpy`, `scipy`, `shapely`, `rtree` and the other
dependencies the core imports SHALL stay required.

The extra that installs the development tools SHALL include `all`, and the
continuous integration and the tox environments SHALL install every kernel
extra, so the framework's own suite runs every kernel.

#### Scenario: A bare install carries no kernel

- **WHEN** the framework's package metadata is read
- **THEN** its required dependencies name none of `cadquery`, `build123d`,
  `ocp-gordon`, `molejo`, `cadquery-ocp`, `manifold3d` or `solidpython2`, and
  they still name `watchdog` and `trimesh`

#### Scenario: Each extra installs what its module needs

- **WHEN** the package metadata's extras are read
- **THEN** `brep`, `mesh`, `cadquery`, `build123d`, `step`, `molejo`,
  `openscad`, `solid2`, `jscad`, `stl` and `all` are declared, each of
  `cadquery`, `build123d`, `step` and `molejo` includes the `brep` extra and
  none includes `mesh`, `openscad` installs `solidpython2` and `solid2`
  includes `openscad`, `jscad` and `stl` list no requirement, `all` includes
  every one of them, every key of the table of supported node types is an
  extra, and the development extra includes `all`

#### Scenario: The ranges are the ones required before

- **WHEN** the extras' requirements are read
- **THEN** CadQuery is `==2.7.*` wherever it is named, build123d `==0.10.*`,
  `ocp-gordon` `>=0.2.2,<0.3`, molejo `molejo[brep]==0.2.*`, the OCCT
  binding `>=7.8.1,<7.9`, SolidPython `solidpython2==2.1.*`, and `manifold3d`
  carries no range, as when it was required

#### Scenario: Continuous integration installs every kernel

- **WHEN** the requirements files the CI jobs install are read
- **THEN** they name every concrete requirement of the `all` extra, `manifold3d`
  among them

### Requirement: A kernel module refuses an absent kernel at import

Each module that needs a kernel the core does not require — the node
modules `machinome.node.cadquery`, `machinome.node.build123d`,
`machinome.node.step`, `machinome.node.molejo` and `machinome.node.solid2`, the
package `machinome.node.openscad`, the B-rep engine `machinome.engine.brep` and
the mesh engine `machinome.engine.mesh` — SHALL
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
  `machinome.node.openscad` and `machinome.node.solid2` are each imported
  with their kernel absent
- **THEN** each refusal names what the module provides and
  `pip install "machinome[build123d]"`, `pip install "machinome[step]"`,
  `pip install "machinome[molejo]"`, `pip install "machinome[brep]"`,
  `pip install "machinome[mesh]"`,
  `pip install "machinome[openscad]"` and `pip install "machinome[solid2]"`
  respectively

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

No module of the core other than the node modules and the package named
above and the B-rep and mesh engines' provider modules SHALL import `cadquery`,
`build123d`, `OCP`, `molejo`, `ocp_gordon`, `manifold3d` or `solid2`, at module
top or inside a function, except the project templates `machinome new`
scaffolds a part from, which are copied into a project and never imported by
the framework. A
core module that needs a kernel module's capability SHALL reach it through a
seam: a try-import of the one known module that answers by that module's extra
when it is absent.

The core modules that name a kernel module are exactly: the table of
supported node types, `machinome.node.supported`, from which the node root's
refusals, the CLI's command table, the `import-step` command, the
snapshot command and `machinome new` reach a node type's module or its name;
the project templates, each of which is a project's file and names its own
node type's module in the import line it gives the project; the markings'
artwork seam, naming `machinome.node.build123d`; `machinome.node.step`, which
uses `machinome.node.cadquery` for its render conversion; and
`machinome.node.solid2`, which uses the package `machinome.node.openscad` it is
built over. The
engines' providers are named by their seams under the `brep-engine-dependency`
and `mesh-engine-dependency` capabilities.

#### Scenario: Scanning the core finds kernels only in their modules

- **WHEN** every module under `machinome/` is scanned for imports of
  `cadquery`, `build123d`, `OCP`, `molejo`, `ocp_gordon`, `manifold3d` and
  `solid2`
- **THEN** they are found only in `machinome/engine/brep.py`, `machinome/engine/mesh.py`,
  `machinome/node/step.py` (`cadquery`, `OCP`),
  `machinome/node/build123d.py` (`build123d`),
  `machinome/node/molejo.py` (`molejo`), `machinome/node/openscad/` and
  `machinome/node/solid2.py` (`solid2`), and the templates
  `machinome/manager/templates/project/root/cadquery.py` (`cadquery`) and
  `machinome/manager/templates/project/root/solid2.py` (`solid2`)

#### Scenario: Scanning the core finds the kernel modules named only at the seams

- **WHEN** every module under `machinome/` is scanned for imports or string
  spellings of `machinome.node.cadquery`, `machinome.node.build123d`,
  `machinome.node.step`, `machinome.node.molejo`, `machinome.node.solid2` and
  `machinome.node.openscad`
- **THEN** they are found only in `machinome/node/supported.py`,
  `machinome/node/markings.py`, `machinome/node/step.py`,
  `machinome/node/solid2.py` and the templates
  `machinome/manager/templates/project/root/cadquery.py`
  (`machinome.node.cadquery`) and
  `machinome/manager/templates/project/root/solid2.py`
  (`machinome.node.solid2`), each naming only the modules listed for it, and
  `machinome/cli.py`, `machinome/manager/import_step.py`,
  `machinome/manager/snapshot.py`, `machinome/manager/new.py` and the node
  root name none of them

### Requirement: The engine providers are modules of one engine package that admits portions

The two engine providers SHALL be the modules `machinome.engine.brep` and
`machinome.engine.mesh` of the package `machinome.engine`, each named for the
representation its engine consumes, a boundary representation and a triangle
mesh, and each installed by the extra of the same name. The package's
`__init__` SHALL hold the core's two seams (the `brep-engine-dependency` and
`mesh-engine-dependency` capabilities) and SHALL import neither provider.

The package SHALL extend its module path with every portion of
`machinome.engine` found on the import path that ships no `__init__.py` of its
own, as `machinome` and `machinome.node` do, so a distribution cut from the
core later can install `machinome/engine/brep.py` or `machinome/engine/mesh.py`
alone and be resolved by the seam. A directory holding its own `__init__.py`,
another copy of the core, SHALL NOT be admitted.

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

#### Scenario: The former addresses are gone

- **WHEN** `machinome.exact_engine`, `machinome.mesh_engine`,
  `machinome.occt` or `machinome.manifold` is imported
- **THEN** each raises `ModuleNotFoundError`, and the package metadata
  declares neither an `occt` nor a `manifold` extra

