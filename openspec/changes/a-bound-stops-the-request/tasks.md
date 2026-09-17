Every task below is RED FIRST: the test is written, run, and SEEN to fail
for the stated reason before the change that turns it green. Neither commit
is made until its whole group is green. Every fixture is geometry-free — no
CAD build, no `meshes = True` — and every run uses
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, ONE JOB AT A TIME:
`/home/asa/devel` is a virtiofs mount whose host daemon exhausts file
descriptors under parallel load, and the symptom is an intermittent "Too
many open files" from git, `ls` or a Python import, never a broken venv.

Run everything from inside this worktree with
`PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python`, so
the worktree's package is imported and not the installed one.

`design.md` section numbers are cited where a task implements a decision.

## 1. Fixtures

- [ ] 1.1 `tests/clocked_project/pawl.py`: cycle 1's `Counter` with a
  `crank_dial` child whose `turn = Revolute(range=(lambda turn: 6 *
  floor(turn / 6), None))` and `crank.drives(crank_dial.turn)`. The
  committing relation and the register dials are cycle 1's, unchanged, so
  the only difference from `counter.py` is the pawl.
- [ ] 1.2 `tests/clocked_project/lock.py`: the note's interlock sketch AS
  WRITTEN — a `knob` whose `travel = Prismatic(range=(0, Bound(lambda
  travel, turn: 54 * (turn - 360 * floor(turn / 360) < 1),
  reads=(crank_dial.turn,))))`, `selector.drives(knob.travel, ratio=6)`,
  `crank.drives(crank_dial.turn)`. Kept deliberately: it is the fixture that
  demonstrates the sketch stopping the CRANK with the knob set (design §4).
- [ ] 1.3 `tests/clocked_project/freeze.py`: the same machine with the pair
  of bounds that read the knob's own committed value, gated on the crank's
  phase (design §4). This is the acceptance fixture.
- [ ] 1.4 `tests/clocked_project/bounds_unsupported.py`: a bounded
  coordinate the tree's own `simulate()` binds BY HAND; a chain through a law
  that is not an expression; a `Bound` reading an unreached coordinate; a
  `Bound` reading a port; a self-read chain; a cyclic chain; a curved level;
  a level whose jump surfaces a long request crosses past the maximum. Each
  written so its refusal test can quote the offending declaration.
- [ ] 1.5 `tests/clocked_project/gate.py`: the STATE-reading fixture of
  design §16 — `travel = crank / 100`, `at = floor(crank / 200)` writing
  `opened`, `range=(0, Bound(lambda travel, opened: 3 + 9 * opened,
  reads=(opened,)))`. This is the fixture that discriminates §8 from
  re-clipping, which the pawl cannot. Plus one fixture whose COMMIT carries a
  bounded coordinate out of range.
- [ ] 1.6 `tests/clocked_project/decorative.py` (a ranged joint NOTHING
  binds, admitted as a constant) and `tests/clocked_project/outside.py` (a
  bank standing OUTSIDE a bound whose read holds no value for the enumeration
  to judge), both per design §3, §7 and §16.

## 2. The compile (design §2, §3)

- [ ] 2.1 RED: a test asserting that constructing `Sim` over the PAWL
  compiles one constraint for `crank_dial.turn`, `low`, whose chain's free
  names are exactly the bank ids it reads. Fails: nothing compiles a chain.
- [ ] 2.2 GREEN: `compile_bounds` in `solid_node/simulation/clocked.py` —
  `_compiled_spans` and `_qualified_reads` consumed for the bounds and their
  reads, `_units` and `checked_expression` consumed for the chain, the chain
  composed by SUBSTITUTION and never simplified, intermediate ports
  traversed, and a `Bounded` value object per bounded side holding the
  chain, the bound graph, the read chains and the joint's unit. The three
  cases of design §3 told apart from the REST RENDER's own records — the slot
  holding no value (a CONSTANT chain at its rest value), a relation, wiring
  or derived formula as `slot.binder` (compose through it), a value with no
  binder (the author's hand: refused).
- [ ] 2.3 RED: the message tests for each row of design §3's refusal table,
  asserting the joint, the node, the side and the offending thing are named.
- [ ] 2.4 GREEN: those refusals, at construction, beside cycle 1's.
- [ ] 2.5 Give `_compiled_spans` and `_qualified_reads` the NAME of the
  authority their refusals speak for, so a clocked refusal does not say "the
  run", and assert the running messages unchanged character for character.

## 3. The classification (design §5)

- [ ] 3.1 RED: affine, kinked, jumped and curved levels classified per
  driver; a level no driver moves classified `constant` and not examined.
- [ ] 3.2 GREEN: `_shape_of` over the level with every name but the moving
  driver standing (cycle 1's `_standing_except`), `_plan_of` where the level
  jumps, `_KinkCuts` where it kinks, and the curved refusal by name.
- [ ] 3.3 RED: a jumped level's path partitioned at its own surfaces and
  each piece's skeleton solved; `TooManyCrossings` re-raised as the clocked
  refusal naming the request, the joint, the side and the maximum.
- [ ] 3.4 GREEN: `JumpPlan.cuts` consumed, no second partition written.

## 4. The clip (design §4, §6, §7)

- [ ] 4.1 RED: the level's own-coordinate argument read ONCE, at the
  request's start — the PAWL's one long backwards request and ten short ones
  ending at the SAME value, the last seated tooth, with the per-request
  admissions asserted (one tooth, then nine zeros) and zero admitted from a
  start already on a tooth (design §4, §8, §17).
- [ ] 4.2 GREEN: the level assembled per request — own coordinate as a
  number from the chain at `t = 0`, reads through their chains, standing
  drivers and states as numbers.
- [ ] 4.3 RED: the threshold `max(0, g(0))` on the OUTSIDE fixture — a
  simulation CONSTRUCTED standing beyond a bound moves inward freely, returns
  to exactly where it stood, and admits zero going further out; and the
  DECORATIVE fixture's constant level, outside its pair forever, stopping
  nothing.
- [ ] 4.4 GREEN: the direction test as one threshold.
- [ ] 4.5 RED: the landing — a bound met exactly at a representable value
  lands ON it; a jumped level lands on the last float before its surface
  (asserted with `math.nextafter`); a kinked level solved at its breakpoint.
- [ ] 4.6 GREEN: the ordinal walk to the SATISFIED side, through
  `far_side_of`'s bisection with membership decided by EVALUATING the level.

## 5. The request (design §9, §11)

- [ ] 5.1 RED: the clip precedes the events — a request whose full travel
  would cross three event surfaces and whose clip admits one and a half
  fires exactly ONE event, at the landing the short request fires it at.
- [ ] 5.2 GREEN: the truncation of `delta` at the head of `Clocked.move`,
  with cycle 1's event loop untouched.
- [ ] 5.3 RED: a request stopped at zero travel is ADMITTED — no exception,
  nothing committed, the bank identical entry for entry, one stop reported.
- [ ] 5.4 GREEN: the zero-travel path.
- [ ] 5.5 RED: `Request.admitted` in design units on a scaled driver;
  `Request.stops` in the documented shape; two constraints at ONE landing
  reported as two entries.
- [ ] 5.6 GREEN: the `Stop` value object and the two `Request` fields.
- [ ] 5.7 RED: `sim.stops` bounded under `record=N`, absent without it, and
  no longer refused by name.
- [ ] 5.8 GREEN: the ring in `sim.py` and the removal of `stops` from the
  clocked refusal list.

## 6. One authority (design §10)

- [ ] 6.1 RED: for each fixture, at twenty fractions of a request path, the
  compiled chain's value for every bounded coordinate against the value the
  POSED tree holds there, `math.isclose(rel_tol=1e-12, abs_tol=1e-12)`.
- [ ] 6.2 GREEN: whatever the composition needs to make that true; a failure
  here is a composition that simplified.
- [ ] 6.3 RED: during a REQUEST the enumeration does not judge a compiled
  coordinate — neither `Joint._refuse_out_of_range` nor `refuse_bounds` — and
  a request whose clip lands a coordinate EXACTLY on an inclusive bound is
  admitted; both judgement sites still judge at a pose that is NOT a request,
  and under an untimed and a running root.
- [ ] 6.4 GREEN: the MARK — `(node, joint)` identities held for the duration
  of one request's pose, opened and closed by `Clocked._posed`, consulted at
  the two judgement sites exactly as `run_owned(slot)` already is. Not a
  binder: the relations bind these coordinates and the double-binding rule
  rests on that identity.
- [ ] 6.5 RED: a request whose COMMIT carries a compiled coordinate out of
  range is refused by the CLOCKED simulation's own end-of-request judgement —
  `JointRangeError` naming the node, the joint, the side, the bound its chain
  evaluates over the FINAL bank and the value that chain gives the coordinate
  there — committing nothing and never posing, with the bank, the tree and
  the record standing (cycle 1's scenario, re-asserted).
- [ ] 6.6 GREEN: the end-of-request judgement over the final bank, through
  the same levels and the same thresholds the clip used, made BEFORE the
  tree is posed, with cycle 1's `_posed` atomicity unchanged.

## 7. The acceptance shapes (design §4, §12)

- [ ] 7.1 RED: the FREEZE fixture — the knob free at rest, admitting ZERO
  travel off rest, and the crank running its whole travel with the knob set.
- [ ] 7.2 RED: the LOCK fixture (the note's sketch) stopping the crank at
  phase 1 with the knob set, asserted in the same test, so the correction of
  design §4 is evidence and not an opinion.
- [ ] 7.3 RED: a plain numeric range (`range=(0, 9)`) stopping a request of
  twenty at exactly `9`, inclusive, with the pose accepting it.
- [ ] 7.4 RED: the GATE — one `move('crank', by=1000)` admitting 300 against
  `move('crank', by=200)` then `move('crank', by=800)` admitting 1000, both
  hand-computed, asserted in one test and named there as §8's deliberate
  coarseness. This is the discriminating evidence for §8.
- [ ] 7.5 RED: the DECORATIVE fixture — a ranged joint nothing binds
  constructs, compiles a constant, stops nothing, and is not a refusal even
  when its rest value lies outside the declared pair (design §3).
- [ ] 7.6 RED: the OUTSIDE fixture — the direction test of §7 on a level that
  really moves: inward admitted whole, back to exactly where it stood
  admitted, further out admitting zero.

## 8. Zero behaviour change (design §15)

- [ ] 8.1 The whole existing suite green.
- [ ] 8.2 A running fixture's stop — including one whose bound reads another
  coordinate — unchanged in behaviour, records and messages.
- [ ] 8.3 The pin tumbler lock's close-of-enumeration judgement unchanged,
  and both judgement sites asserted to take their present branch with no
  clocked simulation in existence — the MARK is inert outside a clocked
  request's pose.
- [ ] 8.4 Cycle 1's register fixture, whose joints declare no range: every
  request admits its whole travel, reports no stop, and gives the same
  events and the same bank as before.
- [ ] 8.5 A byte-identical document for an existing published fixture, and
  no clocked path entered by a stateless tree.

## 9. Measurement, records and the ADR

- [ ] 9.1 Take design §18's measurements on the fixtures only and record
  them in `evidence.md`, compared to nothing.
- [ ] 9.2 `docs/scenarios.rst` and `HISTORY.rst`.
- [ ] 9.3 After implementation and tests confirm the final design, extract
  ONE NODE ADR, candidate **ADR-126**, per design §14, and update the ADR
  index. Do not write it before.
- [ ] 9.4 Record in `workflow/warts.md` anything the implementation found
  that this design did not state, and the open questions that survive.
