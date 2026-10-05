# Motion Expression Sharing Specification

## Purpose

Projects compose and reuse deferred motion without expanding its entire ancestry,
while preserving numeric behavior, supported legacy operands and existing outputs.
## Requirements
### Requirement: Reusing motion does not expand all its descendants

The framework SHALL let a project compose and reuse deferred motion through
ordinary arithmetic, supported `machinome.math` functions, ports, couplings,
transformations and flexible parameters without copying the complete expression
of an operand on each reuse. Memory used to construct these values SHALL scale
with the operations the project constructs and their operand references, not
with the number of occurrences in a fully expanded expression tree.

The guarantee SHALL hold within one law as well as across laws and consumers.
It SHALL NOT require the project to name intermediate values through a special
API, reduce controls, approximate a law or bake poses. The framework SHALL
preserve numerical order of operations and the existing supported math
semantics, including degree trigonometry and symbolic comparisons. A symbolic
value SHALL continue to refuse conversion to Python truth.

The guarantee covers framework-generated values and supported combinations
with legacy symbolic operands. Text explicitly expanded by project code or
arbitrary third-party text-building functions is outside construction's
resource guarantee; accepting that text SHALL NOT be presented as recovering
memory already spent creating it.

#### Scenario: Repeated doubling within one law

- **WHEN** a law applies `x = x + x` N times to a symbolic driver
- **THEN** construction adds a bounded number of operations and references per
  step instead of allocating the exponentially expanded text
- **AND** the value at a driver binding agrees with the original arithmetic

#### Scenario: Carry profile feeds several coordinates

- **WHEN** a composed carry law drives a piecewise profile whose result feeds
  several flexible parameters and rigid transformations
- **THEN** each use preserves the composed value without expanding its entire
  ancestry, and every consumer follows the same driver state

#### Scenario: A deep chain has little repetition

- **WHEN** a law creates and publishes a chain of 10,000 additions with changing
  literal operands
- **THEN** the framework handles that depth without a recursion failure or
  dropping expression sharing because of its own traversal stack

### Requirement: All normal consumers preserve bounded expression handling

Building, exporting, generating SCAD, collecting flexible parameters, inspecting
time dependence and reporting errors SHALL NOT materialize the fully expanded
tree of a shared framework expression. Publication SHALL account for the
reachable expressions and output slots together. SCAD output SHALL remain
bounded by the compact expressions it actually writes, even where separate
output sites carry separate self-contained copies.

Diagnostics SHALL bound the expression detail they produce before rendering
large text, rather than expanding a value and truncating afterward.

#### Scenario: Shared time reaches a flexible part

- **WHEN** animation time reaches a flexible port through shared intermediates
- **THEN** the build preserves the existing time-fed no-snapshot behavior and
  publishes the live flexible parameter without flattening its expression

#### Scenario: Unresolved driver is not mistaken for animation time

- **WHEN** a flexible port holds an unresolved driver-only expression on the
  SCAD snapshot path
- **THEN** the framework reports the existing binding error with bounded
  expression detail and does not silently omit the part as time-fed

#### Scenario: A diagnostic encounters a large shared expression

- **WHEN** an invalid use of a large shared expression must be reported
- **THEN** the error identifies the use and gives bounded expression detail
  without allocating the expression's fully expanded spelling

### Requirement: Expression processing does not retain discarded machines

After a machine and its publication are discarded, the framework SHALL NOT
retain their expression graphs through an unbounded process-wide expression
registry. Processing unrelated models repeatedly SHALL NOT accumulate the
expression data of all previously discarded models.

#### Scenario: Repeated independent publications

- **WHEN** different machine instances are built, published and discarded in
  one process
- **THEN** expression storage for discarded instances can be reclaimed and the
  live expression working set follows the still-referenced instances

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

### Requirement: Repeated numerical evaluation preserves shared expression semantics

The framework SHALL evaluate a shared expression against each supplied input mapping with the same arithmetic order and error behavior, including when the same expression is evaluated repeatedly. Processing repeated evaluations SHALL NOT keep a discarded expression graph alive through a process-wide registry.

#### Scenario: One shared expression at several input values

- **WHEN** one shared expression is evaluated repeatedly with different numeric inputs
- **THEN** each result follows the graph's original operation order and the current inputs, without using an earlier numeric result

#### Scenario: Missing input after a successful evaluation

- **WHEN** a shared expression evaluates successfully and is then evaluated without a required input
- **THEN** the second evaluation reports the same unresolved-input error as a first evaluation would

#### Scenario: Discarded evaluated expression is collectible

- **WHEN** an expression is evaluated, then all its owners release it
- **THEN** evaluation bookkeeping does not keep the expression alive

#### Scenario: Full-graph extrema keep numeric operand identity

- **WHEN** a shared expression containing numeric `min` or `max` is evaluated repeatedly with signed-zero, NaN, or changing operands
- **THEN** every result selects the same operand in the same argument order as its first numerical evaluation

#### Scenario: Malformed full-graph extremum keeps its arity error

- **WHEN** a full-graph `min` or `max` call has other than two operands
- **THEN** it reports the same error as the public two-argument numeric function at that call's place in evaluation order

#### Scenario: An earlier error keeps precedence over a later unsupported operation

- **WHEN** an expression has a failing input or arithmetic node before an unsupported operation in its evaluation order
- **THEN** evaluation reports the earlier failure first, including on repeated calls

#### Scenario: Repeated binary evaluation retains IEEE operand order

- **WHEN** a shared binary expression is evaluated repeatedly with changing finite, signed-zero or nonfinite numeric inputs
- **THEN** each numeric result or error retains the original Python operation and operand order, without replacing a later evaluation with an earlier result

### Requirement: Rebinding an expression path uses current piece values

The framework SHALL evaluate an expression path at each new piece using that piece's current inputs and branch values, preserving the graph's arithmetic order and error behavior. Repeated binding SHALL NOT reuse numeric results from earlier pieces or retain a discarded machine graph through process-wide bookkeeping. Repeated samples within one piece SHALL reuse the path's immutable evaluation structure without hashing expression-node keys for each sample. A running constraint whose read paths are determined SHALL follow its bound expression as one search-local path, preserving each sampled level and its order; a constraint without those paths SHALL retain prefix replay.

#### Scenario: Standing input changes between pieces

- **WHEN** the same expression path is bound to one set of inputs and then to a different set
- **THEN** its value and later path samples reflect the new inputs with the same arithmetic order

#### Scenario: Failed first binding does not poison later binding

- **WHEN** a path binding fails for a missing input and the path is rebound with complete inputs
- **THEN** the first call reports its normal error and the second produces the normal value

#### Scenario: Discarded path releases its graph

- **WHEN** a path has been bound and its owner discards it
- **THEN** path bookkeeping does not retain the expression graph

#### Scenario: Numeric extrema select the same operand

- **WHEN** a bound path evaluates numeric `min` or `max` values, including equal signed zeros or a NaN operand
- **THEN** it selects the same operand and follows the same error behavior as the full graph evaluator in the original argument order

#### Scenario: Malformed path extremum keeps its arity error

- **WHEN** a bound path `min` or `max` call has other than two operands
- **THEN** it reports the same error as the public two-argument numeric function at that call's place in evaluation order

#### Scenario: Repeated samples after a successful bind

- **WHEN** one expression path is sampled repeatedly at different moving inputs within a piece
- **THEN** each sample uses its current inputs and standing values in the original operation order without repeated expression-node key lookup

#### Scenario: Failed later bind leaves the prior piece intact

- **WHEN** an expression path is successfully bound, then a later bind fails before completion
- **THEN** that failure retains its original error and cannot partially publish the later piece's values or evaluation structure

#### Scenario: Determined constraint reads follow one search-local path

- **WHEN** a running bound reads determined paths during a searched stop
- **THEN** every existing sample and bisection compares the same level in the same order, with the bound's own coordinate held at the tick-start value and standing reads refreshed at the next search

#### Scenario: Opposite signed-zero endpoints remain distinct

- **WHEN** a determined read path reports numerically equal signed-zero endpoints with different sign bits
- **THEN** the searched bound evaluates each endpoint's actual bit pattern rather than freezing one endpoint as a standing value

#### Scenario: Undetermined reads still replay their prefix

- **WHEN** a required read has no determined motion path
- **THEN** the constraint still replays its sub-program at each existing search fraction, retaining the same result and refusal behavior

### Requirement: Running Bound reads demand their actual motion paths

A running constraint's declared read coordinates SHALL count as consumers of their determined motion paths during propagation. When a read's determiner can provide a path, the existing bound search SHALL sample that actual path at the same fractions and in the same order as its prefix replay would, with the bound's own coordinate held at its original tick-start value. All resulting level float bits, first errors, stops, records and committed bank values SHALL remain unchanged. A read for which propagation has no determined path, including an untraced Play descendant, SHALL retain the existing prefix replay; the engine SHALL NOT infer a chord from endpoint values.

#### Scenario: A retained own-read law feeds a crank Bound

- **WHEN** a retained law reads the coordinate it drives and its output is named only by a running Bound, not by another edge
- **THEN** the Bound receives the law's actual piecewise motion path and each existing search sample gives the same level float as prefix replay

#### Scenario: A read cannot supply a determined path

- **WHEN** a bound reads a Play descendant or another coordinate for which no actual motion path was determined
- **THEN** every existing search fraction still replays the complete required prefix and retains its result and refusal behavior

#### Scenario: Ordinary motion and a stopped withdrawal

- **WHEN** the same machine completes a free crank turn or reaches a moving-read physical stop
- **THEN** all search levels, stop attribution and bank values match the previous execution, with no change to dt, samples, tolerances or authored laws

### Requirement: Repeated path samples reuse immutable numeric operations

After a path has been bound successfully, repeated samples of the same immutable moving cone SHALL reuse its operation classification and operand positions. Each sample SHALL still read its current moving inputs and the current piece's standing values, evaluate the same nodes in the same postorder with the same numeric operators and operand order, and report the same first error. Binding a new piece SHALL refresh standing values; a failed binding SHALL NOT publish partial values or structure. This optimization SHALL NOT retain discarded paths or change the number of evaluated path points.

#### Scenario: A changing input crosses several arithmetic operators

- **WHEN** a bound path with shared arithmetic, unary operations and numeric extrema is sampled at several moving input values
- **THEN** every result has the same float bits as whole-graph evaluation at the current inputs, including signed zero and NaN operand selection

#### Scenario: A later sample fails

- **WHEN** a moving input makes an earlier operation fail before another node in the path
- **THEN** that sample reports the original earlier error at the same operation, without returning a cached prior value

#### Scenario: A new piece changes standing values

- **WHEN** a path is rebound with different standing inputs or branch placeholders
- **THEN** its later samples use the new standing values and the path's original node order

#### Scenario: The path is released

- **WHEN** the path and its owner are discarded after repeated samples
- **THEN** operation bookkeeping retains no reference to its expression graph

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

