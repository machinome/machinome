## MODIFIED Requirements

### Requirement: A framework internal is a finding

The system SHALL report `framework-internal` when a vetted file reaches,
through an import statement or through an attribute chain on a name that
an import bound, a dotted name equal to or beneath one of the contract's
denied modules: `machinome.cli`, `machinome.manager`,
`machinome.core.builder`, `machinome.core.processes`,
`machinome.core.loader`, `machinome.core.export`,
`machinome.core.pieces`, `machinome.source_generation`,
`machinome.viewers`, `machinome.sphinx`, `machinome.currency`,
`machinome._artifact`, `machinome.exact_cache`, `machinome.exact_artifacts`,
and the exact engine's file operations `machinome.occt.engine.read_brep`,
`machinome.occt.engine.write_brep` and `machinome.occt.engine.write_stl`.
The finding SHALL name the denied name reached. Every other name beneath
the contract members, including `machinome.node`, `machinome.simulation`,
`machinome.motion`, `machinome.math`, `machinome.parameters`,
`machinome.test`, `machinome.exact_engine`, `machinome.occt.engine` and its
other operations, and `machinome.openscad`, SHALL pass.

`machinome.exact` no longer exists: the exact operations a project calls
directly are defined in `machinome.occt.engine` and are reached there. Vet
judges a name by its place in the universe, not by whether a module defines
it, so an import of the removed module is not a vet finding; it fails when the
project runs.

#### Scenario: The loader through an import

- **WHEN** a vetted module runs `from machinome.core.loader import
  load_node`
- **THEN** vet reports kind `framework-internal`, name
  `machinome.core.loader`

#### Scenario: The builder through an attribute chain

- **WHEN** a vetted module runs `import machinome.core.expressions` and
  later names `machinome.core.builder.Builder`
- **THEN** vet reports kind `framework-internal`, name
  `machinome.core.builder`, and no finding for
  `machinome.core.expressions`

#### Scenario: The public contract passes

- **WHEN** a vetted module imports from `machinome.node`,
  `machinome.simulation`, `machinome.motion` and `machinome.occt.engine`
- **THEN** vet reports no finding for those imports

#### Scenario: The engine's exact operations pass

- **WHEN** a vetted module runs `from machinome.occt.engine import
  intersect_shapes, placed_shape, solid_volume`
- **THEN** vet reports no finding for that import

#### Scenario: The engine's file operations are internals

- **WHEN** a vetted module runs `from machinome.occt.engine import
  write_brep`, or names `machinome.exact_cache.cached_shape`
- **THEN** vet reports kind `framework-internal`, naming
  `machinome.occt.engine.write_brep` or `machinome.exact_cache`
