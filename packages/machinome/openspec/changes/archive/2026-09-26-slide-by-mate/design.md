## Context

A mate compiles at realization to a rest placement, a joint on the moving
child and a coordinate on the assembly (ADR-147). Every piece of that is
written for one freedom kind today:

- `mates._check_freedom` refuses anything that is not a `Revolute`
  (`mates.py:452`), naming `Prismatic`, `Orbit` and `Free` as "not mate
  freedoms yet";
- `Mate.__init__` gives the mate a `RotationalPort` (`mates.py:278`);
- `mates._install` builds a `Revolute` for the child (`mates.py:795`),
  its axis the freedom's stated `axis` else the moving frame's declared
  `z`, its anchor the freedom's written `at` else the frame's declared
  `at`, told apart by `Revolute.anchor_written` (identity against the
  one `_DEFAULT_ANCHOR` object);
- `Prismatic` inherits `Joint.__init__(self, axis, at=(0, 0, 0), ...)`:
  its `axis` is required and its default `at` is a plain tuple, so
  `Prismatic(range=...)` fails at construction and a `Prismatic` has no
  `anchor_written` (`evidence/finding.md` §4).

Everything downstream of `_install` is already kind-blind: the joint
resolves, places, clears and range-checks through `Joint`; ADR-150's
realization path copies `mate.joint` and runs its own `resolve`;
`apply_mates` composes the rest placement from the frames alone; the
wiring, the unbound rule and the single-binder refusal key on the mate,
not the joint's kind; the serializer publishes a `Prismatic`'s
`Translation` exactly as for a class-body slide.

open_manipulator (`evidence/finding.md` §2-3) needs, for each finger: a
fixed frame on `Link5Assembly` at `(81.7, ±21.0, 0.0)`, a moving
`Frame()` on the finger, a freedom `Prismatic(axis=(0, ±1, 0),
range=(-11.0, 20.0), unit='mm')`, and the URDF's mimic as a relation
between the two mates' coordinates, driven from the root's `grip` by
path. No anchor, no function, every rest placement one translation.

## Goals / Non-Goals

**Goals:**

- open_manipulator states all six URDF joints as mates, its two fingers
  by a `Prismatic` freedom, and reproduces its hand-placed poses at
  maximum deviation 0.
- A `Prismatic` freedom follows the `Revolute` freedom's rules -- the
  frames fix the rest, the freedom fixes the line, the documented reads
  mean the same thing -- so the mate has one rule with two kinds, not a
  second rule, save one asymmetry: a `Prismatic` freedom states its axis
  (decision 1).
- Every existing mate and every class-body or site `Prismatic` is
  unchanged in behaviour, messages and bytes; a `Prismatic` still
  requires its axis everywhere.

**Non-Goals:**

- `Orbit` and `Free` freedoms; the rigid mate; loops, deeper ends,
  repeated frames.
- Controls on a mated part, the viewer, a documented read of a mate's
  resolved line or range.
- Checking a freedom's `unit` against its kind (a class-body `Prismatic`
  does not check it either).

## Decisions

### 1. A freedom may be a `Revolute` or a `Prismatic`, under one rule save the axis

`_check_freedom` accepts `isinstance(freedom, (Revolute, Prismatic))`
and applies every existing check to both, unchanged and in the same
order: the fresh-freedom check, `_check_stated` on a stated `axis` and a
written `at`, the range rule. `_install` builds `type(freedom)(axis=...,
at=..., range=..., unit=...)` from the same four expressions it uses
today. Nothing downstream changes (Context).

What open_manipulator exercises is a numeric `axis`, a numeric range and
`unit='mm'`. What the kind inherits without new code is the rest of the
rule: a stated `at`, three numbers; a function `axis` or `range` of the
assembly (decision 4). Each is inherited because refusing it for one
kind would be a new branch, a new message and a new line in the spec,
not because a project needs it.

The one asymmetry, stated plainly: a `Revolute` freedom may leave its
axis out, the moving frame's `z` then supplying it (ADR-147), and a
`Prismatic` freedom may not, because only the first was ever needed.
open_manipulator states both finger axes -- the URDF's `(0, 1, 0)` and
`(0, -1, 0)`, not the moving frame's `z` -- and no project needs a slide
along the moving frame's `z`. A `Prismatic` freedom without an axis is
refused by `Prismatic`'s own constructor, as anywhere, before the mate
is stated; the mate adds no refusal of its own (decision 8).

*Alternative rejected: the strictly narrowest `Prismatic` freedom* --
`at` ignored, installed as `Prismatic(axis, at=(0, 0, 0), range, unit)`
exactly as the class-body joint open_manipulator writes today. Its
required `axis` is what ratification kept (decision 8). Its ignored `at`
would leave `Prismatic`'s constructor alone, but the mate's documented
reads (`anchor_written`, "`at` is the mate's anchor only when written")
would mean one thing for a `Revolute` freedom and another, or nothing,
for a `Prismatic` one, and a left-out `at` would be the child's origin
for one kind and the frame's for the other. The cost difference is the
`at` default and `anchor_written` (decision 3).

### 2. `at` on a `Prismatic` freedom is the `Revolute`'s

The briefing asked whether to refuse a written `at` because the joint
ignores it. The source says the joint does not ignore it:

- `Prismatic.placement` does not use the anchor ("a translation along a
  line is the same wherever the line is taken to pass"), but the joint
  resolves and carries it "as the declared position of the slide, for a
  reader and for a later exporter" (`joints.py:870-880`);
- the control compiler reads `joint.arguments(node)[1]` for every joint
  a control poses and publishes it as the control's `origin`
  (`program.py:3886`, `_placed_geometry`; ADR-112 decision 3), so a
  `Slide` on a prismatic joint publishes its anchor as the gesture's
  origin;
- a class-body `Prismatic` accepts `at` in every form the joint argument
  rule takes.

So a `Prismatic` freedom's `at` is taken exactly as a `Revolute`
freedom's: optional, three numbers when written (a token, formula or
function refused with today's reasons), read in the moving child's own
frame, `(0, 0, 0)` written meaning the child's origin, left out meaning
the moving frame's origin. It moves nothing in the placement, and the
spec says so; its one reader is the published control origin. For
open_manipulator every choice gives the same joint: its moving frame is
`Frame()`, so the frame's origin and the class-body default are both
`(0, 0, 0)`.

*Alternative rejected: refuse a written `at` on a `Prismatic` freedom.*
It would make the freedom narrower than the joint it installs, add a
kind-specific refusal, and still need `anchor_written` to tell a
written `(0, 0, 0)` from the default.

### 3. `Prismatic` gains the anchor default and `anchor_written`, nothing else

`Prismatic(axis, at=_DEFAULT_ANCHOR, range=None, unit=None)` and the
`anchor_written` property, with one definition shared with `Revolute` (a
small private base or the two members lifted -- the implementer's
choice, not two copies). `axis` stays the first, required,
positional-or-keyword argument. `Orbit` and `Free` are untouched: their
`at` has no "left out means the frame's" meaning.

- A `Prismatic`, which states its axis positionally or by keyword,
  behaves as before: `_DEFAULT_ANCHOR` is a tuple equal to `(0, 0, 0)`
  and resolves by `resolved_vector` to the same floats, as it already
  does for every `Revolute`.
- Nothing else in `joints.py` or `declarative.py` moves:
  `Joint.__set_name__`, `axisless_refusal` and the site refusal in
  `ChildDeclaration.__init__` stay `Revolute`'s alone, and the `joints`
  spec is not modified -- its "Joint declarations" requirement already
  says "Every other joint kind's `axis` ... SHALL remain required".
  `Revolute` stays the one joint that may leave its axis out, as a
  mate's freedom only (ADR-147).

### 4. Functions of the assembly: ADR-150, unchanged

A `Prismatic` freedom's `axis` and `range` may each be one function of
the assembly that states the mate, called once as it realizes the
moving child, its result checked by the numbers' rules and resolved
against the child. `_install` marks the joint `_resolved_by_mate` from
the freedom's arguments, whatever its kind; `call_freedom_functions`
and `resolve_freedom_functions` copy and resolve `mate.joint` through
its own `resolve`, which is `Joint.resolve` for both kinds. The only
edit is wording: `_result_reason` and `_check_stated`'s zero-length
message say an axis of zero length "states no line", not "no line to
turn about". A fixture pins that the path works for the new kind
(tasks 2.6). No project needs a function in a `Prismatic` freedom now;
it is kept only because refusing it would cost code (scope question
2).

### 5. The mate's coordinate is of the freedom's port kind

`Mate.__init__` builds the coordinate as the freedom's own
`coordinate_kind` -- `TranslationalPort` for a `Prismatic` -- with the
freedom's unit (a `Prismatic`'s `'mm'` by default), falling back to
`RotationalPort` for anything `_check_freedom` will refuse at class
creation (the mate object exists, unassigned and unchecked, while the
body still runs). The kind is not cosmetic: a relation's derived
coordinate refuses terms of two domains (`couplings._shared_domain`), a
running program publishes each coordinate's `domain` and `unit`
(`program.py`, `_published_coordinates`), and a `Slide` control
requires a translational coordinate (`control.py`, `Slide.required_domain`).
A rotational coordinate in millimetres would pass open_manipulator's
non-running document and misdescribe the machine everywhere else;
`declared_ports` pins the kind (tasks 2.3).

### 6. The mimic needs nothing

The URDF's `mimic` becomes a relation between the two mates'
coordinates on the assembly that states both, `left_grip.drives(right_grip)`,
driven from the root by path (`grip.drives(arm....link5.left_grip)`).
The spec already makes a mate's coordinate an end of a relation and a
target of a driver ("A mate owns a coordinate on the assembly"). A probe
with two revolute mates on one palm, related and driven by path two
levels down, binds both and refuses a value past the first's range
(`evidence/finding.md` §6), and OpenArm's validated gripper relates two
mates' coordinates the same way. Nothing refuses it, so nothing is in
scope; a scenario and a test pin it with the slide (tasks 2.5).

### 7. What does not change

`Prismatic`'s required `axis`, the axis-less refusals of `Revolute` at
class definition and at a declaration site, and the `joints` spec. The
rest placement (`apply_mates`, `_placement`): the frames alone fix
it, whatever the kind. The installed joint's slot, identity, wiring,
unbound rest and single binder. The fixed-end rule: a child a
`Prismatic` mate places moves, and is refused as a fixed end by the
existing "a mate moves it" branch, so ADR-147's consequence -- the
dependency order is the declaration order and no cycle can be written
-- holds for both kinds. The document, serializer, export, viewer and
mechanics: a slide reaches the document as the `Translation` a
class-body `Prismatic` already publishes, symbolic in the driver when
driven (`['t', ['0', 'grip', '0']]`, `evidence/finding.md` §6).

### 8. What was struck, and why

- **`Orbit` and `Free` freedoms.** No project needs one; the working
  note argues `Orbit` is not a mate freedom at all. The refusal stays,
  its wording now naming the two accepted kinds.
- **A running-program test.** open_manipulator's `Instruction`s publish
  no program (`evidence/finding.md` §6); decision 5's port-kind test
  covers the domain a running program would publish.
- **A fixed-end-on-a-slid-child test.** Covered by the existing branch
  and its revolute test; no project states one.
- **The rigid mate**, though open_manipulator's gripper base and the
  arm's base would take one: they are not moving links, and their
  `render()` translates stay (as OpenArm's mounts did).
- **The axis-less `Prismatic`** -- `Prismatic(axis=None)` accepted as a
  mate's freedom, the moving frame's `z` supplying the line, refused
  elsewhere by a widened `axisless_refusal` and site check, with a
  `joints` spec delta. open_manipulator states both finger axes (the
  URDF's `(0, 1, 0)` and `(0, -1, 0)`, not the moving frame's `z`); no
  project needs a slide that takes the moving frame's `z`; the argument
  for it was uniformity across kinds, which the evidence rule names as
  not evidence. Struck at ratification by the orchestrator.

### 9. ADR

**ADR-151 (NODE): a mate's freedom may be a `Prismatic`** -- amends
ADR-147 ("The freedom is a fresh `Revolute`"; "A `Mate` is a
`Coordinate` owning one `RotationalPort`"; "`Prismatic`, `Orbit`, `Free`
... are refused naming this version's scope"; the deferral in its
Consequences), extends ADR-148 and ADR-150 (their line and function
rules apply to the new kind unchanged, save that a `Prismatic` freedom
states its axis, which ADR-148 let a freedom leave to the moving frame)
and cites ADR-112 (the published
control origin that makes `at` meaningful). Records the rejected
alternatives: the narrowest `Prismatic` freedom (decision 1), refusing
`at` (decision 2), a rotational coordinate for every mate (decision 5),
the axis-less `Prismatic` (decision 8).
ADR-147 gains an *Amended by* line; the README indexes ADR-151 and
updates ADR-147's entry. Extracted after implementation confirms the
design, per the framework-change skill. A MODIFIED spec block alone was
considered and rejected: ADR-147's decision text would then contradict
the code.

## Risks / Trade-offs

- **`Prismatic`'s constructor changes, for `at` only.** -> `axis` stays
  the first, required parameter, so every positional and keyword use is
  unchanged and an axis-less `Prismatic` is still refused at
  construction. The full suite and the base-document byte guard (tasks
  2.9) cover the default-anchor change.
- **A `Prismatic` freedom without an axis names no mate.** It is refused
  by Python's own "missing 1 required positional argument: 'axis'", at
  the line that writes it, before the mate exists. Accepted: it is the
  refusal a `Prismatic` gets anywhere, and no project writes one.
- **The coordinate's kind is chosen before the freedom is checked.** ->
  The fallback is only ever seen by a mate `_check_freedom` refuses
  when the class is created.
- **Existing tests narrowed.** `RefusalTest.test_other_freedoms_are_refused`
  asserts the `Prismatic` refusal; its `Prismatic` case moves out into
  the new acceptance test, run red first, and its `Orbit` and `Free`
  cases stay, with the message fragment updated to the new wording.
- **A freedom's `unit` is not checked against its kind**
  (`Prismatic(unit='deg')` is accepted), as for a class-body joint.
  Recorded, not fixed: no project writes one.

## Migration Plan

No framework user migrates: every existing mate installs the same joint
and publishes the same bytes. open_manipulator follows later in its own
repository, by a separate agent (tasks §6), compared pose for pose at
maximum deviation 0 against its `main`. Rollback is reverting the
framework commits.

## Open Questions

- None. The four scope questions in `proposal.md` are answered at
  ratification ("Ratified scope"): the three recommendations accepted,
  the axis-less `Prismatic` struck.
