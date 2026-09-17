# Changelog

All notable changes to solid-node-viewer. The Python package and the widget
it carries release together and share one version.

## 0.2.0 — unreleased

The viewer stops posing a machine and starts running one.

- **A clocked machine's declared instructions are PRESSABLE, and a press
  is drawn over its duration: API 19 says so.** solid-node's ADR-129
  decided what an instruction means under a clocked root — ONE request
  over the ONE driver it names, with the declared duration saying how
  long a CONSUMER draws the transition — so the buttons this viewer used
  to list and disable now play. Press one and the machine makes that
  request ONCE, before the first frame: `machine().trigger(name)` returns
  it, the bank stands at the transition's end from that instant, and what
  follows is a PICTURE of it. Each frame poses the tree from the bank the
  machine stood at before, with the moved input at the value the elapsed
  fraction places between the two ends the request now reports (`origin`
  and `end`, taken verbatim from the bank) and every commit whose
  fraction the drawing has reached applied in path order — so **what a
  frame costs is a pose, and the machine is never called in the frame
  loop**. The line is linear like the posed `Ramp` and the last frame
  stands on the request's own end, so the picture finishes ON the
  machine's bank rather than near it; a whole-number input stays whole at
  every frame and never passes the end the machine reported; a downward
  transition is drawn by the same rule. A stopped request is drawn only
  as far as the machine went and the button reports the stop; a request
  an interlock held at zero draws nothing; a duration of zero lands in
  one pose; a refusal draws nothing and is reported where it was pressed.
  **A drawing is the only thing posing the machine while it runs**: any
  other press, handle gesture, host request, restore or reset LANDS it
  first and then acts, so two presses are two strokes, and starting one
  pauses the clock's transport where the machine declares a clock. The
  panel FOLLOWS the drawing rather than jumping to the end bank, through
  a narrow writer instead of a rebuild per frame. An instruction this
  build could not play — both forms or neither, no driver or several, a
  state, the clock, an undeclared id, a travel or duration that is not a
  finite number of the right kind — is **refused at load, by name**,
  mirroring what the producer refuses before a document exists, so every
  button a loaded document shows is one a maker may press. The posed
  `handle.trigger()` is now refused under a clocked document, pointing at
  `machine().trigger()`, rather than silently ramping a driver table
  nothing poses from. Measured on the Curta's own two builds in one
  browser session: the clocked build's per-frame pose — 41 bank values
  over a 39-commit machine — costs **9.20 ms** against the posed
  `fast_curta`'s **9.50 ms**, and the committed calculator acceptance
  draws **120 frames over 2.02 s (59.4 fps)** with a median per-frame
  pose of **0.40 ms**; a `trigger` costs what the same `move` costs
  within the bench's noise. The conformance corpus grew to **81 steps and
  917 recorded numbers over 30 machines** — the producer's `trigger`
  steps and `origin`/`end` on all 65 recorded requests — and every one
  replays bit for bit. Nothing of the clock's transport, the run, its
  worker, the posed `Ramp` or document versions 1–7 changed, and the
  document versions this build reads stay `1 … 8`. (OpenSpec change
  `play-the-instruction`, ADR-064.)

- **An elapsed clocked machine RUNS: the clock is an input a request
  moves, and API 18 says so.** solid-node's ADR-127 gave a clocked root a
  third time base: under `Time.elapsed()` the machine banks `time` in
  seconds, and ADR-128 §10 publishes it as `clocked.clock`. Cycle 5 banked
  that clock at zero, posed from it and refused the one gesture that would
  move it; this build MOVES it. A time request runs the path an ordinary
  request runs — every committing relation whose published `shapes` names
  the clock examined and no others, crossings solved, landings found by the
  same far-side walk, only rising steps firing, ties by identity of the
  landing float, reads pre-event, commits in path order, one pose at the
  end — because **an event on the clock is an event**. **Nothing stops a
  clock**: a declared range is a mechanical stop and nothing is in the way
  of the next second, so no declared stop ever clips a time request (proved
  on the corpus's own `Lift`, which declares a clock AND two compiled
  bounds, admitted whole where its very next driver request is clipped) —
  while a commit fired inside a time request that carries a coordinate out
  of range still refuses the whole request. **Time never reverses**: a
  negative travel, or a `to=` behind the banked instant, is refused by name
  naming both instants, in the producer's own position (after the by/to
  exclusivity refusal, before the clip); zero is admitted and moves
  nothing. A `bounds` entry whose chain, bound, level or `shapes` names the
  clock is now **refused at load**, mirroring a refusal the producer makes
  and the loader was silently wider than. **The conformance corpus closes**:
  all 30 machines, **76 of 76 steps and 722 of 722 recorded numbers**
  replayed bit for bit under `toBe` with `tolerance.float` read from the
  file, no departure and no deferral left, and the census now derived from
  the replay itself so a later build cannot narrow the suite quietly.
  **And a maker can watch one run.** Beside the clock's readout the chrome
  gains a transport: PLAY, which submits exactly one `move(clock, {by})`
  per rendered frame for the wall seconds elapsed times the playback speed
  — so every event inside that frame still fires exactly and in order —
  STEP, one request of a stated number of seconds, and the existing speed
  ladder, whose ×360 and ×3600 exist for this. There is no scrub and no
  reverse: the clock is one-way, and a slider that ignored half its travel
  would be worse than none. A long frame is capped at four frames' worth of
  machine time and the wall time beyond it is lost visibly, rather than
  firing a burst past the machine's own `max_crossings`; a refused frame
  pauses and reports once; pause holds the bank; reset returns the bank to
  its published defaults with the clock at zero and stops the transport,
  and so does a republish under `solid develop`. `handle.machine()` carries
  `clockPlaying()` and `setClockPlaying(playing)` beside the requests it
  already had, and every panel readout now follows the committed bank
  whoever moved it — a host driving the handle no longer leaves a stale
  instant on screen. A clocked document builds ONE chrome (the posed driver
  panel is no longer built behind the clocked one), and an integer state
  reads as the whole number it is. `$t` and the clock are independent and
  neither moves the other: an elapsed document that reads no `$t` gets no
  timeline at all. Measured on the framework's own `Regulator` pendulum,
  exported verbatim as a fixture and played in Chromium: a frame costs
  **0.3–0.4 ms** at ×1 and **1.0–1.8 ms** at ×3600, every number asserted
  under one 16 ms frame budget, and the whole corpus replays in 15.5 ms.
  Nothing of the run, its worker, its playback or versions 1–7 changed, and
  the document versions this build reads stay `1 … 8`. (OpenSpec change
  `run-the-clock`, ADR-063.)

- **A CLOCKED machine is executed: the viewer reads document version 8,
  and API 17 says so.** solid-node's ADR-125 gave a machine MEMORY and no
  cadence — a few retained values, a closed-form position between events,
  and a commit of those values at each event — ADR-126 gave it
  interlocks, and ADR-128 published the whole of it as a version 8
  document: a `states` table beside `drivers`, and a `clocked` object
  carrying the compiled machine. This viewer refused that document by
  name; it now loads it, refusing field by field what it cannot execute,
  and runs it. One gesture is one **request** — one declared input along
  a straight path from the bank — solved SYNCHRONOUSLY on the main
  thread, because a request is not a cadence: crossings solved (affine by
  a division, kinked at its own breakpoints), the landing found by the
  same far-side bit walk the run uses, only RISING steps firing, ties
  decided by IDENTITY of the landing float and never a window, reads
  pre-event, commits in path order, an `int` target rounded once half to
  EVEN, and one pose from the bank afterwards. A refused request leaves
  the bank, the tree and the pose exactly as they stood. **A declared
  stop CLIPS the request before a single event is located** and reports
  itself at the control that made the gesture — coordinate, side, bound,
  value and fraction — so a request an interlock holds is ADMITTED at
  zero travel rather than swallowed, and what the commits carried is
  judged again at the end. The chrome is a third one: a driver is a
  positional HANDLE with a slider where a range is declared, a state and
  a clock are follow-only READOUTS, declared instructions are listed and
  DISABLED (the framework publishes them under a clocked root with no
  runtime meaning), and there is no transport. `$t` animates such a
  document while its bank stands, and the headless capture — which used
  to refuse `--time` on any document of version 5 or above — now asks the
  two questions separately and photographs a clocked document at its
  initial bank. The producer's EXACT conformance corpus is replayed bit
  for bit with `tolerance.float` read from the file: all 30 machines
  load, 68 of the 76 steps and 652 of the 722 recorded numbers agree
  under `toBe`, three of its four recorded refusals are reproduced by
  kind and by name, and a census test derives `76 = 68 + 3 + 5` from the
  file so a regenerated corpus cannot narrow the suite. The 8 steps not
  replayed are the CLOCK's — three requests this build refuses by name
  and five standing downstream of them — and they are asserted as a
  departure rather than dropped. Measured on the Curta-shaped
  `Calculator` fixture in Chromium, a whole stroke over four digits costs
  **0.2–0.4 ms**, a clipped selector move 0.1–0.3 ms, against the
  operating Curta's running model at ≈42 ms per 1/240-second tick; every
  page number is asserted under one 16 ms frame budget. Nothing of the
  run, its worker or versions 1–7 changed, and the released document
  versions stay `1, 2, 3, 4`. (OpenSpec change `execute-the-commit`,
  ADR-062.)

- **A quantity built over `abs`, `min` or `max` is SOLVED at its own
  kinks instead of searched.** Such a quantity is piecewise affine —
  affine between the points where it changes which operand it returns —
  and `clamp`, `ramp` and `piecewise` are all built on it. The viewer now
  derives that shape FROM THE PUBLISHED EXPRESSION, which it already
  holds, and cuts the stretch at those breakpoints, solving each piece by
  one division: no document field, no document version, no API version
  and no knob, and a breakpoint is never recorded as a crossing. The
  derived shape agrees with every one of the 73 `affine` flags the
  conformance corpus publishes and every one of the 815 the operating
  Curta publishes, and a contract test keeps it so. The corpus's 2 018
  recorded floats, of which this engine reproduced 2 009 bit for bit and
  9 within the corpus tolerance, are now reproduced **bit for bit, all of
  them**; nothing else in the corpus's 360 ticks moved by one bit. On the
  committed `clearing` fixture — six self-read dials through a `clamp01`
  station window — a step fell from 32 004 to 2 724 subexpression
  evaluations and from 342 to 1 312 steps a second, while machines with
  no kink pay nothing to the unit, and the operating Curta's own step is
  unchanged in every evaluation and every committed float. (OpenSpec
  change `solve-at-the-kink`, ADR-061.)

- **The conformance corpus is refreshed to the producer's own
  `cut-at-the-kink` regeneration** (ADR-123: `abs`, `min` and `max` are
  KINKS, and a kinked quantity is solved at its own breakpoints rather
  than searched), byte for byte, and the width guard gains the producer's
  new required feature — a stop located strictly inside a step on a
  KINKED DETERMINER, a coordinate whose determining law carries no jump
  plan and whose published expression calls one of those continuous
  selections — mirroring its detection from the corpus's own documents
  and tick logs exactly as it already does for the self-read, the
  selection and the block. No engine behaviour changes: this viewer still
  SEARCHES a kinked stop rather than solving it, and the refreshed
  corpus's one such case replays inside the corpus's own tolerance,
  9.09e-14 from the producer's solved answer. (OpenSpec change
  `mirror-the-kink-guard`.)

- **A quantity followed along a step's path is evaluated as a PATH.** A
  search's samples, a bisection's rounds, a piece's two endpoints all read
  the SAME expression, and the run already knows, from the `delta` it
  built, which of that expression's names can have changed between them —
  yet every one of those points walked the whole graph over again. The
  part that reads no name the step moves is now computed once per piece
  and read back; only the moving cone is evaluated per point, through the
  same operators, the same context and the same node store `valueOf`
  already walks, so every float is the float the old walk gave, bit for
  bit — proved against the whole conformance corpus and against the
  operating Curta's own bank, crossings and stops, byte-identical over 100
  idle ticks, a crank turn, and 60 more. On that document — the largest
  running document this viewer executes, and the one the studio opens —
  an idle tick fell from ≈19 ms to ≈9.5 ms and a crank tick from ≈160 ms to
  ≈42 ms on this bench; a solved self-read, a searched self-read and a
  block tick each measured roughly 2-2.5× faster, and no small machine
  measured slower outside this bench's own run-to-run noise. No document
  field, no API version and no knob: the saving is structural.
  (OpenSpec change `walk-only-what-moves`, ADR-060.)

- **A source checkout answers from a bundle built from its own sources.**
  `dist/solid-widget.js` is this package's one published artifact and a
  build product of `widget/src/`, `package.json`, `build.mjs` and
  `tsconfig.json` — and until now nothing here ever compared the two. In a
  wheel they are the same instant by construction; in a checkout they are
  not, and a maker was told a correct version 7 document "declares document
  version 7, which this viewer does not render" by a bundle built the
  evening before the cycle that reads version 7 landed. The lookup was
  reporting `apiVersion: 16` and `documentVersions: [1..7]` from
  `package.json` while handing out the path of a bundle carrying
  `viewer API 15`. The four exits that hand the bundle out — the
  `solid_node.viewer` entry point and `describe`, the development server's
  `/_viewer` and `/_viewer/bundle.js` routes, the capture's staging, and
  packaging — now make it current first, comparing the newest build input
  against the bundle in integer nanoseconds and rebuilding when it is
  older. The development server checks **per request**, so editing the
  viewer and reloading the page serves what you just wrote. A rebuild
  **builds and never installs**: absent dependencies are reported with the
  `npm ci && npm run build` remedy, never installed, because `npm ci`
  through a worktree's symlinked `node_modules` has emptied a primary
  checkout's dependencies. What cannot be repaired is **refused** rather
  than served — a new `BundleStale`, shaped like `BundleMissing`: the
  entry point raises, `describe` exits non-zero with empty standard
  output, the server's routes answer unavailable, and the capture writes
  no image. A wheel is no longer cut from a stale bundle either.
  (OpenSpec change `keep-the-bundle-current`, ADR-059.)

- **The conformance corpus is refreshed to the producer's own
  `pin-the-block-order` regeneration**, byte for byte, and the width guard
  gains the producer's new required feature — an in-block gate crossing
  located strictly inside a step — mirroring its detection from the
  corpus's own documents and tick logs exactly as it already does for the
  self-read and the selection. The suite now proves directly, against
  this engine and not only through the guard, that a consumer running a
  block's members in the published LISTING order disagrees with the
  corpus, mirroring the producer's own `BlockOrderTest`. No engine
  behaviour changes: `execute-the-selection` already orders a block per
  piece, and the refreshed corpus replays green through it unchanged.
  (OpenSpec change `mirror-the-gate-guard`.)

- **The worker ORDERS A BLOCK PER PIECE of a tick.** solid-node's ADR-122
  lets a machine's dependencies be SELECTED by where one of its own parts
  stands. The Curta's carry levers belong to the FIXED frame and its
  number dials ride on the CARRIAGE, so the same lever is tripped by dial
  `s` and advances dial `s + 1`, where `s` is the carriage position the
  maker chose. At any one position the active dependencies are a chain
  and acyclic; their UNION over the working positions is CYCLIC, and the
  union is what the compiled program orders. The producer compiles such a
  union as a **block** — the nontrivial strongly connected components of
  the dependency graph over the edges' `needs` and `gives`, each
  contracted to one entry — and publishes it as a **version 7** document
  with **no new key**, in which the published order of a block's members
  is a **LISTING and not an execution order**. This viewer therefore
  re-derives the block from the published edges themselves, and each
  member's SELECTORS from the `level` expressions its plan publishes: a
  selector is a jump whose level reads nothing the block determines, and
  a source is SWITCHED when folding that jump to zero removes it from the
  law. Over one step the selectors' crossings are located first over the
  whole stretch, the stretch is cut there, and on each piece the branches
  read at the MIDPOINT are forced into every member's own plan while the
  members are ordered over what the run-time fold leaves active — with
  each in-block coordinate advanced between pieces, and the ABSOLUTE
  value the block advanced it to reported for any it landed. A shape the
  producer refuses at construction — a wiring or a formula on a cycle, a
  member driving a group, a member whose driven end is not a bank
  coordinate, a cycle no selection can break — is refused HERE, when the
  document loads, in the producer's own words; a piece a selection leaves
  genuinely cyclic refuses the step transactionally, and the step commits
  nothing. A program with no block pays one `kind` test per edge per step
  and nothing else. (OpenSpec change `execute-the-selection`, on top of
  solid-node's ADR-122.)

- **The Curta's own carriage mounts, shifts and carries in a browser.**
  The framework's own `CurtaCarriage` — four number dials on the
  carriage, three carry levers on the frame, the lift, and an interlock
  stated as a bound that READS the lift — is exported verbatim as a
  version 7 document and mounted in Chromium at the framework's own
  `0.02` s step. Lifted, shifted to position 1, dropped and cranked by
  36, its dials read `36, 36, 72, 72` and its first lever stands at
  exactly `1.0`; lifted, shifted again and dropped, **every coordinate
  but the carriage's own is BIT-IDENTICAL** to what it was; lifted,
  reset and dropped, the levers return and the dials hold; cranked
  again, each lever now acts on the wheel it FACES and the dials read
  `108` and `144`. With the carriage DOWN and a lever standing set the
  same shift retires BLOCKED with nothing admitted and nothing else
  moves, which is the interlock. A machine whose selection leaves a
  genuine cycle reports its refusal in the page and commits nothing.

- **A piece whose law does not move leaves its coordinate at the EXACT
  float it held.** The walk that integrates a self-read law took the
  driven coordinate's own path as `(own + S) − base`, which rounds
  whenever the skeleton's value is comparable to the coordinate's, so a
  step that moved nothing still shifted it by one ulp. It now takes the
  skeleton's CHANGE first, `own + (S − base)`, as the producer's own walk
  does — which is what makes "a selection change alone moves nothing" a
  bit-for-bit promise rather than an approximate one. A correction for
  every version 6 document too, and the conformance corpus is unchanged
  by it: the producer regenerated the corpus after the same fix.

- **The worker executes a law that READS THE COORDINATE IT DRIVES.**
  solid-node's ADR-121 gave a law the one thing every law it admitted
  before was forbidden: the coordinate a law determines may appear among
  the values it reads, and what it reads there is the value that
  coordinate RETAINS. The mechanism is the Curta's clearing rack — a ring
  carrying nine-tooth racks sweeps past the register dials, and a rack
  turns a dial only while its teeth reach it AND the dial is not already
  standing in its missing-tooth gap, which is what lets the ring go on
  sweeping past a finished dial while it still clears the dials beyond
  it. The producer publishes such a program as a **version 6** document
  and adds no key for it: the self-read is a law edge whose read set
  meets its own determined set, and this viewer recognises it from
  exactly that. Over one step such a law is integrated PIECE BY PIECE —
  the independent jump nodes partition the path as they always did,
  their branches read at the midpoints; inside each of their pieces the
  nodes that depend on the driven coordinate are walked, their branches
  read at the piece's LEFT END with that coordinate at its retained
  value; the piece is cut at the first surface any of them reaches
  strictly inside it; and the coordinate is then placed at the nearest
  representable value on the FAR SIDE of the surface, found by bisecting
  in ordinal float space. A step whose cut placed the coordinate commits
  that float rather than its starting value plus the increment — a ulp
  back toward the surface is the ENGAGED side of the gate — and a
  declared bound on the same coordinate in the same segment still wins,
  because a physical bound is a bound of the coordinate itself. A law
  that reads nothing of its own takes the path it always took, at the
  cost it always paid: one array-length test per edge per step and
  nothing else. (OpenSpec change `execute-the-self-read`, ADR-057, on
  top of solid-node's ADR-121.)

- **The Curta's own clearing interface mounts and clears six dials in a
  browser.** The framework's own `CurtaInterface` — six register dials in
  two rows of three, one clearing input, the originating project's
  measured rack starts, pitches and stations — is exported verbatim as a
  version 6 document and mounted in Chromium. One sweep of the clearing
  input leaves all six dials at exactly `359.5`, which is the number the
  framework's own suite asserts for the same machine; a second sweep
  completes its whole travel and moves no dial AT ALL, bit for bit; no
  stop is recorded and every crossing names a dial's own coordinate. Its
  station window is a `clamp01`, so every one of its self-read crossings
  is a searched one: it runs correctly at the viewer's default `1/240` s
  step and, on the development bench, at about 0.79× real time.

- **The conformance corpus is the producer's regenerated one** — 19
  scenarios over 16 machines, 356 ticks, including `Clearing` at two step
  sizes, `StoppedClearing`, and the two selection machines `ShiftedCarry`
  and `RangedBlock` — replayed here through the shipped engine and
  compared tick by tick. The width guard gains the producer's six new
  required features across the two cycles, so a narrower corpus copied in
  is loud here without anyone running the generator.

- **`documentVersions` becomes `[1, 2, 3, 4, 5, 6, 7]` and the declared
  API version rises to 16.** Executing a version 6 document, and then a
  version 7 one, is each a capability a host may require BEFORE it
  mounts, because unlike a `controls` table or a `markings` list neither
  is additive: a build at the previous version refuses such a document by
  name and renders nothing at all. `bundle.py`'s released-versions floor
  does not move — it is what a viewer that predates the declaration is
  entitled to be assumed to read.

- **A document that carries a compiled mechanical program is executed.**
  solid-node's version 5 document is a version 4 one plus a `program`
  object — the bank of coordinates with their rest values, the values the
  program computes and never stores, the edges in propagation order with
  their expressions, their affinity and their jump plans, the declared
  bounds, the reaching-inputs table and the five constants the algorithm
  is defined by — beside a tree whose pose expressions name **joint
  coordinates** rather than drivers. Under that document the carry law is
  no longer part of a drum's pose: the drum's rotation is one name, and
  what puts a number there is a **run**. The widget now takes the tick.
  Ten `Add one` on the Pascaline module's own published build leave its
  tens drum at 65.54°, where ten of them left it, and not where one
  would have. (OpenSpec change `run-in-the-worker`, ADR-045.)

- **The run executes off the rendering thread.** A TypeScript engine
  mirroring the framework's own `program.py` and `run.py` function for
  function runs in a Web Worker, bundled into the one published
  `solid-widget.js`. The render loop drives the cadence with one advance
  in flight: a page nobody is watching accumulates no unseen steps and
  resumes where it stands, a slow tick drops display frames and never
  mechanics, and a page whose policy forbids a blob worker runs the same
  engine on the rendering thread and says so on the handle. The step size
  is the viewer's own choice — `1/240` s by default, settable once at
  mount — and playback speed changes how many steps a wall second earns,
  never the step size.

- **The numbers are pinned against the producer's own corpus.** The
  framework's committed running corpus — thirteen scenarios over eleven
  machines, 260 steps, every jump primitive, a multi-source law, a
  blocked command, a rate, a state taken and restored — is replayed here
  through the shipped engine and compared step by step: exact for
  discrete state and within the run's own agreement window for floats. A
  disagreement is a bug in this viewer. (ADR-047.)

- **A committed bank poses the geometry through the evaluator that was
  already here**, with no second pose path: the bank's coordinate ids are
  names in the same scope as driver ids, only the parts that read a
  coordinate that moved are re-evaluated, and a flexible part's shape
  follows by the same rule. Two corrections came with it, and neither
  moves a number any correct document produced: a qualified identifier
  now resolves at **every** segment, so an id of three or more segments
  resolves to its value instead of to nothing — which had been silently
  breaking a three-segment driver id in every document version — and
  `sign` resolves by the producer's own definition, including at negative
  zero. (ADR-046.)

- **The declared API version rises to 8**, and `describe` reports
  `documentVersions` beside it — the document schema versions this build
  reads, from the same single declaration the bundle refuses by, so a
  producer can ask rather than infer. A version 7 document is refused by
  name and by list, which is the sentence every viewer released so far
  gives a version 5 one.

- **A running machine is driven on screen.** A document carrying a
  program gets its own chrome: per declared input, a follow-only readout
  of its committed position in design units, a nudge pair asking for a
  relative movement over a duration, and a hold-to-jog pair asking for a
  rate until the interaction ends; per declared instruction, one button,
  which submits the instruction whichever form it is declared in — a
  travel or a target — where the shipped button could only read a
  target. Along the bottom runs the transport: run, pause, step one step
  of the run, the speed to watch at, the elapsed simulation time, and
  reset. Every request reports at the control that made it: completed,
  blocked with the travel the machine actually admitted, refused with the
  run's own reason, or cancelled; a step the run refuses is reported
  across the panel and pauses it. Ten presses of `Add one` on the
  Pascaline module's published build, made **on screen**, leave its
  `units_entry` readout at ten digits and its tens drum at 65.54°.
  (OpenSpec change `drive-the-run-on-screen`, ADR-048.)

- **A running document has no slider and no timeline.** A slider writes a
  position into a coordinate, and under a run a coordinate carries
  history: writing one is the re-entry the running mode exists to
  remove. A jog is bounded by the interaction that started it — release,
  lost pointer capture, lost window focus, and a page that stops being
  displayed — and the amount and rate editors configure the next request
  rather than moving anything. A document of versions 1 to 4 keeps every
  pixel of the chrome it had: the same sliders, the same click-to-edit
  readouts, the same instruction buttons, the same animation bar.
  `driverControls: 'none'` suppresses the running chrome exactly as it
  suppresses the posed one, and `run: {nudge, jog}` sets what the
  controls ask for.

- **A rebuild keeps a live run only when it is the same machine.** The
  development page's targeted document update keeps the bank, the active
  commands, the step count and the elapsed clock when the republished
  program's identity and the run's step size are both unchanged, and
  otherwise discards the run, starts a fresh one at the new document's
  rest state and says which it did. A coordinate is never carried across
  because an identifier matched.

- **A document carrying a program is photographed at its rest state.** No
  step of the run is taken and the program's clock resolves to zero,
  which is the instant the rest state is defined at; a non-zero `--time`
  on such a document is refused by name before any browser starts, since
  a running document publishes no animation cycle. The capture now also
  mounts with the on-screen chrome suppressed, for a posed document and a
  running one alike: a panel over the canvas would be in the photograph.

- **The viewer publishes what it is showing, and tells a host when that
  moves.** A mount handle's `navigation()` reads the focused root and the
  explicitly hidden paths as one serializable snapshot; `onAssemblyChange()`
  subscribes to every accepted operation that publishes a tree or moves
  the focus or the visibility state — a host call, the widget's own
  breadcrumb, or a targeted update — exactly once per operation, whatever
  caused it. A host that used to mirror this by hand, and could be wrong
  about a focus change the widget made itself, now reads one state and
  one subscription instead. Nothing renders: no navigator ships in this
  release, and mounting one on this channel is the next viewer cycle.
  (OpenSpec change `observe-assembly-navigation`, ADR-049.)

- **The declared API version rises to 9**, for the navigation state and
  its subscription — a capability a host may require, added to the
  handle.

- **The bundle carries the assembly navigator itself.**
  `SolidNodeWidget.mountNavigator(target, viewer, options?)` mounts a
  React-free, plain-DOM tree over the state and subscription the previous
  entry publishes: an accessible tree (roles, one tab stop, a roving
  keyboard position), every row's label, depth and effective colour, the
  focused viewer root and the hidden subtrees marked separately, and a
  node invisible only because an ancestor is hidden distinguished from
  one hidden in its own right — its visibility control still reports its
  own setting, and its row says which ancestor hides it. It holds no copy
  of the viewer's state: the focused root and the hidden paths come only
  from the handle, re-read from every notification, so two navigators
  mounted on one handle never disagree about what the viewer shows, even
  while each keeps its own expansion and keyboard position. A maker
  moves the viewer from it — focus a subtree, restore the document root,
  hide or show a part — through the same operations a host calls, by
  pointer or by the keyboard contract (`Up`/`Down`/`Left`/`Right` to
  move, `Enter` to focus, `Space` to toggle visibility). One
  identifiable stylesheet is injected per document, however many
  navigators mount, behind a stable `solid-nav-*` class contract and CSS
  custom properties a host overrides to theme it completely — the escape
  hatch, `styles: 'none'`, skips the injection for a host under a
  Content-Security-Policy that forbids inline style blocks. No new file
  is published: the component and its stylesheet live inside
  `solid-widget.js`, and `solid export` and the Sphinx directive copy the
  same `index.html` + `solid-widget.js` as before. No layout ships in
  this release — no sidebar, no composition with the viewer or the
  export page — and the studio's own `AssemblyPanel` is untouched; both
  are the next cycles. (OpenSpec change `mount-the-navigator`, ADR-050.)

- **The declared API version rises to 10**, for the mountable navigator
  itself — a capability a host may require, on top of the navigation
  state version 9 published.

- **The bundle composes the navigator, the sidebar and the viewer into
  one inspector layout.** `SolidNodeWidget.mountInspector(target,
  sourceUrl, options?)` builds a collapsible assembly sidebar and the
  viewer with its own chrome inside one host element, gives the viewer a
  pane of its own so its teardown cannot remove the sidebar, and
  resolves to a handle that exposes the whole viewer handle and the
  whole navigator handle. A labelled, keyboard-operable toggle stays in
  the DOM in both states, so opening and closing the sidebar never loses
  keyboard focus; collapsing removes the sidebar from layout rather than
  overlaying it, and the viewer's own `ResizeObserver` — already
  installed by `mount()` — resizes the canvas with no code of this
  layout's own. The sidebar remembers nothing across a reload: no
  storage, no cookie, no URL rewriting. A refused mount leaves the
  target empty and rethrows the viewer's own error, rather than
  presenting a sidebar around a viewer that never existed. One
  identifiable stylesheet, a `solid-inspector-*` class contract and
  `--solid-inspector-*` custom properties follow the navigator's own
  pattern, and `styles: 'none'` also defaults the navigator's own
  stylesheet off. No new file is published.

- **The standalone export page selects the inspector.**
  `widget/index.html` gains `data-solid-layout="inspector"` beside its
  existing `data-solid-widget`, with `?layout=`/`?sidebar=` query-string
  twins that override it. **A container carrying no layout selection
  mounts the plain viewer**, exactly as it did before this capability
  existed, so every hand-written page and every already-published export
  is untouched; an unrecognised layout value is written into the
  container by name, never silently ignored. The page this package ships
  selects the inspector, collapsed.

- **The development page becomes a static file this package carries,
  and React leaves the package.** `solid_node_viewer/widget/develop.html`
  is served by `solid-node-viewer serve` at `/`: it checks the bundle's
  own availability, loads it, and calls the published
  `SolidNodeWidget.mountDevelopment(target, options?)`, which mounts the
  **inspector** on the published build with inline animation and
  autoplay and the sidebar **open** — collapsible by `?sidebar=` for a
  link that wants the model alone — names the tab from the model, and
  runs the reload client. The reload client itself is ported into the
  bundle unchanged in behaviour (the same `/ws/reload` socket, the same
  2 s retry and two-attempt grace, the same banner id, class and text),
  its eight jest tests becoming nine vitest tests (one new, for the
  injected stylesheet). Partial reload is
  untouched: every reload still ends in the handle's own
  `manifestChanged()`. **One deliberate behaviour change:** a build error
  is now shown in an error pane over a viewer that stays mounted, rather
  than replacing it — a failed save no longer discards the camera or a
  live run the next save would fix. `solid_node_viewer/app/` — Create
  React App, React, `react-scripts`, the 688 kB lockfile, the second
  frontend build, the httpx proxy and the second dev server — is deleted
  whole; a wheel now needs one npm build. `serve` goes on accepting
  `--dev`, `--start-frontend` and `--frontend-port` as no-ops, logging
  one notice per flag given, because a released solid-node's `solid
  develop --web-dev` passes `--start-frontend` and must keep working.
  (OpenSpec change `ship-the-inspector-layout`, ADR-051, ADR-052;
  supersedes ADR-013, amends ADR-036.)

- **The declared API version rises to 11**, for the inspector layout and
  the development page's own mount built on it — capabilities a host may
  require, on top of the mountable navigator version 10 published.

- **A maker drives the machine by touching it.** A version 5 document
  may carry a `controls` table beside `instructions` — the framework's
  own `Button(part, instruction)` and `Turn(part, input)` declarations,
  published with the part and the joint as node-name paths, the
  coordinate that joint poses, that joint's axis and origin in its own
  frame, and, for a turn, `per_unit`: the coordinate units the part
  moves per design unit the input travels, measured off the compiled
  program at the rest bank. The viewer reads it and binds a pick to it.
  A part the table names takes a pointer cursor, a light highlight and
  its controls' display names on hover; every other part orbits the
  camera exactly as before, a part the assembly navigation has hidden or
  focused out is not touchable, and a part in front of one is not
  reached through it. (OpenSpec change `drive-the-run-by-touch`,
  consuming solid-node's ADR-112; this is the cycle ADR-048 promised by
  name.)

- **A press submits the declared instruction; a drag turns the part by
  whole quanta.** A pointer pressed and released without travelling more
  than four pixels issues `run().trigger(instruction)` — the same call
  the panel's button makes, indistinguishable to the run, to its
  listeners and to a readback. Past that threshold it is a drag,
  measured as the angle swept about the joint's world line, which the
  viewer computes from that one node's world matrix and which does not
  move under the drag that is moving the part. Each time the sweep
  crosses one **quantum** — the input's current nudge amount times the
  published ratio, one digit = 36° on a Pascaline dial — exactly one
  `move(input, {by, duration})` is issued, and **at most one is ever in
  flight**, because the run gives an input one owner at a time. What a
  gesture owes is recomputed from where the pointer stands rather than
  queued, so a sweep forward and back nets out instead of being paid for
  twice.

- **The part follows commits, never the pointer.** Nothing in either
  gesture writes a coordinate, sets a matrix or poses anything: the only
  effect a drag has on the scene is through the run's committed frames.
  The pointer may run ahead while the machine catches up, and a machine
  that refuses to move does not move. A request that does not complete
  leaves the point the next quantum is measured from exactly where it
  was, so a drag against a declared stop reports blocked with the travel
  the machine actually admitted, leaves no remainder to be executed
  later, and repeats nothing while the gesture is held there. The
  gesture ends on all five sides a jog does — release, cancelled
  pointer, lost pointer capture, lost window focus, and a page that
  stops being displayed — and on every one of them the camera becomes
  movable again; a `move` already in flight is left to retire and report
  rather than cancelled.

- **Every outcome is reported twice through one path**: a transient
  `role="status"` label beside the pointer and the panel's own control
  for that instruction or input, in the same words, so a press that is
  blocked says exactly what a nudge that is blocked says.

- **A `controls` table the viewer cannot resolve is refused by name**,
  when the document loads and before anything is rendered — the surface
  an undeclared driver id, an unreadable bindings table and an
  inexecutable program already stand on. Refused: a table or an entry
  that is not of the published shape; a kind that is neither `button`
  nor `turn`; a part or joint that does not resolve to exactly one node
  of the document's own tree, or a joint that is neither the part nor
  one of its ancestors; an instruction, input or coordinate absent from
  the table it must belong to, each naming what the document does
  declare; a `per_unit` that is missing, not finite or zero; an axis or
  origin that is not three finite numbers, or an axis of no direction; a
  joint whose own operations do not begin with that coordinate's
  rotation, optionally preceded by translations — the reading the
  gesture's geometry depends on, and which accepts both shapes the
  producer publishes, including the off-centre `Revolute(at=...)` that
  `origin` exists for; two controls of one kind on one part; and a
  `controls` table on a document that carries no program. A document
  carrying no table loads, poses, runs and is driven exactly as it did
  before.

- **`controls()` on the handle, and `partControls` at mount.**
  `controls()` lists the declared controls with each part's current
  on-screen rectangle and a point at which a press actually reaches it —
  found by casting, because the centre of a dial's rectangle is its axle
  — both in viewport CSS pixels, both `null` for a part that is hidden,
  off screen or reached nowhere, and `[]` for a document declaring none.
  `partControls: 'inline' | 'none'` chooses whether the parts are
  touchable, **independently of `driverControls`**, because a host that
  builds its own instrument panel still wants the dial pressable. What
  either switch gates is pixels and pointers, never an interface: the
  listing answers and the whole run API is there either way. The
  headless capture passes `partControls: 'none'`, and publishes no
  `controls` table at all.

- **The declared API version rises to 12**, for part controls — a
  capability a host presenting a machine a maker touches may require,
  on top of the inspector layout version 11 published. The document
  schema versions this build reads do not move: `controls` is additive
  within version 5.

- **Not in this: no `Slide`** — a prismatic drag — because the framework
  proposes none; **no dialling by position**, the historical Pascaline's
  stylus-and-stop gesture, which belongs to the model and not to the
  viewer; **no keyboard gesture**; and no stream of the crossings and
  stops a drag passes through, which is a different feature from the
  report a gesture needs.

- **A declared bound may read other coordinates, and the worker executes
  it.** solid-node's ADR-113 widened a joint's range bound from a number
  or an expression over the bounded coordinate's own value to one that
  READS OTHER COORDINATES. Under a running root such a bound is a
  CONSTRAINT: the bounded coordinate frozen at the step's committed
  value, every coordinate it reads taken along the step's path by one
  pass over that bound's sub-program, examined only when something it
  depends on moves, located by sampling INSIDE the stretch rather than at
  its ends, and stopping every input that carries the level outward — the
  inputs moving what it READS included, so a dependency never overruns a
  standing coordinate. The viewer derives what it needs from what the
  document already publishes: the bound's reads are its expression's free
  names CLOSED OVER the bindings table, its sub-program is a filter of
  the published edges and its candidates a union over the published
  reaching-input table. A bound over the bounded coordinate alone keeps
  its meaning, its code path and its cost exactly. (ADR-054, consuming
  solid-node ADR-113.)

- **The pin tumbler lock's own published document mounts and runs in a
  browser.** `projects/Locks/Pin_tumbler_lock`'s build was refused by
  name until this — its plug's bound reaches five pin lifts only through
  the document's bindings table, and its key's bound names the plug
  directly. Driven by its own declared instructions, the plug turns its
  whole 90° with the key seated, the key is captured while the plug
  stands turned, and the plug will not turn at all with the key
  withdrawn.

- **The conformance corpus is the producer's regenerated one**: 14
  scenarios over 12 machines, 276 steps, with the new `Captured` machine
  exercising a bound that reads another coordinate and a stop reached by
  the motion of what a bound reads. The suite's own width guard requires
  both, so a narrower corpus copied in is refused here.

- **No version moves.** `documentVersions` stays `[1, 2, 3, 4, 5]`, the
  shape of a span is unchanged, and no public JS surface moves, so the
  declared widget API version stays at 12.

- **The viewer draws what a part carries, so a calculator can be read.**
  A Curta's answer is the angular position of ten printed number rolls,
  and a Pascaline's is the digit each drum shows through its window. Both
  were modelled, driven and run here and both were unreadable, because
  the digits were not on the parts. solid-node's `carry-markings-on-a-part`
  (ADR-120) closed the producer's half: a rigid part declares what it
  **carries** on its surface without declaring a solid, the build writes
  one surface-mesh artifact per marking, and the document publishes it as
  a `markings` entry with its own name, model, `#RRGGBB` colour and
  `mtime`. This draws it. (OpenSpec change `draw-what-a-part-carries`,
  ADR-056.)

- **A decal is a mesh, not a texture.** The artifact is a binary STL like
  any other, loaded through the path a node's own model already takes and
  drawn inside that node's own group. Rasterising the artwork and
  UV-mapping it is the better answer eventually, and needs UV coordinates
  neither the producer nor this viewer has; the decal mesh reuses the
  whole existing rigid path for nothing. Membership in the part's group
  is the whole trick: the part's local matrix is the decal's parent
  matrix, so a pose, an animation instant, a run's committed bank, a
  focus, a hide and a touchable dial's highlight all carry the decal with
  no code of their own — which is exactly why the producer publishes no
  placement and the viewer computes none.

- **The bias that draws a decal over its surface is the viewer's**, and
  says nothing about where the part's surface is. The artifact carries no
  offset by the producer's own design, so the viewer lifts each decal
  0.15 mm along the sheet's own averaged normals — 1.5× the framework's
  default tessellation tolerance, the bound an interpenetration cannot
  exceed — and puts a minimum polygon offset under it for the case a
  camera is zoomed far enough out that 0.15 mm falls below one
  depth-buffer step. The sheet is welded before it is lifted: an STL
  arrives non-indexed, and lifting each facet's private corners along
  their own face normals tears it open along every internal edge.

- **A marking is not a part.** No navigator row, no node in a host's
  assembly readback, no focus or visibility target of its own, and in no
  inventory: a host reading a marked document is given exactly what the
  same document without its markings gives it. The camera's fit box is
  the one place a decal counts, deliberately — a decal may lie outside
  its part's silhouette, and framing the model with its marking cut off
  would be the opposite of the point.

- **A decal reloads on its own currency.** A marking artifact carries its
  own `mtime`, which is the whole reason the producer split it from the
  part's: editing artwork refetches the decal and leaves the part's mesh
  on screen, rebuilding the part refetches the part and leaves the decals
  alone, a marking dropped from the list is removed and disposed while
  the rest stand, and a marking whose colour alone moved has its material
  replaced with no refetch.

- **A `markings` list this viewer cannot read is refused by name** —
  naming the document, the node and the marking, before anything is
  rendered, on the surface an unreadable bindings table, an inexecutable
  program and an unresolvable controls table already stand on. A viewer
  that read nine digits and silently dropped the tenth would show a false
  register.

- **The declared API version rises to 14**, because drawing a document's
  markings is a capability a host may require: a studio that means to
  show a readable Curta wants to know, before it mounts, whether this
  bundle draws the digits or shows a blank drum. `documentVersions` stays
  `[1, 2, 3, 4, 5]` — `markings` is additive and gated on no document
  version, and the framework's own marked fixture declares version 2.

## 0.1.0 — unreleased

The viewer leaves the solid-node framework and becomes this package.

- **Calibration controls accept exact values and complete timelines.** A
  bounded driver keeps its slider and its original passive numeric readout;
  clicking that readout temporarily opens a clean text editor without native
  spinner arrows. Exact design-unit values can lie outside the slider's
  declared travel; the slider pins honestly while the entered machine state
  survives.
  Animation sliders now count both `0` and `1` among the document's declared
  frame positions, so a twelve-hour loop can be scrubbed all the way to its
  `12:00:00` readout instead of stopping one sample short. This corrects the
  existing on-screen controls without changing the host API. (OpenSpec changes
  `include-timeline-endpoint` and `restore-click-to-edit-readouts`.)

- **A machine whose document shrank by 981× still opens, poses and
  plays.** `share-expression-subtrees` resolved a repeated subexpression
  once per frame, wherever it occurred — but the redundancy was still in
  the *document*: 3DPrintedClocks' grasshopper escapement published 116
  operation expressions built from 30 distinct strings, about seven
  million written subexpressions over 263 distinct ones, 31.6 MB in all.
  The producer now writes each subexpression that repeats exactly once,
  as a named entry in an ordered `bindings` table, and references it by
  bare name everywhere it occurred — the same grasshopper document falls
  from 31,638,555 bytes to 32,227, and this viewer now reads it
  (document version 4). A binding name resolves wherever it is used —
  an operation's expression, a flexible leaf's `params`, or another
  binding — to that entry's value under the same `$t` and driver values,
  and resolves as a binding *before* it is ever judged a driver id: a
  document may name every one of its bindings with an empty `drivers`
  table, and it still loads. Dependence flows *through* a binding
  transitively: an operation whose whole expression is a binding name
  resolving through the table to `$t` is time-dependent exactly as if
  it had been written out in full, gets re-evaluated on time change, and
  makes its document animated — the grasshopper document's own shape,
  where not one of its 116 expressions contains `$t` as text, yet 22 of
  them move the clock. A binding a driver reaches is re-evaluated when
  that driver moves and not otherwise, through as many entries as the
  chain runs, and a republish that changes only what a binding reads —
  an operation whose text stays exactly `_b3` while `_b3`'s own
  expression changes from `$t` to a driver, or back — is followed: the
  document's timeline appears or disappears with it. A table this viewer
  cannot resolve is refused when the document is loaded, naming the
  entry: a malformed array or entry, a duplicate name, an entry naming
  itself or a later entry, a name colliding with a declared driver id,
  or a name reached from anywhere in the document that is neither `$t`,
  nor an entry, nor a declared driver id. No number moves: reading a
  document's expressions through its table resolves to exactly what the
  same expressions resolve to with every reference written out, proven
  bit-identical (`Object.is`) against the flat 31.6 MB document at three
  points in its cycle — the two are the same arithmetic, differently
  written. The committed cross-runtime parity fixture is replaced by the
  framework's regenerated one (451 cases, the 421 already pinned
  unmoved, plus 30 new naming its own 4-entry table), so the corpus now
  pins the table's semantics and not only the evaluator's. The viewer
  API rises to 7: reading a version-4 document is a capability a host
  may require, and there is no other number a host can check before
  mounting one. (OpenSpec change `read-expression-bindings`; ADR-044,
  extending `share-expression-subtrees`'s ADR-043; consumes solid-node's
  `expression-bindings`, ADR-080.)

- **A document that repeats itself now animates.** A producer that builds
  an expression by string concatenation — solid2's `OpenSCADConstant` —
  pastes a reused value's full text again on every reuse, and a machine
  whose motion nests those reuses can publish an expression corpus far
  larger than its geometry: 3DPrintedClocks' `wall_clock_53_grasshopper`
  carries 31.6 MB of expressions, 4.28 million parsed nodes, over just
  293 *distinct* subexpressions. The widget no longer walks a parse tree
  on every frame; it interns each parsed expression once into a shared,
  hash-consed table — a repeated subexpression, however many operations
  or however many times one expression repeats it, is resolved once per
  animation frame — and drops the parse tree the moment it is interned.
  Measured on that document: 6,247,876 parsed-node visits per animated
  frame fall to 255 node resolutions; sixty animated frames fall from
  roughly 30 seconds to 29 milliseconds; the parse trees this viewer
  used to retain for the life of the page, 723 MB, fall to a table of a
  few hundred interned nodes. Loading grows by about 16% (an
  interning walk on top of parsing, ~8.9 s against ~7.65 s for this
  document) in exchange for that per-frame win. The numbers themselves
  do not move: every evaluator, tree, flexible-part and cross-runtime
  parity test in the suite passes unedited against the shipped module,
  and OpenSCAD semantics — degree trig, `^` as exponentiation with the
  unary-minus rule, `mod`, `ln`, `log(base, value)` — carry onto the
  shared table unchanged. An expression form the shared evaluation
  cannot support — an inline function, which nothing the producer emits
  carries — is refused when the document is loaded rather than met
  inside a frame. The viewer API stays at 6: nothing on the mount
  options or the handle changes, and the resolution/table-size counts
  this change adds are a widget-source export for its own tests, not a
  capability a host can require. (OpenSpec change
  `share-expression-subtrees`; ADR-043.)

- **Real-time playback.** A document whose `animation` object carries
  `loop` — the seconds of machine time one turn of `$t` covers, which
  solid-node publishes when a root declares `time = Time(loop=...)` —
  plays that loop at real time by default: one turn takes `loop / speed`
  wall-clock seconds, with `speed` defaulting to 1. The animation bar
  gains a speed control over a fixed ladder (×0.1 to ×3600) and a readout
  of the machine time at the slider position (`h:mm:ss` for long loops,
  seconds for short ones). The host sets the initial speed through the
  `speed` mount option and reads or changes it through `speed()` and
  `setSpeed()` on the handle. A document without `loop` plays `frames /
  fps` exactly as before, with the bar it always had. The viewer API rises
  to 6, because a host may now require the speed capability. (OpenSpec
  change `real-time-playback`, paired with solid-node's
  `declared-time-base`.)

- **A large model is photographed at last.** `solid-node-viewer capture`
  clips a page screenshot to the canvas instead of photographing the canvas
  element. Playwright caps an element screenshot's wait for a stable box at
  thirty seconds however long a timeout it is given, so a model that takes
  longer than that to settle — a vendor assembly of dozens of pieces on
  software rendering — never produced a picture at all. The clipped page
  screenshot honours its own, generous timeout.

- **Extracted.** The widget, the development app, the development server
  and the headless capture that shipped inside solid-node up to 0.6.0 move
  here with their history. Nothing a browser sees has changed: the bundle
  is still `solid-widget.js`, it still auto-mounts `data-solid-widget`
  containers, still exposes `SolidNodeWidget.mount()`, and still reads
  document versions 1, 2 and 3 (viewer API 5 at extraction; see
  real-time playback above for 6).
- **Relicensed** under AGPL-3.0-only. The framework stays Apache-2.0 and
  installs this package as its optional `viewer` extra.
- **A process boundary** toward the framework. solid-node locates the
  installed viewer through the `solid_node.viewer` entry point and runs
  the new `solid-node-viewer` console script for everything else:
  `describe` prints the bundle path and API version, `serve --build-dir`
  is the development server `solid develop` launches, and `capture` is
  the headless photograph `solid snapshot --renderer web` requests on a
  staged document. Neither package imports the other.
- **Playwright** moved with the capture: it is the `snapshot` extra of
  this package now, where solid-node's `web-snapshot` extra points.
- **Test fixtures are committed exports** rather than models built at test
  time, so the suite depends on nothing of the framework.
