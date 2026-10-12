## MODIFIED Requirements

### Requirement: The Claude backend operates Claude Code CLI sessions
The Claude backend SHALL launch one `claude` process per profile-declared agent
in non-interactive streaming mode, exchange newline-delimited JSON frames over
stdio, and use the active project as its working directory.

It SHALL deliver the resolved profile prompt and skills as session-level
instructions so the first user message remains a broker envelope. It SHALL use
the profile's selected Claude model, effort, available tools, and permission
policy rather than Markdown model/tool fields or a global adapter file. A
profile policy of `autonomous` SHALL open the session with Claude Code's
`bypassPermissions` permission mode; a policy of `manual` SHALL open it with
Claude Code's `manual` permission mode. The permission mode SHALL only govern
confirmation for available tools and SHALL NOT add tools to the profile's
declared tool list.

It SHALL open each session with both project-level and user-level assistant
configuration, memory, hooks, plugins, and other operator-machine
customization disabled. It SHALL NOT read, store, forward, or require a
credential, and SHALL invoke the `claude` command using authentication the
operator has already configured.

#### Scenario: Claude starts one process per profile agent
- **WHEN** either initial profile opens with Claude
- **THEN** Claude starts exactly one process for every agent declared by that
  profile

#### Scenario: The role contract does not consume a conversational turn
- **WHEN** Claude opens a profile agent
- **THEN** prompt and skill contracts are delivered as session-level
  instructions and the first user message is a broker envelope

#### Scenario: Runtime capability comes from the selected profile
- **WHEN** Claude opens Designer from `fordesmac`
- **THEN** it uses the model, effort, available-tool, and permission policy
  that profile declares for Claude, only Designer's validated profile prompt
  and skill paths, and no global role adapter

#### Scenario: An autonomous role does not pause for tool confirmation
- **WHEN** Claude opens a role whose resolved policy is `autonomous`
- **THEN** the adapter invokes Claude Code with
  `--permission-mode bypassPermissions` while passing only that role's
  declared available tools

#### Scenario: A manual role retains confirmation behavior
- **WHEN** Claude opens a role whose resolved policy is `manual`
- **THEN** the adapter invokes Claude Code with `--permission-mode manual`

#### Scenario: Operator machine configuration does not reach an agent
- **WHEN** the active project or the machine has project-level or user-level
  assistant configuration, memory, hooks, or plugins
- **THEN** the role session is opened without loading any of them
