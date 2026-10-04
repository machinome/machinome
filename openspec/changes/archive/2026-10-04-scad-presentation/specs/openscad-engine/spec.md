## MODIFIED Requirements

### Requirement: The OpenSCAD engine is the package machinome.openscad

The OpenSCAD engine SHALL be the subpackage `machinome.openscad`, whose
`__init__` SHALL export no name of its own and SHALL NOT resolve a
submodule's names as attributes of the package. Its modules SHALL be:

- `machinome.openscad.engine`, the provider the core's seam
  (`machinome.scad_engine`) resolves, declaring the contract version it
  implements as `CONTRACT = 2` and providing that contract's operations,
  `adopt`, `scad_text` and `require_binary`;
- `machinome.openscad.binary`, the conditional OpenSCAD binary contract:
  `openscad_binary()`, `require_openscad(needed_by, reason, alternative=None)`
  and `OpenScadUnavailable`, with the behaviour and messages the
  `openscad-dependency` capability states; `OpenScadUnavailable` derives from
  the seam's `ScadEngineUnavailable`.

Within the framework's own source, only modules under `machinome/openscad/`
SHALL import a SolidPython expression name: `OpenSCADConstant` or anything
else from `solid2.core.object_base`, `scad_inline`, `ScadValue` or
`get_animation_time` from any `solid2` module. `machinome.openscad.binary`
SHALL NOT import `solid2`.

#### Scenario: The package itself exports nothing

- **WHEN** a consumer reads `adopt`, `scad_text`, `CONTRACT` or
  `require_openscad` off `machinome.openscad` directly
- **THEN** `AttributeError` is raised, and each is read off the submodule
  that defines it

#### Scenario: The binary contract at its address

- **WHEN** `require_openscad('node housing (FacetedBox)', 'its STL is
  rendered from SCAD by OpenSCAD')` is called from
  `machinome.openscad.binary` with no `openscad` on the PATH
- **THEN** it raises `OpenScadUnavailable` with the message the
  `openscad-dependency` capability states, unchanged

#### Scenario: The core reaches the binary through the provider

- **WHEN** `require_binary(needed_by, reason, alternative)` is called on the
  provider
- **THEN** it returns what `machinome.openscad.binary.require_openscad` returns
  for those arguments, or raises what it raises, resolving the binary once per
  process

## ADDED Requirements

### Requirement: The engine writes the SCAD text of a presentation description

`machinome.openscad.engine.scad_text(description, fn=None)` SHALL return the
SCAD text of a presentation description the core composed: an artifact import
as OpenSCAD's `import(file = ...)` of its path as given, a colour as `color`
with the given components and alpha, a rotation as `rotate` with the angle and
axis as given, a translation as `translate` with the vector as given, a union
of two or more children as `union`, a union of none as an empty `union();`,
and the geometry a SCAD-presented leaf authored, as SolidPython writes that
object. A scalar in a rotation or translation SHALL be written as SolidPython
writes a parameter value: a number in its own form, and any other value,
including the core's symbolic value and a SolidPython value, by its `str()`,
which for the core's symbolic value is its closed OpenSCAD text. With `fn`
given, the text SHALL begin with `$fn = <fn>;` and a blank line. The engine
SHALL NOT re-anchor, round, reorder or otherwise alter what the description
holds.

For any tree, the text SHALL be byte-identical to the text the core wrote for
that tree before the presentation moved to the engine: no header, comment or
whitespace is added.

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

#### Scenario: The expression golden is unchanged

- **WHEN** the `expression-type` golden's fixture is built and its
  assembly's and children's `scad_code` are read in symbolic driver mode
- **THEN** every SHA-256 and length equals `tests/data/expression_type_golden.json`

#### Scenario: Authored geometry is written as authored

- **WHEN** a `Solid2Node`'s render result, with an `import_stl` of a project
  file by a relative path inside it, is presented
- **THEN** the text is SolidPython's rendering of that object, its import path
  exactly as the project wrote it
