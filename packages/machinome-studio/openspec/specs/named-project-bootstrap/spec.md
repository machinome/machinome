# named-project-bootstrap Specification

## Purpose

Prepare a safely named workspace project as an independent, buildable
repository before its session starts.
## Requirements
### Requirement: Every shop opens for one named workspace project
The system SHALL require an entry path for every project-open request and SHALL
resolve that identity only to a directory beneath the configured working folder,
optionally followed by the name of a model that directory's manifest declares.
Every path segment SHALL be one safe directory or model name, and the resolved
project directory SHALL NOT lie outside the working folder. The system SHALL NOT
impose a stylistic naming convention on project directories.

A path the system cannot accept SHALL be refused for that request alone. It
SHALL NOT prevent the shop from starting, prevent the working folder from being
listed, or prevent another project from being opened.

#### Scenario: A maker names a workspace project
- **WHEN** the maker asks to open a project by a valid entry path
- **THEN** the system selects the corresponding directory beneath the working folder, and the model that path names, as the only working entry for that session

#### Scenario: No project name is supplied
- **WHEN** a project-open request omits the entry path
- **THEN** the system rejects the request before opening any part of a session and explains that an entry path is required

#### Scenario: A project name is unsafe or ambiguous
- **WHEN** a supplied entry path is empty, contains a dot component, is absolute, or does not identify one directory beneath the working folder
- **THEN** the system rejects the request without accessing anything outside the working folder, and the shop and every other project remain available

#### Scenario: A path names a model the project does not declare
- **WHEN** a supplied entry path names a model that the resolved project's manifest does not declare
- **THEN** the system rejects the request, opens no session, and leaves the project untouched

#### Scenario: A project name uses a different style
- **WHEN** a supplied project name uses underscores, uppercase characters, whitespace, or another filesystem-safe style
- **THEN** the system accepts the name without warning about a naming convention

### Requirement: A missing named project receives a standard first state
If the named project does not exist at its resolved location beneath the working
folder, the system SHALL create a standard solid-node project there, SHALL
record the runtime profile chosen for it in that project's own configuration,
and SHALL establish the directory as an independent Git repository with the
generated scaffold recorded before any project-writing agent starts. The system
SHALL create a project only as a direct child of an existing folder beneath the
working folder, and SHALL NOT create intermediate folders.

#### Scenario: The named project does not exist
- **WHEN** the maker creates a project by a valid name absent from the folder being listed
- **THEN** the system creates the standard solid-node scaffold at that location, records the chosen profile in it, and records it as the initial state of that project repository

#### Scenario: The folder to create in does not exist
- **WHEN** a creation request names a folder that does not exist beneath the working folder
- **THEN** the system creates nothing and reports that the folder is not there

#### Scenario: Project creation fails
- **WHEN** the standard scaffold or its initial repository state cannot be created
- **THEN** the system starts no agent for it, reports the failed project-preparation stage and location, and leaves the shop and every other project available

### Requirement: An existing named project is reused without replacement
If the named project exists, the system SHALL use it only when that exact
directory is the root of an independent Git repository. The system SHALL NOT
replace, reinitialize, stage, commit, or otherwise repair an existing project as
a side effect of opening it.

An existing directory that is not such a repository SHALL be reported as a
project that cannot be opened, and SHALL remain visible to the maker rather than
being hidden or altered.

#### Scenario: The named project already exists as a project repository
- **WHEN** the maker opens an existing valid project whose exact directory is its Git repository root
- **THEN** the system reuses that project without recreating or committing it

#### Scenario: The existing location is not the project repository root
- **WHEN** a directory beneath the working folder is not itself the root of an independent Git repository
- **THEN** the system opens no session for it, reports it to the maker as unopenable with that reason, and leaves it untouched

### Requirement: Every project agent works in the verified project root
The system SHALL give every standing agent declared by the project's profile the
same verified project repository root as its project working directory while
retaining shop-owned profile prompts and runtime skills outside the project
repository. An agent SHALL receive the root of its own project only. When the
session belongs to one declared model of that project, the system SHALL also
give the agent the name of that model.

#### Scenario: The Builder project is ready
- **WHEN** the system starts the `builder` profile after preparing the chosen project
- **THEN** Builder works from that exact project repository root

#### Scenario: The Fordesmac project is ready
- **WHEN** the system starts the `fordesmac` profile after preparing the chosen project
- **THEN** Foreman, Designer, Machinist, and Librarian all work from that exact project repository root

#### Scenario: Several projects are open at once
- **WHEN** several projects are open at the same time
- **THEN** each project's agents work from that project's own verified repository root and from no other

#### Scenario: Two models of one project are open at once
- **WHEN** two sessions are open on two declared models of one project repository
- **THEN** the agents of both work from that repository's root, and each is told the model its own session owns

