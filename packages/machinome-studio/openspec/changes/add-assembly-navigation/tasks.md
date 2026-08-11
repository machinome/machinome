## 1. Viewer integration contract

- [ ] 1.1 Update Studio's viewer declaration and preparation compatibility check for viewer API version 4.
- [ ] 1.2 Write focused browser coverage proving unsupported assembly controls are not presented as functional.

## 2. Model-panel assembly navigator

- [ ] 2.1 Write a red React/browser test for hierarchy, selection, focus actions, and accessible visibility squares in coloured, colourless, visible, and hidden states.
- [ ] 2.2 Implement the assembly-tree state, flattening, expansion, selection, focus, and visibility wiring through the viewer handle.
- [ ] 2.3 Implement accessible keyboard navigation, checkbox semantics, colour-filled/empty visibility squares, and visible focus treatments in the existing Model-panel visual language.
- [ ] 2.4 Reconcile local tree state after viewer artifact and manifest updates, including removed focused or hidden nodes.

## 3. Verification

- [ ] 3.1 Run focused frontend/browser tests, type checking or build, and inspect the rendered desktop and narrow workspace states.
- [ ] 3.2 Validate the Studio OpenSpec change and record the paired framework API/version dependency.
