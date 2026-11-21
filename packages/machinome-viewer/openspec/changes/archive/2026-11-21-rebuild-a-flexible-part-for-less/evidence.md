# Evidence: rebuild-a-flexible-part-for-less

Written by the applying agent on 21 November 2026, in the worktree
`machinome/WTs/rebuild-a-flexible-part-for-less`, branch
`rebuild-a-flexible-part-for-less`, above the planning commit `2417f267`
(base `cb0a5958477aee2bf12049ad40a9d0b94419f17c`). Tasks 1.2 to 8.1 except
7.2; nothing committed. The reviewer's measurement on the Enigma page (7.2)
and the decision record (8.2) are not here.

Every run below was made from
`packages/machinome-viewer/machinome/viewer/web/widget/` with the bench's
own `node_modules/.bin/vitest` (3.2.7), one run at a time.

## 1.2 The bench

`git status --short` was empty, `HEAD` was
`2417f2673fe40c63ff0e8183363f6352b793a368` with parent
`cb0a5958477aee2bf12049ad40a9d0b94419f17c`, the branch was
`rebuild-a-flexible-part-for-less`, and
`openspec validate rebuild-a-flexible-part-for-less --strict` printed
`Change 'rebuild-a-flexible-part-for-less' is valid`.

## 2.1 The inputs, checked on the base

Checked with `evalExpr` and the store's own functions on the unmodified
source, in a scratch test since deleted:

| Text | Raw value | `evalExpr` |
|---|---|---|
| `(v.lift > 1)` at lift -1 / 2 | `false` / `true` | `0` / `1` |
| `[v.lift]` at -1 / 2 | array | `-1` / `2` |
| `[1, 2]` | array | `NaN` |
| `"7"` | string `7` | `7` |
| `nobody` | `undefined` | `NaN` |
| `v` (the driver group) | object | `NaN` |
| `sin` | function | `NaN` |
| `(0 * v.lift)` at -1 / 2 | | `-0` / `0` |
| `((v.lift / 0) * 0)` | | `NaN` |
| `(2 * $t)` at `$t` 0.25 | | `0.5` |
| `{}` | throws at `prepare`: `TypeError: Cannot read properties of null (reading 'type')` | |
| `(1 + gate.on.x)` at `gate.on` 1 | throws at evaluation: `TypeError: Cannot use 'in' operator to search for 'x' in 1` | |
| `(x = 3)` | throws at `prepare`: `Error: Expected ) at index 3, found =` | |

- **Replaced: "an object literal" (P1).** The grammar has no object
  literal: `{}` is refused at `prepare` with a `TypeError`, so it cannot
  stand in a test of values. P1 uses `v`, the nested driver map, whose value
  is an object and converts to `NaN` as the design says an object does.
  `[1, 2]` (an array of two, `NaN`) is added beside `[v.lift]`.
- The design's `v.lift` is used literally: the tests' scopes carry
  `drivers: { v: { lift }, gate: { on } }`.
- **L1's trade of ids holds as stated.** In a fresh store `(2 * v.lift)`
  and `(3 + v.lift)` prepare to roots 2 and 4; after a reclamation (the
  generation rose from 1 to 2) and preparation in the other order, to 4
  and 2. At lift 5 the old ids read 8 and 10 where the texts give 10 and 8.
- **R4's figure holds.** A spring of 24 path segments and an 8-sided
  profile (202 vertices, the design's "test spring") makes 606 calls of
  `getX` in `computeBoundingBox` plus `computeBoundingSphere`, three per
  vertex. At `height` 1e39 it writes 129 infinite coordinates of 606, at
  1e308 193, and no `NaN` in either.
- P3's two texts refuse as stated: `(x = 3)` at its preparation, and a
  member read on a number at its evaluation.

## 2.2 Red on the base

The final `src/flexible-rebuild.test.ts` run against the base source. The
working tree was never restored: `src/` was copied to a scratch directory
inside the widget, the copy's `flexible.ts` and `evaluator.ts` replaced by
`git show HEAD:` (identical to `cb0a5958` for `src/`, checked with
`git diff --quiet cb0a5958 HEAD -- …/src`), and the copy's fixture path
lengthened by one `../` for the deeper directory; the copy was then deleted.
The same file was first run against the base in place, before any source
change; that earlier run gave the same counts (R1, R2: 5 and 5; R3: 5 and 5;
R4: 606 each). The file was later changed only in L1 (below) and in B2's
wrap specification.

```
P4 figures: [{"resolutions":3,"entries":2},{"resolutions":6,"entries":4},{"resolutions":9,"entries":6}]

 ❯ .scratch/basesrc/flexible-rebuild.test.ts (17 tests | 8 failed) 64ms
   × … > R1. a warm read looks nothing up 21ms
     → expected { prepare: 5, withExpressions: 5 } to deeply equal { prepare: +0, withExpressions: 1 }
   × … > R2. a warm judgement looks nothing up 4ms
     → expected { prepare: 5, withExpressions: 5 } to deeply equal { prepare: +0, withExpressions: 1 }
   × … > R3. through the tree, shown and judged 3ms
     → expected { …(2) } to deeply equal { …(2) }
   × … > R4. a rebuild does not read the vertices through the accessors 3ms
     → expected { getX: 606, getY: 606, getZ: 606 } to deeply equal { getX: +0, getY: +0, getZ: +0 }
   ✓ … > P1. values, in value and in type, shown and judged 5ms
   ✓ … > P2. one refusal, before anything is written 2ms
   ✓ … > P3. the first of two refusals, in the order of the names 2ms
   ✓ … > P4. a parameter the flat pass serves 5ms
   ✓ … > L1. a reclamation between two reads 2ms
   × … > L1b. the read after the one that prepared again prepares nothing 1ms
     → expected 2 to be +0 // Object.is equality
   ✓ … > L2. a rebind 1ms
   ✓ … > L3. two documents, posed alternately across a reclamation 2ms
   ✓ … > L4. pressure at depth 0 1ms
   ✓ … > L5. a judgement after a reclamation refuses what an evaluation refuses 2ms
   × … > B1. edge arrays 2ms
     → computeFlexibleBounds is not a function
   × … > B2. arrays molejo produces 6ms
     → computeFlexibleBounds is not a function
   × … > B3. the guard sends what it was not proved for to three.js 1ms
     → computeFlexibleBounds is not a function

 FAIL … > R3. through the tree, shown and judged
AssertionError: expected { …(2) } to deeply equal { …(2) }
  {
    "judged": {
      "molejo": 1,
-     "prepare": 0,
+     "prepare": 5,
    },
    "shown": {
      "molejo": 1,
-     "prepare": 0,
+     "prepare": 5,
    },
  }

      Tests  8 failed | 9 passed (17)
```

The counts, base and implementation:

| Test | Base | Implementation |
|---|---|---|
| R1, `evaluate` warm | 5 `prepare`, 5 `withExpressions` | 0, 1 |
| R2, `admit` warm | 5, 5 | 0, 1 |
| R3, `update` / `admit` through the tree | 5 / 5 `prepare` (molejo 1 / 1) | 0 / 0 (molejo 1 / 1) |
| R4, accessor calls on the part's attribute | `getX` 606, `getY` 606, `getZ` 606 | 0, 0, 0 |
| L1b, the read after the re-preparing one | 2 `prepare` | 0 |

Every red is on its count. The B tests fail on the base at the missing name
only, as expected; P1 to P4 and L1 to L5 pass there.

**P4's constants**, printed on the base and written into the test as
`P4_FIGURES`: after the three poses, `expressionMetrics().resolutions` 3,
6, 9 and `flatPassMetrics().entries` 2, 4, 6 (cumulative from a
`resetExpressionMetrics()` after the mount). The same on the
implementation.

## 3.3 and 4.2 On the implementation

After 3.1 and 3.2 (the reader): R1 to R3, P1 to P4 and L1 to L5 green; R4
and B1 to B3 still red (606 accessor calls; the missing name). After 4.1
(the bounds): 17 of 17 green. `tsc --noEmit` clean after each.

B2 compared 51 arrays: the parity fixture's spring at its 4 cases; 21 from
the committed fixtures (the `lock` spring and the `touched` and `pascaline`
blade, which share one spec, each at 7 values of its parameter); 24 from six
hand-written specs (`line`, `arc`, `helix`, `spline`, a path of `line`,
`arc` and `helix`, and `wrap`, over both profiles) at 4 values each; and
the test spring at `height` 1e39 and 1e308. Molejo refused none; 2 arrays
had positions that are not finite.

## 5.1 The existing tests, E1 to E5

`src/flexible.test.ts` with E1 to E5 changed, before any source change:
`Tests 32 passed (32)`. On the implementation: `Tests 32 passed (32)`.

## 5.2 The mutations

Each applied to `src/flexible.ts` by a script, the final
`src/flexible-rebuild.test.ts` run, the file restored from a saved copy and
confirmed byte-equal with `cmp` before the next.

| Mutation | Red | First failure of the named test |
|---|---|---|
| M1, roots reused whenever held | L1 (also L1b, L3, L4, L5) | L1: `expected { p: '8', q: '10' } to deeply equal { p: '10', q: '8' }`, the traded values |
| M2, `rebind` keeps `roots` | L2 | `expected +0 to be 2` (no `prepare` after the rebind; old texts' values would follow) |
| M3, every text prepared before any is evaluated | P3 | `(1 + gate.on.x): … - "TypeError: Cannot use 'in' operator to search for 'x' in 1" + "Error: Expected ) at index 3, found ="` |
| M4, a preparing scope and a reading scope, the generation read outside both | L4 (also P3) | `TypeError: Cannot read properties of undefined (reading 'kind')`: the reading scope's own reset emptied the store between the two |
| M5, `admit` on `evalExpr` | R2 (also R3) | `expected { prepare: 5, withExpressions: 5 } to deeply equal { prepare: +0, withExpressions: 1 }` |
| M6, no morph check in the guard | B3 | `relative morph: expected [ '-29.92367935180664', …(9) ] to deeply equal …`, max x `2` where three.js gives `371.07632064819336` |
| M7, step 4 removed | B1 (also B2) | `axis 0: NaN first: expected [] to deeply equal [ [ 2, "THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. …" ], [ 2, "THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. …" ] ]`; B2: the test spring at 1e39, the sphere's report missing |
| M8, `Math.min`/`Math.max` written as comparisons | B1 | `axis 0: -0 then 0: expected [ '-0', '-5', '6', '-0', … ] to deeply equal [ '-0', '-5', '6', '0', … ]` |

Unmutated, after the eight: `Tests 17 passed (17)`.

**M8 on `NaN`: not observable, and why.** The design expects M8 red "on
`NaN` and on `-0`". It is red on `-0` only. A scratch probe of the M8
function against three.js on `[NaN, 2, 3, 1, 2, 3]` and `[1, 2, 3, NaN, 2,
3]` gave the same ten numbers on both sides (`NaN 2 3 NaN 2 3 NaN 2 3
NaN`). The reason is step 4: a `NaN` coordinate makes its distance `NaN`,
and `Math.max(most, NaN)` is `NaN`, so the radius is `NaN` whatever the box
pass did; step 4 then calls three.js's two functions, which write their
own ten numbers over the fast path's. The same holds for every array with
a coordinate that is not finite: an infinite extreme makes the centre
infinite or `NaN` on that axis, and the vertex at that extreme then has a
`NaN` difference. So on any array that is not all finite, the ten numbers
left on the geometry are three.js's own, written by three.js, and B1's
non-finite cases prove step 4's delegation rather than the fast path's
arithmetic on non-finite values. Nothing is weakened by this: the numbers
are right on those arrays in any case. It means only that an error confined
to the fast path's handling of non-finite values cannot be seen, because
that handling never decides a result.

## 5.3 The existing files, singly

Each run alone, unmodified except `flexible.test.ts` (5.1):

| File | Tests |
|---|---|
| `flexible.test.ts` | 32 passed |
| `parity-fixture.test.ts` | 16 passed |
| `color.test.ts` | 22 passed |
| `tree.test.ts` | 71 passed |
| `document.test.ts` | 65 passed |
| `validation-pressure.test.ts` | 12 passed |
| `evaluator.test.ts` | 25 passed |
| `expressions.test.ts` | 88 passed |
| `expression-reuse.test.ts` | 9 passed |
| `expression-lifetime.test.ts` | 11 passed |
| `flat-pass.test.ts` | 41 passed |
| `flat-pass-parity.test.ts` | 52 passed |

## 6. The gate

- **Widget suite** (`vitest run`, once): `Test Files 70 passed | 1 skipped
  (71)`, `Tests 1888 passed | 2 skipped (1890)`, no failure. The two skips
  are environment-gated: `src/run/profile-contact.test.ts` "loads the
  pinned actual-cover v13 Bound and replays its numeric stop"
  (`it.skipIf(!process.env.CURTA_PROFILE_V13_DOCUMENT)`) and
  `src/run/profile-installed-benchmark.test.ts` "reports one pinned
  installed Curta v13 integration attempt"
  (`it.skipIf(!process.env.CURTA_INSTALLED_PROFILE_DOCUMENT)`); neither
  variable was set. The throughput gates of `src/run/cost.test.ts` passed.
- **Typecheck** (`tsc --noEmit`): clean.
- **Bundle** (`npm run build`): `dist/machinome-viewer.js`, 932,954 bytes,
  SHA256 `a183cb1d3ae18e65bfc96a24a41bc5ebb1d30bef283430272bc9533abf1b9b6b`.
  The guard is in it (`e.getX!==t.getX||e.getY!==t.getY||…`).
- **Python suite** (`pytest tests -rs` on the bench's `.venv`, once, after
  the build): `284 passed, 2 skipped, 71 warnings in 281.21s`, no failure.
  Both skips are `tests/test_curta_drawing.py` (lines 375 and 469): "the
  Curta's own builds are not at
  …/machinome/WTs/projects/Calculators/Curta-Type-I-3x/_build", a project
  build outside this repository. No browser test was skipped for a missing
  Chromium or Playwright. The warnings are Pillow's deprecation of
  `Image.getdata`. The bundle's SHA256 was the same after the suite.

## Departures from the design, and what it left open

- **L1 is two tests.** The design's L1 ends "the next read 0". That is a
  count the base cannot meet (it prepares every text on every read: 2), and
  task 2.2 requires L1 to pass on the base. So L1 keeps the values after the
  reclamation and its 2 `prepare` calls, and passes on the base; the next
  read's 0 is `L1b`, red on the base on that count (2) and green on the
  implementation. In L1 the values are asserted before the count, so M1
  shows the traded values; the count is captured right after the read,
  before the comparison's own `evalExpr` calls.
- **P1's object** is `v`, not an object literal (above).
- **E1.** With its two `toHaveBeenCalledTimes(1)` the line that installed
  the two spies (`const { box, sphere } = bounds(mesh);`) went too, since
  nothing reads them after. E1 to E5 share helpers added at the top of
  `flexible.test.ts` (`SENTINEL`, `mark`, `marked`, `tenOf`,
  `threeBoundsOf`). No other line of that file changed.
- **The guard reads `THREE.BufferAttribute.prototype`'s accessors at each
  call**, not references captured at module load. A spy installed on the
  prototype (R4, and B3's normalized case) is then the prototype's own and
  the fast path runs, which is what R4 needs; for any other caller the two
  readings are the same.
- **The attribute is read as `geometry.attributes.position`**, three.js's
  own reading, and the `Float32Array` check is `instanceof` (a subclass
  indexes as a `Float32Array`). `boundingBox` and `boundingSphere` are
  allocated on `=== null`, as three.js does.
- **`evaluator.ts`** gained a type import of `NodeId` for `evalPrepared`'s
  signature, and a docstring for it; `evalExpr` makes the same calls in the
  same order (`prepare`, then `valueOf`, then the conversion).
- **Tests** are named with the design's labels (R1 … B3). "The test spring"
  is a helix of 24 segments with an 8-sided wire (202 vertices). B2's `wrap`
  takes its parameter as the first circle's radius: with it as the second
  circle's centre, molejo refused two of the four values ("around[0] and
  around[1] are too close"). B3's `GLBufferAttribute` is given `{}` for a
  buffer. P1's judged values come from a second part, never evaluated, so
  that molejo is asked at every scope. R3 counts molejo's calls as well, to
  show the part was reached in both operations.
- Nothing in `tree.ts` or `expressions.ts` changed, and no other test.

## Reviewer's record: review of the implementation and task 7.2

Written by the repository agent, 21 November 2026, after the applier stopped.

### Review of the implementation

The diff of `src/evaluator.ts` and `src/flexible.ts` was read line by line
against design Decisions 1 and 2 and against three.js 0.156.1's
`computeBoundingBox`, `computeBoundingSphere`, `Box3.setFromBufferAttribute`
and `getCenter`: the reader is the design's code block; the bounds perform
three.js's operations in its order; no difference found.

Seventeen faults of the reviewer's own, none of them from the design's
list, were then planted in `src/flexible.ts` one at a time, with
`src/flexible-rebuild.test.ts` and `src/flexible.test.ts` run against each
and the file restored and checked by digest after the last. The verdict
script was first tried on one fault known to be equivalent and one known to
be real.

| Fault planted | Result |
|---|---|
| `dx` as vertex minus centre (the control: the squares are the same) | passes, as it must |
| the sphere pass skips the first vertex | B1, B2 red |
| the centre as `min * 0.5 + max * 0.5` | passes: equivalent, halving is exact and single-precision values neither overflow nor underflow as doubles |
| the centre divided by 2 in place of multiplied by 0.5 | passes: equivalent, the same exact scaling |
| the distance's sum re-associated | B1, B2 red |
| the box pass skips the last vertex | B1 red |
| the empty test with `<=` | B1 red |
| the radius maximum by comparison in place of `Math.max` | B1, B2 red |
| the guard without the item size | B3 red |
| the guard without the `Float32Array` test | passed: a gap, closed below |
| the box's `max.z` written from `x` | B1, B2, B3, R4 and two other tests red |
| the roots committed before the loop | P3 red |
| the skip test with `===` in place of `Object.is` | P2 and four other tests red |
| the reader without the conversion to a number | P1 red |
| the bounds computed on the first build only | R4 and one other test red |
| the generation read before the scope opens, one scope kept | passed: a gap, closed below |
| step 4 on a `NaN` box only | B1, B2 red |

Twelve were caught as the tests stood, three are equivalent, and two showed
gaps in the proof, not in the implementation:

- **The array test of the guard was held by no case.** Design B3 names a
  `Float16BufferAttribute` for it, but in three.js 0.156.1 that class has
  accessors of its own, so the accessor test already turns it away. What
  the array test alone turns away is an integer array marked normalized,
  whose values only `BufferAttribute`'s accessors denormalize. The reviewer
  added that case to B3 ("normalized shorts"); with the fault planted again
  B3 is red.
- **"The generation is read inside the scope" was held only against the
  prototype's two scopes.** With one scope and the generation read just
  before it opens, design L4 still passes: under the suite's
  `everyOperation` switch from the first read on, the held generation is
  always one behind, so the roots are never reused. The reviewer added L4b:
  a part read once, the pressure switched on, then read again, so the roots
  are of the present generation when the read begins and the scope's own
  start empties the store. With the fault planted again L4b is red (a stale
  id read from the emptied store). On the base source L4 and L4b both pass.

The applier's own finding stands and needs no change: a fault confined to
how the fast path treats positions that are not finite cannot be seen,
because for every such array step 4 has three.js write the result.

Final gate with the two added cases: the widget suite 70 files passed and 1
skipped, 1,889 tests passed and 2 skipped (the two environment-gated Curta
profile tests), no failure; `tsc --noEmit` clean; the bundle rebuilt
byte-identical, SHA256
`a183cb1d3ae18e65bfc96a24a41bc5ebb1d30bef283430272bc9533abf1b9b6b`.

### 7.2 The Enigma I page

Method: `workflow/evidence/enigma-flexible-rebuild-cost-2026-11-21.md`'s.
`enigma-i` at `081f4e6`, its `_build-page/`, headless Chromium (Playwright),
WebGL draw calls counted and not executed, so every time is script time on
the measuring machine (a virtual machine). The viewer was built unminified
from source with timers placed by a build-time text edit around the read and
the bounds call inside `FlexibleShape.evaluate`, so the measured code is the
source's own: once from the base (`cb0a5958`) and once from this bench, each
with npm molejo 0.2.0 and with molejo's `main` (`363847a`). Each build ran
in its own page load: a Press and a Release to settle, then three measured
rounds of both.

Script per changing frame of a key press, in milliseconds, lowest to highest
of the measured rounds (Press and Release together):

| | Base, npm molejo | This change, npm molejo | Base, molejo `main` | This change, molejo `main` |
|---|---|---|---|---|
| Page loads, rounds each | 2, 3 | 2, 3 | 1, 3 | 1, 3 |
| The frame | 105.0 to 126.0 | 82.7 to 96.7 | 80.2 to 92.8 | 60.2 to 64.8 |
| The flexible parts | 59.6 to 85.8 | 39.6 to 55.0 | 36.9 to 44.5 | 20.3 to 21.9 |
| Reading the parameters | 13.0 to 19.1 | 7.6 to 10.0 | 13.0 to 15.9 | 8.4 to 9.1 |
| The bounds | 16.9 to 23.4 | 3.8 to 4.9 | 15.2 to 20.5 | 4.0 to 4.5 |
| Pictures in the two seconds | 15 to 20 | 19 to 25 | 22 to 25 | 30 to 31 |
| The click's own task | 84.3 to 115.0 | 78.1 to 92.0 | 58.0 to 73.7 | 53.0 to 60.1 |

Every frame reads 36,415 parameters and rebuilds about six parts, 0.94 to
1.11 million vertices, in all four builds.

Self-check, in the two builds of this change, during presses, releases, key
selections, wheel steps and a flap: each read's values against `evalExpr` of
each text in the same scope, and each rebuild's ten numbers against
three.js's own two functions run on the same geometry, with `Object.is`.
6,154,135 parameter values and 990 rebuilds' bounds (161.8 million vertices)
compared: no difference. No page error in any run.

### The expectations of task 7.2

- No difference in either self-check: held.
- Reading the parameters near 10 ms a frame where it was 16 to 17: 7.6 to
  10.0, where the base read 13.0 to 19.1 in these runs.
- The bounds near 5 ms where they were 16 to 19: 3.8 to 4.9, where the base
  took 15.2 to 23.4.
- The frame with npm molejo lower by about 15 to 20 ms: lower by about 24
  to 27 (medians 113.3 and 116.0 for the base's Press and Release, 89.6 and
  88.6 for this change's). More than the two components account for; not
  explained, and within what two page loads of one build differ by.

Limits: script time on one virtual machine; one or two page loads a build;
the timers' own cost is in every figure; no GPU was involved and nothing was
measured on a maker's hardware; the Enigma document is a project's and its
inputs cannot be committed here.

### Records

Task 8.2: the measurement confirms the design, so ADR-043 carries an
amendment of 21 November 2026 (a flexible part holds its parameters' roots
with their generation). The bounds take no decision record, as the design
states. The finding in `workflow/warts.md` is closed with these figures.
The design's list of tests was brought in line with what was built: L1 and
L1b, L4b, P1's object, B3's normalized shorts.

