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
SHALL pose the tree. The
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

#### Scenario: A version beyond the ones it reads is refused

- **WHEN** a host mounts a document declaring version 6
- **THEN** mounting fails naming that version and the versions the viewer
  renders

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
a capability a host may require is added to the handle. The declared version
SHALL be 9, reflecting the addition of published assembly-navigation state and
its change subscription — the handle's report of the focused root and the
hidden paths, and the notification that follows every change of the published
tree, the focused root or the visibility state — on top of version-5 document
execution.

The package SHALL also declare, in the same one place, the document schema
versions this build reads, and SHALL report them beside the API version
wherever the API version is reported. A consumer asking which documents a
viewer reads SHALL be answered with that list rather than having to infer
it from the API version, and a consumer that receives no such list SHALL be
entitled to assume the versions every released viewer reads.

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

#### Scenario: A producer asks which documents this viewer reads

- **WHEN** a producer asks the installed viewer what it reads, before
  publishing a document
- **THEN** it receives the list of document schema versions this build
  renders, including the running version, from the same declaration the
  bundle refuses by

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
increment per determined value and committing them together.

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
  endpoint values solved rather than searched; any other SHALL be sampled,
  bracketed and bisected under the published subdivision, rounding and
  tolerance limits.
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
be stopped. Each declared bound SHALL be evaluated once per step from the
committed bank, so every segment of one step is measured against the same
number.

A step SHALL be atomic across its segments: the bank, the commands'
admitted travel and the records SHALL be applied only once every segment
has succeeded. A conflict, a partition exceeding the published crossing
limit, a law that cannot be integrated over the step's path, or a stop
that stops no moving input SHALL commit nothing — the bank, the step count
and the pose stand — SHALL retire the commands that moved an input in that
step reporting that the step did not happen, and SHALL report what
disagreed, naming the relation as its author wrote it and the class that
stated it.

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
plans share; an expression, skeleton, level quantity or bound whose free
names are not among the ones that edge or bound may read; a declared bound
over a coordinate the bank does not hold; a limit that is missing or not a
finite number; a computed value the document reads that no edge
determines; a clock name that is also a coordinate or a driver id; and an
identifier set that cannot be resolved as names, such as one identifier
being a strict prefix of another.

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
stated as an expression, a command retired blocked, a rate, a run state
taken and restored, both instruction forms, and a step carrying both a
crossing and a stop — so that a narrower corpus copied in is refused here
without anyone running the producer's generator.

#### Scenario: Every scenario of the corpus replays

- **WHEN** the widget suite replays the committed corpus through the run
  engine
- **THEN** every step of every scenario matches, exactly for discrete
  state and within the stated relative tolerance for floats

#### Scenario: A narrowed corpus is refused

- **WHEN** the committed corpus is replaced by one exercising fewer of the
  stated features
- **THEN** the suite fails naming the feature no longer covered

#### Scenario: A drifted engine is caught, not tolerated

- **WHEN** the engine's arithmetic is changed so one machine's bank
  differs in the last bits beyond the corpus's tolerance
- **THEN** the suite fails naming the scenario, the step and the
  coordinate

