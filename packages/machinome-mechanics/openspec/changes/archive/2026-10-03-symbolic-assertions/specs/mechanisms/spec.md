## MODIFIED Requirements

### Requirement: Mechanism laws as compositions over expression math

The system SHALL provide the package `machinome_mechanics`, whose every
function is a composition of `machinome.math` functions and ordinary
arithmetic, so that one formula computes on plain numbers and builds the
viewer's deferred expression when any argument is symbolic animation time or
a driver. No function in the package SHALL emit an OpenSCAD builtin that
`machinome.math` does not already emit, so the cross-runtime parity corpus
of the `kinematics` capability covers the package without extension.

The package SHALL re-export every public function under a flat name unique
across its families, so `from machinome_mechanics import meshed_angle`
works, and SHALL keep each family in its own module with the family's
conventions stated once in that module.

Every angle SHALL be in degrees, positive by the right-hand rule about the
stated axis, matching `machinome.math` and the node transform API. Every
function's docstring SHALL state its frame, its zero and its sign, and SHALL
map that convention onto the originating project it was lifted from.

The package SHALL NOT provide a declared (class-body) face: its laws carry
degree literals such as `180` and `360` that the dimension algebra cannot
type as angles, so a declared token reaching a law raises the algebra's own
dimension error at class definition rather than yielding a formula. A class
body that needs a mechanism law over declared parameters evaluates it on
`.value` operands, which is the algebra's stated escape hatch.

#### Scenario: A law rides through a symbolic driver

- **WHEN** `piston_height` is called with a symbolic driver expression as
  the crank angle and numbers for the crank radius and rod length
- **THEN** it returns a symbolic expression composed only of `cos`, `sin`,
  `sqrt` calls and arithmetic, and nothing raises

#### Scenario: Numeric and symbolic faces agree

- **WHEN** each exported law is evaluated once on numbers and once on a
  symbolic expression that is then evaluated at the same numbers
- **THEN** the two results are equal within floating-point tolerance for
  every law and every sampled input

#### Scenario: The declared face is refused

- **WHEN** a class body computes `meshed_angle(theta, 12, 24)` over a
  declared `Angle` parameter `theta`
- **THEN** class definition raises a dimension error, and the same
  computation over `theta.value` succeeds

#### Scenario: The framework recognises the deferred face

- **WHEN** a gear-mesh, lead-screw, slider-crank, delta or circle-geometry
  law is applied to a symbolic driver over animation time, directly or
  through a realized Machinome motion law
- **THEN** each value it returns is symbolic by the framework's own
  predicate, `machinome.expression_graph.symbolic(value)` returning an
  expression node rather than `None`, whatever class carries the expression
