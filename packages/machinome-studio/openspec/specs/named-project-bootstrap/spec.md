# named-project-bootstrap Specification

## Purpose

Prepare exactly one safely named workspace project as an independent,
buildable repository before the shop runtime starts.

## Requirements

### Requirement: Every shop opens for one named workspace project
The system SHALL require a project name for every shop-open request and SHALL
resolve that identity only to `projects/<name>` in the configured shop
workspace. The accepted name SHALL be a single lowercase kebab-case directory
name and SHALL NOT resolve outside the workspace project directory.

#### Scenario: A maker names a workspace project
- **WHEN** the maker asks to open the shop for a valid project name
- **THEN** the system selects the corresponding `projects/<name>` project as the only working project for that shop run

#### Scenario: No project name is supplied
- **WHEN** a shop-open request omits the project name
- **THEN** the system rejects the request before opening any part of the shop and explains that a project name is required

#### Scenario: A project name is unsafe or ambiguous
- **WHEN** a supplied project name contains a path separator, dot component, uppercase character, whitespace, or otherwise does not form one lowercase kebab-case name
- **THEN** the system rejects the request without accessing a project outside `projects/`

### Requirement: A missing named project receives a standard first state
If `projects/<name>` does not exist, the system SHALL create a standard
solid-node project there and SHALL establish that directory as an independent
Git repository with the generated scaffold recorded before any project-writing
agent starts.

#### Scenario: The named project does not exist
- **WHEN** the maker opens the shop for a valid name absent from `projects/`
- **THEN** the system creates the standard solid-node scaffold at that location and records it as the initial state of that project repository

#### Scenario: Project creation fails
- **WHEN** the standard scaffold or its initial repository state cannot be created
- **THEN** the system starts no floor service or agent and reports the failed project-preparation stage and location

### Requirement: An existing named project is reused without replacement
If `projects/<name>` exists, the system SHALL use it only when that exact
directory is the root of an independent Git repository. The system SHALL NOT
replace, reinitialize, stage, commit, or otherwise repair an existing project
as a side effect of opening the shop.

#### Scenario: The named project already exists as a project repository
- **WHEN** the maker opens the shop for an existing valid project whose exact directory is its Git repository root
- **THEN** the system reuses that project without recreating or committing it

#### Scenario: The existing location is not the project repository root
- **WHEN** `projects/<name>` exists but is not itself the root of an independent Git repository
- **THEN** the system starts no floor service or agent and reports the repository validation failure

### Requirement: Every project agent works in the verified project root
The system SHALL give the foreman, designer, and machinist the same verified
`projects/<name>` repository root as their project working directory while
retaining shop-owned role instructions outside the project repository.

#### Scenario: The named project is ready
- **WHEN** the system starts the agent team after preparing the named project
- **THEN** all three project agents work from that exact project repository root
