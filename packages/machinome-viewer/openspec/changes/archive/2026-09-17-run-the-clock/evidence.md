# Evidence: `run-the-clock` (cycle 6)

Worktree `solid-node-viewer/WTs/clocked-machine`, branch `clocked-machine`,
base `8a61314` (this change's planning commit, over cycle 5's `ee9bb6c` and
main `4a63aaa`). Producer read-only at `solid-node/WTs/clocked-machine` head
`1a959d3`. Nothing in the framework, the pilot's primary checkouts or any
other worktree was written; the PRIMARY viewer bundle was not rebuilt
(`dist/solid-widget.js` there still dated 2026-09-16, 767 290 bytes).

## 1. The base, re-measured before a line changed

- `npx tsc --noEmit` — clean.
- `npx vitest run` — **44 files, 1139 tests, 30.67 s, all green**, matching
  task 0.1's recorded baseline exactly.
- `src/clocked-corpus.json` — md5 `852b86b804ebd785f6e6b1f5568fb01a`,
  UNCHANGED by this cycle. `src/running-corpus.json` — md5
  `651a3b5750c49eecad4587438dc9a85a`, unchanged.

## 2. The RED log (task 1, task 2, task 3, task 4, task 5)

### 2.1 The corpus, pinned red before a line of source changed (task 1)

With the census closed and the departure/deferral branches deleted,
`npx vitest run src/clocked/clocked-corpus.test.ts` → **4 failed, 40
passed**. The three replay failures, verbatim and identical:

```
FAIL src/clocked/clocked-corpus.test.ts > … > replays Regulator
FAIL src/clocked/clocked-corpus.test.ts > … > replays Lift
FAIL src/clocked/clocked-corpus.test.ts > … > replays ClockAlone
Error: move('time', ...) asks this machine's clock to advance, which this
build does not yet do. The bank stands at 0 seconds and the model is posed
there; a later build moves the clock and fires the events on it.
 ❯ Object.move src/clocked/machine.ts:287:15
 ❯ replayStep src/clocked/clocked-corpus.test.ts:304:30
```

and the closed census:

```
FAIL … > the census, closed > replayed every machine, every step and every
recorded number
AssertionError: expected 71 to be 76 // Object.is equality
```

(71 rather than 68 because `replayStep` counts the step it is about to
compare before the refusal is raised.)

Task 1.3's new exactness test was then tightened so it could not pass on
the wrong throw — `toThrow(/commit 0 value/)` rather than `toThrow()` —
and went red for the right reason:

```
× the exactness claim … > rejects the CLOCK landing 0.49999999999999994
  moved by ONE representable value
```

### 2.2 The clock request (task 2)

`npx vitest run src/clocked/machine.test.ts` → **8 failed, 23 passed**.
Seven failed with the same clock-request refusal quoted above (the
backwards refusal, the `to` behind the bank, the exclusivity order, zero
admitted, `Regulator`, `ClockAlone`, `Lift`); the eighth was the
end-of-request judgement on a time request:

```
× … still JUDGES the end of a time request: a commit that carries a bounded
  coordinate out of range refuses the whole request
  → expected 'ValueError' to be 'JointRangeError'
```

One test in that block passed at once and is a CONFIRMATION rather than a
red: "no compiled constraint of Lift is even examined for the clock". It
states a property of the loaded document (the producer compiles a plan per
declared driver, so `plans.has('time')` is false and `clip` answers `null`),
which design §3 says already falls out — this cycle's work was to state it,
assert it and guard it, not to create it.

### 2.3 The loader guard (task 3)

`npx vitest run src/clocked/document.test.ts` → **3 failed, 31 passed**:

```
× … when a constraint's VALUE follows the clock   → the document was not refused
× … when a constraint's BOUND follows the clock   → the document was not refused
× … when a constraint's SHAPES name the clock …   → expected '…' to contain "this machine's CLOCK"
```

The first two are the hole the proposal names: a hand-written or corrupted
document whose `bounds[0].value` reads `(lift + time)` loaded cleanly on the
base and would then have been clipped against a coordinate the clock drives.
The third was red because the existing message says only "not a declared
driver" — an intermediate assertion of mine that merely contained `clock`
passed trivially off the refusal's own prefix ("carries a **clock**ed
machine"), and was replaced with the message's own reason before the fix.

### 2.4 The per-frame advance (task 4)

`src/clocked/clock.ts` did not exist:

```
Error: Cannot find module './clock' imported from … clock.test.ts
```

### 2.5 The transport plan (task 5.1)

`npx vitest run src/clockedControls.test.ts` → **5 failed, 8 passed**,
including `(0 , clockStepAmount) is not a function` and
`expected undefined to be 'time'` for every field of the transport.

### 2.6 A refused frame pauses (task 5.3)

This behaviour was written in the same edit as the frame hook, so the red
was produced DELIBERATELY afterwards by removing the one line
(`clockPlaying = false` in `clockFrame`'s refusal branch), rebuilding the
bundle and re-running the acceptance:

```
> self.assertFalse(refused['playing'], 'a refused frame left the transport running')
E AssertionError: True is not false : a refused frame left the transport running
```

The line was restored and the suite is green again.

### 2.7 The readout following the bank (a gap this cycle closes)

Task 6.3's screenshots exposed a real defect inherited from cycle 5: a host
driving `machine().move(...)` moved the model but left every panel readout —
the states, the drivers and the clock's seconds — showing the instant the
machine had LEFT, because only the panel's own gesture path rebuilt the
chrome. Pinned red in the page first:

```
> self.assertEqual(moved['readout'], '0:05.25')
E AssertionError: '0:00.00' != '0:05.25'
```

Fixed by wrapping `move` and `restore` on the mount handle so the chrome is
rebuilt after a committed request, whoever made it — the same rebuild a
gesture already made. This is the requirement "its readout SHALL follow the
committed bank" (cycle 5) and "the clock's readout … SHALL follow the
committed bank" (this cycle) being made true rather than a new behaviour.
The evidence is the screenshot: `tests/_shots/clocked-regulator-played.png`
reads `count 5`, `time 5.2500 s`, `0:05.25`. (It read `count 5.0000` until
completion; see §11.1.)

## 3. The census, as measured

The closed census is read off the REPLAY itself — `replayStep` accumulates
what it actually compared, and a final `describe` asserts it — so a later
build cannot narrow the suite by declaring a departure without failing
there:

```
compared.machines.size = 30
compared.steps        = 76
compared.numbers      = 722
```

**76 of 76 steps, 722 of 722 numbers, 30 of 30 machines, no departure and no
deferral.** Agreement is EXACT: every comparison is `toBe` against the
corpus's own `tolerance.float` of `0.0`, and no comparison was widened, no
fixture edited and no scenario skipped. Not one operation disagreed: the
three clock machines replayed bit for bit at the first run after the
backwards refusal was put in the producer's position — `Regulator`'s first
landing `0.49999999999999994` included.

The head-of-file census stays derived from the FILE (30 machines, 76 steps,
722 numbers, the three clock machines named by a `move` whose input is that
machine's own `clocked.clock`), and both "derived from the file" tests are
kept.

One mechanical deviation from task 1.2, recorded rather than hidden: the
helper `departureAt` is DELETED as the task says, and `clockMoves` is KEPT —
the census's "names the three machines that move a clock, off the file" test
and the "a clock request is found by the clock's own name" test are both
written on it, and design §11 requires both to survive. Its doc comment now
says what it means in this build: the steps this build EXECUTES, not departs
from.

## 4. The measurements

### 4.1 In thread (`src/clocked/cost.test.ts`), three runs each

| what | runs (ms) | events |
| --- | --- | --- |
| `Regulator` one frame at ×1 (`by` 0.01666… s) | 0.14 / 0.03 / 0.02 | 0 |
| `Regulator` one frame at ×60 (`by` 1 s) | 0.16 / 0.06 / 0.06 | 1 |
| `Regulator` one frame at ×3600 (`by` 60 s) | 3.20 / 1.10 / 1.56 | 60 |
| `Regulator` one CAPPED stalled frame (`by` 240 s) | 8.52 / 10.45 / 5.53 | 240 |
| `Regulator` per EVENT | 0.0355 / 0.0435 / 0.0231 | — |

No corpus machine was added for these: the corpus is the framework's, and
the speed ladder supplies the event rate. Said so in the test.

### 4.2 In a real page (`tests/test_regulator_document.py`, Chromium)

SOLVE AND POSE, through the same `machine()` handle a host holds, three runs
each, asserted under ONE 16 ms frame budget:

```
  Regulator frame x1 in the page:    0.300 / 0.300 / 0.400 ms
  Regulator frame x60 in the page:   0.400 / 0.500 / 0.400 ms
  Regulator frame x3600 in the page: 1.500 / 1.800 / 1.000 ms
  Regulator posed in the page:       0.200 / 0.300 / 0.300 ms
```

(Chromium coarsens `performance.now()` to 100 µs here, which is why the
small numbers are quantised. These include the panel rebuild of §2.7.)

### 4.3 The whole-corpus replay (task 7.3)

```
  the whole corpus: 76 steps over 30 machines in 15.5 ms
```

against cycle 5's recorded **13.6 ms for 68 steps**: eight more steps —
including the 5 + 3 + 4 = 12 events of the three clock machines — for 1.9 ms
more, and the per-step cost is unchanged (0.200 → 0.204 ms).

### 4.4 One floor was widened, to the design's own ratified number

The ×3600 frame measures 1.1 ms alone and **6.5 ms under a full parallel
vitest run**, so the 4 ms floor the other measurements in that file use (an
order of magnitude below the running Curta's 40 ms per crank TICK — a
gesture comparison) failed on LOAD in the full suite. The frame assertions
are held against **one frame budget, 16 ms**, which is the number design §9
ratifies for this claim, and the reason is written into the test. This is
the design's own recorded risk ("the cost floors are load-sensitive")
materialising; no other floor moved.

### 4.5 What is NOT being compared (task 7.4)

Nothing here is held against the running Curta. A clock request is not a
tick, and `Regulator` is not the Curta — which has no clock at all, and
which ADR-127 records as owing this cycle nothing and costing it nothing.
Stated in `cost.test.ts`'s header.

## 5. The page evidence (task 6)

`tests/fixtures/regulator/` — `viewer.json`, **2 116 bytes**, md5
`2f3fbfa80f4f125c5915c7f4ae74cc66`, `clocked.identity`
`281dfdc2e4e32c0c86f195c2896faed54c6ea534e9557027890f61f132505814`, plus
`models/clocked_project/pendulum-Bob-cd9fb1e148cc.stl`.

Exported VERBATIM with

```
PYTHONPATH="$PWD" solid export tests/clocked_project/pendulum.py:Regulator \
    -o <dir> --no-widget
```

from a THROWAWAY COPY (`git archive HEAD | tar -x`) of solid-node at branch
`clocked-machine` head `1a959d3`; the read-only worktree was never written
and the pilot's primary checkout was never touched. The file `solid export`
wrote (`manifest.json`) is what sits here under the name `viewer.json`,
byte for byte; the rename is the only thing done to it. The export WARNED,
as ADR-128 §15 intends and as the calculator's did:

> this model needs document version 8, and the installed browser viewer
> renders 1, 2, 3, 4, 5, 6, 7 (solid-node-viewer 0.1.0) …

The identity differs from the corpus's `2e172caa…` for ADR-062's finding F2
(`Clocked.described` opens with the class's MODULE PATH); every other field
of the two `clocked` objects and both tables are identical. Recorded in the
fixture's README, as the calculator's records the same finding. The fixture
is never replayed against corpus numbers.

`tests/test_regulator_document.py` — **5 tests, all passing**:

- the document declares version 8, carries `states`, carries
  `clocked.clock: "time"`, carries NO `program` and NO `controls`, declares
  no bound at all, and its pose expressions read the free name `time` and
  never `$t`;
- the page opens at `t = 0` with `count = 0`, the transport present and
  stopped, NO scrub, and the clock absent from the driver handles;
- PLAY for one wall second at ×1 advanced the clock to a real instant and
  the count followed the MACHINE'S OWN LAW rather than a number the test
  invented (`count == int(time + 0.5)`, a release every `T/2 = 1 s`);
- PAUSE held the bank for 300 ms more, value for value;
- a 2 s STEP advanced the clock by exactly 2.0 s and the count by exactly 2;
- RESET returned the bank to `{engaged: 1, count: 0, time: 0}`, stopped the
  transport, and returned the bob to the rest picture byte for byte;
- the bob's pixels DIFFER between `t = 0.25` (8.49°) and `t = 0.5` (12°, the
  swing's extreme), so the pose really follows the bank;
- a backwards request is refused by kind `ValueError` naming `time` and both
  instants, and the bank stands;
- a REFUSED FRAME pauses the transport and reports across the panel, once;
- a host with the chrome SUPPRESSED gets no panel and no transport pixels
  and still runs the clock from the handle.

Screenshots: `tests/_shots/clocked-regulator-rest.png` (t = 0, count 0) and
`tests/_shots/clocked-regulator-played.png` (t = 5.25 s, count 5, readout
`0:05.25`), both inspected — and inspected AGAIN after completion's two
chrome fixes (§11), which is what found them.

Two pixel claims were NOT made, and the reason is the machine's own
arithmetic rather than a weakness of the evidence:

- a single picture taken at the END of a played second may legitimately
  match the one at rest, because the bob's angle `12·sin(180·t)` returns to
  zero at every whole second. Three pictures taken WHILE it swings are the
  claim instead.
- a step of exactly 2 s is exactly one period, so the bob returns to the
  very angle it left. What a step moves is the CLOCK and the COUNT, asserted
  off the bank.

Also recorded: the renderer keeps no drawing buffer between frames, so a
canvas read from a TIMER returns a cleared canvas and every picture matches
every other. Every picture in this suite is taken inside a
`requestAnimationFrame` callback, after the widget's own loop has rendered
that frame. (Cycle 5's suite never met this because every one of its shots
followed a synchronous request.)

## 6. Publication

- `package.json`: `solidNodeViewerApi: 18`; `solidNodeDocumentVersions`
  UNCHANGED at `[1 … 8]`; `RELEASED_DOCUMENT_VERSIONS` left at `[1,2,3,4]`.
- `src/version.test.ts` updated with the reason; the six Python suites that
  assert the declared version moved with it (`test_bundle`,
  `test_widget_e2e`, and the four document acceptances).
- `npm run build` in THIS worktree's widget: `dist/solid-widget.js`
  781.2 kB; `bundle.describe()` reports `apiVersion: 18`,
  `documentVersions: [1..8]`. The PRIMARY checkout's bundle was NOT rebuilt.
- No `npm ci`, no `npm install`, no `scripts/check-dist`; the symlinked
  `node_modules` is intact.

## 7. What is asserted UNCHANGED (task 8.2)

`git diff --stat` over `src/run/`, `src/running-corpus.json`,
`solid_node_viewer/capture.py` and `solid_node_viewer/bundle.py` is
**EMPTY**: not one line of `run.ts`, `worker.ts`, `runtime.ts`, `jumps.ts`
or `edges.ts` changed, the running corpus is byte for byte the same file
(md5 `651a3b5750c49eecad4587438dc9a85a`), and the capture is untouched. The
whole Python suite — the capture's tests, the version 1–7 document
acceptances, the e2e pixels — is green.

## 8. The suites (task 8.3)

- `npx tsc --noEmit` — clean.
- `npx vitest run` — **45 files, 1167 tests, 31.8 s, all green** (from 44 /
  1139: one new file, `src/clocked/clock.test.ts`, and 28 new tests). At
  completion, with §11.1's test, **45 files, 1168 tests, 33.7 s**.
- `PYTHONPATH=$PWD .venv/bin/python -m pytest tests -q -p no:cacheprovider`
  — **173 passed, 18 subtests passed, 53 warnings, 132.6 s. NO SKIPS**: the
  bundle is built and Playwright with its Chromium is installed in the
  workspace venv, so neither `needs_bundle` nor `needs_playwright` skipped
  anything. The 53 warnings are pre-existing Pillow deprecations in
  `test_widget_e2e.py`.

## 9. Design questions

None. Nothing in the ratified design was contradicted or found
underspecified; no operation failed to agree with the producer.

Two places where a judgement was needed and the design's own words decided
it, recorded so a reviewer can check them:

1. **"Assert … that `clip` was never consulted for the clock" (task 2.4).**
   `machine.ts` calls `clip` once per compiled constraint for EVERY request,
   the clock's included, and `clip` answers `null` on its first line because
   `bound.plans.get('time')` is undefined. "Never consulted" is therefore
   asserted in the checkable form design §3 states: for both of `Lift`'s
   constraints, `plans.has(clock)` and `movesWith(bound, clock)` are false
   while `movesWith(bound, 'lift')` is true, and `clip` returns `null`
   without walking a piece of the path.
2. **A step amount a maker types.** The transport has no minus, and a
   negative or non-finite amount typed into the step field is refused as a
   SETTING (`clockStepAmount` leaves the amount where it was) rather than
   clamped as a REQUEST. Nothing a maker asks the MACHINE for is ever
   clamped; the field also carries `min="0"`.

## 10. Warts for the pilot (task 8.8)

1. **What an instruction MEANS under a clocked root** — ADR-128 §14 publishes
   the table and gives it no runtime meaning; the chrome lists each
   instruction DISABLED with the reason. Open in the framework, unchanged by
   this cycle. (Carried forward from ADR-062.)
2. **A CLIP in time, and a chain that follows the clock** — ADR-127's own
   recorded narrowing. This cycle mirrors the producer's refusal (a
   constraint may not name the clock) rather than anticipating the later
   cycle that would take it; that cycle's first task is settling ADR-126's
   contested direction test for a level PERIODIC in time. Producer-side.
3. **Two identities for one machine** (ADR-062 F2) — `Clocked.described`
   opens with the class's MODULE PATH, so the same class exported by `solid
   export <path>:Class` and by the corpus generator publishes two
   identities, and a snapshot taken against one is refused against the other.
   Reproduced exactly by this cycle's fixture; recorded in its README.
   Producer-side, nothing worked around here.
4. **A multi-input request** moving a driver and the clock together
   (ADR-125's narrowing) — not asked for by anything yet; recorded.
5. **`max_crossings` bounds a played frame, and the refusal cannot say what
   speed to drop to.** The refusal names the split and pauses, which is the
   design's decision (Open Question 2); computing the largest admissible
   speed would need the event RATE, which the machine does not publish. A
   maker's remedy is a lower speed. Recorded as a limit, not worked around.
   Producer-side if it is ever to change: the machine would have to publish
   something it does not.
6. **Consumer-side, this repository's, and this cycle FIXED it**: the panel
   readouts did not follow a bank moved through the handle (§2.7). Recorded
   because it was a live defect on the base, not because it is still open.

## 11. Completion, after the adversarial review (tasks 8.5, 8.6, 8.9)

The review re-ran `npx tsc --noEmit` (clean) and the clocked and
running-corpus suites (187 passed), inspected both `Regulator` screenshots
and ACCEPTED the cycle with no closure. The ratified 16 ms frame floor
(§4.4) and the kept `clockMoves` helper (§3) stand as reported. It raised
two chrome NITS, to fix only where each is small and covered by an existing
test pattern. Both were, and both were fixed RED FIRST.

### 11.1 An INTEGER state read `5.0000`

- **Red**, `src/clockedControls.test.ts`, a new case in the file's own
  shape (the `Regulator`'s: an int state beside a clock):

  ```
  × the clocked chrome > reads an INTEGER state as the whole number it is
    AssertionError: expected '5.0000' to be '5'
  ```

- **Fix**, four lines in `src/clockedControls.ts`: a readout's text comes
  from `readoutText`, which prints an `int` coordinate whose DESIGN value is
  whole as that whole number and otherwise falls through to `formatReadout`.
  The fixed four decimals are a CONTINUOUS quantity's policy — a readout
  that changes sixty times a second under a drag wants one constant shape —
  and a state the machine commits as an integer has no fraction to report.
  A SCALED int still reads as a float, because its design value is not
  whole; the CLOCK, which declares no dtype, keeps its decimals (asserted in
  the same test: `5.2500`). Only the READOUTS changed; a driver handle's
  editable field is untouched, because that field is a value a maker types
  into and `formatDisplay` already governs it.
- Visible in `tests/_shots/clocked-regulator-played.png` (`count 5`) and in
  `tests/_shots/clocked-calculator-stroked.png` (`halved 0`).

### 11.2 The overlap at the right edge was a SECOND PANEL

The review read the played screenshot as the `engaged` field overlapping a
`0…100` label. It is not a label: it is the POSED DRIVER CHROME standing
BEHIND the clocked panel. Both are anchored at the container's corner and
the clocked panel's background is translucent, so the posed panel's own
`engaged` readout (`1.0000`) showed through beside the nudge field. Read off
the mounted page rather than guessed — `host.innerHTML` carries
`<div class="driver-controls">` and `<div class="clocked-controls">`, both
`position: absolute; left: 0; top: 0`.

**It is ADR-062's defect, not this cycle's**, and it is not cosmetic: the
ghost panel offers a second control over the same input that writes the
driver through the POSE path, past the machine's bank. `rebuildDriverChrome`
already returns early for a document carrying a PROGRAM, for the same
reason, and did not for one carrying a clocked MACHINE.
`tests/_shots/clocked-calculator-stroked.png` on the base shows it too, with
five ghost rows.

- **Red**, in this cycle's own acceptance (`tests/test_regulator_document.py`,
  the `opened` reading, on `tests/test_capture.py:371`'s pattern of counting
  a selector's nodes):

  ```
  > self.assertEqual(opened['posed'], 0,
                     'a posed driver panel stands beside the clocked one')
  E AssertionError: 1 != 0 : a posed driver panel stands beside the clocked one
  ```

- **Fix**, four lines in `src/viewer.ts`: `rebuildDriverChrome` returns for a
  document carrying a clocked machine, exactly as it does for one carrying a
  program. `loadedMachine` is assigned by `startMachine` before
  `refreshControls` runs, so the guard sees it on the first build as well as
  on every rebuild.
- Both clocked acceptances green afterwards (9 tests), and both pairs of
  screenshots re-taken and re-inspected: the ghost is gone from the
  `Regulator`'s panel and from the `Calculator`'s.

Neither fix touches the machine, the solver, the corpus, the transport or
any published contract; both are the CHROME. The decision each states is
recorded in ADR-063 rather than left in a screenshot.

### 11.3 The record

- **ADR-063** — `docs/adrs/EXPORT/ADR-063-the-clock-is-an-input-and-a-frame-advances-it.md`,
  extracted after implementation from what was built, in ADR-062's house
  style: extends ADR-062, builds on ADR-045/046/047/048, consumes solid-node
  ADR-127 and ADR-128 §10. `docs/adrs/README.md` carries it after ADR-062.
- **README.md** — "Operating a clocked machine" gains the clock (the
  request, nothing stopping it, the backwards refusal, the transport, the
  cap, what a host drives, `$t` beside the clock); the two sentences saying
  a clocked document has NO transport are corrected to "no cadence over its
  drivers"; the version table's `0.2.0` row reads API **18**. Nothing is
  described as released.
- **CHANGELOG.md** — one entry under `0.2.0 — unreleased`, above cycle 5's.
- **workflow/warts.md** — a dated entry for this cycle, framed as cycle 5's
  is: recorded THERE rather than only here because neither finding belongs
  to a viewer cycle to fix. The clip in time / a chain following the clock
  (producer-side, ADR-127's own narrowing) and `max_crossings` bounding a
  played frame with no event rate to name a speed from (a limit of this
  cycle's ratified decision). The multi-input request is noted as recorded
  here and not opened there; cycle 5's identity, instruction-meaning and
  load-sensitivity entries are carried forward rather than restated.
- **The spec** — the delta is synced into
  `openspec/specs/viewer-package/spec.md`: eight MODIFIED requirements
  replaced whole (every surviving scenario carried; the two deliberately
  WITHDRAWN are the clock-request refusal, "A request on the clock is
  refused and the model stands", and the departure census, "A step this
  build does not perform is a stated departure") and two ADDED ones placed
  where they read — the clock request after "The viewer executes a clocked
  machine's requests", the transport after "A maker operates a clocked
  machine on screen". 45 requirements became 47. The merged file was read
  at both seams.

### 11.4 The final validation

Run once each, one process at a time, in this worktree:

- `openspec validate --all --strict` — **7 passed, 0 failed** (six specs and
  the unrelated `slide-and-turn-parts` change; this one is archived).
- `npx tsc --noEmit` — clean.
- `npx vitest run` — **45 files, 1168 tests, 32.7 s, all green**.
- `PYTHONPATH=$PWD .venv/bin/python -m pytest tests -q -p no:cacheprovider`
  — **173 passed, 18 subtests passed, 53 warnings, 138.1 s. NO SKIPS**; the
  53 warnings are the pre-existing Pillow deprecations in
  `test_widget_e2e.py`.
- `npm run build` in THIS worktree's widget — `dist/solid-widget.js`
  781.3 kB, `apiVersion: 18`, `documentVersions: [1..8]`. The PRIMARY
  checkout's bundle is NOT rebuilt; no `npm ci`, no `npm install`, no
  `scripts/check-dist`.

No commit is made here: two commits for the cycle and no more, and the
implementation commit is the orchestrator's.
