## ADDED Requirements

### Requirement: The browser host contract uses Machinome names

The built viewer SHALL publish the browser global `MachinomeViewer`, the bundle
`machinome-viewer.js`, Machinome-prefixed auto-mount attributes, classes and CSS
custom properties, and the corresponding Machinome API-version declaration.
The API version SHALL increase because hosts must change their public names.
The package SHALL NOT publish solid-node-named browser aliases.

#### Scenario: A host mounts the current viewer

- **WHEN** a host loads `machinome-viewer.js` and calls
  `MachinomeViewer.mount(...)`
- **THEN** it receives the same functional viewer handle under the Machinome
  contract

#### Scenario: A host checks the API declaration

- **WHEN** it reads the bundle and package's declared viewer API version
- **THEN** both report the new version that contains the Machinome host names

### Requirement: The loader accepts current and legacy product formats

The viewer SHALL accept `format: "machinome-export"` as the current document
identity and `format: "solid-node-export"` as the legacy identity of committed
solid-node 0.6 and earlier artifacts. Format compatibility SHALL NOT change a
document's numerical schema version or the behavior associated with that
version. Any other format SHALL be refused by name.

#### Scenario: A Machinome document is mounted

- **WHEN** the document declares `format: "machinome-export"`
- **THEN** it loads according to its existing numerical version contract

#### Scenario: A committed 0.6 document is mounted

- **WHEN** the document declares `format: "solid-node-export"`
- **THEN** it remains renderable according to its numerical version contract

#### Scenario: An unrelated document is mounted

- **WHEN** its format is neither current nor legacy
- **THEN** mounting fails naming the unsupported format
