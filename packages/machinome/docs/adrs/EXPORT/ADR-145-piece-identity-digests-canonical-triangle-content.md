# ADR-145: Piece identity digests canonical triangle content, not raw bytes

**Status:** Accepted
**Date:** 2026-09-23
**Change:** `piece-identity-ci` (a focused conformance fix, recorded in
`workflow/warts.md`; no OpenSpec change)
**Amends:**
- [ADR-043: Content-Derived Printed-Piece Identity](ADR-043-content-derived-printed-piece-identity.md) — chooses its option 4
- [ADR-085: Persistent Piece Facts Behind a Verified Artifact Snapshot](ADR-085-persistent-piece-facts-behind-a-verified-artifact-snapshot.md) — the fact record's digest changes meaning, so its version moves to 2

## Context and Problem Statement

ADR-043 identified a printed piece by the sha256 of its STL's raw bytes and
rejected a canonical geometry hash as "strictly more work than byte hashing
for a failure not yet observed". Its risk section expected the only cost to be
an under-merge between different code paths.

The failure was then observed inside one code path. On GitHub Actions
(runs 35836399670 and 35849922652, `ubuntu-latest`, apt
`openscad=2021.01-6build4`) `tests/test_pieces.py` reported the two identical
bushing classes of `tests/pieces_project` as two pieces. Both render the same
SCAD text through the same binary, but OpenSCAD 2021.01 writes the resulting
triangles in a run-dependent facet order. In an `ubuntu:24.04` container with
the same package, thirty renders of one SCAD file by one command line gave two
distinct byte streams (15 and 15) with identical triangle sets; on the
maintainer's machine the order is stable for a given path but changes with the
length of the input path. The facets differ only in their order, their first
vertex and the sign of a zero in a stored normal.

The printed-pieces specification already required that a piece id "SHALL NOT
depend ... on the run that produced it". Raw-byte identity broke that
requirement whenever the backend's output order is not a function of its
input.

## Decision

A piece's full digest is the sha256 of a canonical encoding of the artifact's
**oriented triangle multiset**:

- binary STL is recognised by its exact length and read as float32 facets;
  ASCII STL is read from its `vertex` lines as float64; anything else keeps
  its raw bytes under a distinct domain prefix, so identity is still content
  and never a parameter key;
- the header, stored normals and attribute words are dropped, and `-0.0` is
  folded to `0.0`;
- vertices are indexed into a value-sorted table, every facet is rotated to
  its lexicographically least vertex cycle (rotated, never reflected, so
  winding and handedness remain content), and facets are sorted;
- the digest covers a versioned domain prefix, the table dtype, the table and
  the sorted index triples.

Coordinates are not quantised: two solids are one piece only when their
triangles are exactly equal, so no tolerance can merge different parts. The
public id stays the 12-hex prefix and the collision guard of ADR-085 is
unchanged. The private fact record keeps its `sha256` field, now holding the
canonical digest, and its version becomes 2, so every version-1 record, which
digested raw bytes, certifies nothing and is recomputed.

## Considered Options

1. **Canonical oriented-triangle digest** (chosen) — exact, order-free,
   orientation-preserving; one numpy pass per distinct artifact, and only
   when the fact record is missing or stale.
2. **Make OpenSCAD deterministic** — not in the framework's control; the
   order varies with the input path length and between identical
   invocations, apparently with the process memory layout, and other
   backends and imported STLs owe no ordering either.
3. **Mesh-invariant fingerprint** (ADR-043 option 3) — needs tolerances and
   can merge genuinely different shapes.

## Consequences

- The bushing pair, and any artifact pair differing only in encoding, is one
  piece on every machine; the CI failure is gone for the cause, not the
  symptom.
- Every existing piece id changes once, because the digest input changed.
  Ids are content hashes with no stability promise across framework releases,
  and each producer recomputes them; committed exports carry the ids of the
  release that made them until they are regenerated.
- A mesh written with different float precision (ASCII versus binary, or a
  re-tessellation) is still a different piece: identity follows the exact
  triangles, as before.

## Related

- Capability spec: `openspec/specs/printed-pieces/` (content defined as the
  oriented triangle multiset)
- Finding: `workflow/warts.md`, "Piece identity split by OpenSCAD facet order"
- Tests: `tests/test_pieces.py` (captured OpenSCAD pair, encoding and
  orientation cases), `tests/test_persistent_piece_facts.py`
