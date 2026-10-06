# Fix-warts 3: the entries it resolved

Each entry below left `../../warts.md` in the cycle that closed it, with its
text as it stood there and a paragraph saying what shipped. The campaign's
plan and progress are in `../../ongoing/fix-warts-3.md`; each cycle's
archived OpenSpec change is the authority for what it did.

## `snap-keeps-the-triad-unit`

From "Findings from the SO-ARM100 project's migration onto mates
(2026-09-26)":

- **A snapped triad component leaves the triad non-unit.** `frames.py`
  normalizes a declared direction and then snaps each component within
  `_SNAP = 1e-9` of 0, 1 or -1 onto that value, one component at a time
  and without renormalizing. A URDF rpy of `1.57079` gives
  `z = (0, -0.99999999998, 6.33e-6)`: the second component snaps to
  exactly `-1` while the third stays, and the resolved `z` has length
  `1 + 2e-11`; `3.14158` gives `1 + 8e-11`, on `z` and `x` both. Four of
  the SO-100's six fixed frames resolve so. No pose shows it (the mate's
  axis-angle extraction goes through `atan2`) and the placement is within
  1e-10, but the documented read promises a unit triad, and the project's
  test had to compare resolved directions at 1e-9 rather than 1e-12. The
  snap should keep the triad orthonormal: snap a component only when the
  snapped vector is still unit to `_SNAP` (the other components within
  the snap of 0), or renormalize after snapping. A small fix in
  `frames.py`; the joint's own `_SNAP` shares the rule and should be
  checked with it. **Recorded.**

  **Remaining (2026-10-04):** `explicit-frame-direction-precision`
  (`fabfc3d`) no longer snaps a frame stated with both `x` and `z`; with
  `x` omitted, `frames.py` still snaps each component without
  renormalizing, and the joint's `_snapped` axis does too.

**What shipped.** `explicit-frame-direction-precision` (`fabfc3d`) had
closed it for a frame stating both directions, which is how all four of
the SO-100's off-axis fixed frames are written. `snap-keeps-the-triad-unit`
(`openspec/changes/archive/2026-10-06-snap-keeps-the-triad-unit/`) closed
the rest: on a frame's snapped path, which a non-unit direction reaches
only with `z` omitted and `x` stated (the path the note above calls "`x`
omitted"; an omitted `x` needs `z` on a principal axis, which snaps to
exact integers), and on every joint's axis. One helper,
`machinome.motion.joints._snapped_direction`, now used by `Joint.resolve`
and `Frame.resolve` alike, snaps a direction to a principal axis only as a
whole: exactly that axis in integers when every component is within `1e-9`
of `0`, `1` or `-1`, otherwise only its components within `1e-9` of `0`
made `0`. Every resolved direction is unit to `1e-12`, and a mate stating no
axis turns its child about exactly the moving frame's resolved `z`. In the
SO-100, against the bench, every one of its twelve resolved frame
directions and six joint axes is unit within `2.22e-16`, and its frames,
joint axes and every link's operations in its five documented poses are
identical before and after the change. Its guard's `1e-9` tolerance is the
project's own to tighten. The two per-component snaps the change left, a
site-declared joint's carried axes and a mate's rest-rotation axis, are
recorded as a new entry in the same section of `../../warts.md`.
