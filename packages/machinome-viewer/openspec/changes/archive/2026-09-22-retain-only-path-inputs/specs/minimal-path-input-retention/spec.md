## ADDED Requirements

### Requirement: A followed path retains only its named inputs

A followed expression SHALL retain the input values required to reconstruct its bound piece after the expression table is regenerated, with exact own-property presence and numeric values. It SHALL NOT inspect or copy unrelated bank entries for that retention. A reset and subsequent point SHALL return the same float as a path that was never reset, with the same search points, admissions and committed bank.

#### Scenario: A large unrelated bank
- **WHEN** a followed expression names two bank inputs in a bank with many unrelated coordinates and binds a piece
- **THEN** retention accesses only those two inputs and no unrelated coordinate

#### Scenario: Expression generation reset between points
- **WHEN** the expression table is regenerated between a bind and a later point of that piece
- **THEN** the reconstructed path evaluates the later point to the same float, including through a binding and an absent input

#### Scenario: OperatingCurta's bounded crank window
- **WHEN** selector 1 is set and the first 48 of 480 crank ticks execute on the pinned 213-coordinate export
- **THEN** the admitted crank travel and the entire committed bank match the preceding viewer build bit for bit
