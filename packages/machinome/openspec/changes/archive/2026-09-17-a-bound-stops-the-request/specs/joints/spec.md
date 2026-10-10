## MODIFIED Requirements

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
tick"; under a CLOCKED root it is additionally a stop on a REQUEST'S
PATH, evaluated from the state the request starts at and clipping the
travel that request admits, under the simulation requirement "A bound
stops a clocked request on its path"; under every other root a range
refuses a binding and never clamps or stops.

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
and one authority judges one binding. On that same rule, a coordinate a
CLOCKED simulation compiled a constraint for SHALL NOT be judged by the
enumeration at the pose a REQUEST makes — neither at the moment of
binding nor at the close of that enumeration — because the clocked
simulation clipped the request at that bound and judges the constraint
itself, over the bank the request ends at, under the simulation
requirement "A bound stops a clocked request on its path". Every pose
that is NOT a request — construction, `state=`, `restore` — SHALL be
judged here as it is judged today. A binding made outside any
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

#### Scenario: A clocked request stops at the bound instead of being refused

- **WHEN** a clocked simulation's request would carry a coordinate declaring
  `range=(0, 9)` to `20`
- **THEN** the request admits only the travel that leaves the coordinate at
  `9`, the pose binds `9` without judging it here, no joint range error is
  raised, and the request reports the bound it met

#### Scenario: A pose that is not a request is judged here as before

- **WHEN** the same clocked model is constructed with a `state=` whose bank
  poses that coordinate at `20`
- **THEN** the binding is refused here, naming the node, the joint, `20` and
  the range, because a construction has no path to clip and a machine cannot
  be put where it cannot be
