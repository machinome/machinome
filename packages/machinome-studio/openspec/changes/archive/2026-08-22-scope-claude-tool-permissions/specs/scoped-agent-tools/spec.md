## MODIFIED Requirements

### Requirement: Backend scope
The scoped-agent-tools capability SHALL be available on every selectable
backend. A backend SHALL be selectable only if it can open a session whose
reachable tool set is exactly the profile-declared one; a backend that retains
native file, shell, or network tools regardless of the declared policy SHALL NOT
be selectable. The `claude` and `opencode` backends satisfy this; the retired
`codex` backend did not.

A scoped session SHALL run with its runtime's permission checking active. The
floor tool surface is the boundary, so no backend SHALL open a session with
permission checks disabled, and no profile declaration SHALL be able to disable
them. A backend SHALL grant the session's declared tools by name so the role
never waits for a confirmation nobody can give.

#### Scenario: Role selects claude or opencode with scoped tools
- **WHEN** a role configured for scoped tools opens on the `claude` or
  `opencode` backend
- **THEN** the session has no native file, shell, or network tool reachable,
  only the floor-provided MCP tool set

#### Scenario: A role declares fewer capabilities than the whole tool set
- **WHEN** a role's declared capabilities resolve to a proper subset of the
  floor tool set
- **THEN** the session reaches exactly that subset, and the tools outside it are
  neither advertised nor callable

#### Scenario: A scoped session keeps permission checking on
- **WHEN** any scoped role session opens
- **THEN** it runs with its runtime's permission checks active while its
  declared tools execute without confirmation

#### Scenario: Claude reports the floor MCP server pending before connected
- **WHEN** a scoped Claude role's first real broker envelope triggers init
  frames with the floor server `pending` before a later frame reports it
  `connected`
- **THEN** the envelope remains the session's first user message and its
  delivery waits within a separate bounded readiness deadline, succeeding only
  after the connected frame exposes exactly the expected scoped tools

#### Scenario: Claude role process waits for its first input before init
- **WHEN** a scoped Claude process stays alive but emits no init frame before
  receiving user input
- **THEN** project opening manifests the role after the bounded process-exit
  grace without a warm-up message or a readiness deadlock

#### Scenario: Claude MCP readiness never succeeds
- **WHEN** the first broker delivery triggers initialization but the Claude
  process exits, reports a terminal floor-server failure, or does not connect
  before the bounded readiness deadline
- **THEN** that delivery fails with the relevant process, MCP, or timeout
  evidence and the failed role process is stopped

#### Scenario: A backend that cannot enforce tool policy is not selectable
- **WHEN** a project or maker names a backend whose sessions keep native tools
  the profile did not declare, such as `codex`
- **THEN** the selection is rejected rather than opening a session outside the
  declared tool policy
