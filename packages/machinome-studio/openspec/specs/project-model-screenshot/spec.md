## Purpose

Maintain a durable, lightweight model preview for each project card.

## Requirements

### Requirement: The shop maintains one canonical project model screenshot

The shop SHALL use the exact project-root path `screenshot.png` as the
canonical hub preview. It SHALL render through the selected solid-node CLI
without importing project Python, select the CLI's web renderer to produce a
transparent background, use a fixed shop-owned thumbnail recipe, and atomically
replace the path only after a complete PNG has been produced and only when its
bytes differ from the existing regular non-symlink file.

The shop SHALL compare and publish the complete PNG supplied by the web
renderer without pixel post-processing.

#### Scenario: The model renders a changed screenshot

- **WHEN** the shop receives a complete rendered PNG whose processed bytes
  differ from the current project screenshot
- **THEN** it atomically replaces `<project>/screenshot.png`

#### Scenario: The web renderer supplies a transparent canvas

- **WHEN** a successful web renderer output has a transparent background
- **THEN** the shop publishes those exact complete PNG bytes without flood-fill
  processing

#### Scenario: The screenshot path is unsafe

- **WHEN** `screenshot.png` is a symlink or is not a regular project-root file
- **THEN** the shop does not follow, replace, or automatically stage that path

### Requirement: Screenshot failure is subordinate to project work

A screenshot failure SHALL NOT change a successful build into a failed build,
prevent a requested Git commit, or delete or truncate an existing screenshot.

#### Scenario: Rendering fails after a successful build

- **WHEN** the model build succeeds but screenshot rendering or processing fails
- **THEN** the build remains successful and the prior screenshot remains
  untouched, or no screenshot exists if there was none
