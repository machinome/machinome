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
versions 1, 2, 3 and 4, and SHALL refuse any other version naming it and
the versions it renders. A document whose `drivers`
table is empty SHALL render exactly as a version 1 document. A document
whose `drivers` table is non-empty SHALL load and render at the pose its
expressions evaluate to under the table's declared defaults, with driver
and instruction entries exposed through the handle's driving API. A
document whose expressions reference a qualified id absent from both its
`drivers` table and its `bindings` table is malformed and SHALL fail
loudly naming the id. A version 4 document carries an ordered `bindings`
table, which the viewer SHALL resolve under the binding requirements
above; a document that carries no such table SHALL be read exactly as it
was before the viewer knew of bindings. The
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

#### Scenario: A version beyond the ones it reads is refused

- **WHEN** a host mounts a document declaring version 5
- **THEN** mounting fails naming that version and the versions the viewer
  renders

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
SHALL be 7, reflecting the addition of version-4 document rendering — the
document's `bindings` table — on top of real-time playback. (The baseline
text recorded 5 while the shipped package declared 6: `real-time-playback`
raised the number in `package.json` for the speed capability without a
delta on this requirement. This revision records that correction alongside
the new capability, as the previous revision did for the driver-driving
one.)

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
exponentiation, `$t`, qualified driver ids resolved through the
driver map, and binding names resolved through the document's table —
SHALL match the producer's numeric resolution of the
same expressions to within floating-point rounding, and that agreement
SHALL be enforced by tests against the shipped evaluator module using
producer-computed expected values covering at least: linear and scaled
driver terms, degree-trig chains, `^` terms, sums whose leading term is
negative, expressions mixing `$t` with drivers, expressions that are or
contain a binding name, and design-to-native
instruction target conversion for integer dtypes.

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
flexible node's parameters and a binding's alike, so that no such
expression is first met while a frame is being rendered.

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

### Requirement: A maker drives the focused layer's drivers and instructions on screen

For a document that declares drivers, the mounted viewer SHALL present
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

The host SHALL be able to choose at mount time whether the driver
chrome (controls and focus affordance) is presented. By default it is
presented for documents that declare drivers. A host that suppresses
it SHALL retain the full driving API unchanged.

#### Scenario: A shop floor builds its own instrument panel

- **WHEN** a host mounts with the driver chrome suppressed
- **THEN** no on-screen driver control or focus affordance appears
  while `drivers()`, `setDriver`, `trigger`, and `onDriverChange`
  behave exactly as when the chrome is shown

#### Scenario: A published export shows the controls

- **WHEN** a maker opens a self-contained export of a driver-declaring
  document with default options
- **THEN** the driver chrome is presented

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
