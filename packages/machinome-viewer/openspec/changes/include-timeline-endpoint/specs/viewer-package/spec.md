## MODIFIED Requirements

### Requirement: The host chooses how animation is presented

For a model with `$t` operations, the viewer SHALL present animation as an
always-visible inline play/pause and `0..1` timeline with `frames` inclusive
scrub positions, the same bar behind an initially collapsed accessible toggle,
no controls, or externally driven time with no controls. Both zero and one
SHALL be reachable timeline values; when `frames > 1`, adjacent positions SHALL
be separated by `1 / (frames - 1)`. The host SHALL set initial time and
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
