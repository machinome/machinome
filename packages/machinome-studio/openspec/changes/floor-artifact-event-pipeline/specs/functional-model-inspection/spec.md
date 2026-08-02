## MODIFIED Requirements

### Requirement: The shop floor refreshes a changed functional model
While a named project shop floor is open, the system SHALL keep the maker's
functional-model view current with the project's model source. The system SHALL
build the project when its model source changes, and SHALL separately observe
the project's published build output. Each file that becomes newly published
there SHALL be reported to connected browsers as one event naming that file and
nothing further about it, without regard to what the file is. The system SHALL
report such an event whichever publisher produced the file, including a
publisher that is not the shop. The system SHALL NOT report the removal of a
file, SHALL NOT compare, open, or interpret published contents to decide what to
report, and SHALL NOT import or execute project Python.

#### Scenario: Any author changes the model
- **WHEN** the project's model source changes while the shop floor is open, by whichever author changed it
- **THEN** the system builds the model and reports each artifact the build published

#### Scenario: A publisher other than the shop changes the model
- **WHEN** a build the shop did not run publishes an artifact into the project's build output while the shop floor is open
- **THEN** the system reports that artifact to connected browsers just as it reports one from its own build

#### Scenario: One part of the model changes
- **WHEN** a change to the model republishes one artifact and leaves the project's other artifacts untouched
- **THEN** the system reports that one artifact and reports no event for the untouched ones

#### Scenario: A rebuild produces no change to the published model
- **WHEN** a build completes and republishes no artifact
- **THEN** the system reports no model artifact to connected browsers

#### Scenario: A node is removed from the model
- **WHEN** a change removes a node and its artifact ceases to be published
- **THEN** the system reports the published artifacts that changed and reports no event naming the removed artifact

### Requirement: The shop floor reports a failed model build
A failed build records itself in the project's build output. The system SHALL
report that record to connected browsers as published build output, on the same
terms as any other artifact and whichever publisher produced it, and SHALL keep
every artifact that is currently published available for inspection. A partially
updated model is a legitimate published state: the system SHALL NOT withhold
published artifacts, restore superseded ones, or represent the model as
complete. The system SHALL NOT maintain a separate report of a build failure it
observed, and SHALL NOT read the failure record to decide what to report.

Being unable to run a build at all is a failure of the shop rather than of the
model, produces no build output, and SHALL be reported separately.

#### Scenario: The model source is broken
- **WHEN** the project's model source changes so that the build the shop runs fails
- **THEN** the maker is shown that the build failed together with the reported reason, and the artifacts published so far remain inspectable

#### Scenario: A build the shop did not run fails
- **WHEN** a build the shop did not run fails and records the failure in the project's build output
- **THEN** the maker is shown that failure on the same terms as one from the shop's own build

#### Scenario: A failing build has already published part of the model
- **WHEN** a build publishes some artifacts and then fails before publishing the rest
- **THEN** the system reports the failure and leaves the newly published artifacts in place rather than presenting the model as it was before the build

#### Scenario: The maker fixes the model
- **WHEN** a build succeeds after a previously reported failure, withdrawing the failure record and republishing the model
- **THEN** the reported failure is cleared
- **AND** the browser is told about each artifact that build republished

#### Scenario: The build cannot be run
- **WHEN** the shop cannot run a build of the project at all
- **THEN** the maker is told that the shop could not build, distinctly from the model having failed to build

## ADDED Requirements

### Requirement: The shop floor serves an artifact through a concurrent republication
The system SHALL serve any artifact of the project's published build output for
as long as that artifact is published, including while another artifact of the
same model is being republished. A publication occurring between a request and
its response SHALL NOT cause the system to report the requested artifact as
unknown. The system SHALL serve nothing outside the project's build output.

#### Scenario: An artifact is requested while the model is republished
- **WHEN** the browser requests a published artifact at the moment a build republishes another artifact of the same model
- **THEN** the system serves the requested artifact rather than reporting it unknown

#### Scenario: An artifact is requested while it is itself being replaced
- **WHEN** the browser requests an artifact that a build is concurrently replacing
- **THEN** the system serves either the previous or the new artifact in full, and never a partially written one

#### Scenario: A path outside the build output is requested
- **WHEN** a request names a path that resolves outside the project's published build output
- **THEN** the system reports it unknown and serves nothing
