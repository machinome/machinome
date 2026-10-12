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

The package SHALL hold no viewer. The OpenSCAD viewer, which draws a still of
a node through the package's writer and binary contract, SHALL be the module
`machinome.viewer.openscad` of its own distribution,
`machinome-viewer-openscad`, a provider of the framework's seam of viewers
under the `viewer-seam` capability: it SHALL define `OpenScadViewer` and
`OpenScadImportError`, import the package's writer and binary directly, log
to the logger `viewer.openscad`, and SHALL NOT import a module of the core that
names SCAD.

The package SHALL be shipped by its own distribution, `machinome-node-openscad`,
as a package directory with its own `__init__.py` inside the namespace
portions `machinome` and `machinome.node`, with no `__init__.py` under
`machinome/` or `machinome/node/`; `machinome.node.solid2` SHALL be shipped by
`machinome-node-solid2`. The framework's distribution SHALL ship none of the
family and no OpenSCAD viewer, and `machinome.viewers`,
`machinome.viewers.openscad` and `machinome.node.openscad.renderer` SHALL NOT
exist. In the repository the
package lives at `packages/machinome-node-openscad/machinome/node/openscad/`
and the module at `packages/machinome-node-solid2/machinome/node/solid2.py`.

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

- **WHEN** `machinome.viewer.openscad` is imported with SolidPython
  installed, and again where `solid2` cannot be found
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

#### Scenario: The family resolves from its own distributions

- **WHEN** the repository's workspace is synced and `machinome.node.openscad`,
  `machinome.viewer.openscad` and `machinome.node.solid2` are imported
- **THEN** their files are under `packages/machinome-node-openscad/`,
  `packages/machinome-viewer-openscad/` and `packages/machinome-node-solid2/`,
  the seam's `viewer('openscad')` is that viewer's module, the OpenSCAD node
  package holds no `renderer.py`, and the framework holds neither
  `machinome/node/openscad/` nor `machinome/node/solid2.py` nor a
  `machinome/viewers/` directory

### Requirement: SolidPython is the family's kernel, refused at three doors

The family's kernel SHALL be SolidPython, required by the distribution
`machinome-node-openscad`, which the `openscad` extra installs; the `solid2`
extra SHALL install `machinome-node-solid2`, which requires
`machinome-node-openscad` and names SolidPython in the same range.
`machinome.node.openscad`
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
with the OpenSCAD viewer, whose resolution through the seam of viewers carries
the package's refusal, which SHALL refuse at its start under the `cli`
capability. The node root resolves neither class name, so it is not a door. No
other module of the framework or of its extension packages SHALL import
SolidPython, except the project template that scaffolds a `Solid2Node`.

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

- **WHEN** every module under the framework's `machinome/` and under every
  extension package's `machinome/` is read for imports of `solid2`
- **THEN** the importers are exactly the OpenSCAD package's `__init__.py` and
  `writer.py` in `machinome-node-openscad`, `machinome/node/solid2.py` in
  `machinome-node-solid2`, and the template
  `machinome/manager/templates/project/root/solid2.py`

### Requirement: The core names no SCAD outside the family and the table of node types

No Python module of the framework's core SHALL name SCAD: a scan of every
`machinome/**/*.py` file of the framework's distribution, the project templates
included, and of every extension package's `machinome/**/*.py` under the
repository's `packages/machinome-*`, reading the file's path and every
identifier, attribute name, string, docstring and comment token, SHALL find no
case-insensitive `scad` outside the family's two distributions,
`machinome-node-openscad` and `machinome-node-solid2`, the OpenSCAD viewer's
distribution `machinome-viewer-openscad`, and two modules of the framework:
`machinome/node/supported.py`, which holds the table of supported node types,
and `machinome/viewer/__init__.py`, the seam of viewers, which names the
viewers the core knows. An
occurrence that is JSCAD's own name, a `jscad` whose `j` begins a word (at the
start of the text, after a character that is not a letter, or an upper-case `J`
after a lower-case letter), SHALL pass; `scad` inside any other word SHALL fail.
The scan SHALL be a test of the framework's suite.

The core SHALL describe a node's presentation in its own types
(`machinome.node.presentation`) and SHALL compose no SCAD text; it SHALL obtain
none, except through a family leaf's own members or the OpenSCAD viewer,
which it reaches through the seam of viewers by name.

#### Scenario: The scan finds nothing

- **WHEN** the scan runs over the framework's source and every extension
  package's
- **THEN** it reports no offending module

#### Scenario: JSCAD passes and other words fail

- **WHEN** the scan's rule is applied to `jscad`, `JScadNode`, `OpenJScadNode`,
  `machinome/node/jscad.py`, `openscad`, `scad_file`, `.scad` and `cascade`
- **THEN** the first four pass and the last four fail

#### Scenario: A node is assembled without the family

- **WHEN** `solid2` cannot be found and an assembly of `StlNode` leaves is
  constructed and `assemble()` is called on it
- **THEN** the call returns its presentation description, every child is
  linked and prepared, `mesh` of a child is its world-placed geometry, and no
  module under `machinome.node.openscad` is imported

#### Scenario: The family's former zones in the core offend

- **WHEN** the scan's zones are asked of `machinome/node/openscad/writer.py`,
  `machinome/node/solid2.py` and `machinome/viewers/openscad.py` of the
  framework, and of `machinome/node/stl.py` of `machinome-node-stl`, and the
  framework's `machinome/manager/snapshot.py`
- **THEN** none of them is an allowed zone, and the word in any of them fails
  the scan naming the path
