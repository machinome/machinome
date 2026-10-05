## ADDED Requirements

### Requirement: Generated project source imports every name from its module

The source the CLI writes into a project SHALL import every framework name from
the module that defines it, never from the node package's root, which resolves
no name (`node-model`, "The node package's root exports nothing"):

- the model module `machinome new` scaffolds SHALL import its node type from
  that node type's module: `from machinome.node.solid2 import Solid2Node` from
  the `solid2` template, `from machinome.node.cadquery import CadQueryNode` from
  the `cadquery` template;
- the `parts.py` `machinome import-step` writes SHALL import `StepNode` from
  `machinome.node.step`, and its `assembly.py` SHALL import `AssemblyNode` from
  `machinome.node.assembly`.

The import-step command SHALL compose each of its import lines from the class it
names, its module and its name as the class reports them, so the command's own
module spells no node type's module (`kernel-extras`, "The core imports no
kernel outside its kernel modules"); the templates are a project's files and
spell their own node type's module.

#### Scenario: The scaffolded part imports its node type from its module

- **WHEN** `machinome new my-project` runs where SolidPython is installed, and
  again where only CadQuery is
- **THEN** the first model module's import line is
  `from machinome.node.solid2 import Solid2Node` and the second's
  `from machinome.node.cadquery import CadQueryNode`, neither generated file
  contains `from machinome.node import`, and each generated project builds and
  passes its two tests as the "New command" requirement states

#### Scenario: The STEP scaffold imports from the modules

- **WHEN** `machinome import-step` scaffolds a document into a package
- **THEN** `parts.py` holds `from machinome.node.step import StepNode`,
  `assembly.py` holds `from machinome.node.assembly import AssemblyNode`,
  neither holds `from machinome.node import`, and both modules import
