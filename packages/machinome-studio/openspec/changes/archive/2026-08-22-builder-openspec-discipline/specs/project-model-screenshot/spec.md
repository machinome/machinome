## ADDED Requirements

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
