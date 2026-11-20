# Evidence: rebuild-only-changed-flexible-parts

Applier's record for tasks 1.2 to 6.1 and 7.1. Task 6.2 (the Enigma I
page) is the reviewer's and is not recorded here. Every command ran from
`packages/machinome-viewer/machinome/viewer/web/widget/` in the bench
`machinome/WTs/rebuild-only-changed-flexible-parts`, one at a time, with the
primary checkout's executables (`node_modules/.bin/vitest`, `tsc`) and the
bench's own `node_modules`; vitest 3.2.7.

## 1.2 The bench

- `git log`: HEAD `5e6c2fa9` ("plan: rebuild a flexible part only when its
  values change"), whose parent is
  `69cf7a3f9d002c65429c9de064bc61a38af4d9ef`; `git status --short` empty.
- `openspec validate rebuild-only-changed-flexible-parts --strict` (from
  `packages/machinome-viewer/`): "Change
  'rebuild-only-changed-flexible-parts' is valid".

## 2.1 The test expressions, checked with `evalExpr`

Checked on the base source with a temporary `describe` block appended to
`flexible.test.ts` (scope `{ time: 0, drivers: { valvetrain: { lift },
gate: { on } } }`), run once and then removed. Output:

```
A min(46.8, (66.8 - valvetrain.lift)) @lift 0 = 46.8
A min(46.8, (66.8 - valvetrain.lift)) @lift 3 = 46.8
A min(46.8, (66.8 - valvetrain.lift)) @lift 30 = 36.8
B (46.8 - valvetrain.lift) @lift 0 = 46.8
B (46.8 - valvetrain.lift) @lift 3 = 43.8
D (1 + gate.on.x) @gate.on 1 THROWS TypeError: Cannot use 'in' operator to search for 'x' in 1
D (1 + gate.on.x) @gate.on 0 = NaN
D (gate.on.x * 0 + 1) @gate.on 0 = NaN
E ((valvetrain.lift / 0) * 0) @lift 1 = NaN
E ((valvetrain.lift / 0) * 0) @lift 2 = NaN
H (0 * valvetrain.lift) @lift 1 = 0
H (0 * valvetrain.lift) @lift -1 = -0
G (46.8 - (1.0 * valvetrain.lift)) @lift 0 = 46.8
free (1 + gate.on.x): gate.on.x
free min(...): valvetrain.lift
```

Every value is the one design Decision 5 states. No expression was
replaced.

One detail the design leaves implicit: the free name `freeVariables`
reports for `(1 + gate.on.x)` is `gate.on.x`, not `gate.on`. Test D
therefore puts `valvetrain.lift` and `gate.on.x` in its change set. Either
name alone reaches the part, since `height` reads `valvetrain.lift`.

## 2.2 Tests A to E, red on the base

The tests are in `flexible.test.ts`, in the new `describe` "a reached part
is rebuilt only when a value moved". Test A is split into two `it`s, so
that its second half can be shown to pass on the base:

- A: "keeps a part whose values a changed name left as they were"
- A, second half: "rebuilds that part when a value then moves"
- B: "rebuilds only the one of two reached parts whose values moved"
- C: "rebuilds nothing on an update of everything at unchanged values"
- D: "keeps what it remembers when a parameter expression throws part-way"
- E: "holds a NaN in a parameter the spec does not read as the same value"

`vitest run src/flexible.test.ts` on the unmodified `flexible.ts`
(24 tests, of which 6 new):

```
   × ... > keeps a part whose values a changed name left as they were 8ms
     → expected 2 to be 1 // Object.is equality
   ✓ ... > rebuilds that part when a value then moves 5ms
   × ... > rebuilds only the one of two reached parts whose values moved 2ms
     → expected 4 to be 3 // Object.is equality
   × ... > rebuilds nothing on an update of everything at unchanged values 2ms
     → expected 2 to be 1 // Object.is equality
   × ... > keeps what it remembers when a parameter expression throws part-way 5ms
     → expected 2 to be 1 // Object.is equality
   × ... > holds a NaN in a parameter the spec does not read as the same value 1ms
     → expected 2 to be 1 // Object.is equality

 FAIL ... > keeps a part whose values a changed name left as they were
AssertionError: expected 2 to be 1 // Object.is equality
 ❯ src/flexible.test.ts:420:27
    418|     tree.update(scope(3), lifted());
    420|     expect(evaluations()).toBe(1);

 FAIL ... > rebuilds only the one of two reached parts whose values moved
AssertionError: expected 4 to be 3 // Object.is equality
 ❯ src/flexible.test.ts:459:27
    457|     tree.update(scope(3), lifted());
    459|     expect(evaluations()).toBe(count + 1);

 FAIL ... > rebuilds nothing on an update of everything at unchanged values
AssertionError: expected 2 to be 1 // Object.is equality
 ❯ src/flexible.test.ts:474:27
    472|     tree.update(scope(0));
    474|     expect(evaluations()).toBe(1);

 FAIL ... > keeps what it remembers when a parameter expression throws part-way
AssertionError: expected 2 to be 1 // Object.is equality
 ❯ src/flexible.test.ts:506:27
    504|     tree.update(gated(0, 0), both());
    506|     expect(evaluations()).toBe(1);

 FAIL ... > holds a NaN in a parameter the spec does not read as the same value
AssertionError: expected 2 to be 1 // Object.is equality
 ❯ src/flexible.test.ts:520:27
    518|     tree.update(scope(2), lifted());
    520|     expect(evaluations()).toBe(1);

      Tests  5 failed | 19 passed (24)
```

Each of A to E fails on the molejo-call count, at the assertion the design
names. D fails on its last update (line 506): on the base, the update that
throws already made no molejo call and left the version and positions as
they were, as the design expects. The second half of A passes on the base.
All 18 existing tests pass.

## 3.1 The implementation

`flexible.ts` only; `tree.ts` is unchanged.

- A private `built: number[] | undefined`, with a comment stating the
  invariant.
- `evaluate` evaluates every parameter into a fresh array `next`. It
  returns if the buffers exist, `built` is defined, the lengths are equal,
  and `Object.is` holds at every position. Otherwise it sets
  `built = undefined`, builds the `{name: value}` record from `next`, calls
  molejo, attaches the buffers on the first call, sets `needsUpdate`,
  computes both bounds, and sets `built = next` last.
- `rebind` sets `built = undefined`.
- The module comment and the `evaluate` docstring say that a reached part
  is rebuilt only when a value moved.

`vitest run src/flexible.test.ts`: 24 passed (24).

## 4.1 Tests F, G and H

- F: "rebuilds after the evaluator refused, whatever it left in the
  buffers". The spy's next call is replaced, with `mockImplementationOnce`,
  by one that fills the given `positions` with `NaN` and throws
  `values: refused`. The update from lift 0 to 6 throws. The update back to
  lift 0 makes one molejo call, and the positions equal the mount's.
- G: "rebuilds after a reconcile rebound its expressions, at equal values".
  The test reconciles to the same spec with
  `height: '(46.8 - (1.0 * valvetrain.lift))'`, then updates at lift 0 with
  `valvetrain.lift` changed. It expects one molejo call and asserts the same
  position array, so the reconcile is known to have taken the rebind path.
- H: "holds -0 and 0 to be different values". The part has `height: '46.8'`
  and `tilt: '(0 * valvetrain.lift)'`. Moving lift from 1 to -1 makes one
  molejo call.

All three pass on the base. The full file ran with `flexible.ts` restored
temporarily from `HEAD`: 5 failed (A, B, C, D, E as in 2.2) and 22 passed,
F, G and H among them.

Each test was then shown red against the implementation with its own guard
removed, and the guard was restored. After each run the file was compared
with the saved implementation and matched.

F, with `this.built = undefined;` before the molejo call removed:

```
   × ... > rebuilds after the evaluator refused, whatever it left in the buffers 7ms
     → expected 2 to be 3 // Object.is equality
 ❯ src/flexible.test.ts:544:27
    542|     tree.update(scope(0), lifted());
    544|     expect(evaluations()).toBe(count + 1);
      Tests  1 failed | 26 passed (27)
```

G, with `this.built = undefined;` in `rebind` removed:

```
   × ... > rebuilds after a reconcile rebound its expressions, at equal values 7ms
     → expected +0 to be 1 // Object.is equality
 ❯ src/flexible.test.ts:560:27
    559|     expect(positionsOf(meshOf(tree.children[0])).array).toBe(array);
    560|     expect(evaluations()).toBe(1);
      Tests  1 failed | 26 passed (27)
```

H, with `Object.is(value, built[i])` replaced by `value === built[i]`:

```
   × ... > keeps what it remembers when a parameter expression throws part-way 10ms
     → expected 2 to be 1 // Object.is equality
   × ... > holds a NaN in a parameter the spec does not read as the same value 3ms
     → expected 2 to be 1 // Object.is equality
   × ... > holds -0 and 0 to be different values 1ms
     → expected 1 to be 2 // Object.is equality
 ❯ src/flexible.test.ts:571:27
    569|     tree.update(scope(-1), lifted());
    571|     expect(evaluations()).toBe(2);
      Tests  3 failed | 24 passed (27)
```

With `===`, D and E also fail, because `NaN !== NaN`. That is expected, and
shows that both tests depend on Decision 2's `NaN` rule. The existing
"re-evaluates a spring whose expressions a reconcile replaced" still passed
without the forgetting in `rebind`, because its height moves from 46.8 to
40.8 (Decision 6).

## 4.2 Existing tests

`git diff --numstat src/flexible.test.ts` reports `186 0`: additions only,
and no existing line is changed. Every test listed in design Decision 6
passes as written: the 18 existing tests in `flexible.test.ts`, the 16 in
`parity-fixture.test.ts` and the 21 in `color.test.ts`, singly, and the
whole suite below.

## Counted work per test (implementation)

The design's step: what happens to the part between the step's start and
its end.

| Test | Step | Molejo calls | Position version | Bounds passes (box, sphere) |
|---|---|---|---|---|
| A | lift 0 to 3, `min` height stands at 46.8 | 0 | unchanged | 0, 0 |
| A, second half | lift 3 to 30, height 46.8 to 36.8 | 1 | risen | 1, 1 |
| B | lift 0 to 3: `kept` (min) and `moved` (46.8 - lift) | 1 in total | `kept` unchanged, `moved` risen | not counted |
| C | `update(scope(0))`, `'all'`, at the mount's scope | 0 | unchanged | 0, 0 |
| D | lift 0 to 3 and `gate.on` 0 to 1: `z` throws a TypeError | 0 | unchanged, positions unchanged | not counted |
| D | back to lift 0 and `gate.on` 0 | 0 | unchanged | not counted |
| E | lift 1 to 2, unread `gap` NaN to NaN | 0 | unchanged | not counted |
| F | lift 0 to 6, the call refused after writing NaN | 1 (refused) | not counted | not counted |
| F | back to lift 0 | 1 | positions equal the mount's | not counted |
| G | rebind to equal-valued text, update at the same lift | 1 | not counted | not counted |
| H | lift 1 to -1, unread `tilt` 0 to -0 | 1 | not counted | not counted |

On the base, the same steps make A 1, B 2, C 1, D (last update) 1 and E 1
molejo calls.

## 5.1 The widget gate

Each command ran once, in this order, one at a time:

- `vitest run src/flexible.test.ts`: 1 file, 27 passed (27).
- `vitest run src/parity-fixture.test.ts`: 1 file, 16 passed (16).
- `vitest run src/color.test.ts`: 1 file, 21 passed (21).
- `vitest run` (the whole suite): exit 0, Test Files 67 passed and 1
  skipped (68), Tests 1765 passed and 2 skipped (1767), 54.15 s. No
  failures; the two `src/run/cost.test.ts` throughput gates passed on this
  run. The two skips need environment variables that this bench does not
  set:
  - `src/run/profile-installed-benchmark.test.ts`, "reports one pinned
    installed Curta v13 integration attempt", is skipped by
    `it.skipIf(!process.env.CURTA_INSTALLED_PROFILE_DOCUMENT)`.
  - `src/run/profile-contact.test.ts`, "loads the pinned actual-cover v13
    Bound and replays its numeric stop", is skipped by
    `it.skipIf(!process.env.CURTA_PROFILE_V13_DOCUMENT)`.
- `tsc --noEmit`: exit 0, no output.

## 5.2 The bundle and the Python suite

- `npm run build` (`node build.mjs`): `dist/machinome-viewer.js` 900.5kb,
  exit 0. The file is
  `packages/machinome-viewer/machinome/viewer/web/widget/dist/machinome-viewer.js`
  (922,061 bytes), SHA256
  `4b2e8fdc2bb10a55c512d142da4c6b9363b7de882eba6202cf9a2c5c51ab7693`.
- `.venv/bin/python -m pytest tests -rs -q` (from
  `packages/machinome-viewer`, the bench's venv, run after the build):
  exit 0, 276 passed, 2 skipped, 71 warnings, 215 subtests passed in
  278.54 s. No failures. No browser test was skipped, so the browser
  end-to-end tests (`tests/test_widget_e2e.py`, the lock, touched and
  pascaline fixtures among them) ran. The two skips are not browser
  skips. Both are in `tests/test_curta_drawing.py` (lines 375 and 469),
  with the reason "the Curta's own builds are not at
  …/WTs/projects/Calculators/Curta-Type-I-3x/_build": the tests need a
  project build that this bench does not have. The warnings are
  deprecation warnings (Pillow's `Image.getdata`, among others). The
  suite did not rebuild the bundle: its mtime and SHA256 are the same
  after the run.

## 7.1 CHANGELOG

One bullet was added under "Unreleased" in
`packages/machinome-viewer/CHANGELOG.md`, after the two already there and in
their form. It ends with "Viewer API 30 and document versions 1 through 14
are unchanged."

## Decisions the design left open

- Test A is two `it`s rather than one, so that the second half (the change
  of value rebuilds) runs, and passes, on the base. As a single test it
  would stop at the first half's failure there.
- The bounds passes are counted in A, A's second half and C. B, D, E, F, G
  and H count molejo calls, and where the design names them, versions and
  positions.
- D's change set is `valvetrain.lift` and `gate.on.x`: the free name
  reported for `gate.on.x` is the whole path (see 2.1).
- F's refusal is a one-call `mockImplementationOnce` on the existing spy.
  It writes `NaN` only if buffers were handed to it (they always are after
  the mount), and it throws `Error('values: refused')`.
- G also asserts that the position array is the same object after the
  reconcile, so the test is known to exercise `rebind` and not a new
  `FlexibleShape`.
- `evaluate` builds `next` with `this.params.map` and then the record from
  `next`. The design's step 1 leaves the form open. The order of evaluation
  (sorted by name) and the propagation of a throw are as before.

## Deviations from the design

None.

## Out of scope, found while proposing

From the design's "A pre-existing gap found while reading", in its own
words: "`WidgetTree.update` copies the prepared matrices into the live
groups before `updateShapes` runs. … Under a clocked request the machine
keeps its bank, since the pose hook threw, but the scene has moved.
`refuse-nonfinite-clocked-pose` placed transform refusal before shape
evaluation and declined a shape transaction. This change neither causes nor
repairs the gap, and it is outside this change's scope; it is reported for
the warts record." In short, a refusal that comes from a flexible part
leaves the rigid parts posed at the refused candidate.

Observed on the base source, before any change to `flexible.ts`, with a
temporary test appended to `flexible.test.ts`, run once and then deleted.
The test mounted, at lift 0, an `AssemblyNode` `rigid` with operation
`['t', ['(2 * valvetrain.lift)', '0', '0']]` beside a spring whose `height`
is `sqrt(10 - valvetrain.lift)`. It then called
`update(scope(12), { time: false, drivers: new Set(['valvetrain.lift']) })`:

```
translation before: 0; update at lift 12 threw: values: parameter 'height' must be a finite number, got nan (referenced at path[0].height); translation after: 24
```

The rigid node stands at the refused candidate's translation (24) after the
refusal. It is not fixed here.

## Reviewer's record: review of the implementation and task 6.2

Written by the repository agent, 20 November 2026, after the applier stopped
with its work uncommitted.

### Review of the implementation

The diff of `flexible.ts` was checked against design Decision 1 step by step,
and the test file's diff is additions only (186 lines, none removed). Run
again by the reviewer, one file at a time: `flexible.test.ts` 27 of 27,
`parity-fixture.test.ts` 16 of 16, `color.test.ts` 21 of 21; `tsc --noEmit`
exit 0. A rebuild of the bundle from the final source gave the SHA256 of 5.2
(`4b2e8fdc…51ab7693`).

### 6.2 The Enigma I page

Project `enigma-i` at `081f4e6`, `_build-page/`, manifest SHA256
`a8769deec38e3fbf0dca2b826ef4b7779d29d2137ad7977e2f34ed9d58326fc0`. Same host
and method as `workflow/evidence/enigma-flexible-refills-2026-11-20.md`
(headless Chromium, no GPU, draw calls counted and not executed, so script
only; refills read from position-attribute versions and changes of data from
sampled position sums; each instruction pressed by `element.click()`). A
probe build of the bench's source for the tracker, and the built bundle of
5.2 for the press tasks. Single runs. No page error in either, and the
expression store stood at generation 0 with one binding preparation
throughout.

Before (viewer `69cf7a3f`, from the evidence file) and after (this change):

| Instruction (declared seconds) | Parts refilled per refilling frame | Triangles refilled, whole instruction | Parts whose data changed | Script per refilling frame, ms | Press task, ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| Press (2) | 86 → 7 | 8,470,912 → 2,328,800 | 9 → 9 | 334 → 216 | 678 → 441 |
| Release (2) | 86 → 6 | 8,470,912 → 2,205,872 | 8 → 8 | 305 → 209 | 606 → 429 |
| Key B (0), a different key | 86 → 0 | 8,470,912 → 0 | 0 → 0 | none | 313 → 160 |
| Right wheel on (0.4) | 86 → 1 | 8,470,912 → 122,928 | 0 → 0 | 183 → 92 | 670 → 300 |
| Right wheel back (0.4) | 86 → 1 | 8,470,912 → 122,928 | 0 → 0 | 175 → 77 | 642 → 292 |

The expectations of task 6.2 held. Selecting a different key refills
nothing. A key press refills exactly the nine parts whose sampled data
changes, and no other. A right-wheel step refills one part of 122,928
triangles whose sampled data does not change, which is the right
detent-return spring's size and what design Decision 2 predicted from its
parameter values moving by rounding; the part was identified by its size, not
by its name. The left and middle wheels were not stepped on the page.

A second pass over the nine instructions of the originating evidence, in the
same probe run:

| Instruction (declared seconds) | Press task, ms | Frames that changed the picture | Script per changing frame, ms |
| --- | ---: | ---: | ---: |
| Key A (0), from Key B | 172 | 0 | none |
| Press (2) | 470 | 8 | 217 |
| Release (2) | 462 | 8 | 232 |
| Right wheel on (0.4) | 300 | 1 | 246 |
| Right wheel back (0.4) | 317 | 1 | 182 |
| Open flap (1.5) | 54 | 41 | 32 |
| Open hood (4) | 67 | 103 | 34 |

With the built bundle (SHA256 `4b2e8fdc…51ab7693`): press tasks of 444 and
419 ms (Press, Release), 300 and 303 ms (right wheel on and back), 153 and
146 ms (Key B, Key A again), 53 to 70 ms (flap and hood), in agreement with
the probe build. Its first press after mounting, Key A already selected, took
638 ms, as the first press did before this change (593 ms); that is still
unexplained and is not this change's.

### What this change did not do, measured

- **A key press is still far from smooth.** A changing frame went from about
  0.33 s to about 0.22 s of script, eight pictures in two seconds instead of
  five. In the profile of one Press (4.3 s sampled), what remains is about
  1.0 s in the flexible evaluations of the parts that really change, about
  0.9 s in expression evaluation (`compute`, `resolveName`, `valueOf`), and
  1.7 s in the renderer's per-frame bookkeeping over the whole press.
- **A wheel step still shows its start and its end.** Its press task fell
  from 0.67 s to 0.30 s, but that task is still charged to a motion declared
  at 0.4 s: the first animation frame begins 0.30 s after the click and the
  next one lands the step. This is the third finding of the warts section
  (the press path), not this one.
- **Selecting a different key** costs 0.15 to 0.17 s, not the 0.05 s of
  selecting the key already selected: nothing is refilled, and what remains
  is the evaluation of what the selection feeds.

The reviewer's estimates before the change (a key press at about 0.11 s a
frame, a wheel step's frames at about 0.03 s, a key selection at about
0.05 s) were too low. They scaled the old frame's cost by the share of
triangles no longer refilled, as if the refills were all of it; the
evaluation of the expressions a moved input feeds is the part they left out.

**Acceptance (task 6.2).** The expectations as the task states them are met
and no page error occurred. Accepted, with the shortfalls above recorded.

**Not measured.** Any GPU's frame time; a browser other than Chromium; the
left and middle wheels; how much of a frame's expression evaluation is spent
on nodes whose inputs did not move.

### Final gate

Run by the reviewer on the finished state, after the archive and with it
staged, one at a time.

- Whole widget suite: 68 files, 67 passed and 1 skipped; 1,767 tests, 1,765
  passed, 2 skipped (the two environment-gated Curta files of 5.1), 0
  failed; 56.4 s.
- `tsc --noEmit`: exit 0. The bundle's SHA256 is unchanged
  (`4b2e8fdc…51ab7693`).
- Python suite: 276 passed, 2 skipped, 0 failed, 215 subtests, 282 s. Both
  skips are `tests/test_curta_drawing.py` (lines 375 and 469): the Curta's
  own builds are not on this bench.
- `openspec validate --specs --strict`: 16 passed, 0 failed.
