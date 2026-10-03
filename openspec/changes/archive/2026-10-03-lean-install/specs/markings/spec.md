## ADDED Requirements

### Requirement: Artwork is reduced through a seam that names its extra

The marking declarations `Marking`, `Wrapped`, `Flat` and `Svg` SHALL need no
CAD kernel: importing `machinome.node.markings`, creating a class that
declares a marking (the artwork path's resolution and refusals included), and
building a part whose marking artifacts are current SHALL NOT import
`build123d` and SHALL NOT resolve the artwork reducer.

Reducing `Svg` artwork to its closed regions and their triangles SHALL be done
by the reducer in `machinome.node.build123d`, which the markings module
resolves on first use by importing that one known module, and never imports at
its own top. The reducer SHALL declare the reducer contract version it
implements; the markings module SHALL declare the version it speaks and refuse
a reducer that declares another, or none, naming both versions and the
reducer's module, before any artwork is reduced.

When a marking must be built and the reducer's module refuses because
`build123d` cannot be found, the build SHALL fail with one error that names
the part's class and the marking's attribute, the artwork file, and
`pip install "machinome[build123d]"`, and SHALL write no marking artifact.

The reduction SHALL produce the same regions, triangles and marking bytes as
before this change.

#### Scenario: Declaring a marking needs no kernel

- **WHEN** a class declaring `Marking(Svg('results_dial.svg'), Wrapped(...))`
  is created in an interpreter where `build123d` cannot be found
- **THEN** the class is created, the artwork path is resolved and checked as
  before, and `build123d` is not imported

#### Scenario: A stale marking without the extra is refused by its install line

- **WHEN** that part's marking artifact is stale and the part is built where
  `build123d` cannot be found
- **THEN** the build fails naming the class, the marking's attribute,
  `results_dial.svg` and `pip install "machinome[build123d]"`, and no marking
  artifact is written

#### Scenario: A current marking needs no reducer

- **WHEN** a part whose marking artifacts are current is built again where
  `build123d` cannot be found
- **THEN** the build succeeds and the marking artifacts keep their bytes

#### Scenario: A reducer of another contract is refused

- **WHEN** the reducer's module declares a reducer contract version other
  than the one the markings module speaks
- **THEN** reducing an artwork raises an error naming both versions and
  `machinome.node.build123d`, and no artwork is reduced

#### Scenario: The reduction is unchanged

- **WHEN** a marking fixture is built after this change
- **THEN** its marking artifact's bytes equal those recorded before it
