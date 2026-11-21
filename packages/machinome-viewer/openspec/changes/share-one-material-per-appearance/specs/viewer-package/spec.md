## MODIFIED Requirements

### Requirement: Fresh mounts draw loaded rigid assets independently of fetch completion order

For a fixed published document, viewer build, browser rendering environment, view and pose, the viewer SHALL produce the same fully loaded image on fresh mounts when rigid model or marking STL requests complete in different orders. It SHALL continue to request independent assets concurrently and SHALL preserve the document's geometry, model and marking colours, depth behavior and marking-surface bias. A failed load SHALL discard the mesh newly reserved by that load, dispose any geometry returned to it and retain nothing made for that mesh alone before rejection, without attaching an unready mesh or changing any other part's geometry or look; a targeted update SHALL retain its existing prepare-before-mutation and failure-containment behavior.

Complete supported assemblies SHALL load without exhausting the browser's pending geometry-request capacity through unrestricted viewer request fan-out, including when more than one viewer mounts or reloads in the same page. This SHALL retain independent overlapping loads and every required rigid model and marking, with no geometry omission or permanent substitution cache. A viewer's readiness SHALL wait for all its required assets; a failed required asset SHALL reject loading rather than yield a partially accepted assembly. A failed or disposed owner's outstanding loads SHALL NOT prevent other viewers from completing, attach late geometry to the discarded owner, or retain abandoned reserved meshes, materials or returned geometry.

#### Scenario: Coincident sibling models complete in opposite orders

- **WHEN** two differently coloured, coincident sibling models in the same document are mounted twice and their STL response completion order is reversed
- **THEN** the two fully loaded captures at the same view and pose have exactly equal pixels, with neither model's colour selected by network completion order

#### Scenario: Model and markings resolve out of order

- **WHEN** a rigid part's model and multiple declared markings finish loading in different orders on fresh mounts
- **THEN** the fully loaded images agree exactly, each marking keeps its own declared colour and existing surface bias, and independent requests have been allowed to overlap

#### Scenario: Genuine depth remains authoritative

- **WHEN** two noncoincident rigid surfaces with different depth are loaded in opposite network orders
- **THEN** the nearer surface still occludes the farther one as before, regardless of completion order

#### Scenario: One newly reserved load fails

- **WHEN** a rigid model or marking load fails to fetch or prepare its geometry after reserving its mesh
- **THEN** that load rejects, its own reserved mesh is discarded, any geometry returned to it is disposed, nothing made for that mesh alone is retained, every other part is drawn as before, and no blank mesh from that load was attached

#### Scenario: A targeted replacement fails

- **WHEN** a model or marking replacement fails during `artifactChanged()` or `manifestChanged()`
- **THEN** the previous visible model and camera remain usable, and that failed replacement discards its newly reserved mesh, disposes any returned geometry and retains nothing made for that mesh alone

#### Scenario: Two large viewers mount together

- **WHEN** two supported complete assemblies mount or reload concurrently in the same page, including the full Voron-2 export
- **THEN** their geometry requests remain within a finite shared admission budget, independent assets overlap, all required assets load and each viewer renders its own complete assembly

#### Scenario: Queued assets retain deterministic drawing

- **WHEN** a fresh assembly has more models and markings than can be fetched together and the admitted assets complete in different orders
- **THEN** all assets eventually appear and fully loaded images at the same pose agree exactly under the existing draw-order, colour, depth and marking-bias rules

#### Scenario: A failed owner leaves another viewer usable

- **WHEN** one viewer's initial load, reload or prepared targeted replacement fails while another viewer has pending geometry
- **THEN** the failure retains its error and discards its abandoned new resources, the other viewer can finish, and an existing last good model and camera remain usable

#### Scenario: Disposal during queued and active loading

- **WHEN** an owner is disposed with geometry not yet requested and geometry already being fetched
- **THEN** its unstarted loads do not issue requests, late returned geometry is disposed without attachment, its outstanding promises settle, and another viewer can continue when active requests retire

#### Scenario: Repeated paths retain separate part ownership

- **WHEN** multiple parts name the same model URL and their overlapping loads share a network request
- **THEN** each part still owns separate geometry, disposing or replacing one cannot change the other's geometry or look, and a later genuine artifact update reads the current resource

#### Scenario: Parts of one colour stay independent

- **WHEN** two parts declare the same colour and an in-place update removes one of them, replaces its model, or fails while preparing its replacement
- **THEN** after each of those the other part is drawn exactly as it was before it, and nothing made for the two parts is retained once neither remains in the viewer or the viewer is disposed
