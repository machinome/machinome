# Evidence: place-parts-by-mate

Every command ran from the worktree
`/home/asa/devel/machinome/machinome/WTs/place-parts-by-mate` with
`PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
No `git` write command was run at any point, and no two test suites ran
at once.

## 0.1 Worktree and base

    python -c "import machinome; print(machinome.__file__)"
    /home/asa/devel/machinome/machinome/WTs/place-parts-by-mate/machinome/__init__.py

Branch `place-parts-by-mate`, base commit `9a96d60` ("Split workflow/
notes into ongoing/ and archive/"), planning commit `95b710f` at `HEAD`.
The worktree was clean when this work began.

## 0.2 Full suite at the base (planning commit 95b710f)

    python -m pytest -q -p no:cacheprovider

    3719 passed, 4 skipped, 53 warnings, 2259 subtests passed in 401.24s (0:06:41)

## 0.3 Scope

The three scope questions of `proposal.md` were taken at their
recommendations, ratified on 2026-09-26 under the review gate the pilot
delegated on 2026-09-07 (`proposal.md`, "Ratified scope"):

1. `Revolute` is the only mate freedom; `Prismatic`, `Orbit` and `Free`
   are refused naming this cycle's scope.
2. The rigid mate is deferred; `on()` with no freedom is refused naming
   the deferral. Design §9 is not built.
3. Thor's validation covers the whole five-mate root chain (tasks
   section 9, another agent's, in Thor's own repository).

None differs from the recommendation, so the planning artifacts stand
as ratified.

## 1.1 Planning record

    openspec validate place-parts-by-mate --strict
    Change 'place-parts-by-mate' is valid

## 6.1 Base bytes, captured before any implementation

`tests.joint_project.arm:Arm`, a machine with no frame and no mate,
bound to its declared defaults and published through the same sequence
`tests/test_running_document.py`'s `document()` uses (each node's
`mtime` normalized to `null`, the one checkout-dependent field), was
captured at `95b710f` with no framework source edited:

- `evidence/base_documents/mate_free_arm.json` -- the record;
- `tests/base_documents/mate_free_arm.json` -- the same bytes, which the
  test reads (a test reading this change's folder would break when the
  change is archived).

It declares document version **2**, not 13: the parenthetical "(13)" in
task 6.2 presumed the newest version, and the unmated `Arm` machine
declares the version its features need. Task 6.2's assertion is
therefore "the same version as the unmated machine", as the `mates`
spec states it, and the measured value is 2.

## Method

Sections 2 to 6 were worked slice by slice rather than all tests first:
each section's tests were written and run RED, then the slice of
section 7 that turns them green was written, then the next section's
tests. That makes each later red fail for its own reason (a missing
rest placement, a missing joint) instead of for an import error of a
module an earlier slice would create. Every red run is recorded below
with the failure it showed.

## Section 2: the frame (`tests/test_frames.py`)

**Red** (no framework source edited):

    python -m pytest -q -p no:cacheprovider tests/test_frames.py
    41 failed, 2 passed

Every test failed on the missing declaration itself --
`ImportError: cannot import name 'frames' from 'machinome.node'` (39),
`cannot import name 'Frame' from 'machinome.node'` (2.1's second home)
and `No module named 'machinome.node.frames'` (the import probe). The
two "passed" were the parents of `subTest` loops whose every subtest
failed (2.7's six principal directions, twice).

**Implementation** (tasks 7.1, 7.2, 7.3's frame half):
`machinome/node/frames.py` (`Frame`, `ResolvedFrame`, `declared_frames`,
`resolve_declared_frames`, the principal default `x`); the argument rule
lifted out of `Joint._vector`/`Joint._resolved` into module functions
`resolved_vector`/`resolved_operand` in `machinome/motion/joints.py`,
which the joint now delegates to and the frame reuses (no second copy of
the rule); `resolve_declared_frames(self)` right after
`resolve_declared_joints(self)` in the node constructor;
`_declares_frame`/`_validate_frames` in `NodeMeta.__new__` and the two
in-body clash checks in `_DeclaringNamespace.__setitem__`; `Frame`
exported from `machinome.node`.

One test was wrong, not the code: 2.5's formula case first wrote
`reach + 81.5`, which the dimension algebra refuses (a length plus a
plain number); it now reads `reach / 2`.

**Green:** `31 passed, 51 subtests passed`.

## Section 3: `Revolute` without an axis (`tests/test_joints.py`, `AxislessRevoluteTest`)

**3.5 first:** `grep -rn "Revolute(" tests/` finds no test asserting that
`Revolute()` raises `TypeError`; every `Revolute(unit='deg', **arguments)`
in `test_joints.py` passes an axis. Nothing existing changes.

**Red:**

    python -m pytest -q -p no:cacheprovider tests/test_joints.py -k AxislessRevolute
    7 failed, 4 passed

3.1 and 3.2 failed on the message: today's `TypeError` is
`Joint.__init__() missing 1 required positional argument: 'axis'`, which
names neither the class, nor the joint, nor the mate. 3.3 (`Prismatic()`,
`Orbit()` still raise) and 3.4 (`Revolute((0, 0, 1))` positional) are
green guards, as the tasks name them.

**Implementation** (task 7.5, and 7.3's site refusal):
`Revolute.__init__(axis=None, at=_DEFAULT_ANCHOR, ...)`, the default
anchor a tuple-subclass sentinel so a mate's freedom tells "left out"
from an explicit `at=(0, 0, 0)` by identity (design decision 7);
`Joint.__set_name__` refuses an axis-less joint unless a mate claimed it
(`_mate_freedom`); `ChildDeclaration.__init__` refuses an axis-less
`Revolute` at a declaration site before specializing anything. The site
check is `isinstance(value, Revolute)`, not "axis is None": a site
`Free` has `axis = None` by construction and is untouched (the first
draft of the check refused it; caught by reading `Free.__init__` before
running the suite).

**Green:** `4 passed, 11 subtests passed`; `test_joints.py`,
`test_declarative_nodes.py` and `test_frames.py` together:
`288 passed, 351 subtests passed`.

## Section 4: declaring a mate (`tests/test_mates.py`, fixtures `tests/mate_project/arm.py`)

**Red** (sections 2 and 3 implemented, nothing of the mate):

    python -m pytest -q -p no:cacheprovider tests/test_mates.py
    43 failed, 9 passed

Every test failed because a class body could not yet name a child's
frame: `SidewaysReadError: cannot read 'hinge' off the Pin declaration
(part.hinge): a sibling's parameter is not a value in a class body ...`
(30 of them, the fixture module's own `forearm.hinge` among them), the
misspelling test because the listing named no frame (`Pin declares: no
port, joint or child.`), the read-through test because the same
sideways error fired one attribute early, and the enumerator tests on
`No module named 'machinome.motion.mates'`. The nine "passed" are
parents of `subTest` loops whose subtests all failed.

**Implementation** (tasks 7.3's mate half, 7.4's declaration half, 7.6's
first two items): `machinome/motion/mates.py` -- `FrameRef` (refusing
`drives`, arithmetic and attribute reads by name), `Mate` (a
`Coordinate` owning one `RotationalPort`, with `_names_in_body`),
`state_mate`, `declared_mates`, and `declare_mates` with every
class-creation refusal; `record_mate` and the `__machinome_mates__`
list in `_DeclaringNamespace`; `NodeMeta.__new__` calling
`declare_mates` BEFORE constraints and relations are checked, for a
class that states or inherits a mate; `ChildDeclaration.__getattr__`,
`RepeatDeclaration.__getattr__`, `PathRef.__getattr__` and
`BroadcastRef.__getattr__` yielding a `FrameRef` (the repeat and depth
recorded, refused by the mate, not by the read); `read_through`
admitting a frame; `coordinate_ref` refusing a frame as a relation end
by name; `_declared_places` listing frames; `OwnRef.check_declared_on`
admitting a declared mate; and the in-body clash of a mate with any
other declaration of the same name.

**The `_is_joint()` review finding.** `_is_joint` duck-types on
`coordinate` and says True for a mate. Its callers, checked:

- `_refuse_coordinate_clash` (in-body reassignment): a mate reassigned
  over a port would have been reported as "the joint ... and the port".
  A mate-specific clash check now runs first and names the mate
  (`test_a_mate_and_a_parameter_cannot_share_a_name`).
- `ChildDeclaration.__init__` site-joint detection: a mate passed as a
  keyword (`gauge = Dial(turn=elbow)`) is already bound in the executing
  body, so `_in_current_body` makes it a WIRING, never a site joint --
  correct. But `_check_wiring` then did not find it among the owner's
  coordinates (it collects ports' and joints' identities, and a mate is
  neither) and fell into the "a joint declared on a THIRD class"
  message, which is wrong. A mate's coordinate is an ordinary coordinate
  of the assembly, so `_check_wiring` now admits a mate declared on the
  owner (read off the class dictionaries, since `__set_name__` order
  precedes `declared_mates`). Pinned by the `GaugedArm` fixture
  (`test_a_mates_coordinate_is_wired_like_any_other`, and 5.11's wiring
  case below).

**Clarification (not a redesign):** a subclass's OWN mate whose moving
end is a child an ancestor declares is refused
(`test_a_subclass_cannot_mate_a_child_its_base_declares`). Installing
the mate's joint replaces the child declaration's class and adds to its
wiring, and that declaration object is shared with the base and every
other subclass, which would silently gain the joint. The spec's moving
end is "a frame declared by a child the assembly declares directly"; a
child inherited from a base is refused naming the base, with the remedy
(state the mate in the base, or redeclare the child).

**Green:** `31 passed, 140 subtests passed`; with `test_joints.py`,
`test_couplings.py`, `test_declarative_nodes.py`, `test_markings.py` and
`test_frames.py`: `603 passed, 725 subtests passed`.

## Section 5: what a mate compiles to (`tests/test_mates.py`, `RestPlacementTest`, `InstalledJointTest`, `MateCoordinateTest`)

**Red** (sections 2 to 4 implemented: a mate is declared and checked,
nothing is compiled):

    python -m pytest -q -p no:cacheprovider tests/test_mates.py \
        -k "RestPlacement or InstalledJoint or MateCoordinate"
    27 failed, 1 passed

Each for its own reason: the mated child carried no operation at all
(`Lists differ: [] != [['r', '90', [1, 0, 0]], ['t', ['0.0', '241.5',
'68.0']]]` for 5.1/5.7, `[] != [[0.0, 0.0, 89.0]]` for 5.4, `IndexError`
reading the rest rotation for 5.2/5.3/5.1-reach); no joint on the child
(`[] != ['elbow']` for 5.8, `['spin'] != ['spin', 'steer']` for 5.9,
`[] != ['t', 'r', 't', 'r', 't']` for 5.8's binding and 5.11's driver,
`'MatedForearm' object has no attribute 'elbow'` for the wired joint);
the child realized as its declared class (`unexpectedly identical:
<class 'tests.mate_project.arm.MatedForearm'>` for 5.10); and
`ValueError not raised` for the hand-placement, symbolic-fixed-placement
and one-binder refusals (5.4, 5.6, 5.13). The one "passed" is the parent
of 5.7's three failing subtests.

Five tests first went GREEN at their first run and were rewritten, as
the briefing requires, because the declaration slice already satisfied
what they asserted: 5.5 (coinciding frames place nothing -- true of a
mate that does nothing), 5.11's port enumeration, the wiring of a mate's
coordinate into a port, the in-body relation from a mate, and 5.14's
derived coordinate (all ordinary coordinate machinery once
`OwnRef`/`_check_wiring` admit a mate). Each now also asserts what only
the compile gives -- 5.5 that the BOUND mate turns the part about the
shared line with still no rest operation, the others that the child's
installed joint took the value -- and each then ran red (`[] != ['t',
'r', 't']`, `'elbow' not found in {}`, `'MatedArm' object has no
attribute 'shoulder'`, `'Pin' object has no attribute 'swing'`,
`'MatedForearm' object has no attribute 'elbow'`).

5.10's extension of `SpecializationOwnTypeGuardTest`
(`test_a_mated_child_is_its_declared_class_by_subclass_only`) was
written after the installation existed, so its red is a MUTATION run:
with `_install` disabled in `declare_mates` it fails
(`unexpectedly identical: <class '...Link'>`), restored it passes.

**Implementation** (tasks 7.4's compile half, 7.6's last two items,
7.7): in `machinome/motion/mates.py`, `_install` (the `Revolute` built
from the moving frame's DECLARED `z` and `at` and the freedom's range and
unit, put on the child declaration by `_specialize`, and the mate added
to the declaration's `wiring`), `apply_mates` with the hand-placement
refusal, the slot-marked drop-and-reapply, `_placement`
(`P_owner . F_fixed . F_moving^-1` in pure Python, the fixed child's
rest placement composed through each operation's `matrix()` and refused
by name when not numeric) and `_axis_angle` (angle by `atan2`, axis from
the antisymmetric part up to 90 degrees and from the diagonal beyond,
snapped); `_rest` in `machinome/node/assembly.py` calling `apply_mates`
after the render's phase is popped, before the legacy/cached branch, so
it runs once per instance for an ordinary render and on every re-run of
a legacy one; `Wiring.rests_unbound` and `_refuse` skipping a mate's
wiring whose source is unbound; `BoundPort.mated_by`, set by
`_record_wiring` for a mate's wiring, and `bind` refusing a hand or
relation binding of the installed joint through `mates.refused_binding`,
which names the mate's coordinate by instance path (`Bind arm.elbow
instead.`).

Measured numbers (the design's snapping claim):

- elbow: `['r', '90', [1, 0, 0]]`, `['t', ['0.0', '241.5', '68.0']]`;
  at `reach=150`, `(0.0, 231.5, 68.0)`;
- shoulder: angle `'180'` exactly, axis `(0, 0.7071067811865476,
  0.7071067811865476)` -- both components the same square root, from the
  diagonal -- and translation `(0, -68, 123)` within `1e-9`;
- default-`x` elbow: angle `'120'` exactly (the spike's
  `120.00000000000001` snapped), axis `(1, 1, 1)/sqrt(3)`, translation
  `(-81.5, 160, 68)`.

**Green:** `tests/test_mates.py` `56 passed, 154 subtests passed`; with
`test_joints.py`, `test_couplings.py`, `test_declarative_nodes.py`,
`test_markings.py`, `test_frames.py` and `test_running_document.py`:
`739 passed, 832 subtests passed`.

## Section 6: the document (`tests/test_mates.py`, `DocumentTest`)

Both tests assert an INVARIANCE, so neither can fail at the code state
it guards; each was shown to discriminate by a mutation run, restored
afterwards (the restored base file compared byte-identical to
`evidence/base_documents/mate_free_arm.json` with `cmp`).

- **6.1** `test_a_machine_without_mates_is_unchanged_in_every_byte`:
  `tests.joint_project.arm:Arm`, published now, against the bytes
  captured at `95b710f` before any implementation (§6.1 above). Green
  with every section implemented. Mutation: one value of the base file
  changed (`"241.5"` to `"241.50"`) -- red, `AssertionError: '{\n
  [1236 chars]241.5",...' != '{\n [1236 chars]241.50",...'`.
- **6.2** `test_a_mated_machine_needs_no_newer_consumer`: a root over
  `MatedArm` driving the mate from one driver
  (`MatedElbowMachine`) against the unmated `Arm` root: same `version`
  (**2**, measured -- see §6.1 on the "(13)"), same `format`, same
  top-level keys, the same `drivers` table, the forearm's operations
  equal in kind, order, rotation (angle `'angle'`, the driver's token,
  and axis) and translation value, and every node entry a field set the
  unmated document already publishes. Mutation: `apply_mates` disabled
  in `_rest` -- red, `Lists differ: ['t', 'r', 't'] != ['t', 'r', 't',
  'r', 't']` (the joint without its rest placement).

The mated document differs from the hand-written one only in spelling a
zero translation component `"0.0"` where `Arm.render()` wrote the
integer `0`, which is the arithmetic's float, not a new field or value
(ADR-097: the framework does not edit the arithmetic); the comparison
is numeric there, as the Thor migration's pose comparison is.

**Green:** `2 passed, 4 subtests passed`.

## 7.8 Full suite at the end

First end-of-implementation run (`full-1`), before the manual work:

    2 failed, 3811 passed, 4 skipped, 53 warnings, 2479 subtests passed in 400.87s

Both failures were pins of the previous state, not regressions:

- `tests/test_node_lazy_exports.py::NodePackageExports::test_all_lists_exactly_the_names_exported_before`
  pins `machinome.node.__all__`; the `mates` spec requires `Frame` to
  resolve from `machinome.node`, so its table gained
  `'Frame': 'machinome.node.frames'` with a comment naming the change.
- `tests/test_profile_documentation.py::...::test_released_status_changelog_and_history`
  refused the word "unreleased" anywhere above the 0.7.0 section of the
  changelog; it failed because the changelog was edited mid-run for task
  8.1. The write-the-manual skill's "Work after a release" rule puts work
  since a release in ONE `Unreleased` section above the released one, so
  the assertion now admits exactly that heading and nothing else
  (checked: the unedited test fails on the new changelog, the edited one
  passes; the 0.7.0 section's own assertions are unchanged).

Final run (`full-2`):

    python -m pytest -q -p no:cacheprovider -rs
    3816 passed, 4 skipped, 53 warnings, 2487 subtests passed in 400.94s (0:06:40)

Base: 3719 passed, 4 skipped. The 97 new tests: `test_frames.py` 31,
`test_mates.py` 61, `test_joints.py` 4 (`AxislessRevoluteTest`),
`test_declarative_nodes.py` 1 (the mate case of
`SpecializationOwnTypeGuardTest`). The 4 skips are the base's
(browser snapshot e2e not enabled, jscad CLI absent, the two vendor-STEP
cases), nothing newly skipped.

## 7.9 Import cost

`python -X importtime -c "import machinome.node"`, three alternating
runs each, the base tree exported with `git archive 95b710f` beside the
worktree:

    base      141.5 ms, 115.0 ms, 113.9 ms  (cumulative, machinome.node)
    change    118.6 ms, 120.5 ms, 115.6 ms

indistinguishable within run-to-run noise. `machinome.node.frames` is
imported by `machinome.node.base` at module scope and costs 0.34 ms self
(it imports `math` only); `sys.modules` after `import machinome.node` is
272 modules at the base and 273 now, the one addition being `frames`.
Importing `machinome.node.frames` and `machinome.motion.mates` after
`machinome.node` adds exactly `machinome.motion`,
`machinome.motion.ports` (which any node realization imports anyway) and
`machinome.motion.mates`; `trimesh`, `cadquery`, `build123d` and `OCP`
are not imported. `numpy` is already imported by `machinome.node` at the
base (by `node/base.py`), so neither module adds it; `mates.py` reaches
`numpy` only inside `_rest_placement`, during a live render.
`tests/test_frames.py::DeclarationTest::test_importing_frames_adds_nothing_outside_the_framework`
pins the frame half in a fresh interpreter.

## 8.1 The manual

Under `skills/write-the-manual`:

- **Red first:** `tests/test_mates.py::ManualTest`, three tests, ran red
  on the unedited manual: `ValueError: 'Frames and mates' is not in list`
  (the joints page), `'machinome.node.frames.Frame' not found` (the API
  reference), `'Unreleased\n----------' not found` (the changelog).
- **Written:** `docs/concepts/joints.rst` gains a *Frames and mates*
  section after *The frame rule*, folded into the page that owns the
  subject, and one sentence in *Refusals*; its example is a complete
  module on the public contract (`machinome.motion.joints`,
  `machinome.node`, `machinome.node.frames`, `machinome.parameters`,
  `solid2`) which `ManualTest` EXECUTES and renders, checking the rest
  placement the prose states and `declared_mates`.
  `docs/reference/api.rst` gains a *Frames and mates* section
  (`Frame`, `declared_frames`, `declared_mates` autodoc).
  `docs/project/changelog.rst` gains an `Unreleased` section naming the
  feature (ADR-147 in the bullet), and `docs/project/status.rst` a
  *Since |release|* paragraph, the one page allowed to say unreleased.
- **Rule 3 (machines by kind, never by project):** the tasks ask for
  "Thor's elbow as the example"; the manual uses the elbow's numbers and
  calls it an arm's elbow, as the existing joints page already does, and
  names no project. The module docstrings of `frames.py` and `mates.py`,
  which `help()` and autodoc show, were reworded the same way.
- **Build:** `python -m sphinx -E -b html -n -W --keep-going docs <out>`
  reports 5 warnings, the SAME 5 the base tree reports under the same
  command (`api.rst:23/35/76` unresolved references and two `Sim`
  docstrings); none is on a page or docstring this change touched. The
  built `concepts/joints.html`, `reference/api.html` (six `Frame`/
  `declared_mates` anchors) and `project/status.html` were opened.
  `tests/test_docs_structure.py` and `tests/test_profile_documentation.py`
  pass.

## 8.2 Record for the studio

The studio's `shop-skills/machinome-api/SKILL.md` (the framework's
complete public contract, in the separate `machinome-studio`
repository) must gain `Frame` (`machinome.node.frames`, also
`machinome.node`), the `<child>.<frame>.on(<frame>, Revolute(...))`
statement with its compile and refusals, `declared_frames` and
`declared_mates`, and the one change to `Revolute` (axis optional only as
a mate's freedom). That is a separate change in that repository, made by
someone else; nothing of it is made here.

## 8.3 The working note

`workflow/ongoing/mates-and-sketches.md`: §5 now opens with a paragraph
recording that §5.1–5.2 were cut into this change (revolute only), and
six corrections are folded in place, each marked *(corrected
2026-09-26)*: `x` fixes a revolute mate's zero; the principal-only
default `x`; no frame is symbolic (twice: components, and the "Symbolic
frames" rule); the fixed end may be the declaring assembly's own frame
and ends are depth one in the first cycle (with the rigid mate deferred);
a fixed end on a moving sibling does not follow it, so the
`lid = cap.bottom.on(link.knee)` example is wrong in the tree; and the
freedom's range resolving against the child. §6's first candidate
records that the cut came from Thor.

## 8.4 ADR and architecture

`docs/adrs/NODE/ADR-147-a-mate-compiles-to-a-rest-placement-a-joint-and-a-coordinate.md`,
**Accepted**, written after `full-2` confirmed the design; indexed in
`docs/adrs/README.md` under NODE. `docs/architecture.md`: the Node model
section gains the frame paragraph after the marking's; the Kinematics
section gains the mate paragraph after ADR-114's slot paragraph; the Map
rows *Node model* (`frames.py`, spec `mates`, ADRs 120 and 147) and
*Motion* (`mates.py`, spec `mates`, ADRs 097, 098, 147).

Not done here (the orchestrator's, after review): 8.5 (spec sync,
archive, commit) and section 9 (Thor, in Thor's repository).

## Where the implementation departs from, or clarifies, `design.md`

None contradicts a ratified behaviour; each is a clarification the
evidence forced or the design left open.

1. **Every mate refusal is made at class creation, not at the `on()`
   call.** The spec requires each refusal to name the mate, and a mate's
   name exists only once the assignment has run; `on()` (including
   `Frame.on`, which the design said "exists only to refuse") records the
   statement, and `declare_mates` refuses with the name. The one fact
   only knowable in the body -- whether the freedom was already bound to
   a name there -- is captured at `on()`, and `on()` marks the freedom
   (`_mate_freedom`) so the axis-less refusal of `Joint.__set_name__`
   does not pre-empt the mate's own "already declared" refusal.
2. **A subclass's own mate on a child an ancestor declares is refused.**
   Installing the joint replaces the child declaration's class and adds
   to its wiring; that declaration object is shared with the ancestor
   and its other subclasses (§4 above).
3. **An inherited mate whose fixed frame the subclass drops** (`pin =
   None`) is refused at the subclass's creation, beside the design's
   "subclass that redeclares the mated child".
4. **Mates are processed before constraints as well as relations**, since
   `.constrain()` can name a coordinate too.
5. **The argument rule was lifted, not duplicated:** `Joint._vector` /
   `_resolved` now delegate to module functions `resolved_vector` /
   `resolved_operand`, which `Frame.resolve` calls.
6. **`_check_wiring` admits a mate's coordinate as a wiring source**
   (the `_is_joint` review finding, §4 above).
7. **The range refusal comes from the installed joint**, so its message
   names the child's joint (`arm.forearm: joint 'elbow' declares the
   range -135 to 135 deg, and 150 is outside it`); `Mate.__set__` binds
   the assembly's port without a range check of its own. The design's
   open question (whether the mate's coordinate carries the range for
   range-reading consumers) stays open: not carried.
8. **The 180-degree axis** is taken from the diagonal for every angle
   above 90 degrees, all components by the same square root with signs
   from the symmetric part; the design's "from the diagonal" for 180 is
   the special case. A zero translation component is normalized from
   `-0.0` to `0.0`; nothing else is rounded.
9. **Document version**: 2, the unmated machine's, not the "(13)" of task
   6.2 (§6.1 above).
10. **The manual names no project** (skill rule 3), where the task said
    "Thor's elbow as the example" (§8.1 above).
11. **Two existing tests changed**: `test_node_lazy_exports.py` gains
    `Frame` in its export table, and `test_profile_documentation.py`
    admits one `Unreleased` changelog section (§7.8 above).

## Ratification review of the implementation (orchestrator, 2026-09-26)

Adversarial review before sync and archive, on the uncommitted tree above
`95b710f`. Read in full: `machinome/motion/mates.py`,
`machinome/node/frames.py`, and the diffs of `declarative.py`,
`couplings.py`, `ports.py`, `joints.py`, `assembly.py`, `base.py`, the
ADR, `docs/architecture.md`, the manual section and the note
corrections. Checked against the source: `declared_joints` enumerates by
`isinstance(Joint)` and `clear_solved` finds a coordinate's joint the same
way, so a `Mate` (a `Coordinate`, not a `Joint`) is never resolved,
enumerated or cleared as a joint of the assembly; the binding refusal of
the installed joint sits inside the existing `wired_from and not
_wiring_depth` guard, so the mate's own wiring passes; `apply_mates` runs
on every `_rest` call, legacy re-runs included, and drops by slot mark
first.

Three probes of my own, outside the suite (`evidence/review_probes.py`,
run from a scratch project with a `[tool.machinome]` manifest):

1. axis–angle round trip over 2000 random rotations in every quadrant,
   180° and 179.999999° included: worst rebuilt-matrix residue
   `3.7e-14`;
2. a two-mate chain (Thor's elbow and wrist frames, a driver on each
   coordinate) against a hand-placed twin with class-body joints, under
   seven bindings including both range ends: maximum pose deviation
   `0.0` on three bodies;
3. a fixed end on a child hand-placed with a rotation AND a translation
   (`rotate(90, Z)`, `translate(5, 0, 3)`): the mated housing's world
   matrix equals the expected `(5, 0, 82)` with the turn, residue `0.0`.

Full suite re-run by the reviewer from a clean shell: see the commit
message of the implementation commit for the counts.

## Validation in the originating project (Thor, 2026-09-26)

Performed by a separate agent in Thor's own repository, on branch
`place-parts-by-mate` (commits `7aebdd0`, `8a42a59`, `5cc98c4`), against
this worktree's implementation (its code is that of the implementation
commit; only two manual pages were amended after Thor's records cited it).
All five root-chain links re-placed by frames and mates; `Thor.render()`
gone; five joint declarations and thirteen shared constants deleted;
frames emitted from the design's own connectors by
`simulation/tools/emit_frames.py` and guarded by `test_frames.py`.
`capture_poses.py compare` against `main`: **maximum deviation 0** over 25
poses and 441 leaves (largest unrounded difference `1.42e-14` mm, the
shoulder's new centring pair). Thor's tests identical to `main` (32 of 34;
the two failures are pre-existing). `Home` and `Park` snapshots
pixel-identical to `main`. No framework refusal hit; two probed and fire
by name. Six findings recorded in `workflow/warts.md` under this cycle's
section; the design's stale solve is recorded in Thor's records (Finding
20).
