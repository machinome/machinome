## MODIFIED Requirements

### Requirement: The universe is a versioned declaration shipped with the framework

The system SHALL carry one universe declaration as a data file inside the
installed framework package. The declaration SHALL name the universe
(`machinome`) and the framework version it describes, which SHALL equal the
installed framework's version, and the framework's release tooling
SHALL rewrite that version with the others on every release. It SHALL
declare three tiers and a tests tier:

- **The contract**, allowed whole except a denylist of the framework's
  own modules that spawn processes, write to a caller-chosen path, or
  import by name: `machinome`, `machinome_mechanics`, `molejo`.
- **The kernels**, allowed except for a denylist of IO entry points:
  `cadquery`, `build123d`, `OCP`, `solid2`, `trimesh`, `numpy`, `scipy`,
  `manifold3d`, `shapely`. The denylist covers importers and exporters,
  STEP/IGES/STL readers and writers, numpy's
  load/save/fromfile/tofile/loadtxt/savetxt/genfromtxt/memmap, `scipy.io`,
  and solid2's render-to-file. It SHALL be written as dotted names, plus a
  list of method names that do file IO on kernel objects.
- **Pure stdlib**: `math`, `cmath`, `fractions`, `decimal`, `statistics`,
  `itertools`, `functools`, `operator`, `collections`, `dataclasses`,
  `enum`, `typing`, `abc`, `numbers`, `re`, `string`, `json`, `hashlib`,
  `struct`, `copy`, `contextlib`, `random`, `bisect`, `heapq`,
  `xml.etree`, `__future__`, `ast`, `os` restricted to `os.path` and the
  directory listings `os.listdir`, `os.scandir` and `os.walk`, and `pathlib`.
- **Tests**: `unittest`, `pytest` and `logging`, members only for a file that vet
  reaches solely through a companion test under the tests scope.

A module name SHALL count as a member when it equals a member or lies
beneath one: `xml.etree.ElementTree` is beneath `xml.etree`, but `xml`
alone is not a member. The declaration SHALL be able to restrict a member
to allowed dotted prefixes, as data: for a restricted member, the member
itself and names at or beneath an allowed prefix are members, and every
other name beneath the member is outside the universe. Every name that is
neither a member nor a project module SHALL be outside the universe, and
that includes `sys`, `io`, `subprocess`, `socket`, `urllib`, `http`,
`threading`, `multiprocessing`, `signal`, `ctypes`, `importlib`, `runpy`,
`pickle`, `marshal`, `tempfile`, `shutil` and `glob`.

The verdict SHALL depend only on the declaration and the project's files,
never on which packages the machine happens to have installed.

#### Scenario: The declaration names its version

- **WHEN** the universe declaration is read from the installed package
- **THEN** it names the universe `machinome` and a version equal to
  `machinome.__version__`

#### Scenario: os.path is inside the universe

- **WHEN** a vetted module runs `import os`, `from os.path import join`
  and calls `os.path.join(HERE, 'x')`, `os.path.exists(path)` and
  `os.listdir(HERE)`
- **THEN** vet reports no finding for them

#### Scenario: The rest of os is outside the universe

- **WHEN** a vetted module calls `os.makedirs(HERE)`, reads `os.environ`,
  or runs `from os import system`
- **THEN** vet reports kind `outside-universe`, named `os.makedirs`,
  `os.environ` and `os.system` respectively

#### Scenario: pathlib reads pass

- **WHEN** a vetted module runs `from pathlib import Path` and computes
  `Path(__file__).parent / 'x'`
- **THEN** vet reports no finding for it

#### Scenario: An installed package outside the universe is still outside

- **WHEN** a project imports `requests` on a machine where `requests` is
  installed
- **THEN** vet reports that import as `outside-universe`

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
  `machinome.simulation`, `machinome.motion` and `machinome.engine.brep`
- **THEN** vet reports no finding for those imports

#### Scenario: The engine's exact operations pass

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
