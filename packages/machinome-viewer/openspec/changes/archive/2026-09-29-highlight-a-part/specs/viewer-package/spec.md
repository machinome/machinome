## ADDED Requirements

### Requirement: A host highlights parts and sets the others back

The mount handle SHALL let a host highlight one or more assembly paths,
parts or subassemblies: every visible part under them SHALL take a visible
tint in a host-chosen colour, or a default accent, where its material can
carry one. The host SHALL choose whether every other part is kept as it is,
dimmed, or ghosted: drawn translucent and still drawn, so that a
highlighted part behind it is seen through it. The viewer SHALL draw the
result before returning, and SHALL return a function that puts every part
back exactly as it looked before and draws that.

Only one highlight SHALL stand at a time: a second request before the first
is put back SHALL be refused by name. Putting back more than once SHALL
have no further effect. A request naming an unknown or ambiguous path, an
unreadable colour, an unknown treatment of the others or no path at all
SHALL be refused by name before anything changes.

A highlight SHALL NOT change which parts are shown, the focused root, the
pose or the view, and SHALL NOT notify assembly listeners: a hidden part
stays hidden. A standing highlight SHALL survive the viewer's in-place
updates and reload, applying to the same paths on the new geometry, and a
path the updated tree no longer has SHALL be dropped from it. A part a
maker hovers SHALL return to its highlighted or ordinary look when the
pointer leaves, whatever order hovering and highlighting happened in.

#### Scenario: The narration points at the wheel

- **WHEN** a film host highlights the wheel with the others kept
- **THEN** the captured frame shows the wheel tinted and every other part
  as before

#### Scenario: The housing is seen through

- **WHEN** a host highlights a gear inside a housing with the others ghosted
- **THEN** the housing is drawn translucent and the gear is visible through
  it

#### Scenario: The rest recedes

- **WHEN** a host highlights a part with the others dimmed
- **THEN** every other part is drawn darker and the highlighted part is not

#### Scenario: Putting it back is exact

- **WHEN** a host captures a frame, highlights, calls the returned function
  and captures again
- **THEN** the two captures are identical

#### Scenario: A second highlight is refused

- **WHEN** a host highlights while an earlier highlight still stands
- **THEN** the call fails, naming the need to put the earlier one back, and
  the frame is unchanged

#### Scenario: A hidden part stays hidden

- **WHEN** a host hides a part and then highlights it
- **THEN** the part is not drawn, and it appears highlighted when the host
  shows it again

#### Scenario: Hover and highlight do not fight

- **WHEN** a maker hovers a control's part, the host highlights it, the
  pointer leaves and the host puts the highlight back
- **THEN** the part looks exactly as it did before either happened

### Requirement: A ghosted part does not hide a tracked part

When the others are ghosted, the point the handle reports for where a part
stands on screen SHALL be found as if the ghosted parts were not in front
of it, since they are drawn to be seen through. What a press or a hover
reaches SHALL NOT change.

#### Scenario: An arrow points at a gear inside a ghosted housing

- **WHEN** a host ghosts the others and asks where a gear enclosed by a
  housing stands on screen
- **THEN** it receives a point on the gear rather than nothing
