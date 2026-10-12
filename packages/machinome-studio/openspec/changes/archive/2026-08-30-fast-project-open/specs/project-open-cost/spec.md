## ADDED Requirements

### Requirement: The shop does not re-derive what it already holds

Opening a project SHALL NOT repeat work whose result the shop already has and
which cannot differ between projects or between opens.

The installed framework's viewer bundle — its path and its API version — is a
property of the shop's own installation, not of any project. The shop SHALL
resolve it once for the running shop and reuse it for every session, rather than
asking the framework again on each open.

The shop SHALL still enforce the viewer API version it requires, and SHALL still
fail an open when no usable bundle is installed. Resolving once changes when the
question is asked, never the answer or its consequence.

#### Scenario: Opening several projects asks the framework once

- **WHEN** the maker opens several projects in one running shop
- **THEN** the framework is asked for its viewer bundle once, and every session
  uses that same bundle path and API version

#### Scenario: Reopening a project asks nothing again

- **WHEN** a project is closed and opened again in the same running shop
- **THEN** the framework is not asked for its viewer bundle again

#### Scenario: An unusable viewer installation still fails the open

- **WHEN** the installed viewer bundle is missing, or its API version is below
  the version the shop requires
- **THEN** opening fails with that reason, as it does today
