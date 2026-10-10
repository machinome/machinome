## MODIFIED Requirements

### Requirement: Independent typed bound productions

The bundled system SHALL expose Production from `machinome.production.profile`, Item from `.item`, typed processes from `.process` and values from their defining modules, with no root reexports or mandatory heavy dependency. Production SHALL bind a compatible supplied model without mutation or registration. Attribute names SHALL be arbitrary. Declaration errors SHALL fail at definition and wrong model types at binding. A file the supplied model names that does not exist SHALL be refused at binding with ProductionExportError naming the node and the path, never as a changed input. Production SHALL expose lazy bom, stock, steps, mass, findings and export directly, without evaluate or a second public plan.

#### Scenario: Two profiles share a model
- **WHEN** two productions bind the same parameterized model under different material/instruction choices
- **THEN** each has independent outputs while the model parameters, source, structure and simulation remain unaffected, and construction performs no geometry work

#### Scenario: A model names a file that does not exist
- **WHEN** a production binds a model one of whose repeated children names, among its files, a path that does not exist
- **THEN** construction raises ProductionExportError naming the production, the child's class and name and the path, and no ModelInputChangedError or ProductionInputChangedError is raised
