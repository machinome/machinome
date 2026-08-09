## MODIFIED Requirements

### Requirement: Backend runtime choices are explicit per agent
Each profile agent SHALL declare a model, effort, and tool policy for Codex,
Claude, and Hermes. Each setting SHALL be either a value the backend can
enforce or the literal `inherit`. Each Claude runtime table SHALL additionally
declare `permission` as either `manual` or `autonomous`; no Codex or Hermes
runtime table SHALL declare that field. Selecting a backend SHALL fail
validation if an agent lacks that backend entry, names an unsupported concrete
value, or requests a control that backend cannot enforce. A backend MUST NOT
silently substitute an inherited or differently configured model, effort,
tool, or Claude permission policy for a concrete profile declaration.

The initial profiles SHALL explicitly inherit Hermes model, effort, and tools.
Every shipped Claude role SHALL explicitly declare `permission =
"autonomous"`.

#### Scenario: A complete backend mapping is selected
- **WHEN** the Builder profile is selected with the Codex backend
- **THEN** Builder opens with the model, effort, and tool policy declared for
  Codex by that profile

#### Scenario: A Claude profile selects autonomous execution
- **WHEN** a shipped profile is selected with the Claude backend
- **THEN** every declared role resolves its explicit `autonomous` permission
  policy along with its model, effort, and available tools

#### Scenario: Hermes intentionally inherits process configuration
- **WHEN** either initial profile is selected with the Hermes backend
- **THEN** every agent explicitly inherits model, effort, and tools from the
  configured ACP process

#### Scenario: A concrete control cannot be enforced
- **WHEN** the selected backend cannot enforce a concrete model, effort, tool,
  or Claude permission value declared for an agent
- **THEN** the runtime rejects that profile/backend combination rather than
  silently inheriting

#### Scenario: A Claude permission policy is omitted or invalid
- **WHEN** a Claude runtime table omits `permission` or names a value other
  than `manual` or `autonomous`
- **THEN** profile validation fails before any project or runtime side effect
