## ADDED Requirements

### Requirement: A reframe moves a view's host and fades the rest

When a frame carries a reframe, the stage SHALL draw the incoming set with
its slots and chrome as for any frame, and SHALL position the viewer host of
each view element the reframe moves over the box the frame gives it, in
fractions of the frame, instead of over its slot's box, keeping the host
inside its slot's element so the set's stacking order holds; the slot's own
box SHALL stay what the set draws. The stage SHALL report that box as the
element's `box`, draw the view's marks over it, and wait for the canvas to
fill it before measuring, whenever its size changed. Every other element the
frame places SHALL be drawn at the frame's progress as opacity, and during a
reframe every element SHALL report its opacity. At progress 1 the stage
SHALL draw exactly what it draws for the same frame without a join. The
positioning and the fade SHALL be functions of the frame alone.

#### Scenario: The host follows the frame's box
- **WHEN** a frame of a reframe gives `opening.wide` the box
  `[0.27, 0.17, 0.56, 0.74]` of a 1280×720 page
- **THEN** its host is drawn at 345.6, 122.4, 716.8 by 532.8 pixels, to
  the layout's unit of 1/64 pixel, which the stage reports as the element's
  box, while the `right` slot keeps its own box.

#### Scenario: A view drawn under the set's headline
- **WHEN** the incoming set draws its headline above its right slot and a
  reframe moves the view held there
- **THEN** the headline stays above the moving view on every frame of the
  join.

#### Scenario: Without a reframe
- **WHEN** the next frame carries no reframe
- **THEN** the host fills its element's box again and no element carries an
  opacity of the join.
