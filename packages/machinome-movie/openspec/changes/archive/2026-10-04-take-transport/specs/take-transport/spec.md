## ADDED Requirements

### Requirement: A machine transport poses a bank on the viewer's machine

The take transport SHALL give, for a mounted viewer and the identity a take
was recorded on, a machine transport whose pose restores a whole bank on
the viewer's machine with that identity and then sets the camera it is
given (with up and field of view from Viewer API 28) or, given none, draws
the viewer again with its own camera; and which reports the bank the
viewer's machine holds. Every pose SHALL have been drawn when it returns.
It MUST refuse, before anything is restored, set or drawn, a viewer that
gives no machine for the clocked document, and a machine whose identity
differs from the take's, naming both identities and `take.identity`; the
stage SHALL prefix the refusal with the view and the shot.

#### Scenario: A pose with a camera
- **WHEN** a machine transport attached to the counter's viewer poses the
  bank with crank 1800 and units 5 and a camera on a Viewer API 29 viewer
- **THEN** the machine is restored to a copy of that bank with the
  counter's identity, the camera with its up and field of view is set
  after it, no loop time is set, and the transport reports that bank.

#### Scenario: A pose without a camera
- **WHEN** the transport poses a bank and is given no camera
- **THEN** the machine is restored, and the viewer is drawn again with the
  camera, target, up and field of view it reports, so a viewer that draws
  only on request shows the bank.

#### Scenario: Another machine
- **WHEN** the viewer's machine has another identity than the take's
- **THEN** attaching is refused naming the viewer's identity, the take's
  and `take.identity`, and nothing is restored or drawn.

#### Scenario: No machine
- **WHEN** the viewer gives no machine
- **THEN** attaching is refused naming `viewer.machine()` and Viewer API
  29, and nothing is restored or drawn.

### Requirement: A take transport seeks a clocked take by the frame's own rule

Given a viewer and a take document, the object the pose rule reads,
`{model: {expectedDurationSeconds}, marks, take}` (a movie document that
films a clocked take, or its resolution, is one), the take transport SHALL
give a transport whose `duration` is the take's length as
the document writes it, whose `marks` are the document's marks with their
take times in take-time order, and whose `seek(t)` poses, through the
machine transport, the bank the take gives at `t` clamped to the take, by
the rule the frame uses (`src/take.mjs`, imported and never copied), so a
mark poses exactly its recorded bank; `time()` SHALL report the last time
sought, 0 before any. Attaching SHALL pose nothing. It MUST refuse, naming
the field, a take that is not clocked and a time that is not a number of
seconds.

#### Scenario: Every mark on the double
- **WHEN** the transport, bundled and loaded beside the viewer double whose
  machine answers the counter's take, seeks the fixture `count` to each of
  its marks `one` (2 s), `nine` (6 s) and `ten` (8 s)
- **THEN** the machine holds, after each seek, exactly the bank the take
  records at that mark, each pose being a restore and then a camera call,
  and no loop time is set.

#### Scenario: Every mark on the real viewer
- **WHEN** the viewer layer runs with a Viewer API 29 bundle and the
  transport seeks the fixture counter's export to each mark of `count`
- **THEN** the bank the viewer's machine holds equals the recorded one at
  every mark.

#### Scenario: One time, another, and the first again
- **WHEN** the transport seeks a time inside a step, another time, and the
  first time again
- **THEN** the first and the third seeks hold the same bank and draw
  identical pixels, which differ from the second's.

#### Scenario: Outside the take
- **WHEN** the transport seeks -1 s or 9 s on the 8 s take
- **THEN** it poses the bank at 0 s or at 8 s and `time()` reports 0 or 8.

### Requirement: A posed loop is the trivial take

Given a viewer of a posed loop, the take transport SHALL give a transport
of `duration` 1, no marks and no machine, whose `seek(t)` sets the viewer's
normalized loop time to `t` clamped to `[0, 1]`, drawn when it returns.

#### Scenario: A loop sought
- **WHEN** the viewer layer runs with a bundle and the transport seeks the
  seesaw's export to one time, another and the first again
- **THEN** the first and the third draw identical pixels, which differ
  from the second's, and a time past 1 sets the loop time to 1.

### Requirement: A clock drives a transport by a timer or by the narration

The take transport SHALL give two clocks of one interface: a timer clock
of a given duration and an audio clock whose time is an audio element's
playback position. A clock SHALL play, pause, report whether it plays,
seek to a time clamped to `[0, duration]` without changing whether it
plays, report its time and its rate, take a new positive rate, and call
back each subscriber once per animation frame while it plays and once on
the animation frame after a seek, with the time then; a slow frame is
dropped, never queued, and two seeks within one frame call back once with
the later time. On reaching its duration a clock SHALL stop there and call
back with exactly the duration; playing it again SHALL start from 0. The
audio clock SHALL play, pause, seek and change rate by driving the
element. A clock MUST refuse a duration that is not a positive number of
seconds and a rate that is not positive and finite, naming it.

#### Scenario: A timer to its end
- **WHEN** a 2 s timer clock plays at rate 1 and its animation frames come
  at 0.5 s steps of its time source
- **THEN** a subscriber is called back at 0.5, 1, 1.5 and 2, the clock
  stops at 2, and no further frame is asked for.

#### Scenario: A seek while paused
- **WHEN** a paused clock is sought to 0.75 and then to 1.25 before the
  next animation frame
- **THEN** each subscriber is called back once, with 1.25, and the clock
  stays paused.

#### Scenario: The narration as the clock
- **WHEN** an audio clock over an element is played, sought to 3 s and
  given rate 1.5
- **THEN** the element is played, its playback position is 3 s and its
  rate 1.5, and the clock's time is the element's position.

### Requirement: The take transport depends on the viewer's handle and the pose rule only

The take transport's sources (every file under `transport/` but its tests)
SHALL import only files of the directory and the pose rule
`src/take.mjs`: no package, nothing from the stage, nothing else from
`src/`; its tests MAY also import the test runner and the shared fixtures.
The viewer's public handle as Videomaker reaches it SHALL be declared there,
types only, and the stage SHALL import it from there. A repository test
MUST refuse any other import, naming the file and the specifier, so the
transport can be moved to another package with its tests and nothing
else.

#### Scenario: An import across the boundary
- **WHEN** a file of `transport/` imports `react`, `../stage/types` or
  `../src/movie.mjs`
- **THEN** the repository test fails naming the file and the specifier.

#### Scenario: The pose rule's declaration out of step
- **WHEN** `src/take.mjs` exports a function its declaration file does not
  declare, or the declaration declares one the module does not export
- **THEN** the repository test fails naming the function.
