## ADDED Requirements

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
  machine, and an animation presented toggled, externally or not at all.

Activating the control SHALL put the viewer's full-screen root into full
screen, or take it out when it is already full screen. The full-screen root
SHALL be the element the host gave the viewer, or the whole composed layout
when the viewer is part of a layout the package mounted, so the model, its
on-screen chrome and the control all remain on screen. The canvas SHALL
follow the full-screen size on entering and return to the container's size
on leaving. While in full screen the root SHALL be painted with the page
background it was seen on (white when none is set), not the browser's
black backdrop.

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

## MODIFIED Requirements

### Requirement: The host chooses how animation is presented

For a model with `$t` operations, the viewer SHALL present animation as an
always-visible inline play/pause and `0..1` timeline with `frames` inclusive
scrub positions, the same bar behind an initially collapsed accessible toggle,
no controls, or externally driven time with no controls. When `frames > 1`,
both zero and one SHALL be reachable timeline values and adjacent positions
SHALL be separated by `1 / (frames - 1)`; a single frame SHALL expose only
zero. The host SHALL set initial time and
autoplay. Scrubbing pauses playback. Static models SHALL present no animation
controls. The full-screen control is not an animation control; where it
appears is stated by "A maker watches the model full screen".

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
- **THEN** the viewer renders that pose with no animation controls

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

