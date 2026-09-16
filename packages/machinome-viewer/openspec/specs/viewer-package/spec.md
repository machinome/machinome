# Viewer Package Specification

## Purpose

The reusable, React-free browser viewer: the mount interface, handle,
document loading, animation, camera, drivers, instructions, flexible
geometry and declared API version shared by static exports, the development
app, the snapshot capture and every other host. Migrated from solid-node's
baseline when the viewer became this package; behaviour unchanged.

Code: `solid_node_viewer/widget/src/`.
## Requirements
### Requirement: A host mounts the viewer and receives a handle

The viewer SHALL mount into a caller-supplied container against a published tree
document and resolve to a handle. The handle SHALL expose `dispose()` (stop
rendering, release resources and empty the container), `view()` (camera position
and orbit target), `reload()` (rebuild the document while preserving the view),
`artifactChanged(path)` and `manifestChanged()` (update only what changed),
assembly inspection and navigation operations, and the declared API version.
Loading the viewer core SHALL NOT modify the document; only an explicit mount
may do so.

#### Scenario: A host unmounts a viewer

- **WHEN** a host calls `dispose()`
- **THEN** rendering stops, the container is empty, and no later frame or
  resize callback runs

#### Scenario: A host remounts and keeps the maker's viewpoint

- **WHEN** a host captures `view()`, disposes, and supplies that view to a new
  mount
- **THEN** the new viewer uses the captured camera and orbit target rather
  than fitting again

#### Scenario: A host refreshes a changed model in place

- **WHEN** a source document changes and the host calls `reload()`
- **THEN** the new tree renders while camera position and orbit target remain
  unchanged

#### Scenario: Loading the core mounts nothing

- **WHEN** a host loads the core without calling `mount()`
- **THEN** no element is created, document fetched, or container modified

### Requirement: A host updates only what changed

The handle SHALL expose two targeted updates beside `reload()`.
`artifactChanged(path)` SHALL refetch the model file at that document-relative
path and replace the geometry of every node referencing it without adding or
removing nodes. `manifestChanged()` SHALL refetch the document and reconcile the
rendered tree in place, adding and removing nodes and applying changed operations
and colour. Both updates preserve the camera, orbit target, animation clock, and
every node the document still names.

#### Scenario: One artifact changes

- **WHEN** a host calls `artifactChanged()` with one model path
- **THEN** only that model is requested and replaced

#### Scenario: The model gains and loses parts

- **WHEN** a document adds one node and removes another, and the host calls
  `manifestChanged()`
- **THEN** the added node is rendered, the removed node and its resources are
  gone, and common nodes keep their meshes

#### Scenario: A placement edit costs no fetch

- **WHEN** a document changes only operations or colour
- **THEN** `manifestChanged()` updates the render without requesting a model

### Requirement: Geometry is refetched only when its identity changes

The viewer SHALL treat geometry as current only while both its model path and
`mtime` match the values it loaded, and SHALL refetch when either differs. A
node whose geometry `artifactChanged()` has just fetched SHALL count as current
for the `manifestChanged()` that immediately follows, even though the document
it fetches names a new `mtime` for that node, because the two calls loaded the
same bytes moments apart.

#### Scenario: A parameter change moves the model path

- **WHEN** a node's model path changes with an unchanged `mtime`
- **THEN** its geometry is refetched

#### Scenario: A source edit moves the mtime

- **WHEN** a node's `mtime` changes with an unchanged model path
- **THEN** its geometry is refetched

#### Scenario: A manifest update follows the artifact update it describes

- **WHEN** `manifestChanged()` names a new `mtime` for a node whose geometry
  `artifactChanged()` already replaced
- **THEN** `manifestChanged()` does not refetch that node's geometry

#### Scenario: A marking's artwork is edited

- **WHEN** a document update names a new `mtime` for one of a node's markings
  while the node's own model path and `mtime` are unchanged
- **THEN** that marking's geometry is refetched and the node's own geometry is
  not

#### Scenario: A part is rebuilt and its markings are not

- **WHEN** a document update names a new model path for a node while every one
  of its markings keeps the model path and `mtime` it was loaded with
- **THEN** the node's geometry is refetched and no marking's geometry is

#### Scenario: A marking is removed from a part

- **WHEN** a document update no longer lists a marking a node was carrying
- **THEN** that marking is no longer drawn, the node's remaining markings and
  its own geometry are undisturbed, and no geometry is refetched for them

#### Scenario: A marking artifact is updated on its own

- **WHEN** a host reports that a marking's artifact changed, naming that
  artifact's path
- **THEN** that marking's geometry is refetched and redrawn, no other geometry
  is refetched, and the document update that follows — naming the new `mtime`
  for bytes already on screen — does not refetch it again

### Requirement: A failed update leaves the model standing

A targeted update that cannot fetch what it needs SHALL report the failure while
leaving the rendered model and camera in place; the handle remains usable for a
later update. The viewer SHALL fetch replacements before it removes any node.

#### Scenario: An artifact fetch fails

- **WHEN** `artifactChanged()` cannot fetch its model file
- **THEN** the previous model remains displayed and a later update can succeed

#### Scenario: A document fetch fails

- **WHEN** `manifestChanged()` cannot fetch or parse the document
- **THEN** the rendered tree is unchanged

### Requirement: One loader reads either published document

The viewer SHALL render either portable `manifest.json` or normal-build
`viewer.json`, reading their shared fields. It SHALL render document
versions 1, 2, 3, 4, 5, 6 and 7, and SHALL refuse any other version naming
it and the versions it renders. A document whose `drivers`
table is empty SHALL render exactly as a version 1 document. A document
whose `drivers` table is non-empty SHALL load and render at the pose its
expressions evaluate to under the table's declared defaults, with driver
and instruction entries exposed through the handle's driving API. A
document whose expressions reference a qualified id absent from both its
`drivers` table and its `bindings` table is malformed and SHALL fail
loudly naming the id; under version 5 and above the identifiers an
expression may name also include the program's clock name, its bank coordinates, the
values it publishes as computed, and, inside a jump plan's own
expressions, that plan's branch placeholders. A version 4 document carries
an ordered `bindings` table, which the viewer SHALL resolve under the
binding requirements above; a document that carries no such table SHALL be
read exactly as it was before the viewer knew of bindings. A version 5
document additionally carries a `program` object, which the viewer SHALL
load and validate under the program requirements above, and whose bank
SHALL pose the tree. A version 6 document is a version 5 one whose
compiled program carries at least one law edge that reads the coordinate
it drives; it carries NO further key, its shape is otherwise identical,
and the viewer SHALL load, validate and execute it exactly as it does a
version 5 one. A version 6 document whose program carries no such edge
SHALL NOT be refused for that: the version is a property of the content
the producer published, and this viewer judges the content. A version 7
document is a version 6 one whose compiled program carries a cycle of
edges every one of whose in-cycle dependencies some selection switches;
it too carries NO further key and its shape is otherwise identical, and
the viewer SHALL load, validate and execute it under the requirement
"The worker orders a block per piece". A version 7 document whose program
carries no such cycle SHALL NOT be refused for that either, and SHALL
load, pose and run exactly as the same document declared at version 5 or
6 would. A version 5 document MAY also carry a `controls`
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

- **WHEN** a host mounts a document declaring version 8
- **THEN** mounting fails naming that version and the versions the viewer
  renders

#### Scenario: A document whose program reads a driven coordinate is rendered

- **WHEN** a host mounts a document declaring version 6, whose program
  carries a law edge naming one of its driven ends among the values it
  reads
- **THEN** it renders at the pose the program's published rest values
  evaluate to, its run is available on the handle, and nothing about the
  document's shape differs from a version 5 one

#### Scenario: A version 6 document with no such law is rendered too

- **WHEN** a host mounts a document declaring version 6 whose program
  carries no law edge reading a coordinate it drives
- **THEN** it loads, poses and runs exactly as the same document declared
  at version 5 would

#### Scenario: A document whose program carries a block is rendered

- **WHEN** a host mounts a document declaring version 7, whose program's
  edges carry a cycle over what they read and determine
- **THEN** it renders at the pose the program's published rest values
  evaluate to, its run is available on the handle, and nothing about the
  document's shape differs from a version 6 one

#### Scenario: A version 7 document with no such cycle is rendered too

- **WHEN** a host mounts a document declaring version 7 whose program's
  edges carry no cycle at all
- **THEN** it loads, poses and runs exactly as the same document declared
  at version 5 or 6 would

#### Scenario: Older documents are untouched

- **WHEN** a host mounts a document declaring version 1, 2, 3 or 4
- **THEN** it loads, poses, animates and drives exactly as it did before
  the viewer could read a program

### Requirement: The host chooses how animation is presented

For a model with `$t` operations, the viewer SHALL present animation as an
always-visible inline play/pause and `0..1` timeline with `frames` inclusive
scrub positions, the same bar behind an initially collapsed accessible toggle,
no controls, or externally driven time with no controls. When `frames > 1`,
both zero and one SHALL be reachable timeline values and adjacent positions
SHALL be separated by `1 / (frames - 1)`; a single frame SHALL expose only
zero. The host SHALL set initial time and
autoplay. Scrubbing pauses playback. Static models SHALL present no controls.

For a document whose `animation` object carries no `loop`, playback SHALL
cycle every `frames / fps` seconds, exactly as before, and the bar SHALL
carry no speed control and no time readout.

For a document whose `animation` object carries `loop` — the seconds of
machine time one turn of `$t` covers — playback SHALL cycle every
`loop / speed` wall-clock seconds, where `speed` is a positive multiplier
defaulting to 1 (real time). The bar SHALL carry a speed control offering
a fixed ladder of multipliers from slow motion to thousands of times real
time, and a readout of the machine time at the slider position: `h:mm:ss`
when the loop is an hour or longer, `m:ss.s` when it is a minute or longer,
and seconds with two decimals otherwise. The host MAY set the initial speed
through the `speed` mount option, and the handle SHALL expose `speed()` and
`setSpeed(value)`; a non-positive or non-finite speed SHALL be refused
naming the value, and a host-set speed outside the ladder SHALL still be
offered by the control. Speed SHALL survive a document republish and a
targeted update, as the animation clock does. For a document without
`loop`, `speed()` SHALL report 1 and `setSpeed` SHALL be accepted and have
no effect on playback.

#### Scenario: A shop floor hides the timeline until asked

- **WHEN** an animated model uses toggled presentation
- **THEN** the bar starts hidden behind a collapsed persistent toggle and the
  toggle reports its expanded state when activated

#### Scenario: A published export shows the bar

- **WHEN** an animated model uses inline presentation
- **THEN** play/pause and timeline are visible immediately

#### Scenario: A host drives time itself

- **WHEN** a host uses externally driven presentation and sets time
- **THEN** the viewer renders that pose with no controls

#### Scenario: A static model

- **WHEN** a model has no `$t` operation in any presentation mode
- **THEN** it creates no play/pause, timeline, or toggle

#### Scenario: A document without a loop plays as before

- **WHEN** a document declares `animation: {fps: 30, frames: 360}` and no
  `loop`
- **THEN** one turn takes twelve wall-clock seconds and the bar shows
  play/pause and the timeline only

#### Scenario: A twelve-hour loop plays at real time

- **WHEN** a document declares `animation.loop == 43200` and the host sets
  no speed
- **THEN** one turn of `$t` takes 43200 wall-clock seconds, the readout
  reads `0:00:00` at the start and `6:00:00` at the slider's midpoint, and
  the speed control shows ×1

#### Scenario: The complete loop is reachable

- **WHEN** that twelve-hour document has 360 frames and the maker scrubs the
  timeline to its final position
- **THEN** the slider value is exactly one and the readout says `12:00:00`

#### Scenario: The maker speeds the clock up

- **WHEN** the maker selects ×720 on the speed control of that document
- **THEN** one turn takes sixty wall-clock seconds and `speed()` reports 720

#### Scenario: The host sets the speed

- **WHEN** a host mounts that document with `speed: 60` and later calls
  `setSpeed(3600)`
- **THEN** playback starts at one turn per twelve minutes, and after the
  call one turn takes twelve seconds

#### Scenario: A short loop reads in seconds

- **WHEN** a document declares `animation.loop == 1.5`
- **THEN** the readout shows the machine time in seconds with two decimals

#### Scenario: A bad speed is refused

- **WHEN** a host calls `setSpeed(0)` or `setSpeed(-5)`
- **THEN** the call fails naming the value and the current speed is kept

### Requirement: The camera fits the model unless the host restores a view

The viewer SHALL orient Z-up and, after meshes load, fit the model bounds with
orbit controls targeting its centre. A supplied view SHALL set position and
target instead, while near and far clipping continue to derive from bounds. A
host MAY additionally supply an up direction and a field of view; absent
either, the viewer SHALL keep its own Z-up orientation and default field of
view, so a host that supplies neither sees no change.

#### Scenario: A first look at a model

- **WHEN** a model mounts without a view
- **THEN** the whole model is framed and orbiting targets its centre

#### Scenario: A rebuild during a work session

- **WHEN** a model mounts with a supplied view
- **THEN** the camera is restored and the model is neither clipped nor beyond
  the far plane

#### Scenario: A host reproduces another renderer's framing

- **WHEN** a host mounts with a view, an up direction, and a field of view
- **THEN** the model is seen from that viewpoint, rolled to that up direction,
  and framed at that field of view

#### Scenario: An existing host is unaffected

- **WHEN** a host mounts without an up direction or field of view
- **THEN** the viewer frames the model exactly as it did before those options
  existed

### Requirement: Colour is inherited and falls back to a normal material

The viewer SHALL use a node colour or its nearest ancestor colour, and SHALL
use the framework's normal-based material when no colour is available.

#### Scenario: A part inherits its assembly's colour

- **WHEN** a node has no colour and an ancestor does
- **THEN** the part renders in the ancestor's colour

#### Scenario: A colourless assembly

- **WHEN** no node declares a colour
- **THEN** every model renders with the normal-based material

#### Scenario: A marking keeps its own colour on a colourless part

- **WHEN** a node that inherits no colour carries a marking that declares one
- **THEN** the part renders with the normal-based material and the marking
  renders in its own declared colour, and no colour of the part's is applied
  to it

### Requirement: The host names the canvas for its own styles and assistive tools

The viewer SHALL apply a host-supplied CSS class, role, and accessible label to
the canvas. Absent a host choice, it SHALL add no such attributes.

#### Scenario: A shop floor labels the model view

- **WHEN** a host supplies a canvas class, role, and label
- **THEN** the canvas carries them for host styling and assistive tools

### Requirement: The viewer declares its API version

The package SHALL declare one API version, expose it on every mount handle and
the browser global, and make it readable without executing the bundle. It SHALL
be raised whenever the mount interface or handle changes incompatibly, and when
a capability a host may require is added. The declared version SHALL be 16,
reflecting the ordering of a block of the compiled program once per piece of a
step — the version 7 document a build at the previous version refuses by name —
on top of the execution of a law that reads the coordinate it drives, the
drawing of the markings a document's parts carry, part controls, the inspector
layout, the mountable assembly navigator, the published assembly-navigation
state and its change subscription.

The package SHALL also declare, in the same one place, the document schema
versions this build reads, and SHALL report them beside the API version
wherever the API version is reported. A consumer asking which documents a
viewer reads SHALL be answered with that list rather than having to infer
it from the API version, and a consumer that receives no such list SHALL be
entitled to assume the versions every released viewer reads. Reading a
document's controls table or a node's markings list SHALL NOT change that list:
both are additive within the document versions that carry them, and the API
version is the only capability gate either moves.

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

#### Scenario: A host requires a self-read program executed

- **WHEN** a host means to present a machine one of whose laws reads the
  coordinate it drives — a rack that turns a dial only while the dial is
  not already standing in its own gap — which the producer publishes as a
  version 6 document
- **THEN** the declared API version tells it whether this bundle executes
  one, before it mounts a bundle that would refuse the document by name
  and render nothing at all

#### Scenario: A host requires the markings drawn

- **WHEN** a host means to present a machine whose answer is printed on its
  parts — a calculator's digits, a dial's graduations — rather than a blank
  drum
- **THEN** the declared API version tells it whether this bundle draws a
  document's markings, before it mounts a bundle that would show the same
  document with nothing readable on it

### Requirement: A host reads and drives the document's drivers

The mounted viewer SHALL hold one driver state per mount, keyed by the
document's qualified driver ids and initialized from the `drivers`
table's declared defaults, in native driver units. The handle SHALL
expose `drivers()` (the table's entries verbatim: id, default, range,
unit, dtype, scale), `driver(id)` (the current native value),
`setDriver(id, value)` (bind and re-evaluate; an unknown id SHALL fail
loudly listing the known ids; declared `range` SHALL NOT clamp), and
`onDriverChange(fn)` (called once per changed driver per animation
frame while values change and synchronously on `setDriver`; returns an
unsubscribe function). A driver change SHALL re-evaluate only
operations whose expressions reference that driver's id; operations
referencing `$t` SHALL keep animating with the existing time
transport, including expressions referencing both.

#### Scenario: A slider-shaped call moves one carriage

- **WHEN** a host calls `setDriver('x_axis.motor', 8000)` on a mounted
  two-axis document
- **THEN** operations referencing `x_axis.motor` re-evaluate to the
  new pose that frame, operations referencing only `y_axis.motor` or
  only `$t` are not re-evaluated because of it, and
  `driver('x_axis.motor')` reports 8000

#### Scenario: Out-of-range values bind unclamped

- **WHEN** a host sets a driver past its declared range (a crash
  scenario drives past travel)
- **THEN** the value binds verbatim and the pose follows it

#### Scenario: An unknown id fails loudly

- **WHEN** a host calls `setDriver('z_axis.motor', 0)` on a document
  declaring only `x_axis.motor` and `y_axis.motor`
- **THEN** the call fails naming the unknown id and listing the
  declared ids, and no state changes

#### Scenario: A driver whose name shadows a word is not confused

- **WHEN** a document declares a driver named `total` and an operation
  expression calls a function whose name contains that word
- **THEN** only operations in which `total` is a free variable of the
  parsed expression re-evaluate when it changes — detection is by
  parsed free variables, never substring matching

### Requirement: A host triggers declared instructions

The handle SHALL expose `instructions()` (the document's instruction
entries verbatim: qualified name, design-unit targets keyed by
qualified driver id, duration) and `trigger(name)`. Triggering SHALL
convert each target to native units through the driver table's scale
and dtype exactly as the Python simulation does (nearest native unit
for integer dtypes) and ramp each target driver linearly from its
current value over the instruction's duration, advanced by the
viewer's animation loop on wall-clock elapsed time: intermediate
values are sampling, endpoints are contract — integer-dtype values
SHALL be whole at every frame and the final value SHALL be exactly the
converted target. Triggering an instruction whose target driver
already has an active ramp SHALL replace that ramp from the current
value. `trigger` SHALL return a handle with `done` (a promise
resolving when every target lands or the run is cancelled) and
`cancel()` (stop ramps at their current values). An unknown
instruction name SHALL fail loudly listing the known qualified names.
Disposing the viewer SHALL cancel active ramps.

#### Scenario: A button-shaped call homes one axis

- **WHEN** a host calls `trigger('x_axis.Home')` (target 0.0 mm over
  2.0 s, driver scale 0.0125 mm/µstep, dtype int)
- **THEN** `x_axis.motor` ramps from its current value to exactly 0
  native µsteps as the duration elapses, `y_axis.motor` holds, every
  intermediate value is a whole number, and `done` resolves at landing

#### Scenario: Re-triggering replaces the active ramp

- **WHEN** an instruction is triggered while a prior trigger on the
  same driver is mid-ramp
- **THEN** the new ramp starts from the driver's current value and the
  prior run's `done` resolves without landing on its old target

#### Scenario: An unknown instruction fails loudly

- **WHEN** a host triggers a name the document does not declare
- **THEN** the call fails listing the declared qualified instruction
  names and no driver changes

### Requirement: Client evaluation matches producer numerics

The viewer's expression evaluation — OpenSCAD degree trig, `^` as
exponentiation, `$t`, qualified identifiers resolved through the
value map at every segment of the identifier, and binding names resolved
through the document's table —
SHALL match the producer's numeric resolution of the
same expressions to within floating-point rounding, and that agreement
SHALL be enforced by tests against the shipped evaluator module using
producer-computed expected values covering at least: linear and scaled
driver terms, degree-trig chains, `^` terms, sums whose leading term is
negative, expressions mixing `$t` with drivers, expressions that are or
contain a binding name, and design-to-native
instruction target conversion for integer dtypes.

`sign` SHALL resolve as the producer's own definition does — which side of
zero its argument is on — including at negative zero, where a runtime's
own sign function does not.

The producer-generated corpus SHALL carry the bindings table its cases
reference, and the tests SHALL resolve a case's expression through that
table exactly as the viewer resolves a document's, so the corpus pins the
table's semantics as well as the functions': an entry naming an earlier
entry, an entry over a driver id as well as over `$t`, and an entry
reached from more than one case. A case pinned by an earlier corpus SHALL
keep its key and its expected value.

Agreement SHALL include operator precedence and not only arithmetic. A
unary minus SHALL bind to the term beside it rather than to the rest of
the expression, so a sum whose leading term is negative resolves to that
negative term plus the rest and never to the negation of the whole; and
`^` SHALL bind tighter than a unary minus, as the producer's own
language does.

Agreement SHALL also include the form of the numbers themselves. The
client SHALL read every numeric literal the producer can write, in
particular a literal in exponent notation — which the producer emits
for any magnitude its language prints that way — and SHALL resolve it to
the value those digits name, at any magnitude and without loss from a
floating-point round-trip. A name that merely begins with or contains
the exponent marker SHALL remain a name.

Agreement SHALL hold however evaluation is organized. Sharing a
subexpression between the places that read it, reusing a value already
resolved for the same inputs, and reading a subexpression through a name
the producer published it under, SHALL NOT move a number: a shared
reading, a bound reading and a reading that walked every occurrence
separately SHALL agree exactly, and a
value that is not a number — an unresolved name, or a term that produced no
number — SHALL reach the caller as it does today rather than as a stale or
substituted one.

An expression form the viewer's evaluation cannot support SHALL be refused
when the document is loaded — with the refusals for an unreadable document
version, an unknown flexible technology, an unresolvable bindings table
and an undeclared driver id — naming
the form and quoting the expression, and quoting it in part rather than
whole, since a published expression may be megabytes long. The refusal
SHALL cover every expression the document carries, an operation's, a
flexible node's parameters, a binding's and a program's alike, so that no
such expression is first met while a frame is being rendered or a step
integrated.

#### Scenario: The parity corpus pins the shipped evaluator

- **WHEN** the widget test suite runs the producer-generated parity
  fixture against the shipped evaluator
- **THEN** every expression's client value matches the producer value
  within float rounding, and removing the `^` rewrite makes the suite
  fail

#### Scenario: The corpus pins the bindings table

- **WHEN** the suite runs a corpus whose cases name entries of its
  bindings table, including a case whose whole expression is one name
- **THEN** each value matches the producer value within float rounding,
  and running the same cases without the table installed fails

#### Scenario: A sum whose leading term is negative crosses the boundary

- **WHEN** the corpus carries an expression whose head is a negative
  literal, evaluated at more than one driver setting
- **THEN** the client value matches the producer value at every one of
  them, and a reader that bound the unary minus to the whole sum instead
  would agree at no more than one

#### Scenario: A driver scaled by an exponent-printed factor

- **WHEN** the corpus carries a driver term whose scale is small enough
  that the producer prints it in exponent notation, together with a bare
  tiny literal and a bare large one
- **THEN** the client resolves each to the producer's value, and a reader
  that could not read an exponent literal would fail to parse them at all

#### Scenario: An identifier is not a literal

- **WHEN** an expression names a driver whose id begins with the exponent
  marker, or calls a function whose name contains it
- **THEN** the evaluator reads it as that name and resolves it through
  the driver map or the math context, unchanged

#### Scenario: A shared reading is the same reading

- **WHEN** every expression of the parity corpus is evaluated through the
  sharing evaluation, one input set at a time
- **THEN** each value matches the producer value within float rounding,
  including the degree-trig chains, the `^` terms and the leading negative
  sums

#### Scenario: An unresolved name is still not a number

- **WHEN** an expression names a driver the document does not declare, or
  reaches through one whose value is not a map, and it is evaluated twice
  for the same inputs
- **THEN** both readings produce exactly what the viewer produces today for
  that expression — the same non-number, or the same failure — and neither
  substitutes another node's value

#### Scenario: An unsupported form is refused at load

- **WHEN** a document is loaded whose operation expression, whose flexible
  node's parameter expression, or whose bindings entry carries a form the
  viewer's evaluation does not support, such as an inline function
- **THEN** loading fails naming the form and quoting part of the
  expression, no tree is built for it, a model already standing is left
  standing, and no frame is ever rendered from it

#### Scenario: An identifier of any depth resolves to its value

- **WHEN** an expression names an identifier of three or more segments and
  the viewer holds a value under exactly that identifier
- **THEN** it resolves to that value, as a one- or two-segment identifier
  already does

#### Scenario: The sign of negative zero is the producer's

- **WHEN** an expression applies `sign` to a value that is negative zero
- **THEN** it resolves to what the producer resolves it to

### Requirement: A maker drives the focused layer's drivers and instructions on screen

For a document that declares drivers and carries no program, the mounted
viewer SHALL present
an on-screen control for each driver and each instruction declared at
the focused assembly layer: a button per instruction and a bounded
slider with a passive numeric readout per driver. Clicking or
keyboard-activating that readout SHALL replace it temporarily with a text
editor that carries no native numeric spinner arrows. Control labels SHALL be
the declared identifiers relative to the focused layer. Sliders, passive
readouts, and active editors SHALL present values in design units with the
declared unit, and SHALL move live while a ramp plays except while the maker is
actively editing that readout. Enter or focus loss SHALL commit a non-empty
finite numeric entry; Escape or an invalid entry SHALL leave the driver
unchanged and restore the passive readout. A committed finite numeric entry
SHALL produce the same driver state as dragging the slider to that design-unit
value, including an entry outside the slider's declared range. A driver's
passive readout SHALL show a fixed number of decimal places and SHALL retain
the viewer's prior fixed-width, right-aligned, tabular-number appearance. It
SHALL hold the position of its digits, its sign, and everything laid out beside
it steady as the value changes: reading a value while dragging SHALL not
require following a moving target.
Interacting with a control SHALL produce the
same observable state as the corresponding host driving call, so a
value or trigger set on screen and one set through the handle are
indistinguishable to expressions, listeners, and readbacks. The
declared `range` SHALL bound only the slider's travel, never the
underlying value: a value bound past the range through the host API or numeric
entry SHALL survive intact, with the slider pinned at its end and the
numeric readout showing the true value. Every control SHALL carry an
accessible name for assistive tools. A document declaring no drivers
SHALL present none of this chrome.

A document that carries a program SHALL present none of this chrome
either: its inputs are entry points for movement requests rather than
positions to set, and it is driven by the running controls specified
below.

#### Scenario: A maker homes an axis with a button

- **WHEN** the focused layer declares the instruction `Home` and the
  maker presses the button labelled `Home`
- **THEN** the same ramp plays as a host `trigger` of that qualified
  instruction, the affected driver's slider travels with it to the
  target, and the button indicates the run until it lands

#### Scenario: A maker jogs a motor with a slider

- **WHEN** the maker drags the slider labelled `motor` on a focused
  axis whose driver declares `unit: ustep` and a millimetre scale
- **THEN** the model pose follows the drag, the readout shows the
  design-unit value with its unit, and `driver()` on the handle
  reports the corresponding native value

#### Scenario: A maker enters an exact calibration value

- **WHEN** the maker activates a bounded driver's passive numeric readout,
  enters a finite design-unit number and commits the edit
- **THEN** the model uses that exact value through the same conversion as its
  slider, the slider follows or pins at its nearest endpoint, the unit remains
  visible, and the passive readout returns without persistent field chrome or
  spinner arrows

#### Scenario: A readout holds still through a drag

- **WHEN** the maker drags a driver's slider through values of
  differing digit counts and across zero into negative travel
- **THEN** every passive value is written with the same number of decimal
  places, and neither the change of digit count nor the appearance of
  the minus sign moves the readout's digits or the unit beside them

#### Scenario: A re-pressed button replaces the run

- **WHEN** the maker presses an instruction's button while its ramp is
  still playing
- **THEN** the new run replaces the old one, exactly as a host
  re-trigger does

#### Scenario: An out-of-range value is shown honestly

- **WHEN** a host or maker binds a driver past its declared range and the
  maker looks at that driver's control
- **THEN** the slider sits pinned at its nearest end, the passive readout
  shows the actual out-of-range value, and the bound value is
  unchanged by the chrome

#### Scenario: A driverless document is unchanged

- **WHEN** a document with an empty drivers table is mounted
- **THEN** no driver control, readout, or focus affordance appears and
  the widget presents exactly its pre-existing chrome

#### Scenario: A running document gets the other chrome

- **WHEN** a document carrying a program is mounted with the chrome
  presented
- **THEN** no position slider appears for any of its inputs, and the
  running controls appear in its place

### Requirement: Controls follow the focused layer

The viewer SHALL scope driver controls strictly to the focused
assembly layer. With focus at the document root, only drivers and
instructions declared with bare (root-level) identifiers SHALL be
presented. Focusing an instance SHALL replace the controls with those
the instance itself declares, labelled relative to it; controls of its
descendants and of other branches SHALL NOT be presented. When a
document update removes the focused node and focus resets, the
controls SHALL re-scope with it. A focused layer declaring nothing
SHALL present no sliders or buttons while the focus affordance remains
available.

#### Scenario: Focusing an axis reveals its controls

- **WHEN** the maker focuses `x_axis` on a machine whose axes each
  declare a `motor` driver and a `Home` instruction
- **THEN** exactly one slider labelled `motor` and one button labelled
  `Home` appear, driving `x_axis.motor` and `x_axis.Home`, and
  `y_axis`'s controls are not shown

#### Scenario: A root that declares nothing shows no controls

- **WHEN** the maker views the root of a machine that declares all
  drivers and instructions on its children
- **THEN** no slider or button is presented at the root and the focus
  affordance still offers the declaring children

#### Scenario: A republish that removes the focused node re-scopes

- **WHEN** a document update removes the focused instance and the
  viewer resets focus to the root
- **THEN** the presented controls become the root layer's

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

### Requirement: A maker drives a running machine by requesting movement

For a document carrying a program, the mounted viewer SHALL present, for
each declared input and each declared instruction of the focused assembly
layer, controls that SUBMIT MOVEMENT REQUESTS to the run. It SHALL NOT
present a control that writes a position into a coordinate: under a run a
coordinate carries history, and a control that sets one would undo the
movement the run recorded.

Per declared input of the focused layer:

- a **readout** of that input's actual committed position, in design units
  with its declared unit, which follows the run and is never editable and
  never a source of a request;
- a **nudge** in each direction, issuing a request to move that input by a
  stated amount over a stated duration;
- a **hold-to-jog** in each direction, issuing a request for a continuous
  rate on press and cancelling that request on release, on lost pointer
  capture, on lost window focus, and when the page stops being displayed;
- an **amount** and a **rate** a maker may change, which configure the
  requests those controls will make and SHALL NOT move anything by
  themselves.

Per declared instruction of the focused layer, a **button** that submits
that named instruction to the run, whichever form it is declared in — a
movement to a value or a movement by a travel — and indicates that it is
running until its commands retire.

Control labels SHALL be the declared identifiers relative to the focused
layer, and the controls SHALL follow the focused layer exactly as the
posed chrome's do. Every control SHALL carry an accessible name.
Interacting with a control SHALL produce the same observable run state as
the corresponding host call, so a request made on screen and one made
through the handle are indistinguishable to the run, to listeners and to
readbacks. A request issued while the run is paused SHALL start it. A
document carrying a program SHALL NOT present a position slider or an
animation timeline.

#### Scenario: Repeated entry accumulates

- **WHEN** a maker presses an instruction's button ten times on a machine
  whose law carries a jump, letting each run complete
- **THEN** the driven coordinate stands where ten movements left it, not
  where one would have, and the readout of the input reads ten units

#### Scenario: A readout does not drive

- **WHEN** a maker looks at an input's readout while the run moves it
- **THEN** the readout follows the committed position, and there is no
  way to type or drag a position into it

#### Scenario: A jog ends when the interaction does

- **WHEN** a maker presses a jog control and then releases it, drags the
  pointer away until capture is lost, moves focus out of the window, or
  leaves the page
- **THEN** the rate request is cancelled in every one of those cases and
  the machine stops where it stands

#### Scenario: An amount configures the next request

- **WHEN** a maker changes a nudge amount or a jog rate
- **THEN** nothing moves, and the next nudge or jog asks for the new
  amount or rate

#### Scenario: A relative instruction is a button like any other

- **WHEN** a document declares an instruction as a travel rather than a
  target
- **THEN** it has a button, pressing it submits that travel to the run,
  and the button indicates the run until it retires

#### Scenario: A posed document is untouched

- **WHEN** a document that carries no program is mounted
- **THEN** it presents exactly the sliders, readouts, instruction buttons
  and animation bar it presented before the viewer could run a machine

### Requirement: A maker runs, steps and resets the machine

For a document carrying a program, the mounted viewer SHALL present a
transport: run and pause; a step that advances exactly one step of the
run; a speed over the same ladder of real-time multiples the viewer
already offers; a readout of the elapsed simulation time; and a reset to
the run's initial state.

The elapsed readout SHALL show simulation seconds, which never wrap, in a
form whose width does not change as the digits change, and SHALL widen
rather than narrow as the run grows. Speed SHALL change how fast the
machine is watched and never how finely it is simulated. Step SHALL
advance the run whether it is paused or running, so a maker can walk a
jump or a stop one step at a time. Reset SHALL return the bank, the step
count and the elapsed time to the state the document was mounted at, and
the readouts SHALL follow it.

#### Scenario: A maker walks a carry one step at a time

- **WHEN** a maker pauses the run and presses step repeatedly through the
  window in which a law's jump surface is crossed
- **THEN** each press advances exactly one step, and the geometry follows
  each committed step

#### Scenario: Watching faster is not simulating coarser

- **WHEN** a maker selects a large speed multiple and lets the same
  request run
- **THEN** the machine reaches the same state it reaches at real time,
  sooner

#### Scenario: Reset returns the machine

- **WHEN** a maker resets after driving the machine
- **THEN** every coordinate stands where it stood when the document was
  mounted, the step count and the elapsed time are back at zero, and no
  command is active

#### Scenario: There is no scrubber

- **WHEN** a maker looks for a way to drag the run to an instant
- **THEN** there is none: a running document presents no timeline, and
  the transport offers only run, pause, step, speed and reset

### Requirement: A request reports its outcome where it was made

Every request a maker issues SHALL report its outcome at the control that
issued it: completed; blocked, with the travel the machine actually
admitted in the units the request was stated in; refused, with the run's
own reason; or cancelled. A blocked request SHALL NOT leave any remainder
to be executed later.

A step the run refuses SHALL be reported across the panel rather than at
one control, carrying the run's own message — which names the relation as
its author wrote it and the class that stated it — and the run SHALL
pause on it rather than repeating the refused step. The report SHALL
clear when the run next commits a step.

A request on an input another command already owns SHALL be reported in
place rather than silently dropped, so a manual control never appears to
have taken over an input it did not.

#### Scenario: A blocked nudge says how far it got

- **WHEN** a maker nudges an input whose coordinate meets a declared stop
  part way
- **THEN** the control reports the request blocked and the travel
  admitted, and pressing nudge again asks for a fresh movement rather
  than resuming the blocked one

#### Scenario: A refused step names what disagreed

- **WHEN** a step is refused because two relations disagree on one
  coordinate
- **THEN** the panel shows the run's message naming both relations and the
  coordinate, the machine stands where it stood, and the run is paused

#### Scenario: A second request on a busy input is answered

- **WHEN** a maker jogs an input while an instruction already owns it
- **THEN** the jog reports that the input is owned, and the instruction's
  movement is untouched

### Requirement: The viewer evaluates flexible geometry per frame

The package SHALL bundle the molejo JavaScript evaluator and render a
document's `flexible` nodes: each node's `params` expressions are
evaluated in the same scope as operation expressions (`$t` and the
nested driver map), and the resulting values are handed to the molejo
evaluator, which writes vertex data into buffers the viewer allocates
once per node and reuses — vertex count and ordering are declared by
the spec and never change at frame rate, so no reallocation occurs.

Re-evaluation SHALL be bounded the way operation re-evaluation already
is: a flexible node's geometry is recomputed only on frames where a
free variable of one of its `params` expressions changed, and driving
a driver named by no `params` expression SHALL NOT re-evaluate it.

The loader SHALL accept documents declaring `version: 2` or
`version: 3`, and SHALL refuse — naming the node and the technology —
a `flexible` node whose `tech` the package cannot evaluate, rather
than rendering a wrong or missing shape.

The binding seam SHALL be pinned by the producer-generated parity
fixture: at least one case evaluates a real flexible document's
parameter expression client-side, feeds it to the bundled molejo
evaluator, and matches the producer's Python-side evaluation of the
same spec and binding within the fixture's tolerance. (Vertex-level
agreement between the two molejo evaluators is molejo's own parity
contract; what this package pins is the expression-to-parameter
binding in front of it.)

#### Scenario: A spring animates in the browser

- **WHEN** a document containing a molejo spring whose `height`
  expression references a declared driver is mounted and that driver
  is driven
- **THEN** the spring's geometry re-evaluates into its existing
  buffers on the frames where the driver changed, with vertex count
  unchanged

#### Scenario: An unrelated driver does not touch the spring

- **WHEN** a driver named by no `params` expression of the spring
  changes
- **THEN** the spring's geometry is not re-evaluated that frame

#### Scenario: An unknown technology is refused loudly

- **WHEN** a document carries a `flexible` node whose `tech` the
  package cannot evaluate
- **THEN** loading fails naming the node and the technology, and no
  wrong shape is rendered

#### Scenario: The binding parity case pins the seam

- **WHEN** the widget test suite runs the parity fixture's flexible
  binding case against the shipped evaluator and bundled molejo
- **THEN** the client-side parameter value and resulting evaluation
  agree with the producer-computed expectation within the declared
  tolerance

### Requirement: A flexible spec the evaluator cannot read is refused by name

The package SHALL refuse a `flexible` node whose spec the bundled
evaluator cannot read, naming the node and carrying the evaluator's own
reason, rather than rendering a wrong or missing shape. The refusal SHALL
happen when the node is constructed — the same point at which an
unevaluable `tech` is already refused — so that an unreadable document
fails at load with a message that identifies it, and never as an
exception escaping the render loop on some later frame.

The package SHALL NOT interpret the spec to decide this. It asks the
bundled evaluator whether the spec is readable and reports what the
evaluator says, so the document stays opaque to the viewer and the set of
readable specs remains the evaluator's to define.

#### Scenario: A spec the bundled evaluator cannot read is refused at load

- **WHEN** a document carries a `flexible` node whose `tech` the package
  evaluates, but whose spec the bundled evaluator rejects — for instance
  one written for an older evaluator, declaring a spec version that
  evaluator no longer reads
- **THEN** construction fails naming the node and including the
  evaluator's reason, no geometry is created for it, and no exception is
  raised from a later frame

#### Scenario: A readable spec is unaffected

- **WHEN** a document carries a `flexible` node whose spec the bundled
  evaluator reads
- **THEN** the node is constructed and evaluated exactly as before, with
  no additional per-frame work

### Requirement: A repeated subexpression is evaluated once per pass

A published expression may paste the same subexpression many times over —
the producer builds an expression by string concatenation, so a reused value
arrives as its full text again — and one such expression may appear under
many operations of one document. Evaluating the document's expressions for
one set of inputs SHALL cost the number of DISTINCT subexpressions they
contain rather than the length of their text: a subexpression that occurs
more than once in an expression, or in more than one expression, SHALL be
resolved once for that set of inputs, whichever operation, flexible
parameter or caller asks for it.

The widget SHALL expose, to its own tests, the number of subexpression
resolutions performed and the number of distinct subexpressions prepared, so
the bound is asserted as work performed and never as elapsed time. This is
not a host capability: it SHALL NOT appear on the mount handle, and the
viewer API version SHALL NOT rise for it.

Preparing an expression SHALL NOT retain its parsed form: what the viewer
keeps for a document is its distinct subexpressions, and what it keeps after
its last viewer is disposed of is nothing.

Re-evaluation SHALL stay bounded as it already is — an operation is
re-evaluated only when `$t` or one of its own free variables changed, and a
free variable is still read from the parsed expression, with a dotted driver
id one name and a called function's name never a variable.

#### Scenario: A pasted subexpression costs one resolution

- **WHEN** an expression is built by pasting a subexpression into itself
  repeatedly, so that its text holds thousands of nodes over a few dozen
  distinct ones, and it is evaluated for one set of inputs
- **THEN** its value is the value a reader that walked every pasted node
  would return, and the resolutions performed are of the order of the
  distinct subexpressions, not of the pasted text

#### Scenario: One expression under many operations

- **WHEN** several operations of one document carry the same expression and
  the document is evaluated for one set of inputs
- **THEN** the operations after the first perform no further resolutions,
  and every operation's matrix is the one its expressions name

#### Scenario: New inputs are evaluated afresh

- **WHEN** the animation time advances and the same operations are
  evaluated again
- **THEN** their distinct subexpressions are resolved again for the new
  time, and the values follow the new time

#### Scenario: A driver nobody names still costs nothing

- **WHEN** a driver is set on a document whose operations do not name it
- **THEN** no operation of that document is re-evaluated because of it

#### Scenario: The parse is not kept

- **WHEN** a document's expressions have been prepared and evaluated
- **THEN** the viewer's retained expression state is of the order of the
  document's distinct subexpressions, and disposing of the last viewer on
  the page leaves none of it

### Requirement: A named binding is resolved where it is used

A published document may carry an ordered `bindings` table: named
expressions, published once and referenced by bare name from an
operation's expression, from a flexible leaf's `params`, and from later
entries of the table. The viewer SHALL resolve such a name, wherever it
occurs, to the value of that entry's expression under the same inputs —
the same animation time and the same driver values — as the expression
that named it.

A name SHALL be resolved as a binding BEFORE it is treated as a driver
id, and after `$t`. A binding name SHALL therefore never be reported as
an undeclared driver id.

An entry SHALL be evaluated only when something reads it, and SHALL cost
one resolution per evaluation pass however many operations, parameters or
other entries reach it — the bound the viewer already holds for a
repeated subexpression. Reading a document's expressions through its table
SHALL NOT move a number: an expression that names an entry SHALL resolve
to what the same expression resolves to with that entry's text written out
in its place.

The table SHALL belong to the document that carries it. Two documents
mounted on one page MAY use the same name for different expressions, and
neither SHALL ever resolve a name to the other's value.

A document that carries no table SHALL render exactly as it does when the
viewer knows nothing of bindings.

#### Scenario: A bound document poses as the flat one it was published from

- **WHEN** two documents describing one machine are mounted — one whose
  operations reference a bindings table, one with every reference written
  out in full — at the same animation time and driver values
- **THEN** every operation's matrix is the same in both

#### Scenario: A binding read by many operations costs one resolution

- **WHEN** several operations of one document name the same entry and the
  document is evaluated for one set of inputs
- **THEN** the operations after the first perform no further subexpression
  resolutions, and every operation's matrix is the one its expressions name

#### Scenario: An entry nobody reads costs nothing

- **WHEN** a driver is moved on a document whose table holds entries no
  operation naming that driver reaches
- **THEN** those entries are not evaluated

#### Scenario: Two documents on one page keep their own names

- **WHEN** two documents are mounted on one page, each declaring an entry
  under the same name but with a different expression, and both are
  evaluated at the same animation time and driver values
- **THEN** each renders at the pose its own entry names, and neither reads
  the other's value

#### Scenario: A binding name is not an undeclared driver

- **WHEN** a document declaring an empty `drivers` table carries bindings
  and its operations name them
- **THEN** it loads and renders, because every name its expressions carry
  is `$t`, an entry of its table, or a function of the expression language

### Requirement: Dependence flows through a binding

Where the viewer bounds work by the inputs an expression reads — deciding
whether an operation is re-evaluated, whether a flexible leaf's geometry
is recomputed, and whether a document has a timeline to play — an
expression that names a binding SHALL be treated as reading every input
that binding transitively reads, through as many entries as the chain
runs.

An operation whose whole expression is a binding name resolving through
the table to `$t` SHALL therefore be a time-dependent operation: it SHALL
be re-evaluated when the animation time changes and it SHALL make its
document animated, exactly as it was when its expression was written out
in full. An operation reaching a declared driver id through a binding
SHALL be re-evaluated when that driver moves, and SHALL NOT be
re-evaluated when a driver nothing it reaches names moves.

What an expression reads SHALL follow the table it is read through. When a
document is republished with a table whose entries read different inputs,
the viewer SHALL answer with the new table's inputs even where the
expressions naming those entries are unchanged — so a machine that becomes
time-driven on a republish gains its timeline, one that stops being
time-driven loses it, and each is bounded by what it now reads.

#### Scenario: A document animated only through its table has a timeline

- **WHEN** a document is mounted in which no operation's expression
  mentions `$t`, and every operation that moves does so by naming an entry
  that resolves through the table to `$t`
- **THEN** the viewer presents the animation controls, and advancing the
  time moves those operations

#### Scenario: A driver reached through a binding moves the operation

- **WHEN** an entry's expression names a declared driver id, an operation
  names that entry, and the driver is set
- **THEN** that operation is re-evaluated and the model moves to the pose
  the new value names

#### Scenario: A driver reached by nothing still costs nothing

- **WHEN** a driver is set on a document whose operations, and the entries
  they reach, do not name it
- **THEN** no operation of that document is re-evaluated because of it

#### Scenario: A republished table changes what an unchanged expression reads

- **WHEN** a mounted document is republished with its operations unchanged
  — an operation whose whole expression is one entry name — and that
  entry's expression changed from one over `$t` to one over a declared
  driver id
- **THEN** the operation moves when that driver is set and no longer moves
  when the animation time advances, and the document is no longer animated

#### Scenario: A chain of entries carries dependence to its end

- **WHEN** an operation names an entry that names a second entry that
  names `$t`
- **THEN** the operation is re-evaluated when the animation time changes

### Requirement: A bindings table the viewer cannot resolve is refused by name

A bindings table decides where a machine's parts stand, so a table the
viewer cannot resolve SHALL be refused when the document is loaded —
beside the refusals for an unreadable document version, a flexible
technology or spec it cannot evaluate, an unsupported expression form and
an undeclared driver id — rather than rendering part of a machine from it.
The refusal SHALL name the entry or the name at fault, no tree SHALL be
built from the document, and a model already standing SHALL be left
standing.

The viewer SHALL refuse: a `bindings` value that is not an array of
entries carrying a name and an expression; two entries sharing a name; an
entry whose expression names itself or an entry later in the array; an
entry whose name is also a declared driver id; and a name reached from any
operation, any flexible parameter or any entry that is neither `$t`, nor
an entry of the table, nor a declared driver id — the refusal the viewer
already makes for an undeclared driver id, made after the table's names
are known and naming the name as absent from both tables. An entry whose
expression the viewer cannot read SHALL be refused as such an expression
already is.

The viewer SHALL read a `bindings` table whenever the document carries
one, and SHALL NOT refuse a document for declaring a version whose content
it does not use.

#### Scenario: A dangling reference is refused

- **WHEN** a document is loaded whose operation names an entry its table
  does not carry
- **THEN** loading fails naming that name, no tree is built, and a model
  already standing is left standing

#### Scenario: A table that names forward is refused

- **WHEN** a document is loaded whose entry names an entry appearing later
  in the array, or names itself
- **THEN** loading fails naming that entry

#### Scenario: Two entries under one name are refused

- **WHEN** a document is loaded whose table carries two entries with the
  same name
- **THEN** loading fails naming that name

#### Scenario: An entry named like a declared driver is refused

- **WHEN** a document is loaded whose entry's name is also a key of its
  `drivers` table
- **THEN** loading fails naming that name rather than resolving one of the
  two and leaving the other unreachable

#### Scenario: A malformed table is refused

- **WHEN** a document is loaded whose `bindings` value is not an array, or
  whose entry carries no name or no expression
- **THEN** loading fails naming the offending entry

#### Scenario: An undeclared driver is still refused

- **WHEN** a document carrying a table is loaded, and one of its
  expressions names an id that is neither an entry of the table nor a key
  of its `drivers` table
- **THEN** loading fails naming that id, as it does for a document with no
  table at all

### Requirement: The viewer executes a document's published program

A document may carry a compiled mechanical program: the bank of
coordinates in the order the program propagates them, with the value the
rest pose gave each one; the values the program computes and never stores;
the edges in propagation order with their expressions, their affinity and
their jump plans; the declared bounds; the inputs that reach each value;
the constants the algorithm is defined by; and the free name elapsed
simulation seconds bind to. The viewer SHALL execute that program: on
every step it admits the movement the active commands ask for, propagates
it over the edges, and commits one bank — the machine running, rather than
a pose evaluated.

The run SHALL be executed off the rendering thread. Rendering SHALL NOT
advance it: a dropped display frame SHALL drop display and never a step,
and the mechanism SHALL never be advanced by more steps than elapsed time
has earned. A page that is not being displayed SHALL accumulate no
unseen steps and SHALL resume from where it stands. A host environment
that cannot run the engine off the rendering thread SHALL run the same
engine on it and SHALL say so on the handle, rather than failing to open
the machine.

The step size SHALL be the viewer's own choice — the document publishes
none — SHALL default to a value fine enough to resolve the mechanisms the
producer publishes, and SHALL be settable once when the viewer is mounted.
It SHALL NOT change afterwards, because a run state is only valid at the
step size it was taken at. A non-finite or non-positive step size SHALL
be refused naming the value.

Playback speed SHALL keep its existing meaning — a multiple of real time —
and SHALL change how many steps are taken per second of wall time, never
the step size, so that watching a machine faster does not simulate it more
coarsely.

A run SHALL NOT begin advancing merely because a document was mounted: it
SHALL be created at the program's published rest values, stopped, and
SHALL begin when a host or a control asks it to — so a page that is only
being looked at, a still capture or a thumbnail, shows the rest state
without knowing that a run exists. A host MAY ask at mount time for a run
that begins at once.

The handle SHALL expose the run for a document that carries a program and
SHALL report its absence for one that does not. A host SHALL be able to
read the identity of the program, the step size, the step count, the
elapsed simulation seconds, the committed bank and each coordinate's kind,
unit and domain; to start, pause and advance an exact number of steps; to
request a movement of a declared input by a travel or to a value over a
duration, a continuous rate, a declared instruction, and the cancellation
of any of them; to take, restore and reset a run state; and to be told of
every committed step and every command outcome.

#### Scenario: A machine runs where a pose could not

- **WHEN** a host mounts a document carrying a program, asks for a
  declared instruction that advances an input by one unit, and lets the
  run advance until the command retires, ten times over
- **THEN** the coordinate the program's law drives stands where ten
  separate movements left it, not where one would have

#### Scenario: Display and mechanics are separate

- **WHEN** rendering falls behind while a command is running
- **THEN** no step is skipped, the committed bank a later frame draws is
  the one the run reached, and the elapsed simulation time reports the
  steps actually taken

#### Scenario: A page nobody is watching holds still

- **WHEN** the page carrying a running document stops being displayed and
  is displayed again later
- **THEN** the machine stands where it stood, no steps were taken while it
  was hidden, and the elapsed simulation time did not advance

#### Scenario: The step size is fixed for the life of a mount

- **WHEN** a host mounts with a chosen step size
- **THEN** the run uses it, the handle reports it, and there is no
  operation that changes it on a live run

#### Scenario: Watching faster is not simulating coarser

- **WHEN** the same document is run at real time and at a large multiple
  of it, each for the same number of steps
- **THEN** both reach the same bank, step for step

#### Scenario: A document only being looked at shows its rest state

- **WHEN** a document carrying a program is mounted by a host that asks
  for nothing
- **THEN** no step is taken, the elapsed simulation time stays at zero,
  and the model stands at the published rest values until something asks
  the run to begin

#### Scenario: A document with no program has no run

- **WHEN** a host asks a mounted document with no published program for
  its run
- **THEN** it is told there is none, and every other handle operation
  behaves exactly as it does today

### Requirement: The step reproduces the producer's own integration

For each step the viewer SHALL take the movement each active command
admits for that step — a pure function of the number of steps since the
command started, so a replayed run admits exactly the same travel — and
propagate it over the edges in the published order, producing one
increment per determined value and committing them together. Where the
published edges carry a cycle, the entries propagated over are the edges
with each such cycle contracted to ONE entry, ordered under the
requirement "The worker orders a block per piece"; a program with no
cycle is propagated over exactly as it was before the viewer knew of
blocks.

- A **continuous law** SHALL contribute the difference of its expression
  evaluated at the end of the step's path and at its start.
- A **law that jumps** SHALL contribute the continuous part only: its
  path SHALL be cut at every crossing of every jump surface it meets,
  taking the jump nodes in the published order so that an inner node has
  already cut the path before an outer one is asked; on each piece every
  jump node SHALL hold one branch, read by evaluating its published level
  quantity at that piece's midpoint; and the contribution SHALL be the sum
  of the branch-substituted law's change over the pieces. A jump SHALL
  therefore never move a part. A level quantity the producer published as
  affine in its sources SHALL have every surface between a piece's two
  endpoint values solved rather than searched; one the viewer finds
  PIECEWISE AFFINE under the requirement "A piecewise-affine quantity is
  cut at its own kinks" SHALL have the piece SUB-DIVIDED at that
  quantity's own kinks and every surface of each sub-piece solved the
  same way; any other SHALL be sampled, bracketed and bisected under the
  published subdivision, rounding and tolerance limits.
- A **law that READS THE COORDINATE IT DRIVES** SHALL instead be
  integrated piece by piece, under the requirement "The worker executes a
  law that reads the coordinate it drives" below. Such a law SHALL
  additionally report, for a driven end at least one of whose cuts placed
  it, the ABSOLUTE value that end holds at the end of the step, and the
  step SHALL commit that value rather than the coordinate's starting
  value plus its increment.
- A **BLOCK** — a cycle of edges contracted to one entry — SHALL
  contribute, for each value it determines, the sum of that value's
  increments over the pieces its selectors cut the step into, each piece
  ordered and run under the requirement "The worker orders a block per
  piece"; and SHALL additionally report, for a value at least one of
  those pieces placed, the ABSOLUTE value it has advanced that value to
  by the END of the step, which the step SHALL commit in place of the
  starting value plus the increment.
- A **wiring** SHALL contribute its source's increment times its published
  factor; a **derived coordinate** SHALL contribute its published linear
  combination, forward or solved backward into its one term, with the
  constant replaced by zero for an increment; and a **check** SHALL
  determine nothing and instead predict what its coordinate should have
  received.
- A value no edge determines SHALL hold.
- Two increments that disagree on one value beyond the published agreement
  window, and a check whose prediction disagrees with what its coordinate
  received, SHALL be a conflict.

A step that would take a banked coordinate outside a declared bound, and
further outside than it stood at the start of the stretch, SHALL treat
that bound as a physical stop: the fraction of the stretch at which the
coordinate reaches it SHALL be located, the earliest one taken first and
everything within the crossing tolerance of it treated as one event; the
stretch SHALL be re-integrated up to that fraction only; the coordinate
SHALL be committed exactly at its bound; every input whose own movement
pushes it SHALL be stopped for the remainder of the step; and what remains
of the step SHALL be examined again. An input that reaches a stopped
coordinate only through a law that is disengaged at that moment SHALL NOT
be stopped. A bound that reads the bounded coordinate alone SHALL be
evaluated once per step from the committed bank, so every segment of one
step is measured against the same number.

An absolute value reported by a law that reads the coordinate it drives,
or by a block, SHALL be applied to the segment's committed state BEFORE
any bound is examined, so that the bounds are judged against the value the step will
actually commit; and where a declared bound stops the same coordinate in
the same segment, the BOUND SHALL win, the coordinate being committed
exactly at it. Such a report SHALL NOT be a stop: it stops no input,
retires no command, and appears in the crossing record rather than the
stop record.

A bound that READS OTHER COORDINATES SHALL instead be evaluated ALONG
the path of each stretch: the bounded coordinate inside the expression
SHALL take the value it holds in the STEP's committed bank, and every
coordinate the bound reads SHALL take the value it has along the
stretch's path, computed by one pass over that bound's sub-program with
every input's admission scaled by the fraction — the same arithmetic the
segment is later committed by, edge for edge. The CONSTRAINT LEVEL of
such a bound is the coordinate's value minus the evaluated upper bound,
or the evaluated lower bound minus the coordinate's value; outside is
positive.

Such a bound SHALL be examined on a stretch only when the bounded
coordinate or one of its reads has a nonzero increment over that
stretch, so a stretch in which nothing it depends on moves SHALL
evaluate nothing and SHALL stop nothing, and a coordinate left standing
outside SHALL be free until something carries it further. On a stretch
in which NO read moves, the bound SHALL be the number its expression
gives at the step's committed own value and the reads' start-of-stretch
values, evaluated once, and the coordinate SHALL be stopped or freed
exactly as a bound over its own value alone is — the same detection, the
same localization, and the same commit exactly at the bound.

When a read moves, the level SHALL be sampled at the published number of
sub-intervals, each sample one pass over the sub-program, and the
stretch SHALL stop at the FIRST sample at which the level is positive
AND greater than the level at the stretch's start; a level already
positive at the start with a higher first sample SHALL stop the stretch
at its beginning. The crossing SHALL be bracketed against the previous
sample and bisected to the published crossing tolerance within the
published number of rounds, and the fraction taken SHALL be the INSIDE
end of the final bracket — the last fraction at which the bound is
satisfied. The coordinate SHALL NOT be moved onto such a bound: the
segment committed at that fraction satisfies it by the same arithmetic
that located it. The viewer SHALL assert that it does, at the state the
segment commits, and SHALL refuse the whole step as a broken invariant
otherwise.

The GROUP such a stop stops SHALL be every candidate of that bound with
a nonzero admission whose admission ALONE, over the sub-program, raises
the constraint level from the start of the stretch to its end. An input
moving the bounded coordinate against the bound SHALL therefore be
stopped; an input moving a read so as to make a STANDING position
invalid SHALL be stopped where the bound becomes active, and the
standing coordinate SHALL NOT move; and an input moving a read so as to
RELIEVE the bound SHALL run its whole step. The stop SHALL record the
bound EVALUATED at the committed state, which for such a bound is not
the value the coordinate holds.

A step SHALL be atomic across its segments: the bank, the commands'
admitted travel and the records SHALL be applied only once every segment
has succeeded. A conflict, a partition exceeding the published crossing
limit, a law that cannot be integrated over the step's path, a cut that
places a self-read coordinate nowhere, a stop that
stops no moving input, or a bound the committed state does not satisfy
SHALL commit nothing — the bank, the step count and the pose stand —
SHALL retire the commands that moved an input in that step reporting that
the step did not happen, and SHALL report what disagreed, naming the
relation as its author wrote it and the class that stated it.

A command SHALL retire reporting completed, blocked, refused or cancelled,
with the travel it actually admitted in the units the request was stated
in. A command whose input was stopped SHALL retire **blocked** with the
travel it made, and nothing SHALL remember the travel it did not make.
One input SHALL have one owner at a time.

The viewer SHALL keep a bounded record of the most recent steps, of the
jump surfaces crossed inside them and of the stops located inside them,
each entry naming what a reader of the model can find: the relation, the
coordinate, the primitive and the surface level for a crossing; the
coordinate, the side, the evaluated bound, the fraction of the step and
the inputs blocked for a stop.

#### Scenario: A kink costs nothing and a jump moves nothing

- **WHEN** a step moves a source across a kink of a continuous law and, in
  another law, across a jump surface
- **THEN** the continuous law's coordinate moves by the difference of the
  two evaluations, and the jumping law's coordinate moves by its
  continuous part alone, with the jump's own step subtracted

#### Scenario: Several surfaces in one step are all counted

- **WHEN** one step carries a source across three surfaces of one affine
  level quantity
- **THEN** the path is cut three times and the law's contribution is the
  sum over the four pieces

#### Scenario: A step commits the value a cut left a coordinate at

- **WHEN** a step cuts a self-read law's path and the cut places its
  driven coordinate, and no declared bound stops that coordinate in the
  same segment
- **THEN** the committed bank holds the value the walk left it at rather
  than its starting value plus the step's increment, no stop is recorded
  for it, and the crossing is in the crossing record

#### Scenario: A bound on the same coordinate wins over the value a cut left

- **WHEN** one segment both cuts a self-read law's path, placing its
  driven coordinate, and takes that same coordinate past a declared bound
- **THEN** the coordinate is committed exactly at its bound, the stop is
  recorded naming it, and the value the cut placed it at is not what the
  step commits

#### Scenario: A stop blocks the group that pushes it

- **WHEN** a coordinate reaches a declared bound part-way through a step
  while an unrelated input is running
- **THEN** the coordinate is committed at its bound, the command on every
  input whose movement pushes it retires blocked with the travel admitted
  before the stop, and the unrelated input completes its whole step

#### Scenario: A disengaged coupling is not stopped

- **WHEN** a stopped coordinate is reachable from an input only through a
  law whose slope is zero at that instant
- **THEN** that input is not stopped and its command continues

#### Scenario: Two increments that disagree commit nothing

- **WHEN** two routes give one coordinate increments differing by more
  than the published agreement window
- **THEN** the step commits nothing, the bank and step count stand, the
  commands that moved are retired as refused, and the report names both
  relations and the coordinate

#### Scenario: A run state restores only into the machine it came from

- **WHEN** a host restores a run state whose program identity or step size
  differs from the running one
- **THEN** the restore is refused naming both, before any live state
  changes

#### Scenario: A bounded coordinate is blocked while what its bound reads is in the wrong place

- **WHEN** a step asks an input to move a coordinate whose bound reads
  other coordinates, and those coordinates stand where the bound
  evaluates to the coordinate's current value
- **THEN** the step commits with the coordinate exactly where it stood,
  the command retires blocked with nothing admitted, and the stop names
  the coordinate, the side, the evaluated bound, the fraction zero and
  that input

#### Scenario: One step both frees the bound and asks for the movement it frees

- **WHEN** one step moves the coordinates a bound reads into the place
  that frees it AND asks an input to move the bounded coordinate
- **THEN** the step that frees it completes in full, the bounded
  coordinate does not move inside that step, and the same request made
  on the next step completes

#### Scenario: A dependency never overruns a standing coordinate

- **WHEN** a coordinate stands inside its bound and an input moves a
  coordinate that bound READS, so as to make that standing position
  invalid
- **THEN** the input moving the read is stopped at the fraction at which
  the bound becomes active, its command retires blocked with the travel
  it made, the standing coordinate does not move at all, and the stop
  names the STANDING coordinate with the bound evaluated at the
  committed state

#### Scenario: A bound satisfied again by the end of the step is still a stop

- **WHEN** a step would carry a bound outside part-way through and back
  inside by its end
- **THEN** the step is stopped where the violation begins rather than
  committed whole

#### Scenario: A quiet bound costs nothing

- **WHEN** a step moves nothing a bound that reads other coordinates
  depends on
- **THEN** that bound is not evaluated, nothing is stopped by it, and a
  coordinate standing outside it stays where it is

#### Scenario: A block's values are committed together with the rest

- **WHEN** a step propagates over a program whose edges carry a cycle
- **THEN** the values that cycle determines are committed in the same
  bank as every other value of that step, a conflict between two routes
  is judged by the same agreement window, and a step that fails commits
  none of them

### Requirement: A program the viewer cannot execute is refused by name

A document whose published program the viewer cannot execute SHALL be
refused when the document is loaded — beside the refusals for an
unreadable document version, an unknown flexible technology, an
unresolvable bindings table and an undeclared name — naming what is wrong
and quoting the document. Nothing SHALL be rendered from it and no step
SHALL ever be taken on it.

The refusal SHALL cover at least: a document declaring the running version
with no program object or missing one of its published parts; a coordinate
entry whose kind is unknown or whose rest value is not a finite number;
a set of input coordinates that disagrees with the document's own drivers
table in either direction; an edge whose kind is unknown, or whose
per-output lists are not aligned with its outputs; an edge naming a value
that is neither a bank coordinate nor a published computed value; a jump
whose primitive is outside the published set; a branch placeholder two
plans share; an expression, skeleton or level quantity whose free names
are not among the ones that edge may read; a bound naming anything but
the coordinate it bounds and the program's own bank coordinates; a
declared bound over a coordinate the bank does not hold; a limit that is
missing or not a finite number; a computed value the document reads that
no edge determines; a clock name that is also a coordinate or a driver
id; and an identifier set that cannot be resolved as names, such as one
identifier being a strict prefix of another.

For a law edge that READS THE COORDINATE IT DRIVES — one naming a value
among both what it reads and what it determines — the refusal SHALL also
cover: such an edge that determines more than one value, or that reads
more than one of the values it determines, saying that a law reading its
own driven end drives exactly one coordinate; such an edge whose driven
end is a published computed value rather than a coordinate of the bank,
saying that a retained value is a history and only a coordinate the run
banks keeps one; and such an edge whose jump plan's SKELETON — its
expression with every jump node replaced by that node's branch — still
names the driven coordinate, saying that the read must pass through a
node that is piecewise constant in the coordinate and that a remainder
alone is not one, because with its quotient fixed a remainder still
carries the coordinate's slope. Each refusal SHALL name the edge, the
coordinate and the document.

For a BLOCK — a cycle of the published edges over what they read and
determine, a value an edge itself determines excluded — the refusal SHALL
also cover: a published listing of the edges that is not an order in
which every entry's sources are determined before it runs once each such
cycle is contracted, naming the two edges and the value; a wiring or a
derived coordinate on such a cycle, saying that it carries no jump node
so no selection can switch what it reads; a member of such a cycle that
determines more than one value, saying that what a selection switches is
decided per driven end while a group's ends are bound together; a member
whose driven value is a published computed value rather than a coordinate
of the bank, saying that a block advances its values piece by piece and
only a coordinate the run banks keeps that; and a cycle whose members'
UNCONDITIONAL dependencies — what each still reads with every foldable
selector at its zero branch — are themselves cyclic, saying that such a
cycle is present on every piece and that a dependency inside a cycle is
admitted only where some selection switches it. Each refusal SHALL name
the edge, the class that stated it, and every relation on the cycle.

A bound's free names SHALL be judged after the document's bindings table
has been closed over, so a name reached only through a shared
subexpression is judged as the coordinate it resolves to. A refusal of a
name that the document publishes as a COMPUTED VALUE rather than a bank
coordinate SHALL say so, because such a bound must name the coordinate
that value is computed from.

#### Scenario: A primitive the engine does not know

- **WHEN** a loaded program carries a jump whose primitive is not one the
  viewer can read a branch from
- **THEN** loading fails naming that primitive and the ones it knows, and
  no frame is rendered

#### Scenario: Two plans sharing one placeholder

- **WHEN** two jump plans of one document name their jump nodes with the
  same placeholder
- **THEN** loading fails naming the placeholder, rather than letting two
  different jump nodes share one published subexpression

#### Scenario: The two declarations of an input disagree

- **WHEN** a program declares an input coordinate the document's drivers
  table does not, or the table declares a driver the program does not
- **THEN** loading fails naming the difference

#### Scenario: A pose that reads a value nothing computes

- **WHEN** a document's pose expression reads a published computed value
  that no edge determines
- **THEN** loading fails naming that value, rather than posing the model
  from a number that was never produced

#### Scenario: A bound reading a computed value is refused by name

- **WHEN** a loaded program's bound names a published computed value
  rather than a bank coordinate
- **THEN** loading fails naming that value, saying it is a computed value
  and not a coordinate of the bank, quoting the expression, and nothing
  is rendered

#### Scenario: A bound reading a name the program never declares

- **WHEN** a loaded program's bound names something that is neither the
  bounded coordinate, nor a bank coordinate, nor a computed value
- **THEN** loading fails naming it and saying what such a bound may read

#### Scenario: A self-read law driving more than one coordinate

- **WHEN** a loaded program carries a law edge that determines two values
  and names one of them among the values it reads
- **THEN** loading fails naming that edge and that coordinate, saying a
  law reading its own driven end drives exactly one coordinate, and no
  frame is rendered

#### Scenario: A self-read of a value the bank does not hold

- **WHEN** a loaded program carries a law edge that reads a value it
  determines, and that value is a published computed value rather than a
  bank coordinate
- **THEN** loading fails naming it and saying that a retained value is a
  history and only a coordinate the run banks keeps one

#### Scenario: A read that survives the skeleton

- **WHEN** a loaded program carries a law edge reading a coordinate it
  drives, whose plan's skeleton still names that coordinate
- **THEN** loading fails naming the edge and the coordinate, saying the
  read must pass through a node that is piecewise constant in it and that
  a remainder alone is not one

#### Scenario: A bound reading another coordinate loads

- **WHEN** a loaded program's bound names other bank coordinates, whether
  directly or through the bindings table
- **THEN** the document loads, its run is created at the published rest
  values, and the bound is executed as a constraint

#### Scenario: A cycle no selection can break

- **WHEN** a loaded program's edges carry a cycle one of whose in-cycle
  dependencies survives folding every foldable selector of its member to
  zero
- **THEN** loading fails naming every relation on the cycle and saying
  that a dependency inside a cycle is admitted only where a selection
  switches it, and no frame is rendered

#### Scenario: A wiring on a cycle

- **WHEN** a loaded program's cycle passes through a wiring or a derived
  coordinate
- **THEN** loading fails naming it and the cycle, saying that it carries
  no jump node and that no selection can switch what it reads

#### Scenario: A block member that is not a banked coordinate

- **WHEN** a loaded program's cycle determines a published computed value
- **THEN** loading fails naming that edge and that value, saying that
  only a coordinate the run banks keeps the history a block advances
  piece by piece

#### Scenario: A published listing that is not an order

- **WHEN** a loaded program publishes an edge that reads a value another
  edge determines LATER in the listing, once every cycle is contracted
- **THEN** loading fails naming both edges and the value, rather than
  re-sorting the published edges

### Requirement: A committed bank poses the geometry

For a document carrying a program, the viewer SHALL pose the model from
the bank the run last committed, by evaluating the document's own
expressions with the bank's coordinate identifiers available as names
beside the driver identifiers, through the same evaluation the viewer
performs for any other document. No second pose path and no second table
of poses SHALL exist, and a flexible part's shape parameters SHALL follow
the bank by the same rule as a rigid part's placement.

The program's published clock name SHALL resolve to the elapsed
simulation seconds, which never wrap; with no run — a still capture, a
thumbnail — it SHALL resolve to zero, the instant the rest pose is defined
at. Before the first step, the model SHALL be posed at the rest values the
program publishes.

Only the parts whose expressions read a coordinate that moved SHALL be
re-evaluated, which is the bound the viewer already holds for a driver.

A qualified identifier SHALL resolve at every one of its segments, so an
identifier naming an instance path of any depth resolves to the value
published under it.

#### Scenario: A wheel follows its coordinate

- **WHEN** a run commits a bank in which one joint coordinate moved
- **THEN** the part whose placement names that coordinate is re-posed,
  parts naming only other coordinates keep the matrices they have, and a
  flexible part whose parameter reads it changes shape

#### Scenario: A document opens at its rest pose

- **WHEN** a document carrying a program is mounted and no step has been
  taken
- **THEN** every part stands where the published rest values put it

#### Scenario: A three-segment identifier resolves

- **WHEN** an expression names an identifier of three or more segments,
  such as a joint coordinate on a nested assembly
- **THEN** it resolves to that value rather than to nothing, and the pose
  is a number

### Requirement: The two runtimes agree on a conformance corpus

The widget suite SHALL replay the producer's committed running corpus
through the shipped run engine and SHALL agree with it on every step of
every scenario. The corpus's expected values are the producer's own; a
disagreement means this viewer drifted, and SHALL be fixed here rather
than admitted by widening a tolerance.

For each scenario the suite SHALL build the engine from the corpus's own
copy of the published document — the program, the drivers, the
instructions and the bindings table — at the corpus's step size, apply
each scripted command before the step it names in the order the corpus
lists them, and compare every step: the committed bank, the crossings and
the stops located in that step, and every command created so far with its
status and the travel it has admitted.

Agreement SHALL be EXACT for discrete state — step numbers, command
statuses, coordinate, relation, primitive, bound and input names, crossing
surface levels, and the ORDER of every list — and within the corpus's
stated relative tolerance for floats, which is the run's own agreement
window. A sampled comparison SHALL NOT be accepted: every step the corpus
lists SHALL be compared.

The suite SHALL also assert the corpus's own width — the discontinuous
primitives, a multi-source law, a stop located inside a step, a bound
stated as an expression, a bound READING ANOTHER COORDINATE, a stop
reached by the motion of what a bound reads (one whose coordinate holds
the same value before and after its step), a command retired blocked, a
rate, a run state taken and restored, both instruction forms, a step
carrying both a crossing and a stop, A LAW THAT READS THE COORDINATE IT
DRIVES, a self-read coordinate that HOLDS at its gate over a step in
which an input reaching it goes on moving, a step carrying both a
self-read crossing and a stop, A SWITCHED SOURCE — a published edge on a
cycle that reads a value the cycle determines — a SELECTION CROSSING
inside a step, a step carrying both a selection crossing and a stop, and
an IN-BLOCK GATE CROSSING located STRICTLY INSIDE a step — a crossing
recorded under a member of a block that only a jump reading a value
ANOTHER member of that block determines can account for, the member's own
driven value excluded — and a STOP LOCATED STRICTLY INSIDE a step ON A
KINKED DETERMINER — a coordinate whose determining law carries no jump
plan at all and whose published expression, closed over the corpus's
bindings table, calls one of the CONTINUOUS SELECTIONS `abs`, `min` or
`max`, so that its value along a step is piecewise affine rather than
affine and a consumer dividing once over the whole step would place the
stop where the coordinate never was — so that a narrower corpus copied in
is refused here without anyone running the producer's generator. A bound
reading another coordinate SHALL be recognised through the corpus's own
bindings table, so a corpus whose bound reaches its reads through a
shared subexpression counts as covering it. A block and its selectors
SHALL be re-derived for this assertion FROM THE CORPUS'S OWN DOCUMENTS
and tick logs, by the same reading a consumer of the document makes and
not by asking the run engine, so that the assertion is red on a narrowed
corpus even when the engine is broken; a KINKED DETERMINER SHALL be
re-derived the same way and from the same two sources — the absent plan
and the expression closed over the bindings table — and never by asking
the run engine what it classified; and a crossing SHALL count as a
SELECTION crossing only where its primitive belongs to a selector of the
member that determines its coordinate and to no other jump of that
member, so that a gate which happens to share an operator is not
mistaken for one. An in-block gate crossing SHALL be recognised from the
crossing's own primitive and the preceding step's committed values: the
jumps of that member carrying the primitive, their level quantities closed
over the corpus's bindings table, SHALL be separated into those reaching a
value the block determines other than the member's own and those reaching
none of the block's values, and the crossing SHALL count only where one of
the first kind reads a value that MOVED across the step and no one of the
second kind reads a value that moved or a value the step does not carry.
A step with no predecessor SHALL be skipped, having nothing to compare
against.

The committed corpus SHALL DISCRIMINATE the order in which a block's
members are run, because a document publishes those members as a listing
and not as an execution order: replaying a named scenario through the
shipped engine with the block's members run in the order the document
publishes them, instead of ordered for each piece of the step, SHALL
disagree with the corpus by more than the stated tolerance on the
committed values of at least one step, while the same replay with the
members ordered per piece reproduces them. The suite SHALL assert this
directly, rather than inferring it from the width above.

#### Scenario: Every scenario of the corpus replays

- **WHEN** the widget suite replays the committed corpus through the run
  engine
- **THEN** every step of every scenario matches, exactly for discrete
  state and within the stated relative tolerance for floats

#### Scenario: A narrowed corpus is refused

- **WHEN** the committed corpus is replaced by one exercising fewer of the
  stated features
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: A corpus with no bound reading another coordinate is refused

- **WHEN** the committed corpus is replaced by one whose machines declare
  no bound reading another coordinate, or record no stop whose
  coordinate did not move
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: A corpus with no law reading the coordinate it drives is refused

- **WHEN** the committed corpus is replaced by one none of whose machines
  states a law reading the coordinate it drives, or none of whose steps
  holds such a coordinate at its gate while an input reaching it moves on
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: A corpus with no selection is refused

- **WHEN** the committed corpus is replaced by one none of whose machines
  publishes a cycle of edges with a switched source, or none of whose
  steps carries a selection crossing, or none of whose steps carries both
  a selection crossing and a stop
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: A drifted engine is caught, not tolerated

- **WHEN** the engine's arithmetic is changed so one machine's bank
  differs in the last bits beyond the corpus's tolerance
- **THEN** the suite fails naming the scenario, the step and the
  coordinate

#### Scenario: A corpus with no in-block gate crossing is refused

- **WHEN** the committed corpus is replaced by one none of whose steps
  records a crossing, strictly inside the step, under a member of a block
  that only a gate on a value another member of that block determines can
  account for
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: An engine that runs a block in the published order is caught

- **WHEN** a corpus scenario carrying a block is replayed through the run
  engine with the block's members run in the order the document publishes
  them, instead of ordered for each piece of the step
- **THEN** the replay disagrees with the corpus by more than the stated
  tolerance on the committed values of at least one step, while the same
  replay with the members ordered per piece reproduces them

#### Scenario: A corpus with no stop on a kinked determiner is refused

- **WHEN** the committed corpus is replaced by one none of whose steps
  records a stop, strictly inside the step, on a coordinate whose
  determining law carries no jump plan and whose expression calls a
  continuous selection
- **THEN** the suite fails naming the feature no longer covered

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

### Requirement: A declared bound may read other coordinates

A span the document publishes as an expression MAY name, beside the
bounded coordinate's own identifier, other coordinates of the program's
bank. The viewer SHALL read such a bound as a CONSTRAINT between the
bounded coordinate and what it reads, and SHALL derive everything it
needs to execute one WHEN THE DOCUMENT IS LOADED, from what the document
already publishes — the producer publishes no further table for it.

For each side of each span whose expression names a coordinate other
than the bounded one, the viewer SHALL derive:

- its READS: the free names of that expression, CLOSED OVER the
  document's own bindings table, minus the bounded coordinate's own
  identifier. A bound whose expression reaches a coordinate only through
  a shared subexpression SHALL read that coordinate, exactly as one
  naming it directly does; a bound whose expression never names the
  bounded coordinate is well formed, because the test is containment and
  not equality;
- its SUB-PROGRAM: the published edges that determine the bounded
  coordinate and every read, and everything those need, in the program's
  own published order, a check edge never among them;
- its CANDIDATES: the input identifiers the program's own reaching-input
  table gives for the bounded coordinate or for any read, without
  repetition and in a determinate order.

None of the three SHALL be published in the document, and the viewer
SHALL NOT require any of them to be: each is a projection of the
coordinates, the edges and the reaching-input table the document already
carries.

A span side that is `null` or a number, and one whose expression names
the bounded coordinate alone, SHALL NOT become a constraint: their
meaning, their code path and their cost SHALL be exactly what they are
today.

#### Scenario: A bound reaching a coordinate through a shared subexpression reads it

- **WHEN** a loaded document's bound names only entries of the bindings
  table, and those entries resolve to other bank coordinates
- **THEN** the bound's reads are those coordinates, and a step in which
  one of them moves is measured along the step's path rather than
  against a number taken at its start

#### Scenario: A bound naming no coordinate but its own is not a constraint

- **WHEN** a loaded document declares a bound whose expression names the
  bounded coordinate alone
- **THEN** it is evaluated once per step from the committed bank, the
  coordinate is committed exactly at it when it stops there, and nothing
  about the step differs from before this capability existed

#### Scenario: The sub-program is the published edges, in the published order

- **WHEN** a bound reads coordinates determined by some of the
  program's edges and not others
- **THEN** the constraint's sub-program holds exactly the edges
  determining the bounded coordinate, the reads and what those need, in
  the document's own edge order

### Requirement: The viewer draws the markings a part carries

The viewer SHALL draw every marking a rigid node of the published document
carries, one per entry of that node's markings list, each from the artifact the
entry names and in the colour the entry declares. A marking SHALL be drawn in
its part's own place, moving with the part under every pose, animation instant
and committed mechanical state the part moves under, with no placement supplied
by the viewer: the artifact holds the artwork's surface in the part's own frame,
and the part's own operations place it.

A marking SHALL be drawn OVER the surface it lies on, from every viewing
distance and angle at which the part itself is drawn, and SHALL NOT be broken
up by the surface it marks. The bias that achieves this is the viewer's own
rendering constant and SHALL NOT be presented as, or derived from, anything the
document states about where the part's surface is. A marking whose artwork is
open on both sides SHALL be drawn from either side.

A node that carries no markings SHALL be drawn exactly as it is drawn by a
viewer that has never read a marking: the same geometry, the same material and
the same scene contents. A document whose nodes carry no markings SHALL be
rendered, read back and photographed identically to the same document published
before markings existed.

The viewer SHALL draw markings on a document of any schema version it renders:
the markings list is additive to the document and is gated on no version.

#### Scenario: A part's markings are drawn in their own colours

- **WHEN** a document is mounted whose part carries two markings declaring
  different colours
- **THEN** both are drawn on that part, each in the colour its own entry
  declares, and the part is drawn in the colour it declares

#### Scenario: A marking goes where its part goes

- **WHEN** a driver, an animation instant or a mechanical command moves a part
  that carries a marking
- **THEN** the marking moves with it, arriving in the same place on the part's
  surface it started on, without the viewer computing any placement for it

#### Scenario: A marking is visible over the surface it marks

- **WHEN** a marked part is photographed from a viewpoint that sees the marked
  surface
- **THEN** the marking's colour is what is seen where the marking is, and the
  part's is what is seen where it is not

#### Scenario: A marking on a colourless part

- **WHEN** a document is mounted whose marked part inherits no colour
- **THEN** the part renders with the normal-based material and its marking
  renders in its own declared colour

#### Scenario: A marked document below the running version

- **WHEN** a document that declares an early schema version carries markings on
  its parts
- **THEN** its markings are drawn, exactly as a later version's are

#### Scenario: An unmarked document is untouched

- **WHEN** a document whose parts carry no markings is mounted
- **THEN** it renders exactly the picture it rendered before this viewer could
  draw a marking, and its scene contains nothing a marking would have added

### Requirement: A markings list the viewer cannot read is refused by name

The viewer SHALL refuse a document whose markings it cannot read, before
anything is rendered, naming the document, the node and the marking at fault and
what is wrong with it — the same refusal surface an unresolvable bindings table,
an inexecutable program and an unresolvable controls table already stand on. It
SHALL refuse a markings value that is not a list; an entry that is not an
object, or whose name or artifact reference is not a non-empty string, or whose
colour is not a six-digit hexadecimal colour; two markings of one node declaring
the same name; and a markings list on a node that is not rigid.

The viewer SHALL NOT draw a document's markings in part: a marking it cannot
read is a fault in the document that produced it, and rendering the rest would
present an incomplete marking as the machine's own answer.

A node carrying no markings key SHALL reach exactly the validation it reached
before this viewer could read one.

#### Scenario: A marking without a colour

- **WHEN** a document carries a marking whose entry declares no colour, or one
  that is not a six-digit hexadecimal colour
- **THEN** the document is refused naming it, before anything is rendered

#### Scenario: A marking without an artifact

- **WHEN** a document carries a marking whose entry names no artifact
- **THEN** the document is refused naming the node and the marking, and no
  geometry is fetched

#### Scenario: Two markings of one part share a name

- **WHEN** a node's markings list declares the same name twice
- **THEN** the document is refused naming the node and the repeated name

#### Scenario: A marking on a node that is not rigid

- **WHEN** a markings list appears on a node that carries children or a
  flexible spec
- **THEN** the document is refused naming that node

#### Scenario: A document with no markings is validated as before

- **WHEN** a document whose nodes carry no markings key is mounted
- **THEN** it is accepted or refused exactly as it was before this viewer could
  read a markings list

### Requirement: The worker executes a law that reads the coordinate it drives

A published law edge MAY name, among the values it READS, one of the
values it DETERMINES. That is a law reading the coordinate it drives, and
the viewer SHALL recognise it from what the document already carries —
the intersection of the edge's read set with its determined set — and
SHALL require no further key for it. A law edge with an empty
intersection SHALL be integrated exactly as it is today, by the same
code, at the same cost.

Such an edge SHALL determine exactly ONE value and SHALL read exactly one
of the values it determines, and that value SHALL be a coordinate of the
bank; a shape that is not so SHALL be refused when the document is
loaded, under the requirement "A program the viewer cannot execute is
refused by name". The plan's SKELETON — its expression with every jump
node replaced by that node's branch — SHALL NOT name the driven
coordinate, and one that does SHALL be refused there too: a read that
survives the skeleton enters the law continuously, and the difference of
two evaluations does not define that.

The viewer SHALL derive, WHEN THE DOCUMENT IS LOADED, which of the plan's
jump nodes DEPEND on the driven coordinate: a node depends on it when
that coordinate is among the free names of the node's published level
quantity, CLOSED OVER the document's own bindings table, or when that
level names the branch placeholder of a node that depends on it. A node
reaching the driven coordinate only through a shared subexpression
depends on it exactly as one naming it directly does. Nothing of this
SHALL be published in the document and the viewer SHALL NOT require any
of it to be.

**Over one step such a law SHALL be integrated PIECE BY PIECE.** The
step's path SHALL first be partitioned by the jump nodes that do NOT
depend on the driven coordinate, exactly as any other law's path is,
their branches read at that partition's midpoints; INSIDE each of its
pieces the dependent nodes SHALL then be walked:

- At the walk's left end the driven coordinate holds a known value: the
  step's committed value at the start, and the value the cuts already
  taken placed it at afterwards.
- Every dependent node's branch SHALL be determined in the plan's
  published order, with the driven coordinate at that retained value and
  every OTHER source at the piece's LEFT END — not at its midpoint,
  because a level naming both the driven coordinate and a source may
  cross inside the piece by the source's motion alone, and the branch
  read past that crossing is not the branch the piece begins under.
- A dependent node whose level sits EXACTLY on a surface at that left end
  SHALL take the branch its primitive gives; if the level then LEAVES the
  surface into another branch's region, that node SHALL be flipped to the
  branch of the region IMMEDIATELY on the side it departs to, at the left
  end, and every branch decided again. If the flipped branch carries the
  level back across as well, the STEP SHALL be refused naming the
  relation, the coordinate and the primitive, and SHALL commit nothing.
- With those branches fixed the substituted law SHALL NOT name the driven
  coordinate, so that coordinate's own value along the piece is one
  ordinary evaluation.
- Each dependent node's level quantity SHALL be followed along the piece
  — through the driven coordinate's own path and through the sources —
  and the piece SHALL be CUT at the FIRST surface any of them reaches
  strictly inside it: SOLVED where the producer published both that level
  and the plan's skeleton as affine; solved on SUB-INTERVALS where
  neither is curved and at least one is PIECEWISE AFFINE under the
  requirement "A piecewise-affine quantity is cut at its own kinks", the
  piece being cut first at the SKELETON's kinks — which are what make the
  driven coordinate's own path affine at all — and each of those cut
  again at the LEVEL's own, which ride that path and SHALL therefore be
  located inside one skeleton sub-piece with the driven coordinate read
  by interpolation between that sub-piece's two ends; otherwise sampled
  at the published number of sub-intervals and bisected to the published
  crossing tolerance within the published number of rounds. No further tolerance
  SHALL be introduced, and a crossing found within that tolerance of the
  piece's left end SHALL NOT be merged into it — the merging of two near
  cuts belongs to the partition over the independent nodes and SHALL NOT
  be applied in this walk.
- The piece's contribution SHALL be the substituted law's change over it,
  and the next piece SHALL be decided the same way, until the enclosing
  piece is exhausted or the published crossing limit is reached, which
  refuses the step as any other over-cut path is refused.

**After a cut the driven coordinate SHALL be placed AT THE FAR SIDE OF
THE SURFACE, at the nearest representable value.** Where the piece moved
it, the coordinate SHALL be placed at the representable value NEAREST the
surface among those at which the crossing node's level — evaluated with
the driven coordinate at that value and every other source at the
crossing's own fraction — reads the branch on the side the level was
moving TOWARD, judged by the VIEWER'S OWN evaluation of the published
level. Where the piece did NOT move it, the coordinate SHALL stand where
it stood. A step at least one of whose cuts placed the coordinate SHALL
COMMIT the value the walk left it at rather than its starting value plus
the increment; a step none of whose cuts placed it SHALL commit as it
always has. A cut that can place the coordinate nowhere SHALL refuse the
step naming the relation, the coordinate and the primitive, as a broken
invariant of the run rather than a step size that is too coarse, and
SHALL commit nothing.

The driven coordinate's own value along a piece SHALL be computed by
adding to the value it holds at the piece's left end the CHANGE of the
substituted law over the piece — the change taken FIRST — so that a piece
whose substituted law does not move adds a true zero and the coordinate
keeps the exact float it held. Computed in the other association the sum
rounds whenever the law's magnitude is comparable to the coordinate's,
and a coordinate nothing moved would still shift by one unit in the last
place.

Where such a law is a member of a block, every SELECTOR of its plan SHALL
hold, through the whole of this walk, the branch the block read at the
piece's midpoint — in the partition over the independent nodes, in every
branch reading, in every probe, in every cut and in the far-side landing
— and that node's crossings SHALL NOT be located again inside the piece.

A coordinate held at its gate SHALL therefore read the same branch on
every later step, whatever its sources do, SHALL be unmoved by a further
step in the same direction BIT FOR BIT, and SHALL survive a run state
taken and restored unchanged.

A crossing located by this walk SHALL be recorded as a CROSSING — the
relation, the coordinate, the primitive, the surface level and the
fraction of the step — and never as a stop.

A declared bound on the driven coordinate SHALL still stop it exactly as
it stops any other coordinate — located over this same partition and
committed AT the bound — and where a step's cut has placed the
coordinate and a bound of the same coordinate is reached in the same
segment, the bound SHALL win: a physical bound is a bound of the
coordinate itself.

#### Scenario: A dial clears to its gap and the ring sweeps on

- **WHEN** a document whose law gates a dial on the dial's own retained
  angle, disengaged over a band about every full turn, is run with the
  dial resting part way and the ring swept far enough to carry it to the
  band
- **THEN** the dial ends within the band, at a value that reads
  disengaged under the viewer's own evaluation of the published level,
  the ring completes its whole travel, and the crossing appears in the
  crossing record and not in the stop record

#### Scenario: Sweeping an already-cleared dial moves it by nothing

- **WHEN** the same machine is swept again, and again

- **THEN** the dial holds the same value bit for bit after each sweep,
  every request completes, and no stop is recorded

#### Scenario: A branch is read from the retained value, not the midpoint

- **WHEN** a law's level quantity names both the driven coordinate and a
  moving source, so that it crosses inside a piece by the source's motion
  alone
- **THEN** the piece is integrated under the branch its LEFT END gives
  and cut where the level reaches the surface, rather than under the
  branch a midpoint reading would have chosen

#### Scenario: A coordinate standing exactly on a surface is not driven through it

- **WHEN** the driven coordinate stands exactly at the value its own
  gate's surface sits on — the value a previous cut placed it at — and
  the sources are moved, first so as to carry the level into the engaged
  region and then so as to carry it away
- **THEN** it holds in the first case and moves in the second, and in
  neither is it carried through the band by a piece integrated under the
  wrong branch

#### Scenario: A level that will not settle refuses the step

- **WHEN** a dependent node sits on a surface at a piece's left end and
  each of the two branches carries the level back across it
- **THEN** the step is refused naming the relation, the coordinate and
  the primitive, the bank, the step count and the pose stand as they
  were, and the commands that moved are retired reporting that the step
  did not happen

#### Scenario: Several coordinates clear independently from one input

- **WHEN** one input drives several coordinates, each by its own law
  reading its own driven end, and the input is moved far enough to reach
  some of them and not others
- **THEN** each reached coordinate ends at its own band, each unreached
  one is untouched, one coordinate's disengagement cuts only its own
  path, and the input's command completes with its whole travel admitted

#### Scenario: A declared bound on the same coordinate still stops it

- **WHEN** the coordinate a self-read law drives declares a bound, and
  one step carries the coordinate through a cut of its own gate and on
  to that bound
- **THEN** the coordinate is committed at the bound exactly, the stop
  is recorded in the stop record naming it, the crossing is recorded
  in the crossing record at its fraction of the step, and the inputs
  that pushed it are retired blocked

#### Scenario: A coordinate no piece moved keeps its exact float

- **WHEN** a step moves a source of a self-read law whose substituted law
  does not change over the piece, and the driven coordinate stands at a
  value of a magnitude comparable to that law's
- **THEN** the coordinate holds the float it held, bit for bit, rather
  than shifting by one unit in the last place

#### Scenario: A law that reads nothing of its own is untouched

- **WHEN** a document whose every law edge reads only values it does not
  determine is run
- **THEN** every step is the partition, the midpoint branches and the sum
  it always was, and the run takes the same path at the same cost

### Requirement: The worker orders a block per piece

A published program's dependency graph — edge A before edge B when B
reads a value A determines, with a value an edge itself determines
EXCLUDED — MAY carry a cycle. Every nontrivial strongly connected
component of it is a **BLOCK**, and the viewer SHALL recognise a block
from what the document already carries, requiring no further key for it.
A program with no such component SHALL be executed exactly as it is
today, by the same code, at the same cost.

**The published order of a block's members is a LISTING and not an
execution order.** The viewer SHALL NOT execute a block's members in the
order they are published. It SHALL contract each block to ONE entry of
the program, at the position of the block's first published member, every
other edge keeping its published position and the edges their relative
order; and it SHALL verify that the result is an order in which every
entry's sources are determined before it runs, refusing the document
naming the two edges and the value otherwise. A consumer that re-sorted
the published edges would be inventing an ordering decision the producer
already made.

A **SELECTOR** of a block member is a jump node of that member's plan
whose published level quantity, closed over the document's own bindings
table and resolved transitively through the branch placeholders it names,
reads no value the block determines. A selector's branch is therefore
known before the block runs. A node whose level reads the member's own
driven end is NOT a selector and SHALL stay in the walked layer of the
requirement "The worker executes a law that reads the coordinate it
drives".

A source of a member is **SWITCHED** when setting a selector's branch to
ZERO removes it from that member's law. The viewer SHALL decide this by
folding the member's published skeleton with `x*0`, `0*x` and `0/x`
taken as zero, `0+y`, `y+0`, `y−0` as the surviving operand and `0−y` as
its negation, and reading what the folded skeleton then names, following
every surviving placeholder into its own folded level quantity. A branch
SHALL be admitted as foldable only where its primitive holds that branch
over an INTERVAL of its level quantity — a floor, a ceiling, a remainder
or a comparison — and never where it holds it at a single point, which
is the case of a sign. ONE fold per member with every foldable selector
at zero SHALL decide both what that member reads unconditionally and what
a selection can switch; the value a member reads of its OWN driven end is
neither.

A shape that can never be ordered SHALL be refused when the document is
loaded, under the requirement "A program the viewer cannot execute is
refused by name". The check is deliberately NECESSARY and not SUFFICIENT:
which branch vectors a machine can actually reach is arithmetic about its
inputs rather than structure, so a particular piece that is still cyclic
is refused when it is met.

**Over one step a block SHALL be run PIECE BY PIECE.**

- Every member's SELECTOR crossings SHALL be located over the WHOLE
  stretch, by the partition any other law's path is cut by, over a plan
  of that member's selectors alone; they SHALL be merged into one cut
  list in the members' own order and each member's published jump order,
  under the published crossing tolerance and crossing limit; and they
  SHALL be recorded as crossings of the member whose plan states them.
- On each piece every selector's branch SHALL be read at the piece's
  MIDPOINT, and each member's ACTIVE sources SHALL be what its skeleton
  still reads with those actual branch values substituted. The members
  SHALL be ordered over the in-block ones, a member's own driven end
  ignored, and that order SHALL be reused for any later piece whose
  selectors read the same branch VALUES.
- A piece whose active dependencies are still cyclic SHALL refuse the
  step, naming the piece, the relations on the cycle, and each selector
  with its primitive, its level quantity and the value it read. The step
  SHALL commit nothing.
- The members SHALL then run over the piece in that order, each by the
  machinery that already governs it. A source the block does not
  determine SHALL be taken at its value at the piece's left end, moving
  by its share of the stretch. A source the block DOES determine SHALL be
  taken at the value the block has advanced it to by the piece's start,
  moving by the increment computed for it ON THIS PIECE — and by ZERO
  where this piece's order has not determined it, which is safe because
  every term reading it is multiplied by a branch the block forced to
  zero.
- **Every selector SHALL be a CONSTANT for every member on that piece**:
  the branch the block read SHALL be substituted into the member's own
  plan rather than re-derived inside the piece. A forced node's crossings
  SHALL NOT be located again, and every reading of its branch — in either
  layer of a self-read walk, in a probe, in a cut and in a far-side
  landing — SHALL be the value the block substituted.

**What a block reports.** For each value it determines it SHALL report
the sum of that value's increments over the pieces. For a value at least
one piece PLACED, it SHALL additionally report the ABSOLUTE value it has
advanced that value to by the END of the stretch — the placement plus
every later piece's increment — and the step SHALL commit that, because a
reported absolute replaces the starting value plus the increment and
would otherwise discard the motion after it. A value no piece placed
SHALL be reported as an increment only.

Every crossing a member reports inside a piece SHALL be rescaled to its
fraction of the whole stretch, and the whole list — the selectors'
crossings located over the stretch and the members' own rescaled out of
their pieces — SHALL be sorted by that fraction before it is recorded, so
the listing does not depend on which was computed first.

**A declared bound on a value a block determines SHALL be SEARCHED and
never solved**, whatever affinity the member that determines it
publishes: a block's value is piecewise in the selector partition and
re-ordered across it.

A block SHALL be complete and side-effect-free when it is asked for
increments alone — as the probe that decides which inputs a stop blocks
asks — recording no crossing, reporting no placement and mutating
nothing, and SHALL refuse a cyclic piece there under the same midpoint
reading and the same ordering it uses inside the step, so that a probe
and the step it is probing for cannot disagree about whether the machine
can be ordered. The inputs a stop on a block's value blocks SHALL be
decided by displacing each candidate alone and running the WHOLE block
under that displacement, so an input that reaches the stopped value only
through a selection that is inactive at that moment SHALL NOT be blocked.

#### Scenario: A carry that follows the carriage runs

- **WHEN** a document is mounted whose program carries two laws each
  reading what the other determines, one gated on a carriage position
  below a detent and the other above it, and the carriage is left below
  the detent while the crank is turned
- **THEN** the run commits the values the producer commits for the same
  machine, the carry reaching the wheel in the step it was made rather
  than a step later or not at all

#### Scenario: The published listing is not the execution order

- **WHEN** a block's members are published in an order in which one reads
  what a later one determines, which is what the producer's listing does
- **THEN** the step orders them by the dependencies the piece's own
  selection leaves active, and the committed bank does not depend on the
  order the members were listed in

#### Scenario: A selection crossing cuts the step

- **WHEN** one step carries the selecting input across the value at which
  a block's selection changes
- **THEN** the stretch is cut there, each piece is ordered under the
  branches read at its own midpoint, the members run over each piece with
  their in-block values carried forward, and the crossing is recorded at
  its fraction of the step

#### Scenario: A selection change alone moves nothing

- **WHEN** the selecting input is moved from one side of a selection to
  the other and back, with nothing else moving
- **THEN** every value the block determines holds the float it held,
  bit for bit

#### Scenario: A value placed in one piece and moved in a later one

- **WHEN** one step places a block's value at a gate in one piece and
  another source drives it further in a later piece of the same step
- **THEN** the committed bank holds the value the block advanced it to by
  the end of the step, not the value the placement left it at

#### Scenario: A piece that cannot be ordered refuses the step

- **WHEN** a step reads a selection under which every dependency of a
  block's cycle is active
- **THEN** the step commits nothing, the bank, the step count and the
  pose stand, the commands that moved are retired reporting that the step
  did not happen, and the report names the piece, the relations on the
  cycle and what each selector read

#### Scenario: A stop on a block's value is searched

- **WHEN** a step drives a value a block determines into a declared bound
- **THEN** the fraction at which it reaches the bound is found by
  sampling and bisection over the whole block rather than solved from the
  member's published affinity, and the value is committed exactly at its
  bound

#### Scenario: An inactive selection blocks nothing

- **WHEN** a value a block determines reaches a declared bound while an
  input that reaches it only through a selection that is currently
  inactive is running
- **THEN** that input is not blocked and its command completes its whole
  travel, while the input that does push the value retires blocked

#### Scenario: A program with no cycle is untouched

- **WHEN** a document whose program's dependency graph has no cycle is
  run
- **THEN** every step propagates over the published edges in the
  published order exactly as it did before the viewer knew of blocks, at
  the same cost, and the committed bank is the same float for float

### Requirement: Only what moves along a step's path is walked

Executing a published program, the viewer FOLLOWS a quantity along a
step's path: it evaluates one published expression at many points of that
path — the sub-intervals of a sampled search and the rounds of its
bisection, the two ends of each piece of a solve, the midpoint of each
piece of a partition, the points of a self-read walk. Over ONE path, with
ONE branch reading, the value of the part of that expression which reads
no name the step MOVES cannot change. That part SHALL be computed ONCE
for the piece and read back at every point of it, and only the remainder
SHALL be evaluated per point.

Which names MOVE along a path SHALL be the run's own statement and never
inferred from sampling, from comparing two evaluations, or from a
tolerance:

- a source whose increment over the step is non-zero MOVES;
- a jump node's BRANCH, a constant of its piece by construction, STANDS;
- the coordinate a law READS AND DRIVES moves for a quantity the walk
  hands its value to at every point, and stands for one that by refusal
  does not name it at all;
- a name the document's bindings table defines SHALL be followed INTO
  that table's own expression and SHALL move exactly when that expression
  does, so a quantity reaching a moving source only through a shared
  subexpression moves exactly as one naming it directly does.

The arithmetic SHALL be unchanged: the same nodes, in the same order,
through the same operators and the same function table, on the same
operand values. A quantity's value at any point of a path SHALL therefore
be the SAME FLOAT, bit for bit, that evaluating its whole expression at
that point gives. This requirement changes what the viewer COMPUTES TWICE
and SHALL change no crossing, no landing, no branch reading, no
increment, no stop, no refusal and no committed value.

A quantity's standing part SHALL belong to ONE piece. A piece SHALL be
identified so that no value computed under one piece's branches can be
read back under another's, and nothing decided for a step SHALL outlive
that step: there SHALL be no cache across steps and therefore no
condition under which one goes stale.

Resolving a QUALIFIED id while following a path SHALL read the run's bank
by that id whole. This is the same number the whole-expression walk
reaches by member access at every segment, because a program whose
identifiers could make the two disagree — one id a strict prefix of
another — is already refused when the document is loaded, under the
requirement "A program the viewer cannot execute is refused by name".

The saving SHALL be structural and unconditional. No declaration, option,
tolerance, cache size or sampling count SHALL be introduced; nothing an
author writes and no host call SHALL select it; no document field SHALL
be read for it and no document version or viewer API version SHALL move
for it. A machine whose laws are small, or whose followed quantities move
entirely, SHALL be no slower for it than the cost of deciding, once per
followed quantity per step, which of its nodes move.

The COUNT of points a step evaluates SHALL NOT change: the same search,
the same sub-interval count, the same tolerances and the same rounds.
What falls is the work inside one point, and the widget SHALL report that
work to its own tests through the subexpression-resolution probe it
already exposes, so the fall is asserted as work performed and never as
elapsed time.

#### Scenario: A searched crossing evaluates only the moving part of the law

- **WHEN** a running document's law reads the coordinate it drives
  through a skeleton the producer did not publish as affine, and that law
  also reads sibling coordinates the step does not move, so that most of
  its expression stands
- **THEN** the crossing is located by the same sampled search, at the
  same sub-interval count, the same tolerance and the same number of
  rounds, and the node visits the step performs inside that search fall
  by the share of the expression that stands

#### Scenario: Every value the machine commits is unchanged

- **WHEN** such a machine is stepped for dozens of steps, idle and moving
- **THEN** every banked coordinate, every recorded crossing, every
  landing and every stop is the value it was before this requirement, bit
  for bit, and every scenario of the conformance corpus replays

#### Scenario: A quantity that moves entirely is evaluated whole

- **WHEN** a followed quantity reads only names the step moves, so that
  nothing in it stands
- **THEN** every point evaluates the whole expression exactly as before,
  and the step pays the decision of which nodes move once for that
  quantity rather than once per point

#### Scenario: A branch reading holds for its own piece and no other

- **WHEN** a step's path is cut into several pieces and a jump node reads
  a different branch on each
- **THEN** the standing part is computed again for each piece under that
  piece's own branches, and no value computed under one piece's branches
  is read back under another's

#### Scenario: A qualified id is read whole

- **WHEN** a followed quantity names a coordinate whose id has several
  dotted segments
- **THEN** it reads the value the bank holds under that whole id, which
  is the value the whole-expression walk reaches by member access, and no
  nested scope is built for that point

### Requirement: A piecewise-affine quantity is cut at its own kinks

Following a quantity along a step's path, the viewer decides between
SOLVING it — determining it everywhere on a stretch from that stretch's
two endpoint values — and SEARCHING it, by sampling the published number
of sub-intervals and bisecting. The producer publishes, per driven end of
a law and per jump level, whether that quantity is AFFINE in its sources;
that flag is TWO-VALUED and says nothing about a quantity that is not
affine.

A quantity built over the CONTINUOUS SELECTIONS of the expression
vocabulary — `abs`, `min` and `max`, each of which returns one of its
operands exactly and is continuous where the operands meet — is PIECEWISE
AFFINE: affine on each stretch between the points where it changes which
operand it returns. The viewer SHALL recognise such a quantity FROM THE
PUBLISHED EXPRESSION ITSELF and SHALL solve it on those stretches rather
than search it. No document field is read for this, no document version
and no viewer API version moves for it, and nothing an author writes, no
host call, no option and no tolerance selects it.

**The classification SHALL be structural, conservative, and decided per
published quantity rather than per step.** A number and a jump node's
branch placeholder are CONSTANT; a source name is AFFINE; a name the
document's bindings table defines takes the shape of that table's own
expression; a unary minus, a sum, a difference, a product with a constant
operand and a division by a constant take the shape of their moving
operand and are KINKED exactly when it is; one of the three continuous
selections over operands that are each constant, affine or kinked is
KINKED; everything else — another call, a power, a product of two moving
operands, a moving divisor, a comparison — is UNCLASSIFIED and SHALL go
on being searched. A continuous selection over a CURVED operand SHALL
therefore stay unclassified, even where one of its pieces happens to be
straight.

**The viewer's classification SHALL agree with the flag the producer
publishes.** A quantity the viewer finds constant or affine SHALL be one
the producer published as affine, and a quantity the viewer finds kinked
or unclassified SHALL be one the producer published as not affine. The
viewer SHALL NOT weaken what the producer published: a quantity published
affine SHALL be solved over the whole stretch as it already was.

**A kink's own breakpoints SHALL be SOLVED, never sampled.** A continuous
selection has a level quantity of its own — the argument of `abs`, and
the difference of the two operands of `min` and `max` — whose single
surface, at zero, is where it changes which operand it returns. Over a
stretch those breakpoints SHALL be located by taking the kinks in the
expression's own postorder, so that a kink nested inside another's level
is cut first; by evaluating each kink's level at the two ends of each
sub-interval the earlier kinks have already produced, where that level is
affine in the fraction and its zero is therefore one division; by keeping
only a zero that lies strictly inside its sub-interval and strictly
between the two end values; and by folding the result into the
sub-division under the SAME crossing tolerance two crossings are folded
under. No sampling, no bisection and NO FURTHER TOLERANCE SHALL be
introduced. A level that does not move over a sub-interval reaches
nothing inside it.

**A kink breakpoint SHALL NOT be a crossing.** The quantity is continuous
there. A breakpoint SHALL NOT be recorded among a step's crossings, SHALL
NOT enter any partition an increment is summed over, SHALL NOT place a
coordinate at the far side of a surface, and SHALL NOT count toward the
published crossing maximum. It exists only as a sub-division inside a
solve, and this is what keeps every answer that did not sit on a
reclassified quantity bit-identical.

**A stop SHALL be solved on a kinked determiner.** Where a coordinate's
determining law is piecewise affine, the fraction of the stretch at which
it reaches a declared bound SHALL be located by bracketing the bound
between two consecutive breakpoints and dividing, and not by sampling.
Where such a law carries a jump plan, the breakpoints are the union of
that plan's own partition and the skeleton's kinks, the kinks located
inside each piece of the partition with that piece's branch readings
substituted, because a branch placeholder is constant only within its own
piece. Where such a law carries NO jump plan at all — the shape that
otherwise divides once over the whole step and so reports a stop where
the coordinate never was — the breakpoints are its own kinks over the
step as one piece. Where a kinked law reaches no kink over a step, there
are no breakpoints, the path IS affine over the whole step, and the
single division SHALL be taken exactly as it is for an affine law.

A stop on a coordinate a BLOCK determines SHALL still be searched: a
block has no single published expression until a branch vector is fixed,
and the order its members run in may differ from piece to piece. This
requirement does not lift that, and a bound that READS OTHER COORDINATES
SHALL go on being examined exactly as the requirement "A declared bound
may read other coordinates" states.

Nothing else SHALL move. Every banked value, every recorded crossing,
every landing, every stop, every command outcome and every refusal of a
machine none of whose followed quantities is reclassified SHALL be the
value it was, bit for bit, and the count of points such a machine
evaluates SHALL NOT change.

#### Scenario: A stop on a kinked determiner with no jump plan is solved

- **WHEN** a coordinate's only determining law carries no jump node at
  all, its expression clamps a source into a window, a declared bound
  lies on the sloped piece and the step's path starts on the flat one
- **THEN** the stop is located at the fraction the bracketing division
  gives over the piece the bound lies in, which is the producer's own
  recorded fraction, and not at the fraction a single division over the
  whole step would give

#### Scenario: A kinked level's crossing is solved rather than searched

- **WHEN** a jump node's level quantity is built over a continuous
  selection and the step's path crosses one of that node's surfaces
- **THEN** the crossing is located by solving on the sub-interval between
  the level's own kinks, and the surface lying exactly on an interior
  breakpoint is located once and not twice

#### Scenario: A kink breakpoint is not recorded as a crossing

- **WHEN** a step's path passes a breakpoint of a kinked quantity
- **THEN** no crossing is recorded there, no coordinate is placed at a
  far side, the increment is summed over the same pieces as before, and
  the breakpoint counts toward no published limit

#### Scenario: A curved quantity is still searched

- **WHEN** a followed quantity is a continuous selection over a curved
  operand, a product of two moving operands, or a quantity divided by a
  moving one
- **THEN** it is sampled and bisected exactly as before, at the same
  sub-interval count, the same tolerance and the same number of rounds

#### Scenario: A machine with no kink pays nothing

- **WHEN** a machine none of whose followed quantities is piecewise
  affine is stepped
- **THEN** every value it commits is unchanged bit for bit and the number
  of subexpression resolutions it performs per step is unchanged exactly

#### Scenario: The classification agrees with the published flag

- **WHEN** every law's driven end and every jump level of a published
  document is classified by the viewer
- **THEN** the quantities it finds constant or affine are exactly those
  the document publishes as affine, and no quantity it finds kinked or
  unclassified is published as affine

