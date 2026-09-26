Every command runs from the worktree
`/home/asa/devel/machinome/machinome/WTs/state-the-mate-line` with
`PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
Never run two test suites at once (they share `tests/_build`). Tests
follow `tests/test_mates.py`'s style: `BaseNodeTest` classes, one
behaviour per test, fixtures in `tests/mate_project/`. Every test in
section 2 is run and seen RED, for the reason it names, before the code
that turns it green; record each red run in `evidence.md`.

## 0. Opening evidence

- [ ] 0.1 Confirm `python -c "import machinome; print(machinome.__file__)"`
  prints this worktree's path, and record the base commit (`d791eaa`).
- [ ] 0.2 Run the full suite at the base and record the counts in
  `evidence.md`.
- [ ] 0.3 Record the pilot's answers to the three scope questions in
  `proposal.md`. If any differs from the recommendation, STOP and update
  the planning artifacts before writing a test.
- [ ] 0.4 Before any code change, capture the published documents of two
  mated fixtures whose freedoms state no line — `MatedElbowMachine` and
  a root over `MatedHousing` (add the root to `tests/mate_project/` if
  none exists; a fixture file added here is not implementation) — with
  `test_mates.published` and `json.dumps(..., indent=2) + '\n'`, into
  `evidence/base_documents/` and the same bytes into
  `tests/base_documents/`; record `cmp` of the two copies.

## 1. Planning record

- [ ] 1.1 `openspec validate state-the-mate-line --strict` passes; the
  planning commit holds the change folder and its `evidence/`, nothing
  else. No ADR here (task 4.4).

## 2. Red first (`tests/test_mates.py`, fixtures in `tests/mate_project/`)

Fixtures, all with numbers from `evidence/finding.md` §3 and each beside
a HAND-PLACED TWIN — an assembly whose `render()` writes the same rest
placement and whose child class declares the hand-written joint:

- *verbatim shoulder*: `shoulder_pin = Frame(at=(0, 0, 123))`; child
  `bore = Frame(at=(0, 0, 68), z=(0, 1, 0), x=(-1, 0, 0))`;
  `Revolute(axis=(0, 0, 1), at=(0, 0, 0), unit='deg')`. Twin:
  `rotate(180, (0, √½, √½))`, `translate(0, -68, 123)`,
  `Revolute(axis=(0, 0, 1))`.
- *verbatim wrist*: `wrist_pin = Frame(at=(0, 0, 111.5))`; child
  `bore = Frame(x=(0, -1, 0))`; `Revolute(axis=(1, 0, 0))`. Twin:
  `rotate(90, (0, 0, 1))`, `translate(0, 0, 111.5)`,
  `Revolute(axis=(1, 0, 0))`.
- *reversed yaw*: `yaw_pin = Frame(at=(0, 0, -1))`; child
  `bore = Frame(z=(0, 0, -1))`; `Revolute(axis=(0, 0, 1))`. Twin:
  `rotate(180, (0, 1, 0))`, `translate(0, 0, -1)`,
  `Revolute(axis=(0, 0, 1))`.

- [ ] 2.1 **The refusal is gone.** Replace
  `RefusalTest.test_a_freedom_does_not_restate_the_line` by
  `test_a_freedom_may_state_its_line`: `Revolute(axis=(0, 0, 1))`,
  `Revolute(at=(0, 0, 0))` and both together create the class and
  report the mate. Red at the base with the restatement refusal.
- [ ] 2.2 **A stated line is numbers.** Refused at class creation, naming
  the class, the mate and the argument (`axis` or `at`): an `at` holding
  an assembly `Length` token; an `at` holding a formula over one; an
  `axis` that is a callable; an `axis` of two components; an `axis` with
  a `bool` component. Each message says the line is written in the
  assembly and read in the moving child's frame. Red at the base (the
  restatement refusal fires instead, without the argument's reason —
  assert the reason's fragment).
- [ ] 2.3 **A stated axis has a direction.** `Revolute(axis=(0, 0, 0))`
  refused at class creation naming the class, the mate and `axis`, and
  saying an axis of zero length states no line (assert that fragment:
  at the base the restatement refusal also names `axis`, so only the
  reason makes the test red).
- [ ] 2.4 **The joint turns about the stated line.** Verbatim shoulder:
  `declared_joints` of the child's realized class reports `shoulder`
  with resolved axis `(0, 0, 1)` and anchor `(0.0, 0.0, 0.0)`; bound at
  30 its operations are `['r', '30', [0, 0, 1]]` then the rest rotation
  and translation, with NO centring translation.
- [ ] 2.5 **The anchor pair.** `MatedHousing`'s on-line bore
  (`at=(0, 0, 68)`, `z=(0, 0, 1)`) mated once with `Revolute()` and once
  with `Revolute(at=(0, 0, 0))`, each bound at 30: the first carries the
  centring pair `∓(0, 0, 68)` (today's behaviour, a green guard), the
  second the turn alone; the two composed child matrices agree within
  `1e-12`.
- [ ] 2.6 **Thor's across and reversed shapes reproduce their twins.**
  For the verbatim shoulder, the verbatim wrist and the reversed yaw, at
  bindings `-90, -30, 0, 30, 90` and unbound: the mated child's
  operations equal the twin child's in kind and order, rotations equal
  in angle and in axis within `1e-9`, translations within `1e-9`, and the
  composed world matrices of every leaf equal the twin's within `1e-9`
  (the capture tool's rounding: deviation 0). The shoulder's rest
  rotation is exactly `'180'` about `(0, √½, √½)` and its translation
  `(0, -68, 123)`; the wrist's is exactly `'90'` about `[0, 0, 1]`.
- [ ] 2.7 **The sign.** The reversed yaw with the stated axis turns `+30`
  about `(0, 0, 1)`; the same pair with `Revolute()` turns about
  `(0, 0, -1)` (today's behaviour, pinned so the difference is
  visible).
- [ ] 2.8 **Defaults unchanged.** For a freedom stating no line, the
  installed joint's declared `axis` and `at` are the moving frame's
  declared `z` and `at` (the same objects); every existing test in
  `tests/test_mates.py`, `tests/test_frames.py` and
  `tests/test_joints.py::AxislessRevoluteTest` stays green unedited
  (the axis-less refusal outside a mate is unchanged).
- [ ] 2.9 **Document.** The two fixtures of 0.4 export byte-identical to
  their captured base documents (green at the base; stays green). The
  verbatim-shoulder root exports the version an unmated machine declares,
  no new field, and its child's operations are those of the twin root
  within `1e-9`.

## 3. Implementation

- [ ] 3.1 `machinome/motion/mates.py`, `_check_freedom`: drop the
  restatement refusal; refuse a stated `axis` (not `None`) or a written
  `at` (`anchor_written`) that is not a sequence of three real numbers
  (not `str`/`bytes`, not a callable, no `bool`), and a stated `axis` of
  zero length (the joint's `1e-9` threshold), each naming class, mate
  and argument.
- [ ] 3.2 `_install`: `Revolute(axis=freedom.axis if freedom.axis is not
  None else frame.z, at=freedom.at if freedom.anchor_written else
  frame.at, range=freedom.range, unit=freedom.unit)`.
- [ ] 3.3 Docstrings and messages: `mates.py` module docstring and
  `_install`/`_check_freedom`; `joints.py` `_DefaultAnchor` (one purpose
  now: left out takes the frame's origin), `Revolute` (the axis may be
  left out only in a mate's freedom, where the moving frame supplies it
  by default), `axisless_refusal` wording (keep the fragments `axis` and
  `mate`); `frames.py` `Frame` ("`z` is the line a revolute mate turns
  about unless the mate's freedom states one").
- [ ] 3.4 Every test of section 2 green; the full suite green with the
  counts of 0.2 minus the replaced test plus the new ones, nothing
  skipped that was not skipped at the base. Record in `evidence.md`.

## 4. Documentation, records (the second commit)

- [ ] 4.1 `docs/concepts/joints.rst`, "Frames and mates", under
  `skills/write-the-manual`: the frame's `z` is the line BY DEFAULT; a
  freedom may state `axis` and `at` in the moving part's own frame,
  numbers only, each defaulting to the frame's; the frames fix the rest
  attitude and the zero, the freedom the line; `at=(0, 0, 0)` is the
  part's origin, not the frame's; the refusal list loses "states an
  `axis` or `at`" and gains the non-numeric and zero-length line. A
  second, runnable example (a connector whose `z` stands across the joint
  line) pinned by a `ManualTest` test that execs it and checks the
  installed joint's line.
- [ ] 4.2 `docs/project/changelog.rst`, Unreleased: the mate bullet says a
  freedom may state its own line in the moving part's frame.
- [ ] 4.3 Record for the studio (a separate change in
  `machinome-studio`, not made here): `shop-skills/machinome-api/SKILL.md`
  gains the stated line.
- [ ] 4.4 Write ADR-148 (NODE) as **Accepted** (design §7), add the
  *Amended by* line to ADR-147, both to `docs/adrs/README.md`'s index;
  amend `docs/architecture.md`'s mate paragraph ("the freedom a fresh
  `Revolute` with neither `axis` nor `at`" and "built from the moving
  frame's DECLARED `z` and `at`").
- [ ] 4.5 `workflow/ongoing/mates-and-sketches.md` §5.1–5.2: "`z` is the
  line a revolute turns about" becomes "by default"; "The freedom is a
  joint written with no `axis` and no `at`" gains the stated line in the
  moving child's own frame; mark it cut into this change.
- [ ] 4.6 `workflow/warts.md`: the first two bullets of the
  `place-parts-by-mate` findings gain their new disposition (fixed by
  `state-the-mate-line`, pending the Thor follow-up of §6).

## 5. Sync and archive

- [ ] 5.1 Sync the delta specs into `openspec/specs/` (`mates`,
  `joints`), `openspec validate --strict`, archive the change, final
  full suite, and commit the implementation record.

## 6. Originating project: Thor (later, by a separate agent, in Thor's own repository — NOT in this worktree)

- [ ] 6.1 On a branch of `projects/Robotic-Arms/Thor`, capture base poses
  of every model over Thor's instructions with the workspace's
  `docs/motion-general-refactor/capture_poses.py capture`, against the
  framework at this change's content commit.
- [ ] 6.2 `simulation/tools/emit_frames.py` emits each link's two
  connectors VERBATIM — the `AttachmentOffset` folded into the moving
  frame's triad, NO turn onto the joint line, no restated default-`x`
  choice — and the mate's freedom states the joint line in the link's
  own frame (the `axis` `ROOT_CHAIN` already carries) wherever the
  connector's `z` is not that line (shoulder, wrist, forearm yaw), and
  `at=(0, 0, 0)` where the hand-written joint had no centring pair (the
  shoulder). The emitter still checks every pair against the design's
  solve; `simulation/test_frames.py` checks the emitted frames and the
  freedoms' lines.
- [ ] 6.3 Paste the emitted frames and freedoms into `base.py`,
  `art1.py`…`art56.py`; nothing else in the modules changes.
- [ ] 6.4 `capture_poses.py compare` at its default tolerance: **maximum
  deviation 0** on every model and pose. Unrounded, the shoulder's
  `1.42e-14` mm residue is expected to vanish; record what is measured.
  A non-zero deviation stops the migration and is reported.
- [ ] 6.5 Thor's own tests unchanged in outcome (32 of 34, the two
  pre-existing seat-inventory failures); `Home` and `Park` snapshots
  compared against the base.
