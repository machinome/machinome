## ADDED Requirements

### Requirement: A camera move can change field of view and up

In a format 0.3 episode, the author SHALL be able to key a shot between named
cameras whose field of view or up direction differ. The audience SHALL see the
field of view and the up direction change smoothly between the keys with the
same easing as position and target, and hold after the last key.

#### Scenario: Narrow onto the pawls
- **WHEN** a *Revolutions* shot keys from the `pawls` camera to a preset at the
  same position with a narrower field of view
- **THEN** the pawls grow on screen smoothly over the interval while the camera
  does not move, and the projected size matches the requested field of view.

#### Scenario: Level the view while travelling
- **WHEN** a shot keys between presets whose up directions differ but are not
  opposite
- **THEN** the horizon turns smoothly between them and the up direction is never
  degenerate.

### Requirement: Constant up and field of view render exactly as before

Episodes whose cameras share one up direction and field of view SHALL produce the
same frames as before this change, in either format, with any Viewer API 21 or
later.

#### Scenario: The released episodes are unchanged
- **WHEN** the sawmill rehearsal or *Revolutions* is previewed with the same
  viewer bundle before and after this change
- **THEN** its stills are byte-for-byte identical.

### Requirement: Impossible or unsupported camera moves are refused

Production MUST refuse, naming the shot: adjacent keys whose up directions are
opposite; a frame whose up direction lies along the viewing direction; a format
0.2 episode changing field of view or up within a shot; and any episode whose
cameras differ in field of view or up, within a shot or across a cut, against a
viewer declaring an API below 28. `preview` and `render` MUST refuse a frame
whose viewer does not report back the requested field of view and up.

#### Scenario: Up reverses
- **WHEN** a shot keys from an up of `[0, 0, 1]` to `[0, 0, -1]`
- **THEN** `check` refuses it and asks for an intermediate preset.

#### Scenario: Field-of-view move, old viewer
- **WHEN** an episode narrowing the field of view within a shot is previewed with
  a Viewer API 27 bundle
- **THEN** preview refuses before capturing and names Viewer API 28.

#### Scenario: A cut between different lenses, old viewer
- **WHEN** a format 0.2 episode cuts between presets with different fields of view
  and the viewer declares API 27
- **THEN** production refuses instead of silently keeping the first shot's field of view.
