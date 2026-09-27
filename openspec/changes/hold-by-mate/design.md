## Context

A mate compiles at realization to a rest placement, a joint on the moving
child and a coordinate on the assembly (ADR-147, amended by ADR-148,
ADR-150, ADR-151). The rest placement never reads the freedom:
`apply_mates` (`mates.py:1122`) composes `P_owner · F_fixed · F_moving⁻¹`
from the two resolved frames and, for a fixed child, its rest
operations. Everything else a mate does is keyed on its freedom, and a
mate without one is refused before any of it runs:

- `_check_freedom` (`mates.py:465`) refuses `freedom is None`, naming the
  deferral of place-parts-by-mate;
- `Mate.__init__` (`:293`) builds a coordinate for every mate, and
  `__set_name__`, `__get__`, `__set__` name, read and bind it;
  `declared_ports` reports it through `coordinates`;
- `_install` (`:818`) specializes the moving child's declaration with
  the joint and adds the mate to its wiring -- the only place the
  child's class or realization changes (`ChildDeclaration.realize`
  calls into mates only when the declaration has a wiring);
- the relation and wiring checks admit every declared mate as a
  coordinate (`couplings.py:380-397`, `OwnRef.check_declared_on`;
  `declarative.py:~370-378`, the wiring source check); `coordinate_ref`
  (`couplings.py:2312`) already refuses a FRAME named as a relation's
  end;
- three messages assume a joint: `_check_fixed` ("can move within ...
  the mate '<name>' moves it"), `_check_moving` on an inherited child
  ("A mate gives the child it moves a joint of its own"),
  `_check_child_name` ("the mate gives '<child>' a joint named ...").

AlbertPro (`evidence/finding.md` §2-3) needs, for each of its 16 bought
parts placed in a printed frame and its 32 screws and nuts placed in a
servo's: a seat frame on the holding part, a connector frame on the
held part, and a mate between them that places and does nothing else.
Every fixed end is the holding class's own frame or a still sibling's
(§5); no held part is a fixed end of another mate in the same assembly;
every mate is stated in the class that declares its moving child. A
probe (§6) shows the rest placement already reproduces the project's
hand placement of the left knee servo within `3e-16`.

## Goals / Non-Goals

**Goals:**

- AlbertPro declares every bought part in the printed part that holds
  it, placed by a mate with no freedom at its measured seat, deletes the
  parallel tree, and reproduces its hand-placed poses at maximum
  deviation 0.
- A rigid mate is the rest placement of a mate and nothing else: no
  joint, no coordinate, no wiring, no new document content.
- Every existing mate is unchanged in objects, messages (but the three
  of decision 5 and the bare-mate reason), behaviour and bytes.

**Non-Goals:**

- A fixed end on a moving sibling; a fixed end on a sibling another mate
  places, and the dependency order it would need; a rigid mate on a
  child a base class declares.
- An unassigned rigid mate; a `Rigid()` freedom class.
- Loops, `Orbit` and `Free`, deeper ends, world-placement reads, the
  viewer, controls on a held part.

## Decisions

### 1. The freedom is left out; there is no `Rigid` class

`moving.on(fixed)` -- `FrameRef.on(self, fixed, freedom=None)` already
has the default. `_check_freedom` returns early for `freedom is None`
instead of refusing. `on(fixed, None)` is the same call and is accepted;
the spec says so and the manual does not teach it.

*Alternative rejected: a `Rigid()` freedom.* It would be a joint-like
object that installs no joint, owns no coordinate and takes no argument
AlbertPro would write: a class for symmetry with `Revolute` and
`Prismatic`, which the evidence rule names as not evidence. The working
note settled the spelling long ago ("Rigid is the default, so the base
sentence is placement and the freedom is the addition").

*Alternative rejected: refuse an explicit `None`.* Telling it from the
default needs a sentinel in `on()`'s signature and a refusal to word, for
a spelling nobody writes.

### 2. It compiles to the rest placement alone

`_install` returns before building a joint when the freedom is `None`:
no `_specialize`, no wiring entry, `mate.joint` stays `None`. So the
held child's declaration is untouched: `ChildDeclaration.realize` takes
none of the mate paths (no wiring, so neither `call_freedom_functions`
nor `_record_wiring`), the child's constructor resolves exactly the
joints its class declares (`resolve_declared_joints` finds no mate
joint to skip), and `type(child)` is the declared class -- stronger than
a moved child's `isinstance` (ADR-098's consequence does not apply).
`apply_mates` is unchanged: it iterates `_declared_mates`, which holds
the rigid mate like any other, and places the child from the frames with
the same operations, the same `_mate_slot` mark, the same hand-placement
refusal and the same re-run rule.

A held child that is an assembly with children and mates of its own
(AlbertPro's bolted servo), or that declares joints (a servo's output),
is placed from outside: its rest operations are appended after the
render, untagged, outside its joint block, and its own mates run in its
own `_rest`. Nothing here reads what the child contains.

### 3. Every mate is named

The bare-mate refusal in `declare_mates` stays for a rigid mate, with a
reason that is true for it: a mate is enumerated by `declared_mates`
under its name, read by that name and named by every refusal; a mate with
a freedom also names its coordinate after it. The message keeps the
existing fragments `named after the mate` for a mate with a freedom (the
existing `test_a_bare_mate_with_a_freedom` stays green unedited).

*Alternative rejected: accept a bare rigid mate*, as the wart writes
`servo.ears.on(trunk.bay_fl)`. `declared_mates` would need a second key
kind (the moving child's name, say) beside mate names, every refusal a
second way to name the mate, and the documented `name` read a `None`.
AlbertPro names 48 statements at a word each.

### 4. A rigid mate is not a coordinate

`Mate.__init__` builds no coordinate for `freedom is None`:
`coordinate = None`, `coordinates = {}`; `__set_name__` names none. So
`declared_ports` reports nothing (an empty mapping and a `None`
coordinate are both skipped, `ports.py:545-553`), and every consumer
enumerating ports -- qualified ids, bindings, the serializer, the
capture tool -- sees nothing new.

On an instance, `Mate.__get__` returns the mate itself for a rigid mate
(as reading a frame on an instance yields the frame, and as the working
note says, "reading `arm.lid` yields the declaration"), and `__set__`
raises `AttributeError`, naming the assembly's class and the mate and
saying it states no freedom and owns no coordinate. `AttributeError`
because that is Python's error for an attribute that cannot be set, and
a `hasattr`/`getattr(..., default)` probe then behaves.

Named where a coordinate is named, it is refused with a message naming
the mate: in `coordinate_ref` (`couplings.py:2312`), beside the frame
refusal already there, for the mate itself (the body's `bolted.drives(x)`,
`x.drives(bolted)`, `bolted + 1`) and for a `PathRef` whose terminal is a
rigid mate (`angle.drives(shin.bolted)` from above); and in the wiring
source check (`declarative.py`, the `ours` set built from the class's
mates), for `Wheel(spin=bolted)`. The implementer may choose a narrower
seam if one catches all three routes; each route has a test (tasks 2.6).
`OwnRef.check_declared_on` then never sees a rigid mate.

*Alternative rejected: a coordinate that is never wired* -- the rigid
mate keeping a `RotationalPort` bound to nothing. It would be reported
by `declared_ports`, carried in the bindings table, offered as a
relation end that moves nothing, and a driver aimed at it would silently
do nothing.

*Alternative rejected: let the `None` coordinate fail where it is read.*
An `AttributeError: 'NoneType' object has no attribute '__get__'` names
nothing; a plain "has no attribute 'bolted'" would be false.

### 5. The fixed end stays still, and three messages become true

The fixed-end rule is unchanged: a fixed end is the assembly's own
frame or a frame of a child that no mate places and whose class declares
no joint. AlbertPro declares each bought part in the class of the part
that holds it, so every fixed end is that class's frame or a still
sibling's, and the held part rides because it is the moving part's
descendant (`evidence/finding.md` §5). That is Thor's answer: a
fastener belongs in the class of the part it fastens; a fixed end on a
moving sibling is not needed, and stays refused.

A fixed end on a child a RIGID mate places is also still refused
(`placed` holds every mate). Nothing moves there; the refusal stands
because `apply_mates` places a class's mates in declaration order and
nothing orders the fixed child's mate first -- the dependency order the
place-parts-by-mate design's §9 (b) described, which no project needs
yet. The message changes for this case only: it names the mate that
PLACES the fixed child and says this version orders no mate before
another, instead of "can move ... moves it".

`_check_moving`'s refusal of a mate on an inherited child stays for
every mate; for a rigid mate its reason ("gives the child ... a joint of
its own") is replaced by one that is true: the mate is stated in the
class that declares its moving child. `_check_child_name` is skipped for
a rigid mate, which gives the child nothing under its name.

### 6. What stays refused

A freedom that is not a `Revolute`, a `Prismatic` or left out (the
message names the three); a second mate on one child, whichever are
rigid (a rigid mate enters `placed` like any other, so the existing
loop refusal fires, naming both); a `render()` that also places a held
child (`apply_mates` refuses by the phase's `applied` list, whatever the
freedom); ends through a list, a `repeat()` or more than one child.

### 7. The document: nothing new, a different form

A rigid mate publishes the held child's rest operations, no binding, no
field, no version move. Beside a hand placement the operations differ
only in form: one rotation where a hand writes two (the left knee servo's
`rotate(90, y)`, `rotate(180, x)` becomes one half turn about
`(1, 0, 1)/√2`), none where a hand writes an identity rotation
(AlbertPro's `horn.rotate(0.0, ...)`), and `'180'` where a hand writes
`'180.0'` (the snap makes a whole angle an `int`). The composed matrices
agree within `3e-16` (`evidence/finding.md` §6). So the framework's
twin test compares composed placements and operation kinds, not bytes,
and AlbertPro's validation compares world matrices
(`capture_poses.py compare`), not documents.

### 8. What was struck, and why

- **A fixed end on a moving sibling.** Thor's question; AlbertPro
  answers it by declaring the fastener in the fastened part's class.
- **A fixed end on a rigidly held sibling**, with the dependency order
  and cycle refusal it brings. AlbertPro's screws are held by the servo
  inside `BoltedServo`, whose `servo` is placed by nothing.
- **A rigid mate on an inherited child.** AlbertPro declares every
  corner's children in its per-corner subclass.
- **The bare rigid mate** (decision 3) and **a `Rigid` class**
  (decision 1).
- **A world-placement read** (Thor's first finding): AlbertPro's
  `SourcedTest` recovers placements from meshes; the framework test uses
  the suite's composition of published operations.

### 9. ADR

**ADR-152 (NODE): a mate may leave its freedom out** -- amends ADR-147
("A Mate Compiles at Realization to a Rest Placement, a Joint and a
Coordinate": the compile, "A `Mate` is a `Coordinate` owning one
`RotationalPort`", "no freedom at all (the rigid mate) [is] refused",
the deferral in its Consequences) and ADR-151 ("`Orbit`, `Free` and the
rigid mate stay refused"), cites ADR-098 (the specialization a rigid
mate does not make). Records the rejected alternatives of decisions 1,
3 and 4, and that the dependency order among sibling mates stays
deferred. ADR-147 and ADR-151 gain an *Amended by* line; the README
indexes ADR-152 and updates both entries. Extracted after implementation
confirms the design. A MODIFIED spec block alone was considered and
rejected: both ADRs' decision texts would contradict the code.

## Risks / Trade-offs

- **A `Mate` that is not a coordinate is still a `Coordinate` subclass.**
  -> Its coordinate-taking surfaces are closed by decision 4's refusals,
  each tested; the class split (a `Mate` base and a coordinate-owning
  subclass) is the implementer's option if it is smaller, not required.
- **The refusal seam may miss a route** (a `Bound(reads=...)`, a
  control naming a coordinate by path). -> Both go through coordinate
  references; tasks 2.6 tests the three routes AlbertPro could write by
  mistake, and a route found untested during apply is added red first.
- **Two rigid-refusal tests are replaced.**
  `RefusalTest.test_the_rigid_mate_is_deferred` and
  `test_the_rigid_mate_names_both_freedoms` pin the refusal this cycle
  removes; they become the acceptance tests of tasks 2.1, run red first,
  and the `Orbit`/`Free` test keeps its fragments plus `no freedom`
  (the message keeps saying `a Revolute or a Prismatic`).
- **The operations' form differs from a hand placement** (decision 7).
  -> Documented in the manual paragraph and the project's task; the
  project compares matrices.
- **AlbertPro gives up its printed-only subtree** (its D12). -> A
  project decision, recorded in its own change (tasks §6), not solved
  here.

## Migration Plan

No framework user migrates: every existing mate is unchanged. AlbertPro
follows later in its own repository, by a separate agent (tasks §6),
compared pose for pose at maximum deviation 0 against its `main`.
Rollback is reverting the framework commits.

## Open Questions

- The four scope questions in `proposal.md`, each written to its
  recommendation, await ratification.
