## MODIFIED Requirements

### Requirement: A run selects one trusted runtime profile
The shop SHALL resolve the profile for a session from exactly one of two
sources, in this order of precedence: the project's declared profile when it
declares one, and otherwise the shop default `fordesmac`. It SHALL resolve a
selected profile only from `profiles/<profile-id>/profile.toml` beneath the
primary shop checkout. The broker-only and orchestrated entry points SHALL use
the same profile selection contract. A project's declaration SHALL govern every
session of that project; the shop SHALL provide no way to open a project under a
profile it does not declare.

#### Scenario: The default profile is selected
- **WHEN** a project that declares no profile is opened
- **THEN** the shop selects the repository-owned `fordesmac` profile

#### Scenario: The project's declared profile is selected
- **WHEN** a project that declares a profile is opened
- **THEN** the shop selects the profile that project declares

#### Scenario: An unknown or escaping profile is declared
- **WHEN** a project's declared profile does not identify a valid lowercase kebab-case directory directly beneath `profiles/`
- **THEN** the shop refuses to open that project with an error, before preparing it or starting a backend, and remains available for every other project
