# The finding: a design's connectors are attachment frames, not joint frames

Recorded 2026-09-26 at the planning of `state-the-mate-line`, base
`d791eaa` (framework `main` after `place-parts-by-mate` integrated).
Everything below is quoted or re-derived from committed records; nothing
here was measured by running framework code at a new commit.

## 1. The wart (`workflow/warts.md`, "Findings from the framework cycle `place-parts-by-mate` (2026-09-26)", first two bullets)

> - **A design's attachment frames are not joint frames.** Thor's Assembly4
>   connectors, folded with their `AttachmentOffset`, put the connector's `z`
>   on the joint line for two of the five links (base yaw, elbow), reversed
>   for one (forearm yaw) and ACROSS the line for two (shoulder, wrist). A
>   revolute mate turns only about the moving frame's `z`, so Thor's emitter
>   turns both frames of each pair by one common rotation onto the joint
>   line the model declares, choosing the fixed frame's `x` as the default —
>   a choice the design does not make. The cycle's briefing assumed the
>   folded `z` is always the joint line; it is not. **Deferred.** A mate
>   could take the joint line separately from the attachment frame (an
>   `axis=` in the frame's own terms), which would let a design's
>   connectors be declared verbatim; comes back with a second design read
>   through its connectors, or with the rigid mate, which is the shape those
>   three attachments actually have.
> - **The frame's origin becomes the joint's anchor.** The moving frame's
>   `at` is copied as the installed joint's `at`, so a frame whose origin is
>   off the child's own origin but on the joint line (Thor's shoulder,
>   `(0, 0, 68)`) publishes a centring pair the hand-written joint at the
>   origin did not, and the composed poses differ by up to `1.42e-14` mm
>   under the comparison tool's `1e-9` rounding. Known at proposal time
>   (design.md, risks). **Left as is:** the pose is the same; the centring
>   pair is the honest reading of the declared origin.

Both dispositions were provisional ("every disposition is provisional
until the pilot triages it"). This change reopens both; see
`proposal.md`, scope question 1.

## 2. The originating project's workaround

`/home/asa/devel/machinome/projects/Robotic-Arms/Thor/simulation/tools/emit_frames.py`
(Thor `main`, commit `7aebdd0`, module docstring, read-only):

> What the design does not state is the line each link turns about:
> Assembly4 has no joints, and its connectors are attachment frames, not
> joint frames. `ROOT_CHAIN` names that line in each link's own frame -- the
> joint the model has declared since `move-thor-onto-joints`, in the frame
> ADR-097 reads it in. Where the design's folded `z` already is that line
> the design's two frames are emitted as they stand. Where it is not -- the
> shoulder's and the wrist's connectors stand across their joint lines, and
> the forearm's points down its own -- both frames are turned together
> about their shared origin until the moving `z` is the joint line. Turning
> both by the same turn leaves the placement they solve to unchanged, which
> the emitter checks against the design's own solve for every link; the one
> thing the turn chooses is the attitude about the new `z`, and it is chosen
> so that the FIXED frame's `x` is the framework's default for its `z`.

`ROOT_CHAIN` already carries each link's joint line in the link's own
frame: `yaw` `(0, 0, 1)` on `Art1`, `shoulder` `(0, 0, 1)` on `Art2`,
`elbow` `(0, 1, 0)` on `Art3`, `yaw` `(0, 0, 1)` on `Art4`, `wrist`
`(1, 0, 0)` on `Art56`. `read_link` turns three pairs by a common `Q`
and restates the framework's default-`x` rule (`default_x`) to choose
it.

Thor's records
(`projects/Robotic-Arms/Thor/openspec/changes/archive/2026-09-26-place-the-links-by-mate/proposal.md`,
"Findings for the framework"):

> - A revolute mate turns only about the moving frame's `z`, and Assembly4's
>   connectors are not joint frames: three of Thor's five had to be re-based
>   onto the joint line, a choice the design does not state. A design read
>   connector for connector cannot be mated as it stands.
> - The moving frame's origin becomes the installed joint's anchor, so the
>   shoulder, whose design connector sits 68 up its line, gains a centring
>   pair in the published operations of `shoulder.art2` and differs from the
>   hand-written joint by 1.4e-14 mm in the last bits of some of `Art2`'s
>   own leaves (magnets, one screw) at every instruction pose — zero at the
>   capture tool's 1e-9 rounding. A probe with the shoulder pair moved to
>   `Art2`'s origin was bit-identical.

and `tasks.md` 4.2: "A probe with the shoulder pair moved to `Art2`'s
origin, `Art1.shoulder_pin` at (0, −68, 123), was bit-identical at all
six: the difference is the installed joint's anchor at the design's LCS
origin, 68 up the same line."

## 3. The design's connectors, verbatim

Re-derived read-only at planning time from Thor's design documents with
Thor's own reader (`simulation.tools.emit_frames` helpers,
`PYTHONDONTWRITEBYTECODE=1`, nothing written to Thor), folding each
link's `AttachmentOffset` into its moving LCS and performing NO turn —
what the emitter will emit once the turn is gone. Each pair was checked
against the design's stored solve with the emitter's own
`same_placement(..., 1e-6)`:

| mate | fixed frame (verbatim) | moving frame (verbatim) | joint line (`ROOT_CHAIN`, child frame) | moving `z` vs line | places as the design solves |
|---|---|---|---|---|---|
| `Thor.yaw` | `Base.yaw_pin = Frame(at=(0, 0, 79), x=(0, 1, 0))` | `Art1.yaw_bore = Frame(x=(0, 1, 0))` | `(0, 0, 1)` | on | yes |
| `Art1.shoulder` | `Art1.shoulder_pin = Frame(at=(0, 0, 123))` | `Art2.shoulder_bore = Frame(at=(0, 0, 68), z=(0, 1, 0), x=(-1, 0, 0))` | `(0, 0, 1)` | across | yes |
| `Art2.elbow` | `Art2.elbow_pin = Frame(at=(0, 160, 68))` | `Art3.elbow_bore = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))` | `(0, 1, 0)` | on | yes |
| `Art3.yaw` | `Art3.yaw_pin = Frame(at=(0, 0, -1))` | `Art4.yaw_bore = Frame(z=(0, 0, -1))` | `(0, 0, 1)` | reversed | yes |
| `Art4.wrist` | `Art4.wrist_pin = Frame(at=(0, 0, 111.5))` | `Art56.wrist_bore = Frame(x=(0, -1, 0))` | `(1, 0, 0)` | across | yes |

Every verbatim frame is expressible (every `z` principal, `x` stated
where it is not the default), and every verbatim pair places its link
where the design solves it. So with the joint line stated by the
freedom, Thor can declare the design's connectors as they are:

- `yaw` (base) and `elbow`: nothing changes; no line need be stated.
- `shoulder`: `Revolute(axis=(0, 0, 1), at=(0, 0, 0), ...)` — the axis
  because the connector's `z` stands across the line, the anchor because
  the hand-written `Art2.shoulder` joint was at `Art2`'s origin.
- `wrist`: `Revolute(axis=(1, 0, 0), ...)`.
- forearm `yaw`: `Revolute(axis=(0, 0, 1), ...)` — without it the
  installed joint would turn about the connector's `(0, 0, -1)` and
  every driver of the forearm yaw would turn it the other way.

Hand arithmetic, shoulder, verbatim pair: moving triad `x = (-1, 0, 0)`,
`z = (0, 1, 0)`, `y = z × x = (0, 0, 1)`; `R = F_moving⁻¹ = [[-1, 0, 0],
[0, 0, 1], [0, 1, 0]] = 2nnᵀ − I` for `n = (0, √½, √½)`, a half turn about
`(0, .7071, .7071)`; `t = (0, 0, 123) − R·(0, 0, 68) = (0, −68, 123)` —
Thor's hand-written `Art1.render()` placement, which the current mated
fixture `MatedHousing` also reproduces from its turned pair.

Wrist, verbatim pair: moving `x = (0, −1, 0)`, `z = (0, 0, 1)`,
`y = (1, 0, 0)`; `R = [[0, −1, 0], [1, 0, 0], [0, 0, 1]]`, a quarter turn
about `(0, 0, 1)`; `t = (0, 0, 111.5)`.

## 4. Source facts the design rests on

- `machinome/motion/mates.py`, `_check_freedom`: a freedom with
  `axis is not None` or `anchor_written` is refused ("the two frames
  supply the axis and the anchor"); `_install` builds
  `Revolute(axis=frame.z, at=frame.at, range=freedom.range,
  unit=freedom.unit)` from the moving frame's DECLARED arguments.
- `machinome/motion/joints.py`: `Revolute.__init__(axis=None,
  at=_DEFAULT_ANCHOR, ...)`; `anchor_written` is `self.at is not
  _DEFAULT_ANCHOR`; `Joint.resolve` refuses an axis of zero length at
  REALIZATION as `"{type(node).__name__}.{self.name}: axis -- ... has no
  direction"`, which for an installed joint names the child's class and
  the mate's name but not the mate as a mate, nor the assembly.
- `machinome/parameters.py`, `Quantity.evaluate`: a token resolves as
  `values[self._name]` — BY NAME — against the resolving instance's
  values. An installed joint resolves against the CHILD
  (`resolve_declared_joints`), so an assembly token written in a
  freedom's `at` would read the child's parameter of the same name
  silently (the fixture `MatedForearm` and `MatedArm` both declare
  `reach`), or fail naming the child. This is the reason
  `place-parts-by-mate` design decision 5 admits a freedom's range only
  as numbers, `None` or functions of the coordinate itself; the same
  reason applies to a stated line.
- `machinome/node/base.py`: a node resolves its joints
  (`resolve_declared_joints`) BEFORE its frames
  (`resolve_declared_frames`). A zero-length frame `z` on a mated child
  is therefore refused today by the installed joint's message, not the
  frame's. Not in this finding and not changed here (a stated axis
  bypasses the frame's `z` for the joint; the frame still refuses its
  own zero `z` for the placement).
- `tests/test_mates.py::RefusalTest::test_a_freedom_does_not_restate_the_line`
  asserts the refusal this change removes, for `Revolute(axis=(0, 0, 1))`
  and `Revolute(at=(0, 0, 0))`; it is the test that turns into the
  acceptance tests.
- `tests/test_joints.py::AxislessRevoluteTest` checks only the fragments
  `axis` and `mate` of the axis-less refusal, which a rewording keeps.
