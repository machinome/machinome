---
name: machinome-simulate
description: Add a machinome assembly and simulation layer to an existing mechanical design, preserving its source geometry. Use when asked to reconstruct, assemble, animate, or simulate a machine supplied as CAD source, STL, STEP, URDF, or assembly files. Does not provide structural, fluid, or dynamic physics analysis.
license: GPL-2.0-or-later OR CERN-OHL-S-2.0+
---

# Reconstruct an existing machine

Turn the supplied design into an inspectable, operable model. Keep the simulation
in the consuming project's repository, usually in a thin `simulation/` package.
Preserve the user's requested slice and build order; an incomplete source is a
finding, not permission to invent the rest of the machine.

Use the project's existing environment and planning conventions. OpenSpec is
appropriate when that project uses it or the user requests it; do not install
it or impose a commit sequence. No Studio checkout, agent roster, or watcher is
required. Confirm the actual repository boundary before writing into an imported
project, and preserve its existing manifest and unrelated changes.

## Establish evidence and capabilities

Read the source project's README, assembly instructions, configuration, license
and attribution records, and relevant tests. Identify the source revision and
the evidence for part placement. Record unresolved measurements and the user's
intended controls before implementing consequential choices.

Identify the installed machinome version and consult its official documentation
for the adapters and motion needed. If Context7 is available, resolve `machinome`
and query the relevant topic, checking its source and version. If it is unavailable
or stale, use the official documentation linked by the package or the
[upstream repository](https://github.com/machinome/machinome), or matching
documentation supplied locally. Confirm CLI options with
the installed command's help. Do not assume an example from a newer release is
available, hard-code a Context7 library ID, or install an integration implicitly.

The companion `machinome` skill supplies detailed component-building and contract
guidance when installed. This workflow can also run on its own with the official
documentation; its essential reconstruction checks are stated below.

## Read the design into the assembly

Consult [source adaptation](references/source-adaptation.md) for the formats the
project actually supplies. Establish:

- The source of truth for each part: native CAD, a mesh, an exact solid, or a
  purchased component identified by the assembly documentation.
- Units, handedness, origins, and whether files already share an assembly frame.
- What can be imported directly: configurations, joint definitions, layout
  tables, home poses, or the author's own assembly exports.
- Which hardware is omitted from the CAD, and what dimensioned evidence is
  available to represent it. Keep unknown dimensions explicit.

Use documented adapters instead of redrawing existing parts. Keep source imports
and their build dependencies visible. Leave upstream geometry unchanged unless
the task explicitly includes modifying it. If assembly requires a correction,
record the measured conflict and proposed correction before implementing it in
the adaptation layer. Do not turn missing licensing information into permission
to redistribute source assets or contact the author.

Keep the coordinate convention, placement evidence, simplifications, and open
questions in the project's design record. When transcribing layout data that
cannot be imported, add a test comparing the transcription against its source.

## Build a small, usable increment

Add the model declaration to the existing project configuration without replacing
unrelated settings or choosing a Studio profile. Get a partial root building
early, then compose subassemblies in the requested order or their physical
dependency order. State what the current slice includes.

Assign motion to the body that moves using documented joints and relationships.
Keep rest transforms separate. Give coupled dimensions a common owner and
derive positions from measured relationships rather than independently adjusted
numbers. Preserve recognizable material colors or the upstream color scheme.

Expose controls by what the operator intends. A printer's useful inputs are
nozzle coordinates; a coordinated robot may need body pose and gait controls.
Use one input per actuator where independent operation is meaningful. Do not
hide a joint the requested task needs, or expose every motor merely because a
slider is easy. Choose ranges from evidence and identify assumed limits.

Provide a small set of meaningful operations, such as Home and Present or Rest
and Walk, using the facilities supported by the installed version. Include
automatic motion only when it serves the machine and requested demonstration.
Distinguish normalized animation time from physical seconds and distinguish
kinematic motion from an assertion about forces or material response.

## Prove the reconstruction

Write and run failing contracts before implementing the corresponding interfaces,
then bring them green. Include these checks where they apply:

- Mating features occupy the measured frame: rods through bearings, bolts at
  mounting holes, belts at their pulleys, feet on their support plane.
- Manufactured pieces are connected; separate rigid pieces have no unintended
  overlap. If upstream assets already overlap, record the exact affected pairs
  and measured overlap as a checked inventory, not a blanket exemption.
- Driving pairs engage within the intended play, as well as moving at the right
  ratio. Non-interference alone also passes when the pieces are far apart.
- Operations reach independently calculated targets, with geometry sampled along
  their transition paths. A plausible endpoint does not validate the route.
- Transcribed source data has not drifted. Relevant parameter changes still
  produce the intended assembly.

For each materially new interface, introduce a representative wrong placement
or relationship temporarily and confirm its contract fails; restore and recheck.
Run assembly regression, including documented exact checks where supported, and
report limits for mesh-only sources. Do not weaken a contract to accommodate an
unexplained discrepancy.

Build the model and inspect images at rest and at a meaningful operating pose
from useful views. Use an actual operation to verify retained state; a snapshot
of input values does not replay its history. When tools cannot execute a check
or display an image, identify the missing evidence in the delivery.

## Deliver the layer and its findings

Document how to build and view this model, what each control means, the demo
operations, verified interfaces, source provenance, and reconstruction assumptions.
Record design discrepancies and framework limitations in the consuming project.
Keep fetched assets and generated builds out of source commits as appropriate to
the project's rules. Preserve upstream credits and distinguish adaptation work.

Finish the project's requested planning, testing, and commit workflow. Report
what was verified and what is incomplete; do not call a partial reconstruction
the complete machine. Export, publication, issue submission, and contacting
authors remain separate actions governed by the user's request.
