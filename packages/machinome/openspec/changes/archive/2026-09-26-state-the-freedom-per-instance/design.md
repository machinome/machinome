## Context

A mate compiles at realization to a rest placement, a joint on the moving
child and a coordinate on the assembly (ADR-147). `_install`
(`machinome/motion/mates.py`) builds the joint at class creation as
`Revolute(axis=<freedom's axis or the moving frame's declared z>,
at=<freedom's written at or the moving frame's declared at>,
range=freedom.range, unit=freedom.unit)` and installs it on the child's
specialized class, where `resolve_declared_joints` resolves it in the
child's own constructor, against the child. That is why the freedom's
numbers are numbers: a token written in the assembly would resolve by
name against the child, and a function written there would be called
with the child (ADR-148; `_check_stated`, `_check_freedom`).

OpenArm (`evidence/finding.md`) needs, per realized side, a different
fixed-frame origin (served: a frame's function receives its declarer,
the parent that holds `left`), a different axis on arm joints 1 and 6
and a different range on arm joints 1 and 2 and both fingers (refused).
No joint needs an anchor other than the child's own origin.

Seams, all existing:

- `mates._check_freedom`, `mates._check_stated` -- class-creation
  refusals of a freedom.
- `mates._install` -- the joint built for the child; `joint.installed_by`
  already names the mate; the child declaration's `wiring` already holds
  the mate under its name.
- `declarative.ChildDeclaration.realize(values, owner)` -- constructs the
  child with the realized PARENT in hand, records its wiring, and
  resolves site-declared joints against that parent
  (`_resolve_site_joints`, ADR-098), caching them in the child's
  `_joint_arguments`.
- `joints.resolve_declared_joints` -- runs in the node constructor and
  skips a site-declared joint because its parent is not available there.
- `joints.Joint.resolve` / `_vector` / `_span` / `arguments` -- normalize
  and snap the axis, refuse a zero one, order-check a numeric range,
  cache per instance; `arguments` resolves lazily on a cache miss.

## Goals / Non-Goals

**Goals:**

- OpenArm can state each joint once, as a mate whose fixed frame, axis
  and range are functions of the side, with one class per joint, and
  reproduce its hand-placed poses at maximum deviation 0.
- The function is called with the node whose class body wrote it, as
  every other function the framework calls.
- Every mate whose freedom states numbers or nothing installs the same
  joint by the same path, refuses with the same messages and publishes
  the same bytes.
- A wrong result is refused by the mate's name, before anything reads it.

**Non-Goals:**

- A function `at`; tokens or formulas anywhere in a freedom; a function
  `unit`.
- A documented read of a joint's resolved arguments on an instance.
- `Prismatic`, `Free`, the rigid mate, deeper ends, repeated frames,
  relations, the frame side.
- Moving the resolution of mates that state no function.

## Decisions

### 1. The function is called with the assembly that states the mate

Two candidates were argued against the source.

**(a) The ASSEMBLY (recommended).** The freedom is written in the
assembly's class body, beside the assembly's own frames. Every function
the framework calls today receives the realized node whose class body
wrote it: a frame's function its declarer (spec `mates`), a class-body
joint's its declarer (ADR-097), a site-declared joint's the realized
DECLARING PARENT, "not the child" (ADR-098, "Callables: one argument,
the realized declaring parent"). (A relation's `law=` is the one
different shape: it is handed the owners of the coordinates it relates,
by its own contract, not a node standing for the body it is written
in.) A reader of

```python
class Arm(AssemblyNode):
    left = Flag(False)
    joint1_pin = Frame(at=lambda node: ARM_JOINTS[side(node.left)][0].origin)
    joint1 = Joint1(left=left)
    turn1 = joint1.origin.on(joint1_pin, Revolute(
        axis=lambda node: ARM_JOINTS[side(node.left)][0].axis, ...))
```

reads both `node`s as the arm, and under (a) both are. It is also the
reading ADR-148 promised ("a resolver-side resolution"), and it removes
the reason ADR-147 and ADR-148 give for refusing the function in the
first place, rather than living with it. The frame the numbers are READ
in does not change: the result is a line in the moving child's own rest
frame (ADR-148), exactly as a numeric stated line. Who a function is
called with and which frame its numbers are read in are separate facts;
(a) keeps the first rule the framework already has and the second rule
the mate already has.

**(b) The MOVING CHILD (rejected).** Zero new machinery: drop the two
refusals and the installed class-form joint calls the function with the
child in its constructor, like any class joint. But the author writes
the function in one class and it is called with an instance of another,
the one place in the framework where that happens; an assembly-only
attribute fails at realization with an `AttributeError` about a class
the author did not write it in, and a same-named attribute of the child
is read silently -- the very hazard ADR-148 refused tokens for, now
admitted for functions. The spec would have to say, and the manual
teach, that `node` in the assembly's body is not the assembly. OpenArm
would work under (b) only because it passes `left` to every node, which
is a coincidence of this project, not a rule. A refusal naming the
mate could be arranged, but the surprise cannot be worded away.

### 2. When: as the assembly realizes the moving child

The function is called in `ChildDeclaration.realize(values, owner)`, the
moment a site-declared joint's function is called (ADR-098): `owner` is
the realized assembly -- its parameters resolved, its `check()` run, its
joints and frames resolved, every child it declares before the moving
child already realized, not yet rendered. For an inherited mate it is
the realized subclass instance. The recommended order inside `realize`:
call and check the freedom's functions BEFORE the child is constructed,
so a refused result refuses before the child's subtree is built; then
construct the child; then cache the resolved arguments on it (decision
3). The child's constructor skips that joint in
`resolve_declared_joints`, exactly as it skips a site-declared joint.

**Deviation from the briefing,** which named "the frames resolver ...
at the owner's realization" that "computes the child's rest placement"
as the natural place. In the source the rest placement is composed at
the owner's RENDER: `apply_mates` runs from `assembly._rest` after the
author's `render()` returns, and re-runs under a legacy render. That is
too late and too often: a joint's arguments are read from the
instance's cache by binding (the range refusal), by the constraint and
relation range checks and by the running and clocked compilers, and a
binding need not wait for a render. Resolving at the child's realization
means nothing can read the arguments before they exist.

*Alternatives rejected.* **At the owner's render, in `apply_mates`**:
above. **Lazily, on the first `arguments` read**: the reader would
decide the timing, and the lazy path today resolves against the node
it is handed, the child. **At class creation**: there is no instance.

### 3. How the numbers reach the joint

`_install` builds the joint exactly as today, passing the freedom's
function through as the joint's `axis` or `range`, and marks the joint
as resolved at the child's realization whenever the freedom states a
function (`installed_by` already names the mate). At realization each
argument is resolved against the node whose class body wrote it: the
freedom's function against the assembly, and what the moving frame
supplies (its declared `z` or `at`, numbers, tokens or a function of the
CHILD) against the child, as today. The results then go through the
joint's own resolution -- normalization and snapping of the axis, its
zero-length refusal, the range's bound handling and order check -- and
are cached under the child's `_joint_arguments[<mate>]`, the slot every
reader already uses. The recommended implementation substitutes the
assembly's results for the functions and runs `Joint.resolve` against
the child, so the joint's rules are applied once, in one place.

A mate whose freedom states no function takes today's path unchanged:
resolved in the child's constructor, with today's messages, and today's
`_install` objects (the frame's declared `z` and `at` passed through as
the same objects).

`Joint.arguments`' lazy path (a cache miss) must refuse a joint marked
this way, naming the mate and its assembly, rather than resolve it
against the child; a cache miss can only mean the specialized class was
constructed outside its declaration.

### 4. What is checked, and where

**At class creation** (`_check_freedom`, `TypeError`, as today): a
function `axis` and a function `range` (the whole range) are accepted
-- a function being `callable` and not a parameter token or formula
(`hasattr(value, 'dimension')` is tested first, as `_check_stated`
already orders it). Still refused, each naming the class, the mate and
the argument: a token or formula in `axis`, `at` or the range (reason
unchanged: it would resolve by name against the child); a function
`at` (reason: a stated anchor is three numbers in this version; OpenArm
needs none, decision 5); a `Bound` with reads; a numeric axis of zero
length.

**At realization** (`ParameterError`, the error every realization-time
argument refusal raises): the function's result is checked by the rules
the numbers are checked by at class creation -- `_check_stated`'s
reasons for an `axis` (three components, each an `int` or `float` and
not a `bool`, no token, formula or function, non-zero length) and
`_check_freedom`'s range rule for a `range` (a pair, bounds numbers,
`None`, functions of the coordinate or a `Bound` without reads) --
naming the ASSEMBLY's class, the mate and the argument, quoting the
result and saying it is what the function returned for that assembly. A
function that raises is refused the same way, quoting the exception, as
`resolved_vector` quotes one. Factor the reasons out of `_check_stated`
and `_check_freedom` so both moments word them once. What the joint's
own resolution refuses after that (a reversed numeric range) is refused
as it is for the numbers form today.

### 5. What was struck, and why

- **A function `at`.** Every OpenArm joint turns about the child's own
  origin, which is the moving `Frame()`'s origin, the default a freedom
  that leaves `at` out already takes. Admitting it later is one condition
  at the same seam, with evidence. The asymmetry ("axis may be a
  function, at may not") is stated in the refusal.
- **Tokens and formulas.** Under decision 1 they could resolve against
  the assembly at the same seam, but no project needs one; the
  class-creation refusal and its reason stay.
- **A resolved read.** See decision 6.
- **A function `unit`.** The mate's coordinate carries the unit from
  class creation; nothing varies it.

### 6. The reads

`declared_mates(cls)[name].freedom.axis` and `.range` read what was
written: for a function, the function object itself. The spec sentence
that the mate's line is "readable from these reads and the moving
child's resolved frames alone" holds only for a freedom stating numbers
or nothing; for a function, the line on a built machine is what the
function returned for that assembly, and no documented read gives it in
this version. The installed joint's documented reads do not either:
`declared_joints` is class-level and `Joint.arguments(node)` is not in
the reference. OpenArm's tests read no resolved joint argument
(`evidence/finding.md` §8), so nothing is added; the framework's tests
read `Joint.arguments(child)` as its existing mate tests already do.

### 7. What does not change

The rest placement (`apply_mates`, `_placement`): the frames alone fix
it. The document, serializer, export, viewer and mechanics: a function
axis reaches the document only as the axis of the joint's ordinary
operations, per instance, like any class-declared joint's function
today. Identity: the function is not a declaration and keys nothing. The
mate's coordinate, wiring, unbound rule and single binder. Every other
mate refusal and deferral.

### 8. ADR

**ADR-150 (NODE): a mate's freedom may be a function of the assembly
that states it** -- amends ADR-147 ("a whole-range callable ... is
refused, because the installed joint resolves its range against the
CHILD") and ADR-148 ("A stated line is three numbers"): the `axis` and
the `range` may each be one function, called once with the realized
assembly as it realizes the moving child, its result checked as the
numbers are and read in the child's own frame; `at`, tokens and formulas
unchanged. Records rejected alternatives: (b) the child; resolution at
render; lazy resolution; a function `at` without evidence. ADR-147 and
ADR-148 gain *Amended by* lines; the README index all three. Extracted
after implementation confirms the design, per the framework-change
skill.

## Risks / Trade-offs

- **Two resolution moments for mate joints.** A mate stating a function
  resolves at the child's realization; one stating numbers, in the
  child's constructor. -> Chosen so every existing mate is unchanged in
  bytes and messages; the marker is set in one place (`_install`) and
  read in two (`resolve_declared_joints`, `realize`). A later cycle may
  unify them with evidence.
- **A missed skip is silent for OpenArm.** If the child's constructor
  resolved the marked joint, the function would be called with the
  child, and OpenArm would still work because the child carries `left`
  too. -> The fixtures discriminate: a child that lacks the assembly's
  attribute, and a child whose same-named parameter holds a different
  value (tasks 2.4).
- **A function may read children declared after the moving child**,
  which are not realized yet. -> Refused at realization quoting the
  `AttributeError`; the state the function sees is the one ADR-098
  documents for a site function, and the manual says so in one clause.
- **Asymmetric line** (`axis` a function, `at` not). -> Stated in the
  refusal; widened with evidence.
- **Existing tests inverted.** `RefusalTest.test_a_stated_line_is_numbers`
  (its `callable_axis` case) and
  `RefusalTest.test_a_freedom_range_that_depends_on_a_declarer` (its
  `whole` case) assert the removed refusals; they are narrowed and the
  acceptance tests run red first, not deleted silently.

## Migration Plan

No framework user migrates: every existing mate installs the same joint.
OpenArm follows later in its own repository, by a separate agent (tasks
§6), compared pose for pose at maximum deviation 0 against its `main`.
Rollback is reverting the framework commits.

## Open Questions

- The four scope questions in `proposal.md`; the artifacts follow the
  recommendations.
