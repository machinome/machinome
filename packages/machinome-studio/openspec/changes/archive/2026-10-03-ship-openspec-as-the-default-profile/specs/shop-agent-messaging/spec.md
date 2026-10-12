## MODIFIED Requirements

### Requirement: Declared reporters report through the broker to their parent
An agent with `reports_to` SHALL send progress, findings, and completion reports
through the broker to that declared parent. Reports and shop events SHALL
remain ordered and available while the parent manages work. The orchestrator
SHALL translate backend output from the profile's user-facing agent, and no
other agent, into user-conversation entries.

#### Scenario: A specialist reports while its parent is working
- **WHEN** a specialist reports progress or completion while its reporting parent is using a tool
- **THEN** the report remains queued and is presented after that tool call and before the parent's next task action

#### Scenario: The configured reporting parent resumes after several events
- **WHEN** several reports or lifecycle events occur before that parent next checks the floor
- **THEN** the reporting parent receives the unseen events once in recorded order

#### Scenario: The user-facing agent emits output
- **WHEN** Builder in `openspec` or Foreman in `fordesmac` emits non-empty backend output
- **THEN** the orchestrator records it in the user conversation under that configured agent identity
