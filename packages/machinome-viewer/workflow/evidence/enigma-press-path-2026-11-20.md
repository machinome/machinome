# Enigma I: what a click does before the first frame

A viewer-side measurement on a committed mechanical project's own page,
taken to size the third finding of `workflow/warts.md`'s "Enigma I
(2026-11-20…)" section before a change is cut from it. No project or
framework source is copied here; the page is an ignored build artifact of
the project.

## Pinned inputs

- Project `enigma-i` at `081f4e6`, `_build-page/`, manifest SHA256
  `a8769deec38e3fbf0dca2b826ef4b7779d29d2137ad7977e2f34ed9d58326fc0`.
- Viewer source at `fd334597` (`keep-a-live-model-parsed` and
  `rebuild-only-changed-flexible-parts` integrated), built unminified from
  the widget's own entry with a handle on the scene, and with
  `WidgetTree.prototype.update` (outermost calls only) and
  `FlexibleShape.prototype.evaluate` wrapped to count calls and sum their
  time.
- Headless Chromium through Playwright on an AMD Ryzen 9 5900X virtual
  machine, no GPU. Every WebGL draw call is counted and not executed, so the
  times are script only.

## Method

Each instruction is its own button in the clocked panel, pressed by
`element.click()`; the click's synchronous duration is "the press task".
The counters are read before the click, right after it and at the end of the
observation, which gives the work inside the press task and the work in the
animation frames after it. Between frames a tracker compares every mesh's
world matrix and position-attribute version with the previous frame, which
gives the frames in which the picture changed and when they began, counted
from the click. Single run. The renderer's own time was not separated: in
three.js r156 `render` is an instance method, and the wrap on the prototype
did not take.

## Inside the press task

| Instruction (declared seconds) | Press task, ms | Tree updates in it | Time in them, ms | Of which flexible evaluations, ms | Remainder, ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| Key B (0), a different key | 155 | 1 | 100 | 45 | 55 |
| Press (2) | 381 | 2 | 320 | 204 | 61 |
| Release (2) | 376 | 2 | 315 | 194 | 61 |
| Right wheel on (0.4) | 249 | 2 | 202 | 91 | 47 |
| Right wheel back (0.4) | 261 | 2 | 210 | 92 | 51 |
| Open flap (1.5) | 48 | 2 | 5 | 0 | 43 |
| Close flap (1.5) | 52 | 2 | 5 | 0 | 47 |

A drawn instruction updates the tree twice inside the click: once at the
transition's end, in the request's pose hook, and once at its origin, as the
drawing's frame 0. An instruction of no duration updates it once. The
remainder holds the request itself, the panel's rebuild and two calls of
`renderer.render`, whose bookkeeping is about 25 ms each on this page (an
idle frame's script).

## The frames after it

| Instruction (declared seconds) | Frames that changed the picture | They began, ms after the click | Script per such frame, ms |
| --- | ---: | --- | ---: |
| Press (2) | 9 | 382, 571, 782, 1000, 1219, … | 193 |
| Release (2) | 9 | 378, 571, 760, 955, 1158, … | 195 |
| Right wheel on (0.4) | 2 | 250, 382 | 79 |
| Right wheel back (0.4) | 2 | 262, 334 | 83 |
| Open flap (1.5) | 44 | 49, 73, 111, 145, 176, … | 30 |
| Close flap (1.5) | 45 | 53, 81, 126, 161, 196, … | 29 |

A wheel step declared at 0.4 s begins its first frame 0.25 s after the
click. `drawingFrame` advances the transition by the loop's wall delta since
the previous frame, which contains the press task, so that first frame is
already drawn at about 0.6 of the travel and the second lands the step.

## A key press frame, by subtraction

Over the nine changing frames of the Press, the tree updates took about
1,450 ms (1,707 ms over all 74 updates, less about 4 ms for each of the 65
that moved nothing), of which the flexible evaluations took 897 ms. Against
193 ms a frame that is about 160 ms in the tree update (100 ms in the
flexible evaluations, 60 ms in the transforms) and about 30 ms elsewhere.
A key selection's 86 flexible evaluations with nothing rebuilt cost 45 ms,
so about that much of the 100 ms is the evaluation of parameters and the
rest the rebuild of the parts that change. These are subtractions from one
run, not separate measurements.

## Not measured

The renderer's own time; any GPU's frame time; a browser other than
Chromium; the left and middle wheels; what the frames would cost with the
press task shortened.
