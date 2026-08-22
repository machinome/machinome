## MODIFIED Requirements

### Requirement: The Claude backend operates Claude Code CLI sessions
The Claude backend SHALL launch one `claude` process per profile-declared agent
in non-interactive streaming mode, exchange newline-delimited JSON frames over
stdio, and use the active project as its working directory.

It SHALL deliver the resolved profile prompt and the agent's skill catalogue as
session-level instructions so the first user message remains a broker envelope.
It SHALL register that agent's skills with the session's tool server and SHALL
NOT name a skill's filesystem path to the session. It SHALL use the profile's
selected Claude model, effort, and available tools rather than Markdown
model/tool fields or a global adapter file.

It SHALL open every role session with the runtime's permission checking active
and SHALL NOT pass a permission mode that disables it. The role's declared
floor tools SHALL be granted by name, so a declared tool never pauses for
confirmation, and every floor tool the role did not declare SHALL be
unreachable in that session rather than merely undeclared. No built-in runtime
tool SHALL be available in a role session. The declared tool list is therefore
the entire authority the session holds; the backend SHALL NOT accept a separate
profile permission policy, and SHALL refuse to open a role whose tool policy is
not a concrete list.

It SHALL open each session with both project-level and user-level assistant
configuration, memory, hooks, plugins, and other operator-machine
customization disabled. It SHALL NOT read, store, forward, or require a
credential, and SHALL invoke the `claude` command using authentication the
operator has already configured.

#### Scenario: Claude starts one process per profile agent
- **WHEN** either initial profile opens with Claude
- **THEN** Claude starts exactly one process for every agent declared by that profile

#### Scenario: The role contract does not consume a conversational turn
- **WHEN** Claude opens a profile agent
- **THEN** the prompt contract and skill catalogue are delivered as session-level instructions and the first user message is a broker envelope

#### Scenario: Runtime capability comes from the selected profile
- **WHEN** Claude opens Designer from `fordesmac`
- **THEN** it uses the model, effort, and available tools that profile declares
  for Claude, only Designer's validated profile prompt and Designer's own
  allowlisted skills, and no global role adapter

#### Scenario: A scoped role can load its declared skills
- **WHEN** Claude opens a scoped role whose profile agent declares skills
- **THEN** that session's reachable tool set includes the floor skill-loading
  tool alongside the tools its declared capabilities resolve to

#### Scenario: A declared tool runs without confirmation
- **WHEN** a role calls a floor tool its profile declared
- **THEN** the call executes without a confirmation prompt and without the
  session running with permission checking disabled

#### Scenario: Permission checking is never disabled
- **WHEN** Claude opens any role session
- **THEN** the invocation carries no permission mode that bypasses, presumes,
  or otherwise disables the runtime's permission checks

#### Scenario: A floor tool the role did not declare is unreachable
- **WHEN** a role's profile declares capabilities resolving to fewer than every
  floor tool
- **THEN** the session cannot see or call the remaining floor tools

#### Scenario: A role without a concrete tool list does not open
- **WHEN** a role's resolved Claude tool policy is not a concrete list
- **THEN** opening that role fails instead of starting a session whose tool set
  the backend cannot bound

#### Scenario: Operator machine configuration does not reach an agent
- **WHEN** the active project or the machine has project-level or user-level assistant configuration, memory, hooks, or plugins
- **THEN** the role session is opened without loading any of them
