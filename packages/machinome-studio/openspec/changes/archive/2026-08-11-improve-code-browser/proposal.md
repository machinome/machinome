## Why

The Code navigator currently presents every directory as permanently expanded and uses an undifferentiated cyan square for files, making even modest projects difficult to scan. PNG source files are listed but fail when opened because the editor supports only UTF-8 text, so the interface does not provide a useful view of an important Git-visible project asset.

## What Changes

- Present the project root as expanded while initially collapsing every directory beneath it.
- Let the maker expand and collapse individual directories without losing the current file selection.
- Replace colored source chips with a coherent monochrome icon family for folders, Markdown documents, PNG images, Python files, and generic files.
- Open Git-visible PNG files in a bounded read-only image preview while retaining Monaco editing for text files.
- Preserve source refresh and live reconciliation behavior as folders and files change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-source-editing`: Add navigable collapsed directories, type-specific monochrome file icons, and safe read-only PNG preview behavior to the Code workspace.

## Impact

- `floor/source_files.py` gains a bounded verified PNG-read operation without changing the editable-text contract.
- `floor/app.py` exposes PNG preview bytes from the existing session-scoped source boundary.
- `floor/frontend/src/main.tsx` and `styles.css` gain hierarchical disclosure state, unified SVG icons, and an image preview surface.
- Source service, API, and browser-facing tests cover the new behavior; the reference design and source-editing baseline are updated when the change is archived.
- No new runtime dependency is required.
