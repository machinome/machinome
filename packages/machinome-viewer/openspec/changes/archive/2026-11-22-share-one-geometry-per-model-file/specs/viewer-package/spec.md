## ADDED Requirements

### Requirement: Parts that name one model file share one geometry

Within one viewer, the rigid parts and markings that ask for the same model file in one reading of it SHALL be drawn from one geometry, held once in the page and uploaded once to the viewer's graphics context. A reading SHALL be one request for the file and one parse of its response. A part SHALL join a reading only while the reading's request has not settled. No part SHALL join a geometry already on screen, and no reading SHALL outlive its request: the viewer SHALL keep no cache of geometry or bytes.

Sharing SHALL NOT change the fully loaded picture, the order of drawing, picking, a part's bounds or position on screen, highlights, the markings drawn, the admission of requests, readiness, or the last good model a failed update leaves. A geometry SHALL be freed, in the page and in the graphics context, once no part holds it and no load is still waiting on its reading, and SHALL NOT be freed while a part on screen shows it; a reading that every part waiting on it abandoned SHALL be freed when it arrives, without being drawn. Two viewers in one page SHALL NOT hold one geometry: disposing a viewer SHALL free every geometry it held whatever another viewer still shows.

#### Scenario: Parts of one machine name one file

- **WHEN** a document whose parts name one model file several times, among more files than can be fetched together, is mounted
- **THEN** each named file is requested once and parsed once, the parts naming one file are drawn from one geometry uploaded once, and the fully loaded picture equals the picture of the same document in which every part names its own copy of the same bytes

#### Scenario: A part sharing its file is replaced or removed

- **WHEN** an update replaces or removes one of several parts drawn from one geometry, or the viewer's cleanup runs more than once
- **THEN** the other parts are drawn exactly as before from that geometry, and the geometry is freed once, when the last part holding it is replaced, removed or disposed

#### Scenario: A marking names the file its part names

- **WHEN** a part and a marking, or two markings, name one model file
- **THEN** the file is requested and parsed once, each marking is drawn lifted from the file's geometry as before, and the part's geometry stays drawn

#### Scenario: Parts of two updates are drawn from one reading

- **WHEN** an update asks for a model file while an earlier update's request for it is still outstanding, and the earlier update's parts are then replaced by the later's
- **THEN** no second request is made while the first is outstanding, as before, the parts of both are drawn from that reading's one geometry, and the geometry stays drawn until the last part holding it is replaced, removed or disposed

#### Scenario: A republish adds a part naming a file on screen

- **WHEN** `manifestChanged()` adds a part naming a model file that parts already on screen were loaded from
- **THEN** the file is requested and parsed for the new part, and the parts already on screen keep the geometry they show

#### Scenario: Every part waiting on a reading is abandoned

- **WHEN** a viewer, a pending reload or an update is disposed or fails while a request it alone was waiting on is still outstanding
- **THEN** when the response arrives nothing is drawn from it and its geometry is freed, and no other part's geometry or look changes

#### Scenario: Two viewers mount one document

- **WHEN** two viewers in one page mount documents whose parts name the same model files, and one of them is disposed
- **THEN** each viewer draws from geometry of its own, the disposed viewer's geometry and graphics buffers are freed, and the other viewer is drawn exactly as before

## MODIFIED Requirements

### Requirement: Fresh mounts draw loaded rigid assets independently of fetch completion order

For a fixed published document, viewer build, browser rendering environment, view and pose, the viewer SHALL produce the same fully loaded image on fresh mounts when rigid model or marking STL requests complete in different orders. It SHALL continue to request independent assets concurrently and SHALL preserve the document's geometry, model and marking colours, depth behavior and marking-surface bias. A failed load SHALL discard the mesh newly reserved by that load, release any geometry returned to it, which is freed unless another part holds it, and retain nothing made for that mesh alone before rejection, without attaching an unready mesh or changing any other part's geometry or look; a targeted update SHALL retain its existing prepare-before-mutation and failure-containment behavior.

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
- **THEN** that load rejects, its own reserved mesh is discarded, any geometry returned to it is released and freed unless another part holds it, nothing made for that mesh alone is retained, every other part is drawn as before, and no blank mesh from that load was attached

#### Scenario: A targeted replacement fails

- **WHEN** a model or marking replacement fails during `artifactChanged()` or `manifestChanged()`
- **THEN** the previous visible model and camera remain usable, and that failed replacement discards its newly reserved mesh, releases any returned geometry and retains nothing made for that mesh alone

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
- **THEN** its unstarted loads do not issue requests, late geometry is not attached to it and is freed unless a part of a live viewer holds it, its outstanding promises settle, and another viewer can continue when active requests retire

#### Scenario: Repeated paths retain separate part ownership

- **WHEN** multiple parts of one viewer name the same model URL and ask for it in one reading
- **THEN** each part holds its own share of one geometry, disposing or replacing one cannot change the other's geometry or look, the geometry is freed when no part holds it, and a later genuine artifact update reads the current resource

#### Scenario: Parts of one colour stay independent

- **WHEN** two parts declare the same colour and an in-place update removes one of them, replaces its model, or fails while preparing its replacement
- **THEN** after each of those the other part is drawn exactly as it was before it, and nothing made for the two parts is retained once neither remains in the viewer or the viewer is disposed
