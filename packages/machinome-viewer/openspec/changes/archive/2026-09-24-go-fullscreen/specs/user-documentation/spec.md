## ADDED Requirements

### Requirement: The manual states full-screen viewing

The maker's guide SHALL describe the full-screen control: where it
appears for a model with a timeline or a transport and for one without,
that `f` enters and leaves full screen, and that Escape leaves it. It
SHALL say that the control is absent where the browser or the embedding
page does not permit full screen. The embedding guide SHALL give its
iframe example the full-screen permission and state that without it the
control is hidden. The layout reference SHALL list the control's stable
class. The changelog SHALL record full-screen viewing in the section the
current source belongs to. While 0.7.0 is at released state and not
uploaded, that is the 0.7.0 section, with the viewer API and document
versions unchanged.

#### Scenario: A maker looks for full screen

- **WHEN** a maker reads the guide to using the viewer
- **THEN** they learn where the full-screen button is and that `f` and
  Escape enter and leave full screen

#### Scenario: A site embeds an export

- **WHEN** a developer copies the embedding guide's iframe example
- **THEN** it carries the full-screen permission, and the guide says the
  button is hidden without it
