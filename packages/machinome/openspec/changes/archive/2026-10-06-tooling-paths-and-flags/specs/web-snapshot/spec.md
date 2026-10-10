## MODIFIED Requirements

### Requirement: A requested camera is honoured or refused, never approximated

The web renderer SHALL accept a camera specification in either OpenSCAD form —
eye and target, or translation, rotations, and distance — resolve it to an eye,
a target, an up direction and the field of view OpenSCAD uses, and hand those
to the viewer's capture, so the same specification frames the model
equivalently under either renderer. A specification SHALL be honoured whatever
the signs of its values, including one whose resolved eye, target or up
direction begins with a negative component. Options the browser viewer cannot
honour SHALL be refused with an error naming them, rather than ignored.

#### Scenario: A maker asks for a specific viewpoint

- **WHEN** a maker renders the same camera specification with each renderer
- **THEN** both images frame the model from the same viewpoint at the same
  scale

#### Scenario: A rotated camera

- **WHEN** the camera is specified as a translation, rotations, and a distance
- **THEN** the model appears with the orientation those rotations describe,
  including any roll

#### Scenario: A camera vector that begins with a negative component

- **WHEN** a maker renders with `--renderer web --camera 0,0,0,65,0,35,1400`,
  whose resolved up direction is `(-0.2424..., 0.3462..., 0.9063...)`
- **THEN** the image is written, framed from the viewpoint those rotations
  describe, and the viewer's capture is not refused for the sign of a value

#### Scenario: An option the browser viewer cannot honour

- **WHEN** a maker requests the web renderer together with an OpenSCAD-only
  option
- **THEN** the command fails, naming the options that the web renderer does not
  support, and writes no image

#### Scenario: No camera requested

- **WHEN** no camera is specified
- **THEN** the whole model is framed automatically
