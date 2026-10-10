## ADDED Requirements

### Requirement: The CAD kernels are extras, not required dependencies

The framework's required dependencies SHALL NOT include a CAD kernel: neither
`cadquery`, `build123d`, `ocp-gordon`, `molejo` nor `cadquery-ocp`. Each kernel
SHALL be installed by an extra named by the last component of the address of
the module that needs it:

- `occt`, for the exact engine `machinome.occt.engine`: the OCCT binding;
- `cadquery`, for `machinome.node.cadquery`: CadQuery and the `occt` extra;
- `build123d`, for `machinome.node.build123d`: build123d, its `ocp-gordon`
  bound and the `occt` extra;
- `step`, for `machinome.node.step`: CadQuery and the `occt` extra;
- `molejo`, for `machinome.node.molejo`: `molejo[brep]` and the `occt` extra;
- `all`, every extra above.

Every kernel requirement SHALL keep the version range the framework required
before this change, and a kernel named by two extras SHALL carry the same range
in both, so installing several extras resolves one OCCT binding.

`manifold3d`, `watchdog`, `trimesh`, `numpy`, `scipy`, `shapely`, `rtree`,
`solidpython2` and the other dependencies the core imports SHALL stay
required.

The extra that installs the development tools SHALL include `all`, and the
continuous integration and the tox environments SHALL install every kernel
extra, so the framework's own suite runs every kernel.

#### Scenario: A bare install carries no kernel

- **WHEN** the framework's package metadata is read
- **THEN** its required dependencies name none of `cadquery`, `build123d`,
  `ocp-gordon`, `molejo` or `cadquery-ocp`, and they still name `manifold3d`
  and `watchdog`

#### Scenario: Each extra installs what its module needs

- **WHEN** the package metadata's extras are read
- **THEN** `occt`, `cadquery`, `build123d`, `step`, `molejo` and `all` are
  declared, each of `cadquery`, `build123d`, `step` and `molejo` includes the
  `occt` extra, `all` includes every one of them, and the development extra
  includes `all`

#### Scenario: The ranges are the ones required before

- **WHEN** the extras' requirements are read
- **THEN** CadQuery is `==2.7.*` wherever it is named, build123d `==0.10.*`,
  `ocp-gordon` `>=0.2.2,<0.3`, molejo `molejo[brep]==0.2.*` and the OCCT
  binding `>=7.8.1,<7.9`

#### Scenario: Continuous integration installs every kernel

- **WHEN** the requirements files the CI jobs install are read
- **THEN** they name every concrete requirement of the `all` extra

### Requirement: A kernel module refuses an absent kernel at import

Each module that needs a kernel the core does not require — the four node
modules `machinome.node.cadquery`, `machinome.node.build123d`,
`machinome.node.step` and `machinome.node.molejo`, and the exact engine
`machinome.occt.engine` — SHALL check, when it is imported and before it
imports any kernel or another kernel module, that each kernel it needs can be
found. The check SHALL NOT import the kernel.

When a kernel cannot be found, importing the module SHALL raise one error that
is a `ModuleNotFoundError` whose `name` is the missing kernel's module, and
whose message names what the module provides (its node types, or the exact
engine), the missing module, and the install line
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

- **WHEN** `machinome.node.build123d`, `machinome.node.step` and
  `machinome.node.molejo` are each imported with their kernel absent
- **THEN** each refusal names the module's node types and
  `pip install "machinome[build123d]"`, `pip install "machinome[step]"` and
  `pip install "machinome[molejo]"` respectively

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

- **WHEN** a project using `CadQueryNode`, `StepNode`, `Build123dNode` or
  `MolejoNode` is built and tested with the corresponding extra installed
- **THEN** its results, artifacts and messages are those it produced before
  this change

### Requirement: The core imports no kernel outside its kernel modules

No module of the core other than the four node modules named above and the
exact engine's package SHALL import `cadquery`, `build123d`, `OCP`, `molejo`
or `ocp_gordon`, at module top or inside a function. A core module that needs
a kernel module's capability SHALL reach it through a seam: a try-import of the
one known module that answers by that module's extra when it is absent.

The core modules that name a kernel module are exactly: the node root's export
table, whose targets serve the root spellings until the root cleanup; the
markings' artwork seam, naming `machinome.node.build123d`; the CLI's command
table, naming `machinome.node.step`; the `import-step` command's
implementation, which uses `machinome.node.step`; and `machinome.node.step`
itself, which uses `machinome.node.cadquery` for its render conversion.

#### Scenario: Scanning the core finds kernels only in their modules

- **WHEN** every module under `machinome/` is scanned for imports of
  `cadquery`, `build123d`, `OCP`, `molejo` and `ocp_gordon`
- **THEN** they are found only in `machinome/occt/`,
  `machinome/node/step.py` (`cadquery`, `OCP`),
  `machinome/node/build123d.py` (`build123d`) and
  `machinome/node/molejo.py` (`molejo`)

#### Scenario: Scanning the core finds the kernel modules named only at the seams

- **WHEN** every module under `machinome/` is scanned for imports or string
  spellings of `machinome.node.cadquery`, `machinome.node.build123d`,
  `machinome.node.step` and `machinome.node.molejo`
- **THEN** they are found only in the node root, `machinome/node/markings.py`,
  `machinome/cli.py`, `machinome/manager/import_step.py` and
  `machinome/node/step.py`, each naming only the modules listed for it
