Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Every framework command runs as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`;
every SO-ARM100 command as
`env -C <SO-ARM100> PYTHONPATH=<bench>:<SO-ARM100> /home/asa/devel/machinome/.venv/bin/<tool> ...`
with `<SO-ARM100>` = `/home/asa/devel/machinome/projects/Robotic-Arms/SO-ARM100`.
`<scratch>` is the campaign scratchpad's `cycle1/` directory, where
`probe.py`, `so100_probe.py` and their `pyproject.toml` are. One test run
of ours at a time (they share `tests/_build`). Every test marked RED in
section 2 is run and seen red, for the reason it names, before the code
that turns it green. Record every command and its result in `evidence.md`
as you go, in the shape of
`openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [x] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check (`python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench).
- [x] 1.2 Run `tests/test_frames.py tests/test_joints.py
  tests/test_mates.py tests/test_frame_precision.py
  tests/test_frame_precision_review.py tests/test_frame_precision_docs.py`
  with `pytest -q -p no:cacheprovider`; record counts and wall time
  (Stage P: 370 passed, 766 subtests passed).
- [x] 1.3 Record `sha256sum` of every file in `tests/base_documents/`.
- [x] 1.4 Run `<scratch>/probe.py` from the bench and
  `<scratch>/so100_probe.py <scratch>/so100-before.json` from SO-ARM100;
  record their output and copy both probes' sources into `evidence.md`
  (the scratchpad is not durable). Expect design.md's Context table and
  "12 frames, 6 joint axes, largest |length − 1| 2.22e-16".
- [x] 1.5 Run SO-ARM100's documented suites against the bench, each
  alone, recording counts and wall time: `python -m pytest
  simulation/test_frames.py`, then `machinome test --mesh
  simulation/parts.py`, `--mesh simulation/hardware.py`, `--mesh
  simulation/so_arm100.py`, `--brep simulation/parts.py`, `--brep
  simulation/hardware.py`, `--brep simulation/so_arm100.py` (its README's
  commands). `git -C <SO-ARM100> status --short` before and after: no
  change to the project.

## 2. Red tests

- [x] 2.1 GUARD `tests/test_joints.py` (`NumericHygieneTest`), the joints
  scenario "An axis within the snap of a principal axis resolves to exact
  integers": `axis=(0, 0, 3)` and `axis=(1e-12, 1, 0)` resolve to
  `(0, 0, 1)` and `(0, 1, 0)`, each component `type(c) is int`. Green
  before and after.
- [x] 2.2 RED `tests/test_joints.py` (`NumericHygieneTest`), "An axis a
  few millionths off a principal axis resolves unit":
  `axis=(0, -0.9999999999799858, 6.326794896668469e-06)` resolves to an
  axis of length `1` within `1e-12`, equal to the declared axis within
  `1e-15`, its first component the integer `0`, its second not the integer
  `-1`. Red today: length `1 + 2e-11`.
- [x] 2.3 RED `tests/test_mates.py` (`InstalledJointTest`), "A mate's
  joint turns about its moving frame's z a few millionths off an axis":
  a link class declaring
  `hinge = Frame(z=(0, -0.9999999999799858, 6.326794896668469e-06), x=(1, 0, 0))`,
  mated by `link.hinge.on(pin, Revolute())`; the installed joint's
  resolved axis (`declared_joints(type(stand.link))[<mate>].arguments(stand.link)[0]`)
  has length `1` within `1e-12` and equals
  `resolved_frames(stand.link)['hinge'].z` within `1e-15`, component for
  component. Red today: `(0, -1, 6.33e-6)` against
  `(0.0, -0.9999999999799859, 6.33e-6)`.
- [x] 2.4 RED `tests/test_frames.py` (`TriadTest`), the mates scenario "A
  frame with z omitted and x a few millionths off an axis reads a unit
  triad": `Frame(x=(6.326794896668469e-06, -0.9999999999799858, 0))` and
  `Frame(x=(-0.9999999999199434, 1.2653589793083688e-05, 0))`, read
  through `resolved_frames` of a realized holder, give `x`, `y`, `z` each
  of length `1` within `1e-12`, pairwise perpendicular within `1e-12`,
  `z == (0, 0, 1)` in integers, `x` equal to the declared `x` within
  `1e-15`, no component of `x` or `y` the integer `1` or `-1`, and the
  third component of `x` and of `y` the integer `0`. Red today: `x` and
  `y` `1 + 2e-11` and `1 + 8.01e-11` long.
- [x] 2.5 Run 2.1-2.4 on the unmodified tree; record 2.1 green and the
  failure lines of 2.2, 2.3 and 2.4.

## 3. The change

- [x] 3.1 `machinome/motion/joints.py`: add `_snapped_direction(components)`
  beside `_snapped` (design.md, Decisions 1 and 2), with a docstring
  stating the rule and naming this change; `Joint.resolve` uses it for
  the normalized axis. Run 2.1, 2.2, 2.3: 2.1 green, 2.2 green, 2.3
  green.
- [x] 3.2 `machinome/node/frames.py`: `Frame.resolve` applies one function
  per direction — identity on the precise path, `_snapped_direction`
  (imported from `machinome.motion.joints` with `resolved_vector`) on the
  snapped path — to `z`, to a stated `x` and to `y`; remove
  `frames._snapped`. Run 2.4: green.
- [x] 3.3 Words in code: the `_SNAP` comments of both modules,
  `Joint.resolve`'s docstring, `Frame`'s and `ResolvedFrame`'s docstrings
  state the whole-direction rule (keep the phrases
  `tests/test_frame_precision_docs.py` pins: `both`, `explicitly`,
  `omitted`, `snap`, `mate`, `joint`, `both directions explicitly`).
  `joints._snapped` stays, for the site-joint carry.
- [x] 3.4 Run the focused set of 1.2 again; record counts. Every existing
  test passes unedited, `tests/test_frame_precision*.py` included
  (design.md, Decision 4).

## 4. Framework validation

- [x] 4.1 `black --check` and `flake8 --max-line-length=89` on every
  touched Python file.
- [x] 4.2 Run `<scratch>/probe.py` again; record that every row of
  design.md's Context table now reads unit, the integer rows unchanged,
  and the mate's joint axis equal to the frame's `z`.
- [x] 4.3 Run the full suite (`pytest` at the bench root, alone); record
  counts and wall time. (Run here, it stalled at 82% on seven
  `tests/test_scad_presentation.py` tests whose `machinome build` of a
  fixture restarts without end, for a reason unrelated to this change;
  the complete run was made after section 8 with those seven deselected.
  `evidence.md`, §4.3, has the diagnosis.)
- [x] 4.4 Re-hash `tests/base_documents/` and compare with 1.3: identical.
  If a file differs, stop and record it; it is a document change design.md
  did not predict.

## 5. Validation in SO-ARM100 (read only)

- [x] 5.1 Run `<scratch>/so100_probe.py <scratch>/so100-after.json`;
  record its output (every frame direction and joint axis unit within
  `1e-12`, fixed frames equal to the URDF within `1e-12`) and compare the
  two records with
  `python -c "import json; a = json.load(open('<scratch>/so100-before.json')); b = json.load(open('<scratch>/so100-after.json')); print(a == b)"`:
  `True` — the frames, the joint axes and every link's operations in all
  five documented poses unchanged.
- [x] 5.2 Run the seven commands of 1.5 again, each alone; record counts
  and wall time beside 1.5's. `git -C <SO-ARM100> status --short`: no
  change to the project.

## 6. Words

- [x] 6.1 Read `/home/asa/devel/machinome/skills/write-the-manual/SKILL.md`.
  `docs/concepts/joints.rst`, the paragraph after the `resolved_frames`
  example: the sentence on omitted `x`/`x=None` and the closing sentence
  on final mate and joint snaps state the whole-direction rule (design.md,
  Decision 6). Change those sentences in place; add nothing else.
- [x] 6.2 `docs/architecture.md`: the frame paragraph's sentences on the
  `1e-9` component snap and on "final mate and Joint snaps are unchanged",
  and the joint paragraph's "The normalized axis is snapped to an exact
  0/1/−1 within `1e-9`", state the whole-direction rule.
- [x] 6.3 `docs/project/changelog.rst`: create `Unreleased` above
  `Machinome 0.8.0` and add one bullet naming `snap-keeps-the-triad-unit`
  (design.md, Decision 6). Run `tests/test_release_records.py`.
- [x] 6.4 `grep -rn "1e-9" docs/ machinome/node/frames.py
  machinome/motion/joints.py` and read each hit on a frame direction or a
  joint axis: none still states the per-component rule.

## 7. Findings record

- [x] 7.1 Move the entry "A snapped triad component leaves the triad
  non-unit." (with its **Remaining (2026-10-04)** note) verbatim from
  `workflow/warts.md` to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` (create the file
  if absent) under a heading naming `snap-keeps-the-triad-unit`, with a
  "What shipped" paragraph: `fabfc3d` closed it for frames stating both
  directions (the SO-100's four), this change for the snapped path
  (`z` omitted, `x` stated — the path the note called "`x` omitted") and
  for the joint's axis; and delete it from `warts.md`.
- [x] 7.2 Add to `warts.md`, in the same section, one entry recording the
  two per-component snaps this change left (design.md, Open Question 2):
  `Joint`'s site-declared carry and `mates._axis_angle`'s axis; the same
  shape of defect, reached by no known project, each a one-call change
  with `_snapped_direction`. **Recorded.**
- [x] 7.3 Update `workflow/ongoing/fix-warts-3.md`'s "Progress" with one
  line for this cycle.

## 8. Sync and archive

- [x] 8.1 Sync the three MODIFIED requirements into
  `openspec/specs/mates/spec.md` and `openspec/specs/joints/spec.md`
  (`openspec archive snap-keeps-the-triad-unit --yes`, or by hand and then
  `--skip-specs`); check every carried scenario is present once.
- [x] 8.2 `openspec validate --specs` passes after the archive, and the
  archived folder is `openspec/changes/archive/2026-10-06-snap-keeps-the-triad-unit/`.
- [x] 8.3 Run the focused set of 1.2 once more; record. Leave everything
  uncommitted and report.
