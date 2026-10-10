# ADR-164: The Loaded-Shape Cache Keys on the Artifact's Observation

**Status:** Accepted
**Date:** 2026-10-03
**Change:** [`leaf-contract`](../../../openspec/changes/archive/2026-10-03-leaf-contract/)
**Amends:**
- [ADR-044: Derived exact-geometry capability](ADR-044-derived-exact-geometry-capability.md) — its in-memory shape cache keyed on `(path, mtime)`
**Related to:**
- [ADR-006: Mtime-based STL caching strategy](ADR-006-mtime-based-stl-caching-strategy.md) — why every artifact carries its source's mtime
- [ADR-028: Cached base meshes and single-matrix world composition](ADR-028-cached-base-meshes-and-single-matrix-world-composition.md) — the base-mesh cache, already keyed on the artifact's observation
- [ADR-081: Per-contributor metadata guards aggregate mtime currency](ADR-081-per-contributor-metadata-guards-aggregate-mtime-currency.md) — the same metadata trusted for sources
- [TEST-FRAMEWORK/ADR-156: A decided verdict outlives the run](../TEST-FRAMEWORK/ADR-156-a-decided-verdict-outlives-the-run.md) — the verdict memo and store keyed on a held shape's identity
- [ADR-163: The leaf bases are declared extension points](ADR-163-the-leaf-bases-are-declared-extension-points.md) — the contract that relies on this

## Context and Problem Statement

`exact_cache.cached_shape(brep_file)` kept one loaded shape per
`(brep_file, os.path.getmtime(brep_file))`. Every exact artifact is stamped
with its node's source `mtime_ns` (ADR-006), so a `.brep` replaced while no
tracked source changed carries the stamp of the file it replaced and is the
same key: the old shape is served for the new file. That happens whenever
something beyond the tracked files decides a leaf's geometry. machinome-freecad's
leaf is the case: its native recipe, what FreeCAD made of the document, can
change a BREP with no tracked file moving, and the adapter called the private
`_evict` from its own `materialize()` to work around it. A declared
`source_recipe` (ADR-163) makes the case general. A public eviction call
would make every subclass that replaces an artifact responsible for knowing
to call it.

## Decision Drivers

- No subclass may need to evict, invalidate or reset a core cache.
- The key is taken on every `shape()` of a current leaf, so it must stay
  about as cheap as one `stat`.
- The verdict store's persistent identities (ADR-156) must not change.

## Considered Options

1. **Key on the artifact's observation from one `stat`**: device, inode,
   size, mtime and ctime (chosen)
2. Publish `evict(path)` for subclasses
3. Stamp artifacts with the publication time
4. Key on a content digest of the `.brep`
5. Key on the full `observe_artifact` per request

## Decision Outcome

`cached_shape` keys on `(brep_file, (st_dev, st_ino, st_size, st_mtime_ns,
st_ctime_ns))` from one `os.stat`, the metadata fields of
`ArtifactObservation` and of ADR-081's source observation. A miss evicts
every entry held for the path -- the shape, its identity, bounds, face boxes
and placements -- and loads through the engine as before, the full
observation still taken before and after the read and recorded as the load
observation only when the two agree.

Every artifact the core publishes is written to a new temporary file in its
directory while the previous artifact still exists, then renamed into place,
so a replacement has a different inode, and the rename sets its ctime: the
replacement is a different key even under an equal stamp. Measured on 3
October 2026 with the bench's own publisher: two publications of different
bytes under one stamp gave equal float-mtime keys and unequal observations
on virtiofs and on ext4, and 200 back-to-back replacements on virtiofs gave
no equal observation. One `stat` cost 3.9 µs and the full observation
184-195 µs on a 17-deep virtiofs path, so option 5's correctness at about
fifty times the cost was not needed. `_evict` stays private and no public
eviction is added.

`shape_identity(shape)` still returns the cache key of a held shape, now
`(path, metadata)`, and the in-process verdict memo keys on it. The
persistent identity reads only the path and the recorded load observation,
so the verdict store's keys are unchanged (its stamp digests the package
source and starts afresh once, as after every framework change).

Option 2 was rejected as the Liskov violation the first campaign cycle's
review named, made public; option 3 breaks ADR-006's mtime equality and every
artifact's currency; option 4 reads every byte per request.

## Consequences

- A `.brep` replaced by the core's publication is never served stale, and
  nothing outside the cache evicts anything.
- The one case the key cannot see is an in-place rewrite of an artifact, by
  something other than the core's publication, within one timestamp tick of
  a load, with equal size and mtime; on ext4 an in-place `shutil.copy2`
  keeps the inode and, within a tick, the ctime. The leaf contract
  publishes only by rename, which rules it out; the FreeCAD adapter's
  rollback rewrites in place but restores bytes no reader loaded in between,
  and is recorded as a reach to settle at its retarget.
- Two tests that asserted the old key's shape, `(path, 2.0)`, assert the
  surviving key's path and `st_mtime_ns` instead, and one verdict-store test
  that relied on the old key serving a replaced file now holds `stat`'s
  answer to reach the same in-place case.

## References

- `machinome/exact_cache.py` — `_metadata`, `cached_shape`
- `tests/test_shape_cache_observation.py`, `tests/test_exact_geometry.py`,
  `tests/test_verdict_store.py`
- `openspec/specs/exact-geometry/spec.md` — "Exact geometry is persisted and
  reloaded"
