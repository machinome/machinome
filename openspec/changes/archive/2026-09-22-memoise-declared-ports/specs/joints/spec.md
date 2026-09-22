## ADDED Requirements

### Requirement: Repeated port enumeration preserves class declarations and independent mappings

The port enumerator SHALL report the same names and port declarations on repeated calls for a completed node class, including inherited ports and site-declared joint coordinates. Each returned mapping SHALL be independent: changing one mapping SHALL NOT change a later enumeration. Enumerating a generated specialized class SHALL NOT keep that class alive after its declaration site and instances are released.

#### Scenario: Repeated enumeration of inherited and specialized ports

- **WHEN** a consumer enumerates ports twice on a child class with inherited ports and a site-declared joint coordinate
- **THEN** both calls report the same declarations, and changing the first returned mapping leaves the second result unchanged

#### Scenario: Generated declaration classes can be collected

- **WHEN** a generated site-specialized child class is enumerated and all of its declaring objects are released
- **THEN** the class can be garbage-collected

#### Scenario: A bound checks reads while its joint is being named

- **WHEN** a node class declares a joint with a `Bound` that checks another joint during class creation
- **THEN** port enumeration after class creation reports the fully named coordinates, even if the bound check enumerated ports before descriptor naming finished
