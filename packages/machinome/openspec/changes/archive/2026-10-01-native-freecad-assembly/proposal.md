## Why

Dum-E's native FreeCAD assembly already owns its grounded occurrences, fixed and revolute connections, connector frames and mechanical limits. The pilot needs to simulate it without maintaining a second mechanical definition, and a limits-only native edit must change running admission even when geometry is unchanged.

The originating evidence, source hashes and 2026-10-01 interface/package ratification are in `workflow/ongoing/dume-native-freecad.md`. MakersAsylumIndia/Dum-E is pinned at `1b317d2dc80165d0112c9444739476593fba3e48`. Native loading and provisional limits tests passed, but adversarial review finding 14 exposed an inconsistent native Fixed `Joint002` that the adapter wrongly admitted. The pilot has approved stricter constraint admission and correction of a project-owned native copy; the untouched original becomes expected-refusal evidence and the transparently repaired native copy becomes the primary positive motion proof.

## What Changes

- Implement the separate optional `machinome-freecad` package under LGPL-2.1-or-later, importing `FreeCADAssemblyNode` and `FreeCADJoint` from `machinome_freecad`.
- Preserve the ratified `freecad_source` class attribute and `FreeCADJoint("Joint001")` internal-Name reference, bound by the existing `Driver.drives(...)`, `Time.running()` and `Sim` APIs without project-authored mechanics.
- Resolve FCStd links and joints through a recorded FreeCAD runtime and native recomputation in a worker, compiling its grounded fixed/revolute graph into existing machinome coordinates and placement operations.
- Refuse native Fixed/Revolute constraint residuals outside recorded tolerances even when solve succeeds and saved placements remain stable. Honor the native constraint targets and valid orientation branches; an arbitrary saved Fixed offset is not a satisfied connection.
- Preserve every occurrence and connection, downstream carry, native saved coordinates, zero/sign/units and enabled bounds. Give useful refusals for missing selectors, native errors and unsupported graphs.
- Track semantic and linked-document edits independently of geometry so a fresh run observes native limit changes.
- Preserve the original failure and document the authorized `Joint002` correction in the independent project repository using FreeCAD-authored source, with upstream submodule and FreeCAD runtime unchanged. Preserve geometry and saved pose where possible and record every correction or unavoidable pose difference.
- Rerun the full nine-occurrence/four-coordinate native pose and STEP gates on the repaired copy, including 150° completion under 0–180° and blocking at 120° after a limits-only native maximum edit between otherwise identical repaired variants.
- Provide this package's public API/runtime documentation for the independent simulation author and retain original notices for any adapted third-party source.

## Capabilities

### New Capabilities

- `native-freecad-assembly`: Optional native FreeCAD grounded fixed/revolute assembly resolution, imported-coordinate references, source freshness and running behavior without duplicated mechanics.

### Modified Capabilities

None. Existing framework STEP, mate, declared-joint, simulation and export contracts are compatibility requirements consumed by this package.

## Impact

All FreeCAD-specific loading, conversion, native linkage, tests and source-derived material belong to this LGPL repository. The Apache-2.0 core remains a separate dependency and requires no edit under this plan; a proven unavoidable generic integration need must be reported before opening a separate framework cycle. The package pins/tests the existing framework internals it consumes and installs without bundling FreeCAD binaries. Native runtime absence is a point-of-use error.

The source tree, worker, packaging, public docs and package-owned OpenSpec records change here. Dum-E remains an independent AGPL wrapper repository with untouched pinned upstream submodule; its approved native repair and issue records live in that project, and upstream CAD is not copied into adapter fixtures. No FreeCAD fork, project-Python replacement mechanics or silent importer correction is authorized. The studio contract update belongs to its own repository after the API is proven. No viewer engine, document format change, publication, push or repository integration is authorized.
