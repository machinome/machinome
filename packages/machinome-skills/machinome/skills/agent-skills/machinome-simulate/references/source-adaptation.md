# Adapting source geometry

Choose the route from what the upstream supplies. Confirm the current adapter
names, supported options, and build tracking in official machinome documentation
for the installed version; this guide does not define an API.

## Native CAD and OpenSCAD

Import the original Python CAD implementation and instantiate the selected
configuration instead of copying its code. Preserve its dependency versions and
initialization assumptions. Keep any path adaptation local to the simulation
package and record why it is needed.

For OpenSCAD, preserve the source file and its relative include/use relationships.
Use a file-based import through the documented adapter. Inlining a source file's
text can change where its nested dependencies resolve. A top-level-only drawing
may need a small wrapper in the adaptation layer. Verify rebuilds when an imported
source or configuration changes.

## STL

Establish units and coordinate frames before measuring. Some design repositories
export every part in assembled coordinates; others export print orientations.
Check the assembly guide and compare multiple parts before translating anything
to an assumed local origin.

Determine whether a file contains one part or a pack of bodies. Select bodies
explicitly using the documented adapter's inventory. Record mesh defects instead
of silently repairing them. Do not present a display mesh as an exact or
manufacturing-qualified solid.

Retain useful measurement probes in the project and record their results with
the source revision, units, frame and precision. Bounding boxes help inventory a
file; they do not by themselves identify bearing axes or mounting hole centers.

## STEP

Prefer the document's product identities and assembly occurrence transforms over
inferred placement. Distinguish a part's own frame from each occurrence's world
placement. Use the documented import or scaffolding facility if available, then
treat generated source as project-owned code; do not overwrite edits by casually
regenerating it.

Check the selected product when names are ambiguous or a file contains several
parts. Choose tessellation appropriate for visual inspection without confusing
the display mesh with the underlying exact solid. Record any explicit correction
or unsupported mirrored/scaled placement.

## DXF plates and other profiles

Preserve layers, units, outlines and holes from the drawing. Import the source
profile through the supported tooling rather than restating every coordinate.
If hole positions must be extracted for assembly, retain the extraction and
validate its readings against the file. Sheet thickness is separate evidence;
do not infer it from a two-dimensional outline.

## URDF, assembly files, and configuration tables

Reuse the upstream joint axes, nesting, units and home configuration. A transform
chain is order-dependent: copying its final translations without its nesting can
produce a plausible but incorrect machine.

Prefer parsing the source when the runtime permits it. If transcription is
necessary, record the source and compare every relevant value with a source-drift
test. For unsupported constructs, document the interpretation and check it
against a source assembly export or another independent observable.

## Purchased hardware and flexible components

Model missing hardware only to the fidelity needed by the reconstruction's
interfaces. Use evidenced catalogue dimensions; threads, fillets and internals
are not automatically necessary. Mark substitutes and unknowns clearly.

Use the documented flexible-part facilities for belts, springs, cables and
similar parts when available. Derive routing and changing dimensions from the
parts they connect. Distinguish a shape that follows pose from a model that proves
tension, elasticity, or transmitted force.

## Fetched assets and attribution

Record canonical source, revision or checksum, selected files, and attribution
for any fetched geometry. Use the project's ignored cache convention for assets
it does not redistribute. A fetch-at-build arrangement is not evidence of license
permission; preserve known terms and report missing information.

Keep the original design, reconstruction code, and resulting media distinguishable
in the project's credits. Do not infer authorship from the person who uploaded a
file or replace upstream license notices with the skill package's license.
