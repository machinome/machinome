## MODIFIED Requirements

### Requirement: The motion package holds what moves

The system SHALL provide a package `solid_node.motion` whose subject is
what moves and what drives what, laid out as three submodules so that an
import line names the kind of thing it brings in:

- `solid_node.motion.ports` — a value that flows between nodes: the port
  declarations, their bound value slot, the binding helper, the
  declaration enumerator, the root's own time channel (`Time`, with its
  three bases `Time(loop=...)`, `Time.running()` and `Time.elapsed()`
  told apart by `mode`,
  and the enumerator that reads a class's time declaration), and the
  binder kind a running simulation binds as (`RunBinder`), kept here so
  the binding helper can recognize it without importing the simulation
  layer;
- `solid_node.motion.joints` — a pair that places a body: `Revolute` and
  `Prismatic`, their error kind and their enumerator (capability
  `joints`);
- `solid_node.motion.couplings` — a law between two coordinates: `Affine`,
  the relation and derived-coordinate kinds, their error kinds and their
  enumerators (capability `couplings`).

The package `__init__` SHALL export no name of its own and SHALL NOT
resolve a submodule's names as attributes of the package, so there is
exactly one import path for each name.

#### Scenario: The submodules hold their kinds

- **WHEN** a consumer imports `solid_node.motion.joints` and
  `solid_node.motion.couplings`
- **THEN** `Revolute` and `Prismatic` are read off the first and `Affine`
  off the second, and each module's docstring states its subject

#### Scenario: The package itself exports nothing

- **WHEN** a consumer reads any port, time-base, joint or coupling name
  off `solid_node.motion` directly
- **THEN** `AttributeError` is raised, so
  `from solid_node.motion import RotationalPort` fails at the import and
  the submodule path is the only path

#### Scenario: The running base and the run binder are imported from the ports module

- **WHEN** a consumer writes
  `from solid_node.motion.ports import Time, RunBinder` and declares
  `time = Time.running()` on a root
- **THEN** `type(root).time.mode` reads `'running'`, `type(root).time.loop`
  reads `None`, and `RunBinder` is the class every running simulation's
  binder is an instance of


#### Scenario: The elapsed base is imported from the ports module

- **WHEN** a consumer writes `from solid_node.motion.ports import Time` and
  declares `time = Time.elapsed()` on a root
- **THEN** `type(root).time.mode` reads `'elapsed'` and
  `type(root).time.loop` reads `None`, and no other import is needed to
  declare the base
