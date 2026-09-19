## Why

Three cycles made a CLOCKED machine sayable — a bank of drivers and states
(`declare-the-state`, ADR-125), a declared range that STOPS a request on its
path (`a-bound-stops-the-request`, ADR-126), and a clock that is a banked
value with events on it (`time-without-running`, ADR-127). All three end on
the same sentence: **a clocked model cannot be PUBLISHED or VIEWED.**
`serializer._refuse_a_clocked_model` refuses one by name in `document_body`,
the one function every document producer passes through
(`solid_node/core/serializer.py:658-695`, called at line 719), and ADR-125
records the gap as owned by this cycle
(`workflow/warts.md:3056-3059`, `3197-3202`).

**The originating project is worth nothing to its pilot until this lifts.**
`projects/Calculators/Curta-Type-I-3x` (branch `direct-operation`, HEAD
`9fb725f`; the clocked spike is its worktree `WTs/clocked-spike`, recorded in
`simulation/docs/clocked-spike-2026-09-16.md`) has one machine modelled three
ways. `fast_curta` is closed-form and fast and does not OPERATE. `operating_curta`
operates and costs about 0.73 s per 0.1 s Python tick and about 40 ms per crank
tick in the browser. The clocked model reproduces the operating model's
registers at every stroke end of every in-booklet scenario, its poses to
0.000000 digits, and one revolution 35 times faster — **in Python only.** A
Curta the maker cannot crank in a browser is a measurement, not a machine.

The refusal is also the honest shape of ADR-110's version ladder: a clocked
tree's pose expressions ALREADY read its states as free names — verified on
this worktree, where `tests/clocked_project/register.py`'s three wheels
serialize as `(36.0 * w0.digit)`, `(36.0 * w1.digit)`, `(36.0 * w2.digit)`
— and a version 7 consumer has nothing to bind them to. So the document is
missing, not the model.

## What Changes

- **A clocked root publishes a version 8 document, and the version is NOT
  additive.** A tree in which anything declares a `State` publishes
  `version: 8`, whatever its tree content — a property of the ROOT'S
  DECLARATION exactly as version 5 is, because a clocked machine with one
  state and no flexible leaf is still a machine a version 7 consumer would
  animate wrongly. A consumer that cannot read version 8 REFUSES it by name.
  A tree that declares no `State` is untouched, byte for byte.
- **The gate is not deleted; it is re-aimed.** `document_body` goes on asking
  the one structural question it asks today, and refuses a clocked tree
  published WITHOUT its compiled machine — a producer error, not a model
  error — so no producer can reach a document by a route the check does not
  cover, which is why ADR-125 put the gate there in the first place.
- **A top-level `states` table beside `drivers`**, keyed by qualified id,
  carrying each state's `default`, `range`, `unit`, `dtype` and `scale` under
  the drivers table's own rules. Every declared driver stays a HANDLE; a
  state is never one, and the tables are what say so.
- **A top-level `clocked` object**, on `program`'s pattern — what COMPILE
  TIME decided and nothing a request computes: the clock's name (or `null`),
  the free name a bound reads its own coordinate under, the COMMITS (sources,
  targets, the `at` jump node with its level, the law expressions, and the
  structural shape of the level in each input that can move it), the BOUNDS
  (each compiled constraint's chain, bound, jump plan and per-input shapes),
  the compiled identity, and the two limits the shared locator is defined by.
  Every expression travels as a native graph compiled by `bind_document`
  together with the tree's, so a subexpression a law shares with the geometry
  is published ONCE and nothing carries producer-local sharing syntax.
- **The bank is the two tables and the clock, and nothing repeats it.** A
  clocked bank holds no joint coordinate, so there is nothing a consumer
  cannot compute from what the document already publishes; the `clocked`
  object therefore carries no `coordinates` table, which is the one place
  this design departs from `program`'s shape and it departs for a stated
  reason.
- **Under `Time.elapsed()` the document carries the free name `time`**, not
  `$t`, wherever the model reads the clock — version 5's rule, applied to the
  base it was written for — and publishes it as `clocked.clock`. Under a
  clocked root declaring NO base, `$t` goes on meaning exactly what it means
  in every version 2 document: the `animation` object's own 0..1 timeline,
  with the bank standing.
- **A cross-runtime conformance corpus, and it is EXACT.**
  `tools/generate_clocked_corpus.py` writes `tests/clocked-corpus.json` from
  the framework's own clocked executor and `tests/test_clocked_corpus.py`
  replays it. A clocked model's determinism claim is STRONGER than a run's —
  every event is solved, there is no `dt`, and ties are decided by identity of
  a float — so agreement is bit for bit and not within a window, which is the
  one substantive difference from the running corpus. The claim is stated
  operation by operation rather than assumed, and what it excludes — a
  transcendental or a power, neither correctly rounded — the generator
  REFUSES, as it refuses a corpus missing any listed feature.
- **A published commit law says what the EXECUTOR computed, not what the text
  spells.** The clocked executor calls the project's Python callable with the
  bank's numbers, and Python's remainder takes the sign of the divisor while
  the document's `%` — in both runtimes — takes the sign of the dividend. A
  published law therefore carries the floored form, composed from the
  document's own operators, and an integer state's rounding at a commit is
  published as the rule it is: the nearest whole native unit, an exact half to
  the EVEN one. A chain, a bound and a level keep the document's `%`, because
  the framework evaluates THOSE through the graph. That the same Python text
  means two things inside the framework is a wart this cycle records rather
  than fixes.
- **Every declared instruction travels**, in the version 5 shape, relative ones
  included, and this version gives a published instruction NO execution
  meaning. An instruction naming a state reaches no document at all: the
  compile refuses it before one exists.
- **A Curta-shaped fixture**, `tests/clocked_project/calculator.py`: several
  wheels of one class, two writers per digit (a stroke end and a clearing
  reach), a selector wired through an intermediate PORT, an anti-reversal
  ratchet and an off-rest freeze. The corpus's interesting cases are
  interactions, and no existing fixture carries all of them at once.
- **The producers.** `solid build`, `solid develop` and `solid export` publish
  version 8 and WARN that the installed viewer cannot read it, through the
  channel that already exists. `solid snapshot --renderer web` REFUSES by
  name before the browser starts, through the same channel — and the
  framework needs no new way to detect it: the `solid_node.viewer` entry
  point's `describe` report already carries `documentVersions`
  (`solid_node/viewers/bundle.py:101-136`), and 8 is simply not in it until
  the viewer's own cycle adds it. `solid snapshot --renderer openscad`,
  `render`, `assemble`, `build_stls` and `solid test` are untouched.
- **Every refusal this cycle does not own is kept**, each verified rather than
  assumed: a `State` under `Time(loop=)` or `Time.running()`; a control under
  a clocked root, refused in the publication walk and again at `Sim`
  construction; a state as an `Instruction` target; and `program` never
  appearing beside `clocked`, a running root being unable to declare a state.

## Capabilities

### New Capabilities

None. The change gives an existing document schema one more version and one
more object, and gives an existing conformance pattern a second corpus.

### Modified Capabilities

- `export`: ONE REMOVED requirement, "A clocked model is refused publication",
  which this cycle replaces; and SIX ADDED — "A clocked root's document
  publishes its compiled machine" (the version, the object, what it carries,
  why each key is there, and what a version 8 `instructions` table holds), "A
  clocked document publishes its states beside its drivers" (the second table
  and the handle rule), "A published commit says what it reads, writes and
  fires on" (including the remainder a published law carries and the rounding
  an integer state takes), "A published bound says where a clocked request
  stops", "A clocked document's clock and animation variable" (`$t` under a
  clocked root, and `time` under the elapsed base), and "The two runtimes
  share a clocked conformance corpus" (the generator, what the exactness claim
  rests on, the feature inventory and the replay).
- `web-snapshot`: ONE MODIFIED requirement, "A document the installed viewer
  cannot read is refused before the browser starts", whose scenarios name
  version 5 and which must name the clocked case it now also covers.

## Impact

- `solid_node/core/serializer.py`: `CLOCKED_DOCUMENT_VERSION = 8`;
  `compiled_clocked(node)` beside `compiled_program`; `clocked_block`;
  `states_table`; `document_version`'s eighth rung; `bind_document`'s clocked
  slots; `symbolic_document`'s clocked branch (the early return, the elapsed
  clock binding); `_refuse_a_clocked_model` re-aimed at the producer.
- `solid_node/simulation/clocked.py`: `clocked_of(root)` on `program_of`'s
  shape; `CompiledClocked.published(initial)`; `Committing` retaining the law
  graphs `_checked_law` today checks and discards, and its per-input shapes;
  the desugaring of `%` in a published law graph to the floored remainder the
  callable computes; `Bounded` publishing its chain, bound, plan and shapes;
  the compiled identity.
- `solid_node/simulation/program.py`: nothing but the reuse of
  `_published_plan`, `_renamed`, `_placeholder_prefix`, `_snapshots` and
  `_restore` — no running behaviour changes, asserted by diff.
- `solid_node/core/builder.py`, `solid_node/core/export.py`,
  `solid_node/viewers/browser.py`: each calls `compiled_clocked` beside
  `compiled_program` and passes the block to `document_body`.
- `tools/generate_clocked_corpus.py` (new), `tests/clocked-corpus.json`
  (new), `tests/test_clocked_corpus.py` (new),
  `tests/clocked_project/calculator.py` (new),
  `tests/test_clocked_document.py` (new); added tests in
  `tests/test_viewer_bundle.py`, `tests/test_browser_renderer.py`,
  `tests/test_build_publication.py`, `tests/test_export.py`.
- `docs/scenarios.rst`, `docs/animation.rst`, `HISTORY.rst`.
- One ADR, candidate **ADR-128** (NODE), extracted after implementation.

### Non-goals

Each is named in `design.md` with its reason and the shape a later cycle takes.

- **The viewer's execution of a version 8 document** (cycle 5) and **the
  browser's clock and clip** (cycle 6), both in `solid-node-viewer`'s own
  repository. Nothing in this cycle touches that repository.
- **Any change to document versions 5, 6 and 7, to the running corpus, or to
  `Time.running()`.** `tests/running-corpus.json` and every running fixture
  are byte-for-byte untouched, asserted rather than intended.
- **An `Instruction` or a control under a clocked root.** Both stay as they
  are today, and the design records what "as they are today" actually is,
  because it is not what this cycle's brief assumed.
- **The Curta project's own migration** to the published document, and the
  shop's hub preview.
- **A `State` under `Time.running()`**, still defined and not implemented.
- **A clip in time and a chain that follows the clock** — ADR-127's own single
  open item, untouched here.
- **Reconciling the framework's two meanings of `%`.** This cycle makes the
  published commit law agree with the executor and records the rest as warts:
  the same law text means floored under a clocked root and `fmod` under a
  running one, and a `drives(law=)` law taking `%` of a negative already poses
  one way in Python and publishes another in every version from 2 upward.
  Fixing either moves versions 5, 6 and 7.
