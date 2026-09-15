# Viewer Assembly Navigation Specification

## Purpose

Expose a stable host API for inspecting, focusing, hiding, and showing nodes in
the published viewer assembly without exposing mutable rendering internals.
Migrated from solid-node's baseline when the viewer became this package;
behaviour unchanged.

Code: `solid_node_viewer/widget/src/assembly.ts`.
## Requirements
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

### Requirement: A viewer host can focus an assembly subtree
The viewer handle SHALL let a host set a root-relative node path as the
displayed assembly root, or reset it to the published document root. Focusing
SHALL render only that subtree, fit it for viewing, and leave every visibility
state unchanged.

#### Scenario: A host focuses a subassembly
- **WHEN** a host sets a valid nested node path as the displayed root
- **THEN** the viewer shows and frames only that subtree while retaining every
  existing hidden or shown path

#### Scenario: A host restores the document root
- **WHEN** a host resets the displayed root
- **THEN** the viewer shows the published root subject to its existing
  visibility state

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

### Requirement: Assembly-navigation state reconciles with viewer updates
The viewer SHALL retain focus and visibility state across targeted updates for
paths the updated document still contains. It SHALL discard a missing hidden
path and reset a missing focused root to the document root without preventing
later updates or damaging retained geometry.

#### Scenario: A targeted update retains state
- **WHEN** `manifestChanged()` updates a model while retaining its focused and
  hidden paths
- **THEN** the focused subtree and hidden descendants remain in effect without
  refetching unchanged geometry

#### Scenario: A targeted update removes the focused node
- **WHEN** `manifestChanged()` removes the focused node
- **THEN** the viewer returns to the document root, discards unavailable state,
  and remains usable for subsequent updates

### Requirement: A maker moves focus from within the widget

When the driver chrome is presented, the viewer SHALL offer an
affordance that shows the focused path from the document root and lets
the maker move focus without host code: descending into a subassembly
and returning to any ancestor, including the root. Through it the
maker SHALL be able to reach every layer that declares drivers or
instructions; a child with none declared anywhere beneath it need not
be offered. The affordance SHALL drive the same focus state as the
host focus API and SHALL reflect focus changes the host makes, so the
two never disagree about what is focused.

#### Scenario: A maker descends to an axis and comes back

- **WHEN** the maker uses the affordance to focus `x_axis` on a
  two-axis machine and then selects the root in it
- **THEN** the viewer focuses the subassembly exactly as a host
  `setRoot(['x_axis'])` would — same visibility, same re-scoped
  controls — and returns the same way

#### Scenario: The affordance offers only paths that lead to controls

- **WHEN** the focused layer has one child subtree declaring drivers
  and another declaring nothing anywhere beneath
- **THEN** the declaring child is offered for descent and the empty
  one need not be

#### Scenario: A host focus change is reflected

- **WHEN** the host calls `setRoot` while the driver chrome is shown
- **THEN** the affordance shows the new focused path and the controls
  re-scope to it

### Requirement: A host reads the viewer's assembly navigation state

The viewer handle SHALL expose the navigation state it holds for the
published assembly: the focused root, and the node paths that have been
explicitly hidden. The focused root SHALL be reported as a root-relative
path of sibling names, or as the same null value the focus operation
accepts when the published document root is displayed, so that the
reported root is always a value the focus operation takes. Each hidden
entry SHALL be a root-relative path of sibling names. The list SHALL
contain every path that was explicitly hidden and nothing else: a
descendant that is invisible only because an ancestor is hidden is not
listed, while a descendant that was itself explicitly hidden stays listed
beside its hidden ancestor. A path SHALL be listed only while the current
published tree still contains it. The reported state SHALL be a serializable snapshot
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

### Requirement: A host is told when the assembly or its navigation changes

The viewer handle SHALL let a host subscribe to assembly changes and SHALL
return a function that cancels that subscription. A subscribed listener
SHALL receive the current assembly snapshot and the current navigation
state, and those SHALL equal what the handle's assembly and navigation
reads return at that moment, so a listener needs no other call to redraw.

The viewer SHALL notify every subscribed listener after each accepted
operation that publishes a tree or changes the focused root or the
visibility state, whatever caused it — a host call, an affordance the
widget presents, or a targeted update — exactly once per such operation,
after the viewer has applied it, and before an asynchronous operation's
result is delivered to its caller. The notification SHALL mean that the
state a host last read may be stale; the viewer SHALL NOT be required to
determine that anything differs, so an accepted operation that leaves the
state as it found it SHALL still notify. An operation refused for an
invalid path SHALL change nothing and SHALL notify nobody.

No listener SHALL be notified while the viewer is mounting. Disposal SHALL
itself notify nobody and SHALL release every subscription; no listener
SHALL be notified after the handle is disposed, and a cancel function SHALL
remain safe to call afterwards.
A listener cancelled while a notification is being delivered SHALL NOT
receive that notification. A listener that raises SHALL NOT prevent the
other listeners from being notified and SHALL NOT propagate its failure to
the caller of the operation.

#### Scenario: A host learns of a focus change it did not make

- **WHEN** a maker moves focus with an affordance the widget presents,
  while a host is subscribed
- **THEN** the host's listener is notified, and the navigation state it
  receives reports the newly focused path

#### Scenario: A targeted update notifies once with reconciled state

- **WHEN** a targeted update removes the focused node and one hidden node
  while a host is subscribed
- **THEN** the listener is notified exactly once for that update, before
  the update's result reaches its caller, and the state it receives reports
  the document root and no longer lists the removed hidden path

#### Scenario: A redundant call still notifies

- **WHEN** a host shows a node that is already shown
- **THEN** the listener is notified, and the state it receives reports the
  same visibility it reported before

#### Scenario: A refused operation notifies nobody

- **WHEN** a host focuses an unknown path and the viewer refuses it
- **THEN** the refusal names the path, the navigation state is unchanged,
  and no listener is notified

#### Scenario: A cancelled subscription and a disposed viewer are silent

- **WHEN** a host cancels its subscription, or disposes the viewer, and
  then focus or visibility would otherwise change
- **THEN** the listener is not notified again, and cancelling twice is
  harmless

#### Scenario: Mounting notifies nobody

- **WHEN** a host mounts a viewer and subscribes to the handle it receives
- **THEN** the listener has not been called, the handle's reads already
  report the mounted assembly and the document root, and the first
  notification follows the first change

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

### Requirement: A maker moves the viewer from the navigator

The navigator SHALL let a maker focus a subtree, restore the published
document root, and hide or show a subtree, driving the viewer through the
same operations a host calls. Restoring the document root SHALL be
offered while a subtree is focused, and the navigator SHALL be able to
present that affordance or leave it to its host.

Each row SHALL carry a visibility control with checkbox semantics that
appears as a square filled with the node's effective colour while the
node is shown, uses a neutral fill when a shown node has no effective
colour, and appears empty with only its border while the node is hidden.
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
- **THEN** the shown node's control is checked and filled with its
  effective colour, the hidden node's control is unchecked and empty with
  only its border, and both report their checked state to assistive
  technology

#### Scenario: A colourless node is shown

- **WHEN** a shown node has no effective colour
- **THEN** its control uses the neutral fill and stays distinguishable
  from the empty hidden state

#### Scenario: A descendant of a hidden node is distinguished

- **WHEN** a node with descendants is hidden and its descendants' rows
  are presented
- **THEN** each descendant's control still reports that descendant's own
  visibility setting, its row is marked as obscured, and its control's
  accessible name names the hidden ancestor

### Requirement: The navigator has a keyboard contract

While keyboard focus is on a row, the navigator SHALL move between the
presented rows with Up and Down; expand a collapsed parent with Right and
move into its first child when it is already expanded; collapse an
expanded parent with Left and move to the parent row otherwise; focus the
row's node in the viewer with Enter; and toggle the row's own visibility
with Space. Each of these SHALL suppress the key's default page
behaviour. A row's own controls SHALL remain operable by pointer without
requiring a separate tab stop.

#### Scenario: A maker walks the tree

- **WHEN** keyboard focus is on a row and the maker presses Down and then
  Up
- **THEN** keyboard focus moves to the next presented row and back, and
  the page does not scroll in response

#### Scenario: A maker opens and leaves a subtree

- **WHEN** the maker presses Right on a collapsed parent, Right again,
  and then Left twice
- **THEN** the parent expands, focus moves into its first child, the
  child's focus returns to the parent, and the parent collapses

#### Scenario: A maker focuses and hides from the keyboard

- **WHEN** the maker presses Enter on a row and Space on another
- **THEN** the viewer focuses the first row's node and toggles the second
  row's visibility, exactly as the pointer affordances would

### Requirement: The navigator follows the viewer it was given

The navigator SHALL hold no copy of the viewer's focused root or hidden
paths: it SHALL read both from the handle and re-read them from every
change it is notified of. It SHALL subscribe to the handle's assembly
changes when it mounts and redraw from what the notification carries, so
a change of the published tree, the focused root or the visibility state
reaches it whatever caused it — a host call, an affordance the widget
presents, or a targeted update. It SHALL call the viewer only in response
to a maker's gesture and never from inside that subscription. Because the
viewer notifies before the gesture's call returns, the navigator SHALL
tolerate being redrawn while the gesture's own event is still being
handled: the redraw SHALL complete, the element the maker acted on may be
replaced, and keyboard focus SHALL land on the active row when it was
anywhere inside the tree.

Which rows are expanded and which row holds keyboard focus SHALL belong
to the navigator and not to the viewer, so two navigators on one handle
may present different parts of the tree while never disagreeing about
what is focused or hidden. Across an update the navigator SHALL retain
that state for paths the new tree still contains, discard the rest, and
keep the tree usable with keyboard focus preserved when it was inside the
tree. On its first draw the root SHALL be expanded. When the focused root
moves to a node the maker cannot currently see, the navigator SHALL
reveal that node.

#### Scenario: A focus change made inside the widget reaches the navigator

- **WHEN** the maker moves focus with an affordance the widget itself
  presents, while a navigator is mounted on the same handle
- **THEN** the navigator marks the newly focused node as the focused
  root, without any host code between them

#### Scenario: A targeted update reconciles the navigator

- **WHEN** a targeted update removes a node the navigator had expanded
  and keeps another it had expanded
- **THEN** the removed node's row is gone, the surviving node stays
  expanded, the tree still has exactly one keyboard stop, and the
  navigator shows the viewer's reconciled focused root

#### Scenario: Two navigators on one viewer agree

- **WHEN** two navigators are mounted on one handle and a maker hides a
  node in one of them
- **THEN** both show that node as hidden, while each keeps its own
  expanded rows and its own keyboard position

#### Scenario: A focus moved into a collapsed subtree is revealed

- **WHEN** the focused root moves to a node whose ancestors the maker had
  collapsed
- **THEN** the navigator expands those ancestors so the focused root's
  row is presented

### Requirement: A navigator is disposed independently of its viewer

The navigator's handle SHALL dispose it: cancel its subscription and
empty the element it was mounted into. Disposing SHALL be safe more than
once. The navigator and its viewer SHALL be disposable in either order: a
navigator disposed first SHALL leave the viewer working, and a navigator
whose viewer was disposed first SHALL receive nothing further, stay
inert, and dispose without error. A maker's gesture that the viewer
refuses or cannot serve SHALL change nothing and SHALL NOT propagate a
failure into the host page.

#### Scenario: A host disposes the navigator

- **WHEN** a host disposes a navigator and then changes the viewer's
  focus
- **THEN** the navigator's element is empty, nothing is redrawn, and
  disposing it a second time does nothing

#### Scenario: A host disposes the viewer first

- **WHEN** a host disposes the viewer while a navigator is mounted, and a
  maker then uses one of the navigator's affordances
- **THEN** nothing is thrown into the page, the navigator shows what it
  last drew, and disposing it afterwards still empties its element

### Requirement: The navigator is styled by one stylesheet a host can theme

The navigator SHALL be presented by one stylesheet the bundle carries,
added to the document it is mounted into exactly once however many
navigators are mounted there, and identifiable so a host can find it. The
package SHALL publish no additional file for it: the export directory
SHALL keep carrying exactly the page and the one bundle.

Every element the navigator builds SHALL carry a stable class name under
one documented prefix, and the palette and metrics of the default
presentation — type, indent per level, row padding and height, chip size,
text, hover, focused-root, obscured and focus-ring colours — SHALL be
CSS custom properties. A host SHALL be able to restyle the navigator
completely by overriding those properties, without reaching into the
navigator's elements. The default presentation SHALL be legible on a
light and on a dark page. A host SHALL be able to suppress the injected
stylesheet and present the same class contract from its own.

#### Scenario: Two navigators inject one stylesheet

- **WHEN** two navigators are mounted in one document
- **THEN** the document carries exactly one identifiable navigator
  stylesheet, and both are presented by it

#### Scenario: A host themes the navigator

- **WHEN** a host overrides the navigator's documented custom properties
  from its own stylesheet
- **THEN** the navigator adopts that type, indent, and palette with no
  change to the package and no host code touching its elements

#### Scenario: A host presents the navigator itself

- **WHEN** a host mounts a navigator asking for no injected stylesheet
- **THEN** no stylesheet is added to the document, and the navigator's
  elements still carry the documented class names for the host's own
  rules

