# ADR-071: Determined sources retain their motion path

**Status:** Accepted

**Date:** 2026-09-22

**Amends:** ADR-058 endpoint handoff and unconditional searched block stops;
ADR-061 static-only shape classification. Preserves ADR-057 retained walks,
ADR-060 point-evaluation arithmetic, ADR-067 Play and ADR-070 contact proof.

**Change:** [preserve-running-source-timing](../../../openspec/changes/archive/2026-09-22-preserve-running-source-timing/)

## Context

The producer's Curta reduction exposes the same browser error: the frozen
carry gives 2 rather than 3.5 when a predecessor's stroke then dwell is
replaced by its endpoint ramp. Later result stations introduce cuts which
change the artificial ramp and therefore the earlier carry.

## Decision

Store demanded propagation-local motion pieces with pure memoized evaluation
and timing-preserving restriction. Compose ordinary dependencies and selected
blocks from those paths, holding inactive inputs and using the existing
floating-point evaluator and retained walk. Classify the active substituted
DAG against actual paths, solve certified affine pieces and search curves.
Range/contact probes share the committed path, with fresh prefix replay when
unavailable. Preserve clearance-aware Play replay and independent time drives.
Inherited boundaries retain crossing ownership; law-wide crossing limits
remain effective across pieces, even without history recording.

## Alternatives and consequences

Changing commands, adding microsteps or dropping later selectors would mask
the defect. A second numerical evaluator or coupled solver is unnecessary.
Weak-map metadata and per-motion caches expire with the propagation rather
than retaining documents. Old exact affine controls retain their result;
the carriage control costs 6.16% more expression evaluations for endpoints.
General curves retain the bounded-search limitations. Producer-owned fixtures
pin full banks, commands, crossings, stops, restoration and partitions;
unchanged six/seven/eleven and constrained Curta exports pass. Browser worker
and fallback captures are arithmetic evidence, not complete CAD acceptance.
