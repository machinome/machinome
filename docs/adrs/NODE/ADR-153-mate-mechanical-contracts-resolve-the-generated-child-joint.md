# ADR-153: Mate Mechanical Contracts Resolve the Generated Child Joint

**Status:** Accepted
**Extended by:** [ADR-154](ADR-154-a-mate-may-reference-an-existing-child-joint.md) — referenced-joint handles name the original child endpoint in every reference context and preserve its original Bound scope
**Date:** 2026-09-27
**Amends:** [ADR-147](ADR-147-a-mate-compiles-to-a-rest-placement-a-joint-and-a-coordinate.md), [ADR-150](ADR-150-a-mates-freedom-may-be-a-function-of-the-assembly-that-states-it.md) — their refusal of Bound reads in a mate freedom
**Extends:** [ADR-113](ADR-113-a-bound-may-read-other-coordinates.md), [ADR-117](ADR-117-a-control-may-name-the-freedom-it-means.md), [ADR-134](ADR-134-ancestors-add-constraints-without-replacing-joints.md) — mechanical references may name moving mates
**Preserves:** ADR-097, ADR-148, ADR-151, ADR-152 — the child's geometric frame, line, freedom kind and rigid-mate boundary
**OpenSpec change:** `mates-in-mechanical-contracts`
([change record](../../../openspec/changes/archive/2026-09-27-mates-in-mechanical-contracts/))

## Context

Curta-Type-I-3x's crank at project commit `fb5505d` carries a pawl-dependent
Bound, independent lift, ancestor-installed locking obstacles and separately
selected turn/lift controls. A mate could install its turn joint and preserve
its bank identity, but those contracts could not name the mate: freedom ranges
refused Bound reads, constraints required descendant Joint paths, and explicit
controls rejected a Mate because it is deliberately a Coordinate, not a Joint.

The existing generated child joint is already the physical coordinate the
running program banks. The assembly mate port reaches it through the existing
identity wiring. Extending the contracts requires resolving that physical
endpoint, not adding another retained value.

## Decision

Bound reads, additive constraints and explicit Turn/Slide/Button selections
normalize a bare or descendant-path moving Mate to its generated child joint.
The shared internal `motion.mechanical` resolver is confined to those contexts;
ordinary relations, derived coordinates, wirings and author bindings retain
the assembly mate port. Mate remains a Coordinate and never becomes a Joint of
its assembly. Constraints may target an own moving mate because the physical
target is its child; an ordinary own Joint remains outside the descendant-only
constraint contract. Rigid mates receive the existing named no-coordinate
refusal.

A generated joint retains `installed_by` provenance. Its Bound reads belong
to the declaring assembly, while its axis and anchor continue to resolve in
the child's own rest frame. No site-joint flag or geometric carry is used.
Static Bounds are checked after mate installation. Whole-range functions keep
their once-per-instance pre-child timing; returned Bounds are checked when the
pair becomes available and read values remain unresolved. Evaluation consumes
the actual resolved span and caches endpoints per child instance, after the
parent link and complete sibling tree exist.

Written reference ownership is checked before inherited paths are rewalked.
A reference from an actual declaring class or base may follow a compatible
effective path; a foreign declaration with the same name cannot be redirected
into this tree. Self and duplicate checks compare canonical physical paths,
including mate/explicit generated-joint aliases and a node that infers its
single joint. Incompatible or missing effective references are refused.
Existing restrictions on replacing the child a mate places remain unchanged.

The current running, clocked and untimed evaluators consume the same joint and
contributions. No solver branch, extra bank entry, field or document version
is introduced. Controls reuse the generated joint's actual posing node and
existing placement span, ancestry, kind, bank and input-reachability checks.

## Alternatives considered

- Make Mate a Joint: would enumerate and resolve it as a joint of the assembly
  and give an assembly port physical ownership it does not have.
- Rewrite ordinary coordinate references globally: would alter relation ends,
  wiring and author binding semantics beyond the missing contracts.
- Reuse the site-joint marker for assembly scope: would also carry geometric
  arguments through the child's placement and change the existing mate frame.
- Bank an assembly-port alias: would retain one physical value at two addresses.
- Resolve reads during child construction: cannot see a valid later sibling
  and risks leaking instance state into class-shared declarations.

## Consequences and evidence

The public vocabulary stays the existing Bound, constrain and coordinate=
forms. A project can replace a hand placement with a mate while retaining its
physical bank ids, original stop and separately selected freedoms. Effective
bound changes retain the existing program-identity consequences; selecting the
mate adds no program state.

The acceptance fixtures prove static and returned Bounds, late siblings,
independent inherited instances, compatible read replacements, own/nested mate
targets, both freedom kinds, explicit controls, canonical alias refusals and
rigid refusals. A compact ordinary-joint/mate twin agrees on stop, relief,
ancestor limit, independent lift, composed pose and snapshot replay. Existing
mate and non-mate pinned document tests remain green. This is representative
framework acceptance, not by itself a completed Curta migration; root-owned
caller validation and the separately owned Studio API companion are recorded
with the change's completion evidence.
