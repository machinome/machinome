## Context

Screen 1b's Assembly is currently a visual reference only. The Studio browser
already mounts the framework's reusable viewer and receives its published
`viewer.json` updates through the existing artifact stream, but it deliberately
does not read model-assembly data or own renderer mutations. The paired
framework cycle supplies the missing handle contract.

## Goals / Non-Goals

**Goals:**

- Make the Model panel a usable, accessible assembly tree with the viewer's
  real hierarchy and colour inheritance.
- Let selection, focus, and visibility be clearly distinct, reversible session
  interactions.
- Keep model updates, camera preservation, SSE, and project artifacts on their
  existing boundaries.

**Non-Goals:**

- Editing or persisting the CAD assembly, model source, or build document.
- Supporting assembly actions in Files, Agents, Sheets, or Code panels.
- Selection highlighting, measurements, multi-select, search, or drag-and-drop.
- Reimplementing document traversal or Three.js behaviour in Studio.

## Decisions

### Use the viewer handle as the assembly authority

Studio obtains a serializable tree snapshot and performs focus/visibility
actions only through the paired handle. This ensures the tree labels, paths,
and effective colours represent exactly what the canvas renders. Parsing
`viewer.json` in Studio was rejected because it would duplicate document and
inheritance logic and could drift from the shared viewer.

### Address nodes by stable name paths

Each row carries a root-relative array of sibling names. It is human-readable,
matches the published hierarchy, and avoids exposing artifact identity as a UI
identifier. A replacement model invalidates the local selection and controls
when its selected or focused path no longer exists.

### Separate selection, focus, and visibility

Clicking a row selects it for keyboard navigation and exposes its row actions.
Focus changes only the viewer's displayed root and includes a `Show full
assembly` action to return to the document root. Visibility applies to that
row's entire subtree; it does not alter selection or focus. The tree continues
to show hidden rows with an explicit state so a maker can restore them.

Each row's visibility control is a small square with checkbox semantics. Its
visible state is filled using the node's effective viewer colour; its hidden
state is transparent with only the border remaining. A node without one
effective colour uses a neutral gray visible fill. This preserves the reference
design's model-colour correspondence while making visibility legible without
depending on colour alone. The control exposes its node name and checked state
to assistive technology.

### Use standard tree keyboard behaviour and explicit labelled actions

The tree uses `role=tree`/`treeitem`, roving focus, Up/Down navigation,
Right-to-expand and Left-to-collapse-or-parent behaviour. Enter focuses the
selected node; Space toggles its visibility. Dedicated labelled buttons remain
available per selected row so neither action is discoverable only by keyboard.

## Risks / Trade-offs

- [A framework viewer older than the required API cannot perform real actions]
  → Reject it during the existing viewer compatibility preparation, naming the
  required and supplied API versions.
- [A rebuild removes a focused or hidden node] → The viewer clears that state;
  Studio reconciles its selected path to the new snapshot and returns focus to
  the full assembly when needed.
- [Deep trees can crowd the narrow panel] → Keep the panel's existing own
  scroll boundary, indent by depth, and defer virtualization until measured
  evidence identifies a need.
