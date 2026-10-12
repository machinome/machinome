## MODIFIED Requirements

### Requirement: The shop floor refreshes a changed functional model
While a named project shop floor is open, the system SHALL keep the maker's
functional-model view current with the project's model source. The system SHALL
learn that the model source changed from filesystem change notification rather
than from periodic scanning of the project tree, so that the delay between a
save and the start of a rebuild does not grow with the number of source files.
When the project's model changes, the system SHALL rebuild it and present the
resulting complete `_build` model artifacts to connected browsers, without Floor
importing or executing project Python and without the maker or any agent
performing an action to cause the refresh. Where the project's filesystem cannot
deliver change notification, the system MAY fall back to periodic scanning and
SHALL still satisfy every scenario below.

#### Scenario: Any author changes the model
- **WHEN** the project's model source changes while the shop floor is open, by whichever author changed it
- **THEN** the system rebuilds the model and the browser replaces its artifact view with the complete current model state

#### Scenario: A rebuild produces no change to the published model
- **WHEN** a rebuild completes and leaves the published model artifacts unchanged
- **THEN** the system does not report a model change to connected browsers

#### Scenario: An editor writes a source file through a temporary file
- **WHEN** an editor saves a model source file by writing a temporary file and renaming it over the original
- **THEN** the system treats that as a change to the model source and rebuilds

#### Scenario: A save touches several files at once
- **WHEN** several model source files change within one short burst
- **THEN** the system coalesces the burst into one rebuild rather than building once per file

#### Scenario: A file is observed part-written
- **WHEN** a source file is changed and then changed again immediately, as an in-place write can appear
- **THEN** the system waits for the source to settle before building, so a transient partial state does not produce a reported failure

## ADDED Requirements

### Requirement: A rebuild does not trigger itself
The system SHALL ignore changes it makes to the project's own build output when
deciding whether the model source changed, so that publishing a rebuild cannot
cause a further rebuild.

#### Scenario: A rebuild writes into the build tree
- **WHEN** a rebuild publishes new artifacts into the project's build output
- **THEN** those writes do not cause another rebuild
