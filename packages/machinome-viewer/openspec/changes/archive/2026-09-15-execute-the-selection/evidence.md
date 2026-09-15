# Evidence — execute-the-selection

Every run below was made in the cycle worktree
`solid-node-viewer/WTs/execute-the-selection`, on branch
`execute-the-selection`, off viewer main `fff31e4`, on the planning
commit `1911bdd`. `solid_node_viewer/widget/node_modules` is the main
checkout's, reached through a symlink; no `npm ci` and no `npm install`
was run.

The framework side this cycle consumes is solid-node branch
`select-the-source` at commit `0b0f02a`, read-only at
`/home/asa/devel/libresolid-studio/solid-node/WTs/select-the-source`.
Everything exported from a throwaway copy was exported from
`git archive 0b0f02a | tar -x` under the scratchpad, never from the
pilot's checkout.

## 0. The baseline, re-measured before anything was written

### 0.1 The base

```text
$ git rev-parse --show-toplevel
/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/execute-the-selection
$ git log --oneline -2
1911bdd openspec(execute-the-selection): propose ordering a block per piece from the published edges
fff31e4 feat(run): execute a law that reads the coordinate it drives; API 15; ADR-057
$ ls -la solid_node_viewer/widget/node_modules
node_modules -> /home/asa/devel/libresolid-studio/solid-node-viewer/solid_node_viewer/widget/node_modules
```

`solid_node_viewer/widget/package.json` on the base: `"version": "0.2.0"`,
`"solidNodeViewerApi": 15`, `"solidNodeDocumentVersions": [1,2,3,4,5,6]`.

`npm test` on the base:

```text
 Test Files  36 passed (36)
      Tests  869 passed (869)
   Duration  34.25s
```

### 0.2 The corpus gap

```text
$ md5sum solid-node/WTs/select-the-source/tests/running-corpus.json
c682b7f2c70bc7ef4f29a610ecfa8cb5
$ md5sum solid_node_viewer/widget/src/running-corpus.json
0ba7939ad5b5988f739aa114a26ab464
```

committed: 17 scenarios, 14 machines, 328 ticks; framework: 19, 16, 356.
Added `('ShiftedCarry', 0.05, 20)` and `('RangedBlock', 0.05, 8)` before
`Captured`; removed none; changed none.

## 1. The corpus, red first

### 1.2 The census, RED before the file was replaced

The census was raised to 19/16/356 with the OLD file still in place:

```text
$ npx vitest run src/run/running-corpus.test.ts -t "unedited"
 FAIL  src/run/running-corpus.test.ts > the running corpus > is the
   framework's own fixture, unedited
   - 19
   + 17
 Test Files  1 failed (1)
      Tests  1 failed | 19 skipped (20)
```

### 1.1 The file, copied byte for byte

```text
$ cp .../solid-node/WTs/select-the-source/tests/running-corpus.json \
     solid_node_viewer/widget/src/running-corpus.json
$ md5sum solid_node_viewer/widget/src/running-corpus.json
c682b7f2c70bc7ef4f29a610ecfa8cb5  (the framework's own md5)
```

### 1.3 The replay suite with the new file and the OLD engine

Exactly one of the nineteen is red, and it is the one the design
predicted:

```text
 ✓ replays ShiftedCarry at dt=0.05 (scenario 17) 8ms
 × replays RangedBlock at dt=0.05 (scenario 18) 6ms
   → RangedBlock at dt=0.05, tick 1, the number of crossings:
     expected 3, got 2
 ✓ replays Captured at dt=0.05 (scenario 19) 4ms
 Test Files  1 failed (1)
      Tests  1 failed | 21 passed (22)
```

### 1.4 The width guard, RED with the three features and no detection

```text
$ npx vitest run src/run/running-corpus.test.ts -t "width"
 FAIL  the corpus's width > exercises every feature the producer's
   generator requires
   - []
   + [ "a switched source",
       "a selection crossing inside a tick",
       "a tick carrying both a selection crossing and a stop" ]
```

### 1.5 The detection, mirrored from the generator

`selectionOf` and `memberOf` in `running-corpus.test.ts` mirror
`tools/generate_running_corpus.py`'s `_selection` and `_member_of`,
read through the guard's own `freeNamesOf` and never through
`loadProgram`. Green over the new corpus, and measured over the OLD one
(a throwaway copy imported into a scratch test, deleted after the run):

```text
OLD corpus uncovered -> ["a switched source",
                         "a selection crossing inside a tick",
                         "a tick carrying both a selection crossing and a stop"]
NEW corpus uncovered -> []
```

### 1.6 The narrowed-corpus test names one of the three

`Train` alone leaves `a selection crossing inside a tick` uncovered, and
the trimmed test now asserts it beside the self-read's three.

## 2. The walk's own arithmetic (design D5)

### 2.1 RED, on a VERSION 6 document with no block anywhere

`heldAngle()` in `jumps.test.ts` is the producer's `HeldAngle` shape:
`setter + ring * (wheel > 0.5) * (lift < 0.5)`, setter standing at
`72.0`, ring at `0.0`, the dial resting at `71.99999999999996`, the lift
moved alone by `0.2` over one tick. The dial's own comparison is the
DEPENDENT node and the lift's the independent one (asserted), so the
piece is re-partitioned while every term of the substituted law stands
where it stood.

```text
HELD increment -1.4210854715202004e-14  committed 71.99999999999994
 FAIL  2.1 a piece whose SKELETON does not move leaves the coordinate at
   the exact float it held
   expect(Object.is(increment, 0)).toBe(true)  ->  false
```

### 2.2 The parenthesisation

`Walk.run`'s `ownAt` closure and `Walk.probe` now compute
`ownLeft + (S − base)`. Nothing else in the walk changed.

### 2.3 GREEN, and the seventeen pre-existing scenarios still green

```text
$ npx vitest run src/run/jumps.test.ts
 Test Files  1 passed (1)
      Tests  49 passed (49)

$ npx vitest run src/run/running-corpus.test.ts
 ✓ scenarios 1-17 and 19        × scenario 18 (RangedBlock), unchanged
      Tests  1 failed | 21 passed (22)
```

The producer regenerated the corpus AFTER this fix and every
pre-existing entry is byte-identical, so the seventeen staying green
over the new file is the regression test for it.

## 3-5. The block, its selectors and the load-time refusals

### RED first, measured

The seventeen new load-time tests were written against the finished
loader and then measured RED by DISABLING the two things they are about
— the contraction (`if (component.length < 2 || true) continue;`) and
the order verification (`if (false && source !== undefined …)`) — and
restoring them afterwards. Nothing else changed:

```text
$ npx vitest run src/run/program.test.ts       # contraction disabled
 FAIL 3.2 a CHECK edge is never in a component …
      → expected [ 'law', 'law', 'check' ] to deeply equal [ 'block', 'check' ]
 FAIL 3.2 `ShiftedCarry` and `RangedBlock` each produce exactly the pair …
      → expected [] to have a length of 1 but got +0
 FAIL 3.3 the component is contracted IN PLACE at its first member …
      → expected […] to have a length of 2 but got 3
 FAIL 3.4 the published order is VERIFIED and never re-sorted …
      → expected loadProgram to refuse this document
 FAIL 3.5 a block whose members are published NON-CONTIGUOUSLY …
 FAIL 4.2 / 4.3 / 4.4 / 4.5 (five)  → Cannot read properties of null
                                       (reading 'members')
 FAIL 5.1 wiring / 5.1 formula / 5.2 group / 5.3 not a bank coordinate /
      5.4 a cycle no selection breaks / 5.5 the four at load
      → expected loadProgram to refuse this document  (six)
      Tests  17 failed | 73 passed (90)

$ npx vitest run src/run/program.test.ts       # restored
      Tests  90 passed (90)
```

Task 3.1's test — a document PUBLISHING `kind: "block"` still refused as
an unknown kind — is a NON-regression guard on `EDGE_KINDS`, which the
cycle deliberately leaves alone; it is green on the base and stays green.

### What the derivation finds on the framework's own documents

`ShiftedCarry` and `RangedBlock` each produce exactly ONE nontrivial
component, `{higher.turn, carry.travel}` — ADR-122's evidence group 8's
own answer. `ShiftedCarry`'s three published law edges become TWO
entries: the lower wheel's own law, then the block at the index its first
member held, with

```text
needs        crank, shift, clearing, carry.travel, higher.turn, lower.turn
gives        higher.turn, carry.travel
description  "… drives higher.turn; … drives carry.travel"
statedBy     ShiftedCarry           (de-duplicated in order)
affine       [false, false]
determiner   higher.turn -> {block, 0};  carry.travel -> {block, 1}
```

The fold, on the corpus's own `ShiftedCarry` document (task 4.2's
numbers, which are the producer's `spikes/fold.py` numbers):

| member | substitution | reads |
| --- | --- | --- |
| the lever (`carry.travel`) | `{}` | `carry.travel, higher.turn, lower.turn, shift` |
| the lever | `_j7 = 0` (its `shift >= 0.5`) | `carry.travel, lower.turn, shift` |
| the wheel (`higher.turn`) | `{}` | `carry.travel, clearing, crank, higher.turn, shift` |
| the wheel | `_j3 = 0` (the complementary `<`) | `clearing, crank, higher.turn, shift` |

`unconditional` is empty for both members and `switched` is
`{carry.travel}` and `{higher.turn}` — so nothing is left on the cycle
once the selectors fold, which is why the document loads.

### A DEVIATION from design D1.5, and why

D1.5 says the fold takes "the folded skeleton's names … closing each
through the bindings table" — the closure AFTER the fold. Implemented
that way a binding that CARRIES a placeholder stops the zero at the
binding's name, and the producer's `_folded` (which runs on the
unbound compiler graph) propagates it. That shape is real and published:
`CarryLead`'s own table holds

```json
{ "name": "_b6", "expression": "(360.0 * _j0)" }
```

So `foldedNames` resolves a binding name by walking INTO the binding's
own DAG root instead, which is `_reads_under` exactly — the design's
stated intent ("`_reads_under` exactly", and "where the TypeScript and
`program.py` disagree, `program.py` is right"). The two readings agree
wherever a binding carries no placeholder and no foldable zero, which is
every binding on the corpus's block machines; the difference is that the
implemented one cannot over-approximate a member's reads and so cannot
invent an unconditional cycle. Recorded here rather than silently taken.

## 6-9. The block's step, the forced branch, and what it reports

### The producer's own negative controls, mirrored

| what | the producer measured | this viewer |
| --- | --- | --- |
| the in-block value NOT advanced between pieces | three pieces of one stretch sum to `2.0` where the whole stretch gives `1.0` | `expect(unadvanced).toBe(2)` beside `expect(total).toBe(1)`, the crossing rescaling to exactly `0.5` either way (`jumps.test.ts` 6.6) |
| the block reporting the LAST landing | `AssertionError: 1.0 != 3.0` | `LandedCarry`'s shape at `crank 4`, `shift 0 -> 1`: the block reports `carry.travel 3`, and the SAME stretch truncated at the detent reports `1` — the landing alone (`jumps.test.ts` 8.1) |
| forcing removed from `_partition` | `[Crossing(…, t=0.5)] != []` | unforced the lever locates `['<', 0, 0.5]`; forced it locates `[]` (`jumps.test.ts` 7.4) |
| forcing removed from `_branches` | `0.0 != 1.0` | `{_j3: 1, _j5: 0}` gives `1`, `{_j3: 0, _j5: 1}` gives `0` (`jumps.test.ts` 7.2) |

### The run-time refusal, word for word

`BothActive`'s shape driven past its detent:

```text
UnsupportedLaw: over the piece [0.5, 1] of this tick the relations
(crank, shift, higher.turn) drives lower.turn, (crank, shift, lower.turn)
drives higher.turn form a cycle the run cannot order: each waits on a
coordinate another determines, and the selection this piece was read under
leaves every dependency on this cycle active. The selectors read
lower.turn: >= on (shift - 0.5) reads 1; higher.turn: >= on (shift - 0.5)
reads 1. The tick committed nothing: the bank, the tick count and the tree
stand as they were.
```

The WORDS are the producer's; the floats are this runtime's (`0.5, 1`
where Python's `repr` writes `0.5, 1.0`, and `reads 1` where it writes
`reads 1.0`), exactly as design D2.4 and risk 3 anticipated. Below the
detent the same stretch orders and gives `[['lower.turn', 1],
['higher.turn', 1]]`. `refusalKind` answers `'law'`, so `RefusalKind`
gains nothing.

### The memo is keyed by the branch VALUE vector

A `floor` selector on an input swept `0 -> 3.5` makes FOUR pieces, four
distinct keys and eight `activeReads` calls (two members each), with the
`floor` branch reading `0, 1, 2, 3` in turn — not one key and not one
call.

### The order FLIPS with the selection

On the detent bench, `crank 2` with `shift 0 -> 1`, the vectors the
ordering was asked for, in order:

```text
{"_j0":1,"_j1":0}  {"_j2":1}      piece one, below the detent
{"_j0":0,"_j1":1}  {"_j2":0}      piece two, above it
```

and the increments are `higher.turn 1`, `carry.travel 1`: the wheel
carries the lever below the detent, and above it the lever runs FIRST and
moves by nothing.

### 6.2's crossing count, which is ADR-107's and not a defect

The detent bench's first member carries `<` and `>=` on the SAME surface.
Once the `<` has cut the path at `0.5` the `>=` is asked over `[0, 0.5]`
and `[0.5, 1]`, where `surfacesOf(..., inclusive = false)` does not count
a surface a piece begins or ends on — so the selector partition reports
TWO crossings, not three. That is `partition` reached unchanged, the
producer's own behaviour, and the test says so.

### 9.1-9.3 The framework's own numbers

- **9.1** the corpus's own `ShiftedCarry` document at `dt = 1.0` cranked
  by `2.0` in one tick commits `lower.turn 2.0`, `higher.turn 1.0`,
  `carry.travel 1.0` — and does so with the two block members EXCHANGED
  in the published listing, which is what the base could not do (task 0.4
  measured `0` and `1`).
- **9.2** `ShiftedCarry` cranked by `2.0` over 12 ticks of `dt = 1/12`,
  the bank started at `shift = 0` and at `shift = 1`:

  | coordinate | `shift = 0` | `shift = 1` |
  | --- | --- | --- |
  | `crank` | `2.0` | `2.0` |
  | `lower.turn` | `2.0` | `0.0` |
  | `higher.turn` | `1.5` | `2.0` |
  | `carry.travel` | `1.0` | `1.0` |

  asserted BIT FOR BIT. **A deviation from task 9.2's stated floats, with
  its reason**: the task quotes `1.9999999999999998` /
  `1.4999999999999998`, which are the producer's numbers for
  `spikes/reduced.py`'s variant of the fixture, not for the
  `tests/carriage_project/machine.py` machine the corpus publishes. Run
  on the SAME document the viewer executes, the producer at `0b0f02a`
  gives the clean floats above:

  ```text
  $ PYTHONPATH=<throwaway 0b0f02a>:<…/tests> python -c "…
      Sim(ShiftedCarry(), dt=1/12, state={'shift': s});
      move('crank', by=2.0, duration=1.0); run(1/12) x 12"
  shift 0.0 completed {"carry.travel": 1.0, "clearing": 0.0, "crank": 2.0,
                       "higher.turn": 1.5, "lower.turn": 2.0, "shift": 0.0}
  shift 1.0 completed {"carry.travel": 1.0, "clearing": 0.0, "crank": 2.0,
                       "higher.turn": 2.0, "lower.turn": 0.0, "shift": 1.0}
  ```

  The two runtimes agree exactly, which is the claim the table was making.
- **9.3** a selection change alone moves nothing: cranked, then shifted
  across the detent and back, `lower.turn`, `higher.turn` and
  `carry.travel` are `Object.is`-identical to what they were.

### 8.2 and 8.4 in the run

`RangedBlock`, `spin` by `2.0` and `shift` by `1.0` in one tick of
`dt = 0.05`: the stop on `carry.travel` is located at
`t = 0.29999999999972715` naming `spin`, and `lower.turn` and `spin`
commit `0.5999999999994543` — the producer's floats, which the piecewise
path commits as `0.3` and `0.6`. The determination really is the block,
with `affine[index] === false`.

With the carriage standing ABOVE the detent and the lever already at its
bound, `spin` reaches the lever only through the term the selection has
switched out: it completes its whole `2.0` and no stop is recorded, while
`crank` — which reaches it through the term the selection leaves active —
retires `blocked` with `0.0` admitted and the stop names `['crank']`.
That is `Run.pushes`'s break reading the BLOCK's union of gives, which is
what design D4.6 is about.

### 8.5 `run.ts` has no structural change

```text
$ git status --short
 M solid_node_viewer/widget/src/expressions.ts
 M solid_node_viewer/widget/src/run/edges.ts
 M solid_node_viewer/widget/src/run/jumps.ts
 M solid_node_viewer/widget/src/run/program.ts
 M solid_node_viewer/widget/src/running-corpus.json
 (+ the four test files and the change's own artifacts)
```

`src/run/run.ts` is not in the diff at all.

## 10. The corpus, green

```text
$ npx vitest run src/run/running-corpus.test.ts
      Tests  22 passed (22)          # 19 scenarios + census + two guards
```

All nineteen replay green, exactly for discrete state and within the
corpus's own `1e-9` relative window for floats. The width guard is green
on the new file, red on the old one (measured above) and red on the
trimmed one.

## 11. Versions (design D7)

RED first, with `version.test.ts` raised before `package.json` was:

```text
$ npx vitest run src/version.test.ts
 × API_VERSION > declares the selection API as version 16
   → expected 15 to be 16
 × DOCUMENT_VERSIONS > is declared in package.json …
   → expected [ 1, 2, 3, 4, 5, 6 ] to deeply equal [ 1, 2, 3, 4, 5, 6, 7 ]
      Tests  2 failed | 4 passed (6)
```

then green with `solidNodeViewerApi: 16`,
`solidNodeDocumentVersions: [1,2,3,4,5,6,7]` and `RENDERED_VERSIONS`
following it — pinned equal by the existing "is exactly what the loader
refuses by" test.

- The spec scenario's refused version moves 7 → 8, and with it
  `document.test.ts`'s "refuses a version it does not render" (now
  `\b8\b` and `1, 2, 3, 4, 5, 6, 7`) and the program-carrying suite,
  which now ACCEPTS a version 7 document and refuses a version 8 one.
- `bundle.py`'s `RELEASED_DOCUMENT_VERSIONS` did NOT move; a new test
  asserts `describe()['documentVersions']` is the package's own list
  (`[1,2,3,4,5,6,7]`) and still not equal to the released floor.
- `capture.py`'s `carries_program` did NOT move — the test now asserts
  it admits version 7 AND version 8, so the claim is a test and not a
  reading — and `viewer.ts`'s program gate did not move either: a
  version 7 document with NO program meets the program refusal, not the
  treeful path.

## 12. The Curta's carriage, in a real browser

### 12.1 The export, and that the one changed import moves nothing

The throwaway copy is `git archive 0b0f02a | tar -x` under the
scratchpad. Its one difference from the commit is the line design D10
names:

```text
$ diff <(git -C solid-node show 0b0f02a:tests/carriage_project/machine.py) \
       <throwaway>/tests/carriage_project/machine.py
39c39
< from ..running_project.parts import Arbor, Block, Carriage as Slide
---
> from running_project.parts import Arbor, Block, Carriage as Slide
```

That it changes nothing was checked, not assumed:

```text
# the READ-ONLY worktree at 0b0f02a
$ pytest tests/test_running_selection.py -q
39 passed, 4 subtests passed in 3.19s

# the throwaway copy
$ pytest tests/test_running_selection.py tests/test_running_stops.py -q
107 passed, 32 subtests passed in 5.05s

# and the PUBLISHED PROGRAM, compared between the two copies
$ diff carriage-worktree.json carriage-throwaway.json
823c823
<  "identity": "d69d52118f007a91f8a658a391759098e513cdbd4513126d98ec5f648bfbbba4"
---
>  "identity": "917094ae7e0629ed26e139086cca7c55f4777258e80f8b003f8cf0c4afa89572"
$ diff <(grep -v identity …worktree…) <(grep -v identity …throwaway…)
IDENTICAL apart from identity
```

`identity` takes in the module path, which is the line that changed.

### 12.2 The committed fixture

`tests/fixtures/carriage/viewer.json` is the exported `manifest.json`
renamed, byte for byte: **32,791 bytes, `md5
1598d57e18f772315183a7e466123a39`**, version 7, five drivers, fourteen
coordinates all at `0.0`, thirty-five bindings, no intermediates, a
`seat` span both of whose sides are expressions, nine law edges of which
seven form one block. Beside it the two meshes the document names, which
`solid export` wrote from the machine's own geometry. `tests/support.py`
gains `CARRIAGE` and `published_carriage`. Its README records the
commit, the command, the byte count, the md5, the machine and the
import check above.

### 12.3-12.6 The acceptance

```text
$ PYTHONPATH="$PWD" .venv/bin/python -m pytest tests/test_carriage_document.py -v
CarriageFixtureTest::test_every_model_path_resolves_beside_the_document  PASSED
CarriageFixtureTest::test_seven_of_its_nine_law_edges_form_ONE_block     PASSED
CarriageFixtureTest::test_the_document_is_the_framework_s_own_machine    PASSED
CarriageFixtureTest::test_the_seat_span_reads_another_coordinate_...     PASSED
CarriageInABrowserTest::test_a_cyclic_piece_refuses_the_tick_in_the_page PASSED
CarriageInABrowserTest::test_the_carriage_carries_and_a_shift_...        PASSED
CarriageInABrowserTest::test_the_interlock_refuses_a_shift_while_...     PASSED
7 passed in 5.08s
```

and what the page reported, at the framework's own `dt = 0.02`, driven
only by the document's own declared drivers:

```text
the Curta carriage in a browser: runsInWorker=True
  carried: dial0 36, dial1 36, dial2 72, dial3 72, lever0 1, lever1 1,
           lever2 1, seat 20
  shifted: every dial and every lever BIT-IDENTICAL, seat 40
  reset:   lever0/1/2 1.1102230246251565e-16, dial3 72
  again:   dial2 107.99999999999999, dial3 144.00000000000006
  crossings: 51, stops: 0
```

Every number is the framework's own, the levers' resting
`1.1102230246251565e-16` — the residue of adding a tenth ten times, a
reading taken ON a surface and therefore outside the exact promise —
included.

The INTERLOCK: with the carriage DOWN and lever 0 standing at `1.0`, the
same shift retires `[['position', 'blocked', 0.0]]`, `seat` stands at
`20.0`, the stop names `coordinate seat` and `inputs ['position']`, and
no dial or lever moved.

The REFUSAL reaching the page: the producer's `BothActive` shape, served
as a hand-written version 7 document beside the fixture, orders below the
detent (`lower.turn 1.0`, `higher.turn 1.0`) and, driven past it, puts
into the page's own `.run-refusal` line

```text
over the piece [0.5, 1] of this tick the relations … form a cycle the run
cannot order: … the selection this piece was read under leaves every
dependency on this cycle active. … The tick committed nothing …
```

with the bank and the tick count standing where they stood.

### 12.7 Screenshots

```text
tests/_shots/curta-carriage-at-rest.png    36,578 bytes
tests/_shots/curta-carriage-carried.png    36,865 bytes
```

(`/tests/_shots` is gitignored in this repository — the pixels are
regenerated by running the test, as the clearing acceptance's are.)

## 13. What it costs (design D9)

Measured on this bench, one job at a time, beside the numbers already
there. The ABSOLUTE numbers are this runtime's; the RATIOS are what this
cycle records.

```text
  ShiftedCarry, a quiet block tick: 20000 ticks in 4.552 s =  4394 ticks/s
  ShiftedCarry, the frozen twin:    20000 ticks in 2.825 s =  7079 ticks/s
  ShiftedCarry, a crossing tick:     4000 ticks in 1.920 s =  2083 ticks/s
  a quiet block tick costs 1.6x the same laws with the carriage frozen,
  and a crossing tick 2.1x a quiet one (the producer measured 1.6x and 2.0x)

  the Curta carriage at dt = 0.02:   2000 ticks in 7.142 s =   280 ticks/s
  RangedBlock, a quiet tick (restored):  400 ticks in 0.014 s = 28897 ticks/s
  RangedBlock, a SEARCHED stop (restored): 400 ticks in 1.503 s = 266 ticks/s
  a searched stop costs 108.6x a quiet tick of the same machine

  the Pascaline at dt = 1/240:       2400 ticks in 0.060 s = 39992 ticks/s
```

- **1.6x and 2.1x against the producer's 1.6x and 2.0x.** The frozen twin
  is built from the producer's own published document by substituting
  each selector's branch at `shift = 0`, dropping the need a switched-out
  term named, and publishing the three edges in the order they then run
  in — which is the producer's `FixedZero`, and which the loader's own
  order check forced (it refused the cycle's listing order for the
  acyclic twin, by name, exactly as designed).
- **The Curta carriage at 280 ticks/s** is 3.6 ms/tick for one block of
  seven, against the producer's 10.658 ms/tick.
- **The searched stop is 108.6x its control**, where the producer
  recorded 22x. The two controls are different: this one is a quiet tick
  of `RangedBlock` replayed from the same snapshot with almost no motion
  (0.034 ms), so the ratio is larger than one taken against a busier
  quiet tick. The number that matters is the absolute one: 3.8 ms for a
  searched stop on a two-member block.
- **The control does not move.** The Pascaline reads 39,992 ticks/s where
  the base bench read 38,463 — inside this host's run-to-run spread.
  `Train`, which carries no block, reads 177,353 against the base's
  185,910, likewise.

## 14. The whole suite, and the build

| | base (`fff31e4` + planning) | after |
| --- | --- | --- |
| `npm test` | 36 files, **869** tests, 34.25 s | 36 files, **922** tests, 51.48 s |
| `npm run typecheck` | clean, exit 0 | clean, exit 0 |
| `npm run build` | `dist/solid-widget.js` **702.5 kb** (719,398 bytes) | **723.9 kb** (741,244 bytes) |
| Python suite | (not re-run on the base) | **129 passed**, 12 subtests, 115.55 s |

```text
$ PYTHONPATH="$PWD" .venv/bin/python -m pytest tests -q
129 passed, 53 warnings, 12 subtests passed in 115.55s

$ PYTHON=.venv/bin/python ./scripts/check-dist
{"path": …/solid-widget.js, "index": …, "apiVersion": 16,
 "documentVersions": [1, 2, 3, 4, 5, 6, 7], "version": "0.2.0"}
check-dist: wheel installs clean and carries the bundle (API 16, version 0.2.0).
check-dist: uploads nothing. Publishing waits for the maintainer's explicit go.
```

(`dist/` and `build/` that `check-dist` leaves at the repository root
were removed afterwards; both are gitignored.)

### 14.3 is not doable as stated, and is left undone

The task says to commit the rebuilt `dist/solid-widget.js` "as the
previous cycles committed theirs". They did not:

```text
$ git log --oneline -- solid_node_viewer/widget/dist
(nothing)
$ git check-ignore -v solid_node_viewer/widget/dist
.gitignore:19:/solid_node_viewer/widget/dist
```

The bundle is gitignored in this repository and has never been tracked.
It IS rebuilt (723.9 kb) and every Python suite above ran against the
rebuilt one; there is simply nothing to stage.

## Deviations from the design, and why

1. **The fold resolves a BINDING inside the traversal**, where design
   D1.5 closes the folded names through the bindings table afterwards.
   Recorded in full under §3-5 above. Reason: a binding may CARRY a
   placeholder (`CarryLead`'s `_b6 = (360.0 * _j0)` is published today),
   and closing afterwards would leave that zero unpropagated and
   over-approximate a member's reads. `_reads_under` is what the design
   says the function is.
2. **Task 9.2's floats are restated from the same document.** The task
   quotes `1.9999999999999998` / `1.4999999999999998`, which are the
   producer's numbers for `spikes/reduced.py`'s variant of the fixture.
   Run on the document the corpus publishes and this viewer executes, the
   producer at `0b0f02a` gives `2.0` / `1.5` / `1.0` and `0.0` / `2.0` /
   `1.0`, and this viewer gives the same floats bit for bit. The
   producer's run is quoted under §6-9.
3. **Task 12.6's refusal is read off the page's own run chrome**, not off
   a handle callback: `RunHandle` exposes `onCommit` and `onOutcome` and
   no `onRefusal`, so a host sees a refusal exactly where the viewer puts
   it — the `.run-refusal` line the run panel builds. The test asserts
   that line's text, that it was hidden before, and that neither the bank
   nor the tick count moved. No API was added for the test.
4. **Task 6.2's selector partition reports TWO crossings, not three.**
   The bench's first member carries `<` and `>=` on the same surface, and
   `surfacesOf(..., inclusive = false)` does not count a surface a piece
   begins or ends on once the first has cut the path there. That is
   ADR-107's own partition, reached unchanged; the test says so rather
   than asserting a number the algorithm does not produce.
5. **The frozen-twin cost baseline is built in the test** by substituting
   the selectors' branches into the producer's own published document,
   rather than by exporting `FixedZero`. Recorded under §13, together
   with the fact that building it exercised the loader's order check.

## Design contradictions found while applying

None of the ratified design's DECISIONS was contradicted by the code.
Deviation 1 above is a contradiction between the design's PROSE (the
closure taken after the fold) and `program.py`'s `_reads_under`, resolved
the way the common briefing says to resolve it — `program.py` is right —
and recorded rather than silently taken.

## Left for the reviewer

- `docs/adrs/EXPORT/ADR-058-a-block-is-ordered-per-piece-from-the-published-edges.md`
  and the `docs/adrs/README.md` row (task 15.3).
- Syncing the delta spec into `openspec/specs/viewer-package/spec.md` and
  archiving the change under its dated name (task 15.5's second half).
- Task 14.3, which is not doable as stated (above).

## Follow-ups recorded

1. **The corpus still does not discriminate the ordering.**
   `ShiftedCarry` replays green under either published order of its two
   block members (measured on the base, task 0.3). The gap is the
   PRODUCER's to close — a script whose latch crosses its threshold
   strictly inside a tick would discriminate — and this cycle's
   order-sensitive evidence is the one-tick table (task 9.1, asserted
   under both orders here) and the Curta acceptance.
2. **A block give classified as affine under a fixed branch vector.**
   Recorded on both sides. `blockCuts` is already defined for the day it
   lands; `edgeCuts` reaches it only through the affine path, so nothing
   calls it today.
3. **ADR-113's one-input pushing probe cannot see a push that needs two
   inputs moving together.** Pre-existing, inherited, not lifted.
