## MODIFIED Requirements

### Requirement: The shop floor refreshes a changed functional model
While a named project shop floor is open, the system SHALL keep the maker's
functional-model view current with the project's model source. When the project's
model changes, the system SHALL rebuild it and present the resulting complete
`_build` model artifacts to connected browsers, without Floor importing or
executing project Python and without the maker or any agent performing an action
to cause the refresh.

#### Scenario: Any author changes the model
- **WHEN** the project's model source changes while the shop floor is open, by whichever author changed it
- **THEN** the system rebuilds the model and the browser replaces its artifact view with the complete current model state

#### Scenario: A rebuild produces no change to the published model
- **WHEN** a rebuild completes and leaves the published model artifacts unchanged
- **THEN** the system does not report a model change to connected browsers

## ADDED Requirements

### Requirement: The shop floor reports a failed model rebuild
When a rebuild of the changed model fails, the system SHALL report the failure
and its diagnostic text to connected browsers, and SHALL keep the last complete
model artifacts available for inspection. A subsequent successful rebuild SHALL
clear that reported failure.

#### Scenario: The model source is broken
- **WHEN** the project's model source changes so that a rebuild fails
- **THEN** the maker is shown that the rebuild failed together with the reported reason, and the previously built model remains inspectable

#### Scenario: The maker fixes the model
- **WHEN** a rebuild succeeds after a previously reported failure
- **THEN** the reported failure is cleared
- **AND** the browser presents a newly built model only when the published artifacts changed
