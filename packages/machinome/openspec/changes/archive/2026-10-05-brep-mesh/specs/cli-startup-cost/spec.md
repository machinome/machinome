## RENAMED Requirements

- FROM: `### Requirement: The test framework does not import the exact-geometry stack`
- TO: `### Requirement: The test framework does not import the B-rep stack`

## MODIFIED Requirements

### Requirement: Node backend exports resolve on first use

The system SHALL expose from `machinome.node` the node classes and the
declarative structure helpers, each resolved when it is first
accessed rather than when the package is imported. It SHALL NOT expose the
build-parameter kinds, the `Quantity` base or the parameter enumerator;
those belong to the dedicated build-parameter module and SHALL be reachable
only from there. It SHALL NOT expose the port kinds, the port declaration
enumerator or the time-base declaration; those belong to the dedicated
motion module and SHALL be reachable only from there. Importing
`machinome.node`, or any module beneath it,
SHALL NOT import a backend the caller has not named.

In particular, importing `machinome.node` SHALL NOT import `cadquery`,
`build123d`, `molejo` or the kernel binding `OCP`. A name is
resolved by importing the leaf module that defines it (the `node-model`
capability's table), which imports what that module needs and nothing else:
`StepNode` imports CadQuery and the kernel's STEP reader, `MolejoNode` imports
molejo, and `CadQueryNode`, `Build123dNode` and `Build123dSheetNode` import
no CAD front end, since a project's own module imports it to render.

Attribute access SHALL resolve submodules of `machinome.node` as well as the
exported classes, so a consumer reading `machinome.node.<submodule>` after
importing only the package keeps working.

A name that is not exported SHALL raise `AttributeError`, as it does today.
A name that has moved to another module SHALL raise `ImportError` whose
message names the module that now answers for it: an `ImportError` rather
than an `AttributeError` because `from machinome.node import <name>`
discards an `AttributeError`'s message and substitutes its own generic
text, so only an `ImportError` carries the redirect to the failing import
line. A name whose leaf module refuses an absent kernel SHALL raise that
refusal, which is an `ImportError`, for the same reason.

#### Scenario: An OpenSCAD-only project imports no exact stack

- **WHEN** a project whose model uses only `Solid2Node` is built
- **THEN** the build produces the same artifacts as before and `cadquery` is
  absent from the build process's imported modules

#### Scenario: A named backend is resolved

- **WHEN** a module runs `from machinome.node import CadQueryNode`
- **THEN** it receives the class `machinome.node.cadquery` defines, the same
  class it received before, and `cadquery` is not imported by the resolution

#### Scenario: The STEP reader is not imported by the node package

- **WHEN** `machinome.node` is imported in a fresh interpreter
- **THEN** the kernel's STEP reader is absent from the process's imported
  modules, and it is imported when `StepNode` is first accessed

#### Scenario: A submodule is reached through the package

- **WHEN** a consumer imports `machinome.node` and then reads
  `machinome.node.assembly` or `machinome.node.cadquery`
- **THEN** the submodule is returned

#### Scenario: An unknown name still fails

- **WHEN** a consumer reads a name `machinome.node` does not export
- **THEN** `AttributeError` is raised

#### Scenario: A parameter kind is not a node export

- **WHEN** a consumer reads a build-parameter name off `machinome.node`
- **THEN** `AttributeError` is raised naming it, so
  `from machinome.node import Length` fails at the import, and the
  package's export list carries no build-parameter name

#### Scenario: A port kind is not a node export

- **WHEN** a consumer reads `RotationalPort`, `SignalPort`,
  `TranslationalPort`, `Port`, `declared_ports` or `Time` off
  `machinome.node`
- **THEN** `ImportError` is raised naming `machinome.motion.ports`, so
  `from machinome.node import RotationalPort` fails at the import with
  that message, and the package's export list carries no port or time-base
  name

### Requirement: The test framework is imported by the paths that run tests

The system SHALL import `machinome.test` where tests are discovered or run,
not at the module scope of the loader that every node-scoped command goes
through. Importing `machinome.core.loader` SHALL NOT import
`machinome.test`, and therefore SHALL NOT import the B-rep stack.

The system SHALL likewise resolve `machinome.simulation`'s exports on first
access rather than at package import, so reaching
`machinome.simulation.enumeration` — which the serializer does on every
publication — does not import the scenario module and through it the test
framework.

Neither deferral makes the test framework optional. Discovering or running a
test SHALL import it exactly as it does today, and every name either package
exports today SHALL remain importable and identical.

#### Scenario: Loading a node does not import the test framework

- **WHEN** `machinome.core.loader` is imported in a fresh interpreter
- **THEN** `machinome.test` and `cadquery` are absent from `sys.modules`

#### Scenario: Discovering companion tests still works

- **WHEN** a node's companion tests are discovered
- **THEN** the same `TestCase` subclasses are returned as today, and the test
  framework is imported

#### Scenario: Publishing does not import the scenario module

- **WHEN** a build serializes its viewer document
- **THEN** the driver enumeration it needs is available and
  `machinome.simulation.scenario` is not imported

#### Scenario: The simulation package still exports its names

- **WHEN** a consumer imports a name from `machinome.simulation`
- **THEN** it receives the same object it receives today

### Requirement: The test framework does not import the B-rep stack

The system SHALL resolve the B-rep engine, and through it the
boundary-representation stack, at the B-rep path's first use rather than at
`machinome.test` module scope. Importing `machinome.test` in a fresh
interpreter SHALL NOT import `cadquery`, `OCP` or the B-rep engine.

This completes the deferral the loader requirement already states from the
other side: loading a node imports neither the test framework nor cadquery,
and importing the test framework imports neither cadquery nor the kernel. A
project that models entirely in solid2 and asserts entirely over meshes
therefore runs its tests without ever loading the B-rep stack.

The deferral SHALL NOT make B-rep geometry optional or change any B-rep
verdict. A comparison between two B-rep nodes SHALL resolve the B-rep engine
through the seam the `brep-engine-dependency` capability specifies and
produce the same result as before; only the moment of the import moves.

The B-rep path SHALL look up each name it calls where that name is defined,
at the moment of the call: an engine operation (`intersect_shapes`,
`fuse_shapes`, `placed_shape`, `solid_count`, `solid_volume`, `bounds`,
`face_bounds`, `mutually_outside`) as an attribute of the resolved engine, and
a core memo (`cached_bounding_box`, `cached_face_boxes`, `cached_placement`,
`shape_identity`, `shape_load_observation`) as an attribute of the core module
that defines it. A caller that patches a name in its defining module SHALL
therefore be honoured whether or not a B-rep comparison has yet run.
`machinome.test` SHALL NOT bind those names as attributes of its own, so each
keeps one path.

A failure to import the B-rep engine SHALL surface under the existing
deferred-import requirement and the `brep-engine-dependency` capability: an
absent engine is refused naming its install, a broken one raises its own
import error at first use, and neither is swallowed or substituted.

#### Scenario: Importing the test framework loads no exact stack

- **WHEN** `machinome.test` is imported in a fresh interpreter
- **THEN** `cadquery`, `OCP` and the B-rep engine module are absent from
  `sys.modules`

#### Scenario: A faceted project's test run loads no exact stack

- **WHEN** a project whose nodes are all mesh runs its tests to completion
- **THEN** the run reports the same results as today and `cadquery`, `OCP` and
  the B-rep engine module are absent from `sys.modules`

#### Scenario: An exact comparison still loads the stack

- **WHEN** two B-rep nodes are compared by an intersection assertion
- **THEN** the B-rep engine is resolved and the comparison returns the verdict
  it returns today

#### Scenario: A name patched where it is defined is used

- **WHEN** a caller patches `intersect_shapes` on the engine module, or
  `cached_face_boxes` on the core module that defines it, before any B-rep
  comparison has run
- **THEN** the B-rep path uses the patched object

### Requirement: The motion package is cheap to import

The system SHALL keep `machinome.motion` free of geometry. Importing
`machinome.motion` SHALL import no `machinome` module other than the
top-level `machinome` package itself — its parent, which the import
machinery necessarily creates and whose `__init__` carries version
metadata only — and no CAD backend.
Importing `machinome.motion.ports` SHALL import no
CAD backend and no B-rep stack: it reaches into
`machinome.node` only for the render-phase reporter, and the node
classes it needs to validate and read a time base SHALL be imported
inside the methods that need them, never at module scope.

Importing `machinome.motion.joints` or `machinome.motion.couplings`
SHALL cost what importing `machinome.motion.ports` costs and no more:
a joint owns a port as its coordinate and a relation relates two ports,
so the ports module is imported at their module scope, and everything
else they need from the node package — the tree, the operations, the
lifecycle phase, the declaring namespace, the driver declaration —
SHALL be imported inside the methods that need them, never at module
scope. Importing either SHALL import no CAD backend and no
B-rep stack.

Neither `machinome.motion.ports` nor any module beneath
`machinome.motion` SHALL be imported as a side effect of importing
`machinome.motion`.

#### Scenario: The package itself costs nothing

- **WHEN** `machinome.motion` is imported in a fresh interpreter
- **THEN** no `machinome` module other than the top-level `machinome`
  package itself, and no CAD backend, appears among the process's
  imported modules

#### Scenario: Ports pull no geometry backend

- **WHEN** `machinome.motion.ports` is imported in a fresh interpreter
- **THEN** `cadquery`, the kernel binding `OCP` and the STEP
  reader are absent from the process's imported modules

#### Scenario: Joints and couplings cost what ports cost

- **WHEN** `machinome.motion.joints` is imported in a fresh
  interpreter, and `machinome.motion.couplings` in another, and each
  one's imported `machinome` modules are compared with those of an
  interpreter that imported only `machinome.motion.ports`
- **THEN** each set is the same but for the module itself, and
  `cadquery`, the kernel binding `OCP` and the STEP reader
  are absent from all three

#### Scenario: Either import order works

- **WHEN** `machinome.motion.ports` is imported first in one fresh
  interpreter and `machinome.node.internal` is imported first in
  another
- **THEN** both interpreters complete the import, and a node class
  declaring a port behaves identically in each

### Requirement: The running engine costs nothing to a model that declares no running time

The system SHALL import the running simulation's modules — the compile
step and the engine beneath `machinome.simulation` — only when a `Sim`
is constructed over a root declaring `Time.running()`. Importing
`machinome.simulation`, constructing a `Sim` over an untimed or looping
root, building or publishing any model, and importing
`machinome.motion.ports` or `machinome.motion.couplings` SHALL NOT import
them. The running time base and the run-binder marker SHALL live in
`machinome.motion.ports` with no import of their own, so the motion
package's import cost is unchanged, and the couplings module's recognition
of a run binder SHALL add no import to it.

#### Scenario: A looping root's simulation imports no running engine

- **WHEN** a fresh interpreter constructs a `Sim` over a root declaring
  `Time(loop=...)` and runs it
- **THEN** the compile step and the engine modules are absent from the
  process's imported modules

#### Scenario: Ports and couplings cost what they cost

- **WHEN** `machinome.motion.ports` and `machinome.motion.couplings` are
  imported in fresh interpreters
- **THEN** their imported `machinome` modules are the sets the "The motion
  package is cheap to import" requirement already states, with nothing
  from `machinome.simulation` among them

#### Scenario: A running root's simulation imports the engine on construction

- **WHEN** a `Sim` is constructed over a root declaring `Time.running()`
- **THEN** the compile step and the engine are imported then, and no CAD
  backend and no B-rep stack with them
