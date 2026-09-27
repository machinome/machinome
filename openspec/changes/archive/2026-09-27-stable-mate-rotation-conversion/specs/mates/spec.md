## MODIFIED Requirements

### Requirement: A mate places the moving child at rest

At realization the system SHALL place the moving child, at rest, so that
its moving frame coincides with the fixed frame, whole triad onto whole
triad — origin on origin, `x` on `x`, `y` on `y` and `z` on `z`. Its rest
placement in the assembly SHALL be the fixed frame's owner placement,
composed with the fixed frame, composed with the inverse of the moving
frame, where the owner placement is the identity for a frame of the
declaring assembly and the fixed child's rest placement for a frame of a
child. `x` therefore fixes the rest attitude and the zero of the mate's
coordinate, not only its line.

The placement SHALL be applied as ordinary rest operations on the moving
child — one rotation, omitted when the rotation is the identity, then
one translation, omitted when it is zero — exactly as if the author's
`render()` had written them, after the author's `render()` has returned,
once per instance, and composing outside every joint the child's own
class declares. A rotation axis component and a rotation angle within
`1e-9` of a whole number SHALL be that whole number, as a joint's
normalized axis is snapped; the translation SHALL be what the arithmetic
gives.

Matrix-to-axis-angle conversion SHALL preserve the represented rest rotation,
subject to the unchanged documented `1e-9` snap, without amplifying
cancellation residue into phantom axis components. Signed
principal rotations beyond 90 degrees SHALL retain their principal axis;
genuine small axis components outside the existing snap SHALL remain present.
Near and exact half-turn rotations SHALL remain numerically stable, and
symmetric equal-component half-turns SHALL retain equal axis components. This
SHALL NOT enlarge the snap or alter caller tolerances.

A child a mate places SHALL NOT also be placed by the assembly's
`render()`: a rotation or translation the `render()` applies to it SHALL
be refused, naming the assembly, the child and the mate, because a
placement is stated once. A `render()` that re-runs on every binding
SHALL NOT accumulate a mate's placement.

A fixed child's rest placement that does not evaluate to numbers SHALL
refuse the mate at realization, naming the mate and the child.

#### Scenario: Thor's elbow rests where Thor's render puts it

- **WHEN** the upper arm of "Thor's elbow is one statement" is realized
  and rendered with its coordinate unbound
- **THEN** the forearm root's rest operations are a rotation of 90
  degrees about `(1, 0, 0)` followed by a translation of
  `(0, 241.5, 68)`, equal in kind, order and value to the operations
  Thor's hand-written `render()` applies

#### Scenario: Thor's shoulder rests where Thor's render puts it

- **WHEN** a housing declares
  `shoulder_pin = Frame(at=(0, 0, 123), z=(0, 1, 0))`, its child `art2`
  declares `bore = Frame(at=(0, 0, 68), z=(0, 0, 1), x=(0, 1, 0))`, and
  the housing states `shoulder = art2.bore.on(shoulder_pin, Revolute())`
- **THEN** the child rests turned 180 degrees about
  `(0, 0.7071…, 0.7071…)` and translated by `(0, -68, 123)`, within
  `1e-9` of Thor's hand-written placement

#### Scenario: x fixes the rest attitude

- **WHEN** the elbow of "Thor's elbow is one statement" is declared with
  the forearm root's `x` omitted
- **THEN** the two frames' `z` lines still coincide and the forearm root
  rests turned 120 degrees about `(1, 1, 1)/√3` rather than 90 degrees
  about `(1, 0, 0)`

#### Scenario: A fixed end on a still child uses the child's placement

- **WHEN** an assembly places the child `base` with `translate(0, 0, 10)`
  in `render()`, `base` declaring `seat = Frame(at=(0, 0, 79))` and no
  joint, and states `yaw = housing.origin.on(base.seat, Revolute())`
  with `housing` declaring `origin = Frame()`
- **THEN** the housing rests translated by `(0, 0, 89)`

#### Scenario: A mated child cannot be placed by hand

- **WHEN** an assembly states a mate on `art3` and its `render()` calls
  `self.art3.translate(...)`
- **THEN** rendering raises, naming the assembly, `art3` and the mate

#### Scenario: A re-running render does not stack the placement

- **WHEN** an assembly whose `render()` reads a driver states a mate, and
  it is rendered under three successive bindings
- **THEN** the moving child carries the mate's rest placement exactly
  once after each

#### Scenario: Curta's negative principal rest rotation stays principal

- **WHEN** a mate's rest matrix is a pure Z rotation of -95.6 degrees, as in
  Curta selector 6
- **THEN** its emitted rotation has zero X/Y axis components and represents
  the same signed Z rotation, without the phantom approximately 5e-9 components
- **AND** the unchanged caller physical-basis comparison meets its existing
  tolerance

#### Scenario: Genuine small components are not erased

- **WHEN** a proper rest rotation beyond 90 degrees has a genuine small axis
  component outside the existing 1e-9 snap
- **THEN** conversion preserves that component rather than treating it as
  cancellation noise, and reconstructs the rotation within floating-point
  accuracy subject to the unchanged documented snap of axis components and angle

#### Scenario: Near and exact half turns retain their rotation

- **WHEN** rest rotations approach or reach 180 degrees about principal or
  mixed-sign oblique axes, including symmetric equal-component axes
- **THEN** the emitted rotations reconstruct the represented matrices within
  floating-point accuracy subject to the unchanged documented snap of axis
  components and angle, and preserve equal components in symmetric half turns
