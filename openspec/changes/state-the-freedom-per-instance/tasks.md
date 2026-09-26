Every command runs from the worktree
`/home/asa/devel/machinome/machinome/WTs/state-the-freedom-per-instance`
with `PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
Never run two test suites at once (they share `tests/_build`). Tests
follow `tests/test_mates.py`'s style: `BaseNodeTest` classes, one
behaviour per test, fixtures in `tests/mate_project/`. Every test in
section 2 is run and seen RED, for the reason it names, before the code
that turns it green; record each red run in `evidence.md`.

## 0. Opening evidence

- [ ] 0.1 Confirm `python -c "import machinome; print(machinome.__file__)"`
  prints this worktree's path, and record the base (`61f2335`, plus the
  records commit `9e228fa`).
- [ ] 0.2 Run the full suite at the base and record the counts in
  `evidence.md`.
- [ ] 0.3 Record the pilot's answers to the four scope questions in
  `proposal.md`. If any differs from the recommendation, STOP and update
  the planning artifacts before writing a test.
- [ ] 0.4 Record `sha256sum` of every file in `tests/base_documents/` at
  the base in `evidence.md` (the byte-identity guard of 2.10).

## 1. Planning record

- [ ] 1.1 `openspec validate state-the-freedom-per-instance --strict`
  passes; the planning commit holds the change folder and its
  `evidence/`, nothing else. No ADR here (task 4.4).

## 2. Red first (`tests/test_mates.py`, fixtures in `tests/mate_project/handed.py`)

Fixtures (a new module; adding it is not implementation), with
OpenArm's joint 1 numbers (`evidence/finding.md` §3), in the shortest
form that discriminates the node the function receives:

- `HandedLink(Solid2Node)`: `origin = Frame()`, NO `left` parameter, a
  small cube.
- `HandedMount(AssemblyNode)`: `left = Flag(False)`;
  `pin = Frame(at=lambda node: (0, 62.5 if node.left else -62.5, 0))`;
  `link = HandedLink()`; `turn = link.origin.on(pin, Revolute(axis=lambda
  node: (0, 1, 0) if node.left else (0, -1, 0), range=lambda node:
  (-200, 80) if node.left else (-80, 200), unit='deg'))`.
- `ContraryLink(Solid2Node)`: `origin = Frame()` and its own
  `left = Flag(True)`; `ContraryMount(AssemblyNode)`: as `HandedMount`
  over `link = ContraryLink()` (child's `left` NOT passed).
- `HandedPair(AssemblyNode)`: `angle = Driver(default=30, unit='deg')`,
  `left = HandedMount(left=True)`, `right = HandedMount(left=False)`,
  `angle.drives(left.turn)`, `angle.drives(right.turn)`.
- The hand-placed twin, OpenArm's pre-mate form: `TwinLink(Solid2Node)`
  declaring `left = Flag(False)` and `turn = Revolute(axis=lambda node:
  ..., range=lambda node: ..., unit='deg')` over its own `left`;
  `TwinMount(AssemblyNode)` with `left`, `link = TwinLink(left=left)` and
  a `render()` translating the link to the side's origin; `TwinPair` as
  `HandedPair`, driving `left.link.turn` and `right.link.turn`.

- [ ] 2.1 **The refusals are gone.** In
  `RefusalTest.test_a_stated_line_is_numbers` move the `callable_axis`
  case out, and in
  `RefusalTest.test_a_freedom_range_that_depends_on_a_declarer` move the
  `whole` case out, into `test_a_freedom_axis_or_range_may_be_a_function`:
  `Revolute(axis=lambda node: (0, 0, 1))` and `Revolute(range=lambda
  node: (0, 90))` create the class and report the mate. Red at the base
  with the two refusals. The remaining cases of both tests (token,
  formula, two components, `bool`; range token, `Bound` with reads) stay
  and stay green.
- [ ] 2.2 **A function `at` stays refused, with its own reason.**
  `Revolute(at=lambda node: (0, 0, 0))` refused at class creation naming
  the class, the mate and `at`, and saying a stated anchor is three
  numbers in this version (assert that fragment; at the base the
  refusal fires with "called with the moving child", so the fragment
  makes it red).
- [ ] 2.3 **OpenArm's joint on both sides.** `HandedMount(left=True)` and
  `HandedMount(left=False)`: `declared_joints(type(m.link))['turn']
  .arguments(m.link)` is `((0, 1, 0), (0.0, 0.0, 0.0), (-200, 80))` and
  `((0, -1, 0), (0.0, 0.0, 0.0), (-80, 200))`; rendered unbound, the
  link's operations are one translation `(0, ±62.5, 0)` and no rotation;
  driven to 150 through a root's driver (the shape of
  `test_the_range_belongs_to_the_freedom`), the left mount raises
  `JointRangeError` naming `turn` and the right mount accepts it. Red at
  the base (class refused).
- [ ] 2.4 **The function receives the assembly.** (a) With
  `HandedMount`, whose child has no `left`: realizing succeeds (under
  "called with the child" it would raise `AttributeError`). (b) With
  `ContraryMount(left=False)`: the axis function records its argument;
  it is the `ContraryMount` instance, and the joint's axis is
  `(0, -1, 0)`, not the child's `(0, 1, 0)`. Both red at the base.
- [ ] 2.5 **Called once per realized assembly.** Counting functions as
  `axis` and `range` on a mount; realize two mounts; bind each three
  times, render, export with `published`: each count is 2, and was 2
  before the first binding.
- [ ] 2.6 **The state it sees.** A mount declaring a child `base` before
  the moving child; its axis function reads `node.base` and
  `resolved_frames(node)['pin']` and returns a side's axis: realization
  succeeds and the joint turns about the returned axis.
- [ ] 2.7 **The result is taken as the numbers are.** Classes are
  created, and realization raises `ParameterError` naming the mount's
  class, the mate and the argument and quoting the result or the
  exception, for an axis function returning `(0, 1)`, `(0, 0, 0)`,
  `(0, 0, True)`, `'xyz'`, a function, or raising `KeyError`; and for a
  range function returning `(0,)`, `(True, 90)`, a pair holding a
  `Bound` that reads a declared port, or raising. Assert the refusal
  names the MOUNT's class (not the link's) for each. A returned
  `(0, 3, 0)` resolves to exactly `(0, 1, 0)`.
- [ ] 2.8 **The class reads return the function.**
  `declared_mates(HandedMount)['turn'].freedom.axis` and `.range` are
  the function objects written (identity), `anchor_written` is false;
  reading calls neither (counting functions).
- [ ] 2.9 **The twins.** `HandedPair` against `TwinPair`, at the
  default 30 and at bindings `-80, 0, 80` and unbound: each link's
  operations equal the twin's in kind and order, rotations equal in angle
  and axis within `1e-9`, translations within `1e-9`, and the composed
  world matrices of every leaf equal within `1e-9`.
- [ ] 2.10 **Nothing else moves.** Every file in `tests/base_documents/`
  is byte-identical to its hash in 0.4 (the existing `DocumentTest` and
  `StatedLineDocumentTest` byte-identity tests, run unedited);
  `HandedPair`'s exported document declares the version an unmated
  machine declares and has no key the twin's lacks. Every existing test
  in `tests/test_mates.py`, `tests/test_frames.py`, `tests/test_joints.py`
  and `tests/test_declarative_nodes.py` stays green unedited except the two
  narrowed in 2.1; the installed joint of a mate stating no function
  still holds the moving frame's declared `z` and `at` as the same
  objects.

## 3. Implementation

- [ ] 3.1 `machinome/motion/mates.py`, class creation: `_check_freedom`
  accepts a whole-range function (callable, no `dimension`, not a
  `Bound`); `_check_stated` accepts a function `axis`, and refuses a
  function `at` with the "three numbers in this version" reason; tokens,
  formulas, `bool`s and every other refusal unchanged. Factor the result
  rules (three real numbers, non-zero axis; the range pair rule) so the
  realization check below words them the same.
- [ ] 3.2 `_install`: unchanged construction; mark the joint as resolved
  at the child's realization when the freedom states a function.
- [ ] 3.3 A realization-time resolution in `mates.py`, called from
  `ChildDeclaration.realize` (`machinome/node/declarative.py`) beside
  `_resolve_site_joints`: call each of the freedom's functions with the
  realized assembly (`owner`) once — before the child is constructed —
  check its result by 3.1's rules, raising `ParameterError` naming the
  assembly's class, the mate and the argument; after construction,
  resolve the joint against the child with the results substituted for
  the functions (the moving frame's defaults still against the child),
  through `Joint.resolve`, and cache it in the child's
  `_joint_arguments[<mate>]`.
- [ ] 3.4 `machinome/motion/joints.py`: `resolve_declared_joints` skips a
  marked joint, as it skips a site-declared one; `Joint.arguments`' lazy
  path refuses a marked joint, naming the mate and its assembly, instead
  of resolving it against the child.
- [ ] 3.5 Docstrings and messages: `mates.py` module docstring, `Mate`
  (the reads: `axis`/`range` may be the function as written),
  `_check_freedom`, `_check_stated`, `_install`; `joints.py`
  `resolve_declared_joints`; `declarative.py` `ChildDeclaration.realize`.
- [ ] 3.6 Every test of section 2 green; the full suite green with the
  counts of 0.2 plus the new ones, nothing skipped that was not skipped
  at the base. Record in `evidence.md`.

## 4. Documentation, records (the second commit)

- [ ] 4.1 `docs/concepts/joints.rst`, "Frames and mates", under
  `skills/write-the-manual`: a third, runnable example in the shortest
  form — a handed mount whose frame, axis and range are functions of
  its `left` flag — with one paragraph: a freedom's `axis` and `range`
  may each be one function, called with the assembly that states the
  mate, once, when it builds the moving part, in the state a site's
  function sees; its result is taken as the numbers are and read in the
  moving part's frame; `at` stays numbers. The refusal list loses "a
  function axis" and "a range that reads the node" and gains "a
  function `at`". The paragraph on reads says `freedom.axis` and `range`
  may read a function. Pinned by a `ManualTest` test that execs the
  example, realizes both sides and checks each installed joint's axis
  and range.
- [ ] 4.2 `docs/project/changelog.rst`, Unreleased: a bullet saying a
  mate's freedom may state its axis and range as a function of the
  assembly that states it, so a handed design mates per instance
  (ADR-150).
- [ ] 4.3 Record for the studio (a separate change in
  `machinome-studio`, not made here):
  `shop-skills/machinome-api/SKILL.md` gains the handed freedom.
- [ ] 4.4 Write ADR-150 (NODE) as **Accepted** (design §8); add
  *Amended by* lines to ADR-147 and ADR-148; all three in
  `docs/adrs/README.md`'s index; amend `docs/architecture.md`'s mate
  paragraph ("whose range does not depend on a declarer and whose
  stated line, if any, is three numbers": the axis and range may be a
  function of the assembly, resolved as the assembly realizes the
  child).
- [ ] 4.5 `workflow/ongoing/mates-and-sketches.md`, "Range and `Bound`":
  a whole-range function of the assembly is admitted by this change.
- [ ] 4.6 `workflow/warts.md`: the bullet "A mate's freedom cannot state
  its line or its range as a function of the node" gains its
  disposition (fixed by `state-the-freedom-per-instance` for `axis` and
  `range`; `at` stays numbers; pending the OpenArm follow-up of §6).
- [ ] 4.7 `docs/reference/api.rst`: no entry changes (no new read); the
  `Mate` entry is rendered from its docstring, which carries 3.5's
  wording, and the existing `test_the_reference_lists_frames_and_mates`
  stays green.

## 5. Sync and archive

- [ ] 5.1 Sync the delta spec into `openspec/specs/mates/spec.md`,
  `openspec validate --strict`, archive the change, final full suite,
  and commit the implementation record.

## 6. Originating project: OpenArm (later, by a separate agent, in its own repository — NOT in this worktree)

- [ ] 6.1 On a branch of `projects/Robotic-Arms/openarm` from `main`
  (`48a2ac9`), capture base poses of every model (`OpenArm`,
  `ArmsAtRest`, `GrippersAtThirtyDegrees`, `Body`) over `OpenArm`'s
  instructions and three limit poses with the workspace's
  `capture_poses.py capture`, against the framework at this change's
  content commit.
- [ ] 6.2 Each joint becomes a mate stated in its parent, in
  SO-ARM100's shape: a moving `Frame()` on each joint class and finger
  class; a fixed frame on the parent whose `at` is a function of the
  parent's side (`ARM_JOINTS[side][row].origin`,
  `seated_finger_origin(left, index)`); a freedom
  `Revolute(axis=lambda node: ...axis, range=lambda node: ...limits,
  unit='deg')` over the parent's `left`. `_revolute`,
  `_finger_revolute` and the joints they declare go; the translates in
  `_Joint.render`, `Arm.render` and the fingers' in
  `PinchGripper.render` go (the mounts' and the gripper base's stay).
- [ ] 6.3 Relations re-pathed to the mates' coordinates (the root's
  `...joint1.turn` paths; `PinchGripper`'s `grip.drives(...)`, whose
  `handed` law is then handed the gripper, which carries `left` too).
  Mate names are free on both the parent and the child (a chain cannot
  reuse `turn` at every level); a test that names a joint by `turn`
  follows the mate's name, and each such edit is recorded.
- [ ] 6.4 `capture_poses.py compare` at its default tolerance:
  **maximum deviation 0** on every model and pose. A non-zero deviation
  stops the migration and is reported.
- [ ] 6.5 OpenArm's tests pass with the same counts as `main`, their
  only edits those of 6.3; the three README snapshots re-rendered and
  compared against `main`'s.
