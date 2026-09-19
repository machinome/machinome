## MODIFIED Requirements

### Requirement: Joint arguments resolve against the instance at realization

The system SHALL resolve a joint's `axis`, `at`, `range` and, where the
joint declares one, its further points such as an `Orbit`'s `carries`,
against the DECLARER: for a class-declared joint, each realized instance
of the declaring class, at realization, once its parameters are resolved;
for a SITE-declared joint, the realized DECLARING PARENT, at the moment
the child is realized, once that parent's parameters are resolved and its
`check()` has run. Each component MAY be a plain number, a
declared-parameter token, or a derived formula over such tokens,
resolved against that declarer's values exactly as a child
declaration's arguments are; `axis`, `at`, `carries` or `range` as a
whole MAY instead be a callable of ONE argument, which the framework
SHALL call with the realized DECLARER — the node itself for a
class-declared joint, the declaring parent for a site-declared one — and
which SHALL return the components as plain numbers. EITHER BOUND of a
`range` pair MAY instead be `None`, meaning unbounded on that side, or
a CALLABLE of one argument, which states the bound as an expression
over the joint's OWN COORDINATE and which the framework SHALL NOT
resolve to a number at realization — it is applied where the bound is
used, under the requirement "A declared range refuses a binding outside
it" — or a `Bound(expression, reads=(...))`, which states the bound as
an expression over the joint's own coordinate AND the coordinates it
names. `expression` SHALL be a callable applied to the joint's own
coordinate first and then to each read in the order `reads` states
them, so a `Bound` with no reads means exactly what the one-argument
callable means. Each read SHALL be named as a relation's end is named
in a class body — a joint or port that body owns, a path through child
declarations, or a driver of the declaring class — and SHALL be
refused at CLASS DEFINITION by the same rules: a declaration held in a
list, a repeated child, a child whose class declares no joint or
several, a driver read sideways, and, additionally, a read that names
the bounded coordinate itself. Under a RUNNING root a read SHALL
additionally be a coordinate the run banks, a read of a plain port or a
derived coordinate being refused at simulation construction under the
simulation requirement "A range bound may read other coordinates"; under
every other root such a read is resolved and judged like any other. A
`Bound`'s reads SHALL be resolved against the joint's DECLARER — the
node itself for a class-declared joint, the declaring parent for a
site-declared one — where the values
are needed and never at realization: at the close of the enumeration
that bound the coordinate untimed, and at simulation construction
under a running root. A callable given as the whole `range` and a
callable or `Bound` given as one of its bounds SHALL be told apart by
POSITION and SHALL keep their separate meanings. A site-declared
joint's callable SHALL be able to read the declaring parent's resolved
parameters and flags and anything that parent's own `__init__` has set,
and SHALL NOT be able to read the child's placement, which does not exist
yet, or anything the parent's `render()` produces. A joint on a
`.repeat()` declaration SHALL be resolved once per copy against the same
declaring parent, so every copy carries identical resolved arguments; a
copy's own position SHALL NOT be handed to the callable.
Every one of these resolutions SHALL yield a value in the DECLARER's
frame, and SHALL be complete at realization: no joint argument
of a class-declared joint SHALL depend on the node's placement, so an
`Orbit`'s `carries` left unstated on a CLASS declaration SHALL resolve at
realization to `(0, 0, 0)`, the body's own origin, like any other
defaulted vector; left unstated on a SITE declaration it names the
child's own origin, which is not a number until the body is placed and is
resolved when the joint is carried. A
`Free`'s `at` SHALL resolve by exactly the same path as every other
joint's; a `Free` declares no `axis` and no `range`, so it resolves
neither.

Resolved joint arguments SHALL NOT enter the node's identity: a joint
states where a body may move, not what geometry is built, and two
instances differing only in a joint argument SHALL share their
artifacts.

An argument that cannot resolve SHALL fail at realization, naming the
class, the joint and the argument: a token that is not a declared
parameter of the class, an `axis`, `at` or `carries` that is not three
numbers, an `axis` of zero length, or a `range` that is not a `(lo, hi)`
pair whose bounds are each a number, `None`, a callable or a `Bound` —
the `lo <= hi` ordering being required where both resolve to numbers
at realization and checked where each bound is evaluated otherwise.

#### Scenario: A joint sized by a parameter

- **WHEN** a class declares `reach = Length(160.0)` and
  `elbow = Revolute(axis=(0, 0, 1), at=(0, reach, 68), unit='deg')`, and
  two instances are realized with different `reach`
- **THEN** each instance's joint anchor carries its own resolved number,
  read in that instance's own frame

#### Scenario: A joint anchored on a built position

- **WHEN** a class declares
  `turn = Revolute(axis=(0, 0, 1), at=lambda node: node.built.bearings[node.index])`,
  where `built` is a library object the node constructs from its
  parameters
- **THEN** the callable is called once with the realized node and its
  three numbers become that instance's anchor, read in that instance's
  own frame

#### Scenario: An unresolvable argument fails by name

- **WHEN** a joint declares an `at` naming a token the class does not
  declare, or an `axis` of two components, or a zero-length `axis`, or a
  reversed `range`
- **THEN** realization raises naming the class, the joint and the
  argument at fault, and the instance realized no child

#### Scenario: A joint argument is not identity

- **WHEN** two instances of one class differ only in the resolved value
  of a joint anchor
- **THEN** they share one build identity and one set of artifacts

#### Scenario: An expression bound is carried through realization

- **WHEN** a class declares
  `turn = Revolute(axis=(1, 0, 0), range=(lambda turn: 36 * floor(turn / 36), None))`
  and the instance is realized
- **THEN** realization succeeds, the joint's resolved range carries the
  callable and the open bound as declared, and no number was computed
  for either

#### Scenario: A bound naming other coordinates is carried through realization

- **WHEN** a class declares `p1 = Pin()`, `p2 = Pin()` and then
  `turn = Revolute(axis=(0, 0, 1), range=(0, Bound(lambda turn, a, b: 90 * (abs(a) <= 0.05) * (abs(b) <= 0.05), reads=(p1.lift, p2.lift))))`
  and the instance is realized
- **THEN** realization succeeds, the joint's resolved range carries the
  `Bound` as declared, no read was resolved and no number was computed

#### Scenario: A bound on a site joint reads the declaring parent's subtree

- **WHEN** a parent declares `key = Key()` and then
  `plug = Plug(turn=Revolute(axis=(0, 0, 1), range=(0, Bound(lambda turn, travel: 90 * (travel >= 20), reads=(key.travel,)))))`
- **THEN** the read `key.travel` is resolved against the realized
  PARENT, the node that declared the site, and names that parent's
  `key` child's coordinate

#### Scenario: A read a class body cannot name is refused at class definition

- **WHEN** a class body writes a `Bound` whose `reads` names a child
  held in a list, a repeated child, a child whose class declares two
  joints, a driver read off a child declaration, or the bounded
  coordinate itself
- **THEN** class definition raises naming the read and the rule it
  breaks, exactly as the same end of a relation is refused

#### Scenario: A defaulted carried point resolves at realization

- **WHEN** an `Orbit` is declared with no `carries` and the instance is
  realized
- **THEN** its resolved carried point is `(0, 0, 0)`, the body's own
  origin, available before the body has been placed

#### Scenario: A site joint's callable is handed the declaring parent

- **WHEN** an assembly declares `dir` and `side` as parameters and
  `camera = Link('link-camera', tilt=Revolute(axis=lambda parent: (0.0, -parent.side, 0.0), at=lambda parent: (parent.dir * parent.side * X, Y, Z), unit='deg'))`,
  and two instances are realized with different `dir` and `side`
- **THEN** each callable was called once per realized child with the
  realized ASSEMBLY, and each child carries the arguments its own
  parent's handedness produced

#### Scenario: A site joint's arguments are not identity

- **WHEN** two parents declare the same child class at sites differing
  only in the joint they pass
- **THEN** the two realized children share one build identity and one set
  of artifacts, and neither joint reached the child's constructor

### Requirement: A declared range refuses a binding outside it

The system SHALL refuse, at the moment of binding, a plain numeric value
outside a joint's declared `range`, raising an error of a kind exported
from the joints module and naming the joint, the value, the range, the
unit and the node — by its path in the tree when the node is linked
under a root, and otherwise by its name and class, because a node bound
before any walker linked it has no path to name. A binding that is not a plain
number — a symbolic expression, a driver token — SHALL NOT be checked at
bind time, because its value is not known there; a joint with no
declared range, and a bound stated as `None`, SHALL accept any binding
on that side. A `Driver` bound to a joint
SHALL keep its own declared range, which is presentation metadata and
never a clamp, and the joint's range SHALL apply to the value that
reaches the joint.

A bound stated as a CALLABLE SHALL be applied, at the moment of
binding, to THE VALUE BEING BOUND, and the binding refused when that
value lies outside the pair so evaluated — the refusal naming the
evaluated bound as well as the joint, the value, the unit and the node,
and refusing likewise when the evaluated pair is reversed or is not a
number. A bound that is not satisfied at its own argument therefore
forbids every value and says so by name at the first binding. Under a
RUNNING root the same declaration is additionally a physical stop,
evaluated once per tick from the committed state, under the simulation
requirement "A declared range is a physical stop located inside the
tick"; under every other root a range refuses a binding and never
clamps or stops.

A bound stated as a `Bound` that reads other coordinates SHALL NOT be
applied at the moment of binding, because the coordinates it reads
are bound by the solver in an order the author does not state; the
binding SHALL be recorded on the open enumeration and JUDGED WHEN THAT
ENUMERATION CLOSES, after deferred relations have propagated, over the
values then bound: the reads resolved against the declarer, the
expression applied to the bound value and the read values, the pair
ordered, and the value checked inclusive. A value outside the pair so
evaluated SHALL raise the joint range error naming the node, the joint,
the value, the unit, the evaluated bound AND every coordinate the bound
read with the value it read. A read that holds no value or a symbolic
one at the close SHALL NOT be judged, on the rule a symbolic binding
already has. A coordinate a RUNNING simulation owns SHALL NOT be judged
by the enumeration: the run located its stop and committed inside it,
and one authority judges one binding. A binding made outside any
enumeration SHALL place the body and SHALL NOT be judged there, no pass
being open to record it on — exactly as a read of an unbound coordinate
made outside an enumeration is not recorded; it SHALL be judged at the
close of the next enumeration that binds the coordinate again.

#### Scenario: An out-of-range angle is refused by name

- **WHEN** a joint declaring `range=(-135, 135)` in degrees is bound to
  `170`
- **THEN** the binding raises an error naming the node's path, the
  joint, `170`, the range and `deg`, and the node carries no motion from
  that binding

#### Scenario: A symbolic binding is not checked

- **WHEN** the same joint is bound from an expression in the animation
  time whose values pass outside the range
- **THEN** the binding succeeds and publishes the expression, because
  the value is not known at bind time

#### Scenario: A binding inside the range is placed

- **WHEN** the same joint is bound to `-135` and then to `135`
- **THEN** both bindings succeed, the bounds being inclusive


#### Scenario: An open bound accepts anything on its side

- **WHEN** a joint declares `range=(0, None)` and is bound to `10000`,
  and then to `-1`
- **THEN** the first binding succeeds and the second is refused naming
  the joint, `-1` and the lower bound

#### Scenario: A bound reading other coordinates is judged when the enumeration closes

- **WHEN** an untimed root drives `plug.turn`, whose range is
  `(0, Bound(lambda turn, a, b: 90 * (abs(a) <= 0.05) * (abs(b) <= 0.05), reads=(p1.lift, p2.lift)))`,
  from a `turn` driver and the two lifts from a `feed` driver, and
  `set_state(turn=30, feed=0)` leaves a lift at `5`
- **THEN** the enumeration's close raises the joint range error naming
  `plug.turn`, `30`, the evaluated upper bound `0`, `p1.lift` and
  `p2.lift` with the values they held, whatever order the solver bound
  them in

#### Scenario: A bound reading other coordinates admits a possible pose

- **WHEN** the same root is bound with `set_state(turn=30, feed=20)`,
  which leaves both lifts at `0`
- **THEN** the enumeration closes without error and the plug's body
  carries the 30-degree turn

#### Scenario: A read holding no value is not judged

- **WHEN** a coordinate whose bound reads another is bound while that
  other coordinate is left unbound by the enumeration
- **THEN** the binding is placed and the enumeration closes without
  judging that bound

#### Scenario: A self-referential bound is evaluated at the value being bound

- **WHEN** a joint declaring
  `range=(lambda turn: 36 * floor(turn / 36), None)` is bound to `40`,
  and then to `36`, and then to `0`
- **THEN** every binding succeeds, because the lower bound evaluates to
  `36`, `36` and `0` respectively, and the body carries the motion of
  each

#### Scenario: A bound no value can satisfy is refused by name

- **WHEN** a joint declaring `range=(lambda turn: turn + 1, None)` is
  bound to any number
- **THEN** the binding is refused naming the joint, the value and the
  evaluated bound
