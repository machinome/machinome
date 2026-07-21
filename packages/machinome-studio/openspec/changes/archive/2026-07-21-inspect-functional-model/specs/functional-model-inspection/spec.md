## ADDED Requirements

### Requirement: The shop floor builds the conventional functional model before opening
When opening a project shop floor, the system SHALL use a solid-node CLI
one-shot build of the selected project-local functional-model path before
declaring the shop floor open. The floor service SHALL serve only the resulting completed `_build`
viewer snapshot and its referenced model files. It SHALL NOT import, execute,
reload, inspect, or serve project Python source.

#### Scenario: A project has a selected model path
- **WHEN** the maker opens the shop for a project and selects its project-local functional-model path
- **THEN** the system completes one solid-node CLI build and presents the completed `_build` model artifacts in the shop workspace

#### Scenario: The selected model path does not exist
- **WHEN** the maker opens the shop for a project and the selected functional-model path does not exist
- **THEN** the solid-node CLI exits cleanly with a message that the model does not exist and the system does not declare the shop open

### Requirement: The shop floor refreshes a changed functional model
The system SHALL start the machinist's solid-node development process with a
floor-broker callback location. After that process reports a successfully
updated build, the broker SHALL notify connected browsers and they SHALL load
the complete current `_build` model artifacts. The callback is a build-ready
signal and SHALL NOT cause floor to import or execute project Python.

#### Scenario: The machinist changes the model
- **WHEN** the machinist's development process reports that a new model build is ready
- **THEN** the broker publishes a model-change event and the browser replaces its artifact view with the complete current model state

#### Scenario: A later build fails
- **WHEN** a development-time model build fails after the floor has a previously successful model
- **THEN** the browser retains the last successful model state and does not present a partial update

### Requirement: The shop floor presents the complete static viewer experience
The Floor browser SHALL render the completed build snapshot with the same
viewer semantics as the established solid-node static viewer, while obtaining
only `viewer.json` and referenced model files through Floor's static artifact
route. It SHALL recreate the nested node hierarchy, apply raw operations using
the complete OpenSCAD expression semantics, use a Z-up fitted camera, and
provide working orbit rotation and zoom. It SHALL NOT import, execute, inspect,
or serve project Python or use the separate export widget.

#### Scenario: A colourless V8 model is displayed
- **WHEN** the build snapshot has no explicit or inherited colour for a model
- **THEN** Floor renders that mesh with the normal-based material used by the established viewer rather than a uniform grey material

#### Scenario: Model colours are inherited
- **WHEN** a model node has no colour and an ancestor has an explicit colour
- **THEN** Floor renders the model with the ancestor's colour

#### Scenario: The maker manipulates the model
- **WHEN** the maker drags or scrolls in the functional-model view
- **THEN** the visible model rotates or zooms immediately and remains framed against the complete model bounds

#### Scenario: A build contains time-based operations
- **WHEN** any operation in the build snapshot references `$t`
- **THEN** Floor autoplays the model and provides a compact Timeline toggle;
  the timeline slider and play/pause controls remain hidden until the maker
  requests them, and the model visibly updates over the snapshot's published
  animation cadence

#### Scenario: A build contains no time-based operation
- **WHEN** no operation in the build snapshot references `$t`
- **THEN** Floor presents the static model without animation controls

#### Scenario: A refreshed tree supersedes an earlier load
- **WHEN** a new completed build replaces the current snapshot while earlier STL requests are still in flight
- **THEN** Floor displays only the complete replacement tree and does not reintroduce meshes from the superseded tree

#### Scenario: The maker is inspecting a model when it refreshes
- **WHEN** the maker has rotated, panned, or zoomed the functional model and a
  successful callback-driven build refreshes it
- **THEN** Floor replaces the model tree while retaining the maker's camera
  position, orientation, zoom, and orbit target

### Requirement: The build snapshot carries browser animation metadata
The `solid build` publication consumed by Floor SHALL include a versioned
animation cadence with `fps` and `frames` together with the root viewer tree.
Floor SHALL use that metadata to drive raw `$t` operations and SHALL not read
project source to obtain it.

#### Scenario: Floor opens an animated model
- **WHEN** `solid build` publishes a model whose operations include `$t`
- **THEN** `viewer.json` supplies the animation cadence required for Floor to animate that model without a project runtime
