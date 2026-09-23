## ADDED Requirements

### Requirement: Version-12 Follow programs are accepted by content

The viewer SHALL accept a producer version-12 running document with a well-formed Follow declaration and SHALL validate its authored boundary expressions, source and follower identifiers, retained bank coordinate, writer uniqueness, graph order and initial feasible interval before running it. A version-12 document without Follow SHALL preserve the behavior of its other declarations. A viewer that does not support version 12 SHALL refuse it before operating, rather than silently executing a different contact model. Posed and clocked documents and running versions 1–11 SHALL retain their prior behavior.

#### Scenario: Well-formed Follow export
- **WHEN** the corrected Curta producer exports a version-12 document with its two moving measured surfaces and retained ball
- **THEN** the viewer loads the program and exposes the same controls and running bank as the producer

#### Scenario: Invalid Follow topology
- **WHEN** a declaration names a missing source, non-bank follower, extra writer, cycle, malformed boundary or impossible initial interval
- **THEN** loading refuses it by name before a tick is admitted

#### Scenario: Legacy compatibility
- **WHEN** a valid version-11 source-timed Curta export or an older Play document loads
- **THEN** its existing timing, retained motion, stops, snapshot and replay remain unchanged
