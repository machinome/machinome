## RENAMED Requirements

- FROM: `### Requirement: A view keeps one viewer across its chapter`
- TO: `### Requirement: View elements lease viewer instances`

## MODIFIED Requirements

### Requirement: View elements lease viewer instances

Each view element placed in a frame SHALL be drawn by a viewer instance of
its own in that frame, positioned over the box of the slot it is placed in;
two views placed in one frame SHALL be two instances, each with its own
camera, visibility, highlight and marks. Instances SHALL be leased: a view
element placed in consecutive frames SHALL keep its instance, whatever slot
holds it; an instance whose view element a frame does not place SHALL be
free, and MAY be leased to another view element of that frame or of a later
one; a view element placed without an instance SHALL take a free instance,
and a new instance SHALL mount only when none is free. With a viewer that
declares API 28 or later, a film SHALL therefore mount no more viewer
instances than the largest number of view elements one of its frames places.
A viewer below API 28 cannot be given another up or field of view, so its
instance SHALL be leased only to a view element with the up and field of
view it mounted with. Each frame SHALL state each instance's whole state,
applied against what the instance holds (the layers it hides and the
highlight left standing, whichever view element it served before), so a
leased instance draws exactly what a fresh one would and no instance depends
on the frames posed before.

#### Scenario: The mill moves from the whole frame into the split
- **WHEN** the chapter `drive` of *Cut and Advance* shows `mill` in
  `Leonardo`'s `stage` in `wheel` and then in `LeonardoSplit`'s `right` in
  `coupling`
- **THEN** the same viewer is posed in both shots, in the new box after the
  cut, with the camera the chapter's last move left it at.

#### Scenario: A film whose frames show one view each
- **WHEN** *Cut and Advance*, whose six view elements are placed one per
  frame, is previewed or rendered
- **THEN** one viewer instance mounts, and each chapter's view is drawn on it
  with that chapter's camera, hidden layers, highlight and marks.

#### Scenario: A highlight left standing by the previous view
- **WHEN** a frame highlights a part of one view element, and the next frame
  places another view element, with no highlight, on the instance it freed
- **THEN** the highlight is restored before the new state is applied, the
  layers the first view hid and the second does not are shown again, and the
  frame's pixels are those the second view gives on a fresh instance.

#### Scenario: Two views side by side
- **WHEN** a shot on `split` places two views of one chapter, one in `left`
  and one in `right`, and highlights a part on the left one only
- **THEN** each half shows the model through its own camera, only the left
  half shows the highlight, and frames placing either view alone, before or
  after, mount no third instance.
