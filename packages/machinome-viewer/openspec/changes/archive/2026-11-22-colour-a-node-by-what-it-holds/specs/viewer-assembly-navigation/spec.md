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

#### Scenario: A host reads a group whose parts share one colour

- **WHEN** a host reads the assembly snapshot of a model with a subassembly
  that has no colour of its own and inherits none, and whose parts all show
  one colour, while a navigator on the same viewer shows that colour on the
  subassembly's row
- **THEN** the snapshot reports no colour for the subassembly, and each part
  its own effective colour

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
SHALL show its node's label, its depth in the hierarchy, and a colour when
it has one to show. A node without children SHALL show its effective
inherited colour when it has one. A node with children SHALL show the one
colour its parts show when every one of its parts shows that same colour,
and otherwise its effective inherited colour when it has one. A node's
parts SHALL be every node without children beneath it, whether or not its
row is presented, focused, hidden or obscured, each at its own effective
inherited colour, together with the node itself when it has model geometry
of its own. A part with no colour SHALL keep its node's parts from sharing
one colour. The colour a row with children shows SHALL be decided from the
same assembly its parts' rows are drawn from. The selected row, the
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
  colour that node inherits, unless every part a subassembly holds shows
  one other colour, in which case that subassembly's row shows its parts'
  colour, and the row for the focused viewer root is identified as such

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

#### Scenario: A group whose parts share one colour

- **WHEN** a subassembly that has no colour of its own and inherits none
  holds parts that all show one colour
- **THEN** its row shows that colour, as each of its parts' rows does

#### Scenario: A group whose parts do not share one colour

- **WHEN** a subassembly holds parts of two different colours, or a part
  with no colour beside coloured ones
- **THEN** its row shows the subassembly's own effective colour when it has
  one, and no colour when it has none

#### Scenario: An inner group shares a colour its outer group does not

- **WHEN** a subassembly's parts all show one colour, and the subassembly
  that holds it also holds a part of another colour
- **THEN** the inner row shows the shared colour, and the outer row shows
  its own effective colour when it has one, and no colour when it has none

#### Scenario: A group's own colour does not stand in for its parts

- **WHEN** a subassembly declares a colour and holds parts of two other
  colours, and the subassembly that holds it, which has no colour, holds
  besides it only a part of the inner subassembly's declared colour
- **THEN** the inner row shows its declared colour, and the outer row
  shows no colour, because the parts beneath it do not share one

#### Scenario: A group whose declared colour its parts all override

- **WHEN** a subassembly declares one colour and every part beneath it
  declares one other, same colour
- **THEN** its row shows the colour its parts show, and the assembly
  snapshot a host reads still reports the subassembly's declared colour

#### Scenario: A group's colour does not follow what is expanded, focused or hidden

- **WHEN** a maker collapses or expands a subassembly whose parts share one
  colour, focuses it or one of its parts, or hides one of its parts
- **THEN** the subassembly's row shows the same shared colour throughout,
  while the hidden part's row shows it hidden

#### Scenario: A group's colour agrees with parts whose colour the machine chooses

- **WHEN** the parts of a subassembly show a colour the machine's state
  chooses, and the navigator redraws from an assembly in which they all
  show the same choice, and later from one in which one of them shows the
  other choice
- **THEN** the subassembly's row shows the shared colour while its parts'
  rows all show it, and shows its own effective colour, or no colour, once
  one part's row shows the other choice

### Requirement: A maker moves the viewer from the navigator

The navigator SHALL let a maker focus a subtree, restore the published
document root, and hide or show a subtree, driving the viewer through the
same operations a host calls. Restoring the document root SHALL be
offered while a subtree is focused, and the navigator SHALL be able to
present that affordance or leave it to its host.

Each row SHALL carry a visibility control with checkbox semantics that
appears as a square filled with the colour the row shows while the node
is shown, uses a neutral fill when a shown node's row has no colour to
show, and appears empty with only its border while the node is hidden.
The checked state and the accessible name SHALL communicate visibility
independently of colour.

A node that is invisible only because an ancestor is hidden SHALL be
distinguished from a node hidden in its own right: its visibility control
SHALL keep reporting the node's own setting, so toggling it stays the
exact inverse of what hid it, while the row SHALL mark it as obscured and
its control's accessible name SHALL say which ancestor hides it. A node
hidden in its own right under a hidden ancestor SHALL show its control
unchecked and its row marked both hidden and obscured.

#### Scenario: A maker focuses a subassembly

- **WHEN** the maker focuses a row's node
- **THEN** the viewer displays that subtree as its root, the navigator
  marks that row as the focused root, and no visibility state changes

#### Scenario: A maker returns to the whole assembly

- **WHEN** the maker uses the restore affordance while a subtree is
  focused
- **THEN** the viewer displays the published document root, the focus
  operation receives the value that names the document root rather than
  an empty path, and every hidden or shown subtree keeps its state

#### Scenario: A maker hides and restores a part

- **WHEN** the maker hides a row's node and later shows it again
- **THEN** the viewer hides and restores that node and its descendants,
  and the focused viewer root does not change

#### Scenario: A maker reads visibility off the rows

- **WHEN** one coloured node is shown and another is hidden
- **THEN** the shown node's control is checked and filled with the colour
  its row shows, the hidden node's control is unchecked and empty with
  only its border, and both report their checked state to assistive
  technology

#### Scenario: A colourless node is shown

- **WHEN** a shown node's row has no colour to show
- **THEN** its control uses the neutral fill and stays distinguishable
  from the empty hidden state

#### Scenario: A descendant of a hidden node is distinguished

- **WHEN** a node with descendants is hidden and its descendants' rows
  are presented
- **THEN** each descendant's control still reports that descendant's own
  visibility setting, its row is marked as obscured, and its control's
  accessible name names the hidden ancestor

#### Scenario: A group's control carries its parts' colour

- **WHEN** a subassembly whose parts all show one colour is shown, and is
  then hidden
- **THEN** its control is checked and filled with that colour while it is
  shown, and unchecked and empty with only its border while it is hidden,
  and in each state its checked state and accessible name are those of a
  subassembly whose parts do not share a colour
