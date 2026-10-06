# Framework warts

Open findings only. On 4 October 2026 every entry was checked against
`main` at `feb23f2`, and what is fixed there, closed by decision, or judged
not a framework fix left this file. The file as it stood before, with every
resolved entry and its "What shipped" record, is
[`archive/warts-hygiene-2026-10-04/warts-before-hygiene.md`](archive/warts-hygiene-2026-10-04/warts-before-hygiene.md);
the [resolution index](archive/warts-hygiene-2026-10-04/README.md) beside
it says what closed each entry. Entries below are verbatim from that
snapshot, so their line and commit references describe the tree they were
written against, unless they carry a **Remaining (2026-10-04)** note or were
condensed to their remainder, which says so. A fix that exists only on an
unmerged branch does not close an entry.

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

# kossel (2026-09-06)

- **No clearance contract for a screw in a hole.** `assertClose` is
  unusable for a screw in a hole, so kossel's tests carry their own gap and
  hole helpers. The 2026-09-06 triage deferred it as evidence for a new
  contract rather than a fix ("Deferred item 6"); `assertClose` and
  `assertFar` still check mesh vertices only. The perturbation-frame half of
  kossel's finding is fixed (ADR-075). Condensed 2026-10-04.

# fender-bender

- The upstream geometry has no rigid interference-free bracket release, and its guide-wall click bumps overlap the frame at rest. The contracts carry stated, measured allowances for those two things (release path and snap) and say so in
  the specs and README. If you would rather have them red, say so.

  Held for the pilot since the 2026-09-06 triage: keep the measured
  allowances, or make the contracts red. No decision is recorded.

# Expression math and mechanisms (2026-09-06)

Findings from lifting the project `kinematics.py` helpers into the framework
(`expression-math`, ADR-022 revised; `mechanisms`, ADR-076; both on main).

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

- **The `viewer` extra carries no version floor.** Item 12's fix left it
  unpinned "because the viewer is unreleased"; machinome-viewer has been on
  PyPI since 0.7.0, and `pyproject.toml` still declares
  `viewer = ["machinome-viewer"]`. Added 2026-10-04 from item 12's own
  remainder.

## Deferred

11. **The openflexure four-bar decomposition** (`leg_lean`, `lever_rise`)
    as a mechanism law. One project asks; propose when a second flexure
    stage does (ADR-076 open question).

## Not framework fixes, still open

- Viewer: `npx vitest` at the `machinome-viewer` root runs a stale copy
  under `build/lib/` that fails on a missing `jokenizer`; the widget's own
  runner is the entry point. Clean or ignore `build/`.

- Workspace: `cq_gears` is absent from the workspace venv, so
  `sandbox/gearbox`'s own tests cannot run. (Sphinx, recorded with it, is
  now installed.)

# Internal-Cycloidal-Actuator (2026-09-06, project refactor pass)

Framework candidates from the project refactor pass:

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

    **Remaining (2026-10-04):** the whole-assembly check passes a finite
    negative faceted volume since `voron-faceted-contact` (2026-09-13);
    strict pairwise assertions still fail on one, and the default
    `volume_epsilon` is still 0. Held for the pilot (see "Standing triage").

14. **`machinome snapshot --preview` passes a bare `--preview` to OpenSCAD
    2021.01**, which rejects it with a usage dump
    (`OpenScadRenderer.build_command` emits it unconditionally). Seen in
    3DPrintedClocks.

- Shop: the session scratchpad is shared across parallel agents, and four of
  ten clobbered each other's `before.png` during the refactor pass (each
  caught it and redid the comparison under a distinctive name). No fix is
  recorded.

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

  **Remaining (2026-10-04):** (a) and (b)'s minimum-distance assertion are
  open. Measuring an overlap volume without asserting on it is possible
  through `machinome.exact.intersect_shapes`, which ADR-142 made usable for
  project diagnostics.

# AlbertPro (2026-09-07, simulate the Albert quadruped)

Found while building `projects/Robots/AlbertPro/simulation/` directly
from this conversation: an eighteen-body print plate assembled into the
quadruped `RL/dog.xml` describes, driven by the five trained
trajectories the ESP32 replays.

## Framework

- **A driver's `range` is presentation metadata and nothing enforces
  it.** `height` has a hard geometric range — outside it the machine has
  no pose — and there is no per-driver validator or clamp hook. The
  project guards inside its own `stance_angles()`, which can only act
  when handed a plain number, so the guard fires in tests, snapshots and
  exports but not in the viewer, where a driver is symbolic. Workaround
  in `simulation/layout.py`.

- **There is no `solid import-stl`.** `machinome import-step` scaffolds a
  whole document into declarative source; the equivalent for a
  multi-body mesh pack does not exist, and a pack's inventory is
  reachable only by provoking a build failure. For an eighteen-body
  plate that is enough friction to be worth a committed probe
  (`simulation/tools/probe.py`). Not a blocker — `StlNode`'s `body`
  index and its per-body inventory did the actual job cleanly, and this
  is the smallest of the five.

# YouCanBuildDog

Simulating James Bruton's `dog02_9g` (51 solids, Fusion/AP214 export)
and then fitting the M3 hardware its bores ask for hit three framework
things worth fixing. None is filed.

- **No per-solid selection from a STEP document.** `part_index` (ADR-115)
  closed selection between same-named products; the related shape filed
  with it stays open:

  Worth noting the related shape: an upstream *product* is routinely not
  a printed piece. In this export 20 products hold 51 solids, and two
  toe blocks are filed under a *chassis* product rather than the leg
  they sit on. Per-solid selection — a `machinome` index beside `part`, or a
  `machinome import-step --per-solid` — would be the general answer, and
  would make the framework's own printed-solid unit reachable from a
  STEP document without a project-local splitter.

- **`networkx` is an undeclared need of the mesh path.**
  `assertNoDisconnectedSolids` now takes the exact path for an exact solid
  (`_routes_exact`), which closed the first half of this finding. Its mesh
  path (`split(only_watertight=False)`) can still reach trimesh's
  `fill_holes`, which imports `networkx`, and `networkx` is not among the
  package's declared dependencies: the workspace venv has it only because
  it was installed by hand on 2026-09-07. Whether trimesh's split still
  reaches `fill_holes` is unverified. Condensed 2026-10-04.

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

  **Remaining (2026-10-04):** `refuse-false-empty-exact-common` (ADR-142)
  and `require-resolved-exact-witness` now refuse an exact empty common
  that a witness contradicts. This pair was not re-run against them, the
  witness is not universal, and no mesh cross-check exists. Held for the
  pilot with the indeterminate verdict (see "Standing triage").

## Project follow-ups

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

- Thor's exact suite has two failures that pre-exist this work on this
  framework tree (`seats.assert_inventory`: 260 of 272 overlapping pairs
  not in the seats inventory, in `test_assembly_integrity` and the
  scenario test); byte-identical with the unrefactored model, and the
  same 29/2 on the primary checkout at main cb474e3 with Thor's committed
  code, so it predates the motion branch (an exact-boolean or seats change
  since Thor's last green run, not investigated here).

  Still present on 2026-09-26 (the `place-parts-by-mate` validation: 32 of
  34, "the two failures pre-existing seat-inventory ones"); not diagnosed.

# Motion catalogue refactor (2026-09-09, every project onto `machinome.motion`)

Every other finding of this campaign is fixed (ADR-093 to ADR-100); these
remain. OpenVMP's data-built child is carried under `declaration-site-joint`
below.

- **A relation cannot fan out over LIST-HELD children when each copy needs
  a structurally different expression.** The Pascaline root's eight-way
  carry binding: no single per-copy law states it, and `repeat-fan-out`
  (ADR-096) reaches only `.repeat()` copies under one law. Recorded inside
  the Pascaline pawl entry, whose multi-source half ADR-100 fixed; never
  filed on its own. Condensed 2026-10-04.

- **A bare number cannot be added to a dimensioned token.** The
  Pascaline's slide span, `CHANNEL_Y[1] - CHANNEL_Y[0] - SLIDE_WIDTH - 2 * clearance`
  with `clearance` a declared `Length`, is refused at class definition
  (`DimensionError: 27.0 is dimensionless and <L> is L`): the parameter
  algebra lets a number MULTIPLY a token but not add to or subtract from
  one, so a layout constant in millimetres must be wrapped as
  `Length(...)` before it meets a token. Met writing a `ratio=` and a
  joint `range=`; not a motion-layer gap but the first time the algebra
  was asked this in a class body rather than in `render()`.

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

- **Indexing a repeat in a class body.** The residual of InMoov's wrist and
  finger finding: its conditional-frame half is answered by ADR-098's
  callables of the realized parent, and its ten `connect()` calls by ADR-100
  as a SELECTOR that hands all five motor values to every copy. The
  sentence InMoov wants is a per-copy SOURCE,
  `index.drives(fingers[1].drive)`, which `repeat-fan-out` named a
  non-goal. Held for the pilot as needing its own sighting. The selector
  form is not yet applied in the project's own repository. Condensed
  2026-10-04.

# joint-frame-follows-declarer (2026-09-10)

ADR-097 closed the own-placed-origin finding. Two things it raised remain.

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

  **Remaining (2026-10-04):** the rule is settled by ADR-097; wall clock
  48's pose change is still the pilot's question, and no answer is
  recorded.

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

# declaration-site-joint (2026-09-10, ADR-098)

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

  **Remaining (2026-10-04):** not done. `docs/driving.rst` no longer exists;
  the site paragraph is now in `docs/concepts/joints.rst`, which says
  nothing about a conditional placement.

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

  **Remaining (2026-10-04):** the framework has since shipped retained
  running history (ADR-121 self-read laws, ADR-131 `Play`, ADR-133), and
  the Vault lock states its measured pickup with no project controller.
  `Play` covers linear driver-rooted chains only, and this lock's own move
  off its Python/JS controller is not recorded. Whether what remains
  belongs to the framework, the viewer or the host is still undecided.

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

  **Remaining (2026-10-04):** the whole-assembly check now passes a finite
  negative faceted volume (`voron-faceted-contact`); strict pairwise
  faceted assertions still fail on one (held for the pilot), and the
  positive 5.5e-7 mm³ fitted-peg disagreement is uninvestigated.

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

# Pin tumbler lock (2026-09-14, running-command cancellation)

- **The studio's API skill still warns against `cancel()`.** The framework
  defect is fixed (`cancel-stops-the-command`): `cancel()` retires the
  command and frees its input at once. The shop skill text the original
  entry said a fix would delete is still there
  (`machinome-studio/shop-skills/machinome-api/SKILL.md`, near line 1878:
  "Do not rely on it to stop or replace a move"). A studio change, made in
  that repository. Condensed 2026-10-04.

# Pin tumbler lock (2026-09-14, migration to `Time.running()` under `bounds-read-other-coordinates`)

Recorded from the originating project's migration, run against the cycle's
worktree (`openspec/changes/bounds-read-other-coordinates/evidence.md`, "The
originating project"). Each entry is a finding outside the cycle's ratified
scope; **status: filed here; triage open** unless marked otherwise. No
framework code changed for any of them in that cycle.

- **A `.repeat()` child that owns a JOINT cannot run under a running
  root.** Filed with the `.repeat()` port finding, whose half
  `publish-only-what-runs` fixed; this half as filed:

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

  **Remaining (2026-10-04):** the static-reads shortcut and later
  performance cycles (ADR-123, ADR-124) took part of this. The search is
  still a fixed `_SUBDIVISIONS` sweep plus bisection, so the
  bracketed-refinement item stands.

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

# Standing triage (from the 2026-09-14 execution plan)

The 2026-09-14 plan ranked every entry then open under the pilot's standing
delegation. Its items 1 to 9 are integrated on main. What remains of it:

## Planned, never done

- **Interference failures name the leaf, not its path** (3DPrintedClocks
  mantel 34, Thor). Cycle `name-solids-by-path`: proposed on the unmerged
  branch `fix-warts` (`c8c0b6f`), not implemented.
- **`%` on a symbolic value disagrees across runtimes** (item 7 above; see
  also "The framework's two meanings of `%`" below). Cycle
  `expression-remainder`, never started.
- **`tools/generate_parity_fixture.py` cannot run from a worktree** (item 9)
  and **`machinome snapshot --preview` sends a bare `--preview`** (item 14).
  Cycle `tooling-paths-and-flags`, never started.
- **A `.repeat()` copy's joint arguments resolve before `index` exists**
  (`joint-frame-follows-declarer`). Cycle
  `resolve-repeated-joints-per-copy`, never started.
- **Generated-artifact freshness** (3DPrintedClocks, the first entry).
  Investigation never started; whether later currency cycles cover part of
  it is unmeasured.

## Held for the pilot (a product, architecture or policy choice)

- Negative faceted volumes in STRICT pairwise assertions (items 13, Locks,
  Voron-2): `voron-faceted-contact` deliberately kept pairwise strictness;
  relaxing it reverses that decision.
- A driver's `range` enforcement policy (AlbertPro): clamp, refuse or leave.
- Dimensioned literals and number-plus-token in the parameter algebra
  (item 8, Pascaline): language design.
- An exact boolean that returns empty for an overlapping pair
  (YouCanBuildDog; ADR-142 now refuses a witnessed false empty), an
  indeterminate pair verdict (science-jubilee) and a per-pair exact fallback
  when the faceted engine refuses a mesh (Thor): kernel semantics and sweep
  cost.
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
`projects/Calculators/Pascaline-module`. Cycle 1,
`carry-markings-on-a-part` (ADR-120), and the viewer's drawing of markings
(viewer ADR-056) are on their mains: a rigid node carries a declared
zero-volume `Marking` that the viewer draws, and the Curta uses it. The
original findings are in the snapshot. Still open (condensed 2026-10-04):

- **DXF artwork.** Its chains only close at 0.01 mm and read as the
  stencil.
- **`process`, the nominal cut file and the multi-material 3MF** in which
  the upstream ships its markings (0.8).
- **Whether a co-printed marking is geometry**: one part, several colour
  bodies, one manufacturing unit, as the Curta's `Mods/Printed Lettering/`
  files state it. A product decision held for the pilot (cycle 3 of the
  markings plan).
- **The Pascaline still shows no answer.** Its `DigitDrum` carries no
  `Marking`; a project follow-up.

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
`workflow/archive/curta-retained-angle-clearing-2026-09-15/curta-retained-angle-clearing.md`,
was taken up as this change. Its item 8 (replay through the independent
viewer) is done on the viewer's main (viewer ADR-057); item 9 (the Curta's
own migration) is not recorded as done here. Condensed 2026-10-04.

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

  **Remaining (2026-10-04):** the stale list itself was fixed in the cycle;
  that nothing checks a capability cycle sweeps the narrative refusal lists
  is the open part.

# select-the-source (2026-09-15, found while fixing)

## Originating Curta follow-up: seconds per Python tick (2026-09-15)

The tick cost was taken up by `evaluate-only-what-moves` (ADR-124) and
`memoise-declared-ports` (2026-09-22). One mechanism stays open:

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

## Findings from the framework cycle

Findings outside that cycle's ratified scope (ADR-122), from
`openspec/changes/select-the-source/` (tasks 10.1, design and evidence);
**status: filed here; triage open.**

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

# evaluate-only-what-moves (2026-09-16, found while applying)

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

  **Remaining (2026-10-04):** `running-time-drive` (ADR-133) admits
  `Time.running()` as a `drives` source; an elapsed (clocked) clock is
  still refused as one.

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

### Two things the document had to invent, and what they cost

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

- **A structural pre-check for two writers at one event** (ADR-125's own
  follow-up, above) stays open: publishing it would mean publishing a
  claim the framework does not make.

- **A `Committing.jumps` entry may classify `constant`.** `_compiled`
  classifies EVERY driver among a relation's sources, so a driver the
  level does not read answers True to `moves_with`. The published
  `shapes` omits those entries, because the export requirement admits
  `affine` and `kinked` and a consumer needs the inputs that can MOVE
  the level; `moves_with` and the request path are untouched. Tightening
  `moves_with` itself would save a wasted solve per unrelated driver and
  is worth its own measurement. **Open, small.**

### Closure 1: two landings the shared locator had no answer for

- **The RUNNING walk still scales by the ulp of the value it starts
  from.** `_Walk._far_side` passes no segment, deliberately, so that
  `tests/running-corpus.json` and every running landing stay
  byte-identical — which they are, by construction and not merely by
  measurement. The same latent defect therefore remains on the running
  path, unmeasured and unreachable by any current fixture. Fixing it
  means regenerating the running corpus, which is another cycle's
  ratified artifact. **Open.**

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

- **`docs/api-reference.rst` documented NO clocked API at all** until
  this cycle. `Request`, `Commit`, `Clocked` and `ClockedError` were
  never added by ADR-125..128, and `Request` is still not exported from
  `machinome.simulation`. A short **Clocked simulation** section was
  added here because this is the first cycle to hand a `Request` to a
  consumer and the two new fields needed somewhere to live; it is more
  surface than the ratified task named, reported rather than assumed, and
  accepted at review. **Whether `Request` should be exported from the
  package is open, and unasked by any project.** **Open, small.**

  **Remaining (2026-10-04):** the clocked API section is in the manual;
  only the export question stays.

# Corpus record cursor across restore (2026-09-20)

**Status: observed while validating Curta; deferred, no external issue filed.**
`tools/generate_running_corpus.py::run_machine` and the matching test replay
helper retain their record-list cursors across a scripted `restore`, while
the real run clears its record rings. If the same script step immediately
creates a new stop, the old cursor can omit it from that step's corpus record.
Direct runtime snapshot tests still compare the actual stop correctly.

The periodic-contact corpus restores on its own recorded step before the
next request, so both stops are present. No general corpus cursor repair is
included in that cycle. A future repair should be red-first for restore plus
an immediate same-step stop, and check crossings as well as stops; it should
  not change machine state or command semantics to repair evidence collection.

# Review of the cycles landed after the 0.7.0 fold (2026-09-23)

**Status: review findings, recorded for the pilot; nothing here is triaged.**
Between the fold commit `a659cc7` (22 September, 22:24) and `26cbd63`
(23 September, 08:07) main took seventeen commits: eight complete OpenSpec
cycles and one merge, every record citing the pilot's standing autonomous
framework-fix mandate. Four cycles speed the Curta (ADR-139, ADR-140, the
Follow prefix reuse, the tick-local fold cache), one adds the `Follow` law
(ADR-141, document version 12), three correct the exact kernel (ADR-142 and
its amendment, ADR-143). All eight new test files pass together (60 tests,
22 subtests); no correctness defect was found in the diffs. The findings
below are what the review left open.

- **`Follow` is deliberately narrow, and the narrowing is recorded only in
  the archived change.** The retained coordinate must be terminal among
  program edges (a downstream reader would need the swept path, not the
  endpoint delta); the two sources must be run inputs, held bank
  coordinates, or unbranched affine ordinary-law chains carried as exact
  `Motion.line` values, so wiring and formula ancestry are refused rather
  than approximated by an endpoint chord; the matching lower and upper
  Bounds are recognised by graph text (`str(graph)`) and the same read set,
  so an equivalent expression written differently is refused. The Curta's
  bell-turn and lift sources sit inside every one of these boundaries.
  **Open as a shape, not a defect:** lift each limit when a project writes
  the machine that needs it, and record here which one.
- **The Follow prefix cache stores mapping proxies where a propagation
  used to flow.** `Run._constraint_level` in `machinome/simulation/run.py`
  memoises a successful law-to-Follow prefix as
  `(MappingProxyType(dict(deltas)), MappingProxyType(dict(landings)))`.
  On a hit the rest of the method receives a plain read-only mapping, not
  the `Propagation` object the first walk produced, so `motions`,
  `untraced`, `follow_cuts` and `follow_closures` are absent. Today only
  item access follows the prefix, so it is correct; the first later change
  that reads a path attribute after the prefix will work on a miss and fail
  on a hit, and the focused tests would not necessarily catch it.
  **Deferred:** when that method is next touched, either snapshot the
  propagation itself (frozen) or assert the shape at the hit.
- **The exact-kernel corrections cost time that was measured only on the
  Curta.** ADR-143 deep-copies both operands of every native Common, Fuse
  and witness Section; ADR-142 adds a section plus up to 1,872
  zero-tolerance classifications after every empty near-contact common,
  and `_false_empty_witness` computes six bounding boxes per call, which
  one profile showed to be most of the guard's cost. The full framework
  suite went from about 393–405 s in the earlier cycles to 460 s in the
  last one, with host load uncontrolled. No other project's exact tests
  were timed. **Deferred:** time the exact suites of two or three
  catalogue projects on the fold commit and on main before the next
  release, and record the numbers here.

  **Note (2026-10-04):** 0.7.0 and 0.7.1 were released without these
  numbers; the timing is still unmeasured.

# Piece identity split by OpenSCAD facet order (2026-09-23, CI)

The facet-order defect is fixed (ADR-145). One item was left as is:

- **Committed documentation exports carry the old ids.** The
  `docs/_exports/counter-*/manifest.json` piece ids were digested from
  raw bytes; nothing reads them for identity, and they change the next
  time those exports are regenerated. **Left as is** in this cycle.

# Interface gaps: constrained sketches and closed loops (2026-09-23, pilot)

Not a project finding: two gaps in how a maker states a design, recorded at
the pilot's request so they are not lost. The assessment behind them is
`workflow/ongoing/mates-and-sketches.md` (§2, ideas 1 and 3; §5.3 and §5.4).
Its idea 2, mates between named frames, is the part with project evidence
already on record and is tracked there, not here.

- **No constrained sketches.** Mainstream CAD builds a part from a rough 2D
  profile the author relates — horizontal, equal, tangent, coincident, a
  distance from an edge — and a solver computes the coordinates; features
  are built from the solved sketch. machinome states design intent only as
  one-way parameter formulas, and a part's profile is whatever its backend
  draws (CadQuery's experimental constrained `Sketch` is the one backend
  that has a solver). **Deferred:** no project has asked. Comes back when a
  project's parts genuinely suffer from hand-computed profile coordinates;
  the note's lean is to leave it to the backends, since machinome's job is
  the machine, not the part.
- **No closed-loop solving (skeleton sketches).** A mechanism drawn as a
  stick figure — links, pivots, lengths — keeps its loops closed as it is
  dragged, so a four-bar, a slider-crank, a delta or a Peaucellier never
  has its law derived by hand. machinome closes every loop with a
  hand-derived law: the kinematics helpers (ADR-076), the `Follow` law,
  the hexapod's hand-inverted `R_roll · R_pitch · R_yaw · T_height`, and
  the deferred openflexure four-bar decomposition (Deferred item 11 above).
  **Deferred.** Pilot direction (2026-09-23): the solve happens at
  compile time, never in the viewer; the build publishes a closed form
  where one exists, or a sampled law the viewer interpolates, and judges
  the branch, dead points and closing range once. The viewer receives the
  mates to represent them, and solves nothing (note §5.3, §5.5). Open
  solvers exist (SolveSpace, FreeCAD's planegcs and Assembly solver) for
  the build-time side. Comes back
  with a linkage machine that wants its loop closed rather than derived —
  a second flexure stage, or a Foundry machine built around a linkage — and
  is a natural neighbour of 0.9 dynamics on `workflow/ongoing/roadmap.md`.

## Findings from the Thor project's fastener holders (2026-09-26)

Recorded from project-lane work in Thor, change
`hold-the-fasteners-by-their-bodies` (Thor main `8e575f3`): turning the
tool left bolts and nuts floating behind the gripper, because every
derived fastener of a design group was held by the link's node and stood
in its frame, while some fasten a body that moves inside the link (the
crown plate and gripper the tool turns, a jaw on its parallelogram, a
pinion on its shaft). Thor now holds each fastener in the body it
fastens and guards it with a test that, at seven poses, reads every
fastener's and every part's world placement and holds the two together.
Two findings for the framework; neither is requested, both await the
pilot's triage.

- **No documented read of a node's world placement.** Thor's
  `FastenerRideTest` needs each part's and each fastener's placement in
  world coordinates at a pose, and the public contract gives none; the
  test reads `machinome.node.base._compose_world_matrix`, as the
  workspace's pose-capture tool (`docs/motion-general-refactor/capture_poses.py`)
  does. A project test that holds two nodes together across poses is a
  recurring shape (every "rides with" contract), so the read is a
  candidate for the public contract when a second project needs it.
  **Recorded.**

# OpenSCAD parameter values are echoed by hand (2026-09-26, the vet survey)

- **Three printers run OpenSCAD themselves to read a parameter's value.**
  The catalogue survey behind `vet-the-project` (2026-09-26) found that
  every `subprocess` in the survey but one is the same workaround:
  the project needs a number an OpenSCAD source computes (a rod length,
  a bearing offset, a layout placement), and nothing in the framework
  hands it over, so the project writes a probe `.scad` that `echo`s the
  names, runs `openscad -o <file>.echo` in a temporary directory, and
  parses the `ECHO:` lines back into Python. Evidence:
  `3D-Printers/Metamaquina2/simulation/params.py` (lines 22-23, 54-67: a
  `PARAM`/`PRECISE` echo pair per name, the second splitting a scalar
  into integer and fraction because OpenSCAD prints six significant
  digits), `3D-Printers/snappy-reprap/simulation/params.py` (lines 26-27,
  72-89: the same probe, written independently), and
  `3D-Printers/hangprinter/simulation/csg.py` (lines 16-17, 75-81 and
  234-248: `openscad -o layout.csg` for the layout tree, and an `echo()`
  helper for expressions). Each is `outside-universe` (`subprocess`,
  `tempfile`) and `file-write` under `machinome vet`, so none of the
  three can be pure while the only way to a parameter value is running
  OpenSCAD by hand. The fourth `subprocess` in the survey,
  3DPrintedClocks' `check_models.py`, is a quality audit, not a model
  need. **Gap:** the SCAD import could close it by reading a source's
  top-level assignments, or evaluating named expressions, through the
  OpenSCAD run the framework already makes, with the precision the
  projects had to recover themselves. Not triaged.

## Findings from the SO-ARM100 project's migration onto mates (2026-09-26)

The first migration of a URDF design onto frames and mates, in
SO-ARM100 (project branch `frames-and-mates`, commits `92fb5d0` emitter
and red test, `9762d9b` migration, `ce8b3b1` records; validates framework
`main` at `61f2335`): six revolute joints read verbatim from
`Simulation/SO100/so100.urdf` -- the joint's `<origin>` as a frame of the
parent link, the child's own frame as a bare `Frame()`, the `<axis>` as
the freedom's line where it is not the moving `z` -- with
`capture_poses.py compare` at maximum deviation 0 over 25 poses and 110
leaves (2.1e-13 mm unrounded, the difference of composition order), the
project's tests unchanged but for the two that compared the deleted hand
transcription, and `Rest`/`Grip` snapshots pixel-identical to `main`. The
design states its joint lines, so the emitter needs no hand table of
lines (Thor's `ROOT_CHAIN`). Nothing the URDF states was refused. The
project's guard reads only documented surfaces (`resolved_frames`,
`declared_mates`, the mate's ends and freedom). Two findings; both
recorded, not fixed, until the pilot triages them.

- **Two direction snaps still work one component at a time.** Since
  `snap-keeps-the-triad-unit` (6 October 2026) a joint's axis and a
  frame's directions on its snapped path snap to a principal axis only as
  a whole (`machinome.motion.joints._snapped_direction`), so they stay
  unit. Two other directions still pass each component through a
  per-component snap: the axes a SITE-declared joint carries into the
  child's own rest frame (`Joint`'s carry in `machinome/motion/joints.py`:
  the inverse rest placement, normalized, then `_snapped` on each
  component), and the axis of a mate's rest rotation (`mates._axis_angle`,
  each component through `mates._snapped`, nearest integer within
  `1e-9`). Either can leave a direction a few millionths off a principal
  axis `1 + 2e-11` long, as the frame and the joint did. No project is
  known to reach either: the SO-100 declares no site joint, and its rest
  rotations publish exact axes (`[1, 0, 0]`, `[0, 1, 0]`, `[-1, 0, 0]`).
  Each would be a one-call change to `_snapped_direction`, with its own
  red test. **Recorded.**

## Findings from the OpenArm project's migration onto mates (2026-09-26)

The validation of `state-the-freedom-per-instance` (ADR-150) in its
originating project: OpenArm's seven arm joints and two finger joints
stated once as mates whose fixed frame's `at` and whose freedom's `axis`
and `range` are functions of the parent's `left`, realized per side
(OpenArm branch `frames-and-mates`, commits `8a62ad7`, `53c63f3`,
`7127d19`; framework `b7cc651`), with `capture_poses.py compare` at
maximum deviation 0 (unrounded 0.0) on every model, the four documented
suites at their `main` counts, and the three documented snapshots
identical to `main`'s. Nothing was refused. Four findings; all recorded,
not fixed, until the pilot triages them.

- **No documented read of a mate's resolved line and range for one
  instance.** The ratified scope of ADR-150 deferred it ("no resolved
  read"); OpenArm is the project that needed it: its guard has to hold
  each side's realized line and range to the URDF, and the class reads
  return the function. It checks through behaviour instead -- a bound
  mate turns the child's `mesh` about the side's URDF axis through the
  URDF point within 1e-6 mm, and a binding 0.01° past each side's limit
  raises `JointRangeError` naming the mate -- which is a correct guard
  and a long way round. Thor's guard before `read-frames-and-mates` was
  the first project to reach for the same numbers. What is wanted: a
  read, on a realized assembly or its mated child, of each mate's
  resolved axis, anchor and range for that instance, beside
  `resolved_frames`. **Recorded.**

## Findings from the framework cycle `name-what-is-refused` (2026-10-06)

- **Two comparisons and two messages that cycle left as they were.**
  Neither is reached by a known project. (1) The several-ends self-read
  check does not expand an inferred node: `(rack &
  wheel).drives(wheel.turn, law=...)`, the node standing for its one
  joint as a source beside the driven `wheel.turn`, is not recognized as
  a READ of the driven end unless a reused-joint mate's handle is among
  the ends, because `couplings._alias_comparison_key` expands inferred
  nodes only then. `name-what-is-refused` expands them for the
  one-to-one comparison alone, where a match is only ever refused;
  expanding them in the several-ends comparison would turn an
  unrecognized shape into a read, which is semantics rather than a
  message. (2) The constraint-intersection refusals name a bank id or a
  class: `simulation/program.py`'s `'{identifier}: constraint
  intersection (lo, hi) is empty'` and `motion/constraints.py`'s
  `'{Class}.{joint}: constraint intersection ...'` would name the joint a
  mate installed on the moving child (its bank id is
  `...left_finger.left_travel`) or the child's class, not the mate, for a
  mate's coordinate an ancestor constrains. The bank id is what the run
  and the published document carry, so renaming it is not a message
  change. Evidence:
  `openspec/changes/archive/2026-10-06-name-what-is-refused/design.md`,
  "Open Questions". **Recorded.**

## Findings from the framework cycle `children-refuse-early-reads` (2026-10-06)

- **Eight clock models refuse to load until their colour loops are
  rewritten.** 3DPrintedClocks wall clocks 12, 25, 28, 32, 36, 37, 39 and
  40 colour parts in `render()` by looping over `self.children` (clock
  12 over `self.numerals.children`), eighteen reads in all. The list is
  always empty there, so in seven of the clocks sixty dial islands and
  forty other parts were published uncoloured; clock 40's three loops
  were dead code beside class-level colours. Since this change each of
  the eight is refused at load, naming the assembly and the attributes
  to address. The rewrite is project work on the project branch
  `children-reads` (worktree
  `projects/3DPrintedClocks/WTs/children-reads`, not merged): clocks 12,
  25 and 28 are rewritten there (`58ff90e`) and load with their colours
  against this framework; 32, 36, 37, 39 and 40 are not yet rewritten. Clock 36
  also holds a nineteenth read in a `WindingKey` class its tree never
  instantiates. Evidence:
  `openspec/changes/archive/2026-10-06-children-refuse-early-reads/evidence.md`,
  §4. **Recorded.**
- **A read outside any phase before linking still answers an empty
  list.** A helper walking `node.children` on a root nobody has
  assembled reads an empty tree and passes vacuously. No measured case:
  AlbertPro's and the clocks' test walkers run after assembly. Left as
  it was; design.md, Open Question 2, of the same change. **Recorded.**

# 3DPrintedClocks wall clock 02 (2026-09-29, verdict memo across runs)

The memo finding is fixed (`persistent-verdict-memo`, ADR-156). Not a
framework fix, recorded for the project: the six `wall_clock_02` failures
measured there (collet against hinge_screw 14.58 mm³, holder body against
the beat crinkle washer 1.58 mm³, `standoffs` two bodies, the weight screw
not meeting its nut), undiagnosed.

# `cached_shape` keys a loaded BREP on `(path, float mtime)` (2026-09-29, found while designing persistent-verdict-memo)

**Status (as filed): recorded; triage open.**

`machinome.exact.cached_shape` keeps one imported CadQuery shape per
`(brep path, os.path.getmtime(...))`, a float mtime, and `shape_identity`
hands that key to every exact-path cache: the bounding boxes, the face
boxes, the placements and the in-process verdict memo. Every other artifact
cache has since moved to the full `ArtifactObservation` (realpath, device,
inode, size, mtime_ns, ctime_ns) -- `cached_base_mesh`, the Manifold and
bounds caches, `currency._file_key` -- because `_atomic_export` stamps every
artifact with its SOURCE's mtime: a rebuild not caused by a source edit
(a changed producer recipe, a deleted artifact, a framework or kernel
upgrade that exports differently) reproduces the old mtime while its bytes
may differ. Under the float key such a rebuild inside one long-lived
process keeps serving the old shape, and every exact cache keyed on it.

`persistent-verdict-memo` (ADR-156) did not change this key; it was a
non-goal. The persistent tier guards itself instead: `cached_shape` now
records the observation it loaded from (observed before and after
`importBrep`), and a persisted identity is the digest of THOSE bytes, or
none when the file has changed since. The in-process gap is unchanged:
within one process a same-mtime rebuild still reads as current. Candidate
fix: key `cached_shape` on the load observation, as the mesh caches key on
theirs. Evidence: design.md "Non-Goals" and §3 of the
`persistent-verdict-memo` change; no project has reported a wrong verdict
from it.

# Three findings from filming the clocked Curta (1 October 2026, found by Videomaker's curta-video campaign)

Findings 1 to 3 are fixed on main (`sim-through-a-symlink`, `sim-identity`,
`export-records-its-revision`, ADR-158); finding 7 was not a defect. The
findings met by the bench's cycles that remain (recorded, triage open):

4. **The framework's clocked snapshot carries no identity, the viewer's does.**
   `ClockedSnapshot` holds `model` (the bare class name with the sorted bank
   ids) and `values`, and `Clocked.restore` compares `model` only, so the
   framework restores a snapshot from a machine whose law or range changed
   under the same ids, or from a same-named class in another module; the
   export spec says the identity exists precisely to refuse that, and a
   running `RunSnapshot` does carry and check `program.identity`. Found by
   `sim-identity` (its `evidence.md`, finding 1).
5. **The strict manual build is not a gate.** `sphinx -W` fails on `main` with
   five warnings in untouched lines (`docs/reference/api.rst` 23, 35, 76 and
   the `Sim.initial` and `Sim.state` docstrings). Found by `sim-identity`.
6. **A stale known gap in `docs/architecture.md`:** "A clocked model is
   published but not yet VIEWED" predates viewer 0.7.0, which reads document
   versions 1 to 13. Found by `sim-identity`.

8. **An export written inside the project and not ignored makes every later
   export there dirty.** The Curta's `export/` is untracked, so its record
   says `dirty: true` for untracked files that are no model source. Whether
   projects ignore their export directories, or the marker excludes the
   output directory, is the pilot's; the ruling as written was kept. Found
   by `export-records-its-revision`.
9. **Whether `viewer.json` and the browser snapshot should carry `source`**
   is open; no consumer has asked. The committed tutorial exports under
   `docs/_exports/` will carry the framework's own revision when next
   regenerated. Found by `export-records-its-revision`.
10. **`exclude_build_from_git` does nothing in a Git worktree**, so a project
    checked out as a worktree whose `.gitignore` lacks `_build*` sees its
    exports marked dirty after the first. Existing behaviour, recorded.
    Found by `export-records-its-revision`.

# A machine's identity depends on the module its model is imported from (1 October 2026, found by Videomaker's take-identity change)

**Status (as filed): recorded; triage open.**

The clocked machine's identity, published as the export's `clocked.identity`
and now as `Sim.identity`, includes the model class's module name: the same
`counter.py` gives the export's identity when imported as `models.counter`
and another identity under another module name. A consumer that records a
take through `Sim` over a model imported through a different `PYTHONPATH`
spelling is therefore refused as another machine, which is correct for what
the identity promises and surprising for the author, who changed nothing in
the model. Videomaker names the model as `module:Class` in its refusal and
lists the import module among the causes (its archived change
`take-identity`, 2026-10-01, finding 1). Ask: say in the identity's
definition (export spec, ADR-128) that the import module is part of it, or
anchor the identity on the project-relative module as the manifest's
`[tool.machinome.models]` names it, so the spelling of `PYTHONPATH` cannot
change a machine.

## OpenAstroMount — a scenario test refused by the exact common guard (3 October 2026)

Found validating the framework change `exact-engine` on a branch of the
project. `OpenAstroMountScenarioTest.test_every_instruction_reaches_its_documented_end_state`
fails on the project's `master` against the unmodified framework (feb23f2)
and against the change alike, with `ExactCommonInconsistency`: the exact
common of `housing` and `rolamento_uc206_valor_predeterminado_1` is empty
while a point near (-2.02, 265.56, 442.98) classifies strictly inside both
solids beyond their face tolerances. Same pair, same witness to the last
digit before and after the change, so it is not the engine's doing. Either
the housing and the bearing genuinely overlap at that pose, or the guard
witnesses a false empty on a valid common. Not triaged; the project's other
eight tests pass. Evidence: `openspec/changes/archive/2026-10-03-exact-engine/evidence.md`, §6.

## A first build's sweep removes fused children's STLs (3 October 2026, framework)

Observed in the `exact-engine` cycle's fixture
`tests/meta_project/exact_fusion_current.py`: the first build of an exact
fusion leaves the fused children's `.stl` artifacts removed by the sweep,
and a second build restores them, so a test that needs every artifact
current must build twice. Pre-existing behaviour, observed and left
unchanged by the cycle. Not triaged: whether a fused child's STL is an
artifact the sweep should keep is a build-pipeline question.

## Findings from the framework cycle `backend-switch` (3 October 2026)

- **A self-materializing leaf that publishes nothing falls through to the
  OpenSCAD path.** `AbstractBaseNode.generate_stl` launches OpenSCAD for
  any rigid, unlocked node whose STL is not current after preparation; its
  gate is staleness, not "this node is presented as SCAD". A `LeafNode`
  subclass whose `materialize` returns without publishing its STL reaches
  `require_openscad`, and with OpenSCAD present would launch it on a
  `.scad` preparation never wrote (inferred from the code; not run with the
  binary). Probed on the bench with OpenSCAD absent: `node SilentProducer
  (SilentProducer) requires the OpenSCAD binary because its STL is rendered
  from SCAD by OpenSCAD; ...`. `JScadNode.materialize` is the core's one
  instance: its branch `if not os.path.exists(temporary): return`
  (`node/adapters/jscad.py`) means a `jscad` run that exits 0 and writes
  nothing ends in OpenSCAD, which `openscad-dependency` says a `JScadNode`
  never launches. No project uses `JScadNode` (lean-core plan's count: 0)
  and no self-materializing leaf outside the core exists, so the cycle
  recorded it and changed nothing (design.md, "Findings"). The remedy
  shape, should a project meet it: a refusal naming the node that produced
  no STL, made where `materialize` returns. Evidence:
  `openspec/changes/archive/2026-10-03-backend-switch/evidence.md`, §1.3.
  **Untriaged.**

## Findings from the framework cycle `lean-install` (3 October 2026)

- **A `machinome build` in a fresh project worktree hung for three hours.**
  During the cycle's deep validation, a `machinome build` of
  Actuators/Internal-Cycloidal-Actuator in a fresh git worktree
  (`WTs/lean-core-validation` under the project, on its virtiofs path
  `/mnt/data/machinome-projects/...`, with the ignored 35 MB vendor STEP
  copied in) hung: the `machinome build` process alive with 4 s of CPU, an
  empty `_build/actuator.lock`, no artifact written and no child process;
  killed by the orchestrator after three hours, at 18:29. The same build in
  the project's primary checkout, where artifacts exist, completed in under
  a minute. Not reproduced; the worktree was removed. Evidence:
  `openspec/changes/archive/2026-10-03-lean-install/evidence.md`, §5.1.
  **Untriaged.**

  **Remaining (2026-10-06):** the restart loop the `mesh-engine` cycle
  added here (a build whose sources were written moments earlier starting
  a new generation every second) is closed by
  `build-settles-on-a-grown-source-set`: a mesh or other part source newer
  than its module no longer stands a build down (see
  `archive/fix-warts-3-2026-10-06/resolved.md`). The three-hour hang
  itself is not claimed. Its vendor STEP was copied into the worktree after
  the checkout, the newest file there, so the same mechanism is plausible;
  but its recorded observations, no child process and no artifact after
  three hours, are not the loop's, which spawns a child each generation and
  writes assembly-time artifacts. Not repeated (the change's design.md,
  Open Question 1).

## Findings from the framework cycle `expression-type` (3 October 2026)

- **OpenSCAD's STL output is not reproducible run to run.** Two renders of
  byte-identical SCAD under the same OpenSCAD binary gave different STL
  bytes for several parts of Pin_tumbler_lock (Body, Core, DriverPin,
  Key, ...), and a piece's mesh volume therefore differed by one unit in the
  last place between two exports (`pieces[1].volume`
  `21065.08699624388` against `21065.086996243885`); exporting twice from
  the same build directory gives the same volume. Any byte-pinned
  validation across builds must hash the SCAD, never the STL or a
  mesh-derived number; the export manifest's `volume` carries that noise.
  Evidence: `openspec/changes/archive/2026-10-03-expression-type/evidence.md`,
  §6.1. **Untriaged.**
- **For the record, outside this repository.** machinome-mechanics' tests
  name solid2's `OpenSCADConstant` as the test of symbolic-ness
  (`tests/test_motion.py:46`, `tests/test_mechanisms.py:349`), now
  corrected by a mechanics cycle asserting
  `machinome.expression_graph.symbolic` (the pilot, 3 October 2026); and
  machinome-viewer carries a stray root-level `openscad.py`, outside its
  package and imported by nothing, importing
  `machinome.openscad.require_openscad`, which this cycle moved to
  `machinome.openscad.binary`. Evidence: the same file, §6.3, §6.5.

## Findings from the adversarial review of the framework cycle `production-layer` (4 October 2026)

Reviewed after the cycle was merged into `v0.8-split` (69c7019) at the
pilot's direction, so every item below is on the campaign line. The cycle's
focused suite (94 tests), its package fingerprint `cba98e72…`, its stated
base and its Curta and studio commits were all reproduced; the items are
what the review found beyond the record. Probes ran on the `v0.8-production`
bench against a faceted `FusionNode` of two self-materializing boxes with
one child translated in `render()`.

- **Defect: binding a production after a build doubles the placements of
  children positioned in a rigid internal node's `render()`.** The
  `model-consumption` spec's scenario "Read an advanced machine" promises
  that structural reading leaves established operation values unchanged.
  It holds when the facade reads first and fails when the lifecycle ran
  first: `ModelSnapshot.occurrences` (`machinome/model.py:354-365`) calls
  `render()` on every non-assembly internal node unless its own
  `_production_rest` cache exists, and a node already rendered by
  `_prepare()` or `assemble()` has no such cache, so the author's `render()`
  runs a second time and re-applies every `translate`/`rotate` to the same
  declared children. The doubled structure is then cached and returned by
  every later `render()` (`machinome/node/internal.py:39-42`); nothing
  raises. Measured: child operations 1 in the facade-only, lifecycle-only
  and facade-then-lifecycle orders, 2 in the lifecycle-then-facade order,
  also with the fusion inside a prepared assembly; a regeneration after the
  doubling fused a different solid (content id `f966a273…` became
  `c49003bd…`). The cycle's test
  `test_rigid_rest_placements_reused_by_normal_lifecycle` covers the
  facade-first order only, and the Curta slice prints leaves, so neither
  could meet it. Exposed by any process that builds, snapshots or serves a
  model and then binds a `Production` to the same instance. Remedy shape:
  the walk reuses the node's `_prepared_rendered` when the lifecycle
  already rendered it and renders once otherwise, pinned by a red test in
  the lifecycle-first order that compares operations and the regenerated
  content id. **Untriaged.**
- **A missing input file at binding escapes `Production(model)` as the
  facade's own error.** A node whose `files` names a path that does not
  exist makes the constructor raise
  `machinome.model.ModelInputChangedError("input observation failed: …")`:
  `Production.__init__` (`machinome/production/profile.py:281-288`) wraps
  only `OSError`, so the production error taxonomy is bypassed, and the
  message says a file changed when it never existed. **Untriaged.**
- **The draft bundle is not portable.** Every key of the manifest's
  `input_hashes` and `files`, every `source_paths` entry and every
  `instruction_path` is an absolute local path; the snapshot observes the
  framework's own source files through each node's MRO
  (`ModelSnapshot._sources`), so on the bench all seven input-hash keys of
  a sourced-only bundle were framework files under the worktree, and an
  installed framework will write its `site-packages` path into every
  maker's bundle. Root-relative keys, with the framework identified by its
  version, is the remedy shape. **Untriaged.**
- **The Markdown gate refuses text that is not a dependency.** `_markdown`
  (`profile.py:143-181`) rejected `if a<b then c>d ok` and a code span
  containing a tag as an "unsupported HTML dependency". Version 1 was meant
  to refuse dependencies a bundle cannot carry, not inequalities or quoted
  markup. **Untriaged.**
- **An overlap anywhere in the root blocks an unambiguous child's reports.**
  With an overlap under `right`, `production.left.bom` raises
  `ProductionConflictError`: `_read` (`profile.py:361-374`) checks every
  overlap finding of the shared root, not the ones inside the queried
  scope. The design refuses ambiguous totals; the child's totals are not
  ambiguous. **Untriaged.**
- **Declaration paths change shape with the repetition count.** A
  one-member repeated child binding is named `kids/arbitrary_name` and a
  two-member one `kids-0/arbitrary_name` (`profile.py:1083-1085`), although
  the binding is a tuple in both cases, as the spec requires. A consumer
  test pinning a declaration path breaks when a count parameter moves from
  one to two. **Untriaged.**
- **`Finding.check_status` is always `"checked"`.** No code path produces
  another value, and the export manifest's `checks` block is a constant.
  The design's "an unrequested geometry-dependent check is not advertised
  as passed" has no runtime shape beyond omitting the finding. Either give
  the field a value or drop it before the contract is released.
  **Untriaged.**
- **The facade re-implements the preparation lifecycle by hand.**
  `ModelSnapshot._ensure.prepare` (`model.py:469-492`) copies `_prepare`
  and `InternalNode.materialize` minus markings, scope aggregation,
  `track_sources` and the `_prepared` flag. Fidelity held on the bench: the
  facade's fused STL and the lifecycle's had the same canonical content id.
  But the mesh-engine cycle is about to move these seams, and a copy this
  size drifts silently. Design debt, not a defect today. **Untriaged.**
- **Consumed STL bytes are held in memory for the life of a binding.**
  `ModelSnapshot.geometry` keeps `(observation, facts, data)` per artifact
  so a later copy pairs the same bytes with the same facts. Right for a
  partial Curta; a whole-machine export holds every printed part's STL at
  once. Scalability note. **Untriaged.**
- **Checked and found sound, for the record.** Vet reports the
  attribute-chain route (`import machinome.model as facade;
  facade.ModelSnapshot(...)`) as framework-internal, so the new deny
  entries are not bypassed that way. A mated assembly
  (`tests/mate_project/arm.py`) reads structure-only in both orders
  although mates bind ports at rest. The Curta consumer uses public members
  only and changed no simulation source.

## Voron-2 — native contact measurements and snapshot arguments (5 October 2026)

**Status: recorded; triage open, printer goal paused by the pilot during the
release.** Originating project: `projects/3D-Printers/Voron-2`, integration
`c08fa72`, evidence checkpoint `1fc9e9f`. These measurements used framework
`8d811411b13174e9f78eb636fcecc4943a740f5b` through an explicit `PYTHONPATH`,
CadQuery 2.7.0, molejo 0.2.1, SciPy 1.18.1 and Shapely 2.1.2 on Linux.
Installed 0.7.0 metadata did not identify that checkout. These original
measurements precede the release; the scoped main-branch recheck is below.
Recording them proposes no API,
source repair, collision epsilon or change to a release.

### Six screw/T-nut commons are false-empty; independent sections do not settle the volume

- **Symptom.** The printer cannot complete its native contact inventory for
  source pairs `(1290,1425)`, `(1305,1431)`, `(1306,1434)`, `(1319,918)`,
  `(1421,1083)` and `(1422,1084)`. Raw OCCT commons report valid empty
  shapes, but independently checked positive balls lie inside both originals.
  The framework correctly refuses clearance with `BrepCommonInconsistency`.
- **Evidence.** The project's `docs/evidence/thread-seat-actual-contacts.json`
  retains twelve ordered refusals and R0.01 mm balls independently cut and
  intersected against each actual operand. Those balls prove positive
  subvolume, not the complete overlap. For 1290/1425, axial section estimates
  are near 20.41077 mm3 while the transverse estimate is
  20.415075336799003 mm3; refinement has not established agreement or a
  rigorous error bound. See `thread-seat-section-diagnostics.json` and the
  retained area-accuracy/population records in the same evidence directory.
- **Smaller boundary reproduction.** Original nut 1290, section normal to Z
  at -43.06996213697989 mm: a section reported valid has curve endpoints up
  to 0.0013420880185748274 mm from their nearest topological vertices. Fine
  independent polygon sampling at 1e-6 mm rejects a self-intersection; an
  X section also fails. Direct trim endpoints and arclength endpoints agree
  exactly in this reproduction. Coarse sampling hiding the crossing is not
  an accepted answer. The project retains
  `simulation/tools/section_boundary_probe.py`, `polygon_section_probe.py`
  and `docs/evidence/resumed-integrated-validation.json`.
- **Ownership and workaround.** ADR-142's refusal is working as specified;
  no Machinome conformance defect is established. Sections use CadQuery/OCCT
  directly. Source validity alone does not certify a usable section or
  successful Boolean, and the evidence does not establish source corruption.
  There is no accepted workaround: bespoke witnesses/section diagnostics
  retain the contradiction rather than convert a false zero to clearance.
  Full native scan command: `machinome test --brep
  simulation/nominal_integrity.py:NominalIntegrity`, from the project with
  the recorded framework checkout on `PYTHONPATH`. It was deliberately
  stopped at the pilot's pause with twelve ordered failures still present.
- **Triage.** CAD-dependency investigation needed; complete overlap volumes
  remain unmeasured. No framework fix or replacement measurement is ratified.

### Copying before local relief defeats the material-containment proof for source 580

- **Symptom.** The strict subtractive-relief check for source 580 reports
  almost the whole fitted body as outside its original. This assertion calls
  a B-rep helper even when the enclosing fixture is invoked with `--mesh`;
  it is not evidence of a tessellation discrepancy.
- **Evidence.** `simulation/fits.py` uses `shape.copy().cut(cutter)`;
  `simulation/test_fits.py` requires `construction.cut(placed).Volume() ==
  0.0`. The retained `resume-components-mesh-022.log` reports
  93.68519567017215 mm3. A framework-free CadQuery reproduction on the
  unchanged extracted solids distinguishes topology copies:

  ```python
  import cadquery as cq

  source = cq.importers.importStep("simulation/.cache/part-0580.step").val()
  rail = cq.importers.importStep("simulation/.cache/part-1368.step").val()
  face = cq.Workplane("XY", obj=rail).section(0).faces().vals()[0]
  wire = face.outerWire().offset2D(.001)[0]
  tool = cq.Solid.extrudeLinear(wire, [], (0, 0, 600))
  tool = tool.translate((0, 0, -300))
  tool = tool.translate((6.963318810448982e-11, -.001, 0))
  for copied in (False, True):
      original = source.copy()
      operand = original.copy() if copied else original
      construction = operand.cut(tool.copy())
      outside = construction.cut(original)
      print(copied, construction.Volume(), outside.Volume(), outside.isValid())
  ```

  Both construction bodies are valid with volume 93.68519566365575 mm3.
  Without the extra copy, outside volume is 0 and valid; with it, outside
  volume is 93.68519567017212 mm3 and **invalid**. That invalid result is not
  proof that the relief added material. Direct topology passing does not
  independently certify the copied production artifact.
- **Workaround that failed.** The project test's comment says to keep shared
  topology for containment because reimported coincident faces can produce
  a catastrophically wrong whole-body difference. The actual construction
  copies before cutting, so that rationale no longer proves its artifact.
  The strict gate remains red; the construction was not changed to force it
  green.
- **Triage.** CAD-dependency investigation; no framework intersection policy
  participates in the minimal reproduction. The responsible copying,
  tolerance/topology, cleanup or source characteristic remains unresolved.

### A negative-leading camera vector is rejected at the viewer subprocess boundary

- **Symptom/evidence.** `machinome snapshot --renderer web --autocenter
  --viewall --imgsize 1400x1100 --camera 0,0,0,65,0,35,1400` fails with
  `argument --up: expected one argument`. The tested framework's
  `viewers/browser.py` emits `--up` and its comma tuple as separate tokens.
  This camera produces `(-0.242403876506104, 0.34618861305875415,
  0.9063077870366499)`; the negative-leading tuple is rejected by the viewer
  argument parser. The same construction is used for `--view`.
- **Workaround and limits.** Omitting the requested camera passes parsing,
  but that separate capture then reports `Failed to fetch`; it is not a
  successful replacement snapshot. OpenSCAD rendered the requested views.
  Commands, errors and inspected images are recorded in the project's
  `docs/evidence/resumed-snapshots.json`.
- **Triage.** Framework subprocess argument construction, not a new camera
  API. No fix implemented. The separate static-export browser stall belongs
  in the viewer's `workflow/warts.md`.

The same project also reproduced existing **item 14**, the bare OpenSCAD
`--preview` consuming the following filename. No duplicate wart is opened:
Voron's argument trace and successful captures without the optional flag
are additional evidence for that existing finding.

The project's original `CAD/Voron_2.4r2_Assembly_STEP.zip` remains unchanged,
SHA256 `36c6c58e096aa89aa05a0ef22f3b49cbceedc950424332772461ab0c779cc1c6`.
All project evidence paths above are relative to that independent repository;
the framework owns these findings, not the project's geometry or tests.

### Main-branch recheck, 5 October 2026

At the pilot's direction, scoped checks used framework main `d22d0a1`,
viewer main `ccc05a6` and project `df9ad29`, with no campaign `PYTHONPATH`
override. Both source packages report 0.8.0; installed metadata still says
0.7.0. Source 580 remains 1/2: the strict outside-volume assertion reports
`93.68519567017215 != 0.0` mm3. All twelve ordered thread-seat measurements
still raise `BrepCommonInconsistency`; all six independent positive witnesses
pass. The 3/3 diagnostic fixture result does not establish complete overlap
volumes. Root travel/connectivity tests pass 10/10, not the full inventory.

The project retains commands, terminal statuses, hashes and full witness
records in `docs/evidence/resumed-main-validation.json`. All 84 frozen
production hashes and the upstream archive hash match. The multi-hour final
gates and snapshot-argument reproductions were not rerun. No geometry,
collision tolerance, framework implementation or triage decision changed.
The pilot explicitly authorized rebasing and locally merging these wart
records into main without pushing; this is evidence filing, not a fix.
