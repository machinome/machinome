## MODIFIED Requirements

### Requirement: One part selected out of the document by product name

A STEP file SHALL be treated as a document of products, one of which a
`StepNode` subclass selects with a `part` class attribute naming the
product as the file carries it. A product is any top-level shape the
document holds — a part or a sub-assembly — counted once however many times
it is placed.

The products a node may select by omission are the document's candidates:
every product except a root that is itself an assembly. A root that is
itself a single part SHALL be its own candidate. When a document has
exactly one candidate, `part` MAY be omitted and that product SHALL be the
node's part — which covers both a file holding one part alone and a file in
which an exporter wraps one part in an assembly. An assembly root SHALL
never be selected by omission, so a document of several components SHALL
NOT be handed to a node as one part unless the node names it; naming it
SHALL still select it.

A name is not always unique: a document may carry several distinct products
under one name. A subclass SHALL therefore be able to declare `part_index`
beside `part`, the 1-based position of the product it means among the
products of that name, in the order the document lists them. The index
SHALL be relative to the name, so a `part` and a `part_index` can never
state different products; a subclass that declares `part_index` and no
`part` SHALL be refused, because a node selecting by omission has no name to
index. An index below 1, or beyond the number of products carrying the name,
SHALL be refused naming the index and how many products the name has, and
SHALL NEVER be rounded to a neighbouring product. `part_index = 1` beside a
name only one product carries SHALL select that product.

When a document has more than one candidate and `part` is unset, or when
`part` names a
product the file does not hold, the build SHALL fail with the file's
inventory: one line per product carrying its name, whether it is a part, a
sub-assembly, or the document's root, how many occurrences of it the
document places, how many solids its shape holds, its bounding box and its
volume — so a developer or an agent learns the document's contents from the
failure itself and no separate inspection tool has to exist. A product the
file leaves unnamed SHALL appear in that inventory as unnamed.

Every product whose name another product of the document shares SHALL carry
its index in that inventory, so the selector a subclass must declare is read
off the failure beside the bounds, solid count and volume that say which
product is meant. A product whose name is its own SHALL be reported without
an index.

When two products of one name are present, selecting that name SHALL fail
naming the ambiguity, describing each match with its index, and saying that
`part_index` chooses between them, rather than choosing one.

#### Scenario: A file holding one part alone needs no selection

- **WHEN** a `StepNode` wraps a STEP file holding one part and no assembly,
  and declares no `part`
- **THEN** that product is the part and the build succeeds

#### Scenario: One part wrapped in an assembly needs no selection

- **WHEN** a `StepNode` wraps a STEP file in which an assembly root holds
  exactly one part, and declares no `part`
- **THEN** the part is selected — not the assembly root — and the build
  succeeds

#### Scenario: A multi-component root is never selected by omission

- **WHEN** a `StepNode` wraps a document whose assembly root holds several
  products and declares no `part`
- **THEN** the build fails with the inventory rather than selecting the
  root, and naming the root explicitly still selects it

#### Scenario: An unselected multi-product file reports its inventory

- **WHEN** a `StepNode` wrapping a file of several candidate products
  declares no `part`
- **THEN** the build fails with an error listing every product's name,
  kind, occurrence count, solid count, bounding box and volume

#### Scenario: A name the file does not carry reports the inventory

- **WHEN** a `StepNode` declares a `part` that is not a product of its file
- **THEN** the build fails naming the requested part and listing the
  document's products in the same inventory

#### Scenario: A repeated part is one product

- **WHEN** a document places one part at fourteen occurrences and a
  `StepNode` names it
- **THEN** it is one product in the inventory, reported with fourteen
  occurrences, and the node selects it without ambiguity

#### Scenario: An ambiguous name is refused

- **WHEN** a document holds two distinct products of the same name and a
  `StepNode` names it
- **THEN** the build fails naming the ambiguity and describing both
  products, each with the index that would select it, and no artifact is
  written

#### Scenario: A sub-assembly is a selectable product

- **WHEN** a `StepNode` names a sub-assembly of the document
- **THEN** its geometry is that sub-assembly's components composed at their
  placements within it, as the document holds them

#### Scenario: A shared name is resolved by its index

- **WHEN** a document holds two distinct products named `Pin`, and two
  `StepNode` subclasses name that product declaring `part_index = 1` and
  `part_index = 2`
- **THEN** each builds, and each holds the geometry of the product the
  inventory listed under that index — the first the document lists and the
  second

#### Scenario: An index beyond the products of that name is refused

- **WHEN** a `StepNode` declares a `part` two products carry and a
  `part_index` of 3
- **THEN** the build fails naming the index and the two products the name
  has, listing them with their own indices, and no artifact is written

#### Scenario: An index with no name is refused

- **WHEN** a `StepNode` declares `part_index` and no `part`
- **THEN** the build fails saying that an index selects among the products
  of a declared name, and reports the document's inventory

#### Scenario: A unique name is reported without an index

- **WHEN** the inventory is reported for a document whose product names are
  all distinct
- **THEN** no product line carries an index, and the lines read exactly as
  they do for a document that has no repeated name
