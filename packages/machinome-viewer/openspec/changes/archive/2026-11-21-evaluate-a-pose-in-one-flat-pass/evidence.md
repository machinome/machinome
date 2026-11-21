# Evidence: evaluate a pose in one flat pass (applier, tasks 1.2 to 6.2)

The applier's record, 20 to 21 November 2026, on the bench
`machinome/WTs/evaluate-a-pose-in-one-flat-pass`. Commands ran from
`packages/machinome-viewer/machinome/viewer/web/widget/` with the primary
checkout's `vitest` and `tsc`, one run at a time. The review (7.1), the
Enigma page (7.2), the decision records (8.2) and the sync, archive and
commit (8.3) are the reviewer's and are not recorded here. Sections 1.2
to 8.1 are the first implementation's, under the first form of Decision 4
(a whole pass declined for one absent input); where the correction of
Decision 4 replaced a figure, the section says so, and the correction's
own record is the last section, "4.5 to 4.9".

## 1.2 The bench

Clean tree; HEAD `5f031494` (the planning commit), one commit above the
base `e87683e33f8bd824cd8a27270b6371dfe3a8014a`;
`openspec validate evaluate-a-pose-in-one-flat-pass --strict`: "Change
'evaluate-a-pose-in-one-flat-pass' is valid".

## 2.1 and 2.2 Red on the base

Run against the base's `src/expressions.ts` and `src/tree.ts` (taken from
`HEAD`, which does not change them, and restored afterwards, `cmp` equal),
with the final test files.

`src/flat-pass.test.ts`: 35 failed of 35. Failure reasons, counted:

```
      1 AssertionError: expected 3003 to be less than or equal to 4
      1 TypeError: flatPassMetrics is not a function
     33 TypeError: prepareFlatPass is not a function
```

W1 fails on its resolution count, before any call of a new name: the base
performs 3,003 resolutions for the pose that moves `b` (the design measured
3,004 on its own construction; this one has exactly 1,200 entries, a
balanced sum over 600 leaves `(a + i)` and `_b = (b + 1)`). E16 fails at its
first statement, `flatPassMetrics()`; every other test at its first
`prepareFlatPass`. None fails on a value assertion.

`src/tree.test.ts`: 1 failed, 70 passed (71). T1 fails with
`TypeError: flatPassMetrics is not a function`; T2 and every existing test
pass.

## 2.3 and 5.3 The cost tests, base and implementation

Both files pass on every side (`src/run/cost.test.ts` 14 of 14,
`src/clocked/cost.test.ts` 8 of 8). Single runs on this host. The third
column is the corrected implementation's (task 4.9), run after the
correction; the second, the first implementation's, is kept beside it.

| Figure | Base | Implementation | Corrected |
| --- | ---: | ---: | ---: |
| CarryLead, affine plans | 43,219 ticks/s | 49,939 ticks/s | 46,927 ticks/s |
| CarryLead, plans forced to search | 13,930 | 15,965 | 15,425 |
| Train, no constraint | 63,990 | 70,242 | 64,653 |
| Captured, blocking ticks | 62,621 | 65,057 | 62,115 |
| the lock, idle | 25,705 | 24,894 | 25,827 |
| the lock, advancing the key | 628 | 676 | 648 |
| Clearing, a solved self-read | 7,606 | 8,289 | 8,030 |
| the Curta fixture at dt = 1/240 | 962 | 975 | 1,017 |
| ShiftedCarry, quiet / frozen / crossing | 3,361 / 6,691 / 1,789 | 3,375 / 6,853 / 1,774 | 3,466 / 7,011 / 1,819 |
| the Curta carriage at dt = 0.02 | 391 | 418 | 421 |
| RangedBlock, quiet / searched stop | 7,463 / 1,064 | 7,848 / 1,049 | 7,991 / 1,107 |
| the Pascaline at dt = 1/240 | 4,105 | 4,437 | 3,865 |
| evaluations per tick (Curta fixture; Clearing, Train, Curta carriage) | 2436.0; 459.1, 31.0, 4301.9 | identical | identical |
| Calculator move / trigger, median of 40 | 0.2375 / 0.2087 ms | 0.1741 / 0.1542 ms | 0.2475 / 0.2046 ms |
| Calculator stroke; clearing sweep; clipped move (ms) | 0.27/0.14/0.24; 0.73/1.07/0.73; 1.06/0.25/0.21 | 0.39/0.14/0.16; 0.61/0.38/0.43; 1.03/0.22/0.20 | 0.21/0.14/0.23; 0.68/0.41/0.46; 1.05/0.23/0.23 |
| Counter, ten events (ms) | 0.48 / 0.37 / 0.29 | 0.45 / 0.29 / 0.28 | 0.54 / 0.31 / 0.48 |
| Regulator frame x1 / x60 / x3600 (ms) | 0.19/0.04/0.02; 0.07/0.04/0.03; 2.08/1.29/1.16 | 0.15/0.03/0.02; 0.11/0.04/0.03; 1.98/1.56/1.17 | 0.18/0.07/0.03; 0.07/0.04/0.03; 2.27/1.57/1.26 |
| Regulator, 240 events (ms) | 7.00 / 7.67 / 5.68 | 6.45 / 6.00 / 5.95 | 6.68 / 5.99 / 5.73 |
| the whole clocked corpus, 81 steps | 18.5 ms | 13.1 ms | 13.1 ms |

Within the noise of single runs, as Decision 6 predicted, on both
implementations; no gate failed.

## 3 The implementation, and what the design left open

`src/expressions.ts` gains the flat pass after `valueOf` (module comment,
`FLAT_PASS`, the twenty functions, compile, run, self-check,
`prepareFlatPass`, `flatPassMetrics`, `flatPassServes`), one read in
`valueOf` after the memo test, three lines in `resetStore()` and one in
`resetExpressionMetrics()`. Parsing, interning, `resolveName`, `compute`,
`applyUnary`, `applyBinary`, `PathValue`, `ExpressionPath` and the
structural walkers are unchanged. `src/tree.ts` imports `prepareFlatPass`
and calls it first in `update`'s and `admit`'s `withExpressions`, nothing
else. `tsc --noEmit`: clean.

Decisions the design left open, and what was chosen:

1. **Entry layout.** Entry `e` writes slot `e`: entries occupy the first
   slots in run order and literals and inputs follow, so no destination
   array is needed. A call's function is encoded in its operator code
   (`16 + 4 * index + arity class`); a call of one or two arguments uses
   the two operand arrays, of more the pool (offset and count in the two
   operand arrays). A call of no argument of a listed function (`max()`)
   is covered like any other.
2. **Walk children.** As Decision 1 defines them: a unary's target, a
   binary's operands, a call's arguments and a binding name's root, for
   covered and uncovered unaries, binaries and calls alike; a member,
   index, ternary, array or object is not descended into, so a covered
   subtree reachable only through one of them is left to the walk.
3. **A generation guard** besides the `WeakMap` replacement: a program
   whose recorded generation is not the store's is compiled again. The
   mutation M7a below removes only the `WeakMap` replacement, and L1 stays
   green because of the guard; M7 removes both and L1 goes red.
4. **A root id outside the store** (a stale map handed in by a caller) is
   left uncovered rather than read.
5. **Driver maps the walk cannot use `in` on.** A scope whose `drivers` is
   neither `undefined` nor an object or a function (`null`, a number)
   declines, since the walk's `in` throws there.
6. **The self-check runs before the pass is served**, which is how slot
   reads are suspended (no flag in `valueOf`): leaves first, then the
   entries in run order, then the binding names, so each walk finds its
   children memoized and recursion stays shallow. Its mismatch error is
   thrown outside the failure `catch`: "The flat pass differs from the walk
   at node N, <kind>: flat <value> (<type>), walk <value> (<type>)".
7. **`scope.bindings` is read outside the `try`**, where Decision 3 places
   it.
8. **`flatPassMetrics()` adds `coveredNodes`**, the last compiled
   program's nodes with a slot (binding names included), for the
   reviewer's comparison with the prototype's 433,678 on the Enigma page.

No departure from the design's covered set, kinds, run order or lifetime.

## 4.1 Green

Replaced by the correction (4.8: `src/flat-pass.test.ts` 41 passed of 41,
`src/tree.test.ts` 71 of 71). The first implementation's figures:
`src/flat-pass.test.ts`: 35 passed (35); W1 prints "1200 entries; the pose
moving b: 3 resolutions, 1 flat entries". `src/tree.test.ts`: 71 passed
(71).

## 4.2 The mutations

M1 and M3 to M7a stand for the corrected implementation as they were run
on the first one (the correction does not touch what they mutate). M2's
row is replaced: under the correction S8 is no longer a declined pass, and
M2 is rerun as the callee check made after the inputs are stored, which
turns S14 red (4.8). Each applied to the implementation alone, `src/flat-pass.test.ts` run, the
implementation restored and confirmed byte-equal to a saved copy (`cmp`).

| Mutation | Result | Red tests (first failing assertion) |
| --- | --- | --- |
| M1 boolean slot handed out as its number | 5 failed | E1 "1 (number) is not true (boolean)", E2 "0 (number) is not false (boolean)", E3, E5, E6 |
| M2 inputs written before the checks | 1 failed | S8 "2 (number) is not 4 (number)" (`_as8` stale) |
| M3 no callee-name check against the driver map | 1 failed | S6 (declined 0, expected 1) |
| M4 `&&` and `||` covered eagerly | 1 failed | E6 "_g6: expected true to be false" (served) |
| M5 every context function listed, `random` included | 2 failed | E13 (`random()` served), E14 (`hypot` served) |
| M6 masks saturating to every input past 32 | 1 failed | S7 "expected 70 to be 1" (entries) |
| M7 programs not dropped by `resetStore()` (and no generation guard) | 1 failed | L1 "expected 1 to be 2" (compiles) |
| M7a only the `WeakMap` replacement removed | 0 failed | the generation guard keeps L1 green |

A test defect found here and corrected before these results: the first
version of the tests' `reference()` helper left the evaluation pass equal
to the scope posed next, so the pose was the same pass and `valueOf`
returned the walk's memo, and M1 turned only E6 red and M2 nothing. The
helper now moves the pass after taking the reference. The red run of 2.1
above is with the corrected file.

## 4.3 The parity proof

Replaced by the correction: under the corrected Decision 4 all 52 pass,
every document served in full or in part and none declined (the table of
"4.5 to 4.9"). What follows is the first implementation's run, kept as the
correction's red.

`src/flat-pass-parity.test.ts`, minimum 0 and self-check on, over every
document Decision 10 names: 52 tests, 40 passed, **12 failed**. No
mismatch in any document, by the self-check or by the comparison of every
operation, flexible parameter, colour condition and entry name (raw value
and `evalExpr`) served against walked; no failure (`failures` 0
everywhere). The 12 failures are all the same assertion: no run ever
completes (`runs` 0), because every pose of those documents **declines**.

How each kind was posed: clocked documents by `clockedMachine` with a
`pose` hook posing every committed bank by `clockedScope` at `$t` 0, over
the corpus script, or for a fixture every declared instruction and then
every driver to its range ends and three seeded values inside it (or by
+1, -1 and two seeded travels without a range), and the standing bank
posed again at `$t` 0.37 after every request; running documents by
`Engine` tick by tick, posing `poseScope` of every state, over the corpus
script, the commands file for `follow-wrapped-v12`, or for a fixture every
instruction and every driver's targets with twenty ticks each at dt 1/30;
the four source-timing exports at the program's initial bank and every
bank their `rows` and `partitioned` record (the source-timed moves that
reach them take tens of seconds each, and parity needs the banks only);
the parity fixture's 451 cases at their own scopes through its table, each
case's expression compared beside the entries. A document with a root is
posed through `WidgetTree.update`; one without (the corpora,
`follow-wrapped-v12`) through `prepareFlatPass` alone. The state-colour
fixtures carry no table and are not in the file. `run/profile-overlap-v13.json`
carries no table.

| document | entries | poses | served | compiles | runs | declined | failures | compared | programEntries | segments | inputs | covered | comparisons | refusals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fixtures/calculator | 39 | 47 | 0 | 1 | 0 | 47 | 0 | 0 | 39 | 13 | 9 | 99 | 4230 | 0 |
| fixtures/lock | 23 | 322 | 322 | 1 | 322 | 0 | 0 | 21252 | 28 | 8 | 7 | 66 | 37996 | 0 |
| fixtures/touched | 38 | 322 | 322 | 1 | 322 | 0 | 0 | 30268 | 39 | 6 | 5 | 94 | 63756 | 0 |
| fixtures/pascaline | 50 | 302 | 0 | 1 | 0 | 302 | 0 | 0 | 51 | 12 | 8 | 121 | 66440 | 0 |
| fixtures/carriage | 35 | 402 | 402 | 1 | 402 | 0 | 0 | 35778 | 38 | 10 | 9 | 89 | 42612 | 0 |
| fixtures/clearing | 30 | 82 | 82 | 1 | 82 | 0 | 0 | 7052 | 33 | 8 | 7 | 86 | 6888 | 0 |
| fixtures/astrarium | 1 | 182 | 182 | 1 | 182 | 0 | 0 | 728 | 1 | 1 | 2 | 4 | 1820 | 0 |
| fixtures/pose-admission | 1 | 23 | 23 | 1 | 23 | 0 | 0 | 92 | 1 | 1 | 1 | 4 | 368 | 1 |
| fixtures/direct-motion/columns | 8 | 202 | 0 | 1 | 0 | 202 | 0 | 0 | 8 | 4 | 3 | 22 | 5252 | 0 |
| source-timing/curta-6 | 4227 | 17 | 0 | 1 | 0 | 17 | 0 | 0 | 4295 | 748 | 649 | 9348 | 144772 | 0 |
| source-timing/curta-7 | 4853 | 17 | 0 | 1 | 0 | 17 | 0 | 0 | 4921 | 854 | 741 | 10693 | 166090 | 0 |
| source-timing/curta-11 | 7569 | 17 | 0 | 1 | 0 | 17 | 0 | 0 | 7638 | 1234 | 1089 | 16478 | 258570 | 0 |
| source-timing/curta-11-constrained | 9809 | 17 | 0 | 1 | 0 | 17 | 0 | 0 | 9885 | 1235 | 1090 | 21266 | 334730 | 0 |
| clocked/Counter | 6 | 13 | 13 | 1 | 13 | 0 | 0 | 234 | 6 | 3 | 2 | 18 | 156 | 0 |
| clocked/KinkedCounter | 6 | 5 | 5 | 1 | 5 | 0 | 0 | 90 | 6 | 3 | 2 | 18 | 60 | 0 |
| clocked/Register | 19 | 13 | 13 | 1 | 13 | 0 | 0 | 624 | 19 | 7 | 4 | 48 | 494 | 0 |
| clocked/Clearer | 3 | 5 | 5 | 1 | 5 | 0 | 0 | 45 | 3 | 1 | 1 | 9 | 30 | 0 |
| clocked/Pawl | 7 | 5 | 0 | 1 | 0 | 5 | 0 | 0 | 7 | 4 | 3 | 22 | 70 | 0 |
| clocked/Stroke | 6 | 5 | 5 | 1 | 5 | 0 | 0 | 90 | 6 | 3 | 2 | 18 | 60 | 0 |
| clocked/ScaledStroke | 6 | 3 | 3 | 1 | 3 | 0 | 0 | 54 | 6 | 3 | 2 | 18 | 36 | 0 |
| clocked/Lock | 2 | 5 | 5 | 1 | 5 | 0 | 0 | 40 | 2 | 2 | 2 | 8 | 20 | 0 |
| clocked/Kinked | 1 | 5 | 5 | 1 | 5 | 0 | 0 | 20 | 1 | 1 | 1 | 4 | 10 | 0 |
| clocked/Freeze | 7 | 11 | 0 | 1 | 0 | 11 | 0 | 0 | 7 | 3 | 3 | 21 | 154 | 0 |
| clocked/Gate | 1 | 5 | 5 | 1 | 5 | 0 | 0 | 20 | 1 | 1 | 1 | 4 | 10 | 0 |
| clocked/Shut | 1 | 2 | 2 | 1 | 2 | 0 | 0 | 8 | 1 | 1 | 1 | 4 | 4 | 0 |
| clocked/SamePair | 1 | 3 | 3 | 1 | 3 | 0 | 0 | 12 | 1 | 1 | 1 | 4 | 6 | 0 |
| clocked/SwappedPair | 1 | 3 | 3 | 1 | 3 | 0 | 0 | 12 | 1 | 1 | 1 | 4 | 6 | 0 |
| clocked/JumpsOnly | 3 | 3 | 3 | 1 | 3 | 0 | 0 | 27 | 3 | 1 | 1 | 9 | 18 | 0 |
| clocked/Conflict | 1 | 2 | 2 | 1 | 2 | 0 | 0 | 8 | 1 | 1 | 1 | 4 | 4 | 0 |
| clocked/Calculator | 39 | 33 | 0 | 1 | 0 | 33 | 0 | 0 | 39 | 13 | 9 | 99 | 2574 | 0 |
| running/OvertakenFollower#0 | 2 | 5 | 5 | 1 | 5 | 0 | 0 | 35 | 2 | 1 | 1 | 7 | 20 | 0 |
| running/NegativeFollower#1 | 2 | 5 | 5 | 1 | 5 | 0 | 0 | 35 | 2 | 1 | 1 | 7 | 20 | 0 |
| running/ObservedFollower#2 | 2 | 5 | 5 | 1 | 5 | 0 | 0 | 35 | 2 | 1 | 1 | 7 | 20 | 0 |
| running/FollowingContact#3 | 6 | 5 | 5 | 1 | 5 | 0 | 0 | 95 | 6 | 3 | 2 | 19 | 60 | 0 |
| running/StationaryFollower#4 | 2 | 5 | 5 | 1 | 5 | 0 | 0 | 35 | 2 | 1 | 1 | 7 | 20 | 0 |
| running/PeriodicStop#5 | 1 | 4 | 4 | 1 | 4 | 0 | 0 | 20 | 2 | 2 | 1 | 5 | 8 | 0 |
| running/Window#10 | 1 | 25 | 25 | 1 | 25 | 0 | 0 | 100 | 1 | 1 | 1 | 4 | 50 | 0 |
| running/Wrapped#12 | 2 | 21 | 21 | 1 | 21 | 0 | 0 | 147 | 2 | 1 | 1 | 7 | 84 | 0 |
| running/Throwing#13 | 2 | 21 | 21 | 1 | 21 | 0 | 0 | 147 | 2 | 1 | 1 | 7 | 84 | 0 |
| running/Clutch#14 | 1 | 25 | 25 | 1 | 25 | 0 | 0 | 125 | 2 | 2 | 1 | 5 | 50 | 0 |
| running/CarryLead#15 | 8 | 25 | 0 | 1 | 0 | 25 | 0 | 0 | 8 | 4 | 3 | 22 | 400 | 0 |
| running/CarryLead#16 | 8 | 15 | 0 | 1 | 0 | 15 | 0 | 0 | 8 | 4 | 3 | 22 | 240 | 0 |
| running/StopAndJump#20 | 2 | 13 | 13 | 1 | 13 | 0 | 0 | 91 | 2 | 1 | 1 | 7 | 52 | 0 |
| running/Clearing#21 | 4 | 25 | 25 | 1 | 25 | 0 | 0 | 350 | 4 | 2 | 2 | 14 | 200 | 0 |
| running/Clearing#22 | 4 | 13 | 13 | 1 | 13 | 0 | 0 | 182 | 4 | 2 | 2 | 14 | 104 | 0 |
| running/StoppedClearing#23 | 4 | 17 | 17 | 1 | 17 | 0 | 0 | 238 | 4 | 2 | 2 | 14 | 136 | 0 |
| running/ShiftedCarry#24 | 4 | 21 | 21 | 1 | 21 | 0 | 0 | 231 | 4 | 2 | 2 | 11 | 168 | 0 |
| running/RangedBlock#25 | 3 | 9 | 9 | 1 | 9 | 0 | 0 | 72 | 3 | 1 | 1 | 8 | 54 | 0 |
| time-drive/TimeEnabled | 1 | 6 | 6 | 1 | 6 | 0 | 0 | 24 | 1 | 1 | 1 | 4 | 12 | 0 |
| time-drive/AstrariumClock | 1 | 21 | 21 | 1 | 21 | 0 | 0 | 84 | 1 | 1 | 2 | 4 | 42 | 0 |
| run/follow-wrapped-v12 | 4 | 16 | 16 | 1 | 16 | 0 | 0 | 160 | 4 | 1 | 1 | 10 | 128 | 0 |
| parity-fixture | 4 | 451 | 30 | 1 | 30 | 421 | 0 | 360 | 4 | 3 | 2 | 12 | 4510 | 0 |

### Finding: twelve documents never get a served pose

Why they decline, found by a temporary instrumentation of the run's
checks (restored, `cmp` equal): the first unread input of every declined
pose is a name a pose's scope never binds.

| Document | The unbound name | Example entry |
| --- | --- | --- |
| fixtures/calculator, clocked/Calculator, clocked/Pawl, clocked/Freeze | `_own` | calculator `_b33 = (_own / 6.0)` |
| fixtures/pascaline, fixtures/direct-motion/columns, the four source-timing exports, running/CarryLead (both) | `_j0` | pascaline `_b33 = (360.0 * _j0)` |
| parity-fixture (421 of 451 cases) | `share` | a case scope without that driver |

`_own` is what a clocked relation's law reads for its own value and `_j0`
a jump plan's branch placeholder: the machinery that reads those entries
binds them, a pose never does, and no operation reaches those entries. So
Decision 4's premise, "no committed document or the Enigma is known to
pose with a missing input", does not hold for committed documents: under
"a scope missing one input declines the whole pass", every pose of these
documents is walked, correctly and as slowly as today. That includes
every source-timing Curta export, which Decision 5 expected on the pass.
The spec delta's promises still hold (such a pose is the walk's, and
nothing is left stale); what does not hold is the design's expectation of
who is served, and the parity proof proves nothing about these twelve
programs (`compared` 0). The file keeps the designed assertion and is red
on them, as Decision 10 asks ("a finding to report, not a test to
relax"). Whether the Enigma's table names such a placeholder is the
reviewer's measurement to settle; the prototype's report that nothing
reached from a root was left out, and its 14 inputs, suggest it does not.
The choice of a remedy (for example the rejected alternative "decline only
the cone of a missing input", or leaving a name the compile scope does not
bind uncovered) is a design decision and is not made here. The reviewer
chose the first; it is the corrected Decision 4 ("4.5 to 4.9").

A diagnostic run, not kept in any file: the parity file posed once more
with every bare name an entry reads that the pose leaves unbound set to
0.25 in the scope. All 52 passed, no mismatch, no failure; every one of
the twelve served every pose, for example curta-11-constrained 17 of 17
poses served, 9,885 program entries, 1,235 segments, 1,090 inputs, 21,266
covered nodes, 361,522 values compared by the self-check; curta-6 158,916;
curta-7 181,781; curta-11 280,126; pascaline 36,542; calculator 4,653; the
parity fixture 451 of 451 served, 5,412 compared. The test file was
restored byte-equal afterwards.

## 4.4 The whole suite under the self-check

Replaced by the correction (4.9: 1 failed, W1 alone, for the reason
below). The first implementation's run: `FLAT_PASS` edited in the source to `{ minimumBindings: 0, verify: true }`
for one `vitest run`, then restored (`cmp` equal to the implementation;
the line reads `{ minimumBindings: 1_000, verify: false }`):

```
 Test Files  2 failed | 67 passed | 1 skipped (70)
      Tests  13 failed | 1852 passed | 2 skipped (1867)
```

No self-check mismatch anywhere in the suite (no "The flat pass differs"
in the output). The 13 failures: the 12 declined documents of the parity
proof above, and W1, whose count moves only because the self-check walks
covered nodes: "W1: 1200 entries; the pose moving b: 3003 resolutions, 1
flat entries" (W1 runs before its file's `afterEach` restores the
defaults). The two skips are those of 5.2.

## 5.1 The existing tests, unmodified

Each run singly, all green: `src/expressions.test.ts` 88, `evaluator` 25,
`bindings` 15, `expression-reuse` 9, `expression-lifetime` 11,
`validation-pressure` 12, `document` 65, `color` 22, `flexible` 32,
`parity-fixture` 16, `clocked/clocked-corpus` 47, `run/running-corpus` 36,
`run/jumps` 84, `run/run` 120, `run/kink-probe-cache` 8, `run/pose` 6. The
binding-preparation risk Decision 9 names did not materialize.

## 5.2 The gate

Replaced by the correction (4.9: 69 files passed and 1 skipped, 1,871
tests passed and 2 skipped, no failure; `tsc --noEmit` clean). The first
implementation's whole widget suite with the shipped defaults:

```
 Test Files  1 failed | 68 passed | 1 skipped (70)
      Tests  12 failed | 1853 passed | 2 skipped (1867)
```

The 12 failures are the parity proof's declined documents (4.3). The two
skips are environment-gated and skip on the base too:
`src/run/profile-contact.test.ts` "loads the pinned actual-cover v13 Bound
and replays its numeric stop" (`skipIf(!process.env.CURTA_PROFILE_V13_DOCUMENT)`)
and `src/run/profile-installed-benchmark.test.ts` "reports one pinned
installed Curta v13 integration attempt"
(`skipIf(!process.env.CURTA_INSTALLED_PROFILE_DOCUMENT)`).

`tsc --noEmit`: clean (exit 0).

## 5.4 The bundle and the Python suite

Replaced by the correction (4.9: the bundle's new SHA256 and the Python
suite's run on it). The first implementation's `npm run build`: `dist/machinome-viewer.js` 909.1 kb, SHA256
`1f9dbd9947328ecdd41b2958010f8b0f01c5b83ce4a65f6ca2fdf88639d19c56`.

Then the viewer's Python suite on the bench's venv
(`.venv/bin/python -m pytest tests -rs` from `packages/machinome-viewer`):
**284 passed, 2 skipped, 71 warnings in 293.00 s**, no failure. Both skips
are for a missing project build, not for a missing browser:
`tests/test_curta_drawing.py:375` and `:469`, "the Curta's own builds are
not at .../WTs/projects/Calculators/Curta-Type-I-3x/_build". The warnings
are Pillow `getdata` deprecations.

## 8.1

One CHANGELOG bullet under "Unreleased", after the existing ones.

## 4.5 to 4.9 The correction of Decision 4

21 November 2026, on the same bench, the first implementation's work
kept. The reviewer decided the correction after 4.3's finding: an input
the scope does not supply as a number takes only what depends on it off
the pass, and the whole-pass decline stays for a `drivers` value that is
not an object and a driver named like a called function.

### What was red

The parity proof's 12 failing documents of 4.3, every pose declined
(kept as the red: the first implementation's run, unchanged). And
`src/flat-pass.test.ts` with the changed and new tests (below), run on the
first implementation's `src/expressions.ts` (copied in from the saved copy
and restored afterwards, `cmp` equal): **12 failed, 29 passed (41)**.

| Test | First failing assertion on the first implementation |
| --- | --- |
| E9, E10, S1, S2, S3, S8 | `declined`: "expected 1 to be +0" (the pass declined whole) |
| S9 | `partial`: "expected undefined to be +0" |
| S10 | first pose's entries: "expected +0 to be 1" (declined, nothing computed) |
| S11 | `_as11` served in the pass with `b` absent: "expected false to be true" |
| S12 | the pose's `partial` count: "expected +0 to be 1" |
| S13 | `views`: "expected undefined to be 1" |
| S14 | "TypeError: flatPassServing is not a function" (the new probe; the rest of S14 holds on the first implementation, whose declined run writes nothing) |
| S15 | passes: a `drivers` value of `null` was already declined whole |

A defect of the new tests, found and corrected before the red above was
taken again: S12's first version posed three trees with equal scopes over
hash-consed tables, so the three poses were one evaluation pass and the
second and third read the first's served slots (no run, `partial` 0 on
the corrected implementation). S12 now moves the pass before each pose, as
`reference()` does. The red above is with the corrected file; the earlier
red run, with the defective S12, failed the same 12 tests at the same
assertions.

### What changed

`src/expressions.ts`, the flat-pass section only (`valueOf`'s read,
parsing, interning, `resolveName`, `compute` and the rest unchanged):

- the run returns the number of absent inputs, or -1 for a decline; the
  two whole-pass checks come first, as before; an input missing, not a
  number, or met by a truthy primitive owner on its path is marked in the
  program's `incoming` mask instead of declining; phase two skips it,
  counts a present input changed when it differs by `Object.is` or was in
  the program's `absent` mask, then replaces `absent` by `incoming`;
- a segment whose mask meets `absent` is skipped, on the first run too;
- `servedSlotIndex()`: the program's `slotOf` when nothing is absent, else
  its `view`, rebuilt only when `absent` differs from `viewAbsent` (every
  slot of a segment meeting `absent`, and every absent input's slot, set
  to -1 in a copy of `slotOf`); built inside the failure `try`;
- the self-check walks only the nodes of the served slot index;
- `flatPassMetrics()` adds `partial`, `views` and `absentInputs`; the
  source-only probe `flatPassServing()` answers `'full'`, `'part'` or
  `'none'` for the current pass; the module comment states the rule.

What a flat read costs: unchanged, `servedSlotOf[id]`, which is the
program's own index or its view. What a run costs beyond the first
implementation's: with nothing absent, one zeroing of a mask and one
mask copy; with a steady absent set, one comparison of two masks and one
more mask test per segment the changed inputs meet; a new absent set, one
view (a pass over the compile's node count, the slots and the segments).

`src/flat-pass.test.ts`: E9, E10, S1, S2, S3, S8 changed from a whole
decline to a pass served in part (their `declined` 1 became 0 and
`partial` 1, the entry over the absent input not served and the other
served, the values still the walk's); S9 gained `partial` 0 and its title
"leaves nothing absent"; S10 to S15 added. Every other test unchanged.
`src/flat-pass-parity.test.ts`: each pose is classified by
`flatPassServing()` as served in full, in part or not served, and the
report adds those counts, `partial`, `declined` and `views`; its
assertions are unchanged. `src/tree.ts`, `src/tree.test.ts`: untouched.

### 4.8 Green, and the mutations

`src/flat-pass.test.ts`: **41 passed (41)**; W1 prints "1200 entries; the
pose moving b: 3 resolutions, 1 flat entries". `src/tree.test.ts`: **71
passed (71)**.

Each mutation applied to the corrected implementation alone,
`src/flat-pass.test.ts` run once, the implementation restored and
confirmed byte-equal to a saved copy (`cmp`).

| Mutation | Result | Red tests (first failing assertion) |
| --- | --- | --- |
| M2 the callee check made after the inputs are stored | 1 failed | S14 "1 (number) is not 2 (number)" (`max(a, 1)` stale) |
| M8 a returning input not counted as changed | 3 failed | S8 "4 (number) is not 6 (number)"; S10 entries "expected +0 to be 1"; S11 "12 (number) is not 16 (number)" |
| M9 the program's own slot index served whatever is absent | 9 failed | E9, E10, S1, S2, S3, S8, S11 (an unserved node served: "expected true to be false"); S12 the pose reading the cone does not throw ("expected undefined to be an instance of Error"); S13 `views` "expected +0 to be 1" |
| M10 the view rebuilt at every run | 1 failed | S13 `views` "expected 1 to be +0" |
| M11 segments over an absent input run | 2 failed | S10 first pose's entries "expected 2 to be 1"; S13 "expected 52 to be 51" |

### 4.3 again: the parity proof

`src/flat-pass-parity.test.ts`, minimum 0 and self-check on: **52 passed
(52)**, in 3.2 s. No mismatch, no failure, no pose declined; every
document served at every pose, the twelve of 4.3's finding in part at
every pose (their unbound name's cone walked), the parity fixture in part
in the 421 cases without `share`. Every document built at most one view.
`compared` counts the served nodes only, so for the twelve it is below
the diagnostic run of 4.3 that bound every unbound name (curta-11-constrained
210,545 here against 361,522 there; calculator 4,418 against 4,653).

| document | entries | poses | in full | in part | not served | compiles | runs | partial | declined | views | failures | compared | programEntries | segments | inputs | covered | comparisons | refusals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fixtures/calculator | 39 | 47 | 0 | 47 | 0 | 1 | 47 | 47 | 0 | 1 | 0 | 4418 | 39 | 13 | 9 | 99 | 4230 | 0 |
| fixtures/lock | 23 | 322 | 322 | 0 | 0 | 1 | 322 | 0 | 0 | 0 | 0 | 21252 | 28 | 8 | 7 | 66 | 37996 | 0 |
| fixtures/touched | 38 | 322 | 322 | 0 | 0 | 1 | 322 | 0 | 0 | 0 | 0 | 30268 | 39 | 6 | 5 | 94 | 63756 | 0 |
| fixtures/pascaline | 50 | 302 | 0 | 302 | 0 | 1 | 302 | 302 | 0 | 1 | 0 | 32012 | 51 | 12 | 8 | 121 | 66440 | 0 |
| fixtures/carriage | 35 | 402 | 402 | 0 | 0 | 1 | 402 | 0 | 0 | 0 | 0 | 35778 | 38 | 10 | 9 | 89 | 42612 | 0 |
| fixtures/clearing | 30 | 82 | 82 | 0 | 0 | 1 | 82 | 0 | 0 | 0 | 0 | 7052 | 33 | 8 | 7 | 86 | 6888 | 0 |
| fixtures/astrarium | 1 | 182 | 182 | 0 | 0 | 1 | 182 | 0 | 0 | 0 | 0 | 728 | 1 | 1 | 2 | 4 | 1820 | 0 |
| fixtures/pose-admission | 1 | 23 | 23 | 0 | 0 | 1 | 23 | 0 | 0 | 0 | 0 | 92 | 1 | 1 | 1 | 4 | 368 | 1 |
| fixtures/direct-motion/columns | 8 | 202 | 0 | 202 | 0 | 1 | 202 | 202 | 0 | 1 | 0 | 3434 | 8 | 4 | 3 | 22 | 5252 | 0 |
| source-timing/curta-6 | 4227 | 17 | 0 | 17 | 0 | 1 | 17 | 17 | 0 | 1 | 0 | 76874 | 4295 | 748 | 649 | 9348 | 144772 | 0 |
| source-timing/curta-7 | 4853 | 17 | 0 | 17 | 0 | 1 | 17 | 17 | 0 | 1 | 0 | 85680 | 4921 | 854 | 741 | 10693 | 166090 | 0 |
| source-timing/curta-11 | 7569 | 17 | 0 | 17 | 0 | 1 | 17 | 17 | 0 | 1 | 0 | 129149 | 7638 | 1234 | 1089 | 16478 | 258570 | 0 |
| source-timing/curta-11-constrained | 9809 | 17 | 0 | 17 | 0 | 1 | 17 | 17 | 0 | 1 | 0 | 210545 | 9885 | 1235 | 1090 | 21266 | 334730 | 0 |
| clocked/Counter | 6 | 13 | 13 | 0 | 0 | 1 | 13 | 0 | 0 | 0 | 0 | 234 | 6 | 3 | 2 | 18 | 156 | 0 |
| clocked/KinkedCounter | 6 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 90 | 6 | 3 | 2 | 18 | 60 | 0 |
| clocked/Register | 19 | 13 | 13 | 0 | 0 | 1 | 13 | 0 | 0 | 0 | 0 | 624 | 19 | 7 | 4 | 48 | 494 | 0 |
| clocked/Clearer | 3 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 45 | 3 | 1 | 1 | 9 | 30 | 0 |
| clocked/Pawl | 7 | 5 | 0 | 5 | 0 | 1 | 5 | 5 | 0 | 1 | 0 | 95 | 7 | 4 | 3 | 22 | 70 | 0 |
| clocked/Stroke | 6 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 90 | 6 | 3 | 2 | 18 | 60 | 0 |
| clocked/ScaledStroke | 6 | 3 | 3 | 0 | 0 | 1 | 3 | 0 | 0 | 0 | 0 | 54 | 6 | 3 | 2 | 18 | 36 | 0 |
| clocked/Lock | 2 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 40 | 2 | 2 | 2 | 8 | 20 | 0 |
| clocked/Kinked | 1 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 20 | 1 | 1 | 1 | 4 | 10 | 0 |
| clocked/Freeze | 7 | 11 | 0 | 11 | 0 | 1 | 11 | 11 | 0 | 1 | 0 | 198 | 7 | 3 | 3 | 21 | 154 | 0 |
| clocked/Gate | 1 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 20 | 1 | 1 | 1 | 4 | 10 | 0 |
| clocked/Shut | 1 | 2 | 2 | 0 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 8 | 1 | 1 | 1 | 4 | 4 | 0 |
| clocked/SamePair | 1 | 3 | 3 | 0 | 0 | 1 | 3 | 0 | 0 | 0 | 0 | 12 | 1 | 1 | 1 | 4 | 6 | 0 |
| clocked/SwappedPair | 1 | 3 | 3 | 0 | 0 | 1 | 3 | 0 | 0 | 0 | 0 | 12 | 1 | 1 | 1 | 4 | 6 | 0 |
| clocked/JumpsOnly | 3 | 3 | 3 | 0 | 0 | 1 | 3 | 0 | 0 | 0 | 0 | 27 | 3 | 1 | 1 | 9 | 18 | 0 |
| clocked/Conflict | 1 | 2 | 2 | 0 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 8 | 1 | 1 | 1 | 4 | 4 | 0 |
| clocked/Calculator | 39 | 33 | 0 | 33 | 0 | 1 | 33 | 33 | 0 | 1 | 0 | 3102 | 39 | 13 | 9 | 99 | 2574 | 0 |
| running/OvertakenFollower#0 | 2 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 35 | 2 | 1 | 1 | 7 | 20 | 0 |
| running/NegativeFollower#1 | 2 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 35 | 2 | 1 | 1 | 7 | 20 | 0 |
| running/ObservedFollower#2 | 2 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 35 | 2 | 1 | 1 | 7 | 20 | 0 |
| running/FollowingContact#3 | 6 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 95 | 6 | 3 | 2 | 19 | 60 | 0 |
| running/StationaryFollower#4 | 2 | 5 | 5 | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 35 | 2 | 1 | 1 | 7 | 20 | 0 |
| running/PeriodicStop#5 | 1 | 4 | 4 | 0 | 0 | 1 | 4 | 0 | 0 | 0 | 0 | 20 | 2 | 2 | 1 | 5 | 8 | 0 |
| running/Window#10 | 1 | 25 | 25 | 0 | 0 | 1 | 25 | 0 | 0 | 0 | 0 | 100 | 1 | 1 | 1 | 4 | 50 | 0 |
| running/Wrapped#12 | 2 | 21 | 21 | 0 | 0 | 1 | 21 | 0 | 0 | 0 | 0 | 147 | 2 | 1 | 1 | 7 | 84 | 0 |
| running/Throwing#13 | 2 | 21 | 21 | 0 | 0 | 1 | 21 | 0 | 0 | 0 | 0 | 147 | 2 | 1 | 1 | 7 | 84 | 0 |
| running/Clutch#14 | 1 | 25 | 25 | 0 | 0 | 1 | 25 | 0 | 0 | 0 | 0 | 125 | 2 | 2 | 1 | 5 | 50 | 0 |
| running/CarryLead#15 | 8 | 25 | 0 | 25 | 0 | 1 | 25 | 25 | 0 | 1 | 0 | 425 | 8 | 4 | 3 | 22 | 400 | 0 |
| running/CarryLead#16 | 8 | 15 | 0 | 15 | 0 | 1 | 15 | 15 | 0 | 1 | 0 | 255 | 8 | 4 | 3 | 22 | 240 | 0 |
| running/StopAndJump#20 | 2 | 13 | 13 | 0 | 0 | 1 | 13 | 0 | 0 | 0 | 0 | 91 | 2 | 1 | 1 | 7 | 52 | 0 |
| running/Clearing#21 | 4 | 25 | 25 | 0 | 0 | 1 | 25 | 0 | 0 | 0 | 0 | 350 | 4 | 2 | 2 | 14 | 200 | 0 |
| running/Clearing#22 | 4 | 13 | 13 | 0 | 0 | 1 | 13 | 0 | 0 | 0 | 0 | 182 | 4 | 2 | 2 | 14 | 104 | 0 |
| running/StoppedClearing#23 | 4 | 17 | 17 | 0 | 0 | 1 | 17 | 0 | 0 | 0 | 0 | 238 | 4 | 2 | 2 | 14 | 136 | 0 |
| running/ShiftedCarry#24 | 4 | 21 | 21 | 0 | 0 | 1 | 21 | 0 | 0 | 0 | 0 | 231 | 4 | 2 | 2 | 11 | 168 | 0 |
| running/RangedBlock#25 | 3 | 9 | 9 | 0 | 0 | 1 | 9 | 0 | 0 | 0 | 0 | 72 | 3 | 1 | 1 | 8 | 54 | 0 |
| time-drive/TimeEnabled | 1 | 6 | 6 | 0 | 0 | 1 | 6 | 0 | 0 | 0 | 0 | 24 | 1 | 1 | 1 | 4 | 12 | 0 |
| time-drive/AstrariumClock | 1 | 21 | 21 | 0 | 0 | 1 | 21 | 0 | 0 | 0 | 0 | 84 | 1 | 1 | 2 | 4 | 42 | 0 |
| run/follow-wrapped-v12 | 4 | 16 | 16 | 0 | 0 | 1 | 16 | 0 | 0 | 0 | 0 | 160 | 4 | 1 | 1 | 10 | 128 | 0 |
| parity-fixture | 4 | 451 | 30 | 421 | 0 | 1 | 451 | 421 | 0 | 1 | 0 | 3307 | 4 | 3 | 2 | 12 | 4510 | 0 |


### 4.4 again: the whole suite under the self-check

`FLAT_PASS` edited in the source to `{ minimumBindings: 0, verify: true }`
for one `vitest run`, then restored (`cmp` equal to the saved
implementation; `git diff` shows the line as
`{ minimumBindings: 1_000, verify: false }`):

```
 Test Files  1 failed | 68 passed | 1 skipped (70)
      Tests  1 failed | 1870 passed | 2 skipped (1873)
```

No self-check mismatch anywhere ("The flat pass differs" absent from the
output). The one failure is W1, whose count moves only because the
self-check walks covered nodes: "W1: 1200 entries; the pose moving b: 3003
resolutions, 1 flat entries". The two skips are those of 5.2.

### 5.2 again: the gate

Whole widget suite with the shipped defaults:

```
 Test Files  69 passed | 1 skipped (70)
      Tests  1871 passed | 2 skipped (1873)
```

No failure. The two skips are the environment-gated ones named in 5.2
(`src/run/profile-contact.test.ts`, `src/run/profile-installed-benchmark.test.ts`).
`tsc --noEmit`: clean (exit 0, no output).

### 5.3 again: the cost tests

Both pass (14 of 14, 8 of 8); the figures are the third column of the
table in "2.3 and 5.3". Neither file poses a tree, so the flat pass is not
on their path; the differences from both earlier columns are those of
single runs.

### 5.4 again: the bundle and the Python suite

`npm run build`: `dist/machinome-viewer.js` 909.9 kb, SHA256
`b05d4caf97ddfdab9cc463417748da6e87264fff2a4deddf556f3f0b1d41f14a`.

The viewer's Python suite on the bench's venv, on that bundle: **284
passed, 2 skipped, 71 warnings in 285.38 s**, no failure. The skips are the
two of 5.4, for a missing project build (`tests/test_curta_drawing.py:375`
and `:469`); the warnings are Pillow `getdata` deprecations.

### Records

The CHANGELOG bullet of 8.1 is still true and is unchanged.
`proposal.md` still describes the first form of Decision 4 in two places
("A scope the program cannot serve (an input missing or not a number, a
driver named like a called function) is left to the walk for that pass",
and the expectation of "no declined pass" on the Enigma, which still
holds: a pose served in part is not declined); it is the reviewer's file
and was not edited.

## Reviewer's record: review of the implementation and task 7.2

Written by the repository agent, 21 November 2026, after the correcting agent
stopped with the work uncommitted.

### Review of the implementation (7.1)

Read against the design, as corrected: the two-phase run and its absent set
(`runFlatPass`), the served slot index and its view (`servedSlotIndex`), the
entry of a pose (`prepareFlatPass`), the one read added to `valueOf`, what a
reset drops, the list of twenty functions, and the two calls in `tree.ts`. The
argument that nothing is read stale was followed case by case through the
code: a segment over an absent input is neither run nor served; an input
supplied again is counted as changed by its absent bit before its value is
compared; a whole decline returns before any input is read. Run again by the
reviewer, one file at a time: `flat-pass.test.ts` 41 of 41, `tree.test.ts` 71
of 71, `flat-pass-parity.test.ts` 52 of 52, `expressions.test.ts` 88 of 88;
`tsc --noEmit` exit 0. A rebuild of the bundle from the final source gave the
SHA256 the correcting agent reports (`b05d4caf…1d41f14a`).

The bench's stash list shows two entries. They belong to the framework
repository, are shared by every worktree and predate this change; nothing here
made or touched them.

### 7.2 The Enigma I page

Project `enigma-i` at `081f4e6`, `_build-page/`, manifest SHA256
`a8769deec38e3fbf0dca2b826ef4b7779d29d2137ad7977e2f34ed9d58326fc0`. Same host
and method as `workflow/evidence/enigma-formula-evaluation-2026-11-20.md`
(headless Chromium, no GPU, draw calls counted and not executed, so script
only; a probe build of the bench's source with a handle on the scene and with
`WidgetTree.prototype.update`, `admit` and `FlexibleShape.prototype.evaluate`
wrapped; `FLAT_PASS` and `flatPassMetrics` placed on the page; each
instruction pressed by `element.click()`), and the built bundle for the press
tasks. Single runs. No page error in any of the four.

**The program on this page.** One compilation, at the load: 444,782 of the
546,768 nodes covered, 216,690 entries in 53 segments over 14 inputs. No
input is ever absent: every pose was served in full, none in part, none
declined, no failure, no view built. The walk's resolutions after the load
fell from 546,592 to 101,879.

**Self-check.** With `FLAT_PASS.verify` on, 55 poses over the seven
instructions compared 24,463,010 covered values with the recursive walk's.
A difference throws; none was thrown.

**Timed, one session, the pass off (`minimumBindings` set above the table) and
on:**

| Instruction (declared seconds) | Press task, ms | Script per changing frame, ms | Frames that changed the picture |
| --- | ---: | ---: | ---: |
| Key B (0), a different key | 152 → 67 | none | 0 |
| Press (2) | 176 → 120 | 197 → 108 | 10 → 20 |
| Release (2) | 166 → 91 | 188 → 109 | 11 → 18 |
| Right wheel on (0.4) | 108 → 29 | 34 → 47 | 1 → 1 |
| Right wheel back (0.4) | 106 → 27 | 35 → 50 | 1 → 1 |
| Open flap (1.5) | 7 → 7 | 25 → 30 | 53 → 45 |
| Close flap (1.5) | 6 → 6 | 27 → 28 | 50 → 48 |

In the same run's pass over the nine instructions of the originating evidence,
the pass on: Press 96 ms and 18 changing frames at 110 ms, Release 86 ms and
19 at 106 ms, the wheel steps 24 and 21 ms, a key selection 80 ms, the flap
and the hood 6 to 7 ms with 44 to 47 and 117 to 119 changing frames at about
30 ms, an idle frame 24 ms.

A Press's 22 runs computed 4,705,923 entries, about 214,000 a run; a flap's
47 runs computed 329, seven a run. With the built bundle (SHA256
`b05d4caf…1d41f14a`): press tasks of 105 and 83 ms (Press, Release), 30 and
26 ms (the wheel steps), 75 and 69 ms (a key selection), 6 to 9 ms (flap and
hood).

### The expectations of task 7.2

Met: no mismatch, no declined pass, no failure; one compilation, at the load;
a Press's formula evaluation a few milliseconds a run where the walk took
about 100; a flap frame's run a handful of entries.

Read with their limits. The wheel step's and the flap's per-frame figures
moved the wrong way by amounts inside the differences seen between two runs
of one configuration (a tenth and more), on one changing frame for the wheel;
neither is counted as a cost of the pass, and neither is ruled out as one by
these runs. The first press after mounting, a key already selected, took
557 ms with the built bundle, as it did before this change (593, 638 and
628 ms on the three earlier bundles); it is still unexplained and is not the
compilation, which happens at the load.

What is left of a Press frame, about 108 ms: about 60 ms in the flexible
evaluations (the seven parts rebuilt and their parameters) and the rest in
the transforms and the renderer's bookkeeping.

**Acceptance.** Accepted.

**Not measured.** The program's own memory on this page (the page's heap read
2,006 MB against 1,961 to 1,968 MB on earlier bundles, a difference inside
what those readings vary by); the compilation's own time on this page; any
GPU's frame time; a browser other than Chromium; a second document on the
page; the Curta exports in a browser.

### Final gate

Run by the reviewer on the finished state, after the archive and with it
staged, one at a time.

- Whole widget suite: 70 files, 69 passed and 1 skipped; 1,873 tests, 1,871
  passed, 2 skipped (the two environment-gated Curta files), 0 failed;
  52.3 s.
- `tsc --noEmit`: exit 0. The bundle's SHA256 is unchanged
  (`b05d4caf…1d41f14a`).
- Python suite: 284 passed, 2 skipped, 0 failed, 217 subtests, 281 s. Both
  skips are `tests/test_curta_drawing.py` (lines 375 and 469): the Curta's
  own builds are not on this bench.
- `openspec validate --specs --strict`: 16 passed, 0 failed.
