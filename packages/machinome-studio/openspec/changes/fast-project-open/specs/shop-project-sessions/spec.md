## MODIFIED Requirements

### Requirement: Opening a project starts a session
Opening a project SHALL start a session for it: a prepared project repository,
a model build, a watch on that project's sources, a conversation, and the
standing agents its profile declares. A session SHALL belong to exactly one
project and SHALL be the only thing through which work on that project happens.

The maker SHALL be told that opening is under way while it is, and SHALL be told
the outcome when it finishes.

When the project already holds a complete, valid publication, the session SHALL
become available on that publication without waiting for its build to finish:
the agents start, the conversation is available, and the model is shown from
what is already published. The build SHALL still run, and the maker SHALL be
told that the model is being brought up to date until it completes, so a
publication that is not yet current is never presented as settled. Its result
SHALL reach the maker through the same live model channel a rebuild uses, and a
build failure SHALL be reported rather than swallowed because the session
opened first.

When the project holds no complete, valid publication — it is being created, or
has never been built — opening SHALL wait for the build, because there is
nothing to present.

The repository boundary SHALL be verified before any agent starts, whether or
not the build is awaited.

#### Scenario: The maker opens a project
- **WHEN** the maker opens a listed openable project
- **THEN** the shop reports that the project is opening, prepares it, and reports it as open with its profile's agents present and its conversation available

#### Scenario: The maker watches a project open
- **WHEN** a project is opening and the maker is looking at the hub
- **THEN** the hub shows that project as opening until it is open or has failed, without the maker asking again

#### Scenario: A newly requested project is not on disk yet
- **WHEN** creation has been accepted and project preparation has not yet created its directory
- **THEN** the hub still shows a provisional card in the `creating` state until the project opens or fails

#### Scenario: An already-built project opens on what is published
- **WHEN** the maker opens a project whose published model is complete and valid
- **THEN** the session becomes available with its agents and conversation, and the model is shown from that publication, without waiting for the build

#### Scenario: The model is brought up to date behind an open session
- **WHEN** a session has opened on an existing publication and its build is still running
- **THEN** the maker is told the model is being brought up to date, and is told when it is current

#### Scenario: The build behind an open session fails
- **WHEN** a session opened on an existing publication and its build then fails
- **THEN** the failure is reported to the maker, and the previously published model remains available

#### Scenario: A project with nothing published waits
- **WHEN** the maker opens a project that has never been built, or creates a new one
- **THEN** opening waits for the build, because there is no publication to present
