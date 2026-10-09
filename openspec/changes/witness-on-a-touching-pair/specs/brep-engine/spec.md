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

At each point of the search the engine SHALL consult first the classifiers
of the operand with fewer boundary faces, the first operand when the counts
are equal. Before it consults a classifier of the other operand at that
point, it SHALL read the point's side of each solid of both operands from
the solid's nearest boundary point: when that boundary point lies inside a
face, or inside an edge where two faces meet, the side SHALL be outside or
inside as the outward face normals there show, or on the boundary when the
point is within the native tolerance of a face there; otherwise the side
SHALL be undecided. A solid whose side reads outside or on the boundary
SHALL NOT hold a candidate at that point, and when no solid of an operand
remains, the point SHALL be skipped without consulting the classifiers of
the other operand. A side reading SHALL NOT by itself make a point count.

- When such a point is found, the engine SHALL raise
  `BrepCommonInconsistency` naming both shapes and the point, and SHALL NOT
  infer an overlap volume.
- When the section, a classifier, a face distance or a face tolerance cannot
  be evaluated, it SHALL raise `BrepCommonVerificationError` naming both
  shapes. A nearest boundary point that cannot be measured, or a face
  tolerance there that is not finite, SHALL leave the side undecided.
- When the search ends without such a point, it SHALL return the empty
  Common, without claiming that the emptiness is certified.
- When a solid of either operand is inside out, its signed volume negative,
  the engine SHALL NOT consult a classifier on either operand and SHALL
  raise `BrepCommonVerificationError` naming that operand as inside out,
  with its signed volume, and SHALL NOT claim a shared point. The common
  itself, and a non-empty common's volume, are computed and returned as
  for any operand.

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

#### Scenario: An inside-out operand is refused by name

- **WHEN** the Common of a normal solid and an inside-out solid touching it
  is empty
- **THEN** `intersect_shapes` raises `BrepCommonVerificationError` naming the
  inside-out operand and its negative signed volume, and names no shared
  point

#### Scenario: A touching pair is settled without the classifier of the part with more faces

- **WHEN** a pin and a plate whose hole it fits exactly touch on the hole's
  cylinder, their Common is empty, and the operands are given in either
  order
- **THEN** `intersect_shapes` returns the empty Common without consulting
  the plate's classifier at any point

#### Scenario: A side reading does not move a refusal

- **WHEN** two solids share material, their Common is reported empty, and
  the search with every side reading undecided refuses at a point
- **THEN** `intersect_shapes` raises `BrepCommonInconsistency` at that same
  point
