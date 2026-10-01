## Why

The episode is *Addition*, the Curta film of the curta-video campaign (the
Curta Type I 3x project, `videos/addition/`, filming the clocked model
`clocked_curta` through a take). Its finding is wart 10 of the section
"Addition (Curta, 1 October 2026)" of `workflow/warts.md`, met while the
film's cycle `pose-a-take` was being proved (its `evidence.md`, finding 8):

> **Marks on a take with the viewer double stay put**: the double's part
> rectangles move with a loop's time, not a bank, so a mark on a clocked
> take is proved only at layer 6.

A mark (a ring, a label or an arrow on a part) is drawn where the viewer's
`partOnScreen` says the part is, read after the view is posed. On a posed
loop the double's part rectangles move with the loop time the stage sets,
so layer 5 proves that an arrow follows a moving part. A view on a take is
posed by restoring a bank and is never given a loop time (ADR-012), so the
double's rectangles stand where they stand at time 0 whatever bank the
stage restores: no browser test can tell a mark that follows its part from
one drawn where the part was in another bank, or from one read before the
bank was restored. And the viewer layer, which the finding names as the
only place left, has no mark on a take either: the fixture movie `count`
draws none, and no test of `test/viewer/take.test.mjs` poses one. Today no
layer proves it.

## What the film does with the result

*Addition* draws a highlight and no ring, label or arrow; its pictures do
not change. What the result gives the films on takes, this one's next cut
and the next clocked film, is the proof their marks rest on: a mark on a
part the take moves follows the part from one bank to another, proved in
the browser layer with the double on every run, and with the real viewer
when a bundle is selected, by the same assertion. A stage change that read
a part's rectangle before restoring the bank, or carried one between
frames, is then red at layer 5, before the slow real-viewer layer runs.

## What Changes

- **The double's machine moves its parts with its bank.** The viewer
  double's `machine` option names the input its part rectangles follow and
  that input's range, `follows: {input, range: [low, high]}`; a part's
  rectangle stands at the input's fraction of that range where, without a
  machine, it stands at the loop time. Its value is the one the bank holds,
  set by `restore`, `move` and `reset`, so the rectangles are a function of
  the bank as they are of time without one. A double machine that follows
  nothing, or an input its bank does not hold, is refused at mount naming
  the input. The fixture's take machine follows the counter's `units`,
  0 to 9: the units drum the take turns.
- **A mark between two banks, at layers 5 and 6 with one assertion.** On
  the fixture movie `count`, a ring on the units drum is posed at the take's
  start (the initial bank) and at the mark `one`, then at the start again:
  the two frames place the view in the same box with the same camera, and
  the ring lands at two different screen places, the first identically
  twice, with identical pixels. The assertion lives in one helper both
  layers call: in `test/browser/take.test.mjs` on the double, in
  `test/viewer/take.test.mjs` on the selected bundle.
- **Records**: the test-suite spec's requirement on the take's proofs;
  `AGENTS.md`'s layer 5 line; `fixtures/README.md`; `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `test-suite`: the browser layer proves a mark on a take with the double,
  whose part rectangles follow its bank; the viewer layer proves the same
  with the real viewer.

## Impact

Tests only: `test/viewer-double.mjs`, `test/support/fixture-movie.mjs`
(the take machine), a new helper `test/support/mark-on-a-take.mjs`,
`test/browser/take.test.mjs`, `test/viewer/take.test.mjs`. The double and
`test/support/` are in every slow test's memo key, so every slow test runs
once after this change. Nothing under `src/`, `stage/`, `python/`,
`schema/` or `fixtures/` changes; the real viewer and the Curta film are
untouched.

## Non-goals

A renderer in the double: one input shifts every part's rectangle along
one axis, enough to tell two banks apart; the double does not model which
part an input turns. No mark cue in the shared fixture document `count`
(design D3). No change to how the stage poses a take, to the timeline's
marks or to the viewer. No ADR: a test double that answers one more
question is no architectural decision, and the layer boundary ADR-008
records does not move (design D4).
