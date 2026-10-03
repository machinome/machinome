## ADDED Requirements

### Requirement: Each leaf type is one module under the node package

Each leaf type the core ships SHALL be defined in one module directly under
`machinome.node`, named for its technology, and imported from there:

| module | defines |
|---|---|
| `machinome.node.cadquery` | `CadQueryNode` |
| `machinome.node.build123d` | `Build123dNode`, `Build123dSheetNode`, and the reducer of `Svg` artwork |
| `machinome.node.step` | `StepNode`, `StepAssembly`, `solids_from_faces`, `cached_document` |
| `machinome.node.molejo` | `MolejoNode` |
| `machinome.node.solid2` | `Solid2Node` |
| `machinome.node.openscad` | `OpenScadNode` |
| `machinome.node.jscad` | `JScadNode` |
| `machinome.node.stl` | `StlNode` |

Every name `machinome.node` exported before this change SHALL still resolve
from `machinome.node` to the identical object, now defined in the module
above; the root's re-exports are struck only by the root cleanup.

The package `machinome.node.adapters` SHALL hold no leaf. Importing it, or any
module or name beneath it, SHALL raise `ImportError` at the import line, whose
message names `machinome.node.adapters` as dissolved, states that
`machinome.node.adapters.<x>` is now `machinome.node.<x>` with
`build123d_sheet` folded into `machinome.node.build123d`, and shows the
import to write. It SHALL NOT re-export, alias or forward any name.

#### Scenario: A leaf is imported from its module

- **WHEN** a module runs `from machinome.node.step import StepAssembly,
  StepNode` and `from machinome.node.build123d import Build123dSheetNode`
- **THEN** it receives the classes, and `StepNode` and `Build123dSheetNode`
  are the objects `machinome.node.StepNode` and
  `machinome.node.Build123dSheetNode` resolve to

#### Scenario: A former address is refused naming the new one

- **WHEN** a module runs `from machinome.node.adapters.step import
  StepAssembly`, `from machinome.node.adapters import step` or
  `import machinome.node.adapters.cadquery`
- **THEN** each raises `ImportError` whose message names
  `machinome.node.adapters`, the rule `machinome.node.<x>`, and an import
  line to write instead, and no leaf module is imported by the attempt

#### Scenario: Two types in one module stay distinct

- **WHEN** `Build123dNode` and `Build123dSheetNode`, both defined in
  `machinome.node.build123d`, are tested against each other with
  `isinstance`
- **THEN** neither is an instance of the other
