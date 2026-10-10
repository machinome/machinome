## ADDED Requirements

### Requirement: The OpenSCAD engine is the package machinome.openscad

The OpenSCAD engine SHALL be the subpackage `machinome.openscad`, whose
`__init__` SHALL export no name of its own and SHALL NOT resolve a
submodule's names as attributes of the package. Its modules SHALL be:

- `machinome.openscad.engine`, the provider the core's seam
  (`machinome.scad_engine`) resolves, declaring the contract version it
  implements as `CONTRACT = 1`;
- `machinome.openscad.binary`, the conditional OpenSCAD binary contract:
  `openscad_binary()`, `require_openscad(needed_by, reason, alternative=None)`
  and `OpenScadUnavailable`, with the behaviour and messages the
  `openscad-dependency` capability states.

Within the framework's own source, only modules under `machinome/openscad/`
SHALL import a SolidPython expression name: `OpenSCADConstant` or anything
else from `solid2.core.object_base`, `scad_inline`, `ScadValue` or
`get_animation_time` from any `solid2` module. `machinome.openscad.binary`
SHALL NOT import `solid2`.

#### Scenario: The package itself exports nothing

- **WHEN** a consumer reads `adopt`, `CONTRACT` or `require_openscad` off
  `machinome.openscad` directly
- **THEN** `AttributeError` is raised, and each is read off the submodule
  that defines it

#### Scenario: The binary contract at its address

- **WHEN** `require_openscad('node housing (FacetedBox)', 'its STL is
  rendered from SCAD by OpenSCAD')` is called from
  `machinome.openscad.binary` with no `openscad` on the PATH
- **THEN** it raises `OpenScadUnavailable` with the message the
  `openscad-dependency` capability states, unchanged

### Requirement: The engine adopts a SolidPython scalar as an expression graph

`machinome.openscad.engine.adopt(value)` SHALL return, for a value that is a
SolidPython scalar constant (an instance of SolidPython's `OpenSCADConstant`,
including `ScadValue` and the result of `scad_inline`), the expression graph
node the core's own parser reads from the value's text, or a node carrying
that text verbatim when the text is outside the parser's language. For any
other value it SHALL return `None`. The adopted node SHALL evaluate as the
text would and SHALL carry the text's free names.

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
