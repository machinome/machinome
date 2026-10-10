## Context

Curta Type I at project `a139fe0` uses the unchanged STEP sphere (R3.75 mm) and its fitted native frame. At radial 2.213142830078919 mm and Z offsets −0.2 and +0.2 mm, `BRepAlgoAPI_Common` returns a valid shape with no solids. The native section has respectively two and one intersection edges, and a point away from either boundary is classified inside both solids at classifier tolerance zero. The project source STEP SHA-256 is `943ec7545d9cbcbe69266f0e8b1b65e912f80fa46cad0c974dea164bdcbbbee3`; its deterministic import copy SHA-256 is `87d0c9877ed58986447e70256e33e6854e589880ce4110148b60769d78b96c6a`. The current exact assertion path accepts the empty Boolean as clearance. Reorienting the source sphere still gives empty; a newly parameterized coincident sphere gives an erroneous *whole-sphere* common. Neither reparameterization nor a second Boolean is an acceptance proof.

## Goals / Non-Goals

**Goals:** Refuse a demonstrably inconsistent empty exact common in the shared shape-level comparison, so an exact clearance assertion cannot pass this Curta case. Keep the native common's ordinary count and volume semantics when no inconsistency is witnessed. Give project diagnostic code an explicit supported shape-level call that makes the same refusal.

**Non-Goals:** Recovering a missing overlap volume, changing the faceted kernel, adding a volume epsilon or fuzzy OCCT tolerance, deciding all possible false-empty cases, altering the STEP part or fitting the frame, or claiming a successful test is a universal proof of OCCT Boolean soundness.

## Decisions

### Check only a reported empty exact common

`machinome.exact.intersect_shapes(first, second, first_name, second_name)` remains the shape-level call for a native common. After a successful `BRepAlgoAPI_Common` reports no solids, independently section the original two B-reps. A bounded deterministic search takes interior points along positive-length section edges and a small set of three-dimensional offsets scaled to the operands' size. Two `BRepClass3d_SolidClassifier` instances test the same candidate at **zero tolerance**. Only `TopAbs_IN` for **both** is a contradiction witness; `TopAbs_ON`, an intersection curve alone, a mesh overlap, a finite zero-volume common, or a classifier error never become an invented positive volume. With a witness, raise a named exact-common inconsistency exception carrying the two part names and the point. The existing test verdict code lets this exception fail the assertion/run rather than memoizing clearance.

This search is intentionally sufficient, not complete: failure to find a witness leaves the existing Boolean result intact, and the API documents that it is not a general certificate for every pathological B-rep. The fixed search budget bounds cost. A disjoint pair with no section pays no interior probes. Ordinary face/edge tangency may have a section edge but has no strict shared interior, so it retains the old Boolean verdict.

### Use the existing exact seam, not a mesh fallback

The assertion path already calls `intersect_shapes` after conservative AABB and face-box negative tiers. Guarding the existing shape-level function makes direct project diagnostics and managed exact assertions agree. Preserve `_exact_verdict`'s count/volume interpretation and all volume-epsilon/flush-contact policy. Faceted comparisons are untouched. No new public declarative syntax or document version is involved. The `machinome.exact` function is documented as the supported native shape diagnostic for this narrow failure mode, including its refusal rather than a numeric recovery.

Alternatives rejected: treating a positive faceted common as exact overlap (tessellation can intrude), turning on OCCT fuzzy tolerance (alters geometry policy), rotating or rebuilding the sphere (demonstrably changes the wrong Boolean result but not reliably toward truth), or accepting any section edge as an overlap (would reject zero-volume tangency).

## Risks / Trade-offs

- **Finite search misses another false-empty** → State the limited guarantee; keep a red Curta source-shape capture and the deterministic classifier witness. Never describe an unwitnessed empty as certified by this search.
- **An edge-only tangent is falsely refused** → Require `TopAbs_IN` on both at zero tolerance and test disjoint, touching face/edge, true overlap, and containment controls.
- **A contradictory OCCT classifier or section silently raises** → Propagate a named inability to certify the empty result when the checking operation itself fails; do not return clearance from a failed check.
- **Cost on many empty near-contact pairs** → Run after the existing broad phases and only after an empty native common; cap section edges, sample points and offset directions. Measure focused exact regression cost.

## Migration Plan

No persisted data changes. Exact tests that used to pass because OCCT returned a false-empty common now fail explicitly with the two part names; callers may correct geometry or use an independently proved project-specific capture witness. Project diagnostic code can call `machinome.exact.intersect_shapes` rather than raw CadQuery `intersect`. Rollback is the framework commit only; the project STEP and test kernel selection are unchanged.

## Open Questions

The implementation gate must establish a deterministic stencil that catches both Curta ±0.2 mm cases without refusing the tangent controls. If not, return this design to the pilot rather than claiming a complete guard or changing tolerances.
