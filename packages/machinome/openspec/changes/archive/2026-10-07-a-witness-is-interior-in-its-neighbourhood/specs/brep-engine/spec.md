## MODIFIED Requirements

### Requirement: An empty common is verified before it is returned

When the Common of `intersect_shapes` holds no solid, the engine SHALL search,
within a finite budget, for one point classified inside a solid of each
operand by zero-tolerance solid classifiers and separated from every boundary
face of those solids by more than that face's native tolerance, starting from
points on the operands' native section. Such a point SHALL count only when the
six points at half its smaller distance to the two solids' faces, one along
each of ±x, ±y and ±z, are also classified inside those same two solids by
the same zero-tolerance classifiers; a point whose neighbours are not all
inside both SHALL be skipped and the search SHALL continue. Neither operand
SHALL be modified by the search.

- When such a point is found, the engine SHALL raise
  `BrepCommonInconsistency` naming both shapes and the point, and SHALL NOT
  infer an overlap volume.
- When the section, a classifier, a face distance or a face tolerance cannot
  be evaluated, it SHALL raise `BrepCommonVerificationError` naming both
  shapes.
- When the search ends without such a point, it SHALL return the empty
  Common, without claiming that the emptiness is certified.

Both error types SHALL be those the engine package `machinome.engine`
defines, so a caller catches them without importing the engine.

#### Scenario: A witnessed false empty is refused

- **WHEN** the Common of two solids is empty but a point lies inside both
  beyond their native face tolerances
- **THEN** `intersect_shapes` raises `BrepCommonInconsistency` and returns no
  shape

#### Scenario: Boundary contact is not a witness

- **WHEN** two solids only touch on a face and every candidate point lies
  within a face's native tolerance
- **THEN** `intersect_shapes` returns the empty Common

#### Scenario: A failed check refuses

- **WHEN** the section used to verify an empty Common cannot be built
- **THEN** `intersect_shapes` raises `BrepCommonVerificationError`

#### Scenario: A lone inside reading is not a witness

- **WHEN** two solids only touch on a face, their Common is empty, and one
  solid's classifier reports inside at a single point beyond every face
  tolerance while reporting outside at that point's neighbours
- **THEN** `intersect_shapes` returns the empty Common
