## ADDED Requirements

### Requirement: The shop floor updates the displayed model in place
The Floor browser SHALL mount the viewer once for as long as the shop floor is
open and SHALL answer each reported artifact by updating that mounted viewer,
never by mounting a replacement. It SHALL decide what to update from the
reported artifact's path alone: the published document reconciles the rendered
tree, the failure record updates the reported failure, and any other artifact
replaces the geometry of the nodes referencing that exact path. The browser
SHALL NOT open, compare, or interpret an artifact's contents, and SHALL NOT
request an artifact that no reported path named.

#### Scenario: One part of the model is republished
- **WHEN** the shop floor reports one model artifact of a model with many
- **THEN** the browser requests that artifact and no other, and the parts it
  did not name keep the geometry they are already displaying

#### Scenario: The maker's view survives a change
- **WHEN** the maker has rotated, panned, or zoomed the functional model and
  any artifact of it is reported
- **THEN** the same rendered canvas remains in the page, and the camera
  position, orientation, zoom, and orbit target are unchanged

#### Scenario: An artifact is republished under the name it already had
- **WHEN** a change republishes an artifact at the path the browser has
  already fetched once
- **THEN** the browser displays the republished contents rather than the
  contents it fetched before

#### Scenario: The model gains and loses parts
- **WHEN** a change adds one node and removes another, and the shop floor
  reports the republished document
- **THEN** the browser reconciles the displayed model to the document, showing
  the added node and dropping the removed one, without requesting geometry for
  the parts the document still names unchanged

#### Scenario: A change moves nothing but placement
- **WHEN** a change alters only placement or colour and the shop floor reports
  the republished document
- **THEN** the displayed model reflects the change and the browser requests no
  model geometry

### Requirement: A failed model update leaves the model standing
A request the browser cannot complete SHALL NOT remove the displayed model. The
browser SHALL keep the mounted viewer, the rendered model, and the maker's view
in place, report the failure beside the model rather than in place of it, and
remain able to apply the next reported artifact. Recovering from a failed
update SHALL NOT require the maker to reload the page.

#### Scenario: An artifact cannot be fetched
- **WHEN** the browser cannot fetch an artifact the shop floor reported
- **THEN** the model that is already displayed remains displayed with the
  maker's view intact, and the maker is told the update failed

#### Scenario: The next change arrives after a failure
- **WHEN** an artifact fetch has failed and the shop floor later reports
  another artifact
- **THEN** the browser applies that update to the still-mounted viewer, and
  the reported failure is cleared without a page reload

#### Scenario: The model cannot be shown at all
- **WHEN** the browser cannot mount the viewer when the shop floor opens
- **THEN** the maker is told why, and a later reported artifact is attempted
  rather than ignored

## MODIFIED Requirements

### Requirement: The shop floor presents the complete static viewer experience
The Floor browser SHALL render completed build artifacts with the established
solid-node viewer semantics while obtaining only `viewer.json` and referenced
model files through Floor's static artifact route. It SHALL use nested node
groups, complete OpenSCAD expression evaluation, inherited colours, normal
material for uncoloured models, a Z-up fitted camera, and working orbit
rotation and zoom. A capability that solid-node adds to that viewer SHALL reach
the shop floor without the shop reproducing it.

#### Scenario: A colourless V8 model is displayed
- **WHEN** the build snapshot has no explicit or inherited colour for a model
- **THEN** Floor renders that mesh with the established viewer's normal-based material rather than a uniform grey material

#### Scenario: A build contains time-based operations
- **WHEN** any operation in the build snapshot references `$t`
- **THEN** Floor autoplays the model and provides a compact Timeline toggle; the timeline slider and play/pause controls remain hidden until the maker requests them

#### Scenario: The maker is inspecting a model when it refreshes
- **WHEN** the maker has rotated, panned, or zoomed the functional model and a successful rebuild refreshes it
- **THEN** Floor updates only the parts the rebuild republished, leaving the rest of the rendered model and the maker's camera position, orientation, zoom, and orbit target as they were

#### Scenario: solid-node improves how models are seen
- **WHEN** the installed solid-node changes how it renders a published model
- **THEN** the shop floor shows that change without a corresponding shop change

### Requirement: The shop floor requires a usable solid-node viewer to open
When opening a named project shop floor, the system SHALL obtain the browser
viewer from the installed solid-node through its CLI. The viewer the floor
requires SHALL be one that updates a mounted model in place from a named
artifact and from the published document. When the installed solid-node
supplies no viewer, or supplies one the floor cannot use, the system SHALL
treat preparation as failed, report the reason and its remedy, and SHALL NOT
start Floor or its agents. The maker SHALL NOT be shown a shop that is open
with a model pane that cannot render.

#### Scenario: The installed solid-node ships no viewer
- **WHEN** the maker opens the shop and the installed solid-node has no built viewer available
- **THEN** the shop does not open, and the maker is told that the viewer is unavailable together with how to produce it

#### Scenario: The installed viewer is older than the floor requires
- **WHEN** the maker opens the shop and the installed solid-node's viewer does not meet the interface the floor depends on
- **THEN** the shop does not open, and the maker is told which viewer the floor requires and which one is installed

#### Scenario: The installed viewer cannot update in place
- **WHEN** the maker opens the shop and the installed solid-node's viewer can only be mounted and replaced
- **THEN** the shop does not open rather than opening with a model pane that reloads the whole model on every change

#### Scenario: A usable viewer is installed
- **WHEN** the maker opens the shop and the installed solid-node supplies a usable viewer
- **THEN** the shop opens and the browser renders the functional model with that viewer
