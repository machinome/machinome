## MODIFIED Requirements

### Requirement: The inventory is additive to the published document

The inventory SHALL be published as a top-level `pieces` list beside `root`,
ordered by first encounter in the document tree, and every rigid node in the
tree SHALL carry a `piece` field holding its piece id. Existing node fields,
including `model`, SHALL keep their current meaning, and the document SHALL
keep declaring its current format and version: this growth is additive, so a
consumer reading only previously published fields is unaffected.

A **marking** published on a rigid node under the `markings` capability SHALL
NOT enter this inventory and SHALL NOT carry a piece id. A piece is one thing
to print, identified by the bytes of a built solid; a marking's artifact is a
surface the maker applies, paints or co-prints, and reporting it as a piece
would put a part in the bill of materials that no maker handles — which is the
exact failure that modelling each glyph as its own leaf commits. A part's
piece id and the whole inventory SHALL therefore be identical whether or not
its parts declare markings.

#### Scenario: An existing consumer keeps working

- **WHEN** a consumer written against the previous document reads a document
  containing the inventory
- **THEN** it finds the same `format`, `version`, `animation`, and `root` tree,
  with every previously published node field unchanged

#### Scenario: A tree node resolves to its piece

- **WHEN** a consumer reads a rigid node from the tree
- **THEN** the node's `piece` id matches exactly one entry in the top-level
  `pieces` list

#### Scenario: A marking is not a printed piece

- **WHEN** a document whose parts declare markings publishes its inventory
- **THEN** the `pieces` list is exactly the list the same tree publishes
  without the markings, no entry names a marking artifact, and no marking entry
  carries a `piece`
