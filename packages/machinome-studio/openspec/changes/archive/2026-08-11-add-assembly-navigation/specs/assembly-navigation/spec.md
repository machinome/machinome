## ADDED Requirements

### Requirement: The Model panel provides an interactive assembly navigator
When the workspace has a mounted functional model, the Model panel SHALL show
an accessible tree of every node in that viewer's current published assembly.
Each row SHALL show the node's label, hierarchy position, and effective viewer
colour when one exists. The tree SHALL identify the selected row, the focused
viewer root, and hidden subtrees separately. It SHALL provide labelled controls
to focus the selected subtree, restore the full assembly, and hide or show a
selected subtree. Each visibility control SHALL have checkbox semantics and
appear as a square filled with the node's effective viewer colour while checked
and visible, or empty with only its border while unchecked and hidden. A visible
node without a single effective colour SHALL use a neutral gray fill. The
checked state and accessible name SHALL communicate visibility independently of
colour.

#### Scenario: A maker inspects a coloured nested assembly
- **WHEN** the mounted functional model contains coloured nested assemblies
- **THEN** the Model panel shows the same hierarchy and each row's effective
  viewer colour, including colours inherited from an ancestor

#### Scenario: A maker focuses a subassembly
- **WHEN** the maker focuses an assembly-tree node
- **THEN** the viewer displays that node's subtree as its root and the tree
  marks that row as the focused root without changing any visibility state

#### Scenario: A maker returns to the whole assembly
- **WHEN** the maker selects Show full assembly
- **THEN** the viewer restores the published document root and leaves each
  current hidden or shown subtree in its current visibility state

#### Scenario: A maker hides and restores a part
- **WHEN** the maker hides an assembly-tree node and later shows it
- **THEN** the viewer hides and restores that node and all its descendants
  without changing the focused viewer root

#### Scenario: A maker reads visibility from the assembly tree
- **WHEN** one coloured node is visible and another is hidden
- **THEN** the visible node's checkbox square is filled with its effective
  model colour, the hidden node's square is empty with a border, and both
  expose their checked state to assistive technology

#### Scenario: A colourless node is visible
- **WHEN** a visible node has no single effective viewer colour
- **THEN** its checkbox square uses the neutral visible fill and remains
  distinguishable from the empty hidden state

#### Scenario: A maker uses the assembly keyboard controls
- **WHEN** keyboard focus is in the assembly tree
- **THEN** Up and Down move between visible rows, Right expands a collapsed
  parent, Left collapses an expanded parent or moves to its parent, Enter
  focuses the selected row, and Space toggles its visibility

### Requirement: Assembly navigation is session-local and reconciles on viewer updates
Assembly selection, focus, visibility, and expansion SHALL apply only to the
currently mounted viewer session and SHALL NOT alter the project source or
published build artifacts. When a viewer update retains a named node, its
compatible assembly-navigation state SHALL remain. When an update removes a
selected, focused, or hidden node, the workspace SHALL clear the unavailable
state and retain an inspectable viewer.

#### Scenario: A model update retains the focused part
- **WHEN** a published viewer update changes another part while retaining the
  focused node
- **THEN** the focus and existing visibility state remain applied after the
  update

#### Scenario: A model update removes the focused part
- **WHEN** a published viewer update removes the focused node
- **THEN** the workspace returns the viewer to the full assembly, clears the
  unavailable selection or hidden state, and remains usable
