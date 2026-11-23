## MODIFIED Requirements

### Requirement: A viewer host can inspect the rendered assembly
The viewer handle SHALL expose a serializable assembly snapshot of the current
published tree. Every node in that snapshot SHALL include its name, a
root-relative path of sibling names, effective inherited colour or null,
whether it has model geometry, its effective layers (the keys of the layers its
own document entry names and those every entry above it names, each once, in
the order of the document's `layers` list, and an empty list when it is on
none), and ordered children. The snapshot SHALL expose
no mutable document, Three.js object, or project filesystem reference.

A marking a part carries SHALL NOT appear in that snapshot. A marking is a
region of a part's surface and not a node of the assembly: it has no path of its
own, is no child of the part that carries it, and is counted in nothing a host
reads as the assembly's parts. A host reading the snapshot of a marked document
SHALL be given exactly the nodes, paths, colours and geometry flags it is given
for the same document with no marking on it.

#### Scenario: A host reads a nested coloured assembly
- **WHEN** a host reads the assembly snapshot of a model with a coloured
  ancestor and an uncoloured descendant
- **THEN** the descendant reports its root-relative path and the ancestor's
  effective colour

#### Scenario: A host reads a marked assembly

- **WHEN** a host reads the assembly snapshot of a document whose parts carry
  markings
- **THEN** the snapshot contains one node per part and none per marking, and
  is the same snapshot the same document without its markings produces

#### Scenario: A host reads a group whose parts share one colour

- **WHEN** a host reads the assembly snapshot of a model with a subassembly
  that has no colour of its own and inherits none, and whose parts all show
  one colour, while a navigator on the same viewer shows that colour on the
  subassembly's row
- **THEN** the snapshot reports no colour for the subassembly, and each part
  its own effective colour

#### Scenario: A host reads a part's layers

- **WHEN** a host reads the assembly snapshot of a document whose `circuit`
  entry names `electrical` and whose `circuit/lamp` entry names `mechanical`
- **THEN** `circuit` reports `electrical`, `circuit/lamp` reports `electrical`
  and `mechanical`, and a node no entry above or on it names reports no layer

### Requirement: A host reads the viewer's assembly navigation state

The viewer handle SHALL expose the navigation state it holds for the
published assembly: the focused root, the node paths that have been
explicitly hidden, and the shown layer. The focused root SHALL be reported as a root-relative
path of sibling names, or as the same null value the focus operation
accepts when the published document root is displayed, so that the
reported root is always a value the focus operation takes. Each hidden
entry SHALL be a root-relative path of sibling names. The list SHALL
contain every path that was explicitly hidden and nothing else: a
descendant that is invisible only because an ancestor is hidden is not
listed, while a descendant that was itself explicitly hidden stays listed
beside its hidden ancestor. A node that is not drawn only because the shown
layer leaves it out SHALL NOT be listed. A path SHALL be listed only while the current
published tree still contains it. The shown layer SHALL be reported as a copy
of its key and label, or as the same null value the show operation accepts
for the whole machine, so that the reported layer is always a value the show
operation takes. The reported state SHALL be a serializable snapshot
that the viewer does not later modify, and it SHALL expose no mutable
document, Three.js object, or project filesystem reference.

#### Scenario: A host reads what is focused

- **WHEN** a host focuses a nested subassembly and then reads the
  navigation state
- **THEN** the state reports that subassembly's root-relative path, and
  passing that reported root back to the focus operation leaves the same
  subtree focused

#### Scenario: The published document root is reported as no focused path

- **WHEN** a host resets the displayed root and reads the navigation state
- **THEN** the reported root is the null value the focus operation accepts
  for the document root, rather than an empty path

#### Scenario: A host reads what is hidden

- **WHEN** a host hides a node that has descendants and reads the
  navigation state
- **THEN** the hidden list contains that node's path and no descendant
  path, and showing the listed path again leaves the hidden list empty

#### Scenario: A snapshot is a value

- **WHEN** a host keeps a navigation state it read, and then focuses
  another subtree
- **THEN** the kept state still reports what it reported when it was read,
  and a fresh read reports the new focus

#### Scenario: A host reads the shown layer

- **WHEN** an app shows the electrical layer and a host reads the navigation
  state
- **THEN** the state reports that layer's key and label, lists none of the
  parts the layer leaves out as hidden, and passing the reported layer back
  to the show operation leaves the same layer shown

## ADDED Requirements

### Requirement: The navigator marks the rows the shown layer leaves out

While a layer is shown, the navigator SHALL mark as obscured every row whose
node, and every node below it, is off that layer, as it marks a row under a
hidden ancestor. Such a row's visibility control SHALL keep reporting the
node's own setting, so toggling it stays the exact inverse of what the maker
last did to it, and its accessible name SHALL say that the shown layer, named
by its label, leaves it out, after the hiding ancestor where one also applies.
A row with any node on the shown layer at or below it SHALL NOT be marked for
the layer. The navigator SHALL present no control that shows or switches a
layer, and a row's colour SHALL NOT follow the shown layer. With no layer
shown, every row SHALL be what it was before this capability.

#### Scenario: The case is outside the electrical layer

- **WHEN** the electrical layer is shown and the navigator presents the case's
  row and the keyboard's row, whose keys are on the layer
- **THEN** the case's row is marked obscured, its control is still checked and
  its accessible name says the layer "Electrical path" leaves it out, and the
  keyboard's row is not marked

#### Scenario: Hidden and outside the layer

- **WHEN** a part under a hidden subassembly is off the shown layer
- **THEN** its row's accessible name names the hiding subassembly and the
  shown layer
