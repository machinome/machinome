## Context

The originating evidence and interface/package ratification are in `workflow/ongoing/dume-native-freecad.md`. Dum-E contains nine App::Link occurrences, grounded `Feet`, eight fixed/revolute connections and four revolute coordinates. Only `Joint001` enables limits, 0–180 degrees. The source reports FreeCAD `1.1R20260414`; source metadata alone proves no runtime compatibility.

The pilot subsequently chose an independent optional LGPL-2.1-or-later package, `machinome-freecad`, and authorized native linkage. All FreeCAD-specific and source-derived material belongs here. The Apache-2.0 framework is a dependency, not an implementation destination. This worktree begins at adapter base `c2441d5c446d04901fc90c1d772443b07f68a07f`; framework compatibility is checked against `8a8a26711bcd7fd33c6daf7f8866d10004574f8c` (prepared 0.7.1).

Primary-agent evidence reports successful headless loading with official FreeCAD 1.1.4, AppImage SHA-256 `f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434`. Bundled Python imported FreeCAD/Part with `GuiUp=0`, opened parts before assembly and recomputed them; all nine occurrences hold one solid, all eight joints restored their native Joint proxies, and no Invalid objects were reported. This probe does not establish mechanical zero/sign or motion parity. The saved source pose is not assumed to be zero. Preserve the probe script/results in project-owned evidence and repeat checks through the worker.

Subsequent implementation and independent project testing are historical partial evidence, not completed acceptance. `workflow/ongoing/native-freecad-adversarial-review.md` finding 14 confirms that Fixed `Joint002` has an approximately -1 angular direction-cosine residual after recomputation and `solve()==0`, with an approximately 90-degree connector mismatch. Native motion reaches a turntable target while violating the fixed relative pose. The recorded OndselSolver FixedJoint implementation at `30e9b64e8bf881d438d4b88834f9ba3674865418` uses zero-target direction-cosine constraints; it does not make the arbitrary saved offset valid. The current adapter's admission is therefore defective. The pilot now authorizes rejecting inconsistent native constraints and correcting `Joint002` only in a project-owned native FCStd copy, with issue records in that project. The untouched upstream and all failed native/project evidence remain preserved.

Existing framework architecture, STEP and mate baseline specs, ADR-079, ADR-097, ADR-147 with amendments, ADR-154 and ADR-155 are compatibility constraints. The core already provides exact leaves, absolute operation composition, scalar Revolute and running physical-stop admission; this package compiles into them. Context7 `/freecad/freecad` exposes native `AssemblyObject.h`, `JointObject.py` and related placement APIs. Where implementation uses native source, read the exact provisioned-version source and retain any incorporated material's notices.

## Goals / Non-Goals

**Goals:** import a constraint-consistent complete native rigid assembly through FreeCAD; fail closed on inconsistent authored mechanics; add operating intent without duplicated mechanics; preserve native grounding, frames, zero/sign, saved values and enabled limits; make semantics-only/linked-source edits fresh; prove original-source refusal and native numerical parity/limits-only behavior on the explicitly project-repaired Dum-E copy.

**Non-Goals:** closed-loop solving in machinome, Assembly3/A2plus, generalized CAD adapters, unsupported joint types, actuator inference, dynamics, inverse kinematics, native sketch editing in the adapter, live synchronization, browser FreeCAD, a new viewer engine or export schema. This revision authorizes project-owned native correction, not a FreeCAD fork or solver patch. No private importer call, silent importer repair or project-Python replacement joint substitutes for the originating proof.

## Decisions

### 1. Keep the exact ratified public API in the optional package

```python
from machinome_freecad import FreeCADAssemblyNode, FreeCADJoint
from machinome.motion.ports import Time
from machinome.simulation import Driver, Sim

class DumE(FreeCADAssemblyNode):
    freecad_source = "cad/MA_Dum_E_v2_Assembly.FCStd"
    time = Time.running()
    turntable = FreeCADJoint("Joint001")
    turn = Driver(default=0, unit="deg")
    turn.drives(turntable)

sim = Sim(DumE(), dt=0.02)
command = sim.move("turn", to=150, duration=1.0)
sim.run(1.0)
```

Resolve relative source paths from the module declaring `freecad_source`, including inherited declarations, rather than cwd. Accept only the sole unambiguous native Assembly::AssemblyObject. A reference selects a native internal Name, not a Label, and accepts no type/axis/frame/zero/range replacement. Import every connection whether aliased or not. Ordinary module import and Python class creation do not load CAD or require FreeCAD.

`FreeCADJoint` is a declaration reference to the physical imported joint. Its instance descriptor returns the original BoundPort; its relation resolution returns the original ResolvedEnd. Its class-side metadata/owner checks introduce no bound slot or bank address. Canonical resolution must make two aliases of one native Name the same physical endpoint for duplicate-writer checks. Per-instance native graphs and generated joint arguments do not mutate shared class declarations. Missing or fixed-joint selectors fail with source path, selector, type and available moving Names.

Alternative rejected: a proxy assembly port plus wiring would create another coordinate/address and complicate native bound ownership. Class-time native loading would couple Python imports to a system runtime and freeze source mechanics into shared metadata.

### 2. Use existing constructor/reference seams without changing core

Inspection of the framework reference base establishes that `NodeMeta.__new__` calls a relation reference's `check_declared_on` at class creation. `coordinate_ref` accepts an existing CoordinateRef unchanged. At instance construction end, AbstractBaseNode has already initialized source paths, files, operations and declared children before calling `resolve_declared_relations`; Relation.resolve then calls each reference's resolve(instance). Sim only enumerates/compiles after node construction.

Implement FreeCADJoint as an adapter-owned CoordinateRef/descriptor. Class-side checks establish valid local/inherited declaration ownership and reference shape without CAD. Its resolve(instance) calls an idempotent adapter `_ensure_native_assembly`, which creates the carrying tree and native Name index after root path/source initialization but before returning the original physical endpoint. FreeCADAssemblyNode.__init__ calls super and then ensures/validates the graph and every declared alias, covering models with no relations or unused aliases. No global patch, additional core metaclass hook or core lifecycle override is proposed. The adapter overrides normal render to return its stable imported children and uses ordinary rest placement/simulation phases.

The first red-first probe must instantiate the literal class, resolve the relation before Sim enumeration, handle inheritance and two independent instances, and reject a missing Name without partially compiling the graph. It must check internal compiler/ref assumptions as well as Python construction. If a concrete failure proves this sequence insufficient, report the exact existing call and necessary generic seam before opening a separate framework cycle. Do not silently modify the dependency or force callers to use a private post-construction binder.

Document and pin/test the machinome compatibility version for internal CoordinateRef, ResolvedEnd, source-generation and exact-leaf seams. The initial dependency is the prepared 0.7.1 at the recorded commit; the existing workspace's installed metadata still reports 0.7.0 even though the primary source pyproject declares 0.7.1. Rebuild/reinstall the local dependency metadata in the isolated validation environment and record both distribution version and source commit; do not loosen compatibility to accept an old version solely because its editable source happens to point here. Start with the exact 0.7.1 dependency, widening bounds only with actual compatibility evidence. A public index install cannot be claimed until that dependency is available. Smoke the adapter distribution against that exact local dependency outside the repository.

Alternative rejected: introducing a FreeCAD hook into the Apache core defeats the pilot's package boundary. First-render native realization is too late for constructor relation resolution. Hardcoding a new Sim branch would split existing mechanical authority.

### 3. Isolate native loading in a FreeCAD subprocess worker

The adapter invokes a narrowly scoped worker with FreeCAD-capable Python, avoiding FreeCAD/OCCT interpreter and ABI clashes with the framework. The provisioned runtime supports bundled Python via AppRun with an absolute PYTHONPATH to usr/lib and Assembly module paths; probe and document a deterministic executable configuration. Missing/incompatible runtime errors occur at native instance realization. The package does not install or redistribute a FreeCAD binary.

The worker opens the root and required linked documents through native FreeCAD APIs, restores native proxies, resolves each link/subelement, recomputes source documents/assembly and checks native error/solver status as appropriate. Capture saved occurrence placements before recomputation and compare after; do not silently accept unexplained drift. Native Joint proxy placement helpers, including the provisioned findPlacement/UtilsAssembly path and native offset composition, are the preferred source for resolved connector frames. Do not replace them with a ZIP-XML production interpreter. Before accepting a snapshot, additionally validate resolved Fixed/Revolute connection residuals against the recorded native constraint conventions; successful solve and saved-pose stability are necessary evidence but do not replace these checks.

Return a bounded immutable snapshot containing runtime identity, consumed filenames, occurrence/product document identity and Names/Labels, grounding, joint Names/Labels/types/endpoints, proper world/connector placements, native saved coordinates, units and enabled bounds. Return only assembly members; three unused O-ring bodies in Dum-E's linked source are excluded. Unknown/suppressed/unresolved joint objects remain visible in refusals rather than disappearing.

Transfer exact solid geometry in each product's own frame via native BREP serialization, checking interoperability with the framework OCCT reader. An internal STEP geometry transfer is acceptable if BREP versions are incompatible: the native graph remains the sole mechanical authority. Remove product/link/world placement exactly once; verify volumes, own-frame geometry and pose independently. Build adapter-owned exact leaves/carriers using the framework's ordinary exact materialization/tessellation. Generated carrier/leaf source origin and artifact identities must belong to the authored wrapper/product, distinguish same-named products/documents and survive source-preserving relocation without embedding worker temporary filenames into structural identity. Never fuse fixed-connected occurrences.

Alternative rejected: XML plus stale cached shapes cannot establish link/reference recomputation. In-process linking is licensed but adds runtime/OCCT compatibility costs unnecessary for this working headless worker route. A generalized worker protocol has no originating need.

### 4. Compile connectivity and native coordinates to existing joints

Validate one connected acyclic rigid graph grounded at one occurrence, with all included fixed/revolute edges unsuppressed and resolved. Root by native connectivity, not flat App::Link order or Reference1/2 order. Refuse loops, disconnected occurrences, competing grounding, unsupported types, invalid references or non-rigid placements. Endpoint traversal opposite to authored order must preserve native sign and connector conventions.

Validate the resolved connector origins and the constrained angular residuals of every Fixed/Revolute connection before compiling carriers or caching a successful snapshot. Ground the checks in the recorded version-specific native constraint equations/targets, including the valid orientation branches. For Fixed, evaluate the native zero-target angular direction-cosines and position constraints; preserving an arbitrary saved relative occurrence transform cannot redefine those targets or certify the connection. For Revolute, evaluate the constrained position and transverse angular relations while leaving its permitted spin free. Account explicitly for valid parallel/opposite-axis branches in native conventions; do not impose full-frame equality on all joints or reject Dum-E's valid antiparallel revolute axes merely for their sign. If native conventions or branch validity cannot be established for a candidate, refuse rather than invent a saved-pose convention.

Record finite measured residuals and explicit, dimensionally appropriate numerical tolerances for translation and direction-cosine/angular checks. Tolerances must be justified by the native convention and numerical reference tests and must not be enlarged to admit the observed approximately -1 residual. Refusal identifies source, joint Name/type, connected occurrences, measured residual and tolerance. Native status zero is no exemption. Red-first synthetic tests must include an unsatisfied Fixed quarter-turn that solve reports successful, a displaced/inconsistent Revolute, and native-valid opposite-axis branches. The untouched pinned Dum-E source must now fail with `Joint002` as empirical negative evidence. The adapter performs no native correction itself.

Represent each occurrence as a carrier holding its own exact geometry and downstream carriers. Fixed edges add rest placement only; moving edges add one existing scalar Revolute in the carrier's own rest frame. Preserve native occurrence Names through reparenting and all eight connection records. Use deterministic valid qualified names and stable product identity; editable labels neither select nor merge objects.

For parent/child saved world placements Pp and Pc, the saved relative transform is inv(Pp) @ Pc. It is not automatically the rest transform at coordinate zero. With native saved value qs and correctly signed own-frame rotation M(q), derive Z such that inv(Pp) @ Pc = Z @ M(qs), then compare the actual framework operation composition to the native reference. Native connector frames, offsets and runtime conventions determine zero, axis/anchor, sign and qs. The provisioned native UtilsAssembly.getJointXYAngle reports radians via native getJcsGlobalPlc for Placement1/2 and Reference1/2; use the native facilities rather than reproducing frame resolution. Primary's native probe reports antiparallel turntable JCS Z axes and a saved angle about 39.7392 degrees, while the generic Joint.Angle remains zero. Neither equal-facing frame assumptions nor that generic property's value establish the coordinate. Validate zero and positive motion, including nonzero saved poses and reversed/oblique synthetic edges, before trusting the compiler.

Enabled minima/maxima become ordinary numeric Revolute bounds in degrees. Disabled sides become None even if stored zero; validate units, finite values and ordering. Each uncommanded revolute receives its native saved value through a guarded rest binding only while unbound, preserving relation and run ownership. All four imported coordinates enter the existing running bank once. Clearing/re-enumerating and fresh simulation recover appropriate source defaults without cumulative transforms or second writers.

Imported bounds therefore use existing initial-state refusal and running physical-stop admission after native consistency admission succeeds. The default=0 in the example commands native zero and is checked against native limits; it does not redefine zero. For the accepted repaired native baseline, at 150° its 0–180° range completes; at 120° a reduced maximum blocks outward travel. Driver ranges remain presentation metadata. No new solver, motion engine or export fields are needed.

### 5. Observe complete native source generations

Track root FCStd, every external native document consumed during resolution, and the wrapper's ordinary source contributors with canonical paths and strong observations. Admit discovered linked dependencies before accepting the worker response. Bracket native resolution and producing/publication boundaries against the framework source generation. Use relevant content digests after changed observations and include runtime/importer recipe identity in native snapshot compatibility. A root/linked semantic edit or same-size restored-mtime replacement must invalidate mechanics even when shapes match. A failed or interrupted native load publishes no successful cache entry or stale substitute.

Cache immutable native data only, not nodes/slots. Fresh model/simulation construction consumes the newest source. Bump the native importer recipe/acceptance compatibility identity for residual validation, so a previously admitted inconsistent snapshot cannot bypass the new checks. Cache acceptance covers successfully established native consistency; error paths seed no successful snapshot. A semantic edit need not alter geometry piece identity, but the running graph must rebuild from changed semantics. Active-run reinterpretation is outside scope.

Alternative rejected: geometry hashes, root mtime or max dependency mtime alone miss a limits-only change and linked-source edits below a newer root timestamp.

### 6. Publish package docs and require independent numerical evidence

Provide package-owned public documentation before handing the API to the independent simulation author: imports, exact example, source path/inheritance rules, selector Names, BoundPort observation, supported graph, runtime configuration, tested framework compatibility, fresh-source semantics and useful refusal examples. Existing public node render/children/operations and operation.matrix or mesh surfaces can support numerical project evidence without adapter-private methods. Record native Names/Labels, endpoint frames, units and enabled flags in readable inventory evidence and selector errors. A separate diagnostic-command/API spelling is not ratified by this cycle.

Use authored synthetic FCStd fixtures with explicit provenance for regression tests: external links, fixed descendants, oblique/reversed endpoints, nonzero saved pose and limit variants. Mock worker responses can isolate cache/refusal cases but cannot establish native correctness. Keep ambiguous upstream CAD only in the independently owned project's untouched pinned submodule.

Preserve the original upstream hashes, failure reproductions and previous provisional limit observations as historical evidence. Document the inconsistent `Joint002`, its residual and native motion failure in the independent project's own issue/work records. Through FreeCAD's authoring facilities, correct only that clearly identified connection in a project-owned FCStd closure without modifying the upstream submodule, runtime or solver. Preserve own-frame geometry and the saved occurrence pose where possible by correcting native connector authoring; record before/after native fields, hashes, residuals, geometry and placements. Quantify and explain any unavoidable saved-pose difference. Do not put equivalent replacement joint mechanics into project Python or claim that a valid repaired source is untouched upstream evidence.

The explicitly repaired and re-opened native copy is the primary positive validation source. Establish that its corrected graph satisfies the native constraints and native motion preserves target angles, grounded placement and all fixed connections. Then the independent simulation author must use the unchanged public API, compare every occurrence at multiple turntable poses and at least one nonzero pose per other revolute against native FreeCAD, and report maximum translation/orientation errors. Acceptance tolerances remain 0.01 mm and 0.001 degree, with tighter fixture tolerances where justified. Verify all nine occurrences, all eight connections, four physical coordinates, resolved versus saved placements, and disabled zero bounds. These checks remain required even after source repair; no solver-status-only oracle is accepted.

From the accepted repaired baseline create 0–180° and 0–120° source variants through FreeCAD at a common valid saved pose, differing from each other only in Joint001.AngleMax; record hashes and semantic differences. Both share the same documented `Joint002` correction. Verify unchanged own-frame solids and placements between the two limit variants within recorded tolerances. Run one unchanged public simulation source from 0° to 150° over one second: completed/150° on the repaired 180° baseline, blocked/120° on its reduced-maximum variant after rebuild. Record setup effort, manual mappings, correction effort, refresh timing and failures. Rerun the geometry-only STEP control from the repaired baseline, recording its duplicated joint/frame/limit declarations and required maximum edit. Screenshots supplement numerical assertions.

### 7. Keep source provenance within the LGPL adapter

Linkage and source inspection are authorized. Any incorporated/adapted FreeCAD material retains its upstream copyright/licence and explicit change notice here; source-derived native implementation is never copied into the Apache core. Track actual incorporated material in package notices and distribution manifests. Original adapter work is copyright 2026 Luis Henrique Cassis Fagundes, LGPL-2.1-or-later. The native runtime stays user-provided; packaging checks upload nothing.

## Risks / Trade-offs

- [Internal core seams can change] → Pin and test the reference commit/version, isolate compatibility calls, and reject unsupported versions clearly; require separate authority for any core change.
- [Source saved pose confused with zero/sign] → Native runtime reference poses and oblique/reversed/nonzero fixtures are mandatory before admission claims.
- [Native solver reports success on inconsistent authoring] → Evaluate the recorded native Fixed/Revolute residuals and valid branches before accepting/caching; original `Joint002` is expected refusal, not an offset silently frozen into the importer.
- [Source repair conceals the original defect] → Preserve untouched upstream and failed evidence; project-owned records identify the approved native correction and all before/after geometry/pose/residual changes; rerun every positive gate on that repaired baseline.
- [BREP/OCCT incompatibility or double placement] → Verify own-frame exact transfer/volumes; use a compatible geometry representation while preserving native mechanics.
- [Alias or guarded defaults introduce another writer/bank slot] → Verify endpoint identity, duplicate aliases, four physical coordinates and repeated rendering/new Sim behavior.
- [Semantic or linked edits reuse old mechanics] → Limits-only, restored-mtime linked replacement and source-race regressions gate cache acceptance.
- [Third-party provenance omitted] → Inspect source and distribution notices, retaining original attribution/change notices for every incorporated fragment.
- [CAD fixture provenance ambiguous] → Original synthetic adapter fixtures and project-pinned upstream submodule, no copied Dum-E CAD fixture here.

## Migration Plan

The package is additive and unreleased. This approved revision amends planning while preserving uncommitted implementation and historical evidence; reset planning checkboxes to unchecked for the amended planning commit, then restore achieved status only against evidence after that commit. The separately assigned apply agent carries the new residual-admission delta red-first; project-owned native repair is independent work in the Dum-E repository. Retain the recorded framework dependency `8a8a26711bcd7fd33c6daf7f8866d10004574f8c` in an isolated validation checkout now that primary has moved; do not replace the pinned dependency with current primary by assumption. Revalidate native admission, source/pose conventions, public API, all adapter/native/project gates and relevant framework regression checks. Rebuild/smoke distributions against that dependency. Acceptance stays open until original-source refusal and the complete repaired-source motion/limit/STEP proofs are green.

After proven implementation, the primary owns the studio contract update through the studio's separate process; this package cannot stage or commit it. If framework user manual changes are later authorized, they need a separate framework cycle and the write-the-manual skill. This repository documents its own public API now. Any accepted consequential architecture choice is recorded only after tests confirm it. Sync baseline specs and archive through supported OpenSpec operations only after all proof gates, then make the completed implementation record. No integration, push, publication or tag is implied.

## Open Questions

- Does the existing CoordinateRef/descriptor constructor seam satisfy running compilation and ownership without a core edit? The focused probe decides; concrete failure is reported before expanding scope.
- What exact native zero/sign and offset conventions resolve this saved source pose? Native reference motion decides; successful load alone does not.
- Does native BREP transfer interoperate with the tested framework OCCT? Probe and record the geometry format/version.
- Which minimal deterministic runtime configuration should public docs expose? Use the provisioned working headless path as evidence; do not claim an untested cross-platform matrix.
- Which native connector authoring correction satisfies `Joint002` while retaining the saved machine geometry/pose? Determine it in the project-owned copy and record before/after differences, never in importer-generated replacement mechanics.
- Which finite residual tolerances and valid Fixed/Revolute branches reproduce the recorded native conventions without false rejection? Validate them on native fixtures, original-source refusal and the repaired positive reference before closure.
