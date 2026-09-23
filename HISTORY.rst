=======
History
=======

Current-source work after the 0.7 record (unreleased)
------------------------------------------------------

* A finite, pointwise convex-profile contact predicate can be used as a
  numeric 0/1 term in an existing running Bound. Its compact data table
  is carried only by version-13 documents. The bounded Curta reverser
  trial motivates the capability, but installed-print and axial-band
  coverage remain independent project obligations. This source change
  records no package upload or remote push.

Machinome 0.7.0 (2026-09-23)
----------------------------

**Source code for machines.** Machinome continues solid-node 0.6.0 with
the same Git history, under the ``machinome`` GitHub organisation.
The rename avoids confusion with Tim Berners-Lee's Solid project.
The distribution, import package and command are now ``machinome``;
project tables use ``[tool.machinome]`` and former ``SOLID_NODE_*``
settings use ``MACHINOME_*``. No former import or command alias is shipped.

This release describes a machine's parts, shared dimensions, movement,
inputs and stored state together. Its user-facing summary and migration
map are in ``docs/changelog.rst``, ``docs/releases/release-0.7.rst`` and
``docs/upgrading.rst``. The complete engineering record is preserved in
``docs/releases/development-0.7.rst``.

Release preparation completes the independent mechanics extraction:
``machinome[mechanics]`` installs ``machinome-mechanics`` 0.1.0 and
projects import its twelve helpers from ``machinome_mechanics``.
Viewer 0.7.0 reports API 25 and reads schemas 1–12, including running
``Play`` clearance pickup, explicit time drives, source-timed motion and
the two-surface ``Follow``.
Fresh installations bound ``ocp-gordon`` below 0.3 to preserve the
shared OCP 7.8 CAD runtime.

* **A retained coordinate FOLLOWS two certified clearance surfaces
  (ADR-141).** The Curta Type I's radial positioning ball is free
  between a bell surface and an independently moving carriage collar:
  a self-read switch law pushed it outward but pulled it back when the
  bell retreated, and ``Play`` has one source and fixed offsets. Under
  a running root ``Follow(lower=, upper=)`` projects one banked scalar
  coordinate through the two authored surfaces, ``max(lower,
  min(retained, upper))``, at every certified affine piece of the tick,
  visiting both one-sided closures and the exact value at each cut and
  never snapping a numeric seam by a tolerance. The lower and upper
  dynamic ``Bound`` relations on that coordinate must structurally
  match the two surface graphs; they locate the first admissible
  contact from their original samples plus the certified cuts and
  cut-side candidates, and a strictly positive closure with no
  representable positive neighbour refuses the tick rather than passing
  an undetectable contact. Sources are inputs, held bank values or
  unbranched ordinary affine chains carried as exact ``Motion.line``
  paths; other ancestry is refused rather than approximated by a chord,
  and the follower is terminal among program edges. The producer
  publishes a ``kind: "follow"`` edge with both graphs and nullable
  jump plans, and only a document carrying one declares **version 12**;
  the viewer's API 25 reads it. Change
  ``follow-two-clearance-surfaces``; ratified by the pilot's decision
  to release 0.7.0 with it.
* **Running bounds reuse what they already proved (ADR-139, ADR-140).**
  At the viewer's default cadence the Curta's crank Bound eagerly bound 126,032
  expression nodes each tick while 1,479 depended on the moving bell.
  A ``Run`` now keeps one successful standing-bind snapshot per
  compiled constraint and reuses it when the graph, the moving-name set
  and every referenced standing input are bit-identical finite numbers;
  a path keeps its own last successful first-point bind on the same
  terms. Two later cycles share a successful ``Follow`` prefix
  propagation between the bounds that replay it at the same fraction
  within one stretch (``cache-follow-prefix-probes``) and reuse
  identical successful law folds within one tick
  (``cache-folded-law-graphs``). Every cycle was accepted only on
  bit-identical ordered bound samples and banks; laws, tolerances,
  timestep and sample counts are unchanged, and the machine is still
  not interactive.
* **An exact comparison FAILS CLOSED (ADR-142, ADR-143).** The Curta's
  positioning sphere, shifted 0.2 mm into its frame, shares positive
  interior with it, and OCCT's common returned a valid empty shape. After
  an empty exact common the kernel now sections the pair and classifies
  candidate points against each solid at zero tolerance; a point
  strictly inside both, farther from every face than that face's own
  native tolerance, raises ``ExactCommonInconsistency`` rather than
  passing as clearance, and a check that cannot complete raises
  ``ExactCommonVerificationError``. The reverser-tooth survey then
  showed OCCT's destructive Common altering a reused drum's tolerances
  until its fortieth comparison was grossly wrong: native Common, Fuse
  and the witness Section now receive private copies of both operands.
  ``intersect_shapes`` and the exact assertions share the rules; no
  mesh verdict, overlap epsilon or universal Boolean repair is claimed.

* **A determined source RETAINS its motion path (ADR-137, ADR-138).**
  The Curta's unchanged crank request carried correctly with six result
  stations and lost the carry with seven and eleven: the traced executor
  handed each downstream block only its predecessor's net increment, a
  chord that replaced a stroke and dwell with a ramp and re-timed the
  earlier gate. Demanded, propagation-local motion paths are now composed
  over the common request fraction; a source is commanded, held or
  determined and its path is restricted, never replaced by a chord.
  Range location and contact probes read the same paths as commits.
  Because an endpoint-era viewer reads the corrected payload and silently
  executes the wrong carry, every newly exported running program declares
  document version 11 and its identity carries ``source-timing
  version=11``; the paired viewer declares API 24. Change
  ``preserve-carry-across-graph-expansion``.
* **Running evaluation on a calculator-sized graph.** Nine measured
  cycles on the frozen Curta runtime graph, each accepted only on
  bit-identical bank parity: ``memoise-declared-ports``,
  ``memoise-expression-order``, ``reuse-path-order``,
  ``numeric-path-calls``, ``compile-graph-evaluation``,
  ``compile-moving-path-evaluation``, ``compile-path-operations``,
  ``evaluate-traced-constraint-path`` and ``demand-bound-read-paths``.
  An ordinary two-second crank turn fell from 72.56 to 27.87 CPU
  seconds. ``exact-leaf-shape-currency`` separately makes an exact leaf
  recover native geometry from a stale BREP after its SCAD presentation
  has been assembled.

* **A clocked stroke can be WATCHED: an instruction is one request.** A
  clocked machine could compute a whole stroke exactly and could not show
  it happening. The originating project is
  ``projects/Calculators/Curta-Type-I-3x``, whose ``ClockedCurta``
  declares ``'Turn crank': Instruction(by={'crank_rotation': 360},
  duration=2)`` and got nothing for it: the table was published with no
  meaning, ``trigger`` was refused BY NAME under a clocked root, and the
  only way to turn the crank was one ``move`` that jumped a whole
  revolution and posed the tree once at the end. Under a clocked root an
  instruction is now ONE REQUEST and nothing else — ``by={id: travel}``
  is ``move(id, by=travel)``, ``targets={id: value}`` is ``move(id,
  to=value)``, through the same resolution every other base uses — and
  ``trigger`` RETURNS that request, so a caller that pressed a button
  holds exactly what a caller that moved the input holds. Such an
  instruction names EXACTLY ONE driver: a request names exactly one
  moving input, so an instruction naming two would be a SEQUENCE, which
  is a program, and one naming none would move nothing; both are refused
  where the machine is COMPILED, which is before any document exists, so
  every instruction a version 8 document carries is one a consumer can
  PLAY. The declared ``duration`` is carried and means NOTHING to the
  machine — a request is a path, not an interval — and says how long a
  CONSUMER draws the transition. A request now reports BOTH ENDS of the
  path it travelled, ``origin`` and ``end``, taken verbatim from the bank
  and so in the input's NATIVE units, the units every commit's ``value``
  speaks: a drawer walks the moved input between them, applies every
  commit already reached and poses from the bank, one solve and N poses,
  with no machine work in the frame loop. The same project measured the
  alternative and ruled it out: one stroke costs 0.07875 s in Python and
  36.95 ms in Chromium, and the same stroke sliced into twenty
  requests costs 1.56363 s and 647.7 ms. The DOCUMENT does not change:
  no field, no key, no version bump, no producer change, and a version 8
  document published after an instruction has a meaning is byte for byte
  the one the same root published before it had one. The clocked
  conformance corpus records a ``trigger`` step in each instruction form,
  and both ends of every path, so the two runtimes are pinned to what a
  BUTTON does and not merely to what a hand-made request does.

* **A clocked machine publishes what it IS: document version 8.** A
  machine with MEMORY could be built, tested and photographed, and could
  not leave the process: every document producer refused a tree that
  declared a ``State``, because a clocked pose reads its states as FREE
  NAMES and a consumer that believed it could read the document would
  resolve them to nothing. Such a tree now publishes **version 8**, a
  rung read off the ROOT'S DECLARATION and DOMINATING every other, with a
  top-level ``clocked`` object carrying the machine compile time decided:
  every committing relation as its sources in written order, its ``at``
  as ONE jump node and its level, one law expression per target and the
  structural SHAPE of every input that can move that level; every
  compiled constraint as its chain, its bound read under a minted
  own-name, its jump plan and its per-input shapes, with the level left
  as the consumer's own subtraction; the banked clock as the free name
  ``time`` under ``Time.elapsed()`` and ``null`` otherwise; an
  ``identity`` digest, so a bank taken against one machine is refused
  against another; and the two ``limits`` a clocked path reaches.
  ``states`` joins ``drivers`` as a SECOND table, because every key of
  ``drivers`` is a handle a person may move and no key of ``states``
  ever is, and there is no ``coordinates`` table, because a clocked bank
  holds no joint coordinate and every number in it is already published.
  A ``%`` in a published commit LAW is desugared to Python's floored
  remainder, since the executor CALLS the project's callable rather than
  evaluating the graph, while a chain, a bound and a constraint level
  keep the document's truncated ``%``, which is what the framework
  evaluates them by. A commit that computes an INFINITY or a NaN refuses
  its whole request, naming the relation, the state and the value: that is
  the rule the document states for a consumer, and the framework keeps it
  on its own side too. Every declared ``Instruction`` is published in the
  version 5 shape and given no runtime meaning; a control stays refused.
  A build and an export WARN and publish where the installed viewer
  cannot read version 8; ``solid snapshot --renderer web`` is refused
  before the browser starts, writing no image and leaving no staging
  directory; the OpenSCAD renderer, ``render()``, ``assemble()``,
  ``build_stls()`` and ``solid test`` are untouched. The two runtimes now
  share a clocked conformance corpus that is **exact, bit for bit** —
  thirty machines, eighty-one steps, no tolerance window anywhere — with
  its basis stated operation by operation and a coverage inventory the
  generator refuses to write below. A tree that declares no ``State``
  pays nothing and publishes a byte-identical document, and versions 5,
  6 and 7, the running corpus and ``Time.running()`` are untouched.
  Two landings the shared solver had no answer for were closed with it:
  a crossing belongs to the request whose path CONTAINS its landing — so
  a request ending exactly on a STRICT surface leaves it for the request
  that begins there, which fires it, and a ``sign`` level moved off zero
  now takes both of its rising steps — and the landing walk sizes its
  first step by the SEGMENT it walks, so a bank standing outside a bound
  with its coordinate at exactly zero reports its stop instead of
  raising.

* **A clock without a run: ``Time.elapsed()``, and an event on it.** A
  machine that is OPERATED has elapsed seconds; a machine on a timeline
  has a loop. Until now "elapsed seconds that never wrap" could be said
  only as half of ``Time.running()``, whose other half retains every
  coordinate and integrates every law at a fixed cadence — the
  generality the clocked discipline exists not to pay for. ``time =
  Time.elapsed()`` is now a THIRD spelling of the time base, declared by
  the same rules as the other two, and the time base and the state
  discipline are INDEPENDENT: only a declared ``State`` makes a model
  clocked. A root declaring ``Time.elapsed()`` and no state is admitted
  and equivalent — the same stepped simulation, the same reads, and a
  document byte-identical to an undeclared root's — and what the base
  adds is a MEANING for ``time``. Under a CLOCKED root it adds a banked
  clock: ``time`` in the bank in seconds, initial ``0.0``, opened by
  ``Sim(model, state={'time': ...})``, returned by ``sim.state``, read by
  ``sim.time`` (the one refused name a declared elapsed base gives back),
  carried by ``snapshot()``/``restore()`` and zeroed by ``reset()``. The
  SAME verb moves it — ``sim.move('time', by=)`` or ``to=``, in seconds,
  with every driver standing, or one driver with the clock standing —
  and elapsed seconds never reverse, so a request that would run the
  clock BACKWARDS is refused by name while zero is admitted, firing
  nothing and posing what already stands. ``time`` is a SOURCE of a
  committing relation exactly as a driver is: ``(time & engaged &
  count).commits(count, at=release, law=advance)``, every RISING step of
  ``at`` along the request's path one event located EXACTLY, ordered by
  path, read pre-event and synchronously, with ties by identity of the
  landing float. A pendulum's release is AFFINE in time, so it is solved
  by one division and **no tolerance is introduced anywhere**; a level
  that CURVES in the clock is refused at construction, naming the clock
  and the primitive, and a relation the CLOCK alone can move is now legal
  where one every source of which is a state stays refused. The clock is
  delivered to the pose through the hook the posing walk already has, so
  a request still costs ONE pose and a model with no clock takes exactly
  the path it took before. **Nothing stops a clock**: a time request is
  never clipped — a declared range is a mechanical stop and no interlock
  holds the next second — and a coordinate that leaves its range at some
  instant is an impossible pose whose request is refused whole.
  Correspondingly a coordinate whose compiled chain follows the clock is
  refused at simulation construction, by name, under the general rule
  that any free name surviving a chain that is not a bank id is refused.
  ``Time.running()`` is untouched in every particular — not its compile,
  not its tick, not its document, not its meaning — and so is every
  untimed and looping root.

* **A bound stops a clocked request on its path.** The originating
  project is ``projects/Calculators/Curta-Type-I-3x``, whose eight
  interlocks are each a ``Bound`` on a joint, each quoted from the
  manufacturer's booklet, and none of which needed a framework idea the
  framework did not already have. What it could not do was OBEY them: a
  request that would drive a mechanism through a stop was refused WHOLE
  and committed nothing, which is a machine no maker can operate. A
  declared ``range`` is now a physical STOP on a clocked request path.
  The moving driver's travel is CLIPPED to the point where the bound is
  met — exactly, solved and never searched — and the events are located
  on the clipped path only; a request stopped at ZERO travel is
  ADMITTED, moving nothing, firing nothing and reporting its stop, which
  is what an interlock does. ``move`` returns the same value object with
  two more fields: ``admitted``, the travel actually made in DESIGN
  units, and ``stops``, each naming the bounded coordinate, the side, the
  bound as it evaluated at the landing, the coordinate's value there, the
  input's value and the fraction of the requested travel; ``record=N``
  keeps a bounded ring ``sim.stops`` beside ``sim.commits``, which lifts
  the previous refusal of that name. Each bound is compiled ONCE, at
  construction, into one expression over the bank, by composing the
  relations that determine the coordinate — wirings, derived coordinates,
  ``law=`` relations and INTERMEDIATE PORTS alike — and the level is
  classified per driver exactly as a commit's ``at`` is: affine is one
  division, kinked is cut at its own breakpoints, a level that JUMPS is
  partitioned at its own surfaces and solved piece by piece, and a CURVED
  level is refused at construction by name. **No new locator, no new law
  inspection, no sampling, no bisection and no tolerance at all.** The
  bound is read as ``Time.running()`` reads it, with the REQUEST as the
  quantum the tick was: the bounded coordinate's OWN value is the value
  it held when the request started — which is what makes a ratchet's
  floor the last seated tooth, and what makes an interlock stating a
  FREEZE expressible at all — while each ``reads=`` coordinate takes its
  value along the path, a read of a declared driver or a declared STATE
  included. What the framework cannot follow it refuses at construction,
  by name, naming the joint, the side and where the chain broke: a
  bounded coordinate a ``simulate()`` binds by hand, a chain through a
  law that is not an expression, a ``Bound`` reading something no chain
  reaches. A ranged joint NOTHING binds — a decorative range on a part
  that rests — is admitted instead, compiled as the constant it is and
  examined by no request. During a REQUEST the clocked simulation is the
  SOLE AUTHORITY for the constraints it compiled: the pose that ends a
  request does not judge them, and the simulation judges them itself over
  the final bank through the same chain, so a commit that carries a
  coordinate out of range still refuses the request whole and commits
  nothing. A pose that is NOT a request — construction, ``state=``,
  ``restore`` — goes on being judged by the enumeration, unchanged in
  every particular, and so do an untimed root and a running one.

* **A state is a driver the machine writes, committed at an event.** The
  originating project is ``projects/Calculators/Curta-Type-I-3x``, which
  carries two models of one machine: a closed form that is fast and does
  not OPERATE — turning the crank past a revolution carries nothing
  forward, so the maker edits the registers by hand — and a running model
  that operates and costs about 0.73 s per 0.1 s Python tick. The machine
  between them is a CLOCKED one, and the framework had no word for it:
  ``Time.running()`` bundles a time base with a mechanics that retains
  EVERY coordinate and integrates EVERY law at a fixed cadence, while an
  untimed root has no memory at all. A third state discipline now sits
  between them, declared in the places the API already has.
  ``State(default, range=, unit=, dtype=, scale=)`` is declared beside a
  ``Driver``, takes exactly its arguments with exactly their meanings,
  reads ``self.units`` exactly as a driver's value does and carries the
  same instance-qualified id; everything that differs is about who writes
  it, and ``set_state``, an ``Instruction``, a control and ``drives``
  each refuse one by name.
  ``(crank & units & tens).commits((units, tens), at=strokes,
  law=registers)`` is the verb that writes it, beside ``drives`` in a
  class body, on the same ``&`` groups, with both factories following the
  law-factory protocol this layer already states: called ONCE, at
  realization, with the realized owners, returning a callable over the
  sources' values. No event object, no runtime handle, no per-relation
  protocol. ``Sim(model)`` takes NO ``dt``; ``sim.move(input, by=|to=)``
  moves one declared driver along a straight path, and every RISING
  crossing on it is located EXACTLY — one division on an affine level,
  one division per sub-interval on a kinked one, by the solver
  ``Time.running()`` already owns — and committed in path order, each
  event reading the state the previous one left. **No new locator, no new
  knob, and no tolerance at all**: two relations fire at one event
  exactly when their far-side landings are the SAME float, so ten
  requests of one revolution give the same events as one request of ten,
  which a tick-fraction tolerance could not have promised. A level the
  moving driver CURVES is refused at construction naming the driver and
  the primitive, rather than searched: a clocked model's whole value is
  that its events are exact. Only RISING steps fire — the requirement
  note assumed both edges do and the law neutralises the falling one, and
  the project spike measured that false: with ``floor(crank / 360)`` and
  no pawl, dragging the crank backwards commits a SECOND addition, 9 to
  18 — and a mechanism that wants the other edge negates its own level.
  A commit is evaluated at ONE POINT and never integrated, so a law made
  entirely of jumps is a perfectly good commit where a running law of
  that shape is refused as arithmetic, and ``at`` MAY read the state it
  commits, which is what the Curta's per-digit clearing threshold needs.
  SEVERAL relations may write one state, because the Curta's register
  digit is written at the stroke end AND at the clearing reach — two
  events, two inputs, and one relation states one ``at``; what is refused
  is two answers for one value at ONE landing, and it is the REQUEST that
  is refused, naming the state, both relations and the landing. Two
  children of one class each declare their own state, told apart by the
  PATH and never by the local name they share, which is what makes a
  register of seventeen identical wheels one written line. A committing
  relation whose sources are all STATES is refused at construction: its
  level can never move, so it could never fire.
  Between events nothing is retained: a pose is the existing untimed
  enumeration over the drivers and the states, ``time`` is not in the
  bank, and a clocked pose leaves ``self.time`` the symbolic ``$t``
  exactly as the build path does. Measured on the two geometry-free
  fixtures this cycle adds: **0.9 us per commit against 60 us per pose**,
  a request with no event 82 us and one with ten events 428 us — the
  commit is not the cost, the pose is, and a request pays for exactly one.
  **A tree that declares no State is unchanged**: the states are
  collected in the walk the enumeration already makes, no clocked code
  path is entered for an empty state table, the clocked module is never
  imported, and a stateless document is byte-identical to the one the
  same model published before this existed (verified against ``81c5364``).
  **A clocked model cannot be PUBLISHED yet**: the document version that
  carries declared states is a later cycle's, so every document producer
  refuses one by name — including ``solid snapshot --renderer web``,
  which stages its document without entering the symbolic walk at all.
  Rendering, assembling, STL building, ``solid test`` and an OpenSCAD
  snapshot are untouched. Also refused, each by name and each a later
  cycle's: a ``State`` under ``Time(loop=)`` (a loop replays from zero
  and would replay every commit) and under ``Time.running()`` (whose
  meaning is DEFINED as an ADR-121 self-read switch and deliberately not
  implemented); a bound as a stop on a request path, which stays the
  impossible pose it has always been — and a refused pose now refuses the
  whole request, leaving the bank, the tree and the record standing,
  rather than clipping the path where the machine stops; a port, joint
  coordinate or derived
  coordinate as a SOURCE; a broadcast ``commits``; a multi-input request;
  and an instruction or a control under a clocked root.

* **A kink is a cut, and a piecewise-affine quantity is solved.** Under a
  running root the run has to follow a quantity along each tick's path —
  a jump node's level, a law's skeleton, a determiner's value — and it
  SOLVED that quantity where it was affine in the sources and SEARCHED it
  everywhere else, at 64 samples per piece plus up to 64 bisection rounds
  behind each bracket. Every CALL counted as non-affine, so ``clamp01``,
  which is ``min(max(x, 0), 1)`` — two kinks whose three pieces are each
  perfectly affine — was searched. That is how the framework's own
  ``clamp``, ``ramp`` and ``piecewise`` are built, and how a motion
  profile is normally written. Now ``abs``, ``min`` and ``max`` are
  recognized as the CONTINUOUS SELECTIONS they are — each returns one of
  its operands exactly — so a quantity built over them is PIECEWISE
  AFFINE: its breakpoints are located exactly, in the graph's postorder,
  each from the two endpoint values of the sub-interval the kinks inside
  it have already produced, and every piece between them is solved as any
  affine one is. No sampling, no bisection, no new tolerance, no new
  knob, and nothing to declare. A kink breakpoint is NOT a crossing: the
  law is continuous there, so it is recorded nowhere, enters no partition
  an increment is summed over, moves no coordinate to the far side of
  anything and counts toward no limit — which is why every answer a
  machine gave before this is the answer it gives now. A law carrying no
  kink meets no new code. Measured on the ``CurtaInterface`` fixture, six
  dials cleared by one ``clamp01``-gated ring: **2 861 expression
  evaluations per tick and 28 ticks/s before, 603 and 130 after**, and
  the crossing the search reached 9.3e-14 from its exact answer is now
  8.9e-16 from it. A curved law — a ``sin``, a ``sqrt``, a product of two
  moving quantities — is searched exactly as before, including a kink
  over a curved operand: the classification is structural and
  conservative. **Nothing in a published document changes.** The
  document's ``affine`` flag stays the two-valued statement it always
  was, a piecewise-affine quantity publishes ``false``, no version moves,
  and a consumer that has not learned to cut at a kink goes on searching
  it — correct, and slower.
* **Only what moves along a tick's path is evaluated.** A searched
  crossing samples one graph 64 times per piece, and most of that graph
  never changes over one path with one branch reading: a sibling
  coordinate the tick does not move, a retained dial upstream of it, a
  branch a jump already decided for the piece. The run now decides,
  once per followed quantity per tick, which of a graph's nodes MOVE —
  a source whose increment is non-zero, plus the driven coordinate
  where a level is handed its own value per sample — and computes every
  other node ONCE, reading it back at every later point instead of
  recomputing it. The arithmetic is unchanged, node for node and
  operator for operator, so every crossing, landing, branch reading,
  increment, stop and refusal a machine gave before this is the answer
  it gives now, bit for bit. No sampling, no bisection, no new
  tolerance, no new knob, and nothing to declare; a machine whose
  followed quantities move entirely, or whose graphs are small, pays
  only the one classification walk it was going to make anyway.
  Measured on the originating Curta's clearing dials, whose laws reach
  through seventeen retained dials and fifteen carry sliders: **3.28 s
  per 0.1 s tick before, 0.73 s after** — the same committed snapshot to
  the byte. **Nothing in a published document changes**, and no
  evaluation COUNT a probe reports moves either; what falls is the cost
  inside one evaluation.
* The conformance corpus now **catches a consumer that runs a block's
  members in the order the document lists them.** The ``ShiftedCarry``
  scenario ADR-122 added to pin a block's order replayed green under
  that published listing regardless: its detent landed exactly on a
  tick boundary, so the order never mattered. Its script now crosses the
  gate strictly inside a tick, and a framework test replays it with the
  block ordered as published rather than per piece and asserts the two
  disagree.
* **A selection decides which sources a law reads.** A mechanism's
  dependencies may be SELECTED by where one of its own parts stands, so
  that the union of what it reads over every selection is cyclic although
  each selection's own dependencies are not: a Curta's fixed carry lever
  is tripped by the dial the carriage has brought under it and advances
  the dial beyond that one, and which dial is which follows the carriage.
  Nothing new is declared — the selection is the comparison the model
  already writes, a term multiplied by a gate on the coordinate that
  selects. Under a running root such a union is a **BLOCK**: one entry of
  the program, ordered once per PIECE of a tick rather than once per
  program, so the program as a whole is acyclic again and nothing outside
  a block changes. A **SELECTOR** is a jump node of a member's law whose
  level quantity reads no coordinate the block determines, and a source
  is **SWITCHED** when folding that node's branch to ZERO removes it from
  the law — which ``floor``, ``ceil``, a remainder's quotient and a
  comparison can do, because each holds its zero branch over an INTERVAL
  of its level, and ``sign`` cannot, because its zero is a single point.
  Over a stretch the selectors are located first, the stretch is cut at
  each of their surfaces, and on each piece the branches read at the
  MIDPOINT are SUBSTITUTED into every member's own integration rather
  than located again — so the order the block chose and the branch a
  member reads cannot disagree. A selection change ALONE moves nothing; a
  block relation binds NOTHING at rest, so every coordinate it drives
  needs the author's own guarded rest default; a selector crossing is a
  crossing and not a stop; a declared range on a block coordinate still
  stops it and an input reaching it only through an inactive selection is
  not stopped by it; and what the block commits for a coordinate a piece
  LANDED is the absolute value it advanced that coordinate to by the
  stretch's end, landing and later motion both. Refused at construction
  by relation identity: a wiring or a derived coordinate inside a block,
  a cycle no selection breaks, an intermediate among a block's driven
  ends, and a block member driving a group. A piece that still cannot be
  ordered refuses the TICK, naming the piece, the selector branches and
  the cycle, and commits nothing. **BREAKING for consumers:** a document
  whose program carries a block declares ``version: 7``, because the
  published ORDER of a block's members is a listing and not an execution
  order — a runtime that executed them in it would move the machine by
  whatever that order happened to give, silently, and by a different
  amount for each order it might have chosen. No key is added: a consumer
  re-derives the block from the edges' own ``needs`` and ``gives`` and its
  selectors from the published plans. A program with no block publishes
  the byte-identical version 6 or 5 document it always did, keeps its
  order and its identity, and pays nothing per tick.
* Fixed: a law that reads the coordinate it drives left that coordinate
  one ulp from where it stood on a tick in which a source moved but the
  branch-substituted law did not — ``(own + S) − S`` rounded whenever the
  law's value was comparable in size to the coordinate. The walk now takes
  the difference first, so a piece whose substituted law is unchanged
  leaves the coordinate at the exact float it held.
* A law may **read the coordinate it drives**. A coordinate named in a
  relation's source group AND as its one driven end is a READ of that
  end — ``(ring & wheel.turn).drives(wheel.turn, law=missing_tooth)`` —
  and what the law sees there is the value the coordinate HOLDS, never a
  value the same application is about to give it. That is the Curta's
  missing-tooth clearing rack: a rack turns a register dial only while
  its teeth reach it AND the dial is not already standing at its gap, so
  a dial clears from any digit, the ring sweeps on past a dial that has
  finished, a released ring keeps the partial clearing and an
  already-cleared dial is not turned again. The read must be a SWITCH —
  with every jump node replaced by its branch the law must no longer name
  the coordinate, and a bare ``%`` is not one — and the driven end must be
  a coordinate the run banks; both are refused at construction by
  relation identity. Over a tick such a law is integrated PIECE BY PIECE:
  the jump nodes that do not depend on the driven coordinate partition
  the path as they always did, and inside each of their pieces the ones
  that do are walked, their branches read at the piece's left end from
  the value the coordinate retains there. After a cut the coordinate is
  committed at the nearest representable value on the FAR SIDE of the
  surface, and the run commits that float — so a dial that reached its
  gap reads the same branch on every later tick and survives a snapshot
  and a restore bit for bit. A gate's disengaged state must therefore
  have WIDTH, the mechanism's own clearance, stated as a band about the
  zero and entered from either side. Such a relation drives ONE
  coordinate (a driven group naming one of its own members is refused; a
  broadcast is admitted, each copy reading itself), binds NOTHING at rest
  so the dial's rest value is the author's own guarded default, and is
  refused by name under any time base but ``Time.running()``. A self-read
  crossing is a crossing and not a stop; a declared range on the same
  coordinate still stops it and wins where both fall in one segment.
  **BREAKING for consumers:** a document whose program carries such a law
  declares ``version: 6``, because a runtime evaluating a law edge as the
  difference of its two endpoint evaluations would read it at both ends
  and move the part by a different mechanism in silence. A program with
  no self-read publishes the byte-identical version 5 document it always
  did, and a law with no self-read takes the same path at the same cost.
* A **marking**: what a rigid part carries on its surface, declared in
  its class body as ``digits = Marking(Svg('dial.svg'), Wrapped(...),
  color='#FFFFFF')`` beside its parameters and its children. The artwork
  is an SVG resolved against the module that declared the marking and
  reduced to its closed regions, holes nested and open paths ignored and
  counted; the placement is ``Wrapped`` onto a cylinder (artwork X is
  arc length, with a stated angular zero and an optional repeat pitch)
  or ``Flat`` on a plane, both in the part's own frame, so the part's
  placement carries the decal and nothing about time or a joint is
  involved. A marking adds **no solid, no part and no printed piece**:
  volume, bounds, STL and BREP bytes, piece id and every interference
  and connectivity verdict are what they are without it, and it does not
  key the part's artifacts. The build writes one surface mesh per
  marking beside the part's ``.stl``, at the nominal surface with no
  offset, following a wrap to the part's own tessellation precision, its
  triangles wound away from the part so a viewer can lift the decal
  clear without inspecting the part it belongs to; it has a currency of
  its own, so editing the artwork rebuilds only the
  decal and a lost decal comes back without re-deriving a solid, while
  editing the declaration rebuilds the part as any source edit does. A
  rigid node's published entry gains an optional additive ``markings``
  list (``name``, ``model``, ``color`` and the marking's own ``mtime``,
  with no placement and no ``piece``) that moves no document version, so
  a tree that declares no marking publishes the same bytes as before,
  and ``solid export`` copies each named marking under ``models/``. The
  browser viewer draws markings in its own release; until then a model
  that declares one publishes it and looks as it does today, and the
  OpenSCAD path does not draw them at all.
* **BREAKING:** OpenSCAD is no longer a ``solid develop`` viewer or automatic
  fallback. It was solid-node's first reliable viewer, but as machine
  simulation gained independent drivers, instructions and continuously
  evaluated flexible parts, the browser viewer became the faithful machine
  surface and the OpenSCAD GUI became a roadmap burden. Install
  ``solid-node[viewer]`` and run ordinary ``solid develop`` (or ``--web``), or
  use ``--no-web`` for the viewerless watch loop. ``OpenScadNode``,
  ``Solid2Node``, legacy SCAD evaluation, SCAD output and the default
  fixed-pose OpenSCAD snapshot renderer remain supported.
* **BREAKING:** the browser viewer is no longer part of solid-node. It is
  the separate ``solid-node-viewer`` package, licensed AGPL-3.0-only, and
  installed through the new ``viewer`` extra: ``pip install
  "solid-node[viewer]"``. The framework stays Apache-2.0 and complete
  for non-interactive use without it. ``solid develop`` requires the package;
  ``--web`` remains an explicit spelling of that default. ``solid export``
  (unless ``--no-widget``), the Sphinx directive, ``solid viewer`` and
  ``solid snapshot --renderer web`` need the extra and say so when it is
  absent; the snapshot default stays OpenSCAD regardless. The framework
  reaches the viewer through one entry point and runs it as a separate
  process; it imports none of its code. ``solid develop --debug-web`` is
  removed (run ``solid-node-viewer serve --build-dir _build`` under a
  debugger instead); the ``web-snapshot`` extra now installs
  ``solid-node-viewer[snapshot]``; ``solid viewer`` also reports the
  export page and the viewer package version. Wheels and source
  distributions of solid-node contain no JavaScript and building them
  needs no npm.
* The declarative node API: typed parameter declarations with a
  dimension algebra checked on import, derived formulas, children declared
  in the class body with ``repeat(count)`` for identical units,
  realization top-down from the root, identity derived by the framework,
  ``--set name=value`` on every node-loading command, an internal
  ``render()`` that may return nothing, ``omit()``, and ports bound by
  assignment. Additive: a class that declares nothing is unchanged. A
  migrated class re-keys its artifacts once if it used to omit a keyword
  or pass an integer where a float kind now resolves. A node metaclass
  must derive from ``solid_node.node.declarative.NodeMeta``.
* Follow-ups from the first project migrations: a class-body list
  comprehension over module-level values declares children instead of
  silently building shared instances; a ``Flag`` flows to a declared
  child; a declarative node may define ``check()`` for guards over
  several parameters, called once they are resolved and before any child
  is realized; the declaring page says where a once-only placement goes.
* Build parameters are imported from ``solid_node.parameters`` and are no
  longer exported by ``solid_node.node``: the kinds, the ``Quantity`` base
  and ``declared_parameters`` moved, with no re-export and no deprecation
  path, so an import line says which name builds the machine and which
  drives it. The surface was never released.
* ``render()`` builds the machine at rest and runs once per instance; a
  new ``AssemblyNode.simulate()`` runs after it on every instant, reads
  drivers, time and ports, and its operations compose inside the rest
  placement and are swept before the next run. A ``render()`` that
  reads a driver keeps working and warns once per class. ``omit()`` in
  ``simulate()`` raises. The ``render()`` rename is dropped.

0.6.0 (2026-09-01)
------------------

The release that makes a model a *machine*. Until now a solid-node model
moved as a function of one looping ``$t``; it can now declare named inputs,
be stepped deterministically in Python, and be driven by hand in the viewer.
Alongside that, three new kinds of part — laser-cut sheets, imported STL
meshes, and flexible parts whose shape is a function of machine state — and
an assembly assertion that knows about gravity. The build and the CLI also
got substantially faster on projects large enough for it to matter.

Breaking changes
~~~~~~~~~~~~~~~~

* **Reinstall required.** ``cadquery`` moves from 2.5 to 2.7 and
  ``build123d`` 0.10 joins it, so the shared ``cadquery-ocp`` binding moves
  from 7.7 to 7.8. Both libraries bind the same ``OCP`` module and the
  previous pin admitted no current build123d. Because ``cadquery-ocp`` is a
  large binary wheel and the two versions cannot coexist, upgrade by
  reinstalling the environment rather than in place. No project source
  changes.
* The published document schema moves from version 1 to version 2: every
  document now carries a ``drivers`` table, and operation expressions may
  name qualified driver ids as well as ``$t``. A document containing a
  flexible part declares version 3 instead — the producer emits the lowest
  version its content needs, so a model with no flexible part is the version
  2 it would otherwise have been. The bundled viewer renders versions 1, 2
  and 3, so documents published by earlier releases keep working; what does
  not work is the other direction. A 0.5.x viewer has no version gate at
  all, so pointed at a 0.6 document it will silently render part of a
  machine it cannot evaluate rather than refusing. Hosts pinning their own
  copy of the bundle must upgrade it with the framework. The declared viewer
  API version is 5, and this release's viewer refuses an unreadable schema
  version by name.
* ``export_node`` now leaves the node in symbolic time rather than in
  whatever pose the caller left it. ``solid export`` and the build and
  snapshot paths produce byte-identical output to before, so only a host
  calling ``export_node`` itself and then reusing the node sees the
  difference; such a host re-applies ``set_keyframe`` if it wants a numeric
  pose. See below for what this fixes.

New features
~~~~~~~~~~~~

* **Named drivers.** An assembly declares its inputs as class attributes —
  ``x = Driver(default=0, range=(0, 200), unit='mm')`` — and reads them back
  as attributes: ``self.x``, exactly as a port is read. A driver's value
  belongs to a bound snapshot, so assigning to one raises and names
  ``set_state``, reading an unbound one raises and names the driver, and
  declaring a driver whose name would shadow a node member (``render``,
  ``color``, ``time``, …) fails at class-definition time. ``time`` is now one
  driver among several rather than the only one.
* **Instance-qualified driver ids.** A printer whose X and Y axes are two
  instances of one ``Axis`` class addresses them separately:
  ``set_state(**{'x_axis.motor': 12.5})``. The qualified dotted id is one
  string by construction — the same id appears in the document's driver
  table, the simulation's state bank, and an instruction's targets — and a
  tree that cannot be qualified fails loudly instead of silently sharing one
  value between siblings.
* **Domain-typed ports.** ``Port`` with ``RotationalPort``,
  ``TranslationalPort`` and ``SignalPort``: unit-tagged value slots a node
  re-binds on every render, with declared unit conversion and a causal
  ``connect()`` for wiring one node's output to another's input.
* **A stepped simulation layer**, ``solid_node.simulation``. ``Driver``
  declarations and ``RampProgram``; ``Instruction``, naming driver targets in
  design units plus a duration; and ``Sim``, a fixed-``dt`` loop whose
  instants are integer tick counts, with events at ticks, deferred ``at(t)``
  actions, an ``every(period, fn)`` cadence, per-tick snapshot binding and
  trajectory recording. Integer-typed drivers ramp integer-exactly
  (``start + delta*k//n``) and land on target. Under a simulation
  ``self.time`` reads the stepped clock in seconds; the normalized 0..1
  ``$t`` animation path outside simulations is unchanged. ``ScenarioTest``
  runs scenarios under plain pytest and under ``solid test`` alike.
* **A driveable viewer.** The widget evaluates driver expressions, not just
  ``$t``, and the mount handle gains ``drivers()``, ``instructions()``,
  ``driver(id)``, ``setDriver(id, value)``, ``onDriverChange(fn)`` and
  ``trigger(name)`` returning ``{done, cancel()}``. A trigger runs the
  instruction's ramp client-side over its declared duration, landing exactly
  on target, with a later trigger replacing an active ramp. Which operations
  re-evaluate is decided by the free variables read off the parsed
  expression, so moving one driver does not recompute the rest of the tree.
  Cross-runtime agreement between the Python producer and the JavaScript
  evaluator is now pinned by tests rather than merely measured.
* **On-screen driver controls.** The widget shows one button per instruction
  and one slider with a numeric readout per driver declared at the focused
  assembly layer, labelled relative to that layer and shown in design units.
  A breadcrumb moves focus down into subassemblies that declare controls and
  back up. Scoping is strict: the root of a machine that declares everything
  on its children shows no controls, which is pressure to declare
  machine-level instructions on the machine. A host building its own UI on
  the programmatic API suppresses the chrome with ``driverControls: 'none'``.
  A document with no drivers looks exactly as it did before.
* ``Build123dNode``, a fifth leaf adapter backed by `build123d
  <https://build123d.readthedocs.io/>`_. Like ``CadQueryNode`` it is a front
  end over OCCT, so it produces exact geometry, persists a ``.brep`` beside
  its STL, and needs no OpenSCAD binary. ``render()`` may return a ``Part``,
  ``Solid`` or ``Compound``, or a ``BuildPart`` builder whose finished
  ``.part`` is taken; a sketch or curve is rejected naming the node, since a
  leaf is one part. Exact composition does not require one backend: a fusion
  may mix ``CadQueryNode`` and ``Build123dNode`` children and still fuse
  exactly into a single solid.
* **Sheet parts.** ``SheetLeafNode``, with ``Build123dSheetNode`` as its
  first concrete backend, authors a laser-cut part as a 2D ``profile()`` plus
  a declared ``thickness``. The base owns ``render()`` — the extrusion of
  that profile — so the solid you preview and the outline a cutter consumes
  cannot drift apart. Each sheet leaf writes a nominal, kerf-free ``.dxf``
  beside its STL and BREP, under the same freshness guard, with arcs
  preserved. A profile that is not exactly one planar face, one outer
  boundary with holes strictly inside, is rejected naming the node. Kerf
  compensation, SVG import, engraving, nesting and a production-export
  command are deliberately left out; the persisted exact profile keeps them
  all additive.
* **Imported meshes.** ``StlNode`` wraps an ``.stl`` declared by
  ``stl_source``, so a design published only as a mesh can be assembled and a
  new part can be designed to fit it. A non-watertight mesh fails at build
  naming the file and the defect, with
  ``require_watertight = False`` to admit one knowingly. A multi-body file is
  a part pack: ``body`` selects one component by index, and leaving it unset
  reports the count with a per-body inventory of centroid, bounds and volume.
  An optional ``adjust(self, mesh)`` hook corrects the mesh in code —
  scale, recentre, any trimesh operation — instead of via constructor knobs.
  ``StlNode`` participates in ``FusionNode``, which makes the enclosing
  fusion faceted and routes it through OpenSCAD and CGAL; that cost is the
  documented price of designing a part that fits a downloaded one.
* **Flexible parts.** ``FlexibleNode``, the non-rigid leaf that ADR-003 and
  ADR-008 deferred and ``LeafNode.time`` has been naming as roadmap work,
  with ``MolejoNode`` as its first adapter. A valve spring, timing belt, cable
  loom or filament path is a part whose *shape* is a function of machine
  state, not only of its placement: its geometry is a pure function of its
  declared ports' bound values. It never caches a rigid artifact, because its
  representation in the document is a `molejo <https://molejo.readthedocs.io>`_
  shape spec plus one expression per parameter rather than a mesh. The widget
  evaluates that spec into reused buffers, and only on frames where a free
  variable of those expressions actually changed. Exact geometry comes from
  molejo's OCCT evaluator, and the OpenSCAD path gets per-binding snapshot
  meshes.
* **Assemblies are checked against gravity.** ``assertAssemblySupported(node,
  gravity=(0, 0, -1), max_drop=1.0, ground=None, supports=None,
  stability_margin=0.0)`` selects the same topmost rigid solids
  ``assertNoSolidInterference`` compares and proves two things about them.
  First, support reachability: displaced by ``max_drop`` along gravity, every
  solid lands on another with positive volume, and every solid reaches a
  grounded seed through those "rests on" edges — so a part left floating in
  space fails. Second, static equilibrium: a distribution of unilateral
  push-only contact forces over the detected contacts must balance every
  solid's gravity wrench, force *and* torque, for the whole assembly at once,
  decided by one deterministic linear program. A bar supported at one end
  only fails; a tall solid toppling off a small footprint fails. On failure
  the assertion names which solids could not be balanced and whether force or
  torque balance failed. ``ground`` anchors named solids with bolted
  semantics, ``supports`` declares press-fit or glued holds the geometry
  cannot prove, and ``stability_margin`` shrinks each contact patch so
  knife-edge balances can be rejected. Friction, adhesion and dynamics remain
  out of scope, and the docstring says so.

Correctness and reliability
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Artifact freshness no longer goes through floating-point mtimes. Source
  times are read as integer nanoseconds and artifacts stamped with them, so
  the value the framework writes is the value it read. The float detour lost
  a sub-quantum remainder that the filesystem then truncated, leaving the
  artifact *below* the stamp it was given: on a millisecond-resolution
  filesystem caching stopped working altogether and every build rebuilt
  everything. Measured natively, 50 of 100 whole-millisecond stamps lost a
  millisecond through the round trip; a 25-generation probe under Pyodide's
  MEMFS failed freshness 13 times, always by exactly one millisecond, against
  0 of 25 on ext4. Freshness stays *exact equality* — no tolerance window is
  introduced, because the failure being fixed is a spurious rebuild and a
  tolerance would trade it for a stale artifact reported as current.
* ``manifold3d`` became a conditional dependency of the faceted mesh path,
  resolved at the operation that needs it with one error naming what needed
  it and why, on the model ADR-046 already established for the OpenSCAD
  binary. It was imported at module scope in ``solid_node.test``, so a
  project whose model is entirely exact — every comparison decided by the
  OCCT kernel, never reading a mesh — could not run *any* geometric
  assertion without the compiled wheel, and on a platform with no wheel
  (WebAssembly) lost ``assertNotIntersecting``, ``assertJoined`` and
  ``assertNoDisconnectedSolids`` too.
* ``clear_keyframe()`` joins ``set_keyframe(time)`` as its explicit inverse,
  returning an assembly subtree to symbolic ``$t``. ``set_keyframe`` was a
  one-way door: once ``time`` was a float, ``76.0 * self.time - 38.0``
  evaluated inside user ``render()`` code and the symbolic form no longer
  existed anywhere for the serializer to recover.
* The viewer reads a leading negative term the way it is written. Its
  expression parser took a unary operator's operand to be the whole
  expression beside it, so ``-100.0 + x`` was read as ``-(100.0 + x)`` and
  the sign of a driver's coefficient changed. A negative literal heads a sum
  whenever a part is placed from a rest on the far side of the origin, which
  is ordinary. The cross-runtime parity corpus gains fourteen
  producer-computed cases of that shape, and all 265 distinct expressions the
  Metamaquina 2 example publishes now agree between the Python producer and
  the viewer's parser, where one did not. Separately, ``^`` under a leading
  minus is now emitted the way OpenSCAD and Python both bind it; nothing
  solid-node emits reaches that path, but a hand-written expression does.
* The viewer refuses a flexible part's shape spec that its bundled evaluator
  cannot read, by name and once at construction, exactly as it already
  refused an unevaluable ``tech``. Such a spec previously escaped as a raw
  error out of the evaluator inside the render loop, naming no node and
  arriving on a frame rather than at load. The viewer still never parses a
  version itself; it asks the evaluator and repeats the answer.

Performance
~~~~~~~~~~~

* The ``solid`` command no longer pays for the whole CAD stack to answer a
  question that does not need it. Every invocation imported all seven command
  modules and every backend, whichever command was asked for; commands,
  backends and the test framework are now imported at the point of use.
  ``import solid_node.cli`` goes from 3.48 s to 0.002 s (77 modules rather
  than 2227) and ``solid viewer`` from 3.79 s to 0.044 s. A project built
  entirely from ``Solid2Node`` imports no CadQuery at all; one that uses
  CadQuery still does. Nothing became optional, and no grammar, help text,
  option, exit code or public API changed.
* The source-closure package lookup is indexed instead of rescanned.
  Resolving a module's package walked all of ``sys.modules`` calling
  ``realpath`` on each entry, once per call — a cost that scaled with
  whatever the interpreter happened to have imported, for an answer that
  does not depend on it. On a 567-node project that was 341169 ``realpath``
  calls and 21.8 s of 22.4 s of node construction. A cold ``load_node`` goes
  from 19.4 s to 4.8 s and a no-op ``solid build`` from 23.4 s to 8.0 s, with
  every published artifact identical by SHA-256 and every node carrying the
  same source closure.
* An artifact whose sources were rewritten but not changed is restamped
  rather than re-derived. Currency is mtime equality, which is precise about
  edits and blind to content, so a clone, branch switch, stash pop or restore
  re-derived everything. When mtime equality fails, a digest of exactly the
  tracked sources is compared against the digest recorded when the artifact
  was written, and a match restamps. The hit path opens nothing, so the
  common case is unchanged, and the fallback is stricter than the rule it
  stands behind — byte equality, not timestamp equality. A 22-part CadQuery
  project rebuilt after a full timestamp rewrite goes from 35.70 s to 5.83 s,
  and a relocated copy builds in 5.92 s.

Packaging, documentation, and maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* solid-node now depends on `molejo <https://pypi.org/project/molejo/>`_ with
  its ``brep`` extra. ``MolejoNode`` reaches for molejo's OCCT evaluator at
  import and ``solid_node.node`` imports the adapter, so ``brep`` is required
  rather than optional. The bundled viewer depends on the ``molejo`` npm
  package for the same reason, and bundles it. Both are pinned to molejo's
  minor, because a molejo minor carries the shape-spec version it implements
  and this framework's documents name that version.
* molejo 0.2 renamed the token a document declares its spec version with:
  the integer ``1`` or ``2`` is now the ``MAJOR.MINOR`` string of the release
  that minted it — ``"0.1"``, ``"0.2"`` — and the integer form is refused
  rather than aliased. solid-node never writes that field, so the change
  reaches nothing but test data and the parity fixture, which was regenerated
  rather than hand-patched and came back differing in exactly that one line.
  Documents this release publishes carry whichever version their content
  needs, and molejo 0.2 reads both.
* The user documentation now tells the 0.6 story rather than the 0.3 one.
  The entry surface — index, why, quickstart, README and status — leads with
  drivers, simulation and the driveable viewer; two new tutorials cover
  driving a machine and scenario testing, since ``solid_node.simulation``
  appeared in no page at all; and the guides' stale claims are corrected
  throughout, including the viewer API and document schema versions a host
  needs to know. `Metamaquina 2 <https://github.com/LibreSolid/Metamaquina2>`_
  — a real open-hardware printer with X/Y/Z drivers, root instructions and
  flexible filament, belts and springs — joins the V8 engine as a second
  worked example, and both are exported by the documentation build. A
  narrative announcement is at ``docs/releases/release-0.6.md``.
* Internal: the exact-adapter contract (``exact``, ``shape()``,
  ``as_scad()``) moved to a shared ``ExactLeafNode`` base rather than being
  duplicated in ``CadQueryNode`` and ``Build123dNode``. No project-visible
  effect: both adapters keep their name, import path and behaviour.
* The driver readout in the viewer holds still under a drag: fixed decimal
  places, a fixed-width right-aligned number column with room reserved for a
  minus sign, tabular figures, and the unit in its own segment. Previously
  the string was written with trailing zeros stripped, so the number and
  everything laid out beside it jumped horizontally while the maker was
  trying to land a value.

0.5.1 (2026-08-18)
------------------

Packaging, documentation, and maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* The project's ``Homepage`` metadata pointed at
  ``github.com/lfagundes/solid_node``, which returns 404. It now names the
  repository, ``github.com/LibreSolid/solid-node``. The 0.5.0 page on PyPI
  keeps the dead link, since release metadata is immutable once published.
* The Read the Docs build ran the V8 example export with the ``root``
  argument that 0.5.0 removed, so every documentation build since has failed
  with ``Error loading node: No module named 'root'``. The export now
  resolves the model from the example's ``[tool.solid-node]`` manifest, as
  the GitHub Actions workflow already did.
* Added ``context7.json`` so Context7 indexes the repository with the npm
  viewer trees, OpenSpec records, tests, and generated exports excluded.

0.5.0 (2026-08-17)
------------------

Breaking changes
~~~~~~~~~~~~~~~~

* A project now declares its model in a ``[tool.solid-node]`` table of its
  ``pyproject.toml``, and the framework discovers the project root from the
  nearest ancestor ``pyproject.toml`` carrying that table instead of assuming
  the current working directory. Commands consequently give the same answer
  from a subdirectory as from the root, where ``source_closure`` used to
  truncate silently and report stale artifacts as current.
* Node-scoped commands take an optional *reference* — a qualifier
  (``package.module:Class``), a Python file path, or a path plus class — and
  fall back to the manifest's model when it is omitted. The fixed
  ``root/__init__.py`` entry point, the directory-to-``__init__.py``
  coercion, and the ``NODE`` marker are all removed: a caller that can name a
  class never needed the file to name it. ``solid new`` scaffolds the new
  layout and manifest.
* ``solid test`` now loads *every* ``TestCase`` in a companion file rather
  than the first. Existing single-node projects are unaffected, but a
  multi-node module needs work: a case beside one **fails the whole run
  before any test executes** unless it declares its node, which is a hard
  error rather than a test failure::

      from .valve import ValveMotion

      class ValveMotionTest(TestCase):
          node = ValveMotion

  Without it: ``Error: ValveMotionTest must declare node; candidates: Valve,
  ValveRetainer, BucketLifter, ValveMotion``. Migrating the V8-engine example
  took two lines in each of seven files. Expect cases that were silently not
  running to run for the first time, and to fail: one of them had been
  asserting a design that its own guard rejected, unnoticed.
* Geometric questions are answered exactly wherever both compared nodes are
  exact. Every ``CadQueryNode`` is exact, so verdicts change in both
  directions: real sub-facet interference the mesh path missed now fails, and
  nominally exact fits that failed only on facet phase now pass. Projects can
  retire their tessellation epsilons; ``volume_epsilon`` is ignored, with a
  warning, when every comparison in the call routed exact.
* A failed build now leaves a partially updated model in ``_build`` rather
  than the previous complete artifact set. The 0.4 guarantee that the last
  successful set survives a later failure is withdrawn (ADR-030 reversed by
  ADR-038); in exchange, every individual artifact is written whole or not at
  all, and a successful build sweeps artifacts its manifest no longer
  references.
* A fused solid's STL bytes change, because an all-exact fusion is now
  tessellated by OCCT rather than compiled through OpenSCAD and CGAL.
* ``assertNoPairwiseIntersections`` is deprecated in favour of
  ``assertNoSolidInterference``; it still works and now warns about its
  leaf-based quadratic behaviour. Removal is deferred to a later release.

New features
~~~~~~~~~~~~

* ``solid build [reference]`` runs the ordinary build pipeline once,
  publishes, and exits — no viewer, no watcher. An unresolvable model exits
  with status 66 (``MODEL_NOT_FOUND``).
* ``solid develop --no-web`` runs the watch-and-rebuild loop with no viewer,
  leaving ``SOLID_NODE_PORT`` free for a host that renders the published
  build directory itself, and ``--callback URL`` POSTs that URL after the
  initial build and every later successful rebuild. Callback delivery is best
  effort and never stops development.
* ``solid snapshot --renderer web`` renders through the packaged viewer in
  headless Chromium and captures a real alpha channel, for hosts that
  composite the image onto their own surface. Install with
  ``pip install "solid-node[web-snapshot]"`` and ``playwright install
  chromium``. The OpenSCAD renderer remains the default and the fast
  inspection path; the web renderer never silently falls back to it, and
  rejects by name the options a browser cannot honour.
* ``solid viewer`` reports the installed viewer bundle's path and declared
  API version, so another program can obtain a viewer from an installation.
* Nodes expose exact geometry: a read-only ``exact`` property, a ``shape()``
  accessor returning the node's own OCCT solid in its local frame, and a
  ``.brep`` artifact written beside the ``.stl`` for every exact rigid node.
  A ``FusionNode`` whose subtree is exact composes its children with an OCCT
  fuse instead of launching OpenSCAD.
* Published documents carry a ``pieces`` inventory: one entry per distinct
  *printed piece*, identified by a content fingerprint of its built STL, with
  display name, contributing source files, instance count, bounding extents,
  volume and watertightness. Every rigid node in the tree carries a ``piece``
  reference. Geometrically identical solids are one piece however the code
  was factored; mirrored parts stay distinct. Purely additive.
* New geometric contracts: ``assertNoDisconnectedSolids(node)`` proves each
  printed solid is one connected body, ``assertNoSolidInterference(node)``
  proves the assembled solids do not occupy the same material, and
  ``assertJoined(node1, node2, min_weld_volume=0.0)`` proves two features
  genuinely reach each other. ``solid new`` scaffolds ``test_solid_integrity``
  and ``test_assembly_integrity`` so every new project has both from the
  start.
* OpenSCAD is now a conditional dependency, required only by the paths that
  invoke it — Solid2/OpenSCAD leaves, faceted fusions, symbolic Solid2
  values, the OpenSCAD GUI viewer, and the OpenSCAD snapshot renderer. An
  all-exact CadQuery project builds, tests and publishes without it, and a
  path that does need it reports what needed it and why instead of raising a
  bare ``FileNotFoundError``. (``JScadNode`` carries the same problem with the
  ``jscad`` binary; that is left to a later release.)
* One reusable viewer package now serves every surface — static exports, the
  Sphinx directive and ``solid develop`` — replacing three separate copies of
  the renderer. ``mount()`` returns a handle (``dispose()``, ``view()``,
  ``reload()``, ``apiVersion``) with targeted updates, assembly metadata, and
  subtree focus and visibility controls. The declared viewer API version is
  4. The published bundle, its global, its auto-mount attribute and its query
  parameters are unchanged.
* The development viewer gains inherited colours, lights, a fitted camera and
  the shared animation controls, because it renders through that same
  package. Exported models with no explicit or inherited colour are rendered
  with the development viewer's normal-based material rather than appearing
  untextured.
* Every successful build publishes a complete viewer-readable snapshot,
  including the animation cadence (``fps`` and ``frames``), so a host can
  serve the model straight from the build directory with no source import.

Correctness and reliability
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* A node now tracks the project modules its source imports, not just its own
  file (ADR-033). Editing a module that holds shared geometry but defines no
  node — the conventional ``kinematics.py`` — used to move no tracked mtime,
  so every artifact went on reporting up to date and ``solid develop`` never
  saw the edit; it now invalidates exactly the nodes that import it. Two
  consequences worth knowing: ``assemble()`` may call ``render()`` zero times
  rather than exactly once, so anything relying on a render side effect is
  affected; and a node whose geometry depends on something a static import
  walk cannot see — a data file read at runtime, a module reached through
  ``importlib``, an environment variable — can look current when it is not,
  where the old unconditional render hid it. An existing build directory
  rebuilds once as the corrected source set takes effect.
* Every process that renders artifacts for a project takes an advisory
  ``flock``, so exactly one build runs at a time per project and a build
  finishing late can no longer overwrite a newer model. A second builder
  queues rather than failing; one that finds the project already current, or
  its own source superseded while it waited, stands down. The lock covers the
  build only — ``solid develop`` releases it before waiting for the next
  edit, and ``solid test`` before running tests.
* A self-contained export now renders when served from anywhere but a server
  root. A document URL with no directory component resolves models beside the
  document rather than at the domain root, which is why the V8 engine example
  embedded in the published documentation returned 404 for every mesh.
* An explicit reference can name a node class defined in another project-local
  module, so a package facade no longer needs a meaningless local subclass.
* ``FusionNode`` rejects a non-rigid child instead of silently flipping itself
  non-rigid and producing no STL.
* The viewer no longer refetches geometry an artifact update has just
  fetched, and a failed targeted update leaves the previously rendered model
  on screen with the handle still usable.
* ``solid snapshot`` holds the project build lock while preparing its node,
  releases it before rendering, and defaults ``-o`` from the resolved node
  rather than ``snapshot.png``.

Performance
~~~~~~~~~~~

* The up-to-date check now runs *before* ``render()``, so caching finally
  pays: a no-op rebuild of a CadQuery-heavy project cost the same as building
  it from scratch (19.8 s either way) and now costs 3.2 s. ``CadQueryNode``
  and ``JScadNode`` no longer rewrite an artifact that is already current.
* The viewer updates in place instead of rebuilding the scene. A changed
  artifact is refetched alone and swapped into every node referencing it, and
  a document change reconciles the tree, fetching geometry only where
  ``(model path, mtime)`` genuinely moved — so an operations-only or
  colour-only edit costs no fetch at all. On a 113 MB, 55-STL assembly the
  old full reload re-parsed and re-uploaded everything to show a
  one-leaf difference.
* ``assertNoSolidInterference`` dropped its global batch-union volume
  certificate, whose cost scaled with total assembly triangle count whether or
  not anything was wrong. On a clean 125-solid, 1.02M-triangle assembly the
  certificate cost 273 ms against 2 ms for the sweep-and-prune plus exact
  narrow phase that actually finds and names the interference. The broad
  phase's conservatism is now proved differentially in the framework's own
  suite instead of being re-tested at every project's expense.
* The exact geometry path costs about 2× the mesh path on assertions
  (6.15 s via Manifold against 12.2 s via OCCT on the full V8 engine at one
  instant, identical verdicts), but its cached artifact is cheaper than the
  STL beside it: 4 ms write, 2 ms read, 165 KiB, against 112 ms, 9 ms and
  469 KiB.

Packaging, documentation, and maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* The built viewer bundle now ships inside source distributions and wheels,
  so a fresh installation has a viewer: ``solid export`` can copy one and the
  Sphinx extension can complete a ``--no-widget`` export.
* New optional extra ``solid-node[web-snapshot]`` for the browser snapshot
  renderer, whose Chromium download stays separate.
* The development loop's per-node HTTP API under ``/node`` and the browser
  modules that consumed it are removed, along with the dependencies they
  carried (``three``, ``jokenizer``, ``re-resizable``, ``react-ace``,
  ``ace-builds``, ``react-router-dom``). No published document, URL or CLI
  surface changes.
* Projects scaffolded by ``solid new`` ignore ``__pycache__/`` and ``_build*``.
  An existing project gets ``_build*`` recorded in ``.git/info/exclude`` on
  its next build, leaving its tracked ``.gitignore`` untouched; because that
  file is per-clone, an older project may need the pattern added to
  ``.gitignore`` when cloned elsewhere.
* ``README.rst`` states OpenSCAD as conditional on the backends a project
  uses, documents working on solid-node itself, and the hosted documentation
  builds its embedded exports from source in CI. The obsolete Read the Docs
  configuration is removed.

0.4.0 (2026-07-20)
------------------

* Relicensed from AGPL-3.0 to Apache-2.0, with consent from all contributors
* CLI grammar flip: commands come first, ``solid <command> <node>`` (breaking change)
* New ``solid new`` command to scaffold a starting project structure
* Added static ``solid export`` manifests, STL exports, an embeddable viewer
  widget, and Sphinx embedding support
* Added symbolic degree-aware math and expanded kinematic-fit assertions
* Improved animation correctness, node identity, test-runner behavior, and
  developer reload resilience
* Improved mesh and assertion performance through caching, single-matrix world
  transforms, and AABB broad-phase culling
* Migrated packaging to ``pyproject.toml`` and expanded API and tutorial
  documentation

0.3.0 (2026-01-14)
------------------

* Snapshot CLI for headless PNG rendering (enables AI agent workflows)
* Lean architecture: removed broker, git, refactor modules (ADR-018)
* Full license attribution in CREDITS.md
* License headers on all source files

0.2.0 (2025-02-25)
------------------

* JScadNode adapter for JSCAD backend, plus further work on OpenScadNode
* API reference documentation building on Read the Docs

0.1.0 (2025-02-01)
------------------

* Stable multi-backend architecture (SolidPython2, CadQuery, OpenSCAD)
* Web-based 3D viewer with React/Three.js
* Development server with filesystem monitoring and hot-reload
* Test runner for CAD projects
* STL generation with background optimization

0.0.8 (2024-12-15)
------------------

* Pre-release with improved documentation
* Bug fixes and stability improvements

0.0.1 (2023-07-13)
------------------

* First release on PyPI, with basic structure:
  * Develop using SolidPython and CadQuery combined
  * Filesystem monitoring triggering transpilation to openscad and stl building
  * Background optimization
  * Spatial calculations with trimesh
