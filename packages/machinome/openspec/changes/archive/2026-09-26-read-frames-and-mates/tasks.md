Every command runs from the worktree
`/home/asa/devel/machinome/machinome/WTs/read-frames-and-mates` with
`PYTHONPATH="$PWD"` and `/home/asa/devel/machinome/.venv/bin/python`.
Never run two test suites at once (they share `tests/_build`). Tests
follow the style of `tests/test_frames.py` and `tests/test_mates.py`:
`BaseNodeTest` classes, one behaviour per test, NEW classes only — no
existing test, helper or fixture is edited (in particular
`tests/test_frames.py`'s private `resolved()` helper and
`tests/test_mates.py::ManualTest`'s index-addressed blocks stay as they
are). Every test in section 2 is run and seen RED, for the reason it
names, before the code or docstring that turns it green; record each red
run in `evidence.md`. Nothing in this change alters behaviour, so a red
test is red because `resolved_frames` does not exist yet, or because the
documentation does not yet say what the test reads.

## 0. Opening evidence

- [x] 0.1 Confirm `python -c "import machinome; print(machinome.__file__)"`
  prints this worktree's path, and record the base commit (`0b0eae5`) and
  the planning commit.
- [x] 0.2 Run the full suite at the planning commit
  (`python -m pytest -q -p no:cacheprovider -rs`) and record the counts
  and the skips in `evidence.md`.
- [x] 0.3 Record the pilot's answers to the three scope questions in
  `proposal.md`. If any differs from the recommendation, STOP and update
  the planning artifacts before writing a test.

## 1. Planning record

- [x] 1.1 `openspec validate read-frames-and-mates --strict` passes; the
  planning commit holds the change folder and its `evidence/`, nothing
  else. No ADR (design decision 8).

## 2. Red first

`tests/test_frames.py`, new classes (`ResolvedReadTest`,
`ResolvedReadRefusalTest`):

- [x] 2.1 **The numbers are read off the instance.** An assembly
  declaring `reach = Length(160)` and
  `elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))`, realized with
  `reach=150`: `resolved_frames(arm)` is a `dict` with keys
  `['elbow_pin']`; `at == (0.0, 150.0, 68.0)` with every component a
  `float`; `x == (1, 0, 0)`, `y == (0, 1, 0)`, `z == (0, 0, 1)`;
  `rotation()` is `[[1, 0, 0], [0, 1, 0], [0, 0, 1]]`; `declared_frames`
  of the class still holds the declaration whose `at` carries the token.
  Declaration order: a part declaring three frames reads them in that
  order. Red: `ImportError` on `resolved_frames`.
- [x] 2.2 **The default `x` on each principal `z`.** A part declaring six
  frames, `z` along `+X`, `-X`, `+Y`, `-Y`, `+Z`, `-Z` and no `x`: the
  read gives `x` `(0, 1, 0)`, `(0, -1, 0)`, `(0, 0, 1)`, `(0, 0, -1)`,
  `(1, 0, 0)`, `(-1, 0, 0)` respectively and `y == z × x` exactly, with
  `int` components; the expected values are WRITTEN in the test, never
  computed by a restated rule. A stated `x` squared up:
  `Frame(z=(0, 0, 2), x=(1, 0, 1))` reads `z (0, 0, 1)`, `x (1, 0, 0)`,
  `y (0, 1, 0)`; a non-principal `z` with a stated `x` reads
  `rotation()` whose columns are the read `x`, `y`, `z`.
- [x] 2.3 **The read is what the mate composes.** The upper arm of the
  spec scenario (`reach` token, a child `art3` whose class declares
  `hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))`, mate
  `elbow`; a new in-test class, or `MatedArm` if its numbers serve),
  realized with `reach=150` and rendered unbound: compute
  `R = fixed.rotation() · moving.rotation()ᵀ` and
  `t = fixed.at − R · moving.at` from `resolved_frames(arm)['elbow_pin']`
  and `resolved_frames(arm.art3)['hinge']`, and compare with the child's
  rest operations (rotation `'90'` about `[1, 0, 0]`, translation
  `(0, 231.5, 68)` within `1e-9`). Also: the objects the read returns are
  the ones `mates._placement` reads (`is`, one line, through
  `frames.RESOLVED_KEY` — a test may read the private cache to pin the
  identity; the public read may not depend on it). A mated child's read
  equals an unmated instance's of the same class.
- [x] 2.4 **A function is not called by the read.** A part declaring
  `bore = Frame(at=counting)`, `counting` returning `(0, 0, 7)` and
  counting its calls: after realization, record the count; two reads
  give `(0.0, 0.0, 7.0)` and leave the count unchanged.
- [x] 2.5 **A fresh mapping.** `del` a key from one read's result; a
  second read has every frame; a mate on that node, rendered after the
  deletion, rests exactly as before.
- [x] 2.6 **No frame, a dropped frame.** A leaf declaring no frame reads
  `{}`; `tests/test_frames.py`'s own inheritance shape (base `hinge` and
  `foot`, subclass `foot = None`) reads `['hinge']`.
- [x] 2.7 **Refusals** (`ResolvedReadRefusalTest`), each `TypeError`,
  asserting fragments: the class of 2.1 → names the class and
  `declared_frames`; the child `art3` of 2.3's upper arm read off its
  class (a child declaration) → names `ChildDeclaration` and "realized node"; a `Frame`
  and the number `3` → name their types; a part calling
  `resolved_frames(self)` in `check()` → realizing it raises, naming the
  class and "check()". Red: `ImportError` on `resolved_frames`.
- [x] 2.8 **Importing stays light.** The existing
  `DeclarationTest.test_importing_frames_adds_nothing_outside_the_framework`
  stays green unedited (the new function's import of `AbstractBaseNode`
  is inside it).

`tests/test_mates.py`, new classes (`MateReadTest`, and tests appended to
a NEW class beside `ManualTest`, e.g. `ManualReadTest`, reusing the
module's `_section` and `_code_blocks`):

- [x] 2.9 **The ends and freedom of a mate stating no line.** On
  `tests/mate_project/arm.py`'s `MatedArm`, read without constructing
  anything: `declared_mates(MatedArm)['elbow']` has `name == 'elbow'`,
  `moving.written == 'forearm.hinge'`, `fixed` is the class's own
  `elbow_pin` `Frame` (`is`, and `fixed.name == 'elbow_pin'`),
  `freedom.axis is None`, `freedom.anchor_written is False`,
  `freedom.range == (-135, 135)`, `freedom.unit == 'deg'`. A fixed end on
  a still child, `Pedestal.yaw`: `moving.written == 'housing.origin'`,
  `fixed.written == 'base.seat'`. These pass at the base (the attributes
  exist): they are GREEN GUARDS of the documented contract, recorded as
  such, not claimed red.
- [x] 2.10 **A stated line and a left-out anchor.**
  `tests/mate_project/line.py`'s `VerbatimShoulder.shoulder`:
  `axis == (0, 0, 1)`, `anchor_written is True`, `at == (0, 0, 0)`;
  `AnchoredHousing.shoulder`: `axis is None`, `anchor_written is True`;
  `VerbatimWrist.wrist`: `axis == (1, 0, 0)`, `anchor_written is False`.
  A new in-test assembly stating `Revolute(axis=(0, 0, 2))` on a part
  whose `hinge = Frame(at=(0, 0, 5))`: `axis == (0, 0, 2)` as written,
  `anchor_written is False`, and the installed joint's resolved anchor
  on a realized part is `(0.0, 0.0, 5.0)` — the moving frame's origin
  from `resolved_frames`, not `freedom.at`. Green guards, as 2.9, except
  the `resolved_frames` comparison, red on `ImportError`.
- [x] 2.11 **The mate's line from the documented reads alone.** For each
  mate of 2.9–2.10, on a realized assembly: the line composed by the
  rule of design decision 6 from `freedom` and `resolved_frames(child)`
  equals the installed
  joint's resolved `(axis, anchor)` after normalizing the axis. Red:
  `ImportError` on `resolved_frames`.
- [x] 2.12 **The reference lists the reads.** `docs/reference/api.rst`
  contains `machinome.node.frames.resolved_frames`,
  `machinome.node.frames.ResolvedFrame` (with `rotation`) and
  `machinome.motion.mates.Mate`; the docstrings of `ResolvedFrame`,
  `Mate`, `FrameRef.written`, `Frame.name` and `Revolute.anchor_written`
  contain the facts the spec states (fragments: "columns", "int",
  "'<child>.<frame>'", "anchor_written", "moving frame's origin"). Red:
  the entries and fragments are absent.
- [x] 2.13 **The manual example runs.** The THIRD
  `.. code-block:: python` of `docs/concepts/joints.rst`'s "Frames and
  mates" section (index 2; blocks 0 and 1 unchanged) runs — execed after
  block 0 in one namespace if it builds on `UpperArm`, stated in the
  test — and what it reads matches what the section's prose says
  (`(0.0, 150.0, 68.0)` appears in the section). Red: no third block.

## 3. Implementation

- [x] 3.1 `machinome/node/frames.py`: `resolved_frames(node)` —
  `isinstance(node, type)` → the class refusal; a local
  `from machinome.node.base import AbstractBaseNode` and
  `not isinstance(node, AbstractBaseNode)` → the not-a-node refusal;
  `declared = declared_frames(type(node))`, `cached =
  node.__dict__.get(RESOLVED_KEY, {})`; any name of `declared` missing
  from `cached` → the before-resolution refusal naming the class and the
  missing frames; else `{name: cached[name] for name in declared}`.
  Added to `__all__`. `_placement` is NOT rewritten onto it.
- [x] 3.2 Docstrings, no code: the `frames` module docstring (the read,
  and that an attribute read on an instance gives the declaration);
  `ResolvedFrame` (attributes, types, snapping, `rotation()` columns,
  read not assigned, not constructed by a project); `Frame` (`name`);
  `resolve_declared_frames` (the constructor's hook, not a read);
  `mates.FrameRef` (`written`); `mates.Mate` (`name`, `moving`, `fixed`,
  `freedom` and what each reads, read off the class because on an
  instance a mate reads its coordinate); `joints.Revolute.anchor_written`
  (when false, `at` is the default and a mate's anchor is the moving
  frame's origin).
- [x] 3.3 Every test of section 2 green; the full suite green with the
  counts of 0.2 plus the new tests, nothing skipped that was not skipped
  at the base, no existing test edited (`git diff --stat` on `tests/`
  shows only additions to `tests/test_frames.py` and
  `tests/test_mates.py`, and any new fixture file). Record in
  `evidence.md`.

## 4. Documentation, records (the second commit)

- [x] 4.1 `docs/concepts/joints.rst`, "Frames and mates", under
  `skills/write-the-manual`: after the refusal paragraph, a passage and
  the third code block (design decision 7): `resolved_frames` on a
  realized node, why an instance (a frame may read its parameters), the
  attribute read giving the declaration; `declared_mates(...)[name]` and
  its `name`, `moving.written`, `fixed` (the two forms), `freedom`
  (`axis`, `at` with `anchor_written`, `range`, `unit`), and the line
  rule in one sentence.
- [x] 4.2 `docs/reference/api.rst`, "Frames and mates": `.. autofunction::
  machinome.node.frames.resolved_frames`, `.. autoclass::
  machinome.node.frames.ResolvedFrame` with `:members: rotation`,
  `.. autoclass:: machinome.motion.mates.Mate`, after the existing three
  entries; the section's lead sentence names the read.
- [x] 4.3 `docs/project/changelog.rst`, Unreleased: one bullet — a
  realized node's frames read as numbers with `resolved_frames`, and a
  mate's name, ends and freedom documented reads off the class. The
  existing test that the Unreleased section names `Frame`, `.on(` and
  `Revolute` stays green.
- [x] 4.4 `docs/architecture.md`, the frame paragraph: after "cached as
  `_frame_arguments`", one clause — read publicly on the instance by
  `resolved_frames`, never off the class.
- [x] 4.5 `workflow/warts.md`: the sixth `place-parts-by-mate` bullet
  gains its disposition — fixed by `read-frames-and-mates`, pending the
  Thor follow-up of §7.
- [x] 4.6 Record for the studio (a separate change in `machinome-studio`,
  not made here): `shop-skills/machinome-api/SKILL.md` gains
  `resolved_frames` and the mate's documented reads.
- [x] 4.7 Sphinx builds the reference without a new warning for the new
  entries (`make -C docs html` or the docs test the suite already runs;
  record which).

## 5. Sync and archive

- [x] 5.1 Sync the delta spec into `openspec/specs/mates/spec.md`,
  `openspec validate --strict`, archive the change, final full suite, and
  commit the implementation record. No ADR to write or index.

## 6. Review probes (optional, before archive)

- [ ] 6.1 A scratch probe, recorded in `evidence/`, that realizes each
  test fixture declaring frames and asserts `resolved_frames(node)` equals
  `node.__dict__[RESOLVED_KEY]` key for key and object for object.

## 7. Originating project: Thor (later, by a separate agent, in Thor's own repository — NOT in this worktree)

- [ ] 7.1 On a branch of `projects/Robotic-Arms/Thor` off
  `state-the-mate-line`, against the framework at this change's content
  commit, capture base poses with the workspace's
  `docs/motion-general-refactor/capture_poses.py capture`.
- [ ] 7.2 Rewrite `simulation/test_frames.py` on the documented reads:
  `declared(...)` becomes `resolved_frames(<class>())[<frame>]` of each
  declaring class constructed once in `setUpClass`; the guard stops
  importing `default_x` and drops its own `unit` and `cross` where only
  the re-derivation used them; the assertion on `mate.described()`
  becomes assertions on `mate.moving.written` and on `mate.fixed.written`
  (a child's frame, `entry.fixed_on` set) or `mate.fixed.name` (the
  holder's own); `freedom.axis`, `.anchor_written`, `.at`, `.range`
  stay, now documented; the line test takes the moving frame from
  `resolved_frames`; `mate_placement` takes the two `ResolvedFrame`s as
  they are.
- [ ] 7.3 `simulation/tools/emit_frames.py`: `default_x` STAYS —
  `frame_literal` uses it to decide which emitted frames may leave `x`
  out, a question about what to write that no read answers
  (`evidence/finding.md` §5) — and its docstring says so; nothing else
  in the emitter changes. If Thor prefers to always write `x`, that is a
  separate Thor decision, not this follow-up.
- [ ] 7.4 No module of the model changes; Thor's suite unchanged in
  outcome (32 of 34, the two pre-existing seat-inventory failures, or
  whatever the base records) with `test_frames.py`'s tests all green; and
  `capture_poses.py compare` at its default tolerance: maximum deviation
  0 on every model and pose.
