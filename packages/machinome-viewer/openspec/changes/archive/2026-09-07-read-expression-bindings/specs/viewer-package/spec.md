## ADDED Requirements

### Requirement: A named binding is resolved where it is used

A published document may carry an ordered `bindings` table: named
expressions, published once and referenced by bare name from an
operation's expression, from a flexible leaf's `params`, and from later
entries of the table. The viewer SHALL resolve such a name, wherever it
occurs, to the value of that entry's expression under the same inputs —
the same animation time and the same driver values — as the expression
that named it.

A name SHALL be resolved as a binding BEFORE it is treated as a driver
id, and after `$t`. A binding name SHALL therefore never be reported as
an undeclared driver id.

An entry SHALL be evaluated only when something reads it, and SHALL cost
one resolution per evaluation pass however many operations, parameters or
other entries reach it — the bound the viewer already holds for a
repeated subexpression. Reading a document's expressions through its table
SHALL NOT move a number: an expression that names an entry SHALL resolve
to what the same expression resolves to with that entry's text written out
in its place.

The table SHALL belong to the document that carries it. Two documents
mounted on one page MAY use the same name for different expressions, and
neither SHALL ever resolve a name to the other's value.

A document that carries no table SHALL render exactly as it does when the
viewer knows nothing of bindings.

#### Scenario: A bound document poses as the flat one it was published from

- **WHEN** two documents describing one machine are mounted — one whose
  operations reference a bindings table, one with every reference written
  out in full — at the same animation time and driver values
- **THEN** every operation's matrix is the same in both

#### Scenario: A binding read by many operations costs one resolution

- **WHEN** several operations of one document name the same entry and the
  document is evaluated for one set of inputs
- **THEN** the operations after the first perform no further subexpression
  resolutions, and every operation's matrix is the one its expressions name

#### Scenario: An entry nobody reads costs nothing

- **WHEN** a driver is moved on a document whose table holds entries no
  operation naming that driver reaches
- **THEN** those entries are not evaluated

#### Scenario: Two documents on one page keep their own names

- **WHEN** two documents are mounted on one page, each declaring an entry
  under the same name but with a different expression, and both are
  evaluated at the same animation time and driver values
- **THEN** each renders at the pose its own entry names, and neither reads
  the other's value

#### Scenario: A binding name is not an undeclared driver

- **WHEN** a document declaring an empty `drivers` table carries bindings
  and its operations name them
- **THEN** it loads and renders, because every name its expressions carry
  is `$t`, an entry of its table, or a function of the expression language

### Requirement: Dependence flows through a binding

Where the viewer bounds work by the inputs an expression reads — deciding
whether an operation is re-evaluated, whether a flexible leaf's geometry
is recomputed, and whether a document has a timeline to play — an
expression that names a binding SHALL be treated as reading every input
that binding transitively reads, through as many entries as the chain
runs.

An operation whose whole expression is a binding name resolving through
the table to `$t` SHALL therefore be a time-dependent operation: it SHALL
be re-evaluated when the animation time changes and it SHALL make its
document animated, exactly as it was when its expression was written out
in full. An operation reaching a declared driver id through a binding
SHALL be re-evaluated when that driver moves, and SHALL NOT be
re-evaluated when a driver nothing it reaches names moves.

What an expression reads SHALL follow the table it is read through. When a
document is republished with a table whose entries read different inputs,
the viewer SHALL answer with the new table's inputs even where the
expressions naming those entries are unchanged — so a machine that becomes
time-driven on a republish gains its timeline, one that stops being
time-driven loses it, and each is bounded by what it now reads.

#### Scenario: A document animated only through its table has a timeline

- **WHEN** a document is mounted in which no operation's expression
  mentions `$t`, and every operation that moves does so by naming an entry
  that resolves through the table to `$t`
- **THEN** the viewer presents the animation controls, and advancing the
  time moves those operations

#### Scenario: A driver reached through a binding moves the operation

- **WHEN** an entry's expression names a declared driver id, an operation
  names that entry, and the driver is set
- **THEN** that operation is re-evaluated and the model moves to the pose
  the new value names

#### Scenario: A driver reached by nothing still costs nothing

- **WHEN** a driver is set on a document whose operations, and the entries
  they reach, do not name it
- **THEN** no operation of that document is re-evaluated because of it

#### Scenario: A republished table changes what an unchanged expression reads

- **WHEN** a mounted document is republished with its operations unchanged
  — an operation whose whole expression is one entry name — and that
  entry's expression changed from one over `$t` to one over a declared
  driver id
- **THEN** the operation moves when that driver is set and no longer moves
  when the animation time advances, and the document is no longer animated

#### Scenario: A chain of entries carries dependence to its end

- **WHEN** an operation names an entry that names a second entry that
  names `$t`
- **THEN** the operation is re-evaluated when the animation time changes

### Requirement: A bindings table the viewer cannot resolve is refused by name

A bindings table decides where a machine's parts stand, so a table the
viewer cannot resolve SHALL be refused when the document is loaded —
beside the refusals for an unreadable document version, a flexible
technology or spec it cannot evaluate, an unsupported expression form and
an undeclared driver id — rather than rendering part of a machine from it.
The refusal SHALL name the entry or the name at fault, no tree SHALL be
built from the document, and a model already standing SHALL be left
standing.

The viewer SHALL refuse: a `bindings` value that is not an array of
entries carrying a name and an expression; two entries sharing a name; an
entry whose expression names itself or an entry later in the array; an
entry whose name is also a declared driver id; and a name reached from any
operation, any flexible parameter or any entry that is neither `$t`, nor
an entry of the table, nor a declared driver id — the refusal the viewer
already makes for an undeclared driver id, made after the table's names
are known and naming the name as absent from both tables. An entry whose
expression the viewer cannot read SHALL be refused as such an expression
already is.

The viewer SHALL read a `bindings` table whenever the document carries
one, and SHALL NOT refuse a document for declaring a version whose content
it does not use.

#### Scenario: A dangling reference is refused

- **WHEN** a document is loaded whose operation names an entry its table
  does not carry
- **THEN** loading fails naming that name, no tree is built, and a model
  already standing is left standing

#### Scenario: A table that names forward is refused

- **WHEN** a document is loaded whose entry names an entry appearing later
  in the array, or names itself
- **THEN** loading fails naming that entry

#### Scenario: Two entries under one name are refused

- **WHEN** a document is loaded whose table carries two entries with the
  same name
- **THEN** loading fails naming that name

#### Scenario: An entry named like a declared driver is refused

- **WHEN** a document is loaded whose entry's name is also a key of its
  `drivers` table
- **THEN** loading fails naming that name rather than resolving one of the
  two and leaving the other unreachable

#### Scenario: A malformed table is refused

- **WHEN** a document is loaded whose `bindings` value is not an array, or
  whose entry carries no name or no expression
- **THEN** loading fails naming the offending entry

#### Scenario: An undeclared driver is still refused

- **WHEN** a document carrying a table is loaded, and one of its
  expressions names an id that is neither an entry of the table nor a key
  of its `drivers` table
- **THEN** loading fails naming that id, as it does for a document with no
  table at all

## MODIFIED Requirements

### Requirement: One loader reads either published document

The viewer SHALL render either portable `manifest.json` or normal-build
`viewer.json`, reading their shared fields. It SHALL render document
versions 1, 2, 3 and 4, and SHALL refuse any other version naming it and
the versions it renders. A document whose `drivers`
table is empty SHALL render exactly as a version 1 document. A document
whose `drivers` table is non-empty SHALL load and render at the pose its
expressions evaluate to under the table's declared defaults, with driver
and instruction entries exposed through the handle's driving API. A
document whose expressions reference a qualified id absent from both its
`drivers` table and its `bindings` table is malformed and SHALL fail
loudly naming the id. A version 4 document carries an ordered `bindings`
table, which the viewer SHALL resolve under the binding requirements
above; a document that carries no such table SHALL be read exactly as it
was before the viewer knew of bindings. The
host supplies the document URL
and an optional mesh base; the base defaults to the document's directory, which
for a document URL naming no directory is the directory the document is served
from and never the server root. A fetch or parse failure SHALL name the
document and the reason.

#### Scenario: A build snapshot rooted elsewhere

- **WHEN** a host mounts a `viewer.json` with a mesh base unrelated to its
  document URL
- **THEN** models load from that base with the same tree, colours, and
  animation as the equivalent export

#### Scenario: A self-contained export

- **WHEN** a host mounts an export without supplying a mesh base
- **THEN** its model paths resolve beside the manifest and it renders

#### Scenario: An export served under a subpath

- **WHEN** a host mounts a document URL that names no directory, as the shipped
  export page does with `manifest.json`, and the page is served under a
  subpath rather than at the server root
- **THEN** model paths resolve beside that document under the same subpath, and
  no request is made to the server root

#### Scenario: An unreachable document

- **WHEN** the source document cannot be fetched
- **THEN** mounting fails with an error naming the document and failure

#### Scenario: A driver document renders at its defaults

- **WHEN** a host mounts a document whose `drivers` table declares
  `x_axis.motor` with default 8000
- **THEN** the model renders at the pose its expressions evaluate to
  with `x_axis.motor = 8000`, and no error is raised

#### Scenario: A malformed driver document is refused

- **WHEN** a mounted document's expressions reference a qualified id
  neither its `drivers` table nor its `bindings` table declares
- **THEN** mounting fails naming that id rather than rendering a wrong
  pose

#### Scenario: A document carrying a bindings table is rendered

- **WHEN** a host mounts a document declaring version 4 and carrying a
  non-empty `bindings` table
- **THEN** it renders at the pose its expressions evaluate to through that
  table

#### Scenario: A version beyond the ones it reads is refused

- **WHEN** a host mounts a document declaring version 5
- **THEN** mounting fails naming that version and the versions the viewer
  renders

### Requirement: The viewer declares its API version

The package SHALL declare one API version, expose it on every mount handle and
the browser global, and make it readable without executing the bundle. It SHALL
be raised whenever the mount interface or handle changes incompatibly, and when
a capability a host may require is added to the handle. The declared version
SHALL be 7, reflecting the addition of version-4 document rendering — the
document's `bindings` table — on top of real-time playback. (The baseline
text recorded 5 while the shipped package declared 6: `real-time-playback`
raised the number in `package.json` for the speed capability without a
delta on this requirement. This revision records that correction alongside
the new capability, as the previous revision did for the driver-driving
one.)

#### Scenario: A host checks compatibility before mounting

- **WHEN** a host reads the installed viewer API version
- **THEN** it obtains the package's single declared version without running a
  browser bundle

#### Scenario: A mounted viewer reports its version

- **WHEN** a host inspects a mount handle or the browser global
- **THEN** both report the same declared API version

#### Scenario: A host requires targeted updates

- **WHEN** a host needs `artifactChanged()` and `manifestChanged()`
- **THEN** the declared API version tells it whether they are available

#### Scenario: A host requires camera orientation control

- **WHEN** a host needs to supply an up direction and field of view
- **THEN** the declared API version tells it whether they are available

#### Scenario: A host requires flexible geometry

- **WHEN** a host needs `version: 3` documents rendered
- **THEN** the declared API version tells it whether the capability is
  available

#### Scenario: A host requires documents carrying a bindings table

- **WHEN** a host needs `version: 4` documents rendered
- **THEN** the declared API version tells it whether the capability is
  available

### Requirement: Client evaluation matches producer numerics

The viewer's expression evaluation — OpenSCAD degree trig, `^` as
exponentiation, `$t`, qualified driver ids resolved through the
driver map, and binding names resolved through the document's table —
SHALL match the producer's numeric resolution of the
same expressions to within floating-point rounding, and that agreement
SHALL be enforced by tests against the shipped evaluator module using
producer-computed expected values covering at least: linear and scaled
driver terms, degree-trig chains, `^` terms, sums whose leading term is
negative, expressions mixing `$t` with drivers, expressions that are or
contain a binding name, and design-to-native
instruction target conversion for integer dtypes.

The producer-generated corpus SHALL carry the bindings table its cases
reference, and the tests SHALL resolve a case's expression through that
table exactly as the viewer resolves a document's, so the corpus pins the
table's semantics as well as the functions': an entry naming an earlier
entry, an entry over a driver id as well as over `$t`, and an entry
reached from more than one case. A case pinned by an earlier corpus SHALL
keep its key and its expected value.

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
subexpression between the places that read it, reusing a value already
resolved for the same inputs, and reading a subexpression through a name
the producer published it under, SHALL NOT move a number: a shared
reading, a bound reading and a reading that walked every occurrence
separately SHALL agree exactly, and a
value that is not a number — an unresolved name, or a term that produced no
number — SHALL reach the caller as it does today rather than as a stale or
substituted one.

An expression form the viewer's evaluation cannot support SHALL be refused
when the document is loaded — with the refusals for an unreadable document
version, an unknown flexible technology, an unresolvable bindings table
and an undeclared driver id — naming
the form and quoting the expression, and quoting it in part rather than
whole, since a published expression may be megabytes long. The refusal
SHALL cover every expression the document carries, an operation's, a
flexible node's parameters and a binding's alike, so that no such
expression is first met while a frame is being rendered.

#### Scenario: The parity corpus pins the shipped evaluator

- **WHEN** the widget test suite runs the producer-generated parity
  fixture against the shipped evaluator
- **THEN** every expression's client value matches the producer value
  within float rounding, and removing the `^` rewrite makes the suite
  fail

#### Scenario: The corpus pins the bindings table

- **WHEN** the suite runs a corpus whose cases name entries of its
  bindings table, including a case whose whole expression is one name
- **THEN** each value matches the producer value within float rounding,
  and running the same cases without the table installed fails

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

- **WHEN** a document is loaded whose operation expression, whose flexible
  node's parameter expression, or whose bindings entry carries a form the
  viewer's evaluation does not support, such as an inline function
- **THEN** loading fails naming the form and quoting part of the
  expression, no tree is built for it, a model already standing is left
  standing, and no frame is ever rendered from it
