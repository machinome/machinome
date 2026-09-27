## MODIFIED Requirements

### Requirement: Version 0.7 records the rename lineage

The first Machinome release SHALL be version 0.7.0 and SHALL state that it is
the direct continuation of solid-node 0.6.0 with the repository's complete Git
history. Its changelog, release note and migration guidance SHALL explain the
reason for the name change and map old distribution, import, command,
configuration, viewer and mechanics names to their Machinome replacements.
A later 0.7.x release SHALL keep that material and add its own changelog
entry, `HISTORY.rst` entry and release-note section above it.

Historical ADRs, archived changes and release records SHALL retain the names
that were true when they were written. Current synthesis and indexes SHALL
make the transition discoverable.

#### Scenario: A 0.6 user reads the 0.7 release material

- **WHEN** the user looks for the next release after solid-node 0.6.0
- **THEN** the material identifies Machinome 0.7.0 as that release and gives
  the complete migration map

#### Scenario: A 0.7.0 user reads the 0.7.1 release material

- **WHEN** the user looks for what changed after Machinome 0.7.0
- **THEN** the changelog's 0.7.1 entry sits above the 0.7.0 entry, and the
  rename and migration material of 0.7.0 is unchanged beneath it

#### Scenario: A reader opens a historical decision

- **WHEN** an ADR predating 0.7 discusses solid-node
- **THEN** its historical wording remains intact and current architecture
  material identifies it as a decision inherited by Machinome
