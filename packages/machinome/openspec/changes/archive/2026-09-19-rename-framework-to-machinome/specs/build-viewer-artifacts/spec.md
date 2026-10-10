## ADDED Requirements

### Requirement: New documents carry the Machinome format identity

Every `viewer.json` and `manifest.json` published by Machinome 0.7 SHALL carry
`format: "machinome-export"`. No other document behavior or version is changed
by the product rename. The coordinated viewer SHALL continue accepting
`format: "solid-node-export"` documents produced and committed by solid-node
0.6 and earlier.

#### Scenario: Machinome publishes a build

- **WHEN** Machinome 0.7 completes a build or export
- **THEN** its document declares `format: "machinome-export"`

#### Scenario: A maker retains a committed 0.6 export

- **WHEN** the renamed viewer opens its `solid-node-export` document
- **THEN** the format identity alone does not prevent the document rendering
