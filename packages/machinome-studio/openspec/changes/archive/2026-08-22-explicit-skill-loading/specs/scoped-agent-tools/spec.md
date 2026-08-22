## MODIFIED Requirements

### Requirement: Project sandboxing
Every tool in the floor-provided MCP tool set SHALL resolve path arguments
against the active project's root and SHALL reject any resolved path that
falls outside that root.

`load_skill` is the single exception and SHALL take no path argument. It
resolves a skill name against the registry the shop supplied at launch and
reads only within that skill's directory, as `runtime-skill-loading` requires.
No other tool SHALL read a registered skill directory.

#### Scenario: Path escapes project root
- **WHEN** a tool is called with a path argument that resolves outside the
  active project's root (e.g. via `..` traversal or an absolute path elsewhere)
- **THEN** the tool call fails without performing any filesystem or process
  action

#### Scenario: Path stays within project root
- **WHEN** a tool is called with a path argument that resolves inside the
  active project's root
- **THEN** the tool call proceeds normally

#### Scenario: A registered skill directory is not a project path
- **WHEN** a path-taking tool is called with a path inside a registered skill
  directory
- **THEN** the call is rejected as outside the active project
