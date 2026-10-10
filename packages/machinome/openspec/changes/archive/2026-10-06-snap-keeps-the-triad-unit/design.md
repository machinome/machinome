## Context

### The two snaps as they are at `d9f5354`

`Joint.resolve` (`machinome/motion/joints.py`) normalizes a declared axis
and passes each component through `_snapped`: a component within
`_SNAP = 1e-9` of `0`, `1` or `-1` becomes that integer, one component at
a time. Every joint kind resolves its axis there (`Revolute`,
`Prismatic`, `Orbit`), and so does the joint a mate installs, which is an
ordinary `Revolute` or `Prismatic` on the moving child.

`Frame.resolve` (`machinome/node/frames.py`) has two paths since
`explicit-frame-direction-precision` (`fabfc3d`, 27 September 2026):

- **precise**, when the constructor was given both `z` and `x`
  (`_z_explicit and self.x is not None`): `z` normalized, `x` projected
  across it and normalized, `y = z × x`, no component snapped;
- **snapped**, otherwise (`z` omitted, or `x` omitted or `None`): the
  same arithmetic with every component of `z`, `x` and `y` passed through
  `frames._snapped`, a copy of the joint's per-component rule.

The rule was written so that `(0, 0, 2)` reads `(0, 0, 1)` and
`(1/3*3, 0, 0)` publishes `[1, 0, 0]`
(`tests/test_joints.py::NumericHygieneTest::test_residue_never_reaches_the_document`).
It is wrong for a direction a few millionths off an axis: a unit vector
with one component within `1e-9` of `±1` can have others as large as
`4.5e-5`, and snapping the `±1` alone leaves it `1 + (1 - |c|)` long.

### Which snapped-path frames can be non-unit

On the snapped path `z` is always an exact principal axis:

- `z` omitted is the default `(0, 0, 1)`, exact;
- `x` omitted needs `z` along a principal axis (`_principal_next`); a `z`
  a few millionths off one keeps two non-zero components after the snap
  and is refused for lacking `x`, and a `z` within `1e-9` of one in every
  component snaps to exact integers.

So the only non-unit snapped-path frame is one with `z` omitted and `x`
stated a few millionths off an axis; `x` is then exactly perpendicular to
the integer `z` (its `z` component is removed exactly) and `y = z × x` is
a signed permutation of `x`'s components, both non-unit by the same
amount. The warts note's "with `x` omitted" names the wrong path; the
reproduction below shows both.

### Reproduction at `d9f5354`

Probe: `probe.py` in the campaign scratchpad
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle1/`,
beside a one-line `pyproject.toml` that gives its nodes a project root),
run with the bench first on `PYTHONPATH` (`machinome.__file__` under the
bench), output `probe-base.txt`; the scratchpad is not durable, so
`evidence.md` carries the probes' sources (tasks §1.4). The red tests of
tasks §2 restate every row that matters. The numbers are the SO-100's
(`S = 0.9999999999799858`, `C = 6.326794896668469e-06` from `1.57079`;
`S2 = 0.9999999999199434`, `C2 = 1.2653589793083688e-05` from `3.14158`).

| Declared | Path | Resolved today | length − 1 |
|---|---|---|---|
| `Frame(z=(0, -S, C), x=(1, 0, 0))` | precise | `z = (0.0, -0.9999999999799859, 6.33e-6)` | `0` |
| `Frame(z=(0, -S, C))` | snapped | refused: `x` must be stated | — |
| `Frame(z=(0, 1e-12, 1))` | snapped | `(1,0,0)`, `(0,1,0)`, `(0,0,1)`, integers | `0` |
| `Frame(x=(C, -S, 0))` (rpy `0 0 -1.57079`) | snapped | `x = (6.33e-6, -1, 0)`, `y = (1, 6.33e-6, 0)` | `2e-11` |
| `Frame(x=(-S2, C2, 0))` | snapped | `x = (-1, 1.27e-5, 0)`, `y = (-1.27e-5, -1, 0)` | `8.01e-11` |
| `Frame(x=(1, 1e-12, 0))` | snapped | integers | `0` |
| `Frame(z=(0, 0, 1), x=(C, -S, 0))` | precise | floats, unsnapped | `0` |
| `Revolute(axis=(0, -S, C))` | joint | `(0, -1, 6.33e-6)` | `2e-11` |
| `Revolute(axis=(C2, 0, -S2))` | joint | `(1.27e-5, 0, -1)` | `8.01e-11` |
| `Revolute(axis=(0, 0, 3))`, `(1e-12, 1, 0)` | joint | `(0, 0, 1)`, `(0, 1, 0)`, integers | `0` |

A mate stating `Revolute()` onto a moving frame
`Frame(z=(0, -S, C), x=(1, 0, 0))` installs a joint whose resolved axis is
`(0, -1, 6.33e-6)` while the frame reads
`z = (0.0, -0.9999999999799859, 6.33e-6)`: unequal. Before `fabfc3d` the
two were equally wrong and equal; the precise path made them differ.

### The originating project at `d9f5354`

`so100_probe.py` (same scratchpad; output `so100-base.txt`, record
`so100-base.json`, written by the probe when given a path) realizes `SOArm100` from
`projects/Robotic-Arms/SO-ARM100` (branch `frames-and-mates`, `4438106`,
clean tree) against the bench. Its fixed frames all state `z` and `x`
(precise path); its moving frames are `Frame()`; its joint axes are stated
exactly (`(1, 0, 0)`, `(0, 1, 0)`) or are the moving frame's exact
`(0, 0, 1)`. Result: 12 frames and 6 joint axes, largest `|length − 1|`
`2.22e-16`, largest deviation of a fixed frame's `x` or `z` from the URDF
`1.11e-16`. Each link's operations in the five documented poses (`Rest`,
`Stand`, `Reach`, `Look`, `Grip`) are recorded in `so100-base.json`; the
rest rotations publish exact axes. `python -m pytest
simulation/test_frames.py`: 9 passed.

### Who else could reach it

A literal scan of the catalogue's Python sources (`projects/`, excluding
`_build`, `.git` and vendored tool trees) for direction literals near `±1`
(`0.99999999`) or a few millionths (`e-05` to `e-07`) finds them in
SO-ARM100's frames only (precise path) among frame and joint
declarations; `Frame(x=...)` with `z` omitted appears three times (Thor's
`art1.py` and `art56.py`, Leonardo's hydraulic sawmill), each an exact
axis. Axes computed at realization (a callable, a parameter formula) are
not covered by a literal scan; Open Question 1.

### Focused tests at `d9f5354`

`tests/test_frames.py tests/test_joints.py tests/test_mates.py
tests/test_frame_precision.py tests/test_frame_precision_review.py
tests/test_frame_precision_docs.py`: 370 passed, 766 subtests passed,
5.03 s.

## Goals / Non-Goals

**Goals:** every normalized declared joint axis and every resolved frame
direction unit to within `1e-12`; a direction within `1e-9` of a
principal axis in every component still resolves to that axis in exact
integers, since joints, mates and published documents rely on the exact
`[0, 1, 0]` form; one rule, stated once in code; a mate's joint turning
about the line its moving frame reads when that line is a few millionths
off an axis.

**Non-goals:** `fabfc3d`'s precise path; the site-joint carried axes and
the mate's axis-angle snap (Open Question 2); anchors, origins and
translations; the value of `_SNAP`; any change to SO-ARM100.

## Decisions

### 1. The rule: a direction snaps to ±1 only as a whole

After normalizing, a direction `d` resolves as follows:

- if every component of `d` is within `_SNAP` of `0`, `1` or `-1`, `d`
  is exactly that principal axis, in integers (a unit vector close to
  integers in every component has exactly one `±1`);
- otherwise each component within `_SNAP` of `0` is the integer `0`, and
  every other component is kept as computed.

Why not **renormalize after the per-component snap** (the finding's
second option):

- renormalizing undoes the snap it follows: `(0, -1, 6.33e-6)` divided by
  its length is `(0, -0.99999999998, 6.33e-6)` again, which a second pass
  would snap back; the rule would need a fixed point, or a snap known not
  to be undone, which is this rule;
- renormalizing an exactly axial snapped vector divides integers by the
  float `1.0` and hands back floats, losing the integer form documents
  carry, unless special-cased, which is again this rule;
- it moves every component by the snap's error, where this rule moves
  only components already `0` to within `1e-9`.

Why the zero snap is kept for a non-axial direction: it is what keeps a
residue of `1e-17` publishing as the integer `0`
(`test_residue_never_reaches_the_document`), and dropping a component of
at most `1e-9` changes the length by at most `5e-19`, below what a double
shows next to `1`.

Cases, with the numbers the rule predicts (`probe-base.txt`, "Prediction",
the rule restated in the probe):

- `(0, 0, 3)` → `(0, 0, 1)`; `(1e-12, 1, 0)` → `(0, 1, 0)`;
  `(1/3*3, 0, 0)` → `(1, 0, 0)`; `(3e-10, 0, 1)` → `(0, 0, 1)`: integers,
  as today;
- `(0.6, 0.8, 0)` → `(0.6, 0.8, 0)`; `(1, 1, 1)` → `0.577…` each: as
  today;
- `(0, -S, C)` → `(0, -0.9999999999799859, 6.33e-6)`, unit; equal to the
  precise frame's `z` for the same declaration (`0 == 0.0`), largest
  component difference `0`;
- `Frame(x=(C, -S, 0))` → `x = (6.33e-6, -0.9999999999799859, 0)`,
  `y = (0.9999999999799859, 6.33e-6, 0)`, `z = (0, 0, 1)`: each unit,
  pairwise exactly perpendicular;
- `(2e-9, 0, 1)` → `(2e-9, 0, 1.0)`: today `(2e-9, 0, 1)`. The value is
  the same and the length is unit either way; the `±1` component is now
  the float the normalization computed rather than the integer (Risks).

### 2. One helper, in `joints.py`, used by both

`_snapped_direction(components)`, taking an already normalized direction
as an iterable of three numbers and returning a tuple, lives in
`machinome/motion/joints.py` beside `_SNAP`, `_snapped` and
`resolved_vector` (which `Frame.resolve` already imports from there).

- `Joint.resolve`: `normalized = _snapped_direction(component / length
  for component in axis)`, replacing the per-component tuple.
- `Frame.resolve`: the per-component `component_value` becomes a
  per-direction function — identity on the precise path,
  `_snapped_direction` on the snapped path — applied to `z`, to `x` (when
  stated) and to `y = _cross(z, x)`. The omitted-`x` branch is untouched:
  `_principal_next` still reads a snapped `z`, which is exact integers
  whenever it is principal.
- `frames._snapped` is removed (nothing else reads it); `frames._SNAP`
  stays for the zero-length refusal.
- `joints._snapped` stays: the site-joint carry still uses it
  (Non-goals).

A frame restating the joint's rule is how the defect came to live in two
places; one helper keeps them one rule.

### 3. The joint's own snap is changed with the frame's

The finding asks for the joint to be checked with the frame. On this
tree it has to change for a reason of its own: since `fabfc3d` a mate
whose freedom states no axis installs a joint about its moving frame's
declared `z`, normalized by the joint's rule, while `resolved_frames`
reads the same `z` by the frame's. For a moving frame stating both
directions a few millionths off an axis the two disagree today (Context);
with the joint snapping as a whole they agree. The `joints` delta pins it
with the scenario "A mate's joint turns about its moving frame's z a few
millionths off an axis".

They do NOT agree for a moving frame stating both directions WITHIN the
snap of an axis: `Frame(z=(3e-10, 0, 1), x=(1, 0, 0))` keeps `3e-10`
(precise path) and the joint snaps to `(0, 0, 1)`. That is ratified by
`fabfc3d` and pinned by
`tests/test_frame_precision.py::test_final_mate_snap_and_generated_or_reused_joint_snap_unchanged`;
this change keeps it, so no general "the joint's axis equals the frame's
`z`" promise is written.

### 4. The spec: three MODIFIED requirements

- `mates`, "A frame resolves against its declarer at realization": the
  sentence "On that path, direction components within `1e-9` of `0`, `1`
  or `-1` SHALL be that integer" becomes the whole-direction rule, and the
  requirement gains "every resolved direction SHALL be unit to within
  `1e-12`" for both paths. "Supplying `x` while omitting `z` SHALL retain
  the previous snapped path" becomes "SHALL take the snapped path", the
  path having changed. One scenario added, "A frame with z omitted and x a
  few millionths off an axis reads a unit triad"; the ten existing
  scenarios carried under their exact titles. "Explicit x with default z
  keeps the old snapped path" (`x=(1, 3e-10, 0)`) and "Omitted x retains
  principal inference" hold unchanged under the new rule, every
  component of their inputs being within the snap.
- `mates`, "A realized node reads its resolved frames": its restatement
  "otherwise a direction component within `1e-9` of `0`, `1` or `-1`
  SHALL be that integer" becomes "otherwise each direction SHALL be
  snapped as a whole, as frame resolution requires", with the unit
  promise. No scenario added: the read returns the very objects frame
  resolution made, and the frame scenario's test reads them through
  `resolved_frames`. The ten existing scenarios carried.
- `joints`, "A joint is stated in the frame of whoever declares it": the
  paragraph "The framework SHALL normalize a declared `axis` to unit
  length and SHALL snap each component ..." becomes the whole-direction
  rule, the normalized declared axis unit to within `1e-12`. Three
  scenarios added: "An axis within the snap of a principal axis resolves
  to exact integers" (a guard, green before and after), "An axis a few
  millionths off a principal axis resolves unit" and "A mate's joint
  turns about its moving frame's z a few millionths off an axis" (both
  red today). The eight existing scenarios carried. The requirement's
  carry paragraph is not touched, so nothing is promised about a
  site-declared joint's carried axis.

The existing `tests/test_frame_precision*.py` pins stay green with no
edit: `Frame(x=(1, 3e-10, 0))` still reads `x = (1, 0, 0)`;
`Frame(z=(3e-10, 0, 1))` still reads `(0, 0, 1)`; `Frame(z=(2e-9, 0, 1))`
is still refused (two non-zero components either way); the mate-installed
joint for `z=(3e-10, 0, 1)` is still `(0, 0, 1)`; the docs pin's phrases
(`both`, `explicitly`, `omitted`, `snap`, `mate`, `joint`, `both
directions explicitly`) stay in the reworded passages.

### 5. No ADR

A conformance repair: both specs already promised unit directions, and
the per-component snap broke that promise for inputs no test covered.
The snap's purpose — exact integers for an axis, no residue in a document
— is unchanged, and no reader's contract narrows: a reader who relied on
"every component near `±1` is an integer" was reading a non-unit vector.
ADR-147's "rotation snapped to a whole number within `1e-9`" is the mate's
rest rotation, untouched.

### 6. Manual, architecture note and changelog

- `docs/concepts/joints.rst` (the paragraph after the `resolved_frames`
  example): "Omitted ``x`` or ``x=None`` also keeps that path: components
  within ``1e-9`` of ``0``, ``1`` or ``-1`` become those integers" states
  the whole-direction rule; "Final mate angle/axis snap and Joint axis
  snapping remain unchanged" says that a joint's axis is snapped by the
  same whole-direction rule and a mate's final angle/axis snap is
  unchanged. Read `skills/write-the-manual/SKILL.md` (workspace) before
  the edit; no new section, no account of the change.
- `docs/architecture.md`: the frame paragraph's "With z omitted or x
  omitted/None, the existing `1e-9` component snap remains ... final mate
  and Joint snaps are unchanged", and the joint paragraph's "The
  normalized axis is snapped to an exact 0/1/−1 within `1e-9`", state the
  whole-direction rule.
- `docs/project/changelog.rst`: an `Unreleased` section above
  `Machinome 0.8.0` (created, the release pins allowing exactly one) with
  one bullet naming `snap-keeps-the-triad-unit`: a joint's axis and a
  frame direction on the snapped path snap to a principal axis only as a
  whole, so one a few millionths off an axis is read unit; frames and
  joints are released (0.7.1), so the change is user-visible even where
  no document changes.

## Risks / Trade-offs

- **A `±1` component becomes a float where the direction is not snapped
  whole.** An axis with a component within `1e-9` of `±1` beside a
  component between `1e-9` and about `4.5e-5` publishes that component as
  the float normalization computed — `-0.9999999999799859`, or exactly
  `1.0` when the other component is below about `1.5e-8` — where it
  published the integer. A document carrying such an axis changes in that
  number's text (`1` to `1.0`), not its value. No project is known to
  declare one; `tests/base_documents/` is hashed before and after
  (tasks §1.3, §4.4) and the SO-100's operations compared (tasks §5).
- **An `assertEqual` against the integer `-1` for such a direction would
  now fail.** SO-ARM100 compares at `1e-9`, still green; it is the only
  project known to have had such directions, and its own are on the
  precise path.
- **A direction within `1e-9` of an axis in every component snaps to it**
  even when the author meant a tilt below `1e-9` rad: today's behaviour,
  and the purpose of `_SNAP`.

## Migration Plan

None: no spelling changes. Resolved values change only for directions a
few millionths off an axis, from a non-unit vector to the unit one.

## Open Questions

1. **A catalogue survey of computed axes.** The literal scan cannot see an
   axis or frame direction computed at realization. A scratch survey that
   loads every catalogue model against the bench and lists each resolved
   joint axis and frame direction the rule would change would close that
   gap; it costs a load of every project (`scripts/load-projects` loads
   but does not inspect axes, so it would be a separate scratch script).
   The tasks do not include it. Answered by the orchestrator at review
   (6 October 2026): not owed by this cycle. Every direction the rule
   changes was non-unit before and is unit after, so a computed axis the
   scan cannot see is corrected, not broken; the campaign loads every
   catalogue model against its branch once at close
   (`scripts/load-projects`), which would surface a model the change
   refuses.
2. **The two per-component snaps left alone.** `Joint`'s site-declared
   carry (`carried / norm` then a per-component `_snapped`) and
   `mates._axis_angle`'s axis (`mates._snapped`, nearest integer within
   `1e-9`) can each produce a non-unit direction from an input a few
   millionths off an axis. No project is known to reach either. With the
   helper in place each would be a one-call change. Recorded as a new
   `warts.md` entry (tasks §7); answered by the pilot's triage.
