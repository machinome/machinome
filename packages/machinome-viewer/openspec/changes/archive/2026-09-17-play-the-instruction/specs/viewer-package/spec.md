## ADDED Requirements

### Requirement: The viewer plays a clocked instruction as one drawn transition

A clocked machine's document publishes its declared instructions, each naming
exactly ONE driver — a travel from where it stands, or a value to land on,
in that driver's design units — and a DURATION in seconds. The machine gives
the duration no meaning; it is how long a consumer draws the transition.

The viewer SHALL PLAY such an instruction. Triggering one by name on the
machine SHALL make the ONE REQUEST the instruction states, through the same
executor every other request goes through and under the requirement "The
viewer executes a clocked machine's requests", SHALL return that request, and
SHALL then DRAW the transition the request describes over the declared
duration.

The machine SHALL be solved exactly ONCE per press, BEFORE the first frame of
the drawing. The bank SHALL be FINAL from the moment the request is made: a
readback taken while the drawing runs SHALL report the transition's END, and
NO FURTHER REQUEST SHALL be made by the drawing. What a frame of a drawing
costs SHALL be a POSE and nothing else.

At each frame the viewer SHALL pose the tree from the bank the machine stood
at BEFORE the request, with

- the moved input at the value the elapsed FRACTION of the duration places
  between the two ends the request reports, and
- every commit whose reported fraction is at or before that fraction applied,
  in the order the request reports them, at the values it reports.

The fraction SHALL be what decides which commits are applied, so a transition
that runs DOWNWARD is drawn by the same rule as one that runs upward and the
rounding of a drawn value can neither anticipate a commit nor delay one. The
LAST frame SHALL stand at the request's own reported end with every commit
applied, so the bank the drawing finishes on and the bank the machine holds
are the same values. An input declared as a whole number SHALL be whole at
every frame and SHALL never pass the end the machine reported.

A request the machine STOPPED SHALL be drawn only as far as the machine went,
and the control SHALL report the stop as it does for any other request. A
request that admitted ZERO travel SHALL draw nothing and SHALL report its
stop. A duration of zero SHALL land at once, in one pose. An instruction the
machine REFUSES SHALL draw nothing, SHALL leave the bank and the pose exactly
as they stood, and SHALL report the refusal where it was pressed. Triggering
a name the document does not declare SHALL be refused listing the declared
names.

A drawing SHALL be the only thing posing the machine while it runs. Any other
thing that would move or repose the machine — another instruction, a gesture
on a handle, a request from the host's own handle, a snapshot restore, a reset
— SHALL LAND the drawing first, the drawn pose taking the transition's end,
and then act. Triggering while a drawing runs SHALL therefore land that
drawing and draw the new one, so two presses give two transitions. Starting a
drawing SHALL stop the clock's transport where the machine declares a clock,
the two being two authorities over one pose.

#### Scenario: A press draws the transition the machine solved

- **WHEN** a maker presses an instruction that turns a clocked machine's
  crank one whole turn over two seconds
- **THEN** the crank's value rises through successive frames for those two
  seconds and the geometry follows it, while a readback of the bank reports
  the whole turn from the first frame

#### Scenario: A commit is drawn at the frame the transition reaches it

- **WHEN** the transition carries a commit partway along the path
- **THEN** the parts that commit writes are posed at their new values from
  the first frame whose fraction reaches it, and at their old values in
  every frame before it

#### Scenario: The drawing lands on the machine's own bank

- **WHEN** a drawing finishes
- **THEN** the pose stands at the request's reported end with every commit
  applied, value for value the bank the machine has held since the request
  was made

#### Scenario: One press is one solve

- **WHEN** a drawing of many frames runs to its end
- **THEN** exactly one request was made, before the first frame, and the
  bank read at every frame of the drawing is the same bank

#### Scenario: A stopped instruction is drawn only as far as the machine went

- **WHEN** an interlock clips the request an instruction makes
- **THEN** the drawing ends at the landing the stop gave it, the control
  reports the stop by coordinate and side beside the travel admitted, and
  nothing is drawn beyond it

#### Scenario: An instruction an interlock holds draws nothing

- **WHEN** an instruction's request is admitted at zero travel
- **THEN** nothing moves, the control reports the stop that held it, and no
  drawing runs

#### Scenario: A zero-duration instruction lands at once

- **WHEN** an instruction declaring a duration of zero is pressed
- **THEN** the machine stands at the transition's end in one pose, with no
  frames between

#### Scenario: A second press lands the first drawing

- **WHEN** a maker presses the same instruction twice in quick succession
- **THEN** the first drawing lands at its own end, the second request is
  made from there, and the machine has made both transitions

#### Scenario: Another gesture lands the drawing

- **WHEN** a maker moves a handle, or a host restores a snapshot, while a
  drawing is running
- **THEN** the drawing lands first and the gesture acts on the machine as it
  stands, rather than two things posing the tree at once

#### Scenario: A refused instruction draws nothing

- **WHEN** an instruction's request is refused by the machine, or a name
  nothing declares is triggered
- **THEN** the refusal is reported where it was pressed, listing the declared
  names where the name was unknown, and the bank, the pose and the model
  stand exactly as they did

## MODIFIED Requirements

### Requirement: The viewer executes a clocked machine's requests

A version 8 document carries a compiled CLOCKED machine: a bank of every
declared driver and every declared state at its published default, plus
the clock at zero where the machine declares one, and a set of committing
relations each naming the inputs it moves with, the event level it fires
on, and one law per value it writes.

The viewer SHALL hold that bank, SHALL expose it and the machine's
identity on the mount handle, and SHALL accept a REQUEST that moves ONE
input — a declared driver, or the machine's CLOCK where it declares one,
under the clock requirement below — along a straight path from where it
stands to a stated
value. The value a request names and the travel it reports SHALL both be
in that input's DESIGN units, whatever units the bank holds it in.
Executing a request SHALL, without posing anything until it is done:

- clip the path at every stop the machine declares, under the stop
  requirement below, before locating any event;
- examine every committing relation whose published shapes name the
  moving input, and no others;
- locate every crossing of that relation's event level on the path,
  taking both ends of the path, solving an `affine` level by division and
  cutting a `kinked` level at its own breakpoints before solving each
  piece, and merging crossings no further apart than the machine's
  published crossing tolerance;
- refuse the request when one relation's level crosses more surfaces than
  the machine's published maximum;
- land each crossing on the nearest representable value on the FAR side
  of the surface, deciding membership by reading the level's branch there
  and never by comparing a value to the surface;
- fire a crossing only where the branch RISES between the piece the path
  came from and the landing, and only where the landing lies on the
  request's own path — a landing one representable value beyond the
  request's end belongs to the next request and SHALL NOT fire here,
  while a request resuming from its own landing SHALL fire nothing;
- treat two relations as ONE event exactly when their landings are the
  SAME value, and otherwise as two events in path order;
- read, at each event, every firing relation's sources from the bank as it
  stood BEFORE that event with the moving input at the landing, so the
  order of relations at one event is not observable;
- refuse the request naming the value, both relations and the landing
  when two relations write one value at one event;
- write every firing relation's results together, advance the input to the
  landing, and locate the next event from there, so an event level that
  reads a value the machine just wrote moves with it;
- round a target whose declared type is a whole number to the nearest
  whole number ONCE, taking an exact half to the EVEN one, and apply no
  scaling to a committed value;
- refuse the request when a law produces a value that is not finite.

The request SHALL then pose the tree ONCE from the resulting bank, and
SHALL report the travel it admitted, BOTH ENDS OF THE PATH IT TRAVELLED,
the stops that truncated it, and the
events it fired, each with the relations that fired it, the fraction of
the path, the input's value there and the values written.

The two ENDS SHALL be the value the moving input stood at when the request
began and the value it ended at, each taken VERBATIM from the bank and
therefore in that input's own NATIVE units — the units each event's value
speaks — so that every event's value lies on the segment they span. Neither
end SHALL be left for a caller to recompute: the admitted travel is in DESIGN
units, and a caller reconstructing an end by arithmetic could land on a value
the machine never stood at and so read a fired event as unfired. A request
that a stop truncated SHALL report as its second end the landing the stop
gave it, and one admitted at zero travel SHALL report its two ends equal.

A request the viewer refuses for any reason SHALL leave the bank, the
pose and the model exactly as they stood.

The viewer SHALL provide session control over that bank: a SNAPSHOT of
where the machine stands, a RESTORE of one taken against the SAME
machine — refused by name against another, judged by the machine's
published identity — and a RESET to every published default.

#### Scenario: A request commits what the machine writes

- **WHEN** a host requests that a clocked machine's crank move by one full
  turn, and the machine commits its register at the end of a stroke
- **THEN** the register's new value stands in the bank, the model is posed
  with it, and the request reports one event with the crank's value there

#### Scenario: Several events on one path fire in path order

- **WHEN** a host requests a travel long enough to cross ten event
  surfaces
- **THEN** ten events are reported in path order, each one reading what
  the events before it wrote

#### Scenario: Two relations landing on one value are one event

- **WHEN** two committing relations of one machine land on exactly the
  same value of the moving input
- **THEN** both are reported as ONE event, and each reads the bank as it
  stood before that event rather than what the other wrote

#### Scenario: Two surfaces one representable value apart are two events

- **WHEN** two committing relations land one representable value apart
- **THEN** they are reported as TWO events in path order, and the second
  reads what the first wrote

#### Scenario: A falling step fires nothing

- **WHEN** a request crosses an event surface in the direction that lowers
  the level's branch
- **THEN** no event is reported and nothing is written

#### Scenario: Two writers at one event refuse the request

- **WHEN** two committing relations would write one value at one landing
- **THEN** the request is refused naming that value, both relations as
  they are written in the model, and the landing, and the bank stands
  where it stood

#### Scenario: An integer commit takes an exact half to the even value

- **WHEN** a law lands a whole-number state on an exact half
- **THEN** the value banked is the nearest EVEN whole number, not the one
  a rounding toward positive infinity would give

#### Scenario: A request is refused whole

- **WHEN** a request would produce a value that is not finite, or crosses
  more surfaces than the machine admits
- **THEN** the request is refused naming what happened, and the bank, the
  pose and the model are exactly as they were before it

#### Scenario: A bank is restored only onto the machine it was taken from

- **WHEN** a host restores a snapshot taken against a different clocked
  machine
- **THEN** the restore is refused naming the two identities, and the
  machine stands where it stood

#### Scenario: A request reports both ends of the path it travelled

- **WHEN** a request is made BY a travel over an input standing away from
  zero, and another is clipped at a declared stop
- **THEN** each reports the value the input stood at before it and the value
  it stands at after it, both equal to the bank's own entries before and
  after, every event's value lies between them, and the clipped request's
  second end is the landing the stop gave it rather than the value asked for

### Requirement: A clocked machine the viewer cannot execute is refused by name

A document this viewer cannot execute SHALL be refused rather than
rendered in part, and the refusal SHALL name what the document carries.

The viewer SHALL refuse at load, naming the offending key and value: a
version 8 document carrying no clocked machine; a clocked machine missing
any of its published keys, or carrying one of the wrong type; a
committing relation whose event level names a primitive this viewer does
not implement, whose shapes name a classification it does not implement,
or whose laws do not align with the values it writes; a compiled
constraint missing a published key, naming a side that is neither low nor
high, carrying a jump plan or a classification this viewer does not
implement, or naming the machine's CLOCK anywhere in what it bounds or what
can move it; a states table that is not a table of declarations, or one
whose names collide with the declared drivers or with the machine's clock;
an expression naming an
identifier neither table nor the machine's own reserved names declare.

It SHALL refuse at load, in the same place and by the same naming, an
INSTRUCTION this viewer could not play: one stating neither a travel nor a
target or both, one naming no driver or more than one, one naming something
the drivers table does not declare — a state, the machine's clock, or a name
nothing declares — or one whose duration is not a finite number of seconds at
or above zero. A producer's own compile refuses each of these before a
document exists, so a document carrying one is a document this viewer cannot
trust to say what a press means, and every instruction a loaded version 8
document carries is one a maker may press.

The viewer SHALL refuse a REQUEST, leaving the document loaded and the
model posed, when the request names a CLOCK on a machine that declares
none, when a TRIGGER names an instruction the document does not declare —
listing the declared names — and when a host asks a clocked machine for a
cadence it does not have: a rate, or a step of a run. A request
that ADVANCES a declared clock is not such a refusal and SHALL be executed
under the clock requirement above; neither is a TRIGGER of a declared
instruction, which is executed under the requirement "The viewer plays a
clocked instruction as one drawn transition".

#### Scenario: A malformed clocked machine is refused by name

- **WHEN** a mounted version 8 document's clocked machine carries a
  relation whose event level names a primitive this viewer does not
  implement
- **THEN** mounting fails naming that relation as it is written in the
  model and the primitive, rather than executing a machine it does not
  understand

#### Scenario: A request on a clock the machine has not got is refused

- **WHEN** a host requests that a clocked machine which declares no time base
  advance a clock
- **THEN** the request is refused naming the inputs the machine does declare,
  the document stays loaded, and the model stays posed at the bank it
  already showed

#### Scenario: A cadence a clocked machine does not have is refused

- **WHEN** a host asks a clocked machine to run at a rate, or to step a
  run
- **THEN** the call is refused naming what was asked and what a clocked
  machine offers instead, and nothing about the machine changes

#### Scenario: An instruction this viewer could not play is refused at load

- **WHEN** a mounted version 8 document declares an instruction naming two
  drivers, or one naming a state
- **THEN** mounting fails naming that instruction and what it names, rather
  than listing a button whose meaning the viewer would have to guess

#### Scenario: A trigger of a name nothing declares is refused

- **WHEN** a host triggers an instruction name the document does not carry
- **THEN** the call is refused listing the declared instruction names, the
  document stays loaded, and the model stays posed at the bank it showed

### Requirement: The two runtimes agree on the clocked corpus

The producer publishes a clocked conformance corpus: one document per
machine, embedded verbatim, a script of requests, TRIGGERS of declared
instructions, and session operations,
and — per step — the whole bank afterwards, the travel admitted, BOTH ENDS
OF THE PATH, the
events fired with their landings and the values written, and, for a step
the producer refused, the KIND of refusal and the qualified names its
message carries.

The package SHALL carry that corpus as the producer generated it, byte
for byte, and SHALL replay it. Agreement SHALL be EXACT: every recorded
number SHALL be reproduced bit for bit, and the tolerance compared
against SHALL be the one the corpus file itself states rather than one
the reader chooses. A disagreement SHALL be treated as a defect of this
engine, and SHALL NOT be answered by widening a comparison, editing the
fixture or omitting a scenario.

The replay SHALL load and execute EVERY machine of the corpus and EVERY
step of every script, and SHALL compare, per step, the whole bank, the
travel admitted, BOTH ENDS OF THE PATH, the events fired, the STOPS met and
the refusals by kind
and by name. No step SHALL be departed from, deferred or passed over: a
request that advances a machine's CLOCK is replayed exactly as a request on
a driver is, and so is a step that TRIGGERS a declared instruction — what
the instruction MEANS is part of the contract, not merely that the name was
accepted.

A CENSUS of the machines, the steps and the recorded numbers SHALL be
asserted and SHALL be DERIVED from the corpus file itself rather than from a
list maintained by hand, so a corpus regenerated wider or narrower than the
one this build was written against fails loudly here without anyone running
the producer's generator. The census SHALL state that every step is
replayed, so a later build cannot narrow the suite by declaring a departure
without also moving that number.

#### Scenario: The engine reproduces the producer's own numbers

- **WHEN** the corpus is replayed through this package's clocked executor
- **THEN** every recorded bank value, admitted travel, landing and written
  value is reproduced exactly, with no tolerance

#### Scenario: A refusal is matched by kind and by name

- **WHEN** the corpus records a step the producer refused
- **THEN** this engine refuses the same step with the same kind, its
  message carries every qualified name the corpus lists, and the bank
  afterwards is the one the corpus records

#### Scenario: A machine with interlocks is replayed like any other

- **WHEN** the corpus carries a machine whose clocked object declares a
  stop
- **THEN** its script is replayed step by step like every other machine's,
  and the stops it records are reproduced exactly

#### Scenario: A step that advances a clock is replayed like any other

- **WHEN** the corpus records a step that advances a machine's clock
- **THEN** its script is replayed step by step like every other machine's,
  the events it records on the clock are reproduced exactly, and the steps
  after it are compared against the bank it left

#### Scenario: A landing one representable value off is caught

- **WHEN** a recorded landing on a clock — the first release of a machine
  whose level is a function of elapsed seconds — is moved by one
  representable value
- **THEN** the replay fails, rather than accepting a value within any window

#### Scenario: A step that triggers an instruction is replayed like any other

- **WHEN** the corpus records a step that triggers a declared instruction,
  one stating a travel and one stating a target
- **THEN** each is replayed step by step like every other machine's, the
  request the instruction makes is compared field for field against the
  recorded one, and the steps after it are compared against the bank it left

#### Scenario: A triggered step and the same request by hand agree

- **WHEN** the corpus records a trigger and, from the same restored bank,
  the request that instruction states made by hand
- **THEN** this engine reproduces both, and the two recorded results are the
  same values — the same ends, the same admitted travel and the same events

#### Scenario: A regenerated corpus is loud

- **WHEN** a corpus is copied in carrying more machines or more steps than
  this build was written against
- **THEN** the census fails naming the difference, rather than replaying a
  subset in silence

### Requirement: A maker operates a clocked machine on screen

For a document carrying a clocked machine, the viewer SHALL present the
focused layer's declared inputs as HANDLES and its declared states as
follow-only READOUTS.

Each input's handle SHALL show where the input stands, in design units,
and SHALL offer a way to move it to another value; every such gesture
SHALL submit exactly ONE request to move that input TO the value the
gesture names, and SHALL report that request's outcome where the gesture
was made — the travel admitted, the STOPS that truncated it named by
coordinate and side, or the refusal's own message. A gesture an interlock
holds SHALL be reported as a stop at that control rather than passed over
as a control that did nothing. A declared range SHALL be presentation only
and SHALL NOT clamp a request.

A state SHALL NOT be presented as a handle and SHALL NOT be a source of
any request; its readout SHALL follow the committed bank. A machine's
CLOCK, where it declares one, SHALL likewise be shown as a readout and
never as a positional handle; it is advanced by the transport of the
requirement "A maker runs an elapsed clocked machine on screen" and by
nothing else.

Declared instructions SHALL be listed and SHALL be PRESSABLE. A press SHALL
play that instruction under the requirement "The viewer plays a clocked
instruction as one drawn transition"; the button SHALL indicate for as long
as its drawing runs, and SHALL report the outcome where it was pressed — the
travel admitted, the stops that truncated it, or the refusal's own message —
exactly as a handle's gesture does. While a drawing runs the panel's handles
and readouts SHALL follow THE DRAWING rather than the bank, so that what a
maker reads beside the model is what the model is showing; when the drawing
lands the two are the same values again.

A gesture on a HANDLE SHALL remain ONE immediate request, posed once: a
duration is something a declared instruction states, and a handle declares
none. A handle SHALL stay usable while a drawing runs; a gesture on one lands
the drawing and then acts.

The chrome SHALL offer snapshot, restore and reset of the machine's bank.
It SHALL NOT offer a transport over the machine's DRIVERS — a clocked
machine has no cadence for one to run, step or speed — and SHALL offer the
clock's own transport exactly where the machine declares a clock. A
document's `$t` animation SHALL be presented exactly as it is for a document
carrying no machine at all, independently of the clock: the two advance
different values and neither moves the other.

#### Scenario: A maker moves an input and the machine commits

- **WHEN** a maker moves a clocked machine's crank handle to a new value
- **THEN** one request is submitted to move that input to that value, the
  model poses at the resulting bank, and the handle reports the travel
  admitted

#### Scenario: A register is read, never driven

- **WHEN** a clocked machine's focused layer declares states
- **THEN** each is shown as a readout following the committed bank, with
  no control that could move it

#### Scenario: A refused request is reported where it was made

- **WHEN** a maker's gesture submits a request the machine refuses
- **THEN** the refusal's message is shown at that control, and every
  readout still shows the bank the machine stood at

#### Scenario: A gesture an interlock holds says so at the control

- **WHEN** a maker moves a handle an interlock holds still
- **THEN** that control reports the stop by coordinate and side and the
  travel it admitted, the model does not move, and nothing is reported as
  an error

#### Scenario: A declared instruction is pressed and played

- **WHEN** a maker presses a listed instruction of a clocked document
- **THEN** the machine makes that instruction's one request, the transition
  is drawn over the declared duration, and the button indicates while it runs
  and reports the travel admitted when it lands

#### Scenario: The panel follows the drawing

- **WHEN** a drawing is running
- **THEN** the moved handle's reading and the readouts of the states its
  commits write follow what the model is showing, frame by frame, and stand
  at the machine's own bank when the drawing lands

#### Scenario: A clocked model animates while its bank stands

- **WHEN** a clocked document carries geometry that is a formula of `$t`
- **THEN** the timeline plays it exactly as it does for a document
  carrying no machine, and the bank stands throughout

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

That ramp is what an instruction means for a document the viewer POSES from
its driver table. For a document carrying a CLOCKED machine the handle's own
`trigger` SHALL be REFUSED by name, saying that a clocked machine's
instructions are played on the machine and pointing at it: such a document is
posed from the machine's BANK, so a ramp over the driver table would move
nothing a maker could see.

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

#### Scenario: A posed trigger on a clocked document is refused

- **WHEN** a host calls the viewer handle's own `trigger` on a document
  carrying a clocked machine
- **THEN** the call is refused naming the machine's own trigger as the way
  to play that instruction, and no ramp is started

### Requirement: The viewer declares its API version

The package SHALL declare one API version, expose it on every mount handle and
the browser global, and make it readable without executing the bundle. It SHALL
be raised whenever the mount interface or handle changes incompatibly, and when
a capability a host may require is added. The declared version SHALL be 19,
reflecting the PLAYING of a clocked machine's declared instruction — one
request solved before the first frame and its transition drawn over the
declared duration, where a build at the previous version lists the same
instruction and refuses it — on top of
the advance of a clocked machine's CLOCK,
of the execution of a clocked machine's requests, of the
ordering of a block of the compiled program once per piece of a step, and of the execution of a law that reads the coordinate it drives, the
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

#### Scenario: A host requires a clocked machine executed

- **WHEN** a host means to present a machine with MEMORY and no cadence —
  a calculator whose registers are written at the end of a stroke — which
  the producer publishes as a version 8 document
- **THEN** the declared API version tells it whether this bundle executes
  one, before it mounts a bundle that would refuse the document by name
  and render nothing at all

#### Scenario: A host requires a clock that runs

- **WHEN** a host means to present a machine whose motion is a function of
  ELAPSED SECONDS — a pendulum and the counter beside it — and to let a
  maker watch it run
- **THEN** the declared API version tells it whether this bundle advances a
  clocked machine's clock, before it mounts a bundle that renders the same
  document truthfully at one instant and refuses every request that would
  move it off that instant

#### Scenario: A host requires a clocked instruction played

- **WHEN** a host means to offer a maker the buttons a clocked document
  declares — "Turn crank" on a calculator that holds its registers — and to
  have the stroke WATCHED rather than jumped
- **THEN** the declared API version tells it whether this bundle plays one,
  before it mounts a bundle that lists the same instruction and refuses it

