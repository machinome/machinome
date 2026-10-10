## Why

The originating project is `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation` at `9fb725f`. Its project-level spike — worktree
`WTs/clocked-spike`, commits `0968563` `a56937e` `bcf2017`, recorded in
`simulation/docs/clocked-spike-2026-09-16.md` — emulated the clocked
discipline in ordinary Python and replayed eighteen scenarios against a
recorded `OperatingCurta` oracle (574 ticks, 439.2 s). It settled the
previous cycle's question and left exactly one open, its **finding 4**:

> `blocked_crank_lift` and the ratchet both need a violated `Bound` to CLIP
> a request rather than reject a pose, with the events located on the
> clipped path. The harness does exactly that and records every clip; the
> note names this as the one thing the clocked mode borrows from the run.

That is not a convenience. The spike's **finding 5** is that every interlock
the Curta needs is already expressible — eight locks, each a `Bound` on a
joint (ADR-109, ADR-113), each quoted from the manufacturer's booklet, and
none of them needing a new framework idea. What the framework cannot do is
OBEY them: cycle 1 (`declare-the-state`, ADR-125) states plainly in its
design §11 that a violated `Bound` is still an impossible pose, so a request
that would drive a mechanism through a stop is REFUSED WHOLE and commits
nothing. A machine whose interlocks refuse the request instead of stopping
the handle is a machine no maker can operate: the whole point of the eight
locks is that the Curta *cannot* be misused, not that misusing it deletes
the stroke you were half way through.

Three of the spike's scenarios say it concretely. `blocked_crank_lift` lifts
the crank past its 9 mm stroke and expects the lift to stop at 9 mm.
`crank_reversal` drags the crank backwards, where the anti-reversal pawl —
the booklet's "it is always locked against backward turns" — must hold it at
the last seated tooth; without the pawl, cycle 1's own measurement is that
the additive law commits a SECOND addition, 9 → 18. `mid_stroke_carriage_
shift` moves the carriage while the crank is off rest, which the booklet
forbids and the clocked closed form gets wrong (90 against the operating
model's 9) unless the lock holds the carriage still.

The framework already knows what a stop is. ADR-108 made a declared range a
PHYSICAL STOP located inside a running tick, ADR-109 made a bound an
expression evaluated at the committed state, and ADR-113 made it a
constraint that may read other coordinates and stop what carries it outward.
None of that reaches a clocked root, whose request is not a tick and whose
bank holds no joint coordinate at all. Cycle 1 wrote its solver so that this
cycle's clip is a TRUNCATION OF THE REQUEST'S TRAVEL BEFORE EVENT LOCATION
rather than a second locator; this change is that truncation.

## What Changes

- **A declared `range` is a STOP on a clocked request path.** Under a
  clocked root a request that would carry a bounded JOINT coordinate past a
  declared bound STOPS at the bound: the moving driver's travel is CLIPPED
  to the point where the bound is met, exactly — solved, never searched —
  and cycle 1's events are then located on the CLIPPED path only. Since a
  clocked request moves ONE input, ADR-108's "group of inputs that push" is
  that one input, and nothing else needs deciding. `Driver.range` stays what
  it has always been: presentation metadata, never a clamp and never a stop.
- **A request stopped at zero travel is ADMITTED, not refused.** It moves
  nothing, fires nothing, poses nothing new and reports its stop. That is
  what an interlock does: the selector does not move while the crank is off
  rest, and the maker is told why.
- **Every bound is compiled ONCE, at simulation construction, into a
  CONSTRAINT LEVEL over the bank and the one moving driver.** A bounded
  coordinate reaches the bank through a chain of relations whose laws are
  expressions — `ratio`/`offset` wirings, derived-coordinate formulas and
  `law=` relations, through intermediate PORTS as well as joints — and the
  bound's own expression composes over it. The composed level is classified
  structurally, exactly as cycle 1 classifies an `at`: affine is SOLVED by
  one division, kinked is CUT at its own breakpoints (ADR-123), a level that
  JUMPS is partitioned at its own jump surfaces and solved piece by piece
  (ADR-107), and a CURVED level is refused at construction by name. No
  sampling, no bisection, and no tolerance is introduced anywhere.
- **A bound is read as ADR-109 and ADR-113 read it, with the REQUEST as the
  quantum the tick was.** The bound's own coordinate takes the value it
  holds when the request STARTS — which is what makes the ratchet's lower
  bound the last seated tooth, and what makes an interlock stating a FREEZE
  (`this may not move while the crank is off rest`) expressible at all. Each
  `reads=` coordinate takes its value ALONG THE PATH, through its own
  compiled chain. A read of a declared driver or a declared STATE is
  admitted and is the cheapest read there is, being constant between events.
- **What the framework cannot follow, it refuses at construction, by
  name** — the temperament cycle 1 set for a state nothing writes and a
  relation no driver can reach. A bounded coordinate, or a coordinate a
  `Bound` reads, that the bank cannot reach through such a chain (a joint
  posed BY HAND in `simulate()`, an author-bound port, a law that is not an
  expression) is refused, naming the joint, the side, and where the chain
  broke. A stop that can never stop is a mistake in the model. A ranged
  joint NOTHING binds — no relation, no wiring, no author code: a decorative
  range on a part that rests — is ADMITTED instead, compiled as the constant
  it is, examined by no request and costing nothing.
- **A request reports what it admitted and where it stopped.** `move`
  returns the cycle 1 value object with two more fields: `admitted`, the
  travel actually made in design units, and `stops`, the bounds met — each
  naming the bounded coordinate, the side, the bound's evaluated value, the
  coordinate's value there, the driver's value and the fraction of the
  requested travel. `record=N` keeps a bounded ring `sim.stops` beside
  `sim.commits`, which LIFTS cycle 1's refusal of that name: a clocked model
  has no clock, but it does have stops.
- **One authority judges one binding.** During a REQUEST the clocked
  simulation is the SOLE AUTHORITY for the constraints it compiled: the pose
  that ends a request does not judge those coordinates, and the clocked
  simulation judges them itself at the end of every request, over the final
  bank, THROUGH THE SAME CHAIN the clip used — so one arithmetic decides a
  stop and no legitimate request can be refused by a float's worth of
  disagreement between two evaluation orders. A commit that carries a
  compiled coordinate outside its bound still raises `JointRangeError` and
  still refuses the whole request, which commits nothing, exactly as cycle 1
  states. This is ADR-113's own rule for the run (`refuse_bounds` already
  skips a coordinate the run owns), taken for the clocked request.
- **A pose that is NOT a request goes on being judged by the enumeration.**
  A `Bound` violated at construction, by `state=` or by `restore` is still an
  impossible pose raising `JointRangeError`: those poses have no path and no
  chain, and a machine cannot be PUT where it cannot BE. Nothing about the
  untimed or running reading of a range changes.
- **Zero behaviour change** for a stateless root, an untimed root and a
  RUNNING root: ADR-108's tick, ADR-113's constraint sampling and the
  close-of-enumeration judgement are untouched, and a tree that declares no
  `State` enters no clocked path at all. A requirement with a test, again.

## Capabilities

### New Capabilities

None. A declared range already means "where this coordinate may be"; this
change gives that declaration its clocked reading, beside the running one
ADR-108 gave it and the untimed one it has always had.

### Modified Capabilities

- `simulation`: ONE ADDED requirement — "A bound stops a clocked request on
  its path" — stating the compile, the classification, the clip, the reading
  rule for the own coordinate and the reads, the reporting and every
  refusal; and ONE MODIFIED — "A clocked simulation solves a request path
  event by event", whose closing paragraph today says a request SHALL NOT be
  clipped by a bound and whose refused-name list today includes `stops`.
- `joints`: ONE MODIFIED requirement — "A declared range refuses a binding
  outside it", which today says that under every root but a running one a
  range refuses a binding and never clamps or stops, and that a coordinate a
  RUNNING simulation owns is not judged by the enumeration. What changes is
  the sentence that names where a range is additionally a stop, and one
  sentence putting a coordinate a CLOCKED simulation compiled a constraint
  for beside the run-owned one: at the pose a REQUEST makes it is judged by
  the clocked simulation and not by the enumeration. Every other particular
  of the bind-time and close-of-enumeration judgements is unchanged.

## Impact

- `solid_node/simulation/clocked.py`: the constraint compile
  (`compile_constraints`, a `Constrained` beside cycle 1's `Committing`),
  the clip at the head of `Clocked.move`, the `Stop` value object and the
  two new `Request` fields. A CONSUMER of `program.py` — `_compiled_spans`
  and `_qualified_reads` for the bounds, `_units` and `checked_expression`
  for the chain, `_plan_of`/`JumpPlan.cuts` for a jumped level, `_shape_of`
  and `_KinkCuts` for the classification, `far_side_of`'s ordinal walk for
  the landing — adding no second locator and no second law inspection.
- `solid_node/simulation/program.py`: no behaviour change. `_compiled_spans`
  and `_qualified_reads` are given the name of the authority they speak for,
  so a clocked refusal does not say "the run".
- `solid_node/motion/joints.py` and `solid_node/motion/couplings.py`: the two
  judgement sites (`Joint._refuse_out_of_range`, `refuse_bounds`) consult the
  clocked simulation's mark exactly as `refuse_bounds` already consults
  `run_owned`, and take their present branch everywhere else — no clocked
  simulation, no mark, and an untimed or running tree is judged as it is
  today.
- `solid_node/simulation/sim.py`: `sim.stops` under `record=N`, and its
  removal from the clocked refusal list.
- `tests/clocked_project/`: a PAWL fixture (a one-argument floor bound on
  the crank's own joint, beside cycle 1's register), a LOCK fixture (a
  `Bound` on a selector joint reading the crank joint through an affine
  relation, closed off rest), a FREEZE fixture (the interlock's real shape,
  a bound reading its own committed value), and the refusal fixtures.
- `tests/test_clocked_bounds.py` (new); `docs/scenarios.rst`; `HISTORY.rst`.
- One ADR, candidate **ADR-126** (NODE), extracted after implementation.

### Non-goals

Each is named in `design.md` with its reason.

- **`Time.elapsed()` and events on time** (cycle 3), **the document and the
  conformance corpus** (cycle 4), **the viewer** (cycles 5 and 6).
- **A multi-input request.** One driver moves, so one input is the group.
- **A bound reading a PORT.** Refused today under a running root and refused
  here, with the same message.
- **Re-clipping between events.** The clip is computed once, at the
  request's start, as ADR-109 evaluates a bound once per tick. A state
  committed at an event inside the request does not move a bound already
  read, so one long request and two short ones split at that event can admit
  different travels — stated behaviour, with a fixture of its own — and where
  such a commit carries a coordinate out of range the request is refused
  whole and commits nothing, which is cycle 1's behaviour unchanged.
- **Snapping the stopped coordinate onto its bound.** A clocked simulation
  banks no joint coordinate: it lands the DRIVER, and the coordinate follows
  from the pose.
- **The Curta's own clocked model and its interlock audit.** Project work,
  in the project's repository, after this cycle exists.
