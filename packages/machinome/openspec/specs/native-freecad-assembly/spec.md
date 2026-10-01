# native-freecad-assembly Specification

## Purpose

Import supported native FreeCAD assemblies into machinome through a separate
optional LGPL adapter, preserving authored joints and enabled limits without
project-level mechanical redeclaration. Dum-E provides the empirical acceptance
case, including explicit refusal of inconsistent native constraints.

## Requirements

### Requirement: Native assembly declaration and selected coordinate reference

The system SHALL export `FreeCADAssemblyNode` and `FreeCADJoint` from `machinome_freecad`. A subclass SHALL declare `freecad_source` naming its FCStd source, resolved relative to the Python module declaring that attribute. A class-body `alias = FreeCADJoint("Joint001")` SHALL select the existing imported revolute coordinate by native internal Name and SHALL be accepted as the target of an ordinary `Driver.drives(alias)` relation. The reference SHALL accept no replacement axis, frame, zero, type or range. Native existence and coordinate compatibility SHALL be checked after native resolution and before relation binding and simulation graph compilation.

Importing the public module or declaring the Python class SHALL NOT open CAD or require a FreeCAD runtime. Realizing a native assembly SHALL resolve its source before instance relations or simulation enumeration consume it. Every model instance SHALL own fresh nodes, joint arguments and bound slots; native mechanics SHALL NOT be mutable class-shared state.

Positive Dum-E scenarios in this capability SHALL use the explicitly project-repaired, constraint-consistent native copy described below. The untouched pinned upstream source SHALL remain negative admission evidence; repaired-source success SHALL NOT be reported as acceptance of that untouched source.

#### Scenario: The ratified running example constructs and moves

- **WHEN** the following class is instantiated from a valid supported source and its simulation is run

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

- **THEN** the relation addresses the native `Joint001` coordinate without any project-authored joint, frame or mechanical-limit declaration

#### Scenario: Source resolution does not depend on process cwd

- **WHEN** a supported subclass declares a relative source and is instantiated from another working directory or through an inheriting subclass in another module
- **THEN** the source resolves from the module that declared `freecad_source`

#### Scenario: Native selectors are not display labels

- **WHEN** a reference names an editable Label instead of the native internal Name, or selects a missing or fixed joint
- **THEN** realization refuses it naming the source, selector and type where present, and reports the available moving native Names

#### Scenario: Two instances are independent

- **WHEN** two instances of one native assembly class are simulated at different turntable commands
- **THEN** each retains its own coordinate values and placements and neither changes shared class declarations or the other's pose

### Requirement: Native resolution is authoritative

The system SHALL resolve the FCStd and its consumed external linked documents using FreeCAD document/reference APIs and native recomputation. It SHALL record the runtime version/build and binary identity used. It SHALL check link and subelement resolution, recomputation errors and applicable assembly-solver failures before accepting geometry or mechanics. It SHALL compare resolved occurrence placements with the saved source placements and refuse unexplained drift outside the recorded acceptance tolerances. It SHALL NOT substitute raw FCStd XML interpretation or previously cached shapes when native resolution fails.

The importer SHALL admit exactly one unambiguous native `Assembly::AssemblyObject` with supported rigid occurrences. A supported import SHALL contain the assembly's occurrences only, not every body from a linked parts document. Shape and placement admission SHALL retain exact solid geometry in each product's own frame and SHALL refuse empty/non-solid geometry or non-rigid occurrence transforms that existing operations cannot express.

#### Scenario: Repaired Dum-E resolves its linked assembly

- **WHEN** the documented project-repaired Dum-E source and its project-owned linked closure are resolved in the recorded runtime
- **THEN** the import contains nine occurrences and excludes the three unused O-ring bodies, with `Feet` recorded as grounded

#### Scenario: An unresolved link or native error fails import

- **WHEN** a linked document is missing, a joint subelement cannot resolve, or native recomputation/solver status reports an error
- **THEN** import fails naming the native source and affected object/reference and publishes no successful snapshot or substitute stale shape

#### Scenario: Native assembly selection is ambiguous

- **WHEN** a source contains multiple candidate native assemblies or none
- **THEN** import refuses with the available native assembly inventory and does not guess one from a Label or document order

### Requirement: Native Fixed and Revolute consistency is required for admission

The importer SHALL validate the resolved connector position and constrained angular residuals of every included Fixed and Revolute connection against the recorded version-specific native constraint equations, target values and valid orientation branches before compiling a successful carrying tree or accepting/caching a snapshot. A Fixed connection SHALL satisfy the native position and zero-target direction-cosine/angular constraints; an arbitrary saved relative orientation SHALL NOT redefine those targets. A Revolute SHALL satisfy its constrained position and transverse angular relations while retaining the native free spin. Native-valid opposite-axis branches SHALL be admitted; full-frame equality SHALL NOT be imposed universally. Unknown branch/convention validity, nonfinite residuals or residuals outside explicit justified tolerances SHALL be refused.

Native recomputation/solve success and stable saved occurrence placements SHALL NOT exempt a candidate from consistency checks. A refusal SHALL identify source, native joint Name/type, connected occurrences, measured residual and applicable tolerance. Tolerances SHALL retain their appropriate units and SHALL NOT be enlarged to accept Dum-E's observed approximately -1 Fixed angular residual. The importer SHALL NOT silently repair native source, freeze a saved offset as replacement mechanics or skip an unsatisfied constraint. The changed acceptance recipe SHALL invalidate previously admitted snapshots that did not establish native consistency.

#### Scenario: Successful solve does not admit the original inconsistent Fixed connection

- **WHEN** untouched pinned Dum-E resolves with `solve()==0` and stable saved placements but `Joint002` retains its measured approximately -1 zero-target angular residual
- **THEN** import refuses naming `Joint002`, its Fixed type/endpoints, the residual and tolerance, and publishes no successful model or stale cached substitute

#### Scenario: An inconsistent Revolute is refused

- **WHEN** a native fixture has a resolved Revolute whose constrained connector position or transverse angular residual is outside its recorded tolerance
- **THEN** import refuses that connection rather than inventing an offset or using only its available spin angle to admit it

#### Scenario: Native-valid opposite axes remain supported

- **WHEN** a consistent fixture uses the recorded valid opposite-axis branch for a native connection, including a Revolute with antiparallel connector Z axes
- **THEN** consistency admission succeeds and its zero/sign and positive native motion match the imported coordinate without a false full-frame-equality refusal

#### Scenario: An old provisional snapshot cannot bypass stricter admission

- **WHEN** the importer encounters a snapshot produced before native residual validation for a now-inconsistent source
- **THEN** it rejects that snapshot's acceptance identity and refuses the source after the required native consistency checks

### Requirement: The imported connection tree carries the complete native machine

The system SHALL support a connected acyclic rigid-occurrence graph with one grounding and unsuppressed fixed and revolute connections. It SHALL derive the carrying hierarchy from native connectivity rooted at the grounded occurrence, preserving occurrence and joint internal Names, Labels and external-document identities through any reparenting. Every connection SHALL remain represented in the resolved inventory. Fixed connections SHALL retain rigid relative placement without fusing occurrences or inventing a coordinate; each revolute SHALL create exactly one existing-framework scalar joint coordinate. Native endpoint order SHALL NOT change the physical sign or carrying behavior.

Closed loops, disconnected occurrences, competing grounding, unsupported joint types/objects, unresolved endpoints and suppression that leaves the graph unsupported SHALL be refused naming the responsible objects and reason. The importer SHALL NOT silently flatten unsupported mechanics.

#### Scenario: The complete Dum-E chain is preserved

- **WHEN** Dum-E is imported and its turntable is commanded
- **THEN** all eight connections, including four fixed edges, remain represented; `Shoulder`, `Arm2`, `Arm1`, `Wrist`, `Phone_back` and `Phone_bottom` follow the turntable, `Feet` stays fixed, and each fixed edge retains its relative transform

#### Scenario: Endpoint order differs from rooted traversal

- **WHEN** an authored supported fixture stores a revolute's endpoints opposite to the grounded tree traversal
- **THEN** its native positive coordinate and every downstream placement agree with FreeCAD at the tested poses

#### Scenario: An unsupported graph is explicit

- **WHEN** a native fixture introduces a loop, disconnected occurrence, second grounding, unsupported connection or invalid suppression
- **THEN** import refuses with the involved native Names and unsupported condition before a plausible geometry-only machine is emitted

### Requirement: Native coordinate conventions and enabled bounds are preserved

The system SHALL derive the native revolute coordinate, zero, positive orientation and own-rest-frame line from resolved native connector frames, offsets and placement semantics. A saved pose SHALL NOT be assumed to be coordinate zero, and a generic `Angle` property unrelated to the revolute coordinate SHALL NOT provide its value. Angular coordinates and limits SHALL be exposed in degrees with explicit unit validation. Each enabled native minimum or maximum SHALL become that side of the ordinary imported joint range; a disabled side SHALL be unbounded regardless of its stored number. Invalid nonfinite or reversed enabled bounds SHALL refuse import.

An imported-coordinate alias SHALL resolve to the original physical endpoint for reads, relation binding, state compilation and duplicate-writer checks. It SHALL create no second bank slot, coordinate or independently bound proxy. An uncommanded revolute SHALL retain its resolved saved coordinate as its guarded rest value and remain available in the running bank; source defaults SHALL NOT overwrite a relation or running-owned binding.

#### Scenario: A nonzero saved pose keeps native zero

- **WHEN** an authored fixture saves a revolute at a nonzero coordinate and the project then commands zero and a positive angle
- **THEN** both poses match native FreeCAD reference placements within the declared tolerances rather than rotating from a new zero at the saved pose

#### Scenario: Disabled zero bounds do not lock the arms

- **WHEN** Dum-E's `Joint003`, `Joint004` and `Joint005` have disabled minimum and maximum flags with stored zero values
- **THEN** their imported coordinates are unbounded and a nonzero command on each is admitted and reproduces its native pose

#### Scenario: One-sided limits are respected

- **WHEN** an authored revolute enables only a minimum or only a maximum
- **THEN** only that side limits motion and the disabled side remains unbounded

#### Scenario: The alias has one physical identity

- **WHEN** two declared references select one native Name
- **THEN** they read the same physical endpoint and ordinary duplicate-writer checks refuse competing bindings; the simulation does not bank an additional coordinate under either alias

#### Scenario: Uncommanded native freedoms have rest values

- **WHEN** the running Dum-E example binds only the turntable
- **THEN** all four imported revolutes have one banked rest coordinate, the three uncommanded ones retain native saved values, and fresh enumeration or rendering advances none of them

### Requirement: Imported limits govern ordinary running admission

Native imported bounds SHALL be ordinary joint mechanical ranges consumed by existing initialization, binding and running-admission rules. The project's driver default or explicit initial state SHALL command the existing native coordinate and SHALL be validated against its enabled bounds. Initial out-of-range requests SHALL refuse without silently changing native zero or range. Under a running root, motion exceeding an enabled bound SHALL stop at that bound and report the command as blocked under existing physical-stop behavior; a valid in-range target SHALL complete. A driver range SHALL remain presentation metadata and SHALL NOT replace native mechanical bounds.

#### Scenario: The repaired baseline maximum admits 150 degrees

- **WHEN** a fresh running Dum-E simulation uses the documented consistent project-repaired baseline, starts its turntable command at 0 degrees using native 0–180 degree limits and moves to 150 degrees over one second
- **THEN** the physical turntable reaches 150 degrees, the command completes, and downstream occurrences have the matching native pose

#### Scenario: A native limits-only change blocks at 120 degrees

- **WHEN** the source is rebuilt from a FreeCAD-authored variant of that same repaired baseline changing only `Joint001.AngleMax` from 180 to 120 at a common valid saved pose and the unchanged project simulation requests 150 degrees
- **THEN** the physical turntable stops at 120 degrees and the command is blocked without any project-authored limit edit

#### Scenario: An invalid initial command is refused

- **WHEN** an initial default or `state=` commands beyond an enabled native bound
- **THEN** construction refuses with the source/joint Name, requested value, bound and unit rather than clamping or inventing a new mechanical zero

### Requirement: Native semantic and linked-source changes invalidate fresh builds

The importer SHALL track the root FCStd, the complete external-document closure consumed during native resolution and the wrapper's ordinary source contributors. Cache acceptance SHALL cover canonical paths, strong file observations, relevant content and the native runtime/importer recipe. A contributing semantic edit, file replacement, removal or relink SHALL invalidate resolved mechanics even when own-frame geometry and placements are unchanged or an old mtime is restored. Files changed during native resolution or producing/publication phases SHALL be rejected by the source-generation checks. Failed resolution SHALL NOT seed a successful cache entry.

Resolved immutable native data SHALL be reusable without sharing mutable node/joint state. A source change SHALL take effect in a newly built node and fresh simulation; changing the interpretation of an active run in place is outside this capability.

#### Scenario: An unchanged shape has changed mechanics

- **WHEN** the maximum-limit-only variant leaves the resolved solids and saved placements equal within tolerance
- **THEN** the next fresh build still consumes the new 120 degree limit instead of serving cached 180 degree mechanics

#### Scenario: A linked source changes below a newer root timestamp

- **WHEN** a consumed external FCStd is replaced while the root FCStd has a later unchanged mtime
- **THEN** the next fresh build resolves the linked replacement and cannot reuse a snapshot solely because the maximum source mtime is unchanged

#### Scenario: Source replacement occurs during native loading

- **WHEN** a contributing file changes between the worker's admitted source observation and acceptance/publication
- **THEN** that generation is refused and no stale native snapshot or artifact is published

### Requirement: Project-owned native correction is transparent and preserves the failed baseline

The approved originating-project correction SHALL occur only in a project-owned FCStd copy/linked closure through native FreeCAD authoring, correcting the identified Fixed `Joint002` connection. The pinned upstream submodule and original source hashes SHALL remain untouched, and the recorded failed original admission/motion evidence SHALL be preserved. The correction SHALL NOT change the FreeCAD runtime/solver, use a FreeCAD fork, add project-Python replacement joints/frames/ranges or authorize automatic importer repair.

The project SHALL document the native issue, correction, before/after joint fields, source hashes, constrained residuals, own-frame geometry and saved occurrence placements in its own records. Geometry and saved pose SHALL be preserved where possible, and every unavoidable saved-pose difference SHALL be quantified and explained explicitly. The positive validation source SHALL be the corrected native copy after reopening/recomputing and consistency admission; a repaired source SHALL NOT be described as untouched upstream. Both limits-only variants SHALL share that same documented correction and SHALL differ from each other only in `Joint001.AngleMax` at a common valid saved pose.

#### Scenario: The corrected native baseline is positively validated

- **WHEN** the project corrects `Joint002` through FreeCAD, records the source differences and reopens the project-owned native copy
- **THEN** the native graph satisfies the recorded constraint checks, the importer admits it, and native moving-reference validation preserves target angles, grounded placement and fixed relative transforms

#### Scenario: Correction cannot conceal an occurrence pose change

- **WHEN** the native correction requires a saved-pose difference despite attempts to preserve it
- **THEN** project records quantify and explain that difference against the failed original and the repaired positive baseline is identified explicitly

#### Scenario: The limits-only comparison shares one corrected baseline

- **WHEN** the repaired 180-degree baseline and its 120-degree variant are compared
- **THEN** both contain the same documented `Joint002` correction and equivalent geometry/common saved placements, and their only measured joint-semantic difference from each other is `Joint001.AngleMax`

### Requirement: Native parity and originating-project evidence establish acceptance

Acceptance SHALL include original-source inconsistency refusal, execution in the recorded native runtime and independently compared native/machinome world placements on the explicitly project-repaired consistent source, plus its unchanged-public-API Dum-E limits-only experiment. Static XML inventory, mocked importer success, solver status zero or correct target angle alone SHALL NOT establish native compatibility. At multiple turntable poses and at least one nonzero pose of each other revolute, all nine occurrences SHALL agree with the native reference within 0.01 mm translation and 0.001 degree orientation. All eight connections, four physical coordinates, saved/resolved placements, grounding and fixed-edge relative transforms SHALL be checked. The repaired-baseline limits-only variants SHALL have unchanged geometry and common saved placements within recorded tolerances. Source repair SHALL NOT weaken or replace any full-motion gate.

The completed record SHALL include source/runtime identities, native inventory and frames, constraint residuals, tolerances and maximum measured errors, command statuses, source-change refresh observations, setup/correction effort, manual mappings and encountered failures. The native issue/correction records SHALL remain project-owned, linked from adapter acceptance evidence. Full adapter/native/project/framework validation SHALL be rerun after the admission change and repair against the recorded framework reference commit. A geometry-only STEP control from the repaired baseline SHALL record the mechanical declarations it needs and the edit needed after the native maximum change. Adapter-owned fixtures SHALL be authored synthetic assets with explicit provenance; ambiguous upstream CAD SHALL remain in the originating project's pinned submodule rather than be copied into adapter fixtures. Existing STEP/mate/simulation and exported motion behavior SHALL remain valid without a new viewer engine or document field/version.

#### Scenario: Independent native placement comparisons pass

- **WHEN** the complete admitted project-repaired Dum-E carrying tree is evaluated at the prescribed native reference poses
- **THEN** the record reports each tested pose and worst translation/orientation error, all within acceptance tolerances

#### Scenario: A mocked importer alone is insufficient

- **WHEN** unit tests or earlier provisional limit observations pass but original-source refusal or the repaired full native motion/limits-only/STEP gates have not been executed successfully
- **THEN** the change remains incomplete and its record identifies the missing empirical proof

#### Scenario: Existing consumers retain their contracts

- **WHEN** unchanged STEP models and existing declared-joint/mate running models are built, simulated and exported after this change
- **THEN** their existing behavior and document format remain valid and models without native FreeCAD declarations do not require FreeCAD

### Requirement: Optional LGPL package and documented public contract

The implementation SHALL belong to the independent LGPL-2.1-or-later machinome-freecad distribution importing as machinome_freecad. It SHALL depend on machinome as an independently licensed package and SHALL require no FreeCAD-specific edits, monkeypatches or copied native implementation in the Apache core. Any unavoidable core integration failure SHALL be reported as evidence before a separate framework change is proposed. Incorporated third-party material SHALL retain its original copyright/licence and change notices. The package SHALL NOT redistribute the provisioned FreeCAD binary.

The package SHALL document its public imports, source-path resolution, native selector Names, supported graph, optional runtime setup, supported machinome compatibility, command/status observation and source-refresh behavior. The independent empirical author SHALL be able to construct and validate the simulation through that documented public API without calling adapter-private importer methods. Required native runtime absence SHALL fail clearly at point of use while plain imports and existing machinome-only models remain usable.

#### Scenario: Core remains independent

- **WHEN** machinome is installed and used without machinome-freecad or a FreeCAD runtime
- **THEN** its existing imports, supported builds and simulation behavior remain valid

#### Scenario: The documented example requires no private importer calls

- **WHEN** the independent Dum-E author follows the package public documentation
- **THEN** source realization, native coordinate selection and running commands work using FreeCADAssemblyNode, FreeCADJoint and the existing framework public APIs only

#### Scenario: Packaged provenance is retained

- **WHEN** wheel and source distributions are built and inspected
- **THEN** package licence and third-party notices are included, the worker is present, FreeCAD binaries are absent, and the recorded compatibility dependency is declared
