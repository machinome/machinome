## ADDED Requirements

### Requirement: The node package's root exports nothing

The package `machinome.node` SHALL resolve no name of its own: every class,
function and declaration a project imports from the node package SHALL be
imported from the module that defines it, at one address. Its `__all__` SHALL
be empty, so `from machinome.node import *` binds nothing, and the names its
module namespace binds SHALL be only its submodules, dunder metadata and
private names; it SHALL keep extending its path with node packages installed
as portions.

Each of the twenty-one names the root resolved until the OpenSpec change
`root-cleanup` SHALL be
refused, both as `from machinome.node import <name>` and as an attribute read
of `machinome.node`, with `ImportError` (not `AttributeError`, whose message
the import machinery discards), whose message is exactly

```
module 'machinome.node' has no attribute '<name>': the root of machinome.node exports nothing, and '<name>' is imported from its module, '<module>'. Write `from <module> import <name>`.
```

for the name and module of this table:

| name | module |
|---|---|
| `AssemblyNode` | `machinome.node.assembly` |
| `declared_children` | `machinome.node.declarative` |
| `FusionNode` | `machinome.node.fusion` |
| `SheetLeafNode` | `machinome.node.sheet_leaf` |
| `FlexibleNode` | `machinome.node.flexible` |
| `Marking`, `Wrapped`, `Flat`, `Svg` | `machinome.node.markings` |
| `Frame` | `machinome.node.frames` |
| `property_as_number` | `machinome.node.decorators` |
| `StlRenderStart` | `machinome.node.base` |
| each class name of a row of the table of supported node types (`CadQueryNode`, `Build123dNode`, `Build123dSheetNode`, `StepNode`, `MolejoNode`, `Solid2Node`, `OpenScadNode`, `JScadNode`, `StlNode`) | `machinome.node.<key>` of its row |

The node types' names SHALL be read from the table of supported node types,
never spelled in the root; the refusal SHALL be a lookup of the requested name,
never a comparison with a class's name, and it SHALL decide nothing but the
words of the error. Nothing SHALL alias, re-export or forward a refused name.

The root SHALL keep refusing the port and time-base names under the `ports`
capability, and the package `machinome.node.adapters` SHALL keep refusing
every spelling beneath it, each with its own message. A submodule of the
package SHALL still be reachable through it: `from machinome.node import
supported` and an attribute read `machinome.node.step` return the module, and
a submodule whose kernel is absent raises that module's own refusal,
unmodified. Any other name SHALL raise `AttributeError`.

#### Scenario: A former root name is refused naming its module

- **WHEN** a module runs `from machinome.node import AssemblyNode`
- **THEN** it raises `ImportError` whose message is the sentence above for
  `AssemblyNode` and `machinome.node.assembly`, and binds nothing

#### Scenario: Every former root name is refused

- **WHEN** each of the twenty-one names is imported from `machinome.node`, and
  read with `getattr(machinome.node, name)` and `hasattr(machinome.node, name)`
- **THEN** each raises `ImportError` naming the module of the table, and the
  same name imported from that module is the object the module defines

#### Scenario: The root binds no public name but its submodules

- **WHEN** `machinome.node` is imported and its namespace and `__all__` are read
- **THEN** `__all__` is empty, `from machinome.node import *` binds nothing,
  and every name of the namespace that does not begin with an underscore is a
  submodule of the package

#### Scenario: A submodule is still imported through the package

- **WHEN** a module runs `from machinome.node import supported, phase, step`
- **THEN** it receives the three modules, and where the `step` extra is absent
  the third raises the `step` module's own refusal naming
  `pip install "machinome[step]"`, unmodified

#### Scenario: A table row's classes are refused with their module

- **WHEN** a node type is added to the table of supported node types with its
  class names, and one of them is imported from `machinome.node`
- **THEN** the refusal names `machinome.node.<key>` of the new row, and no
  module of the core but the table spells the class name

## MODIFIED Requirements

### Requirement: Each leaf type is one module under the node package

Each leaf type the core ships SHALL be defined at one address directly under
`machinome.node`, named for its technology, and imported from there: a module,
or, for the OpenSCAD node family, the package `machinome.node.openscad`, whose
`__init__` defines the node type and whose other modules are its machinery
under the `openscad-node` capability. Which node types exist, with the class
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

Each of those classes SHALL be imported from its node type's module and from
nowhere else: the node root resolves none of them, and refuses each naming its
module, under the requirement "The node package's root exports nothing".

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

#### Scenario: The node root's node types come from the table

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
