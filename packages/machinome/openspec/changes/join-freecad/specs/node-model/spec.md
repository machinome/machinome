## MODIFIED Requirements

### Requirement: Each leaf type is one module under the node package

Each leaf type the framework supports SHALL be defined at one address directly
under `machinome.node`, named for its technology, and imported from there: a
module,
or, for the OpenSCAD node family, the package `machinome.node.openscad`, whose
`__init__` defines the node type and whose other modules are its machinery
under the `openscad-node` capability, and, for the FreeCAD node type, the
package `machinome.node.freecad`, whose node is a whole native assembly rather
than a leaf, under the `native-freecad-assembly` capability. Which node types exist, with the class
names each node type's module defines for a project to import, SHALL be stated
once, in the table of supported node types `machinome.node.supported`:

| module | defines |
|---|---|
| `machinome.node.cadquery` | `CadQueryNode` |
| `machinome.node.build123d` | `Build123dNode`, `Build123dSheetNode`, and the reducer of `Svg` artwork |
| `machinome.node.step` | `StepNode`, `StepAssembly`, `solids_from_faces`, `cached_document` |
| `machinome.node.molejo` | `MolejoNode` |
| `machinome.node.solid2` | `Solid2Node` |
| `machinome.node.openscad` (a package) | `OpenScadNode` |
| `machinome.node.jscad` | `JScadNode` |
| `machinome.node.stl` | `StlNode` |
| `machinome.node.freecad` (a package) | `FreeCADAssemblyNode`, `FreeCADJoint` |

Each of those classes SHALL be imported from its node type's module and from
nowhere else: the node root resolves none of them, and refuses each naming its
module, under the requirement "The node package's root exports nothing".

Every node type's module SHALL be shipped by its own distribution,
`machinome-node-<key>`, as a namespace portion of `machinome.node` with no
`__init__.py` under `machinome/` or `machinome/node/`: a module at
`machinome/node/<key>.py`, or, for the OpenSCAD node family and the FreeCAD
node type, the package directory `machinome/node/openscad/` or
`machinome/node/freecad/` with its own `__init__.py`. The framework's
distribution SHALL ship none of them, so its `machinome/node/` holds only the
node base and its machinery, the root's refusals and the table of supported
node types; their address, their classes and their behaviour SHALL be those
they had in the framework's distribution, and the FreeCAD node type's, which
joined the repository from a repository of its own, those it had there under
the module `machinome_freecad`, whose name it does not keep. In the repository each lives at
`packages/machinome-node-<key>/machinome/node/<key>.py`, the OpenSCAD package
at `packages/machinome-node-openscad/machinome/node/openscad/` and the FreeCAD
package at `packages/machinome-node-freecad/machinome/node/freecad/`.

The package `machinome.node.adapters` SHALL hold no leaf. Importing it, or any
module or name beneath it, SHALL raise `ImportError` at the import line, whose
message names `machinome.node.adapters` as dissolved, states that
`machinome.node.adapters.<x>` is now `machinome.node.<x>` with
`build123d_sheet` folded into `machinome.node.build123d`, and shows the
import to write. It SHALL NOT re-export, alias or forward any name.

#### Scenario: A leaf is imported from its module

- **WHEN** a module runs `from machinome.node.step import StepAssembly,
  StepNode` and `from machinome.node.build123d import Build123dSheetNode`
- **THEN** it receives the classes those modules define, and
  `from machinome.node import StepNode` and
  `from machinome.node import Build123dSheetNode` each raise `ImportError`
  naming `machinome.node.step` and `machinome.node.build123d` respectively

#### Scenario: A former address is refused naming the new one

- **WHEN** a module runs `from machinome.node.adapters.step import
  StepAssembly`, `from machinome.node.adapters import step` or
  `import machinome.node.adapters.cadquery`
- **THEN** each raises `ImportError` whose message names
  `machinome.node.adapters`, the rule `machinome.node.<x>`, and an import
  line to write instead, and no leaf module is imported by the attempt

#### Scenario: The node root's refusals come from the table

- **WHEN** each class name the table of supported node types lists is imported
  from `machinome.node`, and then from `machinome.node.<key>` of its row
- **THEN** the first raises `ImportError` naming `machinome.node.<key>`, the
  second returns the class that module defines, and no class name the table
  lists is in `machinome.node.__all__`

#### Scenario: Two types in one module stay distinct

- **WHEN** `Build123dNode` and `Build123dSheetNode`, both defined in
  `machinome.node.build123d`, are tested against each other with
  `isinstance`
- **THEN** neither is an instance of the other

#### Scenario: A node type over the B-rep engine resolves from its own distribution

- **WHEN** the repository's workspace is synced and `machinome.node.step` is
  imported
- **THEN** its file is `packages/machinome-node-step/machinome/node/step.py`,
  `StepNode` is the class the module defines, the module's
  `workplane_shape` is `machinome.node.cadquery`'s, from
  `packages/machinome-node-cadquery/`, and the framework's `machinome/node/`
  holds none of `cadquery.py`, `build123d.py`, `step.py` and `molejo.py`

#### Scenario: A node type resolves from its installed wheel

- **WHEN** the framework's wheel is installed with its `step` extra, which
  installs `machinome-node-step` and `machinome-node-cadquery`
- **THEN** `from machinome.node.step import StepNode` returns the class, whose
  module's file is listed in `machinome-node-step`'s installed files, which
  list no `__init__.py`

#### Scenario: A node type over no B-rep engine resolves from its own distribution

- **WHEN** the repository's workspace is synced and `machinome.node.openscad`,
  `machinome.node.solid2`, `machinome.node.jscad` and `machinome.node.stl` are
  imported
- **THEN** their files are
  `packages/machinome-node-openscad/machinome/node/openscad/__init__.py` and
  `packages/machinome-node-<key>/machinome/node/<key>.py` for the other three,
  `Solid2Node` subclasses the OpenSCAD package's `ScadLeafNode`, and each class
  of the table is the class its module defines

#### Scenario: The framework's node package holds no node type

- **WHEN** the framework's `machinome/node/` is listed
- **THEN** it holds no module and no directory named for a key of the table of
  supported node types, and the layout test fails naming any that appears

#### Scenario: The FreeCAD node type resolves from its own distribution

- **WHEN** the repository's workspace is synced and
  `from machinome.node.freecad import FreeCADAssemblyNode, FreeCADJoint` runs
- **THEN** the package's file is
  `packages/machinome-node-freecad/machinome/node/freecad/__init__.py`, the
  two classes are those its module `adapter` defines, importing them from
  `machinome.node` raises `ImportError` naming `machinome.node.freecad`, and
  the framework's `machinome/node/` holds no `freecad`
