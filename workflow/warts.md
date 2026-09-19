

# 3DPrintedClocks

- **Generated-artifact freshness is not dependable for source-bound CAD
  leaves.** While changing Wall Clock 22's source-derived hanging-weight
  datum, `machinome test wall_clock_22 --faceted` continued to compare an older
  generated assembly pose. Removing only that model's ignored
  `_build/wall_clock_22` cache was needed to force regeneration; the next
  run also tried to reuse a deleted `clock-Pillars...stl` artifact and raised
  `FileNotFoundError`. The artifact identity appears not to include every
  source adapter dependency, and the test artifact index can retain paths
  that the producer no longer restores. A project should never need cache
  deletion for a source edit to reach a spatial assertion. Candidate
  framework work: make dependency fingerprints complete and make the test
  artifact index self-healing when an artifact is absent. Evidence:
  `projects/3DPrintedClocks`, Wall Clock 22, 2026-09-10. Deferred for a
  framework agent; no framework workaround is part of the clock model.

# snappy-reprap

- The shared .venv broke at 00:00 UTC while my first build ran: something else pip-installed ocp_vscode, cadquery-ocp-novtk and downgraded build123d, and import cadquery now fails there. I did not touch it. All builds and tests ran in a
  private venv in the session scratchpad with the same editable framework and molejo checkouts. The repair is a forced reinstall of cadquery-ocp 7.8.1.1.post1, which is your call.
- Framework gap: the faceted test path refuses these OpenSCAD 2021.01 STLs as non-watertight before Manifold ever sees them, though Manifold ingests them without error. The project's contracts therefore call manifold3d directly. That is
  a candidate wart; I have not filed it.


# kossel

- Framework quirks met, not filed: perturbation directions are read in the frame before a node's first translation, so the tests say so; assertClose is unusable for a screw in a hole, so the tests carry gap and hole helpers.
  Out of scope and stated: the retractable Z probe, the FSR glass frame, the spool, wiring, and a length-true Bowden tube.

# fender-bender

- The upstream geometry has no rigid interference-free bracket release, and its guide-wall click bumps overlap the frame at rest. The contracts carry stated, measured allowances for those two things (release path and snap) and say so in
  the specs and README. If you would rather have them red, say so.
- The framework's watertight gate refuses seven upstream STLs that Manifold accepts. That blocked assertNoSolidInterference and the faceted kernel, so the project checks interference pairwise on exact solids, and the
  support-under-gravity contract is unverified. A candidate wart, not filed.

# openvmp

- The blueprint nests each foot 11.5 mm short of the thigh's knee shaft, and the shaft sits inside the foot's hubs at rest. The simulation bends about the shaft and records the offset.
- No pose in this blueprint rolls on level wheels, and the foot fouls the thigh's knee motor past 45° of bend where ROS allows 126°. Duct is therefore a 45° cambered brace. A direct Crouch to Hug ramp swings the hooks through each
  other, so the scenario routes such moves through Rest. Look is limited to the quadrant clear of the hip's vision beams.
- The base's "worm collar" is actually on the gear shaft, two stepper drivers are placed through the battery, and 379 within-link overlaps are the blueprint's own placements. All of it is in the design record.
- Framework gaps, recorded in the design and in memory but not filed: the spatial assertions' watertight gate rejects 21 of 67 vendor pieces, so clearance is measured by a project engine; the exact export keeps degenerate triangles;
  tessellation precision is not declarable per node; a bare file path in machinome test builds every node class, so run it with robot.py:Don1.

# Execution plan (2026-09-06)

Triage of the findings above, pilot-ratified. Items 1-4 are framework fixes
run as standalone framework-change cycles; 5 and 6 are deferred until a
second project asks. Once each fix is on machinome main, the projects that
carried a workaround for it drop the workaround.

## Fix now

1. **The watertight gate.** `_cached_local_bounds` in `machinome/test.py`
   demands trimesh's `is_volume` before any spatial assertion, even on
   exact-kernel runs and even for the broad phase, and the per-binding check
   below it demands `is_watertight`. Manifold accepts the meshes trimesh
   refuses. Let Manifold build the mesh and judge by its own status, keeping
   trimesh's verdict only as diagnostic text. Evidence: snappy-reprap,
   fender-bender, openvmp.
2. **Exact export keeps degenerate triangles.** The exact-leaf STL export
   calls `exact.write_stl` with degenerate removal off while the fusion path
   turns it on. Turn it on for leaves. Evidence: openvmp (shafts, standoff,
   stepper, servo frame close on this alone). Same cycle as item 1.
3. **Perturbation frame.** The perturbation is inserted before the node's
   first Translation, so a node whose only op is a rotation is displaced
   after it, in the parent frame, while the API skill promises directions
   are local. Insert before every operation so the code matches the skill.
   Evidence: kossel, abacus. Own cycle.
4. **Bare-path `machinome test file.py` builds every class.** A sub-assembly
   whose ports are bound by its parent crashes standalone. Default the bare
   path to the manifest's declared models, or the file's main class, instead
   of every class. Evidence: openvmp. Own cycle.

## Deferred

5. **Per-node tessellation precision.** openvmp's stored triangulation in
   render() is a legitimate workaround; one project asks. Propose when a
   second one does.
6. **A clearance contract for a screw in a hole.** kossel's gap and hole
   helpers are the evidence for a new contract, not a fix.

## Not framework fixes

- The venv breakage is repaired; the workspace venv imports cadquery.
- fender-bender's release-path and snap allowances are a pilot decision
  (keep the measured allowances, or make the contracts red).
- The openvmp blueprint findings and kossel's out-of-scope list are design
  record about the upstream machines.

## Project follow-ups after integration

- snappy-reprap: replace the private manifold3d assertions with the
  framework's spatial contracts.
- fender-bender: use assertNoSolidInterference and the faceted kernel;
  verify the support-under-gravity contract.
- openvmp: drop the project clearance engine and the render()-time
  tessellation where degenerate removal now suffices; run `machinome test` on
  the bare file.
- kossel, abacus: state perturbation directions in the node's own frame.

## Status (2026-09-06, end of day)

Items 1-4 are on machinome main, each a two-commit standalone cycle,
nothing pushed:

- 1+2 `trust-manifold-over-trimesh`: 5ed122e + 395769f, ADR-074.
- 3 `perturb-in-the-nodes-own-frame`: b2809b9 + 2fa03ff, ADR-075.
- 4 `test-a-bare-file-by-its-tests`: 811966b + 66f6bee, no ADR.

Shop skills corrected (25e6a93). Projects refactored, each committed in
its own repository: abacus 52e180e and kossel 70e7269 (directions in the
node's frame); snappy-reprap 02561fd (framework pair contracts; the
engine kept only for summed and slab volumes); fender-bender eb672d1
(framework interference and support contracts; the support-under-gravity
requirement is now verified, 18 passed exact); openvmp (bare-path test
run, 30 passed; the engine admits 63 of 67 artifacts, up from 46; the
cross-link clearance engine stays for the four it still refuses and for
the blueprint's within-link overlaps, which are placements, not motion).
Items 5 and 6 remain deferred.

# Expression math and mechanisms (2026-09-06)

Findings from lifting the project `kinematics.py` helpers into the
framework: two standalone cycles, `expression-math` (`machinome.math`
grows abs, floor, ceil, sign, min, max, clamp, clamp01, ramp, lerp, wrap,
piecewise, bump, polar, turn, rotate_x/y/z) and `mechanisms`
(`machinome.mechanisms`: gears, screws, cranks, deltas, linkages). Both are on
machinome main as of 2026-09-06 (main at e28cd3a, nothing pushed):

- `expression-math`: d0688b1 + 2369bd5, ADR-022 revised.
- `mechanisms`: ebe874b + e28cd3a (rebased onto the first; four
  documentation files conflicted additively), ADR-076.

Viewer fixture committed in machinome-viewer at 616ed9b. Cycle worktrees
torn down; branches kept. Not triaged yet; the items below are candidates.

## Framework

7. **`%` on a symbolic value disagrees across runtimes.** solid2's
   `OpenSCADConstant.__mod__` emits `(a % b)`, which OpenSCAD and the viewer
   evaluate C-style (sign of the dividend), while a numeric render uses
   Python's `%` (sign of the divisor). A project writing `angle % 360` on a
   driver gets two answers for a negative operand, and neither the parity
   corpus nor anything else catches it. Candidate fix: export a remainder
   from `machinome.math` whose numeric face is `math.fmod` and whose
   symbolic face is the `%` operator, add it to `SYMBOLIC_BUILTINS` and the
   parity corpus, and document that bare `%` is not expression-safe.
   Evidence: found while refusing `mod` in `expression-math` (design D4).
8. **No way to spell a dimensioned literal in the algebra.** `180` and
   `360` are dimensionless, `Angle` is its own axis, so every law carrying a
   degree literal has no declared face: `meshed_angle(theta, ...)`,
   `screw_travel`, `wrap(angle)` with its default period, and the
   trigonometric `bump` all raise at class definition. The escape hatches
   are `.value` (unchecked) and an inline anonymous declaration
   (`wrap(angle, Angle(360.0))`), which works but is a parameter, not a
   constant. Candidate fix: an Angle-typed (and Length-typed) literal in
   `machinome.parameters`. Evidence: `expression-math` (bump, wrap, turn),
   `mechanisms` (design D3, ADR-076 open question).
9. **`tools/generate_parity_fixture.py` cannot run from a worktree.** Its
   default output path resolves to `ROOT/../machinome-viewer/...`, which
   from `machinome/WTs/<name>/` is a directory that does not exist. Resolve
   through the Git common directory, as the shop contract prescribes for
   workspace paths, or require the output argument. Evidence:
   `expression-math` task 5.4.
10. **Non-reproducible flake in `tests/test_exact_geometry.py`.**
    `ExactArtifactTest::test_a_shape_without_file_identity_is_not_cached`
    failed once in a full run and passed alone and in two further full
    runs. It asserts `assertIsNot` on two `placed_shape` results, so an
    object-identity or GC-recycling assumption is the likely cause. Seen
    once during `mechanisms`.

## Deferred

11. **The openflexure four-bar decomposition** (`leg_lean`, `lever_rise`)
    as a mechanism law. One project asks; propose when a second flexure
    stage does (ADR-076 open question).
12. **`piecewise` expression length.** ~~A sum of clamped ramps puts n-1
    `min(max(...))` terms on the wire with the driver repeated in each;
    `bump` repeats its clamp four times. Accepted in `expression-math`
    (no common-subexpression pass); revisit only if a published document
    grows past what the viewer parses comfortably.~~ **Fixed 2026-09-07**,
    after `wall_clock_53_grasshopper` published 31.6 MB of expressions
    (seven million pasted nodes over 263 distinct subexpressions) and
    animated at two frames per second. Three cycles: the viewer's
    `share-expression-subtrees` (ADR-043, a hash-consed DAG evaluated
    once per distinct subexpression per pass: 633 ms to 0.36 ms per
    frame, 569 MB to 69 MB of heap on documents already published), the
    framework's `expression-bindings` (ADR-080, integrated into main at
    0f210ab: the serializer interns expressions structurally and
    publishes each shared subexpression once in an ordered `bindings`
    table, document version 4; the clock's document is now 32 KB), and
    the viewer's `read-expression-bindings` (ADR-044, viewer API 7).
    The `viewer` extra's version floor is still unpinned, because the
    viewer is unreleased.

## Not framework fixes

- Viewer: `npx vitest` at the `machinome-viewer` root runs a stale copy
  under `build/lib/` that fails on a missing `jokenizer`; the widget's own
  runner is the entry point. Clean or ignore `build/`.
- Viewer: the regenerated `parity-fixture.json` (266 to 421 cases) sits
  uncommitted in `machinome-viewer` and needs its own commit there.
- Shop: the dev-env manifest carries an `exact-geometry` row pointing at an
  old workspace path and a `release-0-5` row with no directory;
  `machinome/WTs/exact-geometry/` is an unregistered leftover checkout.
- Shop: `shop-skills/machinome` and `machinome-api` still let the false
  belief stand that the viewer's expression language has no `min`, `max`,
  `abs` or `floor`; four projects copied a `sqrt` clamp kit on that basis.
  Correct once the cycles are on main.
- Workspace: `cq_gears` is absent from the venv, so `sandbox/gearbox`'s
  own tests cannot run; Sphinx is absent, so the documentation cannot be
  built to check new `.rst`.

## Project follow-ups after integration

Run every project suite with `machinome test --faceted`.

- abacus, fender-bender: commit the uncommitted migrations to the new
  `machinome.math` names (both ran green; abacus's four failures are the
  pilot's own `count` edit).
- pascaline, snappy-reprap (`cable_chain.py`): drop the `sqrt` clamp kit and
  `smooth_min`/`smooth_max` for `clamp01`, `min`, `max`, `wrap`.
- 3DPrintedClocks (four designs): drop the private `OpenSCADConstant`
  `floor`/`min`/`max` wrappers for `machinome.math`; replace the depthing
  functions with `meshed_angle`/`driving_angle` over MrBunsy's references;
  the grasshopper's `nib_position` with `circle_intersection`.
- gearbox: `conjugate_angle` becomes `meshed_angle(theta, z1, z2, alpha,
  180 / z1, 0)`; retire `KinematicAssembly`, which `simulate()` made
  obsolete.
- v8-engine: the three `_at` functions become the crank family.
- kossel: the delta functions become `delta_carriage`/`delta_rod`.
- openflexure, Inmoov: `column_travel`/`elbow_reach` over `screw_travel`,
  `stage_drop`/flexed reach over `link_rise`; `polar` and `rotate_x` from
  `machinome.math`.
- Delete the uncommitted `probe_mechanisms.py` left in gearbox, v8-engine,
  kossel, 3DPrintedClocks, openflexure-microscope and Inmoov-sim.

# Internal-Cycloidal-Actuator (2026-09-06, STEP import cycles)

- Item 5 (per-node tessellation) is fixed and on main (ADR-077, integrated
  with StepNode ADR-078 and import-step ADR-079), with a finding on the way: a stored triangulation only
  partly survives the framework export (Output_Shaft 3.35 MB, not 1.8 MB),
  so the workaround openvmp relies on is weaker than recorded; and the
  BREP had to be written before the STL or the mesher's triangulation
  leaked into it.
- **FIXED (cycle `name-the-missing-file`). `StepNode` (ADR-078) is on main
  too. Finding, not filed as a cycle: a `StepNode` whose `step_source` is
  absent constructs fine and fails later inside `mtime_ns` with a bare
  `FileNotFoundError` naming only the path.** The actuator project calls
  its own `source.require()` at import to keep the extract command in the
  failure. A leaf that validated its declared file at construction, naming
  the class and the path, would be the better failure; `StlNode` has the
  same gap.

  **What shipped.** `StlNode`, `StepNode`, `JScadNode` and `OpenScadNode`
  now each refuse at construction, before anything is read, when their
  declared source file is absent or is a directory rather than a file,
  naming the class, the declaring attribute, its declared value, and the
  resolved absolute path (`machinome/node/sources.py`'s
  `require_source_file`). The actuator's own `source.require()` preamble
  still adds the extract command the framework cannot know, so it is
  untouched and keeps earning its place. No ADR.

## Status (2026-09-06, project refactor pass)

All thirteen designs migrated, each committed in its own repository,
nothing pushed: abacus 98dc357, fender-bender 2a6ac61, pascaline 87b1242,
snappy-reprap 18fd943, kossel b7f4317, v8-engine 3740f6a, openflexure
c077810, Inmoov-sim 20ad316, 3DPrintedClocks 6ec0ff2 (four designs, one
depthing mapping: wheel = driver described by its gap centre, pinion =
driven described by its tooth tip), sandbox/gearbox 4e4efb2 (mesh wrapper
and `KinematicAssembly` retired for `simulate()`). Every snapshot compared
byte- or pixel-identical except fender-bender's intended pulse change.
Probe files deleted. pascaline's `wrap` had a latent edge bug at
-period/2 that the framework's ceil-based `wrap` fixes.

New framework candidates from the pass:

13. **The faceted kernel fails on noise at its default epsilon.** With
    `machinome test --faceted` and no `--volume-epsilon`, interference
    assertions fail on volumes of -2e-14, -4.7e-17, 1e-7 and similar in
    abacus (3 tests), openflexure (4 of 6), fender-bender (4 of 18),
    pascaline (3) and every 3DPrintedClocks design (2-3 each), all
    identical before and after the migration and all green on the exact
    kernel or at the clocks' documented epsilon of 1e-3 mm³. A negative
    volume is not an interference. Candidate fix: treat |volume| below a
    tessellation-scaled floor as zero by default, or make the default
    epsilon nonzero and say so in the summary line.
14. **`machinome snapshot --preview` passes a bare `--preview` to OpenSCAD
    2021.01**, which rejects it with a usage dump
    (`OpenScadRenderer.build_command` emits it unconditionally). Seen in
    3DPrintedClocks.

Project follow-ups still open: gearbox's four test files need a
`node = <Class>` declaration the framework now requires (its two
migration-covering suites ran only under a temporary edit); `cq_gears`
is still absent from the workspace venv; pascaline's package files are
mostly untracked in its repository; Inmoov's `elbow_angle` stays local
(an arcsine over squared reaches, not the law of cosines). Shop
follow-ups: the two shop skills still claim the viewer lacks min/max/
floor; the session scratchpad is shared across parallel agents, and
four of ten clobbered each other's `before.png` (each caught it and
redid the comparison under a distinctive name).
- Phase 4 of the actuator (make-the-actuator-turn) found two more, not
  filed as cycles: (a) an exact Boolean between Output_Shaft and the
  50x65x7 bearing fails in a ~0.18 deg window at exactly 270 deg of input
  (RuntimeError, or a wrong or zero volume) while every other sampled
  angle answers the same constant press-fit volume — a kernel-robustness
  gap at a coincident configuration, recorded in the project as an
  expected failure; (b) no exact minimum-distance assertion exists, so a
  0.05 mm roller clearance had to be measured on a fine private
  tessellation (0.01 mm / 0.1 rad) rather than through the framework's
  spatial contracts, and there is no way to measure an overlap volume
  without asserting on it.
- **FIXED (cycle `honour-skip-and-xfail`, ADR-118). (c) `machinome test`'s
  runner has no skip and no expected-failure concept: it calls each
  method in a loop under a bare `except Exception`, so `self.skipTest()`
  and `@unittest.expectedFailure` both count as plain failures. The
  actuator guards exact-only volume bands with an early `return` and
  records the kernel gap as a canary asserting the wrong value, which is
  the honest equivalent it has; a runner that honoured `SkipTest` and
  expected failures would let a project say these things plainly.**

  **What shipped.** `machinome/manager/test.py`'s runner now classifies
  each animation instant as passed, skipped (`unittest.SkipTest`, raised
  from the method or from `setUp`, or `unittest`'s skip decoration on the
  method or the whole class) or failed, before deciding the method's
  verdict: SKIPPED when every instant skipped, EXPECTED FAILURE when a
  method marked `@unittest.expectedFailure` raised at any instant (no
  traceback printed), UNEXPECTED SUCCESS — which fails the run — when a
  marked method raised at none, and PASSED (saying how many instants
  skipped) otherwise. A skip never overwrites a real failure's
  traceback, and `--failfast` stops only on a real failure or an
  unexpected success. The actuator may now replace its early-`return`
  guards with `skipTest` and its inverted canary with a marked expected
  failure; nothing forces it to.

# AlbertPro (2026-09-07, simulate the Albert quadruped)

Found while building `projects/Robots/AlbertPro/simulation/` directly
from this conversation: an eighteen-body print plate assembled into the
quadruped `RL/dog.xml` describes, driven by the five trained
trajectories the ESP32 replays.

## Framework

- **`self.children` is empty during `simulate()`, and iterating it fails
  silently.** `LowerLeg.simulate()` was written as `for piece in
  self.children: piece.rotate(self.knee.value, AXIS)`. The port was
  bound and correct, the list was empty, the loop applied nothing, and
  nothing raised — the shin simply never turned about its knee, and the
  published model was a robot whose knees did not bend. Every contract
  passed, because a test calls `set_state` before measuring and by then
  the children are linked; only a snapshot showed it. The workaround is
  to address the declared attributes (`self.near`, `self.far`), which
  works in both phases, and that is what
  `projects/Robots/AlbertPro/simulation/leg.py` does. A documented
  empty-during-simulate contract, or a `.children` that raises there
  rather than reading as empty, would turn a silent wrong model into an
  error. This is the one worth filing.

- **A driver's `range` is presentation metadata and nothing enforces
  it.** `height` has a hard geometric range — outside it the machine has
  no pose — and there is no per-driver validator or clamp hook. The
  project guards inside its own `stance_angles()`, which can only act
  when handed a plain number, so the guard fires in tests, snapshots and
  exports but not in the viewer, where a driver is symbolic. Workaround
  in `simulation/layout.py`.

- **No absolute value, min or max in `machinome.math`.** This project
  needs all three symbolically: to clamp a commanded joint angle into
  its declared range (which the MJCF's own `ctrllimited` actuators do,
  and 30% of the published commands need), and to split a two-sided
  slider into its positive and negative halves without a conditional.
  All three are reachable as `|x| = sqrt(x*x)`, `max(a,b) =
  (a+b+|a-b|)/2`, `min(a,b) = (a+b-|a-b|)/2`, so nothing is blocked —
  but every project that needs a clamp will re-derive this. Workaround
  in `simulation/layout.py:clamp`.

- **A deep expression silently loses subexpression sharing.** Summing
  3659 terms left to right built an expression the bindings pass refused
  ("too deeply nested ... published verbatim and unshared"), giving a
  333 KB `viewer.json` with 27 KB unshared expressions. Summing the same
  terms as a balanced tree fixed it completely: no warning, 167 KB, 1656
  shared bindings. The warning is good and said exactly what happened;
  what is missing is that association order is load-bearing for
  published size and viewer cost, which nothing tells you until you hit
  it. Workaround in `simulation/gaits.py:balanced_sum`.

- **There is no `solid import-stl`.** `machinome import-step` scaffolds a
  whole document into declarative source; the equivalent for a
  multi-body mesh pack does not exist, and a pack's inventory is
  reachable only by provoking a build failure. For an eighteen-body
  plate that is enough friction to be worth a committed probe
  (`simulation/tools/probe.py`). Not a blocker — `StlNode`'s `body`
  index and its per-body inventory did the actual job cleanly, and this
  is the smallest of the five.

## Not framework fixes

- `machinome test` needs a node class, so a module that defines only
  constants (`layout.py`, `gaits.py`) cannot carry a companion test
  file. Its contracts live in the root's companion instead. Reasonable
  as it stands; noted because it shapes where a project puts its drift
  tests.
- `sim.every(period, ...)` requires the period to be a whole number of
  `dt` ticks and says so clearly. Correct behaviour, easy to trip over.
- `set_state` refuses a `numpy.float64`, naming the driver and the
  value. Correct and clearly reported.

## Project follow-ups

None open. The change is archived in the project's own
`openspec/changes/archive/`; nothing about AlbertPro is staged here.


# YouCanBuildDog

Simulating James Bruton's `dog02_9g` (51 solids, Fusion/AP214 export)
and then fitting the M3 hardware its bores ask for hit three framework
things worth fixing. None is filed.

- **FIXED (cycle `select-a-step-product`, ADR-115). `StepNode` cannot
  select between products that share a name.**
  `part` is a name, and this export carries **three** products called
  `COMPOUND` — the two chassis halves and the electronics tower, 150 003
  of the machine's 359 786 mm³. The framework refuses correctly and its
  error is excellent, listing all three with distinct bounds, solid
  counts and volumes:

      dog02_9g.stp has 3 products named 'COMPOUND'; the name is
      ambiguous between: ... 7 solids, volume 46025.752 / 4 solids,
      39867.637 / 6 solids, 64813.221

  So they *are* distinguishable — there is simply no way to say which
  one is wanted. A one-based occurrence index alongside `part`, or
  selection by the document entry `StepAssembly` already exposes, would
  close it. Workaround:
  `projects/Robots/YouCanBuildDog/simulation/tools/split_step.py` writes
  one single-product STEP per solid into an ignored directory, which the
  project wanted anyway (see the next paragraph), so the gap cost
  nothing extra here — but a project that only wanted the three
  compounds would have to build the same machinery.
  **What shipped:** `part_index`, a 1-based selector relative to the
  declared `part` name, in document order — not the document entry
  `StepAssembly` exposes, measured unstable across a re-export that
  inserts an unrelated product ahead of the selected ones (ADR-115
  design D1). `StepAssembly.products` now also reports each product's
  own document identity and its `part_index`, and `machinome import-step`
  is keyed on that identity end to end, so two same-named products each
  get their own generated class and selector. Per-solid selection (the
  next paragraph) remains open, unchanged by this fix.

  Worth noting the related shape: an upstream *product* is routinely not
  a printed piece. In this export 20 products hold 51 solids, and two
  toe blocks are filed under a *chassis* product rather than the leg
  they sit on. Per-solid selection — a `machinome` index beside `part`, or a
  `machinome import-step --per-solid` — would be the general answer, and
  would make the framework's own printed-solid unit reachable from a
  STEP document without a project-local splitter.

- **`assertNoDisconnectedSolids` splits each solid's STL rather than
  reading an exact node's solid count.** The API skill says the verdict
  is "the exact geometry's solid count for an exact solid, a split of
  the node's own STL otherwise", but on a tree of 51 exact `StepNode`s
  it went to `cached_base_mesh(solid.stl_file).split(...)`, which
  reaches trimesh's `fill_holes` on a mesh that is not closed, which
  imports `networkx` — absent from the workspace venv:

      ModuleNotFoundError: No module named 'networkx'
      ... trimesh/repair.py:261 in fill_holes
      ... machinome/test.py:1505 in assertNoDisconnectedSolids

  Two things: the exact path looks not to be taken for exact nodes, and
  `networkx` is an undeclared transitive need of the mesh path. The
  project counts face-connected components itself instead
  (`simulation/test_dog.py:test_solid_integrity`), which needs no closed
  mesh and covers all 51 solids including the two the helper cannot
  read. Connectivity does not require watertightness, so the mesh path
  need not go near `fill_holes` at all.

- **An exact intersection returns empty for two solids that plainly
  overlap, and `assertAssemblySupported` silently loses a support edge
  for it.** Fitting the fasteners, the battery holder hangs under the
  lower plate on two countersunk screws driven up into it. Dropped one
  millimetre along gravity the holder demonstrably encloses the screw's
  head, and the framework's support graph should therefore hold the
  holder up. It does not, because `_placed_intersection` takes the exact
  branch for the pair and `intersect_shapes` comes back with zero
  solids. On the same two placed shapes, at the same drop:

      BRepCheck_Analyzer(holder).IsValid()          True
      BRepCheck_Analyzer(screw).IsValid()           True
      BRepExtrema_DistShapeShape(holder, screw)     0.00000
      BRepClass3d_SolidClassifier(holder), a point
        inside the screw head                       TopAbs_IN
      BRepAlgoAPI_Common(holder, screw)             0.00000 mm3
      BRepAlgoAPI_Common(holder, primitive cone
        in the screw's place)                       4.65116 mm3
      BRepAlgoAPI_Common(holder, box there)        16.01830 mm3
      trimesh.boolean.intersection of the two
        placed meshes                               7.41455 mm3

  Every other reading says they overlap; only the boolean of those two
  particular solids says otherwise, and it says so at drops of 0.5, 1,
  1.5, 2 and 3 mm alike. The screw is a `CadQueryNode` built by a loft
  and two unions, the holder a `StepNode` from the export; the same
  screw class intersects three other STEP solids in this machine
  correctly, so it is the pair rather than either shape.

  It matters because the exact branch is *chosen* for exact/exact pairs
  and a missing verdict there is indistinguishable from "no contact":
  the assertion reports a solid unsupported and gives no hint that a
  boolean failed. A cross-check against the mesh branch when the exact
  one reports empty but the two placed bounds overlap would have caught
  it. The project works around it by declaring the battery's hold
  through `supports=`, which is honest but hides a kernel failure behind
  a modelling exemption.

  Reproduction is in
  `projects/Robots/YouCanBuildDog`; the scripts that produced the table
  above are throwaway, but the pair is
  `moving.battery.holder` and `moving.battery_fore` at rest with the
  drivers zeroed.

## Environment

- `networkx` is missing from the workspace `.venv`, and trimesh needs it
  for `fill_holes`. Anything that reaches trimesh's repair path — the
  connectivity assertion above, `mesh.is_volume`, `mesh.split` on an
  open mesh — raises `ModuleNotFoundError` rather than a mesh verdict.
  Your call whether to add it; I did not touch the shared venv.

## Not framework fixes

- `assertAssemblySupported` on the exact kernel gave exactly the right
  answer for this machine — nothing above the feet is supported —
  because the export draws no fasteners at all. The framework is not at
  fault; the CAD is. On the faceted kernel it refuses first, on the
  export's two non-manifold tower panels, which is also correct.
- Six pairs in this export are drawn in exact face contact, so their
  exact booleans return 0 at some states and slivers of 1e-16 to 1e-13
  mm³ at others, flipping with nothing but transform composition order.
  That is coincident-face geometry behaving as coincident-face geometry
  does; the project holds those pairs below a stated floating-point
  floor and records the missing clearance as a design finding.
- The test runner aliases the node under test onto the snake-case of the
  test class name, so a class called `LegTest` silently shadows a
  `leg()` helper on the same class with the node itself
  (`TypeError: 'Dog' object is not callable`). Documented behaviour,
  easy to trip over; renaming the class fixed it.
- The runner collects the `TestCase` classes a companion module
  *defines*, not the ones it imports. A suite split across files has to
  mix contracts in rather than import assembled test classes, or they
  run silently as zero tests — which is how nine leg contracts sat
  unexecuted here until the count looked wrong.

## Project follow-ups

- The `standing-stance` support requirement was met on 2026-09-07 by the
  `fasten-the-dog` change: thirty M3 screws read off the export's own
  bores, and `assertAssemblySupported` now proves the moving half —
  plate, brackets, both legs, battery and its own six fasteners — both
  reachable and in frictionless static equilibrium. Over the whole
  machine it reaches 99 of 101 solids; the two it does not are the
  tower's shelves, which the export draws attached to nothing. That
  residue is the design's, not the model's, and is recorded as its own
  contract rather than papered over.
- `dog02_large` is unmodelled: its export fuses each whole leg into one
  product of eight solids, so the hip cannot be articulated without
  cutting upstream geometry.
- The design findings (a stale back-left leg, no fasteners, no running
  clearance, two non-manifold panels) are in the project's README and
  its archived change. Telling James Bruton is your call; I have not
  contacted anyone.

# 3DPrintedClocks (2026-09-07, shared simulation package)

- No public way to give a declared child an instance-specific tree name.
  Mantel clock 34's `TrainArbor` (one class, six instances) set
  `part.name` and the private `_explicit_name` on its `wheel` and `rod`
  children so the viewer tree and interference failures said which wheel
  was which. The refactor dropped the private and relies on the hierarchy
  (`train.centre.wheel`); an interference failure still names the leaf
  only (`wheel should not interfere with wheel`). A public per-instance
  name, or failure messages that print the qualified path, would close
  it.

# Robots/Thor (2026-09-07, full simulation with fasteners)

507 printed and bought solids, six joints and a gripper, every part exact.
Four framework findings, each met while building it and worked around in
the project rather than fixed there.

- **`assertNoDisconnectedSolids` answers on the STL even when the node is
  exact.** `Art1Top` is a single solid of 530398.4 mm³ — `len(shape.Solids())
  == 1` — and its 0.1 mm tessellation splits into five bodies: the part,
  three two-triangle patches of zero volume and 5.0 × 23.4 in extent, and a
  detached lug of 3220.9 mm³. The assertion reports "5 connected bodies"
  for a part whose B-rep is one, and there is no way to ask it for the
  exact answer. The exact answer is the cheaper one, too: no tessellation,
  no mesh engine.

  The project's `test_solid_integrity` walks the tree itself and counts
  `Solids()` per exact leaf (`simulation/test_thor.py`), which is the
  question the assertion is named for. Reproduction: `Art1Top` in
  `projects/Robots/Thor/step/`.

- **The faceted kernel raises instead of answering, and one bad mesh takes
  the whole run with it.** Seven of Thor's parts tessellate non-manifold
  (`Art1Body`, `Art1Top`, `Art1GearMotor`, `Art2BodyB`, `Art2MotorGear`,
  `Art3Body`, `Art4BodyBot`); their exact geometry is sound. Every faceted
  comparison touching one of them raises

      ValueError: ... the mesh engine refuses this mesh (NotManifold)

  so `machinome test --faceted` cannot run this machine at all — not "reports
  a worse verdict", cannot run. Six of twenty-eight contracts died on it,
  including both integrity contracts, before any of them compared
  anything. The faceted kernel is the loop kernel the craft skill asks for,
  and a machine assembled from vendor STEP is exactly where it is most
  wanted.

  A verdict of "cannot decide this pair" that the assertion could report
  and skip, or a per-pair fallback to the exact branch, would leave the
  other 493 solids testable. The project runs exact for both the loop and
  the certification, which is affordable here (194 s) only because of the
  next item.

- **There is no public way to ask which pairs of an assembly interfere,
  and by how much.** `assertNoSolidInterference` raises on the first pair
  it finds. A machine whose own design overlaps — this one, and every
  simulated upstream so far — needs the whole set, because the honest
  contract is an inventory of the overlaps the design has, not "none".

  Writing that walk by hand is a trap: `projects/Robots/Thor`'s first
  version composed placements and culled bounds itself and took **over an
  hour** for one pose, where the framework's own path takes **116 seconds**
  for the same 507 solids. `simulation/seats.py` therefore imports
  `_placed_assembly_solids`, `_bounds_candidates` and
  `_candidate_intersection` — three private names — and says so in its
  docstring. A public `solid_interference(node)` returning the pairs and
  volumes, with `assertNoSolidInterference` built on it, would make the
  inventory pattern first-class instead of a raid on the internals. It
  would also let it follow the run's kernel, which the hand-rolled version
  could not.

  Related: neither the assertion nor the pair helpers can name a solid by
  its path. `seats.qualified_names()` walks the tree to build
  `{id(node): 'shoulder.art2.art3.art4.art56.gt2x40_pulley_1'}`, because
  `solid.name` is `gt2x40_pulley_1` and this machine has two. Same gap as
  the 3DPrintedClocks entry above, from the other side.

- **FIXED (cycle `import-the-artifact-by-path`, ADR-116). A leaf's
  artifact is imported into its parent's `.scad` by bare filename, so an
  assembly in a different Python package renders it as nothing —
  silently.** Artifacts live under `_build/<package path>/`. An
  assembly in `simulation/tools/` holding a `MolejoNode` declared in
  `simulation/` emitted

      union() {
        color(...) { import(file = "flexibles-ElbowBelt-...stl", ...); }
        import(file = "beltview-Disc,...stl", ...);
      }

  from `_build/simulation/tools/`, where the belt's STL does not exist —
  it is in `_build/simulation/`. OpenSCAD renders the discs and no belt,
  with no error, and `machinome snapshot` reports success. I lost a snapshot
  cycle to a belt I thought was broken.

  Observed with a molejo leaf; nothing about it looks specific to
  flexibles, since the import is written the same way for every leaf.
  Reproduction: put an `AssemblyNode` under `simulation/tools/` whose
  children include a node class defined in `simulation/`, and snapshot it.
  Moving the assembly beside the leaf fixes it, which is why
  `projects/Robots/Thor` has no belt-viewing helper under `tools/`.

  **What shipped.** Every framework-emitted import is now anchored on the
  build directory and re-anchored onto a node's own build directory only
  when that node writes its own `.scad` (ADR-116) — the same rule for
  every leaf kind, not only the flexible one this finding observed.
  Measuring it surfaced the same bug from the other side: an
  intermediate assembly several packages below the root held a path
  anchored on the ROOT's build directory, not its own, and was fixed by
  the same change. `projects/Robots/Thor` can put its belt-viewing
  helper back under `tools/`, though no project source change is
  required.

## Environment

- `networkx` — the missing package recorded under YouCanBuildDog above —
  is now installed in the workspace `.venv` (3.6.1, `pip install --no-deps`
  so nothing else moved). `assertNoDisconnectedSolids` reaches a verdict
  again rather than raising `ModuleNotFoundError`. I installed it; say if
  you would rather it came out.

## Not framework fixes

- A `clear_state()` inside a test helper un-binds the declared driver
  defaults for the rest of the run: the runner binds them once before the
  first render, and the next test's `set_keyframe(0)` then renders with no
  drivers bound and raises `driver 'art1' ... is not bound`. Documented
  behaviour — state merges, and clearing clears — but the failure surfaces
  in a later test, in framework code, naming a driver the later test never
  touched. Every contract here names every driver instead.
- `machinome test <file.py>` on a companion test module maps to the node file
  of the same name, so a pure measurement suite with no node class
  (`test_layout.py` → `layout.py`) fails with `No node class found`. Those
  two suites run under pytest. This is the bare-path item already fixed for
  `openvmp` seen from the other end: the mapping is right, there is just no
  way to say "this test file has no node".

# science-jubilee (2026-09-08)

- Exact OCCT intersection reports a `BRepAlgoAPI` not-done operation for at
  least one valid threaded-ball/fastener pair imported from
  `sonicator_tool_assembly.STEP`. Both leaves are valid exact shapes and
  publish as single watertight bodies, but the exact operation cannot produce
  the source assembly's required seat inventory. The project therefore
  measures the exact pair set on machinome's published meshes with the
  manifold boolean engine in `simulation/seats.py`; `machinome test --exact`
  still covers exact source evaluation and placement. Candidate wart, not
  filed: expose an explicit indeterminate pair verdict or a supported
  exact-to-faceted fallback for interference inventory contracts.

# 3DPrintedClocks wall clock 01 and Thor (2026-09-09, motion layer refactors)

Found while moving the two originating projects onto `machinome.motion`
(cycles `motion-package`, `joints`, `couplings`, branch `motion`). Poses
were bit-identical before and after in both projects.

- **A joint cannot be anchored at a design-placed part's own origin.**
  `resolve_declared_joints()` runs in `AbstractBaseNode.__init__`, before
  the parent's `render()` has placed the node, so a joint's `at` has no
  way to say "the line through this part's own placed origin". Thor's
  thirteen catalogue parts that spin on their own bearings (pinions,
  pulleys, optodisk, ball cage, bevels) therefore keep one hand-written
  `rotate` each with the sign from `placing.axis_sign`; every sub-assembly
  freedom became a joint. Candidate fix: an anchor mode meaning the node's
  own placed origin (resolved at first bind from the rest placement), or
  lazy resolution of joint arguments at first bind with the eager pass
  kept for tokens and callables that do not touch the placement.

  **Still OPEN after `orbit-joint` (ADR-094).** That cycle gave the
  own-placed-origin mode to ONE argument of ONE joint — an `Orbit`'s
  `carries`, whose default is the body's own placed origin, settled at
  the first binding and costing nothing because in the body's own frame
  that point is exactly the origin. It does NOT give `Revolute`'s `at`
  the same mode: an anchor has to be carried through the inverse of the
  rest placement, which is a different answer, and Thor's thirteen parts
  need it at realization time. This finding is unchanged.
- **FIXED (cycle `whole-tree-fixpoint`, ADR-099). A relation chain must
  be stated in one class body.** Relations are
  solved per instance at the end of its own simulate phase, and a child's
  relations solve after its parent's. Clock 01 binds `escape.turn` in
  `Movement.simulate()`; stating `centre.drives(third)` inside `Train`
  while `power.drives(train.centre)` stays in `Movement` is refused with
  `UnreachedCoordinate` at `Movement`'s end, because `Train`'s relations
  have not run yet. The message names both ends, so the constraint is
  visible, but it forces every chain into the class that binds its known
  end. Candidate fix: let a parent's fixpoint defer an unreached relation
  until its descendants have solved, then re-run once.
  **What shipped:** exactly the candidate fix — an unresolved relation
  defers to the enumeration's own whole-tree fixpoint, resolved once
  every assembly's phase has run, and refused only then. Proven on this
  exact shape
  (`tests/test_couplings.py::TreeFixpointTest::test_a_chain_stated_one_level_down_solves`).
  Wall clock 01's own two-arbor chain (task 9.4 of the change) is NOT
  proven here: 3DPrintedClocks' working tree was under the pilot's own
  session throughout this implementation, and the overlay is left for a
  follow-up that can read it.
- **FIXED (cycle `whole-tree-fixpoint`, ADR-099). A node's own derived
  coordinate is unbound inside its own `simulate()`.** `clear_solved()`
  runs before the author's `simulate()`
  and the fixpoint after it, so `Art4.left = art56.wrist + 2 * tool` reads
  as an unbound slot in `Art4.simulate()` and a hand-written rotate from it
  silently turns nothing (Thor's two motor pulleys, caught by the pose
  comparison). Coordinates bound by an ancestor's relation are fine.
  Candidate fix: refuse the read by name rather than yield an empty slot,
  or state the two-phase order in the read's error.
  **What shipped:** the read is recorded while it is unbound and judged
  at the end of the enumeration by what actually bound the coordinate
  afterward — a relation, a derived formula or a wiring: refused, naming
  both classes and the two-phase order. Bound afterward by the reading
  class's OWN `simulate()` instead: not refused, which is the ordinary
  rest-default guard and stays exactly as unremarkable as it was.
  Proven on Thor's own shape
  (`tests/test_couplings.py::ReadRefusalTest::test_a_class_reading_its_own_derived_coordinate_is_refused`).
- Thor's exact suite has two failures that pre-exist this work on this
  framework tree (`seats.assert_inventory`: 260 of 272 overlapping pairs
  not in the seats inventory, in `test_assembly_integrity` and the
  scenario test); byte-identical with the unrefactored model, and the
  same 29/2 on the primary checkout at main cb474e3 with Thor's committed
  code, so it predates the motion branch (an exact-boolean or seats change
  since Thor's last green run, not investigated here).

# Motion catalogue refactor (2026-09-09, every project onto `machinome.motion`)

Found while moving the rest of the project catalogue onto joints and
couplings after the ports move broke every unmigrated import. Tracker:
`machinome-studio/docs/motion-general-refactor.md`. Pilot's rule for this
campaign: a missing primitive defers the project and is recorded here first,
with the sentence the project wants to write, so the primitive is built
before the project is refactored around its absence.

- **A joint's axis and anchor belong to the declaration site as often as
  to the class.** Two more sightings of the first 2026-09-09 finding, from
  the opposite side: not a design-placed part whose origin is unknown, but
  a shared or catalogue class whose placement is the PARENT's knowledge.
  Poseidon's `ThreadedRod` and `ShaftCoupling` are bought-hardware
  envelopes; to turn on the drive axis each must now carry
  `turn = Revolute(axis=(1, 0, 0), at=(LEADSCREW_START_X, *DRIVE_AXIS_YZ))`
  with the pump's layout constants inside the hardware module, even though
  both anchors are exactly the rods' own placed origins.
  OpenMANIPULATOR-X's seven mesh packs share one `VisualPack` class; the two
  gripper fingers slide on mirrored axes, so the project needs two
  three-line subclasses whose only content is one `Prismatic` each, and
  every arm link writes its URDF origin twice — in the parent's
  `render().translate()` and again as the joint's `at`. The sentences the
  projects want:

      leadscrew = ThreadedRod(turn=Revolute(axis=(1, 0, 0), at=(LEADSCREW_START_X, *DRIVE_AXIS_YZ)))
      left_finger = VisualPack('gripper_left_palm.stl', travel=Prismatic(axis=(0, 1, 0), range=(-11, 20), unit='mm'))
      base_yaw = Revolute(axis=(0, 0, 1), unit='deg')      # anchored at my own placed origin, no `at`

  Neither project is deferred: the motion is fully stated either way, and
  the cost is duplication and ceremony, not hand-written motion. Candidate
  fixes, complementary: (a) the own-placed-origin anchor mode already
  proposed above, which removes every `at` that repeats the parent's
  translate; (b) a joint passed as a declaration keyword, resolved on the
  child like a wiring is today but declaring a freedom rather than binding
  one, so a shared class can be given a joint where it is placed.

- **FIXED (cycle `joint-composition-order`, ADR-093). Two joints on one
  body compose in binding order, which a relation cannot see.** OpenCycloid's cycloidal disks orbit the main axis at the
  eccentric radius while spinning at the reduced rate about their own
  centre: `R(in)·T(d)·R(out−in)`. Two `Revolute` joints on the disk state
  it — `orbit` about the parent's axis and `spin` about the disk's own
  placed origin — but the pose is right only when `spin` is applied inside
  `orbit`, and the joints spec composes joint motion in the order the
  coordinates were BOUND. Bound by relations, that is the solver's pass
  order, which the couplings spec fixes as declaration order within a pass
  but which a reader of the class cannot see and a derived coordinate
  would silently change. The sentences the project wants, either:

      orbit = Orbit(axis=(0, 0, 1), radius=ECCENTRIC_RADIUS, phase=-90.0, unit='deg')
      eccentric_shaft.spin.drives(stage_one.orbit)
      eccentric_shaft.spin.drives(stage_one.spin, ratio=-1.0 / REDUCTION)

  (a carried body whose attitude the orbit leaves alone, so the spin is
  absolute and the `-1` term vanishes), or a stated contract that the
  joints of one class compose in their DECLARATION order, innermost first,
  whatever order they are bound in. OpenCycloid is deferred at stage A
  until one exists.

  The second form is now the contract: the joints declared on one class
  compose in declaration order, innermost first, whatever order they are
  bound in (ADR-093, cycle `joint-composition-order`). **The first form
  is now the contract too** (ADR-094, cycle `orbit-joint`): `Orbit` is
  built, and OpenCycloid writes `spin` first and then
  `orbit = Orbit(axis=(0, 0, 1), unit='deg')` with no `carries` at all —
  its plan moves the eccentricity into the rest placement, so the disk's
  own placed origin IS the eccentric centre and the DEFAULT carried point
  derives both the `ECCENTRIC_RADIUS = 2.5` and the `-90.0` phase the
  sentence above typed. The `- 1.0` in `ratio=-1.0 / REDUCTION - 1.0`
  goes with them. OpenCycloid still waits on ONE finding: the fan-out
  over a repeated child below. Its deferral stands on that alone.
- **A relation cannot fan out over a repeated child.** The same actuator's
  four eccentric bearings and six output pins are `.repeat()` children with
  a per-copy sign or phase; the couplings spec refuses a path through a
  repeated declaration and advises stating the relation inside the repeated
  class, which cannot read the parent's coordinate. They stay bound in a
  `for` loop in `simulate()`. Wanted:

      eccentric_bearings = RadialBearing(...).repeat(4, orbit=eccentric_shaft.spin)
      eccentric_shaft.spin.drives(eccentric_bearings.orbit, law=per_copy_sign)

  where the law is handed the copy (its index) as the driven node. Second
  reason OpenCycloid is deferred.

  **FIXED (cycle `repeat-fan-out`, ADR-096).** A relation whose DRIVEN end
  passes through a repeated child now resolves to one relation per
  realized copy, `law=` called once per copy with the copy as its second
  argument, so `eccentric_shaft.spin.drives(eccentric_bearings.orbit,
  law=per_copy_sign)` states it in one line and `per_copy_sign` reads the
  copy's own `index` with no new argument. No `.repeat(n, orbit=...)`
  keyword was built: an identity wiring over a repeat already worked
  (measured, `evidence/probe_wiring_repeat.py`), and what it could not do
  — take its source from a path — is exactly what a broadcast relation
  states. OpenCycloid becomes refactorable at stage B in its own
  repository's own cycle; nothing in the framework waits on it.
- **FIXED (cycle `whole-tree-fixpoint`, ADR-099). Two smaller sightings
  from OpenTorque (planetary reducer, not
  deferred).** (a) The one-class-body rule again: the root cannot say
  `reducer.planet_1.orbit.drives(output_stack.planet_carrier_b.turn)`
  because the reducer's own relations have not run when the root solves,
  so the 1:8 carrier ratio is stated twice from one constant, once in the
  reducer and once at the root. (b) Relations are additive through
  inheritance, so a preview subclass that wants the same coordinate driven
  from a different source (`motor_rotor.spin = input_angle + 360 * time`)
  cannot restate the base's relation; the base binds the rotor in one
  `simulate()` line instead of stating `input_angle.drives(motor_rotor.spin)`.
  Wanted: a subclass may replace a NAMED relation of its base, the way a
  redeclared port wins.
  **What shipped:** (a) is the same whole-tree fixpoint as the two
  entries above. (b) is exactly
  the wanted mechanism: a subclass assigning a relation to a name a base
  already used REPLACES it, at the base's position in the enumeration
  (the rule a redeclared joint already obeys, ADR-093); a bare statement,
  or a name no base used, stays additive. Proven directly, on OpenTorque's
  own two-relation shape, as a unit test
  (`tests/test_couplings.py::SubclassReplacesRelationTest`). An overlay
  proving BOTH (a) and (b) on OpenTorque's own project code (task 9.6 of
  the change) is NOT proven here, deferred for time; the project's own
  base-against-head pose comparison, unmodified, is 0.000e+00
  (`evidence.md` §9).
- **FIXED for the composition half (cycle `joint-composition-order`,
  ADR-093). A floating body's attitude is the same composition gap, from
  the other side.** The hexapod's chassis has four freedoms against the
  ground — roll, pitch, yaw, lift — and its inverse kinematics hand-invert
  exactly `R_roll · R_pitch · R_yaw · T_height`. Four joints on the chassis
  would put that composition at the mercy of binding order. Wanted:

      class Chassis(AssemblyNode):
          roll  = Revolute(axis=(1, 0, 0), unit='deg')
          pitch = Revolute(axis=(0, 1, 0), unit='deg')
          yaw   = Revolute(axis=(0, 0, 1), unit='deg')
          lift  = Prismatic(axis=(0, 0, 1), unit='mm')

  composed innermost-first in DECLARATION order whatever order the
  coordinates are bound in — or the `Free` joint the design note listed
  for later. Second sighting of the OpenCycloid finding; the hexapod is
  deferred at stage A on it, so one primitive unblocks both. Its eighteen
  leg joints are statable today and wait with it.

  The four-declaration form above is exactly what the contract now
  guarantees, so the hexapod is unblocked by ADR-093.

  **FIXED, the other half too (cycle `free-joint`, ADR-095).** `Free` is
  now a declaration: `pose = Free(angle_unit='deg', length_unit='mm')`,
  one joint owning six coordinates reached as `chassis.pose.roll` …
  `chassis.pose.z` and reported by the port enumerator under those dotted
  names, composing `R(roll) · R(pitch) · R(yaw) · T(x, y, z)` innermost
  first — the product `Chassis._to_chassis` hand-inverts, measured
  against the hexapod's own four calls at seven poses before the cycle
  was written. The chassis binds four of the six and the other two place
  nothing. The refactor itself is the project's own stage B, in its own
  repository; nothing in the framework waits on it.
- **Fan-out over a repeated child, second sighting: the abacus.** Each
  column's five beads are one `Bead` class repeated; the heaven bead is
  one relation with a clamp law, but the four earth beads each need the
  column's `earth` value clamped against their own rank in the stack, so
  the law must read the copy's index. Wanted:

      earth.drives(earth_beads.travel, law=earth_lift)   # law(column, bead) reads bead.index

  With the relation refused through `.repeat()`, all four stay bound in
  a loop in `Column.simulate()` and a joints-only refactor would be
  cosmetic; the abacus is deferred at stage A on the same primitive as
  OpenCycloid's bearings and pins.

  **FIXED (cycle `repeat-fan-out`, ADR-096), the same primitive as
  OpenCycloid's.** `earth.drives(earth_beads.travel, law=earth_lift)`
  now states it in one line, and `earth_lift(column, bead)` reads
  `bead.index` for the rank — the abacus's own real shape
  (`FrameHalf(count=count, ...).repeat(2)`, where `FrameHalf` declares a
  `count` of its own) is what decided the copy carries `index` and not
  `count`. The abacus becomes refactorable at stage B in its own
  repository's own cycle.
- **A carried body: the orbit primitive, second sighting.** YouCanBuildDog's
  five lower-leg parts per leg translate by `R(θ)·s − s` with their
  attitude fixed — one coordinate, but not one coordinate on one axis.
  With the API as it stands each would need two prismatics and two trig
  laws with no inverse (forty joints and forty laws for four freedoms).
  Wanted, exactly OpenCycloid's:

      carried = Orbit(axis=(1, 0, 0), radius=40.0, phase=-55.0, unit='deg')
      swing.drives(carried.orbit)

  The dog's `MovingHalf` also turns about the joint centre and slides
  along the channel — two joints on one body whose order matters
  (`T(slide)·R(turn)`), the third sighting of the composition-order gap.
  Deferred at stage A on both. **That third sighting is FIXED** (cycle
  `joint-composition-order`, ADR-093): `pivot` declared before `slide`
  now composes `T(slide)·R(turn)` whatever binds them. The carried
  lower-leg parts still want `Orbit`, which is NOT built, so
  YouCanBuildDog's deferral stood on the orbit finding alone.

  **FIXED (cycle `orbit-joint`, ADR-094).** `Orbit` is built, and it
  takes neither a radius nor a phase: the dog writes
  `carry = Orbit(axis=(1, 0, 0), at=(0, *SHORT_PIVOT),
  carries=(0, *KNEE_PIVOT), unit='deg')`, and the framework derives the
  per-leg 40.0000 and 39.9239 mm and the -55.000 and -55.1033 degrees
  from the two pivot positions `layout.LINK_SPANS` already measures —
  the 0.076 mm short back-left leg included, and its phase corrected
  from the -55.104 the project's proposal typed. The default carried
  point is not enough here: five bodies per leg, five rest placements,
  one shared offset, so the knee pivot is named. YouCanBuildDog now
  waits on nothing and becomes refactorable at stage B.
- **A path on one body, per repeated copy: fender-bender's bracket
  release.** One freedom, `lift`, realized as `T(dx, dz, 0)·Rz(-tilt)` in
  each channel's own frame from nine measured waypoints, on five channels
  held by `.repeat()`. It hits three of the findings above at once —
  several joints composing on one body, an anchor at the copy's own
  placed origin (`channel_y(index)`), and a relation fanning out over a
  repeated child with a per-copy law. Wanted, either three joints with a
  stated composition order, or

      release = Path(RELEASE_WAYPOINTS, at=OWN_PLACED_ORIGIN, unit='mm')

  Deferred at stage A. The two motions the API states today — the
  filament wheel's spin and the lock pin's draw — wait with it; the
  loop's `drop` port feeds molejo geometry and is not a forwarder.
  One of its three blockers is gone — several joints on one body now
  compose in declaration order (ADR-093) — and a second is now gone too:
  **FIXED (cycle `repeat-fan-out`, ADR-096)**, the per-copy fan-out over
  `.repeat()`. The own-placed-origin anchor is the one blocker still
  untouched, so fender-bender's deferral stands on it alone.
- **A joint on a child built from data, not from a class body.** OpenVMP
  Don1's links realize their parts in a loop from PartCAD `.assy`
  blueprints, one generic `StepPart` per entry named by the file. A joint
  is class metadata and a relation path is checked against declared
  children, so none of the 82 drive-train parts that visibly turn — worms,
  worm gears, shafts, sprockets — can carry a joint or be reached by a
  relation; nine `spin()` call sites stay hand-written, each with its own
  frame inversion. Wanted:

      front.yaw.drives(base['motion-front-wormgear/worm'].spin, ratio=WORM_GEAR_TEETH)

  a joint declared on a child a parent realized from data, and a relation
  that can reach it by name. The 24 declared freedoms are statable today,
  so the project proceeds; this is transmission, not dressing, and a
  later primitive adds to the refactor rather than redoing it. The same
  project is the fourth sighting of the declaration-site joint: two `Link`
  subclasses exist only to carry a joint, and `CameraArm` needs callables
  because its anchor's sign is the PARENT's handedness times its own.
- **FIXED (cycle `multi-source-multi-target-laws`, ADR-100). A relation
  reads one coordinate; the Pascaline's pawl reads two.**
  The pawl's swing is `PAWL_DEFLECTION * (climbing(count) + ratchet(next_count) * (1 - pushing(count)))`,
  bilinear in this digit's drum and the next one's. Wanted:

      (count, next_count).drives(sautoir.pawl.swing, law=pawl_deflection)

  a relation with several sources, its law handed all of them. **Stated
  as `(count & next_count).drives(sautoir.pawl.swing, law=pawl_deflection)`**
  — `&` rather than the tuple the finding wrote, because a tuple display
  cannot be given a `.drives` (measured, `probe_today.py`); proved on a
  read-only overlay at maximum deviation 0 over 27 poses
  (`multi-source-multi-target-laws/evidence.md`, task 7.2). `next_count`'s
  "built on its own" default moves from a local variable in
  `Digit.simulate()` to the port itself, because a multi-source relation
  has no partial application. Not yet applied in the project's own
  repository — that is its own next stage B, in its own cycle. The same
  machine adds the sharpest own-placed-origin sighting yet — `Pawl.swing`'s
  anchor must re-evaluate the `profiles.hinge(...)` formula
  `Sautoir.render()` already computed — and a fan-out over LIST-HELD
  children where each copy gets a structurally different expression (the
  root's eight-way carry binding), which no single per-copy law would
  state either: BOTH stay open, untouched by this fix.
- **FIXED (cycle `joint-composition-order`, ADR-093). Composition order,
  fourth sighting, and the minimal unblocker.** The
  Internal Cycloidal Actuator's two disks each want `orbit` (about the
  drive axis, 1:1 with the eccentric shaft) and `spin` (about their own
  bore, `ratio=-1/8` with a mesh-phase offset) on ONE body: the tree is
  `machinome import-step` output mirroring the document one-for-one, so there
  is no carrier body to hang the orbit on and inventing one would break
  the one-to-one reading and sixteen tests. It is blocked on the
  composition-order contract alone — joints of one class compose in
  declaration order, innermost first — which is therefore the smallest
  primitive that unblocks it, OpenCycloid and the hexapod at once. Its
  preferred `Orbit` form, if one is built, anchors the carried point
  (`Orbit(axis, at=<carried point>)`) rather than taking a radius and a
  phase, because the eccentricity is a derived value there.

  The contract exists: `spin` declared before `orbit` is applied inside
  it, whatever order the two relations solve in. This project is
  unblocked by ADR-093 alone and is the sighting that named it the
  minimal unblocker. Its `Orbit` preference was an open want, not a
  blocker.

  **That want is now FILLED (cycle `orbit-joint`, ADR-094)**, with one
  keyword renamed: the carried point is `carries=`, not `at=`, because
  `at` may not mean the line for a `Revolute` and the carried point for
  an `Orbit` — so the disk reads
  `spin = Revolute(axis=(0, 1, 0), at=DISK_1_BORE_CENTRE)` then
  `orbit = Orbit(axis=(0, 1, 0), carries=DISK_1_BORE_CENTRE)`, `at`
  keeping its default because the actuator axis runs through the parent's
  origin. Nothing is typed that the project's spec forbids: the 2.000 mm
  eccentricity and the -79.0959 degree phase are derived from the bore
  centre and the axis. The project's own algebraic identity between that
  form and today's `_simulate_disk()` is a framework fixture
  (`tests/test_joints.py::ProjectAlgebraTest`), measured at a rotation
  deviation of exactly 0 and a position deviation of 4.4e-16 mm. Its
  proposal lists `orbit` before `spin`, which was written before ADR-093
  fixed first-declared-innermost: at stage B the two transpose.
- **FIXED for the composition half (cycle `joint-composition-order`,
  ADR-093). Composition order, fifth sighting: a delta printer's rods.** The Mini
  Kossel's six rods each hang between a carriage and the effector; a rod's
  pose is a spin, a lean, a swing and a rise — four joints on one body
  whose order is the whole of its attitude and which a reader of the class
  cannot see. The effector's three prismatics commute and the carriages
  and pulleys are one joint each, so the composition contract is again the
  one thing missing; the delta law itself (three drivers to each rod) is
  the multi-source relation already recorded. Deferred at stage A.
  The four joints on one rod now compose in declaration order (ADR-093);
  the multi-source relation the delta law needs is a SEPARATE finding.

  **FIXED (cycle `multi-source-multi-target-laws`, ADR-100).** The delta
  law is now exactly two sentences —
  `(x & y & z).drives((rods.spin, rods.lean, rods.swing, rods.rise), law=delta_rod)`
  and `(x & y & z).drives(towers.height, law=delta_carriage_law)` — proved
  on a read-only overlay against the project's own stage-A pose capture
  at maximum deviation 0 over 11 poses, 378 leaves
  (`multi-source-multi-target-laws/evidence.md`, task 7.1: "the sentence
  the cycle exists for"). Not yet applied in the project's own
  repository; kossel's stage B is its own cycle there, both composition
  order and this now unblocked.
- **A bare number cannot be added to a dimensioned token.** The
  Pascaline's slide span, `CHANNEL_Y[1] - CHANNEL_Y[0] - SLIDE_WIDTH - 2 * clearance`
  with `clearance` a declared `Length`, is refused at class definition
  (`DimensionError: 27.0 is dimensionless and <L> is L`): the parameter
  algebra lets a number MULTIPLY a token but not add to or subtract from
  one, so a layout constant in millimetres must be wrapped as
  `Length(...)` before it meets a token. Met writing a `ratio=` and a
  joint `range=`; not a motion-layer gap but the first time the algebra
  was asked this in a class body rather than in `render()`.
- **Declaration-site joint, sharpest form: the Prusa i3's Z screws.** Each
  screw's anchor is `(±17, 0, 0)` by the PARENT's `left` flag, so neither
  an own-placed-origin mode nor a callable of the realized child can
  state it, and giving `ZScrew` a parameter for it would mint a second
  cached exact ISO thread. The two screws keep a port and one `rotate`
  each. Wanted, as before: `screw = ZScrew(turn=Revolute(axis=(0, 0, 1), at=(side * 17, 0, 0)))`
  resolved against the declaring parent's parameters.

  **CORRECTED (cycle `joint-frame-follows-declarer`, ADR-097).** This
  entry's claim that no recorded candidate fix reaches the Z screws was
  wrong once the frame itself is the fix rather than a mode within it.
  `ZScrew` is drawn along its own `+Z` from its own origin and each side
  is placed by a pure `translate([±17, 0, 75])`; under the new rule
  `turn = Revolute(axis=(0, 0, 1), unit='deg')`, own-frame, no anchor at
  all, states BOTH sides with one declaration — the project's own
  reviewed proposal already conceded the own-origin mode "would" reach
  this case, and the survey confirms it. The declaration-site keyword
  below is still wanted for the five axes decision 3 of that cycle
  found, which this Z-screw case is not one of.
- **OpenFlexure: two lighter sightings.** (a) Fan-out over `.repeat()`
  with the IDENTITY law: the three stage nuts and the gear lock screws
  simply follow one coordinate each, so a `.repeat(n, travel=column.travel)`
  wiring would do without any per-copy law — the weakest form of the
  fan-out finding, worth building first.

  **FIXED (cycle `repeat-fan-out`, ADR-096).** Measured, not assumed:
  `Bead(travel=earth).repeat(4)` already binds every copy through the
  existing per-instance wiring mechanism
  (`evidence/probe_wiring_repeat.py`), because a wiring is downward-only
  and needs no PATH for its source — `shaft_pin.turn.drives(gear_screws.orbit)`
  is the case a wiring cannot state, and it is exactly a broadcast
  relation with the default ratio of one. No `.repeat(n, travel=...)`
  keyword was built; it would have given the identity case a second
  spelling and the path case nothing. (b) The third 2026-09-09 limit
  again: a coordinate a class's own relation binds is unbound inside that
  class's own `simulate()`, which forced the actuator's thread ratio up
  one level into `Axis`. The four flexure legs (two rotations each, on
  repeated bodies, from a multi-source law) stay hand-written as
  followers; the principal chains are statable and the project proceeds.

  **FIXED (cycle `multi-source-multi-target-laws`, ADR-100).** The four
  flexure legs' two rotations now come from one two-source,
  two-driven-end law per repeat —
  `(stage.slide_x & stage.slide_y).drives((driven_legs.radial, driven_legs.tangential), law=leg_lean)`,
  and its `idle_legs` twin — proved on a read-only overlay at maximum
  deviation 0 over 11 poses, 113 leaves
  (`multi-source-multi-target-laws/evidence.md`, task 7.3). This is
  itself a live sighting the cycle closes: the project's own migration
  today (commit 99b0fcd5, `simulation/microscope/body/body.py`) had
  already reached this exact shape by reading `stage.slide_y.value`
  directly off the driving node inside a ONE-source law's closure,
  because the framework had no other way to state it yet — the overlay
  restates it with the framework's own two-source relation instead, at
  the same tolerance. Not yet applied in the project's own repository.
- **FIXED for the composition half (cycle `joint-composition-order`,
  ADR-093). Composition order, sixth sighting, and a joint under a
  conditional placement: the InMoov hand.** Eight phalanx bodies (middle phalanges,
  fingertips, thumb tip, the `dip` fasteners) each carry two
  non-commuting rotations, and the fingers are `.repeat(4)`; nesting the
  phalanges or naming the fingers one by one would state the motion
  today but renames every leaf and breaks six tests, which is refactoring
  around the gap. New form of the declaration-site joint: `Forearm.render()`
  applies `present()` conditionally to its direct children, so the wrist
  group's parent-frame axis depends on a flag the gear, clevis and bolt
  cannot see from their own classes. Deferred at stage A on the
  composition contract; the tendon ratios (`-50/FINGER_CLOSED` and
  siblings) and the 11:20 wrist train are ready to be sentences.
  The two non-commuting rotations per phalanx now compose in declaration
  order (ADR-093). The conditional-placement form of the
  declaration-site joint recorded in the same entry is UNTOUCHED and
  still open, and Inmoov-sim waits on it.
- **FIXED for the composition half (cycle `joint-composition-order`,
  ADR-093). Composition order, seventh sighting: the V8's connecting
  rods.** Each
  rod is `T(crank pin)·R(rod angle)` on one body, eight of them on
  `.repeat()` units driven through a per-unit phase; the pistons, valves,
  camshafts (`cam = crankshaft.turn / 2`, a derived coordinate) and the
  crank itself are statable today. The rod reads as `Orbit(axis, at=<the
  pin>)` plus its own `Revolute`, or as two joints under the declaration
  order contract. Deferred at stage A. The four timing gears are the
  eighth own-placed-origin sighting (one class, four anchors).
  The two-joint form is now statable (ADR-093), and the orbit half is
  built too (ADR-094, cycle `orbit-joint`): the rod reads
  `swing = Revolute(axis=(1, 0, 0))` then
  `orbit = Orbit(axis=(1, 0, 0), carries=(0, 0, CRANK_RADIUS))` — the
  carried point spelled `carries=`, and `at` keeping its default because
  the crank axis runs through the cylinder unit's own origin, which its
  class docstring states. The rod MUST name `carries`: it is not placed
  by `CylinderUnit.render()`, so its own placed origin is the unit
  origin, which is ON the crank axis, and the framework refuses a
  carried point there by name. Its listing writes `orbit` before
  `swing`; at stage B the two transpose. The own-placed-origin finding
  the four timing gears carry is untouched and still open, and the V8's
  deferral stands on that.
- **FIXED (cycle `whole-tree-fixpoint`, ADR-099). An ancestor's relation
  cannot SOURCE from a coordinate a descendant's relations solve.** The
  mirror of reaching by path: OpenFlexure's root
  stated `z_axis.actuator.column.travel.drives(body.lower_strut.swing, law=...)`,
  but the column's travel is bound by `Axis`'s own relations, which run
  after the root's, so the root's solve found it unreached at every
  pose. The four flexure laws had to be re-sourced from the root's
  `z_motor` driver with the step-to-travel conversion composed into each
  law. Same root cause as the one-class-body rule (no whole-tree
  fixpoint); the candidate fix already listed — defer an unreached
  relation until the descendants have solved, then re-run once — would
  make the sentence as written work.
  **What shipped:** the same whole-tree fixpoint as above. Proven on
  this exact shape
  (`tests/test_couplings.py::TreeFixpointTest::test_an_ancestor_sources_from_a_descendant_solved_coordinate`).
  An overlay restoring openflexure's own root sentence as written (task
  9.5 of the change) is NOT proven here, deferred for time; the
  project's own base-against-head pose comparison, unmodified, is
  0.000e+00 (`evidence.md` §9).
- **FIXED (cycle `whole-tree-fixpoint`, ADR-099). An author-bound joint
  keeps its value but loses its motion between
  runs.** A standalone root that binds its own joint in `simulate()` as a
  rest default with `if value is None: bind` stands correctly once, then
  at rest forever: the joint's operations are swept at the start of the
  next run as every simulate-phase motion is, but the coordinate's VALUE
  survives, so the guard skips the rebind and nothing re-applies the
  motion. Prusa i3's X and Y axes and extruder showed it as 37.5 mm,
  70.4 mm and 0.05 mm pose deviations on a second render; the fix is to
  rebind unconditionally. The hangprinter's winches carry the same guard,
  masked by a zero default. Candidate fixes: clear an author-bound
  joint's value with its swept motion, or refuse the read of a stale
  value by name.
  **What shipped:** clear, chosen over refuse (design.md §6 of the
  change): the value and binder of every coordinate an assembly bound
  during its PREVIOUS phase are dropped at the start of its next one,
  the author's own binding included. Measured live against Prusa i3's
  and hangprinter's OWN current, already-defensive code (an unconditional
  rebind pattern that works around this exact gap): both now measure
  0.000000 mm on a second render, on the base commit BEFORE this cycle's
  code changed anything (`openspec/changes/whole-tree-fixpoint/evidence.md`
  §0.6) — the fix keeps that true rather than needing to make it true.
  A synthetic reproduction of the naive (bind-inside-guard) shape those
  projects no longer write is proven directly
  (`tests/test_joints.py::StaleAuthorBoundJointTest`). A second, more
  severe defect surfaced only once the fix was measured against the
  FULL tree rather than a project in isolation: two assemblies
  alternating which one binds ONE coordinate across runs (Prusa's root
  relation `x.drives(xaxis.carriage.travel)` racing `XAxis`'s own
  rest-default guard) let the later one's stale record of its own past
  binding erase the value the earlier one had ALREADY correctly produced
  THIS run; fixed by scoping the clear to `_enum_marker`, the
  enumeration a slot was last bound in, not merely to which assembly
  bound it last time. Proven on Prusa i3's and abacus's own trees, base
  against head, from an unmodified `git archive HEAD` snapshot of each:
  0.000e+00 over every pose
  (`openspec/changes/whole-tree-fixpoint/evidence.md` §9).

# 3DPrintedClocks wall clock 02 (2026-09-09, exact sweep cost)

Measured on `machinome test wall_clock_02` under the exact kernel, at the
primary's 1822221: 1175 s for 16 tests, of which the two sweeps
(`@testing_steps(48)` over the swing, `@testing_steps(32)` over the great
wheel's turn, each calling `assertNoUnintendedSolidInterference`) are
~18.5 min. A sweep instant costs ~19 s, essentially all of it in
`BRepAlgoAPI_Common`: 53 topmost rigid solids, ~118 candidate pairs from
the world-AABB broad phase, ~110 booleans re-run per instant, every one
of them empty. Placement, BREP copies and keyframe binding are under
0.3 s per instant. Findings, in order of leverage:

- **The verdict memo misses co-moving pairs on float noise. Fixed** by
  cycle `quantise-verdict-memo` (ADR-090, amending ADR-070). The key was
  the exact bytes of `inv(M1) @ M2`. Of the 118 pairs, 30 are carried
  together (pendulum, motion works, weight and its line) and differ
  between instants by ~1e-13 — the noise of composing a rotation through
  a parent — so a question the memo already held was re-asked at every
  instant. The key now quantises the relative matrix to a run-level
  placement quantum (default 1e-9 mm, `--placement-quantum`/
  `SOLID_TEST_PLACEMENT_QUANTUM`, `0` restoring the exact-bytes key).
  Measured on the same test (`wall_clock_02`,
  `test_movement_runs_free_through_a_swing`, `@testing_steps(48)`, exact
  kernel): booleans 3820 → 2526 (33.9% fewer, exactly the rise in memo
  hits, 1823 → 3117) and wall time 779.37 s → 533.39 s (31.6% faster,
  keeping the same test verdict). Full counts and the quantum-0 control
  run in `evidence.md` of the `quantise-verdict-memo` OpenSpec change.
- **A common rigid turn inflates every world box. Fixed** by cycle
  `broad-phase-indexing-frame` (ADR-091, extending ADR-029). The clock
  declares `facing` on each child of its root — `Clock.render()` applies
  `rotate(self.facing, Z)` to each direct child, not to the root, which
  carries no placement of its own — so every topmost rigid solid shares
  one outermost rigid turn, and the movement's AABBs, taken on world
  axes, all grow by up to √2 and pairs that never meet overlap. At
  `--set facing=0` the same model yields fewer candidate pairs (see
  below). The broad phase now takes its boxes in a chosen INDEXING
  FRAME instead of always on world axes: the world frame, or the
  placement frame of one of the assembly's `K = 3` largest topmost
  solids by local-bounds diagonal, whichever scores the smallest total
  (padded) box volume — a fix that reaches the turn wherever it was
  declared, not only on a root that carries no placement of its own.
  Measured on `wall_clock_02` at the first swing-sweep instant: 116
  candidate pairs at the declared `facing=45` before, 67 at
  `--set facing=0`; after, 67 at `facing=45` (chosen frame: `standoffs`,
  tied with `plates` — the fused frame this bullet is about, both among
  the top two candidates by diagonal) and 67 at `facing=0` (world frame,
  unaffected) — the chosen frame recovers the un-turned candidate count
  exactly. Over the full 48-instant swing sweep
  (`test_movement_runs_free_through_a_swing`, exact kernel, default
  `facing=45`, measured against the tree after `quantise-verdict-memo`):
  booleans 2526 → 1089 (56.9% fewer) and wall time 533.39 s → 265.99 s
  (50.1% faster), same test verdict. Full counts, the chooser's own
  ranking and scores, and the honest comparison against the finding's
  3x forecast are in `evidence.md` of the `broad-phase-indexing-frame`
  OpenSpec change.
- **One enclosing solid defeats whole-solid boxes. Fixed** by cycle
  `face-box-broad-phase` (ADR-092, extending ADR-029 and ADR-091). One
  correction to this bullet's own wording first: "the fused frame (both
  plates and their pillars, one solid) sits in 40 of the 118 pairs" was
  never quite right — `broad-phase-indexing-frame`'s own evidence had
  already shown `standoffs` and `plates` are two separate topmost solids,
  not one fused one, and this cycle's own measurement (67 candidate pairs
  at the first swing-sweep instant, the tree after
  `broad-phase-indexing-frame`) shows neither one dominates the pairs a
  face-box tier cannot decide: of the 57 pairs the tier declines (it
  decides the other 10 without a boolean), `wheel` (the train's five
  wheels) appears in 24, `rod` — a 3-face cylindrical shaft the wheel
  train is mounted on — in 23, `plates` in 9 and `standoffs` in only 3.
  The wheel train's mounting rod, not the frame, is what the tier cannot
  separate from the wheels bored onto it — a genuinely close fit, not a
  spurious enclosure.

  A second exact-negative tier now runs after the AABB cull and before
  any boolean, for a pair of EXACT solids: each solid's face boxes
  (`BRepBndLib.Add_s(face, box, False)`, cached once per shape identity)
  are compared in one solid's own frame, and if none of one solid's
  meets any of the other's, a containment guard — one representative
  vertex of every solid of each shape classified against every solid of
  the other, in both directions — tells a genuine disjoint pair from one
  solid wholly inside the other before reporting it empty. Measured over
  the 48-instant swing sweep
  (`test_movement_runs_free_through_a_swing`, exact kernel, default
  quantum, `facing=45`, against the tree after `broad-phase-indexing-frame`):
  booleans 1089 → 708 (35.0% fewer — the tier decided 381 of the 1089
  memo-misses without a boolean) and wall time 265.99 s → 216.50 s
  (18.6% faster), same test verdict; keyed asks and memo hits are
  unchanged at 3210/2121, as expected since this tier does not change
  which pairs are emitted. At the first instant the tier's own cost was
  0.955 s (its containment-guard share 0.770 s across 10 classifier
  calls) against 10.04 s of boolean time for the 57 declined pairs —
  smaller than the ~8 s this bullet once attributed to plates × wheel
  booleans alone, because the dominant surviving cost turned out to be
  the mounting rod, not the plates. Full counts, the surviving pairs'
  solids, and the tier's own cost are in `evidence.md` of the
  `face-box-broad-phase` OpenSpec change.
- **An exact solid's index bounds are inscribed, not conservative.**
  `_solid_geometry` takes every topmost solid's local bounds from the
  STL mesh even for an exact solid; a tessellation's vertices lie ON the
  exact surface, so those bounds fall up to the declared linear
  deflection (0.1 mm default) short of the exact extents on a curved
  face, and a sub-deflection overlap at a box boundary could in
  principle be culled by the whole-assembly index. The fix: an exact
  solid's local bounds become the union of the exact face boxes
  `face-box-broad-phase`'s `cached_face_boxes` already computes; faceted
  solids keep mesh bounds. Left for a separate cycle for three reasons
  (design.md section 8 of `face-box-broad-phase`): it reverses two
  ratified sentences of `Accelerated intersection evaluation` ("The
  bounding boxes the broad phase transforms SHALL come from the cached
  base mesh for every solid, exact or faceted" and "The candidate pairs
  a given assembly emits SHALL NOT depend on whether its solids carry
  exact geometry"); it must not fire under the faceted kernel, where a
  run may not read any solid's `shape()` at all; and it moves WHEN an
  exact solid's faces are measured, from "when a candidate pair reaches
  the face-box tier" to "at selection", including solids no candidate
  pair ever compares. **Filed:** cycle `exact-solid-index-bounds`.
- **A mesh-distance exact-negative tier** (distance above twice the
  declared linear deflection proves the exact solids disjoint) and
  **parallel pair booleans** (the run used 225 % of 1600 % CPU; OCCT's
  `SetRunParallel` thread pool deadlocks under `fork`, so workers must
  spawn) are the two remaining framework levers. The three cycles this
  bullet once deferred them behind — `quantise-verdict-memo`,
  `broad-phase-indexing-frame`, `face-box-broad-phase` — have all landed
  and are measured above.
- Not a framework fix: fusing the plates and pillars into one solid is
  the project's choice, and `cProfile` over `machinome test` reports garbage
  totals (instrument directly).

# Inmoov-sim stage B (2026-09-10, first project on ADR-093)

Found resuming the InMoov hand and forearm on the composition-order
contract. Stage B went through unchanged: eighteen `Revolute`s on twelve
classes, twenty relations, poses max deviation 0 on both models, both
suites green with no test edited. Two findings, neither blocking.

- **A subclass cannot put its own joint INSIDE an inherited one.** ADR-093
  orders a class's joints base-first and a redeclaration keeps the base's
  slot, so a `ThumbFingertip(Fingertip)` inheriting `dip, pip, mcp` in
  slots 0-2 gets its own `tj` in slot 3 — outside `mcp`, which is the
  wrong side of the knuckle — and redeclaring cannot move it. The project
  restructured: both tips now subclass a jointless `GluedTip` and declare
  their own stacks. Same node names, children and paths, so the cost was
  one class, not a hack; but a body whose subclass adds an INNER freedom
  has no way to say so short of re-parenting. Candidate fix, if a project
  ever needs it: an explicit slot keyword, rejected by ADR-093 for lack of
  a sighting — this is the first, and it was absorbed.
- **Declaration-site joint, third direction: a parent whose own frame is
  conditional.** `Forearm.render()` applies `present()` to its direct
  children only when `self.presented` is true, so the wrist group's
  parent-frame axis (gear, clevis, axle, hand) depends on a flag none of
  their classes can see; they stay hand-written in `Forearm.simulate()`
  with `_about_axis`. Wanted, as the earlier sightings:

      gear = WristGear(turn=Revolute(axis=wrist_axis, at=wrist_anchor, unit='deg'))

  with the callables evaluated against the realized PARENT. The wrist
  pinion did escape (`wrist.drives(drive.pinion.spin, offset=...)`)
  because `WristDrive` is built in the pinion's frame. `Hand.simulate()`'s
  ten `connect()` calls were carried on the `.repeat()` fan-out finding;
  moved to the tuple-source cycle instead now that fan-out is FIXED
  (cycle `repeat-fan-out`, ADR-096), because a broadcast has one SOURCE
  and `Hand` drives each of its four repeated fingers from a DIFFERENT
  driver. That is a per-copy source, not a per-copy law.

  **FIXED as a SELECTOR (cycle `multi-source-multi-target-laws`, ADR-100),
  not as the cleaner sentence.** The ten `connect()` calls become
  `(thumb & index & middle & ring & little).drives(fingers.drive, law=by_finger)`,
  its twin over `drives = Drive().repeat(5)`, and one one-to-one relation
  for `thumb_finger.drive` (which no repeat reaches) — proved on a
  read-only overlay at maximum deviation 0 over 15 poses, 53 leaves
  (`multi-source-multi-target-laws/evidence.md`, task 7.4). The law is a
  SELECTOR, not a mechanism: all five motor values are handed to every
  copy so each may pick its own one by index, because the cleaner
  sentence — a per-copy SOURCE, `index.drives(fingers[1].drive)`, naming
  the copy by its own position — is INDEXING A REPEAT IN A CLASS BODY,
  which `repeat-fan-out` named as a non-goal and this cycle does not add
  either. **Residual want, recorded here rather than closed:** indexing a
  repeat in a class body, so InMoov's sighting can close as the sentence
  it actually wants instead of a selector. Not yet applied in the
  project's own repository.

# hexapod_spiderbot_model stage B (2026-09-10, first project on Free)

Found resuming the SpiderBot on ADR-093 and ADR-095. Stage B went through
unchanged: `pose = Free(...)` on the chassis driven by four root
relations, three `Revolute` declarations for eighteen leg freedoms, the
root's `simulate()` gone; poses bit-identical over 28 poses and 172
leaves, 34/34 green, no test edited. One finding, not blocking.

- **A dotted coordinate name can be written but not read by name.**
  `declared_ports(Chassis)` reports a `Free`'s six coordinates under
  dotted keys (`pose.roll`, ...), and `set_coordinate(node, 'pose.roll',
  value)` binds one; but there is no reader: `getattr(node, 'pose.roll')`
  raises `AttributeError`, so every consumer that iterates
  `declared_ports` and reads each name — the shop's own
  `capture_poses.py` was the first — records an error for all six. Exactly
  the consequence ADR-095 predicted, arriving on the primitive's first
  use. Wanted, the read counterpart of the writer:

      get_coordinate(node, 'pose.roll')      # the bound slot, or None

  exported beside `set_coordinate`, and the ports spec saying that a
  name the enumerator reports is a name the framework can read back.
  Nothing in the project needs it (`self.pose.roll.value` reads fine).

  **FIXED (cycle `repeat-fan-out`, ADR-096).** `get_coordinate(node,
  name)` is exported from `machinome.motion.ports` beside
  `set_coordinate`, mirroring it segment for segment, returning the
  bound slot — `None` value for an unbound one — and refusing a name
  `declared_ports` does not report by name rather than answering `None`
  for that case too. The ports spec now states the pairing as a
  requirement.
- The "own-placed-origin" anchor sighting again: `Femur.lift` and
  `Tibia.knee` restate the parent's `translate` as `at`.

# joint-frame-follows-declarer (2026-09-10, closing the own-placed-origin finding)

**CLOSES the "a joint cannot be anchored at a design-placed part's own
origin" finding**, open since wall clock 01/Thor (2026-09-09) and
re-sighted in the hexapod, the V8, Poseidon, OpenMANIPULATOR-X, the
Pascaline, fender-bender, the Prusa i3 and InMoov. ADR-097 answers it
directly rather than adding a mode: a joint written in a class body is
now read in that body's OWN rest frame, `at` defaulting to the body's
own origin, so the mode this finding kept asking for is simply the
frame, not a special case within the old one. Measured over the whole
catalogue (`evidence/survey.md`, the change's own evidence): 23
projects, 249 class-body joint declarations, 133 of them exactly this
shape (69 restating a placement, 64 already anchorless) plus roughly 30
hand-written rotations the rule newly makes declarable. A 24th project,
OpenCycloid, joined the catalogue mid-cycle (see below). Of the 24, 23
compare at maximum deviation 0 against a mechanical rewrite (three
grasshopper clocks and one hangprinter roller first deviated and were
each traced to a cause and closed at 0 -- the entries below); the one
real nonzero is wall clock 48's own already-migrated source, carried to
the pilot. OpenCycloid's own default-only rewrite now REFUSES to bind
rather than building silently wrong (see "OpenCycloid" below). Seven
clocks show a residue under 8 microns on a wound-string port that two
captures of the SAME tree reproduce against each other and
`PYTHONHASHSEED=0` removes: capture-process nondeterminism, not this
change (last entry below). Full numbers: `evidence.md`
§7 of `joint-frame-follows-declarer`.

Two things the finding did not anticipate, filed as their own entries
rather than folded into the closure:

- **Five axes lose their literal.** Where one class is placed at
  several sites with OPPOSED rotations — Prusa `XGuide`/`YGuide`
  (`.repeat(2)`, `along_y`/`along_minus_y`), hangprinter's mirrored
  `MotorGear` and its `RollerBearing` pair, OpenVMP's two `Leg`s — one
  parent-frame axis literal served every site; the own-frame axis is
  different per site and cannot be written as one literal. Two of the
  three projects state the choice as a deliberate design decision in
  their own source (`hangprinter/simulation/winch.py:57-64`). Two
  bridges exist and neither is new machinery: a callable of the
  realized node reading the body's own parameter or a `.repeat()`
  copy's `index` (from `repeat-fan-out`, ADR-096), or the parent
  supplying the sign in the relation (`ratio=-1`, or `law=` under a
  broadcast) — which is what Thor already does. Neither is built by
  this cycle; the literal is wanted back at a declaration site, which is
  `declaration-site-joint`'s open question: whether that keyword should
  itself be repeatable, since three of these five really want it on a
  `.repeat()` copy.
- **3DPrintedClocks disagrees with itself, and the rule settles it in
  clock 48's favour.** Clocks 19, 21, 22, 41, 49 and 51 (six, each with
  its OWN local `TurningArbor(Arbor)` class -- `Arbor` there is the
  plain-geometry `parts.Arbor`, not the motion-composing
  `shared.TrainArbor`) write `at=lambda node: arbor_bearing(node)` on a
  leaf `place_train_arbor` has already translated by that same bearing
  (as one of `FixedRodArbor.render()`'s CHILDREN, unlike the shared
  module's own `TrainArbor.turn`, whose placement of ITSELF is the
  identity and needs no change); wall clock 48's `TurningArbor`/
  `TurningPalletPin` write NO `at` at all, with a source comment
  (`wall_clock_48/clock.py:135-140`) explaining that the plate-frame
  bearing "applies that offset twice." Under the OLD rule exactly one
  of the two families was wrong wherever the bearing is not the
  origin; wall clock 48 already reads as the new rule wants, unedited
  -- its source was written for a rule the framework did not have yet.
  The six unmigrated clocks were fixed the same way wall clock 48's own
  source already reads (delete the `at=`); a first pass at this fix
  left them unpatched and the pose overlay caught it immediately (166.2
  mm on wall clock 49, 177.2 mm on 51, present even at `defaults`, on
  `movement.train.*`). Wall clock 48 itself is the one place in the
  whole survey that does NOT compare at zero: `AnchorArbor`'s wheel
  (index 5) and its two pallet pins move, by construction, towards what
  the clock's own comment already asks for -- measured peak 3.985 mm at
  `time@0.5`, flat 2.841 mm at every pose that does not vary `time`.
  Carried to the pilot as a question in the change's evidence, not
  accepted here as a difference: this file's job is to record that it
  is exactly the disagreement predicted, not to
  judge whether the corrected pose is right.

- **A `.repeat()` copy's `index` does not exist yet when a joint's own
  `axis`/`at`/`carries` resolves, so "a callable of the copy's index"
  is not actually a working bridge for a JOINT argument.** Found
  applying decision 4's Bridge A to Prusa3-vanilla's `XGuide`/`YGuide`,
  hangprinter's `RollerBearing`, and OpenCycloid's `RadialBearing`/`Pin`
  in this cycle's own pose overlay: `axis=lambda node: (0, 0, 1 if
  node.index == 0 else -1)` on a `.repeat(2)` class raises
  `AttributeError: '<Class>' object has no attribute 'index'` at
  REALIZATION, every time, because `resolve_declared_joints` runs
  inside the copy's own `__init__` (ADR-088) while
  `RepeatDeclaration.realize()` assigns `child.__dict__['index'] =
  index` on the line AFTER that construction returns
  (`machinome/node/declarative.py:391`, whose own comment already says
  "no sighting needs `index` during construction" — true for a LAW
  resolved later, false for a joint argument resolved eagerly).
  `MotionWorksPart`'s existing `at=lambda node: ... node.index ...`
  works today only because `index` there is a DECLARED PARAMETER
  (`Count(min=0, max=2)`, passed as a constructor kwarg), not a
  `.repeat()`-assigned attribute — the working and the broken case look
  identical at the call site and are easy to conflate, which the
  overlay did once. Worked around, three times over, by deriving the
  axis from the copy's ACTUAL placement in the PARENT's `render()`
  instead of a class-body callable — the overlay's own
  `derive_helper.axis_from_placement`, `_carry`'s own arithmetic reused
  for one run. Candidate fix: resolve a REPEATED class's joint
  arguments once per copy, after `index` is assigned, rather than
  inside the copy's own `__init__` — or let `resolve_declared_joints`
  defer a `NameError`/`AttributeError` from a callable and retry once
  the realization path can say why, naming which attribute was missing
  rather than failing opaquely. This closes the axis half of decision 4
  as WRITTEN (Bridge A does not work as stated for the five axes); the
  parent-supplies-the-sign bridge (Thor's own `ratio=`) is unaffected,
  since a relation's `law=`/`ratio=` resolves later, after `index`
  exists.

- **Two more sites in the shared clock module needed the same
  restates-to-zero treatment as `MotionWorksPart.turn`/`Pendulum.swing`/
  `Escapement.frame_turn`, found by the SAME pose overlay.**
  `ZDayPart.turn` (`wall_clock_52`, `wall_clock_54`, the day-of-week
  complication) restates `DayComplication.render()`'s
  `part.translate(positions[0 or 1])` for either branch of its own
  `node.index in (0, 1)` conditional -- own-frame anchor is `(0, 0, 0)`
  either way, so the whole conditional callable is removed. Fixing it
  did not close either clock's whole residual: `wall_clock_52` still
  shows 1.069e-03 mm (a floating-point residue on a wound-string port,
  present on several other clocks too, none of them exceeding 5
  microns) and `wall_clock_54` still shows 3.477 mm on an UNRELATED
  leaf (see the grasshopper `entry_arm` finding, below).
- **CLOSED. Three grasshopper-escapement clocks (`wall_clock_21`,
  `wall_clock_53_grasshopper`, `wall_clock_54`) showed a deviation
  confined to `movement.escapement.entry_arm`, zero at `defaults` and
  growing with `time` (0.681/2.321/3.954 mm on `wall_clock_21`;
  1.162/3.477 mm on the other two) -- traced to a missed citation, not
  a new framework finding. Each clock's OWN `parts.py` declares
  `PalletArm.turn = Revolute(axis=Z, at=lambda node: (*node.built.
  grasshopper.drawn_position('G' if node.exit_side else 'P'), 0.0))`,
  a RESTATES site `evidence/survey.md` §1.3 (line 142) already names
  correctly for `wall_clock_53_grasshopper` and `wall_clock_54` --
  `assemblies.Escapement.render()` translates each arm by exactly that
  same pivot -- but `wall_clock_21` has the identical class and was
  missing from that row's citation list, so `patch_3DPrintedClocks.py`
  implemented every other row but this one. Only the entry arm ever
  deviated because the exit pivot `'G'` is at the origin, matching
  every measured number exactly. Fixed by deleting the `at=` in all
  three clocks' overlay `parts.py`; re-captured sequentially, all three
  now compare at 0.000e+00.
- **CLOSED, by using the cheaper bridge. hangprinter's
  `RollerBearing.spin` axis derivation had an unexplained residual on
  exactly one roller** (`ceiling.winch_d.rollers-0`, up to 1.986 mm,
  growing with driven angle): a runtime-injection workaround (deriving
  the axis at the end of each winch's `render()`, because a `.repeat()`
  copy's `index` is not available at eager joint-argument resolution --
  the entry above) correctly reached `winch_c`'s roller but left
  `winch_d`'s roller-0 reading the class's own placeholder axis
  literal, unfixed -- an ordering race in the workaround itself, never
  identified further. `evidence/survey.md`'s own row 241 already states
  the two per-site literals this joint actually needs
  (`(0, 0, -1)`/`(0, 0, 1)`, one per `BELT_ROLLERS` entry a roller is
  zipped against, the SAME pair for `WinchABC` and `WinchD` alike) --
  cycle 2's simplest bridge, a plain per-site value, not a callable of
  an unavailable `index` and not a runtime derivation either. Fixed by
  replacing each winch's `rollers = RollerBearing().repeat(2)` with two
  NAMED, non-repeated leaves (`roller_a`/`roller_b`), each a trivial
  `RollerBearing` subclass carrying its own literal `spin` axis -- no
  `.repeat()`, no `index`, no injection, no race to have a bug in.
  Re-captured once: every roller, on every winch, at every pose,
  compares at exactly 0.000e+00 (checked leaf-by-leaf against the
  renamed nodes directly, since the compare tool's own path-matching
  reports a rename as one node missing and one new rather than a
  diffable pair).
- **OpenCycloid (added to the survey mid-cycle, its own stage B landing
  on `d07b14c` while this survey was being read) shows the same
  `at`/`carries` asymmetry as the Internal Cycloidal Actuator, but
  because its OWN source already declares both `Orbit`s fully
  defaulted -- no `at=lambda ...` to delete -- a plain default-only
  mechanical migration does not go silently wrong here: it REFUSES.**
  `CycloidalDiskStageOne.orbit`/`StageTwo.orbit` and
  `RadialBearing.orbit`/`Pin.orbit` all default both `at` and `carries`
  to the body's own origin under the new rule (where the old rule's
  asymmetric defaults -- `carries` to the sentinel own-placed-origin,
  `at` to the literal parent origin -- gave every one of them a real
  eccentricity for free); with both at the same point the derived
  radius is zero and `Orbit.placement` refuses at first bind, by name:
  `ValueError: stage_one (CycloidalDiskStageOne): joint 'orbit' carries
  a point that lies ON its own axis, so binding it would move nothing.
  ... the radius they derive is 0.0.` This was confirmed directly
  against the UNPATCHED project. The overlay's own DERIVED fix (parity
  with the Internal Cycloidal Actuator's `BORE_AXIS_POINT`) reaches
  0.000e+00 over 7 poses once each disk's own-frame anchor is restated
  as the NEGATION of its own placement translate -- a first attempt
  used the same sign as the placement rather than its negation and the
  pose overlay caught it immediately (9.961 mm on
  `drive.stage_one`/`stage_two`).
- **The 1-8 micron `movement.string.*` residues on seven clocks
  (`wall_clock_23`/`24`/`25`/`26`/`28`/`49`/`52`) are capture-process
  nondeterminism, not a source difference this cycle made.** Captured
  `wall_clock_24` TWICE from the SAME already-patched overlay tree (no
  file touched between the two runs): the two captures differ from
  each other by the exact same magnitude and on the exact same ports
  as the original before/after comparison (4.828e-03 mm max, on
  `movement.string.{coil_height,entry_*,pulley_*,tie_*,wraps}`).
  Re-running the same two captures with `PYTHONHASHSEED=0` fixed
  (rather than Python's default per-process random hash seed) makes
  them match EXACTLY. The string-wrap computation (molejo's wrap
  solver, reached through `movement.string`) iterates something whose
  order depends on Python's hash-randomized dict/set ordering, and a
  non-associative floating-point sum over that ordering gives a
  run-dependent last few digits -- comparing a `before2/` capture (one
  process) against an `after/` capture (a separate, later process)
  always carries this noise, independent of whether `joints.py`
  changes at all. Not a framework defect and not something this
  overlay methodology can avoid without pinning `PYTHONHASHSEED` for
  every capture; recorded here so a future comparison at this
  precision knows to pin it rather than chase phantom regressions.

# v8-engine (2026-09-10, stage B on ADR-093 + ADR-097)

- **A bound coordinate's VALUE is never cleared between simulate passes,
  so the `if self.turn.value is None: self.turn = ...` fallback idiom
  silently freezes.** The v8-engine's stage B (its `docs/move-onto-motion.md`,
  commit a25b074) needed nodes that bind their own coordinate when run
  standalone but defer to an ancestor's relation when assembled; the
  campaign's suggested idiom tests `value is None`. Measured with
  `machinome test`: the operations a binding produced are swept between
  passes but the value is not, so after the first standalone bind the
  guard is never true again and every later `set_keyframe` / pose
  re-capture of the same instance keeps the first value. The project's
  bridge: an unconditional re-bind where the fallback formula equals what
  the ancestor would set anyway, and a structural `hasattr(self, 'index')`
  guard (ADR-096's per-copy stamp) where the fallback genuinely differs
  (`CylinderUnit.crank`, `ValveMotion.lift`, per-copy phase offsets).
  This is the stale author-bound value `whole-tree-fixpoint` proposes to
  CLEAR with the sweep, sighted from the other side: the fix is that
  cycle, and the `hasattr` guard should go when it lands. Filed here;
  triage: cycle 4.
- **Tooling.** `openspec validate` refuses a change with no spec delta
  ("Change must have at least one delta"), so a project migration whose
  whole point is zero behavioural change (every ADR-097 stage B: poses
  0.000e+00, no requirement touched) cannot be validated at all and is
  archived with `--yes` past a warning. Not a framework matter; noted so
  nobody fabricates a delta to satisfy the tool.

# declaration-site-joint (2026-09-10, ADR-098)

- **CLOSED: the declaration-site finding.** ADR-097 named the second
  declarer and built none of it; ADR-098 builds it. Fourteen live
  sightings in eight projects, all reproduced at maximum deviation
  0.000e+00 in a read-only overlay: OpenCycloid's twelve orbiting
  bodies (four site `Orbit`s, ten of them `.repeat()` copies, all
  REFUSED by ADR-097 alone, now binding again); the Internal Cycloidal
  Actuator's two disk `Orbit`s; InMoov-sim's seven finger `Revolute`s
  and (recorded separately) its wrist axle; openflexure-microscope's
  `GearLockScrew.orbit` on a `.repeat(2)`; Prusa3-vanilla's two belt
  guide pairs; hangprinter's roller pair; openvmp's `Leg` (two sites)
  and `CameraArm`; open_manipulator's two gripper fingers. Four
  subclasses-for-metadata are deleted in their overlays: openvmp's
  `Wheel` and `CameraArm` (with `CameraArm`'s `__init__` override and
  its two instance attributes), OMX's `LeftFinger` and `RightFinger`.
- **CORRECTED: the plan note's record.** `workflow/docs/motion-catalogue-2.md`
  §3.3 gave three example sentences and named four validation projects;
  measured against the source (`declaration-site-joint/evidence/sightings.md`
  §5), two of the three examples are ADR-097's work, not this cycle's
  (Poseidon's `ThreadedRod`, Prusa's Z screw, both already clean
  own-frame declarations with no anchor needed), the third
  (InMoov's wrist gear) is three-quarters ADR-097's (the axle is the
  one piece this cycle actually serves, and for a different reason
  than the note gives — shared catalogue hardware, not a conditional
  frame), and the fourth (the actuator's `disk_one = CycloidalDisk(orbit=
  Orbit(axis=(0, 1, 0)))`) is short by a `carries=` whose absence is a
  2 mm error and a wrong phase with NO refusal to catch it. Poseidon is
  not a validation project for this cycle at all. The corrected list of
  eight — OpenCycloid, the Internal Cycloidal Actuator, Inmoov-sim,
  OMX, openvmp, Prusa3-vanilla, hangprinter, openflexure-microscope —
  is what `declaration-site-joint`'s own proposal and evidence.md
  actually measure.
- **NEW: a parent's hand-written motion and its own site joint read two
  different frames on one child.** A parent's `self.child.rotate(...)`
  in its own `simulate()` is inserted inside the child's rest placement
  and is therefore read in the CHILD's frame; a site joint the SAME
  parent declares on the SAME child is read in the PARENT's. After
  ADR-098 a project can write both on one child and get two frames from
  one author, with nothing in the framework to catch the mismatch. No
  sighting in the catalogue is harmed by it today. Filed, not fixed;
  triage: needs its own sighting before a direction is chosen (state
  hand-written motion in the parent's frame too, at the cost of
  carrying it always; or refuse the combination by name; or leave it,
  documented, as the one seam where "declares" and "writes by hand" do
  not agree).
- **NEW: a relation cannot name a child a loop builds from data.**
  openvmp's own written-down sentence
  (`archive/2026-09-09-move-onto-motion/proposal.md:225-231`):
  `front.yaw.drives(base['motion-front-wormgear/worm'].spin, ratio=...)`.
  A relation is class metadata whose every segment is checked at CLASS
  DEFINITION against the class the previous segment names; a child
  built from a `.assy` file at construction time has no class-level
  name to check against. `declaration-site-joint` measured the OTHER
  half of this sighting — giving such a child a real, bindable
  coordinate — and found it already answered by ADR-097 and ADR-088
  alone (a project-side `TurningPart(StepPart)` subclass with a
  declared parameter and a class-body callable, built by the project's
  existing loop): no cycle in this campaign closes the relation-naming
  half, and openvmp does not get the sentence it asked for. Triage:
  needs its own cycle if a project ever needs it for real; openvmp's
  eight sites stay hand-bound in its own `simulate()` until then.
- **NEW: `type(x) is C` no longer holds for a child whose declaration
  site gave it a joint.** The specialization (ADR-098) copies the
  written class's `__name__`, `__qualname__`, `__module__` and source
  file, deliberately (a joint is not identity), so `isinstance` holds
  but an identity check against the exact class does not.
  `machinome/node/internal.py:166` is the one place in the framework
  that makes this check — a guard against a render returning its own
  type, `type(child) is type(self)` — and a site-jointed child of a
  parent's own class would slip past it. Pinned for the ordinary case
  (`SpecializationOwnTypeGuardTest`), not fixed; no sighting in the
  catalogue reaches this guard with a site-jointed child of its own
  parent's class today.

# Inmoov-sim (2026-09-10, stage B on ADR-098)

- **A site joint's value is the line in the parent's frame where the
  child FINALLY rests, after every rest operation the parent applies to
  it — and when one of those is conditional, a plain value is silently
  wrong for the other branch.** `Forearm` places its wrist `axle` with
  `_in_wrist` and then, when `presented` is true, `present()`'s turn;
  the site joint `Bolt(turn=Revolute(axis=..., at=...))` written as the
  plain pre-presentation numbers reproduced the reference poses only
  with `presented=False`, and with the project's own default missed by
  622 mm³ of palm/axle interference at rest and 14.2 mm at full wrist
  travel, with no refusal. Correct: a callable of the realized parent
  (`_presented(vector)` rotating the value through `PRESENTATION` when
  `forearm.presented`), which is the ADR-098 contract working as
  designed — the parent's frame is where the child ends up — but nothing
  in the docs says a plain site value should be treated as suspect
  whenever the parent's own rest placement of that child is conditional.
  Triage: one sentence in `docs/driving.rst`'s site paragraph and in the
  shop craft skill; no framework change.

# deferred-read-is-current (2026-09-11, worktree deferred-read-current on ADR-099)

- **FIXED: a deferred relation read its source one enumeration stale on
  every re-pose.** Sighted in openflexure-microscope's stage B, restoring
  the root sentence `z_axis.actuator.column.travel.drives(body.
  lower_strut.swing, law=…)` — an ancestor sourcing from a coordinate a
  descendant's own relation solves, the exact shape ADR-099 promises.
  Correct on the FIRST `render()`; on every later `set_state()`, the
  driven end read the value the source held at the end of the PREVIOUS
  enumeration, never the current one. A second, independently-measured
  sighting (OpenTorque's `reducer.planet_1.orbit.drives(
  output_stack.planet_carrier_b.turn)`, landing 4.320e+02 mm off on a
  second `set_state()`) confirmed the same cause on a different shape
  (two separate descendant subtrees rather than one chain into a leaf).
  Cause, measured: tree order runs an ancestor's own relation attempt
  BEFORE the descendant that owns the source has cleared and rebound it
  this enumeration; `ResolvedEnd.bound()` asked only whether the slot
  held a non-`None` value, which a stale leftover from the previous
  enumeration also satisfies, so the ancestor's own attempt solved
  immediately from stale data instead of deferring — and once solved,
  the descendant's later fresh rebind is never revisited this
  enumeration. Fixed in `deferred-read-is-current`
  (`machinome/motion/couplings.py`, `machinome/node/phase.py`,
  `machinome/motion/ports.py`): a non-fresh value now reads as unbound,
  and this attempt defers, exactly when the assembly that bound it
  (tracked as `BoundPort._bound_by`) is the one currently attempting or
  one of its own descendants — still due to run before this pass
  concludes. A naive "not bound this enumeration means unbound" rule is
  WRONG and was measured to be: it defers forever a value bound by an
  assembly outside the current pass's own subtree, which the serializer
  produces routinely (`serialize_node`'s own recursive `render()` at
  every level, each opening a NEW enumeration over a narrower subtree
  once its parent's has already closed — ADR-099's own accepted
  "idempotent re-attempt" case) and which a hand-bound coordinate set
  before the first `render()` ever opened one also produces.

# 3DPrintedClocks (2026-09-11, stage B on ADR-099)

- **A descendant's hand-written `simulate()` that needs a coordinate an
  ANCESTOR's deferred relation binds gets it too late.** Wall clock 01's
  two-arbor chain, moved back inside `Train` as ADR-099 now allows
  (`centre.drives(third, law=going_train)`, `third.drives(escape, ...)`),
  declares fine and then refuses on the FIRST enumeration:
  `movement.string.drop was read by StringAssembly's own simulate()
  (motion.py:327) before the relation power.turn drives string.drop bound
  it`. Once the chain is stated one level down, everything `Movement`
  states from `power.turn` — the weight's string drop, the cannon-pinion
  setting — defers to the tree-wide fixpoint, which runs only after every
  node's own phase, but `StringAssembly.simulate()` computes its geometry
  from `drop` DURING its phase. Identical before and after
  `deferred-read-is-current` (a different defect: this one is first-pass).
  The chain stays hoisted in `Movement`; the sentence wanted is exactly
  those two lines. Not a bug in the fixpoint — it delivers exactly when
  ADR-099 says — but the ADR's "a chain may be stated one level down"
  is only true when nothing below the chain reads its results by hand.
  Candidate directions, each needing its own sighting before a choice:
  a descendant's hand-written read could itself defer (the phase re-run
  once its inputs bind), or the rule could refuse at CLASS DEFINITION
  when a class both reads a coordinate in `simulate()` and has an
  ancestor relation feeding it, naming the read. Filed; triage open.
- **Four seconds-hand clocks (19, 28, 39, 41) declare no relation onto
  `seconds_hand.arbor`** where the other six write
  `train.escape.turn.drives(seconds_hand.arbor)`; the premature read that
  used to feed it (now deleted) left it stale before and `None` now. A
  project matter for its own maintainer, one line per clock; recorded
  here because ADR-099's read refusal is what made it visible.

# orcahand_hardware (2026-09-10, ORCA v1 STEP import)

- **FIXED (cycle `select-a-step-product`, ADR-115). `machinome import-step`
  can generate Python that does not parse.** Importing
  `orca_v1/ORCA_Assembly/ORCA_v1.step` generated 53 assembly adapters; an
  identity-only assembly received a `render()` body containing comments but
  no statement, so importing `simulation/v1/assembly.py` raised
  `IndentationError`. Inserting an inert `pass` into every generated
  `render()` made the transcription compile without changing any placement.
  The generator should emit `pass` whenever a generated method has no
  executable placement. Filed here; not triaged.
  **What shipped:** exactly the candidate fix — `_placement_lines` now
  reports whether it emitted a rotate/translate statement, and
  `_assembly_class_source` appends `pass` under the comments whenever no
  child of that class emitted one, subsuming the pre-existing
  childless-assembly fallback. Proven on the framework's own fixtures:
  three of five existing `StepNode` documents generated an unparseable
  `assembly.py` before this fix, all compile after
  (`tests/test_import_step.py::GeneratedSourceCompilesTest`).
- **FIXED (cycle `select-a-step-product`, ADR-115). `machinome import-step`
  can scaffold a document that `StepNode` cannot
  select.** The same document contains 15 distinct products named `SHELL`.
  The importer generated adapters whose only selector is `part = 'SHELL'`;
  the first build then failed because `StepNode` correctly reported all 15
  name matches as ambiguous. The public adapter and generated source expose
  no product label, occurrence path, or other stable disambiguator, so the
  command cannot build the complete assembly it just scaffolded. Candidate
  fix: give `StepNode` a stable document-product selector and have
  `machinome import-step` emit it whenever names are not unique. The project
  workaround imports the v1 printed STLs and applies the occurrence
  transforms recovered from the generated STEP transcription; a seven-part
  palm/tower/articulated-index probe built and rendered, and all v1 finger
  STLs are watertight single bodies. Evidence:
  `projects/Robotic-Hands/orcahand_hardware`, change
  `simulate-orca-v1`. Filed here; not triaged.
  **What shipped:** a name-relative `part_index` on `StepNode` (not the
  document entry the candidate fix suggested — measured unstable across
  a re-export, ADR-115 design D1), and `machinome import-step` keyed on
  each product's own identity end to end, emitting `part_index` on a
  generated class whenever its product name is shared. Proven on a
  duplicate-name fixture reproducing this document's own shape: the
  scaffold's two generated classes for two same-named products build
  distinct geometry, never overwrite one another, and the generated
  assembly places each at its own occurrence
  (`tests/test_import_step.py::GeneratedModelFaithfulnessTest::test_a_duplicate_named_model_is_faithful`).

# Locks (2026-09-13, Combination safe lock)

Recorded at the pilot's explicit request. Project: `projects/Locks`, change
`simulate-the-combination-safe-lock`, Roffe's Printables model 921305.
These are empirical findings, not ratified requirements or permission to
implement a framework change. No framework source was read or modified for
the simulation; the public API skill and viewer's public host interface were
used. Reproductions and full validation remain with the originating project
in `docs/framework-findings.md` and `docs/validation.md`.

- **History-dependent pickup requires a project-owned host controller.**
  A combination lock reaches different wheel positions at the same absolute
  dial angle after different reversals and complete turns. The public
  snapshot/driver/instruction surface does not describe a serialized state
  transition for history-dependent contacts. The lock therefore retains
  history in `simulation/mechanism.py`, mirrors the numeric law in
  `web/mechanism.mjs`, and poses the standard viewer with public `setDriver`
  calls. Tests cover all 900 supported combinations and compare Python and
  browser state at 120 poses. The full interaction works in the project's
  exported demonstration; the ordinary shop viewer exposes pose channels
  but does not acquire the history controller by loading its manifest.
  Candidate requirement: a supported, portable way to retain and replay
  mechanism history across the machine's control surface. Whether that
  belongs in the framework, viewer or host is undecided. Filed here;
  triage open.
- **Faceted strict tangency can fail on a negative intersection volume.**
  `machinome test --faceted simulation/lock.py` reports dial/cam interference
  at −4.440892098500626e−16 mm³ and wheel 3/peg 3 at
  −4.440892098500626e−15 mm³. A reconfigured fitted peg also reports a
  positive 5.538349691151255e−7 mm³ intersection in the faceted representation;
  that is distinct from the negative-volume failure and is not asserted to
  have the same cause. Final faceted result: 8 passed, 6 failed, volume
  epsilon zero. The same 14 contracts pass with `--exact`, including sampled
  opening/relocking and 145 quarter-degree final-cam positions. No solids
  are skipped and no volume allowance hides the failures. The source's
  original exact pairwise overlap inventory is empty; documented 0.05 mm
  dial/lid axial seating stand-offs do not eliminate fitted-face tangency.
  Candidate framework investigation: distinguish negative-volume artifacts
  from true overlap and characterize faceted fitted-face disagreement.
  Filed here; triage open.
- **Finer STEP tessellation can open engraved-text seams.** The source dial
  is one exact solid. At `angular_deflection = 0.15`, its generated STL is
  not watertight according to trimesh and the faceted engine refuses it.
  At the import scaffold's 0.5 setting the mesh is watertight; the project
  retains that setting for the dial and 0.15 for the other parts. The root's
  `test_display_meshes_are_watertight` checks every delivered leaf. To
  reproduce, change only `Dial.angular_deflection` in
  `simulation/source/parts.py`, rebuild and run that contract; restore 0.5
  afterwards. Source: ignored `upstream/safe-lock.step`, SHA-256
  `70d467a15ce8b4dcf7ab081d23466474a9b07974d17be5638d78c61a6883291a`,
  fetched by `tools/fetch-source.py`. No STEP repair was made. Whether the
  defect belongs to tessellation, export or source tolerance needs isolation;
  no root cause is claimed. Filed here; triage open.

# Voron-2 (2026-09-13, Voron 2.4r2 source assembly)

Project: `projects/3D-Printers/Voron-2`, active change
`simulate-the-voron-2`, project evidence commit `235451b`. This entry is
historical evidence, not a requirement. The pilot ratified the separate cycle
`voron-faceted-contact`, implemented in an isolated bench from `main` at
`b768bdf979552751d016dd89c2f5814693134f9a`. Its accepted behavior and proof
are in the archived change; integration is authorized after clean-state
verification. No external issue was opened.

- **Negative faceted volume is rejected as assembly interference.** The
  unchanged source extrusions 1262 (horizontal) and 1388 (vertical) reproduce
  `assertNoSolidInterference` failure at −9.947598300641403e−14 mm³. Both this
  assembly check and `assertNotIntersecting` fail with `--faceted`; both pass
  with `--exact`. Direct CadQuery reports an empty exact intersection with
  zero solids. This was reproduced in `WTs/voron-faceted-contact` using the
  workspace venv and `PYTHONPATH` pointing at that bench; logs are ignored
  `_build/voron-corner-faceted.log` and `_build/voron-corner-exact.log`.
  Public reproduction: the project's
  `simulation/tools/corner_probe.py:SourceCorner` and companion tests.
  The initial project interpretation conflated the two assertion contracts:
  ADR-029 deliberately preserves non-empty faceted contact as a strict
  pairwise foul; ADR-040's whole-assembly check instead promises positive
  shared volume. The baseline `is_empty or volume == 0.0` branch rejected
  negative results too. Implemented fix: pass finite negative faceted
  candidates only in assembly integrity, keeping raw measurements,
  pairwise/fit strictness, all positive failures and exact-path behavior.
  No epsilon, source displacement, mesh repair or skipped component is the
  workaround: the project remains paused with its honest tests red. The
  original frame also has genuine fastener overlaps; a direct exact scan's
  54 positive results are recorded in the project, not waived by this fix.
  Related evidence: the Locks negative-volume finding above. Triage:
  scope ratified 2026-09-13 ("ratify, go on"), including implementation and
  fast-forward integration after validation. Resolution: the assembly check
  now passes this unchanged corner on both kernels; strict faceted pairwise
  still fails and both exact tests pass. Framework regression: 237 tests and
  72 subtests pass; both old-sign and positive-skipping mutations are caught.
  See `openspec/changes/archive/2026-09-13-voron-faceted-contact/validation.md`.
- **FIXED (cycle `select-a-step-product`, ADR-115). Duplicate STEP
  names still defeat generated selectors.** This document
  contains 118 products named `SOLID`; `machinome import-step` emits distinct
  Python classes with identical `part = 'SOLID'` selectors, then a build is
  ambiguous. CadQuery's convenience `Assembly.load` also rejects duplicate
  assembly names. The project's `simulation/tools/probe.py` traverses OCP
  document occurrence labels, retains identities/placements/colours, and
  extracts all 1,715 unchanged solids to individually addressable ignored
  STEP files. The 180-solid frame builds through ordinary `StepNode`.
  This repeats the YouCanBuildDog and orcahand findings. Selector changes are
  not part of `voron-faceted-contact`; workaround retained, triage open.
  **What shipped:** `part_index` and the identity-keyed generator
  described under the YouCanBuildDog and orcahand entries above, the
  same fix for all three findings. Not applied back to this project's
  own `simulation/tools/probe.py` workaround here — that remains the
  project's own choice on its own schedule (`machinome-studio/CLAUDE.md`,
  "Mechanical project work"); this entry records that the underlying
  framework gap identified across all three projects is closed.

# machinome-viewer bundle staleness (2026-09-14, shop floor, Pascaline-module)

Met opening the shop on port 9000 after fast-forwarding `machinome-viewer`
main to the `open-run-simulation` campaign branch (`f25c5a1`) and merging the
same branch into `machinome` main. Not a project finding; no mechanical
project's simulation code was touched. This is a `machinome-viewer`-owned
contract, `machinome_viewer/bundle.py`, recorded here because `workflow/`
is the one place these findings are kept; see `machinome-studio/CLAUDE.md`,
"machinome-viewer work".

- **`document_versions()` can promise a document the served bundle refuses.**
  The Pascaline module's exported document declared version 5; the browser
  reported "this viewer does not render" it, even though the merge that adds
  version-5 rendering was already on both mains and `machinome viewer` reported
  `documentVersions: [1, 2, 3, 4, 5]`. Cause: `machinome_viewer/widget/dist/
  machinome-viewer.js` is a gitignored build artifact (`.gitignore:14`), so
  `git merge --ff-only` moved the widget's TypeScript source and
  `package.json`'s `solidNodeDocumentVersions` field but left the primary
  checkout's built `dist/` at its last `npm run build` (546,459 bytes, built
  2026-09-08, declaring `[1,2,3,4]`) untouched. `bundle.py:document_versions()`
  reads `package.json` alone — the field that *did* move — so `describe()`
  reported five renderable versions while the file it also names as `path`
  could read only four. The docstring's claim that the two "can never
  disagree" holds only when `dist/` is rebuilt in lockstep with
  `package.json`; nothing enforces that, and no producer (`machinome build`,
  `machinome export`, shop session preparation) rebuilds the widget or compares
  bundle contents against the declaration before serving it. Worked around
  by hand: `npm run build` in the primary viewer checkout produced a
  659,294-byte bundle, md5 `baf972b885ce80ce03c532165ffffffa`, byte-identical
  to the campaign worktree's own build; re-fetching the same live session's
  `/api/sessions/<id>/viewer/machinome-viewer.js` after the rebuild returned that
  bundle and the document rendered. Evidence: session
  `kpvQF8FXYy8wrX-5xZI4XfhcCgPSQJyC` on the shop hub at port 9000,
  2026-09-14; before/after bundle sizes and md5 above are the reproduction.
  No `bundle.py` change was made. Candidate framework/viewer work: have
  `document_versions()` (or `describe()` generally) read what the built
  bundle itself declares rather than `package.json` alone, so a stale
  `dist/` cannot be described as current — or have the shop/framework
  compare bundle and declaration mtimes and warn before serving. Filed here;
  triage open.

# Pin tumbler lock (2026-09-14, running-command cancellation)

Recorded at the pilot's request while preparing
`projects/Locks/Pin_tumbler_lock` for `Time.running()` and updating the
shop's public API skill. Found in a minimal API probe before changing the
lock; this is not a failure observed in the lock's existing browser demo.
**Status: FIXED (cycle `cancel-stops-the-command`).** `cancel()` now
retires the command at once — status set, the entry removed from
`Run.active`, its reference to the run dropped — instead of only setting
its status: the input is free the moment `cancel()` returns, so a
replacement is accepted the same tick, and a cancelled command no longer
survives into a snapshot.

- **Symptom.** A Python running command's `cancel()` changes its status to
  `cancelled`, but the command continues moving its input and keeps owning
  it. A replacement request fails saying to cancel the command that is
  already cancelled. The skill therefore has to warn projects not to rely
  on cancellation to stop or replace a move.
- **Evidence.** First reproduced at framework `9238ef8`; reproduced again
  at `00398f4` on 2026-09-14 with the workspace Python environment. With
  `dt=0.02`, a 5 mm move over 0.2 s cancelled before the first tick still
  moves both the input and its carriage by 0.5 mm on the next tick. The
  handle reports `cancelled`, `admitted == 0.5`, and remains the one entry
  in `sim.commands`. A new move on the same input raises `ValueError`:
  `'feed' is already owned by <move feed cancelled: 0.5 admitted>`.
  In `machinome/simulation/run.py`, `Command.cancel()` only updates the
  status; `Run.integrate()` still asks every held command for admissions,
  `Command.admits()` does not exclude cancelled commands, and
  `Run._claim()` rejects any held owner. The public baseline is
  `openspec/specs/simulation/spec.md`, "Commands have one owner per input
  and report their outcome"; `Command.cancel()` itself promises to stop
  the command where it stands.
- **Skill text a fix would delete.** The shop's
  `shop-skills/machinome-api/SKILL.md`, added in shop commit `99611ce`:
  "Do not rely on it to stop or replace a move until the framework fixes
  this; `rate(input, 0)` releases an active rate, and restore/reset replace
  the run state." Releasing a rate or restoring state is not equivalent
  to cancelling one finite move while preserving other commands.
- **Candidate correction, not ratified.** Keep the existing
  `handle.cancel()` interface: stop admitting travel for that command,
  release its input so a replacement can be issued immediately, and keep
  the retired handle's `cancelled` status and already-admitted travel.
  Verify cancellation before the first tick and midway through a move or
  rate, immediate replacement, repeated cancellation, unrelated inputs
  continuing, and snapshot/restore behavior. No framework code changed.

Minimal reproduction: save this as `probe.py` in a directory with a
`pyproject.toml` containing `[tool.machinome]` and `model = "probe:Feed"`,
then run it with Python using the affected framework installation. It
needs no CAD build or viewer:

```python
from machinome.node import AssemblyNode
from machinome.motion.ports import Time
from machinome.motion.joints import Prismatic
from machinome.simulation import Driver, Sim

class Carriage(AssemblyNode):
    travel = Prismatic(axis=(1, 0, 0), range=(0, 12), unit="mm")

class Feed(AssemblyNode):
    time = Time.running()
    feed = Driver(default=0, unit="mm")
    carriage = Carriage()
    feed.drives(carriage.travel)

sim = Sim(Feed(), dt=0.02)
command = sim.move("feed", by=5, duration=0.2)
command.cancel()
sim.run(0.02)
print(command.status, command.admitted, sim.state, len(sim.commands))
# Observed: cancelled 0.5 {'carriage.travel': 0.5, 'feed': 0.5} 1
# Expected after cancellation before the first tick: no travel, no owner.
sim.move("feed", by=1, duration=0.02)  # observed: ValueError, already owned
```

# declare-controls-on-parts (2026-09-14)

- **A relation onto a coordinate the render OMITS makes a running root's
  document unpublishable.**
  **FIXED (cycle `publish-only-what-runs`).** The compiled program's
  coordinate table is now exactly the bank plus the ends its kept edges
  read and give; a relation onto an omitted part's own joint reaches no
  bank coordinate, so `_reaching_the_bank` was already dropping it, and
  the table no longer keeps its end after. The omitted node's fallback
  name is published nowhere and can no longer refuse the document. Met
  while building the cycle's
  `OmittedControl` fixture; it involves no control and is entirely
  pre-existing. `omit()` leaves a node "not linked, built, exported,
  fused or serialized", so `qualified_coordinates` never sees the
  omitted child and `instance_path` cannot qualify it — but the RELATION
  the parent's class body states is still compiled, and
  `compile_program` gives its driven end the `<ClassName>.<name>`
  fallback. `Program.published()._refuse_unqualified` then refuses the
  whole document. The practical shape: a machine with an optional
  subassembly whose joint a driver reaches cannot build at all with that
  option off, under a running root, even though the part is simply
  absent.
- **Evidence.** Reproduced at `33d8bf5` on 2026-09-14 with the workspace
  Python environment, on a fixture carrying no control:

  ```python
  # probe.py, beside a pyproject.toml with
  # [tool.machinome] / model = "probe:Machine"
  from solid2 import cylinder

  from machinome.motion.joints import Revolute
  from machinome.motion.ports import Time
  from machinome.node import AssemblyNode, Solid2Node
  from machinome.parameters import Flag
  from machinome.simulation import Driver


  class Arbor(Solid2Node):
      turn = Revolute(axis=(0, 0, 1), unit='deg')

      def render(self):
          return cylinder(r=5, h=2)


  class Machine(AssemblyNode):
      time = Time.running()
      fitted = Flag(True)

      crank = Driver(default=0.0, unit='deg')

      first = Arbor()
      spare = Arbor()

      crank.drives(first.turn, ratio=2.0)
      crank.drives(spare.turn, ratio=3.0)

      def render(self):
          self.spare.translate([20.0, 0.0, 0.0])
          if not self.fitted:
              self.spare.omit()
  ```

  Publishing `Machine(fitted=True)` succeeds. Publishing
  `Machine(fitted=False)` raises `UnsupportedLaw`: *"the program names
  'Arbor.turn', which is a FALLBACK derived from a class name rather
  than an instance path: the node it belongs to is not linked under the
  root ... Hold the node on its own attribute of its parent."* The
  advice is inapplicable — the node IS held on its own attribute; it is
  simply omitted.
- **Candidate correction, not ratified, and out of this cycle's scope.**
  `compile_program` could drop a relation whose end resolves to an
  omitted node, the way `declare-controls-on-parts` drops a control
  whose part this render omitted (its design §10): structure may vary
  with parameters, so a relation into a part that is not in the machine
  states nothing about the machine that is. The alternative — refusing
  at relation resolution with a message that says "omitted" rather than
  "not linked" — is worse, because it would still refuse a build the
  parameter legitimately asks for.
- **Not blocking.** The cycle's own fixture was reshaped to omit the
  PART (a leaf under the joint-bearing node) rather than the node
  carrying the driven coordinate, which is design §10's own case and
  needs no framework change.
# Pin tumbler lock (2026-09-14, migration to `Time.running()` under `bounds-read-other-coordinates`)

Recorded from the originating project's migration, run against the cycle's
worktree (`openspec/changes/bounds-read-other-coordinates/evidence.md`, "The
originating project"). Each entry is a finding outside the cycle's ratified
scope; **status: filed here; triage open** unless marked otherwise. No
framework code changed for any of them in that cycle.

- **The test runner's operation checkpoints double a leaf child's joint
  displacement under a running root.** **FIXED (cycle
  `checkpoint-the-joint`, ADR-114).** `machinome/manager/test.py:327`
  snapshots each ROOT CHILD's `operations` before every test and `:368`/`:383`
  restored them after; from the SECOND test on, the `set_keyframe(instant)`
  at `:344` appended the joint displacement a second time. The lock's five
  driver pins (leaves owning a `Prismatic`) then stood 0.1 mm deeper than
  their own coordinate said (`d1.lift` read `0.1000002`, the mesh sat at
  `x = 12.46` instead of `12.56`), and `_prepare()`, `render()` and a
  `set_state` round trip all left the fifth operation in place. Children of
  a sub-assembly were unaffected because the runner checkpoints only the
  root's own children.

  **Two factual errors in the original filing, corrected by the fix
  cycle's own evidence.** The claim that the project's previous UNTIMED
  model was immune is wrong: it is only RARER — an untimed root goes
  out of phase too, whenever a test binds a coordinate by hand between
  checkpoints, and before the fix that stranded a PERMANENT extra
  operation no later enumeration could remove
  (`openspec/changes/checkpoint-the-joint/evidence.md` §6, open question
  2). And the minimal reproduction below, re-run verbatim on this
  worktree, no longer reaches the defect on its own: the lock's own tests
  stopped stepping the runner's node when this wart was filed
  (`lock_under_test()` in `simulation/test_lock.py` builds a private
  lock), so nothing in the sequence binds the runner's tree outside the
  enumeration any more — it reports FOUR operations today, not the five
  originally recorded (`evidence.md` §8). The doubling this wart
  describes is reproduced instead on framework fixtures, in `evidence.md`
  §1, §3 and §7:

      a = load_node('simulation/lock.py:PinTumblerLock')
      a.set_keyframe(0); a._prepare(); a.build_stls()
      for _ in range(2):
          saved = {c: list(c.operations) for c in a.children}
          a.set_keyframe(0)
          for c, ops in saved.items(): c.operations[:] = list(ops)
      a.set_keyframe(0)          # -> d1 has 4 operations today, not the
                                  #    five originally recorded

  Cost to the project: `assertNoSolidInterference` reported
  `core should not interfere with d2 (intersection volume 0.103)` at ±90°
  from the second geometry test on; its geometry tests now build a lock of
  their own (`lock_under_test()`) rather than testing the node the runner
  hands it — a project change the pilot may now undo, since testing the
  runner's own node is safe again.

  **Root cause and fix.** A joint identified its previous placement by
  the OBJECT IDENTITIES `place` recorded in
  `node.__dict__['_joint_motion']`, while the runner's checkpoint restore
  replaces a child's operation list BY CONTENT — deliberately, so a
  leaked operation inserted anywhere is reverted. After a restore the two
  disagreed and `Joint.clear` found nothing to remove. Fixed by
  identifying a placement by the MARK its operations carry instead
  (`_joint_slot`, ADR-093's declaration slot), stable across a wholesale
  list replacement, behind a new seam (`re_place_declared_joints`) the
  runner's restore and the refused-`set_state` rollback
  (`CoordinateDelivery.restore`) both call to re-place a child's joints
  from the coordinates it holds — neither of the two candidate fixes this
  entry originally proposed (both examined and rejected in the cycle's
  `design.md`, decision 3). A second, narrower gap the fix's own design
  surfaced — an untagged placement the restore's re-place makes can
  outlive an enumeration that leaves its coordinate unbound — is closed
  by making `clear_solved` (ADR-099) drop a coordinate's joint along with
  its value literally, rather than delegating to a sweep that cannot see
  an untagged operation. Full measurement in
  `openspec/changes/checkpoint-the-joint/evidence.md`.

- **`machinome build` refuses a coordinate bound by a CHILD-declared relation
  and read by a ROOT-declared one as doubly bound.** **FIXED (cycle
  `a-read-is-not-a-binding`).** The producer's epilogue in
  `symbolic_document` now puts each assembly's record of what its own
  previous phase bound back beside the coordinates it restores, so the
  re-render clears and re-solves exactly as the pose did; the lock's
  shape publishes with its five lift relations in `Plug`'s own body,
  measured on a copy of the project. Original filing, with two
  corrections this cycle measured, below. With
  `key.insert.drives(p1.lift, law=…)` in `Plug`'s body and
  `plug.p1.lift.drives(d1.lift, ratio=-1)` in the root's, the symbolic
  publication pass (`core/serializer.py:249` → `qualified.py:311` →
  `couplings.py:1898`; the filing cited `serializer.py:240`, which is a
  comment — the call is the RE-RENDER's `drive_tree` at :249, not the
  walk's at :227) raises

      DoublyBound: plug.p1.lift would be bound by the relation key.insert
      drives p1.lift and by the relation plug.p1.lift drives d1.lift. A
      coordinate has exactly one binder in one enumeration of the tree ...

  The second relation READS `plug.p1.lift`; the message names a relation's
  source as a binder. Every untimed pose, every `Sim` and the whole test
  suite accept the same declarations; only the publication pass refuses
  them, evidently by solving the root's relation backwards against a
  symbolically bound driven end. Worked around by declaring all five lift
  relations in the ROOT's body. Candidate fix: the publication binder's
  symbolic binding of every coordinate must read as "bound by the run" to
  `_step_relation` the way a `RunBinder` does, so a relation whose driven
  end it holds is recorded as solved rather than inverted.

  Two corrections the cycle's evidence makes to that filing. The refusal
  is NOT in the publication walk: that walk already records every
  relation as solved by the run, exactly as the candidate fix asks, and
  it is the RE-RENDER the producer runs in its `finally` that refuses.
  And it needs a tree an ENUMERATION posed — `machinome build` poses and
  renders before it writes the viewer snapshot — so a never-posed tree of
  the same class always published, which is why the suite never saw it.

- **A `.repeat()` child's PORT cannot be published under a running root.**
  **FIXED (cycle `publish-only-what-runs`).** `Program.published()`
  refused the lock's spring bank:

      UnsupportedLaw: the program names 'PenSpring.height', which is a
      FALLBACK derived from a class name rather than an instance path ...
      Hold the node on its own attribute of its parent.

  Root cause located in `machinome/simulation/program.py`:
  `compile_program` registers a program node for EVERY end of every candidate
  relation (`_relation_edge` → `_register`) before `_reaching_the_bank` drops
  the edges that reach no bank coordinate, and `Program.nodes` kept the
  dropped edges' ends. `_refuse_unqualified` and the published
  `intermediates` list then saw nodes nothing in the program computes — the
  repeated springs' height ports, named by their class fallback. The run
  itself was untouched (the edge is not compiled); only publication refused.
  Fixed exactly as the candidate fix here proposed: `compile_program` now
  reduces `nodes` to the bank plus the ends the kept edges read and give,
  right after `_reaching_the_bank`, so the dropped springs' ports leave
  nothing behind for `_refuse_unqualified` or `intermediates` to see. The
  lock named its springs `s1`…`s5` as a workaround meanwhile; restored to
  `springs = PenSpring().repeat(5)` with the driving relation grouped by
  `&` (the shape the project carried before its migration to
  `Time.running()`), the lock now publishes, names none of the five
  copies, and each spring's height still follows its own pin
  independently — measured in the cycle's `evidence.md`. The shop's API
  skill said a `.repeat()` child under a running root may own neither a
  joint nor a port a relation drives; the port half of that claim is now
  false.

  **The other half — a `.repeat()` child that owns a JOINT — is a
  DIFFERENT, still-open refusal, measured and left alone
  (`evidence/probe_repeat_joint.py`).** It is not reached through
  publication at all: `qualified_coordinates` (`program.py:227`) calls
  `driver_id` while enumerating the BANK, and the id grammar
  (`_LEGAL_SEGMENT`) raises `DriverIdError` on the list-held name
  (`pins-0`) before any program exists — inside `Sim.__init__` via
  `release_tree`, so the machine cannot be SIMULATED, let alone
  published. No pruning of the program's node table can reach it; only a
  change to what a qualified id segment may contain (the grammar's own
  documented bijective-sanitization extension) could, and that is a
  published-document contract the viewer reads, deliberately out of this
  cycle's scope (design.md decision 6).

- **The sampled search of a constraint costs about a whole program pass per
  sample.** On the lock (five `piecewise` lift laws of 8–26 knots feeding a
  two-sided plug bound) an active tick measured 193–195 ms against 3 ms
  idle, `_SUBDIVISIONS` samples each evaluating the five laws twice
  (`f(start)` recomputed per sample), paid even when only the plug turned.
  The cycle's review added the static-reads shortcut — a stretch in which no
  read moves takes the exact self-only path — which brought the turning tick
  to 4.7 ms and the insertion tick to 45 ms. What remains for a later
  performance cycle: evaluate `f(start)` once per stretch per edge instead
  of per sample, sample the sub-program once for the two sides of one
  coordinate that read the same coordinates, and consider fewer samples with
  a bracketed refinement when the constraint's reads are affine over the
  stretch. Numbers in the cycle's evidence.

# a-read-is-not-a-binding (2026-09-14, the producer's restore)

Findings outside that cycle's ratified scope, measured in
`openspec/changes/a-read-is-not-a-binding/evidence.md` §6; **status: filed
here; triage open**. No framework code changed for either.

- **The enumeration's fixpoint leaves `_bound_by = None`, and a value it
  bound therefore reads as trustworthy in a LATER enumeration where the
  same value bound in a phase would defer.** `run_deferred` (ADR-099) runs
  with no phase current, so `phase.note_bound` stamps nothing, and
  `ResolvedEnd.bound()` reads that as "bound outside any enumeration;
  nothing left will reclaim it". It is harmless while `clear_solved` drops
  such a value at the owning assembly's next phase — the record the
  producer was the one known thing to destroy — but whether the fixpoint
  should bind under the stating assembly's phase at all is a couplings
  question, and a bigger one than that defect.

- **`_ran_in_enumeration` is the other assembly-level mark the
  publication's phases overwrite, and the cycle restored only
  `_solver_bound`.** Nothing measured depends on it: the re-render opens a
  new enumeration, against which a stale mark compares unequal either way.
  Left alone deliberately rather than fixed blind.

# Execution plan (2026-09-14, autonomous wart fixes)

Triage of every entry above still open, made under the pilot's standing
delegation ("fix what you can that does not need my attention"; opus
proposes, sonnet applies, the reviewing agent's adversarial pass is the
ratification gate). Ranked by benefit over cost. Each item below is a
standalone two-commit cycle stacked on branch `fix-warts` (worktree
`WTs/fix-warts`, base bd74132), one after another, so integration is one
fast-forward the pilot performs or declines. Nothing is integrated or
pushed by this plan.

## Fix now, in this order

1. **`Command.cancel()` does not stop the command** (Pin tumbler lock,
   2026-09-14). Spec violation with a reproduction; the shop skill carries
   a warning a fix deletes. Cycle `cancel-stops-the-command`.
2. **The program names coordinates it does not compute**: a `.repeat()`
   child's driven port refuses publication, and a relation onto an omitted
   child's coordinate refuses the whole document (Pin tumbler lock and
   `declare-controls-on-parts`, 2026-09-14). Both root-caused in
   `compile_program`'s node registry. Cycle `publish-only-what-runs`.
3. **The runner's checkpoints double a root leaf's joint displacement under
   a running root** (Pin tumbler lock). Wrong geometry from the second test
   on, root-caused at `manager/test.py`. Cycle `checkpoint-the-joint`.
4. **A child-declared relation read by a root-declared one publishes as
   `DoublyBound`** (Pin tumbler lock). False refusal of a legal shape,
   located in the publication binder. Cycle `a-read-is-not-a-binding`.
5. **`machinome import-step` emits a `render()` that does not parse** when
   every placement is the identity (orcahand). Trivial. Folded into 6.
6. **`StepNode` cannot select between products sharing a name**, and
   `import-step` scaffolds selectors it cannot build (YouCanBuildDog,
   orcahand, Voron-2: 3, 15 and 118 duplicates). A stable per-occurrence
   selector emitted by the importer whenever a name is not unique. Cycle
   `select-a-step-occurrence`.
7. **A leaf's artifact is imported into its parent's `.scad` by bare
   filename**, so an assembly in another package renders it as nothing
   (Thor). Silent wrong render. Cycle `import-the-artifact-by-path`.
8. **`StepNode`/`StlNode` with an absent file fail late inside
   `mtime_ns`** (Internal-Cycloidal-Actuator). Validate at construction,
   naming class and path. Cycle `name-the-missing-file`.
9. **The test runner counts `SkipTest` and `expectedFailure` as plain
   failures** (Internal-Cycloidal-Actuator). Cycle `honour-skip-and-xfail`.
10. **Interference failures name the leaf, not its path** (3DPrintedClocks
    mantel 34, Thor). Cycle `name-solids-by-path`.
11. **`%` on a symbolic value disagrees across runtimes** (item 7). A
    `remainder` in `machinome.math` with a parity case. Cycle
    `expression-remainder`.
12. **`self.children` reads empty during `simulate()`** and a loop over it
    silently applies nothing (AlbertPro). Cycle `children-refuse-early-reads`.
13. **`tools/generate_parity_fixture.py` cannot run from a worktree**
    (item 9) and **`machinome snapshot --preview` sends a bare `--preview`**
    (item 14). Tooling; one small cycle `tooling-paths-and-flags` if time.
14. **A `.repeat()` copy's joint arguments resolve before `index` exists**
    (`joint-frame-follows-declarer`, three projects worked around). Cycle
    `resolve-repeated-joints-per-copy` if time.
15. **Generated-artifact freshness** (3DPrintedClocks, 2026-09-10): make the
    test artifact index self-healing when an artifact is absent, and audit
    the source-adapter fingerprint. Investigation first; if time.

## Held for the pilot (a product, architecture or policy choice)

- Negative faceted volumes in STRICT pairwise assertions (items 13, Locks,
  Voron-2): `voron-faceted-contact` deliberately kept pairwise strictness;
  relaxing it reverses that decision.
- A driver's `range` enforcement policy (AlbertPro): clamp, refuse or leave.
- Dimensioned literals and number-plus-token in the parameter algebra
  (item 8, Pascaline): language design.
- An exact boolean that returns empty for an overlapping pair
  (YouCanBuildDog), an indeterminate pair verdict (science-jubilee) and a
  per-pair exact fallback when the faceted engine refuses a mesh (Thor):
  kernel semantics and sweep cost.
- A public interference inventory `solid_interference(node)` (Thor): a new
  public contract; proposed only after item 10 lands, if the pilot wants it.
- `exact-solid-index-bounds`: reverses two ratified spec sentences; filed,
  left for the pilot to open.
- Mechanism history across the control surface (Locks): framework, viewer
  or host is undecided.
- The seams recorded as "needs its own sighting": hand-written motion
  versus a site joint on one child; naming a data-built child in a
  relation; a descendant's hand-written read of a deferred relation; a
  subclass's inner joint slot; indexing a repeat in a class body.
- `solid import-stl` (AlbertPro): a new command.
- The viewer bundle staleness entry belongs to `machinome-viewer`, not
  this branch.

## Already fixed, recorded here so nobody reopens them

- `assertNoDisconnectedSolids` takes the exact path for an exact solid
  (YouCanBuildDog, Thor): `_routes_exact` in `machinome/test.py`.
- Stale author-bound joint values (v8-engine): `whole-tree-fixpoint`.
- Negative faceted volume in the ASSEMBLY check: `voron-faceted-contact`.

# import-the-artifact-by-path (2026-09-15, found while fixing)

Findings outside that cycle's ratified scope, measured in
`openspec/changes/import-the-artifact-by-path/evidence.md` ("Noticed and
left out of scope"); **status: filed here; triage open**. No framework
code changed for either.

- **A rigid leaf's own `.scad` stops describing its geometry after the
  first build: it becomes a self-import of the STL it exists to
  regenerate.** Build 1 writes it as the leaf's own geometry (e.g.
  `cube(size = [10, 10, 10]);`); once the STL is current, `assemble()`'s
  up-to-date branch sets `self.model = self.artifact_import(self.local_stl)`
  (`base.py:862-863`) and then calls `generate_scad()`, so the file that is
  supposed to be able to rebuild the STL from scratch merely imports it.
  It resolves (same directory), so it is not this change's bug.
  `FusionNode`'s own `.scad` is written the same self-importing way, but
  harmlessly: its STL is produced natively (OCCT or manifold3d), never by
  OpenSCAD from that `.scad`.
- **`self.mesh_scad_file` / `self.mesh_stl_file` are vestigial.** Nothing
  in `machinome/` writes or reads them beyond the assignment at
  `base.py:711-712`.

# Calculators (2026-09-15, markings applied after the part is made)

Recorded at the pilot's explicit request, from
`projects/Calculators/Curta-Type-I-3x` and
`projects/Calculators/Pascaline-module`. These are empirical findings, not
ratified requirements or permission to implement a framework change. No
framework source was modified; `machinome/node/base.py`,
`machinome/core/serializer.py` and the viewer's `widget/src/tree.ts` were
read to locate the limit. The proposed design is
`workflow/docs/markings.md`; **status: cycle 1 of 3 implemented** — OpenSpec change
`carry-markings-on-a-part` (archived 2026-09-15, ADR-120) gives a rigid node a
declared zero-volume `Marking` with `Svg` artwork and `Wrapped`/`Flat` placement,
a decal artifact with its own currency, and an additive `markings` document
field; on branch `markings`, not yet integrated. Still open: drawing it (the
viewer's cycle), DXF artwork (its chains only close at 0.01 mm and read as the
stencil), and `process` with the cut file and multi-material 3MF (0.8).

- **A part can carry only one colour, so a marking the maker applies after
  manufacture cannot be modelled at all.** `color` is one class attribute per
  node (`base.py:569`), validated to one `#RRGGBB` and applied whole-node
  (`_colorize`, `base.py:1002`), published as one scalar
  (`serializer.py:645`), and resolved by the viewer to exactly one
  `MeshStandardMaterial` per mesh (`machinome-viewer`,
  `machinome_viewer/widget/src/tree.ts:55,106`). Nothing in that chain names
  a region of a part or a finishing step. A project wanting digits on a
  number roll must either declare each glyph as its own leaf — which adds
  parts no maker handles, volume, and (after 0.8) mass, and puts phantom
  solids in front of every clearance and interference contract — or drop the
  markings. Both calculators dropped them.
- **The consequence is a calculator that cannot show its answer.** The Curta's
  ten number rolls are modelled and driven (`FittedDialType1`/`Type2` in
  `simulation/dial_fits.py`, on `Revolute` joints in `simulation/registers.py`,
  each carrying the register value through its port), so the register value is
  computed correctly and is unreadable: the digits are not on the part. The
  Pascaline's `DigitDrum` (`simulation/parts.py`) is the same, one `StlNode`
  with one colour turning `DIGIT_STEP` per entered digit. Driving the crank in
  the browser produces no answer, which for a calculator is the whole point of
  the machine. The same gap covers every dial face, index mark, scale, label
  and part number in the catalogue.
- **The upstream already states the concept the framework is missing.** The
  Curta ships its markings three ways: as paint and vinyl artwork
  (`Manual/Painting/`, eleven DXF; `Drawings/`, the same as SVG;
  `Drawings/cricut-images/`, PNG with a sizing table — `upper_housing_numbers`
  is sized by width, 224.8 mm, being an unwrapped circumference); as a
  co-printed variant (`Mods/Printed Lettering/`, the body STL plus one STL per
  glyph — `results dial - digit 0.stl` through `digit 9.stl`, `upper housing -
  digit 1.stl` through `digit 11-2.stl`, the sleeve's `A/C/R/T/U` and two
  arrows — each set beside a `.3mf` grouping body and glyphs as one
  multi-material object); or not at all. **One part, several colour bodies, one
  manufacturing unit** is what those file names say and what 3MF expresses
  natively. Candidate requirement: a declared, zero-volume surface marking on
  a leaf, placed by cylindrical wrap or on a plane, carrying artwork, a colour
  and a process — drawn by the viewer, excluded from every solid contract and
  from the part inventory, and (with 0.8's process and material) exported as
  the nominal flat cut file or the multi-material 3MF the maker actually uses.
  Whether a co-printed marking is geometry is a product decision held for the
  pilot. Cycle 1 implemented as `carry-markings-on-a-part` (ADR-120), see the
  status above; the co-printed question stays with the pilot for cycle 3.

# name-the-missing-file (2026-09-15, found while fixing)

Findings outside that cycle's ratified scope, from
`openspec/changes/name-the-missing-file/proposal.md` ("Out of scope") and
`design.md` (reviewer's note 1); **status: filed here; triage open**. No
framework code changed for either.

- **The four adapters refuse a missing DECLARATION inconsistently.**
  `StlNode` and `StepNode` raise `ValueError` naming the class
  (`stl.py:162`, `step.py:476`). `JScadNode` raises a bare `Exception`
  that names only `"OpenJScadNode subclass"`, never the actual subclass
  (`jscad.py:28-30`). `OpenScadNode` has no check at all: an
  undeclared `scad_source` reaches `os.path.join(basedir, None)` and
  raises `TypeError: join() argument must be str, bytes, or os.PathLike
  object, not 'NoneType'` (`openscad.py:40`), naming neither the class nor
  the attribute. This cycle adds a fourth failure family — a *declared but
  absent* file — that IS consistent across all four (`FileNotFoundError`
  or `ValueError`, always naming the class); the pre-existing
  *undeclared* family above it is not touched.
- **The builder's own wrapper text reads as broken English and names the
  model, not the node.** `Builder._start()` wraps a load-time failure as
  `f'{self.path}: failed to {stage} project: {exc}'` (`builder.py:356`,
  stage `'load'` or `'inspect initial sources'`), e.g. `parts:MissingStl:
  failed to load project: ...` — "failed to load project" reads oddly for
  a single model reference, and `self.path` is the CLI's model argument,
  not the node whose declaration was wrong; for a leaf nested inside an
  assembly the wrapper still names only the root (`evidence.md`,
  measurement 4/"After"). This cycle's own message, inside `exc`, does
  name the node; the wrapper around it is untouched.

# honour-skip-and-xfail (2026-09-15, found while fixing)

Findings outside that cycle's ratified scope, from
`openspec/changes/honour-skip-and-xfail/proposal.md` ("Out of scope") and
`design.md` ("Reviewer's notes (ratification, 2026-09-15)", note 1);
**status: filed here; triage open**. No framework code changed for any of
these.

- **The runner keeps the LAST failing instant's traceback, not the
  first.** `run_test`'s `error` is rebound on every raising instant
  (`manager/test.py`) and only the last is printed, so a method that
  fails at instant 0 and again, differently, at instant 2 reports
  instant 2's traceback. This change only stopped a SKIP from becoming
  that traceback (`error` is now set in the `except Exception` arm
  alone); which real failure is reported when several instants fail is
  left exactly as it was.
- **No failure report names the instant it happened at.** `FAIL!`'s
  traceback shows where in the method's own source the assertion raised,
  never which declared instant (`0`, `0.5`, `1`, ...) it raised at under
  `@testing_steps`/`@testing_instant`. A maker reproducing a sweep
  failure has to re-run the method by hand to find the instant.
- **A non-skip exception from `setUp`, or any exception from
  `setUpClass`, aborts the run without a verdict.** `run_test` now
  catches `unittest.SkipTest` from `setUp` and reports the method
  skipped; any OTHER exception `setUp` raises still escapes `run_test`
  uncaught, as does anything `setUpClass` raises, and `handle` catches
  only `StopTestRun` — so the run stops with a bare traceback, no
  summary line, and no verdict for the tests that would have followed.
  `unittest` itself reports these as ERRORS, distinct from failures, and
  keeps running the rest of the suite; `machinome test` has no error
  classification at all, for a set-up exception or any other.

# read-the-driven-coordinate (2026-09-15, found while fixing)

Findings outside that cycle's ratified scope, from
`openspec/changes/read-the-driven-coordinate/proposal.md` ("Non-goals"),
`design.md` ("Open Questions", §1, §4, §11 and the dated "Implementation
notes") and `tasks.md` 9.1; **status: filed here; triage open**. The cycle
itself is ADR-121, which gives a relation whose source group names its own
driven end a meaning and integrates it piece by piece; nothing below was
implemented by it.

The pilot's retained-angle clearing requirement,
`workflow/docs/curta-retained-angle-clearing.md` (Curta Type I 3x, branch
`direct-operation`, checkpoint `b285393`), was **taken up as this change**.
Its items 8 (replay through the independent viewer, whose version 6 execution
is that repository's own cycle) and 9 (the Curta's own migration) stay open,
and the shape item 9 needs is stated in the change's design.md §12.

- **A gate with no WIDTH is not refused, and the framework cannot tell one
  from a band.** A self-read gate whose disengaged state is a single value of
  the coordinate — `wheel % 360 > 0` — is not a gap, and the distinction
  between it and a band is numeric, not syntactic: refusing every gate whose
  disengaged interval is narrow would need a number nobody can justify. It is
  documented in `docs/scenarios.rst`, pinned by `KnifeEdgeTest` asserting only
  what the framework promises, and left as ADR-121's open question 1.
  Implementation found that such a gate HELD in every case probed — ratios
  `1`, `7/3`, `0.7` and `π`, digits `108`, `107.3` and `12.345`, both
  directions, two step sizes — because `_land` walks the crossed nodes in
  postorder with the others at their near-side branches, so coincident `floor`
  and comparison surfaces land the coordinate exactly ON the surface where the
  comparison reads disengaged. That is the landing's arithmetic and not a
  promise: a single float is still not a gap, and nothing guarantees another
  model's numbers land on the surface rather than past it.
- **`a.drives(a)`, one to one, still deadlocks into `UnreachedCoordinate`
  instead of naming itself.** ADR-100 declined to widen its shared-coordinate
  refusal to the one-to-one shape and ADR-121 does not either: recognition is
  scoped to a relation naming SEVERAL ends, which is the only shape that is
  forward-only, so `a.drives(a)` is not checked at class definition at all.
  Measured on this worktree (`evidence.md` §1 E): it raises
  `UnreachedCoordinate: wheel.turn drives wheel.turn: nothing bound either
  end` at the close of the enumeration, which says nothing about the shape. A
  one-to-one self-read has no second source to carry slope, so the skeleton
  test would refuse every such law anyway — the message, not the verdict, is
  what is wrong.
- **ADR-113's pushing test is net over the stretch, not local at `t*`.**
  Recorded by ADR-113 itself and untouched here, but a self-read gate makes
  the limit easier to reach: an input that pushes a coordinate over the first
  half of a stretch and is DISENGAGED over the second is counted as pushing.
- **A driven GROUP with a self-read is refused, and lifting it needs a joint
  walk.** `Edge.increments` walks ONE plan per driven end, so a member reading
  a sibling would need that sibling's path while the sibling's own walk is
  cutting it at its own crossings — a joint walk over several plans that
  nothing defines yet. The rest rule is undefined for such a group too: one
  mixing a self-read end with a plain driven end would leave the plain end
  unbound at rest. Refused at class definition by name (design.md §1); no
  mechanism in the campaign has asked for the shape.
- **TAKEN UP as `cut-at-the-kink` (ADR-123): a kinked but piecewise-affine
  skeleton fell to the 64-sample search where an exact path exists.**
  `_affine_in_sources` called a CALL non-affine, so a skeleton gated by
  `clamp01` — two kinks whose pieces are each affine — was not affine, the
  driven coordinate's own path was not affine in the fraction, and every
  self-read crossing was SEARCHED rather than solved. That is the Curta's own
  shape, and it was measured: `Clearing` (affine skeleton, solved) ran at
  **1 349 ticks/s** and 99 graph evaluations per tick, `CurtaInterface`
  (`clamp01` window, searched) at **24.4 ticks/s** and 2 861 — about 29 times
  the cost, six dials at 64 samples per piece plus the bisection behind each.
  Re-measured at 27.2 ticks/s after the closure's fixes. `cut-at-the-kink`
  classifies `abs`, `min` and `max` as CONTINUOUS SELECTIONS, cuts the path
  at their breakpoints — recording nothing — and solves each piece:
  `CurtaInterface` now pays 603 evaluations per tick at 130 ticks/s, and
  `Clearing` and `Train` are unchanged to the evaluation.
- **A repeated child's JOINT coordinate cannot be banked under a running root,
  so a `.repeat()` self-read cannot be a running machine.** Pre-existing and
  already recorded under the fix-warts campaign; recorded again here because
  it is what stops the broadcast self-read from having a corpus scenario.
  Measured on the base tree `cd3e6ca`, with no self-read in sight:
  `DriverIdError: cannot qualify driver 'turn' through node segment
  'wheels-0': a qualified driver id must be a legal identifier …`. The
  couplings-level resolution rule ADR-121 ratifies IS implemented and tested
  directly (`SelfReadTest::test_each_copy_of_a_broadcast_reads_itself`: four
  records, each copy reading its own slot), and the export spec's generator
  list never named `.repeat()`, so the ratified contract is met; only the
  change's design.md §10 prose asked for something unattainable.
- **`docs/scenarios.rst` was stale on ADR-113 (fixed in this cycle).** Its
  "refused by name, each a later cycle's to lift" list still said a range
  bound naming a SECOND coordinate was not sayable, which
  `bounds-read-other-coordinates` (ADR-113, 2026-09-14) had already
  implemented as `Bound(expression, reads=(...))`. Task 8.1 replaced that
  bullet with the continuous-read refusal this cycle adds. Filed as a finding
  because the miss is a class: a cycle that adds a capability has to sweep the
  narrative documentation's refusal lists, and nothing checks that it did.

# select-the-source (2026-09-15, found while fixing)

## Originating Curta follow-up: seconds per Python tick (2026-09-15)

**Status: TAKEN UP as `evaluate-only-what-moves` (ADR-124), 2026-09-16.**
`cut-at-the-kink` (ADR-123) measured the shape of this cost and stated
plainly that it did not claim to move it; `evaluate-only-what-moves`
took it up. Measured on this worktree: 83.7 % of a Curta tick was
`GraphValue.evaluate` recomputing, at every one of 64 samples, the 89–98 %
of a followed graph that no source moving on that tick's path can
change. The fix computes that standing part once per graph per tick and
reads it back at every later point, unconditionally and structurally —
no knob, no declaration, no sampling decision.

**Before → after**, read-only against the originating project (branch
`direct-operation`, HEAD `9fb725f`):

| measure | before | after |
| --- | --- | --- |
| `running_probe --ticks 3`, seconds per 0.1-s tick | 3.279 / 3.273 | 0.727 / 0.727 (4.5×) |
| committed snapshot after three ticks (SHA-256) | `dda09193…` | `dda09193…`, identical |
| `simulation/test_running.py` + `test_running_clearing.py` | 843.18 s | 274.17 s (≤ 1/3) |

**Two mechanisms remain, measured and deferred to their own cycles, not
taken up here:**

- **`declared_ports` is re-walked from every call, not memoised by
  class.** 61 % of construction (5.46 s → 1.98 s memoised alone) and
  12.5 % of a tick (3.27 s → 2.82 s memoised alone; 0.294 s with
  `evaluate-only-what-moves` together). Now the biggest remaining item.
  It needs its own answer to when a class's port enumeration may be
  trusted to stand — a declarative class is built dynamically by
  `.repeat()`, so a memo keyed by class either holds classes alive or
  needs a weak key. **Open.**
- **A per-PIECE classification** (`cut-at-the-kink` design.md §8's
  question, now measured): substituting every kink whose level keeps one
  sign over the piece would make 192 of the Curta's 200 searched
  skeletons solvable (160 constant, 32 kinked, 8 still curved). Not
  taken: it MOVES a crossing located by search to the solved answer —
  every recorded crossing would move — and it makes the classification
  depend on which piece you are in, which ADR-123 deliberately kept
  static. After `evaluate-only-what-moves`, its remaining prize is small
  (21 % of the post-change tick against the port enumeration's 56 %).
  **Open.**

A finding for machinome-viewer, not proposed there: its TypeScript run
has the same whole-graph-walk shape and would take the same win, with no
document or flag change owed to it.

Below is the original finding, as filed, for the record.

**Status (as filed): recorded; triage open.** The pilot explicitly chose to keep
implementing the Python Curta, not prepare a performance handoff or start a
framework fix. No viewer performance claim is made here.

- **Symptom:** the source-backed `OperatingCurta` runs correctly in the
  exercised addition, carry, release/replay and clearing cases, but Python
  stepping is not interactive. The project must use bounded timing probes
  and wait minutes for a short mechanical regression.
- **Evidence:** framework `0b0f02ae743f4143fb235b0b0dba59d7f48d05ec`
  (ADR-122), project `Calculators/Curta-Type-I-3x`, `direct-operation`
  implementation in progress above `6a00abe`. From that project, with the
  workspace venv, `PYTHONPATH="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
  ../../../.venv/bin/python -m simulation.tools.running_probe --ticks 3`
  measured construction at 4.973 s and three 0.1-s simulation ticks at
  **3.3797, 2.9304, 3.3858 s** wall time. The ten tests in
  `simulation.test_running`, `simulation.test_running_laws`, and
  `simulation.test_running_clearing` passed in **528.874 s**. There are 17
  retained dials and 15 retained carry sliders, with carriage-selected
  physical associations and own-coordinate clearing/latch comparisons.
  Runtime stack samples repeatedly visited crossing-search expression
  evaluation; they do not establish a complete cost attribution.
- **Workaround:** keep inactive own-read comparison levels away from their
  boundary without changing active mechanical thresholds; use bounded
  probes while developing. Expanding piecewise profiles into comparison
  expressions was tried and reverted after increasing tick time to roughly
  9–11 s. No arithmetic shortcut or alternate state bank was substituted.
  Reproduction and current limitations live in the project's
  `simulation/docs/direct-operation-implementation-2026-09-15.md`.
- **Skill text this would delete:** none identified. This is an empirical
  usability/performance finding extending the searched-crossing findings
  above, not a proposed new capability or a measured viewer failure.
- **Proposed interface:** none. Preserve the current retained-state,
  selection, stop and transactional semantics; optimization strategy and
  performance acceptance criteria remain unratified.

## Findings from the framework cycle

Findings outside that cycle's ratified scope, from
`openspec/changes/select-the-source/tasks.md` 10.1, `design.md` (§2, §7,
§10 and "Risks / Trade-offs") and `evidence.md` ("Out of scope, found while
applying" and "Review closure (round 1)"); **status: filed here; triage
open** except the last entry, which was fixed inside the cycle and is
recorded so nobody reopens it. The cycle itself is ADR-122, which lets a
union of dependencies that every selection breaks compile as a BLOCK ordered
once per piece of a tick; nothing below except that last entry was
implemented by it.

The pilot's shifted carry association requirement,
`workflow/docs/curta-shifted-carry-association.md`, is what the cycle took
up; the Curta's own migration (item 6 there) and the viewer's execution of a
version 7 document (item 7) are open in their own repositories.

- **A stop on a block coordinate is never SOLVED.** A block's gives are classified
  non-affine by construction (`Edge._end_shapes`), so `Run._locate` searches every
  stop on one: 64 samples plus bisection of the WHOLE block per event. Measured
  17.2 ms for the tick that drives `RangedBlock`'s lever into its range against
  1.3 ms for a quiet tick of the same block (`tools/bench_selection.py`). A later
  cycle could classify a block give affine per branch vector and take `_piecewise`.
  **Still open.** `cut-at-the-kink` examined it and found a DIFFERENT mechanism:
  `_end_shapes` returns nothing for a block not because a block's value is curved
  but because a block has no single expression until a branch vector is fixed and
  the ORDER its members run in may differ from piece to piece, so classifying a
  give would mean classifying it per branch vector AND proving the order stable on
  the piece — ADR-122's territory, not a kink in an expression. That cycle
  asserted `RangedBlock`'s tick cost does not move (16.0 ms/tick against its
  recorded 16.1). Deferred; nothing has asked for the speed yet.
- **`Program.sources` treats a block as ONE node.** Every input reaching any member
  is a candidate for a stop on any other (`['crank', 'shift', 'spin']` for
  `carry.travel` in `RangedBlock`); `_pushes` filters it per tick, so the answer is
  right and the cost is one extra propagation per spurious candidate on a blocking
  tick only. Deferred.
- **A block member driving a GROUP is refused by name.** The fold that decides an
  active dependency is per driven end off that end's own skeleton, and a group's
  ends are claimed and bound together. No mechanism has asked for the shape.
- **A `sign`-gated dependency is never switched.** `_branch_of` gives `sign` its zero
  only where the level is EXACTLY zero, a point and not an interval, so the fold
  cannot fold it and a cycle gated only by `sign` is refused at construction —
  intended, and documented in `docs/driving.rst`, but a shape an author could
  reasonably expect to work. A comparison says the same thing and is switched.
- **FIXED by `cut-at-the-kink` (ADR-123): `_affine_in_sources` called any CALL
  non-affine, so a `clamp01` in a selector's level sent it to the 64-sample
  search** — pre-existing (recorded under `read-the-driven-coordinate`), and the
  reason the Curta's own migration had to write its association as comparisons
  rather than the pose model's `1 − clamp01(abs(…))` hat
  (`simulation/transmission.py:24`), which is not a jump node at all. A
  selector's level is located through `plan._partition` like any other, so a
  kinked one is now solved for free; no block fixture has one yet.
- **ADR-113's one-input pushing probe cannot see a push that needs TWO inputs
  moving together.** A clutch `(shaft & sleeve).drives(wheel.turn, law=s * (v > 0.5))`
  whose sleeve engages mid-tick while the shaft turns, the wheel declaring a range it
  reaches only after engagement, refuses the tick with `StopInvariantError: … locating
  the stop stopped no input that was moving`, because `_pushes` displaces one input
  with every other still. Pre-existing on main, identical with no block in sight;
  met again on `RangedBlock` when a detent passes and the crank then pushes the lever
  through the other wheel. Transactional, not a wrong answer. A follow-up would
  displace the selecting inputs alongside the candidate — a change to the pushing
  test, not to the block.
- **FIXED in this cycle: ADR-121's walk moved a HELD self-read coordinate by one ulp.**
  `_Walk.run`'s `own_at` and `_Walk._probe` computed `own_left + S − base` left to
  right; when the skeleton is unchanged over a piece but comparable in magnitude to
  the coordinate, `(own + S) − S` rounds. Reproduced on main with no block (a wheel
  at `71.99999999999996` under `crank` standing at `72` committed `71.99999999999994`
  when an unrelated hoist moved); on the Curta-shaped fixture a lift moved two dials
  by an ulp. Parenthesized as `own_left + (S − base)`; every pre-existing corpus
  entry byte-identical afterwards (see the change's evidence.md).
- **FIXED by `pin-the-block-order`: the corpus's `ShiftedCarry` scenario did
  not discriminate the block's order.** ADR-122 named the corpus as the
  thing that pins the published listing against a consumer that executes
  it as an order, and added `ShiftedCarry` to be the scenario that proves
  it. Measured: `_Block._order` monkeypatched at runtime to return the
  members in listing order left the committed scenario GREEN — every bank
  value, crossing, stop and command identical in twenty ticks — under
  BOTH the listing order and the two members reversed, because the
  crank's `2.0` over `0.2 s` landed the lever's `carry.travel >= 0.5` gate
  exactly on a tick boundary and the run recorded no crossing at all.
  Across the whole 19-scenario corpus the listing order reproduced every
  bank value, stop, command status and admitted travel; the one thing it
  got wrong anywhere was `RangedBlock` tick 1's crossing COUNT (2 against
  3). `pin-the-block-order` changed the script alone — crank `2.0` over
  `0.3 s` instead, six ticks of `1/3` — so the gate now crosses strictly
  inside tick 2: the listing order loses a sixth of a turn of
  `higher.turn` from that tick on and never heals (`3.5` against
  `3.3333333333333335` at tick 20), 21 disagreements against zero before.
  `tests/test_running_corpus.py::BlockOrderTest` now pins the
  discrimination directly, and `uncovered_features` refuses a corpus
  missing the new `'an in-block gate crossing inside a tick'` feature.

# evaluate-only-what-moves (2026-09-16, found while applying)

**Status: fixed inside the cycle; recorded so nobody reopens it.** A
piece was identified by `id(branches)` / `id(inner)` in the first draft
of `_PathValue`'s call sites. A transient `branches`/`inner` dict is
unreferenced the moment the next piece replaces it in the caller's local
variable, and CPython is then free to hand a LATER, unrelated piece the
exact same address once the earlier dict is garbage collected — which it
did, reliably, on `Clearing`'s corpus scenario: a jump's decided branch
from an earlier piece answered for a structurally identical-looking but
numerically different later one, moving `wheel.turn` by exactly 100 on
tick 1 of `Clearing` (dt=0.1) and `StoppedClearing` (dt=0.05) in
`tests/test_running_corpus.py`. Fixed two ways: `JumpPlan`'s own
`_LevelPaths` now identifies a piece by a monotonic counter token
(`new_piece()`), never by a dict's `id()`; `_Walk`'s skeleton/level
tracking instead keeps every `branches` dict it ever builds alive for
the walk's own lifetime (`_live_branches`), which makes `id()` safe
again by construction. Both are documented at their call sites.

**Findings outside this cycle's ratified scope** (tasks.md 10.1):

- **`_along` builds a fresh source dict per point.** `_Walk`'s `own_at`,
  `_level` and `_skeleton`, and `JumpPlan`'s `_level_at`, each call
  `_along(start, delta, t)` — a fresh `{name: start[name] + delta[name]
  * t for name in start}` dict comprehension — every single point,
  including a point a bound path value then walks in a fraction of a
  microsecond. Measured on the end-to-end prototype
  (`spikes/endtoend_curta.py`): together with the walk's own bookkeeping
  this is 17.2 % of the POST-CHANGE tick — the single largest residue
  after this cycle and the port enumeration (design.md section 5, section
  8). Building it incrementally (only the moving names, added to a
  standing base) would need the SAME moving-set concept this cycle
  introduces, applied one level up; recorded here rather than folded in,
  because it changes a different call shape (`_along`'s callers, not a
  graph's own evaluation) and was not in the ratified scope. **Open.**
- **A compiled-closure path evaluation measures 58× against the current
  walk, 3× faster again than the path value this cycle takes** (design.md
  section 6 C, `spikes/proto_eval.py`): `exec` of generated Python source
  over the moving cone, still bit-identical over the same 2 600 captured
  evaluations. Rejected for this cycle because it puts run-time code
  generation into the engine for a term (`_PathValue.at`) this change
  already leaves at 17.8 % of the patched tick, and its own build cost
  (3.3 evaluations against this cycle's 1.4) would need a cross-tick
  cache the "no cache outlives the tick" decision (section 3.3) measured
  away. Recorded so a later cycle, if the residue above and the port
  enumeration are both taken and evaluation is STILL the bottleneck, has
  the number. **Open.**

# declare-the-state (2026-09-17, the clocked discipline)

Named in the ratified change's Non-goals, each with the reason it was left
out and with the shape a later cycle would take. Nothing here is a defect:
each is a narrowing chosen deliberately, and each is cheap to lift because
the machinery it needs is already in place.

- **A port, joint coordinate or derived coordinate as a SOURCE of a
  committing relation.** A clocked simulation holds a bank of drivers and
  states and NOTHING else; a port is a calculation the untimed enumeration
  recomputes from that bank on every pose, so reading one inside `at`
  would cost a pose per sample or a compiled program over the whole tree
  — which is exactly the generality the clocked discipline exists not to
  pay for (design section 4). Neither of the project spike's two
  committing relations reads anything but drivers and states. A mechanism
  that genuinely needs one is a mechanism whose event surface is a
  function of the POSE, and that is a question worth its own evidence.
  **Open.**
- **A broadcast `commits` over a `.repeat()` child.** A repeated child's
  banked value has no legal qualified id — `drivers-0` is not a legal id
  segment — so the copies could not be addressed apart. It is THAT
  problem, the one `machinome.node.qualified` records against a repeated
  `Driver`, and not this one; the Curta's seventeen clearing relations
  are seventeen written lines until it is fixed. **Open.**
- **A multi-input request.** The exactness classification is stated
  against ONE moving input, and the underlying machinery integrates a
  path in a joint source space perfectly well, so widening later is a
  change to the CHECK and not to the solver. Nothing in the corpus needs
  two. **Open.**
- **A `direction=` keyword on `commits`.** Rising-only is fully
  expressive — a mechanism that commits on the other edge negates its own
  level, `floor(-crank / 360)` — so the keyword would ship with no test
  in the corpus that discriminates it. If one appears, the keyword is a
  branch in `Committing.next_event` and nothing else. **Open.**
- **An `Instruction` under a clocked root.** A declared move with no
  duration, targeting one input, is a coherent idea and is what a browser
  panel will want when the viewer executes a clocked document. Left out
  because its shape depends on what that cycle needs from it; today an
  instruction targeting a STATE is refused at construction and `trigger`
  is refused by name. **Open.**
- **A fold-commit — a `commits` with no `at`.** The project spike
  measured that per-digit comparison events cover partial clearing in
  BOTH directions with no held value, and that the one gap a fold would
  close is a rest the manufacturer's booklet forbids. `at` is therefore
  required, and a `commits` without one is refused by name. The fold's
  shape is recorded in the spike's own record
  (`simulation/docs/clocked-spike-2026-09-16.md`) for the project that
  does need it. **Open.**
- **Two writers at one event are found by RUNNING, not by reading.**
  Closure 1 (2026-09-17) made several committing relations per state
  legal and refuses only two of them firing at ONE landing. That
  judgement needs a landing, so it belongs to the request: a model whose
  two writers always coincide is admitted at construction and refused the
  first time somebody moves the input they share. A structural
  pre-check — two relations on ONE input whose levels are the same graph
  — would catch the commonest case at construction, and is worth its own
  evidence before it is written. **Open.**
- **A clocked model cannot be PUBLISHED or VIEWED.** Every document
  producer refuses one by name. The document version that carries
  declared states, and the viewer that executes `at` and `law` on its
  expression DAG, are the next two cycles.
  **PUBLISHED: CLOSED** by the change `publish-the-clocked-machine`
  (2026-09-17, ADR-128): a clocked root publishes document version 8
  with its compiled machine, and `document_body`'s refusal is re-aimed
  at a producer that publishes WITHOUT compiling.
  **VIEWED: open, the viewer's own cycle** — no released viewer reports
  version 8, so a build and an export warn, a web snapshot is refused
  before the browser starts, and the model still does not reach a
  browser.
- **A `Bound` does not clip a request path.** A request that would drive
  a mechanism through a stop is REFUSED WHOLE: the events are solved, the
  final pose raises `JointRangeError` exactly as an untimed pose does,
  and the bank, the tree and the record stand where they stood
  (amended by closure 1, 2026-09-17: the first implementation left the
  bank advanced past the refused pose, which was a bug and not this
  gap). What is missing is the CLIP — stopping where the machine stops
  and keeping what was committed on the way.
  The Curta's eight interlocks are all of this shape,
  so its clocked model is not complete until that cycle. The solver is
  written so the clip is a truncation of the request's travel before the
  first location, not a second locator. **CLOSED** by the change
  `a-bound-stops-the-request` (2026-09-17): a declared range is now a
  stop on a clocked request path, the travel is clipped before the events
  are located, and a request stopped at zero travel is admitted.
- **A `State` under `Time.running()` is refused, with its meaning
  defined.** Under a run a value committed at an event is an ADR-121
  self-read law whose value changes only through a switch — exactly how
  the operating Curta's wheels already work — so a `State` under a
  running root compiles to that law and becomes one retained coordinate
  among all the others. It buys no speed. The one reason to fix the
  meaning now is PORTABILITY: a project writes "this register is a state
  committed at the stroke end" once and has it mean the same under both
  roots. **Open, deliberately.**

## Findings from the framework cycle `a-bound-stops-the-request` (2026-09-17)

What the implementation found that its own ratified design did not state,
and the questions that survive it. The full write-up is
`openspec/changes/archive/2026-09-17-a-bound-stops-the-request/evidence.md`,
and the decision is ADR-126; the originating project is
`projects/Calculators/Curta-Type-I-3x`.

- **The direction test and "a request back to exactly where it started".**
  The design's decision (section 7) is `h = max(0, g(0))`, read at the
  start of EACH request; its planned proof (section 17) asks for a
  request "back to exactly where it started" to be admitted. Those
  contradict: once a request has carried a coordinate back INSIDE its
  bound, the next request reads `h = 0` and is clipped at the bound, so
  it cannot return to an illegal starting point — measured at 4 of 15
  admitted on the `outside` fixture. The decision was implemented and the
  proof text is what moved. If the intended behaviour is a threshold that
  is REMEMBERED across requests rather than read per request, that is a
  different design and needs its own evidence. **Open, recorded.**
- **Two rows of the construction refusal table are unreachable.** A chain
  that reads the coordinate it drives, and a chain that is CYCLIC, are
  both refused by the RELATION layer under every non-running root
  (`CouplingError` for the self-read, `UnreachedCoordinate` for the
  cycle) long before the clocked compile is reached. The guards remain as
  backstops, untested and untestable from a fixture. A structural blind
  spot, reported rather than hidden. **Open.**
- **A relation binding into a SCALED sink.** `ports.bind` multiplies by
  the sink's declared `scale` for every binder alike, while the running
  compile applies a scale factor only for a WIRING edge. The clocked
  chain applies it uniformly, because it is asserted against the pose. No
  existing model can tell the two readings apart — a joint's own
  coordinate never carries a scale — but if one ever does, the running
  compile is the side that looks wrong. **Open, not acted on.**
- **The clip is not re-computed between events**, deliberately (design
  section 8). A bound that reads a STATE a commit inside the same request
  writes is read at its pre-request value, so one long request and two
  short ones split at that event admit different travels, and a commit
  that carries a compiled coordinate out of range refuses the request
  whole. The spike's corpus contains no mechanism that needs the finer
  reading; a project that does splits the request, which is exact.
  **Open, deliberately.**
- **A request does not report the constraints it EXAMINED.** A maker
  asking "why did the knob not move" is answered by `stops`; one asking
  "which interlocks are live right now" is not. Deferred to the cycle
  that gives a clocked model a panel. **Open.**
- **An author's REST-DEFAULT GUARD on a ranged joint is refused.** The
  framework cannot tell a guard's constant (`if self.wheel.turn is None:
  self.wheel.turn = 0`) from a `simulate()` that computes a coordinate
  from three other things, so a ranged joint held by a guard falls on the
  refused side of "the author binds it by hand". The message names the
  joint and the one-line fix. A common shape; recorded rather than
  solved. **Open.**
- **The clocked authority MARK is process-wide.** `ports._clocked_marked`
  is a module-level `frozenset` holding the `(id(node), joint name)`
  identities one request's pose is judged under — the shape `run_owned`
  already has, empty everywhere else, opened and closed by
  `Clocked._posed`. A per-simulation mark would be cleaner: two clocked
  simulations posing on two threads would share this one, and the
  identity is a `id(node)` rather than the simulation that compiled it.
  Nothing in the corpus does that today, so it is recorded rather than
  fixed. **Open, a follow-up.**

## Findings from the framework cycle `time-without-running` (2026-09-17)

The cycle's own Non-goals, each with its reason and the shape a later
cycle takes, plus what the implementation found. The full write-up is
`openspec/changes/archive/2026-09-17-time-without-running/evidence.md`,
the decision is ADR-127, and the originating project is
`projects/Calculators/Curta-Type-I-3x` — which **does not owe this cycle
and paid nothing for it**: the Curta has no clock, it is operated, and
its events are located on the crank and the clearing ring. What owed the
cycle is ADR-125's own two-axis table, whose `elapsed × memory` square
was unsayable. Nothing below was closed by this cycle.

- **A clip in TIME, and a compiled chain that FOLLOWS the clock, are one
  piece of work.** A time request is never clipped by a bound (a declared
  range is a mechanical stop, and no interlock holds the next second), and
  a coordinate whose chain carries the clock is refused at simulation
  construction by name. Admitting the clock as a chain free name and
  clipping a time request like a driver request is coherent and is where
  a later cycle goes; it was refused HERE because it is two changes. The
  easy half is renaming the animation symbol to a bank id where a chain
  is composed; the hard half is that a level moving with the clock must
  be classified, solved and given a DIRECTION TEST, and a level periodic
  in time is exactly the case ADR-126's contested `h = max(0, g(0))`
  reading (above, still open) was never asked about — that contradiction
  is the first thing the cycle must settle. Half of it would ship a clip
  that stops a clock sometimes. **Open, deliberately, as ONE item.**
- **A looping root with MEMORY is still refused by name.** A loop replays
  from zero, so it replays every commit and the state climbs across
  loops. The demo that would make it sayable — a snapshot restored at each
  wrap — has not appeared, and until it does the refusal is honest.
  **Open.**
- **`Time.elapsed()` under a RUNNING root** is a category error with no
  spelling, and **a `State` under `Time.running()`** stays refused with
  its meaning DEFINED and not implemented (ADR-125, unchanged): a
  self-read switch of ADR-121's kind, buying no speed because every other
  coordinate is still integrated at the cadence. **Open, unchanged.**
- **No `Instruction`, no control and no `move(duration=)` over the
  clock.** A declared advance of a named number of seconds is a coherent
  idea and is what a browser panel will want; its shape depends on what
  the viewer cycle needs from it, so it is deliberately not invented
  here. **Open, waiting on cycle 6.**
- **No MULTI-INPUT request** moving a driver and the clock together.
  ADR-125's narrowing, unchanged: the exactness classification is stated
  against ONE moving input, and widening it is a change to the
  classification rather than to the clock. **Open, deliberately.**
- **`time` is not the source of a `drives` relation.** A part whose pose
  is a formula of time is written in `simulate()`, which is what the
  pendulum fixture does; admitting the clock into the relation graph
  would reach the running compile's own source space. Refused at class
  definition, by name. **Open, deliberately.**
- **The clocked document and the viewer are cycles 4, 5 and 6.** What a
  version carrying a clocked clock publishes — the clock's name, its
  initial value, and whether a consumer advances it — is deliberately not
  presumed by this cycle. The `declare-the-state` bullet "A clocked model
  cannot be PUBLISHED or VIEWED" above stays open and is cycle 4's.
  **Open, and owned.**
- **A class body that binds no `time` gets Python's `NameError`, and no
  framework refusal can improve on it.** A class body does not see
  `AssemblyNode.time`, so a body declaring no time base never reaches the
  framework through that name. Where the file imported the stdlib `time`,
  the reflected `&` added by this cycle names the MODULE and says a clock
  is named only through the root's own declaration; where nothing bound
  the name at all, the name fails before an operator is reached. A
  structural blind spot, asserted in a test as Python's own answer rather
  than papered over. **Open, and probably permanent under this shape.**
- **Should a time request report the instants it PASSED without firing?**
  A maker asking "what happened between 0 and 10 seconds" is answered by
  the commits; one asking "which releases were disengaged" is not. The
  same question ADR-126 records for constraints examined but not met
  (above). **Open.**
- **Does an elapsed clocked root want `set_keyframe` refused?** Today
  `set_state(time=)` is a general delivery and the clocked simulation
  does not own the clock the way a run owns its coordinates, so both go on
  working over a clocked root. Left alone: this cycle refuses nothing that
  already works. **Open, a question.**
- **The user manual named TWO time bases.** `docs/scenarios.rst` and
  `HISTORY.rst` carried the third spelling, but `docs/animation.rst`'s
  own time-base page ("A machine that never wraps: `Time.running()`")
  was written when there were two and was not in this cycle's task
  list. **CLOSED** at completion (2026-09-17): the page now states the
  third spelling; the passing mentions in `docs/api-reference.rst`,
  `docs/declaring.rst` and `docs/driving.rst` are statements about the
  RUNNING base specifically and stay true.

## Findings from the framework cycle `publish-the-clocked-machine` (2026-09-17)

What the implementation and its adversarial review found beyond the
ratified design, and what this cycle deliberately did not fix. The full
write-up is
`openspec/changes/archive/2026-09-17-publish-the-clocked-machine/evidence.md`,
the decision is ADR-128, and the originating project is
`projects/Calculators/Curta-Type-I-3x` (branch `direct-operation`, HEAD
`9fb725f`; spike worktree `WTs/clocked-spike`), whose clocked model
reproduces the operating model's registers at every stroke end and is
worth nothing to its pilot until a browser can crank it.

### The framework's two meanings of `%`

Not Python-versus-JavaScript. The DOCUMENT's `%` is TRUNCATED in all
three runtimes that read one (`math.fmod` in the framework's two
evaluators, JavaScript's native `%` in the viewer's). What differs is
CALLABLE versus GRAPH, and the framework is on both sides:

- **Cross-mode, and newly visible.** A commit LAW is CALLED with the
  bank's numbers, so its `%` is Python's FLOORED remainder; a RUNNING law
  edge of the same text is evaluated as a GRAPH, so its `%` is `fmod`.
  The same law text therefore means two different things under a clocked
  root and under a running one. This cycle publishes the truth of the
  place it publishes from — a published commit law is DESUGARED to the
  floored remainder, verified against CPython's `float_rem` over 500 000
  random double pairs with zero value mismatches — and does not
  reconcile the two modes, because doing so would change what a running
  law edge MEANS and move version 5. **Open.**
- **Pose versus graph, framework-wide and PRE-EXISTING — for the
  pilot.** A `drives(law=)` whose law takes `%` of a negative POSES
  through the Python callable and PUBLISHES the graph applied to
  symbols, so the rendered pose and the published expression already
  disagree, in **every document version from 2 upward**. Nothing in this
  cycle caused it and nothing in this cycle could fix it: the fix moves
  what a published pose expression means, which moves versions 2 through
  7. It needs the pilot's decision about which side is right before any
  cycle touches it. **Open, held for the pilot.**
- The one stated exception to the desugaring is the SIGN of a zero
  result under a negative divisor — Python's `copysign(0.0, b)` gives
  `-0.0` where the desugaring gives `+0.0` — which compares equal as a
  number in both runtimes and which nothing in the published vocabulary
  distinguishes. Counted and asserted, not hidden.

### What the cycle's brief assumed wrongly

- **An instruction under a clocked root is NOT refused.** The brief said
  it was. Only an instruction whose TARGET is a state is refused, at
  simulation construction; one targeting a driver is admitted and now
  PUBLISHES, in the version 5 shape, with `duration` and exactly one of
  `targets` and `by`. Pinned as a test rather than left as prose.
  **What it MEANS under a clocked root is now settled**: an instruction
  under a clocked root IS one request over the one driver it names,
  `trigger` makes it and returns it, and the document does not change.
  **CLOSED 2026-09-17** by `play-the-instruction` (ADR-129), which also
  narrowed the declaration to exactly one driver; see that cycle's
  findings below.
- **The parity fixture does not pin the document's `%`.** Design section
  16 said it does. `%` is an OPERATOR and not one of
  `SYMBOLIC_BUILTINS`, and no parity case carries a remainder. What pins
  the document's own `%` is the RUNNING corpus (its inventory requires
  it, within that corpus's `1e-9`); what pins the DESUGARED commit form
  is this cycle's corpus, exactly. Recorded as a test. **Closed by
  evidence; the design sentence is corrected there and not re-edited.**

### Two things the document had to invent, and what they cost

- **`$own` cannot travel, so the own-name is MINTED and DECLARED.** The
  document's expression language admits exactly ONE `$`-name, `$t`, so
  the spelling a constraint level reads its own coordinate under does
  not even tokenize. Widening that shared regex — the language every
  document and every consumer shares — for one producer's private
  convention was rejected. Instead `clocked.own` publishes the name
  (`_own`, lengthened by a leading underscore for as long as any
  published id equals it) and a consumer binds each bound's `value` at
  the request's start to it for the whole request. It is the published
  clock's pattern exactly: a reserved free name published as a string,
  not a convention a consumer has to know. **Closed by decision.**
- **The exactness claim is stated, not assumed.** The clocked corpus
  agrees BIT FOR BIT and carries `"tolerance": {"float": 0.0}` as a
  field of the file. It rests on IEEE `+ - * /` and `sqrt` (correctly
  rounded by the standard), the truncated remainder (exact) and the
  floored one composed from it (one further rounding), the selecting
  operations (`floor`, `ceil`, `abs`, `sign`, `min`, `max`, the six
  comparisons), and the landing walk, a bisection in the ORDINAL space
  of a double's own bits. It does NOT cover a TRANSCENDENTAL or a POWER,
  neither correctly rounded, and the generator REFUSES a machine
  carrying one in a published commit law, event level, constraint level
  or chain — so the limitation is enforced rather than remembered. A
  project that ever needs a transcendental commit law needs a
  per-machine tolerance field beside the file's own, one machine opting
  out by name, and not a window the whole file relaxes into. **Open as a
  shape, not as a defect.**

### Non-goals of this cycle, with the shape a later one takes

- **Executing a version 8 document** (the viewer's cycle) and **the
  browser's clock and clip** (the one after). Both are
  `machinome-viewer`'s own repository and its own OpenSpec records; the
  contract between the packages is this cycle's design plus the corpus.
  A consumer owes a BIT WALK for the landing, not an epsilon walk: a
  walk by a small quantity lands on a different float at exactly the
  surfaces the corpus is built on. **Open, and owned.**
- **`identity` has no consumer yet.** It is a digest of a canonical
  listing, published so a bank taken against one machine is refused
  against another — which is what a viewer persisting a bank across a
  reload will need. If that cycle wants a different granularity, the
  listing is the only thing that moves. **Open, a question.**
- **A structural pre-check for two writers at one event** (ADR-125's own
  follow-up, above) stays open: publishing it would mean publishing a
  claim the framework does not make.
- **`Sim(model, state={...})` is not published.** A document says where
  the machine RESTS; where a particular session opened it is session
  setup. Stated rather than hidden. **Closed by decision.**
- **A `Committing.jumps` entry may classify `constant`.** `_compiled`
  classifies EVERY driver among a relation's sources, so a driver the
  level does not read answers True to `moves_with`. The published
  `shapes` omits those entries, because the export requirement admits
  `affine` and `kinked` and a consumer needs the inputs that can MOVE
  the level; `moves_with` and the request path are untouched. Tightening
  `moves_with` itself would save a wasted solve per unrelated driver and
  is worth its own measurement. **Open, small.**

### Closure 1: two landings the shared locator had no answer for

Both were found by THIS cycle's corpus, both LOST or REFUSED a request
the ratified rules already describe, and both were closed here rather
than deferred.

- **A crossing belongs to the request whose path CONTAINS its landing.**
  ADR-125 stated the containment by FRACTION, and that reading lost an
  event: a request ending exactly on a STRICT comparison's surface
  solved its crossing at fraction 1.0 but landed one representable value
  BEYOND its own endpoint, then resumed backwards from there and raised
  `LandingInvariantError`, while the next request excluded its own left
  end by fraction and never saw the surface at all. Now: a landing on
  the endpoint is this request's, a landing beyond it is the next
  request's, and the left end is excluded by LANDING — a crossing solved
  at fraction zero whose far side lies ahead inside the path IS an
  event. A `sign` level moved off zero consequently takes BOTH of its
  rising steps, which the corpus's `Signed` machine now records.
  **CLOSED** by `publish-the-clocked-machine`; ADR-125 carries the
  amendment note.
- **The landing walk's first step was the ulp of the value it started
  from.** From a coordinate standing at exactly `0.0` that is a denormal,
  and two hundred doublings reach about 1e-263 — no distance on a
  segment a millimetre long — so a bank standing outside a LOW bound
  with its coordinate at zero raised instead of stopping, where the
  HIGH-bound mirror admitted zero travel and reported its stop. The two
  CLOCKED callers now size the step by the SEGMENT. **CLOSED** by
  `publish-the-clocked-machine`; ADR-126 carries the amendment note.
- **The RUNNING walk still scales by the ulp of the value it starts
  from.** `_Walk._far_side` passes no segment, deliberately, so that
  `tests/running-corpus.json` and every running landing stay
  byte-identical — which they are, by construction and not merely by
  measurement. The same latent defect therefore remains on the running
  path, unmeasured and unreachable by any current fixture. Fixing it
  means regenerating the running corpus, which is another cycle's
  ratified artifact. **Open.**
- **A zero-travel stop is now said off the CROSSING.** `Bounded.clip`
  returns zero travel as soon as the crossing solves at fraction 0,
  rather than walking. Left to the walk, the LOW side of a bound admits
  half an ulp OF THE LEVEL of travel (`-2.22e-16`, measured on
  `Standing`) where the HIGH side of the same bound admits nothing, only
  because the coordinate happens to stand near zero. Recorded because it
  is a behaviour decision and not only a bug fix. **Closed by decision.**


## Findings from the framework cycle `play-the-instruction` (2026-09-17)

What this cycle deliberately narrowed, what it left asymmetric, and what
its implementation found beyond the ratified design. The full write-up is
`openspec/changes/archive/2026-09-17-play-the-instruction/evidence.md`,
the decision is ADR-129, and the originating project is
`projects/Calculators/Curta-Type-I-3x` (branch `direct-operation`, HEAD
`9fb725f`), whose `ClockedCurta` declares `'Turn crank':
Instruction(by={'crank_rotation': 360}, duration=2)` and could not be
watched turning it. Nothing here is a defect.

- **An instruction under a clocked root names EXACTLY ONE driver, and
  that is a deliberate, liftable narrowing.** One naming two would be a
  SEQUENCE and one naming none would move nothing; both are now refused
  where the machine is compiled, which is before any document exists, so
  every instruction a version 8 document carries is one a consumer can
  play. A multi-input instruction on a clocked root was legal before this
  cycle — published as a disabled button — and is now a construction
  refusal. No model in this repository, in the Curta or in any fixture
  declares one; checked. **What lifting it costs, stated so a later cycle
  does not have to rediscover it:** requests are atomic INDIVIDUALLY
  (ADR-125) and a sequence of them is not, so it needs a
  snapshot/restore envelope, a rule for a STOP in the middle of the
  sequence, and two more corpus features; it would be a THIRD meaning for
  one declaration, since a running root moves the named inputs
  CONCURRENTLY over one duration; and it changes `trigger`'s return
  shape, which is a `Request` today precisely because one input means one
  request. Lift it when a project writes the machine, not before.
  **Open as a shape, not as a defect.**
- **`trigger` under an UNTIMED root still returns `None`.** It ramps, as
  it always did, and reports nothing; a RUNNING root returns its tuple of
  command handles, and a CLOCKED one now returns its single `Request`.
  Three bases, three return shapes. The asymmetry is recorded rather than
  fixed because no project needs an untimed ramp's handle, and it is now
  pinned by a test (`test_an_untimed_trigger_still_returns_nothing`) so
  it cannot drift unnoticed. **Open, a question, small.**
- **`trigger`'s clocked return shape is not future-proof, knowingly.** It
  is the `Request` itself, not a one-element tuple and not a
  `Triggered(name, requests)` wrapper: the name is what the caller typed
  and the duration is what the document publishes. If the multi-input
  narrowing above is ever lifted, this shape changes with it. Accepted at
  ratification as cheaper than ceremony in every caller today for a
  machine nobody has written. **Closed by decision, recorded because it
  is a decision.**
- **`origin`/`end` are NATIVE while `admitted` is DESIGN, inside one
  value object.** A genuine asymmetry, and the honest one: the two ends
  must match `Commit.value`, which is native, and `admitted` must match
  what `by=` asked, which is design. Both are documented in one sentence
  of `Request`'s own docstring, and the scaled case is proved rather than
  asserted (a `by=3.0` request on a scale-2 driver reports `admitted`
  `3.0` and `end` `6.0`). A consumer that rebuilds an end through the
  scale can land on a float the machine never stood at, and a commit
  landing exactly ON the end would then read as unfired. **Closed by
  decision.**
- **Each end is the bank entry VERBATIM, so `origin` carries the bank's
  own type.** An integer-typed driver standing at its integer default
  reports `origin` as an `int`; everything else reports a float. A
  consumer treats both ends as numbers. Stated rather than normalized,
  because normalizing would mean the machine publishing a float it did
  not stand at. **Closed by decision.**
- **`docs/api-reference.rst` documented NO clocked API at all** until
  this cycle. `Request`, `Commit`, `Clocked` and `ClockedError` were
  never added by ADR-125..128, and `Request` is still not exported from
  `machinome.simulation`. A short **Clocked simulation** section was
  added here because this is the first cycle to hand a `Request` to a
  consumer and the two new fields needed somewhere to live; it is more
  surface than the ratified task named, reported rather than assumed, and
  accepted at review. **Whether `Request` should be exported from the
  package is open, and unasked by any project.** **Open, small.**
- **The clocked cadence refusal list lives in TWO test modules**, not
  one: `tests/test_clocked_sim.py:CadenceRefusalTest` for an untimed
  clocked root and `tests/test_clocked_time.py:RefusedNamesTest` for the
  elapsed root's own copy. Both had to lose `trigger`. The second is what
  proves the meaning holds under EVERY time base, which the simulation
  requirement states; a later cycle changing that surface must change
  both. **Recorded so it is not found twice.**
- **Nothing contradicted the ratified design's substance.**
  `compile_clocked` already had the facts the arity refusal needs;
  `Clocked.move` already held both floats at its return; `Sim.trigger`'s
  existing `_instruction`/`_driver` resolvers gave the unknown-name and
  unknown-driver messages by construction; and the design's own
  prediction that `machinome/core/serializer.py` would not change held
  exactly. What the viewer's own cycle inherits is stated in ADR-129's
  consequences and is not framework work. **Closed.**

# Vault running pickup (2026-09-19, complex twelve-bolt vault)

**Status: resolved by `unilateral-running-pickup` and its independent viewer
companion after adversarial review; originating project migration follows.**
Originating project `projects/Locks/Vault_with_combination_lock`, checkpoint
`78d4ceb`; framework baseline `b9b64dd`. Historical reproduction and control
evidence: [investigation](docs/vault-running-pickup-investigation.md).
The [external issue draft](docs/vault-running-pickup-wart.md) was not posted:
GitHub CLI authentication is unavailable. No external issue number is claimed.

- A positional self-read gate cannot state the Vault's unilateral peg contact:
  from dial 1590 / wheel 1587, reversal to 1580 gives wheel 1577 instead of
  retaining 1587. This conforms to ADR-121's surface-following branch rule;
  it is a missing opt-in capability, not a regression in missing-tooth clearing.
  Strict comparisons and smaller ticks were not reliable workarounds.
- The ratified response is an explicit `Play(low, high)` law under
  `Time.running()`, initially limited to linear driver-rooted chains. It
  preserves callable-law semantics and uses the run's existing retained bank,
  not a project Python/browser controller. Publication is document version 9;
  viewer execution belongs to the viewer's own `execute-running-play` cycle.
- Independent review tests exposed incorrect cascade stop interpolation,
  cancellation when one wheel's absolute landing was recomputed from its
  increment, an ambiguous terminal writer, and refusal to recollect free
  clearance while a wheel remains at a physical stop. These tests are retained
  as acceptance evidence; final validation and project migration follow below.

Resolution: the reviewed implementation, ADR-131, synchronized baseline specs,
and validation are recorded in
[the completed change](../openspec/changes/archive/2026-09-19-unilateral-running-pickup/evidence.md).
Additional review covered bounded affine/nonlinear/multi-source observers,
rollback after projection, corpus behavior-removal mutations and early malformed
declaration refusals. The viewer companion is integrated into its local main at
`038f74d`; its API 22 explicitly reports document versions 1–9. The framework
and viewer corpus bytes agree. The original callable prototype remains a red
control; the measured direct-dial Play caller is green. This resolution does
not certify the Vault's source orientation, password or complete assembly.
The GitHub issue draft is still unposted because authentication is absent.
