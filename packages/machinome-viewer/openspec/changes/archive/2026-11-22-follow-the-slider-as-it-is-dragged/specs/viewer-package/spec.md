## MODIFIED Requirements

### Requirement: A maker operates a clocked machine on screen

For a document carrying a clocked machine, the viewer SHALL present the
focused layer's declared inputs as HANDLES and its declared states as
follow-only READOUTS.

Each input's handle SHALL show where the input stands, in design units,
and SHALL offer a way to move it to another value. Every such gesture other
than a DRAG of the input's slider SHALL submit exactly ONE request to move
that input TO the value the gesture names, and SHALL report that request's
outcome where the gesture was made — the travel admitted, the STOPS that
truncated it named by coordinate and side, or the refusal's own message; a
drag SHALL submit the requests and report the outcome stated below. A
gesture an interlock
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

A gesture on a HANDLE, other than the positions a drag FOLLOWS, SHALL be ONE
request, and the transition that request reports SHALL BE DRAWN under the requirement "The viewer plays a clocked
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

A DRAG is a pointer pressed on a ranged input's slider and moved while it is
held. A PRESS begins when the pointer's primary button or contact goes down on
the slider while no clock's transport is playing, and lasts until it ends as
stated below. While a press lasts, each
value the slider reports is a POSITION, and the thumb SHALL stay where the
pointer puts it. A position SHALL be DRAWN, as one request under the paragraph
above, when it is the first position of its press and either the pointer had
not moved since the press began — the slider placed its thumb where a press on
its track landed — or the input, as the model showed it at the press, stood
outside the slider's range. Every other position SHALL be FOLLOWED: the viewer
SHALL ask the machine for it in ONE request, posed at once and not drawn, so
that the model, the handle's reading and the readouts of the states its
commits write show the machine's answer no later than the next animation
frame. The viewer SHALL submit at most one followed request per animation
frame, for the latest position the thumb has reached; SHALL NOT submit two in
succession for one position; and SHALL NOT leave the last position of a press
unasked. A thumb held still SHALL submit nothing and draw nothing. The
positions that come while a press's own drawn position is being drawn SHALL
wait until that drawing lands, and the latest of them SHALL then be followed.

A press SHALL end when its pointer is let go, wherever it is let go; when the
pointer is cancelled or the slider loses it; when a key is pressed on the
slider; and when another slider is pressed. The window losing focus or the
page being hidden SHALL NOT end it. No release event SHALL be needed for any of these. When a
press ends, its last position SHALL be asked if it has not been, once any
drawing of its own position has landed; nothing further SHALL be asked or
drawn for that gesture; and the thumb SHALL stand where the machine stands,
pinned at an end where that lies outside the range. While a press lasts the
panel SHALL NOT be replaced: the slider the pointer holds SHALL remain the
element it holds, and SHALL keep the focus after the press ends. The handle
SHALL report a drag as a whole: the travel the machine admitted from where the
input stood at the press, with the stops of its latest request, or that
request's refusal. A stop or a refusal repeated by later positions SHALL leave
the report as it stands.

A drag is a sequence of requests, each admitted or refused by the machine as
the one before it left it, and the bank a drag leaves SHALL be the bank that
sequence leaves. For a travel in one direction that is the bank one request to
the last position leaves; a hand that crosses a commit's level back and forth
fires that commit at every crossing the machine fires on that path; and a drag
can be admitted step by step where one request for the same travel would be
refused whole.

While the clock's transport plays, where the machine declares a clock, no
press SHALL begin, and a slider's gesture is then the one request this
requirement states for a gesture that is not a drag. Anything that would
move or repose the machine or replace the panel while a press lasts — a typed
value, a nudge, a pressed instruction, a request, restore, reset, trigger or
clock start from the host's own handle, a change of focus, a reload, or an
in-place update that keeps the machine — SHALL end the press first, its last
position asked before that thing acts, and a slider that thing replaces SHALL
submit nothing afterwards. A press whose machine is replaced by a republish,
or whose viewer is disposed, SHALL end with nothing more asked of any machine.

A handle SHALL stay usable while a drawing runs; a gesture on one LANDS the
running drawing and then draws its own, so repeated gestures give consecutive
transitions, each drawn. A followed position lands a running drawing and is
posed; the positions after a press's own drawn position wait for it, as stated
above. A gesture whose request admits no travel and commits
nothing SHALL draw nothing and SHALL report its outcome exactly as it does now.

A control a maker is EDITING SHALL NOT be rewritten by a drawing that is
running; every other handle and readout follows it. A slider a pointer holds
is a control a maker is editing.

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

- **WHEN** a maker clicks a ranged input's slider's track away from the thumb
  and lets go without moving, or moves the slider with the keyboard
- **THEN** the one request that gesture makes is drawn from where the input
  stood to where the gesture put it, rather than posed in a single frame, and a
  click on the track is drawn from the moment the pointer goes down

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

#### Scenario: A dragged slider is followed

- **WHEN** a maker presses a ranged input's slider on its thumb and drags it
- **THEN** in every animation frame in which the thumb has moved, the machine
  stands at the thumb's position, the model and the handle's reading show it,
  the readouts show the states its commits wrote, the thumb stays under the
  pointer, and nothing is drawn between one position and the next

#### Scenario: Letting go asks nothing more

- **WHEN** the maker lets the dragged thumb go
- **THEN** no request is made beyond the last position the thumb reached and
  nothing further is drawn, the slider is the element that was pressed and keeps
  the focus, and the handle reports the travel the drag admitted

#### Scenario: A thumb held still costs nothing

- **WHEN** a maker holds a dragged thumb still
- **THEN** no request is made and nothing is drawn for as long as it stays

#### Scenario: A fast hand is not queued

- **WHEN** the thumb reaches several positions before the next animation frame,
  or a request takes longer than a frame
- **THEN** one request is made in that frame, for the latest position, and the
  position the thumb ends at is asked no later than the end of the press

#### Scenario: A drag pushed past a stop

- **WHEN** a maker drags a thumb past where an interlock stops the input
- **THEN** the model and the handle's reading stand at the stop while the thumb
  stays under the pointer, the handle reports the travel admitted and the stop
  without the panel being replaced, and when the thumb is let go it moves to
  where the machine stands

#### Scenario: A refused position leaves the last admitted one

- **WHEN** a position the thumb reaches is refused by the machine
- **THEN** the model, the reading and the readouts stand where the last
  admitted position put them, the handle reports the refusal once however many
  later positions are refused, and when the thumb is let go it moves to where
  the machine stands

#### Scenario: A press on the track and then a drag

- **WHEN** a maker presses a slider's track away from the thumb and drags without
  letting go
- **THEN** the jump to where the press landed is drawn from where the input
  stood, the thumb stays under the pointer, and once that drawing lands the
  machine follows the thumb

#### Scenario: A press on a pinned thumb

- **WHEN** an input stands outside its slider's range and a maker drags the
  thumb pinned at the range's end
- **THEN** the first position is drawn from where the input stood, and the
  positions after it are followed once that drawing lands

#### Scenario: A press that ends with no release

- **WHEN** a press is cancelled or the slider loses the pointer while a thumb is
  dragged
- **THEN** the machine stands at the last position the thumb reached, nothing
  more is asked, and the thumb stands where the machine stands

#### Scenario: Another authority ends the drag first

- **WHEN** a host requests, restores, resets or triggers through its handle,
  or the maker types a value, nudges or presses an instruction, while a thumb is
  dragged
- **THEN** the drag's last position is asked first, the other thing then acts
  on the bank it left, and the slider the pointer held asks nothing more

#### Scenario: A replaced machine is asked nothing

- **WHEN** the document is republished with another machine, or the viewer is
  disposed, while a thumb is dragged
- **THEN** no request from that drag reaches any machine

#### Scenario: A window that loses focus does not end a drag

- **WHEN** the window loses focus, or the page is hidden and shown again, while a
  maker still holds a dragged thumb
- **THEN** the positions the thumb reaches afterwards are followed as before

#### Scenario: Whole-number and scaled inputs are dragged in design units

- **WHEN** a maker drags the slider of an input declared as a whole number, or of
  an input whose design units are scaled from its native ones
- **THEN** every position asked is a whole number of design units for the first,
  the machine holds the native value of each design position for the second, and
  the reading shows the design value

#### Scenario: A drag across a commit is the requests it made

- **WHEN** a maker drags a thumb back and forth across the level at which a
  commit fires
- **THEN** the commit fires at every crossing the machine fires on that path,
  and the bank is the one that drag's requests leave, which can differ from the
  bank of one request to the last position

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
where the document states none. A position a DRAGGED slider follows under that
requirement SHALL NOT be drawn: it is one request posed at once, as a request
on the mount handle is. A PRESSED instruction SHALL still be drawn over
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

- **WHEN** a maker's gesture on a handle, other than a position a dragged
  slider follows, makes a request that travels
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
