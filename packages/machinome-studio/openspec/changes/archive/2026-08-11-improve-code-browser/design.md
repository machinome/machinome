## Context

The source API currently enumerates the correct Git-visible working set and exposes only bounded UTF-8 text. The React navigator renders that flat entry list with indentation, a fixed expanded chevron for directories, and one cyan square for every file. Because PNG bytes are not text, selecting a PNG currently produces an editing error. ADR 0021 requires source access to remain verified, bounded, inert, and separate from model execution.

## Goals / Non-Goals

**Goals:**

- Make the hierarchy compact by default and directly navigable.
- Give common file types recognizable icons with one coherent neutral treatment.
- Preview PNG files safely without weakening the editable-text boundary.
- Keep live tree reconciliation, open text buffers, and editor state intact.

**Non-Goals:**

- Editing, transforming, downloading, or persisting image files.
- Persisting disclosure state across page loads or shop sessions.
- Adding previews for formats other than PNG.
- Adding create, rename, delete, Git, terminal, or language-server controls.

## Decisions

### Derive the visible tree from the existing flat inventory in the browser

The frontend will retain the API's stable flat path inventory and hold a set of expanded directory paths. A row is visible only when all of its ancestor directories are expanded. All directories begin collapsed whenever the session changes; the conceptual project root remains expanded because its top-level entries stay visible. Refresh reconciliation removes disclosure entries for directories that no longer exist while preserving state for directories that remain.

This avoids changing the source inventory API or introducing recursive client data structures whose identity would be rebuilt on every filesystem event. Rendering every entry permanently expanded was rejected because it is the behavior being corrected; server-owned disclosure state was rejected because it is ephemeral view state.

### Use small inline SVG components with `currentColor`

Folder, Markdown document, image, Python, and generic-file icons will share the same stroke width, dimensions, line caps, and neutral `currentColor` styling. Inline SVG keeps the icon family locally bundled, accessible, and consistent without a colorful icon package or new dependency. The folder disclosure uses a separate neutral chevron so its state is obvious without changing folder color.

### Add a dedicated verified PNG preview route

`SourceWorkspace` will add a PNG read operation that reuses the same Git visibility, path containment, regular-file, and symlink checks as text reads. It will enforce the existing byte limit and verify the eight-byte PNG signature. A dedicated route returns `image/png` with no-cache and nosniff headers. The existing source GET continues returning JSON text documents, so callers and ADR 0021's editing contract remain stable.

Using a browser `file:` URL or a broad static mount was rejected because either would escape the session-scoped verified boundary. Encoding images into the text JSON response was rejected because it conflates editable revisions with binary preview and inflates payloads.

### Model PNG tabs as read-only preview tabs

The frontend will classify a path by its case-insensitive extension before opening it. A PNG gets a tab and preview URL but no Monaco model, revision, dirty state, conflict state, or save action. Cache busting uses the latest source-event sequence so an externally replaced open PNG reloads. Text files retain the current buffer model unchanged.

## Risks / Trade-offs

- [A deeply nested tree is filtered on each render] → Project source inventories are local and bounded by Git-visible files; use a set lookup for ancestor checks and avoid additional network work.
- [Malformed or renamed images may fail in the browser] → Verify the PNG signature server-side, show the existing Code error surface on load failure, and retain a manual refresh.
- [A changed PNG may remain cached] → Return no-cache headers and add the source-event sequence to the preview URL.
- [Extension-based icon classification is imperfect] → Treat it as presentation only; the server independently validates bytes before serving a PNG.

## Migration Plan

No stored data migration is required. Ship the source service and frontend together, rebuild the bundled static assets, and roll back by reverting the change as one unit.

## Open Questions

None.
