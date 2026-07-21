# Functional Model Inspection Specification

## Purpose

Present a completed solid-node build in the shop floor without loading project
Python into Floor.

## Requirements

### Requirement: The shop floor builds the selected functional model before opening
When opening a project shop floor, the system SHALL use a solid-node CLI
one-shot build of the selected project-local functional-model path before
declaring the shop floor open. The floor service SHALL serve only the resulting
completed `_build` viewer snapshot and referenced model files. It SHALL NOT
import, execute, reload, inspect, or serve project Python source.

#### Scenario: A project has a selected model path
- **WHEN** the maker opens the shop for a project and selects its project-local functional-model path
- **THEN** the system completes one solid-node CLI build and presents the completed `_build` model artifacts in the shop workspace

### Requirement: The shop floor refreshes a changed functional model
After a development process reports a successfully updated build through the
floor callback, the broker SHALL notify connected browsers and they SHALL load
the complete current `_build` model artifacts without Floor importing or
executing project Python.

#### Scenario: The machinist changes the model
- **WHEN** the machinist's development process reports that a new model build is ready
- **THEN** the broker publishes a model-change event and the browser replaces its artifact view with the complete current model state

### Requirement: The shop floor presents the complete static viewer experience
The Floor browser SHALL render completed build artifacts with the established
solid-node viewer semantics while obtaining only `viewer.json` and referenced
model files through Floor's static artifact route. It SHALL use nested node
groups, complete OpenSCAD expression evaluation, inherited colours, normal
material for uncoloured models, a Z-up fitted camera, and working orbit
rotation and zoom. It SHALL NOT use the separate export widget.

#### Scenario: A colourless V8 model is displayed
- **WHEN** the build snapshot has no explicit or inherited colour for a model
- **THEN** Floor renders that mesh with the established viewer's normal-based material rather than a uniform grey material

#### Scenario: A build contains time-based operations
- **WHEN** any operation in the build snapshot references `$t`
- **THEN** Floor autoplays the model and provides a compact Timeline toggle; the timeline slider and play/pause controls remain hidden until the maker requests them

#### Scenario: The maker is inspecting a model when it refreshes
- **WHEN** the maker has rotated, panned, or zoomed the functional model and a successful callback-driven build refreshes it
- **THEN** Floor replaces the model tree while retaining the maker's camera position, orientation, zoom, and orbit target

### Requirement: The build snapshot carries browser animation metadata
The `solid build` publication consumed by Floor SHALL include a versioned
animation cadence with `fps` and `frames` together with the root viewer tree.

#### Scenario: Floor opens an animated model
- **WHEN** `solid build` publishes a model whose operations include `$t`
- **THEN** `viewer.json` supplies the animation cadence required for Floor to animate that model without a project runtime
