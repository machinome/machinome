## ADDED Requirements

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

## MODIFIED Requirements

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
above.

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
