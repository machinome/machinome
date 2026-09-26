## Why

OpenArm is two mirrored seven-joint arms with a pinch gripper each, one
class per joint instantiated once per side, and its URDF states a
different axis (arm joints 1 and 6) and a different range (arm joints 1
and 2, both fingers) on each side. The project reads them per instance,
`Revolute(axis=lambda node: ..., range=lambda node: ...)` over a `left`
flag, as its ADR-097 migration settled: handedness is a fact of the
realized node, not of the class (`evidence/finding.md` §2-3). Its
migration onto frames and mates finds the frame side served (a frame
takes a function of its declarer) and the freedom side refused:
`_check_stated` refuses a function `axis` and ADR-147 a function `range`,
because the installed joint would call them with the moving child while
they are written in the assembly. Without a change the only migration
splits the whole chain by side, sixteen stating classes and two grippers
for eight and one (§5), and gives up the per-instance handedness.
ADR-148 foresaw exactly this: "one that does gets a resolver-side
resolution then, together with the range."

This is the wart recorded in `workflow/warts.md`, "A handed design cannot
state its mates per instance (2026-09-26, openarm)", first bullet. The
originating project is `projects/Robotic-Arms/openarm`; its follow-up
states every joint as a mate whose fixed frame, axis and range are
functions of the side, and deletes the hand placements (tasks §6).

## What Changes

- **A mate's freedom may state its `axis` and its `range` as one
  function of one argument each**, beside the numbers they take today.
- **The function is called with the realized ASSEMBLY that states the
  mate** -- the node whose class body it is written in, the node a
  function given to that assembly's own frame is called with -- never
  with the moving child. It is called once per realized assembly, when
  that assembly realizes the moving child (ADR-098's moment for a
  site-declared joint's function), and never again.
- **Its result is taken as the numbers are.** An `axis` must be three
  real numbers of non-zero length, read in the moving child's own frame;
  a `range` must be a pair whose bounds are numbers, `None` or functions
  of the coordinate's own value. A result that is not is refused at
  realization, naming the assembly, the mate and the argument. The joint
  the mate installs then resolves, normalizes and refuses the result
  exactly as it does the numbers.
- **Removed refusals:** a function `axis`; a function `range` (the whole
  range).
- **Kept refusals, reasons unchanged:** a parameter token or formula in
  a stated line or a range (they resolve BY NAME against the node the
  installed joint resolves on, ADR-148); a `Bound` with reads; a
  function `at` (see "Deliberately out").
- **Unchanged:** the rest placement (the frames alone fix it); every
  mate whose freedom states numbers or nothing, which installs the same
  joint on the same path, refuses with the same messages and publishes
  the same bytes; the document (no field, no version move; the line
  reaches it only as the axis of the joint's ordinary operations); the
  serializer, the viewer, the mechanics package.
- **Reads:** `declared_mates(cls)[name].freedom.axis` and `.range` read
  the function as written. No new read of the resolved values.
- **Words that change with it:** the `mates` spec, the manual's "Frames
  and mates" (a handed example), the changelog's Unreleased mate bullet,
  the `Mate` and `mates` module docstrings and refusal messages,
  ADR-147 and ADR-148 (both amended by a new ADR-150 at archive),
  `docs/architecture.md`'s mate paragraph, the working note's "Range and
  `Bound`" item, the wart's disposition.

**Deliberately out**, with the reason:

- a function `at`: OpenArm's every joint turns about the child's own
  origin, which is the moving `Frame()`'s origin, the default a freedom
  leaving `at` out already takes (`evidence/finding.md` §3);
- tokens and formulas in the freedom: no project needs one; they would
  still resolve against the child by name;
- a documented read of a joint's resolved axis or range on an instance
  (no OpenArm test reads one, §8), a function `unit`;
- `Prismatic` freedoms (open_manipulator's cycle), the rigid mate
  (OpenArm's mounts stay `translate`), relations, the frame side
  (already served).

## Scope questions for the pilot

The artifacts are written to each recommendation.

1. **Which node the function receives.** *Recommendation: the assembly
   that states the mate* (design decision 1). Every function the
   framework calls today receives the realized node whose class body
   wrote it -- a frame's its declarer, a class joint's its declarer, a
   site joint's the declaring parent (ADR-098) -- and a function written
   in the assembly and called with the child is the hazard ADR-148
   refused tokens for. OpenArm passes `left` to every node, so either
   serves it; the fixtures discriminate.
2. **`at` stays numbers.** *Recommendation: strike the function `at`*;
   OpenArm needs none, and admitting it later is one condition at the
   same seam. The line then reads "axis may be a function, at may not",
   which the refusal explains.
3. **No resolved read.** *Recommendation: add none*; the class reads
   return the function, and the spec says the per-instance values are not
   a documented read in this version.
4. **The ADR.** *Recommendation: a new ADR-150 (NODE) amending ADR-147
   (the range rule) and ADR-148 (the numbers-only line)*, with *Amended
   by* lines on both, written after implementation confirms the design.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `mates`: a freedom's `axis` and `range` may each be a function of the
  assembly that states the mate, called once when the assembly realizes
  the moving child, its result checked and resolved as the numbers are;
  the refusals of a function `axis` and a function `range` go; a
  function `at`, tokens and formulas stay refused; the class reads
  return the function.

## Impact

- `machinome/motion/mates.py`: `_check_freedom` and `_check_stated`
  (admit a function `axis` and `range`; keep refusing a function `at`,
  tokens, formulas), `_install` (mark a joint whose freedom states a
  function), a realization-time resolution against the assembly and its
  result check, docstrings and messages.
- `machinome/node/declarative.py`: `ChildDeclaration.realize` calls the
  mate resolution beside `_resolve_site_joints`.
- `machinome/motion/joints.py`: `resolve_declared_joints` skips a joint
  resolved at the child's realization, as it skips a site joint;
  `Joint.arguments`' lazy path refuses such a joint rather than resolve
  it against the child; docstrings.
- Tests: `tests/test_mates.py` (inverted refusals, new acceptance,
  realization refusals, discrimination, twins, document), a new fixture
  module `tests/mate_project/handed.py`.
- Documentation: `docs/concepts/joints.rst` "Frames and mates",
  `docs/project/changelog.rst` (Unreleased), `docs/architecture.md`, new
  ADR-150, headers of ADR-147 and ADR-148, `docs/adrs/README.md`,
  `workflow/ongoing/mates-and-sketches.md`, `workflow/warts.md`.
- Studio (separate change in `machinome-studio`, not made here):
  `shop-skills/machinome-api/SKILL.md` gains the handed freedom.
- Originating project: OpenArm's migration, later, by a separate agent,
  in its own repository (tasks §6).
