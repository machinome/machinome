## Why

OpenMANIPULATOR-X is a four-joint arm with a two-finger gripper,
reconstructed from its URDF, and the URDF states its two finger joints
exactly as it states its four revolutes -- parent, child, origin, axis in
the child's frame, limits -- except that they are `prismatic`
(`evidence/finding.md` §2). Its migration onto frames and mates, in
SO-ARM100's shape, can mate the four links and not the fingers: a mate's
freedom must be a `Revolute` (ADR-147, "because Thor exercised only
revolutes"), so the fingers would stay a `translate` in `render()` and a
class-body `Prismatic`, the migration split down the middle. ADR-147
deferred `Prismatic` freedoms until a project needed one; this is that
project.

This is the wart recorded in `workflow/warts.md`, "A gripper's fingers
cannot be mated: no prismatic freedom (2026-09-26, open_manipulator)",
bullet "A mate's freedom must be a `Revolute`". The originating project
is `projects/Robotic-Arms/open_manipulator`; its follow-up states all six
URDF joints as mates read verbatim from the URDF and deletes every hand
placement of a moving link (tasks §6).

## What Changes

- **A mate's freedom may be a `Prismatic`**, beside the `Revolute`:
  `finger.origin.on(seat, Prismatic(axis=(0, 1, 0), range=(-11, 20), unit='mm'))`.
- **By the `Revolute` freedom's rules, save the axis:** the frames alone
  fix the rest placement and so the zero of the coordinate; `axis` is
  three numbers of non-zero length or one function of the assembly
  (ADR-148, ADR-150), and is always stated, as a `Prismatic` anywhere
  must state it -- only a `Revolute` freedom may leave its axis out, the
  moving frame's `z` then supplying it; `at` is three
  numbers, left out taking the moving frame's origin, a written
  `(0, 0, 0)` being the child's own origin; `range` is a pair of numbers,
  `None` or functions of the coordinate's own value, or one function of
  the assembly; tokens, formulas, a `Bound` with reads and a function
  `at` stay refused with the same reasons.
- **What it compiles to:** the moving child gets a `Prismatic` of its
  class, installed as today's `Revolute` is, under the mate's name; the
  assembly gets a TRANSLATIONAL coordinate under the mate's name, in the
  freedom's unit (`'mm'` by default); the rest placement is unchanged.
- **`Prismatic` gains `Revolute`'s anchor default:** `at` left out is
  the shared default-anchor object, read by `anchor_written`; `axis`
  stays its first, required argument, so a `Prismatic` without an axis
  is still refused by its constructor, wherever it is written, and the
  mate adds no refusal of its own. A class-body or site `Prismatic` is
  unchanged in behaviour and bytes.
- **Refusals that stay:** `Orbit` and `Free` freedoms, the rigid mate,
  and every other mate refusal; the "not a `Revolute`" refusal becomes
  "neither a `Revolute` nor a `Prismatic`".
- **Unchanged:** the rest placement (`apply_mates`), relations (a
  relation between two mates' coordinates on one assembly already works,
  `evidence/finding.md` §6), the document (no field, no version move: a
  slide reaches it as the translation of the joint's ordinary
  operations), the serializer, the viewer, the mechanics package, every
  existing mate, which installs the same joint and publishes the same
  bytes.
- **Words that change with it:** the `mates` spec, the manual's "Frames
  and mates" (a fifth, sliding example), `docs/reference/api.rst`'s
  "Frames and mates" sentence, the changelog's Unreleased, the `Mate`,
  `mates`, `Prismatic` and `Revolute` docstrings and messages, ADR-147
  (amended by a new ADR-151 at archive), `docs/architecture.md`'s mate
  paragraph, the working note, the wart's disposition.

**Deliberately out**, with the reason:

- `Orbit` and `Free` freedoms: no project needs one (the working note
  already argues `Orbit` is not a mate freedom);
- the rigid mate, loops, deeper ends, repeated frames: open_manipulator's
  fixed parts are not mated in this cycle and need none;
- the viewer, controls on a mated part, the studio skill (a separate
  change in `machinome-studio`, recorded as a follow-up);
- a documented read of a mate's resolved line and range (OpenArm's
  recorded finding, awaiting triage), the double report of a mate's
  coordinate (ditto);
- the axis-less `Prismatic`: struck at ratification (scope question 4).

## Scope questions for the pilot

The artifacts are written to each recommendation.

1. **`at` on a `Prismatic` freedom.** *Recommendation: treat it as the
   `Revolute` freedom's -- accepted as three numbers, left out taking the
   moving frame's origin --* rather than refuse it (design decision 2).
   The slide's placement ignores its anchor, but the joint carries it and
   the control compiler publishes it as a `Slide` control's gesture
   origin (ADR-112), and a class-body `Prismatic` accepts it; refusing it
   would make the mate's freedom narrower than the joint it installs and
   add a kind-specific rule. open_manipulator writes no `at` either way.
2. **Functions of the assembly in a `Prismatic` freedom.**
   *Recommendation: admit them by ADR-150's rules unchanged* (decision
   4). open_manipulator states numbers; but ADR-150's machinery is
   kind-blind (it substitutes the results and runs the joint's own
   `resolve`), so admitting them costs no code, while refusing them for
   one kind would be a new branch and a new refusal to word.
3. **The ADR.** *Recommendation: a new ADR-151 (NODE), "a mate's freedom
   may be a `Prismatic`", amending ADR-147* (the freedom is a `Revolute`;
   the coordinate is a `RotationalPort`; `Prismatic` deferred) and
   extending ADR-148 and ADR-150 (their rules apply to the new kind
   unchanged), with an *Amended by* line on ADR-147, written after
   implementation confirms the design. A MODIFIED spec block alone would
   leave ADR-147's decision text contradicting the code.
4. **The axis-less `Prismatic`.** Struck at ratification: a `Prismatic`
   freedom states its axis; no project needs the other.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `mates`: a mate's freedom may be a `Revolute` or a `Prismatic`; a
  `Prismatic` freedom states its axis, follows the `Revolute` freedom's
  rules for its anchor, range and functions, gives the moving child a
  `Prismatic` joint and the assembly a translational coordinate in its
  unit, and publishes its slide as the joint's ordinary operations;
  `Orbit`, `Free` and the rigid mate stay refused.

## Impact

- `machinome/motion/joints.py`: `Prismatic`'s `at` defaults to
  `_DEFAULT_ANCHOR` and it gains `anchor_written`, one definition shared
  with `Revolute`; its `axis` stays required; docstrings of
  `_DefaultAnchor`, `Revolute`, `Prismatic`.
- `machinome/motion/mates.py`: `_check_freedom` admits a `Prismatic`;
  `Mate.__init__` gives the mate a coordinate of the freedom's port kind;
  `_install` installs a joint of the freedom's kind; the zero-length
  refusal's wording; module, `Mate`, `_check_freedom`, `_check_stated`
  and `_install` docstrings and messages.
- Tests: `tests/test_mates.py` (the narrowed "other freedoms" refusal, a
  new `SlidingMateTest` and its twin and document tests, the manual
  example), a new fixture module `tests/mate_project/slide.py`.
- Documentation: `docs/concepts/joints.rst` "Frames and mates",
  `docs/reference/api.rst` "Frames and mates", `docs/project/changelog.rst`
  (Unreleased), `docs/architecture.md`, new ADR-151, ADR-147's header,
  `docs/adrs/README.md`, `workflow/ongoing/mates-and-sketches.md`,
  `workflow/warts.md`.
- Studio (separate change in `machinome-studio`, not made here):
  `shop-skills/machinome-api/SKILL.md` gains the sliding freedom.
- Originating project: open_manipulator's migration, later, by a
  separate agent, in its own repository (tasks §6).

## Ratified scope

Ratified by the orchestrator on 2026-09-26:

1. **`at` on a `Prismatic` freedom:** accepted as the `Revolute`
   freedom's -- three numbers, left out taking the moving frame's origin,
   a written `(0, 0, 0)` the child's own; `Prismatic` gains the default
   anchor and `anchor_written` for it.
2. **Functions of the assembly in a `Prismatic` freedom:** admitted by
   ADR-150's rules unchanged, at no code.
3. **The ADR:** a new ADR-151 (NODE) amending ADR-147 and extending
   ADR-148 and ADR-150, save that a `Prismatic` freedom states its axis,
   written after implementation confirms the design.
4. **The axis-less `Prismatic`:** struck. A `Prismatic` freedom states
   its `axis`, three numbers or one function of the assembly, as a
   `Prismatic` anywhere must; its constructor keeps requiring `axis`,
   the `joints` spec is not modified, the site refusal and
   `axisless_refusal` are not widened, and `Revolute` stays the one
   joint that may leave its axis out, as a mate's freedom only
   (ADR-147).
