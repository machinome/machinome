## ADDED Requirements

### Requirement: A realized node reads its resolved frames

The system SHALL provide `resolved_frames(node)`, importable from
`machinome.node.frames` beside `declared_frames`, documented in the
framework's API reference. Given a realized node, it SHALL return a
mapping from the name of every frame the node's class declares, in
declaration order, to that frame as it resolved against the node (see "A
frame resolves against its declarer at realization"): an origin `at` and
three unit directions `x`, `y`, `z`, each a tuple of three plain
numbers in the node's own rest frame, and a `rotation()` giving the 3×3
matrix, as three rows, whose columns are `x`, `y` and `z`. `at` SHALL be
three floats; a direction component within `1e-9` of `0`, `1` or `-1`
SHALL be that integer.

The read SHALL be exactly what a mate composes with: the same resolution
made once when the node was constructed, not a second one, so a function
of the node given as a frame argument SHALL NOT be called by the read.
Each read SHALL return a new mapping, and changing that mapping SHALL
change nothing the node or its mates use. Reading SHALL change no node,
no identity, no artifact and no published document.

A node whose class declares no frame SHALL read an empty mapping; a
frame a subclass removed by assigning `None` SHALL NOT appear. A child
placed by a mate SHALL read the frames its declared class declares.

The read SHALL be refused, raising `TypeError`:

- given a class, naming the class and saying a frame resolves against
  the instance that declares it — its arguments may read that instance's
  parameters or be a function of it — and that the declarations are read
  with `declared_frames`;
- given anything that is not a realized node — a child declaration read
  off a class body, a frame, a number —, naming its type and saying the
  read takes a realized node;
- given a realized node whose frames are not yet resolved — a read made
  from its own `check()`, or from a function given as one of its joint or
  frame arguments —, naming the class and saying a node's frames resolve
  after its `check()` and its joints.

Reading a frame as an attribute of an instance SHALL continue to yield
the declaration.

#### Scenario: A frame's numbers are read off the instance

- **WHEN** an assembly declaring `reach = Length(160)` and
  `elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))` is realized with
  `reach=150`, and `resolved_frames` reads it
- **THEN** the mapping holds `elbow_pin` alone, with `at` equal to
  `(0.0, 150.0, 68.0)`, `x` to `(1, 0, 0)`, `y` to `(0, 1, 0)` and `z`
  to `(0, 0, 1)`, while `declared_frames` of the class still reports the
  declaration with its `reach` token

#### Scenario: The default x is read, not restated

- **WHEN** a part declares `bore = Frame(z=(0, 1, 0))` and
  `yaw_bore = Frame(z=(0, 0, -1))`, neither stating `x`, and a realized
  part is read
- **THEN** `bore` reads `x = (0, 0, 1)` and `y = (1, 0, 0)`, and
  `yaw_bore` reads `x = (-1, 0, 0)` and `y = (0, 1, 0)`

#### Scenario: A stated x is read squared up

- **WHEN** a part declares `pin = Frame(z=(0, 0, 2), x=(1, 0, 1))` and a
  realized part is read
- **THEN** `pin` reads `z = (0, 0, 1)`, `x = (1, 0, 0)` and
  `y = (0, 1, 0)`

#### Scenario: The read is what the mate composes

- **WHEN** an upper arm declares `reach = Length(160)`,
  `elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))` and the child
  `art3 = Art3()`, `Art3` declaring
  `hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))`, states
  `elbow = art3.hinge.on(elbow_pin, Revolute(range=(-135, 135)))`, is
  realized with `reach=150` and rendered with `elbow` unbound, and the
  frames of the arm and of its child `art3` are read
- **THEN** `art3` reads `hinge` with `x = (1, 0, 0)`, `y = (0, 0, -1)`
  and `z = (0, 1, 0)`, and `art3`'s rest operations — a rotation of 90
  degrees about `(1, 0, 0)` and a translation of `(0, 231.5, 68)` — are
  the placement composed from the two reads as the fixed frame times the
  inverse of the moving frame

#### Scenario: A frame computed by a function is not recomputed

- **WHEN** a part declares `bore = Frame(at=lambda node: ...)` whose
  function counts its calls, and a realized part is read twice
- **THEN** both reads give the same origin and the count is what it was
  before the first read

#### Scenario: Changing a read changes nothing

- **WHEN** a key is removed from the mapping one read returned
- **THEN** a second read of the same node returns every frame, and a
  mate placed from that node's frames rests where it rested before

#### Scenario: A node declaring no frame reads nothing

- **WHEN** a leaf declaring no frame is realized and read, and a
  subclass assigning `foot = None` under a base declaring `hinge` and
  `foot` is realized and read
- **THEN** the first reads an empty mapping and the second reads `hinge`
  alone

#### Scenario: A class has no resolved frames

- **WHEN** `resolved_frames` is given the assembly class of "A frame's
  numbers are read off the instance", or its child declaration read off
  the class body
- **THEN** it raises `TypeError`; for the class naming the class and
  `declared_frames`, for the declaration naming its type and saying a
  realized node is read

#### Scenario: Frames are not read before they resolve

- **WHEN** a part declaring a frame calls `resolved_frames(self)` in its
  `check()`
- **THEN** realizing the part raises `TypeError`, naming the class and
  saying its frames resolve after `check()` and its joints

### Requirement: A mate's ends and freedom are read off the class

A mate SHALL be readable, off the class and without constructing an
instance, as the object `declared_mates(cls)` reports under its name,
with these reads documented in the framework's API reference:

- `name`, the attribute the mate is assigned to — also the name of its
  coordinate on the assembly and of the joint it gives the child;
- `moving`, the moving end, whose `written` SHALL be
  `'<child>.<frame>'` as the class body writes it;
- `fixed`, the fixed end as the class body writes it: for a frame of a
  child, a reference whose `written` SHALL be `'<child>.<frame>'`; for a
  frame of the assembly itself, written by its bare name, that `Frame`
  declaration, whose `name` SHALL be its attribute;
- `freedom`, the `Revolute` written in the statement, whose `axis` SHALL
  be `None` when no axis is stated and otherwise the three numbers as
  written, not normalized; whose `anchor_written` SHALL say whether `at`
  was written; whose `at` SHALL be the three numbers as written when
  `anchor_written` is true, and SHALL NOT be the mate's anchor when it is
  false, the anchor then being the moving frame's origin; whose `range`
  SHALL be as written, or `None`; and whose `unit` SHALL be as written,
  or `'deg'`.

The line a mate turns its child about SHALL be readable from these reads
and the moving child's resolved frames alone: `freedom.axis` when it is
not `None`, else the moving frame's resolved `z`; through `freedom.at`
when `anchor_written` is true, else through the moving frame's resolved
`at`. Reading any of them SHALL change nothing.

#### Scenario: Thor's elbow is read back

- **WHEN** `declared_mates` of the upper arm of "Thor's elbow is one
  statement" is read under `elbow`
- **THEN** its `name` is `elbow`, its `moving.written` is
  `'art3.hinge'`, its `fixed` is the upper arm's `elbow_pin` frame with
  `name` `elbow_pin`, and its freedom's `axis` is `None`,
  `anchor_written` false, `range` `(-135, 135)` and `unit` `'deg'`

#### Scenario: A fixed end on a child is read as written

- **WHEN** an assembly states `yaw = housing.origin.on(base.seat,
  Revolute())` and `declared_mates` is read under `yaw`
- **THEN** its `moving.written` is `'housing.origin'` and its
  `fixed.written` is `'base.seat'`

#### Scenario: A stated line is read as written

- **WHEN** the housing of "A freedom states the line across its
  attachment frame" is read under `shoulder`
- **THEN** its freedom's `axis` is `(0, 0, 1)`, `anchor_written` is true
  and `at` is `(0, 0, 0)`, the child's own origin

#### Scenario: A left-out anchor is not the child's origin

- **WHEN** an assembly states
  `swing = part.hinge.on(pin, Revolute(axis=(0, 0, 2)))`, `part`
  declaring `hinge = Frame(at=(0, 0, 5))`, and the mate is read
- **THEN** its freedom's `axis` is `(0, 0, 2)` as written and
  `anchor_written` is false, and the installed joint's anchor on a
  realized `part` is `(0, 0, 5)`, the moving frame's resolved origin,
  not `(0, 0, 0)`

#### Scenario: The reference lists the reads

- **WHEN** a reader opens the framework's API reference at "Frames and
  mates"
- **THEN** it lists `resolved_frames`, the resolved frame with
  `rotation`, and the mate with its `name`, `moving`, `fixed` and
  `freedom`, beside `Frame`, `declared_frames` and `declared_mates`
