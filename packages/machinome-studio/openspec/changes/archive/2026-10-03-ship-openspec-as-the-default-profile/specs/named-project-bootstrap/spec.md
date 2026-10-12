## MODIFIED Requirements

### Requirement: Every project agent works in the verified project root
The system SHALL give every standing agent declared by the project's profile the
same verified project repository root as its project working directory while
retaining shop-owned profile prompts and runtime skills outside the project
repository. An agent SHALL receive the root of its own project only. When the
session belongs to one declared model of that project, the system SHALL also
give the agent the name of that model.

#### Scenario: The Builder project is ready
- **WHEN** the system starts the `openspec` profile after preparing the chosen project
- **THEN** Builder works from that exact project repository root

#### Scenario: The Fordesmac project is ready
- **WHEN** the system starts the `fordesmac` profile after preparing the chosen project
- **THEN** Foreman, Designer, Machinist, and Librarian all work from that exact project repository root

#### Scenario: Several projects are open at once
- **WHEN** several projects are open at the same time
- **THEN** each project's agents work from that project's own verified repository root and from no other

#### Scenario: Two models of one project are open at once
- **WHEN** two sessions are open on two declared models of one project repository
- **THEN** the agents of both work from that repository's root, and each is told the model its own session owns
