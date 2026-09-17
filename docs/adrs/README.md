# Architecture Decision Records

This directory is solid-node's decision log. Each ADR records one
architectural decision — its context, the options weighed, and its
consequences — as a **delta** against the architecture that existed
before it. The synthesized current state lives in
[`docs/architecture.md`](../architecture.md); the behavioral contracts
live in [`openspec/specs/`](../../openspec/specs/). Read the synthesis
first, the specs to know exact behavior, and an ADR to know *why* it is
that way.

## Discipline

- **One decision per ADR**, numbered sequentially across all categories,
  filed under the subsystem directory it primarily affects.
- **Statuses:** `Proposed` → `Accepted`; later decisions may mark an ADR
  `Superseded` (with a *Superseded by* link) or amend it in place with a
  dated *Amendment* section. Superseded ADRs stay in the log — they are
  the history that makes later decisions legible.
- **Characterization ADRs** record a decision after the implementation
  landed (marked as such in the preamble). They are legitimate but
  should be the exception: the normal flow is an OpenSpec change
  proposal ratified *before* implementation, with the ADR written
  alongside. When a change is archived into the main specs, any
  architectural shift it carries gets its ADR and, if needed, an update
  to `docs/architecture.md`.
- **Cross-links** are relative paths between category directories, so
  the tree is self-contained wherever it is checked out.

## Index

### NODE — core node tree and lifecycle
- [ADR-001](NODE/ADR-001-composite-pattern-node-tree-architecture.md) — Composite pattern node tree — **Accepted**, extended by 061
- [ADR-002](NODE/ADR-002-template-method-pattern-for-node-lifecycle.md) — Template-method node lifecycle — **Accepted**, amended by 033, extended by 064
- [ADR-003](NODE/ADR-003-rigid-vs-non-rigid-node-distinction.md) — Rigid vs non-rigid distinction — **Accepted**, amended by 039, third case added by 057, empty boundary defined by 082
- [ADR-004](NODE/ADR-004-multi-cad-backend-adapter-pattern.md) — Multi-CAD backend adapters — **Accepted**, universal target superseded by 046
- [ADR-006](NODE/ADR-006-mtime-based-stl-caching-strategy.md) — Mtime-based STL caching — **Accepted**, extended by 026/028/033, amended by 050/060
- [ADR-008](NODE/ADR-008-time-based-animation-system-for-assemblies.md) — Time-based animation — **Accepted**, extended by 023/072, deferred leaf geometry resolved by 057
- [ADR-023](NODE/ADR-023-kinematic-operations-and-driver-tagged-idempotent-renders.md) — Kinematic operations, driver-tagged idempotent renders — **Accepted**, extended by 027/028
- [ADR-026](NODE/ADR-026-node-identity-parameter-hashed-artifact-keys-vs-tree-names.md) — Parameter-hashed artifact keys vs tree names — **Accepted**, extended by 043/063
- [ADR-028](NODE/ADR-028-cached-base-meshes-and-single-matrix-world-composition.md) — Cached base meshes, single-matrix world composition — **Accepted** (characterization), amended by 085
- [ADR-033](NODE/ADR-033-import-closure-source-set-and-up-to-date-leaf-path.md) — Import-closure source set, up-to-date leaf path — **Accepted**, one-node-per-file driver withdrawn by 071
- [ADR-039](NODE/ADR-039-solid-integrity-at-the-topmost-rigid-node.md) — Solid integrity at the topmost rigid node — **Accepted**, amended 2026-08-10
- [ADR-044](NODE/ADR-044-derived-exact-geometry-capability.md) — Derived exact-geometry capability — **Accepted**
- [ADR-045](NODE/ADR-045-exact-fusion-composition.md) — Exact fusion composition — **Accepted**
- [ADR-046](NODE/ADR-046-conditional-openscad-dependency.md) — Conditional OpenSCAD dependency — **Accepted**
- [ADR-047](NODE/ADR-047-shared-occt-currency-for-exact-backends.md) — One shared OCCT currency for every exact backend — **Accepted**, amended 2026-08-22
- [ADR-050](NODE/ADR-050-nanosecond-fidelity-artifact-freshness.md) — Nanosecond-fidelity artifact freshness — **Accepted**
- [ADR-053](NODE/ADR-053-authored-profile-as-the-sheet-part-source-of-truth.md) — Authored profile as a sheet part's source of truth — **Accepted**
- [ADR-054](NODE/ADR-054-imported-meshes-admitted-selected-and-corrected-explicitly.md) — An imported mesh is admitted, selected and corrected explicitly — **Accepted**
- [ADR-055](NODE/ADR-055-wrapper-module-in-the-imported-part-source-set.md) — The wrapper module joins an imported part's tracked source set — **Accepted**
- [ADR-056](NODE/ADR-056-signals-drivers-ports-and-stepped-simulation.md) — Signals, drivers, ports, and stepped simulation — **Proposed** (design draft, pre-OpenSpec), amended 2026-08-27, amended by 087, extended by 088
- [ADR-057](NODE/ADR-057-the-flexible-leaf-and-spec-carried-geometry.md) — The flexible leaf, whose geometry travels as a spec — **Accepted**
- [ADR-058](NODE/ADR-058-indexed-package-lookup-for-source-closures.md) — Indexed package lookup for source closures — **Accepted**
- [ADR-060](NODE/ADR-060-content-verified-currency-beneath-the-mtime-rule.md) — Content-verified currency beneath the mtime rule — **Accepted**, amends 006, amended by 071/081
- [ADR-061](NODE/ADR-061-a-call-in-a-class-body-is-a-declaration.md) — A call in a node class body is a declaration — **Accepted**, extends 001
- [ADR-062](NODE/ADR-062-typed-parameters-and-the-exponent-algebra.md) — Typed parameters and the exponent algebra — **Accepted** *(amended 2026-09-04: the vocabulary lives in `solid_node.parameters`)*
- [ADR-063](NODE/ADR-063-identity-from-resolved-declared-values.md) — Identity from resolved declared values — **Accepted**, extends 026
- [ADR-064](NODE/ADR-064-an-internal-render-that-returns-nothing.md) — An internal render() that returns nothing, and structural omission — **Accepted**, extends 002, extended by 082
- [ADR-065](NODE/ADR-065-instance-checks-after-resolution.md) — Instance checks after resolution: `check()` on a declarative node — **Accepted**, extends 062
- [ADR-066](NODE/ADR-066-render-at-rest-simulate-per-instant.md) — render() builds the machine at rest, simulate() moves it — **Accepted**, extends 002, 023, extended by 088
- [ADR-071](NODE/ADR-071-node-scoped-content-currency.md) — Node-scoped content currency — **Accepted**, amends 060/033, amended by 081
- [ADR-072](NODE/ADR-072-a-declared-time-base.md) — A declared time base: `time = Time(loop=…)`, seconds on every path — **Accepted**, extends 008, amended by 087
- [ADR-077](NODE/ADR-077-declared-tessellation-precision.md) — Declared tessellation precision: `linear_deflection` / `angular_deflection` — **Accepted**, depends on 026/044/045/047/063/071
- [ADR-078](NODE/ADR-078-the-step-part-as-an-exact-external-file-leaf.md) — The STEP part as an exact external-file leaf: `StepNode` — **Accepted**, extends 054/055, depends on 047/050/071/077, extended by 115
- [ADR-079](NODE/ADR-079-reading-a-step-documents-placements-and-scaffolding-source.md) — Reading a STEP document's placements and scaffolding declarative source: `StepAssembly`, `solid import-step` — **Accepted**, extends 078, depends on 077, amended by 115
- [ADR-081](NODE/ADR-081-per-contributor-metadata-guards-aggregate-mtime-currency.md) — Per-contributor metadata guards aggregate-mtime currency — **Accepted**, amends 060/071, depends on 033/050
- [ADR-082](NODE/ADR-082-empty-composition-belongs-to-assemblies-not-fusions.md) — Empty composition belongs to assemblies, not fusions — **Accepted**, extends 064, depends on 003/039/061
- [ADR-083](NODE/ADR-083-simulation-time-is-finite-forward-and-tick-aligned.md) — Simulation time is finite, forward, and tick-aligned — **Accepted**, extends 056
- [ADR-087](NODE/ADR-087-one-module-one-question.md) — One module, one question: ports and the declared time base move to `solid_node.motion.ports` — **Accepted**, amends 056/072 (export location only)
- [ADR-088](NODE/ADR-088-a-joint-owns-one-coordinate.md) — A joint owns one coordinate: `Revolute` and `Prismatic` — **Accepted**, extends 056/066, depends on 023/028/061/063/087, extended by 093/094/095, frame decision superseded in part by 097
- [ADR-089](NODE/ADR-089-drives-relates-two-coordinates.md) — `drives` relates two coordinates: one verb, a law passed in, and a solve oriented from the bound side — **Accepted**, extends 061/066, depends on 022/056/076/080/087/088
- [ADR-093](NODE/ADR-093-joints-of-one-class-compose-in-declaration-order.md) — The joints of one class compose in declaration order, innermost first — **Accepted**, extends 088, depends on 023/028/066
- [ADR-094](NODE/ADR-094-an-orbit-carries-a-point-and-derives-its-radius.md) — An orbit carries a point, and derives its radius: `Orbit`, with no typed radius or phase — **Accepted**, extends 088, depends on 022/093, `carries` sentinel revised by 097, revived by 098 for the site-declared default
- [ADR-095](NODE/ADR-095-a-free-joint-owns-six-coordinates.md) — A free joint owns six coordinates: `Free`, one declaration for a floating body — **Accepted**, extends 088, depends on 093, related to 089/094, open frame question closed by 097 for the class-declared form and given its other spelling by 098
- [ADR-096](NODE/ADR-096-a-relation-broadcasts-over-a-repeated-child.md) — A relation broadcasts over a repeated child: one relation per realized copy, `index` on the copy — **Accepted**, extends 089, depends on 061/063/093
- [ADR-097](NODE/ADR-097-a-joint-is-stated-in-the-frame-of-whoever-declares-it.md) — A joint is stated in the frame of whoever declares it: a class-body joint reads its own rest frame, no carry — **Accepted**, supersedes 088's frame decision in part, revises 094/095, depends on 093, extended by 098
- [ADR-098](NODE/ADR-098-a-joint-may-be-declared-where-a-child-is-placed.md) — A joint may be declared where a child is placed: a site-declared joint reads the declaring parent's frame, carried innermost — **Accepted**, extends 097, revives 094's `_OWN_PLACED_ORIGIN` sentinel, extends the slot of 093, gives a spelling to 095's open frame question
- [ADR-099](NODE/ADR-099-the-enumerations-simulate-phases-are-one-tree-pass.md) — The enumeration's simulate phases are one tree pass: relations defer to a whole-tree fixpoint, a read of a coordinate a relation binds is refused, a coordinate is cleared with the motion it caused, a subclass replaces a named relation — **Accepted**, revises 089, cites 093/096
- [ADR-100](NODE/ADR-100-a-relation-may-name-several-coordinates-at-each-end.md) — A relation may name several coordinates at each end: `&` groups a source, a tuple or `&` groups a driven end, the law's two arguments shaped rather than spread, one record per copy holding all its ends — **Accepted**, extends 089, depends on 096, cites 099, shared-coordinate refusal amended by 121
- [ADR-102](NODE/ADR-102-native-materialization-precedes-optional-scad-presentation.md) — Native materialization precedes optional SCAD presentation — **Accepted**, amends 002/004/045/046 and artifact currency
- [ADR-104](NODE/ADR-104-a-third-time-base-elapsed-seconds-that-never-wrap.md) — A third time base — elapsed seconds that never wrap: `Time.running()` beside `Time(loop=...)`, told apart by `mode`, reading bare `$t` until the compiled program is published — **Accepted**, extends 072, cites 008
- [ADR-105](NODE/ADR-105-the-run-owns-the-coordinates-and-binds-them.md) — The run owns the coordinates and binds them: a bank of every driver and joint coordinate from the rest pose, bound through `set_state`'s delivery as a binder the solver recognizes, one owner per input — **Accepted**, amended 2026-09-13 (one simulation owns a tree at a time, and the newest takes it), depends on 104, extends 056, cites 089/099
- [ADR-106](NODE/ADR-106-one-law-two-readings.md) — One law, two readings: running, a relation contributes `f(end) − f(start)` over a tick, exact across kinks, and a law is inspected as the expression it builds over symbols — **Accepted**, amended by 122 for its Kahn ordering clause (a strongly connected component is contracted to one entry and ordered per piece), depends on 105, extends 089, cites 022/076
- [ADR-107](NODE/ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md) — A jump is located inside the tick and subtracted: the path is cut at every crossing, each piece holds a branch read at its midpoint, and the increment is the sum over the pieces — **Accepted**, depends on 106/105, cites 022/076/080, amended by 121 for a law that reads its own driven coordinate
- [ADR-108](NODE/ADR-108-a-range-is-a-physical-stop-that-stops-the-connected-group.md) — A range is a physical stop that stops the connected group: the tick is cut at the fraction the coordinate reaches its bound, every input whose movement pushes it stops with it, and the command that pushed retires `blocked` with the travel it admitted — **Accepted**, depends on 105/107, cites 083
- [ADR-109](NODE/ADR-109-a-range-bound-may-be-an-expression-evaluated-at-the-committed-state.md) — A range bound may be an expression evaluated at the committed state: a callable of the joint's own coordinate, compiled once like a law, evaluated per tick under a running root and at the value being bound everywhere else — **Accepted**, amended by 113, depends on 106, cites 076/088
- [ADR-112](NODE/ADR-112-a-control-is-a-declaration-on-the-model-and-the-gesture-comes-from-the-tree.md) — A control is a declaration on the model, and the gesture's geometry comes from the tree: `Button(part, instruction)` and `Turn(part, input)` declared beside `instructions`, the coordinate, joint, axis and origin read off the tree, `per_unit` measured from the compiled program at rest, published additively under version 5 — **Accepted**, its single-joint narrowing superseded in part by 117; depends on 105/110, cites 111 and viewer ADR-048
- [ADR-113](NODE/ADR-113-a-bound-may-read-other-coordinates.md) — A bound may read other coordinates — a constraint stops what carries it outward: `Bound(expression, reads=(...))` named as a relation's ends and resolved against the declarer; under a running root the reads are evaluated along the tick's path over the bound's sub-program, the level sampled inside the stretch, and every input carrying it outward stopped, the reads' inputs included; untimed it is judged when the enumeration closes — **Accepted**, amends 109, depends on 108/109, cites 089/097/110/111
- [ADR-114](NODE/ADR-114-a-joints-placement-is-identified-by-its-slot-not-by-what-bound-it.md) — A joint's placement is identified by its slot, not by what bound it: `Joint.clear` drops by `_joint_slot` rather than by remembered objects, `clear_solved` clears a coordinate's joint along with its value, and the test runner's checkpoint restore re-places a restored child's joints through one shared seam — **Accepted**, depends on 093, cites 099
- [ADR-115](NODE/ADR-115-a-product-is-selected-by-name-then-by-its-index-among-the-products-of-that-name.md) — A product is selected by name, then by its index among the products of that name: `part_index` beside `part`, a 1-based position relative to the declared name that can never contradict it, `StepAssembly` publishing each product's identity and selector, and `solid import-step` keyed on identity end to end so two same-named products or sub-assemblies each get their own generated class — **Accepted**, extends 078, amends 079
- [ADR-117](NODE/ADR-117-a-control-may-name-the-freedom-it-means.md) — A control may name the freedom it means, and the document says which placement that freedom is: `Slide(part, input)` beside `Button` and `Turn`, a keyword-only `coordinate=` selecting one existing single-coordinate joint that poses the part or an ancestor, and `operation_span` publishing that coordinate's own placement block for a translational or selected entry, so an inner joint's motion never turns an outer joint's line — **Accepted**, supersedes 112 in part, depends on 093/114, cites 110/111 and viewer `slide-and-turn-parts`
- [ADR-120](NODE/ADR-120-a-marking-is-a-declaration-that-produces-an-artifact-and-no-solid.md) — A marking is a declaration on a part that produces an artifact and no solid: `Marking(Svg(...), Wrapped(...)|Flat(...), color=...)` in a rigid node's class body — or in a plain mixin it inherits — collected and refused by `NodeMeta`, meshed as one surface artifact beside the part's `.stl` with a currency of its own over the artwork, and published as an additive `markings` list that keys no artifact, enters no piece and moves no document version — **Accepted**, depends on 026/061, cites 043/057/060/071
- [ADR-121](NODE/ADR-121-a-law-may-read-the-coordinate-it-drives.md) — A law may read the coordinate it drives — retained-angle engagement, integrated piece by piece: a coordinate named in a relation's source group AND as its one driven end is a READ of that end, admitted only as a SWITCH over a banked coordinate, binding nothing at rest and refused under any other time base; its tick is integrated in two layers — the independent jump nodes partitioning the path as ever, the dependent ones walked inside each piece with their branches read at the piece's LEFT END from the retained value — and after a cut the coordinate is committed at the nearest representable value on the FAR SIDE of the surface, published as `needs ∩ gives` in a version 6 document — **Accepted**, amends 100/107, depends on 105/106/107/108/113, cites 057/110/111
- [ADR-122](NODE/ADR-122-a-selection-decides-which-sources-a-law-reads.md) — A selection decides which sources a law reads — a cycle every selection breaks is a BLOCK, ordered piece by piece: the nontrivial strongly connected components of the program's dependency graph are contracted to one entry each, a SELECTOR is a jump node of a member's law whose level reads no coordinate the block determines, a source is SWITCHED when folding that node's branch to zero removes it from the law (`floor`, `ceil`, a remainder's quotient and a comparison, never `sign`), and over a stretch the selectors are located first and the block runs piece by piece with their midpoint branches SUBSTITUTED into each member; membership is decided by a pre-pass before the rest render, where a block relation binds nothing; a still-cyclic piece refuses the tick transactionally, and a program carrying a block is a version 7 document whose published member order is a listing, not an execution order — **Accepted**, amended 2026-09-16 (the corpus scenario meant to pin the block's order did not, until `pin-the-block-order` changed its script), amends 106, depends on 105/106/107/121, cites 057/110/111/113
- [ADR-123](NODE/ADR-123-a-kink-is-a-cut.md) — A kink is a cut, and a piecewise-affine quantity is solved — `abs`, `min` and `max` are the CONTINUOUS SELECTIONS of the symbolic vocabulary, each returning one of its operands exactly, so a followed quantity built over them is PIECEWISE AFFINE: its breakpoints are solved in the graph's postorder with no sampling, no bisection and no new tolerance, and each piece between them is solved as any affine one is; a kink breakpoint is not a crossing, so it is recorded nowhere, enters no partition an increment is summed over and moves no coordinate to a far side, which is why every existing answer is unchanged; the published `affine` flag stays two-valued and a kinked quantity publishes `false`, so no document field is added and no version moves — **Accepted**, amends 107/108/121/122, cites 110/111
- [ADR-124](NODE/ADR-124-only-what-moves-along-a-tick-s-path-is-evaluated.md) — Only what moves along a tick's path is evaluated — a quantity followed over one compiled graph evaluated many times along one tick's path, with one branch reading, has the part of it that no moving source reaches computed ONCE and read back at every later point, decided in the same postorder walk `GraphValue.evaluate` would have made anyway for the piece's own first point; the moving names are the run's own `delta` statement plus, for a level only, the driven coordinate of a self-read; no cache outlives the tick, no knob, no document field or version moves, and every crossing, landing, branch reading, stop and committed value is unchanged to the byte; measured 4.5× on the originating Curta's tick (3.279 s → 0.727 s) with the same committed snapshot — **Accepted**, extends 107/121, depends on 123
- [ADR-125](NODE/ADR-125-a-state-is-a-driver-the-machine-writes.md) — A state is a driver the machine writes, committed at an event: `State(...)` declared beside `Driver` on any assembly and qualified by the driver's own rule, written by nothing but a `(a & b).commits(targets, at=, law=)` relation stated beside `drives`, whose `at` is ONE jump node of ADR-107's vocabulary — solved where it is affine or kinked, refused at construction where it curves — and whose every RISING crossing on a request's straight path is an event, landed on ADR-121's far side, read pre-event and synchronously, committed in path order, with ties decided by IDENTITY of the landing float and no tolerance anywhere; several relations MAY write one state and two of them at ONE landing refuse the request; a clocked `Sim` takes no `dt`, costs no pose per request, refuses the whole cadence surface by name, commits nothing when anything including the FINAL POSE is refused, and is refused publication until the document cycle — while a tree declaring no `State` is unchanged in behaviour, in published bytes and in cost — **Accepted**, amends nothing, depends on 056/099/106/107/109/121/123, cites 100/104/105/110/124
- [ADR-126](NODE/ADR-126-a-bound-stops-a-clocked-request-on-its-path.md) — A bound stops a clocked request on its path: under a clocked root a declared `range` is a STOP, and the stop is a TRUNCATION of the request's travel before any event is located — one moving driver being ADR-108's whole group — solved against a CHAIN composed once at construction by SUBSTITUTION from the relations the rest render resolved (intermediate ports traversed, nothing simplified, neither a symbolic pose nor `compile_program`), with the bound's own coordinate read at the request's START, its `reads` taken along the path, a jumped level PARTITIONED at its own surfaces and a curved one refused; the driver lands on the last representable value that SATISFIES the bound, the threshold is `max(0, g(0))` per request, a request stopped at ZERO travel is ADMITTED, and the clocked simulation is the SOLE AUTHORITY for the constraints it compiled — the enumeration skipping them at a request's pose through a mark, the simulation judging them itself over the final bank through the same chain, and the agreement between chain and pose being a tolerant TEST and never a runtime refusal — reported as `admitted`, `stops` and the ring `sim.stops` — **Accepted**, amends nothing, depends on 106/107/108/109/113/121/123/125, cites 104/105/110/122/124
- [ADR-127](NODE/ADR-127-a-clock-is-a-banked-value-and-an-event-on-it-is-an-event.md) — A clock is a banked value, and an event on it is an event: `Time.elapsed()` is a THIRD spelling of `Time` in ADR-104's own one-field shape — elapsed seconds that never wrap, WITHOUT the running mechanics — which makes the time base and the state discipline independent axes of which only the STATE DISCIPLINE selects the executor, so an elapsed root declaring no `State` is admitted and equivalent down to its published bytes; under a CLOCKED root it banks `time` in seconds under the one `CLOCK_NAME` (carried by `snapshot`/`restore`, opened by `state=`, returned by `reset`, read by `sim.time`, the one refused name this lifts), moved by the SAME verb `move('time', by=|to=)` with backwards refused by name and zero admitted, and NAMED as a source of a committing relation whose every rising step is an event located by ADR-125's own solver with NO new tolerance — the pendulum's release being affine in time and rising twice per period — the clock delivered through `drive_tree`'s EXISTING `visit` hook so a request still costs one pose; nothing stops a clock: a time request is never clipped, an impossible pose refuses the request whole, and any free name surviving a composed chain that is not a bank id is refused at construction — **Accepted**, amends nothing, depends on 104/107/121/123/125, cites 105/106/108/110/113/126

### BUILD — loading, watching, CLI
- [ADR-005](BUILD/ADR-005-path-based-dynamic-module-loading.md) — Path-based dynamic module loading — **Accepted**, amended by 119
- [ADR-007](BUILD/ADR-007-watchdog-library-filesystem-monitoring.md) — Watchdog filesystem monitoring — **Accepted**
- [ADR-021](BUILD/ADR-021-snapshot-cli-command-for-agent-autonomy.md) — Snapshot CLI command — **Accepted**, amended by 041
- [ADR-024](BUILD/ADR-024-command-first-cli-grammar-and-duck-typed-command-registry.md) — Command-first CLI grammar — **Accepted**, amended by 119
- [ADR-030](BUILD/ADR-030-complete-build-publication-boundary.md) — Complete-build publication boundary — **Reversed** by 038
- [ADR-031](BUILD/ADR-031-published-viewer-snapshot.md) — Published viewer snapshot — **Accepted**, amended by 034
- [ADR-032](BUILD/ADR-032-symlink-swap-build-publication.md) — Symlink-swap build publication — **Superseded** by 038
- [ADR-038](BUILD/ADR-038-per-artifact-atomic-build-publication.md) — Per-artifact atomic build publication — **Accepted**, amended by 119, extended by 086
- [ADR-041](BUILD/ADR-041-browser-rendered-transparent-snapshots.md) — Browser-rendered transparent snapshots — **Accepted**
- [ADR-059](BUILD/ADR-059-import-at-the-point-of-use.md) — Import at the point of use — **Accepted**, extends 024, extended by 069
- [ADR-067](BUILD/ADR-067-fresh-interpreter-build-subprocesses.md) — Fresh-interpreter build subprocesses — **Accepted**, amended by 084
- [ADR-069](BUILD/ADR-069-deferred-callables-for-a-modules-own-call-sites.md) — Deferred callables for a module's own call sites — **Accepted**, extends 059
- [ADR-084](BUILD/ADR-084-one-fresh-builder-per-sealed-source-generation.md) — One fresh builder per sealed source generation — **Accepted**, amends 067
- [ADR-086](BUILD/ADR-086-state-dependent-scad-publishes-at-assembly-phase-completion.md) — State-dependent SCAD publishes at assembly phase completion — **Accepted**, extends 038
- [ADR-103](BUILD/ADR-103-the-browser-is-the-only-interactive-development-viewer.md) — The browser is the only interactive development viewer — **Accepted**, amends 046/068/102
- [ADR-116](BUILD/ADR-116-an-artifact-import-is-anchored-on-the-build-directory.md) — An artifact import is anchored on the build directory — **Accepted**, extends 119, cites 086
- [ADR-119](BUILD/ADR-119-named-project-models-and-per-model-build-directories.md) — Named project models and per-model build directories — **Accepted**, amends 005, 024, 038, extended by 116 (renumbered 2026-09-15 from 073)

### IPC — inter-process communication
- [ADR-015](IPC/ADR-015-fastapi-unified-stack-for-http-services.md) — FastAPI + Uvicorn HTTP stack — **Accepted, amended** (broker consumer removed)
- [ADR-016](IPC/ADR-016-websocket-broker-pattern-for-ipc.md) — WebSocket broker — **Superseded** by 018
- [ADR-017](IPC/ADR-017-websocket-global-lock-for-process-synchronization.md) — WebSocket global lock — **Superseded** by 018
- [ADR-018](IPC/ADR-018-lean-framework-separation.md) — Lean framework separation — **Accepted**

### MATH — expression evaluation parity
- [ADR-022](MATH/ADR-022-cross-runtime-degree-trig-parity-for-t-expressions.md) — Cross-runtime degree-trig parity for `$t` and driver expressions — **Accepted**, revised 2026-09-06 (defect fixed and parity enforced 2026-08-26; vocabulary widened beyond trigonometry, and the corpus must cover every emitted name)
- [ADR-076](MATH/ADR-076-mechanism-laws-as-compositions-over-expression-math.md) — Mechanism laws as compositions over expression math — **Accepted**, depends on 022
- [ADR-101](MATH/ADR-101-motion-sharing-begins-at-construction.md) — Motion sharing begins at construction — **Accepted**, supersedes 080's eager construction and flat SCAD decisions in part, depends on 022/076

### TEST-FRAMEWORK — CAD testing
- [ADR-009](TEST-FRAMEWORK/ADR-009-trimesh-based-mesh-assertions-for-cad-testing.md) — Trimesh mesh assertions — **Accepted**, extended by 025
- [ADR-010](TEST-FRAMEWORK/ADR-010-testcasemixin-pattern-for-embedded-tests.md) — TestCaseMixin embedded tests — **Accepted**
- [ADR-011](TEST-FRAMEWORK/ADR-011-animation-testing-decorators.md) — Animation testing decorators — **Accepted**
- [ADR-025](TEST-FRAMEWORK/ADR-025-perturbation-based-kinematic-fit-assertions.md) — Perturbation-based kinematic fit assertions — **Accepted**, extended by 029, adjacency guidance superseded by 040
- [ADR-029](TEST-FRAMEWORK/ADR-029-manifold-cache-and-aabb-broad-phase-for-assertions.md) — Manifold cache, AABB broad-phase — **Accepted** (characterization), extended by 070, 091, 092
- [ADR-040](TEST-FRAMEWORK/ADR-040-topmost-rigid-assembly-integrity.md) — Topmost-rigid assembly integrity — **Accepted**, revised 2026-08-11 (volume certificate removed)
- [ADR-048](TEST-FRAMEWORK/ADR-048-gravity-support-graph-assertion.md) — Gravity support graph assertion — **Accepted**, extended by 049
- [ADR-049](TEST-FRAMEWORK/ADR-049-static-equilibrium-as-lp-feasibility.md) — Static equilibrium as LP feasibility — **Accepted**
- [ADR-052](TEST-FRAMEWORK/ADR-052-conditional-mesh-engine-dependency.md) — Conditional mesh-engine dependency — **Accepted**
- [ADR-070](TEST-FRAMEWORK/ADR-070-relative-placement-as-the-identity-of-an-intersection-question.md) — Relative placement as the identity of an intersection question — **Accepted**, extends 029, amended by 090
- [ADR-073](TEST-FRAMEWORK/ADR-073-the-comparison-kernel-is-a-property-of-the-test-run.md) — The comparison kernel is a property of the test run — **Accepted**, extends 044, 029
- [ADR-074](TEST-FRAMEWORK/ADR-074-the-mesh-engine-judges-its-own-input.md) — The mesh engine judges its own input — **Accepted**, amends 029
- [ADR-075](TEST-FRAMEWORK/ADR-075-the-perturbation-is-the-nodes-first-operation.md) — The perturbation is the node's first operation — **Accepted**, amends 025
- [ADR-090](TEST-FRAMEWORK/ADR-090-the-placement-quantum-is-a-property-of-the-test-run.md) — The placement quantum is a property of the test run — **Accepted**, amends 070
- [ADR-091](TEST-FRAMEWORK/ADR-091-the-broad-phase-chooses-its-indexing-frame.md) — The broad phase chooses its indexing frame — **Accepted**, extends 029, extended by 092
- [ADR-092](TEST-FRAMEWORK/ADR-092-face-boxes-decide-an-enclosed-pair-without-a-boolean.md) — Face boxes decide an enclosed pair without a boolean — **Accepted**, extends 029, 091
- [ADR-118](TEST-FRAMEWORK/ADR-118-an-unexpected-success-fails-the-run.md) — An unexpected success fails the run: `solid test` honours `skipTest`/`unittest.skip` and `@unittest.expectedFailure`, and a stale expected-failure marking that starts passing fails the run — **Accepted**

### VIEWER-WEB — web viewer
- [ADR-012](VIEWER-WEB/ADR-012-threejs-for-3d-rendering.md) — Three.js rendering — **Accepted** — *Relocated* to solid-node-viewer (ADR-068)
- [ADR-013](VIEWER-WEB/ADR-013-react-frontend-framework.md) — React frontend — **Accepted**, amended by 036 — *Relocated* to solid-node-viewer (ADR-068)
- [ADR-014](VIEWER-WEB/ADR-014-recursive-nodeapi-rest-pattern.md) — Recursive NodeAPI REST pattern — **Superseded** by 036 — *Relocated* to solid-node-viewer (ADR-068)
- [ADR-027](VIEWER-WEB/ADR-027-absolute-matrix-composition-for-viewer-transforms.md) — Absolute world-matrix viewer transforms — **Superseded** by 036 — *Relocated* to solid-node-viewer (ADR-068)
- [ADR-036](VIEWER-WEB/ADR-036-snapshot-served-shared-viewer-shell.md) — Snapshot-served shared viewer shell — **Accepted** — *Relocated* to solid-node-viewer (ADR-068)
- [ADR-037](VIEWER-WEB/ADR-037-targeted-in-place-viewer-updates.md) — Targeted in-place viewer updates — **Accepted** — *Relocated* to solid-node-viewer (ADR-068)

### EXPORT — static distribution
- [ADR-068](EXPORT/ADR-068-optional-viewer-package-behind-a-process-boundary.md) — Optional viewer package behind a process boundary — **Accepted**, amends 020, 035, 036, 041
- [ADR-020](EXPORT/ADR-020-static-export-and-embeddable-viewer-widget.md) — Static export and embeddable widget — **Accepted** — *Relocated* to solid-node-viewer (ADR-068)
- [ADR-034](EXPORT/ADR-034-shared-node-tree-document-schema.md) — Shared node-tree document schema across export and build snapshots — **Accepted**, amended by 051
- [ADR-035](EXPORT/ADR-035-reusable-viewer-core-and-declared-api.md) — Reusable viewer core and declared API version — **Accepted** — *Relocated* to solid-node-viewer (ADR-068)
- [ADR-042](EXPORT/ADR-042-host-controlled-viewer-assembly-navigation.md) — Host-controlled viewer assembly navigation — **Accepted** — *Relocated* to solid-node-viewer (ADR-068)
- [ADR-043](EXPORT/ADR-043-content-derived-printed-piece-identity.md) — Content-derived printed-piece identity — **Accepted**, amended by 085
- [ADR-051](EXPORT/ADR-051-producer-owned-animation-time-in-node-documents.md) — Producer-owned animation time in node-tree documents — **Accepted**
- [ADR-080](EXPORT/ADR-080-a-shared-subexpression-is-named-once.md) — A shared subexpression is named once: the document's `bindings` table — **Accepted**, eager construction and flat SCAD decisions superseded in part by 101; extends 034, depends on 022/051
- [ADR-085](EXPORT/ADR-085-persistent-piece-facts-behind-a-verified-artifact-snapshot.md) — Persistent piece facts behind a verified artifact snapshot — **Accepted**, amends 043/028
- [ADR-110](EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md) — The compiled program is published in the document, under a version an old consumer refuses: a running root's document declares version 5, carries the program compile time decided, and poses its geometry from a committed bank — **Accepted**, extends 034/080, depends on 104–109, cites 051/068
- [ADR-111](EXPORT/ADR-111-a-conformance-corpus-is-the-contract-between-the-two-runtimes.md) — A conformance corpus is the contract between the two runtimes: a producer-generated fixture replayed by both, exact for discrete state and at the run's own agreement tolerance for floats, with a coverage guard that refuses to regenerate a narrower one — **Accepted**, depends on 110, cites 022/068

ADR-019 (the solid-builder agent system) predates the shop and lives
with the agent tooling's own history, not in this framework log.
