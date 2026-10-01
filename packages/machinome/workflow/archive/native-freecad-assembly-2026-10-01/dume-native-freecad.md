# Dum-E: reuse native FreeCAD joints in simulation

Status: interface ratified by the pilot on 2026-10-01; implementation and
empirical validation authorized, not yet completed. Static inspection establishes
the native data below; it does not establish runtime compatibility or motion
parity. The OpenSpec change will own the implementation contract. This workflow
record preserves the originating evidence, ratification, and cycle discipline.

## Package boundary ratified on 2026-10-01

The pilot subsequently directed: “let's make this a separate package,
machinome-freecad LGPL-2.1-or-later, and you are free to link. go on, same
plan, just in a different package.” This supersedes implementation inside
the Apache-2.0 framework and changes the public import to
`from machinome_freecad import FreeCADAssemblyNode, FreeCADJoint`.

All FreeCAD-specific code, tests, worker integration, and any source-derived
material belong in this independent LGPL-2.1-or-later repository. The adapter
may link to FreeCAD and depend on machinome. Retain upstream copyright and
licence notices for any reused material; linkage permission is not permission
to remove attribution or relicense third-party code. The Apache-2.0 framework
remains a separate dependency, not a vendor tree. Do not modify it unless an
empirical integration failure requires a separately scoped framework change.

The earlier framework proposal draft was stopped before implementation. No
FreeCAD implementation was copied into it; source excerpts informed planning.
The new package is the implementation owner from this decision onward.

## Pilot ratification and cycle discipline

The pilot ratified the interface shown below and directed its implementation
on 2026-10-01: “ratify the interface. save this to workflow. then implement it.”
The ratified spelling is `machinome_freecad.FreeCADAssemblyNode` with
`freecad_source`, and `FreeCADJoint("Joint001")` as a reference to an imported
coordinate, bound by an existing `Driver.drives(...)` relation. No manual
joint, axis, frame, or mechanical-limit declarations are required in the project.
Changes to that interface or materially different behavior require a new pilot
decision; deployment details are to be tested, not silently presented as proven.

The pilot also authorized this cycle's empirical discipline:

1. Create an independent local repository at `projects/Robotic-Arms/Dum-E`.
   License its original wrapper/simulation work AGPL-3.0-or-later, copyright
   2026 Luis Henrique Cassis Fagundes. Keep the original upstream as a pinned
   Git submodule under `upstream/`; do not relicense its content.
2. A GPT-6.1 Sol subagent proposes the adapter change; a separate GPT-6.1 Sol
   subagent applies it. The primary agent checks the proposal against this
   ratification and performs adversarial review of the implementation.
3. One separate GPT-6.1 Sol subagent authors and runs the Dum-E simulation
   through the new public API. It must report framework failures instead of
   bypassing them with private APIs or project-local mechanical definitions.
4. The cycle is validated by that real project, including the limits-only
   experiment below, not solely by mocked importer tests. Preserve failures and
   corrections in the records. Finish with project and framework validation.

Adapter repository: `machinome-freecad/`; development worktree:
`machinome-freecad/WTs/native-freecad-assembly`. The earlier framework worktree
`machinome/WTs/native-freecad-assembly` is superseded as implementation owner.
Framework reference base: `8a8a26711bcd7fd33c6daf7f8866d10004574f8c`.
The original exploratory note is recorded at framework commit
`0adff7040dc29839b30844a4ccb02e0769c2423b`. No push, publication, or integration
into another repository is authorized by the package decision.

## Originating need

The pilot's requirement is: “I want to simulate Dum-E without having to
re-declare its joints and limits already authored.”

FreeCAD should remain the complementary authoring tool and source of truth
for this assembly's geometry and mechanical connections. Machinome should
add operating intent, running simulation, scenarios, and observations without
making the project maintain a second mechanical definition.

The finding is duplication required by a geometry-only route, not a measured
failure of an existing native importer. The existing STEP reader/scaffolder
does not recover this FreeCAD joint graph. This note does not claim that every
STEP application protocol is incapable of representing kinematics; it compares
the actual geometry-import route with the native data inspected here.

## Evidence: a specific native assembly

Source: [MakersAsylumIndia/Dum-E](https://github.com/MakersAsylumIndia/Dum-E),
pinned at `1b317d2dc80165d0112c9444739476593fba3e48`.

- [Assembly document](https://github.com/MakersAsylumIndia/Dum-E/blob/1b317d2dc80165d0112c9444739476593fba3e48/MA_Dum_E_v2_Assembly.FCStd):
  `MA_Dum_E_v2_Assembly.FCStd`.
  SHA-256: `db9bc7ba69f7375e1d1dcc096f20ddc3694a9eb314da8d3bee1c9d7ed0078878`.
- [Linked parts document](https://github.com/MakersAsylumIndia/Dum-E/blob/1b317d2dc80165d0112c9444739476593fba3e48/MA_Dum_E_v2.FCStd):
  `MA_Dum_E_v2.FCStd`.
  SHA-256: `44e4548b19aa6c510d51b22f0330d6aaf721ec5816e2bec2e22ebbd434f97d54`.

Method: inspect `Document.xml` inside each FCStd ZIP archive. Both record
`SchemaVersion="4"` and `ProgramVersion="1.1R20260414 (Git shallow)"`.
These are file metadata, not a verified runtime compatibility requirement.
No FreeCAD solver or STEP export was run for this finding.

The assembly contains an `Assembly::AssemblyObject` named `Assembly`, nine
`App::Link` occurrences referencing the parts document, and a `GroundedJoint`
whose `ObjectToGround` is `Feet`. Its eight joints are all unsuppressed:

| Native Name | Label | Type | Connected occurrences | Enabled angular bounds |
| --- | --- | --- | --- | --- |
| `Joint` | `Fixed002` | Fixed | Feet → Base | Not applicable |
| `Joint001` | `Revolute001` | Revolute | Base → Turn_table | 0° to 180° |
| `Joint002` | `Fixed003` | Fixed | Turn_table → Shoulder | Not applicable |
| `Joint003` | `Revolute003` | Revolute | Shoulder → Arm2 | None |
| `Joint004` | `Revolute004` | Revolute | Arm2 → Arm1 | None |
| `Joint005` | `Revolute005` | Revolute | Arm1 → Wrist | None |
| `Joint006` | `Fixed` | Fixed | Wrist → Phone_back | Not applicable |
| `Joint007` | `Fixed001` | Fixed | Phone_back → Phone_bottom | Not applicable |

`Joint001` has `EnableAngleMin=true`, `AngleMin=0`,
`EnableAngleMax=true`, and `AngleMax=180`. The other three revolutes have
both enable flags false: their stored zero bounds must not become locked
joints or invented zero-to-zero ranges.

The joints also carry `Reference1/2`, `Placement1/2`, and `Offset1/2`.
For example, `Joint001` references `Base.Edge234` and
`Turn_table.Edge193`. Those references and connector frames are evidence
that connection placement was authored, not something the importer should
guess from cylindrical faces. The generic `Angle` property's own description
says it is used only by the Angle joint; its zero value is not evidence of
a revolute's current coordinate.

The parts document contains twelve PartDesign bodies, sixty sketches and
eleven SubShapeBinders. The assembly links nine bodies; the three O-ring
bodies are not assembly occurrences. Importing every body would therefore
change the selected machine. Native feature history and cross-body references
are additional authoring value, but this first requirement does not need to
expose them in machinome. No spreadsheets or nonempty expression engines
were found; they are not this project's empirical justification.

Licence provenance needs care before distributing fixtures: the pinned
[README](https://github.com/MakersAsylumIndia/Dum-E/blob/1b317d2dc80165d0112c9444739476593fba3e48/README.md)
declares CERN-OHL-S-2.0 for hardware, MIT for software, and CC-BY-4.0 for
documentation, while both FCStd documents embed “All rights reserved” and
an older CERN-OHL-v1.2 URL. Record this discrepancy rather than resolve it by
assumption. This note redistributes no CAD files.

## Smallest useful capability

Load the saved native assembly and its linked document, resolve its authored
mechanics, and materialize a machinome assembly whose joint coordinates can
be driven through the existing simulation API.

FreeCAD owns occurrence identity, geometry, grounding, connections, connector
frames, enabled limits, and saved assembly state. Machinome owns the chosen
command inputs, trajectories, timing, scenarios, and assertions. A driver
says what to command; it must not repeat a joint's axis, origin, type, or range.
Native joints do not imply motors, speeds, torque, collision constraints, or
physical stops that were never authored.

The initial scope is this native Assembly document's grounded tree of fixed
and revolute joints. Preserve all nine occurrences and all eight connections,
including the four fixed connections. Fixed connections need not fuse solids.
Only joints explicitly bound to operating inputs become commandable; other
revolutes remain at their resolved saved coordinates for this kinematic test.

Use FreeCAD's document/recompute facilities to resolve the source rather than
making this evidence-inspection XML script the production file interpreter.
Pin and report the runtime used, load the linked file, reject recompute errors,
and compare its resolved placements with the saved source before proceeding.
Do not silently substitute stale cached shapes when native resolution fails.
Whether the adapter is packaged in-process or as an optional worker remains
open; the evidence does not yet choose a deployment architecture.

Compile the resolved tree into machinome's existing joint and placement
machinery. The flat FreeCAD occurrence list is not itself the carrying
hierarchy: movement of the turntable must carry the shoulder, arms, wrist,
and phone holder. Preserve native occurrence identifiers through any internal
reparenting. Validate frame orientation, positive angle, zero, and units;
do not treat the saved pose as the zero-angle definition.

Existing framework contracts to preserve are `openspec/specs/step-assembly`,
`openspec/specs/mates`, ADR-079 and ADR-147 in the machinome repository at
the reference base above.
This is not a replacement for `StepNode`, `StepAssembly`, or one-shot
`import-step` scaffolding, and does not require a new viewer motion engine.

## Ratified interface

The following names and module are ratified for implementation. They are not
a released capability until the cycle is implemented, validated, and released:

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

`FreeCADJoint` selects and aliases an existing imported coordinate; it does
not declare another joint. It accepts no replacement axis or range. All native
joints are imported whether or not the project gives them an alias. The string
is the external document's internal `Name`, not the editable display label.
`turntable` is then an ordinary declaration reference for `drives`, not a
second independently bound coordinate. Missing names, fixed-joint selections,
or unsupported coordinate types must produce useful errors.

`default=0` is the project's requested initial turntable command, not a new
mechanical zero definition. Initialization must validate that request against
the imported bounds and resolve the remaining coordinates from the source.
The importer must resolve the source before validating drive targets and
binding the graph; the precise declaration/materialization lifecycle needs
an implementation probe; a contradictory result must return to the pilot.

An inspection report should expose native Names, labels, occurrence endpoints,
types, resolved frames, units, enabled limits, and unsupported objects, so users
can select a coordinate without reverse-engineering the FCStd file. The report
is a proposed diagnostic need, not a second API designed in this note.

## Decisive experiment: a limits-only change

The test must distinguish native semantics from geometry import. A robot that
merely looks right in the viewer does not establish this capability.

1. Resolve both pinned files in a recorded FreeCAD runtime. Verify the nine
   occurrences, grounded Feet, eight joints, enabled flags, and the native
   angle convention. Compare multiple turntable poses and one pose per other
   revolute with FreeCAD before trusting the coordinate mapping.
2. Establish a common saved pose inside both candidate ranges. Make two
   project-owned source variants through FreeCAD: the original 0–180° range
   and a variant changing only `Joint001.AngleMax` to 120°. Keep joint frames,
   geometry, and saved pose unchanged. Record hashes and semantic differences;
   verify unchanged resolved solids and placements within recorded tolerances,
   rather than relying on byte-identical STEP exports.
3. Use one unchanged machinome simulation definition with no declared joint
   axes or limits. Start its turntable command at 0° and request 150° over one
   second. With the original source it must reach 150° and complete. After
   replacing the source with the 120° variant and rebuilding, a fresh run must
   stop at 120° and report the command as blocked.
4. Verify all downstream occurrences follow correctly, the grounded end stays
   fixed, and fixed connections retain their relative transforms. Verify that
   the other revolutes' disabled limit flags do not lock them at zero.
5. Run the geometry-only STEP path as a control. Record the joint/frame/limit
   declarations needed to reproduce the same behavior and which must be edited
   after the native limit change. Do not claim a STEP comparison was performed
   until these observations exist.

Acceptance: zero duplicated mechanical declarations, pose parity against the
native reference within explicitly chosen tolerances, and changed simulation
behavior from a native limit edit alone. Record setup effort, manual mappings,
refresh time, and failures as well as success. Screenshots supplement numerical
placement and command-status assertions; they do not replace them.

The bounds must govern simulation admission, not merely a slider's displayed
range. A semantic change must invalidate the import cache even when geometry
is unchanged. Cache identity must cover linked documents and the relevant
native mechanics, not just tessellation. Rebuild into a fresh simulation;
silently reinterpreting an active run under a different source is out of scope.

## Development sequence and limits

Record the already-ratified interface in the smallest adapter OpenSpec
change, then implement red-first against the limits-only regression. Native
resolution and pose parity must be established, not assumed from XML inspection.
Use the separate Dum-E simulation subagent for end-to-end validation; an importer unit test alone does
not settle the originating need. Do not turn this note into a general FreeCAD
integration campaign without another project's concrete finding.

Refuse unsupported joint types, unresolved references, ambiguous assembly
selection, or unsupported graphs rather than silently flattening them. The
first experiment does not promise closed-loop solving, Assembly3/A2plus,
dynamic physics, inverse kinematics, automatic actuator inference, native
sketch editing in machinome, bidirectional live synchronization, or FreeCAD
execution in a browser. A clear error is preferable to plausible but wrong
mechanics.

Open questions are the FreeCAD runtime and packaging boundary, angle/placement
parity after recomputation, declaration binding timing, and fixture licensing.
None requires the pilot to re-author the native joints as the proposed solution.
