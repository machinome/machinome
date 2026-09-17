## Why

The originating project is `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation` at `9fb725f`. It carries two models of one machine, both
declared in its manifest. `fast_curta` is a closed form: every part position
is an expression of the drivers, one expression-DAG evaluation per pose,
fast in Python and in the browser. It does not OPERATE — turning the crank
past a revolution carries nothing forward, so the maker edits the registers
by hand. `operating_curta` declares `Time.running()`, retains every
coordinate and integrates every law; it operates, it produced the findings
the framework took up in ADR-121, ADR-123 and ADR-124, and after the
`curta-speed` campaign it still costs about **0.73 s per 0.1 s Python tick**
and about 40 ms per crank tick in the browser (`workflow/warts.md`,
"Originating Curta follow-up: seconds per Python tick").

The requirement note is `workflow/docs/clocked-machine.md`: the Curta is a
**clocked machine**. It has a few retained values, closed-form positions
between events, and a commit of the retained values at each event; its
interlocks hold the selectors, the carriage and the clearing ring while the
crank is off rest, so nothing about its state changes except at the end of a
stroke. The running executor pays for a generality this machine does not
use.

A project-level spike answered whether that is true of the real machine,
with no framework change: Curta worktree `WTs/clocked-spike`, branch
`clocked-spike`, commits `0968563` `a56937e` `bcf2017`, recorded in
`simulation/docs/clocked-spike-2026-09-16.md`. It wrapped the fast model in
an ordinary-Python harness with two committing relations in the note's
shape, and replayed eighteen scenarios against a recorded `OperatingCurta`
oracle (574 ticks, 439.2 s). It found:

- The clocked model reproduces the operating model's registers at **every
  stroke end** of every scenario in which the machine is operated as the
  manufacturer's booklet says it must be.
- Fed from the committed state, the project's own `cycle.py:dial_positions`
  reproduces the operating model's **actual dial angles to 0.000000 digits**
  at every in-corpus read — mid-stroke reads included — except after a
  clearing sweep, where it differs by 0.0139 digits, exactly the
  zero-capture band the project's own `clearing_travel` prescribes.
  "Between events nothing is retained" is measured, not assumed.
- One clockwise revolution costs the operating model 15.3 s and the clocked
  model 0.438 s at the same 20 samples — a factor of **35**. The commit is
  not the cost: one commit through `calculate` is **26 microseconds**. The
  cost is the pose, and the pose is the fast model's existing per-pose cost,
  unchanged.
- Every interlock the machine needs is a project-owned `Bound` on a joint
  (eight of them, each quoted from the booklet). The framework needs no new
  lock idea.

The framework cannot express this today. `Time.running()` bundles a time
base (ADR-104) with a mechanics (ADR-105 to ADR-107) that retains every
coordinate and integrates every law at a fixed cadence; an untimed root has
no memory at all, so a pose request cannot carry anything forward. There is
deliberately no project-declared state: the pilot rejected the `running(r)`
/ `r.state` / `r.event` protocol on 2026-09-13
(`workflow/open-run-simulation/design.md`, "Decision 2026-09-13"), and
nothing here reintroduces it. What is missing is a third state discipline
beside "none" and "integrated" — **memory** — declared in the places the API
already has: a declaration beside `Driver`, and a verb beside `.drives`.

## What Changes

- **A `State` is a driver the machine writes.** `State(default, range=None,
  unit=None, dtype=None, scale=None)` is declared as a class attribute on an
  assembly, takes exactly `Driver`'s arguments with exactly their meanings,
  is read in `simulate()` and in laws exactly as a driver is, and carries
  the same instance-qualified id. Everything that differs is about who
  writes it: `set_state` refuses it BY NAME, an `Instruction` and a
  `controls` entry cannot target it, and `sim.snapshot()` / `sim.restore()`
  carry it. A tree that declares one is a **clocked** model.
- **A grouped source COMMITS states at an event.** `(crank & result &
  turns).commits((result, turns), at=strokes, law=registers)` is a
  declaration in a class body beside `drives`, on the same `&` groups, with
  `at` and `law` following the existing law-factory protocol — called once
  at realization with the realized owners, returning a callable over the
  sources' values. `at` is ONE jump node (`floor`, `ceil`, `sign` or a
  comparison); every RISING step of it along a request's path is one event.
  A state may appear among its own sources, and both `at` and `law` then
  read its PRE-EVENT value.
- **Several relations may write one state; two of them at ONE event may
  not.** A register digit is written at the stroke end and again at the
  clearing reach — two events, two inputs, and one relation states one `at`
  — so a state is not owned by a single relation. What is refused is two
  answers for one value at one landing: the REQUEST is refused by name,
  naming the state, both relations and the landing, and commits nothing.
  Two states of two children of one class are two states, keyed by the path
  as written and never by the local name, which is what makes a register of
  seventeen identical wheels one line rather than seventeen. *Amended
  2026-09-17 during the review of the implementation; the first draft of
  this proposal refused a second writer at class definition, and the Curta
  is inexpressible under that rule.*
- **A clocked `Sim` takes no `dt` and solves events along a request path.**
  `Sim(model)`; `sim.move(input, by=|to=)` moves ONE declared driver along a
  straight path; every rising crossing on that path is located EXACTLY by
  the tools ADR-107 and ADR-123 already own — solved, never searched — and
  committed in path order, each event reading the state the previous one
  left. Two relations are ONE synchronous event exactly when their landings
  are the SAME float — no tolerance decides it, because a tolerance stated
  as a fraction of a tick cannot be carried onto a request whose travel is
  the author's to choose. `sim.state` is the readout;
  `snapshot`/`restore`/`reset` and `state=` are the session-setup path. A
  refused request commits nothing — including one whose FINAL POSE the tree
  refuses, which leaves the bank and the pose exactly where they stood.
  A committing relation no declared driver can reach — every source a state,
  so its level can never move — is refused at construction rather than left
  silently inert.
- **Between events nothing is retained.** A pose under a clocked root is the
  existing untimed enumeration over the drivers, the states and nothing
  else — `time` is not in the bank, and a clocked pose leaves it the untimed
  symbolic `$t` exactly as the build path does. A request costs NO pose:
  `at` and `law` read only banked values, so the tree is bound once, at the
  end of the request. A commit law reads and returns NATIVE values, with a
  single nearest-integer rounding for a `dtype=int` state and no second
  scale conversion.
- **Only rising steps fire**, because the spike measured the note's
  assumption false: with `at = floor(crank / 360)` and no pawl, dragging the
  crank backwards fires the falling step and the additive law commits a
  SECOND addition (9 → 18). A mechanism that wants the other edge negates
  its own level (`floor(-crank / 360)`), which is exact and needs no
  keyword.
- **A `State` under `Time(loop=)` is refused by name**: a loop replays every
  commit from zero and the state climbs across loops. A `State` under
  `Time.running()` is refused in this cycle too, with its MEANING defined
  (an ADR-121 self-read switch) and deliberately not implemented.
- **Publishing a clocked model is refused by name.** The document version
  that carries states is a later cycle's; until it exists the serializer
  refuses rather than publishing a document a consumer would animate
  wrongly. Rendering, assembling, STL building and `solid test` are
  untouched.
- **Zero behaviour change for every model that declares no `State`.** No new
  tree walk, no new per-pose cost, byte-identical documents, and the
  existing `Sim(node, dt)` surface unchanged in every particular.

## Capabilities

### New Capabilities

None. The change gives meaning to two sentences the existing capabilities
have no word for, inside the grammar they already define.

### Modified Capabilities

- `simulation`: FOUR ADDED requirements — "A state is a value the machine
  writes", "A committing relation writes states at an event", "A clocked
  simulation solves a request path event by event", and "A clocked
  discipline costs a stateless model nothing" — and TWO MODIFIED: "Qualified
  tree-wide driver enumeration" (states enumerate beside drivers in the same
  walk) and "Fixed-dt stepping loop with deferred actions" (`Sim` takes no
  `dt` over a clocked root, and the cadence surface is refused there).
- `couplings`: ONE ADDED requirement, "A grouped source commits states at an
  event", stating the verb, the factories, the refusals and the pre-event
  reading rule; and one MODIFIED, "A relation is stated by `drives` in a
  class body", for the refusal of a `State` as the driven end of `.drives`.
- `export`: ONE ADDED requirement, "A clocked model is refused publication" —
  a tree that declares a `State` is refused by name where a document's body
  is assembled, the one function every document producer passes through,
  naming the states and saying the version that carries them is not defined
  yet. Every entry point is named and verified at apply — build, export, the
  development server's publish and the browser-rendered snapshot refused;
  rendering, assembling, STL building, `solid test` and an OpenSCAD snapshot
  untouched. No existing requirement's behaviour changes.

## Impact

- `solid_node/simulation/state.py` (new): the `State` declaration and its
  enumeration faces, beside `driver.py`.
- `solid_node/simulation/enumeration.py`: `qualified_states` and
  `declared_states`, collected in the walk `qualified_declarations` already
  makes.
- `solid_node/motion/couplings.py`: `commits` as a verb on `CoordinateRef`
  and `Coordinates`; a `Commitment` declaration and its record; the
  class-definition refusals.
- `solid_node/simulation/clocked.py` (new): the event solver and the request
  path — a consumer of `program.py`'s `JumpPlan`, `_shape_of`, `_surfaces`,
  `_KinkCuts` and `_far_side`, adding no second locator.
- `solid_node/simulation/sim.py`: the clocked constructor, `move`, the
  clocked `state`/`snapshot`/`restore`/`reset`, and the refusals of the
  cadence surface.
- `solid_node/core/serializer.py`: the publication refusal, in
  `document_body` — the one function `solid build`, `solid export`,
  `solid develop` and `solid snapshot --renderer web` all reach, the last of
  them bypassing `symbolic_document` entirely.
- `tests/clocked_project/` (new): the two-digit register fixture; the
  state-reading clearing fixture, declaring its state on a CHILD and
  committed by a relation the root states through a path; the Curta-shaped
  REGISTER fixture — three wheels of one class, one stroke relation and one
  clearing relation each — which is the fixture the several-writers
  amendment exists for; `tests/` refusal fixtures;
  `docs/scenarios.rst`; `HISTORY.rst`.
- One ADR, candidate **ADR-125** (NODE), extracted after implementation.

### Non-goals

Each is named in `design.md` with its reason and the cycle that owns it.

- **A bound as a stop on a request path.** A violated `Bound` stays the
  untimed `JointRangeError` on the pose the request ends at. Cycle 2.
- **`Time.elapsed()`, and events on time.** A clocked root is UNTIMED in
  this cycle, so `time` is not a source of a committing relation. Cycle 3.
- **The document and the conformance corpus.** Cycle 4.
- **The viewer.** Cycles 5 and 6, in `solid-node-viewer`'s own repository.
- **A fold-commit** (a `commits` with no `at`). The spike measured that
  per-digit comparison events cover partial clearing in BOTH directions with
  no held value, and that the one gap a fold would close is a rest the
  manufacturer's booklet forbids. `at` is required.
- **A port, joint coordinate or derived coordinate as a source** of a
  committing relation.
- **A broadcast `commits` over a `.repeat()` child**, a multi-input request,
  a direction keyword, an instruction or a control under a clocked root, and
  a `State` implemented under `Time.running()`.
- **The Curta's own clocked model, and its interlock audit.** Project work
  in the project's repository. The spike's harness is not a framework API
  and does not become one here.
