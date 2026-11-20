## MODIFIED Requirements

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

A pose of a document whose bindings table the flat pass serves SHALL cost
less than that bound where its inputs moved only in part: the subexpressions
the flat pass covers SHALL be computed for a pose only when an input they
read changed since that table's last served pose, and once; the others SHALL
be resolved once per pass as above.

The widget SHALL expose, to its own tests, the number of subexpression
resolutions performed by the recursive evaluation, the number of values
computed by the flat pass, and the number of distinct subexpressions
prepared, so the bound is asserted as work performed and never as elapsed
time; the work a pose performs is the first two together. This is not a
host capability: it SHALL NOT appear on the mount handle, and the viewer API
version SHALL NOT rise for it.

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
- **THEN** their distinct subexpressions that read the time are computed
  again for the new time, every other one is resolved again unless the flat
  pass serves it, and the values follow the new time

#### Scenario: A driver nobody names still costs nothing

- **WHEN** a driver is set on a document whose operations do not name it
- **THEN** no operation of that document is re-evaluated because of it

#### Scenario: The parse is not kept

- **WHEN** a document's expressions have been prepared and evaluated
- **THEN** the viewer's retained expression state is of the order of the
  document's distinct subexpressions, and disposing of the last viewer on
  the page leaves none of it

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
repeated subexpression. A pose served by the flat pass MAY also compute an
entry the pose does not read, and only when an input that entry reads
changed; such a computation SHALL NOT throw, SHALL NOT change any value the
viewer computes, and SHALL be counted as the flat pass's work, never as a
resolution. Reading a document's expressions through its table SHALL NOT
move a number: an expression that names an entry SHALL resolve to what the
same expression resolves to with that entry's text written out in its
place.

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
- **THEN** those entries are not resolved, and the flat pass computes none
  of them that does not itself read that driver

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

## ADDED Requirements

### Requirement: A pose evaluates a large document's formulas in one flat pass

When a pose is made — a tree update or a judgement of a pose without showing
it, whether for a driver change, a drawn frame, a clocked request, a running
pose or a republish — of a document whose bindings table holds at least a
source-defined minimum of entries, the viewer SHALL first evaluate, in one
flat pass, the part of that table's expression graph the pass covers: numeric
literals, `$t`, binding names, names read from the scope, unary minus,
arithmetic, comparisons and equality, and calls of a fixed set of the
expression language's functions that never throw on numbers and keep no
state, wherever every operand is itself covered. Everything else SHALL be
evaluated as before, reading covered values where it reaches them.

Every value the flat pass hands out SHALL be identical to the one the
recursive evaluation gives for the same node and inputs, in value and in
type: negative zero and not-a-number included, and the result of a
comparison a boolean. The flat pass SHALL NOT throw, and a pose SHALL refuse
exactly what it refuses today, with the same message: anything that can throw
— a member read on a primitive owner, a call of something that is not a
function, a function that may throw, an unknown operator, the untaken side
of `&&`, `||` or a ternary — SHALL stay with the recursive evaluation, lazy
as it is.

A pose whose scope the flat pass cannot serve — an input it reads missing or
not a number, a member read through a primitive owner, a driver named like a
function it calls — SHALL be evaluated wholly as before for that pose, and
SHALL leave nothing of the flat pass that a later pose could read stale.

The flat pass SHALL compute only what the inputs that changed since the
table's last served pose feed, however many inputs the table reads, so a
pose that moves an input few formulas read SHALL compute few of them. A
document with no bindings table, or a smaller one, SHALL compile nothing and
SHALL be evaluated as before. The first pose of a table pays its
compilation.

The compiled form SHALL belong to the table and to the expression store's
generation: it SHALL be discarded wherever the store is reclaimed, SHALL
never serve a pose under another document's table, and SHALL keep serving
its own table after expressions are prepared that it does not contain. Two
documents operated alternately SHALL NOT recompile on each switch.
Evaluation outside a pose — a clocked machine's solving, a running
program's ticks, a value followed along a path, validation — SHALL NOT run
the flat pass.

#### Scenario: A moved input computes only what it feeds

- **WHEN** a document whose table is served by the flat pass is posed, and
  then posed again with one input moved that only a few of its formulas read
- **THEN** the second pose computes only those formulas and the operations
  that read them, and every matrix is the one the recursive evaluation gives

#### Scenario: A comparison stays a boolean

- **WHEN** an entry of a served table is a comparison and an expression the
  flat pass does not cover tests it with `===` or `!==`
- **THEN** that expression receives `true` or `false`, as before

#### Scenario: An untaken side is still not evaluated

- **WHEN** an expression of a served table guards, with `&&`, `||` or a
  ternary, a side that would throw, and the guard does not take that side
- **THEN** the pose does not throw; and when the guard does take it, the
  pose refuses with the message it gives without the flat pass

#### Scenario: A scope the flat pass cannot serve

- **WHEN** a pose's scope lacks an input of a served table, or holds
  something other than a number there, or names a driver like a function the
  table calls
- **THEN** the pose gives the values, and the refusal if any, of the
  recursive evaluation, and a later pose with a complete scope gives the
  values of its own inputs

#### Scenario: A small document compiles nothing

- **WHEN** a document with no bindings table, or one smaller than the flat
  pass's minimum, is posed
- **THEN** nothing is compiled and the pose is evaluated as before

#### Scenario: Two documents are posed alternately

- **WHEN** two documents whose tables bind the same names to different
  expressions are posed alternately several times
- **THEN** each poses by its own table, and each table is compiled once

#### Scenario: The store is reclaimed between poses

- **WHEN** the expression store is reclaimed after a served pose and the
  document is posed again
- **THEN** the table is compiled again and the pose gives the values of its
  own expressions, never a value of a node from before the reclamation

#### Scenario: Ticks and clocked solving do not run the flat pass

- **WHEN** a running program ticks or a clocked machine solves a request
- **THEN** their evaluations do not run the flat pass, and their results and
  resolutions are what they are without it
