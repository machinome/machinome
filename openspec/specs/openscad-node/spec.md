# openscad-node Specification

## Purpose
The OpenSCAD node family as the node package `machinome.node.openscad`
(`OpenScadNode`, the leaf base `ScadLeafNode`, the SCAD writer and the
OpenSCAD binary contract), `Solid2Node` at `machinome.node.solid2` over it,
SolidPython as the family's kernel refused at three doors, the adoption of
SolidPython values through a registered hook, and the gate that keeps the
technology's name out of the rest of the core. Encodes ADR-177 (OpenSpec
change `openscad-out`), which took over `openscad-engine` and
`scad-engine-dependency`.

Code: `machinome/node/openscad/`, `machinome/node/solid2.py`,
`machinome/viewers/openscad.py` (until the viewer cycle),
`tests/test_core_names_no_scad.py`.
## Requirements
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
  `machinome.node.openscad`, which is the object `machinome.node.OpenScadNode`
  resolves to, and which is a subclass of
  `machinome.node.openscad.leaf.ScadLeafNode`

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

### Requirement: Solid2Node is machinome.node.solid2 over the package

`Solid2Node` SHALL be defined in the module `machinome.node.solid2`, a
`ScadLeafNode` declaring `namespace = 'solid2'`, whose `as_number` evaluates a
SolidPython value through the OpenSCAD binary of
`machinome.node.openscad.binary` exactly as before. The module SHALL define
`adopt(value)`, which returns, for a SolidPython scalar constant (an instance of
SolidPython's `OpenSCADConstant`, including `ScadValue` and the result of
`scad_inline`), the expression graph node the core's own parser reads from the
value's text, or a node carrying that text verbatim when the text is outside the
parser's language, and `None` for any other value; and it SHALL register `adopt`
with the core's expression graph when it is imported. The adopted node SHALL
evaluate as the text would and SHALL carry the text's free names.

#### Scenario: SolidPython's animation time

- **WHEN** `adopt` is given `solid2.get_animation_time()`
- **THEN** it returns a name node for `$t`

#### Scenario: SolidPython arithmetic over a framework value

- **WHEN** `adopt` is given the text constant SolidPython builds for a
  SolidPython operand on the left of a framework value
- **THEN** the returned graph evaluates as the two operands in that order
  would and its free names are the operands' free names

#### Scenario: Text outside the language

- **WHEN** `adopt` is given `scad_inline('$mystery ? 1 : 2')`
- **THEN** it returns a node carrying that text verbatim, which a law or a
  bound refuses as raw text and publication emits verbatim with its existing
  warning

#### Scenario: Not a SolidPython value

- **WHEN** `adopt` is given a number, a string, a framework symbolic value or
  an expression graph node
- **THEN** it returns `None`

#### Scenario: Importing the module registers the adopter

- **WHEN** a fresh interpreter asks `machinome.expression_graph.symbolic` of
  `solid2.get_animation_time()` before and after importing
  `machinome.node.solid2`
- **THEN** the first answer is `None` and the second is the name node for `$t`

### Requirement: The package writes the SCAD text of a presentation, byte for byte

`machinome.node.openscad.writer.scad_text(description, fn=None)` SHALL return
the SCAD text of a presentation description the core composed: an artifact
import as OpenSCAD's `import(file = ...)` of its path as given, a colour as
`color` with the given components and alpha, a rotation as `rotate` with the
angle and axis as given, a translation as `translate` with the vector as given,
a union of two or more children as `union`, a union of none as an empty
`union();`, and the geometry a family leaf authored, as SolidPython writes that
object. A scalar in a rotation or translation SHALL be written as SolidPython
writes a parameter value: a number in its own form, and any other value,
including the core's symbolic value and a SolidPython value, by its `str()`,
which for the core's symbolic value is its closed text. With `fn` given, the
text SHALL begin with `$fn = <fn>;` and a blank line. The writer SHALL NOT
re-anchor, round, reorder or otherwise alter what the description holds.

`scad_code(node)` SHALL be `scad_text` of the node's own presentation
(`node.presentation()`, its artifact imports resolving from the node's own build
directory) with the node's `fn` when it declares one; `generate_scad(node)`
SHALL publish that text at `<basepath>.scad`, stamped and recorded like every
artifact, replacing nothing whose bytes, stamp and record already match, and
reusing within one source generation the text already published for the same
full source identity of a rigid node. A family leaf's `scad_code` and
`generate_scad()` SHALL be these for the leaf; `OpenScadNode.scad_code` SHALL be
its source followed by a blank line and the last line of the writer's text of
its presentation, as before.

The writer SHALL write SCAD through SolidPython, so for any tree and any process
the text SHALL be byte-identical to the text the framework wrote for that tree in
that process before the family became a package: no header, comment or
whitespace added or removed, and the `use` and `include` lines SolidPython
prefixes kept.

#### Scenario: A placed, coloured artifact import

- **WHEN** `scad_text` is given a rotation by `30.0` about `[0, 0, 1]` of a
  translation by `[1, 2.5, 0]` of a colour `[1.0, 0.5, 0.0]` with alpha `1` of
  the import of `a/b.stl`
- **THEN** it returns `rotate(a = 30.0, v = [0, 0, 1]) {` over a nested
  `translate(v = [1, 2.5, 0])`, `color(alpha = 1, c = [1.0, 0.5, 0.0])` and
  `import(file = "a/b.stl", origin = [0, 0]);`, tab-indented, exactly as
  SolidPython renders those calls

#### Scenario: A symbolic angle

- **WHEN** a rotation's angle is the core's symbolic value `$t * 360`
- **THEN** the text carries `rotate(a = ($t * 360), v = [0, 0, 1])`, the
  value's closed text, unquoted

#### Scenario: The goldens are unchanged

- **WHEN** the `expression-type` and `scad-presentation` goldens' fixtures are
  built and the SCAD text of every recorded node is read through the writer
- **THEN** every SHA-256 and length equals `tests/data/expression_type_golden.json`
  and `tests/data/scad_presentation_golden.json`

#### Scenario: Authored geometry is written as authored

- **WHEN** a `Solid2Node`'s render result, with an `import_stl` of a project
  file by a relative path inside it, is written
- **THEN** the text is SolidPython's rendering of that object, its import path
  exactly as the project wrote it

#### Scenario: Text after an imported SCAD library keeps its use line

- **WHEN** a process has imported a SCAD library through SolidPython's
  `import_scad` and the writer writes a description holding only artifact imports
- **THEN** the text begins with the `use` line SolidPython prefixes, exactly as
  before the family became a package

### Requirement: A family leaf writes and keeps its own SCAD and renders its STL with OpenSCAD

A family leaf's materialization SHALL write its own `.scad` (`generate_scad()`)
from what it rendered, and its `generate_stl()` SHALL render the leaf's STL from
that file with the OpenSCAD binary under the asynchronous STL render protocol of
the `build-pipeline` capability, confirming the binary first under the
`openscad-dependency` capability. It SHALL declare its `.scad` in
`kept_artifacts()`, so the build sweep keeps it while the leaf is in the
published tree. The family leaf's `present(rendered)` SHALL return what it
rendered, which the core holds as authored geometry.

#### Scenario: A Solid2Node leaf builds through OpenSCAD

- **WHEN** a project with a stale `Solid2Node` leaf is built with OpenSCAD
  available
- **THEN** its `.scad` is written by its materialization, OpenSCAD renders its
  `.stl` from it, and both remain after the build's sweep

#### Scenario: A current leaf keeps its SCAD

- **WHEN** a `Solid2Node` leaf whose `.stl` is current is rebuilt
- **THEN** its `.scad` and its currency record are not rewritten and are still
  present after the sweep

### Requirement: SolidPython is the family's kernel, refused at three doors

The family's kernel SHALL be SolidPython, installed by the `openscad` extra;
the `solid2` extra SHALL install the `openscad` extra. `machinome.node.openscad`
and `machinome.node.solid2` SHALL each check, when imported and before importing
SolidPython or each other, that SolidPython can be found, under the
`kernel-extras` capability, and refuse its absence with these messages:

- `machinome.node.openscad (OpenScadNode and the OpenSCAD writer) needs solid2, which is not installed; install it with 'pip install "machinome[openscad]"'`
- `machinome.node.solid2 (Solid2Node) needs solid2, which is not installed; install it with 'pip install "machinome[solid2]"'`

The node root's export SHALL carry the module's refusal unmodified; the table of
supported node types SHALL read it as an absent node type; and a command that
needs the family, `machinome snapshot` with the OpenSCAD renderer, SHALL refuse
at its start under the `cli` capability. No other module of the framework SHALL
import SolidPython, except the project template that scaffolds a `Solid2Node`.

#### Scenario: OpenScadNode without SolidPython

- **WHEN** `machinome.node.openscad` is imported where `solid2` cannot be found
- **THEN** a `ModuleNotFoundError` is raised whose `name` is `solid2` and whose
  message is the first message above, naming `machinome[openscad]`

#### Scenario: Solid2Node without SolidPython

- **WHEN** `from machinome.node import Solid2Node` runs where `solid2` cannot be
  found
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

### Requirement: The core names no SCAD outside the family and the table of node types

No Python module of the framework's core SHALL name SCAD: a scan of every
`machinome/**/*.py` file, the project templates included, reading the file's path
and every identifier, attribute name, string, docstring and comment token, SHALL
find no case-insensitive `scad` outside the package `machinome/node/openscad/`,
the module `machinome/node/solid2.py`, the OpenSCAD viewer's module
`machinome/viewers/openscad.py` and the module `machinome/node/supported.py`,
which holds the table of supported node types. An
occurrence that is JSCAD's own name, a `jscad` whose `j` begins a word (at the
start of the text, after a character that is not a letter, or an upper-case `J`
after a lower-case letter), SHALL pass; `scad` inside any other word SHALL fail.
The scan SHALL be a test of the framework's suite.

The core SHALL describe a node's presentation in its own types
(`machinome.node.presentation`) and SHALL compose no SCAD text; it SHALL obtain
none, except through a family leaf's own members or the OpenSCAD viewer.

#### Scenario: The scan finds nothing

- **WHEN** the scan runs over the framework's source
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

