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
`machinome._artifact`, `machinome.brep_cache`, `machinome.brep_artifacts`,
and the B-rep engine's file operations `machinome.engine.brep.read_brep`,
`machinome.engine.brep.write_brep` and `machinome.engine.brep.write_stl`.
The finding SHALL name the denied name reached. Every other name beneath
the contract members, including `machinome.node`, `machinome.simulation`,
`machinome.motion`, `machinome.math`, `machinome.parameters`,
`machinome.test`, `machinome.engine`, `machinome.engine.brep` and its
other operations, and the leaf modules `machinome.node.cadquery`,
`machinome.node.build123d`, `machinome.node.step`, `machinome.node.molejo`,
`machinome.node.solid2`, `machinome.node.jscad` and `machinome.node.stl` and the
package `machinome.node.openscad` with its modules, SHALL pass.

`machinome.openscad` and `machinome.scad_engine` no longer exist: the OpenSCAD
writer and binary contract are `machinome.node.openscad.writer` and
`machinome.node.openscad.binary`. An import of a removed module is not a vet
finding; it fails when the project runs.

`machinome.exact` no longer exists: the B-rep operations a project calls
directly are defined in `machinome.engine.brep` and are reached there. Vet
judges a name by its place in the universe, not by whether a module defines
it, so an import of the removed module is not a vet finding; it fails when the
project runs.

`machinome.node.adapters` no longer holds the leaf modules: each is
`machinome.node.<x>`. An import beneath the dissolved package is, likewise, not
a vet finding; it fails when the project runs, naming the new address. Whether
a kernel's extra is installed does not enter a verdict.

The node package's root resolves no name (`node-model`, "The node package's
root exports nothing"): every node class is imported from its module,
`machinome.node.assembly`, `machinome.node.cadquery` and the others, which are
beneath the contract members and pass. An import of a former root name, such as
`from machinome.node import AssemblyNode`, is, likewise, not a vet finding; it
fails when the project runs, naming the module that defines the name.

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

- **WHEN** a vetted module imports from `machinome.node.assembly`,
  `machinome.node.cadquery`, `machinome.node.stl`, `machinome.simulation`,
  `machinome.motion` and `machinome.engine.brep`
- **THEN** vet reports no finding for those imports

#### Scenario: The engine's B-rep operations pass

- **WHEN** a vetted module runs `from machinome.engine.brep import
  intersect_shapes, placed_shape, solid_volume`
- **THEN** vet reports no finding for that import

#### Scenario: The engine's file operations are internals

- **WHEN** a vetted module runs `from machinome.engine.brep import
  write_brep`, or names `machinome.brep_cache.cached_shape`
- **THEN** vet reports kind `framework-internal`, naming
  `machinome.engine.brep.write_brep` or `machinome.brep_cache`

#### Scenario: A leaf module passes

- **WHEN** a vetted module runs `from machinome.node.cadquery import
  CadQueryNode` and `from machinome.node.step import StepAssembly,
  solids_from_faces`
- **THEN** vet reports no finding for those imports
