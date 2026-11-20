## Context

A flexible part (`FlexibleShape`, `flexible.ts`) owns its molejo spec, its parameter list (`[name, expression]` pairs sorted by name), the free-variable set of those expressions closed over the document's bindings table, and the buffers molejo allocated at its first evaluation. `WidgetTree.update` first prepares every affected transform and copies the matrices into the live groups, then calls `updateShapes`, which walks the tree in order and calls `evaluate(scope)` on every flexible part whose free set the change set touches (`touchedBy`). `evaluate` evaluates every parameter, calls molejo's `evaluate(spec, values, buffers)`, which refills the existing `Float32Array` in place, sets `needsUpdate` on the position attribute and recomputes the bounding box and sphere. Nothing in that path asks whether a value moved.

On the Enigma I page that costs, per frame of a wheel step or a key selection, 86 molejo evaluations over 8.47 million triangles whose data does not change (`workflow/evidence/enigma-flexible-refills-2026-11-20.md`). The pilot has deferred anything that lowers a part's resolution or a flexible part's sampling (`workflow/warts.md`, same section), so the cost has to come from not doing work whose result is already on the part.

## Goals / Non-Goals

**Goals:**

- A flexible part reached by a changed name is rebuilt only when a value handed to its evaluator differs from the one its present vertex data was built from. Otherwise it costs no molejo evaluation, no upload and no bounds pass.
- What is drawn never differs from what a rebuild would draw: a kept part holds exactly the vertex data molejo produces from its spec and its current parameter values.
- The skip and the rebuild are both shown in the widget's suite by counted work.

**Non-Goals:**

- Anything that lowers resolution or sampling, for the picture or otherwise.
- Avoiding the evaluation of the parameters themselves (Decision 4).
- The press path, the drawing load, the expression store, the change-set mechanism for rigid parts, molejo, any project's source.
- Making `updateShapes` atomic against a refusal (see "A pre-existing gap found while reading").
- Viewer API (stays 30) and document versions (stay 1 to 14): verified in `widget/package.json` (`machinomeViewerApi: 30`, `machinomeDocumentVersions`); nothing here touches either.

## Decisions

### 1. The part remembers what its buffers were built from

`FlexibleShape` gains one private field, `built: number[] | undefined`: the parameter values, in the order of `this.params`, that the vertex data now in its buffers was computed from. It is the only writer of those buffers, so it is the only place that can know what they hold. `evaluate(scope)` becomes:

1. Evaluate every parameter into a fresh array `next`, as today. A throw here propagates as today, before anything else happens.
2. If the buffers exist, `built` is defined, `next.length === built.length`, and `Object.is(next[i], built[i])` for every `i`, return. Nothing is written, no attribute version moves, no bounds are computed.
3. Otherwise set `built = undefined`, build the `{name: value}` record from the names and `next`, call molejo, attach the buffers on the first call, set `needsUpdate`, compute the bounds, and only then set `built = next`.

`rebind` sets `built = undefined` beside `freeVars = undefined`. `dispose` does not touch it (see below). `tree.ts` does not change: it still decides which parts are reached, and each reached part decides whether it is rebuilt.

Alternatives rejected:

- *Keep the memory in `tree.ts`, keyed by part.* Splits what the buffers hold from the one object that writes them; every future writer would have to remember a second structure.
- *Compare with a tolerance, or after `Math.fround`.* Molejo computes in double precision from its inputs, so inputs equal in single precision can still round to a different single-precision output; a tolerance draws, however slightly, a shape the expressions do not describe.
- *Compare molejo's output instead of its input* (evaluate into a scratch buffer, skip the upload if equal). It keeps the molejo evaluation, which is the cost, and needs a second position array per part.
- *Keep the memory across `rebind` and compare by parameter name.* It would save rebuilds only on a republish whose spec is unchanged, which rebuilds every part today and is not the finding, and it would need a name-aware comparison where forgetting needs none.
- *`===` instead of `Object.is`.* It calls `-0` and `0` the same; see Decision 2.

### 2. What "the same value" means

Two values are the same when `Object.is` says so, position by position in a parameter list that has not changed:

- **`-0` and `0` differ.** Molejo's output can depend on the sign of a zero (an angle from `atan2`, a reciprocal), so a change of sign rebuilds.
- **`NaN` is the same as `NaN`.** A `NaN` can only be remembered for a parameter the spec does not reference: molejo's `resolve` refuses a non-finite value for a referenced parameter (`values: parameter '…' must be a finite number`), and nothing is remembered from a refused evaluation (Decision 1, step 3). A value the spec does not read cannot change the output.
- **Not a number.** `evalExpr` returns `typeof value === 'number' ? value : Number(value)` (`evaluator.ts`), so every value is a number; `Object.is` would compare anything else correctly in any case.
- **Length or names changed.** The memory is parallel to `this.params`, which only `rebind` replaces, and `rebind` forgets the memory. The length check in step 2 is a guard, not the mechanism.

A consequence measured on the Enigma's own document (method under Decision 4): stepping `operation.right` from 4 to 5, with every other input at the document's declared defaults, leaves 85 of the 86 reached parts with identical values. The 86th, `Enigma/stepping/detent_returns/right` (1,563 parameters, 122,928 triangles), has 635 values that move in the last digits (for example `0.6951934709831846` to `0.6951934709831562`), and molejo's single-precision output for the two value sets is identical in all 184,398 entries. Under this design that part is rebuilt on a right-wheel step, where the evidence file, which compares sampled vertex data, counts it as unchanged. Stepping `operation.left` 17 to 18, `operation.middle` 11 to 12 and `operation.key` 1 to 2 left all 86 identical; `operation.press` 0 to 0.5 left 79 identical and 7 different, consistent with the evidence's median press frame. Only those steps were tried.

### 3. The shape is a function of the spec and the values alone

Read from the bundled molejo, version 0.2.0 (`node_modules/molejo/src/evaluate.js`, resolved by the widget's `"molejo": "^0.2.0"`):

- `evaluate(spec, values, buffers)` parses and validates the spec into a fresh object, reads `values` only through `resolve` for the names the spec references (others are ignored), and reads `buffers` only to check their types and lengths (`checkBuffer`), never their contents.
- It resolves every parameter-dependent quantity before writing a single vertex, then writes every entry of `positions`: `rings × profile` vertices, plus two cap centres for an open path, exactly the length it checked. The index is written only when it allocates.
- It has no module-level mutable state, no randomness and no clock; all intermediate arrays are local and the spec is not mutated.

Equal spec and equal values therefore give bit-identical positions in one JavaScript engine, independent of what the buffers held before. The spec is fixed for a `FlexibleShape`'s life: `reconcile` builds a new one whenever `describes` reports a different `tech` or spec. The bounds are computed from the positions, so a kept part's bounds already belong to its data.

### 4. The cost left behind is accepted

A skipped part still has every parameter evaluated on each frame a changed name reaches it. On the Enigma, the 86 parts reached by `operation.right` or `operation.key` carry 36,415 parameter expressions (52 parts of 42, 17 of 400, 9 of 906, 3 of 1,563, 3 of 2,460, 2 of 3,604). Most are a constant plus one binding name (`(0.0219 + _b1481)`), and a binding's value is computed once per evaluation pass however many expressions read it (ADR-043's pass memo).

Measured on this bench with a temporary single-file vitest script, since deleted, that read the project's manifest (`enigma-i` at `081f4e6`, SHA256 `a8769dee…326fc0`), built its bindings table and the 86 `FlexibleShape`s, and alternated `operation.right` between 4 and 5 over 20 frames, each frame a fresh scope and so a fresh pass, under Node 24.11.1: evaluating the parameters alone took a median of 7.6 ms a frame (6.5 to 61.7 ms; a first run gave 8.1, 7.2 to 72.1), comparing all of them with a previous frame's about 0.01 ms, and the full evaluation of the same parts (parameters, molejo, bounds) a median of 324 ms (247 to 360). This is Node, not Chromium; it counts binding values that a real frame shares with the rigid operations of the same walk, so it is an upper figure for what this change leaves; it was not measured on the page.

About 8 ms against the 30 ms an instruction that rebuilds nothing already costs does not justify a second mechanism (tracking which binding values changed within a pass, or a per-part key over the bindings it reads). The design accepts it.

### 5. Proof by counted work

`flexible.test.ts` already wraps molejo's real `evaluate` in a `vi.fn` spy and counts its calls, and reads the position attribute's `version` (what `needsUpdate` raises and the renderer reads). The bounds pass is counted with `vi.spyOn` on the part's `geometry.computeBoundingBox` and `computeBoundingSphere`. No source-only counter is needed. The new tests, all on `WidgetTree` and `FlexibleShape` with hand-written specs, depending on no project export:

- **A. A changed name that leaves every value as it was.** A spring whose `height` is `min(46.8, (66.8 - valvetrain.lift))` (46.8 at lifts 0 and 3, 36.8 at 30), mounted at lift 0, updated to lift 3 with `valvetrain.lift` in the change set: no molejo call, attribute version unchanged, no bounds pass, positions unchanged. Then lift 30: one call, version risen, bounds computed, positions changed. Red on the base: one molejo call where none is expected.
- **B. Two parts reached by one name, one of which changes.** The spring of A beside one whose `height` is `(46.8 - valvetrain.lift)`, lift 0 to 3: exactly one molejo call, only the second part's version rises. Red on the base: two calls.
- **C. An update of everything at unchanged values.** `tree.update(scope)` with the default `'all'` at the mount's own scope: no molejo call. Red on the base: one call.
- **D. A parameter expression that throws part-way through the list.** Parameters `height: '(46.8 - valvetrain.lift)'` and `z: '(1 + gate.on.x)'`, `z` sorted after `height` and not referenced by the spec. At `gate.on = 1` reading a member of the number `1` throws the native `TypeError` ADR-043 preserves; at `gate.on = 0` the member reads as `undefined` and `z` is `NaN`, which Decision 2 makes equal to itself. Mounted at lift 0 and `gate.on = 0`; the update to lift 3 and `gate.on = 1`, both in the change set, evaluates `height` and then throws, with no molejo call, no version change and positions unchanged; the update back to lift 0 and `gate.on = 0` makes no molejo call. Red on the base: that last update rebuilds.
- **E. `NaN` stays `NaN`.** A part with `height: '46.8'` and an unreferenced `gap: '((valvetrain.lift / 0) * 0)'`, lift 1 to 2: no molejo call. Red on the base.
- **F. A refused molejo evaluation leaves nothing remembered.** With the spy's next call replaced by one that writes `NaN` into the given `positions` and throws, the update from lift 0 to 6 throws; the update back to lift 0 then makes one molejo call and the positions equal the mount's again. Green on the base, which always rebuilds; shown red against the implementation with step 3's `built = undefined` before the call removed.
- **G. `rebind` forgets.** A reconcile to the same spec with `height: '(46.8 - (1.0 * valvetrain.lift))'`, then an update reaching the part at the same lift: one molejo call. Green on the base; shown red against the implementation with the forgetting in `rebind` removed.
- **H. `-0` is not `0`.** A part with `height: '46.8'` and an unreferenced `tilt: '(0 * valvetrain.lift)'`, lift 1 to -1: one molejo call. Green on the base; shown red against the implementation with `Object.is` replaced by `===`.

During this proposal `evalExpr` on the base gave: A's `min` expression 46.8, 46.8 and 36.8 at lifts 0, 3 and 30; E's `gap` `NaN` at lifts 1 and 2; H's `tilt` `0` at lift 1 and `-0` at lift -1; and a `TypeError` for `(1 + gate.on.x)` at `gate.on = 1` and `NaN` for `(gate.on.x * 0 + 1)` at `gate.on = 0`. A first form of A, `(valvetrain.lift > 20 ? 30.0 : 46.8)`, gave 0 at all three lifts and was dropped. The applier checks them again before relying on them, and replaces one that does not give the stated value with one that does, recording the replacement.

### 6. Existing tests that assert a re-evaluation

Every one still holds as written, because in each the asserted re-evaluation follows a change of value:

- `flexible.test.ts`, "reads a readable spec once, at construction and not per frame": lift 0, 12, 4 moves `height` each time.
- "refills the buffers it already owns when its driver moves": lift 0 to 12, `height` 46.8 to 34.8.
- "animates a `$t` parameter under the time loop": `$t` 0 to 0.5, `height` 46.8 to 40.8.
- "re-evaluates a spring whose expressions a reconcile replaced": `height` 46.8 at mount, 40.8 at `cam.angle = 3`; it would also hold at equal values, because `rebind` forgets.
- "re-evaluates when the driver reached through a binding changes, and not another": lift 0 to 6 moves `height`; the unrelated driver still costs nothing.
- "carries dependence through a chain of two entries": lift 0 to 6.
- "follows the table from one driver to another, though the params text never changed": after the rebind, speed 0 to 6.8 moves `height`; the lift move still costs nothing.
- The mount counts (`evaluations()` is 1 after `mounted()`): a first evaluation always builds.
- `parity-fixture.test.ts`, "evaluates to the producer's geometry at every binding": its four cases have four different heights (46.8, 43.05, 40.8, 34.8), so every case rebuilds the one reused part.
- `color.test.ts`, "keeps an inherited flexible color through geometry evaluation and reconciliation": asserts material and geometry identity, not counts; `powered` 0 to 1 moves `height`, and the reconcile rebinds and so rebuilds.
- `validation-pressure.test.ts` uses flexible parameters only for load-time refusals; `tree.test.ts` has no flexible node. Neither is affected.
- The Python suite's browser tests over `tests/fixtures/lock`, `touched` and `pascaline` (five springs and three blades) see what is drawn, which this change does not alter.

## Every way the memory and the buffers could disagree

The invariant: whenever `built` is defined, the part's position array holds exactly what molejo produces from its spec and `built`, and its bounds were computed from that array.

- **A parameter expression throws part-way.** Step 1 throws before anything is written or forgotten; buffers and `built` keep agreeing (test D).
- **Molejo throws.** `built` is undefined before the call, so whatever the buffers hold afterwards, the next evaluation rebuilds unconditionally (test F). Molejo 0.2.0 in fact writes nothing on the way to failing (Decision 3); the design does not depend on it.
- **The first evaluation.** No buffers and no `built`: it always builds. If it throws, nothing is attached and nothing remembered, as today.
- **`rebind`** (same spec, new expressions or table). Forgets `built`; the next evaluation rebuilds (test G).
- **`reconcile`.** A different spec makes a new `FlexibleShape` with nothing remembered; the same spec rebinds; a removed part is disposed. When `reconcile` is given a candidate scope it calls `update(scope)` with `'all'`, which rebuilds every rebound part, as today.
- **`artifactChanged`.** Replaces meshes whose `model` names the artifact; a flexible node has no model, and its `FlexibleShape` is not touched.
- **A refused pose followed by the standing pose.** A transform refusal happens in `prepareTransforms`, before `updateShapes`, so no part is evaluated (the existing test "does not refill an earlier spring before a later transform refuses"). A refusal inside `updateShapes` (a parameter expression throwing, or molejo refusing a value) leaves every earlier part in the walk whose values moved rebuilt at the refused candidate, as the base leaves it; each such part's `built` holds the candidate's values, which is what its buffers hold, so the next pose that reaches it compares against them and rebuilds if the standing values differ. The refused part itself keeps its standing data with `built` either standing (expression throw) or forgotten (molejo throw). The memory adds no disagreement, and it does not repair the gap below.
- **A part hidden and shown.** Visibility is not an input to `updateShapes`: hidden parts are evaluated exactly as shown ones. A skipped part's attribute version does not move; a part refilled while hidden has a version above the one the renderer last uploaded, and is uploaded when it is next drawn, as today.
- **`dispose`.** Frees the GPU side only (`geometry.dispose()`, the materials); the CPU array and `built` still agree. `removeFlexible` drops the disposed part, and a disposed tree is not updated again; if one were, three.js would upload the CPU array the memory still describes.
- **Colour.** `setColor` replaces the material only.

## A pre-existing gap found while reading

`WidgetTree.update` copies the prepared matrices into the live groups before `updateShapes` runs. A probe on this bench (a temporary test, since deleted) mounted a rigid node translated by `(2 * v.lift)` beside a spring whose `height` is `sqrt(10 - v.lift)`; `update` at lift 12 threw molejo's `values: parameter 'height' must be a finite number, got nan`, and the rigid node's translation stood at 24 afterwards. Under a clocked request the machine keeps its bank, since the pose hook threw, but the scene has moved. `refuse-nonfinite-clocked-pose` placed transform refusal before shape evaluation and declined a shape transaction. This change neither causes nor repairs the gap, and it is outside this change's scope; it is reported for the warts record.

## Risks / Trade-offs

- [A part whose values move by rounding is rebuilt though its data would not change, as the Enigma's right detent-return spring is on a right-wheel step] → Accepted: anything looser than exact equality of inputs can draw what the expressions do not describe. Its cost is one part of 122,928 triangles, against 86 parts and 8.47 million today.
- [The parameters of a reached part are still evaluated] → Accepted with the measurement of Decision 4.
- [One array of numbers is retained per flexible part] → It holds as many numbers as the part has parameters (38,396 over the Enigma's 426 parts), against the position arrays of 28.3 million triangles that are retained already.
- [A later writer of the position array that does not go through `evaluate`] → None exists (`liftAlongNormals` writes decals only); the field's comment states the invariant so one is not added without it.

## Decision record

No decision record is expected. The change narrows when an existing rule fires, inside the one object that owns the buffers; it changes no interface, data flow or ownership. If review judges otherwise, the amendment belongs to ADR-043 (`workflow/adrs/EXPORT/ADR-043-hash-consed-expression-evaluation.md`), whose consequences state that free variables bound re-evaluation for drivers and flexible parts.

## Open Questions

None technical. Whether to record the gap above in `workflow/warts.md` is the reviewer's and the pilot's.
