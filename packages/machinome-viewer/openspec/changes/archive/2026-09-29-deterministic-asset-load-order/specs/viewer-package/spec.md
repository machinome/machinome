## ADDED Requirements

### Requirement: Fresh mounts draw loaded rigid assets independently of fetch completion order

For a fixed published document, viewer build, browser rendering environment, view and pose, the viewer SHALL produce the same fully loaded image on fresh mounts when rigid model or marking STL requests complete in different orders. It SHALL continue to request independent assets concurrently and SHALL preserve the document's geometry, model and marking colours, depth behavior and marking-surface bias. A failed load SHALL discard the mesh newly reserved by that load and dispose its material and any geometry returned to it before rejection, without attaching an unready mesh; a targeted update SHALL retain its existing prepare-before-mutation and failure-containment behavior.

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

- **WHEN** a rigid model or marking load fails to fetch or prepare its geometry after reserving its mesh and material
- **THEN** that load rejects, its own reserved mesh is discarded, its material and any geometry returned to it are disposed, and no blank mesh from that load was attached

#### Scenario: A targeted replacement fails

- **WHEN** a model or marking replacement fails during `artifactChanged()` or `manifestChanged()`
- **THEN** the previous visible model and camera remain usable, and that failed replacement discards its newly reserved mesh and disposes its material and any returned geometry
