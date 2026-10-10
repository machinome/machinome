## MODIFIED Requirements

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
- `openscad`, for the package `machinome.node.openscad`: `solidpython2`;
- `solid2`, for `machinome.node.solid2`: the `openscad` extra;
- `jscad`, for `machinome.node.jscad`: nothing, because the module needs no
  Python package the core does not require (its renderer, the `jscad`
  command, is a Node program no pip extra installs);
- `stl`, for `machinome.node.stl`: nothing, because the module reads with
  trimesh, a required dependency;
- `all`, every extra above.

The `brep`, `mesh`, `cadquery`, `build123d`, `step` and `molejo` extras SHALL
require their distributions with the compatible-release pin `~=<version>`,
the version being the framework's own, and each of those distributions SHALL
require the framework with the same pin and state its kernel:
`machinome-engine-brep` the OCCT binding `cadquery-ocp>=7.8.1,<7.9`, stated
there and nowhere else; `machinome-engine-mesh` `manifold3d`, unranged; each
node distribution its kernel and `machinome-engine-brep~=<version>`, and
`machinome-node-step` also `machinome-node-cadquery~=<version>`, whose module
it imports. A distribution of the set SHALL declare every third-party package
its module imports directly, unranged when the framework pins the range.

Every node type of the table of supported node types SHALL have the extra of
its key, so the install line a refusal or a manifest names for a node type,
`machinome[<key>]`, is always one pip resolves; an extra that installs nothing
today keeps a manifest naming it valid when the node type's package is cut.
`machinome.node.jscad` and `machinome.node.stl` SHALL check no kernel and
refuse nothing at import.

Every kernel requirement SHALL keep the version range the framework required
before it became an extra, and a kernel named by two manifests SHALL carry the
same range in both, so installing several extras resolves one OCCT binding.
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
  `openscad`, `solid2`, `jscad`, `stl` and `all` are declared, `brep`
  requires `machinome-engine-brep~=<version>`, `mesh`
  `machinome-engine-mesh~=<version>`, and each of `cadquery`, `build123d`,
  `step` and `molejo` `machinome-node-<key>~=<version>`, with the framework's
  version and nothing else, `openscad` installs `solidpython2` and `solid2`
  includes `openscad`, `jscad` and `stl` list no requirement, `all` includes
  every one of them, every key of the table of supported node types is an
  extra, and the development extra includes `all`

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

#### Scenario: The ranges are the ones required before

- **WHEN** the extras' and the distributions' requirements are read
- **THEN** CadQuery is `==2.7.*` wherever it is named, build123d `==0.10.*`,
  `ocp-gordon` `>=0.2.2,<0.3`, molejo `molejo[brep]==0.2.*`, the OCCT
  binding `>=7.8.1,<7.9` and named only in `machinome-engine-brep`'s
  manifest, SolidPython `solidpython2==2.1.*`, and `manifold3d` carries no
  range, as when it was required

#### Scenario: Continuous integration installs every kernel

- **WHEN** the CI workflow and the repository's lock are read
- **THEN** the `lint`, `test` and `browser-snapshot` jobs each run
  `uv sync --locked` at the repository root, and the lock holds every
  concrete requirement of the `all` extra, `manifold3d`, `cadquery-ocp`, both
  engine distributions and the four node distributions among them

#### Scenario: The installation page names the extension distributions

- **WHEN** the manual's installation page is read
- **THEN** it names `machinome[brep]`, `machinome[mesh]`,
  `machinome[cadquery]`, `machinome[build123d]`, `machinome[step]` and
  `machinome[molejo]` and the distributions `machinome-engine-brep`,
  `machinome-engine-mesh`, `machinome-node-cadquery`,
  `machinome-node-build123d`, `machinome-node-step` and
  `machinome-node-molejo` they install

### Requirement: The core imports no kernel outside its kernel modules

No module of the core other than the node modules and the package named
above SHALL import `cadquery`, `build123d`, `OCP`, `molejo`, `ocp_gordon`,
`manifold3d` or `solid2`, at module top or inside a function, except the
project templates `machinome new` scaffolds a part from, which are copied
into a project and never imported by the framework. The modules of the
framework's extension packages are not modules of the core: the B-rep and
mesh engines' providers and the node modules `machinome.node.cadquery`,
`machinome.node.build123d`, `machinome.node.step` and `machinome.node.molejo`
SHALL each live in its own distribution, and SHALL import no kernel but its
own: `OCP` for the B-rep engine, `manifold3d` for the mesh engine, `build123d`
for the build123d module, `cadquery` and `OCP` for the STEP module, `molejo`
for the molejo module, and none for the CadQuery module, whose project's
`render()` imports CadQuery. A core module that needs a kernel module's
capability SHALL reach it through a seam: a try-import of the one known module
that answers by that module's extra when it is absent.

The core modules that name a kernel module are exactly: the table of
supported node types, `machinome.node.supported`, from which the node root's
refusals, the CLI's command table, the `import-step` command, the
snapshot command and `machinome new` reach a node type's module or its name;
the project templates, each of which is a project's file and names its own
node type's module in the import line it gives the project; the markings'
artwork seam, naming `machinome.node.build123d`; and `machinome.node.solid2`,
which uses the package `machinome.node.openscad` it is built over. Among the
extension packages, `machinome.node.step` names `machinome.node.cadquery`, for
its render conversion, and no other kernel module. The engines' providers are
named by their seams under the `brep-engine-dependency` and
`mesh-engine-dependency` capabilities.

#### Scenario: Scanning the core finds kernels only in their modules

- **WHEN** every module under the core's `machinome/` is scanned for imports
  of `cadquery`, `build123d`, `OCP`, `molejo`, `ocp_gordon`, `manifold3d`
  and `solid2`
- **THEN** they are found only in `machinome/node/openscad/` and
  `machinome/node/solid2.py` (`solid2`), and the templates
  `machinome/manager/templates/project/root/cadquery.py` (`cadquery`) and
  `machinome/manager/templates/project/root/solid2.py` (`solid2`)

#### Scenario: Scanning the extension distributions finds only their kernels

- **WHEN** every module of the engine and node distributions under
  `packages/machinome-*` is scanned for the same imports
- **THEN** `machinome/engine/brep.py` of `machinome-engine-brep` imports
  `OCP` alone, `machinome/engine/mesh.py` of `machinome-engine-mesh`
  `manifold3d` alone, `machinome/node/build123d.py` `build123d` alone,
  `machinome/node/step.py` `cadquery` and `OCP`, `machinome/node/molejo.py`
  `molejo` alone, `machinome/node/cadquery.py` none, and each calls its
  extra's `require_extra` before any kernel import or kernel module import

#### Scenario: Scanning the core finds the kernel modules named only at the seams

- **WHEN** every module under the core's `machinome/` and every module of the
  extension distributions is scanned for imports or string spellings of
  `machinome.node.cadquery`, `machinome.node.build123d`,
  `machinome.node.step`, `machinome.node.molejo`, `machinome.node.solid2` and
  `machinome.node.openscad`
- **THEN** they are found only in `machinome/node/supported.py`,
  `machinome/node/markings.py`, `machinome/node/solid2.py`, the step
  distribution's `machinome/node/step.py` (`machinome.node.cadquery` alone)
  and the templates `machinome/manager/templates/project/root/cadquery.py`
  (`machinome.node.cadquery`) and
  `machinome/manager/templates/project/root/solid2.py`
  (`machinome.node.solid2`), each naming only the modules listed for it, and
  `machinome/cli.py`, `machinome/manager/import_step.py`,
  `machinome/manager/snapshot.py`, `machinome/manager/new.py` and the node
  root name none of them

## ADDED Requirements

### Requirement: An absent node package is refused by its extra at its import

When no installed distribution ships the module of a node type of the table of
supported node types, importing `machinome.node.<key>` SHALL raise the same
refusal `machinome.node.supported.load(key)` raises: a `ModuleNotFoundError`
whose `name` is `machinome.node.<key>`, which carries `<key>` as its extra and
whose message names the node type, its classes, the module and the install
line `pip install "machinome[<key>]"`. The refusal SHALL be raised at the
module's import, so a project's import line, `from machinome.node import
<key>`, an attribute read of `machinome.node`, `hasattr`, the CLI and every
seam that imports the module by name meet it alike.

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
