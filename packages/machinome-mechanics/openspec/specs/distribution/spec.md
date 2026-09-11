# Distribution Specification

## Purpose

Provide an independently installable library of helpers for solid-node projects.

## Requirements

### Requirement: Helpers depend on the framework

The distribution SHALL be named solid-node-mechanics and expose the Python
package solid_node_mechanics under Apache-2.0. It SHALL declare solid-node
as its runtime dependency and use solid_node.math for its nonlinear formulas.
It SHALL NOT bundle a copy of the framework or replace its expression evaluator.

#### Scenario: Install a built distribution

- **WHEN** a wheel or source distribution is installed with solid-node available
- **THEN** the twelve public helpers are importable from solid_node_mechanics
- **AND** they preserve numeric and symbolic computation

#### Scenario: Use a helper inside a motion law

- **WHEN** a project supplies a piston-height helper inside a solid-node motion law
- **THEN** the joint receives the numeric height at a bound crank angle
- **AND** symbolic driver evaluation preserves the deferred expression
