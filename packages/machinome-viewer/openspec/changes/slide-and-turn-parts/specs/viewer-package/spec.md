## MODIFIED Requirements

### Requirement: The viewer declares its API version

The package SHALL declare one API version, expose it on every mount handle and
the browser global, and make it readable without executing the bundle. It SHALL
be raised whenever the mount interface or handle changes incompatibly, and when
a capability a host may require is added. The declared version SHALL be 13,
reflecting direct sliding controls, separately reachable sliding and turning
freedoms on one part, and current selected-joint interaction frames, on top
of the existing press/turn controls and all previously declared capabilities.

The package SHALL also declare, in the same one place, the document schema
versions this build reads, and SHALL report them beside the API version
wherever the API version is reported. A consumer asking which documents a
viewer reads SHALL be answered with that list rather than having to infer
it from the API version, and a consumer that receives no such list SHALL be
entitled to assume the versions every released viewer reads. Reading a
document's controls table SHALL NOT change that list: the table is additive
within the running document version, and the API version is the only
capability gate it moves.

#### Scenario: A host checks compatibility before mounting

- **WHEN** a host reads the installed viewer API version
- **THEN** it obtains the package's single declared version without running a
  browser bundle

#### Scenario: A mounted viewer reports its version

- **WHEN** a host inspects a mount handle or the browser global
- **THEN** both report the same declared API version

#### Scenario: A host requires targeted updates

- **WHEN** a host needs `artifactChanged()` and `manifestChanged()`
- **THEN** the declared API version tells it whether they are available

#### Scenario: A host requires camera orientation control

- **WHEN** a host needs to supply an up direction and field of view
- **THEN** the declared API version tells it whether they are available

#### Scenario: A host requires flexible geometry

- **WHEN** a host needs `version: 3` documents rendered
- **THEN** the declared API version tells it whether the capability is
  available

#### Scenario: A host requires documents carrying a bindings table

- **WHEN** a host needs `version: 4` documents rendered
- **THEN** the declared API version tells it whether the capability is
  available

#### Scenario: A host requires the published navigation state

- **WHEN** a host needs to read the focused root and the hidden paths, and
  to be told when they change
- **THEN** the declared API version tells it whether the capability is
  available, before it mounts a bundle it cannot build a navigator on

#### Scenario: A host requires the mountable navigator

- **WHEN** a host means to present the package's own assembly navigator
  rather than build one
- **THEN** the declared API version tells it whether the bundle carries
  one, before it mounts a bundle that publishes the navigation state but
  no navigator

#### Scenario: A host requires the inspector layout

- **WHEN** a host means to mount the package's composed inspector —
  sidebar, navigator and viewer in one element — rather than lay those
  parts out itself
- **THEN** the declared API version tells it whether the bundle carries
  one, before it mounts a bundle that carries a navigator and no layout to
  put it in

#### Scenario: A host requires part controls

- **WHEN** a host means to present a machine a maker drives by touching it,
  rather than only from a panel
- **THEN** the declared API version tells it whether this bundle reads a
  document's controls table and binds a pick to it, before it mounts a
  bundle that would show the same document with no affordance at all

#### Scenario: A producer asks which documents this viewer reads

- **WHEN** a producer asks the installed viewer what it reads, before
  publishing a document
- **THEN** it receives the list of document schema versions this build
  renders, including the running version, from the same declaration the
  bundle refuses by

#### Scenario: A host requires direct sliding and composed-joint controls

- **WHEN** a host needs a machine with sliding parts and a crank that both
  lifts and turns
- **THEN** API version 13 reports that those controls and their reachable
  gesture points are supported, without claiming a new document schema version


### Requirement: A maker presses and turns the part itself

For a document carrying a program and a table of controls, the mounted
viewer SHALL make each part that table names touchable, and SHALL leave
every other part exactly as it is today — a surface that moves the camera.

A touchable part SHALL, while the pointer is over it, present a pointer
cursor, a visible change distinguishing it from the parts around it
wherever its material admits one, and the declared display names of every
control that names it. A part the viewer is not currently showing — hidden
through the assembly navigation, or outside the focused subtree — SHALL NOT
be touchable, and a part standing in front of a touchable one SHALL NOT be
reached through.

A **press** — a pointer pressed and released on a touchable part without
travelling beyond a small threshold — SHALL submit that part's declared
instruction to the run, and SHALL be indistinguishable to the run, to its
listeners and to a readback from pressing that instruction's button on the
panel. A press on a part that declares no instruction SHALL move nothing
and report nothing.

A **drag** — a pointer travelling beyond that threshold while engaged on a
touchable part — SHALL be measured as an angle swept about a Turn's joint
or signed displacement along a Slide's joint, in the sense and units of
the selected coordinate. Each time the accumulated movement crosses one
**quantum** — the
input's current nudge amount, converted to that coordinate through the
ratio the document publishes — the viewer SHALL issue exactly one request
to move that input by that amount over that duration, in the direction the
sweep and the ratio together give. It SHALL have at most one such request
in flight at a time, because the run gives an input one owner at a time,
and SHALL issue the next only once the previous has retired. The quanta a
gesture owes SHALL be derived from where the pointer stands, never
accumulated as a queue, so a sweep forward and back nets out rather than
being paid for twice.

The part SHALL follow the movements the run **commits** and never the
pointer: the pointer may run ahead while the machine catches up, and a
machine that will not move does not move.

A request that does not complete SHALL NOT advance the point the next
quantum is measured from, so a drag against a stop reports the travel the
machine actually admitted, leaves no remainder to be executed later, and
does not repeat itself while the gesture is held there.

While a gesture is engaged on a part the camera SHALL NOT move. A gesture
SHALL end on release, on a cancelled pointer, on lost pointer capture, on
lost window focus, and when the page stops being displayed, and on every
one of those the camera SHALL become movable again and the affordance SHALL
be cleared. A press or a drag issued while the run is paused SHALL start
it.

The outcome of a request a gesture made SHALL be reported where it was
made — beside the pointer — and at the panel's control for the same
instruction or input, through the one path every other request is reported
by, in the same words.

Nothing in a press, turn or slide SHALL write a coordinate, pose a part, or move
anything except by a request the run commits.

When one part carries both sliding and turning controls, the viewer SHALL
present separately identifiable on-part axial and turning handles while
hovered or selected. Grabbing a handle SHALL select exactly that control
until the gesture ends. Both handles SHALL be discoverable and reachable
without a keyboard modifier, including with touch. A body press SHALL retain
its declared instruction behavior; an ambiguous body drag SHALL NOT choose
a freedom or submit a movement. The handles SHALL obey the part's visibility,
focus and occlusion, and SHALL NOT reposition another part or control.

Gesture geometry SHALL follow the selected joint's current interaction frame
as the machine moves. An inner motion SHALL NOT rotate an outer joint's
axis. When the view makes axial displacement indeterminate, a Slide SHALL
report that the view needs rotating and SHALL submit no guessed movement.

Every control a part carries SHALL also be reachable from the running
panel — a declared instruction has a button there and a declared input has
a nudge pair — so the affordance adds a way to ask and never the only way.

#### Scenario: A press advances the dial

- **WHEN** a maker presses a part the document declares a button on
- **THEN** the run receives that instruction, the machine moves exactly as
  it moves when the panel's button for it is pressed, and the outcome is
  reported beside the pointer and on that button

#### Scenario: A part nothing declares still moves the camera

- **WHEN** a maker presses and drags a part the table does not name
- **THEN** the camera orbits exactly as it did before the viewer read
  controls, and no request reaches the run

#### Scenario: A part the navigator is not showing is not touchable

- **WHEN** a maker hides a touchable part, or focuses a subtree that does
  not contain it, and then presses where it stood
- **THEN** nothing is pressed, no request reaches the run, and the camera
  orbits instead

#### Scenario: A part in front is not pressed through

- **WHEN** a touchable part stands behind another part the maker presses
- **THEN** the front part is what was pressed, which declares no control,
  so no request reaches the run

#### Scenario: A drag enters one digit at a time

- **WHEN** a maker drags a dial through three quanta of sweep, letting each
  request retire
- **THEN** three movement requests were issued, one at a time, the input
  stands three amounts further on, and the part stands where the run's
  committed frames put it

#### Scenario: A drag against a stop reports blocked and leaves no backlog

- **WHEN** a maker drags a dial in the direction its declared stop forbids,
  past more than one quantum, and holds it there
- **THEN** the first quantum is reported blocked with the travel the
  machine admitted, the part has not moved, no further request is issued
  while the gesture stays there, and releasing and pressing again asks for
  a fresh movement rather than resuming a stored one

#### Scenario: A gesture ends on every side an interaction can

- **WHEN** a maker drags a part and then releases, has the pointer
  cancelled, loses pointer capture, moves focus out of the window, or
  leaves the page
- **THEN** in every one of those cases the gesture ends, the camera becomes
  movable again, and nothing new is requested

#### Scenario: A press into a paused run starts it

- **WHEN** a maker presses a part while the run is paused
- **THEN** the run starts and the request is carried out, exactly as a
  press on the panel does

#### Scenario: The pointer never poses the part

- **WHEN** a maker drags a dial faster than the run can follow
- **THEN** the part stands where the last committed frame put it at every
  instant, and reaches the requested position only as the run commits it

#### Scenario: A selector slides along its rail

- **WHEN** a maker drags a selector through three admitted translational quanta
- **THEN** exactly three sequential requests reach its declared input,
  and the selector follows only the run's committed positions

#### Scenario: A crank is lifted and turned independently

- **WHEN** a maker chooses the axial handle on a crank carrying a Slide,
  Turn and Button, drags, releases and then chooses the turning handle
- **THEN** the first gesture requests only its lift input and the second
  only its turn input, with no implicit seating, lifting or mode change

#### Scenario: Clicking remains a separate physical request

- **WHEN** a maker presses and releases that crank body without dragging
- **THEN** its declared instruction is submitted exactly once, and
  no slide or turn drag request is submitted

#### Scenario: An ambiguous body drag does not choose for the maker

- **WHEN** a maker drags a body with both sliding and turning controls
  without selecting either of its visible handles
- **THEN** no movement request is submitted and the two handles remain
  independently identifiable

#### Scenario: Touch can select either physical freedom

- **WHEN** a maker selects a two-freedom part using touch
- **THEN** both on-part handles become reachable, and touching and dragging
  either selects that control without requiring a keyboard modifier

#### Scenario: Sliding against an interlock leaves no delayed action

- **WHEN** a slide request is blocked by a run constraint and the maker
  keeps the gesture held, then releases it and moves the interlocking part
- **THEN** no further slide request occurs without a fresh gesture and
  no stored pointer travel moves the now-unblocked part

#### Scenario: An end-on rail requires a different view

- **WHEN** the camera looks too nearly along a sliding axis to measure travel
- **THEN** the viewer indicates that the view must rotate, submits no
  movement for the attempted drag, and permits normal camera movement once
  the gesture is released

#### Scenario: Moving ancestors carry the gesture frame

- **WHEN** a controlled joint's ancestor moves during an engaged gesture
- **THEN** the gesture uses the joint's current committed placement and
  does not keep using the pointer-down axis or pivot

### Requirement: A host reads the controls a document's parts carry

The mount handle SHALL expose the controls the loaded document declares.
For each it SHALL report the declared display name, the kind, the part and
the joint as node-name paths, the instruction it submits or the input it
moves with the published ratio, the selected coordinate and placement metadata,
where the part stands on screen at that moment, and a point at which a press reaches
that control at that moment — or nothing for either where the part is not
visible, is wholly off screen, or is reached at no point.

For every drag control the listing SHALL also report a reachable gesture
point: on its drag handle when its part carries two freedoms, or on the part
itself for an ordinary single-freedom drag. An unavailable or occluded handle
SHALL have no reachable gesture point. The existing part rectangle and button
press point meanings SHALL remain unchanged.

Positions SHALL be reported in the same coordinates and the same units as
the rectangles the host's own document elements report, so a host or a test
may act on them without converting.

The listing SHALL be answered for a document that declares no control, as
an empty listing, and SHALL be answered whether or not the affordance is
presented — what a presentation choice gates is the pixels and the pointer,
never the interface.

#### Scenario: A host labels the parts itself

- **WHEN** a host asks the handle for the document's controls and draws its
  own label beside each reported position
- **THEN** the labels stand over the parts, and move with them as the
  camera moves

#### Scenario: A test presses where the viewer says

- **WHEN** a test asks for the controls and sends a real pointer press to
  the point reported for one
- **THEN** that control's request reaches the run

#### Scenario: A part that is not shown reports no position

- **WHEN** a host asks for the controls while one control's part is hidden
- **THEN** that control is still listed, with its declaration intact and no
  position and no point

#### Scenario: A document declaring no control answers plainly

- **WHEN** a host asks a document that carries no controls
- **THEN** it receives an empty listing rather than an error or an absent
  operation

#### Scenario: A host can target both freedoms without private scene access

- **WHEN** a host reads controls for a visible crank with sliding and
  turning controls
- **THEN** each control reports its own reachable gesture point in viewport
  CSS coordinates, and a real drag at that point selects that control

### Requirement: A controls table the viewer cannot resolve is refused by name

A document whose controls table the viewer cannot resolve SHALL be refused
when it is loaded, naming the document, the control and what is wrong,
before anything is rendered — the surface an undeclared driver id, an
unreadable bindings table and an inexecutable program already stand on. A
document is refused when:

- the table, or an entry in it, is not of the published shape, or an
  entry's kind is not a button, turn or slide;
- an entry's part or joint does not name exactly one node of that
  document's own tree, or the joint is not that part or one of its
  ancestors;
- an entry names an instruction its document's instruction table does not
  declare, an input its drivers table does not declare, or a coordinate its
  program does not publish — each refusal naming what the document does
  declare;
- a turn's or slide's published ratio is missing, not a finite number, or zero, which
  would make the gesture's quantum meaningless;
- an entry's axis or origin is not three finite numbers, or its axis has no
  direction;
- an entry without a selected operation span fails the legacy rotational
  placement rule: its coordinate must pose the joint's LEADING run of
  operations, consisting of a rotation alone or its complete pivot placement;
- a selected operation span is malformed, outside the joint node's operation
  list or does not identify the complete placement of the selected coordinate;
- a turn's selected placement is not rotational or a slide's is not
  translational; a button SHALL accept either placement domain;
- two controls of the same kind name the same part, so that one gesture
  would have two meanings and the viewer would have to choose;
- the document carries a controls table and no program, which every
  document below the running version is, since a control has nothing to
  submit a request to.

A document that carries no controls table SHALL load, pose, run and drive
exactly as it did before the viewer could read one.

#### Scenario: A part that does not resolve is named

- **WHEN** a document's control names a part its own tree does not contain
- **THEN** mounting fails naming the document, the control and the path,
  and nothing is rendered

#### Scenario: An instruction the document does not declare is named

- **WHEN** a document's press control names an instruction absent from its
  instruction table
- **THEN** mounting fails naming the control, the instruction and the
  instructions the document does declare

#### Scenario: A ratio of zero is refused

- **WHEN** a document's turn control publishes a ratio of zero
- **THEN** mounting fails saying the gesture has no quantum, rather than
  presenting a part that cannot be turned

#### Scenario: A joint that does not pose the coordinate is refused

- **WHEN** a document's legacy control without an operation span names a
  joint whose own operations do not begin with that coordinate's rotation,
  or with translations and then that rotation
- **THEN** mounting fails naming the control, the joint and what the joint
  is posed by, rather than turning the part about a line derived from it

#### Scenario: A joint placed off its node's origin is accepted

- **WHEN** a document's control names a joint whose operations are a
  translation, the rotation over the coordinate, and the translation back,
  and whose entry publishes the point it turns about as `origin`
- **THEN** mounting succeeds, and a drag on the part is measured about the
  line through the world image of `origin` along the world image of `axis`
  — the same line the joint's own placement turns the part about

#### Scenario: A control without a run is refused

- **WHEN** a document below the running version, or one carrying no
  program, carries a controls table
- **THEN** mounting fails naming the table, rather than presenting an
  affordance with nothing to ask

#### Scenario: A document with no controls is untouched

- **WHEN** a document carrying no controls table is mounted
- **THEN** it loads, poses, runs and is driven exactly as it was before
  this capability existed, and its parts move the camera


#### Scenario: A selected prismatic placement is accepted

- **WHEN** a document carries a Slide or Button whose selected operation
  span identifies its named prismatic coordinate's complete placement
- **THEN** mounting succeeds without requiring a rotational placement

#### Scenario: A selected non-leading joint is accepted

- **WHEN** a two-joint body carries separate controls whose spans identify
  each selected joint's actual placement
- **THEN** mounting succeeds and each gesture uses its own selected frame
  instead of treating the whole body's world matrix as both joint frames

#### Scenario: A malformed selected placement is named

- **WHEN** a control's span points outside the operation list, to another
  coordinate's placement, or to only part of an off-centre pivot placement
- **THEN** loading is refused naming the control and offending span before
  the existing scene is replaced

#### Scenario: A slide cannot name a rotational placement

- **WHEN** a Slide identifies a rotational placement
- **THEN** mounting is refused naming the control and domain mismatch

#### Scenario: Duplicate slides remain ambiguous

- **WHEN** two Slide controls name the same part
- **THEN** mounting is refused naming both controls instead of choosing
  which input the same sliding gesture should move
