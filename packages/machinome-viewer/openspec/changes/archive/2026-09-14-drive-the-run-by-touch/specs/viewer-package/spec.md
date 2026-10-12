## ADDED Requirements

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
touchable part — SHALL be measured as an angle swept about the joint the
control names, in the sense and the units of the coordinate that joint
poses. Each time the accumulated sweep crosses one **quantum** — the
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

Nothing in either gesture SHALL write a coordinate, pose a part, or move
anything except by a request the run commits.

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

### Requirement: A host reads the controls a document's parts carry

The mount handle SHALL expose the controls the loaded document declares.
For each it SHALL report the declared display name, the kind, the part and
the joint as node-name paths, the instruction it submits or the input it
moves with the published ratio, the coordinate it turns about, where the
part stands on screen at that moment, and a point at which a press reaches
that control at that moment — or nothing for either where the part is not
visible, is wholly off screen, or is reached at no point.

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

### Requirement: A controls table the viewer cannot resolve is refused by name

A document whose controls table the viewer cannot resolve SHALL be refused
when it is loaded, naming the document, the control and what is wrong,
before anything is rendered — the surface an undeclared driver id, an
unreadable bindings table and an inexecutable program already stand on. A
document is refused when:

- the table, or an entry in it, is not of the published shape, or an
  entry's kind is neither a press nor a turn;
- an entry's part or joint does not name exactly one node of that
  document's own tree, or the joint is not that part or one of its
  ancestors;
- an entry names an instruction its document's instruction table does not
  declare, an input its drivers table does not declare, or a coordinate its
  program does not publish — each refusal naming what the document does
  declare;
- a turn's published ratio is missing, not a finite number, or zero, which
  would make the gesture's quantum meaningless;
- an entry's axis or origin is not three finite numbers, or its axis has no
  direction;
- the joint the entry names is not posed by the coordinate the entry names
  as the LEADING run of its own operations — zero or more translations and
  then exactly one rotation over that coordinate, which are the two shapes
  the producer's joint placement publishes: the rotation alone, or a
  translation, the rotation and the translation back for a joint placed off
  its node's origin — the reading the gesture's geometry depends on;
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

- **WHEN** a document's control names a joint whose own operations do not
  begin with that coordinate's rotation, or with translations and then
  that rotation
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

## MODIFIED Requirements

### Requirement: One loader reads either published document

The viewer SHALL render either portable `manifest.json` or normal-build
`viewer.json`, reading their shared fields. It SHALL render document
versions 1, 2, 3, 4 and 5, and SHALL refuse any other version naming it
and the versions it renders. A document whose `drivers`
table is empty SHALL render exactly as a version 1 document. A document
whose `drivers` table is non-empty SHALL load and render at the pose its
expressions evaluate to under the table's declared defaults, with driver
and instruction entries exposed through the handle's driving API. A
document whose expressions reference a qualified id absent from both its
`drivers` table and its `bindings` table is malformed and SHALL fail
loudly naming the id; under version 5 the identifiers an expression may
name also include the program's clock name, its bank coordinates, the
values it publishes as computed, and, inside a jump plan's own
expressions, that plan's branch placeholders. A version 4 document carries
an ordered `bindings` table, which the viewer SHALL resolve under the
binding requirements above; a document that carries no such table SHALL be
read exactly as it was before the viewer knew of bindings. A version 5
document additionally carries a `program` object, which the viewer SHALL
load and validate under the program requirements above, and whose bank
SHALL pose the tree. A version 5 document MAY also carry a `controls`
table, which the viewer SHALL read and validate under the control
requirements above; the table is additive and does not move the document's
version, a document carrying none SHALL be read exactly as it was before
the viewer knew of controls, and a document below version 5 carrying one
SHALL be refused naming it. The
host supplies the document URL
and an optional mesh base; the base defaults to the document's directory, which
for a document URL naming no directory is the directory the document is served
from and never the server root. A fetch or parse failure SHALL name the
document and the reason.

#### Scenario: A build snapshot rooted elsewhere

- **WHEN** a host mounts a `viewer.json` with a mesh base unrelated to its
  document URL
- **THEN** models load from that base with the same tree, colours, and
  animation as the equivalent export

#### Scenario: A self-contained export

- **WHEN** a host mounts an export without supplying a mesh base
- **THEN** its model paths resolve beside the manifest and it renders

#### Scenario: An export served under a subpath

- **WHEN** a host mounts a document URL that names no directory, as the shipped
  export page does with `manifest.json`, and the page is served under a
  subpath rather than at the server root
- **THEN** model paths resolve beside that document under the same subpath, and
  no request is made to the server root

#### Scenario: An unreachable document

- **WHEN** the source document cannot be fetched
- **THEN** mounting fails with an error naming the document and failure

#### Scenario: A driver document renders at its defaults

- **WHEN** a host mounts a document whose `drivers` table declares
  `x_axis.motor` with default 8000
- **THEN** the model renders at the pose its expressions evaluate to
  with `x_axis.motor = 8000`, and no error is raised

#### Scenario: A malformed driver document is refused

- **WHEN** a mounted document's expressions reference a qualified id
  neither its `drivers` table nor its `bindings` table declares
- **THEN** mounting fails naming that id rather than rendering a wrong
  pose

#### Scenario: A document carrying a bindings table is rendered

- **WHEN** a host mounts a document declaring version 4 and carrying a
  non-empty `bindings` table
- **THEN** it renders at the pose its expressions evaluate to through that
  table

#### Scenario: A document carrying a program is rendered

- **WHEN** a host mounts a document declaring version 5 and carrying a
  `program` object
- **THEN** it renders at the pose the program's published rest values
  evaluate to, and its run is available on the handle

#### Scenario: A document carrying a controls table is rendered

- **WHEN** a host mounts a document declaring version 5 and carrying both a
  `program` object and a `controls` table
- **THEN** it renders exactly as the same document without that table does,
  its run is available on the handle, and the parts the table names are
  touchable

#### Scenario: A version beyond the ones it reads is refused

- **WHEN** a host mounts a document declaring version 6
- **THEN** mounting fails naming that version and the versions the viewer
  renders

#### Scenario: Older documents are untouched

- **WHEN** a host mounts a document declaring version 1, 2, 3 or 4
- **THEN** it loads, poses, animates and drives exactly as it did before
  the viewer could read a program

### Requirement: The viewer declares its API version

The package SHALL declare one API version, expose it on every mount handle and
the browser global, and make it readable without executing the bundle. It SHALL
be raised whenever the mount interface or handle changes incompatibly, and when
a capability a host may require is added. The declared version SHALL be 12,
reflecting the addition of part controls — a press and a turn on the part
itself, bound to a control the document declares, with the listing of those
controls on the handle and the presentation choice that gates them — on top
of the inspector layout, the mountable assembly navigator, the published
assembly-navigation state and its change subscription.

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

### Requirement: The host chooses how driver controls are presented

The host SHALL be able to choose at mount time whether the on-screen
chrome (controls and focus affordance) is presented, for a posed document
and for a running one alike. By default it is
presented for documents that declare drivers. A host that suppresses
it SHALL retain the full driving API unchanged, and for a running
document the full run API unchanged.

The host SHALL be able to choose, **independently of that**, whether the
parts a document's controls table names are touchable. By default they are,
for a document that declares them. A host that suppresses the panel and
keeps the parts touchable SHALL get exactly that, and so SHALL a host that
does the opposite: the two choices gate different pixels and neither gates
an interface. A host that suppresses the part affordance SHALL retain the
listing of the document's controls on the handle, and the full run API,
unchanged.

#### Scenario: A shop floor builds its own instrument panel

- **WHEN** a host mounts with the driver chrome suppressed
- **THEN** no on-screen driver control or focus affordance appears
  while `drivers()`, `setDriver`, `trigger`, and `onDriverChange`
  behave exactly as when the chrome is shown

#### Scenario: A published export shows the controls

- **WHEN** a maker opens a self-contained export of a driver-declaring
  document with default options
- **THEN** the driver chrome is presented

#### Scenario: A host drives a running machine from its own panel

- **WHEN** a host mounts a document carrying a program with the chrome
  suppressed
- **THEN** no running control or transport appears, while the run
  behaves exactly as it does when they are shown

#### Scenario: A published export of a running model runs

- **WHEN** a maker opens a self-contained export of a document carrying a
  program, from a static directory and with default options
- **THEN** the running controls and the transport are presented, and the
  machine runs offline

#### Scenario: A host keeps the dial pressable and builds its own panel

- **WHEN** a host mounts a document carrying controls with the panel
  suppressed and the part affordance left as it is
- **THEN** no panel or transport appears, the parts the table names are
  still touchable, and a press reports its outcome beside the pointer

#### Scenario: A host suppresses the part affordance

- **WHEN** a host mounts a document carrying controls with the part
  affordance suppressed
- **THEN** no part shows a cursor, a highlight or a name, pressing a part
  moves the camera, and the handle still lists the document's controls
  and drives the run unchanged
