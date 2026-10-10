Every behavioural task is RED FIRST: write the test, watch it fail for the
stated reason, then make it pass. Run framework code from inside this
worktree with `PYTHONPATH="$PWD"` and the workspace venv, under
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, ONE job at a time — this tree is
on a virtiofs mount that exhausts file descriptors under parallel load. Do not
edit any fixture or expected value of the cycles `declare-the-state`,
`a-bound-stops-the-request` or `time-without-running`, and do not edit
`tests/running-corpus.json` or anything under `tests/running_project/`.
Section references are to `design.md`.

## 1. The baseline this cycle must not move

- [x] 1.1 Record the green baseline: run the whole suite and keep the summary
      and the per-test timings of the running fixtures.
- [x] 1.2 Record `git status --short`, the hash of `tests/running-corpus.json`
      and the hash of every file under `tests/running_project/`, so
      "untouched" is a checked fact at the end and not a claim.
- [x] 1.3 Publish and keep the FULL document body of at least four stateless
      fixtures — one plain, one flexible, one with a non-empty `bindings`
      table, one running — as files, for the literal byte comparisons in
      section 11.
- [x] 1.4 Verify against the SOURCE and record: every producer that reaches
      `document_body` (`core/builder.py`, `core/export.py`,
      `viewers/browser.py`, and the running corpus generator's `document_of`);
      every caller of `viewer_bundle.unreadable_document`; and every caller of
      `instructions_table` with its current `running=` argument. Note any site
      the design did not name.

## 2. What the compiled machine must retain (design §6, §7, §12, §13)

- [x] 2.1 RED: a test asserting that a compiled committing relation exposes
      the LAW GRAPHS its inspection built. `_checked_law`
      (`simulation/clocked.py:490-542`) applies the law to one token per
      source, checks the shape and returns only the callable; the graphs are
      what this cycle publishes.
- [x] 2.2 Implement: `Committing` retains the checked law graphs, one per
      target in written order, beside the callable it already holds. Nothing
      about the executor's request path changes — the callable is still what
      `commit` calls (`clocked.py:222-242`).
- [x] 2.3 RED then green: `CompiledClocked.published(initial)` — the whole
      `clocked` object of design §5, with every key in its fixed order, every
      expression slot a NATIVE GRAPH, `commits` in `_records_of` tree order
      and `bounds` in `compile_bounds` order. Assert that republishing an
      unchanged machine gives an equal object.
- [x] 2.4 Implement `commits` entries (design §6): `sources`, `targets`,
      `at: {primitive, level}`, `law` aligned with targets (a numeric law
      publishing a numeric literal, never null), `shapes` from
      `Committing.jumps[input].shape`, `description` and `stated_by`.
- [x] 2.4a RED: a law over a NEGATIVE operand banks one value and a verbatim
      published graph gives another — `(-1) % 10` is `9` from the callable
      (`clocked.py:222-242`) and `-1` from `math.fmod`
      (`scad_expression.py:59`). Write the failure before the rewrite exists.
- [x] 2.4b Implement the DESUGARING of design §16: every `%` node of a
      published LAW graph becomes `r + b * ((r != 0) * ((r < 0) != (b < 0)))`
      over `r = a % b`. Prove it against CPython's `float_rem`
      (`Objects/floatobject.c`) by property test — random doubles of both
      signs, including integral values and sub-ulp magnitudes — asserting
      equality with Python's own `a % b`, with the SIGN of a zero under a
      negative divisor recorded as the one stated exception. Assert the
      rewrite touches a law and NOTHING else: an `at` cannot carry a `%` at
      all (`_event_level`, `clocked.py:474-487`), and a chain, a bound and a
      constraint level are published verbatim because the framework evaluates
      them through the graph (`clocked.py:986-1015`).
- [x] 2.4c Pin the INTEGER ROUNDING a commit applies, as a test naming what
      `State.committed` does (`state.py:84-93`): the nearest whole native
      unit, an exact half to the EVEN one, `scale` applied nowhere. Assert the
      three existing `%`-writing fixtures (`counter.py:67-68`,
      `register.py:86-88`, `units.py:90`) publish and bank identically before
      and after the rewrite, since all three run on non-negative operands.
- [x] 2.5 Implement `bounds` entries (design §7): `coordinate`, `side`,
      `unit`, `node`, `joint`, `description`, `value` from `Bounded.chain`,
      `bound` from `Bounded.bound`, `plan` through the EXISTING
      `program._published_plan`/`_renamed`, and `shapes` carrying the
      skeleton's shape and one per published jump from `Bounded.shapes` and
      `Bounded.plans[input].jumps`. Assert the level is NOT published.
- [x] 2.6 Implement the placeholder mint for the bounds' plans through the
      EXISTING `program._placeholder_prefix` and the whole-document rule
      (`program.py:2781-2799`), and test that two bounds each carrying a
      `floor` get two distinct published names.
- [x] 2.7 Implement `identity` (design §13) as a digest over a canonical
      listing, on `Program.described`'s shape. RED first: two machines
      differing only in a declared range have different identities, and
      re-compiling one machine twice gives the same one.
- [x] 2.8 Implement `limits` (design §9) with `crossing_tolerance` and
      `max_crossings` only, and a test asserting the other three running
      limits are absent.
- [x] 2.9 RED then green: `clocked_of(root)` (design §12) on `program_of`'s
      shape — construct `Sim(root)`, read the compiled machine and
      `dict(sim.initial.values)`, restore every node's snapshot and re-render
      in a `finally`. Assert a tree posed at chosen driver values holds
      exactly the same snapshots and rendered operations afterwards.

## 3. `$own` cannot travel, and the minted name (design §8)

- [x] 3.1 RED: assert directly that `'$own'` is not a name of the document's
      expression language — `core/expressions.py:25` admits `$t` and nothing
      else `$`-prefixed — so a bound published with it fails to parse. This
      test exists to pin WHY the minted name is there.
- [x] 3.2 Implement the minted own-name: `_own`, lengthened by a leading
      underscore while any published id matches it, published as
      `clocked.own`, and substituted for `_OWN` in every published bound
      expression. Test the collision case with a tree declaring a driver
      literally named `_own`.
- [x] 3.3 Assert the shared expression parser and `bind_expressions` are
      UNCHANGED, by diff.

## 4. The document: version 8, the tables, the object (design §1-§5)

- [x] 4.1 RED: `document_version` gives 8 for a clocked root — including a
      clocked root that also carries a flexible leaf and a non-empty
      `bindings` table — and never for a stateless one. Test each rung of the
      ladder, 2 through 8.
- [x] 4.2 Implement `CLOCKED_DOCUMENT_VERSION = 8` and the eighth rung of
      `document_version` (`core/serializer.py:446-484`), clocked dominating.
- [x] 4.3 Implement `states_table` over the `drivers_table` rules
      (`serializer.py:352-376`) — the same five fields, keys sorted — and a
      test that the two tables name disjoint id sets.
- [x] 4.4 Implement `compiled_clocked(node)` and `clocked_block` in the
      serializer beside `compiled_program`/`program_block`, with the clocked
      import deferred to that one place, and a test that importing the
      serializer imports no clocked module.
- [x] 4.5 RED then green: `document_body(..., clocked=...)` publishes
      `version: 8`, `states` and `clocked` in their fixed positions, and
      `bind_document` compiles the clocked expression slots in the SAME pass
      as the tree's — a subexpression shared between a commit law and a pose
      expression appears once as a `bindings` entry.
- [x] 4.6 Implement `_collect_clocked_slots` and extend `bind_document`'s id
      set with the states' keys, the clock and the own-name, and test that a
      minted `_b` name can collide with none of them.
- [x] 4.7 Re-aim the gate (design §2): `_refuse_a_clocked_model` becomes the
      refusal of a clocked tree published WITHOUT its compiled machine.
      INVERT the existing refusal test in `tests/` — the one asserting a
      clocked model is refused becomes the one asserting it publishes — and
      add the producer-error test.
- [x] 4.8 Assert that a stateless tree still costs `document_body` exactly one
      structural walk that renders nothing.

## 5. The clock, `$t`, and `symbolic_document` (design §10, §11)

- [x] 5.1 RED: a clocked root declaring `Time.elapsed()` whose part is posed
      from `self.time` publishes the free name `time`, and `clocked.clock`
      reads `"time"`.
- [x] 5.2 Implement the one line in `symbolic_document`'s clocked branch —
      `target._states[CLOCK_NAME] = symbol(CLOCK_NAME)`, per visited assembly,
      as the running branch already does (`serializer.py:258`) — and NOTHING
      else: no coordinate delivery, no run binder.
- [x] 5.3 RED then green: a clocked root with NO time base publishes the
      animation variable in that same operation, byte for byte as a root
      declaring no base at all, and `clocked.clock` is `null`.
- [x] 5.4 Assert `animation` carries `fps` and `frames` and no `loop` under
      both clocked bases.
- [x] 5.5 Confirm against the source and by test what design §11 measured:
      `drive_tree` binds a state through the same resolver
      (`node/qualified.py:401-416`), `tree_declares_drivers` answers True for
      a state-only tree (`enumeration.py:285-289`), and
      `pendulum.ClockAlone` — an elapsed clocked root with no driver at all —
      publishes rather than being skipped by the early return.
- [x] 5.6 Assert the control refusal is unchanged in both places
      (`serializer.py:250-253`, `sim.py:200-202`) and that a version 8
      document never carries a `controls` key.

## 6. `instructions` under a clocked root (design §14)

- [x] 6.1 Record the probe as a TEST: a clocked root declaring an instruction
      targeting a DRIVER constructs, both forms appear in `sim.instructions`,
      and only `trigger` is refused by name. This corrects the brief's
      assumption and pins the behaviour this cycle does not change.
- [x] 6.2 Rename `instructions_table`'s `running=` parameter to say what it
      means — the document is version 5 or above — updating its docstring and
      its three call sites to pass exactly what they pass today.
- [x] 6.3 RED then green: a version 8 document publishes EVERY declared
      instruction, each with exactly one of `targets` and `by`, and a
      stateless untimed document still omits the relative ones.
- [x] 6.4 Test that an instruction naming a STATE reaches NO document: the
      compile refuses it (`clocked.py:338-347`) and every producer compiles
      before it publishes, so the refusal is structural and not a filter in
      `instructions_table`. Assert the same version 8 document gives a
      published instruction no execution meaning — `trigger` stays refused by
      name.

## 7. The producers (design §15)

- [x] 7.1 `core/builder.py`: call `compiled_clocked` beside
      `compiled_program`, pass the block, and test that a build of a clocked
      model writes a version 8 `viewer.json` and logs the unreadable-version
      warning once.
- [x] 7.2 `core/export.py`: the same, and test that the export is WRITTEN with
      the warning rather than refused.
- [x] 7.3 `viewers/browser.py`: the same, publishing the two tables off the
      compiled machine's own inputs and states as its running branch does
      (`browser.py:98-101`); test that `--renderer web` on a clocked model is
      REFUSED naming version 8, with no browser started, no image written and
      no staging directory left behind.
- [x] 7.4 Test that `--renderer openscad` on a clocked model renders the
      INITIAL BANK, that `--drive` poses a declared driver, and that `--drive`
      naming a state is refused by name.
- [x] 7.5 `tests/test_viewer_bundle.py`: added tests only — a viewer reporting
      `documentVersions` including 8 makes `unreadable_document(8)` `None`,
      one that does not returns the three facts, and a viewer reporting none
      at all is read as `[1, 2, 3, 4]`. Assert `bundle.py` itself is
      UNCHANGED, by diff.
- [x] 7.6 Assert the four producers reach the re-aimed gate: each is tested
      with a clocked tree and no compiled machine and is refused.

## 8. The Curta-shaped fixture (design §17)

- [x] 8.1 Write `tests/clocked_project/calculator.py`: four dials of one
      class, a crank and a ring, a selector driven through a plain `Port` into
      a knob's joint, the stroke relation over the four digits and an operand,
      one clearing relation per dial reading its own digit, the ratchet bound
      on the crank's own coordinate, the freeze pair on the selector's joint,
      and one relation whose law lands a `dtype=int` state on an EXACT HALF
      (design §17), so the half-to-even rounding is a machine and not a
      sentence. One box per part from `tests/clocked_project/parts.py`.
- [x] 8.2 Compute BY HAND the expected bank after a small scripted sequence —
      three strokes with a carry, a clearing sweep, a blocked reverse, a
      blocked selector move mid-stroke — and assert it. No expected value is
      taken from the implementation.
- [x] 8.3 Measure and record: the compile cost of this fixture, the node count
      of its longest published chain (the selector's, through the port and
      the ratio), and the size of its published `clocked` object.

## 9. The corpus (design §16)

- [x] 9.1 Write `tools/generate_clocked_corpus.py` on
      `tools/generate_running_corpus.py`'s shape: the machine list with its
      scripts, `document_of` publishing the machine-bearing keys, the replay
      that records each step, `uncovered_features` over the stated inventory,
      and `build`/`main`.
- [x] 9.2 Implement the refusal recording — the kind and the qualified names,
      with the bank after each refusal asserted equal to the bank before it —
      and NOT the message text.
- [x] 9.3 Implement `uncovered_features` over the full inventory in
      `design.md` §16 and the export spec, stated in the tool rather than
      inferred.
- [x] 9.4 Script the machines: `counter`, `register`, `clearing`, `pawl`,
      `lock`, `freeze`, `gate`, `ties`, `pendulum`, `outside`, `decorative`,
      `units` and `calculator`. Edit NO fixture. The `%`-of-a-negative case
      needs no new class and no edit: `register`'s stroke law is `total % 10`
      and its `operand` driver's `range=(0, 9)` is presentation and clamps
      nothing, so a script that moves `operand` negative asks the question on
      the fixture as it stands. The EXACT-HALF case is the relation added to
      `calculator.py` in task 8.1. Where the inventory needs any other shape no
      fixture has, add a class to `calculator.py` rather than changing an
      existing fixture.
- [x] 9.5 Write `tests/clocked-corpus.json` and record its size and machine
      count.
- [x] 9.6 Write `tests/test_clocked_corpus.py`: the framework reproduces its
      own corpus EXACTLY, floats included, with no tolerance anywhere in the
      comparison; every step is present in order; and each machine's real
      published document equals the fixture's copy.
- [x] 9.7 Test the generator's refusal directly, at least four ways — a
      missing event primitive, a missing tie, a missing clip, a missing
      zero-travel admission — so the corpus's width is visible without running
      the generator.
- [x] 9.8 Implement the generator's EXACTNESS GUARD: refuse a machine whose
      published commit law, event level, constraint level or chain calls a
      transcendental (`sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`)
      or raises to a power, naming the operation and the machine, and test that
      refusal directly. `sqrt` is admitted — IEEE requires it correctly
      rounded. Record what the parity fixture
      (`tools/generate_parity_fixture.py`, ADR-022) already pins for the
      document's own `%`, which is what a chain and a bound carry.
- [x] 9.9 Record in `evidence.md` the basis of the exactness claim, operation
      by operation (design §16), including the property-test numbers from task
      2.4b and the statement that the landing walk is a bit walk
      (`far_side_of`, `program.py:1578-1634`; `_ordinal`,
      `program.py:1029-1041`) which cycle 5 must reproduce as one.

## 10. Golden documents (design §21)

- [x] 10.1 Pin the version 8 documents of `counter`, `register`, `pawl`,
      `pendulum` and `calculator` as committed fixture files, compared
      LITERALLY.
- [x] 10.2 Write `tests/test_clocked_document.py` for everything not already
      covered: the object's key order, the disjoint tables, a decorative
      range publishing as a constant, a chain through a port carrying no port,
      and every free name of every pose expression resolving.

## 11. What must not have moved

- [x] 11.1 Compare, LITERALLY, the documents of section 1.3 published now
      against the files kept then. Any difference is a stop condition.
- [x] 11.2 Re-hash `tests/running-corpus.json` and every
      `tests/running_project` file against section 1.2.
- [x] 11.3 `git diff` `simulation/run.py` and `simulation/program.py`: the
      first must be empty, and the second must contain nothing but what
      design §6, §7 and §12 reuse, each line accounted for.
- [x] 11.4 Assert the `simulation.clocked` counter (`clocked.py:75-89`) reads
      ZERO across a stateless model's construction, pose, `Sim(node, dt)`
      stepping AND publication.
- [x] 11.5 Run the whole suite and compare against the section 1.1 baseline:
      green, no fixture edited, no expected value moved, and the running
      fixtures' timings inside the recorded envelope.

## 12. Records

- [x] 12.1 `docs/scenarios.rst` and `docs/animation.rst`: what a clocked model
      publishes, and what a viewer that cannot read it does.
- [x] 12.2 `HISTORY.rst`.
- [x] 12.3 `workflow/warts.md`: CLOSE "A clocked model cannot be PUBLISHED or
      VIEWED" for the publication half and state plainly that the VIEWING half
      is cycle 5's; record this cycle's own findings, including the brief's
      wrong assumption about instructions under a clocked root, the `$own`
      name that cannot travel, and the exactness claim with what it rests on.
      FILE two `%` warts as their own entries (design §16, §20): the CROSS-MODE
      one — the same law text means the floored remainder under a clocked root
      (the callable is called) and `fmod` under a running root (the graph is
      evaluated) — and the POSE-versus-GRAPH one, framework-wide and
      pre-existing, where a `drives(law=)` taking `%` of a negative poses
      through the callable (`couplings.py:1640-1650`) and publishes through the
      graph, in every document version from 2 upward. Neither is fixed here,
      and say why: fixing them moves versions 5, 6 and 7.
- [x] 12.4 Write `evidence.md`: the red log, every measurement, every
      deviation reported as a deviation, and the open questions.
- [x] 12.5 Extract ONE ADR, candidate **ADR-128** (NODE), after implementation
      and green tests: extending ADR-125, citing ADR-104, ADR-107, ADR-110,
      ADR-111, ADR-126 and ADR-127, naming the Curta and its spike, and
      stating what it does NOT amend. Update `docs/adrs/NODE/README.md` (or
      the index in use) and `docs/architecture.md` if the synthesis moved.
