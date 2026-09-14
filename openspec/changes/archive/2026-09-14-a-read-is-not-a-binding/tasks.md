## 1. Red first: the fixtures and what they must publish

- [x] 1.1 Record the baseline in `evidence.md`: run
      `tests/test_running_document.py`, `tests/test_running_simulation.py`,
      `tests/test_couplings.py` and `tests/test_running_corpus.py` on the
      planning commit and write down the counts, so "green unchanged" in
      task 4 has something to mean.
- [x] 1.2 In `tests/running_project/machine.py`, one fixture pair beside
      the existing running machines — no new module, and no entry in
      `tools/generate_running_corpus.py`'s `CORPUS`:
      - `StatedBelow`: a running root with one driver, a child assembly
        holding two leaves (`Slide`-like `insert`, `Pin`-like `lift`)
        whose OWN body states `key.insert.drives(p1.lift, ratio=0.5)`,
        and the root's own body stating `push.drives(plug.key.insert)`
        and `plug.p1.lift.drives(d1.lift, ratio=-1)` onto a second
        root-level leaf. This is `evidence/fixture.py`'s `Lock`, renamed
        to the running project's vocabulary (arbors and slides, not
        locks) and using the existing `parts.py` leaves wherever they
        fit.
      - `StatedBelowBody`: the same declarations with no time base, the
        untimed twin that already publishes today.
      - `StatedBelowOpaque`: the running root with a law that does NOT
        invert on the ROOT's relation (`evidence/fixture.py`'s
        `OpaqueLock`), which fails differently and must also publish.
- [x] 1.3 In `tests/test_running_document.py`, one test per new spec
      scenario, all red before task 2:
      - `StatedBelow()` POSED with `set_state` and then published: today
        `DoublyBound` naming `plug.p1.lift`; after the change the
        document is produced, `d1`'s placement operation is the single
        name `d1.lift`, and `plug.p1.lift` is a key of
        `program.coordinates`.
      - `StatedBelowOpaque()` posed and published: today `DoublyBound`
        naming `d1.lift`; after the change published.
      - `StatedBelow()` posed, published, then posed AGAIN: every
        coordinate holds the value that second pose computes, each bound
        by the relation that states it, and nothing is refused. This is
        the re-pose half of the requirement and is the test that fails
        for the RIGHT reason if the restore is only partial.
      - `StatedBelowBody()` posed and published stays green unchanged —
        the untimed path is the reference behaviour, not a new one.
      - A never-posed `StatedBelow()` publishes the SAME document as the
        posed one (compare the normalized documents), so "posed or not
        makes no difference" is pinned rather than assumed.
- [x] 1.4 In `tests/test_running_simulation.py`, that a LIVE run is
      untouched: `Sim(StatedBelow(), dt)` poses `p1.lift` and `d1.lift`
      from its driver on every tick; publishing while that run owns the
      tree still succeeds; and the bank one tick later is the bank the
      run computes. The existing "publication runs over a tree a live run
      owns" coverage stays green.

## 2. The change

- [x] 2.1 In `symbolic_document` (`solid_node/core/serializer.py`),
      snapshot each remembered node's `_solver_bound` where `remember`
      already snapshots its driver states, and put it back in the same
      `finally` — after `delivery.restore()` and BEFORE the re-render —
      only when `delivery is not None`. Restore ABSENCE as absence: a
      node that held no record must hold none again.
- [x] 2.2 Comment it with WHY, in the module's own voice: the walk's own
      phases overwrite the record of what the previous enumeration bound,
      and under a running root they bind no joint coordinate to put in
      it, so the re-render would inherit the pose's values with nothing
      left that knows to clear them.
- [x] 2.3 Extend `symbolic_document`'s docstring — the paragraph that
      already explains the restore — to say that the enumeration's own
      record travels with the coordinates, and why the untimed path needs
      none.
- [x] 2.4 Nothing in `solid_node/motion/couplings.py`,
      `solid_node/motion/ports.py`, `solid_node/node/phase.py` or
      `solid_node/node/assembly.py` changes. Confirm by reading and say
      so in `evidence.md`.

## 3. The recorded documents

- [x] 3.1 Confirm every base document under `tests/base_documents/` is
      byte-identical and `ByteIdentityTest` passes over all of them: the
      change adds no fixture to the corpus and alters no published byte.
- [x] 3.2 Confirm `tests/running-corpus.json` is unchanged by
      re-generating it with `python tools/generate_running_corpus.py` and
      showing an empty diff.

## 4. Proof

- [x] 4.1 `tests/test_running_document.py`,
      `tests/test_running_simulation.py`, `tests/test_running_stops.py`,
      `tests/test_running_jumps.py`, `tests/test_couplings.py` and
      `tests/test_running_corpus.py` green; then the whole suite, with
      the counts in `evidence.md` against the baseline of 1.1.
- [x] 4.2 Re-run `evidence/probe_publication.py`, `evidence/probe_sim.py`
      and `evidence/probe_candidates.py` against the changed worktree and
      paste the output beside the before: the fixture publishes, the
      candidate-A patch becomes a no-op, and the traced re-render shows
      `clear_solved` dropping the coordinates it could not drop.
- [x] 4.3 Publish the originating project's machine: re-run
      `evidence/probe_lock.py` against a copy of
      `projects/Locks/Pin_tumbler_lock` with its five lift relations moved
      back into `Plug`, with no patch, and record that it publishes. The
      project's own edit stays the pilot's call; record the measurement
      either way.

## 5. The record

- [x] 5.1 `docs/architecture.md`: the publication synthesis says what the
      producer puts back.
- [x] 5.2 `docs/changelog.rst`.
- [x] 5.3 `workflow/warts.md`: mark the finding FIXED with the cycle's
      name, the measured cause and the two corrections this cycle's
      evidence makes to the original filing — the refusal is in the
      producer's re-render epilogue and not in the publication walk, and
      it needs a tree an enumeration posed, so a never-posed tree of the
      same class always published.
- [x] 5.4 No ADR: this restores a stated contract and opens no new
      boundary (design.md decision 4). If the reviewer disagrees, the ADR
      is numbered next in `docs/adrs/` and added to `docs/adrs/README.md`.
