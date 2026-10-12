## Context

The viewer double (`test/viewer-double.mjs`) stands in for the
machinome-viewer in every browser and pipeline test. Its `partOnScreen`
returns a 24 × 20 px rectangle whose left edge stands at
`0.35 + 0.3 · time` of the canvas width, `time` being the loop time the
stage last set (`options.time` at mount, `0` when none); `project` is a
pinhole camera. With the `machine` option (the pose-a-take change) it has a
clocked machine: `restore`, `move` and `reset` change its bank, and the
bank is painted as an inset outline of the canvas so a pose change reaches
the pixels. The stage poses a view on a take by `machine.restore(bank)`
and never calls `setTime` on it (ADR-012), so the double's rectangles stay
at time 0 whatever bank is restored.

The stage draws a view's marks after posing its viewer, from what
`partOnScreen` and `project` report (`stage/marks.ts`); the session checks
each mark's target on screen, a ring wholly on screen and in the frame,
and a text inside the frame (`src/render.mjs`, `show`). The marks a frame
carries come from the timeline, which builds them the same way for a view
on a loop and on a take (`src/timeline.mjs`, `viewState`).

The fixture movie `count` films the counter's take: shot `once` (set
`frame`, take 0 to mark `one` at 2 s), `nine` (set `frame`, mark `one` to
mark `nine` at 6 s) and `carry` (set `split`, mark `nine` to mark `ten` at
8 s, by a dissolve). The marks' banks are `one` {crank 360, units 1, tens
0}, `nine` {crank 3240, units 9, tens 0}, `ten` {crank 3600, units 0,
tens 1}, over the initial bank {crank 0, units 0, tens 0}.

A probe on the selected bundle (API 29), run before this design was
written and not kept, read the counter's part rectangles through the stage
at 640 px (x, y, width, height in client pixels):

| instant | bank | `handle` | `units_drum` |
|---|---|---|---|
| 1.6 s (`once`) | crank 180, units 0 | 258.3, 96.2, 72.1 × 129.8 | 273.8, 161.8, 90.7 × 62.6 |
| 3.2 s, mark `one` (`nine`) | crank 360, units 1 | 309.5, 103.4, 78.9 × 137.3 | 255.2, 156.4, 126.4 × 76.6 |
| 4.25 s (`nine`) | crank 1800, units 5 | 309.5, 103.4, 78.9 × 137.3 | 273.8, 161.8, 90.7 × 62.6 |
| 5.3 s, mark `nine` (`carry`) | crank 3240, units 9 | 445.7, 115.6, 66.2 × 115.2 | 400.1, 160.0, 106.0 × 64.3 |

Three facts follow. The crank stands at whole turns at every mark, so the
handle is drawn alike at all of them. The units drum's rectangle changes
with the units (0° and 180° alike, 36° wider), so the real viewer moves a
mark on the drum between the initial bank and mark `one`. And mark `nine`
opens the `split`, where the view has another box: a mark there lands
elsewhere whatever the bank, with the double as with the real viewer.

## Goals / Non-Goals

Goals: the double's part rectangles are a function of the bank its machine
holds; one assertion proves at layer 5 with the double and at layer 6 with
the selected bundle that a mark on a part the take moves follows it between
two banks. Non-goals: those of the proposal.

## Decisions

### D1. The double's machine follows one named input

`machine.follows: {input, range: [low, high]}`. With a machine, the
rectangle's left edge stands at `0.35 + 0.3 · f` of the canvas width, with
`f = (bank[input] − low) / (high − low)`, the value read from the bank the
machine holds when `partOnScreen` is called; without a machine it stands at
`0.35 + 0.3 · time` as before. Everything else of the rectangle (its row
per path, `rectSize`, `vanishAfter`, the unknown-path refusal) is
unchanged. The double stays a function of what it was told: no state is
carried between poses beyond the bank `restore` replaces whole.

A machine without `follows`, or whose `follows.input` is not an id of its
initial bank, is refused when the double is mounted:
`the double's machine follows no input; name one of crank, tens, units in
machine.follows` and `the double's machine follows <input>, which its bank
does not hold (crank, tens, units)`. A double that silently kept its
rectangles still is the wart; a forged machine in a test names what it
follows like the fixture's.

The fixture's take machine (`takeMachine` in
`test/support/fixture-movie.mjs`) follows `units` over `[0, 9]`: the input
whose value the units drum shows, and the one whose drum the real viewer
moves between the initial bank and mark `one`.

Rejected: following every input (a hash of the bank, as the outline is
painted): a rectangle that jumps with the crank's angle at every frame of a
step would make the outline and the rectangles two encodings of one hash,
and a test could not say where a mark should be; following the first id of
the bank by default (the counter's first id is `crank`, whose value at
the marks is a whole number of turns the real viewer draws alike, so the
double would prove a movement the viewer does not make); moving the
rectangle by the input in client pixels (3600° would leave the canvas).

### D2. Two banks in one box: the take's start and mark `one`

The proof poses three frames of `count` with transitions off: 0 s (shot
`once`, take time 0, the initial bank), the start of shot `nine` (mark
`one`, the bank the take records there) and 0 s again. Both are recorded
banks, posed exactly (`bankAt` returns the initial bank at 0 and the
mark's bank at its take time); both frames place the view on the `frame`
set with the camera `front`, so the view's box and camera are equal and a
difference in a mark's place is the bank's.

Mark `nine` is not used: its shot `carry` is on `split`, where the view's
box differs, so a mark would land elsewhere without any bank (the probe;
with today's double the rectangle's left edge moves with the canvas too).
Mark `ten` is the last shot's end, which no frame of the film reaches
exactly.

### D3. The mark is the frame's state with a ring added, not a cue in `count`

Each pose hands the stage the frame's own state for `counting.view` with
one ring added, `{id: 'units-ring', kind: 'ring', target: {paths:
[['units_drum']]}, padding: 0.01, opacity: 1, drawn: 1}`, the state the
timeline builds for a ring cue at rest; the session's override replaces
only that element's state (the pattern the bank refusal test already
uses). The session's own checks then run on it: the target on screen, the
ring wholly on screen and inside the frame, the bank against the frame's
and, at mark `one`, the take's.

Rejected: a ring cue in the shared fixture document `count`. It would
change the document both runtimes emit and check, its resolved pin, the
Python fixture movie and the pipeline's `count` render, and its timeline
marks are already proved at layer 3 the same way as a loop's; the browser
proof needs only a mark on the view at two banks.

### D4. One assertion, called by both layers; no ADR

A helper, `test/support/mark-on-a-take.mjs`, poses the three frames in one
browser session on a given viewer (a double's file or the bundle's path)
and asserts:

1. the bank the view reports at each pose is the frame's (the initial bank,
   then `take.banks.one`);
2. the view's box is the same at both instants;
3. the ring's rectangle and its anchor at mark `one` differ from those at
   the start: the mark moved with the bank;
4. the ring's rectangle and anchor at the start, posed again after mark
   `one`, are those of the first pose exactly, and the two pictures are
   identical: the mark is a function of the bank posed, never of the pose
   before it.

`test/browser/take.test.mjs` calls it with the fixture's double,
`test/viewer/take.test.mjs` with the selected bundle. The red proof is
layer 5 on today's double: 3 fails, the ring standing at one place.

A stage that read `partOnScreen` before restoring the bank would report at
mark `one` the start's rectangle (3 fails) and at the second start mark
`one`'s (4 fails); one that kept a mark between frames fails 4.

No ADR: a test double answering one more question, and a test helper, are
no architectural decision. ADR-008 records the gate and the real-viewer
layer's scope, which stay: the viewer layer gains one proof, the browser
layer gains one, and the boundary between them does not move.

## Risks / Trade-offs

- **Every slow test runs once.** The double and `test/support/` are in
  every slow test's key (`ALWAYS` in `test/support/reach.mjs`).
- **The real viewer's drum moves little.** The units drum's centre moves
  about 2 px between units 0 and 1 while its rectangle widens from 91 to
  126 px; assertion 3 compares rectangles and anchors exactly, which the
  viewer's deterministic poses permit, and the ring's size is the visible
  difference. A future viewer that bounded parts by their exact silhouette
  could draw a round drum alike at every units value; the test would then
  fail at layer 6 naming the ring, and the proof would move to another part
  or instant, a test change.
