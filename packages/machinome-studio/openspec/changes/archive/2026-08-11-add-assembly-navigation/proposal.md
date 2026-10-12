## Why

The workspace's Model panel currently has no assembly data, even though the
published viewer already renders an authoritative nested model tree. Makers
need to inspect a complex assembly by its parts, isolate a subassembly, and
temporarily hide obstructing parts without changing the project model.

## What Changes

- Add an interactive Assembly navigator to the Model panel, populated from the
  viewer's published tree and using the corresponding inherited part colours.
- Let a maker select a node, focus it so its subtree becomes the viewer root,
  and hide or show that node's subtree in the current viewer session.
- Render each node's visibility control as a checkbox-like square: filled with
  the node's effective model colour while visible, or empty with only its
  border while hidden; use a neutral gray fill when the viewer has no single
  effective colour for that node.
- Keep focus and visibility independent: hiding a node does not change focus,
  and focusing a node does not restore hidden descendants.
- Reset assembly-navigation state when the viewer is replaced for a new model;
  it is not project configuration or a build artifact.
- Depend on the shared viewer's versioned assembly-navigation handle rather
  than reproducing tree traversal or Three.js mutations in Studio.

## Capabilities

### New Capabilities

- `assembly-navigation`: An accessible Studio assembly tree that controls the
  current viewer's focused root and visible model subtrees.

### Modified Capabilities

- `shop-browser-workspace`: The Model panel gains supported assembly controls
  backed by the currently displayed functional model.

## Impact

- `floor/frontend/src/main.tsx` and `styles.css` gain the Model-panel UI,
  accessible visibility checkboxes, keyboard interactions, and session-local
  selection state.
- `floor/frontend/src/solid-node-widget.d.ts` requires the new viewer API.
- Studio requires the paired `solid-node` viewer capability before enabling
  the controls; an incompatible viewer keeps the existing model usable and
  reports its unavailable assembly controls honestly.
