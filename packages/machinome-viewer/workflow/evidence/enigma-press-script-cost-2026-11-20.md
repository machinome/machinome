# Enigma I: what a press costs in script, measured without drawing

This is a viewer-side performance finding from a committed mechanical
project's own page. No project or framework source is copied into this
repository. The page is an ignored build artifact of the project, not a
viewer fixture.

The question was the pilot's: on the Enigma's page a pressed button freezes
the page and then shows the end state, with no motion between. The pilot
watches the page in a browser with a hardware GPU; these measurements were
taken on a host without one. They therefore time **script only**, with every
WebGL draw call skipped, and make no statement about how long any GPU takes
to draw this scene.

## Pinned inputs

- Project `enigma-i` at `081f4e6`, its page built by
  `tools/machine/build_page.py` into `_build-page/`. Manifest
  `_build-page/model/manifest.json`, 59 MB, SHA256
  `a8769deec38e3fbf0dca2b826ef4b7779d29d2137ad7977e2f34ed9d58326fc0`:
  document version 14, a clocked machine, 214,278 bindings holding 4,424,644
  characters of expression text, 1,046 STL files of 396.5 MB, 426 flexible
  parts.
- Viewer source at `3d1fdfa8` (0.9.0, viewer API 30), built unminified from
  `widget/src/widget.ts` with two additions that change no behaviour: a handle
  on the renderer, scene and camera taken in `Scene.onBeforeRender`, and the
  exported `EXPRESSION_LIMITS` and `expressionMetrics` placed on the page so
  the ceiling can be read and, for the second run only, set before mounting.
- Headless Chromium through Playwright on an AMD Ryzen 9 5900X virtual
  machine, 16 cores, 15 GB, no GPU (ANGLE on Mesa llvmpipe).

## Method

`drawElements`, `drawArrays` and their instanced forms were replaced on the
WebGL prototypes by counters that do not call through, so a frame's time is
the viewer's own script and three.js's bookkeeping. `requestAnimationFrame`
was wrapped to time each callback. Between frames a tracker compared every
mesh's world matrix, its position attribute's version and its material
colour against the previous frame, which gives the number of frames in which
the picture changed and what changed in each. A press is the instruction's
own button in the clocked panel, clicked by `element.click()`; the click's
synchronous duration is "the press task". A CDP sampling profile was taken
over one Press.

"Frames that changed the picture" is the count a watcher would see as
distinct pictures, were drawing free. Two means the start and the end.

## The store never holds this model

The mounted document holds **546,768** expression nodes. The store's
reclamation trigger is 125,000 (`EXPRESSION_LIMITS.nodes`), so every
outermost `withExpressions` finds the store over it and empties it, and
`bindings.ts`'s `roots()` prepares all 214,278 entries again. One such
preparation is about 2.3 s on this host.

The profile of one Press at the shipped ceiling: 15.5 s sampled, 14.9 s in
script; `prepare` 11.5 s inclusive and jokenizer's `tokenize` 7.5 s of it;
`intern` 2.6 s self.

## Before and after, the ceiling being the only difference

Second column: the same bundle, the same page, with
`EXPRESSION_LIMITS.nodes` set to 50,000,000 before mounting. No source was
changed for the pair.

| Instruction (declared seconds) | Press task, ms | Script per changing frame, ms | Frames that changed the picture |
| --- | ---: | ---: | ---: |
| Key A (0) | 2,398 → 71 | none | 0 → 0 |
| Press (2) | 6,960 → 900 | 3,591 → 418 | 2 → 4 |
| Release (2) | 7,078 → 858 | 3,476 → 453 | 2 → 4 |
| Right wheel on (0.4) | 7,225 → 847 | 1,737 → 239 | 2 → 2 |
| Right wheel back (0.4) | 7,139 → 813 | 1,819 → 209 | 2 → 2 |
| Open flap (1.5) | 4,760 → 80 | 2,378 → 44 | 2 → 29 |
| Close flap (1.5) | 4,734 → 65 | 2,413 → 40 | 2 → 33 |
| Open hood (4) | 4,823 → 71 | 2,437 → 44 | 2 → 80 |
| Close hood (4) | 4,622 → 68 | 2,452 → 40 | 2 → 87 |

An idle frame's script went from 42 ms to 34 ms. The page's JavaScript heap
was 1,932 MB before and 1,961 MB after: holding the whole graph cost about
30 MB on a page that already holds 1.9 GB. No page error in either run.

## What remains with the ceiling out of the way

- **Flexible parts.** On every changing frame of a Press, 86 flexible parts
  had their position buffers refilled (52 switch leaves, 26 key return
  springs, 8 of the stepping), 8.47 million triangles between them. In the
  profile of one Press (4.7 s sampled), `updateShapes` is 1.5 s inclusive.
  The Press travels one key. That the other parts received identical vertex
  data was reasoned from the model, not compared buffer by buffer.
- **The press task.** Every press, the instant ones included, called
  `renderer.render` twice inside the click's own task, before any animation
  frame.
- **Short instructions.** A 0.4 s wheel step still showed two pictures, with
  an 847 ms press task ahead of it.
- **An idle frame** is 34 ms of script with nothing moving: 3,347 meshes,
  3,347 draw calls, 3,347 geometries, 3,347 materials, 44.8 million
  triangles, 62.9 million vertices, 1,681 MB of vertex attributes.

## What a press changes

| Instruction | Meshes that changed | Triangles in them |
| --- | ---: | ---: |
| Press | 441 | 14,910,557 |
| Right wheel on | 391 | 14,587,138 |
| Open flap | 7 | 6,776 |
| Open hood | 64 | 274,324 |

Of 3,347 meshes and 44.8 million triangles in the scene.

## Not measured

- The time any hardware GPU takes for a frame of this scene. Frames drawn
  for real through llvmpipe took about 7 s each; that is a figure about this
  host's rasteriser and is not used above.
- A browser other than Chromium, and a CPU other than this one. The script
  figures scale with the CPU and not with the GPU.
- Memory beyond the one heap reading per run.

The harness lived in a session scratch directory and is not committed:
a Playwright script modelled on the project's `tools/machine/check_page.py`,
serving `_build-page/` through request interception, with the page script
and tracker described under Method.
