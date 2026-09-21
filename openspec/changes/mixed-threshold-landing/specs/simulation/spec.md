## ADDED Requirements

### Requirement: Moving engagement thresholds preserve valid running motion

A running mechanism whose engagement depends on both a driven part's retained
position and another moving part SHALL follow the relative engagement crossing,
including when the threshold overtakes the driven part. A valid request SHALL
not fail merely because that crossing direction differs from the driven part's
own displacement. The existing nearest-representable far-side, retained-state
and transactional-refusal requirements remain in force.

#### Scenario: A threshold overtakes a moving part
- **WHEN** a permitted request moves a part and its engagement threshold in
  the same direction but the threshold passes the part
- **THEN** engagement changes on the reached side of the threshold without an
  artificial stop, invented travel or landing error
- **AND** a later request and snapshot replay preserve the admitted state

#### Scenario: A restraint observes a free carry movement
- **WHEN** an ordinary crank turn moves a carry mechanism through its allowed
  engagement and a crank restraint reads that mechanism's retained position
- **THEN** the free turn completes with the same physical result as without
  that observer
- **AND** a subsequent genuinely obstructed request still stops at its first
  physical contact without automatic repositioning

#### Scenario: A genuinely invalid crossing remains transactional
- **WHEN** a requested motion has no valid engagement continuation or encounters
  a separately invalid relation
- **THEN** it is refused by the existing named failure behavior without partially
  committing the machine

#### Scenario: A part follows a moving contact
- **WHEN** a part and its contact move together with provably constant relative
  position on a continuous piece
- **THEN** rounding in point evaluations SHALL NOT invent an engagement crossing
  or cause an impossible-contact refusal
- **AND** genuine nonzero relative movement, however small, and genuine invalid
  continuation retain the existing crossing and transactional-refusal behavior
