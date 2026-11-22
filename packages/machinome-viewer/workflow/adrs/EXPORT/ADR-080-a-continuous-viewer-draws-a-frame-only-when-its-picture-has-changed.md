# ADR-080: A continuous viewer draws a frame only when its picture has changed

**Status:** Accepted

**Date:** 2026-11-22

**Change:** [draw-only-when-the-picture-changes](../../../openspec/changes/archive/2026-11-22-draw-only-when-the-picture-changes/)

**Builds on:** [ADR-076: A part's presented look has one owner](ADR-076-a-parts-presented-look-has-one-owner.md)
(the holder of the materials, which carries the counter),
[ADR-077: An on-demand viewer poses a clocked machine by request](ADR-077-an-on-demand-viewer-poses-a-clocked-machine-by-request.md)
(every call that changes the picture draws before it returns),
[ADR-043: Hash-consed expression evaluation](ADR-043-hash-consed-expression-evaluation.md)
(what a tree update does to the expression store)

## Context

In the `continuous` render mode the viewer's loop updated the tree and drew
the scene on every animation frame, whether or not anything had changed.
On the Enigma I page that was 20 to 23 ms of script a frame, 16 to 19 of it
the draw and 3 to 4 a tree update whose change set named nothing, and
3,347 draw calls and 44.8 million triangles asked of the graphics card on
every frame for as long as the page was open. In the eight seconds after a
key press about 300 frames were drawn and under 40 changed anything.

The loop drew because it could not tell. Sixteen other places in
`viewer.ts` already draw after a change they make, which is how the
`on-demand` mode works; but several changes reached the screen only
because the next frame was drawn anyway: a turn of the model, a resize, a
hover and its end, a mount and a reload, the frames of a drawn request, a
ramp, and an in-place update applied while a new program starts.

## Decision

**In the continuous mode the loop still runs on every animation frame, and
draws only when the picture can have changed since the last draw, or while
something moves.**

1. **What the loop compares** with what the last draw recorded: the tree
   shown, by identity; the mount's picture revision; the camera's world and
   projection matrices, 32 numbers, under `Object.is`. It also draws when
   nothing has been drawn yet, and on the frame after the browser restores
   a lost graphics context or a hidden page is shown again.
2. **The picture revision** is one counter per mount (`picture.ts`),
   carried by the mount's material holder, which every tree and flexible
   part of the mount already shares. It is raised by the two owners of
   what the scene holds: the holder, at the one place a mesh is pointed at
   another material; and the tree, in its four writers: an update whose
   change set reaches a node, before its first write; `applyVisibility`;
   `artifactChanged` and `reconcile` when they apply. Judging a pose
   raises nothing.
3. **The camera is compared, not listened to.** Whoever writes it (the
   controls, which are replaced by a new object when the up direction
   changes; `setView`; framing) is seen by value, and a `NaN` aspect from a
   container with no size equals itself.
4. **In doubt, the loop draws.** While the timeline plays, a ramp moves a
   driver, the clock plays, a request's transition is drawn, a run is
   started or a gesture on a part is engaged, every frame is drawn and
   updated exactly as before, the frame the motion stops in included
   (the state is read at the start of the frame and at its end). A paused
   run joins the rule above: its picture changes only through a committed
   frame, which draws.
5. **A resize draws itself.** Setting the renderer's size clears the canvas
   when the size changes, and a browser may clear it at an equal size; no
   comparison could see that. The resize observer's callback draws after
   it resizes, in the continuous mode, so the frame in which the canvas is
   resized shows the picture.
6. **Every call that drew before it returned still does,** unconditionally,
   through the one function that renders (`drawPicture`), which also
   records what the loop compares.
7. **The update that names no change is skipped.** A tree update whose
   change set has no time and no driver reaches no node for any kind of
   document, and its scope of the expression store is not a reclamation
   point: the store reclaims at the end of a scope only what was requested
   while that scope was open.
8. **The loop is not stopped.** It advances the ramps, polls the hover and
   keeps the time between frames on every frame, drawn or not, so no
   motion loses or gains the time of the still frames before it.
9. **On demand nothing changes:** no loop, no record, no listener, and the
   observer resizes without drawing.

**The rule for later code.** Whatever writes something a draw reads goes
through the tree's four writers or the holder, which raise the revision;
or is the camera, which is compared; or draws itself. Every `setSize` is
followed by a draw. A write to a three.js object from anywhere else is the
one way to a stale picture.

## A consequence for hosts

A script that reads the canvas's drawing buffer (`toDataURL`, `drawImage`,
`readPixels`, `captureStream`) in an animation frame of its own, after the
viewer's, used to find the picture the loop had just drawn. It now finds a
cleared buffer in a frame in which nothing changed, because the renderer
does not preserve its drawing buffer. A read in the task of a call that
draws, a screenshot of the page and what a maker sees are unchanged. No
host in this repository's workspace reads that way; one test of the viewer
did and reads in the task of a call that draws now. Keeping such reads
working would take `preserveDrawingBuffer: true`, a renderer setting whose
cost was not measured. The pilot was told before integration.

## Alternatives

- **A flag set at each source in `viewer.ts`:** the place that writes is
  not where the flag is set, and the source added next is the one missed.
- **Comparing the whole scene by value every frame:** a walk of every
  object per frame, like the one this decision removes. The tests do it
  (the detector), where it buys proof.
- **Listening to the camera controls:** lost with the controls object that
  is replaced, and blind to `setView` and framing.
- **Stopping the loop when still:** every source would have to restart it,
  and the first frame after a restart would carry the stopped interval. A
  loop that skips both measured 0.03 to 0.05 ms a frame.
- **A periodic safety draw:** it would turn a missed source from a stale
  picture into a late one, which looks like lag and is less likely to be
  reported.
- **Letting motion join the rule:** it changes what a frame of a motion
  costs, which this decision leaves as it was.

## Consequences

- A page on which nothing moves asks nothing of the graphics card and runs
  no part of the pose.
- The frame in which the canvas is resized shows the picture where it
  showed a cleared canvas.
- The first task after a still period starts from a machine that has run
  no script for a while. On the Enigma page a press's click measured about
  4 ms more than after frames that drew; the same click on the previous
  viewer, after still frames in which the draw and the update were skipped
  from outside, was slower by more.
- The tree-identity term and `reconcile`'s own raise are redundant on
  every path of the mount, because an update of the whole tree follows
  both; they are kept, and the second is held by a unit test.

## Proof

A bench that mounts the real viewer in jsdom with a counting renderer and
drives its loop frame by frame. Counts red before the change: draws and
tree updates over still frames; for each source a draw within one frame
and none after. A detector that reads everything a draw reads and fails
when it differs from what was last drawn, run after every step and through
200 generated sequences of host and maker actions. Per-frame counts during
every kind of motion, and the time a motion takes after still frames,
recorded on the base and reproduced. Browser tests: no WebGL draw call
over still frames; each kind of change compared with a forced redraw; a
canvas read inside the resize; a press drawn until it lands and not after.
Thirteen designed mutations and sixteen faults planted in review turn
named tests red or are shown redundant or equivalent.

**Measured** on the Enigma I page (`enigma-i` at `081f4e6`), script only:
a still frame 16 to 20 ms before and 0.03 to 0.05 after, with no draw and
no update; in the eight seconds after a key press 7.4 to 7.5 s of script
before and 1.9 to 2.0 after, every changing frame drawn and none after
the last. Really drawn in software, in 18 states (a mount, a key, the
highlights, the flap, a wheel, a turn, a zoom, a resize, a reload): what
is on screen equals a forced draw and equals the previous viewer's picture
pixel for pixel; a build without the camera comparison goes stale on the
turn and the zoom. Not measured: any GPU, another browser.

[Design](../../../openspec/changes/archive/2026-11-22-draw-only-when-the-picture-changes/design.md) and
[evidence](../../../openspec/changes/archive/2026-11-22-draw-only-when-the-picture-changes/evidence.md)
record the cases, the tests and the measurements.
