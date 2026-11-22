## Context

Every rigid part and marking reaches its geometry through `loadMesh` (`src/tree.ts` 897): it reserves the mesh and its material in document order on an empty placeholder, asks the page-wide admission queue (`src/geometry-admission.ts`) for its URL, and on admission calls `STLLoader.loadAsync` itself, then `computeVertexNormals` on what it got. Admission groups the subscribers of one URL so that they count as one of four active request slots (ADR-078); each subscriber's own `loadAsync` joins the request already in flight because three.js 0.156.1's `FileLoader` keeps one module-level table of in-flight URLs and hands every caller the same response (`FileLoader.js`, the `loading[url]` table). The parse is per subscriber: the Enigma page holds 2,868 geometries for 993 files (evidence `enigma-page-memory-2026-11-22.md`).

Measured for this proposal, with three.js's own `STLLoader` and `FileLoader` over a stubbed network in the widget suite (scratch tests, not kept; Decision 11's tests reproduce them), on the base source:

- Three parts naming one file: one request, three parses, three geometries.
- Two `artifactChanged()` calls for one path, the file rewritten between them while the first request was held: one request in all; the part ends showing the first call's bytes.
- A new tree for the same document (the path `reload()` takes) built while an artifact update's request for its file was held, the file rewritten before the tree was built: the new tree showed the earlier bytes. A `reconcile` adding a part naming that file did the same.

And in the suite's Chromium (Playwright 1.63, SwiftShader), with the bundle built from the base (`67c7794777ea6d40b888a638781ce4df1077c4141b20da14daec1cf6e8843e28`), a document of four parts, three naming one file: 8 WebGL buffers created at mount, 6 more created and 6 deleted by `artifactChanged()` of the shared path, all 14 deleted at `dispose()`; the two-notice case above left the part's on-screen rectangle at the earlier file's size (width 53.4 px where a fresh mount of the final file gives 76.3).

A prototype of the proposer's design, reverted, gave in the same runs one parse and one geometry; 4 buffers at mount, 2 created and 2 deleted by the update, all 6 deleted at disposal; the final file's size in the two-notice case (by the stricter rule the review struck, "Corrected in review"); and equal pixels against the same document with every part naming its own copy of the bytes, plain and under a ghosting highlight. With it, the twelve widget test files that mock the STL loader (`geometry-admission`, `parent-adversarial-geometry`, `tree`, `shared-materials`, `draw-on-change`, `picture-revision`, `assembly`, `color`, `flat-pass`, `flat-pass-parity`, `navtree`, `follow-the-slider`) passed unmodified except four tests of `src/geometry-admission.test.ts` (Decision 11); the typecheck passed. The prototype is evidence that the design can be built; the applier writes the implementation from this design.

## Goals / Non-Goals

**Goals:** the parts and markings of one viewer that name one model file, asking while one reading of it is open, are drawn from one geometry, uploaded once. No part shows a freed geometry; no part is given older bytes than the base gives it. The picture, the order of drawing and everything a maker or a host can see or rely on are as they are: a mount, a reload, a republish applied in place, a changed file during `machinome develop`, a failed load that leaves the last good model, a disposal that leaves nothing behind.

**Non-goals:** dropping the `normal` attribute; dropping the tab's copy after the upload; instancing or merging draw calls; a flexible part's geometry (it is built from its shape and rewritten at every evaluation, so it is never the same as another part's and is not a file); anything that changes how many triangles a part has; keeping fetched bytes; sharing between copies of the bundle; any option or handle method; molejo; any project's source. Giving an update a request of its own when one for its file is already in flight: the base folds the two, this change gives the same bytes, and the staleness that follows is a finding of its own (Decisions 1 and 2).

## Decisions

### 1. When two parts share (attack point 1)

**The rule.** A part's load joins the open reading of its URL and receives that reading's geometry for its viewer; a load that finds no open reading of its URL opens one. A reading is open from the load that opens it until the first of: its request settles (success or failure); every queued subscriber of a not-yet-sent reading is cancelled (as today). It reads exactly three things: the URL string (`baseUrl + model`, as today's group key), whether a reading of it is open, and the viewer the part belongs to. It reads no `mtime`: whether a part asks at all is decided, as today, by the model path and `mtime` rule of "Geometry is refetched only when its identity changes", which does not change. This is ADR-078's join eligibility with one difference: a group closed at its first subscriber's settlement, some microtasks after the response; a reading closes when its request settles.

**The pieces.** A *reading* is one admission group (one URL, one slot of the four, FIFO as today) that sends one request through `STLLoader.loadAsync` and computes normals once. A viewer is identified by its `MaterialPresentation`, which `loadMesh` already receives and which is one per viewer (`viewer.ts` 621; a `WidgetTree` built without one makes its own). Within a reading, each viewer has its own *holding*: the first viewer to take the reading gets the parsed geometry, each further viewer a copy (`BufferGeometry.clone`, which copies every array).

**Every path that gives a part a geometry:**

| Path | Where it asks | What the rule gives it |
|---|---|---|
| A fresh mount | `replaceTree` → `new WidgetTree` (`viewer.ts` 2071); the constructor is synchronous and every `loadMesh`/`loadDecal` reaches `admitGeometry` before its first `await` | Every part of the mount asks before any load can settle, so every part naming one file joins one reading: the first four readings are sent during the construction and the rest are queued. True for any document by construction; not observed on the Enigma's document, which this proposal did not open |
| `reload()` | Builds a whole new tree with a new batch while the old one is on screen (`viewer.ts` 2060-2121) | Never a geometry of a settled reading: the old tree's readings closed when their requests settled, so the reload reads each of those files again. A reading still queued or in flight when the reload asks is joined, as the base's loads are folded into its request |
| `reconcile`, a part whose model or `mtime` moved | `prepareReconcile` (`tree.ts` 404): a node's own load is awaited before its markings and children are visited | Joins a reading that is queued or in flight, whichever operation opened it; a node visited after that reading settled opens another (a second copy, development only) |
| `reconcile`, a part new in the republish | `new WidgetTree(childData, …, batch, …)` with the republish's batch | As above. A file already on screen is read again for it: no part joins a geometry on screen |
| `artifactChanged(path)` | One batch; every replacement and decal for the path asks synchronously (`tree.ts` 348-356) | One reading for the whole batch; if a request for the path is already in flight the batch joins it, as the base folds it |
| A marking | `loadDecal` → `loadMesh` with the marking's own URL | Joins like a part (a part and a marking naming one file share the reading); `liftDecal` lifts from a copy and the decal's own geometry is the lifted one; the marking lets go of the file's geometry at once |
| Two viewers in one page | The queue and its groups are module-level, shared by every viewer of this bundle | A second viewer's parts join a reading of the first's while it is queued or in flight; the second viewer gets a copy, never the first's geometry |

**Why per viewer.** three.js keeps, per renderer, one GL buffer per attribute and one `dispose` listener per geometry it drew (`WebGLGeometries.js` `get`), and frees them only when that geometry's `dispose` event fires; `WebGLRenderer.dispose()` (`WebGLRenderer.js` 655-685) frees neither, and the viewer does not force a context loss. One geometry held by two viewers would keep a disposed viewer's buffers, and through the listener its context, alive until the other viewer lets go; and disposing it from one viewer would fire the event in every renderer that drew it, deleting the other viewer's buffers under it (three.js would upload them again at that viewer's next draw). A copy per viewer costs exactly today's memory for a second viewer of the same files, and the materials are per viewer already (`share-one-material-per-appearance`, "One holder for the page" rejected).

**Why the rule and not a stricter or a wider one.**

- *A stricter rule, the proposer's:* a load never joins a reading whose request was sent before its operation (its `GeometryBatch`) began; it opens a reading of its own, whose request waits for the earlier one to settle so that `FileLoader` cannot fold the two. It closes a staleness the base has (Context: measured in both suites): a later operation asking for a file whose request is in flight is given that request's bytes. That is a correction of the base's freshness and not part of sharing: under the rule above a part receives the bytes the base gives it (Decision 2). The stricter rule costs a tick on every operation, readings that hold a slot while they wait, and extra requests whenever operations overlap, a second viewer mounting beside the first included; and no project has reported the staleness. Struck in review ("Corrected in review") and recorded as a finding in `workflow/warts.md` for the pilot to order or not.
- *The wider rule* (the pilot's point 2 as told: joinable until the viewer is told the file changed, by an artifact notice or a moved `mtime`) shares in one more case: a republish that adds a part naming a file already on screen. It needs a table of readings that outlives their requests, which is the cache ADR-078 set aside; it is only as fresh as the signals that reach it, and two do not (a reload, which exists to read what is there now and is told nothing; and a pending reload tree, which `artifactChanged` does not reach, "Found while proposing"); and it must key on `mtime`, which is per part in the document, not per file. Its gain is a second copy in development sessions, where memory is not the problem.

Costs of the chosen rule: a republish adding a part naming a file on screen holds a second copy until the next mount or reload; a republish whose parts naming one file ask at different depths may hold more than one.

### 2. Freshness (attack point 2)

"Geometry is current only while its model path and `mtime` both match" decides whether a part asks; this rule decides which bytes it gets, and it gives **the bytes the base gives.** A load that asks while a request for its URL is in flight receives that request's result: on the base as a parse of its own of the response `FileLoader` folded it into, here as its viewer's holding of the one parse.

| Case | Base | This design |
|---|---|---|
| Two notices for one path, the second while the first's reading is still queued | Both batches' loads wait in one group and start together; one request, sent after both | The same: one reading, joined by both, sent after both |
| The same, the second while the first's request is in flight | The second batch joins the active group; its `loadAsync` is folded into the first request; the part ends on the first request's bytes (measured) | The second batch joins the reading: the same bytes, one geometry, held by the first batch's parts and then by the second's |
| A notice during a reconcile | The notice's batch is folded into any request for the path in flight | It joins that reading: the same bytes |
| A reconcile adding a part naming a path while a batch for the path is in flight | Folded: the new part gets the batch's bytes (measured) | Joins: the same bytes; the new part and the batch's parts hold one geometry |
| A reload during any of these | The new tree's loads are folded into requests in flight (measured) | They join those readings: the same bytes. Every file whose reading has settled is read again |
| A reconcile's later load for a file its own earlier load is still reading | Folded: one request, two parses | Joins: one request, one parse, the same bytes |
| A load asking in the microtasks between a response and the close of its reading | Its own `loadAsync` finds `FileLoader`'s entry gone and fetches again | It joins the arrived reading. The only case where the base reads fresher bytes: a reading closes in the first reaction to its request's settlement, so the interval is the microtasks between `FileLoader`'s response and that reaction, in which no time passes |

In every other case a part is given the bytes the base gives it. The folding itself, and the stale part it can leave, are a finding recorded while proposing (`workflow/warts.md`, "An update that asks for a file still being fetched is given the earlier request's bytes"), which this change neither closes nor widens. In `machinome develop` the development page calls `manifestChanged()` on its reload message and never `artifactChanged()` (`develop.ts` 112-117): a changed file reaches the viewer as a republish whose parts naming the file have moved `mtime`s, and they read it in that republish's readings. The development server answers with `Cache-Control: no-store` (`server.py` 158) and the suite's server likewise (`tests/support.py` 245), so a second request reaches the file.

### 3. Ownership (attack point 3)

**The structure.** A reading holds, per viewer, a *holding*: its geometry and a count of holders. A load that is admitted gets a *share* of its viewer's holding; the share's `release()` decrements the count once and does nothing the second time. A holding's geometry is disposed exactly once: when its count is zero and its reading has *retired* (every subscriber that joined it has settled), checked at both events. A parse that no subscriber took (every one cancelled) is disposed when the reading retires; it was never uploaded. A disposed holding is removed from its reading and drops its geometry; a share refers to its own holding only; a retired reading keeps no geometry. So nothing in the admission module keeps a freed geometry's arrays reachable. `tree.ts` keeps each mesh's share in a `WeakMap` beside `meshOwnership`.

**Every place a geometry is disposed today:**

| Site | Today | After |
|---|---|---|
| `disposeMesh` (`tree.ts` 171), idempotent by its `WeakSet` | `mesh.geometry.dispose()`, then the material released | A mesh holding a share releases it (and forgets it) instead; any other geometry (the placeholder, a decal's own, a flexible part's) is disposed as today. Still idempotent: the `WeakSet` stops a second call, and the share's own flag would stop a second release |
| `loadMesh`'s failure path (`tree.ts` 923-930) | Disposes a returned geometry not yet on the mesh, then `disposeMesh`, then `forget` | Releases a share not yet recorded on the mesh, then `disposeMesh` (which disposes the placeholder), then `forget` |
| The admission's abandon callback (`tree.ts` 917) and `startLoad`'s own check (`tree.ts` 915) | Dispose a geometry that arrives for a cancelled owner | Gone with the per-subscriber parse: a subscriber whose owner is cancelled when the reading arrives is never given a share; what no one took is disposed at retirement |
| The placeholder (`tree.ts` 907, 921) | Disposed when the loaded geometry takes its place, or by `disposeMesh` if the load never lands | Unchanged |
| `loadDecal` (`tree.ts` 963-975) | Lifts, then disposes the loaded geometry | Lifts, sets the decal's own geometry on the mesh, forgets the share and releases it. If the mesh was already disposed between `loadMesh`'s return and this continuation (its owner cancelled), it makes nothing and rejects with the cancellation; the base lifts a decal for a disposed mesh there, never uploaded |
| A failed preparation (`GeometryBatch.cancel`, from `reconcile`'s and `artifactChanged`'s `catch` and a failing subtree's `loaded`) | Its owners' cleanups dispose the meshes they reserved; `batch.own` disposes created subtrees and flexible shapes | The same calls; the prepared meshes release their shares. The live tree's meshes hold shares of their own, of readings that closed before they were attached, and are not touched: the last good model stands |
| A cancelled owner (`GeometryOwner.cancel`) | Rejects its queued jobs; its cleanups `disposeMesh` every mesh it made | Unchanged; its active subscribers settle with the cancellation when their reading arrives, with no share |
| A late result after a disposal | Disposed by the abandon path, once (the tests at `geometry-admission.test.ts` 90-112 and `parent-adversarial-geometry.test.ts`) | Not handed out; disposed at retirement unless another holder of the same viewer took it, in which case it stays theirs |
| `dispose()` with loads in flight (`viewer.ts` 2515-2530; `WidgetTree.dispose`) | Owners and preparations cancelled, then every mesh's `disposeMesh` | Unchanged calls; readings in flight that no live part takes are disposed on arrival |
| `FlexibleShape.dispose` and `disposeMesh` on a flexible mesh | Dispose the flexible part's own geometry | Unchanged: a flexible mesh holds no share |

**The invariants and why they hold.** The count equals the unreleased shares of the holding, so it is never negative. A mesh in a scene holds an unreleased share: shares are released only by `disposeMesh` (called when a mesh leaves its group, when its tree is disposed, or when the owner that reserved it is cancelled, which for an attached mesh is only its tree's disposal), by `loadMesh`'s failure path before attachment, and by `loadDecal` after the decal's own geometry has replaced the file's on the mesh. A geometry is disposed only at zero holders after retirement, so no mesh that shows it remains. Every subscriber that joins a reading joins before it closes, and closing happens in the first reaction to its request's settlement, before any subscriber's reaction; so every share is taken before any holder can release one, and the retirement condition is a defence the generated proof watches rather than an ordering the tests can provoke (MU10).

### 4. Writers (attack point 4)

| Writer | What it writes | With sharing |
|---|---|---|
| `computeVertexNormals` (`tree.ts` 919, every subscriber today) | The `normal` attribute, from positions | Moved into the reading: once per parse, before any part has the geometry. It recomputes from positions, so the values are the ones every subscriber computed |
| Bounding box and sphere: three.js's frustum culling and render-list depth (`WebGLRenderer.js` 1244), `Mesh.raycast`, `screen.ts` `worldBounds` (77-89), `viewer.ts` `visibleBounds` (3289-3306) | `boundingBox`/`boundingSphere`, each only when null, from positions | The same value for every holder, computed once |
| `liftDecal` (`tree.ts` 949) | Clones the geometry (`BufferAttribute.copy` makes new arrays, three.js `BufferAttribute.js` 56), deletes the clone's `normal`, welds the clone into a new geometry (`mergeVertices`), computes that one's normals and lifts it | Reads the source only |
| `liftAlongNormals` (`tree.ts` 103) | The positions of the geometry it is given, and nulls its bounds | Called only on `liftDecal`'s welded result (and on the tests' own geometries) |
| Highlight, hover, colour (`presentation.ts`) | Materials only; meshes pointed at materials | None. `presentation.ts` never reads a geometry beyond constructing the mesh |
| Part controls (`partControls.ts`) | No geometry | None. Its line 659 is the pick's visibility filter, which reads `visible` |
| Picking (`Raycaster.intersectObject` → `Mesh.raycast`) | The bounding sphere when null | As above |
| The renderer's upload (`WebGLAttributes`) | Reads arrays; records the attribute's version | One upload per attribute per context |
| `FlexibleShape` | Its own geometry, at every evaluation | Out of scope; never shared |

A later writer is caught by S12, which checks every shared geometry's attribute versions and array contents after a battery of every operation that reads a geometry, and by the ADR's rule (Decision record): nothing writes a rigid part's geometry after it is handed out but three.js's bounds caches.

### 5. The picture and the order of drawing (attack point 5)

The mesh and its place in the order of drawing are still reserved in `loadMesh` before admission, in the order the loads are called, which this change does not touch. The opaque list is sorted by `drawOrderSort` (`presentation.ts`; installed at `viewer.ts` 425): group order, render order, place, depth, object id. The transparent list by three.js's `reversePainterSortStable`: group order, render order, depth, object id. Neither reads a geometry. Depth is the geometry's bounding sphere centre in the object's world matrix (`WebGLRenderer.js` 1244); the sphere is computed from the same positions for every holder, so every depth is the base's.

What in three.js keys on a geometry's identity, and what sharing does to it:

- `WebGLAttributes`: one GL buffer per `BufferAttribute`. One upload a file in each viewer: the saving.
- `WebGLGeometries`: one `dispose` listener and one count in `info.memory.geometries` per geometry; fewer of each.
- `WebGLBindingStates`: one vertex array object per geometry, program and wireframe flag (`bindingStates[geometry.id][program.id]`), and a bind skipped when consecutive draws use the same pair. Fewer objects, perhaps fewer binds; nothing a draw computes.
- `WebGLObjects.update`: a geometry's attributes are checked once a frame however many meshes use it.
- Program parameters read the material and the geometry's attribute set, which is the same for every geometry of one file.

What could make a picture differ, and why none does: a write to a shared geometry (Decision 4; S12); normals computed otherwise (they are computed by the same call on the same positions); a mesh drawn with a disposed geometry (three.js would upload it again, with the same picture: the detector of G1 and G2 catches the state, B1 the buffers); a change in the order of reservation (none); a second viewer's copy differing (`clone` copies every array exactly; it does not copy `STLLoader`'s `hasColors` and `alpha` properties, which nothing in the viewer reads); vertex colours of a coloured binary STL (the `color` attribute is copied, and no material enables vertex colours). B2 compares decoded pixels of a document whose parts share files with the same document in which each part names its own copy of the same bytes, in several states; the prototype gave equal pixels plain and under a ghosting highlight.

### 6. Loading and failure (attack point 6)

- **Budget and order:** one reading is one group and one slot of the four, in FIFO order, as today.
- **The slot is held until every subscriber settles**, as today. All of a reading's subscribers wait on one request and settle in one round.
- **Queued work cancelled** is rejected without a request, and a reading left with no queued subscriber is closed at once, so a later load gets a new FIFO position (ADR-078; the test at `geometry-admission.test.ts` 51).
- **What a subscriber is promised:** a share of its viewer's holding of the reading's geometry, which it must release exactly once and must not write; or the reading's error; or its cancellation. A subscriber whose owner is cancelled when the reading arrives gets its cancellation if the reading succeeded and the reading's error if it failed, as today. One of several cancelled: it takes no share and the others are unaffected. All cancelled: the parse is made, taken by no one and disposed at retirement. A copy that throws rejects that subscriber with its error. A reading's failure (`FileLoader`'s `HttpError`, an exception in `computeVertexNormals`) rejects every subscriber with that error, where the base gave each subscriber the outcome of its own parse of the same bytes; with one response the outcomes were the same but for the error object.
- **Readiness** still waits for every required asset (`tree.loaded`, unchanged), and a failed asset still rejects the mount or the update, leaving the last good model.

### 7. Load time and peak memory (attack point 7)

Not measured in the opening evidence, and not measured here. What the design changes, each an expectation for the reviewer to measure: on the Enigma's mount, 993 parses and normal computations of 7.8 million triangles where there were 2,868 of 16.2 million; 573.5 MiB fewer bytes handed to WebGL; one copy of each file's arrays alive in the tab while the page loads, where the base made one per part as each part's parse ran; the same 993 requests, since the base fetched each file once already. A slot is released when a file's one parse is done, where the base held it through every subscriber's parse in `FileLoader`'s callback loop, so admission may turn over sooner. Nothing here predicts a time or a peak.

### 8. What must not change (attack point 8)

Each verified against the source:

- Viewer API 30 and document versions 1 to 14: `package.json` 4-5, not touched.
- The mount handle: `viewer.ts` is not touched; `reload`, `artifactChanged`, `manifestChanged`, `dispose` call the tree as they do.
- `on-demand` mode and capture: the draw path, `drawPicture` and the picture revision are not touched; no write this change adds is read by a draw (replacing a mesh releases its share inside the reconcile's or artifact batch's application, after the revision is raised, `tree.ts` 360 and 396; disposing a geometry no mesh in a scene shows changes no draw).
- Flexible parts: `flexible.ts` is not touched; a flexible mesh holds no share.
- Markings as drawn: the decal's geometry is the welded, lifted copy, as today; ADR-056's group is not touched.
- Materials and highlights: `presentation.ts` is not touched; meshes are reserved where they were.
- Picking and part controls: they read geometry (Decision 4) and are not touched.
- A changed file during `machinome develop`: Decision 2, last paragraph.

### 9. The requirement's words (attack point 9)

Read in the baseline `viewer-package` spec: "A host mounts the viewer and receives a handle", "A host updates only what changed" ("`artifactChanged(path)` SHALL refetch the model file", which the base does not do in the overlap it folds; unchanged here, and a finding), "Geometry is refetched only when its identity changes" (whether a part asks; unchanged), "A failed update leaves the model standing", "Expression cache pressure does not change a machine" (geometry requested; unchanged), "The viewer draws the markings a part carries", "Fresh mounts draw loaded rigid assets independently of fetch completion order", and "A continuous viewer draws a frame only when its picture has changed".

Only the last but one promises independence: its scenario "Repeated paths retain separate part ownership" says "each part still owns separate geometry", and its failure and disposal sentences say a returned geometry is disposed. The delta restates that requirement whole, with all eleven scenarios, changing those five places and nothing else. "Separate part ownership" stays true as the scenario now states it: each part owns its share. The new requirement states the observable behaviour this change adds: one geometry, held and uploaded once; when a reading may be joined; the release; two viewers never sharing.

### 10. What this replaces, and everything the replaced thing did

- **A subscriber's own `startLoad`** (`tree.ts` 913-917): called `loadAsync` (joining `FileLoader`'s in-flight request), disposed and threw if its owner had been cancelled meanwhile, and through the abandon callback disposed a value arriving for a cancelled owner; its settlement held the slot. Replaced by the reading's one `loadAsync`, the per-subscriber check at arrival, and disposal at retirement (Decision 3). The slot is still held until every subscriber settles.
- **`computeVertexNormals` in `loadMesh`** (`tree.ts` 919): prepared the normals and, if it threw, made that load fail, disposing its geometry and its reserved mesh. Replaced by the same call in the reading: if it throws, the reading disposes its parse and every subscriber fails with that error, and each disposes its reserved mesh as today (the test at `tree.test.ts` 215 holds this unmodified on the prototype).
- **`geometry.dispose()` in `disposeMesh`, the failure path and `loadDecal`**: Decision 3's table.
- **`admitGeometry`'s signature**: the start and abandon callbacks per subscriber become a viewer and the reading's read; the module gains the census (Decision 11).

### 11. Tests (attack points 9 and 10, and the planned proof)

Two widget files, run with three.js's real `STLLoader` and `FileLoader`: no mocked loader, so every parse is a real parse producing a new geometry. The network is a stubbed `fetch` that records each request with the file's version when it is sent and answers only when the test releases it, with a binary STL whose size encodes the version, through an object whose `body` is undefined (`FileLoader` then reads `arrayBuffer()` directly; the stream path is the browser tests'). URLs are absolute (Node's `Request` refuses a relative one) and distinct in every test: a request left unanswered keeps its reading open, and every later load of its URL would join it and wait. Disposal is recorded by wrapping `BufferGeometry.prototype.dispose`; parses by spying `STLLoader.prototype.parse`; normals by spying `computeVertexNormals`. The admission module exports a census for the tests: the holdings alive, with URL, viewer and holder count.

**`src/share-one-geometry.test.ts`, the real tree (node environment).** Red on the base for the reason given.

- **S1** A mount of fifteen parts over seven files, past the budget, three of them on one file and the first file's second part built after its reading was sent: one request, one parse, one normals call and one geometry per file; each shared geometry's `normal` attribute written once (its version 1). Base: a parse and a geometry per part.
- **S2** Of three parts on one geometry, a republish removes one, then moves the `mtime` of another (it takes a new reading), the tree's cleanup runs twice (`dispose()` twice, and the owners' cleanups after the traversal): after each step the remaining parts show an undisposed geometry and the census counts them; the shared geometry is disposed once, when the last is gone. Base: the parts' geometries are distinct.
- **S3** A part and its marking on one file, and two markings on one file: one request and one parse each; the decals lifted and their own; the part's geometry undisposed after the lifts. Base: two parses.
- **S4** Two `artifactChanged()` for one path while the first request is held: one request and one parse in all; the second batch's parts join the first's reading; after both are applied the parts naming the path show one undisposed geometry, held by exactly them, the first batch's replaced meshes having let go. With the file rewritten between the two calls, the parts end on the first request's bytes, as on the base: asserted, so that a change to the base's freshness has to change this test. Base: a parse per part of each batch.
- **S5** A reconcile adding a part naming a path while an artifact update's request for it is held: one request and one parse; the new part and the update's parts show one geometry, which stays undisposed when either is removed. Base: a parse per part.
- **S6** A new tree for the document built while a request for one of its files is held (the path `reload()` takes): the new tree joins that reading and reads every other file again, none of those geometries being the old tree's; when the old tree is disposed the new tree's meshes show undisposed geometries and the census counts exactly them. Base: a parse per part.
- **S7** One operation's later load joins its own reading in flight: a republish in which one part's `mtime` moves and a part new under an unchanged sibling (asked a few microtasks later) names the same file: one request, one geometry. Base: one request, two parses.
- **S8** Two trees of two viewers (two holders) in one batch, both naming one file twice: one request, one parse, one copy; shared within each viewer, distinct across them; disposing one disposes its holding only; disposing the other leaves nothing alive. Base: four parses.
- **S9** A tree disposed while the request every part was waiting on is held: when it is answered, one parse, disposed once, never attached, census empty. Base: a parse per part.
- **S10** Two trees of one viewer built in one batch, so that they share a reading; the first disposed 0 to 6 microtasks after the response: the second tree's meshes show an undisposed geometry and the census counts exactly them. Base: distinct geometries.
- **S11** A shared file answered with HTTP 500, at a mount and in a republish: every subscriber rejects with the loader's error, the reserved meshes are discarded, nothing of the failed reading is alive, and the republish leaves the last good model with its geometry held. Passes on the base (no sharing to break); a guard.
- **S12** No writer: after a mount, a battery (a highlight of each mode and a hover through the holder, a colour change by republish, a part hidden and shown and a focus, `worldBounds`, `visibleBounds` through a camera fit, a raycast through the scene, a decal lifted from a shared file, an artifact update of another file, a republish moving operations): every shared geometry's attribute versions and array contents are those it had after the mount. Passes on the base; a guard.
- **S13** After every tree is disposed and every request answered, the census is empty and every parsed or copied geometry has been disposed exactly once. On the base it fails because the census does not exist; S1 to S10 carry the red-first proof.

The file reads the census through the module's namespace (`import * as admission`), so that on the base a missing export fails only the assertions that read it, and S1 to S10 assert their stated reason before any census read. They build trees, never call `admitGeometry`, and use only constructor parameters the base has (a batch and a holder may be passed to `WidgetTree`), so each runs on the base far enough to fail where stated.

**`src/share-one-geometry-viewer.test.ts`, the real viewer in jsdom**, a copy of `src/draw-on-change.test.ts`'s bench (its counting renderer, kept loop and stubbed `ResizeObserver`) with its STL loader mock removed and its `fetch` stub answering both documents and model files, so that no existing file changes:

- **V1** `reload()` while nothing is in flight: the new tree's geometries are none of the old tree's; the old tree's meshes stay in the scene and their geometries undisposed until the new tree is installed; after it, the old geometries are disposed and the census counts only the new tree's holders. Base: geometries per part (red at the count).
- **V2** Two viewers of one document sharing files; one disposed: the other's meshes show undisposed geometries, the disposed viewer's holdings are gone; both disposed: nothing alive. Base: geometries per part.
- **V3** `manifestChanged()` adding a part naming a file on screen: the file is requested and parsed again and the parts on screen keep their geometry (pins the rejection of the wider rule). Passes on the base; a guard that turns red under MU11.
- **V4** `artifactChanged()` through the handle on a shared path: one request, one parse, every part naming the path replaced in one application, and the next frame drawn (the picture revision raised). Base: a parse per part.

**G1, generated, on trees** (in `src/share-one-geometry.test.ts`): 300 seeded sequences of 40 steps over documents of up to eight parts and markings on three files, with a seeded generator printing its seed on failure. Steps: mount a tree (one of two viewers' holders), reload (a new tree with the same holder, the old disposed once the new is loaded, as `replaceTree` does), a republish that adds, removes, moves the `mtime` of, or renames the file of a part or a marking, an artifact update, rewriting a file, answering a held request (in a random order, some with HTTP 500), disposing a tree mid-load or at rest. After every step, the work released so far run to quiescence, the detector:

- D1 every mesh under a live or pending tree's group holds a geometry not disposed (rigid parts, decals, the placeholder of a load still waiting);
- D2 the parsed and copied geometries not disposed are exactly those some such mesh holds, plus none (at quiescence no taken share is outside a mesh);
- D3 each holding's count equals the meshes that show its geometry;
- D4 every part shows the bytes of the reading that was open for its URL when it asked, or of the one it opened: no part is handed another file's or another reading's geometry;
- D5 after the last tree is disposed and every request answered, the census is empty and every parsed or copied geometry was disposed exactly once.

**G2, generated, on the viewer** (in `src/share-one-geometry-viewer.test.ts`): 40 seeded sequences of 25 steps on two mounts, with `reload()`, `manifestChanged()`, `artifactChanged()`, rewritten files, answered and failed requests and `dispose()`; the same detector over the meshes of each live viewer's scene.

What G1 and G2 would not see: anything in WebGL; pixels; a state that exists only between two microtasks inside a step (the detector runs at quiescence); a write to a shared geometry (S12's business); a freed geometry still reachable in the tab (the census is the module's own account); faults that need more steps, files or viewers than generated; a browser's network and cache.

**`tests/test_share_one_geometry.py`, a real browser** (Chromium with SwiftShader, as the suite's other browser tests; served by `QuietHandler`, which sends `no-store`). `createBuffer`, `deleteBuffer` and `bufferData` are wrapped per context by an init script.

- **B1** A document of four parts, three naming one file: 4 buffers created at mount; `artifactChanged()` of the shared path and a draw create 2 and delete 2; `dispose()` deletes every buffer created. Base: 8; 6 and 6 (measured above). The old buffers are deleted when the application disposes the old geometry and the new are created at the next draw, so the buffers of the two never coexist; the arrays in the tab do, while the update is prepared, once each.
- **B2** Pixels: that document and the same with each part naming its own copy of the same bytes, decoded and compared after mount, under each highlight mode, with a part hidden, and after an artifact update. Equal on the base too: a guard of the picture, not a red test.
- **B3** Two viewers of one document; one disposed: every buffer its context created is deleted, and the other's decoded pixels are unchanged. Passes on the base; a guard that turns red under MU2.

**Existing tests that change**, all in `src/geometry-admission.test.ts`, each because it asserts a parse per subscriber or calls the old signature:

- "cancels queued jobs without requests and retains active capacity until real settlement" and "removes cancelled queued URL eligibility so a later request cannot inherit abandoned FIFO priority": they call `admitGeometry` with a start per subscriber. Rewritten on the new signature with the same counts and the same order asserted.
- "releases failures, preserves their original error and closes duplicate groups after actual settlement": its second subscriber of one URL succeeded with a start of its own while the first's failed. With one request there is one outcome: its row becomes rejected with the original error. The original error preserved, and a later load after settlement being a fresh load (`fresh` 1), are asserted as they are.
- "does not commit prepared shared-path models or markings after disposal at microtask %i": a part and its marking on one path made two loads (`expect(pending).toHaveLength(2)`); they make one. Its assertions on attachment are kept.

No other assertion is weakened. ADR-078's counted test ("four started/peak four with all 18 completed") holds: its eighteen URLs are distinct.

**Mutations.** Each applied alone to the implementation, then reverted; each must turn the named tests red:

| | Mutation | Red |
|---|---|---|
| MU1 | A load per subscriber again (no sharing) | S1, S3, S7, S8, V4, B1 |
| MU2 | One holding per reading for every viewer | S8, V2, B3 |
| MU3 | Never join a reading whose request has been sent | S1 (the first four files' later parts), S4, S5, S6, S7 |
| MU4 | `release()` without its flag | S2 (cleanup twice) |
| MU5 | `disposeMesh` disposes a shared geometry | S2, S4, S10, G1 D1 |
| MU6 | `loadDecal` disposes the file's geometry (today's line) | S3 |
| MU7 | Normals computed by each subscriber | S1 (normals count, `normal` version) |
| MU8 | `loadMesh`'s failure path disposes the returned geometry | S10 |
| MU9 | An untaken parse kept at retirement | S9, S13 |
| MU10 | A holding disposed at zero holders before its reading retires | Expected equivalent: by the ordering in Decision 3 every share is taken before any is released. G1 D1 would see it if not |
| MU11 | A reading left open after its request settles (a cache) | V3 |
| MU12 | A disposed holding kept in its reading | Not seen by any test: the census counts holdings alive, and reachability is outside the suite. The reviewer's memory measurement on the page is the check |

Where two guards cover one case: S1 is held by the sharing (MU1) and by the join of a reading whose request has been sent (MU3), each by its own assertion: the parse count (MU1) and the first four files' later parts (MU3). S4 is held by the sharing across two operations (MU3) and by the count that keeps the geometry while the first batch's meshes let go (MU5).

The final gate: the whole widget suite, the typecheck, the bundle built, then the viewer's Python suite.

## What the Enigma should show (predictions)

Predictions, resting on the evidence's census of the page's document (993 files, 7,816,568 distinct triangles, 72 bytes a triangle as these geometries hold them) and on every part of a mount joining its file's reading, which holds by construction. Earlier predictions in this campaign that scaled one measured figure were wrong three times; these rest on a count, but the process totals include allocators no one has measured:

- No pixel differs from the base's in any state compared.
- The scene: 3,347 meshes as before, on 1,472 geometries where there were 3,347 (993 rigid, 426 flexible, 53 decals; fewer still if the markings' files repeat, which the evidence did not count). WebGL buffers alive about 2,997 where there were 6,747.
- Typed arrays in the tab and WebGL buffer bytes each about 573.5 MiB less (about 1,030 MiB of 1,603.4); one open copy near 3,070 MiB where it was 4,214, if nothing else moves.
- The same 993 requests for the rigid parts' files.
- The load: shorter, by fewer parses and smaller uploads. No figure.

## For the pilot

Every difference between this design and the five points the pilot was told:

1. "One reading per batch": a reading belongs to an admission group, not to a batch. Every part that asks while it is open shares it, whatever update the part belongs to; and the parts of one batch that ask after its reading settled get another.
2. "A changed file never joins an old geometry: joinable until the viewer is told its file changed, by the artifact notice and a moved `mtime`": a reading is joinable only until its request settles, never after, so no part ever joins a geometry already on screen, and a republish adding a part naming a file on screen holds a second copy. And one thing the pilot was told is not true of the viewer today and is not made true here: "Parts never see bytes older than what the viewer has been told about." An update that asks for a file while an earlier request for it is still in flight is given that request's result, today as a parse of its own (three.js folds the two requests into one) and here as the same geometry. The bytes are the same as today's; the staleness is recorded as a finding of its own.
3. "A count of users, not a cache": as told, and a geometry is freed only once no load is still waiting on its reading as well as no holder.
4. "The swap stays": as told.
5. "A cancelled load gives its share back; if every part waiting on a reading is abandoned, the geometry is dropped on arrival": as told; a load cancelled before its reading arrives is never given a share.

Beyond the five points: two viewers in one page never share a geometry (one request, one parse, a copy for each further viewer); a reading's failure fails every subscriber of it.

And: this revises ADR-078, a ratified decision.

## Alternatives rejected

- **The wider rule** (point 2 as told) and **the stricter rule** (an operation's own reading, the proposer's): Decision 1.
- **One geometry across viewers:** Decision 1, "Why per viewer".
- **A parse per viewer instead of a copy:** the same memory and the same picture; a copy needs no second response and no second parse.
- **Running the queue's pump after the current task, so a mount's loads all ask before anything is sent:** it shares the same, but moves when the first requests go out and the synchronous counts four existing tests make (`tree.test.ts` 108, 141; `geometry-admission.test.ts` 28, 140); joining a reading whose request has been sent gives the same sharing without it.
- **Sharing a lifted decal among markings naming one file:** 3.2 MiB on the page (evidence), and a decal is the viewer's own derived geometry; not this change.
- **A mount option:** none is needed; a correct design needs none.

## Risks / Trade-offs

- [A later writer] → S12 and the ADR's rule.
- [A freed geometry kept reachable in the tab] → Decision 3's structure; MU12 says no test sees it; the reviewer's measurement does.
- [The widget suite's tests share the admission module] → distinct URLs per test, answered or abandoned before the test ends.
- [jsdom cannot run the renderer] → B1 to B3 in Chromium; MU1 and MU2 each bite there.
- [Time] → None claimed beyond the reviewer's measurement.

## Decision record

A new ADR-082 under `workflow/adrs/EXPORT/`, amending ADR-078, written after the reviewer's measurement and only if it confirms the design, in the register of the ADRs beside it, with a dated pointer amendment in ADR-078 and its line in `workflow/adrs/README.md`. It must record:

- One reading per admission group: one request, one parse, normals computed once; the parts and markings of one viewer that join it hold its geometry by count; a further viewer gets a copy. This replaces ADR-078's "each subscriber owns its own STLLoader parse, mutable geometry and material" and "Admitted subscribers use the real STLLoader and existing normal/marking preparation" (the reading uses the real STLLoader and the normal preparation once; marking preparation is per marking as before), and its consequence "Parsed geometry and scene resources remain owner-local, while transient queue state is shared".
- When a reading may be joined: while its request has not settled. ADR-078's "Pending identical string URLs may join one queued or active group" and "A later genuine artifact request must read the current resource, not join a completed group" stand, with eligibility closing when the request settles where it closed at the first subscriber's settlement.
- Release: a share released exactly once; a geometry disposed exactly once, at no holder after its reading retires; an untaken parse disposed at retirement. This replaces "Late or abandoned returned geometry is disposed exactly once, including cancellation between promise continuations".
- What stands from ADR-078: the budget, FIFO, queued cancellation without requests, the slot held to settlement, the last good model, idempotent cleanup, and "There is no public host option, retry, permanent STL cache, geometry substitution or document/API version change": a reading never outlives its request.
- The rule for writers: nothing writes a rigid part's geometry after it is handed out but three.js's bounds caches.

## Found while proposing, out of scope

- On the base a load that asks for a URL whose request is in flight is folded into it by three.js's `FileLoader` and given its bytes, so an update that begins after a file changed can show the file as it was when the earlier request was sent (Context: measured in both suites, 53.4 px where a fresh mount gives 76.3). This change gives the same bytes. Recorded in `workflow/warts.md`, "An update that asks for a file still being fetched is given the earlier request's bytes".
- A pending reload tree is not told of artifact notices (`viewer.ts` 2558 reaches `tree` only), and a `manifestChanged()` during a reload reconciles the tree about to be replaced, so a reload overlapping a notice can install bytes and a document older than the notice. Unchanged by this change.
- In a republish a node's children are asked for only after its own replacement and markings have loaded (`tree.ts` 412-466), which is why the order of new parts can follow completion (the open wart "After an in-place update, the order new parts are drawn in can follow which fetch finished first") and why a child naming the file its parent reloads takes a second reading here.
- `loadDecal` on the base lifts a decal for a mesh disposed between `loadMesh`'s return and its continuation; the decal's geometry is made and never disposed (never uploaded). Decision 3 makes nothing there.

## Open Questions

None for the implementation. What is the pilot's is under "For the pilot".

## Corrected in review, before the planning commit

The reviewing agent changed one thing in these artifacts, and what follows from it; the proposer's text is otherwise as written.

- **No rule for freshness.** The proposal gave every operation a request of its own: a load never joined a reading whose request was sent before its operation began, and its reading waited for the earlier request so that `FileLoader` could not fold the two. It closed a staleness the proposer found and measured on the base, and it was built on the brief's own first requirement and on a sentence the pilot had been told ("Parts never see bytes older than what the viewer has been told about"), which the base does not satisfy. It is a correction of something else: the finding this change answers is the page's memory, sharing by the admission group gives every part the bytes the base gives it, and no project has reported the staleness. The stricter rule also changed what a page requests when two viewers mount together. So the rule is the admission group's, the tick, the displaced reading and its wait are struck with their tests (the freshness cases of S4 to S6 now assert the sharing and the count across two operations, B3 and three mutations are gone, D4 checks that no part is handed another reading's geometry), and the staleness is recorded as a finding for the pilot to order or not. The sentence the pilot was told is corrected to them with the result.
