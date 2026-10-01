# Implementation evidence

## Authority and scope

Cycle 2 of Videomaker's curta-video campaign, on branch `pose-a-take`
(worktree `WTs/pose-a-take`), cut from `curta-video` at `fae72ee`, which
carries the take contract, `declare-a-take` (ADR-011), `reframe-join`
(ADR-010) and the spike's note. The planning commit is `58d4736`. Nothing was
pushed or published; no network or paid request was made; nothing was
installed. No Python source, schema, contract section other than the API
sentence, or viewer source was changed. The viewer was reached only through
the bundle selected by path: the API 29 bundle of the viewer cycle
`on-demand-clocked` (banner `machinome-viewer 0.7.1 - viewer API 29`, sha256
`b5fcdb8613aceb39…`), and once the API 28 bundle of the viewer checkout, to
see the take's API test fail by name. Neither path is written into the
repository. Integration into `curta-video` is the orchestrator's.

Environment: Linux, 16 cores, Node v24.11.1, vitest 5.0.3, Playwright's
Chromium, Python 3.12 from the workspace venv. Other agents may have run
suites in other worktrees; the load is given with the full run.

## Red

Every red below was run before the code it proves was written, except where
the section says otherwise.

### Layer 3 (`test/take.test.mjs`)

First run, before `src/take.mjs` existed:

    FAIL  |pure| test/take.test.mjs [ test/take.test.mjs ]
    Error: Cannot find module '../src/take.mjs' imported from …/test/take.test.mjs

Then with `src/take.mjs` written and `movie.mjs`, `timeline.mjs` unchanged
(the behaviour the import error hid):

    FAIL  |pure| test/take.test.mjs > the recorded banks of the counter are its replay at every mark; a forged one is refused naming the mark and the id
    AssertionError: was not refused
    FAIL  |pure| test/take.test.mjs > a view on the counter carries the bank of its take time and no loop time
    AssertionError: nine starts on the bank of one
    + undefined
    - { crank: 360, tens: 0, units: 1 }
    FAIL  |pure| test/take.test.mjs > a movie on a take needs Viewer API 29, its first reason the clocked take
    +   api: 28,
    -   api: 29,
          Tests  3 failed | 7 passed (10)

The seven that passed are the bank rule's own tests against the new module.
On the base, layer 2 was red as the brief said
(`fixture count has no pinned resolution fixtures/resolved/count.json`;
`take-bank-differs.json was not refused`); with the take rules ported into
`checkMovie` every one of the 68 invalid fixtures is refused by its words,
and with `fixtures/resolved/count.json` pinned the registered-document test
passes.

### Layer 4 (`stage/take.test.tsx`)

    TypeError: poseView is not a function
    AssertionError: expected [Function] to throw error matching /^View counting\.view in shot once: .*…/ but got '(0 , __vite_ssr_import_1__.viewMachin…'
          Tests  7 failed (7)

### Layer 5 (`test/browser/take.test.mjs`, the new test of `test/browser/reframe.test.mjs`)

Cold, with the stage's runtime changed but `src/render.mjs` not yet (so the
stage refused the take's missing identity), and with the stage's canvas wait
put back to its one-sided form for this run only:

    FAIL  |slow| test/browser/reframe.test.mjs > a canvas that follows a shrinking box several frames late is waited for; one that never shrinks is refused
    AssertionError: every frame of the shrinking join is posed into a canvas of its box's size
    +   '2.50 s: canvas 434.40625×287.78125 in 432.171875×287.15625',
    +   '2.53 s: canvas 432.171875×287.15625 in 428.59375×286.140625',
    …   (every one of the 22 frames of the join)
    FAIL  |slow| test/browser/take.test.mjs > every view on the take is restored to its frame's bank, never given a loop time, and reports the bank it holds
    Error: page.evaluate: Error: View counting.view in shot once: the viewer's machine is d46d4f1ee76199bce9aa9924e34a97020fd28bd3073939a2a85ec0eceb1111d6, and the take was recorded on undefined (take.identity)
    FAIL  |slow| test/browser/take.test.mjs > a viewer that answers a step otherwise than the take is refused before the first frame, naming the step and the field
    AssertionError: The input did not match the regular expression /The viewer does not reproduce the take: step step-2 \(take\.steps\[1\]\), commits\[0\]\.targets\.units: the viewer gives 7, the take records 2/.
          Tests  6 failed | 2 passed (8)

The first is the spike's finding made a test: a canvas four animation
frames late is left larger than its shrinking box on every frame of the
reframe, and the one-sided wait poses into it.

### Layer 8 (`test/pipeline/movie-pipeline.test.mjs`)

    AssertionError: The input did not match the regular expression /^ {2}counting: take [\d.]+ s, chapter 11\.40 s, tail [\d.]+ s\nTake: 3 steps, …/m. Input:
    'Count: 1 chapters, 3 shots, 11.4s; model 8s\n' +
      '  counting: take 10.84 s, chapter 11.40 s, tail 0.36 s\n' +
      'Viewer API 29 required for clocked take, highlight (shot carry); /tmp/videomaker-movie-WXPwou/viewer-double.js declares API 29\n' +
          Tests  1 failed | 11 skipped (12)

### Mutations, each restored and the file compared

Tests written after their code, shown not vacuous by removing the code:

| removed | went red |
|---|---|
| the refusal of a clocked export filmed as a loop (`checkProject`) | `the load films a take on a clocked export, …`: `AssertionError: was not refused` |
| the refusal of a running program (`checkProject`) | the same test, `AssertionError: was not refused` |
| the renderer's `Viewer canvas exceeds its view` | `a canvas that follows a shrinking box …`: `AssertionError: Missing expected rejection.` |

### Layer 6 with an older bundle

The take's layer 6 run with the API 28 bundle selected fails every test, the
API test naming the path and both APIs:

    Error: The selected viewer bundle …/machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js declares Viewer API 28; the fixture movie needs 29 (VIDEOMAKER_VIEWER_BUNDLE)
    Error: page.evaluate: Error: View counting.view in shot once: the viewer did not mount: on-demand rendering requires a posed document without instructions

## Green, file by file, on the API 29 bundle

    ✓ |viewer| test/viewer/take.test.mjs (5 tests) 17853ms
      ✓ the bundle declares the Viewer API a take needs, and its machine is the export's, read from a mounted instance 669ms
      ✓ every step of the recorded take, replayed on the viewer from its bank, returns the framework's request exactly 483ms
      ✓ posing one bank, then another, then the first gives identical pixels; the banks at the marks are the recorded ones; no viewer control is shown 652ms
      ✓ a copy of the take with one commit's target forged is refused before the first frame, naming the step and the field 362ms
      ✓ the counter's take is checked, previewed and rendered with the real viewer 15679ms

The second test compares, beyond what the session compares, every field of
every request (`input`, `origin`, `end`, `admitted`, each commit's
`fraction`, `value`, `targets` and `relations`, the number of stops) and the
bank the machine holds after it, with `Object.is`: no difference.

## The suites on the final content

- **Node**, `VIDEOMAKER_VIEWER_BUNDLE=<the API 29 bundle> npm test`, started
  02:45:20 (1-minute load 0.42), on the final content but this file and
  `tasks.md`, which no key reads:

      Test Files  38 passed (38)
           Tests  372 passed (372)
        Duration  804.01s (tests 98%, import 1%)
      Test memo: 0 passed from the memo, 372 run

  Every slow test ran (the viewer double, the stage runtime and the
  renderer changed, so every key missed); the viewer layer ran:
  `✓ |viewer| test/viewer/real-viewer.test.mjs (7 tests) 143330ms` and
  `✓ |viewer| test/viewer/take.test.mjs (5 tests) 18360ms`.
- **Python**, `python -m pytest -q` in `python/`, run alone after the Node
  suite: `279 passed in 11.31s`. (An earlier Python run was started while
  the Node suite was still running in this worktree, against the rule; it
  also passed, and the run quoted here is the one made alone.)

## Findings

1. **The contract does not say which step owns the instant between two
   steps.** "For a take time `t` inside a step … Between steps, and after
   the last, the bank is the one the previous step ended with": at the
   instant one step ends and the next begins, `f = 1` of the first and
   `f = 0` of the second both apply, and they differ when the second has a
   commit at fraction 0. The implementation gives the instant to the step
   that ends there (`at < t ≤ at + duration`), which is the only reading
   under which a mark, "the instant after the step before it", is posed on
   `banks[mark]`; a test pins it. Smallest correction: one sentence in "The
   take" of `docs/movie-document.md`, "a step owns its end: the instant one
   step ends and the next begins is posed on the bank the first ended
   with".
2. **`origin + f · (end − origin)` at `f = 1` is not always `end`**
   (`0.7 + 1 · (0.1 − 0.7)` is `0.09999999999999998`). The implementation
   writes `end` exactly at `f = 1`, so a mark's bank equals the record
   exactly; a test pins it. Smallest correction: "(exactly `end` at
   `f = 1`)" in the same paragraph; the Python side does not compute poses
   and is unaffected.
3. **An older viewer refuses a clocked document before the stage can read
   its API.** The stage's API refusal reads `apiVersion` from a mounted
   instance; a Viewer API 28 bundle refuses to mount the clocked document
   under on-demand rendering (`on-demand rendering requires a posed
   document without instructions`), so `preview` and `render` stop on the
   viewer's own words, which the stage quotes naming the view and the shot.
   `check` names the requirement from the bundle's banner first
   (`Viewer API 29 required for clocked take, …`). Recorded, not changed.
4. **The API 29 on-demand mount shows no full-screen control.** The layer 6
   test asserts that no `.machinome-fullscreen` element is visible on a
   posed view of the clocked fixture, so the stage's stylesheet is
   unchanged (design D9).
5. **The counter export's mesh names with commas and `=`**
   (`declare-a-take`'s finding 5) are served by the stage's asset server
   as they are: the clocked fixture mounted, posed and rendered.
6. **The bank's integers and floats do not matter to parity on the
   counter.** The spike noted that JSON cannot carry Python's distinction
   between `0` and `0.0`; the replay on the real viewer and the per-frame
   and per-mark readbacks are exact with `Object.is` on the fixture.
7. **The session's per-frame bank check runs on its probe pose too**, so a
   viewer that holds another bank than the one restored is refused at the
   film's first frame, before the take's replay; a test asserts the time it
   names (`at 0.00 s`).
8. **The viewer double's part rectangles move with a loop's time, which a
   view on a take does not set**: with the double, a mark on a take's view
   stays where it is at time 0. The fixture `count` has no mark; a test of
   marks on a take with the double would need the double to move them with
   the bank. Not built (no episode needs it in a test yet).
9. **`CHANGELOG.md`'s `declare-a-take` bullet still says the commands do
   not read a take document.** It is that change's bullet and is left as
   written; the `pose-a-take` bullet above it says they do. The
   orchestrator may strike the stale sentence at merge.

## What was not done, and why

- Running machines stay refused (`program`), by the ruling; no scenario
  take is recorded by a framework command.
- No change to the Python side, the schema or the viewer; the two contract
  sentences of findings 1 and 2 are recorded with their smallest
  correction, not written into the orchestrator's page.
- The stage's stylesheet does not hide the viewer's full-screen control:
  the API 29 on-demand mount shows none (finding 4).
- The double moves no mark with a take's bank (finding 8).
- The Curta film itself is cycle 4's.
- Task 0.3, the orchestrator's review of the planning commit, is not
  claimed.
