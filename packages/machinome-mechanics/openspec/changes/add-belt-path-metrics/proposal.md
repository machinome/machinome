## Why

Prusa3-vanilla, Kossel, Metamaquina2 and Hangprinter independently compute the
same closed pitch path's spans, wrap arcs, total length and element stations.
Thor separately computes length and wraps; extracting the shared measurement
removes duplicated mechanics while preserving project turn markers and phase.

## What Changes

- Add one public `belt_path_metrics(centres, radii, senses=None)` helper for
  an ordered closed route in a common XY plane, using existing tangent senses.
- Return spans, circle-indexed wrap angles and arc lengths, traversal-ordered
  stations and total length, including deferred coordinate/radius expressions.
- Migrate real consumers with Sol agents and compare independent pre-refactor
  measurements, affected CAD contracts and snapshots before integrating.
- Keep zero-wrap/full-turn legacy choices, pitch fitting, routing and diagnostic
  guards in project adapters. No belt geometry, object schema or topology solver.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: Closed directed belt path measurements and explicit indexing.

## Impact

Independent mechanics package: belts module, flat export, tests, reference
documentation and distribution smoke. Separate consumer commits in the named
projects. No framework, viewer or molejo changes and no new dependency.
Pilot's 2026-09-20 autonomous-cycle authority replaces per-cycle ratification;
at least two distinct project consumers must validate before archival.
