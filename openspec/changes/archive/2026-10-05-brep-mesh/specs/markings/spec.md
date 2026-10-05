## MODIFIED Requirements

### Requirement: A marking contributes no solid and is not a part

A marking SHALL contribute no solid. A part's volume, bounds, STL bytes, BREP
bytes and piece id SHALL be identical whether or not it declares markings, and
`assertNoIntersectingSolids`, `assertNoDisconnectedSolids` and every pairwise
interference sweep SHALL return the same verdict, on the mesh engine and the
B-rep engine alike.


A marking SHALL NOT be a node and SHALL NOT be a child. A part's `children`,
the shape of the tree, an assembly's part count and the published piece
inventory SHALL be unchanged by a marking, and a marking SHALL NOT be
addressable as a part.

A marking SHALL NOT enter the part's artifact identity: adding or removing a
marking declaration SHALL leave the part's `uniq_id` exactly as it was, because
a marking is not a parameter.

#### Scenario: The solid is byte-identical with and without markings

- **WHEN** two node classes of the same name and the same parameters build the
  same solid, one of them additionally declaring a marking
- **THEN** their STL artifacts hold identical bytes, their BREP artifacts hold
  identical bytes, and both report the same piece id

#### Scenario: A marking changes no geometric verdict

- **WHEN** an assembly whose parts carry markings runs
  `assertNoIntersectingSolids` and `assertNoDisconnectedSolids`, on the mesh
  engine and on the B-rep engine

- **THEN** every verdict equals the verdict the same assembly gives with the
  markings removed

#### Scenario: A marking is not in the tree

- **WHEN** a part declaring two markings is rendered and assembled
- **THEN** its `children` is empty, the assembly's part count is what it is
  without the markings, and no node of the tree is named for a marking

#### Scenario: A marking does not key the artifact

- **WHEN** two node classes of the same name and the same parameters are
  realized, one declaring a marking and one declaring none
- **THEN** both report the same `uniq_id`, so the marking changed no artifact
  key
