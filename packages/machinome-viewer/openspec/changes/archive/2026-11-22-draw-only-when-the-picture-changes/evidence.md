# Evidence: draw-only-when-the-picture-changes

Written by the applying agent on 22 November 2026, in the bench
`machinome/WTs/draw-only-when-the-picture-changes` (branch
`draw-only-when-the-picture-changes`, planning commit `79e52106` above the
base `56de33dd`). Tasks 1.2 to 6.2, 7.1 and 8.1. Task 7.2 (the Enigma page)
and 8.2 (the decision record) are the reviewer's and are not recorded here.

## 1.2 The bench

The worktree was clean, `79e52106` exactly one commit above `56de33dd`
(`git diff --stat 56de33dd HEAD` touches only the change directory,
`workflow/warts.md` and the evidence file), and
`openspec validate draw-only-when-the-picture-changes --strict` answered
"Change 'draw-only-when-the-picture-changes' is valid".

## 2.3 Red on the base, by count

Both new widget files were run on the base source (the worktree's `src/`
before any source change). The bench's file was run a second time on the
base, after G1's own bookkeeping was corrected (see "Deviations"), by
putting the base's `viewer.ts`, `tree.ts`, `presentation.ts` and
`drivers.ts` back from `HEAD` and removing `picture.ts`, then restoring the
implementation, confirmed byte-equal by SHA256. That second run is the one
below; the first gave the same 44 failures and 17 passes.

`src/draw-on-change.test.ts` on the base: 61 tests, 44 failed, 17 passed.
Passing on the base, as the design says: D0; S0 (twelve kinds); W1 (three);
O1. Every other test fails on its count, and nothing fails on a setup,
import or fixture error. The parts of S9 that count draws inside each call,
the first frame of S11 (held start: drawn once, D matches) and the per-frame
counts of M1 to M6 hold on the base; those tests fail at their ten-frame
tails. G1: 200 of 200 sequences failed, every one at its idle tail; D matched
after every frame of every sequence.

Failing output (passes omitted):

```
G1: 200 of 200 sequences failed, 200 of them at the idle tail
× I1: a still page draws and updates nothing > a hand-written version 2 document: thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > regulator (clocked, clock paused): thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > touched (running, run paused): thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: +0 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > state-color/posed (a colour choice): thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > spinner (timeline, autoplay false): thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > a posed document with drivers and an instruction: thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > a flexible part: thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > markings: thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > the whole posed document: thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > marked (fixture): thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > calculator (clocked fixture): thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I1: a still page draws and updates nothing > a hand-written clocked document with drawn instructions: thirty still frames draw nothing and update nothing
  → expected { draws: 30, updates: 30 } to deeply equal { draws: +0, updates: +0 }
× I2: a zero-sized container is still too > thirty frames of a container with no size draw nothing
  → expected 30 to be +0 // Object.is equality
× S1 to S8: each source of a changed picture is drawn within one frame, and not after > S1: a wheel event on the canvas
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S1 to S8: each source of a changed picture is drawn within one frame, and not after > S2: a pointer drag on the canvas turns the model
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S1 to S8: each source of a changed picture is drawn within one frame, and not after > S3: a resize is drawn inside the observer's callback, then nothing
  → draws inside the observer's callback: expected +0 to be 1 // Object.is equality
× S1 to S8: each source of a changed picture is drawn within one frame, and not after > S4: a hover on a touchable part, and its end by moving away
  → expected { draws: 10, updates: +0 } to deeply equal { draws: +0, updates: +0 }
× S1 to S8: each source of a changed picture is drawn within one frame, and not after > S5: a hover ended by the window's blur
  → expected { draws: 10, updates: +0 } to deeply equal { draws: +0, updates: +0 }
× S1 to S8: each source of a changed picture is drawn within one frame, and not after > S6: reload() shows the new tree
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S1 to S8: each source of a changed picture is drawn within one frame, and not after > S7: a restored graphics context draws the next frame
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S1 to S8: each source of a changed picture is drawn within one frame, and not after > S8: a page shown again draws the next frame
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > setView
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > setView with a new up
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > setDriver
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > setTime
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > setVisible off
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > setRoot
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > highlight
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > artifactChanged
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > manifestChanged
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > machine().move
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > machine().restore
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > machine().reset
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > highlight's put-back
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S9: every call that draws still draws before it returns, and nothing after > setVisible on again, and setRoot back
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× S10: two changes before one frame cost one draw > a wheel event and a hover before one frame: one draw, showing both
  → expected { draws: 10, updates: +0 } to deeply equal { draws: +0, updates: +0 }
× S11: a republish applied while its new program starts is drawn by the next frame > the frame between the application and the call's own draw is drawn, and nothing after
  → expected { draws: 10, updates: +0 } to deeply equal { draws: +0, updates: +0 }
× M1 to M6: while something moves every frame draws and updates as on the base, and nothing after > M1: a ramp of an integer driver slow enough that some frames move no value
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× M1 to M6: while something moves every frame draws and updates as on the base, and nothing after > M2: the timeline played on spinner, and paused
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× M1 to M6: while something moves every frame draws and updates as on the base, and nothing after > M3: the clock played on regulator, and paused
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× M1 to M6: while something moves every frame draws and updates as on the base, and nothing after > M4: a drawn press of an instruction on an integer input
  → expected { draws: 10, updates: 10 } to deeply equal { draws: +0, updates: +0 }
× M1 to M6: while something moves every frame draws and updates as on the base, and nothing after > M5: a run started on touched, and paused
  → expected { draws: 10, updates: +0 } to deeply equal { draws: +0, updates: +0 }
× M1 to M6: while something moves every frame draws and updates as on the base, and nothing after > M6: a press held on a part of touched without moving, and let go
  → expected { draws: 10, updates: +0 } to deeply equal { draws: +0, updates: +0 }
× G1: generated sequences of host and maker actions > 200 seeded sequences of 30 steps: D matches after every frame, and twenty still frames after each draw and update nothing
  → AssertionError: seed 1 (regulator.json), idle tail after artifactChanged, setVisible, reload, highlight, resize, setVisible, visibilitychange, highlight, highlight, setView, clock played, machine().reset, reload, clock paused, resize, reload, machine().reset, setVisible, manifestChanged, webglcontextrestored, reload, highlight, resize, wheel, wheel, machine().reset, machine().reset, setTime, clock played, setView: expected { draws: 20, updates: 20 } to deeply equal { draws: +0, updates: +0 }
⎯⎯⎯⎯⎯⎯ Failed Tests 44 ⎯⎯⎯⎯⎯⎯⎯
 Test Files  1 failed (1)
   Tests  44 failed | 17 passed (61)
```

`src/picture-revision.test.ts` on the base: 20 tests, 20 failed: 16 at
"Cannot read properties of undefined (reading 'value')" (the absent
`presentation.picture`) and 4 at "Cannot find module './picture'" (U7 and
the U6 case that builds a holder on a given revision). This is the expected
red.

Counts per test on the base and on the implementation:

| Test | Base | Implementation |
|---|---|---|
| I1, eleven kinds but `touched` | 30 draws, 30 updates | 0, 0 |
| I1, `touched` | 30 draws, 0 updates | 0, 0 |
| I2 | 30 draws | 0 |
| S0 (12 kinds) | 1 draw, D matches | 1 draw, D matches |
| S1, S2, S6, S7, S8 tails | 10 draws, 10 updates | 0, 0 |
| S3 inside the callback | 0 draws | 1 draw, D matches; tail 0 |
| S4, S5, S10, S11 tails (`touched`) | 10 draws, 0 updates | 0, 0 |
| S9 (14 calls), inside each call | > 0 draws, D matches | the same |
| S9 tails | 10 draws, 10 updates | 0, 0 |
| S11, frame while the start is held | 1 draw, D matches | 1 draw, D matches |
| M1 to M6 per frame | the constants below | the same constants |
| M1 to M4 tails | 10 draws, 10 updates | 0, 0 |
| M5, M6 tails | 10 draws, 0 updates | 0, 0 |
| G1 | 200 of 200 sequences red at the idle tail, D always matched | 0 of 200 red |

## Constants recorded on the base

W1, O1 and M1 to M6 were printed on the base before any source change, by
`expectRecorded`, and written into `RECORDED` in
`src/draw-on-change.test.ts` as printed. They were not regenerated. The
implementation printed the same lines (the sorted `RECORDED` lines of the
base run and of the implementation's run have the same MD5,
`2fe74d6d037e047fd7e25c6a3815733c`), and every one of these tests passes on
it. The raw lines, from the base:

```
RECORDED M1 [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1]]
RECORDED M2 [[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2]]
RECORDED M3 [[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1],[3,1]]
RECORDED M4 [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,1]]
RECORDED M5 [[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1],[2,1]]
RECORDED M6 [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
RECORDED O1 [["setTime",1],["setView",1],["setDriver",1],["setDriver (colour)",1],["setVisible off",1],["setVisible on",1],["highlight",1],["put-back",1],["observer",0],["webglcontextrestored",0],["visibilitychange",0],["machine().move",1],["machine().move again",1],["machine().restore",1],["machine().reset",1],["setTime",1],["observer",0]]
RECORDED W1.clock {"first":0.016,"second":0.036000000000000004}
RECORDED W1.press {"landedOnFrame":14,"originFrames":13}
RECORDED W1.ramp {"landedOnFrame":32,"elapsedMs":512,"value":5}
```

Read: W1.clock is the clock's value after its first played frame of 16 ms
(0.016 s) and after a second frame of 20 ms, after sixty still frames;
W1.press is a 0.2 s drawn press on an integer input after sixty still
frames: it stands at its origin for 13 frames, the first included, and
lands on frame 14 (13 × 16 ms = 0.208 s ≥ 0.2); W1.ramp is a 0.5 s ramp
triggered after sixty still frames, landing on frame 32 (512 ms) at 5.
M1 to M6 are `[draws, updates whose change set names something]` per
frame, the frame the motion ends in included (M6: ten frames held, then
the frame after the press is let go by `pointercancel`). O1 is
`[call, draws inside it]` for an on-demand mount.

## 2.4 The browser tests on the base bundle

Base bundle: `npm run build` on the base source, SHA256
`878801de6adcd3c4c273f779d72672dcaf99140e86f6fb5cbf0a2f4b32cc6f7b`, kept
as a copy under the widget's `.scratch/` while the work ran (deleted before
stopping).

`tests/test_regulator_document.py`, with `shot()` restated, on the base
bundle: 5 passed. Every assertion held, `stepped_period`, `reset_to_rest`
and `two_instants_differ` included.

`tests/test_draw_on_change.py` on the base bundle: 5 failed, as designed:
B1 red on its counts (marked 150, regulator 30, touched 1,350 draw calls
over thirty still frames); B2's picture comparisons all passed on both
documents (every step's canvas equal to the canvas after a forced redraw,
and different from the previous step's wherever the step changes what is
seen) and B2 failed on its ten-frame counts; B3 red (the read after the
width change was the blank canvas); B4's landing passed (122 frames from
the click to the landing, 6 draw calls on every one) and its thirty frames
after made 180 draw calls.

```
  B1 draw calls over thirty still frames: {'marked/manifest.json': 150, 'regulator/viewer.json': 30, 'touched/viewer.json': 1350}
F  B2 {'step': 'machine().move', 'draws': 10, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'machine().restore', 'draws': 10, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'machine().move again', 'draws': 10, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'machine().reset', 'draws': 10, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'the clock played for half a second and paused', 'draws': 10, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'a wheel step', 'draws': 10, 'current': True, 'changed': True, 'changes': True}
F  B2 {'step': 'a mouse drag turns the model', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'a wheel step', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'setView', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'setRoot', 'draws': 150, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'setRoot back', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'setVisible off', 'draws': 300, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'setVisible on', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'highlight kept', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'its put-back', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'highlight dimmed', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'its put-back', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'highlight ghosted', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'its put-back', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'a hover on a dial', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'the pointer moved away', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'the host narrowed', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'the host restored', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'reload()', 'draws': 450, 'current': True, 'changed': False, 'changes': False}
  B2 {'step': 'the context lost and restored', 'draws': 450, 'current': True, 'changed': False, 'changes': False}
  B2 {'step': 'run().step(240) after a trigger', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'full screen', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B2 {'step': 'full screen left', 'draws': 450, 'current': True, 'changed': True, 'changes': True}
  B3 reads inside the resize observer: [{'width': 800, 'blank': False, 'current': True}, {'width': 640, 'blank': True, 'current': False}]
  B4 frames from the click to the landing: 122, draw calls per frame 6 to 6; after the landing, thirty frames: 180
        print(f'\n  B1 draw calls over thirty still frames: {counts}')
E       AssertionError: {'mar[15 chars]on': 150, 'regulator/viewer.json': 30, 'touche[16 chars]1350} != {'mar[15 chars]on': 0, 'regulator/viewer.json': 0, 'touched/viewer.json': 0}
E   AssertionError: {'machine().move': 10, 'machine().restore'[124 chars]: 10} != {}
E   AssertionError: {'a mouse drag turns the model': 450, 'a w[453 chars] 450} != {}
        print(f'\n  B3 reads inside the resize observer: {result}')
E       AssertionError: Lists differ: [False, True] != [False, False]
        print(f"\n  B4 frames from the click to the landing: {len(frames)}, "
E       AssertionError: 180 != 0 : frames after the landing made draw calls
============================== 5 failed in 25.23s ==============================
```

## A stated fact about the base that is false in headless Chromium

Design Decision 2, point 6, and Decision 3 say `renderer.setSize` clears
the canvas even at an equal size, so that on the base the observer's first
observation after a mount clears the canvas after the loop's first draw and
that frame is painted cleared. In the suite's headless Chromium
(SwiftShader) that is not so for a WebGL canvas. Measured on the base
bundle (a scratch script, not a test): after a draw, `canvas.width =
canvas.width` left the drawing buffer as it was (`toDataURL()` not blank),
while a real change of width and back cleared it; and a second resize
observer made after the mount read a drawn, not a blank, canvas at the
mount's first observation (800 px, the size set at mount). So on the base
only a resize that changes the size leaves its frame cleared, in Chromium.

B3 therefore fails on the base by its second read only (the width change);
its first read is not blank on the base. The test asserts what the design
states for both reads, and both hold on the implementation. This does not
change what the change promises: the delta requires a resize to be drawn
in its own frame, which the implementation does for every observation,
equal size or not, and a draw where none was needed costs one draw. What it
changes is a sentence of the proposal and of design Decision 3: "the first
frame after a mount among them" is not, in headless Chromium, a frame that
was painted cleared on the base. Other browsers were not examined.

## 5.1 Existing tests, run singly on the implementation, unmodified

All green: `presentation` 18, `shared-materials` 25, `tree` 71, `color`
22, `flexible` 32, `flexible-rebuild` 18, `drivers` 28, `playback` 20,
`partSurface` 36, `inspector` 22, `navigator` 26, `flat-pass` 41,
`flat-pass-parity` 52, `expression-lifetime` 11, `expression-reuse` 9,
`document` 65.

## 5.2 Mutations

Each was applied to the implementation by a scratch script, its named test
files were run, the output kept, and `viewer.ts`, `tree.ts`,
`presentation.ts`, `drivers.ts` and `picture.ts` were written back and
confirmed byte-equal by SHA256 before the next. The bench's file
(`draw-on-change`) was run for every mutation, the units' file
(`picture-revision`) for MU2, MU10 and MU12.

| Mutation | What turned red |
|---|---|
| MU1 the camera left out of `changed()` | S1, S2 (and S10, G1) |
| MU2 the holder's raise removed | S4, S5, U6 (two cases) (and M6, G1) |
| MU3 the tree's identity left out | **nothing** (see below) |
| MU4 the observer's callback draws nothing | S3 |
| MU5 the restore listener removed | S7 |
| MU6 the visibility listener removed | S8 |
| MU7 the empty update not skipped | I1 (updates: 30, draws 0), eleven kinds; and S1 to S3, S6 to S8, S9, M1 to M4, G1 at their tails |
| MU8 both of the loop's draws unconditional | I1 (draws: 30), twelve kinds; I2; S1 to S8, S9, S10, S11, M1 to M6 at their tails; G1 |
| MU9 `playing` removed from `moving()` | nothing: equivalent, as the design says (every playing frame writes a `$t`-reading node, which raises the revision) |
| MU9 `drivers.ramping()` removed | M1 |
| MU9 `clockPlaying` removed | M3 |
| MU9 `clockedDrawing !== null` removed | M4 |
| MU9 `runtime.running()` removed | M5 |
| MU9 `partSurface.engaged()` removed | M6 |
| MU10 `update`'s raises removed (both sites) | U1 (four cases); no mount-level test, as the design says |
| MU10 `applyVisibility`'s raise removed | U3; no mount-level test, as the design says |
| MU10 `artifactChanged`'s raise removed | U4; no mount-level test, as the design says |
| MU10 `reconcile`'s raise removed | **nothing** (see below) |
| MU11 `drawn` initialised to a reading at mount | S0, all twelve kinds |
| MU12 `Object.is` replaced by `===` in `sameReading` | I2, U7 (two cases), G1 |
| MU13 the explicit draw in `setVisible` removed | S9 (`setVisible off`; `setVisible on again, and setRoot back`), O1 |
| MU-W 1: the camera left out, bundle rebuilt | B2's orbit step (`a mouse drag turns the model`) and both wheel steps: the canvas was not the current picture (bundle SHA256 `fcd53d51…37edfb7`) |
| MU-W 2: the observer's draw removed, bundle rebuilt | B3: the read after the width change was blank (bundle SHA256 `2312252d…07ccc5`) |

After MU-W the source was restored, confirmed byte-equal, and the bundle
built again (`d1b7b0af…c780f`, the implementation's).

**MU3 turned nothing red**, where the design says S6 should. The reason is
in the implementation's own counters: `reload()` builds the new tree with
the mount's holder and calls `next.update(scope())`, a change set of
`'all'` that reaches every node, so the revision is raised by the tree's
own writer before the new tree is shown, and the next frame draws whether
or not the tree's identity is compared. The identity comparison is
therefore redundant on every path the bench and G1 reach (a mount's first
frame also draws because `drawn` is null). It is kept, as the design
writes it; it guards a tree shown without an update, which no path makes
today.

**MU10's `reconcile` raise turned nothing red**, where the design says U5
and S11 should. `WidgetTree.reconcile` calls `this.update(scope)` right
after `apply()` when it is given a candidate scope, in the same
synchronous block, and that update's change set is `'all'`, so it raises
the revision; `manifestChanged` always passes a candidate scope, and U5's
first case passes one too. The application's own raise is therefore
redundant on every path the viewer takes. The raise is kept, as the design
writes it. U5 was not changed to make the mutation bite (a case of
`reconcile` with no candidate scope would); that is the reviewer's to
decide.

The other mutations turned red exactly the tests the design names, and for
MU10's update, `applyVisibility` and `artifactChanged` raises no
mount-level test turned red, as the design predicts.

## 5.3 Searches

`renderer.render(` occurs once in `src/viewer.ts`, at line 629, inside the
one draw function (`drawPicture`, see "Deviations"). `setSize(` occurs once,
at line 2077, inside `resize`.

## 6.1 The widget suite and the typecheck

`vitest run` (the whole suite, once): 74 files, 73 passed, 1 skipped;
1,997 tests, 1,995 passed, 2 skipped, 0 failed. The two skips are
`src/run/profile-installed-benchmark.test.ts` ("reports one pinned
installed Curta v13 integration attempt", `skipIf(!path)`) and one case of
`src/run/profile-contact.test.ts` (`skipIf(!actualCurtaDocument)`): both
need a Curta project export that is not on this bench. No wall-clock gate
failed in this run.

`tsc --noEmit`: exit 0, no output.

## 6.2 The implementation's bundle and the Python suite

`npm run build`: `dist/machinome-viewer.js`, SHA256
`d1b7b0af54e27ac5ddb48be8f2a96114269ff0ed8a9141a96b6bb17ab84c780f`.

The viewer's Python suite on the bench's venv (`python -m pytest tests -rs`,
once, after the build): 290 passed, 2 skipped, 0 failed, in 305 s. The two
skips are `tests/test_curta_drawing.py:375` and `:469`: "the Curta's own
builds are not at .../WTs/projects/Calculators/Curta-Type-I-3x/_build" (a
project export, not on this bench). No browser test was skipped for a
missing Chromium or Playwright. The bundle's SHA256 was the same before and
after the run (the currency check did not rebuild it).

`tests/test_draw_on_change.py` and the restated
`tests/test_regulator_document.py`, run again alone with their prints on the
implementation's bundle: 10 passed.

```
  B1 draw calls over thirty still frames: {'marked/manifest.json': 0, 'regulator/viewer.json': 0, 'touched/viewer.json': 0}
  B2: every step of both documents 'draws': 0 and 'current': True; 'changed': True wherever the step changes what is seen
      (reload() and the context lost and restored: 'changed': False, as on the base, where they change nothing seen)
  B3 reads inside the resize observer: [{'width': 800, 'blank': False, 'current': True}, {'width': 640, 'blank': False, 'current': True}]
  B4 frames from the click to the landing: 122, draw calls per frame 6 to 6; after the landing, thirty frames: 0
```

The unrestated `test_regulator_document.py` (its text at `HEAD`, run from a
scratch copy, deleted) on the implementation's bundle fails, as design
Decision 10 says it would: "AssertionError: False is not true : the bob
stands in the same place at two instants" (`two_instants_differ`), its
`shot()` reading a cleared buffer in an animation frame in which nothing
changed.

## Existing tests changed

One, as design Decision 10 says: `tests/test_regulator_document.py`, whose
`shot()` read the canvas in an animation-frame callback registered after
the viewer's loop. It now calls `viewer.setTime(0)` and reads
`toDataURL()` in the same task, every shot alike; its comment is restated
to say why; every assertion is kept, and nothing else in the file changed.
It passes on the base bundle and on the implementation's. No other
existing test, vitest or Python, was changed, and every existing test the
design says holds as written held (the whole widget suite and the whole
Python suite are green on the implementation).

## Deviations from the design, and decisions it left open

- **The one draw is named `drawPicture()`, not `draw()`.** `clockedRequest`
  has a parameter named `draw` (whether a request is drawn), which shadows
  a `draw()` of the mount: `tsc` refused the call inside it
  (`TS2349: This expression is not callable`). Renaming that parameter
  would change code outside the list of task 4.1, so the new function
  carries another name. Its comment says so and cites Decision 2, point 7.
- **`drawPicture()` holds the one `renderer.render(scene, camera)` of the
  file and records only when the mount is continuous** (a `continuous`
  constant fixed at mount), so `renderer.render(` occurs once (5.3). In the
  on-demand mode it renders and records nothing, with one constant false
  test beside the render. The resize observer is given `resize` itself in
  the on-demand mode, exactly as on the base, and a callback that resizes
  and draws in the continuous mode.
- **`update` raises at two places:** before copying the prepared
  transforms when any was prepared, and in `updateShapes` before each
  flexible part the change set reaches is evaluated (the private recursive
  helper `update` calls), so the raise precedes every write. A colour
  prepared alone (a node whose colour expression the change set reaches)
  counts as a prepared transform and raises.
- **`artifactChanged` raises once its loads are complete, before applying,
  whether or not any replacement matched the path** (an unknown artifact
  then raises with nothing to apply: one redundant draw, never a missed
  one).
- **B2 mounts with `driverControls: 'none'`.** A Playwright screenshot of
  the canvas's box takes in the panels drawn over the canvas; on the base,
  the clocked panel's text rasterised a few pixels differently between two
  screenshots of the same state (a difference of at most 7 in one channel,
  in the panel's row of buttons), which made B2's comparison fail on the
  base for reasons that are not the canvas. With the panels off (the
  handle keeps the whole machine and run API), every comparison passed on
  the base. Pictures are compared decoded (size and RGBA pixels), not as
  PNG bytes, because two encodings of the same pixels differed.
- **The bench's documents.** Hand-written: a version 2 document; a version
  14 posed document with float and integer drivers, two instructions, a
  `$t` timeline, a colour choice, markings and a flexible part; a version 2
  posed document with one driver and one instruction; a version 3 document
  with a flexible part; a version 2 document with markings; a version 8
  clocked document with no clock and two drawn instructions on an integer
  input. Fixtures read: `regulator`, `touched`, `spinner`, `marked`,
  `state-color/posed`, `calculator`. I1 and S0 run on twelve kinds (the
  design's eight plus `marked`, `calculator`, the whole posed document and
  the clocked one).
- **The counting renderer** keeps the real canvas, defines its client size,
  rectangle and pointer capture, and records D's reading at each draw.
  `performance.now` is controlled for every test (the bench's clock), not
  only where a ramp runs. Frames are followed by forty microtask turns,
  enough for the in-thread run's replies; no wall clock is slept on.
- **What counts as an update.** I1, I2 and the tails count every call of
  `WidgetTree.prototype.update`; M1 to M6 count, per frame, the calls whose
  change set names something (`'all'`, time, or a driver).
- **S11's republish** changes the program's identity, so the run restarts
  and the call awaits the new program's start, and moves a part. The start
  is held by a spy on `RunRuntime.start` returning the real run with its
  `ready` gated. The bench held it: while held, the call had applied and
  not drawn, the next frame drew once with D matching (on the base too),
  and after release the call drew and ten frames drew nothing (red on the
  base).
- **M5** starts the run and triggers `Add one` through the handle; **M6**
  holds a press on a dial with `pointerdown` and lets it go with
  `pointercancel` (a `pointerup` would submit the instruction and start
  the run); its recorded sequence includes the frame after the release,
  which shows the hover's end.
- **G1:** 200 sequences, seeds 1 to 200, the document by `seed % 4` over
  the posed, `regulator`, clocked and `touched` documents, 30 steps each
  from a common vocabulary (`setView` sometimes with a new up, wheel, drag,
  resize sometimes to zero, highlight in each treatment or its put-back,
  `setVisible`, `setRoot`, `setTime`, blur, `reload()`, `manifestChanged()`
  with the served document recoloured, moved, grown or shrunk,
  `artifactChanged()`, `webglcontextrestored`, `visibilitychange`) and the
  document's own (`setDriver` and `trigger` then frames until it lands; the
  machine's `move`, `restore`, `reset`; the clock played and paused; a
  drawn `machine().trigger`, waited for or not; a hover and its end; the
  run started, paused and triggered), each followed by one to three frames
  of 1 to 40 ms, D checked after every frame. At the end every motion is
  stopped (clock and run paused, ramps and drawings left to land) and
  twenty frames must draw and update nothing. Correction made after the
  first base run: a drawing is waited for by its declared duration rather
  than by its button's `aria-busy`, because after `setRoot` the clocked
  panel shows no instruction button and the bench stopped waiting while a
  drawing still ran (three sequences on the implementation then drew in
  their tails, which was the drawing, correctly drawn). The corrected file
  was run on the base again (above).
- **B2's steps** run in one page per document; the drag starts at a point
  of the canvas clear of every control's rectangle and of any panel; full
  screen was granted by headless Chromium and ran.
- **`picture.ts`'s names:** `PictureRevision` with `value()` and
  `raise()`; `cameraReading(camera)`; `sameReading(a, b)`.

## Found while applying, out of scope

- A clocked panel rebuilt while a drawing runs (for another focus, or by a
  republish's `refreshControls`) does not carry the running instruction's
  `aria-busy` onto the rebuilt button, and after `setRoot` to a subassembly
  the panel shows no instruction button at all. Unchanged here.

## Reviewer's record: review of the implementation and task 7.2

Written by the repository agent, 22 November 2026, after the applier stopped.

### Review of the implementation

`src/picture.ts` and the diffs of `src/viewer.ts`, `src/tree.ts`,
`src/presentation.ts` and `src/drivers.ts` were read line by line against
design Decisions 2 to 5 and 7: the loop is the design's code; `changed()`
is the four terms; `moving()` is the six; the one render is in
`drawPicture()`, which records only in the continuous mode; the observer
resizes and then draws in the continuous mode and is the bare `resize` on
demand; the two listeners are installed with the loop and removed at
disposal. No difference from the design found. One comment in `viewer.ts`
repeated the design's statement that `setSize` clears the canvas at an
equal size; it now says what is known (it clears when the size changes,
and a browser may at an equal size).

**The constants, again.** Both test files were copied into a clean
checkout of the base (`56de33dd`, another bench of the repository), run
there and removed: 17 tests pass on the base (D0, S0 for its twelve kinds,
W1's three, O1) with the recorded constants; M1 to M6 fail there only at
their ten still frames, which the base draws, so their per-frame counts
are the base's; S3 fails at once (no draw inside the observer's callback);
`picture-revision.test.ts` fails at the absent module. The constants are
the base's.

**Faults of the reviewer's own.** Sixteen, none of them from the design's
list, planted one at a time in `src/viewer.ts`, `src/tree.ts`,
`src/presentation.ts` or `src/picture.ts`, with
`src/draw-on-change.test.ts` and `src/picture-revision.test.ts` run
against each and the files restored and checked by digest. The verdict
script was first tried on an edit of a comment (no test red) and on one
fault known to be real.

| Fault planted | Result |
|---|---|
| a comment edited (the control) | passes, as it must |
| the frame a motion stops in is drawn only if something else calls for it (posed and clocked documents) | passed: a gap, closed below |
| the same for a run | passes: equivalent in every case the bench reaches, see below |
| the observer draws only when the size really changed | passed: a gap, closed below |
| a page hidden forces the next frame, a page shown does not | S8 red |
| an update whose change set names a moved driver is skipped too | M1 red |
| the camera compared within a tolerance | U7 and G1 red |
| the camera read without its projection | U7 red |
| an update that only refills a flexible part raises nothing | U1 red |
| an update raises the revision after its transform writes | passes: equivalent, see below |
| a paused run draws for motion only, never for a change | S0, S1 to S8, S10, S11, M and G1 red |
| a highlight's put-back does not draw before it returns | S9 and O1 red |
| a run's committed frame does not draw in its own task | M5 and G1 red |
| the time between frames counted from the last frame that mattered | W1 red |
| `reconcile` does not raise the revision itself | passed: a gap, closed below (the applier's MU10 found it too) |
| the observer draws before it resizes | S3 red |
| every holder shares one revision | passed: a gap, closed below |

Ten were caught as the tests stood. Four showed gaps in the proof, not in
the implementation, and are closed by four cases the reviewer added:

- **The frame a motion stops in.** In M1 to M6 the last frame of each
  motion moves something, and a frame that moves something is drawn
  anyway. M7: a ramp to the value its driver already has moves nothing on
  any frame, the one it lands on included; its 63 frames each draw once on
  the base (recorded on the clean base checkout) and must on the
  implementation, and then nothing. Red with the fault planted again.
- **A resize at an unchanged size.** S3 now observes a second time without
  changing the size and requires a draw: "every `setSize` is followed by a
  draw" was held by no count, because headless Chromium does not clear at
  an equal size and so no picture could show it.
- **`reconcile`'s own raise.** U5 gains a republish applied with no
  candidate scope, so that no update follows the application.
- **One revision per holder.** U6 gains two holders made without a
  revision: raising one's does not move the other's. The existing case
  compared two fresh counters, both zero.

Two are equivalent:

- **`wasMoving` in the run's branch.** A run stops inside a frame only by
  a refusal, which commits nothing, so that frame's picture is the one
  before it; every other stop (a pause, a gesture let go) happens between
  frames. The term keeps the rule that a motion's last frame is drawn; no
  test in the bench can reach a refusing program.
- **The raise before or after the transform writes.** Nothing between the
  first matrix copy and the last can throw; what can throw is the flexible
  parts' evaluation after them, and the raise precedes it either way.

The applier's two mutations that turned nothing red are of the same kind
as the third gap: the tree-identity term and `reconcile`'s raise are both
made redundant, on every path of the mount, by an update of the whole tree
that follows them. The identity term is kept as the design has it.

Final gate with the four added cases: the widget suite 73 files passed and
1 skipped, 1,998 tests passed and 2 skipped (the two environment-gated
Curta profile tests), no failure; `tsc --noEmit` clean; the bundle rebuilt
with the SHA256 the applier recorded,
`d1b7b0af54e27ac5ddb48be8f2a96114269ff0ed8a9141a96b6bb17ab84c780f`; the
Python suite on that bundle 290 passed and 2 skipped (the Curta's own
builds are not on this machine), B1 to B4 and the restated regulator test
among the passed.

### 7.2 The Enigma I page

Method: `workflow/evidence/enigma-idle-frame-cost-2026-11-21.md`'s.
`enigma-i` at `081f4e6`, its `_build-page/`, headless Chromium
(Playwright) on a virtual machine with no GPU. The viewer was built
unminified from its unedited source with a scratch entry exposing the
renderer, the scene and the mounted handle, with molejo's `main`: once
from the base (`56de33dd`) and once from this bench. Each build ran in two
page loads: one for counts and times, with WebGL draw calls counted and
not executed, and one for pictures, really drawn by the software
rasteriser from the page's first frame on.

**Counts and times.** Four still periods of 2.5 seconds, and the eight
seconds after the click of three presses and three releases.

| | Base | This change |
|---|---|---|
| Still: frames in 2.5 s | 121 to 143 | 147 to 150 |
| of them, frames that drew | all | 0 |
| tree updates | one a frame, each naming no change | 0 |
| WebGL draw calls | 3,347 a frame | 0 |
| script per frame, median | 16.0 to 20.3 ms | 0.0 ms (mean 0.03 to 0.05, largest 0.2) |
| After a press: frames in the eight seconds | 324 to 372 | 398 to 402 |
| of them, frames that drew | all | 39 to 42 |
| frames in which a mesh moved, a geometry was refilled or a colour changed | 36 to 39 | 38 to 41 |
| such frames not drawn | 0 | 0 |
| the last frame drawn, after the click | at the end of the eight seconds | 2,012 to 2,050 ms, the last frame that changed anything |
| script per changing frame, median | 49.9 to 53.5 ms | 49.6 to 51.0 ms |
| script in the eight seconds | 7.43 to 7.55 s | 1.93 to 1.97 s |
| the click's own task | 50.1 to 58.8 ms | 57.7 to 62.3 ms |

In this change every press draws one frame more than changed something:
the first frame of the drawing, which stands at the origin.

**The click.** It measured about 4 ms more with this change. On the
base's own code, a click after five seconds in which the measurement
skipped the draw and the empty update from outside cost 59.9 to 71.7 ms
(eight clicks), against 52.3 to 59.6 and one of 91.7 after ordinary still
frames in the same page load. The click is slower after a period in which
the page ran no script, whichever viewer; this change adds no work to it.
Why (processor caches, the virtual machine's scheduling) was not
established.

**Pictures.** Eighteen states, in the same order in every page load: at
rest after the mount; a key held; released; the three highlights
(`keyboard/front_row/keys-0`, others kept, dimmed, ghosted) and each
put-back; the flap opened and closed; a wheel stepped and back; the model
turned by a drag on the canvas; zoomed by the wheel; the window resized to
1180 by 760 and back; a reload through the handle. In each state, after
three animation frames and three more, a screenshot of the composited
page clipped to the canvas (what is on screen); then the same state drawn
again by a direct call of the renderer, two frames, and a second
screenshot.

| Page load | States in which what is on screen differs from the forced draw, of 18 | Draws in the three waiting frames |
|---|---|---|
| The base | 0 | 3 in every state |
| This change | 0 | 0 in every state |
| This change built without the camera in what the loop compares (the control for a stale picture) | 2: the turn (177,910 pixels) and the zoom (102,026) | 0 |

Between the base's page load and this change's, the 36 screenshots
compared one for one: no pixel differs. Between the base's and the
control's: the two on-screen pictures of the turn and the zoom differ and
the other 34 do not.

No page error and no console error or warning in any run.

**The design's expectations** ("What the Enigma should show"): no pixel
differs: met, in these states. No draw and no update in a still period,
near 0.1 ms of script: met, at 0.03 to 0.05 ms. After a press, draws on
every frame until the last drawing lands and none after: met. The frames
of a press cost what they cost: met. A press itself costing what it
costs: its click measured about 4 ms more, for the reason above.

**Limits.** Script time on one virtual machine; no GPU was involved, and
what the page no longer asks of a graphics card was counted (draw calls),
not measured. The pictures are 18 states of one document in headless
Chromium on a software rasteriser: they do not show that no state of no
document goes stale, which is what the detector, the generated sequences
and the browser tests on fixtures are for; another browser was not tried.
Not exercised on this page: a hover and a gesture on a part (the page
declares no part controls), a running program, a republish, a lost
graphics context, a page hidden and shown again. The Enigma document is a
project's and is not in this repository; its pictures cannot be committed
here.

