## ADDED Requirements

### Requirement: Mechanics users can reach the independent helper manual

The framework manual SHALL identify machinome-mechanics as its optional
mechanics helper package and link directly to that package's user documentation
from its guide navigation, helper API reference, motion-law guidance and
migration guidance. It SHALL preserve the separate installation and import
boundary and direct readers to the mechanics manual for complete helper usage
and coordinate conventions.

#### Scenario: Find a helper from the framework

- **WHEN** a framework user looks for a gear, screw, crank, delta or linkage helper
- **THEN** the manual offers a direct link to the mechanics user reference
- **AND** states that helpers are imported from `machinome_mechanics`

#### Scenario: Follow a motion-law or migration guide

- **WHEN** a reader wants to reuse a mechanical formula or migrate the former
  framework helper imports
- **THEN** they can follow a direct link to the mechanics manual for examples
  and conventions without needing internal workflow records
