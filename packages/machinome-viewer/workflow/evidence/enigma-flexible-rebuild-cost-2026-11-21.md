# What a flexible part costs around its evaluator, Enigma I, 21 November 2026

Opening evidence for `rebuild-a-flexible-part-for-less`, written by the
reviewing agent before the proposal. Measured facts with their limits;
nothing here is a design.

## Where the finding comes from

The Enigma I reconstruction (`enigma-i` at `081f4e6`), as its page is built
by the project's own tools, in the viewer at framework commit `cb0a5958`
(after `evaluate-a-pose-in-one-flat-pass`). The page has 426 flexible parts.

Pressing a key draws a two-second transition. On each of its frames
`tree.ts`'s `updateShapes` visits the 86 flexible parts whose parameters
read the press. `flexible.ts`'s `evaluate` reads their 36,415 parameter
expressions, finds that six or seven parts took new values, and rebuilds
those: about one million vertices a frame (two wires of 335,258 vertices
and 3,604 parameters each, three parts of 118,106 vertices, one of 76,826,
one of 61,466, two small ones).

## What was measured

Headless Chromium (Playwright), the page's own files, WebGL draw calls
counted and not executed, so every time below is script time on the
measuring machine (a virtual machine, one run each). The viewer was built
unminified from its source with `src/flexible.ts` replaced by a copy
carrying timers and switches, so the variants below ran in one page load,
each over a Press and a Release.

Script per changing frame, in milliseconds, as shipped:

| | Press | Release |
|---|---|---|
| The frame | 111.2 | 111.5 |
| The tree update | 84.7 | 98.9 |
| of it, the flexible parts | 63.3 | 77.2 |
| reading the parameters | 16.3 | 17.3 |
| comparing them with what was built | 0.3 | 0.3 |
| the values object for the evaluator | 0.7 | 0.7 |
| molejo's `evaluate` | 30.4 | 40.3 |
| the bounds | 15.6 | 18.6 |
| Rendering, averaged over all frames | 25.6 | 26.6 |

Run again at the end of the same page load: 115.8 and 110.7 ms a frame.

Read from the source:

- **The parameters.** `evaluate` reads them with
  `this.params.map(([, expression]) => evalExpr(expression, scope))`, and
  `evalExpr` (`evaluator.ts`) is
  `withExpressions(() => valueOf(prepare(expression), scope))` with a
  conversion to a number. Each parameter therefore pays one lookup of its
  text by `prepare` and one `withExpressions` scope, on every frame, for
  every visited part, whether or not the part is then rebuilt: 36,415 a
  frame here, for six or seven parts rebuilt.
- **The bounds.** After a rebuild `evaluate` calls
  `geometry.computeBoundingBox()` and `geometry.computeBoundingSphere()`.
  In three.js 0.156.1 the first is one pass of
  `Box3.setFromBufferAttribute` (`expandByPoint(_vector.fromBufferAttribute(...))`
  per vertex); the second makes that pass again into a box of its own for
  the centre, then a third pass for the largest squared distance. Three
  passes over a million vertices through the attribute's accessors. A CPU
  profile of the Press puts 15 ms a frame in `setFromBufferAttribute`
  alone.

## The prototypes

`enigma-flexible-rebuild-cost-2026-11-21.patch`, beside this file, is both
as a diff against `src/flexible.ts` (apply with `git apply -p1
--directory=packages/machinome-viewer/machinome/viewer/web/widget`). It was
built with esbuild and never type-checked.

1. **The bounds in two passes over the array.** One loop over the
   `Float32Array` for the box, a second for the sphere about the box's
   centre, written into the geometry's `boundingBox` and `boundingSphere`.
2. **The parameters read by prepared node.** The expressions are prepared
   once and their node ids kept with the store's generation
   (`expressionGeneration()`), prepared again when the generation differs;
   a frame reads them with `valueOf` inside one `withExpressions` scope for
   the whole part, with `evalExpr`'s conversion. The values object handed
   to molejo is kept between rebuilds. `admit` was left on `evalExpr`.

Script per changing frame, in milliseconds, Press and Release:

| Variant | The frame | Reading the parameters | The bounds | Pictures in the two seconds |
|---|---|---|---|---|
| As shipped | 111.2, 111.5 | 16.3, 17.3 | 15.6, 18.6 | 19, 17 |
| Bounds in two passes | 96.0, 102.2 | 17.2, 16.8 | 4.7, 5.4 | 20, 19 |
| Parameters by node | 104.4, 111.8 | 10.3, 9.6 | 17.0, 19.3 | 19, 17 |
| Both, with molejo's evaluator replaced too | 64.1, 65.3 | 9.4, 9.9 | 4.6, 5.2 | 30, 28 |

The last row also carries a prototype of molejo's evaluator that allocates
nothing per ring; that work has since been done in molejo's own repository
(`refill-without-allocating`, on its `main`, unreleased) and is no part of
this finding. With that evaluator alone the frame was 80.2 and 85.2 ms, so
the two prototypes here account for about 16 to 20 ms of the difference to
the last row. For the parameters taken alone, the component's timer shows
the gain and the whole frame's figure does not rise above the run-to-run
spread (the Release reads 111.8 against 111.5).

Checked in the same page load, during presses, releases, key selections,
wheel steps and a flap, each prototype against the shipped path on the
same inputs, with `Object.is`:

- 349 rebuilds' bounds, ten numbers each (the box's two corners, the
  sphere's centre and radius), against three.js's own: no difference;
- 2,112,070 parameter values against `evalExpr`'s: no difference.

## Limits

- Script time on one virtual machine, single runs. No GPU was involved and
  nothing was measured on a maker's hardware.
- The bounds were compared on what this page's parts produce: finite
  positions in non-empty arrays. Not compared: an empty position array, a
  position that is not finite (three.js logs an error when a bound comes
  out `NaN`; the prototype logs nothing), a zero of either sign.
- The parameter prototype was compared on values only. Not examined: what
  the suite's resolution counts (`expressionMetrics().resolutions`) become
  when a part's parameters are read in one scope; the store being
  reclaimed between two evaluations beyond the generation check; `admit`,
  which the prototype leaves reading by text, so the two entry points no
  longer share one reader.
- Reading the parameters is paid by every visited part, 86 here, for six
  or seven rebuilt. The prototype shortens each read; it does not reduce
  how many are made.
- Not prototyped: the nodes the parameter expressions read are not roots
  of the flat pass, so the walk still computes them, about 9 ms a frame in
  the profile.
- The Enigma document is a project's and is not in this repository; the
  comparison's inputs cannot be committed here.
