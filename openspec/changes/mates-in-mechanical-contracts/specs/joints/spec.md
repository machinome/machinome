## MODIFIED Requirements

### Requirement: An assembly constrains an existing descendant joint

The system SHALL accept `path.to.joint.constrain(range=(lo, hi))` in an
assembly class body as an additional constraint on that existing scalar
joint. The target SHALL be an explicitly named one-coordinate joint reached
through child declarations, or a moving mate named bare in its declaring
assembly or by a path through declared children. A mate target SHALL resolve
to its existing generated child joint; the mate SHALL not become a joint of
its declaring assembly. The constraint SHALL preserve its target's
owner, axis, anchor, unit, placement frame, joint order, source geometry,
qualified coordinate path and original range. It SHALL create no new joint,
input or retained value.

Each side SHALL use the existing range-side vocabulary: `None`, a numeric
or parameter-derived value, an expression of the target's own coordinate,
or `Bound(expression, reads=(...))`. Structural values and read references
SHALL resolve against the assembly declaring the additional constraint.
Its implicit first expression argument SHALL remain the target coordinate.

Declarations SHALL be recorded in written order and inherited additively;
this surface SHALL provide no removal or named-replacement operation.
Each instance SHALL resolve its own endpoints. Invalid inherited
paths SHALL be refused rather than silently ignored or redirected.

Targets that are a rigid mate, whole node, input, state, plain or derived port, grouped
end, broadcast, or multi-coordinate joint/component SHALL be refused by name.
Statements outside an assembly class body, malformed or wholly unbounded
ranges, out-of-scope references and reads of the target itself SHALL be
refused. Existing duplicate and unused read checks SHALL remain effective.

#### Scenario: Curta's ancestor states an installed locking obstacle

- **WHEN** an assembly constrains `main_drive.crank.turn` with a bound reading
  `transmission.result.ones.turn`
- **THEN** the target and read resolve to those actual descendant joints,
  and the crank's stationary siblings, node tree and controls remain unchanged

#### Scenario: Two instances do not share a resolved constraint

- **WHEN** two instances of the same nested assembly have different read
  values and constraints
- **THEN** each constraint evaluates its own instance's coordinates and
  neither instance changes the other's joint metadata or admitted travel

#### Scenario: An inherited constraint cannot vanish after a child override

- **WHEN** a subclass replaces a constrained child with a class lacking the
  targeted joint
- **THEN** the system refuses the invalid constraint by its target path
  instead of constructing an unconstrained machine

#### Scenario: Inherited constraints remain effective

- **WHEN** a subclass adds another constraint on a descendant already
  constrained by its base
- **THEN** both constraints and the target's own range remain effective

#### Scenario: Unsupported targets and self reads are diagnosed

- **WHEN** a constraint targets a plain port or repeated broadcast, or names
  its own target in `reads`
- **THEN** declaration is refused with the offending target/read identified
  and no fake banked coordinate is introduced

#### Scenario: A declaring assembly constrains its mate

- **WHEN** an assembly declares a moving mate `turn` and states `turn.constrain(range=(0, 90))`
- **THEN** the added limit intersects the generated child's joint range and changes no binding address or placement

#### Scenario: An ancestor constrains a nested mate

- **WHEN** an ancestor states `unit.mount.turn.constrain(range=(Bound(limit, reads=(pawl.turn,)), None))` on a moving mate
- **THEN** the target is the existing generated child joint, reads resolve in the ancestor, and the existing additive intersection semantics apply

#### Scenario: A rigid mate cannot be constrained

- **WHEN** a constraint targets a rigid mate
- **THEN** the system refuses it by name because it owns no coordinate


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
declarations, or a driver of the declaring class, including a moving mate reference
identifying its generated child joint — and SHALL be
refused at CLASS DEFINITION by the same rules: a declaration held in a
list, a repeated child, a child whose class declares no joint or
several, a driver read sideways, and, additionally, a read that names
the bounded coordinate itself. A Bound returned by a mate's whole-range
function SHALL receive these same reference and self-read checks when the
returned pair becomes available at realization; read values SHALL still
remain unresolved until ordinary evaluation. Under a RUNNING root a read SHALL
additionally be a coordinate the run banks, and under a CLOCKED root a
declared driver, a declared state or a joint coordinate a chain from the
bank reaches — a read of a plain port or a derived coordinate being
refused at simulation construction under the simulation requirements "A
range bound may read other coordinates" and "A bound stops a clocked
request on its path"; under every other root such a read is resolved and
judged like any other. A
`Bound`'s reads SHALL be resolved against the joint's DECLARER — the
node itself for a class-declared joint, the declaring parent for a
site-declared one, or the declaring assembly for a joint generated by a
mate — where the values
are needed and never at realization: at the close of the enumeration
that bound the coordinate untimed, and at simulation construction
under a running or a clocked root. A callable given as the whole `range` and a
callable or `Bound` given as one of its bounds SHALL be told apart by
POSITION and SHALL keep their separate meanings. A site-declared
joint's callable SHALL be able to read the declaring parent's resolved
parameters and flags and anything that parent's own `__init__` has set,
and SHALL NOT be able to read the child's placement, which does not exist
yet, or anything the parent's `render()` produces. A joint on a
`.repeat()` declaration SHALL be resolved once per copy against the same
declaring parent, so every copy carries identical resolved arguments; a
copy's own position SHALL NOT be handed to the callable.
Geometric argument resolutions SHALL yield values in the DECLARER's
frame and SHALL be complete at realization. For a mate-generated joint,
its axis and anchor SHALL instead retain their moving child's own rest
frame under the mates requirements: the Bound read scope and the receiver
of a mate's freedom factory are the declaring assembly, not a change of
geometric frame. No joint argument
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

## ADDED Requirements

### Requirement: Mechanical contract mate references identify their existing generated joint

A Bound read SHALL accept a moving mate declared on the body stating the Bound or reached through declared children. For Bound reads and constrain targets, the mate reference SHALL identify its existing generated child joint's scalar coordinate, including nested paths. This SHALL preserve the mate's existing public coordinate, relation/wiring behavior and sole binding route. The system SHALL refuse a rigid mate by name because it owns no coordinate. Scope, inherited-path compatibility, repeated/list-held path, unused read and simulation banking checks SHALL remain effective. Self-read and duplicate-read checks SHALL compare the resolved physical coordinate: a mate reference and a reference to its generated child joint SHALL NOT evade those checks by having different written names.

#### Scenario: A Bound reads a nested moving mate

- **WHEN** a Bound names a moving mate reached through nested assembly children
- **THEN** its read identifies the existing generated child joint, within the declaring subtree, without creating a new coordinate

#### Scenario: Alias names cannot hide a self read

- **WHEN** a Bound constraining a moving mate reads that same mate or its generated child joint under another reachable spelling
- **THEN** declaration or resolved compilation refuses the self read and identifies the offending reference

#### Scenario: Alias names cannot duplicate a read

- **WHEN** one Bound lists a moving mate and its generated child joint as separate reads
- **THEN** the system refuses the duplicate physical coordinate rather than providing it twice to the expression

#### Scenario: Invalid inherited mate references do not disappear

- **WHEN** a subclass replaces a referenced child so that a Bound read or constraint no longer reaches a compatible moving mate and generated joint
- **THEN** the invalid inherited reference is refused by name instead of becoming inert or silently selecting another coordinate

#### Scenario: Rigid mate reads are refused

- **WHEN** a Bound names a rigid mate in reads
- **THEN** it is refused by name because the mate owns no coordinate
