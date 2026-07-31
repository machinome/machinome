## MODIFIED Requirements

> **Synchronization intent:** each MODIFIED requirement in this file replaces
> its complete baseline requirement block, including its scenario set.

### Requirement: Every project agent works in the verified project root
The system SHALL give every standing agent declared by the selected profile the
same verified `projects/<name>` repository root as its project working
directory while retaining shop-owned profile prompts and runtime skills outside
the project repository.

#### Scenario: The Builder project is ready
- **WHEN** the system starts the default `builder` profile after preparing the named project
- **THEN** Builder works from that exact project repository root

#### Scenario: The Fordesmac project is ready
- **WHEN** the system starts the `fordesmac` profile after preparing the named project
- **THEN** Foreman, Designer, Machinist, and Librarian all work from that exact project repository root
