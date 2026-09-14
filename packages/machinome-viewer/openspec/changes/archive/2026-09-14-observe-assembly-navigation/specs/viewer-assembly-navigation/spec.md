## ADDED Requirements

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
