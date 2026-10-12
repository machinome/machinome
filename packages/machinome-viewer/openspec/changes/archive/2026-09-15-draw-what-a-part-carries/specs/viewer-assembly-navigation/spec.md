## MODIFIED Requirements

### Requirement: A viewer host can inspect the rendered assembly
The viewer handle SHALL expose a serializable assembly snapshot of the current
published tree. Every node in that snapshot SHALL include its name, a
root-relative path of sibling names, effective inherited colour or null,
whether it has model geometry, and ordered children. The snapshot SHALL expose
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

### Requirement: A viewer host can hide and show an assembly subtree
The viewer handle SHALL let a host hide or show a valid root-relative node
path. Hiding SHALL affect that node and all descendants without unloading their
geometry or changing the displayed root. Showing SHALL restore the subtree
unless an ancestor remains hidden.

A part's markings SHALL be hidden and shown with the part that carries them, and
SHALL be addressable in no other way: there is no path that names a marking, so
a marking is never hidden, shown or focused apart from its part. A part that is
an ancestor of the focused root, whose own surface is therefore not drawn, SHALL
NOT have its markings drawn either.

#### Scenario: A host hides a part
- **WHEN** a host hides a model-bearing node
- **THEN** that node's geometry and all descendant geometry are absent from
  the viewer while the rest of the focused subtree remains rendered

#### Scenario: A host restores a hidden child under a hidden parent
- **WHEN** a host shows a child whose ancestor remains hidden
- **THEN** the child remains absent until its hidden ancestor is shown


#### Scenario: A host hides a marked part

- **WHEN** a host hides a node carrying markings
- **THEN** that node's geometry and its markings are both absent from the
  viewer, and showing it again restores both

#### Scenario: A marked part above the focused root

- **WHEN** a host focuses a node whose ancestor carries markings
- **THEN** neither that ancestor's own geometry nor its markings are drawn,
  while the focused subtree is

### Requirement: The package mounts an assembly navigator into any host element

The package SHALL offer a navigator that a host mounts into an element it
supplies — named directly or by selector — against a mounted viewer
handle, and that needs nothing else: no assembly, no navigation state and
no callbacks from the host. Mounting SHALL draw the tree from the handle
before it returns, without waiting for a change notification, and SHALL
return a handle of its own that disposes it. A target that names no
element SHALL be refused by name. Mounting SHALL require no UI framework
of the host.

The navigator SHALL present the viewer's whole published assembly as an
accessible tree: a tree container with an accessible name, one tree item
per presented node, each item declaring whether it is the selected item
and, when it has children, whether it is expanded. The tree SHALL be a
single stop in the page's tab order, with keyboard focus moving inside it
by the keyboard contract rather than by tabbing between rows. Each row
SHALL show its node's label, its depth in the hierarchy, and its
effective inherited colour when the node has one. The selected row, the
focused viewer root and the hidden subtrees SHALL be identified
separately from one another.

#### Scenario: A host mounts a navigator beside a viewer

- **WHEN** a host mounts a viewer, then mounts a navigator into another
  element passing only that viewer's handle
- **THEN** the navigator's element already contains a tree of the
  viewer's published assembly when the mount call returns, before any
  change has been notified

#### Scenario: A navigator shows a nested coloured assembly

- **WHEN** the published assembly contains coloured nested subassemblies
- **THEN** each row shows its node's label, its depth, and the effective
  colour that node inherits, and the row for the focused viewer root is
  identified as such

#### Scenario: The tree is one tab stop

- **WHEN** a maker moves the page's tab focus into the navigator and then
  tabs again
- **THEN** exactly one row was reachable by tabbing, and tabbing again
  leaves the tree rather than stepping through its rows or their controls

#### Scenario: A target that names nothing is refused

- **WHEN** a host mounts a navigator against a selector matching no
  element
- **THEN** the call is refused with a message naming the selector, and
  nothing is drawn


#### Scenario: A marking is no row of the navigator

- **WHEN** a navigator is mounted on a viewer showing a document whose parts
  carry markings
- **THEN** the tree presents one row per part and no row for any marking, and
  presents the same rows it presents for the same document with no marking on
  it
