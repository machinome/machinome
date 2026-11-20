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

The request SHALL then pose the tree ONCE from the resulting bank — or,
where the viewer will DRAW the transition the request reports under the
requirement "The viewer plays a clocked instruction as one drawn
transition", SHALL JUDGE that pose ONCE, refusing exactly what posing it
would refuse, without showing it, the drawing showing it when it lands — and
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

The viewer SHALL draw, in the same way and by the same rule, the transition a
maker's GESTURE on a handle produces, under the requirement "A maker operates
a clocked machine on screen": one request, made once at the gesture, drawn over
the duration that requirement gives it — the tempo of a declared instruction
that states a travel on the same input, or the viewer's own short duration
where the document states none. A PRESSED instruction SHALL still be drawn over
the duration it DECLARES, whatever travel its request admits: an instruction
states its own duration and the viewer honours it, and a tempo is derived only
where nothing is declared. Everything
this requirement states about a drawing — the one solve, the bank that is final
from the request, the fraction that decides a commit, the landing, the stopped
and refused cases, and the one authority over the pose — SHALL hold for such a
drawing exactly as it does for a pressed instruction's.

A request the CLOCK'S OWN TRANSPORT makes — a played frame, or a step of a
stated number of seconds — SHALL NOT be drawn: it advances a clock the maker is
already watching, and a drawing would take the pose from the transport that
asked for it. A request made on the mount HANDLE rather than on screen SHALL
NOT be drawn either, and SHALL land at once.

The machine SHALL be solved exactly ONCE per press, BEFORE the first frame of
the drawing. The bank SHALL be FINAL from the moment the request is made: a
readback taken while the drawing runs SHALL report the transition's END, and
NO FURTHER REQUEST SHALL be made by the drawing. What a frame of a drawing
costs SHALL be a POSE and nothing else.

The pose the request ends at SHALL be JUDGED at the press, so that a request
whose final pose the viewer would refuse is refused there, and SHALL NOT be
shown. From the press until the drawing's first frame the model, every
picture rendered and the panel's handles and readouts SHALL show the
transition's ORIGIN. A press SHALL render no picture itself.

The declared duration SHALL be counted from the drawing's FIRST FRAME, which
SHALL stand at the transition's origin: the time the press itself took, and
any time that passed before that first frame, SHALL NOT be taken from the
transition. Each later frame SHALL advance the drawing by the wall seconds
since the frame before it.

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
as they stood, and SHALL report the refusal where it was pressed. This SHALL
hold whatever refused the request's final pose, an evaluator of a flexible
part included: every part, rigid or flexible, SHALL stand where it stood.
Triggering
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

#### Scenario: A handle's gesture is drawn like an instruction's press

- **WHEN** a maker's gesture on a handle makes a request that travels
- **THEN** exactly one request is made before the first frame, the transition
  is drawn frame by frame over the duration the panel gives it with each commit
  at its own fraction, and the drawing lands on the bank the machine has held
  since the gesture

#### Scenario: A gesture of the declared travel takes the declared duration

- **WHEN** a maker's gesture on a handle asks for exactly the travel a declared
  instruction states on that input, and the instruction is pressed for the same
  travel from the same bank
- **THEN** both transitions are drawn over the same duration and land on the
  same bank, the gesture and the button being two ways of asking for one stroke

#### Scenario: A step of the clock is not drawn

- **WHEN** a maker steps a clocked machine's clock by a stated number of
  seconds, or the transport advances it on a rendered frame
- **THEN** the machine poses once for that request, the transport keeps
  running where it was running, and no drawing is started

#### Scenario: A host's request lands at once

- **WHEN** a host moves an input through the mount handle
- **THEN** the machine poses once at the resulting bank and nothing is drawn,
  whatever the panel would have done for the same request


#### Scenario: Nothing shows the transition's end before the first frame

- **WHEN** a maker presses an instruction that turns a crank one whole turn
  over two seconds, and a picture is rendered or the panel is read before
  the drawing's first frame
- **THEN** the picture, the model's parts and the panel's reading all stand
  at the transition's origin, while a readback of the bank reports the whole
  turn

#### Scenario: A press renders no picture itself

- **WHEN** a maker presses an instruction of non-zero duration, or makes a
  gesture on a handle whose transition is drawn
- **THEN** nothing is rendered in the course of the press, and the first
  frame of the drawing is the next picture the viewer renders for it

#### Scenario: A slow press does not shorten the motion

- **WHEN** a press takes longer than a frame, or longer than the transition
  it plays
- **THEN** the drawing's first frame stands at the transition's origin, and
  the transition is drawn over its declared duration counted from that frame

#### Scenario: A drawn request refused by a flexible part moves nothing

- **WHEN** a drawn instruction's or gesture's request ends at a pose that the
  evaluator of a flexible part refuses
- **THEN** the refusal is reported where the request was made, the bank
  stands, and every rigid and flexible part stands exactly where it stood
