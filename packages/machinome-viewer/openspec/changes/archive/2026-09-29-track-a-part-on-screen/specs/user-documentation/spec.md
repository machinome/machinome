## ADDED Requirements

### Requirement: The manual states film annotations as current-source capability

The host reference SHALL document `partOnScreen` and `project`, and, with
the changes that land beside them, `highlight` and `setView`'s up and field
of view: how to call each, its result, its units and coordinate frame, its
errors and that reading renders nothing. The compatibility page SHALL name
API 28 as the API of the current source that adds them, after the 0.7.1
release and in no published release, without rewriting the recorded 0.7.1
facts: its changelog section, the README and the manual home SHALL keep
stating API 27. The `describe` example SHALL match the package's
declarations. Reader-facing pages SHALL NOT name the originating project,
the film or the tool that asked for these members.

#### Scenario: A host looks up part tracking

- **WHEN** a host developer reads the viewer-handle reference
- **THEN** it finds `partOnScreen` and `project` with their pixel frame, the
  cases that answer nothing and the errors, and the API that introduced
  them

#### Scenario: A reader checks the release record

- **WHEN** a reader reads the 0.7.1 changelog section and the manual home
- **THEN** they still see API 27 and document versions 1 to 13, and no page
  claims API 28 was published
