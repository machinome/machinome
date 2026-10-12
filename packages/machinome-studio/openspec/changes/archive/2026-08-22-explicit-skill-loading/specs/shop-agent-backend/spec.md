## MODIFIED Requirements

### Requirement: A role-contract bootstrap is not bounded by the control-plane timeout
Opening a role loads that role's card and the catalogue of the skills it names,
which is model work whose duration is unrelated to protocol liveness. The
backend SHALL bound control-plane requests such as `initialize` and
`session/new` separately from prompt work. A role-contract bootstrap that is
still progressing SHALL NOT fail shop open because a control-plane timeout
elapsed.

#### Scenario: A slow role bootstrap still opens the shop
- **WHEN** a role's bootstrap prompt takes longer than the control-plane request timeout but completes successfully
- **THEN** the role manifests and the shop opens

#### Scenario: An unresponsive control-plane request still fails fast
- **WHEN** the subprocess does not answer `initialize` or `session/new` within the control-plane timeout
- **THEN** the backend reports the failure rather than waiting for the longer prompt budget

### Requirement: The Claude backend operates Claude Code CLI sessions
The Claude backend SHALL launch one `claude` process per profile-declared agent
in non-interactive streaming mode, exchange newline-delimited JSON frames over
stdio, and use the active project as its working directory.

It SHALL deliver the resolved profile prompt and the agent's skill catalogue as
session-level instructions so the first user message remains a broker envelope.
It SHALL register that agent's skills with the session's tool server and SHALL
NOT name a skill's filesystem path to the session. It SHALL use the profile's
selected Claude model, effort, available tools, and permission policy rather
than Markdown model/tool fields or a global adapter file. A profile policy of
`autonomous` SHALL open the session with Claude Code's `bypassPermissions`
permission mode; a policy of `manual` SHALL open it with Claude Code's `manual`
permission mode. The permission mode SHALL only govern confirmation for
available tools and SHALL NOT add tools to the profile's declared tool list.

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
- **THEN** it uses the model, effort, available-tool, and permission policy
  that profile declares for Claude, only Designer's validated profile prompt
  and Designer's own allowlisted skills, and no global role adapter

#### Scenario: A scoped role can load its declared skills
- **WHEN** Claude opens a scoped role whose profile agent declares skills
- **THEN** that session's reachable tool set includes the floor skill-loading
  tool alongside the tools its declared capabilities resolve to

#### Scenario: An autonomous role does not pause for tool confirmation
- **WHEN** Claude opens a role whose resolved policy is `autonomous`
- **THEN** the adapter invokes Claude Code with
  `--permission-mode bypassPermissions` while passing only that role's
  declared available tools

#### Scenario: A manual role retains confirmation behavior
- **WHEN** Claude opens a role whose resolved policy is `manual`
- **THEN** the adapter invokes Claude Code with `--permission-mode manual`

#### Scenario: Operator machine configuration does not reach an agent
- **WHEN** the active project or the machine has project-level or user-level assistant configuration, memory, hooks, or plugins
- **THEN** the role session is opened without loading any of them

### Requirement: OpenCode uses bounded adapter-owned compatibility defaults
The OpenCode adapter SHALL NOT require or read OpenCode declarations from a
profile manifest, and profiles SHALL remain valid without one. When the active
project selects an OpenCode provider and model for an agent, the adapter SHALL
apply exactly that provider and model to that agent's sessions. When the project
selects no OpenCode provider and model, the adapter SHALL inherit the
authenticated operator model, variant, and configuration and SHALL own temporary
compatibility defaults for model/variant/tool handling. Effort, tool, and
permission handling SHALL remain adapter-owned in both cases.

The adapter SHALL generate one primary OpenCode agent shared by its persistent
role sessions and SHALL apply a deny-by-default permission policy. Every
delivery SHALL carry the target role's exact profile prompt and the catalogue
of that role's profile-allowlisted skills as system context, and SHALL NOT
carry any skill's instructions. The adapter SHALL register the profile's skills
with its tool server so a role can load its own on demand. The adapter SHALL
explicitly admit required shop tool classes while denying native subagents,
interactive questions, external directories, and native skill discovery. This
bounded exception to profile-explicit runtime policy SHALL NOT be represented
as equivalent control across backends.

#### Scenario: A project selects an OpenCode provider and model
- **WHEN** a project declares `opencode:<provider>:<model>` for an agent
- **THEN** that agent's OpenCode sessions use exactly that provider and model rather than the operator default

#### Scenario: Existing profile selects OpenCode
- **WHEN** Builder or Fordesmac opens an agent on OpenCode and the project names no provider and model
- **THEN** profile validation succeeds without an OpenCode table and the adapter supplies the compatibility defaults

#### Scenario: A role agent is generated
- **WHEN** OpenCode starts and later opens resolved profile roles
- **THEN** one generated primary agent serves their persistent sessions and each role delivery carries that role's exact profile prompt and that role's own skill catalogue

#### Scenario: A skill's instructions are not repeated per delivery
- **WHEN** an OpenCode role holding skills receives several deliveries
- **THEN** no delivery's system context contains a skill's instructions, and the role obtains them by loading a skill through the floor tool set

#### Scenario: OpenCode permissions are established
- **WHEN** the adapter generates its OpenCode agent
- **THEN** it applies deny-by-default permissions with only required shop tool classes admitted and reads no permission declarations from the profile manifest

#### Scenario: Operator runtime choices are inherited
- **WHEN** the generated role starts without a project-selected provider and model and without adapter-selected concrete values
- **THEN** OpenCode uses the authenticated operator model, variant, and configuration
