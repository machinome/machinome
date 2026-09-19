## ADDED Requirements

### Requirement: A joint's placement is replaced whole

A joint's placement is every operation its last binding applied to the node,
and the system SHALL remove ALL of them when that joint is placed again or
cleared — however many operations the placement produced, and whatever has
happened to the node's operation list in between. A tool that replaces a
node's `operations` wholesale (the test runner's checkpoint restore, a pose
capture, a test) SHALL NOT be able to strand an operation of a previous
placement beside the new one, and SHALL NOT be able to make a later binding
state a body's travel twice.

A node carrying several joints SHALL be unaffected in its other joints:
re-placing one removes that joint's operations and leaves every other
joint's where they stand, at their own declared positions. Clearing a joint
removes its placement and adds nothing.

This is the other half of "An author-bound joint is cleared with its
motion": that requirement drops a coordinate whose motion was swept, and
this one drops the motion of a coordinate that is bound again.

#### Scenario: A placement survives no wholesale replacement of the list

- **WHEN** a leaf's prismatic coordinate is bound, the node's operation list
  is then replaced with a copy of an earlier list that still holds that
  placement's operation, and the coordinate is bound again
- **THEN** the leaf carries exactly one translation from that joint, stating
  the value bound last, and the body stands where its coordinate says

#### Scenario: A many-operation placement goes as one

- **WHEN** the same happens to a leaf carrying a `Free` joint, whose one
  binding places several operations
- **THEN** the leaf carries exactly one run of that joint's operations after
  the second binding, and no operation of the first placement remains

#### Scenario: A sibling joint is left alone

- **WHEN** a node declaring two joints has one of them bound again after its
  operation list was replaced
- **THEN** only the re-bound joint's operations are replaced, the other
  joint's placement is untouched, and the two still compose in declaration
  order

#### Scenario: Clearing removes a stranded placement too

- **WHEN** a joint whose operation list was replaced under it is cleared
- **THEN** no operation of its placement is left on the node

## MODIFIED Requirements

### Requirement: An author-bound joint is cleared with its motion

A joint's coordinate holds a value and the joint's placement holds
operations, and the two are halves of ONE binding. The system SHALL drop
them together: at the start of an assembly's simulate phase, in the same
moment as the sweep that removes the operations that assembly applied,
the framework SHALL clear the value and the binder record of every
coordinate that assembly bound DURING ITS PREVIOUS SIMULATE PHASE —
including a coordinate the author's own `simulate()` bound — AND SHALL
remove that coordinate's joint's whole placement from the node that owns
it, whatever applied that placement and whether or not the sweep can see
it.

A coordinate SHALL therefore never go on holding a value whose motion
has been swept, and a joint's motion SHALL NOT outlive its coordinate's
value: a body SHALL NOT stand at a pose no coordinate states. An assembly
that binds a joint under a guard such as `if <coordinate>.value is None:`
SHALL find the coordinate unbound on every run and SHALL rebind and
re-place the body on every run, so the pose it states on the first
enumeration is the pose it states on the second and the tenth; and an
assembly that binds a joint under a guard that is TRUE on one instant and
FALSE on the next SHALL leave the body at rest on that next instant, with
nothing of the previous instant's placement on it.

A binding made OUTSIDE any simulate phase — in `__init__`, in a test, or
through a `render()` no walker drove — SHALL NOT be cleared, exactly as
an operation applied outside a phase is never swept, and two assemblies
that bind coordinates of one node SHALL clear only their own. A
coordinate a running simulation owns SHALL NOT be cleared either, and
neither SHALL its placement: the run binds outside every enumeration and
rebinds on every tick.

Between one enumeration and the next, a joint's coordinate SHALL go on
reading what the last enumeration bound, so a test, a serializer or a
pose capture that reads a joint after a walk reads the pose that walk
produced.

#### Scenario: A rest-default joint stands where it says it stands

- **WHEN** a root whose `simulate()` reads a child's prismatic
  coordinate, finds it unbound and binds it to a non-zero rest default
  is enumerated three times
- **THEN** the child carries the translation of that default on every
  run, and the coordinate reads that default after each of them

#### Scenario: A stale value cannot outlive its motion

- **WHEN** the same tree is enumerated a second time
- **THEN** at no point does the coordinate hold a value while the body
  carries no operation from it: the value and the operations were
  dropped together and rebound together

#### Scenario: A joint bound outside a phase keeps its value

- **WHEN** a test binds a joint of a node it constructed itself, with no
  walker and no simulate phase running, and then reads it
- **THEN** the value and the placement are still there, because nothing
  recorded the binding on a phase and nothing swept it

#### Scenario: A stale motion cannot outlive its value

- **WHEN** a root binds a root-level leaf's joint under a guard that is
  true at one instant and false at the next, and the placement standing
  at the second instant was applied outside any simulate phase — so no
  sweep can reach it
- **THEN** the body is at rest at that second instant, carrying no
  operation of the first instant's placement, and the coordinate is
  unbound

#### Scenario: The run's own placement is not cleared

- **WHEN** a running simulation owns a leaf's joint coordinate and the
  root is enumerated again
- **THEN** the value and the placement the run made are both still
  there, because the coordinate is the run's and nothing else clears it
