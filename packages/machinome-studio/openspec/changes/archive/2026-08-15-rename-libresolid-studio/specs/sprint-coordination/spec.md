## MODIFIED Requirements

### Requirement: Repository participation follows ratified sprint scope
A sprint SHALL coordinate cycles in every repository required by its ratified
goal. A shop-only sprint SHALL remain valid without framework sprint state. A
framework integration line SHALL be created only when framework work is
explicitly included in the sprint scope.

#### Scenario: Sprint requires shop and framework work
- **WHEN** the pilot ratifies a sprint whose goal requires cycles in libresolid-studio and solid-node
- **THEN** the sprint establishes and tracks an integration line in both repositories
- **THEN** those integration lines form one coordinated sprint state without sharing Git history

#### Scenario: Sprint requires only shop work
- **WHEN** the pilot ratifies a sprint whose cycles all belong to libresolid-studio
- **THEN** the sprint creates only the shop integration line
- **THEN** it does not fabricate a framework branch, worktree, link, or record entry
