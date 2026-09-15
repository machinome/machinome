Every task below is RED FIRST: the test is written, run, and seen to fail
for the stated reason before the change that turns it green. Neither
commit is made until its whole group is green. The two fixtures are
geometry-free — no CAD build, no `meshes = True` — and every heavy run
uses `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one job at a time.

## 1. Fixtures

- [ ] 1.1 Add to `tests/running_project/parts.py` nothing new; add to
  `tests/running_project/machine.py` a `missing_tooth` law — the BAND
  gate of design.md §4, written with `solid_node.math.floor` because
  the symbolic vocabulary has no `modulo`:
  `shifted = wheel + GAP; ring * (shifted - 360.0 * floor(shifted / 360.0) >= 2 * GAP)`
  with `GAP` the stated clearance (`0.5` degrees in the fixture, so the
  band is one degree wide and the arithmetic is readable) — a
  `ClearingBody`/`Clearing` pair declaring `ring` and `setter` drivers, a
  wheel whose `turn` is an `Arbor` joint with a rest default in a guarded
  `simulate()`, and one multi-source relation
  `(setter & ring & wheel.turn).drives(wheel.turn, law=...)` whose
  `setter` term is affine and whose `ring` term is the rack window gated
  by the self-read. Expected travel is computed BY HAND in each test,
  never by calling the law.
- [ ] 1.2 Add the refusal fixtures beside it: a continuous read
  (`ring * wheel`), a remainder-only read (`ring * (wheel % 360)`), a
  self-read whose driven end is a plain port, a self-read on a root with
  no time base, a self-read on a `Time(loop=4)` root, a self-read with no
  rest default, a driven GROUP one of whose members the source group
  names (refused, F3), a `.repeat()` broadcast with a self-read
  (admitted), and a knife-edge gate (`wheel % 360 > 0`) for the
  documentation test of 4.8.
- [ ] 1.3 Add `tests/clearing_project/` — a `CurtaInterface`-shaped
  fixture on the source-backed numbers: two rack rows on opposite halves
  with nine teeth each, start angles `9.75` and `10.5` degrees, pitches
  `degrees(3.75 / 52)` and `degrees(3.75 / 49.55)` ring-degrees per
  tooth, `36` wheel-degrees per tooth, stations
  `(130 if counter else 0) - 20 * place`, the ring angle over the middle
  80 % of the clearing control, several wheels declared through
  `.repeat()` where that is the natural shape, and the band gate of 1.1
  with a STATED clearance (the migration substitutes the measured one).
  Expected values are restated in the test from `cleared_position`'s own
  arithmetic, not imported from it.

## 2. Recognition: the coordinate named on both sides is a read

- [ ] 2.1 RED: `tests/test_couplings.py` — a class stating
  `(rack & wheel.turn).drives(wheel.turn, law=...)` is expected to define
  without raising, its record naming `wheel.turn` as both a source and
  its driven end. Fails today with
  `TypeError: wheel.rotation is named as both a source and a driven end`.
- [ ] 2.2 GREEN: `motion/couplings.py` — `_refuse_shared_coordinate`
  becomes `_record_self_read`, recording on the relation the index of the
  source that names its ONE driven end, and REFUSING a driven end that is
  a group. Keep the named-twice-in-one-group refusal untouched, and admit
  the broadcast source member the relation itself drives
  (`BroadcastRef.check`, `Relation.resolve`; `evidence.md` §6).
- [ ] 2.3 RED then GREEN: a driven GROUP one of whose members the source
  group names — itself or a sibling — is REFUSED at class definition
  naming the relation and the coordinate; a `.repeat()` broadcast in
  which each copy reads ITSELF resolves to one record per copy with the
  same slot on both sides, which `spikes/broadcast.py` measured
  implementable in eleven lines over `BroadcastRef.resolve_all`.
- [ ] 2.4 RED then GREEN: `tests/test_couplings.py` — a self-read
  relation on a root declaring no time base, and on a `Time(loop=…)`
  root, is refused at the close of the enumeration naming the relation,
  the class and `Time.running()`. `_step_relation` leaves it unsolved
  there and `_refuse` names it.
- [ ] 2.5 RED then GREEN: under a running root the relation is recorded
  solved `'forward'`, binds nothing at rest, and the author's guarded
  rest default survives (`tests/test_running_simulation.py`). Today the
  guarded shape raises `DoublyBound` and the unguarded one
  `UnreachedCoordinate` — both reproduced in `evidence.md` §2.
- [ ] 2.6 RED then GREEN: a self-read relation with no rest default is
  refused at `Sim` construction by the run's existing "needs a rest value
  for every joint coordinate" message.

## 3. Compile: the edge, the refusals and the order

- [ ] 3.1 RED: `tests/test_running_simulation.py` — constructing the
  fixture of 1.1 compiles. Fails today in `_ordered` with *"the relations
  … form a cycle the run cannot order"* (`evidence.md` §2).
- [ ] 3.2 GREEN: `simulation/program.py` — `_relation_edge` registers the
  self-read source, `Edge` records which `gives` indices read their own
  id, `_ordered` ignores a need an edge itself gives. Assert
  `_reaching_inputs` needs no change by test rather than by reading.
- [ ] 3.3 RED then GREEN: a law whose SKELETON still names the driven
  coordinate is refused at construction by relation identity — covering
  `ring * wheel` and `ring * (wheel % 360)` — with the message the spec
  states.
- [ ] 3.4 RED then GREEN: a self-read whose driven end is a plain port or
  a derived coordinate is refused at construction naming the port.
- [ ] 3.5 GREEN by inspection AND test: `Program.described()` already
  names the read through the law's graph text; assert two roots differing
  only in the read have different identities and that a snapshot of one
  is refused by the other.

## 4. Integrate: the two-layer partition and the landing

- [ ] 4.1 RED: one tick of the fixture of 1.1 from a wheel at `108` with
  a `500`-degree ring sweep is expected to leave the wheel at the band's
  lower edge, `360 - GAP`. Fails today (with 3.2 in place) at `608`, with
  no crossing located — the measured wrong answer in `evidence.md` §2.
- [ ] 4.2 GREEN: `JumpPlan` gains the TWO-LAYER partition — `_partition`
  unchanged over the jump nodes that do NOT depend on the driven
  coordinate, and the dependent nodes walked piece by piece inside each
  of its pieces: branches read in postorder with the driven coordinate at
  the piece's LEFT END value and every other source at the left end too;
  the substituted skeleton giving the coordinate's path; the first
  surface strictly inside the piece solved where the level is affine
  along that path and searched otherwise; the next piece decided from the
  coordinate the pieces so far produced. `_merged`'s folding applies to
  the first layer only. `Edge.increments` takes ADR-107's unchanged path
  in ONE test when the edge has no self-read.
- [ ] 4.3 RED then GREEN: the crossing is recorded in `sim.crossings` and
  NOT in `sim.stops`.
- [ ] 4.4 RED then GREEN: a second sweep of the same fixture leaves an
  already-cleared wheel BIT-IDENTICAL, and its command completes.
- [ ] 4.5 RED then GREEN: ten constructions, one per digit `0 … 324`,
  each ending within `GAP` of the next multiple of `360` in the sweep's
  direction, at the far-side float of the band's edge; the wheel that
  rested at `0` does not move. Then the same ten swept BACKWARD, each
  ending at the band's upper edge, `GAP` above the multiple below.
- [ ] 4.6 RED then GREEN: the ACCURACY CONTRACT — one sweep taken in one
  tick, in twelve, in two hundred and forty, and as four partial commands
  with the ring released between them, agree within
  `1e-9 * max(1, |a|, |b|)`; no stop is recorded, no command retires
  `blocked`, and the total admitted travel is identical.
- [ ] 4.7 RED then GREEN: both sweep directions; reversal with the wheel
  INSIDE the band moves nothing in either direction; reversal while
  engaged returns the wheel to where it started within the agreement
  window; entry and exit of the rack's station window — a LAYER-ONE jump
  over the ring alone, in the same law as the gate — contributes only the
  travel inside it, which is the test that the two layers compose
  (`evidence.md` §8 runs it on the prototype: the station window sorts
  independent, the gate dependent, and 1, 12 and 240 ticks land on the
  same float).
- [ ] 4.8 A DOCUMENTATION test for the knife-edge gate (`wheel % 360 > 0`,
  whose disengaged set is a single value): it asserts only what the
  framework promises — the wheel holds where the far side of the surface
  is the disengaged region and runs on where it is not — and points at
  the `docs/scenarios.rst` paragraph that says a gap has width. No
  requirement scenario promises this failure.
- [ ] 4.9 RED then GREEN: a tick that would cut one self-read law's path
  more than `_MAX_CROSSINGS` times is refused naming the relation, the
  coordinate, the primitive and the count, and commits nothing.
- [ ] 4.10 RED then GREEN — the FAR-SIDE LANDING (F1). RED: with the
  segment's arithmetic alone, a randomized sweep over start, rate, period
  and gap width leaves the gate ENGAGED after the cut in 6.3 % of
  crossings and refuses another 12.7 % as `TooManyCrossings`
  (`evidence.md` §7, measured). GREEN: the coordinate is placed at the
  nearest representable value on the FAR side of the surface, the run
  commits THAT float rather than `value + delta`, and the same sweep
  re-engages zero times in 200 000 trials. The suite carries the
  deterministic core of it: the landing is bit-identical three ticks
  later while the ring runs on, one float back toward the surface reads
  ENGAGED, and both sweep directions land on their own edge of the band.
- [ ] 4.11 RED then GREEN: a wheel standing EXACTLY on a band edge — the
  float a previous sweep landed it at, and the float a rest default puts
  on a digit boundary — is not driven through the band by a piece
  integrated under the wrong branch, swept in either direction; and a
  gate whose two branches each carry the level back across one surface at
  a piece's left end is refused as chattering, naming the relation, the
  coordinate and the primitive, committing nothing.

## 5. Interaction with the rest of the tick

- [ ] 5.1 RED then GREEN (`tests/test_running_stops.py`): a declared
  range on the driven coordinate stops it at its bound EXACTLY, located
  over the same partition, and its bound wins over a landing the same
  segment reported; a stop earlier in the stretch than the gate's
  crossing and vice versa; each crossing recorded at its fraction OF THE
  TICK; and a wheel resting exactly at a band edge, swept both ways, in
  the same file as the on-surface case of 4.11.
- [ ] 5.2 RED then GREEN: a declared range on the RING still blocks as
  its own physical stop, retiring the ring's command `blocked`, while the
  wheels clear only as far as the admitted sweep carried their racks.
- [ ] 5.3 RED then GREEN: a `Bound(..., reads=…)` one of whose reads is a
  self-read driven coordinate samples correctly over the sub-program.
- [ ] 5.4 RED then GREEN: several wheels from one ring input disengage
  independently; an untouched wheel and an unswept register are unchanged.
- [ ] 5.5 RED then GREEN: transactional refusal — a conflict in the
  segment after a self-read cut commits nothing, records no crossing, and
  retires the commands that moved `refused`.
- [ ] 5.6 RED then GREEN: snapshot, restore, reset and bounded recording
  are unchanged across a self-read run; a partial sweep inspected,
  snapshotted and restored replays to the same admitted travel; and the
  bank value a wheel HELD at its gate survives `snapshot`/`restore` BIT
  FOR BIT, the tick after the restore reading disengaged and moving it by
  nothing.

## 6. Regression: nothing without a self-read moves

- [ ] 6.1 `tests/test_running_simulation.py`,
  `tests/test_running_jumps.py`, `tests/test_running_stops.py`,
  `tests/test_running_document.py`, `tests/test_couplings.py` pass
  unchanged. Record the counts.
- [ ] 6.2 `tests/test_running_corpus.py` replays the EXISTING committed
  fixture byte-identically before any regeneration.
- [ ] 6.3 Measure `Train` before and after: the deterministic count of
  graph evaluations per tick is identical and the wall time is inside
  measurement noise. Then TIME the `CurtaInterface` fixture of 1.3 —
  ticks per second and graph evaluations per tick — because its
  rack-station term is a `clamp01` window, whose skeleton is not affine,
  so every self-read crossing of the migrated model falls to the
  64-subdivision search (design.md §11). Record all of it in
  `evidence.md`, so the migration knows the price.
- [ ] 6.4 Run the whole suite once, sequentially, and record the count.

## 7. Publication

- [ ] 7.1 RED then GREEN (`tests/test_running_document.py`): a root with
  a self-read law publishes `version: 6`; the law edge's `needs` holds
  the driven id and its expression's free names are exactly `needs`; no
  key was added to `program`.
- [ ] 7.2 RED then GREEN: a root with NO self-read law publishes a
  byte-identical version 5 document. Extend `tests/base_documents` with
  the new fixture's document if that is the mechanism the suite uses, and
  assert every existing base document is unchanged byte for byte.
- [ ] 7.3 GREEN: `core/serializer.py` — the version ladder learns 6, and
  the CLI's existing "the installed viewer renders versions N…M" warning
  names it.
- [ ] 7.4 RED then GREEN: `tools/generate_running_corpus.py` refuses a
  corpus that exercises no self-read law, and no tick in which such a
  coordinate holds at its gate while the input reaching it moves on.
- [ ] 7.5 Regenerate `tests/running-corpus.json` with the new machines
  added and every existing scenario's expected values byte-identical;
  `tests/test_running_corpus.py` replays it and the document-agreement
  test passes.

## 8. Documentation and record

- [ ] 8.1 `docs/scenarios.rst` — a subsection under "A law that jumps"
  stating the self-read: the sentence, the retained-value reading, the
  piece-by-piece walk, the far-side landing, the WIDTH obligation as a
  BAND about the zero — entered from either side, the dial stopping at
  the edge it arrives at — with the knife-edge gate named as what a gap
  without width does, the rest-default requirement, the one-driven-end
  rule, and the version 6 consequence.
  While there, correct the stale bullet in "What this release refuses"
  that still says a range bound naming a second coordinate is refused —
  ADR-113 landed and that page was never updated (reported separately).
- [ ] 8.2 `HISTORY.rst` — one entry.
- [ ] 8.3 `docs/architecture.md` — the "Simulation" section's running-mode
  paragraph and the "Known gaps and tensions" list.
- [ ] 8.4 Extract **ADR-121** (NODE), "A law may read the coordinate it
  drives", AFTER implementation and at the reviewer's direction:
  re-check that 121 is still free, add it to `docs/adrs/README.md` in
  chronological order, and record the alternatives this change rejected
  with their measurements.
- [ ] 8.5 `evidence.md` — the three failing routes, the deleted-refusal
  measurement, the float sweeps, the `Train` numbers, the suite counts
  and the regenerated corpus's diff summary.
- [ ] 8.6 `openspec validate read-the-driven-coordinate` passes; archive
  the change and sync the three baseline specs.

## 9. Out of this cycle, recorded for the reviewer

- [ ] 9.1 File in `workflow/warts.md`: a gate with no width is silently
  wrong in one direction and is not refused; `a.drives(a)` one-to-one
  still deadlocks into `UnreachedCoordinate`; ADR-113's pushing test is
  net over the stretch; `docs/scenarios.rst` was stale on ADR-113 before
  8.1 fixed it; a DRIVEN GROUP with a self-read is refused in this cycle
  and would need a joint walk over several plans (design.md §1); a
  kinked-but-piecewise-affine skeleton (`clamp01`) falls to the search
  where an exact path exists (design.md §11).
- [ ] 9.2 NOT this cycle: the viewer's execution of a version 6 document
  (`solid-node-viewer`, its own repository and its own cycle, held to the
  corpus 7.5 regenerates), and the Curta's own migration
  (`projects/Calculators/Curta-Type-I-3x`, requirement item 9), whose
  shape design.md §12 states.
