## ADDED Requirements

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
