## ADDED Requirements

### Requirement: A selected control follows a supported joint override

A control inherited from a reusable body SHALL select the effective named
joint when a subclass or declaration site overrides that joint. Its axis,
origin, coordinate count and domain SHALL come from the effective declaration.
Selection SHALL retain its existing declaration-ownership, ancestry and input
reachability checks; matching a foreign joint's name SHALL NOT admit it.

#### Scenario: A site changes the rail direction
- **WHEN** a body with an inherited selected Slide is placed with a site
  override changing its prismatic joint's direction
- **THEN** its control constructs and publishes that effective rail direction

#### Scenario: A subclass changes a selected pivot
- **WHEN** a subclass overrides a selected revolute joint's axis or pivot
- **THEN** its inherited control constructs and uses the overridden placement

#### Scenario: An override is no longer a sliding coordinate
- **WHEN** a body carrying a selected Slide has that joint replaced by a
  revolute or multi-coordinate joint
- **THEN** the control is refused by name for the effective domain or
  coordinate count, without an attribute error or stale geometry
