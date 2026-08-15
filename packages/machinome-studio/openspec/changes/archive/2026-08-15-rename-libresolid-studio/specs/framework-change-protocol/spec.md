## MODIFIED Requirements

### Requirement: Shop-owned framework orchestration
The shop SHALL be the sole source of agent prompts and lifecycle orchestration for solid-node development. A framework checkout SHALL provide implementation and durable framework records but SHALL NOT be relied upon for `AGENTS.md`, assistant-specific workflow copies, or other framework-local agent prompts.

#### Scenario: Framework mutation is requested through the shop
- **WHEN** the pilot requests a change to solid-node
- **THEN** the shop routes the work through its framework-change protocol
- **THEN** the protocol loads its agent instructions from libresolid-studio rather than from the framework checkout

#### Scenario: Framework-local prompt is encountered
- **WHEN** the protocol finds a framework-local agent prompt or competing workflow copy
- **THEN** it reports the ownership violation
- **THEN** it does not treat that file as development authority
