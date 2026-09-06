## MODIFIED Requirements

### Requirement: The shop maintains one canonical project model screenshot

The shop SHALL maintain one canonical hub preview per openable entry. For a
project listed as a single openable project that path is the exact project-root
path `screenshot.png`. For one declared model of a multi-model project it is the
exact project-root path `screenshots/<model>.png`, where `<model>` is the name
the manifest gives that model. The shop SHALL render through the selected
solid-node CLI without importing project Python, render the entry's own model,
select the CLI's web renderer to produce a transparent background, use a fixed
shop-owned thumbnail recipe, and atomically replace the path only after a
complete PNG has been produced and only when its bytes differ from the existing
regular non-symlink file.

The shop SHALL compare and publish the complete PNG supplied by the web
renderer without pixel post-processing.

#### Scenario: The model renders a changed screenshot

- **WHEN** the shop receives a complete rendered PNG whose processed bytes
  differ from the current screenshot of a single-model project
- **THEN** it atomically replaces `<project>/screenshot.png`

#### Scenario: One model of several renders a changed screenshot

- **WHEN** the shop receives a complete rendered PNG for a declared model whose
  bytes differ from that model's current screenshot
- **THEN** it atomically replaces `<project>/screenshots/<model>.png` and leaves
  every sibling model's screenshot untouched

#### Scenario: The web renderer supplies a transparent canvas

- **WHEN** a successful web renderer output has a transparent background
- **THEN** the shop publishes those exact complete PNG bytes without flood-fill
  processing

#### Scenario: The screenshot path is unsafe

- **WHEN** the entry's screenshot path is a symlink or is not a regular file
  under the project root
- **THEN** the shop does not follow, replace, or automatically stage that path

### Requirement: Opening a project renders only when the open changed the model

Opening an entry SHALL render a screenshot only when that open changed what its
model publishes, or when that entry has no valid screenshot yet. An open whose
build published nothing SHALL NOT render, because a render that cannot produce
different bytes cannot produce a different screenshot.

This is the rule floor-mediated commits already follow — content that cannot
change the model does not render — applied to the other path that triggers a
render.

The shop SHALL decide this from the publication itself, before rendering, and
SHALL NOT decide it by rendering and then comparing the result. Comparing after
the fact still pays the whole cost, which on a large project is the single
largest part of opening it.

An entry with no valid screenshot SHALL still get one on open even when its
build published nothing, so an entry that has never been rendered does not stay
without a preview.

#### Scenario: Reopening an unchanged project

- **WHEN** the maker opens an entry whose build publishes nothing, and a valid
  screenshot already exists for it
- **THEN** no render is attempted and the existing screenshot is untouched

#### Scenario: Opening a project that published new work

- **WHEN** opening an entry runs a build that publishes a changed model
- **THEN** a screenshot is rendered and published as it is today

#### Scenario: A model that has never been rendered

- **WHEN** the maker opens a declared model whose build publishes nothing and
  which has no valid screenshot of its own
- **THEN** a screenshot is rendered so that model gains its preview, even when a
  sibling model of the same project already has one

#### Scenario: Rendering stays subordinate to the model

- **WHEN** an open renders a screenshot and the render fails
- **THEN** the session still opens and the build result stands, as screenshot
  failure already requires
