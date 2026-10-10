## Why

A mate turns its child about the moving frame's `z`, through the moving
frame's origin, and refuses a freedom that states its own line. That
assumes a part's connector IS its joint frame. Thor's design says
otherwise: its FreeCAD Assembly4 connectors are ATTACHMENT frames, and
folded with their offsets their `z` lies on the joint line for two of
Thor's five root-chain links (base yaw, elbow), reversed for one
(forearm yaw) and across it for two (shoulder, wrist)
(`evidence/finding.md`, §3). To mate the three, Thor's frame emitter
(`projects/Robotic-Arms/Thor/simulation/tools/emit_frames.py`) turns both
frames of each pair about their shared origin until the moving `z` is the
joint line, and picks the attitude about it by restating the framework's
default-`x` rule — a choice the design does not make, in code whose only
purpose is to work around the mate. The same mechanism, seen from the
anchor, gave Thor's shoulder a centring pair its hand-written joint did
not have (the moving frame sits 68 up the joint line; `1.42e-14` mm in
composed poses).

These are the first two findings `place-parts-by-mate` recorded in
`workflow/warts.md` (2026-09-26), where the first was **Deferred** and the
second **Left as is**. This change reopens both (scope question 1) with
Thor as the originating project: its follow-up emits the design's
connectors verbatim, states each joint line in the link's own frame where
the connector's `z` is not that line, and deletes the turn.

## What Changes

- **A mate's freedom may state its own line.** `Revolute(axis=...,
  at=..., range=..., unit=...)` is accepted as a mate's freedom. A stated
  `axis` and a stated `at` are read in the MOVING CHILD's own rest frame
  — ADR-097's class-form rule, the frame the installed joint already
  resolves in, and the frame Thor's `ROOT_CHAIN` and its pre-mate joints
  state the line in.
- **Each defaults independently to today's behaviour.** No `axis` → the
  moving frame's `z`; no `at` → the moving frame's origin. The installed
  joint is `Revolute(axis=<stated or frame z>, at=<stated or frame at>,
  range, unit)`. An explicit `at=(0, 0, 0)` means the CHILD's origin, so
  `Revolute`'s left-out-anchor sentinel (`_DefaultAnchor`) stays, now to
  tell "left out, take the frame's" from "written".
- **The rest placement is untouched.** The frames remain the attachment,
  triad onto triad, and so still fix the rest attitude and the zero of
  the coordinate; the freedom fixes only the line. The frame's default-`x`
  rule and its diagonal-`z` refusal are untouched.
- **Removed refusal:** "a freedom that states its own `axis` or `at`".
- **New refusals, at class creation, naming the class, the mate and the
  argument:** a stated `axis` or `at` that is not three numbers (a
  parameter token, a formula or a callable — each would be resolved
  against the CHILD although written in the ASSEMBLY, the reason
  `place-parts-by-mate` design decision 5 restricts the freedom's range);
  a stated `axis` of zero length.
- **No check that a stated line passes through the frames' common
  origin.** An anchor is any point on its line, and the line is the
  freedom's own.
- **Untouched:** the document (no field, no version move; a machine whose
  mates state no line publishes the same bytes), the simulation package,
  the viewer, the mechanics package; `Revolute`'s axis-less refusal
  outside a mate; every other mate refusal.
- **Words that change with it:** the `mates` and `joints` specs, the
  manual's "Frames and mates" section, the changelog's Unreleased bullet,
  docstrings and refusal messages that say "the two frames supply the
  axis and the anchor", ADR-147 (amended by a new ADR-148 at archive),
  `docs/architecture.md`, and the working note §5.1–5.2 (second commit).

**Deliberately out**, with the reason: stating the line on the FRAME (the
line belongs to the joint; one connector may serve a revolute and, later,
a rigid mate — design decision 2); a line in the moving frame's own axes
or in the assembly's (design decision 1); tokens, formulas and callables
in a stated line (no project needs one; they would resolve against the
wrong node); `Prismatic`, `Free` and the rigid mate (unchanged deferrals);
a documented read of a declared frame's or mate's resolved numbers off
the class (Thor's third framework finding, not this one).

## Scope questions for the pilot

The artifacts are written to each recommendation.

1. **Reopening two provisional dispositions on one project's evidence.**
   The wart deferred the first finding until "a second design read through
   its connectors, or the rigid mate", and left the second as is.
   *Recommendation: reopen both now.* Thor needs it now and names what it
   does with it (the emitter loses its turn and its restated default-`x`
   rule; the five connectors become the design's own; the shoulder's
   centring residue goes); the change is one relaxed refusal plus one
   defaulting rule on a feature not yet released (it sits under the
   changelog's Unreleased heading), and it only widens what is accepted.
2. **A stated line is numbers only.** The briefing proposed the joint
   argument rule (tokens, formulas, a callable of the child). The source
   resolves a token BY NAME against the node the joint resolves on — the
   child — so an assembly's token would silently read a child parameter
   of the same name (`evidence/finding.md` §4). *Recommendation: numbers
   only, refused by name at class creation*, mirroring the range rule;
   Thor's lines are numbers.
3. **The ADR.** *Recommendation: a new ADR-148 (NODE) that amends ADR-147*
   ("the freedom is a fresh `Revolute` with neither axis nor anchor"),
   with an *Amended by* line on ADR-147, following the log's
   one-decision-per-ADR discipline. Written after implementation confirms
   the design, per the framework-change skill.

## Ratified scope (2026-09-26)

Ratified by the orchestrator's adversarial review under the review gate
the pilot delegated on 2026-09-07, on the pilot's instruction of
2026-09-26 to work the `place-parts-by-mate` findings with Thor as the
validator: both provisional dispositions reopened; a stated line is
numbers only; a new ADR-148 amends ADR-147.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `mates`: the freedom may state `axis` and `at` in the moving child's
  own frame, each defaulting to the moving frame's; the refusal of a
  stated line is replaced by the refusal of a non-numeric or zero-length
  one; the installed joint's line is the freedom's, else the frame's; a
  mate stating no line publishes the bytes it published before.
- `joints`: `Revolute` as a mate's freedom may state or leave out each of
  `axis` and `at` (one sentence of "Joint declarations").

## Impact

- `machinome/motion/mates.py`: `_check_freedom` (drop the restatement
  refusal, add the numbers and zero-length refusals), `_install` (stated
  line or the frame's), module and function docstrings.
- `machinome/motion/joints.py`: docstrings of `_DefaultAnchor` and
  `Revolute`, the wording of `axisless_refusal`. No behaviour change.
- `machinome/node/frames.py`: `Frame`'s docstring ("`z` is the line a
  revolute mate turns about" becomes "by default").
- Tests: `tests/test_mates.py` (the restatement test turns into
  acceptance tests; new refusal, line, anchor, fixture and document
  tests), fixtures in `tests/mate_project/`, a mated base document
  captured before implementation.
- Documentation: `docs/concepts/joints.rst` "Frames and mates",
  `docs/project/changelog.rst` (Unreleased), `docs/architecture.md`, new
  ADR-148, ADR-147's header, `docs/adrs/README.md` index,
  `workflow/ongoing/mates-and-sketches.md` §5.1–5.2, and the wart's
  disposition in `workflow/warts.md`.
- Studio (separate change in `machinome-studio`, not made here):
  `shop-skills/machinome-api/SKILL.md` gains the stated line.
- Originating project: Thor's follow-up, later, by a separate agent, in
  Thor's own repository (tasks §7).
