## ADDED Requirements

### Requirement: A project declares its default runtime profile
The `[tool.solid-node-studio]` table SHALL admit a `profile` key whose value is a
string naming a runtime profile. That value SHALL select the profile for any run
of that project in which `--profile` is not given, and SHALL be overridden by
`--profile` when it is given.

A value that is not a well-formed lowercase kebab-case profile ID SHALL be
rejected on every run of that project, whether or not the run uses it, because it
cannot name a profile under any invocation. A well-formed value that does not
resolve to a profile beneath the shop's `profiles/` directory SHALL be rejected
on any run that uses it, and the run SHALL NOT fall back to the default profile.
Every such rejection SHALL identify the project file and the offending value.

A project that declares no `profile` key, no `[tool.solid-node-studio]` table, or
no `pyproject.toml` at all SHALL be opened under the profile `--profile` names or
the shop default. Scaffolding a new project SHALL NOT write a `profile` key.

#### Scenario: A project declares its profile
- **WHEN** a project's `pyproject.toml` declares `profile = "fordesmac"` and the shop opens for that project without `--profile`
- **THEN** the run opens the `fordesmac` roster

#### Scenario: The option overrides the declared profile
- **WHEN** a project declares `profile = "fordesmac"` and the shop opens with `--profile builder`
- **THEN** the run opens the `builder` roster and the project file is not modified

#### Scenario: A project declares no profile
- **WHEN** a project declares no `profile` key and the shop opens without `--profile`
- **THEN** the run opens the shop default profile

#### Scenario: A malformed profile value is always rejected
- **WHEN** a project's `profile` value is not lowercase kebab-case, such as a path or a value containing a separator
- **THEN** the run exits with an error naming the project file and the value, even when `--profile` is given, and before any project or backend side effect

#### Scenario: An unresolvable declared profile is rejected rather than replaced
- **WHEN** a project declares a well-formed profile that no `profiles/<profile-id>/profile.toml` provides and no `--profile` is given
- **THEN** the run exits with an error naming the project file and the value rather than opening the default profile

#### Scenario: An overridden declaration is not required to resolve
- **WHEN** a project declares a well-formed profile that this shop checkout does not provide and the shop opens with a valid `--profile`
- **THEN** the run opens the profile the option names

#### Scenario: A scaffolded project declares no profile
- **WHEN** the shop opens for a named project that must first be scaffolded
- **THEN** the scaffold contains no `profile` key and the run opens the profile `--profile` names or the shop default

## MODIFIED Requirements

### Requirement: Tools and permission remain profile-owned
A project SHALL NOT select tool policy or Claude permission policy. Those SHALL
continue to resolve from the active profile alone. Declaring a `profile` key
SHALL select one repository-owned profile package in its entirety and SHALL NOT
make any policy that package carries project-authored: a project SHALL NOT
select, widen, narrow, or otherwise state tool or permission policy
independently of the profile it names. A `[tool.solid-node-studio]` table SHALL
reject keys other than those this capability defines rather than ignoring them,
so a reasoning level SHALL be selectable only as a segment of an agent's runtime
value and never as a key of its own.

#### Scenario: A project attempts to widen tool policy
- **WHEN** a project's runtime table declares a tool or permission key
- **THEN** the run exits with an error identifying the unsupported key

#### Scenario: A reasoning level is declared as a separate key
- **WHEN** a project's runtime table declares an `effort` key beside an agent's runtime value
- **THEN** the run exits with an error identifying the unsupported key

#### Scenario: A selected model keeps profile tools and permission
- **WHEN** a project selects a Claude model and reasoning level for an agent
- **THEN** the agent opens with the project's model and reasoning level and the profile's tool policy and permission

#### Scenario: A declared profile carries its own policy unchanged
- **WHEN** a project declares a profile and the run opens under it
- **THEN** every agent resolves the tool and permission policy that profile declares, unmodified by anything else in the project file

### Requirement: Selections are resolved against the active profile roster
Resolution SHALL apply a selection only to an agent the active profile declares.
A syntactically valid selection keyed to an agent outside the active roster
SHALL be ignored rather than rejected, because a project may be opened under
several profiles with different rosters: a project that declares a profile may
still be opened under another one by `--profile`. The launcher SHALL report
every key it ignored so a misspelled agent ID is visible rather than silently
inert. An agent key that is not a well-formed lowercase kebab-case agent ID
SHALL be rejected.

#### Scenario: A project carries selections for two rosters
- **WHEN** a project declares selections for both `builder` and the Fordesmac specialists and is opened under `builder`
- **THEN** the Builder selection applies, the Fordesmac keys are ignored, and the ignored keys are reported

#### Scenario: A declared profile is overridden and its selections fall outside the roster
- **WHEN** a project declares `fordesmac` with selections for its specialists and is opened with `--profile builder`
- **THEN** the run opens `builder`, the specialist keys are ignored rather than rejected, and they are reported

#### Scenario: An agent ID is misspelled
- **WHEN** a project declares a selection for an agent key absent from the active roster
- **THEN** the run opens without applying it and reports that the key was ignored

#### Scenario: An agent key is malformed
- **WHEN** an agent key is not lowercase kebab-case
- **THEN** the run exits with an error before any project or backend side effect
