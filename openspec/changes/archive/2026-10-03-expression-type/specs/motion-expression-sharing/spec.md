## ADDED Requirements

### Requirement: A symbolic value is the framework's own type

Every symbolic value the framework produces SHALL be an instance of
`machinome.expression_graph.GraphValue`, a class defined there once, whose
method resolution order contains no class defined in a `solid2` module:
animation time where it is not bound, a driver read in symbolic mode, a
symbolic port value, every symbolic result of `machinome.math`, of arithmetic
on a framework symbolic value, and of a law, bound, chain, jump plan or
profile contact the simulation compiles. Importing `machinome.math` or
`machinome.expression_graph` SHALL NOT import SolidPython.

The value SHALL support, with a framework symbolic value or a plain number on
either side, `+`, `-`, `*`, `/`, `%`, `**` (published as `^`), the six
comparisons, unary `-` and `abs()`, each producing a framework symbolic value
whose evaluation follows the operation in its written operand order; and
`float()` of a value with no free input. It SHALL NOT be iterable or hashable,
and unary `+` SHALL raise `TypeError`. Asking for its truth SHALL raise
`machinome.expression_graph.SymbolicTruthError`, a subclass of `Exception`
that is not a `TypeError`, whose message identifies the value with bounded
detail and names composing with `machinome.math` (`min`, `max`, `clamp`,
`sign`) or binding the drivers first as the remedy.

Its `str()` and `value` SHALL be the framework's compact closed scalar text,
the same text the framework emitted for the same construction before this
type had its own class; consequently a standalone operation serialization, a
generated SCAD file, an identity derived from that text, and a published
document SHALL be byte-identical to what the same model produced before, and
the document version SHALL NOT change because of the type.

#### Scenario: Time and math carry no SolidPython class

- **WHEN** a project reads unbound `self.time`, a driver in symbolic mode, and
  `machinome.math.sin(self.time * 360)`
- **THEN** each is a `GraphValue` and no class in its MRO comes from a
  `solid2` module

#### Scenario: Importing the vocabulary imports no SolidPython

- **WHEN** a fresh interpreter imports `machinome.math` and
  `machinome.expression_graph`
- **THEN** no `solid2` module is among the imported modules

#### Scenario: Truth is refused without a TypeError

- **WHEN** a project writes `if self.time < 0.5:` on a symbolic time
- **THEN** `SymbolicTruthError` is raised naming the comparison with bounded
  detail, and an `except TypeError` around it does not catch it

#### Scenario: Outputs do not change

- **WHEN** a model whose operations, flexible parameters, laws and bounds
  carry symbolic values is built, published and its SCAD written, before and
  after the type became the framework's own
- **THEN** its SCAD files, its operations' standalone serializations and its
  published document are byte-identical

## MODIFIED Requirements

### Requirement: Supported legacy expressions retain their behavior

Existing SolidPython symbolic operands SHALL remain accepted by framework
math and motion in either operand order when the OpenSCAD engine resolves
(capability `scad-engine-dependency`), which it does in every installation
carrying SolidPython. The framework SHALL recognise such an operand only
through that engine; no core module outside the engine imports SolidPython to
do so. Recognized scalar expression text SHALL retain its evaluation and free
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

The framework's own compact SCAD scalar expressions SHALL be readable back
into motion processing without adding that syntax to the viewer document
language. Unrecognized legacy text SHALL retain the export capability's
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
