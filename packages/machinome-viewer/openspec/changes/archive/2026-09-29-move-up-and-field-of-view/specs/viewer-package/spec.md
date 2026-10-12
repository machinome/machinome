## ADDED Requirements

### Requirement: A scripted view may roll and change its field of view

A host changing the view of a loaded viewer SHALL be able to supply, with
the camera position and target, an up direction, a vertical field of view
in degrees, both, or neither. What it omits SHALL keep its current value.
The viewer SHALL adopt and draw the whole view before returning, without
reloading geometry or changing machine time, driver values, assembly
visibility or focus. Reading the view back SHALL report camera, target, up
direction and field of view, as copies the viewer does not later modify,
with the up direction as the host supplied it.

The viewer SHALL refuse, by name and leaving the previous view intact, an
up direction that is not three finite numbers, is zero, or is parallel to
the direction from camera to target, and a field of view that is not a
finite number strictly between 0 and 180 degrees. An adopted up direction
and field of view SHALL persist through refocusing, in-place updates and
reload, and a maker orbiting by pointer SHALL orbit about the adopted up
direction.

#### Scenario: A shot tightens on the saw

- **WHEN** a film host sets the same camera and target with a smaller field
  of view
- **THEN** the captured frame shows the model larger, and the view read back
  reports the new field of view

#### Scenario: A shot rolls to follow a part

- **WHEN** a host sets a view with a new up direction
- **THEN** the frame is drawn rolled to that direction, and the view read
  back reports it as supplied

#### Scenario: An omitted value is kept

- **WHEN** a host sets a new field of view and then a new camera position
  without one
- **THEN** the second frame keeps the field of view the first set

#### Scenario: An impossible roll is refused

- **WHEN** a host supplies an up direction along the line from camera to
  target, a zero up direction, or a field of view of 0 or 180 degrees
- **THEN** the call fails naming the value, and the view and frame are
  unchanged

#### Scenario: Refocusing keeps the roll

- **WHEN** a host sets an up direction and then focuses a subassembly
- **THEN** the refocused frame keeps the adopted up direction

#### Scenario: A maker orbits about the new up

- **WHEN** a host adopts a new up direction on an interactive viewer and a
  maker drags to orbit horizontally
- **THEN** the camera turns about the adopted up direction, keeping its
  angle to it
