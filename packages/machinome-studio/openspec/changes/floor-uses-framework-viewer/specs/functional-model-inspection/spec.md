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
- **THEN** Floor replaces the model tree while retaining the maker's camera position, orientation, zoom, and orbit target

#### Scenario: solid-node improves how models are seen
- **WHEN** the installed solid-node changes how it renders a published model
- **THEN** the shop floor shows that change without a corresponding shop change

## ADDED Requirements

### Requirement: The shop floor requires a usable solid-node viewer to open
When opening a named project shop floor, the system SHALL obtain the browser
viewer from the installed solid-node through its CLI. When that solid-node
supplies no viewer, or supplies one the floor cannot use, the system SHALL treat
preparation as failed, report the reason and its remedy, and SHALL NOT start
Floor or its agents. The maker SHALL NOT be shown a shop that is open with a
model pane that cannot render.

#### Scenario: The installed solid-node ships no viewer
- **WHEN** the maker opens the shop and the installed solid-node has no built viewer available
- **THEN** the shop does not open, and the maker is told that the viewer is unavailable together with how to produce it

#### Scenario: The installed viewer is older than the floor requires
- **WHEN** the maker opens the shop and the installed solid-node's viewer does not meet the interface the floor depends on
- **THEN** the shop does not open, and the maker is told which viewer the floor requires and which one is installed

#### Scenario: A usable viewer is installed
- **WHEN** the maker opens the shop and the installed solid-node supplies a usable viewer
- **THEN** the shop opens and the browser renders the functional model with that viewer
