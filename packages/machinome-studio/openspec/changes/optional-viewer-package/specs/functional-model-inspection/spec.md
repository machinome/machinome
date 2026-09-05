# functional-model-inspection

## MODIFIED Requirements

### Requirement: The shop floor requires a usable solid-node viewer to open
When opening a named project shop floor, the system SHALL obtain the browser
viewer from the installed solid-node through its CLI, which reports the viewer
package installed beside it. The viewer the floor requires SHALL be one that
updates a mounted model in place from a named artifact and from the published
document. When the installed solid-node reports no viewer — because the
`solid-node-viewer` package is not installed — or reports one the floor cannot
use, the system SHALL treat preparation as failed, report the reason and its
remedy, and SHALL NOT start Floor or its agents. The maker SHALL NOT be shown a
shop that is open with a model pane that cannot render.

#### Scenario: No viewer package is installed
- **WHEN** the maker opens the shop and the installed solid-node has no viewer package installed beside it
- **THEN** the shop does not open, and the maker is told that the viewer is unavailable together with the framework's remedy, installing the `viewer` extra

#### Scenario: The installed viewer is older than the floor requires
- **WHEN** the maker opens the shop and the installed viewer package does not meet the interface the floor depends on
- **THEN** the shop does not open, and the maker is told which viewer the floor requires and which one is installed

#### Scenario: The installed viewer cannot update in place
- **WHEN** the maker opens the shop and the installed viewer can only be mounted and replaced
- **THEN** the shop does not open rather than opening with a model pane that reloads the whole model on every change

#### Scenario: A usable viewer is installed
- **WHEN** the maker opens the shop and the installed solid-node reports a usable viewer
- **THEN** the shop opens and the browser renders the functional model with that viewer
