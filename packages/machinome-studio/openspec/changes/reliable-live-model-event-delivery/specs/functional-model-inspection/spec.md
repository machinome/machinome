## MODIFIED Requirements

### Requirement: The shop floor updates the displayed model in place
The Floor browser SHALL mount the viewer once for as long as the shop floor is
open and SHALL answer each reported artifact by updating that mounted viewer,
never by mounting a replacement. It SHALL decide what to update from the
reported artifact's path alone: the published document reconciles the rendered
tree, the failure record updates the reported failure, and any other artifact
replaces the geometry of the nodes referencing that exact path. The browser
SHALL NOT open, compare, or interpret an artifact's contents, and SHALL NOT
request an artifact that no reported path named. A browser that has obtained a
Floor run snapshot SHALL receive every later reported artifact, including one
published before its live-event subscription is established, and apply it to
the mounted viewer without a page reload.

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

#### Scenario: A publication arrives during the browser subscription hand-off
- **WHEN** an already-open Floor browser has read its run snapshot, an
  assembly-to-fusion build publishes `viewer.json`, and the browser's live
  event subscription becomes active afterward
- **THEN** the browser reconciles the mounted model to the fused publication
  without navigating, reloading, or mounting a second viewer
