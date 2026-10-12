## MODIFIED Requirements

### Requirement: Helpers depend on the framework

The distribution SHALL be named `machinome-mechanics` and expose the Python
package `machinome_mechanics` under Apache-2.0. It SHALL declare
`machinome>=0.7.0` as its runtime dependency and use `machinome.math` for its
nonlinear formulas. It SHALL NOT bundle a copy of the framework or replace its
expression evaluator. Because no mechanics version has been published, the
first release SHALL NOT expose a `solid_node_mechanics` compatibility package.

#### Scenario: Install a built distribution

- **WHEN** a wheel or source distribution is installed with Machinome 0.7 or
  newer available
- **THEN** every declared public helper is importable from
  `machinome_mechanics`
- **AND** they preserve numeric and symbolic computation

#### Scenario: Use a helper inside a motion law

- **WHEN** a project supplies a piston-height helper inside a Machinome motion
  law
- **THEN** the joint receives the numeric height at a bound crank angle
- **AND** symbolic driver evaluation preserves the deferred expression

#### Scenario: Ask the framework to install mechanics

- **WHEN** a user installs `machinome[mechanics]`
- **THEN** the `machinome-mechanics` distribution is selected without making
  the framework depend on or re-export its helpers at runtime
