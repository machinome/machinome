## MODIFIED Requirements

### Requirement: A missing named project receives a standard first state
If the named project does not exist beneath the working folder, the system SHALL
create a standard solid-node project there, SHALL record the runtime profile
chosen for it in that project's own configuration, SHALL establish the
directory as an independent Git repository, and SHALL attempt the initial model
build and canonical project screenshot before recording the generated scaffold.
A successfully rendered `screenshot.png` SHALL be included in that initial
repository state. A build or screenshot failure SHALL preserve the existing
project-preparation failure behavior and SHALL NOT cause the initial Git commit
to fail solely because the image is absent. The generated scaffold SHALL be
recorded before any project-writing agent starts.

#### Scenario: The named project does not exist
- **WHEN** the maker creates a project by a valid name absent from the working folder and its initial model and screenshot render successfully
- **THEN** the system creates the standard solid-node scaffold, records its chosen profile, and records `screenshot.png` with the initial state of that project repository

#### Scenario: The initial screenshot fails
- **WHEN** the initial project can otherwise be recorded but screenshot rendering or staging fails
- **THEN** the system records the initial project state without `screenshot.png` and does not fail creation solely because the image is absent

#### Scenario: Project creation fails
- **WHEN** the standard scaffold or its required initial repository state cannot be created
- **THEN** the system starts no agent for it, reports the failed project-preparation stage and location, and leaves the shop and every other project available
