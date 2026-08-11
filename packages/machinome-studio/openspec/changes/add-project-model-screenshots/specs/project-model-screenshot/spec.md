## ADDED Requirements

### Requirement: The shop maintains one canonical project model screenshot
The shop SHALL use the exact project-root path `screenshot.png` as the canonical
hub preview for a project. It SHALL render the image through the selected
solid-node CLI's web renderer without importing project Python, SHALL render
with one shop-owned thumbnail recipe, and SHALL atomically replace the path
only after a complete PNG has been produced and only when its bytes differ from
the existing regular non-symlink file.

The shop SHALL compare and publish the complete PNG supplied by the web
renderer without pixel post-processing.

#### Scenario: The model renders a changed screenshot
- **WHEN** the shop requests a screenshot and the renderer produces a complete PNG whose bytes differ from the current project screenshot
- **THEN** the shop atomically replaces `<project>/screenshot.png` with the completed image

#### Scenario: The model renders the same screenshot
- **WHEN** the shop requests a screenshot and the rendered PNG has the same bytes as the current project screenshot
- **THEN** the shop leaves `screenshot.png` unchanged

#### Scenario: The web renderer supplies a transparent canvas
- **WHEN** a successful web renderer output has a transparent background
- **THEN** the shop publishes those exact complete PNG bytes without flood-fill
  processing

#### Scenario: The project has no screenshot yet
- **WHEN** the first successful screenshot render completes for a project without `screenshot.png`
- **THEN** the shop atomically creates `<project>/screenshot.png`

#### Scenario: The screenshot path is unsafe
- **WHEN** `screenshot.png` is a symlink or is not a regular project-root file
- **THEN** the shop does not follow, replace, or automatically stage that path

### Requirement: Screenshot failure is subordinate to project work
A screenshot failure SHALL NOT change a successful build into a failed build,
SHALL NOT prevent a requested Git commit, and SHALL NOT delete or truncate an
existing screenshot. When no prior screenshot exists, the project SHALL remain
without one.

#### Scenario: Rendering fails after a successful build
- **WHEN** the model build succeeds but screenshot rendering fails
- **THEN** the build remains successful and the prior `screenshot.png` remains untouched, or no screenshot exists if there was none

#### Scenario: Atomic publication fails
- **WHEN** a complete temporary screenshot cannot be compared with or atomically installed at the project root
- **THEN** the shop preserves the existing project screenshot whenever possible and does not report a model-build failure

### Requirement: Existing projects acquire screenshots without eager migration
The shop SHALL NOT modify a closed project merely because it is inventoried.
An existing project without `screenshot.png` SHALL retain the hub placeholder
until an observed successful build or floor-mediated commit produces one.

#### Scenario: An older project appears in the working folder
- **WHEN** the hub inventories an existing project that has no `screenshot.png`
- **THEN** the project remains unchanged and its card uses the placeholder

#### Scenario: The older project later builds successfully
- **WHEN** that project has an observed successful build while its shop session is open
- **THEN** the shop attempts to create its canonical screenshot
