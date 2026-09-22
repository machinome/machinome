## MODIFIED Requirements

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

A gesture on a HANDLE SHALL be ONE request, and the transition that request
reports SHALL BE DRAWN under the requirement "The viewer plays a clocked
instruction as one drawn transition", exactly as a pressed instruction's is:
the machine is solved once, at the gesture, and what follows is a picture of a
transition that has already happened. A handle declares no duration, so the
viewer SHALL take one from the document where the document states one: where a
declared instruction states a TRAVEL on that same input over a duration, the
viewer SHALL draw the gesture's transition AT THAT INSTRUCTION'S TEMPO, so that
the same travel takes the same time however a maker asks for it — the duration
drawn being the declared duration in the proportion the travel admitted bears
to the travel declared. Where SEVERAL declared instructions state a travel on
one input, the FIRST the document declares SHALL be the one whose tempo the
gesture takes. Where NO declared instruction states a travel on that
input, the viewer SHALL draw the transition over ONE SHORT DURATION OF ITS OWN,
the same for every such handle and every travel, so that a gesture is watched
rather than jumped. Neither duration SHALL be scaled by the playback speed.

A gesture on an input a tempo governs SHALL take proportionally long however
far it travels, WITHOUT CAP: a maker who asks for twice the declared travel has
asked to watch twice the declared stroke, and a picture drawn at one rate for
its first half and another for the rest would be a picture of neither.

A handle SHALL stay usable while a drawing runs; a gesture on one LANDS the
running drawing and then draws its own, so repeated gestures give consecutive
transitions, each drawn. A gesture whose request admits no travel and commits
nothing SHALL draw nothing and SHALL report its outcome exactly as it does now.

A control a maker is EDITING SHALL NOT be rewritten by a drawing that is
running; every other handle and readout follows it.

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
  model is drawn from where it stood to the resulting bank, and the handle
  reports the travel admitted

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

#### Scenario: A nudge is drawn rather than jumped

- **WHEN** a maker sets a handle's nudge amount to a whole turn of a crank and
  presses the plus button
- **THEN** the crank's value rises through successive frames and the geometry
  follows it, rather than arriving in one frame, and the handle reports the
  whole turn admitted

#### Scenario: A typed value is drawn

- **WHEN** a maker types an absolute value into a handle's field and commits it
- **THEN** the transition from where the input stood to that value is drawn
  frame by frame, with every commit along the way drawn where it falls

#### Scenario: A slider's commit is drawn

- **WHEN** a maker drags a ranged input's slider and releases it, or clicks its
  track away from the thumb
- **THEN** the one request that gesture makes is drawn from where the input
  stood to where the gesture put it, rather than posed in a single frame

#### Scenario: Consecutive gestures are consecutive drawings

- **WHEN** a maker presses the same nudge button again while its drawing is
  still running
- **THEN** the first drawing lands at its own end, the second request is made
  from there, and both transitions are drawn one after the other

#### Scenario: A field a maker is editing is left alone

- **WHEN** a drawing runs while the maker's cursor is in a handle's own field
- **THEN** that field keeps what the maker typed, while the model, the other
  handles and the readouts follow the drawing

#### Scenario: A nudge is drawn at the tempo the document declares

- **WHEN** a maker nudges an input by the whole travel a declared instruction
  states for it, the instruction declaring that travel over two seconds
- **THEN** the transition is drawn over those two seconds, the same stroke the
  instruction's own button draws, rather than over the duration a handle gets
  where the document declares nothing

#### Scenario: Half the declared travel is drawn in half the declared time

- **WHEN** a maker nudges that same input by a twelfth of the declared travel
- **THEN** the transition is drawn over a twelfth of the declared duration, so
  the input moves at the rate the document declared for it whatever the
  gesture asked for

#### Scenario: An input no declared travel names keeps the viewer's own duration

- **WHEN** a maker nudges an input that no declared instruction states a travel
  on — because no instruction names it, or because the one that does states a
  landing rather than a travel
- **THEN** the transition is drawn over the viewer's own short duration, the
  same for every such gesture

#### Scenario: A stopped gesture is drawn only for the travel it admitted

- **WHEN** an interlock clips a gesture on an input a tempo governs, so the
  machine admits less travel than the gesture asked for
- **THEN** the drawing takes the declared duration in the proportion the
  ADMITTED travel bears to the declared travel, so the input is drawn at the
  declared rate and stops where the machine stopped

#### Scenario: The first declared travel gives the tempo

- **WHEN** a document declares two instructions that each state a travel on one
  input, over different durations
- **THEN** a gesture on that input is drawn at the tempo of the one the document
  declares FIRST, whatever the second states

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
