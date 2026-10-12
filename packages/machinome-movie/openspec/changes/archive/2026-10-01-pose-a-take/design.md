## Context

`declare-a-take` (ADR-011) records a clocked take in the movie document: the
`take` block with the machine's `identity`, the `initial` bank, every step
with the request the framework returned verbatim, and the `banks` at the
marks; `model.timeMode` is `"take"`. The contract (`docs/movie-document.md`,
"The take", "The frame", "The stage") says how a frame poses it and how the
viewer is held to it. The Node side refuses it today: `checkProject` admits
only a posed normalized loop, `checkMovie` knows no take rule (all five take
fixtures pass it), `viewState` gives every view a loop `time`, and the stage
calls `setTime`.

The spike (`workflow/ongoing/curta-video-campaign/spike.md`) established on
the real viewer: `machine().restore({identity, bank})` accepts a bank whose
input lies mid-path and poses it before it returns; `state()` returns
exactly the bank given; posing A, B, A gives identical bytes;
`machine().move(input, {to}|{by})` from a restored bank returns the
framework's request with `Object.is` equality; a highlight survives a
restore. The viewer cycle `on-demand-clocked` (Viewer API 29) admits a
clocked document under on-demand rendering: `restore`, `reset` and `move`
pose and draw before they return, `setView` redraws (and refits the
clipping planes), and `trigger` is refused under on-demand. The spike also
found that the stage's canvas check (`≥ 98 %` of the box) accepts a stale
canvas larger than its box after a shrink, which a reframe makes on every
frame.

## Goals / Non-Goals

Goals: film the take exactly as the contract says, every pixel a function
of take time; refuse a document, a viewer or a frame that disagrees with
the record, by name, as early as it can be known; prove it at layers 2 to 6
and 8. Non-goals: those of the proposal.

## Decisions

### D1. Loading a take document

`checkMovie` gains the take rules of Python's `check_document`
(`declare-a-take`, D7), ported with the same words: the time mode; the
block's presence; with the manifest, a clocked export, the identity, every
step's input among the export's drivers (and its clock when it declares
one), `initial` holding exactly the export's drivers and states; unique step
ids, exactly one of `to` and `by`, steps end to end from 0 (within 1e-9 s),
the length; marks at 0 or a step's end, each with its bank; the replay
(D2); and a shot's model time within the take (`outside the take`). They
run before anything needs a take of speech, so `check` refuses them first.

`checkProject` (the load's check of the document against its export)
branches on the time mode. A loop keeps its checks (the export's
`animation.loop` is the document's period). A loop document whose export
publishes a clocked machine is refused naming `model.timeMode` and the
export's `clocked` block: a clocked machine is filmed through a take. A
take document needs the export's `clocked` block (already refused by
`checkMovie` with the manifest). An export with a `program` block, a running
machine, is refused for either mode, naming `program`. The sentence "Only
posed normalized-loop models are supported" goes from the movie path; a YAML
episode keeps its own checks, unchanged.

### D2. The take, pure, in `src/take.mjs`

One module holds what the take means, with no I/O:

- `replayTake(take)`: the bank before each step (from `initial`) and after
  it (the input at `end`, every commit's `targets` written in path order).
- `checkTakeBanks(doc)`: the bank the replay gives at each mark (the initial
  bank at 0, otherwise the bank after the step ending there) must equal
  `take.banks[mark]` exactly, id by id in sorted order, or the document is
  refused naming `take.banks.<mark>`, the mark and the first differing id.
- `bankAt(take, seconds)`: the contract's pose rule (D3).
- `takeLine(doc)`: what `check` prints.

Exact comparison (`Object.is` after JSON), because both sides hold the
framework's floats verbatim and the rule only copies them.

### D3. The bank at a take time

For a take time `t`: `t ≤ 0` is `initial`. Otherwise the step is the one
with `at < t ≤ at + duration`, and `f = (t − at) / duration`; the bank is
the bank before that step, its input at `origin + f · (end − origin)`, and
the targets of every commit whose `fraction ≤ f` written. At `f = 1` the
input is exactly `end` (not the arithmetic, which can miss `end` by its
last bit). Past the last step the bank is the one it ended with.

A step therefore owns its end and not its start. That is what makes a mark
agree with the rule: a mark is the instant after the step before it, and
its recorded bank is the bank that step ended with; were the instant the
start of the next step, a commit of that step at fraction 0 would be
written at the mark and the frame posed there would not be `banks[mark]`.
A step whose input and origin equal the previous end (the normal case)
draws the same pose either way.

The bank is a fresh object whose ids are in `initial`'s order, so a frame
serializes identically wherever it is computed. Banks before each step are
computed once per film and cached by the film object, as the timeline's
index is.

Alternatives rejected: computing the dials' pose in the tool (the machine's
pose mid-stroke is the viewer's closed form of the restored bank, ADR-011);
interpolating states between commits (a state is discrete; the contract
writes it at its commit).

### D4. The frame of a view on a take

`viewState` gives a view in a take document `bank` (D3 at the shot's model
time, which resolves marks and keys in take seconds exactly as model
seconds) and no `time`. Everything else of the view state is unchanged.
Under a reframe the incoming shot's live frame is drawn (ADR-010), so the
moving view's take runs on as a loop's time did. A shot whose model time
leaves the take is refused at resolution as a loop's leaves its period;
the existing check does it, since a take document's
`expectedDurationSeconds` is its length.

### D5. The stage

- The config (`stageConfig`) carries the take's identity,
  `take: {identity}`, for a take document.
- A view whose state carries `bank` mounts without a `time` option, then
  the stage reads `viewer.machine()`: a viewer that has no `machine`, or
  whose `machine()` returns nothing, is refused at mount naming the view and
  the shot; one whose `identity()` differs from the take's is refused naming
  the view, both identities and `take.identity`.
- Each pose of such a view calls `machine().restore({identity, bank})`
  with the whole bank, then `setView`; `setTime` is not called. The pose is
  one exported helper, `poseView(viewer, state, identity)`, which the
  runtime calls for every view and layer 4 tests with a stub viewer.
- The view's report gains `bank`, `machine().state()` after the pose.
- `movieViewerApi` adds the reason `clocked take` and requires Viewer API 29
  for a take document; the stage's existing API refusal and `check`'s
  banner check apply unchanged.

Alternative rejected: `trigger` to draw a stroke. It runs on the viewer's
own clock and is refused under on-demand; the take is posed by `restore`
only, so a frame is a function of take time and nothing else.

### D6. The renderer holds the viewer to the take

- **Before the first frame**, once per session, on the instance the first
  view of the film mounted: for each step, `restore` the bank before it,
  `move(input, {to}|{by})`, and compare `origin`, `end`, the number of
  commits and each commit's `fraction`, `value` and every `targets` id
  exactly with the record; refuse on the first difference naming the step
  (its id and `take.steps[i]`) and the field (`commits[2].targets.units`).
  The next frame restores its own whole bank, so nothing of the replay is
  carried into a picture. The session's info records the replay
  (`takeReplay: {steps, matched}`), which `preview`'s report keeps.
- **At every posed frame**, a view on a take must report exactly the bank
  its frame asked for (`Viewer bank differs from the frame`), and when its
  take time is a mark (within 1e-9 s), exactly `take.banks[mark]` (`Viewer
  bank differs from the take at mark <mark>`), naming the view, the shot,
  the time and the first differing id.
- **A canvas larger than its view** by more than one pixel in either
  dimension is refused on every posed frame: `Viewer canvas exceeds its
  view: <view> in <shot> at <t> s (canvas …, box …)`. The stage's canvas
  wait counts a canvas as ready when it fills its box and exceeds it by no
  more than a pixel, so a shrinking host is waited for as a growing one is.

These are refusals of the film, like the camera readback: `preview` and
`render` stop on them before capturing.

### D7. `check` prints the take

After the chapters' lines, a take document prints one line:
`Take: 3 steps, marks one 2 s, nine 6 s, ten 8 s, 8 s long; the replay of
its steps gives the recorded bank at every mark`. `check` reaches it only
after `checkMovie` ran the replay, so the line states a check that passed.

### D8. The viewer double and the fixtures

- `viewerDouble` gains `machine: {identity, initial, requests}`: `machine()`
  returns a handle with `identity()`, `order()`, `state()`, `restore()`
  (refusing another identity), `reset()`, `snapshot()` and `move()`, which
  answers from `requests` (the record's steps, or a table the test forges)
  by the input, the `to` or `by` and the origin, and writes the bank after
  the request; an unknown request throws. A restore or move recolours the
  canvas from the bank, so the pixel proofs see a pose change. `trigger`
  throws under on-demand rendering, as the real viewer does. Without
  `machine`, `machine()` returns null. `lateCanvas` may give a number of
  frames the canvas waits after a resize before it follows; `stuckCanvas`
  never follows a shrink.
- `fixtureMovie` gives a take document's default double the take's own
  machine and API 29.
- `fixtures/resolved/count.json` is pinned by `scripts/pin-resolved.mjs
  count` and reviewed: the take block passes through resolution unchanged,
  and the banks at the shots' first instants are the rule's.

### D9. The viewer's controls

The stage draws no viewer control in a film. A layer 6 test asserts that a
mounted on-demand view of the clocked fixture shows no full-screen control
(`.machinome-fullscreen`). If the viewer draws one, the stage's stylesheet
hides it with the viewer's documented rule, `.machinome-fullscreen {
display: none }`; otherwise the stylesheet is unchanged.

## Refusal words

Both runtimes, by the shared invalid fixtures (`fixtures/README.md`): the
five of `declare-a-take`, now refused by Node too. Node only (tests assert
each name):

- a loop document over a clocked export: `model.timeMode`, `clocked`;
- a running program: `program`, `running`;
- a viewer without a machine: the view, the shot, `machine`;
- another machine: the view, `take.identity`, both identities;
- the replay on the viewer: the step's id, `take.steps[i]`, the field;
- a bank that differs: the view, the shot, the mark, the id;
- `Viewer canvas exceeds its view`, the view and the shot.

## Risks / Trade-offs

- The replay before the first frame costs one `restore` and one `move` per
  step (tens of milliseconds each on the Curta, the spike measured): paid
  once per session.
- Every view on a take restores the whole bank on every frame (about 23 ms
  on the Curta's 41 ids): small beside a capture.
- The runtime changes, so every film's stage bundle changes and every film
  recaptures once.
- A real viewer below API 29 refuses to mount the clocked document under
  on-demand rendering, before the stage can read its API: `check` names the
  requirement from the bundle's banner; `preview` and `render` stop on the
  viewer's own refusal, which the stage reports naming the view and the
  shot.
