## MODIFIED Requirements

### Requirement: The shop floor builds the selected functional model before opening
When opening a named project shop floor, the system SHALL use a solid-node CLI
one-shot build of the project's default `root` functional model before starting
the Floor service or agent runtime. The build SHALL produce a complete
`_build` viewer snapshot and all referenced model files before Floor can be
declared open. The Model area SHALL consume only that completed snapshot and
its referenced model files. Floor MAY list, read, and atomically replace
verified project source as inert text for the Code area, but it SHALL NOT
import, execute, reload, or interpret that source.

#### Scenario: A named project has a buildable default model
- **WHEN** the maker opens the shop for a named project whose default `root` model builds successfully
- **THEN** the system completes one solid-node CLI build and makes the complete `_build` model artifacts available before starting Floor

#### Scenario: The build command succeeds without a complete publication
- **WHEN** the initial build does not leave a readable viewer snapshot and every referenced model artifact
- **THEN** the system treats preparation as failed and does not start Floor or its agents

#### Scenario: The maker first opens the reported browser location
- **WHEN** the system has reported a named project shop as open
- **THEN** the browser can retrieve the already-validated initial viewer snapshot rather than receiving a no-build response

#### Scenario: The maker opens project source
- **WHEN** the maker reads a verified text file through Code
- **THEN** Floor returns inert text without using it as functional-model input or executing it

### Requirement: The shop floor refreshes a changed functional model
While a named project shop floor is open, the system SHALL keep the maker's
functional-model view current with the project's model source. The system SHALL
build the project when its model source changes, including an atomic maker save
from Code, and SHALL separately observe the project's published build output.
Each file that becomes newly published there SHALL be reported to connected
browsers as one event naming that file and nothing further about it, without
regard to what the file is. The system SHALL report such an event whichever
publisher produced the file, including a publisher that is not the shop. The
system SHALL NOT report the removal of a file, SHALL NOT compare, open, or
interpret published contents to decide what to report, and SHALL NOT import or
execute project Python. A build reads the model source it loads; the system
SHALL treat only source that is created, modified, relocated, or removed as
changed, and SHALL NOT treat a build's own reads as a change. The Code save
operation SHALL NOT invoke a separate build.

#### Scenario: Any author changes the model
- **WHEN** the project's model source changes while the shop floor is open, by whichever author changed it
- **THEN** the system builds the model and reports each artifact the build published

#### Scenario: The maker saves Python source in Code
- **WHEN** an accepted Code save atomically replaces a Python model source file
- **THEN** the existing source watcher observes it and coalesces it into the same build path used for an agent write

#### Scenario: The maker saves a non-source file in Code
- **WHEN** an accepted Code save changes a file the source watcher does not treat as model source
- **THEN** the Code save operation starts no model build of its own

#### Scenario: A publisher other than the shop changes the model
- **WHEN** a build the shop did not run publishes an artifact into the project's build output while the shop floor is open
- **THEN** the system reports that artifact to connected browsers just as it reports one from its own build

#### Scenario: One part of the model changes
- **WHEN** a change to the model republishes one artifact and leaves the project's other artifacts untouched
- **THEN** the system reports that one artifact and reports no event for the untouched ones

#### Scenario: A build reads the model source it is building
- **WHEN** a build the shop ran reads the project's model source files while the shop floor is open
- **THEN** the system runs no further build on account of those reads

#### Scenario: A rebuild produces no change to the published model
- **WHEN** a rebuild completes and leaves the published model artifacts unchanged
- **THEN** the system reports no model artifact to connected browsers

#### Scenario: A node is removed from the model
- **WHEN** a change removes a node and its artifact ceases to be published
- **THEN** the system reports the published artifacts that changed and reports no event naming the removed artifact
