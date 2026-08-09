## MODIFIED Requirements

### Requirement: A run selects one trusted runtime profile
The shop launcher SHALL accept `--profile <profile-id>` and SHALL resolve the
profile for a run from exactly one of three sources, in this order of
precedence: the `--profile` option when it is given, the active project's
declared profile when the option is absent and the project declares one, and
otherwise the shop default `fordesmac`. It SHALL resolve a selected profile only
from `profiles/<profile-id>/profile.toml` beneath the primary shop checkout. The
broker-only and orchestrated entry points SHALL use the same profile selection
contract. A project SHALL declare a profile only as the default for its own
runs; `--profile` SHALL override that declaration for one run without altering
the project.

#### Scenario: The default profile is selected
- **WHEN** the user opens a shop without `--profile` for a project that declares no profile
- **THEN** the runtime selects the repository-owned `fordesmac` profile

#### Scenario: The project's declared profile is selected
- **WHEN** the user opens a shop without `--profile` for a project that declares one
- **THEN** the runtime selects the profile that project declares

#### Scenario: The option overrides the project
- **WHEN** the user opens a shop with `--profile builder` for a project that declares `fordesmac`
- **THEN** the runtime selects `builder` for that run and the project's declaration is unchanged

#### Scenario: An unknown or escaping profile is selected
- **WHEN** `--profile` does not identify a valid lowercase kebab-case directory directly beneath `profiles/`
- **THEN** the runtime exits with an error before preparing a project, binding a listener, or starting a backend

### Requirement: Profile validation precedes every project side effect
The launcher SHALL complete profile filesystem, schema, prompt, skill, topology,
and runtime-table validation before it creates or validates a project
repository, invokes `solid`, binds an HTTP listener, or starts an agent backend.

Because both the profile's identity and the per-agent runtime selections live in
the project, the launcher SHALL first perform a bounded, side-effect-free read of
the project's `pyproject.toml`: resolving and containment-checking the project
path and parsing that one file. That read SHALL NOT create, scaffold,
initialize, modify, or build anything, and SHALL tolerate a project that does not
yet exist. Profile resolution, profile validation, and runtime resolution SHALL
all complete before any project side effect follows. A validation error SHALL
identify the profile or project file and the invalid field or path.

#### Scenario: An invalid profile is used with a missing project
- **WHEN** the selected profile is invalid and the named project does not exist
- **THEN** the runtime reports the profile error and does not scaffold or initialize the project

#### Scenario: Reading project configuration creates nothing
- **WHEN** the launcher reads the profile and runtime selection for a project that does not yet exist
- **THEN** no directory, repository, scaffold, or build is produced by that read, the profile resolves from `--profile` or the default, and runtime resolution falls back to the profile defaults

#### Scenario: An invalid runtime selection stops the run early
- **WHEN** a project's runtime selection is malformed and the named project exists
- **THEN** the runtime reports the offending project file and value and does not invoke `solid`, bind a listener, or start a backend

#### Scenario: An unresolvable project-declared profile stops the run early
- **WHEN** a project declares a profile that does not resolve and no `--profile` is given
- **THEN** the runtime reports the offending project file and value and does not invoke `solid`, bind a listener, or start a backend
