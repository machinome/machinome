## MODIFIED Requirements

### Requirement: Expression cache pressure does not change a machine

A supported document SHALL load, pose and execute with the same results
regardless of expression-cache reclamation or prior supported documents
loaded on the page. A document whose live expression working set exceeds
the cache's reclamation threshold SHALL NOT fail or evaluate differently
solely because it crosses that threshold. Existing malformed-document
refusals and document-local binding meanings SHALL remain unchanged.

This promise SHALL include a large posed portable export whose operations
and flexible parameters read a shared ordered binding table. The complete
valid export SHALL mount with its published rigid and flexible geometry,
driver defaults and declared instruction targets; loading SHALL not stall
indefinitely before geometry is requested solely because its valid binding
table exceeds expression-cache headroom. Invalid content in such a document
SHALL still be refused before rendering it, preserving any last good model.

When a supported machine's prepared expression graph fits within the
viewer's finite cache capacity, consecutive ticks SHALL reuse that graph
without reclaiming and reparsing it between those ticks. This reuse SHALL
NOT change the machine's admitted travel, coordinate bank, event records,
snapshot/replay behavior, numerical semantics or refusal behavior.

Expression retention across repeated publications SHALL be bounded by
current live work and cache headroom, not accumulated publication history.
Disposing of the last viewer SHALL release retained expression state.

#### Scenario: A large operating machine opens

- **WHEN** a supported operating machine's expression working set crosses
  the cache reclamation threshold while its document is loaded
- **THEN** mounting completes and its initial pose and subsequent request
  results match the same machine without cache pressure

#### Scenario: A complete binding-rich posed printer opens

- **WHEN** the complete supported Voron-2 portable export is opened with
  its ordered bindings, rigid model assets and flexible parts intact
- **THEN** the viewer mounts the full assembly, renders its default pose
  and permits its declared Home, Center and Present targets with the same
  placements and flexible shapes the published expressions describe

#### Scenario: Large invalid content is refused before replacement

- **WHEN** a large posed document carries an invalid binding or unsupported
  expression, including one reached through an operation or flexible parameter
- **THEN** loading refuses that content by the existing named error, no
  tree is rendered from it, and a last good model remains standing

#### Scenario: Consecutive ticks reuse a fitting graph

- **WHEN** a supported running document has a prepared graph within the
  finite cache capacity and advances several consecutive ticks
- **THEN** those ticks reuse the prepared graph without a cache generation
  change between ticks and produce the same complete bank and event records
  as evaluation under forced reclamation

#### Scenario: Reclamation happens between operations

- **WHEN** the expression cache is reclaimed after a machine has loaded
  and before it is posed or stepped again
- **THEN** it produces the same values, stops and request outcomes as it
  would without that reclamation, never values from another expression

#### Scenario: Documents keep their own binding meanings under pressure

- **WHEN** two mounted documents use the same binding names for different
  expressions and loading or operating either creates cache pressure
- **THEN** each continues to pose and operate according to its own bindings

#### Scenario: Reload history is not retained indefinitely

- **WHEN** a host repeatedly replaces a document with supported documents
  of a bounded working-set size, including a failed replacement
- **THEN** obsolete expression state is reclaimed, the last good model
  continues to operate correctly, and retained expression state does not
  grow with the number of past replacements

#### Scenario: The final viewer is disposed

- **WHEN** the last viewer is disposed after operation under cache pressure
- **THEN** no expression state remains retained by the viewer

### Requirement: Fresh mounts draw loaded rigid assets independently of fetch completion order

For a fixed published document, viewer build, browser rendering environment, view and pose, the viewer SHALL produce the same fully loaded image on fresh mounts when rigid model or marking STL requests complete in different orders. It SHALL continue to request independent assets concurrently and SHALL preserve the document's geometry, model and marking colours, depth behavior and marking-surface bias. A failed load SHALL discard the mesh newly reserved by that load and dispose its material and any geometry returned to it before rejection, without attaching an unready mesh; a targeted update SHALL retain its existing prepare-before-mutation and failure-containment behavior.

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

- **WHEN** a rigid model or marking load fails to fetch or prepare its geometry after reserving its mesh and material
- **THEN** that load rejects, its own reserved mesh is discarded, its material and any geometry returned to it are disposed, and no blank mesh from that load was attached

#### Scenario: A targeted replacement fails

- **WHEN** a model or marking replacement fails during `artifactChanged()` or `manifestChanged()`
- **THEN** the previous visible model and camera remain usable, and that failed replacement discards its newly reserved mesh and disposes its material and any returned geometry

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
- **THEN** each part still owns separate geometry and material, disposing or replacing one cannot change the other's geometry, and a later genuine artifact update reads the current resource
