## Context

At Curta result station 1, drop 2.1 mm, the reported witness `(60.22464937443688, -7.8900000000000015, 20.24964937443688)` is 2.66 × 10⁻¹⁵ mm from the slider's planar face and 7.11 × 10⁻¹⁵ mm from the guide's planar face. Both faces carry native tolerance `1e-7` mm. Classifying at tolerance 0 returns IN on both, but classification at `1e-12` returns ON; ±`1e-7` mm along Y puts the point OUT of opposite solids. The reported point is unresolved boundary contact, not a reliable shared-interior witness. The original Curta ball/frame witnesses are respectively 0.000294 and 0.001333 mm from the nearest frame face and about 0.01 mm from the sphere surface.

## Goals / Non-Goals

**Goals:** Use the native face uncertainty bound to prevent a rounded boundary point from becoming positive-interior proof; retain a bounded, independent witness guard for the original ball/frame failure.

**Non-Goals:** Do not waive a positive intersection volume, classify a small overlap as empty, replace OCCT's Boolean, or prove every unwitnessed empty common correct.

## Decisions

- Keep `BRepClass3d_SolidClassifier.Perform(point, 0.0)` and `TopAbs_IN` as the first necessary condition. On both-IN only, measure point-to-face distance for every face of the classified solid and require each distance to exceed that face's own `BRep_Tool.Tolerance`. This is a proof threshold on the candidate witness, not a user-visible collision tolerance. Native face tolerances are used rather than an invented fixed epsilon.
- A nonfinite/negative native tolerance, nonfinite distance, or native distance failure is an independent-check failure and raises the existing verification refusal. A point at or within any face's tolerance is not a witness; search continues. Classifier UNKNOWN remains a refusal.
- Delay face distances until the cheap classifications both say IN, and use the existing finite section/stencil budget. Positive native commons return before this path unchanged.

## Risks / Trade-offs

- [A real overlap thinner than a face's native tolerance may go unwitnessed] → This guard has always been a finite one-way check, not a completeness certificate; never convert positive common volume to zero.
- [Many apparent candidate points could add distance cost] → Only both-IN candidates pay this check; measure focused and originating-model cost.
- [Native distance/tolerance computation could fail] → Refuse verification rather than claim clearance.
