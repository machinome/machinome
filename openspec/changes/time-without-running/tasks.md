Every behavioural task is RED FIRST: write the test, watch it fail for the
stated reason, then make it pass. Run framework code from inside this
worktree with `PYTHONPATH="$PWD"` and the workspace venv, under
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one job at a time — this tree is
on a virtiofs mount that exhausts file descriptors under parallel load. Do
not edit any fixture or expected value of the cycles `declare-the-state` or
`a-bound-stops-the-request`.

## 1. The baseline this cycle must not move

- [ ] 1.1 Record the green baseline: run the whole suite and keep the
      summary, the running-fixture timings, and the document body of one
      published stateless fixture for the byte-identity assertions later.
- [ ] 1.2 Record `git status --short` and the hashes of
      `tests/running-corpus.json` and every `tests/running_project` fixture,
      so "untouched" is a checked fact at the end and not a claim.
- [ ] 1.3 Verify against the SOURCE, and record, every consumer of
      `declared_time(cls)`: each that reads `.loop` (`animation_block`,
      `read_time`, `manager/snapshot.py`) and each that compares `.mode` to
      `'running'` (`serializer.running_root`, `Sim.__init__`,
      `couplings.run_owned`, `assembly._coordinate_delivery`,
      `manager/snapshot.py`). Note any site the design did not name.

## 2. The third spelling (design §1, §2)

- [ ] 2.1 RED: tests in `tests/test_time_base.py` (ADDED tests only, no
      existing test edited) for `Time.elapsed()` — `mode == 'elapsed'`,
      `loop is None`, `declared_time` returning it, the misnamed, leaf-borne
      and below-the-root refusals, and `Time()` naming three spellings.
- [ ] 2.2 Implement `Time.elapsed()` in `solid_node/motion/ports.py`:
      the constructor built without `__init__` as `running()` is, `mode`
      answering `'elapsed'`, and the `TypeError` message gaining the third
      spelling. Confirm the two existing assertions on that message
      (substrings `Time(loop=` and `Time.running()`) still hold.
- [ ] 2.3 RED then green: an elapsed root that declares NO `State` is
      admitted and equivalent — `Sim(node, dt)` steps it, `sim.time` reads
      `tick * dt`, `self.time` is `$t` unbound and the bound number
      keyframed, and its published document is compared BYTE FOR BYTE with
      the same tree declaring no base at all.
- [ ] 2.4 Confirm no clocked code path is entered for 2.3's stateless
      elapsed root: the `simulation.clocked` counter reads zero across its
      construction, pose, stepping and publication.

## 3. The clock in the bank (design §3, §6)

- [ ] 3.1 RED: `tests/clocked_project/pendulum.py` — `Regulator` (elapsed ×
      memory: the clock, an `engaged` driver, a `count` state, a bob posed
      from `A * sin(2 * pi * self.time / T)`, and one committing relation on
      `floor((time + T/4) / (T/2))`) and `Swing` (the same root with the
      state and the relation removed). Assert the bank carries `time` at
      `0.0`, `sim.time` reads it, `state={'time': 4.0}` opens there, and
      `snapshot`/`restore`/`reset` carry it.
- [ ] 3.2 Admit a `State` under the elapsed base in
      `enumeration.refuse_states_under_a_clock`
      (`solid_node/simulation/enumeration.py:160-200`), leaving the looping
      and running refusals and their messages exactly as they are. NOTE the
      shape: that function refuses the LOOP base by test and falls THROUGH
      to an unconditional running refusal, so an elapsed root would be
      handed the running message unless the elapsed base returns before it.
      Assert both messages unchanged and the elapsed root admitted.
- [ ] 3.3 Bank the clock in `simulation/clocked.py`: the initial entry, the
      `state=` acceptance, the snapshot identity, and `sim.time` in
      `simulation/sim.py` lifted for this base only — with the untimed
      clocked root's refusal message improved to name `Time.elapsed()`.
- [ ] 3.4 Deliver the clock in the ONE walk that poses the tree —
      `solid_node/node/qualified.py:drive_tree(root, resolve, visit=None,
      collected=None)`, which binds by writing each node's snapshot directly
      (line 389) and renders the tree once at the end (lines 421-422).
      Deliver through the EXISTING `visit(node, path, children)` hook, called
      per assembly after binding and before anything renders (lines 415-417)
      and already used this way by `qualified_declarations`: under an elapsed
      clocked root `Clocked.pose` (`simulation/clocked.py:1394-1408`) passes
      a `visit` that writes the banked seconds into `node._states['time']`,
      and under every other root it passes NONE. Add no parameter to
      `drive_tree`. Assert ONE render per request with a counter; assert a
      descendant's `self.time` reads the banked seconds, not `$t`; assert the
      walk is entered with `visit=None` for a model with no clock.
- [ ] 3.5 Assert the no-collision claim rather than stating it: a
      root-declared `Driver`/`State` named `time` is refused at class
      definition by the existing shadowing message.

## 4. The request that moves the clock (design §4)

- [ ] 4.1 RED: `tests/test_clocked_time.py` — `move('time', by=)` and
      `to=`, seconds in and seconds out with no conversion; `admitted`
      equal to the seconds made; the `Request` object otherwise unchanged.
- [ ] 4.2 RED: a negative `by=`, and a `to=` behind the banked instant, each
      refused BY NAME naming both instants, with the bank, the pose and the
      record standing; `by=0` admitted with no event and `admitted == 0.0`.
- [ ] 4.3 RED: `move('time', ...)` under a clocked root with no time base
      refused by name naming `Time.elapsed()`; a request naming two inputs,
      a state or a joint coordinate refused as before.
- [ ] 4.4 Implement the clock as a moving input in `Clocked.move` and
      `Clocked._input`, with the clock's own seconds-in-seconds-out
      declaration, and the backwards refusal.

## 5. Events on the clock (design §5)

- [ ] 5.1 RED: the clock as a SOURCE — `(time & engaged & count).commits(...)`
      recorded on the class, both factories called once with the realized
      owners, and the returned callables receiving the seconds positionally
      in written order.
- [ ] 5.2 RED: the class-definition refusals — `time` as a source under
      `Time(loop=)` and under `Time.running()` naming `Time.elapsed()`;
      `time` as a target of `commits`; `time` as either end of `drives`.
      Then the two cases of a body that declares NO base, which are NOT the
      same case (design §5): with the stdlib `time` imported by the file,
      `time & <a declaration>` is refused BY NAME by the reflected `&`,
      naming the operand and saying the clock is only the root's own
      `Time.elapsed()` declaration; with nothing bound to `time` at all, the
      test asserts PYTHON's `NameError` and the change claims no framework
      message. Do not write a test that expects a framework refusal for the
      second: a class body does not see `AssemblyNode.time`.
- [ ] 5.3 Implement the clock reference kind in
      `solid_node/motion/couplings.py` and the `&`/`commits` faces on
      `Time` in `ports.py`, with every refusal of 5.2 raised at class
      definition — and the reflected `__rand__` that makes the group's
      left-operand refusal the mirror of `group_with`'s existing
      right-operand one (`motion/couplings.py:828-848`). Assign it on the
      kinds that already carry `__and__`: `Coordinate`
      (`motion/ports.py:169`), `CoordinateRef` (`motion/couplings.py:320`),
      `Coordinates` (`motion/couplings.py:789`), `DriverDeclaration` and
      through it `StateDeclaration` (`node/qualified.py:167`),
      `ChildDeclaration` (`node/declarative.py:451`) and
      `RepeatDeclaration` (`node/declarative.py:567`). One helper, six
      assignments, no new class. Assert that a left operand which IS a
      coordinate never reaches it (its own `__and__` answers first), so no
      admitted `&` changes.
- [ ] 5.4 RED then green in `simulation/clocked.py`: the clock joins the
      per-input classification loop, so `moves_with('time')` answers for a
      level the clock moves; a CURVED level in the clock is refused at
      construction naming the clock and the primitive; the "no request can
      reach this relation" refusal now admits a relation the clock alone
      moves and names the clock in its message.
- [ ] 5.5 RED then green: forty events in one `move('time', by=40*T)` in
      path order at exactly the hand-computed release instants; ten short
      requests equal to one long one, bank for bank and instant for instant;
      a driver request at a standing clock firing nothing on the clock; a
      request crossing `_MAX_CROSSINGS` refused naming the request, the
      relation, the count and the maximum.
- [ ] 5.6 Assert that NO tolerance was introduced: the clocked path's use of
      `_CROSSING_TOLERANCE` is unchanged from the base commit, checked by
      diff.

## 6. The pose, and the document producers (design §6)

- [ ] 6.1 RED then green: after a time request the posed operation is the
      number the instant gives; the same tree rendered outside any
      simulation carries `$t`, and its serialized expression is identical to
      `Swing`'s.
- [ ] 6.2 Confirm by test that no document producer is touched, with NO
      headless browser anywhere in this cycle:
      (a) the ONE gate — `serializer.document_body` over `Swing` is
      BYTE-IDENTICAL to the same tree declaring no time base at all;
      (b) `solid build` and `solid export` run on `Swing` (whose geometry is
      a single box) and produce what an undeclared root produces;
      (c) `solid snapshot` on the OPENSCAD path keyframes the fraction as it
      does for an undeclared root;
      (d) publication still refuses `Regulator` by the unchanged
      clocked-publication gate, naming its states.
      A Chromium capture is deliberately out: it cannot strengthen a
      byte-identity claim, and it adds the snapshot extra and this mount to
      a test that needs neither.

## 7. Bounds and the clock (design §7)

- [ ] 7.1 RED: a clocked elapsed fixture with a ranged joint a DRIVER moves
      — the driver request is clipped at the bound and reports its stop
      (ADR-126 unchanged), and a time request over the same fixture reports
      no stop and makes its whole travel.
- [ ] 7.2 RED: a commit made by a TIME request that carries a bounded
      coordinate out of range refuses the whole request by name, commits
      nothing and never poses; assert the bank, the record and the posed
      tree stand.
- [ ] 7.3 RED: a ranged joint driven by a relation whose LAW FACTORY
      captured the clock is refused AT SIMULATION CONSTRUCTION, by name,
      naming the joint, the node, the side and the surviving name. The
      fixture is the construction design §7 spells out and nothing more
      contrived: a `law=` factory that reads `owner.time` at realization
      (`motion/couplings.py:1552-1554` calls it once with the realized
      owners), which is the symbolic `$t` while unbound
      (`node/assembly.py:693-700`), and closes over it. Expect the
      legacy-render `FutureWarning` if that read happens inside a render
      phase — `note_read` records, it does not raise
      (`node/phase.py:191-203`). Implement the general rule — any free name
      surviving a composed chain that is not a bank id is refused — in
      `_constrained` (`simulation/clocked.py:1137-1187`), which already
      computes `moving = free_names(root)` (line 1166) and already holds the
      bank, drivers AND states, as `chains.bank` (lines 1113-1122); `$own`
      is the one name exempt.
- [ ] 7.4 If the fixture of 7.3 cannot reach the chain compile for an
      unrelated reason, STOP, report the evidence, and record the blind spot
      rather than inventing a path to the refusal. The route above is
      established STATICALLY — law factory, symbolic capture,
      `checked_expression` passing a free name through
      (`simulation/program.py:3772-3796`), `free_names` keeping it,
      `Bounded.standing` raising the bare `KeyError`
      (`simulation/clocked.py:964-969`) — and has not been executed. If it
      turns out unreachable, the general free-name rule still goes in as a
      BACKSTOP, the way cycle 2 recorded its unreachable cyclic chain, and
      the spec scenario for it is rewritten to promise only what a test can
      reach.

## 8. Zero behaviour change, proved (design §11)

- [ ] 8.1 The whole suite green, with no fixture of the two previous cycles
      edited and no expected value changed anywhere; `git status --short`
      compared with 1.2.
- [ ] 8.2 `tests/running-corpus.json` and every running fixture byte-for-byte
      unchanged; the running fixtures' per-tick cost inside the envelope
      recorded in 1.1.
- [ ] 8.3 The stateless fixture's document byte-identical to 1.1's copy; the
      clocked-path counter zero across a stateless model's construction,
      pose, `Sim(node, dt)` stepping and publication.
- [ ] 8.4 `Time.running()` untouched, asserted by diff: no line of
      `simulation/run.py`, `simulation/program.py`'s compile or the running
      document path changed by this cycle.

## 9. Measurement (design §14)

- [ ] 9.1 Measure and record, on the pendulum fixtures only: seconds per time
      request with no event, with one event and with forty; seconds per pose.
- [ ] 9.2 Measure the cycle 1 register fixture's seconds per request before
      and after this change, and a stateless fixture's seconds per pose
      before and after, to show the clock costs a model that has none
      nothing.
- [ ] 9.3 Write the numbers into `evidence.md`. Claim nothing about the
      Curta, which has no clock, and nothing comparative about
      `Time.running()`.

## 10. Records and completion

- [ ] 10.1 `docs/scenarios.rst` and `HISTORY.rst`: the third spelling, the
      banked clock, the request that moves it and the events on it.
- [ ] 10.2 Extract ONE NODE ADR, candidate ADR-127, after the implementation
      is green, per design §10; update `docs/adrs/README.md` and
      `docs/architecture.md` if the synthesis moved.
- [ ] 10.3 Carry design §12's Non-goals into `workflow/warts.md` as a
      section for this cycle, each with its reason and the shape a later
      cycle takes, and mark nothing CLOSED that this cycle did not close.
- [ ] 10.4 Sync the baseline specs, archive the change, run
      `openspec validate --strict`, confirm the repository root with
      `git rev-parse --show-toplevel`, and make commit 2 with the whole
      completed state.
