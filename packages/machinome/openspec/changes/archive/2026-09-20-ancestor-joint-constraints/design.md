## Context

The operating Curta has real nested joints in the crank, carry mechanism and
result transmission. Its source locking disc supplies a physical restraint
that their common ancestor can describe, but their separate placement owners
cannot. The latest main includes running-time drives (ADR-133); it still
refuses all three attempted nested routes in the project reproduction.

The pilot authorized this framework cycle and required Curta validation while
preserving the Studio tree. Framework source, records and commits belong in
the isolated framework worktree. Curta tests and measured mechanical limits
remain in Curta's repository. No viewer source belongs in this cycle.

## Goals / Non-Goals

**Goals:**

- A common ancestor can add a physical constraint to an existing scalar
  descendant joint, using actual retained coordinates as reads.
- Placement ownership, joint frame/order, declared geometry and tree/control
  paths remain unchanged. Another instance of the same class is unaffected.
- Existing limits remain effective. Additional constraints only narrow travel.
- Untimed inspection, running stops and clocked stops consume the same
  declaration with their established semantics and refusals.
- Produce red-first framework proof and a source-geometry Curta acceptance.

**Non-Goals:**

- General collision response, force simulation, a redesigned range solver,
  a different search tolerance, or detection of contacts narrower than the
  existing search can resolve.
- Constraint targets that are inputs, states, ordinary/derived ports, grouped
  ends, repeated broadcasts or a component of a multi-coordinate joint.
  Curta needs individually named scalar joints; no broader API is inferred.
- Upward paths, string paths, arbitrary mutation of child declarations,
  replacement of joints, copied state, or a second writer to retained motion.
- Completing every Curta lockout, clearing-loop fit or arithmetic demo.
- A new export format, viewer implementation, release or remote publication.

## Decisions

### 1. A checked descendant path states an additive constraint

Proposed public spelling, written in an assembly class body:

```python
main_drive.crank.turn.constrain(range=(None, Bound(
    closing_limit, reads=(transmission.result.ones.turn,))))
```

`closing_limit` is project-owned expression code, not framework geometry.
The `range` pair accepts the existing side vocabulary: `None`, numeric or
parameter-derived bounds, a one-argument own-coordinate expression, or
`Bound(expression, reads=(...))`. Structural numeric values resolve against
the assembly declaring the constraint. An entire callable range factory is
not introduced for this surface. A malformed pair or a wholly unbounded
`(None, None)` is refused; an empty numeric intersection is an error, not
permission to choose a writer.

Only a path to an explicit existing one-coordinate joint is accepted. The
statement records declaration metadata, never a coordinate value. It is
recorded in declaration order, like `drives`. Inherited constraints remain
additive; this surface introduces no removal or named-replacement operation.
Validate inherited paths against the
realized subclass as well as the written class: a subclass cannot silently
redirect a base constraint to a missing or incompatible joint.

The declaring assembly owns the constraint; the descendant still owns its
joint. No `Revolute` clone or dynamic class specialization is required for
this declaration. No body is reparented or moved into another coordinate
frame, and no author-facing coordinate is minted.

Alternatives:

- Reparent Curta's moving parts into one flat assembly: preserves existing
  API but destroys the requested assembly/inspection structure.
- Proxy port or dummy joint: either not banked or a fake mechanical state.
- Replace the descendant joint/range: would silently remove its own stops
  and can change its placement frame (ADR-098); rejected.
- Broaden ordinary `Bound` reads to escape its scope: obscures ownership and
  creates upward references; rejected.

This is an explicit amendment of ADR-113's rejection of a separately stated
bound. Its warning about competing range definitions is addressed by additive
intersection, not by last-writer precedence. Joint-site replacement remains
exactly ADR-098's existing operation and is not repurposed.

### 2. Each contribution keeps its own scope

Check the target and every read with the existing typed path machinery.
Check additionally that the target is a scalar joint, references remain in
the declarer's subtree, and no read resolves to the constrained coordinate
itself. The own coordinate is already the expression's first argument.
Retain the existing duplicate-read and unused-read refusals on each bound;
composition must not hide an invalid contribution behind a tighter limit.

Resolve contributions per instance after the declared tree can be linked,
before a compiled program or a completed enumeration judges that tree.
Keep their declaring instances explicitly. Never mutate class-level joint
metadata or reuse one instance's resolved endpoints for another.

Untimed checks run when the complete enumeration closes, after relations
have propagated. They evaluate every available contribution in its own
scope. A symbolic/unbound read defers that contribution only: a numeric
original range or another fully known constraint is still judged. Diagnostics
name the target, evaluated limit and scoped reads; failure must not depend
on sibling declaration order. Run-owned and clocked-request-owned values
retain their existing single-authority exemptions.

### 3. Intersect ranges before publication, retaining the existing solver

For each coordinate, gather its original range and scoped contributions.
Compile and validate each side independently through the existing bound
compiler. Resolve original `Bound` reads against the original joint declarer
and added reads against their constraint declarers.

The effective low side is the maximum of present low sides; the effective
high side is their minimum. `None` is absent, not a numeric infinity. Keep
one contribution verbatim when it is alone; use the existing expression
`min`/`max` vocabulary only when combining. The read-id list is the stable
deduplicated union of participating contributions, not a copied coordinate.
Do not permit a wider ancestor limit to relax a narrower native limit.

Publish the resulting ordinary span pair. Existing constraint construction
derives its sub-program and pushing inputs from those qualified reads. Own
coordinate arguments remain frozen at the committed tick/request start;
other reads follow the attempted motion. No run executor branch, new stop
type or new document version is required. A stop reports the actual target
coordinate and effective side, not an invented proxy. A precise source
constraint label need not become a new wire field.

The clocked compiler already consumes the same span compiler and will retain
its existing affine/piecewise-affine admission and curved-level refusals.
No compatibility promise is made for a mathematical level that the current
clocked solver already refuses.

ADR-133's independent time-drive admissions must still work when a descendant
constraint stops one of them: elapsed time and unrelated drives continue,
and resumption never catches up discarded motion.

### 4. Compatibility must be demonstrated, not assumed

The no-constraint path keeps the existing span compiler output and fast path.
Existing model documents and program identities must remain unchanged.
Effective changed limits must change identity and invalidate incompatible
snapshots. Fresh enumeration, construction, restore and rebuild must neither
drop nor duplicate constraints or alter the node/control paths.

Compare a nested constrained fixture's compiled publication and replay with
an equivalent existing range declaration. Run the installed viewer against
the actual published document, using only its public API, and verify a
pointer command stops with the same committed travel and tree. If that fails
because the viewer needs code changes, report a separate repository decision;
do not silently expand this cycle.

### 5. Curta is the empirical acceptance, not just a placeholder test

First preserve the existing failing action order as a red test: selector 3,
crank 120 degrees, withdraw selector to 0, then request 150 degrees. The
actual retained shaft is 189.6 degrees and the complete source bell overlaps
its upper lockout at the admitted endpoint today.

Use a Curta-owned diagnostic declaration on existing descendant joints,
leaving the operating tree and controls intact. Measure the complete bell's
first contact against the retained lockout at the relevant phase, validate
the local free/blocked bracket in both geometry kernels, and derive the
bounded-window expression from those measurements. The isolated disc's
125.335121..125.335169-degree bracket is starting evidence, not a hard-coded
whole-machine law. Test the actual crank request stopping on its free side,
unchanged held shaft phase, a relief/reverse request without backlog, and
snapshot/replay. Compare assembly and control paths before and after; inspect
pixels of the stopped real geometry.

The acceptance must state the phase and crank window actually validated.
It must not extrapolate a sampled boundary into a permanent whole-machine
crank cap or mark all operating restraints complete. If full integration
requires more mechanical evidence, keep this scoped diagnostic explicit and
continue that work in the operating-Curta roadmap after the framework cycle.

## Risks / Trade-offs

- Multiple stops on one coordinate add declaration complexity → define
  intersection explicitly and test native, ancestor and nested-ancestor
  limits together, including a wider ancestor and a reversed intersection.
- Instance/scope leakage → two identical branches with different reads and
  limits must keep independent state, shapes and compiled ids.
- A combined expression can alter rounding/order → validate each original
  bound before composing and compare stopped outcomes and replay under the
  existing tolerances; retain unchanged expressions on the single-side path.
- A late constraint could be absent at a pose check → validate the full
  enumeration boundary and restore/rebuild paths, not just `Sim.move`.
- Existing search may miss a narrow contact → retain its documented limits;
  use a measured Curta bracket and explicit timestep evidence, not a claim of
  continuous collision detection.
- Main may advance again → preserve the recorded base and stop for an
  integration decision if it changes; never silently rebase the cycle.

## Migration Plan

This is additive; existing callers require no migration. Curta opts into the
new declaration in its own evidence-backed increment. Complete the framework
two-commit cycle, sync and archive after tests, and extract an ADR amending
ADR-113 only after implementation confirms the decision. Integration remains
a separately verified fast-forward under pilot authority. Removing Curta's
opt-in restores the previous unsupported restraint, not a safe operating
machine, so retain the failing diagnostic in its history.

## Open Questions

The public spelling and additive composition were ratified on 2026-09-20.
No mechanical boundary beyond the measured Curta window is settled by this
document. Any need for a new runtime or viewer protocol returns to the pilot.
