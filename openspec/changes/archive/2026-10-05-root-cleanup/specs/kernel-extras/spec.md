## MODIFIED Requirements

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
