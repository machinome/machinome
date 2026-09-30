## Why

Two findings of 30 September 2026 in `workflow/warts.md`:

- "The React stage", wart 4: **every pose repaints the whole page.** Four
  animation frames per pose (the old page did it only for fresh poses,
  pictures and source-only frames): the fixture tour captures 567 frames at
  1280×720 in about two minutes with the viewer double. A long 1080p film
  pays it on every frame.
- "Cut and Advance, version 2", wart 5: **the render took 638 s for 1769
  frames at 1080p** (about 2.8 frames a second), the whole film recaptured
  because the template's bundle is a common key. Every pose repaints; the
  render itself is where a film's time goes now.

The episode is *Cut and Advance* (the Leonardo project, version 2,
30 September 2026): every change to its template recaptures the whole film,
and every captured frame waits for a whole-page repaint whether or not
anything but the mill moved.

Measured before any change, on the fixture tour at its output size
(1280×720, 30 fps, 567 frames, the viewer double; the capture loop of
`render`, `pose(t)` then `page.screenshot()`, timed in the page with
`performance.now()` and in Node around each call): the loop took
**116.1 s, 4.89 frames a second**. The page's `setFrame` ran 778 times (the
extra poses are the same-instant captures a transition or a faded mark is
composed from) and repainted 778 times, **43.5 s**, 55.9 ms a pose; the
commit took 0.32 ms a pose, posing the views 3.0 ms, decoding pictures
0.03 ms, measuring 0.13 ms. The compositions of transitions and blends
repainted 194 more times, 10.8 s. The screenshots took 30.8 s. The whole-page
repaint is the largest single cost of a frame. A probe of the rule proposed
below, run in the unchanged page (it computed the decision and repainted
anyway), found that **207 of the 778 poses** changed nothing outside the
views' canvases since the last repaint; serializing the page for the
comparison cost 0.04 ms a pose. The tour is dense with cues (typing,
reveals, moving marks, transitions and blends, whose poses always change
the page), so it is the lower end of what a film saves; a film's held shots,
where only the model moves, save the most.

What the film does with the result: its next render after a template change
waits for a repaint only on the frames whose words, marks, pictures or layout
change. After this change merges, *Cut and Advance* is re-rendered and its
638 s compared (the orchestrator's; owed, not claimed here).

## What Changes

- **A pose waits for what can change the picture, and for nothing else.**
  `setFrame` ends with the whole-page repaint only when the frame is fresh
  (a proof pose of `preview`), when a view was mounted, placed again or its
  box resized on this pose, or when what the page draws outside the pixels
  of its canvases (its elements, their attributes and text) differs from
  what it drew at its last repaint. A pose that changes only the pixels of
  the views' canvases requests no animation frame. `compose` and
  `composeMarkBlend` keep repainting every time, and the pose after a
  composition always repaints, since it empties the transition layer.
- **A browser test pins the rule** with the viewer double: a frame posed
  again, and a frame of the view alone posed at another instant, request no
  animation frame; a frame whose title changes its words repaints, and
  posing A, then B, then A gives identical pixels for A.
- **Records**: ADR-004 amended in place with a dated section (the rule is a
  decision); `docs/stage.md` where it says the stage repaints; the runtime's
  comments; `CHANGELOG.md` with the measured numbers; spec deltas.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `react-stage`: a new requirement, "A pose waits for what can change the
  picture".
- `test-suite`: the browser proofs of the stage include the rule.

## Impact

Code: `stage/runtime.tsx` (`setFrame`, `poseViews`, `repaint`), the comment
in `src/render.mjs`'s `show()` that says every pose repaints;
`test/browser/stage.test.mjs`. The runtime is bundled into every film's
stage bundle and `src/render.mjs` is hashed into the shot cache's common key,
so every film recaptures once, as every change to either does. No format,
document, schema, refusal or command option changes.

## Non-goals

No change to the shot cache or its keys (the bundle stays a common key: a
template change may change every frame); no parallel capture; no change to
the screenshot format; no change to the canvas wait or its bound; no change
to how a repaint is made (the background flip over two pairs of animation
frames), only to when. Real-viewer timing is the orchestrator's, after the
merge. No publication, push or paid request.
