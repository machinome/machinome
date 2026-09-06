## MODIFIED Requirements

### Requirement: Opening a project starts a session
Opening a project SHALL start a session for it: a prepared project repository,
a model build, a watch on that project's sources, a conversation, and the
standing agents its profile declares. A session SHALL belong to exactly one
openable hub entry — a project repository together with the one model that entry
names — and SHALL be the only thing through which work on that entry happens.

The maker SHALL be told that opening is under way while it is, and SHALL be told
the outcome when it finishes.

When the entry's model already holds a complete, valid publication, the session
SHALL become available on that publication without waiting for its build to
finish: the agents start, the conversation is available, and the model is shown
from what is already published. The build SHALL still run, and the maker SHALL be
told that the model is being brought up to date until it completes, so a
publication that is not yet current is never presented as settled. Its result
SHALL reach the maker through the same live model channel a rebuild uses, and a
build failure SHALL be reported rather than swallowed because the session
opened first.

When the entry's model holds no complete, valid publication — it is being
created, or has never been built — opening SHALL wait for the build, because
there is nothing to present.

The repository boundary SHALL be verified before any agent starts, whether or
not the build is awaited.

#### Scenario: The maker opens a project
- **WHEN** the maker opens a listed openable project
- **THEN** the shop reports that the project is opening, prepares it, and reports it as open with its profile's agents present and its conversation available

#### Scenario: The maker opens one model of a multi-model project
- **WHEN** the maker opens a model listed inside a multi-model project
- **THEN** the session prepares that repository, builds and watches that model, and presents that model's publication

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

### Requirement: A project has at most one session
The shop SHALL hold at most one session per openable hub entry. A request to
open an entry that is already open SHALL join that existing session rather than
start a second one, however many browsers ask and whatever they were doing
before.

The shop SHALL NOT limit how many different entries are open at once, including
two models of one project repository.

#### Scenario: A second browser opens an open project
- **WHEN** a maker opens a project that already has a session
- **THEN** that browser joins the existing session and sees its current agents and conversation, and no second session is started

#### Scenario: Several projects are open at once
- **WHEN** the maker opens several different projects
- **THEN** each has its own session with its own agents, conversation, model, and build, all running at the same time

#### Scenario: Two models of one repository are open at once
- **WHEN** the maker opens two models declared by the same project repository
- **THEN** each model has its own session, agents, conversation, build, and watch, and neither joins nor closes the other

## ADDED Requirements

### Requirement: A session tells its agents which model it owns

When a session belongs to one model of a multi-model project, the shop SHALL
give that session's agents the name of that model without their having to
determine it, and every model build, model test, and published artifact the
session performs or serves SHALL be that model's. Two sessions on one repository
SHALL share only what the repository itself holds; neither SHALL build, publish,
or present the other's model.

#### Scenario: An agent works on its own model
- **WHEN** an agent of a session opened on one model of a multi-model project builds the model
- **THEN** the build is of that session's model, and the sibling model's publication is untouched

#### Scenario: Two model sessions build at the same time
- **WHEN** both models of one repository are open and each is building
- **THEN** each build publishes into its own model's build directory and neither waits on the other's publication
