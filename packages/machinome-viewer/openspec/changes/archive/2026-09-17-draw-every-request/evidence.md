# Evidence: `draw-every-request`

Every red recorded before its fix, every number read off a run, in the
order the work happened. Worktree
`solid-node-viewer/WTs/clocked-machine`, branch `draw-every-request`,
base `ae9cb91` (the ratified planning commit over viewer main `77b97e1`,
ADR-064, API 19).

## 0. The base

`src/clocked-corpus.json` md5 `bc4174cf47f844b035125ed3afcee3aa`;
`solidNodeViewerApi` 19, `solidNodeDocumentVersions` `[1 … 8]`;
`dist/solid-widget.js` 804 744 B. `git status --short` clean.

## RED 1 — the chrome states no gesture duration (task 1.1)

`src/clockedControls.test.ts` gains "states how long a drawn GESTURE
takes: one short duration of the viewer's own, the same for every
travel". `npx vitest run src/clockedControls.test.ts`:

```
FAIL  src/clockedControls.test.ts > the clocked chrome > states how long a
      drawn GESTURE takes: one short duration of the viewer's own, the same
      for every travel
AssertionError: expected undefined to be 0.2 // Object.is equality
 ❯ src/clockedControls.test.ts:207:29
 Test Files  1 failed (1)
      Tests  1 failed | 20 passed (21)
```

The chrome exports `DEFAULT_NUDGE` (an amount) and `DEFAULT_CLOCK_STEP`
(seconds of the clock) and no duration for a gesture at all, because on
the base no gesture is drawn.

## RED 2 — a gesture on a handle poses ONCE (tasks 2.1, 4.1–4.3)

`viewer.ts` has no node-level harness in this package (nothing under
`src/*.test.ts` mounts it), so the wiring's red is a BROWSER one, as
task 2.1 says. `tests/test_calculator_document.py` gains
`GestureDrawnInABrowserTest` — the pilot's own gesture on the committed
version 8 calculator fixture: the nudge amount set to a whole turn, the
plus button pressed, sampled per animation frame.

```
$ pytest tests/test_calculator_document.py -k GestureDrawn
>       self.assertEqual(result['crankAtOnce'], 0)
E       AssertionError: 360 != 0
tests/test_calculator_document.py:1054: AssertionError
1 failed, 6 deselected in 7.36s
```

The very first read after the click already stands at the landing: one
request, one pose, no frame between — the teleport this cycle removes.

## RED 3 — the gesture that lands a drawing starts none of its own (task 4.4)

The committed acceptance's own section 4 (`+` on `feed` while the
`Stroke` drawing runs) now asserts BOTH the landing and the new drawing.

```
$ pytest tests/test_calculator_document.py -k InstructionDrawn
>       self.assertEqual(result['landedByGesture']['feed'], 0)
E       AssertionError: 1 != 0
tests/test_calculator_document.py:760: AssertionError
1 failed, 6 deselected in 11.00s
```

`feed` reads its landing on the frame of the gesture, where a drawn
request reads the transition's ORIGIN.

## GREEN, and what it cost (tasks 1.2, 2.2–2.3, 4.1–4.5)

`src/clockedControls.ts` states `GESTURE_SECONDS = 0.2` beside
`DEFAULT_NUDGE`, whose comment no longer says a clocked request is
instantaneous by construction. `src/viewer.ts` routes the panel's `move`
and `nudge` through `clockedRequest(id, request, GESTURE_SECONDS)`, which
now takes the bank BEFORE the request (only where one will be drawn) and
finishes through `startDrawing` in the order ADR-064 fixed — rebuild the
panel once, then frame 0 in the same task, then render. `clockedDrawing`
carries `name: string | null`, the indicator key, `null` for a handle's
gesture.

```
$ pytest tests/test_calculator_document.py
  Calculator stroke in the page: 0.90 / 0.70 / 0.80 ms
  calculator drawing: 118 frames over 2.02 s (58.5 fps), per-frame pose median 0.70 ms
  calculator gesture: 60 frames over 1.00 s (60.1 fps), per-frame pose median 0.50 ms,
                      worst 3.30 ms
  frozen mid-nudge at crank 119.88, landed at 360
7 passed in 20.67s
```

The nudge of a whole turn: the panel reads **0** on the gesture's own
frame while the machine already banks **360**; the reading rises
monotonically over the sampled frames through more than five distinct
values to 360; `machine.state()` is the SAME bank at every one of them;
the landing equals one `move('crank', {by: 360})` from the same start,
bank for bank; and the canvas at frame 3 differs from the canvas at the
end. The typed 720 draws the second stroke; the ranged whole-number
`operand` draws 1 → 9 with every frame a whole number never past the
end, the thumb following; the host handle lands at once.

## Mutation checks — the three claims that cannot go red before the change

Nothing draws on the base, so "the clock is not drawn" and "the host
handle is not drawn" have no red of their own. Each was proved by
MUTATING the implementation and watching the guard fail; every mutation
was reverted and the bundle rebuilt.

1. **A drawn STEP** (`step()` passing `GESTURE_SECONDS`):

```
>       self.assertTrue(result['steppedWhilePlaying']['playing'],
                        'a step stopped the transport that asked for it')
E       AssertionError: False is not true
```

2. **A drawn PLAYED FRAME** (`clockFrame` passing `GESTURE_SECONDS`):

```
>       self.assertGreater(seconds, 0.3, 'the clock did not run')
E       AssertionError: 0.06666666666666667 not greater than 0.3
```

The transport stops on its first drawn frame — ADR-064's one-authority
rule turning the transport off — which is design D4's reason, measured.

3. **A drawn HOST HANDLE** (`machine().move` starting a drawing):

```
>       self.assertEqual(result['hostAtOnce']['crank'], 360)
E       AssertionError: 0 != 360
```

## The Curta, where the finding came from (tasks 5.1, 5.2)

`tests/test_curta_drawing.py` gains `CurtaGestureTest` — skippable, a
MEASUREMENT and not a contract — served through the directory of
SYMLINKS the file already builds to `projects/Calculators/
Curta-Type-I-3x/_build/clocked_curta`, copying nothing into this
repository. The pilot's own gesture: the `crank_rotation` nudge amount
set to 360 and `+` pressed, then 720 typed into the field, then the
declared `'Turn crank'` for comparison, all in ONE session on one page.

```
mounted in 0.91 s; IDLE (no drawing): 12 frames over 5.54 s (2.2 fps),
  per-frame median 6.10 ms
the NUDGE of 360 deg (0.2 s):
  one solve 54.50 ms; the panel read 0 on the gesture's own frame, the bank 360
  1 frames over 1.22 s (0.8 fps), per-frame median 17.10 ms, 2 distinct poses
  readings: [0, 360]
the TYPED 720 (0.2 s):
  one solve 40.00 ms; the panel read 360 on the gesture's own frame, the bank 720
  1 frames over 1.37 s (0.7 fps), per-frame median 17.20 ms, 2 distinct poses
  readings: [360, 720]
the declared 'Turn crank' (2 s):
  one solve 42.40 ms; the panel read 720 on the gesture's own frame, the bank 1080
  6 frames over 3.43 s (1.7 fps), per-frame median 14.10 ms, 4 distinct poses
  readings: [720, 947.988, 1028.988, 1080, 1080, 1080, 1080]
  the POSE, by difference: nudge +11.00 ms, typed +11.10 ms,
  declared +8.00 ms a frame
```

**The answer to open question 1, in numbers.** The machinery is right on
the Curta — one request at the gesture (40–55 ms, the same solve
ADR-064 measured), the panel reading the transition's ORIGIN on the
gesture's own frame while the machine banks the end, and the pose
costing ~11 ms a frame, which is ADR-064's 9.20 ms within this bench's
noise. What a 0.2 s gesture CANNOT do on this host is be watched: the
page idles at **2.2 fps** — headless Chromium on `swiftshader` with
54 MB of meshes, the same 3 fps ADR-064 recorded — so a fifth of a
second gets ONE frame after its origin and lands in it. Two distinct
poses, and both are endpoints. The declared 2 s stroke, ten times
longer, draws four. **That frame rate measures the software rasteriser,
not this cycle** (the committed calculator acceptance draws 60 frames at
60.1 fps on the same host), and whether 0.2 s is watchable on the
pilot's own hardware is a question only the pilot's own hardware can
answer. The constant is one number in one file.

**The pictures.** Two screenshots of the Curta's own nudge, outside this
repository (a measurement is not a contract):
`scratchpad/viewer-acceptance/curta-nudge-drawing.png` — the panel
reading `crank_rotation` **180** with the amount box at 360 and the
outcome `moved 360 deg`, the model's crank part-way round, while the
machine banks 360 — and `curta-nudge-landed.png`, the same gesture at
**360**. The drawing one is taken with the loop's frames handed a 50 ms
stride, because at 2.2 fps no mid-travel frame exists to photograph; the
stride changes nothing in the viewer, which advances a drawing on the
elapsed seconds the loop reports, whatever reports them.

## Two findings, neither worked around (task 6.1, `workflow/warts.md`)

1. **The nudge AMOUNT reaches the row's buttons only at the next rebuild
   of the panel.** `setNudge` writes `clockedNudge[id]` and rebuilds
   nothing, while the `±` buttons carry the amount their row was BUILT
   with (`viewer.ts:3446-3455`), so the pilot's own sequence — type 360,
   press `+` — moves **1 deg** the first time and 360 after. Measured:
   `the first press after setting the amount moved to 1 (moved 1 deg)`.
   Pre-existing, ADR-062's; the running chrome keeps its amount in a
   live closure instead. Both new harnesses ARM the amount with a reset
   rather than hiding it.
2. **A value committed with the field still focused loses the element it
   was typed into.** Every request rebuilds the whole clocked panel, so
   the focused `<input>` is removed and replaced; the design's open item
   3 ("a typed value committed with Enter keeps focus, so its own field
   does not follow the drawing") is WRONG. Measured: after the commit
   `document.activeElement` is the body and the new field reads `30.06`,
   a drawn intermediate. The requirement's clause is still met and still
   reachable — a maker whose cursor is in a field WHILE a drawing runs
   keeps what they typed, pinned by the acceptance's section 5 (`42`
   survives twelve frames while the machine draws a whole turn) — but it
   protects the field a maker moves INTO, not the one they committed
   from.

## The pointer, not just the event (task 4.3)

The slider commit is also driven by the BROWSER'S OWN MOUSE: a recorder
samples `operand`'s reading once per animation frame, the harness clicks
the slider's track at 95 % of its width with `page.mouse.click`, and the
reading rises from **1** — where the input stood — through whole numbers
to the bank that click made, more than two distinct poses on the way,
with the last reading equal to the bank. A real pointer on the track is
one request and it is drawn, exactly as the dispatched `change` is.

## Closing suites (task 6.4)

- `npx tsc --noEmit` — clean.
- `npx vitest run` — **46 files, 1219 tests, 35.27 s, green** (from 46 /
  1218: the chrome's gesture-duration test).
- `pytest tests` from the worktree root on the workspace venv —
  **178 passed, 18 subtests, 53 warnings, 242.59 s, no skips** (from 176
  / 18): this host carries the Curta's builds, so both measurements ran
  rather than skipping.
- `npm run build` — `dist/solid-widget.js` **804 744 B → 804 870 B**.
- `src/clocked-corpus.json` md5 `bc4174cf47f844b035125ed3afcee3aa`,
  unchanged; `git diff --stat` over `src/clocked/drawing.ts`,
  `src/clocked/machine.ts`, the corpus, `src/run/`, `src/drivers.ts` and
  `src/runControls.ts` EMPTY; `solidNodeViewerApi` 19 and
  `solidNodeDocumentVersions` `[1 … 8]` untouched.
- `openspec validate draw-every-request --strict` → valid, before the
  archive; `openspec validate --all --strict` after it.
