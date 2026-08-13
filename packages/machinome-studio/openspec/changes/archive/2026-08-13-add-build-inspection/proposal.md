## Why

The framework now publishes stable printed-piece identity and the geometry facts needed to inspect a print job, but Studio still exposes Build as a static design prototype and leaves Sheets disabled. Makers need a truthful place to inspect each distinct piece, see how many copies to print, and download a deterministic handoff package without implying that Studio has sliced or automatically arranged the job.

## What Changes

- Replace the deferred Sheets rail item with an interactive Build area driven by the current published `viewer.json` piece inventory.
- Present one representative STL at a time on a fixed 250 × 210 × 220 mm virtual printer bed, with explicit quantity, dimensions, volume, watertightness, provenance, and simple axis-aligned bed-fit results.
- Keep the Build state synchronized with atomic model publications over the existing session stream, including honest empty and rebuild-failure states.
- Add a download endpoint that creates a deterministic ZIP containing one STL per distinct piece and a generated `README.md` telling the maker which files to print and how many.
- Exclude slicer estimates, support analysis, material calculations, orientation recommendations, and automatic multi-copy arrangement from this first version.

## Capabilities

### New Capabilities

- `build-inspection`: Inspect the framework-published distinct-piece inventory on a fixed virtual printer bed and download its deterministic print package.

### Modified Capabilities

- `shop-browser-workspace`: Replace the deferred Sheets affordance with the interactive Build area while preserving the workspace's live conversation and area state.

## Impact

- Browser UI and styles under `floor/frontend/src/`.
- A session-scoped package-download route and deterministic ZIP assembly in the Floor backend.
- Browser and backend tests for piece inventory updates, bed-fit presentation, safe artifact resolution, and package contents.
- The reference architecture and baseline workspace specification after the change is accepted.
