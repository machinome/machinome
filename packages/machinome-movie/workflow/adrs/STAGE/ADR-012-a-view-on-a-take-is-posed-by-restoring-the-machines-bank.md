# ADR-012: A view on a take is posed by restoring the machine's bank, and the viewer is held to the take

Status: Accepted (OpenSpec change `pose-a-take`, 1 October 2026). Builds on
[ADR-011](../SOURCE/ADR-011-a-clocked-take-is-the-frameworks-requests-recorded-once-by-evaluation.md)
(the take is the framework's requests, recorded once by evaluation) and
[ADR-007](ADR-007-viewer-instances-are-leased-to-view-elements-per-frame.md)
(each frame states each instance's whole state).

## Context

The Curta film of the curta-video campaign (*Addition*, `23 + 145`) films a
clocked machine. ADR-011 put its take in the movie document: the bank
before the first step, each step with the request the framework returned,
and the bank at every mark. Nothing drew it: a view's state was a loop's
normalized time, the stage called `setTime`, and the commands refused
anything but a posed loop. The spike of the campaign showed, on the real
viewer, that `machine().restore({identity, bank})` accepts a bank whose
input lies mid-path and poses it synchronously and exactly, that posing A,
B, A gives identical bytes, and that `machine().move()` from a restored bank
reproduces the framework's requests bit for bit; the viewer's API 29
admits a clocked document under on-demand rendering, draws a restored bank
on the next `setView`, and refuses `trigger` there. It also showed that the
stage's canvas check accepts a stale canvas larger than a box that shrank,
which a reframe does on every frame.

## Decision

1. **A frame poses a bank.** In a take document a view's state carries
   `bank`, the machine's whole bank at its take time, instead of a loop
   time. The bank is the contract's rule, computed in one pure module
   (`src/take.mjs`): the bank before the step, its input along the
   recorded path, every commit up to the fraction written; a step owns its
   end, so a mark poses exactly the bank recorded there.
2. **The stage restores it.** A view on a take mounts without a loop time
   and is posed by `machine().restore({identity, bank})` with the take's
   identity, then the camera; its loop time is never set and nothing is
   triggered. The stage refuses at mount a viewer that gives no machine, or
   another machine, naming the view, and reports the bank the machine holds
   after each pose. A movie on a take needs Viewer API 29.
3. **The viewer is held to the take.** Node checks a take document as
   Python does, the replay of its steps against its banks included, before
   any take of speech. Before the first frame of each `preview` and
   `render` session, each step is replayed on the viewer's machine from its
   recorded bank and its request compared exactly with the record (`origin`,
   `end`, each commit's `fraction`, `value` and `targets`); at every posed
   frame the reported bank must be the frame's, and at a mark the recorded
   one. A difference stops the film, naming the step and the field, or the
   view, the mark and the id.
4. **A canvas is its box's size.** The stage's canvas wait counts a canvas
   ready when it fills its box and exceeds it by no more than a pixel, and
   the renderer refuses a larger one (`Viewer canvas exceeds its view`).

## Options considered

- **Draw a stroke with `trigger`.** It runs on the viewer's own clock,
  needs the frame loop, and is refused under on-demand rendering; a frame
  would depend on when it was asked for.
- **Compute the pose in the tool** (the dials' angles mid-stroke). The
  machine's pose of a restored bank is the viewer's closed form; the tool
  would be a second implementation of the machine.
- **Trust the viewer's `move` without comparing it.** The film would show
  whatever a viewer of another version solved; parity is the point of
  recording the take.
- **Carry the take time on the frame** and let the stage ask the machine.
  The stage would decide what is drawn from something other than the
  frame; the frame carries the bank, a complete state.
- **Keep the stage's one-sided canvas check.** It passed because the
  viewer happened to resize within two frames; a slower resize would pose
  into a stale canvas unseen.

## Consequences

- A movie on a clocked take is filmed by the commands and needs Viewer API
  29; a running machine stays refused.
- Each session pays one `restore` and one `move` per step before its first
  frame, and each pose of a view on a take restores the whole bank.
- The runtime changes, so every film's stage bundle changes and recaptures
  once.
