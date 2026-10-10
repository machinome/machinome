## MODIFIED Requirements

### Requirement: A control says which part a person presses or turns

The system SHALL let an assembly declare a `controls` mapping beside
`instructions`, of display name to CONTROL, stating how a person issues
a movement request by touching a part of the machine:

- `Button(part, instruction, *, coordinate=None)` — a press on `part`
  submits the named instruction;
- `Turn(part, input, *, coordinate=None)` — a drag about the selected
  rotational coordinate is a sequence of relative moves on `input`; and
- `Slide(part, input, *, coordinate=None)` — a drag along the selected
  translational coordinate is a sequence of relative moves on `input`.

A control SHALL move nothing itself. It names a request the run already
accepts, and every rule about ownership, admission, stops and outcomes
SHALL be the one `trigger`, `move` and `rate` already state. A control
SHALL carry no state and SHALL NOT repeat an instruction's definition.

`part` SHALL be a NODE, named in the class body the way a relation's
path ends are named — a declared child, or a path of declared children
and child declarations through one (`units.input.dial`). A `Turn` or `Slide` control's
`input` SHALL be a `Driver` declared on the class that declares the
control; a driver of a child is named by declaring the control on the
child, exactly as an instruction over a child's driver is.

Controls declared on any node in the tree SHALL be discoverable by
QUALIFIED name — the declaring node's instance path joined with the
declared name, a root-declared control keeping its bare name — and a
`Button`'s instruction reference SHALL qualify through that same path,
so it equals a key of the tree's instruction table by construction.

Without explicit selection, a control's COORDINATE SHALL be the one owned
by the nearest ancestor-or-self of the part that declares a joint whose
coordinate the run banks. The joint's declaring node SHALL be the node that
coordinate poses.

An explicit `coordinate` SHALL name one existing single-coordinate joint,
using its declaration or a declaration path from the class declaring the
control. The joint SHALL pose the touched part or one of its ancestors in
that same tree, and its coordinate SHALL be run-banked. Selection SHALL
permit independently controlled sliding and turning joints on the same
body without changing the body, its placement, or the run program.
`Button` SHALL accept either a translational or rotational selected joint.
Omitting selection SHALL preserve the existing ambiguity refusal.

Each of the following SHALL be REFUSED, naming the facts a reader can
find in the model:

- a `controls` value that is not a mapping of names to controls, or an
  entry that is not a control — refused AT CLASS DEFINITION naming the
  entry and the reservation of the name;
- a `part` that is not a node reference — a coordinate, a driver, a
  repeated child, a list-held child or a plain value — refused where it
  is written, naming what was written;
- a `part` whose first segment is not a child the DECLARING class
  declares — refused at class definition, naming the class and the
  control;
- a `Turn` or `Slide` whose `input` is not a `Driver` declared on the declaring
  class — refused at class definition, listing the drivers that class
  declares;
- a `Button` whose instruction is not a declared instruction — refused
  when the tree is enumerated, listing the known qualified instruction
  names;
- a part no run-owned coordinate poses — refused naming the part and
  saying nothing the run owns moves it;
- a control without explicit selection whose nearest posing node declares
  MORE THAN ONE joint, or any selected joint owning MORE THAN ONE coordinate
  — refused naming them and saying a control names one coordinate;
- an explicit coordinate that is not a joint declaration/reference, is not
  run-banked, or does not pose this part or an ancestor in this tree —
  refused naming the control, part and selected reference;
- a `Turn` whose coordinate's domain is not `rotational`, or a `Slide`
  whose coordinate's domain is not `translational` — refused naming the
  actual and required domains;
- a `Turn` or `Slide` whose `input` is not among the inputs that reach its
  coordinate through the compiled program — refused naming the
  coordinate and the inputs that DO reach it;
- a control under a root that does not declare `Time.running()` —
  refused naming the declaring class, the control and `Time.running()`.

#### Scenario: A control is declared beside the instructions

- **WHEN** a running root declares
  `instructions = {'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0)}`
  and
  `controls = {'units dial': Button(units.dial, 'Add one'),
  'turn units': Turn(units.dial, units_entry)}`,
  where `units` declares `turn = Revolute(axis=(1, 0, 0))` and holds the
  leaf `dial`
- **THEN** the simulation is constructed, both controls are discovered
  under their bare names, each names the part `units.dial`, the
  coordinate `units.turn` and the joint node `units`, and nothing about
  the run's bank, edges or identity differs from the same root declaring
  no controls

#### Scenario: A control on a child qualifies through its path

- **WHEN** a running root holds `column`, an assembly that declares both
  `'Add one'` and `controls = {'dial': Button(arbor.dial, 'Add one')}`
- **THEN** the control is discovered as `column.dial`, its instruction
  reference is `column.Add one` — a key of the tree's instruction table
  — and its part is `column.arbor.dial`

#### Scenario: A misspelt part is refused where it is written

- **WHEN** a class body writes `Button(units.dail, 'Add one')` and
  `units`'s class declares no `dail`
- **THEN** class definition raises naming `units.dail`, saying that
  class declares no port, joint or child of that name, and listing what
  it does declare

#### Scenario: A part of another class is refused at class definition

- **WHEN** a class declares `controls` whose part's first segment is a
  child declaration some OTHER class holds
- **THEN** class definition raises naming the declaring class, the
  control's name, and that a control's part is walked from the assembly
  that declares it

#### Scenario: A coordinate is not a part

- **WHEN** a class body writes `Turn(units.turn, units_entry)`, naming
  the joint rather than the body it moves
- **THEN** declaration raises saying a control names a PART — a node
  whose geometry a hand touches — not a coordinate

#### Scenario: An input of another class is refused

- **WHEN** a class declares `Turn(units.dial, other_entry)` where
  `other_entry` is a `Driver` that class does not declare
- **THEN** class definition raises naming the driver and listing the
  drivers the declaring class does declare

#### Scenario: A button names an instruction that is not declared

- **WHEN** a running root declares `Button(units.dial, 'Add two')` and
  no instruction of that qualified name exists
- **THEN** construction is refused naming `Add two` and listing the
  known qualified instruction names

#### Scenario: A part nothing run-owned moves is refused

- **WHEN** a running root declares `Button(frame, 'Add one')` where
  `frame` is a leaf the root holds and no ancestor-or-self of it
  declares a joint
- **THEN** construction is refused naming `frame` and saying nothing the
  run owns moves that part

#### Scenario: A turn on a coordinate that does not turn is refused

- **WHEN** a running root declares `Turn(carriage.plate, feed)` and
  `carriage` declares `travel = Prismatic(...)`
- **THEN** construction is refused naming `carriage.travel`, its
  `translational` domain, and that a turn is about a rotational
  coordinate

#### Scenario: A turn whose input does not reach the part is refused

- **WHEN** a running root's `tens.turn` is reached by `tens_entry` and
  `units_entry` while `units.turn` is reached by `units_entry` alone,
  and the root declares `Turn(units.dial, tens_entry)`
- **THEN** construction is refused naming `units.turn` and listing
  `units_entry` as the input that reaches it

#### Scenario: A dial two inputs reach is bound to the one the author names

- **WHEN** the same root declares `Turn(tens.dial, tens_entry)`
- **THEN** it is admitted, its coordinate is `tens.turn`, and its input
  is `tens_entry` — the other input that reaches that coordinate having
  no bearing on the gesture

#### Scenario: A joint owning several coordinates is refused

- **WHEN** a running root declares a control on a part whose nearest
  posing node declares `pose = Free(...)`
- **THEN** construction is refused naming the joint, the coordinates it
  owns, and that a control names one coordinate

#### Scenario: A control without a running root is refused

- **WHEN** a root declaring no time base, or `Time(loop=2.0)`, declares
  a `controls` table and a simulation is constructed over it or its
  document is published
- **THEN** each is refused naming the declaring class, the control and
  `Time.running()`

#### Scenario: A controls attribute that is not a control table is refused

- **WHEN** a node class declares `controls = {'speed': 3}`
- **THEN** class definition raises naming the entry and saying
  `controls` names the machine's controls on a node class

#### Scenario: A selector is handled along its sliding joint

- **WHEN** a running root declares `Slide(selector.knob, setting)` and
  setting reaches the selector's single prismatic joint
- **THEN** construction admits the control with that coordinate and input,
  and the control neither moves the part nor changes the program's identity

#### Scenario: One body can be lifted and turned independently

- **WHEN** a crank declares single-coordinate revolute and prismatic joints
  and its controls explicitly select turn for a Turn and lift for a Slide
- **THEN** both controls are admitted on the same body, each resolving to its
  selected coordinate and the input that reaches it

#### Scenario: Ambiguity is not resolved by guessing

- **WHEN** the same two-joint crank declares a control without selection
- **THEN** construction is refused naming both joints and the ambiguous control

#### Scenario: A press can request movement of a sliding part

- **WHEN** a Button names a selector with one prismatic joint and a declared
  instruction requesting one detent
- **THEN** construction admits it and the instruction is the same request
  the run accepts through its normal instruction interface

#### Scenario: Selection cannot reach sideways

- **WHEN** a control on a crank explicitly selects a carriage joint that
  poses neither the crank nor any ancestor of it
- **THEN** construction refuses the control naming the part and selected joint

#### Scenario: An explicit ancestor coordinate remains reachable

- **WHEN** a touched knob sits beneath a jointed child on a carriage, and
  its Slide explicitly selects the carriage's prismatic joint
- **THEN** construction admits that ancestral coordinate instead of
  silently selecting the nearer child's different joint

#### Scenario: Selecting a joint does not unpack a multi-coordinate joint

- **WHEN** a control explicitly selects a Free joint
- **THEN** construction refuses it naming the joint and its multiple coordinates

#### Scenario: A slide cannot masquerade as a turn

- **WHEN** a Slide selects a rotational joint
- **THEN** construction is refused naming the coordinate's rotational domain
  and the required translational domain

#### Scenario: Sliding cannot bypass a stop or change another control

- **WHEN** a request submitted through a sliding control meets a declared bound
  dependent on a second mechanism
- **THEN** the run admits exactly the movement the same ordinary move request
  admits, reports the same outcome, and does not reposition that second mechanism

