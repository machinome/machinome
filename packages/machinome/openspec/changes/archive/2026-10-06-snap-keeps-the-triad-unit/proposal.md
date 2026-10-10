## Why

Originating project: `projects/Robotic-Arms/SO-ARM100` (branch
`frames-and-mates`), whose six URDF joints were migrated onto frames and
mates on 26 September 2026. Finding, `workflow/warts.md`, "Findings from
the SO-ARM100 project's migration onto mates (2026-09-26)":

> **A snapped triad component leaves the triad non-unit.** `frames.py`
> normalizes a declared direction and then snaps each component within
> `_SNAP = 1e-9` of 0, 1 or -1 onto that value, one component at a time
> and without renormalizing. A URDF rpy of `1.57079` gives
> `z = (0, -0.99999999998, 6.33e-6)`: the second component snaps to
> exactly `-1` while the third stays, and the resolved `z` has length
> `1 + 2e-11`; `3.14158` gives `1 + 8e-11`, on `z` and `x` both. Four of
> the SO-100's six fixed frames resolve so. [...] the documented read
> promises a unit triad, and the project's test had to compare resolved
> directions at 1e-9 rather than 1e-12. [...] the joint's own `_SNAP`
> shares the rule and should be checked with it. **Recorded.**
>
> **Remaining (2026-10-04):** `explicit-frame-direction-precision`
> (`fabfc3d`) no longer snaps a frame stated with both `x` and `z`; with
> `x` omitted, `frames.py` still snaps each component without
> renormalizing, and the joint's `_snapped` axis does too.

Reproduced on the bench `fix-warts-3` at `d9f5354` (design.md, Context,
has the table and the probe):

- **The SO-100 itself no longer reaches the defect.** Its four off-axis
  fixed frames state both `z` and `x`, so `fabfc3d` resolves them without
  a component snap; its moving frames are `Frame()`; its six joint axes are
  exact. Realized against the bench, every one of its twelve resolved
  frame directions and six joint axes is unit within `2.22e-16`, and every
  fixed frame's `x` and `z` equals the URDF's within `1.11e-16`. Its guard
  `simulation/test_frames.py` passes 9 of 9 and still carries `SNAP = 1e-9`
  with the comment "`-sin(1.57079)` is 2e-11 from -1", a tolerance the
  project may now tighten on its own.
- **The frame defect remains on the other snapped path, and it is
  `z` omitted, not `x` omitted.** With `x` omitted, a `z` a few millionths
  off an axis keeps two non-zero components after the snap and is refused
  for lacking `x`, as before; a `z` within the snap becomes exact integers.
  That path cannot produce a non-unit direction. With `z` omitted and `x`
  stated, it does: `Frame(x=(6.326794896668469e-06, -0.9999999999799858, 0))`
  (the `x` of `rpy="0 0 -1.57079"`) resolves `x = (6.33e-6, -1, 0)` and
  `y = (1, 6.33e-6, 0)`, each `1 + 2e-11` long; the `x` of `3.14158`
  gives `1 + 8.01e-11`.
- **The joint has the same defect.** `Revolute(axis=(0,
  -0.9999999999799858, 6.326794896668469e-06))` resolves to
  `(0, -1, 6.33e-6)`, `1 + 2e-11` long; `(1.27e-5, 0, -0.99999999992)`
  to `(1.27e-5, 0, -1)`, `1 + 8.01e-11`.
- **Since `fabfc3d`, a mate's line reads two ways.** A mate whose freedom
  states no axis hands the moving frame's declared `z` to the joint it
  installs. With the moving frame `Frame(z=(0, -0.9999999999799858,
  6.326794896668469e-06), x=(1, 0, 0))`, the frame reads the precise unit
  `z = (0.0, -0.9999999999799859, 6.33e-6)` and the joint turns about
  `(0, -1, 6.33e-6)`: unequal, and the joint's axis non-unit.

Both baseline specs contradict themselves on these inputs. `mates`, "A
frame resolves against its declarer at realization", promises "three unit
directions" and, on the snapped path, that "direction components within
`1e-9` of `0`, `1` or `-1` SHALL be that integer"; `joints`, "A joint is
stated in the frame of whoever declares it", promises to "normalize a
declared `axis` to unit length" and to "snap each component of the
normalized axis within `1e-9`". For a direction a few millionths off an
axis the two sentences cannot both hold. This change is that conformance
repair: the originating project's own frames were brought into conformance
by `fabfc3d`, and no project in the catalogue is known to declare the
inputs that remain (design.md, Context, records the scan).

## What Changes

- **A direction snaps as a whole.** After normalizing, a direction whose
  every component lies within `1e-9` of `0`, `1` or `-1` becomes exactly
  that principal axis, in integers, as today. Any other direction keeps
  its components as computed, except that a component within `1e-9` of
  `0` is still the integer `0`; no component of it is made `1` or `-1`.
  Every direction so resolved is unit to within `1e-12`.
- **Where it applies:** a joint's normalized declared axis (every joint
  kind, through `Joint.resolve`), and a frame's `z`, `x` and `y` on the
  snapped path (`z` omitted, or `x` omitted or `None`). A frame stating
  both directions keeps `fabfc3d`'s unsnapped precision, unchanged.
- **One rule in one place.** One private helper in
  `machinome/motion/joints.py`, beside `_SNAP` and `resolved_vector`, used
  by `Joint.resolve` and by `Frame.resolve`; `frames.py`'s own `_snapped`
  goes.
- **Words that change with it:** the `_SNAP` comments of both modules,
  `Joint.resolve`'s, `Frame`'s and `ResolvedFrame`'s docstrings,
  `docs/concepts/joints.rst`'s paragraph on a resolved frame's
  components, and `docs/architecture.md`'s two sentences (the frame
  paragraph's "the existing `1e-9` component snap remains ... final mate
  and Joint snaps are unchanged", and "The normalized axis is snapped to
  an exact 0/1/−1 within `1e-9`"); one changelog bullet under
  `Unreleased`.

**Deliberately out**, with the reason:

- the axes a SITE-declared joint carries into the child's rest frame
  (`Joint`'s carry in `joints.py`: inverse rest placement, then a
  per-component `_snapped`) and the axis of a mate's rest rotation
  (`mates._axis_angle` with `mates._snapped`). Both have the same shape
  of per-component snap; no project is known to reach either (the SO-100
  declares no site joint, and its rest rotations publish exact axes, at
  bench `d9f5354`: `[1, 0, 0]`, `[0, 1, 0]`, `[-1, 0, 0]`). They are
  recorded as a new `warts.md` entry for triage (tasks §7), not changed;
- `fabfc3d`'s precise path, the value of `_SNAP`, the zero-length and
  parallel refusals, the omitted-`x` principal inference, anchors and
  translations;
- the SO-ARM100 project: read and run, never changed. Its guard's `1e-9`
  is its own to tighten;
- the studio's API skill (`machinome-studio/shop-skills/machinome-api/
  SKILL.md`, the Frame paragraph, "There, components within 1e-9 of 0, 1
  or -1 become those integers ... Joint axis snapping remain unchanged")
  states the old rule. It is a companion edit in the studio repository,
  made by the orchestrator there, never in this framework cycle.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `mates`: "A frame resolves against its declarer at realization" — the
  snapped path's per-component sentence becomes the whole-direction rule,
  with every resolved direction unit to `1e-12`; one scenario added, every
  existing scenario carried. "A realized node reads its resolved frames" —
  its restatement of the per-component snap becomes a reference to the
  frame resolution rule and the unit promise; every scenario carried.
- `joints`: "A joint is stated in the frame of whoever declares it" — the
  axis paragraph's per-component snap becomes the whole-direction rule,
  with the normalized axis unit to `1e-12`; three scenarios added, every
  existing scenario carried.

## Impact

- Code: `machinome/motion/joints.py` (one helper, `Joint.resolve`, the
  `_SNAP` comment and docstring), `machinome/node/frames.py`
  (`Frame.resolve`, `_snapped` removed, the `_SNAP` comment, `Frame` and
  `ResolvedFrame` docstrings).
- Tests: `tests/test_frames.py`, `tests/test_joints.py`,
  `tests/test_mates.py`; the existing `tests/test_frame_precision*.py`
  pins stay green unchanged (design.md, Decision 4).
- Documents: a published joint axis changes only for an axis that is not
  within `1e-9` of a principal axis in every component but has a component
  within `1e-9` of `±1`: today that component is the integer, afterwards
  the float the normalization computed (`-0.9999999999799859`, or `1.0`
  for an off component below about `1.5e-8`). No project is known to
  declare one; the byte-identity corpus `tests/base_documents/` is hashed
  before and after.
- No ADR (design.md, Decision 5).

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is cycle 1 of that note's table. The direction itself — a
direction snaps to an axis only as a whole, one helper in `joints.py`
for the frame and the joint — is the one ratified for this same change on
27 September 2026 (planning commit `8d14014`, branch `fix-warts-2`, never
applied), before `fabfc3d` added the precise path; this proposal rewrites
it for the current tree and narrows it to what `fabfc3d` left.
