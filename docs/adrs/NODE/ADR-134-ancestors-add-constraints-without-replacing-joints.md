# ADR-134: Ancestors Add Constraints Without Replacing Joints

**Status:** Accepted
**Date:** 2026-09-20
**Amends:** ADR-113's rejection of a separately stated bound
**Depends on:** ADR-061, ADR-098, ADR-108, ADR-109, ADR-113, ADR-126
**Cites:** ADR-110, ADR-111, ADR-133
**OpenSpec change:** `ancestor-joint-constraints`
([archived record](../../../openspec/changes/archive/2026-09-20-ancestor-joint-constraints/))

## Context

Operating Curta's crank and retained result shafts belong to different nested
mechanical assemblies. Withdrawing a selector mid-turn leaves a shaft where
the source bell's closing disc can strike its lockout. The common ancestor
can name both actual joints, but a bound declared beside the crank cannot
read out of its subtree. Reparenting the parts would dismantle the established
Studio tree; a plain relay port is not retained state. The existing flat
`Bound` positive control works. This is missing composition, not a new solver.

The pilot ratified the declaration, additive intersection, unchanged tree and
publication, and real Curta acceptance before implementation. The plan and
evidence distinguish a measured local diagnostic from whole-Curta completion.

## Decision

An assembly class body may state
`path.to.joint.constrain(range=(lo, hi))` on an explicit scalar descendant
joint. Each side uses the existing bound vocabulary; structural values resolve
in the declaring ancestor. Entire range factories and wholly unbounded pairs
are refused. Reads use typed declaration references within that ancestor's
subtree; the implicit first argument is the target's own coordinate.

Constraints are additive, including through inheritance. No named override,
removal or joint replacement is introduced. Each instance resolves its own
contributions and scopes. The original joint still alone owns its coordinate,
frame, placement order and geometry. Inherited paths are checked again against
the actual class; missing or incompatible targets fail instead of disappearing.

Untimed enumeration judges each available contribution at its close. An
unknown read defers only that contribution. Running and clocked ownership
exemptions remain unchanged. Compilation validates each bound independently,
then intersects present lower sides with `max` and upper sides with `min`,
using the existing expression vocabulary and stable union of qualified reads.
An invalid hidden contribution or empty numeric intersection is refused.

The compiled result is an ordinary span on the existing coordinate. Existing
running and clocked executors, including own-coordinate freezing, moving-read
restraints, supported-level refusals, time-drive admissions and replay, need
no new branch. No wire field, document version or viewer code is added. The
no-contribution compiler path is preserved. Changed effective limits change
program identity; they do not change part identity or control paths.

## Alternatives considered

- Flatten Curta's ownership: changes the established mechanical/educational
  tree, controls and relations to accommodate a declaration limitation.
- Relay the shaft into a port or fake joint: respectively unbanked derived
  state or invented mechanical state, not the real retained shaft.
- Replace the target joint: removes existing stops and risks changing its
  frame; ADR-098 remains a separate, deliberately replacing operation.
- Let ordinary `Bound` reads escape their declarer's scope: obscures ownership
  and introduces upward references instead of naming the shared ancestor.

## Consequences

Physical installation limits can be stated where the interacting parts are
known, without rebuilding their ownership. ADR-113's competing-range concern
is settled by intersection, never precedence. Multiple contributions add
metadata and scope validation, and still inherit the existing solvers' search
and expression limits. This is not collision response: projects remain
responsible for measuring and validating their mechanical bound functions.
