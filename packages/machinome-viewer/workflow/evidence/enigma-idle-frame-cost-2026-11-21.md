# What a frame costs in which nothing changed, Enigma I, 21 November 2026

Opening evidence for `draw-only-when-the-picture-changes`, written by the
reviewing agent before the proposal. Measured facts with their limits;
nothing here is a design.

## Where the finding comes from

The Enigma I reconstruction (`enigma-i` at `081f4e6`), as its page is built
by the project's own tools, in the viewer at framework commit `56de33dd`
(after `share-one-material-per-appearance`). The page mounts the viewer in
its default, `continuous`, render mode.

Read from `viewer.ts`: in that mode the loop given to
`renderer.setAnimationLoop` runs on every animation frame. It advances the
ramps (`drivers.tick()`), polls the hover, and then either hands the frame
to a running program and draws, or advances the clock, the drawing of a
pressed instruction and the timeline, calls
`tree.update(scope(), { time: playing, drivers: movedDrivers })` and calls
`renderer.render(scene, camera)`. The update and the draw are not
conditional on anything having changed.

The same file draws explicitly in sixteen other places, after a change it
makes itself (a highlight, a view set, a reload, a request to a clocked
machine): that is how the `on-demand` render mode, which has no loop, shows
anything. Other things are shown only because the loop draws the next
frame anyway, among them a turn of the model, since the camera controls
(`OrbitControls`) are not listened to, and a resize, whose observer resizes
the renderer and draws nothing. The change's design lists them all.

## What was measured

Headless Chromium (Playwright), the page's own files, the viewer built
unminified from its unedited source (with molejo's `main`) and a scratch
entry that exposes the renderer and the scene and wraps two calls with
switches: the outermost `WidgetTree.update` is skipped when its change set
names nothing (`time` false, no driver), and `renderer.render` is skipped.
WebGL draw calls were counted and not executed, so every time is script
time on the measuring machine (a virtual machine with no GPU). One page
load; after a key, a press and a release to settle, the four variants ran
alternately, 2.5 seconds each, three rounds.

Script per animation frame with nothing changing, in milliseconds, median
of each round:

| Variant | The frame | of it, the draw | of it, the tree update |
|---|---|---|---|
| As shipped | 20.8, 22.6, 19.9 | 17.2, 18.9, 16.4 | 3.6, 4.0, 3.7 |
| The update that names no change skipped | 19.1, 20.6, 15.2 | 19.3, 20.6, 15.1 | 0 |
| The draw skipped | 2.2, 2.2, 2.2 | 0 | 2.1, 2.3, 2.1 |
| Both skipped | 0.0, 0.1, 0.1 | 0 | 0 |

In every round every update of the loop named no change (123 of 123 in the
last as-shipped round). Each drawn frame is 3,347 draw calls and 44,819,200
triangles. Two idle frames really drawn by the software rasteriser and
read back from the canvas: no pixel differs.

After a key press, over the eight seconds that follow the click, three
rounds of Press and Release:

| | Lowest to highest of six |
|---|---|
| Frames drawn in the eight seconds | 281 to 338 |
| of them, frames in which a mesh moved, a geometry was refilled or a colour changed | 33 to 38 |
| The last such frame, after the click | 1,982 to 2,043 ms |
| Script per frame that changed something, median | 51.1 to 56.8 ms |
| Script per frame that changed nothing, median | 18.3 to 22.1 ms |
| Script spent on the frames that changed nothing | 5.56 to 5.64 s of the 8 |

## Limits

- Script time on one virtual machine, one page load, three rounds. No GPU
  was involved: what drawing 44.8 million triangles costs a graphics card,
  and what an idle page costs a maker's machine in power or heat, were not
  measured. At 60 frames a second the shipped page asks for about 200,000
  draw calls and 2.7 billion triangles a second while nothing moves; that
  is arithmetic from the counts above, not a measurement.
- The switches are blunt and from outside the viewer: they skip every draw
  and every update naming no change, during periods in which the script
  made sure nothing changed. They show a floor. Nothing in them decides
  when a draw is needed, which is the whole of the design.
- "Changed" in the press count is what the measurement samples: each
  mesh's world matrix, the version of its geometry and its material's
  colours. A camera move, a change of visibility or a resize would not be
  seen by it; none happened.
- The update that names no change measured 2.1 to 2.3 ms with the draw
  skipped and 3.6 to 4.0 beside the draw. It is the same work; the
  difference was not explained.
- Not examined: what skipping that update does to the expression store's
  scopes and reclamation, which today are entered once a frame; a running
  program, whose frames are driven by a worker; a document with a
  timeline playing.
- The Enigma document is a project's and is not in this repository.
