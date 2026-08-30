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

### Requirement: A commit carrying no model content does not render

A floor-mediated commit whose staged content cannot change the model SHALL NOT
trigger a render, and SHALL neither replace nor stage the project screenshot.
The commit SHALL report that it carried no model content, so a missing
screenshot refresh is never mistaken for a rendering failure.

#### Scenario: Committing only spec text

- **WHEN** a floor-mediated commit stages only files belonging to the project's
  spec record
- **THEN** no render is attempted, the existing screenshot is untouched and
  unstaged, and the commit succeeds

#### Scenario: Committing parts alongside spec text

- **WHEN** a floor-mediated commit stages model source together with spec
  record files
- **THEN** the screenshot is refreshed and staged as for any model commit

### Requirement: Opening a project renders only when the open changed the model

Opening a project SHALL render a screenshot only when that open changed what is
published, or when the project has no valid screenshot yet. An open whose build
published nothing SHALL NOT render, because a render that cannot produce
different bytes cannot produce a different screenshot.

This is the rule floor-mediated commits already follow — content that cannot
change the model does not render — applied to the other path that triggers a
render.

The shop SHALL decide this from the publication itself, before rendering, and
SHALL NOT decide it by rendering and then comparing the result. Comparing after
the fact still pays the whole cost, which on a large project is the single
largest part of opening it.

A project with no valid screenshot SHALL still get one on open even when its
build published nothing, so a project that has never been rendered does not stay
without a preview.

#### Scenario: Reopening an unchanged project

- **WHEN** the maker opens a project whose build publishes nothing, and a valid
  screenshot already exists
- **THEN** no render is attempted and the existing screenshot is untouched

#### Scenario: Opening a project that published new work

- **WHEN** opening a project runs a build that publishes a changed model
- **THEN** a screenshot is rendered and published as it is today

#### Scenario: A project that has never been rendered

- **WHEN** the maker opens a project whose build publishes nothing and which has
  no valid `screenshot.png`
- **THEN** a screenshot is rendered so the project gains its preview

#### Scenario: Rendering stays subordinate to the model

- **WHEN** an open renders a screenshot and the render fails
- **THEN** the session still opens and the build result stands, as screenshot
  failure already requires

