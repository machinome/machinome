## ADDED Requirements

### Requirement: A profile-capable document is version-gated and mount-isolated

The viewer SHALL advertise a capability version that includes the producer's version-13 finite-profile document, refuse that document on an older viewer, and leave versions 1–12 unchanged. Each loaded program's profile table SHALL be part of its evaluation and snapshot identity: the same expression and bank values in two mounted documents with different tables SHALL never reuse the other's result, and a snapshot for one profile table SHALL not restore into a changed table.

#### Scenario: Capability and legacy documents
- **WHEN** a version-13 profile document is loaded on a capable or older viewer, or a valid version-12 running document is loaded on the capable viewer
- **THEN** the capable viewer executes the profile document, the older viewer refuses it before operating, and the version-12 document retains its previous behavior

#### Scenario: Follow and profile contact share one program
- **WHEN** a running document contains both a version-12 Follow and a finite profile contact call
- **THEN** it declares version 13, the capable viewer executes both declarations, and an older viewer refuses it before operating

#### Scenario: Simultaneous distinct profiles
- **WHEN** two mounts evaluate the same profile-call text at equal bank and placement values but have different published tables
- **THEN** each returns its own table's result without expression-cache contamination

#### Scenario: Restoring against changed profile content
- **WHEN** a snapshot from a program with one profile table is restored into a re-export with different profile content
- **THEN** the existing program-identity guard refuses the restore rather than reusing stale contact state
