## MODIFIED Requirements

### Requirement: The workspace menu preserves live shop context
The Model context panel SHALL show the current functional model's supported
assembly navigator when that model is mounted, alongside every
profile-declared agent's profile-provided display label and live state using
the run data of the project that workspace shows. The assembly navigator SHALL
not require or invent model data outside the viewer's published assembly, and
the panel SHALL NOT require or invent separate profile display labels, build
metadata, or per-agent assignment detail. It SHALL NOT show an agent belonging
to another open project.

#### Scenario: The default profile is visible
- **WHEN** the maker opens the workspace of a project declaring `builder`
- **THEN** the Model panel shows the mounted model's assembly navigator and
  Builder's live state

#### Scenario: Fordesmac is visible
- **WHEN** the maker opens the workspace of a project declaring `fordesmac`
- **THEN** the Model panel shows the mounted model's assembly navigator and
  Foreman, Designer, Machinist, and Librarian

#### Scenario: An agent changes work state
- **WHEN** a declared agent's state changes while its project's workspace is open
- **THEN** that agent's state updates without a page reload

#### Scenario: Two project workspaces are open at once
- **WHEN** the maker views two open projects in two browser locations
- **THEN** each Model panel shows only its own project's assembly and agents
  and their states
