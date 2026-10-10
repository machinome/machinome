# ADR-150: A Mate's Freedom May Be a Function of the Assembly That States It

**Status:** Accepted
**Amended by:** [ADR-153](ADR-153-mate-mechanical-contracts-resolve-the-generated-child-joint.md) — returned range Bounds may read the declaring assembly; factory timing and the child's geometric frame remain unchanged
**Date:** 2026-09-26
**Amends:** [ADR-147](ADR-147-a-mate-compiles-to-a-rest-placement-a-joint-and-a-coordinate.md) ("a whole-range callable ... is refused, because the installed joint resolves its range against the CHILD"), [ADR-148](ADR-148-a-mates-freedom-may-state-its-own-line.md) ("A stated line is three numbers")
**Extends:** [ADR-097](ADR-097-a-joint-is-stated-in-the-frame-of-whoever-declares-it.md) (a function is called with the node whose class body wrote it), [ADR-098](ADR-098-a-joint-may-be-declared-where-a-child-is-placed.md) (called at the moment, and in the state, a site-declared joint's function is)
**OpenSpec change:** `state-the-freedom-per-instance`
**Ratified:** 26 September 2026, by the orchestrator's review under the review gate the pilot delegated on 7 September 2026, with the proposal's four scope questions at their recommendations: the function receives the assembly, `at` stays numbers, no read of the resolved values, a new ADR amending ADR-147 and ADR-148.

## Context

The originating project is two mirrored seven-joint arms, each ending
in a pinch gripper, reconstructed from a URDF: one class per joint,
instantiated once per side, with a `left` flag handed down every
declaration. Per side the URDF states a different joint origin, a
different axis (two arm joints flip sign) and a different range (two
arm joints and both fingers). The project had settled, when ADR-097
moved its joints into their own frames, that handedness is a fact of
the realized node, not of the class, and read each argument as
`Revolute(axis=lambda node: ..., range=lambda node: ...)`.

Moving onto frames and mates (ADR-147), the fixed frame is served: a
frame's function is called with its declarer, the parent that holds
`left`. The freedom was not: ADR-148 refused a function `axis`, and
ADR-147 a function `range`, because the joint the mate installs is a
class joint of the moving child, resolved in the child's own
constructor, which would call a function written in the assembly with
the child. Without a change the only migration splits the whole chain
by side, sixteen stating classes and two grippers for eight and one,
and gives the per-instance handedness up. ADR-148 foresaw it: "one that
does gets a resolver-side resolution then, together with the range."

## Decision

**A mate's freedom may state its `axis` and its `range`, each as a
whole, as one function of one argument** -- a callable that is not a
parameter token, a formula or a `Bound` -- beside the numbers they take
already.

**The function is called with the realized ASSEMBLY that states the
mate**, the node whose class body it is written in, and never with the
moving child. Every function the framework calls receives the realized
node whose class body wrote it: a frame's its declarer, a class joint's
its declarer (ADR-097), a site-declared joint's the declaring parent
(ADR-098). For an inherited mate it is the realized subclass instance.
Who a function is called with and which frame its numbers are read in
are separate facts: the result is read in the moving child's own rest
frame, as numbers written in the freedom are (ADR-148).

**It is called once per realized assembly, when the assembly realizes
the moving child, before the child is constructed** --
`ChildDeclaration.realize`, the moment and the state ADR-098 gives a
site-declared joint's function: the assembly's parameters resolved, its
`check()` run, its joints and frames resolved, every child it declares
before the moving child realized, nothing rendered. Binding, rendering,
reading and exporting do not call it again, and it enters no identity.

**Its result is taken as the numbers are.** It is checked there by the
rules the numbers are checked by at class creation, worded once for both
moments -- an `axis` three `int` or `float` values, not `bool`, of
non-zero length; a `range` a pair whose bounds are numbers, `None`,
functions of the coordinate's own value or a `Bound` reading no other
coordinate -- and a result that is not, or a function that raises, is a
`ParameterError` naming the ASSEMBLY's class, the mate and the argument
and quoting what it returned or raised. The joint is then resolved
against the child by `Joint.resolve` with the results in the functions'
place, so the joint's own rules -- normalizing and snapping the axis,
ordering a numeric range -- apply once, in one place, and what the
moving frame supplies (its declared `z` or `at`) still resolves against
the child. The result is cached in the child's `_joint_arguments`, the
slot every reader already uses.

**The mechanism is a mark, set in one place and read in two.**
`_install` builds the joint exactly as before, the function passed
through, and marks it `_resolved_by_mate` when the freedom states a
function. `resolve_declared_joints` skips a marked joint, as it skips a
site-declared one; `Joint.arguments`' lazy path refuses one, naming the
mate and its assembly, rather than resolve it against the child. A mate
whose freedom states numbers or nothing installs the same unmarked
joint, on the same path, with the same messages and the same bytes.

**Unchanged:** a stated `at` is three numbers, and a function `at` is
refused at class creation with that reason; tokens and formulas
anywhere in a freedom, and a `Bound` with reads, are refused for the
reasons ADR-147 and ADR-148 give; the frames alone fix the rest
placement; the document, serializer, viewer and mechanics package.
`declared_mates(cls)[name].freedom.axis` and `.range` read the function
as written; no documented read gives the values it returned.

## Rejected alternatives

- **The moving child as the function's argument.** Zero new machinery:
  drop the two refusals and the installed class joint calls the
  function in the child's constructor. But the function is written in
  one class and called with an instance of another, the one place in
  the framework where that would happen: an assembly-only attribute
  fails with an `AttributeError` about a class the author did not write
  it in, and a same-named attribute of the child is read silently -- the
  hazard ADR-148 refused tokens for. The originating project would work
  only because it passes `left` to every node. The fixtures that pin
  this decision are a child with no `left` and a child whose own `left`
  says the opposite side.
- **Resolution at the assembly's render**, in `apply_mates`: the rest
  placement is composed there, but a joint's arguments are read by
  binding, by the range checks and by the running and clocked compilers,
  none of which waits for a render; and a legacy render re-runs.
- **Lazy resolution**, on the first `arguments` read: the reader would
  decide the timing, and the lazy path resolves against the node it is
  handed, the child.
- **A function `at`** without a project that needs one: every joint of
  the originating project turns about the child's own origin, the
  default a freedom leaving `at` out takes. Admitting it later is one
  condition at the same seam, with evidence.

## Consequences

- A handed design states each joint once, as a mate whose fixed frame,
  axis and range are functions of the side, with one class per joint;
  the originating project's hand placements go in its own repository's
  follow-up.
- Two resolution moments for a mate's joint: at the child's realization
  when its freedom states a function, in the child's constructor
  otherwise. Chosen so every existing mate is unchanged in bytes and
  messages; a later cycle may unify them with evidence.
- The line of a mate whose axis is a function is no longer readable
  from the class reads and the moving child's resolved frames alone;
  the read returns the function.
- A child built outside the assembly that declares it cannot resolve
  the joint and is refused by the mate's name -- the child as the
  assembly realizes it, the class carrying the mate's joint; the plain
  class it was written as carries no joint and builds alone as before
  (clarified 2026-09-26 from OpenArm's validation).
- The line is asymmetric: `axis` may be a function, `at` may not. The
  refusal says so.
