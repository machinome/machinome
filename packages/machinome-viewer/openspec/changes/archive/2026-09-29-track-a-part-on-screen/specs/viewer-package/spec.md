## ADDED Requirements

### Requirement: A host reads where any part stands on screen

The mount handle SHALL answer, for any assembly path of the loaded tree, a
part or a subassembly, the on-screen rectangle enclosing its visible
geometry and a point at which its surface is the nearest visible surface,
for the pose and camera the host last set. It SHALL answer this whether or
not the document declares controls. Positions SHALL be in the same
coordinates and units as the positions reported for declared controls, and
the rectangle and point SHALL be computed by the same rule the controls
listing uses, so a control's part and the same path report the same
rectangle and point.

The answer SHALL be nothing when no geometry under the path is visible,
because the host hid it, focused elsewhere, or it has none, or when all of
it is outside the viewer's canvas; the point alone SHALL be nothing when
no probe of the bounded search finds the path's surface in front. An
unknown or ambiguous path SHALL be refused with an error naming the path.
Reading SHALL NOT draw a frame, change the view, the pose, visibility or
any material, or notify assembly listeners.

#### Scenario: An arrow follows a turning wheel

- **WHEN** a film host sets a time and a view on a document that declares
  no controls and asks where a part stands on screen
- **THEN** it receives a rectangle around that part and a point on it, and
  after the host sets a later time the answer moves with the part

#### Scenario: A subassembly is one target

- **WHEN** a host asks for a path naming a subassembly
- **THEN** the rectangle encloses the visible geometry of all its parts

#### Scenario: A hidden part is not on screen

- **WHEN** a host hides a path and asks where it stands
- **THEN** the answer is nothing

#### Scenario: A declared control and its part agree

- **WHEN** a document declares a control on a part and a host asks both for
  the controls listing and for that part's path
- **THEN** both report the same rectangle and the same point

#### Scenario: A misspelt path is refused

- **WHEN** a host asks for a path the tree does not have
- **THEN** the call fails with an error naming that path

#### Scenario: Reading draws nothing

- **WHEN** an on-demand viewer is asked where parts stand, any number of
  times, between two host changes
- **THEN** no frame is drawn by those reads and the next captured frame is
  the one the host's last change drew

### Requirement: A host projects a world point onto the screen

The mount handle SHALL answer the on-screen position of a point given in
the scene's world coordinates, the coordinates a host gives camera and
target in, for the current camera, in the same coordinates and units as
the positions of parts. It SHALL answer nothing for a point at or behind
the camera, and SHALL answer a position outside the canvas for a point in
front of the camera that falls outside it. It SHALL refuse a point that is
not three finite numbers. Projecting SHALL NOT draw a frame or change any
state.

#### Scenario: A label marks a point on the machine

- **WHEN** a host projects a world point lying on a visible part
- **THEN** the position falls inside that part's on-screen rectangle

#### Scenario: A point behind the camera

- **WHEN** a host projects a point behind the camera
- **THEN** the answer is nothing rather than a mirrored position
