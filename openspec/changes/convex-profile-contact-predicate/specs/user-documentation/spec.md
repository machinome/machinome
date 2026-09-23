## ADDED Requirements

### Requirement: Profile contact is documented as a current-source, pointwise capability

The public `machinome.simulation.profile` imports `ConvexProfile` and
`profile_overlap` SHALL have tested docstrings explaining authored finite
convex loops, ordered rigid-XY placement, inclusive pointwise touching,
invalid-arithmetic refusal and the fact that a running `Bound` still samples
its path under the existing stop rule. The current-source status and
unreleased changelog SHALL distinguish the new predicate and version-13
paired-viewer requirement from the 0.7 release record and its version-11/12
documents. The record SHALL NOT imply a remote push or package-index upload
without evidence. Teaching pages and release substitutions SHALL not be
silently rewritten to present this current-source capability as published.

#### Scenario: A reader inspects the current-source API

- **WHEN** a developer imports the two public names and uses `help()`
- **THEN** the import and docstrings identify the numeric predicate, its
  limits and refusal behavior without naming a workspace project

#### Scenario: A reader checks release status

- **WHEN** a reader compares the project status and changelog with the
  0.7 manual and metadata
- **THEN** the new contact capability and version-13 viewer dependency are
  explicitly current-source/unreleased, while recorded 0.7 version facts
  remain unchanged without an unsupported publication assertion
