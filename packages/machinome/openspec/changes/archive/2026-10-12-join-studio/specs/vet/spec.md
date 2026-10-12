## ADDED Requirements

### Requirement: A model that reaches the studio is refused

The contract's denied modules SHALL include `machinome.studio`: a vetted file
that reaches, through an import statement or an attribute chain on a name an
import bound, `machinome.studio` or a name beneath it SHALL be reported
`framework-internal`, naming the denied name reached, as for the contract's
other denied modules. The studio's former package name `floor`, which no
package of the set installs, SHALL stay outside the universe.

#### Scenario: The studio is an internal to a model

- **WHEN** a project's model imports `from machinome.studio.app import
  create_app` and the project is vetted
- **THEN** the model's report holds `framework-internal` naming
  `machinome.studio`, and the model is not pure; and a model importing
  `floor.app` instead is reported `outside-universe` naming it
