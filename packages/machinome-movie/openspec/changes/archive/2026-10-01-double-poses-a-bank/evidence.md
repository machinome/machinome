# Implementation evidence

## Authority and scope

Cycle 7 of Videomaker's addition-warts campaign, wart 10 of "Addition
(Curta, 1 October 2026)", on branch `double-poses-a-bank` (worktree
`WTs/double-poses-a-bank`), cut from `addition-warts` at `500ebca`, which
holds `exact-take-times` (`bankAt(doc, seconds)`, `stepEnds(doc)`, exact
marks), `honest-provenance`, `serve-what-the-viewer-reads` and the
`render-cost` investigation. The planning commit is `fdb4c17`. Nothing was
pushed or published; no network or paid request was made; nothing was
installed. Nothing under `src/`, `stage/`, `python/`, `schema/` or
`fixtures/` (but its README) changed. The viewer was reached only through
the bundle selected by path
(`machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js`, API
29), never written into the repository. Integration into `addition-warts`
is the orchestrator's.

Environment: Linux, Node v24, vitest 5.0.3, Playwright's Chromium, Python
3.12 from the workspace venv. Other campaign agents may have run suites in
other worktrees at the same time; durations are not comparable.

## The probe behind design D2

Before the design was written, a throwaway test (deleted, never committed)
posed `count` on the selected bundle with labels on `handle`,
`units_drum`, `tens_drum` and `base` and read their rectangles; the table
is in `design.md`. It showed that the crank stands at whole turns at every
mark (the handle is drawn alike at all of them), that the units drum's
rectangle changes between units 0 and 1, and that mark `nine` opens the
`split`, where the view has another box.

## Red

### Layer 5, the double unchanged

The helper `test/support/mark-on-a-take.mjs` and its call in
`test/browser/take.test.mjs`, run cold
(`VIDEOMAKER_TEST_COLD=1 npx vitest run --project slow
test/browser/take.test.mjs -t "ring on the units drum"`):

     × a ring on the units drum follows it from the take's start to the mark one, and back (the assertion layer 6 makes) 1102ms
     FAIL  |slow| test/browser/take.test.mjs > a ring on the units drum follows it from the take's start to the mark one, and back (the assertion layer 6 makes)
    AssertionError: the ring on units_drum moves with the bank: at the take's start rect {"x":224,"y":126.80000000000001,"width":24,"height":20}, anchor {"x":236,"y":136.8}, at the mark one rect {"x":224,"y":126.80000000000001,"width":24,"height":20}, anchor {"x":236,"y":136.8}
          Tests  1 failed | 5 skipped (6)
    Test memo: 0 passed from the memo, 1 run

The wart, reproduced: the ring stands at one place at both banks.

### The refusal of a machine that follows nothing, on the old double

With the double's change stashed (`git stash push -- test/viewer-double.mjs`)
and the new tests run cold:

     FAIL  |slow| test/browser/take.test.mjs > a double whose machine follows no input, or one its bank does not hold, is refused at mount, naming it
    AssertionError: Missing expected rejection.

and the mark test failed as above (2 failed). The stash was popped.

### Layer 6 before the double changed

The same assertion with the selected bundle, cold, before the double was
touched: green, since the real viewer moves the drum.

     ✓ |viewer| test/viewer/take.test.mjs (6 tests | 5 skipped) 1581ms
       ✓ a ring on the units drum follows it from the take's start to the mark one, and back (the assertion layer 5 makes) 1571ms
    Test memo: 0 passed from the memo, 1 run

## Green

With `machine.follows` (design D1), the fixture's machine following
`units` over `[0, 9]`, cold:

     ✓ |slow| test/browser/take.test.mjs (7 tests) 4569ms
       ✓ every view on the take is restored to its frame's bank, never given a loop time, and reports the bank it holds 1045ms
       ✓ posing one bank, then another, then the first gives identical pixels; a mark poses its recorded bank 645ms
       ✓ a ring on the units drum follows it from the take's start to the mark one, and back (the assertion layer 6 makes) 674ms
       ✓ a double whose machine follows no input, or one its bank does not hold, is refused at mount, naming it 404ms
       ✓ a viewer below API 29, without a machine, or with another machine is refused at mount, naming the view 502ms
       ✓ a viewer that answers a step otherwise than the take is refused before the first frame, naming the step and the field 553ms
       ✓ a view whose bank differs from the frame's is refused naming the view, the time and the id; at a mark, naming the mark 725ms
          Tests  7 passed (7)
    Test memo: 0 passed from the memo, 7 run

### A control: a stage that keeps marks between frames

To see the proof catch a stage fault and not only the double's, the stage
(`stage/runtime.tsx`, the `drawMarks` call) was edited for one run to reuse
a view's mark reports from its previous frame when its marks were
unchanged, the shape of a cache carried between frames. The layer 5 test,
cold:

     FAIL  |slow| test/browser/take.test.mjs > a ring on the units drum follows it from the take's start to the mark one, and back (the assertion layer 6 makes)
    AssertionError: the ring on units_drum moves with the bank: at the take's start rect {"x":224,"y":126.80000000000001,"width":24,"height":20}, anchor {"x":236,"y":136.8}, at the mark one rect {"x":224,"y":126.80000000000001,"width":24,"height":20}, anchor {"x":236,"y":136.8}

The edit was reverted with `git checkout -- stage/runtime.tsx`; the stage
is unchanged by this change.

## The suites on the final content

Node, the whole suite, cold, with `VIDEOMAKER_VIEWER_BUNDLE` naming the
API 29 bundle (the viewer project ran: `real-viewer.test.mjs` 7 tests,
`take.test.mjs` 6 tests), before the archive moved the records:

     ✓ |viewer| test/viewer/real-viewer.test.mjs (7 tests) 148960ms
     ✓ |viewer| test/viewer/take.test.mjs (6 tests) 22776ms
     Test Files  40 passed (40)
          Tests  390 passed (390)
       Duration  885.58s (tests 98%, import 1%)
    Test memo: 0 passed from the memo, 390 run

Python (`python -m pytest -q` in `python/`):

    286 passed in 17.93s

After the archive, the ticked tasks and this file (before the last edit of
this paragraph), `openspec validate --specs --strict` (16 passed) and the
same Node command without `--cold`, with the bundle:

     Test Files  40 passed (40)
          Tests  390 passed (390)
       Duration  915.04s (tests 98%, import 1%, transform 1%)
    Test memo: 0 passed from the memo, 390 run

Every test ran again, since a cold run writes no memo (finding 5); this
run's slow passes are now in the shared store for this content.

## Findings

1. **No layer posed a mark on a take before this change.** The wart says a
   mark on a clocked take "is proved only at layer 6"; the viewer layer had
   no such test either (`test/viewer/take.test.mjs` posed no mark, and the
   fixture `count` draws none). Both layers now make one assertion.
2. **The counter's marks are whole turns of the crank**, so the real viewer
   draws the handle alike at every mark, and `count`'s only marks in one
   box are the take's start and `one`: mark `nine` opens the `split`. A
   film that wants to prove a mark between two marks of its own take must
   pick a part the bank moves and two marks in one box.
3. **The real viewer's part rectangle of a turned drum changes size more
   than place**: the units drum is 90.7 px wide at units 0 and 126.4 px at
   units 1 (36°), its centre moving about 2 px, which reads as a bounding
   box of the turned part rather than its silhouette. A ring is the mark
   that shows it; a label or an arrow on a round drum barely moves. The
   viewer's; recorded, not filed there.
4. **The control mutated one fault, not every one.** A stage that kept
   marks between frames is shown red above; one that read a part's
   rectangle before restoring the bank is argued red in design D4 (the
   mark at `one` would carry the start's rectangle) but was not mutated,
   since the stage poses every view before it draws any mark and the edit
   would have reordered `setFrame`'s phases.
5. **A warm run after the cold one ran every test**, as the memo's rules
   say it must: the cold switch ignores the memo entirely, so the cold run
   recorded no pass, and the warm run, the first to write the store for
   this content, ran all 390. Not a defect; it makes the warm run a second
   fresh run of the final content.

## What was not done, and why

- No mark cue in the shared fixture document `count` (design D3): the
  override proves the browser seam without changing what both runtimes
  emit and pin.
- No ADR: ADR-018 is released (design D4). ADR-008 is unchanged, since the
  real-viewer layer's gate and scope stay.
- The double models one input on one axis; it does not model which part an
  input turns, nor size changes like the real viewer's drum (finding 3).
- `docs/architecture-overview.md` and the manual are unchanged: no
  structure they describe moved, and no reader-facing contract changed.
- The Curta film was neither run nor rendered: it draws no ring, label or
  arrow, and nothing it reads changed.
- Task 0.3, the orchestrator's review of the planning commit, is not
  claimed.
