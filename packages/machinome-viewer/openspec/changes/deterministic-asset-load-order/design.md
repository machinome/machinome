## Context

Leonardo's 70-frame `demo-incremental-source-grid` differed between fresh cold mounts only at frame 10, pixel (487, 262), despite fixed source, bundle and frame inputs. That is the integration symptom, not yet a proven causal attribution. The controlled diagnostic in Videomaker's `experiments/film-production/load-order-diagnostic.mjs` isolates one viewer defect: a fixed API 28 bundle (SHA-256 `a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`) draws identical coincident red/blue STLs differently when only their network completion order is reversed. Two independent ABBA reports under production flags and root reproduction record five stable PNGs per mount: red-then-blue completion yields `069361…`, centre `[30,30,204]`; blue-then-red yields `529fc…`, centre `[201,30,30]`. They establish completion-order sensitivity; the repaired real film must establish whether this is its one-pixel cause.

In `WidgetTree` construction, node and child load calls begin synchronously in document traversal order and run concurrently. `loadMesh` currently awaits `STLLoader.loadAsync` before constructing `THREE.Mesh` and material. Sibling parts can therefore receive mesh/material identities in fetch completion order. `loadMarkings` already collects records with `Promise.all` and seats them in document order, but its mesh/material allocation also follows each fetch. The correction must account for resources it newly reserves in these load paths. `artifactChanged` and `prepareReconcile` fetch replacements before live mutation (ADR-037; ADR-056); this correction must keep that guarantee, including marking own colours and bias.

## Goals / Non-Goals

**Goals:**

- For one published document, viewer build, browser/render environment, view and pose, fresh mounts draw the same fully loaded image regardless of the order in which rigid model and marking STL requests complete.
- Keep the existing document tree, material properties, real depth/geometry, marking lift/polygon offset, concurrent requests and failed targeted-update containment.
- Establish a red-first controlled failure, then exact browser and real-film proof without relaxing pixel equality.

**Non-Goals:**

- No public API, schema field, document/package version declaration, new dependency, global renderer sorting policy, geometry bias or general graphics reproducibility audit.
- No assertion that every possible sequence of `artifactChanged`, `manifestChanged` and `reload` yields the same tie order as a cold mount. Those operations must retain their existing correctness and failure guarantees; any broader history equivalence needs separate evidence and authorization.
- No repair of pre-existing aggregate staging cleanup when one of several concurrent sibling or reconciliation loads fails after another has succeeded. This is an out-of-scope finding, not a promise of this pixel-correction cycle.
- No claim of byte-identical images across different browser, GPU or renderer configurations.

## Decisions

### D1 — Reserve draw identity in document traversal before awaiting bytes

Construct the rigid mesh and its intended material synchronously when its document entry is visited, then load and prepare its geometry asynchronously. For markings, reserve mesh/material identities in marking-list order before awaiting their STLs; keep their own colour, double-sided material and existing geometry lift. Only attach a ready mesh to the live scene at the established loaded boundary. This makes identity allocation independent of response completion while retaining parallel fetches. The implementation may use a small internal prepared-load object or equivalent, but must not change the host boundary.

The observed result, not an assumption about one renderer's sorting internals, is the acceptance criterion: the ABBA fixture's two network orders must produce equal complete PNGs at the same frame and view. If pre-await identity reservation does not pass that, inspect the remaining viewer-owned ordering seam before choosing any further internal change; return to ratification if it requires a public contract or materially wider renderer architecture.

**Alternative rejected:** serializing STL requests would also impose one completion order but needlessly sacrifices the existing concurrency. A universal `renderOrder`, depth-test change or geometry offset would change genuine occlusion and ADR-056's marking rendering rather than fixing an asynchronous identity accident.

### D2 — Own resources newly reserved by each load

The load that reserves a mesh/material before awaiting an STL owns those resources. If that fetch or that load's geometry preparation fails, it discards its unready mesh and disposes its material and any geometry returned to that load before rejecting. Do not attach a blank reserved mesh early. A successful load hands ownership to the existing tree or replacement path. Existing `artifactChanged` and `prepareReconcile` prepare-before-mutation and previous-live-model/camera failure containment remain intact; replacements and retained markings keep their established document order and own colour. Do not change viewer mount/reconcile aggregate lifecycle merely to settle or dispose unrelated pending or successful sibling loads.

**Alternative rejected:** attach blank placeholders or mutate the live tree as each fetch completes. That would expose partial state and weaken the failed-update contract. Broad aggregate cleanup of independently prepared siblings is a separate pre-existing issue without evidence that it caused the observed pixels; it is not bundled here.

### D3 — Bound the proof to the demonstrated mechanism and consumers

First make deferred-load unit tests fail on current code: reverse sibling STL completion and assert stable pre-ready mesh/material order and the same fully loaded tree; cover model-plus-marking order and concurrent starts. Add red-first checks for the new local ownership behavior: each load has its reserved identity before its request resolves, then a failed fetch or preparation discards its unready mesh and disposes its material and returned geometry without attaching a blank mesh. Keep targeted-update failure containment and normal-depth/marking properties as regression checks; do not assert cleanup of unrelated successful siblings. A viewer-owned Python/Playwright ABBA regression must fail its exact PNG equality assertion on the old bundle before runtime edits, then pass on the repaired bundle. Verify that the response orders actually reversed and all repeated captures agree. Preserve the separate independent diagnostic reports, whose original scripts reported the mismatch without failing their exit status. No one-colour aesthetic preference is specified; consistency with document order is the contract.

Then run repeated fresh 70-frame Leonardo cold captures under the repaired viewer and compare every corresponding PNG hash, including the original frame-10 pixel. Also run the existing 80-frame `demo-incremental-rendering` and 70-frame `demo-incremental-source-grid` cold-versus-incremental Videomaker proofs with every frame exactly equal, recording the viewer bundle hash, consumer inputs and render configuration. If ABBA passes but a real-film comparison fails, retain the mismatch as an unresolved finding; do not declare the video cache valid or loosen equality. These integration checks are verification gates, not a new viewer API.

## Risks / Trade-offs

- **A mesh/material identity may not be the only renderer ordering input** → the browser ABBA test judges pixels; inspect any remaining viewer-controlled source of ordering if it fails, without assuming the hypothesis succeeded.
- **Early allocation can leak on rejection** → test disposal of the newly reserved objects and any returned geometry for that failed load, without treating pre-existing aggregate cleanup as solved; preserve prepare-before-mutation for targeted updates.
- **Deterministic ties are not physically defined occlusion** → retain depth test/write, geometry and marking bias; use differing-depth regression so a nearer part still occludes the farther one.
- **The Leonardo pixel may have another cause** → require repeated full cold captures and exact cold/incremental comparison; report any residual separately.

## Migration Plan

Internal viewer-bundle replacement only. Existing documents and host calls are unchanged. Rollback is the prior bundle, but that restores the measured completion-order defect; do not use it to bless exact Videomaker cache reuse.

## Open Questions

None requiring a public decision. The causal link to Leonardo's frame-10 pixel is deliberately an empirical gate, not a premise of this design.
