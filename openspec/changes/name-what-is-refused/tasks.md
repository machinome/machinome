Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Every framework command runs as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`;
every project command as
`env -C <project> PYTHONPATH=<bench>:<project> /home/asa/devel/machinome/.venv/bin/<tool> ...`
with `<OMX>` = `/home/asa/devel/machinome/projects/Robotic-Arms/open_manipulator`
and `<OpenArm>` = `/home/asa/devel/machinome/projects/Robotic-Arms/openarm`.
`<scratch>` is the campaign scratchpad's `cycle2a/` directory, where
`probe.py`, `clocked_probe.py`, `omx_probe.py` and their `pyproject.toml`
are; `probe.py` and `clocked_probe.py` run from `<scratch>`, `omx_probe.py`
from `<OMX>`. One test run of ours at a time (they share `tests/_build`).
Every test marked RED in section 2 is run and seen red, for the reason it
names, before the code that turns it green. Record every command and its
result in `evidence.md` as you go, in the shape of
`openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check (`python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench).
- [ ] 1.2 Run `tests/test_joints.py tests/test_mates.py
  tests/test_couplings.py tests/test_clocked_bounds.py
  tests/test_running_reads.py tests/test_mate_existing_joint.py` with
  `pytest -q -p no:cacheprovider`; record counts and wall time (Stage P:
  603 passed, 954 subtests passed, 11.21 s).
- [ ] 1.3 Run `<scratch>/probe.py`, `<scratch>/clocked_probe.py` and
  `<scratch>/omx_probe.py`; record their output and copy the three
  probes' sources into `evidence.md` (the scratchpad is not durable).
  Expect design.md's Context tables.
- [ ] 1.4 Run, each alone, recording counts and wall time:
  `python -m pytest -q -p no:cacheprovider simulation/test_frames.py`
  and `machinome test --mesh simulation/open_manipulator_x.py:OpenManipulatorX`
  in `<OMX>` (Stage P: 11 passed; 4 passed), and `python -m pytest -q -p
  no:cacheprovider simulation/test_frames.py` in `<OpenArm>` (Stage P: 10
  passed). `git -C <OMX> status --short` and `git -C <OpenArm> status
  --short` before and after: no change to either project.

## 2. Red tests

- [ ] 2.1 RED `tests/test_joints.py`, beside `AxislessRevoluteTest` (a new
  class `AxislessKindTest`), the joints scenario "A joint of another kind
  written without an axis is refused naming its kind":
  - a class body `slide = Prismatic(axis=None, unit='mm')` on `Loose`
    raises `TypeError` containing `Loose.slide`, `Prismatic`, `required
    everywhere` and `a mate's freedom included`, and not `is a Revolute`;
  - a parent `Rail` declaring `car = Slider(travel=Prismatic(axis=None))`
    raises `TypeError` containing `Rail`, `Slider`, `travel`, `Prismatic`
    and `required everywhere`, and not `is a Revolute`;
  - a class body `orbit = Orbit(axis=None, carries=(0, 0, 1))` raises
    `TypeError` containing `an Orbit` and `required everywhere`, and not
    `is a Revolute` nor `a mate's freedom included`.
  Red today: each reads "is a Revolute without an axis"; the site one
  names `Slider.travel`, not `Rail`.
- [ ] 2.2 RED `tests/test_mates.py` (`SlidingMateTest`), same scenario,
  the mate's freedom: a palm `Palm` declaring
  `grip = finger.origin.on(seat, Prismatic(axis=None, range=(-11, 20), unit='mm'))`
  raises `TypeError` containing `Palm.grip`, `the mate's freedom`,
  `Prismatic` and `required everywhere`, and not `is a Revolute` nor
  `Finger.grip`. Red today: `Finger.grip is a Revolute without an axis`.
- [ ] 2.3 RED `tests/test_mates.py` (`SlidingMateTest`), the joints
  scenario "A range refusal on a mate's joint names the mate": with
  `slide_fixtures().Gripper` bound to `grip=25` (through the class's
  existing `posed`), the `JointRangeError` message starts with
  `wrist.palm: mate 'left_grip' declares the range -11 to 20 mm` and does
  not contain `left_finger`; with `slide_fixtures().Palm()` alone,
  `palm.left_grip = 25; palm.render()` raises a message starting with
  `Palm (Palm): mate 'left_grip'` (a root is named by its name, `'Palm'`,
  and class, measured). Red today: `wrist.palm.left_finger: joint
  'left_grip' ...` and `left_finger: joint 'left_grip' ...`.
- [ ] 2.4 RED `tests/test_mates.py` (`SlidingMateTest`), the enumeration's
  close: `<scratch>/probe.py`'s `HeldGate` — a root with drivers `gate`
  and `push` holding `palm = PortGatedPalm()`, whose port `gate` the
  freedom `Prismatic(axis=(1, 0, 0), unit='mm', range=(0, Bound(lambda
  own, gate: gate, reads=(gate,))))` reads, `gate.drives(palm.gate)`,
  `push.drives(palm.grip)` — bound to `gate=3, push=5`: the message
  contains `palm: mate 'grip' -- the coordinate palm.grip --` and `0 to
  3 mm`, and not `finger`. Red today (measured): `palm.finger: joint
  'grip' -- the coordinate palm.finger.grip -- declares the range 0 to 3
  mm, and 5 is outside it. ...`.
- [ ] 2.5 RED `tests/test_clocked_bounds.py` (`RefusalTest`), the clocked
  commit: `<scratch>/clocked_probe.py`'s `MatedShut` (defined in the test
  module, importing `hundredth`, `reaches`, `shuts` from
  `tests/clocked_project/gate.py`), `Sim(MatedShut(), record=8).move('crank',
  by=400.0)` raises `JointRangeError` containing `mate 'travel' -- the
  coordinate 'shutter.travel' --`, `high bound of 0.0` and `committed
  nothing`, and not `shutter: joint`. Red today: `shutter: joint 'travel'
  -- the coordinate 'shutter.travel' -- ...`. The existing
  `test_a_commit_out_of_range_refuses_the_request_by_name` (a site joint,
  `"joint 'travel'"`) is the guard and stays green unedited.
- [ ] 2.6 RED `tests/test_couplings.py` (`SelfReadTest`), the couplings
  scenario "A relation whose one source is its own driven end is refused":
  each of `wheel.turn.drives(wheel.turn)`, the same with a `law=`,
  `turn.drives(turn)` on a port the class declares,
  `wheel.drives(wheel.turn)` (the node standing for its one joint), and
  `mount = body.axle.on(seat, body.turn)` with `mount.drives(body.turn)`,
  raises `TypeError` AT CLASS DEFINITION, its message containing the
  relation as written (`wheel.turn drives wheel.turn`, `wheel drives
  wheel.turn`, `mount drives body.turn`, ...), `one source` and `its own
  driven end`, and `.drives(` with `& ` (the group form it points to).
  Red today: every class is created.
- [ ] 2.7 GUARD `tests/test_couplings.py` (`SelfReadTest`): `crank.drives(crank)`
  on a `Driver` still raises the driver refusal (`cannot be the driven
  end`), `wheels.turn.drives(wheels.turn)` over a repeat still raises the
  repeat refusal (`cannot be the SOURCE`), and
  `(rack & wheel.turn).drives(wheel.turn, law=...)` is still accepted as
  a read. Green before and after.
- [ ] 2.8 Run 2.1-2.7 on the unmodified tree; record 2.7 green and the
  failure lines of 2.1-2.6.

## 3. The change

- [ ] 3.1 `machinome/motion/joints.py`: `axisless_refusal(kind, where)`
  (design.md, Decision 1), the `Revolute` text unchanged; `Joint.__set_name__`
  builds `where` from `installed_by` when set. `machinome/node/declarative.py`:
  the site check covers `Revolute`, `Prismatic` and `Orbit`, calling
  `axisless_refusal(type(value).__name__, where)`. Run 2.1, 2.2 and
  `AxislessRevoluteTest`: green.
- [ ] 3.2 `machinome/motion/joints.py`: `_binding_site(node, joint)` beside
  `_where` (design.md, Decision 2), with a docstring naming this change;
  `_refuse_out_of_range`'s two messages and `_bound_at`'s two take their
  head from it. Run 2.3: green.
- [ ] 3.3 `machinome/motion/couplings.py`: `refuse_bounds`'s two messages
  and `_bound_side`'s one take their head from `_binding_site`. Run 2.4:
  green.
- [ ] 3.4 `machinome/simulation/clocked.py`: `_constrained`'s `refuse` and
  `_commit_out_of_range` take their head from `_binding_site`, the bank
  id quoted as today. Run 2.5: green.
- [ ] 3.5 `machinome/motion/couplings.py`: `_names_one_coordinate` beside
  `_self_read_index`, and the refusal in `relate` after the end checks
  for a relation naming one coordinate at each end (design.md, Decision
  3). Run 2.6 and 2.7: green. If a spelling of 2.6 is not caught by the
  comparison, stop and record it rather than widen the comparison.
- [ ] 3.6 `grep -n "_where(node)}: joint '\|_where(bounded.node)}: joint '"
  machinome/` lists no range refusal that can judge a mate's joint
  (the site-only placement refusal at `joints.py:812`, the `Orbit` one at
  `:1092` and `declarer_of`'s two may remain); record the grep.
- [ ] 3.7 Run the focused set of 1.2 again; record counts. Every existing
  test passes unedited.

## 4. Framework validation

- [ ] 4.1 `black --check` and `flake8 --max-line-length=89` on every
  touched Python file.
- [ ] 4.2 Run `<scratch>/probe.py` and `<scratch>/clocked_probe.py` again;
  record each changed message, and that every control row reads as
  before.
- [ ] 4.3 Run the full suite (`pytest` at the bench root, alone); record
  counts and wall time.

## 5. Validation in OpenMANIPULATOR-X and OpenArm (read only)

- [ ] 5.1 Run `<scratch>/omx_probe.py` from `<OMX>`; record the four
  messages: `set_state(grip=21)` and `grip=-12` head
  `arm.link2.link3.link4.link5: mate 'left_travel' declares the range
  -11.0 to 20.0 mm`, and the two `Link5Assembly()` cases head with the
  palm and `mate 'left_travel'`.
- [ ] 5.2 Run the three commands of 1.4 again, each alone; record counts
  and wall time beside 1.4's. `git -C <OMX> status --short` and `git -C
  <OpenArm> status --short`: no change to either project.

## 6. Words

- [ ] 6.1 `grep -rn "without an axis\|declares the range\|nothing bound either end" docs/ --include=*.rst --include=*.md`
  outside `docs/adrs/`; read each hit: none is made wrong (design.md,
  Decision 6). Change nothing unless one is.
- [ ] 6.2 `docs/project/changelog.rst`: one bullet under the existing
  `Unreleased` section naming `name-what-is-refused` (design.md, Decision
  6). Run `tests/test_release_records.py`.

## 7. Findings record

- [ ] 7.1 Move, verbatim, from `workflow/warts.md` to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under one heading
  naming `name-what-is-refused`, with a "What shipped" paragraph for
  each, and delete them from `warts.md`:
  "The axis-less refusal names a `Revolute` for any kind." (section
  "Findings from the framework cycle `slide-by-mate` (2026-09-26)" — the
  section heading goes too if it is left empty);
  "`JointRangeError` names the child's installed joint, not the mate's
  coordinate." (section "Findings from the OpenMANIPULATOR-X project's
  migration onto mates (2026-09-26)", whose other entries stay);
  "`a.drives(a)`, one to one, still deadlocks into `UnreachedCoordinate`
  instead of naming itself." (section "read-the-driven-coordinate
  (2026-09-15, found while fixing)", whose other entries stay).
- [ ] 7.2 Add to `warts.md` one entry recording design.md's Open
  Questions 1 and 2: the several-ends check does not expand an inferred
  node, and the constraint-intersection refusals name the bank id for a
  mate's coordinate; reached by no known project. **Recorded.**
- [ ] 7.3 Update `workflow/ongoing/fix-warts-3.md`'s "Progress" with one
  line for this cycle.

## 8. Sync and archive

- [ ] 8.1 Sync the three MODIFIED requirements into
  `openspec/specs/joints/spec.md` and `openspec/specs/couplings/spec.md`
  (`openspec archive name-what-is-refused --yes`, or by hand and then
  `--skip-specs`); check every carried scenario is present once.
- [ ] 8.2 `openspec validate --specs` passes after the archive, and the
  archived folder is
  `openspec/changes/archive/2026-10-06-name-what-is-refused/`.
- [ ] 8.3 Run the focused set of 1.2 once more; record. Leave everything
  uncommitted and report.
