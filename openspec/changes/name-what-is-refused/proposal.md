## Why

Three refusals point at the wrong thing. Each refuses what it should and
keeps doing so; each names, in its message, something the author cannot
act on. They share one shape — the message names what the framework
refused, in the words the author can act on — and close three entries of
`workflow/warts.md`.

**1. The axis-less refusal names a `Revolute` for any kind.** Finding,
`workflow/warts.md`, "Findings from the framework cycle `slide-by-mate`
(2026-09-26)":

> **The axis-less refusal names a `Revolute` for any kind.**
> `Joint.__set_name__`'s `axisless_refusal` was written when only a
> `Revolute` could lack an axis; a `Prismatic(axis=None)` written in a
> class body, or as a mate's freedom, is refused by it with "is a
> Revolute without an axis ... where the moving frame supplies it",
> which is wrong on both counts for a `Prismatic` (a `Prismatic` freedom
> states its axis, ADR-151). [...] A one-line wording fix naming the kind
> and, for a `Prismatic`, saying the axis is required everywhere.
> **Recorded.**

Reproduced on the bench `fix-warts-3` at `9f86b6a` (design.md, Context):
`slide = Prismatic(axis=None)` in a class body reads `Loose.slide is a
Revolute without an axis. An axis may be left out only in a mate's
freedom -- moving.on(fixed, Revolute(...)) -- where the moving frame
supplies it; ...`. As a mate's freedom it names, besides, a place the
author never wrote: `Finger.grip is a Revolute without an axis ...`,
where `grip` is the mate on the palm and `Finger` the moving child's
class. At a declaration site, `car = Slider(travel=Prismatic(axis=None))`
reads `Slider.travel is a Revolute ...`, naming the child's class where a
site `Revolute()` names the declaring class (`Axle: the joint 'turn'
passed where Finger is declared ...`), because the site check in
`ChildDeclaration.__init__` looks for a `Revolute` only.

**2. `JointRangeError` names the child's installed joint, not the mate's
coordinate.** Originating project:
`projects/Robotic-Arms/open_manipulator` (OpenMANIPULATOR-X, branch
`frames-and-mates`). Finding, `workflow/warts.md`, "Findings from the
OpenMANIPULATOR-X project's migration onto mates (2026-09-26)":

> **`JointRangeError` names the child's installed joint, not the mate's
> coordinate.** `set_state(grip=21)` is refused as
> `...link5.left_finger: joint 'left_travel' declares the range -11.0
> to 20.0 mm`, naming the joint the mate installed on the finger, while
> the only place it can be bound is `Link5Assembly.left_travel`; the
> names match, so a reader finds it, but the message points at the
> node a reader cannot bind. A wording candidate for the next mates
> cycle. **Recorded.**

Reproduced against the bench at `9f86b6a` with the project at `04f1188`
(clean tree): `OpenManipulatorX().set_state(base_yaw=0, shoulder=0,
elbow=0, wrist=0, grip=21)` raises

```text
JointRangeError: arm.link2.link3.link4.link5.left_finger: joint
'left_travel' declares the range -11.0 to 20.0 mm, and 21 is outside it.
[...]
```

from `Joint._refuse_out_of_range` (`machinome/motion/joints.py:696`).
The same head, `<the moving child's path>: joint '<name>'`, is written by
every range refusal that can judge a mate's joint: the reversed-range
and bound-expression refusals beside it (`joints.py:688`, `:728`,
`:736`), the judgement at the close of an enumeration of a `Bound` that
reads other coordinates (`couplings.py:2855`, `:2862`, `:2904`; measured:
`finger: joint 'grip' -- the coordinate finger.grip -- declares the range
0 to 3 mm ...`), and the clocked simulation's two
(`simulation/clocked.py:1421`, `:1546`; measured on a mated copy of the
`Shut` fixture: `shutter: joint 'travel' -- the coordinate
'shutter.travel' -- declares a high bound of 0.0 mm ...`). The mates
capability already refuses a binding of the installed joint by any other
route "naming the mate's coordinate as the one to bind"; the range
refusal is the one message that still sends the author to the child.

**3. `a.drives(a)`, one to one, deadlocks into `UnreachedCoordinate`
instead of naming itself.** Finding, `workflow/warts.md`,
"read-the-driven-coordinate (2026-09-15, found while fixing)":

> **`a.drives(a)`, one to one, still deadlocks into `UnreachedCoordinate`
> instead of naming itself.** ADR-100 declined to widen its
> shared-coordinate refusal to the one-to-one shape and ADR-121 does not
> either: recognition is scoped to a relation naming SEVERAL ends, which
> is the only shape that is forward-only, so `a.drives(a)` is not checked
> at class definition at all. [...] it raises `UnreachedCoordinate:
> wheel.turn drives wheel.turn: nothing bound either end` at the close of
> the enumeration, which says nothing about the shape. A one-to-one
> self-read has no second source to carry slope, so the skeleton test
> would refuse every such law anyway — the message, not the verdict, is
> what is wrong.

Reproduced at `9f86b6a`: `wheel.turn.drives(wheel.turn)` is accepted at
class definition and refused at the first enumeration in every shape
probed — rendered at rest (`UnreachedCoordinate: wheel.turn drives
wheel.turn: nothing bound either end. wheel.turn and wheel.turn are both
unbound ...`), with `wheel.turn` bound by the author or by another
relation (`DoublyBound: wheel.turn would be bound by the relation
wheel.turn drives wheel.turn and by ...`), with a `law=`, under
`Time.running()`, on a port of the class, and through a reused-joint
mate's handle (`mount = body.axle.on(seat, body.turn)`;
`mount.drives(body.turn)`). None names the shape. ADR-100 declined to
widen its class-definition refusal to this shape as "a strict
improvement this cycle does not measure against the catalogue"; a
literal scan of the catalogue (4238 `.drives(` lines in 552 Python files
under `projects/`) finds no one-to-one relation naming one coordinate at
both ends, and the framework's own tests and manual write none.

## What Changes

- **The axis-less refusal names the kind.** `axisless_refusal` in
  `machinome/motion/joints.py` takes the joint's kind. For a `Revolute`
  its text is unchanged. For any other kind it says that kind's axis is
  required everywhere — for a `Prismatic`, a mate's freedom included —
  and that only a `Revolute` may leave its axis out, as a mate's freedom.
  `Joint.__set_name__` passes the kind, and for a joint a mate installed
  from its freedom it names the mate on the assembly that states it
  (`Palm.grip`) rather than the moving child's class. The declaration
  site check in `machinome/node/declarative.py` refuses every joint kind
  that declares an axis (`Revolute`, `Prismatic`, `Orbit`) when it is
  `None`, so a site `Prismatic(axis=None)` names the declaring class as a
  site `Revolute()` does.
- **A range refusal on a mate's joint names the mate.** One private
  helper in `joints.py` answers where a joint's coordinate is bound: the
  node and the word `joint` for a joint of the node's own or given at a
  declaration site; the assembly that states the mate — the node's linked
  parent — and the word `mate` for a joint a mate installed. Every range
  refusal that can judge a mate's joint uses it for its head: the four
  in `joints.py`, the three in `couplings.py`, the two in
  `simulation/clocked.py`. The OpenMANIPULATOR-X message becomes
  `arm.link2.link3.link4.link5: mate 'left_travel' declares the range
  -11.0 to 20.0 mm, and 21 is outside it. ...`. A child not yet linked
  under the assembly keeps today's wording.
- **`a.drives(a)` is refused by name, at class definition.** `relate` in
  `machinome/motion/couplings.py` already compares a relation's sources
  with its driven ends, through `_self_read_index` and the reused-joint
  alias keys, but only when an end names several coordinates. It makes
  the same comparison for a relation naming one coordinate at each end,
  after the existing end checks, and refuses a match with a `TypeError`
  naming the relation and saying that its one source is its own driven
  end, and how a law that reads the coordinate it drives is written —
  `(source & wheel.turn).drives(wheel.turn, law=...)`.

**Deliberately out**, with the reason:

- the verdicts. Nothing refused today is accepted, nothing accepted is
  refused; `a.drives(a)` is refused earlier, at class definition, where
  the several-ends shape is (Risks in design.md). No one-to-one self-read
  semantics is added: ADR-121's reading stays scoped to a relation
  naming several ends;
- `simulation/program.py:4067` and `motion/constraints.py:131`/`:156`.
  They refuse an empty or violated intersection of an assembly's
  installed constraints, naming the bank's qualified id or the class and
  joint; the bank's id of a mate's coordinate is the installed joint's
  path (`...left_finger.left_travel`, measured), which is how the
  published document and the run name it. Renaming bank ids is not a
  message change, and no project reaches these refusals with a mate;
- the clocked messages' quoted bank id (`the coordinate
  'shutter.travel'`), for the same reason: only their head changes;
- the OpenMANIPULATOR-X project: read and run, never changed. Its guard
  `test_a_finger_binding_past_the_urdf_limit_is_refused` asserts only
  that `left_travel` appears, which stays true;
- the studio's API skill, which quotes none of these messages.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `joints`: "Joint declarations" — a joint of a kind other than
  `Revolute` written with `axis=None`, in a class body, at a declaration
  site or as a mate's freedom, is refused naming its kind and saying its
  axis is required; one scenario added, every existing scenario carried.
  "A declared range refuses a binding outside it" — the refusal of a
  binding of a joint a mate installed names the mate and the assembly
  that states it; one scenario added, every existing scenario carried.
- `couplings`: "A relation may name several coordinates at each end" —
  a relation naming the same coordinate as its one source and its one
  driven end is refused at class definition by name; one scenario added,
  every existing scenario carried.

## Impact

- Code: `machinome/motion/joints.py` (`axisless_refusal`,
  `Joint.__set_name__`, one helper beside `_where`, four range messages),
  `machinome/node/declarative.py` (the site check),
  `machinome/motion/couplings.py` (`relate`, `refuse_bounds`,
  `_bound_side`), `machinome/simulation/clocked.py` (`_constrained`,
  `_commit_out_of_range`).
- Tests: `tests/test_joints.py`, `tests/test_mates.py`,
  `tests/test_couplings.py`, `tests/test_clocked_bounds.py`. Existing
  assertions on these messages pin fragments that stay (`'elbow'`,
  `'left_grip'`, `'turn'`, `'axis'`, `'mate'`, and `"joint 'lift'"`,
  `"joint 'travel'"`, `"joint 'turn'"` in `tests/test_clocked_bounds.py`
  and `tests/test_clocked_time.py`, all on joints no mate installed); none
  is edited.
- Documents, published artifacts, bank ids: unchanged.
- Manual: no page quotes a changed message or states a changed rule
  (`docs/concepts/joints.rst` already says a `Prismatic` always states its
  axis); `docs/project/changelog.rst` takes one bullet under `Unreleased`.
- No ADR (design.md, Decision 5).

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 2a, `name-what-is-refused`,
validated in OpenMANIPULATOR-X.
