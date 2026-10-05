# ADR-162: A Resolved Provider Declares the Contract Version It Implements

**Status:** Accepted; the constants named per role in one module, the B-rep contract 2, amended 2026-10-05 by [ADR-180](ADR-180-the-engines-are-named-for-the-representation-each-consumes.md)
**Date:** 2026-10-03
**Change:** [`exact-engine`](../../../openspec/changes/archive/2026-10-03-exact-engine/)
**Related to:**
- [ADR-161: The core holds no kernel code](ADR-161-the-core-holds-no-kernel-code.md) — the first seam to check a declaration
- [EXPORT/ADR-068: Optional viewer package behind a process boundary](../EXPORT/ADR-068-optional-viewer-package-behind-a-process-boundary.md) — the viewer's declared API version, the pattern this follows

## Context and Problem Statement

The lean-core campaign moves kernels out of the core into packages the core
resolves through seams (`workflow/ongoing/lean-core.md`, "The seams"). A
seam that imports a provider by name trusts that the module it finds offers
the operations it calls, with the meaning it expects. Once the provider is a
separately installed package, the two can drift: a newer engine with an
older core, or the reverse. The package standard (section 1.2) asks every
provider to declare the contract it implements, and the core to check it.

## Decision Drivers

- A mismatch must fail at resolve time, before any operation runs, naming
  what each side speaks.
- The check must cost nothing a correct install notices.
- The declaration must not be computed from the core's own, or it checks
  nothing.

## Considered Options

1. **An integer the provider states, compared by equality at resolve time**
   (chosen)
2. A version range the core accepts
3. A per-operation conformance probe at resolve time

## Decision Outcome

The seam module declares `CONTRACT`, the integer contract version the core
speaks, beside the Protocols naming the operations that version comprises.
The provider declares `CONTRACT` as its own integer literal. When the seam
resolves the provider it reads `getattr(provider, 'CONTRACT', None)`; unless
it equals the core's, both `exact_engine()` and `require_exact_engine()`
raise one error naming the core's version, the provider's (or that it
declares none) and the provider module, and no operation runs. The refusal
is not cached, so it is raised at every ask.

Equality, not a range: the engine is numbered with the framework (the plan's
D7) and a contract change bumps both. In this cycle the engine ships inside
the core, so a mismatch is exercised only by stub providers in tests; at the
cut the same integer is also declared in the package metadata the standard
asks for, and the engine package's dependency pin on the core guards a
project importing it directly, which bypasses the seam.

This is the pattern the `Svg` reducer's seam and `import-step`'s will follow
when their packages are cut.

## Consequences

- A contract change is a deliberate act on both sides: the core's `CONTRACT`
  and the provider's literal, in one change.
- A conformance test checks that every Protocol member exists on the
  provider as a function it defines, and that the provider's `CONTRACT` is
  an integer literal.

## References

- `machinome/exact_engine.py` — `CONTRACT`, `ExactEngineIncompatible`,
  `exact_engine()`
- `machinome/occt/engine.py` — `CONTRACT = 1`
- `tests/test_exact_engine_seam.py`, `tests/test_occt_engine.py`
