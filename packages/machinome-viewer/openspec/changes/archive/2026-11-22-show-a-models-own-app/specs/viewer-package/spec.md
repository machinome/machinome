## MODIFIED Requirements

### Requirement: The host chooses how driver controls are presented

The host SHALL be able to choose at mount time whether the on-screen
chrome (controls and focus affordance) is presented, for a posed document,
for a running one and for a CLOCKED one alike — one switch over all three
kinds. By default it is
presented for documents that declare drivers. Where the document names its
model's own app and the chrome is presented, the app SHALL be shown in place
of that chrome under the `model-app` capability, and no posed, running or
clocked panel and no animation bar SHALL be drawn; suppressing the chrome
SHALL suppress the app with it. A host that suppresses
it SHALL retain the full driving API unchanged, for a running
document the full run API unchanged, and for a clocked one the full machine
API — its requests, its session verbs and its clock — unchanged.

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

#### Scenario: A model's own app is presented in the chrome's place

- **WHEN** a maker opens, with default options, an export of a clocked
  document that names its model's app
- **THEN** the app is shown and no clocked panel, instruction button or
  animation bar of the viewer's is drawn

#### Scenario: Suppressing the chrome suppresses the app

- **WHEN** a host mounts the same document with the chrome suppressed
- **THEN** neither the app nor any panel is drawn, and the machine API is
  unchanged

### Requirement: A maker watches the model full screen

A viewer mounted with continuous rendering in a document where the browser
permits full screen SHALL present one full-screen control. The control
SHALL be a keyboard-focusable button whose accessible name says whether it
enters or exits full screen, whose title names the `f` key, and whose icon
is drawn by the package itself rather than taken from a font or a
dependency. It SHALL be placed on the control surface the viewer draws:

- at the end of the running machine's transport bar, when one is drawn;
- otherwise at the end of the inline animation timeline bar, when one is
  drawn;
- otherwise as a permanently visible overlay in the bottom-right corner of
  the viewer, for a static model, a model posed only by drivers, a clocked
  machine, and an animation presented toggled, externally or not at all;
- while a model's own app is shown, as a permanently visible overlay in the
  bottom-right corner of the picture the app places, wherever the app places
  it.

Activating the control SHALL put the viewer's full-screen root into full
screen, or take it out when it is already full screen. The full-screen root
SHALL be the element the host gave the viewer, or the whole composed layout
when the viewer is part of a layout the package mounted, so the model, its
on-screen chrome or its app, and the control all remain on screen. The
canvas SHALL follow the full-screen size on entering and return to the
container's size on leaving, or, while an app is shown, to the size of the
place the app gives the picture. While in full screen the root SHALL be
painted with the page background it was seen on (white when none is set),
not the browser's black backdrop.

The `f` key, lower or upper case, SHALL toggle full screen when it is pressed
inside the viewer's full-screen root, or when nothing on the page has focus
and this is the only viewer in that document able to go full screen. It
SHALL NOT toggle while the target is a text field, a select, a textarea or
editable content, while Ctrl, Alt or Meta is held, on key repeat, or when
another handler has already consumed the key. The viewer SHALL NOT
intercept Escape. Leaving full screen by Escape or by any other means SHALL
leave the control showing the true state.

Where the browser does not permit full screen for the document, such as an
iframe without the full-screen permission or a browser without element full
screen, the viewer SHALL present no full-screen control, the `f` key SHALL
do nothing, and nothing SHALL imitate full screen. A viewer in on-demand
render mode SHALL present no full-screen control. Disposing a viewer whose
root is full screen SHALL leave full screen first. The control SHALL carry
the stable class `machinome-fullscreen`, so a host can style or hide it.

#### Scenario: A timeline carries the button

- **WHEN** a model that reads `$t` is mounted with inline animation
- **THEN** the full-screen button is the last control on its timeline bar
  and no corner button is drawn

#### Scenario: A running machine carries it on its transport

- **WHEN** a document carrying a program is mounted
- **THEN** the full-screen button is the last control on the run transport
  bar

#### Scenario: A model without a timeline carries it in the corner

- **WHEN** a static model, a drivers-only posed model or a clocked machine
  is mounted
- **THEN** the full-screen button stands in the bottom-right corner of the
  viewer, outside any bar, and stays there

#### Scenario: The f key goes full screen and Escape comes back

- **WHEN** the maker clicks the model and presses `f`
- **THEN** the full-screen root is the document's full-screen element, the
  canvas fills the screen and the button reads "Exit full screen"
- **AND WHEN** the maker then presses Escape
- **THEN** the browser leaves full screen, the canvas returns to its
  container's size and the button reads "Full screen" again

#### Scenario: Typing is not a shortcut

- **WHEN** the maker types `f` into a value field of the viewer's panel, or
  presses Ctrl+F
- **THEN** the viewer does not change full-screen state

#### Scenario: An iframe that does not permit full screen

- **WHEN** an export is embedded in an iframe without `allowfullscreen`
- **THEN** no full-screen button is drawn and `f` does nothing

#### Scenario: Two viewers on one page

- **WHEN** a page mounts two viewers and nothing has focus
- **THEN** `f` puts neither in full screen, and `f` pressed on a control
  inside one of them toggles only that one

#### Scenario: A model's app carries it in the picture's corner

- **WHEN** a clocked document naming its model's app is mounted and the app
  places the picture above its own keyboard
- **THEN** the full-screen button stands in the bottom-right corner of the
  picture, not of the viewer's area, and activating it puts the whole app
  in full screen

## ADDED Requirements

### Requirement: A page is told when a clocked machine's bank or drawing changes

For a document carrying a clocked machine, the mount handle SHALL let a page
subscribe to the machine's changes and SHALL answer whether a drawn
transition is running. A subscriber SHALL be notified once after every
accepted operation that changes the committed bank or starts or ends a drawn
transition, whatever made it — a gesture on the viewer's panel, a call on
the machine's handle, the clock's transport, a dragged slider, the last
frame of a drawing or its landing, or a load or republish that builds,
rebuilds or keeps the machine — and SHALL NOT be notified for a refused
request. The notification SHALL mean that what the page last read may be
stale; it SHALL carry no value, and the page reads the bank and the drawing
from the handle. The subscription SHALL belong to the mount, so it SHALL
survive a republish that replaces the machine. A subscriber that throws
SHALL NOT keep the others from being notified. Disposing the viewer SHALL
drop every subscription and notify nobody. A document with no clocked
machine SHALL never notify.

#### Scenario: A drawn instruction notifies twice

- **WHEN** a page plays a declared instruction with a duration through the
  machine's handle
- **THEN** it is notified once at the request, when the handle answers that
  a transition is drawn and the bank already stands at its end, and once
  when the drawing's last frame is shown, when the handle answers that none
  is drawn

#### Scenario: A refused request notifies nobody

- **WHEN** a request is refused by the machine
- **THEN** no subscriber is notified and the bank is unchanged

#### Scenario: A republish keeps the subscription

- **WHEN** the document is republished with a changed machine and the page
  then moves the new machine
- **THEN** the page is notified of the republish and of the move, reading
  the new machine's bank

#### Scenario: The clock notifies per played frame

- **WHEN** a machine declaring a clock plays its transport
- **THEN** a subscriber is notified once for each frame the clock advanced
  in
