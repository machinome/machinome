## MODIFIED Requirements

### Requirement: A project declares its default runtime profile
The `[tool.solid-node-studio]` table SHALL admit a `profile` key whose value is a
string naming a runtime profile. That value SHALL select the profile for every
session of that project.

A value that is not a well-formed lowercase kebab-case profile ID SHALL be
rejected whenever that project is read, because it cannot name a profile. A
well-formed value that does not resolve to a profile beneath the shop's
`profiles/` directory SHALL be rejected when that project is opened, and the
session SHALL NOT fall back to the default profile. Every such rejection SHALL
identify the project file and the offending value, and SHALL leave the shop and
every other project available.

A project that declares no `profile` key, no `[tool.solid-node-studio]` table, or
no `pyproject.toml` at all SHALL be opened under the shop default.

Creating a project SHALL write the `profile` key the maker chose for it, so a
project created by the shop declares its profile from its first state.

#### Scenario: A project declares its profile
- **WHEN** a project's `pyproject.toml` declares `profile = "fordesmac"` and it is opened
- **THEN** the session opens the `fordesmac` roster

#### Scenario: A project declares no profile
- **WHEN** a project declares no `profile` key and it is opened
- **THEN** the session opens the shop default profile

#### Scenario: A malformed profile value is always rejected
- **WHEN** a project's `profile` value is not lowercase kebab-case, such as a path or a value containing a separator
- **THEN** the shop refuses to open that project, naming the project file and the value, before any project or backend side effect, and remains available for every other project

#### Scenario: An unresolvable declared profile is rejected rather than replaced
- **WHEN** a project declares a well-formed profile that no `profiles/<profile-id>/profile.toml` provides
- **THEN** the shop refuses to open that project, naming the project file and the value, rather than opening the default profile

#### Scenario: A created project declares its chosen profile
- **WHEN** the maker creates a project and chooses a profile for it
- **THEN** the created project's `pyproject.toml` declares that profile, and opening it again later uses that declaration without the maker choosing again

### Requirement: Selections are resolved against the active profile roster
Resolution SHALL apply a selection only to an agent the active profile declares.
A syntactically valid selection keyed to an agent outside the active roster
SHALL be ignored rather than rejected, because a project's declared profile may
change over its life while selections for its former roster remain in the file.
The shop SHALL report every key it ignored so a misspelled agent ID is visible
rather than silently inert. An agent key that is not a well-formed lowercase
kebab-case agent ID SHALL be rejected.

#### Scenario: A project carries selections for two rosters
- **WHEN** a project declares selections for both `builder` and the Fordesmac specialists and declares the profile `builder`
- **THEN** the Builder selection applies, the Fordesmac keys are ignored, and the ignored keys are reported

#### Scenario: A project changes its declared profile
- **WHEN** a project that declared `fordesmac` with selections for its specialists is changed to declare `builder` and is opened
- **THEN** the session opens `builder`, the specialist keys are ignored rather than rejected, and they are reported

#### Scenario: An agent ID is misspelled
- **WHEN** a project declares a selection for an agent key absent from the active roster
- **THEN** the session opens without applying it and reports that the key was ignored

#### Scenario: An agent key is malformed
- **WHEN** an agent key is not lowercase kebab-case
- **THEN** the shop refuses to open that project before any project or backend side effect
