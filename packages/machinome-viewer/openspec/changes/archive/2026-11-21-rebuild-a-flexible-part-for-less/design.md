## Context

`FlexibleShape` (`src/flexible.ts`) holds a part's molejo spec, its parameter list (`[name, expression]` pairs sorted by name), the buffers molejo allocated at its first evaluation, and `built`, the values its present vertex data was built from (`rebuild-only-changed-flexible-parts`). `WidgetTree.update` and `WidgetTree.admit` (`src/tree.ts`) open one `withExpressions` scope, call `prepareFlatPass(scope)`, prepare or judge the transforms, then walk the tree and call `evaluate(scope)` or `admit(scope)` on every part whose free set the change set touches.

Both entry points begin `this.params.map(([, expression]) => evalExpr(expression, scope))`. `evalExpr` (`src/evaluator.ts`) is `withExpressions(() => { const value = valueOf(prepare(expression), scope); return typeof value === 'number' ? value : Number(value); })`: per parameter, one scope and one lookup of the text in `expressionRoots` (`prepare`, `expressions.ts` 419-431). After a rebuild `evaluate` calls `geometry.computeBoundingBox()` and `geometry.computeBoundingSphere()`.

The opening evidence (`workflow/evidence/enigma-flexible-rebuild-cost-2026-11-21.md`) measured these at 16 to 17 ms and 16 to 19 ms of a 111 ms key-press frame on the Enigma I page, and two prototypes (the `.patch` beside it) at about 10 and about 5 ms, with no difference from the shipped path on that page. It records the prototypes' limits: no empty array, no non-finite position and no signed zero met; resolution counts, reclamation beyond the generation check, and `admit` not examined.

## Goals / Non-Goals

**Goals:**

- Every parameter value a part reads (in value and in type), every refusal it makes (the same error, from the same parameter, before anything is written or forgotten), its vertex data, its bounding box and sphere (ten numbers under `Object.is`), and what three.js reports on the console about them, are what the base produces. First requirement.
- A warm read of a part's parameters makes no text lookup and opens one scope; a rebuild computes the bounds without the attribute's accessors, in two passes over the array. Second requirement.
- Both shown by tests that count work on the base, with no wall clock and no project export.

**Non-Goals:**

- Which parts `updateShapes` visits and how many parameters a frame reads; making parameter formulas roots of the flat pass; molejo and its bundling; `expressions.ts`; the renderer; any project's source.
- Anything that lowers a part's resolution or a flexible part's sampling (deferred by the pilot).
- Viewer API (stays 30) and document versions (stay 1 to 14): verified in `widget/package.json` (`machinomeViewerApi: 30`, `machinomeDocumentVersions: [1, …, 14]`); nothing here touches either.

## Decisions

### 1. One reader of a part's parameters

`FlexibleShape` gains a private field `roots: { generation: number; ids: NodeId[] } | undefined` and a private method `readParameters(scope): number[]`, which both `evaluate` and `admit` call where they call `evalExpr` today:

```ts
private readParameters(scope: EvalScope): number[] {
  return withExpressions(() => {
    const generation = expressionGeneration();
    const held = this.roots;
    const reuse = held !== undefined && held.generation === generation;
    const params = this.params;
    const ids: NodeId[] = reuse ? held.ids : new Array(params.length);
    const values: number[] = new Array(params.length);
    for (let i = 0; i < params.length; i += 1) {
      const id = reuse ? ids[i] : (ids[i] = prepare(params[i][1]));
      values[i] = evalPrepared(id, scope);
    }
    if (!reuse) this.roots = { generation, ids };
    return values;
  });
}
```

`evaluator.ts` gains `evalPrepared(root, scope)`, `const value = valueOf(root, scope); return typeof value === 'number' ? value : Number(value);`, and `evalExpr` becomes `withExpressions(() => evalPrepared(prepare(expression), scope))`. `rebind` sets `roots = undefined` beside `freeVars` and `built`. Nothing in `expressions.ts` changes: `prepare`, `valueOf`, `withExpressions`, `expressionGeneration` and `NodeId` are already exported.

#### The same values and the same refusals (attack point 4)

- **Conversion.** One function, `evalPrepared`, converts for `evalExpr` and for the reader, so the two cannot drift. A value that is not a number goes through `Number` as today: a comparison gives `1` or `0`, an array literal `[x]` gives `x`, a string literal `"7"` gives `7`, an unknown name, a function or an object gives `NaN` (checked on the base during this proposal with `evalExpr`).
- **Value.** For one text, `prepare` returns the same root as long as the generation stands: `expressionRoots` only gains entries between resets (`expressions.ts` 420-428), and only `resetStore()` (575-597) replaces it, raising the generation by one. So within a generation `ids[i] === prepare(params[i][1])`, and the reader makes exactly `evalExpr`'s call, `valueOf(prepare(text), scope)`, minus the lookup.
- **Order of refusals.** The base's sequence per parameter, in name order, is: the text's lookup (a parse or a refused form can throw, `Cannot evaluate a "Func" expression: …` or the parser's own error, only when the text is not in the store), its evaluation (`valueOf` can throw: a member read on a number, a call of something that is not a function), its conversion. The reader performs the same three steps in the same order for each parameter, a lookup included whenever the store's entry may be missing (the first read, after a rebind, after a reclamation). So when two parameters would throw, the first in name order throws, with the same error. Nothing is written before: `evaluate` and `admit` still compare and build only after the whole array is read, and the reader commits `roots` only after its loop, so a throw leaves `roots` as it stood.
- **Where the prototype differed.** It prepared every text first and evaluated after, so a parameter whose text fails to parse, sorted after one whose evaluation throws, would surface the parse error where the base surfaces the evaluation error. Through the tree that case is not reachable: `free` (`freeVariables` over every text) is read by `touchedBy` before `evaluate`, and validation refuses such a text at load. The design does not rely on that; test P3 calls the part directly.

#### What is kept and how long (attack point 5)

What a generation is: `storeGeneration`, raised by exactly one in `resetStore()` and by nothing else (567-597). Every call of `resetStore()` is guarded so it never runs inside an open scope: at the start of an outermost `withExpressions` under the suite's `everyOperation` switch (499-500), at the start of an outermost `withDocumentLoad` (526), in `requestReclamation` with no scope open (468-474), in `releaseExpressions` with no scope open (614-616), and at the end of the outermost scope in `scoped` (481-488). The three reclamation points of `keep-a-live-model-parsed` (a load's start, a refused load's end, a document's settlement, and every disposal, ADR-043's reclamation-point amendment) all reach `resetStore()` through those paths.

- **Can the store be emptied without the generation changing?** No: the only assignments to `nodes`, `table` and `expressionRoots` after module load are in `resetStore()`, which raises the generation.
- **Can it be emptied inside the scope that reads?** No: the reader reads the generation and every id inside its own `withExpressions`, and a reset never runs while a scope is open. A reset at the start of that scope (under `everyOperation`) happens before the generation is read. This is a departure from the prototype, which read the generation outside any scope and prepared and read in two separate scopes; at depth 0 under `everyOperation` the second scope's start could reset the store between them (test L4).
- **A `rebind`** to new expressions or a new table drops `roots`. A root depends only on the text, not on the table (a binding name is a name node resolved through `scope.bindings` at evaluation, ADR-044), so keeping it across a new table would be correct; it is dropped anyway because the texts may have changed, and one rule is simpler than two.
- **Two documents on one page, operated alternately.** The store and its generation are page-wide; each part keeps the roots of its own texts. A reset caused by either document moves the generation for both, and each part prepares again on its next read. Operating either document reclaims nothing (`keep-a-live-model-parsed`).
- **A republish.** `reconcile` builds a new `FlexibleShape` (new spec, nothing kept) or calls `rebind` (roots dropped); the load's `withDocumentLoad` may reset the store, which moves the generation.
- **Disposal.** `dispose` frees the GPU side; a disposed part is dropped by `removeFlexible` and never read again. If one were, the generation check would still apply. The ids are numbers and keep nothing of the store alive.
- **`EXPRESSION_LIMITS`.** Unchanged, and the reader adds no expression state: a lookup of a text already in the store interns nothing, and after a reset the reader prepares exactly the texts the base prepares at the same moment. The rule the reclamation-point amendment rests on ("after load, no operation prepares expression text the loaded document does not already hold") holds as before.
- **The first read after a reclamation.** It makes the calls the base makes on every read: one `prepare` per parameter, a lookup where the text is in the store and a parse and interning where it is not, which the base would also pay on that read. On the Enigma page that is 36,415 calls over the 86 parts a press reaches, once, in the first pose after the reclamation that reaches each part; every later read makes none. Reclamations there happen at a load, a settlement or a disposal (the amendment measured the generation standing at 0 across the mount and nine instructions), so the time lands in the load's own first pose. Not measured; it rests on the base's reading figure (16 to 17 ms a frame for all of it, lookups and evaluation together) as an upper bound for the lookups.

#### One scope for a part, and counted work (attack point 6)

A `withExpressions` scope means one thing: the store is not reset while it is open (`scoped`, 476-490). It plays no part in memoisation: `valueOf` decides a pass by the scope's value (`ensurePass`, 848-858) and reuses a node's value by its stamp (917), and `resolutions` rises only when `valueOf` computes a node (927). Inside `WidgetTree.update` and `admit` every read already sits inside the tree's own scope, so the base's per-parameter scopes are nested and change nothing; one scope per part changes nothing either. Outside the tree, a direct call at depth 0 differs only under the suite's `everyOperation` switch with the store at its threshold, where the base resets before every parameter and the reader once, at its start; values are the same either way, and no committed test does that to a part (listed under Decision 4).

The flat pass: the reader calls `valueOf(id, scope)` with the id `prepare` would return, at the same point in the walk, after the same `prepareFlatPass(scope)`. `valueOf`'s served branch depends only on the id, the pass (`servedPass === passCounter`) and the served slot index (918-923). A parameter whose root the program covers (a parameter that is a bare binding name, whose name node shares its root's slot) is served exactly as `evalExpr`'s read is; any other is walked as today. A document the flat pass does not serve (no table, a table under `FLAT_PASS.minimumBindings`, a declined scope) has `servedPass !== passCounter`, and every read is the walk, as today. So the sequence of `valueOf` calls, and with it every memo stamp, `resolutions` and every `flatPassMetrics()` counter, is the base's.

#### `admit` and `evaluate` (attack point 7)

Both call `readParameters`; neither keeps its own path to `evalExpr`. The skip test that follows (`buffers`, `built`, same length, `Object.is` at every position) is also moved into one private predicate both call, so the two decide "these are the values the buffers were built from" by one piece of code. `admit` may set `roots`; that is a cache of the store keyed by text and generation, holds no value, and changes nothing a later `evaluate` computes. Draw-a-press design D1's list of what `admit` leaves alone (buffers, `built`, `needsUpdate`, bounds) stands.

#### The values object (attack point 8)

Left out. The object handed to molejo is built fresh for each rebuild, as today. The evidence measures building it at 0.7 ms a frame as shipped and 0.6 with it kept, and nothing found here adds a reason. (Molejo reads `values` only during `evaluate`, through `resolve`, and keeps no reference: no module state, `evaluate.js` 976-1073.) The comparison with `built` and the construction of the object stay as shipped (0.3 and 0.7 ms measured); the prototype's loop rewrites of both are not taken.

### 2. The bounds in two passes, number for number

#### What three.js 0.156.1 does (attack point 1)

`BufferGeometry.computeBoundingBox` (`node_modules/three/src/core/BufferGeometry.js` 290-358): allocate `new Box3()` if `boundingBox` is null; if the position attribute `isGLBufferAttribute`, log and set an infinite box; if there is a position attribute, `boundingBox.setFromBufferAttribute(position)` and then expand by each morph target if `morphAttributes.position` is truthy; else `makeEmpty()`; then, if `isNaN` of any of `min.x`, `min.y`, `min.z`, `console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. …', this)`.

`Box3.setFromBufferAttribute` (`math/Box3.js` 37-49): `makeEmpty()` (99-106: min components `+Infinity`, max `-Infinity`), then for `i` from 0 while `i < attribute.count`: `_vector.fromBufferAttribute(attribute, i)` (`Vector3.js` 676-684: `x = getX(i)`, `y = getY(i)`, `z = getZ(i)`) and `expandByPoint(_vector)` (128-135: `min.min(v)`, then `max.max(v)`; `Vector3.min` 318-326 is `x = Math.min(x, v.x)` for x, y, z, `max` 328-336 likewise with `Math.max`). `BufferAttribute.getX` (`core/BufferAttribute.js` 198-206) is `this.array[index * this.itemSize]`, denormalized when `normalized`; `denormalize` of a `Float32Array` value is the value (`math/MathUtils.js` 234). `count` is `array.length / itemSize`, set at construction (26).

`computeBoundingSphere` (360-468): allocate `new Sphere()` if null; GL attribute as above; if there is a position attribute: `_box.setFromBufferAttribute(position)` (the same pass into a module box), morph targets, `_box.getCenter(center)` (`Box3.js` 116-120: `isEmpty()` (108-114: `max.x < min.x || max.y < min.y || max.z < min.z`) ? `center.set(0, 0, 0)` : `center.addVectors(min, max).multiplyScalar(0.5)`, i.e. `(min.x + max.x) * 0.5`, `Vector3.js` 126-134 and 186-194); `maxRadiusSq = 0`; for each `i < position.count`: `maxRadiusSq = Math.max(maxRadiusSq, center.distanceToSquared(_vector))` with `distanceToSquared` (544-550) `dx = this.x - v.x` (and y, z), `dx * dx + dy * dy + dz * dz`; morph targets; `radius = Math.sqrt(maxRadiusSq)`; if `isNaN(radius)`, `console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. …', this)`. With no position attribute it leaves the sphere as it is.

#### What the new function does

`computeFlexibleBounds(geometry)`, exported from `flexible.ts`:

1. **Guard.** If the geometry has no position attribute, or `morphAttributes.position` is truthy, or the attribute's `getX`, `getY` or `getZ` is not `THREE.BufferAttribute.prototype`'s own, or its `itemSize` is not 3, or its `array` is not a `Float32Array`: call `geometry.computeBoundingBox()` then `geometry.computeBoundingSphere()` and return.
2. **The box.** `minX = minY = minZ = +Infinity`, `maxX = maxY = maxZ = -Infinity`; for `i` from 0 while `i < attribute.count`: `x = array[i * 3]`, `y = array[i * 3 + 1]`, `z = array[i * 3 + 2]`; `minX = Math.min(minX, x)` (y, z), then `maxX = Math.max(maxX, x)` (y, z). Allocate `new THREE.Box3()` only if `boundingBox` is null; set `min` and `max` from the six numbers.
3. **The sphere.** Allocate `new THREE.Sphere()` only if `boundingSphere` is null. `empty = maxX < minX || maxY < minY || maxZ < minZ`; centre `(0, 0, 0)` when empty, else `cx = (minX + maxX) * 0.5` (y, z). `most = 0`; for each `i < count`: `dx = cx - array[i * 3]` (y, z), `most = Math.max(most, dx * dx + dy * dy + dz * dz)`. Set the centre and `radius = Math.sqrt(most)`.
4. **The report.** If `Number.isNaN` of `minX`, `minY`, `minZ` or the radius: call `geometry.computeBoundingBox()` then `geometry.computeBoundingSphere()`.

Why the numbers are the same: with the guard passed, `getX(i)` is `array[i * 3]` exactly (plain accessor, item size 3, a `Float32Array` whose denormalization is the identity, so `normalized` needs no check), and there are no morph targets; the reads, the `Math.min` and `Math.max` calls, the centre's sum and product and the distance's three differences and left-to-right sum are the operations three.js performs, on the same doubles, in the same order. The sphere's own box pass is left out because it computes, from the same array with nothing written in between, the same six numbers the first pass did: `Math.min` and `Math.max` are pure. Step 4 recomputes with three.js's own functions exactly when one of three.js's two conditions holds (the box's `min` or the radius is `NaN`, the same numbers), so the console receives the same calls, in the same order, with the message three.js writes and the geometry as argument; the numbers they write are the ones already there. The report is kept because it is what the base does, and test B1 holds it; it is not written into the requirement, which speaks of the numbers.

The cases, one by one, each in test B1:

- **Empty position array** (`count` 0): box `+Infinity`/`-Infinity`, `isEmpty`, centre `(0, 0, 0)`, radius `Math.sqrt(0) = 0`; no `NaN`, no report. Molejo 0.2.0 cannot produce it (a path has at least one primitive and the tessellation counts are positive integers, `spec.js` 189-195, 318, 451-457, so an open path has at least two rings plus two cap centres), and the function does not depend on that.
- **One vertex:** `min = max = v`, centre `(v + v) * 0.5`, radius 0.
- **A zero of either sign:** `Math.min(+Infinity, -0)` is `-0`, `Math.min(-0, 0)` and `Math.min(0, -0)` are `-0`, `Math.max(-0, 0)` is `0`; the centre `(-0 + -0) * 0.5` is `-0`, `(-0 + 0) * 0.5` is `0`. The same calls give the same signs; test B1 covers each axis with `-0` alone, `0` alone and both in both orders.
- **`NaN`:** `Math.min` and `Math.max` propagate it, so the box's `min` and `max` on that axis are `NaN`, `isEmpty` is false (every comparison with `NaN` is false), the centre and the radius are `NaN`; step 4 runs and three.js logs both messages, as on the base.
- **Infinite positions:** a `+Infinity` alone on an axis gives a centre of `+Infinity` there and `dx = Infinity - Infinity = NaN`, so the radius is `NaN` and three.js logs the sphere's message only; both infinities on one axis give a `NaN` centre and the same. Step 4 reproduces it. These are reachable from finite bindings: molejo refuses a non-finite *parameter* (`resolve`, `evaluate.js` 86-92) but checks nothing it writes, and a double beyond the single-precision range is stored as an infinity. Checked during this proposal: the test spring with `height` 1e39 writes 129 infinite coordinates of 606, with 1e308 193; no `NaN` was produced there, and none is ruled out (`Infinity * 0` in `centre + u * x` is one route).

Checked during this proposal with a scratch test since deleted: the function against three.js's own on those cases, on 200 seeded random arrays of 1 to 50 vertices, and on 40 molejo outputs of the committed fixtures' parts (`pascaline` and `lock`): the ten numbers equal under `Object.is` everywhere, and the console calls equal on the edge cases.

#### Who reads the bounds (attack point 2)

Every reader in the widget and in three.js 0.156.1 that can reach a flexible mesh copies the numbers and keeps no reference to the objects:

- the renderer's culling, `Frustum.intersectsObject` (`math/Frustum.js` 79-95): computes the sphere if null, then `_sphere.copy(geometry.boundingSphere).applyMatrix4(…)`;
- the renderer's sort, `WebGLRenderer.projectObject` (1237-1246): computes the sphere if null, then `_vector3.copy(geometry.boundingSphere.center)`;
- picking and hover, `raycaster.intersectObject(scene, true)` (`viewer.ts` 810) into `Mesh.raycast` (`objects/Mesh.js` 160-186): sphere computed if null and copied, box tested by `_ray.intersectsBox` if non-null;
- the camera's framing, `visibleBounds` (`viewer.ts` 2897-2915): box computed if null, then `clone().applyMatrix4(…)`;
- a part's place on screen (track and highlight), `worldBounds` (`screen.ts` 77-91): the same.

None depends on the objects' identity, and the function keeps it anyway: like three.js it allocates only when the field is null and writes in place. After any evaluation that rebuilds, both fields are non-null, as today. Nobody recomputes a flexible geometry's bounds: the readers compute only when a field is null, which after the first evaluation it never is; the only code that sets them null is `liftAlongNormals` (`tree.ts` 99-118), on decal geometry. Before a part's first evaluation a reader may have had three.js allocate an empty box or a sphere of radius -1 on the attribute-less geometry; the first evaluation then writes into those objects, as three.js's functions would.

#### A second implementation beside three.js's (attack point 3)

The rigid parts keep three.js's functions; only `FlexibleShape` calls this one. What keeps the two from drifting:

- **The guard.** The fast path runs only on what it was proved for: a plain accessor, item size 3, a `Float32Array`, no morph targets. Anything else (an interleaved attribute or a `GLBufferAttribute`, whose accessors are not `BufferAttribute`'s or are absent, a `Float16BufferAttribute`, a morph target) goes to three.js's functions, and test B3 shows the numbers and reports equal for each. A flexible geometry has none of those by construction: the geometry is private to `FlexibleShape`, its only writer of attributes is `evaluate`, which sets one `new THREE.BufferAttribute(buffers.positions, 3)` on the first evaluation, molejo allocates `positions` as a `Float32Array` and checks its type and length on every reuse (`checkBuffer`, `evaluate.js` 962-971), and nothing in the widget sets `morphAttributes`. The guard makes that checked at every rebuild for six comparisons, instead of assumed.
- **The oracle on every run.** The bounds parity tests (B1 to B3) run three.js's own functions beside the new one on the same arrays in every suite run, with the installed three.js, whatever its revision. A three.js whose bounding computation or report changes on any of those arrays turns them red, naming the array and the ten numbers on each side. On the day of an upgrade the maintainer sees those tests red when a number or a report moved, and nothing when none did. A test pinning `THREE.REVISION` was considered and left out: it would fail at every upgrade, also when nothing moved, and the oracle tests compare behaviour where a pin compares a version string.

### 3. Tests

A new `src/flexible-rebuild.test.ts`. It wraps molejo's `evaluate` in a pass-through spy as `flexible.test.ts` does, and wraps `prepare` and `withExpressions` of `./expressions` in pass-through spies (`vi.mock` with `importOriginal`, as `tree.test.ts` does for `./evaluator`). Calls from inside `expressions.ts` are not seen; calls from `evaluator.ts`, `flexible.ts`, `tree.ts` and `bindings.ts` are. Hand-written specs and committed fixtures only. Every test that forces a reclamation asserts the generation rose (ADR-043's reclamation-point amendment).

**Red on the base, by count (attack point 9):**

- **R1. A warm read looks nothing up.** A `FlexibleShape` with five parameters (`height` read by the spec, four unreferenced), evaluated at lift 0, then at lift 1: during the second, `prepare` calls 0 and `withExpressions` calls 1. Base (measured during this proposal): 5 and 5.
- **R2. A warm judgement looks nothing up.** The same part after one `evaluate`, `admit` at lift 2: 0 and 1. Base: 5 and 5.
- **R3. Through the tree.** A `WidgetTree` with that part and no operations, mounted, then `update` and `admit` each reaching the part with a moved input: `prepare` calls 0 for each. Base: 5 each.
- **R4. A rebuild does not use the accessors.** Spies on `THREE.BufferAttribute.prototype`'s `getX`, `getY`, `getZ`, restored after the test, counting the calls whose receiver is the part's position attribute; a rebuild: 0 calls each, and the ten numbers equal three.js's for the new array (computed on a copy of the attribute, outside the counted span). The spies sit on the prototype because one installed on the attribute itself would fail the guard and send the rebuild to three.js's functions. Base (measured): 606 calls of `getX` for 202 vertices, three per vertex.

What they prove: a warm read makes no text lookup and opens one scope, a judgement the same, and the bounds no longer go through the accessors. What they cannot: that any value is right (P, L, B do that), how many passes over the array the bounds make, or any time.

**Parameters against `evalExpr` (attack points 4, 5, 7):**

- **P1. Values.** Parts whose unreferenced parameters are a comparison, an array literal, a string literal, an unknown name, a name whose value is an object (the driver map `v`; the grammar has no object literal), `(0 * v.lift)` at a negative lift (`-0`), `((v.lift / 0) * 0)` (`NaN`), a `$t` expression, a binding name and an expression over one (with a table); several scopes, each moving the lift so the part rebuilds. The `values` object molejo receives equals, name by name under `Object.is`, `evalExpr` of each text in the same scope.
- **P2. One refusal.** A part whose second parameter in name order throws (a member read on a number): `evaluate` and `admit` throw an error of the same constructor and message as `evalExpr` of that text; no molejo call, attribute version and positions unchanged, and a following read at the standing values makes no molejo call.
- **P3. The first of two refusals.** Parameters `a` (throws at evaluation, a member read on a number) and `b` (a text the store refuses to prepare, `(x = 3)`): the error is `a`'s. With the names swapped (`a` the unpreparable text): `a`'s parse error. Each compared with the first throw of `params.map(evalExpr)` in name order, by constructor and message. Called on `FlexibleShape` directly, since through the tree `free` refuses the text first.
- **P4. A parameter the flat pass serves.** A table served by the flat pass (`FLAT_PASS.minimumBindings` lowered in the test, as `flat-pass.test.ts` does), a part whose parameter is a bare binding name and another over it, posed through the tree at three scopes: the values equal `evalExpr`'s, and `expressionMetrics().resolutions` and `flatPassMetrics().entries` after each pose equal the figures the same test prints on the base, which the applier records there first (task 2.2) and writes into the test as constants.

**Lifetime (attack point 5):**

- **L1. A reclamation between two reads.** A part with `p: '(2 * v.lift)'` and `q: '(3 + v.lift)'` read once; the store reclaimed (`retainExpressions(); releaseExpressions();`, generation risen); the two texts prepared in reverse order by `evalExpr`, so their roots trade ids (checked during this proposal: ids 2 and 4 become each other's, and the old ids read 8 and 10 where the texts give 10 and 8); the part read again: values equal `evalExpr`'s, 2 `prepare` calls. **L1b:** the read after that one makes 0 `prepare` calls; kept apart because the base prepares on every read, so L1 passes on the base and L1b is red there.
- **L2. A rebind.** A reconcile to the same spec with new texts, then a read: the new texts' values, one `prepare` per parameter.
- **L3. Two documents.** Two trees, two tables binding `_b0` to different expressions, parts over `_b0`, posed alternately with a reclamation between two poses: each gives its own table's values.
- **L4. Pressure at depth 0.** `EXPRESSION_LIMITS.nodes = 1`, `everyOperation = true`, the part read directly three times at moved inputs: the values equal `evalExpr`'s, the generation rose at each read. **L4b** (added in review): the part read once, then the pressure switched on, then read again, so the roots are of the present generation when the read begins and the scope's own start empties the store; it holds the generation's being read inside the scope when there is one scope, which L4 alone does not.
- **L5. A judgement after a reclamation.** `admit` after a reclamation refuses, and accepts, exactly what `evaluate` does at the same scopes.

**Bounds against three.js (attack points 1 to 3):**

- **B1. Edge arrays.** For each array: one geometry bounded by three.js's two functions, one by `computeFlexibleBounds`; the ten numbers under `Object.is`; `console.error` spied, the two sequences of calls equal in count and first argument, and each second argument the respective geometry. Arrays: empty; one vertex; per axis `-0` alone, `0` alone, both in each order; `NaN` in each coordinate; `+Infinity`, `-Infinity`, both on one axis; values near the single-precision limit; 200 seeded random arrays of 1 to 50 vertices. Also: pre-existing `Box3` and `Sphere` are the same objects afterwards; fresh ones are allocated when null.
- **B2. Arrays molejo produces.** The parity fixture's spring at every case; every flexible part of the committed `lock`, `touched` and `pascaline` fixtures at several parameter values; hand-written specs of each path primitive molejo 0.2.0 evaluates (`line`, `arc`, `helix`, `spline`, `wrap`) and of both profiles; the test spring at `height` 1e39 (infinite positions). Same comparison as B1.
- **B3. The guard.** Geometries on which the fast path must not run: a morph position attribute (relative and absolute), an `InterleavedBufferAttribute`, a `Float16BufferAttribute`, an item size of 4, a `GLBufferAttribute`, no position attribute, an attribute carrying an accessor of its own, a normalized `Int16Array` (added in review: the one case only the guard's array test turns away, since a `Float16BufferAttribute` already has accessors of its own); and one on which it runs, a `normalized` `Float32Array`. Same comparison.

What P, L and B cannot see: an input, an array or an expression form outside their sets, and the Enigma's own document (a project's, not committable here).

### 4. Existing tests

Each `flexible.test.ts` test that watches the bounds spies `geometry.computeBoundingBox` and `computeBoundingSphere`. After this change a rebuild calls neither, so:

- **E1.** "rebuilds that part when a value then moves" asserts each is called once. It cannot hold as written. Its two assertions are replaced by: a sentinel written into `boundingBox.min.x` and `boundingSphere.radius` before the update is gone after it, and the ten numbers equal three.js's for the new array. Everything else in it stands.
- **E2 to E5.** "keeps a part whose values a changed name left as they were", "rebuilds nothing on an update of everything at unchanged values", "judges a moving candidate without showing it" and "refuses with molejo's own message and leaves every part standing" assert both are not called. They would still pass, and no longer prove that no bounds pass ran. Each keeps its assertions and gains the sentinel check: the sentinels stand after the kept update or the judgement.

Every other test holds as written, by the reasons of Decision 1:

- `flexible.test.ts`, every other test: they count molejo calls, attribute versions and positions, which do not change.
- `parity-fixture.test.ts`: binds the fixture's parameters with `evalExpr` (unchanged) and evaluates one reused `FlexibleShape` directly at depth 0 without `everyOperation`; its box is compared within the fixture's tolerance and is the same box.
- `flat-pass-parity.test.ts`: poses the committed documents through `WidgetTree.update`, the `lock`, `touched` and `pascaline` parts included, and counts mismatches, serving and refusals; the reads make the base's `valueOf` calls, so none of those moves.
- `color.test.ts`, "keeps an inherited flexible color through geometry evaluation and reconciliation": material and geometry identity.
- `tree.test.ts` counts `evalExpr` calls through its mock; it has no flexible node, so the reader's calls are not among them.
- `document.test.ts` and `validation-pressure.test.ts` reach flexible parameters only through validation (`freeVariables`, `assertRenderable`), which does not change.
- `expressions.test.ts`, `expression-reuse.test.ts`, `expression-lifetime.test.ts` and `flat-pass.test.ts` (the only files that assert `resolutions` or set `everyOperation`) have no flexible part.
- The Python suite's browser tests over `lock`, `touched` and `pascaline` see what is drawn, which does not change.

### 5. Mutations

Each applied to the implementation, its test run, the output kept, the implementation restored: M1 the generation check removed (roots reused whenever held): L1 red, with the traded values. M2 `rebind` keeps `roots`: L2 red. M3 every text prepared before any is evaluated (the prototype's order): P3 red. M4 the reader split into a preparing scope and a reading scope, the generation read outside both (the prototype's shape): L4 red. M5 `admit` on `evalExpr` (the prototype): R2 red. M6 the morph check removed from the guard: B3 red. M7 step 4 removed: B1 red on the console calls. M8 `Math.min(minX, x)` written `x < minX ? x : minX` (and the same for `max`): B1 red on `NaN` and on `-0`.

## What the Enigma should show (predictions)

Predictions, resting on the prototypes' figures, which the reviewer's measurement decides:

- Reading the parameters near the prototype's 10.3 and 9.6 ms a frame (shipped 16.3 and 17.3), since a warm read makes the prototype's calls per parameter plus one branch and one function call.
- The bounds near the prototype's 4.7 and 5.4 ms (shipped 15.6 and 18.6), the guard being six comparisons a rebuild.
- With npm molejo, the frame lower by about the sum, 15 to 20 ms; the evidence measured the two prototypes together only beside molejo's own new evaluator, where they accounted for 16 to 20 ms. Not measured alone; the earlier predictions of this campaign that scaled one figure were wrong three times.
- No difference in either self-check (bounds of every rebuild against three.js's own, parameter values against `evalExpr`'s).

## Departures from the prototypes

- The reader prepares each text just before evaluating it when it prepares at all, in one scope with the generation read inside it, and commits the roots after the loop (the prototype prepared all first, in a scope apart from the reading one, with the generation read outside): Decision 1, P3, L4.
- `admit` shares the reader and the skip predicate (the prototype left it on `evalExpr`).
- The conversion is shared with `evalExpr` through `evalPrepared` (the prototype copied it).
- The values object is not kept, and the comparison and the object's construction stay as shipped.
- The bounds read the geometry's position attribute and its `count` rather than molejo's returned array, so they read what three.js reads; a guard sends anything not proved to three.js's functions; a `NaN` bound is reported through three.js's own functions (the prototype logged nothing).

## Alternatives rejected

- **Keep three.js's functions and make only one of them cheaper** (three.js's box, then a sphere pass of our own): the second implementation is still there, for less of the gain.
- **Copy three.js's two console messages** instead of calling its functions on a `NaN`: two strings to keep in step by hand; calling three.js costs only on that case and needs nothing kept.
- **Prove non-finite positions unreachable and drop the report:** they are reachable from finite bindings (Decision 2).
- **Skip the guard and rely on construction:** six comparisons a rebuild against a silent divergence if a later writer adds a morph target or replaces the attribute.
- **Read the parameters through a root list prepared by `free`** (which prepares every text once anyway): it would tie the dependency set's cache to the store's generation and to `rebind` in a second place.
- **A source-only counter in `flexible.ts`** for text lookups and bounds passes: it would not exist on the base, so a test on it is red for a missing export and not for the work; the pass-through spies count what the base does.
- **Keep roots across a `rebind`:** correct for an unchanged text, but a second rule for a saving made once per republish.

## Risks / Trade-offs

- [A second implementation of three.js's bounds in the package] → Confined by the guard and compared with the installed three.js's own on every suite run.
- [One array of ids per part is retained across operations] → As many numbers as the part has parameters (38,396 over the Enigma's 426 parts), beside the `built` arrays of the same size already retained; it keeps nothing of the store alive.
- [The first read after a reclamation prepares every reached part's texts] → What the base pays on every read; once per reclamation.
- [A deeply nested parameter expression that exhausts the stack] → The reader calls `valueOf` a few frames shallower than `evalExpr` did, so an expression at the edge of the engine's stack could now evaluate where it overflowed. Stack exhaustion is the engine's limit, not a refusal the viewer specifies; no committed document is near it.
- [Admitted time] → None claimed beyond the reviewer's measurement.

## Decision record

An amendment to ADR-043 (`workflow/adrs/EXPORT/ADR-043-hash-consed-expression-evaluation.md`), written after the reviewer's measurement and only if it confirms the design. Its lifetime amendment of 22 September 2026 says raw node ids are operation-local and names the holders that keep source and generation (kink descriptors, `ExpressionPath`); the binding table (D4) was already one. A flexible part becomes another holder of ids across operations, rebuilt by generation, and the record should say so, so that a later change to reclamation sees every holder.

The bounds take no decision record. They are local to `flexible.ts`, change no interface, data flow or ownership, and the guard and the parity tests carry what a maintainer needs to know. The ADR that owns flexible parts is the framework's ADR-057 (`packages/machinome/docs/adrs/NODE/ADR-057-the-flexible-leaf-and-spec-carried-geometry.md`, the one `flexible.ts` names; the viewer's own ADR-057 is another record). Its viewer section, "The widget evaluates shape the way it already evaluates pose", says each node "parses its `params` once through the existing evaluator cache, evaluates them in the existing scope … and hands the values to molejo", which stays true, and says nothing about bounds. ADR-044 stands as is: a binding name resolves through the scope at evaluation, which is what makes a root independent of the table.

## Open Questions

None.
