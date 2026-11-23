## ADDED Requirements

### Requirement: The manual states layers

The viewer's pages of the manual SHALL state, as user guidance, how a model's
app reads the layers a document declares and shows one: the handle's list of
layers, the lookup by key and its refusal, showing a layer and the whole
machine, and what `show` refuses; that a part the shown layer leaves out is
absent for drawing, pressing, hovering, its on-screen position and framing;
how the shown layer composes with focusing and hiding, what the navigation
state and the assembly snapshot report, and how the navigator marks the rows
the layer leaves out; what a republish does to the shown layer; that the
viewer presents no layer control of its own; what a document with malformed
layers is refused for; and the viewer API that carries the capability. The
shared how-to SHALL walk a maker from declaring the layers to the app's
buttons on the public contract alone.

#### Scenario: A maker writes the layer buttons

- **WHEN** a maker writing an app looks up `show` in the viewer's reference
- **THEN** the reference states what it takes, that `null` shows the whole
  machine, that a string is refused, and that the navigator's hidden parts
  stay hidden

#### Scenario: A maker reads the navigator under a layer

- **WHEN** a maker sees obscured rows while a layer is shown and looks them up
- **THEN** the layouts page says those rows are outside the shown layer and
  that their controls still report the maker's own setting
