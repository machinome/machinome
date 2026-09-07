## ADDED Requirements

### Requirement: A repeated subexpression is evaluated once per pass

A published expression may paste the same subexpression many times over —
the producer builds an expression by string concatenation, so a reused value
arrives as its full text again — and one such expression may appear under
many operations of one document. Evaluating the document's expressions for
one set of inputs SHALL cost the number of DISTINCT subexpressions they
contain rather than the length of their text: a subexpression that occurs
more than once in an expression, or in more than one expression, SHALL be
resolved once for that set of inputs, whichever operation, flexible
parameter or caller asks for it.

The widget SHALL expose, to its own tests, the number of subexpression
resolutions performed and the number of distinct subexpressions prepared, so
the bound is asserted as work performed and never as elapsed time. This is
not a host capability: it SHALL NOT appear on the mount handle, and the
viewer API version SHALL NOT rise for it.

Preparing an expression SHALL NOT retain its parsed form: what the viewer
keeps for a document is its distinct subexpressions, and what it keeps after
its last viewer is disposed of is nothing.

Re-evaluation SHALL stay bounded as it already is — an operation is
re-evaluated only when `$t` or one of its own free variables changed, and a
free variable is still read from the parsed expression, with a dotted driver
id one name and a called function's name never a variable.

#### Scenario: A pasted subexpression costs one resolution

- **WHEN** an expression is built by pasting a subexpression into itself
  repeatedly, so that its text holds thousands of nodes over a few dozen
  distinct ones, and it is evaluated for one set of inputs
- **THEN** its value is the value a reader that walked every pasted node
  would return, and the resolutions performed are of the order of the
  distinct subexpressions, not of the pasted text

#### Scenario: One expression under many operations

- **WHEN** several operations of one document carry the same expression and
  the document is evaluated for one set of inputs
- **THEN** the operations after the first perform no further resolutions,
  and every operation's matrix is the one its expressions name

#### Scenario: New inputs are evaluated afresh

- **WHEN** the animation time advances and the same operations are
  evaluated again
- **THEN** their distinct subexpressions are resolved again for the new
  time, and the values follow the new time

#### Scenario: A driver nobody names still costs nothing

- **WHEN** a driver is set on a document whose operations do not name it
- **THEN** no operation of that document is re-evaluated because of it

#### Scenario: The parse is not kept

- **WHEN** a document's expressions have been prepared and evaluated
- **THEN** the viewer's retained expression state is of the order of the
  document's distinct subexpressions, and disposing of the last viewer on
  the page leaves none of it

## MODIFIED Requirements

### Requirement: Client evaluation matches producer numerics

The viewer's expression evaluation — OpenSCAD degree trig, `^` as
exponentiation, `$t`, and qualified driver ids resolved through the
driver map — SHALL match the producer's numeric resolution of the
same expressions to within floating-point rounding, and that agreement
SHALL be enforced by tests against the shipped evaluator module using
producer-computed expected values covering at least: linear and scaled
driver terms, degree-trig chains, `^` terms, sums whose leading term is
negative, expressions mixing `$t` with drivers, and design-to-native
instruction target conversion for integer dtypes.

Agreement SHALL include operator precedence and not only arithmetic. A
unary minus SHALL bind to the term beside it rather than to the rest of
the expression, so a sum whose leading term is negative resolves to that
negative term plus the rest and never to the negation of the whole; and
`^` SHALL bind tighter than a unary minus, as the producer's own
language does.

Agreement SHALL also include the form of the numbers themselves. The
client SHALL read every numeric literal the producer can write, in
particular a literal in exponent notation — which the producer emits
for any magnitude its language prints that way — and SHALL resolve it to
the value those digits name, at any magnitude and without loss from a
floating-point round-trip. A name that merely begins with or contains
the exponent marker SHALL remain a name.

Agreement SHALL hold however evaluation is organized. Sharing a
subexpression between the places that read it, and reusing a value already
resolved for the same inputs, SHALL NOT move a number: a shared reading and
a reading that walked every occurrence separately SHALL agree exactly, and a
value that is not a number — an unresolved name, or a term that produced no
number — SHALL reach the caller as it does today rather than as a stale or
substituted one.

An expression form the viewer's evaluation cannot support SHALL be refused
when the document is loaded — with the refusals for an unreadable document
version, an unknown flexible technology and an undeclared driver id — naming
the form and quoting the expression, and quoting it in part rather than
whole, since a published expression may be megabytes long. The refusal
SHALL cover every expression the document carries, an operation's and a
flexible node's parameters alike, so that no such expression is first met
while a frame is being rendered.

#### Scenario: The parity corpus pins the shipped evaluator

- **WHEN** the widget test suite runs the producer-generated parity
  fixture against the shipped evaluator
- **THEN** every expression's client value matches the producer value
  within float rounding, and removing the `^` rewrite makes the suite
  fail

#### Scenario: A sum whose leading term is negative crosses the boundary

- **WHEN** the corpus carries an expression whose head is a negative
  literal, evaluated at more than one driver setting
- **THEN** the client value matches the producer value at every one of
  them, and a reader that bound the unary minus to the whole sum instead
  would agree at no more than one

#### Scenario: A driver scaled by an exponent-printed factor

- **WHEN** the corpus carries a driver term whose scale is small enough
  that the producer prints it in exponent notation, together with a bare
  tiny literal and a bare large one
- **THEN** the client resolves each to the producer's value, and a reader
  that could not read an exponent literal would fail to parse them at all

#### Scenario: An identifier is not a literal

- **WHEN** an expression names a driver whose id begins with the exponent
  marker, or calls a function whose name contains it
- **THEN** the evaluator reads it as that name and resolves it through
  the driver map or the math context, unchanged

#### Scenario: A shared reading is the same reading

- **WHEN** every expression of the parity corpus is evaluated through the
  sharing evaluation, one input set at a time
- **THEN** each value matches the producer value within float rounding,
  including the degree-trig chains, the `^` terms and the leading negative
  sums

#### Scenario: An unresolved name is still not a number

- **WHEN** an expression names a driver the document does not declare, or
  reaches through one whose value is not a map, and it is evaluated twice
  for the same inputs
- **THEN** both readings produce exactly what the viewer produces today for
  that expression — the same non-number, or the same failure — and neither
  substitutes another node's value

#### Scenario: An unsupported form is refused at load

- **WHEN** a document is loaded whose operation expression, or whose
  flexible node's parameter expression, carries a form the viewer's
  evaluation does not support, such as an inline function
- **THEN** loading fails naming the form and quoting part of the
  expression, no tree is built for it, a model already standing is left
  standing, and no frame is ever rendered from it
