# ADR-146: An Inherited Control Follows a Compatible Child Replacement

**Status:** Accepted
**Date:** 2026-09-23
**Amends:** [ADR-117](ADR-117-a-control-may-name-the-freedom-it-means.md) only for an explicitly preserved inherited control across a child replacement
**OpenSpec change:** `inherit-controls-through-replaced-child`

## Context

The Curta's `LoopOperatingTrial` specializes the inherited `carriage` and
adds a loop deployment control. It explicitly preserves
`OperatingCurta.controls`, but those existing controls hold references to
the ancestor's `carriage` declaration. The subclass's child at that same
path is a different declaration, so exact object-identity validation
refused `shift carriage` at class definition even though the effective
tree contains a compatible carriage and the selected joint can already
be resolved to its effective declaration.

An explicit subclass `controls` mapping replaces the inherited mapping.
Silently merging tables would change the meaning of `controls = {}` and
does not solve references copied into a table the author intentionally
extends. Accepting any same-spelled child would admit foreign controls
that the declaration contract expressly refuses.

## Decision

Keep explicit table replacement. When an entry is the *same control
object under the same name* in a validated ancestor table, its original
first child belongs to that ancestor, and the subclass declares a
subclass-compatible child at that name, class validation may carry the
part and explicit coordinate paths into the effective tree. All other
controls still require exact current declaration identity. In particular,
a newly constructed control borrowing the ancestor's child, or a control
borrowing a foreign same-name child, is refused.

At compilation the part and selected joint are resolved on the realized
replacement, not on the ancestor. The existing joint ancestry, bank
ownership, domain and input-reachability tests decide whether the gesture
still exists there. A missing nested path is a named control refusal.
The control publishes no new field, and a control still changes neither
the running program nor its identity.

## Consequences

The Curta can preserve its 25 hand controls and add the loop control
without copying their definitions. Incompatible replacements and stale
paths fail closed. There is no new author syntax or producer wire: a
version-13 document carries the same control schema. The originating
document exposed a separate viewer refusal of two distinct selected
Turn joints on one visible leaf; that consumer correction belongs to
its own viewer-owned cycle rather than this producer decision.
