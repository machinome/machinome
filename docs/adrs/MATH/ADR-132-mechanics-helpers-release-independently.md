# ADR-132: Mechanics helpers release independently

**Status:** Accepted
**Date:** 2026-09-20
**Supersedes:** ADR-076's framework ownership and import path
**Preserves:** ADR-022 expression semantics and ADR-089 project-supplied laws

## Context

Kossel and V8 use the twelve mechanism formulas as arithmetic inside their
motion laws. The maintainer previously selected independent development of
these helpers. Commits `b4eb460` (extraction) and `08ba6a9` (opt-in extra)
completed that work on branches that did not reach framework main. The
independent mechanics package was founded, but framework main still bundled
the formulas when preparing 0.7. The pilot explicitly directed completion of
the existing extraction during release maintenance.

## Decision

machinome-mechanics owns the twelve formulas, their conventions, tests and
behavioral specification, imported as `machinome_mechanics`. It depends on
machinome >=0.7.0 and uses `machinome.math`. Framework math and motion work
without it. The default framework installation has no mechanics dependency;
the existing `mechanics` extra installs it. No compatibility shim or re-export
of `machinome.mechanisms` is retained.

This completes the original extraction under the accepted ADR-130 rename.
The old branch numbered its extraction ADR 101; main already uses 101 for
motion sharing, so this record uses 132 rather than overwriting that decision.

## Alternatives and consequences

Keeping both copies would split ownership and let formulas drift. A shim would
retain a framework API for independently owned helpers. Both are rejected, as
in the original extraction. Removing the math dependency would invent a second
expression provider and was explicitly excluded from that work.

Projects using the unreleased helper import change it to `machinome_mechanics`.
The equations and signatures do not change. Formula and motion-integration
tests belong to mechanics; the framework keeps distribution-boundary tests.
Versions 0.7.0 / 0.2.0 / 0.1.0 remain pending publication.

Release evidence: `workflow/archive/release-0.7-2026-09-20/README.md`.
