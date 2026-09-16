## 1. Red: record the finding on this tree

- [x] 1.1 Copy `spikes/order.py`, `spikes/patched_corpus.py`,
      `spikes/gate_survey.py`, `spikes/alternatives.py` and
      `spikes/regenerate.py` into the change's `spikes/` directory with a
      `README.md` table, as `select-the-source` did, and re-run each from
      the worktree root; paste the output into `evidence.md`.
- [x] 1.2 RED (the replay): with `_Block._order` patched to return the
      members in listing order, the COMMITTED `ShiftedCarry` entry
      replays with zero disagreements — every bank value, crossing, stop
      and command identical. Record it, and the same result with the
      members reversed.
- [x] 1.3 RED (the whole corpus): under the same patch every one of the
      19 committed scenarios reproduces its bank exactly; the only
      disagreement anywhere is `RangedBlock` tick 1's crossing COUNT
      (2 against 3). Record the per-scenario table.
- [x] 1.4 RED (the guard): `uncovered_features` over the committed
      corpus, with the new feature appended to `REQUIRED`, returns
      `['an in-block gate crossing inside a tick']` — no committed
      machine supplies it.

## 2. The scenario

- [x] 2.1 In `tools/generate_running_corpus.py`, change the
      `ShiftedCarry` entry of `CORPUS` so both cranks run `by: 2.0` over
      `duration: 0.3` instead of `0.2`. Nothing else in the entry moves:
      same `dt` `0.05`, same 20 steps, same shift at tick 8, same handles.
- [x] 2.2 Update the entry's comment to say what the script is FOR — the
      gate the higher wheel reads on the lever crosses strictly inside
      tick 2, which is what makes the scenario discriminate the order.
- [x] 2.3 Regenerate `tests/running-corpus.json` with the tool (never by
      hand) and diff it against the committed file: expect
      `removed: []`, `added: []`,
      `changed: [('ShiftedCarry', 0.05, 20)]`, the pre-existing entries'
      order preserved, 19 scenarios over 16 machines and 356 ticks.
      Record the diff.
- [x] 2.4 Confirm the regenerated `ShiftedCarry` entry's `document` is
      byte-identical to the committed one (the script is not part of the
      document) and that it still publishes `version: 7`.

## 3. The generator's refusal

- [x] 3.1 Add `'an in-block gate crossing inside a tick'` to `REQUIRED`,
      after `'a tick carrying both a selection crossing and a stop'`.
- [x] 3.2 Derive it in `uncovered_features` as design.md §2 states:
      for a crossing under a block member with `0 < t < 1`, split the
      member's jumps carrying that primitive — levels resolved
      transitively through `bindings` — into GATES (naming a coordinate
      the block gives other than the member's own driven end) and
      SELECTORS (naming none); count the crossing when a gate's in-block
      name moved across the tick and no such selector reads anything that
      moved or anything the bank does not carry. Skip a scenario's first
      tick, which has no preceding bank.
- [x] 3.3 Keep the helper small and beside `_selection` and `_member_of`,
      reusing `free_names`; add no new import and no new document key.
- [x] 3.4 GREEN: `uncovered_features` over the regenerated corpus returns
      `[]`, and it returns the new feature for a corpus with
      `ShiftedCarry` removed.

## 4. The tests

- [x] 4.1 In `tests/test_running_corpus.py::CoverageGuardTest`, add
      `test_a_corpus_with_no_in_block_gate_crossing_is_refused`: drop
      `ShiftedCarry` and assert the new feature is in `missing`, and
      assert `'a switched source'` is NOT (RangedBlock still carries the
      block), so the two features are shown to be independent.
- [x] 4.2 Add a second narrowed case in the shape of
      `test_a_corpus_with_no_selection_crossing_is_refused`: every
      machine kept but `ShiftedCarry`'s crossings blanked, and the new
      feature still missing.
- [x] 4.3 Add `BlockOrderTest` (design.md §3): replay the `ShiftedCarry`
      entry with `solid_node.simulation.program._Block._order` patched to
      `tuple(range(len(self.members)))`, restored in `tearDown` or a
      context manager, and assert at least one tick's bank differs from
      the corpus by more than `tolerance * max(1, |a|, |b|)`; and assert
      the UNPATCHED replay of the same entry reproduces it. Name the
      expected divergence in the failure message.
- [x] 4.4 Prove 4.3 red first: run it against the committed corpus and
      the committed script (git stash-free — check out nothing; run the
      test with the OLD entry restored in a scratch copy of the tool, or
      record the equivalent spike output from task 1.2) and show the
      first assertion failing. Record which.
- [x] 4.5 Run `tests/test_running_corpus.py` and
      `tests/test_running_document.py` green, and report the counts.
- [x] 4.6 Run the named running and export suites
      (`tests/test_running_simulation.py`, `tests/test_running_jumps.py`,
      `tests/test_running_document.py`, `tests/test_running_corpus.py`
      and the export tests) and report the counts; no other suite can see
      this change, and say so rather than running the full 2930.

## 5. Records

- [x] 5.1 Sync the `export` delta into
      `openspec/specs/export/spec.md`: the MODIFIED requirement "The two
      runtimes share a conformance corpus", carrying every existing
      scenario under its exact title plus the two new ones.
- [x] 5.2 One `HISTORY.rst` line under Unreleased, in the voice of the
      existing entries: the corpus now catches a consumer that runs a
      block's members in the order the document lists them.
- [x] 5.3 In `workflow/warts.md`, under the `select-the-source` section,
      record the finding and mark it **FIXED by `pin-the-block-order`**,
      with the measured numbers (the committed scenario replaying green
      under listing AND reversed order; one sixth of a turn of
      `higher.turn` after the fix).
- [x] 5.4 Note in the cycle's report, for the viewer's own cycle: the
      regenerated `tests/running-corpus.json` and the same `REQUIRED`
      entry are owed to
      `solid_node_viewer/widget/src/run/running-corpus.test.ts`
      (`REQUIRED`, `uncoveredFeatures`) in `solid-node-viewer`. No ADR is
      extracted for this cycle.
- [x] 5.5 `openspec validate pin-the-block-order --strict`; the reviewer
      archives after review.
- [x] 5.6 A dated note in `docs/adrs/NODE/ADR-122-...md`'s Consequences,
      in the style of ADR-105's amendment paragraph: the `ShiftedCarry`
      scenario the decision added to pin the block's ordering replayed
      green under the published listing order (and under the members
      reversed) until `pin-the-block-order` changed its script, with the
      measured numbers; the decision itself is unchanged, so
      `docs/architecture.md` is untouched and the ADR index's status row
      gains only the amendment note.
