## Context

Line numbers are the base's (`56de33dd`), in `machinome/viewer/web/widget/src/` unless a file is named.

In the `continuous` render mode `viewer.ts` gives three.js one loop (`renderer.setAnimationLoop`, 2063-2103). On every animation frame it computes the wall seconds since the previous frame, advances the ramps (`drivers.tick()`), polls the hover (`partSurface.pollHover()`), and then either hands the frame to a running program (`runtime.frame(elapsed)`) and draws, or advances the clock (`clockFrame`), the drawing of a request (`drawingFrame`) and the timeline (`setTime(advance(...))` when `playing`), calls `tree.update(scope(), { time: playing, drivers: movedDrivers })` and draws. Neither the update nor the draw depends on anything having changed. Sixteen other places in the file draw explicitly, after a change they make (645, 657, 1114, 1121, 1245, 1315, 1437, 1502, 1520, 1712, 1730, 1865, 2172, 2188, 2251, 2272); that is how the `on-demand` mode, which has no loop, shows anything (ADR-077, point 2).

The opening evidence (`workflow/evidence/enigma-idle-frame-cost-2026-11-21.md`) measured on the Enigma I page a still frame at 20 to 23 ms of script, 16 to 19 of it the draw and 3 to 4 the update, every update of the loop naming no change, and 0.1 ms with both skipped from outside; each drawn frame is 3,347 draw calls and 44,819,200 triangles; in the eight seconds after a key press 281 to 338 frames were drawn and 33 to 38 changed anything, the last at 1,982 to 2,043 ms. Its limits: script time on one virtual machine with no GPU, blunt switches during periods the script kept still, no camera move, visibility change or resize sampled, and nothing examined about the expression store, a running program or a playing timeline.

Read from the source for this proposal: the evidence names two things shown only because the loop draws the next frame (a turn of the model and a resize). There are more: a mount and a `reload()` (`replaceTree` draws nothing, 1743-1798), a hover and its end (`presentation.setHover` draws nothing, 847-850; the end can come from a window blur, 2816), the frames of a drawn request (`drawFrame` draws nothing, 1328-1338), the ramps, and an in-place update applied while a running document's new program starts (`reconcile` applies at `tree.ts` 391, `manifestChanged` draws at 2251 after `await startRuntime`, 2237). Decision 1 lists every source.

## Goals / Non-Goals

**Goals:**

- The picture on screen is always the current state, shown no later than today, whatever changed it and in whatever order: no stale picture, no cleared canvas, no missed last frame of a motion. First requirement.
- While something moves, every frame is drawn as today. Second requirement's boundary.
- A frame in which nothing the picture depends on changed draws nothing and updates nothing. Second requirement.
- Shown by counts red on the base in a bench that runs the real mount's loop, a detector of everything a draw reads, generated sequences, mutations, and browser pictures compared with a forced redraw; no wall clock and no project export.

**Non-Goals:**

- The `on-demand` render mode (unchanged in every respect, Decision 7); what a frame costs while something moves (a key press, a turn of the model); sharing or merging geometry; anything that lowers a part's resolution or a flexible part's sampling; lights and the renderer's settings; molejo; any project's source.
- Viewer API (stays 30) and document versions (stay 1 to 14): verified in `widget/package.json` (`machinomeViewerApi: 30`, `machinomeDocumentVersions: [1, …, 14]`). No mount option, handle method, document field or published name is added, and every handle method keeps its meaning.

## Decisions

### 1. What a draw reads, and every path that changes it (attack point 1)

`WebGLRenderer.render(scene, camera)` (three.js 0.156.1, `WebGLRenderer.js` 1031 onwards) reads: the camera's world matrix and its inverse, its projection matrix and its layers; the drawing buffer's size, the viewport and the pixel ratio; the scene's background, environment, fog and override material; every object's world matrix, `visible` along its ancestors, layers, `renderOrder` and `frustumCulled`; every mesh's geometry (attributes and their versions, index, draw range, groups) and material; the lights; the clear colour and alpha; tone mapping and output colour space. It writes the world matrices of the scene and the camera first (1044, 1048), and draws nothing while the context is lost (1040).

What in the viewer writes any of that, and what makes a draw follow, today and after:

| Source | What it writes | Today | After |
|---|---|---|---|
| Pointer, touch and wheel on the canvas | the camera, through `OrbitControls.update()` (keys: `listenToKeyEvents` is never called) | the next loop frame draws; nothing listens to the controls | the camera is compared by value at every frame (Decision 2) |
| `rebuildOrbit` (a `setView` with a new up, 458-467) | a new controls object, whose constructor writes the camera | `setView` draws (2172) | unchanged; any camera write is seen by value |
| `setView` | field of view, projection, up, position, near and far, target | draws (2172) | unchanged |
| Framing (`applyFrame`, 1159-1174) in `focusOn`, `manifestChanged`, `replaceTree` | the camera | `focusOn` (1865) and `manifestChanged` (2251) draw; `replaceTree` does not | unchanged where they draw; `replaceTree` by the shown tree's identity and the camera's value |
| Container size: full screen, the inspector's sidebar, host CSS, page zoom | `renderer.setSize`, which assigns `canvas.width` and so clears the canvas even at an equal size (`WebGLRenderer.js` 433), and the aspect | the observer resizes (2049-2061) and draws nothing; the next loop frame draws | the observer's callback draws after it resizes (Decision 3) |
| Device pixel ratio | nothing: `setPixelRatio` is called once, at mount (425) | the loop redraws the same bitmap | not a source; the browser scales the last picture as it scales today's redraws |
| `setDriver`, the driver slider | the tree, through `update` | `driveTo` draws (645) | unchanged |
| A ramp (`trigger` on a posed document, its buttons) | the tree, through the loop's `update` | every loop frame | drawn on every frame while a ramp exists (Decision 5) |
| `setTime`, the timeline slider | the tree | draws (657) | unchanged |
| The timeline playing | the tree | `setTime` draws in the loop, then the loop's update and draw | unchanged, drawn in doubt |
| The clock playing | the tree, through the pose hook | the hook draws (1315), `clockedRequest` draws (1437), the loop draws | unchanged, drawn in doubt |
| A drawn request's frames and its last frame | the tree, through `drawFrame`'s `update` | the loop draws | drawn in doubt, on its last frame too |
| A drawn press itself | nothing: its end pose is judged by `tree.admit` (1308), which writes nothing | nothing drawn | unchanged; nothing raises the revision |
| `machine().move`, `restore`, `reset`; the panel's reset and step | the tree, through the hook | the hook draws; the panel's reset and step draw again (1712, 1730) | unchanged |
| `landDrawing` from a gesture or a handle call | the tree, through `drawFrame` | followed by a draw or by a drawing | unchanged, and the tree raises the revision |
| A run's committed frames (worker, or the in-thread fallback) | the tree, in `onFrame` | `onFrame` draws (1245), and the loop draws | `onFrame` unchanged; the loop draws in doubt while the run is started |
| `manifestChanged` | structure, colours, flexible parts, overlays | draws at its end (2251) | unchanged; its application raises the revision, so a frame between the application and that draw (a new program starting) draws as today |
| `artifactChanged` | replaced meshes and decals | draws (2188), in the task its application ends in | unchanged; the application raises the revision |
| `reload()` and the mount | a new tree in the scene, framing, overlays re-resolved | the next loop frame | the shown tree's identity and the camera's value, at the next frame |
| Models arriving | only into a tree not yet shown: `replaceTree` awaits `next.loaded` before `scene.add` (1757, 1782), a reconcile awaits `created.loaded` before applying (`tree.ts` 453), `artifactChanged` awaits its loads before applying (`tree.ts` 348-356) | covered by the three rows above | the same |
| A colour the model chooses | the mesh's material pointer, inside `update` (`setBaseColor`) | the draw of whoever updated | the holder raises the revision (Decision 2) |
| A hover, and its end (the poll; `endGesture` on blur, on the page hidden, on `pointercancel` and `lostpointercapture`, on a part gone off screen, on `rebuildPartControls`) | material pointers | the next loop frame | the holder raises the revision; the poll's own change is drawn in the same frame, since the poll runs before the frame's decision |
| `highlight` and its put-back | material pointers | draw (1114, 1121) | unchanged |
| `setVisible`, `setRoot`, the navigator, the breadcrumb | `visible` through `applyVisibility`; `focusOn`'s framing | draw (2272, 1865) | unchanged; `applyVisibility` raises the revision |
| A flexible part refilled | its buffers, inside `update` | the draw of whoever updated | the update raises the revision |
| A lost and restored WebGL context | the GPU's state; draws during the loss do nothing | the next loop frame after the restore | a `webglcontextrestored` listener forces the next frame (Decision 2) |
| The page hidden and shown | nothing; animation frames stop while hidden | the first frame after showing draws | a `visibilitychange` listener forces it (Decision 2) |
| Lights, clear colour, background, renderer settings | constant after mount (412-425) | — | not a source |
| `setSpeed`; read-only calls (`view`, `controls()`, `partOnScreen`, `project`, `assembly`, `navigation`, `drivers`, `machine().state`, `run().state`, …) | nothing a draw reads differently (the reads recompute world matrices as render would) | — | not sources; "Reading draws nothing" holds |

Nothing else writes three.js state: a search of `src/` for `scene.add`, `scene.remove`, `.visible =`, `.matrix`, `.position.`, `mesh.material =`, `geometry =` and `needsUpdate` finds the writes in `tree.ts`, `flexible.ts` (buffers, inside `update`), `presentation.ts` (the one assignment of `mesh.material`, 484), the camera in `viewer.ts`, and `replaceTree`'s `scene.add`/`scene.remove` (1778, 1782), and nothing in `inspector.ts`, `navigator.ts`, `fullscreen.ts`, `develop.ts` or `partSurface`'s DOM code. No three.js object crosses the mount handle (ADR-076, point 5), so a host can change the picture only through the handle's methods above.

### 2. How the loop knows, and what makes a missed source unlikely or caught (attack point 2)

The loop draws when one of these holds, checked at the end of its frame:

1. **Never drawn, or forced.** `drawn` is null at mount, after `webglcontextrestored` on the canvas and after a `visibilitychange` to visible.
2. **The shown tree is another object** than at the last draw (`replaceTree`).
3. **The mount's picture revision moved.** One counter per mount, `PictureRevision` in a new `picture.ts`, carried by the mount's `MaterialPresentation` (`presentation.picture`), which every tree of the mount and every flexible part already holds (`viewer.ts` 608, 1754; `tree.ts` 251, 280-281, 286, 418, 451; `flexible.ts` 114), so no constructor gains a parameter and no tree can hold another mount's counter. It is raised by the two owners of what the scene holds:
   - the holder, in `point()` (`presentation.ts` 480-488), the one place a mesh is pointed at another material after it is made, only when the material differs;
   - the tree, in its four public writers: `update` when its change set reaches a node (a transform prepared or a flexible part evaluated), raised before the first write so that a write followed by a throw is still drawn; `applyVisibility`; `artifactChanged` when it applies its replacements; `reconcile` when it calls its application. `admit` never raises it. Everything else in `tree.ts` that writes (`setColor`, `applyMarkings`, `replaceMesh`, `removeMesh`, `removeFlexible`, `orderMarkings`, the loads' attachments into trees not yet shown) runs inside one of those four or before a tree is shown.
4. **The camera moved:** its world matrix (after `camera.updateMatrixWorld()`, which render calls anyway) and its projection matrix, 32 numbers, differ from those at the last draw under `Object.is`, so a `NaN` aspect from a zero-sized container is equal to itself and draws once, not on every frame. Every writer of the camera is seen without being listened to, the controls object `rebuildOrbit` replaces included.
5. **Something moves** (Decision 5).

And independently of the loop:

6. **The size draws itself.** `renderer.setSize` clears the canvas even when the size is unchanged, which no comparison could detect. Its one function, `resize`, has two callers: the observer's callback, which draws after it in continuous mode, and the call at mount (2059), which precedes the first loop frame, drawn because nothing has been. The rule stated for later code: every call of `setSize` is followed by a draw, in its own task where it can happen between two frames.
7. **Every explicit draw stays** and goes through one `draw()`, which renders and records `drawn` (the tree, the revision, the camera's 32 numbers). After the change `renderer.render` appears once in `viewer.ts`, inside `draw()`; a later direct render would cause one redundant draw, not a stale picture.

What this makes of a missed source:

- **Impossible:** a camera write missed (compared by value); a material change missed (one assignment site, which raises; ADR-076 as amended makes the holder the only writer of `mesh.material`); a tree replacement missed (identity); a resize left cleared (its caller draws).
- **Unlikely:** a write to the tree missed. It needs a new writer outside the four methods, or a write to a three.js object outside `tree.ts`, `flexible.ts`, `presentation.ts` and the camera. The ADR records the rule; the unit tests U1 to U5 hold the four methods.
- **Caught:** the detector D of Decision 8 reads everything a draw reads, and after every step of every test followed by an animation frame fails when it differs from what was last drawn; the generated sequences G1 put every host and maker action through it.

**No periodic safety draw.** One every second would cost one draw a second (16 to 19 ms of script a second on the Enigma page, by the evidence), would turn a missed source from a stale picture into one up to a second late, which in use looks like lag and is less likely to be reported, and would not meet the first goal; the tests would still see a missed source because they drive frames with timestamps that never reach the period, but a maker would not. It is listed under alternatives.

### 3. The frame, and not later than today (attack points 3 and 5)

After the change the loop is:

```ts
// continuous only; `moving()` is Decision 5, `changed()` is Decision 2, points 1 to 4
renderer.setAnimationLoop((timestamp: number) => {
  const elapsed = lastTimestamp === undefined ? 0 : (timestamp - lastTimestamp) / 1000;
  lastTimestamp = timestamp;
  const wasMoving = moving();
  const movedDrivers = drivers.tick();
  partSurface.pollHover();
  if (runtime !== undefined) {
    runtime.frame(elapsed);
    if (wasMoving || moving() || changed()) draw();
    return;
  }
  clockFrame(elapsed);
  drawingFrame(elapsed);
  if (playing) setTime(advance(time, elapsed, cycleSeconds));
  if (playing || movedDrivers.size > 0) {
    tree?.update(scope(), { time: playing, drivers: movedDrivers });
  }
  if (wasMoving || moving() || changed()) draw();
});
```

and the observer's callback is `resize()` followed, in continuous mode and not after disposal, by `draw()`. The explicit `resize()` at mount (2059) does not draw: the first loop frame does (`drawn` is null), and a canvas read in the task that resolves the mount stays as it is today (blank, nothing drawn yet). The two listeners are installed with the loop and removed by `dispose()`.

**No source is drawn later than today.** A source that draws in its own task still does. Every other source was drawn by the next loop frame and is drawn by it now: a change made between two frames raises the revision, replaces the tree or moves the camera before that frame's decision, and a change the frame makes itself (the poll's hover, a ramp, a drawing's pose, the timeline, the clock) is made before the decision at the end of the frame. A resize is drawn earlier than today: ResizeObserver callbacks run after the animation-frame callbacks and before the paint of the same rendering update (HTML, "update the rendering"), so today the frame in which the canvas is resized is painted cleared, the first frame after every mount among them (the observer's first observation clears it after the loop's first draw), and after the change it is painted drawn. That is a visible difference, towards the first goal; B3 shows it in Chromium.

**The last frame of a motion is drawn.** `wasMoving` is read before the frame's work, so the frame in which a ramp lands, a drawing reaches `done`, a refused clock frame stops the transport or a run's last tick commits is drawn whatever else holds; its pose also raises the revision.

**Two changes in one frame cost one draw:** the loop draws at most once a frame. Explicit draws are today's, one per call that draws.

**Wall time.** The loop keeps running on every animation frame and does everything it does today except the update named in Decision 4 and the draw. `lastTimestamp` is set on every frame, drawn or not, so every elapsed interval is one frame's, counted once; the ramps read their own clock (`drivers.ts`, `defaultClock`) as today; the clock and the timeline advance only while they play, by the frame's elapsed seconds, as today; a drawing's clock starts at its first frame (`draw-a-press-from-its-first-frame`, Decision 3), which is still the first loop frame after the press. The first frame after a long still period carries one frame's interval, not the period. A hidden page gets no animation frames, today as after, so the first frame after showing carries the hidden interval exactly as today (the clock caps it, `clockAdvance`). Stopping the loop when still would need every source to restart it and would make the first frame after a restart carry the stopped interval unless re-based; the evidence measured a loop that skips both at 0.1 ms.

### 4. The update that names no change (attack point 4)

The loop's `tree.update(scope(), { time: false, drivers: ∅ })` writes nothing to the scene, for every kind of document:

- `WidgetTree.update` (`tree.ts` 722-738) copies a matrix and sets a colour only for the nodes `prepareTransforms` pushed, and evaluates a flexible part only where `updateShapes` finds it touched. Both ask `touchedBy` (855-862), which for that change set returns false for every node: it is not `'all'`, `time` is false, and there is no driver to look up. So `prepared` is empty (797), `composed()` is never called (783-792, only for a node or ancestor that changed), `resolveColor` is not called (795-796), and no flexible part is evaluated (808).
- Posed, timeline (not playing: `time` is `playing`), clocked (the scope reads the bank, but nothing is evaluated), with flexible parts (`flexible.free`) and with colour choices (`colorFree`): the same test decides each, so the same result. A running document never reaches that call: its branch returns before it (2077-2084).

What else the call does, and what skipping it changes:

- **The expression store's scope** (`withExpressions`, `expressions.ts` 498-502; `scoped`, 476-490). Ending the outermost scope resets the store only if a reclamation is pending. None can be pending at the start of a frame: `requestReclamation` (468-474) defers only while a scope is open and the end of that scope consumes it; `releaseExpressions` (611-620) resets at once with no scope open; scopes are synchronous and never span an await (the comment at 492-497). So the loop's scope is not a reclamation point, as the settlement of `keep-a-live-model-parsed` already states ("Ordinary operations -- poses, drawn frames, clocked requests, run ticks, tree updates -- never reclaim", 450-453). The exception is the suite-only switch `EXPRESSION_LIMITS.everyOperation`, under which every outermost scope resets a store at its limit; no test drives the loop, so none relies on it there. Skipping changes no reclamation and no generation.
- **The flat pass** (`prepareFlatPass`, 1702-1741). For a table of 1,000 bindings or more it compares the scope with the store's last scope by value (`ensurePass`, 848-858); equal, it returns; different (after a judged request's `admit` under the end bank, or a pose under another bank), it computes and serves a pass that no write then uses. Skipped, the next update that evaluates computes it under its own scope; the memo is a pure cache (ADR-043), so no number changes. The flat-pass metrics (`flatPassMetrics`: runs, partial runs, declines) count fewer runs over still frames; no test counts them across loop frames, and none can today since no test runs the loop.
- **`lastScope`** keeps the previous scope object instead of an equal new one; it is compared by value, so nothing changes.
- **`scope()`** builds plain objects (`drivers.scope()`, `clockedScope`, `poseScope`) and its `bindings` getter reads `bindingsTable.roots()`, which prepares the table again only after a store reset (`bindings.ts` 29-31, comparing `expressionGeneration()`). Skipped, the next update that reads it does that, under the same generation.
- **The walk itself**: `prepareTransforms` visits every node and builds a path array per node (798-800) even when nothing is touched, which is where the evidence's 2 to 4 ms goes. That is what is saved.

The condition skipped is exactly the change set that names nothing: `!playing && movedDrivers.size === 0`. Every other update of the loop runs as today.

### 5. Motion: the timeline, ramps, the clock, a drawing, a run, a gesture on a part (attack points 7 and 8)

`moving()` is true while the timeline plays (`playing`), a ramp exists (`drivers.ramping()`, a new reader of `ramps.size > 0` on `DriverStore`), the clock plays (`clockPlaying`), a request's transition is drawn (`clockedDrawing !== null`), the run is started (`runtime.running()`), or a gesture on a part is engaged (`partSurface.engaged()`). While it is true at the start or the end of a frame, the frame is drawn exactly as today: the same draws (the timeline still draws twice a frame, once in `setTime` and once in the loop; a playing clock three times, the hook, `clockedRequest` and the loop) and the same updates, except an update whose change set names nothing, which writes nothing (Decision 4). M1 to M6 of Decision 8 record those counts per frame on the base and require them.

What tells the loop each has stopped: `playing` false (the toggle or the bar; a timeline never stops by itself); the ramp map empty (`tick` deletes a landed ramp, 238-241); `clockPlaying` false (pause, reset, a refusal, a drawing starting); `clockedDrawing` null (`done`, `landDrawing`, a republish's `startMachine`); `runtime.running()` false (pause, a refusal). In each case the frame in which it stops is drawn (`wasMoving`), and from the next frame the loop draws only for a change.

A **paused run** joins the rule: its picture changes only through `onFrame` (a `step`, `reset` or `restore` that commits), which draws; the loop's own draw of a paused run's frames drew nothing new.

A **turn of the model** is not in `moving()`: it is the camera, seen by value. Every frame of a turn in which the camera moved is drawn, as today; a frame of a held drag in which it did not move is not, and shows the same pixels (Departures).

**The pointer, per frame, after the change:**

- At rest: `drivers.tick()` (no ramp), `pollHover()` (no cast: `hoverDue` is false; `positionHandles()` only while a part with two freedoms has its handles shown, Found while proposing), `moving()` and the comparison (32 numbers, two integers, one identity). No draw, no update.
- Moving over the canvas: one cast per frame (`pickAt`, which returns at once for a document that declares no control, as the Enigma page does); a change of the hovered part points meshes at other materials, which raises the revision and is drawn in that frame; no change, no draw.
- Dragging a part: the gesture is engaged, so every frame is drawn as today; its requests go to the run, which starts, and whose commits draw.
- Turning the model: `OrbitControls` writes the camera on pointer events; the next frame draws once however many events came; nothing else changes.

### 6. Who relies on a frame being drawn (attack point 6)

- **What a maker sees.** The browser keeps showing a canvas's last presented picture until it is drawn again; a frame that draws nothing leaves it on screen. That is what three.js's own "render on demand" pattern rests on; B2 holds it in Chromium.
- **Page screenshots** (Playwright `page.screenshot`, element screenshots, Chromium's `--screenshot`): taken from the composited page, so they show the last picture. The capture command's continuous path (`capture.py` 240-311: two animation frames, then a page screenshot) is among them. Unchanged.
- **A canvas read in the task of a draw** (after any call that draws, or inside `onFrame`'s task, as `test_calculator_document.py`, `test_lock_document.py`, `test_clearing_document.py` and `test_running_document.py` read): unchanged.
- **A canvas read in a timer or event task in which nothing drew**: three.js's default `preserveDrawingBuffer: false` lets the browser clear the drawing buffer once it is presented; `test_regulator_document.py` records that such a read returns a cleared canvas in the suite's Chromium (its comment at 138-142). Unchanged: nothing drew there today either.
- **A canvas read in an animation-frame callback that runs after the viewer's** (registered after the mount, as `test_regulator_document.py`'s `shot()` does): today it reads the picture the loop drew in that frame, every frame; after, only in frames that changed something, and a cleared buffer in a still frame. **This is the host-visible change.** `captureStream()` likewise yields frames only when the canvas is drawn; what a recorder does between them is the recorder's (not examined).
- **The `on-demand` mode**: unchanged (Decision 7).
- **The studio's floor and the site** mount the bundle in continuous mode. A search of `machinome-studio/` and `machinome.org/` for `toDataURL`, `captureStream`, `readPixels` and `preserveDrawingBuffer`, outside third-party bundles, finds none; the videomaker mounts on demand and takes page screenshots. Hosts outside this workspace cannot be checked.
- **The development server's page** mounts continuous and drives the viewer through the handle's update calls; nothing there reads the canvas.

Whether the change of the fourth case is accepted, or the pilot prefers `preserveDrawingBuffer: true` (a renderer setting outside this change's scope, cost not measured), is the pilot's ("For the pilot").

### 7. The on-demand mode

No loop is installed (2064), so nothing of Decisions 2 to 5 runs. In `on-demand` mode `draw()` is exactly `renderer.render(scene, camera)` and records nothing, the observer's callback resizes and draws nothing, and no listener is added. O1 records the base's draw counts per call for a scripted on-demand session and requires them.

### 8. Tests (attack points 2, 9)

**How the suite drives the loop today: it does not.** No widget test calls `mount()`: `inspector.test.ts` and `partSurface.test.ts` say jsdom gives no WebGL context and use seams; only the Python browser tests run the loop. During this proposal a trial file (deleted) showed that the real `mount()` runs in jsdom with `THREE.WebGLRenderer` replaced through `vi.mock('three')`, `ResizeObserver` and `fetch` stubbed and the STL loader mocked: on the base, ten loop frames with nothing changing gave ten renders for a hand-written version 2 document, `regulator` (clocked), `touched` (running, `run.autostart: false`, the default), `state-color/posed` (version 14, a colour choice) and `spinner` (timeline, `autoplay: false`); `WidgetTree.prototype.update` was called ten times with `{ time: false, drivers: ∅ }` for each but `touched` (zero: its branch returns before the update); a `wheel` event on the canvas moved the camera through the real `OrbitControls`; the observer's callback rendered nothing.

**The bench** (`src/draw-on-change.test.ts`, jsdom): `WebGLRenderer` replaced by a counting renderer whose `domElement` is a real canvas, whose `render(scene, camera)` does to the scene graph what 0.156's does before drawing (`scene.updateMatrixWorld()`, then `camera.updateMatrixWorld()` for a camera with no parent), counts and records D's reading; `setSize` sets the canvas's size and counts; `setAnimationLoop` keeps the callback; `setPixelRatio`, `getPixelRatio`, `setOpaqueSort`, `dispose`. `ResizeObserver` stubbed, keeping its callback; the container's `clientWidth`/`clientHeight`, the canvas's `getBoundingClientRect`, `setPointerCapture` and `releasePointerCapture` defined. `fetch` serves documents from a map (fixtures read with `readFileSync`, and hand-written ones). The STL loader mocked as `tree.test.ts` does, deferred where a load must complete later. `WidgetTree.prototype.update` spied, passing through (a prototype spy sees every tree the mount makes). `performance.now` controlled where a ramp runs. Frames are driven by calling the kept callback with timestamps the test chooses. Every export this change adds is read through its module's namespace, so the file loads on the base.

**D, the detector.** `pictureState(scene, camera, canvas)` reads, after `scene.updateMatrixWorld(true)` and `camera.updateMatrixWorld()`: the camera's world and projection matrices and layers; the canvas's width and height; the scene's background, environment, fog and override material; for every object in traversal order its identity, its parent's, `visible`, world matrix, layers, `renderOrder`, `frustumCulled`; for a mesh its material's identity and `version`, its geometry's identity, every attribute's identity and `version`, the index's identity and `version`, the draw range and the number of groups; for a light its colour and intensity. Two readings are compared element by element under `Object.is`, with no rounding; a difference is reported by name. The counting renderer records a reading at each draw; `expectDrawn()` compares the present reading with it. D0, its self-test: after a draw, a write behind the viewer's back to each kind of field (a group's matrix, a mesh's `visible`, a mesh pointed at another material, an attribute's version, the camera, the canvas's size) makes `expectDrawn()` fail naming it. What D cannot see: a material property written in place without its version (`share-one-material-per-appearance`'s R3 holds that rule), a buffer written without its version (three.js would not upload it either), state outside three.js objects, pixels.

**Red on the base, by count:**

- **I1. A still page draws and updates nothing.** For each kind above, plus a posed document with drivers and an instruction, one with a flexible part and one with markings (hand-written): mount, two frames, the observer's callback, then thirty frames: 0 draws and 0 updates. Base: 30 draws, and 30 updates for every kind but the running one (0 there, so its update count passes on the base and its draw count fails).
- **I2. A zero-sized container is still too.** `clientWidth` and `clientHeight` 0 (aspect `NaN`): thirty frames, 0 draws. Base: 30.
- **S0. The first frame after a mount is drawn**, once, and D matches. Holds on the base; it is MU11's test.
- **S1 to S8. Each source drawn within one frame and not after.** For each: the change, one frame, `expectDrawn()`, then ten frames with 0 draws. Red on the base by the ten frames, which draw ten times there. S1 a `wheel` event; S2 a pointer drag on the canvas (OrbitControls rotates); S3 a resize: the observer's callback with a new size draws once inside the callback (base: 0, red at once), then nothing; S4 a hover on `touched` (pointer moved over a control's part with the canvas's rectangle defined, so the cast hits; the next frame draws and the part's meshes point at the hovered material) and its end by moving away; S5 the hover ended by the window's `blur`; S6 `reload()`; S7 `webglcontextrestored` dispatched on the canvas; S8 `visibilitychange` with `document.hidden` false.
- **S9. Every call that draws still draws before it returns, and nothing after:** `setView`, `setDriver`, `setTime`, `setVisible`, `setRoot`, `highlight` and its put-back, `artifactChanged`, `manifestChanged`, `machine().move`, `restore`, `reset`: the render count rises inside the call (holds on the base), D matches right after, and ten frames draw nothing (red on the base).
- **S11. A republish drawn while its new program starts.** On `touched`: `manifestChanged()` with the served document moved, and the new program's start held pending (`RunRuntime.start` spied to return the real run with its `ready` deferred), so that the call has applied the update and not yet drawn; one frame: drawn once, and D matches; then the start released, the call returns having drawn, and ten frames draw nothing. This is the one case in which a write of the tree is followed neither by an explicit draw in its task nor by a motion, so the tree's own raise is what draws it. Holds on the base at its first frame (the loop draws); red on the base by its ten-frame tail. If the bench cannot hold the start pending, that is reported with what was tried, not replaced by another assertion.
- **S10. Two changes before one frame cost one draw:** a wheel event and a hover before one frame: that frame draws once and D matches. Base: one loop draw too (holds); the idle tail after it is red on the base.
- **W1. Still frames lose and double no time.** Sixty still frames of 16 ms, then the clock played on `regulator`: after its first playing frame the clock's value in `machine().state()` has advanced by that one frame's seconds times the speed, not by the still period, as on the base; sixty still frames, then a drawn press of 0.2 s on a hand-written clocked document: the drawing's first frame stands at the origin and it lands on the frame whose elapsed seconds since that first frame reach 0.2, as on the base; a ramp across still frames lands on the frame `performance.now` reaches its end. Recorded on the base and required; it holds on the base.

**During motion, recorded on the base (attack point 7):**

- **M1 to M6.** For a ramp of an integer driver slow enough that some frames move no value; the timeline played on `spinner` and paused; the clock played on `regulator` and paused; a drawn press of an instruction on an integer input; a run started on `touched` and paused; a press held on a part of `touched` without moving: the applier runs each on the base and writes into the test, per frame, the number of draws and of updates whose change set names something; the implementation must give the same, the frame each motion ends in included, and then ten frames with 0 draws (red on the base, which draws them).

**The owners count (attack point 2):** `src/picture-revision.test.ts`, reading through the namespace (red on the base at the absent `picture`, which is expected):

- **U1.** `update` raises the revision when its change set reaches a node, by a transform or a flexible part, and not when it reaches none (empty, or a driver no expression reads); a throwing update that wrote raises it.
- **U2.** `admit` never raises it. **U3.** `applyVisibility` raises it. **U4.** `artifactChanged` raises it when it applies, not while its loads are pending, not when they fail. **U5.** `reconcile` raises it when it applies, not before, and a refused one does not.
- **U6.** The holder raises it on every pointer change (hover, highlight, put-back, `setBaseColor` to another colour value, `recolor`, `forget`) and not on a call that points nothing elsewhere (the same hover again; a normal material under a lit highlight).
- **U7.** The camera comparison: equal for equal numbers, `NaN` equal to `NaN`, `-0` different from `0`, any one of the 32 different makes it different.

What U cannot see: a writer outside these methods; whether the loop reads the revision (S4, S5, S6).

**G1. Generated sequences.** 200 seeded sequences of 30 steps, each followed by one to three frames of 1 to 40 ms, over a posed document (drivers, an instruction, a timeline, a colour choice, markings, a flexible part), `regulator` and a hand-written clocked document with a drawn instruction, and `touched` with its run paused: `setView` (random camera, sometimes a new up), a wheel event, a pointer drag, a resize, `setDriver`, `setTime`, `trigger` then frames until it lands, `highlight` in each treatment and its put-back, `setVisible`, `setRoot`, a hover and its end (on `touched`), a blur, `reload()`, `manifestChanged()` with the served document recoloured, moved, grown or shrunk, `artifactChanged()`, `machine().move`, `trigger`, `restore`, `reset`, the clock played and paused, the run started and paused, `webglcontextrestored`, `visibilitychange`. After every frame D matches; after every sequence twenty frames draw nothing and update nothing. What it would not see: a source not in that vocabulary (full screen itself, which reaches the viewer only as a resize; a real device pixel ratio change); the browser's order of resize observations and animation frames; a worker's timing (the suite runs the run in thread); a real loss of the context; a material property written without its version; pixels; and, by design, a missed revision during a motion, which is drawn anyway.

**Mutations.** Each applied to the implementation, its tests run and the output kept, the implementation restored byte for byte: MU1 the camera left out of the comparison: S1, S2 red. MU2 the holder's raise removed: S4, S5, U6 red. MU3 the tree's identity left out: S6 red. MU4 the observer's callback draws nothing: S3 red. MU5 the restore listener removed: S7 red. MU6 the visibility listener removed: S8 red. MU7 the empty update not skipped: I1 red (updates). MU8 the loop's draw unconditional: I1 red (draws). MU9 each of the six terms of `moving()` removed in turn: M1 (ramp), M3 (clock: a playing clock frame draws three times on the base and twice without it), M4 (drawing), M5 (run), M6 (gesture) red; the timeline's term is an equivalent mutant, since every playing frame writes `$t`-reading nodes and so raises the revision; that is reported, not hidden. MU10 each of the tree's four raises removed in turn: U1, U3, U4, U5 red, and S11 red for `reconcile`'s; for the other three no mount-level test turns red, because each of those writers is followed by an explicit draw or happens during a motion, which is drawn anyway; reported. MU11 `drawn` initialised to a reading instead of null: S0 red. MU12 `Object.is` replaced by `===`: I2 red. MU13 the explicit draw in `setVisible` removed: S9 red. MU-W (browser) the camera left out of the comparison and the bundle rebuilt: B2's orbit step red; the observer's draw removed and the bundle rebuilt: B3 red.

**On demand.** **O1**: an on-demand mount of a posed and of a clocked document, scripted `setTime`, `setView`, `setDriver`, `machine().move`, `restore`, `reset`, `highlight` and put-back, `setVisible`, the observer's callback and the two events: the base's draw count per call, recorded, reproduced; `setAnimationLoop` never given a function; the observer's callback draws nothing. Holds on the base.

### 9. The requirement's words (attack point 9)

The delta adds one requirement to `viewer-package`, "A continuous viewer draws a frame only when its picture has changed", stating what can be observed: the picture is the current state; when it is shown; a still frame draws and re-evaluates nothing; motion is drawn as before, its last frame included; a resize is drawn in its frame; a restored context and a page shown again are drawn; calls that draw still draw; time advances by wall time; on demand unchanged; and what a read of the canvas in a frame that drew nothing gets. No ratified sentence changes. Every baseline sentence found that promises or assumes a draw in continuous mode, and why it holds:

- "A host mounts the viewer and receives a handle": `dispose()` stops rendering and no later frame or resize callback runs; `reload()` "the new tree renders" (S6).
- "A host reads and drives the document's drivers": `onDriverChange` "called once per changed driver per animation frame while values change" is `drivers.tick()`, which still runs every frame; "that frame" re-evaluation of `setDriver` is `driveTo`'s, unchanged.
- "A host triggers declared instructions": ramps "advanced by the viewer's animation loop on wall-clock elapsed time", whole "at every frame": every frame of a ramp is drawn.
- "The viewer evaluates flexible geometry per frame": recomputation only "on frames where a free variable ... changed"; skipping an update that names nothing keeps it.
- "The viewer executes a document's published program": "Rendering SHALL NOT advance it: a dropped display frame SHALL drop display and never a step", and "the committed bank a later frame draws": a commit draws in `onFrame`.
- "A maker runs an elapsed clocked machine on screen": "exactly ONE request per rendered frame", and the stall scenario: while the clock plays every frame is rendered.
- "The viewer plays a clocked instruction as one drawn transition": "A press SHALL render no picture itself", "the first frame of the drawing is the next picture the viewer renders for it", the first frame standing at the origin and the duration counted from it, "At each frame the viewer SHALL pose …", the last frame at the reported end: a drawing is drawn on every frame and on the frame it lands; the press raises nothing (`admit`); "A step of the clock is not drawn … the transport advances it on a rendered frame": unchanged.
- "A maker watches the model full screen": "The canvas SHALL follow the full-screen size": a resize draws.
- "A host highlights parts and sets the others back": draws before returning, and the put-back draws: explicit, unchanged.
- "An on-demand viewer poses and draws a clocked machine" and `snapshot-capture`'s "Eligible stills are captured without a continuing viewer frame loop": on demand unchanged; the continuous capture path screenshots after two frames, both drawn (the first frame and the observer's draw).
- `inspector-layout`: "the viewer's canvas is wider than it was, framed and projected for its new size", "the canvas SHALL follow the pane's size": resizes draw.

No scenario reads differently.

### 10. The picture: the Python suite (attack point 10)

New, `tests/test_draw_on_change.py`, in that suite's way (served fixtures, the built bundle, headless Chromium with SwiftShader):

- **B1. A still page draws nothing.** WebGL draw calls counted by wrapping the context's draw methods, as `test_widget_e2e.py`'s `test_reading_positions_draws_no_frame` does: after a mount and ten frames, thirty frames make 0 draw calls, for `marked`, `regulator` (clock paused) and `touched` (run paused). Red on the base (thousands).
- **B2. Every kind of change reaches the canvas.** On `touched` (`run.autostart: false`) and `regulator`: after each change, three frames, a canvas screenshot A; then `viewer.setTime(0)` (every step holds the timeline at 0, so it re-poses nothing and draws the same state; a pure redraw on any kind of document), a screenshot B; A must equal B exactly, and A must differ from the previous step's picture where the step changes what is seen. Steps: a mouse drag (orbit), a wheel, `setView`, `setRoot` and back, `setVisible` off and on, `highlight` kept, dimmed and ghosted and each put back, a hover on a dial and away (cursor `pointer` checked), the host's width changed and restored, `reload()`, the context lost and restored through `WEBGL_lose_context`, `run().step(240)` after a `trigger`; on `regulator` `machine().move`, `restore`, `reset`, the clock played for half a second and paused. Full screen where headless Chromium grants it; otherwise that step is skipped with its reason. It passes on the base, which draws every frame: it pins that nothing goes stale. Ten frames after each step make 0 draw calls (red on the base).
- **B3. A resize shows the picture in its own frame.** A second `ResizeObserver` on the host, made after the mount and so notified after the viewer's, reads `toDataURL()` in its callback: after the mount's first observation and after a change of the host's width, the read is not the blank canvas of that size and equals the canvas after `setTime(0)`. Red on the base (blank: the canvas was resized and not drawn).
- **B4. A press is drawn until it lands, and not after.** On `tests/fixtures/calculator` (`'Stroke'`, 2 s): draw calls per frame from the click to the landing are above 0 on every frame, as on the base; the thirty frames after the landing make 0 (red on the base).

What B cannot see: what a real GPU does; a source not scripted; a device pixel ratio change; a browser other than headless Chromium that might not keep a canvas's last picture while nothing is drawn.

**The existing tests,** each read for this proposal:

- `test_regulator_document.py`: **does not hold.** Its `shot()` reads the canvas in an animation-frame callback after the viewer's (its comment, 138-145); `steppedShot`, `resetShot`, `quarterShot` and `halfShot` follow a change that drew in its own task, so in their frame nothing changes, nothing is drawn, and they read a cleared buffer: `stepped_period`, `reset_to_rest` and `two_instants_differ` turn false. Restated: `shot()` becomes `viewer.setTime(0)` followed by `toDataURL()` in the same task, every shot alike, every assertion kept. The restated file is run on the base bundle first, where it must pass.
- `test_calculator_document.py`: holds. Its shots are read in the task of a handle call that draws, or in a frame continuation during a drawing (drawn) or on the frame it lands (drawn); its draw counts are inside a click's task; `idleStable` uses `partOnScreen`, which updates the matrices itself.
- `test_lock_document.py`, `test_clearing_document.py`, `test_running_document.py`: hold. The rest shot is read before any frame (blank, as today, since the mount draws nothing synchronously); the others in the continuation of `onFrame`'s task; the hover and visibility checks are page screenshots.
- `test_asset_load_order.py`, `test_state_color.py` (on demand, and continuous with element screenshots), `test_clocked_pose_admission.py` (on demand; its continuous case compares screenshots after two frames), `test_widget_e2e.py` (Chromium `--screenshot` with a virtual-time budget, page screenshots, `controls()` after two frames, the on-demand draw count), `test_time_drive_document.py`, `test_carriage_document.py`, `test_direct_motion.py`, `test_profile_document.py`, `test_source_timing_browser.py`, `test_real_time_playback.py`, `test_server.py`, `test_capture.py`: hold; they compare page screenshots or read on demand.
- `test_curta_drawing.py`: needs a project export and skips without it; its canvas lengths are printed, not asserted; its frozen photograph stops the loop during a drawing, whose frames are drawn. Holds.
- `test_bundle.py`, `test_cli.py`, `test_currency.py`, `test_documentation.py`, `test_licence.py`, `test_machinome_identity.py`, `test_packaging.py`, `test_session.py`, `test_version.py`: draw nothing. Hold.

## What the Enigma should show (predictions)

Predictions, which the reviewer's measurement decides. They rest on the evidence's figures for this page and on reading the source, not on scaling one figure:

- No pixel differs from the base's in any view of the scripted sequence, each compared after waiting with a forced redraw of the same state.
- In a still period: 0 draws and 0 tree updates a frame, and script per frame near the evidence's 0.1 ms with both skipped (the change adds a camera matrix update and a comparison of 32 numbers, not measured).
- After a key press: draws on every frame from the click until the last drawing lands (the evidence puts the last changing frame at 1,982 to 2,043 ms), the same draws per frame as the base's in that interval, and none after it.
- The frames of a press cost what they cost today; a press itself costs what it costs today.
- A turn of the model: one draw per frame in which the camera moved. A resize: one draw per observation, and no cleared frame.

## Departures from the basis

- **A turn of the model is judged by the camera's value**, not by "a pointer gesture is active". Every frame of a turn in which the camera moved is drawn, as the basis has; a frame of a held drag in which the camera did not move is not, and shows the same pixels. The value comparison sees every writer of the camera without a listener; a listener on the controls' `start` and `end` would be lost with the controls object `rebuildOrbit` disposes, a `setView` with a new up during a drag leaving the gesture marked as active.
- **Three sources the basis does not list are added:** a restored graphics context and a page shown again force the next frame; a resize is drawn in its own callback. The last makes the frame of a resize show the picture where today it shows a cleared canvas, a visible difference towards the first requirement.
- Not departures but more than the basis says: a gesture on a part is in doubt as the basis has, and also a ramp, the clock, a drawing and a started run, while a paused run joins the rule; the explicit draws stay unconditional.

## For the pilot

- **A canvas read in a later animation frame.** A script that reads the canvas's drawing buffer in an animation-frame callback after the viewer's, relying on it having drawn in that frame, now reads a cleared buffer in frames in which nothing changed (Decision 6). Reads in the task of a call that draws, page screenshots and what a maker sees are unchanged, and no host in this workspace reads that way; one test of this repository does and is restated. Accepting it is the pilot's. The alternative that keeps such reads working is `preserveDrawingBuffer: true`, a renderer setting outside this change's scope, whose cost was not measured; it would make a read at any time return the last picture drawn.
- **A visible difference:** the frame in which the canvas is resized shows the picture instead of a cleared canvas.
- **No new handle method.** A host that wants a redraw in its own task has `setTime(t)` at the time it holds, or `setView(view())`, which also refits the clipping planes (ADR-077, Consequences). A pure redraw verb would be a new handle method and an API change; it is not proposed.

## Alternatives rejected

- **Flags set at each source in `viewer.ts`:** the place that writes is not where the flag is set, and the source added next is the one missed. Counting at the two owners of the scene, comparing the camera by value and drawing after every resize leave nothing to set in the viewer.
- **Comparing the whole scene by value every frame at runtime** (what D does): it would see a writer the owners do not count, at a cost per frame in the number of objects (3,347 meshes on the Enigma page and their groups; the cost not measured), and it would have to enumerate what a draw reads, which is the list D holds; in the tests that enumeration buys proof, in the bundle it buys a per-frame walk like the one Decision 4 removes.
- **Listening to `OrbitControls`' `change`:** lost with the object `rebuildOrbit` replaces, and blind to `applyFrame` and `setView`; the value comparison sees them all.
- **Stopping the loop when still** and restarting it at a change: every source would have to restart it, and the first frame after a restart would carry the stopped interval unless re-based; the evidence measured the loop that skips both at 0.1 ms.
- **A periodic safety draw:** Decision 2.
- **Making the explicit draws conditional too:** a host reading the canvas after a call that draws would read a cleared buffer, and the on-demand mode would change.
- **Letting motion join the rule** (drawing a drawing's frame only when it moved something): it would save any frame of a motion that moves nothing, and it changes what a frame of a motion costs, which is out of scope, against the basis. The evidence does not show such frames on the Enigma page: its 33 to 38 changing frames, at 51 to 57 ms each, account for the two seconds of a press.
- **Drawing the frame after every explicit draw** so that `test_regulator_document.py`'s way of reading keeps working: a heuristic for one way of reading, which a read two frames later would still miss.
- **`preserveDrawingBuffer: true`:** a renderer setting; For the pilot.
- **A seventh constructor parameter threading a counter through every `WidgetTree`:** three construction sites to keep in step, one missed silently splitting the counter; the holder every tree already shares carries it.

## Risks / Trade-offs

- [A writer of the scene the owners do not count] → the rule in the ADR, U1 to U5 for the four writers, D in every bench test and G1.
- [A browser that does not keep a canvas's last picture while nothing is drawn] → B2 in headless Chromium; other browsers not tested.
- [The host-visible read] → For the pilot; the CHANGELOG says it.
- [A frame that throws stops three.js 0.156's loop] → the new code in the loop throws nothing: a comparison, a counter, a reader.
- [jsdom cannot run the renderer or order observations as a browser does] → B1 to B4 in Chromium; MU-W shows two of them bite.
- [Admitted time] → None claimed beyond the reviewer's measurement.

## Decision record

A new **ADR-080**, "A continuous viewer draws a frame only when its picture has changed", under `workflow/adrs/EXPORT/`, written after the reviewer's measurement and only if it confirms the design. It must record: what the loop compares (the shown tree's identity, the mount's picture revision, the camera's world and projection matrices under `Object.is`) and that it draws when any differs, when forced (never drawn, a restored context, a page shown again) or while something moves (the six terms, at the start or the end of a frame); the owners' rule for later code, that whatever writes what a draw reads goes through the tree's four writers or the holder, which raise the revision, or is compared by value, or draws itself, and that every `setSize` is followed by a draw; that the loop runs on every frame and skips only the update whose change set names nothing, with why that update writes nothing and is not a reclamation point; that every call that draws before it returns still draws; that on demand is unchanged; the canvas read in a later frame and the pilot's decision on it; and the alternatives above with their reasons. It cites ADR-076 (the holder), ADR-077 (on demand, its point 2 and the redraw of its Consequences), ADR-043 (the store), ADR-063 and ADR-064 (the clock's frames and a drawing's frames, unchanged), and this change's design and evidence.

A dated **amendment to ADR-076**, beside its shared-materials amendment of 21 November 2026: the holder also carries the mount's picture revision and raises it whenever it points a mesh at another material.

## Found while proposing, out of scope

- `partSurface.pollHover()` calls `positionHandles()` on every frame, which for each shown handle of a part with two freedoms asks `host.point`, a bounded grid of casts through the scene (`partPoint`, `searchPoint`); a page with such a part selected pays that on every frame, still or not. Unchanged here.
- A playing timeline draws twice a frame and updates its `$t` nodes twice (`setTime` in the loop, then the loop's own update and draw); a playing clock draws three times (recorded by `draw-a-press-from-its-first-frame`). Kept by Decision 5, since motion is out of scope.
- Whether every frame of a key press differs, as the basis says, is not something the evidence decides: its 33 to 38 changing frames at 51 to 57 ms each fill the two seconds give or take a frame, and it did not count the frames of those two seconds that changed nothing. Decision 5 draws them all either way, so the outcome the basis promises holds.

## Open Questions

None for the design. The pilot's decision on the canvas read is listed under "For the pilot".
