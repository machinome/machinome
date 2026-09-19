:orphan:

0.7 development record
======================

This record preserves the engineering notes behind 0.7, including
intermediate interfaces and the former solid-node names. It is not the
migration guide. Use :doc:`../upgrading` and the current tutorials for
the supported API.

Machine state and clocked requests
----------------------------------

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


Earlier 0.7 development
-----------------------

**The framework becomes Machinome 0.7.** The distribution and import package
are now ``machinome``, the command is ``machinome``, project declarations use
``[tool.machinome]``, and runtime settings use ``MACHINOME_*``. The repository
moves from ``LibreSolid/solid-node`` to
``machinome/machinome-framework``. This is a clean package/API break: 0.7 does
not ship ``solid_node`` or the ``solid`` command. It does detect the former
project table and environment prefix and reports their replacements. New
exports use ``machinome-export``; Machinome Viewer accepts the legacy
``solid-node-export`` format so committed 0.6 artifacts remain viewable. The
optional packages are selected with ``machinome[viewer]`` and
``machinome[mechanics]``; ``machinome[studio]`` names the future Studio extra
but remains unavailable while Machinome Studio is unpublished.

**A skipped test is not a failure, and an unexpected success fails the
run.** ``solid test``'s runner had no skip concept and no
expected-failure concept: every method ran under one bare ``except
Exception``, so ``self.skipTest(reason)`` and ``unittest``'s skip
decorators counted as an ordinary failure, and ``@unittest.expectedFailure``
was read nowhere. A test that skips — in the method, in ``setUp``, or by
carrying ``unittest``'s skip decoration on the method or on the whole
class — is now reported skipped, named with its reason, and does not
count as a failure; the unit of a skip is the animation instant. A
method marked ``@unittest.expectedFailure`` is now honoured: an expected
failure when it raises, with no traceback printed, and an **unexpected
success** — which fails the run — when it does not (ADR-118). The
summary line gains ``, S skipped``, ``, X expected failures`` and
``, U unexpected successes``, each printed only when non-zero; a default
run's output is unchanged. Originating project:
``Internal-Cycloidal-Actuator``.

**A source-bound leaf names its missing file.** ``StlNode``, ``StepNode``,
``JScadNode`` and ``OpenScadNode`` each bind a node to a file outside
Python; a declared file that was not there used to construct without
complaint and fail later, deep inside ``mtime_ns``, with a bare
``FileNotFoundError`` naming only the path — and a declared file that
turned out to be a directory was not caught at all, failing instead
inside trimesh or the STEP reader. Each of the four now refuses at
construction, naming the class, the declaring attribute and its declared
value, and the absolute path the declaration resolved to; a path that
exists but is not a regular file refuses the same way, saying so. A
source removed after its node was constructed is unaffected: that is
still a currency question, answered by ``mtime_ns`` exactly as before.
Originating project: ``Internal-Cycloidal-Actuator``.

**A part that slides is operated along its rail, and a body with two
freedoms is operated along each of them.** ``Slide(part, input)`` joins
``Button`` and ``Turn``: a drag *along* the translational coordinate the
part rides, declared exactly as a turn is and deriving its axis, its
origin and its ratio from the same places. A ``Button`` now names a
sliding part as readily as a turning one — a press has no direction.

A body whose parts ride two joints — the Curta's crank, which lifts and
turns about the same line, and its register carriage, which does the
same — had no control at all, because a control inferred the nearest
posing joint and refused a node declaring two. Such a control now says
which coordinate it means: ``coordinate=crank.lift`` names an existing
joint declaration, by the same path a relation's end is written. The
selected joint must pose the part or one of its ancestors in the same
tree, own exactly one coordinate and be one the run banks; it may be
further from the part than the nearest joint, and it may never reach
sideways to another mechanism. Without a selection, inference and its
ambiguity refusal are exactly what they were.

The document gains one field, on the entries that need it: a
translational or explicitly selected control publishes
``operation_span``, the half-open pair of indices identifying that
coordinate's own placement inside the joint node's ``operations``, read
off the slot mark every placed operation already carries. A consumer
builds the gesture's frame from the operations *outside* that block, so
an inner joint's motion is never applied to an outer joint's line and a
sliding pivot travels with its rail. An entry inferred over a single
rotational joint carries no span and is byte-identical to the one
published before this existed; a document with no control, the compiled
program, its ``identity`` and the conformance corpus are all untouched,
and the document version does not move. Operating a sliding part or
choosing between the two freedoms of one body in the browser needs a
viewer of API 13 or later.

Nothing about the run changes. A control still moves nothing itself: a
sliding request is the ``move`` the panel would have issued, a stop that
belongs to a second mechanism stops it exactly as it stops that move,
and releasing a gesture rewinds nothing.

**A read is not a binding: a child's relation the root only reads
publishes.** A relation an assembly declares into its OWN leaf's joint,
whose value a relation the ROOT declares then reads to drive another
coordinate, was refused at publication with ``DoublyBound`` naming the
root relation's SOURCE as one of its binders. Every pose, every ``Sim``
and every untimed document accepted the same declarations; only
publication over a tree an ENUMERATION had posed — which is what ``solid
build``, ``solid export`` and ``solid snapshot`` hand the producer —
refused. The producer's epilogue restored every coordinate's value,
binder and freshness marks but not the enumeration's own record of
having bound them, so its re-render inherited the pose's values with
nothing left that knew to clear them and read one relation's two ends
asymmetrically. That record now travels back with the coordinates, and a
tree posed before publication poses again afterwards exactly as if
nothing had been published. No document moves a byte, and the untimed
and looping paths are untouched.

**A running root's document publishes only the program it computes.** A
``.repeat()`` child's port and a part this render ``omit()``s used to
refuse the whole document when a driver drove them: the relation reaches
no bank coordinate and is left to the ordinary enumeration, but the
compiled program kept a coordinate for it anyway, under a name
publication then refused as unqualifiable. The program's coordinate
table is now exactly the bank plus the ends its compiled edges read and
give, so such a relation leaves nothing in it, is published nowhere and
cannot refuse the document however its dropped node is named. A
coordinate a kept edge still reads or gives — an omitted node's, reached
through a chain of relations that does reach the bank — is refused
exactly as before. Three existing fixtures publish one fewer name in
consequence: ``Train`` (``wheel.turn``), ``Gauged`` (``gauge.angle``) and
``PortDrivenJoint`` (``register``) — a name no expression in any of those
documents reads, and none a ``bindings`` entry. Nothing about the run, ``program.identity``, the document version, the
drivers table, the poses or the bindings table moves; the conformance
corpus's two ``Train`` documents lose the same one name, and no tick or
script in it changes.

**``handle.cancel()`` now stops the command.** It used to set the
handle's status to ``cancelled`` and nothing else: the command kept
admitting travel every tick, kept owning its input, and a replacement
was refused with a message telling the caller to cancel the command it
had already cancelled. A cancelled command is now retired exactly as a
blocked or a refused one is: it stops where it stands, keeping the
travel it had actually admitted; its input is free the moment
``cancel()`` returns, so a replacement is accepted the same tick; and it
is no longer among ``sim.commands`` or in a snapshot taken after the
cancel. Nothing else moves — cancelling one command leaves every other
command running, and cancelling a command already retired keeps what it
reported.

**A control says which part a person presses and which part a person
turns.** An assembly declares ``controls`` beside ``instructions``:
``Button(part, instruction)`` is a press on that part submitting the
named instruction, and ``Turn(part, input)`` is a drag on that part,
about the rotational coordinate it rides, issued as relative moves on
that input. A control moves nothing itself — ownership, admission, stops
and outcomes stay exactly what ``trigger``, ``move`` and ``rate`` state.

The framework never guesses the binding, because it cannot: on a
Pascaline the tens dial is moved by its own entry *and* by the carry
from the column below, and the number drum turns with an input a hand
may not touch at all. It does derive everything else. The gesture's
coordinate is the one owned by the nearest ancestor-or-self of the part
whose joint the run banks; the axis and the point it turns about are the
values that joint's own placement used; and ``per_unit``, how far the
input travels per unit of the part, is *measured* from the compiled
program at the rest bank in both directions rather than declared, so
there is no second number to drift. Every mistake is refused with the
facts — at class definition where the classes are known, at compile
where the program is known, at publication where the rest bank is.

A version 5 document gains a top-level ``controls`` table beside
``instructions``, **additively**: the version does not move, because a
consumer that ignores the table still drives the machine from the panel
and still renders the truth, and a document that declares no control
omits the key and is byte-identical to the one published before this
existed. The compiled program, its ``identity`` and the conformance
corpus are untouched. ``controls`` is now a reserved class-body name on a
node class. What a viewer *does* with the table is the browser viewer's
own release.

**A running root's document publishes the compiled program, under schema
version 5.** Cycles one to three built a machine that runs in Python and
nothing of it reached the browser: a running root's document was
byte-identical to an untimed root's, so its pose expressions were the law
read *absolutely* at the driver values — the reading that makes a
register snap back at every carry window. It now carries a ``program``
object beside the geometry: the coordinate table with each bank id's
kind, rest value, declared unit and domain, the intermediates, the
compiled edges in program order with their expressions, per-end affine
flags and jump plans, the spans, the candidate table of which inputs
reach what, the program identity, the clock name, and the constants the
algorithm is defined by — everything compile time decided, and nothing
the tick computes.

**A committed bank poses the geometry.** Under a running root every joint
coordinate of the tree is serialized as its own qualified id, so a
joint's placement publishes as that coordinate's name and every plain
port, derived coordinate and flexible ``params`` expression publishes as
an expression over the bank. A consumer evaluates exactly the expressions
it always evaluated, from a scope holding the bank it just committed
instead of the driver values alone. The clock leaves with it: a version 5
document carries the free name ``time``, declared as ``program.clock``,
never ``$t``; every other reading of an unbound ``time`` is unchanged.

Both instruction forms are published under version 5 — each entry
carrying exactly one of ``targets`` and ``by`` — where versions 2 to 4 go
on publishing only the absolute form. An untimed or looping root's
document is unchanged in every byte.

The bump is **not additive**: a consumer ignoring ``program`` would read
a document whose joint placements are bare coordinate names it can bind
nothing to. The framework asks the installed viewer which document
versions it renders (``solid viewer``'s new ``documentVersions`` field; a
viewer without it renders 1 to 4). ``solid build``, ``solid develop`` and
``solid export`` publish a version 5 document and **warn once**, naming
the version written, the versions the viewer renders and its package
version; the Sphinx directive warns about a committed export it embeds,
without failing the build; and ``solid snapshot --renderer web``
**refuses** before it starts the browser, because a capture is a one-shot.
A browser that runs the machine is the viewer package's own next release.

**A conformance corpus pins the two runtimes to each other.**
``tools/generate_running_corpus.py`` writes ``tests/running-corpus.json``
from the framework's own run over thirteen scenarios across eleven small
running roots — every tick, with its bank, crossings, stops and command
outcomes — and refuses to write one missing any of the features the
export contract lists. The suite replays it exactly for discrete state
and within the run's own ``1e-9`` agreement window for floats.

**``solid snapshot --drive NAME=VALUE``**, repeatable, binds a declared
driver by its qualified id before the image is taken; drivers left
unnamed stand at their declared defaults. It works under every root — a
driver-declaring untimed project had the same gap — and it is distinct
from ``--set``, which reaches the root's declared *parameters*. Under a
running root the image is the untimed rest pose at those driver values,
the state a simulation itself starts from. A ``--drive`` naming a joint
coordinate of a running root is refused by name, and a non-zero
``--time`` on a running root is refused too: elapsed simulation seconds
never wrap, so there is no timeline to be a position on.

**One simulation owns a tree at a time, and the newest takes it.**
Constructing a ``Sim`` over a tree a previous run owns now releases that
ownership before the rest render, instead of failing as doubly bound —
which is what makes ``ScenarioTest.simulation()``'s "fresh per call"
promise true over a node built once per class, so two scenarios of one
running class run. The released run refuses to advance, naming both,
rather than binding over the simulation that now poses the tree. An
author's ``simulate()`` binding a run-owned coordinate is still refused
exactly as before. ``time`` is reserved: a driver or joint coordinate
qualifying to that id is refused at construction.

**A joint's range is a physical stop, located inside the tick.** Under a
running root a declared ``range`` is now the mechanical limit it states
rather than a refusal of the tick: when a tick would take a banked
coordinate outside a bound, and further outside than it stood at the
start, the run locates the fraction of the tick at which it reaches that
bound, commits it there exactly, and the tick commits. What stops with it
is the connected group — every input whose own movement pushes the
stopped coordinate, and everything those inputs alone determine. An
unrelated input runs its full tick, and so does one coupled to the
stopped coordinate only through a law that is currently disengaged: an
open clutch does not stop its crank. A coordinate determined by both a
stopped input and a free one goes on moving on what the free one
contributes. The tick becomes segments, each integrated by exactly the
procedure above, and stays atomic across them: a conflict or an
unintegrable law in any segment commits nothing. Both bounds stay
inclusive, so a move landing exactly on one is no stop at all.

A command whose input is stopped is retired reporting ``blocked``, with
the travel it actually admitted — fractional within the tick, in design
units — and it never resumes: nothing remembers the travel it did not
make. A ``rate`` on a stopped input is retired ``blocked`` too, and a new
command on that input is accepted at once. **Reverse moves and reverse
rates are admitted**, meeting a stop exactly as forward ones do; a rate's
cumulative travel on an integer input is now truncated toward zero, so
the two directions round alike.

**A range bound may be an expression over the joint's own coordinate**,
written as a callable of one argument inside the ``(lo, hi)`` pair, and
either bound may be ``None`` for unbounded on that side.
``range=(lambda turn: 36 * floor(turn / 36), None)`` is a ten-tooth
ratchet whose lower bound is the last seated tooth. Under a running root
it is compiled once, like a law, and evaluated at the start of every tick
from the committed bank; everywhere else it is evaluated at the value
being bound, so one declaration poses and runs. A jump in a bound is
evaluated, never integrated. ``record=N`` keeps a third bounded ring,
read through ``sim.stops``, of the most recent ``N`` stops; a crossing
located inside a segment is still recorded at its fraction of the TICK.

**A jump is located inside the tick and subtracted.** A running law may
now contain ``floor``, ``ceil``, ``sign``, ``%`` or a comparison — the
periodic and gated shapes a real mechanism is written in. Over one tick
the run cuts the path its sources take at every crossing of every jump
surface it meets; on each piece every jump node holds one BRANCH, read at
the piece's midpoint, which makes the law continuous there; and the
increment is the sum of the branch-substituted law's change over the
pieces. So a jump never moves a part: the Curta's tooth window leaves its
pinion at ``4`` at rest, ``76`` after one crank turn and ``148`` after
two, and the tick in which the crank passes 360 degrees contributes
exactly zero. Every crossing inside the tick is found, not only the
difference of its ends — a crank passing three tooth windows in one tick
adds three throws — including several jump nodes and a jump nested in
another's argument. ``wrap()`` integrates as the ``ceil`` it is built on,
so a wrapped law reads as the unwrapped travel, and ``piecewise()``
needed nothing of its own. Disengagement is a law's own business and both
its shapes are now expressible: a gate factor in a multi-source law
(``-2 * shaft * (sleeve > 0.5)``, which re-engages mid-tick without a
jump) and the zero-slope region of a single-source one.

Two laws are refused at construction, by relation identity: one that can
move its coordinate ONLY by jumping, because every jump is subtracted so
it can never move anything — it states arithmetic, not a mechanism — and
a jumping law none of whose driven ends the run owns, because a
subtracted jump implies a history and only an owned coordinate keeps one.
A tick that would cross more than a thousand surfaces of one law, or that
meets a ``%`` whose divisor is zero, refuses the tick and commits
nothing. ``record=N`` now keeps a second bounded ring, read through
``sim.crossings``, of the most recent ``N`` crossings located inside a
tick.

**A machine can keep its history: the run owns the coordinates.** A pose
was a function of the current input values and nothing else, so a Curta
pinion posed at any crank angle was right and turned through two crank
revolutions was wrong. A root may now declare a third time base,
``time = Time.running()`` — elapsed simulation seconds that never wrap —
and under it a ``Sim`` owns a BANK of every driver AND every joint
coordinate of the linked tree, by the same qualified ids the document
publishes, initialized from the untimed rest pose and advanced by
INCREMENTS: over one tick a continuous law contributes exactly
``f(end) - f(start)`` to its driven coordinate, from where it stood,
exact across the kinks of ``abs``, ``min``, ``max`` and the compositions
built on them. Increments propagate in the direction the rest render
solved each relation, a coordinate no increment reaches holds, and two
that disagree are a conflict that rolls the tick back.

The run is a BINDER the solver recognizes rather than a second kind of
state: it binds the whole bank through ``set_state``, so ``render()`` and
``simulate()`` stay pure over the snapshot and an inspection or an extra
render advances nothing; the freshness clear leaves its slots alone, a
relation whose driven ends it owns is recorded as solved by the run, and
an author's ``simulate()`` that binds one is refused as doubly bound.
There is no memory bank and the author declares no state.

Requests replace bindings: ``sim.move(input, by=|to=, duration=)``,
``sim.rate(input, rate)`` and ``sim.trigger(name)`` are one path with one
ownership rule — only a declared driver can be moved, one owner at a
time — and each returns a handle reporting ``active``, ``completed``,
``blocked``, ``refused`` or ``cancelled`` and the travel actually
admitted. ``Instruction(by=..., duration=)`` is the relative form, and
ramps relatively under every time base. ``sim.snapshot()``,
``sim.restore()`` and ``sim.reset()`` act on the bank, and recording is
explicit and bounded (``record=N`` keeps a ring; the default keeps
nothing). Under a running root ``set_state`` also accepts a qualified
joint-coordinate id, delivered to the node that owns it, a leaf
included.

This first increment refuses, by name, what it cannot yet do: a law that
cannot be applied to a symbol, a relation into a run-owned
coordinate sourced from a plain port ``simulate()`` binds, a reverse
move, and a joint coordinate leaving its declared range, which fails the
tick rather than stopping the group. Nothing about an untimed or looping
model changes: a running root's document is byte-identical to an
undeclared root's, ``Time(loop=...)`` is untouched, and a model that
declares no running time imports none of the new modules.

**OpenSCAD is no longer an interactive viewer.** OpenSCAD was solid-node's
first reliable development viewer, but the browser viewer became the faithful
machine surface as simulation gained independent drivers, instructions and
continuously evaluated flexible parts. The GUI and its installation-dependent
fallback represented progressively less of the machine while burdening the
v0.7 roadmap, so ``solid develop --openscad`` and the OpenSCAD PID lifecycle
are removed. Install ``solid-node[viewer]`` and run ``solid develop`` (or the
retained explicit ``--web`` spelling); use ``--no-web`` for a viewerless watch
loop. OpenSCAD and SolidPython modelling through ``OpenScadNode`` and
``Solid2Node``, legacy SCAD evaluation, SCAD output, and the default fixed-pose
OpenSCAD snapshot renderer all remain supported.

**Native geometry no longer passes through OpenSCAD as a core broker.** Node
preparation now links and validates the tree and materializes backend-owned
artifacts before optional SCAD presentation. Exact geometry remains in OCCT;
faceted fusions union current child meshes directly with Manifold. Export,
tests and browser development do not construct assembly SCAD, while ordinary
builds, direct SCAD APIs, Solid2/raw OpenSCAD modelling, and the OpenSCAD
snapshot renderer remain supported. Producer recipes migrate affected fusion
caches without changing node identities or filenames. Existing
``as_scad``-only project adapters retain an explicit compatibility bridge.

**A relation may name several coordinates at each end.** A mechanism that
reads several coordinates and moves several — a delta printer's rod, a
Pascaline's pawl deflecting from two drums, a flexure stage's leg leaning
two ways from two coordinates — states it in one sentence instead of a
hand-written loop. A source group is written with ``&`` (free on every
declaration that carries ``drives``, chaining flat); a driven group is
written as a tuple or with ``&``::

    (count & next_count).drives(sautoir.pawl.swing, law=pawl_deflection)
    (x & y & z).drives((rod.spin, rod.lean, rod.swing, rod.rise), law=delta_rod)

The law's two arguments are shaped by the sentence — the realized OWNER
of a side naming one coordinate, or the TUPLE of owners for a side naming
several — never spread one per end. ``forward`` takes one positional
argument per source and returns the driven value itself for one driven
end, or a sequence of exactly as many values for several, checked by
name at every application. Such a relation is read FORWARD ONLY, for the
reason a broadcast is: recovering several sources from several driven
values would mean comparing or solving values, which the framework does
not do. See "Several coordinates at one end".

**Relations resolve over the whole tree in one pass.** What one
instance's own simulate phase cannot reach is deferred to the
enumeration rather than refused, and resolved once every assembly's
phase has run — a relation may now be stated inside the class that
owns it, reaching an ancestor's coordinate or waiting on a descendant's,
rather than being hoisted, duplicated or re-sourced from a driver to
work around today's per-instance-only solve. A read of a coordinate a
relation, a derived formula or a wiring is going to bind is refused by
name instead of silently reading an empty slot, unless the reading
class's own ``simulate()`` binds it there itself (the ordinary
rest-default guard). A subclass may replace a base's NAMED relation,
keeping its position in the solve. A coordinate is cleared with the
motion it caused at the start of the OWNING assembly's next phase — the
author's own binding included — so a rest-default guard rebinds and
re-places its body on every run instead of standing, from the second
run on, at a stale number with no operation left to show for it. See
"Relations: one coordinate drives another" and "Joints: where a part
may move".

**A deferred relation now reads its source's current value, not the
previous enumeration's.** An ancestor's relation sourced from a
coordinate a descendant's own relation solves was correct on the FIRST
``render()`` and stale on every ``set_state()`` after: the ancestor's
own attempt runs before the descendant has cleared and rebound the
source this pass, found a value still sitting there from before, and
solved immediately instead of deferring. The driven end now tracks
whatever the source holds at the end of the CURRENT enumeration.

**A joint may be declared where a child is placed.** The other half of
"a joint is stated in the frame of whoever declares it" (below): a joint
passed as a KEYWORD where a parent declares a child is the parent's own
statement about a child it is placing, read in the DECLARING PARENT's
frame — URDF's rule — where a class-body joint is read in its own::

    class MotorDrive(AssemblyNode):
        gear_screws = GearLockScrew(
            orbit=Revolute(axis=(0, 0, 1), unit='deg')).repeat(2)

``at`` defaults to `(0, 0, 0)`, the DECLARING PARENT's own origin this
time, not the child's — so a child the parent translates SWINGS about
the parent's origin unless ``at`` names the child's own placement, which
is what lets a shared catalogue class — a bought bearing, a fastener —
be given a freedom its own class body has no way to state. An
``Orbit``'s ``carries`` keeps its own exception: WRITTEN at a site it
follows ``at`` into the parent's frame; DEFAULTED it is still the
CHILD's own origin, never the parent's, which is the case that keeps a
project's own already-derived radius and phase untyped even at a site.
A site joint may be passed to a ``.repeat()`` — one declaration, every
copy's arguments resolved once against the same parent, each copy's own
CARRY (through its own rest placement) supplying the number that would
otherwise need a sign, a flag or an index.

A site joint of a name the child's class already declares REPLACES that
declaration WHOLE — axis, anchor, unit and range together, never a
partial override — and keeps that name's SLOT in the composition order;
a site joint of a new name is appended after every class-declared joint,
in keyword order. Neither is a parameter: the keyword never reaches the
child's constructor and never enters its identity, so two children of
one class differing only in the joints their sites passed still key one
printed artifact. A callable argument at a site is called with the
REALIZED DECLARING PARENT (not the child, and not a ``.repeat()`` copy's
``index``, which is not yet assigned when a site's arguments resolve).
Refused by name at class definition: a keyword naming a port, a
parameter, or any other attribute the child already answers to; a joint
declared on some third class; two things landing on one coordinate. A
site-declared joint's operations are carried through the inverse of the
child's own rest placement (the arithmetic a class-declared joint no
longer needs, restored for this one case), so a rest placement the
framework cannot evaluate numerically refuses binding a SITE-declared
joint by name, where it would not refuse a class-declared one on the
same body.

No project is edited by this change; the evidence is a read-only
overlay, and every project the catalogue tracks — including the four
cycle 2 leaves broken or refused (OpenCycloid, the Internal Cycloidal
Actuator, Inmoov-sim, openflexure-microscope) — compares at maximum
deviation 0 against its pre-cycle-2 reference. (OpenSpec change
``declaration-site-joint``, extending ADR-097 and reviving ADR-094's
``_OWN_PLACED_ORIGIN`` sentinel and ADR-093's composition order one
writer further out.)

**A joint is stated in the frame of whoever declares it.** A joint
written in a class body says where THAT body may move, so it is now read
in the body's OWN rest frame rather than the parent's — MuJoCo's rule,
where a ``<joint pos>`` is a point of the body frame — and ``at``
defaults to the body's own origin::

    class Pinion(Solid2Node):
        turn = Revolute(axis=(0, 0, 1), unit='deg')   # its own bearing, no anchor

A survey of the whole catalogue — 23 projects, 249 class-body joint
declarations — found that 133 of them are exactly this shape (a wheel,
a gear, a pinion, a screw turning on its own bearing) and roughly 30
more are hand-written ``rotate()`` calls that exist only because a
shared class placed at several sites, or several attitudes, had no way
to state one parent-frame anchor that was right everywhere. A body its
parent ROTATES now carries its joint line WITH it, so Thor's thirteen
catalogue parts, the V8's four timing gears and openflexure's four
flexure legs can each state one declaration instead. The framework
transforms nothing: ``Joint._carry``, the inversion that used to carry a
parent-frame axis and anchor into the body's own frame, is deleted
outright, and with it the framework's only use of ``numpy`` in this
module. ``Orbit``'s ``carries`` now defaults to the plain ``(0, 0, 0)``
it always meant in the body's own frame, with no sentinel; a ``Free``'s
three directions are the declaring body's own rest frame's, literally,
and its translation — the outermost operation of its own run —
displaces along those same fixed directions rather than along whatever
the rotations have just turned. A rest placement the framework cannot
evaluate numerically no longer prevents a joint from being bound,
because nothing inverts it any more.

The rule is not free. **The one silent case:** a ``Revolute``, ``Orbit``
or ``Free`` written today with no ``at`` on a body its parent
TRANSLATES meant "about the parent's origin"; it now means "about my own
origin". The survey found 47 such sites, 35 of them inert (a
``Prismatic``, or a placement translation parallel to the joint's own
axis) and 12 that change a pose. Ten of those twelve name a line that
belongs to the ASSEMBLY, not the body — the Internal Cycloidal
Actuator's two disk ``Orbit``\ s, InMoov's seven finger ``Revolute``\ s,
openflexure's one ``GearLockScrew.orbit`` — and are not migrated by this
change: their real form is a joint stated at the site that already
knows the line, which is the next cycle's feature, and until then those
three projects keep exactly what they carry today. The other two are
3DPrintedClocks wall clock 48's, which are the fix its own source
comment already asked for. **Five axes lose their literal:** where one
class is placed at several sites with OPPOSED rotations — both Prusa
belt-guide pairs, hangprinter's mirrored motor gear and roller pair,
OpenVMP's two legs — today's one parent-frame literal cannot be written
as one own-frame literal any more. A callable of the realized node
(reading the body's own parameter, or a ``.repeat()`` copy's ``index``)
or the parent supplying the sign in the relation (``ratio=-1``, or
``law=`` under a broadcast) both already exist as bridges; neither is
new machinery, and the literal returns once a joint can be stated at a
declaration site.

No project is edited by this change. The evidence is a read-only
overlay of each project's simulation package with its joints
mechanically rewritten per the survey: all 23 (plus a 24th, OpenCycloid,
added after its own stage B landed mid-cycle) compare at maximum
deviation 0 against the unmodified project, with two named exceptions.
3DPrintedClocks wall clock 48 is EXPECTED (its own source was already
migrated ahead of this change, and the new engine correctly stops
reproducing an old double-transformation bug there — carried to the
pilot as an open question, not accepted as a difference). A handful of
other clocks show a 1-8 micron residue on a wound-string port that
disappears when the two captures being compared are pinned to the same
Python hash seed — capture-process nondeterminism in a pre-existing
solver, not a source difference, and not evidence about this change.
OpenCycloid's own default-only source, unlike the other three
PARENT-KNOWLEDGE-IN-SUBSTANCE projects, has no `at=` to delete at all:
both `at` and `carries` default to the same point under the new rule
where the old rule's asymmetric defaults gave a real eccentricity for
free, so every one of its orbits now REFUSES at bind, by name, rather
than building a silently wrong pose — confirmed directly against the
unpatched project; its own DERIVED overlay (parity with the Internal
Cycloidal Actuator's own migration) still reaches 0. (OpenSpec change
``joint-frame-follows-declarer``; ADR-097, superseding ADR-088's frame
decision in part and revising ADR-094 and ADR-095.)

**A relation broadcasts over a repeated child.** ``.repeat(n)`` says one
part, n placements; nothing said *one relation, n copies*, so a machine
whose repeated parts move was a machine whose motion was written back
out by hand. An abacus column bound its four beads by hand::

    def simulate(self):
        for index, bead in enumerate(self.earth_beads):
            bead.travel = earth_lift(self.earth.value, index, self.stroke)

One relation, with a per-copy ``law=``, now replaces the loop::

    earth.drives(earth_beads.travel, law=earth_lift)

    def earth_lift(column, bead):
        return lambda level: clamp(level, bead.index) * column.stroke

A relation whose DRIVEN end reaches through a repeated child is a
**broadcast**: it resolves to one relation per realized copy, at the
position its declaration was written, in copy order. ``law=`` is called
once per COPY at realization — the copy is the driven end's owner under
a broadcast, so a per-copy sign, phase or rank is one attribute read,
the copy's own ``index`` — with no change to the callable's two-argument
signature. ``ratio=``/``offset=`` still resolve once against the
declaring instance and the same ``Affine`` is every copy's law. Every
copy a repeat realizes now carries its own 0-based ``index``, a plain
instance attribute: never a declared parameter, never part of a part's
identity or its cached artifact, and refused where the repeat is written
if the repeated class already answers to that name. A repeated end is a
driven end only — named as the source, in any spelling, it is refused
at class definition naming the repeated declaration and its class — and,
once bound, a broadcast is never read backwards, whatever its law
offers: the copies hold one value each, and the framework does not
compare values to decide they agree.

``get_coordinate(node, name)`` joins ``set_coordinate`` in
``solid_node.motion.ports``: the reader for any name the port enumerator
reports, plain or dotted (``pose.roll``), returning the bound slot
rather than the value so an unbound coordinate reads back as ``None``
rather than being confused with a name that names no coordinate at all.

Nothing else changes: no new document key, no viewer or serialization
change, nothing deprecated, and a pose comparison over every project on
the catalogue that uses ``.repeat()`` with the motion layer moves
nothing. (OpenSpec change ``repeat-fan-out``; ADR-096, extending
ADR-089 and depending on ADR-061, ADR-063 and ADR-093.)

**A body that floats is one declaration.** A walking robot's chassis has
no parent to be jointed to: it stands where its legs put it, six freedoms
against the ground. Nothing said that. The hexapod in the catalogue
applies its chassis pose by hand — four chained calls in its root's
``simulate()`` — and hand-inverts exactly that composition to bring a
foot target on the ground into the chassis's frame, so every leg solution
in the model depends on a product written in two places. Stated as four
joints it costs four declarations and four forwarding ports, and says
*four independent freedoms* where the machine has *one floating body*.
``Free`` is one declaration owning SIX coordinates::

    class Chassis(AssemblyNode):
        pose = Free(angle_unit='deg', length_unit='mm')

    def simulate(self):
        self.chassis.pose.roll = self.roll
        self.chassis.pose.pitch = self.pitch
        self.chassis.pose.yaw = self.yaw
        self.chassis.pose.z = self.height

The six — ``roll``, ``pitch``, ``yaw`` in ``angle_unit`` and ``x``,
``y``, ``z`` in ``length_unit`` — are ordinary coordinates: bound by
assignment, named at either end of ``drives``, read by a driver or an
expression, reported by the port enumerator. What is new is the NAME. A
joint owning one coordinate still names it after the joint; a joint
owning several names each ``<joint>.<coordinate>``, so these are
``pose.roll`` … ``pose.z``, and that one string is the port's name, the
enumerator's key and the tail of a relation path
(``tilt.drives(chassis.pose.pitch)``). It is not a Python identifier, so
it is deliberately not a wiring keyword: both wiring forms are refused
where they are written, naming the joint and listing what it owns.

The composition is fixed by the joint, innermost first —
``R(roll, x̂) · R(pitch, ŷ) · R(yaw, ẑ) · T(x, y, z)`` about the point
``at`` names in the parent's frame — and it is the product the hexapod
hand-inverts, measured against it at seven poses including two at gimbal
lock before a line of the joint was written. Binding any one of the six
re-places the whole joint, so the order they are bound in never shows;
an unbound coordinate places nothing while still reading as unbound, so
the hexapod's four-of-six leaves the other two at the identity. A
``Free`` takes no ``axis`` — a free body turns about the frame's own
three directions — and no ``range``.

Three angles gimbal-lock at ``pitch = ±90``; that is inherited from
stating an attitude as three angles at all, and the fixtures record the
degenerate pose rather than avoiding it. Nothing else changes: no new
operation kind, no document key, no viewer or serialization change,
nothing deprecated, and no existing declaration, pose or test moves.
(OpenSpec change ``free-joint``; ADR-095, extending ADR-088 and
depending on ADR-093.)

**A body can be carried round a line without being turned by it.** A
cycloidal disk on its eccentric, a connecting rod's big end on the crank
pin, the lower half of a parallelogram leg: a point of the body travels
a circle while the body's attitude stays exactly as it was. No primitive
said that. A ``Revolute`` about the same line turns the body too, so a
project paid for it in every ratio that then had to cancel the unwanted
turn; a pair of ``Prismatic``\ s with a trigonometric ``law=`` each says
it but has no inverse, so nothing can be driven backwards through it —
one project carried forty of them, with forty laws, for four freedoms.
``Orbit`` is the third one-coordinate declaration::

    class CycloidalDisk(Solid2Node):
        spin  = Revolute(axis=(0, 0, 1), unit='deg')   # innermost: its own centre
        orbit = Orbit(axis=(0, 0, 1), unit='deg')      # outermost: the drive axis

    shaft.spin.drives(disk.orbit)
    shaft.spin.drives(disk.spin, ratio=-1.0 / REDUCTION)

``axis`` and ``at`` mean what they mean on a ``Revolute`` — a direction
and a point ON the line. ``carries`` is the point of the body that
travels round it, in the same frame, defaulting to the body's own placed
origin. The eccentric radius and the starting phase are **derived from
that point and that line and can never be declared**: OpenCycloid, whose
disk is placed at its eccentric offset, writes the two lines above and
its ``ratio=-1.0 / REDUCTION - 1.0`` loses the ``- 1.0`` it only ever
carried because the orbit used to turn the body. A carried point lying
ON the line derives a radius of zero — the body would not move — and is
refused by name at the first binding.

An orbit's coordinate is an ANGLE, so a relation into it inverts exactly
as a relation into a ``Revolute`` does, and its placement is one ordinary
translation whose components are built in the framework's own degree
trigonometry: a symbolic binding publishes ``cos``/``sin`` expressions
the viewer already evaluates.

Nothing else changes: no new operation kind, no document key, no viewer
or serialization change, no parity-corpus entry, nothing deprecated, and
no existing declaration, pose or test moves — ``Revolute`` and
``Prismatic`` place their bodies with the same code they placed them with
before. (OpenSpec change ``orbit-joint``; ADR-094, extending ADR-088.)

**The joints of one class compose in declaration order.** A body with
more than one freedom used to compose them in the order their
coordinates were BOUND — which, when relations bind them, is the
couplings solver's pass order: a property of where the relations were
written, not of the class carrying the joints. A reader of the class
body could not see it, a derived coordinate could silently change it, a
sweep and a re-bind could reverse it between two runs, and seven
projects in the catalogue met it, six of them blocked outright. The
joints declared on one class now compose in **declaration order**, the
first declared innermost and the last outermost, whatever order they are
bound in::

    class Chassis(AssemblyNode):
        roll  = Revolute(axis=(1, 0, 0), unit='deg')   # innermost
        pitch = Revolute(axis=(0, 1, 0), unit='deg')
        yaw   = Revolute(axis=(0, 0, 1), unit='deg')
        lift  = Prismatic(axis=(0, 0, 1), unit='mm')   # outermost

so a class read top to bottom reads a machine from the body outward.
Base-class joints come before a subclass's, and a subclass redeclaring
an inherited joint keeps the position the base gave it — which is what
``declared_joints()`` already reported and is now the contract. Each
joint's operations are one contiguous run at its own position, so
re-binding one joint of several returns it to its place instead of
moving it outside its siblings, a sweep and a re-bind compose the same
way they did before, and two assemblies animating different joints of
one node no longer decide the order between them by walk order. There is
no ordering keyword: if a body's freedoms stack the wrong way round,
reorder the declarations.

**Hand-written motion now composes outside the whole joint block**,
keeping its call order among itself — where before it interleaved with
joint motion in the order it was applied. This is a visible behaviour
change and the only part of this release no project asked for; it is
what makes the joint block a contiguous, reorderable unit. It can only
affect a node where a hand-written simulate-phase ``rotate``/
``translate`` runs BEFORE that node's joint is bound. Measured across
the sixteen migrated catalogue projects, every model, before and after,
**maximum deviation 0.000e+00** — 32 models, 334 poses, 2 319 leaf world
matrices, not a tolerance.

Nothing else changes: no public name is added or removed, no ordering
keyword exists, the document format, its keys and the viewer are
untouched, and nothing is deprecated — a project that turns its parts by
hand in ``simulate()`` keeps working, and both forms still sit on one
node. (OpenSpec change ``joint-composition-order``; ADR-093, extending
ADR-088.)

**A face-box tier decides an enclosed exact pair without a boolean.** A
whole-solid bound, in any frame, cannot separate a wheel running in the
clearance gap between two plates from the plates it runs between: the
plates' box encloses the wheel's wherever it turns. A second
exact-negative tier now runs after the AABB broad phase and before any
boolean, for a pair of two exact solids: each solid's face boxes (a pure
function of the exact surface, cached once per shape) are compared in one
solid's own frame, and if none of one meets any of the other, a
containment guard classifies one representative point of every solid of
each shape against every solid of the other, in both directions, before
reporting the pair empty. A solid wholly inside another is not mistaken
for this case — the guard still sends it to the boolean, and it still
fails. Flush contact still reaches the kernel, because touching face
boxes count as meeting, and still fouls at exactly 0.0 mm³. No verdict,
message, or epsilon changes; the tier can only remove a boolean it would
have run anyway. No public surface changes: no flag, no environment
variable, no assertion argument. Measured on the originating model's
48-instant swing sweep: booleans fell 1089 → 708 (35.0% fewer) and wall
time 265.99 s → 216.50 s (18.6% faster), the test's own verdict
unchanged. (OpenSpec change ``face-box-broad-phase``; ADR-092, extending
ADR-029 and ADR-091.)

**The whole-assembly interference index chooses its own indexing
frame.** A world-axis conservative bound is exact for an axis-aligned
part and grows under rotation; when every part in an assembly shares
one outermost rigid turn, every box grows and the index no longer sees
how sparse the assembly really is. ``assertNoSolidInterference`` now
indexes its candidate pairs in a chosen frame: the world frame, or the
placement frame of one of the assembly's largest topmost solids by
local-bounds diagonal, whichever scores the smallest total box volume,
world winning ties. A bound taken in a non-world frame is enlarged by a
small fixed margin absorbing the extra arithmetic the frame change
costs, so a flush-contact pair is never lost to it; world bounds are
never enlarged, so an assembly that gains nothing from the choice is
indexed exactly as it always was. The choice can only change which
candidate pairs are emitted, never a verdict, a message, or an epsilon.
``assertAssemblySupported``'s own bounds are unaffected and stay
world-axis, because gravity is a world-frame fact. No public surface
changes: no flag, no environment variable, no assertion argument.
(OpenSpec change ``broad-phase-indexing-frame``; ADR-091, extending
ADR-029.)

**The verdict memo absorbs float noise between two rigid motions.** A
pair carried together by a rotating parent recomposes a relative matrix
that differs from the previous instant's by float noise far below any
real placement — the residue of composing the same motion through a
different multiplication order — and the memo's exact-bytes key
(ADR-070) missed every one of those. ``solid test`` now resolves a
run-wide **placement quantum**: the relative matrix is divided by it and
rounded to integer cell indices, so two placements in the same cell are
one question. ``--placement-quantum MM`` / ``SOLID_TEST_PLACEMENT_QUANTUM``
select it, the same way as the kernel and the volume epsilon; the
default is ``1e-9`` mm, and ``0`` restores the exact-bytes key exactly.
Unlike the volume epsilon, the quantum applies under both kernels and
the exact kernel accepts it. A run at the default quantum is unchanged,
byte for byte; a non-default quantum names itself on the summary line.
(OpenSpec change ``quantise-verdict-memo``; ADR-090, amending ADR-070.)

**One coordinate can drive another.** A class body may now state a
relation between two coordinates, wherever they are in the tree::

    class Movement(AssemblyNode):
        power = TrainArbor(index=0)
        centre = TrainArbor(index=1)

        power.drives(centre, law=going_train)

``drives`` needs no import, and it is the ONLY vocabulary for relating
two coordinates: the framework looks up no method, attribute or hook of
any name on a project's class to discover what a relation means. Written
bare it is a statement, recorded on the class; assigned
(``great = power.drives(centre)``) it is additionally named, so a test
can reach it and every message about it can say its name. Either end may
be a port, a joint, a child declaration standing for its class's ONE
joint, a path through declared children (``motion_works.cannon.turn``,
``shoulder.art2.art3.wrist``), a derived coordinate, or — as the source
only — a ``Driver``, so a root driver reaches a joint at any depth
without a port forwarded at every level in between.

``drives`` states the MECHANICAL direction; which way the framework
SOLVES it is decided per run from whichever end is actually bound —
forward through the law, backward through its inverse — so a going train
written from the power arbor forwards is solved backwards from the one
arbor its ``simulate()`` bound, with nothing reordered.
``Affine(ratio, offset)``, the one new importable name in
``solid_node.motion.couplings``, is that law's usual shape, and
``ratio=``/``offset=`` on ``drives`` are its shorthand; ``law=`` takes a
CALLABLE of the two realized coordinate owners, called once per instance
at realization, so a project's own function reads the tooth counts and
the registration off the two arbors it is handed and returns the law.
Everything stays symbolic: a driver read or ``$t`` rides through a
relation into the published expressions the viewer already evaluates,
and is a plain number under ``set_state``.

A **derived coordinate** — a linear formula over coordinates, written in
the class body: ``relative_elbow = art3.elbow - shoulder``,
``left = wrist + 2 * tool`` — is itself a coordinate of the class. It
reads on an instance as a bound port slot, ``declared_ports`` reports it
under its name, it can drive and be driven, and it solves backwards
through exactly one unbound term. Anything that is not linear is a
``law=``, and a product of two coordinates is refused where it is
written.

Reading a port, a joint or another child off a child declaration in a
class body now yields a PATH REFERENCE instead of raising: naming a
place in the tree is what a declaration has always done. Reading a
declared PARAMETER sideways is still refused with the same message, and
so is reading a ``Driver``.

Three refusals keep a wrong drive network from becoming a pose, each its
own error kind exported from ``solid_node.motion.couplings`` and each
naming the node paths, the relation as written and the ends:
``UnreachedCoordinate``, ``DoublyBound`` (an author's binding, a wiring
or another relation already bound that coordinate — including two
relations that would agree, because the framework does not compare two
symbolic expressions to decide whether they do) and ``NotInvertible``.
Wirings are now solved together with the relations, in one fixpoint at
the end of the simulate phase, so a wiring whose source a relation
solves binds after it instead of refusing an unbound source; and at the
START of that phase the framework clears what it bound through a wiring
or a relation in the previous run, so each instant re-solves from the
author's fresh binding. Nothing an author's own code bound is ever
cleared. (OpenSpec change ``couplings``; ADR-089, extending ADR-061 and
ADR-066.)

**A joint says where a body may move.** ``solid_node.motion.joints`` now
holds the two one-coordinate lower pairs, ``Revolute`` and ``Prismatic``,
declared as a class attribute of the node they move:
``elbow = Revolute(axis=(0, 0, 1), at=(0, 160, 68), range=(-135, 135),
unit='deg')``. ``axis`` and ``at`` are stated in the PARENT's frame — the
frame the parent's ``render()`` places the node in, where MuJoCo and
Modelica state them too — and each component may be a number, a declared
parameter, a formula over them, or, for the whole argument, a callable of
the realized node; they resolve at realization and never enter a part's
build identity. A joint owns exactly one coordinate and that coordinate
is a port: reading the joint gives the port slot, ``declared_ports``
reports it under the joint's name, and assigning to it binds through the
one binding path ``connect()`` uses. Binding it PLACES the body: the
framework inverts the node's rest placement to carry the parent-frame
axis and anchor into the node's own frame and applies ordinary rotations
and translations there, so an axis that does not run through the moving
part's origin no longer needs the frame arithmetic every robot arm writes
by hand, and nothing new travels on the wire. A parent may hand one of
its coordinates down to a child declaration by naming a port or joint the
child declares — ``wheel = Arbor(index=index, turn=turn)`` — which is a
wiring rather than a parameter: absent from the child's parameters and
identity, rebound from the parent's end on every ``simulate()``, refused
at class definition when the child cannot receive it, and the coordinate's
one binder. A numeric binding outside a declared ``range`` raises
``JointRangeError`` naming the node, the joint, the value and the range;
a symbolic binding is not checked, because its value is not known at bind
time. Nothing is deprecated: a project goes on turning its parts by hand
in ``simulate()`` for as long as it likes, and both forms may sit on one
node. (OpenSpec change ``joints``; ADR-088, extending ADR-056 and
ADR-066.)

**Ports and the declared time base moved to a new** ``solid_node.motion``
**package.** ``solid_node.motion.ports`` is now the one home for
``Port``, ``BoundPort``, ``RotationalPort``, ``TranslationalPort``,
``SignalPort``, ``bind``, ``declared_ports``, ``Time`` and
``declared_time`` — the module that answers what moves and what drives
what, alongside the empty ``solid_node.motion.joints`` and
``solid_node.motion.couplings`` two later cycles will fill.
``solid_node.node`` no longer exports any of those six names and no
longer has ``ports`` or ``timebase`` submodules; there is no shim, alias,
or deprecation warning. ``from solid_node.node import RotationalPort,
SignalPort, Time`` now raises ``ImportError`` naming
``solid_node.motion.ports``; migrate to ``from solid_node.motion.ports
import RotationalPort, SignalPort, Time``. (OpenSpec change
``motion-package``; ADR-087, amending ADR-056 and ADR-072 on export
location only.)

**Simulation time boundaries now fail before effects.** ``Sim`` requires a
finite positive ``dt`` before binding its node, and instants, cadence periods,
run durations, and instruction durations require finite real seconds with
their declared sign and whole-tick constraints. A past absolute instant is
rejected while the current tick remains schedulable through ``run(0)``.
Zero-duration instructions now settle and bind every target immediately at
the current tick without advancing time or adding a trajectory entry.
(OpenSpec change ``validate-simulation-time-boundaries``; ADR-083.)

**New-project guidance now defers viewer details to development.** The
successful ``solid new`` message still shows how to enter the generated
directory and run ``solid develop``, but no longer promises a browser at a
hard-coded port. The development command owns viewer selection, configured
ports, and dependency diagnostics. (OpenSpec change
``make-scaffold-next-steps-viewer-neutral``.)

**A repeated subexpression is published once, not once per use.** Every
symbolic value in the framework is a solid2 ``OpenSCADConstant``, and
``OpenSCADConstant`` is string-eager: a value used twice is written out
twice, and a value reused at each of several nested levels is written
exponentially often. 3DPrintedClocks' grasshopper escapement
(``wall_clock_53_grasshopper``) found the far end of that: its published
``viewer.json`` was 31,638,555 bytes, of which 31,611,478 were operation
expression text — seven million written copies of 263 distinct
subexpressions — and the document would not animate in the browser
viewer. The export ``manifest.json`` and the normal-build ``viewer.json``
now gain an ordered top-level ``bindings`` table: a subexpression that
occurs more than once anywhere in the document's expressions is published
once, named, and referenced by name everywhere it occurred, except a bare
number or a bare driver id, which is shorter written out than referenced.
Rebuilding that same clock's document measured expression text falling
from 31,611,478 to 3,130 bytes and the document itself from 31,638,555 to
32,227 bytes, with 56 bindings published and the longest one 212
characters; every one of its 116 operation values, evaluated at three
points in the animation under the document's own OpenSCAD-degree
semantics, matched the flattened document's exactly. A document with
nothing to share is byte-identical to the one the framework has always
published. A document carrying a non-empty ``bindings`` table declares
schema **version 4**, and the bump is not additive: a consumer that
ignores ``bindings`` would resolve a reference to nothing and render a
wrong pose, so a consumer that cannot read version 4 refuses the document
rather than render it, in the same phase that already refuses an unknown
version. Sharing is detected at serialization by a new internal parser
(``solid_node/core/expressions.py``) reading the expression text the
producer already built; nothing about how a project writes kinematics, or
about solid2's own arithmetic, changes. An expression the parser cannot
read — reachable only through a hand-written ``scad_inline`` string
outside the grammar the two producers emit — is published verbatim and
unshared, with a warning, and never fails the build. The ``.scad`` path
is untouched: it reads operation and port values directly rather than
their serialized form, so generated SCAD and ``Solid2Node.as_number``'s
OpenSCAD round-trip are unaffected, and ``solid snapshot --renderer web``
keyframes and bakes constants, so it never carries a table and stays at
version 2/3 with any viewer. The producer cost is small against a CAD
build: two clean rebuilds of the grasshopper clock (STLs already current)
measured 17.6 s and 23.3 s of whole build time. **A viewer that has not
yet widened its accepted document versions to include 4 refuses a
version-4 document, loudly, in its own prepare phase, before the live
scene is touched** — until the paired ``solid-node-viewer`` change lands,
this is expected for nearly any animated model, not only a
grasshopper-sized one, because the sharing rule has no size threshold: a
subexpression as small as ``$t * loop`` reaching two operations is
already enough. (OpenSpec change ``expression-bindings``, ADR-080.)

**Empty non-rigid assemblies now build as empty groups.** A declarative repeat
resolved to zero, omission of every declared child, or an explicit empty child
list now passes through assembly and serialization as ``children: []`` and
produces no STL for the non-rigid group. A rigid fusion with no selected child
is rejected during validation because it cannot represent one solid.
(OpenSpec change ``support-empty-assemblies``; ADR-082.)

**All-model tests now continue after a model fails to build.** During
``solid test --all``, a failure while loading, constructing, keyframing,
rendering, assembling, or generating artifacts is counted once against the
declared model and the next model still runs. ``--failfast`` records that
failure before stopping, and both paths retain the command's single aggregate
report. (OpenSpec change
``continue-all-model-tests-after-build-failure``.)

**New-project scaffolds always use valid Python identifiers.** Names that
sanitize to a leading digit or Python keyword now gain a deterministic
``project_`` prefix before paths, modules, classes, and the manifest are
derived. For example, ``solid new 3d-printer`` creates
``project_3d_printer:Project3dPrinter``; established punctuation normalization
such as ``snowman-3`` to ``snowman_3:Snowman3`` is unchanged. (OpenSpec change
``normalize-scaffold-identifiers``.)

**Successful unchanged builds now clear prior failure status.** A complete
build removes ``errors.json`` after constructing its viewer document even when
those document bytes already match the published snapshot. The snapshot stays
untouched, while ``solid models`` transitions from ``failed`` to ``published``.
Development callbacks report that recovery after the build lock is released;
a true no-op with no prior error remains silent. (OpenSpec change
``clear-recovered-build-errors``.)

**Development watches now rebuild for every tracked source.** After successful
assembly, modifications to explicitly tracked OpenSCAD, JSCAD, STL, STEP, and
Python sources all end the current builder pass so the develop loop can reload
the model. The recursive recovery watch used after a failed load remains
limited to Python sources outside ``__pycache__`` to avoid rebuild noise.
(OpenSpec change ``watch-all-tracked-sources``.)

**Every tracked source now guards artifact currency.** A settled artifact must
match both the maximum source timestamp and a recorded metadata fingerprint of
each contributing file, so an edit to an older dependency cannot be hidden by
a future-dated source. Fingerprint changes invoke the existing node-scoped
content digest, preserving no-op timestamp rewrites, relocated projects, and
unrelated sibling-class edits without regenerating geometry. Legacy
digest-only sidecars validate and upgrade in place; malformed records rebuild.
(OpenSpec change ``guard-source-set-currency``; ADR-081.)

**Artifact-producing assembly now holds the project build lock.** Ordinary
builds acquire their selected build lock before assembly can materialize SCAD,
BREP, or STL files and keep it through viewer-document publication. The test
runner likewise holds one lock through keyframing, preliminary render,
assembly, and STL generation, then releases it before project tests execute.
A builder whose loaded sources change while it waits stands down before
rendering. (OpenSpec change ``lock-artifact-assembly``.)

**Static exports keep every model inside the requested output.** Model paths
are now derived from the same project-aware, selected build directory that
owns the artifacts, rather than from the command's working directory. Exporting
an explicit reference from a nested directory therefore retains the portable
``models/<source path>/<artifact>.stl`` layout. A custom node whose STL resolves
outside its build directory is rejected before the output changes, with a
controlled CLI diagnostic. (OpenSpec change ``confine-export-models``.)

**Build preparation preserves sibling data.** The one-time migration from the
retired symlink publication layout now moves only the directory referenced by
the build path. Ordinary preparation and migration leave every other
``<build>.`` sibling untouched, including user notes, backups, legacy-looking
directories, the project lock, and browser snapshot stages still being
captured. An orphan from the retired layout can therefore remain on disk when
its name is the only evidence of ownership. (OpenSpec change
``preserve-unowned-build-siblings``.)

**Failed OpenSCAD renders no longer publish empty geometry.** The asynchronous
STL render protocol now checks OpenSCAD's exit status before replacing the
published artifact. A failed render exits the build nonzero, records the
failure in ``errors.json``, removes its temporary output and render lock, and
leaves any previously published STL and viewer snapshot intact. (OpenSpec
change ``reject-failed-openscad-render``.)

**Reading a STEP document's assembly structure, and scaffolding source
from it.** ``StepAssembly(path)`` reads a document's products and every
occurrence of them, walked through nested sub-assemblies — each
occurrence's placement matrix in its parent's frame, its world matrix
composed outward, and, for every placement that is a proper rigid
transform, the exact ``(angle, axis)``/``translation`` pair that
reproduces it through the framework's own ``rotate`` then ``translate``.
The decomposition goes through OCCT's own quaternion
(``gp_Trsf.GetRotation().GetVectorAndAngle()``), never through the trace
and an ``acos``: measured over the Internal-Cycloidal-Actuator's 55
placements (27 of them exactly 180°, 2 the identity), the quaternion
route reproduces every matrix to 4.4e-16 and the trace route only to
3.0e-8 — thirty times outside the 1e-9 the contract asks, and wrong
exactly on the half-turns. A placement that is not proper — a mirror or
a scale — is reported with its determinant and scale factor and is not
decomposed, because ``rotate``/``translate`` cannot state one; the rest
of the document is unaffected. ``StepAssembly`` is not a node: it reads
through the same cached document ``StepNode`` does, so a process that
has already read a file for one pays nothing more for the other, and
reading the whole structure of the actuator's 35 MB document — 21
products, 55 occurrences — costs 0.042 s after the 11.10 s document
read is warm.

``solid import-step FILE [--into PACKAGE_DIR] [--model NAME]`` turns a
document into project-owned, declarative source in one shot: ``parts.py``
(one ``StepNode`` subclass per part, declaring ``step_source``, ``part``
and ``angular_deflection = 0.5`` under a comment) and ``assembly.py``
(one ``AssemblyNode`` per assembly product, one child declaration per
occurrence, and a ``render()`` placing each by ``rotate`` then
``translate`` at the document's own transform, under a comment naming
the occurrence and the file). The generated machine is at rest — no
driver, no ``simulate()`` — and the command never overwrites an
existing ``parts.py`` or ``assembly.py``, writes nothing when any
placement is improper, and prints the manifest lines rather than
editing ``pyproject.toml``. Born of the same two projects as ``StepNode``:
``Internal-Cycloidal-Actuator``'s design record named six placements
typed by hand into ``machine.py``, one of them (``Eccentric_Shaft``) an
axis sign that is not visible in the matrix at a glance, and a
recomposition test that existed only to check the typing; ``openvmp``
wrote the same occurrence walk against PartCAD's ``.assy`` format.
Scaffolded into a scratchpad project and built against this cycle: the
actuator document builds in 21.5 s, 20 distinct part artifacts (the
other 35 of 55 occurrences share theirs, as repeated placements of the
same product always have), 11.74 MiB of STL against the 19.91 MB one
part alone would cost at the inherited default; every one of the 55
generated leaves' composed world placements agrees with the reader's
own world matrix to within 4.93e-10 mm, the contract
``Internal-Cycloidal-Actuator``'s hand-written ``test_machine.py``
existed only to check by hand. See :ref:`import-step`. (OpenSpec change
``step-assembly-import``; ADR-079.)

**The STEP part, an exact external-file leaf.** ``StepNode`` reads one
product out of a STEP document as an ordinary part —
selected by ``part``, naming the product as the file carries it; a
document with exactly one candidate product (a bare single-part file,
or the commoner file in which an exporter wraps one part in an
assembly) needs no ``part`` at all, while a document of several never
hands its assembly root to a node by omission. A wrong or missing
``part`` fails with the document's own inventory — one line per
product, naming its kind, occurrence count, solid count, bounding box
and volume — so no separate inspection tool has to exist. The selected
geometry is always the product's own, unplaced shape, never an
occurrence's located copy; ``adjust(self, shape)`` corrects it in code,
and the module exports ``solids_from_faces(shape, tolerance)`` for
sewing a vendor part published as bare surfaces, called knowingly from
an ``adjust`` hook — a product that still holds no solid fails
admission naming the node, the file, the part and what it does hold,
and nothing is repaired silently. A subclass that declares no ``color``
takes it from the document — the product's own surface colour, else the
colour every occurrence of it agrees on, else none — converted from
XCAF's linear RGB to the sRGB the framework's ``color`` attribute
already is; a declared ``color`` wins and never opens the document. The
document is read and transferred at most once per file per process,
cached on the file's path and modification time, so several nodes over
one file share one read and a node whose artifacts are current triggers
none at all. Unlike ``StlNode``, this leaf is **exact**: it derives
``ExactLeafNode`` and so inherits ``shape()``, the ``.brep``, exact
fusion and :ref:`declared tessellation precision
<tessellation-precision>` at the same inherited defaults every exact
leaf has, whole. Born of two projects that had each written this reader
by hand — ``Internal-Cycloidal-Actuator`` (a 35 MB, 21-product Inventor
assembly) and ``openvmp`` (67 vendor STEP files) — both of which also
carried their own module-level document cache for the same reason this
leaf now has one built in. Measured on the actuator's own
``Output_Shaft`` through this leaf: 19.91 MB (398,184 triangles) at the
inherited default, against 1.76 MB (35,240 triangles) declaring
``angular_deflection = 0.5``, with an identical ``.brep`` between the
two; reading that 35 MB document costs 14 to 17 seconds once per
process, and a second node selecting from the same cached document
costs 0.0003 s. See :ref:`step-import`. (OpenSpec change
``step-part-leaf``; ADR-078.)

**Declared tessellation precision.** An exact leaf (``CadQueryNode``,
``Build123dNode``, ``Build123dSheetNode``) or a ``FusionNode`` fusing
exact children may now declare ``linear_deflection`` (mm) and
``angular_deflection`` (radians) as class attributes, shaping how finely
that node's own ``.stl`` is tessellated. A node declaring neither is
tessellated at ``linear_deflection = 0.1`` and ``angular_deflection =
0.1`` — the values the framework has always used — so an existing
project's artifacts do not change. The declaration is not a constructor
parameter and does not enter the node's artifact identity: editing it
rebuilds the same artifact in place through the ordinary node-scoped
content path (ADR-071), the way editing
:attr:`~solid_node.node.SheetLeafNode.thickness` does when it is
declared rather than passed. A ``FusionNode`` declares precision for its
own fused solid and does not inherit a child's. Only the mesh changes:
the ``.brep`` and ``shape()`` are identical whatever is declared, but
everything that reads the mesh — the viewer, the export, a faceted
``solid test`` run, and printed-piece identity (a fingerprint of built
content) — sees the declared precision, so redeclaring it gives a node a
new piece id. ``openvmp`` and ``Internal-Cycloidal-Actuator`` are the two
projects that asked for this, each having reached past the public API
into ``BRepMesh_IncrementalMesh`` to premesh a shape before ``render()``
returned it; Internal-Cycloidal-Actuator's design record measured the
cost on a vendor STEP part: 19.9 MB (398,184 triangles) at the
framework's default against 1.8 MB (35,776 triangles) at
``angular_deflection = 0.5``. See :ref:`tessellation-precision`.
(OpenSpec change ``declared-tessellation-precision``; ADR-077.)

**The expression vocabulary projects kept rebuilding.**
``solid_node.math`` now carries ``abs``, ``floor``, ``ceil``, ``sign``,
``min`` and ``max`` — the OpenSCAD builtins, emitted by name — plus
``clamp``, ``clamp01``, ``ramp``, ``lerp``, ``wrap``, ``piecewise`` and
``bump`` composed over them, and the vector helpers ``polar``, ``turn``,
``rotate_x``, ``rotate_y`` and ``rotate_z``. Each has the module's three
faces: a number in tests, a deferred OpenSCAD expression in the viewer,
and a dimension-checked formula in a declarative class body. Born of
thirteen project ``kinematics.py`` modules: four of them built a clamp
kit out of ``sqrt(x * x)`` believing the browser had no ``min``, ``max``
or ``floor`` — it has had all three all along — and four clock models
imported solid2's private ``OpenSCADConstant`` to emit ``floor``
themselves. An abacus clamp that published 123 characters of nested
``sqrt`` now publishes 44 of ``min(max(...))``.

There is deliberately no ``round`` (OpenSCAD, JavaScript and Python
round halves three different ways; ``floor(x + 0.5)`` is the half-up all
three agree on) and no ``mod`` (OpenSCAD spells it as the ``%``
operator, whose sign rule differs from Python's). ``floor`` and ``ceil``
take a dimensionless quantity, because a whole number bears no
dimension: count in the unit you mean, ``floor(travel / pitch)``. Every
name the module can emit is in ``solid_node.math.SYMBOLIC_BUILTINS`` and
is pinned by the cross-runtime parity fixture, which the generator now
refuses to write while one is uncovered. A call mixing animation time
with a declared parameter, which used to render the declaration's
``repr()`` into the published expression, now raises. See
:ref:`Non-linear kinematics <non-linear-kinematics>`. (OpenSpec change
``expression-math``; ADR-022, revised.)
**The mechanism laws, carried once.** ``solid_node.mechanisms`` holds
the textbook geometry thirteen projects' ``kinematics.py`` kept
rewriting, each in its own frame and sign convention: the external
spur-gear mesh and its inverse (``meshed_angle``, ``driving_angle``),
the lead screw (``screw_travel``, ``screw_angle``), the planar
slider-crank (``crank_pin``, ``crank_rod_angle``, ``piston_height``),
linear delta kinematics (``delta_carriage``, ``delta_rod``) and the
circle geometry a linkage asks for (``circle_intersection``,
``triangle_angle``, ``link_rise``). Every one is a composition over
``solid_node.math``, so it computes on numbers and builds the viewer's
expression on symbolic time or a driver, and emits no OpenSCAD builtin
that module does not already emit. A gear library's convention is two
argument values rather than a fork of the law: cq_gears' gap centre at
``180 / teeth``, MrBunsy's at ``gap_angle / 2``. There is no declared
(class-body) face — the laws carry degree literals the dimension
algebra cannot type as angles, so a declared token raises there and
``.value`` is the way through. Lifted from ``sandbox/gearbox``,
``3DPrintedClocks`` (``wall_clock_01`` and the grasshopper),
``v8-engine``, ``kossel``, ``openflexure-microscope``, ``Inmoov-sim``
and ``snappy-reprap``, and checked against each of their own functions.
(OpenSpec change ``mechanisms``.)

**Several models in one project.** A manifest may declare its models by
name in ``[tool.solid-node.models]``, with ``model`` naming the default
among them; a manifest without the table is unchanged. A declared name
is a node reference — ``solid build wall_clock_02`` — and each declared
model owns its own build directory, ``_build/<name>/``, with its own
``viewer.json``, ``errors.json`` and lock, so publishing one model never
sweeps another. ``solid models`` lists them with their state, as text or
``--json``, without importing project code; ``solid build --all`` and
``solid test --all`` walk every declared model and never stop at a
failing one. Born of ``3DPrintedClocks``: one repository, one shared
library, one model per clock. (OpenSpec change ``named-project-models``;
ADR-119 (numbered 073 at the time).)

**A test run chooses its comparison kernel.** ``solid test`` compares on
the exact boundary-representation kernel by default, exactly as before,
or on the parts' meshes with ``--faceted`` — selected for a checkout by
``SOLID_TEST_KERNEL=faceted`` in its ignored ``.env``, so CI keeps the
exact kernel with no configuration. A faceted run answers every
intersection, containment, connectivity and weld question at
tessellation precision, carries one run-wide volume epsilon
(``--volume-epsilon``, ``SOLID_TEST_VOLUME_EPSILON``; refused by the
exact kernel), and names itself before the first build and on its
summary line. Nothing about the model, the build or ``node.exact``
changes between the two runs. On the v8-engine root suite, whose springs
made every comparison an OCCT Boolean, the faceted run takes 90 s where
the exact run took 28 minutes and reaches the same verdict on every
comparison at epsilon 0. ``solid new`` now ignores ``.env``. (OpenSpec
change ``faceted-test-kernel``.)

**A declared time base.** A root assembly can declare what one turn of
the animation timeline *is*: ``time = Time(loop=12 * 3600)`` says a turn
is twelve hours, and from then on ``self.time`` reads seconds everywhere
— ``$t * loop`` on the symbolic build path, so ``$t`` stays the 0..1
slider and the multiplication travels inside the published expressions;
the bound number under ``set_keyframe``, the testing decorators and a
stepped simulation, all of which state seconds. Every assembly below the
root reads the root's time base, and a declaration on a linked descendant
is refused when read. The documents ``solid build``, ``solid export`` and
the web snapshot publish carry ``animation.loop`` beside ``fps`` and
``frames`` (additive; an older viewer keeps playing ``frames / fps``),
and ``solid snapshot --time`` keeps its 0..1 meaning, landing on the
seconds that slider position means. A root that declares nothing is
unchanged. See :ref:`Declaring the time base <time-base>`. (OpenSpec
change ``declared-time-base``; ADR-072.)

Migrating a model to ``Time`` changes the meaning of every instant it
states: ``simulate()`` stops multiplying the fraction by a project
constant, tests stop dividing by it, and ``set_keyframe`` callers state
seconds.
**Several node classes in one file rebuild independently.** The
content-verified currency check beneath the mtime rule is now scoped to
the node: a source file that defines more than one node class contributes
to each node's digest only the text that node can see — the file minus
the other node classes' bodies, unless the rest of the file names them —
so editing one class re-derives that node and the fusions above it, and
merely restamps its neighbours. Shared module-level code still rebuilds
every node in the file. Nothing is required of a project's layout any
more: one node per file is no longer a premise of the cache. A file that
defines one node class digests exactly as before, so no existing build
directory rebuilds on upgrade; the nodes of a multi-node file rebuild
once. (OpenSpec change ``node-scoped-currency``; ADR-071.)

**The declarative node API.** A node class body can now *declare* its
parameters (``Length``, ``Angle``, ``Count``, ``Ratio``, ``Flag``,
``Scalar``), derive others as bare formulas over them, and declare its
children by constructing them in the class body — with literal lists and
``repeat(count)`` for identical units. A formula's dimensions are checked
on ``import``; ``sqrt`` and the degree trigonometry of ``solid_node.math``
take part. Each parent instance realizes its own children, top-down from
the root's values, so ``Engine(bore=32.0)`` moves the whole machine, and
``--set name=value`` on every node-loading command does the same from the
shell. An internal node's ``render()`` may return nothing, in which case
the children are the declared ones minus any it ``omit()``\ s; a pure
grouping node needs no ``render()`` at all. Ports bind by assignment.
See :doc:`Declaring a machine <../declaring>`. (OpenSpec change
``declarative-node-api``.)

Nothing changes for a class that declares nothing. When migrating a
class, its artifacts re-key once if it used to omit a keyword from
``super().__init__()`` or passed an integer where a float kind now
resolves; the next build rebuilds them. A node class carrying its own
metaclass must now derive it from ``solid_node.node.declarative.NodeMeta``.

**render() builds the machine at rest; simulate() moves it.** An
assembly's ``render()`` declares structure and places what does not
move, reads no driver, time or port, and runs once per instance. The
new ``AssemblyNode.simulate()`` runs after it on every instant, under
symbolic ``$t`` or the bound state, reads drivers, ``self.time`` and
ports, and every operation it applies composes *inside* the part's
rest placement and is swept before the next run. ``omit()`` in
``simulate()`` raises. Nothing that worked stops working: a
``render()`` that reads a driver keeps re-running per instant as before,
and the build prints one ``FutureWarning`` per class naming the read and
``simulate()``. Placement in ``__init__`` is no longer recommended; it
still works. The rename of ``render()`` proposed by the design reference
is dropped: *render* also means *to make*. See :ref:`Rest and motion
<rest-and-motion>`. (OpenSpec change ``render-simulate-split``.)

**Build parameters have a module of their own.** ``Length``, ``Angle``,
``Count``, ``Ratio``, ``Scalar``, ``Flag``, ``Quantity`` and
``declared_parameters`` are imported from ``solid_node.parameters``, a
top-level peer of ``solid_node.simulation`` and ``solid_node.test``, and
are **no longer exported by** ``solid_node.node``. An import line now says
which of its names is a node kind and which is a knob on the machine:
parameters build the machine, drivers drive it. There is no re-export and
no deprecation path — the declarative parameter surface has never been
released, so the only code to update is code written against an unreleased
branch, and a second working path would defeat the point. Change
``from solid_node.node import CadQueryNode, Length`` to two lines. See
:doc:`Declaring a machine <../declaring>`. (OpenSpec change
``build-parameters-module``.)

**Follow-ups from the first project migrations** (OpenSpec change
``declarative-node-api-fixes``). A list comprehension in a class body
over module-level values now declares children — it used to build
shared instances silently under Python 3.12's inlined comprehensions. A
``Flag`` passed to a declared child now resolves to the parent's
boolean, so a structural choice can live on the root and be set with
``--set``. A declarative node may define ``check()`` for guards over
several parameters at once; the framework calls it once the parameters
are resolved and before any child is realized. The declaring page says
where a once-only placement goes.
