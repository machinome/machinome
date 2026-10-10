## MODIFIED Requirements

### Requirement: Supported legacy expressions retain their behavior

Existing SolidPython symbolic operands SHALL remain accepted by framework
math and motion in either operand order in a process that has imported
`machinome.node.solid2`, which registers its adopter with the expression graph
(capability `openscad-node`); every project using `Solid2Node` has. The
framework SHALL recognise such an operand only through a registered adopter;
no core module imports SolidPython to do so. Without an adopter, such an
operand meets the refusal its path gives any value that is neither a number nor
an expression. Recognized scalar expression text SHALL retain its evaluation and free
inputs when combined with shared values.

With a framework symbolic value as the left operand, the result SHALL be a
framework symbolic value. With a SolidPython operand on the left of a
framework value, SolidPython's own operator SHALL produce the result, a
SolidPython text constant embedding the framework value's compact closed
text; the framework SHALL read that result back, with the original operand
order, evaluation and free inputs, wherever it reaches framework math, a
law, a bound, an operation or a flexible parameter, and it SHALL remain
publishable. Construction of such a SolidPython result is SolidPython's text
building and falls under the explicitly expanded text clause below, not under
the framework's construction resource guarantee.

The framework's own compact closed scalar expressions
(`machinome.core.expressions.closed_expression`, the `str()` of its symbolic
value) SHALL be readable back into motion processing without adding that
syntax to the viewer document language. Unrecognized legacy text SHALL retain the export capability's
verbatim fallback and warning behavior; failure to read the framework's own
emitted scalar form SHALL be reported as a framework defect.

#### Scenario: Legacy operand appears on either side

- **WHEN** a legacy SolidPython scalar is added, subtracted, divided, compared
  or otherwise combined using a supported operator with a framework symbolic
  value in either order
- **THEN** the operation preserves its original operand order and evaluation,
  and supported combinations remain publishable

#### Scenario: Legacy operand on the left yields SolidPython text the framework reads

- **WHEN** a SolidPython scalar is the left operand of a supported operator
  whose right operand is a framework symbolic value
- **THEN** the result is SolidPython's text constant, and passing it to
  `machinome.math`, returning it from a law or publishing it gives the value
  and free inputs of the operation in that order

#### Scenario: A legacy function wraps compact framework text

- **WHEN** a supported legacy scalar function wraps a shared framework value
  in its own symbolic text
- **THEN** the framework recovers the value and its local dependencies for
  publication without leaking SCAD-local bindings into the viewer document

#### Scenario: Explicitly expanded project text

- **WHEN** project code constructs a large raw expression string before passing
  it to the framework
- **THEN** the existing legacy-input behavior applies, but the framework makes
  no guarantee that constructing that project-owned string used bounded memory
