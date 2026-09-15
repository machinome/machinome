## 0. Before anything else

- [x] 0.1 The base, recorded. Worktree
      `solid-node-viewer/WTs/execute-the-selection`, branch
      `execute-the-selection`, base viewer main `fff31e4` (package
      `0.2.0` unreleased, `solidNodeViewerApi: 15`,
      `solidNodeDocumentVersions: [1, 2, 3, 4, 5, 6]`, highest ADR 057 in
      `docs/adrs/EXPORT`). Measured in that worktree, one job at a time:

      ```text
      $ npm test         →  Test Files  36 passed (36)
                            Tests  869 passed (869)      35.06 s
      $ npm run typecheck →  clean (tsc --noEmit, exit 0)
      $ npm run build     →  dist/solid-widget.js  702.5kb   (719,398 bytes)
      ```

      `solid_node_viewer/widget/node_modules` is a SYMLINK to the primary
      checkout's: never run `npm install` or `npm ci` here.
- [x] 0.2 The corpus gap, measured against the framework's file at
      `0b0f02a` before anything is written. Committed copy: 17 scenarios,
      14 machines, 328 ticks. Framework: 19, 16, 356. Added
      `('ShiftedCarry', 0.05, 20)` and `('RangedBlock', 0.05, 8)`,
      inserted before `Captured`; removed none; **changed none** —
      every pre-existing scenario byte-identical, `generated_by`,
      `corpus` and `tolerance` equal.
- [x] 0.3 The framework's file replayed through the shipped engine on the
      base, scenario by scenario. **Exactly one fails:**

      ```text
      × replays RangedBlock at dt=0.05 (scenario 18)
        → RangedBlock at dt=0.05, tick 1, the number of crossings:
          expected 3, got 2
      ```

      and the same tick also commits `spin` and `lower.turn` at `0.6`
      against the producer's `0.5999999999994543`, the stop at `t = 0.3`
      against `0.29999999999972715`, and `h0` admitted `0.6` against
      `0.5999999999994543`. `ShiftedCarry` replays GREEN — and so it does
      with its two block members EXCHANGED in the published listing,
      which is the measurement that says the scenario does not
      discriminate the ordering at all.
- [x] 0.4 What the base actually does with a block, measured on the
      corpus's own `ShiftedCarry` document at `dt = 1.0`, cranked by
      `2.0` in one tick: `higher.turn = 0` under the published listing
      and `1` under the reversed one, against the producer's `1.0`
      (`Sim(ShiftedCarry(), dt=1.0)` in a throwaway copy of solid-node at
      `0b0f02a`). Silently: no refusal, no crossing, no stop.
- [x] 0.5 The width guard, measured. The existing `REQUIRED` is satisfied
      by BOTH corpora, so nothing is red until it gains the producer's
      three. A JavaScript spike of the generator's own
      `_selection`/`_member_of` re-derivation
      (`scratchpad/viewer-spikes/selection-spike.ts`) finds, on the
      framework's file, the blocks `{higher.turn, carry.travel}` for both
      new machines with selector primitives `{<}` and `{>=}`, and reports
      the three features COVERED; over the committed file, all three
      UNCOVERED.
- [x] 0.6 The producer's own refusal of this viewer, reproduced.
      `solid export tests/carriage_project/machine.py:CurtaCarriage` from
      a throwaway copy at `0b0f02a` writes a 32,791-byte version 7
      `manifest.json` (`md5 1598d57e18f772315183a7e466123a39`) and warns
      "this model needs document version 7, and the installed browser
      viewer renders 1, 2, 3, 4, 5, 6".

## 1. The corpus, red first

- [ ] 1.1 Copy the framework's `tests/running-corpus.json` at `0b0f02a`
      over `solid_node_viewer/widget/src/running-corpus.json`, BYTE FOR
      BYTE. Nothing here edits it, ever.
- [ ] 1.2 Update the census in `run/running-corpus.test.ts`: 19
      scenarios, 16 unique machines, 356 ticks. RED first (the assertion
      must fail on the old file before the new one is in place), then
      green for the census alone.
- [ ] 1.3 Record the replay suite's state with the new file and the old
      engine: exactly `RangedBlock` red, with the message of 0.3. This is
      the failing test the whole cycle turns green, and it is recorded
      before a line of engine code is touched.
- [ ] 1.4 Add the producer's three features to `REQUIRED`, in the
      producer's own order and spelling: `'a switched source'`,
      `'a selection crossing inside a tick'`, `'a tick carrying both a
      selection crossing and a stop'`. RED first over the OLD corpus
      (all three uncovered), green over the new one.
- [ ] 1.5 Implement their detection in `uncoveredFeatures`, mirroring
      `tools/generate_running_corpus.py`'s `_member_of` and `_selection`
      — from the corpus's DOCUMENTS and tick logs, through the guard's
      own `freeNamesOf` and never through `loadProgram`, so the guard is
      red on a narrowed corpus even when the engine is broken. A
      selector's primitive counts only where no OTHER jump of that member
      has it. The spike of 0.5 is the starting point.
- [ ] 1.6 Extend the narrowed-corpus test to name one of the three, as it
      already names the self-read's three.

## 2. The walk's own arithmetic (design D5), red first

- [ ] 2.1 A red test on a VERSION 6 document with no block anywhere: the
      producer's `HeldAngle` shape — a crank standing at `72.0`, a wheel
      resting at `71.99999999999996` whose self-read law's substituted
      skeleton does not move, a `hoist` moved alone by `0.2`. Assert the
      wheel is `71.99999999999996` bit for bit; the base gives
      `71.99999999999994`.
- [ ] 2.2 Parenthesise `Walk.run`'s `ownAt` closure
      (`jumps.ts:566-567`) and `Walk.probe` (`jumps.ts:700`) as
      `ownLeft + (S − base)`. Nothing else in the walk changes.
- [ ] 2.3 Green, and the seventeen pre-existing corpus scenarios still
      byte-for-byte green over the NEW file — the producer regenerated it
      after this fix and every pre-existing entry is unchanged, so this
      is the regression test for it.

## 3. The block, re-derived at load (design D1.1–D1.3)

- [ ] 3.1 `ProgramBlock` and `EdgeKind` gain `'block'` in `program.ts`.
      `EDGE_KINDS`, which validates the PUBLISHED kind, does NOT: a
      document publishing `kind: "block"` stays refused as an unknown
      kind. Red test for that.
- [ ] 3.2 The dependency graph and iterative Tarjan over it, in the
      published order, with members sorted and components ordered by
      first member — `_components` and `_strongly_connected`
      (`program.py:3474-3501`, `3794-3833`). Unit tests: a program with
      no cycle produces no component; `ShiftedCarry`'s and
      `RangedBlock`'s documents each produce exactly
      `{higher.turn, carry.travel}`; a self-read edge alone is not a
      component (the `needs ∩ gives` exclusion); a `check` edge is never
      in one; a chain 2,000 edges deep does not exhaust the stack.
- [ ] 3.3 Contraction in place at the first member's index —
      `_blocked`/`_block_edge` (`program.py:3503-3550`): needs as the
      union in first-seen order, gives as all members' gives,
      `description` joined with `'; '`, `statedBy` de-duplicated in
      order, `affine` all `false`. `LoadedProgram.edges` becomes the
      contracted list and `determiner` maps each give to the block edge
      with its index in `gives`.
- [ ] 3.4 The order VERIFIED, not re-sorted (design D1.2): every entry's
      needs minus its own gives are given earlier or by nobody. Red test:
      a hand-built document whose two independent law edges are published
      in the wrong order is refused naming both edges and the value.
- [ ] 3.5 A document whose block members are published NON-CONTIGUOUSLY
      but in a valid order loads and runs, contracted at the first
      member's index. Test.

## 4. The selectors and the fold (design D1.4–D1.6)

- [ ] 4.1 One read-only structural accessor exported from
      `expressions.ts` giving a node's kind, operator and child ids. No
      second parser, and no tree construction.
- [ ] 4.2 `readsUnder(plan, substitution)` as the bottom-up
      `(isZero, names)` traversal of design D1.5, with surviving
      placeholders followed into their own folded levels transitively and
      every name closed over the bindings table. Unit tests against the
      producer's `spikes/fold.py` numbers on the corpus's own
      `ShiftedCarry` document: with nothing folded the lever reads
      `carry.travel, higher.turn, lower.turn, shift`; with its `shift >=
      0.5` selector at zero it reads `carry.travel, lower.turn, shift`
      and NO LONGER `higher.turn`; the wheel drops `carry.travel` under
      the complementary comparison.
- [ ] 4.3 MONOTONICITY pinned, as the producer pinned it (task 2.4
      there): the reads under the all-zero fold are a SUBSET of the reads
      under each single zero.
- [ ] 4.4 `selectorsOf(plan, blockGives)` — `_selectors`
      (`program.py:1245-1266`): upward closed along the nesting, names
      closed over the bindings table. Test that a level written `_b2`
      resolves to `shift` and that a node whose level reads the member's
      own driven end is NOT a selector.
- [ ] 4.5 `unconditional` and `switched` per member, own give excluded
      from both; a member with no plan gets its in-block needs minus its
      own. `sign` is NOT foldable — test that a `sign`-gated in-block
      source is NOT counted switched, and that such a block is therefore
      refused by 5.4.

## 5. The load-time refusals (design D1.7)

- [ ] 5.1 A wiring or a formula on a cycle. Red first, message naming the
      edge, its `statedBy` and every member.
- [ ] 5.2 A member driving a GROUP (more than one give). Red first.
- [ ] 5.3 A member whose give is not a bank coordinate. Red first.
- [ ] 5.4 A cycle no selection can break — `unconditionalCycle`
      (`_Block.unconditional_cycle`, `program.py:1328-1350`) — with
      `_cycle_message` (`program.py:3591-3604`) word for word, including
      the sentence about `sign`. Red first.
- [ ] 5.5 Each of the four is refused at LOAD, quoting the document, with
      nothing rendered and no tick taken — the surface `program.ts`
      already stands on.

## 6. The block's step (design D2)

- [ ] 6.1 `blockIncrements` reached from `edgeIncrements` on
      `kind === 'block'`; `edgeCuts` and `edgeValues` likewise.
- [ ] 6.2 The selector partition over the whole stretch
      (`_Block._partition`): a plan of the member's selectors alone over
      its own published skeleton, through the existing `partition`, its
      crossings recorded under that member, its interior cuts merged into
      one list through the existing `merged`, in the members' order and
      each member's postorder.
- [ ] 6.3 The midpoint branches per piece (`_Block._forced`), and the
      per-piece order over the run-time fold (`_Block._order`), memoised
      by the branch VALUE vector — a key built from sorted
      `[name, value]` pairs. Test that a `floor` selector passing three
      windows makes three keys and not one.
- [ ] 6.4 A still-cyclic piece refuses the tick with `_Block._refused`'s
      message: the piece bounds, the relations, and each selector's
      primitive, level and value. Red first, on the producer's
      `BothActive` shape driven past its detent. `UnsupportedLaw`, so
      `RefusalKind` is unchanged.
- [ ] 6.5 The members run over the piece: sources the block does not give
      at `values[k] + deltas[k]·left` moving by `deltas[k]·(right−left)`;
      sources it does give at the BLOCK-ADVANCED value with this piece's
      increment, or `0` where the order has not reached them.
      `memberIncrement` mirrors `_integrated` (`program.py:1517-1536`) —
      no plan, a plan, a self-read reading.
- [ ] 6.6 **The in-block value ADVANCED between pieces, with the
      producer's own negative control as a test**: the lever edge over
      `[0, 0.25]`, `[0.25, 0.6]`, `[0.6, 1]` sums to `1.0` advanced and
      `2.0` not, with the same landing float and the same crossing
      fraction `0.5` as the whole-stretch run.
- [ ] 6.7 Crossings rescaled `left + t·(right − left)` per piece, the
      whole located list SORTED by fraction before it reaches the record.
      Test that a selector's crossing and a member's own interleave
      correctly.
- [ ] 6.8 The two-argument call shape (design D2.7): complete,
      side-effect-free, recording nothing — and still refusing a cyclic
      piece. Test both halves.

## 7. The forced branch, threaded (design D3)

- [ ] 7.1 `forced` added to `partition` and `branchesAt` — the ONLY two
      places it is read. `partition` skips locating a forced node's
      crossings; `branchesAt` returns the forced value without evaluating
      the level.
- [ ] 7.2 `planIncrement`, `planCuts`, `retainedIncrement`,
      `retainedCuts` and `Walk` pass it down; `Walk.outerCuts` and
      `Walk.outerBranches` carry it, and everything downstream inherits
      it from the `branches` map.
- [ ] 7.3 Test that a member whose selector sits in layer one and whose
      LATCH sits in ADR-057's layer three — the Curta lever's shape —
      holds the forced branch through the whole walk, the far-side
      landing included; and that flipping the forced branch changes the
      answer (the producer's reverted-forcing measurement:
      `0.0 != 1.0`).
- [ ] 7.4 Test that a forced node's crossings are NOT located inside the
      piece (the producer's other reverted measurement:
      `[Crossing(..., primitive='>=', level=0.0, t=0.5)] != []`).
- [ ] 7.5 A law with no block pays exactly one extra optional argument
      and nothing else: the seventeen pre-existing corpus scenarios stay
      byte-identical.

## 8. What a block reports (design D4)

- [ ] 8.1 The ADVANCED ABSOLUTE at the stretch's end for every coordinate
      any piece landed; nothing for one none landed. Red first on
      `LandedCarry`'s shape — a landing in one piece and a further
      increment in a later one — asserting the committed float is the
      advanced absolute and NOT the landing (the producer measured
      `1.0 != 3.0`).
- [ ] 8.2 `affine` FALSE on every give, so `Run.locate` takes `searched`.
      This is what turns `RangedBlock` green: the stop at
      `0.29999999999972715` and `spin` at `0.5999999999994543`.
- [ ] 8.3 `edgeCuts` on a block returns the selector partition
      (`_Block.cuts`); `edgeValues` returns nothing, and `Run.valuesOf`
      never asks because every give is a bank key.
- [ ] 8.4 `Run.pushes`'s break: a test that an input reaching a stopped
      block coordinate only through an INACTIVE selection is NOT stopped
      and completes its whole travel, while the pushing input retires
      blocked — `RangedBlock`'s `spin` against its `crank`.
- [ ] 8.5 `run.ts` has no structural change. State it in the commit and
      show the diff is confined to `program.ts`, `jumps.ts`, `edges.ts`
      and the version/corpus files.

## 9. The framework's own numbers, mirrored

- [ ] 9.1 The one-tick table of task 0.4, turned into an assertion: the
      corpus's own `ShiftedCarry` document at `dt = 1.0` cranked by `2.0`
      commits `lower.turn 2.0`, `higher.turn 1.0`, `carry.travel 1.0` —
      and does so whatever order the two members are published in.
- [ ] 9.2 The producer's frozen-twin table at `dt = 1/12` over 12 ticks:
      `shift = 0` gives `lower.turn 1.9999999999999998`,
      `higher.turn 1.4999999999999998`, `carry.travel 1.0`; `shift = 1`
      gives `0.0`, `1.9999999999999998`, `1.0`.
- [ ] 9.3 A selection change ALONE moves nothing — exactly the number
      zero, bit for bit, not approximately.

## 10. The corpus, green

- [ ] 10.1 All 19 scenarios replay green, exactly for discrete state and
      within the corpus's own `1e-9` relative window for floats.
- [ ] 10.2 The width guard green on the new file, red on the old and on a
      trimmed one.

## 11. Versions (design D7)

- [ ] 11.1 Red first: `version.test.ts` for `documentVersions`
      `[1, 2, 3, 4, 5, 6, 7]` and `RENDERED_VERSIONS` following it in
      `viewer.ts`.
- [ ] 11.2 Red, then `solidNodeViewerApi` `15 → 16`, with the comment in
      `package.json` and the spec's own sentence agreeing.
- [ ] 11.3 The spec scenario "A version beyond the ones it reads is
      refused" now mounts a version 8 document; the Python and widget
      tests that pin the refused version follow.
- [ ] 11.4 `bundle.py`'s `RELEASED_DOCUMENT_VERSIONS` does NOT move;
      assert `describe()['documentVersions']` is the package's new list.
- [ ] 11.5 `capture.py`'s `carries_program` and `viewer.ts`'s program
      gate do NOT move — assert both admit a version 7 document, so the
      claim is a test and not a reading.

## 12. The Curta's carriage, in a real browser (design D10)

- [ ] 12.1 Export `tests/carriage_project/machine.py:CurtaCarriage` from
      a THROWAWAY copy of solid-node at `0b0f02a`, with the one relative
      import changed as the clearing fixture's was, and check that the
      change moves nothing: the framework's own carriage tests pass on
      both copies and the published program is identical apart from its
      `identity`.
- [ ] 12.2 Commit it as `tests/fixtures/carriage/` with a README stating
      the commit, the command, the byte count and md5
      (`1598d57e18f772315183a7e466123a39`), and what the machine is.
      `tests/support.py` gains `CARRIAGE`.
- [ ] 12.3 A document test with no browser: version 7, five drivers,
      fourteen coordinates at `0.0`, thirty-five bindings, a `seat` span
      whose two sides are expressions, nine law edges of which SEVEN form
      one block, every model path resolving beside the document.
- [ ] 12.4 A Playwright acceptance beside `tests/test_clearing_document.py`,
      at the framework's own `dt = 0.02`, driving only the document's own
      drivers: lift/shift/drop/crank to `dial0 36, dial1 36, dial2 72,
      dial3 72`, `lever0.travel` exactly `1.0`; lift/shift/drop again and
      EVERY coordinate but `seat`, `hoist`, `position`, `lift`
      BIT-IDENTICAL with `seat` at `40.0`; lift/reset/drop and the levers
      back within the agreement window with `dial3` still `72`; crank
      again to `dial2 108, dial3 144`.
- [ ] 12.5 The interlock: with the carriage down and a lever set, the
      shift retires `blocked` with `0.0` admitted, `seat` stands at
      `20.0`, the stop names `('position',)`, and no dial or lever moved.
- [ ] 12.6 A run-time refusal reaching the page: the producer's
      `BothActive` shape driven past its detent, reported as a refusal
      with the bank standing where it stood.
- [ ] 12.7 Screenshots written to `tests/_shots/`, as the clearing
      acceptance writes them, so the evidence is a file and not a claim.

## 13. What it costs (design D9)

- [ ] 13.1 `cost.test.ts`: `ShiftedCarry` quiet and crossing ticks, the
      carriage fixture (one block of seven), and `RangedBlock`'s searched
      stop, each as ticks/s beside the Pascaline's and the Clearing
      fixture's existing numbers.
- [ ] 13.2 The ratios recorded against the producer's (1.6x a frozen
      twin, 2.0x on a crossing tick, 22x for the searched stop), and the
      control: the Pascaline's figure must not move.

## 14. The whole suite, and the build

- [ ] 14.1 `npm test`, `npm run typecheck`, `npm run build` — against the
      0.1 baseline, with the new totals recorded.
- [ ] 14.2 The Python suite from the worktree root with the workspace
      venv, and `scripts/check-dist` (which uploads nothing).
- [ ] 14.3 The rebuilt `dist/solid-widget.js` committed, as the previous
      cycles committed theirs.

## 15. The record

- [ ] 15.1 `CHANGELOG.md` under `0.2.0 — unreleased`: the block, the
      per-piece order, the version 7 document, the walk's ulp, and the
      carriage in a browser.
- [ ] 15.2 `README.md`'s version claims.
- [ ] 15.3 `docs/adrs/EXPORT/ADR-058-a-block-is-ordered-per-piece-from-the-published-edges.md`,
      extracted AFTER implementation, and `docs/adrs/README.md` updated.
- [ ] 15.4 `evidence.md` for this change: the measurements of §0 with the
      after numbers beside them, the deviations from this design and why,
      and the follow-ups.
- [ ] 15.5 `openspec validate execute-the-selection --strict` green, and
      the change archived under its dated name after implementation.
