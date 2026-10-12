## Context

The framework's additive `viewer.json` schema now publishes a `pieces` inventory. Each entry has a content-derived id, display name, sorted model and source references, instance count, axis-aligned size in millimetres, volume in cubic millimetres, and watertightness. Every referenced STL is already served through the verified project artifact boundary, and atomic replacement of `viewer.json` already reaches the browser over the session SSE stream.

The current Studio frontend keeps Model mounted while switching among Model, Code, and Agents, but its fourth rail item is a disabled Sheets placeholder. The Build prototype under `docs/design/build/` depicts unsupported slicer-derived facts and a generic model placeholder. This change implements the settled subset: inspection, one representative piece, an explicit required quantity, a fixed 250 × 210 × 220 mm bed, and a deterministic ZIP handoff.

## Goals / Non-Goals

**Goals:**

- Make every framework-published distinct piece inspectable without changing the framework document.
- Render the selected STL against a scale-accurate virtual build volume and bed with orbit, zoom, and reset controls.
- Make required print quantity visually prominent and distinguish geometric envelope fit from printability.
- Reconcile selection and inventory after each atomic `viewer.json` publication using the existing live connection.
- Download one canonical STL per distinct piece plus deterministic Markdown instructions.
- Preserve the verified artifact-root and session boundaries for every read.

**Non-Goals:**

- Slicing, G-code, automatic arrangement, multiple visual copies, supports, print-time or mass estimates, material choice, or orientation recommendations.
- Configurable printer profiles in this version.
- Inventing piece identity, geometry facts, or provenance when the framework has not published them.

## Decisions

### Render Build independently with Three.js

The Build viewport will use Three.js directly with `STLLoader` and `OrbitControls`. It will load the first sorted `models` reference for the selected piece through the existing artifact route, translate the mesh so its bounding-box centre lies over the bed centre and its minimum Z rests on the bed, and render a 250 × 210 mm gridded plane plus a 250 × 210 × 220 mm wireframe volume. Camera framing will include the full bed and selected piece, so their relative scale is truthful. The viewer will resize through `ResizeObserver`, render on control changes, and dispose controls, geometry, material, helpers, and renderer on replacement or unmount.

The existing framework widget remains the Model viewer. Reusing it was rejected because its public API mounts a whole document and auto-frames assembly geometry; it does not expose a single-piece scene or a scale-aware printer-bed extension. A CSS plate behind that canvas was rejected because it would imply a scale relationship that does not exist.

### Treat fit as an envelope check, not print advice

Studio will compare the published `[x, y, z]` size with the fixed `[250, 210, 220]` build volume, allowing permutations of the three axes. It will report either `fits 250 × 210 × 220 mm envelope` or `exceeds 250 × 210 × 220 mm envelope`. This answers whether the bounding box can fit under an orthogonal rotation; it does not select or display a recommended print orientation and does not claim the piece is printable. Watertightness remains an independent published fact.

### Read the inventory in the browser and refresh it on the existing stream

The browser will fetch the current `/projects/{project}/artifacts/viewer.json` when Build first becomes available and after reconnection or a `viewer.json` publication. It will validate only the shape it consumes and present an unavailable state for missing, malformed, or legacy documents. A new lifecycle connection and polling are both unnecessary. When an inventory changes, the browser retains the selected piece by stable id when it still exists, otherwise selecting the first published piece.

### Build the package on demand at a session-scoped endpoint

`GET /api/sessions/{session_id}/build-package` will read the current published document from that session's verified artifact root. For every piece, it will select the first lexically sorted model reference as the canonical STL, resolve it under the artifact root, reject escapes, missing files, duplicate piece ids, malformed entries, and two pieces mapping to the same output filename, then return an attachment ZIP.

Each STL filename will be `<sanitized-name>-<piece-id>.stl`, using a lowercase ASCII slug and the published content id to keep names deterministic and collision-resistant. Pieces are ordered by id in both the archive and instructions. `README.md` will contain a stable heading, the fixed build-volume context, and a Markdown table of filename and required quantity. It will state that each file represents one distinct piece and that the maker must print the listed number of copies. It will not contain timestamps, host paths, source paths, or slicer advice.

ZIP entries will use a fixed timestamp, permissions, compression method, and ordering. The response filename derives from the project name, while archive contents depend only on the current published inventory and referenced STL bytes.

Generating the ZIP in the browser was rejected because it duplicates verified-path handling, downloads every source artifact before creating the real download, and makes byte-level determinism browser-dependent. Publishing a persistent package into the project was rejected because inspection should not mutate the project or build publication.

### Keep the Build area mounted with workspace context

Build becomes the fourth interactive rail area and uses the existing left-panel/central-area shell. Its piece list and selection remain mounted while another area is active, just as Code buffers, Agents state, Model camera, and conversation do. The Build viewer itself may stop rendering while hidden but retains the selected piece and camera until its piece changes.

## Risks / Trade-offs

- **A published model reference names a non-STL or unsafe path** → validate the suffix, resolve beneath the exact artifact root, and return a non-downloadable error rather than substituting another file.
- **A large package consumes server memory** → build into a spooled temporary file and stream it; the route creates no persistent project artifact.
- **Three.js duplicates code already bundled inside the framework widget** → accept one direct dependency because the widget has no supported scene-extension API; keep it isolated in one Build viewer module.
- **Bounding-box fit can be mistaken for printability** → label it as envelope fit and keep watertightness separate; omit supports, orientation, slicer, and material claims.
- **An older framework publishes no pieces** → show a specific unavailable state while Model, Code, Agents, and conversation continue to work.

## Migration Plan

Land the change additively: the new endpoint is unused until the Build rail ships, and projects with older documents receive an honest Build empty state. Rollback removes the rail and endpoint without changing project data or framework publications.

## Open Questions

None. The pilot selected inspection-only behavior, one representative piece, explicit quantities, a deterministic ZIP with Markdown instructions, and the fixed 250 × 210 × 220 mm build volume.
