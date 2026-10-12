# Assembly Navigation Specification

## Purpose

Let a maker inspect the model hierarchy and control the current viewer's focus
and subtree visibility without changing the CAD project or its build artifacts.
## Requirements
### Requirement: The Model panel presents the viewer's navigator
When the workspace has a mounted functional model, the Model panel SHALL
present the assembly navigator the installed browser viewer package mounts over
that viewer, under the panel's own heading, and SHALL NOT build, reproduce, or
substitute a tree of its own. The navigator's hierarchy, node labels, effective
colours, focused root, hidden subtrees, visibility controls, keyboard contract,
and restore-the-full-assembly affordance are the viewer's, specified by the
viewer package's own assembly-navigation capability; the shop SHALL NOT
reimplement, reword, or re-specify them. The panel SHALL give the navigator the
accessible name `Assembly` and SHALL present it in the workspace's own
typography and palette, as the reference design's Model panel states them,
using only the presentation surface the viewer package publishes for a host.
When no viewer is mounted, the panel SHALL say no model assembly is available
rather than show an empty tree.

#### Scenario: A maker inspects a mounted model
- **WHEN** the maker opens a workspace whose functional model is mounted
- **THEN** the Model panel shows the viewer's own assembly navigator for that
  model, named `Assembly`, with a row for each node of the viewer's published
  assembly

#### Scenario: The navigator wears the workspace's presentation
- **WHEN** the Model panel shows the viewer's navigator
- **THEN** its rows, indentation, colour chips, focused-root marking, and focus
  ring are the Model panel's own, matching the reference design, and the shop
  achieves that without depending on any part of the navigator the viewer
  package has not published for a host

#### Scenario: A maker restores the full assembly
- **WHEN** a subtree is the viewer's focused root
- **THEN** the panel offers the navigator's own affordance to restore the
  published document root, and the shop offers no second control of its own

#### Scenario: No functional model is mounted
- **WHEN** the workspace has no mounted viewer
- **THEN** the Model panel says no model assembly is available

#### Scenario: The mounted viewer goes away
- **WHEN** the workspace's mounted viewer is disposed, or the maker leaves the
  project
- **THEN** the panel disposes the navigator it mounted, leaves no second
  navigator behind, and stops observing that viewer

#### Scenario: The maker moves between workspace areas
- **WHEN** the maker selects Code and then returns to Model
- **THEN** the same navigator is still mounted over the same viewer, neither
  having been torn down and remounted

### Requirement: The Model panel reflects the viewer after an update
Assembly focus, subtree visibility, and expansion SHALL apply only to the
currently mounted viewer session and SHALL NOT alter the project source or
published build artifacts. The shop SHALL NOT hold its own copy of the focused
root or the hidden subtrees, and SHALL NOT reconcile them after a published
update: the panel SHALL show whatever the viewer's navigation state is at that
moment, whichever gesture or update moved it.

#### Scenario: A model update retains the focused part
- **WHEN** a published viewer update changes another part while retaining the
  focused node
- **THEN** the panel shows the updated assembly with that focus and the existing
  visibility state still applied, and the shop performs no reconciliation of its
  own

#### Scenario: A model update removes the focused part
- **WHEN** a published viewer update removes the focused node
- **THEN** the panel shows the viewer's resulting navigation state and remains
  inspectable, without the shop clearing or restoring any state it kept

#### Scenario: The maker's inspection does not reach the project
- **WHEN** the maker focuses a subtree and hides a part
- **THEN** the project's source and published build artifacts are unchanged

