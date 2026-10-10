## MODIFIED Requirements

### Requirement: The CAD kernels are extras, not required dependencies

The framework's required dependencies SHALL NOT include a CAD kernel: neither
`cadquery`, `build123d`, `ocp-gordon`, `molejo`, `cadquery-ocp`,
`manifold3d` nor `solidpython2`, nor an engine distribution. Each kernel
SHALL be installed by an extra named by the last component of the address of
the module that needs it:

- `brep`, for the B-rep engine `machinome.engine.brep`: the distribution
  `machinome-engine-brep`, which requires the OCCT binding;
- `mesh`, for the mesh engine `machinome.engine.mesh`: the distribution
  `machinome-engine-mesh`, which requires `manifold3d`;
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

The `brep` and `mesh` extras SHALL require their distributions with the
compatible-release pin `~=<version>`, the version being the framework's own,
and each engine distribution SHALL require the framework with the same pin
and state its kernel: `machinome-engine-brep` the OCCT binding
`cadquery-ocp>=7.8.1,<7.9`, stated there and nowhere else, and
`machinome-engine-mesh` `manifold3d`, unranged.

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
continuous integration SHALL install the repository's workspace from its
lock, whose default group installs that extra, so the framework's own suite
runs every kernel and both engines.

The installation page of the manual SHALL name, for the `brep` and `mesh`
extras, the distribution each installs.

#### Scenario: A bare install carries no kernel

- **WHEN** the framework's package metadata is read
- **THEN** its required dependencies name none of `cadquery`, `build123d`,
  `ocp-gordon`, `molejo`, `cadquery-ocp`, `manifold3d`, `solidpython2`,
  `machinome-engine-brep` or `machinome-engine-mesh`, and they still name
  `watchdog` and `trimesh`

#### Scenario: Each extra installs what its module needs

- **WHEN** the package metadata's extras are read
- **THEN** `brep`, `mesh`, `cadquery`, `build123d`, `step`, `molejo`,
  `openscad`, `solid2`, `jscad`, `stl` and `all` are declared, `brep`
  requires `machinome-engine-brep~=<version>` and `mesh`
  `machinome-engine-mesh~=<version>` with the framework's version, each of
  `cadquery`, `build123d`, `step` and `molejo` includes the `brep` extra and
  none includes `mesh`, `openscad` installs `solidpython2` and `solid2`
  includes `openscad`, `jscad` and `stl` list no requirement, `all` includes
  every one of them, every key of the table of supported node types is an
  extra, and the development extra includes `all`

#### Scenario: Each engine distribution requires the framework and its kernel

- **WHEN** the manifests of `machinome-engine-brep` and
  `machinome-engine-mesh` are read
- **THEN** each requires `machinome~=<version>` with the framework's
  version and `numpy`, the B-rep engine `cadquery-ocp>=7.8.1,<7.9` and the
  mesh engine `manifold3d`

#### Scenario: The ranges are the ones required before

- **WHEN** the extras' and the engine distributions' requirements are read
- **THEN** CadQuery is `==2.7.*` wherever it is named, build123d `==0.10.*`,
  `ocp-gordon` `>=0.2.2,<0.3`, molejo `molejo[brep]==0.2.*`, the OCCT
  binding `>=7.8.1,<7.9` and named only in `machinome-engine-brep`'s
  manifest, SolidPython `solidpython2==2.1.*`, and `manifold3d` carries no
  range, as when it was required

#### Scenario: Continuous integration installs every kernel

- **WHEN** the CI workflow and the repository's lock are read
- **THEN** the `lint`, `test` and `browser-snapshot` jobs each run
  `uv sync --locked` at the repository root, and the lock holds every
  concrete requirement of the `all` extra, `manifold3d`, `cadquery-ocp`,
  `machinome-engine-brep` and `machinome-engine-mesh` among them

#### Scenario: The installation page names the engine distributions

- **WHEN** the manual's installation page is read
- **THEN** it names `machinome[brep]` and `machinome[mesh]` and the
  distributions `machinome-engine-brep` and `machinome-engine-mesh` they
  install

### Requirement: The core imports no kernel outside its kernel modules

No module of the core other than the node modules and the package named
above SHALL import `cadquery`, `build123d`, `OCP`, `molejo`, `ocp_gordon`,
`manifold3d` or `solid2`, at module top or inside a function, except the
project templates `machinome new` scaffolds a part from, which are copied
into a project and never imported by the framework. The B-rep and mesh
engines' provider modules are not modules of the core: each SHALL live in
its own distribution, and SHALL import only its own kernel, `OCP` for the
B-rep engine and `manifold3d` for the mesh engine. A core module that needs
a kernel module's capability SHALL reach it through a seam: a try-import of
the one known module that answers by that module's extra when it is absent.

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

- **WHEN** every module under the core's `machinome/` is scanned for imports
  of `cadquery`, `build123d`, `OCP`, `molejo`, `ocp_gordon`, `manifold3d`
  and `solid2`
- **THEN** they are found only in `machinome/node/step.py` (`cadquery`,
  `OCP`), `machinome/node/build123d.py` (`build123d`),
  `machinome/node/molejo.py` (`molejo`), `machinome/node/openscad/` and
  `machinome/node/solid2.py` (`solid2`), and the templates
  `machinome/manager/templates/project/root/cadquery.py` (`cadquery`) and
  `machinome/manager/templates/project/root/solid2.py` (`solid2`)

#### Scenario: Scanning the engine distributions finds only their kernels

- **WHEN** every module of `machinome-engine-brep` and
  `machinome-engine-mesh` is scanned for the same imports
- **THEN** `machinome/engine/brep.py` of the first imports `OCP` alone and
  `machinome/engine/mesh.py` of the second `manifold3d` alone, and each
  calls its extra's `require_extra` before any kernel import

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
