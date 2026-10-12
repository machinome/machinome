## MODIFIED Requirements

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

## ADDED Requirements

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
