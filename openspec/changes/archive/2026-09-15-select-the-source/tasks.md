Every task below is RED FIRST: the test is written, run, and seen to
fail for the stated reason before the change that turns it green.
Neither commit is made until its whole group is green. Both fixtures are
geometry-free — no CAD build, no `meshes = True` — and every heavy run
uses `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one job at a time.

Expected motion is computed BY HAND in each test, from the arithmetic
restated there, never by calling the law under test.

## 1. Fixtures

- [x] 1.1 Add `tests/carriage_project/` (`__init__.py` and `machine.py`;
  no manifest of its own — `tests/pyproject.toml` is the only
  `[tool.solid-node]` under `tests/` and covers every fixture package
  there, `tests/clearing_project/` included), holding the REDUCED fixture
  of `workflow/docs/curta-shifted-carry-association.md`: `crank`, `shift`
  and `clearing` drivers, two `Shaft`s with a `Revolute` `turn`, one
  `Latch` with a `Prismatic` `travel`, every driven coordinate carrying
  a guarded rest default, and the three relations exactly as
  `simulation/tools/shifted_carry_probe.py` writes them in the
  originating project — the lower wheel gated by `shift < .5`, the
  higher wheel by `shift >= .5` and by the latch when `shift < .5`, the
  latch reading whichever wheel the shift selects — each with its own
  ADR-121 self-read term. Add beside it the FROZEN twin used as ground
  truth: the same laws with `shift` replaced by the literal `0` and by
  the literal `1`, which compile as ordinary acyclic programs today.
- [x] 1.2 Add the CURTA-SHAPED fixture to the same package: four dials on
  a carriage and three fixed levers; a `position` driver wired to a
  carriage joint coordinate by `position.drives(seat.turn, ratio=20)`,
  so every selector reads the JOINT and not the driver; six working
  positions twenty degrees apart written as pairs of comparisons on
  `seat.turn / 20`; a `lift` driver whose joint coordinate is a SECOND
  selector factor disengaging every association while the carriage is
  lifted; each lever's latch as an ADR-121 self-read hysteresis (set by
  the dial's pin, held, reset by the crank's cam); a missing-tooth
  clearing self-read on each dial; and a `Bound(..., reads=)` interlock
  on the carriage coordinate refusing a shift unless lifted.
- [x] 1.3 Add the REFUSAL fixtures beside them: the reduced fixture with
  its selections removed and its SELF-READ terms KEPT (an unconditional
  cycle that reaches `_ordered` today — measured on this worktree, it
  prints today's cycle message verbatim); the same with the self-reads
  ALSO removed (an unconditional cycle that today is refused
  `DoublyBound` by the rest render and after this cycle is refused by the
  compile, for the scenario "A cycle with no self-read and no selection
  is refused by the compile"); the reduced fixture's SELECTED cycle with
  every self-read removed (`spikes/reduced.py`'s `NoSelfRead`, refused
  `DoublyBound` today and ADMITTED after this cycle); a cycle one of
  whose steps is a wiring — the wiring's source being a JOINT of the
  declaring parent that another relation determines, which is what makes
  a wiring reachable on a cycle at all (`declarative.py:346`); a
  cycle one of whose steps is a derived coordinate; a block one of whose
  driven ends is a plain port; a block member whose driven end is a
  group; a block relation with no rest default; a block whose only gate
  is a `sign`, so no source is switched and the unconditional cycle
  stands; a block whose two selections are both active at some reachable
  value of the selecting input (for the run-time refusal of task 6.1);
  a cycle of plain-port relations that reaches NO bank coordinate, which
  must be left alone and behave exactly as it does today; and the same
  reduced fixture under no time base and under `Time(loop=4)`.

## 2. Recognition: blocks, selectors and switched sources

- [x] 2.1 RED: `tests/test_running_simulation.py` — the reduced fixture
  is expected to CONSTRUCT. Fails today with `UnsupportedLaw: the
  relations ... form a cycle the run cannot order`, the message
  `spikes/reduced.py` reproduces verbatim.
- [x] 2.2 RED: a test that the unconditional cycle of 1.3 WITH ITS
  SELF-READS KEPT still refuses with today's message, naming both
  relations. That is the fixture that actually reaches `_ordered` today —
  a cycle with no self-read anywhere never gets past the rest render —
  so this test PASSES today and must go on passing. It is written first
  because no test pins that refusal anywhere in the suite (verified:
  `grep -rn 'form a cycle' tests/` finds nothing) and the specs never
  stated it. Record in the same test file, as its sibling, which refusal
  each 1.3 fixture gets TODAY: cycle message with self-reads kept,
  `DoublyBound` with them removed and rest guards present,
  `UnreachedCoordinate` with neither.
- [x] 2.3 GREEN: `program.py` — the union dependency graph over the
  compiled candidate edges with a self-need excluded, its nontrivial
  SCCs as BLOCKS, and `_ordered` contracting each block to one node.
  Keep today's message word for word for a block that turns out to be
  unconditional (2.5); the acyclic path is untouched.
- [x] 2.4 GREEN: the SELECTOR classification on each law edge's plan —
  a jump node whose level quantity, with placeholders resolved
  transitively into their own jumps' levels, names no coordinate the
  block gives — and the FOLD that decides a switched source
  (`x*0 → 0`, `0*x → 0`, `0/x → 0`, `0+y → y`, `y+0 → y`, `y−0 → y`,
  `0−y → −y`, a surviving placeholder followed into its own folded
  level), with a placeholder FOLDABLE only where its primitive holds the
  zero branch over an interval of its level — `floor`, `ceil`, `%` and a
  comparison, and NOT `sign` (`_branch_of`, `program.py:527`, returns
  `0.0` for `sign` only at exactly `0.0`). `spikes/fold.py` measured the
  single-placeholder folds on the reduced fixture; a unit test asserts
  the same two fold results it printed, asserts the MONOTONICITY the
  single all-zero fold rests on — the reads under every foldable selector
  at zero are a SUBSET of the reads under each one alone, on that same
  fixture — and asserts that a `sign` gate leaves its source
  unconditional.
- [x] 2.5 RED then GREEN: the construction refusals of design.md §2,
  each by relation identity and each against a fixture of 1.3 — a wiring
  in a block (the wiring reachable on a cycle through a parent joint
  another relation determines); a derived coordinate in a block; a block
  whose members' UNCONDITIONAL dependencies are still cyclic, including
  the `sign`-gated fixture; an intermediate among a block's driven ends;
  a block member driving a group.
- [x] 2.6 RED then GREEN: `Program.described()` gains one `block` line
  per block naming its members' driven ids in the block's own order
  (design.md §3: the candidates' order — `_units`' tree order,
  declaration order within an assembly, copy order within a broadcast),
  followed CONTIGUOUSLY by each member's ordinary edge line, so the
  identity still covers every member's expression. The test asserts the
  block line's position and the member lines after it; that two programs
  whose block membership differs have different identities; and that a
  program with NO block prints exactly what it printed before —
  `described()` and `identity` of an existing fixture unchanged,
  character for character.

## 3. Rest and initialization

- [x] 3.1 RED: the reduced fixture's rest bank is expected to be each
  driven coordinate's own guarded default, with nothing refused. The
  reduced fixture itself fails today at the COMPILE (its self-reads
  already carry it past the rest render); its `NoSelfRead` twin of 1.3
  fails today at the REST RENDER, before the compile — `spikes/reduced.py`
  measured `DoublyBound` with rest guards and `UnreachedCoordinate`
  without — which is why membership cannot wait for the compile. Assert
  the rest bank on BOTH.
- [x] 3.2 GREEN: `program.py` gains `_block_members(root)`, a pre-pass
  over `_units(root)` computing the SCCs over resolved driven SLOTS from
  EVERY relation record, wiring and derived coordinate that walk returns,
  each taken FORWARD AS DECLARED; it keeps only an SCC holding at least
  one BANKED driven end and marks the RELATION RECORDS in it — a
  single-ended relation included, a wiring and a derived coordinate not
  (they are in the graph to close the cycle, and the compile is what
  refuses them). `sim.py` calls it in the running branch of `__init__`,
  between `release_tree(node)` and `_bind_initial(state)`;
  `couplings.py::_step_relation` skips a marked record exactly where it
  skips a self-read, under a running root and only there.
- [x] 3.3 RED then GREEN: a block relation with no rest default is
  refused naming the qualified id, with the run's existing message for
  an unbound joint coordinate.
- [x] 3.4 RED then GREEN: under no time base and under `Time(loop=4)`
  the same relations are solved, deferred and refused by the ordinary
  enumeration EXACTLY as they are today — the test asserts the same
  exception type and message as the fixture gives on `main`.
- [x] 3.5 GREEN: assert the pre-pass's membership and the compile's
  membership AGREE, raising an internal error naming both if they do
  not (design.md's fifth risk). Pin the shape that would have fired it
  under the earlier rule: the 1.3 fixture whose cycle reaches no bank
  coordinate constructs, is left unmarked, and is posed exactly as it is
  today.
- [x] 3.6 RED then GREEN: the marks do not outlive a simulation. The
  marks live on the RECORDS, which `resolve_declared_relations`
  (`couplings.py:1785`) writes once per instance CONSTRUCTION and no
  render rewrites, so (a) `release_tree` (`program.py:3076`) CLEARS them
  with the run's claim and a second `Sim` over the same tree — the
  `ScenarioTest` shape — gets the same bank as the first; (b) running the
  pre-pass twice over one tree gives the same marks; and (c) a NON-running
  `Sim` constructed over a tree a running one marked behaves exactly as
  it does today, `_step_relation`'s running-root guard being what makes
  that true.
- [x] 3.7 RED then GREEN: the two moved refusals of design.md §5 — the
  1.3 fixture with selections and no self-read CONSTRUCTS where it is
  `DoublyBound` today, and the unconditional one with no self-read is
  refused by the COMPILE's cycle message where it is `DoublyBound` today.
  Both assert the new message, and the test names the old one so the move
  is visible in the diff.

## 4. Evaluation: the block runs piece by piece

- [x] 4.1 RED: the reduced fixture cranked with `shift` at `0`, and
  again at `1`, is expected to equal the FROZEN twin of 1.1 at that
  value, coordinate for coordinate within the run's agreement window.
  Fails today at construction (2.1), and would fail on the numbers under
  any arbitrary order: `spikes/arbitrary.py` measured
  `higher.turn = 1.48` under declaration order and `0.0` under the
  reverse, against the frozen twin's `1.5000000000000018`.
- [x] 4.2 GREEN: the compound `block` `Edge` — union `needs`, all
  members' `gives`, `affine` False on every give, `values` empty, `cuts`
  the selector partition merged with each member's own — and its
  `increments`: locate the selectors' crossings over the stretch through
  `JumpPlan`'s existing `_crossings_of`/`_deduplicated`/`_merged`/
  `_MAX_CROSSINGS`; read each selector's branch at the piece MIDPOINT;
  fold and Kahn the active graph, memoised per vector of ACTUAL branch
  VALUES (integers for `floor`/`ceil`/`%`, not booleans); run the members
  over the piece with the selector placeholders FORCED, the in-block
  values the order has already determined ADVANCED, and an in-block
  source this piece switched out but has not yet determined at its
  block-advanced value with a delta of `0.0`; sum the increments,
  ACCUMULATE a landed coordinate's absolute value across the later
  pieces, and rescale every reported crossing by `a + t*(b − a)`.
  It must be complete with `crossings`, `tick` and `landings` all
  omitted, because `Run._pushes`, `Run._along` and `Program.response`
  call it that way. `spikes/pieces.py` measured the composition:
  `0.5 + 0.5 + 0.0 = 1.0`, landing `1.0`, the crossing back at fraction
  `0.5`.
- [x] 4.3 RED then GREEN: a unit test that a member's plan evaluated with
  a selector placeholder FORCED gives the same value the block read at
  the midpoint, and that the member relocates NO crossing of that node —
  the property design.md §3 replaces the reviewer's ulp argument with.
  Include the case that makes the forcing reach the whole plan: a member
  whose forced selector is a LAYER-ONE node of its plan and which ALSO
  reads the coordinate it drives (the Curta lever — selector on the
  carriage, latch on its own travel), asserting that the forced branch
  holds through `_Retained.outer`'s partition, through `_decide` and
  `_tentative`, through the `_probe`/`_searched` sampling and through the
  far-side landing, and that flipping the forced branch changes the
  answer (so the assertion is not vacuous).
- [x] 4.4 RED then GREEN: `tests/test_running_jumps.py` — a selector
  crossing is recorded in `sim.crossings` under the member whose law
  states it, at its fraction of the TICK, and is NOT recorded in
  `sim.stops`.
- [x] 4.5 RED then GREEN: a selection change alone moves nothing —
  `shift` driven from `0` to `1` in one tick with every other input
  still, and every block coordinate committing the float it held, bit
  for bit.
- [x] 4.6 RED then GREEN: the ACCURACY CONTRACT — the same crank travel
  as one tick, as twelve and as two hundred and forty, each from one
  restored snapshot, agreeing within `1e-9*max(1, |a|, |b|)` per
  coordinate AND for each command's admitted travel, and EXACTLY for
  every command's status and every discrete reading. Admitted travel is
  asserted within the window and NOT bit for bit: `Command.admits`
  (`run.py:183-200`) returns one difference per tick and `Run.integrate`
  sums them (`run.py:645`), so 240 summed differences and one difference
  are ulps apart by construction — check the failure first by asserting
  equality and watching it fail, so the window is justified rather than
  assumed. Choose the fixture's thresholds and bounds away from every
  tick's end, which is the contract's stated precondition.
- [x] 4.7 RED then GREEN: a LANDING followed by MOTION in a later piece
  of the same stretch — the block lands a coordinate at its gate in one
  piece and a selection the next crossing brings in advances it further —
  commits the block's ADVANCED ABSOLUTE, not the landing. Red against
  "report the last landing", which commits the landing and silently loses
  the later increment because `Run._landed` (`run.py:661`) overwrites
  `value + delta` with whatever the edge reported. `spikes/pieces.py`
  cannot see this: its landing is in the second piece and the third
  piece's increment is `0.0`.
- [x] 4.8 RED then GREEN: a member evaluated on a piece with an in-block
  source SWITCHED OUT and handed a delta of `0.0` gives the same
  increment as the same piece with that source moving — the safety
  design.md §3 argues from the fold, tested rather than trusted.

## 5. Stops, constraints and retention

- [x] 5.1 RED then GREEN: `tests/test_running_stops.py` — a declared
  range on a coordinate the block drives stops it, located through the
  block's searched path, committed AT its bound, with the stop recorded
  and the pushing inputs retired `blocked`.
- [x] 5.2 RED then GREEN: a landing and a stop on the same block
  coordinate in one segment — the bound wins, as `_landed` running
  before the stops already decides.
- [x] 5.3 RED then GREEN: a stop EARLIER in the stretch than a selector
  crossing, and a selector crossing earlier than a stop; both recorded,
  in order, from one tick.
- [x] 5.4 RED then GREEN: an input that reaches a stopped block
  coordinate ONLY through a currently inactive selection is not retired
  `blocked` and admits its whole travel — ADR-113's pushing test through
  the block, requirement-note item 2. Assert the mechanism as well as the
  answer: `Run._pushes` runs the WHOLE block under the displacement
  before its `key in edge.gives` break, and a displacement probe over a
  genuinely cyclic piece refuses exactly as the tick over that piece
  does — same midpoint reading, same order, same message — so a stop's
  blocked group cannot become a function of the probe.
- [x] 5.5 RED then GREEN: the Curta-shaped fixture's interlock — a
  `Bound(..., reads=)` on the carriage coordinate refusing a shift
  unless lifted — stops the shift at its restraint while a lever stands
  SET, and neither discards nor completes the pending carry.
- [x] 5.6 RED then GREEN: RETENTION — shift away and back preserves
  every wheel's and every lever's value except motion the modeled
  mechanism caused; a lever left SET at one position stays set until the
  crank's own reset term returns it, and then acts on the wheel it now
  faces.

## 6. The run-time refusal

- [x] 6.1 RED then GREEN: the fixture of 1.3 whose two selections are
  both active at some reachable value refuses the TICK naming the
  piece's selector branches and the relations on the cycle;
  TRANSACTIONALLY — `sim.state` equals the previous tick's bank exactly,
  `sim.tick` did not advance, `sim.crossings` and `sim.stops` gained
  nothing, and every command that moved an input reports `refused`.

## 7. Composition with ADR-121

- [x] 7.1 RED then GREEN: `tests/test_running_reads.py` — a block member
  that also READS the coordinate it drives walks its two layers inside
  each selector piece, and a tick carrying both a selector crossing and
  a self-read crossing records both at their own fractions and commits
  the latch at the value its walk left it at.
- [x] 7.2 GREEN: assert that the `_Retained` split is decided ONCE at
  compile with the selectors still symbolic (design.md §6), so a
  non-block law's two-layer partition is character-for-character what it
  is today.

## 8. Publication and the corpus

- [x] 8.1 RED then GREEN: `tests/test_running_document.py` — a program
  carrying a block publishes `version: 7`; a program with none publishes
  byte-identically at the version it always did, asserted over an
  existing fixture's whole document.
- [x] 8.2 GREEN: `serializer.py` — `BLOCK_DOCUMENT_VERSION = 7`,
  `_carries_a_block` reading the block off the published `edges` exactly
  as a consumer would, and `document_version` with 7 dominating 6.
- [x] 8.3 RED then GREEN: a block's members publish as ORDINARY law
  edges, contiguously at the block's position, in the block's own
  deterministic order; no new key appears anywhere in `program`; and a
  selector is derivable from the published `plans[i].jumps[j].level`
  alone. `Program._placeholders` and `Program.published`
  (`program.py:1713`, `1620`) walk `self.edges` in step and index one by
  the other, so both must EXPAND a block into its members in that same
  order — the test asserts that placeholder minting over a document with
  a block is still `_j0`, `_j1`, … in edge order and then postorder over
  the flat list of law edges.
- [x] 8.4 GREEN: `tools/generate_running_corpus.py` — three new
  `REQUIRED` entries (`'a switched source'`, `'a selection crossing
  inside a tick'`, `'a tick carrying both a selection crossing and a
  stop'`), each detected from the document and the tick log the way the
  existing entries are, plus the carriage machine in `CORPUS`.
- [x] 8.5 RED then GREEN: `tests/test_running_corpus.py` — the generator
  REFUSES a corpus lacking any of the three, and the committed
  `tests/running-corpus.json` replays exactly, every PRE-EXISTING
  machine's entry byte-identical to what it holds today.
- [x] 8.6 Regenerate `tests/running-corpus.json` through
  `tools/generate_running_corpus.py` and confirm by diff that only the
  new machine's entry was added.

## 9. Regression, cost and documentation

- [x] 9.1 Run `tests/test_running_simulation.py`,
  `tests/test_running_jumps.py`, `tests/test_running_stops.py`,
  `tests/test_running_reads.py`, `tests/test_running_document.py`,
  `tests/test_running_corpus.py`, `tests/test_couplings.py`,
  `tests/test_export.py` and `tests/test_build_publication.py`
  unchanged, then the whole suite once.
- [x] 9.2 Measure the cost, per design.md §10: the `Train` bench as the
  control, and the carriage fixture at `dt = 0.02` — a revolution at a
  fixed position, the same with a range on a block coordinate so every
  tick pays the search, and a tick crossing a detent — reported as
  ms/tick beside the architecture's existing numbers and recorded in the
  change's evidence.
- [x] 9.3 `docs/driving.rst` and `docs/scenarios.rst`: a section on a
  selected association — what a selector is, what the fold means for a
  law an author writes (including why a `sign` gate does not switch a
  source and a comparison does), the run-time refusal and what it names,
  and the rest-default obligation on every block coordinate.
- [x] 9.4 `HISTORY.rst`: the Unreleased entry, in the voice of the
  self-read entry above it, including the **BREAKING for consumers**
  version 7 sentence.
- [x] 9.5 `workflow/docs/curta-shifted-carry-association.md`: the status
  line becomes "Taken up as `select-the-source`", with the ADR number
  once it exists.
- [x] 9.6 AFTER implementation, under the reviewer's direction, and in
  ONE pass because the two are the same act of ratification: extract
  **ADR-122** (NODE) — a selection decides which sources a law reads,
  AMENDING ADR-106's "edges are ordered by Kahn over the ends they
  determine" and specifying the cycle refusal ADR-106 left implicit —
  update `docs/adrs/README.md`, and rewrite `docs/architecture.md`'s
  Simulation section to match: the "edges ordered by Kahn" sentence, and
  the paragraph after the self-read one. The overview describes the
  system that exists, so it moves when the decision is recorded, not
  when the implementer's pass ends.

## 10. Out of scope, recorded

- [x] 10.1 Record in the change's report, for the reviewer to file in
  `workflow/warts.md`: (a) a block give is never classified affine, so
  every stop on one is searched (design.md §10); (b) `Program.sources`
  treats a block as one node, so a stop's candidate list is over-broad
  and `_pushes` pays for it on a blocking tick; (c) a block member
  driving a GROUP is refused and no mechanism has asked for one yet;
  (d) `_affine_in_sources` calls any CALL non-affine, so a `clamp01`
  anywhere in a selector's level sends it to the 64-sample search — a
  pre-existing wart this cycle's Curta-shaped fixture will hit, and the
  reason design.md §12 tells the project to write comparisons rather
  than the pose model's `clamp01` hat; (e) a `sign`-gated dependency is
  never switched, because `sign`'s zero branch is one point and not an
  interval, so a mechanism written that way is refused at construction
  with the cycle message — intended, and worth a follow-up if any
  mechanism ever asks for it (design.md §2 and the risks).
- [x] 10.2 Record that MIGRATING THE CURTA is another agent's project
  work, with design.md §12's list of what it must do.
