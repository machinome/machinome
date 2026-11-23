## MODIFIED Requirements

### Requirement: The app capability has an explicit reader capability

The viewer SHALL advertise viewer API 31 or a later one for reading a
document's app record, showing a model's app and notifying a page of a clocked
machine's changes, and SHALL keep reading document versions 1 to 14. The app
record SHALL be additive within those versions: it SHALL NOT change the
document versions read, and a viewer before this capability, which ignores
it, shows the automatic panel.

#### Scenario: A host requires the capability

- **WHEN** a host reads the mount handle's API version
- **THEN** it is 31 or later, and the document versions reported are 1 to 14
