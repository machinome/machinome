## MODIFIED Requirements

### Requirement: The OpenSCAD node family is the package machinome.node.openscad

The OpenSCAD node family SHALL be one package directory at its node type's
address, `machinome.node.openscad`, whose `__init__` SHALL define the node type
`OpenScadNode`, so its one import path and its class's module are
`machinome.node.openscad`. Its submodules SHALL be:

- `machinome.node.openscad.leaf`: `ScadLeafNode`, the family's leaf base, a
  `LeafNode` declaring `fn`, `scad_file`, `scad_code`, `generate_scad()`, the
  STL runner `generate_stl()` with `stl_builder_command` and
  `stl_builder_command_for(output)`, `present(rendered)` returning what the
  leaf rendered, `materialize(rendered)` writing its own `.scad`, and
  `kept_artifacts()` returning its `scad_file`;
- `machinome.node.openscad.writer`: `scad_text(description, fn=None)`,
  `scad_code(node)` and `generate_scad(node)`, which write the SCAD of any
  node's presentation;
- `machinome.node.openscad.binary`: `openscad_binary()`,
  `require_openscad(needed_by, reason, alternative=None)` and
  `OpenScadUnavailable`, with the behaviour and messages the
  `openscad-dependency` capability states.

The OpenSCAD snapshot renderer stays at `machinome.viewers.openscad`, the
OpenSCAD viewer's own module, and SHALL import the package's writer and binary
directly; it SHALL NOT import a module of the core that names SCAD.

`OpenScadNode` and `Solid2Node` SHALL subclass `ScadLeafNode`. The modules
`machinome.openscad`, `machinome.openscad.engine`, `machinome.openscad.binary`
and `machinome.scad_engine` SHALL NOT exist, and
nothing SHALL re-export, alias or forward a name they held: importing one fails
with Python's own `ModuleNotFoundError`.

#### Scenario: The node type at its address

- **WHEN** a module runs `from machinome.node.openscad import OpenScadNode`
- **THEN** it receives the class, whose `__module__` is
  `machinome.node.openscad`, which is a subclass of
  `machinome.node.openscad.leaf.ScadLeafNode`, and
  `from machinome.node import OpenScadNode` raises `ImportError` naming
  `machinome.node.openscad`: the package is the class's one import path

#### Scenario: The former addresses are gone

- **WHEN** a module imports `machinome.scad_engine`, `machinome.openscad` or
  `machinome.openscad.binary`
- **THEN** each raises `ModuleNotFoundError` naming the module, whatever other
  copy of the framework lies on `sys.path`

#### Scenario: The OpenSCAD viewer reaches the package directly

- **WHEN** `machinome.viewers.openscad` is imported with SolidPython installed,
  and again where `solid2` cannot be found
- **THEN** the first import loads `machinome.node.openscad.writer` and
  `machinome.node.openscad.binary` and no other module naming SCAD outside the
  allowed zones, and the second raises the package's refusal naming
  `machinome[openscad]`

#### Scenario: The binary contract at its new address

- **WHEN** `require_openscad('node housing (FacetedBox)', 'its STL is rendered
  from SCAD by OpenSCAD')` is called from `machinome.node.openscad.binary` with
  no `openscad` on the PATH
- **THEN** it raises `OpenScadUnavailable` with the message the
  `openscad-dependency` capability states, unchanged

### Requirement: SolidPython is the family's kernel, refused at three doors

The family's kernel SHALL be SolidPython, installed by the `openscad` extra;
the `solid2` extra SHALL install the `openscad` extra. `machinome.node.openscad`
and `machinome.node.solid2` SHALL each check, when imported and before importing
SolidPython or each other, that SolidPython can be found, under the
`kernel-extras` capability, and refuse its absence with these messages:

- `machinome.node.openscad (OpenScadNode and the OpenSCAD writer) needs solid2, which is not installed; install it with 'pip install "machinome[openscad]"'`
- `machinome.node.solid2 (Solid2Node) needs solid2, which is not installed; install it with 'pip install "machinome[solid2]"'`

The three doors SHALL be the module's own import, whether written
`from machinome.node.solid2 import Solid2Node` or reached through the node
package as `from machinome.node import solid2`, which SHALL carry the module's
refusal unmodified; the table of supported node types, which SHALL read it as
an absent node type; and a command that needs the family, `machinome snapshot`
with the OpenSCAD renderer, which SHALL refuse at its start under the `cli`
capability. The node root resolves neither class name, so it is not a door. No other module of the framework SHALL
import SolidPython, except the project template that scaffolds a `Solid2Node`.

#### Scenario: OpenScadNode without SolidPython

- **WHEN** `machinome.node.openscad` is imported where `solid2` cannot be found
- **THEN** a `ModuleNotFoundError` is raised whose `name` is `solid2` and whose
  message is the first message above, naming `machinome[openscad]`

#### Scenario: Solid2Node without SolidPython

- **WHEN** `from machinome.node.solid2 import Solid2Node` runs where `solid2`
  cannot be found
- **THEN** the import line raises the second message above, naming
  `machinome[solid2]`, unmodified

#### Scenario: A project without the family imports no SolidPython

- **WHEN** a project of B-rep and imported STL leaves is loaded, built, tested
  and published where `solid2` cannot be found
- **THEN** everything succeeds, no `.scad` is written, and no SolidPython module
  and no module under `machinome.node.openscad` is imported

#### Scenario: The framework's SolidPython importers

- **WHEN** every module under `machinome/` is read for imports of `solid2`
- **THEN** the importers are exactly the modules under
  `machinome/node/openscad/`, `machinome/node/solid2.py` and the template
  `machinome/manager/templates/project/root/solid2.py`
