Every command runs from the worktree
`/home/asa/devel/machinome/machinome/WTs/place-parts-by-mate` with
`PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
Never run two test suites at once (they share `tests/_build`). Tests
follow the style of `tests/test_markings.py`, `tests/test_joints.py`
(`FrameCarryTest`, `SiteFrameCarryTest`, `SiteSlotOrderTest`,
`JointSlotTaggingTest`), `tests/test_couplings.py` and
`tests/test_declarative_nodes.py` (`SpecializationOwnTypeGuardTest`):
`BaseNodeTest` classes, one behaviour per test, fixtures in a
`tests/<name>_project/` package. Every test in sections 2–7 is run and
seen RED, for the reason it names, before the code that turns it green;
record each red run in `evidence.md`.

## 0. Opening evidence

- [ ] 0.1 Confirm `python -c "import machinome; print(machinome.__file__)"`
  prints this worktree's path, and record the base commit (`9a96d60`).
- [ ] 0.2 Run the full suite at the base and record the counts in
  `evidence.md`.
- [ ] 0.3 Record the scope decisions the pilot ratified for the three
  questions in `proposal.md`. If any differs from the recommendation,
  STOP and update the planning artifacts (design §9 for the rigid mate)
  before writing a test.

## 1. Planning record

- [ ] 1.1 `openspec validate place-parts-by-mate --strict` passes; the
  planning commit holds the change folder and its `evidence/`, nothing
  else. ADR-147 is NOT written here: under the workspace's
  framework-change skill an ADR is extracted only after implementation
  and tests confirm the final design (task 8.4).

## 2. Red first: the frame (`tests/test_frames.py`)

- [ ] 2.1 A leaf and an `AssemblyNode` each declare a `Frame`; the class
  reports it by name through `declared_frames`, in declaration order,
  with no instance constructed. `Frame` imports from
  `machinome.node.frames` and from `machinome.node`.
- [ ] 2.2 Inheritance: a subclass inherits; a subclass assigning `None`
  drops one and the base keeps it; a frame in a plain mixin reaches the
  node.
- [ ] 2.3 Clashes refused at class creation, naming class, attribute and
  collision: parameter, child, port, joint coordinate, marking, a node
  attribute (`color`) and a `_RESERVED` name (`files`).
- [ ] 2.4 Identity: two classes differing only in a frame key the same
  artifacts (`uniq_id` equal).
- [ ] 2.5 Resolution at realization: a parameter token (`reach=150`
  gives `(0, 150, 68)`), a formula, a callable of the realized node; a
  non-number component refused naming class, frame, argument.
- [ ] 2.6 The triad: `z` normalized; `x` squared up against `z`
  (`z=(0,0,2), x=(1,0,1)` gives `x=(1,0,0), y=(0,1,0)`); `y = z × x`.
- [ ] 2.7 The default `x` on all six principal `z` directions (`+Z→+X`,
  `+X→+Y`, `+Y→+Z`, `-Z→-X`, `-X→-Y`, `-Y→-Z`), matching
  `Wrapped`'s derived zero for the same axis; a diagonal `z` with no
  `x` refused naming `x`; `z` of zero length and `x` parallel to `z`
  refused.
- [ ] 2.8 A frame whose resolution fails is refused when its declarer is
  constructed, even when no mate names it.

## 3. Red first: `Revolute` without an axis (`tests/test_joints.py`)

- [ ] 3.1 `Revolute(unit='deg')` as a class attribute is refused at class
  definition naming the class, the joint and the mate as the only place.
- [ ] 3.2 The same at a declaration site (`Wheel(turn=Revolute())`).
- [ ] 3.3 `Prismatic()` and `Orbit()` without an axis still raise as
  today.
- [ ] 3.4 `Revolute((0, 0, 1))` positional is unchanged (a green guard).
- [ ] 3.5 Re-check with `grep` that no existing test asserts
  `Revolute()` raises `TypeError`; if one does, it changes here and the
  change is recorded.

## 4. Red first: declaring a mate (`tests/test_mates.py`, fixtures in `tests/mate_project/`)

The fixture is Thor's elbow, the one `tests/joint_project/arm.py`
already pins: `MatedArm` declares `reach = Length(160)`,
`elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))`,
`forearm = MatedForearm(reach=reach)` and
`elbow = forearm.hinge.on(elbow_pin, Revolute(range=(-135, 135),
unit='deg'))`, with `MatedForearm` = `Forearm` minus its `elbow` joint
plus `hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))`; and a
`MatedHousing` reproducing Thor's shoulder with the spike's frames.

- [ ] 4.1 `forearm.hinge` in a class body yields a frame reference;
  `forearm.hinge.drives(...)` and `forearm.hinge.anything` are refused
  naming the path; a misspelled frame keeps today's sideways-read error
  listing what the class declares.
- [ ] 4.2 The class reports one mate `elbow` through `declared_mates`,
  moving `forearm.hinge` onto `elbow_pin`; a subclass inherits it.
- [ ] 4.3 Refusals at class creation, each naming class, mate and
  reason: a mate on a leaf; the assembly's own frame as the moving end;
  a moving frame two children deep; a fixed frame two children deep; a
  fixed end on a child with a class joint, with a site joint, and with a
  mate's joint; a list-held child at either end; a repeated child at
  either end; a second mate on one child (naming both); a bare
  (unnamed) mate with a freedom; `on()` with no freedom (the rigid mate,
  naming the deferral); `Prismatic`, `Orbit`, `Free` as freedoms; a
  `Revolute` stating `axis` or an explicit `at`; a freedom whose range is
  a token, a whole-range callable, or has a `Bound(reads=...)`; a
  freedom already assigned in the body; a mate name the child already
  answers to (joint, parameter, frame, method); a subclass that
  redeclares the mated child.
- [ ] 4.4 A relation in the declaring body naming the mate
  (`elbow.drives(belt.travel)`) is accepted at class creation.

## 5. Red first: what a mate compiles to

- [ ] 5.1 **Rest placement, elbow.** `MatedArm()` rendered unbound: the
  forearm's operations equal `Arm()`'s forearm operations at rest —
  kind, order and value — rotation `90` about `[1, 0, 0]`, translation
  `(0, 241.5, 68)`; `reach=150` moves the translation to
  `(0, 231.5, 68)`.
- [ ] 5.2 **Rest placement, shoulder.** The housing fixture's child rests
  within `1e-9` of `rotate(180, (0, .7071…, .7071…))`,
  `translate(0, -68, 123)`, and the rotation angle is exactly `180`.
- [ ] 5.3 **x fixes the zero.** The elbow with `hinge`'s `x` omitted
  rests turned 120 degrees about `(1,1,1)/√3` (angle exactly `120`
  after snapping), not 90 about X.
- [ ] 5.4 **Fixed end on a still child.** A `base` hand-placed with
  `translate(0, 0, 10)` carrying `seat = Frame(at=(0, 0, 79))`; the mated
  housing rests at `(0, 0, 89)`. A base whose rest placement does not
  evaluate to numbers refuses the mate at realization naming the mate
  and the base.
- [ ] 5.5 **Identity rotation and zero translation are omitted**: a
  frame pair that coincides places no operation at all.
- [ ] 5.6 **Hand placement refused.** `render()` translating a mated
  child raises naming assembly, child and mate; placing an unmated
  sibling in the same render is fine.
- [ ] 5.7 **Legacy render does not stack.** An assembly whose `render()`
  reads a driver, rendered under three bindings, carries the mate's
  placement exactly once each time (slot mark).
- [ ] 5.8 **Joint.** The realized forearm's class reports a joint `elbow`
  with axis `(0, 1, 0)` and anchor `(0, 0, 81.5)`; binding the mate to
  30 gives the forearm operations equal to `Arm`'s at 30 (the
  `FrameCarryTest` pins: `['t','r','t','r','t']`, the centring pair at
  `∓(0, 0, 81.5)`, turn `'30'`).
- [ ] 5.9 **Slot.** A wheel with its own `spin` mated with `steer`:
  `declared_joints` reads `spin`, `steer`; operations compose `spin`
  innermost, then `steer`, then the rest placement.
- [ ] 5.10 **Identity kept.** The mated child's class is named like the
  declared class, is a subclass of it, and the child's `uniq_id` equals
  an unmated one's; extend `SpecializationOwnTypeGuardTest` with the
  mate case.
- [ ] 5.11 **Coordinate.** `declared_ports(MatedArm)` reports `elbow`, a
  rotational port in degrees; a root driver bound through
  `angle.drives(arm.elbow)` to 30 gives the forearm operations of `Arm`
  at 30; the range refuses 150 as a joint's range does.
- [ ] 5.12 **Unbound rests.** Rendering with nothing binding `elbow`
  succeeds and leaves only the rest placement; bound in one enumeration
  and unbound in the next, the joint's motion is cleared.
- [ ] 5.13 **One binder.** `self.forearm.elbow = 10` in the declaring
  assembly's `simulate()`, and a root relation driving
  `arm.forearm.elbow`, are refused naming `elbow` on the assembly as the
  coordinate to bind; reading `arm.forearm.elbow` as a relation SOURCE
  is allowed.
- [ ] 5.14 **Derived coordinate.** A housing's
  `drive = shoulder + 5.85 * art2.elbow` over two mates reads the linear
  combination when both are bound.

## 6. Red first: the document

- [ ] 6.1 A fixture machine with no frame and no mate exports a document
  byte-identical to the one exported at the base commit (capture the
  base bytes in `evidence/` before implementing).
- [ ] 6.2 A root over `MatedArm` exports a document declaring the same
  version as the unmated `Arm` root (13), with the forearm's operations
  and the elbow's binding those of `Arm`'s, and no new field.

## 7. Implementation

- [ ] 7.1 `machinome/node/frames.py`: `Frame`, `declared_frames`,
  resolution (reusing the joint argument rule), the default `x`;
  re-export from `machinome/node/__init__.py`.
- [ ] 7.2 `machinome/node/base.py`: resolve frames right after
  `resolve_declared_joints(self)`.
- [ ] 7.3 `machinome/node/declarative.py`: `_declares_frame` and frame
  validation in `NodeMeta.__new__`; the `__machinome_mates__` list in
  `_DeclaringNamespace`; `record_mate`; mate processing BEFORE relation
  checks; the frame/mate clash checks in `__setitem__`;
  `ChildDeclaration.__getattr__` yielding a `FrameRef`; the axis-less
  `Revolute` refusal at a declaration site.
- [ ] 7.4 `machinome/motion/mates.py`: `FrameRef`, `Mate`,
  `declared_mates`, the class-creation checks, the installation
  (specialize + wiring), `apply_mates`.
- [ ] 7.5 `machinome/motion/joints.py`: `Revolute(axis=None, ...)`; the
  axis-less refusal in `__set_name__`.
- [ ] 7.6 `machinome/motion/couplings.py`: `read_through` admits a frame;
  `OwnRef.check_declared_on` admits a mate; the mate wiring's
  unbound-source exemption; the single-binder message names the mate.
- [ ] 7.7 `machinome/node/assembly.py`: `_rest` calls `apply_mates` after
  `render()` returns (and on every legacy re-run), refusing hand
  placement from the phase's `applied` list.
- [ ] 7.8 Every test of sections 2–6 green; the full suite green with the
  same counts as 0.2 plus the new tests, nothing skipped that was not
  skipped at the base. Record in `evidence.md`.
- [ ] 7.9 Measure `python -X importtime -c "import machinome.node"` before
  and after: `machinome/motion/mates.py` and `frames.py` add no CAD
  backend, no numpy and no trimesh at import (record the numbers).

## 8. Documentation, records, archive (the second commit)

- [ ] 8.1 User manual: the driving/joints page gains frames and mates,
  with Thor's elbow as the example, under `skills/write-the-manual`
  (examples on the public contract, pinned by the manual's tests); the
  changelog's Unreleased section names the feature.
- [ ] 8.2 Record for the studio (a separate change in
  `machinome-studio`, not made here): `shop-skills/machinome-api/SKILL.md`
  gains `Frame` and `on()`.
- [ ] 8.3 Correct `workflow/ongoing/mates-and-sketches.md` §5.1–5.2:
  `x` fixes a revolute mate's zero, not only a rigid mate's; the fixed
  end may be the declaring assembly's own frame (owner placement
  identity); a fixed end on a moving sibling does not follow it (the
  `lid = cap.bottom.on(link.knee)` example is wrong in the tree); ends
  are depth one in the first cycle; no frame is symbolic; a non-principal
  `z` must state `x`. Mark §5.1–5.2 as cut into this change.
- [ ] 8.4 Write ADR-147 under `docs/adrs/NODE/` as **Accepted** (design
  §10), add it to `docs/adrs/README.md`'s index, and give
  `docs/architecture.md` the frame and the mate where joints and
  markings are described (and the Map row).
- [ ] 8.5 Sync the delta specs into `openspec/specs/` (new `mates`;
  `joints`, `declarative-nodes`, `couplings`), `openspec validate
  --strict`, archive the change, and commit the implementation record.

## 9. Originating project: Thor (later, by a separate agent, in Thor's own repository — NOT in this worktree)

- [ ] 9.1 On a branch of `projects/Robotic-Arms/Thor`, capture the base
  poses of every model over Thor's instructions (`Home`, `Ready`,
  `Reach`, `Pick`, `Place`, `Park`) with the workspace's
  `docs/motion-general-refactor/capture_poses.py capture`, against the
  framework at this change's content commit.
- [ ] 9.2 A frame emitter beside `simulation/tools/emit_layout.py` that
  reads each root-chain link's `AttachedBy` and `AttachedTo` LCS from the
  design documents and folds the link's `AttachmentOffset` into the
  moving frame's triad, checking that the folded `z` is the joint line
  Thor declares today. The five links are listed in
  `evidence/spike.md`.
- [ ] 9.3 Re-place the five root-chain links with frames and mates
  (the scope the pilot ratified): delete `Art1`/`Art2`/`Art3`/`Art4`/
  `Art56`'s hand placements of their moving child and `Thor.render()`'s,
  the joint declarations the mates replace (`Art1.yaw`, `Art2.shoulder`,
  `Art3.elbow`, `Art4.yaw`, `Art56.wrist`), the shared constants
  (`ELBOW_ALONG_ARM`, `ELBOW_ACROSS_ARM`, `ELBOW_ACROSS_FOREARM`,
  `ARM_ORIGIN`/`ARM_TURN*`, `FOREARM_ORIGIN`/`FOREARM_TURN*`,
  `WRIST_HEIGHT`/`WRIST_TURN`) and the docstrings deriving them; rewrite
  the driver and coupling paths onto the mates' coordinates.
- [ ] 9.4 Compare with `capture_poses.py compare` at its default
  tolerance: **maximum deviation 0** on every model and pose. A non-zero
  deviation stops the migration and is reported, never explained away.
- [ ] 9.5 Thor's own tests green; snapshot inspection of `Home` and
  `Park` against the base.
- [ ] 9.6 Record the stale-solve finding in Thor's records
  (`docs/design.md`, Findings): `Art3Body`'s stored placement
  `(0, 0, -7)` against its own attachment's `(0, 0, 0)`, and the two
  parts attached to its `LCS_OptoRing` and `LCS_Bottom` solved against a
  different state of that part document — the design's own solve is
  stale against its own frames.
