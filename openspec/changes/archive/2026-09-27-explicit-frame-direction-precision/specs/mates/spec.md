## MODIFIED Requirements

### Requirement: A frame resolves against its declarer at realization

Each of a frame's three arguments SHALL follow the rule a joint's
arguments follow: a sequence of three components, each a number, a token
of a parameter the declaring class declares or a formula over such
tokens; or, for the whole argument, a callable of one argument called
with the realized declaring node. A frame SHALL be resolved per instance
when its declaring node is constructed — after the node's parameters are
resolved and its `check()` has run, and before any of its children is
realized, the moment a class-declared joint's arguments are resolved —
so a frame that cannot resolve is refused naming the class, the frame
and the argument, whether or not any mate names it.

A resolved frame SHALL be an origin and three unit directions `x`, `y`,
`z`: `z` the declared `z` normalized; `x` the declared `x` with its
component along `z` removed, then normalized; `y` equal to `z × x`.
Neither `z` nor `x` need be written as a unit vector.

When BOTH `x` and `z` are explicitly supplied, resolution SHALL preserve
full floating-point precision of the normalized `z`, projected and normalized
`x`, and cross-product `y`, without snapping direction components to `0`, `1`
or `-1`. This includes literal, parameter/formula and callable vectors, and
an explicitly supplied `z=(0, 0, 1)`. Supplying `x` while omitting `z` SHALL
retain the previous snapped path, as SHALL omitting `x` (including `x=None`).
On that path, direction components within `1e-9` of `0`, `1` or `-1` SHALL be
that integer. No new public argument SHALL select this behavior. Projection,
normalization and zero/parallel refusal thresholds SHALL remain unchanged.
This precision rule SHALL NOT alter final mate rotation-angle/axis snapping.

When `x` is omitted and `z` lies along a principal axis, `x` SHALL be
the next principal axis in right-hand order — the rule a wrapped
marking's derived zero follows: `+X` for `+Z`, `+Y` for `+X`, `+Z` for
`+Y`, and the negated axis for a negated `z` (`-X` for `-Z`). When `x`
is omitted and `z` does not lie along a principal axis, the frame SHALL
be refused, naming the frame and saying that `x` must be stated, because
`x` fixes the zero of a revolute mate and a derived one would be
invisible in the declaration.

A frame SHALL be refused, naming the class, the frame and the argument,
when a component does not resolve to a number, when `z` has no length,
or when `x` is parallel to `z`.

#### Scenario: A frame reads its declarer's parameters

- **WHEN** a part declaring `reach = Length(160)` and
  `pin = Frame(at=(0, reach, 68), z=(0, 0, 1))` is realized with
  `reach=150`
- **THEN** the resolved frame's origin is `(0, 150, 68)`

#### Scenario: A frame may be computed from the realized node

- **WHEN** a part declares `bore = Frame(at=lambda node: node.built.bore)`
- **THEN** each realized instance resolves the origin by calling the
  function with that instance

#### Scenario: The x axis follows the principal rule when omitted

- **WHEN** a frame declares `z=(0, 1, 0)` and no `x`
- **THEN** it resolves with `x = (0, 0, 1)` and `y = (1, 0, 0)`

#### Scenario: The x axis is squared up against z

- **WHEN** a frame declares `z=(0, 0, 2)` and `x=(1, 0, 1)`
- **THEN** it resolves with `z = (0, 0, 1)`, `x = (1, 0, 0)` and
  `y = (0, 1, 0)`

#### Scenario: A diagonal z must state x

- **WHEN** a frame declares `z=(0, 1, 1)` and no `x`
- **THEN** realizing the declaring node raises, naming the class and the
  frame and saying `x` must be stated

#### Scenario: A degenerate frame is refused

- **WHEN** a frame declares `z=(0, 0, 0)`, or `z=(0, 0, 1)` with
  `x=(0, 0, 5)`
- **THEN** realizing the declaring node raises, naming the class, the
  frame and the argument

#### Scenario: Curta's explicit attachment directions retain precision

- **WHEN** a frame explicitly supplies
  `x=(-3.2740476996195866e-13, 3.6046641539722035e-10, 1)` and
  `z=(.9999983500045653, .0018165869499783267, -3.2740476996195866e-13)`
- **THEN** its directions are normalized, projected and crossed without
  replacing genuine tiny components by snapped integers

#### Scenario: Explicit expressions retain the same direction precision

- **WHEN** both `x` and `z` are supplied as parameter/formula vectors or
  whole-vector callables resolving to near-principal directions
- **THEN** the same unsnapped normalization/projection rule applies per instance

#### Scenario: Explicit x with default z keeps the old snapped path

- **WHEN** a frame supplies `x=(1, 3e-10, 0)` but omits `z`
- **THEN** it retains snapped directions, while explicitly supplying the same
  default `z=(0, 0, 1)` with that x retains its normalized tiny component

#### Scenario: Omitted x retains principal inference

- **WHEN** x is omitted or None and z has near-principal components inside
  the existing snap threshold
- **THEN** the prior snapped principal direction and inferred x remain, and
  nonprincipal z outside that rule is still refused for lacking x


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
three floats. When both direction vectors were explicitly supplied, their
normalized/projected/cross-product components SHALL retain full floating-point
precision as required by frame resolution; otherwise a direction component
within `1e-9` of `0`, `1` or `-1` SHALL be that integer.

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
  after its `check()` and its joints. From such a function the refusal
  reaches the author as the argument rule reports any error a function
  raises, quoting it.

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

#### Scenario: The precise readout is the basis mates actually use

- **WHEN** a realized node's frame explicitly supplies both near-principal
  directions and a mate composes it with a nonidentity moving/fixed endpoint
- **THEN** `resolved_frames` exposes the same unsnapped resolved basis used in
  that actual mate composition, not a separately prettified or recomputed one
- **AND** the emitted mate rotation retains its existing final `1e-9` snap

