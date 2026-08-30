# shop-project-sessions Specification

## Purpose

Define isolated, concurrent, and ephemeral project sessions that can be opened
and closed independently within one running shop.
## Requirements
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

### Requirement: A project has at most one session
The shop SHALL hold at most one session per project. A request to open a project
that is already open SHALL join that existing session rather than start a second
one, however many browsers ask and whatever they were doing before.

The shop SHALL NOT limit how many different projects are open at once.

#### Scenario: A second browser opens an open project
- **WHEN** a maker opens a project that already has a session
- **THEN** that browser joins the existing session and sees its current agents and conversation, and no second session is started

#### Scenario: Several projects are open at once
- **WHEN** the maker opens several different projects
- **THEN** each has its own session with its own agents, conversation, model, and build, all running at the same time

### Requirement: An agent reaches only its own session
Every session SHALL have an identity distinct from every other session, past or
present, and the shop SHALL give each agent the identity of the session it
belongs to without that agent having to determine, state, or remember it. An
agent SHALL reach only its own session: a request carrying no session identity,
an unknown one, or one belonging to another session SHALL be refused rather than
applied to any session.

#### Scenario: An agent works in its session
- **WHEN** an agent of an open session sends a message, takes an assignment, or reports work
- **THEN** it reaches its own session without naming one, and no other open session observes it

#### Scenario: An agent of one project addresses another
- **WHEN** a request carries the identity of a session other than the one its agent belongs to
- **THEN** the shop refuses it and neither session is affected

#### Scenario: An agent outlives its session
- **WHEN** an agent process from a closed session issues a request after that session ended
- **THEN** the shop refuses it, and a later session for the same project is unaffected

### Requirement: Closing a session ends its work
The maker SHALL be able to close an open project from that project's workspace.
Closing SHALL end every agent of that session, stop watching that project, and
end the session. Closing SHALL be bounded, active work SHALL NOT prevent it, and
no process the session owned may survive it. Closing one project SHALL NOT
disturb any other open project or the shop itself.

Because a session holds no durable record, the maker SHALL be warned before
closing discards work an agent is in the middle of.

#### Scenario: The maker closes a project
- **WHEN** the maker closes an open project
- **THEN** that session's agents are ended, that project stops being watched, the project is reported as no longer open, and every other open project continues undisturbed

#### Scenario: The maker closes a project during active work
- **WHEN** the maker closes a project while one of its agents is working on an assignment
- **THEN** the shop warns that the work in progress will be discarded, and on confirmation closes within bounded time leaving no agent process behind

#### Scenario: An agent will not stop
- **WHEN** an agent of a closing session does not end when asked
- **THEN** the shop forces it to end, releases the rest of that session, and completes closing

#### Scenario: A browser is looking at a closed project
- **WHEN** a project is closed while a browser is displaying its workspace
- **THEN** that browser is returned to the hub rather than left displaying a session that no longer exists

### Requirement: A session keeps nothing after it ends
A session's conversation, agents, and work state SHALL last only as long as the
session. Reopening a project SHALL start a session with no memory of any earlier
one, and stopping the shop SHALL end every open session. The shop SHALL NOT
present an earlier session's conversation or work as belonging to a new one.

#### Scenario: The maker reopens a project
- **WHEN** the maker closes a project and opens it again
- **THEN** the new session begins with no conversation and freshly started agents

#### Scenario: The shop stops with projects open
- **WHEN** the shop stops while projects are open
- **THEN** every session ends, and after the shop starts again the hub lists those projects as not open

