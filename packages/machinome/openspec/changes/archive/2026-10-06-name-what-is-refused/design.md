## Context

### Reproduction at `9f86b6a`

Probes in the campaign scratchpad
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle2a/`):
`probe.py` (all three findings on fixtures, beside a one-line
`pyproject.toml` that gives its nodes a project root; output
`probe-base.txt`), `clocked_probe.py` (a mated copy of
`tests/clocked_project/gate.py`'s `Shut`; output `clocked-probe-base.txt`)
and `omx_probe.py` (the originating project; output
`omx-probe-base.txt`). Each was run with the bench first on `PYTHONPATH`;
`machinome.__file__` printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.
The scratchpad is not durable: `evidence.md` carries the probes' sources
(tasks §1.4).

**Finding 1, the axis-less refusal** (all raised at class definition):

| Written | Raised by | Message today (head) |
|---|---|---|
| class body `slide = Prismatic(axis=None)` | `Joint.__set_name__` (`joints.py:392`) | `Loose.slide is a Revolute without an axis. An axis may be left out only in a mate's freedom ...` |
| mate `grip = finger.origin.on(seat, Prismatic(axis=None, ...))` on `Palm` | the same, on the joint `_install` gives the moving child | `Finger.grip is a Revolute without an axis. ...` |
| site `car = Slider(travel=Prismatic(axis=None))` on `Rail` | the same, on the specialized child class | `Slider.travel is a Revolute without an axis. ...` |
| class body `turn = Revolute()` | the same | `Loose.turn is a Revolute without an axis. ...` (right) |
| site `wheel = Finger(turn=Revolute())` on `Axle` | `ChildDeclaration.__init__` (`declarative.py:328`) | `...Axle: the joint 'turn' passed where Finger is declared is a Revolute without an axis. ...` (right) |
| `Prismatic()` | Python | `_MateFreedom.__init__() missing 1 required positional argument: 'axis'` (ADR-151's consequence; not touched) |

Three things are wrong for a non-`Revolute`: the kind, the advice (an
axis left to the moving frame), and — for the mate and the site — the
class named, which is the moving child's or the specialized child's
rather than the class whose body the author wrote. The site check in
`ChildDeclaration.__init__` tests `isinstance(value, Revolute)` only, so
a site `Prismatic(axis=None)` falls through to `__set_name__` on the
specialized class.

**Finding 2, the range refusal on a mate's joint.** A mate's fresh freedom
becomes a joint `_install` (`machinome/motion/mates.py`) gives the moving
child's class, named after the mate and marked `installed_by = mate`; the
assembly's mate coordinate is wired into it. A binding is judged on that
joint, against the child, and every range message heads itself
`{_where(node)}: joint '{name}'` with `node` the child:

| Path | Site | Measured head |
|---|---|---|
| OpenMANIPULATOR-X, `set_state(grip=21)` | `Joint._refuse_out_of_range`, `joints.py:696` | `arm.link2.link3.link4.link5.left_finger: joint 'left_travel' declares the range -11.0 to 20.0 mm, and 21 is outside it.` |
| the same, `grip=-12` | the same | `... and -12 is outside it.` |
| `Link5Assembly()` alone, `left_travel = 21` | the same | `left_finger: joint 'left_travel' ...` |
| fixture `Gripper` (the project's shape), `grip=21` | the same | `wrist.palm.finger: joint 'grip' ...` |
| a freedom whose upper bound is `Bound(..., reads=(gate,))`, `gate=3`, value 5 | `couplings.refuse_bounds`, `couplings.py:2862` | `finger: joint 'grip' -- the coordinate finger.grip -- declares the range 0 to 3 mm, and 5 is outside it. ...` |
| the same palm held as `palm` under a root (`HeldGate`) | the same | `palm.finger: joint 'grip' -- the coordinate palm.finger.grip -- ...` |
| `tests/mate_project/slide.py`'s `Palm()` as the root, `left_grip = 25` | `joints.py:696` | `left_finger: joint 'left_grip' ...` (the root's name is `'Palm'`) |
| a mated `Shut` under a clocked root, `move('crank', by=400.0)` | `clocked._commit_out_of_range`, `clocked.py:1546` | `shutter: joint 'travel' -- the coordinate 'shutter.travel' -- declares a high bound of 0.0 mm, ...` |
| a site-declared `Prismatic` on `finger` (control) | `joints.py:696` | `finger (Finger): joint 'grip' ...` (right: the site joint is bound as `finger.grip`) |

The same head is written, unmeasured but on the same arguments, by the
reversed-range refusal (`joints.py:688`), the two bound-expression
refusals (`joints.py:728`, `:736`), the reversed refusal at the
enumeration's close (`couplings.py:2855`), the non-numeric `Bound`
refusal (`couplings.py:2904`) and the clocked construction refusal
(`clocked.py:1421`). `Joint.declarer_of` (`joints.py:483`) already names
the mate. The qualified id a running or clocked bank gives a mate's
coordinate is the installed joint's path
(`arm.link2.link3.link4.link5.left_finger.left_travel`, measured with
`qualified_coordinates`), and the clocked messages quote it as such.

**Finding 3, `a.drives(a)`.** `relate` (`couplings.py:2363`) compares a
relation's sources with its driven ends — `_self_read_index`, through the
reused-joint alias keys — only when an end names several coordinates
(`several`). A one-to-one relation naming one coordinate at both ends is
recorded and refused at the first enumeration:

| Written | At class definition | First enumeration |
|---|---|---|
| `wheel.turn.drives(wheel.turn)`, rendered at rest | accepted | `UnreachedCoordinate: wheel.turn drives wheel.turn: nothing bound either end. ...` (`couplings._refuse`, `:3242`) |
| the same, `wheel.turn = 30` bound | accepted | `DoublyBound: wheel.turn would be bound by the relation wheel.turn drives wheel.turn and by the author's simulate(). ...` |
| the same beside `crank.drives(wheel.turn)` | accepted | `DoublyBound: ... by the relation wheel.turn drives wheel.turn and by the relation crank drives wheel.turn. ...` |
| with `law=` | accepted | `UnreachedCoordinate`, as above |
| under `Time.running()`, `Sim(...).run(0.1)` | accepted | `UnreachedCoordinate`, as above |
| own port `turn.drives(turn)` | accepted | `UnreachedCoordinate: turn drives turn: ...` |
| `wheel.drives(wheel.turn)` (the node standing for its one joint) | accepted | `UnreachedCoordinate: wheel drives wheel.turn: ...` |
| `mount = body.axle.on(seat, body.turn)`; `mount.drives(body.turn)` | accepted | `UnreachedCoordinate: mount drives body.turn: ...` |
| `crank.drives(crank)`, a `Driver` (control) | `TypeError: driver 'crank' cannot be the driven end of a relation ...` | — |
| `wheels.turn.drives(wheels.turn)` over a repeat (control) | `TypeError: 'wheels.turn' passes through the repeated declaration ... cannot be the SOURCE ...` | — |
| `(crank & wheel.turn).drives(wheel.turn, law=...)` (control) | accepted: a read (ADR-121) | — |

No probed shape is ever posed. ADR-100 declined to widen its
class-definition refusal to the one-to-one shape as "a strict improvement
this cycle does not measure against the catalogue"; ADR-121 recorded it
as a follow-up. Measured now: a literal scan of every Python file under
`projects/` (excluding `_build` and `.git`) for `X.drives(X)` with the
same dotted name on both sides finds none among 4238 `.drives(` lines in
552 files; the framework's `tests/`, `machinome/` and `docs/` write none.
A relation spelled across two lines, or naming one coordinate through
two different spellings, is not seen by a literal scan.

### The originating project at `9f86b6a`

`projects/Robotic-Arms/open_manipulator`, branch `frames-and-mates`,
`04f1188`, clean tree. Against the bench: `python -m pytest
simulation/test_frames.py`, 11 passed in 1.55 s; `machinome test --mesh
simulation/open_manipulator_x.py:OpenManipulatorX`, 4 passed in 1.66 s
(mesh engine, volume epsilon 0 mm³). Its guard
`test_a_finger_binding_past_the_urdf_limit_is_refused` asserts only that
`left_travel` appears in the message. A second project pins the mate's
name in the same refusal: `projects/Robotic-Arms/openarm`
(`frames-and-mates`, `a59c006`, clean), `simulation/test_frames.py`
asserting `assertIn(mate_name, ...)` and `r"finger[12]_turn"`; 10 passed
in 5.40 s against the bench.

### Focused tests at `9f86b6a`

`tests/test_joints.py tests/test_mates.py tests/test_couplings.py
tests/test_clocked_bounds.py tests/test_running_reads.py
tests/test_mate_existing_joint.py`: 603 passed, 954 subtests passed,
11.21 s.

## Goals / Non-Goals

**Goals:** each of the three refusals names what was refused in the words
of the declaration the author wrote — the joint's kind; the mate, on the
assembly that states it; the relation whose one source is its own driven
end — at the point it is refused today, or for the third at class
definition, where the several-ends self-read is judged.

**Non-goals:** any verdict; any new reading of `a.drives(a)`; bank ids and
published documents; the constraint-intersection refusals
(`program.py:4067`, `constraints.py:131`, `:156`); the site-declared joint's
head (it is bound where it names); `Prismatic()`'s Python error; the
projects.

## Decisions

### 1. The axis-less refusal takes the kind and the place the author wrote

`axisless_refusal(owner, name, site=None)` becomes
`axisless_refusal(kind, where)`: `kind` the joint's class, `where`
the phrase naming the declaration, built by each caller. The kind is
told by `issubclass(kind, Revolute)` / `issubclass(kind, Prismatic)` and
displayed by `kind.__name__`: comparing the class's name to a string is
what `node-model`'s "No node type is recognised by its class name"
(ADR-166) forbids, and `tests/test_no_class_name_recognition.py` refused
the first implementation, which passed `type(self).__name__` and compared
it with `'Revolute'` and `'Prismatic'` (evidence.md, §4.3). Text:

- a `Revolute`: exactly today's text after `where` — "is a
  Revolute without an axis. An axis may be left out only in a mate's
  freedom -- moving.on(fixed, Revolute(...)) -- where the moving frame
  supplies it; everywhere else a joint states the line it turns about:
  Revolute(axis=(x, y, z), ...)." The existing `AxislessRevoluteTest`
  stays green unedited.
- any other kind, with `a`/`an` by its initial: "{where} is a {kind}
  without an axis. A {kind}'s axis is required everywhere[, a mate's
  freedom included]: {kind}(axis=(x, y, z), ...). Only a Revolute may
  leave its axis out, and only as a mate's freedom, where the moving
  frame supplies it." — the bracketed clause for a `Prismatic` only, the
  one other kind a mate takes as its freedom.

The callers:

- `Joint.__set_name__` (`joints.py:391`): `where` is
  `f"{mate.owner.__name__}.{mate.name}: the mate's freedom"` when
  `getattr(self, 'installed_by', None)` is a mate — `_install` sets it
  before `_specialize` fires `__set_name__`, and `declare_mates` runs after
  the mate's own `__set_name__` gave it its owner — and otherwise
  `f"{owner.__name__}.{name}"`, as today. Kind: `type(self)`.
- `ChildDeclaration.__init__` (`declarative.py:315`): the test widens
  from `isinstance(value, Revolute)` to
  `isinstance(value, (Revolute, Prismatic, Orbit))` — every kind that
  declares an axis; `Free` sets `axis = None` by design and is excluded
  by not being listed — with `where` today's
  `f"{declaring}: the joint '{key}' passed where {node_class.__name__} is declared"`.

So: class body `Loose.slide is a Prismatic without an axis. A Prismatic's
axis is required everywhere, a mate's freedom included: ...`; mate
`Palm.grip: the mate's freedom is a Prismatic without an axis. ...`; site
`...Rail: the joint 'travel' passed where Slider is declared is a
Prismatic without an axis. ...`; `Orbit(axis=None, ...)` in a class body
`Loose.orbit is an Orbit without an axis. An Orbit's axis is required
everywhere: Orbit(axis=(x, y, z), ...). ...`.

Why not a mate-side refusal in `mates._check_freedom`: the `mates`
capability says a `Prismatic` without an axis is refused as it is
anywhere and "the mate SHALL add no refusal of its own" (ADR-151). The
joint's own refusal, naming the mate, keeps that.

### 2. One helper says where a joint's coordinate is bound

`_binding_site(node, joint)` in `joints.py`, beside `_where`, returns
`(site, named)`:

- `joint.installed_by` is a mate, `node._parent` is linked and is an
  instance of `mate.owner`: `(node._parent, f"mate '{mate.name}'")` — the
  assembly that states the mate, the one place its coordinate can be
  bound (mates: "binding it by any other route ... SHALL be refused,
  naming the mate's coordinate as the one to bind");
- otherwise `(node, f"joint '{joint.name}'")`, today's head.

A reused-joint mate installs nothing (`installed_by` stays unset on the
original joint), so its refusals keep naming the child's joint, which is
bindable there. A mate's child not yet linked under its assembly keeps
today's wording: there is no path to give, and `Joint.declarer_of`
already refuses a `Bound` read from it naming the mate.

Every range refusal that can judge a mate's joint takes its head from it:

- `joints.py`: `_refuse_out_of_range`'s reversed (`:688`) and
  out-of-range (`:696`) messages, `_bound_at`'s two (`:728`, `:736`):
  `f"{_where(site)}: {named} declares the range ..."`;
- `couplings.py`: `refuse_bounds`'s two (`:2855`, `:2862`) —
  `f"{_where(site)}: {named} -- the coordinate {_where(site)}.{joint.name} -- ..."`
  — and `_bound_side`'s (`:2904`);
- `simulation/clocked.py`: `_constrained`'s `refuse` (`:1421`) and
  `_commit_out_of_range` (`:1546`) — `f"{_where(site)}: {named} -- the
  coordinate '{identifier}' -- ..."`, the bank id quoted as it is today.

The rest of every message is unchanged. The OpenMANIPULATOR-X refusal
then reads `arm.link2.link3.link4.link5: mate 'left_travel' declares the
range -11.0 to 20.0 mm, and 21 is outside it. A range refuses ...`. The
installed joint's name is the mate's name by construction
(`_specialize(..., {mate.name: joint})`), so nothing a reader could
search for is lost.

Why not name both ("mate 'left_travel' -- the joint it gives
'left_finger' --"): the joint on the child cannot be bound and is not
written anywhere in the project; naming it again is what the finding
asks to stop. Why not rename the bank id: it is the qualified id the run,
the clocked bank and the published document carry; that is not a
message change.

### 3. `a.drives(a)` is refused at class definition

In `relate`, after the existing end checks (`member.check('driver')`,
`driven_ref.check('driven')`, which keep their own refusals for a driver
or a repeat named at a forbidden end), and only when `several` is false:
if the source and the driven end name one coordinate, raise `TypeError`.

The comparison is the one `_self_read_index` makes for a group —
`_alias_comparison_key` of each side — with inferred nodes expanded
unconditionally (`_alias_comparison_key(ref, True)`), so a written path
(`wheel.turn`), the node standing for its one joint (`wheel`, keyed
`('path', id(root), ('turn',))` once expanded) and a reused-joint mate's
handle (`mount`) all compare equal to `wheel.turn` / `body.turn`. The
expansion is safe there: the end checks have run, so `declaration()` of
an inferred node resolves. A private helper beside `_self_read_index`,
`_names_one_coordinate(driver_ref, driven_ref)`, holds the comparison.

Message (the relation as written, its one source and driven end, and
what to write instead):

```text
wheel.turn drives wheel.turn: the relation's one source, wheel.turn, is
its own driven end, wheel.turn. A relation naming one coordinate at each
end computes the driven value from the source's, and here there is no
other value to compute it from: bound at either end it is the same
coordinate bound twice, and bound at neither nothing reaches it. Drive
wheel.turn from another coordinate; a law that reads the coordinate it
drives names another source beside it,
(source & wheel.turn).drives(wheel.turn, law=...), under a root
declaring time = Time.running().
```

Why at class definition rather than at the enumeration's close: the
comparison is already made there for the several-ends shape and costs
one key comparison; every probed shape is refused at its first
enumeration anyway, so the earlier refusal changes when, not whether. The
brief's alternative, refusing at `_refuse`'s "nothing bound either end"
branch, would leave the bound shapes refused as `DoublyBound`, still not
naming the shape.

Why not a new error kind: the several-ends refusals beside it are
`TypeError` at class definition; `UnreachedCoordinate` and `DoublyBound`
are enumeration refusals, and this is no longer one.

### 4. The specs: three MODIFIED requirements

- `joints`, "Joint declarations": the sentence "Every other joint kind's
  `axis`, where it has one, SHALL remain required." gains the refusal of
  an explicit `axis=None` of any other kind — in a class body, at a
  declaration site or as a mate's freedom — at class definition, naming
  the class and the joint (for a mate's freedom, the assembly and the
  mate), the kind, and that the axis is required. One scenario added; the
  eight existing scenarios carried.
- `joints`, "A declared range refuses a binding outside it": the first
  paragraph's "naming the joint, the value, the range, the unit and the
  node" gains: for a joint a mate gave the node, the refusal names the
  mate and the assembly that states it, by that assembly's path, in place
  of the joint and the child. One scenario added; the eleven existing
  scenarios carried.
- `couplings`, "A relation may name several coordinates at each end": a
  closing paragraph, after the refusal of a self-read under no running
  root — a relation naming ONE coordinate at each end, the same
  coordinate on both, however spelled, is not a read and is refused at
  class definition naming the relation and saying its one source is its
  own driven end. The sentence "Such a relation SHALL be recognized only
  where an end names SEVERAL coordinates" stands: the one-to-one shape is
  refused, not read. One scenario added; the ten existing scenarios
  carried.

### 5. No ADR

Three wording repairs and one earlier refusal of a shape that is refused
anyway. ADR-100 and ADR-121 left the one-to-one refusal open as an
unmeasured improvement, not as a decision against it; this change
measures it (Context) and takes it. ADR-151's consequence "whose wording
still names a `Revolute`" is a record of that cycle and stays as written.

### 6. Manual and changelog

No manual page quotes any of these messages; `docs/concepts/joints.rst`
already says a `Prismatic` "always states its `axis`, here as anywhere",
and `docs/concepts/relations.rst`'s refusal list describes the
enumeration's refusals, which this change does not alter. The applier
greps `docs/` for `without an axis`, `declares the range` and
`nothing bound either end` and confirms no hit is made wrong.
`docs/project/changelog.rst`: one bullet under the existing `Unreleased`
section naming `name-what-is-refused` — the three messages, and that
`a.drives(a)` is now refused at class definition.

## Risks / Trade-offs

- **A class declaring `a.drives(a)` that was never enumerated now fails
  at import.** Today such a class imports and is refused only when a tree
  holding it is solved. No class in the catalogue, the tests or the
  manual writes one (literal scan, Context); the campaign loads every
  catalogue model against its branch once at close
  (`scripts/load-projects`), which would surface a spelling the scan
  cannot see.
- **A message a project asserts verbatim would change.** The two projects
  known to assert on a mate's range refusal (OpenMANIPULATOR-X, OpenArm)
  assert the mate's name only, which every new head carries; both are
  run before and after (tasks §5). The framework's own assertions on
  these messages pin fragments that stay (Impact, proposal).
- **A mate's child linked under a parent that is not the mate's
  assembly** cannot happen (a mate's moving end is a frame of a child the
  assembly declares directly); `_binding_site` checks
  `isinstance(parent, mate.owner)` and falls back to today's wording
  rather than name a wrong assembly.

## Migration Plan

None: no spelling changes; three messages read differently, and
`a.drives(a)` is refused at class definition instead of at the first
enumeration.

## Open Questions

1. **The several-ends check does not expand an inferred node.**
   `(rack & wheel).drives(wheel.turn, law=...)` — the node standing for
   its one joint as a source beside the driven `wheel.turn` — is not
   recognized as a read by `_self_read_index` unless a reused-joint
   handle is among the ends, because `_alias_comparison_key` expands
   inferred nodes only then. This change expands them for the one-to-one
   comparison only (Decision 3), where a match can only be refused.
   Expanding them for the several-ends comparison would turn an
   unrecognized shape into a READ, which is semantics. Not taken; no
   project writes it. Recorded as a new `warts.md` entry (tasks §7) for
   the pilot's triage. Answered by the pilot.
2. **The constraint-intersection refusals name the bank id.**
   `program.py:4067` (`'{identifier}: constraint intersection (lo, hi) is
   empty'`) and `constraints.py:156` (`'{Class}.{joint}: constraint
   intersection ...'`) would name the installed joint's id or the child's
   class for a mate whose coordinate an ancestor constrains. No project
   constrains a mate's coordinate; the id is the bank's. Left as it is
   and recorded with Question 1's entry. Answered by the pilot.
